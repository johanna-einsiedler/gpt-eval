#!/usr/bin/env python3
"""
Food Service Manager Practical Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Food Service Manager practical exam, focusing on sales data analysis.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

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


def evaluate_item_metrics(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the accuracy of item metrics calculations.
    
    Returns a dictionary with evaluation results.
    """
    results = {
        "total_items": len(answer_key["item_metrics"]),
        "correct_items": 0,
        "items_with_errors": [],
        "error_details": []
    }
    
    # Create lookup dictionaries for faster access
    submission_items = {item["item_id"]: item for item in submission["item_metrics"]}
    answer_key_items = {item["item_id"]: item for item in answer_key["item_metrics"]}
    
    # Check if all items are present
    missing_items = set(answer_key_items.keys()) - set(submission_items.keys())
    if missing_items:
        results["error_details"].append(f"Missing items in submission: {', '.join(missing_items)}")
    
    # Check each item's metrics
    for item_id, key_item in answer_key_items.items():
        if item_id not in submission_items:
            results["items_with_errors"].append(item_id)
            continue
            
        sub_item = submission_items[item_id]
        item_errors = []
        
        # Check each metric
        metrics_to_check = [
            ("total_quantity", 0),  # No decimal places for quantities
            ("total_revenue", 2),   # 2 decimal places for currency
            ("total_food_cost", 2), # 2 decimal places for currency
            ("gross_profit", 2),    # 2 decimal places for currency
            ("profit_margin_percentage", 1),  # 1 decimal place for percentages
            ("popularity_rank", 0), # No decimal places for ranks
            ("profit_rank", 0)      # No decimal places for ranks
        ]
        
        has_errors = False
        for metric, decimal_places in metrics_to_check:
            # Skip if metric is missing
            if metric not in sub_item or metric not in key_item:
                item_errors.append(f"Missing metric: {metric}")
                has_errors = True
                continue
                
            # For ranks, exact match is required
            if metric in ["popularity_rank", "profit_rank"]:
                if sub_item[metric] != key_item[metric]:
                    item_errors.append(f"{metric}: {sub_item[metric]} (expected {key_item[metric]})")
                    has_errors = True
            # For other metrics, check within rounding tolerance
            else:
                # Round both values to specified decimal places for comparison
                sub_value = round(float(sub_item[metric]), decimal_places)
                key_value = round(float(key_item[metric]), decimal_places)
                
                # Allow small floating point differences
                tolerance = 10**(-decimal_places) / 2
                if abs(sub_value - key_value) > tolerance:
                    item_errors.append(f"{metric}: {sub_value} (expected {key_value})")
                    has_errors = True
        
        if has_errors:
            results["items_with_errors"].append(item_id)
            results["error_details"].append(f"Item {item_id} errors: {', '.join(item_errors)}")
        else:
            results["correct_items"] += 1
    
    # Calculate percentage correct
    results["percentage_correct"] = (results["correct_items"] / results["total_items"]) * 100
    
    return results


def evaluate_underperforming_items(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the identification of underperforming items.
    
    Returns a dictionary with evaluation results.
    """
    results = {
        "expected_items": set(answer_key["underperforming_items"]),
        "submitted_items": set(submission.get("underperforming_items", [])),
        "correctly_identified": 0,
        "incorrectly_identified": 0,
        "missed_items": []
    }
    
    # Calculate correctly identified items
    correct_items = results["expected_items"].intersection(results["submitted_items"])
    results["correctly_identified"] = len(correct_items)
    
    # Calculate incorrectly identified items
    incorrect_items = results["submitted_items"] - results["expected_items"]
    results["incorrectly_identified"] = len(incorrect_items)
    
    # Calculate missed items
    missed_items = results["expected_items"] - results["submitted_items"]
    results["missed_items"] = list(missed_items)
    
    # Calculate percentage correct (based on correctly identified minus penalties for incorrect)
    total_expected = len(results["expected_items"])
    results["percentage_correct"] = max(0, (results["correctly_identified"] - 
                                           results["incorrectly_identified"] / 2) / total_expected * 100)
    
    return results


def evaluate_price_adjustments(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the price adjustment calculations.
    
    Returns a dictionary with evaluation results.
    """
    results = {
        "total_adjustments": len(answer_key["price_adjustments"]),
        "correct_adjustments": 0,
        "items_with_errors": [],
        "error_details": []
    }
    
    # Create lookup dictionaries
    submission_adjustments = {adj["item_id"]: adj for adj in submission.get("price_adjustments", [])}
    answer_key_adjustments = {adj["item_id"]: adj for adj in answer_key["price_adjustments"]}
    
    # Check if all required adjustments are present
    missing_items = set(answer_key_adjustments.keys()) - set(submission_adjustments.keys())
    if missing_items:
        results["error_details"].append(f"Missing price adjustments for items: {', '.join(missing_items)}")
        results["items_with_errors"].extend(missing_items)
    
    # Check each price adjustment
    for item_id, key_adj in answer_key_adjustments.items():
        if item_id not in submission_adjustments:
            continue
            
        sub_adj = submission_adjustments[item_id]
        item_errors = []
        
        # Check current price
        if abs(round(sub_adj.get("current_price", 0), 2) - round(key_adj["current_price"], 2)) > 0.01:
            item_errors.append(f"current_price: {sub_adj.get('current_price')} (expected {key_adj['current_price']})")
        
        # Check new price
        if abs(round(sub_adj.get("new_price", 0), 2) - round(key_adj["new_price"], 2)) > 0.01:
            item_errors.append(f"new_price: {sub_adj.get('new_price')} (expected {key_adj['new_price']})")
        
        if item_errors:
            results["items_with_errors"].append(item_id)
            results["error_details"].append(f"Price adjustment for {item_id} errors: {', '.join(item_errors)}")
        else:
            results["correct_adjustments"] += 1
    
    # Calculate percentage correct
    results["percentage_correct"] = (results["correct_adjustments"] / results["total_adjustments"]) * 100
    
    return results


def calculate_overall_score(metrics_results: Dict, underperforming_results: Dict, 
                           price_results: Dict) -> Tuple[float, str]:
    """
    Calculate the overall score and determine the performance level.
    
    Returns a tuple of (score, performance_level).
    """
    # Weights for each section
    metrics_weight = 0.50  # 50% of total score
    underperforming_weight = 0.25  # 25% of total score
    price_weight = 0.25  # 25% of total score
    
    # Calculate weighted score
    weighted_score = (
        metrics_results["percentage_correct"] * metrics_weight +
        underperforming_results["percentage_correct"] * underperforming_weight +
        price_results["percentage_correct"] * price_weight
    )
    
    # Determine performance level
    if weighted_score >= 90:
        performance = "Excellent"
    elif weighted_score >= 80:
        performance = "Good"
    elif weighted_score >= 70:
        performance = "Satisfactory"
    elif weighted_score >= 60:
        performance = "Needs Improvement"
    else:
        performance = "Failing"
    
    return weighted_score, performance


def main():
    """Main function to evaluate the candidate's submission."""
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load JSON files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    metrics_results = evaluate_item_metrics(submission, answer_key)
    underperforming_results = evaluate_underperforming_items(submission, answer_key)
    price_results = evaluate_price_adjustments(submission, answer_key)
    
    # Calculate overall score
    overall_score, performance_level = calculate_overall_score(
        metrics_results, underperforming_results, price_results
    )
    
    # Prepare results
    evaluation_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 1),
        "performance_level": performance_level,
        "section_scores": {
            "item_metrics": {
                "score": round(metrics_results["percentage_correct"], 1),
                "weight": "50%",
                "correct_items": metrics_results["correct_items"],
                "total_items": metrics_results["total_items"],
                "items_with_errors": metrics_results["items_with_errors"],
                "error_details": metrics_results["error_details"]
            },
            "underperforming_items": {
                "score": round(underperforming_results["percentage_correct"], 1),
                "weight": "25%",
                "correctly_identified": underperforming_results["correctly_identified"],
                "incorrectly_identified": underperforming_results["incorrectly_identified"],
                "expected_items": list(underperforming_results["expected_items"]),
                "submitted_items": list(underperforming_results["submitted_items"]),
                "missed_items": underperforming_results["missed_items"]
            },
            "price_adjustments": {
                "score": round(price_results["percentage_correct"], 1),
                "weight": "25%",
                "correct_adjustments": price_results["correct_adjustments"],
                "total_adjustments": price_results["total_adjustments"],
                "items_with_errors": price_results["items_with_errors"],
                "error_details": price_results["error_details"]
            }
        },
        "passing_criteria": {
            "item_metrics": metrics_results["percentage_correct"] >= 90,
            "underperforming_items": (
                underperforming_results["correctly_identified"] >= 5 and
                underperforming_results["incorrectly_identified"] <= 2
            ),
            "price_adjustments": price_results["correct_adjustments"] >= 4
        },
        "passed": overall_score >= 70  # Passing threshold is 70%
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {round(overall_score, 1)}% - {performance_level}")


if __name__ == "__main__":
    main()