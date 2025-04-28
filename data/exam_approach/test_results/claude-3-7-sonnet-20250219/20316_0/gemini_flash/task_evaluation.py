#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, List, Union, Any

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Program Cost Analysis."""
    results = {
        "points_possible": 4,
        "points_earned": 0,
        "details": {}
    }
    
    # Check cost_per_participant (allow 5% margin of error)
    expected = answer_key["task1"]["cost_per_participant"]
    submitted = submission.get("task1", {}).get("cost_per_participant")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        if abs(submitted - expected) <= error_margin:
            results["points_earned"] += 1
            results["details"]["cost_per_participant"] = {
                "correct": True,
                "submitted": submitted,
                "expected": expected
            }
        elif abs(submitted - expected) <= error_margin * 2:
            results["points_earned"] += 0.5
            results["details"]["cost_per_participant"] = {
                "correct": "partial",
                "submitted": submitted,
                "expected": expected
            }
        else:
            results["details"]["cost_per_participant"] = {
                "correct": False,
                "submitted": submitted,
                "expected": expected
            }
    else:
        results["details"]["cost_per_participant"] = {
            "correct": False,
            "submitted": None,
            "expected": expected
        }
    
    # Check highest_cost_program
    expected = answer_key["task1"]["highest_cost_program"]
    submitted = submission.get("task1", {}).get("highest_cost_program")
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["highest_cost_program"] = {
            "correct": True,
            "submitted": submitted,
            "expected": expected
        }
    else:
        results["details"]["highest_cost_program"] = {
            "correct": False,
            "submitted": submitted,
            "expected": expected
        }
    
    # Check lowest_cost_program
    expected = answer_key["task1"]["lowest_cost_program"]
    submitted = submission.get("task1", {}).get("lowest_cost_program")
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["lowest_cost_program"] = {
            "correct": True,
            "submitted": submitted,
            "expected": expected
        }
    else:
        results["details"]["lowest_cost_program"] = {
            "correct": False,
            "submitted": submitted,
            "expected": expected
        }
    
    # Check participation_threshold_programs
    expected = set(answer_key["task1"]["participation_threshold_programs"])
    submitted_list = submission.get("task1", {}).get("participation_threshold_programs", [])
    submitted = set(submitted_list if isinstance(submitted_list, list) else [])
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["participation_threshold_programs"] = {
            "correct": True,
            "submitted": list(submitted),
            "expected": list(expected)
        }
    elif len(submitted.intersection(expected)) > 0:
        # Partial credit if some programs match
        results["points_earned"] += 0.5
        results["details"]["participation_threshold_programs"] = {
            "correct": "partial",
            "submitted": list(submitted),
            "expected": list(expected)
        }
    else:
        results["details"]["participation_threshold_programs"] = {
            "correct": False,
            "submitted": list(submitted),
            "expected": list(expected)
        }
    
    return results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: ROI Evaluation."""
    results = {
        "points_possible": 5,
        "points_earned": 0,
        "details": {}
    }
    
    # Check program_roi_values
    expected_roi = answer_key["task2"]["program_roi_values"]
    submitted_roi = submission.get("task2", {}).get("program_roi_values", {})
    
    roi_correct_count = 0
    roi_details = {}
    
    for program, expected_value in expected_roi.items():
        submitted_value = submitted_roi.get(program)
        
        if submitted_value is not None:
            error_margin = abs(expected_value * 0.05)
            if abs(submitted_value - expected_value) <= error_margin:
                roi_correct_count += 1
                roi_details[program] = {
                    "correct": True,
                    "submitted": submitted_value,
                    "expected": expected_value
                }
            elif abs(submitted_value - expected_value) <= error_margin * 2:
                roi_correct_count += 0.5
                roi_details[program] = {
                    "correct": "partial",
                    "submitted": submitted_value,
                    "expected": expected_value
                }
            else:
                roi_details[program] = {
                    "correct": False,
                    "submitted": submitted_value,
                    "expected": expected_value
                }
        else:
            roi_details[program] = {
                "correct": False,
                "submitted": None,
                "expected": expected_value
            }
    
    # Award points based on number of correct ROI calculations
    results["points_earned"] += min(3, roi_correct_count)
    results["details"]["program_roi_values"] = roi_details
    
    # Check highest_roi_program
    expected = answer_key["task2"]["highest_roi_program"]
    submitted = submission.get("task2", {}).get("highest_roi_program")
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["highest_roi_program"] = {
            "correct": True,
            "submitted": submitted,
            "expected": expected
        }
    else:
        results["details"]["highest_roi_program"] = {
            "correct": False,
            "submitted": submitted,
            "expected": expected
        }
    
    # Check cost_effective_programs
    expected = set(answer_key["task2"]["cost_effective_programs"])
    submitted_list = submission.get("task2", {}).get("cost_effective_programs", [])
    submitted = set(submitted_list if isinstance(submitted_list, list) else [])
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["cost_effective_programs"] = {
            "correct": True,
            "submitted": list(submitted),
            "expected": list(expected)
        }
    elif len(submitted.intersection(expected)) / max(1, len(expected)) >= 0.5:
        # Partial credit if at least half of the programs match
        results["points_earned"] += 0.5
        results["details"]["cost_effective_programs"] = {
            "correct": "partial",
            "submitted": list(submitted),
            "expected": list(expected)
        }
    else:
        results["details"]["cost_effective_programs"] = {
            "correct": False,
            "submitted": list(submitted),
            "expected": list(expected)
        }
    
    return results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Cost Trend Analysis."""
    results = {
        "points_possible": 4,
        "points_earned": 0,
        "details": {}
    }
    
    # Check quarterly_cost_trend
    expected = answer_key["task3"]["quarterly_cost_trend"]
    submitted = submission.get("task3", {}).get("quarterly_cost_trend")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        if abs(submitted - expected) <= error_margin:
            results["points_earned"] += 1
            results["details"]["quarterly_cost_trend"] = {
                "correct": True,
                "submitted": submitted,
                "expected": expected
            }
        elif abs(submitted - expected) <= error_margin * 2:
            results["points_earned"] += 0.5
            results["details"]["quarterly_cost_trend"] = {
                "correct": "partial",
                "submitted": submitted,
                "expected": expected
            }
        else:
            results["details"]["quarterly_cost_trend"] = {
                "correct": False,
                "submitted": submitted,
                "expected": expected
            }
    else:
        results["details"]["quarterly_cost_trend"] = {
            "correct": False,
            "submitted": None,
            "expected": expected
        }
    
    # Check projected_annual_savings
    expected = answer_key["task3"]["projected_annual_savings"]
    submitted = submission.get("task3", {}).get("projected_annual_savings")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        if abs(submitted - expected) <= error_margin:
            results["points_earned"] += 1
            results["details"]["projected_annual_savings"] = {
                "correct": True,
                "submitted": submitted,
                "expected": expected
            }
        elif abs(submitted - expected) <= error_margin * 2:
            results["points_earned"] += 0.5
            results["details"]["projected_annual_savings"] = {
                "correct": "partial",
                "submitted": submitted,
                "expected": expected
            }
        else:
            results["details"]["projected_annual_savings"] = {
                "correct": False,
                "submitted": submitted,
                "expected": expected
            }
    else:
        results["details"]["projected_annual_savings"] = {
            "correct": False,
            "submitted": None,
            "expected": expected
        }
    
    # Check cost_reduction_percentage
    expected = answer_key["task3"]["cost_reduction_percentage"]
    submitted = submission.get("task3", {}).get("cost_reduction_percentage")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        if abs(submitted - expected) <= error_margin:
            results["points_earned"] += 1
            results["details"]["cost_reduction_percentage"] = {
                "correct": True,
                "submitted": submitted,
                "expected": expected
            }
        elif abs(submitted - expected) <= error_margin * 2:
            results["points_earned"] += 0.5
            results["details"]["cost_reduction_percentage"] = {
                "correct": "partial",
                "submitted": submitted,
                "expected": expected
            }
        else:
            results["details"]["cost_reduction_percentage"] = {
                "correct": False,
                "submitted": submitted,
                "expected": expected
            }
    else:
        results["details"]["cost_reduction_percentage"] = {
            "correct": False,
            "submitted": None,
            "expected": expected
        }
    
    # Check break_even_month
    expected = answer_key["task3"]["break_even_month"]
    submitted = submission.get("task3", {}).get("break_even_month")
    
    if submitted == expected:
        results["points_earned"] += 1
        results["details"]["break_even_month"] = {
            "correct": True,
            "submitted": submitted,
            "expected": expected
        }
    elif submitted is not None and abs(submitted - expected) <= 1:
        # Allow off-by-one for break-even month
        results["points_earned"] += 0.5
        results["details"]["break_even_month"] = {
            "correct": "partial",
            "submitted": submitted,
            "expected": expected
        }
    else:
        results["details"]["break_even_month"] = {
            "correct": False,
            "submitted": submitted,
            "expected": expected
        }
    
    return results

def check_critical_elements(task_results: Dict, submission: Dict, answer_key: Dict) -> Dict:
    """Check if critical elements are correct."""
    critical_elements = {
        "roi_calculations": False,
        "average_cost_per_participant": False,
        "projected_annual_savings": False
    }
    
    # Check ROI calculations (at least 3 of 5 correct)
    roi_correct_count = 0
    submitted_roi = submission.get("task2", {}).get("program_roi_values", {})
    expected_roi = answer_key["task2"]["program_roi_values"]
    
    for program, expected_value in expected_roi.items():
        submitted_value = submitted_roi.get(program)
        if submitted_value is not None:
            error_margin = abs(expected_value * 0.05)
            if abs(submitted_value - expected_value) <= error_margin:
                roi_correct_count += 1
    
    critical_elements["roi_calculations"] = roi_correct_count >= 3
    
    # Check average cost per participant
    expected = answer_key["task1"]["cost_per_participant"]
    submitted = submission.get("task1", {}).get("cost_per_participant")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        critical_elements["average_cost_per_participant"] = abs(submitted - expected) <= error_margin
    
    # Check projected annual savings
    expected = answer_key["task3"]["projected_annual_savings"]
    submitted = submission.get("task3", {}).get("projected_annual_savings")
    
    if submitted is not None:
        error_margin = abs(expected * 0.05)
        critical_elements["projected_annual_savings"] = abs(submitted - expected) <= error_margin
    
    return critical_elements

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Calculate total points
    total_points_possible = task1_results["points_possible"] + task2_results["points_possible"] + task3_results["points_possible"]
    total_points_earned = task1_results["points_earned"] + task2_results["points_earned"] + task3_results["points_earned"]
    
    # Check critical elements
    critical_elements = check_critical_elements(
        {"task1": task1_results, "task2": task2_results, "task3": task3_results},
        submission,
        answer_key
    )
    
    # Calculate overall score as a percentage
    overall_score = (total_points_earned / total_points_possible) * 100
    
    # Determine if the candidate passed
    passed = (total_points_earned >= 10) and all(critical_elements.values())
    
    return {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "passed": passed,
        "critical_elements": critical_elements,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results
        }
    }

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()