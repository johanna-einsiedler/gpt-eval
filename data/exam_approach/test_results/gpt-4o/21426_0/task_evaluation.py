import json

def load_json(file_name):
    """Load JSON data from a file."""
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_submission(submission, answer_key):
    results = {
        "document_issues": [],
        "claim_decisions": [],
        "overall_score": 0
    }
    
    # Check candidate ID
    if submission.get("candidate_id") != answer_key["candidate_id"]:
        results["overall_score"] = 0
        return results

    # Validate document issues
    correct_issues = set(answer_key["document_issues"])
    submitted_issues = set(submission.get("document_issues", []))
    correct_issues_identified = correct_issues.intersection(submitted_issues)
    results["document_issues"] = list(correct_issues_identified)
    
    # Calculate document issues score
    document_issues_score = len(correct_issues_identified) / len(correct_issues) * 50  # 50% of total score
    results["document_issues_score"] = document_issues_score

    # Validate claim decisions
    correct_decisions = answer_key["claim_decisions"]
    submitted_decisions = submission.get("claim_decisions", [])
    correct_count = 0
    decision_results = []

    for correct_decision in correct_decisions:
        for submitted_decision in submitted_decisions:
            if (submitted_decision["claim_id"] == correct_decision["claim_id"] and
                submitted_decision["payable_amount"] == correct_decision["payable_amount"] and
                submitted_decision["decision"] == correct_decision["decision"]):
                correct_count += 1
                decision_results.append(submitted_decision)
                break

    results["claim_decisions"] = decision_results
    
    # Calculate claim decisions score
    claim_decisions_score = correct_count / len(correct_decisions) * 50  # 50% of total score
    results["claim_decisions_score"] = claim_decisions_score

    # Calculate overall score
    results["overall_score"] = document_issues_score + claim_decisions_score

    return results

def save_results(results, file_name):
    """Save the results to a JSON file."""
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    # Load the submission and answer key
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Validate the submission
    results = validate_submission(submission, answer_key)

    # Save the results
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()