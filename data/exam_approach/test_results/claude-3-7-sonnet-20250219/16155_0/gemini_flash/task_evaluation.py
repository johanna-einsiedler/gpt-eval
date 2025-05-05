#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Customer Feedback Analysis (25 points)"""
    results = {"points": 0, "max_points": 25, "details": {}}
    
    # Check top pain points (5 points)
    sub_points = set(submission.get("top_pain_points", []))
    key_points = set(answer_key.get("top_pain_points", []))
    correct = sub_points == key_points
    points = 5 if correct else 0
    results["details"]["top_pain_points"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": submission.get("top_pain_points", []),
        "expected": answer_key.get("top_pain_points", [])
    }
    results["points"] += points
    
    # Check pain point percentages (5 points)
    sub_percentages = submission.get("pain_point_percentages", [])
    key_percentages = answer_key.get("pain_point_percentages", [])
    
    # Allow for ±2% tolerance
    correct = True
    if len(sub_percentages) == len(key_percentages):
        for i in range(len(sub_percentages)):
            if abs(sub_percentages[i] - key_percentages[i]) > 2:
                correct = False
                break
    else:
        correct = False
    
    points = 5 if correct else 0
    results["details"]["pain_point_percentages"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_percentages,
        "expected": key_percentages,
        "note": "±2% tolerance allowed"
    }
    results["points"] += points
    
    # Check highest dissatisfaction department (5 points)
    sub_dept = submission.get("highest_dissatisfaction_department", "")
    key_dept = answer_key.get("highest_dissatisfaction_department", "")
    correct = sub_dept == key_dept
    points = 5 if correct else 0
    results["details"]["highest_dissatisfaction_department"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_dept,
        "expected": key_dept
    }
    results["points"] += points
    
    # Check average satisfaction rating (5 points)
    sub_rating = submission.get("average_satisfaction_rating", 0)
    key_rating = answer_key.get("average_satisfaction_rating", 0)
    # Allow for ±0.05 tolerance
    correct = abs(sub_rating - key_rating) <= 0.05
    points = 5 if correct else 0
    results["details"]["average_satisfaction_rating"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_rating,
        "expected": key_rating,
        "note": "±0.05 tolerance allowed"
    }
    results["points"] += points
    
    # Check common feature request (5 points)
    sub_feature = submission.get("common_feature_request", "")
    key_feature = answer_key.get("common_feature_request", "")
    correct = sub_feature == key_feature
    points = 5 if correct else 0
    results["details"]["common_feature_request"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_feature,
        "expected": key_feature
    }
    results["points"] += points
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Research Method Selection (20 points)"""
    results = {"points": 0, "max_points": 20, "details": {}}
    
    scenarios = ["scenario1", "scenario2", "scenario3", "scenario4"]
    
    for scenario in scenarios:
        sub_answer = submission.get(scenario, "")
        key_answer = answer_key.get(scenario, "")
        correct = sub_answer == key_answer
        points = 5 if correct else 0
        results["details"][scenario] = {
            "correct": correct,
            "points": points,
            "max_points": 5,
            "submitted": sub_answer,
            "expected": key_answer
        }
        results["points"] += points
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Customer Requirements Prioritization (25 points)"""
    results = {"points": 0, "max_points": 25, "details": {}}
    
    # Check top 5 features (5 points)
    sub_features = submission.get("top5_features", [])
    key_features = answer_key.get("top5_features", [])
    correct = sub_features == key_features
    points = 5 if correct else 0
    results["details"]["top5_features"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_features,
        "expected": key_features
    }
    results["points"] += points
    
    # Check high impact low frequency feature (5 points)
    sub_feature = submission.get("high_impact_low_frequency", "")
    # Accept either "System monitoring dashboard" or "Financial dashboard"
    correct = sub_feature in ["System monitoring dashboard", "Financial dashboard"]
    points = 5 if correct else 0
    results["details"]["high_impact_low_frequency"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_feature,
        "expected": answer_key.get("high_impact_low_frequency", ""),
        "note": "Either 'System monitoring dashboard' or 'Financial dashboard' is accepted"
    }
    results["points"] += points
    
    # Check average urgency (5 points)
    sub_urgency = submission.get("average_urgency", 0)
    key_urgency = answer_key.get("average_urgency", 0)
    # Allow for ±0.05 tolerance
    correct = abs(sub_urgency - key_urgency) <= 0.05
    points = 5 if correct else 0
    results["details"]["average_urgency"] = {
        "correct": correct,
        "points": points,
        "max_points": 5,
        "submitted": sub_urgency,
        "expected": key_urgency,
        "note": "±0.05 tolerance allowed"
    }
    results["points"] += points
    
    # Check highest priority department (10 points)
    sub_dept = submission.get("highest_priority_department", "")
    key_dept = answer_key.get("highest_priority_department", "")
    correct = sub_dept == key_dept
    points = 10 if correct else 0
    results["details"]["highest_priority_department"] = {
        "correct": correct,
        "points": points,
        "max_points": 10,
        "submitted": sub_dept,
        "expected": key_dept
    }
    results["points"] += points
    
    return results

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Communication Planning (30 points)"""
    results = {"points": 0, "max_points": 30, "details": {}}
    
    # Check key stakeholders (6 points)
    sub_stakeholders = set(submission.get("key_stakeholders", []))
    # The first two stakeholders must be correct
    required_stakeholders = ["Michael Chen", "Sarah Johnson"]
    # The third can be either Jennifer Williams or Robert Kim
    optional_stakeholders = ["Jennifer Williams", "Robert Kim"]
    
    # Check if submission has exactly 3 stakeholders
    if len(sub_stakeholders) != 3:
        correct = False
    else:
        # Check if the first two required stakeholders are present
        if all(stakeholder in sub_stakeholders for stakeholder in required_stakeholders):
            # Check if the third stakeholder is one of the optional ones
            remaining = sub_stakeholders - set(required_stakeholders)
            correct = len(remaining) == 1 and list(remaining)[0] in optional_stakeholders
        else:
            correct = False
    
    points = 6 if correct else 0
    results["details"]["key_stakeholders"] = {
        "correct": correct,
        "points": points,
        "max_points": 6,
        "submitted": list(sub_stakeholders),
        "expected": answer_key.get("key_stakeholders", []),
        "note": "Must include Michael Chen, Sarah Johnson, and either Jennifer Williams or Robert Kim"
    }
    results["points"] += points
    
    # Check executive communication method (6 points)
    sub_method = submission.get("executive_communication_method", "")
    key_method = answer_key.get("executive_communication_method", "")
    correct = sub_method == key_method
    points = 6 if correct else 0
    results["details"]["executive_communication_method"] = {
        "correct": correct,
        "points": points,
        "max_points": 6,
        "submitted": sub_method,
        "expected": key_method
    }
    results["points"] += points
    
    # Check steering committee frequency (6 points)
    sub_freq = submission.get("steering_committee_frequency", "")
    key_freq = answer_key.get("steering_committee_frequency", "")
    correct = sub_freq == key_freq
    points = 6 if correct else 0
    results["details"]["steering_committee_frequency"] = {
        "correct": correct,
        "points": points,
        "max_points": 6,
        "submitted": sub_freq,
        "expected": key_freq
    }
    results["points"] += points
    
    # Check top metrics (6 points)
    # For top metrics, we'll be more flexible and accept reasonable alternatives
    sub_metrics = set(submission.get("top_metrics", []))
    key_metrics = set(answer_key.get("top_metrics", []))
    
    # Define acceptable alternative metrics
    acceptable_alternatives = {
        "User adoption rate", 
        "Number of reported issues", 
        "Response time improvements",
        "User satisfaction trends",
        "Bug resolution rate",
        "Feature completion percentage",
        "System performance metrics",
        "Training completion rates"
    }
    
    # Count how many of the submitted metrics are either in the key or in acceptable alternatives
    correct_count = 0
    for metric in sub_metrics:
        if metric in key_metrics or metric in acceptable_alternatives:
            correct_count += 1
    
    # Calculate points based on how many correct metrics were provided
    if len(sub_metrics) == 3:  # They provided exactly 3 metrics
        if correct_count == 3:
            points = 6  # All 3 are correct
        elif correct_count == 2:
            points = 4  # 2 out of 3 are correct
        elif correct_count == 1:
            points = 2  # 1 out of 3 is correct
        else:
            points = 0  # None are correct
    else:
        points = 0  # Did not provide exactly 3 metrics
    
    results["details"]["top_metrics"] = {
        "correct": correct_count == 3 and len(sub_metrics) == 3,
        "points": points,
        "max_points": 6,
        "submitted": list(sub_metrics),
        "expected": list(key_metrics),
        "note": "Reasonable alternatives are accepted"
    }
    results["points"] += points
    
    # Check development team format (6 points)
    sub_format = submission.get("development_team_format", "")
    key_format = answer_key.get("development_team_format", "")
    correct = sub_format == key_format
    points = 6 if correct else 0
    results["details"]["development_team_format"] = {
        "correct": correct,
        "points": points,
        "max_points": 6,
        "submitted": sub_format,
        "expected": key_format
    }
    results["points"] += points
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {})),
        "task2": evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {})),
        "task3": evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {})),
        "task4": evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    }
    
    # Calculate total points and max points
    total_points = sum(results[task]["points"] for task in ["task1", "task2", "task3", "task4"])
    max_points = sum(results[task]["max_points"] for task in ["task1", "task2", "task3", "task4"])
    
    # Calculate overall score as a percentage
    overall_score = (total_points / max_points) * 100 if max_points > 0 else 0
    
    # Add summary to results
    results["summary"] = {
        "total_points": total_points,
        "max_points": max_points,
        "overall_score": round(overall_score, 2),
        "passed": overall_score >= 70  # Passing threshold is 70%
    }
    
    return results

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
    
    # Add overall_score as a separate variable at the top level
    results["overall_score"] = results["summary"]["overall_score"]
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['summary']['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()