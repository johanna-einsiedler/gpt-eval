import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_submission(candidate_submission, answer_key):
    results = {
        "questionable_claims_correct": 0,
        "referral_report_correct": False,
        "details": {
            "questionable_claims": [],
            "referral_report": {}
        }
    }
    
    # Evaluate questionable claims
    candidate_claims = {claim['claim_id']: claim['reason'] for claim in candidate_submission['questionable_claims']}
    answer_claims = {claim['claim_id']: claim['reason'] for claim in answer_key['questionable_claims']}
    
    for claim_id, reason in candidate_claims.items():
        if claim_id in answer_claims and reason == answer_claims[claim_id]:
            results["questionable_claims_correct"] += 1
            results["details"]["questionable_claims"].append({
                "claim_id": claim_id,
                "correct": True,
                "reason": reason
            })
        else:
            results["details"]["questionable_claims"].append({
                "claim_id": claim_id,
                "correct": False,
                "reason": reason
            })
    
    # Evaluate referral report
    candidate_report = candidate_submission['referral_report']
    answer_report = answer_key['referral_report']
    
    if (candidate_report['claim_id'] == answer_report['claim_id'] and
        candidate_report['summary'] == answer_report['summary'] and
        candidate_report['additional_information'] == answer_report['additional_information']):
        results["referral_report_correct"] = True
    
    results["details"]["referral_report"] = {
        "claim_id": candidate_report['claim_id'],
        "correct": results["referral_report_correct"],
        "summary": candidate_report['summary'],
        "additional_information": candidate_report['additional_information']
    }
    
    # Calculate overall score
    total_possible_points = len(answer_key['questionable_claims']) + 1  # +1 for the referral report
    total_achieved_points = results["questionable_claims_correct"] + (1 if results["referral_report_correct"] else 0)
    overall_score = (total_achieved_points / total_possible_points) * 100
    
    results["overall_score"] = overall_score
    
    return results

def save_results(results, file_name='test_results.json'):
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    results = evaluate_submission(candidate_submission, answer_key)
    save_results(results)

if __name__ == "__main__":
    main()