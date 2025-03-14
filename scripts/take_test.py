import pandas as pd
import pandas as pd
import random
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anthropic
import regex as re
import json
import subprocess
import shutil

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


test_prompt_template = """Instructions: <instructions> {answer_instructions} </instructions>
Answer materials: <materials> {answer_materials} </materials>
Submission instructions: <submission_instructions> {answer_submission} </submission_instructions>"""

system_prompt_template = """You are an expert worker within the domain of {occupation}. Complete the following test."""


def query_deepseek(row,  system_prompt_template, test_prompt_template, model="deepseek-chat", top_p=0.1):
    print("Putting DeepSeek to the test")
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        test_prompt = test_prompt_template.format(
        answer_instructions = row['answer_instructions'],
        answer_materials = row['answer_materials'],
        answer_submission = row['answer_submission']

        )
        
        message = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt_template.format(occupation=row['occupation'])},
                {"role": "user", "content": test_prompt},
            ],
            top_p=top_p
        )

        return message.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None
def query_chatgpt(row, system_prompt_template, test_prompt_template, model="gpt-4o", top_p=0.1):
    print("Putting ChatGPT to the test")

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        test_prompt = test_prompt_template.format(
        answer_instructions = row['answer_instructions'],
        answer_materials = row['answer_materials'],
        answer_submission = row['answer_submission']

        )
        
        message = client.chat.completions.create(
            messages=[
                {"role": "developer", "content": system_prompt_template.format(occupation=row['occupation'])},
                {
                    "role": "user",
                    "content": test_prompt
                }
            ],
            model=model,
            top_p=top_p,
            max_tokens =4096
        )
        return message.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def query_claude(row, system_prompt_template, test_prompt_template, model="claude-3-7-sonnet-20250219", top_p=0.1):
    print("Putting Claude to the test")

    try:
        client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=ANTHROPIC_API_KEY
        )

        test_prompt = test_prompt_template.format(
            answer_instructions = row['answer_instructions'],
            answer_materials = row['answer_materials'],
            answer_submission = row['answer_submission']

        )

        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system = system_prompt_template.format(occupation=row['occupation']),
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            top_p=top_p
        )
        out = message.content[0].text
        return out
    except Exception as e:
        print(f"Error: {e}")
        return None


def save_answer_json(row, path, model):
    folder = os.path.join(path, str(row['task_id']).replace(".", "_"))
    try:
        answer_json = json.loads(re.search(r'```json(.*?)```', row['test_answers_'+model], re.DOTALL).group(1).strip())
    except Exception as e:
        answer_json='{}'
    json_path = os.path.join(path, str(row['task_id']),'/')
    os.makedirs(folder+'/'+model, exist_ok=True)

    with open(folder+'/'+model+"/test_submission.json", "w") as json_file:
        json.dump(answer_json, json_file, ensure_ascii=False, indent=4)

def save_evaluation(row, path):
    print(path)
    folder = os.path.join(path, str(row['task_id']).replace(".", "_"))
    eval_file = re.search(r'```python(.*?)```', row['answer_grading'], re.DOTALL).group(1).strip()
    # Create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    # Write to the Python file
    with open(folder+'/task_evaluation.py', "w", encoding="utf-8") as py_file:
        py_file.write(eval_file)

def save_answer_key(row, path):
    folder = os.path.join(path, str(row['task_id']).replace(".", "_"))
    answer_file = json.loads(re.search(r'```json(.*?)```', row['answer_evaluation'], re.DOTALL).group(1).strip())
    # Create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # Write to the Python file
    with open(folder+'/answer_key.json', "w", encoding="utf-8") as json_file:
        json.dump(answer_file, json_file, ensure_ascii=False, indent=4)


def run_evaluation(row,path, model):
    folder = os.path.join(path, '12865_0')
    print("Running python", folder+"/task_evaluation.py")
    print("Evaluating ", model)
    print(os.getcwd())
    try:
        subprocess.run(
            ["python", "../task_evaluation.py"],
            cwd=f"../data/test_results/12865_0/{model}",  # Use f-string for clarity
            check=True  # Raise an exception if the command fails
        )
        print("Script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Script failed with return code {e.returncode}")
        print(f"Error Output:\n{e.stderr}")
    except FileNotFoundError:
        print("Error: The script or directory was not found. Check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

  


def copy_answer_key(row,folder):
    parent_directory = folder+'/'+str(row['task_id']).replace(".", "_")
    source_file = parent_directory+'/answer_key.json'
    # Iterate over all subdirectories
    for subdir in next(os.walk(parent_directory))[1]:  # Get only subfolder names
        subdir_path = os.path.join(parent_directory, subdir)  # Full path to subfolder
        destination = os.path.join(subdir_path, os.path.basename(source_file))  # Destination path
        
        # Copy the file
        shutil.copy(source_file, destination)
        print(f"Copied {source_file} to {destination}")


if __name__ == "__main__":

    
    df = pd.read_csv('../data/task_prompts/task_prompts_business_and_financial_operations_occupations.csv')
    #df = pd.read_csv('../data/test_results/test_results_business_and_financial_operations_occupations.csv')
    #df = df[df['task_id']==12865]
    print(df.shape)
    df['test_answers_claude'] = df.apply(query_claude,axis=1, args=(system_prompt_template, test_prompt_template, ))
    df['test_answers_chatgpt'] = df.apply(query_chatgpt,axis=1, args=(system_prompt_template, test_prompt_template,))
    df['test_answers_deepseek'] = df.apply(query_deepseek,axis=1, args=(system_prompt_template, test_prompt_template,))

    df.apply(save_answer_json, axis=1, args=('../data/test_results/', 'chatgpt'))
    df.apply(save_answer_json, axis=1, args=('../data/test_results/', 'claude'))
    df.apply(save_answer_json, axis=1, args=('../data/test_results/', 'deepseek'))
    df.apply(save_evaluation, axis=1, args=('../data/test_results/',))
    df.apply(save_answer_key, axis=1, args=('../data/test_results/',))

    df.apply(copy_answer_key, axis=1, args=('../data/test_results/',))

    df.apply(run_evaluation, axis=1, args=('../data/test_results/','claude',))
    df.apply(run_evaluation, axis=1, args=('../data/test_results/','chatgpt',))
    df.apply(run_evaluation, axis=1, args=('../data/test_results/','deepseek',))





    #df.to_csv('../data/test_results/test_results_business_and_financial_operations_occupations.csv')