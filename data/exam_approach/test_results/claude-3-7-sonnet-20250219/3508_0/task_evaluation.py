#!/usr/bin/env python3
"""
Actuarial Exam Evaluator

This script evaluates a candidate's actuarial exam submission against an answer key,
following the scoring criteria provided in the exam instructions.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any, List, Union


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def is_close(val1: float, val2: float, tolerance: float = 0.0002) -> bool:
    """Check if two float values are close within a tolerance."""
    return abs(val1 - val2) <= tolerance


def evaluate_fire_probability_table(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 1: Fire Incident Probability Table."""
    results = {
        "points_earned": 0,
        "points_possible": 35,
        "details": {}
    }
    
    # Evaluate fire probability table (20 points)
    table_points = 0
    table_details = {}
    
    sub_table = submission.get("task1", {}).get("fire_probability_table", {})
    key_table = answer_key.get("task1", {}).get("fire_probability_table", {})
    
    for property_type in key_table:
        property_points = 0
        property_max = 4
        property_details = {"correct": True, "errors": []}
        
        if property_type not in sub_table:
            property_details["correct"] = False
            property_details["errors"].append(f"Missing property type: {property_type}")
        else:
            sub_values = sub_table[property_type]
            key_values = key_table[property_type]
            
            if len(sub_values) != len(key_values):
                property_details["correct"] = False
                property_details["errors"].append(f"Expected {len(key_values)} values, got {len(sub_values)}")
            else:
                errors = 0
                for i, (sub_val, key_val) in enumerate(zip(sub_values, key_values)):
                    if not is_close(sub_val, key_val):
                        property_details["correct"] = False
                        property_details["errors"].append(f"Month {i+1}: Expected {key_val}, got {sub_val}")
                        errors += 1
                
                # Deduct 0.5 points for each incorrect value (up to 2 points per property type)
                deduction = min(errors * 0.5, 2)
                property_points = property_max - deduction
        
        table_points += property_points
        table_details[property_type] = {
            "points_earned": property_points,
            "points_possible": property_max,
            "details": property_details
        }
    
    # Evaluate highest risk property type (5 points)
    highest_risk_points = 0
    highest_risk_details = {"correct": False, "expected": "", "submitted": ""}
    
    sub_highest = submission.get("task1", {}).get("highest_risk_property_type", "")
    key_highest = answer_key.get("task1", {}).get("highest_risk_property_type", "")
    
    highest_risk_details["expected"] = key_highest
    highest_risk_details["submitted"] = sub_highest
    
    if sub_highest == key_highest:
        highest_risk_points = 5
        highest_risk_details["correct"] = True
    
    # Evaluate lowest risk property type (5 points)
    lowest_risk_points = 0
    lowest_risk_details = {"correct": False, "expected": "", "submitted": ""}
    
    sub_lowest = submission.get("task1", {}).get("lowest_risk_property_type", "")
    key_lowest = answer_key.get("task1", {}).get("lowest_risk_property_type", "")
    
    lowest_risk_details["expected"] = key_lowest
    lowest_risk_details["submitted"] = sub_lowest
    
    if sub_lowest == key_lowest:
        lowest_risk_points = 5
        lowest_risk_details["correct"] = True
    
    # Evaluate average monthly fire probability (5 points)
    avg_points = 0
    avg_details = {"correct": False, "expected": 0, "submitted": 0}
    
    sub_avg = submission.get("task1", {}).get("average_monthly_fire_probability", 0)
    key_avg = answer_key.get("task1", {}).get("average_monthly_fire_probability", 0)
    
    avg_details["expected"] = key_avg
    avg_details["submitted"] = sub_avg
    
    if is_close(sub_avg, key_avg):
        avg_points = 5
        avg_details["correct"] = True
    
    # Compile results
    results["points_earned"] = table_points + highest_risk_points + lowest_risk_points + avg_points
    results["details"] = {
        "fire_probability_table": {
            "points_earned": table_points,
            "points_possible": 20,
            "details": table_details
        },
        "highest_risk_property_type": {
            "points_earned": highest_risk_points,
            "points_possible": 5,
            "details": highest_risk_details
        },
        "lowest_risk_property_type": {
            "points_earned": lowest_risk_points,
            "points_possible": 5,
            "details": lowest_risk_details
        },
        "average_monthly_fire_probability": {
            "points_earned": avg_points,
            "points_possible": 5,
            "details": avg_details
        }
    }
    
    return results


def evaluate_disaster_probability_matrix(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 2: Natural Disaster Risk Matrix."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "details": {}
    }
    
    # Evaluate disaster probability matrix (15 points)
    matrix_points = 0
    matrix_details = {}
    
    sub_matrix = submission.get("task2", {}).get("disaster_probability_matrix", {})
    key_matrix = answer_key.get("task2", {}).get("disaster_probability_matrix", {})
    
    for region in key_matrix:
        region_points = 0
        region_max = 3.75
        region_details = {"correct": True, "errors": []}
        
        if region not in sub_matrix:
            region_details["correct"] = False
            region_details["errors"].append(f"Missing region: {region}")
        else:
            sub_values = sub_matrix[region]
            key_values = key_matrix[region]
            
            if len(sub_values) != len(key_values):
                region_details["correct"] = False
                region_details["errors"].append(f"Expected {len(key_values)} values, got {len(sub_values)}")
            else:
                errors = 0
                for i, (sub_val, key_val) in enumerate(zip(sub_values, key_values)):
                    if not is_close(sub_val, key_val):
                        region_details["correct"] = False
                        severity = ["Mild", "Moderate", "Severe"][i]
                        region_details["errors"].append(f"{severity}: Expected {key_val}, got {sub_val}")
                        errors += 1
                
                # Deduct 0.5 points for each incorrect value (up to 1.5 points per region)
                deduction = min(errors * 0.5, 1.5)
                region_points = region_max - deduction
        
        matrix_points += region_points
        matrix_details[region] = {
            "points_earned": region_points,
            "points_possible": region_max,
            "details": region_details
        }
    
    # Evaluate region with highest severe disaster probability (5 points)
    highest_severe_points = 0
    highest_severe_details = {"correct": False, "expected": "", "submitted": ""}
    
    sub_highest = submission.get("task2", {}).get("region_with_highest_severe_disaster_probability", "")
    key_highest = answer_key.get("task2", {}).get("region_with_highest_severe_disaster_probability", "")
    
    highest_severe_details["expected"] = key_highest
    highest_severe_details["submitted"] = sub_highest
    
    if sub_highest == key_highest:
        highest_severe_points = 5
        highest_severe_details["correct"] = True
    
    # Evaluate conditional probability (10 points)
    cond_prob_points = 0
    cond_prob_details = {"correct": False, "expected": 0, "submitted": 0}
    
    sub_cond_prob = submission.get("task2", {}).get("conditional_probability_severe_given_disaster", 0)
    key_cond_prob = answer_key.get("task2", {}).get("conditional_probability_severe_given_disaster", 0)
    
    cond_prob_details["expected"] = key_cond_prob
    cond_prob_details["submitted"] = sub_cond_prob
    
    if is_close(sub_cond_prob, key_cond_prob):
        cond_prob_points = 10
        cond_prob_details["correct"] = True
    
    # Compile results
    results["points_earned"] = matrix_points + highest_severe_points + cond_prob_points
    results["details"] = {
        "disaster_probability_matrix": {
            "points_earned": matrix_points,
            "points_possible": 15,
            "details": matrix_details
        },
        "region_with_highest_severe_disaster_probability": {
            "points_earned": highest_severe_points,
            "points_possible": 5,
            "details": highest_severe_details
        },
        "conditional_probability_severe_given_disaster": {
            "points_earned": cond_prob_points,
            "points_possible": 10,
            "details": cond_prob_details
        }
    }
    
    return results


def evaluate_unemployment_transition_matrix(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 3: Unemployment Transition Probability Table."""
    results = {
        "points_earned": 0,
        "points_possible": 35,
        "details": {}
    }
    
    # Evaluate unemployment transition matrix (15 points)
    matrix_points = 0
    matrix_details = {}
    
    sub_matrix = submission.get("task3", {}).get("unemployment_transition_matrix", {})
    key_matrix = answer_key.get("task3", {}).get("unemployment_transition_matrix", {})
    
    for transition in key_matrix:
        transition_points = 0
        transition_max = 3.75
        transition_details = {"correct": False, "expected": 0, "submitted": 0}
        
        if transition not in sub_matrix:
            transition_details["expected"] = key_matrix[transition]
            transition_details["submitted"] = "Missing"
        else:
            sub_val = sub_matrix[transition]
            key_val = key_matrix[transition]
            
            transition_details["expected"] = key_val
            transition_details["submitted"] = sub_val
            
            if is_close(sub_val, key_val):
                transition_points = transition_max
                transition_details["correct"] = True
            else:
                # Deduct 1 point for each incorrect value
                transition_points = max(0, transition_max - 1)
        
        matrix_points += transition_points
        matrix_details[transition] = {
            "points_earned": transition_points,
            "points_possible": transition_max,
            "details": transition_details
        }
    
    # Evaluate probability remain unemployed (5 points)
    remain_points = 0
    remain_details = {"correct": False, "expected": 0, "submitted": 0}
    
    sub_remain = submission.get("task3", {}).get("probability_remain_unemployed", 0)
    key_remain = answer_key.get("task3", {}).get("probability_remain_unemployed", 0)
    
    remain_details["expected"] = key_remain
    remain_details["submitted"] = sub_remain
    
    if is_close(sub_remain, key_remain):
        remain_points = 5
        remain_details["correct"] = True
    
    # Evaluate expected unemployment duration (10 points)
    duration_points = 0
    duration_details = {"correct": False, "expected": 0, "submitted": 0}
    
    sub_duration = submission.get("task3", {}).get("expected_unemployment_duration", 0)
    key_duration = answer_key.get("task3", {}).get("expected_unemployment_duration", 0)
    
    duration_details["expected"] = key_duration
    duration_details["submitted"] = sub_duration
    
    if is_close(sub_duration, key_duration):
        duration_points = 10
        duration_details["correct"] = True
    
    # Evaluate demographic with highest recovery rate (5 points)
    demographic_points = 0
    demographic_details = {"correct": False, "expected": "", "submitted": ""}
    
    sub_demographic = submission.get("task3", {}).get("demographic_highest_recovery_rate", "")
    key_demographic = answer_key.get("task3", {}).get("demographic_highest_recovery_rate", "")
    
    demographic_details["expected"] = key_demographic
    demographic_details["submitted"] = sub_demographic
    
    if sub_demographic == key_demographic:
        demographic_points = 5
        demographic_details["correct"] = True
    
    # Compile results
    results["points_earned"] = matrix_points + remain_points + duration_points + demographic_points
    results["details"] = {
        "unemployment_transition_matrix": {
            "points_earned": matrix_points,
            "points_possible": 15,
            "details": matrix_details
        },
        "probability_remain_unemployed": {
            "points_earned": remain_points,
            "points_possible": 5,
            "details": remain_details
        },
        "expected_unemployment_duration": {
            "points_earned": duration_points,
            "points_possible": 10,
            "details": duration_details
        },
        "demographic_highest_recovery_rate": {
            "points_earned": demographic_points,
            "points_possible": 5,
            "details": demographic_details
        }
    }
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "total_points_earned": 0,
        "total_points_possible": 100,
        "passed": False,
        "tasks": {}
    }
    
    # Evaluate Task 1
    task1_results = evaluate_fire_probability_table(submission, answer_key)
    results["tasks"]["task1"] = task1_results
    
    # Evaluate Task 2
    task2_results = evaluate_disaster_probability_matrix(submission, answer_key)
    results["tasks"]["task2"] = task2_results
    
    # Evaluate Task 3
    task3_results = evaluate_unemployment_transition_matrix(submission, answer_key)
    results["tasks"]["task3"] = task3_results
    
    # Calculate total points earned
    total_points_earned = (
        task1_results["points_earned"] +
        task2_results["points_earned"] +
        task3_results["points_earned"]
    )
    results["total_points_earned"] = total_points_earned
    
    # Calculate overall score as a percentage
    overall_score = (total_points_earned / results["total_points_possible"]) * 100
    results["overall_score"] = round(overall_score, 2)
    
    # Determine if the candidate passed
    passed_overall = overall_score >= 70
    passed_task1 = task1_results["points_earned"] >= 25
    passed_task2 = task2_results["points_earned"] >= 20
    passed_task3 = task3_results["points_earned"] >= 25
    
    results["passed"] = passed_overall and passed_task1 and passed_task2 and passed_task3
    
    # Add pass/fail details for each task
    results["tasks"]["task1"]["passed"] = passed_task1
    results["tasks"]["task2"]["passed"] = passed_task2
    results["tasks"]["task3"]["passed"] = passed_task3
    
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
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()