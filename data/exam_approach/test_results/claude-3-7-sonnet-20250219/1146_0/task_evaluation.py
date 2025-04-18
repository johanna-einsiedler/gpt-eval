import json
import sys
from typing import Dict, Any


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_exercise1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 1 - Procurement Scenarios."""
    result = {"points": 0, "max_points": 30, "details": {}}
    
    for scenario_num in range(1, 4):
        scenario_result = {"points": 0, "max_points": 10, "feedback": []}
        
        # Check violation code
        submission_code = submission["exercise1"][f"scenario{scenario_num}_violation_code"]
        answer_code = answer_key["exercise1"][f"scenario{scenario_num}_violation_code"]
        
        # Special case for scenario 1 where either ETH-02 or COR-03 is acceptable
        if scenario_num == 1 and submission_code in ["ETH-02", "COR-03"]:
            scenario_result["points"] += 5
            scenario_result["feedback"].append("Correct violation code identified.")
        elif submission_code == answer_code:
            scenario_result["points"] += 5
            scenario_result["feedback"].append("Correct violation code identified.")
        else:
            scenario_result["feedback"].append(f"Incorrect violation code. Expected: {answer_code}, Got: {submission_code}")
        
        # Check regulation reference
        submission_ref = submission["exercise1"][f"scenario{scenario_num}_regulation_reference"]
        answer_ref = answer_key["exercise1"][f"scenario{scenario_num}_regulation_reference"]
        
        # For scenario 1, accept reference that matches the violation code provided
        if scenario_num == 1:
            alt_ref = "Anti-Corruption Act of 2010, Section 7"
            if (submission_code == "ETH-02" and submission_ref == answer_ref) or \
               (submission_code == "COR-03" and submission_ref == alt_ref):
                scenario_result["points"] += 5
                scenario_result["feedback"].append("Correct regulation reference provided.")
            else:
                scenario_result["feedback"].append("Incorrect regulation reference for the violation code.")
        elif submission_ref == answer_ref:
            scenario_result["points"] += 5
            scenario_result["feedback"].append("Correct regulation reference provided.")
        else:
            scenario_result["feedback"].append(f"Incorrect regulation reference. Expected: {answer_ref}, Got: {submission_ref}")
        
        result["details"][f"Scenario {scenario_num}"] = scenario_result
        result["points"] += scenario_result["points"]
    
    return result


def evaluate_exercise2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 2 - Policy Update."""
    result = {"points": 0, "max_points": 30, "details": {}}
    
    # Check policy section
    policy_result = {"points": 0, "max_points": 10, "feedback": []}
    if submission["exercise2"]["policy_section"] == answer_key["exercise2"]["policy_section"]:
        policy_result["points"] = 10
        policy_result["feedback"].append("Correct policy section identified.")
    else:
        policy_result["feedback"].append(f"Incorrect policy section. Expected: {answer_key['exercise2']['policy_section']}, Got: {submission['exercise2']['policy_section']}")
    result["details"]["Policy Section"] = policy_result
    result["points"] += policy_result["points"]
    
    # Check update required
    update_result = {"points": 0, "max_points": 10, "feedback": []}
    if submission["exercise2"]["update_required"] == answer_key["exercise2"]["update_required"]:
        update_result["points"] = 10
        update_result["feedback"].append("Correct determination of update requirement.")
    else:
        update_result["feedback"].append(f"Incorrect update requirement. Expected: {answer_key['exercise2']['update_required']}, Got: {submission['exercise2']['update_required']}")
    result["details"]["Update Required"] = update_result
    result["points"] += update_result["points"]
    
    # Check compliance status code
    status_result = {"points": 0, "max_points": 10, "feedback": []}
    if submission["exercise2"]["compliance_status_code"] == answer_key["exercise2"]["compliance_status_code"]:
        status_result["points"] = 10
        status_result["feedback"].append("Correct compliance status code selected.")
    else:
        status_result["feedback"].append(f"Incorrect compliance status code. Expected: {answer_key['exercise2']['compliance_status_code']}, Got: {submission['exercise2']['compliance_status_code']}")
    result["details"]["Compliance Status Code"] = status_result
    result["points"] += status_result["points"]
    
    return result


def evaluate_exercise3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 3 - Supplier Contract Review."""
    result = {"points": 0, "max_points": 40, "details": {}}
    
    # Evaluate each clause
    for clause_num in range(1, 4):
        clause_result = {"points": 0, "max_points": 10, "feedback": []}
        
        # Check if compliant
        compliant_key = f"clause{clause_num}_compliant"
        violation_key = f"clause{clause_num}_violation_code"
        
        if submission["exercise3"][compliant_key] == answer_key["exercise3"][compliant_key]:
            clause_result["points"] += 5
            clause_result["feedback"].append("Correct compliance determination.")
        else:
            clause_result["feedback"].append(f"Incorrect compliance determination. Expected: {answer_key['exercise3'][compliant_key]}, Got: {submission['exercise3'][compliant_key]}")
        
        # Check violation code
        if submission["exercise3"][compliant_key] == True and submission["exercise3"][violation_key] == "N/A":
            # If marked as compliant and violation code is N/A
            if answer_key["exercise3"][compliant_key] == True:
                clause_result["points"] += 5
                clause_result["feedback"].append("Correctly provided N/A for violation code on compliant clause.")
        elif submission["exercise3"][compliant_key] == False:
            # If marked as non-compliant, check violation code
            if submission["exercise3"][violation_key] == answer_key["exercise3"][violation_key]:
                clause_result["points"] += 5
                clause_result["feedback"].append("Correct violation code provided.")
            else:
                clause_result["feedback"].append(f"Incorrect violation code. Expected: {answer_key['exercise3'][violation_key]}, Got: {submission['exercise3'][violation_key]}")
        
        result["details"][f"Clause {clause_num}"] = clause_result
        result["points"] += clause_result["points"]
    
    # Check overall status code
    status_result = {"points": 0, "max_points": 10, "feedback": []}
    if submission["exercise3"]["overall_status_code"] == answer_key["exercise3"]["overall_status_code"]:
        status_result["points"] = 10
        status_result["feedback"].append("Correct overall status code selected.")
    else:
        status_result["feedback"].append(f"Incorrect overall status code. Expected: {answer_key['exercise3']['overall_status_code']}, Got: {submission['exercise3']['overall_status_code']}")
    result["details"]["Overall Status"] = status_result
    result["points"] += status_result["points"]
    
    return result


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "exercise1": evaluate_exercise1(submission, answer_key),
        "exercise2": evaluate_exercise2(submission, answer_key),
        "exercise3": evaluate_exercise3(submission, answer_key),
    }
    
    # Calculate total score
    total_points = sum(results[ex]["points"] for ex in ["exercise1", "exercise2", "exercise3"])
    max_points = sum(results[ex]["max_points"] for ex in ["exercise1", "exercise2", "exercise3"])
    overall_percentage = (total_points / max_points) * 100
    
    # Add overall assessment
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["overall_score"] = round(overall_percentage, 2)
    
    if overall_percentage >= 90:
        results["performance_level"] = "Excellent"
    elif overall_percentage >= 70:
        results["performance_level"] = "Pass"
    else:
        results["performance_level"] = "Fail"
    
    return results


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}% ({results['performance_level']})")


if __name__ == "__main__":
    main()