#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, List, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_budget_analysis(submission: Dict, answer_key: Dict, client: str) -> Tuple[float, Dict]:
    """Evaluate the budget analysis section for a client."""
    score = 0
    details = {}
    
    # Check income/expense calculations (5 points)
    income_diff = abs(submission[client]["monthly_budget"]["total_income"] - 
                     answer_key[client]["monthly_budget"]["total_income"])
    income_score = 5 if income_diff <= 0.01 else max(0, 5 - (income_diff / 100) * 5)
    
    expense_diff = abs(submission[client]["monthly_budget"]["total_expenses"] - 
                      answer_key[client]["monthly_budget"]["total_expenses"])
    expense_score = 5 if expense_diff <= 50 else max(0, 5 - (expense_diff / 200) * 5)
    
    calc_score = min(5, income_score + expense_score / 2)
    score += calc_score
    details["income_expense_calculations"] = {
        "score": calc_score,
        "max_score": 5,
        "notes": f"Income diff: ${income_diff:.2f}, Expense diff: ${expense_diff:.2f}"
    }
    
    # Check expense reductions (5 points)
    # This is more subjective, but we can check if discretionary income is reasonable
    discretionary_diff = abs(submission[client]["monthly_budget"]["discretionary_income"] - 
                           answer_key[client]["monthly_budget"]["discretionary_income"])
    reduction_score = 5 if discretionary_diff <= 100 else max(0, 5 - (discretionary_diff / 200) * 5)
    score += reduction_score
    details["expense_reductions"] = {
        "score": reduction_score,
        "max_score": 5,
        "notes": f"Discretionary income difference: ${discretionary_diff:.2f}"
    }
    
    # Check category allocations (5 points)
    category_score = 5
    category_notes = []
    
    for category in answer_key[client]["monthly_budget"]["expense_categories"]:
        key_value = answer_key[client]["monthly_budget"]["expense_categories"][category]
        sub_value = submission[client]["monthly_budget"]["expense_categories"][category]
        diff = abs(sub_value - key_value)
        
        # If difference is more than 20% of the answer key value, deduct points
        if key_value > 0 and diff / key_value > 0.2:
            category_score -= 0.5
            category_notes.append(f"{category}: ${sub_value:.2f} vs expected ~${key_value:.2f}")
    
    category_score = max(0, category_score)
    score += category_score
    details["category_allocations"] = {
        "score": category_score,
        "max_score": 5,
        "notes": ", ".join(category_notes) if category_notes else "Appropriate allocations"
    }
    
    # Check balanced budget (5 points)
    income = submission[client]["monthly_budget"]["total_income"]
    expenses = submission[client]["monthly_budget"]["total_expenses"]
    discretionary = submission[client]["monthly_budget"]["discretionary_income"]
    
    # Check if discretionary income calculation is correct
    calc_discretionary = income - expenses
    discretionary_calc_diff = abs(calc_discretionary - discretionary)
    
    # Check if budget is balanced (income >= expenses)
    is_balanced = income >= expenses
    
    balance_score = 5 if is_balanced and discretionary_calc_diff <= 0.01 else 0
    score += balance_score
    details["balanced_budget"] = {
        "score": balance_score,
        "max_score": 5,
        "notes": "Budget is balanced" if is_balanced else "Budget is not balanced"
    }
    
    return score, details

def evaluate_debt_management(submission: Dict, answer_key: Dict, client: str) -> Tuple[float, Dict]:
    """Evaluate the debt management section for a client."""
    score = 0
    details = {}
    
    # Check debt prioritization (5 points)
    prioritization_score = 5
    prioritization_notes = []
    
    # Create dictionaries mapping account names to priorities
    key_priorities = {debt["account_name"]: debt["priority"] 
                     for debt in answer_key[client]["debt_management"]["prioritized_debts"]}
    sub_priorities = {debt["account_name"]: debt["priority"] 
                     for debt in submission[client]["debt_management"]["prioritized_debts"]}
    
    # Check if all debts are included
    if set(key_priorities.keys()) != set(sub_priorities.keys()):
        missing = set(key_priorities.keys()) - set(sub_priorities.keys())
        extra = set(sub_priorities.keys()) - set(key_priorities.keys())
        prioritization_score -= 2
        if missing:
            prioritization_notes.append(f"Missing debts: {missing}")
        if extra:
            prioritization_notes.append(f"Extra debts: {extra}")
    
    # Check if priorities are correct
    for account, key_priority in key_priorities.items():
        if account in sub_priorities:
            if sub_priorities[account] != key_priority:
                prioritization_score -= 1
                prioritization_notes.append(f"{account}: priority {sub_priorities[account]} vs expected {key_priority}")
    
    prioritization_score = max(0, prioritization_score)
    score += prioritization_score
    details["debt_prioritization"] = {
        "score": prioritization_score,
        "max_score": 5,
        "notes": ", ".join(prioritization_notes) if prioritization_notes else "Correct prioritization"
    }
    
    # Check appropriate monthly payment (5 points)
    key_payment = answer_key[client]["debt_management"]["monthly_debt_payment"]
    sub_payment = submission[client]["debt_management"]["monthly_debt_payment"]
    
    # Define acceptable ranges based on client
    if client == "client1":
        payment_min, payment_max = 600, 750
    else:  # client2
        payment_min, payment_max = 1300, 1700
    
    payment_score = 5 if payment_min <= sub_payment <= payment_max else 0
    score += payment_score
    details["monthly_payment"] = {
        "score": payment_score,
        "max_score": 5,
        "notes": f"Payment ${sub_payment:.2f} is {'within' if payment_score > 0 else 'outside'} acceptable range (${payment_min:.2f}-${payment_max:.2f})"
    }
    
    # Check realistic payoff timeline (5 points)
    key_timeline = answer_key[client]["debt_management"]["debt_payoff_timeline_months"]
    sub_timeline = submission[client]["debt_management"]["debt_payoff_timeline_months"]
    
    # Define acceptable ranges based on client
    if client == "client1":
        timeline_min, timeline_max = 12, 18
    else:  # client2
        timeline_min, timeline_max = 30, 42
    
    timeline_score = 5 if timeline_min <= sub_timeline <= timeline_max else 0
    score += timeline_score
    details["payoff_timeline"] = {
        "score": timeline_score,
        "max_score": 5,
        "notes": f"Timeline {sub_timeline} months is {'within' if timeline_score > 0 else 'outside'} acceptable range ({timeline_min}-{timeline_max} months)"
    }
    
    # Check mathematical accuracy (5 points)
    # This is a simplified check - in reality would need more complex validation
    total_debt_diff = abs(submission[client]["debt_management"]["total_debt"] - 
                         answer_key[client]["debt_management"]["total_debt"])
    
    math_score = 5 if total_debt_diff <= 0.01 else 0
    score += math_score
    details["mathematical_accuracy"] = {
        "score": math_score,
        "max_score": 5,
        "notes": f"Total debt calculation {'accurate' if math_score > 0 else 'inaccurate'}"
    }
    
    return score, details

def evaluate_savings_plan(submission: Dict, answer_key: Dict, client: str) -> Tuple[float, Dict]:
    """Evaluate the savings plan section for a client."""
    score = 0
    details = {}
    
    # Check appropriate emergency fund target (3 points)
    key_target = answer_key[client]["savings_goal"]["emergency_fund_target"]
    sub_target = submission[client]["savings_goal"]["emergency_fund_target"]
    
    # Define acceptable ranges based on client
    if client == "client1":
        target_min, target_max = 6000, 7000
    else:  # client2
        target_min, target_max = 7000, 8500
    
    target_score = 3 if target_min <= sub_target <= target_max else 0
    score += target_score
    details["emergency_fund_target"] = {
        "score": target_score,
        "max_score": 3,
        "notes": f"Target ${sub_target:.2f} is {'within' if target_score > 0 else 'outside'} acceptable range (${target_min:.2f}-${target_max:.2f})"
    }
    
    # Check realistic monthly contribution (3 points)
    key_contribution = answer_key[client]["savings_goal"]["monthly_contribution"]
    sub_contribution = submission[client]["savings_goal"]["monthly_contribution"]
    
    # Define acceptable ranges based on client
    if client == "client1":
        contribution_min, contribution_max = 75, 150
    else:  # client2
        contribution_min, contribution_max = 300, 500
    
    contribution_score = 3 if contribution_min <= sub_contribution <= contribution_max else 0
    score += contribution_score
    details["monthly_contribution"] = {
        "score": contribution_score,
        "max_score": 3,
        "notes": f"Contribution ${sub_contribution:.2f} is {'within' if contribution_score > 0 else 'outside'} acceptable range (${contribution_min:.2f}-${contribution_max:.2f})"
    }
    
    # Check accurate timeline calculation (4 points)
    # This is a simplified check - in reality would need to verify the calculation
    key_months = answer_key[client]["savings_goal"]["months_to_complete"]
    sub_months = submission[client]["savings_goal"]["months_to_complete"]
    
    # Allow for some variation in the timeline calculation
    months_diff = abs(sub_months - key_months)
    months_score = 4 if months_diff <= 6 else max(0, 4 - (months_diff / 12) * 4)
    
    score += months_score
    details["timeline_calculation"] = {
        "score": months_score,
        "max_score": 4,
        "notes": f"Timeline calculation difference: {months_diff} months"
    }
    
    return score, details

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "client1": {
            "budget_analysis": {},
            "debt_management": {},
            "savings_plan": {},
            "total_score": 0
        },
        "client2": {
            "budget_analysis": {},
            "debt_management": {},
            "savings_plan": {},
            "total_score": 0
        }
    }
    
    # Evaluate Client 1
    budget_score, budget_details = evaluate_budget_analysis(submission, answer_key, "client1")
    debt_score, debt_details = evaluate_debt_management(submission, answer_key, "client1")
    savings_score, savings_details = evaluate_savings_plan(submission, answer_key, "client1")
    
    results["client1"]["budget_analysis"] = budget_details
    results["client1"]["debt_management"] = debt_details
    results["client1"]["savings_plan"] = savings_details
    results["client1"]["total_score"] = budget_score + debt_score + savings_score
    
    # Evaluate Client 2
    budget_score, budget_details = evaluate_budget_analysis(submission, answer_key, "client2")
    debt_score, debt_details = evaluate_debt_management(submission, answer_key, "client2")
    savings_score, savings_details = evaluate_savings_plan(submission, answer_key, "client2")
    
    results["client2"]["budget_analysis"] = budget_details
    results["client2"]["debt_management"] = debt_details
    results["client2"]["savings_plan"] = savings_details
    results["client2"]["total_score"] = budget_score + debt_score + savings_score
    
    # Calculate overall score
    results["total_points"] = results["client1"]["total_score"] + results["client2"]["total_score"]
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Add performance rating
    if results["overall_score"] >= 90:
        results["rating"] = "Pass with Distinction"
    elif results["overall_score"] >= 75:
        results["rating"] = "Pass"
    elif results["overall_score"] >= 65:
        results["rating"] = "Conditional Pass"
    else:
        results["rating"] = "Fail"
    
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
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
    print(f"Rating: {results['rating']}")
    print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()