#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_budget_task(submission, answer_key):
    results = {
        "total_projected_expenses": {
            "correct": False,
            "submitted": submission["budget_task"]["total_projected_expenses"],
            "expected": answer_key["budget_task"]["total_projected_expenses"],
            "points": 0
        },
        "variance_percentage": {
            "correct": False,
            "submitted": submission["budget_task"]["variance_percentage"],
            "expected": answer_key["budget_task"]["variance_percentage"],
            "points": 0
        },
        "largest_expense_category": {
            "correct": False,
            "submitted": submission["budget_task"]["largest_expense_category"],
            "expected": answer_key["budget_task"]["largest_expense_category"],
            "points": 0
        },
        "cost_per_client": {
            "correct": False,
            "submitted": submission["budget_task"]["cost_per_client"],
            "expected": answer_key["budget_task"]["cost_per_client"],
            "points": 0
        }
    }
    
    # Total projected expenses - exact match required
    if submission["budget_task"]["total_projected_expenses"] == answer_key["budget_task"]["total_projected_expenses"]:
        results["total_projected_expenses"]["correct"] = True
        results["total_projected_expenses"]["points"] = 1
    
    # Variance percentage - allow 0.5% margin of error
    submitted_variance = submission["budget_task"]["variance_percentage"]
    expected_variance = answer_key["budget_task"]["variance_percentage"]
    if abs(submitted_variance - expected_variance) <= 0.5:
        results["variance_percentage"]["correct"] = True
        results["variance_percentage"]["points"] = 1
    elif abs(submitted_variance - expected_variance) <= 1.0:
        # Partial credit for close answers
        results["variance_percentage"]["points"] = 0.5
    
    # Largest expense category - exact match required
    if submission["budget_task"]["largest_expense_category"] == answer_key["budget_task"]["largest_expense_category"]:
        results["largest_expense_category"]["correct"] = True
        results["largest_expense_category"]["points"] = 1
    
    # Cost per client - allow 0.5% margin of error
    submitted_cost = submission["budget_task"]["cost_per_client"]
    expected_cost = answer_key["budget_task"]["cost_per_client"]
    if abs(submitted_cost - expected_cost) <= (expected_cost * 0.005):
        results["cost_per_client"]["correct"] = True
        results["cost_per_client"]["points"] = 1
    elif abs(submitted_cost - expected_cost) <= (expected_cost * 0.01):
        # Partial credit for close answers
        results["cost_per_client"]["points"] = 0.5
    
    return results

def evaluate_personnel_task(submission, answer_key):
    results = {
        "total_staff": {
            "correct": False,
            "submitted": submission["personnel_task"]["total_staff"],
            "expected": answer_key["personnel_task"]["total_staff"],
            "points": 0
        },
        "certification_expiring": {
            "correct": False,
            "submitted": submission["personnel_task"]["certification_expiring"],
            "expected": answer_key["personnel_task"]["certification_expiring"],
            "points": 0
        },
        "average_years_experience": {
            "correct": False,
            "submitted": submission["personnel_task"]["average_years_experience"],
            "expected": answer_key["personnel_task"]["average_years_experience"],
            "points": 0
        },
        "staff_to_supervisor_ratio": {
            "correct": False,
            "submitted": submission["personnel_task"]["staff_to_supervisor_ratio"],
            "expected": answer_key["personnel_task"]["staff_to_supervisor_ratio"],
            "points": 0
        }
    }
    
    # Total staff - exact match required
    if submission["personnel_task"]["total_staff"] == answer_key["personnel_task"]["total_staff"]:
        results["total_staff"]["correct"] = True
        results["total_staff"]["points"] = 1
    
    # Certification expiring - exact match required for all IDs
    submitted_certs = set(submission["personnel_task"]["certification_expiring"])
    expected_certs = set(answer_key["personnel_task"]["certification_expiring"])
    
    if submitted_certs == expected_certs:
        results["certification_expiring"]["correct"] = True
        results["certification_expiring"]["points"] = 1
    
    # Average years experience - allow 0.5% margin of error
    submitted_avg = submission["personnel_task"]["average_years_experience"]
    expected_avg = answer_key["personnel_task"]["average_years_experience"]
    if abs(submitted_avg - expected_avg) <= 0.03:  # ~0.5% of 5.71
        results["average_years_experience"]["correct"] = True
        results["average_years_experience"]["points"] = 1
    elif abs(submitted_avg - expected_avg) <= 0.06:  # ~1.0% of 5.71
        # Partial credit for close answers
        results["average_years_experience"]["points"] = 0.5
    
    # Staff to supervisor ratio - allow 0.5% margin of error
    submitted_ratio = submission["personnel_task"]["staff_to_supervisor_ratio"]
    expected_ratio = answer_key["personnel_task"]["staff_to_supervisor_ratio"]
    if abs(submitted_ratio - expected_ratio) <= 0.03:  # ~0.5% of 5.67
        results["staff_to_supervisor_ratio"]["correct"] = True
        results["staff_to_supervisor_ratio"]["points"] = 1
    elif abs(submitted_ratio - expected_ratio) <= 0.06:  # ~1.0% of 5.67
        # Partial credit for close answers
        results["staff_to_supervisor_ratio"]["points"] = 0.5
    
    return results

def evaluate_training_task(submission, answer_key):
    results = {
        "section_title": {
            "correct": False,
            "submitted": submission["training_task"]["section_title"],
            "expected": answer_key["training_task"]["section_title"],
            "points": 0
        },
        "word_count": {
            "correct": False,
            "submitted": submission["training_task"]["word_count"],
            "expected": answer_key["training_task"]["word_count"],
            "points": 0
        },
        "key_points": {
            "correct": False,
            "submitted": submission["training_task"]["key_points"],
            "expected": answer_key["training_task"]["key_points"],
            "points": 0
        },
        "procedure_steps": {
            "correct": False,
            "submitted": submission["training_task"]["procedure_steps"],
            "expected": answer_key["training_task"]["procedure_steps"],
            "points": 0
        }
    }
    
    # Section title - exact match required
    if submission["training_task"]["section_title"] == answer_key["training_task"]["section_title"]:
        results["section_title"]["correct"] = True
        results["section_title"]["points"] = 1
    
    # Word count - allow small margin of error (±3 words)
    submitted_count = submission["training_task"]["word_count"]
    expected_count = answer_key["training_task"]["word_count"]
    if abs(submitted_count - expected_count) <= 3:
        results["word_count"]["correct"] = True
        results["word_count"]["points"] = 1
    
    # Key points - exact matches required for all points
    submitted_points = submission["training_task"]["key_points"]
    expected_points = answer_key["training_task"]["key_points"]
    
    if set(submitted_points) == set(expected_points):
        results["key_points"]["correct"] = True
        results["key_points"]["points"] = 1
    
    # Procedure steps - exact matches required in correct order
    submitted_steps = submission["training_task"]["procedure_steps"]
    expected_steps = answer_key["training_task"]["procedure_steps"]
    
    if submitted_steps == expected_steps:
        results["procedure_steps"]["correct"] = True
        results["procedure_steps"]["points"] = 1
    
    return results

def check_critical_items(evaluation_results, answer_key):
    critical_items_passed = True
    
    # Check total projected expenses
    if not evaluation_results["budget_task"]["total_projected_expenses"]["correct"]:
        critical_items_passed = False
    
    # Check certification expiring
    if not evaluation_results["personnel_task"]["certification_expiring"]["correct"]:
        critical_items_passed = False
    
    # Check key points
    if not evaluation_results["training_task"]["key_points"]["correct"]:
        critical_items_passed = False
    
    return critical_items_passed

def check_minimum_task_performance(evaluation_results):
    task_minimums_passed = True
    
    # Budget task: at least 3 out of 4 correct
    budget_points = sum(item["points"] for item in evaluation_results["budget_task"].values())
    if budget_points < 3:
        task_minimums_passed = False
    
    # Personnel task: at least 3 out of 4 correct
    personnel_points = sum(item["points"] for item in evaluation_results["personnel_task"].values())
    if personnel_points < 3:
        task_minimums_passed = False
    
    # Training task: at least 3 out of 4 correct
    training_points = sum(item["points"] for item in evaluation_results["training_task"].values())
    if training_points < 3:
        task_minimums_passed = False
    
    return task_minimums_passed

def calculate_overall_score(evaluation_results):
    total_points = 0
    max_points = 12  # 4 items per task × 3 tasks
    
    # Sum points from all tasks
    for task in ["budget_task", "personnel_task", "training_task"]:
        for item in evaluation_results[task].values():
            total_points += item["points"]
    
    # Calculate percentage
    percentage = (total_points / max_points) * 100
    return round(percentage, 2)

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    evaluation_results = {
        "budget_task": evaluate_budget_task(submission, answer_key),
        "personnel_task": evaluate_personnel_task(submission, answer_key),
        "training_task": evaluate_training_task(submission, answer_key)
    }
    
    # Check critical items and minimum task performance
    critical_items_passed = check_critical_items(evaluation_results, answer_key)
    task_minimums_passed = check_minimum_task_performance(evaluation_results)
    
    # Calculate overall score
    overall_score = calculate_overall_score(evaluation_results)
    
    # Determine if candidate passed
    passed = overall_score >= 75 and critical_items_passed and task_minimums_passed
    
    # Prepare final results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_results": evaluation_results,
        "overall_score": overall_score,
        "critical_items_passed": critical_items_passed,
        "task_minimums_passed": task_minimums_passed,
        "passed": passed
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score}%")
    print(f"Passed: {passed}")

if __name__ == "__main__":
    main()