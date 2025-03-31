import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def calculate_task_1_score(candidate_data, answer_key):
    """Calculate the score for Task 1."""
    candidate_items = candidate_data['task_1']['items']
    answer_items = answer_key['task_1']['items']
    
    correct_items = 0
    for candidate_item, answer_item in zip(candidate_items, answer_items):
        if candidate_item['duty_payable'] == answer_item['duty_payable']:
            correct_items += 1
    
    total_items = len(answer_items)
    item_score = (correct_items / total_items) * 100
    
    # Check total duty
    total_duty_correct = candidate_data['task_1']['total_duty'] == answer_key['task_1']['total_duty']
    total_duty_score = 100 if total_duty_correct else 0
    
    # Average the item score and total duty score
    task_1_score = (item_score + total_duty_score) / 2
    return task_1_score

def calculate_task_2_score(candidate_data, answer_key):
    """Calculate the score for Task 2."""
    candidate_quote = candidate_data['task_2']['freight_quote']
    answer_quote = answer_key['task_2']['freight_quote']
    
    correct_fields = 0
    total_fields = 4  # service_provider, quote_amount, currency, confirmation_number
    
    for field in ['service_provider', 'quote_amount', 'currency', 'confirmation_number']:
        if candidate_quote[field] == answer_quote[field]:
            correct_fields += 1
    
    task_2_score = (correct_fields / total_fields) * 100
    return task_2_score

def main():
    # Load the candidate's submission and the answer key
    candidate_data = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    # Calculate scores for each task
    task_1_score = calculate_task_1_score(candidate_data, answer_key)
    task_2_score = calculate_task_2_score(candidate_data, answer_key)
    
    # Calculate overall score as the average of both tasks
    overall_score = (task_1_score + task_2_score) / 2
    
    # Prepare the results
    results = {
        "task_1_score": task_1_score,
        "task_2_score": task_2_score,
        "overall_score": overall_score
    }
    
    # Save the results to a JSON file
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()