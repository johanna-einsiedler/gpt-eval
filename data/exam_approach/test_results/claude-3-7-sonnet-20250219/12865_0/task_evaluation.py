#!/usr/bin/env python3

import json
import sys
import math
from typing import Dict, Any, List

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def round_to_2_decimals(value: float) -> float:
    """Round a value to 2 decimal places."""
    return round(value * 100) / 100

def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Commission Calculation."""
    result = {
        "points_possible": 20,
        "points_earned": 0,
        "details": []
    }
    
    sub_amounts = submission.get("task1", {}).get("commissionAmounts", {})
    key_amounts = answer_key.get("task1", {}).get("commissionAmounts", {})
    
    # Check each category
    categories = ["musicSales", "livePerformances", "merchandising", "endorsements", "totalCommission"]
    correct_categories = 0
    
    for category in categories:
        sub_value = sub_amounts.get(category, 0)
        key_value = key_amounts.get(category, 0)
        
        is_correct = math.isclose(sub_value, key_value, abs_tol=0.01)
        if is_correct:
            correct_categories += 1
            
        result["details"].append({
            "category": category,
            "submission_value": sub_value,
            "expected_value": key_value,
            "is_correct": is_correct
        })
    
    # Score based on how many categories are correct
    if correct_categories == 5:  # All correct
        result["points_earned"] = 20
    elif correct_categories == 4:  # Minor error in one category, but total is correct
        result["points_earned"] = 16
    elif correct_categories == 3:  # Multiple minor errors
        result["points_earned"] = 12
    elif correct_categories > 0:  # Some correct calculations
        result["points_earned"] = 8
    else:  # All wrong
        result["points_earned"] = 0
        
    return result

def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Payment Discrepancy Identification."""
    result = {
        "points_possible": 20,
        "points_earned": 0,
        "details": {
            "discrepancies_found": [],
            "discrepancies_missed": [],
            "incorrect_calculations": [],
            "total_comparison": {
                "submission_value": 0,
                "expected_value": 0,
                "is_correct": False
            }
        }
    }
    
    # Extract discrepancies from submission and answer key
    sub_discrepancies = submission.get("task2", {}).get("discrepancies", [])
    key_discrepancies = answer_key.get("task2", {}).get("discrepancies", [])
    
    # Map answer key discrepancies by paymentId for easier lookup
    key_discrepancies_map = {d["paymentId"]: d for d in key_discrepancies}
    
    # Check which discrepancies were found and which were missed
    found_payment_ids = set()
    
    for sub_d in sub_discrepancies:
        payment_id = sub_d.get("paymentId", "")
        
        if payment_id in key_discrepancies_map:
            found_payment_ids.add(payment_id)
            key_d = key_discrepancies_map[payment_id]
            
            # Check if the calculated values match
            expected_correct = math.isclose(sub_d.get("expectedAmount", 0), key_d.get("expectedAmount", 0), abs_tol=0.01)
            actual_correct = math.isclose(sub_d.get("actualAmount", 0), key_d.get("actualAmount", 0), abs_tol=0.01)
            diff_correct = math.isclose(sub_d.get("difference", 0), key_d.get("difference", 0), abs_tol=0.01)
            
            if expected_correct and actual_correct and diff_correct:
                result["details"]["discrepancies_found"].append({
                    "paymentId": payment_id,
                    "correct_calculation": True
                })
            else:
                result["details"]["incorrect_calculations"].append({
                    "paymentId": payment_id,
                    "submission": sub_d,
                    "expected": key_d
                })
        else:
            # This is a false positive - they identified a discrepancy that doesn't exist
            result["details"]["incorrect_calculations"].append({
                "paymentId": payment_id,
                "submission": sub_d,
                "expected": "No discrepancy should be reported for this payment ID"
            })
    
    # Check for missed discrepancies
    for payment_id, key_d in key_discrepancies_map.items():
        if payment_id not in found_payment_ids:
            result["details"]["discrepancies_missed"].append(key_d)
    
    # Check the total discrepancy amount
    sub_total = submission.get("task2", {}).get("totalDiscrepancyAmount", 0)
    key_total = answer_key.get("task2", {}).get("totalDiscrepancyAmount", 0)
    
    total_is_correct = math.isclose(sub_total, key_total, abs_tol=0.01)
    
    result["details"]["total_comparison"] = {
        "submission_value": sub_total,
        "expected_value": key_total,
        "is_correct": total_is_correct
    }
    
    # Calculate score
    num_key_discrepancies = len(key_discrepancies)
    num_found_correctly = len(result["details"]["discrepancies_found"])
    num_calculated_incorrectly = len(result["details"]["incorrect_calculations"])
    num_missed = len(result["details"]["discrepancies_missed"])
    
    # Critical failure check - missing more than 2 discrepancies
    critical_failure = num_missed > 2
    
    if critical_failure:
        result["points_earned"] = 0
        result["critical_failure"] = "Missing more than two discrepancies"
    elif num_found_correctly == num_key_discrepancies and total_is_correct:
        # All discrepancies found and total is correct
        result["points_earned"] = 20
    elif num_found_correctly == num_key_discrepancies and not total_is_correct:
        # All discrepancies found but total is wrong
        result["points_earned"] = 16
    elif num_found_correctly >= num_key_discrepancies - 1:
        # Found most discrepancies
        result["points_earned"] = 12
    elif num_found_correctly >= num_key_discrepancies - 2:
        # Found some discrepancies
        result["points_earned"] = 8
    else:
        # Found few or no discrepancies
        result["points_earned"] = 4
        
    return result

def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Collection Process Implementation."""
    result = {
        "points_possible": 20,
        "points_earned": 0,
        "details": {
            "priority_client": {
                "submission_value": "",
                "expected_value": "",
                "is_correct": False
            },
            "collection_steps": {
                "submission_value": [],
                "expected_value": [],
                "evaluation": ""
            },
            "recovery_amount": {
                "submission_value": 0,
                "expected_value": 0,
                "is_correct": False
            }
        }
    }
    
    # Extract values from submission and answer key
    sub_task3 = submission.get("task3", {})
    key_task3 = answer_key.get("task3", {})
    
    # Check priority client
    sub_client = sub_task3.get("priorityClient", "").upper()
    key_client = key_task3.get("priorityClient", "").upper()
    client_correct = sub_client == key_client
    
    result["details"]["priority_client"] = {
        "submission_value": sub_task3.get("priorityClient", ""),
        "expected_value": key_task3.get("priorityClient", ""),
        "is_correct": client_correct
    }
    
    # Check collection steps
    sub_steps = sub_task3.get("collectionSteps", [])
    key_steps = key_task3.get("collectionSteps", [])
    
    # Convert string numbers to integers for comparison if needed
    sub_steps_normalized = [str(step).strip() for step in sub_steps]
    key_steps_normalized = [str(step).strip() for step in key_steps]
    
    # Evaluate steps - exact match is best, but we need to be flexible
    if sub_steps_normalized == key_steps_normalized:
        steps_evaluation = "Excellent - Perfect match with recommended steps"
        steps_score = 1.0
    elif set(sub_steps_normalized) == set(key_steps_normalized):
        steps_evaluation = "Good - Same steps but different order"
        steps_score = 0.8
    else:
        # Check if the steps are at least in the same general category (initial, secondary, escalation)
        # This is a simplified evaluation - in reality, we would need domain knowledge
        steps_evaluation = "Acceptable - Different approach but reasonable"
        steps_score = 0.5
        
        # Check if their approach is completely wrong
        if not client_correct:
            steps_evaluation = "Poor - Inappropriate collection approach for the situation"
            steps_score = 0.2
    
    result["details"]["collection_steps"] = {
        "submission_value": sub_steps,
        "expected_value": key_steps,
        "evaluation": steps_evaluation,
        "score": steps_score
    }
    
    # Check recovery amount
    sub_amount = sub_task3.get("expectedRecoveryAmount", 0)
    key_amount = key_task3.get("expectedRecoveryAmount", 0)
    amount_correct = math.isclose(sub_amount, key_amount, abs_tol=0.01)
    
    result["details"]["recovery_amount"] = {
        "submission_value": sub_amount,
        "expected_value": key_amount,
        "is_correct": amount_correct
    }
    
    # Calculate overall score
    # Critical failure check - completely incorrect approach
    if not client_correct and steps_score < 0.3:
        result["points_earned"] = 0
        result["critical_failure"] = "Fundamental misunderstanding of collection prioritization"
    else:
        # Weight: client (40%), steps (40%), amount (20%)
        score = (0.4 * int(client_correct)) + (0.4 * steps_score) + (0.2 * int(amount_correct))
        result["points_earned"] = round(score * 20)
        
    return result

def evaluate_task4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 4: Commission Split Determination."""
    result = {
        "points_possible": 20,
        "points_earned": 0,
        "details": {
            "commission_splits": {},
            "split_application": {
                "submission_value": None,
                "expected_value": None,
                "is_correct": False
            }
        }
    }
    
    # Extract values from submission and answer key
    sub_task4 = submission.get("task4", {})
    key_task4 = answer_key.get("task4", {})
    
    # Check commission splits
    sub_splits = sub_task4.get("commissionSplits", {})
    key_splits = key_task4.get("commissionSplits", {})
    
    roles = ["primaryAgent", "coAgent", "businessManager"]
    incorrect_roles = []
    
    for role in roles:
        sub_value = sub_splits.get(role, 0)
        key_value = key_splits.get(role, 0)
        is_correct = math.isclose(sub_value, key_value, abs_tol=0.01)
        
        result["details"]["commission_splits"][role] = {
            "submission_value": sub_value,
            "expected_value": key_value,
            "is_correct": is_correct
        }
        
        if not is_correct:
            incorrect_roles.append(role)
    
    # Check split application determination
    sub_correct_split = sub_task4.get("correctSplitApplied", None)
    key_correct_split = key_task4.get("correctSplitApplied", None)
    split_application_correct = sub_correct_split == key_correct_split
    
    result["details"]["split_application"] = {
        "submission_value": sub_correct_split,
        "expected_value": key_correct_split,
        "is_correct": split_application_correct
    }
    
    # Calculate score
    # Critical failure check - fundamental misunderstanding
    all_splits_incorrect = len(incorrect_roles) == len(roles)
    critical_failure = all_splits_incorrect and not split_application_correct
    
    if critical_failure:
        result["points_earned"] = 0
        result["critical_failure"] = "Fundamental misunderstanding of commission split structure"
    else:
        # Calculate points based on correctness
        correct_split_calculations = len(roles) - len(incorrect_roles)
        
        if correct_split_calculations == len(roles) and split_application_correct:
            # All calculations correct and correct split determination
            result["points_earned"] = 20
        elif correct_split_calculations == len(roles) and not split_application_correct:
            # All calculations correct but wrong split determination
            result["points_earned"] = 16
        elif correct_split_calculations >= 1 and split_application_correct:
            # Some calculations correct and correct split determination
            result["points_earned"] = 12
        else:
            # Multiple errors
            result["points_earned"] = 8
            
    return result

def evaluate_task5(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 5: Payment Documentation."""
    result = {
        "points_possible": 20,
        "points_earned": 0,
        "details": {}
    }
    
    # Extract values from submission and answer key
    sub_task5 = submission.get("task5", {})
    key_task5 = answer_key.get("task5", {})
    
    # Check each financial metric
    metrics = ["clientNetEarnings", "totalCommissionsCollected", "outstandingPayments"]
    statuses = ["reconciliationStatus"]
    
    for metric in metrics + statuses:
        sub_value = sub_task5.get(metric, 0 if metric in metrics else "")
        key_value = key_task5.get(metric, 0 if metric in metrics else "")
        
        if metric in metrics:
            is_correct = math.isclose(sub_value, key_value, abs_tol=0.01)
        else:
            is_correct = sub_value == key_value
            
        result["details"][metric] = {
            "submission_value": sub_value,
            "expected_value": key_value,
            "is_correct": is_correct
        }
    
    # Calculate score
    correct_metrics = sum(1 for m in result["details"].values() if m["is_correct"])
    
    # Critical failure check - major accounting errors
    # Consider including pending payments as received a critical error if applicable
    critical_failure = False
    client_earnings_error = abs(result["details"]["clientNetEarnings"]["submission_value"] - 
                               result["details"]["clientNetEarnings"]["expected_value"]) > 10000
    
    if client_earnings_error:
        critical_failure = True
        result["critical_failure"] = "Major accounting errors in financial calculations"
    
    if critical_failure:
        result["points_earned"] = 0
    elif correct_metrics == 4:  # All correct
        result["points_earned"] = 20
    elif correct_metrics == 3:  # One error
        result["points_earned"] = 15
    elif correct_metrics == 2:  # Two errors
        result["points_earned"] = 10
    else:  # Multiple errors
        result["points_earned"] = 5
        
    return result

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "task1_results": evaluate_task1(submission, answer_key),
        "task2_results": evaluate_task2(submission, answer_key),
        "task3_results": evaluate_task3(submission, answer_key),
        "task4_results": evaluate_task4(submission, answer_key),
        "task5_results": evaluate_task5(submission, answer_key)
    }
    
    # Calculate overall score
    total_possible = sum(task["points_possible"] for task in [
        results["task1_results"],
        results["task2_results"],
        results["task3_results"],
        results["task4_results"],
        results["task5_results"]
    ])
    
    total_earned = sum(task["points_earned"] for task in [
        results["task1_results"],
        results["task2_results"],
        results["task3_results"],
        results["task4_results"],
        results["task5_results"]
    ])
    
    # Check for any critical failures
    has_critical_failure = any("critical_failure" in task for task in [
        results["task1_results"],
        results["task2_results"],
        results["task3_results"],
        results["task4_results"],
        results["task5_results"]
    ])
    
    overall_score = (total_earned / total_possible) * 100 if total_possible > 0 else 0
    
    # According to the evaluation criteria, any critical failure results in automatic fail
    if has_critical_failure:
        results["pass_fail"] = "FAIL"
        results["reason"] = "Critical failure in one or more tasks"
    else:
        results["pass_fail"] = "PASS" if overall_score >= 70 else "FAIL"
        results["reason"] = f"Overall score {overall_score:.2f}% {'meets' if overall_score >= 70 else 'does not meet'} the 70% passing threshold"
    
    results["overall_score"] = round_to_2_decimals(overall_score)
    
    return results

def main():
    """Main function to run the evaluation script."""
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
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {results['pass_fail']} - {results['reason']}")

if __name__ == "__main__":
    main()