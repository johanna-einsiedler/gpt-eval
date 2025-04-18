#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any, List


def load_json(filename: str) -> Dict[str, Any]:
    """Load JSON from file."""
    with open(filename, 'r') as file:
        return json.load(file)


def evaluate_liability_determination(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the liability determination section."""
    result = {
        "section_name": "Liability Determination",
        "total_points": 20,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Primary Liability (8 points)
    primary_liability = submission.get("liability_determination", {}).get("primary_liability_percentage", 0)
    primary_points = 0
    if 75 <= primary_liability <= 85:
        primary_points = 8
    elif 65 <= primary_liability < 75 or 85 < primary_liability <= 95:
        primary_points = 4
    
    result["breakdown"]["primary_liability"] = {
        "possible_points": 8,
        "earned_points": primary_points,
        "submission_value": primary_liability,
        "expected_range": "75-85%",
        "comment": "Full points: 75-85%, Partial: 65-74% or 86-95%, None: <65% or >95%"
    }
    
    # Contributory Negligence (8 points)
    contributory = submission.get("liability_determination", {}).get("contributory_negligence_percentage", 0)
    contributory_points = 0
    if 15 <= contributory <= 25:
        contributory_points = 8
    elif 5 <= contributory < 15 or 25 < contributory <= 35:
        contributory_points = 4
    
    result["breakdown"]["contributory_negligence"] = {
        "possible_points": 8,
        "earned_points": contributory_points,
        "submission_value": contributory,
        "expected_range": "15-25%",
        "comment": "Full points: 15-25%, Partial: 5-14% or 26-35%, None: <5% or >35%"
    }
    
    # Rationale Code (4 points)
    rationale_code = submission.get("liability_determination", {}).get("liability_rationale_code", "")
    rationale_points = 0
    if rationale_code == "LR-02":
        rationale_points = 4
    elif rationale_code == "LR-03":
        rationale_points = 2
    
    result["breakdown"]["rationale_code"] = {
        "possible_points": 4,
        "earned_points": rationale_points,
        "submission_value": rationale_code,
        "expected_value": "LR-02",
        "comment": "Full points: LR-02, Partial: LR-03, None: Any other code"
    }
    
    result["points_earned"] = primary_points + contributory_points + rationale_points
    
    # Check for critical errors
    result["critical_error"] = False
    
    return result


def evaluate_coverage_analysis(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the coverage analysis section."""
    result = {
        "section_name": "Coverage Analysis",
        "total_points": 15,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Coverage Applies (5 points)
    coverage_applies = submission.get("coverage_analysis", {}).get("coverage_applies", None)
    coverage_points = 5 if coverage_applies == answer_key["coverage_analysis"]["coverage_applies"] else 0
    
    result["breakdown"]["coverage_applies"] = {
        "possible_points": 5,
        "earned_points": coverage_points,
        "submission_value": coverage_applies,
        "expected_value": answer_key["coverage_analysis"]["coverage_applies"],
        "comment": "All or nothing"
    }
    
    # Policy Section (5 points)
    policy_section = submission.get("coverage_analysis", {}).get("applicable_policy_section", None)
    policy_points = 5 if policy_section == answer_key["coverage_analysis"]["applicable_policy_section"] else 0
    
    result["breakdown"]["policy_section"] = {
        "possible_points": 5,
        "earned_points": policy_points,
        "submission_value": policy_section,
        "expected_value": answer_key["coverage_analysis"]["applicable_policy_section"],
        "comment": "All or nothing"
    }
    
    # Exclusions (5 points)
    exclusions = submission.get("coverage_analysis", {}).get("exclusions_applied", [])
    exclusion_points = 0
    
    # Check if no exclusions are applied (correct answer)
    if len(exclusions) == 0 and len(answer_key["coverage_analysis"]["exclusions_applied"]) == 0:
        exclusion_points = S
    
    result["breakdown"]["exclusions"] = {
        "possible_points": 5,
        "earned_points": exclusion_points,
        "submission_value": exclusions,
        "expected_value": answer_key["coverage_analysis"]["exclusions_applied"],
        "comment": "Full points: No exclusions applied, None: Any exclusions incorrectly applied"
    }
    
    result["points_earned"] = coverage_points + policy_points + exclusion_points
    
    # Check for critical errors
    result["critical_error"] = False
    if coverage_applies is False and answer_key["coverage_analysis"]["coverage_applies"] is True:
        result["critical_error"] = True
        result["critical_error_description"] = "Determining no coverage applies when it clearly does"
    
    return result


def evaluate_reserve_calculations(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the reserve calculations section."""
    result = {
        "section_name": "Reserve Calculations",
        "total_points": 30,
        "points_earned": 0,
        "breakdown": {},
        "critical_error": False
    }
    
    # Bodily Injury Reserve (12 points)
    bi_reserve = submission.get("reserve_calculations", {}).get("bodily_injury_reserve", 0)
    bi_points = 0
    if 50000 <= bi_reserve <= 70000:
        bi_points = 12
    elif 40000 <= bi_reserve < 50000 or 70000 < bi_reserve <= 80000:
        bi_points = 6
    
    result["breakdown"]["bodily_injury_reserve"] = {
        "possible_points": 12,
        "earned_points": bi_points,
        "submission_value": bi_reserve,
        "expected_range": "$50,000-$70,000",
        "comment": "Full: $50,000-$70,000, Partial: $40,000-$49,999 or $70,001-$80,000, None: <$40,000 or >$80,000"
    }
    
    # Property Damage Reserve (10 points)
    pd_reserve = submission.get("reserve_calculations", {}).get("property_damage_reserve", 0)
    pd_points = 0
    if 24000 <= pd_reserve <= 30000:
        pd_points = 10
    elif 20000 <= pd_reserve < 24000 or 30000 < pd_reserve <= 35000:
        pd_points = 5
    
    result["breakdown"]["property_damage_reserve"] = {
        "possible_points": 10,
        "earned_points": pd_points,
        "submission_value": pd_reserve,
        "expected_range": "$24,000-$30,000",
        "comment": "Full: $24,000-$30,000, Partial: $20,000-$23,999 or $30,001-$35,000, None: <$20,000 or >$35,000"
    }
    
    # Expense Reserve (8 points)
    exp_reserve = submission.get("reserve_calculations", {}).get("expense_reserve", 0)
    exp_points = 0
    if 4000 <= exp_reserve <= 6000:
        exp_points = 8
    elif 2500 <= exp_reserve < 4000 or 6000 < exp_reserve <= 8000:
        exp_points = 4
    
    result["breakdown"]["expense_reserve"] = {
        "possible_points": 8,
        "earned_points": exp_points,
        "submission_value": exp_reserve,
        "expected_range": "$4,000-$6,000",
        "comment": "Full: $4,000-$6,000, Partial: $2,500-$3,999 or $6,001-$8,000, None: <$2,500 or >$8,000"
    }
    
    result["points_earned"] = bi_points + pd_points + exp_points
    
    # Check for critical errors
    key_bi = answer_key["reserve_calculations"]["bodily_injury_reserve"]
    key_pd = answer_key["reserve_calculations"]["property_damage_reserve"]
    key_exp = answer_key["reserve_calculations"]["expense_reserve"]
    
    if (bi_reserve < 0.5 * key_bi or bi_reserve > 2 * key_bi or
        pd_reserve < 0.5 * key_pd or pd_reserve > 2 * key_pd or
        exp_reserve < 0.5 * key_exp or exp_reserve > 2 * key_exp):
        result["critical_error"] = True
        result["critical_error_description"] = "Setting reserves less than 50% or more than 200% of appropriate amounts"
    
    return result


def evaluate_investigation_steps(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the investigation steps section."""
    result = {
        "section_name": "Investigation Steps",
        "total_points": 20,
        "points_earned": 0,
        "breakdown": {},
        "critical_error": False
    }
    
    steps = submission.get("investigation_steps", [])
    key_steps = answer_key.get("investigation_steps", [])
    
    # Check initial steps (5 points)
    initial_steps_correct = all(step in steps[:5] for step in ["IS-01", "IS-03", "IS-13"])
    initial_steps_points = 5 if initial_steps_correct else 0
    
    result["breakdown"]["initial_steps"] = {
        "possible_points": 5,
        "earned_points": initial_steps_points,
        "submission_value": steps[:5],
        "expected_value": "IS-01, IS-03, IS-13 should be in first 5 steps",
        "comment": "Proper sequencing of initial steps"
    }
    
    # Fact gathering before analysis (5 points)
    fact_gathering_steps = ["IS-02", "IS-04", "IS-05", "IS-06", "IS-07", "IS-08", "IS-09", "IS-10", "IS-11"]
    analysis_steps = ["IS-14", "IS-15", "IS-16", "IS-17", "IS-18", "IS-19", "IS-20"]
    
    # Get indices of steps if they exist in the submission
    fact_indices = [steps.index(step) for step in fact_gathering_steps if step in steps]
    analysis_indices = [steps.index(step) for step in analysis_steps if step in steps]
    
    fact_before_analysis = True
    if fact_indices and analysis_indices:
        fact_before_analysis = max(fact_indices) < min(analysis_indices)
    
    fact_gathering_points = 5 if fact_before_analysis else 0
    
    result["breakdown"]["fact_gathering"] = {
        "possible_points": 5,
        "earned_points": fact_gathering_points,
        "comment": "Proper fact gathering before analysis"
    }
    
    # Proper placement of liability evaluation (5 points)
    liability_eval_proper = False
    if "IS-14" in steps:
        liability_index = steps.index("IS-14")
        # Check if most fact gathering is before liability evaluation
        fact_steps_before = sum(1 for step in fact_gathering_steps if step in steps[:liability_index])
        liability_eval_proper = fact_steps_before >= len(fact_gathering_steps) * 0.7
    
    liability_eval_points = 5 if liability_eval_proper else 0
    
    result["breakdown"]["liability_evaluation"] = {
        "possible_points": 5,
        "earned_points": liability_eval_points,
        "comment": "Proper placement of liability evaluation (IS-14)"
    }
    
    # Proper placement of communication (5 points)
    communication_proper = False
    if "IS-17" in steps and "IS-14" in steps:
        comm_index = steps.index("IS-17")
        strategy_index = steps.index("IS-16") if "IS-16" in steps else float('inf')
        liability_index = steps.index("IS-14")
        
        communication_proper = comm_index > liability_index
        if "IS-16" in steps:
            communication_proper = communication_proper and comm_index > strategy_index
    
    communication_points = 5 if communication_proper else 0
    
    result["breakdown"]["communication"] = {
        "possible_points": 5,
        "earned_points": communication_points,
        "comment": "Proper placement of communication (IS-17 after strategy)"
    }
    
    result["points_earned"] = initial_steps_points + fact_gathering_points + liability_eval_points + communication_points
    
    # Check for critical errors
    if "IS-17" in steps and "IS-14" in steps and steps.index("IS-17") < steps.index("IS-14"):
        result["critical_error"] = True
        result["critical_error_description"] = "Placing communication with claimants (IS-17) before liability evaluation (IS-14)"
    
    return result


def evaluate_communication_responses(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the communication responses section."""
    result = {
        "section_name": "Communication Responses",
        "total_points": 15,
        "points_earned": 0,
        "breakdown": {},
        "critical_error": False
    }
    
    # Claimant Letter (5 points)
    claimant_letter = submission.get("communication_responses", {}).get("claimant_letter", "")
    letter_points = 0
    if claimant_letter == "CL-07":
        letter_points = 5
    elif claimant_letter == "CL-06":
        letter_points = 2
    
    result["breakdown"]["claimant_letter"] = {
        "possible_points": 5,
        "earned_points": letter_points,
        "submission_value": claimant_letter,
        "expected_value": "CL-07",
        "comment": "Full points: CL-07, Partial points: CL-06, No points: Any other template"
    }
    
    # Defense Counsel Referral (5 points)
    defense_counsel = submission.get("communication_responses", {}).get("defense_counsel_referral", None)
    defense_points = 5 if defense_counsel == answer_key["communication_responses"]["defense_counsel_referral"] else 0
    
    result["breakdown"]["defense_counsel_referral"] = {
        "possible_points": 5,
        "earned_points": defense_points,
        "submission_value": defense_counsel,
        "expected_value": answer_key["communication_responses"]["defense_counsel_referral"],
        "comment": "All or nothing"
    }
    
    # Subrogation Potential (5 points)
    subrogation = submission.get("communication_responses", {}).get("subrogation_potential", "")
    subrogation_points = 0
    if subrogation == "SP-04":
        subrogation_points = 5
    elif subrogation == "SP-03":
        subrogation_points = 2
    
    result["breakdown"]["subrogation_potential"] = {
        "possible_points": 5,
        "earned_points": subrogation_points,
        "submission_value": subrogation,
        "expected_value": "SP-04",
        "comment": "Full points: SP-04, Partial points: SP-03, No points: SP-01, SP-02, or SP-05"
    }
    
    result["points_earned"] = letter_points + defense_points + subrogation_points
    
    # Check for critical errors
    if defense_counsel is True and answer_key["communication_responses"]["defense_counsel_referral"] is False:
        result["critical_error"] = True
        result["critical_error_description"] = "Recommending defense counsel when clearly unnecessary (wasting resources)"
    
    if subrogation in ["SP-01", "SP-02"] and answer_key["communication_responses"]["subrogation_potential"] == "SP-04":
        result["critical_error"] = True
        result["critical_error_description"] = "Identifying subrogation potential when insured is primarily at fault"
    
    return result


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the entire submission."""
    # Evaluate each section
    liability_result = evaluate_liability_determination(submission, answer_key)
    coverage_result = evaluate_coverage_analysis(submission, answer_key)
    reserve_result = evaluate_reserve_calculations(submission, answer_key)
    investigation_result = evaluate_investigation_steps(submission, answer_key)
    communication_result = evaluate_communication_responses(submission, answer_key)
    
    # Collect all results
    sections = [
        liability_result,
        coverage_result,
        reserve_result,
        investigation_result,
        communication_result
    ]
    
    # Calculate total points and check for critical errors
    total_points = sum(section["total_points"] for section in sections)
    earned_points = sum(section["points_earned"] for section in sections)
    overall_score = round((earned_points / total_points) * 100, 2)
    
    critical_errors = [section for section in sections if section.get("critical_error", False)]
    
    # Check section minimums
    section_minimums_met = (
        liability_result["points_earned"] >= 15 and
        coverage_result["points_earned"] >= 10 and
        reserve_result["points_earned"] >= 20 and
        investigation_result["points_earned"] >= 15 and
        communication_result["points_earned"] >= 10
    )
    
    # Determine pass/fail status
    passed = overall_score >= 75 and section_minimums_met and not critical_errors
    
    # Prepare the final result
    result = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_score,
        "total_points": total_points,
        "earned_points": earned_points,
        "passed": passed,
        "sections": sections
    }
    
    if critical_errors:
        result["critical_errors"] = [
            {"section": section["section_name"], 
             "description": section.get("critical_error_description", "Undefined critical error")}
            for section in critical_errors
        ]
    
    return result


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    try:
        submission = load_json(submission_file)
        answer_key = load_json(answer_key_file)
        
        # Evaluate the submission
        evaluation_result = evaluate_submission(submission, answer_key)
        
        # Save the results to a file
        with open("test_results.json", "w") as f:
            json.dump(evaluation_result, f, indent=2)
            
        print(f"Evaluation complete. Results saved to test_results.json")
        print(f"Overall score: {evaluation_result['overall_score']}%")
        print(f"Result: {'PASS' if evaluation_result['passed'] else 'FAIL'}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()