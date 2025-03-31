import json
import os
from typing import Dict, List, Any, Union

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return {}

def save_json_file(data: Dict, filename: str) -> None:
    """Save data to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, indent=2, sort_keys=False, file=file)

def calculate_scenario_1_score(submission: Dict, answer_key: Dict) -> Dict:
    """Calculate the score for Scenario 1."""
    results = {
        "points_possible": 30,
        "points_earned": 0,
        "breakdown": {
            "irregularities_identified": {"points_possible": 10, "points_earned": 0, "details": []},
            "calculation_accuracy": {"points_possible": 10, "points_earned": 0, "details": []},
            "recommended_actions": {"points_possible": 5, "points_earned": 0, "details": ""},
            "priority_classification": {"points_possible": 5, "points_earned": 0, "details": ""}
        }
    }
    
    # Check if the scenario exists in both submission and answer key
    if "scenario_1" not in submission or "scenario_1" not in answer_key:
        return results
    
    sub_scenario = submission["scenario_1"]
    key_scenario = answer_key["scenario_1"]
    
    # 1. Evaluate irregularities identified (10 points - 5 points each)
    sub_irregularities = sub_scenario.get("irregularities_identified", [])
    key_irregularities = key_scenario.get("irregularities_identified", [])
    
    # Create a mapping of key irregularities by type and amount for easier matching
    key_irreg_map = {(i["type"], i["amount"]): i for i in key_irregularities}
    
    for sub_irreg in sub_irregularities:
        sub_type = sub_irreg.get("type", "")
        sub_amount = sub_irreg.get("amount", 0)
        
        # Check if this irregularity matches any in the answer key
        for key_type, key_amount in key_irreg_map:
            # Allow for small differences in amount (5% margin)
            if sub_type == key_type and abs(sub_amount - key_amount) <= key_amount * 0.05:
                results["breakdown"]["irregularities_identified"]["points_earned"] += 5
                results["breakdown"]["irregularities_identified"]["details"].append(
                    f"Correctly identified {sub_type} irregularity of ${sub_amount:.2f}"
                )
                # Remove this key irregularity so it's not matched again
                del key_irreg_map[(key_type, key_amount)]
                break
    
    # Cap at maximum points
    results["breakdown"]["irregularities_identified"]["points_earned"] = min(
        results["breakdown"]["irregularities_identified"]["points_earned"], 
        results["breakdown"]["irregularities_identified"]["points_possible"]
    )
    
    # 2. Evaluate calculation accuracy (10 points - 5 points each)
    sub_total = sub_scenario.get("total_discrepancy_amount", 0)
    key_total = key_scenario.get("total_discrepancy_amount", 0)
    
    # Check if total is within 5% of expected
    if abs(sub_total - key_total) <= key_total * 0.05:
        results["breakdown"]["calculation_accuracy"]["points_earned"] += 10
        results["breakdown"]["calculation_accuracy"]["details"].append(
            f"Correctly calculated total discrepancy amount of ${sub_total:.2f}"
        )
    else:
        # Partial credit if they got the individual amounts right but total wrong
        if results["breakdown"]["irregularities_identified"]["points_earned"] > 0:
            results["breakdown"]["calculation_accuracy"]["points_earned"] += 5
            results["breakdown"]["calculation_accuracy"]["details"].append(
                f"Identified some correct amounts but total (${sub_total:.2f}) differs from expected (${key_total:.2f})"
            )
        else:
            results["breakdown"]["calculation_accuracy"]["details"].append(
                f"Incorrect total discrepancy amount: ${sub_total:.2f}, expected: ${key_total:.2f}"
            )
    
    # 3. Evaluate recommended actions (5 points)
    sub_actions = sub_scenario.get("recommended_actions", [])
    key_actions = key_scenario.get("recommended_actions", [])
    
    # Check if at least 2 appropriate actions are recommended
    valid_action_codes = set()
    for action in sub_actions:
        if any(code in action for code in ["Code A1", "Code A2", "Code A3", "Code A4", "Code A5", 
                                          "Code B1", "Code B2", "Code B3", 
                                          "Code C1", "Code C2", "Code C3", "Code C4"]):
            valid_action_codes.add(action.split(":")[0].strip())
    
    if len(valid_action_codes) >= 2:
        results["breakdown"]["recommended_actions"]["points_earned"] = 5
        results["breakdown"]["recommended_actions"]["details"] = f"Recommended {len(valid_action_codes)} valid actions"
    else:
        results["breakdown"]["recommended_actions"]["details"] = f"Insufficient valid actions: {len(valid_action_codes)}/2 required"
    
    # 4. Evaluate priority classification (5 points)
    sub_priority = sub_scenario.get("reporting_priority", "")
    key_priority = key_scenario.get("reporting_priority", "")
    
    if sub_priority.lower() == key_priority.lower():
        results["breakdown"]["priority_classification"]["points_earned"] = 5
        results["breakdown"]["priority_classification"]["details"] = f"Correct priority classification: {sub_priority}"
    else:
        results["breakdown"]["priority_classification"]["details"] = f"Incorrect priority: {sub_priority}, expected: {key_priority}"
    
    # Calculate total points earned
    results["points_earned"] = sum(section["points_earned"] for section in results["breakdown"].values())
    
    return results

def calculate_scenario_2_score(submission: Dict, answer_key: Dict) -> Dict:
    """Calculate the score for Scenario 2."""
    results = {
        "points_possible": 35,
        "points_earned": 0,
        "breakdown": {
            "irregularities_identified": {"points_possible": 15, "points_earned": 0, "details": []},
            "calculation_accuracy": {"points_possible": 10, "points_earned": 0, "details": []},
            "recommended_actions": {"points_possible": 5, "points_earned": 0, "details": ""},
            "priority_classification": {"points_possible": 5, "points_earned": 0, "details": ""}
        }
    }
    
    # Check if the scenario exists in both submission and answer key
    if "scenario_2" not in submission or "scenario_2" not in answer_key:
        return results
    
    sub_scenario = submission["scenario_2"]
    key_scenario = answer_key["scenario_2"]
    
    # 1. Evaluate irregularities identified (15 points - 5 points each)
    sub_irregularities = sub_scenario.get("irregularities_identified", [])
    key_irregularities = key_scenario.get("irregularities_identified", [])
    
    # Create a mapping of key irregularities by type and amount for easier matching
    key_irreg_map = {(i["type"], i["amount"]): i for i in key_irregularities}
    
    for sub_irreg in sub_irregularities:
        sub_type = sub_irreg.get("type", "")
        sub_amount = sub_irreg.get("amount", 0)
        
        # Check if this irregularity matches any in the answer key
        for key_type, key_amount in key_irreg_map:
            # Allow for small differences in amount (5% margin)
            if sub_type == key_type and abs(sub_amount - key_amount) <= key_amount * 0.05:
                results["breakdown"]["irregularities_identified"]["points_earned"] += 5
                results["breakdown"]["irregularities_identified"]["details"].append(
                    f"Correctly identified {sub_type} irregularity of ${sub_amount:.2f}"
                )
                # Remove this key irregularity so it's not matched again
                del key_irreg_map[(key_type, key_amount)]
                break
    
    # Cap at maximum points
    results["breakdown"]["irregularities_identified"]["points_earned"] = min(
        results["breakdown"]["irregularities_identified"]["points_earned"], 
        results["breakdown"]["irregularities_identified"]["points_possible"]
    )
    
    # 2. Evaluate calculation accuracy (10 points)
    sub_total = sub_scenario.get("total_discrepancy_amount", 0)
    key_total = key_scenario.get("total_discrepancy_amount", 0)
    
    # Check if total is within 5% of expected
    if abs(sub_total - key_total) <= key_total * 0.05:
        results["breakdown"]["calculation_accuracy"]["points_earned"] = 10
        results["breakdown"]["calculation_accuracy"]["details"].append(
            f"Correctly calculated total discrepancy amount of ${sub_total:.2f}"
        )
    else:
        # Partial credit if they got the individual amounts right but total wrong
        if results["breakdown"]["irregularities_identified"]["points_earned"] > 0:
            results["breakdown"]["calculation_accuracy"]["points_earned"] = 5
            results["breakdown"]["calculation_accuracy"]["details"].append(
                f"Identified some correct amounts but total (${sub_total:.2f}) differs from expected (${key_total:.2f})"
            )
        else:
            results["breakdown"]["calculation_accuracy"]["details"].append(
                f"Incorrect total discrepancy amount: ${sub_total:.2f}, expected: ${key_total:.2f}"
            )
    
    # 3. Evaluate recommended actions (5 points)
    sub_actions = sub_scenario.get("recommended_actions", [])
    key_actions = key_scenario.get("recommended_actions", [])
    
    # Check if at least 2 appropriate actions are recommended
    valid_action_codes = set()
    for action in sub_actions:
        if any(code in action for code in ["Code A1", "Code A2", "Code A3", "Code A4", "Code A5", 
                                          "Code B1", "Code B2", "Code B3", 
                                          "Code C1", "Code C2", "Code C3", "Code C4"]):
            valid_action_codes.add(action.split(":")[0].strip())
    
    if len(valid_action_codes) >= 2:
        results["breakdown"]["recommended_actions"]["points_earned"] = 5
        results["breakdown"]["recommended_actions"]["details"] = f"Recommended {len(valid_action_codes)} valid actions"
    else:
        results["breakdown"]["recommended_actions"]["details"] = f"Insufficient valid actions: {len(valid_action_codes)}/2 required"
    
    # 4. Evaluate priority classification (5 points)
    sub_priority = sub_scenario.get("reporting_priority", "")
    key_priority = key_scenario.get("reporting_priority", "")
    
    if sub_priority.lower() == key_priority.lower():
        results["breakdown"]["priority_classification"]["points_earned"] = 5
        results["breakdown"]["priority_classification"]["details"] = f"Correct priority classification: {sub_priority}"
    else:
        results["breakdown"]["priority_classification"]["details"] = f"Incorrect priority: {sub_priority}, expected: {key_priority}"
    
    # Calculate total points earned
    results["points_earned"] = sum(section["points_earned"] for section in results["breakdown"].values())
    
    return results

def calculate_scenario_3_score(submission: Dict, answer_key: Dict) -> Dict:
    """Calculate the score for Scenario 3."""
    results = {
        "points_possible": 25,
        "points_earned": 0,
        "breakdown": {
            "irregularities_identified": {"points_possible": 10, "points_earned": 0, "details": []},
            "calculation_accuracy": {"points_possible": 5, "points_earned": 0, "details": []},
            "recommended_actions": {"points_possible": 5, "points_earned": 0, "details": ""},
            "priority_classification": {"points_possible": 5, "points_earned": 0, "details": ""}
        }
    }
    
    # Check if the scenario exists in both submission and answer key
    if "scenario_3" not in submission or "scenario_3" not in answer_key:
        return results
    
    sub_scenario = submission["scenario_3"]
    key_scenario = answer_key["scenario_3"]
    
    # 1. Evaluate irregularities identified (10 points)
    sub_irregularities = sub_scenario.get("irregularities_identified", [])
    key_irregularities = key_scenario.get("irregularities_identified", [])
    
    # Create a mapping of key irregularities by type and amount for easier matching
    key_irreg_map = {(i["type"], i["amount"]): i for i in key_irregularities}
    
    for sub_irreg in sub_irregularities:
        sub_type = sub_irreg.get("type", "")
        sub_amount = sub_irreg.get("amount", 0)
        
        # Check if this irregularity matches any in the answer key
        for key_type, key_amount in key_irreg_map:
            # Allow for small differences in amount (5% margin)
            if sub_type == key_type and abs(sub_amount - key_amount) <= key_amount * 0.05:
                results["breakdown"]["irregularities_identified"]["points_earned"] = 10
                results["breakdown"]["irregularities_identified"]["details"].append(
                    f"Correctly identified {sub_type} irregularity of ${sub_amount:.2f}"
                )
                # Remove this key irregularity so it's not matched again
                del key_irreg_map[(key_type, key_amount)]
                break
    
    # 2. Evaluate calculation accuracy (5 points)
    sub_total = sub_scenario.get("total_discrepancy_amount", 0)
    key_total = key_scenario.get("total_discrepancy_amount", 0)
    
    # Check if total is within 5% of expected
    if abs(sub_total - key_total) <= key_total * 0.05:
        results["breakdown"]["calculation_accuracy"]["points_earned"] = 5
        results["breakdown"]["calculation_accuracy"]["details"].append(
            f"Correctly calculated total discrepancy amount of ${sub_total:.2f}"
        )
    else:
        results["breakdown"]["calculation_accuracy"]["details"].append(
            f"Incorrect total discrepancy amount: ${sub_total:.2f}, expected: ${key_total:.2f}"
        )
    
    # 3. Evaluate recommended actions (5 points)
    sub_actions = sub_scenario.get("recommended_actions", [])
    key_actions = key_scenario.get("recommended_actions", [])
    
    # Check if at least 2 appropriate actions are recommended
    valid_action_codes = set()
    for action in sub_actions:
        if any(code in action for code in ["Code A1", "Code A2", "Code A3", "Code A4", "Code A5", 
                                          "Code B1", "Code B2", "Code B3", 
                                          "Code C1", "Code C2", "Code C3", "Code C4"]):
            valid_action_codes.add(action.split(":")[0].strip())
    
    if len(valid_action_codes) >= 2:
        results["breakdown"]["recommended_actions"]["points_earned"] = 5
        results["breakdown"]["recommended_actions"]["details"] = f"Recommended {len(valid_action_codes)} valid actions"
    else:
        results["breakdown"]["recommended_actions"]["details"] = f"Insufficient valid actions: {len(valid_action_codes)}/2 required"
    
    # 4. Evaluate priority classification (5 points)
    sub_priority = sub_scenario.get("reporting_priority", "")
    key_priority = key_scenario.get("reporting_priority", "")
    
    if sub_priority.lower() == key_priority.lower():
        results["breakdown"]["priority_classification"]["points_earned"] = 5
        results["breakdown"]["priority_classification"]["details"] = f"Correct priority classification: {sub_priority}"
    else:
        results["breakdown"]["priority_classification"]["details"] = f"Incorrect priority: {sub_priority}, expected: {key_priority}"
    
    # Calculate total points earned
    results["points_earned"] = sum(section["points_earned"] for section in results["breakdown"].values())
    
    return results

def evaluate_json_format(submission: Dict) -> Dict:
    """Evaluate the JSON format compliance."""
    results = {
        "points_possible": 10,
        "points_earned": 0,
        "breakdown": {
            "structure": {"points_possible": 5, "points_earned": 0, "details": ""},
            "codes_and_formatting": {"points_possible": 5, "points_earned": 0, "details": ""}
        }
    }
    
    # 1. Check structure (5 points)
    structure_issues = []
    
    # Check for required top-level keys
    required_keys = ["candidate_id", "scenario_1", "scenario_2", "scenario_3"]
    missing_keys = [key for key in required_keys if key not in submission]
    
    if missing_keys:
        structure_issues.append(f"Missing required keys: {', '.join(missing_keys)}")
    
    # Check for required scenario structure
    for scenario in ["scenario_1", "scenario_2", "scenario_3"]:
        if scenario in submission:
            scenario_data = submission[scenario]
            scenario_required_keys = ["irregularities_identified", "total_discrepancy_amount", 
                                     "recommended_actions", "reporting_priority", "justification"]
            
            missing_scenario_keys = [key for key in scenario_required_keys if key not in scenario_data]
            if missing_scenario_keys:
                structure_issues.append(f"{scenario} missing keys: {', '.join(missing_scenario_keys)}")
            
            # Check irregularities structure if present
            if "irregularities_identified" in scenario_data:
                for i, irreg in enumerate(scenario_data["irregularities_identified"]):
                    irreg_required_keys = ["type", "description", "amount", "calculation_method"]
                    missing_irreg_keys = [key for key in irreg_required_keys if key not in irreg]
                    
                    if missing_irreg_keys:
                        structure_issues.append(f"{scenario} irregularity #{i+1} missing keys: {', '.join(missing_irreg_keys)}")
    
    # Assign points based on structure issues
    if not structure_issues:
        results["breakdown"]["structure"]["points_earned"] = 5
        results["breakdown"]["structure"]["details"] = "JSON structure is correct"
    elif len(structure_issues) <= 2:
        results["breakdown"]["structure"]["points_earned"] = 3
        results["breakdown"]["structure"]["details"] = f"Minor structure issues: {'; '.join(structure_issues)}"
    else:
        results["breakdown"]["structure"]["points_earned"] = 0
        results["breakdown"]["structure"]["details"] = f"Major structure issues: {'; '.join(structure_issues)}"
    
    # 2. Check codes and formatting (5 points)
    formatting_issues = []
    
    # Check for correct reporting codes
    valid_types = ["OVP", "UNP", "DUP", "NCS"]
    valid_priorities = ["high", "medium", "low"]
    
    for scenario in ["scenario_1", "scenario_2", "scenario_3"]:
        if scenario in submission:
            scenario_data = submission[scenario]
            
            # Check irregularity types
            if "irregularities_identified" in scenario_data:
                for i, irreg in enumerate(scenario_data["irregularities_identified"]):
                    if "type" in irreg and irreg["type"] not in valid_types:
                        formatting_issues.append(f"{scenario} uses invalid type code: {irreg['type']}")
                    
                    # Check amount formatting
                    if "amount" in irreg and not isinstance(irreg["amount"], (int, float)):
                        formatting_issues.append(f"{scenario} irregularity #{i+1} has non-numeric amount")
            
            # Check priority value
            if "reporting_priority" in scenario_data and scenario_data["reporting_priority"].lower() not in valid_priorities:
                formatting_issues.append(f"{scenario} has invalid priority: {scenario_data['reporting_priority']}")
            
            # Check action codes
            if "recommended_actions" in scenario_data:
                for action in scenario_data["recommended_actions"]:
                    if not any(code in action for code in ["Code A", "Code B", "Code C"]):
                        formatting_issues.append(f"{scenario} has action without proper code: {action}")
    
    # Assign points based on formatting issues
    if not formatting_issues:
        results["breakdown"]["codes_and_formatting"]["points_earned"] = 5
        results["breakdown"]["codes_and_formatting"]["details"] = "Codes and formatting are correct"
    elif len(formatting_issues) <= 2:
        results["breakdown"]["codes_and_formatting"]["points_earned"] = 3
        results["breakdown"]["codes_and_formatting"]["details"] = f"Minor formatting issues: {'; '.join(formatting_issues)}"
    else:
        results["breakdown"]["codes_and_formatting"]["points_earned"] = 0
        results["breakdown"]["codes_and_formatting"]["details"] = f"Major formatting issues: {'; '.join(formatting_issues)}"
    
    # Calculate total points earned
    results["points_earned"] = sum(section["points_earned"] for section in results["breakdown"].values())
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    # Calculate scores for each section
    scenario_1_results = calculate_scenario_1_score(submission, answer_key)
    scenario_2_results = calculate_scenario_2_score(submission, answer_key)
    scenario_3_results = calculate_scenario_3_score(submission, answer_key)
    json_format_results = evaluate_json_format(submission)
    
    # Calculate total score
    total_points_possible = (
        scenario_1_results["points_possible"] +
        scenario_2_results["points_possible"] +
        scenario_3_results["points_possible"] +
        json_format_results["points_possible"]
    )
    
    total_points_earned = (
        scenario_1_results["points_earned"] +
        scenario_2_results["points_earned"] +
        scenario_3_results["points_earned"] +
        json_format_results["points_earned"]
    )
    
    overall_score_percentage = (total_points_earned / total_points_possible) * 100 if total_points_possible > 0 else 0
    
    # Determine if the candidate passed
    passed = overall_score_percentage >= 75
    
    # Compile results
    results = {
        "overall_score": round(overall_score_percentage, 2),
        "passed": passed,
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "scenario_1": scenario_1_results,
        "scenario_2": scenario_2_results,
        "scenario_3": scenario_3_results,
        "json_format": json_format_results,
        "irregularities_identified_count": sum(
            len(submission.get(f"scenario_{i}", {}).get("irregularities_identified", [])) 
            for i in range(1, 4)
        ),
        "required_irregularities_count": sum(
            len(answer_key.get(f"scenario_{i}", {}).get("irregularities_identified", [])) 
            for i in range(1, 4)
        )
    }
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json_file(results, "test_results.json")
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()