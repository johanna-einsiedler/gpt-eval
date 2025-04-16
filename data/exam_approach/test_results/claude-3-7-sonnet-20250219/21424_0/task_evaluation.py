#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_part1(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 45,
        "details": {}
    }
    
    for claim_id in ["claim001", "claim002", "claim003"]:
        claim_results = {"points_earned": 0, "points_possible": 15, "details": {}}
        
        # Skip if claim is missing in submission
        if claim_id not in submission:
            claim_results["details"]["error"] = f"Missing {claim_id} in submission"
            results["details"][claim_id] = claim_results
            continue
            
        sub_claim = submission[claim_id]
        key_claim = answer_key[claim_id]
        
        # Indemnity Reserve (8 points)
        indemnity_points = 0
        tolerance = 0.05  # 5% for claim001 and claim002
        if claim_id == "claim003":
            tolerance = 0.10  # 10% for claim003
            
        if "indemnityReserve" in sub_claim:
            sub_indemnity = float(sub_claim["indemnityReserve"])
            key_indemnity = float(key_claim["indemnityReserve"])
            
            percentage_diff = abs((sub_indemnity - key_indemnity) / key_indemnity)
            if percentage_diff <= tolerance:
                indemnity_points = 8
            else:
                indemnity_points = math.floor(8 * (1 - percentage_diff / (2 * tolerance)))
                indemnity_points = max(0, indemnity_points)
                
            claim_results["details"]["indemnityReserve"] = {
                "submitted": sub_indemnity,
                "expected": key_indemnity,
                "diff_percentage": round(percentage_diff * 100, 2),
                "points_earned": indemnity_points,
                "points_possible": 8
            }
        else:
            claim_results["details"]["indemnityReserve"] = {
                "error": "Missing indemnityReserve",
                "points_earned": 0,
                "points_possible": 8
            }
            
        # Expense Reserve (4 points)
        expense_points = 0
        if "expenseReserve" in sub_claim:
            sub_expense = float(sub_claim["expenseReserve"])
            key_expense = float(key_claim["expenseReserve"])
            
            percentage_diff = abs((sub_expense - key_expense) / key_expense)
            if percentage_diff <= 0.05:  # 5% tolerance
                expense_points = 4
            else:
                expense_points = math.floor(4 * (1 - percentage_diff / 0.1))
                expense_points = max(0, expense_points)
                
            claim_results["details"]["expenseReserve"] = {
                "submitted": sub_expense,
                "expected": key_expense,
                "diff_percentage": round(percentage_diff * 100, 2),
                "points_earned": expense_points,
                "points_possible": 4
            }
        else:
            claim_results["details"]["expenseReserve"] = {
                "error": "Missing expenseReserve",
                "points_earned": 0,
                "points_possible": 4
            }
            
        # Policy Reference (3 points)
        policy_points = 0
        if "policyReference" in sub_claim:
            sub_policy = sub_claim["policyReference"]
            key_policy = key_claim["policyReference"]
            
            if sub_policy == key_policy:
                policy_points = 3
                
            claim_results["details"]["policyReference"] = {
                "submitted": sub_policy,
                "expected": key_policy,
                "points_earned": policy_points,
                "points_possible": 3
            }
        else:
            claim_results["details"]["policyReference"] = {
                "error": "Missing policyReference",
                "points_earned": 0,
                "points_possible": 3
            }
            
        claim_results["points_earned"] = indemnity_points + expense_points + policy_points
        results["points_earned"] += claim_results["points_earned"]
        results["details"][claim_id] = claim_results
        
    return results

def evaluate_part2(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "details": {}
    }
    
    # Check if adjustedClaims exists in submission
    if "adjustedClaims" not in submission:
        results["details"]["error"] = "Missing adjustedClaims in submission"
        return results
        
    # Create dictionary of answer key claims for easier lookup
    key_claims = {claim["claimId"]: claim for claim in answer_key["adjustedClaims"]}
    sub_claims = {claim["claimId"]: claim for claim in submission["adjustedClaims"]}
    
    identified_claims = set(sub_claims.keys())
    required_claims = set(key_claims.keys())
    
    # Check if submission identified all 15 claims (2 points each for identification)
    identification_points = 0
    for claim_id in required_claims:
        if claim_id in identified_claims:
            identification_points += 2
    
    results["details"]["claim_identification"] = {
        "points_earned": identification_points,
        "points_possible": 30,
        "submitted_count": len(identified_claims),
        "expected_count": len(required_claims),
        "missing_claims": list(required_claims - identified_claims),
        "extra_claims": list(identified_claims - required_claims)
    }
    
    # Evaluate each claim that was included in the submission
    claim_points = 0
    claim_evaluations = {}
    
    for claim_id in identified_claims:
        claim_eval = {"points_earned": 0, "points_possible": 2}
        
        # Skip if not in answer key (shouldn't happen if we checked correctly)
        if claim_id not in key_claims:
            claim_eval["error"] = "Claim not in answer key"
            claim_evaluations[claim_id] = claim_eval
            continue
            
        sub_claim = sub_claims[claim_id]
        key_claim = key_claims[claim_id]
        
        # Direction of adjustment (0.5 point)
        sub_original = float(sub_claim.get("originalReserve", 0))
        sub_adjusted = float(sub_claim.get("adjustedReserve", 0))
        key_original = float(key_claim.get("originalReserve", 0))
        key_adjusted = float(key_claim.get("adjustedReserve", 0))
        
        sub_direction = sub_adjusted > sub_original
        key_direction = key_adjusted > key_original
        
        direction_points = 0.5 if sub_direction == key_direction else 0
        
        # Value within tolerance (0.5 point)
        value_points = 0
        if "adjustedReserve" in sub_claim:
            percentage_diff = abs((sub_adjusted - key_adjusted) / key_adjusted)
            if percentage_diff <= 0.15:  # 15% tolerance
                value_points = 0.5
                
        # Reason code (1 point)
        reason_points = 0
        if "reasonCode" in sub_claim and sub_claim["reasonCode"] == key_claim["reasonCode"]:
            reason_points = 1
            
        claim_eval["points_earned"] = direction_points + value_points + reason_points
        claim_eval["details"] = {
            "direction": {
                "submitted": "increase" if sub_direction else "decrease",
                "expected": "increase" if key_direction else "decrease",
                "points": direction_points
            },
            "value": {
                "submitted": sub_adjusted,
                "expected": key_adjusted,
                "diff_percentage": round(percentage_diff * 100, 2) if "adjustedReserve" in sub_claim else "N/A",
                "points": value_points
            },
            "reason_code": {
                "submitted": sub_claim.get("reasonCode", "Missing"),
                "expected": key_claim["reasonCode"],
                "points": reason_points
            }
        }
        
        claim_points += claim_eval["points_earned"]
        claim_evaluations[claim_id] = claim_eval
    
    # Critical error check: if more than 5 claims are missing, it's an automatic failure
    critical_error = None
    if len(required_claims - identified_claims) > 5:
        critical_error = "Missed more than 5 claims that require adjustment"
    
    # Check for direction reversal critical error
    direction_errors = []
    for claim_id in identified_claims.intersection(required_claims):
        sub_claim = sub_claims[claim_id]
        key_claim = key_claims[claim_id]
        
        sub_original = float(sub_claim.get("originalReserve", 0))
        sub_adjusted = float(sub_claim.get("adjustedReserve", 0))
        key_original = float(key_claim.get("originalReserve", 0))
        key_adjusted = float(key_claim.get("adjustedReserve", 0))
        
        sub_direction = sub_adjusted > sub_original
        key_direction = key_adjusted > key_original
        
        if sub_direction != key_direction:
            direction_errors.append(claim_id)
    
    if direction_errors:
        if not critical_error:
            critical_error = "Increasing reserves when they should be decreased or vice versa"
        results["details"]["direction_errors"] = direction_errors
    
    if critical_error:
        results["critical_error"] = critical_error
    
    # Final part2 score (identification score already included in identification_points)
    results["points_earned"] = identification_points
    results["details"]["claim_evaluations"] = claim_evaluations
    
    return results

def evaluate_part3(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 25,
        "details": {}
    }
    
    # Check if recommendations exists in submission
    if "recommendations" not in submission:
        results["details"]["error"] = "Missing recommendations in submission"
        return results
    
    # Get the three largest percentage change claims from answer key
    key_recommendations = answer_key["recommendations"]
    key_claim_ids = {rec["claimId"] for rec in key_recommendations}
    
    # Check which of the correct claims the candidate identified
    sub_recommendations = submission["recommendations"]
    sub_claim_ids = {rec["claimId"] for rec in sub_recommendations if "claimId" in rec}
    
    # Score for correctly identifying the three claims (5 points each)
    identification_points = 0
    for claim_id in key_claim_ids:
        if claim_id in sub_claim_ids:
            identification_points += 5
    
    results["details"]["claim_identification"] = {
        "points_earned": identification_points,
        "points_possible": 15,
        "expected_claims": list(key_claim_ids),
        "submitted_claims": list(sub_claim_ids),
        "correct_claims": list(key_claim_ids.intersection(sub_claim_ids)),
        "incorrect_claims": list(sub_claim_ids - key_claim_ids)
    }
    
    # Create dictionaries for easier lookup
    key_recs = {rec["claimId"]: rec for rec in key_recommendations}
    sub_recs = {rec["claimId"]: rec for rec in sub_recommendations if "claimId" in rec}
    
    # Evaluate each recommendation that was included in the submission and is one of the correct ones
    detail_points = 0
    rec_evaluations = {}
    
    for claim_id in key_claim_ids.intersection(sub_claim_ids):
        rec_eval = {"points_earned": 0, "points_possible": 3.5}
        
        sub_rec = sub_recs[claim_id]
        key_rec = key_recs[claim_id]
        
        # Reserve values match Part 2 (1 point)
        reserve_match = False
        if ("currentReserve" in sub_rec and "recommendedReserve" in sub_rec and
            abs(float(sub_rec["currentReserve"]) - float(key_rec["currentReserve"])) < 0.01 and
            abs(float(sub_rec["recommendedReserve"]) - float(key_rec["recommendedReserve"])) < 0.01):
            reserve_match = True
            
        # Policy section reference (1.5 points)
        policy_match = False
        if "policySection" in sub_rec and sub_rec["policySection"] == key_rec["policySection"]:
            policy_match = True
            
        # Change category (1 point)
        category_match = False
        if "changeCategory" in sub_rec and sub_rec["changeCategory"] == key_rec["changeCategory"]:
            category_match = True
            
        rec_eval["points_earned"] = (1 if reserve_match else 0) + (1.5 if policy_match else 0) + (1 if category_match else 0)
        rec_eval["details"] = {
            "reserve_values": {
                "submitted": {
                    "current": sub_rec.get("currentReserve", "Missing"),
                    "recommended": sub_rec.get("recommendedReserve", "Missing")
                },
                "expected": {
                    "current": key_rec["currentReserve"],
                    "recommended": key_rec["recommendedReserve"]
                },
                "match": reserve_match,
                "points": 1 if reserve_match else 0
            },
            "policy_section": {
                "submitted": sub_rec.get("policySection", "Missing"),
                "expected": key_rec["policySection"],
                "match": policy_match,
                "points": 1.5 if policy_match else 0
            },
            "change_category": {
                "submitted": sub_rec.get("changeCategory", "Missing"),
                "expected": key_rec["changeCategory"],
                "match": category_match,
                "points": 1 if category_match else 0
            }
        }
        
        detail_points += rec_eval["points_earned"]
        rec_evaluations[claim_id] = rec_eval
    
    results["points_earned"] = identification_points + detail_points
    results["details"]["recommendation_evaluations"] = rec_evaluations
    
    return results

def evaluate_submission(submission, answer_key):
    # Initialize results dictionary
    results = {
        "overall_score": 0,
        "points_earned": 0,
        "points_possible": 100,
        "pass_status": None,
        "parts": {}
    }
    
    # Check if submission has the necessary structure
    if "part1" not in submission or "part2" not in submission or "part3" not in submission:
        results["error"] = "Submission missing one or more required parts"
        results["pass_status"] = "Fail"
        return results
    
    # Evaluate each part
    part1_results = evaluate_part1(submission["part1"], answer_key["part1"])
    part2_results = evaluate_part2(submission["part2"], answer_key["part2"])
    part3_results = evaluate_part3(submission["part3"], answer_key["part3"])
    
    # Add results to the main dictionary
    results["parts"]["part1"] = part1_results
    results["parts"]["part2"] = part2_results
    results["parts"]["part3"] = part3_results
    
    # Calculate total points
    total_earned = part1_results["points_earned"] + part2_results["points_earned"] + part3_results["points_earned"]
    total_possible = part1_results["points_possible"] + part2_results["points_possible"] + part3_results["points_possible"]
    
    results["points_earned"] = total_earned
    
    # Check for critical errors that cause automatic failure
    if "critical_error" in part2_results:
        results["critical_error"] = part2_results["critical_error"]
        results["pass_status"] = "Fail"
    else:
        # Determine pass status
        if total_earned >= 80:
            results["pass_status"] = "Pass"
        elif total_earned >= 65:
            results["pass_status"] = "Conditional Pass"
        else:
            results["pass_status"] = "Fail"
    
    # Calculate overall percentage score
    results["overall_score"] = round((total_earned / total_possible) * 100, 2)
    
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
    print(f"Pass status: {results['pass_status']}")

if __name__ == "__main__":
    main()