#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_critical_path(submission_path: List[str], answer_path: List[str]) -> Tuple[bool, float, str]:
    """Evaluate the critical path submission."""
    # Check if paths are identical
    if submission_path == answer_path:
        return True, 1.0, "Critical path is correct"
    
    # Check if submission is an alternative valid critical path
    alt_path = ["A", "B", "C", "D", "I", "J", "L", "M"]
    if submission_path == alt_path:
        return True, 1.0, "Critical path is an acceptable alternative"
    
    # Calculate overlap percentage
    common_elements = set(submission_path).intersection(set(answer_path))
    overlap_percentage = len(common_elements) / len(answer_path)
    
    if overlap_percentage >= 0.75:  # At least 6 of 8 correct
        return True, overlap_percentage, f"Critical path has {len(common_elements)}/{len(answer_path)} correct elements"
    else:
        return False, overlap_percentage, f"Critical path has insufficient overlap ({len(common_elements)}/{len(answer_path)})"

def evaluate_slack_values(submission_slack: Dict[str, int], answer_slack: Dict[str, int]) -> Tuple[bool, float, str]:
    """Evaluate the slack values submission."""
    correct_count = sum(1 for task, value in submission_slack.items() 
                       if task in answer_slack and value == answer_slack[task])
    
    accuracy = correct_count / len(answer_slack)
    passed = correct_count >= 10  # At least 10 out of 13 correct
    
    return passed, accuracy, f"{correct_count}/{len(answer_slack)} slack values correct"

def evaluate_project_duration(submission_duration: int, answer_duration: int, 
                             tolerance: int = 2) -> Tuple[bool, float, str]:
    """Evaluate the project duration submission."""
    difference = abs(submission_duration - answer_duration)
    
    if difference <= tolerance:
        accuracy = 1.0 - (difference / (tolerance * 2))
        return True, accuracy, f"Project duration within tolerance (±{difference} days)"
    elif difference <= 10:  # Not an automatic failure
        accuracy = 0.5 - (difference / 20)  # Linear decrease from 0.5 to 0
        return False, max(0, accuracy), f"Project duration off by {difference} days"
    else:
        return False, 0.0, f"Project duration off by more than 10 days ({difference})"

def evaluate_crash_plan(submission_plan: Dict[str, int], answer_plan: Dict[str, int]) -> Tuple[bool, float, str]:
    """Evaluate the optimal crash plan submission."""
    # Count correctly crashed activities
    correct_activities = 0
    for task, days in submission_plan.items():
        if task in answer_plan:
            if days == answer_plan[task]:
                correct_activities += 1
            elif days > 0:  # At least they crashed the right activity
                correct_activities += 0.5
    
    # Calculate accuracy
    max_correct = len(answer_plan)
    accuracy = correct_activities / max_correct
    
    # Check if at least 4 of 5 correct activities were crashed
    passed = correct_activities >= 4
    
    return passed, accuracy, f"{correct_activities}/{max_correct} crash activities correct"

def evaluate_crash_cost(submission_cost: int, answer_cost: int, 
                       tolerance: int = 3000) -> Tuple[bool, float, str]:
    """Evaluate the crash cost submission."""
    difference = abs(submission_cost - answer_cost)
    
    if difference <= tolerance:
        accuracy = 1.0 - (difference / (tolerance * 2))
        return True, accuracy, f"Crash cost within tolerance (±${difference})"
    else:
        # Linear decrease in score as difference increases
        accuracy = max(0, 0.5 - (difference - tolerance) / (tolerance * 4))
        return False, accuracy, f"Crash cost off by ${difference}"

def evaluate_resource_schedule(submission_schedule: Dict[str, int], 
                              answer_schedule: Dict[str, int]) -> Tuple[bool, float, str]:
    """Evaluate the resource-leveled schedule submission."""
    # Count reasonable start times (within ±2 days of answer or maintaining precedence)
    reasonable_count = 0
    for task, start_day in submission_schedule.items():
        if task in answer_schedule:
            if abs(start_day - answer_schedule[task]) <= 2:
                reasonable_count += 1
    
    accuracy = reasonable_count / len(answer_schedule)
    passed = reasonable_count >= 10  # At least 10 of 13 start times reasonable
    
    return passed, accuracy, f"{reasonable_count}/{len(answer_schedule)} reasonable start times"

def evaluate_max_resource_usage(submission_usage: int, answer_usage: int) -> Tuple[bool, float, str]:
    """Evaluate the maximum resource usage submission."""
    if submission_usage <= answer_usage:
        # Perfect if equal to optimal, good if less than 14
        return True, 1.0, f"Optimal resource usage ({submission_usage} ≤ {answer_usage})"
    elif submission_usage <= 14:
        # Acceptable if ≤ 14
        accuracy = 1.0 - ((submission_usage - answer_usage) / 4)
        return True, accuracy, f"Acceptable resource usage ({submission_usage} ≤ 14)"
    else:
        # Poor if > 14
        accuracy = max(0, 0.5 - (submission_usage - 14) / 8)
        return False, accuracy, f"Suboptimal resource usage ({submission_usage} > 14)"

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0.0,
        "passed": False,
        "task1": {
            "passed": False,
            "score": 0.0,
            "details": {}
        },
        "task2": {
            "passed": False,
            "score": 0.0,
            "details": {}
        },
        "task3": {
            "passed": False,
            "score": 0.0,
            "details": {}
        }
    }
    
    # Task 1 evaluation
    task1_results = []
    
    # Critical path
    critical_path_passed, critical_path_score, critical_path_msg = evaluate_critical_path(
        submission["task1"]["critical_path"], 
        answer_key["task1"]["critical_path"]
    )
    task1_results.append((critical_path_passed, critical_path_score, "critical_path", critical_path_msg))
    
    # Project duration
    duration_passed, duration_score, duration_msg = evaluate_project_duration(
        submission["task1"]["project_duration"], 
        answer_key["task1"]["project_duration"]
    )
    task1_results.append((duration_passed, duration_score, "project_duration", duration_msg))
    
    # Slack values
    slack_passed, slack_score, slack_msg = evaluate_slack_values(
        submission["task1"]["slack_values"], 
        answer_key["task1"]["slack_values"]
    )
    task1_results.append((slack_passed, slack_score, "slack_values", slack_msg))
    
    # Calculate Task 1 overall score and pass status
    task1_score = sum(score for _, score, _, _ in task1_results) / len(task1_results)
    task1_passed = (critical_path_passed and duration_passed and slack_passed)
    
    results["task1"]["passed"] = task1_passed
    results["task1"]["score"] = task1_score
    results["task1"]["details"] = {key: {"passed": passed, "score": score, "message": msg} 
                                  for passed, score, key, msg in task1_results}
    
    # Task 2 evaluation
    task2_results = []
    
    # Optimal crash plan
    crash_plan_passed, crash_plan_score, crash_plan_msg = evaluate_crash_plan(
        submission["task2"]["optimal_crash_plan"], 
        answer_key["task2"]["optimal_crash_plan"]
    )
    task2_results.append((crash_plan_passed, crash_plan_score, "optimal_crash_plan", crash_plan_msg))
    
    # Crashed duration
    crashed_duration_passed, crashed_duration_score, crashed_duration_msg = evaluate_project_duration(
        submission["task2"]["crashed_duration"], 
        answer_key["task2"]["crashed_duration"]
    )
    task2_results.append((crashed_duration_passed, crashed_duration_score, "crashed_duration", crashed_duration_msg))
    
    # Total crash cost
    crash_cost_passed, crash_cost_score, crash_cost_msg = evaluate_crash_cost(
        submission["task2"]["total_crash_cost"], 
        answer_key["task2"]["total_crash_cost"]
    )
    task2_results.append((crash_cost_passed, crash_cost_score, "total_crash_cost", crash_cost_msg))
    
    # New critical path
    new_path_passed, new_path_score, new_path_msg = evaluate_critical_path(
        submission["task2"]["new_critical_path"], 
        answer_key["task2"]["new_critical_path"]
    )
    task2_results.append((new_path_passed, new_path_score, "new_critical_path", new_path_msg))
    
    # Calculate Task 2 overall score and pass status
    task2_score = sum(score for _, score, _, _ in task2_results) / len(task2_results)
    task2_passed = (crash_plan_passed and crashed_duration_passed and 
                   crash_cost_passed and new_path_passed)
    
    results["task2"]["passed"] = task2_passed
    results["task2"]["score"] = task2_score
    results["task2"]["details"] = {key: {"passed": passed, "score": score, "message": msg} 
                                  for passed, score, key, msg in task2_results}
    
    # Task 3 evaluation
    task3_results = []
    
    # Resource-leveled schedule
    schedule_passed, schedule_score, schedule_msg = evaluate_resource_schedule(
        submission["task3"]["resource_leveled_schedule"], 
        answer_key["task3"]["resource_leveled_schedule"]
    )
    task3_results.append((schedule_passed, schedule_score, "resource_leveled_schedule", schedule_msg))
    
    # Project duration after leveling
    leveled_duration_passed, leveled_duration_score, leveled_duration_msg = evaluate_project_duration(
        submission["task3"]["project_duration_after_leveling"], 
        answer_key["task3"]["project_duration_after_leveling"],
        tolerance=2
    )
    task3_results.append((leveled_duration_passed, leveled_duration_score, "project_duration_after_leveling", leveled_duration_msg))
    
    # Max resource usage
    resource_usage_passed, resource_usage_score, resource_usage_msg = evaluate_max_resource_usage(
        submission["task3"]["max_resource_usage"], 
        answer_key["task3"]["max_resource_usage"]
    )
    task3_results.append((resource_usage_passed, resource_usage_score, "max_resource_usage", resource_usage_msg))
    
    # Calculate Task 3 overall score and pass status
    task3_score = sum(score for _, score, _, _ in task3_results) / len(task3_results)
    task3_passed = (schedule_passed and leveled_duration_passed and resource_usage_passed)
    
    results["task3"]["passed"] = task3_passed
    results["task3"]["score"] = task3_score
    results["task3"]["details"] = {key: {"passed": passed, "score": score, "message": msg} 
                                  for passed, score, key, msg in task3_results}
    
    # Calculate overall score and pass status
    overall_score = (task1_score + task2_score + task3_score) / 3
    results["overall_score"] = round(overall_score * 100, 2)  # Convert to percentage
    
    # Pass if at least 2 of 3 tasks are passed
    tasks_passed = sum([task1_passed, task2_passed, task3_passed])
    results["passed"] = tasks_passed >= 2
    results["tasks_passed"] = f"{tasks_passed}/3"
    
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
    print(f"Passed: {results['passed']} ({results['tasks_passed']} tasks passed)")

if __name__ == "__main__":
    main()