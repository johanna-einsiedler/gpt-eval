#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Fixed-Rate Mortgage Calculation."""
    correct_payment = answer_key["task1"]["monthly_payment"]
    submitted_payment = submission["task1"]["monthly_payment"]
    
    # Full credit if within $0.02
    if abs(submitted_payment - correct_payment) <= 0.02:
        score = 2
        feedback = "Correct"
    # Half credit if within $1.00
    elif abs(submitted_payment - correct_payment) <= 1.00:
        score = 1
        feedback = "Partially correct (within $1.00)"
    else:
        score = 0
        feedback = "Incorrect"
    
    return {
        "score": score,
        "max_score": 2,
        "feedback": feedback,
        "submitted_value": submitted_payment,
        "correct_value": correct_payment
    }

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Payment Schedule Creation."""
    results = {"score": 0, "max_score": 6, "months": {}}
    
    for month in ["month_1", "month_6", "month_12"]:
        month_result = {"score": 0, "max_score": 2, "fields": {}}
        
        # Check each field in the month
        for field in ["payment_amount", "principal_portion", "interest_portion", "remaining_balance"]:
            correct_value = answer_key["task2"][month][field]
            submitted_value = submission["task2"][month][field]
            
            # Evaluate field
            if abs(submitted_value - correct_value) <= 0.02:
                field_score = 0.5  # Each field is worth 0.5 points
                field_feedback = "Correct"
            elif abs(submitted_value - correct_value) <= 1.00:
                field_score = 0.25  # Half credit if within $1.00
                field_feedback = "Partially correct (within $1.00)"
            else:
                field_score = 0
                field_feedback = "Incorrect"
            
            month_result["fields"][field] = {
                "score": field_score,
                "feedback": field_feedback,
                "submitted_value": submitted_value,
                "correct_value": correct_value
            }
            month_result["score"] += field_score
        
        results["months"][month] = month_result
        results["score"] += month_result["score"]
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Extra Payment Impact."""
    results = {"score": 0, "max_score": 4, "fields": {}}
    
    # Check loan term years and months
    for field in ["new_loan_term_years", "new_loan_term_months"]:
        correct_value = answer_key["task3"][field]
        submitted_value = submission["task3"][field]
        
        # Exact match for time periods
        if submitted_value == correct_value:
            field_score = 1
            field_feedback = "Correct"
        # Half credit if within 1 month/year
        elif abs(submitted_value - correct_value) <= 1:
            field_score = 0.5
            field_feedback = "Partially correct (within 1 unit)"
        else:
            field_score = 0
            field_feedback = "Incorrect"
        
        results["fields"][field] = {
            "score": field_score,
            "feedback": field_feedback,
            "submitted_value": submitted_value,
            "correct_value": correct_value
        }
        results["score"] += field_score
    
    # Check monetary values
    for field in ["total_interest_saved", "balance_after_5_years"]:
        correct_value = answer_key["task3"][field]
        submitted_value = submission["task3"][field]
        
        if abs(submitted_value - correct_value) <= 0.02:
            field_score = 1
            field_feedback = "Correct"
        elif abs(submitted_value - correct_value) <= 1.00:
            field_score = 0.5
            field_feedback = "Partially correct (within $1.00)"
        else:
            field_score = 0
            field_feedback = "Incorrect"
        
        results["fields"][field] = {
            "score": field_score,
            "feedback": field_feedback,
            "submitted_value": submitted_value,
            "correct_value": correct_value
        }
        results["score"] += field_score
    
    return results

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Balloon Payment Calculation."""
    results = {"score": 0, "max_score": 4, "fields": {}}
    
    for field in ["monthly_payment", "balloon_payment_amount"]:
        correct_value = answer_key["task4"][field]
        submitted_value = submission["task4"][field]
        
        if abs(submitted_value - correct_value) <= 0.02:
            field_score = 2
            field_feedback = "Correct"
        elif abs(submitted_value - correct_value) <= 1.00:
            field_score = 1
            field_feedback = "Partially correct (within $1.00)"
        else:
            field_score = 0
            field_feedback = "Incorrect"
        
        results["fields"][field] = {
            "score": field_score,
            "feedback": field_feedback,
            "submitted_value": submitted_value,
            "correct_value": correct_value
        }
        results["score"] += field_score
    
    return results

def evaluate_task5(submission, answer_key):
    """Evaluate Task 5: Refinance Analysis."""
    results = {"score": 0, "max_score": 4, "fields": {}}
    
    # Check monetary values
    for field in ["new_monthly_payment", "monthly_payment_savings"]:
        correct_value = answer_key["task5"][field]
        submitted_value = submission["task5"][field]
        
        if abs(submitted_value - correct_value) <= 0.02:
            field_score = 1.33
            field_feedback = "Correct"
        elif abs(submitted_value - correct_value) <= 1.00:
            field_score = 0.665
            field_feedback = "Partially correct (within $1.00)"
        else:
            field_score = 0
            field_feedback = "Incorrect"
        
        results["fields"][field] = {
            "score": field_score,
            "feedback": field_feedback,
            "submitted_value": submitted_value,
            "correct_value": correct_value
        }
        results["score"] += field_score
    
    # Check breakeven months
    field = "breakeven_months"
    correct_value = answer_key["task5"][field]
    submitted_value = submission["task5"][field]
    
    if submitted_value == correct_value:
        field_score = 1.34  # Adjusted to make total exactly 4 points
        field_feedback = "Correct"
    elif abs(submitted_value - correct_value) <= 1:
        field_score = 0.67
        field_feedback = "Partially correct (within 1 month)"
    else:
        field_score = 0
        field_feedback = "Incorrect"
    
    results["fields"][field] = {
        "score": field_score,
        "feedback": field_feedback,
        "submitted_value": submitted_value,
        "correct_value": correct_value
    }
    results["score"] += field_score
    
    # Round to 2 decimal places for consistency
    results["score"] = round(results["score"], 2)
    
    return results

def check_critical_tasks(task_results):
    """Check if candidate passed critical task requirements."""
    task1_passed = task_results["task1"]["score"] >= 1
    task2_passed = task_results["task2"]["score"] >= 3
    
    return {
        "task1_requirement_met": task1_passed,
        "task2_requirement_met": task2_passed,
        "all_critical_requirements_met": task1_passed and task2_passed
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the full submission against the answer key."""
    # Evaluate each task
    task_results = {
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key),
        "task4": evaluate_task4(submission, answer_key),
        "task5": evaluate_task5(submission, answer_key)
    }
    
    # Calculate total score
    total_score = sum(task_results[task]["score"] for task in task_results)
    max_score = sum(task_results[task]["max_score"] for task in task_results)
    overall_percentage = (total_score / max_score) * 100
    
    # Check critical task requirements
    critical_tasks_status = check_critical_tasks(task_results)
    
    # Determine if candidate passed
    passed = overall_percentage >= 80 and critical_tasks_status["all_critical_requirements_met"]
    
    return {
        "candidate_name": submission.get("candidate_name", "Unknown"),
        "task_results": task_results,
        "total_score": round(total_score, 2),
        "max_score": max_score,
        "overall_score": round(overall_percentage, 2),
        "critical_tasks_status": critical_tasks_status,
        "passed": passed
    }

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()