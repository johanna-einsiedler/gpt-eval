#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Historical Trend Analysis and Resource Projection."""
    score = 0
    details = {}
    
    # Evaluate average growth rates (10 points)
    growth_rates_correct = 0
    growth_rate_details = {}
    for category, expected in answer_key["average_growth_rates"].items():
        if category in submission["average_growth_rates"]:
            actual = submission["average_growth_rates"][category]
            # Allow ±0.01 tolerance
            if abs(actual - expected) <= 0.01:
                growth_rates_correct += 1
                growth_rate_details[category] = {"status": "correct", "submitted": actual, "expected": expected}
            else:
                growth_rate_details[category] = {"status": "incorrect", "submitted": actual, "expected": expected}
        else:
            growth_rate_details[category] = {"status": "missing", "expected": expected}
    
    growth_rate_score = growth_rates_correct
    details["average_growth_rates"] = {
        "score": growth_rate_score,
        "max_score": 10,
        "details": growth_rate_details
    }
    score += growth_rate_score
    
    # Evaluate projected costs (10 points)
    projected_costs_correct = 0
    projected_costs_details = {}
    for category, expected in answer_key["projected_costs"].items():
        if category in submission["projected_costs"]:
            actual = submission["projected_costs"][category]
            # Allow ±1% tolerance
            if abs(actual - expected) <= 0.01 * expected:
                projected_costs_correct += 1
                projected_costs_details[category] = {"status": "correct", "submitted": actual, "expected": expected}
            else:
                projected_costs_details[category] = {"status": "incorrect", "submitted": actual, "expected": expected}
        else:
            projected_costs_details[category] = {"status": "missing", "expected": expected}
    
    projected_costs_score = projected_costs_correct
    details["projected_costs"] = {
        "score": projected_costs_score,
        "max_score": 10,
        "details": projected_costs_details
    }
    score += projected_costs_score
    
    # Evaluate top growth categories (10 points)
    top_categories_correct = 0
    top_categories_details = {}
    expected_categories = set(answer_key["top_growth_categories"])
    
    if len(submission["top_growth_categories"]) == 3:
        for i, category in enumerate(submission["top_growth_categories"]):
            if category in expected_categories:
                top_categories_correct += 1
                top_categories_details[f"category_{i+1}"] = {"status": "correct", "submitted": category}
            else:
                top_categories_details[f"category_{i+1}"] = {"status": "incorrect", "submitted": category, "expected": "One of " + ", ".join(expected_categories)}
    else:
        top_categories_details["error"] = "Expected exactly 3 categories"
    
    top_categories_score = (top_categories_correct / 3) * 10
    details["top_growth_categories"] = {
        "score": top_categories_score,
        "max_score": 10,
        "details": top_categories_details
    }
    score += top_categories_score
    
    return score, details

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Program Cost Analysis and Resource Allocation."""
    score = 0
    details = {}
    
    # Evaluate total resources needed (10 points)
    total_resources_expected = answer_key["total_resources_needed"]
    total_resources_actual = submission["total_resources_needed"]
    
    # Allow ±1% tolerance
    if abs(total_resources_actual - total_resources_expected) <= 0.01 * total_resources_expected:
        total_resources_score = 10
        total_resources_status = "correct"
    else:
        total_resources_score = 0
        total_resources_status = "incorrect"
    
    details["total_resources_needed"] = {
        "score": total_resources_score,
        "max_score": 10,
        "details": {
            "status": total_resources_status,
            "submitted": total_resources_actual,
            "expected": total_resources_expected
        }
    }
    score += total_resources_score
    
    # Evaluate departmental allocation (10 points)
    dept_allocation_correct = 0
    dept_allocation_details = {}
    
    for dept, expected in answer_key["departmental_allocation"].items():
        if dept in submission["departmental_allocation"]:
            actual = submission["departmental_allocation"][dept]
            # Allow ±1% tolerance
            if abs(actual - expected) <= 0.01 * expected:
                dept_allocation_correct += 1
                dept_allocation_details[dept] = {"status": "correct", "submitted": actual, "expected": expected}
            else:
                dept_allocation_details[dept] = {"status": "incorrect", "submitted": actual, "expected": expected}
        else:
            dept_allocation_details[dept] = {"status": "missing", "expected": expected}
    
    dept_allocation_score = (dept_allocation_correct / 4) * 10
    details["departmental_allocation"] = {
        "score": dept_allocation_score,
        "max_score": 10,
        "details": dept_allocation_details
    }
    score += dept_allocation_score
    
    # Evaluate cost per unit (10 points)
    cost_per_unit_correct = 0
    cost_per_unit_details = {}
    
    for dept, expected in answer_key["cost_per_unit"].items():
        if dept in submission["cost_per_unit"]:
            actual = submission["cost_per_unit"][dept]
            # Allow ±2% tolerance
            if abs(actual - expected) <= 0.02 * expected:
                cost_per_unit_correct += 1
                cost_per_unit_details[dept] = {"status": "correct", "submitted": actual, "expected": expected}
            else:
                cost_per_unit_details[dept] = {"status": "incorrect", "submitted": actual, "expected": expected}
        else:
            cost_per_unit_details[dept] = {"status": "missing", "expected": expected}
    
    cost_per_unit_score = (cost_per_unit_correct / 4) * 10
    details["cost_per_unit"] = {
        "score": cost_per_unit_score,
        "max_score": 10,
        "details": cost_per_unit_details
    }
    score += cost_per_unit_score
    
    # Evaluate resource constraints (5 points)
    constraints_correct = 0
    constraints_details = {}
    expected_constraints = set(answer_key["resource_constraints"])
    
    if len(submission["resource_constraints"]) == 2:
        for i, constraint in enumerate(submission["resource_constraints"]):
            if constraint in expected_constraints:
                constraints_correct += 1
                constraints_details[f"constraint_{i+1}"] = {"status": "correct", "submitted": constraint}
            else:
                constraints_details[f"constraint_{i+1}"] = {"status": "incorrect", "submitted": constraint, "expected": "One of " + ", ".join(expected_constraints)}
    else:
        constraints_details["error"] = "Expected exactly 2 constraints"
    
    constraints_score = (constraints_correct / 2) * 5
    details["resource_constraints"] = {
        "score": constraints_score,
        "max_score": 5,
        "details": constraints_details
    }
    score += constraints_score
    
    return score, details

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Variance Analysis and Resource Determination."""
    score = 0
    details = {}
    
    # Evaluate significant variances (15 points)
    variances_correct = 0
    variances_details = {}
    expected_variances = set(answer_key["significant_variances"].keys())
    submitted_variances = set(submission["significant_variances"].keys())
    
    # Check if the correct categories are identified
    for category in submitted_variances:
        if category in expected_variances:
            submitted_data = submission["significant_variances"][category]
            expected_data = answer_key["significant_variances"][category]
            
            # Check budgeted amount
            budget_correct = abs(submitted_data["budgeted"] - expected_data["budgeted"]) <= 0.01 * expected_data["budgeted"]
            
            # Check actual projected
            actual_correct = abs(submitted_data["actual_projected"] - expected_data["actual_projected"]) <= 0.01 * expected_data["actual_projected"]
            
            # Check variance percent
            variance_correct = abs(submitted_data["variance_percent"] - expected_data["variance_percent"]) <= 0.02
            
            if budget_correct and actual_correct and variance_correct:
                variances_correct += 1
                variances_details[category] = {"status": "correct", "submitted": submitted_data, "expected": expected_data}
            else:
                variances_details[category] = {
                    "status": "partially correct",
                    "submitted": submitted_data,
                    "expected": expected_data,
                    "details": {
                        "budgeted": "correct" if budget_correct else "incorrect",
                        "actual_projected": "correct" if actual_correct else "incorrect",
                        "variance_percent": "correct" if variance_correct else "incorrect"
                    }
                }
        else:
            variances_details[category] = {"status": "incorrect", "submitted": submission["significant_variances"][category], "expected": "Not a significant variance"}
    
    # Check for missing categories
    for category in expected_variances - submitted_variances:
        variances_details[category] = {"status": "missing", "expected": answer_key["significant_variances"][category]}
    
    # Calculate score based on correct identifications (out of 4 expected variances)
    variances_score = min(15, (variances_correct / 4) * 15)
    details["significant_variances"] = {
        "score": variances_score,
        "max_score": 15,
        "details": variances_details
    }
    score += variances_score
    
    # Evaluate additional resources needed (10 points)
    additional_resources_expected = answer_key["additional_resources_needed"]
    additional_resources_actual = submission["additional_resources_needed"]
    
    # Allow ±2% tolerance
    if abs(additional_resources_actual - additional_resources_expected) <= 0.02 * additional_resources_expected:
        additional_resources_score = 10
        additional_resources_status = "correct"
    else:
        additional_resources_score = 0
        additional_resources_status = "incorrect"
    
    details["additional_resources_needed"] = {
        "score": additional_resources_score,
        "max_score": 10,
        "details": {
            "status": additional_resources_status,
            "submitted": additional_resources_actual,
            "expected": additional_resources_expected
        }
    }
    score += additional_resources_score
    
    # Evaluate recommended adjustments (10 points)
    adjustments_correct = 0
    adjustments_details = {}
    expected_adjustments = answer_key["recommended_adjustments"]
    submitted_adjustments = submission["recommended_adjustments"]
    
    # Count how many categories have correct adjustment values
    for category, expected in expected_adjustments.items():
        if category in submitted_adjustments:
            actual = submitted_adjustments[category]
            # Allow ±2% tolerance
            if abs(actual - expected) <= 0.02 * expected:
                adjustments_correct += 1
                adjustments_details[category] = {"status": "correct", "submitted": actual, "expected": expected}
            else:
                adjustments_details[category] = {"status": "incorrect", "submitted": actual, "expected": expected}
        else:
            adjustments_details[category] = {"status": "missing", "expected": expected}
    
    # Check for extra categories
    for category in submitted_adjustments:
        if category not in expected_adjustments:
            adjustments_details[category] = {"status": "extra", "submitted": submitted_adjustments[category]}
    
    # Calculate score based on correct adjustments (out of 4 expected adjustments)
    adjustments_score = min(10, (adjustments_correct / 4) * 10)
    details["recommended_adjustments"] = {
        "score": adjustments_score,
        "max_score": 10,
        "details": adjustments_details
    }
    score += adjustments_score
    
    return score, details

def check_critical_errors(submission, answer_key):
    """Check for critical errors that would result in automatic failure."""
    critical_errors = []
    
    # Check for incorrect calculation methodology for growth rates
    growth_rates_correct = 0
    for category, expected in answer_key["task1"]["average_growth_rates"].items():
        if category in submission["task1"]["average_growth_rates"]:
            actual = submission["task1"]["average_growth_rates"][category]
            if abs(actual - expected) <= 0.05:  # Wider tolerance to check methodology
                growth_rates_correct += 1
    
    if growth_rates_correct < 5:  # Less than half correct indicates wrong methodology
        critical_errors.append("Incorrect calculation methodology for growth rates")
    
    # Check for failure to identify any significant variances
    if len(submission["task3"]["significant_variances"]) == 0:
        critical_errors.append("Failure to identify any significant variances")
    
    # Check for incorrect application of resource allocation percentages
    total_resources = submission["task2"]["total_resources_needed"]
    operations_allocation = submission["task2"]["departmental_allocation"]["Operations"]
    admin_allocation = submission["task2"]["departmental_allocation"]["Administration"]
    dev_allocation = submission["task2"]["departmental_allocation"]["Development"]
    support_allocation = submission["task2"]["departmental_allocation"]["Support"]
    
    # Check if allocations roughly match the expected percentages (40%, 15%, 30%, 15%)
    if not (0.38 <= operations_allocation / total_resources <= 0.42):
        critical_errors.append("Incorrect application of resource allocation percentages (Operations)")
    if not (0.13 <= admin_allocation / total_resources <= 0.17):
        critical_errors.append("Incorrect application of resource allocation percentages (Administration)")
    if not (0.28 <= dev_allocation / total_resources <= 0.32):
        critical_errors.append("Incorrect application of resource allocation percentages (Development)")
    if not (0.13 <= support_allocation / total_resources <= 0.17):
        critical_errors.append("Incorrect application of resource allocation percentages (Support)")
    
    return critical_errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_score, task1_details = evaluate_task1(submission["task1"], answer_key["task1"])
    task2_score, task2_details = evaluate_task2(submission["task2"], answer_key["task2"])
    task3_score, task3_details = evaluate_task3(submission["task3"], answer_key["task3"])
    
    # Check for critical errors
    critical_errors = check_critical_errors(submission, answer_key)
    
    # Calculate overall score
    max_score = 100
    raw_score = task1_score + task2_score + task3_score
    
    # If there are critical errors, the candidate fails
    if critical_errors:
        overall_score = 0
        result = "FAIL (Critical Errors)"
    else:
        overall_score = (raw_score / max_score) * 100
        result = "PASS" if overall_score >= 70 else "FAIL"
    
    # Prepare the results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_score,
        "result": result,
        "task_scores": {
            "task1": {
                "score": task1_score,
                "max_score": 30,
                "percentage": (task1_score / 30) * 100,
                "details": task1_details
            },
            "task2": {
                "score": task2_score,
                "max_score": 35,
                "percentage": (task2_score / 35) * 100,
                "details": task2_details
            },
            "task3": {
                "score": task3_score,
                "max_score": 35,
                "percentage": (task3_score / 35) * 100,
                "details": task3_details
            }
        },
        "critical_errors": critical_errors
    }
    
    # Save the results to a file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {overall_score:.2f}% - {result}")

if __name__ == "__main__":
    main()