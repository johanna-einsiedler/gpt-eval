#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def validate_dates(task):
    try:
        start = datetime.strptime(task["start_date"], "%Y-%m-%d")
        end = datetime.strptime(task["end_date"], "%Y-%m-%d")
        return start <= end
    except:
        return False

def check_dependency_compliance(submission):
    """Check if all task dependencies are respected"""
    task_schedule = submission["task_schedule"]
    
    # Create a dictionary of tasks with their start and end dates
    task_dates = {}
    for task in task_schedule:
        task_id = task["task_id"]
        try:
            start_date = datetime.strptime(task["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(task["end_date"], "%Y-%m-%d")
            task_dates[task_id] = {"start": start_date, "end": end_date}
        except:
            return False, f"Invalid date format in task {task_id}"
    
    # Define dependencies based on the provided materials
    dependencies = {
        "T3": ["T1"],
        "T4": ["T3"],
        "T5": ["T2"],
        "T6": ["T2"],
        "T7": ["T2", "T5"],
        "T8": ["T2"],
        "T9": ["T2"],
        "T10": ["T2", "T5"],
        "T11": ["T1", "T4"],
        "T12": ["T4"],
        "T13": ["T2", "T7"],
        "T14": ["T6", "T9"],
        "T15": ["T4", "T10", "T11"]
    }
    
    # Check if dependencies are respected
    for task_id, deps in dependencies.items():
        if task_id in task_dates:
            task_start = task_dates[task_id]["start"]
            
            for dep_id in deps:
                if dep_id in task_dates:
                    dep_end = task_dates[dep_id]["end"]
                    if task_start < dep_end:
                        return False, f"Task {task_id} starts before its dependency {dep_id} is completed"
                else:
                    # Dependency is not scheduled but the task is
                    if dep_id not in submission.get("unscheduled_tasks", []):
                        return False, f"Task {task_id} is scheduled but its dependency {dep_id} is missing"
    
    return True, "All dependencies are respected"

def check_skill_matching(submission, materials):
    """Check if tasks are assigned to team members with required skills"""
    task_schedule = submission["task_schedule"]
    
    # Extract required skills for each task
    task_skills = {}
    for row in materials["research_tasks"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 7:
                task_id = parts[0]
                required_skill = parts[6]
                task_skills[task_id] = required_skill
    
    # Extract skills for each team member
    member_skills = {}
    for row in materials["team_members"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 6:
                member_id = parts[0]
                skills = parts[5].strip('"').split(", ")
                member_skills[member_id] = skills
    
    # Check if assignments match skills
    for task in task_schedule:
        task_id = task["task_id"]
        assigned_to = task["assigned_to"]
        
        if task_id in task_skills and assigned_to in member_skills:
            required_skill = task_skills[task_id]
            if required_skill not in member_skills[assigned_to]:
                return False, f"Task {task_id} requires {required_skill} but {assigned_to} doesn't have this skill"
    
    return True, "All task assignments match team member skills"

def check_resource_allocation(submission, materials):
    """Check if team members are not overallocated"""
    # Extract available hours for each team member
    member_hours = {}
    member_dates = {}
    for row in materials["team_members"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 5:
                member_id = parts[0]
                available_hours = int(parts[2])
                start_date = parts[3]
                end_date = parts[4]
                member_hours[member_id] = available_hours
                member_dates[member_id] = {
                    "start": datetime.strptime(start_date, "%Y-%m-%d"),
                    "end": datetime.strptime(end_date, "%Y-%m-%d")
                }
    
    # Calculate total hours assigned to each team member
    assigned_hours = {}
    for task in submission["task_schedule"]:
        member_id = task["assigned_to"]
        hours = task["estimated_hours"]
        assigned_hours[member_id] = assigned_hours.get(member_id, 0) + hours
    
    # Check if any team member is overallocated
    for member_id, hours in assigned_hours.items():
        if member_id in member_hours:
            if hours > member_hours[member_id]:
                return False, f"{member_id} is overallocated: {hours} hours assigned but only {member_hours[member_id]} available"
    
    # Check if tasks are scheduled within team member availability
    for task in submission["task_schedule"]:
        member_id = task["assigned_to"]
        task_start = datetime.strptime(task["start_date"], "%Y-%m-%d")
        task_end = datetime.strptime(task["end_date"], "%Y-%m-%d")
        
        if member_id in member_dates:
            member_start = member_dates[member_id]["start"]
            member_end = member_dates[member_id]["end"]
            
            if task_start < member_start or task_end > member_end:
                return False, f"Task {task['task_id']} is scheduled outside {member_id}'s availability period"
    
    return True, "Resource allocation is within limits"

def check_schedule_conflicts(submission):
    """Check if any team member has overlapping tasks"""
    task_schedule = submission["task_schedule"]
    
    # Group tasks by team member
    member_tasks = {}
    for task in task_schedule:
        member_id = task["assigned_to"]
        if member_id not in member_tasks:
            member_tasks[member_id] = []
        
        try:
            start_date = datetime.strptime(task["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(task["end_date"], "%Y-%m-%d")
            member_tasks[member_id].append({
                "task_id": task["task_id"],
                "start": start_date,
                "end": end_date
            })
        except:
            return False, f"Invalid date format in task {task['task_id']}"
    
    # Check for overlaps
    for member_id, tasks in member_tasks.items():
        sorted_tasks = sorted(tasks, key=lambda x: x["start"])
        
        for i in range(len(sorted_tasks) - 1):
            current_end = sorted_tasks[i]["end"]
            next_start = sorted_tasks[i + 1]["start"]
            
            if current_end > next_start:
                return False, f"{member_id} has overlapping tasks: {sorted_tasks[i]['task_id']} and {sorted_tasks[i+1]['task_id']}"
    
    return True, "No schedule conflicts found"

def evaluate_high_priority_completion(submission, materials):
    """Score based on completion of high-priority tasks"""
    high_priority_tasks = []
    
    # Identify high-priority tasks
    for row in materials["research_tasks"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 5 and parts[4] == "High":
                high_priority_tasks.append(parts[0])
    
    # Count scheduled high-priority tasks
    scheduled_tasks = [task["task_id"] for task in submission["task_schedule"]]
    completed_count = sum(1 for task in high_priority_tasks if task in scheduled_tasks)
    
    # 5 points for each high-priority task scheduled (max 30)
    score = min(completed_count * 5, 30)
    
    return score, f"Scheduled {completed_count}/{len(high_priority_tasks)} high-priority tasks"

def evaluate_strategic_goal_alignment(submission, materials):
    """Score based on alignment with strategic goals G1 and G2"""
    # Parse goal-task mapping
    goal_tasks = {"G1": [], "G2": []}
    
    for row in materials["goal_task_mapping"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 2:
                goal_id = parts[0]
                task_id = parts[1]
                if goal_id in ["G1", "G2"]:
                    goal_tasks[goal_id].append(task_id)
    
    # Check which tasks are scheduled
    scheduled_tasks = [task["task_id"] for task in submission["task_schedule"]]
    
    # Calculate completion percentages
    g1_total = len(goal_tasks["G1"])
    g1_completed = sum(1 for task in goal_tasks["G1"] if task in scheduled_tasks)
    g1_percentage = (g1_completed / g1_total) if g1_total > 0 else 0
    
    g2_total = len(goal_tasks["G2"])
    g2_completed = sum(1 for task in goal_tasks["G2"] if task in scheduled_tasks)
    g2_percentage = (g2_completed / g2_total) if g2_total > 0 else 0
    
    # G1 (15 points), G2 (10 points) based on % completion
    g1_score = g1_percentage * 15
    g2_score = g2_percentage * 10
    total_score = g1_score + g2_score
    
    return total_score, f"G1: {g1_percentage:.1%} completed, G2: {g2_percentage:.1%} completed"

def evaluate_resource_utilization(submission, materials):
    """Score based on efficient use of team member hours"""
    # Extract available hours for each team member
    member_hours = {}
    for row in materials["team_members"].split("\n")[1:]:
        if row.strip():
            parts = row.split(",")
            if len(parts) >= 3:
                member_id = parts[0]
                available_hours = int(parts[2])
                member_hours[member_id] = available_hours
    
    # Calculate utilization from submission
    resource_allocation = submission.get("resource_allocation", {})
    utilization = {}
    
    for member_id, allocation in resource_allocation.items():
        if member_id in member_hours:
            total_assigned = allocation.get("total_hours_assigned", 0)
            utilization[member_id] = total_assigned / member_hours[member_id]
    
    # Score based on utilization of critical resources (TM1 and TM2)
    critical_members = ["TM1", "TM2"]
    critical_utilization = [utilization.get(member, 0) for member in critical_members]
    avg_critical_utilization = sum(critical_utilization) / len(critical_utilization) if critical_utilization else 0
    
    # Up to 15 points based on utilization (>80% for critical resources)
    score = min(avg_critical_utilization * 18.75, 15)  # 15 points at 80% utilization
    
    return score, f"Critical resource utilization: {avg_critical_utilization:.1%}"

def evaluate_dependency_management(submission):
    """Score based on proper sequencing of dependent tasks"""
    dependency_check, message = check_dependency_compliance(submission)
    
    # 10 points for proper dependency management
    score = 10 if dependency_check else 0
    
    return score, message

def evaluate_documentation_completeness(submission):
    """Score based on proper completion of all JSON fields"""
    required_fields = [
        "task_schedule", "resource_allocation", "priority_completion", 
        "unscheduled_tasks", "strategic_goal_completion", "scheduling_rationale"
    ]
    
    missing_fields = [field for field in required_fields if field not in submission]
    
    if missing_fields:
        return 0, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Check for completeness of nested fields
    score = 10  # Start with full points
    issues = []
    
    # Check task_schedule entries
    for task in submission.get("task_schedule", []):
        required_task_fields = ["task_id", "assigned_to", "start_date", "end_date", "priority", "estimated_hours"]
        missing_task_fields = [field for field in required_task_fields if field not in task]
        if missing_task_fields:
            score -= 2
            issues.append(f"Task {task.get('task_id', 'unknown')} missing fields: {', '.join(missing_task_fields)}")
            break  # Only penalize once for task issues
    
    # Check resource_allocation
    for member_id, allocation in submission.get("resource_allocation", {}).items():
        required_allocation_fields = ["total_hours_assigned", "utilization_percentage", "tasks_assigned"]
        missing_allocation_fields = [field for field in required_allocation_fields if field not in allocation]
        if missing_allocation_fields:
            score -= 2
            issues.append(f"Resource allocation for {member_id} missing fields: {', '.join(missing_allocation_fields)}")
            break  # Only penalize once for resource allocation issues
    
    # Check strategic_goal_completion
    for goal_id, completion in submission.get("strategic_goal_completion", {}).items():
        required_completion_fields = ["percentage_completed", "completed_tasks", "incomplete_tasks"]
        missing_completion_fields = [field for field in required_completion_fields if field not in completion]
        if missing_completion_fields:
            score -= 2
            issues.append(f"Strategic goal completion for {goal_id} missing fields: {', '.join(missing_completion_fields)}")
            break  # Only penalize once for goal completion issues
    
    # Check scheduling_rationale
    if "scheduling_rationale" in submission:
        if len(submission["scheduling_rationale"]) > 500:
            score -= 1
            issues.append("Scheduling rationale exceeds 500 character limit")
    
    score = max(0, score)  # Ensure score doesn't go negative
    
    return score, "Documentation is complete" if not issues else "; ".join(issues)

def evaluate_scheduling_rationale(submission):
    """Score based on quality of explanation for prioritization decisions"""
    if "scheduling_rationale" not in submission:
        return 0, "Missing scheduling rationale"
    
    rationale = submission["scheduling_rationale"]
    
    # Check for key elements in the rationale
    key_elements = [
        "priorit", "strategic goal", "dependenc", "skill", "resource", "constraint"
    ]
    
    element_count = sum(1 for element in key_elements if element in rationale.lower())
    
    # Score based on coverage of key elements (up to 10 points)
    score = min(element_count * 2, 10)
    
    return score, f"Rationale addresses {element_count}/{len(key_elements)} key elements"

def evaluate_submission(submission, answer_key, materials):
    """Evaluate the submission against the answer key and materials"""
    results = {
        "essential_requirements": {
            "dependency_compliance": check_dependency_compliance(submission),
            "skill_matching": check_skill_matching(submission, materials),
            "resource_allocation": check_resource_allocation(submission, materials),
            "schedule_conflicts": check_schedule_conflicts(submission)
        },
        "scoring": {
            "high_priority_task_completion": evaluate_high_priority_completion(submission, materials),
            "strategic_goal_alignment": evaluate_strategic_goal_alignment(submission, materials),
            "resource_utilization": evaluate_resource_utilization(submission, materials),
            "dependency_management": evaluate_dependency_management(submission),
            "documentation_completeness": evaluate_documentation_completeness(submission),
            "scheduling_rationale": evaluate_scheduling_rationale(submission)
        }
    }
    
    # Check if all essential requirements are met
    all_requirements_met = all(result[0] for result in results["essential_requirements"].values())
    
    # Calculate total score
    total_score = sum(score for score, _ in results["scoring"].values())
    
    # Apply penalty if essential requirements are not met
    if not all_requirements_met:
        total_score = min(total_score, 69)  # Cap at 69% if requirements not met
    
    results["all_requirements_met"] = all_requirements_met
    results["total_score"] = total_score
    results["overall_score"] = total_score  # As a percentage (out of 100)
    
    return results

def extract_materials(answer_key_file):
    """Extract materials from the answer key file path"""
    # This is a simplified approach - in a real scenario, you might need to parse the materials from separate files
    materials = {
        "research_tasks": """task_id,task_name,estimated_hours,deadline,priority,dependencies,required_skill
T1,Literature review on quantum algorithms,40,2023-06-15,High,,Research
T2,Develop simulation framework,60,2023-06-30,High,,Programming
T3,Data collection from experimental runs,30,2023-07-10,Medium,T1,Data Analysis
T4,Statistical analysis of results,25,2023-07-20,High,T3,Data Analysis
T5,Optimization of core algorithm,45,2023-07-15,High,T2,Programming
T6,Documentation of framework,20,2023-08-01,Medium,T2,Documentation
T7,Integration with existing systems,35,2023-07-25,Medium,"T2,T5",Programming
T8,Security audit of framework,15,2023-08-05,Low,T2,Security
T9,User interface development,30,2023-08-10,Low,T2,UI Design
T10,Performance benchmarking,20,2023-07-30,Medium,"T2,T5",Programming
T11,Prepare conference paper draft,50,2023-08-15,High,"T1,T4",Research
T12,Create visualization tools,25,2023-08-10,Medium,T4,Data Analysis
T13,Develop API documentation,15,2023-08-05,Low,"T2,T7",Documentation
T14,Conduct user testing,20,2023-08-20,Medium,"T6,T9",UI Design
T15,Prepare final research report,35,2023-08-25,High,"T4,T10,T11",Research""",
        
        "team_members": """member_id,name,available_hours,start_date,end_date,skills
TM1,Dr. Alex Chen,160,2023-06-01,2023-08-31,"Research, Data Analysis"
TM2,Maria Rodriguez,120,2023-06-01,2023-08-31,"Programming, Security"
TM3,James Wilson,140,2023-06-15,2023-08-31,"Programming, UI Design"
TM4,Sarah Johnson,100,2023-06-01,2023-07-31,"Documentation, Research" """,
        
        "strategic_goals": """goal_id,goal_description,importance
G1,Submit research findings to major conference,Very High
G2,Develop reusable framework for future projects,High
G3,Establish collaboration with industry partners,Medium
G4,Train junior researchers on new methodologies,Medium
G5,Improve documentation standards,Low""",
        
        "goal_task_mapping": """goal_id,task_id
G1,T1
G1,T3
G1,T4
G1,T11
G1,T15
G2,T2
G2,T5
G2,T7
G2,T10
G3,T9
G3,T14
G4,T6
G4,T12
G5,T6
G5,T13"""
    }
    
    return materials

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    materials = extract_materials(answer_key_file)
    
    results = evaluate_submission(submission, answer_key, materials)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()