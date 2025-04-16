#!/usr/bin/env python3
"""
Evaluation script for the Purchasing Agent practical exam.
This script compares a candidate's submission against an answer key
and generates a detailed score report.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, Any


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def is_close_enough(candidate_value: float, answer_value: float, tolerance: float = 0.01) -> bool:
    """Check if candidate's numerical answer is within tolerance of correct answer."""
    if math.isclose(candidate_value, answer_value, rel_tol=tolerance):
        return True
    return False


def evaluate_scenario(candidate_scenario: Dict[str, Any], 
                     answer_scenario: Dict[str, Any],
                     scenario_name: str) -> Dict[str, Any]:
    """Evaluate a single scenario and return detailed results."""
    
    results = {
        "items": {},
        "points_earned": 0,
        "points_possible": len(answer_scenario) * 4,
        "percentage": 0
    }
    
    for key, correct_value in answer_scenario.items():
        # Initialize result for this item
        results["items"][key] = {
            "candidate_answer": candidate_scenario.get(key),
            "correct_answer": correct_value,
            "points_earned": 0,
            "points_possible": 4,
            "is_correct": False,
            "notes": ""
        }
        
        # Get candidate's answer (default to None if missing)
        candidate_answer = candidate_scenario.get(key)
        if candidate_answer is None:
            results["items"][key]["notes"] = "Missing answer"
            continue
            
        # Handle different types of questions
        if isinstance(correct_value, (int, float)) and isinstance(candidate_answer, (int, float)):
            # Numeric value comparison (monetary values)
            if candidate_answer == correct_value:
                results["items"][key]["points_earned"] = 4
                results["items"][key]["is_correct"] = True
            elif is_close_enough(candidate_answer, correct_value):
                results["items"][key]["points_earned"] = 2
                results["items"][key]["notes"] = "Within 1% of correct answer"
            else:
                results["items"][key]["notes"] = "Incorrect calculation"
                
        elif isinstance(correct_value, str) and isinstance(candidate_answer, str):
            # Multiple choice answers
            if candidate_answer.upper() == correct_value.upper():
                results["items"][key]["points_earned"] = 4
                results["items"][key]["is_correct"] = True
            else:
                results["items"][key]["notes"] = "Incorrect selection"
        else:
            results["items"][key]["notes"] = "Invalid answer format"
    
    # Calculate total points earned for this scenario
    results["points_earned"] = sum(item["points_earned"] for item in results["items"].values())
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    
    return results


def evaluate_submission(candidate_submission: Dict[str, Any], 
                        answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    
    results = {
        "candidate_id": candidate_submission.get("candidate_id", "UNKNOWN"),
        "scenarios": {},
        "overall_points_earned": 0,
        "overall_points_possible": 0,
        "overall_score": 0,
        "passed": False
    }
    
    # Evaluate each scenario
    for scenario in ["scenario_1", "scenario_2", "scenario_3"]:
        if scenario not in candidate_submission or scenario not in answer_key:
            results["scenarios"][scenario] = {"error": f"Missing {scenario} data"}
            continue
            
        results["scenarios"][scenario] = evaluate_scenario(
            candidate_submission[scenario],
            answer_key[scenario],
            scenario
        )
        
        results["overall_points_earned"] += results["scenarios"][scenario]["points_earned"]
        results["overall_points_possible"] += results["scenarios"][scenario]["points_possible"]
    
    # Calculate overall score as a percentage
    if results["overall_points_possible"] > 0:
        results["overall_score"] = (results["overall_points_earned"] / results["overall_points_possible"]) * 100
    
    # Determine if candidate passed (75% overall and at least 60% in each scenario)
    scenario_pass = all(
        results["scenarios"].get(scenario, {}).get("percentage", 0) >= 60
        for scenario in ["scenario_1", "scenario_2", "scenario_3"]
    )
    overall_pass = results["overall_score"] >= 75
    
    results["passed"] = scenario_pass and overall_pass
    
    return results


def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    # Load files
    candidate_submission = load_json_file(sys.argv[1])
    answer_key = load_json_file(sys.argv[2])
    
    # Evaluate submission
    results = evaluate_submission(candidate_submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed: {results['passed']}")


if __name__ == "__main__":
    main()