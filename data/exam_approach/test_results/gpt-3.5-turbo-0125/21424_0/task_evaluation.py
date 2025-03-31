import json

def evaluate_submission(submission_file, answer_key_file, result_file):
    # Load the candidate's submission
    with open(submission_file, 'r') as file:
        submission = json.load(file)
    
    # Load the answer key
    with open(answer_key_file, 'r') as file:
        answer_key = json.load(file)
    
    # Initialize result structure
    results = {
        "adjusted_reserves": [],
        "reserve_recommendation_report": {
            "recommendations": [],
            "justifications": ""
        },
        "overall_score": 0
    }
    
    # Evaluate adjusted reserves
    correct_reserves = answer_key["adjusted_reserves"]
    reserve_correct_count = 0
    for reserve in submission.get("adjusted_reserves", []):
        claim_id = reserve["claim_id"]
        adjusted_reserve = reserve["adjusted_reserve"]
        correct_reserve = next((item for item in correct_reserves if item["claim_id"] == claim_id), None)
        if correct_reserve and correct_reserve["adjusted_reserve"] == adjusted_reserve:
            reserve_correct_count += 1
            results["adjusted_reserves"].append({"claim_id": claim_id, "correct": True})
        else:
            results["adjusted_reserves"].append({"claim_id": claim_id, "correct": False})
    
    # Evaluate reserve recommendations
    correct_recommendations = answer_key["reserve_recommendation_report"]["recommendations"]
    recommendation_correct_count = 0
    for recommendation in submission.get("reserve_recommendation_report", {}).get("recommendations", []):
        claim_id = recommendation["claim_id"]
        recommended_reserve = recommendation["recommended_reserve"]
        correct_recommendation = next((item for item in correct_recommendations if item["claim_id"] == claim_id), None)
        if correct_recommendation and correct_recommendation["recommended_reserve"] == recommended_reserve:
            recommendation_correct_count += 1
            results["reserve_recommendation_report"]["recommendations"].append({"claim_id": claim_id, "correct": True})
        else:
            results["reserve_recommendation_report"]["recommendations"].append({"claim_id": claim_id, "correct": False})
    
    # Evaluate justifications
    correct_justifications = answer_key["reserve_recommendation_report"]["justifications"]
    submission_justifications = submission.get("reserve_recommendation_report", {}).get("justifications", "")
    if submission_justifications.strip() == correct_justifications.strip():
        results["reserve_recommendation_report"]["justifications"] = "Correct"
    else:
        results["reserve_recommendation_report"]["justifications"] = "Incorrect"
    
    # Calculate overall score
    total_reserves = len(correct_reserves)
    total_recommendations = len(correct_recommendations)
    total_justifications = 1  # Only one justification to evaluate
    
    total_correct = reserve_correct_count + recommendation_correct_count
    if results["reserve_recommendation_report"]["justifications"] == "Correct":
        total_correct += 1
    
    total_possible = total_reserves + total_recommendations + total_justifications
    overall_score = (total_correct / total_possible) * 100
    results["overall_score"] = overall_score
    
    # Save results to file
    with open(result_file, 'w') as file:
        json.dump(results, file, indent=4)

# Example usage
evaluate_submission('test_submission.json', 'answer_key.json', 'test_results.json')