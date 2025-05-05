#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Project Charter Development (30 points)"""
    score = 0
    feedback = []
    
    # Project charter elements (10 points)
    charter_score = 0
    charter_feedback = []
    
    # Check project title
    if submission["task1"]["project_charter"]["project_title"] == answer_key["task1"]["project_charter"]["project_title"]:
        charter_score += 2.5
    else:
        charter_feedback.append("Incorrect project title")
    
    # Check project start date
    if submission["task1"]["project_charter"]["project_start_date"] == answer_key["task1"]["project_charter"]["project_start_date"]:
        charter_score += 2.5
    else:
        charter_feedback.append("Incorrect project start date")
    
    # Check project end date
    if submission["task1"]["project_charter"]["project_end_date"] == answer_key["task1"]["project_charter"]["project_end_date"]:
        charter_score += 2.5
    else:
        charter_feedback.append("Incorrect project end date (should be 6 months from start date)")
    
    # Check project sponsor
    if submission["task1"]["project_charter"]["project_sponsor"] == answer_key["task1"]["project_charter"]["project_sponsor"]:
        charter_score += 2.5
    else:
        charter_feedback.append("Incorrect project sponsor")
    
    # Key objectives (10 points)
    objectives_score = 0
    objectives_feedback = []
    
    # Check if there are 5 objectives
    if len(submission["task1"]["key_objectives"]) == 5:
        objectives_score += 2
    else:
        objectives_feedback.append(f"Expected 5 key objectives, found {len(submission['task1']['key_objectives'])}")
    
    # Check content of objectives
    key_terms = [
        ["migrat", "6 month"],
        ["20%", "cost", "reduc"],
        ["99.9%", "availab"],
        ["performance", "exceed"],
        ["secur", "complian"]
    ]
    
    for i, terms in enumerate(key_terms):
        if i < len(submission["task1"]["key_objectives"]):
            obj = submission["task1"]["key_objectives"][i].lower()
            if any(term.lower() in obj for term in terms):
                objectives_score += 1.6
            else:
                objectives_feedback.append(f"Objective {i+1} missing key terms: {terms}")
    
    # Success criteria (10 points)
    criteria_score = 0
    criteria_feedback = []
    
    # Check if there are 3 success criteria
    if len(submission["task1"]["success_criteria"]) == 3:
        criteria_score += 2
    else:
        criteria_feedback.append(f"Expected 3 success criteria, found {len(submission['task1']['success_criteria'])}")
    
    # Check content of success criteria
    key_criteria_terms = [
        ["budget", "$250,000"],
        ["20%", "cost", "reduc"],
        ["99.9%", "availab"]
    ]
    
    for i, terms in enumerate(key_criteria_terms):
        if i < len(submission["task1"]["success_criteria"]):
            crit = submission["task1"]["success_criteria"][i].lower()
            if any(term.lower() in crit for term in terms):
                criteria_score += 2.67
            else:
                criteria_feedback.append(f"Success criterion {i+1} missing key terms: {terms}")
    
    # Round scores to nearest 0.5
    charter_score = round(charter_score * 2) / 2
    objectives_score = round(objectives_score * 2) / 2
    criteria_score = round(criteria_score * 2) / 2
    
    score = charter_score + objectives_score + criteria_score
    
    feedback = {
        "charter": {
            "score": charter_score,
            "max_score": 10,
            "feedback": charter_feedback
        },
        "objectives": {
            "score": objectives_score,
            "max_score": 10,
            "feedback": objectives_feedback
        },
        "success_criteria": {
            "score": criteria_score,
            "max_score": 10,
            "feedback": criteria_feedback
        },
        "total_score": score,
        "max_score": 30
    }
    
    return score, feedback

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Project Schedule Creation (40 points)"""
    score = 0
    feedback = {}
    
    # Schedule includes at least 10 logical activities (15 points)
    schedule_score = 0
    schedule_feedback = []
    
    # Check number of activities
    activities = submission["task2"]["project_schedule"]
    if len(activities) >= 10:
        schedule_score += 5
    else:
        schedule_feedback.append(f"Expected at least 10 activities, found {len(activities)}")
    
    # Check activity structure and logic
    valid_activities = 0
    activity_issues = []
    
    for activity in activities:
        issues = []
        
        # Check activity ID format
        if not activity.get("activity_id", "").startswith("ACT-"):
            issues.append("Activity ID should follow format ACT-XX")
        
        # Check for missing fields
        required_fields = ["activity_name", "duration_days", "predecessors", "start_date", "end_date"]
        for field in required_fields:
            if field not in activity:
                issues.append(f"Missing required field: {field}")
        
        # Check date format and logic
        try:
            start = datetime.strptime(activity.get("start_date", ""), "%Y-%m-%d")
            end = datetime.strptime(activity.get("end_date", ""), "%Y-%m-%d")
            duration = activity.get("duration_days", 0)
            
            # Calculate expected end date (start date + duration - 1)
            from datetime import timedelta
            expected_end = start + timedelta(days=duration-1)
            
            if end.date() != expected_end.date():
                issues.append(f"End date doesn't match duration. Expected: {expected_end.date()}, Found: {end.date()}")
                
        except ValueError:
            issues.append("Invalid date format. Use YYYY-MM-DD")
        
        if not issues:
            valid_activities += 1
        else:
            activity_issues.append({activity.get("activity_id", "Unknown"): issues})
    
    # Score based on valid activities (10 points for 10+ valid activities)
    schedule_score += min(10, valid_activities) * 1.0
    
    if activity_issues:
        schedule_feedback.append({"activity_issues": activity_issues})
    
    # Critical path correctly identified (10 points)
    critical_path_score = 0
    critical_path_feedback = []
    
    # Check if critical path is provided
    if "critical_path_activities" in submission["task2"]:
        cp_activities = submission["task2"]["critical_path_activities"]
        
        # Check if critical path has reasonable length (at least 3 activities)
        if len(cp_activities) >= 3:
            critical_path_score += 5
        else:
            critical_path_feedback.append(f"Critical path too short. Expected at least 3 activities, found {len(cp_activities)}")
        
        # Check if critical path activities exist in schedule
        activity_ids = [a.get("activity_id") for a in activities]
        invalid_cp = [cp for cp in cp_activities if cp not in activity_ids]
        
        if invalid_cp:
            critical_path_feedback.append(f"Critical path contains activities not in schedule: {invalid_cp}")
        else:
            critical_path_score += 5
    else:
        critical_path_feedback.append("Critical path activities not provided")
    
    # Resource allocation respects constraints (15 points)
    resource_score = 0
    resource_feedback = []
    
    # Check if resource allocation is provided
    if "resource_allocation" in submission["task2"]:
        resource_allocation = submission["task2"]["resource_allocation"]
        
        # Check if all activities have resource allocation
        missing_allocation = [a.get("activity_id") for a in activities if a.get("activity_id") not in resource_allocation]
        if missing_allocation:
            resource_feedback.append(f"Missing resource allocation for activities: {missing_allocation}")
        else:
            resource_score += 5
        
        # Check resource allocation constraints
        resource_limits = {
            "Project Manager": 1.00,
            "Systems Architect": 0.80,
            "Database Administrator": 0.60,
            "Network Engineer": 0.70,
            "Security Specialist": 0.50,
            "Cloud Engineer": 0.90
        }
        
        constraint_violations = []
        
        for activity_id, resources in resource_allocation.items():
            for role, allocation in resources.items():
                if role in resource_limits:
                    if allocation > resource_limits[role]:
                        constraint_violations.append(f"{activity_id}: {role} allocated {allocation}, exceeds limit of {resource_limits[role]}")
                else:
                    constraint_violations.append(f"{activity_id}: Unknown role '{role}'")
        
        if constraint_violations:
            resource_feedback.append({"constraint_violations": constraint_violations})
        else:
            resource_score += 5
        
        # Check allocation format (increments of 0.25)
        format_violations = []
        
        for activity_id, resources in resource_allocation.items():
            for role, allocation in resources.items():
                if allocation % 0.25 != 0:
                    format_violations.append(f"{activity_id}: {role} allocation {allocation} not in increments of 0.25")
        
        if format_violations:
            resource_feedback.append({"format_violations": format_violations})
        else:
            resource_score += 5
    else:
        resource_feedback.append("Resource allocation not provided")
    
    # Round scores to nearest 0.5
    schedule_score = round(schedule_score * 2) / 2
    critical_path_score = round(critical_path_score * 2) / 2
    resource_score = round(resource_score * 2) / 2
    
    score = schedule_score + critical_path_score + resource_score
    
    feedback = {
        "schedule": {
            "score": schedule_score,
            "max_score": 15,
            "feedback": schedule_feedback
        },
        "critical_path": {
            "score": critical_path_score,
            "max_score": 10,
            "feedback": critical_path_feedback
        },
        "resource_allocation": {
            "score": resource_score,
            "max_score": 15,
            "feedback": resource_feedback
        },
        "total_score": score,
        "max_score": 40
    }
    
    return score, feedback

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Project Budget Preparation (30 points)"""
    score = 0
    feedback = {}
    
    # Budget calculations accurate (15 points)
    budget_score = 0
    budget_feedback = []
    
    # Check if budget is provided
    if "project_budget" in submission["task3"]:
        budget = submission["task3"]["project_budget"]
        
        # Check required categories
        required_categories = ["personnel_costs", "hardware_costs", "software_licenses", 
                              "training_costs", "contingency_reserve", "total_budget"]
        
        missing_categories = [cat for cat in required_categories if cat not in budget]
        if missing_categories:
            budget_feedback.append(f"Missing budget categories: {missing_categories}")
        else:
            budget_score += 3
        
        # Check hardware costs (should be $33,000)
        if "hardware_costs" in budget:
            if abs(budget["hardware_costs"] - 33000.00) < 0.01:
                budget_score += 2
            else:
                budget_feedback.append(f"Incorrect hardware costs. Expected: $33,000.00, Found: ${budget['hardware_costs']}")
        
        # Check software licenses (should be $55,000)
        if "software_licenses" in budget:
            if abs(budget["software_licenses"] - 55000.00) < 0.01:
                budget_score += 2
            else:
                budget_feedback.append(f"Incorrect software licenses. Expected: $55,000.00, Found: ${budget['software_licenses']}")
        
        # Check training costs (should be 5% of personnel costs)
        if "training_costs" in budget and "personnel_costs" in budget:
            expected_training = budget["personnel_costs"] * 0.05
            if abs(budget["training_costs"] - expected_training) < 0.01:
                budget_score += 2
            else:
                budget_feedback.append(f"Incorrect training costs. Should be 5% of personnel costs (${expected_training:.2f})")
        
        # Check contingency reserve (should be 10% of all other costs)
        if all(cat in budget for cat in ["personnel_costs", "hardware_costs", "software_licenses", "training_costs", "contingency_reserve"]):
            base_costs = budget["personnel_costs"] + budget["hardware_costs"] + budget["software_licenses"] + budget["training_costs"]
            expected_contingency = base_costs * 0.10
            if abs(budget["contingency_reserve"] - expected_contingency) < 0.01:
                budget_score += 3
            else:
                budget_feedback.append(f"Incorrect contingency reserve. Should be 10% of other costs (${expected_contingency:.2f})")
        
        # Check total budget (should be sum of all categories)
        if all(cat in budget for cat in required_categories[:-1]):
            expected_total = budget["personnel_costs"] + budget["hardware_costs"] + budget["software_licenses"] + budget["training_costs"] + budget["contingency_reserve"]
            if abs(budget["total_budget"] - expected_total) < 0.01:
                budget_score += 3
            else:
                budget_feedback.append(f"Incorrect total budget. Should be sum of all categories (${expected_total:.2f})")
    else:
        budget_feedback.append("Project budget not provided")
    
    # Phase breakdown totals to overall budget (10 points)
    phase_score = 0
    phase_feedback = []
    
    # Check if cost breakdown is provided
    if "cost_breakdown" in submission["task3"] and "project_budget" in submission["task3"] and "total_budget" in submission["task3"]["project_budget"]:
        breakdown = submission["task3"]["cost_breakdown"]
        total_budget = submission["task3"]["project_budget"]["total_budget"]
        
        # Check required phases
        required_phases = ["planning", "design", "implementation", "testing", "deployment"]
        
        missing_phases = [phase for phase in required_phases if phase not in breakdown]
        if missing_phases:
            phase_feedback.append(f"Missing phases in cost breakdown: {missing_phases}")
        else:
            phase_score += 5
        
        # Check if phases sum to total budget
        if all(phase in breakdown for phase in required_phases):
            phase_sum = sum(breakdown[phase] for phase in required_phases)
            if abs(phase_sum - total_budget) < 0.01:
                phase_score += 5
            else:
                phase_feedback.append(f"Phase costs don't sum to total budget. Sum: ${phase_sum:.2f}, Budget: ${total_budget:.2f}")
    else:
        phase_feedback.append("Cost breakdown not provided or total budget missing")
    
    # Budget risks relevant to project (5 points)
    risk_score = 0
    risk_feedback = []
    
    # Check if budget risks are provided
    if "budget_risks" in submission["task3"]:
        risks = submission["task3"]["budget_risks"]
        
        # Check number of risks
        if len(risks) == 3:
            risk_score += 2
        else:
            risk_feedback.append(f"Expected 3 budget risks, found {len(risks)}")
        
        # Check if risks are from predefined list
        valid_risks = [
            "Scope creep",
            "Resource availability",
            "Technology compatibility issues",
            "Vendor delays",
            "Regulatory compliance requirements"
        ]
        
        invalid_risks = [risk for risk in risks if risk not in valid_risks]
        if invalid_risks:
            risk_feedback.append(f"Invalid risks not from predefined list: {invalid_risks}")
        else:
            risk_score += 3
    else:
        risk_feedback.append("Budget risks not provided")
    
    # Round scores to nearest 0.5
    budget_score = round(budget_score * 2) / 2
    phase_score = round(phase_score * 2) / 2
    risk_score = round(risk_score * 2) / 2
    
    score = budget_score + phase_score + risk_score
    
    feedback = {
        "budget_calculations": {
            "score": budget_score,
            "max_score": 15,
            "feedback": budget_feedback
        },
        "phase_breakdown": {
            "score": phase_score,
            "max_score": 10,
            "feedback": phase_feedback
        },
        "budget_risks": {
            "score": risk_score,
            "max_score": 5,
            "feedback": risk_feedback
        },
        "total_score": score,
        "max_score": 30
    }
    
    return score, feedback

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_score, task1_feedback = evaluate_task1(submission, answer_key)
    task2_score, task2_feedback = evaluate_task2(submission, answer_key)
    task3_score, task3_feedback = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    max_score = 100  # 30 + 40 + 30
    overall_percentage = (total_score / max_score) * 100
    
    # Determine if candidate passed
    passed = overall_percentage >= 70
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passed": passed,
        "task_scores": {
            "task1": task1_feedback,
            "task2": task2_feedback,
            "task3": task3_feedback
        },
        "total_points": total_score,
        "max_points": max_score,
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}% ({'PASS' if passed else 'FAIL'})")

if __name__ == "__main__":
    main()