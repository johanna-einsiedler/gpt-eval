#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Union

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_section1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 1: Form Review and Error Detection."""
    results = {
        "form1040_client_a_errors": {"score": 0, "max_points": 14, "details": []},
        "schedule_c_client_b_errors": {"score": 0, "max_points": 8, "details": []},
        "form_8949_client_c_missing_fields": {"score": 0, "max_points": 8, "details": []}
    }
    
    # Evaluate Form 1040 Client A errors (2 points per error)
    submission_errors = submission.get("section1", {}).get("form1040_client_a_errors", [])
    answer_key_errors = answer_key.get("section1", {}).get("form1040_client_a_errors", [])
    
    found_errors = []
    for sub_error in submission_errors:
        error_matched = False
        for key_error in answer_key_errors:
            # Check if the field matches
            if sub_error.get("field") == key_error.get("field"):
                error_matched = True
                if sub_error.get("error_type") == key_error.get("error_type"):
                    # Full points if error type and field match
                    if key_error.get("field") not in found_errors:
                        results["form1040_client_a_errors"]["score"] += 2
                        found_errors.append(key_error.get("field"))
                        results["form1040_client_a_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 2,
                            "max_points": 2,
                            "correct": True
                        })
                else:
                    # Partial credit (1 point) if field is correct but error type is wrong
                    if key_error.get("field") not in found_errors:
                        results["form1040_client_a_errors"]["score"] += 1
                        found_errors.append(key_error.get("field"))
                        results["form1040_client_a_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 1,
                            "max_points": 2,
                            "correct": False,
                            "reason": "Incorrect error type"
                        })
                break
        
        if not error_matched:
            # False positive - no points deducted but noted
            results["form1040_client_a_errors"]["details"].append({
                "field": sub_error.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - error doesn't exist"
            })
    
    # Note missed errors
    for key_error in answer_key_errors:
        if key_error.get("field") not in found_errors:
            results["form1040_client_a_errors"]["details"].append({
                "field": key_error.get("field"),
                "points_earned": 0,
                "max_points": 2,
                "correct": False,
                "reason": "Error not identified"
            })
    
    # Evaluate Schedule C Client B errors (4 points per error)
    submission_errors = submission.get("section1", {}).get("schedule_c_client_b_errors", [])
    answer_key_errors = answer_key.get("section1", {}).get("schedule_c_client_b_errors", [])
    
    found_errors = []
    for sub_error in submission_errors:
        error_matched = False
        for key_error in answer_key_errors:
            if sub_error.get("field") == key_error.get("field"):
                error_matched = True
                if sub_error.get("error_type") == key_error.get("error_type"):
                    # Full points if error type and field match
                    if key_error.get("field") not in found_errors:
                        results["schedule_c_client_b_errors"]["score"] += 4
                        found_errors.append(key_error.get("field"))
                        results["schedule_c_client_b_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 4,
                            "max_points": 4,
                            "correct": True
                        })
                else:
                    # Partial credit (2 points) if field is correct but error type is wrong
                    if key_error.get("field") not in found_errors:
                        results["schedule_c_client_b_errors"]["score"] += 2
                        found_errors.append(key_error.get("field"))
                        results["schedule_c_client_b_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 2,
                            "max_points": 4,
                            "correct": False,
                            "reason": "Incorrect error type"
                        })
                break
        
        if not error_matched:
            # False positive - no points deducted but noted
            results["schedule_c_client_b_errors"]["details"].append({
                "field": sub_error.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - error doesn't exist"
            })
    
    # Note missed errors
    for key_error in answer_key_errors:
        if key_error.get("field") not in found_errors:
            results["schedule_c_client_b_errors"]["details"].append({
                "field": key_error.get("field"),
                "points_earned": 0,
                "max_points": 4,
                "correct": False,
                "reason": "Error not identified"
            })
    
    # Evaluate Form 8949 Client C missing fields (2 points per missing field)
    submission_fields = submission.get("section1", {}).get("form_8949_client_c_missing_fields", [])
    answer_key_fields = answer_key.get("section1", {}).get("form_8949_client_c_missing_fields", [])
    
    found_fields = []
    for sub_field in submission_fields:
        field_matched = False
        for key_field in answer_key_fields:
            if sub_field.get("field") == key_field.get("field"):
                field_matched = True
                # Full points if field matches
                if key_field.get("field") not in found_fields:
                    results["form_8949_client_c_missing_fields"]["score"] += 2
                    found_fields.append(key_field.get("field"))
                    results["form_8949_client_c_missing_fields"]["details"].append({
                        "field": key_field.get("field"),
                        "points_earned": 2,
                        "max_points": 2,
                        "correct": True
                    })
                break
        
        if not field_matched:
            # False positive - no points deducted but noted
            results["form_8949_client_c_missing_fields"]["details"].append({
                "field": sub_field.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - field isn't actually missing"
            })
    
    # Note missed fields
    for key_field in answer_key_fields:
        if key_field.get("field") not in found_fields:
            results["form_8949_client_c_missing_fields"]["details"].append({
                "field": key_field.get("field"),
                "points_earned": 0,
                "max_points": 2,
                "correct": False,
                "reason": "Missing field not identified"
            })
    
    return results

def evaluate_section2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 2: Numerical Verification."""
    results = {
        "tax_calculation_client_d_errors": {"score": 0, "max_points": 12, "details": []},
        "income_reconciliation_client_e": {"score": 0, "max_points": 4, "details": {}},
        "estimated_tax_client_f": {"score": 0, "max_points": 4, "details": {}}
    }
    
    # Evaluate Tax Calculation Client D errors (3 points per error)
    submission_errors = submission.get("section2", {}).get("tax_calculation_client_d_errors", [])
    answer_key_errors = answer_key.get("section2", {}).get("tax_calculation_client_d_errors", [])
    
    found_errors = []
    for sub_error in submission_errors:
        error_matched = False
        for key_error in answer_key_errors:
            if sub_error.get("field") == key_error.get("field"):
                error_matched = True
                # Check if correct value matches
                if abs(float(sub_error.get("correct_value", 0)) - float(key_error.get("correct_value", 0))) < 0.01:
                    # Full points if field and correct value match
                    if key_error.get("field") not in found_errors:
                        results["tax_calculation_client_d_errors"]["score"] += 3
                        found_errors.append(key_error.get("field"))
                        results["tax_calculation_client_d_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 3,
                            "max_points": 3,
                            "correct": True
                        })
                else:
                    # Partial credit (1 point) if field is correct but value is wrong
                    if key_error.get("field") not in found_errors:
                        results["tax_calculation_client_d_errors"]["score"] += 1
                        found_errors.append(key_error.get("field"))
                        results["tax_calculation_client_d_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 1,
                            "max_points": 3,
                            "correct": False,
                            "reason": "Incorrect calculation of value"
                        })
                break
        
        if not error_matched:
            # False positive - no points deducted but noted
            results["tax_calculation_client_d_errors"]["details"].append({
                "field": sub_error.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - error doesn't exist"
            })
    
    # Note missed errors
    for key_error in answer_key_errors:
        if key_error.get("field") not in found_errors:
            results["tax_calculation_client_d_errors"]["details"].append({
                "field": key_error.get("field"),
                "points_earned": 0,
                "max_points": 3,
                "correct": False,
                "reason": "Error not identified"
            })
    
    # Evaluate Income Reconciliation Client E (all or nothing - 4 points)
    sub_reconciliation = submission.get("section2", {}).get("income_reconciliation_client_e", {})
    key_reconciliation = answer_key.get("section2", {}).get("income_reconciliation_client_e", {})
    
    if sub_reconciliation.get("discrepancy_found") == key_reconciliation.get("discrepancy_found"):
        results["income_reconciliation_client_e"]["score"] = 4
        results["income_reconciliation_client_e"]["details"] = {
            "points_earned": 4,
            "max_points": 4,
            "correct": True
        }
    else:
        results["income_reconciliation_client_e"]["details"] = {
            "points_earned": 0,
            "max_points": 4,
            "correct": False,
            "reason": "Incorrect assessment of discrepancy"
        }
    
    # Evaluate Estimated Tax Client F (all or nothing - 4 points)
    sub_estimated_tax = submission.get("section2", {}).get("estimated_tax_client_f", {})
    key_estimated_tax = answer_key.get("section2", {}).get("estimated_tax_client_f", {})
    
    # Check if reported and correct payments match
    reported_match = abs(float(sub_estimated_tax.get("reported_payments", 0)) - float(key_estimated_tax.get("reported_payments", 0))) < 0.01
    correct_match = abs(float(sub_estimated_tax.get("correct_payments", 0)) - float(key_estimated_tax.get("correct_payments", 0))) < 0.01
    discrepancy_match = abs(float(sub_estimated_tax.get("discrepancy_amount", 0)) - float(key_estimated_tax.get("discrepancy_amount", 0))) < 0.01
    
    if reported_match and correct_match and discrepancy_match:
        results["estimated_tax_client_f"]["score"] = 4
        results["estimated_tax_client_f"]["details"] = {
            "points_earned": 4,
            "max_points": 4,
            "correct": True
        }
    else:
        results["estimated_tax_client_f"]["details"] = {
            "points_earned": 0,
            "max_points": 4,
            "correct": False,
            "reason": "Incorrect assessment of estimated tax payments"
        }
    
    return results

def evaluate_section3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 3: Data Entry Validation."""
    results = {
        "client_g_discrepancies": {"score": 0, "max_points": 8, "details": []},
        "client_h_dependent_errors": {"score": 0, "max_points": 6, "details": []},
        "client_i_contact_errors": {"score": 0, "max_points": 6, "details": []}
    }
    
    # Evaluate Client G discrepancies (4 points per discrepancy)
    submission_discrepancies = submission.get("section3", {}).get("client_g_discrepancies", [])
    answer_key_discrepancies = answer_key.get("section3", {}).get("client_g_discrepancies", [])
    
    found_discrepancies = []
    for sub_discrepancy in submission_discrepancies:
        discrepancy_matched = False
        for key_discrepancy in answer_key_discrepancies:
            if sub_discrepancy.get("field") == key_discrepancy.get("field"):
                discrepancy_matched = True
                # Check if reported and correct values match
                reported_match = sub_discrepancy.get("reported_value") == key_discrepancy.get("reported_value")
                correct_match = sub_discrepancy.get("correct_value") == key_discrepancy.get("correct_value")
                
                if reported_match and correct_match:
                    # Full points if field and values match
                    if key_discrepancy.get("field") not in found_discrepancies:
                        results["client_g_discrepancies"]["score"] += 4
                        found_discrepancies.append(key_discrepancy.get("field"))
                        results["client_g_discrepancies"]["details"].append({
                            "field": key_discrepancy.get("field"),
                            "points_earned": 4,
                            "max_points": 4,
                            "correct": True
                        })
                else:
                    # Partial credit (2 points) if field is correct but values are wrong
                    if key_discrepancy.get("field") not in found_discrepancies:
                        results["client_g_discrepancies"]["score"] += 2
                        found_discrepancies.append(key_discrepancy.get("field"))
                        results["client_g_discrepancies"]["details"].append({
                            "field": key_discrepancy.get("field"),
                            "points_earned": 2,
                            "max_points": 4,
                            "correct": False,
                            "reason": "Incorrect reported or correct value"
                        })
                break
        
        if not discrepancy_matched:
            # False positive - no points deducted but noted
            results["client_g_discrepancies"]["details"].append({
                "field": sub_discrepancy.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - discrepancy doesn't exist"
            })
    
    # Note missed discrepancies
    for key_discrepancy in answer_key_discrepancies:
        if key_discrepancy.get("field") not in found_discrepancies:
            results["client_g_discrepancies"]["details"].append({
                "field": key_discrepancy.get("field"),
                "points_earned": 0,
                "max_points": 4,
                "correct": False,
                "reason": "Discrepancy not identified"
            })
    
    # Evaluate Client H dependent errors (6 points for the SSN error)
    submission_errors = submission.get("section3", {}).get("client_h_dependent_errors", [])
    answer_key_errors = answer_key.get("section3", {}).get("client_h_dependent_errors", [])
    
    found_errors = []
    for sub_error in submission_errors:
        error_matched = False
        for key_error in answer_key_errors:
            if (sub_error.get("dependent_name") == key_error.get("dependent_name") and 
                sub_error.get("field") == key_error.get("field")):
                error_matched = True
                # Check if reported and correct values match
                reported_match = sub_error.get("reported_value") == key_error.get("reported_value")
                correct_match = sub_error.get("correct_value") == key_error.get("correct_value")
                
                if reported_match and correct_match:
                    # Full points if dependent, field, and values match
                    error_key = f"{key_error.get('dependent_name')}_{key_error.get('field')}"
                    if error_key not in found_errors:
                        results["client_h_dependent_errors"]["score"] += 6
                        found_errors.append(error_key)
                        results["client_h_dependent_errors"]["details"].append({
                            "dependent_name": key_error.get("dependent_name"),
                            "field": key_error.get("field"),
                            "points_earned": 6,
                            "max_points": 6,
                            "correct": True
                        })
                else:
                    # Partial credit (3 points) if dependent and field are correct but values are wrong
                    error_key = f"{key_error.get('dependent_name')}_{key_error.get('field')}"
                    if error_key not in found_errors:
                        results["client_h_dependent_errors"]["score"] += 3
                        found_errors.append(error_key)
                        results["client_h_dependent_errors"]["details"].append({
                            "dependent_name": key_error.get("dependent_name"),
                            "field": key_error.get("field"),
                            "points_earned": 3,
                            "max_points": 6,
                            "correct": False,
                            "reason": "Incorrect reported or correct value"
                        })
                break
        
        if not error_matched:
            # False positive - no points deducted but noted
            results["client_h_dependent_errors"]["details"].append({
                "dependent_name": sub_error.get("dependent_name"),
                "field": sub_error.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - error doesn't exist"
            })
    
    # Note missed errors
    for key_error in answer_key_errors:
        error_key = f"{key_error.get('dependent_name')}_{key_error.get('field')}"
        if error_key not in found_errors:
            results["client_h_dependent_errors"]["details"].append({
                "dependent_name": key_error.get("dependent_name"),
                "field": key_error.get("field"),
                "points_earned": 0,
                "max_points": 6,
                "correct": False,
                "reason": "Error not identified"
            })
    
    # Evaluate Client I contact errors (6 points for the ZIP code error)
    submission_errors = submission.get("section3", {}).get("client_i_contact_errors", [])
    answer_key_errors = answer_key.get("section3", {}).get("client_i_contact_errors", [])
    
    found_errors = []
    for sub_error in submission_errors:
        error_matched = False
        for key_error in answer_key_errors:
            if sub_error.get("field") == key_error.get("field"):
                error_matched = True
                # Check if reported and correct values match
                reported_match = sub_error.get("reported_value") == key_error.get("reported_value")
                correct_match = sub_error.get("correct_value") == key_error.get("correct_value")
                
                if reported_match and correct_match:
                    # Full points if field and values match
                    if key_error.get("field") not in found_errors:
                        results["client_i_contact_errors"]["score"] += 6
                        found_errors.append(key_error.get("field"))
                        results["client_i_contact_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 6,
                            "max_points": 6,
                            "correct": True
                        })
                else:
                    # Partial credit (3 points) if field is correct but values are wrong
                    if key_error.get("field") not in found_errors:
                        results["client_i_contact_errors"]["score"] += 3
                        found_errors.append(key_error.get("field"))
                        results["client_i_contact_errors"]["details"].append({
                            "field": key_error.get("field"),
                            "points_earned": 3,
                            "max_points": 6,
                            "correct": False,
                            "reason": "Incorrect reported or correct value"
                        })
                break
        
        if not error_matched:
            # False positive - no points deducted but noted
            results["client_i_contact_errors"]["details"].append({
                "field": sub_error.get("field"),
                "points_earned": 0,
                "max_points": 0,
                "correct": False,
                "reason": "False positive - error doesn't exist"
            })
    
    # Note missed errors
    for key_error in answer_key_errors:
        if key_error.get("field") not in found_errors:
            results["client_i_contact_errors"]["details"].append({
                "field": key_error.get("field"),
                "points_earned": 0,
                "max_points": 6,
                "correct": False,
                "reason": "Error not identified"
            })
    
    return results

def calculate_section_scores(evaluation_results: Dict) -> Dict:
    """Calculate scores for each section and overall score."""
    section_scores = {
        "section1": {
            "score": 0,
            "max_points": 30,
            "percentage": 0,
            "pass_threshold": 60
        },
        "section2": {
            "score": 0,
            "max_points": 20,
            "percentage": 0,
            "pass_threshold": 60
        },
        "section3": {
            "score": 0,
            "max_points": 20,
            "percentage": 0,
            "pass_threshold": 60
        },
        "overall": {
            "score": 0,
            "max_points": 70,
            "percentage": 0,
            "pass_threshold": 70,
            "passed": False
        }
    }
    
    # Calculate Section 1 score
    section1_score = (
        evaluation_results["section1"]["form1040_client_a_errors"]["score"] +
        evaluation_results["section1"]["schedule_c_client_b_errors"]["score"] +
        evaluation_results["section1"]["form_8949_client_c_missing_fields"]["score"]
    )
    section_scores["section1"]["score"] = section1_score
    section_scores["section1"]["percentage"] = round((section1_score / section_scores["section1"]["max_points"]) * 100, 2)
    
    # Calculate Section 2 score
    section2_score = (
        evaluation_results["section2"]["tax_calculation_client_d_errors"]["score"] +
        evaluation_results["section2"]["income_reconciliation_client_e"]["score"] +
        evaluation_results["section2"]["estimated_tax_client_f"]["score"]
    )
    section_scores["section2"]["score"] = section2_score
    section_scores["section2"]["percentage"] = round((section2_score / section_scores["section2"]["max_points"]) * 100, 2)
    
    # Calculate Section 3 score
    section3_score = (
        evaluation_results["section3"]["client_g_discrepancies"]["score"] +
        evaluation_results["section3"]["client_h_dependent_errors"]["score"] +
        evaluation_results["section3"]["client_i_contact_errors"]["score"]
    )
    section_scores["section3"]["score"] = section3_score
    section_scores["section3"]["percentage"] = round((section3_score / section_scores["section3"]["max_points"]) * 100, 2)
    
    # Calculate overall score
    overall_score = section1_score + section2_score + section3_score
    section_scores["overall"]["score"] = overall_score
    section_scores["overall"]["percentage"] = round((overall_score / section_scores["overall"]["max_points"]) * 100, 2)
    
    # Determine if passed
    section1_passed = section_scores["section1"]["percentage"] >= section_scores["section1"]["pass_threshold"]
    section2_passed = section_scores["section2"]["percentage"] >= section_scores["section2"]["pass_threshold"]
    section3_passed = section_scores["section3"]["percentage"] >= section_scores["section3"]["pass_threshold"]
    overall_passed = section_scores["overall"]["percentage"] >= section_scores["overall"]["pass_threshold"]
    
    section_scores["overall"]["passed"] = section1_passed and section2_passed and section3_passed and overall_passed
    
    return section_scores

def main():
    """Main function to evaluate tax preparer exam submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    evaluation_results = {
        "section1": evaluate_section1(submission, answer_key),
        "section2": evaluate_section2(submission, answer_key),
        "section3": evaluate_section3(submission, answer_key)
    }
    
    # Calculate section scores and overall score
    section_scores = calculate_section_scores(evaluation_results)
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_results": evaluation_results,
        "section_scores": section_scores,
        "overall_score": section_scores["overall"]["percentage"]
    }
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {section_scores['overall']['passed']}")

if __name__ == "__main__":
    main()