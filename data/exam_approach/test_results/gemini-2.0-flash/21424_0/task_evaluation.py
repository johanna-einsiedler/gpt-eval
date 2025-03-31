import json

def evaluate_exam(submission_file="test_submission.json", answer_key_file="answer_key.json", output_file="test_results.json"):
    """
    Evaluates the candidate's submission against the answer key and saves the results to a JSON file.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        with open(answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
            answer_key = answer_key_data['answer_key']
            evaluation_info = answer_key_data['evaluation_information']
            passing_criteria = evaluation_info['passing_criteria']
            components_considered = passing_criteria['components_considered']
            justification_accuracy_weight = passing_criteria['justification_accuracy_weight']
            amount_accuracy_weight = passing_criteria['amount_accuracy_weight']
            overall_passing_score = passing_criteria['overall_passing_score']
            min_correct_answers = passing_criteria['minimum_correct_answers']

    except FileNotFoundError:
        print(f"Error: Could not find {submission_file} or {answer_key_file}. Make sure they are in the same directory.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {submission_file} or {answer_key_file}.")
        return

    results = {
        "candidate_id": submission.get("candidate_id", "N/A"),
        "claim_number": submission["claim_number"],
        "component_results": {},
        "overall_score": 0,
        "passed": False
    }

    component_scores = []
    correct_components_count = 0

    reserve_types = ["property_damage_reserve", "bodily_injury_reserve", "claim_expenses_reserve"]

    for reserve_type in reserve_types:
        results["component_results"][reserve_type] = {
            "amount_correct": False,
            "justification_correct": False,
            "component_score": 0
        }

        submission_amount = submission[reserve_type]["amount"]
        answer_amount = answer_key[reserve_type]["amount"]
        submission_justification = submission[reserve_type]["justification"]
        answer_justification = answer_key[reserve_type]["justification"]

        amount_correct = submission_amount == answer_amount
        justification_correct = submission_justification == answer_justification

        results["component_results"][reserve_type]["amount_correct"] = amount_correct
        results["component_results"][reserve_type]["justification_correct"] = justification_correct

        amount_score = 1 if amount_correct else 0
        justification_score = 1 if justification_correct else 0

        component_score = (amount_score * amount_accuracy_weight) + (justification_score * justification_accuracy_weight)
        results["component_results"][reserve_type]["component_score"] = component_score
        component_scores.append(component_score)

        if amount_correct and justification_correct:
            correct_components_count += 1


    total_reserve_correct = submission["total_recommended_reserve"] == answer_key["total_recommended_reserve"]
    results["component_results"]["total_recommended_reserve"] = {
        "total_reserve_correct": total_reserve_correct
    }
    total_reserve_score = 1 if total_reserve_correct else 0
    component_scores.append(total_reserve_score)


    overall_score = sum(component_scores) / len(component_scores) if component_scores else 0
    results["overall_score"] = round(overall_score * 100, 2)

    if overall_score >= overall_passing_score and correct_components_count >= min_correct_answers:
        results["passed"] = True
    else:
        results["passed"] = False

    results["correct_components_count"] = correct_components_count
    results["passing_score_required"] = overall_passing_score * 100
    results["minimum_correct_answers_required"] = min_correct_answers


    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to {output_file}")
    except IOError:
        print(f"Error: Could not save results to {output_file}.")


if __name__ == "__main__":
    evaluate_exam()