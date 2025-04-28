#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "total_points": 0,
        "max_points": 12,
        "scenario_scores": {},
        "critical_elements_passed": True,
        "passed": False
    }
    
    # Define tolerance ranges for numeric answers
    tolerances = {
        "scenario1": {
            "emergencyFund": (10410, 20820),
            "monthlyDiscretionaryIncome": (400, 500)
        },
        "scenario2": {
            "lifeInsuranceCoverage": (750000, 950000),
            "disabilityMonthlyBenefit": (4400, 4800),
            "bundlingSavings": (400, 500)
        },
        "scenario3": {
            "monthlySavingsRequired": (1800, 2300),
            "projectedValue10Years": (1300000, 1450000)
        }
    }
    
    # Define critical elements
    critical_elements = {
        "scenario1": {"debtPriorityId": ["D3"]},
        "scenario2": {"healthPlanId": ["HP3", "HP4"]},
        "scenario3": {"assetAllocationId": ["AA2", "AA3", "AA4"]}
    }
    
    # Evaluate each scenario
    for scenario in ["scenario1", "scenario2", "scenario3"]:
        results["scenario_scores"][scenario] = {
            "points": 0,
            "max_points": 4,
            "details": {}
        }
        
        # Check each answer in the scenario
        for key, expected_value in answer_key[scenario].items():
            submitted_value = submission.get(scenario, {}).get(key)
            is_correct = False
            
            # Check if the answer is within tolerance range for numeric values
            if key in tolerances.get(scenario, {}):
                min_val, max_val = tolerances[scenario][key]
                is_correct = isinstance(submitted_value, (int, float)) and min_val <= submitted_value <= max_val
            # Check if the answer matches exactly for ID values
            elif key in critical_elements.get(scenario, {}).keys():
                is_correct = submitted_value in critical_elements[scenario][key]
                # Check critical elements
                if not is_correct:
                    results["critical_elements_passed"] = False
            else:
                is_correct = submitted_value == expected_value
            
            # Record the result
            results["scenario_scores"][scenario]["details"][key] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": is_correct
            }
            
            if is_correct:
                results["scenario_scores"][scenario]["points"] += 1
                results["total_points"] += 1
    
    # Calculate overall score percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Check if passing criteria are met
    scenario_minimums_met = all(score["points"] >= 2 for score in results["scenario_scores"].values())
    results["passed"] = (results["total_points"] >= 9 and 
                         scenario_minimums_met and 
                         results["critical_elements_passed"])
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()