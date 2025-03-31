import json
import os

def load_json(filename):
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def evaluate_referral_decisions(submission, answer_key):
    """Evaluate the correctness of referral decisions."""
    results = {
        "points_earned": 0,
        "points_possible": 10,
        "details": []
    }
    
    # Create a mapping of claim_id to answer key data for easier lookup
    answer_key_map = {item["claim_id"]: item for item in answer_key["submissions"]}
    
    for item in submission["submissions"]:
        claim_id = item["claim_id"]
        if claim_id in answer_key_map:
            correct_decision = answer_key_map[claim_id]["refer_for_investigation"]
            candidate_decision = item["refer_for_investigation"]
            is_correct = candidate_decision == correct_decision
            
            detail = {
                "claim_id": claim_id,
                "candidate_decision": candidate_decision,
                "correct_decision": correct_decision,
                "is_correct": is_correct,
                "points_earned": 1 if is_correct else 0
            }
            
            results["details"].append(detail)
            if is_correct:
                results["points_earned"] += 1
    
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    return results

def evaluate_red_flags(submission, answer_key):
    """Evaluate the identification of red flags."""
    results = {
        "points_earned": 0,
        "points_possible": 7,  # 7 claims requiring investigation
        "details": []
    }
    
    # Create a mapping of claim_id to answer key data for easier lookup
    answer_key_map = {item["claim_id"]: item for item in answer_key["submissions"]}
    
    # Filter for claims that should be referred according to answer key
    referred_claims = [item for item in answer_key["submissions"] if item["refer_for_investigation"]]
    
    for answer_item in referred_claims:
        claim_id = answer_item["claim_id"]
        correct_red_flags = set(flag.lower() for flag in answer_item["red_flags"])
        
        # Find corresponding submission item
        submission_item = next((item for item in submission["submissions"] if item["claim_id"] == claim_id), None)
        
        if submission_item:
            candidate_red_flags = set(flag.lower() for flag in submission_item["red_flags"])
            
            # Count matches
            matches = 0
            for candidate_flag in candidate_red_flags:
                # Check if any correct flag is substantially similar to the candidate flag
                if any(correct_flag in candidate_flag or candidate_flag in correct_flag for correct_flag in correct_red_flags):
                    matches += 1
            
            # Calculate percentage of correct flags identified
            correct_flag_count = len(correct_red_flags)
            percentage_identified = (matches / correct_flag_count) * 100 if correct_flag_count > 0 else 0
            
            # Assign points based on percentage
            points = 0
            if percentage_identified >= 50:
                points = 1
            elif percentage_identified >= 25:
                points = 0.5
            
            detail = {
                "claim_id": claim_id,
                "correct_red_flags": list(answer_item["red_flags"]),
                "candidate_red_flags": list(submission_item["red_flags"]),
                "matches": matches,
                "percentage_identified": percentage_identified,
                "points_earned": points
            }
            
            results["details"].append(detail)
            results["points_earned"] += points
    
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    return results

def evaluate_justifications(submission, answer_key):
    """Evaluate the quality of justifications."""
    results = {
        "points_earned": 0,
        "points_possible": 30,  # 3 points per claim × 10 claims
        "details": []
    }
    
    # Create a mapping of claim_id to answer key data for easier lookup
    answer_key_map = {item["claim_id"]: item for item in answer_key["submissions"]}
    
    for item in submission["submissions"]:
        claim_id = item["claim_id"]
        if claim_id in answer_key_map:
            answer_item = answer_key_map[claim_id]
            
            # Check if justification references specific claim details
            # This is a simplified check - in a real system, this would be more sophisticated
            references_details = len(item["justification"]) > 50  # Basic length check
            
            # Check if justification correctly applies company guidelines
            # This is a simplified check - in a real system, this would be more sophisticated
            applies_guidelines = "guidelines" in item["justification"].lower() or "policy" in item["justification"].lower()
            
            # Check if justification logically supports the referral decision
            # This is a simplified check - in a real system, this would be more sophisticated
            supports_decision = item["refer_for_investigation"] == answer_item["refer_for_investigation"]
            
            points = (1 if references_details else 0) + (1 if applies_guidelines else 0) + (1 if supports_decision else 0)
            
            detail = {
                "claim_id": claim_id,
                "references_details": references_details,
                "applies_guidelines": applies_guidelines,
                "supports_decision": supports_decision,
                "points_earned": points
            }
            
            results["details"].append(detail)
            results["points_earned"] += points
    
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    return results

def evaluate_priority_levels(submission, answer_key):
    """Evaluate the correctness of priority level assignments."""
    results = {
        "points_earned": 0,
        "points_possible": 7,  # 7 claims requiring investigation
        "details": []
    }
    
    # Filter for claims that should be referred according to answer key
    referred_claims = [item for item in answer_key["submissions"] if item["refer_for_investigation"]]
    
    # Create a mapping of claim_id to submission data for easier lookup
    submission_map = {item["claim_id"]: item for item in submission["submissions"]}
    
    for answer_item in referred_claims:
        claim_id = answer_item["claim_id"]
        correct_priority = answer_item["priority_level"]
        
        if claim_id in submission_map:
            submission_item = submission_map[claim_id]
            candidate_priority = submission_item.get("priority_level")
            
            # Calculate points based on how close the priority level is
            points = 0
            if candidate_priority == correct_priority:
                points = 1
            elif candidate_priority is not None and abs(candidate_priority - correct_priority) == 1:
                points = 0.5
            
            detail = {
                "claim_id": claim_id,
                "candidate_priority": candidate_priority,
                "correct_priority": correct_priority,
                "points_earned": points
            }
            
            results["details"].append(detail)
            results["points_earned"] += points
    
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    return results

def evaluate_routing_codes(submission, answer_key):
    """Evaluate the correctness of routing code assignments."""
    results = {
        "points_earned": 0,
        "points_possible": 7,  # 7 claims requiring investigation
        "details": []
    }
    
    # Filter for claims that should be referred according to answer key
    referred_claims = [item for item in answer_key["submissions"] if item["refer_for_investigation"]]
    
    # Create a mapping of claim_id to submission data for easier lookup
    submission_map = {item["claim_id"]: item for item in submission["submissions"]}
    
    for answer_item in referred_claims:
        claim_id = answer_item["claim_id"]
        correct_code = answer_item["routing_code"]
        
        if claim_id in submission_map:
            submission_item = submission_map[claim_id]
            candidate_code = submission_item.get("routing_code")
            
            # Check if routing code is correct
            is_correct = candidate_code == correct_code
            
            detail = {
                "claim_id": claim_id,
                "candidate_code": candidate_code,
                "correct_code": correct_code,
                "is_correct": is_correct,
                "points_earned": 1 if is_correct else 0
            }
            
            results["details"].append(detail)
            if is_correct:
                results["points_earned"] += 1
    
    results["percentage"] = (results["points_earned"] / results["points_possible"]) * 100
    return results

def evaluate_submission():
    """Main function to evaluate the candidate's submission."""
    # Load the submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Perform evaluations
    referral_results = evaluate_referral_decisions(submission, answer_key)
    red_flag_results = evaluate_red_flags(submission, answer_key)
    justification_results = evaluate_justifications(submission, answer_key)
    priority_results = evaluate_priority_levels(submission, answer_key)
    routing_results = evaluate_routing_codes(submission, answer_key)
    
    # Calculate overall score
    total_points_earned = (
        referral_results["points_earned"] +
        red_flag_results["points_earned"] +
        justification_results["points_earned"] +
        priority_results["points_earned"] +
        routing_results["points_earned"]
    )
    
    total_points_possible = (
        referral_results["points_possible"] +
        red_flag_results["points_possible"] +
        justification_results["points_possible"] +
        priority_results["points_possible"] +
        routing_results["points_possible"]
    )
    
    overall_percentage = (total_points_earned / total_points_possible) * 100
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_percentage,
        "passing_score": 75,
        "passed": overall_percentage >= 75,
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "evaluation_areas": {
            "referral_decisions": referral_results,
            "red_flag_identification": red_flag_results,
            "justification_quality": justification_results,
            "priority_level_assignment": priority_results,
            "routing_code_assignment": routing_results
        }
    }
    
    # Save results
    save_json(results, "test_results.json")

if __name__ == "__main__":
    evaluate_submission()