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

def is_close_enough(candidate_value, answer_value, tolerance=0.05):
    """Check if candidate's value is within tolerance of the answer."""
    if isinstance(candidate_value, str) or isinstance(answer_value, str):
        return candidate_value == answer_value
    
    # For numerical values
    if answer_value == 0:
        return abs(candidate_value) < tolerance
    
    relative_error = abs((candidate_value - answer_value) / answer_value)
    return relative_error <= tolerance

def evaluate_section(candidate_section, answer_section, section_name):
    """Evaluate a section of the submission against the answer key."""
    results = {
        "total_points": len(answer_section),
        "points_earned": 0,
        "details": {}
    }
    
    for key, answer_value in answer_section.items():
        if key in candidate_section:
            candidate_value = candidate_section.get(key)
            is_correct = is_close_enough(candidate_value, answer_value)
            
            results["details"][key] = {
                "candidate_value": candidate_value,
                "expected_value": answer_value,
                "is_correct": is_correct
            }
            
            if is_correct:
                results["points_earned"] += 1
        else:
            results["details"][key] = {
                "candidate_value": None,
                "expected_value": answer_value,
                "is_correct": False,
                "error": "Missing value"
            }
    
    return results

def check_budget_sum(candidate_budget):
    """Check if budget allocation percentages sum to 1.0 (100%)."""
    budget_keys = [
        "search_budget_percentage", 
        "social_budget_percentage", 
        "display_budget_percentage", 
        "email_budget_percentage"
    ]
    
    total = sum(candidate_budget.get(key, 0) for key in budget_keys)
    return math.isclose(total, 1.0, abs_tol=0.01)

def evaluate_submission(candidate, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "roi_model": evaluate_section(
            candidate.get("roi_model", {}), 
            answer_key.get("roi_model", {}),
            "roi_model"
        ),
        "revenue_forecast": evaluate_section(
            candidate.get("revenue_forecast", {}), 
            answer_key.get("revenue_forecast", {}),
            "revenue_forecast"
        ),
        "cpa_analysis": evaluate_section(
            candidate.get("cpa_analysis", {}), 
            answer_key.get("cpa_analysis", {}),
            "cpa_analysis"
        ),
        "budget_allocation": evaluate_section(
            candidate.get("budget_allocation", {}), 
            answer_key.get("budget_allocation", {}),
            "budget_allocation"
        )
    }
    
    # Check if budget percentages sum to 100%
    budget_sum_correct = check_budget_sum(candidate.get("budget_allocation", {}))
    results["budget_allocation"]["budget_sum_correct"] = budget_sum_correct
    
    # Calculate overall score
    total_points = sum(section["total_points"] for section in results.values())
    points_earned = sum(section["points_earned"] for section in results.values())
    
    # Deduct a point if budget doesn't sum to 100%
    if not budget_sum_correct and "budget_allocation" in results:
        points_earned = max(0, points_earned - 1)
    
    results["overall_score"] = round((points_earned / total_points) * 100, 2) if total_points > 0 else 0
    results["total_points"] = total_points
    results["points_earned"] = points_earned
    
    # Add candidate ID if available
    if "candidate_id" in candidate:
        results["candidate_id"] = candidate["candidate_id"]
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(candidate, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")

if __name__ == "__main__":
    main()