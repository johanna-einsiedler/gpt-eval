#!/usr/bin/env python3
import json
import sys
from collections import Counter

def load_json_file(filename):
    """Load JSON data from file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_scenario1(submission, answer_key):
    """Evaluate Scenario 1: Documentation Completeness Check."""
    score = 0
    details = {}
    
    # Check missing documents (10 points)
    correct_missing = set(answer_key["missingDocuments"])
    submitted_missing = set(submission.get("missingDocuments", []))
    
    correctly_identified = correct_missing.intersection(submitted_missing)
    incorrectly_identified = submitted_missing - correct_missing
    
    doc_score = min(10, max(0, 2.5 * len(correctly_identified) - 1 * len(incorrectly_identified)))
    details["missingDocuments"] = {
        "score": doc_score,
        "possiblePoints": 10,
        "correctlyIdentified": list(correctly_identified),
        "incorrectlyIdentified": list(incorrectly_identified),
        "missingFromSubmission": list(correct_missing - submitted_missing)
    }
    score += doc_score
    
    # Check claim validity (5 points)
    if submission.get("validClaim") == answer_key["validClaim"]:
        validity_score = 5
    else:
        validity_score = 0
    details["validClaim"] = {
        "score": validity_score,
        "possiblePoints": 5,
        "submitted": submission.get("validClaim"),
        "correct": answer_key["validClaim"]
    }
    score += validity_score
    
    # Check reason code (10 points)
    if submission.get("reasonCode") == answer_key["reasonCode"]:
        reason_score = 10
    else:
        reason_score = 0
    details["reasonCode"] = {
        "score": reason_score,
        "possiblePoints": 10,
        "submitted": submission.get("reasonCode"),
        "correct": answer_key["reasonCode"]
    }
    score += reason_score
    
    return score, details

def evaluate_scenario2(submission, answer_key):
    """Evaluate Scenario 2: Fraud Detection."""
    score = 0
    details = {}
    
    # Check fraud indicators (15 points)
    correct_indicators = set(answer_key["fraudIndicators"])
    submitted_indicators = set(submission.get("fraudIndicators", []))
    
    correctly_identified = correct_indicators.intersection(submitted_indicators)
    incorrectly_identified = submitted_indicators - correct_indicators
    
    indicator_score = min(15, max(0, 5 * len(correctly_identified) - 2 * len(incorrectly_identified)))
    details["fraudIndicators"] = {
        "score": indicator_score,
        "possiblePoints": 15,
        "correctlyIdentified": list(correctly_identified),
        "incorrectlyIdentified": list(incorrectly_identified),
        "missingFromSubmission": list(correct_indicators - submitted_indicators)
    }
    score += indicator_score
    
    # Check investigation recommendation (5 points)
    if submission.get("investigationRecommended") == answer_key["investigationRecommended"]:
        recommendation_score = 5
    else:
        recommendation_score = 0
    details["investigationRecommended"] = {
        "score": recommendation_score,
        "possiblePoints": 5,
        "submitted": submission.get("investigationRecommended"),
        "correct": answer_key["investigationRecommended"]
    }
    score += recommendation_score
    
    # Check suspicion level (5 points)
    submitted_level = submission.get("suspicionLevel", "")
    correct_level = answer_key["suspicionLevel"]
    
    if submitted_level == correct_level:
        level_score = 5
    elif submitted_level in ["4", "5", "6"]:
        level_score = 3
    else:
        level_score = 0
    
    details["suspicionLevel"] = {
        "score": level_score,
        "possiblePoints": 5,
        "submitted": submitted_level,
        "correct": correct_level
    }
    score += level_score
    
    return score, details

def evaluate_scenario3(submission, answer_key):
    """Evaluate Scenario 3: Coverage Verification."""
    score = 0
    details = {}
    
    # Check coverage applies (10 points)
    if submission.get("coverageApplies") == answer_key["coverageApplies"]:
        coverage_score = 10
    else:
        coverage_score = 0
    details["coverageApplies"] = {
        "score": coverage_score,
        "possiblePoints": 10,
        "submitted": submission.get("coverageApplies"),
        "correct": answer_key["coverageApplies"]
    }
    score += coverage_score
    
    # Check applicable section (5 points)
    if submission.get("applicableSection") == answer_key["applicableSection"]:
        section_score = 5
    else:
        section_score = 0
    details["applicableSection"] = {
        "score": section_score,
        "possiblePoints": 5,
        "submitted": submission.get("applicableSection"),
        "correct": answer_key["applicableSection"]
    }
    score += section_score
    
    # Check if exclusion applies (5 points)
    if submission.get("exclusionApplies") == answer_key["exclusionApplies"]:
        exclusion_score = 5
    else:
        exclusion_score = 0
    details["exclusionApplies"] = {
        "score": exclusion_score,
        "possiblePoints": 5,
        "submitted": submission.get("exclusionApplies"),
        "correct": answer_key["exclusionApplies"]
    }
    score += exclusion_score
    
    # Check exclusion code (5 points)
    if submission.get("exclusionCode") == answer_key["exclusionCode"]:
        code_score = 5
    else:
        code_score = 0
    details["exclusionCode"] = {
        "score": code_score,
        "possiblePoints": 5,
        "submitted": submission.get("exclusionCode"),
        "correct": answer_key["exclusionCode"]
    }
    score += code_score
    
    return score, details

def evaluate_scenario4(submission, answer_key):
    """Evaluate Scenario 4: Settlement Calculation."""
    score = 0
    details = {}
    
    # Check base settlement amount (6 points)
    submitted_base = submission.get("baseSettlementAmount", "")
    correct_base = answer_key["baseSettlementAmount"]
    
    if submitted_base == correct_base:
        base_score = 6
    else:
        # Consider potential partial credit for close calculations
        try:
            if abs(int(submitted_base) - int(correct_base)) / int(correct_base) <= 0.05:
                base_score = 3  # Within 5% error
            else:
                base_score = 0
        except (ValueError, ZeroDivisionError):
            base_score = 0
    
    details["baseSettlementAmount"] = {
        "score": base_score,
        "possiblePoints": 6,
        "submitted": submitted_base,
        "correct": correct_base
    }
    score += base_score
    
    # Check deductible amount (4 points)
    if submission.get("deductibleAmount") == answer_key["deductibleAmount"]:
        deductible_score = 4
    else:
        deductible_score = 0
    details["deductibleAmount"] = {
        "score": deductible_score,
        "possiblePoints": 4,
        "submitted": submission.get("deductibleAmount"),
        "correct": answer_key["deductibleAmount"]
    }
    score += deductible_score
    
    # Check depreciation amount (8 points)
    submitted_depreciation = submission.get("depreciationAmount", "")
    correct_depreciation = answer_key["depreciationAmount"]
    
    if submitted_depreciation == correct_depreciation:
        depreciation_score = 8
    else:
        # Consider potential partial credit for close calculations
        try:
            if abs(int(submitted_depreciation) - int(correct_depreciation)) / int(correct_depreciation) <= 0.05:
                depreciation_score = 4  # Within 5% error
            else:
                depreciation_score = 0
        except (ValueError, ZeroDivisionError):
            depreciation_score = 0
    
    details["depreciationAmount"] = {
        "score": depreciation_score,
        "possiblePoints": 8,
        "submitted": submitted_depreciation,
        "correct": correct_depreciation
    }
    score += depreciation_score
    
    # Check final settlement amount (7 points)
    submitted_final = submission.get("finalSettlementAmount", "")
    correct_final = answer_key["finalSettlementAmount"]
    
    if submitted_final == correct_final:
        final_score = 7
    else:
        # Consider potential partial credit for close calculations
        try:
            if abs(int(submitted_final) - int(correct_final)) / int(correct_final) <= 0.05:
                final_score = 3  # Within 5% error
            else:
                final_score = 0
        except (ValueError, ZeroDivisionError):
            final_score = 0
    
    details["finalSettlementAmount"] = {
        "score": final_score,
        "possiblePoints": 7,
        "submitted": submitted_final,
        "correct": correct_final
    }
    score += final_score
    
    return score, details

def check_critical_errors(results):
    """Check for critical errors that result in automatic failure."""
    critical_errors = []
    
    # Error 1: Claiming a policy covers a clearly excluded risk (Scenario 3)
    if (results["scenario3"]["coverageApplies"]["submitted"] == True and 
        results["scenario3"]["coverageApplies"]["correct"] == False):
        critical_errors.append("Claimed coverage for a clearly excluded risk")
    
    # Error 2: Settlement calculation error exceeding 10% (Scenario 4)
    try:
        submitted_final = int(results["scenario4"]["finalSettlementAmount"]["submitted"])
        correct_final = int(results["scenario4"]["finalSettlementAmount"]["correct"])
        if abs(submitted_final - correct_final) / correct_final > 0.1:
            critical_errors.append("Settlement calculation error exceeding 10%")
    except (ValueError, ZeroDivisionError, KeyError):
        critical_errors.append("Invalid or missing settlement calculation")
    
    # Error 3: Complete failure to identify fraud indicators (Scenario 2)
    if len(results["scenario2"]["fraudIndicators"]["correctlyIdentified"]) == 0:
        critical_errors.append("Complete failure to identify fraud indicators")
    
    return critical_errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each scenario
    scenario1_score, scenario1_details = evaluate_scenario1(
        submission.get("scenario1", {}), answer_key["scenario1"])
    
    scenario2_score, scenario2_details = evaluate_scenario2(
        submission.get("scenario2", {}), answer_key["scenario2"])
    
    scenario3_score, scenario3_details = evaluate_scenario3(
        submission.get("scenario3", {}), answer_key["scenario3"])
    
    scenario4_score, scenario4_details = evaluate_scenario4(
        submission.get("scenario4", {}), answer_key["scenario4"])
    
    # Compile results
    results = {
        "scenario1": scenario1_details,
        "scenario2": scenario2_details,
        "scenario3": scenario3_details,
        "scenario4": scenario4_details,
        "scenarioScores": {
            "scenario1": scenario1_score,
            "scenario2": scenario2_score,
            "scenario3": scenario3_score,
            "scenario4": scenario4_score
        },
        "totalScore": scenario1_score + scenario2_score + scenario3_score + scenario4_score,
        "possiblePoints": 100,
        "overall_score": (scenario1_score + scenario2_score + scenario3_score + scenario4_score)
    }
    
    # Calculate percentage score
    results["overall_score"] = results["totalScore"] / results["possiblePoints"] * 100
    
    # Check for passing criteria
    results["passedMinimumScore"] = results["totalScore"] >= 75
    results["passedScenarioMinimums"] = all([
        scenario1_score >= 15,
        scenario2_score >= 15,
        scenario3_score >= 15,
        scenario4_score >= 15
    ])
    
    # Check for critical errors
    critical_errors = check_critical_errors(results)
    results["criticalErrors"] = critical_errors
    results["passed"] = (results["passedMinimumScore"] and 
                         results["passedScenarioMinimums"] and 
                         len(critical_errors) == 0)
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Total score: {results['totalScore']}/100 ({results['overall_score']:.2f}%)")
    print(f"Passed: {results['passed']}")
    if critical_errors:
        print("Critical errors found:")
        for error in critical_errors:
            print(f"- {error}")

if __name__ == "__main__":
    main()