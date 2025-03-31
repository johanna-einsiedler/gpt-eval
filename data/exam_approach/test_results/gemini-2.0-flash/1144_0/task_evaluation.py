import json

def evaluate_submission(submission_file_path, answer_key_file_path):
    """
    Evaluates the candidate submission against the answer key and generates a score.

    Args:
        submission_file_path (str): Path to the candidate's submission JSON file.
        answer_key_file_path (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the test results, including task-wise scores,
              overall score, and feedback.
    """
    try:
        with open(submission_file_path, 'r') as f:
            submission = json.load(f)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in submission file."}
    except FileNotFoundError:
        return {"error": "Submission file not found."}

    try:
        with open(answer_key_file_path, 'r') as f:
            answer_key_data = json.load(f)
        answer_key = answer_key_data.get("answer_key", {}) # Access answer_key part
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in answer key file."}
    except FileNotFoundError:
        return {"error": "Answer key file not found."}

    task_results = {
        "task1_supplier_identification": {"task_score": 0, "feedback": ""},
        "task2_data_collection": {"task_score": 0, "feedback": ""},
        "task3_recommendation_justification": {"task_score": 0, "feedback": ""},
        "adherence_to_instructions": {"task_score": 0, "feedback": ""}
    }
    overall_score = 0
    overall_feedback = ""

    # --- Task 1 Evaluation ---
    task1_score = 0
    task1_feedback = ""
    if "task1_suppliers" in submission and isinstance(submission["task1_suppliers"], list) and len(submission["task1_suppliers"]) == 3:
        suppliers = submission["task1_suppliers"]
        supplier_relevance_points = 5  # Points per relevant supplier
        correct_urls_points = 5 # Points for correct URLs

        task1_supplier_identification_results = {}
        total_relevance_score = 0
        urls_correct = True

        expected_supplier_keywords = ["dell", "lenovo", "hp", "business", "laptop", "computer", "tech"] # Keywords to check for supplier relevance

        for i, supplier_data in enumerate(suppliers):
            supplier_name = supplier_data.get("supplier_name", "").lower()
            supplier_url = supplier_data.get("supplier_url", "")
            relevance_score = 0

            if any(keyword in supplier_name for keyword in expected_supplier_keywords):
                relevance_score = supplier_relevance_points
                total_relevance_score += relevance_score
            else:
                task1_feedback += f"Supplier {i+1} ('{supplier_name}') might not be sufficiently business-focused. "

            if not supplier_url.startswith(("http://", "https://")):
                urls_correct = False
                task1_feedback += f"URL for Supplier {i+1} ('{supplier_name}') does not start with http:// or https://. "

            task1_supplier_identification_results[f"supplier{i+1}_relevance_score"] = relevance_score


        task1_score = total_relevance_score
        if urls_correct:
            task1_score += correct_urls_points
            task1_supplier_identification_results["correct_urls_score"] = correct_urls_points
        else:
            task1_supplier_identification_results["correct_urls_score"] = 0


        task1_results["task_score"] = task1_score
        task1_results["feedback"] = task1_feedback
        task_results["task1_supplier_identification"] = task1_supplier_identification_results
    else:
        task1_feedback = "Task 1 not completed or incorrectly formatted."
        task_results["task1_supplier_identification"]["feedback"] = task1_feedback


    # --- Task 2 Evaluation ---
    task2_score = 0
    task2_feedback = ""
    if "task2_supplier_data" in submission and isinstance(submission["task2_supplier_data"], list) and len(submission["task2_supplier_data"]) == 3:
        supplier_data_list = submission["task2_supplier_data"]
        data_plausibility_points = 10 # Total points for price, availability, reputation plausibility per supplier

        task2_data_collection_results = {}
        total_plausibility_score = 0

        for i, data_entry in enumerate(supplier_data_list):
            plausibility_score = 0
            supplier_name = data_entry.get("supplier_name", "")
            price_info = data_entry.get("price", "")
            availability_info = data_entry.get("availability", "")
            reputation_info = data_entry.get("reputation", "")

            # Basic Plausibility Checks - can be improved with more specific ranges from answer_key if provided
            if price_info:
                plausibility_score += (data_plausibility_points / 3) # Roughly distribute points
            if availability_info:
                plausibility_score += (data_plausibility_points / 3)
            if reputation_info:
                plausibility_score += (data_plausibility_points / 3)

            total_plausibility_score += plausibility_score
            task2_data_collection_results[f"supplier{i+1}_data_plausibility_score"] = plausibility_score


        task2_score = total_plausibility_score
        task_results["task2_data_collection"] = task2_data_collection_results
        task_results["task2_data_collection"]["task_score"] = task2_score
        task_results["task2_data_collection"]["feedback"] = task2_feedback

    else:
        task2_feedback = "Task 2 not completed or incorrectly formatted."
        task_results["task2_data_collection"]["feedback"] = task2_feedback


    # --- Task 3 Evaluation ---
    task3_score = 0
    task3_feedback = ""
    if "task3_recommendation" in submission and isinstance(submission["task3_recommendation"], dict):
        recommendation_data = submission["task3_recommendation"]
        recommended_supplier = recommendation_data.get("recommended_supplier", "")
        justification = recommendation_data.get("justification", "")

        recommendation_valid_points = 5
        justification_criteria_points = 10
        justification_logic_points = 15
        justification_detail_points = 10

        task3_recommendation_justification_results = {}

        if any(supplier["supplier_name"] == recommended_supplier for supplier in submission.get("task1_suppliers", [])):
            task3_score += recommendation_valid_points
            task3_recommendation_justification_results["recommendation_valid_score"] = recommendation_valid_points
        else:
            task3_recommendation_justification_results["recommendation_valid_score"] = 0
            task3_feedback += "Recommended supplier is not among the identified suppliers in Task 1. "

        justification_keywords = ["price", "availability", "reputation"]
        criteria_mentioned_score = 0
        for keyword in justification_keywords:
            if keyword in justification.lower():
                criteria_mentioned_score += (justification_criteria_points / 3) # Roughly distribute points
        task3_score += criteria_mentioned_score
        task3_recommendation_justification_results["justification_criteria_mentioned_score"] = criteria_mentioned_score


        # Basic logic and detail check - Subjective and can be improved
        if len(justification) > 100: # Basic detail check
            task3_score += justification_detail_points
            task3_recommendation_justification_results["justification_detail_score"] = justification_detail_points
        else:
             task3_recommendation_justification_results["justification_detail_score"] = 0
             task3_feedback += "Justification is not very detailed. "

        # Logic is hard to automate without more context.  Assume some logic if justification exists and criteria are mentioned.
        if criteria_mentioned_score > justification_criteria_points / 2 and len(justification) > 50:
            task3_score += justification_logic_points
            task3_recommendation_justification_results["justification_logic_score"] = justification_logic_points
        else:
            task3_recommendation_justification_results["justification_logic_score"] = 0
            task3_feedback += "Justification logic could be clearer or stronger. "


        task_results["task3_recommendation_justification"] = task3_recommendation_justification_results
        task_results["task3_recommendation_justification"]["task_score"] = task3_score
        task_results["task3_recommendation_justification"]["feedback"] = task3_feedback

    else:
        task3_feedback = "Task 3 not completed or incorrectly formatted."
        task_results["task3_recommendation_justification"]["feedback"] = task3_feedback


    # --- Adherence to Instructions Evaluation ---
    adherence_score = 0
    adherence_feedback = ""
    valid_json_points = 5
    correct_filename_points = 5 # Assumed correct if script loaded the file

    adherence_score += valid_json_points # If it loaded, it's valid JSON
    task_results["adherence_to_instructions"]["valid_json_score"] = valid_json_points
    adherence_score += correct_filename_points # Assumed correct
    task_results["adherence_to_instructions"]["correct_filename_score"] = correct_filename_points


    task_results["adherence_to_instructions"]["task_score"] = adherence_score
    task_results["adherence_to_instructions"]["feedback"] = adherence_feedback


    overall_score = sum(task_data["task_score"] for task_data in task_results.values())
    overall_percentage = (overall_score / 100) * 100 # Assuming total possible score is 100

    results = {
        "task_results": task_results,
        "overall_score": round(overall_percentage, 1),
        "overall_feedback": overall_feedback # Can add overall feedback based on task feedbacks later
    }

    return results


if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json" # Assuming answer_key.json is in the same directory
    evaluation_results = evaluate_submission(submission_file, answer_key_file)

    if "error" in evaluation_results:
        print(f"Error during evaluation: {evaluation_results['error']}")
    else:
        results_file = "test_results.json"
        with open(results_file, 'w') as outfile:
            json.dump(evaluation_results, outfile, indent=2)
        print(f"Evaluation completed. Results saved to '{results_file}'")
        print(json.dumps(evaluation_results, indent=2))