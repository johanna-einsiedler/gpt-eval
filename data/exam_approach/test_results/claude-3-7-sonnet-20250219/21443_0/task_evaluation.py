#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_true_false_section(submission: Dict[str, bool], answer_key: Dict[str, bool]) -> Tuple[int, int]:
    """Evaluate a section with true/false answers."""
    correct = 0
    total = len(answer_key)
    
    for key, expected in answer_key.items():
        if key in submission and submission[key] == expected:
            correct += 1
    
    return correct, total

def evaluate_numerical_values(submission: Dict[str, float], answer_key: Dict[str, float]) -> Tuple[int, int]:
    """Evaluate numerical values with 5% tolerance."""
    correct = 0
    total = len(answer_key) * 2  # Each numerical value is worth 2 points
    
    for key, expected in answer_key.items():
        if key in submission:
            # Accept answers within ±5% of the correct values
            tolerance = 0.05 * expected
            if abs(submission[key] - expected) <= tolerance:
                correct += 2
    
    return correct, total

def evaluate_multiple_choice(submission: Dict[str, str], answer_key: Dict[str, str]) -> Tuple[int, int]:
    """Evaluate multiple choice answers."""
    correct = 0
    total = len(answer_key) * 2  # Each multiple choice is worth 2 points
    
    for key, expected in answer_key.items():
        if key in submission and submission[key] == expected:
            correct += 2
    
    return correct, total

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "section_scores": {},
        "task_scores": {},
        "critical_elements": {},
        "points_earned": 0,
        "points_possible": 30,
        "overall_score": 0.0,
        "passed": False
    }
    
    # Section 1
    section1_points = 0
    
    # Task 1.1: Document Review Checklist (8 true/false items, 1 point each)
    task1_1_correct, task1_1_total = evaluate_true_false_section(
        submission["section1"]["task1_1"], 
        answer_key["section1"]["task1_1"]
    )
    section1_points += task1_1_correct
    results["task_scores"]["task1_1"] = {
        "points_earned": task1_1_correct,
        "points_possible": task1_1_total
    }
    
    # Task 1.2: Settlement Value Calculation (2 numerical values, 2 points each)
    task1_2_correct, task1_2_total = evaluate_numerical_values(
        submission["section1"]["task1_2"], 
        answer_key["section1"]["task1_2"]
    )
    section1_points += task1_2_correct
    results["task_scores"]["task1_2"] = {
        "points_earned": task1_2_correct,
        "points_possible": task1_2_total
    }
    
    # Task 1.3: Authority Verification (1 multiple choice, 2 points)
    task1_3_correct = 0
    if submission["section1"]["task1_3"]["authority_action"] == answer_key["section1"]["task1_3"]["authority_action"]:
        task1_3_correct = 2
    section1_points += task1_3_correct
    results["task_scores"]["task1_3"] = {
        "points_earned": task1_3_correct,
        "points_possible": 2
    }
    
    # Critical element check for Task 1.3
    results["critical_elements"]["task1_3"] = (task1_3_correct == 2)
    
    results["section_scores"]["section1"] = {
        "points_earned": section1_points,
        "points_possible": 12
    }
    
    # Section 2
    section2_points = 0
    
    # Task 2.1: Opening Position (1 multiple choice, 2 points)
    task2_1_correct = 0
    if submission["section2"]["task2_1"]["opening_offer"] == answer_key["section2"]["task2_1"]["opening_offer"]:
        task2_1_correct = 2
    section2_points += task2_1_correct
    results["task_scores"]["task2_1"] = {
        "points_earned": task2_1_correct,
        "points_possible": 2
    }
    
    # Task 2.2: Response to Arguments (1 multiple choice, 2 points)
    task2_2_correct = 0
    if submission["section2"]["task2_2"]["response_to_future_treatment"] == answer_key["section2"]["task2_2"]["response_to_future_treatment"]:
        task2_2_correct = 2
    section2_points += task2_2_correct
    results["task_scores"]["task2_2"] = {
        "points_earned": task2_2_correct,
        "points_possible": 2
    }
    
    # Task 2.3: Negotiation Strategy (1 multiple choice, 2 points)
    task2_3_correct = 0
    if submission["section2"]["task2_3"]["negotiation_strategy"] == answer_key["section2"]["task2_3"]["negotiation_strategy"]:
        task2_3_correct = 2
    section2_points += task2_3_correct
    results["task_scores"]["task2_3"] = {
        "points_earned": task2_3_correct,
        "points_possible": 2
    }
    
    results["section_scores"]["section2"] = {
        "points_earned": section2_points,
        "points_possible": 6
    }
    
    # Section 3
    section3_points = 0
    
    # Task 3.1: Settlement Documentation (7 true/false items, 1 point each)
    task3_1_correct, task3_1_total = evaluate_true_false_section(
        submission["section3"]["task3_1"], 
        answer_key["section3"]["task3_1"]
    )
    section3_points += task3_1_correct
    results["task_scores"]["task3_1"] = {
        "points_earned": task3_1_correct,
        "points_possible": task3_1_total
    }
    
    # Task 3.2: Claim Outcome Coding (1 multiple choice, 2 points)
    task3_2_correct = 0
    if submission["section3"]["task3_2"]["claim_outcome_code"] == answer_key["section3"]["task3_2"]["claim_outcome_code"]:
        task3_2_correct = 2
    section3_points += task3_2_correct
    results["task_scores"]["task3_2"] = {
        "points_earned": task3_2_correct,
        "points_possible": 2
    }
    
    # Task 3.3: Authority Compliance (1 multiple choice, 2 points)
    task3_3_correct = 0
    if submission["section3"]["task3_3"]["authority_compliance"] == answer_key["section3"]["task3_3"]["authority_compliance"]:
        task3_3_correct = 2
    section3_points += task3_3_correct
    results["task_scores"]["task3_3"] = {
        "points_earned": task3_3_correct,
        "points_possible": 2
    }
    
    # Critical element check for Task 3.3
    results["critical_elements"]["task3_3"] = (task3_3_correct == 2)
    
    results["section_scores"]["section3"] = {
        "points_earned": section3_points,
        "points_possible": 12
    }
    
    # Calculate total points earned
    total_points_earned = section1_points + section2_points + section3_points
    results["points_earned"] = total_points_earned
    
    # Calculate overall score as a percentage
    results["overall_score"] = (total_points_earned / results["points_possible"]) * 100
    
    # Determine if the candidate passed
    # Passing criteria: 80% overall score (24/30 points) and all critical elements correct
    all_critical_correct = all(results["critical_elements"].values())
    results["passed"] = (results["overall_score"] >= 80) and all_critical_correct
    
    # Add candidate ID if available
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
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
    
    # Save results to test_results.json
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()