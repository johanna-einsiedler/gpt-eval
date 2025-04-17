#!/usr/bin/env python3
"""
Claims Adjusters Practical Exam Evaluator

This script evaluates a candidate's submission against an answer key for the 
Claims Adjusters, Examiners, and Investigators practical examination.

Usage:
    python task_evaluation.py test_submission.json answer_key.json

Output:
    Creates test_results.json with detailed scoring information
"""

import json
import sys


def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "exercises": {},
        "critical_errors": [],
        "passed": False
    }
    
    total_points = 0
    earned_points = 0

    # Evaluate each exercise
    exercises = ["exercise_1", "exercise_2", "exercise_3"]
    for exercise in exercises:
        if exercise not in submission or exercise not in answer_key:
            results["exercises"][exercise] = {
                "score": 0,
                "total_points": len(answer_key.get(exercise, {})),
                "errors": ["Exercise missing from submission"]
            }
            continue

        sub_ex = submission[exercise]
        key_ex = answer_key[exercise]
        
        ex_results = evaluate_exercise(exercise, sub_ex, key_ex)
        results["exercises"][exercise] = ex_results
        
        total_points += ex_results["total_points"]
        earned_points += ex_results["score"]
        
        # Check for critical errors
        if exercise == "exercise_1" and sub_ex.get("incident_covered") != key_ex.get("incident_covered"):
            results["critical_errors"].append(f"Incorrect coverage determination in {exercise}")
            
        if exercise == "exercise_2" and sub_ex.get("procedure_covered") != key_ex.get("procedure_covered"):
            results["critical_errors"].append(f"Incorrect procedure coverage determination in {exercise}")
            
        if exercise == "exercise_3":
            if sub_ex.get("coverage_applies") != key_ex.get("coverage_applies"):
                results["critical_errors"].append(f"Incorrect coverage determination in {exercise}")
            
            if sub_ex.get("potential_red_flags", 0) == 0:
                results["critical_errors"].append("Failed to identify any red flags in Exercise 3")
                
            prev_claims_diff = abs(sub_ex.get("previous_similar_claims", 0) - key_ex.get("previous_similar_claims", 0))
            if prev_claims_diff > 1:
                results["critical_errors"].append("Missed more than one previous similar claim in Exercise 3")

    # Calculate overall score
    if total_points > 0:
        results["overall_score"] = round((earned_points / total_points) * 100, 2)

    # Determine if candidate passed
    # Need at least 80% correct answers (14 out of 17) and no critical errors
    passing_score = 80.0
    results["passed"] = (results["overall_score"] >= passing_score and len(results["critical_errors"]) == 0)

    return results


def evaluate_exercise(exercise_name, submission_ex, answer_key_ex):
    """Evaluate a single exercise."""
    results = {
        "score": 0,
        "total_points": len(answer_key_ex),
        "field_results": {},
        "errors": []
    }

    for field, expected in answer_key_ex.items():
        if field not in submission_ex:
            results["errors"].append(f"Missing field: {field}")
            results["field_results"][field] = {
                "correct": False,
                "submitted": None,
                "expected": expected
            }
            continue

        submitted = submission_ex[field]
        is_correct = submitted == expected
        
        results["field_results"][field] = {
            "correct": is_correct,
            "submitted": submitted,
            "expected": expected
        }
        
        if is_correct:
            results["score"] += 1

    return results


def main():
    """Main function to process submission and generate results."""
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
    print(f"Passed: {results['passed']}")


if __name__ == "__main__":
    main()