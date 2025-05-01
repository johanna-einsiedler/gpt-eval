#!/usr/bin/env python3
"""
Task Evaluation Script for Online Merchant Financial Calculation Exam

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any, List, Tuple


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def compare_values(candidate_value: Any, key_value: Any, field_name: str) -> Tuple[bool, str]:
    """Compare candidate's value with the answer key value."""
    # For string comparisons (like product names)
    if isinstance(key_value, str):
        is_correct = candidate_value == key_value
        message = f"{field_name}: {'Correct' if is_correct else f'Incorrect - Expected {key_value}, got {candidate_value}'}"
        return is_correct, message
    
    # For numeric comparisons, allow small rounding differences
    elif isinstance(key_value, (int, float)):
        # For integers (like units sold)
        if isinstance(key_value, int):
            is_correct = candidate_value == key_value
        # For floats (like monetary values and percentages), allow small rounding differences
        else:
            is_correct = math.isclose(candidate_value, key_value, abs_tol=0.01)
        
        message = f"{field_name}: {'Correct' if is_correct else f'Incorrect - Expected {key_value}, got {candidate_value}'}"
        return is_correct, message
    
    # For nested dictionaries (like expense categories)
    elif isinstance(key_value, dict):
        # This will be handled separately in evaluate_task2
        return True, f"{field_name}: Nested structure, evaluated separately"
    
    # Fallback for other types
    else:
        is_correct = candidate_value == key_value
        message = f"{field_name}: {'Correct' if is_correct else f'Incorrect - Expected {key_value}, got {candidate_value}'}"
        return is_correct, message


def evaluate_task1(candidate: Dict[str, Any], key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Sales Analysis."""
    results = {
        "score": 0,
        "max_score": 25,
        "percentage": 0,
        "details": []
    }
    
    fields = [
        ("total_revenue", "Total Revenue"),
        ("total_units_sold", "Total Units Sold"),
        ("average_order_value", "Average Order Value"),
        ("best_selling_product", "Best Selling Product")
    ]
    
    correct_count = 0
    points_per_field = 6.25  # 25% total / 4 fields
    
    for field_key, field_name in fields:
        is_correct, message = compare_values(
            candidate["task1"][field_key], 
            key["task1"][field_key],
            field_name
        )
        
        results["details"].append({
            "field": field_key,
            "correct": is_correct,
            "message": message
        })
        
        if is_correct:
            correct_count += 1
    
    results["score"] = correct_count * points_per_field
    results["percentage"] = (correct_count / len(fields)) * 100
    
    return results


def evaluate_task2(candidate: Dict[str, Any], key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Expense Analysis and Profitability."""
    results = {
        "score": 0,
        "max_score": 45,
        "percentage": 0,
        "details": []
    }
    
    # Evaluate expense categories separately
    expense_categories = [
        ("advertising", "Advertising"),
        ("shipping", "Shipping"),
        ("product_costs", "Product Costs"),
        ("platform_fees", "Platform Fees"),
        ("other", "Other")
    ]
    
    correct_count = 0
    category_correct_count = 0
    
    # Check expense categories
    for cat_key, cat_name in expense_categories:
        is_correct, message = compare_values(
            candidate["task2"]["expense_categories"][cat_key],
            key["task2"]["expense_categories"][cat_key],
            f"Expense Category: {cat_name}"
        )
        
        results["details"].append({
            "field": f"expense_categories.{cat_key}",
            "correct": is_correct,
            "message": message
        })
        
        if is_correct:
            category_correct_count += 1
    
    # Other fields in task2
    other_fields = [
        ("total_expenses", "Total Expenses"),
        ("gross_profit", "Gross Profit"),
        ("profit_margin_percentage", "Profit Margin Percentage")
    ]
    
    for field_key, field_name in other_fields:
        is_correct, message = compare_values(
            candidate["task2"][field_key],
            key["task2"][field_key],
            field_name
        )
        
        results["details"].append({
            "field": field_key,
            "correct": is_correct,
            "message": message
        })
        
        if is_correct:
            correct_count += 1
    
    # Calculate score
    # 5 categories (25% of task2 score) + 3 other fields (20% of task2 score)
    category_points = (category_correct_count / len(expense_categories)) * 25
    other_points = (correct_count / len(other_fields)) * 20
    
    results["score"] = category_points + other_points
    results["percentage"] = ((category_correct_count + correct_count) / 
                            (len(expense_categories) + len(other_fields))) * 100
    
    return results


def evaluate_task3(candidate: Dict[str, Any], key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Monthly Financial Summary."""
    results = {
        "score": 0,
        "max_score": 30,
        "percentage": 0,
        "details": []
    }
    
    fields = [
        ("total_revenue", "Monthly Summary: Total Revenue"),
        ("total_expenses", "Monthly Summary: Total Expenses"),
        ("net_profit", "Monthly Summary: Net Profit"),
        ("roi_percentage", "ROI Percentage"),
        ("conversion_rate_percentage", "Conversion Rate Percentage")
    ]
    
    correct_count = 0
    points_per_field = 6  # 30% total / 5 fields
    
    for field_key, field_name in fields:
        is_correct, message = compare_values(
            candidate["task3"]["monthly_summary"][field_key],
            key["task3"]["monthly_summary"][field_key],
            field_name
        )
        
        results["details"].append({
            "field": f"monthly_summary.{field_key}",
            "correct": is_correct,
            "message": message
        })
        
        if is_correct:
            correct_count += 1
    
    results["score"] = correct_count * points_per_field
    results["percentage"] = (correct_count / len(fields)) * 100
    
    return results


def check_critical_errors(candidate: Dict[str, Any], key: Dict[str, Any]) -> List[str]:
    """Check for automatic failure conditions."""
    critical_errors = []
    
    # Check total revenue and expenses (fundamental errors)
    if not math.isclose(candidate["task1"]["total_revenue"], key["task1"]["total_revenue"], abs_tol=0.01):
        critical_errors.append("Incorrect calculation of total revenue (fundamental error)")
    
    if not math.isclose(candidate["task2"]["total_expenses"], key["task2"]["total_expenses"], abs_tol=0.01):
        critical_errors.append("Incorrect calculation of total expenses (fundamental error)")
    
    # Check best-selling product
    if candidate["task1"]["best_selling_product"] != key["task1"]["best_selling_product"]:
        critical_errors.append("Failure to identify the correct best-selling product")
    
    # Check sign for profit values
    if (math.copysign(1, candidate["task2"]["gross_profit"]) != 
        math.copysign(1, key["task2"]["gross_profit"])):
        critical_errors.append("Incorrect sign (positive/negative) for gross profit")
    
    if (math.copysign(1, candidate["task3"]["monthly_summary"]["net_profit"]) != 
        math.copysign(1, key["task3"]["monthly_summary"]["net_profit"])):
        critical_errors.append("Incorrect sign (positive/negative) for net profit")
    
    # Check expense categorization errors
    expense_categories = ["advertising", "shipping", "product_costs", "platform_fees", "other"]
    category_errors = 0
    
    for category in expense_categories:
        if not math.isclose(
            candidate["task2"]["expense_categories"][category],
            key["task2"]["expense_categories"][category],
            abs_tol=0.01
        ):
            category_errors += 1
    
    if category_errors > 2:
        critical_errors.append(f"More than two calculation errors in expense categorization ({category_errors} errors)")
    
    return critical_errors


def evaluate_submission(candidate_path: str, key_path: str) -> Dict[str, Any]:
    """Evaluate the candidate's submission against the answer key."""
    candidate = load_json_file(candidate_path)
    key = load_json_file(key_path)
    
    # Evaluate each task
    task1_results = evaluate_task1(candidate, key)
    task2_results = evaluate_task2(candidate, key)
    task3_results = evaluate_task3(candidate, key)
    
    # Check for critical errors
    critical_errors = check_critical_errors(candidate, key)
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Determine if the candidate passed
    passed = overall_percentage >= 80 and len(critical_errors) == 0
    
    # Compile results
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passed": passed,
        "critical_errors": critical_errors,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results
        }
    }
    
    return results


def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    candidate_path = sys.argv[1]
    key_path = sys.argv[2]
    
    results = evaluate_submission(candidate_path, key_path)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")
    
    if results["critical_errors"]:
        print("\nCritical Errors:")
        for error in results["critical_errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()