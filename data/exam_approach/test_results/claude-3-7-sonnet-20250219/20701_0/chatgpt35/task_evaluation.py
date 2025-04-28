#!/usr/bin/env python3
"""
Task Evaluation Script for General and Operations Manager Practical Exam
"""

import json
import sys
import os
from typing import Dict, Any, List, Tuple


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_labor_metrics(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the labor hours and cost calculations."""
    metrics_score = 0.0
    metrics_details = {}
    
    # Check total labor hours (within ±5%)
    expected_hours = answer_key["total_labor_hours"]
    submitted_hours = submission.get("total_labor_hours", 0)
    hours_diff_percent = abs(submitted_hours - expected_hours) / expected_hours * 100
    hours_score = 5.0 if hours_diff_percent <= 5.0 else (5.0 - min(5.0, hours_diff_percent - 5.0))
    
    metrics_details["labor_hours"] = {
        "submitted": submitted_hours,
        "expected": expected_hours,
        "difference_percent": round(hours_diff_percent, 2),
        "score": round(hours_score, 2),
        "max_score": 5.0
    }
    
    # Check total labor cost (within ±5%)
    expected_cost = answer_key["total_labor_cost"]
    submitted_cost = submission.get("total_labor_cost", 0)
    cost_diff_percent = abs(submitted_cost - expected_cost) / expected_cost * 100
    cost_score = 5.0 if cost_diff_percent <= 5.0 else (5.0 - min(5.0, cost_diff_percent - 5.0))
    
    metrics_details["labor_cost"] = {
        "submitted": submitted_cost,
        "expected": expected_cost,
        "difference_percent": round(cost_diff_percent, 2),
        "score": round(cost_score, 2),
        "max_score": 5.0
    }
    
    metrics_score = hours_score + cost_score
    return metrics_score, metrics_details


def evaluate_department_coverage(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the department coverage percentages."""
    coverage_score = 0.0
    coverage_details = {}
    
    submitted_coverage = submission.get("department_coverage", {})
    expected_coverage = answer_key["department_coverage"]
    
    total_points = 0
    max_points = 50.0  # 50% of total score for schedule completeness and compliance
    
    for dept in ["department_A", "department_B", "department_C"]:
        submitted_value = submitted_coverage.get(dept, 0)
        expected_value = expected_coverage.get(dept, 100)
        
        # Calculate points based on coverage percentage
        # Must have at least 90% coverage to pass
        if submitted_value >= 90:
            dept_score = (submitted_value / 100) * (max_points / 3)
        else:
            dept_score = (submitted_value / 90) * (max_points / 3) * 0.8  # Significant penalty below 90%
        
        total_points += dept_score
        
        coverage_details[dept] = {
            "submitted": submitted_value,
            "expected": expected_value,
            "score": round(dept_score, 2),
            "max_score": round(max_points / 3, 2)
        }
    
    coverage_score = total_points
    return coverage_score, coverage_details


def evaluate_conflict_resolutions(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the conflict resolution choices."""
    conflict_score = 0.0
    conflict_details = {}
    
    submitted_resolutions = submission.get("conflict_resolutions", {})
    expected_resolutions = answer_key["conflict_resolutions"]
    
    max_points = 15.0  # 15% of total score for conflict resolutions
    points_per_conflict = max_points / 3
    
    correct_count = 0
    
    for conflict in ["conflict_1", "conflict_2", "conflict_3"]:
        submitted_value = submitted_resolutions.get(conflict, "")
        expected_value = expected_resolutions.get(conflict, "")
        
        is_correct = submitted_value.upper() == expected_value.upper()
        if is_correct:
            correct_count += 1
        
        conflict_details[conflict] = {
            "submitted": submitted_value,
            "expected": expected_value,
            "correct": is_correct,
            "score": points_per_conflict if is_correct else 0,
            "max_score": points_per_conflict
        }
    
    conflict_score = correct_count * points_per_conflict
    
    # Add a summary of correct conflicts
    conflict_details["summary"] = {
        "correct_count": correct_count,
        "total_count": 3,
        "passed_minimum": correct_count >= 2  # At least 2 of 3 must be correct
    }
    
    return conflict_score, conflict_details


def evaluate_duty_allocation(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the duty allocations."""
    duty_score = 0.0
    duty_details = {}
    
    submitted_duties = submission.get("duty_allocation", {})
    expected_duties = answer_key["duty_allocation"]
    
    max_points = 25.0  # 25% of total score for duty allocation
    points_per_duty = max_points / 3
    
    total_correct_assignments = 0
    total_expected_assignments = 0
    
    for duty in ["duty_1", "duty_2", "duty_3"]:
        submitted_value = submitted_duties.get(duty, "")
        expected_value = expected_duties.get(duty, "")
        
        # Parse the employee IDs
        submitted_ids = set(submitted_value.split(",")) if submitted_value else set()
        expected_ids = set(expected_value.split(",")) if expected_value else set()
        
        # Count correct assignments
        correct_assignments = len(submitted_ids.intersection(expected_ids))
        total_assignments = len(expected_ids)
        
        total_correct_assignments += correct_assignments
        total_expected_assignments += total_assignments
        
        # Calculate score based on percentage of correct assignments
        if total_assignments > 0:
            duty_percent_correct = correct_assignments / total_assignments
        else:
            duty_percent_correct = 0
            
        duty_points = points_per_duty * duty_percent_correct
        
        duty_details[duty] = {
            "submitted": submitted_value,
            "expected": expected_value,
            "correct_assignments": correct_assignments,
            "total_assignments": total_assignments,
            "percent_correct": round(duty_percent_correct * 100, 2),
            "score": round(duty_points, 2),
            "max_score": points_per_duty
        }
    
    # Calculate overall duty allocation score
    overall_percent_correct = (total_correct_assignments / total_expected_assignments) if total_expected_assignments > 0 else 0
    duty_score = sum(detail["score"] for detail in duty_details.values())
    
    # Add a summary of duty allocation
    duty_details["summary"] = {
        "overall_percent_correct": round(overall_percent_correct * 100, 2),
        "passed_minimum": overall_percent_correct >= 0.8  # At least 80% of duty assignments must be optimal
    }
    
    return duty_score, duty_details


def calculate_overall_score(scores: Dict[str, float]) -> float:
    """Calculate the overall score as a percentage."""
    total_points = sum(scores.values())
    max_points = 100.0  # Total possible points
    return (total_points / max_points) * 100


def main():
    """Main function to evaluate the candidate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate each section
    metrics_score, metrics_details = evaluate_labor_metrics(submission, answer_key)
    coverage_score, coverage_details = evaluate_department_coverage(submission, answer_key)
    conflict_score, conflict_details = evaluate_conflict_resolutions(submission, answer_key)
    duty_score, duty_details = evaluate_duty_allocation(submission, answer_key)
    
    # Compile scores
    scores = {
        "labor_metrics": metrics_score,
        "department_coverage": coverage_score,
        "conflict_resolutions": conflict_score,
        "duty_allocation": duty_score
    }
    
    # Calculate overall score
    overall_score = calculate_overall_score(scores)
    passed = overall_score >= 75.0  # Minimum passing score is 75%
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "section_scores": {
            "labor_metrics": round(metrics_score, 2),
            "department_coverage": round(coverage_score, 2),
            "conflict_resolutions": round(conflict_score, 2),
            "duty_allocation": round(duty_score, 2)
        },
        "details": {
            "labor_metrics": metrics_details,
            "department_coverage": coverage_details,
            "conflict_resolutions": conflict_details,
            "duty_allocation": duty_details
        }
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}% - {'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()