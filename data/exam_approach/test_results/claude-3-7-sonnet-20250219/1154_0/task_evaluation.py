#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Union

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: List[int], answer_key: List[int]) -> Dict:
    """Evaluate Task 1: Critical Questions."""
    correct_count = len(set(submission) & set(answer_key))
    return {
        "score": correct_count,
        "max_score": 5,
        "details": {
            "correct_answers": answer_key,
            "submitted_answers": submission,
            "correct_count": correct_count
        }
    }

def evaluate_task2(submission: Dict[str, str], answer_key: Dict[str, str]) -> Dict:
    """Evaluate Task 2: Requirements Met."""
    correct_count = 0
    details = {}
    
    for req_num in range(1, 6):
        req_key = f"requirement{req_num}"
        if req_key in submission and req_key in answer_key:
            is_correct = submission[req_key] == answer_key[req_key]
            correct_count += 1 if is_correct else 0
            details[req_key] = {
                "submitted": submission[req_key],
                "correct": answer_key[req_key],
                "is_correct": is_correct
            }
    
    return {
        "score": correct_count,
        "max_score": 5,
        "details": details
    }

def evaluate_task3(submission: Dict[str, float], answer_key: Dict[str, float]) -> Dict:
    """Evaluate Task 3: Pricing Calculations."""
    correct_count = 0
    details = {}
    
    for key in ["total_cost", "per_unit_cost", "percentage_difference"]:
        if key in submission and key in answer_key:
            # Allow for small floating point differences
            is_correct = abs(submission[key] - answer_key[key]) < 0.01
            correct_count += 1 if is_correct else 0
            details[key] = {
                "submitted": submission[key],
                "correct": answer_key[key],
                "is_correct": is_correct
            }
    
    return {
        "score": correct_count,
        "max_score": 3,
        "details": details
    }

def evaluate_task4(submission: Dict[str, str], answer_key: Dict[str, str]) -> Dict:
    """Evaluate Task 4: Vendor Capabilities."""
    correct_count = 0
    details = {}
    
    for cap_num in range(1, 6):
        cap_key = f"capability{cap_num}"
        if cap_key in submission and cap_key in answer_key:
            is_correct = submission[cap_key] == answer_key[cap_key]
            correct_count += 1 if is_correct else 0
            details[cap_key] = {
                "submitted": submission[cap_key],
                "correct": answer_key[cap_key],
                "is_correct": is_correct
            }
    
    return {
        "score": correct_count,
        "max_score": 5,
        "details": details
    }

def evaluate_task5(submission: List[int], answer_key: List[int]) -> Dict:
    """Evaluate Task 5: Documentation Items."""
    correct_count = len(set(submission) & set(answer_key))
    return {
        "score": correct_count,
        "max_score": 5,
        "details": {
            "correct_answers": answer_key,
            "submitted_answers": submission,
            "correct_count": correct_count
        }
    }

def check_critical_errors(results: Dict) -> Dict:
    """Check for critical errors that would result in automatic failure."""
    critical_errors = []
    
    # Check for incorrect total cost calculation
    if "task3" in results and "details" in results["task3"]:
        if "total_cost" in results["task3"]["details"]:
            if not results["task3"]["details"]["total_cost"]["is_correct"]:
                critical_errors.append("Incorrect total cost calculation")
    
    # Check for failure to identify missing armrest width adjustment
    if "task2" in results and "details" in results["task2"]:
        if "requirement3" in results["task2"]["details"]:
            if not results["task2"]["details"]["requirement3"]["is_correct"]:
                critical_errors.append("Failed to identify missing armrest width adjustment")
    
    # Check for failure to recognize insufficient information about quality assurance
    if "task4" in results and "details" in results["task4"]:
        if "capability3" in results["task4"]["details"]:
            if not results["task4"]["details"]["capability3"]["is_correct"]:
                critical_errors.append("Failed to recognize insufficient information about quality assurance")
    
    return {
        "has_critical_errors": len(critical_errors) > 0,
        "critical_errors": critical_errors
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {}
    
    # Evaluate each task
    if "task1_critical_questions" in submission and "task1_critical_questions" in answer_key:
        results["task1"] = evaluate_task1(
            submission["task1_critical_questions"], 
            answer_key["task1_critical_questions"]
        )
    
    if "task2_requirements_met" in submission and "task2_requirements_met" in answer_key:
        results["task2"] = evaluate_task2(
            submission["task2_requirements_met"], 
            answer_key["task2_requirements_met"]
        )
    
    if "task3_pricing" in submission and "task3_pricing" in answer_key:
        results["task3"] = evaluate_task3(
            submission["task3_pricing"], 
            answer_key["task3_pricing"]
        )
    
    if "task4_vendor_capabilities" in submission and "task4_vendor_capabilities" in answer_key:
        results["task4"] = evaluate_task4(
            submission["task4_vendor_capabilities"], 
            answer_key["task4_vendor_capabilities"]
        )
    
    if "task5_documentation_items" in submission and "task5_documentation_items" in answer_key:
        results["task5"] = evaluate_task5(
            submission["task5_documentation_items"], 
            answer_key["task5_documentation_items"]
        )
    
    # Calculate overall score
    total_score = sum(task["score"] for task in results.values())
    max_score = sum(task["max_score"] for task in results.values())
    overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    # Check for critical errors
    critical_error_check = check_critical_errors(results)
    
    # Check task-specific minimum scores
    task_minimums = {
        "task1": 3,  # At least 3/5 correct critical questions
        "task2": 3,  # At least 3/5 correct requirement evaluations
        "task3": 3,  # All pricing calculations must be correct (3/3)
        "task4": 3,  # At least 3/5 correct capability assessments
        "task5": 3   # At least 3/5 correct documentation items
    }
    
    task_minimum_failures = []
    for task, min_score in task_minimums.items():
        if task in results and results[task]["score"] < min_score:
            task_minimum_failures.append(f"{task} score below minimum ({results[task]['score']}/{min_score})")
    
    # Determine if candidate passed
    passed = (
        overall_percentage >= 70 and 
        not critical_error_check["has_critical_errors"] and
        len(task_minimum_failures) == 0
    )
    
    return {
        "task_results": results,
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_score,
        "critical_errors": critical_error_check,
        "task_minimum_failures": task_minimum_failures,
        "passed": passed,
        "candidate_id": submission.get("candidate_id", "Unknown")
    }

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
    print(f"Pass/Fail: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()