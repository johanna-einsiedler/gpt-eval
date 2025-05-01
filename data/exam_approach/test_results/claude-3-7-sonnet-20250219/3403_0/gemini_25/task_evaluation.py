#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_npv(submission_value: float, key_value: float) -> Tuple[float, str]:
    """Evaluate NPV calculation."""
    max_points = 10
    # Within ±5% of the correct value
    error_percentage = abs((submission_value - key_value) / key_value) * 100
    
    if error_percentage <= 5:
        return max_points, "Correct within acceptable margin"
    elif error_percentage <= 10:
        return max_points * 0.7, "Outside optimal range but reasonable"
    elif error_percentage <= 20:
        return max_points * 0.4, "Significant deviation from expected value"
    else:
        return 0, "Incorrect calculation"

def evaluate_bcr(submission_value: float, key_value: float) -> Tuple[float, str]:
    """Evaluate Benefit-Cost Ratio calculation."""
    max_points = 10
    # Within ±0.05 of the correct value
    error = abs(submission_value - key_value)
    
    if error <= 0.05:
        return max_points, "Correct within acceptable margin"
    elif error <= 0.1:
        return max_points * 0.7, "Outside optimal range but reasonable"
    elif error <= 0.2:
        return max_points * 0.4, "Significant deviation from expected value"
    else:
        return 0, "Incorrect calculation"

def evaluate_irr(submission_value: float, key_value: float) -> Tuple[float, str]:
    """Evaluate IRR calculation."""
    max_points = 10
    # Within ±0.5 percentage points of the correct value
    error = abs(submission_value - key_value)
    
    if error <= 0.5:
        return max_points, "Correct within acceptable margin"
    elif error <= 1.0:
        return max_points * 0.7, "Outside optimal range but reasonable"
    elif error <= 2.0:
        return max_points * 0.4, "Significant deviation from expected value"
    else:
        return 0, "Incorrect calculation"

def evaluate_payback_period(submission: Dict[str, int], key: Dict[str, int]) -> Tuple[float, str]:
    """Evaluate payback period calculation."""
    max_points = 10
    # Convert to total months for comparison
    submission_months = submission["years"] * 12 + submission["months"]
    key_months = key["years"] * 12 + key["months"]
    
    # Within ±3 months of the correct value
    error_months = abs(submission_months - key_months)
    
    if error_months <= 3:
        return max_points, "Correct within acceptable margin"
    elif error_months <= 6:
        return max_points * 0.7, "Outside optimal range but reasonable"
    elif error_months <= 12:
        return max_points * 0.4, "Significant deviation from expected value"
    else:
        return 0, "Incorrect calculation"

def evaluate_recommendation(submission_code: str, key_code: str, submission_justification: str) -> Tuple[float, str]:
    """Evaluate recommendation and justification."""
    max_points = 10
    
    # Check if recommendation code matches
    if submission_code == key_code:
        code_points = max_points * 0.5
        code_feedback = "Correct recommendation code"
    else:
        code_points = 0
        code_feedback = "Incorrect recommendation code"
    
    # Evaluate justification (simplified - in a real scenario, this would be more nuanced)
    if len(submission_justification) > 20 and "NPV" in submission_justification and "IRR" in submission_justification:
        justification_points = max_points * 0.5
        justification_feedback = "Justification addresses key financial metrics"
    else:
        justification_points = 0
        justification_feedback = "Justification missing key financial considerations"
    
    return code_points + justification_points, f"{code_feedback}; {justification_feedback}"

def evaluate_financing_calculations(submission: Dict[str, Any], key: Dict[str, Any]) -> Tuple[float, str]:
    """Evaluate financing calculations for all options."""
    max_points = 25
    points = 0
    feedback = []
    
    # Evaluate each option
    for option in ["option_a", "option_b", "option_c"]:
        sub_option = submission["financing_options"][option]
        key_option = key["financing_options"][option]
        
        # Annual debt service (±2%)
        ads_error = abs((sub_option["annual_debt_service"] - key_option["annual_debt_service"]) / key_option["annual_debt_service"]) * 100
        if ads_error <= 2:
            points += 2
            feedback.append(f"{option} annual debt service: correct")
        else:
            feedback.append(f"{option} annual debt service: error of {ads_error:.2f}%")
        
        # Total cost (±2%)
        tc_error = abs((sub_option["total_cost"] - key_option["total_cost"]) / key_option["total_cost"]) * 100
        if tc_error <= 2:
            points += 2
            feedback.append(f"{option} total cost: correct")
        else:
            feedback.append(f"{option} total cost: error of {tc_error:.2f}%")
        
        # Present value cost (±3%)
        pvc_error = abs((sub_option["present_value_cost"] - key_option["present_value_cost"]) / key_option["present_value_cost"]) * 100
        if pvc_error <= 3:
            points += 2
            feedback.append(f"{option} present value cost: correct")
        else:
            feedback.append(f"{option} present value cost: error of {pvc_error:.2f}%")
        
        # Debt service coverage ratio (±0.05)
        dscr_error = abs(sub_option["debt_service_coverage_ratio"] - key_option["debt_service_coverage_ratio"])
        if dscr_error <= 0.05:
            points += 1.5
            feedback.append(f"{option} DSCR: correct")
        else:
            feedback.append(f"{option} DSCR: error of {dscr_error:.2f}")
        
        # Meets minimum coverage
        if sub_option["meets_minimum_coverage"] == key_option["meets_minimum_coverage"]:
            points += 0.83  # ~2.5 points divided by 3 options
            feedback.append(f"{option} minimum coverage assessment: correct")
        else:
            feedback.append(f"{option} minimum coverage assessment: incorrect")
    
    return points, "; ".join(feedback)

def evaluate_lowest_cost_option(submission: str, key: str) -> Tuple[float, str]:
    """Evaluate identification of lowest cost option."""
    max_points = 5
    
    if submission == key:
        return max_points, "Correctly identified lowest cost option"
    else:
        return 0, "Failed to identify lowest cost option"

def evaluate_recommended_option(submission: str, key: str, justification: str) -> Tuple[float, str]:
    """Evaluate recommended financing option and justification."""
    max_points = 20  # 10 for recommendation, 10 for justification
    
    # Check recommendation
    if submission == key:
        rec_points = 10
        rec_feedback = "Correct recommendation"
    else:
        # Critical error - automatic failure if recommending any option when none are viable
        if key == "FIN-X" and submission != "FIN-X":
            rec_points = 0
            rec_feedback = "CRITICAL ERROR: Recommended a financing option when none meet minimum requirements"
        else:
            rec_points = 0
            rec_feedback = "Incorrect recommendation"
    
    # Evaluate justification
    if "coverage ratio" in justification.lower() and "1.25" in justification:
        just_points = 10
        just_feedback = "Justification correctly addresses debt service coverage requirements"
    elif len(justification) > 20 and ("debt" in justification.lower() or "coverage" in justification.lower()):
        just_points = 5
        just_feedback = "Justification partially addresses key considerations"
    else:
        just_points = 0
        just_feedback = "Justification missing key considerations"
    
    return rec_points + just_points, f"{rec_feedback}; {just_feedback}"

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "scenario_1": {
            "npv": {},
            "benefit_cost_ratio": {},
            "irr": {},
            "payback_period": {},
            "recommendation": {},
            "total_points": 0
        },
        "scenario_2": {
            "financing_calculations": {},
            "lowest_cost_option": {},
            "recommendation": {},
            "total_points": 0
        },
        "critical_errors": [],
        "overall_score": 0
    }
    
    total_points = 0
    
    # Scenario 1 evaluation
    # NPV
    points, feedback = evaluate_npv(submission["scenario_1"]["npv"], answer_key["scenario_1"]["npv"])
    results["scenario_1"]["npv"] = {"points": points, "feedback": feedback, "max_points": 10}
    results["scenario_1"]["total_points"] += points
    total_points += points
    
    # BCR
    points, feedback = evaluate_bcr(submission["scenario_1"]["benefit_cost_ratio"], answer_key["scenario_1"]["benefit_cost_ratio"])
    results["scenario_1"]["benefit_cost_ratio"] = {"points": points, "feedback": feedback, "max_points": 10}
    results["scenario_1"]["total_points"] += points
    total_points += points
    
    # IRR
    points, feedback = evaluate_irr(submission["scenario_1"]["irr"], answer_key["scenario_1"]["irr"])
    results["scenario_1"]["irr"] = {"points": points, "feedback": feedback, "max_points": 10}
    results["scenario_1"]["total_points"] += points
    total_points += points
    
    # Payback period
    points, feedback = evaluate_payback_period(submission["scenario_1"]["payback_period"], answer_key["scenario_1"]["payback_period"])
    results["scenario_1"]["payback_period"] = {"points": points, "feedback": feedback, "max_points": 10}
    results["scenario_1"]["total_points"] += points
    total_points += points
    
    # Recommendation
    points, feedback = evaluate_recommendation(
        submission["scenario_1"]["recommendation_code"], 
        answer_key["scenario_1"]["recommendation_code"],
        submission["scenario_1"]["justification"]
    )
    results["scenario_1"]["recommendation"] = {"points": points, "feedback": feedback, "max_points": 10}
    results["scenario_1"]["total_points"] += points
    total_points += points
    
    # Scenario 2 evaluation
    # Financing calculations
    points, feedback = evaluate_financing_calculations(submission["scenario_2"], answer_key["scenario_2"])
    results["scenario_2"]["financing_calculations"] = {"points": points, "feedback": feedback, "max_points": 25}
    results["scenario_2"]["total_points"] += points
    total_points += points
    
    # Lowest cost option
    points, feedback = evaluate_lowest_cost_option(
        submission["scenario_2"]["lowest_cost_option"], 
        answer_key["scenario_2"]["lowest_cost_option"]
    )
    results["scenario_2"]["lowest_cost_option"] = {"points": points, "feedback": feedback, "max_points": 5}
    results["scenario_2"]["total_points"] += points
    total_points += points
    
    # Recommended option and justification
    points, feedback = evaluate_recommended_option(
        submission["scenario_2"]["recommended_option"], 
        answer_key["scenario_2"]["recommended_option"],
        submission["scenario_2"]["justification"]
    )
    results["scenario_2"]["recommendation"] = {"points": points, "feedback": feedback, "max_points": 20}
    results["scenario_2"]["total_points"] += points
    total_points += points
    
    # Check for critical errors
    if "CRITICAL ERROR" in results["scenario_2"]["recommendation"]["feedback"]:
        results["critical_errors"].append("Recommended a financing option when none meet minimum requirements")
    
    # Calculate overall score
    results["overall_score"] = round((total_points / 100) * 100, 2)  # As percentage
    
    # Determine pass/fail status
    if results["critical_errors"] or results["overall_score"] < 75:
        results["status"] = "FAIL"
    else:
        if results["overall_score"] >= 90:
            results["status"] = "PASS - Excellent"
        else:
            results["status"] = "PASS"
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Status: {results['status']}")

if __name__ == "__main__":
    main()