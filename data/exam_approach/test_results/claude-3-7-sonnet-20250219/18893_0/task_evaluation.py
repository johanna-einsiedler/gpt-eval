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

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Contract Compliance Analysis."""
    score = 0
    details = {}
    
    # Overtime violations (3 points)
    correct_overtime = set(answer_key["task1"]["overtime_violations"])
    submitted_overtime = set(submission["task1"]["overtime_violations"])
    overtime_correct = len(correct_overtime.intersection(submitted_overtime))
    overtime_score = overtime_correct
    details["overtime_violations"] = {
        "score": overtime_score,
        "max_points": 3,
        "correct_answers": list(correct_overtime),
        "submitted_answers": list(submitted_overtime),
        "explanation": f"Identified {overtime_correct} out of {len(correct_overtime)} overtime violations correctly."
    }
    score += overtime_score
    
    # Shift differential violations (4 points)
    correct_shift = set(answer_key["task1"]["shift_differential_violations"])
    submitted_shift = set(submission["task1"]["shift_differential_violations"])
    shift_correct = len(correct_shift.intersection(submitted_shift))
    shift_score = shift_correct
    details["shift_differential_violations"] = {
        "score": shift_score,
        "max_points": 4,
        "correct_answers": list(correct_shift),
        "submitted_answers": list(submitted_shift),
        "explanation": f"Identified {shift_correct} out of {len(correct_shift)} shift differential violations correctly."
    }
    score += shift_score
    
    # Break period violations (3 points)
    correct_break = set(answer_key["task1"]["break_period_violations"])
    submitted_break = set(submission["task1"]["break_period_violations"])
    break_correct = len(correct_break.intersection(submitted_break))
    break_score = break_correct * 0.5
    details["break_period_violations"] = {
        "score": break_score,
        "max_points": 3,
        "correct_answers": list(correct_break),
        "submitted_answers": list(submitted_break),
        "explanation": f"Identified {break_correct} out of {len(correct_break)} break period violations correctly (0.5 points each)."
    }
    score += break_score
    
    # Total unpaid wages (2 points)
    correct_wages = answer_key["task1"]["total_unpaid_wages"]
    submitted_wages = submission["task1"]["total_unpaid_wages"]
    wage_diff = abs(correct_wages - submitted_wages)
    
    if wage_diff <= 5:
        wage_score = 2
        explanation = "Within $5 of correct amount."
    elif wage_diff <= 10:
        wage_score = 1
        explanation = "Within $10 of correct amount."
    else:
        wage_score = 0
        explanation = "More than $10 from correct amount."
    
    details["total_unpaid_wages"] = {
        "score": wage_score,
        "max_points": 2,
        "correct_answer": correct_wages,
        "submitted_answer": submitted_wages,
        "explanation": explanation
    }
    score += wage_score
    
    return score, details

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Working Conditions Assessment."""
    score = 0
    details = {}
    
    # Safety violations (4 points)
    correct_violations = set(answer_key["task2"]["safety_violations"])
    submitted_violations = set(submission["task2"]["safety_violations"])
    violations_correct = len(correct_violations.intersection(submitted_violations))
    violations_score = violations_correct
    details["safety_violations"] = {
        "score": violations_score,
        "max_points": 4,
        "correct_answers": list(correct_violations),
        "submitted_answers": list(submitted_violations),
        "explanation": f"Identified {violations_correct} out of {len(correct_violations)} safety violations correctly."
    }
    score += violations_score
    
    # Reporting compliance (1 point)
    correct_compliance = answer_key["task2"]["reporting_compliance"]
    submitted_compliance = submission["task2"]["reporting_compliance"]
    compliance_score = 1 if correct_compliance == submitted_compliance else 0
    details["reporting_compliance"] = {
        "score": compliance_score,
        "max_points": 1,
        "correct_answer": correct_compliance,
        "submitted_answer": submitted_compliance,
        "explanation": "Correct" if compliance_score == 1 else "Incorrect"
    }
    score += compliance_score
    
    # Remediation status (1 point)
    correct_status = answer_key["task2"]["remediation_status"]
    submitted_status = submission["task2"]["remediation_status"]
    status_score = 1 if correct_status == submitted_status else 0
    details["remediation_status"] = {
        "score": status_score,
        "max_points": 1,
        "correct_answer": correct_status,
        "submitted_answer": submitted_status,
        "explanation": "Correct" if status_score == 1 else "Incorrect"
    }
    score += status_score
    
    # Days since last safety meeting (2 points)
    correct_days = answer_key["task2"]["days_since_last_safety_meeting"]
    submitted_days = submission["task2"]["days_since_last_safety_meeting"]
    days_score = 2 if correct_days == submitted_days else 0
    details["days_since_last_safety_meeting"] = {
        "score": days_score,
        "max_points": 2,
        "correct_answer": correct_days,
        "submitted_answer": submitted_days,
        "explanation": "Correct" if days_score == 2 else "Incorrect"
    }
    score += days_score
    
    return score, details

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Wage Structure Compliance."""
    score = 0
    details = {}
    
    # Misclassified employees (5 points)
    correct_misclass = set(answer_key["task3"]["misclassified_employees"])
    submitted_misclass = set(submission["task3"]["misclassified_employees"])
    misclass_correct = len(correct_misclass.intersection(submitted_misclass))
    misclass_score = misclass_correct
    details["misclassified_employees"] = {
        "score": misclass_score,
        "max_points": 5,
        "correct_answers": list(correct_misclass),
        "submitted_answers": list(submitted_misclass),
        "explanation": f"Identified {misclass_correct} out of {len(correct_misclass)} misclassified employees correctly."
    }
    score += misclass_score
    
    # Seniority violations (1 point)
    correct_seniority = set(answer_key["task3"]["seniority_violations"])
    submitted_seniority = set(submission["task3"]["seniority_violations"])
    seniority_score = 1 if correct_seniority == submitted_seniority else 0
    details["seniority_violations"] = {
        "score": seniority_score,
        "max_points": 1,
        "correct_answers": list(correct_seniority),
        "submitted_answers": list(submitted_seniority),
        "explanation": "Correct" if seniority_score == 1 else "Incorrect"
    }
    score += seniority_score
    
    # Wage scale errors (2 points)
    correct_errors = set(answer_key["task3"]["wage_scale_errors"])
    submitted_errors = set(submission["task3"]["wage_scale_errors"])
    errors_correct = len(correct_errors.intersection(submitted_errors))
    errors_score = errors_correct
    details["wage_scale_errors"] = {
        "score": errors_score,
        "max_points": 2,
        "correct_answers": list(correct_errors),
        "submitted_answers": list(submitted_errors),
        "explanation": f"Identified {errors_correct} out of {len(correct_errors)} wage scale errors correctly."
    }
    score += errors_score
    
    # Total wage discrepancy (2 points)
    correct_discrepancy = answer_key["task3"]["total_wage_discrepancy"]
    submitted_discrepancy = submission["task3"]["total_wage_discrepancy"]
    discrepancy_diff = abs(correct_discrepancy - submitted_discrepancy)
    
    if discrepancy_diff <= 2:
        discrepancy_score = 2
        explanation = "Within $2 of correct amount."
    elif discrepancy_diff <= 5:
        discrepancy_score = 1
        explanation = "Within $5 of correct amount."
    else:
        discrepancy_score = 0
        explanation = "More than $5 from correct amount."
    
    details["total_wage_discrepancy"] = {
        "score": discrepancy_score,
        "max_points": 2,
        "correct_answer": correct_discrepancy,
        "submitted_answer": submitted_discrepancy,
        "explanation": explanation
    }
    score += discrepancy_score
    
    return score, details

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "tasks": {}
    }
    
    # Evaluate each task
    task1_score, task1_details = evaluate_task1(submission, answer_key)
    task2_score, task2_details = evaluate_task2(submission, answer_key)
    task3_score, task3_details = evaluate_task3(submission, answer_key)
    
    # Store task results
    results["tasks"]["task1"] = {
        "name": "Contract Compliance Analysis",
        "score": task1_score,
        "max_points": 12,
        "percentage": round((task1_score / 12) * 100, 2),
        "details": task1_details
    }
    
    results["tasks"]["task2"] = {
        "name": "Working Conditions Assessment",
        "score": task2_score,
        "max_points": 8,
        "percentage": round((task2_score / 8) * 100, 2),
        "details": task2_details
    }
    
    results["tasks"]["task3"] = {
        "name": "Wage Structure Compliance",
        "score": task3_score,
        "max_points": 10,
        "percentage": round((task3_score / 10) * 100, 2),
        "details": task3_details
    }
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    total_possible = 30
    overall_percentage = (total_score / total_possible) * 100
    
    results["overall_score"] = round(overall_percentage, 2)
    results["total_points"] = total_score
    results["total_possible"] = total_possible
    
    # Determine if candidate passed
    task1_passed = (task1_score / 12) >= 0.5
    task2_passed = (task2_score / 8) >= 0.5
    task3_passed = (task3_score / 10) >= 0.5
    overall_passed = overall_percentage >= 70
    
    results["passed"] = overall_passed and task1_passed and task2_passed and task3_passed
    results["pass_criteria"] = {
        "overall": {
            "required": "70% of total points (21/30)",
            "achieved": f"{round(overall_percentage, 2)}% ({total_score}/{total_possible})",
            "passed": overall_passed
        },
        "task1": {
            "required": "50% of task points (6/12)",
            "achieved": f"{round((task1_score / 12) * 100, 2)}% ({task1_score}/12)",
            "passed": task1_passed
        },
        "task2": {
            "required": "50% of task points (4/8)",
            "achieved": f"{round((task2_score / 8) * 100, 2)}% ({task2_score}/8)",
            "passed": task2_passed
        },
        "task3": {
            "required": "50% of task points (5/10)",
            "achieved": f"{round((task3_score / 10) * 100, 2)}% ({task3_score}/10)",
            "passed": task3_passed
        }
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()