#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any, Union

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Work Schedule Creation."""
    results = {
        "score": 0,
        "max_score": 40,
        "details": {}
    }
    
    # Check schedule conflicts (10 points)
    sub_conflicts = set(submission.get("task1", {}).get("schedule_conflicts", []))
    key_conflicts = set(answer_key.get("task1", {}).get("schedule_conflicts", []))
    
    if sub_conflicts == key_conflicts:
        results["details"]["schedule_conflicts"] = {
            "score": 10,
            "max_score": 10,
            "comment": "Correctly identified schedule conflicts."
        }
    else:
        results["details"]["schedule_conflicts"] = {
            "score": 0,
            "max_score": 10,
            "comment": "Failed to correctly identify schedule conflicts."
        }
    
    # Check coverage score (10 points)
    sub_coverage = submission.get("task1", {}).get("coverage_score", 0)
    key_coverage = answer_key.get("task1", {}).get("coverage_score", 0)
    
    if abs(sub_coverage - key_coverage) <= 0.05:
        results["details"]["coverage_score"] = {
            "score": 10,
            "max_score": 10,
            "comment": f"Coverage score {sub_coverage} is within acceptable range of correct value {key_coverage}."
        }
    else:
        results["details"]["coverage_score"] = {
            "score": 0,
            "max_score": 10,
            "comment": f"Coverage score {sub_coverage} is outside acceptable range of correct value {key_coverage}."
        }
    
    # Check total labor hours (10 points)
    sub_hours = submission.get("task1", {}).get("total_labor_hours", 0)
    key_hours = answer_key.get("task1", {}).get("total_labor_hours", 0)
    
    if abs(sub_hours - key_hours) <= 16:
        results["details"]["total_labor_hours"] = {
            "score": 10,
            "max_score": 10,
            "comment": f"Total labor hours {sub_hours} is within acceptable range of correct value {key_hours}."
        }
    else:
        results["details"]["total_labor_hours"] = {
            "score": 0,
            "max_score": 10,
            "comment": f"Total labor hours {sub_hours} is outside acceptable range of correct value {key_hours}."
        }
    
    # Check schedule data (10 points)
    sub_schedule = submission.get("task1", {}).get("schedule_data", [])
    key_schedule = answer_key.get("task1", {}).get("schedule_data", [])
    
    # Simplified validation - check if at least 80% of assignments are valid
    # In a real implementation, we would check each assignment against employee availability
    valid_assignments = 0
    total_assignments = len(sub_schedule)
    
    if total_assignments > 0:
        # For simplicity, we'll consider an assignment valid if it has all required fields
        required_fields = ["day", "shift", "employee_id", "position"]
        for assignment in sub_schedule:
            if all(field in assignment for field in required_fields):
                valid_assignments += 1
        
        validity_percentage = valid_assignments / total_assignments
        
        if validity_percentage >= 0.8:
            results["details"]["schedule_data"] = {
                "score": 10,
                "max_score": 10,
                "comment": f"{valid_assignments}/{total_assignments} assignments are valid (>= 80%)."
            }
        else:
            score = int(10 * validity_percentage)
            results["details"]["schedule_data"] = {
                "score": score,
                "max_score": 10,
                "comment": f"Only {valid_assignments}/{total_assignments} assignments are valid (< 80%)."
            }
    else:
        results["details"]["schedule_data"] = {
            "score": 0,
            "max_score": 10,
            "comment": "No schedule data provided."
        }
    
    # Calculate total score for Task 1
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Station Assignment Planning."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check station assignments (10 points)
    sub_assignments = submission.get("task2", {}).get("station_assignments", [])
    key_assignments = answer_key.get("task2", {}).get("station_assignments", [])
    
    # Extract premium stations from key
    premium_stations = []
    for station in key_assignments:
        if station.get("station_id", "").startswith("S00") and int(station.get("station_id", "S000")[3:]) <= 10 and int(station.get("station_id", "S000")[3:]) % 2 != 0:
            premium_stations.append(station.get("station_id"))
    
    # Check if premium stations are properly staffed in submission
    premium_staffed = 0
    for station_id in premium_stations:
        for station in sub_assignments:
            if station.get("station_id") == station_id and len(station.get("employee_ids", [])) > 0:
                premium_staffed += 1
                break
    
    premium_percentage = premium_staffed / len(premium_stations) if premium_stations else 0
    
    if premium_percentage >= 0.75:
        results["details"]["station_assignments"] = {
            "score": 10,
            "max_score": 10,
            "comment": f"{premium_staffed}/{len(premium_stations)} premium stations properly staffed (>= 75%)."
        }
    else:
        score = int(10 * premium_percentage)
        results["details"]["station_assignments"] = {
            "score": score,
            "max_score": 10,
            "comment": f"Only {premium_staffed}/{len(premium_stations)} premium stations properly staffed (< 75%)."
        }
    
    # Check coverage percentage (10 points)
    sub_coverage = submission.get("task2", {}).get("coverage_percentage", 0)
    key_coverage = answer_key.get("task2", {}).get("coverage_percentage", 0)
    
    if abs(sub_coverage - key_coverage) <= 0.1:
        results["details"]["coverage_percentage"] = {
            "score": 10,
            "max_score": 10,
            "comment": f"Coverage percentage {sub_coverage} is within acceptable range of correct value {key_coverage}."
        }
    else:
        results["details"]["coverage_percentage"] = {
            "score": 0,
            "max_score": 10,
            "comment": f"Coverage percentage {sub_coverage} is outside acceptable range of correct value {key_coverage}."
        }
    
    # Check high value stations covered (10 points)
    sub_high_value = submission.get("task2", {}).get("high_value_stations_covered", 0)
    key_high_value = answer_key.get("task2", {}).get("high_value_stations_covered", 0)
    
    if abs(sub_high_value - key_high_value) <= 1:
        results["details"]["high_value_stations_covered"] = {
            "score": 10,
            "max_score": 10,
            "comment": f"High value stations covered {sub_high_value} is within acceptable range of correct value {key_high_value}."
        }
    else:
        results["details"]["high_value_stations_covered"] = {
            "score": 0,
            "max_score": 10,
            "comment": f"High value stations covered {sub_high_value} is outside acceptable range of correct value {key_high_value}."
        }
    
    # Calculate total score for Task 2
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Attendance Record Analysis."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check attendance rate (7.5 points)
    sub_rate = submission.get("task3", {}).get("attendance_rate", 0)
    key_rate = answer_key.get("task3", {}).get("attendance_rate", 0)
    
    if abs(sub_rate - key_rate) <= 0.02:
        results["details"]["attendance_rate"] = {
            "score": 7.5,
            "max_score": 7.5,
            "comment": f"Attendance rate {sub_rate} is within acceptable range of correct value {key_rate}."
        }
    else:
        results["details"]["attendance_rate"] = {
            "score": 0,
            "max_score": 7.5,
            "comment": f"Attendance rate {sub_rate} is outside acceptable range of correct value {key_rate}."
        }
    
    # Check most absences (7.5 points)
    sub_absences = set(submission.get("task3", {}).get("most_absences", []))
    key_absences = set(answer_key.get("task3", {}).get("most_absences", []))
    
    common_absences = sub_absences.intersection(key_absences)
    
    if len(common_absences) >= 2:
        results["details"]["most_absences"] = {
            "score": 7.5,
            "max_score": 7.5,
            "comment": f"Correctly identified at least 2 of 3 employees with most absences."
        }
    else:
        score = (len(common_absences) / 2) * 7.5
        results["details"]["most_absences"] = {
            "score": score,
            "max_score": 7.5,
            "comment": f"Only identified {len(common_absences)} of 3 employees with most absences correctly."
        }
    
    # Check understaffed days (7.5 points)
    sub_understaffed = set(submission.get("task3", {}).get("understaffed_days", []))
    key_understaffed = set(answer_key.get("task3", {}).get("understaffed_days", []))
    
    if sub_understaffed == key_understaffed:
        results["details"]["understaffed_days"] = {
            "score": 7.5,
            "max_score": 7.5,
            "comment": "Correctly identified understaffed days."
        }
    else:
        results["details"]["understaffed_days"] = {
            "score": 0,
            "max_score": 7.5,
            "comment": "Failed to correctly identify understaffed days."
        }
    
    # Check attendance trend (7.5 points)
    sub_trend = submission.get("task3", {}).get("attendance_trend", "")
    key_trend = answer_key.get("task3", {}).get("attendance_trend", "")
    
    if sub_trend == key_trend:
        results["details"]["attendance_trend"] = {
            "score": 7.5,
            "max_score": 7.5,
            "comment": f"Correctly identified attendance trend as '{key_trend}'."
        }
    else:
        results["details"]["attendance_trend"] = {
            "score": 0,
            "max_score": 7.5,
            "comment": f"Failed to correctly identify attendance trend. Expected '{key_trend}', got '{sub_trend}'."
        }
    
    # Calculate total score for Task 3
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key)
    }
    
    # Calculate overall score
    total_score = sum(task["score"] for task in results.values())
    max_score = sum(task["max_score"] for task in results.values())
    overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    results["overall_score"] = round(overall_percentage, 2)
    
    # Check if candidate passed
    task1_percentage = (results["task1"]["score"] / results["task1"]["max_score"]) * 100 if results["task1"]["max_score"] > 0 else 0
    task2_percentage = (results["task2"]["score"] / results["task2"]["max_score"]) * 100 if results["task2"]["max_score"] > 0 else 0
    task3_percentage = (results["task3"]["score"] / results["task3"]["max_score"]) * 100 if results["task3"]["max_score"] > 0 else 0
    
    passed = overall_percentage >= 70 and task1_percentage >= 60 and task2_percentage >= 60 and task3_percentage >= 60
    
    results["passed"] = passed
    results["pass_criteria"] = {
        "overall_minimum": "70%",
        "task_minimum": "60%",
        "task1_percentage": round(task1_percentage, 2),
        "task2_percentage": round(task2_percentage, 2),
        "task3_percentage": round(task3_percentage, 2)
    }
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()