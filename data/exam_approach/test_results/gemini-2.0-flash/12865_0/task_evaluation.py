import json

def validate_task3_1(candidate_answer_list):
    """
    Validates the candidate's answer for Task 3.1 (Invoice Components).

    Args:
        candidate_answer_list: A list of strings representing the candidate's invoice components.

    Returns:
        True if the answer is valid, False otherwise.
    """
    acceptable_invoice_components = {
        "Invoice Number", "Invoice Date", "Amount Due", "Payee Name",
        "Payee Address", "Payer Name", "Payer Address", "Description of Services",
        "Payment Terms"
    }
    candidate_answer_set = set(candidate_answer_list)

    # Check if all components in candidate's answer are in the acceptable set
    if all(component in candidate_answer_set for component in acceptable_invoice_components):
        return True
    else:
        return False

def evaluate_basic_exam(submission_json_file, answer_key_json_file):
    """
    Evaluates the basic exam submission against the answer key.

    Args:
        submission_json_file: Path to the candidate's test_submission.json file.
        answer_key_json_file: Path to the answer key JSON file.

    Returns:
        A dictionary containing the evaluation results, including pass/fail status, task-wise correctness and overall score.
    """
    try:
        with open(submission_json_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file not found: {submission_json_file}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file: {submission_json_file}"}

    try:
        with open(answer_key_json_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": f"Answer key file not found: {answer_key_json_file}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file: {answer_key_json_file}"}

    results = {}
    correct_tasks = 0
    total_tasks = 5 # Number of scored tasks

    # Task 1.1
    results["task1_1_correct"] = submission.get("task1_commission_percentage") == answer_key.get("task1_commission_percentage")
    if results["task1_1_correct"]: correct_tasks += 1

    # Task 1.2
    results["task1_2_correct"] = set(submission.get("task1_gross_performance_income_definition", [])) == set(answer_key.get("task1_gross_performance_income_definition", []))
    if results["task1_2_correct"]: correct_tasks += 1

    # Task 2.1
    results["task2_1_correct"] = submission.get("task2_november_commission_due") == answer_key.get("task2_november_commission_due")
    if results["task2_1_correct"]: correct_tasks += 1

    # Task 3.1 (using validation function)
    results["task3_1_correct"] = validate_task3_1(submission.get("task3_invoice_essential_components", []))
    if results["task3_1_correct"]: correct_tasks += 1

    # Task 4.1
    results["task4_1_correct"] = submission.get("task4_remaining_balance_due") == answer_key.get("task4_remaining_balance_due")
    if results["task4_1_correct"]: correct_tasks += 1

    pass_fail_status = "Pass" if correct_tasks >= 4 else "Fail"
    overall_score = (correct_tasks / total_tasks) * 100

    return {
        "pass_fail_status": pass_fail_status,
        "correct_tasks_count": correct_tasks,
        "overall_score": overall_score,
        "task_results": results
    }

if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"

    evaluation_result = evaluate_basic_exam(submission_file, answer_key_file)

    if "error" in evaluation_result:
        print(f"Error during evaluation: {evaluation_result['error']}")
    else:
        try:
            with open(results_file, 'w') as outfile:
                json.dump(evaluation_result, outfile, indent=4)
            print(f"Evaluation completed. Results saved to {results_file}")
        except IOError as e:
            print(f"Error saving results to {results_file}: {e}")