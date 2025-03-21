
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import json
import re

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# Function to call OpenAI API using the updated client
def run_openai_prompt(prompt: str, model: str):
    """
    Sends a prompt to the OpenAI API and returns the generated response.
    
    Parameters:
        prompt (str): The input prompt to send to the OpenAI API.
        model (str): The OpenAI model to use for generating responses.
        
    Returns:
        str: The generated response from the OpenAI API, or None if an error occurs.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=model,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_requirements(df: pd.DataFrame, prompt: str, model: str) -> pd.DataFrame:
    """
    Processes a DataFrame to generate OpenAI API responses based on formatted prompts.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame containing 'title', 'task', and 'task_id' columns.
        prompt (str): Template prompt with placeholders for occupation, task description, and task ID.
        model (str): OpenAI model to use for generating responses.
    
    Returns:
        pd.DataFrame: A DataFrame containing the original row index, formatted prompt, and parsed JSON output.
    """
    results = []

    for i, row in df.iterrows():
        try:
            # Extract variables for substitution
            occupation = row['title']
            task_description = row['task']
            task_id = row['task_id']

            # Format the prompt using the provided template
            prompt_formatted = prompt.format(
                occupation=occupation,
                task_description=task_description,
                task_id=task_id
            )
            #print(occupation)
            #print(prompt_formatted)
            # Run the prompt through OpenAI API
            output = run_openai_prompt(prompt_formatted, model)
            try:
                # Try to parse the output as JSON
                parsed_output = json.loads(output) if output else {}
            except:
                parsed_output = json.loads(re.search(r'```json\n(.*?)\n```', output, re.DOTALL).group(1))

        except Exception as e:
           print(f"Error processing row {i}: {e}")
           parsed_output = {}  # Fallback to an empty dictionary in case of errors

        # Build a result dictionary including row index, prompt, and parsed JSON output
        result = {"row": i, "prompt": prompt_formatted}
        result.update(parsed_output)
        results.append(result)

        # Print progress
        print(f"Processed row {i}")

    # Convert the results list into a DataFrame using json_normalize for structured output
    df_results = pd.json_normalize(results)
    return df_results



prompt=  '''
You are an excellent examiner of {occupation} capabilities. The overall objective is to evaluate, via a practical online exam without a time limit, whether {occupation} can {task_description}

Task ID: {task_id}

Your assignment is to determine if it is possible to design a meaningful exam for this task that can be performed remotely and to identify the required tools and materials for the evaluation. Remember that all tool and material assessments must be made with respect to the specific context of the given task and occupation.

**Definitions:**
- **Tools:** Software or applications (e.g., Python, Excel, Word, PowerPoint, Image Generators) that the candidate needs to use to complete the test.
- **Materials:** Digital content (e.g., CSV files, PDFs, images, audio files, virtual lab environments) that form part of the test content.
- **Submission Requirements:** The format(s) of the files the candidate must use when submitting their solution. The simplest format is **answering questions with exact answers**, but you may also require one or more files:  
  - `.md` (for text-based submissions, e.g., a detailed write-up)  
  - `.csv` (for data or spreadsheets)  
  - `.py` (for code in Python)


**Instructions:**

1. **Remote Feasibility:**  
   Evaluate whether the task can be performed online/remotely or if it requires in-person presence.
   - **If the task requires in-person presence:**  
     - Output `"can_be_performed_remotely": false`
     - For all other fields (tools and materials), output `"NA"` as the value.
   - **If the task can be performed remotely:**  
     - Output `"can_be_performed_remotely": true` and continue with the evaluation.

2. **Tools Required:**  
    For each tool listed below, assess its necessity for carrying out the task ({task_description}) in the role of {occupation}. Choose from the following options:
   - Not Required
   - Required
   
   Evaluate the following tools:
   - "coding/Python":
   - "Excel":
   - "Word":
   - "PDF viewer":
   - "PowerPoint":
   - "Image Generator":
   - "Web Browser":
   - "Other": (Should be "NA" unless it is impossible to do this task with the tools above and a different tool is needed, specify the tool name and its classification if so.)

3. **Materials Required:**  
    For each material listed below, determine whether it is required as a component of the test to evaluate {occupation}'s ability to perform the task ({task_description}). Choose from the following options:
   - Required
   - Not required

   Evaluate the following materials:
   - "Text Instructions":
   - "Text PDF reports, books, etc":
   - "Data, CSV":
   - "Images, PNG/JPG, etc":
   - "Audio files mp3":
   - "Audio files mp4":
   - "Virtual labs or sandbox environments":
    - "Other": (If the materials above are not enough and a different file format is needed, specify the material name and its classification; otherwise, use "NA".)

4. **Submission Requirements**
If `"can_be_performed_remotely" = true`, specify how the candidate should submit their work. Because we prefer to evaluate them through questions with exact short answers, that is listed first. If question-answering alone cannot fully assess the candidate, require one or more of the additional file types.

For each item, choose:
- **Required**
- **Not Required**
- **NA** (if not relevant)

These are the only allowed options:
- `"exact_answer_questions"` (set direct answers, no file)
- `"md"` (text-based submission)
- `"csv"` (data or spreadsheets)
- `"py"` (Python code)

5. **Chain-of-Thought Reasoning:**  
   Include a brief chain-of-thought explanation (in no more than 150 words) for your evaluations. If you choose to include this, add it in a separate field named `"chain_of_thought"`.  
   **Important:** Ensure that the final output adheres strictly to the JSON format provided and does not include any extra commentary outside of the designated JSON fields.

**Output Requirement:**  
Your response must be in valid JSON format following the structure provided below. Do not include any extra text or commentary outside of this JSON. The "/" delimit the options you can choose from

**Expected JSON Structure:**
{{
  "task_id": "{task_id}",
  "occupation": "{occupation}",
  "task_description": "{task_description}",
  "can_be_performed_remotely": true/false,
  "tools": {{
    "coding/Python": "Not Required/Required/NA",
    "Excel": "Not Required/Required/NA",
    "Word": "Not Required/Required/NA",
    "PDF viewer":"Not Required/Required/NA", 
    "PowerPoint": "Not Required/Required/NA",
    "Web Browser": "Not Required/Required/NA",
    "Image Generator": "Not Required/Required/NA",
    "Other": {{
      "name": "Tool Name/NA",
      "classification": "Not Required/Required/NA",
    }}
  }},
  "materials": {{
    "Text Instructions": "Not Required/Required/NA",
    "Text PDF reports, books, etc": "Not Required/Required/NA",
    "Data, CSV": "Not Required/Required/NA",
    "Images, PNG/JPG, etc": "Not Required/Required/NA",
    "Audio files mp3": "Not Required/Required/NA",
    "Audio files mp4": "Not Required/Required/NA",
    "Virtual labs or sandbox environments": "Not Required/Required/NA",
    "Other": {{
      "name": "Material Name/NA",
      "classification": "Not Required/Required/NA",
    }}
  }},
  "submission_requirements": {{
    exact_answer_questions": "Required/Not Required/NA",
    "md": "Required/Not Required/NA",
    "csv": "Required/Not Required/NA",
    "py": "Required/Not Required/NA"
    }}
  }},
  "chain_of_thought": "Brief explanation (no more than 150 words)."
}}

'''


def get_required(row: pd.Series, keyword: str, cols: List[str]) -> Union[List[str], str]:
    """
    Extracts required items from a row based on a given keyword.

    Parameters:
    -----------
    row : pd.Series
        A row from the DataFrame.
    keyword : str
        The keyword to remove from column names when adding to the required list.
    cols : List[str]
        The list of column names to check.

    Returns:
    --------
    List[str] or str
        A list of required items if found, otherwise an empty string.
    """
    required = [col.replace(keyword, '') for col in cols if row[col] == "Required"]
    return required if required else ''

def get_requirement_lists(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates lists of required tools, materials, and submission requirements for each row.

    Parameters:
    -----------
    df : pd.DataFrame
        A DataFrame containing tool, material, and submission requirement columns.

    Returns:
    --------
    pd.DataFrame
        The updated DataFrame with new columns: 'required_tools', 'required_materials', 'required_submission'.
    """
    tool_columns = [col for col in df.columns if col.startswith('tool')]
    df["required_tools"] = df.apply(get_required, axis=1, args=('tools.', tool_columns))

    material_columns = [col for col in df.columns if col.startswith('material')]
    df["required_materials"] = df.apply(get_required, axis=1, args=('materials.', material_columns))

    submission_columns = [col for col in df.columns if col.startswith('submission')]
    df["required_submission"] = df.apply(get_required, axis=1, args=('submission_requirements.', submission_columns))

    return df



if __name__ == "__main__":
    path_to_data = '../../data/task_lists/business_and_financial_operations_occupations_CORE.csv'
    df = pd.read_csv(path_to_data)
    df = df.rename(columns={'Task ID':'task_id', 'Task': 'task', 'Title':'title'})
    df = df[0:20]
    print(df.shape)

    # set to false if you want to add on to existing runs, set to true if you want to overwrite all ready exsiting material
    overwrite = False
    if ~overwrite:
        existing_df = pd.read_csv('../../data/exam_approach/material_lists/materials_business_and_financial_operations_occupations.csv')
        df = df[~df['task_id'].isin(existing_df['task_id'])]
        print(existing_df.shape)
        print(df.shape)

       # subset to
    print('Processing dataset with ', df.shape[0],' observations')
    out = get_requirements(df, prompt, model='gpt-4o')
    out = get_requirement_lists(out)
    if ~overwrite:
        out = pd.concat([existing_df,out])
    out.to_csv('../../data/exam_approach/material_lists/materials_business_and_financial_operations_occupations.csv')
