import json

def validate_basic_exam(submission_file="test_submission.json", answer_key_file="answer_key.json"):
    """
    Automatically validates the basic purchasing agent exam submission against the answer key.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the test results, including scores and feedback.
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
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": f"Answer key file '{answer_key_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file '{answer_key_file}'."}

    results = {
        "candidate_id": submission.get('candidate_id', 'N/A'),
        "question_results": {},
        "overall_score": 0
    }
    total_possible_score = 4  # 4 questions

    # Question 1: Supplier Sourcing
    q1_results = {"is_correct": False, "details": [], "score": 0, "possible_score": 1}
    supplier_analysis_submission = submission.get('supplier_analysis', [])
    if len(supplier_analysis_submission) >= 3:
        q1_results["is_correct"] = True
        q1_results["score"] = 1 # All or nothing for basic exam, for now. Can refine later.
    else:
        q1_results["details"].append(f"Only {len(supplier_analysis_submission)} suppliers found, expecting at least 3.")
    results["question_results"]["question_1_supplier_sourcing"] = q1_results

    # Question 2: Price Comparison
    q2_results = {"is_correct": True, "details": [], "score": 1, "possible_score": 1} # Initially assume correct, disprove if not
    supplier_analysis_answer_key = answer_key.get('supplier_analysis', [])
    quantity_calculation_answer_key = answer_key.get('quantity_calculation', {})
    expected_reams = quantity_calculation_answer_key.get('total_reams_needed', 20) # Default to 20 if not found

    for i in range(min(len(supplier_analysis_submission), len(supplier_analysis_answer_key))):
        submitted_supplier = supplier_analysis_submission[i]
        answer_key_supplier = supplier_analysis_answer_key[i]

        try:
            submitted_price_per_ream = float(submitted_supplier.get('price_per_ream', 0))
            submitted_total_cost = float(submitted_supplier.get('total_cost_for_month', 0))
            expected_total_cost = answer_key_supplier['price_per_ream'] * expected_reams
            cost_comparison_valid = abs(submitted_total_cost - expected_total_cost) < 0.01
            if not cost_comparison_valid:
                q2_results["is_correct"] = False
                q2_results["score"] = 0
                q2_results["details"].append(f"Supplier '{submitted_supplier.get('supplier_name', 'Supplier ' + str(i+1))}': Total cost calculation incorrect. Submitted: {submitted_total_cost:.2f}, Expected: {expected_total_cost:.2f}")

        except (ValueError, TypeError):
            q2_results["is_correct"] = False
            q2_results["score"] = 0
            q2_results["details"].append(f"Supplier '{submitted_supplier.get('supplier_name', 'Supplier ' + str(i+1))}': Invalid price or total cost format.")


    results["question_results"]["question_2_price_comparison"] = q2_results

    # Question 3: Quantity Calculation
    q3_results = {"is_correct": False, "details": [], "score": 0, "possible_score": 1}
    quantity_calculation_submission = submission.get('quantity_calculation', {})
    q3_answer_key = answer_key.get('quantity_calculation', {})

    if (quantity_calculation_submission.get('weekly_usage_reams') == q3_answer_key.get('weekly_usage_reams') and
            quantity_calculation_submission.get('weeks_in_month') == q3_answer_key.get('weeks_in_month') and
            quantity_calculation_submission.get('total_reams_needed') == q3_answer_key.get('total_reams_needed')):
        q3_results["is_correct"] = True
        q3_results["score"] = 1
    else:
        q3_results["details"].append("Incorrect quantity calculation. Check weekly usage, weeks in month, and total reams needed.")
    results["question_results"]["question_3_quantity_calculation"] = q3_results

    # Question 4: Supplier Selection & Justification
    q4_results = {"is_correct": False, "details": [], "score": 0, "possible_score": 1}
    supplier_selection_submission = submission.get('supplier_selection', {})
    chosen_supplier_name = supplier_selection_submission.get('chosen_supplier_name', '')
    justification = supplier_selection_submission.get('justification', '')

    if chosen_supplier_name and justification: # Basic check for presence, more sophisticated check can be added.
        q4_results["is_correct"] = True # For basic exam, assume correct if present and reasonable. Manual review needed for justification quality.
        q4_results["score"] = 1
    else:
        q4_results["details"].append("Supplier selection or justification missing.")
    results["question_results"]["question_4_supplier_selection_justification"] = q4_results

    # Calculate overall score
    achieved_score = sum(q_result["score"] for q_result in results["question_results"].values())
    results["overall_score"] = (achieved_score / total_possible_score) * 100

    return results

if __name__ == '__main__':
    test_results = validate_basic_exam()

    if "error" in test_results:
        print(f"Error during evaluation: {test_results['error']}")
    else:
        results_for_json = {
            "candidate_id": test_results["candidate_id"],
            "overall_score": f"{test_results['overall_score']:.2f}%",
            "detailed_results": test_results["question_results"]
        }
        with open('test_results.json', 'w') as outfile:
            json.dump(results_for_json, outfile, indent=4)
        print("Test evaluation completed. Results saved to 'test_results.json'")