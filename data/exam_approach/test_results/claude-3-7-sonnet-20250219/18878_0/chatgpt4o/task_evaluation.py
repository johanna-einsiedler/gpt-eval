#!/usr/bin/env python3
import json
import sys
import re
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(candidate, key):
    score = 0
    feedback = []
    
    # Key issues (10 points - 2 points per correct issue)
    issue_score = 0
    if len(candidate.get("key_issues", [])) == 5:
        for issue in candidate["key_issues"]:
            # Check if any key issue matches (partial matching)
            for key_issue in key["key_issues"]:
                if any(keyword in issue.lower() for keyword in key_issue.lower().split()):
                    issue_score += 2
                    break
        issue_score = min(issue_score, 10)  # Cap at 10 points
    else:
        feedback.append("Did not provide exactly 5 key issues")
    
    # Relevant clauses (5 points - 1 point per correct clause)
    clause_score = 0
    candidate_clauses = candidate.get("relevant_clauses", [])
    key_clauses = key["relevant_clauses"]
    
    for clause in candidate_clauses:
        if clause in key_clauses:
            clause_score += 1
    clause_score = min(clause_score, 5)  # Cap at 5 points
    
    # Priority ranking (5 points for logical prioritization with safety first)
    priority_score = 0
    candidate_ranking = candidate.get("priority_ranking", [])
    
    # Check if safety issues (positions 2 and 3 in key issues) are prioritized
    if len(candidate_ranking) == 5:
        # Check if safety training is high priority (1 or 2)
        safety_training_pos = candidate_ranking[2] if len(candidate_ranking) > 2 else 0
        if safety_training_pos in [1, 2]:
            priority_score += 2.5
        
        # Check if PPE provision is high priority (1 or 2)
        ppe_pos = candidate_ranking[3] if len(candidate_ranking) > 3 else 0
        if ppe_pos in [1, 2]:
            priority_score += 2.5
    else:
        feedback.append("Did not provide exactly 5 priority rankings")
    
    score = issue_score + clause_score + priority_score
    
    return {
        "score": score,
        "max_score": 20,
        "breakdown": {
            "key_issues": issue_score,
            "relevant_clauses": clause_score,
            "priority_ranking": priority_score
        },
        "feedback": feedback
    }

def evaluate_task2(candidate, key):
    score = 0
    feedback = []
    
    # Meeting agenda (6 points - 1 point per appropriate agenda item)
    agenda_score = 0
    candidate_agenda = candidate.get("meeting_agenda", [])
    key_agenda = key["meeting_agenda"]
    
    if len(candidate_agenda) == 6:
        for item in candidate_agenda:
            for key_item in key_agenda:
                if any(keyword in item.lower() for keyword in key_item.lower().split()):
                    agenda_score += 1
                    break
        agenda_score = min(agenda_score, 6)  # Cap at 6 points
    else:
        feedback.append("Did not provide exactly 6 agenda items")
    
    # Prepared questions (8 points - 2 points per effective question)
    question_score = 0
    candidate_questions = candidate.get("prepared_questions", [])
    key_questions = key["prepared_questions"]
    
    if len(candidate_questions) == 4:
        for question in candidate_questions:
            is_effective = False
            # Check if question addresses key topics
            if any("PPE" in q and "PPE" in question for q in key_questions):
                question_score += 2
                continue
            if any("emergency" in q and "emergency" in question for q in key_questions):
                question_score += 2
                continue
            if any("training" in q and "training" in question for q in key_questions):
                question_score += 2
                continue
            if any("overtime" in q and "overtime" in question for q in key_questions):
                question_score += 2
                continue
            
            # General check for open-ended, relevant questions
            if question.endswith("?") and any(keyword in question.lower() for keyword in ["how", "what", "when", "why", "who"]):
                question_score += 1
        
        question_score = min(question_score, 8)  # Cap at 8 points
    else:
        feedback.append("Did not provide exactly 4 prepared questions")
    
    # Documentation needed (6 points - 1.2 points per relevant document)
    doc_score = 0
    candidate_docs = candidate.get("documentation_needed", [])
    key_docs = key["documentation_needed"]
    
    if len(candidate_docs) == 5:
        for doc in candidate_docs:
            for key_doc in key_docs:
                if any(keyword in doc.lower() for keyword in key_doc.lower().split()):
                    doc_score += 1.2
                    break
        doc_score = min(doc_score, 6)  # Cap at 6 points
    else:
        feedback.append("Did not provide exactly 5 documents")
    
    score = agenda_score + question_score + doc_score
    
    return {
        "score": score,
        "max_score": 20,
        "breakdown": {
            "meeting_agenda": agenda_score,
            "prepared_questions": question_score,
            "documentation_needed": doc_score
        },
        "feedback": feedback
    }

def evaluate_task3(candidate, key):
    score = 0
    feedback = []
    
    # Email subject (5 points - clear, professional, informative)
    subject_score = 0
    candidate_subject = candidate.get("email_subject", "")
    
    if candidate_subject:
        # Check if subject is clear and informative
        if "meeting" in candidate_subject.lower() and "june 29" in candidate_subject.lower():
            subject_score += 2
        
        # Check if subject mentions grievances or concerns
        if any(keyword in candidate_subject.lower() for keyword in ["grievance", "safety", "concern"]):
            subject_score += 2
        
        # Check length (not too long, not too short)
        if 20 <= len(candidate_subject) <= 100:
            subject_score += 1
    else:
        feedback.append("No email subject provided")
    
    # Email body (15 points - addresses all issues, professional tone, complete information)
    body_score = 0
    candidate_body = candidate.get("email_body", "")
    
    if candidate_body:
        # Check if email confirms meeting details
        if "june 29" in candidate_body.lower() and "10:00" in candidate_body:
            body_score += 3
        
        # Check if email addresses all four issues from the union's request
        issues_addressed = 0
        if "grievance #2023-17" in candidate_body.lower() or ("overtime" in candidate_body.lower() and "distribution" in candidate_body.lower()):
            issues_addressed += 1
        if "grievance #2023-19" in candidate_body.lower() or ("safety" in candidate_body.lower() and ("training" in candidate_body.lower() or "ppe" in candidate_body.lower())):
            issues_addressed += 1
        if "overtime policy" in candidate_body.lower() or "three refusals" in candidate_body.lower():
            issues_addressed += 1
        if "health and safety committee" in candidate_body.lower() or "assessment" in candidate_body.lower():
            issues_addressed += 1
        
        body_score += min(issues_addressed * 2, 8)
        
        # Check if email confirms attendance of requested participants
        if "lisa chen" in candidate_body.lower() and "robert johnson" in candidate_body.lower():
            body_score += 2
        
        # Check professional tone
        if "thank" in candidate_body.lower() and "sincerely" in candidate_body.lower():
            body_score += 2
    else:
        feedback.append("No email body provided")
    
    score = subject_score + body_score
    
    return {
        "score": score,
        "max_score": 20,
        "breakdown": {
            "email_subject": subject_score,
            "email_body": body_score
        },
        "feedback": feedback
    }

def evaluate_task4(candidate, key):
    score = 0
    feedback = []
    
    # Scenario 1 (6 points - knowledge of CBA, professional response)
    scenario1_score = 0
    candidate_response1 = candidate.get("scenario1_response", "")
    
    if candidate_response1:
        # Check for reference to Article 7.3
        if "article 7.3" in candidate_response1.lower() or "7.3" in candidate_response1:
            scenario1_score += 2
        
        # Check for professional tone
        if "understand" in candidate_response1.lower() and not any(word in candidate_response1.lower() for word in ["wrong", "incorrect", "mistaken"]):
            scenario1_score += 2
        
        # Check for solution-oriented approach
        if any(word in candidate_response1.lower() for word in ["clarify", "review", "discuss", "resolve"]):
            scenario1_score += 2
    else:
        feedback.append("No response provided for scenario 1")
    
    # Scenario 2 (7 points - de-escalation techniques, professional response)
    scenario2_score = 0
    candidate_response2 = candidate.get("scenario2_response", "")
    
    if candidate_response2:
        # Check for acknowledgment of emotions
        if any(word in candidate_response2.lower() for word in ["understand", "appreciate", "recognize"]):
            scenario2_score += 2
        
        # Check for de-escalation techniques
        if any(phrase in candidate_response2.lower() for phrase in ["take a break", "pause", "step back", "calm"]):
            scenario2_score += 3
        
        # Check for solution-oriented approach
        if any(word in candidate_response2.lower() for word in ["solution", "resolve", "address", "concern"]):
            scenario2_score += 2
    else:
        feedback.append("No response provided for scenario 2")
    
    # Scenario 3 (7 points - problem-solving approach, professional response)
    scenario3_score = 0
    candidate_response3 = candidate.get("scenario3_response", "")
    
    if candidate_response3:
        # Check for acknowledgment of impasse
        if any(word in candidate_response3.lower() for word in ["impasse", "stuck", "challenging", "difficult"]):
            scenario3_score += 2
        
        # Check for alternative suggestions
        if any(phrase in candidate_response3.lower() for phrase in ["move on", "next item", "return later", "working group", "alternative"]):
            scenario3_score += 3
        
        # Check for collaborative approach
        if any(phrase in candidate_response3.lower() for phrase in ["would you prefer", "what do you think", "your input", "together"]):
            scenario3_score += 2
    else:
        feedback.append("No response provided for scenario 3")
    
    score = scenario1_score + scenario2_score + scenario3_score
    
    return {
        "score": score,
        "max_score": 20,
        "breakdown": {
            "scenario1_response": scenario1_score,
            "scenario2_response": scenario2_score,
            "scenario3_response": scenario3_score
        },
        "feedback": feedback
    }

def evaluate_task5(candidate, key):
    score = 0
    feedback = []
    
    # Meeting summary (6 points - 1 point per appropriate summary point)
    summary_score = 0
    candidate_summary = candidate.get("meeting_summary", [])
    
    if len(candidate_summary) == 6:
        for point in candidate_summary:
            if any(keyword in point.lower() for keyword in ["grievance", "overtime", "ppe", "training", "safety", "policy"]):
                summary_score += 1
        summary_score = min(summary_score, 6)  # Cap at 6 points
    else:
        feedback.append("Did not provide exactly 6 meeting summary points")
    
    # Action items (8 points - 2 points per specific, assignable action item)
    action_score = 0
    candidate_actions = candidate.get("action_items", [])
    
    if len(candidate_actions) == 4:
        for action in candidate_actions:
            # Check if action is specific
            if any(keyword in action.lower() for keyword in ["provide", "revise", "develop", "complete", "schedule", "update"]):
                action_score += 1
            
            # Check if action is assignable (mentions who is responsible)
            if any(role in action.lower() for role in ["director", "manager", "supervisor", "committee", "hr"]):
                action_score += 1
        action_score = min(action_score, 8)  # Cap at 8 points
    else:
        feedback.append("Did not provide exactly 4 action items")
    
    # Follow-up timeline (6 points - 2 points per appropriate timeline entry)
    timeline_score = 0
    candidate_timeline = candidate.get("follow_up_timeline", [])
    
    if len(candidate_timeline) == 3:
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
        for entry in candidate_timeline:
            # Check if entry has a date in the correct format
            if re.search(date_pattern, entry):
                timeline_score += 1
            
            # Check if entry has a specific action
            if any(keyword in entry.lower() for keyword in ["assessment", "verification", "meeting", "review", "follow"]):
                timeline_score += 1
        timeline_score = min(timeline_score, 6)  # Cap at 6 points
    else:
        feedback.append("Did not provide exactly 3 timeline entries")
    
    score = summary_score + action_score + timeline_score
    
    return {
        "score": score,
        "max_score": 20,
        "breakdown": {
            "meeting_summary": summary_score,
            "action_items": action_score,
            "follow_up_timeline": timeline_score
        },
        "feedback": feedback
    }

def check_critical_failures(candidate, results):
    critical_failures = []
    
    # 1. Fundamental misunderstanding of labor relations principles
    if results["task1"]["score"] < 10 or results["task4"]["score"] < 10:
        critical_failures.append("Demonstrates fundamental misunderstanding of labor relations principles")
    
    # 2. Prioritizing administrative issues over safety issues
    task1 = candidate.get("task1", {})
    priority_ranking = task1.get("priority_ranking", [])
    if len(priority_ranking) == 5:
        safety_training_pos = priority_ranking[2] if len(priority_ranking) > 2 else 0
        ppe_pos = priority_ranking[3] if len(priority_ranking) > 3 else 0
        if not (safety_training_pos in [1, 2] or ppe_pos in [1, 2]):
            critical_failures.append("Prioritizes administrative issues over safety issues")
    
    # 3. Proposing actions that would violate the CBA
    # This is difficult to check automatically, would require NLP analysis
    
    # 4. Displaying unprofessional communication
    unprofessional_terms = ["stupid", "ridiculous", "absurd", "wrong", "incorrect", "fault", "blame", "idiot"]
    for task_id in ["task3", "task4"]:
        task_data = candidate.get(task_id, {})
        for key, value in task_data.items():
            if isinstance(value, str) and any(term in value.lower() for term in unprofessional_terms):
                critical_failures.append(f"Displays unprofessional communication in {task_id}")
                break
    
    # 5. Failing to address all required elements
    missing_elements = []
    for task_id in ["task1", "task2", "task3", "task4", "task5"]:
        if task_id not in candidate:
            missing_elements.append(task_id)
    
    if missing_elements:
        critical_failures.append(f"Failed to address required elements: {', '.join(missing_elements)}")
    
    return critical_failures

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate = load_json_file(submission_file)
    key = load_json_file(answer_key_file)
    
    # Evaluate each task
    results = {
        "task1": evaluate_task1(candidate.get("task1", {}), key.get("task1", {})),
        "task2": evaluate_task2(candidate.get("task2", {}), key.get("task2", {})),
        "task3": evaluate_task3(candidate.get("task3", {}), key.get("task3", {})),
        "task4": evaluate_task4(candidate.get("task4", {}), key.get("task4", {})),
        "task5": evaluate_task5(candidate.get("task5", {}), key.get("task5", {}))
    }
    
    # Calculate overall score
    total_score = sum(task["score"] for task in results.values())
    max_score = sum(task["max_score"] for task in results.values())
    overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    # Check for critical failures
    critical_failures = check_critical_failures(candidate, results)
    
    # Check if each task meets minimum threshold (60%)
    task_thresholds = {}
    for task_id, task_result in results.items():
        threshold_percentage = (task_result["score"] / task_result["max_score"]) * 100 if task_result["max_score"] > 0 else 0
        task_thresholds[task_id] = {
            "percentage": threshold_percentage,
            "passed": threshold_percentage >= 60
        }
    
    # Determine if candidate passed
    passed = overall_percentage >= 70 and all(task["passed"] for task in task_thresholds.values()) and not critical_failures
    
    # Prepare final results
    final_results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_score,
        "passed": passed,
        "task_results": results,
        "task_thresholds": task_thresholds,
        "critical_failures": critical_failures
    }
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(final_results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {round(overall_percentage, 2)}%")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

if __name__ == "__main__":
    main()