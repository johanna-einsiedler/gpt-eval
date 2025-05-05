#!/usr/bin/env python3
"""
Logistics Analyst Practical Exam Evaluator

This script evaluates a candidate's submission against an answer key and generates
a detailed assessment report with an overall score.

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


def evaluate_forecast_values(submission: List[float], key: List[float]) -> Tuple[float, str]:
    """Evaluate the forecast values."""
    # Check if trend is maintained (approximately 5 units per week)
    trend_correct = True
    for i in range(1, len(submission)):
        if not (3 <= submission[i] - submission[i-1] <= 7):
            trend_correct = False
            break
    
    # Calculate average deviation from expected values
    deviations = [abs(s - k) for s, k in zip(submission, key)]
    avg_deviation = sum(deviations) / len(deviations)
    
    # Score based on deviation and trend
    if trend_correct and avg_deviation <= 2:
        score = 1.0
        feedback = "Excellent forecast with correct trend and minimal deviation."
    elif trend_correct and avg_deviation <= 5:
        score = 0.8
        feedback = "Good forecast with correct trend but some deviation."
    elif trend_correct:
        score = 0.6
        feedback = "Acceptable forecast with correct trend but significant deviation."
    else:
        score = 0.3
        feedback = "Poor forecast. The trend is not maintained correctly."
    
    return score, feedback


def evaluate_accuracy_metric(submission: float, key: float) -> Tuple[float, str]:
    """Evaluate the accuracy metric (MAPE)."""
    deviation = abs(submission - key)
    
    if deviation <= 0.01:
        score = 1.0
        feedback = "Excellent MAPE calculation, very close to expected value."
    elif deviation <= 0.03:
        score = 0.8
        feedback = "Good MAPE calculation, within acceptable range."
    elif deviation <= 0.05:
        score = 0.6
        feedback = "Acceptable MAPE calculation."
    else:
        score = 0.3
        feedback = "MAPE calculation is outside the acceptable range."
    
    return score, feedback


def evaluate_cost_driver(submission: str, key: str) -> Tuple[float, str]:
    """Evaluate the identified cost driver."""
    if submission.lower() == key.lower():
        score = 1.0
        feedback = f"Correct cost driver identified: {submission}"
    elif submission.lower() == "quantity":
        score = 0.9
        feedback = "Quantity is an acceptable alternative, though weight is the more logical causal factor."
    else:
        score = 0.0
        feedback = f"Incorrect cost driver. Expected {key} or quantity."
    
    return score, feedback


def evaluate_correlation(submission: float, key: float) -> Tuple[float, str]:
    """Evaluate the correlation value."""
    deviation = abs(submission - key)
    
    if deviation <= 0.02:
        score = 1.0
        feedback = "Excellent correlation calculation, very close to expected value."
    elif deviation <= 0.05:
        score = 0.8
        feedback = "Good correlation calculation, within acceptable range."
    elif deviation <= 0.1:
        score = 0.6
        feedback = "Acceptable correlation calculation."
    else:
        score = 0.3
        feedback = "Correlation calculation is outside the acceptable range."
    
    return score, feedback


def evaluate_fixed_cost(submission: float, key: float) -> Tuple[float, str]:
    """Evaluate the fixed cost calculation."""
    deviation = abs(submission - key)
    deviation_percent = (deviation / key) * 100 if key != 0 else float('inf')
    
    if deviation <= 0:
        score = 1.0
        feedback = "Perfect fixed cost calculation."
    elif deviation_percent <= 2:
        score = 0.9
        feedback = "Very good fixed cost calculation, minimal deviation."
    elif deviation_percent <= 5:
        score = 0.7
        feedback = "Acceptable fixed cost calculation."
    else:
        score = 0.3
        feedback = "Fixed cost calculation is outside the acceptable range."
    
    return score, feedback


def evaluate_variable_cost(submission: float, key: float) -> Tuple[float, str]:
    """Evaluate the variable cost coefficient."""
    deviation = abs(submission - key)
    
    if deviation <= 0.05:
        score = 1.0
        feedback = "Excellent variable cost calculation, very close to expected value."
    elif deviation <= 0.15:
        score = 0.8
        feedback = "Good variable cost calculation, within acceptable range."
    elif deviation <= 0.3:
        score = 0.6
        feedback = "Acceptable variable cost calculation."
    else:
        score = 0.3
        feedback = "Variable cost calculation is outside the acceptable range."
    
    return score, feedback


def evaluate_total_cost(submission: float, key: float) -> Tuple[float, str]:
    """Evaluate the total estimated cost."""
    deviation_percent = (abs(submission - key) / key) * 100 if key != 0 else float('inf')
    
    if deviation_percent <= 1:
        score = 1.0
        feedback = "Excellent total cost estimation, very close to expected value."
    elif deviation_percent <= 3:
        score = 0.8
        feedback = "Good total cost estimation, within acceptable range."
    elif deviation_percent <= 5:
        score = 0.6
        feedback = "Acceptable total cost estimation."
    elif deviation_percent <= 20:
        score = 0.3
        feedback = "Total cost estimation has significant deviation."
    else:
        score = 0.0
        feedback = "Total cost estimation is critically incorrect (>20% deviation)."
    
    return score, feedback


def evaluate_cost_breakdown(submission: Dict[str, float], key: Dict[str, float]) -> Tuple[float, str]:
    """Evaluate the cost breakdown."""
    categories = ["labor", "transportation", "handling", "other"]
    deviations = []
    
    for category in categories:
        sub_value = submission.get(category, 0)
        key_value = key.get(category, 0)
        if key_value != 0:
            deviation_percent = (abs(sub_value - key_value) / key_value) * 100
            deviations.append(deviation_percent)
    
    avg_deviation = sum(deviations) / len(deviations) if deviations else float('inf')
    
    # Check if proportions are correct (labor > transportation > handling)
    correct_proportions = (
        submission.get("labor", 0) > submission.get("transportation", 0) > 
        submission.get("handling", 0)
    )
    
    if avg_deviation <= 3 and correct_proportions:
        score = 1.0
        feedback = "Excellent cost breakdown with correct proportions."
    elif avg_deviation <= 7 and correct_proportions:
        score = 0.8
        feedback = "Good cost breakdown with correct proportions."
    elif avg_deviation <= 15 and correct_proportions:
        score = 0.6
        feedback = "Acceptable cost breakdown with correct proportions."
    elif correct_proportions:
        score = 0.4
        feedback = "Cost breakdown has significant deviations but correct proportions."
    else:
        score = 0.2
        feedback = "Cost breakdown has incorrect proportions."
    
    return score, feedback


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": {},
        "task2": {},
        "scores": {},
        "overall_score": 0.0
    }
    
    # Define weights for each component
    weights = {
        "forecast_values": 15,
        "accuracy_metric": 10,
        "cost_driver": 10,
        "correlation_value": 5,
        "fixed_cost": 15,
        "variable_cost_coefficient": 15,
        "total_estimated_cost": 15,
        "cost_breakdown": 15
    }
    
    # Task 1 evaluations
    task1_sub = submission.get("task1", {})
    task1_key = answer_key.get("task1", {})
    
    # Forecast values
    score, feedback = evaluate_forecast_values(
        task1_sub.get("forecast_values", []), 
        task1_key.get("forecast_values", [])
    )
    results["task1"]["forecast_values"] = {
        "score": score,
        "feedback": feedback,
        "submission": task1_sub.get("forecast_values"),
        "expected": task1_key.get("forecast_values")
    }
    results["scores"]["forecast_values"] = score * weights["forecast_values"]
    
    # Accuracy metric
    score, feedback = evaluate_accuracy_metric(
        task1_sub.get("accuracy_metric", 0), 
        task1_key.get("accuracy_metric", 0)
    )
    results["task1"]["accuracy_metric"] = {
        "score": score,
        "feedback": feedback,
        "submission": task1_sub.get("accuracy_metric"),
        "expected": task1_key.get("accuracy_metric")
    }
    results["scores"]["accuracy_metric"] = score * weights["accuracy_metric"]
    
    # Cost driver
    score, feedback = evaluate_cost_driver(
        task1_sub.get("cost_driver", ""), 
        task1_key.get("cost_driver", "")
    )
    results["task1"]["cost_driver"] = {
        "score": score,
        "feedback": feedback,
        "submission": task1_sub.get("cost_driver"),
        "expected": task1_key.get("cost_driver")
    }
    results["scores"]["cost_driver"] = score * weights["cost_driver"]
    
    # Correlation value
    score, feedback = evaluate_correlation(
        task1_sub.get("correlation_value", 0), 
        task1_key.get("correlation_value", 0)
    )
    results["task1"]["correlation_value"] = {
        "score": score,
        "feedback": feedback,
        "submission": task1_sub.get("correlation_value"),
        "expected": task1_key.get("correlation_value")
    }
    results["scores"]["correlation_value"] = score * weights["correlation_value"]
    
    # Task 2 evaluations
    task2_sub = submission.get("task2", {})
    task2_key = answer_key.get("task2", {})
    
    # Fixed cost
    score, feedback = evaluate_fixed_cost(
        task2_sub.get("fixed_cost", 0), 
        task2_key.get("fixed_cost", 0)
    )
    results["task2"]["fixed_cost"] = {
        "score": score,
        "feedback": feedback,
        "submission": task2_sub.get("fixed_cost"),
        "expected": task2_key.get("fixed_cost")
    }
    results["scores"]["fixed_cost"] = score * weights["fixed_cost"]
    
    # Variable cost coefficient
    score, feedback = evaluate_variable_cost(
        task2_sub.get("variable_cost_coefficient", 0), 
        task2_key.get("variable_cost_coefficient", 0)
    )
    results["task2"]["variable_cost_coefficient"] = {
        "score": score,
        "feedback": feedback,
        "submission": task2_sub.get("variable_cost_coefficient"),
        "expected": task2_key.get("variable_cost_coefficient")
    }
    results["scores"]["variable_cost_coefficient"] = score * weights["variable_cost_coefficient"]
    
    # Total estimated cost
    score, feedback = evaluate_total_cost(
        task2_sub.get("total_estimated_cost", 0), 
        task2_key.get("total_estimated_cost", 0)
    )
    results["task2"]["total_estimated_cost"] = {
        "score": score,
        "feedback": feedback,
        "submission": task2_sub.get("total_estimated_cost"),
        "expected": task2_key.get("total_estimated_cost")
    }
    results["scores"]["total_estimated_cost"] = score * weights["total_estimated_cost"]
    
    # Cost breakdown
    score, feedback = evaluate_cost_breakdown(
        task2_sub.get("cost_breakdown", {}), 
        task2_key.get("cost_breakdown", {})
    )
    results["task2"]["cost_breakdown"] = {
        "score": score,
        "feedback": feedback,
        "submission": task2_sub.get("cost_breakdown"),
        "expected": task2_key.get("cost_breakdown")
    }
    results["scores"]["cost_breakdown"] = score * weights["cost_breakdown"]
    
    # Calculate overall score (percentage)
    total_points = sum(weights.values())
    earned_points = sum(results["scores"].values())
    results["overall_score"] = round((earned_points / total_points) * 100, 2)
    
    # Add overall assessment
    if results["overall_score"] >= 90:
        results["assessment"] = "Excellent (90-100%): All values within the narrow acceptable ranges."
    elif results["overall_score"] >= 75:
        results["assessment"] = "Good (75-89%): Most values correct with minor deviations in 1-2 calculations."
    elif results["overall_score"] >= 60:
        results["assessment"] = "Satisfactory (60-74%): Correct approach but with calculation errors in 3-4 values."
    else:
        results["assessment"] = "Needs Improvement (below 60%): Significant errors in methodology or calculations."
    
    # Check for critical errors (automatic failure conditions)
    critical_errors = []
    
    # Check forecast trend
    if results["task1"]["forecast_values"]["score"] < 0.4:
        critical_errors.append("Completely incorrect forecasting approach")
    
    # Check fixed/variable cost separation
    if results["task2"]["fixed_cost"]["score"] < 0.4 or results["task2"]["variable_cost_coefficient"]["score"] < 0.4:
        critical_errors.append("Failure to separate fixed and variable costs")
    
    # Check total cost estimation
    if results["task2"]["total_estimated_cost"]["score"] == 0:
        critical_errors.append("Total estimated cost off by more than 20%")
    
    if critical_errors:
        results["critical_errors"] = critical_errors
        results["assessment"] = "FAILED: " + ", ".join(critical_errors)
    
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
    print(f"Assessment: {results['assessment']}")


if __name__ == "__main__":
    main()