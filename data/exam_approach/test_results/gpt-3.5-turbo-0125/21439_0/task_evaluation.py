import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def evaluate_submission(candidate_data, answer_key_data):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "correct_irregularities": 0,
        "total_irregularities": len(answer_key_data["irregularities"]),
        "summary_correct": False,
        "overall_score": 0
    }
    
    # Check candidate ID
    if candidate_data["candidate_id"] != answer_key_data["candidate_id"]:
        results["overall_score"] = 0
        return results

    # Validate irregularities
    candidate_irregularities = candidate_data["irregularities"]
    answer_irregularities = answer_key_data["irregularities"]
    
    for candidate_irregularity in candidate_irregularities:
        if candidate_irregularity in answer_irregularities:
            results["correct_irregularities"] += 1
    
    # Calculate accuracy
    accuracy = results["correct_irregularities"] / results["total_irregularities"]
    
    # Validate summary
    candidate_summary = candidate_data["summary"]
    answer_summary = answer_key_data["summary"]
    
    results["summary_correct"] = (
        candidate_summary["total_overpayments"] == answer_summary["total_overpayments"] and
        candidate_summary["total_underpayments"] == answer_summary["total_underpayments"] and
        candidate_summary["total_other_irregularities"] == answer_summary["total_other_irregularities"]
    )
    
    # Determine overall score
    if results["summary_correct"]:
        results["overall_score"] = accuracy * 100
    else:
        results["overall_score"] = accuracy * 50  # Penalize for incorrect summary
    
    return results

def save_results(results, file_path):
    """Save the evaluation results to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    # Load candidate submission and answer key
    candidate_data = load_json('test_submission.json')
    answer_key_data = load_json('answer_key.json')
    
    # Evaluate the submission
    results = evaluate_submission(candidate_data, answer_key_data)
    
    # Save the results
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()