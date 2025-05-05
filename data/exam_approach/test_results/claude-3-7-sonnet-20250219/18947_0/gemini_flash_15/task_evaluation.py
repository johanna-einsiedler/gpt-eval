#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_modification_needed(submission: Dict, answer_key: Dict) -> Tuple[int, int]:
    """Evaluate if the candidate correctly identified whether modifications are needed."""
    points = 0
    max_points = 3
    
    for case in ["case1", "case2", "case3"]:
        if submission.get(case, {}).get("modification_needed") == answer_key.get(case, {}).get("modification_needed"):
            points += 1
    
    return points, max_points

def evaluate_recommended_changes(submission: Dict, answer_key: Dict) -> Tuple[int, int]:
    """Evaluate the recommended changes for each case."""
    points = 0
    max_points = 7  # 1 for case1, 3 for case2, 3 for case3
    
    # Case 1 - Must recommend the optimal split approach (1 point)
    sub_changes = set(submission.get("case1", {}).get("recommended_changes", []))
    key_changes = set(answer_key.get("case1", {}).get("recommended_changes", []))
    
    if "Split additional income: $425 to debt, $425 to savings" in sub_changes:
        points += 1
    
    # Case 2 - Must identify all three key elements (3 points)
    sub_changes = set(submission.get("case2", {}).get("recommended_changes", []))
    
    if "Reduce childcare budget by $600/month" in sub_changes:
        points += 1
    if "Allocate $200/month for mother's medical expenses" in sub_changes:
        points += 1
    if "Split mother's contribution: $600 to debt payoff, $300 to emergency fund" in sub_changes:
        points += 1
    
    # Case 3 - Must identify all three key elements (3 points)
    sub_changes = set(submission.get("case3", {}).get("recommended_changes", []))
    
    if "Reduce entertainment budget by $200/month" in sub_changes:
        points += 1
    if "Open HSA account with $100/month contribution" in sub_changes:
        points += 1
    if "Restructure debt payments to focus on highest interest debt" in sub_changes:
        points += 1
    
    return points, max_points

def evaluate_budget_impact(submission: Dict, answer_key: Dict) -> Tuple[int, int]:
    """Evaluate the budget impact calculations."""
    points = 0
    max_points = 3
    
    for case in ["case1", "case2", "case3"]:
        sub_impact = submission.get(case, {}).get("monthly_budget_impact", 0)
        key_impact = answer_key.get(case, {}).get("monthly_budget_impact", 0)
        
        # Must be within ±$50 of the correct amount
        if abs(sub_impact - key_impact) <= 50:
            points += 1
        # No credit if directionally incorrect
        elif (sub_impact > 0 and key_impact < 0) or (sub_impact < 0 and key_impact > 0):
            points += 0
    
    return points, max_points

def evaluate_debt_payoff_impact(submission: Dict, answer_key: Dict) -> Tuple[int, int]:
    """Evaluate the debt payoff impact calculations."""
    points = 0
    max_points = 3
    
    for case in ["case1", "case2", "case3"]:
        sub_impact = submission.get(case, {}).get("debt_payoff_impact_months", 0)
        key_impact = answer_key.get(case, {}).get("debt_payoff_impact_months", 0)
        
        # Must be within ±3 months of the correct amount
        if abs(sub_impact - key_impact) <= 3:
            points += 1
        # No credit if directionally incorrect
        elif (sub_impact > 0 and key_impact < 0) or (sub_impact < 0 and key_impact > 0):
            points += 0
    
    return points, max_points

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_details": {}
    }
    
    total_points = 0
    total_max_points = 0
    
    # Evaluate modification needed
    mod_points, mod_max = evaluate_modification_needed(submission, answer_key)
    results["evaluation_details"]["modification_needed"] = {
        "points": mod_points,
        "max_points": mod_max,
        "comments": f"Correctly identified {mod_points}/{mod_max} cases requiring modification."
    }
    total_points += mod_points
    total_max_points += mod_max
    
    # Evaluate recommended changes
    rec_points, rec_max = evaluate_recommended_changes(submission, answer_key)
    results["evaluation_details"]["recommended_changes"] = {
        "points": rec_points,
        "max_points": rec_max,
        "comments": f"Identified {rec_points}/{rec_max} key recommended changes across all cases."
    }
    total_points += rec_points
    total_max_points += rec_max
    
    # Evaluate budget impact
    budget_points, budget_max = evaluate_budget_impact(submission, answer_key)
    results["evaluation_details"]["budget_impact"] = {
        "points": budget_points,
        "max_points": budget_max,
        "comments": f"Calculated {budget_points}/{budget_max} budget impacts within acceptable range."
    }
    total_points += budget_points
    total_max_points += budget_max
    
    # Evaluate debt payoff impact
    debt_points, debt_max = evaluate_debt_payoff_impact(submission, answer_key)
    results["evaluation_details"]["debt_payoff_impact"] = {
        "points": debt_points,
        "max_points": debt_max,
        "comments": f"Calculated {debt_points}/{debt_max} debt payoff impacts within acceptable range."
    }
    total_points += debt_points
    total_max_points += debt_max
    
    # Calculate overall score
    overall_percentage = (total_points / total_max_points) * 100 if total_max_points > 0 else 0
    
    results["total_points"] = total_points
    results["max_points"] = total_max_points
    results["overall_score"] = round(overall_percentage, 2)
    results["passed"] = total_points >= 10  # Passing score is 10 points
    
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
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()