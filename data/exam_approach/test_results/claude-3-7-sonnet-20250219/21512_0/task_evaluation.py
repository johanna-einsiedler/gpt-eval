#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any, List, Union

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_exercise1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 1: Cash Count Reconciliation."""
    result = {"points_earned": 0, "points_possible": 20, "details": {}}
    
    fields = ["cashCountTotal", "ledgerBalance", "discrepancyAmount", "discrepancyType"]
    points_per_field = 5
    
    for field in fields:
        is_correct = submission["exercise1"][field] == answer_key["exercise1"][field]
        result["details"][field] = {
            "is_correct": is_correct,
            "submitted_value": submission["exercise1"][field],
            "correct_value": answer_key["exercise1"][field],
            "points_earned": points_per_field if is_correct else 0,
            "points_possible": points_per_field
        }
        if is_correct:
            result["points_earned"] += points_per_field
    
    return result

def evaluate_exercise2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 2: Notes Verification."""
    result = {"points_earned": 0, "points_possible": 20, "details": {}}
    
    notes = ["note1", "note2"]
    points_per_note = 10
    
    for note in notes:
        note_result = {"points_earned": 0, "points_possible": points_per_note, "fields": {}}
        fields = ["isCorrectlyRecorded", "discrepancyField", "correctValue"]
        points_per_field = points_per_note / len(fields)
        
        for field in fields:
            is_correct = submission["exercise2"][note][field] == answer_key["exercise2"][note][field]
            note_result["fields"][field] = {
                "is_correct": is_correct,
                "submitted_value": submission["exercise2"][note][field],
                "correct_value": answer_key["exercise2"][note][field],
                "points_earned": points_per_field if is_correct else 0,
                "points_possible": points_per_field
            }
            if is_correct:
                note_result["points_earned"] += points_per_field
        
        result["details"][note] = note_result
        result["points_earned"] += note_result["points_earned"]
    
    return result

def evaluate_exercise3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 3: Securities Authentication."""
    result = {"points_earned": 0, "points_possible": 20, "details": {}}
    
    securities = ["security1", "security2"]
    points_per_security = 10
    
    for security in securities:
        security_result = {"points_earned": 0, "points_possible": points_per_security, "fields": {}}
        fields = ["isAuthentic", "isCorrectlyValued", "correctBookValue"]
        points_per_field = points_per_security / len(fields)
        
        for field in fields:
            is_correct = submission["exercise3"][security][field] == answer_key["exercise3"][security][field]
            security_result["fields"][field] = {
                "is_correct": is_correct,
                "submitted_value": submission["exercise3"][security][field],
                "correct_value": answer_key["exercise3"][security][field],
                "points_earned": points_per_field if is_correct else 0,
                "points_possible": points_per_field
            }
            if is_correct:
                security_result["points_earned"] += points_per_field
        
        result["details"][security] = security_result
        result["points_earned"] += security_result["points_earned"]
    
    return result

def evaluate_exercise4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 4: Canceled Check Analysis."""
    result = {"points_earned": 0, "points_possible": 20, "details": {}}
    
    checks = ["check1", "check2"]
    points_per_check = 10
    
    for check in checks:
        check_result = {"points_earned": 0, "points_possible": points_per_check, "fields": {}}
        fields = ["isProperlyEndorsed", "isProperlyAuthorized", "isCorrectlyRecorded", "discrepancyType"]
        points_per_field = points_per_check / len(fields)
        
        for field in fields:
            is_correct = submission["exercise4"][check][field] == answer_key["exercise4"][check][field]
            check_result["fields"][field] = {
                "is_correct": is_correct,
                "submitted_value": submission["exercise4"][check][field],
                "correct_value": answer_key["exercise4"][check][field],
                "points_earned": points_per_field if is_correct else 0,
                "points_possible": points_per_field
            }
            if is_correct:
                check_result["points_earned"] += points_per_field
        
        result["details"][check] = check_result
        result["points_earned"] += check_result["points_earned"]
    
    return result

def evaluate_exercise5(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 5: Comprehensive Case."""
    result = {"points_earned": 0, "points_possible": 20, "details": {}}
    
    fields = ["totalDiscrepancyAmount", "adjustmentRequired", "fraudIndicatorsPresent"]
    points_per_field = 5
    
    for field in fields:
        is_correct = submission["exercise5"][field] == answer_key["exercise5"][field]
        result["details"][field] = {
            "is_correct": is_correct,
            "submitted_value": submission["exercise5"][field],
            "correct_value": answer_key["exercise5"][field],
            "points_earned": points_per_field if is_correct else 0,
            "points_possible": points_per_field
        }
        if is_correct:
            result["points_earned"] += points_per_field
    
    # Special handling for affectedAccounts array
    field = "affectedAccounts"
    submitted_accounts = set(submission["exercise5"][field])
    correct_accounts = set(answer_key["exercise5"][field])
    
    is_correct = submitted_accounts == correct_accounts
    result["details"][field] = {
        "is_correct": is_correct,
        "submitted_value": submission["exercise5"][field],
        "correct_value": answer_key["exercise5"][field],
        "points_earned": points_per_field if is_correct else 0,
        "points_possible": points_per_field
    }
    if is_correct:
        result["points_earned"] += points_per_field
    
    return result

def check_critical_elements(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Check if candidate correctly identified critical elements."""
    critical_elements = {
        "cash_count_discrepancy": submission["exercise1"]["discrepancyType"] == answer_key["exercise1"]["discrepancyType"],
        "note_discrepancy": (
            submission["exercise2"]["note1"]["isCorrectlyRecorded"] == answer_key["exercise2"]["note1"]["isCorrectlyRecorded"] or
            submission["exercise2"]["note2"]["isCorrectlyRecorded"] == answer_key["exercise2"]["note2"]["isCorrectlyRecorded"]
        ),
        "check_amount_discrepancy": (
            submission["exercise4"]["check2"]["isCorrectlyRecorded"] == answer_key["exercise4"]["check2"]["isCorrectlyRecorded"] and
            submission["exercise4"]["check2"]["discrepancyType"] == answer_key["exercise4"]["check2"]["discrepancyType"]
        ),
        "fraud_indicators": submission["exercise5"]["fraudIndicatorsPresent"] == answer_key["exercise5"]["fraudIndicatorsPresent"]
    }
    
    # Count authentication/valuation errors in Exercise 3
    auth_val_errors = 0
    for security in ["security1", "security2"]:
        for field in ["isAuthentic", "isCorrectlyValued"]:
            if submission["exercise3"][security][field] != answer_key["exercise3"][security][field]:
                auth_val_errors += 1
    
    critical_elements["excessive_auth_val_errors"] = auth_val_errors <= 2
    
    # Check automatic failure conditions
    automatic_failure = (
        not critical_elements["check_amount_discrepancy"] or
        not critical_elements["fraud_indicators"] or
        not critical_elements["excessive_auth_val_errors"]
    )
    
    return {
        "critical_elements": critical_elements,
        "automatic_failure": automatic_failure
    }

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "exercise1": evaluate_exercise1(submission, answer_key),
        "exercise2": evaluate_exercise2(submission, answer_key),
        "exercise3": evaluate_exercise3(submission, answer_key),
        "exercise4": evaluate_exercise4(submission, answer_key),
        "exercise5": evaluate_exercise5(submission, answer_key)
    }
    
    # Calculate total points
    total_points_earned = sum(results[ex]["points_earned"] for ex in results)
    total_points_possible = sum(results[ex]["points_possible"] for ex in results)
    overall_score = (total_points_earned / total_points_possible) * 100
    
    # Check critical elements
    critical_check = check_critical_elements(submission, answer_key)
    
    # Determine if candidate passed
    passed = overall_score >= 80 and not critical_check["automatic_failure"]
    
    return {
        "candidate_id": submission.get("candidateId", "Unknown"),
        "results": results,
        "critical_elements": critical_check["critical_elements"],
        "automatic_failure": critical_check["automatic_failure"],
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "overall_score": overall_score,
        "passed": passed
    }

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {evaluation_results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if evaluation_results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()