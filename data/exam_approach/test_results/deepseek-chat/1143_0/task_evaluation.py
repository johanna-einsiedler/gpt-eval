import json

def evaluate_task_1(submission, answer_key):
    score = 0
    max_score = 30
    feedback = []
    
    # Check errors found
    submission_errors = set(submission['task_1']['errors_found'])
    correct_errors = set(answer_key['task_1']['errors_found'])
    
    if submission_errors == correct_errors:
        score += 10
        feedback.append("All errors correctly identified in Task 1")
    else:
        missing = correct_errors - submission_errors
        extra = submission_errors - correct_errors
        if missing:
            feedback.append(f"Missed errors in Task 1: {', '.join(missing)}")
        if extra:
            feedback.append(f"Incorrectly identified errors in Task 1: {', '.join(extra)}")
    
    # Check corrected requisition
    submission_req = submission['task_1']['corrected_requisition']
    correct_req = answer_key['task_1']['corrected_requisition']
    
    if submission_req == correct_req:
        score += 20
        feedback.append("Requisition correctly formatted in Task 1")
    else:
        errors = []
        for field in correct_req:
            if submission_req.get(field) != correct_req[field]:
                errors.append(f"{field} (expected: {correct_req[field]}, got: {submission_req.get(field)})")
        feedback.append(f"Requisition formatting errors in Task 1: {', '.join(errors)}")
    
    return score, max_score, feedback

def evaluate_task_2(submission, answer_key):
    score = 0
    max_score = 40
    feedback = []
    
    submission_po = submission['task_2']['purchase_order']
    correct_po = answer_key['task_2']['purchase_order']
    
    # Check required fields
    required_fields = ['vendor_name', 'items', 'total_cost']
    for field in required_fields:
        if submission_po.get(field) == correct_po[field]:
            score += 10
        else:
            feedback.append(f"Incorrect {field} in Task 2 (expected: {correct_po[field]}, got: {submission_po.get(field)})")
    
    # Check payment terms
    if submission_po.get('payment_terms') == correct_po['payment_terms']:
        score += 10
    else:
        feedback.append(f"Incorrect payment terms in Task 2 (expected: {correct_po['payment_terms']}, got: {submission_po.get('payment_terms')})")
    
    if score == max_score:
        feedback.append("Purchase order correctly formatted in Task 2")
    
    return score, max_score, feedback

def evaluate_task_3(submission, answer_key):
    score = 0
    max_score = 30
    feedback = []
    
    # Check selected bid
    if submission['task_3']['selected_bid'] == answer_key['task_3']['selected_bid']:
        score += 10
        feedback.append("Correct bid selected in Task 3")
    else:
        feedback.append(f"Incorrect bid selected in Task 3 (expected: {answer_key['task_3']['selected_bid']}, got: {submission['task_3']['selected_bid']})")
    
    # Check reason
    required_phrases = ["$120.00", "2 weeks", "Net 30"]
    reason = submission['task_3']['reason']
    missing_phrases = [phrase for phrase in required_phrases if phrase not in reason]
    
    if not missing_phrases:
        score += 20
        feedback.append("Bid selection properly justified in Task 3")
    else:
        feedback.append(f"Missing justification elements in Task 3: {', '.join(missing_phrases)}")
    
    return score, max_score, feedback

def main():
    # Load files
    try:
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Evaluate tasks
    task1_score, task1_max, task1_feedback = evaluate_task_1(submission, answer_key)
    task2_score, task2_max, task2_feedback = evaluate_task_2(submission, answer_key)
    task3_score, task3_max, task3_feedback = evaluate_task_3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    max_possible = task1_max + task2_max + task3_max
    overall_score = round((total_score / max_possible) * 100, 2)
    
    # Prepare results
    results = {
        "overall_score": overall_score,
        "task_1": {
            "score": task1_score,
            "max_score": task1_max,
            "feedback": task1_feedback
        },
        "task_2": {
            "score": task2_score,
            "max_score": task2_max,
            "feedback": task2_feedback
        },
        "task_3": {
            "score": task3_score,
            "max_score": task3_max,
            "feedback": task3_feedback
        }
    }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()