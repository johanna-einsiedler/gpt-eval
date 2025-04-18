#!/usr/bin/env python3

import json
import sys
import os
from typing import Dict, List, Any, Union

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Writing a Product Specification."""
    score = 0
    max_score = 40
    feedback = []
    
    submission_spec = submission.get("task1", {}).get("specification", {})
    answer_spec = answer_key.get("task1", {}).get("specification", {})
    
    # General Information section (5 points)
    general_info_score = 0
    if submission_spec.get("general_information"):
        sub_general = submission_spec.get("general_information", {})
        ans_general = answer_spec.get("general_information", {})
        
        fields_correct = 0
        total_fields = len(ans_general)
        
        for key, expected in ans_general.items():
            if key in sub_general and sub_general[key].strip():
                if expected.lower() in sub_general[key].lower():
                    fields_correct += 1
        
        if total_fields > 0:
            general_info_score = round(5 * fields_correct / total_fields, 1)
        
        feedback.append(f"General Information: {fields_correct}/{total_fields} fields correct - {general_info_score}/5 points")
    else:
        feedback.append("General Information section missing - 0/5 points")
    
    score += general_info_score
    
    # Technical Requirements section (10 points)
    tech_req_score = 0
    if submission_spec.get("technical_requirements"):
        sub_tech = submission_spec.get("technical_requirements", {})
        ans_tech = answer_spec.get("technical_requirements", {})
        
        fields_correct = 0
        total_fields = len(ans_tech)
        
        for key, expected in ans_tech.items():
            if key in sub_tech and sub_tech[key].strip():
                if expected.lower() in sub_tech[key].lower():
                    fields_correct += 1
        
        if total_fields > 0:
            tech_req_score = round(10 * fields_correct / total_fields, 1)
        
        feedback.append(f"Technical Requirements: {fields_correct}/{total_fields} fields correct - {tech_req_score}/10 points")
    else:
        feedback.append("Technical Requirements section missing - 0/10 points")
    
    score += tech_req_score
    
    # Material Requirements section (8 points)
    material_req_score = 0
    if submission_spec.get("material_requirements"):
        sub_material = submission_spec.get("material_requirements", {})
        ans_material = answer_spec.get("material_requirements", {})
        
        fields_correct = 0
        total_fields = len(ans_material)
        
        for key, expected in ans_material.items():
            if key in sub_material and sub_material[key].strip():
                if expected.lower() in sub_material[key].lower():
                    fields_correct += 1
        
        if total_fields > 0:
            material_req_score = round(8 * fields_correct / total_fields, 1)
        
        feedback.append(f"Material Requirements: {fields_correct}/{total_fields} fields correct - {material_req_score}/8 points")
    else:
        feedback.append("Material Requirements section missing - 0/8 points")
    
    score += material_req_score
    
    # Performance Requirements section (7 points)
    perf_req_score = 0
    if submission_spec.get("performance_requirements"):
        sub_perf = submission_spec.get("performance_requirements", {})
        ans_perf = answer_spec.get("performance_requirements", {})
        
        fields_correct = 0
        total_fields = len(ans_perf)
        
        for key, expected in ans_perf.items():
            if key in sub_perf and sub_perf[key].strip():
                if expected.lower() in sub_perf[key].lower():
                    fields_correct += 1
        
        if total_fields > 0:
            perf_req_score = round(7 * fields_correct / total_fields, 1)
        
        feedback.append(f"Performance Requirements: {fields_correct}/{total_fields} fields correct - {perf_req_score}/7 points")
    else:
        feedback.append("Performance Requirements section missing - 0/7 points")
    
    score += perf_req_score
    
    # Certification Requirements section (5 points)
    cert_req_score = 0
    if submission_spec.get("certification_requirements"):
        sub_cert = submission_spec.get("certification_requirements", {})
        ans_cert = answer_spec.get("certification_requirements", {})
        
        standards_score = 0
        certifications_score = 0
        
        # Check required standards
        if "required_standards" in sub_cert and "required_standards" in ans_cert:
            sub_standards = set([s.lower() for s in sub_cert.get("required_standards", [])])
            ans_standards = set([s.lower() for s in ans_cert.get("required_standards", [])])
            
            if ans_standards and sub_standards:
                overlap = len(sub_standards.intersection(ans_standards))
                standards_score = round(2.5 * overlap / len(ans_standards), 1)
        
        # Check required certifications
        if "required_certifications" in sub_cert and "required_certifications" in ans_cert:
            sub_certifications = set([s.lower() for s in sub_cert.get("required_certifications", [])])
            ans_certifications = set([s.lower() for s in ans_cert.get("required_certifications", [])])
            
            if ans_certifications and sub_certifications:
                overlap = len(sub_certifications.intersection(ans_certifications))
                certifications_score = round(2.5 * overlap / len(ans_certifications), 1)
        
        cert_req_score = standards_score + certifications_score
        feedback.append(f"Certification Requirements: {cert_req_score}/5 points")
    else:
        feedback.append("Certification Requirements section missing - 0/5 points")
    
    score += cert_req_score
    
    # Testing Requirements section (5 points)
    test_req_score = 0
    if submission_spec.get("testing_requirements"):
        sub_test = submission_spec.get("testing_requirements", {})
        ans_test = answer_spec.get("testing_requirements", {})
        
        protocols_score = 0
        criteria_score = 0
        
        # Check test protocols
        if "test_protocols" in sub_test and "test_protocols" in ans_test:
            sub_protocols = set([p.lower() for p in sub_test.get("test_protocols", [])])
            
            # Count number of protocols that contain key phrases from answer key
            matches = 0
            for ans_protocol in ans_test.get("test_protocols", []):
                for sub_protocol in sub_protocols:
                    # Check if major parts of the expected protocol are in the submission
                    key_parts = ans_protocol.lower().split()
                    if sum(part in sub_protocol for part in key_parts) >= len(key_parts) / 2:
                        matches += 1
                        break
            
            ans_count = len(ans_test.get("test_protocols", []))
            if ans_count > 0:
                protocols_score = round(3 * min(matches, ans_count) / ans_count, 1)
        
        # Check acceptance criteria
        if "acceptance_criteria" in sub_test and "acceptance_criteria" in ans_test:
            sub_criteria = set([c.lower() for c in sub_test.get("acceptance_criteria", [])])
            
            # Count number of criteria that contain key phrases from answer key
            matches = 0
            for ans_criterion in ans_test.get("acceptance_criteria", []):
                for sub_criterion in sub_criteria:
                    # Check if major parts of the expected criterion are in the submission
                    key_parts = ans_criterion.lower().split()
                    if sum(part in sub_criterion for part in key_parts) >= len(key_parts) / 2:
                        matches += 1
                        break
            
            ans_count = len(ans_test.get("acceptance_criteria", []))
            if ans_count > 0:
                criteria_score = round(2 * min(matches, ans_count) / ans_count, 1)
        
        test_req_score = protocols_score + criteria_score
        feedback.append(f"Testing Requirements: {test_req_score}/5 points")
    else:
        feedback.append("Testing Requirements section missing - 0/5 points")
    
    score += test_req_score
    
    # Round the final score to 1 decimal place
    score = round(score, 1)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round(score / max_score * 100, 1),
        "feedback": feedback
    }

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Reviewing and Correcting Flawed Specifications."""
    score = 0
    max_score = 35
    feedback = []
    
    # Evaluate identified errors (20 points, 4 points each)
    sub_errors = submission.get("task2", {}).get("errors", [])
    ans_errors = answer_key.get("task2", {}).get("errors", [])
    
    error_descriptions = []
    for error in sub_errors:
        if "description" in error:
            error_descriptions.append(error["description"].lower())
    
    correct_errors = 0
    error_matches = []
    
    # For each answer key error, check if it was identified
    for ans_error in ans_errors:
        matched = False
        ans_desc = ans_error.get("description", "").lower()
        
        # Extract key words from the error description
        key_words = []
        for word in ans_desc.split():
            if len(word) > 4 and word not in ["incorrect", "impossible", "inadequate", "configuration"]:
                key_words.append(word)
        
        # Check each submission error
        for i, sub_desc in enumerate(error_descriptions):
            # Count matching key words
            matching_words = sum(1 for word in key_words if word in sub_desc)
            
            # If enough key words match, consider it a match
            if matching_words >= len(key_words) / 3:
                matched = True
                error_matches.append(i)
                break
        
        if matched:
            correct_errors += 1
    
    error_score = round(20 * correct_errors / 5, 1)
    feedback.append(f"Error identification: {correct_errors}/5 errors correctly identified - {error_score}/20 points")
    
    score += error_score
    
    # Evaluate corrections (15 points, 3 points each)
    sub_corrections = submission.get("task2", {}).get("corrections", {})
    ans_corrections = answer_key.get("task2", {}).get("corrections", {})
    
    correct_solutions = 0
    
    # For each error in the answer key, check if a correct solution was provided
    for i in range(1, 6):
        error_key = f"error{i}"
        
        if error_key in sub_corrections and error_key in ans_corrections:
            sub_correct = sub_corrections[error_key].get("correct", "").lower()
            ans_correct = ans_corrections[error_key].get("correct", "").lower()
            
            # Extract key phrases from the answer key correction
            key_phrases = []
            for phrase in ans_correct.split(" or "):
                key_phrases.append(phrase.strip())
            
            # Check if any key phrase is in the submission
            if any(phrase in sub_correct for phrase in key_phrases):
                correct_solutions += 1
            # Check if similar technical terms are used
            elif any(sum(1 for word in phrase.split() if word in sub_correct) >= len(phrase.split()) / 2 for phrase in key_phrases):
                correct_solutions += 0.5
    
    correction_score = round(15 * correct_solutions / 5, 1)
    feedback.append(f"Corrections: {correct_solutions}/5 correct solutions provided - {correction_score}/15 points")
    
    score += correction_score
    
    # Round the final score to 1 decimal place
    score = round(score, 1)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round(score / max_score * 100, 1),
        "feedback": feedback
    }

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Evaluating Competing Products."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check recommended model (10 points)
    sub_model = submission.get("task3", {}).get("recommended_model", "")
    ans_model = answer_key.get("task3", {}).get("recommended_model", "")
    
    model_score = 10 if sub_model == ans_model else 0
    feedback.append(f"Recommended model: {'Correct' if model_score > 0 else 'Incorrect'} - {model_score}/10 points")
    
    score += model_score
    
    # Check requirements met (10 points)
    sub_met = submission.get("task3", {}).get("technical_requirements_met", [])
    ans_met = answer_key.get("task3", {}).get("technical_requirements_met", [])
    
    # Extract requirements from submission
    sub_met_reqs = set()
    for req in sub_met:
        if "requirement" in req:
            sub_met_reqs.add(req["requirement"].lower())
    
    # Extract requirements from answer key
    ans_met_reqs = set()
    for req in ans_met:
        if "requirement" in req:
            ans_met_reqs.add(req["requirement"].lower())
    
    # Count correct requirements met
    correct_met = len(sub_met_reqs.intersection(ans_met_reqs))
    incorrect_met = len(sub_met_reqs - ans_met_reqs)
    
    # Calculate score for requirements met
    if len(ans_met_reqs) > 0:
        met_score = round(10 * (correct_met - 0.5 * incorrect_met) / len(ans_met_reqs), 1)
        met_score = max(0, met_score)  # Ensure score is not negative
    else:
        met_score = 0
    
    feedback.append(f"Requirements met: {correct_met}/{len(ans_met_reqs)} correct - {met_score}/10 points")
    
    score += met_score
    
    # Check requirements not met (5 points)
    sub_not_met = submission.get("task3", {}).get("technical_requirements_not_met", [])
    ans_not_met = answer_key.get("task3", {}).get("technical_requirements_not_met", [])
    
    # Extract requirements from submission
    sub_not_met_reqs = set()
    for req in sub_not_met:
        if "requirement" in req:
            sub_not_met_reqs.add(req["requirement"].lower())
    
    # Extract requirements from answer key
    ans_not_met_reqs = set()
    for req in ans_not_met:
        if "requirement" in req:
            ans_not_met_reqs.add(req["requirement"].lower())
    
    # Count correct requirements not met
    correct_not_met = len(sub_not_met_reqs.intersection(ans_not_met_reqs))
    incorrect_not_met = len(sub_not_met_reqs - ans_not_met_reqs)
    
    # Calculate score for requirements not met
    if len(ans_not_met_reqs) > 0:
        not_met_score = round(5 * (correct_not_met - 0.5 * incorrect_not_met) / len(ans_not_met_reqs), 1)
        not_met_score = max(0, not_met_score)  # Ensure score is not negative
    else:
        # Answer key has no "not met" requirements, so check if submission also has none
        not_met_score = 5 if len(sub_not_met_reqs) == 0 else 0
    
    feedback.append(f"Requirements not met: {'Correct' if not_met_score == 5 else 'Incorrect'} - {not_met_score}/5 points")
    
    score += not_met_score
    
    # Round the final score to 1 decimal place
    score = round(score, 1)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round(score / max_score * 100, 1),
        "feedback": feedback
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the full submission against the answer key."""
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_percentage = round(total_score / max_score * 100, 1)
    
    # Determine if the candidate passed
    passed = overall_percentage >= 70 and (
        task1_results["percentage"] >= 50 and
        task2_results["percentage"] >= 50 and
        task3_results["percentage"] >= 50
    )
    
    results = {
        "overall_score": overall_percentage,
        "passed": passed,
        "total_points": total_score,
        "max_points": max_score,
        "tasks": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results
        },
        "passing_criteria": {
            "overall_score_requirement": "≥ 70%",
            "per_task_requirement": "≥ 50% per task",
            "overall_score_achieved": f"{overall_percentage}%",
            "task1_score_achieved": f"{task1_results['percentage']}%",
            "task2_score_achieved": f"{task2_results['percentage']}%",
            "task3_score_achieved": f"{task3_results['percentage']}%"
        }
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py submission_file.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()