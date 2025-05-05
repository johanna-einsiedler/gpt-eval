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

def evaluate_service_coverage(submission, answer_key):
    """Evaluate service coverage (30 points)."""
    score = 0
    feedback = []
    
    # Check if all services are staffed (26 points)
    if not submission.get("unassigned_services"):
        score += 26
        feedback.append("All services properly staffed (+26 points)")
    else:
        assigned_services = 13 - len(submission.get("unassigned_services", []))
        score += assigned_services * 2
        feedback.append(f"{assigned_services}/13 services properly staffed (+{assigned_services * 2} points)")
    
    # Check for coverage gaps (4 points)
    if not submission.get("coverage_gaps"):
        score += 4
        feedback.append("No coverage gaps detected (+4 points)")
    else:
        feedback.append(f"Coverage gaps detected: {submission.get('coverage_gaps')} (0/4 points)")
    
    return score, feedback

def evaluate_schedule_compliance(submission, answer_key):
    """Evaluate schedule compliance (30 points)."""
    score = 0
    feedback = []
    
    # Check availability constraints (10 points)
    if submission.get("schedule_verification", {}).get("availability_constraints_respected", False):
        score += 10
        feedback.append("All employee availability constraints respected (+10 points)")
    else:
        feedback.append("Employee availability constraints violated (0/10 points)")
    
    # Check breaks and rest periods (10 points)
    if submission.get("schedule_verification", {}).get("breaks_scheduled_properly", False) and \
       submission.get("schedule_verification", {}).get("rest_periods_maintained", False):
        score += 10
        feedback.append("Breaks and rest periods properly scheduled (+10 points)")
    elif submission.get("schedule_verification", {}).get("breaks_scheduled_properly", False):
        score += 5
        feedback.append("Breaks properly scheduled but rest periods violated (+5/10 points)")
    elif submission.get("schedule_verification", {}).get("rest_periods_maintained", False):
        score += 5
        feedback.append("Rest periods maintained but breaks improperly scheduled (+5/10 points)")
    else:
        feedback.append("Both breaks and rest periods improperly scheduled (0/10 points)")
    
    # Check consecutive working hours (10 points)
    if submission.get("schedule_verification", {}).get("no_consecutive_hours_violation", False):
        score += 10
        feedback.append("No violations of maximum consecutive working hours (+10 points)")
    else:
        feedback.append("Maximum consecutive working hours violated (0/10 points)")
    
    return score, feedback

def evaluate_hour_requirements(submission, answer_key):
    """Evaluate hour requirements (20 points)."""
    score = 0
    feedback = []
    
    # Check full-time employees (10 points)
    ft_employees = ["FT001", "FT002", "FT003", "FT004", "FT005"]
    ft_correct = 0
    
    for emp_id in ft_employees:
        if submission.get("staff_utilization", {}).get(emp_id) == 40:
            ft_correct += 1
    
    ft_score = round((ft_correct / len(ft_employees)) * 10)
    score += ft_score
    feedback.append(f"{ft_correct}/{len(ft_employees)} full-time employees scheduled for exactly 40 hours (+{ft_score}/10 points)")
    
    # Check part-time employees (10 points)
    pt_requirements = {
        "PT001": 25,
        "PT002": 20,
        "PT003": 30,
        "PT004": 25
    }
    
    pt_correct = 0
    for emp_id, required_hours in pt_requirements.items():
        if submission.get("staff_utilization", {}).get(emp_id) == required_hours:
            pt_correct += 1
    
    pt_score = round((pt_correct / len(pt_requirements)) * 10)
    score += pt_score
    feedback.append(f"{pt_correct}/{len(pt_requirements)} part-time employees met their hour requirements (+{pt_score}/10 points)")
    
    return score, feedback

def evaluate_conflict_resolution(submission, answer_key):
    """Evaluate conflict resolution (15 points)."""
    score = 0
    feedback = []
    
    conflicts = ["conflict1", "conflict2", "conflict3"]
    correct_resolutions = answer_key.get("conflict_resolutions", {})
    
    for conflict in conflicts:
        submission_resolution = submission.get("conflict_resolutions", {}).get(conflict)
        correct_resolution = correct_resolutions.get(conflict)
        
        if submission_resolution == correct_resolution:
            score += 5
            feedback.append(f"{conflict} resolved optimally with {submission_resolution} (+5 points)")
        elif submission_resolution in ["SOLUTION_CODE_A", "SOLUTION_CODE_B", "SOLUTION_CODE_C"]:
            score += 2
            feedback.append(f"{conflict} resolved with {submission_resolution}, but {correct_resolution} would be optimal (+2/5 points)")
        else:
            feedback.append(f"{conflict} not properly resolved (0/5 points)")
    
    return score, feedback

def evaluate_json_submission(submission, answer_key):
    """Evaluate JSON submission accuracy (5 points)."""
    score = 0
    feedback = []
    
    # Check if all required fields are present
    required_fields = [
        "candidate_id", "total_scheduled_hours", "employees_with_overtime", 
        "unassigned_services", "conflict_resolutions", "coverage_gaps",
        "schedule_verification", "staff_utilization"
    ]
    
    missing_fields = [field for field in required_fields if field not in submission]
    
    if not missing_fields:
        # All fields present
        if isinstance(submission.get("total_scheduled_hours"), int) and \
           isinstance(submission.get("employees_with_overtime"), list) and \
           isinstance(submission.get("unassigned_services"), list) and \
           isinstance(submission.get("conflict_resolutions"), dict) and \
           isinstance(submission.get("coverage_gaps"), list) and \
           isinstance(submission.get("schedule_verification"), dict) and \
           isinstance(submission.get("staff_utilization"), dict):
            score += 5
            feedback.append("JSON submission correctly formatted (+5 points)")
        else:
            score += 2
            feedback.append("JSON submission has all required fields but some have incorrect data types (+2/5 points)")
    else:
        feedback.append(f"JSON submission missing required fields: {', '.join(missing_fields)} (0/5 points)")
    
    return score, feedback

def check_essential_requirements(submission, answer_key):
    """Check if all essential requirements are met."""
    essential_requirements = {
        "All services staffed": len(submission.get("unassigned_services", [])) == 0,
        "No availability constraints violated": submission.get("schedule_verification", {}).get("availability_constraints_respected", False),
        "All conflicts resolved": all(submission.get("conflict_resolutions", {}).get(f"conflict{i}") in ["SOLUTION_CODE_A", "SOLUTION_CODE_B", "SOLUTION_CODE_C"] for i in range(1, 4)),
        "No full-time overtime": not any(emp_id.startswith("FT") for emp_id in submission.get("employees_with_overtime", [])),
        "Part-time minimum hours met": submission.get("schedule_verification", {}).get("weekly_hours_requirements_met", False)
    }
    
    return essential_requirements

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate each section
    service_coverage_score, service_coverage_feedback = evaluate_service_coverage(submission, answer_key)
    schedule_compliance_score, schedule_compliance_feedback = evaluate_schedule_compliance(submission, answer_key)
    hour_requirements_score, hour_requirements_feedback = evaluate_hour_requirements(submission, answer_key)
    conflict_resolution_score, conflict_resolution_feedback = evaluate_conflict_resolution(submission, answer_key)
    json_submission_score, json_submission_feedback = evaluate_json_submission(submission, answer_key)
    
    # Calculate total score
    total_score = service_coverage_score + schedule_compliance_score + hour_requirements_score + conflict_resolution_score + json_submission_score
    overall_percentage = (total_score / 100) * 100
    
    # Check essential requirements
    essential_requirements = check_essential_requirements(submission, answer_key)
    all_essential_met = all(essential_requirements.values())
    
    # Determine pass/fail status
    passed = all_essential_met and total_score >= 80
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_percentage,
        "total_points": total_score,
        "passing_score": 80,
        "passed": passed,
        "essential_requirements": essential_requirements,
        "all_essential_requirements_met": all_essential_met,
        "section_scores": {
            "service_coverage": {
                "score": service_coverage_score,
                "max_points": 30,
                "feedback": service_coverage_feedback
            },
            "schedule_compliance": {
                "score": schedule_compliance_score,
                "max_points": 30,
                "feedback": schedule_compliance_feedback
            },
            "hour_requirements": {
                "score": hour_requirements_score,
                "max_points": 20,
                "feedback": hour_requirements_feedback
            },
            "conflict_resolution": {
                "score": conflict_resolution_score,
                "max_points": 15,
                "feedback": conflict_resolution_feedback
            },
            "json_submission": {
                "score": json_submission_score,
                "max_points": 5,
                "feedback": json_submission_feedback
            }
        },
        "submission_analysis": {
            "total_scheduled_hours": submission.get("total_scheduled_hours"),
            "expected_total_hours": answer_key.get("total_scheduled_hours"),
            "employees_with_overtime": submission.get("employees_with_overtime", []),
            "unassigned_services": submission.get("unassigned_services", []),
            "coverage_gaps": submission.get("coverage_gaps", [])
        }
    }
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.1f}%")
    print(f"Pass status: {'PASSED' if passed else 'FAILED'}")

if __name__ == "__main__":
    main()