#!/usr/bin/env python3
import json
import sys
import math

def evaluate_submission(submission_file, answer_key_file):
    # Load submission and answer key
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    
    # Initialize results structure
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": {"score": 0, "max_score": 4, "details": {}},
        "task2": {"score": 0, "max_score": 4, "details": {}},
        "task3": {"score": 0, "max_score": 4, "details": {}},
        "overall_score": 0,
        "passed": False,
        "critical_errors": []
    }
    
    # Evaluate Task 1
    task1_submission = submission.get("task1", {})
    task1_key = answer_key.get("task1", {})
    
    # Design choice
    design_choice = task1_submission.get("design_choice", "")
    correct_design = task1_key.get("design_choice", "")
    design_correct = design_choice == correct_design
    results["task1"]["details"]["design_choice"] = {
        "submitted": design_choice,
        "correct": correct_design,
        "points": 1 if design_correct else 0
    }
    results["task1"]["score"] += results["task1"]["details"]["design_choice"]["points"]
    
    if not design_correct:
        results["critical_errors"].append("Selected inappropriate research design")
    
    # Sample size
    sample_size = task1_submission.get("sample_size", 0)
    correct_sample_size = task1_key.get("sample_size", 0)
    sample_size_correct = abs(sample_size - correct_sample_size) <= 5
    results["task1"]["details"]["sample_size"] = {
        "submitted": sample_size,
        "correct": correct_sample_size,
        "points": 1 if sample_size_correct else 0
    }
    results["task1"]["score"] += results["task1"]["details"]["sample_size"]["points"]
    
    if sample_size < 40:
        results["critical_errors"].append("Calculated severely underpowered sample size")
    
    # Stratification variables
    strat_vars = set(task1_submission.get("stratification_variables", []))
    correct_strat_vars = set(task1_key.get("stratification_variables", []))
    strat_vars_correct = strat_vars == correct_strat_vars
    results["task1"]["details"]["stratification_variables"] = {
        "submitted": list(strat_vars),
        "correct": list(correct_strat_vars),
        "points": 1 if strat_vars_correct else 0
    }
    results["task1"]["score"] += results["task1"]["details"]["stratification_variables"]["points"]
    
    if "age" not in strat_vars:
        results["critical_errors"].append("Failed to identify age as important for stratification")
    
    # Effect size
    effect_size = task1_submission.get("expected_effect_size", 0)
    correct_effect_size = task1_key.get("expected_effect_size", 0)
    effect_size_correct = abs(effect_size - correct_effect_size) <= 0.05
    results["task1"]["details"]["expected_effect_size"] = {
        "submitted": effect_size,
        "correct": correct_effect_size,
        "points": 1 if effect_size_correct else 0
    }
    results["task1"]["score"] += results["task1"]["details"]["expected_effect_size"]["points"]
    
    # Evaluate Task 2
    task2_submission = submission.get("task2", {})
    task2_key = answer_key.get("task2", {})
    
    # Minimum sample size
    min_sample_size = task2_submission.get("minimum_sample_size", 0)
    correct_min_sample_size = task2_key.get("minimum_sample_size", 0)
    min_sample_size_correct = abs(min_sample_size - correct_min_sample_size) <= 5
    results["task2"]["details"]["minimum_sample_size"] = {
        "submitted": min_sample_size,
        "correct": correct_min_sample_size,
        "points": 1 if min_sample_size_correct else 0
    }
    results["task2"]["score"] += results["task2"]["details"]["minimum_sample_size"]["points"]
    
    # Power at sample sizes
    submitted_power = task2_submission.get("power_at_sample_sizes", [])
    correct_power = task2_key.get("power_at_sample_sizes", [])
    
    power_points = 0
    power_details = []
    
    # Check if the arrays have the same length
    if len(submitted_power) == len(correct_power):
        for i, (submitted, correct) in enumerate(zip(submitted_power, correct_power)):
            submitted_sample = submitted.get("sample_size", 0)
            correct_sample = correct.get("sample_size", 0)
            submitted_power_val = submitted.get("power", 0)
            correct_power_val = correct.get("power", 0)
            
            sample_match = submitted_sample == correct_sample
            power_match = abs(submitted_power_val - correct_power_val) <= 0.02
            
            if sample_match and power_match:
                power_points += 1
            
            power_details.append({
                "sample_size": {
                    "submitted": submitted_sample,
                    "correct": correct_sample,
                    "matches": sample_match
                },
                "power": {
                    "submitted": submitted_power_val,
                    "correct": correct_power_val,
                    "matches": power_match
                }
            })
    
    # Award up to 2 points for power calculations (1 point for each correct calculation)
    power_points = min(2, power_points)
    results["task2"]["details"]["power_at_sample_sizes"] = {
        "details": power_details,
        "points": power_points
    }
    results["task2"]["score"] += power_points
    
    # Optimal allocation ratio
    allocation_ratio = task2_submission.get("optimal_allocation_ratio", "")
    correct_allocation_ratio = task2_key.get("optimal_allocation_ratio", "")
    allocation_ratio_correct = allocation_ratio == correct_allocation_ratio
    results["task2"]["details"]["optimal_allocation_ratio"] = {
        "submitted": allocation_ratio,
        "correct": correct_allocation_ratio,
        "points": 1 if allocation_ratio_correct else 0
    }
    results["task2"]["score"] += results["task2"]["details"]["optimal_allocation_ratio"]["points"]
    
    # Evaluate Task 3
    task3_submission = submission.get("task3", {})
    task3_key = answer_key.get("task3", {})
    
    # Control group mean
    control_mean = task3_submission.get("control_group_mean", 0)
    correct_control_mean = task3_key.get("control_group_mean", 0)
    control_mean_correct = abs(control_mean - correct_control_mean) <= 1
    results["task3"]["details"]["control_group_mean"] = {
        "submitted": control_mean,
        "correct": correct_control_mean,
        "points": 1 if control_mean_correct else 0
    }
    results["task3"]["score"] += results["task3"]["details"]["control_group_mean"]["points"]
    
    # Treatment effect estimate
    treatment_effect = task3_submission.get("treatment_effect_estimate", 0)
    correct_treatment_effect = task3_key.get("treatment_effect_estimate", 0)
    treatment_effect_correct = abs(treatment_effect - correct_treatment_effect) <= 1
    results["task3"]["details"]["treatment_effect_estimate"] = {
        "submitted": treatment_effect,
        "correct": correct_treatment_effect,
        "points": 1 if treatment_effect_correct else 0
    }
    results["task3"]["score"] += results["task3"]["details"]["treatment_effect_estimate"]["points"]
    
    # Confounders identified
    confounders = set(task3_submission.get("confounders_identified", []))
    correct_confounders = set(task3_key.get("confounders_identified", []))
    
    # Special case: "bmi" is acceptable as an alternative to "diabetes"
    alternative_correct_confounders = correct_confounders.copy()
    if "diabetes" in alternative_correct_confounders:
        alternative_correct_confounders.remove("diabetes")
        alternative_correct_confounders.add("bmi")
    
    confounders_correct = (confounders == correct_confounders or 
                           confounders == alternative_correct_confounders)
    
    results["task3"]["details"]["confounders_identified"] = {
        "submitted": list(confounders),
        "correct": list(correct_confounders),
        "alternative_correct": list(alternative_correct_confounders) if "diabetes" in correct_confounders else None,
        "points": 1 if confounders_correct else 0
    }
    results["task3"]["score"] += results["task3"]["details"]["confounders_identified"]["points"]
    
    # Matching variables
    matching_vars = set(task3_submission.get("matching_variables", []))
    correct_matching_vars = set(task3_key.get("matching_variables", []))
    matching_vars_correct = matching_vars == correct_matching_vars
    results["task3"]["details"]["matching_variables"] = {
        "submitted": list(matching_vars),
        "correct": list(correct_matching_vars),
        "points": 1 if matching_vars_correct else 0
    }
    results["task3"]["score"] += results["task3"]["details"]["matching_variables"]["points"]
    
    if "age" not in matching_vars and "age" not in confounders:
        if "age" not in strat_vars:  # Only add if not already added for stratification
            results["critical_errors"].append("Failed to identify age as important variable")
    
    # Calculate overall score
    total_score = results["task1"]["score"] + results["task2"]["score"] + results["task3"]["score"]
    max_score = results["task1"]["max_score"] + results["task2"]["max_score"] + results["task3"]["max_score"]
    results["overall_score"] = round((total_score / max_score) * 100, 2)
    
    # Determine if candidate passed
    passed_overall = total_score >= 10
    passed_task1 = results["task1"]["score"] >= 3
    passed_task2 = results["task2"]["score"] >= 3
    passed_task3 = results["task3"]["score"] >= 3
    no_critical_errors = len(results["critical_errors"]) == 0
    
    results["passed"] = passed_overall and passed_task1 and passed_task2 and passed_task3 and no_critical_errors
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()