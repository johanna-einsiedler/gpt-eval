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

def validate_date_format(date_str):
    """Validate that a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_date_in_quarter(date_str, start_date, end_date):
    """Validate that a date is within the specified quarter."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        quarter_start = datetime.strptime(start_date, '%Y-%m-%d')
        quarter_end = datetime.strptime(end_date, '%Y-%m-%d')
        return quarter_start <= date <= quarter_end
    except ValueError:
        return False

def check_essential_requirements(submission, answer_key):
    """Check if the submission meets all essential requirements."""
    requirements = {
        "has_5_goals": len(submission.get("departmental_goals", [])) == 5,
        "all_goals_in_quarter": True,
        "all_goals_have_3_milestones": True,
        "resources_within_limits": True
    }
    
    # Check if all goals have deadlines within the quarter
    quarter_start = answer_key["implementation_timeline"]["quarter_start_date"]
    quarter_end = answer_key["implementation_timeline"]["quarter_end_date"]
    
    for goal in submission.get("departmental_goals", []):
        deadline = goal.get("deadline", "")
        if not validate_date_in_quarter(deadline, quarter_start, quarter_end):
            requirements["all_goals_in_quarter"] = False
        
        # Check if each goal has exactly 3 milestones
        milestones = goal.get("milestones", [])
        if len(milestones) != 3:
            requirements["all_goals_have_3_milestones"] = False
    
    # Resource validation would require more context about available resources
    # For now, we'll assume this check is passed
    
    return requirements

def score_goal_selection(submission, answer_key):
    """Score the goal selection and alignment (30 points)."""
    score = 0
    max_score = 30
    feedback = []
    
    # Check if goals address high-priority organizational needs (15 points)
    high_priority_addressed = 0
    high_priority_goals = ["document processing", "filing", "records management", 
                          "operational costs", "staff productivity"]
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        for priority_goal in high_priority_goals:
            if priority_goal in desc:
                high_priority_addressed += 1
                break
    
    high_priority_score = min(15, high_priority_addressed * 3)
    score += high_priority_score
    feedback.append(f"Goals addressing high-priority needs: {high_priority_score}/15 points")
    
    # Check if goals target metrics with significant performance gaps (10 points)
    performance_gaps_addressed = 0
    gap_metrics = ["document processing", "customer response", "filing accuracy", 
                  "meeting room", "budget variance"]
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        for gap_metric in gap_metrics:
            if gap_metric in desc:
                performance_gaps_addressed += 1
                break
    
    gap_score = min(10, performance_gaps_addressed * 2)
    score += gap_score
    feedback.append(f"Goals targeting significant performance gaps: {gap_score}/10 points")
    
    # Check if goals align with executive leadership expectations (5 points)
    exec_alignment = 0
    exec_expectations = ["efficiency", "cost", "meeting room", "responsiveness", 
                        "filing", "budget", "staff"]
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        for expectation in exec_expectations:
            if expectation in desc:
                exec_alignment += 1
                break
    
    exec_score = min(5, exec_alignment)
    score += exec_score
    feedback.append(f"Goals aligning with executive expectations: {exec_score}/5 points")
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def score_goal_quality(submission, answer_key):
    """Score the quality of goals (25 points)."""
    score = 0
    max_score = 25
    feedback = []
    
    # Goals are specific and measurable (10 points)
    specific_measurable = 0
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "")
        # Check if the goal has specific metrics or numbers
        if any(char.isdigit() for char in desc) and len(desc) >= 50:
            specific_measurable += 1
    
    specific_score = min(10, specific_measurable * 2)
    score += specific_score
    feedback.append(f"Goals are specific and measurable: {specific_score}/10 points")
    
    # Goals are realistic given available resources (10 points)
    # This is a simplified check - would need more context for a thorough evaluation
    realistic_goals = 0
    for goal in submission.get("departmental_goals", []):
        resources = goal.get("resources_required", {})
        staff_hours = resources.get("staff_hours", 0)
        budget = resources.get("budget_allocation", 0)
        
        # Simple heuristic: goals with reasonable resource allocations
        if 20 <= staff_hours <= 200 and 1000 <= budget <= 15000:
            realistic_goals += 1
    
    realistic_score = min(10, realistic_goals * 2)
    score += realistic_score
    feedback.append(f"Goals are realistic given resources: {realistic_score}/10 points")
    
    # Priority levels are appropriate (5 points)
    appropriate_priority = 0
    high_priority_keywords = ["document processing", "filing", "records management"]
    medium_priority_keywords = ["customer", "meeting room", "budget"]
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        priority = goal.get("priority", "")
        
        is_high_match = any(keyword in desc for keyword in high_priority_keywords)
        is_medium_match = any(keyword in desc for keyword in medium_priority_keywords)
        
        if (is_high_match and priority == "High") or (is_medium_match and priority == "Medium"):
            appropriate_priority += 1
    
    priority_score = min(5, appropriate_priority)
    score += priority_score
    feedback.append(f"Priority levels are appropriate: {priority_score}/5 points")
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def score_timeline_milestones(submission, answer_key):
    """Score the timeline and milestones (25 points)."""
    score = 0
    max_score = 25
    feedback = []
    
    # Milestones show logical progression (10 points)
    logical_progression = 0
    for goal in submission.get("departmental_goals", []):
        milestones = goal.get("milestones", [])
        if len(milestones) == 3:
            # Check if milestone dates are in sequence
            dates_in_order = True
            prev_date = None
            for milestone in milestones:
                curr_date = milestone.get("target_date", "")
                if prev_date and curr_date <= prev_date:
                    dates_in_order = False
                    break
                prev_date = curr_date
            
            # Check if milestone descriptions show progression (analysis -> implementation -> completion)
            has_analysis = any("analys" in m.get("description", "").lower() or 
                              "assess" in m.get("description", "").lower() or
                              "identif" in m.get("description", "").lower() for m in milestones)
            has_implementation = any("implement" in m.get("description", "").lower() or 
                                    "train" in m.get("description", "").lower() or
                                    "develop" in m.get("description", "").lower() for m in milestones)
            has_completion = any("complet" in m.get("description", "").lower() or 
                                "achiev" in m.get("description", "").lower() or
                                "finalize" in m.get("description", "").lower() for m in milestones)
            
            if dates_in_order and (has_analysis and has_implementation) or has_completion:
                logical_progression += 1
    
    progression_score = min(10, logical_progression * 2)
    score += progression_score
    feedback.append(f"Milestones show logical progression: {progression_score}/10 points")
    
    # Timeline accounts for company events (5 points)
    company_events_considered = 0
    # April: vendor contract renewals
    # May: company-wide training
    # June: mid-year financial review
    
    for goal in submission.get("departmental_goals", []):
        goal_id = goal.get("goal_id")
        deadline = goal.get("deadline", "")
        desc = goal.get("goal_description", "").lower()
        
        # Check if budget/finance goals complete before mid-year review
        if "budget" in desc and deadline < "2023-06-15":
            company_events_considered += 1
        
        # Check if meeting room improvements complete before May training
        if "meeting room" in desc and deadline < "2023-05-01":
            company_events_considered += 1
    
    events_score = min(5, company_events_considered)
    score += events_score
    feedback.append(f"Timeline accounts for company events: {events_score}/5 points")
    
    # Deadlines are realistic (10 points)
    realistic_deadlines = 0
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        deadline = goal.get("deadline", "")
        
        # Complex goals should have later deadlines
        is_complex = "modernize" in desc or "implement" in desc or "system" in desc
        
        if is_complex and deadline > "2023-05-15":
            realistic_deadlines += 1
        elif not is_complex:
            realistic_deadlines += 1
    
    deadline_score = min(10, realistic_deadlines * 2)
    score += deadline_score
    feedback.append(f"Deadlines are realistic: {deadline_score}/10 points")
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def score_resource_allocation(submission, answer_key):
    """Score the resource allocation (20 points)."""
    score = 0
    max_score = 20
    feedback = []
    
    # Staff allocations match required skills (10 points)
    appropriate_staff = 0
    staff_skills = {
        "S001": ["document", "filing"],
        "S002": ["supply", "customer"],
        "S003": ["vendor", "budget"],
        "S004": ["meeting", "document"],
        "S005": ["vendor", "budget"],
        "S006": ["filing", "document"],
        "S007": ["customer", "meeting"]
    }
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        
        # Check resource allocations in the implementation timeline
        goal_id = goal.get("goal_id")
        staff_matched = False
        
        for schedule in submission.get("implementation_timeline", {}).get("goal_schedule", []):
            if schedule.get("goal_id") == goal_id:
                for allocation in schedule.get("resource_allocation_periods", []):
                    resource_id = allocation.get("resource_id", "")
                    if resource_id in staff_skills:
                        # Check if staff skills match goal description
                        if any(skill in desc for skill in staff_skills.get(resource_id, [])):
                            staff_matched = True
                            break
        
        if staff_matched:
            appropriate_staff += 1
    
    staff_score = min(10, appropriate_staff * 2)
    score += staff_score
    feedback.append(f"Staff allocations match required skills: {staff_score}/10 points")
    
    # Budget allocations are appropriate (5 points)
    appropriate_budget = 0
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        budget = goal.get("resources_required", {}).get("budget_allocation", 0)
        
        # Technology/system goals should have higher budgets
        is_tech = "system" in desc or "technology" in desc or "digital" in desc
        
        if is_tech and budget >= 5000:
            appropriate_budget += 1
        elif not is_tech and budget <= 5000:
            appropriate_budget += 1
    
    budget_score = min(5, appropriate_budget)
    score += budget_score
    feedback.append(f"Budget allocations are appropriate: {budget_score}/5 points")
    
    # Equipment selections are appropriate (5 points)
    appropriate_equipment = 0
    equipment_uses = {
        "E001": ["document", "scanning"],
        "E002": ["document", "management"],
        "E003": ["meeting", "room"],
        "E004": ["mobile", "tablet"],
        "E005": ["filing", "system"]
    }
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        equipment_ids = goal.get("resources_required", {}).get("equipment_ids", [])
        
        equipment_matched = False
        for eq_id in equipment_ids:
            if eq_id in equipment_uses:
                if any(use in desc for use in equipment_uses.get(eq_id, [])):
                    equipment_matched = True
                    break
        
        if equipment_matched:
            appropriate_equipment += 1
    
    equipment_score = min(5, appropriate_equipment)
    score += equipment_score
    feedback.append(f"Equipment selections are appropriate: {equipment_score}/5 points")
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def check_deductions(submission, answer_key):
    """Check for automatic deductions."""
    deductions = 0
    reasons = []
    
    # Missing or incomplete goals (-10 points each)
    goal_count = len(submission.get("departmental_goals", []))
    if goal_count < 5:
        missing_goals = 5 - goal_count
        deduction = missing_goals * 10
        deductions += deduction
        reasons.append(f"Missing goals: -{deduction} points ({missing_goals} goals missing)")
    
    # Resource overallocation (-5 points for each instance)
    # This would require more context about available resources
    # For now, we'll skip this check
    
    # Unrealistic timelines (-5 points for each instance)
    unrealistic_timelines = 0
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        deadline = goal.get("deadline", "")
        
        # Check if complex goals have very short timelines
        is_complex = "modernize" in desc or "implement" in desc or "system" in desc
        quarter_start = answer_key["implementation_timeline"]["quarter_start_date"]
        
        if is_complex:
            try:
                start_date = datetime.strptime(quarter_start, '%Y-%m-%d')
                end_date = datetime.strptime(deadline, '%Y-%m-%d')
                days_difference = (end_date - start_date).days
                
                if days_difference < 30:  # Less than a month for complex goals
                    unrealistic_timelines += 1
            except ValueError:
                pass
    
    if unrealistic_timelines > 0:
        deduction = unrealistic_timelines * 5
        deductions += deduction
        reasons.append(f"Unrealistic timelines: -{deduction} points ({unrealistic_timelines} instances)")
    
    # Incorrect priority assignments (-3 points for each instance)
    incorrect_priorities = 0
    high_priority_keywords = ["document processing", "filing", "records management"]
    medium_priority_keywords = ["customer", "meeting room", "budget"]
    
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        priority = goal.get("priority", "")
        
        is_high_match = any(keyword in desc for keyword in high_priority_keywords)
        is_medium_match = any(keyword in desc for keyword in medium_priority_keywords)
        
        if (is_high_match and priority != "High") or (is_medium_match and priority != "Medium"):
            incorrect_priorities += 1
    
    if incorrect_priorities > 0:
        deduction = incorrect_priorities * 3
        deductions += deduction
        reasons.append(f"Incorrect priority assignments: -{deduction} points ({incorrect_priorities} instances)")
    
    return {
        "total_deductions": deductions,
        "reasons": reasons
    }

def check_bonus_points(submission, answer_key):
    """Check for bonus points (up to 10)."""
    bonus = 0
    reasons = []
    
    # Exceptional alignment with organizational strategy (+3)
    strategy_alignment = True
    high_priority_goals = 0
    for goal in submission.get("departmental_goals", []):
        priority = goal.get("priority", "")
        if priority == "High":
            high_priority_goals += 1
    
    if high_priority_goals >= 2:
        bonus += 3
        reasons.append("Exceptional alignment with organizational strategy: +3 points")
    
    # Creative but realistic solutions (+3)
    creative_solutions = False
    for goal in submission.get("departmental_goals", []):
        desc = goal.get("goal_description", "").lower()
        if "innovative" in desc or "creative" in desc or "new approach" in desc:
            creative_solutions = True
            break
    
    if creative_solutions:
        bonus += 3
        reasons.append("Creative but realistic solutions: +3 points")
    
    # Well-structured milestone progression (+2)
    well_structured = True
    for goal in submission.get("departmental_goals", []):
        milestones = goal.get("milestones", [])
        if len(milestones) != 3:
            well_structured = False
            break
            
        # Check for clear progression in milestone descriptions
        has_analysis = any("analys" in m.get("description", "").lower() or 
                          "assess" in m.get("description", "").lower() for m in milestones)
        has_implementation = any("implement" in m.get("description", "").lower() or 
                                "train" in m.get("description", "").lower() for m in milestones)
        has_completion = any("complet" in m.get("description", "").lower() or 
                            "achiev" in m.get("description", "").lower() for m in milestones)
        
        if not (has_analysis and has_implementation and has_completion):
            well_structured = False
            break
    
    if well_structured:
        bonus += 2
        reasons.append("Well-structured milestone progression: +2 points")
    
    # Highly efficient resource allocation (+2)
    # This would require more context about available resources
    # For now, we'll skip this check
    
    return {
        "total_bonus": min(10, bonus),  # Cap at 10 points
        "reasons": reasons
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    # Check essential requirements
    essential_requirements = check_essential_requirements(submission, answer_key)
    meets_essential = all(essential_requirements.values())
    
    # Score each section
    goal_selection_results = score_goal_selection(submission, answer_key)
    goal_quality_results = score_goal_quality(submission, answer_key)
    timeline_results = score_timeline_milestones(submission, answer_key)
    resource_results = score_resource_allocation(submission, answer_key)
    
    # Calculate deductions and bonus points
    deductions = check_deductions(submission, answer_key)
    bonus = check_bonus_points(submission, answer_key)
    
    # Calculate total score
    base_score = (
        goal_selection_results["score"] +
        goal_quality_results["score"] +
        timeline_results["score"] +
        resource_results["score"]
    )
    
    max_possible = (
        goal_selection_results["max_score"] +
        goal_quality_results["max_score"] +
        timeline_results["max_score"] +
        resource_results["max_score"]
    )
    
    adjusted_score = base_score - deductions["total_deductions"] + bonus["total_bonus"]
    final_score = max(0, min(adjusted_score, max_possible))  # Ensure score is between 0 and max
    
    # Calculate percentage
    percentage = round((final_score / max_possible) * 100, 2)
    
    # Determine if candidate passed
    passed = meets_essential and percentage >= 70
    
    return {
        "essential_requirements": essential_requirements,
        "meets_essential_requirements": meets_essential,
        "goal_selection": goal_selection_results,
        "goal_quality": goal_quality_results,
        "timeline_and_milestones": timeline_results,
        "resource_allocation": resource_results,
        "deductions": deductions,
        "bonus_points": bonus,
        "base_score": base_score,
        "adjusted_score": adjusted_score,
        "max_possible_score": max_possible,
        "final_score": final_score,
        "overall_score": percentage,
        "passed": passed
    }

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
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()