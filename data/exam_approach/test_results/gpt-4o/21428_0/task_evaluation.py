import json

def evaluate_task_1(candidate_issues, answer_key_issues):
    correct_issues = 0
    detailed_results = []

    for candidate_issue in candidate_issues:
        for correct_issue in answer_key_issues:
            if (candidate_issue['claim_id'] == correct_issue['claim_id'] and
                candidate_issue['issue'] == correct_issue['issue']):
                correct_issues += 1
                detailed_results.append({
                    "claim_id": candidate_issue['claim_id'],
                    "correct": True,
                    "issue": candidate_issue['issue'],
                    "proposed_correction": candidate_issue['proposed_correction']
                })
                break
        else:
            detailed_results.append({
                "claim_id": candidate_issue['claim_id'],
                "correct": False,
                "issue": candidate_issue['issue'],
                "proposed_correction": candidate_issue['proposed_correction']
            })

    return correct_issues, detailed_results

def evaluate_task_2(candidate_claims, answer_key_claims):
    correct_claims = 0
    detailed_results = []

    for candidate_claim in candidate_claims:
        for correct_claim in answer_key_claims:
            if (candidate_claim['claim_id'] == correct_claim['claim_id'] and
                candidate_claim['reason'] == correct_claim['reason']):
                correct_claims += 1
                detailed_results.append({
                    "claim_id": candidate_claim['claim_id'],
                    "correct": True,
                    "reason": candidate_claim['reason']
                })
                break
        else:
            detailed_results.append({
                "claim_id": candidate_claim['claim_id'],
                "correct": False,
                "reason": candidate_claim['reason']
            })

    return correct_claims, detailed_results

def main():
    with open('test_submission.json', 'r') as f:
        candidate_data = json.load(f)

    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)

    # Evaluate Task 1
    task_1_correct, task_1_results = evaluate_task_1(
        candidate_data['task_1']['issues'],
        answer_key['task_1']['issues']
    )

    # Evaluate Task 2
    task_2_correct, task_2_results = evaluate_task_2(
        candidate_data['task_2']['non_compliant_claims'],
        answer_key['task_2']['non_compliant_claims']
    )

    # Calculate overall score
    total_possible = len(answer_key['task_1']['issues']) + len(answer_key['task_2']['non_compliant_claims'])
    total_correct = task_1_correct + task_2_correct
    overall_score = (total_correct / total_possible) * 100

    # Prepare results
    results = {
        "task_1_results": task_1_results,
        "task_2_results": task_2_results,
        "overall_score": overall_score
    }

    # Save results to a JSON file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()