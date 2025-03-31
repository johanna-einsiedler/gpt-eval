import json

def evaluate_basic_exam(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    """
    Evaluates the candidate submission against the answer key and saves the results in JSON format.
    """
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file '{submission_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file '{submission_file}'."}

    try:
        with open(answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
            answer_key = answer_key_data['answer_key']
    except FileNotFoundError:
        return {"error": f"Answer key file '{answer_key_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file '{answer_key_file}'."}

    results = {
        "candidate_id": submission.get("candidate_id", "N/A"),
        "model_version": submission.get("model_version", "N/A"),
        "part1_duty_payment": {},
        "part2_freight_payment": {}
    }
    total_points = 0
    achieved_points = 0

    # Part 1: Duty Payment
    results_part1 = results["part1_duty_payment"]
    answer_part1 = answer_key["part1_duty_payment"]

    # 1. Estimated Duty Amount
    estimated_duty_correct = submission["part1_duty_payment"]["estimated_duty_amount"] == answer_part1["estimated_duty_amount"]
    results_part1["estimated_duty_amount_correct"] = estimated_duty_correct
    if estimated_duty_correct:
        achieved_points += 1
    total_points += 1

    # 2. Duty Calculation Steps
    calculation_steps_keywords = ["2.5%", "20000", "multiply", "500"]
    calculation_steps_present = all(keyword in submission["part1_duty_payment"]["duty_calculation_steps"].lower() for keyword in calculation_steps_keywords)
    results_part1["calculation_steps_keywords_present"] = calculation_steps_present
    if calculation_steps_present:
        achieved_points += 1
    total_points += 1

    # 3. Common Duty Payment Methods
    valid_duty_payment_methods = set(method.lower() for method in answer_part1["common_duty_payment_methods"])
    candidate_duty_payment_methods = set(method.lower() for method in submission["part1_duty_payment"]["common_duty_payment_methods"])
    duty_payment_methods_correct = len(candidate_duty_payment_methods.intersection(valid_duty_payment_methods)) >= 1
    results_part1["duty_payment_methods_correct"] = duty_payment_methods_correct
    results_part1["correct_duty_payment_methods_provided"] = list(candidate_duty_payment_methods.intersection(valid_duty_payment_methods))
    if duty_payment_methods_correct:
        achieved_points += 1
    total_points += 1

    # 4. Steps to Arrange Duty Payment
    valid_duty_payment_steps_keywords = [set(step.lower().split()) for step in answer_part1["steps_to_arrange_duty_payment"]]
    candidate_duty_payment_steps = [step.lower() for step in submission["part1_duty_payment"]["steps_to_arrange_duty_payment"]]
    duty_payment_steps_correct_count = 0
    for candidate_step in candidate_duty_payment_steps:
        for valid_step_keywords in valid_duty_payment_steps_keywords:
            if valid_step_keywords.issubset(set(candidate_step.split())):
                duty_payment_steps_correct_count += 1
                break # avoid counting same valid step multiple times
    duty_payment_steps_correct = duty_payment_steps_correct_count >= 3
    results_part1["duty_payment_steps_correct"] = duty_payment_steps_correct
    results_part1["correct_duty_payment_steps_count"] = duty_payment_steps_correct_count
    if duty_payment_steps_correct:
        achieved_points += 1
    total_points += 1


    # Part 2: Freight Payment
    results_part2 = results["part2_freight_payment"]
    answer_part2 = answer_key["part2_freight_payment"]

    # 5. Common Freight Payment Methods
    valid_freight_payment_methods = set(method.lower() for method in answer_part2["common_freight_payment_methods"])
    candidate_freight_payment_methods = set(method.lower() for method in submission["part2_freight_payment"]["common_freight_payment_methods"])
    freight_payment_methods_correct = len(candidate_freight_payment_methods.intersection(valid_freight_payment_methods)) >= 1
    results_part2["freight_payment_methods_correct"] = freight_payment_methods_correct
    results_part2["correct_freight_payment_methods_provided"] = list(candidate_freight_payment_methods.intersection(valid_freight_payment_methods))
    if freight_payment_methods_correct:
        achieved_points += 1
    total_points += 1

    # 6. Steps to Arrange Freight Payment
    valid_freight_payment_steps_keywords = [set(step.lower().split()) for step in answer_part2["steps_to_arrange_freight_payment"]]
    candidate_freight_payment_steps = [step.lower() for step in submission["part2_freight_payment"]["steps_to_arrange_freight_payment"]]
    freight_payment_steps_correct_count = 0
    for candidate_step in candidate_freight_payment_steps:
        for valid_step_keywords in valid_freight_payment_steps_keywords:
            if valid_step_keywords.issubset(set(candidate_step.split())):
                freight_payment_steps_correct_count += 1
                break # avoid counting same valid step multiple times
    freight_payment_steps_correct = freight_payment_steps_correct_count >= 3
    results_part2["freight_payment_steps_correct"] = freight_payment_steps_correct
    results_part2["correct_freight_payment_steps_count"] = freight_payment_steps_correct_count
    if freight_payment_steps_correct:
        achieved_points += 1
    total_points += 1

    # 7. Information for Payment Instructions
    valid_payment_info = set(info.lower() for info in answer_part2["information_for_freight_payment_instructions"])
    candidate_payment_info = set(info.lower() for info in submission["part2_freight_payment"]["information_for_freight_payment_instructions"])
    payment_info_correct = len(candidate_payment_info.intersection(valid_payment_info)) >= 2 # Adjusted to 2 as per evaluation criteria
    results_part2["payment_info_correct"] = payment_info_correct
    results_part2["correct_payment_info_provided"] = list(candidate_payment_info.intersection(valid_payment_info))
    if payment_info_correct:
        achieved_points += 1
    total_points += 1

    overall_score = (achieved_points / total_points) * 100 if total_points > 0 else 0
    results["overall_score"] = round(overall_score, 2)
    results["achieved_points"] = achieved_points
    results["total_points"] = total_points


    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        return {"success": f"Test results saved to '{results_file}'."}
    except Exception as e:
        return {"error": f"Error saving results to '{results_file}': {e}"}

if __name__ == "__main__":
    evaluation_result = evaluate_basic_exam()
    if "error" in evaluation_result:
        print(f"Evaluation failed: {evaluation_result['error']}")
    elif "success" in evaluation_result:
        print(evaluation_result['success'])
        with open("test_results.json", 'r') as f:
            results = json.load(f)
            print(json.dumps(results, indent=2))