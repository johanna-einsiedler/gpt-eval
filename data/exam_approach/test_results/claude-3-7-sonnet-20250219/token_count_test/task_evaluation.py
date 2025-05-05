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

def evaluate_numeric_answer(candidate_value, correct_value):
    """Evaluate a numeric answer with partial credit."""
    if candidate_value is None:
        return 0
    
    # Calculate percentage difference
    if correct_value == 0:
        percentage_diff = float('inf') if candidate_value != 0 else 0
    else:
        percentage_diff = abs((candidate_value - correct_value) / correct_value)
    
    # Assign points based on accuracy
    if percentage_diff <= 0.02:  # Within 2%
        return 1.0
    elif percentage_diff <= 0.05:  # Within 5%
        return 0.5
    else:
        return 0.0

def evaluate_list_answer(candidate_list, correct_list):
    """Evaluate a list answer with partial credit."""
    if not candidate_list:
        return 0
    
    # Convert to sets for comparison
    candidate_set = set(candidate_list)
    correct_set = set(correct_list)
    
    if candidate_set == correct_set:
        return 1.0
    
    # Calculate percentage of correct items
    if len(correct_set) == 0:
        return 1.0 if len(candidate_set) == 0 else 0.0
    
    correct_items = len(candidate_set.intersection(correct_set))
    percentage_correct = correct_items / len(correct_set)
    
    if percentage_correct >= 0.7:  # At least 70% correct
        return 0.5
    else:
        return 0.0

def evaluate_single_answer(candidate_value, correct_value):
    """Evaluate a single answer (no partial credit)."""
    if candidate_value is None:
        return 0
    return 1.0 if candidate_value == correct_value else 0.0

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "exercise1": {},
        "exercise2": {},
        "exercise3": {},
        "points_earned": {},
        "points_possible": {},
        "passed_critical_elements": False
    }
    
    total_points = 0
    total_possible = 13  # Total possible points as per evaluation criteria
    
    # Exercise 1 evaluation (4 points)
    ex1_points = 0
    
    # Budget variance (1 point)
    score = evaluate_numeric_answer(
        submission.get("exercise1", {}).get("budget_variance"),
        answer_key["exercise1"]["budget_variance"]
    )
    results["exercise1"]["budget_variance"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise1"]["budget_variance"]
    }
    ex1_points += score
    
    # Overspent categories (1 point)
    score = evaluate_list_answer(
        submission.get("exercise1", {}).get("overspent_categories"),
        answer_key["exercise1"]["overspent_categories"]
    )
    results["exercise1"]["overspent_categories"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise1"]["overspent_categories"]
    }
    ex1_points += score
    
    # Underspent categories (1 point)
    score = evaluate_list_answer(
        submission.get("exercise1", {}).get("underspent_categories"),
        answer_key["exercise1"]["underspent_categories"]
    )
    results["exercise1"]["underspent_categories"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise1"]["underspent_categories"]
    }
    ex1_points += score
    
    # R&D percentage (1 point)
    score = evaluate_numeric_answer(
        submission.get("exercise1", {}).get("total_rd_percentage"),
        answer_key["exercise1"]["total_rd_percentage"]
    )
    results["exercise1"]["total_rd_percentage"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise1"]["total_rd_percentage"]
    }
    ex1_points += score
    
    results["points_earned"]["exercise1"] = ex1_points
    results["points_possible"]["exercise1"] = 4
    total_points += ex1_points
    
    # Exercise 2 evaluation (3 points)
    ex2_points = 0
    
    # Campaign ROI (1 point)
    score = evaluate_numeric_answer(
        submission.get("exercise2", {}).get("campaign_roi"),
        answer_key["exercise2"]["campaign_roi"]
    )
    results["exercise2"]["campaign_roi"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise2"]["campaign_roi"]
    }
    ex2_points += score
    
    # Most efficient channel (1 point)
    score = evaluate_single_answer(
        submission.get("exercise2", {}).get("most_efficient_channel"),
        answer_key["exercise2"]["most_efficient_channel"]
    )
    results["exercise2"]["most_efficient_channel"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise2"]["most_efficient_channel"]
    }
    ex2_points += score
    
    # Breakeven point (1 point)
    score = evaluate_numeric_answer(
        submission.get("exercise2", {}).get("breakeven_point"),
        answer_key["exercise2"]["breakeven_point"]
    )
    results["exercise2"]["breakeven_point"] = {
        "score": score,
        "points": score,
        "correct_answer": answer_key["exercise2"]["breakeven_point"]
    }
    ex2_points += score
    
    results["points_earned"]["exercise2"] = ex2_points
    results["points_possible"]["exercise2"] = 3
    total_points += ex2_points
    
    # Exercise 3 evaluation (6 points)
    ex3_points = 0
    
    # Year 1 profit (1.5 points)
    score = evaluate_numeric_answer(
        submission.get("exercise3", {}).get("year1_profit"),
        answer_key["exercise3"]["year1_profit"]
    )
    results["exercise3"]["year1_profit"] = {
        "score": score,
        "points": score * 1.5,  # Worth 1.5 points
        "correct_answer": answer_key["exercise3"]["year1_profit"]
    }
    ex3_points += score * 1.5
    
    # Projected ROI (1.5 points)
    score = evaluate_numeric_answer(
        submission.get("exercise3", {}).get("projected_roi"),
        answer_key["exercise3"]["projected_roi"]
    )
    results["exercise3"]["projected_roi"] = {
        "score": score,
        "points": score * 1.5,  # Worth 1.5 points
        "correct_answer": answer_key["exercise3"]["projected_roi"]
    }
    ex3_points += score * 1.5
    
    # Payback period (1.5 points)
    score = evaluate_numeric_answer(
        submission.get("exercise3", {}).get("payback_period_months"),
        answer_key["exercise3"]["payback_period_months"]
    )
    results["exercise3"]["payback_period_months"] = {
        "score": score,
        "points": score * 1.5,  # Worth 1.5 points
        "correct_answer": answer_key["exercise3"]["payback_period_months"]
    }
    ex3_points += score * 1.5
    
    # Profit margin percentage (1.5 points)
    score = evaluate_numeric_answer(
        submission.get("exercise3", {}).get("profit_margin_percentage"),
        answer_key["exercise3"]["profit_margin_percentage"]
    )
    results["exercise3"]["profit_margin_percentage"] = {
        "score": score,
        "points": score * 1.5,  # Worth 1.5 points
        "correct_answer": answer_key["exercise3"]["profit_margin_percentage"]
    }
    ex3_points += score * 1.5
    
    results["points_earned"]["exercise3"] = ex3_points
    results["points_possible"]["exercise3"] = 6
    total_points += ex3_points
    
    # Check critical elements requirement (at least one correct answer from each exercise)
    has_ex1_correct = any(results["exercise1"][key]["score"] > 0 for key in results["exercise1"] if key not in ["points_earned", "points_possible"])
    has_ex2_correct = any(results["exercise2"][key]["score"] > 0 for key in results["exercise2"] if key not in ["points_earned", "points_possible"])
    has_ex3_correct = any(results["exercise3"][key]["score"] > 0 for key in results["exercise3"] if key not in ["points_earned", "points_possible"])
    
    results["passed_critical_elements"] = has_ex1_correct and has_ex2_correct and has_ex3_correct
    
    # Calculate overall score as percentage
    results["total_points"] = total_points
    results["total_possible"] = total_possible
    results["overall_score"] = (total_points / total_possible) * 100
    
    # Determine if candidate passed (10 out of 13 points and passed critical elements)
    results["passed"] = total_points >= 10 and results["passed_critical_elements"]
    
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
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()