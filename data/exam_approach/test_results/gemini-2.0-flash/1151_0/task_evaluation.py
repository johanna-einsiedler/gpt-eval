import json

def evaluate_test(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    """
    Evaluates the candidate's test submission against the answer key and saves the results to a JSON file.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.
        results_file (str): Path to save the test results JSON file.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        print(f"Error: Submission file '{submission_file}' not found.")
        return

    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file '{answer_key_file}' not found.")
        return

    results = {}
    total_points = 0
    achieved_points = 0

    # Evaluate "Total Cost PO-2023-103"
    question_name_cost = "Total Cost PO-2023-103"
    results[f"{question_name_cost}_expected"] = answer_key.get(question_name_cost)
    results[f"{question_name_cost}_submitted"] = submission.get(question_name_cost)
    if submission.get(question_name_cost) == answer_key.get(question_name_cost):
        results[f"{question_name_cost}_score"] = 1
        achieved_points += 1
    else:
        results[f"{question_name_cost}_score"] = 0
    total_points += 1

    # Evaluate "Overdue Delivery POs"
    question_name_overdue = "Overdue Delivery POs"
    expected_overdue_pos = answer_key.get(question_name_overdue)
    submitted_overdue_pos = submission.get(question_name_overdue)

    results[f"{question_name_overdue}_expected"] = expected_overdue_pos
    results[f"{question_name_overdue}_submitted"] = submitted_overdue_pos

    if isinstance(expected_overdue_pos, list) and isinstance(submitted_overdue_pos, list):
        expected_overdue_pos.sort()
        submitted_overdue_pos.sort()
        if expected_overdue_pos == submitted_overdue_pos:
            results[f"{question_name_overdue}_score"] = 1
            achieved_points += 1
        else:
            results[f"{question_name_overdue}_score"] = 0
    else:
        results[f"{question_name_overdue}_score"] = 0 # Incorrect format in submission
    total_points += 1


    # Evaluate "Global Components Inc. Order Count"
    question_name_count = "Global Components Inc. Order Count"
    results[f"{question_name_count}_expected"] = answer_key.get(question_name_count)
    results[f"{question_name_count}_submitted"] = submission.get(question_name_count)
    if submission.get(question_name_count) == answer_key.get(question_name_count):
        results[f"{question_name_count}_score"] = 1
        achieved_points += 1
    else:
        results[f"{question_name_count}_score"] = 0
    total_points += 1

    overall_score = (achieved_points / total_points) * 100 if total_points > 0 else 0
    results["overall_score"] = round(overall_score, 2)

    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Test results saved to '{results_file}'")
    except IOError as e:
        print(f"Error writing to results file '{results_file}': {e}")


if __name__ == "__main__":
    # Create dummy answer_key.json and test_submission.json for testing
    answer_key_data = {
        "Total Cost PO-2023-103": "500.00",
        "Overdue Delivery POs": ["PO-2023-103", "PO-2023-108", "PO-2023-110"],
        "Global Components Inc. Order Count": "3"
    }
    submission_data = {
        "Total Cost PO-2023-103": "500.00",
        "Overdue Delivery POs": ["PO-2023-103", "PO-2023-110"],
        "Global Components Inc. Order Count": "2"
    }

    with open("answer_key.json", 'w') as f:
        json.dump(answer_key_data, f, indent=2)
    with open("test_submission.json", 'w') as f:
        json.dump(submission_data, f, indent=2)

    evaluate_test()