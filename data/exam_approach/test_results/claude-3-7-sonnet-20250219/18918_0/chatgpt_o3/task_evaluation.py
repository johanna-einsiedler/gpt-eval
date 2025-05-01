#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, List, Any, Union

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_budget_variance(submission: int, answer: int) -> Dict:
    """Evaluate the budget variance answer."""
    # Allow for ±5% of the correct value
    margin = answer * 0.05
    is_correct = abs(submission - answer) <= margin
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The correct budget variance is {answer}."
    }

def evaluate_largest_expense(submission: str, answer: str) -> Dict:
    """Evaluate the largest expense category answer."""
    is_correct = submission == answer
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The largest expense category is '{answer}'."
    }

def evaluate_expense_trend(submission: str, answer: str) -> Dict:
    """Evaluate the expense trend direction answer."""
    is_correct = submission.lower() == answer.lower()
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The expense trend is '{answer}'."
    }

def evaluate_donor_retention(submission: float, answer: float) -> Dict:
    """Evaluate the donor retention rate answer."""
    # Allow for ±5% of the correct value
    margin = answer * 0.05
    is_correct = abs(submission - answer) <= margin
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The donor retention rate is {answer}."
    }

def evaluate_cost_per_dollar(submission: float, answer: float) -> Dict:
    """Evaluate the cost per dollar raised answer."""
    # Allow for ±5% of the correct value
    margin = answer * 0.05
    is_correct = abs(submission - answer) <= margin
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The cost per dollar raised is {answer}."
    }

def evaluate_over_budget_categories(submission: List[str], answer: List[str]) -> Dict:
    """Evaluate the over budget categories answer."""
    # Convert to sets for easier comparison
    submission_set = set(submission)
    answer_set = set(answer)
    
    # Calculate correctness percentage
    if len(answer_set) == 0:
        percentage_correct = 1.0 if len(submission_set) == 0 else 0.0
    else:
        correct_items = len(submission_set.intersection(answer_set))
        total_unique_items = len(submission_set.union(answer_set))
        percentage_correct = correct_items / len(answer_set) if len(answer_set) > 0 else 0
    
    is_correct = percentage_correct >= 0.8  # At least 80% correct
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "percentage_correct": round(percentage_correct * 100, 2),
        "submitted_answer": sorted(list(submission_set)),
        "correct_answer": sorted(list(answer_set)),
        "feedback": "Correct" if is_correct else f"Incorrect. The over budget categories are {sorted(list(answer_set))}."
    }

def evaluate_highest_revenue_month(submission: str, answer: str) -> Dict:
    """Evaluate the month with highest revenue answer."""
    is_correct = submission == answer
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The month with highest revenue is '{answer}'."
    }

def evaluate_fundraising_roi(submission: float, answer: float) -> Dict:
    """Evaluate the fundraising ROI answer."""
    # Allow for ±5% of the correct value
    margin = answer * 0.05
    is_correct = abs(submission - answer) <= margin
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The fundraising ROI is {answer}."
    }

def evaluate_expense_percentages(submission: Dict[str, float], answer: Dict[str, float]) -> Dict:
    """Evaluate the expense category percentages answer."""
    # Check if all required categories are present
    missing_categories = set(answer.keys()) - set(submission.keys())
    
    if missing_categories:
        return {
            "points_earned": 0,
            "points_possible": 1,
            "is_correct": False,
            "submitted_answer": submission,
            "correct_answer": answer,
            "feedback": f"Missing categories: {', '.join(missing_categories)}"
        }
    
    # Calculate percentage of correct values (within 5% margin)
    correct_count = 0
    for category, correct_value in answer.items():
        if category in submission:
            submitted_value = submission[category]
            margin = correct_value * 0.05
            if abs(submitted_value - correct_value) <= margin:
                correct_count += 1
    
    percentage_correct = correct_count / len(answer)
    is_correct = percentage_correct >= 0.8  # At least 80% correct
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "percentage_correct": round(percentage_correct * 100, 2),
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else "Incorrect. At least 80% of expense percentages must be within 5% of the correct values."
    }

def evaluate_budget_status(submission: str, answer: str) -> Dict:
    """Evaluate the budget status answer."""
    is_correct = submission.lower() == answer.lower()
    
    return {
        "points_earned": 1 if is_correct else 0,
        "points_possible": 1,
        "is_correct": is_correct,
        "submitted_answer": submission,
        "correct_answer": answer,
        "feedback": "Correct" if is_correct else f"Incorrect. The budget status is '{answer}'."
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_details": {}
    }
    
    # Evaluate each question
    results["evaluation_details"]["budget_variance_total"] = evaluate_budget_variance(
        submission.get("budget_variance_total", 0), 
        answer_key.get("budget_variance_total", 0)
    )
    
    results["evaluation_details"]["largest_expense_category"] = evaluate_largest_expense(
        submission.get("largest_expense_category", ""), 
        answer_key.get("largest_expense_category", "")
    )
    
    results["evaluation_details"]["expense_trend_direction"] = evaluate_expense_trend(
        submission.get("expense_trend_direction", ""), 
        answer_key.get("expense_trend_direction", "")
    )
    
    results["evaluation_details"]["donor_retention_rate"] = evaluate_donor_retention(
        submission.get("donor_retention_rate", 0.0), 
        answer_key.get("donor_retention_rate", 0.0)
    )
    
    results["evaluation_details"]["cost_per_dollar_raised"] = evaluate_cost_per_dollar(
        submission.get("cost_per_dollar_raised", 0.0), 
        answer_key.get("cost_per_dollar_raised", 0.0)
    )
    
    results["evaluation_details"]["over_budget_categories"] = evaluate_over_budget_categories(
        submission.get("over_budget_categories", []), 
        answer_key.get("over_budget_categories", [])
    )
    
    results["evaluation_details"]["month_with_highest_revenue"] = evaluate_highest_revenue_month(
        submission.get("month_with_highest_revenue", ""), 
        answer_key.get("month_with_highest_revenue", "")
    )
    
    results["evaluation_details"]["fundraising_roi"] = evaluate_fundraising_roi(
        submission.get("fundraising_roi", 0.0), 
        answer_key.get("fundraising_roi", 0.0)
    )
    
    results["evaluation_details"]["expense_category_percentages"] = evaluate_expense_percentages(
        submission.get("expense_category_percentages", {}), 
        answer_key.get("expense_category_percentages", {})
    )
    
    results["evaluation_details"]["budget_status"] = evaluate_budget_status(
        submission.get("budget_status", ""), 
        answer_key.get("budget_status", "")
    )
    
    # Calculate overall score
    total_points_earned = sum(q["points_earned"] for q in results["evaluation_details"].values())
    total_points_possible = sum(q["points_possible"] for q in results["evaluation_details"].values())
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    
    # Calculate critical questions score
    critical_questions = ["budget_variance_total", "cost_per_dollar_raised", 
                         "over_budget_categories", "fundraising_roi", "budget_status"]
    critical_points_earned = sum(results["evaluation_details"][q]["points_earned"] for q in critical_questions)
    critical_points_possible = sum(results["evaluation_details"][q]["points_possible"] for q in critical_questions)
    results["critical_questions_score"] = round((critical_points_earned / critical_points_possible) * 100, 2)
    
    # Determine if the candidate passed
    correct_answers_count = sum(1 for q in results["evaluation_details"].values() if q["is_correct"])
    critical_correct_count = sum(1 for q in critical_questions if results["evaluation_details"][q]["is_correct"])
    
    results["passed"] = (correct_answers_count >= 7 and critical_correct_count >= 3)
    
    # Add summary
    results["summary"] = {
        "total_questions": total_points_possible,
        "correct_answers": correct_answers_count,
        "critical_questions_correct": critical_correct_count,
        "overall_score_percentage": results["overall_score"],
        "critical_questions_score_percentage": results["critical_questions_score"],
        "passed": results["passed"]
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
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
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Critical Questions Score: {results['critical_questions_score']}%")
    print(f"Passed: {'Yes' if results['passed'] else 'No'}")

if __name__ == "__main__":
    main()