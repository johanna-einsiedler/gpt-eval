#!/usr/bin/env python3
"""
Logistics Data Analysis Exam Evaluator

This script evaluates a candidate's submission against an answer key for the
logistics data analysis practical exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any, List, Union


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_numeric(candidate_value: float, correct_value: float, 
                     tolerance: float = 0.05) -> float:
    """
    Evaluate a numeric answer with tolerance.
    
    Args:
        candidate_value: The candidate's answer
        correct_value: The correct answer
        tolerance: The acceptable percentage difference (default 5%)
        
    Returns:
        Score (1.0 for correct, 0.5 for close, 0.0 for incorrect)
    """
    if candidate_value == correct_value:
        return 1.0
    
    # Calculate percentage difference
    if correct_value != 0:
        diff_pct = abs(candidate_value - correct_value) / abs(correct_value)
        if diff_pct <= tolerance:
            return 0.5
    
    return 0.0


def evaluate_list(candidate_list: List[str], correct_list: List[str]) -> float:
    """
    Evaluate a list answer.
    
    Args:
        candidate_list: The candidate's list
        correct_list: The correct list
        
    Returns:
        Score (1.0 for exact match, 0.5 for partial match, 0.0 for poor match)
    """
    if candidate_list == correct_list:
        return 1.0
    
    # Check for partial match (at least 75% correct)
    if not candidate_list or not correct_list:
        return 0.0
    
    correct_set = set(correct_list)
    candidate_set = set(candidate_list)
    
    common_items = len(correct_set.intersection(candidate_set))
    total_correct = len(correct_set)
    
    if common_items / total_correct >= 0.75:
        return 0.5
    
    return 0.0


def evaluate_dict(candidate_dict: Dict[str, float], 
                  correct_dict: Dict[str, float],
                  tolerance: float = 0.05) -> float:
    """
    Evaluate a dictionary of numeric values.
    
    Args:
        candidate_dict: The candidate's dictionary
        correct_dict: The correct dictionary
        tolerance: The acceptable percentage difference (default 5%)
        
    Returns:
        Score (1.0 for correct, 0.5 for close, 0.0 for incorrect)
    """
    if not candidate_dict or not correct_dict:
        return 0.0
    
    if set(candidate_dict.keys()) != set(correct_dict.keys()):
        return 0.0
    
    total_score = 0
    for key in correct_dict:
        total_score += evaluate_numeric(
            candidate_dict.get(key, 0), 
            correct_dict[key],
            tolerance
        )
    
    avg_score = total_score / len(correct_dict)
    
    if avg_score >= 0.9:
        return 1.0
    elif avg_score >= 0.75:
        return 0.5
    else:
        return 0.0


def evaluate_string(candidate_str: str, correct_str: str) -> float:
    """
    Evaluate a string answer.
    
    Args:
        candidate_str: The candidate's string
        correct_str: The correct string
        
    Returns:
        Score (1.0 for exact match, 0.0 for mismatch)
    """
    return 1.0 if candidate_str == correct_str else 0.0


def evaluate_submission(submission: Dict[str, Any], 
                        answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate the candidate's submission against the answer key.
    
    Args:
        submission: The candidate's submission
        answer_key: The answer key
        
    Returns:
        Dictionary with evaluation results
    """
    results = {
        "task1": {},
        "task2": {},
        "task3": {},
        "scores": {
            "task1": 0,
            "task2": 0,
            "task3": 0,
            "total": 0
        }
    }
    
    # Task 1 evaluation
    task1_submission = submission.get("task1", {})
    task1_key = answer_key.get("task1", {})
    
    # Excess inventory value
    excess_score = evaluate_numeric(
        task1_submission.get("excess_inventory_value", 0),
        task1_key.get("excess_inventory_value", 0)
    )
    results["task1"]["excess_inventory_value"] = {
        "candidate_answer": task1_submission.get("excess_inventory_value", 0),
        "correct_answer": task1_key.get("excess_inventory_value", 0),
        "score": excess_score
    }
    
    # Stockout risk SKUs
    stockout_score = evaluate_list(
        task1_submission.get("stockout_risk_skus", []),
        task1_key.get("stockout_risk_skus", [])
    )
    results["task1"]["stockout_risk_skus"] = {
        "candidate_answer": task1_submission.get("stockout_risk_skus", []),
        "correct_answer": task1_key.get("stockout_risk_skus", []),
        "score": stockout_score
    }
    
    # Optimal reorder point
    reorder_score = evaluate_numeric(
        task1_submission.get("optimal_reorder_point_sku123", 0),
        task1_key.get("optimal_reorder_point_sku123", 0)
    )
    results["task1"]["optimal_reorder_point_sku123"] = {
        "candidate_answer": task1_submission.get("optimal_reorder_point_sku123", 0),
        "correct_answer": task1_key.get("optimal_reorder_point_sku123", 0),
        "score": reorder_score
    }
    
    # Highest carrying cost category
    category_score = evaluate_string(
        task1_submission.get("highest_carrying_cost_category", ""),
        task1_key.get("highest_carrying_cost_category", "")
    )
    results["task1"]["highest_carrying_cost_category"] = {
        "candidate_answer": task1_submission.get("highest_carrying_cost_category", ""),
        "correct_answer": task1_key.get("highest_carrying_cost_category", ""),
        "score": category_score
    }
    
    # Task 2 evaluation
    task2_submission = submission.get("task2", {})
    task2_key = answer_key.get("task2", {})
    
    # Carrier cost per mile
    carrier_cost_score = evaluate_dict(
        task2_submission.get("carrier_cost_per_mile", {}),
        task2_key.get("carrier_cost_per_mile", {})
    )
    results["task2"]["carrier_cost_per_mile"] = {
        "candidate_answer": task2_submission.get("carrier_cost_per_mile", {}),
        "correct_answer": task2_key.get("carrier_cost_per_mile", {}),
        "score": carrier_cost_score
    }
    
    # Most efficient carrier
    carrier_score = evaluate_string(
        task2_submission.get("most_efficient_carrier", ""),
        task2_key.get("most_efficient_carrier", "")
    )
    results["task2"]["most_efficient_carrier"] = {
        "candidate_answer": task2_submission.get("most_efficient_carrier", ""),
        "correct_answer": task2_key.get("most_efficient_carrier", ""),
        "score": carrier_score
    }
    
    # Potential annual savings
    savings_score = evaluate_numeric(
        task2_submission.get("potential_annual_savings", 0),
        task2_key.get("potential_annual_savings", 0)
    )
    results["task2"]["potential_annual_savings"] = {
        "candidate_answer": task2_submission.get("potential_annual_savings", 0),
        "correct_answer": task2_key.get("potential_annual_savings", 0),
        "score": savings_score
    }
    
    # Optimal shipment size
    shipment_score = evaluate_numeric(
        task2_submission.get("optimal_shipment_size", 0),
        task2_key.get("optimal_shipment_size", 0)
    )
    results["task2"]["optimal_shipment_size"] = {
        "candidate_answer": task2_submission.get("optimal_shipment_size", 0),
        "correct_answer": task2_key.get("optimal_shipment_size", 0),
        "score": shipment_score
    }
    
    # Task 3 evaluation
    task3_submission = submission.get("task3", {})
    task3_key = answer_key.get("task3", {})
    
    # Worst performing region
    region_score = evaluate_string(
        task3_submission.get("worst_performing_region", ""),
        task3_key.get("worst_performing_region", "")
    )
    results["task3"]["worst_performing_region"] = {
        "candidate_answer": task3_submission.get("worst_performing_region", ""),
        "correct_answer": task3_key.get("worst_performing_region", ""),
        "score": region_score
    }
    
    # On-time delivery percentage
    delivery_score = evaluate_numeric(
        task3_submission.get("on_time_delivery_percentage", 0),
        task3_key.get("on_time_delivery_percentage", 0)
    )
    results["task3"]["on_time_delivery_percentage"] = {
        "candidate_answer": task3_submission.get("on_time_delivery_percentage", 0),
        "correct_answer": task3_key.get("on_time_delivery_percentage", 0),
        "score": delivery_score
    }
    
    # Correlation coefficient
    correlation_score = evaluate_numeric(
        task3_submission.get("correlation_coefficient", 0),
        task3_key.get("correlation_coefficient", 0)
    )
    results["task3"]["correlation_coefficient"] = {
        "candidate_answer": task3_submission.get("correlation_coefficient", 0),
        "correct_answer": task3_key.get("correlation_coefficient", 0),
        "score": correlation_score
    }
    
    # Priority improvement metric
    metric_score = evaluate_string(
        task3_submission.get("priority_improvement_metric", ""),
        task3_key.get("priority_improvement_metric", "")
    )
    results["task3"]["priority_improvement_metric"] = {
        "candidate_answer": task3_submission.get("priority_improvement_metric", ""),
        "correct_answer": task3_key.get("priority_improvement_metric", ""),
        "score": metric_score
    }
    
    # Calculate task scores
    results["scores"]["task1"] = (
        excess_score + stockout_score + reorder_score + category_score
    )
    results["scores"]["task2"] = (
        carrier_cost_score + carrier_score + savings_score + shipment_score
    )
    results["scores"]["task3"] = (
        region_score + delivery_score + correlation_score + metric_score
    )
    
    # Calculate total score
    total_points = (
        results["scores"]["task1"] + 
        results["scores"]["task2"] + 
        results["scores"]["task3"]
    )
    
    # Calculate overall percentage score (out of 12 possible points)
    results["overall_score"] = round((total_points / 12) * 100, 2)
    results["scores"]["total"] = total_points
    
    # Add candidate ID if available
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
    return results


def main():
    """Main function to process command line arguments and evaluate submission."""
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


if __name__ == "__main__":
    main()