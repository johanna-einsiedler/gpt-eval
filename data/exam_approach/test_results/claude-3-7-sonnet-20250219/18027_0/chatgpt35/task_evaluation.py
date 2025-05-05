#!/usr/bin/env python3
"""
Regulatory Affairs Manager Exam Evaluator

This script evaluates a candidate's submission against an answer key for the
Regulatory Affairs Manager practical exam, focusing on regulatory priorities,
budget allocation, and resource management.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_prioritization(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the project prioritization section."""
    results = {
        "points_earned": 0,
        "points_possible": 35,
        "details": {
            "critical_projects": {"earned": 0, "possible": 9},
            "high_projects": {"earned": 0, "possible": 8},
            "medium_projects": {"earned": 0, "possible": 5},
            "low_projects": {"earned": 0, "possible": 3},
            "primary_reasons": {"earned": 0, "possible": 10},
        },
        "feedback": []
    }
    
    # Create dictionaries for easier lookup
    submission_priorities = {item["project_id"]: item for item in submission["prioritization"]["project_ranking"]}
    answer_key_priorities = {item["project_id"]: item for item in answer_key["prioritization"]["project_ranking"]}
    
    # Check critical projects (3 points each)
    critical_projects = [pid for pid, item in answer_key_priorities.items() if item["priority_level"] == "Critical"]
    for project_id in critical_projects:
        if project_id in submission_priorities and submission_priorities[project_id]["priority_level"] == "Critical":
            results["details"]["critical_projects"]["earned"] += 3
        else:
            results["feedback"].append(f"Project {project_id} should be Critical priority")
    
    # Check high projects (2 points each)
    high_projects = [pid for pid, item in answer_key_priorities.items() if item["priority_level"] == "High"]
    for project_id in high_projects:
        if project_id in submission_priorities and submission_priorities[project_id]["priority_level"] == "High":
            results["details"]["high_projects"]["earned"] += 2
        else:
            results["feedback"].append(f"Project {project_id} should be High priority")
    
    # Check medium projects (1 point each)
    medium_projects = [pid for pid, item in answer_key_priorities.items() if item["priority_level"] == "Medium"]
    for project_id in medium_projects:
        if project_id in submission_priorities and submission_priorities[project_id]["priority_level"] == "Medium":
            results["details"]["medium_projects"]["earned"] += 1
        else:
            results["feedback"].append(f"Project {project_id} should be Medium priority")
    
    # Check low projects (1 point each)
    low_projects = [pid for pid, item in answer_key_priorities.items() if item["priority_level"] == "Low"]
    for project_id in low_projects:
        if project_id in submission_priorities and submission_priorities[project_id]["priority_level"] == "Low":
            results["details"]["low_projects"]["earned"] += 1
        else:
            results["feedback"].append(f"Project {project_id} should be Low priority")
    
    # Check primary reasons (1 point each)
    for project_id, key_item in answer_key_priorities.items():
        if (project_id in submission_priorities and 
            submission_priorities[project_id]["primary_reason"] == key_item["primary_reason"]):
            results["details"]["primary_reasons"]["earned"] += 1
        else:
            results["feedback"].append(f"Project {project_id} primary reason should be {key_item['primary_reason']}")
    
    # Calculate total points earned
    results["points_earned"] = (
        results["details"]["critical_projects"]["earned"] +
        results["details"]["high_projects"]["earned"] +
        results["details"]["medium_projects"]["earned"] +
        results["details"]["low_projects"]["earned"] +
        results["details"]["primary_reasons"]["earned"]
    )
    
    # Add pass/fail status
    results["passed"] = results["points_earned"] >= 21  # 60% of 35 points
    
    return results


def evaluate_budget_allocation(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the budget allocation section."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "details": {
            "quarterly_distribution": {"earned": 0, "possible": 5},
            "personnel_costs": {"earned": 0, "possible": 5},
            "training_allocation": {"earned": 0, "possible": 5},
            "consultant_allocation": {"earned": 0, "possible": 5},
            "contingency_planning": {"earned": 0, "possible": 5},
            "total_budget": {"earned": 0, "possible": 5}
        },
        "feedback": []
    }
    
    sub_budget = submission["budget_allocation"]["quarterly_breakdown"]
    key_budget = answer_key["budget_allocation"]["quarterly_breakdown"]
    
    # Check if total budget equals $1,200,000
    sub_total = sum(sum(q[cat] for cat in ["personnel", "submissions", "training", "consultants", "contingency"]) 
                   for q in sub_budget)
    if sub_total == 1200000:
        results["details"]["total_budget"]["earned"] = 5
    else:
        results["feedback"].append(f"Total budget should be $1,200,000, found ${sub_total}")
    
    # Check quarterly distribution (higher in Q2-Q3)
    sub_q2_q3 = sum(q["submissions"] for q in sub_budget if q["quarter"] in ["Q2", "Q3"])
    key_q2_q3 = sum(q["submissions"] for q in key_budget if q["quarter"] in ["Q2", "Q3"])
    sub_q1_q4 = sum(q["submissions"] for q in sub_budget if q["quarter"] in ["Q1", "Q4"])
    key_q1_q4 = sum(q["submissions"] for q in key_budget if q["quarter"] in ["Q1", "Q4"])
    
    if sub_q2_q3 > sub_q1_q4 and sub_q2_q3 >= 200000:
        results["details"]["quarterly_distribution"]["earned"] = 5
    elif sub_q2_q3 > sub_q1_q4:
        results["details"]["quarterly_distribution"]["earned"] = 3
    else:
        results["feedback"].append("Q2-Q3 should have higher submission fees than Q1-Q4")
    
    # Check personnel costs (should be consistent)
    personnel_values = [q["personnel"] for q in sub_budget]
    if all(p == personnel_values[0] for p in personnel_values) and personnel_values[0] >= 140000:
        results["details"]["personnel_costs"]["earned"] = 5
    elif max(personnel_values) - min(personnel_values) <= 20000:
        results["details"]["personnel_costs"]["earned"] = 3
    else:
        results["feedback"].append("Personnel costs should be relatively consistent across quarters")
    
    # Check training allocation (higher in Q1)
    sub_q1_training = next((q["training"] for q in sub_budget if q["quarter"] == "Q1"), 0)
    other_quarters_training = [q["training"] for q in sub_budget if q["quarter"] != "Q1"]
    
    if sub_q1_training > max(other_quarters_training):
        results["details"]["training_allocation"]["earned"] = 5
    else:
        results["feedback"].append("Training budget should be highest in Q1")
    
    # Check consultant allocation (aligned with submission peaks)
    sub_q2_consultants = next((q["consultants"] for q in sub_budget if q["quarter"] == "Q2"), 0)
    if sub_q2_consultants >= 35000 and sub_q2_consultants == max(q["consultants"] for q in sub_budget):
        results["details"]["consultant_allocation"]["earned"] = 5
    elif sub_q2_consultants >= 30000:
        results["details"]["consultant_allocation"]["earned"] = 3
    else:
        results["feedback"].append("Consultant budget should be highest in Q2 to support peak submission period")
    
    # Check contingency planning
    sub_q2_contingency = next((q["contingency"] for q in sub_budget if q["quarter"] == "Q2"), 0)
    if sub_q2_contingency >= 15000 and sub_q2_contingency >= max(q["contingency"] for q in sub_budget if q["quarter"] != "Q2"):
        results["details"]["contingency_planning"]["earned"] = 5
    elif sub_q2_contingency >= 10000:
        results["details"]["contingency_planning"]["earned"] = 3
    else:
        results["feedback"].append("Contingency should be higher in Q2 when most critical submissions are due")
    
    # Calculate total points earned
    results["points_earned"] = sum(detail["earned"] for detail in results["details"].values())
    
    # Add pass/fail status
    results["passed"] = results["points_earned"] >= 18  # 60% of 30 points
    
    return results


def evaluate_resource_allocation(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the resource allocation section."""
    results = {
        "points_earned": 0,
        "points_possible": 35,
        "details": {
            "expertise_matching": {"earned": 0, "possible": 16},
            "workload_balancing": {"earned": 0, "possible": 16},
            "resource_gaps": {"earned": 0, "possible": 3}
        },
        "feedback": []
    }
    
    # Create dictionaries for easier lookup
    sub_assignments = {item["team_member_id"]: item for item in submission["resource_allocation"]["team_assignments"]}
    key_assignments = {item["team_member_id"]: item for item in answer_key["resource_allocation"]["team_assignments"]}
    
    # Define expertise areas for team members
    expertise_areas = {
        "TM001": ["P001", "P015", "P013", "P004", "P009"],  # US Regulations
        "TM002": ["P007", "P011", "P002", "P008"],  # EU Regulations
        "TM003": ["P001", "P007", "P009", "P013"],  # Global Strategy
        "TM004": ["P003", "P012", "P014"],  # Documentation (Junior)
        "TM005": ["P004", "P008", "P013"],  # Clinical Trials
        "TM006": ["P005", "P015", "P001"],  # CMC
        "TM007": ["P002", "P006", "P012"],  # Labeling (Junior)
        "TM008": ["P011", "P012", "P003"]   # Safety Reporting
    }
    
    # Check expertise matching (2 points per team member)
    for team_id, expertise_projects in expertise_areas.items():
        if team_id in sub_assignments:
            assigned_projects = sub_assignments[team_id]["assigned_projects"]
            matching_projects = [p for p in assigned_projects if p in expertise_projects]
            
            # Award points based on percentage of projects matching expertise
            if len(assigned_projects) > 0:
                match_percentage = len(matching_projects) / len(assigned_projects)
                if match_percentage >= 0.75:
                    results["details"]["expertise_matching"]["earned"] += 2
                elif match_percentage >= 0.5:
                    results["details"]["expertise_matching"]["earned"] += 1
                else:
                    results["feedback"].append(f"{team_id} should be assigned to projects matching their expertise: {expertise_projects}")
        else:
            results["feedback"].append(f"Missing assignments for {team_id}")
    
    # Check workload balancing (2 points per team member)
    for team_id, assignment in sub_assignments.items():
        # Check if allocation percentages sum to 100%
        allocation_sum = sum(assignment["allocation_percentage"])
        if allocation_sum == 100:
            results["details"]["workload_balancing"]["earned"] += 2
        else:
            results["feedback"].append(f"{team_id} allocation percentages sum to {allocation_sum}, should be 100%")
    
    # Check resource gaps (3 points for identifying at least 3 appropriate gaps)
    sub_gaps = submission["resource_allocation"]["resource_gaps"]
    key_gaps = answer_key["resource_allocation"]["resource_gaps"]
    
    # Define critical gaps that should be identified
    critical_gap_projects = ["P004", "P010", "P009"]
    identified_critical_gaps = [gap["project_id"] for gap in sub_gaps if gap["project_id"] in critical_gap_projects]
    
    if len(identified_critical_gaps) >= 3:
        results["details"]["resource_gaps"]["earned"] = 3
    elif len(identified_critical_gaps) >= 2:
        results["details"]["resource_gaps"]["earned"] = 2
    elif len(identified_critical_gaps) >= 1:
        results["details"]["resource_gaps"]["earned"] = 1
    else:
        results["feedback"].append(f"Failed to identify critical resource gaps in projects {critical_gap_projects}")
    
    # Calculate total points earned
    results["points_earned"] = (
        results["details"]["expertise_matching"]["earned"] +
        results["details"]["workload_balancing"]["earned"] +
        results["details"]["resource_gaps"]["earned"]
    )
    
    # Add pass/fail status
    results["passed"] = results["points_earned"] >= 21  # 60% of 35 points
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the full submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "prioritization": evaluate_prioritization(submission, answer_key),
        "budget_allocation": evaluate_budget_allocation(submission, answer_key),
        "resource_allocation": evaluate_resource_allocation(submission, answer_key),
    }
    
    # Calculate overall score
    total_points_earned = (
        results["prioritization"]["points_earned"] +
        results["budget_allocation"]["points_earned"] +
        results["resource_allocation"]["points_earned"]
    )
    total_points_possible = (
        results["prioritization"]["points_possible"] +
        results["budget_allocation"]["points_possible"] +
        results["resource_allocation"]["points_possible"]
    )
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    
    # Determine if the candidate passed overall
    section_passes = (
        results["prioritization"]["passed"] and
        results["budget_allocation"]["passed"] and
        results["resource_allocation"]["passed"]
    )
    overall_pass = section_passes and results["overall_score"] >= 70
    
    results["passed"] = overall_pass
    
    return results


def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")


if __name__ == "__main__":
    main()