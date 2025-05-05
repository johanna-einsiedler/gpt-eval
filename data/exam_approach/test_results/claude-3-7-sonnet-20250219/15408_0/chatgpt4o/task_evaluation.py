#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_numeric_answer(candidate_value, correct_value):
    """
    Evaluate a numeric answer and return points awarded.
    Full credit (1 point): Within ±1% of correct value
    Partial credit (0.5 points): Within ±5% of correct value
    No credit (0 points): Off by more than ±5%
    """
    if correct_value == 0:
        # Avoid division by zero
        return 1 if candidate_value == 0 else 0
    
    percentage_diff = abs((candidate_value - correct_value) / correct_value * 100)
    
    if percentage_diff <= 1:
        return 1.0  # Full credit
    elif percentage_diff <= 5:
        return 0.5  # Partial credit
    else:
        return 0.0  # No credit

def evaluate_list_answer(candidate_list, correct_list):
    """Evaluate a list answer and return points awarded."""
    # For simplicity, we'll check if the lists contain the same elements
    # regardless of order for this specific case
    if set(candidate_list) == set(correct_list):
        return 1.0
    else:
        return 0.0

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "task1": {"points": 0, "details": {}},
        "task2": {"points": 0, "details": {}},
        "task3": {"points": 0, "details": {}},
        "total_points": 0,
        "max_points": 16,
        "overall_score": 0
    }
    
    # Task 1 evaluation (5 points)
    task1_fields = ["personnel_costs", "equipment_maintenance_costs", "consumables_costs", 
                   "training_costs", "total_budget"]
    
    for field in task1_fields:
        candidate_value = submission["task1"].get(field, 0)
        correct_value = answer_key["task1"].get(field, 0)
        points = evaluate_numeric_answer(candidate_value, correct_value)
        results["task1"]["details"][field] = {
            "candidate_value": candidate_value,
            "correct_value": correct_value,
            "points": points
        }
        results["task1"]["points"] += points
    
    # Task 2 evaluation (7 points)
    # Category variances (5 points)
    results["task2"]["details"]["category_variances"] = {}
    
    for category, values in answer_key["task2"]["category_variances"].items():
        results["task2"]["details"]["category_variances"][category] = {}
        
        if category in submission["task2"]["category_variances"]:
            # Dollar variance
            candidate_dollar = submission["task2"]["category_variances"][category].get("dollar_variance", 0)
            correct_dollar = values["dollar_variance"]
            dollar_points = evaluate_numeric_answer(candidate_dollar, correct_dollar)
            
            # Percentage variance
            candidate_percent = submission["task2"]["category_variances"][category].get("percentage_variance", 0)
            correct_percent = values["percentage_variance"]
            percent_points = evaluate_numeric_answer(candidate_percent, correct_percent)
            
            # Store results
            results["task2"]["details"]["category_variances"][category] = {
                "dollar_variance": {
                    "candidate_value": candidate_dollar,
                    "correct_value": correct_dollar,
                    "points": dollar_points
                },
                "percentage_variance": {
                    "candidate_value": candidate_percent,
                    "correct_value": correct_percent,
                    "points": percent_points
                }
            }
            
            # Only count one point per category (combining dollar and percentage)
            category_point = max(dollar_points, percent_points)
            results["task2"]["points"] += category_point
        else:
            results["task2"]["details"]["category_variances"][category] = {
                "error": "Category missing in submission",
                "points": 0
            }
    
    # Largest variance categories (1 point)
    candidate_largest = submission["task2"].get("largest_variance_categories", [])
    correct_largest = answer_key["task2"]["largest_variance_categories"]
    largest_points = evaluate_list_answer(candidate_largest, correct_largest)
    results["task2"]["details"]["largest_variance_categories"] = {
        "candidate_value": candidate_largest,
        "correct_value": correct_largest,
        "points": largest_points
    }
    results["task2"]["points"] += largest_points
    
    # Total variance (1 point)
    candidate_total_dollars = submission["task2"].get("total_variance_dollars", 0)
    correct_total_dollars = answer_key["task2"]["total_variance_dollars"]
    total_dollars_points = evaluate_numeric_answer(candidate_total_dollars, correct_total_dollars)
    
    candidate_total_percent = submission["task2"].get("total_variance_percentage", 0)
    correct_total_percent = answer_key["task2"]["total_variance_percentage"]
    total_percent_points = evaluate_numeric_answer(candidate_total_percent, correct_total_percent)
    
    results["task2"]["details"]["total_variance"] = {
        "dollars": {
            "candidate_value": candidate_total_dollars,
            "correct_value": correct_total_dollars,
            "points": total_dollars_points
        },
        "percentage": {
            "candidate_value": candidate_total_percent,
            "correct_value": correct_total_percent,
            "points": total_percent_points
        }
    }
    
    # Only count one point for total variance (combining dollar and percentage)
    total_variance_point = max(total_dollars_points, total_percent_points)
    results["task2"]["points"] += total_variance_point
    
    # Task 3 evaluation (4 points)
    task3_fields = ["total_cost_of_ownership", "annual_cost_savings", 
                   "roi_percentage", "payback_period_months"]
    
    for field in task3_fields:
        candidate_value = submission["task3"].get(field, 0)
        correct_value = answer_key["task3"].get(field, 0)
        points = evaluate_numeric_answer(candidate_value, correct_value)
        results["task3"]["details"][field] = {
            "candidate_value": candidate_value,
            "correct_value": correct_value,
            "points": points
        }
        results["task3"]["points"] += points
    
    # Calculate total points and overall score
    total_points = results["task1"]["points"] + results["task2"]["points"] + results["task3"]["points"]
    results["total_points"] = total_points
    results["overall_score"] = (total_points / results["max_points"]) * 100
    
    # Determine pass/fail status
    if total_points >= 14:
        results["status"] = "Pass with Distinction"
    elif total_points >= 12:
        results["status"] = "Pass"
    else:
        results["status"] = "Fail"
    
    return results

def main():
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
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Status: {results['status']}")

if __name__ == "__main__":
    main()