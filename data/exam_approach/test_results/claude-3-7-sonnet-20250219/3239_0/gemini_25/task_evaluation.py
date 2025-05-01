#!/usr/bin/env python3
import json
import sys
import math

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Budget Variance Analysis"""
    correct_variance = submission["task1"]["budget_variance_total"] == answer_key["task1"]["budget_variance_total"]
    correct_category = submission["task1"]["highest_overspend_category"] == answer_key["task1"]["highest_overspend_category"]
    
    return {
        "budget_variance_correct": correct_variance,
        "highest_overspend_category_correct": correct_category,
        "passed": correct_variance and correct_category,
        "comments": "Both answers must be correct to pass this task."
    }

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Calculate Key Performance Metrics"""
    # Check if each metric is within ±5% of the correct value
    response_rate_within_tolerance = abs(submission["task2"]["response_rate"] - answer_key["task2"]["response_rate"]) <= 0.05 * answer_key["task2"]["response_rate"]
    cpa_within_tolerance = abs(submission["task2"]["cost_per_acquisition"] - answer_key["task2"]["cost_per_acquisition"]) <= 0.05 * answer_key["task2"]["cost_per_acquisition"]
    roi_within_tolerance = abs(submission["task2"]["roi"] - answer_key["task2"]["roi"]) <= 0.05 * answer_key["task2"]["roi"]
    
    all_metrics_correct = response_rate_within_tolerance and cpa_within_tolerance and roi_within_tolerance
    
    return {
        "response_rate_within_tolerance": response_rate_within_tolerance,
        "cpa_within_tolerance": cpa_within_tolerance,
        "roi_within_tolerance": roi_within_tolerance,
        "passed": all_metrics_correct,
        "comments": "All three metrics must be within ±5% of the correct values to pass this task."
    }

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Channel Performance Evaluation"""
    best_channel_correct = submission["task3"]["best_performing_channel"] == answer_key["task3"]["best_performing_channel"]
    worst_channel_correct = submission["task3"]["worst_performing_channel"] == answer_key["task3"]["worst_performing_channel"]
    
    return {
        "best_channel_correct": best_channel_correct,
        "worst_channel_correct": worst_channel_correct,
        "passed": best_channel_correct and worst_channel_correct,
        "comments": "Both channel identifications must be correct to pass this task."
    }

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Benchmark Comparison"""
    # Check if each variance is within ±0.05 of the correct value
    ctr_variance_correct = abs(submission["task4"]["benchmark_comparison"]["ctr_variance"] - answer_key["task4"]["benchmark_comparison"]["ctr_variance"]) <= 0.05
    cpa_variance_correct = abs(submission["task4"]["benchmark_comparison"]["cpa_variance"] - answer_key["task4"]["benchmark_comparison"]["cpa_variance"]) <= 0.05
    roi_variance_correct = abs(submission["task4"]["benchmark_comparison"]["roi_variance"] - answer_key["task4"]["benchmark_comparison"]["roi_variance"]) <= 0.05
    
    correct_count = sum([ctr_variance_correct, cpa_variance_correct, roi_variance_correct])
    
    return {
        "ctr_variance_correct": ctr_variance_correct,
        "cpa_variance_correct": cpa_variance_correct,
        "roi_variance_correct": roi_variance_correct,
        "correct_count": correct_count,
        "passed": correct_count >= 2,
        "comments": "At least 2 out of 3 variance calculations must be within ±0.05 of the correct values to pass this task."
    }

def evaluate_task5(submission, answer_key):
    """Evaluate Task 5: Budget Reallocation"""
    budget_allocation = submission["task5"]["budget_reallocation"]
    
    # Check if the total budget is exactly $100,000
    total_budget = sum(budget_allocation.values())
    total_correct = total_budget == 100000
    
    # Check if each channel gets at least $10,000
    min_allocation_correct = all(amount >= 10000 for amount in budget_allocation.values())
    
    # Check if all allocations are in increments of $5,000
    increments_correct = all(amount % 5000 == 0 for amount in budget_allocation.values())
    
    # Check if the allocation is logical based on performance
    # This is a simplified check - we're comparing with the answer key's allocation
    # to see if the relative ordering of channel budgets is similar
    
    # Get the channel order from highest to lowest budget in the submission
    submission_order = sorted(budget_allocation.keys(), key=lambda x: budget_allocation[x], reverse=True)
    
    # Get the channel order from highest to lowest budget in the answer key
    answer_key_order = sorted(answer_key["task5"]["budget_reallocation"].keys(), 
                             key=lambda x: answer_key["task5"]["budget_reallocation"][x], 
                             reverse=True)
    
    # Check if the top 2 channels match (not necessarily in the same order)
    top_channels_match = set(submission_order[:2]) == set(answer_key_order[:2])
    
    # Check if the bottom 2 channels match (not necessarily in the same order)
    bottom_channels_match = set(submission_order[2:]) == set(answer_key_order[2:])
    
    logical_allocation = top_channels_match and bottom_channels_match
    
    all_criteria_met = total_correct and min_allocation_correct and increments_correct and logical_allocation
    
    return {
        "total_budget_correct": total_correct,
        "minimum_allocation_correct": min_allocation_correct,
        "increments_correct": increments_correct,
        "logical_allocation": logical_allocation,
        "passed": all_criteria_met,
        "comments": "Budget allocation must sum to $100,000, allocate at least $10,000 to each channel, use increments of $5,000, and show a logical relationship to performance."
    }

def evaluate_submission(submission_file, answer_key_file):
    """Evaluate the candidate's submission against the answer key"""
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
        
        # Evaluate each task
        task1_results = evaluate_task1(submission, answer_key)
        task2_results = evaluate_task2(submission, answer_key)
        task3_results = evaluate_task3(submission, answer_key)
        task4_results = evaluate_task4(submission, answer_key)
        task5_results = evaluate_task5(submission, answer_key)
        
        # Count passed tasks
        passed_tasks = sum([
            task1_results["passed"],
            task2_results["passed"],
            task3_results["passed"],
            task4_results["passed"],
            task5_results["passed"]
        ])
        
        # Calculate overall score as a percentage
        overall_score = (passed_tasks / 5) * 100
        
        # Determine if the candidate passed overall (needs 4 out of 5 tasks)
        overall_passed = passed_tasks >= 4
        
        # Compile results
        results = {
            "candidate_id": submission.get("candidate_id", "Unknown"),
            "task1_evaluation": task1_results,
            "task2_evaluation": task2_results,
            "task3_evaluation": task3_results,
            "task4_evaluation": task4_results,
            "task5_evaluation": task5_results,
            "passed_tasks": passed_tasks,
            "total_tasks": 5,
            "overall_score": overall_score,
            "overall_passed": overall_passed,
            "overall_comments": "Candidate must successfully complete at least 4 out of the 5 tasks to pass the exam."
        }
        
        return results
    
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0,
            "overall_passed": False
        }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Overall result: {'PASSED' if results['overall_passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()