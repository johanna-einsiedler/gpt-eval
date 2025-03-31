import json

def evaluate_task(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    """
    Evaluates the candidate's submission against the answer key and saves the results to a JSON file.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.
        results_file (str): Path to the output results JSON file.
    """
    try:
        with open(submission_file, 'r') as f:
            submission_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Submission file '{submission_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in submission file '{submission_file}'.")
        return

    try:
        with open(answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file '{answer_key_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in answer key file '{answer_key_file}'.")
        return

    submission_discrepancies = {item['claim_id']: item for item in submission_data.get('discrepancies', [])}
    answer_key_discrepancies = {item['claim_id']: item for item in answer_key_data.get('discrepancies', [])}
    expected_discrepancies_count = len(answer_key_data.get('discrepancies', []))
    correct_count = 0
    detailed_results = []

    for submitted_claim_id, submitted_discrepancy in submission_discrepancies.items():
        result_item = {
            "claim_id": submitted_claim_id,
            "submitted_discrepancy_type": submitted_discrepancy['discrepancy_type'],
            "submitted_explanation": submitted_discrepancy['explanation'],
            "expected_discrepancy_type": None,
            "expected_explanation": None,
            "is_correct_type": False
        }
        if submitted_claim_id in answer_key_discrepancies:
            answer_key_discrepancy = answer_key_discrepancies[submitted_claim_id]
            result_item["expected_discrepancy_type"] = answer_key_discrepancy['discrepancy_type']
            result_item["expected_explanation"] = answer_key_discrepancy['explanation']
            if submitted_discrepancy['discrepancy_type'] == answer_key_discrepancy['discrepancy_type']:
                correct_count += 1
                result_item["is_correct_type"] = True
        else:
            result_item["expected_discrepancy_type"] = "No discrepancy expected"
            result_item["expected_explanation"] = "No discrepancy expected according to answer key"

        detailed_results.append(result_item)

    overall_score = 0
    if expected_discrepancies_count > 0:
        overall_score = (correct_count / expected_discrepancies_count) * 100

    test_results = {
        "candidate_id": submission_data.get("candidate_id", "N/A"),
        "model_version": submission_data.get("model_version", "N/A"),
        "overall_score": overall_score,
        "detailed_results": detailed_results,
        "correct_discrepancy_count": correct_count,
        "expected_discrepancy_count": expected_discrepancies_count
    }

    try:
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=4)
        print(f"Evaluation completed. Results saved to '{results_file}'")
    except IOError:
        print(f"Error: Could not write results to file '{results_file}'.")


if __name__ == "__main__":
    evaluate_task()