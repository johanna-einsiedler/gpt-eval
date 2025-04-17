#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any


def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_status(submission: Dict, answer_key: Dict) -> Dict[str, int]:
    """Evaluate the correctness of claim status determinations."""
    results = {"points": 0, "max_points": 50, "details": {}}
    
    for claim_num in range(1, 6):
        claim_key = f"claim_{claim_num}"
        submission_claim = submission["claims"].get(claim_key, {})
        answer_claim = answer_key["claims"].get(claim_key, {})
        
        submission_status = submission_claim.get("status", "")
        answer_status = answer_claim.get("status", "")
        
        is_correct = submission_status == answer_status
        points = 10 if is_correct else 0
        
        results["details"][claim_key] = {
            "points": points,
            "max_points": 10,
            "submitted": submission_status,
            "expected": answer_status,
            "correct": is_correct
        }
        results["points"] += points
        
    return results


def evaluate_discrepancies(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the correctness of identified discrepancies."""
    results = {"points": 0, "max_points": 40, "details": {}}
    
    # Points allocation per claim
    point_values = {
        "claim_1": 5,  # No discrepancies
        "claim_2": 10,  # Two discrepancies (5 each)
        "claim_3": 10,  # One discrepancy
        "claim_4": 10,  # Two discrepancies (5 each)
        "claim_5": 5,   # No discrepancies
    }
    
    for claim_num in range(1, 6):
        claim_key = f"claim_{claim_num}"
        submission_claim = submission["claims"].get(claim_key, {})
        answer_claim = answer_key["claims"].get(claim_key, {})
        
        submission_discrepancies = submission_claim.get("discrepancies", [])
        answer_discrepancies = answer_claim.get("discrepancies", [])
        
        # Create sets of error codes from both submissions
        submission_codes = {d.get("error_code") for d in submission_discrepancies}
        answer_codes = {d.get("error_code") for d in answer_discrepancies}
        
        # Calculate correctly identified discrepancies
        correct_codes = submission_codes.intersection(answer_codes)
        
        # Handle evaluation differently based on whether there should be discrepancies
        if not answer_discrepancies:  # No discrepancies expected
            points = point_values[claim_key] if not submission_discrepancies else 0
            correct_percentage = 1.0 if not submission_discrepancies else 0.0
        else:  # Discrepancies expected
            # Calculate points based on number of correct discrepancies
            max_claim_points = point_values[claim_key]
            points_per_discrepancy = max_claim_points / len(answer_codes)
            points = len(correct_codes) * points_per_discrepancy
            
            # Handle partial credit for correct codes but incomplete descriptions
            if len(correct_codes) < len(submission_codes.intersection(answer_codes)):
                for code in correct_codes:
                    # Check if description is incomplete
                    sub_desc = next((d.get("description", "") for d in submission_discrepancies 
                                   if d.get("error_code") == code), "")
                    ans_desc = next((d.get("description", "") for d in answer_discrepancies 
                                   if d.get("error_code") == code), "")
                    
                    # Partial credit (3 points) for correct code but incomplete description
                    if sub_desc and len(sub_desc) < len(ans_desc) * 0.5:  # Simplified check
                        points -= (points_per_discrepancy - 3)
            
            correct_percentage = len(correct_codes) / len(answer_codes) if answer_codes else 0.0
            
            # No points for extraneous discrepancies
            if len(submission_codes - answer_codes) > 0:
                points = max(0, points - 3)  # Penalty for incorrect discrepancies
        
        results["details"][claim_key] = {
            "points": round(points, 1),
            "max_points": point_values[claim_key],
            "correct_codes": list(correct_codes),
            "missing_codes": list(answer_codes - submission_codes),
            "extra_codes": list(submission_codes - answer_codes),
            "correct_percentage": correct_percentage
        }
        results["points"] += points
    
    results["points"] = round(results["points"], 1)
    return results


def evaluate_additional_info(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the correctness of additional information needed."""
    results = {"points": 0, "max_points": 10, "details": {}}
    
    # Claims that require additional information in the answer key
    claims_needing_info = ["claim_3", "claim_4"]
    points_per_claim = 5
    
    for claim_key in claims_needing_info:
        submission_claim = submission["claims"].get(claim_key, {})
        answer_claim = answer_key["claims"].get(claim_key, {})
        
        submission_status = submission_claim.get("status", "")
        submission_info = submission_claim.get("additional_information_needed", [])
        answer_info = answer_claim.get("additional_information_needed", [])
        
        # If status is not "Requires Additional Information", no points
        if submission_status != "Requires Additional Information":
            points = 0
            reason = "Wrong status (should be 'Requires Additional Information')"
        # If no additional info provided but required, no points
        elif not submission_info and answer_info:
            points = 0
            reason = "No additional information provided"
        else:
            # Simple check: is there overlap in the additional information?
            # This is simplified - in a real evaluation you might want more sophisticated matching
            has_relevant_info = any(any(sub_info.lower() in ans_info.lower() or 
                                       ans_info.lower() in sub_info.lower() 
                                       for ans_info in answer_info)
                                   for sub_info in submission_info)
            
            points = points_per_claim if has_relevant_info else 0
            reason = "Correct" if has_relevant_info else "Additional information not relevant to discrepancies"
        
        results["details"][claim_key] = {
            "points": points,
            "max_points": points_per_claim,
            "submitted": submission_info,
            "expected": answer_info,
            "reason": reason
        }
        results["points"] += points
    
    return results


def check_critical_element(submission: Dict) -> bool:
    """Check if the candidate correctly identified Claim #2 as Invalid (critical element)."""
    claim2 = submission["claims"].get("claim_2", {})
    return claim2.get("status") == "Invalid"


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the full submission against the answer key."""
    status_results = evaluate_status(submission, answer_key)
    discrepancy_results = evaluate_discrepancies(submission, answer_key)
    additional_info_results = evaluate_additional_info(submission, answer_key)
    
    # Calculate total score
    total_points = status_results["points"] + discrepancy_results["points"] + additional_info_results["points"]
    max_points = status_results["max_points"] + discrepancy_results["max_points"] + additional_info_results["max_points"]
    overall_percentage = (total_points / max_points) * 100
    
    # Check critical element
    critical_element_passed = check_critical_element(submission)
    passed = overall_percentage >= 75 and critical_element_passed
    
    if not critical_element_passed and overall_percentage >= 75:
        fail_reason = "Failed to correctly identify Claim #2 as Invalid (critical element)"
    elif overall_percentage < 75:
        fail_reason = f"Overall score below 75% threshold ({overall_percentage:.1f}%)"
    else:
        fail_reason = None
    
    return {
        "overall_score": round(overall_percentage, 1),
        "passing_threshold": 75,
        "passed": passed,
        "fail_reason": fail_reason,
        "critical_element_passed": critical_element_passed,
        "total_points": total_points,
        "max_points": max_points,
        "status_evaluation": status_results,
        "discrepancy_evaluation": discrepancy_results,
        "additional_info_evaluation": additional_info_results
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    if results['fail_reason']:
        print(f"Reason: {results['fail_reason']}")


if __name__ == "__main__":
    main()