#!/usr/bin/env python3
"""
Spa Manager Practical Exam Evaluator

This script evaluates a candidate's submission against an answer key for the
Spa Manager practical exam on establishing spa budgets and financial goals.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any, List, Tuple


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def is_within_range(value: float, target: float, tolerance: float) -> bool:
    """Check if a value is within the specified tolerance of the target."""
    return abs(value - target) <= tolerance


def is_within_benchmark(value: float, min_val: float, max_val: float) -> bool:
    """Check if a value is within the benchmark range."""
    return min_val <= value <= max_val


def evaluate_budget_analysis(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the budget analysis section."""
    score = 0
    max_score = 25
    details = {}
    
    # Average monthly revenue calculations (10 points): 2 points for each correct category
    revenue_categories = [
        "massage_services", "facial_services", "body_treatments", 
        "nail_services", "retail_products"
    ]
    revenue_score = 0
    revenue_details = {}
    
    for category in revenue_categories:
        submitted_value = submission["budget_analysis"]["average_monthly_revenue_by_category"].get(category, 0)
        expected_value = answer_key["budget_analysis"]["average_monthly_revenue_by_category"].get(category, 0)
        
        # Tolerance: ±$50 for amounts under $100,000
        tolerance = 50
        
        if is_within_range(submitted_value, expected_value, tolerance):
            revenue_score += 2
            revenue_details[category] = {"points": 2, "submitted": submitted_value, "expected": expected_value}
        else:
            revenue_details[category] = {"points": 0, "submitted": submitted_value, "expected": expected_value}
    
    score += revenue_score
    details["average_monthly_revenue"] = {"score": revenue_score, "max_score": 10, "details": revenue_details}
    
    # Top expense categories identification (9 points): 3 points for each correct category
    submitted_categories = submission["budget_analysis"]["top_expense_categories"]
    expected_categories = answer_key["budget_analysis"]["top_expense_categories"]
    
    category_score = 0
    category_details = {"submitted": submitted_categories, "expected": expected_categories}
    
    for category in submitted_categories:
        if category in expected_categories:
            category_score += 3
    
    score += category_score
    details["top_expense_categories"] = {"score": category_score, "max_score": 9, "details": category_details}
    
    # Previous year profit margin calculation (6 points)
    submitted_margin = submission["budget_analysis"]["previous_year_profit_margin"]
    expected_margin = answer_key["budget_analysis"]["previous_year_profit_margin"]
    
    # Tolerance: ±0.02 (2 percentage points)
    margin_tolerance = 0.02
    
    if is_within_range(submitted_margin, expected_margin, margin_tolerance):
        margin_score = 6
    else:
        margin_score = 0
    
    score += margin_score
    details["previous_year_profit_margin"] = {
        "score": margin_score, 
        "max_score": 6, 
        "details": {"submitted": submitted_margin, "expected": expected_margin}
    }
    
    return score, {"score": score, "max_score": max_score, "details": details}


def evaluate_revenue_projection(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the revenue projection section."""
    score = 0
    max_score = 25
    details = {}
    
    # Projected annual revenue calculations (15 points): 3 points for each correct category
    revenue_categories = [
        "massage_services", "facial_services", "body_treatments", 
        "nail_services", "retail_products", "total"
    ]
    revenue_score = 0
    revenue_details = {}
    
    for category in revenue_categories:
        submitted_value = submission["revenue_projection"]["projected_annual_revenue"].get(category, 0)
        expected_value = answer_key["revenue_projection"]["projected_annual_revenue"].get(category, 0)
        
        # Tolerance: ±$100 for amounts over $100,000
        tolerance = 100
        
        if is_within_range(submitted_value, expected_value, tolerance):
            points = 3 if category != "total" else 0  # Total is derived, not directly scored
            revenue_score += points
            revenue_details[category] = {"points": points, "submitted": submitted_value, "expected": expected_value}
        else:
            revenue_details[category] = {"points": 0, "submitted": submitted_value, "expected": expected_value}
    
    score += revenue_score
    details["projected_annual_revenue"] = {"score": revenue_score, "max_score": 15, "details": revenue_details}
    
    # Projected revenue mix calculations (10 points): 2 points for each correct percentage
    mix_categories = [
        "massage_services", "facial_services", "body_treatments", 
        "nail_services", "retail_products"
    ]
    mix_score = 0
    mix_details = {}
    
    for category in mix_categories:
        submitted_value = submission["revenue_projection"]["projected_revenue_mix"].get(category, 0)
        expected_value = answer_key["revenue_projection"]["projected_revenue_mix"].get(category, 0)
        
        # Tolerance: ±0.02 (2 percentage points)
        tolerance = 0.02
        
        if is_within_range(submitted_value, expected_value, tolerance):
            mix_score += 2
            mix_details[category] = {"points": 2, "submitted": submitted_value, "expected": expected_value}
        else:
            mix_details[category] = {"points": 0, "submitted": submitted_value, "expected": expected_value}
    
    score += mix_score
    details["projected_revenue_mix"] = {"score": mix_score, "max_score": 10, "details": mix_details}
    
    return score, {"score": score, "max_score": max_score, "details": details}


def evaluate_expense_budget(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the expense budget creation section."""
    score = 0
    max_score = 25
    details = {}
    
    # Annual expenses by category (18 points): 2 points for each category within target range
    expense_categories = [
        "staff_wages", "benefits", "supplies", "products", "utilities",
        "marketing", "maintenance", "admin", "rent"
    ]
    expense_score = 0
    expense_details = {}
    
    for category in expense_categories:
        submitted_value = submission["expense_budget"]["annual_expenses_by_category"].get(category, 0)
        expected_value = answer_key["expense_budget"]["annual_expenses_by_category"].get(category, 0)
        
        # Tolerance: ±$100 for amounts over $100,000; ±$50 for smaller amounts
        tolerance = 100 if expected_value > 100000 else 50
        
        if is_within_range(submitted_value, expected_value, tolerance):
            expense_score += 2
            expense_details[category] = {"points": 2, "submitted": submitted_value, "expected": expected_value}
        else:
            expense_details[category] = {"points": 0, "submitted": submitted_value, "expected": expected_value}
    
    score += expense_score
    details["annual_expenses_by_category"] = {"score": expense_score, "max_score": 18, "details": expense_details}
    
    # Total annual expenses calculation (2 points)
    submitted_total = submission["expense_budget"]["total_annual_expenses"]
    expected_total = answer_key["expense_budget"]["total_annual_expenses"]
    
    # Tolerance: ±$100 for amounts over $100,000
    total_tolerance = 100
    
    if is_within_range(submitted_total, expected_total, total_tolerance):
        total_score = 2
    else:
        total_score = 0
    
    score += total_score
    details["total_annual_expenses"] = {
        "score": total_score, 
        "max_score": 2, 
        "details": {"submitted": submitted_total, "expected": expected_total}
    }
    
    # Expense-to-revenue ratio calculation (2 points)
    submitted_ratio = submission["expense_budget"]["expense_to_revenue_ratio"]
    expected_ratio = answer_key["expense_budget"]["expense_to_revenue_ratio"]
    
    # Tolerance: ±0.02 (2 percentage points)
    ratio_tolerance = 0.02
    
    if is_within_range(submitted_ratio, expected_ratio, ratio_tolerance):
        ratio_score = 2
    else:
        ratio_score = 0
    
    score += ratio_score
    details["expense_to_revenue_ratio"] = {
        "score": ratio_score, 
        "max_score": 2, 
        "details": {"submitted": submitted_ratio, "expected": expected_ratio}
    }
    
    # Projected annual profit calculation (3 points)
    submitted_profit = submission["expense_budget"]["projected_annual_profit"]
    expected_profit = answer_key["expense_budget"]["projected_annual_profit"]
    
    # Tolerance: ±$100 for amounts over $100,000
    profit_tolerance = 100
    
    if is_within_range(submitted_profit, expected_profit, profit_tolerance):
        profit_score = 3
    else:
        profit_score = 0
    
    score += profit_score
    details["projected_annual_profit"] = {
        "score": profit_score, 
        "max_score": 3, 
        "details": {"submitted": submitted_profit, "expected": expected_profit}
    }
    
    return score, {"score": score, "max_score": max_score, "details": details}


def evaluate_financial_goals(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the financial goal setting section."""
    score = 0
    max_score = 25
    details = {}
    
    # Revenue per treatment room (6 points): Must be within benchmark range
    submitted_room_revenue = submission["financial_goals"]["revenue_per_treatment_room"]
    expected_room_revenue = answer_key["financial_goals"]["revenue_per_treatment_room"]
    
    # Benchmark range: $11,000-$14,000/month
    min_room_revenue = 11000
    max_room_revenue = 14000
    
    if is_within_benchmark(submitted_room_revenue, min_room_revenue, max_room_revenue):
        room_score = 6
    else:
        room_score = 0
    
    score += room_score
    details["revenue_per_treatment_room"] = {
        "score": room_score, 
        "max_score": 6, 
        "details": {
            "submitted": submitted_room_revenue, 
            "expected": expected_room_revenue,
            "benchmark_range": [min_room_revenue, max_room_revenue]
        }
    }
    
    # Revenue per therapist (6 points): Must be within benchmark range
    submitted_therapist_revenue = submission["financial_goals"]["revenue_per_therapist"]
    expected_therapist_revenue = answer_key["financial_goals"]["revenue_per_therapist"]
    
    # Benchmark range: $7,500-$9,500/month
    min_therapist_revenue = 7500
    max_therapist_revenue = 9500
    
    if is_within_benchmark(submitted_therapist_revenue, min_therapist_revenue, max_therapist_revenue):
        therapist_score = 6
    else:
        therapist_score = 0
    
    score += therapist_score
    details["revenue_per_therapist"] = {
        "score": therapist_score, 
        "max_score": 6, 
        "details": {
            "submitted": submitted_therapist_revenue, 
            "expected": expected_therapist_revenue,
            "benchmark_range": [min_therapist_revenue, max_therapist_revenue]
        }
    }
    
    # Product sales percentage (6 points): Must be within benchmark range
    submitted_product_percentage = submission["financial_goals"]["product_sales_percentage"]
    expected_product_percentage = answer_key["financial_goals"]["product_sales_percentage"]
    
    # Benchmark range: 8-12%
    min_product_percentage = 0.08
    max_product_percentage = 0.12
    
    if is_within_benchmark(submitted_product_percentage, min_product_percentage, max_product_percentage):
        product_score = 6
    else:
        product_score = 0
    
    score += product_score
    details["product_sales_percentage"] = {
        "score": product_score, 
        "max_score": 6, 
        "details": {
            "submitted": submitted_product_percentage, 
            "expected": expected_product_percentage,
            "benchmark_range": [min_product_percentage, max_product_percentage]
        }
    }
    
    # Target profit margin (7 points): Must be within benchmark range
    submitted_margin = submission["financial_goals"]["target_profit_margin"]
    expected_margin = answer_key["financial_goals"]["target_profit_margin"]
    
    # Benchmark range: 28-32%
    min_margin = 0.28
    max_margin = 0.32
    
    if is_within_benchmark(submitted_margin, min_margin, max_margin):
        margin_score = 7
    else:
        margin_score = 0
    
    score += margin_score
    details["target_profit_margin"] = {
        "score": margin_score, 
        "max_score": 7, 
        "details": {
            "submitted": submitted_margin, 
            "expected": expected_margin,
            "benchmark_range": [min_margin, max_margin]
        }
    }
    
    return score, {"score": score, "max_score": max_score, "details": details}


def check_critical_elements(submission: Dict, answer_key: Dict) -> Dict:
    """Check if the candidate correctly completed the critical elements."""
    critical_elements = {
        "previous_year_profit_margin": False,
        "projected_total_annual_revenue": False,
        "balanced_expense_budget": False,
        "financial_goals_within_benchmarks": False
    }
    
    # Previous year's profit margin (within ±2%)
    submitted_margin = submission["budget_analysis"]["previous_year_profit_margin"]
    expected_margin = answer_key["budget_analysis"]["previous_year_profit_margin"]
    if is_within_range(submitted_margin, expected_margin, 0.02):
        critical_elements["previous_year_profit_margin"] = True
    
    # Project total annual revenue (within ±5%)
    submitted_revenue = submission["revenue_projection"]["projected_annual_revenue"]["total"]
    expected_revenue = answer_key["revenue_projection"]["projected_annual_revenue"]["total"]
    if is_within_range(submitted_revenue, expected_revenue, expected_revenue * 0.05):
        critical_elements["projected_total_annual_revenue"] = True
    
    # Create a balanced expense budget with expense-to-revenue ratio between 60-70%
    submitted_ratio = submission["expense_budget"]["expense_to_revenue_ratio"]
    if 0.60 <= submitted_ratio <= 0.70:
        critical_elements["balanced_expense_budget"] = True
    
    # Set financial goals within the provided benchmark ranges
    financial_goals_correct = True
    
    # Revenue per treatment room: $11,000-$14,000/month
    if not (11000 <= submission["financial_goals"]["revenue_per_treatment_room"] <= 14000):
        financial_goals_correct = False
    
    # Revenue per therapist: $7,500-$9,500/month
    if not (7500 <= submission["financial_goals"]["revenue_per_therapist"] <= 9500):
        financial_goals_correct = False
    
    # Product sales percentage: 8-12%
    if not (0.08 <= submission["financial_goals"]["product_sales_percentage"] <= 0.12):
        financial_goals_correct = False
    
    # Target profit margin: 28-32%
    if not (0.28 <= submission["financial_goals"]["target_profit_margin"] <= 0.32):
        financial_goals_correct = False
    
    critical_elements["financial_goals_within_benchmarks"] = financial_goals_correct
    
    return critical_elements


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "sections": {},
        "critical_elements": {},
        "section_scores": {},
        "overall_score": 0.0,
        "passed": False
    }
    
    # Evaluate each section
    budget_score, budget_details = evaluate_budget_analysis(submission, answer_key)
    revenue_score, revenue_details = evaluate_revenue_projection(submission, answer_key)
    expense_score, expense_details = evaluate_expense_budget(submission, answer_key)
    goals_score, goals_details = evaluate_financial_goals(submission, answer_key)
    
    # Store section results
    results["sections"]["budget_analysis"] = budget_details
    results["sections"]["revenue_projection"] = revenue_details
    results["sections"]["expense_budget"] = expense_details
    results["sections"]["financial_goals"] = goals_details
    
    # Check critical elements
    results["critical_elements"] = check_critical_elements(submission, answer_key)
    
    # Calculate section scores as percentages
    results["section_scores"]["budget_analysis"] = (budget_score / 25) * 100
    results["section_scores"]["revenue_projection"] = (revenue_score / 25) * 100
    results["section_scores"]["expense_budget"] = (expense_score / 25) * 100
    results["section_scores"]["financial_goals"] = (goals_score / 25) * 100
    
    # Calculate overall score
    total_score = budget_score + revenue_score + expense_score + goals_score
    results["overall_score"] = (total_score / 100) * 100
    
    # Determine if the candidate passed
    section_minimums_met = all(score >= 60 for score in results["section_scores"].values())
    critical_elements_met = all(results["critical_elements"].values())
    overall_score_met = results["overall_score"] >= 70
    
    results["passed"] = section_minimums_met and critical_elements_met and overall_score_met
    
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
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed: {results['passed']}")


if __name__ == "__main__":
    main()