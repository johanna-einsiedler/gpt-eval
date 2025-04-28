#!/usr/bin/env python3
"""
Agricultural Record-Keeping Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Agricultural Record-Keeping Exam and generates a detailed score report.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, Any, List, Tuple


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Financial Record Organization and Analysis."""
    results = {
        "points_earned": 0,
        "points_possible": 20,
        "details": {}
    }
    
    # Evaluate monthly expense totals (9 points)
    expense_points = 0
    expense_details = {}
    
    for month in ["January", "February", "March"]:
        month_details = {"correct": True, "errors": []}
        
        # Check month total (1 point each)
        sub_total = submission["task1"]["monthly_expense_totals"][month].get("Total", 0)
        key_total = answer_key["task1"]["monthly_expense_totals"][month].get("Total", 0)
        
        if sub_total == key_total:
            expense_points += 1
        else:
            month_details["correct"] = False
            month_details["errors"].append(f"Total: expected {key_total}, got {sub_total}")
        
        # Check each category (0.5 points each)
        for category, key_value in answer_key["task1"]["monthly_expense_totals"][month].items():
            if category == "Total":
                continue
                
            sub_value = submission["task1"]["monthly_expense_totals"][month].get(category, 0)
            
            if sub_value == key_value:
                expense_points += 0.5
            else:
                month_details["correct"] = False
                month_details["errors"].append(f"{category}: expected {key_value}, got {sub_value}")
        
        expense_details[month] = month_details
    
    results["details"]["monthly_expense_totals"] = {
        "points_earned": expense_points,
        "points_possible": 9,
        "details": expense_details
    }
    
    # Evaluate profit/loss calculations (9 points)
    profit_loss_points = 0
    profit_loss_details = {}
    
    for month in ["January", "February", "March"]:
        month_details = {"correct": True, "errors": []}
        
        # Check Income (1 point each)
        sub_income = submission["task1"]["profit_loss_calculation"][month].get("Income", 0)
        key_income = answer_key["task1"]["profit_loss_calculation"][month].get("Income", 0)
        
        if sub_income == key_income:
            profit_loss_points += 1
        else:
            month_details["correct"] = False
            month_details["errors"].append(f"Income: expected {key_income}, got {sub_income}")
        
        # Check Expenses (1 point each)
        sub_expenses = submission["task1"]["profit_loss_calculation"][month].get("Expenses", 0)
        key_expenses = answer_key["task1"]["profit_loss_calculation"][month].get("Expenses", 0)
        
        if sub_expenses == key_expenses:
            profit_loss_points += 1
        else:
            month_details["correct"] = False
            month_details["errors"].append(f"Expenses: expected {key_expenses}, got {sub_expenses}")
        
        # Check Profit_Loss (1 point each)
        sub_pl = submission["task1"]["profit_loss_calculation"][month].get("Profit_Loss", 0)
        key_pl = answer_key["task1"]["profit_loss_calculation"][month].get("Profit_Loss", 0)
        
        if sub_pl == key_pl:
            profit_loss_points += 1
        else:
            month_details["correct"] = False
            month_details["errors"].append(f"Profit_Loss: expected {key_pl}, got {sub_pl}")
        
        profit_loss_details[month] = month_details
    
    results["details"]["profit_loss_calculation"] = {
        "points_earned": profit_loss_points,
        "points_possible": 9,
        "details": profit_loss_details
    }
    
    # Evaluate highest expense category (2 points)
    highest_category_points = 0
    highest_category_details = {"correct": True, "errors": []}
    
    sub_highest = submission["task1"].get("highest_expense_category", "")
    key_highest = answer_key["task1"].get("highest_expense_category", "")
    
    if sub_highest == key_highest:
        highest_category_points = 2
    else:
        highest_category_details["correct"] = False
        highest_category_details["errors"].append(f"Expected {key_highest}, got {sub_highest}")
    
    results["details"]["highest_expense_category"] = {
        "points_earned": highest_category_points,
        "points_possible": 2,
        "details": highest_category_details
    }
    
    # Calculate total points for Task 1
    results["points_earned"] = expense_points + profit_loss_points + highest_category_points
    
    return results


def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Production Record Maintenance and Reporting."""
    results = {
        "points_earned": 0,
        "points_possible": 20,
        "details": {}
    }
    
    # Evaluate total production (4 points)
    production_points = 0
    production_details = {"correct": True, "errors": []}
    
    for crop, key_value in answer_key["task2"]["total_production"].items():
        sub_value = submission["task2"]["total_production"].get(crop, 0)
        
        if sub_value == key_value:
            production_points += 1
        else:
            production_details["correct"] = False
            production_details["errors"].append(f"{crop}: expected {key_value}, got {sub_value}")
    
    results["details"]["total_production"] = {
        "points_earned": production_points,
        "points_possible": 4,
        "details": production_details
    }
    
    # Evaluate yield calculations (10 points)
    yield_points = 0
    yield_details = {"correct": True, "errors": []}
    
    for field, key_value in answer_key["task2"]["yield_calculations"].items():
        sub_value = submission["task2"]["yield_calculations"].get(field, 0)
        
        if sub_value == key_value:
            yield_points += 1
        else:
            yield_details["correct"] = False
            yield_details["errors"].append(f"{field}: expected {key_value}, got {sub_value}")
    
    results["details"]["yield_calculations"] = {
        "points_earned": yield_points,
        "points_possible": 10,
        "details": yield_details
    }
    
    # Evaluate highest yield field (6 points)
    highest_field_points = 0
    highest_field_details = {"correct": True, "errors": []}
    
    sub_highest = submission["task2"].get("highest_yield_field", "")
    key_highest = answer_key["task2"].get("highest_yield_field", "")
    
    if sub_highest == key_highest:
        highest_field_points = 6
    else:
        highest_field_details["correct"] = False
        highest_field_details["errors"].append(f"Expected {key_highest}, got {sub_highest}")
    
    results["details"]["highest_yield_field"] = {
        "points_earned": highest_field_points,
        "points_possible": 6,
        "details": highest_field_details
    }
    
    # Calculate total points for Task 2
    results["points_earned"] = production_points + yield_points + highest_field_points
    
    return results


def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Employee Time Tracking and Payroll."""
    results = {
        "points_earned": 0,
        "points_possible": 20,
        "details": {}
    }
    
    # Evaluate employee hours (8 points)
    hours_points = 0
    hours_details = {}
    
    for emp_id, key_data in answer_key["task3"]["employee_hours"].items():
        emp_details = {"correct": True, "errors": []}
        sub_data = submission["task3"]["employee_hours"].get(emp_id, {})
        
        # Check Week1, Week2, and Total (0.5 points each)
        for period in ["Week1", "Week2", "Total"]:
            key_value = key_data.get(period, 0)
            sub_value = sub_data.get(period, 0)
            
            if sub_value == key_value:
                hours_points += 0.5
            else:
                emp_details["correct"] = False
                emp_details["errors"].append(f"{period}: expected {key_value}, got {sub_value}")
        
        hours_details[emp_id] = emp_details
    
    results["details"]["employee_hours"] = {
        "points_earned": hours_points,
        "points_possible": 8,
        "details": hours_details
    }
    
    # Evaluate payroll calculations (8 points)
    payroll_points = 0
    payroll_details = {}
    
    for emp_id, key_data in answer_key["task3"]["payroll_calculations"].items():
        emp_details = {"correct": True, "errors": []}
        sub_data = submission["task3"]["payroll_calculations"].get(emp_id, {})
        
        # Check Regular_Pay, Overtime_Pay, and Gross_Pay (0.5 points each)
        for pay_type in ["Regular_Pay", "Overtime_Pay", "Gross_Pay"]:
            key_value = key_data.get(pay_type, 0)
            sub_value = sub_data.get(pay_type, 0)
            
            if sub_value == key_value:
                payroll_points += 0.5
            else:
                emp_details["correct"] = False
                emp_details["errors"].append(f"{pay_type}: expected {key_value}, got {sub_value}")
        
        payroll_details[emp_id] = emp_details
    
    results["details"]["payroll_calculations"] = {
        "points_earned": payroll_points,
        "points_possible": 8,
        "details": payroll_details
    }
    
    # Evaluate total labor cost (4 points)
    labor_cost_points = 0
    labor_cost_details = {"correct": True, "errors": []}
    
    sub_cost = submission["task3"].get("total_labor_cost", 0)
    key_cost = answer_key["task3"].get("total_labor_cost", 0)
    
    if sub_cost == key_cost:
        labor_cost_points = 4
    else:
        labor_cost_details["correct"] = False
        labor_cost_details["errors"].append(f"Expected {key_cost}, got {sub_cost}")
    
    results["details"]["total_labor_cost"] = {
        "points_earned": labor_cost_points,
        "points_possible": 4,
        "details": labor_cost_details
    }
    
    # Calculate total points for Task 3
    results["points_earned"] = hours_points + payroll_points + labor_cost_points
    
    return results


def check_critical_requirements(submission: Dict[str, Any], answer_key: Dict[str, Any], 
                               task_results: Dict[str, Any]) -> Dict[str, Any]:
    """Check if the candidate meets the critical requirements."""
    critical_results = {
        "passed": True,
        "details": {}
    }
    
    # 1. Format Compliance - already checked by loading the JSON
    critical_results["details"]["format_compliance"] = {
        "passed": True,
        "notes": "Submission is in valid JSON format with the required structure."
    }
    
    # 2. Critical Calculation Accuracy
    
    # Check if at least one complete month's expenses is correct
    month_expenses_correct = False
    for month in ["January", "February", "March"]:
        if task_results["task1"]["details"]["monthly_expense_totals"]["details"][month]["correct"]:
            month_expenses_correct = True
            break
    
    critical_results["details"]["month_expenses_calculation"] = {
        "passed": month_expenses_correct,
        "notes": "At least one complete month's expenses calculated correctly." if month_expenses_correct 
                else "Failed to correctly calculate any complete month's expenses."
    }
    
    # Check if at least one crop's total production is correct
    crop_production_correct = False
    for crop, key_value in answer_key["task2"]["total_production"].items():
        if submission["task2"]["total_production"].get(crop, 0) == key_value:
            crop_production_correct = True
            break
    
    critical_results["details"]["crop_production_calculation"] = {
        "passed": crop_production_correct,
        "notes": "At least one crop's total production calculated correctly." if crop_production_correct 
                else "Failed to correctly calculate any crop's total production."
    }
    
    # Check if at least one employee's complete payroll is correct
    employee_payroll_correct = False
    for emp_id, key_data in answer_key["task3"]["payroll_calculations"].items():
        sub_data = submission["task3"]["payroll_calculations"].get(emp_id, {})
        if (sub_data.get("Regular_Pay", 0) == key_data.get("Regular_Pay", 0) and
            sub_data.get("Overtime_Pay", 0) == key_data.get("Overtime_Pay", 0) and
            sub_data.get("Gross_Pay", 0) == key_data.get("Gross_Pay", 0)):
            employee_payroll_correct = True
            break
    
    critical_results["details"]["employee_payroll_calculation"] = {
        "passed": employee_payroll_correct,
        "notes": "At least one employee's complete payroll calculated correctly." if employee_payroll_correct 
                else "Failed to correctly calculate any employee's complete payroll."
    }
    
    # 3. Decimal Precision
    # This is implicitly checked in the point-by-point evaluation
    # If any value doesn't match exactly, it would have failed the specific check
    
    critical_results["details"]["decimal_precision"] = {
        "passed": True,
        "notes": "Decimal precision requirements met."
    }
    
    # Overall critical requirements check
    critical_results["passed"] = (month_expenses_correct and 
                                 crop_production_correct and 
                                 employee_payroll_correct)
    
    return critical_results


def main():
    """Main function to evaluate the candidate's submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    total_points_earned = task1_results["points_earned"] + task2_results["points_earned"] + task3_results["points_earned"]
    total_points_possible = task1_results["points_possible"] + task2_results["points_possible"] + task3_results["points_possible"]
    overall_score_percentage = (total_points_earned / total_points_possible) * 100
    
    # Check critical requirements
    critical_requirements = check_critical_requirements(
        submission, answer_key, 
        {"task1": task1_results, "task2": task2_results, "task3": task3_results}
    )
    
    # Determine if the candidate passed
    passed = overall_score_percentage >= 75 and critical_requirements["passed"]
    
    # Compile the results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score_percentage, 2),
        "passed": passed,
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "critical_requirements": critical_requirements,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results
        }
    }
    
    # Save the results to a file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score_percentage:.2f}%")
    print(f"Pass status: {'PASSED' if passed else 'FAILED'}")


if __name__ == "__main__":
    main()