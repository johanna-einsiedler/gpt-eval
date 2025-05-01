#!/usr/bin/env python3
"""
Budget Analysis Practical Examination Evaluator

This script evaluates a candidate's budget analysis test submission against an answer key.
It scores each task according to the evaluation criteria and generates a detailed results file.

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


def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Budget Variance Analysis."""
    results = {
        "variances": {"correct": 0, "total": 10, "details": {}},
        "variance_percentages": {"correct": 0, "total": 10, "details": {}},
        "largest_overruns": {"correct": 0, "total": 3, "details": {}},
        "passed": False
    }
    
    # Check variances
    for category in answer_key["task1"]["variances"]:
        expected = answer_key["task1"]["variances"][category]
        actual = submission.get("task1", {}).get("variances", {}).get(category)
        
        is_correct = actual is not None and math.isclose(actual, expected, abs_tol=0.01)
        results["variances"]["details"][category] = {
            "expected": expected,
            "submitted": actual,
            "correct": is_correct
        }
        if is_correct:
            results["variances"]["correct"] += 1
    
    # Check variance percentages
    for category in answer_key["task1"]["variance_percentages"]:
        expected = answer_key["task1"]["variance_percentages"][category]
        actual = submission.get("task1", {}).get("variance_percentages", {}).get(category)
        
        is_correct = actual is not None and math.isclose(actual, expected, abs_tol=0.1)
        results["variance_percentages"]["details"][category] = {
            "expected": expected,
            "submitted": actual,
            "correct": is_correct
        }
        if is_correct:
            results["variance_percentages"]["correct"] += 1
    
    # Check largest overruns
    expected_overruns = answer_key["task1"]["largest_overruns"]
    actual_overruns = submission.get("task1", {}).get("largest_overruns", [])
    
    for i, expected_item in enumerate(expected_overruns):
        is_correct = (i < len(actual_overruns) and actual_overruns[i] == expected_item)
        results["largest_overruns"]["details"][f"item_{i+1}"] = {
            "expected": expected_item,
            "submitted": actual_overruns[i] if i < len(actual_overruns) else None,
            "correct": is_correct
        }
        if is_correct:
            results["largest_overruns"]["correct"] += 1
    
    # Determine if task is passed
    variances_passed = results["variances"]["correct"] >= 8
    percentages_passed = results["variance_percentages"]["correct"] >= 8
    overruns_passed = results["largest_overruns"]["correct"] >= 2
    
    results["passed"] = variances_passed and percentages_passed and overruns_passed
    
    return results


def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Budget Summary Creation."""
    results = {
        "total_budget": {"correct": False, "details": {}},
        "department_percentages": {"correct": 0, "total": 4, "details": {}},
        "highest_personnel_department": {"correct": False, "details": {}},
        "passed": False
    }
    
    # Check total budget
    expected_budget = answer_key["task2"]["total_budget"]
    actual_budget = submission.get("task2", {}).get("total_budget")
    
    budget_correct = actual_budget is not None and math.isclose(actual_budget, expected_budget, abs_tol=0.01)
    results["total_budget"]["details"] = {
        "expected": expected_budget,
        "submitted": actual_budget,
        "correct": budget_correct
    }
    results["total_budget"]["correct"] = budget_correct
    
    # Check department percentages
    for dept in answer_key["task2"]["department_percentages"]:
        expected = answer_key["task2"]["department_percentages"][dept]
        actual = submission.get("task2", {}).get("department_percentages", {}).get(dept)
        
        is_correct = actual is not None and math.isclose(actual, expected, abs_tol=0.1)
        results["department_percentages"]["details"][dept] = {
            "expected": expected,
            "submitted": actual,
            "correct": is_correct
        }
        if is_correct:
            results["department_percentages"]["correct"] += 1
    
    # Check highest personnel department
    expected_dept = answer_key["task2"]["highest_personnel_department"]
    actual_dept = submission.get("task2", {}).get("highest_personnel_department")
    
    dept_correct = actual_dept == expected_dept
    results["highest_personnel_department"]["details"] = {
        "expected": expected_dept,
        "submitted": actual_dept,
        "correct": dept_correct
    }
    results["highest_personnel_department"]["correct"] = dept_correct
    
    # Determine if task is passed
    budget_passed = results["total_budget"]["correct"]
    percentages_passed = results["department_percentages"]["correct"] >= 3
    dept_passed = results["highest_personnel_department"]["correct"]
    
    results["passed"] = budget_passed and percentages_passed and dept_passed
    
    return results


def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Fund Request Evaluation."""
    results = {
        "request_decisions": {"correct": 0, "total": 5, "details": {}},
        "guideline_references": {"correct": 0, "total": 5, "details": {}},
        "passed": False
    }
    
    # Check request decisions
    for req_id in answer_key["task3"]["request_decisions"]:
        expected = answer_key["task3"]["request_decisions"][req_id]
        actual = submission.get("task3", {}).get("request_decisions", {}).get(req_id)
        
        is_correct = actual == expected
        results["request_decisions"]["details"][req_id] = {
            "expected": expected,
            "submitted": actual,
            "correct": is_correct
        }
        if is_correct:
            results["request_decisions"]["correct"] += 1
    
    # Check guideline references
    for req_id in answer_key["task3"]["guideline_references"]:
        expected = answer_key["task3"]["guideline_references"][req_id]
        actual = submission.get("task3", {}).get("guideline_references", {}).get(req_id)
        
        is_correct = actual == expected
        results["guideline_references"]["details"][req_id] = {
            "expected": expected,
            "submitted": actual,
            "correct": is_correct
        }
        if is_correct:
            results["guideline_references"]["correct"] += 1
    
    # Determine if task is passed
    decisions_passed = results["request_decisions"]["correct"] >= 4
    guidelines_passed = results["guideline_references"]["correct"] >= 3
    
    results["passed"] = decisions_passed and guidelines_passed
    
    return results


def calculate_overall_score(task_results: Dict) -> float:
    """Calculate the overall score as a percentage."""
    total_points = 0
    earned_points = 0
    
    # Task 1 (10 variances + 10 percentages + 3 largest overruns = 23 points)
    total_points += 23
    earned_points += task_results["task1"]["variances"]["correct"]
    earned_points += task_results["task1"]["variance_percentages"]["correct"]
    earned_points += task_results["task1"]["largest_overruns"]["correct"]
    
    # Task 2 (1 total budget + 4 department percentages + 1 highest personnel = 6 points)
    total_points += 6
    earned_points += 1 if task_results["task2"]["total_budget"]["correct"] else 0
    earned_points += task_results["task2"]["department_percentages"]["correct"]
    earned_points += 1 if task_results["task2"]["highest_personnel_department"]["correct"] else 0
    
    # Task 3 (5 request decisions + 5 guideline references = 10 points)
    total_points += 10
    earned_points += task_results["task3"]["request_decisions"]["correct"]
    earned_points += task_results["task3"]["guideline_references"]["correct"]
    
    return round((earned_points / total_points) * 100, 1)


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Count passed tasks
    tasks_passed = sum([
        1 if task1_results["passed"] else 0,
        1 if task2_results["passed"] else 0,
        1 if task3_results["passed"] else 0
    ])
    
    # Calculate overall score
    overall_score = calculate_overall_score({
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    })
    
    # Determine if exam is passed (at least 2 out of 3 tasks passed)
    passed = tasks_passed >= 2
    
    return {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "tasks_passed": tasks_passed,
        "total_tasks": 3,
        "overall_score": overall_score,
        "passed": passed
    }


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
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Exam {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()