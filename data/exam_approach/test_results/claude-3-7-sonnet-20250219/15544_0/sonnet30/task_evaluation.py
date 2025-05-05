#!/usr/bin/env python3
"""
Fitness and Wellness Coordinator Practical Exam Evaluator

This script evaluates a candidate's submission against the answer key and
generates a detailed report of their performance.

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


def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Data Organization and Basic Tracking."""
    results = {
        "total_participants_per_event": {
            "score": 0,
            "max_score": 5,
            "details": {}
        },
        "attendance_rates": {
            "score": 0,
            "max_score": 5,
            "details": {}
        }
    }
    
    # Evaluate total participants per event
    sub_totals = submission.get("task1", {}).get("total_participants_per_event", {})
    key_totals = answer_key.get("task1", {}).get("total_participants_per_event", {})
    
    for event_id, correct_value in key_totals.items():
        submitted_value = sub_totals.get(event_id)
        is_correct = submitted_value == correct_value
        
        results["total_participants_per_event"]["details"][event_id] = {
            "submitted": submitted_value,
            "correct": correct_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            results["total_participants_per_event"]["score"] += 1
    
    # Evaluate attendance rates
    sub_rates = submission.get("task1", {}).get("attendance_rates", {})
    key_rates = answer_key.get("task1", {}).get("attendance_rates", {})
    
    for event_id, correct_value in key_rates.items():
        submitted_value = sub_rates.get(event_id)
        
        # Check if value is within ±2% for partial credit
        is_correct = submitted_value == correct_value
        is_close = False
        if not is_correct and submitted_value is not None:
            is_close = abs(submitted_value - correct_value) <= 0.02
        
        results["attendance_rates"]["details"][event_id] = {
            "submitted": submitted_value,
            "correct": correct_value,
            "is_correct": is_correct,
            "is_close": is_close
        }
        
        if is_correct:
            results["attendance_rates"]["score"] += 1
        elif is_close:
            results["attendance_rates"]["score"] += 0.5
    
    return results


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Participation Analysis."""
    results = {
        "score": 0,
        "max_score": 4,
        "details": {}
    }
    
    sub_task2 = submission.get("task2", {})
    key_task2 = answer_key.get("task2", {})
    
    # Evaluate highest attendance event
    submitted_event = sub_task2.get("highest_attendance_event")
    correct_event = key_task2.get("highest_attendance_event")
    is_correct_event = submitted_event == correct_event
    
    results["details"]["highest_attendance_event"] = {
        "submitted": submitted_event,
        "correct": correct_event,
        "is_correct": is_correct_event
    }
    
    if is_correct_event:
        results["score"] += 1
    
    # Evaluate average attendance rate
    submitted_rate = sub_task2.get("average_attendance_rate")
    correct_rate = key_task2.get("average_attendance_rate")
    
    is_correct_rate = submitted_rate == correct_rate
    is_close_rate = False
    if not is_correct_rate and submitted_rate is not None:
        is_close_rate = abs(submitted_rate - correct_rate) <= 0.02
    
    results["details"]["average_attendance_rate"] = {
        "submitted": submitted_rate,
        "correct": correct_rate,
        "is_correct": is_correct_rate,
        "is_close": is_close_rate
    }
    
    if is_correct_rate:
        results["score"] += 1
    elif is_close_rate:
        results["score"] += 0.5
    
    # Evaluate highest participation week
    submitted_week = sub_task2.get("highest_participation_week")
    correct_week = key_task2.get("highest_participation_week")
    is_correct_week = submitted_week == correct_week
    
    results["details"]["highest_participation_week"] = {
        "submitted": submitted_week,
        "correct": correct_week,
        "is_correct": is_correct_week
    }
    
    if is_correct_week:
        results["score"] += 1
    
    # Evaluate highest participation department
    submitted_dept = sub_task2.get("highest_participation_department")
    correct_dept = key_task2.get("highest_participation_department")
    is_correct_dept = submitted_dept == correct_dept
    
    results["details"]["highest_participation_department"] = {
        "submitted": submitted_dept,
        "correct": correct_dept,
        "is_correct": is_correct_dept
    }
    
    if is_correct_dept:
        results["score"] += 1
    
    return results


def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Trend Identification."""
    results = {
        "week_over_week_changes": {
            "score": 0,
            "max_score": 5,  # One point per event
            "details": {}
        },
        "most_consistent_event": {
            "score": 0,
            "max_score": 1,
            "details": {}
        },
        "age_group_with_highest_attendance": {
            "score": 0,
            "max_score": 1,
            "details": {}
        }
    }
    
    sub_task3 = submission.get("task3", {})
    key_task3 = answer_key.get("task3", {})
    
    # Evaluate week-over-week changes
    sub_changes = sub_task3.get("week_over_week_changes", {})
    key_changes = key_task3.get("week_over_week_changes", {})
    
    for event_id, correct_values in key_changes.items():
        submitted_values = sub_changes.get(event_id, [])
        event_score = 0
        event_max_score = len(correct_values)
        details = []
        
        for i, correct_value in enumerate(correct_values):
            if i < len(submitted_values):
                submitted_value = submitted_values[i]
                
                # Check if value is correct or within ±5% for partial credit
                is_correct = abs(submitted_value - correct_value) < 0.001  # Account for floating point precision
                is_close = False
                correct_direction = False
                
                if not is_correct and submitted_value is not None:
                    is_close = abs(submitted_value - correct_value) <= 0.05
                    # Check if the direction (sign) is correct
                    correct_direction = (submitted_value > 0 and correct_value > 0) or \
                                        (submitted_value < 0 and correct_value < 0) or \
                                        (abs(submitted_value) < 0.001 and abs(correct_value) < 0.001)
                
                details.append({
                    "week": i + 2,  # Week 2 is the first change (compared to Week 1)
                    "submitted": submitted_value,
                    "correct": correct_value,
                    "is_correct": is_correct,
                    "is_close": is_close,
                    "correct_direction": correct_direction
                })
                
                if is_correct:
                    event_score += 1
                elif is_close and correct_direction:
                    event_score += 0.5
                elif correct_direction:
                    event_score += 0.25
            else:
                details.append({
                    "week": i + 2,
                    "submitted": None,
                    "correct": correct_value,
                    "is_correct": False,
                    "is_close": False,
                    "correct_direction": False
                })
        
        # Calculate percentage score for this event's changes
        event_percentage = event_score / event_max_score if event_max_score > 0 else 0
        
        results["week_over_week_changes"]["details"][event_id] = {
            "score": event_score,
            "max_score": event_max_score,
            "percentage": event_percentage,
            "details": details
        }
        
        # Add to overall week-over-week score (max 1 point per event)
        results["week_over_week_changes"]["score"] += min(1, event_percentage)
    
    # Evaluate most consistent event
    submitted_event = sub_task3.get("most_consistent_event")
    correct_event = key_task3.get("most_consistent_event")
    is_correct_event = submitted_event == correct_event
    
    results["most_consistent_event"]["details"] = {
        "submitted": submitted_event,
        "correct": correct_event,
        "is_correct": is_correct_event
    }
    
    if is_correct_event:
        results["most_consistent_event"]["score"] = 1
    
    # Evaluate age group with highest attendance
    submitted_age = sub_task3.get("age_group_with_highest_attendance")
    correct_age = key_task3.get("age_group_with_highest_attendance")
    is_correct_age = submitted_age == correct_age
    
    results["age_group_with_highest_attendance"]["details"] = {
        "submitted": submitted_age,
        "correct": correct_age,
        "is_correct": is_correct_age
    }
    
    if is_correct_age:
        results["age_group_with_highest_attendance"]["score"] = 1
    
    return results


def check_critical_elements(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Check if critical elements are correct."""
    critical_elements = {
        "attendance_rates_threshold": {
            "required": 3,
            "achieved": 0,
            "max": 5,
            "passed": False
        },
        "highest_attendance_event": {
            "required": 1,
            "achieved": 0,
            "max": 1,
            "passed": False
        },
        "json_format": {
            "required": 1,
            "achieved": 1,  # Assume format is correct if we got this far
            "max": 1,
            "passed": True
        }
    }
    
    # Check attendance rates
    attendance_correct = 0
    for event_details in evaluation["task1"]["attendance_rates"]["details"].values():
        if event_details["is_correct"]:
            attendance_correct += 1
    
    critical_elements["attendance_rates_threshold"]["achieved"] = attendance_correct
    critical_elements["attendance_rates_threshold"]["passed"] = attendance_correct >= critical_elements["attendance_rates_threshold"]["required"]
    
    # Check highest attendance event
    highest_event_correct = evaluation["task2"]["details"]["highest_attendance_event"]["is_correct"]
    critical_elements["highest_attendance_event"]["achieved"] = 1 if highest_event_correct else 0
    critical_elements["highest_attendance_event"]["passed"] = highest_event_correct
    
    # Overall critical elements check
    all_critical_passed = all(element["passed"] for element in critical_elements.values())
    
    return {
        "details": critical_elements,
        "all_passed": all_critical_passed
    }


def calculate_overall_score(evaluation: Dict[str, Any]) -> Tuple[float, float, float]:
    """Calculate the overall score as a percentage."""
    total_score = 0
    max_score = 0
    
    # Task 1 scores
    total_score += evaluation["task1"]["total_participants_per_event"]["score"]
    max_score += evaluation["task1"]["total_participants_per_event"]["max_score"]
    
    total_score += evaluation["task1"]["attendance_rates"]["score"]
    max_score += evaluation["task1"]["attendance_rates"]["max_score"]
    
    # Task 2 scores
    total_score += evaluation["task2"]["score"]
    max_score += evaluation["task2"]["max_score"]
    
    # Task 3 scores
    total_score += evaluation["task3"]["week_over_week_changes"]["score"]
    max_score += evaluation["task3"]["week_over_week_changes"]["max_score"]
    
    total_score += evaluation["task3"]["most_consistent_event"]["score"]
    max_score += evaluation["task3"]["most_consistent_event"]["max_score"]
    
    total_score += evaluation["task3"]["age_group_with_highest_attendance"]["score"]
    max_score += evaluation["task3"]["age_group_with_highest_attendance"]["max_score"]
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    return total_score, max_score, percentage


def check_passing_criteria(evaluation: Dict[str, Any], overall_percentage: float) -> Dict[str, Any]:
    """Check if the candidate meets the passing criteria."""
    # Minimum requirements for each task
    task1_correct = (evaluation["task1"]["total_participants_per_event"]["score"] + 
                     evaluation["task1"]["attendance_rates"]["score"])
    task1_max = (evaluation["task1"]["total_participants_per_event"]["max_score"] + 
                 evaluation["task1"]["attendance_rates"]["max_score"])
    task1_passed = task1_correct >= 8
    
    task2_correct = evaluation["task2"]["score"]
    task2_max = evaluation["task2"]["max_score"]
    task2_passed = task2_correct >= 3
    
    task3_correct = (evaluation["task3"]["week_over_week_changes"]["score"] + 
                     evaluation["task3"]["most_consistent_event"]["score"] + 
                     evaluation["task3"]["age_group_with_highest_attendance"]["score"])
    task3_max = (evaluation["task3"]["week_over_week_changes"]["max_score"] + 
                 evaluation["task3"]["most_consistent_event"]["max_score"] + 
                 evaluation["task3"]["age_group_with_highest_attendance"]["max_score"])
    task3_passed = task3_correct >= 7
    
    # Overall score requirement
    overall_passed = overall_percentage >= 75
    
    # Critical elements check
    critical_elements_passed = evaluation["critical_elements"]["all_passed"]
    
    # Final determination
    passed = task1_passed and task2_passed and task3_passed and overall_passed and critical_elements_passed
    
    return {
        "task1": {
            "required": 8,
            "achieved": task1_correct,
            "max": task1_max,
            "passed": task1_passed
        },
        "task2": {
            "required": 3,
            "achieved": task2_correct,
            "max": task2_max,
            "passed": task2_passed
        },
        "task3": {
            "required": 7,
            "achieved": task3_correct,
            "max": task3_max,
            "passed": task3_passed
        },
        "overall_score": {
            "required": 75,
            "achieved": overall_percentage,
            "passed": overall_passed
        },
        "critical_elements": {
            "passed": critical_elements_passed
        },
        "final_result": passed
    }


def main():
    """Main function to evaluate the candidate's submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    evaluation = {
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key)
    }
    
    # Check critical elements
    evaluation["critical_elements"] = check_critical_elements(evaluation)
    
    # Calculate overall score
    total_score, max_score, percentage = calculate_overall_score(evaluation)
    evaluation["overall_score"] = percentage
    
    # Check passing criteria
    evaluation["passing_criteria"] = check_passing_criteria(evaluation, percentage)
    
    # Add candidate ID if available
    if "candidate_id" in submission:
        evaluation["candidate_id"] = submission["candidate_id"]
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(evaluation, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {percentage:.2f}% ({total_score}/{max_score})")
    print(f"Result: {'PASS' if evaluation['passing_criteria']['final_result'] else 'FAIL'}")


if __name__ == "__main__":
    main()