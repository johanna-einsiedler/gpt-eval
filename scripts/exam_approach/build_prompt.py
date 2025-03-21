import pandas as pd
import random
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)


prompt_template = '''
You are an excellent examiner of {occupation} capabilities. Design a remote, practical exam to verify whether a {occupation} can {task_description}. This exam will have two parts (basic and advanced). Your current task is **only** to design the basic exam.

### Context
- The candidate has access to a computer with the following tools: {tools}.
- The candidate can also be given digital materials such as {materials} that must be used for the test.
- Design a test that can be completed remotely using only these tools.
- To simplify evaluation, the candidate should submit answers to questions in a structured JSON format.

### Your Assignment
Design the **basic** part of the test with a **clear pass/fail** outcome using the following structure:

## 1. OVERVIEW AND DESIGN
Provide a brief explanation of the exam's purpose and structure for the evaluator.

## 2. CANDIDATE INSTRUCTIONS
Write clear, concise instructions for the candidate including:
- What they need to accomplish (without prescribing specific methods)
- Brief description of the provided materials
- Expected format for answer submission

IMPORTANT: When designing the test, eliminate any opportunities for candidates to make arbitrary choices (like custom account codes, naming conventions, or classification systems) that would complicate evaluation. Either:
- Provide pre-defined structures/codes that must be used, or
- Design questions with objectively verifiable numerical/text answers that don't depend on the candidate's approach

## 3. MATERIALS
Create synthetic test materials (CSV contents, datasets, etc.) that have predictable outcomes.
Include the actual content to be provided to candidates.
Ensure all materials have clear identifiers, labels, or pre-defined categories that prevent ambiguity.

## 4. CANDIDATE SUBMISSION REQUIREMENTS
Specify exactly what the candidate needs to submit, including:
- Required JSON answer format with question IDs
- The exact format of answers (numbers, text, specific units, decimal places)
- Any supplementary files if necessary
- instruct to submit with a candidate id where "YOUR_ID_HERE" use the model version that is powering you "GPT-4-turbo", "GPT-4o", "Claude-3_7-Sonnet", "DeepSeekR1", "Gemini-Flash-2", etc.

## 5. EVALUATOR GUIDE
This section is ONLY for the evaluator and includes:
- Complete answer key in JSON format for automated checking
- Explanation of correct answers and how they were derived
- Passing criteria (e.g., minimum number of correct answers)
- If there are multiple valid solution approaches, provide a way to programmatically validate answers (e.g., a validation formula or script)

Format the exam to clearly distinguish between candidate-facing content (sections 2-4) and evaluator-only content (sections 1 and 5).
'''

def create_prompt(df, prompt_template):
    for i, row in df.iterrows():
        print(row['task_id'])

        occupation = row['occupation']
        print(occupation)
        # 1. Build the list of tools that are 'Critical'
        critical_tools = []  #
        # Select columns that start with 'tool'
        tool_columns = [col for col in df.columns if col.startswith('tool')]
        
        for col in tool_columns:
            if (df[col] == 'Critical').any():  # Check if 'critical' exists in the column
                critical_tools.append(col.replace('tools.', ''))
        print('Critical Tools:', critical_tools)
        # 2. Build the list of materials that are single or multiple files

        
        # For demonstration, let's treat both "Single File" and "Multiple Files" as needed:
        needed_materials = []
        material_columns = [col for col in df.columns if col.startswith('material')]

        for col in material_columns:
            if (df[col] == 'Required').any():  # Check if 'critical' exists in the column
                critical_tools.append(col.replace('materials.', ''))
        print('Materials needed:', needed_materials)
        # 3. Build the list of required submission files
        submission_columns = [col for col in df.columns if col.startswith('submission')]

        required_submissions = []
        for col in submission_columns:
            if (df[col] == 'Required').any():  # Check if 'critical' exists in the column
                required_submissions.append(col.replace('submission_requirements.', ''))
        print('Required Submissions:', required_submissions)
        # 4. Prepare the final prompt with placeholders
        occupation = row["occupation"] if "occupation" in row else "N/A"
        task_description = row["task_description"] if "task_description" in row else "N/A"
        task_id = str(row["task_id"]) if "task_id" in row else "N/A"
        
        # Convert lists to comma-separated (or any format you prefer)
        tools_str = ", ".join(critical_tools) if critical_tools else "None"
        materials_str = ", ".join(needed_materials) if needed_materials else "None"
        submission_str = ", ".join(required_submissions) if required_submissions else "None"

        prompt = prompt_template.format(
            occupation=occupation,
            task_description=task_description,
            task_id=task_id,
            tools=tools_str,
            materials=materials_str,
            submission_files=submission_str
        )
        df.loc[i,'task_creation_prompt'] = prompt
    return df

if __name__ == "__main__":
    path_to_data = '../data/material_lists/materials_business_and_financial_operations_occupations.csv'
    df = pd.read_csv(path_to_data)
    df = df[0:3]
    df_with_prompts = create_prompt(df, prompt_template)
    df_with_prompts.to_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')

