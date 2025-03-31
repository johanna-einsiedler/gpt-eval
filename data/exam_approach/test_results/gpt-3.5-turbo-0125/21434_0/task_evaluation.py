import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def calculate_score(candidate_submission, answer_key):
    score_details = {
        "settled_claims_summary_correct": False,
        "claims_inventory_correct": False,
        "discrepancies_correct": False
    }
    total_checks = 3
    score = 0

    # Check Settled Claims Summary
    if candidate_submission["settled_claims_summary"] == answer_key["settled_claims_summary"]:
        score_details["settled_claims_summary_correct"] = True
        score += 1

    # Check Claims Inventory
    correct_claims = 0
    for claim in candidate_submission["claims_inventory"]:
        if claim in answer_key["claims_inventory"]:
            correct_claims += 1
    if correct_claims / len(answer_key["claims_inventory"]) >= 0.8:
        score_details["claims_inventory_correct"] = True
        score += 1

    # Check Discrepancies
    correct_discrepancies = 0
    for discrepancy in candidate_submission["discrepancies"]:
        if discrepancy in answer_key["discrepancies"]:
            correct_discrepancies += 1
    if correct_discrepancies / len(answer_key["discrepancies"]) >= 0.8:
        score_details["discrepancies_correct"] = True
        score += 1

    overall_score = (score / total_checks) * 100
    return score_details, overall_score

def save_results(score_details, overall_score):
    results = {
        "score_details": score_details,
        "overall_score": overall_score
    }
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    score_details, overall_score = calculate_score(candidate_submission, answer_key)
    save_results(score_details, overall_score)

if __name__ == "__main__":
    main()