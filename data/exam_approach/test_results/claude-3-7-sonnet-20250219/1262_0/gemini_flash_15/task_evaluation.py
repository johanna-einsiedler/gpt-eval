#!/usr/bin/env python3
import json
import sys
import re
from datetime import datetime, timedelta

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    score = 0
    feedback = {}
    
    # Check recipient identification (3 points)
    if "Dr. Sarah Johnson" in submission.get("recipient", "") and "Citywide Medical Center" in submission.get("recipient", ""):
        score += 3
        feedback["recipient"] = "Correct recipient identified (3/3)"
    else:
        feedback["recipient"] = f"Incorrect or incomplete recipient (0/3). Expected 'Dr. Sarah Johnson, Citywide Medical Center', got '{submission.get('recipient', '')}'."
    
    # Check subject line with reference number (3 points)
    subject = submission.get("subject", "")
    if "APP-2023-45871" in subject and ("James Rodriguez" in subject or "Rodriguez" in subject):
        score += 3
        feedback["subject"] = "Clear subject line with reference number (3/3)"
    elif "APP-2023-45871" in subject:
        score += 2
        feedback["subject"] = "Subject includes reference number but missing patient name (2/3)"
    else:
        feedback["subject"] = f"Incorrect or incomplete subject line (0/3). Expected reference to James Rodriguez and APP-2023-45871."
    
    # Check for medical condition code (3 points)
    body = submission.get("body", "")
    if "M47.26" in body and ("spinal stenosis" in body.lower() or "spondylosis" in body.lower()):
        score += 3
        feedback["medical_condition"] = "Proper reference to medical condition code (3/3)"
    elif "M47.26" in body:
        score += 2
        feedback["medical_condition"] = "Includes code but missing condition description (2/3)"
    else:
        feedback["medical_condition"] = "Missing proper reference to medical condition code M47.26 (0/3)"
    
    # Check for 9 required information points (18 points, 2 each)
    required_info = [
        ("date of diagnosis", "diagnosis date"),
        ("specific diagnosis", "diagnosis"),
        ("severity classification", "severity"),
        ("treatment plan", "treatment"),
        ("impact on activities", "impact on", "adl", "activities of daily living"),
        ("prognosis", "prognosis"),
        ("surgical", "surgery"),
        ("pain management", "pain"),
        ("imaging", "x-ray", "mri", "ct scan")
    ]
    
    info_points = 0
    info_feedback = []
    
    for i, terms in enumerate(required_info, 1):
        found = any(term.lower() in body.lower() for term in terms)
        if found:
            info_points += 2
            info_feedback.append(f"Item {i}: Found (2/2)")
        else:
            info_feedback.append(f"Item {i}: Not found (0/2). Expected reference to {terms[0]}")
    
    score += info_points
    feedback["required_info"] = {
        "score": f"{info_points}/18 points",
        "details": info_feedback
    }
    
    # Check for 15-day response deadline (3 points)
    if "15 day" in body.lower() or "fifteen day" in body.lower():
        score += 3
        feedback["deadline"] = "Includes 15-day response deadline (3/3)"
    else:
        feedback["deadline"] = "Missing or incorrect response deadline (0/3)"
    
    # Check for professional tone and formatting (5 points)
    professionalism_score = 0
    prof_feedback = []
    
    # Check for salutation
    if re.search(r'dear\s+dr\.?\s+johnson', body.lower()):
        professionalism_score += 1
        prof_feedback.append("Proper salutation (1/1)")
    else:
        prof_feedback.append("Missing or improper salutation (0/1)")
    
    # Check for closing
    if re.search(r'sincerely|regards|respectfully|thank you', body.lower()):
        professionalism_score += 1
        prof_feedback.append("Proper closing (1/1)")
    else:
        prof_feedback.append("Missing or improper closing (0/1)")
    
    # Check for clear paragraphs
    if body.count('\n') >= 3:
        professionalism_score += 1
        prof_feedback.append("Clear paragraph structure (1/1)")
    else:
        prof_feedback.append("Poor paragraph structure (0/1)")
    
    # Check for professional language
    if not re.search(r'slang|inappropriate|unprofessional', body.lower()):
        professionalism_score += 1
        prof_feedback.append("Professional language (1/1)")
    else:
        prof_feedback.append("Unprofessional language detected (0/1)")
    
    # Check for contact information
    if re.search(r'contact|phone|email|fax', body.lower()):
        professionalism_score += 1
        prof_feedback.append("Includes contact information (1/1)")
    else:
        prof_feedback.append("Missing contact information (0/1)")
    
    score += professionalism_score
    feedback["professionalism"] = {
        "score": f"{professionalism_score}/5 points",
        "details": prof_feedback
    }
    
    # Check reference number
    ref_num = submission.get("reference_number", "")
    if ref_num == "APP-2023-45871":
        feedback["reference_number"] = "Correct reference number"
    else:
        feedback["reference_number"] = f"Incorrect reference number. Expected 'APP-2023-45871', got '{ref_num}'"
    
    # Check response deadline format
    deadline = submission.get("response_deadline", "")
    if "15 day" in deadline.lower():
        feedback["response_deadline_format"] = "Acceptable deadline format"
    else:
        feedback["response_deadline_format"] = f"Deadline format may be incorrect: '{deadline}'"
    
    return {
        "score": score,
        "max_points": 35,
        "percentage": round((score / 35) * 100, 2),
        "feedback": feedback
    }

def evaluate_task2(submission, answer_key):
    score = 0
    feedback = {}
    
    # Check for correct final premium calculation (10 points)
    quoted_rate = submission.get("quoted_rate", "")
    # Extract the numeric value from the quoted rate
    match = re.search(r'\$?([\d,]+\.?\d*)', quoted_rate)
    if match:
        submitted_rate = float(match.group(1).replace(',', ''))
        correct_rate = 1428.00
        
        if abs(submitted_rate - correct_rate) < 0.01:  # Exact match
            score += 10
            feedback["premium_calculation"] = "Correct premium calculation (10/10)"
        elif abs(submitted_rate - correct_rate) <= correct_rate * 0.05:  # Within 5%
            score += 7
            feedback["premium_calculation"] = f"Premium calculation close but not exact (7/10). Expected $1,428.00, got ${submitted_rate:.2f}"
        elif abs(submitted_rate - correct_rate) <= correct_rate * 0.1:  # Within 10%
            score += 5
            feedback["premium_calculation"] = f"Premium calculation off by less than 10% (5/10). Expected $1,428.00, got ${submitted_rate:.2f}"
        else:
            feedback["premium_calculation"] = f"Incorrect premium calculation (0/10). Expected $1,428.00, got ${submitted_rate:.2f}"
    else:
        feedback["premium_calculation"] = f"Could not parse premium amount from '{quoted_rate}' (0/10)"
    
    # Check for accurate identification of all rating factors (14 points, 2 each)
    factors = {
        "base_rate": ("$1,400", 2),
        "age_factor": ("1.00", 2),
        "license_factor": ("1.00", 2),
        "driving_record_factor": ("1.20", 2),
        "credit_factor": ("0.85", 2),
        "mileage_factor": ("1.00", 2),
        "territory_factor": ("1.00", 2),
        "multi_policy_factor": ("1.00", 2)
    }
    
    breakdown = submission.get("calculation_breakdown", {})
    factor_score = 0
    factor_feedback = []
    
    for factor, (expected_value, points) in factors.items():
        submitted_value = breakdown.get(factor, "")
        
        # For base_rate, extract numeric value for comparison
        if factor == "base_rate":
            base_match = re.search(r'\$?([\d,]+)', submitted_value)
            if base_match and float(base_match.group(1).replace(',', '')) == 1400:
                factor_score += points
                factor_feedback.append(f"{factor}: Correct (2/2)")
            else:
                factor_feedback.append(f"{factor}: Incorrect (0/2). Expected {expected_value}, got '{submitted_value}'")
        else:
            # For multipliers, compare directly
            if submitted_value == expected_value:
                factor_score += points
                factor_feedback.append(f"{factor}: Correct (2/2)")
            else:
                factor_feedback.append(f"{factor}: Incorrect (0/2). Expected {expected_value}, got '{submitted_value}'")
    
    score += factor_score
    feedback["rating_factors"] = {
        "score": f"{factor_score}/14 points",
        "details": factor_feedback
    }
    
    # Check for clear explanation of calculation process (5 points)
    body = submission.get("body", "")
    explanation_score = 0
    explanation_feedback = []
    
    # Check if calculation formula is included
    if re.search(r'\$1,?400.*1\.00.*1\.00.*1\.20.*0\.85.*1\.00.*1\.00.*1\.00', body.replace(" ", "")):
        explanation_score += 2
        explanation_feedback.append("Includes complete calculation formula (2/2)")
    elif "1.20" in body and "0.85" in body:
        explanation_score += 1
        explanation_feedback.append("Includes partial calculation explanation (1/2)")
    else:
        explanation_feedback.append("Missing calculation formula (0/2)")
    
    # Check if factors are explained
    if "speeding ticket" in body.lower() and "credit score" in body.lower():
        explanation_score += 2
        explanation_feedback.append("Explains key factors affecting premium (2/2)")
    elif "speeding ticket" in body.lower() or "credit score" in body.lower():
        explanation_score += 1
        explanation_feedback.append("Explains some factors affecting premium (1/2)")
    else:
        explanation_feedback.append("Missing explanation of factors (0/2)")
    
    # Check if final premium is clearly stated
    if "$1,428" in body and "annual" in body.lower():
        explanation_score += 1
        explanation_feedback.append("Clearly states final premium (1/1)")
    else:
        explanation_feedback.append("Final premium not clearly stated (0/1)")
    
    score += explanation_score
    feedback["calculation_explanation"] = {
        "score": f"{explanation_score}/5 points",
        "details": explanation_feedback
    }
    
    # Check for reference to correct guidelines section (3 points)
    if "Section 4.5" in body or "section 4.5" in body:
        score += 3
        feedback["guidelines_reference"] = "Correct reference to guidelines section 4.5 (3/3)"
    elif "Section 4" in body or "section 4" in body:
        score += 1
        feedback["guidelines_reference"] = "Partial reference to guidelines section (1/3)"
    else:
        feedback["guidelines_reference"] = "Missing reference to guidelines section 4.5 (0/3)"
    
    # Check for professional tone and clarity (3 points)
    prof_score = 0
    prof_feedback = []
    
    # Check for salutation
    if re.search(r'dear\s+thomas|dear\s+mr\.?\s+wilson', body.lower()):
        prof_score += 1
        prof_feedback.append("Proper salutation (1/1)")
    else:
        prof_feedback.append("Missing or improper salutation (0/1)")
    
    # Check for closing
    if re.search(r'sincerely|regards|respectfully|thank you', body.lower()):
        prof_score += 1
        prof_feedback.append("Proper closing (1/1)")
    else:
        prof_feedback.append("Missing or improper closing (0/1)")
    
    # Check for clear organization
    if body.count('\n') >= 3 and len(body) > 200:
        prof_score += 1
        prof_feedback.append("Clear organization and sufficient detail (1/1)")
    else:
        prof_feedback.append("Poor organization or insufficient detail (0/1)")
    
    score += prof_score
    feedback["professionalism"] = {
        "score": f"{prof_score}/3 points",
        "details": prof_feedback
    }
    
    return {
        "score": score,
        "max_points": 35,
        "percentage": round((score / 35) * 100, 2),
        "feedback": feedback
    }

def evaluate_task3(submission, answer_key):
    score = 0
    feedback = {}
    
    # Check for correct policy classification (8 points)
    policy_class = submission.get("policy_classification", "")
    if policy_class == "Rated A":
        score += 8
        feedback["policy_classification"] = "Correct policy classification (8/8)"
    else:
        feedback["policy_classification"] = f"Incorrect policy classification (0/8). Expected 'Rated A', got '{policy_class}'"
        # This is a critical error - automatic failure
        feedback["critical_error"] = "Critical Error: Incorrect policy classification"
    
    # Check for correct premium adjustment (5 points)
    premium_adj = submission.get("premium_adjustment", "")
    if "+25% from Standard" in premium_adj:
        score += 5
        feedback["premium_adjustment"] = "Correct premium adjustment (5/5)"
    elif "25%" in premium_adj and "standard" in premium_adj.lower():
        score += 4
        feedback["premium_adjustment"] = "Mostly correct premium adjustment (4/5)"
    elif "25%" in premium_adj:
        score += 2
        feedback["premium_adjustment"] = "Partially correct premium adjustment (2/5)"
    else:
        feedback["premium_adjustment"] = f"Incorrect premium adjustment (0/5). Expected '+25% from Standard', got '{premium_adj}'"
    
    # Check for correct guideline reference (3 points)
    guideline_ref = submission.get("guideline_reference", "")
    if guideline_ref == "UW-LI-5.3.27":
        score += 3
        feedback["guideline_reference"] = "Correct guideline reference (3/3)"
    else:
        feedback["guideline_reference"] = f"Incorrect guideline reference (0/3). Expected 'UW-LI-5.3.27', got '{guideline_ref}'"
    
    # Check for accurate explanation of all rating factors (10 points)
    body = submission.get("body", "")
    factors_score = 0
    factors_feedback = []
    
    # Check for age at diagnosis explanation
    if re.search(r'(age 45|diagnosed at 45|between 40-50|40-50)', body):
        factors_score += 2
        factors_feedback.append("Correctly explains age at diagnosis factor (2/2)")
    else:
        factors_feedback.append("Missing or incorrect explanation of age at diagnosis factor (0/2)")
    
    # Check for HbA1c explanation
    if re.search(r'(HbA1c.{1,20}7\.4%|7\.4%.{1,20}HbA1c|7\.0-7\.5%)', body):
        factors_score += 2
        factors_feedback.append("Correctly explains HbA1c factor (2/2)")
    else:
        factors_feedback.append("Missing or incorrect explanation of HbA1c factor (0/2)")
    
    # Check for BMI explanation
    if re.search(r'(BMI.{1,20}31\.2|31\.2.{1,20}BMI|30-32)', body):
        factors_score += 2
        factors_feedback.append("Correctly explains BMI factor (2/2)")
    else:
        factors_feedback.append("Missing or incorrect explanation of BMI factor (0/2)")
    
    # Check for blood pressure explanation
    if re.search(r'(blood pressure.{1,30}142/92|142/92.{1,30}blood pressure|controlled but elevated)', body.lower()):
        factors_score += 2
        factors_feedback.append("Correctly explains blood pressure factor (2/2)")
    else:
        factors_feedback.append("Missing or incorrect explanation of blood pressure factor (0/2)")
    
    # Check for cardiovascular risk factors explanation
    if re.search(r'(cardiovascular risk|cholesterol|smoking history|history of smoking)', body.lower()):
        factors_score += 2
        factors_feedback.append("Correctly explains cardiovascular risk factors (2/2)")
    else:
        factors_feedback.append("Missing or incorrect explanation of cardiovascular risk factors (0/2)")
    
    score += factors_score
    feedback["rating_factors_explanation"] = {
        "score": f"{factors_score}/10 points",
        "details": factors_feedback
    }
    
    # Check for professional tone and clarity (4 points)
    prof_score = 0
    prof_feedback = []
    
    # Check for salutation
    if re.search(r'dear\s+maria|dear\s+ms\.?\s+garcia', body.lower()):
        prof_score += 1
        prof_feedback.append("Proper salutation (1/1)")
    else:
        prof_feedback.append("Missing or improper salutation (0/1)")
    
    # Check for closing
    if re.search(r'sincerely|regards|respectfully|thank you', body.lower()):
        prof_score += 1
        prof_feedback.append("Proper closing (1/1)")
    else:
        prof_feedback.append("Missing or improper closing (0/1)")
    
    # Check for clear organization
    if body.count('\n') >= 3:
        prof_score += 1
        prof_feedback.append("Clear organization (1/1)")
    else:
        prof_feedback.append("Poor organization (0/1)")
    
    # Check for appropriate language (not too technical)
    if len(body) > 200 and not re.search(r'unprofessional|inappropriate', body.lower()):
        prof_score += 1
        prof_feedback.append("Appropriate language and sufficient detail (1/1)")
    else:
        prof_feedback.append("Inappropriate language or insufficient detail (0/1)")
    
    score += prof_score
    feedback["professionalism"] = {
        "score": f"{prof_score}/4 points",
        "details": prof_feedback
    }
    
    return {
        "score": score,
        "max_points": 30,
        "percentage": round((score / 30) * 100, 2),
        "feedback": feedback
    }

def check_critical_errors(task_results):
    critical_errors = []
    
    # Check Task 2 premium calculation (more than 10% off is critical)
    task2 = task_results.get("task2", {})
    premium_feedback = task2.get("feedback", {}).get("premium_calculation", "")
    if "off by" in premium_feedback and "10%" in premium_feedback:
        critical_errors.append("Critical Error in Task 2: Premium calculation off by more than 10%")
    
    # Check Task 3 policy classification (anything other than "Rated A" is critical)
    task3 = task_results.get("task3", {})
    if "critical_error" in task3.get("feedback", {}):
        critical_errors.append(task3["feedback"]["critical_error"])
    
    # Check for fabricated information (this is harder to detect automatically)
    # Would need more sophisticated NLP to detect fabricated information reliably
    
    return critical_errors

def evaluate_submission(submission, answer_key):
    results = {}
    
    # Evaluate each task
    results["task1"] = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    results["task2"] = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    results["task3"] = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    
    # Calculate total score
    total_score = results["task1"]["score"] + results["task2"]["score"] + results["task3"]["score"]
    max_points = results["task1"]["max_points"] + results["task2"]["max_points"] + results["task3"]["max_points"]
    
    # Check for critical errors
    critical_errors = check_critical_errors(results)
    
    # Determine if passed
    passed = total_score >= 80 and results["task1"]["score"] >= 20 and results["task2"]["score"] >= 20 and results["task3"]["score"] >= 20 and not critical_errors
    
    # Compile final results
    final_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round((total_score / max_points) * 100, 2),
        "total_points": total_score,
        "max_points": max_points,
        "passed": passed,
        "task_results": results,
        "critical_errors": critical_errors
    }
    
    return final_results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    if results["passed"]:
        print("PASSED")
    else:
        print("FAILED")
        if results["critical_errors"]:
            for error in results["critical_errors"]:
                print(f"- {error}")

if __name__ == "__main__":
    main()