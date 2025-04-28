#!/usr/bin/env python3
"""
Credit Analysis Practical Examination Evaluator

This script evaluates a candidate's submission for the Credit Analysis Practical Examination
by comparing it against an answer key and generating a detailed score report.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any, Tuple


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_task1(submission: Dict[str, float], answer_key: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate Task 1: Financial Ratio Calculation
    
    Each correct ratio is worth 2.5 points.
    Partial credit (1 point) if within ±0.05 of the correct value.
    """
    max_points = 25
    points_per_ratio = 2.5
    
    total_points = 0
    details = {}
    
    for key, correct_value in answer_key.items():
        submitted_value = submission.get(key, None)
        
        if submitted_value is None:
            details[key] = {
                "submitted": None,
                "correct": correct_value,
                "points": 0,
                "max_points": points_per_ratio,
                "comment": "Missing value"
            }
        elif abs(submitted_value - correct_value) <= 0.05:
            # Full credit if exact or very close
            if abs(submitted_value - correct_value) <= 0.01:
                details[key] = {
                    "submitted": submitted_value,
                    "correct": correct_value,
                    "points": points_per_ratio,
                    "max_points": points_per_ratio,
                    "comment": "Correct"
                }
                total_points += points_per_ratio
            # Partial credit if within tolerance
            else:
                details[key] = {
                    "submitted": submitted_value,
                    "correct": correct_value,
                    "points": 1.0,
                    "max_points": points_per_ratio,
                    "comment": "Close to correct value (within ±0.05)"
                }
                total_points += 1.0
        else:
            details[key] = {
                "submitted": submitted_value,
                "correct": correct_value,
                "points": 0,
                "max_points": points_per_ratio,
                "comment": "Incorrect"
            }
    
    return total_points, details


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate Task 2: Cash Flow Analysis
    
    - Operating Cash Flow calculation: 8 points
    - Free Cash Flow calculation: 7 points
    - Cash Flow to Debt Ratio calculation: 5 points
    - Cash Flow Sufficiency determination: 5 points
    """
    total_points = 0
    details = {}
    
    # Operating Cash Flow (8 points)
    ocf_key = "operating_cash_flow_2023"
    ocf_max_points = 8
    ocf_submitted = submission.get(ocf_key)
    ocf_correct = answer_key.get(ocf_key)
    
    if ocf_submitted is not None:
        # Allow for some rounding differences
        if abs(ocf_submitted - ocf_correct) <= 1000:
            details[ocf_key] = {
                "submitted": ocf_submitted,
                "correct": ocf_correct,
                "points": ocf_max_points,
                "max_points": ocf_max_points,
                "comment": "Correct"
            }
            total_points += ocf_max_points
        # Partial credit for close answers
        elif abs(ocf_submitted - ocf_correct) <= 50000:
            partial_points = ocf_max_points * 0.5
            details[ocf_key] = {
                "submitted": ocf_submitted,
                "correct": ocf_correct,
                "points": partial_points,
                "max_points": ocf_max_points,
                "comment": "Close but not exact"
            }
            total_points += partial_points
        else:
            details[ocf_key] = {
                "submitted": ocf_submitted,
                "correct": ocf_correct,
                "points": 0,
                "max_points": ocf_max_points,
                "comment": "Incorrect"
            }
    else:
        details[ocf_key] = {
            "submitted": None,
            "correct": ocf_correct,
            "points": 0,
            "max_points": ocf_max_points,
            "comment": "Missing value"
        }
    
    # Free Cash Flow (7 points)
    fcf_key = "free_cash_flow_2023"
    fcf_max_points = 7
    fcf_submitted = submission.get(fcf_key)
    fcf_correct = answer_key.get(fcf_key)
    
    if fcf_submitted is not None:
        # Allow for some rounding differences
        if abs(fcf_submitted - fcf_correct) <= 1000:
            details[fcf_key] = {
                "submitted": fcf_submitted,
                "correct": fcf_correct,
                "points": fcf_max_points,
                "max_points": fcf_max_points,
                "comment": "Correct"
            }
            total_points += fcf_max_points
        # Partial credit for close answers
        elif abs(fcf_submitted - fcf_correct) <= 25000:
            partial_points = fcf_max_points * 0.5
            details[fcf_key] = {
                "submitted": fcf_submitted,
                "correct": fcf_correct,
                "points": partial_points,
                "max_points": fcf_max_points,
                "comment": "Close but not exact"
            }
            total_points += partial_points
        else:
            details[fcf_key] = {
                "submitted": fcf_submitted,
                "correct": fcf_correct,
                "points": 0,
                "max_points": fcf_max_points,
                "comment": "Incorrect"
            }
    else:
        details[fcf_key] = {
            "submitted": None,
            "correct": fcf_correct,
            "points": 0,
            "max_points": fcf_max_points,
            "comment": "Missing value"
        }
    
    # Cash Flow to Debt Ratio (5 points)
    cfdr_key = "cash_flow_to_debt_ratio_2023"
    cfdr_max_points = 5
    cfdr_submitted = submission.get(cfdr_key)
    cfdr_correct = answer_key.get(cfdr_key)
    
    if cfdr_submitted is not None:
        if abs(cfdr_submitted - cfdr_correct) <= 0.02:
            details[cfdr_key] = {
                "submitted": cfdr_submitted,
                "correct": cfdr_correct,
                "points": cfdr_max_points,
                "max_points": cfdr_max_points,
                "comment": "Correct"
            }
            total_points += cfdr_max_points
        # Partial credit for close answers
        elif abs(cfdr_submitted - cfdr_correct) <= 0.05:
            partial_points = cfdr_max_points * 0.5
            details[cfdr_key] = {
                "submitted": cfdr_submitted,
                "correct": cfdr_correct,
                "points": partial_points,
                "max_points": cfdr_max_points,
                "comment": "Close but not exact"
            }
            total_points += partial_points
        else:
            details[cfdr_key] = {
                "submitted": cfdr_submitted,
                "correct": cfdr_correct,
                "points": 0,
                "max_points": cfdr_max_points,
                "comment": "Incorrect"
            }
    else:
        details[cfdr_key] = {
            "submitted": None,
            "correct": cfdr_correct,
            "points": 0,
            "max_points": cfdr_max_points,
            "comment": "Missing value"
        }
    
    # Cash Flow Sufficiency (5 points) - Critical element
    suff_key = "sufficient_cash_flow"
    suff_max_points = 5
    suff_submitted = submission.get(suff_key)
    suff_correct = answer_key.get(suff_key)
    
    if suff_submitted is not None:
        if suff_submitted == suff_correct:
            details[suff_key] = {
                "submitted": suff_submitted,
                "correct": suff_correct,
                "points": suff_max_points,
                "max_points": suff_max_points,
                "comment": "Correct"
            }
            total_points += suff_max_points
        else:
            details[suff_key] = {
                "submitted": suff_submitted,
                "correct": suff_correct,
                "points": 0,
                "max_points": suff_max_points,
                "comment": "Incorrect - Critical element"
            }
    else:
        details[suff_key] = {
            "submitted": None,
            "correct": suff_correct,
            "points": 0,
            "max_points": suff_max_points,
            "comment": "Missing value"
        }
    
    return total_points, details


def evaluate_task3(submission: Dict[str, str], answer_key: Dict[str, str]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate Task 3: Risk Factor Identification
    
    5 points for each correct risk factor identification (5 factors total)
    """
    max_points = 25
    points_per_factor = 5
    
    total_points = 0
    details = {}
    
    for key, correct_value in answer_key.items():
        submitted_value = submission.get(key)
        
        if submitted_value is None:
            details[key] = {
                "submitted": None,
                "correct": correct_value,
                "points": 0,
                "max_points": points_per_factor,
                "comment": "Missing value"
            }
        elif submitted_value == correct_value:
            details[key] = {
                "submitted": submitted_value,
                "correct": correct_value,
                "points": points_per_factor,
                "max_points": points_per_factor,
                "comment": "Correct"
            }
            total_points += points_per_factor
        else:
            details[key] = {
                "submitted": submitted_value,
                "correct": correct_value,
                "points": 0,
                "max_points": points_per_factor,
                "comment": "Incorrect"
            }
    
    return total_points, details


def evaluate_task4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate Task 4: Credit Recommendation
    
    - Maximum loan amount calculation: 5 points
    - DSCR calculation: 8 points
    - DSCR minimum requirement determination: 5 points
    - Final loan recommendation: 7 points
    """
    total_points = 0
    details = {}
    
    # Maximum loan amount (5 points)
    mla_key = "max_loan_amount"
    mla_max_points = 5
    mla_submitted = submission.get(mla_key)
    mla_correct = answer_key.get(mla_key)
    
    if mla_submitted is not None:
        # Allow for some rounding differences
        if abs(mla_submitted - mla_correct) <= 10000:
            details[mla_key] = {
                "submitted": mla_submitted,
                "correct": mla_correct,
                "points": mla_max_points,
                "max_points": mla_max_points,
                "comment": "Correct"
            }
            total_points += mla_max_points
        # Partial credit for close answers
        elif abs(mla_submitted - mla_correct) <= 100000:
            partial_points = mla_max_points * 0.5
            details[mla_key] = {
                "submitted": mla_submitted,
                "correct": mla_correct,
                "points": partial_points,
                "max_points": mla_max_points,
                "comment": "Close but not exact"
            }
            total_points += partial_points
        else:
            details[mla_key] = {
                "submitted": mla_submitted,
                "correct": mla_correct,
                "points": 0,
                "max_points": mla_max_points,
                "comment": "Incorrect"
            }
    else:
        details[mla_key] = {
            "submitted": None,
            "correct": mla_correct,
            "points": 0,
            "max_points": mla_max_points,
            "comment": "Missing value"
        }
    
    # DSCR calculation (8 points)
    dscr_key = "debt_service_coverage_ratio"
    dscr_max_points = 8
    dscr_submitted = submission.get(dscr_key)
    dscr_correct = answer_key.get(dscr_key)
    
    if dscr_submitted is not None:
        if abs(dscr_submitted - dscr_correct) <= 0.02:
            details[dscr_key] = {
                "submitted": dscr_submitted,
                "correct": dscr_correct,
                "points": dscr_max_points,
                "max_points": dscr_max_points,
                "comment": "Correct"
            }
            total_points += dscr_max_points
        # Partial credit for close answers
        elif abs(dscr_submitted - dscr_correct) <= 0.1:
            partial_points = dscr_max_points * 0.5
            details[dscr_key] = {
                "submitted": dscr_submitted,
                "correct": dscr_correct,
                "points": partial_points,
                "max_points": dscr_max_points,
                "comment": "Close but not exact"
            }
            total_points += partial_points
        else:
            details[dscr_key] = {
                "submitted": dscr_submitted,
                "correct": dscr_correct,
                "points": 0,
                "max_points": dscr_max_points,
                "comment": "Incorrect"
            }
    else:
        details[dscr_key] = {
            "submitted": None,
            "correct": dscr_correct,
            "points": 0,
            "max_points": dscr_max_points,
            "comment": "Missing value"
        }
    
    # Meets minimum DSCR (5 points) - Critical element
    min_dscr_key = "meets_minimum_dscr"
    min_dscr_max_points = 5
    min_dscr_submitted = submission.get(min_dscr_key)
    min_dscr_correct = answer_key.get(min_dscr_key)
    
    if min_dscr_submitted is not None:
        if min_dscr_submitted == min_dscr_correct:
            details[min_dscr_key] = {
                "submitted": min_dscr_submitted,
                "correct": min_dscr_correct,
                "points": min_dscr_max_points,
                "max_points": min_dscr_max_points,
                "comment": "Correct"
            }
            total_points += min_dscr_max_points
        else:
            details[min_dscr_key] = {
                "submitted": min_dscr_submitted,
                "correct": min_dscr_correct,
                "points": 0,
                "max_points": min_dscr_max_points,
                "comment": "Incorrect - Critical element"
            }
    else:
        details[min_dscr_key] = {
            "submitted": None,
            "correct": min_dscr_correct,
            "points": 0,
            "max_points": min_dscr_max_points,
            "comment": "Missing value"
        }
    
    # Loan recommendation (7 points) - Critical element
    rec_key = "loan_recommendation"
    rec_max_points = 7
    rec_submitted = submission.get(rec_key)
    rec_correct = answer_key.get(rec_key)
    
    if rec_submitted is not None:
        if rec_submitted == rec_correct:
            details[rec_key] = {
                "submitted": rec_submitted,
                "correct": rec_correct,
                "points": rec_max_points,
                "max_points": rec_max_points,
                "comment": "Correct"
            }
            total_points += rec_max_points
        else:
            details[rec_key] = {
                "submitted": rec_submitted,
                "correct": rec_correct,
                "points": 0,
                "max_points": rec_max_points,
                "comment": "Incorrect - Critical element"
            }
    else:
        details[rec_key] = {
            "submitted": None,
            "correct": rec_correct,
            "points": 0,
            "max_points": rec_max_points,
            "comment": "Missing value"
        }
    
    return total_points, details


def check_critical_elements(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if the candidate correctly identified the critical elements:
    1. Cash flow is insufficient to service the requested loan
    2. The loan does not meet the minimum DSCR requirement
    3. The loan recommendation is to deny
    
    Returns a tuple of (passed, reason)
    """
    # Check cash flow sufficiency
    if submission.get("task2", {}).get("sufficient_cash_flow") != answer_key.get("task2", {}).get("sufficient_cash_flow"):
        return False, "Failed to correctly identify that cash flow is insufficient to service the loan"
    
    # Check DSCR minimum requirement
    if submission.get("task4", {}).get("meets_minimum_dscr") != answer_key.get("task4", {}).get("meets_minimum_dscr"):
        return False, "Failed to correctly identify that the loan does not meet the minimum DSCR requirement"
    
    # Check loan recommendation
    if submission.get("task4", {}).get("loan_recommendation") != answer_key.get("task4", {}).get("loan_recommendation"):
        return False, "Failed to correctly recommend denying the loan"
    
    return True, "Passed all critical elements"


def check_task_minimum_scores(task_scores: Dict[str, float]) -> Tuple[bool, str]:
    """
    Check if the candidate achieved the minimum required score for each task (60%).
    
    Returns a tuple of (passed, reason)
    """
    task_minimums = {
        "task1": 15,  # 60% of 25
        "task2": 15,  # 60% of 25
        "task3": 15,  # 60% of 25
        "task4": 15,  # 60% of 25
    }
    
    for task, min_score in task_minimums.items():
        if task_scores.get(task, 0) < min_score:
            return False, f"Failed to achieve minimum required score for {task.capitalize()}"
    
    return True, "Passed all task minimum score requirements"


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Extract candidate ID if available
    candidate_id = submission.get("candidate_id", "Unknown")
    
    # Evaluate each task
    task1_score, task1_details = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    task2_score, task2_details = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    task3_score, task3_details = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    task4_score, task4_details = evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    
    # Calculate total score
    task_scores = {
        "task1": task1_score,
        "task2": task2_score,
        "task3": task3_score,
        "task4": task4_score
    }
    
    total_score = sum(task_scores.values())
    max_possible_score = 100  # 25 points per task, 4 tasks
    overall_score_percentage = (total_score / max_possible_score) * 100
    
    # Check if candidate passed the minimum requirements
    passed_critical_elements, critical_elements_reason = check_critical_elements(submission, answer_key)
    passed_task_minimums, task_minimums_reason = check_task_minimum_scores(task_scores)
    
    # Determine if the candidate passed overall
    passed_overall = (
        overall_score_percentage >= 70 and
        passed_critical_elements and
        passed_task_minimums
    )
    
    # Prepare the results
    results = {
        "candidate_id": candidate_id,
        "overall_score": round(overall_score_percentage, 2),
        "passed": passed_overall,
        "total_points": total_score,
        "max_possible_points": max_possible_score,
        "task_scores": {
            "task1": {
                "score": task1_score,
                "max_possible": 25,
                "percentage": (task1_score / 25) * 100,
                "details": task1_details
            },
            "task2": {
                "score": task2_score,
                "max_possible": 25,
                "percentage": (task2_score / 25) * 100,
                "details": task2_details
            },
            "task3": {
                "score": task3_score,
                "max_possible": 25,
                "percentage": (task3_score / 25) * 100,
                "details": task3_details
            },
            "task4": {
                "score": task4_score,
                "max_possible": 25,
                "percentage": (task4_score / 25) * 100,
                "details": task4_details
            }
        },
        "critical_elements": {
            "passed": passed_critical_elements,
            "reason": critical_elements_reason
        },
        "task_minimums": {
            "passed": passed_task_minimums,
            "reason": task_minimums_reason
        }
    }
    
    # Save the results to a file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score_percentage:.2f}%")
    print(f"Passed: {passed_overall}")


if __name__ == "__main__":
    main()