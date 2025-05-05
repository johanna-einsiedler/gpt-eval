#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Store Loss Analysis."""
    result = {"max_points": 20, "points_earned": 0, "feedback": []}
    
    # Check store ID
    submitted_store = submission.get("store_with_highest_loss")
    correct_store = answer_key.get("store_with_highest_loss")
    if submitted_store == correct_store:
        result["points_earned"] += 10
        result["feedback"].append("Correct store identified.")
    else:
        result["feedback"].append(f"Incorrect store. Submitted: {submitted_store}, Expected: {correct_store}")
    
    # Check loss amount
    submitted_amount = submission.get("loss_amount")
    correct_amount = answer_key.get("loss_amount")
    
    if submitted_amount is not None and correct_amount is not None:
        # Allow 5% margin of error
        margin = correct_amount * 0.05
        if abs(submitted_amount - correct_amount) <= margin:
            result["points_earned"] += 10
            result["feedback"].append("Correct loss amount (within 5% margin).")
        else:
            result["feedback"].append(f"Incorrect loss amount. Submitted: {submitted_amount}, Expected: {correct_amount} (±5%)")
    else:
        result["feedback"].append("Missing loss amount value.")
    
    return result


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Suspicious Transaction Patterns."""
    result = {"max_points": 20, "points_earned": 0, "feedback": []}
    
    # Check employee ID
    submitted_employee = submission.get("suspicious_employee_id")
    correct_employee = answer_key.get("suspicious_employee_id")
    if submitted_employee == correct_employee:
        result["points_earned"] += 7
        result["feedback"].append("Correct employee identified.")
    else:
        result["feedback"].append(f"Incorrect employee. Submitted: {submitted_employee}, Expected: {correct_employee}")
    
    # Check transaction count
    submitted_count = submission.get("transaction_count")
    correct_count = answer_key.get("transaction_count")
    
    if submitted_count is not None and correct_count is not None:
        # Allow ±2 transactions
        if abs(submitted_count - correct_count) <= 2:
            result["points_earned"] += 7
            result["feedback"].append("Correct transaction count (within ±2 margin).")
        else:
            result["feedback"].append(f"Incorrect transaction count. Submitted: {submitted_count}, Expected: {correct_count} (±2)")
    else:
        result["feedback"].append("Missing transaction count value.")
    
    # Check average transaction value
    submitted_avg = submission.get("average_transaction_value")
    correct_avg = answer_key.get("average_transaction_value")
    
    if submitted_avg is not None and correct_avg is not None:
        # Allow 5% margin of error
        margin = correct_avg * 0.05
        if abs(submitted_avg - correct_avg) <= margin:
            result["points_earned"] += 6
            result["feedback"].append("Correct average transaction value (within 5% margin).")
        else:
            result["feedback"].append(f"Incorrect average transaction value. Submitted: {submitted_avg}, Expected: {correct_avg} (±5%)")
    else:
        result["feedback"].append("Missing average transaction value.")
    
    return result


def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Department Shrinkage Analysis."""
    result = {"max_points": 20, "points_earned": 0, "feedback": []}
    
    # Check department
    submitted_dept = submission.get("department_with_highest_shrinkage")
    correct_dept = answer_key.get("department_with_highest_shrinkage")
    if submitted_dept == correct_dept:
        result["points_earned"] += 10
        result["feedback"].append("Correct department identified.")
    else:
        result["feedback"].append(f"Incorrect department. Submitted: {submitted_dept}, Expected: {correct_dept}")
    
    # Check shrinkage percentage
    submitted_pct = submission.get("shrinkage_percentage")
    correct_pct = answer_key.get("shrinkage_percentage")
    
    if submitted_pct is not None and correct_pct is not None:
        # Allow ±0.5% margin
        if abs(submitted_pct - correct_pct) <= 0.5:
            result["points_earned"] += 10
            result["feedback"].append("Correct shrinkage percentage (within ±0.5% margin).")
        else:
            result["feedback"].append(f"Incorrect shrinkage percentage. Submitted: {submitted_pct}, Expected: {correct_pct} (±0.5%)")
    else:
        result["feedback"].append("Missing shrinkage percentage value.")
    
    return result


def evaluate_task4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 4: Void Analysis."""
    result = {"max_points": 20, "points_earned": 0, "feedback": []}
    
    # Check date
    submitted_date = submission.get("date_with_highest_voids")
    correct_date = answer_key.get("date_with_highest_voids")
    if submitted_date == correct_date:
        result["points_earned"] += 7
        result["feedback"].append("Correct date identified.")
    else:
        result["feedback"].append(f"Incorrect date. Submitted: {submitted_date}, Expected: {correct_date}")
    
    # Check void count
    submitted_count = submission.get("void_count")
    correct_count = answer_key.get("void_count")
    
    if submitted_count is not None and correct_count is not None:
        if submitted_count == correct_count:
            result["points_earned"] += 7
            result["feedback"].append("Correct void count.")
        else:
            result["feedback"].append(f"Incorrect void count. Submitted: {submitted_count}, Expected: {correct_count}")
    else:
        result["feedback"].append("Missing void count value.")
    
    # Check void value
    submitted_value = submission.get("void_value")
    correct_value = answer_key.get("void_value")
    
    if submitted_value is not None and correct_value is not None:
        # Allow 5% margin of error
        margin = correct_value * 0.05
        if abs(submitted_value - correct_value) <= margin:
            result["points_earned"] += 6
            result["feedback"].append("Correct void value (within 5% margin).")
        else:
            result["feedback"].append(f"Incorrect void value. Submitted: {submitted_value}, Expected: {correct_value} (±5%)")
    else:
        result["feedback"].append("Missing void value.")
    
    return result


def evaluate_task5(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 5: Emerging Trend Identification."""
    result = {"max_points": 20, "points_earned": 0, "feedback": []}
    
    # Check start date (allow ±3 days)
    from datetime import datetime, timedelta
    
    submitted_start = submission.get("pattern_timeframe_start")
    correct_start = answer_key.get("pattern_timeframe_start")
    
    if submitted_start and correct_start:
        try:
            submitted_start_date = datetime.strptime(submitted_start, "%Y-%m-%d")
            correct_start_date = datetime.strptime(correct_start, "%Y-%m-%d")
            
            if abs((submitted_start_date - correct_start_date).days) <= 3:
                result["points_earned"] += 7
                result["feedback"].append("Correct pattern start date (within ±3 days).")
            else:
                result["feedback"].append(f"Incorrect pattern start date. Submitted: {submitted_start}, Expected: {correct_start} (±3 days)")
        except ValueError:
            result["feedback"].append(f"Invalid date format for pattern start date: {submitted_start}")
    else:
        result["feedback"].append("Missing pattern start date.")
    
    # Check end date (allow ±3 days)
    submitted_end = submission.get("pattern_timeframe_end")
    correct_end = answer_key.get("pattern_timeframe_end")
    
    if submitted_end and correct_end:
        try:
            submitted_end_date = datetime.strptime(submitted_end, "%Y-%m-%d")
            correct_end_date = datetime.strptime(correct_end, "%Y-%m-%d")
            
            if abs((submitted_end_date - correct_end_date).days) <= 3:
                result["points_earned"] += 7
                result["feedback"].append("Correct pattern end date (within ±3 days).")
            else:
                result["feedback"].append(f"Incorrect pattern end date. Submitted: {submitted_end}, Expected: {correct_end} (±3 days)")
        except ValueError:
            result["feedback"].append(f"Invalid date format for pattern end date: {submitted_end}")
    else:
        result["feedback"].append("Missing pattern end date.")
    
    # Check estimated loss
    submitted_loss = submission.get("total_estimated_loss")
    correct_loss = answer_key.get("total_estimated_loss")
    
    if submitted_loss is not None and correct_loss is not None:
        # Allow 10% margin of error
        margin = correct_loss * 0.10
        if abs(submitted_loss - correct_loss) <= margin:
            result["points_earned"] += 6
            result["feedback"].append("Correct estimated loss (within 10% margin).")
        else:
            result["feedback"].append(f"Incorrect estimated loss. Submitted: {submitted_loss}, Expected: {correct_loss} (±10%)")
    else:
        result["feedback"].append("Missing estimated loss value.")
    
    return result


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task_results": {},
        "overall_score": 0,
        "passing_threshold": 60,
        "passed": False
    }
    
    total_points = 0
    total_possible = 0
    
    # Evaluate each task
    task_evaluators = {
        "task1": evaluate_task1,
        "task2": evaluate_task2,
        "task3": evaluate_task3,
        "task4": evaluate_task4,
        "task5": evaluate_task5
    }
    
    for task_id, evaluator in task_evaluators.items():
        if task_id in submission and task_id in answer_key:
            task_result = evaluator(submission[task_id], answer_key[task_id])
            results["task_results"][task_id] = task_result
            
            total_points += task_result["points_earned"]
            total_possible += task_result["max_points"]
        else:
            results["task_results"][task_id] = {
                "max_points": 20,
                "points_earned": 0,
                "feedback": ["Task not attempted or missing from submission."]
            }
            total_possible += 20
    
    # Calculate overall score as a percentage
    if total_possible > 0:
        results["overall_score"] = round((total_points / total_possible) * 100, 2)
    
    # Determine if candidate passed
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    
    # Check if Task 5 is at least partially correct (required for passing)
    task5_result = results["task_results"].get("task5", {})
    task5_points = task5_result.get("points_earned", 0)
    
    if results["passed"] and task5_points == 0:
        results["passed"] = False
        results["feedback"] = "Failed: Task 5 must be at least partially correct to pass."
    
    # Count correct tasks (tasks with at least half the points)
    correct_tasks = sum(1 for task in results["task_results"].values() 
                        if task.get("points_earned", 0) >= task.get("max_points", 20) / 2)
    
    if results["passed"] and correct_tasks < 3:
        results["passed"] = False
        results["feedback"] = "Failed: At least 3 out of 5 tasks must be correct to pass."
    
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
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()