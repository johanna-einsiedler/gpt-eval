import json

def load_json(file_path):
    """Loads JSON data from a file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def validate_red_flags(candidate_flags, expected_flags, validation_keywords):
    """Validates red flags based on keyword matching."""
    validated_flags = []
    valid_flag_count = 0
    expected_flag_keywords_sets = [set(flag.lower().split()) for flag in expected_flags]

    for candidate_flag in candidate_flags:
        candidate_flag_keywords = set(candidate_flag.lower().split())
        for i, expected_keywords in enumerate(expected_flag_keywords_sets):
            if expected_keywords.intersection(candidate_flag_keywords):
                if expected_flags[i] not in validated_flags: # Avoid duplicate validation for similar flags
                    validated_flags.append(expected_flags[i])
                    valid_flag_count += 1
                    break # Move to next candidate flag after finding a match
    return valid_flag_count, validated_flags


def validate_justification(candidate_justification, expected_justification_keywords):
    """Validates justification based on keyword matching."""
    candidate_justification_keywords = set(candidate_justification.lower().split())
    expected_keywords_set = set(expected_justification_keywords.lower().split())
    if expected_keywords_set.intersection(candidate_justification_keywords):
        return True
    return False

def validate_referral_decision(candidate_decision, expected_decision):
    """Validates referral decision."""
    return candidate_decision == expected_decision

def evaluate_scenario(candidate_response, answer_key_scenario, answer_key_explanation):
    """Evaluates a single scenario."""
    scenario_id = candidate_response["scenario_id"]
    identified_red_flags = candidate_response["identified_red_flags"]
    justification_for_referral = candidate_response["justification_for_referral"]
    referral_decision = candidate_response["referral_decision"]

    expected_red_flags = answer_key_scenario["expected_red_flags"]
    justification_explanation = answer_key_scenario["justification_explanation"]
    expected_referral = answer_key_scenario["expected_referral_decision"]

    red_flags_valid_count, validated_red_flags = validate_red_flags(identified_red_flags, expected_red_flags, answer_key_explanation["correct_red_flags_explanation"])
    justification_valid = validate_justification(justification_for_referral, justification_explanation)
    referral_correct = validate_referral_decision(referral_decision, expected_referral)

    scenario_results = {
        "scenario_id": scenario_id,
        "candidate_identified_red_flags": identified_red_flags,
        "validated_red_flags": validated_red_flags,
        "red_flags_valid_count": red_flags_valid_count,
        "justification_for_referral": justification_for_referral,
        "justification_valid": justification_valid,
        "candidate_referral_decision": referral_decision,
        "referral_decision_correct": referral_correct,
        "expected_red_flags": expected_red_flags,
        "expected_justification": justification_explanation,
        "expected_referral_decision": expected_referral
    }
    return scenario_results

def evaluate_test(submission_data, answer_key_data, answer_key_explanation, passing_criteria):
    """Evaluates the entire test."""
    scenario_responses = submission_data["scenario_responses"]
    answer_key_scenarios = answer_key_data["answer_key"]["scenario_responses"]
    scenario_explanations = answer_key_explanation["answer_explanation"]

    scenario_results_list = []
    total_possible_points = 0
    total_achieved_points = 0

    for i in range(len(scenario_responses)):
        candidate_response = scenario_responses[i]
        answer_key_scenario = answer_key_scenarios[i]
        scenario_explanation = scenario_explanations[f"scenario_{i+1}"]

        scenario_result = evaluate_scenario(candidate_response, answer_key_scenario, scenario_explanation)
        scenario_results_list.append(scenario_result)

        possible_red_flag_points = len(answer_key_scenario["expected_red_flags"]) # Max points for red flags is number of expected flags
        achieved_red_flag_points = min(scenario_result["red_flags_valid_count"], possible_red_flag_points) # Cap at max possible
        justification_points = 1 if scenario_result["justification_valid"] else 0
        referral_points = 1 if scenario_result["referral_decision_correct"] else 0

        scenario_score = achieved_red_flag_points + justification_points + referral_points
        scenario_results_list[i]["scenario_score"] = scenario_score

        total_possible_points += possible_red_flag_points + 2 # +1 for justification, +1 for referral
        total_achieved_points += scenario_score


    overall_score_percentage = (total_achieved_points / total_possible_points) * 100 if total_possible_points > 0 else 0
    overall_pass = True # Initialize as passing, will be updated based on criteria
    pass_fail_reasons = []

    for i in range(len(scenario_results_list)):
        scenario_result = scenario_results_list[i]
        scenario_id = scenario_result["scenario_id"]

        if scenario_result["red_flags_valid_count"] < passing_criteria[f"minimum_red_flags_{scenario_id.lower()}"]:
            overall_pass = False
            pass_fail_reasons.append(f"{scenario_id}: Did not identify enough red flags (minimum {passing_criteria[f'minimum_red_flags_{scenario_id.lower()}']} required).")
        if not scenario_result["referral_decision_correct"]:
            overall_pass = False
            pass_fail_reasons.append(f"{scenario_id}: Incorrect referral decision.")


    overall_results = {
        "candidate_id": submission_data["candidate_id"],
        "scenario_results": scenario_results_list,
        "overall_score": overall_score_percentage,
        "overall_pass": overall_pass,
        "pass_fail_reasons": pass_fail_reasons
    }
    return overall_results

if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"

    submission_data = load_json(submission_file)
    answer_key_data = load_json(answer_key_file)

    answer_key_explanation = answer_key_data["answer_explanation"]
    passing_criteria = answer_key_data["passing_criteria"]

    overall_results = evaluate_test(submission_data, answer_key_data, answer_key_explanation, passing_criteria)

    results_file = "test_results.json"
    with open(results_file, 'w') as outfile:
        json.dump(overall_results, outfile, indent=4)

    print(f"Test evaluation completed. Results saved to '{results_file}'")