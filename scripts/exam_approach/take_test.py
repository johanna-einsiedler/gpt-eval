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
import google.generativeai as genai
from query_agents import query_agent, take_test
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# load openai api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


test_prompt_template = """Instructions: <instructions> {answer_instructions} </instructions>
Answer materials: <materials> {answer_materials} </materials>
Submission instructions: <submission_instructions> {answer_submission} </submission_instructions>"""
system_prompt_template = """You are an expert worker within the domain of {occupation}. Complete the following test."""


def save_answer_json(row, path, model):
    folder = os.path.join(path, str(row['task_id']).replace(".", "_"))
    try:
        answer_file = json.loads(re.search(r'```json(.*?)```', row['test_answers_'+model], re.DOTALL).group(1).strip())
    except:
        try:
            answer_file =  json.loads(row['test_answers_'+model])
        except:
            answer_file = '''{}'''
            return False
    json_path = os.path.join(path, str(row['task_id']),'/')
    os.makedirs(folder+'/'+model, exist_ok=True)

    with open(folder+'/'+model+"/test_submission.json", "w") as json_file:
        json.dump(answer_file, json_file, ensure_ascii=False, indent=4)

    return True

def save_evaluation(row, path):
    folder = os.path.join(path, str(row['task_id']).replace(".", "_").replace("/", "_"))
    
    # Extract Python code from answer_grading
    match = re.search(r'```python(.*?)```', row['answer_grading'], re.DOTALL)
    if not match:
        print(f"Warning: No Python code found in answer_grading for task_id {row['task_id']}")
        return False
    
    eval_file = match.group(1).strip()

    # Create the directory
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, 'task_evaluation.py')

    print(f"Writing file: {file_path}")

    # Write to the Python file
    with open(file_path, "w", encoding="utf-8") as py_file:
        py_file.write(eval_file)

    print(f"File saved successfully: {file_path}")
    return True



def save_answer_key(row, path):
    folder = os.path.join(path, str(row['task_id']).replace(".", "_"))
    try:
        answer_file = json.loads(re.search(r'```json(.*?)```', row['answer_evaluation'], re.DOTALL).group(1).strip())
    except:
        try:
            answer_file =  json.loads(row['answer_evaluation'])
        except:
            answer_file = '''{}'''
            return False
    
    # Create the folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # Write to the Python file
    with open(folder+'/answer_key.json', "w", encoding="utf-8") as json_file:
        json.dump(answer_file, json_file, ensure_ascii=False, indent=4)
    return True


def run_evaluation(row,path, model):
    folder = os.path.join(path, str(row['task_id']).replace('.','_'))
    if row['answer_key_json']* row['evaluation_python']:
        errors =[]
        try:
            result = subprocess.run(
                ["python", "../task_evaluation.py"],
                cwd=f"{folder}/{model}",  # Use f-string for clarity
                check=True,  # Raise an exception if the command fails
                stderr=subprocess.PIPE,  # Capture stderr
                stdout=subprocess.PIPE   # Capture stdout (if needed)
            )
            print("Script executed successfully.")
            # If the script runs successfully, append None to errors list (no errors)
            errors.append(None)
        except subprocess.CalledProcessError as e:
            # Capture and store the error output in the errors list
            print(f"Error: Script failed with return code {e.returncode}")
            print(f"Error Output:\n{e.stderr.decode('utf-8')}")
            errors.append(e.stderr.decode('utf-8'))  # Append the error message to the errors list
        except FileNotFoundError:
            error_message = "Error: The script or directory was not found. Check the path."
            print(error_message)
            errors.append(error_message)  # Append the error message to the errors list
        except Exception as e:
            # Capture and store any unexpected error
            error_message = f"An unexpected error occurred: {str(e)}"
            print(error_message)
            errors.append(error_message)  # Append the error message to the errors list   
        return errors
    else:
        return 'no answer key or evaluation script found'

  


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


def collect_overall_scores(row,parent_directory):
    scores_dict = {}  # Dictionary to store scores with subfolder names as keys
    parent_directory = parent_directory+str(row['task_id']).replace(".", "_")
    # Iterate over each subfolder in the parent directory
    for subfolder in os.listdir(parent_directory):
        subfolder_path = os.path.join(parent_directory, subfolder)

        # Check if it's a directory
        if os.path.isdir(subfolder_path):
            submission_file = os.path.join(subfolder_path, "test_results.json")

            # Check if the submission.json file exists
            if os.path.isfile(submission_file):
                try:
                    # Read the JSON file
                    with open(submission_file, "r", encoding="utf-8") as file:
                        data = json.load(file)
                    
                    # Convert JSON to DataFrame (if it's a list of dicts)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        df = pd.DataFrame([data])  # Convert single dict to DataFrame
                    else:
                        print(f"Unexpected format in {submission_file}")
                        continue
                    # Ensure 'overall_score' exists
                    if 'overall_score' in df.columns:
                        scores_dict[subfolder] = df['overall_score'].iloc[0]
                    else:
                        print(f"'overall_score' column missing in {submission_file}")

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error reading {submission_file}: {e}")
                except Exception as e:
                    print(f"Unexpected error in {submission_file}: {e}")
    print(scores_dict)
    return scores_dict


if __name__ == "__main__":
    path_to_data = '../../data/exam_approach/exams/'
    for root, dirs, files in os.walk(path_to_data):
        for model in dirs:
            print('Taking the exams of', model)

                 # Create the output directory for the current model if it does not exist
            output_dir = f'../../data/exam_approach/test_results/{model}/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for root, dirs, files in os.walk(path_to_data+model+'/'):
                for file in files:
                # Only process CSV files
                    if file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        print(file_path)
                        df = pd.read_csv(file_path)
                        print('Overall ', df.shape[0], ' tasks in the data')

            df= pd.read_csv(f'../../data/exam_approach/test_results/{model}/test_results_business_and_financial_operations_occupations_scores.csv')

            #test models
            df['test_answers_gemini'] = df.apply(take_test,axis=1, args=(system_prompt_template, test_prompt_template, 'gemini'))
            df['test_answers_claude'] = df.apply(take_test,axis=1, args=(system_prompt_template, test_prompt_template, 'claude' ))
            df['test_answers_chatgpt4o'] = df.apply(take_test,axis=1, args=(system_prompt_template, test_prompt_template, "gpt-4o"))
            df['test_answers_chatgpt35'] = df.apply(take_test,axis=1, args=(system_prompt_template, test_prompt_template,'gpt-3.5-turbo-0125'))
            df['test_answers_deepseek'] = df.apply(take_test,axis=1, args=(system_prompt_template, test_prompt_template,'deepseek'))

            df.to_csv(f'../../data/exam_approach/test_results/{model}/test_results_business_and_financial_operations_occupations_CORE_automatable.csv')




# overwrite = True
    # if  overwrite == False:
    #     print('reading in existing results')
    #     existing_df = pd.read_csv('../../data/exam_approach/test_results/test_results_business_and_financial_operations_occupations.csv')
    #     df = df[~df['task_id'].isin(existing_df['task_id'])]
    # print('Processing ', df.shape[0], ' new tasks.')
  
        # #
    
    # # # read in labels & filter exposure 
   
            # print(df.shape[0])
            model_folder_path = f'../../data/exam_approach/test_results/{model}/'
            # save answers as json files
            print('saving answer files')
            df['answer_valid_chatgpt4o'] = df.apply(save_answer_json, axis=1, args=(model_folder_path, 'chatgpt4o'))
            df['answer_valid_chatgpt35'] = df.apply(save_answer_json, axis=1, args=(model_folder_path, 'chatgpt35'))
            df['answer_valid_deepseek'] = df.apply(save_answer_json, axis=1, args=(model_folder_path, 'deepseek'))
            df['answer_valid_claude'] = df.apply(save_answer_json, axis=1, args=(model_folder_path, 'claude'))
            df['answer_valid_gemini'] = df.apply(save_answer_json, axis=1, args=(model_folder_path, 'gemini'))
            df.to_csv(f'../../data/exam_approach/test_results/{model}/test_results_business_and_financial_operations_occupations_scores.csv')

            print('saving evaluation files and answer keys')
            # save evaluation script and answer key in appropriate folders
            df['evaluation_python'] = df.apply(save_evaluation, axis=1, args=(model_folder_path,))
            df['answer_key_json']=  df.apply(save_answer_key, axis=1, args=(model_folder_path,))
            df.apply(copy_answer_key, axis=1, args=(model_folder_path,))


            # run evaluation and document potential errors
            print('running evaluation')
            df['errors_chatgpt35'] = df.apply(run_evaluation, axis=1, args=(model_folder_path,'chatgpt35',))
            df['errors_chatgpt4o'] = df.apply(run_evaluation, axis=1, args=(model_folder_path,'chatgpt4o',))
            df['errors_claude'] = df.apply(run_evaluation, axis=1, args=(model_folder_path,'claude',))
            df['errors_deepseek'] = df.apply(run_evaluation, axis=1, args=(model_folder_path,'deepseek',))
            df['errors_gemini'] = df.apply(run_evaluation, axis=1, args=(model_folder_path,'gemini',))

            print('collecting scores')
            df['scores'] =  df.apply(collect_overall_scores,axis=1, args= (model_folder_path,))
            scores_df = pd.json_normalize(df['scores'])
            scores_df.columns = 'score_'+scores_df.columns
            # Combine the original DataFrame with the new columns
            df_expanded = pd.concat([df.drop('scores', axis=1), scores_df], axis=1)
            
            df_expanded.to_csv(f'../../data/exam_approach/test_results/{model}/test_results_business_and_financial_operations_occupations_scores.csv')

            scores_df = pd.concat([df[['task_id','occupation','task_description']],scores_df], axis=1)
            scores_df.to_csv(f'../../data/exam_approach/test_results/{model}/overall_scores.csv')
