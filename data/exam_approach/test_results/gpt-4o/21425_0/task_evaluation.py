import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_data, answer_key):
    correct_count = 0
    total_claims = len(answer_key['task_1']['prioritization'])
    detailed_results = []

    for candidate_claim in candidate_data['task_1']['prioritization']:
        claim_id = candidate_claim['claim_id']
        candidate_priority = candidate_claim['priority']
        candidate_justification = candidate_claim['justification']

        # Find the corresponding claim in the answer key
        answer_claim = next((claim for claim in answer_key['task_1']['prioritization'] if claim['claim_id'] == claim_id), None)

        if answer_claim:
            is_priority_correct = candidate_priority == answer_claim['priority']
            is_justification_correct = all(keyword in candidate_justification for keyword in ["severity", "urgency", "financial", "legal"])

            if is_priority_correct and is_justification_correct:
                correct_count += 1

            detailed_results.append({
                "claim_id": claim_id,
                "priority_correct": is_priority_correct,
                "justification_correct": is_justification_correct
            })

    score = (correct_count / total_claims) * 100
    return score, detailed_results

def evaluate_task_2(candidate_data, answer_key):
    candidate_strategy = candidate_data['task_2']['resolution_strategy']
    answer_strategy = answer_key['task_2']['resolution_strategy']

    steps_correct = sum(1 for step in candidate_strategy['steps'] if step in answer_strategy['steps'])
    total_steps = len(answer_strategy['steps'])

    communication_correct = "regular updates" in candidate_strategy['communication_strategy'] and "transparency" in candidate_strategy['communication_strategy']
    resource_allocation_correct = "claims adjuster" in candidate_strategy['resource_allocation'] or "legal advisor" in candidate_strategy['resource_allocation']
    potential_challenges_correct = "challenges" in candidate_strategy['potential_challenges'] and "solution" in candidate_strategy['potential_challenges']

    score = ((steps_correct / total_steps) * 0.4 + communication_correct * 0.2 + resource_allocation_correct * 0.2 + potential_challenges_correct * 0.2) * 100

    detailed_results = {
        "steps_correct": steps_correct,
        "total_steps": total_steps,
        "communication_correct": communication_correct,
        "resource_allocation_correct": resource_allocation_correct,
        "potential_challenges_correct": potential_challenges_correct
    }

    return score, detailed_results

def main():
    candidate_data = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_details = evaluate_task_1(candidate_data, answer_key)
    task_2_score, task_2_details = evaluate_task_2(candidate_data, answer_key)

    overall_score = (task_1_score + task_2_score) / 2

    results = {
        "task_1_score": task_1_score,
        "task_1_details": task_1_details,
        "task_2_score": task_2_score,
        "task_2_details": task_2_details,
        "overall_score": overall_score
    }

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()