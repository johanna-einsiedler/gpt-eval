#### Note uses python 3.9 environment (newenv)
from typing import TypedDict
import pandas as pd
import random
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anthropic
import regex as re
import sys
import ast
import json
import subprocess
import numpy as np

from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # or your equivalent import
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import START
from langgraph.graph import END
from IPython.display import Image, display


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


model = 'claude-3-7-sonnet-20250219'
# Initialize Claude Sonnet
llm = ChatAnthropic(
    model= 'claude-3-7-sonnet-20250219',  # Claude Haiku model
    anthropic_api_key=ANTHROPIC_API_KEY,
    temperature=0,
    max_tokens=8192
)

# 1. Using __call__ (direct function call)
#response_via_call = llm(prompt)
#response_via_call.content

def safe_eval(value, default=[]):
    """
    Safely evaluates a string as a Python literal.

    Parameters:
        value (any): The value to evaluate. Typically a string representing a Python literal.
        default (any): The default value to return if evaluation fails or value is NaN. Defaults to an empty list.

    Returns:
        any: The evaluated Python object, or the default value if evaluation fails.
    """
    if pd.isna(value):
        return default
    try:
        return ast.literal_eval(value)
    except:
        return default

def join_items(items, conj='and'):
    """
    Joins a list of strings into a human-readable string with commas and a conjunction.

    Parameters:
        items (list of str): The list of string items to join.
        conj (str): The conjunction to use before the last item. Defaults to 'and'.

    Returns:
        str: A string of items joined by commas and the conjunction.
        
    Examples:
        join_items(['apples']) -> "apples"
        join_items(['apples', 'oranges']) -> "apples and oranges"
        join_items(['apples', 'bananas', 'oranges']) -> "apples, bananas and oranges"
    """
    if len(items) == 1:
        return items[0]
    if len(items) > 1:
        return ', '.join(items[:-1]) + f' {conj} ' + items[-1]
    return ''

def build_system_prompt(occupation, task_description, task_id, required_tools, required_materials, template):
    # Tools
    if required_tools:
        tools_instructions = (
            f"- The candidate has access to a computer with the following tools: "
            f"{join_items(required_tools, conj='and')}" )
    else:
        tools_instructions = "- The candidate does not have access to any special tools."
    # Materials
    if required_materials:
        materials_instructions = (
            f"- The candidate can also be given digital materials such as "
            f"{join_items(required_materials, conj='or')} that must be used for the test.")
    else:
        materials_instructions = "- The candidate does not have access to any additional digital materials."

    return template.format(
        occupation=occupation,
        task_description=task_description,
        task_id=task_id,
        tools_instructions=tools_instructions,
        materials_instructions=materials_instructions
    )


def extract_and_save_python_script(script_text: str, folder: str, filename: str = "task_evaluation.py"):
    """Finds Python code enclosed in triple backticks ```python ...``` and saves it to file.
    useful for extractign grading script
    """
    match = re.search(r'```python(.*?)```', script_text, re.DOTALL)
    if not match:
        raise ValueError("No ```python ... ``` code block found in the grading text.")
    code = match.group(1).strip()

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    return code

def extract_and_save_json(json_text: str, folder: str, filename: str = "answer_key.json"):
    """
    Finds JSON enclosed in triple backticks ```json ...``` and saves it to a file.
    """
    match = re.search(r'```json(.*?)```', json_text, re.DOTALL)
    if not match:
        raise ValueError("No ```json ... ``` block found in the evaluation text.")
    json_str = match.group(1).strip()

    data = json.loads(json_str)  # parse the JSON
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return data



class ExamState(TypedDict):
    occupation: str
    task_id: str
    task_description: str
    exam_author_model: str
    
    # Tools and materials
    tools: str#List[str]
    materials: str#List[str]
    
    # Container for any dynamic exam data you generate, 
    # e.g. in multiple nodes (overview, instructions, materials, etc.)
    exam: dict
    
    # If you plan to store specific text prompts or outputs from nodes:
    system_prompt: str
    overview: str
    instructions: str
    materials_all: str
    materials_candidate: str
    submission: str
    evaluation: str
    grading: str
    answer_key:str

    errors: list
    # Boolean flags for validation checks
    check_real_materials: bool
    check_no_internet: bool
    failed_candidate_materials:int
    # Key grade and count how many times below threshold
    key_grade_threshold:float
    key_grade:float
    answer_key_count: int
    check_overall_makes_sense: bool
    explanation_overall_makes_sense:str
    

def node_system_prompt(state: ExamState) -> ExamState:
    occupation = state['occupation']
    task_description = state['task_description']
    task_id = state['task_id']
    required_tools = state['tools']
    required_materials = state['materials']

    system_prompt_template = '''You are an excellent examiner of {occupation} capabilities. Design a remote, **practical** exam to verify whether a {occupation} can {task_description}.
    This exam will have two parts (basic and advanced). Your current task is **only** to design the basic exam.

    ### Context
    {tools_instructions}
    {materials_instructions}
    - Design a **practical** exam that can be completed remotely using only these tools. A practical exam is an exam actually testing whether the described task can be performed successfully. An exam testing knowledge about the task is NOT a practical exam.
    - To simplify evaluation, the candidate should submit answers in a structured JSON format. Name the file "test_submission.json".
    - The candidate should be able to complete the exam in maximum 90 minutes.
    '''

    state["system_prompt"] = build_system_prompt(occupation, task_description, task_id, required_tools, required_materials, template=system_prompt_template)

    return state


# 2. Query overview
def node_overview(state: ExamState) -> ExamState:
    # NOTE - Maybe we want to in the overview prentively prompt the LLM to have trick questions or things that are
    # not obvious, so that the evaluator knows this, but the candidate doesn't
    prompt_overview ='''### Your assignment
    Provide a brief explanation of the exam's purpose and structure for the evaluator.
    '''
    print('creating exam overview')
    messages = [
    SystemMessage(content=state["system_prompt"]),
    HumanMessage(content=prompt_overview)
    ]

    state["overview"] = llm(messages).content
    return state

def node_instructions(state: ExamState) -> ExamState:
    prompt_template_instructions ='''Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview} </examoverview>

    ### Your assignment:

    Based on the explanation write clear, concise instructions for the candidate including:
    - What they need to accomplish (without prescribing specific methods)
    - Brief description of any materials that will be provided
    - Expected format for answer submission
    - The actual test they need perform, i.e. the tasks that need to be done or questions that need to be answered.

    IMPORTANT: When designing the test, eliminate any opportunities for candidates to make arbitrary choices (like custom account codes, naming conventions, or classification systems) that would complicate evaluation. Either:
    - Provide pre-defined structures/codes that must be used, or
    - Design questions with objectively verifiable numerical/text answers that don't depend on the candidate's approach. 
    - You can ask for text answers that can be compared to an exact match, but avoid asking for text answers such as justification that require interpretation and/or with many possible correct answers.
    '''
    prompt = prompt_template_instructions.format(answer_overview=state["overview"])
    
    messages = [
    SystemMessage(content=state["system_prompt"]),
    HumanMessage(content=prompt)
    ]


    state["instructions"] = llm(messages).content
    return state

def node_materials(state: ExamState) -> ExamState:
    prompt_template_materials = """Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
    Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>

    ## Your assignment:
    - If the exam doesn't require any additional material, just respond with "No material required".
    - Otherwise, create two parts:
    1. Synthetic test materials (CSV contents, datasets, etc.) that have predictable outcomes. Include the actual content to be provided to candidates and ensure all materials have clear identifiers, labels, or pre-defined categories that prevent ambiguity.
    2. An explanation for the evaluator on how these materials were created and any knowledge helpful for knowing the correct answers

    Format your response with these specific XML tags:
    <MATERIALS_FOR_CANDIDATE>
    [Include here the actual content to be provided to candidates. Ensure all materials have clear identifiers, labels, or pre-defined categories that prevent ambiguity.]
    </MATERIALS_FOR_CANDIDATE>

    <MATERIALS_EXPLANATION_FOR_EVALUATOR>
    [Explain to the evaluator:
    - How the materials were created and what, if any, statistical patterns or other relationships exist
    - Cross-references or important conections between different materials (e.g., codes in a CSV that match details in text, or relationships between texts)
    - Any tricky elements or common pitfalls in the materials that may cause candidates to answer incorrectly
    - "Hidden" information that requires careful reading to identify]
    </MATERIALS_EXPLANATION_FOR_EVALUATOR> 

    IMPORTANT: When designing the test, eliminate any opportunities for candidates to make arbitrary choices (like custom account codes, naming conventions, or classification systems) that would complicate evaluation. Either:
    - Provide pre-defined structures/codes that must be used, or
    - Design questions with objectively verifiable numerical/text answers that don't depend on the candidate's approach
    - Make sure both start and end XML tags are present
    """

    prompt = prompt_template_materials.format(answer_overview=state["overview"], answer_instructions=state["instructions"])
    
    messages = [
    SystemMessage(content=state["system_prompt"]),
    HumanMessage(content=prompt)
    ]

    msg = llm(messages).content
    state["materials_all"] = msg
    try:
        state["materials_candidate"] = re.search(r'<MATERIALS_FOR_CANDIDATE>(.*?)</MATERIALS_FOR_CANDIDATE>', state["materials_all"], re.DOTALL).group(1)
    except:
        state["materials_candidate"] = "Not extracted"
        # keep track of how many times this fails, if more than 3 then break
        state["failed_candidate_materials"] += 1
        print("materials candidate was not able to be extracted")

    return state


def node_submission(state: ExamState) -> ExamState:
    prompt_template_submission = """
    Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
    Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
    Here are the materials provided to the candidate: <materials> {answer_materials} </materials>

    ## Your assignment
    Based on the given information, specify exactly what format the candidate's answers must be in, including:
    - Required JSON answer format with question IDs
    - The exact format of answers (numbers, text, specific units, decimal places)
    - Any supplementary files if necessary
    - You should only specify format and/or code/conventions to use in answering, but you should not give the answers away
    - Instruct to submit with a candidate id where "YOUR_ID_HERE" is the model version that is powering the candidate "GPT-4-turbo", "GPT-4o", "Claude-3_7-Sonnet", "DeepSeekR1", "Gemini-Flash-2", etc.
    """
    prompt = prompt_template_submission.format(
        answer_overview=state["overview"],
        answer_instructions=state["instructions"],
        answer_materials=state["materials_all"]
    )
    messages = [
        SystemMessage(content=state["system_prompt"]),
        HumanMessage(content=prompt)
    ]
    state["submission"] = llm(messages).content
    return state


def node_evaluation(state: ExamState) -> ExamState:
    print('starting node evaluation')
    prompt_template_evaluation = """
    Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
    Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
    Here are the materials provided to the candidate: <materials> {answer_materials} </materials>
    Here are the submission requirements for the candidate: <submission_requirements> {answer_submission} </submission_requirements>

    ## Your assignment

    Based on the given information create the following for the evaluator:
    - Complete answer key in JSON format for automated checking
    - Explanation of correct answers and how they were derived
    - Passing criteria (e.g., minimum number of correct answers)
    """
    prompt = prompt_template_evaluation.format(
        answer_overview=state["overview"],
        answer_instructions=state["instructions"],
        answer_materials=state["materials_all"],
        answer_submission=state["submission"]
    )
    messages = [
        SystemMessage(content=state["system_prompt"]),
        HumanMessage(content=prompt)
    ]
    state['evaluation']= llm(messages).content
    state["answer_key_count"] += 1
    return state

def node_grading(state: ExamState) -> ExamState:
    print('starting node grading')
    # Note, I modified the prompt so that files are passed as argument
    prompt_template_grading ="""
    Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
    Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
    Here are the materials provided to the candidate: <materials> {answer_materials} </materials>
    Here are the submission requirements for the candidate: <submission_requirements> {answer_submission} </submission_requirements>
    Here is the information given to the evaluator: <evaluation_information> {answer_evaluation} </evaluation_information>

    ## Your assignment
    Based on the given information, create a Python script named 'task_evaluation.py' that reads in the candidate submission and the answer key provided as arguments in the command line. The script should:
    - Accept two arguments in the following order:
    1. The **first argument** is the name of the candidate submission JSON file (e.g., `test_submission.json`).
    2. The **second argument** is the name of the answer key JSON file (e.g., `answer_key.json`).
    - Automatically score the test performance based on the provided files.
    - Save the results as `test_results.json` in the same folder as the script.
    - In addition to the detailed test results, `test_results.json` should include one variable `overall_score` with the percentage of points achieved by the candidate.

    The script should be runnable from the command line like this:
    ```bash
    python task_evaluation.py test_submission.json answer_key.json
    """
    prompt = prompt_template_grading.format(
        answer_overview=state["overview"],
        answer_instructions=state["instructions"],
        answer_materials=state["materials_all"],
        answer_submission=state["submission"],
        answer_evaluation=state["evaluation"]
    )
    messages = [
        SystemMessage(content=state["system_prompt"]),
        HumanMessage(content=prompt)
    ]
    state["grading"] = llm(messages).content
    return state


def node_save_eval_and_answer(state: ExamState) -> ExamState:
    """
    1) Saves the Python grading script from state["grading"] into `task_evaluation.py`
    2) Saves the answer key JSON from state["evaluation"] into `answer_key.json`
    """
    ('starting node save eval and answer')
    task_id = state["task_id"]
    path = "../../data/exam_approach/test_results/" + state["exam_author_model"] + "/"
    folder = task_id.replace(".", "_")
    
    try:
        # 1. Save the Python grading script
        script = extract_and_save_python_script(
            script_text=state["grading"], 
            folder= path + folder, 
            filename="task_evaluation.py"
        )
        # 2. Save the answer key
        key = extract_and_save_json(
            json_text=state["evaluation"], 
            folder=path + folder, 
            filename="answer_key.json"
        )
        state['answer_key'] = key
        print(f"Grading script and answer key saved successfully for task {task_id}.")
    except Exception as exc:
        err_msg = f"Error saving assets for {task_id}: {exc}"
        print(err_msg)
        state["errors"].append(err_msg)
    return state



def node_check_materials_fake_image(state: ExamState) -> ExamState:
    # NOTE - TODO, maybe we want to add space for reasoning?
    prompt_check_fake_image = """
    You are a system verifying if the provided instructions and/or materials falsely claim to include an image, but it is only a description. 
    If the materials explicitly claim they have an image but only provide a textual description, 
    and that image is crucial for at least one task, respond with "Y". 
    In all other cases (including no mention of an image at all), respond with "N". 
    Return only "Y" or "N".
    """

    messages = [
        SystemMessage(content=prompt_check_fake_image),
        HumanMessage(content=state['instructions'] + state["materials_all"])
    ]

    if llm(messages).content == "Y":
        state["check_real_materials"] = False
    else:
        state["check_real_materials"] = True
    return state

def node_check_materials_fake_website(state: ExamState) -> ExamState:
    prompt_check_fake_website = """
    You are a system verifying whether the instructions and/or materials provided reference a publicly available website or news source that appears to be fabricated. 
    It is acceptable if the materials reference an internal document, company guidelines, accounting statements or well known public documents. 
    However, if the materials claim to reference a real, publicly accessible website or piece of news (e.g., something you would expect to find only online) 
    and that url or texts  appears to be made up, respond with "Y". 
    In all other cases, respond with "N". 
    Return only "Y" or "N".
    """
    
    messages = [
        SystemMessage(content=prompt_check_fake_website),
        HumanMessage(content= state["instructions"] + state["materials_all"])
    ]

    if llm(messages).content == "Y":
        state["check_no_internet"] = False
    else:
        state["check_no_internet"] = True
    return state


def node_check_answer_key(state: ExamState) -> ExamState:
    errors =[]
    task_id = state["task_id"]
    subfolder = task_id.replace(".", "_")
    path =  "../../data/exam_approach/test_results/" + state["exam_author_model"] + "/" + subfolder + "/"
    # Passes answer_key isntead of test_submission to later check answer key gets full marks
    # subprocess.run(["ls", "-l", path])
    try:
        result = subprocess.run(
            ["python", "task_evaluation.py", "answer_key.json", "answer_key.json"],
            cwd=path,
            check=True,  # Raise an exception if the command fails
            stderr=subprocess.PIPE,  # Capture stderr
            stdout=subprocess.PIPE   # Capture stdout (if needed)
            )
        print("Script executed successfully.")

        # If the script runs successfully, append None to errors list (no errors)
        errors.append(None)
            # Now get answer key grade
        try:
            # Load the JSON file
            with open(path + 'test_results.json', 'r') as f:
                data = json.load(f)
            
            # Extract the overall_score
            overall_score = data.get("overall_score", None)
            state["key_grade"] = np.round(overall_score)
            return state

        except FileNotFoundError:
            print(path)
            print(f"Error: The file '{path}' was not found.")
            errors.append('no overall score found')
            state["errors"].append(errors)
            state["key_grade"] = np.nan
            return state
        except json.JSONDecodeError:
            print(f"Error: The file '{path}' is not a valid JSON file.")
            errors.append('not json file')
            state["errors"].append(errors)
            state["key_grade"] = np.nan
            return state
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            state["errors"].append(errors)
            errors.append(str(e))
            state["key_grade"] = np.nan
            return state
    
    except subprocess.CalledProcessError as e:
        # Capture and store the error output in the errors list
        print(f"Error: Script failed with return code {e.returncode}")
        print(f"Error Output:\n{e.stderr.decode('utf-8')}")
        errors.append(e.stderr.decode('utf-8'))  # Append the error message to the errors list
        state["errors"].append(errors)
        state["key_grade"] = np.nan
        return state
    except FileNotFoundError:
        error_message = "Error: The script or directory was not found. Check the path."
        print(error_message)
        print(path)
        errors.append(error_message)  # Append the error message to the errors list
        state["errors"].append(errors)
        state["key_grade"] = np.nan
        return state
    except Exception as e:
        # Capture and store any unexpected error
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        errors.append(error_message)  # Append the error message to the errors list   
        state["errors"].append(errors)
        state["key_grade"] = np.nan
        return state



def node_overall_makes_sense(state: ExamState) -> ExamState:

    system_prompt = f"""
    You are a system verifying a remote, **practical** exam to assess a {state['occupation']}'s ability to {state['task_description']}.

    CANDIDATE vs. EVALUATOR CONTEXT:
    - The candidate only sees: Instructions, Materials, Submission format.
    - The evaluator sees everything else (Overview, Evaluation info, Grading script, and the answer key).

    CHECKS TO PERFORM:
    1) Is this exam actually practical (testing real job tasks) rather than purely theoretical?
    2) Are the tasks realistic for a {state['occupation']} in the year 2025?
    3) Are the instructions, materials, and submission requirements unambiguous?
    4) Do the grading script and answer key correctly reflect the exam?
    - No scenario where a candidate can pass overall despite failing a critical part.
    - No scenario where a candidate who meets all requirements is incorrectly failed.
    - The answer key should score 100% on the grading script.

    HOW TO RESPOND:
    Return EXACTLY one JSON object. Here is the required structure (note the doubled braces to show literal braces in an f-string):

    {{
    "makes_sense": true,
    "explanation": "A concise explanation here. Also suggest potential weaknesses (e.g. key not scoring 100) or ambiguities in the exam."
    }}

    No additional text (e.g., disclaimers, markdown formatting) outside this JSON object.
        """

    user_message = f"""
    === EXAM CONTENT (Evaluator-Only Context in addition to Candidate Materials) ===

    • Overview (Evaluator-Only):
    {state["overview"]}

    • Instructions (Candidate Sees):
    {state["instructions"]}

    • Materials (Candidate Sees):
    {state["materials_all"]}

    • Submission Format (Candidate Sees):
    {state["submission"]}

    • Evaluation Info & Answer Key Explanation (Evaluator-Only):
    {state["evaluation"]}

    • Grading Script (Evaluator-Only):
    {state["grading"]}
    • Answer key (Evaluator-Only):
    {state['answer_key']}

    (Note: The answer key is passed to the grading script as 'answer_key.json'.)
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message.strip())
    ]

    response = llm(messages).content.strip()

    try:
        result = json.loads(response)
        state["check_overall_makes_sense"] = bool(result.get("makes_sense", False))
        state["explanation_overall_makes_sense"] = str(result.get("explanation", ""))
    except json.JSONDecodeError:
        # If the LLM's response isn't valid JSON, mark sense-check as False
        # and store the raw response for debugging.
        state["check_overall_makes_sense"] = False
        state["explanation_overall_makes_sense"] = (
            "Could not parse JSON. Raw LLM response:\n" + response
        )

    return state


def node_end(state: ExamState) -> ExamState:
    '''Compiles the exam
    '''
    if state["check_real_materials"] and state["check_no_internet"] and state["key_grade"] >= state["key_grade_threshold"]:
        state['exam'] = state['instructions'] + state['materials_candidate'] + state['submission'] 
    else:
        state['exam'] = "Exam not valid"
    return state

#### Routing functions

def route_after_materials_candiate(state: ExamState) -> str:

    if state["failed_candidate_materials"] >= 3:
        # if it has consistently failed in generating materials for candiate just end it
        return "node_end"
    elif state["materials_candidate"] == "Not extracted":
        return "node_materials"
    else:
        return "node_check_images"


def route_after_image_check(state: ExamState) -> str:

    if state["check_real_materials"] == False:
        return "node_end"
    else:
        return "node_check_websites"

def route_after_internet_check(state: ExamState) -> str:

    if state["check_no_internet"] == False:
        return "node_end"
    else:
        return "node_submission"


# # Add a dummy node that does nothing but moves to node_evaluation
# def node_pause_before_evaluation(state: ExamState) -> ExamState:
#     return state


# Update route
def route_after_key_check(state: ExamState) -> str:
    if state["key_grade"] >= state["key_grade_threshold"]:
        return "node_overall_makes_sense"
    elif state["answer_key_count"] > 3:
        return "node_end"
    else:
        return "node_evaluation"


if __name__ == "__main__":
    #file_answers = "../../data/exam_approach/test_results/{}/test_results_business_and_financial_operations_occupations_CORE_automatable.csv".format(model)
    tasks_file = '/Users/htr365/Documents/PhD/21_automatisation/gpt_eval/data/exam_approach/material_lists/claude-3-7-sonnet-20250219/task_list_management_occupations_CORE.csv'
    df_tasks = pd.read_csv(tasks_file)
    df_tasks  = df_tasks.loc[:, ~df_tasks .columns.str.contains('^Unnamed')]
    print('overall data shape',df_tasks.shape)

    #already_done = pd.read_csv('/Users/htr365/Documents/PhD/21_automatisation/gpt_eval/data/exam_approach/test_results/claude-3-7-sonnet-20250219/scores_61.csv')
    # remove according to exclusion list
    exclusion_list = pd.read_csv('../../data/exam_approach/exclusion_lists/management_occupations_only_data_text_CORE.csv',index_col=0).rename(columns={'0':'task_id'})
    df_tasks = df_tasks[~df_tasks['task_id'].isin(exclusion_list['task_id'])]
    print('data after filtering for tools/materials', df_tasks.shape)
   # df_tasks = df_tasks[~df_tasks['task_id'].isin(already_done['task_id'])]
   # print('data after filtering for already existing exams', df_tasks.shape)


    #df_tasks = df_tasks[df_tasks['task_id']==12882]
    df_tasks = df_tasks[['occupation', 'task_description', 'task_id', 'required_tools_standard', 'required_materials_standard']]
    print(df_tasks.shape)
    # Initialize an empty list to store result states
    result_states = []


    graph_builder = StateGraph(ExamState)

    # Add nodes to the graph
    graph_builder.add_node("construct_system_prompt", node_system_prompt)
    graph_builder.add_node("node_overview", node_overview)
    graph_builder.add_node("node_instructions", node_instructions)
    graph_builder.add_node("node_materials", node_materials)
    graph_builder.add_node("node_check_images", node_check_materials_fake_image)
    graph_builder.add_node("node_check_websites", node_check_materials_fake_website)
    graph_builder.add_node("node_submission", node_submission)
    graph_builder.add_node("node_evaluation", node_evaluation)
    graph_builder.add_node("node_grading", node_grading)
    graph_builder.add_node("node_save_eval_and_answer", node_save_eval_and_answer)
    graph_builder.add_node("node_check_answer_key", node_check_answer_key)
    graph_builder.add_node("node_overall_makes_sense", node_overall_makes_sense)
    graph_builder.add_node("node_end", node_end)
    #graph_builder.add_node("node_pause_before_evaluation", node_pause_before_evaluation)

    #Add edges the graph
    graph_builder.add_edge(START, "construct_system_prompt")
    graph_builder.add_edge("construct_system_prompt", "node_overview")
    graph_builder.add_edge("node_overview", "node_instructions")
    ### NOTE - probably add conditional edge depending on whether materials are required
    graph_builder.add_edge("node_instructions", "node_materials")
    # add conditional edges in case materials for candidate where not extracted
    graph_builder.add_conditional_edges("node_materials", route_after_materials_candiate)
    ### Add conditional edges if materials_fake_website or materials_fake_image then end the process
    graph_builder.add_conditional_edges("node_check_images", route_after_image_check)
    graph_builder.add_conditional_edges("node_check_websites", route_after_internet_check)
    # If it passes will continue to generatl submissions and grading
    graph_builder.add_edge("node_submission", 'node_evaluation')
    # graph_builder.add_edge("node_pause_before_evaluation", "node_evaluation")

    graph_builder.add_edge("node_evaluation", 'node_grading')
    # Now check the answer key and how much it scores
    graph_builder.add_edge("node_grading", 'node_save_eval_and_answer')
    graph_builder.add_edge("node_save_eval_and_answer", "node_check_answer_key")
    # graph_builder.add_edge("node_check_answer_key", "node_overall_makes_sense")
    graph_builder.add_conditional_edges("node_check_answer_key", route_after_key_check)
    graph_builder.add_edge("node_overall_makes_sense", "node_end")
    graph_builder.add_edge("node_end", END)

    graph = graph_builder.compile()
  
    # row = {
    #     'occupation': 'Wholesale and Retail Buyers, Except Farm Products',
    #     'task_description': 'Recommend mark-up rates, mark-down rates, or merchandise selling prices.',
    #     'task_id': '20713.0',
    #     'required_tools_standard': "[['Spreadsheets', 'PDF viewer']]",
    #     'required_materials_standard': "[['Text', 'Data']]"
    # }
    print(df_tasks.head())
    #row = df_tasks.iloc[0]

    # tools = safe_eval(row['required_tools_standard'])
    # materials = safe_eval(row['required_materials_standard'])
    # system_prompt_template = '''You are an excellent examiner of {occupation} capabilities. Design a remote, **practical** exam to verify whether a {occupation} can {task_description}.
    # This exam will have two parts (basic and advanced). Your current task is **only** to design the basic exam.

    # ### Context
    # {tools_instructions}
    # {materials_instructions}
    # - Design a **practical** exam that can be completed remotely using only these tools. A practical exam is an exam actually testing whether the described task can be performed successfully. An exam testing knowledge about the task is NOT a practical exam.
    # - To simplify evaluation, the candidate should submit answers in a structured JSON format. Name the file "test_submission.json".
    # - The candidate should be able to complete the exam in maximum 90 minutes.
    # '''

    # system_prompt = build_system_prompt('test', 'blablabla', 0, tools, materials, template=system_prompt_template)
    # # print(system_prompt)
    # init_state: ExamState = {
    #     "occupation": row["occupation"],
    #     "task_id": str(row["task_id"]),  # Convert task_id to a string
    #     "task_description": row["task_description"],
    #     "exam_author_model": model,

    #     # Map your row fields to the typed dict fields
    #     "tools": safe_eval(row["required_tools_standard"]),
    #     "materials": safe_eval(row["required_materials_standard"]),

    #     # Provide defaults or placeholders for the rest
    #     "exam": {},
    #     "system_prompt": "",
    #     "overview": "",
    #     "instructions": "",
    #     "materials_all": "",
    #     "materials_candidate": "",
    #     "submission": "",
    #     "evaluation": "",
    #     "grading": "",
    #     "answer_key": "",

    #     "errors": [],
    #     "check_real_materials": True,
    #     "check_no_internet": True,
    #     "failed_candidate_materials": 0,
    #     "key_grade_threshold": 99.0,
    #     "key_grade": 0.0,
    #     "answer_key_count": 0,
    #     "check_overall_makes_sense": True,
    #     "explanation_overall_makes_sense": ""
    # }

    # # Now just invoke the compiled graph with that initial state
    # result_state = graph.invoke(init_state)

    # #print(result_state)
    # print('done')

    #g   = graph.get_graph()


        # # Mermaid text
        # print(g.draw_mermaid())

    # # display(Image(g.draw_mermaid_png()))

# ##### Now run on a real dataframe

# Iterate over each row in the DataFrame
for _, row in df_tasks.iterrows():  # Use iterrows() to iterate over rows
    # Initialize the state for the current row
    
    init_state: ExamState = {
        "occupation": row["occupation"],
        "task_id": str(row["task_id"]),  # Convert task_id to a string
        "task_description": row["task_description"],
        "exam_author_model": model,

        # Map your row fields to the typed dict fields
        "tools": safe_eval(row["required_tools_standard"]),
        "materials": safe_eval(row["required_materials_standard"]),

        # Provide defaults or placeholders for the rest
        "exam": {},
        "system_prompt": "",
        "overview": "",
        "instructions": "",
        "materials_all": "",
        "materials_candidate": "",
        "submission": "",
        "evaluation": "",
        "grading": "",
        "answer_key": "",

        "errors": [],
        "check_real_materials": True,
        "check_no_internet": True,
        "failed_candidate_materials": 0,
        "key_grade_threshold": 99.0,
        "key_grade": 0.0,
        "answer_key_count": 0,
        "check_overall_makes_sense": True,
        "explanation_overall_makes_sense": ""
    }
    print(init_state['task_id'])
    try:
        # Invoke the compiled graph with the initial state
        result_state = graph.invoke(init_state)
        # Append the result_state to the list
        result_states.append(result_state)
    except Exception as e:
        # Handle any errors during graph invocation
        print(f"Error processing task_id {row['task_id']}: {e}")
        # Append an error state to the list for debugging
        result_states.append({
            "occupation": row["occupation"],
            "task_id": row["task_id"],
            "task_description": row["task_description"],
            "exam_author_model": model,
            "errors": [str(e)]
        })

# # Convert the list of result states into a DataFrame
    #result_states.append(result_state)
    #result_states.append(result_state)

    df_result_states = pd.DataFrame(result_states)

    df_result_states.to_csv("../../data/exam_approach/test_results/{}/management_occupations_exams.csv".format(model), index=False)

# # # Save the resulting DataFrame to a CSV file (optional)
    df_result_states.to_csv("../../data/exam_approach/test_results/management_occupations_exams.csv", index=False)
