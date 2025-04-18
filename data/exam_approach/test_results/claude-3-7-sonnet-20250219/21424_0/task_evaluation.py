#!/usr/bin/env python3
"""
Evaluation script for Claims Reserve Adjustment Practical Exam.
Usage: python task_evaluation.py test_submission.json answer_key.json
"""

import sys
import json
import os


def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_reserve_amount(candidate_reserve, expected_reserve):
    """Evaluate the reserve amount and return score and feedback."""
    # Calculate percentage difference
    percent_diff = abs(candidate_reserve - expected_reserve) / expected_reserve * 100
    
    if percent_diff <= 5:  # Superior performance: within 5%
        return 10, f"Excellent - within 5% of expected reserve"
    elif percent_diff <= 10:  # Passing: within 10%
        return 10, f"Good - within 10% of expected reserve"
    elif percent_diff <= 30:  # Substandard but not failing
        return 5, f"Needs improvement - {percent_diff:.1f}% from expected reserve"
    else:  # Automatic failure condition
        return 0, f"Unacceptable - {percent_diff:.1f}% from expected reserve"


def evaluate_reserve_code(candidate_code, expected_code):
    """Evaluate the reserve code and return score and feedback."""
    if candidate_code == expected_code:
        return 5, "Correct reserve change code"
    else:
        return 0, f"Incorrect code. Used {candidate_code} instead of {expected_code}"


def evaluate_category_code(candidate_code, expected_code):
    """Evaluate the category code and return score and feedback."""
    if candidate_code == expected_code:
        return 5, "Correct reserve category code"
    else:
        return 0, f"Incorrect category. Used {candidate_code} instead of {expected_code}"


def evaluate_justification(justification, expected_justification, scenario_data):
    """Evaluate the justification and return score and feedback."""
    if not justification:
        return 0, "No justification provided"
    
    # Count key content elements
    elements_found = 0
    feedback = []
    
    # Check for reference to new information
    if any(term in justification.lower() for term in ["new information", "updated", "report", "evaluation"]):
        elements_found += 1
    else:
        feedback.append("Missing reference to specific new information")
    
    # Check for reference to company policy
    if any(term in justification.lower() for term in ["section", "policy", "guidelines", "appendix"]):
        elements_found += 1
    else:
        feedback.append("Missing reference to company policies")
    
    # Check for calculation methodology
    if any(term in justification.lower() for term in ["calculat", "compon", "total", "estimate", "adjust"]):
        elements_found += 1
    else:
        feedback.append("Missing explanation of calculation methodology")
    
    # Evaluate length (assuming 50-200 words is reasonable)
    word_count = len(justification.split())
    if word_count < 20:
        feedback.append(f"Justification too brief ({word_count} words)")
    
    # Scoring
    if elements_found == 3:
        return 5, "Complete justification with all required elements"
    elif elements_found == 2:
        return 3, "Adequate justification, but " + feedback[0]
    elif elements_found == 1:
        return 1, "Minimal justification. " + " and ".join(feedback[:2])
    else:
        return 0, "Inadequate justification. " + " and ".join(feedback[:3])


def evaluate_scenario(candidate_scenario, answer_scenario):
    """Evaluate a single scenario and return score and feedback."""
    results = {
        "claim_number": candidate_scenario["claim_number"],
        "evaluation": {},
        "score": 0,
        "max_score": 25,
        "feedback": []
    }
    
    # Evaluate reserve amount
    candidate_reserve = candidate_scenario.get("recommended_reserve", 0)
    expected_reserve = answer_scenario.get("recommended_reserve", 0)
    score, feedback = evaluate_reserve_amount(candidate_reserve, expected_reserve)
    results["evaluation"]["reserve_amount"] = {
        "candidate_value": candidate_reserve,
        "expected_value": expected_reserve,
        "score": score,
        "max_score": 10,
        "feedback": feedback
    }
    results["score"] += score
    results["feedback"].append(feedback)
    
    # Evaluate reserve change code
    candidate_code = candidate_scenario.get("reserve_change_code", "")
    expected_code = answer_scenario.get("reserve_change_code", "")
    score, feedback = evaluate_reserve_code(candidate_code, expected_code)
    results["evaluation"]["reserve_change_code"] = {
        "candidate_value": candidate_code,
        "expected_value": expected_code,
        "score": score,
        "max_score": 5,
        "feedback": feedback
    }
    results["score"] += score
    results["feedback"].append(feedback)
    
    # Evaluate reserve category code
    candidate_category = candidate_scenario.get("reserve_category_code", "")
    expected_category = answer_scenario.get("reserve_category_code", "")
    score, feedback = evaluate_category_code(candidate_category, expected_category)
    results["evaluation"]["reserve_category_code"] = {
        "candidate_value": candidate_category,
        "expected_value": expected_category,
        "score": score,
        "max_score": 5,
        "feedback": feedback
    }
    results["score"] += score
    results["feedback"].append(feedback)
    
    # Evaluate justification
    justification = candidate_scenario.get("justification", "")
    expected_justification = answer_scenario.get("justification", "")
    
    # Use reserve_explanation if justification is not present in the answer key
    if not expected_justification and "reserve_explanation" in answer_scenario:
        expected_justification = answer_scenario["reserve_explanation"]
    
    score, feedback = evaluate_justification(justification, expected_justification, candidate_scenario)
    results["evaluation"]["justification"] = {
        "score": score,
        "max_score": 5,
        "feedback": feedback
    }
    results["score"] += score
    results["feedback"].append(feedback)
    
    return results


def evaluate_submission(submission, answer_key):
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "scenario_results": [],
        "total_score": 0,
        "max_score": 100,
        "overall_score": 0,
        "passing_threshold": 75,
        "passed": False,
        "overall_feedback": []
    }
    
    # Create a mapping of claim numbers to answer key scenarios
    answer_scenarios = {s["claim_number"]: s for s in answer_key["scenarios"]}
    
    # Evaluate each scenario in the submission
    for candidate_scenario in submission.get("scenarios", []):
        claim_number = candidate_scenario.get("claim_number")
        if claim_number in answer_scenarios:
            scenario_result = evaluate_scenario(candidate_scenario, answer_scenarios[claim_number])
            results["scenario_results"].append(scenario_result)
            results["total_score"] += scenario_result["score"]
        else:
            # Handle missing or invalid claim number
            results["overall_feedback"].append(f"Missing or invalid claim number: {claim_number}")
    
    # Calculate overall score as percentage
    results["overall_score"] = (results["total_score"] / results["max_score"]) * 100
    
    # Determine if candidate passed
    results["passed"] = results["total_score"] >= results["passing_threshold"]
    
    # Generate overall feedback
    correct_reserves = sum(1 for r in results["scenario_results"] 
                          if r["evaluation"]["reserve_amount"]["score"] >= 10)
    correct_codes = sum(1 for r in results["scenario_results"] 
                        if r["evaluation"]["reserve_change_code"]["score"] == 5)
    correct_categories = sum(1 for r in results["scenario_results"] 
                            if r["evaluation"]["reserve_category_code"]["score"] == 5)
    adequate_justifications = sum(1 for r in results["scenario_results"] 
                                 if r["evaluation"]["justification"]["score"] >= 3)
    
    # Add performance summary
    results["overall_feedback"].append(f"Correctly calculated reserves for {correct_reserves} of 4 scenarios")
    results["overall_feedback"].append(f"Correctly identified reserve codes for {correct_codes} of 4 scenarios")
    results["overall_feedback"].append(f"Correctly identified category codes for {correct_categories} of 4 scenarios")
    results["overall_feedback"].append(f"Provided adequate justifications for {adequate_justifications} of 4 scenarios")
    
    if results["overall_score"] >= 90:
        results["overall_feedback"].append("Superior performance demonstrated")
    elif results["passed"]:
        results["overall_feedback"].append("Satisfactory performance demonstrated")
    else:
        results["overall_feedback"].append("Performance below passing threshold")
    
    # Check for automatic failure conditions
    if correct_reserves == 0:
        results["overall_feedback"].append("AUTOMATIC FAILURE: Failed to appropriately adjust any reserves")
        results["passed"] = False
    
    if any(r["evaluation"]["reserve_amount"]["score"] == 0 for r in results["scenario_results"]):
        results["overall_feedback"].append("AUTOMATIC FAILURE: At least one reserve recommendation is dramatically insufficient or excessive")
        results["passed"] = False
    
    return results


def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()