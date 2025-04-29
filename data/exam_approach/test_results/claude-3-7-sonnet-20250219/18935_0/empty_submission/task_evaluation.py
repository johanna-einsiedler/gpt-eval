#!/usr/bin/env python3
import json
import sys
import os
from math import isclose

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_result": {},
        "scenarios": {}
    }
    
    total_points = 0
    earned_points = 0
    
    # Define tolerance levels for different types of values
    tolerances = {
        "monetary": 5.0,  # ±$5.00
        "ratio": 0.02,    # ±0.02
        "months": 1       # ±1 month
    }
    
    # Fields to evaluate for each scenario
    fields = [
        {"name": "total_monthly_income", "type": "monetary", "points": 1},
        {"name": "total_necessary_expenses", "type": "monetary", "points": 1},
        {"name": "available_monthly_income", "type": "monetary", "points": 1, "critical": True},
        {"name": "debt_to_income_ratio", "type": "ratio", "points": 1},
        {"name": "recommended_monthly_debt_payment", "type": "monetary", "points": 1},
        {"name": "debt_free_timeline_months", "type": "months", "points": 1}
    ]
    
    # Track critical skill success
    critical_skill_success = True
    
    # Evaluate each scenario
    for scenario_num in range(1, 4):
        scenario_key = f"scenario{scenario_num}"
        
        if scenario_key not in submission or scenario_key not in answer_key:
            results["scenarios"][scenario_key] = {"error": f"Missing {scenario_key} data"}
            continue
        
        candidate_scenario = submission[scenario_key]
        correct_scenario = answer_key[scenario_key]
        
        scenario_results = {
            "correct_count": 0,
            "total_count": len(fields),
            "fields": {}
        }
        
        # Evaluate each field in the scenario
        for field in fields:
            field_name = field["name"]
            field_type = field["type"]
            field_points = field["points"]
            is_critical = field.get("critical", False)
            
            if field_name not in candidate_scenario or field_name not in correct_scenario:
                scenario_results["fields"][field_name] = {
                    "status": "error",
                    "message": "Field missing from submission or answer key",
                    "points_earned": 0,
                    "points_possible": field_points
                }
                continue
            
            candidate_value = candidate_scenario[field_name]
            correct_value = correct_scenario[field_name]
            
            # Check if the values are within tolerance
            if field_type == "monetary" or field_type == "ratio":
                is_correct = isclose(
                    candidate_value, 
                    correct_value, 
                    abs_tol=tolerances[field_type]
                )
            elif field_type == "months":
                is_correct = abs(candidate_value - correct_value) <= tolerances[field_type]
            else:
                is_correct = candidate_value == correct_value
            
            # Update results
            if is_correct:
                scenario_results["correct_count"] += 1
                earned_points += field_points
                status = "correct"
            else:
                status = "incorrect"
                # Check if this is a critical skill failure
                if is_critical:
                    critical_skill_success = False
            
            total_points += field_points
            
            # Add detailed field results
            scenario_results["fields"][field_name] = {
                "status": status,
                "candidate_value": candidate_value,
                "correct_value": correct_value,
                "points_earned": field_points if is_correct else 0,
                "points_possible": field_points
            }
        
        # Add scenario pass/fail status
        scenario_results["passed"] = scenario_results["correct_count"] >= 4
        
        # Add scenario results to overall results
        results["scenarios"][scenario_key] = scenario_results
    
    # Calculate overall score as a percentage
    results["overall_score"] = round((earned_points / total_points) * 100, 2) if total_points > 0 else 0
    
    # Determine if the candidate passed based on criteria
    total_correct = sum(scenario["correct_count"] for scenario in results["scenarios"].values())
    total_fields = sum(scenario["total_count"] for scenario in results["scenarios"].values())
    
    # Check passing criteria
    passed_overall_minimum = total_correct >= 15
    passed_per_scenario = all(scenario.get("passed", False) for scenario in results["scenarios"].values())
    passed_critical_skill = critical_skill_success
    
    results["overall_result"] = {
        "passed": passed_overall_minimum and passed_per_scenario and passed_critical_skill,
        "total_correct": total_correct,
        "total_fields": total_fields,
        "passed_overall_minimum": passed_overall_minimum,
        "passed_per_scenario": passed_per_scenario,
        "passed_critical_skill": passed_critical_skill
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
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
    print(f"Passed: {results['overall_result']['passed']}")

if __name__ == "__main__":
    main()