#!/usr/bin/env python3
"""
Claims Adjuster Authority Level Processing Exam Evaluator.

This script evaluates a candidate's submission for the Claims Adjuster practical exam
by comparing it to an answer key and generating a detailed evaluation report.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_claim(candidate_claim: Dict, answer_claim: Dict) -> Tuple[int, Dict]:
    """
    Evaluate a single claim against the answer key.
    
    Returns a tuple containing:
        - Score out of 20 points
        - Dictionary with detailed evaluation results
    """
    score = 0
    evaluation = {
        "claim_id": candidate_claim["claim_id"],
        "details": [],
        "score": 0,
        "max_score": 20,
    }
    
    # 1. Coverage determination evaluation (5 points)
    if candidate_claim["coverage_determination"] == answer_claim["coverage_determination"]:
        score += 5
        evaluation["details"].append({
            "criterion": "Coverage Determination",
            "points_earned": 5,
            "max_points": 5,
            "candidate_answer": candidate_claim["coverage_determination"],
            "correct_answer": answer_claim["coverage_determination"],
            "correct": True
        })
    else:
        evaluation["details"].append({
            "criterion": "Coverage Determination",
            "points_earned": 0,
            "max_points": 5,
            "candidate_answer": candidate_claim["coverage_determination"],
            "correct_answer": answer_claim["coverage_determination"],
            "correct": False
        })
    
    # 2. Settlement calculation evaluation (5 points)
    # Allow for a small margin of error ($50)
    candidate_settlement = candidate_claim["calculated_settlement"]
    correct_settlement = answer_claim["calculated_settlement"]
    settlement_points = 0
    
    if abs(candidate_settlement - correct_settlement) <= 50:
        settlement_points = 5
    
    score += settlement_points
    evaluation["details"].append({
        "criterion": "Settlement Calculation",
        "points_earned": settlement_points,
        "max_points": 5,
        "candidate_answer": candidate_settlement,
        "correct_answer": correct_settlement,
        "correct": settlement_points == 5,
        "note": "Within $50 margin" if 0 < abs(candidate_settlement - correct_settlement) <= 50 else None
    })
    
    # 3. Decision evaluation (5 points)
    if candidate_claim["decision"] == answer_claim["decision"]:
        score += 5
        evaluation["details"].append({
            "criterion": "Decision (Approve/Deny/Escalate)",
            "points_earned": 5,
            "max_points": 5,
            "candidate_answer": candidate_claim["decision"],
            "correct_answer": answer_claim["decision"],
            "correct": True
        })
    else:
        evaluation["details"].append({
            "criterion": "Decision (Approve/Deny/Escalate)",
            "points_earned": 0,
            "max_points": 5,
            "candidate_answer": candidate_claim["decision"],
            "correct_answer": answer_claim["decision"],
            "correct": False
        })
    
    # 4. Authority level assessment (3 points)
    if candidate_claim["within_authority"] == answer_claim["within_authority"]:
        score += 3
        evaluation["details"].append({
            "criterion": "Authority Level Assessment",
            "points_earned": 3,
            "max_points": 3,
            "candidate_answer": candidate_claim["within_authority"],
            "correct_answer": answer_claim["within_authority"],
            "correct": True
        })
    else:
        evaluation["details"].append({
            "criterion": "Authority Level Assessment",
            "points_earned": 0,
            "max_points": 3,
            "candidate_answer": candidate_claim["within_authority"],
            "correct_answer": answer_claim["within_authority"],
            "correct": False
        })
    
    # 5. Reason code evaluation (part of justification - evaluated separately)
    if candidate_claim["coverage_determination"] == "not_covered":
        if candidate_claim["reason_code"] == answer_claim["reason_code"]:
            evaluation["details"].append({
                "criterion": "Reason Code",
                "points_earned": 0,  # Not counted in score directly, but noted
                "max_points": 0,
                "candidate_answer": candidate_claim["reason_code"],
                "correct_answer": answer_claim["reason_code"],
                "correct": True
            })
        else:
            evaluation["details"].append({
                "criterion": "Reason Code",
                "points_earned": 0,
                "max_points": 0,
                "candidate_answer": candidate_claim["reason_code"],
                "correct_answer": answer_claim["reason_code"],
                "correct": False
            })
    
    # 6. Justification evaluation (2 points)
    # Simplified evaluation - just check if justification exists and isn't empty
    if candidate_claim["justification"] and len(candidate_claim["justification"].strip()) > 0:
        score += 2
        evaluation["details"].append({
            "criterion": "Justification",
            "points_earned": 2,
            "max_points": 2,
            "candidate_answer": candidate_claim["justification"][:50] + "..." if len(candidate_claim["justification"]) > 50 else candidate_claim["justification"],
            "correct": True
        })
    else:
        evaluation["details"].append({
            "criterion": "Justification",
            "points_earned": 0, 
            "max_points": 2,
            "candidate_answer": "(Missing or empty)",
            "correct": False
        })
    
    evaluation["score"] = score
    return score, evaluation


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete test submission against the answer key."""
    total_score = 0
    max_score = 100
    claim_evaluations = []
    
    # Create a mapping of claim_id to answer_key claim for easier lookup
    answer_claims = {claim["claim_id"]: claim for claim in answer_key["claim_decisions"]}
    
    # Track critical claims (3 and 5)
    critical_claim_ids = ["CL-64510", "CL-52198"]  # Claim 3 and Claim 5
    critical_claims_correct = {claim_id: False for claim_id in critical_claim_ids}
    
    # Counters for pass criteria
    correct_decisions = 0
    accurate_calculations = 0
    
    for candidate_claim in submission["claim_decisions"]:
        claim_id = candidate_claim["claim_id"]
        
        if claim_id in answer_claims:
            answer_claim = answer_claims[claim_id]
            claim_score, claim_evaluation = evaluate_claim(candidate_claim, answer_claim)
            
            # Add to total score
            total_score += claim_score
            claim_evaluations.append(claim_evaluation)
            
            # Check if decision is correct
            decision_correct = False
            for detail in claim_evaluation["details"]:
                if detail["criterion"] == "Decision (Approve/Deny/Escalate)" and detail["correct"]:
                    decision_correct = True
                    correct_decisions += 1
            
            # Check if calculation is within margin
            calculation_accurate = False
            for detail in claim_evaluation["details"]:
                if detail["criterion"] == "Settlement Calculation" and detail["correct"]:
                    calculation_accurate = True
                    accurate_calculations += 1
            
            # Check if critical claims are correct
            if claim_id in critical_claim_ids:
                critical_claims_correct[claim_id] = decision_correct
    
    # Determine if pass criteria are met
    passes_critical_claims = all(critical_claims_correct.values())
    passes_decision_accuracy = correct_decisions >= 4
    passes_calculation_accuracy = accurate_calculations >= 4
    
    # Calculate percentage score
    percentage_score = (total_score / max_score) * 100
    
    # Create the evaluation results
    results = {
        "candidate_id": submission.get("candidate_id", "UNKNOWN"),
        "claim_evaluations": claim_evaluations,
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": percentage_score,
        "pass_criteria": {
            "critical_claims_handled_correctly": passes_critical_claims,
            "critical_claim_details": {
                "CL-64510": critical_claims_correct["CL-64510"],
                "CL-52198": critical_claims_correct["CL-52198"]
            },
            "decision_accuracy": {
                "correct_decisions": correct_decisions,
                "required": 4,
                "passed": passes_decision_accuracy
            },
            "calculation_accuracy": {
                "accurate_calculations": accurate_calculations,
                "required": 4,
                "passed": passes_calculation_accuracy
            }
        },
        "passed_exam": passes_critical_claims and passes_decision_accuracy and passes_calculation_accuracy and percentage_score >= 80
    }
    
    return results


def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed exam: {results['passed_exam']}")


if __name__ == "__main__":
    main()