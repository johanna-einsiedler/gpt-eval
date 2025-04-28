#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Tuple

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_broader_program_matching(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the broader program matching section (45 points)."""
    max_points = 45
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    submission_matches = {item["specific_program_id"]: item for item in submission["matches"]}
    answer_key_matches = {item["specific_program_id"]: item for item in answer_key["matches"]}
    
    for program_id, answer in answer_key_matches.items():
        if program_id not in submission_matches:
            details.append({
                "specific_program_id": program_id,
                "points": 0,
                "max_points": 3,
                "reason": "Program missing from submission"
            })
            continue
            
        submission_item = submission_matches[program_id]
        is_correct = (
            submission_item.get("broader_program_id") == answer.get("broader_program_id") and
            submission_item.get("broader_program_name") == answer.get("broader_program_name")
        )
        
        points = 3 if is_correct else 0
        points_earned += points
        
        details.append({
            "specific_program_id": program_id,
            "points": points,
            "max_points": 3,
            "reason": "Correct match" if is_correct else "Incorrect match"
        })
    
    return points_earned, details

def evaluate_emergency_fund_identification(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the emergency fund identification section (30 points)."""
    max_points = 30
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    submission_matches = {item["specific_program_id"]: item for item in submission["matches"]}
    answer_key_matches = {item["specific_program_id"]: item for item in answer_key["matches"]}
    
    # Group programs by whether they have emergency funding
    programs_with_emergency = []
    programs_without_emergency = []
    
    for program_id, answer in answer_key_matches.items():
        if answer.get("emergency_fund_id"):
            programs_with_emergency.append(program_id)
        else:
            programs_without_emergency.append(program_id)
    
    # Check programs with emergency funding (2 points each for ID, 2 points for amount)
    for program_id in programs_with_emergency:
        if program_id not in submission_matches:
            details.append({
                "specific_program_id": program_id,
                "points": 0,
                "max_points": 4,
                "reason": "Program missing from submission"
            })
            continue
            
        submission_item = submission_matches[program_id]
        answer = answer_key_matches[program_id]
        
        # Check emergency fund ID (2 points)
        id_correct = submission_item.get("emergency_fund_id") == answer.get("emergency_fund_id")
        id_points = 2 if id_correct else 0
        
        # Check emergency fund amount (2 points)
        amount_correct = submission_item.get("emergency_fund_portion") == answer.get("emergency_fund_portion")
        amount_points = 2 if amount_correct else 0
        
        total_points = id_points + amount_points
        points_earned += total_points
        
        details.append({
            "specific_program_id": program_id,
            "points": total_points,
            "max_points": 4,
            "reason": f"Emergency fund ID: {'correct' if id_correct else 'incorrect'}, Amount: {'correct' if amount_correct else 'incorrect'}"
        })
    
    # Check programs without emergency funding (1 point each)
    for program_id in programs_without_emergency:
        if program_id not in submission_matches:
            details.append({
                "specific_program_id": program_id,
                "points": 0,
                "max_points": 1,
                "reason": "Program missing from submission"
            })
            continue
            
        submission_item = submission_matches[program_id]
        
        # Check if correctly identified as having no emergency funding
        is_correct = (
            submission_item.get("emergency_fund_id") is None and
            submission_item.get("emergency_fund_portion") == 0
        )
        
        points = 1 if is_correct else 0
        points_earned += points
        
        details.append({
            "specific_program_id": program_id,
            "points": points,
            "max_points": 1,
            "reason": "Correctly identified as having no emergency funding" if is_correct else "Incorrectly identified emergency funding status"
        })
    
    return points_earned, details

def evaluate_appropriation_code(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the appropriation code documentation section (15 points)."""
    max_points = 15
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    submission_matches = {item["specific_program_id"]: item for item in submission["matches"]}
    answer_key_matches = {item["specific_program_id"]: item for item in answer_key["matches"]}
    
    for program_id, answer in answer_key_matches.items():
        if program_id not in submission_matches:
            details.append({
                "specific_program_id": program_id,
                "points": 0,
                "max_points": 1,
                "reason": "Program missing from submission"
            })
            continue
            
        submission_item = submission_matches[program_id]
        is_correct = submission_item.get("appropriation_code") == answer.get("appropriation_code")
        
        points = 1 if is_correct else 0
        points_earned += points
        
        details.append({
            "specific_program_id": program_id,
            "points": points,
            "max_points": 1,
            "reason": "Correct appropriation code" if is_correct else "Incorrect appropriation code"
        })
    
    return points_earned, details

def evaluate_funding_amount(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the funding amount documentation section (10 points)."""
    max_points = 10
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    submission_matches = {item["specific_program_id"]: item for item in submission["matches"]}
    answer_key_matches = {item["specific_program_id"]: item for item in answer_key["matches"]}
    
    # Allocate points proportionally across all programs
    points_per_program = max_points / len(answer_key_matches)
    
    for program_id, answer in answer_key_matches.items():
        if program_id not in submission_matches:
            details.append({
                "specific_program_id": program_id,
                "points": 0,
                "max_points": points_per_program,
                "reason": "Program missing from submission"
            })
            continue
            
        submission_item = submission_matches[program_id]
        is_correct = submission_item.get("funding_amount") == answer.get("funding_amount")
        
        points = points_per_program if is_correct else 0
        points_earned += points
        
        details.append({
            "specific_program_id": program_id,
            "points": points,
            "max_points": points_per_program,
            "reason": "Correct funding amount" if is_correct else "Incorrect funding amount"
        })
    
    return round(points_earned), details

def evaluate_json_format(submission: Dict) -> Tuple[int, Dict]:
    """Evaluate the JSON format compliance section (10 points)."""
    max_points = 10
    points_earned = 0
    details = {}
    
    # Check proper structure and syntax (3 points)
    structure_points = 3
    if "candidate_id" in submission and "matches" in submission and isinstance(submission["matches"], list):
        details["structure"] = {
            "points": structure_points,
            "max_points": structure_points,
            "reason": "Proper JSON structure"
        }
        points_earned += structure_points
    else:
        details["structure"] = {
            "points": 0,
            "max_points": structure_points,
            "reason": "Improper JSON structure"
        }
    
    # Check all required fields present (3 points)
    required_fields = [
        "specific_program_id", "specific_program_name", "broader_program_id", 
        "broader_program_name", "appropriation_code", "funding_amount", 
        "emergency_fund_portion", "emergency_fund_id"
    ]
    
    fields_present = True
    missing_fields = []
    
    for item in submission.get("matches", []):
        for field in required_fields:
            if field not in item:
                fields_present = False
                missing_fields.append(field)
    
    fields_points = 3
    if fields_present:
        details["fields"] = {
            "points": fields_points,
            "max_points": fields_points,
            "reason": "All required fields present"
        }
        points_earned += fields_points
    else:
        details["fields"] = {
            "points": 0,
            "max_points": fields_points,
            "reason": f"Missing required fields: {', '.join(set(missing_fields))}"
        }
    
    # Check correct data types (2 points)
    data_types_correct = True
    incorrect_types = []
    
    for item in submission.get("matches", []):
        # Check string fields
        string_fields = ["specific_program_id", "specific_program_name", "appropriation_code"]
        for field in string_fields:
            if field in item and not (item[field] is None or isinstance(item[field], str)):
                data_types_correct = False
                incorrect_types.append(f"{field} should be string")
        
        # Check nullable string fields
        nullable_string_fields = ["broader_program_id", "broader_program_name", "emergency_fund_id"]
        for field in nullable_string_fields:
            if field in item and not (item[field] is None or isinstance(item[field], str)):
                data_types_correct = False
                incorrect_types.append(f"{field} should be string or null")
        
        # Check integer fields
        integer_fields = ["funding_amount", "emergency_fund_portion"]
        for field in integer_fields:
            if field in item and not isinstance(item[field], int):
                data_types_correct = False
                incorrect_types.append(f"{field} should be integer")
    
    data_types_points = 2
    if data_types_correct:
        details["data_types"] = {
            "points": data_types_points,
            "max_points": data_types_points,
            "reason": "Correct data types used"
        }
        points_earned += data_types_points
    else:
        details["data_types"] = {
            "points": 0,
            "max_points": data_types_points,
            "reason": f"Incorrect data types: {', '.join(set(incorrect_types))}"
        }
    
    # Check proper handling of null values (2 points)
    null_handling_correct = True
    
    for item in submission.get("matches", []):
        # Check if emergency_fund_id is null when emergency_fund_portion is 0
        if "emergency_fund_portion" in item and "emergency_fund_id" in item:
            if item["emergency_fund_portion"] == 0 and item["emergency_fund_id"] is not None:
                null_handling_correct = False
            elif item["emergency_fund_portion"] > 0 and item["emergency_fund_id"] is None:
                null_handling_correct = False
    
    null_points = 2
    if null_handling_correct:
        details["null_handling"] = {
            "points": null_points,
            "max_points": null_points,
            "reason": "Proper handling of null values"
        }
        points_earned += null_points
    else:
        details["null_handling"] = {
            "points": 0,
            "max_points": null_points,
            "reason": "Improper handling of null values"
        }
    
    return points_earned, details

def check_critical_requirements(evaluation_results: Dict) -> Dict:
    """Check if the candidate meets the critical requirements to pass."""
    # Requirement 1: Correctly identify at least 12 out of 15 broader program matches
    broader_program_correct = sum(1 for item in evaluation_results["broader_program_matching"]["details"] 
                                if item["points"] == item["max_points"])
    
    # Requirement 2: Correctly identify at least 7 out of 9 emergency fund allocations
    emergency_fund_details = evaluation_results["emergency_fund_identification"]["details"]
    emergency_fund_programs = [item for item in emergency_fund_details if item["max_points"] > 1]
    emergency_fund_correct = sum(1 for item in emergency_fund_programs 
                               if item["points"] == item["max_points"])
    
    # Requirement 3: Submit a valid JSON file (already checked by loading the file)
    json_valid = True
    
    return {
        "broader_program_requirement": {
            "required": 12,
            "achieved": broader_program_correct,
            "passed": broader_program_correct >= 12
        },
        "emergency_fund_requirement": {
            "required": 7,
            "achieved": emergency_fund_correct,
            "passed": emergency_fund_correct >= 7
        },
        "valid_json_requirement": {
            "required": True,
            "achieved": json_valid,
            "passed": json_valid
        },
        "all_requirements_passed": (broader_program_correct >= 12 and 
                                   emergency_fund_correct >= 7 and 
                                   json_valid)
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    # Evaluate each section
    broader_program_points, broader_program_details = evaluate_broader_program_matching(submission, answer_key)
    emergency_fund_points, emergency_fund_details = evaluate_emergency_fund_identification(submission, answer_key)
    appropriation_code_points, appropriation_code_details = evaluate_appropriation_code(submission, answer_key)
    funding_amount_points, funding_amount_details = evaluate_funding_amount(submission, answer_key)
    json_format_points, json_format_details = evaluate_json_format(submission)
    
    # Calculate total score
    total_points = broader_program_points + emergency_fund_points + appropriation_code_points + funding_amount_points + json_format_points
    max_points = 100
    overall_score = (total_points / max_points) * 100
    
    # Compile results
    evaluation_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "total_points": total_points,
        "max_points": max_points,
        "broader_program_matching": {
            "points": broader_program_points,
            "max_points": 45,
            "details": broader_program_details
        },
        "emergency_fund_identification": {
            "points": emergency_fund_points,
            "max_points": 30,
            "details": emergency_fund_details
        },
        "appropriation_code_documentation": {
            "points": appropriation_code_points,
            "max_points": 15,
            "details": appropriation_code_details
        },
        "funding_amount_documentation": {
            "points": funding_amount_points,
            "max_points": 10,
            "details": funding_amount_details
        },
        "json_format_compliance": {
            "points": json_format_points,
            "max_points": 10,
            "details": json_format_details
        }
    }
    
    # Check critical requirements
    evaluation_results["critical_requirements"] = check_critical_requirements(evaluation_results)
    
    # Determine pass/fail status
    evaluation_results["passed"] = (
        evaluation_results["overall_score"] >= 75 and 
        evaluation_results["critical_requirements"]["all_requirements_passed"]
    )
    
    if evaluation_results["overall_score"] >= 90:
        evaluation_results["grade"] = "Excellent"
    elif evaluation_results["overall_score"] >= 75:
        evaluation_results["grade"] = "Pass"
    else:
        evaluation_results["grade"] = "Fail"
    
    return evaluation_results

def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(evaluation_results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {evaluation_results['overall_score']}%")
    print(f"Grade: {evaluation_results['grade']}")

if __name__ == "__main__":
    main()