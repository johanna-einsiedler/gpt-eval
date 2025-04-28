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

def evaluate_financial_position(submission, answer_key):
    results = {"points": 0, "max_points": 3, "details": {}}
    
    # Net Worth
    net_worth_diff = abs(submission["net_worth"] - answer_key["net_worth"])
    net_worth_percent_diff = net_worth_diff / answer_key["net_worth"]
    results["details"]["net_worth"] = {
        "submission": submission["net_worth"],
        "answer_key": answer_key["net_worth"],
        "correct": net_worth_percent_diff <= 0.05,
        "points": 1 if net_worth_percent_diff <= 0.05 else 0
    }
    results["points"] += results["details"]["net_worth"]["points"]
    
    # Debt-to-Income Ratio
    dti_diff = abs(submission["debt_to_income_ratio"] - answer_key["debt_to_income_ratio"])
    results["details"]["debt_to_income_ratio"] = {
        "submission": submission["debt_to_income_ratio"],
        "answer_key": answer_key["debt_to_income_ratio"],
        "correct": dti_diff <= 0.05 * answer_key["debt_to_income_ratio"],
        "points": 1 if dti_diff <= 0.05 * answer_key["debt_to_income_ratio"] else 0
    }
    results["points"] += results["details"]["debt_to_income_ratio"]["points"]
    
    # Emergency Fund Months
    ef_diff = abs(submission["emergency_fund_months"] - answer_key["emergency_fund_months"])
    results["details"]["emergency_fund_months"] = {
        "submission": submission["emergency_fund_months"],
        "answer_key": answer_key["emergency_fund_months"],
        "correct": ef_diff <= 0.05 * answer_key["emergency_fund_months"],
        "points": 1 if ef_diff <= 0.05 * answer_key["emergency_fund_months"] else 0
    }
    results["points"] += results["details"]["emergency_fund_months"]["points"]
    
    return results

def evaluate_retirement_planning(submission, answer_key):
    results = {"points": 0, "max_points": 2, "details": {}}
    
    # Projected Gap
    gap_diff = abs(submission["projected_gap"] - answer_key["projected_gap"])
    results["details"]["projected_gap"] = {
        "submission": submission["projected_gap"],
        "answer_key": answer_key["projected_gap"],
        "correct": gap_diff <= 50000,  # Critical element with specific tolerance
        "points": 1 if gap_diff <= 50000 else 0
    }
    results["points"] += results["details"]["projected_gap"]["points"]
    
    # Required Monthly Savings
    savings_diff = abs(submission["required_monthly_savings"] - answer_key["required_monthly_savings"])
    savings_percent_diff = savings_diff / answer_key["required_monthly_savings"]
    results["details"]["required_monthly_savings"] = {
        "submission": submission["required_monthly_savings"],
        "answer_key": answer_key["required_monthly_savings"],
        "correct": savings_percent_diff <= 0.05,
        "points": 1 if savings_percent_diff <= 0.05 else 0
    }
    results["points"] += results["details"]["required_monthly_savings"]["points"]
    
    return results

def evaluate_goal_prioritization(submission, answer_key):
    results = {"points": 0, "max_points": 7, "details": {}}
    
    # Ranked Goals (4 points)
    correct_goals = 0
    for i, (sub_goal, key_goal) in enumerate(zip(submission["ranked_goals"], answer_key["ranked_goals"])):
        if sub_goal == key_goal:
            correct_goals += 1
    
    # Check for automatic failure condition
    top_priority_is_home_renovation = submission["ranked_goals"][0] == "Goal_C"
    
    results["details"]["ranked_goals"] = {
        "submission": submission["ranked_goals"],
        "answer_key": answer_key["ranked_goals"],
        "correct_count": correct_goals,
        "automatic_failure": top_priority_is_home_renovation,
        "points": correct_goals
    }
    results["points"] += correct_goals
    
    # Top Priority Strategies (3 points)
    correct_strategies = 0
    for strategy in submission["top_priority_strategies"]:
        if strategy in answer_key["top_priority_strategies"]:
            correct_strategies += 1
    
    results["details"]["top_priority_strategies"] = {
        "submission": submission["top_priority_strategies"],
        "answer_key": answer_key["top_priority_strategies"],
        "correct_count": correct_strategies,
        "critical_element_satisfied": correct_strategies >= 2,  # Critical element
        "points": correct_strategies
    }
    results["points"] += correct_strategies
    
    return results

def evaluate_investment_assessment(submission, answer_key):
    results = {"points": 0, "max_points": 5, "details": {}}
    
    # Current Allocation (3 points)
    allocation_points = 0
    allocation_details = {}
    
    for asset_class in ["stocks", "bonds", "cash", "other"]:
        sub_value = submission["current_allocation"][asset_class]
        key_value = answer_key["current_allocation"][asset_class]
        diff = abs(sub_value - key_value)
        is_correct = diff <= 0.02  # 2% tolerance
        
        allocation_details[asset_class] = {
            "submission": sub_value,
            "answer_key": key_value,
            "correct": is_correct
        }
        
        if is_correct:
            allocation_points += 0.75  # 0.75 points per correct asset class (3 points total)
    
    allocation_points = min(3, allocation_points)  # Cap at 3 points
    
    results["details"]["current_allocation"] = {
        "asset_classes": allocation_details,
        "points": allocation_points
    }
    results["points"] += allocation_points
    
    # Aligned with Risk Profile (1 point)
    results["details"]["aligned_with_risk_profile"] = {
        "submission": submission["aligned_with_risk_profile"],
        "answer_key": answer_key["aligned_with_risk_profile"],
        "correct": submission["aligned_with_risk_profile"] == answer_key["aligned_with_risk_profile"],
        "critical_element_satisfied": submission["aligned_with_risk_profile"] == answer_key["aligned_with_risk_profile"],  # Critical element
        "points": 1 if submission["aligned_with_risk_profile"] == answer_key["aligned_with_risk_profile"] else 0
    }
    results["points"] += results["details"]["aligned_with_risk_profile"]["points"]
    
    # Average Expense Ratio (1 point)
    expense_diff = abs(submission["average_expense_ratio"] - answer_key["average_expense_ratio"])
    results["details"]["average_expense_ratio"] = {
        "submission": submission["average_expense_ratio"],
        "answer_key": answer_key["average_expense_ratio"],
        "correct": expense_diff <= 0.0002,  # Specific tolerance
        "points": 1 if expense_diff <= 0.0002 else 0
    }
    results["points"] += results["details"]["average_expense_ratio"]["points"]
    
    return results

def evaluate_recommendations(submission, answer_key):
    results = {"points": 0, "max_points": 3, "details": {}}
    
    # Emergency Fund
    results["details"]["emergency_fund"] = {
        "submission": submission["emergency_fund"],
        "answer_key": answer_key["emergency_fund"],
        "correct": submission["emergency_fund"] == answer_key["emergency_fund"],
        "points": 1 if submission["emergency_fund"] == answer_key["emergency_fund"] else 0
    }
    results["points"] += results["details"]["emergency_fund"]["points"]
    
    # Debt Management
    results["details"]["debt_management"] = {
        "submission": submission["debt_management"],
        "answer_key": answer_key["debt_management"],
        "correct": submission["debt_management"] == answer_key["debt_management"],
        "points": 1 if submission["debt_management"] == answer_key["debt_management"] else 0
    }
    results["points"] += results["details"]["debt_management"]["points"]
    
    # Investment Allocation
    invest_option_1_selected = submission["investment_allocation"] == "Invest_Option_1"
    
    results["details"]["investment_allocation"] = {
        "submission": submission["investment_allocation"],
        "answer_key": answer_key["investment_allocation"],
        "correct": submission["investment_allocation"] == answer_key["investment_allocation"],
        "automatic_failure": invest_option_1_selected,  # Automatic failure condition
        "points": 1 if submission["investment_allocation"] == answer_key["investment_allocation"] else 0
    }
    results["points"] += results["details"]["investment_allocation"]["points"]
    
    return results

def check_automatic_failure_conditions(evaluation_results, submission):
    # Check for automatic failure conditions
    failure_conditions = []
    
    # 1. Prioritizing home renovation (Goal_C) as the top priority
    if evaluation_results["goal_prioritization"]["details"]["ranked_goals"]["automatic_failure"]:
        failure_conditions.append("Prioritized home renovation (Goal_C) as the top priority")
    
    # 2. Recommending no change to the investment allocation (Invest_Option_1)
    if evaluation_results["recommendations"]["details"]["investment_allocation"]["automatic_failure"]:
        failure_conditions.append("Recommended no change to investment allocation (Invest_Option_1)")
    
    # 3. Calculating a debt-to-income ratio below 0.25 or above 0.40
    dti_ratio = submission["financial_position"]["debt_to_income_ratio"]
    if dti_ratio < 0.25 or dti_ratio > 0.40:
        failure_conditions.append(f"Calculated debt-to-income ratio ({dti_ratio}) is outside acceptable range (0.25-0.40)")
    
    return failure_conditions

def check_critical_elements(evaluation_results):
    critical_elements_satisfied = []
    critical_elements_failed = []
    
    # 1. The retirement savings gap (within ±$50,000)
    if evaluation_results["retirement_planning"]["details"]["projected_gap"]["correct"]:
        critical_elements_satisfied.append("Correctly identified retirement savings gap")
    else:
        critical_elements_failed.append("Failed to correctly identify retirement savings gap")
    
    # 2. That the current investment allocation does not align with risk profile
    if evaluation_results["investment_assessment"]["details"]["aligned_with_risk_profile"]["critical_element_satisfied"]:
        critical_elements_satisfied.append("Correctly identified investment allocation alignment with risk profile")
    else:
        critical_elements_failed.append("Failed to correctly identify investment allocation alignment with risk profile")
    
    # 3. At least 2 of the 3 recommended strategies for the top priority goal
    if evaluation_results["goal_prioritization"]["details"]["top_priority_strategies"]["critical_element_satisfied"]:
        critical_elements_satisfied.append("Correctly identified at least 2 of 3 recommended strategies for top priority goal")
    else:
        critical_elements_failed.append("Failed to correctly identify at least 2 of 3 recommended strategies for top priority goal")
    
    return {
        "satisfied": critical_elements_satisfied,
        "failed": critical_elements_failed,
        "all_satisfied": len(critical_elements_failed) == 0
    }

def evaluate_submission(submission, answer_key):
    # Evaluate each section
    evaluation = {
        "financial_position": evaluate_financial_position(
            submission["financial_position"], 
            answer_key["financial_position"]
        ),
        "retirement_planning": evaluate_retirement_planning(
            submission["retirement_planning"], 
            answer_key["retirement_planning"]
        ),
        "goal_prioritization": evaluate_goal_prioritization(
            submission["goal_prioritization"], 
            answer_key["goal_prioritization"]
        ),
        "investment_assessment": evaluate_investment_assessment(
            submission["investment_assessment"], 
            answer_key["investment_assessment"]
        ),
        "recommendations": evaluate_recommendations(
            submission["recommendations"], 
            answer_key["recommendations"]
        )
    }
    
    # Calculate total points
    total_points = sum(section["points"] for section in evaluation.values())
    max_points = sum(section["max_points"] for section in evaluation.values())
    
    # Check for automatic failure conditions
    failure_conditions = check_automatic_failure_conditions(evaluation, submission)
    
    # Check critical elements
    critical_elements = check_critical_elements(evaluation)
    
    # Calculate overall score as a percentage
    overall_score = (total_points / max_points) * 100
    
    # Determine if the candidate passed
    passed = (overall_score >= 75) and (not failure_conditions) and critical_elements["all_satisfied"]
    
    return {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "section_results": evaluation,
        "total_points": total_points,
        "max_points": max_points,
        "overall_score": overall_score,
        "automatic_failure_conditions": failure_conditions,
        "critical_elements": critical_elements,
        "passed": passed
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()