#!/usr/bin/env python3
import json
import sys
import math
import numpy as np

def load_json(filename):
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Correlation Analysis."""
    results = {
        "score": 0,
        "max_score": 100,
        "details": {}
    }
    
    # Check correlation coefficients
    sub_corr = submission.get("correlation_coefficients", {})
    key_corr = answer_key.get("correlation_coefficients", {})
    
    correct_coeffs = 0
    total_coeffs = len(key_corr)
    
    results["details"]["correlation_coefficients"] = {
        "correct": 0,
        "total": total_coeffs,
        "errors": []
    }
    
    for pair, key_value in key_corr.items():
        if pair in sub_corr:
            sub_value = sub_corr[pair]
            if abs(sub_value - key_value) <= 0.05:
                correct_coeffs += 1
            else:
                results["details"]["correlation_coefficients"]["errors"].append({
                    "pair": pair,
                    "submitted": sub_value,
                    "expected": key_value
                })
    
    results["details"]["correlation_coefficients"]["correct"] = correct_coeffs
    corr_score = (correct_coeffs / total_coeffs) * 50 if total_coeffs > 0 else 0
    
    # Check strongest relationship
    sub_strongest = submission.get("strongest_relationship", "")
    key_strongest = answer_key.get("strongest_relationship", "")
    alt_strongest = "age_cholesterol"  # Alternative acceptable answer
    
    strongest_correct = (sub_strongest == key_strongest) or (sub_strongest == alt_strongest)
    results["details"]["strongest_relationship"] = {
        "correct": strongest_correct,
        "submitted": sub_strongest,
        "expected": key_strongest,
        "alternative_acceptable": alt_strongest
    }
    
    strongest_score = 25 if strongest_correct else 0
    
    # Check relationship direction
    sub_direction = submission.get("relationship_direction", "")
    key_direction = answer_key.get("relationship_direction", "")
    
    direction_correct = (sub_direction == key_direction)
    results["details"]["relationship_direction"] = {
        "correct": direction_correct,
        "submitted": sub_direction,
        "expected": key_direction
    }
    
    direction_score = 25 if direction_correct else 0
    
    # Calculate total score for Task 1
    results["score"] = corr_score + strongest_score + direction_score
    
    # Check if task passes
    corr_percentage = (correct_coeffs / total_coeffs) if total_coeffs > 0 else 0
    results["passes"] = (corr_percentage >= 0.75 and strongest_correct and direction_correct)
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Time Series Trend Analysis."""
    results = {
        "score": 0,
        "max_score": 100,
        "details": {}
    }
    
    # Check overall trend
    sub_trend = submission.get("overall_trend", "")
    key_trend = answer_key.get("overall_trend", "")
    
    trend_correct = (sub_trend == key_trend)
    results["details"]["overall_trend"] = {
        "correct": trend_correct,
        "submitted": sub_trend,
        "expected": key_trend
    }
    
    trend_score = 20 if trend_correct else 0
    
    # Check trend magnitude
    sub_magnitude = submission.get("trend_magnitude", 0)
    key_magnitude = answer_key.get("trend_magnitude", 0)
    
    magnitude_correct = abs(sub_magnitude - key_magnitude) <= 500
    results["details"]["trend_magnitude"] = {
        "correct": magnitude_correct,
        "submitted": sub_magnitude,
        "expected": key_magnitude,
        "tolerance": 500
    }
    
    magnitude_score = 20 if magnitude_correct else 0
    
    # Check seasonal pattern
    sub_seasonal = submission.get("seasonal_pattern", False)
    key_seasonal = answer_key.get("seasonal_pattern", False)
    
    seasonal_correct = (sub_seasonal == key_seasonal)
    results["details"]["seasonal_pattern"] = {
        "correct": seasonal_correct,
        "submitted": sub_seasonal,
        "expected": key_seasonal
    }
    
    seasonal_score = 20 if seasonal_correct else 0
    
    # Check peak month
    sub_peak = submission.get("peak_month", "")
    key_peak = answer_key.get("peak_month", "")
    
    peak_correct = (sub_peak == key_peak)
    results["details"]["peak_month"] = {
        "correct": peak_correct,
        "submitted": sub_peak,
        "expected": key_peak
    }
    
    peak_score = 20 if peak_correct else 0
    
    # Check trough month
    sub_trough = submission.get("trough_month", "")
    key_trough = answer_key.get("trough_month", "")
    
    trough_correct = (sub_trough == key_trough)
    results["details"]["trough_month"] = {
        "correct": trough_correct,
        "submitted": sub_trough,
        "expected": key_trough
    }
    
    trough_score = 20 if trough_correct else 0
    
    # Calculate total score for Task 2
    results["score"] = trend_score + magnitude_score + seasonal_score + peak_score + trough_score
    
    # Check if task passes
    results["passes"] = (trend_correct and magnitude_correct and seasonal_correct and 
                         peak_correct and trough_correct)
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Confounding Variable Identification."""
    results = {
        "score": 0,
        "max_score": 100,
        "details": {}
    }
    
    # Check primary predictor
    sub_predictor = submission.get("primary_predictor", "")
    key_predictor = answer_key.get("primary_predictor", "")
    
    predictor_correct = (sub_predictor == key_predictor)
    results["details"]["primary_predictor"] = {
        "correct": predictor_correct,
        "submitted": sub_predictor,
        "expected": key_predictor
    }
    
    predictor_score = 25 if predictor_correct else 0
    
    # Check confounding variable
    sub_confounder = submission.get("confounding_variable", "")
    key_confounder = answer_key.get("confounding_variable", "")
    alt_confounder = "socioeconomic_status"  # Alternative acceptable answer
    
    confounder_correct = (sub_confounder == key_confounder)
    confounder_acceptable = (sub_confounder == alt_confounder)
    
    results["details"]["confounding_variable"] = {
        "correct": confounder_correct,
        "acceptable_alternative": confounder_acceptable,
        "submitted": sub_confounder,
        "expected": key_confounder,
        "alternative_acceptable": alt_confounder
    }
    
    confounder_score = 25 if confounder_correct else (15 if confounder_acceptable else 0)
    
    # Check unadjusted relationship
    sub_unadjusted = submission.get("unadjusted_relationship", 0)
    key_unadjusted = answer_key.get("unadjusted_relationship", 0)
    
    unadjusted_correct = abs(sub_unadjusted - key_unadjusted) <= 0.10
    results["details"]["unadjusted_relationship"] = {
        "correct": unadjusted_correct,
        "submitted": sub_unadjusted,
        "expected": key_unadjusted,
        "tolerance": 0.10
    }
    
    unadjusted_score = 25 if unadjusted_correct else 0
    
    # Check adjusted relationship
    sub_adjusted = submission.get("adjusted_relationship", 0)
    key_adjusted = answer_key.get("adjusted_relationship", 0)
    
    adjusted_correct = abs(sub_adjusted - key_adjusted) <= 0.10
    results["details"]["adjusted_relationship"] = {
        "correct": adjusted_correct,
        "submitted": sub_adjusted,
        "expected": key_adjusted,
        "tolerance": 0.10
    }
    
    adjusted_score = 25 if adjusted_correct else 0
    
    # Calculate total score for Task 3
    results["score"] = predictor_score + confounder_score + unadjusted_score + adjusted_score
    
    # Check if task passes
    results["passes"] = (predictor_correct and 
                        (confounder_correct or confounder_acceptable) and
                        unadjusted_correct and adjusted_correct)
    
    # Check if task is partially correct (primary predictor identified)
    results["partially_correct"] = predictor_correct
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "task1": evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {})),
        "task2": evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {})),
        "task3": evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    }
    
    # Calculate overall score
    total_score = (results["task1"]["score"] + results["task2"]["score"] + results["task3"]["score"]) / 3
    results["overall_score"] = round(total_score, 2)
    
    # Determine if the candidate passes
    tasks_passed = sum([results[task]["passes"] for task in ["task1", "task2", "task3"]])
    task3_partially_correct = results["task3"]["partially_correct"]
    
    results["passes_exam"] = (tasks_passed >= 2 and task3_partially_correct)
    
    # Add candidate ID if available
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
    return results

def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Candidate passes: {results['passes_exam']}")

if __name__ == "__main__":
    main()