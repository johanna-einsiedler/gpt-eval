import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_section(candidate_section, answer_section):
    score = 0
    total = len(answer_section)
    detailed_results = {}

    for key, correct_answer in answer_section.items():
        candidate_answer = candidate_section.get(key, "")
        if candidate_answer.strip().lower() == correct_answer.strip().lower():
            score += 1
            detailed_results[key] = "Correct"
        else:
            detailed_results[key] = "Incorrect"

    return score, total, detailed_results

def evaluate_submission(candidate_submission, answer_key):
    results = {}
    total_score = 0
    total_possible = 0

    # Evaluate policy draft
    policy_score, policy_total, policy_results = evaluate_section(
        candidate_submission.get("policy_draft", {}),
        answer_key.get("policy_draft", {})
    )
    results["policy_draft"] = policy_results
    total_score += policy_score
    total_possible += policy_total

    # Evaluate procedure development
    procedure_score, procedure_total, procedure_results = evaluate_section(
        candidate_submission.get("procedure_development", {}),
        answer_key.get("procedure_development", {})
    )
    results["procedure_development"] = procedure_results
    total_score += procedure_score
    total_possible += procedure_total

    # Calculate overall score
    overall_score = (total_score / total_possible) * 100 if total_possible > 0 else 0
    results["overall_score"] = overall_score

    return results

def main():
    # Load candidate submission and answer key
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate the submission
    results = evaluate_submission(candidate_submission, answer_key)

    # Save the results
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()