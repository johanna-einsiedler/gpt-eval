#!/usr/bin/env python3
"""
Purchasing Manager Practical Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Purchasing Manager practical exam, calculates scores, and saves the results to a JSON file.

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
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_purchase_order(candidate_po: Dict, answer_po: Dict) -> Dict:
    """Evaluate a single purchase order review."""
    result = {
        "po_number": candidate_po["po_number"],
        "compliant_determination": {
            "correct": candidate_po["compliant"] == answer_po["compliant"],
            "points_earned": 0,
            "points_possible": 2
        },
        "violations": {
            "identified": [],
            "missed": [],
            "incorrect": [],
            "points_earned": 0,
            "points_possible": 0
        },
        "total_points_earned": 0,
        "total_points_possible": 0
    }
    
    # Score compliance determination
    if result["compliant_determination"]["correct"]:
        result["compliant_determination"]["points_earned"] = 2
    
    # If the PO is non-compliant in the answer key
    if not answer_po["compliant"]:
        # Calculate possible points for violations (2 points per violation)
        result["violations"]["points_possible"] = len(answer_po["violations"]) * 2
        
        # Create a dictionary of answer violations for easy lookup
        answer_violations = {(v["violation_code"], v["policy_section"]): v for v in answer_po["violations"]}
        
        # Check candidate violations
        candidate_violations = candidate_po["violations"] if "violations" in candidate_po else []
        
        for violation in candidate_violations:
            key = (violation["violation_code"], violation["policy_section"])
            
            if key in answer_violations:
                # Violation correctly identified
                correct_action = answer_violations[key]["corrective_action_code"]
                candidate_action = violation["corrective_action_code"]
                
                violation_result = {
                    "violation_code": violation["violation_code"],
                    "policy_section": violation["policy_section"],
                    "corrective_action": {
                        "candidate": candidate_action,
                        "correct": candidate_action == correct_action,
                        "expected": correct_action
                    },
                    "points_earned": 0
                }
                
                # Award points: 1 for correct violation identification, 1 for correct action
                points = 1  # For correct violation identification
                if candidate_action == correct_action:
                    points += 1  # For correct corrective action
                
                violation_result["points_earned"] = points
                result["violations"]["points_earned"] += points
                result["violations"]["identified"].append(violation_result)
                
                # Remove from answer violations to track what's been found
                del answer_violations[key]
            else:
                # Incorrect violation reported
                result["violations"]["incorrect"].append({
                    "violation_code": violation["violation_code"],
                    "policy_section": violation["policy_section"],
                    "corrective_action_code": violation["corrective_action_code"]
                })
        
        # Record missed violations
        for v in answer_violations.values():
            result["violations"]["missed"].append({
                "violation_code": v["violation_code"],
                "policy_section": v["policy_section"],
                "corrective_action_code": v["corrective_action_code"]
            })
    
    # Calculate total points
    result["total_points_earned"] = result["compliant_determination"]["points_earned"] + result["violations"]["points_earned"]
    result["total_points_possible"] = result["compliant_determination"]["points_possible"] + result["violations"]["points_possible"]
    
    return result


def evaluate_contract_clause(candidate_clause: Dict, answer_clause: Dict) -> Dict:
    """Evaluate a single contract clause analysis."""
    result = {
        "contract": candidate_clause["contract"],
        "clause_number": candidate_clause["clause_number"],
        "compliance_determination": {
            "candidate": candidate_clause["compliant"],
            "expected": answer_clause["compliant"],
            "correct": candidate_clause["compliant"] == answer_clause["compliant"],
            "points_earned": 0,
            "points_possible": 1
        },
        "policy_section": {
            "candidate": candidate_clause["policy_section"],
            "expected": answer_clause["policy_section"],
            "correct": False,
            "points_earned": 0,
            "points_possible": 0
        },
        "corrective_action": {
            "candidate": candidate_clause["corrective_action_code"],
            "expected": answer_clause["corrective_action_code"],
            "correct": False,
            "points_earned": 0,
            "points_possible": 0
        },
        "total_points_earned": 0,
        "total_points_possible": 3
    }
    
    # Score compliance determination
    if result["compliance_determination"]["correct"]:
        result["compliance_determination"]["points_earned"] = 1
    
    # If non-compliant in answer key, evaluate policy section and corrective action
    if answer_clause["compliant"] == "NC":
        result["policy_section"]["points_possible"] = 1
        result["corrective_action"]["points_possible"] = 1
        
        # Check policy section
        if candidate_clause["policy_section"] == answer_clause["policy_section"]:
            result["policy_section"]["correct"] = True
            result["policy_section"]["points_earned"] = 1
        
        # Check corrective action
        if candidate_clause["corrective_action_code"] == answer_clause["corrective_action_code"]:
            result["corrective_action"]["correct"] = True
            result["corrective_action"]["points_earned"] = 1
    
    # Calculate total points
    result["total_points_earned"] = (
        result["compliance_determination"]["points_earned"] +
        result["policy_section"]["points_earned"] +
        result["corrective_action"]["points_earned"]
    )
    
    return result


def evaluate_submission(candidate_data: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire candidate submission against the answer key."""
    results = {
        "candidate_name": candidate_data.get("candidate_name", "Unknown"),
        "exam_date": candidate_data.get("exam_date", "Unknown"),
        "task1_purchase_order_review": {
            "evaluations": [],
            "points_earned": 0,
            "points_possible": 40,
            "non_compliant_identified_count": 0,
            "violations_identified_count": 0,
            "total_violations_count": 0
        },
        "task2_contract_clause_analysis": {
            "evaluations": [],
            "points_earned": 0,
            "points_possible": 30,
            "correct_compliance_assessments": 0
        },
        "critical_requirements": {
            "identified_3_of_5_non_compliant_pos": False,
            "identified_7_of_10_violations": False,
            "correctly_assessed_7_of_10_clauses": False,
            "all_met": False
        },
        "overall_score": 0
    }
    
    # Evaluate Task 1: Purchase Order Review
    po_map = {po["po_number"]: po for po in answer_key["task1_purchase_order_review"]}
    total_violations = sum(len(po["violations"]) for po in answer_key["task1_purchase_order_review"] if not po["compliant"])
    results["task1_purchase_order_review"]["total_violations_count"] = total_violations
    
    violations_identified = 0
    
    for candidate_po in candidate_data["task1_purchase_order_review"]:
        po_number = candidate_po["po_number"]
        if po_number in po_map:
            evaluation = evaluate_purchase_order(candidate_po, po_map[po_number])
            results["task1_purchase_order_review"]["evaluations"].append(evaluation)
            
            # Update points
            results["task1_purchase_order_review"]["points_earned"] += evaluation["total_points_earned"]
            
            # Track non-compliant POs correctly identified
            if not po_map[po_number]["compliant"] and not candidate_po["compliant"]:
                results["task1_purchase_order_review"]["non_compliant_identified_count"] += 1
            
            # Track violations correctly identified
            violations_identified += len(evaluation["violations"]["identified"])
    
    results["task1_purchase_order_review"]["violations_identified_count"] = violations_identified
    
    # Evaluate Task 2: Contract Clause Analysis
    for i, candidate_clause in enumerate(candidate_data["task2_contract_clause_analysis"]):
        if i < len(answer_key["task2_contract_clause_analysis"]):
            answer_clause = answer_key["task2_contract_clause_analysis"][i]
            evaluation = evaluate_contract_clause(candidate_clause, answer_clause)
            results["task2_contract_clause_analysis"]["evaluations"].append(evaluation)
            
            # Update points
            results["task2_contract_clause_analysis"]["points_earned"] += evaluation["total_points_earned"]
            
            # Track correct compliance assessments
            if evaluation["compliance_determination"]["correct"]:
                results["task2_contract_clause_analysis"]["correct_compliance_assessments"] += 1
    
    # Evaluate critical requirements
    results["critical_requirements"]["identified_3_of_5_non_compliant_pos"] = (
        results["task1_purchase_order_review"]["non_compliant_identified_count"] >= 3
    )
    
    results["critical_requirements"]["identified_7_of_10_violations"] = (
        results["task1_purchase_order_review"]["violations_identified_count"] >= 7
    )
    
    results["critical_requirements"]["correctly_assessed_7_of_10_clauses"] = (
        results["task2_contract_clause_analysis"]["correct_compliance_assessments"] >= 7
    )
    
    results["critical_requirements"]["all_met"] = (
        results["critical_requirements"]["identified_3_of_5_non_compliant_pos"] and
        results["critical_requirements"]["identified_7_of_10_violations"] and
        results["critical_requirements"]["correctly_assessed_7_of_10_clauses"]
    )
    
    # Calculate overall score
    total_points_earned = (
        results["task1_purchase_order_review"]["points_earned"] +
        results["task2_contract_clause_analysis"]["points_earned"]
    )
    
    total_points_possible = (
        results["task1_purchase_order_review"]["points_possible"] +
        results["task2_contract_clause_analysis"]["points_possible"]
    )
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    
    return results


def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    candidate_data = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(candidate_data, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")


if __name__ == "__main__":
    main()