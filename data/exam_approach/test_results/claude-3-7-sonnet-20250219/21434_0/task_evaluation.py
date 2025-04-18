#!/usr/bin/env python3

import json
import sys
import os


def load_json_file(filename):
    """Load and parse JSON from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_exercise1(submission, answer_key):
    """Evaluate Exercise 1: Claim Organization and Categorization."""
    results = {
        "settled_claims": {
            "correct": False,
            "score": 0,
            "max_score": 6,
            "details": "Incorrect settled claims"
        },
        "pending_claims": {
            "correct": False,
            "score": 0,
            "max_score": 8,
            "details": "Incorrect pending claims"
        },
        "denied_claims": {
            "correct": False,
            "score": 0,
            "max_score": 6,
            "details": "Incorrect denied claims"
        }
    }
    
    # Check settled claims
    sub_settled = set(submission.get("settled_claims", []))
    key_settled = set(answer_key.get("settled_claims", []))
    
    if sub_settled == key_settled:
        results["settled_claims"]["correct"] = True
        results["settled_claims"]["score"] = 6
        results["settled_claims"]["details"] = "All settled claims correct"
    else:
        # Calculate percentage correct for failure condition
        if len(key_settled) > 0:
            correct_percentage = len(sub_settled.intersection(key_settled)) / len(key_settled) * 100
            results["settled_claims"]["details"] = f"{correct_percentage:.1f}% of settled claims correct"
            # Check for automatic failure condition (below 75%)
            if correct_percentage < 75:
                results["automatic_failure"] = True
                results["automatic_failure_reason"] = "Failed to identify at least 75% of settled claims"
    
    # Check pending claims
    sub_pending = set(submission.get("pending_claims", []))
    key_pending = set(answer_key.get("pending_claims", []))
    
    if sub_pending == key_pending:
        results["pending_claims"]["correct"] = True
        results["pending_claims"]["score"] = 8
        results["pending_claims"]["details"] = "All pending claims correct"
    else:
        # Calculate percentage correct for failure condition
        if len(key_pending) > 0:
            correct_percentage = len(sub_pending.intersection(key_pending)) / len(key_pending) * 100
            results["pending_claims"]["details"] = f"{correct_percentage:.1f}% of pending claims correct"
            # Check for automatic failure condition (below 75%)
            if correct_percentage < 75:
                results["automatic_failure"] = True
                results["automatic_failure_reason"] = "Failed to identify at least 75% of pending claims"
    
    # Check denied claims
    sub_denied = set(submission.get("denied_claims", []))
    key_denied = set(answer_key.get("denied_claims", []))
    
    if sub_denied == key_denied:
        results["denied_claims"]["correct"] = True
        results["denied_claims"]["score"] = 6
        results["denied_claims"]["details"] = "All denied claims correct"
    else:
        # Calculate percentage correct for failure condition
        if len(key_denied) > 0:
            correct_percentage = len(sub_denied.intersection(key_denied)) / len(key_denied) * 100
            results["denied_claims"]["details"] = f"{correct_percentage:.1f}% of denied claims correct"
            # Check for automatic failure condition (below 75%)
            if correct_percentage < 75:
                results["automatic_failure"] = True
                results["automatic_failure_reason"] = "Failed to identify at least 75% of denied claims"
    
    return results


def evaluate_exercise2(submission, answer_key):
    """Evaluate Exercise 2: Claim Status Updates and Inventory Maintenance."""
    results = {
        "updated_claims": {
            "correct": False,
            "score": 0,
            "max_score": 6,
            "details": "Incorrect updated claims"
        },
        "followup_claims": {
            "correct": False,
            "score": 0,
            "max_score": 5,
            "details": "Incorrect followup claims"
        },
        "priority1_claims": {
            "correct": False,
            "score": 0,
            "max_score": 5,
            "details": "Incorrect priority1 claims"
        },
        "avg_days_to_resolve": {
            "correct": False,
            "score": 0,
            "max_score": 4,
            "details": "Incorrect average days calculation"
        }
    }
    
    # Check updated claims - must be exact match
    sub_updated = set(submission.get("updated_claims", []))
    key_updated = set(answer_key.get("updated_claims", []))
    
    if sub_updated == key_updated:
        results["updated_claims"]["correct"] = True
        results["updated_claims"]["score"] = 6
        results["updated_claims"]["details"] = "All updated claims correct"
    else:
        results["automatic_failure"] = True
        results["automatic_failure_reason"] = "Failed to identify all three claims that should be updated to 'Closed' status"
    
    # Check followup claims - need at least 80% correct
    sub_followup = set(submission.get("followup_claims", []))
    key_followup = set(answer_key.get("followup_claims", []))
    
    if key_followup:
        correct_percentage = len(sub_followup.intersection(key_followup)) / len(key_followup) * 100
        results["followup_claims"]["details"] = f"{correct_percentage:.1f}% of followup claims correct"
        
        if correct_percentage >= 80:
            results["followup_claims"]["score"] = 5
            if correct_percentage == 100:
                results["followup_claims"]["correct"] = True
                results["followup_claims"]["details"] = "All followup claims correct"
        else:
            results["followup_claims"]["score"] = int((correct_percentage / 80) * 5)
    
    # Check priority1 claims - need at least 90% correct
    sub_priority = set(submission.get("priority1_claims", []))
    key_priority = set(answer_key.get("priority1_claims", []))
    
    if key_priority:
        correct_percentage = len(sub_priority.intersection(key_priority)) / len(key_priority) * 100
        results["priority1_claims"]["details"] = f"{correct_percentage:.1f}% of priority1 claims correct"
        
        if correct_percentage >= 90:
            results["priority1_claims"]["score"] = 5
            if correct_percentage == 100:
                results["priority1_claims"]["correct"] = True
                results["priority1_claims"]["details"] = "All priority1 claims correct"
        else:
            results["priority1_claims"]["score"] = int((correct_percentage / 90) * 5)
    
    # Check average days calculation - within ±5 days
    sub_avg_days = submission.get("avg_days_to_resolve", 0)
    key_avg_days = answer_key.get("avg_days_to_resolve", 0)
    
    if isinstance(sub_avg_days, (int, float)) and isinstance(key_avg_days, (int, float)):
        difference = abs(sub_avg_days - key_avg_days)
        results["avg_days_to_resolve"]["details"] = f"Submitted {sub_avg_days}, expected {key_avg_days}, difference of {difference} days"
        
        if difference <= 5:
            results["avg_days_to_resolve"]["score"] = 4
            if difference == 0:
                results["avg_days_to_resolve"]["correct"] = True
                results["avg_days_to_resolve"]["details"] = "Correct average days calculation"
            else:
                results["avg_days_to_resolve"]["details"] = f"Within acceptable range (±5 days)"
    
    return results


def evaluate_exercise3(submission, answer_key):
    """Evaluate Exercise 3: Claims Requiring Detailed Analysis."""
    results = {
        "high_complexity_claims": {
            "correct": False,
            "score": 0,
            "max_score": 4,
            "details": "Incorrect high complexity claims"
        },
        "total_financial_exposure": {
            "correct": False,
            "score": 0,
            "max_score": 3,
            "details": "Incorrect financial exposure calculation"
        },
        "highest_severity": {
            "correct": False,
            "score": 0,
            "max_score": 3,
            "details": "Incorrect severity code"
        }
    }
    
    # Check high complexity claims - need at least 90% correct
    sub_complexity = set(submission.get("high_complexity_claims", []))
    key_complexity = set(answer_key.get("high_complexity_claims", []))
    
    if key_complexity:
        correct_percentage = len(sub_complexity.intersection(key_complexity)) / len(key_complexity) * 100
        results["high_complexity_claims"]["details"] = f"{correct_percentage:.1f}% of high complexity claims correct"
        
        if correct_percentage >= 90:
            results["high_complexity_claims"]["score"] = 4
            if correct_percentage == 100:
                results["high_complexity_claims"]["correct"] = True
                results["high_complexity_claims"]["details"] = "All high complexity claims correct"
        else:
            results["high_complexity_claims"]["score"] = int((correct_percentage / 90) * 4)
    
    # Check financial exposure - within ±$5,000
    sub_exposure = submission.get("total_financial_exposure", 0)
    key_exposure = answer_key.get("total_financial_exposure", 0)
    
    if isinstance(sub_exposure, (int, float)) and isinstance(key_exposure, (int, float)):
        difference = abs(sub_exposure - key_exposure)
        results["total_financial_exposure"]["details"] = f"Submitted {sub_exposure}, expected {key_exposure}, difference of ${difference:,}"
        
        if difference <= 5000:
            results["total_financial_exposure"]["score"] = 3
            if difference == 0:
                results["total_financial_exposure"]["correct"] = True
                results["total_financial_exposure"]["details"] = "Correct financial exposure calculation"
            else:
                results["total_financial_exposure"]["details"] = f"Within acceptable range (±$5,000)"
    
    # Check highest severity - must be exact
    sub_severity = submission.get("highest_severity", "")
    key_severity = answer_key.get("highest_severity", "")
    
    if sub_severity == key_severity:
        results["highest_severity"]["correct"] = True
        results["highest_severity"]["score"] = 3
        results["highest_severity"]["details"] = "Correct severity code"
    else:
        results["automatic_failure"] = True
        results["automatic_failure_reason"] = "Failed to correctly identify the highest severity code"
    
    return results


def calculate_overall_score(results):
    """Calculate the overall score as a percentage."""
    total_score = 0
    total_possible = 0
    
    # Exercise 1
    for category in results["exercise1"]:
        if category not in ["automatic_failure", "automatic_failure_reason"]:
            total_score += results["exercise1"][category]["score"]
            total_possible += results["exercise1"][category]["max_score"]
    
    # Exercise 2
    for category in results["exercise2"]:
        if category not in ["automatic_failure", "automatic_failure_reason"]:
            total_score += results["exercise2"][category]["score"]
            total_possible += results["exercise2"][category]["max_score"]
    
    # Exercise 3
    for category in results["exercise3"]:
        if category not in ["automatic_failure", "automatic_failure_reason"]:
            total_score += results["exercise3"][category]["score"]
            total_possible += results["exercise3"][category]["max_score"]
    
    # Calculate percentage
    if total_possible > 0:
        return (total_score / total_possible) * 100
    else:
        return 0


def evaluate_submission(submission_file, answer_key_file):
    """Evaluate a candidate's submission against the answer key."""
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Check if the submission is valid JSON
    if not isinstance(submission, dict):
        return {
            "automatic_failure": True,
            "automatic_failure_reason": "Submission is not a valid JSON object",
            "overall_score": 0
        }
    
    # Extract exercises from submission and answer key
    sub_ex1 = submission.get("exercise1", {})
    sub_ex2 = submission.get("exercise2", {})
    sub_ex3 = submission.get("exercise3", {})
    
    key_ex1 = answer_key.get("exercise1", {})
    key_ex2 = answer_key.get("exercise2", {})
    key_ex3 = answer_key.get("exercise3", {})
    
    # Evaluate each exercise
    results = {
        "exercise1": evaluate_exercise1(sub_ex1, key_ex1),
        "exercise2": evaluate_exercise2(sub_ex2, key_ex2),
        "exercise3": evaluate_exercise3(sub_ex3, key_ex3)
    }
    
    # Check for automatic failure conditions
    automatic_failure = False
    failure_reasons = []
    
    for exercise in ["exercise1", "exercise2", "exercise3"]:
        if "automatic_failure" in results[exercise]:
            automatic_failure = True
            failure_reasons.append(results[exercise]["automatic_failure_reason"])
    
    if automatic_failure:
        results["automatic_failure"] = True
        results["automatic_failure_reason"] = "; ".join(failure_reasons)
        results["overall_score"] = 0
        results["pass"] = False
    else:
        # Calculate overall score
        overall_score = calculate_overall_score(results)
        results["overall_score"] = round(overall_score, 2)
        
        # Determine if candidate passed (needs 80% or higher)
        results["pass"] = overall_score >= 80
    
    return results


def main():
    """Main function to parse arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Evaluate submission
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Pass: {results['pass']}")


if __name__ == "__main__":
    main()