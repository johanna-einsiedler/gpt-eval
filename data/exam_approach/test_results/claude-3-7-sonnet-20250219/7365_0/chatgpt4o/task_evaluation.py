#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "scenarios": {},
        "critical_errors": {
            "complexity_factor_errors": 0,
            "additional_form_fee_errors": 0,
            "total_fee_large_errors": 0
        },
        "passed": False
    }
    
    # Points per field in each scenario
    field_points = {
        "base_fee": 3,
        "time_charge": 5,
        "complexity_adjustment": 4,
        "additional_forms_fee": 4,
        "total_fee": 4
    }
    
    # Evaluate each scenario
    for scenario_num in range(1, 6):
        scenario_key = f"scenario_{scenario_num}"
        
        if scenario_key not in submission or scenario_key not in answer_key:
            continue
            
        sub_scenario = submission[scenario_key]
        ans_scenario = answer_key[scenario_key]
        
        scenario_results = {
            "points_earned": 0,
            "max_points": 20,
            "field_scores": {},
            "errors": []
        }
        
        # Check each field
        for field, points in field_points.items():
            if field not in sub_scenario or field not in ans_scenario:
                scenario_results["field_scores"][field] = {
                    "points": 0,
                    "max_points": points,
                    "correct": False,
                    "submitted_value": None if field not in sub_scenario else sub_scenario[field],
                    "expected_value": None if field not in ans_scenario else ans_scenario[field]
                }
                scenario_results["errors"].append(f"Missing {field} field")
                continue
                
            sub_value = sub_scenario[field]
            ans_value = ans_scenario[field]
            
            # Check if values are close enough (for rounding differences)
            is_correct = False
            if field in ["base_fee", "time_charge", "complexity_adjustment", "additional_forms_fee", "total_fee"]:
                # Allow small rounding differences (±$0.01)
                is_correct = abs(float(sub_value) - float(ans_value)) <= 0.01
            
            points_earned = points if is_correct else 0
            scenario_results["points_earned"] += points_earned
            
            scenario_results["field_scores"][field] = {
                "points": points_earned,
                "max_points": points,
                "correct": is_correct,
                "submitted_value": sub_value,
                "expected_value": ans_value
            }
            
            # Track critical errors
            if not is_correct:
                if field == "complexity_adjustment":
                    results["critical_errors"]["complexity_factor_errors"] += 1
                elif field == "additional_forms_fee":
                    results["critical_errors"]["additional_form_fee_errors"] += 1
                elif field == "total_fee" and abs(float(sub_value) - float(ans_value)) / float(ans_value) > 0.15:
                    results["critical_errors"]["total_fee_large_errors"] += 1
        
        results["scenarios"][scenario_key] = scenario_results
        results["total_points"] += scenario_results["points_earned"]
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Determine if the candidate passed
    passed_score = results["overall_score"] >= 80
    no_critical_errors = (
        results["critical_errors"]["complexity_factor_errors"] <= 1 and
        results["critical_errors"]["additional_form_fee_errors"] <= 2 and
        results["critical_errors"]["total_fee_large_errors"] <= 2
    )
    
    results["passed"] = passed_score and no_critical_errors
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to test_results.json
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()