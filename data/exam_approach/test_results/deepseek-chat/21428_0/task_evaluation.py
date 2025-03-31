import json

def evaluate_task_1(submission, answer_key):
    score = 0
    max_score = 3
    details = {}
    
    # Check covered damages
    if set(submission['task_1']['covered_damages']) == set(answer_key['task_1']['covered_damages']):
        score += 1
        details['covered_damages'] = "Correct"
    else:
        details['covered_damages'] = f"Incorrect. Expected: {answer_key['task_1']['covered_damages']}"
    
    # Check non-covered damages
    if set(submission['task_1']['non_covered_damages']) == set(answer_key['task_1']['non_covered_damages']):
        score += 1
        details['non_covered_damages'] = "Correct"
    else:
        details['non_covered_damages'] = f"Incorrect. Expected: {answer_key['task_1']['non_covered_damages']}"
    
    # Check missing info
    if set(submission['task_1']['missing_info']) == set(answer_key['task_1']['missing_info']):
        score += 1
        details['missing_info'] = "Correct"
    else:
        details['missing_info'] = f"Incorrect. Expected: {answer_key['task_1']['missing_info']}"
    
    return score, max_score, details

def evaluate_task_2(submission, answer_key):
    score = 0
    max_score = 2
    details = {}
    
    # Check fraud flags
    if set(submission['task_2']['fraud_flags']) == set(answer_key['task_2']['fraud_flags']):
        score += 1
        details['fraud_flags'] = "Correct"
    else:
        details['fraud_flags'] = f"Incorrect. Expected: {answer_key['task_2']['fraud_flags']}"
    
    # Check high value claims
    if set(submission['task_2']['high_value_claims']) == set(answer_key['task_2']['high_value_claims']):
        score += 1
        details['high_value_claims'] = "Correct"
    else:
        details['high_value_claims'] = f"Incorrect. Expected: {answer_key['task_2']['high_value_claims']}"
    
    return score, max_score, details

def evaluate_task_3(submission, answer_key):
    score = 0
    max_score = 2
    details = {}
    
    # Check decision
    if submission['task_3']['decision'].lower() == answer_key['task_3']['decision'].lower():
        score += 1
        details['decision'] = "Correct"
    else:
        details['decision'] = f"Incorrect. Expected: {answer_key['task_3']['decision']}"
    
    # Check reason (case insensitive and partial match)
    expected_reason = answer_key['task_3']['reason'].lower()
    submitted_reason = submission['task_3']['reason'].lower()
    if expected_reason in submitted_reason or any(keyword in submitted_reason for keyword in ['$10,000', 'threshold', '10k']):
        score += 1
        details['reason'] = "Correct"
    else:
        details['reason'] = f"Incorrect. Expected to contain: {expected_reason}"
    
    return score, max_score, details

def main():
    # Load submission and answer key
    try:
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)['answer_key']
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Evaluate each task
    task1_score, task1_max, task1_details = evaluate_task_1(submission, answer_key)
    task2_score, task2_max, task2_details = evaluate_task_2(submission, answer_key)
    task3_score, task3_max, task3_details = evaluate_task_3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    total_max = task1_max + task2_max + task3_max
    overall_score = round((total_score / total_max) * 100, 2)
    
    # Determine pass/fail based on criteria
    passed = (task2_score == task2_max) and (task1_score >= 2) and (task3_score >= 2)
    
    # Prepare results
    results = {
        'task_1': {
            'score': task1_score,
            'max_score': task1_max,
            'details': task1_details
        },
        'task_2': {
            'score': task2_score,
            'max_score': task2_max,
            'details': task2_details
        },
        'task_3': {
            'score': task3_score,
            'max_score': task3_max,
            'details': task3_details
        },
        'overall_score': overall_score,
        'pass_status': "PASS" if passed else "FAIL",
        'total_score': total_score,
        'total_max_score': total_max
    }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()