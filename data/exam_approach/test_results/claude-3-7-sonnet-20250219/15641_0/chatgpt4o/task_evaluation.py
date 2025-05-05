#!/usr/bin/env python3
"""
Compliance Manager Practical Exam Evaluator

This script evaluates a candidate's submission against an answer key and generates
a detailed assessment with an overall score.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any, Tuple


def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_exercise1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 1: Violation Classification and Disciplinary Action."""
    results = {
        "score": 0,
        "max_score": 8,
        "details": {}
    }
    
    # Check case classifications (3 points)
    for case_num in range(1, 4):
        case_key = f"case{case_num}_classification"
        if submission["exercise1"].get(case_key) == answer_key["exercise1"].get(case_key):
            results["score"] += 1
            results["details"][case_key] = "Correct"
        else:
            results["details"][case_key] = {
                "submitted": submission["exercise1"].get(case_key),
                "expected": answer_key["exercise1"].get(case_key),
                "status": "Incorrect"
            }
    
    # Check recommended actions (3 points)
    for case_num in range(1, 4):
        action_key = f"case{case_num}_action"
        submitted_action = submission["exercise1"].get(action_key, "").strip()
        expected_action = answer_key["exercise1"].get(action_key, "").strip()
        
        # Check if the submitted action is contained within the expected action
        # This allows for partial matches as long as the key elements are present
        if submitted_action and (
            submitted_action == expected_action or 
            (len(submitted_action) > 10 and submitted_action in expected_action)
        ):
            results["score"] += 1
            results["details"][action_key] = "Correct"
        else:
            results["details"][action_key] = {
                "submitted": submitted_action,
                "expected": expected_action,
                "status": "Incorrect"
            }
    
    # Check precedent cases (2 points)
    submitted_precedents = set(submission["exercise1"].get("precedent_case_ids", []))
    valid_precedents = set(answer_key["exercise1"].get("precedent_case_ids", []))
    
    valid_submitted_precedents = submitted_precedents.intersection(valid_precedents)
    
    # Award points based on number of valid precedents (up to 2 points)
    precedent_points = min(len(valid_submitted_precedents), 2)
    results["score"] += precedent_points
    
    if precedent_points == 2:
        results["details"]["precedent_case_ids"] = "Correct"
    elif precedent_points == 1:
        results["details"]["precedent_case_ids"] = {
            "submitted": list(submitted_precedents),
            "valid_matches": list(valid_submitted_precedents),
            "expected": list(valid_precedents),
            "status": "Partially Correct"
        }
    else:
        results["details"]["precedent_case_ids"] = {
            "submitted": list(submitted_precedents),
            "expected": list(valid_precedents),
            "status": "Incorrect"
        }
    
    return results


def evaluate_exercise2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 2: Compliance-HR Workflow Development."""
    results = {
        "score": 0,
        "max_score": 15,
        "details": {}
    }
    
    # Evaluate workflow steps (8 points)
    submitted_steps = submission["exercise2"].get("workflow_steps", [])
    expected_steps = answer_key["exercise2"].get("workflow_steps", [])
    
    # Count how many expected steps are covered in the submission
    # We'll do a fuzzy match to allow for slight wording differences
    matched_steps = []
    for expected_step in expected_steps:
        for submitted_step in submitted_steps:
            # Convert to lowercase and check if the key concepts are included
            if any(key_concept.lower() in submitted_step.lower() 
                  for key_concept in expected_step.lower().split(", ")):
                matched_steps.append(expected_step)
                break
    
    # Award points based on correct steps (max 8 points)
    step_points = min(len(matched_steps), 8)
    results["score"] += step_points
    
    if step_points >= 6:  # Passing requires at least 6 steps
        status = "Correct" if step_points == 8 else "Partially Correct"
    else:
        status = "Insufficient"
        
    results["details"]["workflow_steps"] = {
        "matched_count": step_points,
        "expected_count": len(expected_steps),
        "status": status
    }
    
    # Evaluate required documentation (5 points)
    submitted_docs = [doc.lower() for doc in submission["exercise2"].get("required_documentation", [])]
    expected_docs = [doc.lower() for doc in answer_key["exercise2"].get("required_documentation", [])]
    
    # Count matches
    doc_matches = sum(1 for doc in expected_docs if any(submitted_doc in doc or doc in submitted_doc 
                                                       for submitted_doc in submitted_docs))
    
    # Award points based on correct documentation (max 5 points)
    doc_points = min(doc_matches, 5)
    results["score"] += doc_points
    
    if doc_points >= 4:  # Passing requires at least 4 documents
        status = "Correct" if doc_points == 5 else "Partially Correct"
    else:
        status = "Insufficient"
        
    results["details"]["required_documentation"] = {
        "matched_count": doc_points,
        "expected_count": len(expected_docs),
        "status": status
    }
    
    # Evaluate approval sequence (2 points)
    submitted_sequence = [role.lower() for role in submission["exercise2"].get("approval_sequence", [])]
    expected_sequence = [role.lower() for role in answer_key["exercise2"].get("approval_sequence", [])]
    
    # Check sequence order and completeness
    sequence_matches = 0
    for i, expected_role in enumerate(expected_sequence):
        if i < len(submitted_sequence) and any(expected_role in submitted_role or submitted_role in expected_role 
                                              for submitted_role in [submitted_sequence[i]]):
            sequence_matches += 1
    
    # Award points based on correct sequence (max 2 points)
    sequence_points = 2 if sequence_matches >= 4 else (1 if sequence_matches >= 2 else 0)
    results["score"] += sequence_points
    
    if sequence_points == 2:
        status = "Correct"
    elif sequence_points == 1:
        status = "Partially Correct"
    else:
        status = "Incorrect"
        
    results["details"]["approval_sequence"] = {
        "matched_count": sequence_matches,
        "expected_count": len(expected_sequence),
        "status": status
    }
    
    return results


def evaluate_exercise3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 3: Communication Protocol Development."""
    results = {
        "score": 0,
        "max_score": 7,
        "details": {}
    }
    
    # Evaluate communication template (2 points)
    submitted_template = submission["exercise3"].get("communication_template", "").strip()
    
    # Check for key elements in the template
    key_elements = [
        "COMPLIANCE VIOLATION NOTIFICATION",
        "Violation Level: 3",
        "Confidentiality Rating: Sensitive",
        "Required Stakeholders:",
        "Escalation Threshold:"
    ]
    
    template_matches = sum(1 for element in key_elements if element.lower() in submitted_template.lower())
    template_points = 2 if template_matches >= 4 else (1 if template_matches >= 2 else 0)
    results["score"] += template_points
    
    if template_points == 2:
        status = "Correct"
    elif template_points == 1:
        status = "Partially Correct"
    else:
        status = "Incorrect"
        
    results["details"]["communication_template"] = {
        "key_elements_found": template_matches,
        "expected_elements": len(key_elements),
        "status": status
    }
    
    # Evaluate escalation threshold (1 point)
    submitted_threshold = submission["exercise3"].get("escalation_threshold", "").strip()
    expected_threshold = answer_key["exercise3"].get("escalation_threshold", "").strip()
    
    if submitted_threshold.lower() == expected_threshold.lower():
        results["score"] += 1
        results["details"]["escalation_threshold"] = "Correct"
    else:
        results["details"]["escalation_threshold"] = {
            "submitted": submitted_threshold,
            "expected": expected_threshold,
            "status": "Incorrect"
        }
    
    # Evaluate confidentiality rating (1 point)
    submitted_rating = submission["exercise3"].get("confidentiality_rating", "").strip()
    expected_rating = answer_key["exercise3"].get("confidentiality_rating", "").strip()
    
    if submitted_rating.lower() == expected_rating.lower():
        results["score"] += 1
        results["details"]["confidentiality_rating"] = "Correct"
    else:
        results["details"]["confidentiality_rating"] = {
            "submitted": submitted_rating,
            "expected": expected_rating,
            "status": "Incorrect"
        }
    
    # Evaluate required stakeholders (3 points)
    submitted_stakeholders = [s.lower() for s in submission["exercise3"].get("required_stakeholders", [])]
    expected_stakeholders = [s.lower() for s in answer_key["exercise3"].get("required_stakeholders", [])]
    
    # Count matches
    stakeholder_matches = sum(1 for expected in expected_stakeholders 
                             if any(expected in submitted or submitted in expected 
                                   for submitted in submitted_stakeholders))
    
    # Award points based on correct stakeholders (max 3 points)
    stakeholder_points = min(stakeholder_matches, 3)
    results["score"] += stakeholder_points
    
    if stakeholder_points == 3:
        status = "Correct"
    elif stakeholder_points > 0:
        status = "Partially Correct"
    else:
        status = "Incorrect"
        
    results["details"]["required_stakeholders"] = {
        "matched_count": stakeholder_matches,
        "expected_count": len(expected_stakeholders),
        "status": status
    }
    
    return results


def calculate_overall_score(exercise_results: Dict) -> float:
    """Calculate the overall percentage score."""
    total_score = sum(result["score"] for result in exercise_results.values())
    max_score = sum(result["max_score"] for result in exercise_results.values())
    return round((total_score / max_score) * 100, 2)


def get_performance_rating(score: float) -> str:
    """Determine the performance rating based on the score."""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Satisfactory"
    elif score >= 60:
        return "Needs Improvement"
    else:
        return "Failing"


def main():
    """Main function to evaluate the candidate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the JSON files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each exercise
    results = {
        "exercise1": evaluate_exercise1(submission, answer_key),
        "exercise2": evaluate_exercise2(submission, answer_key),
        "exercise3": evaluate_exercise3(submission, answer_key)
    }
    
    # Calculate overall score
    overall_score = calculate_overall_score(results)
    
    # Prepare the final results
    final_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_score,
        "performance_rating": get_performance_rating(overall_score),
        "exercise_results": results,
        "passing_threshold": 70.0,
        "passed": overall_score >= 70.0
    }
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {overall_score}%")
    print(f"Performance Rating: {get_performance_rating(overall_score)}")
    print(f"Pass/Fail: {'PASSED' if overall_score >= 70.0 else 'FAILED'}")


if __name__ == "__main__":
    main()