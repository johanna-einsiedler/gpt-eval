#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Tuple
import math

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_discrepancies(submission: List[Dict], answer_key: List[Dict]) -> Tuple[int, List[Dict]]:
    """Evaluate the discrepancies identified in Exercise 1."""
    score = 0
    max_score = 20
    points_per_item = 5
    feedback = []
    
    # Create dictionaries for easier comparison
    submission_dict = {item["account"]: item for item in submission}
    answer_key_dict = {item["account"]: item for item in answer_key}
    
    # Check each discrepancy in the answer key
    for account, key_item in answer_key_dict.items():
        if account in submission_dict:
            sub_item = submission_dict[account]
            reported_correct = sub_item["reported_value"] == key_item["reported_value"]
            actual_correct = sub_item["correct_value"] == key_item["correct_value"]
            
            if reported_correct and actual_correct:
                score += points_per_item
                feedback.append({
                    "account": account,
                    "status": "correct",
                    "points": points_per_item
                })
            else:
                feedback.append({
                    "account": account,
                    "status": "incorrect",
                    "points": 0,
                    "expected": key_item,
                    "submitted": sub_item
                })
        else:
            feedback.append({
                "account": account,
                "status": "missing",
                "points": 0
            })
    
    # Check for any extra discrepancies reported by the candidate
    for account in submission_dict:
        if account not in answer_key_dict:
            feedback.append({
                "account": account,
                "status": "extra",
                "points": 0,
                "submitted": submission_dict[account]
            })
    
    return score, feedback

def evaluate_numeric_value(submitted: float, expected: float, tolerance: float, max_points: int) -> Tuple[int, Dict]:
    """Evaluate a numeric value with a tolerance."""
    if submitted == expected:
        return max_points, {"status": "correct", "points": max_points}
    
    # Calculate percentage difference
    percent_diff = abs(submitted - expected) / expected if expected != 0 else float('inf')
    
    if percent_diff <= tolerance:
        # Partial credit for close answers
        points = math.ceil(max_points / 2)
        return points, {
            "status": "partial",
            "points": points,
            "expected": expected,
            "submitted": submitted,
            "percent_diff": percent_diff
        }
    else:
        return 0, {
            "status": "incorrect",
            "points": 0,
            "expected": expected,
            "submitted": submitted,
            "percent_diff": percent_diff
        }

def evaluate_misclassified_items(submission: List[Dict], answer_key: List[Dict]) -> Tuple[int, List[Dict]]:
    """Evaluate the misclassified items identified in Exercise 2."""
    score = 0
    max_score = 20
    points_per_item = 5
    feedback = []
    
    # Create a set of tuples for easier comparison
    submission_set = {(item["account"], item["amount"], item["correct_category"]) for item in submission}
    answer_key_set = {(item["account"], item["amount"], item["correct_category"]) for item in answer_key}
    
    # Check each item in the answer key
    for key_item in answer_key:
        key_tuple = (key_item["account"], key_item["amount"], key_item["correct_category"])
        if key_tuple in submission_set:
            score += points_per_item
            feedback.append({
                "item": key_item,
                "status": "correct",
                "points": points_per_item
            })
        else:
            # Check if account and amount match but category is wrong
            partial_matches = [s for s in submission if 
                              s["account"] == key_item["account"] and 
                              s["amount"] == key_item["amount"]]
            
            if partial_matches:
                feedback.append({
                    "item": key_item,
                    "status": "partial",
                    "points": 0,
                    "submitted": partial_matches[0]
                })
            else:
                feedback.append({
                    "item": key_item,
                    "status": "missing",
                    "points": 0
                })
    
    # Check for any extra items reported by the candidate
    for sub_item in submission:
        sub_tuple = (sub_item["account"], sub_item["amount"], sub_item["correct_category"])
        if sub_tuple not in answer_key_set:
            feedback.append({
                "item": sub_item,
                "status": "extra",
                "points": 0
            })
    
    return score, feedback

def evaluate_missing_documents(submission: List[str], answer_key: List[str]) -> Tuple[int, List[Dict]]:
    """Evaluate the missing documents identified in Exercise 3."""
    score = 0
    max_score = 10
    points_per_item = 5
    feedback = []
    
    # Convert to sets for easier comparison
    submission_set = set(submission)
    answer_key_set = set(answer_key)
    
    # Check each document in the answer key
    for document in answer_key_set:
        if document in submission_set:
            score += points_per_item
            feedback.append({
                "document": document,
                "status": "correct",
                "points": points_per_item
            })
        else:
            feedback.append({
                "document": document,
                "status": "missing",
                "points": 0
            })
    
    # Check for any extra documents reported by the candidate
    for document in submission_set:
        if document not in answer_key_set:
            feedback.append({
                "document": document,
                "status": "extra",
                "points": 0
            })
    
    return score, feedback

def evaluate_compliance_issues(submission: List[Dict], answer_key: List[Dict]) -> Tuple[int, List[Dict]]:
    """Evaluate the compliance issues identified in Exercise 3."""
    score = 0
    max_score = 10
    points_per_item = max_score / len(answer_key)
    feedback = []
    
    # Create a set of issue IDs for easier comparison
    submission_ids = {item["issue_id"] for item in submission}
    answer_key_ids = {item["issue_id"] for item in answer_key}
    
    # Check each issue in the answer key
    for key_item in answer_key:
        if key_item["issue_id"] in submission_ids:
            # Find the submitted item with this ID
            sub_item = next(item for item in submission if item["issue_id"] == key_item["issue_id"])
            
            if sub_item["description"] == key_item["description"]:
                score += points_per_item
                feedback.append({
                    "issue_id": key_item["issue_id"],
                    "status": "correct",
                    "points": points_per_item
                })
            else:
                feedback.append({
                    "issue_id": key_item["issue_id"],
                    "status": "partial",
                    "points": 0,
                    "expected": key_item["description"],
                    "submitted": sub_item["description"]
                })
        else:
            feedback.append({
                "issue_id": key_item["issue_id"],
                "status": "missing",
                "points": 0,
                "expected": key_item
            })
    
    # Check for any extra issues reported by the candidate
    for sub_item in submission:
        if sub_item["issue_id"] not in answer_key_ids:
            feedback.append({
                "issue_id": sub_item["issue_id"],
                "status": "extra",
                "points": 0,
                "submitted": sub_item
            })
    
    return score, feedback

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "exercise1": {
            "max_points": 35,
            "points": 0,
            "details": {}
        },
        "exercise2": {
            "max_points": 35,
            "points": 0,
            "details": {}
        },
        "exercise3": {
            "max_points": 30,
            "points": 0,
            "details": {}
        },
        "overall_score": 0
    }
    
    # Exercise 1: Balance Sheet Analysis
    # Evaluate discrepancies (20 points)
    discrepancy_score, discrepancy_feedback = evaluate_discrepancies(
        submission["exercise1"]["discrepancies"],
        answer_key["exercise1"]["discrepancies"]
    )
    results["exercise1"]["details"]["discrepancies"] = {
        "score": discrepancy_score,
        "max_score": 20,
        "feedback": discrepancy_feedback
    }
    results["exercise1"]["points"] += discrepancy_score
    
    # Evaluate total assets difference (7 points)
    assets_diff_score, assets_diff_feedback = evaluate_numeric_value(
        submission["exercise1"]["total_assets_difference"],
        answer_key["exercise1"]["total_assets_difference"],
        0.05,  # 5% tolerance
        7
    )
    results["exercise1"]["details"]["total_assets_difference"] = {
        "score": assets_diff_score,
        "max_score": 7,
        "feedback": assets_diff_feedback
    }
    results["exercise1"]["points"] += assets_diff_score
    
    # Evaluate liquidity ratio (8 points)
    liquidity_score, liquidity_feedback = evaluate_numeric_value(
        submission["exercise1"]["liquidity_ratio"],
        answer_key["exercise1"]["liquidity_ratio"],
        0.05,  # 5% tolerance
        8
    )
    results["exercise1"]["details"]["liquidity_ratio"] = {
        "score": liquidity_score,
        "max_score": 8,
        "feedback": liquidity_feedback
    }
    results["exercise1"]["points"] += liquidity_score
    
    # Exercise 2: Income Statement Review
    # Evaluate misclassified items (20 points)
    misclass_score, misclass_feedback = evaluate_misclassified_items(
        submission["exercise2"]["misclassified_items"],
        answer_key["exercise2"]["misclassified_items"]
    )
    results["exercise2"]["details"]["misclassified_items"] = {
        "score": misclass_score,
        "max_score": 20,
        "feedback": misclass_feedback
    }
    results["exercise2"]["points"] += misclass_score
    
    # Evaluate adjusted net income (7 points)
    net_income_score, net_income_feedback = evaluate_numeric_value(
        submission["exercise2"]["adjusted_net_income"],
        answer_key["exercise2"]["adjusted_net_income"],
        0.05,  # 5% tolerance
        7
    )
    results["exercise2"]["details"]["adjusted_net_income"] = {
        "score": net_income_score,
        "max_score": 7,
        "feedback": net_income_feedback
    }
    results["exercise2"]["points"] += net_income_score
    
    # Evaluate expense ratio (8 points)
    expense_ratio_score, expense_ratio_feedback = evaluate_numeric_value(
        submission["exercise2"]["expense_ratio"],
        answer_key["exercise2"]["expense_ratio"],
        0.05,  # 5% tolerance
        8
    )
    results["exercise2"]["details"]["expense_ratio"] = {
        "score": expense_ratio_score,
        "max_score": 8,
        "feedback": expense_ratio_feedback
    }
    results["exercise2"]["points"] += expense_ratio_score
    
    # Exercise 3: Loan Documentation Examination
    # Evaluate loan-to-value ratio (10 points)
    ltv_score, ltv_feedback = evaluate_numeric_value(
        submission["exercise3"]["loan_to_value_ratio"],
        answer_key["exercise3"]["loan_to_value_ratio"],
        0.01,  # 1% tolerance (stricter for this calculation)
        10
    )
    results["exercise3"]["details"]["loan_to_value_ratio"] = {
        "score": ltv_score,
        "max_score": 10,
        "feedback": ltv_feedback
    }
    results["exercise3"]["points"] += ltv_score
    
    # Evaluate missing documents (10 points)
    docs_score, docs_feedback = evaluate_missing_documents(
        submission["exercise3"]["missing_documents"],
        answer_key["exercise3"]["missing_documents"]
    )
    results["exercise3"]["details"]["missing_documents"] = {
        "score": docs_score,
        "max_score": 10,
        "feedback": docs_feedback
    }
    results["exercise3"]["points"] += docs_score
    
    # Evaluate compliance issues (10 points)
    issues_score, issues_feedback = evaluate_compliance_issues(
        submission["exercise3"]["compliance_issues"],
        answer_key["exercise3"]["compliance_issues"]
    )
    results["exercise3"]["details"]["compliance_issues"] = {
        "score": issues_score,
        "max_score": 10,
        "feedback": issues_feedback
    }
    results["exercise3"]["points"] += issues_score
    
    # Calculate overall score
    total_points = (
        results["exercise1"]["points"] +
        results["exercise2"]["points"] +
        results["exercise3"]["points"]
    )
    total_max_points = (
        results["exercise1"]["max_points"] +
        results["exercise2"]["max_points"] +
        results["exercise3"]["max_points"]
    )
    results["overall_score"] = round((total_points / total_max_points) * 100, 2)
    
    # Determine if the candidate passed based on criteria
    exercise1_passed = (
        results["exercise1"]["details"]["discrepancies"]["score"] >= 15 and  # At least 3 of 4 discrepancies
        results["exercise1"]["details"]["total_assets_difference"]["feedback"]["status"] != "incorrect" and
        results["exercise1"]["details"]["liquidity_ratio"]["feedback"]["status"] != "incorrect"
    )
    
    exercise2_passed = (
        results["exercise2"]["details"]["misclassified_items"]["score"] >= 15 and  # At least 3 of 4 items
        results["exercise2"]["details"]["adjusted_net_income"]["feedback"]["status"] != "incorrect" and
        results["exercise2"]["details"]["expense_ratio"]["feedback"]["status"] != "incorrect"
    )
    
    exercise3_passed = (
        results["exercise3"]["details"]["loan_to_value_ratio"]["feedback"]["status"] != "incorrect" and
        results["exercise3"]["details"]["missing_documents"]["score"] >= 5 and  # At least 1 of 2 documents
        issues_score >= 6  # At least 2 of 3 compliance issues
    )
    
    exercises_passed = sum([exercise1_passed, exercise2_passed, exercise3_passed])
    results["passed"] = exercises_passed >= 2 and results["overall_score"] >= 70
    
    # Add candidate ID if provided
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
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
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()