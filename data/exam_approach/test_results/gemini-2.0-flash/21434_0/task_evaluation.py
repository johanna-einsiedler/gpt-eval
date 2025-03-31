import json

def load_json_file(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in: {file_path}")
        return None

def compare_claim_records(submission_records, answer_key_records):
    """Compares two lists of claim records (lists of dictionaries)."""

    if not isinstance(submission_records, list) or not isinstance(answer_key_records, list):
        return False, "Invalid input format: records should be lists."

    if len(submission_records) != len(answer_key_records):
        return False, "Incorrect number of records."

    submission_set = {tuple(sorted(record.items())) for record in submission_records}
    answer_key_set = {tuple(sorted(record.items())) for record in answer_key_records}

    if submission_set == answer_key_set:
        return True, "Records are correct."
    else:
        return False, "Records are incorrect."

def evaluate_basic_exam(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    """Evaluates the basic claim file maintenance exam."""

    submission_data = load_json_file(submission_file)
    answer_key_data = load_json_file(answer_key_file)

    if submission_data is None or answer_key_data is None:
        return False

    results = {
        "overall_score": 0.0,
        "detailed_results": {
            "settled_claims_record": {
                "is_correct": False,
                "message": ""
            },
            "detailed_analysis_inventory": {
                "is_correct": False,
                "message": ""
            }
        }
    }

    # Evaluate settled_claims_record
    if 'settled_claims_record' in submission_data and 'settled_claims_record' in answer_key_data:
        is_correct_settled, message_settled = compare_claim_records(
            submission_data['settled_claims_record'], answer_key_data['settled_claims_record']
        )
        results["detailed_results"]["settled_claims_record"]["is_correct"] = is_correct_settled
        results["detailed_results"]["settled_claims_record"]["message"] = message_settled
        if is_correct_settled:
            results["overall_score"] += 50.0
    else:
        results["detailed_results"]["settled_claims_record"]["message"] = "Section 'settled_claims_record' not found in submission."

    # Evaluate detailed_analysis_inventory
    if 'detailed_analysis_inventory' in submission_data and 'detailed_analysis_inventory' in answer_key_data:
        is_correct_detailed, message_detailed = compare_claim_records(
            submission_data['detailed_analysis_inventory'], answer_key_data['detailed_analysis_inventory']
        )
        results["detailed_results"]["detailed_analysis_inventory"]["is_correct"] = is_correct_detailed
        results["detailed_results"]["detailed_analysis_inventory"]["message"] = message_detailed
        if is_correct_detailed:
            results["overall_score"] += 50.0
    else:
        results["detailed_results"]["detailed_analysis_inventory"]["message"] = "Section 'detailed_analysis_inventory' not found in submission."

    # Ensure overall score is capped at 100
    results["overall_score"] = min(results["overall_score"], 100.0)

    # Save results to JSON file
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to: {results_file}")
    except Exception as e:
        print(f"Error saving results to {results_file}: {e}")
        return False

    return True


if __name__ == "__main__":
    # Create a dummy answer_key.json for testing (replace with actual answer key)
    dummy_answer_key = {
        "candidate_id": "ANSWER_KEY",
        "model_version": "N/A",
        "settled_claims_record": [
            {
                "Claim ID": "CLAIM001",
                "Policy Holder Name": "Alice Smith",
                "Claim Amount": 2500,
                "Settlement Date": "2023-10-26"
            },
            {
                "Claim ID": "CLAIM004",
                "Policy Holder Name": "Diana Lee",
                "Claim Amount": 4800,
                "Settlement Date": "2023-11-15"
            },
            {
                "Claim ID": "CLAIM007",
                "Policy Holder Name": "George White",
                "Claim Amount": 6000,
                "Settlement Date": "2023-12-01"
            },
            {
                "Claim ID": "CLAIM010",
                "Policy Holder Name": "Jack Red",
                "Claim Amount": 1000,
                "Settlement Date": "2024-01-10"
            }
        ],
        "detailed_analysis_inventory": [
            {
                "Claim ID": "CLAIM002",
                "Claim Type": "Property",
                "Claim Amount": 12000,
                "Reason for Detailed Analysis": "Claim Amount greater than $5,000"
            },
            {
                "Claim ID": "CLAIM003",
                "Claim Type": "Liability",
                "Claim Amount": 7000,
                "Reason for Detailed Analysis": "Claim Amount greater than $5,000"
            },
            {
                "Claim ID": "CLAIM006",
                "Claim Type": "Complex",
                "Claim Amount": 9000,
                "Reason for Detailed Analysis": "Claim Type is Complex"
            },
            {
                "Claim ID": "CLAIM009",
                "Claim Type": "Property",
                "Claim Amount": 5500,
                "Reason for Detailed Analysis": "Claim Amount greater than $5,000"
            }
        ]
    }
    with open("answer_key.json", 'w') as f:
        json.dump(dummy_answer_key, f, indent=4)

    # Create a dummy test_submission.json for testing (replace with actual submission)
    dummy_submission = {
        "candidate_id": "CANDIDATE001",
        "model_version": "GPT-4-turbo",
        "settled_claims_record": [
            { "Claim ID": "CLAIM001", "Policy Holder Name": "Alice Smith", "Claim Amount": 2500, "Settlement Date": "2023-10-26" },
            { "Claim ID": "CLAIM004", "Policy Holder Name": "Diana Lee", "Claim Amount": 4800, "Settlement Date": "2023-11-15" },
            { "Claim ID": "CLAIM007", "Policy Holder Name": "George White", "Claim Amount": 6000, "Settlement Date": "2023-12-01" },
            { "Claim ID": "CLAIM010", "Policy Holder Name": "Jack Red", "Claim Amount": 1000, "Settlement Date": "2024-01-10" }
        ],
        "detailed_analysis_inventory": [
            { "Claim ID": "CLAIM002", "Claim Type": "Property", "Claim Amount": 12000, "Reason for Detailed Analysis": "Claim Amount greater than $5,000" },
            { "Claim ID": "CLAIM003", "Claim Type": "Liability", "Claim Amount": 7000, "Reason for Detailed Analysis": "Claim Amount greater than $5,000" },
            { "Claim ID": "CLAIM006", "Claim Type": "Complex", "Claim Amount": 9000, "Reason for Detailed Analysis": "Claim Type is Complex" },
            { "Claim ID": "CLAIM009", "Claim Type": "Property", "Claim Amount": 5500, "Reason for Detailed Analysis": "Claim Amount greater than $5,000" }
        ]
    }
    with open("test_submission.json", 'w') as f:
        json.dump(dummy_submission, f, indent=4)


    evaluate_basic_exam()