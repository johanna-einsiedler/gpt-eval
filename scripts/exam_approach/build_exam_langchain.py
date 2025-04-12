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

from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI  # or your equivalent import
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import START
from langgraph.graph import END


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# llm = ChatOpenAI(model="gpt-3.5-turbo")

# Initialize Claude Haiku
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",  # Claude Haiku model
    anthropic_api_key=ANTHROPIC_API_KEY
)

# Initialize Claude Haiku
llm = ChatAnthropic(
    model= 'claude-3-7-sonnet-20250219',  # Claude Haiku model
    anthropic_api_key=ANTHROPIC_API_KEY
)
prompt = "How much is 2 + 2?"

# 1. Using __call__ (direct function call)
response_via_call = llm(prompt)
response_via_call.content


system_prompt_template = '''
You are an excellent examiner of {occupation} capabilities. Design a remote, **practical** exam to verify whether a {occupation} can {task_description}.
 This exam will have two parts (basic and advanced). Your current task is **only** to design the basic exam.

### Context
{tools_instructions}
{materials_instructions}
- Design a **practical** exam that can be completed remotely using only these tools. A practical exam is a an exam actually testing whether the described task can be performed successfully. An exam testing the knowledge about the task is NOT a practical exam.
- To simplify evaluation, the candidate should submit answers to questions in a structured JSON format. The JSON file should have the name "test_submission.json".
'''

prompt_overview ='''

### Your assignment
Provide a brief explanation of the exam's purpose and structure for the evaluator.
'''

prompt_template_instructions ='''
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview} </examoverview>

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

prompt_template_materials = """
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
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
"""

prompt_check_fake_image = """
You are a system verifying if the provided materials falsely claim to include an image, but it is only a description. 
If the materials explicitly claim they have an image but only provide a textual description, 
and that image is crucial for at least one task, respond with "Y". 
In all other cases (including no mention of an image at all), respond with "N". 
Return only "Y" or "N".
"""

prompt_check_fake_website = """
You are a system verifying whether the provided materials reference a publicly available website or news source that appears to be fabricated. 
It is acceptable if the materials reference an internal document, company guideline, accounting statement or well known public documents. 
However, if the materials claim to reference a real, publicly accessible website or piece of news (e.g., something you would expect to find online) 
and that url or texts  appears to be made up, respond with "Y". 
In all other cases, respond with "N". 
Return only "Y" or "N".
"""


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

prompt_template_grading ="""
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
Here are the materials provided to the candidate: <materials> {answer_materials} </materials>
Here are the submission requirements for the candidate: <submission_requirements> {answer_submission} </submission_requirements>
Here is the information given to the evaluator: <evaluation_information> {answer_evaluation} </evaluation_information>

## Your assignment
Based on the given information create a python script named 'task_evaluation.py' that reads in the candidate submission ('test_submission.json') and reads in the answer key ('answer_key.json') provided, placed in the same folder as 'task_evaluation.py'.
Then the script should automatically score the test performance and save the result as 'test_results.json' in the same folder. 
In addition to the detailed test results, 'test_results.json' should include one variable 'overall_score' with the percentage of points achieved by the candidate.

"""


def safe_eval(value, default=[]):
    if pd.isna(value):
        return default
    try:
        return ast.literal_eval(value)
    except:
        return default

def join_items(items, conj='and'):
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



row = {
    'occupation': 'Wholesale and Retail Buyers, Except Farm Products',
    'task_description': 'Recommend mark-up rates, mark-down rates, or merchandise selling prices.',
    'task_id': 'TASK123',
    'required_tools_standard': "['Spreadsheets', 'PDF viewer']",
    'required_materials_standard': "['Text', 'Data']"
}


tools = safe_eval(row['required_tools_standard'])
materials = safe_eval(row['required_materials_standard'])

tools

prompt = build_system_prompt(
    occupation=row['occupation'],
    task_description=row['task_description'],
    task_id=row['task_id'],
    required_tools=tools,
    required_materials=materials,
    template=system_prompt_template
)

print(prompt)

row = {
    'occupation': 'Wholesale and Retail Buyers, Except Farm Products',
    'task_description': 'Recommend mark-up rates, mark-down rates, or merchandise selling prices.',
    'task_id': 'TASK123',
    'required_tools_standard': "[['Spreadsheets', 'PDF viewer']]",
    'required_materials_standard': "[['Text', 'Data']]"
}

class ExamState(TypedDict):
    occupation: str
    task_id: str
    task_description: str
    
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

    # Boolean flags for validation checks
    check_real_materials: bool
    check_no_internet: bool
    # Counters for failed checks that could be fixed interatively
    failed_answer_key_test:int
    

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
    '''

    state["system_prompt"] = build_system_prompt(occupation, task_description, task_id, required_tools, required_materials, template=system_prompt_template)

    return state


# 2. Query overview
def node_overview(state: ExamState) -> ExamState:
    prompt_overview ='''### Your assignment
    Provide a brief explanation of the exam's purpose and structure for the evaluator.
    '''

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
        print(msg)

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
    state["evaluation"] = llm(messages).content
    return state

def node_grading(state: ExamState) -> ExamState:
    prompt_template_grading ="""
    Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
    Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
    Here are the materials provided to the candidate: <materials> {answer_materials} </materials>
    Here are the submission requirements for the candidate: <submission_requirements> {answer_submission} </submission_requirements>
    Here is the information given to the evaluator: <evaluation_information> {answer_evaluation} </evaluation_information>

    ## Your assignment
    Based on the given information create a python script named 'task_evaluation.py' that reads in the candidate submission ('test_submission.json') and reads in the answer key ('answer_key.json') provided, placed in the same folder as 'task_evaluation.py'.
    Then the script should automatically score the test performance and save the result as 'test_results.json' in the same folder. 
    In addition to the detailed test results, 'test_results.json' should include one variable 'overall_score' with the percentage of points achieved by the candidate.
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


def node_check_materials_fake_image(state: ExamState) -> ExamState:
    prompt_check_fake_image = """
    You are a system verifying if the provided materials falsely claim to include an image, but it is only a description. 
    If the materials explicitly claim they have an image but only provide a textual description, 
    and that image is crucial for at least one task, respond with "Y". 
    In all other cases (including no mention of an image at all), respond with "N". 
    Return only "Y" or "N".
    """

    messages = [
        SystemMessage(content=prompt_check_fake_image),
        HumanMessage(content=state["materials_all"])
    ]

    if llm(messages).content == "Y":
        state["check_real_materials"] = False
    else:
        state["check_real_materials"] = True
    return state



def node_check_materials_fake_website(state: ExamState) -> ExamState:
    prompt_check_fake_website = """
    You are a system verifying whether the provided materials reference a publicly available website or news source that appears to be fabricated. 
    It is acceptable if the materials reference an internal document, company guidelines, accounting statements or well known public documents. 
    However, if the materials claim to reference a real, publicly accessible website or piece of news (e.g., something you would expect to find only online) 
    and that url or texts  appears to be made up, respond with "Y". 
    In all other cases, respond with "N". 
    Return only "Y" or "N".
    """
    
    messages = [
        SystemMessage(content=prompt_check_fake_website),
        HumanMessage(content=state["materials_all"])
    ]

    if llm(messages).content == "Y":
        state["check_no_internet"] = False
    else:
        state["check_no_internet"] = True
    return state


def route_after_image_check(state: ExamState) -> str:

    if state["check_real_materials"] == False:
        return "node_finish"
    else:
        return "node_check_websites"

def route_after_internet_check(state: ExamState) -> str:

    if state["check_no_internet"] == False:
        return "node_finish"
    else:
        return "node_submission"


def node_end(state: ExamState):
    pass

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
graph_builder.add_node("node_end", node_end)

#Add edges the graph
graph_builder.add_edge(START, "construct_system_prompt")
graph_builder.add_edge("construct_system_prompt", "node_overview")
graph_builder.add_edge("node_overview", "node_instructions")

### NOTE - probably add conditional edge depending on whether materials are required
graph_builder.add_edge("node_instructions", "node_materials")
graph_builder.add_edge("node_materials", "node_check_images")
### Add conditional edges if materials_fake_website or materials_fake_image then end the process
graph_builder.add_conditional_edges("node_check_images", route_after_image_check)
graph_builder.add_conditional_edges("node_check_websites", route_after_internet_check)

graph_builder.add_edge("node_submission", 'node_evaluation')
graph_builder.add_edge("node_evaluation", 'node_grading')
graph_builder.add_edge("node_grading", 'node_end')
graph_builder.add_edge("node_end", END)

graph = graph_builder.compile()

init_state: ExamState = {
    "occupation": row["occupation"],
    "task_id": row["task_id"],
    "task_description": row["task_description"],

    # Map your row fields to the typed dict fields
    "tools": row["required_tools_standard"],
    "materials": row["required_materials_standard"],

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

    "check_real_materials": True,
    "check_no_internet": True,
    "failed_answer_key_test": 0
}

# Now just invoke the compiled graph with that initial state
result_state = graph.invoke(init_state)

result_state



# graph_builder.add_edge("evaluation", "grading")
# graph_builder.set_finish_point("grading")

# graph = graph_builder.compile()

# for _, row in df.iterrows():
#     result = graph.invoke({"row": row.to_dict()})
#     results.append(result["row"])
