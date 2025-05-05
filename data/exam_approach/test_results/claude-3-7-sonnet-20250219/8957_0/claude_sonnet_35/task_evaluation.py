#!/usr/bin/env python3
"""
Evaluator script for Data Preparation Exam
Usage: python task_evaluation.py test_submission.json answer_key.json
"""

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


def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 1: Data Cleaning and Organization."""
    results = {
        "record_count": {
            "points_earned": 0,
            "points_possible": 5,
            "correct": False,
            "submitted_value": submission.get("record_count"),
            "expected_value": answer_key.get("record_count")
        },
        "missing_values_count": {
            "points_earned": 0,
            "points_possible": 5,
            "correct": False,
            "submitted_value": submission.get("missing_values_count"),
            "expected_value": answer_key.get("missing_values_count")
        },
        "duplicate_records_removed": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("duplicate_records_removed"),
            "expected_value": answer_key.get("duplicate_records_removed")
        },
        "outliers_identified": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("outliers_identified", []),
            "expected_value": answer_key.get("outliers_identified", []),
            "details": "0 out of 5 outliers correctly identified"
        }
    }
    
    # Record count
    if submission.get("record_count") == answer_key.get("record_count"):
        results["record_count"]["points_earned"] = 5
        results["record_count"]["correct"] = True
    
    # Missing values count
    if submission.get("missing_values_count") == answer_key.get("missing_values_count"):
        results["missing_values_count"]["points_earned"] = 5
        results["missing_values_count"]["correct"] = True
    
    # Duplicate records removed
    if submission.get("duplicate_records_removed") == answer_key.get("duplicate_records_removed"):
        results["duplicate_records_removed"]["points_earned"] = 10
        results["duplicate_records_removed"]["correct"] = True
    
    # Outliers identified
    submitted_outliers = set(submission.get("outliers_identified", []))
    expected_outliers = set(answer_key.get("outliers_identified", []))
    
    correct_outliers = submitted_outliers.intersection(expected_outliers)
    num_correct = len(correct_outliers)
    
    # 2 points per correct outlier
    results["outliers_identified"]["points_earned"] = min(num_correct * 2, 10)
    results["outliers_identified"]["details"] = f"{num_correct} out of {len(expected_outliers)} outliers correctly identified"
    
    if submitted_outliers == expected_outliers:
        results["outliers_identified"]["correct"] = True
    
    # Calculate total points for Task 1
    total_earned = sum(item["points_earned"] for item in results.values())
    total_possible = sum(item["points_possible"] for item in results.values())
    
    return {
        "details": results,
        "points_earned": total_earned,
        "points_possible": total_possible,
        "requirements_met": (
            results["record_count"]["correct"] +
            results["missing_values_count"]["correct"] +
            results["duplicate_records_removed"]["correct"] +
            (num_correct >= 3)  # At least 3 outliers identified
        ) >= 3  # At least 3 out of 4 correct
    }


def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 2: Data Quality Assessment."""
    results = {
        "inconsistent_entries": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("inconsistent_entries", []),
            "expected_value": answer_key.get("inconsistent_entries", [])
        },
        "corrected_values": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("corrected_values", {}),
            "expected_value": answer_key.get("corrected_values", {})
        },
        "data_validation_rules": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("data_validation_rules", []),
            "expected_value": answer_key.get("data_validation_rules", []),
            "details": "0 valid rules provided"
        }
    }
    
    # Inconsistent entries
    # Check if the candidate identified the negative age value
    submitted_inconsistencies = submission.get("inconsistent_entries", [])
    expected_inconsistencies = answer_key.get("inconsistent_entries", [])
    
    # Check if the candidate identified the key inconsistency (row_id 1006, field age, value -5)
    identified_key_inconsistency = False
    for entry in submitted_inconsistencies:
        if (entry.get("row_id") == "1006" and 
            entry.get("field") == "age" and 
            entry.get("value") == "-5"):
            identified_key_inconsistency = True
            break
    
    if identified_key_inconsistency:
        results["inconsistent_entries"]["points_earned"] = 10
        results["inconsistent_entries"]["correct"] = True
    
    # Corrected values
    submitted_corrections = submission.get("corrected_values", {})
    expected_corrections = answer_key.get("corrected_values", {})
    
    # Check if the candidate correctly fixed the age value for row 1006
    if "1006" in submitted_corrections and "age" in submitted_corrections.get("1006", {}):
        if submitted_corrections["1006"]["age"] == expected_corrections["1006"]["age"]:
            results["corrected_values"]["points_earned"] = 10
            results["corrected_values"]["correct"] = True
    
    # Data validation rules
    submitted_rules = submission.get("data_validation_rules", [])
    
    # Count valid rules (looking for rules about age, education, and income)
    valid_rules = 0
    rule_keywords = {
        "age": ["age", "18", "100"],
        "education": ["education", "high school", "associate", "bachelor", "master", "doctorate"],
        "income": ["income", "positive", "500000"]
    }
    
    rule_matches = {"age": False, "education": False, "income": False}
    
    for rule in submitted_rules:
        rule_lower = rule.lower()
        for category, keywords in rule_keywords.items():
            if not rule_matches[category] and any(keyword.lower() in rule_lower for keyword in keywords):
                rule_matches[category] = True
                valid_rules += 1
                break
    
    # Award points based on number of valid rules (max 10 points)
    points_per_rule = 10 / 3  # 3-4 points per valid rule
    results["data_validation_rules"]["points_earned"] = min(round(valid_rules * points_per_rule), 10)
    results["data_validation_rules"]["details"] = f"{valid_rules} valid rules provided"
    
    if valid_rules >= 3:
        results["data_validation_rules"]["correct"] = True
    
    # Calculate total points for Task 2
    total_earned = sum(item["points_earned"] for item in results.values())
    total_possible = sum(item["points_possible"] for item in results.values())
    
    return {
        "details": results,
        "points_earned": total_earned,
        "points_possible": total_possible,
        "requirements_met": (
            results["inconsistent_entries"]["correct"] +
            results["corrected_values"]["correct"] +
            (valid_rules >= 2)  # At least 2 reasonable validation rules
        ) >= 2  # At least 2 out of 3 correct components
    }


def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 3: Data Weighting."""
    results = {
        "weighted_average_income": {
            "points_earned": 0,
            "points_possible": 15,
            "correct": False,
            "submitted_value": submission.get("weighted_average_income"),
            "expected_value": answer_key.get("weighted_average_income"),
            "details": "Outside acceptable range"
        },
        "weighted_proportion_category_a": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("weighted_proportion_category_a"),
            "expected_value": answer_key.get("weighted_proportion_category_a"),
            "details": "Outside acceptable range"
        },
        "post_stratification_weights": {
            "points_earned": 0,
            "points_possible": 5,
            "correct": False,
            "submitted_value": submission.get("post_stratification_weights", []),
            "expected_value": answer_key.get("post_stratification_weights", [])
        },
        "effective_sample_size": {
            "points_earned": 0,
            "points_possible": 10,
            "correct": False,
            "submitted_value": submission.get("effective_sample_size"),
            "expected_value": answer_key.get("effective_sample_size"),
            "details": "Outside acceptable range"
        }
    }
    
    # Weighted average income (within ±5% of correct value)
    submitted_income = submission.get("weighted_average_income")
    expected_income = answer_key.get("weighted_average_income")
    
    if submitted_income is not None and expected_income is not None:
        tolerance = 0.05 * expected_income
        if abs(submitted_income - expected_income) <= tolerance:
            results["weighted_average_income"]["points_earned"] = 15
            results["weighted_average_income"]["correct"] = True
            results["weighted_average_income"]["details"] = "Within acceptable range"
    
    # Weighted proportion (within ±0.05 of correct value)
    submitted_proportion = submission.get("weighted_proportion_category_a")
    expected_proportion = answer_key.get("weighted_proportion_category_a")
    
    if submitted_proportion is not None and expected_proportion is not None:
        if abs(submitted_proportion - expected_proportion) <= 0.05:
            results["weighted_proportion_category_a"]["points_earned"] = 10
            results["weighted_proportion_category_a"]["correct"] = True
            results["weighted_proportion_category_a"]["details"] = "Within acceptable range"
    
    # Post-stratification weights
    submitted_weights = submission.get("post_stratification_weights", [])
    expected_weights = answer_key.get("post_stratification_weights", [])
    
    # Check if the first 5 weights are reasonable
    if len(submitted_weights) >= 5 and len(expected_weights) >= 5:
        # Allow some tolerance in the weights
        all_reasonable = True
        for i in range(5):
            if abs(submitted_weights[i] - expected_weights[i]) > 0.2:  # 20% tolerance
                all_reasonable = False
                break
        
        if all_reasonable:
            results["post_stratification_weights"]["points_earned"] = 5
            results["post_stratification_weights"]["correct"] = True
    
    # Effective sample size
    submitted_ess = submission.get("effective_sample_size")
    expected_ess = answer_key.get("effective_sample_size")
    
    if submitted_ess is not None and expected_ess is not None:
        # Allow 10% tolerance for effective sample size
        tolerance = 0.1 * expected_ess
        if abs(submitted_ess - expected_ess) <= tolerance:
            results["effective_sample_size"]["points_earned"] = 10
            results["effective_sample_size"]["correct"] = True
            results["effective_sample_size"]["details"] = "Within acceptable range"
    
    # Calculate total points for Task 3
    total_earned = sum(item["points_earned"] for item in results.values())
    total_possible = sum(item["points_possible"] for item in results.values())
    
    return {
        "details": results,
        "points_earned": total_earned,
        "points_possible": total_possible,
        "requirements_met": (
            results["weighted_average_income"]["correct"] +
            results["weighted_proportion_category_a"]["correct"] +
            results["post_stratification_weights"]["correct"] +
            results["effective_sample_size"]["correct"]
        ) >= 2  # At least 2 out of 4 correct calculations
    }


def evaluate_submission(submission_file: str, answer_key_file: str) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Extract candidate ID
    candidate_id = submission.get("candidate_id", "Unknown")
    
    # Evaluate each task
    task1_results = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    task2_results = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    task3_results = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    
    # Calculate overall score
    total_earned = task1_results["points_earned"] + task2_results["points_earned"] + task3_results["points_earned"]
    total_possible = task1_results["points_possible"] + task2_results["points_possible"] + task3_results["points_possible"]
    overall_score = (total_earned / total_possible) * 100 if total_possible > 0 else 0
    
    # Determine if candidate passed
    requirements_met_count = task1_results["requirements_met"] + task2_results["requirements_met"] + task3_results["requirements_met"]
    passed = requirements_met_count >= 2 and overall_score >= 70
    
    return {
        "candidate_id": candidate_id,
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "overall_score": round(overall_score, 2),
        "total_points_earned": total_earned,
        "total_points_possible": total_possible,
        "requirements_met": requirements_met_count,
        "passed": passed
    }


def main():
    """Main function to run the evaluation."""
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
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()