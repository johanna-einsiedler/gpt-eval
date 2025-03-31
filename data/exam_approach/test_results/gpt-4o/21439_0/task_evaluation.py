import json

def evaluate_submission(candidate_file, answer_key_file, result_file):
    # Load candidate submission
    with open(candidate_file, 'r') as f:
        candidate_data = json.load(f)
    
    # Load answer key
    with open(answer_key_file, 'r') as f:
        answer_key_data = json.load(f)
    
    candidate_discrepancies = candidate_data.get("Discrepancies", [])
    answer_key_discrepancies = answer_key_data.get("Discrepancies", [])
    
    correct_count = 0
    detailed_results = []

    # Evaluate each candidate discrepancy
    for candidate_discrepancy in candidate_discrepancies:
        match_found = False
        for answer_key_discrepancy in answer_key_discrepancies:
            if (candidate_discrepancy["Claim ID"] == answer_key_discrepancy["Claim ID"] and
                candidate_discrepancy["Discrepancy Type"] == answer_key_discrepancy["Discrepancy Type"] and
                candidate_discrepancy["Explanation"] == answer_key_discrepancy["Explanation"]):
                correct_count += 1
                match_found = True
                break
        detailed_results.append({
            "Claim ID": candidate_discrepancy["Claim ID"],
            "Discrepancy Type": candidate_discrepancy["Discrepancy Type"],
            "Explanation": candidate_discrepancy["Explanation"],
            "Correct": match_found
        })
    
    # Calculate overall score
    total_discrepancies = len(answer_key_discrepancies)
    overall_score = (correct_count / total_discrepancies) * 100 if total_discrepancies > 0 else 0

    # Prepare results
    results = {
        "Candidate ID": candidate_data.get("Candidate ID", "Unknown"),
        "Detailed Results": detailed_results,
        "Overall Score": overall_score
    }

    # Save results to a JSON file
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=4)

# Example usage
evaluate_submission('test_submission.json', 'answer_key.json', 'test_results.json')