#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_submission(submission, answer_key):
    """Evaluate the submission against the answer key."""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "scenarios": {},
        "overall_results": {
            "total_correct": 0,
            "total_items": 0,
            "overall_score": 0,
            "passed": False
        },
        "critical_calculations": {
            "correct_scenarios": 0,
            "passed": False
        },
        "scenario_specific": {
            "scenario1": {"correct": 0, "total": 5, "passed": False},
            "scenario2": {"correct": 0, "total": 5, "passed": False},
            "scenario3": {"correct": 0, "total": 7, "passed": False},
            "passed": False
        },
        "automatic_failure": False,
        "failure_reasons": []
    }
    
    # Check for automatic failure conditions
    if "scenario1" not in submission or "scenario2" not in submission or "scenario3" not in submission:
        results["automatic_failure"] = True
        results["failure_reasons"].append("Missing one or more scenarios in submission")
    
    # Evaluate each scenario
    total_correct = 0
    total_items = 0
    
    for scenario in ["scenario1", "scenario2", "scenario3"]:
        if scenario not in submission:
            continue
            
        scenario_results = {"items": {}, "correct": 0, "total": 0}
        
        # Get expected fields for this scenario
        expected_fields = list(answer_key[scenario].keys())
        scenario_results["total"] = len(expected_fields)
        total_items += len(expected_fields)
        
        # Check each field
        critical_fields = ["adjustedGrossIncome", "taxableIncome", "taxLiability", "refundOrAmountDue"]
        critical_correct = 0
        critical_total = len([f for f in critical_fields if f in expected_fields])
        
        for field in expected_fields:
            if field not in submission[scenario]:
                scenario_results["items"][field] = {
                    "expected": answer_key[scenario][field],
                    "submitted": "Missing",
                    "correct": False
                }
                continue
                
            expected = answer_key[scenario][field]
            submitted = submission[scenario][field]
            
            # Allow small rounding errors (within ±$5)
            is_correct = False
            if isinstance(expected, (int, float)) and isinstance(submitted, (int, float)):
                is_correct = abs(expected - submitted) <= 5
            else:
                is_correct = expected == submitted
                
            scenario_results["items"][field] = {
                "expected": expected,
                "submitted": submitted,
                "correct": is_correct
            }
            
            if is_correct:
                scenario_results["correct"] += 1
                total_correct += 1
                if field in critical_fields:
                    critical_correct += 1
        
        # Check if critical calculations are correct for this scenario
        scenario_critical_passed = critical_correct == critical_total
        
        # Check scenario-specific requirements
        if scenario == "scenario1":
            results["scenario_specific"]["scenario1"]["correct"] = scenario_results["correct"]
            results["scenario_specific"]["scenario1"]["passed"] = scenario_results["correct"] >= 4
        elif scenario == "scenario2":
            results["scenario_specific"]["scenario2"]["correct"] = scenario_results["correct"]
            results["scenario_specific"]["scenario2"]["passed"] = scenario_results["correct"] >= 4
        elif scenario == "scenario3":
            results["scenario_specific"]["scenario3"]["correct"] = scenario_results["correct"]
            results["scenario_specific"]["scenario3"]["passed"] = scenario_results["correct"] >= 6
            
            # Check for specific failure conditions in scenario 3
            if "childTaxCredit" not in submission[scenario] or "earnedIncomeTaxCredit" not in submission[scenario]:
                results["automatic_failure"] = True
                results["failure_reasons"].append("Missing tax credits in Scenario 3")
        
        # Add scenario results to overall results
        results["scenarios"][scenario] = scenario_results
        
        # Count critical scenarios passed
        if scenario_critical_passed:
            results["critical_calculations"]["correct_scenarios"] += 1
    
    # Calculate overall score
    if total_items > 0:
        results["overall_results"]["total_correct"] = total_correct
        results["overall_results"]["total_items"] = total_items
        results["overall_results"]["overall_score"] = round((total_correct / total_items) * 100, 2)
        results["overall_results"]["passed"] = total_correct >= 17  # 80% of 21 items
    
    # Check critical calculations requirement
    results["critical_calculations"]["passed"] = results["critical_calculations"]["correct_scenarios"] >= 2
    
    # Check scenario-specific requirements
    results["scenario_specific"]["passed"] = (
        results["scenario_specific"]["scenario1"]["passed"] and
        results["scenario_specific"]["scenario2"]["passed"] and
        results["scenario_specific"]["scenario3"]["passed"]
    )
    
    # Check for income sources in scenarios 2 and 3
    if "scenario2" in submission:
        if submission["scenario2"].get("adjustedGrossIncome", 0) < 114000:  # Approximate check for missing income
            results["automatic_failure"] = True
            results["failure_reasons"].append("Failed to include all income sources in Scenario 2")
    
    if "scenario3" in submission:
        if submission["scenario3"].get("adjustedGrossIncome", 0) < 48000:  # Approximate check for missing income
            results["automatic_failure"] = True
            results["failure_reasons"].append("Failed to include all income sources in Scenario 3")
    
    # Final pass/fail determination
    overall_passed = (
        results["overall_results"]["passed"] and
        results["critical_calculations"]["passed"] and
        results["scenario_specific"]["passed"] and
        not results["automatic_failure"]
    )
    
    results["passed"] = overall_passed
    results["overall_score"] = results["overall_results"]["overall_score"]
    
    return results

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
    print(f"Pass/Fail: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()