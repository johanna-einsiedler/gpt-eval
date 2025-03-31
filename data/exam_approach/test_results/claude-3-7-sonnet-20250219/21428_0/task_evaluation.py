import json
import re
from difflib import SequenceMatcher

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def similarity_score(a, b):
    """Calculate string similarity between 0 and 1"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_match(candidate_item, answer_items, threshold=0.7):
    """Find the best matching item from answer_items for candidate_item"""
    best_score = 0
    best_match = None
    
    for answer_item in answer_items:
        score = similarity_score(candidate_item, answer_item)
        if score > best_score:
            best_score = score
            best_match = answer_item
    
    if best_score >= threshold:
        return best_match
    return None

def evaluate_exercise1(candidate, answer_key):
    score = 0
    feedback = []
    
    # Check inconsistencies (6 points)
    candidate_inconsistencies = candidate.get("exercise1", {}).get("inconsistencies", [])
    answer_inconsistencies = answer_key.get("exercise1", {}).get("inconsistencies", [])
    
    matched_inconsistencies = []
    for c_inconsistency in candidate_inconsistencies:
        match = find_best_match(c_inconsistency, answer_inconsistencies)
        if match and match not in matched_inconsistencies:
            matched_inconsistencies.append(match)
    
    inconsistency_points = min(6, len(matched_inconsistencies) * 2)
    score += inconsistency_points
    feedback.append(f"Identified {len(matched_inconsistencies)} of 4 inconsistencies: {inconsistency_points}/6 points")
    
    # Check verification status (2 points)
    candidate_status = candidate.get("exercise1", {}).get("verificationStatus", "")
    answer_status = answer_key.get("exercise1", {}).get("verificationStatus", "")
    
    if candidate_status.lower() == answer_status.lower():
        score += 2
        feedback.append("Correct verification status: 2/2 points")
    else:
        feedback.append(f"Incorrect verification status. Expected '{answer_status}', got '{candidate_status}': 0/2 points")
    
    # Check reason code (2 points)
    candidate_code = candidate.get("exercise1", {}).get("reasonCode", "")
    answer_code = answer_key.get("exercise1", {}).get("reasonCode", "")
    
    # Allow for R03 or R04 as valid reason codes
    if candidate_code == answer_code or (answer_code == "R04" and candidate_code == "R03"):
        score += 2
        feedback.append("Correct reason code: 2/2 points")
    else:
        feedback.append(f"Incorrect reason code. Expected '{answer_code}' (or R03), got '{candidate_code}': 0/2 points")
    
    return score, feedback

def evaluate_exercise2(candidate, answer_key):
    score = 0
    feedback = []
    
    # Check coverage decision (4 points)
    candidate_decision = candidate.get("exercise2", {}).get("coverageDecision", "")
    answer_decision = answer_key.get("exercise2", {}).get("coverageDecision", "")
    
    if candidate_decision.lower() == answer_decision.lower():
        score += 4
        feedback.append("Correct coverage decision: 4/4 points")
    else:
        feedback.append(f"Incorrect coverage decision. Expected '{answer_decision}', got '{candidate_decision}': 0/4 points")
    
    # Check applicable clauses (4 points)
    candidate_clauses = candidate.get("exercise2", {}).get("applicableClauses", [])
    answer_clauses = answer_key.get("exercise2", {}).get("applicableClauses", [])
    
    matched_clauses = [clause for clause in candidate_clauses if clause in answer_clauses]
    
    if len(matched_clauses) >= 2:
        clause_points = 4
    elif len(matched_clauses) == 1:
        clause_points = 2
    else:
        clause_points = 0
    
    score += clause_points
    feedback.append(f"Identified {len(matched_clauses)} of {len(answer_clauses)} applicable clauses: {clause_points}/4 points")
    
    # Check exclusions (2 points)
    candidate_exclusions = candidate.get("exercise2", {}).get("exclusions", [])
    answer_exclusions = answer_key.get("exercise2", {}).get("exclusions", [])
    
    if len(candidate_exclusions) == len(answer_exclusions) == 0:
        score += 2
        feedback.append("Correctly identified no exclusions apply: 2/2 points")
    else:
        feedback.append(f"Incorrect exclusions. Expected empty list, got {candidate_exclusions}: 0/2 points")
    
    return score, feedback

def evaluate_exercise3(candidate, answer_key):
    score = 0
    feedback = []
    
    # Check calculated amount (3 points)
    candidate_amount = candidate.get("exercise3", {}).get("calculatedAmount", 0)
    answer_amount = answer_key.get("exercise3", {}).get("calculatedAmount", 0)
    
    if isinstance(candidate_amount, str):
        try:
            candidate_amount = float(candidate_amount.replace(',', ''))
        except:
            candidate_amount = 0
    
    if abs(candidate_amount - answer_amount) <= 300:
        score += 3
        feedback.append("Calculated amount within acceptable range: 3/3 points")
    else:
        feedback.append(f"Calculated amount outside acceptable range. Expected around {answer_amount}, got {candidate_amount}: 0/3 points")
    
    # Check deductible applied (2 points)
    candidate_deductible = candidate.get("exercise3", {}).get("deductibleApplied", 0)
    answer_deductible = answer_key.get("exercise3", {}).get("deductibleApplied", 0)
    
    if isinstance(candidate_deductible, str):
        try:
            candidate_deductible = float(candidate_deductible.replace(',', ''))
        except:
            candidate_deductible = 0
    
    if abs(candidate_deductible - answer_deductible) <= 0.01:
        score += 2
        feedback.append("Correct deductible applied: 2/2 points")
    else:
        feedback.append(f"Incorrect deductible. Expected {answer_deductible}, got {candidate_deductible}: 0/2 points")
    
    # Check final settlement (3 points)
    candidate_settlement = candidate.get("exercise3", {}).get("finalSettlement", 0)
    answer_settlement = answer_key.get("exercise3", {}).get("finalSettlement", 0)
    
    if isinstance(candidate_settlement, str):
        try:
            candidate_settlement = float(candidate_settlement.replace(',', ''))
        except:
            candidate_settlement = 0
    
    if abs(candidate_settlement - answer_settlement) <= 300:
        score += 3
        feedback.append("Final settlement within acceptable range: 3/3 points")
    else:
        feedback.append(f"Final settlement outside acceptable range. Expected around {answer_settlement}, got {candidate_settlement}: 0/3 points")
    
    # Check adjustment factors (2 points)
    candidate_factors = candidate.get("exercise3", {}).get("adjustmentFactors", [])
    answer_factors = answer_key.get("exercise3", {}).get("adjustmentFactors", [])
    
    if "ADJ01" in candidate_factors:
        score += 2
        feedback.append("Correctly identified ADJ01 adjustment factor: 2/2 points")
    else:
        feedback.append(f"Failed to identify ADJ01 adjustment factor. Got {candidate_factors}: 0/2 points")
    
    return score, feedback

def evaluate_exercise4(candidate, answer_key):
    score = 0
    feedback = []
    
    # Check fraud risk score (2 points)
    candidate_risk = candidate.get("exercise4", {}).get("fraudRiskScore", 0)
    answer_risk = answer_key.get("exercise4", {}).get("fraudRiskScore", 0)
    
    if isinstance(candidate_risk, str):
        try:
            candidate_risk = int(candidate_risk)
        except:
            candidate_risk = 0
    
    if abs(candidate_risk - answer_risk) <= 1:
        score += 2
        feedback.append("Fraud risk score within acceptable range: 2/2 points")
    else:
        feedback.append(f"Fraud risk score outside acceptable range. Expected around {answer_risk}, got {candidate_risk}: 0/2 points")
    
    # Check red flags identified (6 points)
    candidate_flags = candidate.get("exercise4", {}).get("redFlagsIdentified", [])
    answer_flags = answer_key.get("exercise4", {}).get("redFlagsIdentified", [])
    
    matched_flags = [flag for flag in candidate_flags if flag in answer_flags]
    
    if len(matched_flags) >= 6:
        flag_points = 6
    else:
        flag_points = min(len(matched_flags), 6)
    
    score += flag_points
    feedback.append(f"Identified {len(matched_flags)} of {len(answer_flags)} red flags: {flag_points}/6 points")
    
    # Check recommended action (2 points)
    candidate_action = candidate.get("exercise4", {}).get("recommendedAction", "")
    answer_action = answer_key.get("exercise4", {}).get("recommendedAction", "")
    
    # Allow for A6 or A7 as valid actions
    if candidate_action == answer_action or (answer_action == "A7" and candidate_action == "A6"):
        score += 2
        feedback.append("Appropriate recommended action: 2/2 points")
    else:
        feedback.append(f"Inappropriate recommended action. Expected '{answer_action}' (or A6), got '{candidate_action}': 0/2 points")
    
    return score, feedback

def evaluate_submission(candidate, answer_key):
    results = {
        "overall_score": 0,
        "passing_threshold": 70,
        "total_points": 40,
        "points_achieved": 0,
        "exercises": {}
    }
    
    # Evaluate Exercise 1
    ex1_score, ex1_feedback = evaluate_exercise1(candidate, answer_key)
    results["exercises"]["exercise1"] = {
        "score": ex1_score,
        "max_score": 10,
        "percentage": (ex1_score / 10) * 100,
        "feedback": ex1_feedback,
        "passed": ex1_score >= 5  # 50% threshold
    }
    
    # Evaluate Exercise 2
    ex2_score, ex2_feedback = evaluate_exercise2(candidate, answer_key)
    results["exercises"]["exercise2"] = {
        "score": ex2_score,
        "max_score": 10,
        "percentage": (ex2_score / 10) * 100,
        "feedback": ex2_feedback,
        "passed": ex2_score >= 5  # 50% threshold
    }
    
    # Evaluate Exercise 3
    ex3_score, ex3_feedback = evaluate_exercise3(candidate, answer_key)
    results["exercises"]["exercise3"] = {
        "score": ex3_score,
        "max_score": 10,
        "percentage": (ex3_score / 10) * 100,
        "feedback": ex3_feedback,
        "passed": ex3_score >= 5  # 50% threshold
    }
    
    # Evaluate Exercise 4
    ex4_score, ex4_feedback = evaluate_exercise4(candidate, answer_key)
    results["exercises"]["exercise4"] = {
        "score": ex4_score,
        "max_score": 10,
        "percentage": (ex4_score / 10) * 100,
        "feedback": ex4_feedback,
        "passed": ex4_score >= 5  # 50% threshold
    }
    
    # Calculate overall results
    total_score = ex1_score + ex2_score + ex3_score + ex4_score
    results["points_achieved"] = total_score
    results["overall_score"] = (total_score / 40) * 100
    
    # Determine if candidate passed
    min_score_requirement = total_score >= 28  # 70% overall
    min_exercise_requirement = all(results["exercises"][ex]["passed"] for ex in results["exercises"])
    results["passed"] = min_score_requirement and min_exercise_requirement
    
    if results["passed"]:
        results["result"] = "PASS"
    else:
        results["result"] = "FAIL"
    
    return results

def main():
    # Load the candidate submission and answer key
    candidate = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not candidate or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(candidate, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {results['result']}")

if __name__ == "__main__":
    main()