#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)


def evaluate_referral_decision(candidate_answer, correct_answer, claim_number):
    """Evaluate if the candidate made the correct referral decision"""
    score = 0
    max_score = 5
    
    feedback = ""
    if candidate_answer == correct_answer:
        score = max_score
        feedback = "Correct referral decision"
    else:
        feedback = f"Incorrect referral decision. Expected: {correct_answer}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }


def evaluate_red_flags(candidate_flags, correct_flags, claim_number):
    """Evaluate if the candidate identified the correct red flags"""
    score = 0
    max_score = 7
    
    # Normalize the format of red flags for comparison
    normalized_candidate_flags = [flag.split(':')[0].strip() for flag in candidate_flags]
    normalized_correct_flags = [flag.split(':')[0].strip() for flag in correct_flags]
    
    # Count matching red flags
    matched_flags = set(normalized_candidate_flags) & set(normalized_correct_flags)
    matched_count = len(matched_flags)
    
    # Determine if critical red flags were identified
    key_flags_identified = len(matched_flags) >= 2
    critical_flags_missed = []
    
    for flag in normalized_correct_flags:
        if flag not in normalized_candidate_flags:
            critical_flags_missed.append(flag)
    
    # Score based on the number of key red flags identified
    if matched_count >= 3:
        score = 7  # Identified all major red flags (3+ keys)
        feedback = "Excellent job identifying all major red flags"
    elif matched_count >= 2 and key_flags_identified:
        score = 5  # Identified most major red flags (2+ keys, including most critical)
        feedback = "Good job identifying most major red flags, but missed some"
    elif matched_count > 0:
        score = 3  # Identified some red flags but missed critical ones
        feedback = "Identified some red flags but missed critical ones"
    else:
        score = 0  # Failed to identify any valid red flags
        feedback = "Failed to identify any valid red flags"
    
    feedback += f"\nCorrectly identified: {matched_count}/{len(normalized_correct_flags)} red flags"
    if critical_flags_missed:
        feedback += f"\nMissed critical flags: {', '.join(critical_flags_missed)}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback,
        "matched_flags": list(matched_flags),
        "missed_flags": critical_flags_missed
    }


def evaluate_referral_destination(candidate_destination, correct_destination, claim_number):
    """Evaluate if the candidate chose the correct referral destination"""
    score = 0
    max_score = 3
    
    feedback = ""
    if candidate_destination.lower() == correct_destination.lower():
        score = max_score
        feedback = "Correct referral destination"
    else:
        feedback = f"Incorrect referral destination. Expected: {correct_destination}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }


def evaluate_justification(candidate_justification, red_flags_result, claim_number):
    """Evaluate the quality of the candidate's justification"""
    score = 0
    max_score = 5
    
    # Calculate a preliminary score based on word count and matched red flags
    word_count = len(candidate_justification.split())
    matched_flags_count = len(red_flags_result.get("matched_flags", []))
    
    if word_count < 100:
        preliminary_score = 1  # Very brief justification
    elif word_count < 150:
        preliminary_score = 2  # Brief justification
    elif word_count < 200:
        preliminary_score = 3  # Adequate justification
    else:
        preliminary_score = 4  # Comprehensive justification
    
    # Adjust score based on how many red flags were correctly identified
    if matched_flags_count >= 3 and preliminary_score >= 3:
        score = 5  # Comprehensive justification with specific evidence cited from multiple documents
        feedback = "Excellent comprehensive justification with specific evidence cited"
    elif matched_flags_count >= 2 and preliminary_score >= 2:
        score = 3  # Adequate justification with some specific evidence cited
        feedback = "Adequate justification with some specific evidence cited"
    elif matched_flags_count >= 1:
        score = 1  # Basic justification with minimal evidence
        feedback = "Basic justification with minimal evidence"
    else:
        score = 0  # Vague justification or no evidence cited
        feedback = "Vague justification or insufficient evidence cited"
    
    feedback += f"\nWord count: {word_count} words"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }


def evaluate_claim(candidate_claim, correct_claim, claim_number):
    """Evaluate a single claim"""
    results = {}
    
    # Evaluate referral decision
    results["referral_decision"] = evaluate_referral_decision(
        candidate_claim.get("requires_referral", False),
        correct_claim.get("requires_referral", True),
        claim_number
    )
    
    # Evaluate red flags
    results["red_flags"] = evaluate_red_flags(
        candidate_claim.get("red_flags", []),
        correct_claim.get("red_flags", []),
        claim_number
    )
    
    # Evaluate referral destination
    results["referral_destination"] = evaluate_referral_destination(
        candidate_claim.get("referral_destination", ""),
        correct_claim.get("referral_destination", "investigation"),
        claim_number
    )
    
    # Evaluate justification
    results["justification"] = evaluate_justification(
        candidate_claim.get("justification", ""),
        results["red_flags"],
        claim_number
    )
    
    # Calculate total score for this claim
    total_score = (
        results["referral_decision"]["score"] +
        results["red_flags"]["score"] +
        results["referral_destination"]["score"] +
        results["justification"]["score"]
    )
    
    max_score = (
        results["referral_decision"]["max_score"] +
        results["red_flags"]["max_score"] +
        results["referral_destination"]["max_score"] +
        results["justification"]["max_score"]
    )
    
    results["total_score"] = total_score
    results["max_score"] = max_score
    results["percentage"] = round((total_score / max_score) * 100, 2)
    
    return results


def check_critical_failures(evaluation_results):
    """Check for any critical failures that would result in automatic failure"""
    critical_failures = []
    
    # Count incorrect referral decisions
    incorrect_referrals = 0
    for claim_number, claim_results in evaluation_results.items():
        if claim_results["referral_decision"]["score"] == 0:
            incorrect_referrals += 1
    
    if incorrect_referrals >= 2:
        critical_failures.append("Identified 2 or more claims as 'does not require referral' when clear fraud indicators exist")
    
    # Count claims where no valid red flags were identified
    claims_without_flags = 0
    for claim_number, claim_results in evaluation_results.items():
        if len(claim_results["red_flags"].get("matched_flags", [])) == 0:
            claims_without_flags += 1
    
    if claims_without_flags >= 2:
        critical_failures.append("Failed to identify any valid red flags in 2 or more scenarios")
    
    # Count claims with incorrect referral destination
    incorrect_destinations = 0
    for claim_number, claim_results in evaluation_results.items():
        if claim_results["referral_destination"]["score"] == 0:
            incorrect_destinations += 1
    
    if incorrect_destinations >= 2:
        critical_failures.append("Referred 2 or more claims to settlement rather than investigation when multiple fraud indicators are present")
    
    # Count claims with inadequate justification
    inadequate_justifications = 0
    for claim_number, claim_results in evaluation_results.items():
        if claim_results["justification"]["score"] < 3:
            inadequate_justifications += 1
    
    if inadequate_justifications >= 2:
        critical_failures.append("Provided inadequate justification for 2 or more claims")
    
    return critical_failures


def generate_overall_assessment(total_score, max_score, critical_failures):
    """Generate an overall assessment based on the score and critical failures"""
    percentage = (total_score / max_score) * 100
    
    if critical_failures:
        assessment = "FAILING"
        reason = "Critical failures detected: " + "; ".join(critical_failures)
    elif percentage >= 90:
        assessment = "EXCELLENT"
        reason = "Demonstrated exceptional ability to identify and properly refer questionable claims."
    elif percentage >= 80:
        assessment = "GOOD"
        reason = "Demonstrated strong ability to identify and properly refer questionable claims."
    elif percentage >= 70:
        assessment = "SATISFACTORY"
        reason = "Demonstrated adequate ability to identify and properly refer questionable claims."
    elif percentage >= 60:
        assessment = "NEEDS IMPROVEMENT"
        reason = "Demonstrated limited ability to identify and properly refer questionable claims."
    else:
        assessment = "FAILING"
        reason = "Failed to demonstrate ability to identify and properly refer questionable claims."
    
    return {
        "assessment": assessment,
        "reason": reason
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the candidate submission and answer key
    candidate_submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Extract claims from both files
    candidate_claims = {claim["claim_number"]: claim for claim in candidate_submission.get("claim_referrals", [])}
    correct_claims = {claim["claim_number"]: claim for claim in answer_key.get("claim_referrals", [])}
    
    # Evaluate each claim
    evaluation_results = {}
    for claim_number, correct_claim in correct_claims.items():
        candidate_claim = candidate_claims.get(claim_number, {})
        evaluation_results[claim_number] = evaluate_claim(candidate_claim, correct_claim, claim_number)
    
    # Calculate total scores
    total_score = sum(claim_result["total_score"] for claim_result in evaluation_results.values())
    max_score = sum(claim_result["max_score"] for claim_result in evaluation_results.values())
    overall_percentage = round((total_score / max_score) * 100, 2)
    
    # Check for critical failures
    critical_failures = check_critical_failures(evaluation_results)
    
    # Generate overall assessment
    overall_assessment = generate_overall_assessment(total_score, max_score, critical_failures)
    
    # Prepare the final results
    final_results = {
        "candidate_name": candidate_submission.get("candidate_name", "Unknown"),
        "candidate_id": candidate_submission.get("candidate_id", "Unknown"),
        "submission_date": candidate_submission.get("submission_date", "Unknown"),
        "evaluation_date": Path(submission_file).stat().st_mtime,
        "overall_score": overall_percentage,
        "total_points": total_score,
        "max_points": max_score,
        "critical_failures": critical_failures,
        "assessment": overall_assessment["assessment"],
        "assessment_reason": overall_assessment["reason"],
        "claim_evaluations": evaluation_results
    }
    
    # Save the results to test_results.json
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall score: {overall_percentage}%")
    print(f"Assessment: {overall_assessment['assessment']}")
    if critical_failures:
        print("Critical failures detected:")
        for failure in critical_failures:
            print(f"- {failure}")


if __name__ == "__main__":
    main()