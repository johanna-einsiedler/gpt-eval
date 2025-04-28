#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timedelta

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)

def save_json_file(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        sys.exit(1)

def evaluate_schedule_compliance(submission, answer_key):
    score = 0
    max_score = 60
    feedback = []
    
    # Check if all days are present
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    missing_days = [day for day in days if day not in submission["schedule"]]
    if missing_days:
        feedback.append(f"Missing days in schedule: {', '.join(missing_days)}")
        return 0, max_score, feedback
    
    # Check supervisor coverage
    supervisor_coverage = True
    for day in days:
        has_supervisor = any(emp["role"] == "Supervisor" for emp in submission["schedule"][day])
        if not has_supervisor:
            supervisor_coverage = False
            feedback.append(f"No supervisor scheduled for {day}")
    
    if supervisor_coverage:
        score += 15
        feedback.append("✓ At least one supervisor scheduled for all operating hours")
    
    # Check minimum staffing levels
    staffing_levels_met = True
    for day in days:
        if day != "saturday":
            # Check regular hours staffing (minimum 3)
            if len(submission["schedule"][day]) < 3:
                staffing_levels_met = False
                feedback.append(f"Insufficient staffing on {day}: {len(submission['schedule'][day])} employees (minimum 3 required)")
            
            # Check peak hours staffing (minimum 4)
            morning_peak = submission["coverage_analysis"][day]["morning_peak"]
            afternoon_peak = submission["coverage_analysis"][day]["afternoon_peak"]
            if morning_peak < 4 or afternoon_peak < 4:
                staffing_levels_met = False
                feedback.append(f"Insufficient peak hour staffing on {day}: Morning: {morning_peak}, Afternoon: {afternoon_peak} (minimum 4 required)")
        else:
            # Check Saturday staffing (minimum 2)
            if len(submission["schedule"][day]) < 2:
                staffing_levels_met = False
                feedback.append(f"Insufficient staffing on Saturday: {len(submission['schedule'][day])} employees (minimum 2 required)")
    
    if staffing_levels_met:
        score += 15
        feedback.append("✓ Minimum staffing levels met for all days")
    
    # Check employee constraints
    employee_constraints_met = True
    
    # Check if John Smith is not scheduled on Wednesday
    if "wednesday" in submission["schedule"]:
        if any(emp["employee"] == "John Smith" for emp in submission["schedule"]["wednesday"]):
            employee_constraints_met = False
            feedback.append("John Smith is scheduled on Wednesday despite constraint")
    
    # Check if Maria Garcia is not scheduled on Monday
    if "monday" in submission["schedule"]:
        if any(emp["employee"] == "Maria Garcia" for emp in submission["schedule"]["monday"]):
            employee_constraints_met = False
            feedback.append("Maria Garcia is scheduled on Monday despite constraint")
    
    # Check if Jennifer Lee is only scheduled on Monday, Wednesday, and Friday
    jennifer_days = []
    for day in days:
        if any(emp["employee"] == "Jennifer Lee" for emp in submission["schedule"][day]):
            jennifer_days.append(day)
    
    if set(jennifer_days) - set(["monday", "wednesday", "friday"]):
        employee_constraints_met = False
        feedback.append(f"Jennifer Lee is scheduled on incorrect days: {jennifer_days} (should only be Monday, Wednesday, Friday)")
    
    # Check if Michael Davis is only scheduled on Tuesday, Thursday, and Saturday
    michael_days = []
    for day in days:
        if any(emp["employee"] == "Michael Davis" for emp in submission["schedule"][day]):
            michael_days.append(day)
    
    if set(michael_days) - set(["tuesday", "thursday", "saturday"]):
        employee_constraints_met = False
        feedback.append(f"Michael Davis is scheduled on incorrect days: {michael_days} (should only be Tuesday, Thursday, Saturday)")
    
    if employee_constraints_met:
        score += 10
        feedback.append("✓ All employee availability constraints respected")
    
    # Check lunch breaks
    lunch_breaks_correct = True
    for day in days:
        for emp in submission["schedule"][day]:
            if "lunch_break" not in emp or not emp["lunch_break"]:
                lunch_breaks_correct = False
                feedback.append(f"Missing lunch break for {emp['employee']} on {day}")
    
    if lunch_breaks_correct:
        score += 10
        feedback.append("✓ Proper lunch breaks scheduled for all employees")
    
    # Check consecutive days off for full-time employees
    full_time_employees = ["John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", "David Brown"]
    consecutive_days_off = True
    
    for emp_name in full_time_employees:
        # Create a list of days the employee works
        working_days = []
        for i, day in enumerate(days):
            if any(emp["employee"] == emp_name for emp in submission["schedule"][day]):
                working_days.append(i)  # Use index to check consecutive days
        
        # Check if employee has 2 consecutive days off
        has_consecutive_off = False
        for i in range(7):  # Check all possible 2-day periods in a week
            if i not in working_days and (i+1)%7 not in working_days:
                has_consecutive_off = True
                break
        
        if not has_consecutive_off:
            consecutive_days_off = False
            feedback.append(f"{emp_name} does not have 2 consecutive days off")
    
    if consecutive_days_off:
        score += 10
        feedback.append("✓ Full-time employees have consecutive days off")
    
    return score, max_score, feedback

def evaluate_weekly_hours(submission, answer_key):
    score = 0
    max_score = 15
    feedback = []
    
    # Check if weekly hours are calculated for all employees
    expected_employees = [
        "John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", 
        "David Brown", "James Wilson", "Jennifer Lee", "Michael Davis"
    ]
    
    submission_employees = [entry["employee"] for entry in submission["weekly_hours"]]
    missing_employees = [emp for emp in expected_employees if emp not in submission_employees]
    
    if missing_employees:
        feedback.append(f"Missing weekly hours for employees: {', '.join(missing_employees)}")
        return 0, max_score, feedback
    
    # Check if weekly hours are calculated correctly
    hours_correct = True
    full_time_employees = ["John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", "David Brown"]
    part_time_employees = ["James Wilson", "Jennifer Lee", "Michael Davis"]
    
    # Verify hours from schedule
    calculated_hours = {}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
        for emp in submission["schedule"][day]:
            name = emp["employee"]
            
            # Parse times
            try:
                start_time = datetime.strptime(emp["start_time"], "%H:%M")
                end_time = datetime.strptime(emp["end_time"], "%H:%M")
                
                # Calculate hours (excluding lunch break)
                hours = (end_time - start_time).total_seconds() / 3600
                
                if name not in calculated_hours:
                    calculated_hours[name] = hours
                else:
                    calculated_hours[name] += hours
            except Exception as e:
                feedback.append(f"Error calculating hours for {name} on {day}: {e}")
                hours_correct = False
    
    # Compare with submitted weekly hours
    for entry in submission["weekly_hours"]:
        name = entry["employee"]
        submitted_hours = entry["total_hours"]
        
        if name in calculated_hours:
            # Allow for small rounding differences (0.1 hour)
            if abs(calculated_hours[name] - submitted_hours) > 0.1:
                hours_correct = False
                feedback.append(f"Incorrect weekly hours for {name}: submitted {submitted_hours}, calculated {calculated_hours[name]:.1f}")
        else:
            hours_correct = False
            feedback.append(f"Could not verify hours for {name}")
    
    if hours_correct:
        score += 5
        feedback.append("✓ Weekly hours calculated correctly")
    
    # Check if full-time employees don't exceed 40 hours
    full_time_hours_valid = True
    for entry in submission["weekly_hours"]:
        if entry["employee"] in full_time_employees and entry["total_hours"] > 40:
            full_time_hours_valid = False
            feedback.append(f"{entry['employee']} exceeds 40 hours: {entry['total_hours']}")
    
    if full_time_hours_valid:
        score += 5
        feedback.append("✓ Full-time employees do not exceed 40 hours")
    
    # Check if part-time employees don't exceed 20 hours
    part_time_hours_valid = True
    for entry in submission["weekly_hours"]:
        if entry["employee"] in part_time_employees and entry["total_hours"] > 20:
            part_time_hours_valid = False
            feedback.append(f"{entry['employee']} exceeds 20 hours: {entry['total_hours']}")
    
    if part_time_hours_valid:
        score += 5
        feedback.append("✓ Part-time employees do not exceed 20 hours")
    
    return score, max_score, feedback

def evaluate_coverage_analysis(submission, answer_key):
    score = 0
    max_score = 15
    feedback = []
    
    # Check if coverage analysis is present for all days
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    missing_days = [day for day in days if day not in submission["coverage_analysis"]]
    
    if missing_days:
        feedback.append(f"Missing coverage analysis for days: {', '.join(missing_days)}")
        return 0, max_score, feedback
    
    # Check peak hour counts
    peak_counts_correct = True
    
    for day in days:
        if day != "saturday":
            # Check if morning and afternoon peak counts are present
            if "morning_peak" not in submission["coverage_analysis"][day]:
                peak_counts_correct = False
                feedback.append(f"Missing morning peak count for {day}")
            
            if "afternoon_peak" not in submission["coverage_analysis"][day]:
                peak_counts_correct = False
                feedback.append(f"Missing afternoon peak count for {day}")
        else:
            # Saturday only needs morning peak
            if "morning_peak" not in submission["coverage_analysis"][day]:
                peak_counts_correct = False
                feedback.append(f"Missing morning peak count for {day}")
    
    # Verify peak counts from schedule
    for day in days:
        # Count employees during morning peak (10:00-12:00)
        morning_count = 0
        for emp in submission["schedule"][day]:
            try:
                start_time = datetime.strptime(emp["start_time"], "%H:%M")
                end_time = datetime.strptime(emp["end_time"], "%H:%M")
                
                # Check if employee covers the entire morning peak
                morning_peak_start = datetime.strptime("10:00", "%H:%M")
                morning_peak_end = datetime.strptime("12:00", "%H:%M")
                
                if start_time <= morning_peak_start and end_time >= morning_peak_end:
                    morning_count += 1
            except Exception as e:
                feedback.append(f"Error calculating morning peak for {emp['employee']} on {day}: {e}")
                peak_counts_correct = False
        
        # Verify morning peak count
        if "morning_peak" in submission["coverage_analysis"][day]:
            submitted_morning = submission["coverage_analysis"][day]["morning_peak"]
            if submitted_morning != morning_count:
                peak_counts_correct = False
                feedback.append(f"Incorrect morning peak count for {day}: submitted {submitted_morning}, calculated {morning_count}")
        
        # For weekdays, also check afternoon peak (14:00-16:00)
        if day != "saturday":
            afternoon_count = 0
            for emp in submission["schedule"][day]:
                try:
                    start_time = datetime.strptime(emp["start_time"], "%H:%M")
                    end_time = datetime.strptime(emp["end_time"], "%H:%M")
                    
                    # Check if employee covers the entire afternoon peak
                    afternoon_peak_start = datetime.strptime("14:00", "%H:%M")
                    afternoon_peak_end = datetime.strptime("16:00", "%H:%M")
                    
                    if start_time <= afternoon_peak_start and end_time >= afternoon_peak_end:
                        afternoon_count += 1
                except Exception as e:
                    feedback.append(f"Error calculating afternoon peak for {emp['employee']} on {day}: {e}")
                    peak_counts_correct = False
            
            # Verify afternoon peak count
            if "afternoon_peak" in submission["coverage_analysis"][day]:
                submitted_afternoon = submission["coverage_analysis"][day]["afternoon_peak"]
                if submitted_afternoon != afternoon_count:
                    peak_counts_correct = False
                    feedback.append(f"Incorrect afternoon peak count for {day}: submitted {submitted_afternoon}, calculated {afternoon_count}")
    
    if peak_counts_correct:
        score += 10
        feedback.append("✓ Peak hour counts calculated correctly")
    
    # Check adequate coverage assessment
    adequate_coverage_correct = True
    
    for day in days:
        if "adequate_coverage" not in submission["coverage_analysis"][day]:
            adequate_coverage_correct = False
            feedback.append(f"Missing adequate_coverage assessment for {day}")
            continue
        
        submitted_assessment = submission["coverage_analysis"][day]["adequate_coverage"]
        
        # Calculate expected assessment
        if day != "saturday":
            morning_peak = submission["coverage_analysis"][day].get("morning_peak", 0)
            afternoon_peak = submission["coverage_analysis"][day].get("afternoon_peak", 0)
            expected_assessment = morning_peak >= 4 and afternoon_peak >= 4
        else:
            morning_peak = submission["coverage_analysis"][day].get("morning_peak", 0)
            expected_assessment = morning_peak >= 2
        
        if submitted_assessment != expected_assessment:
            adequate_coverage_correct = False
            feedback.append(f"Incorrect adequate_coverage assessment for {day}: submitted {submitted_assessment}, expected {expected_assessment}")
    
    if adequate_coverage_correct:
        score += 5
        feedback.append("✓ Adequate coverage assessed correctly")
    
    return score, max_score, feedback

def evaluate_json_format(submission, answer_key):
    score = 0
    max_score = 10
    feedback = []
    
    # Check if all required top-level fields are present
    required_fields = ["schedule", "weekly_hours", "coverage_analysis", "scheduling_challenges"]
    missing_fields = [field for field in required_fields if field not in submission]
    
    if missing_fields:
        feedback.append(f"Missing required fields: {', '.join(missing_fields)}")
        return 0, max_score, feedback
    
    # Check if all days are present in schedule
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    missing_days = [day for day in days if day not in submission["schedule"]]
    
    if missing_days:
        feedback.append(f"Missing days in schedule: {', '.join(missing_days)}")
    else:
        score += 2
        feedback.append("✓ All required days present in schedule")
    
    # Check if all employees are present in weekly_hours
    expected_employees = [
        "John Smith", "Maria Garcia", "Robert Johnson", "Sarah Williams", 
        "David Brown", "James Wilson", "Jennifer Lee", "Michael Davis"
    ]
    
    submission_employees = [entry["employee"] for entry in submission["weekly_hours"]]
    missing_employees = [emp for emp in expected_employees if emp not in submission_employees]
    
    if missing_employees:
        feedback.append(f"Missing employees in weekly_hours: {', '.join(missing_employees)}")
    else:
        score += 2
        feedback.append("✓ All employees present in weekly_hours")
    
    # Check time format (HH:MM)
    time_format_correct = True
    for day in days:
        if day in submission["schedule"]:
            for emp in submission["schedule"][day]:
                # Check start_time format
                if "start_time" not in emp or not emp["start_time"]:
                    time_format_correct = False
                    feedback.append(f"Missing start_time for {emp.get('employee', 'unknown')} on {day}")
                else:
                    try:
                        datetime.strptime(emp["start_time"], "%H:%M")
                    except ValueError:
                        time_format_correct = False
                        feedback.append(f"Incorrect start_time format for {emp.get('employee', 'unknown')} on {day}: {emp['start_time']} (should be HH:MM)")
                
                # Check end_time format
                if "end_time" not in emp or not emp["end_time"]:
                    time_format_correct = False
                    feedback.append(f"Missing end_time for {emp.get('employee', 'unknown')} on {day}")
                else:
                    try:
                        datetime.strptime(emp["end_time"], "%H:%M")
                    except ValueError:
                        time_format_correct = False
                        feedback.append(f"Incorrect end_time format for {emp.get('employee', 'unknown')} on {day}: {emp['end_time']} (should be HH:MM)")
                
                # Check lunch_break format (HH:MM-HH:MM)
                if "lunch_break" not in emp or not emp["lunch_break"]:
                    time_format_correct = False
                    feedback.append(f"Missing lunch_break for {emp.get('employee', 'unknown')} on {day}")
                else:
                    try:
                        parts = emp["lunch_break"].split("-")
                        if len(parts) != 2:
                            raise ValueError("Incorrect format")
                        
                        datetime.strptime(parts[0], "%H:%M")
                        datetime.strptime(parts[1], "%H:%M")
                    except Exception:
                        time_format_correct = False
                        feedback.append(f"Incorrect lunch_break format for {emp.get('employee', 'unknown')} on {day}: {emp['lunch_break']} (should be HH:MM-HH:MM)")
    
    if time_format_correct:
        score += 3
        feedback.append("✓ Time formats are correct")
    
    # Check scheduling_challenges length (max 250 characters)
    if len(submission.get("scheduling_challenges", "")) > 250:
        feedback.append(f"scheduling_challenges exceeds 250 characters: {len(submission['scheduling_challenges'])} characters")
    else:
        score += 3
        feedback.append("✓ scheduling_challenges within character limit")
    
    return score, max_score, feedback

def evaluate_submission(submission, answer_key):
    results = {
        "schedule_compliance": {},
        "weekly_hours": {},
        "coverage_analysis": {},
        "json_format": {},
        "overall_score": 0
    }
    
    # Evaluate each section
    schedule_score, schedule_max, schedule_feedback = evaluate_schedule_compliance(submission, answer_key)
    results["schedule_compliance"] = {
        "score": schedule_score,
        "max_score": schedule_max,
        "percentage": round(schedule_score / schedule_max * 100, 1),
        "feedback": schedule_feedback
    }
    
    hours_score, hours_max, hours_feedback = evaluate_weekly_hours(submission, answer_key)
    results["weekly_hours"] = {
        "score": hours_score,
        "max_score": hours_max,
        "percentage": round(hours_score / hours_max * 100, 1),
        "feedback": hours_feedback
    }
    
    coverage_score, coverage_max, coverage_feedback = evaluate_coverage_analysis(submission, answer_key)
    results["coverage_analysis"] = {
        "score": coverage_score,
        "max_score": coverage_max,
        "percentage": round(coverage_score / coverage_max * 100, 1),
        "feedback": coverage_feedback
    }
    
    format_score, format_max, format_feedback = evaluate_json_format(submission, answer_key)
    results["json_format"] = {
        "score": format_score,
        "max_score": format_max,
        "percentage": round(format_score / format_max * 100, 1),
        "feedback": format_feedback
    }
    
    # Calculate overall score
    total_score = schedule_score + hours_score + coverage_score + format_score
    total_max = schedule_max + hours_max + coverage_max + format_max
    results["overall_score"] = round(total_score / total_max * 100, 1)
    
    # Determine if the candidate passed
    schedule_percentage = results["schedule_compliance"]["percentage"]
    passed = results["overall_score"] >= 80 and schedule_percentage >= 70
    
    results["passed"] = passed
    results["pass_criteria"] = {
        "overall_score_requirement": "≥ 80%",
        "schedule_compliance_requirement": "≥ 70%",
        "overall_score_achieved": f"{results['overall_score']}%",
        "schedule_compliance_achieved": f"{schedule_percentage}%"
    }
    
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
    
    save_json_file(results, "test_results.json")
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()