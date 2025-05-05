#!/usr/bin/env python3
import json
import sys
import re
from collections import Counter

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate protocol issue identification task"""
    results = {
        "identified_issues_count": len(submission.get("task1_protocol_issues", [])),
        "critical_issues_identified": 0,
        "major_issues_identified": 0,
        "minor_issues_identified": 0,
        "correct_classifications": 0,
        "issue_types_identified": [],
        "severity_distribution": {},
        "issues_with_clear_descriptions": 0,
        "score": 0,
        "max_score": 40,
        "feedback": []
    }
    
    # Count issues by severity
    severity_counts = Counter()
    for issue in submission.get("task1_protocol_issues", []):
        severity = issue.get("severity", "").lower()
        severity_counts[severity] += 1
        
        # Check if description is clear and specific (50-100 words)
        description = issue.get("description", "")
        word_count = len(re.findall(r'\b\w+\b', description))
        if 40 <= word_count <= 120:  # Being a bit flexible with the word count
            results["issues_with_clear_descriptions"] += 1
    
    results["severity_distribution"] = dict(severity_counts)
    results["critical_issues_identified"] = severity_counts.get("critical", 0)
    results["major_issues_identified"] = severity_counts.get("major", 0)
    results["minor_issues_identified"] = severity_counts.get("minor", 0)
    
    # Check for correct issue types
    valid_issue_types = set()
    for issue in answer_key.get("task1_protocol_issues", []):
        valid_issue_types.add(issue.get("issue_type"))
    
    for issue in submission.get("task1_protocol_issues", []):
        issue_type = issue.get("issue_type")
        if issue_type in valid_issue_types:
            results["correct_classifications"] += 1
            if issue_type not in results["issue_types_identified"]:
                results["issue_types_identified"].append(issue_type)
    
    # Calculate score
    # Base points for identifying at least 5 issues
    if results["identified_issues_count"] >= 5:
        results["score"] += 10
        results["feedback"].append("Successfully identified at least 5 protocol issues.")
    else:
        results["feedback"].append(f"Identified only {results['identified_issues_count']} issues. Minimum requirement is 5.")
    
    # Points for identifying critical issues (up to 15 points)
    if results["critical_issues_identified"] >= 3:
        results["score"] += 15
        results["feedback"].append("Excellent job identifying all critical issues.")
    elif results["critical_issues_identified"] == 2:
        results["score"] += 10
        results["feedback"].append("Good job identifying 2 critical issues.")
    elif results["critical_issues_identified"] == 1:
        results["score"] += 5
        results["feedback"].append("Identified only 1 critical issue. At least 2 are required for a passing score.")
    else:
        results["feedback"].append("Failed to identify any critical issues. This is a significant gap.")
    
    # Points for correct classifications (up to 10 points)
    classification_score = min(10, results["correct_classifications"] * 2.5)
    results["score"] += classification_score
    if results["correct_classifications"] >= 4:
        results["feedback"].append(f"Successfully classified {results['correct_classifications']} issues correctly.")
    else:
        results["feedback"].append(f"Only {results['correct_classifications']} issues were classified correctly. Minimum requirement is 4.")
    
    # Points for clear descriptions (up to 5 points)
    description_score = min(5, results["issues_with_clear_descriptions"])
    results["score"] += description_score
    results["feedback"].append(f"{results['issues_with_clear_descriptions']} issues had clear, specific descriptions.")
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate investigator communication task"""
    results = {
        "has_professional_subject_line": False,
        "focuses_on_critical_issues": False,
        "has_three_actionable_recommendations": False,
        "subject_line_word_count": 0,
        "key_issues_summary_word_count": 0,
        "recommended_actions_count": 0,
        "score": 0,
        "max_score": 30,
        "feedback": []
    }
    
    task2 = submission.get("task2_investigator_communication", {})
    
    # Check subject line
    subject_line = task2.get("subject_line", "")
    results["subject_line_word_count"] = len(re.findall(r'\b\w+\b', subject_line))
    if 8 <= results["subject_line_word_count"] <= 20 and "protocol" in subject_line.lower():
        results["has_professional_subject_line"] = True
        results["score"] += 5
        results["feedback"].append("Subject line is professional and appropriate.")
    else:
        results["feedback"].append("Subject line needs improvement in clarity, professionalism, or length.")
    
    # Check key issues summary
    key_issues = task2.get("key_issues_summary", "")
    results["key_issues_summary_word_count"] = len(re.findall(r'\b\w+\b', key_issues))
    
    # Check if summary focuses on critical issues
    critical_issue_keywords = [
        "safety", "adverse event", "reporting", "inclusion criteria", 
        "inconsistency", "informed consent", "withdraw", "regulatory"
    ]
    
    critical_focus_count = sum(1 for keyword in critical_issue_keywords if keyword.lower() in key_issues.lower())
    
    if critical_focus_count >= 3 and 80 <= results["key_issues_summary_word_count"] <= 170:
        results["focuses_on_critical_issues"] = True
        results["score"] += 15
        results["feedback"].append("Key issues summary effectively focuses on critical issues.")
    else:
        results["feedback"].append("Key issues summary needs improvement in focus on critical issues or length.")
    
    # Check recommended actions
    recommended_actions = task2.get("recommended_actions", [])
    results["recommended_actions_count"] = len(recommended_actions)
    
    action_word_counts = [len(re.findall(r'\b\w+\b', action)) for action in recommended_actions]
    actionable_count = sum(1 for count in action_word_counts if 10 <= count <= 30)
    
    if results["recommended_actions_count"] == 3 and actionable_count == 3:
        results["has_three_actionable_recommendations"] = True
        results["score"] += 10
        results["feedback"].append("Provided 3 specific, actionable recommendations.")
    else:
        results["feedback"].append(f"Recommended actions need improvement. Found {results['recommended_actions_count']} actions with {actionable_count} being appropriately specific and actionable.")
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate protocol revision proposals task"""
    results = {
        "revision_proposals_count": 0,
        "critical_issues_addressed": 0,
        "appropriate_rationale_codes": 0,
        "revisions_that_address_problems": 0,
        "score": 0,
        "max_score": 30,
        "feedback": []
    }
    
    task3 = submission.get("task3_protocol_revisions", [])
    results["revision_proposals_count"] = len(task3)
    
    # Get critical issue IDs from task1
    critical_issue_ids = []
    for issue in submission.get("task1_protocol_issues", []):
        if issue.get("severity", "").lower() == "critical":
            critical_issue_ids.append(issue.get("issue_id"))
    
    # Check if revisions address critical issues
    addressed_critical_issues = set()
    valid_rationale_codes = {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"}
    
    for revision in task3:
        issue_id = revision.get("issue_id")
        
        # Check if revision addresses a critical issue
        if issue_id in critical_issue_ids:
            addressed_critical_issues.add(issue_id)
        
        # Check if rationale code is valid
        if revision.get("rationale_code") in valid_rationale_codes:
            results["appropriate_rationale_codes"] += 1
        
        # Check if revision addresses the problem
        current_text = revision.get("current_text", "")
        proposed_revision = revision.get("proposed_revision", "")
        
        if current_text and proposed_revision and current_text != proposed_revision:
            results["revisions_that_address_problems"] += 1
    
    results["critical_issues_addressed"] = len(addressed_critical_issues)
    
    # Calculate score
    # Points for number of revision proposals (up to 5 points)
    if results["revision_proposals_count"] >= 3:
        results["score"] += 5
        results["feedback"].append("Provided the required 3 revision proposals.")
    else:
        results["feedback"].append(f"Provided only {results['revision_proposals_count']} revision proposals. 3 are required.")
    
    # Points for addressing critical issues (up to 15 points)
    critical_score = min(15, results["critical_issues_addressed"] * 7.5)
    results["score"] += critical_score
    if results["critical_issues_addressed"] >= 2:
        results["feedback"].append(f"Successfully addressed {results['critical_issues_addressed']} critical issues.")
    else:
        results["feedback"].append(f"Only addressed {results['critical_issues_addressed']} critical issues. At least 2 are required for a passing score.")
    
    # Points for appropriate rationale codes (up to 5 points)
    rationale_score = min(5, results["appropriate_rationale_codes"] * 1.67)
    results["score"] += rationale_score
    results["feedback"].append(f"Used appropriate rationale codes for {results['appropriate_rationale_codes']} revisions.")
    
    # Points for revisions that address problems (up to 5 points)
    revision_quality_score = min(5, results["revisions_that_address_problems"] * 1.67)
    results["score"] += revision_quality_score
    results["feedback"].append(f"{results['revisions_that_address_problems']} revisions effectively address the identified problems.")
    
    return results

def calculate_overall_score(task_results):
    """Calculate overall score and performance level"""
    total_score = sum(task["score"] for task in task_results.values())
    max_score = sum(task["max_score"] for task in task_results.values())
    percentage = (total_score / max_score) * 100
    
    # Determine performance level
    if percentage >= 90:
        performance_level = "Excellent"
    elif percentage >= 80:
        performance_level = "Good"
    elif percentage >= 70:
        performance_level = "Satisfactory"
    elif percentage >= 60:
        performance_level = "Needs Improvement"
    else:
        performance_level = "Unsatisfactory"
    
    # Determine pass/fail status
    passed = percentage >= 70  # "Satisfactory" or better
    
    return {
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": round(percentage, 2),
        "performance_level": performance_level,
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
    
    # Evaluate each task
    results = {
        "candidate_id": submission.get("candidateID", "Unknown"),
        "task1_results": evaluate_task1(submission, answer_key),
        "task2_results": evaluate_task2(submission, answer_key),
        "task3_results": evaluate_task3(submission, answer_key)
    }
    
    # Calculate overall score
    overall_results = calculate_overall_score({
        "task1": results["task1_results"],
        "task2": results["task2_results"],
        "task3": results["task3_results"]
    })
    
    results.update(overall_results)
    
    # Generate summary feedback
    summary_feedback = []
    if overall_results["passed"]:
        summary_feedback.append(f"PASSED with an overall score of {overall_results['overall_score']}% ({overall_results['performance_level']}).")
    else:
        summary_feedback.append(f"DID NOT PASS with an overall score of {overall_results['overall_score']}% ({overall_results['performance_level']}).")
    
    # Add task-specific summary feedback
    task1 = results["task1_results"]
    if task1["critical_issues_identified"] < 2 or task1["identified_issues_count"] < 5:
        summary_feedback.append("Task 1: Failed to identify sufficient protocol issues, especially critical ones.")
    
    task2 = results["task2_results"]
    if not task2["focuses_on_critical_issues"]:
        summary_feedback.append("Task 2: Communication did not adequately focus on critical issues.")
    
    task3 = results["task3_results"]
    if task3["critical_issues_addressed"] < 2:
        summary_feedback.append("Task 3: Failed to provide adequate revisions for critical issues.")
    
    results["summary_feedback"] = summary_feedback
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()