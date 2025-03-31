import json
import re

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_task_1(submission, answer_key):
    # Check if the link is present and matches the expected format
    link = submission.get("purchase_order_link", "")
    if link.startswith("https://") and "spreadsheet" in link:
        return 1  # Full points for a valid link
    return 0  # No points if the link is invalid

def validate_task_2(submission, answer_key):
    # Check if the RFP text includes required sections
    rfp_text = submission.get("rfp_text", "")
    required_sections = ["service required", "evaluation criteria", "submission guidelines"]
    if all(section in rfp_text.lower() for section in required_sections):
        return 1  # Full points if all sections are present
    return 0  # No points if any section is missing

def validate_task_3(submission, answer_key):
    # Check if the summary identifies discrepancies
    summary = submission.get("requisition_summary", "")
    # For simplicity, assume we have a list of known discrepancies
    known_discrepancies = ["incorrect item codes", "missing quantities", "incomplete supplier details"]
    identified_discrepancies = [discrepancy for discrepancy in known_discrepancies if discrepancy in summary.lower()]
    if len(identified_discrepancies) / len(known_discrepancies) >= 0.8:
        return 1  # Full points if 80% or more discrepancies are identified
    return 0  # No points if less than 80% are identified

def evaluate_submission(submission, answer_key):
    results = {
        "task_1": validate_task_1(submission.get("task_1", {}), answer_key.get("task_1", {})),
        "task_2": validate_task_2(submission.get("task_2", {}), answer_key.get("task_2", {})),
        "task_3": validate_task_3(submission.get("task_3", {}), answer_key.get("task_3", {}))
    }
    overall_score = sum(results.values()) / len(results) * 100
    results["overall_score"] = overall_score
    return results

def main():
    # Load the candidate's submission and the answer key
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)

    # Save the results to a JSON file
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()