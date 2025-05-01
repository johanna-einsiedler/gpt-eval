#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Policy Provision Comparison."""
    score = 0
    max_score = 20
    details = {}
    
    # Incontestability Periods (4 points)
    incontestability_score = 0
    incontestability_details = {}
    for policy_type in answer_key["task1"]["incontestability_periods"]:
        correct = answer_key["task1"]["incontestability_periods"][policy_type]
        submitted = submission["task1"]["incontestability_periods"].get(policy_type)
        is_correct = submitted == correct
        incontestability_details[policy_type] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": is_correct,
            "points": 1 if is_correct else 0
        }
        if is_correct:
            incontestability_score += 1
    
    # Provisions Present (12 points)
    provisions_score = 0
    provisions_details = {}
    for policy_type in answer_key["task1"]["provisions_present"]:
        policy_details = {}
        for provision in answer_key["task1"]["provisions_present"][policy_type]:
            correct = answer_key["task1"]["provisions_present"][policy_type][provision]
            submitted = submission["task1"]["provisions_present"].get(policy_type, {}).get(provision)
            is_correct = submitted == correct
            policy_details[provision] = {
                "submitted": submitted,
                "correct": correct,
                "is_correct": is_correct,
                "points": 0.75 if is_correct else 0
            }
            if is_correct:
                provisions_score += 0.75
        provisions_details[policy_type] = policy_details
    
    # Cancellation Provisions (4 points)
    cancellation_score = 0
    cancellation_details = {}
    for policy_type in answer_key["task1"]["cancellation_provisions"]:
        correct = answer_key["task1"]["cancellation_provisions"][policy_type]
        submitted = submission["task1"]["cancellation_provisions"].get(policy_type)
        
        # Full credit for exact match
        if submitted == correct:
            points = 1
            partial = False
        # Partial credit if they identified the section but not exact text
        elif submitted and correct.split(":")[0] in submitted:
            points = 0.5
            partial = True
        else:
            points = 0
            partial = False
            
        cancellation_details[policy_type] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": submitted == correct,
            "partial_credit": partial,
            "points": points
        }
        cancellation_score += points
    
    # Calculate total score for Task 1
    task1_score = incontestability_score + provisions_score + cancellation_score
    
    details = {
        "incontestability_periods": {
            "score": incontestability_score,
            "max_score": 4,
            "details": incontestability_details
        },
        "provisions_present": {
            "score": provisions_score,
            "max_score": 12,
            "details": provisions_details
        },
        "cancellation_provisions": {
            "score": cancellation_score,
            "max_score": 4,
            "details": cancellation_details
        },
        "total_score": task1_score,
        "max_score": max_score
    }
    
    return task1_score, details

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Provision Compliance Analysis."""
    score = 0
    max_score = 10
    details = {}
    
    # Non-Compliant Provisions (6 points)
    non_compliant_score = 0
    non_compliant_details = []
    
    # Create a list of correct policy sections and regulatory requirements
    correct_policy_sections = [item["policy_section"] for item in answer_key["task2"]["non_compliant_provisions"]]
    correct_regulatory_requirements = [item["regulatory_requirement"] for item in answer_key["task2"]["non_compliant_provisions"]]
    
    # Check each submitted non-compliant provision
    for submitted_item in submission["task2"]["non_compliant_provisions"]:
        item_details = {
            "submitted": submitted_item,
            "is_correct": False,
            "partial_credit": False,
            "points": 0
        }
        
        # Check if the submission matches any of the correct answers
        for correct_item in answer_key["task2"]["non_compliant_provisions"]:
            if (submitted_item.get("policy_section") == correct_item["policy_section"] and 
                submitted_item.get("regulatory_requirement") == correct_item["regulatory_requirement"]):
                item_details["is_correct"] = True
                item_details["points"] = 2
                non_compliant_score += 2
                break
            # Partial credit for correct policy section only
            elif submitted_item.get("policy_section") == correct_item["policy_section"]:
                item_details["partial_credit"] = True
                item_details["points"] = 1
                non_compliant_score += 1
                break
        
        non_compliant_details.append(item_details)
    
    # Add any missing correct answers to the details
    for correct_item in answer_key["task2"]["non_compliant_provisions"]:
        found = False
        for submitted_item in submission["task2"]["non_compliant_provisions"]:
            if (submitted_item.get("policy_section") == correct_item["policy_section"] and 
                submitted_item.get("regulatory_requirement") == correct_item["regulatory_requirement"]):
                found = True
                break
            elif submitted_item.get("policy_section") == correct_item["policy_section"]:
                found = True
                break
        
        if not found:
            non_compliant_details.append({
                "submitted": None,
                "correct": correct_item,
                "is_correct": False,
                "partial_credit": False,
                "points": 0
            })
    
    # Minimum Coverage Limits (4 points)
    coverage_score = 0
    coverage_details = {}
    for limit_type in answer_key["task2"]["minimum_coverage_limits"]:
        correct = answer_key["task2"]["minimum_coverage_limits"][limit_type]
        submitted = submission["task2"]["minimum_coverage_limits"].get(limit_type)
        is_correct = submitted == correct
        coverage_details[limit_type] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": is_correct,
            "points": 1.33 if is_correct else 0
        }
        if is_correct:
            coverage_score += 1.33
    
    # Calculate total score for Task 2
    task2_score = non_compliant_score + coverage_score
    
    details = {
        "non_compliant_provisions": {
            "score": non_compliant_score,
            "max_score": 6,
            "details": non_compliant_details
        },
        "minimum_coverage_limits": {
            "score": coverage_score,
            "max_score": 4,
            "details": coverage_details
        },
        "total_score": task2_score,
        "max_score": max_score
    }
    
    return task2_score, details

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Provision Identification."""
    score = 0
    max_score = 10
    details = {}
    
    for scenario in ["scenario1", "scenario2", "scenario3", "scenario4", "scenario5"]:
        scenario_score = 0
        scenario_details = {}
        
        # Check provision name (1 point)
        correct_name = answer_key["task3"][scenario]["provision_name"]
        submitted_name = submission["task3"][scenario].get("provision_name")
        name_correct = submitted_name == correct_name
        if name_correct:
            scenario_score += 1
        
        # Check policy section (1 point)
        correct_section = answer_key["task3"][scenario]["policy_section"]
        submitted_section = submission["task3"][scenario].get("policy_section")
        section_correct = submitted_section == correct_section
        if section_correct:
            scenario_score += 1
        
        scenario_details = {
            "provision_name": {
                "submitted": submitted_name,
                "correct": correct_name,
                "is_correct": name_correct,
                "points": 1 if name_correct else 0
            },
            "policy_section": {
                "submitted": submitted_section,
                "correct": correct_section,
                "is_correct": section_correct,
                "points": 1 if section_correct else 0
            },
            "total_points": scenario_score
        }
        
        details[scenario] = scenario_details
        score += scenario_score
    
    return score, {"scenarios": details, "total_score": score, "max_score": max_score}

def check_critical_elements(submission, answer_key, task_scores):
    """Check if the candidate meets the critical element requirements."""
    critical_elements_met = True
    critical_elements_details = {}
    
    # Critical Element 1: Correctly identifying at least 3 of 4 incontestability periods
    incontestability_correct = 0
    for policy_type in answer_key["task1"]["incontestability_periods"]:
        if submission["task1"]["incontestability_periods"].get(policy_type) == answer_key["task1"]["incontestability_periods"][policy_type]:
            incontestability_correct += 1
    
    critical_elements_details["incontestability_periods"] = {
        "requirement": "Correctly identifying at least 3 of 4 incontestability periods",
        "correct": incontestability_correct,
        "required": 3,
        "met": incontestability_correct >= 3
    }
    
    if incontestability_correct < 3:
        critical_elements_met = False
    
    # Critical Element 2: Correctly identifying at least 2 of 3 non-compliant provisions
    non_compliant_correct = 0
    for submitted_item in submission["task2"]["non_compliant_provisions"]:
        for correct_item in answer_key["task2"]["non_compliant_provisions"]:
            if (submitted_item.get("policy_section") == correct_item["policy_section"] and 
                submitted_item.get("regulatory_requirement") == correct_item["regulatory_requirement"]):
                non_compliant_correct += 1
                break
    
    critical_elements_details["non_compliant_provisions"] = {
        "requirement": "Correctly identifying at least 2 of 3 non-compliant provisions",
        "correct": non_compliant_correct,
        "required": 2,
        "met": non_compliant_correct >= 2
    }
    
    if non_compliant_correct < 2:
        critical_elements_met = False
    
    # Critical Element 3: Correctly identifying the provisions for at least 3 of 5 scenarios in Task 3
    scenarios_correct = 0
    for scenario in ["scenario1", "scenario2", "scenario3", "scenario4", "scenario5"]:
        if (submission["task3"][scenario].get("provision_name") == answer_key["task3"][scenario]["provision_name"] and
            submission["task3"][scenario].get("policy_section") == answer_key["task3"][scenario]["policy_section"]):
            scenarios_correct += 1
    
    critical_elements_details["scenarios"] = {
        "requirement": "Correctly identifying the provisions for at least 3 of 5 scenarios in Task 3",
        "correct": scenarios_correct,
        "required": 3,
        "met": scenarios_correct >= 3
    }
    
    if scenarios_correct < 3:
        critical_elements_met = False
    
    return critical_elements_met, critical_elements_details

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_score, task1_details = evaluate_task1(submission, answer_key)
    task2_score, task2_details = evaluate_task2(submission, answer_key)
    task3_score, task3_details = evaluate_task3(submission, answer_key)
    
    # Calculate total score
    total_score = task1_score + task2_score + task3_score
    max_possible_score = 40  # As specified in the evaluation criteria
    
    # Check critical elements
    critical_elements_met, critical_elements_details = check_critical_elements(
        submission, answer_key, {
            "task1": task1_score,
            "task2": task2_score,
            "task3": task3_score
        }
    )
    
    # Determine if the candidate passed
    passing_score = 28  # 70% of 40
    passed = total_score >= passing_score and critical_elements_met
    
    # Calculate overall percentage score
    overall_score = (total_score / max_possible_score) * 100
    
    # Prepare results
    results = {
        "overall_score": overall_score,
        "total_points": total_score,
        "max_possible_points": max_possible_score,
        "passing_score": passing_score,
        "passed": passed,
        "critical_elements_met": critical_elements_met,
        "critical_elements_details": critical_elements_details,
        "task_scores": {
            "task1": task1_details,
            "task2": task2_details,
            "task3": task3_details
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    print(f"Total points: {total_score}/{max_possible_score}")
    print(f"Passed: {passed}")

if __name__ == "__main__":
    main()