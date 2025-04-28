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
    """Evaluate Task 1: Vendor Performance Analysis."""
    results = {
        "vendor_rankings": {
            "correct": False,
            "score": 0,
            "expected": answer_key["vendor_rankings"],
            "submitted": submission.get("vendor_rankings", [])
        },
        "lowest_performing_vendor": {
            "correct": False,
            "score": 0,
            "expected": answer_key["lowest_performing_vendor"],
            "submitted": submission.get("lowest_performing_vendor", "")
        },
        "highest_performing_vendor": {
            "correct": False,
            "score": 0,
            "expected": answer_key["highest_performing_vendor"],
            "submitted": submission.get("highest_performing_vendor", "")
        },
        "average_on_time_percentage": {
            "correct": False,
            "score": 0,
            "expected": answer_key["average_on_time_percentage"],
            "submitted": submission.get("average_on_time_percentage", 0)
        },
        "total_late_deliveries": {
            "correct": False,
            "score": 0,
            "expected": answer_key["total_late_deliveries"],
            "submitted": submission.get("total_late_deliveries", 0)
        }
    }
    
    # Check vendor rankings
    if results["vendor_rankings"]["submitted"] == results["vendor_rankings"]["expected"]:
        results["vendor_rankings"]["correct"] = True
        results["vendor_rankings"]["score"] = 1
    else:
        # Partial credit if at least 3 vendors are in correct position
        correct_positions = sum(1 for i, v in enumerate(results["vendor_rankings"]["submitted"]) 
                               if i < len(results["vendor_rankings"]["expected"]) and v == results["vendor_rankings"]["expected"][i])
        if correct_positions >= 3:
            results["vendor_rankings"]["score"] = 0.5
    
    # Check lowest performing vendor
    if results["lowest_performing_vendor"]["submitted"] == results["lowest_performing_vendor"]["expected"]:
        results["lowest_performing_vendor"]["correct"] = True
        results["lowest_performing_vendor"]["score"] = 1
    
    # Check highest performing vendor
    if results["highest_performing_vendor"]["submitted"] == results["highest_performing_vendor"]["expected"]:
        results["highest_performing_vendor"]["correct"] = True
        results["highest_performing_vendor"]["score"] = 1
    
    # Check average on-time percentage (allow ±0.2% variance)
    submitted_avg = results["average_on_time_percentage"]["submitted"]
    expected_avg = results["average_on_time_percentage"]["expected"]
    if abs(submitted_avg - expected_avg) <= 0.2:
        results["average_on_time_percentage"]["correct"] = True
        results["average_on_time_percentage"]["score"] = 1
    
    # Check total late deliveries
    if results["total_late_deliveries"]["submitted"] == results["total_late_deliveries"]["expected"]:
        results["total_late_deliveries"]["correct"] = True
        results["total_late_deliveries"]["score"] = 1
    
    # Calculate total score for Task 1
    total_score = sum(item["score"] for item in results.values())
    correct_count = sum(1 for item in results.values() if item["correct"])
    
    return {
        "details": results,
        "score": total_score,
        "max_score": 5,
        "correct_count": correct_count,
        "passed_critical": (results["highest_performing_vendor"]["correct"] and 
                           results["lowest_performing_vendor"]["correct"])
    }

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Service Quality Evaluation."""
    results = {
        "negative_feedback_count": {
            "correct": False,
            "score": 0,
            "expected": answer_key["negative_feedback_count"],
            "submitted": submission.get("negative_feedback_count", 0)
        },
        "most_mentioned_vendor": {
            "correct": False,
            "score": 0,
            "expected": answer_key["most_mentioned_vendor"],
            "submitted": submission.get("most_mentioned_vendor", "")
        },
        "service_issue_frequency": {
            "correct": False,
            "score": 0,
            "expected": answer_key["service_issue_frequency"],
            "submitted": submission.get("service_issue_frequency", {})
        },
        "highest_rated_vendor": {
            "correct": False,
            "score": 0,
            "expected": answer_key["highest_rated_vendor"],
            "submitted": submission.get("highest_rated_vendor", "")
        }
    }
    
    # Check negative feedback count
    if results["negative_feedback_count"]["submitted"] == results["negative_feedback_count"]["expected"]:
        results["negative_feedback_count"]["correct"] = True
        results["negative_feedback_count"]["score"] = 1
    
    # Check most mentioned vendor
    if results["most_mentioned_vendor"]["submitted"] == results["most_mentioned_vendor"]["expected"]:
        results["most_mentioned_vendor"]["correct"] = True
        results["most_mentioned_vendor"]["score"] = 1
    
    # Check service issue frequency
    expected_freq = results["service_issue_frequency"]["expected"]
    submitted_freq = results["service_issue_frequency"]["submitted"]
    
    if submitted_freq == expected_freq:
        results["service_issue_frequency"]["correct"] = True
        results["service_issue_frequency"]["score"] = 1
    else:
        # Partial credit if at least 3 categories are correct
        correct_categories = 0
        for category in expected_freq:
            if category in submitted_freq and submitted_freq[category] == expected_freq[category]:
                correct_categories += 1
        
        if correct_categories >= 3:
            results["service_issue_frequency"]["score"] = 0.5
    
    # Check highest rated vendor
    if results["highest_rated_vendor"]["submitted"] == results["highest_rated_vendor"]["expected"]:
        results["highest_rated_vendor"]["correct"] = True
        results["highest_rated_vendor"]["score"] = 1
    
    # Calculate total score for Task 2
    total_score = sum(item["score"] for item in results.values())
    correct_count = sum(1 for item in results.values() if item["correct"])
    
    return {
        "details": results,
        "score": total_score,
        "max_score": 4,
        "correct_count": correct_count,
        "passed_critical": results["most_mentioned_vendor"]["correct"]
    }

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Cost-Efficiency Assessment."""
    results = {
        "recommended_vendor": {
            "correct": False,
            "score": 0,
            "expected": answer_key["recommended_vendor"],
            "submitted": submission.get("recommended_vendor", "")
        },
        "annual_cost_difference": {
            "correct": False,
            "score": 0,
            "expected": answer_key["annual_cost_difference"],
            "submitted": submission.get("annual_cost_difference", 0)
        },
        "quality_score_leader": {
            "correct": False,
            "score": 0,
            "expected": answer_key["quality_score_leader"],
            "submitted": submission.get("quality_score_leader", "")
        },
        "delivery_time_leader": {
            "correct": False,
            "score": 0,
            "expected": answer_key["delivery_time_leader"],
            "submitted": submission.get("delivery_time_leader", "")
        }
    }
    
    # Check recommended vendor
    if results["recommended_vendor"]["submitted"] == results["recommended_vendor"]["expected"]:
        results["recommended_vendor"]["correct"] = True
        results["recommended_vendor"]["score"] = 1
    
    # Check annual cost difference
    if results["annual_cost_difference"]["submitted"] == results["annual_cost_difference"]["expected"]:
        results["annual_cost_difference"]["correct"] = True
        results["annual_cost_difference"]["score"] = 1
    
    # Check quality score leader
    if results["quality_score_leader"]["submitted"] == results["quality_score_leader"]["expected"]:
        results["quality_score_leader"]["correct"] = True
        results["quality_score_leader"]["score"] = 1
    
    # Check delivery time leader
    if results["delivery_time_leader"]["submitted"] == results["delivery_time_leader"]["expected"]:
        results["delivery_time_leader"]["correct"] = True
        results["delivery_time_leader"]["score"] = 1
    
    # Calculate total score for Task 3
    total_score = sum(item["score"] for item in results.values())
    correct_count = sum(1 for item in results.values() if item["correct"])
    
    return {
        "details": results,
        "score": total_score,
        "max_score": 4,
        "correct_count": correct_count,
        "passed_critical": results["recommended_vendor"]["correct"]
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    # Extract task-specific data
    submission_task1 = submission.get("task1", {})
    submission_task2 = submission.get("task2", {})
    submission_task3 = submission.get("task3", {})
    
    answer_key_task1 = answer_key.get("task1", {})
    answer_key_task2 = answer_key.get("task2", {})
    answer_key_task3 = answer_key.get("task3", {})
    
    # Evaluate each task
    task1_results = evaluate_task1(submission_task1, answer_key_task1)
    task2_results = evaluate_task2(submission_task2, answer_key_task2)
    task3_results = evaluate_task3(submission_task3, answer_key_task3)
    
    # Calculate overall results
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Check passing criteria
    passed_task1 = task1_results["correct_count"] >= 3
    passed_task2 = task2_results["correct_count"] >= 3
    passed_task3 = task3_results["correct_count"] >= 3
    passed_critical = (task1_results["passed_critical"] and 
                      task2_results["passed_critical"] and 
                      task3_results["passed_critical"])
    
    passed_exam = (total_score >= 10 and 
                  passed_task1 and 
                  passed_task2 and 
                  passed_task3 and 
                  passed_critical)
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1_results": task1_results,
        "task2_results": task2_results,
        "task3_results": task3_results,
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": round(overall_percentage, 2),
        "passed_exam": passed_exam,
        "passed_criteria": {
            "minimum_score": total_score >= 10,
            "task1_minimum": passed_task1,
            "task2_minimum": passed_task2,
            "task3_minimum": passed_task3,
            "critical_items": passed_critical
        }
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed exam: {results['passed_exam']}")

if __name__ == "__main__":
    main()