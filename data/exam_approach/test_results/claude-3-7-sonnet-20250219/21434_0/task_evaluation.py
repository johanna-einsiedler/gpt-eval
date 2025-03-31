import json
import os

def validate_submission(submission, answer_key):
    score = 0
    max_score = 100
    
    # Exercise 1 validation (50 points)
    ex1_score = 0
    max_ex1_score = 50
    
    # Validate settled claims (40 points)
    for i, claim in enumerate(submission["exercise1"]["settled_claims"]):
        key_claim = answer_key["exercise1"]["settled_claims"][i]
        
        # Exact match fields (1 point each)
        exact_fields = ["claim_number", "claimant_name", "date_of_loss", 
                        "date_of_settlement", "coverage_type", "claim_handler", 
                        "settlement_method", "subrogation_potential", "final_disposition_code"]
        
        for field in exact_fields:
            if claim[field] == key_claim[field]:
                ex1_score += 1
        
        # Settlement amount (within $0.01)
        if abs(claim["settlement_amount"] - key_claim["settlement_amount"]) <= 0.01:
            ex1_score += 1
    
    # Validate summary (10 points)
    summary = submission["exercise1"]["summary"]
    key_summary = answer_key["exercise1"]["summary"]
    
    # Exact match fields (2 points each)
    if summary["total_claims"] == key_summary["total_claims"]:
        ex1_score += 2
    
    if summary["oldest_settlement_date"] == key_summary["oldest_settlement_date"]:
        ex1_score += 2
        
    if summary["most_recent_settlement_date"] == key_summary["most_recent_settlement_date"]:
        ex1_score += 2
    
    # Flexible range fields (2 points each)
    if abs(summary["total_settlement_amount"] - key_summary["total_settlement_amount"]) <= 0.01:
        ex1_score += 2
        
    if abs(summary["average_settlement_amount"] - key_summary["average_settlement_amount"]) <= 0.01:
        ex1_score += 2
    
    # Exercise 2 validation (50 points)
    ex2_score = 0
    max_ex2_score = 50
    
    # Validate claim inventory (35 points)
    for i, claim in enumerate(submission["exercise2"]["claim_inventory"]):
        key_claim = answer_key["exercise2"]["claim_inventory"][i]
        
        # Exact match fields (1 point each)
        if claim["claim_number"] == key_claim["claim_number"]:
            ex2_score += 1
            
        if claim["complexity_level"] == key_claim["complexity_level"]:
            ex2_score += 1
            
        if claim["analysis_type"] == key_claim["analysis_type"]:
            ex2_score += 1
            
        if claim["next_action"] == key_claim["next_action"]:
            ex2_score += 1
            
        if claim["action_due_date"] == key_claim["action_due_date"]:
            ex2_score += 1
            
        if claim["priority_code"] == key_claim["priority_code"]:
            ex2_score += 1
        
        # Flexible range fields
        if abs(claim["estimated_completion_days"] - key_claim["estimated_completion_days"]) <= 10:
            ex2_score += 1
        
        # Missing documentation (check if all required items are present, order doesn't matter)
        missing_docs_match = True
        if len(claim["missing_documentation"]) != len(key_claim["missing_documentation"]):
            missing_docs_match = False
        else:
            for doc in key_claim["missing_documentation"]:
                if doc not in claim["missing_documentation"]:
                    missing_docs_match = False
                    break
        
        if missing_docs_match:
            ex2_score += 1
    
    # Validate detailed analysis claims (15 points)
    submitted_claims = {c["claim_number"]: c for c in submission["exercise2"]["detailed_analysis_claims"]}
    key_claims = {c["claim_number"]: c for c in answer_key["exercise2"]["detailed_analysis_claims"]}
    
    # Check if the correct claims are identified (5 points)
    for claim_number in key_claims:
        if claim_number in submitted_claims:
            ex2_score += 2.5  # Correct identification
            
            # Check reason (2.5 points)
            # This is subjective - we'll check if key terms are present
            key_terms = ["complexity", "reserve", "exceeds $50,000"]
            reason_score = 0
            for term in key_terms:
                if term.lower() in submitted_claims[claim_number]["reason_for_detailed_analysis"].lower():
                    reason_score += 0.83  # 2.5 points divided by 3 terms
            
            ex2_score += min(reason_score, 2.5)
            
            # Check hours (2.5 points)
            if abs(submitted_claims[claim_number]["estimated_hours_needed"] - key_claims[claim_number]["estimated_hours_needed"]) <= 5:
                ex2_score += 2.5
    
    # Calculate total score
    score = ex1_score + ex2_score
    
    # Calculate percentage score
    percentage_score = (score / max_score) * 100
    
    # Determine if passed
    passed = score >= 80 and ex1_score >= 35 and ex2_score >= 35
    
    return {
        "total_score": score,
        "exercise1_score": ex1_score,
        "exercise2_score": ex2_score,
        "max_score": max_score,
        "max_exercise1_score": max_ex1_score,
        "max_exercise2_score": max_ex2_score,
        "overall_score": percentage_score,
        "passed": passed,
        "detailed_results": {
            "exercise1": {
                "settled_claims_score": ex1_score - (
                    2 if summary["total_claims"] == key_summary["total_claims"] else 0
                ) - (
                    2 if summary["oldest_settlement_date"] == key_summary["oldest_settlement_date"] else 0
                ) - (
                    2 if summary["most_recent_settlement_date"] == key_summary["most_recent_settlement_date"] else 0
                ) - (
                    2 if abs(summary["total_settlement_amount"] - key_summary["total_settlement_amount"]) <= 0.01 else 0
                ) - (
                    2 if abs(summary["average_settlement_amount"] - key_summary["average_settlement_amount"]) <= 0.01 else 0
                ),
                "summary_score": (
                    2 if summary["total_claims"] == key_summary["total_claims"] else 0
                ) + (
                    2 if summary["oldest_settlement_date"] == key_summary["oldest_settlement_date"] else 0
                ) + (
                    2 if summary["most_recent_settlement_date"] == key_summary["most_recent_settlement_date"] else 0
                ) + (
                    2 if abs(summary["total_settlement_amount"] - key_summary["total_settlement_amount"]) <= 0.01 else 0
                ) + (
                    2 if abs(summary["average_settlement_amount"] - key_summary["average_settlement_amount"]) <= 0.01 else 0
                )
            },
            "exercise2": {
                "claim_inventory_score": ex2_score - sum(
                    2.5 + min(sum(0.83 for term in ["complexity", "reserve", "exceeds $50,000"] 
                                 if term.lower() in submitted_claims[claim_number]["reason_for_detailed_analysis"].lower()), 2.5) + 
                    (2.5 if abs(submitted_claims[claim_number]["estimated_hours_needed"] - key_claims[claim_number]["estimated_hours_needed"]) <= 5 else 0)
                    for claim_number in key_claims if claim_number in submitted_claims
                ),
                "detailed_analysis_score": sum(
                    2.5 + min(sum(0.83 for term in ["complexity", "reserve", "exceeds $50,000"] 
                                 if term.lower() in submitted_claims[claim_number]["reason_for_detailed_analysis"].lower()), 2.5) + 
                    (2.5 if abs(submitted_claims[claim_number]["estimated_hours_needed"] - key_claims[claim_number]["estimated_hours_needed"]) <= 5 else 0)
                    for claim_number in key_claims if claim_number in submitted_claims
                )
            }
        }
    }

def main():
    # Check if files exist
    if not os.path.exists('test_submission.json'):
        print("Error: test_submission.json not found")
        return
    
    if not os.path.exists('answer_key.json'):
        print("Error: answer_key.json not found")
        return
    
    # Load submission and answer key
    try:
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    except Exception as e:
        print(f"Error loading files: {e}")
        return
    
    # Validate submission
    results = validate_submission(submission, answer_key)
    
    # Save results
    try:
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Evaluation complete. Results saved to test_results.json")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()