#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_financial_impact(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the financial impact calculations for each program change."""
    max_points = 40
    points_earned = 0
    details = []
    
    # Create lookup dictionaries for easier access
    sub_changes = {change["change_id"]: change for change in submission["program_changes"]}
    key_changes = {change["change_id"]: change for change in answer_key["program_changes"]}
    
    # Each program change is worth 10 points
    points_per_change = max_points / len(key_changes)
    
    for change_id, key_change in key_changes.items():
        if change_id in sub_changes:
            sub_change = sub_changes[change_id]
            key_impact = key_change["financial_impact"]
            sub_impact = sub_change["financial_impact"]
            
            # Calculate percentage error
            if key_impact == 0:
                error_percentage = 100 if sub_impact != 0 else 0
            else:
                error_percentage = abs(sub_impact - key_impact) / abs(key_impact) * 100
            
            # Award points based on accuracy
            if error_percentage == 0:
                score = points_per_change
            elif error_percentage <= 5:
                score = points_per_change * 0.9
            elif error_percentage <= 10:
                score = points_per_change * 0.7
            elif error_percentage <= 20:
                score = points_per_change * 0.5
            else:
                score = 0
            
            points_earned += score
            
            details.append({
                "change_id": change_id,
                "correct_impact": key_impact,
                "submitted_impact": sub_impact,
                "error_percentage": round(error_percentage, 2),
                "points_possible": points_per_change,
                "points_earned": score,
                "explanation": f"{'Correct' if error_percentage == 0 else f'Error of {error_percentage:.2f}%'}"
            })
        else:
            details.append({
                "change_id": change_id,
                "points_possible": points_per_change,
                "points_earned": 0,
                "explanation": "Program change not found in submission"
            })
    
    return round(points_earned, 2), details

def evaluate_budget_lines(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the identification of affected budget lines."""
    max_points = 20
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    sub_changes = {change["change_id"]: change for change in submission["program_changes"]}
    key_changes = {change["change_id"]: change for change in answer_key["program_changes"]}
    
    # Each program change is worth 5 points
    points_per_change = max_points / len(key_changes)
    
    for change_id, key_change in key_changes.items():
        if change_id in sub_changes:
            sub_change = sub_changes[change_id]
            key_lines = set(key_change["affected_budget_lines"])
            sub_lines = set(sub_change["affected_budget_lines"])
            
            # Calculate correct, missing, and extra lines
            correct_lines = key_lines.intersection(sub_lines)
            missing_lines = key_lines - sub_lines
            extra_lines = sub_lines - key_lines
            
            # Calculate score based on accuracy
            if len(key_lines) == 0:
                accuracy = 1.0 if len(sub_lines) == 0 else 0.0
            else:
                accuracy = len(correct_lines) / len(key_lines)
                # Penalize for extra lines
                if extra_lines:
                    accuracy = max(0, accuracy - (len(extra_lines) / len(key_lines) * 0.5))
            
            score = points_per_change * accuracy
            points_earned += score
            
            details.append({
                "change_id": change_id,
                "correct_lines": list(key_lines),
                "submitted_lines": list(sub_lines),
                "missing_lines": list(missing_lines),
                "extra_lines": list(extra_lines),
                "points_possible": points_per_change,
                "points_earned": score,
                "explanation": f"Identified {len(correct_lines)}/{len(key_lines)} correct lines" + 
                              (f", missed {len(missing_lines)}" if missing_lines else "") +
                              (f", added {len(extra_lines)} extra" if extra_lines else "")
            })
        else:
            details.append({
                "change_id": change_id,
                "points_possible": points_per_change,
                "points_earned": 0,
                "explanation": "Program change not found in submission"
            })
    
    return round(points_earned, 2), details

def evaluate_policy_compliance(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the assessment of policy compliance."""
    max_points = 20
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    sub_changes = {change["change_id"]: change for change in submission["program_changes"]}
    key_changes = {change["change_id"]: change for change in answer_key["program_changes"]}
    
    # Each program change is worth 5 points
    points_per_change = max_points / len(key_changes)
    
    for change_id, key_change in key_changes.items():
        if change_id in sub_changes:
            sub_change = sub_changes[change_id]
            
            # Create lookup dictionaries for adjustments
            key_adjustments = {adj["budget_line"]: adj for adj in key_change["adjustments"]}
            sub_adjustments = {adj["budget_line"]: adj for adj in sub_change["adjustments"]}
            
            # Count correct compliance assessments
            total_assessments = len(key_adjustments)
            correct_assessments = 0
            
            assessment_details = []
            
            for budget_line, key_adj in key_adjustments.items():
                if budget_line in sub_adjustments:
                    sub_adj = sub_adjustments[budget_line]
                    key_complies = key_adj["complies_with_policy"]
                    sub_complies = sub_adj["complies_with_policy"]
                    
                    if key_complies == sub_complies:
                        correct_assessments += 1
                        assessment_details.append({
                            "budget_line": budget_line,
                            "correct": True,
                            "explanation": "Correct compliance assessment"
                        })
                    else:
                        assessment_details.append({
                            "budget_line": budget_line,
                            "correct": False,
                            "explanation": f"Incorrect compliance assessment: should be {key_complies}"
                        })
                else:
                    assessment_details.append({
                        "budget_line": budget_line,
                        "correct": False,
                        "explanation": "Budget line not found in submission"
                    })
            
            # Calculate score
            if total_assessments == 0:
                accuracy = 1.0
            else:
                accuracy = correct_assessments / total_assessments
            
            score = points_per_change * accuracy
            points_earned += score
            
            details.append({
                "change_id": change_id,
                "correct_assessments": correct_assessments,
                "total_assessments": total_assessments,
                "assessment_details": assessment_details,
                "points_possible": points_per_change,
                "points_earned": score,
                "explanation": f"Correctly assessed {correct_assessments}/{total_assessments} budget lines"
            })
        else:
            details.append({
                "change_id": change_id,
                "points_possible": points_per_change,
                "points_earned": 0,
                "explanation": "Program change not found in submission"
            })
    
    return round(points_earned, 2), details

def evaluate_notifications(submission: Dict, answer_key: Dict) -> Tuple[int, List[Dict]]:
    """Evaluate the selection of manager notification templates."""
    max_points = 20
    points_earned = 0
    details = []
    
    # Create lookup dictionaries
    key_notifications = {notif["change_id"]: notif for notif in answer_key["manager_notifications"]}
    
    # Handle different submission formats
    if "manager_notifications" in submission:
        sub_notifications = {notif["change_id"]: notif for notif in submission["manager_notifications"]}
    else:
        # Try to find notification in the main structure
        sub_notifications = {}
        for change in submission.get("program_changes", []):
            if "notification_template_code" in change:
                sub_notifications[change["change_id"]] = {
                    "change_id": change["change_id"],
                    "notification_template_code": change["notification_template_code"]
                }
    
    # Each notification is worth 5 points
    points_per_notification = max_points / len(key_notifications)
    
    for change_id, key_notif in key_notifications.items():
        if change_id in sub_notifications:
            sub_notif = sub_notifications[change_id]
            key_template = key_notif["notification_template_code"]
            sub_template = sub_notif.get("notification_template_code", "")
            
            # Check if templates match
            if key_template == sub_template:
                score = points_per_notification
                explanation = "Correct notification template selected"
            # Special case for PC003 where both BN-101 and BN-104 could be acceptable
            elif change_id == "PC003" and sub_template in ["BN-101", "BN-104"]:
                score = points_per_notification
                explanation = "Alternative acceptable template selected"
            else:
                score = 0
                explanation = f"Incorrect template: selected {sub_template}, should be {key_template}"
            
            points_earned += score
            
            details.append({
                "change_id": change_id,
                "correct_template": key_template,
                "submitted_template": sub_template,
                "points_possible": points_per_notification,
                "points_earned": score,
                "explanation": explanation
            })
        else:
            details.append({
                "change_id": change_id,
                "points_possible": points_per_notification,
                "points_earned": 0,
                "explanation": "Notification not found in submission"
            })
    
    return round(points_earned, 2), details

def evaluate_submission(submission_path: str, answer_key_path: str) -> Dict:
    """Evaluate a candidate's submission against the answer key."""
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate each section
    financial_points, financial_details = evaluate_financial_impact(submission, answer_key)
    budget_line_points, budget_line_details = evaluate_budget_lines(submission, answer_key)
    policy_points, policy_details = evaluate_policy_compliance(submission, answer_key)
    notification_points, notification_details = evaluate_notifications(submission, answer_key)
    
    # Calculate total score
    total_points = financial_points + budget_line_points + policy_points + notification_points
    max_points = 100
    overall_score = (total_points / max_points) * 100
    
    # Determine if the candidate passed
    passed = overall_score >= 70
    
    return {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "total_points": round(total_points, 2),
        "max_points": max_points,
        "section_scores": {
            "financial_impact": {
                "points_earned": financial_points,
                "points_possible": 40,
                "percentage": round((financial_points / 40) * 100, 2),
                "details": financial_details
            },
            "budget_lines": {
                "points_earned": budget_line_points,
                "points_possible": 20,
                "percentage": round((budget_line_points / 20) * 100, 2),
                "details": budget_line_details
            },
            "policy_compliance": {
                "points_earned": policy_points,
                "points_possible": 20,
                "percentage": round((policy_points / 20) * 100, 2),
                "details": policy_details
            },
            "notifications": {
                "points_earned": notification_points,
                "points_possible": 20,
                "percentage": round((notification_points / 20) * 100, 2),
                "details": notification_details
            }
        }
    }

def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Save results to file
    output_path = "test_results.json"
    with open(output_path, 'w') as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_path}")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()