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

def evaluate_scenario_1(submission, answer_key):
    """Evaluate Scenario 1 answers."""
    results = {
        "highest_risk_debt_id": {
            "candidate_answer": submission.get("highest_risk_debt_id", ""),
            "correct_answer": answer_key.get("highest_risk_debt_id", ""),
            "score": 0,
            "is_critical": True
        },
        "minimum_payment_to_prevent_foreclosure": {
            "candidate_answer": submission.get("minimum_payment_to_prevent_foreclosure", 0),
            "correct_answer": answer_key.get("minimum_payment_to_prevent_foreclosure", 0),
            "score": 0,
            "is_critical": False
        },
        "expense_category_to_reduce": {
            "candidate_answer": submission.get("expense_category_to_reduce", ""),
            "correct_answer": answer_key.get("expense_category_to_reduce", ""),
            "score": 0,
            "is_critical": False
        },
        "interest_savings_highest_interest_first": {
            "candidate_answer": submission.get("interest_savings_highest_interest_first", 0),
            "correct_answer": answer_key.get("interest_savings_highest_interest_first", 0),
            "score": 0,
            "is_critical": False
        }
    }
    
    # Evaluate highest_risk_debt_id (critical question)
    if results["highest_risk_debt_id"]["candidate_answer"] == results["highest_risk_debt_id"]["correct_answer"]:
        results["highest_risk_debt_id"]["score"] = 1
    
    # Evaluate minimum_payment_to_prevent_foreclosure with 5% tolerance
    candidate_payment = results["minimum_payment_to_prevent_foreclosure"]["candidate_answer"]
    correct_payment = results["minimum_payment_to_prevent_foreclosure"]["correct_answer"]
    if correct_payment > 0:
        if abs(candidate_payment - correct_payment) / correct_payment <= 0.05:
            results["minimum_payment_to_prevent_foreclosure"]["score"] = 1
    
    # Evaluate expense_category_to_reduce
    if results["expense_category_to_reduce"]["candidate_answer"] == results["expense_category_to_reduce"]["correct_answer"]:
        results["expense_category_to_reduce"]["score"] = 1
    
    # Evaluate interest_savings_highest_interest_first with 5% tolerance
    candidate_savings = results["interest_savings_highest_interest_first"]["candidate_answer"]
    correct_savings = results["interest_savings_highest_interest_first"]["correct_answer"]
    if correct_savings > 0:
        if abs(candidate_savings - correct_savings) / correct_savings <= 0.05:
            results["interest_savings_highest_interest_first"]["score"] = 1
    
    return results

def evaluate_scenario_2(submission, answer_key):
    """Evaluate Scenario 2 answers."""
    results = {
        "debt_priority_ranking": {
            "candidate_answer": submission.get("debt_priority_ranking", []),
            "correct_answer": answer_key.get("debt_priority_ranking", []),
            "score": 0,
            "is_critical": False
        },
        "total_interest_avalanche_method_24_months": {
            "candidate_answer": submission.get("total_interest_avalanche_method_24_months", 0),
            "correct_answer": answer_key.get("total_interest_avalanche_method_24_months", 0),
            "score": 0,
            "is_critical": False
        },
        "total_interest_snowball_method_24_months": {
            "candidate_answer": submission.get("total_interest_snowball_method_24_months", 0),
            "correct_answer": answer_key.get("total_interest_snowball_method_24_months", 0),
            "score": 0,
            "is_critical": False
        },
        "monthly_payment_for_36_month_payoff": {
            "candidate_answer": submission.get("monthly_payment_for_36_month_payoff", 0),
            "correct_answer": answer_key.get("monthly_payment_for_36_month_payoff", 0),
            "score": 0,
            "is_critical": False
        }
    }
    
    # Evaluate debt_priority_ranking (first three must be correct)
    candidate_ranking = results["debt_priority_ranking"]["candidate_answer"]
    correct_ranking = results["debt_priority_ranking"]["correct_answer"]
    
    if len(candidate_ranking) >= 3 and len(correct_ranking) >= 3:
        if candidate_ranking[:3] == correct_ranking[:3]:
            results["debt_priority_ranking"]["score"] = 1
    
    # Evaluate total_interest_avalanche_method_24_months with 5% tolerance
    candidate_avalanche = results["total_interest_avalanche_method_24_months"]["candidate_answer"]
    correct_avalanche = results["total_interest_avalanche_method_24_months"]["correct_answer"]
    if correct_avalanche > 0:
        if abs(candidate_avalanche - correct_avalanche) / correct_avalanche <= 0.05:
            results["total_interest_avalanche_method_24_months"]["score"] = 1
    
    # Evaluate total_interest_snowball_method_24_months with 5% tolerance
    candidate_snowball = results["total_interest_snowball_method_24_months"]["candidate_answer"]
    correct_snowball = results["total_interest_snowball_method_24_months"]["correct_answer"]
    if correct_snowball > 0:
        if abs(candidate_snowball - correct_snowball) / correct_snowball <= 0.05:
            results["total_interest_snowball_method_24_months"]["score"] = 1
    
    # Evaluate monthly_payment_for_36_month_payoff with 5% tolerance
    candidate_payment = results["monthly_payment_for_36_month_payoff"]["candidate_answer"]
    correct_payment = results["monthly_payment_for_36_month_payoff"]["correct_answer"]
    if correct_payment > 0:
        if abs(candidate_payment - correct_payment) / correct_payment <= 0.05:
            results["monthly_payment_for_36_month_payoff"]["score"] = 1
    
    return results

def evaluate_scenario_3(submission, answer_key):
    """Evaluate Scenario 3 answers."""
    results = {
        "debts_with_legal_consequences": {
            "candidate_answer": submission.get("debts_with_legal_consequences", []),
            "correct_answer": answer_key.get("debts_with_legal_consequences", []),
            "score": 0,
            "is_critical": True
        },
        "debt_to_income_ratio": {
            "candidate_answer": submission.get("debt_to_income_ratio", 0),
            "correct_answer": answer_key.get("debt_to_income_ratio", 0),
            "score": 0,
            "is_critical": False
        },
        "monthly_increase_needed_for_5year_payoff": {
            "candidate_answer": submission.get("monthly_increase_needed_for_5year_payoff", 0),
            "correct_answer": answer_key.get("monthly_increase_needed_for_5year_payoff", 0),
            "score": 0,
            "is_critical": False
        },
        "monthly_savings_with_consolidation": {
            "candidate_answer": submission.get("monthly_savings_with_consolidation", 0),
            "correct_answer": answer_key.get("monthly_savings_with_consolidation", 0),
            "score": 0,
            "is_critical": False
        }
    }
    
    # Evaluate debts_with_legal_consequences (at least 2 of 3 must be correct)
    candidate_debts = set(results["debts_with_legal_consequences"]["candidate_answer"])
    correct_debts = set(results["debts_with_legal_consequences"]["correct_answer"])
    
    # Check if at least 2 correct debts are identified and C3 (tax debt) is included
    if len(candidate_debts.intersection(correct_debts)) >= 2 and "C3" in candidate_debts:
        results["debts_with_legal_consequences"]["score"] = 1
    
    # Evaluate debt_to_income_ratio with 5% tolerance
    candidate_ratio = results["debt_to_income_ratio"]["candidate_answer"]
    correct_ratio = results["debt_to_income_ratio"]["correct_answer"]
    if correct_ratio > 0:
        if abs(candidate_ratio - correct_ratio) / correct_ratio <= 0.05:
            results["debt_to_income_ratio"]["score"] = 1
    
    # Evaluate monthly_increase_needed_for_5year_payoff with 5% tolerance
    candidate_increase = results["monthly_increase_needed_for_5year_payoff"]["candidate_answer"]
    correct_increase = results["monthly_increase_needed_for_5year_payoff"]["correct_answer"]
    if correct_increase > 0:
        if abs(candidate_increase - correct_increase) / correct_increase <= 0.05:
            results["monthly_increase_needed_for_5year_payoff"]["score"] = 1
    
    # Evaluate monthly_savings_with_consolidation with 5% tolerance
    candidate_savings = results["monthly_savings_with_consolidation"]["candidate_answer"]
    correct_savings = results["monthly_savings_with_consolidation"]["correct_answer"]
    if correct_savings > 0:
        if abs(candidate_savings - correct_savings) / correct_savings <= 0.05:
            results["monthly_savings_with_consolidation"]["score"] = 1
    
    return results

def check_automatic_failure(evaluation_results):
    """Check for automatic failure conditions."""
    # Condition 1: Failing to identify mortgage (A1) as highest risk debt
    if evaluation_results["scenario_1"]["highest_risk_debt_id"]["candidate_answer"] != "A1":
        return True
    
    # Condition 3: Failing to identify tax debt (C3) as having legal consequences
    if "C3" not in evaluation_results["scenario_3"]["debts_with_legal_consequences"]["candidate_answer"]:
        return True
    
    return False

def calculate_overall_score(evaluation_results):
    """Calculate the overall score as a percentage."""
    total_points = 0
    earned_points = 0
    
    # Count points from all scenarios
    for scenario in ["scenario_1", "scenario_2", "scenario_3"]:
        for question in evaluation_results[scenario]:
            total_points += 1
            earned_points += evaluation_results[scenario][question]["score"]
    
    # Calculate percentage
    if total_points > 0:
        return (earned_points / total_points) * 100
    return 0

def evaluate_submission(submission_path, answer_key_path):
    """Evaluate a candidate's submission against the answer key."""
    # Load the submission and answer key
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Extract the scenario data
    submission_s1 = submission.get("scenario_1", {})
    submission_s2 = submission.get("scenario_2", {})
    submission_s3 = submission.get("scenario_3", {})
    
    answer_key_s1 = answer_key.get("scenario_1", {})
    answer_key_s2 = answer_key.get("scenario_2", {})
    answer_key_s3 = answer_key.get("scenario_3", {})
    
    # Evaluate each scenario
    evaluation_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "scenario_1": evaluate_scenario_1(submission_s1, answer_key_s1),
        "scenario_2": evaluate_scenario_2(submission_s2, answer_key_s2),
        "scenario_3": evaluate_scenario_3(submission_s3, answer_key_s3)
    }
    
    # Check for automatic failure conditions
    automatic_failure = check_automatic_failure(evaluation_results)
    
    # Calculate overall score
    overall_score = 0 if automatic_failure else calculate_overall_score(evaluation_results)
    
    # Add overall score to results
    evaluation_results["overall_score"] = overall_score
    evaluation_results["automatic_failure"] = automatic_failure
    
    # Determine if the candidate passed (75% or higher and no automatic failure)
    total_questions = 12
    passing_threshold = 9  # 75% of 12 questions
    
    total_correct = sum(
        evaluation_results[scenario][question]["score"] 
        for scenario in ["scenario_1", "scenario_2", "scenario_3"]
        for question in evaluation_results[scenario]
    )
    
    evaluation_results["passed"] = (
        not automatic_failure and 
        total_correct >= passing_threshold
    )
    
    return evaluation_results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    # Evaluate the submission
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Save the results to test_results.json
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Pass status: {'Passed' if results['passed'] else 'Failed'}")

if __name__ == "__main__":
    main()