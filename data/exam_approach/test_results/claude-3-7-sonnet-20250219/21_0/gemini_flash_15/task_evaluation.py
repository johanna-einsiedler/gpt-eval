#!/usr/bin/env python3
"""
Administrative Services Manager Practical Exam Evaluator

This script evaluates a candidate's submission against an answer key and
generates a detailed assessment with scores for each task and an overall score.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import re
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
    """Evaluate Task 1: Review and Correct Expense Report."""
    results = {
        "score": 0,
        "max_score": 30,
        "feedback": [],
        "details": {}
    }
    
    # Check data_errors (10 points)
    sub_errors = submission.get("task1", {}).get("data_errors", [])
    key_errors = answer_key.get("task1", {}).get("data_errors", [])
    
    # Check if the candidate identified the cost per employee error
    error_identified = False
    for error in sub_errors:
        if "cost per employee" in error.lower() and "incorrect" in error.lower():
            error_identified = True
            results["score"] += 10
            results["feedback"].append("✓ Correctly identified the cost per employee calculation error")
            break
    
    if not error_identified:
        results["feedback"].append("✗ Failed to identify the cost per employee calculation error")
    
    results["details"]["data_errors"] = {
        "submitted": sub_errors,
        "expected": key_errors,
        "score": 10 if error_identified else 0,
        "max_score": 10
    }
    
    # Check total_correct_expenses (10 points)
    sub_total = submission.get("task1", {}).get("total_correct_expenses", 0)
    key_total = answer_key.get("task1", {}).get("total_correct_expenses", 0)
    
    if abs(sub_total - key_total) < 0.01:  # Allow for small floating-point differences
        results["score"] += 10
        results["feedback"].append("✓ Correctly calculated the total expenses")
    else:
        results["feedback"].append(f"✗ Incorrect total expenses: submitted {sub_total}, expected {key_total}")
    
    results["details"]["total_correct_expenses"] = {
        "submitted": sub_total,
        "expected": key_total,
        "score": 10 if abs(sub_total - key_total) < 0.01 else 0,
        "max_score": 10
    }
    
    # Check efficiency_score (10 points)
    sub_efficiency = submission.get("task1", {}).get("efficiency_score", 0)
    key_efficiency = answer_key.get("task1", {}).get("efficiency_score", 0)
    
    if sub_efficiency == key_efficiency:
        results["score"] += 10
        results["feedback"].append("✓ Correctly calculated the efficiency score")
    else:
        results["feedback"].append(f"✗ Incorrect efficiency score: submitted {sub_efficiency}, expected {key_efficiency}")
    
    results["details"]["efficiency_score"] = {
        "submitted": sub_efficiency,
        "expected": key_efficiency,
        "score": 10 if sub_efficiency == key_efficiency else 0,
        "max_score": 10
    }
    
    return results


def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Optimize Staff Scheduling."""
    results = {
        "score": 0,
        "max_score": 40,
        "feedback": [],
        "details": {}
    }
    
    # Check coverage_gaps (15 points)
    sub_gaps = submission.get("task2", {}).get("coverage_gaps", [])
    key_gaps = answer_key.get("task2", {}).get("coverage_gaps", [])
    
    # Count how many of the key gaps were identified
    gap_count = 0
    for key_gap in key_gaps:
        for sub_gap in sub_gaps:
            # Check for department and time period matches
            if (("reception" in key_gap.lower() and "reception" in sub_gap.lower() and "wednesday" in sub_gap.lower()) or
                ("finance" in key_gap.lower() and "finance" in sub_gap.lower() and "monday" in sub_gap.lower()) or
                ("hr" in key_gap.lower() and "hr" in sub_gap.lower() and ("monday" in sub_gap.lower() or "tuesday" in sub_gap.lower()))):
                gap_count += 1
                break
    
    # Score based on number of gaps identified (5 points per gap, max 15)
    gap_score = min(gap_count * 5, 15)
    results["score"] += gap_score
    
    if gap_score == 15:
        results["feedback"].append("✓ Correctly identified all coverage gaps")
    elif gap_score > 0:
        results["feedback"].append(f"⚠ Identified {gap_count} out of 3 coverage gaps")
    else:
        results["feedback"].append("✗ Failed to identify any coverage gaps correctly")
    
    results["details"]["coverage_gaps"] = {
        "submitted": sub_gaps,
        "expected": key_gaps,
        "score": gap_score,
        "max_score": 15
    }
    
    # Check optimal_staff_count (15 points)
    sub_count = submission.get("task2", {}).get("optimal_staff_count", 0)
    key_count = answer_key.get("task2", {}).get("optimal_staff_count", 0)
    
    if sub_count == key_count:
        results["score"] += 15
        results["feedback"].append("✓ Correctly determined the optimal staff count")
    else:
        results["feedback"].append(f"✗ Incorrect optimal staff count: submitted {sub_count}, expected {key_count}")
    
    results["details"]["optimal_staff_count"] = {
        "submitted": sub_count,
        "expected": key_count,
        "score": 15 if sub_count == key_count else 0,
        "max_score": 15
    }
    
    # Check schedule_conflicts (10 points)
    sub_conflicts = submission.get("task2", {}).get("schedule_conflicts", [])
    key_conflicts = answer_key.get("task2", {}).get("schedule_conflicts", [])
    
    # Count how many of the key conflicts were identified
    conflict_count = 0
    for key_conflict in key_conflicts:
        for sub_conflict in sub_conflicts:
            # Check for employee ID matches
            if (("E004" in key_conflict and "E004" in sub_conflict) or
                ("Patricia" in key_conflict and "Patricia" in sub_conflict) or
                ("E011" in key_conflict and "E011" in sub_conflict) or
                ("Joseph" in key_conflict and "Joseph" in sub_conflict)):
                conflict_count += 1
                break
    
    # Score based on number of conflicts identified (5 points per conflict, max 10)
    conflict_score = min(conflict_count * 5, 10)
    results["score"] += conflict_score
    
    if conflict_score == 10:
        results["feedback"].append("✓ Correctly identified all schedule conflicts")
    elif conflict_score > 0:
        results["feedback"].append(f"⚠ Identified {conflict_count} out of 2 schedule conflicts")
    else:
        results["feedback"].append("✗ Failed to identify any schedule conflicts correctly")
    
    results["details"]["schedule_conflicts"] = {
        "submitted": sub_conflicts,
        "expected": key_conflicts,
        "score": conflict_score,
        "max_score": 10
    }
    
    return results


def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Report Structure Analysis."""
    results = {
        "score": 0,
        "max_score": 30,
        "feedback": [],
        "details": {}
    }
    
    # Check report_frequency (10 points)
    sub_frequency = submission.get("task3", {}).get("report_frequency", "")
    key_frequency = answer_key.get("task3", {}).get("report_frequency", "")
    
    if sub_frequency.lower() == key_frequency.lower():
        results["score"] += 10
        results["feedback"].append("✓ Correctly selected the appropriate report frequency")
    else:
        results["feedback"].append(f"✗ Incorrect report frequency: submitted '{sub_frequency}', expected '{key_frequency}'")
    
    results["details"]["report_frequency"] = {
        "submitted": sub_frequency,
        "expected": key_frequency,
        "score": 10 if sub_frequency.lower() == key_frequency.lower() else 0,
        "max_score": 10
    }
    
    # Check key_metrics (10 points)
    sub_metrics = submission.get("task3", {}).get("key_metrics", [])
    key_metrics = answer_key.get("task3", {}).get("key_metrics", [])
    
    # Count how many of the key metrics were selected
    metric_matches = set(sub_metrics).intersection(set(key_metrics))
    metric_count = len(metric_matches)
    
    # Score based on number of metrics matched (2 points per metric, max 10)
    metric_score = min(metric_count * 2, 10)
    results["score"] += metric_score
    
    if metric_score == 10:
        results["feedback"].append("✓ Selected all appropriate key metrics")
    elif metric_score >= 6:
        results["feedback"].append(f"⚠ Selected {metric_count} out of 5 appropriate key metrics")
    else:
        results["feedback"].append(f"✗ Selected only {metric_count} out of 5 appropriate key metrics")
    
    results["details"]["key_metrics"] = {
        "submitted": sub_metrics,
        "expected": key_metrics,
        "matches": list(metric_matches),
        "score": metric_score,
        "max_score": 10
    }
    
    # Check selected_report_format (10 points)
    sub_format = submission.get("task3", {}).get("selected_report_format", "")
    key_format = answer_key.get("task3", {}).get("selected_report_format", "")
    
    if sub_format.lower() == key_format.lower():
        results["score"] += 10
        results["feedback"].append("✓ Correctly selected the appropriate report format")
    else:
        results["feedback"].append(f"✗ Incorrect report format: submitted '{sub_format}', expected '{key_format}'")
    
    results["details"]["selected_report_format"] = {
        "submitted": sub_format,
        "expected": key_format,
        "score": 10 if sub_format.lower() == key_format.lower() else 0,
        "max_score": 10
    }
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key),
    }
    
    # Calculate overall score
    total_score = results["task1"]["score"] + results["task2"]["score"] + results["task3"]["score"]
    total_possible = results["task1"]["max_score"] + results["task2"]["max_score"] + results["task3"]["max_score"]
    overall_percentage = round((total_score / total_possible) * 100, 2)
    
    results["overall_score"] = overall_percentage
    
    # Add performance assessment
    if overall_percentage >= 90:
        performance = "Excellent"
    elif overall_percentage >= 75:
        performance = "Good"
    elif overall_percentage >= 60:
        performance = "Satisfactory"
    else:
        performance = "Needs Improvement"
    
    results["performance_assessment"] = {
        "score": total_score,
        "max_score": total_possible,
        "percentage": overall_percentage,
        "rating": performance,
        "summary": f"The candidate scored {total_score}/{total_possible} ({overall_percentage}%), which is rated as '{performance}'."
    }
    
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
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Performance Rating: {results['performance_assessment']['rating']}")


if __name__ == "__main__":
    main()