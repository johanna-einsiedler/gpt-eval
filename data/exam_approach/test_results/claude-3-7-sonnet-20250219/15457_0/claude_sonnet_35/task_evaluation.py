#!/usr/bin/env python3
"""
Biofuels Production Manager Budget Preparation Exam Evaluator

This script evaluates a candidate's submission against the answer key and generates
a detailed score report.

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


def is_within_tolerance(value: float, target: float, tolerance: float = 0.02) -> bool:
    """Check if a value is within a specified tolerance of the target."""
    if target == 0:
        return value == 0
    return abs((value - target) / target) <= tolerance


def evaluate_quarterly_budget(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the quarterly budget section."""
    max_points = 25
    points = 0
    comments = []
    
    # Check each budget category (5 points each)
    categories = ["raw_materials", "labor", "utilities", "maintenance", "overhead"]
    for category in categories:
        submission_value = submission["quarterly_budget"].get(category, 0)
        key_value = answer_key["quarterly_budget"].get(category, 0)
        
        if is_within_tolerance(submission_value, key_value):
            points += 5
        else:
            comments.append(f"Incorrect {category} budget: {submission_value} (expected {key_value})")
    
    # Check total expenses (5 points)
    submission_total = submission["quarterly_budget"].get("total_expenses", 0)
    key_total = answer_key["quarterly_budget"].get("total_expenses", 0)
    
    # Check if total matches the sum of categories
    submission_sum = sum(submission["quarterly_budget"].get(cat, 0) for cat in categories)
    
    if is_within_tolerance(submission_total, key_total):
        if is_within_tolerance(submission_total, submission_sum):
            points += 5
        else:
            comments.append(f"Total expenses ({submission_total}) doesn't match sum of categories ({submission_sum})")
    else:
        comments.append(f"Incorrect total expenses: {submission_total} (expected {key_total})")
    
    return points, comments


def evaluate_financial_metrics(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the financial metrics section."""
    max_points = 20
    points = 0
    comments = []
    
    metrics = ["projected_revenue", "projected_profit", "profit_margin_percentage", "cost_per_gallon"]
    
    for metric in metrics:
        submission_value = submission["financial_metrics"].get(metric, 0)
        key_value = answer_key["financial_metrics"].get(metric, 0)
        
        if is_within_tolerance(submission_value, key_value):
            points += 5
        else:
            comments.append(f"Incorrect {metric}: {submission_value} (expected {key_value})")
    
    return points, comments


def evaluate_top_expenses(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the top expenses section."""
    max_points = 15
    points = 0
    comments = []
    
    # Convert to a more comparable format
    submission_expenses = {item["category"]: item["percentage"] for item in submission.get("top_expenses", [])}
    key_expenses = {item["category"]: item["percentage"] for item in answer_key.get("top_expenses", [])}
    
    # Check if the right categories are identified (in any order)
    key_categories = set(key_expenses.keys())
    submission_categories = set(submission_expenses.keys())
    
    # Check each of the top 3 expenses
    for i, (key_cat, key_pct) in enumerate(key_expenses.items()):
        # Check if category is in submission's top 3
        if key_cat in submission_categories:
            # Check if percentage is correct
            submission_pct = submission_expenses.get(key_cat, 0)
            if is_within_tolerance(submission_pct, key_pct):
                points += 5
            else:
                comments.append(f"Incorrect percentage for {key_cat}: {submission_pct} (expected {key_pct})")
        else:
            comments.append(f"Missing top expense category: {key_cat}")
    
    # Check if categories are in descending order
    submission_list = submission.get("top_expenses", [])
    if len(submission_list) >= 2:
        is_descending = all(submission_list[i]["percentage"] >= submission_list[i+1]["percentage"] 
                           for i in range(len(submission_list)-1))
        if not is_descending:
            comments.append("Top expenses are not listed in descending order by percentage")
    
    return points, comments


def evaluate_cost_reduction(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the cost reduction section."""
    max_points = 10
    points = 0
    comments = []
    
    fields = ["original_maintenance_cost", "reduced_maintenance_cost", "total_savings"]
    
    # Check all fields together
    all_correct = True
    for field in fields:
        submission_value = submission["cost_reduction"].get(field, 0)
        key_value = answer_key["cost_reduction"].get(field, 0)
        
        if not is_within_tolerance(submission_value, key_value):
            all_correct = False
            comments.append(f"Incorrect {field}: {submission_value} (expected {key_value})")
    
    if all_correct:
        points = max_points
    
    return points, comments


def evaluate_variance_response(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the variance response section."""
    max_points = 20
    points = 0
    comments = []
    
    # Check numerical fields (5 points each)
    numerical_fields = ["new_raw_material_cost", "new_total_expenses", "new_profit_margin_percentage"]
    for field in numerical_fields:
        submission_value = submission["variance_response"].get(field, 0)
        key_value = answer_key["variance_response"].get(field, 0)
        
        if is_within_tolerance(submission_value, key_value):
            points += 5
        else:
            comments.append(f"Incorrect {field}: {submission_value} (expected {key_value})")
    
    # Check mitigation strategy (5 points)
    submission_strategy = submission["variance_response"].get("selected_mitigation_strategy", "")
    key_strategy = answer_key["variance_response"].get("selected_mitigation_strategy", "")
    
    if submission_strategy == key_strategy:
        points += 5
    else:
        comments.append(f"Incorrect mitigation strategy: {submission_strategy} (expected {key_strategy})")
    
    return points, comments


def evaluate_contingency_allocation(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the contingency allocation section."""
    max_points = 10
    points = 0
    comments = []
    
    # Check if all allocations match the answer key
    submission_allocation = submission.get("contingency_allocation", {})
    key_allocation = answer_key.get("contingency_allocation", {})
    
    categories = ["raw_materials", "labor", "utilities", "maintenance", "overhead"]
    
    all_correct = True
    for category in categories:
        submission_value = submission_allocation.get(category, 0)
        key_value = key_allocation.get(category, 0)
        
        if not is_within_tolerance(submission_value, key_value):
            all_correct = False
            comments.append(f"Incorrect {category} allocation: {submission_value} (expected {key_value})")
    
    # Check if total allocation is exactly $75,000
    submission_total = sum(submission_allocation.get(cat, 0) for cat in categories)
    if submission_total != 75000:
        all_correct = False
        comments.append(f"Total contingency allocation is {submission_total}, must be exactly 75000")
    
    if all_correct:
        points = max_points
    
    return points, comments


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the full submission and generate a detailed report."""
    results = {
        "sections": {},
        "overall_score": 0,
        "comments": [],
        "passing_threshold": 75
    }
    
    # Evaluate each section
    sections = [
        ("quarterly_budget", evaluate_quarterly_budget, 25),
        ("financial_metrics", evaluate_financial_metrics, 20),
        ("top_expenses", evaluate_top_expenses, 15),
        ("cost_reduction", evaluate_cost_reduction, 10),
        ("variance_response", evaluate_variance_response, 20),
        ("contingency_allocation", evaluate_contingency_allocation, 10)
    ]
    
    total_points = 0
    max_points = 0
    
    for section_name, evaluation_func, section_max_points in sections:
        points, comments = evaluation_func(submission, answer_key)
        
        results["sections"][section_name] = {
            "points": points,
            "max_points": section_max_points,
            "percentage": round(points / section_max_points * 100, 1),
            "comments": comments
        }
        
        total_points += points
        max_points += section_max_points
        results["comments"].extend(comments)
    
    # Calculate overall score
    results["overall_score"] = round(total_points / max_points * 100, 1)
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    
    return results


def main():
    """Main function to process command line arguments and evaluate the submission."""
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