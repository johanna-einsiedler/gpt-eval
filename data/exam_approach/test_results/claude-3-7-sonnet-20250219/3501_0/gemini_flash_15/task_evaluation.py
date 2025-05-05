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

def compare_values(candidate_value, key_value, tolerance=0.0001):
    """Compare numerical values within tolerance."""
    if candidate_value is None:
        return False
    
    # Handle non-numeric values (like strings)
    if not isinstance(key_value, (int, float)):
        return candidate_value == key_value
    
    # Handle numeric values
    if isinstance(key_value, int):
        return candidate_value == key_value
    else:
        return abs(candidate_value - key_value) <= tolerance

def evaluate_task1(candidate, answer_key):
    """Evaluate Task 1: Mortality Analysis."""
    results = {"points": 0, "max_points": 12, "details": {}}
    
    # Crude death rates (10 items)
    results["details"]["crude_death_rates"] = {}
    for age_group, key_value in answer_key["task1"]["crude_death_rates"].items():
        candidate_value = candidate["task1"]["crude_death_rates"].get(age_group)
        correct = compare_values(candidate_value, key_value)
        results["details"]["crude_death_rates"][age_group] = {
            "candidate_value": candidate_value,
            "correct_value": key_value,
            "points": 1 if correct else 0,
            "max_points": 1
        }
        if correct:
            results["points"] += 1
    
    # Age-standardized death rate
    key_value = answer_key["task1"]["age_standardized_death_rate"]
    candidate_value = candidate["task1"]["age_standardized_death_rate"]
    correct = compare_values(candidate_value, key_value)
    results["details"]["age_standardized_death_rate"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    # Life expectancy at birth (special tolerance of ±0.5 years)
    key_value = answer_key["task1"]["life_expectancy_at_birth"]
    candidate_value = candidate["task1"]["life_expectancy_at_birth"]
    correct = candidate_value is not None and abs(candidate_value - key_value) <= 0.5
    results["details"]["life_expectancy_at_birth"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1,
        "note": "Accepted range: 73.7000 to 74.7000"
    }
    if correct:
        results["points"] += 1
    
    # Highest mortality improvement age group
    key_value = answer_key["task1"]["highest_mortality_improvement_age_group"]
    candidate_value = candidate["task1"]["highest_mortality_improvement_age_group"]
    correct = candidate_value == key_value
    results["details"]["highest_mortality_improvement_age_group"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    return results

def evaluate_task2(candidate, answer_key):
    """Evaluate Task 2: Disability Claims Analysis."""
    results = {"points": 0, "max_points": 10, "details": {}}
    
    # Disability incidence rates (3 items)
    results["details"]["disability_incidence_rates"] = {}
    for category, key_value in answer_key["task2"]["disability_incidence_rates"].items():
        candidate_value = candidate["task2"]["disability_incidence_rates"].get(category)
        correct = compare_values(candidate_value, key_value)
        results["details"]["disability_incidence_rates"][category] = {
            "candidate_value": candidate_value,
            "correct_value": key_value,
            "points": 1 if correct else 0,
            "max_points": 1
        }
        if correct:
            results["points"] += 1
    
    # Average claim duration (5 items)
    results["details"]["average_claim_duration"] = {}
    for category, key_value in answer_key["task2"]["average_claim_duration"].items():
        candidate_value = candidate["task2"]["average_claim_duration"].get(category)
        correct = compare_values(candidate_value, key_value)
        results["details"]["average_claim_duration"][category] = {
            "candidate_value": candidate_value,
            "correct_value": key_value,
            "points": 1 if correct else 0,
            "max_points": 1
        }
        if correct:
            results["points"] += 1
    
    # Probability claim exceeds 24 months
    key_value = answer_key["task2"]["probability_claim_exceeds_24_months"]
    candidate_value = candidate["task2"]["probability_claim_exceeds_24_months"]
    correct = compare_values(candidate_value, key_value)
    results["details"]["probability_claim_exceeds_24_months"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    # Gender difference p-value (special tolerance)
    key_value = answer_key["task2"]["gender_difference_p_value"]
    candidate_value = candidate["task2"]["gender_difference_p_value"]
    # Accept answers between 0.6500 and 0.7200
    correct = candidate_value is not None and 0.6500 <= candidate_value <= 0.7200
    results["details"]["gender_difference_p_value"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1,
        "note": "Accepted range: 0.6500 to 0.7200"
    }
    if correct:
        results["points"] += 1
    
    # Overall disability rate confidence interval (2 items)
    for bound in ["lower", "upper"]:
        key_value = answer_key["task2"]["overall_disability_rate_confidence_interval"][bound]
        candidate_value = candidate["task2"]["overall_disability_rate_confidence_interval"].get(bound)
        correct = compare_values(candidate_value, key_value)
        if "overall_disability_rate_confidence_interval" not in results["details"]:
            results["details"]["overall_disability_rate_confidence_interval"] = {}
        results["details"]["overall_disability_rate_confidence_interval"][bound] = {
            "candidate_value": candidate_value,
            "correct_value": key_value,
            "points": 1 if correct else 0,
            "max_points": 1
        }
        if correct:
            results["points"] += 1
    
    return results

def evaluate_task3(candidate, answer_key):
    """Evaluate Task 3: Retirement Rate Analysis."""
    results = {"points": 0, "max_points": 8, "details": {}}
    
    # Retirement rates (5 items)
    results["details"]["retirement_rates"] = {}
    for age_group, key_value in answer_key["task3"]["retirement_rates"].items():
        candidate_value = candidate["task3"]["retirement_rates"].get(age_group)
        correct = compare_values(candidate_value, key_value)
        results["details"]["retirement_rates"][age_group] = {
            "candidate_value": candidate_value,
            "correct_value": key_value,
            "points": 1 if correct else 0,
            "max_points": 1
        }
        if correct:
            results["points"] += 1
    
    # Projected retirements next year
    key_value = answer_key["task3"]["projected_retirements_next_year"]
    candidate_value = candidate["task3"]["projected_retirements_next_year"]
    correct = candidate_value == key_value
    results["details"]["projected_retirements_next_year"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    # Present value future benefits (special tolerance of ±1%)
    key_value = answer_key["task3"]["present_value_future_benefits"]
    candidate_value = candidate["task3"]["present_value_future_benefits"]
    # Accept answers within ±1% of the correct value
    correct = candidate_value is not None and abs(candidate_value - key_value) <= 0.01 * key_value
    results["details"]["present_value_future_benefits"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1,
        "note": f"Accepted range: {int(key_value * 0.99)} to {int(key_value * 1.01)}"
    }
    if correct:
        results["points"] += 1
    
    # Funding ratio
    key_value = answer_key["task3"]["funding_ratio"]
    candidate_value = candidate["task3"]["funding_ratio"]
    correct = compare_values(candidate_value, key_value)
    results["details"]["funding_ratio"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    # Discount rate sensitivity
    key_value = answer_key["task3"]["discount_rate_sensitivity"]
    candidate_value = candidate["task3"]["discount_rate_sensitivity"]
    correct = compare_values(candidate_value, key_value)
    results["details"]["discount_rate_sensitivity"] = {
        "candidate_value": candidate_value,
        "correct_value": key_value,
        "points": 1 if correct else 0,
        "max_points": 1
    }
    if correct:
        results["points"] += 1
    
    return results

def evaluate_submission(candidate, answer_key):
    """Evaluate the entire submission."""
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "task1": evaluate_task1(candidate, answer_key),
        "task2": evaluate_task2(candidate, answer_key),
        "task3": evaluate_task3(candidate, answer_key),
    }
    
    # Calculate total points and overall score
    total_points = sum(results[task]["points"] for task in ["task1", "task2", "task3"])
    max_points = sum(results[task]["max_points"] for task in ["task1", "task2", "task3"])
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["overall_score"] = round(total_points / max_points * 100, 2)
    
    # Determine if the candidate passed
    min_passing_score = 24  # 80% of 30 points
    min_points_per_task = 7
    task1_passed = results["task1"]["points"] >= min_points_per_task
    task2_passed = results["task2"]["points"] >= 7  # Task 2 has 10 points, so need 7
    task3_passed = results["task3"]["points"] >= 7  # Task 3 has 8 points, so need 7
    
    results["passed"] = (total_points >= min_passing_score and 
                         task1_passed and task2_passed and task3_passed)
    
    results["passing_criteria"] = {
        "minimum_total_points": min_passing_score,
        "minimum_points_per_task": min_points_per_task,
        "task1_minimum_met": task1_passed,
        "task2_minimum_met": task2_passed,
        "task3_minimum_met": task3_passed
    }
    
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
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()