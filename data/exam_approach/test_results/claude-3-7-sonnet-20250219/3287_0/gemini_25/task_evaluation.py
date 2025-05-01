#!/usr/bin/env python3
"""
Compensation and Benefits Manager Practical Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Compensation and Benefits Manager practical exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, Any, List, Tuple


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_total_personnel_budget(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, float, str]:
    """Evaluate the accuracy of the total personnel budget."""
    submission_value = submission.get("total_personnel_budget", 0)
    answer_key_value = answer_key.get("total_personnel_budget", 0)
    
    if answer_key_value == 0:
        percentage_diff = float('inf')
    else:
        percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
    
    passed = percentage_diff <= 2.0
    
    return passed, percentage_diff, f"Total Personnel Budget: {'PASS' if passed else 'FAIL'} - Difference: {percentage_diff:.2f}%"


def evaluate_department_budgets(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, int, str]:
    """Evaluate the accuracy of department budgets."""
    submission_depts = submission.get("department_budgets", {})
    answer_key_depts = answer_key.get("department_budgets", {})
    
    correct_count = 0
    details = []
    
    for dept in answer_key_depts:
        submission_value = submission_depts.get(dept, 0)
        answer_key_value = answer_key_depts.get(dept, 0)
        
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        
        is_correct = percentage_diff <= 3.0
        if is_correct:
            correct_count += 1
        
        details.append(f"{dept}: {'PASS' if is_correct else 'FAIL'} - Difference: {percentage_diff:.2f}%")
    
    passed = correct_count >= 4
    
    return passed, correct_count, f"Department Budgets: {'PASS' if passed else 'FAIL'} - {correct_count}/5 correct\n" + "\n".join(details)


def evaluate_salary_and_benefits(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, int, str]:
    """Evaluate the accuracy of salary and benefits totals."""
    submission_salary = submission.get("salary_totals", {})
    answer_key_salary = answer_key.get("salary_totals", {})
    
    submission_benefits = submission.get("benefits_totals", {})
    answer_key_benefits = answer_key.get("benefits_totals", {})
    
    correct_count = 0
    details = []
    
    # Check salary totals
    for dept in answer_key_salary:
        submission_value = submission_salary.get(dept, 0)
        answer_key_value = answer_key_salary.get(dept, 0)
        
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        
        is_correct = percentage_diff <= 3.0
        if is_correct:
            correct_count += 1
        
        details.append(f"Salary {dept}: {'PASS' if is_correct else 'FAIL'} - Difference: {percentage_diff:.2f}%")
    
    # Check benefits totals
    for dept in answer_key_benefits:
        submission_value = submission_benefits.get(dept, 0)
        answer_key_value = answer_key_benefits.get(dept, 0)
        
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        
        is_correct = percentage_diff <= 3.0
        if is_correct:
            correct_count += 1
        
        details.append(f"Benefits {dept}: {'PASS' if is_correct else 'FAIL'} - Difference: {percentage_diff:.2f}%")
    
    passed = correct_count >= 8
    
    return passed, correct_count, f"Salary and Benefits Totals: {'PASS' if passed else 'FAIL'} - {correct_count}/10 correct\n" + "\n".join(details)


def evaluate_year_over_year(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, int, str]:
    """Evaluate the accuracy of year-over-year change percentages."""
    submission_yoy = submission.get("year_over_year_change_percentage", {})
    answer_key_yoy = answer_key.get("year_over_year_change_percentage", {})
    
    correct_count = 0
    details = []
    
    for category in answer_key_yoy:
        submission_value = submission_yoy.get(category, 0)
        answer_key_value = answer_key_yoy.get(category, 0)
        
        abs_diff = abs(submission_value - answer_key_value)
        
        is_correct = abs_diff <= 1.0
        if is_correct:
            correct_count += 1
        
        details.append(f"{category}: {'PASS' if is_correct else 'FAIL'} - Absolute Difference: {abs_diff:.2f} percentage points")
    
    passed = correct_count >= 5
    
    return passed, correct_count, f"Year-Over-Year Change Percentages: {'PASS' if passed else 'FAIL'} - {correct_count}/6 correct\n" + "\n".join(details)


def evaluate_benefits_to_salary(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, int, str]:
    """Evaluate the accuracy of benefits-to-salary ratios."""
    submission_ratio = submission.get("benefits_to_salary_ratio", {})
    answer_key_ratio = answer_key.get("benefits_to_salary_ratio", {})
    
    correct_count = 0
    details = []
    
    for category in answer_key_ratio:
        submission_value = submission_ratio.get(category, 0)
        answer_key_value = answer_key_ratio.get(category, 0)
        
        abs_diff = abs(submission_value - answer_key_value)
        
        is_correct = abs_diff <= 0.02
        if is_correct:
            correct_count += 1
        
        details.append(f"{category}: {'PASS' if is_correct else 'FAIL'} - Absolute Difference: {abs_diff:.3f}")
    
    passed = correct_count >= 5
    
    return passed, correct_count, f"Benefits-to-Salary Ratios: {'PASS' if passed else 'FAIL'} - {correct_count}/6 correct\n" + "\n".join(details)


def evaluate_headcount(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[bool, int, str]:
    """Evaluate the accuracy of headcount figures."""
    submission_headcount = submission.get("headcount_by_department", {})
    answer_key_headcount = answer_key.get("headcount_by_department", {})
    
    correct_count = 0
    details = []
    
    for category in answer_key_headcount:
        submission_value = submission_headcount.get(category, 0)
        answer_key_value = answer_key_headcount.get(category, 0)
        
        is_correct = submission_value == answer_key_value
        if is_correct:
            correct_count += 1
        
        details.append(f"{category}: {'PASS' if is_correct else 'FAIL'} - Submitted: {submission_value}, Expected: {answer_key_value}")
    
    passed = correct_count >= 5
    
    return passed, correct_count, f"Headcount: {'PASS' if passed else 'FAIL'} - {correct_count}/6 correct\n" + "\n".join(details)


def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "criteria_results": [],
        "passed_criteria_count": 0,
        "total_criteria_count": 6,
        "overall_score": 0.0,
        "passed": False,
        "exceptional_performance": False
    }
    
    # Evaluate each criterion
    criteria_evaluations = [
        evaluate_total_personnel_budget(submission, answer_key),
        evaluate_department_budgets(submission, answer_key),
        evaluate_salary_and_benefits(submission, answer_key),
        evaluate_year_over_year(submission, answer_key),
        evaluate_benefits_to_salary(submission, answer_key),
        evaluate_headcount(submission, answer_key)
    ]
    
    # Process evaluation results
    for passed, score, details in criteria_evaluations:
        results["criteria_results"].append({
            "passed": passed,
            "score": score,
            "details": details
        })
        
        if passed:
            results["passed_criteria_count"] += 1
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["passed_criteria_count"] / results["total_criteria_count"]) * 100
    
    # Determine if the candidate passed
    results["passed"] = results["passed_criteria_count"] >= 5
    
    # Check for exceptional performance
    # Exceptional: All monetary values within 1% and exact matches on all headcount figures
    exceptional = True
    
    # Check total personnel budget
    total_budget_diff = abs(submission.get("total_personnel_budget", 0) - answer_key.get("total_personnel_budget", 0)) / answer_key.get("total_personnel_budget", 1) * 100
    if total_budget_diff > 1.0:
        exceptional = False
    
    # Check department budgets
    for dept in answer_key.get("department_budgets", {}):
        submission_value = submission.get("department_budgets", {}).get(dept, 0)
        answer_key_value = answer_key.get("department_budgets", {}).get(dept, 0)
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        if percentage_diff > 1.0:
            exceptional = False
            break
    
    # Check salary and benefits totals
    for dept in answer_key.get("salary_totals", {}):
        submission_value = submission.get("salary_totals", {}).get(dept, 0)
        answer_key_value = answer_key.get("salary_totals", {}).get(dept, 0)
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        if percentage_diff > 1.0:
            exceptional = False
            break
    
    for dept in answer_key.get("benefits_totals", {}):
        submission_value = submission.get("benefits_totals", {}).get(dept, 0)
        answer_key_value = answer_key.get("benefits_totals", {}).get(dept, 0)
        if answer_key_value == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = abs(submission_value - answer_key_value) / answer_key_value * 100
        if percentage_diff > 1.0:
            exceptional = False
            break
    
    # Check headcount
    for category in answer_key.get("headcount_by_department", {}):
        submission_value = submission.get("headcount_by_department", {}).get(category, 0)
        answer_key_value = answer_key.get("headcount_by_department", {}).get(category, 0)
        if submission_value != answer_key_value:
            exceptional = False
            break
    
    results["exceptional_performance"] = exceptional
    
    return results


def main():
    """Main function to process command line arguments and evaluate the submission."""
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
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Passed: {'Yes' if results['passed'] else 'No'}")
    if results['exceptional_performance']:
        print("Exceptional Performance: Yes")


if __name__ == "__main__":
    main()