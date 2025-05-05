#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_system_goals(submission_goals: List[Dict], answer_goals: List[Dict]) -> Dict:
    """Evaluate the system goals section of the submission."""
    results = {
        "goal_relevance": {"score": 0, "max_points": 10, "comments": []},
        "goal_completeness": {"score": 0, "max_points": 5, "comments": []},
        "prioritization": {"score": 0, "max_points": 5, "comments": []},
        "measurable_outcomes": {"score": 0, "max_points": 10, "comments": []},
        "total": 0,
        "max_points": 30
    }
    
    # Check number of goals (5-7 required)
    goal_count = len(submission_goals)
    if 5 <= goal_count <= 7:
        results["goal_completeness"]["score"] = 5
    elif 3 <= goal_count < 5:
        results["goal_completeness"]["score"] = 3
        results["goal_completeness"]["comments"].append("Fewer than 5 goals provided")
    elif goal_count > 7:
        results["goal_completeness"]["score"] = 3
        results["goal_completeness"]["comments"].append("More than 7 goals provided")
    else:
        results["goal_completeness"]["score"] = 0
        results["goal_completeness"]["comments"].append("Insufficient number of goals")
    
    # Check goal relevance
    relevant_goals = 0
    key_topics = ["standardize", "centralize", "no-show", "resource utilization", 
                 "appointment", "scheduling", "clinic", "patient"]
    
    for goal in submission_goals:
        topic_matches = sum(1 for topic in key_topics if topic.lower() in goal.get("description", "").lower())
        if topic_matches >= 2:
            relevant_goals += 1
    
    relevance_percentage = relevant_goals / max(1, len(submission_goals))
    results["goal_relevance"]["score"] = round(10 * relevance_percentage)
    if results["goal_relevance"]["score"] < 7:
        results["goal_relevance"]["comments"].append("Some goals don't directly address the scenario requirements")
    
    # Check prioritization
    has_priorities = all("priority" in goal for goal in submission_goals)
    priority_range = all(1 <= goal.get("priority", 0) <= 5 for goal in submission_goals)
    
    if has_priorities and priority_range:
        # Check if highest priority goals address core requirements
        high_priority_goals = [g for g in submission_goals if g.get("priority", 5) <= 2]
        high_priority_topics = ["standardize", "centralize", "no-show", "resource"]
        
        high_priority_matches = 0
        for goal in high_priority_goals:
            if any(topic in goal.get("description", "").lower() for topic in high_priority_topics):
                high_priority_matches += 1
        
        if high_priority_matches >= 2:
            results["prioritization"]["score"] = 5
        else:
            results["prioritization"]["score"] = 3
            results["prioritization"]["comments"].append("Prioritization doesn't emphasize core business needs")
    else:
        results["prioritization"]["score"] = 1
        results["prioritization"]["comments"].append("Missing or invalid priority values")
    
    # Check measurable outcomes
    measurable_count = 0
    for goal in submission_goals:
        outcome = goal.get("measurableOutcome", "")
        # Check if outcome contains numbers/percentages and timeframes
        has_metrics = any(char.isdigit() for char in outcome)
        has_timeframe = any(term in outcome.lower() for term in ["month", "year", "week", "day", "quarter"])
        
        if has_metrics and len(outcome.split()) >= 5:
            measurable_count += 1
            if has_timeframe:
                measurable_count += 0.5
    
    measurable_score = min(10, round(10 * measurable_count / max(1, len(submission_goals))))
    results["measurable_outcomes"]["score"] = measurable_score
    
    if measurable_score < 7:
        results["measurable_outcomes"]["comments"].append("Some outcomes lack specific, quantifiable metrics")
    
    # Calculate total score for system goals
    results["total"] = sum(category["score"] for category in results.values() if isinstance(category, dict))
    
    return results

def evaluate_constraints(submission_constraints: List[Dict], answer_constraints: List[Dict]) -> Dict:
    """Evaluate the constraints section of the submission."""
    results = {
        "constraints_identification": {"score": 0, "max_points": 5, "comments": []},
        "constraints_impact": {"score": 0, "max_points": 5, "comments": []},
        "total": 0,
        "max_points": 10
    }
    
    # Check number of constraints (exactly 3 required)
    constraint_count = len(submission_constraints)
    if constraint_count == 3:
        results["constraints_identification"]["score"] = 5
    elif 1 <= constraint_count < 3:
        results["constraints_identification"]["score"] = 3
        results["constraints_identification"]["comments"].append("Fewer than 3 constraints provided")
    elif constraint_count > 3:
        results["constraints_identification"]["score"] = 4
        results["constraints_identification"]["comments"].append("More than 3 constraints provided")
    else:
        results["constraints_identification"]["score"] = 0
        results["constraints_identification"]["comments"].append("No constraints provided")
    
    # Check constraint impacts
    impact_count = sum(1 for c in submission_constraints if "impact" in c and len(c.get("impact", "").split()) >= 5)
    
    if impact_count == constraint_count and constraint_count > 0:
        results["constraints_impact"]["score"] = 5
    elif impact_count > 0:
        results["constraints_impact"]["score"] = round(5 * impact_count / max(1, constraint_count))
        results["constraints_impact"]["comments"].append("Some constraints lack clear impact descriptions")
    else:
        results["constraints_impact"]["score"] = 0
        results["constraints_impact"]["comments"].append("Missing impact descriptions for constraints")
    
    # Calculate total score for constraints
    results["total"] = results["constraints_identification"]["score"] + results["constraints_impact"]["score"]
    
    return results

def evaluate_flowchart(submission_flowchart: Dict, answer_flowchart: Dict) -> Dict:
    """Evaluate the flowchart section of the submission."""
    results = {
        "process_completeness": {"score": 0, "max_points": 15, "comments": []},
        "error_handling": {"score": 0, "max_points": 10, "comments": []},
        "system_integration": {"score": 0, "max_points": 10, "comments": []},
        "logical_flow": {"score": 0, "max_points": 15, "comments": []},
        "symbol_usage": {"score": 0, "max_points": 5, "comments": []},
        "step_descriptions": {"score": 0, "max_points": 5, "comments": []},
        "total": 0,
        "max_points": 60
    }
    
    flowchart_steps = submission_flowchart.get("flowchartSteps", [])
    
    # Check process completeness
    has_start = any(step.get("stepType") == "start" for step in flowchart_steps)
    has_end = any(step.get("stepType") == "end" for step in flowchart_steps)
    step_count = len(flowchart_steps)
    
    # Key process elements to check for
    key_processes = [
        "appointment request", "patient information", "available", "select", "confirm", 
        "reminder", "cancel", "reschedule", "complete", "no-show"
    ]
    
    process_elements_found = 0
    for process in key_processes:
        if any(process.lower() in step.get("description", "").lower() for step in flowchart_steps):
            process_elements_found += 1
    
    process_coverage = process_elements_found / len(key_processes)
    
    if has_start and has_end and step_count >= 15:
        if process_coverage >= 0.8:
            results["process_completeness"]["score"] = 15
        elif process_coverage >= 0.6:
            results["process_completeness"]["score"] = 12
            results["process_completeness"]["comments"].append("Missing some key process elements")
        elif process_coverage >= 0.4:
            results["process_completeness"]["score"] = 8
            results["process_completeness"]["comments"].append("Missing many key process elements")
        else:
            results["process_completeness"]["score"] = 5
            results["process_completeness"]["comments"].append("Incomplete process coverage")
    else:
        if not has_start or not has_end:
            results["process_completeness"]["comments"].append("Missing start or end steps")
        if step_count < 15:
            results["process_completeness"]["comments"].append(f"Insufficient steps ({step_count}/15 minimum)")
        results["process_completeness"]["score"] = max(3, round(10 * process_coverage))
    
    # Check error handling
    decision_steps = [step for step in flowchart_steps if step.get("stepType") == "decision"]
    error_handling_keywords = ["error", "invalid", "not available", "unavailable", "no-show", "cancel", "reschedule", "fail"]
    
    error_handling_paths = 0
    for step in decision_steps:
        description = step.get("description", "").lower()
        if any(keyword in description for keyword in error_handling_keywords) or "?" in description:
            if len(step.get("nextStepIds", [])) >= 2:
                error_handling_paths += 1
    
    if error_handling_paths >= 3:
        results["error_handling"]["score"] = 10
    elif error_handling_paths == 2:
        results["error_handling"]["score"] = 7
        results["error_handling"]["comments"].append("Limited error handling scenarios")
    elif error_handling_paths == 1:
        results["error_handling"]["score"] = 4
        results["error_handling"]["comments"].append("Only one error handling scenario found")
    else:
        results["error_handling"]["score"] = 0
        results["error_handling"]["comments"].append("No error handling scenarios found")
    
    # Check system integration
    database_steps = [step for step in flowchart_steps if step.get("stepType") == "database"]
    integration_keywords = ["database", "system", "EHR", "record", "retrieve", "store", "save", "query"]
    
    integration_points = 0
    for step in database_steps:
        if any(keyword.lower() in step.get("description", "").lower() for keyword in integration_keywords):
            integration_points += 1
    
    # Also check process steps that might mention integration
    for step in flowchart_steps:
        if step.get("stepType") != "database" and any(f"from {kw}" in step.get("description", "").lower() or 
                                                     f"to {kw}" in step.get("description", "").lower() 
                                                     for kw in ["EHR", "system", "database"]):
            integration_points += 0.5
    
    integration_points = min(4, integration_points)
    
    if integration_points >= 2:
        results["system_integration"]["score"] = 10
    elif integration_points >= 1:
        results["system_integration"]["score"] = 5
        results["system_integration"]["comments"].append("Limited system integration points")
    else:
        results["system_integration"]["score"] = 0
        results["system_integration"]["comments"].append("No clear system integration points")
    
    # Check logical flow
    # Build a graph of the flowchart to check connectivity
    step_ids = {step.get("stepId"): step for step in flowchart_steps}
    reachable_steps = set()
    
    # Start from the start node
    start_nodes = [step.get("stepId") for step in flowchart_steps if step.get("stepType") == "start"]
    if start_nodes:
        to_visit = [start_nodes[0]]
        while to_visit:
            current = to_visit.pop(0)
            if current in reachable_steps:
                continue
            reachable_steps.add(current)
            
            current_step = step_ids.get(current)
            if current_step:
                for next_id in current_step.get("nextStepIds", []):
                    if next_id not in reachable_steps:
                        to_visit.append(next_id)
    
    # Check if all steps are reachable
    unreachable = set(step_ids.keys()) - reachable_steps
    
    # Check if decision nodes have exactly two next steps
    decision_issues = 0
    for step in decision_steps:
        if len(step.get("nextStepIds", [])) != 2:
            decision_issues += 1
    
    # Check for invalid nextStepIds
    invalid_refs = 0
    for step in flowchart_steps:
        for next_id in step.get("nextStepIds", []):
            if next_id not in step_ids:
                invalid_refs += 1
    
    if not unreachable and decision_issues == 0 and invalid_refs == 0:
        results["logical_flow"]["score"] = 15
    elif len(unreachable) <= 2 and decision_issues <= 1 and invalid_refs <= 1:
        results["logical_flow"]["score"] = 10
        if unreachable:
            results["logical_flow"]["comments"].append(f"Some steps are unreachable: {', '.join(unreachable)}")
        if decision_issues:
            results["logical_flow"]["comments"].append("Some decision steps don't have exactly two paths")
        if invalid_refs:
            results["logical_flow"]["comments"].append("Some nextStepIds reference non-existent steps")
    else:
        results["logical_flow"]["score"] = 5
        results["logical_flow"]["comments"].append("Significant issues with flow connectivity")
    
    # Check symbol usage
    required_symbols = {
        "start": 1,
        "end": 1,
        "decision": 3,
        "database": 1,
        "input/output": 2,
        "process": 1
    }
    
    symbol_counts = {}
    for step in flowchart_steps:
        step_type = step.get("stepType", "")
        symbol_counts[step_type] = symbol_counts.get(step_type, 0) + 1
    
    symbol_issues = []
    for symbol, required_count in required_symbols.items():
        if symbol_counts.get(symbol, 0) < required_count:
            symbol_issues.append(f"Not enough {symbol} steps (found {symbol_counts.get(symbol, 0)}, need {required_count})")
    
    if not symbol_issues:
        results["symbol_usage"]["score"] = 5
    elif len(symbol_issues) <= 2:
        results["symbol_usage"]["score"] = 3
        results["symbol_usage"]["comments"].extend(symbol_issues)
    else:
        results["symbol_usage"]["score"] = 1
        results["symbol_usage"]["comments"].extend(symbol_issues[:3])
        if len(symbol_issues) > 3:
            results["symbol_usage"]["comments"].append(f"...and {len(symbol_issues) - 3} more symbol issues")
    
    # Check step descriptions
    clear_descriptions = 0
    for step in flowchart_steps:
        description = step.get("description", "")
        words = description.split()
        if 5 <= len(words) <= 30 and description[0].isupper():
            clear_descriptions += 1
    
    description_quality = clear_descriptions / max(1, len(flowchart_steps))
    
    if description_quality >= 0.9:
        results["step_descriptions"]["score"] = 5
    elif description_quality >= 0.7:
        results["step_descriptions"]["score"] = 4
        results["step_descriptions"]["comments"].append("Some step descriptions could be clearer or more concise")
    elif description_quality >= 0.5:
        results["step_descriptions"]["score"] = 3
        results["step_descriptions"]["comments"].append("Many step descriptions need improvement")
    else:
        results["step_descriptions"]["score"] = 1
        results["step_descriptions"]["comments"].append("Most step descriptions are inadequate")
    
    # Calculate total score for flowchart
    results["total"] = sum(category["score"] for category in results.values() if isinstance(category, dict))
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "task1": {
            "systemGoals": evaluate_system_goals(
                submission.get("task1", {}).get("systemGoals", []),
                answer_key.get("task1", {}).get("systemGoals", [])
            ),
            "constraints": evaluate_constraints(
                submission.get("task1", {}).get("constraints", []),
                answer_key.get("task1", {}).get("constraints", [])
            ),
            "total": 0,
            "max_points": 40
        },
        "task2": evaluate_flowchart(
            submission.get("task2", {}),
            answer_key.get("task2", {})
        ),
        "critical_elements": {
            "has_5_goals": False,
            "has_3_constraints": False,
            "has_15_steps": False,
            "has_3_error_scenarios": False,
            "has_2_integration_points": False,
            "all_present": False
        },
        "overall_score": 0,
        "max_points": 100,
        "passed": False
    }
    
    # Calculate task1 total
    results["task1"]["total"] = results["task1"]["systemGoals"]["total"] + results["task1"]["constraints"]["total"]
    
    # Calculate overall score
    results["overall_score"] = results["task1"]["total"] + results["task2"]["total"]
    
    # Check critical elements
    results["critical_elements"]["has_5_goals"] = len(submission.get("task1", {}).get("systemGoals", [])) >= 5
    results["critical_elements"]["has_3_constraints"] = len(submission.get("task1", {}).get("constraints", [])) >= 3
    results["critical_elements"]["has_15_steps"] = len(submission.get("task2", {}).get("flowchartSteps", [])) >= 15
    
    # Error scenarios (from error_handling evaluation)
    error_handling_score = results["task2"]["error_handling"]["score"]
    results["critical_elements"]["has_3_error_scenarios"] = error_handling_score >= 7  # Score of 7+ means at least 2 scenarios
    
    # Integration points (from system_integration evaluation)
    integration_score = results["task2"]["system_integration"]["score"]
    results["critical_elements"]["has_2_integration_points"] = integration_score >= 5  # Score of 5+ means at least 1 integration point
    
    # Check if all critical elements are present
    results["critical_elements"]["all_present"] = all(
        value for key, value in results["critical_elements"].items() if key != "all_present"
    )
    
    # Calculate percentage score
    percentage_score = (results["overall_score"] / results["max_points"]) * 100
    results["percentage_score"] = round(percentage_score, 1)
    
    # Check if passed (75% overall and 70% on each task)
    task1_percentage = (results["task1"]["total"] / results["task1"]["max_points"]) * 100
    task2_percentage = (results["task2"]["total"] / results["task2"]["max_points"]) * 100
    
    results["passed"] = (
        percentage_score >= 75 and
        task1_percentage >= 70 and
        task2_percentage >= 70 and
        results["critical_elements"]["all_present"]
    )
    
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
    print(f"Overall score: {results['percentage_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()