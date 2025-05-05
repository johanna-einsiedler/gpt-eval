#!/usr/bin/env python3
import json
import sys
import os

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Budget Development (40 points)"""
    results = {"points_earned": 0, "max_points": 40, "details": {}}
    
    categories = [
        ("total_compensation_budget", 10),
        ("total_benefits_budget", 10),
        ("total_training_budget", 10),
        ("total_hr_budget", 10)
    ]
    
    for category, points in categories:
        submission_value = submission["task1"][category]
        answer_value = answer_key["task1"][category]
        
        # Allow ±2% variance
        tolerance = answer_value * 0.02
        if abs(submission_value - answer_value) <= tolerance:
            results["points_earned"] += points
            results["details"][category] = {
                "points_earned": points,
                "max_points": points,
                "submission": submission_value,
                "answer": answer_value,
                "correct": True
            }
        else:
            results["details"][category] = {
                "points_earned": 0,
                "max_points": points,
                "submission": submission_value,
                "answer": answer_value,
                "correct": False
            }
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Budget Variance Analysis (20 points)"""
    results = {"points_earned": 0, "max_points": 20, "details": {}}
    
    categories = [
        ("variance_category_1", 5),
        ("variance_percentage_1", 5),
        ("variance_category_2", 5),
        ("variance_percentage_2", 5)
    ]
    
    for category, points in categories:
        submission_value = submission["task2"][category]
        answer_value = answer_key["task2"][category]
        
        # Exact match required for categories and percentages
        if submission_value == answer_value:
            results["points_earned"] += points
            results["details"][category] = {
                "points_earned": points,
                "max_points": points,
                "submission": submission_value,
                "answer": answer_value,
                "correct": True
            }
        else:
            results["details"][category] = {
                "points_earned": 0,
                "max_points": points,
                "submission": submission_value,
                "answer": answer_value,
                "correct": False
            }
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Cost Reduction Scenario (20 points)"""
    results = {"points_earned": 0, "max_points": 20, "details": {}}
    
    # Check option selection (10 points)
    if submission["task3"]["option_selected"] == answer_key["task3"]["option_selected"]:
        results["points_earned"] += 10
        results["details"]["option_selected"] = {
            "points_earned": 10,
            "max_points": 10,
            "submission": submission["task3"]["option_selected"],
            "answer": answer_key["task3"]["option_selected"],
            "correct": True
        }
    else:
        results["details"]["option_selected"] = {
            "points_earned": 0,
            "max_points": 10,
            "submission": submission["task3"]["option_selected"],
            "answer": answer_key["task3"]["option_selected"],
            "correct": False
        }
    
    # Check projected savings (10 points)
    if submission["task3"]["projected_savings"] == answer_key["task3"]["projected_savings"]:
        results["points_earned"] += 10
        results["details"]["projected_savings"] = {
            "points_earned": 10,
            "max_points": 10,
            "submission": submission["task3"]["projected_savings"],
            "answer": answer_key["task3"]["projected_savings"],
            "correct": True
        }
    else:
        results["details"]["projected_savings"] = {
            "points_earned": 0,
            "max_points": 10,
            "submission": submission["task3"]["projected_savings"],
            "answer": answer_key["task3"]["projected_savings"],
            "correct": False
        }
    
    return results

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Training Budget Allocation (20 points)"""
    results = {"points_earned": 0, "max_points": 20, "details": {}}
    
    # Check if all departments are within tolerance (±$100)
    departments = [
        "department_1_allocation",
        "department_2_allocation",
        "department_3_allocation",
        "department_4_allocation"
    ]
    
    all_within_tolerance = True
    department_details = {}
    
    for dept in departments:
        submission_value = submission["task4"][dept]
        answer_value = answer_key["task4"][dept]
        
        # Allow ±$100 variance
        if abs(submission_value - answer_value) <= 100:
            correct = True
        else:
            correct = False
            all_within_tolerance = False
        
        department_details[dept] = {
            "submission": submission_value,
            "answer": answer_value,
            "correct": correct
        }
    
    # Award points for methodology (10 points) if all departments are within tolerance
    if all_within_tolerance:
        results["points_earned"] += 10
        results["details"]["allocation_methodology"] = {
            "points_earned": 10,
            "max_points": 10,
            "correct": True,
            "note": "All department allocations within acceptable tolerance"
        }
    else:
        results["details"]["allocation_methodology"] = {
            "points_earned": 0,
            "max_points": 10,
            "correct": False,
            "note": "One or more department allocations outside acceptable tolerance"
        }
    
    # Award points for accurate calculations (10 points)
    # Count how many departments are correct
    correct_departments = sum(1 for dept in department_details if department_details[dept]["correct"])
    points_per_department = 10 / len(departments)
    calculation_points = int(correct_departments * points_per_department)
    
    results["points_earned"] += calculation_points
    results["details"]["accurate_calculations"] = {
        "points_earned": calculation_points,
        "max_points": 10,
        "correct": correct_departments == len(departments),
        "note": f"{correct_departments} of {len(departments)} departments correctly calculated"
    }
    
    # Add department details
    results["details"]["departments"] = department_details
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
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
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    task4_results = evaluate_task4(submission, answer_key)
    
    # Calculate overall score
    total_points_earned = (
        task1_results["points_earned"] +
        task2_results["points_earned"] +
        task3_results["points_earned"] +
        task4_results["points_earned"]
    )
    
    total_possible_points = (
        task1_results["max_points"] +
        task2_results["max_points"] +
        task3_results["max_points"] +
        task4_results["max_points"]
    )
    
    overall_score = (total_points_earned / total_possible_points) * 100
    
    # Determine if candidate passed (70 points or higher)
    passed = total_points_earned >= 70
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_score,
        "total_points_earned": total_points_earned,
        "total_possible_points": total_possible_points,
        "passed": passed,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results,
            "task4": task4_results
        }
    }
    
    # Save results to file
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}% ({total_points_earned}/{total_possible_points} points)")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

if __name__ == "__main__":
    main()