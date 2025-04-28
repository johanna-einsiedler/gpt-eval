#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    score = 0
    feedback = []
    
    # Check discrepancies identification (10 points)
    if len(submission.get("discrepancies_found", [])) == len(answer_key.get("discrepancies_found", [])):
        score += 10
        feedback.append("Correctly identified that there are no transaction amount discrepancies.")
    else:
        feedback.append("Incorrectly identified transaction amount discrepancies.")
    
    # Check account balance verification (10 points)
    if submission.get("account_balance_correct") == answer_key.get("account_balance_correct"):
        score += 10
        feedback.append("Correctly verified the final account balance.")
    else:
        feedback.append("Incorrectly verified the final account balance.")
    
    return {
        "score": score,
        "max_score": 20,
        "feedback": feedback
    }

def evaluate_task2(submission, answer_key):
    score = 0
    feedback = []
    
    # Check over-budget categories identification (20 points)
    submission_categories = {item.get("category") for item in submission.get("over_budget_categories", [])}
    answer_key_categories = {item.get("category") for item in answer_key.get("over_budget_categories", [])}
    
    correct_categories = submission_categories.intersection(answer_key_categories)
    
    if len(correct_categories) == len(answer_key_categories):
        score += 20
        feedback.append("Correctly identified all over-budget categories.")
    elif len(correct_categories) >= 3:
        score += 15
        feedback.append(f"Identified {len(correct_categories)} of {len(answer_key_categories)} over-budget categories.")
    elif len(correct_categories) > 0:
        score += 10
        feedback.append(f"Identified only {len(correct_categories)} of {len(answer_key_categories)} over-budget categories.")
    else:
        feedback.append("Failed to identify any over-budget categories correctly.")
    
    # Check total variance calculation (10 points)
    submission_variance = submission.get("total_variance", 0)
    answer_key_variance = answer_key.get("total_variance", 0)
    
    if abs(submission_variance - answer_key_variance) <= 10:
        score += 10
        feedback.append("Correctly calculated the total variance within acceptable margin.")
    else:
        feedback.append("Incorrectly calculated the total variance.")
    
    # Check percent over budget calculation (10 points)
    submission_percent = submission.get("percent_over_budget", 0)
    answer_key_percent = answer_key.get("percent_over_budget", 0)
    
    if abs(submission_percent - answer_key_percent) <= 0.5:
        score += 10
        feedback.append("Correctly calculated the percent over budget within acceptable margin.")
    else:
        feedback.append("Incorrectly calculated the percent over budget.")
    
    return {
        "score": score,
        "max_score": 40,
        "feedback": feedback
    }

def evaluate_task3(submission, answer_key):
    score = 0
    feedback = []
    
    # Check missing entries identification (30 points)
    submission_missing_entries = {(item.get("transaction_id"), item.get("date")) 
                                 for item in submission.get("missing_entries", [])}
    answer_key_missing_entries = {(item.get("transaction_id"), item.get("date")) 
                                 for item in answer_key.get("missing_entries", [])}
    
    correct_entries = submission_missing_entries.intersection(answer_key_missing_entries)
    
    if len(correct_entries) == len(answer_key_missing_entries):
        score += 30
        feedback.append("Correctly identified all missing entries.")
    elif len(correct_entries) >= 1:
        score += 15
        feedback.append(f"Identified {len(correct_entries)} of {len(answer_key_missing_entries)} missing entries.")
    else:
        feedback.append("Failed to identify any missing entries correctly.")
    
    # Check total collection verification (10 points)
    submission_total = submission.get("total_collection_reported", 0)
    answer_key_total = answer_key.get("total_collection_reported", 0)
    
    if abs(submission_total - answer_key_total) <= 0.1:
        score += 10
        feedback.append("Correctly verified the total collection amount.")
    else:
        feedback.append("Incorrectly verified the total collection amount.")
    
    return {
        "score": score,
        "max_score": 40,
        "feedback": feedback
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    task2_results = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    task3_results = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Determine performance level
    if overall_percentage >= 90:
        performance_level = "Excellent"
    elif overall_percentage >= 75:
        performance_level = "Good"
    elif overall_percentage >= 60:
        performance_level = "Pass"
    else:
        performance_level = "Fail"
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": round(overall_percentage, 2),
        "performance_level": performance_level,
        "pass_fail": "Pass" if overall_percentage >= 60 else "Fail"
    }
    
    # Save results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {round(overall_percentage, 2)}% - {performance_level} ({results['pass_fail']})")

if __name__ == "__main__":
    main()