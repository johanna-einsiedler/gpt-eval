#!/usr/bin/env python3

import json
import sys
from typing import Dict, Any, List, Union


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)


def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1 answers and assign points."""
    result = {"points": 0, "max_points": 30, "breakdown": {}}
    
    # Top Products (10 points)
    submitted_products = submission["task1"]["top_products"]
    correct_products = answer_key["task1"]["top_products"]
    
    if submitted_products == correct_products:
        result["breakdown"]["top_products"] = {"points": 10, "max_points": 10, "note": "All 3 correct in right order"}
        result["points"] += 10
    elif submitted_products[:2] == correct_products[:2]:
        result["breakdown"]["top_products"] = {"points": 6, "max_points": 10, "note": "2 correct in right order"}
        result["points"] += 6
    elif set(submitted_products) == set(correct_products):
        result["breakdown"]["top_products"] = {"points": 5, "max_points": 10, "note": "All correct but wrong order"}
        result["points"] += 5
    else:
        result["breakdown"]["top_products"] = {"points": 0, "max_points": 10, "note": "Incorrect products"}
    
    # Growth Rate Q4 (8 points)
    submitted_growth = submission["task1"]["growth_rate_q4"]
    correct_growth = answer_key["task1"]["growth_rate_q4"]
    growth_diff = abs(submitted_growth - correct_growth)
    
    if growth_diff <= 0.5:
        result["breakdown"]["growth_rate_q4"] = {"points": 8, "max_points": 8, "note": "Within ±0.5%"}
        result["points"] += 8
    elif growth_diff <= 1.0:
        result["breakdown"]["growth_rate_q4"] = {"points": 4, "max_points": 8, "note": "Within ±1%"}
        result["points"] += 4
    else:
        result["breakdown"]["growth_rate_q4"] = {"points": 0, "max_points": 8, "note": "Outside ±1%"}
    
    # Seasonal Pattern (6 points)
    if submission["task1"]["seasonal_pattern"] == answer_key["task1"]["seasonal_pattern"]:
        result["breakdown"]["seasonal_pattern"] = {"points": 6, "max_points": 6, "note": "Correct"}
        result["points"] += 6
    else:
        result["breakdown"]["seasonal_pattern"] = {"points": 0, "max_points": 6, "note": "Incorrect"}
    
    # Peak Month (6 points)
    if submission["task1"]["peak_month"] == answer_key["task1"]["peak_month"]:
        result["breakdown"]["peak_month"] = {"points": 6, "max_points": 6, "note": "Correct"}
        result["points"] += 6
    else:
        result["breakdown"]["peak_month"] = {"points": 0, "max_points": 6, "note": "Incorrect"}
    
    return result


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2 answers and assign points."""
    result = {"points": 0, "max_points": 30, "breakdown": {}}
    
    # Market Expansion (6 points)
    if submission["task2"]["market_expansion"] == answer_key["task2"]["market_expansion"]:
        result["breakdown"]["market_expansion"] = {"points": 6, "max_points": 6, "note": "Correct"}
        result["points"] += 6
    else:
        result["breakdown"]["market_expansion"] = {"points": 0, "max_points": 6, "note": "Incorrect"}
    
    # Price Sensitivity Score (8 points)
    submitted_score = submission["task2"]["price_sensitivity_score"]
    correct_score = answer_key["task2"]["price_sensitivity_score"]
    score_diff = abs(submitted_score - correct_score)
    
    if score_diff == 0:
        result["breakdown"]["price_sensitivity_score"] = {"points": 8, "max_points": 8, "note": "Exact score"}
        result["points"] += 8
    elif score_diff <= 1:
        result["breakdown"]["price_sensitivity_score"] = {"points": 4, "max_points": 8, "note": "Within ±1"}
        result["points"] += 4
    else:
        result["breakdown"]["price_sensitivity_score"] = {"points": 0, "max_points": 8, "note": "Outside ±1"}
    
    # Trend Direction (6 points)
    if submission["task2"]["trend_direction"] == answer_key["task2"]["trend_direction"]:
        result["breakdown"]["trend_direction"] = {"points": 6, "max_points": 6, "note": "Correct"}
        result["points"] += 6
    else:
        result["breakdown"]["trend_direction"] = {"points": 0, "max_points": 6, "note": "Incorrect"}
    
    # Expected Demand Change (10 points)
    submitted_demand = submission["task2"]["expected_demand_change"]
    correct_demand = answer_key["task2"]["expected_demand_change"]
    demand_diff = abs(submitted_demand - correct_demand)
    
    if demand_diff == 0:
        result["breakdown"]["expected_demand_change"] = {"points": 10, "max_points": 10, "note": "Exact answer"}
        result["points"] += 10
    elif demand_diff <= 0.5:
        result["breakdown"]["expected_demand_change"] = {"points": 6, "max_points": 10, "note": "Within ±0.5%"}
        result["points"] += 6
    elif demand_diff <= 1.0:
        result["breakdown"]["expected_demand_change"] = {"points": 3, "max_points": 10, "note": "Within ±1%"}
        result["points"] += 3
    else:
        result["breakdown"]["expected_demand_change"] = {"points": 0, "max_points": 10, "note": "Outside ±1%"}
    
    return result


def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3 answers and assign points."""
    result = {"points": 0, "max_points": 40, "breakdown": {}}
    
    # Product Forecasts (15 points, 5 each)
    products = ["product_a_forecast", "product_b_forecast", "product_c_forecast"]
    forecast_points = 0
    
    for product in products:
        submitted_value = submission["task3"][product]
        correct_value = answer_key["task3"][product]
        percentage_diff = abs((submitted_value - correct_value) / correct_value * 100)
        
        if percentage_diff <= 5:
            result["breakdown"][product] = {"points": 5, "max_points": 5, "note": f"Within ±5% (submitted: {submitted_value}, correct: {correct_value})"}
            forecast_points += 5
        else:
            result["breakdown"][product] = {"points": 0, "max_points": 5, "note": f"Outside ±5% (submitted: {submitted_value}, correct: {correct_value})"}
    
    result["points"] += forecast_points
    
    # Total Inventory Value (10 points)
    submitted_inventory = submission["task3"]["total_inventory_value"]
    correct_inventory = answer_key["task3"]["total_inventory_value"]
    inventory_percentage_diff = abs((submitted_inventory - correct_inventory) / correct_inventory * 100)
    
    if inventory_percentage_diff <= 2:
        result["breakdown"]["total_inventory_value"] = {"points": 10, "max_points": 10, "note": "Within ±2%"}
        result["points"] += 10
    elif inventory_percentage_diff <= 5:
        result["breakdown"]["total_inventory_value"] = {"points": 5, "max_points": 10, "note": "Within ±5%"}
        result["points"] += 5
    else:
        result["breakdown"]["total_inventory_value"] = {"points": 0, "max_points": 10, "note": "Outside ±5%"}
    
    # Recommended Stock Ratio (15 points)
    submitted_ratio = submission["task3"]["recommended_stock_ratio"]
    correct_ratio = answer_key["task3"]["recommended_stock_ratio"]
    
    # Check if ratios sum to 1.00
    if abs(sum(submitted_ratio) - 1.00) > 0.01:
        result["breakdown"]["recommended_stock_ratio"] = {"points": 0, "max_points": 15, "note": "Ratios don't sum to 1.00"}
    else:
        # Check differences for each ratio
        max_diff = max(abs(submitted_ratio[i] - correct_ratio[i]) for i in range(3))
        
        if max_diff <= 0.03:
            result["breakdown"]["recommended_stock_ratio"] = {"points": 15, "max_points": 15, "note": "All ratios within ±0.03"}
            result["points"] += 15
        elif max_diff <= 0.05:
            result["breakdown"]["recommended_stock_ratio"] = {"points": 7, "max_points": 15, "note": "All ratios within ±0.05"}
            result["points"] += 7
        else:
            result["breakdown"]["recommended_stock_ratio"] = {"points": 0, "max_points": 15, "note": "Outside ±0.05"}
    
    return result


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "UNKNOWN"),
        "overall_score": 0,
        "passing_threshold": 70,
        "strong_performance_threshold": 85,
        "tasks": {}
    }
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    results["tasks"]["task1"] = task1_results
    results["tasks"]["task2"] = task2_results
    results["tasks"]["task3"] = task3_results
    
    # Calculate overall score
    total_points = task1_results["points"] + task2_results["points"] + task3_results["points"]
    max_points = task1_results["max_points"] + task2_results["max_points"] + task3_results["max_points"]
    results["overall_score"] = round((total_points / max_points) * 100, 2)
    
    # Determine if candidate passed
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    results["strong_performance"] = results["overall_score"] >= results["strong_performance_threshold"]
    
    return results


def main():
    """Main function to process command line arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
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
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")
    if results['strong_performance']:
        print("Strong Performance: YES")


if __name__ == "__main__":
    main()