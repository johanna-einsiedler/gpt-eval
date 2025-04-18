#!/usr/bin/env python3
import json
import sys

def load_json_file(file_path):
    """Load and return JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_referral_decisions(submission, answer_key):
    """Evaluate the correctness of referral decisions (40% of score)."""
    correct_count = 0
    results = []
    
    for sub_claim, key_claim in zip(submission["claims"], answer_key["claims"]):
        claim_id = sub_claim["claim_id"]
        is_correct = sub_claim["requires_referral"] == key_claim["requires_referral"]
        
        results.append({
            "claim_id": claim_id,
            "submitted": sub_claim["requires_referral"],
            "expected": key_claim["requires_referral"],
            "is_correct": is_correct
        })
        
        if is_correct:
            correct_count += 1
    
    # Calculate score (40% of total)
    score_percentage = (correct_count / len(submission["claims"])) * 100
    weighted_score = score_percentage * 0.4
    
    return {
        "score_percentage": score_percentage,
        "weighted_score": weighted_score,
        "correct_count": correct_count,
        "total_count": len(submission["claims"]),
        "details": results
    }

def evaluate_referral_types(submission, answer_key):
    """Evaluate the correctness of referral type selections (20% of score)."""
    correct_count = 0
    total_referrals = 0
    results = []
    
    for sub_claim, key_claim in zip(submission["claims"], answer_key["claims"]):
        claim_id = sub_claim["claim_id"]
        
        # Only evaluate referral types for claims that require referral in the answer key
        if key_claim["requires_referral"]:
            total_referrals += 1
            is_correct = sub_claim["referral_type"] == key_claim["referral_type"]
            
            results.append({
                "claim_id": claim_id,
                "submitted": sub_claim["referral_type"],
                "expected": key_claim["referral_type"],
                "is_correct": is_correct
            })
            
            if is_correct:
                correct_count += 1
    
    # Calculate score (20% of total)
    score_percentage = (correct_count / total_referrals) * 100 if total_referrals > 0 else 0
    weighted_score = score_percentage * 0.2
    
    return {
        "score_percentage": score_percentage,
        "weighted_score": weighted_score,
        "correct_count": correct_count,
        "total_count": total_referrals,
        "details": results
    }

def evaluate_red_flags(submission, answer_key):
    """Evaluate the identification of red flags (25% of score)."""
    results = []
    total_key_flags = 0
    identified_key_flags = 0
    
    for sub_claim, key_claim in zip(submission["claims"], answer_key["claims"]):
        claim_id = sub_claim["claim_id"]
        
        # Count key red flags in answer key
        key_flags = set(key_claim["red_flags"])
        total_key_flags += len(key_flags)
        
        # Count correctly identified key flags
        submitted_flags = set(sub_claim["red_flags"])
        correct_flags = key_flags.intersection(submitted_flags)
        identified_key_flags += len(correct_flags)
        
        # Count irrelevant flags
        irrelevant_flags = submitted_flags - key_flags
        
        results.append({
            "claim_id": claim_id,
            "correct_flags": list(correct_flags),
            "missed_flags": list(key_flags - correct_flags),
            "irrelevant_flags": list(irrelevant_flags),
            "irrelevant_count": len(irrelevant_flags)
        })
    
    # Calculate score (25% of total)
    identification_percentage = (identified_key_flags / total_key_flags) * 100 if total_key_flags > 0 else 0
    
    # Apply penalty for irrelevant flags (max 2 per claim allowed)
    penalty = 0
    for result in results:
        if result["irrelevant_count"] > 2:
            penalty += (result["irrelevant_count"] - 2) * 5  # 5% penalty per excess irrelevant flag
    
    adjusted_percentage = max(0, identification_percentage - penalty)
    weighted_score = adjusted_percentage * 0.25
    
    return {
        "score_percentage": adjusted_percentage,
        "weighted_score": weighted_score,
        "identified_key_flags": identified_key_flags,
        "total_key_flags": total_key_flags,
        "details": results
    }

def evaluate_evidence_citation(submission, answer_key):
    """Evaluate the citation of relevant evidence (15% of score)."""
    results = []
    correct_citations_count = 0
    
    for sub_claim, key_claim in zip(submission["claims"], answer_key["claims"]):
        claim_id = sub_claim["claim_id"]
        
        # Count correctly cited evidence
        key_evidence = set(key_claim["key_evidence"])
        submitted_evidence = set(sub_claim["key_evidence"])
        correct_evidence = key_evidence.intersection(submitted_evidence)
        
        # A claim needs at least 2 correct evidence citations to be considered correct
        is_sufficient = len(correct_evidence) >= 2
        if is_sufficient:
            correct_citations_count += 1
            
        results.append({
            "claim_id": claim_id,
            "correct_evidence": list(correct_evidence),
            "missed_evidence": list(key_evidence - correct_evidence),
            "irrelevant_evidence": list(submitted_evidence - key_evidence),
            "sufficient_citations": is_sufficient
        })
    
    # Calculate score (15% of total)
    score_percentage = (correct_citations_count / len(submission["claims"])) * 100
    weighted_score = score_percentage * 0.15
    
    return {
        "score_percentage": score_percentage,
        "weighted_score": weighted_score,
        "correct_citations_count": correct_citations_count,
        "total_claims": len(submission["claims"]),
        "details": results
    }

def check_fatal_errors(submission, answer_key):
    """Check for fatal errors that would cause automatic failure."""
    fatal_errors = []
    
    # Check for failures to refer Claims 1 and 3 (which contain obvious social media contradictions)
    for i, (sub_claim, key_claim) in enumerate(zip(submission["claims"], answer_key["claims"])):
        if key_claim["claim_id"] in ["Claim-1", "Claim-3"] and key_claim["requires_referral"]:
            if not sub_claim["requires_referral"]:
                fatal_errors.append(f"Failed to refer {key_claim['claim_id']} which contains obvious social media contradictions")
    
    return fatal_errors

def evaluate_submission(submission, answer_key):
    """Evaluate the full submission and calculate overall score."""
    # Run individual evaluations
    referral_decisions = evaluate_referral_decisions(submission, answer_key)
    referral_types = evaluate_referral_types(submission, answer_key)
    red_flags = evaluate_red_flags(submission, answer_key)
    evidence = evaluate_evidence_citation(submission, answer_key)
    fatal_errors = check_fatal_errors(submission, answer_key)
    
    # Calculate overall score
    overall_score = (
        referral_decisions["weighted_score"] +
        referral_types["weighted_score"] +
        red_flags["weighted_score"] +
        evidence["weighted_score"]
    )
    
    # Check if candidate passed (minimum 75% overall score and no fatal errors)
    passed = overall_score >= 75 and not fatal_errors
    
    return {
        "candidate_id": submission["candidate_id"],
        "overall_score": overall_score,
        "passed": passed,
        "fatal_errors": fatal_errors,
        "referral_decisions": referral_decisions,
        "referral_types": referral_types,
        "red_flags": red_flags,
        "evidence_citation": evidence
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load JSON files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open('test_results.json', 'w') as outfile:
        json.dump(results, outfile, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    
    if results["fatal_errors"]:
        print("Fatal errors:")
        for error in results["fatal_errors"]:
            print(f"- {error}")

if __name__ == "__main__":
    main()