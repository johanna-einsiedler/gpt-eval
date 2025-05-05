#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_retention_recommendations(submission, answer_key):
    """Evaluate Task 1: Retention Recommendations."""
    points = 0
    max_points = 6
    feedback = []
    
    # Create sets of teacher IDs for comparison
    submission_ids = {item["teacher_id"] for item in submission}
    answer_key_ids = {item["teacher_id"] for item in answer_key}
    
    # Check each teacher ID
    for teacher in answer_key:
        teacher_id = teacher["teacher_id"]
        if teacher_id in submission_ids:
            points += 2
            feedback.append(f"Correctly identified {teacher_id} for non-renewal.")
        else:
            feedback.append(f"Failed to identify {teacher_id} for non-renewal.")
    
    # Check for incorrect additions
    for teacher_id in submission_ids - answer_key_ids:
        feedback.append(f"Incorrectly included {teacher_id} for non-renewal.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_reassignment_recommendations(submission, answer_key):
    """Evaluate Task 1: Reassignment Recommendations."""
    points = 0
    max_points = 6
    feedback = []
    
    # Create dictionaries for easier comparison
    submission_dict = {item["teacher_id"]: item for item in submission}
    answer_key_dict = {item["teacher_id"]: item for item in answer_key}
    
    # Check each teacher ID
    for teacher_id, answer in answer_key_dict.items():
        if teacher_id in submission_dict:
            submission_item = submission_dict[teacher_id]
            
            # Check if current and recommended programs match
            if (submission_item["current_program"] == answer["current_program"] and 
                submission_item["recommended_program"] == answer["recommended_program"]):
                points += 2
                feedback.append(f"Correctly identified {teacher_id} for reassignment from {answer['current_program']} to {answer['recommended_program']}.")
                
                # Check rationale
                if any(keyword in submission_item["rationale"].lower() for keyword in ["performance", "evaluation", "score", "growth"]):
                    points += 1
                    feedback.append(f"Provided appropriate rationale for {teacher_id} reassignment.")
                else:
                    feedback.append(f"Rationale for {teacher_id} reassignment lacks performance-based justification.")
            else:
                feedback.append(f"Incorrect program reassignment for {teacher_id}.")
        else:
            feedback.append(f"Failed to identify {teacher_id} for reassignment.")
    
    # Check for incorrect additions
    for teacher_id in submission_dict.keys() - answer_key_dict.keys():
        feedback.append(f"Incorrectly included {teacher_id} for reassignment.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_priority_hiring_needs(submission, answer_key):
    """Evaluate Task 1: Priority Hiring Needs."""
    points = 0
    max_points = 8
    feedback = []
    
    # Create sets of subject areas for comparison
    submission_subjects = {item["subject_area"].lower() for item in submission}
    answer_key_subjects = {item["subject_area"].lower() for item in answer_key}
    
    # Check each subject area
    for item in answer_key:
        subject = item["subject_area"].lower()
        if subject in submission_subjects:
            points += 2
            feedback.append(f"Correctly identified {item['subject_area']} as a priority hiring need.")
            
            # Check if justification connects to retention/reassignment decisions
            submission_item = next((s for s in submission if s["subject_area"].lower() == subject), None)
            if submission_item and any(teacher_id in submission_item["justification"] 
                                      for teacher_id in ["T118", "T205", "T401", "T287", "T298"]):
                points += 0.67  # Approximately 2 points divided by 3 subjects
                feedback.append(f"Justification for {item['subject_area']} correctly references specific teachers.")
            else:
                feedback.append(f"Justification for {item['subject_area']} lacks connection to specific teacher recommendations.")
        else:
            feedback.append(f"Failed to identify {item['subject_area']} as a priority hiring need.")
    
    # Round points to nearest integer
    points = round(points)
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_staffing_plan(submission, answer_key):
    """Evaluate Task 2: Staffing Plan."""
    points = 0
    max_points = 7
    feedback = []
    
    # Create dictionaries for easier comparison
    submission_dict = {item["position_code"]: item for item in submission}
    answer_key_dict = {item["position_code"]: item for item in answer_key}
    
    # Check each position
    for position_code, answer in answer_key_dict.items():
        if position_code in submission_dict:
            submission_item = submission_dict[position_code]
            
            # Check if FTE matches
            if submission_item["fte"] == answer["fte"]:
                points += 1
                feedback.append(f"Correctly included {position_code} with {answer['fte']} FTE.")
            else:
                feedback.append(f"Incorrect FTE for {position_code}. Expected {answer['fte']}, got {submission_item['fte']}.")
        else:
            feedback.append(f"Failed to include {position_code} in staffing plan.")
    
    # Check for incorrect additions
    for position_code in submission_dict.keys() - answer_key_dict.keys():
        feedback.append(f"Incorrectly included {position_code} in staffing plan.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_budget_allocation(submission, answer_key):
    """Evaluate Task 2: Budget Allocation."""
    points = 0
    max_points = 8
    feedback = []
    
    # Check budget breakdown
    if submission["personnel_total"] == answer_key["personnel_total"]:
        points += 1
        feedback.append("Correctly allocated personnel budget.")
    else:
        feedback.append(f"Incorrect personnel budget. Expected {answer_key['personnel_total']}, got {submission['personnel_total']}.")
    
    if submission["equipment_supplies"] == answer_key["equipment_supplies"]:
        points += 1
        feedback.append("Correctly allocated equipment and supplies budget.")
    else:
        feedback.append(f"Incorrect equipment and supplies budget. Expected {answer_key['equipment_supplies']}, got {submission['equipment_supplies']}.")
    
    if submission["professional_development"] == answer_key["professional_development"]:
        points += 1
        feedback.append("Correctly allocated professional development budget.")
    else:
        feedback.append(f"Incorrect professional development budget. Expected {answer_key['professional_development']}, got {submission['professional_development']}.")
    
    # Check budget shortfall identification
    if "adjustments_needed" in submission and submission["adjustments_needed"]:
        if any(keyword in submission["adjustments_needed"].lower() for keyword in 
              ["exceed", "shortfall", "insufficient", "over budget", "phase", "reduce"]):
            points += 5
            feedback.append("Correctly identified and explained the budget shortfall.")
        else:
            points += 2
            feedback.append("Mentioned adjustments needed but did not clearly explain the budget shortfall.")
    else:
        feedback.append("Failed to identify the budget shortfall.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_implementation_timeline(submission, answer_key):
    """Evaluate Task 2: Implementation Timeline."""
    points = 0
    max_points = 5
    feedback = []
    
    # Check dates
    correct_dates = True
    submission_dict = {item["milestone"]: item for item in submission}
    answer_key_dict = {item["milestone"]: item for item in answer_key}
    
    for milestone, answer in answer_key_dict.items():
        if milestone in submission_dict:
            if submission_dict[milestone]["date"] != answer["date"]:
                correct_dates = False
                feedback.append(f"Incorrect date for {milestone}. Expected {answer['date']}, got {submission_dict[milestone]['date']}.")
        else:
            correct_dates = False
            feedback.append(f"Missing milestone: {milestone}")
    
    if correct_dates:
        points += 1
        feedback.append("All milestone dates are correct.")
    
    # Check action items
    action_items_score = 0
    for milestone, answer in answer_key_dict.items():
        if milestone in submission_dict and "action_items" in submission_dict[milestone]:
            if submission_dict[milestone]["action_items"]:
                action_items_score += 1
                if len(submission_dict[milestone]["action_items"]) > 10:  # Simple check for meaningful content
                    action_items_score += 0.5
    
    action_points = min(4, round(action_items_score))
    points += action_points
    
    if action_points >= 3:
        feedback.append("Provided appropriate action items for most milestones.")
    elif action_points >= 1:
        feedback.append("Provided some action items but lacking detail or missing for some milestones.")
    else:
        feedback.append("Failed to provide meaningful action items for milestones.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_action_recommendation(submission, answer_key):
    """Evaluate Task 3: Action Recommendation."""
    points = 0
    max_points = 3
    feedback = []
    
    if submission.lower() == answer_key.lower():
        points = 3
        feedback.append("Correctly recommended 'Performance improvement plan'.")
    else:
        feedback.append(f"Incorrect action recommendation. Expected '{answer_key}', got '{submission}'.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_policy_references(submission, answer_key):
    """Evaluate Task 3: Policy References."""
    points = 0
    max_points = 3
    feedback = []
    
    # Create sets for comparison
    submission_set = set(submission)
    answer_key_set = set(answer_key)
    
    # Check each policy reference
    for policy in answer_key_set:
        if policy in submission_set:
            points += 1.5
            feedback.append(f"Correctly cited policy reference {policy}.")
        else:
            feedback.append(f"Failed to cite policy reference {policy}.")
    
    # Check for incorrect additions
    for policy in submission_set - answer_key_set:
        feedback.append(f"Incorrectly included policy reference {policy}.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def evaluate_documentation_requirements(submission, answer_key):
    """Evaluate Task 3: Documentation Requirements."""
    points = 0
    max_points = 4
    feedback = []
    
    # Create dictionaries for easier comparison
    submission_dict = {item["requirement_id"]: item for item in submission}
    answer_key_dict = {item["requirement_id"]: item for item in answer_key}
    
    # Check each requirement
    for req_id in answer_key_dict:
        if req_id in submission_dict:
            points += 0.5
            feedback.append(f"Correctly included documentation requirement {req_id}.")
        else:
            feedback.append(f"Failed to include documentation requirement {req_id}.")
    
    # Check for incorrect additions
    for req_id in submission_dict.keys() - answer_key_dict.keys():
        feedback.append(f"Incorrectly included documentation requirement {req_id}.")
    
    return {
        "points": points,
        "max_points": max_points,
        "feedback": feedback
    }

def check_critical_elements(results):
    """Check if critical elements are satisfied."""
    critical_elements = {
        "identified_low_performers": False,
        "recognized_budget_shortfall": False,
        "correct_action_for_chen": False
    }
    
    # Check if at least 2 of 3 lowest-performing teachers were identified
    retention_points = results["task1"]["retention_recommendations"]["points"]
    if retention_points >= 4:  # At least 2 out of 3 teachers (2 points each)
        critical_elements["identified_low_performers"] = True
    
    # Check if budget shortfall was recognized
    budget_feedback = results["task2"]["budget_allocation"]["feedback"]
    if any("shortfall" in fb.lower() or "exceed" in fb.lower() for fb in budget_feedback):
        critical_elements["recognized_budget_shortfall"] = True
    
    # Check if correct action for Robert Chen was recommended
    action_points = results["task3"]["action_recommendation"]["points"]
    if action_points == 3:  # Full points for correct action
        critical_elements["correct_action_for_chen"] = True
    
    return critical_elements

def calculate_overall_score(results):
    """Calculate the overall score as a percentage."""
    total_points = 0
    max_points = 0
    
    # Sum up points from all sections
    for task, task_results in results.items():
        if task.startswith("task"):
            for section, section_results in task_results.items():
                if isinstance(section_results, dict) and "points" in section_results:
                    total_points += section_results["points"]
                    max_points += section_results["max_points"]
    
    # Calculate percentage
    percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    return round(percentage, 1)

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "task1": {
            "retention_recommendations": evaluate_retention_recommendations(
                submission["task1"]["retention_recommendations"],
                answer_key["task1"]["retention_recommendations"]
            ),
            "reassignment_recommendations": evaluate_reassignment_recommendations(
                submission["task1"]["reassignment_recommendations"],
                answer_key["task1"]["reassignment_recommendations"]
            ),
            "priority_hiring_needs": evaluate_priority_hiring_needs(
                submission["task1"]["priority_hiring_needs"],
                answer_key["task1"]["priority_hiring_needs"]
            )
        },
        "task2": {
            "staffing_plan": evaluate_staffing_plan(
                submission["task2"]["staffing_plan"],
                answer_key["task2"]["staffing_plan"]
            ),
            "budget_allocation": evaluate_budget_allocation(
                submission["task2"]["budget_allocation"],
                answer_key["task2"]["budget_allocation"]
            ),
            "implementation_timeline": evaluate_implementation_timeline(
                submission["task2"]["implementation_timeline"],
                answer_key["task2"]["implementation_timeline"]
            )
        },
        "task3": {
            "action_recommendation": evaluate_action_recommendation(
                submission["task3"]["action_recommendation"],
                answer_key["task3"]["action_recommendation"]
            ),
            "policy_references": evaluate_policy_references(
                submission["task3"]["policy_references"],
                answer_key["task3"]["policy_references"]
            ),
            "documentation_requirements": evaluate_documentation_requirements(
                submission["task3"]["documentation_requirements"],
                answer_key["task3"]["documentation_requirements"]
            )
        }
    }
    
    # Check critical elements
    results["critical_elements"] = check_critical_elements(results)
    
    # Calculate overall score
    results["overall_score"] = calculate_overall_score(results)
    
    # Determine if passed (80% or higher and all critical elements satisfied)
    passed = (results["overall_score"] >= 80 and 
              all(results["critical_elements"].values()))
    
    results["passed"] = passed
    
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
    
    # Save results
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()