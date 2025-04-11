import pandas as pd
import os
import sys

print("Current working directory:", os.getcwd())

model ='claude-3-7-sonnet-20250219'
file_exams = "../../data/exam_approach/exams/{}/exams_business_and_financial_operations_occupations_CORE_automatable.csv".format(model)
file_answers = "../../data/exam_approach/test_results/{}/test_results_business_and_financial_operations_occupations_CORE_automatable.csv".format(model)
file_scores = "../../data/exam_approach/test_results/{}/test_results_business_and_financial_operations_occupations_scores.csv".format(model)

df_exams = pd.read_csv(file_exams)
task_id_list = df_exams['task_id'].to_list()
df_results = pd.read_csv(file_answers)
df_scores = pd.read_csv(file_scores)

# Remove unnamed columns from all DataFrames
df_exams = df_exams.loc[:, ~df_exams.columns.str.contains('^Unnamed')]
df_results = df_results.loc[:, ~df_results.columns.str.contains('^Unnamed')]
df_scores = df_scores.loc[:, ~df_scores.columns.str.contains('^Unnamed')]
df_exams.columns
df_scores.columns
df_results.columns

# Rank tasks by best performance

models_list = ['claude', 'chatgpt4o', 'chatgpt35', 'deepseek', 'gemini']

# Dynamically create the score_columns list
score_columns = [f"score_{model}" for model in models_list]

# Replace NaN values with 0 in the score columns
df_scores_filled = df_scores.copy()
df_scores_filled[score_columns] = df_scores_filled[score_columns].fillna(0)

# Calculate the average score for each task
df_scores_filled['average_score'] = df_scores_filled[score_columns].mean(axis=1)

# Sort tasks by average score in descending order
sorted_tasks = df_scores_filled.sort_values(by='average_score', ascending=False)
sorted_tasks_id = sorted_tasks['task_id'].to_list()
# Print the sorted task IDs and their average scores
print("Tasks sorted by average scores (highest first):")
print(sorted_tasks[['task_id', 'task_description', 'average_score']])


# Print the sorted tasks as a Markdown table
print("Tasks sorted by average scores (highest first):\n")
print("| Task ID | Task Description | Average Score |")
print("|---------|------------------|---------------|")

for _, row in sorted_tasks.iterrows():
    task_id = row['task_id']
    task_description = row['task_description']
    average_score = row['average_score']
    print(f"| {task_id} | {task_description} | {average_score:.2f} |")

def get_exam_generation_prompts(task_id, prompt_type, content_type, print_on=True):
    column_name = f"{content_type}_{prompt_type}"
    text = df_exams[ column_name][df_exams['task_id'] == task_id].values[0]
    if print_on:
        print(task_id)
        print(text)
    return text

def get_final_exam(task_id, print_on=True):
    text = df_results['answer_instructions'][df_results['task_id'] == task_id].values[0] +\
    df_results['answer_materials'][df_results['task_id'] == task_id].values[0] +\
              df_results['answer_submission'][df_results['task_id'] == task_id].values[0]
    if print_on:
        print(task_id)
        print(text)
    return text

df_scores[ df_scores['task_id'] ==sorted_tasks_id[0]]

get_final_exam(sorted_tasks_id[19])

get_exam_generation_prompts(sorted_tasks_id[19], 'evaluation', 'answer')
get_exam_generation_prompts(sorted_tasks_id[19], 'grading', 'answer')


get_exam_generation_prompts(sorted_tasks_id[19], 'materials', 'prompt')

df_exams.columns

sorted_tasks



df_results.columns

content = get_exam_generation_prompts(task_id, 'materials', 'prompt')

# Define the function to retrieve exam generation prompts or answers
def get_exam_generation_prompts(task_id, prompt_type, content_type):
    """
    Retrieves and prints the specified prompt or answer for a given task ID and prompt type from df_exams.

    Args:
        task_id (str): The task ID to filter.
        prompt_type (str): The type of prompt to retrieve (e.g., 'overview', 'instructions', 'materials', etc.).
        content_type (str): Either 'prompt' or 'answer' to specify what to retrieve.

    Returns:
        str: The content of the specified prompt or answer.
    """
    # Validate prompt_type and content_type
    prompt_type_list = ['overview', 'instructions', 'materials', 'submission', 'evaluation']
    content_type_list = ['prompt', 'answer']

    if prompt_type not in prompt_type_list:
        print(f"Invalid prompt_type. Use one of {prompt_type_list}.")
        return
    if content_type not in content_type_list:
        print(f"Invalid content_type. Use one of {content_type_list}.")
        return

    # Construct the column name
    column_name = f"{content_type}_{prompt_type}"

    # Check if the column exists in df_exams
    if column_name not in df_exams.columns:
        print(f"Column '{column_name}' not found in the DataFrame.")
        return

    # Filter the DataFrame for the specified task ID
    task_row = df_exams[df_exams['task_id'] == task_id]
    if task_row.empty:
        print(f"Task ID '{task_id}' not found in the DataFrame.")
        return

    # Retrieve the content
    df_exams[ column_name].iloc[0]
    content = task_row[column_name].values[0]
    print(f"Task ID: {task_id}")
    print(f"{content_type.capitalize()} ({prompt_type}):")
    print(content)
    return content

# Example usage
task_id = task_id = task_id_list[1]  # Replace with the actual task ID
prompt_type = "instructions"  # Replace with 'overview', 'instructions', etc.
content_type = "prompt"  # Use 'prompt' or 'answer'
df_exams.columns
# Call the function
content = get_exam_generation_prompts(task_id, 'materials', 'prompt')

df_exams['prompt_materials'][df_exams['task_id'] == task_id_list[1]].values[0]
# Print the content of the specified prompt

print(df_exams['prompt_materials'].iloc[0])

print(df_exams['prompt_materials'].iloc[0])

def get_prompt_or_answer(task_id, prompt_type, content_type, model=None):
    """
    Retrieves and prints the specified prompt, answer, or score for a given task ID and prompt type.

    Args:
        task_id (str): The task ID to filter.
        prompt_type (str): The type of prompt to retrieve (e.g., 'instructions', 'overview').
        content_type (str): Either 'prompt', 'answer', or 'score' to specify what to retrieve.
        model (str): The model name (e.g., 'claude', 'chatgpt4o') for answers and scores.

    Returns:
        str: The content of the specified prompt, answer, or score.
    """
    # Validate content_type
    if content_type not in ['prompt', 'answer', 'score']:
        print("Invalid content_type. Use 'prompt', 'answer', or 'score'.")
        return

    # Handle prompts
    if content_type == 'prompt':
        column_name = f"prompt_{prompt_type}"
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in the DataFrame.")
            return
        task_row = df[df['task_id'] == task_id]
        if task_row.empty:
            print(f"Task ID '{task_id}' not found in the DataFrame.")
            return
        content = task_row[column_name].values[0]
        print(f"Task ID: {task_id}")
        print(f"Prompt ({prompt_type}):")
        print(content)

    # Handle answers
    elif content_type == 'answer':
        if not model:
            print("Model name is required for retrieving answers.")
            return
        column_name = f"test_answers_{model}"
        valid_column_name = f"answer_valid_{model}"
        if column_name not in df_results.columns or valid_column_name not in df_results.columns:
            print(f"Columns '{column_name}' or '{valid_column_name}' not found in the DataFrame.")
            return
        task_row = df_results[df_results['task_id'] == task_id]
        if task_row.empty:
            print(f"Task ID '{task_id}' not found in the DataFrame.")
            return
        answer = task_row[column_name].values[0]
        validity = task_row[valid_column_name].values[0]
        print(f"Task ID: {task_id}")
        print(f"Answer ({model}):")
        print(answer)
        print(f"Answer Validity ({model}): {validity}")

    # Handle scores
    elif content_type == 'score':
        if not model:
            print("Model name is required for retrieving scores.")
            return
        score_column_name = f"score_{model}"
        if score_column_name not in df_scores.columns:
            print(f"Column '{score_column_name}' not found in the DataFrame.")
            return
        task_row = df_scores[df_scores['task_id'] == task_id]
        if task_row.empty:
            print(f"Task ID '{task_id}' not found in the DataFrame.")
            return
        score = task_row[score_column_name].values[0]
        print(f"Task ID: {task_id}")
        print(f"Score ({model}): {score}")

# Example usage
task_id = task_id_list[1]  # Replace with the actual task ID
prompt_type = "submission"  # Replace with 'overview', 'instructions', etc.
content_type = "prompt"  # Use 'prompt', 'answer', or 'score'
mdl = "claude"  # Replace with the model name (e.g., 'claude', 'chatgpt4o')

df_scores.columns


# Filter tasks where score_claude is NaN
tasks_with_nan_scores = df_scores['task_id'][df_scores['score_claude'].isna()].to_list()

score_columns = ['score_chatgpt4o', 'score_deepseek', 'score_chatgpt35', 'score_gemini', 'score_claude']


tasks_all_scores_valid = df_scores['task_id'][
    df_scores[score_columns].notna().all(axis=1) &  # All scores are non-NA
    df_scores[score_columns].applymap(lambda x: isinstance(x, int)).all(axis=1)  # All scores are integers
].to_list()

# 2. Tasks where at least one model has a non-NA score
tasks_at_least_one_score = df_scores['task_id'][
    df_scores[score_columns].notna().any(axis=1)  # At least one score is non-NA
].to_list()

# 3. Tasks where all models have NaN scores
tasks_all_scores_nan = df_scores['task_id'][
    df_scores[score_columns].isna().all(axis=1)  # All scores are NaN
].to_list()

len(tasks_at_least_one_score)
len(tasks_all_scores_nan)
# Check if all answers are NaN for these tasks
models_list = ['claude', 'chatgpt4o', 'chatgpt35', 'deepseek', 'gemini']
answer_columns = [f"score_{model}" for model in models_list]

task_id = tasks_at_least_one_score[0]
task_id
# Retrieve prompt
get_prompt_or_answer(task_id, prompt_type, "prompt")
get_prompt_or_answer(task_id, 'evaluation', "answer", model=mdl)

# Retrieve answer
get_prompt_or_answer(task_id, prompt_type, "answer", model=mdl)
get_prompt_or_answer(task_id, 'evaluation', "prompt", model=mdl)
get_prompt_or_answer(task_id, 'evaluation', "answer", model=mdl)
# Retrieve score
get_prompt_or_answer(task_id, prompt_type, "score", model=mdl)
# Example usage
task_id = task_id_list[0]  # Replace with the actual task ID
prompt_type = "instructions"  # Replace with 'overview', 'instructions', etc.
content_type = "prompt"  # Use 'prompt' or 'answer'

prompt_type_lists = ['overview','instructions',  'materials', 'submission', 'evaluation']
content_type_lists = ['prompt', 'answer']

prompt_type_lists[2]
get_prompt_or_answer(df, task_id, "overview", "prompt")
get_prompt_or_answer(df, task_id, "overview", "answer")
get_prompt_or_answer(df, task_id, "instructions", "prompt")