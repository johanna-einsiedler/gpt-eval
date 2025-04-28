import json
import sys
import math

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_total_divisible_surplus(submission, answer_key):
    """Evaluate the total divisible surplus section (10% of score)."""
    correct = submission["total_divisible_surplus"] == answer_key["total_divisible_surplus"]
    return {
        "points_earned": 10 if correct else 0,
        "points_possible": 10,
        "details": "Correct" if correct else f"Incorrect. Expected: {answer_key['total_divisible_surplus']}, Got: {submission['total_divisible_surplus']}"
    }

def evaluate_sources_of_surplus(submission, answer_key):
    """Evaluate the sources of surplus section (15% of score)."""
    sources = ["mortality", "expense", "investment", "lapse"]
    results = {}
    total_points = 0
    
    for source in sources:
        correct = submission["sources_of_surplus"][source] == answer_key["sources_of_surplus"][source]
        points = 3.75 if correct else 0
        total_points += points
        results[source] = {
            "points_earned": points,
            "points_possible": 3.75,
            "details": "Correct" if correct else f"Incorrect. Expected: {answer_key['sources_of_surplus'][source]}, Got: {submission['sources_of_surplus'][source]}"
        }
    
    return {
        "points_earned": total_points,
        "points_possible": 15,
        "details": results
    }

def evaluate_three_factor_formula(submission, answer_key):
    """Evaluate the three-factor formula parameters (15% of score)."""
    parameters = ["interest_rate", "expense_adjustment", "mortality_adjustment"]
    results = {}
    total_points = 0
    
    for param in parameters:
        correct = submission["three_factor_formula_parameters"][param] == answer_key["three_factor_formula_parameters"][param]
        points = 5 if correct else 0
        total_points += points
        results[param] = {
            "points_earned": points,
            "points_possible": 5,
            "details": "Correct" if correct else f"Incorrect. Expected: {answer_key['three_factor_formula_parameters'][param]}, Got: {submission['three_factor_formula_parameters'][param]}"
        }
    
    return {
        "points_earned": total_points,
        "points_possible": 15,
        "details": results
    }

def evaluate_policy_dividends(submission, answer_key):
    """Evaluate the policy dividends calculations (40% of score)."""
    # Create dictionaries for easier lookup
    submission_dividends = {item["policy_id"]: item["dividend_amount"] for item in submission["policy_dividends"]}
    answer_key_dividends = {item["policy_id"]: item["dividend_amount"] for item in answer_key["policy_dividends"]}
    
    correct_count = 0
    results = {}
    
    for policy_id, expected_amount in answer_key_dividends.items():
        if policy_id in submission_dividends:
            submitted_amount = submission_dividends[policy_id]
            # Check if within ±5% of correct amount
            lower_bound = expected_amount * 0.95
            upper_bound = expected_amount * 1.05
            is_correct = lower_bound <= submitted_amount <= upper_bound
            
            if is_correct:
                correct_count += 1
                
            results[policy_id] = {
                "expected": expected_amount,
                "submitted": submitted_amount,
                "is_correct": is_correct
            }
        else:
            results[policy_id] = {
                "expected": expected_amount,
                "submitted": "Missing",
                "is_correct": False
            }
    
    # Determine points based on correct count
    points_earned = 0
    if correct_count >= 90:
        points_earned = 40
    elif correct_count >= 75:
        points_earned = 30
    elif correct_count >= 60:
        points_earned = 20
    elif correct_count >= 45:
        points_earned = 10
    
    return {
        "points_earned": points_earned,
        "points_possible": 40,
        "correct_count": correct_count,
        "total_policies": len(answer_key_dividends),
        "details": results
    }

def evaluate_dividend_metrics(submission, answer_key):
    """Evaluate the dividend metrics (20% of score)."""
    metrics = {
        "average_dividend": {
            "tolerance": 0.01,  # Within ±1%
            "points": 5
        },
        "highest_dividend": {
            "tolerance": 0,  # Exact match
            "points": 5
        },
        "lowest_dividend": {
            "tolerance": 0,  # Exact match
            "points": 5
        },
        "dividend_concentration_ratio": {
            "tolerance": 0.01,  # Within ±0.01
            "points": 5
        }
    }
    
    results = {}
    total_points = 0
    
    for metric, config in metrics.items():
        expected = answer_key["dividend_metrics"][metric]
        submitted = submission["dividend_metrics"][metric]
        
        if config["tolerance"] == 0:
            # Exact match required
            is_correct = submitted == expected
        else:
            # Check if within tolerance
            if metric == "average_dividend":
                # Percentage tolerance
                lower_bound = expected * (1 - config["tolerance"])
                upper_bound = expected * (1 + config["tolerance"])
                is_correct = lower_bound <= submitted <= upper_bound
            else:
                # Absolute tolerance
                is_correct = abs(submitted - expected) <= config["tolerance"]
        
        points = config["points"] if is_correct else 0
        total_points += points
        
        results[metric] = {
            "points_earned": points,
            "points_possible": config["points"],
            "details": "Correct" if is_correct else f"Incorrect. Expected: {expected}, Got: {submitted}"
        }
    
    return {
        "points_earned": total_points,
        "points_possible": 20,
        "details": results
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    total_divisible_surplus_result = evaluate_total_divisible_surplus(submission, answer_key)
    sources_of_surplus_result = evaluate_sources_of_surplus(submission, answer_key)
    three_factor_formula_result = evaluate_three_factor_formula(submission, answer_key)
    policy_dividends_result = evaluate_policy_dividends(submission, answer_key)
    dividend_metrics_result = evaluate_dividend_metrics(submission, answer_key)
    
    # Calculate overall score
    total_points_earned = (
        total_divisible_surplus_result["points_earned"] +
        sources_of_surplus_result["points_earned"] +
        three_factor_formula_result["points_earned"] +
        policy_dividends_result["points_earned"] +
        dividend_metrics_result["points_earned"]
    )
    
    total_points_possible = (
        total_divisible_surplus_result["points_possible"] +
        sources_of_surplus_result["points_possible"] +
        three_factor_formula_result["points_possible"] +
        policy_dividends_result["points_possible"] +
        dividend_metrics_result["points_possible"]
    )
    
    overall_score = (total_points_earned / total_points_possible) * 100
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passing_threshold": 70,
        "passed": overall_score >= 70,
        "sections": {
            "total_divisible_surplus": total_divisible_surplus_result,
            "sources_of_surplus": sources_of_surplus_result,
            "three_factor_formula": three_factor_formula_result,
            "policy_dividends": policy_dividends_result,
            "dividend_metrics": dividend_metrics_result
        },
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    print(f"Result: {'PASS' if overall_score >= 70 else 'FAIL'}")

if __name__ == "__main__":
    main()