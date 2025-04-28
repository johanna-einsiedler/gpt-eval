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

def evaluate_exercise1(submission, answer_key):
    """Evaluate Exercise 1: Budget Analysis."""
    results = {
        "points_earned": 0,
        "points_possible": 7,
        "details": {}
    }
    
    # Evaluate errors identification (3 points)
    correct_errors = 0
    submission_errors = set()
    answer_key_errors = set()
    
    # Convert errors to sets for comparison
    for error in submission["errors"]:
        error_tuple = (error["row"], error["column"])
        submission_errors.add(error_tuple)
    
    for error in answer_key["errors"]:
        error_tuple = (error["row"], error["column"])
        answer_key_errors.add(error_tuple)
    
    # Count correct errors
    correct_errors = len(submission_errors.intersection(answer_key_errors))
    
    # Assign points for errors (3 points max)
    error_points = min(3, correct_errors)
    results["details"]["errors_identified"] = {
        "points_earned": error_points,
        "points_possible": 3,
        "correct_count": correct_errors,
        "total_count": 5
    }
    
    # Evaluate correct total cost (2 points)
    submission_total = submission["correct_total_cost"]
    answer_key_total = answer_key["correct_total_cost"]
    
    percent_diff = abs((submission_total - answer_key_total) / answer_key_total) * 100
    
    if percent_diff <= 0.5:
        total_cost_points = 2
    elif percent_diff <= 2:
        total_cost_points = 1
    else:
        total_cost_points = 0
    
    results["details"]["correct_total_cost"] = {
        "points_earned": total_cost_points,
        "points_possible": 2,
        "submitted_value": submission_total,
        "correct_value": answer_key_total,
        "percent_difference": percent_diff
    }
    
    # Evaluate R&D percentage (2 points)
    submission_rd = submission["rd_percentage"]
    answer_key_rd = answer_key["rd_percentage"]
    
    percent_diff = abs(submission_rd - answer_key_rd)
    
    if percent_diff <= 0.5:
        rd_points = 2
    elif percent_diff <= 2:
        rd_points = 1
    else:
        rd_points = 0
    
    results["details"]["rd_percentage"] = {
        "points_earned": rd_points,
        "points_possible": 2,
        "submitted_value": submission_rd,
        "correct_value": answer_key_rd,
        "absolute_difference": percent_diff
    }
    
    # Calculate total points for Exercise 1
    results["points_earned"] = error_points + total_cost_points + rd_points
    
    return results

def evaluate_exercise2(submission, answer_key):
    """Evaluate Exercise 2: ROI Analysis."""
    results = {
        "points_earned": 0,
        "points_possible": 7,
        "details": {}
    }
    
    # Evaluate ROI calculations (3 points)
    roi_fields = ["campaign_a_roi", "campaign_b_roi", "campaign_c_roi"]
    roi_points = 0
    
    for field in roi_fields:
        submission_value = submission[field]
        answer_key_value = answer_key[field]
        
        percent_diff = abs(submission_value - answer_key_value)
        
        if percent_diff <= 0.01:  # Within 0.01 (1% ROI)
            roi_points += 1
            accuracy = "correct"
        elif percent_diff <= 0.04:  # Within 0.04 (4% ROI)
            roi_points += 0.5
            accuracy = "partially_correct"
        else:
            accuracy = "incorrect"
            
        results["details"][field] = {
            "submitted_value": submission_value,
            "correct_value": answer_key_value,
            "absolute_difference": percent_diff,
            "accuracy": accuracy
        }
    
    results["details"]["roi_calculations"] = {
        "points_earned": roi_points,
        "points_possible": 3
    }
    
    # Evaluate highest ROI campaign (1 point)
    if submission["highest_roi_campaign"] == answer_key["highest_roi_campaign"]:
        highest_roi_points = 1
        accuracy = "correct"
    else:
        highest_roi_points = 0
        accuracy = "incorrect"
    
    results["details"]["highest_roi_campaign"] = {
        "points_earned": highest_roi_points,
        "points_possible": 1,
        "submitted_value": submission["highest_roi_campaign"],
        "correct_value": answer_key["highest_roi_campaign"],
        "accuracy": accuracy
    }
    
    # Evaluate blended ROI (2 points)
    submission_blended = submission["blended_roi"]
    answer_key_blended = answer_key["blended_roi"]
    
    percent_diff = abs(submission_blended - answer_key_blended)
    
    if percent_diff <= 0.01:  # Within 0.01 (1% ROI)
        blended_roi_points = 2
        accuracy = "correct"
    elif percent_diff <= 0.04:  # Within 0.04 (4% ROI)
        blended_roi_points = 1
        accuracy = "partially_correct"
    else:
        blended_roi_points = 0
        accuracy = "incorrect"
    
    results["details"]["blended_roi"] = {
        "points_earned": blended_roi_points,
        "points_possible": 2,
        "submitted_value": submission_blended,
        "correct_value": answer_key_blended,
        "absolute_difference": percent_diff,
        "accuracy": accuracy
    }
    
    # Evaluate break-even point (1 point)
    submission_breakeven = submission["campaign_b_breakeven_units"]
    answer_key_breakeven = answer_key["campaign_b_breakeven_units"]
    
    percent_diff = abs((submission_breakeven - answer_key_breakeven) / answer_key_breakeven) * 100
    
    if percent_diff <= 0.5:
        breakeven_points = 1
        accuracy = "correct"
    elif percent_diff <= 2:
        breakeven_points = 0.5
        accuracy = "partially_correct"
    else:
        breakeven_points = 0
        accuracy = "incorrect"
    
    results["details"]["campaign_b_breakeven_units"] = {
        "points_earned": breakeven_points,
        "points_possible": 1,
        "submitted_value": submission_breakeven,
        "correct_value": answer_key_breakeven,
        "percent_difference": percent_diff,
        "accuracy": accuracy
    }
    
    # Calculate total points for Exercise 2
    results["points_earned"] = roi_points + highest_roi_points + blended_roi_points + breakeven_points
    
    return results

def evaluate_exercise3(submission, answer_key):
    """Evaluate Exercise 3: Product Launch Financial Projection."""
    results = {
        "points_earned": 0,
        "points_possible": 6,
        "details": {}
    }
    
    # Evaluate total annual revenue (1.5 points)
    submission_revenue = submission["total_annual_revenue"]
    answer_key_revenue = answer_key["total_annual_revenue"]
    
    percent_diff = abs((submission_revenue - answer_key_revenue) / answer_key_revenue) * 100
    
    if percent_diff <= 0.5:
        revenue_points = 1.5
        accuracy = "correct"
    elif percent_diff <= 2:
        revenue_points = 0.75
        accuracy = "partially_correct"
    else:
        revenue_points = 0
        accuracy = "incorrect"
    
    results["details"]["total_annual_revenue"] = {
        "points_earned": revenue_points,
        "points_possible": 1.5,
        "submitted_value": submission_revenue,
        "correct_value": answer_key_revenue,
        "percent_difference": percent_diff,
        "accuracy": accuracy
    }
    
    # Evaluate total annual profit (1.5 points)
    submission_profit = submission["total_annual_profit"]
    answer_key_profit = answer_key["total_annual_profit"]
    
    percent_diff = abs((submission_profit - answer_key_profit) / answer_key_profit) * 100
    
    if percent_diff <= 0.5:
        profit_points = 1.5
        accuracy = "correct"
    elif percent_diff <= 2:
        profit_points = 0.75
        accuracy = "partially_correct"
    else:
        profit_points = 0
        accuracy = "incorrect"
    
    results["details"]["total_annual_profit"] = {
        "points_earned": profit_points,
        "points_possible": 1.5,
        "submitted_value": submission_profit,
        "correct_value": answer_key_profit,
        "percent_difference": percent_diff,
        "accuracy": accuracy
    }
    
    # Evaluate break-even month (1.5 points)
    submission_month = submission["breakeven_month"]
    answer_key_month = answer_key["breakeven_month"]
    
    if submission_month == answer_key_month:
        month_points = 1.5
        accuracy = "correct"
    elif abs(submission_month - answer_key_month) == 1:
        month_points = 0.75
        accuracy = "partially_correct"
    else:
        month_points = 0
        accuracy = "incorrect"
    
    results["details"]["breakeven_month"] = {
        "points_earned": month_points,
        "points_possible": 1.5,
        "submitted_value": submission_month,
        "correct_value": answer_key_month,
        "difference": abs(submission_month - answer_key_month),
        "accuracy": accuracy
    }
    
    # Evaluate annual profit margin percentage (1.5 points)
    submission_margin = submission["annual_profit_margin_percentage"]
    answer_key_margin = answer_key["annual_profit_margin_percentage"]
    
    percent_diff = abs(submission_margin - answer_key_margin)
    
    if percent_diff <= 0.5:
        margin_points = 1.5
        accuracy = "correct"
    elif percent_diff <= 2:
        margin_points = 0.75
        accuracy = "partially_correct"
    else:
        margin_points = 0
        accuracy = "incorrect"
    
    results["details"]["annual_profit_margin_percentage"] = {
        "points_earned": margin_points,
        "points_possible": 1.5,
        "submitted_value": submission_margin,
        "correct_value": answer_key_margin,
        "absolute_difference": percent_diff,
        "accuracy": accuracy
    }
    
    # Calculate total points for Exercise 3
    results["points_earned"] = revenue_points + profit_points + month_points + margin_points
    
    return results

def check_critical_failures(results):
    """Check for critical failures that would result in automatic failure."""
    critical_failures = []
    
    # Check if any exercise was completely skipped
    for exercise in ["exercise1", "exercise2", "exercise3"]:
        if results[exercise]["points_earned"] == 0:
            critical_failures.append(f"{exercise} was completely skipped or incorrect")
    
    # Check if any exercise scored less than 40%
    for exercise in ["exercise1", "exercise2", "exercise3"]:
        score_percentage = (results[exercise]["points_earned"] / results[exercise]["points_possible"]) * 100
        if score_percentage < 40:
            critical_failures.append(f"{exercise} scored less than 40% ({score_percentage:.2f}%)")
    
    return critical_failures

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load JSON files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each exercise
    results = {
        "candidate_id": submission.get("candidate_id", "UNKNOWN"),
        "exercise1": evaluate_exercise1(submission["exercise1"], answer_key["exercise1"]),
        "exercise2": evaluate_exercise2(submission["exercise2"], answer_key["exercise2"]),
        "exercise3": evaluate_exercise3(submission["exercise3"], answer_key["exercise3"]),
    }
    
    # Calculate total points
    total_points_earned = (
        results["exercise1"]["points_earned"] +
        results["exercise2"]["points_earned"] +
        results["exercise3"]["points_earned"]
    )
    
    total_points_possible = (
        results["exercise1"]["points_possible"] +
        results["exercise2"]["points_possible"] +
        results["exercise3"]["points_possible"]
    )
    
    # Calculate overall score as a percentage
    overall_score = (total_points_earned / total_points_possible) * 100
    
    # Check for critical failures
    critical_failures = check_critical_failures(results)
    
    # Add summary to results
    results["summary"] = {
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "overall_score": overall_score,
        "passing_threshold": 70,
        "passed": overall_score >= 70 and not critical_failures,
        "critical_failures": critical_failures
    }
    
    # Add overall score as a separate field as required
    results["overall_score"] = overall_score
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {overall_score:.2f}%")
    if critical_failures:
        print("Critical failures detected:")
        for failure in critical_failures:
            print(f"- {failure}")
    print(f"Result: {'PASS' if results['summary']['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()