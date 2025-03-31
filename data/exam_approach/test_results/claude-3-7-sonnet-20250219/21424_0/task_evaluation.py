import json
import re

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def validate_reserve(candidate_value, key_value, allowed_percentage):
    """Validate if candidate's reserve value is within acceptable range"""
    lower_bound = key_value * (1 - allowed_percentage/100)
    upper_bound = key_value * (1 + allowed_percentage/100)
    return lower_bound <= candidate_value <= upper_bound

def validate_reserve_codes(candidate_code, acceptable_codes):
    """Validate if candidate's reserve code is acceptable"""
    return candidate_code in acceptable_codes

def validate_policy_sections(candidate_sections, required_sections):
    """Validate if candidate included all required policy sections"""
    return all(section in candidate_sections for section in required_sections)

def count_words(text):
    """Count words in a text string"""
    return len(re.findall(r'\w+', text))

def validate_justification(justification, required_elements):
    """Check if justification contains required elements and is within word limit"""
    if count_words(justification) > 250:
        return False, "Exceeds 250 word limit"
    
    missing_elements = [element for element in required_elements 
                        if element.lower() not in justification.lower()]
    
    if missing_elements:
        return False, f"Missing elements: {', '.join(missing_elements)}"
    return True, ""

def evaluate_scenario_1(candidate, answer_key):
    """Evaluate Auto Liability Claim scenario"""
    score = 0
    max_score = 30
    feedback = []
    critical_errors = []
    
    # Bodily Injury Reserve (10 points)
    bi_reserve = candidate["bodily_injury_reserve"]
    key_bi_reserve = answer_key["bodily_injury_reserve"]
    
    if validate_reserve(bi_reserve, key_bi_reserve, 15):
        score += 10
        feedback.append("Bodily Injury Reserve calculation: Correct (10/10)")
    else:
        if bi_reserve < key_bi_reserve * 0.5 or bi_reserve > key_bi_reserve * 2:
            critical_errors.append("Critical Error: Bodily Injury Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Bodily Injury Reserve calculation: Incorrect (0/10) - Critical Error")
        else:
            points = max(0, 10 - int(abs(bi_reserve - key_bi_reserve) / key_bi_reserve * 20))
            score += points
            feedback.append(f"Bodily Injury Reserve calculation: Partially correct ({points}/10)")
    
    # Property Damage Reserve (8 points)
    pd_reserve = candidate["property_damage_reserve"]
    key_pd_reserve = answer_key["property_damage_reserve"]
    
    if validate_reserve(pd_reserve, key_pd_reserve, 10):
        score += 8
        feedback.append("Property Damage Reserve calculation: Correct (8/8)")
    else:
        if pd_reserve < key_pd_reserve * 0.5 or pd_reserve > key_pd_reserve * 2:
            critical_errors.append("Critical Error: Property Damage Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Property Damage Reserve calculation: Incorrect (0/8) - Critical Error")
        else:
            points = max(0, 8 - int(abs(pd_reserve - key_pd_reserve) / key_pd_reserve * 16))
            score += points
            feedback.append(f"Property Damage Reserve calculation: Partially correct ({points}/8)")
    
    # Medical Expense Reserve (7 points)
    me_reserve = candidate["medical_expense_reserve"]
    key_me_reserve = answer_key["medical_expense_reserve"]
    
    if validate_reserve(me_reserve, key_me_reserve, 15):
        score += 7
        feedback.append("Medical Expense Reserve calculation: Correct (7/7)")
    else:
        if me_reserve < key_me_reserve * 0.5 or me_reserve > key_me_reserve * 2:
            critical_errors.append("Critical Error: Medical Expense Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Medical Expense Reserve calculation: Incorrect (0/7) - Critical Error")
        else:
            points = max(0, 7 - int(abs(me_reserve - key_me_reserve) / key_me_reserve * 14))
            score += points
            feedback.append(f"Medical Expense Reserve calculation: Partially correct ({points}/7)")
    
    # Reserve Codes (part of above scores)
    acceptable_bi_codes = ["AL-BI-01", "AL-BI-02"]
    acceptable_pd_codes = ["AL-PD-01"]
    acceptable_me_codes = ["AL-ME-01", "AL-ME-02", "AL-ME-03"]
    
    if not validate_reserve_codes(candidate["bodily_injury_code"], acceptable_bi_codes):
        critical_errors.append("Critical Error: Incorrect Bodily Injury Reserve code")
        feedback.append("Incorrect Bodily Injury Reserve code")
    
    if not validate_reserve_codes(candidate["property_damage_code"], acceptable_pd_codes):
        critical_errors.append("Critical Error: Incorrect Property Damage Reserve code")
        feedback.append("Incorrect Property Damage Reserve code")
    
    if not validate_reserve_codes(candidate["medical_expense_code"], acceptable_me_codes):
        critical_errors.append("Critical Error: Incorrect Medical Expense Reserve code")
        feedback.append("Incorrect Medical Expense Reserve code")
    
    # Policy references and justification (5 points)
    required_sections = ["2.1", "2.2", "2.3"]
    candidate_sections = candidate["policy_sections_referenced"]
    
    if validate_policy_sections(candidate_sections, required_sections):
        score += 3
        feedback.append("Policy references: Correct (3/3)")
    else:
        missing = [s for s in required_sections if s not in candidate_sections]
        points = max(0, 3 - len(missing))
        score += points
        feedback.append(f"Policy references: Missing {', '.join(missing)} ({points}/3)")
    
    required_elements = [
        "pain and suffering multiplier",
        "attorney",
        "contingency"
    ]
    
    justification_valid, justification_feedback = validate_justification(
        candidate["justification"], required_elements
    )
    
    if justification_valid:
        score += 2
        feedback.append("Justification: Complete (2/2)")
    else:
        if not candidate["justification"]:
            critical_errors.append("Critical Error: No justification provided")
            feedback.append("Justification: Missing (0/2) - Critical Error")
        else:
            feedback.append(f"Justification: Incomplete (0/2) - {justification_feedback}")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback,
        "critical_errors": critical_errors
    }

def evaluate_scenario_2(candidate, answer_key):
    """Evaluate Workers' Compensation scenario"""
    score = 0
    max_score = 35
    feedback = []
    critical_errors = []
    
    # Indemnity Reserve (10 points)
    indemnity_reserve = candidate["indemnity_reserve"]
    key_indemnity_reserve = answer_key["indemnity_reserve"]
    
    if validate_reserve(indemnity_reserve, key_indemnity_reserve, 15):
        score += 10
        feedback.append("Indemnity Reserve calculation: Correct (10/10)")
    else:
        if indemnity_reserve < key_indemnity_reserve * 0.5 or indemnity_reserve > key_indemnity_reserve * 2:
            critical_errors.append("Critical Error: Indemnity Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Indemnity Reserve calculation: Incorrect (0/10) - Critical Error")
        else:
            points = max(0, 10 - int(abs(indemnity_reserve - key_indemnity_reserve) / key_indemnity_reserve * 20))
            score += points
            feedback.append(f"Indemnity Reserve calculation: Partially correct ({points}/10)")
    
    # Medical Reserve (10 points)
    medical_reserve = candidate["medical_reserve"]
    key_medical_reserve = answer_key["medical_reserve"]
    
    if validate_reserve(medical_reserve, key_medical_reserve, 15):
        score += 10
        feedback.append("Medical Reserve calculation: Correct (10/10)")
    else:
        if medical_reserve < key_medical_reserve * 0.5 or medical_reserve > key_medical_reserve * 2:
            critical_errors.append("Critical Error: Medical Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Medical Reserve calculation: Incorrect (0/10) - Critical Error")
        else:
            points = max(0, 10 - int(abs(medical_reserve - key_medical_reserve) / key_medical_reserve * 20))
            score += points
            feedback.append(f"Medical Reserve calculation: Partially correct ({points}/10)")
    
    # Rehabilitation Reserve (8 points)
    rehab_reserve = candidate["rehabilitation_reserve"]
    key_rehab_reserve = answer_key["rehabilitation_reserve"]
    
    if validate_reserve(rehab_reserve, key_rehab_reserve, 50):  # Higher tolerance due to subjectivity
        score += 8
        feedback.append("Rehabilitation Reserve calculation: Correct (8/8)")
    else:
        if rehab_reserve < key_rehab_reserve * 0.5 or rehab_reserve > key_rehab_reserve * 2:
            critical_errors.append("Critical Error: Rehabilitation Reserve significantly off (below 50% or above 200% of expected)")
            feedback.append("Rehabilitation Reserve calculation: Incorrect (0/8) - Critical Error")
        else:
            points = max(0, 8 - int(abs(rehab_reserve - key_rehab_reserve) / key_rehab_reserve * 16))
            score += points
            feedback.append(f"Rehabilitation Reserve calculation: Partially correct ({points}/8)")
    
    # Net change calculation (2 points)
    expected_net_change = candidate["total_reserve"] - candidate["previous_total_reserve"]
    if abs(candidate["net_change"] - expected_net_change) < 0.01:  # Allow for rounding differences
        score += 2
        feedback.append("Net change calculation: Correct (2/2)")
    else:
        feedback.append(f"Net change calculation: Incorrect (0/2). Expected {expected_net_change}, got {candidate['net_change']}")
    
    # Reserve Codes (part of above scores)
    acceptable_indemnity_codes = ["WC-IN-01", "WC-IN-02", "WC-IN-03"]
    acceptable_medical_codes = ["WC-ME-02", "WC-ME-03", "WC-ME-05"]
    acceptable_rehab_codes = ["WC-RH-01", "WC-RH-02"]
    
    if not validate_reserve_codes(candidate["indemnity_code"], acceptable_indemnity_codes):
        critical_errors.append("Critical Error: Incorrect Indemnity Reserve code")
        feedback.append("Incorrect Indemnity Reserve code")
    
    if not validate_reserve_codes(candidate["medical_code"], acceptable_medical_codes):
        critical_errors.append("Critical Error: Incorrect Medical Reserve code")
        feedback.append("Incorrect Medical Reserve code")
    
    if not validate_reserve_codes(candidate["rehabilitation_code"], acceptable_rehab_codes):
        critical_errors.append("Critical Error: Incorrect Rehabilitation Reserve code")
        feedback.append("Incorrect Rehabilitation Reserve code")
    
    # Policy references and justification (5 points)
    required_sections = ["3.1", "3.2", "3.3", "3.4"]
    candidate_sections = candidate["policy_sections_referenced"]
    
    if validate_policy_sections(candidate_sections, required_sections):
        score += 3
        feedback.append("Policy references: Correct (3/3)")
    else:
        missing = [s for s in required_sections if s not in candidate_sections]
        points = max(0, 3 - len(missing))
        score += points
        feedback.append(f"Policy references: Missing {', '.join(missing)} ({points}/3)")
    
    required_elements = [
        "MRI",
        "surgery",
        "disability",
        "contingency",
        "rehabilitation"
    ]
    
    justification_valid, justification_feedback = validate_justification(
        candidate["justification"], required_elements
    )
    
    if justification_valid:
        score += 2
        feedback.append("Justification: Complete (2/2)")
    else:
        if not candidate["justification"]:
            critical_errors.append("Critical Error: No justification provided")
            feedback.append("Justification: Missing (0/2) - Critical Error")
        else:
            feedback.append(f"Justification: Incomplete (0/2) - {justification_feedback}")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback,
        "critical_errors": critical_errors
    }

def evaluate_scenario_3(candidate, answer_key):
    """Evaluate General Liability scenario"""
    score = 0
    max_score = 35
    feedback = []
    critical_errors = []
    
    # Identification of exposures (10 points)
    candidate_exposures = candidate["exposures"]
    if len(candidate_exposures) < 3:
        critical_errors.append("Critical Error: Failed to identify at least 3 exposures")
        feedback.append("Exposure identification: Insufficient (0/10) - Critical Error")
    else:
        score += 10
        feedback.append("Exposure identification: Complete (10/10)")
    
    # Check for property damage reserve (8 points)
    property_damage_exposure = None
    for exposure in candidate_exposures:
        if "property" in exposure["exposure_type"].lower():
            property_damage_exposure = exposure
            break
    
    if property_damage_exposure:
        pd_reserve = property_damage_exposure["reserve_amount"]
        key_pd_reserve = 142300.00  # From answer key
        
        if validate_reserve(pd_reserve, key_pd_reserve, 15):
            score += 8
            feedback.append("Property Damage Reserve calculation: Correct (8/8)")
        else:
            if pd_reserve < key_pd_reserve * 0.5 or pd_reserve > key_pd_reserve * 2:
                critical_errors.append("Critical Error: Property Damage Reserve significantly off (below 50% or above 200% of expected)")
                feedback.append("Property Damage Reserve calculation: Incorrect (0/8) - Critical Error")
            else:
                points = max(0, 8 - int(abs(pd_reserve - key_pd_reserve) / key_pd_reserve * 16))
                score += points
                feedback.append(f"Property Damage Reserve calculation: Partially correct ({points}/8)")
        
        # Check code
        acceptable_pd_codes = ["GL-PD-01", "GL-PD-02", "GL-PD-03"]
        if not validate_reserve_codes(property_damage_exposure["reserve_code"], acceptable_pd_codes):
            critical_errors.append("Critical Error: Incorrect Property Damage Reserve code")
            feedback.append("Incorrect Property Damage Reserve code")
    else:
        critical_errors.append("Critical Error: No Property Damage exposure identified")
        feedback.append("Property Damage Reserve: Missing (0/8) - Critical Error")
    
    # Check for business interruption reserve (8 points)
    bi_exposure = None
    for exposure in candidate_exposures:
        if "business" in exposure["exposure_type"].lower() or "interruption" in exposure["exposure_type"].lower():
            bi_exposure = exposure
            break
    
    if bi_exposure:
        bi_reserve = bi_exposure["reserve_amount"]
        key_bi_reserve = 34100.00  # From answer key
        
        if validate_reserve(bi_reserve, key_bi_reserve, 10):
            score += 8
            feedback.append("Business Interruption Reserve calculation: Correct (8/8)")
        else:
            if bi_reserve < key_bi_reserve * 0.5 or bi_reserve > key_bi_reserve * 2:
                critical_errors.append("Critical Error: Business Interruption Reserve significantly off (below 50% or above 200% of expected)")
                feedback.append("Business Interruption Reserve calculation: Incorrect (0/8) - Critical Error")
            else:
                points = max(0, 8 - int(abs(bi_reserve - key_bi_reserve) / key_bi_reserve * 16))
                score += points
                feedback.append(f"Business Interruption Reserve calculation: Partially correct ({points}/8)")
        
        # Check code
        acceptable_bi_codes = ["GL-BI-01", "GL-BI-02"]
        if not validate_reserve_codes(bi_exposure["reserve_code"], acceptable_bi_codes):
            critical_errors.append("Critical Error: Incorrect Business Interruption Reserve code")
            feedback.append("Incorrect Business Interruption Reserve code")
    else:
        critical_errors.append("Critical Error: No Business Interruption exposure identified")
        feedback.append("Business Interruption Reserve: Missing (0/8) - Critical Error")
    
    # Check for additional exposure (4 points)
    # Look for emergency response, legal expenses, or other valid third exposure
    additional_exposure = None
    for exposure in candidate_exposures:
        if ("emergency" in exposure["exposure_type"].lower() or 
            "legal" in exposure["exposure_type"].lower() or 
            "third" in exposure["exposure_type"].lower()):
            additional_exposure = exposure
            break
    
    if additional_exposure:
        # We'll check if it's emergency response costs specifically
        if "emergency" in additional_exposure["exposure_type"].lower():
            er_reserve = additional_exposure["reserve_amount"]
            key_er_reserve = 10000.00  # From answer key
            
            if validate_reserve(er_reserve, key_er_reserve, 15):
                score += 4
                feedback.append("Additional Exposure Reserve calculation: Correct (4/4)")
            else:
                if er_reserve < key_er_reserve * 0.5 or er_reserve > key_er_reserve * 2:
                    critical_errors.append("Critical Error: Additional Exposure Reserve significantly off (below 50% or above 200% of expected)")
                    feedback.append("Additional Exposure Reserve calculation: Incorrect (0/4) - Critical Error")
                else:
                    points = max(0, 4 - int(abs(er_reserve - key_er_reserve) / key_er_reserve * 8))
                    score += points
                    feedback.append(f"Additional Exposure Reserve calculation: Partially correct ({points}/4)")
        else:
            # If it's another valid exposure type, we'll give partial credit
            score += 2
            feedback.append("Additional Exposure identified but not Emergency Response Costs (2/4)")
        
        # Check code
        acceptable_additional_codes = ["GL-ER-01", "GL-LE-01", "GL-TP-01", "GL-TP-02", "GL-SU-01"]
        if not validate_reserve_codes(additional_exposure["reserve_code"], acceptable_additional_codes):
            critical_errors.append("Critical Error: Incorrect Additional Exposure Reserve code")
            feedback.append("Incorrect Additional Exposure Reserve code")
    else:
        feedback.append("Additional Exposure Reserve: Missing (0/4)")
    
    # Policy references and justification (5 points)
    required_sections = ["4.1", "4.2", "4.3"]
    candidate_sections = candidate["policy_sections_referenced"]
    
    if validate_policy_sections(candidate_sections, required_sections):
        score += 3
        feedback.append("Policy references: Correct (3/3)")
    else:
        missing = [s for s in required_sections if s not in candidate_sections]
        points = max(0, 3 - len(missing))
        score += points
        feedback.append(f"Policy references: Missing {', '.join(missing)} ({points}/3)")
    
    required_elements = [
        "separate",
        "exposure",
        "contingency",
        "business interruption"
    ]
    
    justification_valid, justification_feedback = validate_justification(
        candidate["justification"], required_elements
    )
    
    if justification_valid:
        score += 2
        feedback.append("Justification: Complete (2/2)")
    else:
        if not candidate["justification"]:
            critical_errors.append("Critical Error: No justification provided")
            feedback.append("Justification: Missing (0/2) - Critical Error")
        else:
            feedback.append(f"Justification: Incomplete (0/2) - {justification_feedback}")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback,
        "critical_errors": critical_errors
    }

def evaluate_submission(candidate, answer_key):
    """Evaluate the entire submission"""
    scenario1_results = evaluate_scenario_1(candidate["scenario_1"], answer_key["scenario_1"])
    scenario2_results = evaluate_scenario_2(candidate["scenario_2"], answer_key["scenario_2"])
    scenario3_results = evaluate_scenario_3(candidate["scenario_3"], answer_key["scenario_3"])
    
    # Calculate overall score
    total_score = scenario1_results["score"] + scenario2_results["score"] + scenario3_results["score"]
    max_score = scenario1_results["max_score"] + scenario2_results["max_score"] + scenario3_results["max_score"]
    overall_percentage = round((total_score / max_score) * 100, 2)
    
    # Check for passing criteria
    passed = True
    failure_reasons = []
    
    # 1. Overall score at least 70%
    if overall_percentage < 70:
        passed = False
        failure_reasons.append(f"Overall score below 70% (got {overall_percentage}%)")
    
    # 2. Minimum scenario scores (60% each)
    if scenario1_results["percentage"] < 60:
        passed = False
        failure_reasons.append(f"Scenario 1 score below 60% (got {scenario1_results['percentage']}%)")
    
    if scenario2_results["percentage"] < 60:
        passed = False
        failure_reasons.append(f"Scenario 2 score below 60% (got {scenario2_results['percentage']}%)")
    
    if scenario3_results["percentage"] < 60:
        passed = False
        failure_reasons.append(f"Scenario 3 score below 60% (got {scenario3_results['percentage']}%)")
    
    # 3. Critical errors
    all_critical_errors = (
        scenario1_results["critical_errors"] + 
        scenario2_results["critical_errors"] + 
        scenario3_results["critical_errors"]
    )
    
    if all_critical_errors:
        passed = False
        failure_reasons.append(f"Critical errors present: {len(all_critical_errors)}")
    
    return {
        "overall_score": overall_percentage,
        "total_points": total_score,
        "max_points": max_score,
        "passed": passed,
        "failure_reasons": failure_reasons if not passed else [],
        "scenario_1": scenario1_results,
        "scenario_2": scenario2_results,
        "scenario_3": scenario3_results,
        "critical_errors": all_critical_errors
    }

def main():
    # Load files
    candidate_submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not candidate_submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate submission
    results = evaluate_submission(candidate_submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    if not results['passed']:
        print("Failure reasons:")
        for reason in results['failure_reasons']:
            print(f"- {reason}")
    print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()