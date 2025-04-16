#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any, List, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_exercise1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, int, List[str]]:
    """Evaluate Exercise 1 (6 points total)."""
    points = 0
    max_points = 6
    feedback = []
    
    sub_ex1 = submission.get("exercise1", {})
    key_ex1 = answer_key.get("exercise1", {})
    
    # Check claim number (1 point)
    if sub_ex1.get("claimNumber") == key_ex1.get("claimNumber"):
        points += 1
    else:
        feedback.append("Incorrect claim number")
    
    # Check coverage determination (1 point)
    if sub_ex1.get("coverageDetermination") == key_ex1.get("coverageDetermination"):
        points += 1
    else:
        feedback.append("Incorrect coverage determination")
    
    # Check applicable limit (1 point)
    if sub_ex1.get("applicableLimit") == key_ex1.get("applicableLimit"):
        points += 1
    else:
        feedback.append("Incorrect applicable limit")
    
    # Check applicable deductible (1 point)
    if sub_ex1.get("applicableDeductible") == key_ex1.get("applicableDeductible"):
        points += 1
    else:
        feedback.append("Incorrect applicable deductible")
    
    # Check relevant policy section (1 point)
    if sub_ex1.get("relevantPolicySection") == key_ex1.get("relevantPolicySection"):
        points += 1
    else:
        feedback.append("Incorrect relevant policy section")
    
    # Check applicable exclusions (1 point)
    if sorted(sub_ex1.get("applicableExclusions", [])) == sorted(key_ex1.get("applicableExclusions", [])):
        points += 1
    else:
        feedback.append("Incorrect applicable exclusions")
    
    return points, max_points, feedback

def evaluate_exercise2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, int, List[str]]:
    """Evaluate Exercise 2 (10 points total - 5 for policy matches, 5 for benefits calculation)."""
    points = 0
    max_points = 10
    feedback = []
    
    sub_ex2 = submission.get("exercise2", {})
    key_ex2 = answer_key.get("exercise2", {})
    
    # Evaluate policy matches (5 points)
    sub_matches = {(match.get("claimId"), match.get("policyId"), match.get("coverageType")) 
                  for match in sub_ex2.get("policyMatches", [])}
    key_matches = {(match.get("claimId"), match.get("policyId"), match.get("coverageType")) 
                  for match in key_ex2.get("policyMatches", [])}
    
    # Count correct matches
    correct_matches = len(sub_matches.intersection(key_matches))
    points += correct_matches
    
    if correct_matches < 5:
        feedback.append(f"Matched {correct_matches}/5 policies correctly")
    
    # Evaluate benefits calculation (5 points)
    sub_benefits = {(calc.get("claimId"), calc.get("eligibleAmount"), calc.get("ineligibleAmount")) 
                   for calc in sub_ex2.get("benefitsCalculation", [])}
    key_benefits = {(calc.get("claimId"), calc.get("eligibleAmount"), calc.get("ineligibleAmount")) 
                   for calc in key_ex2.get("benefitsCalculation", [])}
    
    # Count correct benefit calculations
    correct_benefits = len(sub_benefits.intersection(key_benefits))
    points += correct_benefits
    
    if correct_benefits < 5:
        feedback.append(f"Calculated benefits correctly for {correct_benefits}/5 claims")
    
    return points, max_points, feedback

def evaluate_exercise3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, int, List[str]]:
    """Evaluate Exercise 3 (4 points total - 2 points per claim)."""
    points = 0
    max_points = 4
    feedback = []
    
    sub_ex3 = submission.get("exercise3", {})
    key_ex3 = answer_key.get("exercise3", {})
    
    # Evaluate claim 1
    sub_claim1 = sub_ex3.get("claim1", {})
    key_claim1 = key_ex3.get("claim1", {})
    
    # Check coverage verification (1 point)
    if sub_claim1.get("coverageVerification") == key_claim1.get("coverageVerification"):
        points += 1
    else:
        feedback.append("Incorrect coverage verification for claim 1")
    
    # Check maximum payable or denial reason (1 point)
    if sub_claim1.get("coverageVerification") == True:
        if sub_claim1.get("maximumPayable") == key_claim1.get("maximumPayable"):
            points += 1
        else:
            feedback.append("Incorrect maximum payable amount for claim 1")
    else:
        if sub_claim1.get("denialReason") == key_claim1.get("denialReason"):
            points += 1
        else:
            feedback.append("Incorrect denial reason for claim 1")
    
    # Evaluate claim 2
    sub_claim2 = sub_ex3.get("claim2", {})
    key_claim2 = key_ex3.get("claim2", {})
    
    # Check coverage verification (1 point)
    if sub_claim2.get("coverageVerification") == key_claim2.get("coverageVerification"):
        points += 1
    else:
        feedback.append("Incorrect coverage verification for claim 2")
    
    # Check maximum payable or denial reason (1 point)
    if sub_claim2.get("coverageVerification") == True:
        if sub_claim2.get("maximumPayable") == key_claim2.get("maximumPayable"):
            points += 1
        else:
            feedback.append("Incorrect maximum payable amount for claim 2")
    else:
        if sub_claim2.get("denialReason") == key_claim2.get("denialReason"):
            points += 1
        else:
            feedback.append("Incorrect denial reason for claim 2")
    
    return points, max_points, feedback

def check_critical_requirements(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> List[str]:
    """Check if critical requirements are met."""
    critical_issues = []
    
    # Must correctly identify coverage determination in Exercise 1
    if submission.get("exercise1", {}).get("coverageDetermination") != answer_key.get("exercise1", {}).get("coverageDetermination"):
        critical_issues.append("Failed to correctly identify coverage determination in Exercise 1")
    
    # Must correctly identify at least 4/5 policy matches in Exercise 2
    sub_matches = {(match.get("claimId"), match.get("policyId"), match.get("coverageType")) 
                  for match in submission.get("exercise2", {}).get("policyMatches", [])}
    key_matches = {(match.get("claimId"), match.get("policyId"), match.get("coverageType")) 
                  for match in answer_key.get("exercise2", {}).get("policyMatches", [])}
    correct_matches = len(sub_matches.intersection(key_matches))
    
    if correct_matches < 4:
        critical_issues.append(f"Failed to correctly identify at least 4/5 policy matches in Exercise 2 (got {correct_matches})")
    
    # Must correctly identify both coverage determinations in Exercise 3
    sub_ex3 = submission.get("exercise3", {})
    key_ex3 = answer_key.get("exercise3", {})
    
    if sub_ex3.get("claim1", {}).get("coverageVerification") != key_ex3.get("claim1", {}).get("coverageVerification"):
        critical_issues.append("Failed to correctly identify coverage determination for claim 1 in Exercise 3")
    
    if sub_ex3.get("claim2", {}).get("coverageVerification") != key_ex3.get("claim2", {}).get("coverageVerification"):
        critical_issues.append("Failed to correctly identify coverage determination for claim 2 in Exercise 3")
    
    return critical_issues

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission and generate results."""
    results = {"candidate_id": submission.get("candidate_id", "Unknown")}
    
    # Evaluate each exercise
    ex1_points, ex1_max, ex1_feedback = evaluate_exercise1(submission, answer_key)
    ex2_points, ex2_max, ex2_feedback = evaluate_exercise2(submission, answer_key)
    ex3_points, ex3_max, ex3_feedback = evaluate_exercise3(submission, answer_key)
    
    # Calculate total score
    total_points = ex1_points + ex2_points + ex3_points
    total_max = ex1_max + ex2_max + ex3_max
    overall_score = (total_points / total_max) * 100
    
    # Check critical requirements
    critical_issues = check_critical_requirements(submission, answer_key)
    
    # Compile results
    results.update({
        "exercise1": {
            "points": ex1_points,
            "max_points": ex1_max,
            "feedback": ex1_feedback
        },
        "exercise2": {
            "points": ex2_points,
            "max_points": ex2_max,
            "feedback": ex2_feedback
        },
        "exercise3": {
            "points": ex3_points,
            "max_points": ex3_max,
            "feedback": ex3_feedback
        },
        "overall_score": round(overall_score, 2),
        "total_points": total_points,
        "passing_score": 80,
        "passed": overall_score >= 80 and not critical_issues,
        "critical_issues": critical_issues
    })
    
    return results

def main():
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
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    if results.get("passed"):
        print("PASSED")
    else:
        print("FAILED")
        if results.get("critical_issues"):
            for issue in results.get("critical_issues"):
                print(f"- {issue}")

if __name__ == "__main__":
    main()