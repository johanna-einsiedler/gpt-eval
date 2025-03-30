import pandas as pd
import random
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anthropic
import regex as re
from query_agents import query_agent
import sys
import ast

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# client = OpenAI(
#     api_key=OPENAI_API_KEY
# )
 # practical tests 
 # if not possible -> say no 

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
- Design questions with objectively verifiable numerical/text answers that don't depend on the candidate's approach

'''

prompt_template_materials = """
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>

## Your assignment:
- If the exam doesn't require any additional material, just respond with "No material required".
- Else create synthetic test materials (CSV contents, datasets, etc.) that have predictable outcomes. Include the actual content to be provided to candidates and ensure all materials have clear identifiers, labels, or pre-defined categories that prevent ambiguity.

IMPORTANT: When designing the test, eliminate any opportunities for candidates to make arbitrary choices (like custom account codes, naming conventions, or classification systems) that would complicate evaluation. Either:
- Provide pre-defined structures/codes that must be used, or
- Design questions with objectively verifiable numerical/text answers that don't depend on the candidate's approach
"""

prompt_template_submission = """
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>
Here are the instructions for the candidate: <instructions> {answer_instructions} </instructions>
Here are the materials provided to the candidate: <materials> {answer_materials} </materials>

## Your assignment
Based on the given information, specify exactly what the candidate needs to submit, including:
- Required JSON answer format with question IDs
- The exact format of answers (numbers, text, specific units, decimal places)
- Any supplementary files if necessary
- instruct to submit with a candidate id where "YOUR_ID_HERE" use the model version that is powering you "GPT-4-turbo", "GPT-4o", "Claude-3_7-Sonnet", "DeepSeekR1", "Gemini-Flash-2", etc.


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
- If there are multiple valid solution approaches, provide a way to programmatically validate answers (e.g., a validation formula or script)
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


def custom_join_or(lst):
    """
    Joins a list of strings with commas and the word 'or' before the last item.

    Args:
        lst (list): A list of strings to join.

    Returns:
        str: A string with the list items joined by commas and 'or', or an empty string if the list is empty.
    
    Examples:
        custom_join_or(['apple', 'banana', 'cherry']) -> "apple, banana or cherry"
        custom_join_or(['apple']) -> "apple"
        custom_join_or([]) -> ""
    """
    if len(lst) > 1:
        return ", ".join(lst[:-1]) + " or " + lst[-1]
    elif lst:
        return lst[0]
    else:
        return ""  # If the list is empty

def custom_join_and(lst):
    """
    Joins a list of strings with commas and the word 'and' before the last item.

    Args:
        lst (list): A list of strings to join.

    Returns:
        str: A string with the list items joined by commas and 'and', or an empty string if the list is empty.
    
    Examples:
        custom_join_and(['apple', 'banana', 'cherry']) -> "apple, banana and cherry"
        custom_join_and(['apple']) -> "apple"
        custom_join_and([]) -> ""
    """
    if len(lst) > 1:
        return ", ".join(lst[:-1]) + " and " + lst[-1]
    elif lst:
        return lst[0]
    else:
        return ""  # If the list is empty


def build_system_prompt(row, system_prompt_template, standard=True):
    """
    Builds a system prompt for designing a practical exam based on the given row of data.

    Args:
        row (pd.Series): A row of data containing information about the task, including required tools, materials, 
                         occupation, and task description.
        system_prompt_template (str): A template string for the system prompt with placeholders for dynamic content.
        standard (bool): A flag indicating whether to use the standard tools and materials fields 
                         (default is True). If False, non-standard fields are used.

    Returns:
        str: A formatted system prompt string with the provided task details.

    Example:
        row = {
            'occupation': 'data scientist',
            'task_description': 'analyze a dataset',
            'task_id': '123',
            'required_tools_standard': "['Python', 'Jupyter Notebook']",
            'required_materials_standard': "['sample_dataset.csv']"
        }
        system_prompt_template = "You are an examiner of {occupation} capabilities. {tools_instructions} {materials_instructions}"
        build_system_prompt(row, system_prompt_template)

        Output:
        "You are an examiner of data scientist capabilities. - The candidate has access to a computer with the following tools: Python and Jupyter Notebook. - The candidate can also be given digital materials such as sample_dataset.csv that must be used for the test."
    """
    if standard:
        required_tools = ast.literal_eval(row['required_tools_standard'])
        required_materials = ast.literal_eval(row['required_materials_standard'])
    else:
        required_tools = ast.literal_eval(row['required_tools'])
        required_materials = ast.literal_eval(row['required_materials'])

    if isinstance(required_tools, (tuple, list)):
        tools_instructions = """- The candidate has access to a computer with the following tools: """ + custom_join_and(required_tools)
    else: 
        tools_instructions = """- The candidate does not have access to any special tools."""

    if isinstance(required_materials, (tuple, list)):
        materials_instructions = """- The candidate can also be given digital materials such as """ + \
            custom_join_or(required_materials) + """ that must be used for the test."""
    else:
        materials_instructions = """- The candidate does not have access to any additional digital materials."""

    system_prompt = system_prompt_template.format(
        occupation=row['occupation'],
        task_description=row['task_description'],
        task_id=row['task_id'],
        tools_instructions=tools_instructions,
        materials_instructions=materials_instructions
    )
    print(system_prompt)
    return system_prompt


def build_prompts(row, prompt_template):
    """
    Builds a formatted prompt by replacing placeholders in the template with values from the given row.

    Args:
        row (pd.Series): A row of data containing key-value pairs where keys correspond to placeholders 
                         in the prompt template.
        prompt_template (str): A string template containing placeholders in the format {placeholder_name}.

    Returns:
        str: A formatted string where placeholders in the template are replaced with corresponding values 
             from the row.

    Example:
        row = {
            'answer_overview': 'This is an overview.',
            'answer_instructions': 'These are instructions.'
        }
        prompt_template = "Overview: {answer_overview}, Instructions: {answer_instructions}"
        build_prompts(row, prompt_template)

        Output:
        "Overview: This is an overview., Instructions: These are instructions."
    """
    placeholders = re.findall(r'\{(.*?)\}', prompt_template)
    prompt = prompt_template.format(**{ph: row[ph] for ph in placeholders})
    return prompt


def run_query(row, prompt, model):
    response = query_agent(row['system_prompt'], row[prompt], model)
    return response

if __name__ == "__main__":



    if len(sys.argv) >1:
        path_to_data = sys.argv[1]
    else:
        #path_to_data = '../../data/exam_approach/material_lists/'
        path_to_data = '../../data/exam_approach/exams/'

    if len(sys.argv)>2:
        overwrite = sys.argv[3]
    else:
        overwrite = True



    # read in list of task ids to be excluded
    exclusion_list = pd.read_csv('../../data/exam_approach/exclusion_lists/presention_image_audio_video_virtual_all.csv',index_col=0).rename(columns={'0':'task_id'})
    
  for root, dirs, files in os.walk(path_to_data):
    # Iterate over models (subdirectories) in the current root directory
    for model in dirs:
        print('Generating exams using', model)

        # Create the output directory for the current model if it does not exist
        output_dir = f'../../data/exam_approach/exams/{model}/'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Process files in the model's directory
        model_path = os.path.join(root, model)  # Construct the full path to the model directory
        for file in os.listdir(model_path):  # Use os.listdir instead of os.walk for files in the model
            file_path = os.path.join(model_path, file)  # Full path to the file

            # Only process CSV files
            if file.endswith('.csv') and os.path.isfile(file_path):
                print(f"Processing file: {file_path}")
                df = pd.read_csv(file_path)
                print(f"Overall {df.shape[0]} tasks in the data\n")
                if overwrite == False:
                    existing_df = pd.read_csv(f'../../data/exam_approach/exams/{model}/exams_{file.replace("task_list_","")}')
                    df = df[~df['task_id'].isin(existing_df['task_id'])]
                print('Processing ', df.shape[0], ' new tasks.')
                df = df[~df['task_id'].isin(exclusion_list['task_id'])]
                print('After applying tools and materials exclusion criteria there are ', df.shape[0], ' tasks left.')
                df["system_prompt"] = df.apply(build_system_prompt, axis=1, args=(system_prompt_template,))
                
                # get 1. OVERVIEW
                print('Generating overview')
                df["prompt_overview"] = prompt_overview
                df["answer_overview"] = df.apply(run_query, axis=1, args=('prompt_overview',model,))

                # get 2. INSTRUCTIONS
                print('Generating instructions')
                df['prompt_instructions'] = df.apply(build_prompts, axis=1, args=(prompt_template_instructions,))
                df['answer_instructions'] = df.apply(run_query, axis=1, args=('prompt_instructions',model, ))


                get 3. MATERIALS
                print('Generating materials')
                df['prompt_materials'] = df.apply(build_prompts, axis=1, args=(prompt_template_materials,))
                df['answer_materials'] = df.apply(run_query, axis=1, args=('prompt_materials',model,))


                4. SUBMISSION
                print('Generating submission requirements')
                df['prompt_submission'] = df.apply(build_prompts, axis=1, args=(prompt_template_submission,))
                df['answer_submission'] = df.apply(run_query, axis=1, args=('prompt_submission',model,))


                4. EVALUATION
                print('Generating evaluation guide')
                df['prompt_evaluation'] = df.apply(build_prompts, axis=1, args=(prompt_template_evaluation,))
                df['answer_evaluation'] = df.apply(run_query, axis=1, args=('prompt_evaluation',model,))

                # 5. GRADING
                print('Generating grading script')
                df['prompt_grading'] = df.apply(build_prompts, axis=1, args=(prompt_template_grading,))
                df['answer_grading'] = df.apply(run_query, axis=1, args=('prompt_grading',model,))
            
                if overwrite == False:
                    pd.concat([existing_df,df]).to_csv(f'../../data/exam_approach/exams/{model}/exams_{file.replace("task_list_","")}')
                else:
                    df.to_csv(f'../../data/exam_approach/exams/{model}/exams_{file.replace("task_list_","")}')
                    print('saved to ', f'../../data/exam_approach/exams/{model}/exams_{file.replace("task_list_","")}')
        print('Finished! Processed '+str(df.shape[0]) +' tasks!')
