import json

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 4
    task_1_results = {}

    # Check commission rate
    if candidate.get("commission_rate") == answer_key.get("commission_rate"):
        task_1_results["commission_rate"] = "Correct"
        score += 1
    else:
        task_1_results["commission_rate"] = "Incorrect"

    # Check payment schedule
    if candidate.get("payment_schedule") == answer_key.get("payment_schedule"):
        task_1_results["payment_schedule"] = "Correct"
        score += 1
    else:
        task_1_results["payment_schedule"] = "Incorrect"

    # Check additional fees
    if candidate.get("additional_fees") == answer_key.get("additional_fees"):
        task_1_results["additional_fees"] = "Correct"
        score += 1
    else:
        task_1_results["additional_fees"] = "Incorrect"

    # Check total amount due
    if candidate.get("total_amount_due") == answer_key.get("total_amount_due"):
        task_1_results["total_amount_due"] = "Correct"
        score += 1
    else:
        task_1_results["total_amount_due"] = "Incorrect"

    return task_1_results, score, max_score

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = 1
    task_2_results = {}

    # Check if the email contains the correct total amount due
    if answer_key.get("total_amount_due") in candidate.get("payment_request_email", ""):
        task_2_results["total_amount_due_in_email"] = "Correct"
        score += 1
    else:
        task_2_results["total_amount_due_in_email"] = "Incorrect"

    # Check for presence of key phrases
    key_phrases = ["10% commission", "5% administrative fee", "request the payment"]
    for phrase in key_phrases:
        if phrase in candidate.get("payment_request_email", ""):
            task_2_results[f"phrase_{phrase}"] = "Correct"
        else:
            task_2_results[f"phrase_{phrase}"] = "Incorrect"

    return task_2_results, score, max_score

def main():
    # Load candidate submission
    with open('test_submission.json', 'r') as file:
        candidate_submission = json.load(file)

    # Load answer key
    with open('answer_key.json', 'r') as file:
        answer_key = json.load(file)

    # Evaluate Task 1
    task_1_results, task_1_score, task_1_max_score = evaluate_task_1(candidate_submission.get("task_1", {}), answer_key.get("task_1", {}))

    # Evaluate Task 2
    task_2_results, task_2_score, task_2_max_score = evaluate_task_2(candidate_submission.get("task_2", {}), answer_key.get("task_2", {}))

    # Calculate overall score
    total_score = task_1_score + task_2_score
    total_max_score = task_1_max_score + task_2_max_score
    overall_score = (total_score / total_max_score) * 100

    # Prepare results
    results = {
        "task_1_results": task_1_results,
        "task_2_results": task_2_results,
        "overall_score": overall_score
    }

    # Save results to JSON
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()