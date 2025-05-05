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

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Create an Annual IT Project Budget."""
    score = 0
    max_score = 40
    feedback = []
    
    # Check if total budget is exactly $450,000
    if submission["task1"]["total_budget"] == 450000:
        score += 10
        feedback.append("Total budget is correctly set to $450,000.")
    else:
        feedback.append("Total budget is not $450,000. This is a critical error.")
        return 0, feedback  # Automatic failure condition
    
    # Check if allocations sum to total budget
    allocation_sum = (
        submission["task1"]["hardware_allocation"] +
        submission["task1"]["software_allocation"] +
        submission["task1"]["personnel_allocation"] +
        submission["task1"]["services_allocation"] +
        submission["task1"]["contingency_allocation"]
    )
    
    if allocation_sum == 450000:
        score += 10
        feedback.append("All allocations correctly sum to $450,000.")
    else:
        feedback.append(f"Allocations sum to ${allocation_sum}, not $450,000. This is a critical error.")
        return 0, feedback  # Automatic failure condition
    
    # Check if allocations are within recommended ranges
    total = 450000
    allocation_checks = [
        ("Hardware", submission["task1"]["hardware_allocation"], 0.25 * total, 0.30 * total),
        ("Software", submission["task1"]["software_allocation"], 0.35 * total, 0.40 * total),
        ("Personnel", submission["task1"]["personnel_allocation"], 0.25 * total, 0.30 * total),
        ("Services", submission["task1"]["services_allocation"], 0.15 * total, 0.20 * total),
        ("Contingency", submission["task1"]["contingency_allocation"], 0.05 * total, 0.10 * total)
    ]
    
    within_range_count = 0
    for category, value, min_val, max_val in allocation_checks:
        if min_val <= value <= max_val:
            within_range_count += 1
            feedback.append(f"{category} allocation (${value}) is within recommended range (${min_val:.0f}-${max_val:.0f}).")
        else:
            feedback.append(f"{category} allocation (${value}) is outside recommended range (${min_val:.0f}-${max_val:.0f}).")
    
    # Score based on how many allocations are within range
    range_score = 20 * (within_range_count / 5)
    score += range_score
    
    return score, feedback

def evaluate_task2(submission, answer_key, task1_submission):
    """Evaluate Task 2: Budget Variance Analysis."""
    score = 0
    max_score = 30
    feedback = []
    
    # Calculate expected variances based on the candidate's Task 1 allocations
    # The midyear budget is 50% of the annual budget
    expected_variances = {
        "hardware": task1_submission["hardware_allocation"] / 2 - 54000,
        "software": task1_submission["software_allocation"] / 2 - 103500,
        "personnel": task1_submission["personnel_allocation"] / 2 - 81000,
        "services": task1_submission["services_allocation"] / 2 - 49500,
        "contingency": task1_submission["contingency_allocation"] / 2 - 9000
    }
    
    expected_total_variance = sum(expected_variances.values())
    
    # Check individual variance calculations
    variance_correct_count = 0
    for category in ["hardware", "software", "personnel", "services", "contingency"]:
        submission_key = f"variance_{category}"
        expected = expected_variances[category]
        submitted = submission["task2"][submission_key]
        
        # Allow for small rounding differences (±2)
        if abs(submitted - expected) <= 2:
            variance_correct_count += 1
            feedback.append(f"{category.capitalize()} variance correctly calculated as ${submitted}.")
        else:
            feedback.append(f"{category.capitalize()} variance incorrectly calculated as ${submitted}, expected ${expected:.0f}.")
    
    # Score based on correct variance calculations (5 points per correct variance)
    score += 5 * variance_correct_count
    
    # Check total variance calculation
    submitted_total = submission["task2"]["variance_total"]
    if abs(submitted_total - expected_total_variance) <= 2:  # Allow for small rounding differences
        score += 5
        feedback.append(f"Total variance correctly calculated as ${submitted_total}.")
    else:
        feedback.append(f"Total variance incorrectly calculated as ${submitted_total}, expected ${expected_total_variance:.0f}.")
    
    # Find category with largest absolute variance
    abs_variances = {k: abs(v) for k, v in expected_variances.items()}
    max_abs_variance = max(abs_variances.values())
    largest_variance_categories = [k.capitalize() for k, v in abs_variances.items() if abs(v) == max_abs_variance]
    
    submitted_largest = submission["task2"]["largest_variance_category"]
    if submitted_largest in largest_variance_categories:
        score += 5
        feedback.append(f"Correctly identified {submitted_largest} as a category with largest absolute variance.")
    else:
        feedback.append(f"Incorrectly identified {submitted_largest} as the category with largest absolute variance. Expected one of: {', '.join(largest_variance_categories)}.")
    
    return score, feedback

def evaluate_task3(submission, answer_key, task1_submission):
    """Evaluate Task 3: Budget Reallocation."""
    score = 0
    max_score = 30
    feedback = []
    
    # Get the selected option
    selected_option = submission["task3"]["selected_option"]
    if selected_option not in ["A", "B", "C"]:
        feedback.append(f"Invalid option selected: {selected_option}. Must be A, B, or C.")
        return 0, feedback
    
    feedback.append(f"Selected Option {selected_option}.")
    
    # Calculate expected reallocations based on the selected option and Task 1 allocations
    original_budget = {
        "hardware": task1_submission["hardware_allocation"],
        "software": task1_submission["software_allocation"],
        "personnel": task1_submission["personnel_allocation"],
        "services": task1_submission["services_allocation"],
        "contingency": task1_submission["contingency_allocation"]
    }
    
    expected_budget = original_budget.copy()
    
    if selected_option == "A":
        # Increase Software by 15%, decrease Hardware by 10%
        expected_budget["software"] = int(original_budget["software"] * 1.15)
        expected_budget["hardware"] = int(original_budget["hardware"] * 0.90)
    elif selected_option == "B":
        # Increase Personnel by 12%, decrease Services by 8%
        expected_budget["personnel"] = int(original_budget["personnel"] * 1.12)
        expected_budget["services"] = int(original_budget["services"] * 0.92)
    elif selected_option == "C":
        # Increase Services by 20%, decrease Contingency by 25%
        expected_budget["services"] = int(original_budget["services"] * 1.20)
        expected_budget["contingency"] = int(original_budget["contingency"] * 0.75)
    
    # Check if the reallocated budget matches expectations
    submitted_budget = submission["task3"]["reallocated_budget"]
    correct_categories = 0
    
    for category in ["hardware", "software", "personnel", "services", "contingency"]:
        expected = expected_budget[category]
        submitted = submitted_budget[category]
        
        # Allow for small rounding differences (±2)
        if abs(submitted - expected) <= 2:
            correct_categories += 1
            feedback.append(f"{category.capitalize()} correctly reallocated to ${submitted}.")
        else:
            feedback.append(f"{category.capitalize()} incorrectly reallocated to ${submitted}, expected ${expected}.")
    
    # Score based on correct category reallocations (4 points per correct category)
    score += 4 * correct_categories
    
    # Check if total budget remains unchanged
    original_total = sum(original_budget.values())
    reallocated_total = sum(submitted_budget.values())
    
    if reallocated_total == 450000:
        score += 10
        feedback.append("Total budget correctly maintained at $450,000.")
    else:
        feedback.append(f"Total budget changed to ${reallocated_total}, should remain at $450,000. This is a critical error.")
        return 0, feedback  # Automatic failure condition
    
    return score, feedback

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Extract Task 1 submission for use in other evaluations
    task1_submission = submission["task1"]
    
    # Evaluate each task
    task1_score, task1_feedback = evaluate_task1(submission, answer_key)
    task2_score, task2_feedback = evaluate_task2(submission, answer_key, task1_submission)
    task3_score, task3_feedback = evaluate_task3(submission, answer_key, task1_submission)
    
    # Calculate overall score
    max_total_score = 100
    total_score = task1_score + task2_score + task3_score
    overall_percentage = (total_score / max_total_score) * 100
    
    # Determine if candidate passed
    task1_percentage = (task1_score / 40) * 100
    task2_percentage = (task2_score / 30) * 100
    task3_percentage = (task3_score / 30) * 100
    
    passed = (
        overall_percentage >= 70 and
        task1_percentage >= 60 and
        task2_percentage >= 60 and
        task3_percentage >= 60
    )
    
    # Prepare results
    results = {
        "overall_score": overall_percentage,
        "passed": passed,
        "task_scores": {
            "task1": {
                "score": task1_score,
                "max_score": 40,
                "percentage": task1_percentage,
                "feedback": task1_feedback
            },
            "task2": {
                "score": task2_score,
                "max_score": 30,
                "percentage": task2_percentage,
                "feedback": task2_feedback
            },
            "task3": {
                "score": task3_score,
                "max_score": 30,
                "percentage": task3_percentage,
                "feedback": task3_feedback
            }
        },
        "submission": submission,
        "answer_key": answer_key
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    print(f"Result: {'PASSED' if passed else 'FAILED'}")

if __name__ == "__main__":
    main()