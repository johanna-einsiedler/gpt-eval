#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any

def load_json_file(filename: str) -> Dict:
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate a candidate's submission against the answer key."""
    # Initialize scoring
    results = {
        "identification_score": 0,
        "classification_score": 0,
        "financial_impact_score": 0,
        "recommended_action_score": 0,
        "documentation_score": 0,
        "false_positives": 0,
        "details": {
            "correct_identifications": [],
            "missed_identifications": [],
            "false_identifications": [],
            "correct_classifications": [],
            "incorrect_classifications": [],
            "correct_financial_impacts": [],
            "incorrect_financial_impacts": [],
            "correct_recommended_actions": [],
            "incorrect_recommended_actions": [],
            "correct_documentation": [],
            "incorrect_documentation": []
        }
    }
    
    # Extract irregularities from answer key and submission
    key_irregularities = {item["claim_id"]: item for item in answer_key.get("identified_irregularities", [])}
    submission_irregularities = {item["claim_id"]: item for item in submission.get("identified_irregularities", [])}
    
    # Check for candidate identification
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
    # Check for correct identifications and false positives
    for claim_id in submission_irregularities:
        if claim_id in key_irregularities:
            # Correct identification
            results["identification_score"] += 5
            results["details"]["correct_identifications"].append(claim_id)
            
            # Check classification
            sub_type = submission_irregularities[claim_id]["irregularity_type"]
            key_type = key_irregularities[claim_id]["irregularity_type"]
            if sub_type == key_type:
                results["classification_score"] += 5
                results["details"]["correct_classifications"].append(claim_id)
            else:
                results["details"]["incorrect_classifications"].append({
                    "claim_id": claim_id,
                    "submitted": sub_type,
                    "expected": key_type
                })
            
            # Check financial impact
            sub_impact = submission_irregularities[claim_id]["financial_impact"]
            key_impact = key_irregularities[claim_id]["financial_impact"]
            # Allow a small tolerance for floating point precision
            if abs(float(sub_impact) - float(key_impact)) < 0.01:
                results["financial_impact_score"] += 5
                results["details"]["correct_financial_impacts"].append(claim_id)
            else:
                results["details"]["incorrect_financial_impacts"].append({
                    "claim_id": claim_id,
                    "submitted": sub_impact,
                    "expected": key_impact
                })
            
            # Check recommended action
            sub_action = submission_irregularities[claim_id]["recommended_action"]
            key_action = key_irregularities[claim_id]["recommended_action"]
            if sub_action == key_action:
                results["recommended_action_score"] += 5
                results["details"]["correct_recommended_actions"].append(claim_id)
            else:
                results["details"]["incorrect_recommended_actions"].append({
                    "claim_id": claim_id,
                    "submitted": sub_action,
                    "expected": key_action
                })
            
            # Check documentation citation
            sub_doc = submission_irregularities[claim_id]["evidence_location"]
            key_doc = key_irregularities[claim_id]["evidence_location"]
            # Look for page numbers in both, allowing for some variation in format
            if (sub_doc.lower().replace(" ", "") == key_doc.lower().replace(" ", "") or
                (sub_doc.lower().startswith("page") and key_doc.lower().startswith("page") and
                 any(num in sub_doc for num in key_doc.split("-")))):
                results["documentation_score"] += 5
                results["details"]["correct_documentation"].append(claim_id)
            else:
                results["details"]["incorrect_documentation"].append({
                    "claim_id": claim_id,
                    "submitted": sub_doc,
                    "expected": key_doc
                })
                
        else:
            # False positive
            results["false_positives"] += 1
            results["details"]["false_identifications"].append(claim_id)
    
    # Check for missed identifications
    for claim_id in key_irregularities:
        if claim_id not in submission_irregularities:
            results["details"]["missed_identifications"].append(claim_id)
    
    # Calculate total score
    max_points = 100  # 5 points × 4 categories × 5 claims
    actual_points = (results["identification_score"] + 
                    results["classification_score"] + 
                    results["financial_impact_score"] + 
                    results["recommended_action_score"] + 
                    results["documentation_score"])
    
    results["overall_score"] = (actual_points / 80) * 100  # 80 is max possible (20 points per category)
    
    # Determine pass/fail status
    primary_criteria_met = 0
    if results["identification_score"] >= 15:  # 3 out of 4 correct (75%)
        primary_criteria_met += 1
    if results["classification_score"] >= 15:  # 3 out of 4 correct (75%)
        primary_criteria_met += 1
    if results["financial_impact_score"] >= 15:  # 3 out of 4 correct (75%)
        primary_criteria_met += 1
    if results["recommended_action_score"] >= 15:  # 3 out of 4 correct (75%)
        primary_criteria_met += 1
    
    if results["overall_score"] == 100:
        results["status"] = "Pass with Excellence"
    elif primary_criteria_met == 4 and results["false_positives"] <= 1:
        results["status"] = "Pass"
    elif primary_criteria_met == 3 and results["false_positives"] <= 1:
        results["status"] = "Conditional Pass"
    else:
        results["status"] = "Fail"
    
    results["primary_criteria_met"] = primary_criteria_met
    
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
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Status: {results['status']}")

if __name__ == "__main__":
    main()