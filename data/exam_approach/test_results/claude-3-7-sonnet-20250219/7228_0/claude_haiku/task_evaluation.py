#!/usr/bin/env python3
"""
Property Management Financial Competency Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Property Management Financial Competency Exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, Any, List, Tuple


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Annual Operating Budget Creation."""
    task1_sub = submission.get("task1", {}).get("annual_budget", {})
    task1_key = answer_key.get("task1", {}).get("annual_budget", {})
    
    results = {
        "total_points": 6,
        "points_earned": 0,
        "details": {}
    }
    
    # Evaluate main budget values
    for field in ["total_income", "total_expenses", "net_operating_income"]:
        sub_value = task1_sub.get(field, 0)
        key_value = task1_key.get(field, 0)
        
        # Check if within 3% margin of error
        if key_value == 0:
            is_correct = sub_value == 0
        else:
            error_margin = abs((sub_value - key_value) / key_value)
            is_correct = error_margin <= 0.03
        
        results["details"][field] = {
            "submitted": sub_value,
            "correct": key_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            results["points_earned"] += 1
    
    # Evaluate expense categories
    sub_categories = task1_sub.get("expense_categories", {})
    key_categories = task1_key.get("expense_categories", {})
    
    for category in ["utilities", "maintenance", "administrative", "taxes_insurance"]:
        sub_value = sub_categories.get(category, 0)
        key_value = key_categories.get(category, 0)
        
        # Check if within 3% margin of error
        if key_value == 0:
            is_correct = sub_value == 0
        else:
            error_margin = abs((sub_value - key_value) / key_value)
            is_correct = error_margin <= 0.03
        
        results["details"][f"expense_{category}"] = {
            "submitted": sub_value,
            "correct": key_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            results["points_earned"] += 1
    
    # Check if task1 passes the requirements (at least 4 out of 6 correct)
    results["passes_requirements"] = results["points_earned"] >= 4
    
    return results


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Financial Variance Analysis."""
    task2_sub = submission.get("task2", {}).get("variance_analysis", {})
    task2_key = answer_key.get("task2", {}).get("variance_analysis", {})
    
    results = {
        "total_points": 4,
        "points_earned": 0,
        "details": {}
    }
    
    # Evaluate category name (must match exactly)
    category_field = "largest_variance_category"
    sub_category = task2_sub.get(category_field, "")
    key_category = task2_key.get(category_field, "")
    is_category_correct = sub_category == key_category
    
    results["details"][category_field] = {
        "submitted": sub_category,
        "correct": key_category,
        "is_correct": is_category_correct
    }
    
    if is_category_correct:
        results["points_earned"] += 1
    
    # Evaluate numeric values
    for field in ["largest_variance_amount", "utility_expense_variance"]:
        sub_value = task2_sub.get(field, 0)
        key_value = task2_key.get(field, 0)
        
        # For monetary values, check if within 3% margin of error
        if key_value == 0:
            is_correct = sub_value == 0
        else:
            error_margin = abs((sub_value - key_value) / key_value)
            is_correct = error_margin <= 0.03
        
        results["details"][field] = {
            "submitted": sub_value,
            "correct": key_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            results["points_earned"] += 1
    
    # Evaluate percentage (within 0.2 percentage points)
    field = "total_expense_variance_percentage"
    sub_value = task2_sub.get(field, 0)
    key_value = task2_key.get(field, 0)
    is_correct = abs(sub_value - key_value) <= 0.2
    
    results["details"][field] = {
        "submitted": sub_value,
        "correct": key_value,
        "is_correct": is_correct
    }
    
    if is_correct:
        results["points_earned"] += 1
    
    # Check if task2 passes the requirements (at least 3 out of 4 correct, including category)
    results["passes_requirements"] = (results["points_earned"] >= 3 and 
                                     results["details"]["largest_variance_category"]["is_correct"])
    
    return results


def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Financial Report Preparation."""
    task3_sub = submission.get("task3", {}).get("financial_summary", {})
    task3_key = answer_key.get("task3", {}).get("financial_summary", {})
    
    results = {
        "total_points": 4,
        "points_earned": 0,
        "details": {}
    }
    
    # Evaluate percentage (within 0.2 percentage points)
    field = "operating_expense_ratio"
    sub_value = task3_sub.get(field, 0)
    key_value = task3_key.get(field, 0)
    is_correct = abs(sub_value - key_value) <= 0.2
    
    results["details"][field] = {
        "submitted": sub_value,
        "correct": key_value,
        "is_correct": is_correct
    }
    
    if is_correct:
        results["points_earned"] += 1
    
    # Evaluate expense per square foot (within 5% margin of error)
    field = "expense_per_square_foot"
    sub_value = task3_sub.get(field, 0)
    key_value = task3_key.get(field, 0)
    
    if key_value == 0:
        is_correct = sub_value == 0
    else:
        error_margin = abs((sub_value - key_value) / key_value)
        is_correct = error_margin <= 0.05
    
    results["details"][field] = {
        "submitted": sub_value,
        "correct": key_value,
        "is_correct": is_correct
    }
    
    if is_correct:
        results["points_earned"] += 1
    
    # Evaluate monetary values (within 5% margin of error)
    for field in ["income_per_unit", "maintenance_reserve_allocation"]:
        sub_value = task3_sub.get(field, 0)
        key_value = task3_key.get(field, 0)
        
        if key_value == 0:
            is_correct = sub_value == 0
        else:
            error_margin = abs((sub_value - key_value) / key_value)
            is_correct = error_margin <= 0.05
        
        results["details"][field] = {
            "submitted": sub_value,
            "correct": key_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            results["points_earned"] += 1
    
    # Check if task3 passes the requirements (at least 3 out of 4 correct)
    results["passes_requirements"] = results["points_earned"] >= 3
    
    return results


def check_critical_elements(task_results: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    """Check if critical elements are correct."""
    critical_elements = {
        "net_operating_income": task_results["task1"]["details"]["net_operating_income"]["is_correct"],
        "total_income": task_results["task1"]["details"]["total_income"]["is_correct"],
        "total_expenses": task_results["task1"]["details"]["total_expenses"]["is_correct"],
        "operating_expense_ratio": task_results["task3"]["details"]["operating_expense_ratio"]["is_correct"]
    }
    
    return critical_elements


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Combine results
    task_results = {
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    }
    
    # Check critical elements
    critical_elements = check_critical_elements(task_results)
    all_critical_correct = all(critical_elements.values())
    
    # Calculate overall score
    total_points = sum(task["total_points"] for task in task_results.values())
    points_earned = sum(task["points_earned"] for task in task_results.values())
    overall_score = (points_earned / total_points) * 100
    
    # Determine if candidate passes
    passes_exam = (
        overall_score >= 80 and
        all_critical_correct and
        task1_results["passes_requirements"] and
        task2_results["passes_requirements"] and
        task3_results["passes_requirements"]
    )
    
    # Compile final results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 1),
        "passes_exam": passes_exam,
        "total_points": total_points,
        "points_earned": points_earned,
        "critical_elements": critical_elements,
        "all_critical_elements_correct": all_critical_correct,
        "task_results": task_results
    }
    
    return results


def main():
    """Main function to run the evaluation."""
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
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Candidate {'PASSED' if results['passes_exam'] else 'FAILED'} the exam.")


if __name__ == "__main__":
    main()