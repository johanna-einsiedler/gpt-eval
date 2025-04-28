#!/usr/bin/env python3
"""
Debt Liquidation Planning Exam Evaluator

This script evaluates a candidate's debt liquidation plan submission against an answer key.
It scores the submission based on specified criteria and generates a detailed results file.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import os
from typing import Dict, List, Any, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_debt_prioritization(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the debt prioritization component."""
    max_points = 25
    points = 0
    comments = []
    
    # Check if debt payoff order exists and is complete
    if "debt_payoff_order" not in submission or len(submission["debt_payoff_order"]) != 5:
        comments.append("Debt payoff order is missing or incomplete.")
        return 0, comments
    
    # Check if all required debt IDs are included
    required_debts = set(answer_key["debt_payoff_order"])
    submission_debts = set(submission["debt_payoff_order"])
    
    if submission_debts != required_debts:
        missing = required_debts - submission_debts
        extra = submission_debts - required_debts
        if missing:
            comments.append(f"Missing debt IDs: {', '.join(missing)}")
        if extra:
            comments.append(f"Extra debt IDs: {', '.join(extra)}")
        points = 5  # Partial credit for attempting
    else:
        # Evaluate the order
        optimal_order = answer_key["debt_payoff_order"]
        submission_order = submission["debt_payoff_order"]
        
        # Check if using avalanche method (highest interest first)
        if submission_order == optimal_order:
            points = max_points
            comments.append("Perfect debt prioritization using the avalanche method.")
        else:
            # Check if it's a snowball method (smallest balance first)
            if submission_order[0] == "CC2" and "CC1" in submission_order[1:3]:
                points = 20
                comments.append("Used debt snowball method (smallest balance first). While not optimal for interest savings, this is a valid approach.")
            else:
                # Check how many are in the correct position
                correct_positions = sum(1 for i, debt in enumerate(submission_order) if i < len(optimal_order) and debt == optimal_order[i])
                points = 5 + (correct_positions * 4)  # 5 base points + 4 points per correct position
                
                if correct_positions > 0:
                    comments.append(f"{correct_positions} debts are in optimal positions.")
                
                # Check if high-interest debts are prioritized early
                high_interest = {"CC1", "CC2"}
                if submission_order[0] in high_interest and submission_order[1] in high_interest:
                    points += 5
                    comments.append("Correctly prioritized high-interest credit cards early.")
                else:
                    comments.append("Did not optimally prioritize high-interest debts.")
    
    return min(points, max_points), comments


def evaluate_payment_allocation(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the payment allocation component."""
    max_points = 25
    points = 0
    comments = []
    
    # Check if payment allocation exists
    if "monthly_payment_allocation" not in submission:
        comments.append("Monthly payment allocation is missing.")
        return 0, comments
    
    payment_allocation = submission["monthly_payment_allocation"]
    
    # Check if all required debt IDs are included in payment allocation
    required_debts = set(answer_key["monthly_payment_allocation"].keys())
    submission_debts = set(payment_allocation.keys())
    
    if submission_debts != required_debts:
        missing = required_debts - submission_debts
        if missing:
            comments.append(f"Missing payment allocations for: {', '.join(missing)}")
        points = 5  # Partial credit for attempting
    else:
        # Check budget compliance (total <= $1,500)
        total_payment = sum(payment_allocation.values())
        if total_payment > 1500:
            comments.append(f"Total payment (${total_payment:.2f}) exceeds budget of $1,500.00.")
            return 5, comments  # Serious error but give minimal points for attempt
        
        # Check if all minimum payments are met
        min_payments = {
            "CC1": 255,
            "CC2": 96,
            "PL1": 320,
            "AL1": 375,
            "SL1": 210
        }
        
        all_mins_met = True
        for debt_id, min_payment in min_payments.items():
            if debt_id in payment_allocation and payment_allocation[debt_id] < min_payment:
                all_mins_met = False
                comments.append(f"{debt_id} payment (${payment_allocation[debt_id]:.2f}) is below minimum (${min_payment:.2f}).")
        
        if not all_mins_met:
            return 5, comments  # Serious error but give minimal points for attempt
        
        # Award points for budget compliance and meeting minimums
        points += 10
        comments.append("Budget compliance: All payments within $1,500 limit.")
        comments.append("Minimum payment compliance: All minimum payments met.")
        
        # Check strategic allocation (extra to highest interest)
        highest_interest_debt = answer_key["debt_payoff_order"][0]  # Should be CC1
        if payment_allocation[highest_interest_debt] > min_payments[highest_interest_debt]:
            points += 10
            comments.append(f"Strategic allocation: Extra payment directed to highest interest debt ({highest_interest_debt}).")
        else:
            comments.append(f"Did not allocate extra payment to highest interest debt ({highest_interest_debt}).")
        
        # Check if total payment maximizes the budget
        if abs(total_payment - 1500) < 0.01:  # Within a penny of $1,500
            points += 5
            comments.append("Maximized available budget for debt repayment.")
        else:
            comments.append(f"Did not maximize budget. Using ${total_payment:.2f} of $1,500.00 available.")
    
    return min(points, max_points), comments


def evaluate_timeline_accuracy(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the timeline accuracy component."""
    max_points = 20
    points = 0
    comments = []
    
    # Check if timeline data exists
    required_fields = ["total_months_to_debt_freedom", "first_debt_paid_off", "last_debt_paid_off"]
    missing_fields = [field for field in required_fields if field not in submission]
    
    if missing_fields:
        comments.append(f"Missing timeline fields: {', '.join(missing_fields)}")
        return 0, comments
    
    # Evaluate total months to debt freedom
    optimal_months = answer_key["total_months_to_debt_freedom"]
    submission_months = submission["total_months_to_debt_freedom"]
    
    # Allow ±3 months variance
    if abs(submission_months - optimal_months) <= 3:
        points += 8
        if submission_months == optimal_months:
            comments.append(f"Perfect timeline calculation: {submission_months} months.")
        else:
            comments.append(f"Timeline calculation ({submission_months} months) within acceptable range of optimal solution ({optimal_months} months).")
    else:
        points += 3
        comments.append(f"Timeline calculation ({submission_months} months) differs significantly from optimal solution ({optimal_months} months).")
    
    # Evaluate first debt paid off
    if "debt_id" in submission["first_debt_paid_off"] and "month_number" in submission["first_debt_paid_off"]:
        first_debt_id = submission["first_debt_paid_off"]["debt_id"]
        first_debt_month = submission["first_debt_paid_off"]["month_number"]
        optimal_first_debt_id = answer_key["first_debt_paid_off"]["debt_id"]
        optimal_first_debt_month = answer_key["first_debt_paid_off"]["month_number"]
        
        if first_debt_id == optimal_first_debt_id:
            points += 3
            comments.append(f"Correctly identified first debt paid off: {first_debt_id}.")
            
            # Check month accuracy
            if abs(first_debt_month - optimal_first_debt_month) <= 1:
                points += 3
                comments.append(f"Accurate first debt payoff timeline: month {first_debt_month}.")
            else:
                points += 1
                comments.append(f"First debt payoff timeline ({first_debt_month}) differs from optimal ({optimal_first_debt_month}).")
        else:
            comments.append(f"Incorrectly identified first debt paid off as {first_debt_id} instead of {optimal_first_debt_id}.")
    else:
        comments.append("Incomplete first debt paid off information.")
    
    # Evaluate last debt paid off
    if "debt_id" in submission["last_debt_paid_off"] and "month_number" in submission["last_debt_paid_off"]:
        last_debt_id = submission["last_debt_paid_off"]["debt_id"]
        last_debt_month = submission["last_debt_paid_off"]["month_number"]
        optimal_last_debt_id = answer_key["last_debt_paid_off"]["debt_id"]
        optimal_last_debt_month = answer_key["last_debt_paid_off"]["month_number"]
        
        if last_debt_id == optimal_last_debt_id:
            points += 3
            comments.append(f"Correctly identified last debt paid off: {last_debt_id}.")
            
            # Check month accuracy
            if abs(last_debt_month - optimal_last_debt_month) <= 3:
                points += 3
                comments.append(f"Accurate last debt payoff timeline: month {last_debt_month}.")
            else:
                points += 1
                comments.append(f"Last debt payoff timeline ({last_debt_month}) differs from optimal ({optimal_last_debt_month}).")
        else:
            comments.append(f"Incorrectly identified last debt paid off as {last_debt_id} instead of {optimal_last_debt_id}.")
    else:
        comments.append("Incomplete last debt paid off information.")
    
    return min(points, max_points), comments


def evaluate_interest_calculations(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the interest calculations component."""
    max_points = 20
    points = 0
    comments = []
    
    # Check if interest saved is provided
    if "interest_saved_vs_minimum_payments" not in submission:
        comments.append("Interest saved calculation is missing.")
        return 0, comments
    
    # Evaluate interest saved calculation
    optimal_interest_saved = answer_key["interest_saved_vs_minimum_payments"]
    submission_interest_saved = submission["interest_saved_vs_minimum_payments"]
    
    # Allow ±$1,000 variance
    if abs(submission_interest_saved - optimal_interest_saved) <= 1000:
        points += 15
        if abs(submission_interest_saved - optimal_interest_saved) <= 100:
            points += 5
            comments.append(f"Highly accurate interest savings calculation: ${submission_interest_saved:.2f}.")
        else:
            comments.append(f"Interest savings calculation (${submission_interest_saved:.2f}) within acceptable range of optimal solution (${optimal_interest_saved:.2f}).")
    else:
        # Award partial points based on how close they are
        percentage_diff = abs(submission_interest_saved - optimal_interest_saved) / optimal_interest_saved
        if percentage_diff <= 0.2:  # Within 20%
            points += 10
            comments.append(f"Interest savings calculation (${submission_interest_saved:.2f}) differs from optimal solution (${optimal_interest_saved:.2f}) but is reasonably close.")
        elif percentage_diff <= 0.5:  # Within 50%
            points += 5
            comments.append(f"Interest savings calculation (${submission_interest_saved:.2f}) significantly differs from optimal solution (${optimal_interest_saved:.2f}).")
        else:
            points += 2
            comments.append(f"Interest savings calculation (${submission_interest_saved:.2f}) is substantially off from optimal solution (${optimal_interest_saved:.2f}).")
    
    return min(points, max_points), comments


def evaluate_strategy_explanation(submission: Dict, answer_key: Dict) -> Tuple[int, List[str]]:
    """Evaluate the strategy explanation component."""
    max_points = 10
    points = 0
    comments = []
    
    # Check if strategy explanation exists
    if "strategy_explanation" not in submission or not submission["strategy_explanation"]:
        comments.append("Strategy explanation is missing.")
        return 0, comments
    
    explanation = submission["strategy_explanation"]
    
    # Check length (2-3 sentences, max 500 chars)
    if len(explanation) > 500:
        comments.append(f"Strategy explanation exceeds 500 character limit ({len(explanation)} characters).")
    
    # Check for key concepts
    key_concepts = [
        ("avalanche", "debt avalanche", "highest interest"),
        ("snowball", "smallest balance", "smallest debt"),
        ("interest", "minimize interest", "save interest"),
        ("budget", "$1,500", "1500"),
        ("redirect", "roll over", "freed-up")
    ]
    
    concept_count = 0
    for concept_group in key_concepts:
        if any(term.lower() in explanation.lower() for term in concept_group):
            concept_count += 1
    
    # Award points based on concepts covered
    if concept_count >= 4:
        points += 8
        comments.append(f"Comprehensive strategy explanation covering {concept_count}/5 key concepts.")
    elif concept_count >= 2:
        points += 5
        comments.append(f"Adequate strategy explanation covering {concept_count}/5 key concepts.")
    elif concept_count >= 1:
        points += 3
        comments.append(f"Basic strategy explanation covering {concept_count}/5 key concepts.")
    else:
        comments.append("Strategy explanation lacks key debt reduction concepts.")
    
    # Check for clarity and coherence
    sentences = explanation.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        points += 2
        comments.append("Strategy explanation is clear and properly structured.")
    else:
        comments.append("Strategy explanation lacks proper structure or clarity.")
    
    return min(points, max_points), comments


def check_automatic_failure(submission: Dict) -> Tuple[bool, List[str]]:
    """Check for automatic failure conditions."""
    failure_reasons = []
    
    # Check if payment allocation exists
    if "monthly_payment_allocation" not in submission:
        failure_reasons.append("Missing monthly payment allocation.")
        return True, failure_reasons
    
    payment_allocation = submission["monthly_payment_allocation"]
    
    # Check budget compliance (total <= $1,500)
    total_payment = sum(payment_allocation.values())
    if total_payment > 1500:
        failure_reasons.append(f"Total payment (${total_payment:.2f}) exceeds budget of $1,500.00.")
    
    # Check if all minimum payments are met
    min_payments = {
        "CC1": 255,
        "CC2": 96,
        "PL1": 320,
        "AL1": 375,
        "SL1": 210
    }
    
    for debt_id, min_payment in min_payments.items():
        if debt_id in payment_allocation and payment_allocation[debt_id] < min_payment:
            failure_reasons.append(f"{debt_id} payment (${payment_allocation[debt_id]:.2f}) is below minimum (${min_payment:.2f}).")
    
    # Check for coherent strategy
    if "strategy_explanation" not in submission or not submission["strategy_explanation"]:
        failure_reasons.append("Missing strategy explanation.")
    
    # Check for missing required elements
    required_fields = [
        "debt_payoff_order",
        "total_months_to_debt_freedom",
        "monthly_payment_allocation",
        "interest_saved_vs_minimum_payments",
        "first_debt_paid_off",
        "last_debt_paid_off"
    ]
    
    missing_fields = [field for field in required_fields if field not in submission]
    if missing_fields:
        failure_reasons.append(f"Missing required fields: {', '.join(missing_fields)}.")
    
    return bool(failure_reasons), failure_reasons


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "automatic_failure": False,
        "failure_reasons": [],
        "component_scores": {},
        "total_points": 0,
        "max_points": 100,
        "overall_score": 0.0,
        "passing_threshold": 70,
        "passed": False
    }
    
    # Check for automatic failure conditions
    results["automatic_failure"], results["failure_reasons"] = check_automatic_failure(submission)
    
    # Evaluate each component
    components = [
        ("debt_prioritization", evaluate_debt_prioritization, 25, 15),
        ("payment_allocation", evaluate_payment_allocation, 25, 15),
        ("timeline_accuracy", evaluate_timeline_accuracy, 20, 14),
        ("interest_calculations", evaluate_interest_calculations, 20, 14),
        ("strategy_explanation", evaluate_strategy_explanation, 10, 7)
    ]
    
    for component_name, evaluation_func, max_points, threshold in components:
        points, comments = evaluation_func(submission, answer_key)
        
        results["component_scores"][component_name] = {
            "points": points,
            "max_points": max_points,
            "threshold": threshold,
            "passed_component": points >= threshold,
            "comments": comments
        }
        
        results["total_points"] += points
    
    # Calculate overall score as percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Determine if passed based on overall score and no automatic failures
    results["passed"] = (
        not results["automatic_failure"] and 
        results["overall_score"] >= results["passing_threshold"] and
        all(comp["passed_component"] for comp in results["component_scores"].values())
    )
    
    return results


def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    output_path = "test_results.json"
    with open(output_path, 'w') as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_path}")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()