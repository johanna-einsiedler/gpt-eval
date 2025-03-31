import json

def load_json(file_name):
    """Load JSON data from a file."""
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_data, answer_key):
    """Evaluate Task 1 and return the score and details."""
    score = 0
    details = {}

    # Check calculated fees
    if candidate_data['calculated_fees'] == answer_key['calculated_fees']:
        score += 1
    else:
        details['calculated_fees'] = f"Expected {answer_key['calculated_fees']}, got {candidate_data['calculated_fees']}"

    # Check summary
    if candidate_data['summary'] == answer_key['summary']:
        score += 1
    else:
        details['summary'] = f"Expected '{answer_key['summary']}', got '{candidate_data['summary']}'"

    return score, details

def evaluate_task_2(candidate_data, answer_key):
    """Evaluate Task 2 and return the score and details."""
    score = 0
    details = {}

    # Check payment matching results
    if candidate_data['payment_matching_results'] == answer_key['payment_matching_results']:
        score += 1
    else:
        details['payment_matching_results'] = "Payment matching results do not match the expected results."

    # Check discrepancies
    if candidate_data['discrepancies'] == answer_key['discrepancies']:
        score += 1
    else:
        details['discrepancies'] = "Discrepancies do not match the expected results."

    return score, details

def main():
    # Load the candidate's submission and the answer key
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate Task 1
    task_1_score, task_1_details = evaluate_task_1(candidate_submission['task_1'], answer_key['task_1'])

    # Evaluate Task 2
    task_2_score, task_2_details = evaluate_task_2(candidate_submission['task_2'], answer_key['task_2'])

    # Calculate overall score
    total_score = task_1_score + task_2_score
    max_score = 4  # 2 points for each task
    overall_score = (total_score / max_score) * 100

    # Prepare the results
    results = {
        "task_1_score": task_1_score,
        "task_1_details": task_1_details,
        "task_2_score": task_2_score,
        "task_2_details": task_2_details,
        "overall_score": overall_score
    }

    # Save the results to a JSON file
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()