import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_policy_draft(candidate_policy, answer_key_policy):
    score = 0
    max_score = len(answer_key_policy)
    detailed_results = {}

    for section, correct_answer in answer_key_policy.items():
        candidate_answer = candidate_policy.get(section, "").strip().lower()
        correct_answer = correct_answer.strip().lower()
        if candidate_answer == correct_answer:
            score += 1
            detailed_results[section] = "Correct"
        else:
            detailed_results[section] = "Incorrect"

    return score, max_score, detailed_results

def evaluate_procedure_development(candidate_procedure, answer_key_procedure):
    score = 0
    max_score = len(answer_key_procedure)
    detailed_results = []

    for i, correct_step in enumerate(answer_key_procedure):
        if i < len(candidate_procedure):
            candidate_step = candidate_procedure[i].strip().lower()
            correct_step = correct_step.strip().lower()
            if candidate_step == correct_step:
                score += 1
                detailed_results.append("Correct")
            else:
                detailed_results.append("Incorrect")
        else:
            detailed_results.append("Missing")

    return score, max_score, detailed_results

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate policy draft
    policy_score, policy_max_score, policy_results = evaluate_policy_draft(
        candidate_submission['policy_draft'],
        answer_key['policy_draft']
    )

    # Evaluate procedure development
    procedure_score, procedure_max_score, procedure_results = evaluate_procedure_development(
        candidate_submission['procedure_development'],
        answer_key['procedure_development']
    )

    # Calculate overall score
    total_score = policy_score + procedure_score
    total_max_score = policy_max_score + procedure_max_score
    overall_score = (total_score / total_max_score) * 100

    # Prepare results
    results = {
        "policy_draft_results": policy_results,
        "procedure_development_results": procedure_results,
        "overall_score": overall_score
    }

    # Save results to JSON
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()