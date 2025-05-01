#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_compliance_assessment(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the compliance assessment section."""
    max_points = 15
    earned_points = 0
    details = {}
    
    submission_compliance = submission.get("compliance_assessment", {})
    key_compliance = answer_key.get("compliance_assessment", {})
    
    for category in ["delivery_compliance", "quality_compliance", "pricing_compliance"]:
        if submission_compliance.get(category) == key_compliance.get(category):
            earned_points += 5
            details[category] = {"correct": True, "points": 5, "max_points": 5}
        else:
            details[category] = {"correct": False, "points": 0, "max_points": 5}
    
    return earned_points, {"points": earned_points, "max_points": max_points, "details": details}

def evaluate_performance_metrics(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the performance metrics section."""
    max_points = 20
    earned_points = 0
    details = {}
    
    submission_metrics = submission.get("performance_metrics", {})
    key_metrics = answer_key.get("performance_metrics", {})
    
    for metric in ["on_time_delivery_percentage", "order_accuracy_percentage", 
                  "price_variance_percentage", "quality_rejection_rate"]:
        sub_value = submission_metrics.get(metric)
        key_value = key_metrics.get(metric)
        
        if sub_value is None or key_value is None:
            details[metric] = {"correct": False, "points": 0, "max_points": 5}
            continue
            
        # Check if values are within 1% for partial credit
        if abs(sub_value - key_value) < 0.01:  # Exact match
            earned_points += 5
            details[metric] = {"correct": True, "points": 5, "max_points": 5}
        elif abs(sub_value - key_value) <= 1.0:  # Within 1%
            earned_points += 3
            details[metric] = {"correct": "partial", "points": 3, "max_points": 5}
        else:
            details[metric] = {"correct": False, "points": 0, "max_points": 5}
    
    return earned_points, {"points": earned_points, "max_points": max_points, "details": details}

def evaluate_contract_violations(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the contract violations section."""
    max_points = 30
    earned_points = 0
    details = {}
    
    submission_violations = submission.get("contract_violations", [])
    key_violations = answer_key.get("contract_violations", [])
    
    # Create a dictionary of key violations for easier lookup
    key_violations_dict = {v["violation_id"]: v for v in key_violations}
    
    # Track which violations have been matched
    matched_violations = set()
    
    for i, sub_violation in enumerate(submission_violations):
        violation_id = sub_violation.get("violation_id")
        
        if violation_id not in key_violations_dict:
            details[f"violation_{i+1}"] = {"correct": False, "points": 0, "max_points": 6}
            continue
            
        key_violation = key_violations_dict[violation_id]
        matched_violations.add(violation_id)
        
        # Check if clause reference and occurrence count match
        clause_correct = sub_violation.get("clause_reference") == key_violation.get("clause_reference")
        count_correct = sub_violation.get("occurrence_count") == key_violation.get("occurrence_count")
        
        if clause_correct and count_correct:
            earned_points += 6
            details[f"violation_{i+1}"] = {"correct": True, "points": 6, "max_points": 6}
        else:
            earned_points += 3
            details[f"violation_{i+1}"] = {"correct": "partial", "points": 3, "max_points": 6}
    
    # Check for missing key violations
    for violation_id, key_violation in key_violations_dict.items():
        if violation_id not in matched_violations:
            details[f"missing_{violation_id}"] = {"correct": False, "points": 0, "max_points": 6}
    
    return earned_points, {"points": earned_points, "max_points": max_points, "details": details}

def evaluate_recommended_actions(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the recommended actions section."""
    max_points = 25
    earned_points = 0
    details = {}
    
    submission_actions = submission.get("recommended_actions", [])
    key_actions = answer_key.get("recommended_actions", [])
    
    # Create sets of action codes from submission and key
    sub_action_codes = {action.get("action_code") for action in submission_actions}
    key_action_codes = {action.get("action_code") for action in key_actions}
    
    # Check for COR-01 as highest priority (5 points)
    cor01_highest = False
    for action in submission_actions:
        if action.get("action_code") == "COR-01" and action.get("priority") == 1:
            cor01_highest = True
            earned_points += 5
            break
    
    details["COR-01_highest_priority"] = {"correct": cor01_highest, "points": 5 if cor01_highest else 0, "max_points": 5}
    
    # Check for appropriate actions (5 points each, up to 4 actions)
    matched_actions = sub_action_codes.intersection(key_action_codes)
    action_points = min(len(matched_actions), 4) * 5
    earned_points += action_points
    
    details["appropriate_actions"] = {
        "correct": len(matched_actions) >= 4, 
        "points": action_points, 
        "max_points": 20,
        "matched_actions": list(matched_actions)
    }
    
    return earned_points, {"points": earned_points, "max_points": max_points, "details": details}

def evaluate_contract_change(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the contract change determination."""
    max_points = 10
    earned_points = 0
    
    sub_change = submission.get("contract_change_required")
    key_change = answer_key.get("contract_change_required")
    
    if sub_change == key_change:
        earned_points = 10
        correct = True
    else:
        correct = False
    
    return earned_points, {"points": earned_points, "max_points": max_points, "correct": correct}

def check_critical_elements(submission: Dict, answer_key: Dict) -> Dict:
    """Check if critical elements are correctly identified."""
    critical_elements = {
        "all_compliance_areas_identified": False,
        "at_least_three_violations_identified": False,
        "corrective_action_needed": False
    }
    
    # Check compliance areas
    submission_compliance = submission.get("compliance_assessment", {})
    if (submission_compliance.get("delivery_compliance") is False and
        submission_compliance.get("quality_compliance") is False and
        submission_compliance.get("pricing_compliance") is False):
        critical_elements["all_compliance_areas_identified"] = True
    
    # Check violations
    submission_violations = submission.get("contract_violations", [])
    if len(submission_violations) >= 3:
        critical_elements["at_least_three_violations_identified"] = True
    
    # Check for COR-01 action
    submission_actions = submission.get("recommended_actions", [])
    for action in submission_actions:
        if action.get("action_code") == "COR-01":
            critical_elements["corrective_action_needed"] = True
            break
    
    return critical_elements

def determine_result(total_points: int, critical_elements: Dict) -> str:
    """Determine the final result based on points and critical elements."""
    all_critical_met = all(critical_elements.values())
    
    if total_points >= 75 and all_critical_met:
        return "Pass"
    elif total_points >= 65 and total_points < 75 and all_critical_met:
        return "Conditional Pass"
    elif not all_critical_met:
        return "Conditional Pass (missing critical elements)"
    else:
        return "Fail"

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    compliance_points, compliance_details = evaluate_compliance_assessment(submission, answer_key)
    metrics_points, metrics_details = evaluate_performance_metrics(submission, answer_key)
    violations_points, violations_details = evaluate_contract_violations(submission, answer_key)
    actions_points, actions_details = evaluate_recommended_actions(submission, answer_key)
    change_points, change_details = evaluate_contract_change(submission, answer_key)
    
    # Calculate total points
    total_points = compliance_points + metrics_points + violations_points + actions_points + change_points
    max_points = 100
    
    # Check critical elements
    critical_elements = check_critical_elements(submission, answer_key)
    
    # Determine result
    result = determine_result(total_points, critical_elements)
    
    # Calculate overall score as percentage
    overall_score = (total_points / max_points) * 100
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_score,
        "total_points": total_points,
        "max_points": max_points,
        "result": result,
        "critical_elements": critical_elements,
        "section_scores": {
            "compliance_assessment": compliance_details,
            "performance_metrics": metrics_details,
            "contract_violations": violations_details,
            "recommended_actions": actions_details,
            "contract_change": change_details
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()