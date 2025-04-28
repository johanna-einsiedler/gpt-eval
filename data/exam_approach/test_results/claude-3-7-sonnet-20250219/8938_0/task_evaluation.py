#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_schedule(submission, answer_key):
    score = 0
    feedback = []
    
    # Check critical path tasks (10 points)
    correct_critical_path = set(answer_key["schedule"]["critical_path_tasks"])
    submitted_critical_path = set(submission["schedule"]["critical_path_tasks"])
    
    common_tasks = correct_critical_path.intersection(submitted_critical_path)
    critical_path_score = min(10, len(common_tasks) * 10 / 6)  # 10 points for at least 4 of 6 tasks
    
    score += critical_path_score
    feedback.append(f"Critical path identification: {critical_path_score:.1f}/10 points")
    feedback.append(f"  - Correctly identified {len(common_tasks)} of 6 critical path tasks")
    
    # Check project duration (10 points)
    correct_duration = answer_key["schedule"]["project_duration_days"]
    submitted_duration = submission["schedule"]["project_duration_days"]
    
    duration_diff = abs(correct_duration - submitted_duration)
    duration_score = 10 if duration_diff <= 5 else max(0, 10 - (duration_diff - 5))
    
    score += duration_score
    feedback.append(f"Project duration calculation: {duration_score:.1f}/10 points")
    feedback.append(f"  - Calculated duration: {submitted_duration} days (correct: {correct_duration} days)")
    
    # Check task schedule with proper dependencies (10 points)
    # This is a simplified check - we're just counting how many tasks have reasonable dates
    correct_tasks = 0
    for task in submission["schedule"]["task_schedule"]:
        task_id = task["task_id"]
        # Find the same task in the answer key
        answer_task = next((t for t in answer_key["schedule"]["task_schedule"] if t["task_id"] == task_id), None)
        
        if answer_task:
            # Check if duration matches
            if task["duration_days"] == answer_task["duration_days"]:
                correct_tasks += 1
    
    task_schedule_score = min(10, correct_tasks * 10 / 12)  # 10 points for at least 12 of 15 tasks
    
    score += task_schedule_score
    feedback.append(f"Task schedule creation: {task_schedule_score:.1f}/10 points")
    feedback.append(f"  - Created logical schedule for {correct_tasks} of 15 tasks")
    
    return score, feedback

def evaluate_responsibility(submission, answer_key):
    score = 0
    feedback = []
    
    # Check RACI matrix (15 points)
    correct_assignments = 0
    for task_assignment in submission["responsibility"]["task_owners"]:
        task_id = task_assignment["task_id"]
        # Find the same task in the answer key
        answer_assignment = next((t for t in answer_key["responsibility"]["task_owners"] if t["task_id"] == task_id), None)
        
        if answer_assignment:
            # Check if responsible person matches
            if task_assignment["responsible"] == answer_assignment["responsible"]:
                correct_assignments += 1
    
    raci_score = min(15, correct_assignments * 15 / 12)  # 15 points for at least 12 of 15 tasks
    
    score += raci_score
    feedback.append(f"RACI matrix creation: {raci_score:.1f}/15 points")
    feedback.append(f"  - Created appropriate assignments for {correct_assignments} of 15 tasks")
    
    # Check most assigned team member (5 points)
    correct_most_assigned = answer_key["responsibility"]["most_assigned_team_member"]
    submitted_most_assigned = submission["responsibility"]["most_assigned_team_member"]
    
    most_assigned_score = 5 if submitted_most_assigned == correct_most_assigned else 0
    
    score += most_assigned_score
    feedback.append(f"Most assigned team member identification: {most_assigned_score}/5 points")
    feedback.append(f"  - Identified: {submitted_most_assigned} (correct: {correct_most_assigned})")
    
    # Check unassigned tasks (5 points)
    unassigned_score = 5 if len(submission["responsibility"]["unassigned_tasks"]) == 0 else 0
    
    score += unassigned_score
    feedback.append(f"Task assignment completeness: {unassigned_score}/5 points")
    feedback.append(f"  - {len(submission['responsibility']['unassigned_tasks'])} unassigned tasks (should be 0)")
    
    return score, feedback

def evaluate_compliance(submission, answer_key):
    score = 0
    feedback = []
    
    # Check highest priority item (5 points)
    correct_highest_priority = answer_key["compliance"]["highest_priority_item"]
    submitted_highest_priority = submission["compliance"]["highest_priority_item"]
    
    highest_priority_score = 5 if submitted_highest_priority == correct_highest_priority else 0
    
    score += highest_priority_score
    feedback.append(f"Highest priority compliance item: {highest_priority_score}/5 points")
    feedback.append(f"  - Identified: {submitted_highest_priority} (correct: {correct_highest_priority})")
    
    # Check compliance requirements linked to tasks (10 points)
    correct_links = 0
    for req_detail in submission["compliance"]["requirement_details"]:
        req_id = req_detail["req_id"]
        # Find the same requirement in the answer key
        answer_req = next((r for r in answer_key["compliance"]["requirement_details"] if r["req_id"] == req_id), None)
        
        if answer_req:
            # Check if linked tasks match
            submitted_links = set(req_detail["linked_tasks"])
            correct_links_set = set(answer_req["linked_tasks"])
            
            if submitted_links == correct_links_set:
                correct_links += 1
    
    links_score = min(10, correct_links * 10 / 6)  # 10 points for at least 6 of 8 requirements
    
    score += links_score
    feedback.append(f"Compliance requirements linking: {links_score:.1f}/10 points")
    feedback.append(f"  - Properly linked {correct_links} of 8 requirements to tasks")
    
    # Check deadline dates (10 points)
    correct_deadlines = 0
    for req_detail in submission["compliance"]["requirement_details"]:
        req_id = req_detail["req_id"]
        # Find the same requirement in the answer key
        answer_req = next((r for r in answer_key["compliance"]["requirement_details"] if r["req_id"] == req_id), None)
        
        if answer_req:
            # Parse dates and check if they're close enough
            try:
                submitted_date = datetime.strptime(req_detail["deadline_date"], "%Y-%m-%d")
                answer_date = datetime.strptime(answer_req["deadline_date"], "%Y-%m-%d")
                
                # Allow a 3-day margin of error for dates
                if abs((submitted_date - answer_date).days) <= 3:
                    correct_deadlines += 1
            except:
                pass
    
    deadlines_score = min(10, correct_deadlines * 10 / 6)  # 10 points for at least 6 of 8 requirements
    
    score += deadlines_score
    feedback.append(f"Compliance deadline calculation: {deadlines_score:.1f}/10 points")
    feedback.append(f"  - Calculated accurate deadlines for {correct_deadlines} of 8 requirements")
    
    return score, feedback

def evaluate_integration(submission, answer_key):
    score = 0
    feedback = []
    
    # Check high-risk tasks (10 points)
    correct_high_risk = set(answer_key["integration"]["high_risk_tasks"])
    submitted_high_risk = set(submission["integration"]["high_risk_tasks"])
    
    common_high_risk = correct_high_risk.intersection(submitted_high_risk)
    high_risk_score = min(10, len(common_high_risk) * 10 / 3)  # 10 points for at least 3 of 5 tasks
    
    score += high_risk_score
    feedback.append(f"High-risk task identification: {high_risk_score:.1f}/10 points")
    feedback.append(f"  - Correctly identified {len(common_high_risk)} of 5 high-risk tasks")
    
    # Check next deadline (5 points)
    correct_next_deadline = answer_key["integration"]["next_deadline"]
    submitted_next_deadline = submission["integration"]["next_deadline"]
    
    # Parse dates and check if they're close enough
    try:
        submitted_date = datetime.strptime(submitted_next_deadline, "%Y-%m-%d")
        answer_date = datetime.strptime(correct_next_deadline, "%Y-%m-%d")
        
        # Allow a 3-day margin of error for dates
        next_deadline_score = 5 if abs((submitted_date - answer_date).days) <= 3 else 0
    except:
        next_deadline_score = 0
    
    score += next_deadline_score
    feedback.append(f"Next deadline identification: {next_deadline_score}/5 points")
    feedback.append(f"  - Identified: {submitted_next_deadline} (correct: {correct_next_deadline})")
    
    # Check task status tracking framework (5 points)
    # This is more subjective, but we'll check if they have the right categories
    correct_categories = set(answer_key["integration"]["task_status_summary"].keys())
    submitted_categories = set(submission["integration"]["task_status_summary"].keys())
    
    common_categories = correct_categories.intersection(submitted_categories)
    framework_score = 5 if len(common_categories) == len(correct_categories) else min(3, len(common_categories))
    
    score += framework_score
    feedback.append(f"Task status tracking framework: {framework_score}/5 points")
    feedback.append(f"  - Included {len(common_categories)} of {len(correct_categories)} required status categories")
    
    return score, feedback

def check_automatic_failure(submission, answer_key):
    failures = []
    
    # Check for JSON format issues
    required_sections = ["schedule", "responsibility", "compliance", "integration"]
    for section in required_sections:
        if section not in submission:
            failures.append(f"Missing required section: {section}")
    
    # Check for dependency violations in schedule
    # This would require more complex logic to fully implement
    
    # Check for unassigned critical tasks
    if "unassigned_tasks" in submission["responsibility"]:
        critical_path = set(answer_key["schedule"]["critical_path_tasks"])
        unassigned = set(submission["responsibility"]["unassigned_tasks"])
        critical_unassigned = critical_path.intersection(unassigned)
        
        if critical_unassigned:
            failures.append(f"Critical tasks left unassigned: {', '.join(critical_unassigned)}")
    
    # Check if compliance requirements are linked to tasks
    if "requirement_details" in submission["compliance"]:
        for req in submission["compliance"]["requirement_details"]:
            if "linked_tasks" not in req or not req["linked_tasks"]:
                failures.append(f"Compliance requirement {req.get('req_id', 'unknown')} not linked to any tasks")
    
    return failures

def evaluate_submission(submission, answer_key):
    results = {
        "schedule": {},
        "responsibility": {},
        "compliance": {},
        "integration": {},
        "overall_score": 0,
        "automatic_failures": [],
        "passed": False
    }
    
    # Check for automatic failure conditions
    automatic_failures = check_automatic_failure(submission, answer_key)
    results["automatic_failures"] = automatic_failures
    
    if automatic_failures:
        results["passed"] = False
        results["overall_score"] = 0
        return results
    
    # Evaluate each section
    schedule_score, schedule_feedback = evaluate_schedule(submission, answer_key)
    responsibility_score, responsibility_feedback = evaluate_responsibility(submission, answer_key)
    compliance_score, compliance_feedback = evaluate_compliance(submission, answer_key)
    integration_score, integration_feedback = evaluate_integration(submission, answer_key)
    
    # Record section results
    results["schedule"] = {
        "score": schedule_score,
        "max_score": 30,
        "feedback": schedule_feedback
    }
    
    results["responsibility"] = {
        "score": responsibility_score,
        "max_score": 25,
        "feedback": responsibility_feedback
    }
    
    results["compliance"] = {
        "score": compliance_score,
        "max_score": 25,
        "feedback": compliance_feedback
    }
    
    results["integration"] = {
        "score": integration_score,
        "max_score": 20,
        "feedback": integration_feedback
    }
    
    # Calculate overall score
    total_score = schedule_score + responsibility_score + compliance_score + integration_score
    percentage_score = round(total_score)
    
    results["overall_score"] = percentage_score
    results["passed"] = percentage_score >= 70
    
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
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()