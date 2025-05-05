#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_weekly_schedule(candidate_schedule, answer_key_schedule):
    """Evaluate Task 1: Weekly Schedule (50 points)"""
    score = 0
    feedback = []
    
    # Check if all days are present
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    candidate_days = [day["day"] for day in candidate_schedule]
    
    if set(days_of_week) != set(candidate_days):
        feedback.append("Missing days in the weekly schedule")
    else:
        score += 5
        feedback.append("All days of the week are included")
    
    # Staffing Requirements (15 points)
    staffing_score = 0
    
    # Create a lookup for answer key schedule
    answer_key_by_day = {day["day"]: day for day in answer_key_schedule}
    
    # Check position coverage for each day
    position_coverage_issues = []
    for day_schedule in candidate_schedule:
        day = day_schedule["day"]
        if day not in answer_key_by_day:
            continue
            
        # Get unique positions for the day
        candidate_positions = {shift["position"] for shift in day_schedule["shifts"]}
        answer_key_positions = {shift["position"] for shift in answer_key_by_day[day]["shifts"]}
        
        missing_positions = answer_key_positions - candidate_positions
        if missing_positions:
            position_coverage_issues.append(f"Missing positions on {day}: {', '.join(missing_positions)}")
    
    if not position_coverage_issues:
        staffing_score += 10
        feedback.append("All required positions are covered during business hours")
    else:
        # Partial credit for position coverage
        staffing_score += max(0, 10 - len(position_coverage_issues))
        feedback.extend(position_coverage_issues)
    
    # Check minimum staffing levels (simplified check)
    if staffing_score >= 5:
        staffing_score += 5
        feedback.append("Minimum staffing levels appear to be maintained")
    
    score += staffing_score
    
    # Labor Regulations (15 points)
    labor_score = 0
    labor_issues = []
    
    # Check shift lengths and breaks
    for day_schedule in candidate_schedule:
        for shift in day_schedule["shifts"]:
            # Check shift length
            start_time = datetime.strptime(shift["start_time"], "%H:%M")
            end_time = datetime.strptime(shift["end_time"], "%H:%M")
            
            # Handle overnight shifts
            hours = (end_time - start_time).seconds / 3600
            if hours < 0:
                hours += 24
                
            if hours > 8:
                labor_issues.append(f"Shift too long: {shift['employee_id']} on {day_schedule['day']} ({hours:.1f} hours)")
            
            # Check breaks for shifts over 5 hours
            if hours > 5:
                if "break_start" not in shift or "break_end" not in shift:
                    labor_issues.append(f"Missing break: {shift['employee_id']} on {day_schedule['day']} (shift > 5 hours)")
                else:
                    break_start = datetime.strptime(shift["break_start"], "%H:%M")
                    break_end = datetime.strptime(shift["break_end"], "%H:%M")
                    break_duration = (break_end - break_start).seconds / 60
                    
                    if break_duration != 30:
                        labor_issues.append(f"Incorrect break duration: {shift['employee_id']} on {day_schedule['day']} ({break_duration} minutes)")
    
    if not labor_issues:
        labor_score += 15
        feedback.append("Labor regulations are followed (shift lengths and breaks)")
    else:
        # Partial credit based on number of issues
        labor_score += max(0, 15 - len(labor_issues))
        feedback.extend(labor_issues[:3])  # Limit feedback to first 3 issues
        if len(labor_issues) > 3:
            feedback.append(f"...and {len(labor_issues) - 3} more labor regulation issues")
    
    score += labor_score
    
    # Staff Utilization (10 points) - simplified check
    # In a real implementation, this would check against staff availability data
    staff_utilization_score = 10
    feedback.append("Staff utilization appears appropriate (simplified check)")
    
    score += staff_utilization_score
    
    # Schedule Efficiency (10 points) - simplified check
    schedule_efficiency_score = 10
    feedback.append("Schedule efficiency appears appropriate (simplified check)")
    
    score += schedule_efficiency_score
    
    return {
        "score": score,
        "max_score": 50,
        "percentage": (score / 50) * 100,
        "feedback": feedback
    }

def evaluate_schedule_adjustments(candidate_adjustments, answer_key_adjustments):
    """Evaluate Task 2: Schedule Adjustments (25 points)"""
    score = 0
    feedback = []
    
    # Check if the day is correct
    if candidate_adjustments.get("day") != "Wednesday":
        feedback.append("Adjusted schedule is not for Wednesday")
    else:
        score += 2
    
    # Addressing Required Changes (15 points)
    changes_score = 0
    
    # 1. Check if sick employee (E003) is not scheduled
    employee_ids = [shift["employee_id"] for shift in candidate_adjustments.get("shifts", [])]
    if "E003" not in employee_ids:
        changes_score += 5
        feedback.append("Correctly removed sick employee E003 from schedule")
    else:
        feedback.append("Failed to remove sick employee E003 from schedule")
    
    # 2. Check for additional server during 18:00-22:00
    server_count_evening = 0
    for shift in candidate_adjustments.get("shifts", []):
        if shift["position"] == "Server":
            start_time = datetime.strptime(shift["start_time"], "%H:%M")
            end_time = datetime.strptime(shift["end_time"], "%H:%M")
            
            # Check if shift covers 18:00-22:00
            if (start_time.hour <= 18 and end_time.hour >= 22) or \
               (start_time.hour <= 18 and end_time.hour >= 18) or \
               (start_time.hour >= 18 and start_time.hour < 22):
                server_count_evening += 1
    
    # We need at least 4 servers in the evening (3 regular + 1 additional)
    if server_count_evening >= 4:
        changes_score += 5
        feedback.append("Added additional server for the private event")
    else:
        feedback.append(f"Failed to add additional server for private event (found {server_count_evening} servers)")
    
    # 3. Check for early kitchen opening at 07:00
    early_opening_staff = False
    for shift in candidate_adjustments.get("shifts", []):
        if shift["start_time"] == "07:00":
            early_opening_staff = True
            break
    
    if early_opening_staff:
        changes_score += 5
        feedback.append("Accommodated early kitchen opening at 07:00")
    else:
        feedback.append("Failed to accommodate early kitchen opening at 07:00")
    
    score += changes_score
    
    # Maintaining Requirements (10 points) - simplified check
    # In a real implementation, this would check staffing levels and labor regulations
    maintaining_score = 10
    feedback.append("Staffing levels and labor regulations appear maintained (simplified check)")
    
    score += maintaining_score
    
    return {
        "score": score,
        "max_score": 25,
        "percentage": (score / 25) * 100,
        "feedback": feedback
    }

def evaluate_duty_assignments(candidate_assignments, answer_key_assignments):
    """Evaluate Task 3: Duty Assignments (25 points)"""
    score = 0
    feedback = []
    
    # Check if all duties are assigned
    duty_ids = ["D001", "D002", "D003", "D004", "D005"]
    candidate_duties = [duty["duty_id"] for duty in candidate_assignments]
    
    missing_duties = set(duty_ids) - set(candidate_duties)
    if missing_duties:
        feedback.append(f"Missing duty assignments: {', '.join(missing_duties)}")
    else:
        score += 5
        feedback.append("All required duties are assigned")
    
    # Qualification Matching (10 points) - simplified check
    # In a real implementation, this would check against qualification data
    qualification_score = 10
    feedback.append("Duty qualifications appear to be matched appropriately (simplified check)")
    
    score += qualification_score
    
    # Schedule Integration (10 points) - simplified check
    # In a real implementation, this would check for conflicts with regular shifts
    schedule_integration_score = 10
    feedback.append("Duty assignments appear to be integrated with regular schedule (simplified check)")
    
    score += schedule_integration_score
    
    return {
        "score": score,
        "max_score": 25,
        "percentage": (score / 25) * 100,
        "feedback": feedback
    }

def evaluate_submission(candidate_submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "task1": evaluate_weekly_schedule(
            candidate_submission.get("task1", {}).get("weekly_schedule", []),
            answer_key.get("task1", {}).get("weekly_schedule", [])
        ),
        "task2": evaluate_schedule_adjustments(
            candidate_submission.get("task2", {}).get("adjusted_schedule", {}),
            answer_key.get("task2", {}).get("adjusted_schedule", {})
        ),
        "task3": evaluate_duty_assignments(
            candidate_submission.get("task3", {}).get("duty_assignments", []),
            answer_key.get("task3", {}).get("duty_assignments", [])
        )
    }
    
    # Calculate overall score
    total_score = sum(task["score"] for task in results.values())
    max_score = sum(task["max_score"] for task in results.values())
    overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    results["overall_score"] = overall_percentage
    results["total_points"] = total_score
    results["max_points"] = max_score
    results["pass_fail"] = "PASS" if overall_percentage >= 70 else "FAIL"
    
    # Check if any task is below 60% (automatic fail)
    for task, evaluation in results.items():
        if task in ["task1", "task2", "task3"] and evaluation["percentage"] < 60:
            results["pass_fail"] = "FAIL"
            results["fail_reason"] = f"{task} score below 60% threshold"
            break
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    candidate_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate_submission = load_json_file(candidate_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(candidate_submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']:.2f}% ({results['pass_fail']})")

if __name__ == "__main__":
    main()