import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_submission(submission, answer_key):
    """Validate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "questionable_claims_correct": 0,
        "total_questionable_claims": len(answer_key["questionable_claims"]),
        "referral_email_correct": False,
        "overall_score": 0
    }

    # Validate questionable claims
    for claim in submission.get("questionable_claims", []):
        for answer in answer_key["questionable_claims"]:
            if claim["claim_id"] == answer["claim_id"] and claim["explanation"] == answer["explanation"]:
                results["questionable_claims_correct"] += 1

    # Validate referral email
    if submission.get("referral_email") == answer_key.get("referral_email"):
        results["referral_email_correct"] = True

    # Calculate overall score
    claims_score = (results["questionable_claims_correct"] / results["total_questionable_claims"]) * 50
    email_score = 50 if results["referral_email_correct"] else 0
    results["overall_score"] = claims_score + email_score

    return results

def save_results(results, file_path):
    """Save the evaluation results to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    # Load the candidate's submission and the answer key
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Validate the submission
    results = validate_submission(submission, answer_key)

    # Save the results
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()