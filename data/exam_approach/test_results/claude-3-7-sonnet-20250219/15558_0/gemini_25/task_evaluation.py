#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Client Records Management."""
    results = {
        "client_summary": {
            "bmi_over_25": {"score": 0, "max_points": 5, "details": ""},
            "elevated_heart_rate": {"score": 0, "max_points": 5, "details": ""},
            "low_attendance": {"score": 0, "max_points": 5, "details": ""}
        },
        "client_flags": {
            "consecutive_misses": {"score": 0, "max_points": 7, "details": ""},
            "reassessment_due": {"score": 0, "max_points": 8, "details": ""}
        },
        "total_score": 0,
        "max_points": 30
    }
    
    # Client Summary - BMI over 25
    sub_bmi = set(submission["task1"]["client_summary"]["bmi_over_25"])
    key_bmi = set(answer_key["task1"]["client_summary"]["bmi_over_25"])
    bmi_score = 5 - min(5, len(sub_bmi.symmetric_difference(key_bmi)))
    results["client_summary"]["bmi_over_25"]["score"] = bmi_score
    results["client_summary"]["bmi_over_25"]["details"] = f"Identified {len(sub_bmi.intersection(key_bmi))}/{len(key_bmi)} correct clients"
    
    # Client Summary - Elevated Heart Rate
    sub_hr = set(submission["task1"]["client_summary"]["elevated_heart_rate"])
    key_hr = set(answer_key["task1"]["client_summary"]["elevated_heart_rate"])
    hr_score = 5 if sub_hr == key_hr else 0
    results["client_summary"]["elevated_heart_rate"]["score"] = hr_score
    results["client_summary"]["elevated_heart_rate"]["details"] = "Correct" if hr_score == 5 else "Incorrect"
    
    # Client Summary - Low Attendance
    sub_att = set(submission["task1"]["client_summary"]["low_attendance"])
    key_att = set(answer_key["task1"]["client_summary"]["low_attendance"])
    att_score = 5 - min(5, len(sub_att.symmetric_difference(key_att)))
    results["client_summary"]["low_attendance"]["score"] = att_score
    results["client_summary"]["low_attendance"]["details"] = f"Identified {len(sub_att.intersection(key_att))}/{len(key_att)} correct clients"
    
    # Client Flags - Consecutive Misses
    sub_miss = set(submission["task1"]["client_flags"]["consecutive_misses"])
    key_miss = set(answer_key["task1"]["client_flags"]["consecutive_misses"])
    miss_diff = len(sub_miss.symmetric_difference(key_miss))
    miss_score = max(0, 7 - (2 * miss_diff))
    results["client_flags"]["consecutive_misses"]["score"] = miss_score
    results["client_flags"]["consecutive_misses"]["details"] = f"Identified {len(sub_miss.intersection(key_miss))}/{len(key_miss)} correct clients"
    
    # Client Flags - Reassessment Due
    sub_due = set(submission["task1"]["client_flags"]["reassessment_due"])
    key_due = set(answer_key["task1"]["client_flags"]["reassessment_due"])
    due_diff = len(sub_due.symmetric_difference(key_due))
    due_score = max(0, 8 - (1.5 * due_diff))
    results["client_flags"]["reassessment_due"]["score"] = due_score
    results["client_flags"]["reassessment_due"]["details"] = f"Identified {len(sub_due.intersection(key_due))}/{len(key_due)} correct clients"
    
    # Calculate total score for Task 1
    results["total_score"] = (
        bmi_score + hr_score + att_score + miss_score + due_score
    )
    
    return results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Program Schedule Management."""
    results = {
        "resolved_conflicts": {"score": 0, "max_points": 10, "details": ""},
        "program_hours": {"score": 0, "max_points": 8, "details": ""},
        "utilization": {"score": 0, "max_points": 9, "details": ""},
        "instructor_load": {"score": 0, "max_points": 8, "details": ""},
        "total_score": 0,
        "max_points": 35
    }
    
    # Resolved Conflicts (2 points per correct resolution)
    conflicts = ["monday_0930", "tuesday_1200", "wednesday_1430", "thursday_1045", "friday_0930"]
    correct_conflicts = 0
    
    for conflict in conflicts:
        sub_val = submission["task2"]["resolved_conflicts"][conflict]
        # For this task, we accept any valid instructor assignment
        # The answer key provides one possible solution
        if sub_val in ["John", "Maria", "Sarah"] and sub_val != "":
            correct_conflicts += 1
    
    conflict_score = correct_conflicts * 2
    results["resolved_conflicts"]["score"] = conflict_score
    results["resolved_conflicts"]["details"] = f"Correctly resolved {correct_conflicts}/5 conflicts"
    
    # Program Hours (2 points per correct program)
    programs = ["cardio", "strength", "flexibility", "weight_management"]
    correct_programs = 0
    
    for program in programs:
        sub_val = submission["task2"]["program_hours"][program]
        key_val = answer_key["task2"]["program_hours"][program]
        if sub_val == key_val:
            correct_programs += 1
    
    program_score = correct_programs * 2
    results["program_hours"]["score"] = program_score
    results["program_hours"]["details"] = f"Correctly calculated {correct_programs}/4 program hours"
    
    # Utilization (3 points per correct room)
    rooms = ["room_a", "room_b", "room_c"]
    correct_rooms = 0
    
    for room in rooms:
        sub_val = submission["task2"]["utilization"][room]
        key_val = answer_key["task2"]["utilization"][room]
        # Allow for small rounding differences (±0.1)
        if abs(sub_val - key_val) <= 0.1:
            correct_rooms += 1
    
    util_score = correct_rooms * 3
    results["utilization"]["score"] = util_score
    results["utilization"]["details"] = f"Correctly calculated {correct_rooms}/3 room utilizations"
    
    # Instructor Load (all or nothing - 8 points)
    instructors = ["maria", "john", "sarah"]
    instructor_correct = True
    
    # Check if loads are balanced (all instructors have same number of classes)
    sub_loads = [submission["task2"]["instructor_load"][i] for i in instructors]
    if len(set(sub_loads)) != 1:
        instructor_correct = False
    
    # Check if total matches expected (75 total classes)
    if sum(sub_loads) != 75:
        instructor_correct = False
    
    instructor_score = 8 if instructor_correct else 0
    results["instructor_load"]["score"] = instructor_score
    results["instructor_load"]["details"] = "Correct balanced load" if instructor_correct else "Incorrect or unbalanced load"
    
    # Calculate total score for Task 2
    results["total_score"] = (
        conflict_score + program_score + util_score + instructor_score
    )
    
    return results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Program Participation Reporting."""
    results = {
        "unique_participants": {"score": 0, "max_points": 8, "details": ""},
        "day_attendance_rate": {"score": 0, "max_points": 10, "details": ""},
        "peak_times": {"score": 0, "max_points": 7, "details": ""},
        "declining_attendance": {"score": 0, "max_points": 5, "details": ""},
        "attendance_satisfaction_correlation": {"score": 0, "max_points": 5, "details": ""},
        "total_score": 0,
        "max_points": 35
    }
    
    # Unique Participants (2 points per correct program)
    programs = ["cardio", "strength", "flexibility", "weight_management"]
    correct_participants = 0
    
    for program in programs:
        sub_val = submission["task3"]["participation"]["unique_participants"][program]
        key_val = answer_key["task3"]["participation"]["unique_participants"][program]
        if sub_val == key_val:
            correct_participants += 1
    
    participants_score = correct_participants * 2
    results["unique_participants"]["score"] = participants_score
    results["unique_participants"]["details"] = f"Correctly calculated {correct_participants}/4 program participants"
    
    # Day Attendance Rate (2 points per correct day)
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    correct_days = 0
    
    for day in days:
        sub_val = submission["task3"]["participation"]["day_attendance_rate"][day]
        key_val = answer_key["task3"]["participation"]["day_attendance_rate"][day]
        # Allow for small rounding differences (±0.1)
        if abs(sub_val - key_val) <= 0.1:
            correct_days += 1
    
    days_score = correct_days * 2
    results["day_attendance_rate"]["score"] = days_score
    results["day_attendance_rate"]["details"] = f"Correctly calculated {correct_days}/5 day attendance rates"
    
    # Peak Times (all 3 correct = 7 points, 2 correct = 4 points, 1 correct = 2 points)
    sub_peaks = set(submission["task3"]["participation"]["peak_times"])
    key_peaks = set(answer_key["task3"]["participation"]["peak_times"])
    correct_peaks = len(sub_peaks.intersection(key_peaks))
    
    if correct_peaks == 3:
        peaks_score = 7
    elif correct_peaks == 2:
        peaks_score = 4
    elif correct_peaks == 1:
        peaks_score = 2
    else:
        peaks_score = 0
    
    results["peak_times"]["score"] = peaks_score
    results["peak_times"]["details"] = f"Identified {correct_peaks}/3 correct peak times"
    
    # Declining Attendance (1.25 points per correct program)
    sub_declining = set(submission["task3"]["program_analysis"]["declining_attendance"])
    key_declining = set(answer_key["task3"]["program_analysis"]["declining_attendance"])
    correct_declining = len(sub_declining.intersection(key_declining))
    
    declining_score = correct_declining * 1.25
    results["declining_attendance"]["score"] = declining_score
    results["declining_attendance"]["details"] = f"Identified {correct_declining}/{len(key_declining)} programs with declining attendance"
    
    # Attendance-Satisfaction Correlation (within ±0.02 of correct value)
    sub_corr = submission["task3"]["program_analysis"]["attendance_satisfaction_correlation"]
    key_corr = answer_key["task3"]["program_analysis"]["attendance_satisfaction_correlation"]
    
    corr_score = 5 if abs(sub_corr - key_corr) <= 0.02 else 0
    results["attendance_satisfaction_correlation"]["score"] = corr_score
    results["attendance_satisfaction_correlation"]["details"] = "Correct correlation" if corr_score == 5 else "Incorrect correlation"
    
    # Calculate total score for Task 3
    results["total_score"] = (
        participants_score + days_score + peaks_score + declining_score + corr_score
    )
    
    return results

def check_critical_elements(task_results: Dict) -> List[str]:
    """Check if candidate failed any critical elements."""
    critical_failures = []
    
    # 1. Correctly identifying clients due for reassessment
    reassessment_score = task_results["task1"]["client_flags"]["reassessment_due"]["score"]
    if reassessment_score < 4:  # Less than 50% of 8 points
        critical_failures.append("Failed to demonstrate competency in identifying clients due for reassessment")
    
    # 2. Successfully resolving scheduling conflicts
    conflicts_score = task_results["task2"]["resolved_conflicts"]["score"]
    if conflicts_score < 5:  # Less than 50% of 10 points
        critical_failures.append("Failed to demonstrate competency in resolving scheduling conflicts")
    
    # 3. Accurately calculating program utilization rates
    utilization_score = task_results["task2"]["utilization"]["score"]
    if utilization_score < 4.5:  # Less than 50% of 9 points
        critical_failures.append("Failed to demonstrate competency in calculating program utilization rates")
    
    # 4. Identifying programs with declining attendance
    declining_score = task_results["task3"]["declining_attendance"]["score"]
    if declining_score < 2.5:  # Less than 50% of 5 points
        critical_failures.append("Failed to demonstrate competency in identifying programs with declining attendance")
    
    return critical_failures

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Combine results
    results = {
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "total_score": task1_results["total_score"] + task2_results["total_score"] + task3_results["total_score"],
        "max_points": 100,
        "overall_score": 0,  # Will be calculated
        "passed": False,  # Will be determined
        "performance_level": "",  # Will be determined
        "critical_failures": []  # Will be populated if any
    }
    
    # Calculate overall percentage score
    results["overall_score"] = round((results["total_score"] / results["max_points"]) * 100, 1)
    
    # Check for critical failures
    results["critical_failures"] = check_critical_elements(results)
    
    # Determine if passed and performance level
    if results["critical_failures"]:
        results["passed"] = False
        results["performance_level"] = "Failed (Critical Element Failure)"
    elif results["overall_score"] >= 90:
        results["passed"] = True
        results["performance_level"] = "Excellent"
    elif results["overall_score"] >= 70:
        results["passed"] = True
        results["performance_level"] = "Passed"
    else:
        results["passed"] = False
        results["performance_level"] = "Failed"
    
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
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Performance Level: {results['performance_level']}")
    
    if results["critical_failures"]:
        print("\nCritical Failures:")
        for failure in results["critical_failures"]:
            print(f"- {failure}")

if __name__ == "__main__":
    main()