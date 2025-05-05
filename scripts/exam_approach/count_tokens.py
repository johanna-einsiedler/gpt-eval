# import google.generativeai as genai
from build_exam_langchain import *
import anthropic
import pandas as pd
#dotenv_path = find_dotenv()
#load_dotenv(dotenv_path)
#from query_agents import query_agent, take_test
prompt_overview ='''### Your assignment:
    Provide a brief explanation of the exam's purpose and structure for the evaluator.
    '''
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

prompt_check_fake_image = """
You are a system verifying if the provided instructions and/or materials falsely claim to include an image, but it is only a description. 
If the materials explicitly claim they have an image but only provide a textual description, 
and that image is crucial for at least one task, respond with "Y". 
In all other cases (including no mention of an image at all), respond with "N". 
Return only "Y" or "N".
"""
prompt_check_fake_website = """
You are a system verifying whether the instructions and/or materials provided reference a publicly available website or news source that appears to be fabricated. 
It is acceptable if the materials reference an internal document, company guidelines, accounting statements or well known public documents. 
However, if the materials claim to reference a real, publicly accessible website or piece of news (e.g., something you would expect to find only online) 
and that url or texts  appears to be made up, respond with "Y". 
In all other cases, respond with "N". 
Return only "Y" or "N".
"""


system_prompt_makes_sense = f"""
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

user_message_makes_sense = f"""
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

if __name__ == "__main__":
    occupations =['Business and Financial Operations Occupations',
    'Computer and Mathematical Occupations',
    'Management Occupations']

    occupations_file_names = [occ.lower().replace(' ', '_') for occ in occupations]

    exam_list = pd.DataFrame()
    for occ in occupations_file_names:
        results = pd.read_csv(f'../../data/exam_approach/test_results/claude-3-7-sonnet-20250219/test_results_{occ}.csv',index_col=0)
        results = results.loc[:, ~results.columns.str.startswith('Unnamed')]
        results['occupation_group'] = occ
        exam_list = pd.concat([exam_list, results], axis=0, ignore_index=True)
    
    client = anthropic.Anthropic()

    row = exam_list.iloc[0]
    state = row
    token_count = []
    prompts = [prompt_overview, prompt_template_instructions, prompt_template_materials, prompt_template_submission,    prompt_template_evaluation,prompt_template_grading]
    prompt_names = ['prompt_overview', 'prompt_template_instructions',' prompt_template_materials',' prompt_template_submission','    prompt_template_evaluation','prompt_template_grading']

    # get token count for all prompts for exam generation
    for prompt, name in zip(prompts, prompt_names):
        response = client.messages.count_tokens(
        model='claude-3-7-sonnet-20250219',
        system= row['system_prompt'],
        messages=[{
            "role": "user",
            "content": prompt
        }],
        )
        token_count.append({name: response.input_tokens})

    outputs = [ 'overview',
       'instructions', 'materials_all', 'submission','evaluation', 'grading', 'answer_key']
    # get tokens for outputs
    for output in outputs:
        
        response = client.messages.count_tokens(
        model='claude-3-7-sonnet-20250219',
        #system= row['system_prompt'],
        messages=[{
            "role": "user",
            "content":row[output],
        }],
        )
        token_count.append({output: response.input_tokens})
    print(token_count)