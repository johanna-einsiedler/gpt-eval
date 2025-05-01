#!/usr/bin/env python3
"""
Biostatistician Sample Size Calculation Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
biostatistician sample size calculation exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math


def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def is_within_margin(candidate_value, correct_value, margin_percentage=5):
    """Check if a value is within the specified margin of error."""
    if isinstance(correct_value, bool):
        return candidate_value == correct_value
    
    # For numerical values
    margin = correct_value * (margin_percentage / 100)
    return abs(candidate_value - correct_value) <= margin


def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Two-Proportion Comparison."""
    results = {
        "sample_size_per_group": {
            "candidate_answer": submission["sample_size_per_group"],
            "correct_answer": answer_key["sample_size_per_group"],
            "is_correct": is_within_margin(
                submission["sample_size_per_group"], 
                answer_key["sample_size_per_group"]
            ),
            "points": 0
        },
        "total_sample_size": {
            "candidate_answer": submission["total_sample_size"],
            "correct_answer": answer_key["total_sample_size"],
            "is_correct": is_within_margin(
                submission["total_sample_size"], 
                answer_key["total_sample_size"]
            ),
            "points": 0
        },
        "power_calculation": {
            "candidate_answer": submission["power_calculation"],
            "correct_answer": answer_key["power_calculation"],
            "is_correct": is_within_margin(
                submission["power_calculation"], 
                answer_key["power_calculation"], 
                margin_percentage=8.33  # Equivalent to ±0.05 for power of 0.60
            ),
            "points": 0
        }
    }
    
    # Assign points
    for key in results:
        if results[key]["is_correct"]:
            results[key]["points"] = 1
    
    # Calculate total points
    total_points = sum(item["points"] for item in results.values())
    
    return {
        "details": results,
        "total_points": total_points,
        "max_points": 3,
        "passed_requirement": total_points >= 2
    }


def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Continuous Outcome Measure."""
    results = {
        "sample_size_per_group": {
            "candidate_answer": submission["sample_size_per_group"],
            "correct_answer": answer_key["sample_size_per_group"],
            "is_correct": is_within_margin(
                submission["sample_size_per_group"], 
                answer_key["sample_size_per_group"]
            ),
            "points": 0
        },
        "total_sample_size": {
            "candidate_answer": submission["total_sample_size"],
            "correct_answer": answer_key["total_sample_size"],
            "is_correct": is_within_margin(
                submission["total_sample_size"], 
                answer_key["total_sample_size"]
            ),
            "points": 0
        },
        "detectable_difference": {
            "candidate_answer": submission["detectable_difference"],
            "correct_answer": answer_key["detectable_difference"],
            "is_correct": is_within_margin(
                submission["detectable_difference"], 
                answer_key["detectable_difference"]
            ),
            "points": 0
        }
    }
    
    # Assign points
    for key in results:
        if results[key]["is_correct"]:
            results[key]["points"] = 1
    
    # Calculate total points
    total_points = sum(item["points"] for item in results.values())
    
    return {
        "details": results,
        "total_points": total_points,
        "max_points": 3,
        "passed_requirement": total_points >= 2
    }


def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Dropout Adjustment."""
    results = {
        "initial_sample_size": {
            "candidate_answer": submission["initial_sample_size"],
            "correct_answer": answer_key["initial_sample_size"],
            "is_correct": is_within_margin(
                submission["initial_sample_size"], 
                answer_key["initial_sample_size"]
            ),
            "points": 0
        },
        "adjusted_sample_size": {
            "candidate_answer": submission["adjusted_sample_size"],
            "correct_answer": answer_key["adjusted_sample_size"],
            "is_correct": is_within_margin(
                submission["adjusted_sample_size"], 
                answer_key["adjusted_sample_size"]
            ),
            "points": 0
        },
        "percentage_increase": {
            "candidate_answer": submission["percentage_increase"],
            "correct_answer": answer_key["percentage_increase"],
            "is_correct": abs(submission["percentage_increase"] - answer_key["percentage_increase"]) <= 1,
            "points": 0
        }
    }
    
    # Assign points
    for key in results:
        if results[key]["is_correct"]:
            results[key]["points"] = 1
    
    # Calculate total points
    total_points = sum(item["points"] for item in results.values())
    
    return {
        "details": results,
        "total_points": total_points,
        "max_points": 3,
        "passed_requirement": total_points >= 2
    }


def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Evaluating Sample Size Justifications."""
    results = {
        "scenario_a_correct": {
            "candidate_answer": submission["scenario_a_correct"],
            "correct_answer": answer_key["scenario_a_correct"],
            "is_correct": submission["scenario_a_correct"] == answer_key["scenario_a_correct"],
            "points": 0
        },
        "scenario_b_correct": {
            "candidate_answer": submission["scenario_b_correct"],
            "correct_answer": answer_key["scenario_b_correct"],
            "is_correct": submission["scenario_b_correct"] == answer_key["scenario_b_correct"],
            "points": 0
        },
        "scenario_c_correct": {
            "candidate_answer": submission["scenario_c_correct"],
            "correct_answer": answer_key["scenario_c_correct"],
            "is_correct": submission["scenario_c_correct"] == answer_key["scenario_c_correct"],
            "points": 0
        },
        "scenario_d_correct": {
            "candidate_answer": submission["scenario_d_correct"],
            "correct_answer": answer_key["scenario_d_correct"],
            "is_correct": submission["scenario_d_correct"] == answer_key["scenario_d_correct"],
            "points": 0
        }
    }
    
    # Assign points
    for key in results:
        if results[key]["is_correct"]:
            results[key]["points"] = 1
    
    # Calculate total points
    total_points = sum(item["points"] for item in results.values())
    
    return {
        "details": results,
        "total_points": total_points,
        "max_points": 4,
        "passed_requirement": total_points >= 3
    }


def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    # Evaluate each task
    task1_results = evaluate_task1(submission["task1"], answer_key["task1"])
    task2_results = evaluate_task2(submission["task2"], answer_key["task2"])
    task3_results = evaluate_task3(submission["task3"], answer_key["task3"])
    task4_results = evaluate_task4(submission["task4"], answer_key["task4"])
    
    # Calculate total points and max points
    total_points = (
        task1_results["total_points"] +
        task2_results["total_points"] +
        task3_results["total_points"] +
        task4_results["total_points"]
    )
    
    max_points = (
        task1_results["max_points"] +
        task2_results["max_points"] +
        task3_results["max_points"] +
        task4_results["max_points"]
    )
    
    # Check if all mandatory requirements are met
    all_requirements_passed = (
        task1_results["passed_requirement"] and
        task2_results["passed_requirement"] and
        task3_results["passed_requirement"] and
        task4_results["passed_requirement"]
    )
    
    # Calculate overall score as a percentage
    overall_score = (total_points / max_points) * 100
    
    # Determine if the candidate passed
    passed_exam = all_requirements_passed and total_points >= 10
    
    return {
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "task4": task4_results,
        "total_points": total_points,
        "max_points": max_points,
        "overall_score": overall_score,
        "all_requirements_passed": all_requirements_passed,
        "passed_exam": passed_exam
    }


def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed exam: {results['passed_exam']}")


if __name__ == "__main__":
    main()