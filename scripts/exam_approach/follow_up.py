import os
from build_prompt_parts import  build_system_prompt, query_LLM
from take_test import run_evaluation
import pandas as pd


def check_for_test_submission(root_dir):
    """
    Recursively checks all subfolders of root_dir to see 
    if at least one file named 'test_submission.json' exists.
    Returns True if found, otherwise False.
    """ 
    for dirpath, _, filenames in os.walk(root_dir):
        if 'test_results.json' in filenames:
            return True
    return False

def find_empty_folders(folder_path):
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    failed_task_eval =[]
    for subfolder in subfolders:
        checkmark = check_for_test_submission(folder_path+subfolder)
        if checkmark == False:
            failed_task_eval.append(subfolder)
    return failed_task_eval
    
def regenerate_eval(df, folder_path):
    #print(df['task_id'].astype(str).str.replace(".", "_"))
    fails= find_empty_folders(folder_path)
    print('found ', len(fails),' empty folders.')
    df = df[df['task_id'].astype(str).str.replace(".", "_").isin(fails)]
    df['answer_grading'] = df.apply(query_LLM, axis=1, args=('prompt_grading',))
    print('running evaluation')
    df['errors_chatgpt35'] = df.apply(run_evaluation, axis=1, args=('../../data/exam_approach/test_results/','chatgpt35',))
    df['errors_chatgpt4o'] = df.apply(run_evaluation, axis=1, args=('../../data/exam_approach/test_results/','chatgpt4o',))
    df['errors_claude'] = df.apply(run_evaluation, axis=1, args=('../../data/exam_approach/test_results/','claude',))
    df['errors_deepseek'] = df.apply(run_evaluation, axis=1, args=('../../data/exam_approach/test_results/','deepseek',))
    df['errors_gemini'] = df.apply(run_evaluation, axis=1, args=('../../data/exam_approach/test_results/','gemini',))
    fails_remaining= find_empty_folders(folder_path)
    print('found ', len(fails_remaining),' empty folders.')


if __name__ == "__main__":
    folder_path= '../../data/exam_approach/test_results/'

    df = pd.read_csv('../../data/exam_approach/test_results/test_results_business_and_financial_operations_occupations.csv')

    regenerate_eval(df, folder_path)
