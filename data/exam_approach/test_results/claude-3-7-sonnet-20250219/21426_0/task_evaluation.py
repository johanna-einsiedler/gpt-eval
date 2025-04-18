#!/usr/bin/env python3

import json
import sys
import os
from math import isclose

def load_json(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_submission(submission, answer_key):
    """Evaluate a candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "claim_results": [],
        "overall_score": 0,
        "max_possible_score": 100,
        "passing_threshold": 75
    }
    
    total_points = 0
    
    # Match claims by claim_id for evaluation
    submission_claims = {claim["claim_id"]: claim for claim in submission.get("claims", [])}
    answer_key_claims = {claim["claim_id"]: claim for claim in answer_key.get("claims", [])}
    
    for claim_id, answer in answer_key_claims.items():
        if claim_id not in submission_claims:
            results["claim_results"].append({
                "claim_id": claim_id,
                "points": 0,
                "max_points": 20,
                "details": "Claim missing from submission"
            })
            continue
            
        submission_claim = submission_claims[claim_id]
        claim_score = evaluate_claim(submission_claim, answer)
        total_points += claim_score["total_points"]
        results["claim_results"].append(claim_score)
    
    # Check for any extra claims in submission that weren't in the answer key
    for claim_id in submission_claims:
        if claim_id not in answer_key_claims:
            results["claim_results"].append({
                "claim_id": claim_id,
                "points": 0,
                "max_points": 0,
                "details": "Extra claim not in answer key"
            })
    
    # Calculate overall percentage score
    results["overall_score"] = round((total_points / 100) * 100, 2)
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    
    # Check for critical errors (automatic failure conditions)
    critical_errors = check_critical_errors(submission_claims, answer_key_claims)
    
    if critical_errors:
        results["critical_errors"] = critical_errors
        results["passed"] = False
        results["details"] = "Automatic failure due to critical errors"
    
    return results

def evaluate_claim(submission, answer):
    """Evaluate a single claim against its answer."""
    result = {
        "claim_id": submission["claim_id"],
        "max_points": 20,
        "scoring_details": {
            "calculation": {"earned": 0, "possible": 8, "notes": ""},
            "decision": {"earned": 0, "possible": 5, "notes": ""},
            "escalation_code": {"earned": 0, "possible": 3, "notes": ""},
            "payment_breakdown": {"earned": 0, "possible": 4, "notes": ""}
        }
    }
    
    # Evaluate calculated payment (8 points, with 5% tolerance)
    if isclose(submission["calculated_payment"], answer["calculated_payment"], rel_tol=0.05):
        result["scoring_details"]["calculation"]["earned"] = 8
    else:
        result["scoring_details"]["calculation"]["notes"] = (
            f"Expected {answer['calculated_payment']}, "
            f"got {submission['calculated_payment']}"
        )
    
    # Evaluate decision (5 points)
    if submission["decision"] == answer["decision"]:
        result["scoring_details"]["decision"]["earned"] = 5
    else:
        result["scoring_details"]["decision"]["notes"] = (
            f"Expected '{answer['decision']}', got '{submission['decision']}'"
        )
    
    # Evaluate escalation code (3 points)
    # Only matters if the decision is "escalate"
    if answer["decision"] == "escalate":
        if submission["escalation_code"] == answer["escalation_code"]:
            result["scoring_details"]["escalation_code"]["earned"] = 3
        else:
            result["scoring_details"]["escalation_code"]["notes"] = (
                f"Expected '{answer['escalation_code']}', "
                f"got '{submission['escalation_code']}'"
            )
    else:
        # If the answer doesn't require escalation, we only give points if the
        # submission also doesn't have an escalation code
        if submission["escalation_code"] is None:
            result["scoring_details"]["escalation_code"]["earned"] = 3
        else:
            result["scoring_details"]["escalation_code"]["notes"] = (
                f"Expected null, got '{submission['escalation_code']}'"
            )
    
    # Evaluate payment breakdown (4 points)
    breakdown_score, breakdown_notes = evaluate_payment_breakdown(
        submission["payment_breakdown"], 
        answer["payment_breakdown"]
    )
    result["scoring_details"]["payment_breakdown"]["earned"] = breakdown_score
    if breakdown_notes:
        result["scoring_details"]["payment_breakdown"]["notes"] = breakdown_notes
    
    # Calculate total points for this claim
    result["total_points"] = sum(
        detail["earned"] for detail in result["scoring_details"].values()
    )
    
    return result

def evaluate_payment_breakdown(submission_breakdown, answer_breakdown):
    """Evaluate the payment breakdown with 5% tolerance on each component."""
    # Get all possible keys from both breakdowns
    all_keys = set(submission_breakdown.keys()).union(set(answer_breakdown.keys()))
    
    # Count components that match within tolerance
    matching_components = 0
    total_components = len(all_keys)
    notes = []
    
    for key in all_keys:
        sub_value = submission_breakdown.get(key, 0)
        ans_value = answer_breakdown.get(key, 0)
        
        # If both values are zero, consider them matching
        if sub_value == 0 and ans_value == 0:
            matching_components += 1
            continue
            
        # Otherwise, check with tolerance
        if isclose(sub_value, ans_value, rel_tol=0.05):
            matching_components += 1
        else:
            notes.append(f"{key}: Expected {ans_value}, got {sub_value}")
    
    # Calculate score proportionally (out of 4 points)
    score = round(4 * (matching_components / total_components))
    
    return score, "; ".join(notes) if notes else ""

def check_critical_errors(submission_claims, answer_key_claims):
    """Check for critical errors that result in automatic failure."""
    critical_errors = []
    
    # Check for approving claims that exceed authority
    for claim_id, answer in answer_key_claims.items():
        if claim_id not in submission_claims:
            continue
            
        submission = submission_claims[claim_id]
        
        # Critical error: Approving a claim that should be escalated
        if (answer["decision"] == "escalate" and 
            submission["decision"] == "approve" and
            answer["calculated_payment"] > 25000):
            critical_errors.append(
                f"Claim {claim_id}: Approved a claim that exceeds authority limit"
            )
            
        # Critical error: Using incorrect escalation code when escalating
        if (submission["decision"] == "escalate" and 
            submission["escalation_code"] != answer["escalation_code"] and
            submission["escalation_code"] is not None):
            critical_errors.append(
                f"Claim {claim_id}: Used incorrect escalation code"
            )
            
        # Critical error: Failure to recognize replacement cost vs ACV in Claim 5
        if (claim_id == "RD-20231105" and 
            submission["decision"] == "approve" and
            answer["decision"] == "escalate"):
            critical_errors.append(
                "Claim RD-20231105: Failed to recognize replacement cost vs. actual cash value distinction"
            )
    
    return critical_errors

def main():
    """Main function to parse arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    # Normalize answer key structure if needed
    if "answer_key" in answer_key:
        answer_key = answer_key["answer_key"]
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to JSON file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    if results.get("passed", False):
        print("PASSED")
    else:
        print("FAILED")
        if "critical_errors" in results:
            print("Critical errors found:")
            for error in results["critical_errors"]:
                print(f"- {error}")

if __name__ == "__main__":
    main()