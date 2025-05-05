#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        sys.exit(1)

def evaluate_annual_budget_total(submission, answer_key):
    """Evaluate the annual budget total with partial credit."""
    correct_value = answer_key["annual_budget_total"]
    submission_value = submission.get("annual_budget_total")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    # Calculate percentage difference
    percentage_diff = abs(submission_value - correct_value) / correct_value
    
    if percentage_diff <= 0.02:  # Within 2%
        return {"score": 1, "max_score": 1, "feedback": "Correct (within 2% margin)"}
    elif percentage_diff <= 0.05:  # Within 5%
        return {"score": 0.5, "max_score": 1, "feedback": "Partially correct (within 5% margin)"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect (outside 5% margin)"}

def evaluate_q1_variance(submission, answer_key):
    """Evaluate the Q1 variance percentage."""
    correct_value = answer_key["q1_variance_percentage"]
    submission_value = submission.get("q1_variance_percentage")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    # Allow a small rounding difference
    if abs(submission_value - correct_value) < 0.0001:
        return {"score": 1, "max_score": 1, "feedback": "Correct"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect"}

def evaluate_fuel_adjustment(submission, answer_key):
    """Evaluate the fuel cost adjustment."""
    correct_value = answer_key["fuel_cost_adjustment"]
    submission_value = submission.get("fuel_cost_adjustment")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    if submission_value == correct_value:
        return {"score": 1, "max_score": 1, "feedback": "Correct"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect"}

def evaluate_maintenance_allocation(submission, answer_key):
    """Evaluate the maintenance allocation."""
    correct_value = answer_key["maintenance_allocation"]
    submission_value = submission.get("maintenance_allocation")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    if submission_value == correct_value:
        return {"score": 1, "max_score": 1, "feedback": "Correct"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect"}

def evaluate_priority_ranking(submission, answer_key):
    """Evaluate the priority ranking with partial credit."""
    correct_value = answer_key["priority_ranking"]
    submission_value = submission.get("priority_ranking")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    # Check if arrays have the same length
    if len(submission_value) != len(correct_value):
        return {"score": 0, "max_score": 1, "feedback": "Incorrect number of priorities"}
    
    # Check if it's an exact match
    if submission_value == correct_value:
        return {"score": 1, "max_score": 1, "feedback": "Correct"}
    
    # Check if top 2 priorities are correct
    top_2_correct = submission_value[:2] == correct_value[:2]
    if top_2_correct:
        return {"score": 0.5, "max_score": 1, "feedback": "Partially correct (top 2 priorities correct)"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect"}

def evaluate_cost_per_mile(submission, answer_key):
    """Evaluate the cost per mile with partial credit."""
    correct_value = answer_key["cost_per_mile"]
    submission_value = submission.get("cost_per_mile")
    
    if submission_value is None:
        return {"score": 0, "max_score": 1, "feedback": "No answer provided"}
    
    difference = abs(submission_value - correct_value)
    
    if difference <= 0.02:  # Within $0.02
        return {"score": 1, "max_score": 1, "feedback": "Correct (within $0.02 margin)"}
    elif difference <= 0.05:  # Within $0.05
        return {"score": 0.5, "max_score": 1, "feedback": "Partially correct (within $0.05 margin)"}
    else:
        return {"score": 0, "max_score": 1, "feedback": "Incorrect (outside $0.05 margin)"}

def check_critical_elements(results):
    """Check if critical elements are correct."""
    budget_result = results["annual_budget_total"]
    maintenance_result = results["maintenance_allocation"]
    
    # For budget, consider it correct if it got any points (full or partial)
    budget_correct = budget_result["score"] > 0
    maintenance_correct = maintenance_result["score"] == 1
    
    return budget_correct and maintenance_correct

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    results = {
        "annual_budget_total": evaluate_annual_budget_total(submission, answer_key),
        "q1_variance_percentage": evaluate_q1_variance(submission, answer_key),
        "fuel_cost_adjustment": evaluate_fuel_adjustment(submission, answer_key),
        "maintenance_allocation": evaluate_maintenance_allocation(submission, answer_key),
        "priority_ranking": evaluate_priority_ranking(submission, answer_key),
        "cost_per_mile": evaluate_cost_per_mile(submission, answer_key)
    }
    
    # Calculate total score
    total_score = sum(item["score"] for item in results.values())
    max_score = sum(item["max_score"] for item in results.values())
    overall_percentage = (total_score / max_score) * 100
    
    # Count number of correct answers (full or partial credit)
    correct_answers = sum(1 for item in results.values() if item["score"] > 0)
    
    # Check critical elements
    critical_elements_passed = check_critical_elements(results)
    
    # Determine if candidate passed
    passed = correct_answers >= 4 and critical_elements_passed
    
    # Add candidate ID if available
    candidate_id = submission.get("candidate_id", "Unknown")
    
    return {
        "candidate_id": candidate_id,
        "results": results,
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": overall_percentage,
        "correct_answers": correct_answers,
        "critical_elements_passed": critical_elements_passed,
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
    
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {evaluation_results['overall_score']:.2f}%")
    print(f"Passed: {evaluation_results['passed']}")

if __name__ == "__main__":
    main()