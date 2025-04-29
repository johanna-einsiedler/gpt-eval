#!/usr/bin/env python3
import json
import sys
import os

def evaluate_submission(submission_file, answer_key_file):
    # Load the submission and answer key
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    
    # Initialize results structure
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "candidate_name": submission.get("candidate_name", "Unknown"),
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "passed": False,
        "scenario_results": [],
        "critical_requirements_met": {
            "identified_unpayable_debt": False,
            "accurate_calculations": False
        },
        "feedback": ""
    }
    
    # Get the answer key scenarios
    answer_scenarios = {scenario["client_id"]: scenario for scenario in answer_key["answer_key"]["client_scenarios"]}
    
    # Track correct calculations for repayable scenarios
    correct_repayable_calculations = 0
    total_repayable_scenarios = 0
    
    # Evaluate each scenario
    for submission_scenario in submission.get("client_scenarios", []):
        client_id = submission_scenario.get("client_id")
        if client_id not in answer_scenarios:
            continue
        
        answer_scenario = answer_scenarios[client_id]
        scenario_result = {
            "client_id": client_id,
            "points_earned": 0,
            "max_points": 20,
            "details": []
        }
        
        # Check if repayable status is correct
        is_repayable_correct = submission_scenario.get("is_repayable") == answer_scenario.get("is_repayable")
        scenario_result["details"].append({
            "criterion": "is_repayable",
            "submitted_value": submission_scenario.get("is_repayable"),
            "expected_value": answer_scenario.get("is_repayable"),
            "correct": is_repayable_correct,
            "points": 0,  # No direct points but required to pass
            "notes": "Critical requirement" if client_id == "CL005" else ""
        })
        
        # Track if scenario 5 (unpayable debt) is correctly identified
        if client_id == "CL005" and is_repayable_correct:
            results["critical_requirements_met"]["identified_unpayable_debt"] = True
        
        # For repayable debts, check calculations
        if answer_scenario.get("is_repayable"):
            total_repayable_scenarios += 1
            scenario_correct = True
            
            # Check months to repay (±1 month tolerance)
            submitted_months = submission_scenario.get("months_to_repay")
            expected_months = answer_scenario.get("months_to_repay")
            months_correct = (
                submitted_months is not None and 
                expected_months is not None and
                abs(submitted_months - expected_months) <= 1
            )
            points_months = 10 if months_correct else 0
            scenario_result["points_earned"] += points_months
            scenario_result["details"].append({
                "criterion": "months_to_repay",
                "submitted_value": submitted_months,
                "expected_value": expected_months,
                "correct": months_correct,
                "points": points_months,
                "notes": "±1 month tolerance"
            })
            scenario_correct = scenario_correct and months_correct
            
            # Check total amount paid (±$100 tolerance)
            submitted_total = submission_scenario.get("total_amount_paid")
            expected_total = answer_scenario.get("total_amount_paid")
            total_correct = (
                submitted_total is not None and 
                expected_total is not None and
                abs(submitted_total - expected_total) <= 100
            )
            points_total = 5 if total_correct else 0
            scenario_result["points_earned"] += points_total
            scenario_result["details"].append({
                "criterion": "total_amount_paid",
                "submitted_value": submitted_total,
                "expected_value": expected_total,
                "correct": total_correct,
                "points": points_total,
                "notes": "±$100 tolerance"
            })
            scenario_correct = scenario_correct and total_correct
            
            # Check total interest paid (±$100 tolerance)
            submitted_interest = submission_scenario.get("total_interest_paid")
            expected_interest = answer_scenario.get("total_interest_paid")
            interest_correct = (
                submitted_interest is not None and 
                expected_interest is not None and
                abs(submitted_interest - expected_interest) <= 100
            )
            points_interest = 5 if interest_correct else 0
            scenario_result["points_earned"] += points_interest
            scenario_result["details"].append({
                "criterion": "total_interest_paid",
                "submitted_value": submitted_interest,
                "expected_value": expected_interest,
                "correct": interest_correct,
                "points": points_interest,
                "notes": "±$100 tolerance"
            })
            scenario_correct = scenario_correct and interest_correct
            
            if scenario_correct:
                correct_repayable_calculations += 1
        
        # For non-repayable debts, check if null values are provided
        else:
            # Check if months to repay is null or -1
            submitted_months = submission_scenario.get("months_to_repay")
            months_correct = submitted_months is None or submitted_months == -1
            points_months = 10 if months_correct else 0
            scenario_result["points_earned"] += points_months
            scenario_result["details"].append({
                "criterion": "months_to_repay",
                "submitted_value": submitted_months,
                "expected_value": None,
                "correct": months_correct,
                "points": points_months,
                "notes": "Should be null or -1 for unpayable debt"
            })
            
            # Check if total amount paid is null or -1
            submitted_total = submission_scenario.get("total_amount_paid")
            total_correct = submitted_total is None or submitted_total == -1
            points_total = 5 if total_correct else 0
            scenario_result["points_earned"] += points_total
            scenario_result["details"].append({
                "criterion": "total_amount_paid",
                "submitted_value": submitted_total,
                "expected_value": None,
                "correct": total_correct,
                "points": points_total,
                "notes": "Should be null or -1 for unpayable debt"
            })
            
            # Check if total interest paid is null or -1
            submitted_interest = submission_scenario.get("total_interest_paid")
            interest_correct = submitted_interest is None or submitted_interest == -1
            points_interest = 5 if interest_correct else 0
            scenario_result["points_earned"] += points_interest
            scenario_result["details"].append({
                "criterion": "total_interest_paid",
                "submitted_value": submitted_interest,
                "expected_value": None,
                "correct": interest_correct,
                "points": points_interest,
                "notes": "Should be null or -1 for unpayable debt"
            })
        
        # Add calculation method evaluation
        calculation_method = submission_scenario.get("calculation_method", "")
        scenario_result["details"].append({
            "criterion": "calculation_method",
            "submitted_value": calculation_method,
            "expected_value": "Valid calculation method",
            "correct": True if calculation_method else False,
            "points": 0,  # No direct points
            "notes": "Method documentation required"
        })
        
        # Add scenario result to overall results
        results["scenario_results"].append(scenario_result)
        results["total_points"] += scenario_result["points_earned"]
    
    # Check if accurate calculations requirement is met (at least 3 of 4 repayable scenarios correct)
    results["critical_requirements_met"]["accurate_calculations"] = correct_repayable_calculations >= 3
    
    # Calculate overall score as percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Determine if candidate passed
    passed = (
        results["critical_requirements_met"]["identified_unpayable_debt"] and
        results["critical_requirements_met"]["accurate_calculations"] and
        results["overall_score"] >= 80
    )
    results["passed"] = passed
    
    # Generate feedback
    feedback = []
    if not results["critical_requirements_met"]["identified_unpayable_debt"]:
        feedback.append("Failed to identify the unpayable debt (Scenario 5).")
    
    if not results["critical_requirements_met"]["accurate_calculations"]:
        feedback.append(f"Insufficient accurate calculations. Got {correct_repayable_calculations} correct out of {total_repayable_scenarios} repayable scenarios, needed at least 3.")
    
    if results["overall_score"] < 80:
        feedback.append(f"Overall score ({results['overall_score']:.1f}%) below passing threshold of 80%.")
    
    if passed:
        feedback.append(f"Passed with a score of {results['overall_score']:.1f}%.")
    
    results["feedback"] = " ".join(feedback)
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.1f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    print(f"Feedback: {results['feedback']}")

if __name__ == "__main__":
    main()