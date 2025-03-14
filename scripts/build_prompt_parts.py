import pandas as pd
import random
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anthropic
import regex as re


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# client = OpenAI(
#     api_key=OPENAI_API_KEY
# )


system_prompt_template = '''
You are an excellent examiner of {occupation} capabilities. Design a remote, practical exam to verify whether a {occupation} can {task_description}. This exam will have two parts (basic and advanced). Your current task is **only** to design the basic exam.

### Context
{tools_instructions}
{materials_instructions}
- Design a test that can be completed remotely using only these tools.
- To simplify evaluation, the candidate should submit answers to questions in a structured JSON format. The JSON file should have the name "test_submission.json".
'''

prompt_overview ='''

### Your assignment
Provide a brief explanation of the exam's purpose and structure for the evaluator.
'''

prompt_template_instructions ='''
Here is brief explanation of the exam's purpose and structure intended for the evaluator: <examoverview> {answer_overview}</examoverview>

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

## Your assingment
Based on the given information, pecify exactly what the candidate needs to submit, including:
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

"""









def build_system_prompt(row, system_prompt_template):

    if isinstance(row['required_tools'],(tuple, list)):
        tools_instructions = """- The candidate has access to a computer with the following tools:""" + ", ".join(row['required_tools'])
    else: 
        tools_instructions = """- The candidate does not have access to a computer."""

    if isinstance(row['required_materials'],(tuple, list)):
        materials_instructions = """- The candidate can also be given digital materials such as""" +\
             + ", ".join(row['required_tools']) + """that must be used for the test."""
    else:
        materials_instructions = """- The candidate does not have access to any additional digital materials."""


    system_prompt = system_prompt_template.format(
        occupation=row['occupation'],
        task_description=row['task_description'],
        task_id=row['task_id'],
        tools_instructions= tools_instructions,
        materials_instructions= materials_instructions
        #submission_files=", ".join(row['required_submission']) if isinstance(row['required_submission'],(tuple, list)) else 'None'
    )
    return system_prompt

def build_instructions_prompt(row, prompt_template_instructions):
    prompt_instructions = prompt_template_instructions.format(
        answer_overview = row['answer_overview']
        )
    return prompt_instructions

def build_materials_prompt(row, prompt_template_materials):
    prompt_materials = prompt_template_materials.format(
    answer_overview = row['answer_overview'],
    answer_instructions = row['answer_instructions']
    )
    return prompt_materials

def build_prompts(row, prompt_template):
    placeholders = re.findall(r'\{(.*?)\}', prompt_template)
    prompt = prompt_template.format(**{ph: row[ph] for ph in placeholders})

    # prompt = prompt_template.format(
    # answer_overview = row['answer_overview'],
    # answer_instructions = row['answer_instructions'] if row['answer_instructions'] else None,
    # answer_materials = row['answer_materials'] if row['answer_materials'] else None,
    # answer_submission = row['answer_submission'] if row['answer_submission'] else None,
    # answer_evaluation = row['answer_evaluation'] if row['answer_evaluation'] else None
    # )
    return prompt



def query_LLM(row,  col):
    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=ANTHROPIC_API_KEY
    )
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=8192,
        system = row['system_prompt'],
        messages=[
            {"role": "user", "content": row[col]}
        ]
    )
    out = message.content[0].text
    return out





if __name__ == "__main__":
    path_to_data = '../data/material_lists/materials_business_and_financial_operations_occupations.csv'
    df = pd.read_csv(path_to_data)
    #    # subset to tasks that don't require imaging stuff for now
    df = df[(df['tools.Image Generator'] == 'Not Required') * (df['tools.PowerPoint'] =='Not Required')* (df['tools.Web Browser'] =='Not Required')*\
        (df['tools.PDF viewer'] =='Not Required')] # * df['tools.Excel'] =='Necessary']
    #  subset to 10 tasks 
    df = df[0:5]

    df["system_prompt"] = df.apply(build_system_prompt, axis=1, args=(system_prompt_template,))

    # # get 1. OVERVIEW
    print('Generating overview')
    df["prompt_overview"] = prompt_overview
    df["answer_overview"] = df.apply(query_LLM, axis=1, args=('prompt_overview',))
    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

    # # get 2. INSTRUCTIONS
    print('Generating instructions')
    df['prompt_instructions'] = df.apply(build_prompts, axis=1, args=(prompt_template_instructions,))
    df['answer_instructions'] = df.apply(query_LLM, axis=1, args=('prompt_instructions',))
    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

    # get 3. MATERIALS
    print('Generating materials')
    df['prompt_materials'] = df.apply(build_prompts, axis=1, args=(prompt_template_materials,))
    df['answer_materials'] = df.apply(query_LLM, axis=1, args=('prompt_materials',))
    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

    # 4. SUBMISSION
    print('Generating submission requirements')
    df['prompt_submission'] = df.apply(build_prompts, axis=1, args=(prompt_template_submission,))
    df['answer_submission'] = df.apply(query_LLM, axis=1, args=('prompt_submission',))
    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

    # 4. EVALUATION
    print('Generating evaluation guide')
    df['prompt_evaluation'] = df.apply(build_prompts, axis=1, args=(prompt_template_evaluation,))
    df['answer_evaluation'] = df.apply(query_LLM, axis=1, args=('prompt_evaluation',))
    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

    # 5. GRADING
    print('Generating grading script')
    df['prompt_grading'] = df.apply(build_prompts, axis=1, args=(prompt_template_grading,))
    df['answer_grading'] = df.apply(query_LLM, axis=1, args=('prompt_grading',))



    df.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')
    print('Finished! Processed '+str(df.shape[0]) +' tasks!')
    # test = pd.read_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')
    # print(test.columns)
    # test['prompt_instructions'] = test.apply(build_prompts, axis=1, args=(prompt_template_instructions,))
