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
    """Evaluate Task 1: Annual Operating Budget Preparation."""
    results = {"points_earned": 0, "points_possible": 40, "details": {}}
    
    # Evaluate fuel costs (8 points)
    sub_fuel = submission["task1"]["annual_budget"]["fuel_costs"]
    key_fuel = answer_key["task1"]["annual_budget"]["fuel_costs"]
    fuel_error = abs((sub_fuel - key_fuel) / key_fuel) if key_fuel != 0 else float('inf')
    fuel_points = 8 if fuel_error <= 0.01 else 0
    results["details"]["fuel_costs"] = {
        "points_earned": fuel_points,
        "points_possible": 8,
        "submitted_value": sub_fuel,
        "correct_value": key_fuel,
        "error_percentage": round(fuel_error * 100, 2)
    }
    results["points_earned"] += fuel_points
    
    # Evaluate maintenance costs (8 points)
    sub_maint = submission["task1"]["annual_budget"]["maintenance_costs"]
    key_maint = answer_key["task1"]["annual_budget"]["maintenance_costs"]
    maint_error = abs((sub_maint - key_maint) / key_maint) if key_maint != 0 else float('inf')
    maint_points = 8 if maint_error <= 0.01 else 0
    results["details"]["maintenance_costs"] = {
        "points_earned": maint_points,
        "points_possible": 8,
        "submitted_value": sub_maint,
        "correct_value": key_maint,
        "error_percentage": round(maint_error * 100, 2)
    }
    results["points_earned"] += maint_points
    
    # Evaluate labor costs (8 points)
    sub_labor = submission["task1"]["annual_budget"]["labor_costs"]
    key_labor = answer_key["task1"]["annual_budget"]["labor_costs"]
    labor_error = abs((sub_labor - key_labor) / key_labor) if key_labor != 0 else float('inf')
    labor_points = 8 if labor_error <= 0.01 else 0
    results["details"]["labor_costs"] = {
        "points_earned": labor_points,
        "points_possible": 8,
        "submitted_value": sub_labor,
        "correct_value": key_labor,
        "error_percentage": round(labor_error * 100, 2)
    }
    results["points_earned"] += labor_points
    
    # Evaluate overhead costs (8 points)
    sub_overhead = submission["task1"]["annual_budget"]["overhead_costs"]
    key_overhead = answer_key["task1"]["annual_budget"]["overhead_costs"]
    overhead_error = abs((sub_overhead - key_overhead) / key_overhead) if key_overhead != 0 else float('inf')
    overhead_points = 8 if overhead_error <= 0.01 else 0
    results["details"]["overhead_costs"] = {
        "points_earned": overhead_points,
        "points_possible": 8,
        "submitted_value": sub_overhead,
        "correct_value": key_overhead,
        "error_percentage": round(overhead_error * 100, 2)
    }
    results["points_earned"] += overhead_points
    
    # Evaluate total annual budget (4 points)
    sub_total = submission["task1"]["annual_budget"]["total_annual_budget"]
    key_total = answer_key["task1"]["annual_budget"]["total_annual_budget"]
    total_error = abs((sub_total - key_total) / key_total) if key_total != 0 else float('inf')
    total_points = 4 if total_error <= 0.01 else 0
    results["details"]["total_annual_budget"] = {
        "points_earned": total_points,
        "points_possible": 4,
        "submitted_value": sub_total,
        "correct_value": key_total,
        "error_percentage": round(total_error * 100, 2)
    }
    results["points_earned"] += total_points
    
    # Evaluate cost per MWh (4 points)
    sub_cost_per_mwh = submission["task1"]["cost_per_mwh"]
    key_cost_per_mwh = answer_key["task1"]["cost_per_mwh"]
    cost_per_mwh_error = abs(sub_cost_per_mwh - key_cost_per_mwh)
    cost_per_mwh_points = 4 if cost_per_mwh_error <= 0.1 else 0
    results["details"]["cost_per_mwh"] = {
        "points_earned": cost_per_mwh_points,
        "points_possible": 4,
        "submitted_value": sub_cost_per_mwh,
        "correct_value": key_cost_per_mwh,
        "absolute_error": round(cost_per_mwh_error, 2)
    }
    results["points_earned"] += cost_per_mwh_points
    
    # Calculate percentage score for the task
    results["percentage_score"] = (results["points_earned"] / results["points_possible"]) * 100
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Budget Variance Analysis."""
    results = {"points_earned": 0, "points_possible": 30, "details": {}}
    
    # Evaluate variance percentages (16 points total, 4 points each)
    variance_categories = [
        "fuel_variance_percentage",
        "maintenance_variance_percentage",
        "labor_variance_percentage",
        "overhead_variance_percentage"
    ]
    
    for category in variance_categories:
        sub_value = submission["task2"]["variance_analysis"][category]
        key_value = answer_key["task2"]["variance_analysis"][category]
        error = abs(sub_value - key_value)
        points = 4 if error <= 0.1 else 0
        results["details"][category] = {
            "points_earned": points,
            "points_possible": 4,
            "submitted_value": sub_value,
            "correct_value": key_value,
            "absolute_error": round(error, 2)
        }
        results["points_earned"] += points
    
    # Evaluate primary variance category (7 points)
    sub_primary = submission["task2"]["primary_variance_category"]
    key_primary = answer_key["task2"]["primary_variance_category"]
    primary_points = 7 if sub_primary == key_primary else 0
    results["details"]["primary_variance_category"] = {
        "points_earned": primary_points,
        "points_possible": 7,
        "submitted_value": sub_primary,
        "correct_value": key_primary,
        "is_correct": sub_primary == key_primary
    }
    results["points_earned"] += primary_points
    
    # Evaluate corrective action code (7 points)
    sub_action = submission["task2"]["corrective_action_code"]
    key_action = answer_key["task2"]["corrective_action_code"]
    action_points = 7 if sub_action == key_action else 0
    results["details"]["corrective_action_code"] = {
        "points_earned": action_points,
        "points_possible": 7,
        "submitted_value": sub_action,
        "correct_value": key_action,
        "is_correct": sub_action == key_action
    }
    results["points_earned"] += action_points
    
    # Calculate percentage score for the task
    results["percentage_score"] = (results["points_earned"] / results["points_possible"]) * 100
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Capital Expenditure Evaluation."""
    results = {"points_earned": 0, "points_possible": 30, "details": {}}
    
    # Evaluate total investment (6 points)
    sub_investment = submission["task3"]["capex_evaluation"]["total_investment"]
    key_investment = answer_key["task3"]["capex_evaluation"]["total_investment"]
    investment_error = abs((sub_investment - key_investment) / key_investment) if key_investment != 0 else float('inf')
    investment_points = 6 if investment_error <= 0.01 else 0
    results["details"]["total_investment"] = {
        "points_earned": investment_points,
        "points_possible": 6,
        "submitted_value": sub_investment,
        "correct_value": key_investment,
        "error_percentage": round(investment_error * 100, 2)
    }
    results["points_earned"] += investment_points
    
    # Evaluate annual savings (8 points)
    sub_savings = submission["task3"]["capex_evaluation"]["annual_savings"]
    key_savings = answer_key["task3"]["capex_evaluation"]["annual_savings"]
    savings_error = abs((sub_savings - key_savings) / key_savings) if key_savings != 0 else float('inf')
    savings_points = 8 if savings_error <= 0.01 else 0
    results["details"]["annual_savings"] = {
        "points_earned": savings_points,
        "points_possible": 8,
        "submitted_value": sub_savings,
        "correct_value": key_savings,
        "error_percentage": round(savings_error * 100, 2)
    }
    results["points_earned"] += savings_points
    
    # Evaluate payback period (6 points)
    sub_payback = submission["task3"]["capex_evaluation"]["payback_period"]
    key_payback = answer_key["task3"]["capex_evaluation"]["payback_period"]
    payback_error = abs(sub_payback - key_payback)
    payback_points = 6 if payback_error <= 0.1 else 0
    results["details"]["payback_period"] = {
        "points_earned": payback_points,
        "points_possible": 6,
        "submitted_value": sub_payback,
        "correct_value": key_payback,
        "absolute_error": round(payback_error, 2)
    }
    results["points_earned"] += payback_points
    
    # Evaluate five-year ROI (6 points)
    sub_roi = submission["task3"]["capex_evaluation"]["five_year_roi"]
    key_roi = answer_key["task3"]["capex_evaluation"]["five_year_roi"]
    roi_error = abs(sub_roi - key_roi)
    roi_points = 6 if roi_error <= 0.1 else 0
    results["details"]["five_year_roi"] = {
        "points_earned": roi_points,
        "points_possible": 6,
        "submitted_value": sub_roi,
        "correct_value": key_roi,
        "absolute_error": round(roi_error, 2)
    }
    results["points_earned"] += roi_points
    
    # Evaluate recommendation code (4 points)
    sub_recommendation = submission["task3"]["recommendation_code"]
    key_recommendation = answer_key["task3"]["recommendation_code"]
    recommendation_points = 4 if sub_recommendation == key_recommendation else 0
    results["details"]["recommendation_code"] = {
        "points_earned": recommendation_points,
        "points_possible": 4,
        "submitted_value": sub_recommendation,
        "correct_value": key_recommendation,
        "is_correct": sub_recommendation == key_recommendation
    }
    results["points_earned"] += recommendation_points
    
    # Calculate percentage score for the task
    results["percentage_score"] = (results["points_earned"] / results["points_possible"]) * 100
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key),
    }
    
    # Calculate overall score
    total_points_earned = (
        results["task1"]["points_earned"] + 
        results["task2"]["points_earned"] + 
        results["task3"]["points_earned"]
    )
    total_points_possible = (
        results["task1"]["points_possible"] + 
        results["task2"]["points_possible"] + 
        results["task3"]["points_possible"]
    )
    results["overall_score"] = (total_points_earned / total_points_possible) * 100
    
    # Determine if the candidate passed
    task1_percentage = results["task1"]["percentage_score"]
    task2_percentage = results["task2"]["percentage_score"]
    task3_percentage = results["task3"]["percentage_score"]
    
    # Check critical calculations
    fuel_costs_error = abs((submission["task1"]["annual_budget"]["fuel_costs"] - 
                           answer_key["task1"]["annual_budget"]["fuel_costs"]) / 
                           answer_key["task1"]["annual_budget"]["fuel_costs"])
    
    primary_variance_correct = (submission["task2"]["primary_variance_category"] == 
                               answer_key["task2"]["primary_variance_category"])
    
    payback_period_error = abs((submission["task3"]["capex_evaluation"]["payback_period"] - 
                               answer_key["task3"]["capex_evaluation"]["payback_period"]) / 
                               answer_key["task3"]["capex_evaluation"]["payback_period"])
    
    critical_calcs_ok = (fuel_costs_error <= 0.1 and 
                         primary_variance_correct and 
                         payback_period_error <= 0.1)
    
    # Determine if passed based on criteria
    passed = (
        results["overall_score"] >= 75 and
        task1_percentage >= 50 and
        task2_percentage >= 50 and
        task3_percentage >= 50 and
        critical_calcs_ok
    )
    
    results["passed"] = passed
    results["pass_criteria"] = {
        "overall_score_sufficient": results["overall_score"] >= 75,
        "task1_score_sufficient": task1_percentage >= 50,
        "task2_score_sufficient": task2_percentage >= 50,
        "task3_score_sufficient": task3_percentage >= 50,
        "critical_calculations_accurate": critical_calcs_ok
    }
    
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
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()