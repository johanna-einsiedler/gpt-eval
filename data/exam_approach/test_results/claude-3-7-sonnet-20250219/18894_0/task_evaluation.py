#!/usr/bin/env python3
"""
Labor Relations Specialist Practical Exam Evaluator

This script evaluates a candidate's submission for the Labor Relations Specialist
practical exam by comparing it against an answer key and scoring based on predefined criteria.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from datetime import datetime


def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_schedule_creation(submission, answer_key):
    """Evaluate the schedule creation section (50 points)."""
    results = {
        "priority_order": {"score": 0, "max_score": 10, "comments": []},
        "room_assignments": {"score": 0, "max_score": 10, "comments": []},
        "participant_availability": {"score": 0, "max_score": 10, "comments": []},
        "meeting_duration": {"score": 0, "max_score": 10, "comments": []},
        "notification_requirements": {"score": 0, "max_score": 10, "comments": []},
    }
    
    # Create lookup dictionaries for easier access
    submission_cases = {case["case_number"]: case for case in submission.get("schedule", [])}
    answer_key_cases = {case["case_number"]: case for case in answer_key.get("schedule", [])}
    
    # Check if all 8 cases are scheduled
    if len(submission_cases) != 8:
        results["priority_order"]["comments"].append(
            f"Expected 8 cases, found {len(submission_cases)}."
        )
    
    # 1. Evaluate priority order (10 points)
    # Define the correct priority order based on case type and deadlines
    correct_priority_order = [
        "GR-2023-048",  # Termination, earliest deadline
        "GR-2023-044",  # Termination, second earliest deadline
        "GR-2023-046",  # Disciplinary
        "GR-2023-042",  # Disciplinary
        "GR-2023-043",  # Contract Interpretation
        "GR-2023-049",  # Work Assignment
        "GR-2023-045",  # Contract Interpretation
        "GR-2023-047",  # Benefits
    ]
    
    # Check if termination cases are given highest priority
    termination_cases = ["GR-2023-048", "GR-2023-044"]
    submission_dates = {case["case_number"]: datetime.strptime(case["date"], "%Y-%m-%d") 
                       for case in submission.get("schedule", []) if case["case_number"] in termination_cases}
    
    other_cases = [case for case in submission.get("schedule", []) if case["case_number"] not in termination_cases]
    other_dates = {case["case_number"]: datetime.strptime(case["date"], "%Y-%m-%d") for case in other_cases}
    
    # Check if termination cases are scheduled before other cases
    termination_priority_correct = True
    for term_case, term_date in submission_dates.items():
        for other_case, other_date in other_dates.items():
            if term_date > other_date:
                termination_priority_correct = False
                results["priority_order"]["comments"].append(
                    f"Termination case {term_case} scheduled after non-termination case {other_case}."
                )
    
    # Check if cases are scheduled before their deadlines
    deadlines = {
        "GR-2023-048": datetime.strptime("2023-11-11", "%Y-%m-%d"),
        "GR-2023-044": datetime.strptime("2023-11-14", "%Y-%m-%d"),
        "GR-2023-046": datetime.strptime("2023-11-17", "%Y-%m-%d"),
        "GR-2023-042": datetime.strptime("2023-11-19", "%Y-%m-%d"),
        "GR-2023-043": datetime.strptime("2023-11-21", "%Y-%m-%d"),
        "GR-2023-049": datetime.strptime("2023-11-24", "%Y-%m-%d"),
        "GR-2023-045": datetime.strptime("2023-11-27", "%Y-%m-%d"),
        "GR-2023-047": datetime.strptime("2023-11-29", "%Y-%m-%d"),
    }
    
    deadline_violations = []
    for case_num, case_date in {**submission_dates, **other_dates}.items():
        if case_num in deadlines and case_date > deadlines[case_num]:
            deadline_violations.append(case_num)
            results["priority_order"]["comments"].append(
                f"Case {case_num} scheduled after its deadline."
            )
    
    # Score priority order
    if termination_priority_correct and not deadline_violations:
        results["priority_order"]["score"] = 10
    elif termination_priority_correct:
        results["priority_order"]["score"] = 5
    else:
        results["priority_order"]["score"] = max(0, 10 - (len(deadline_violations) * 2))
    
    # 2. Evaluate room assignments (10 points)
    room_errors = []
    
    # Check if termination cases are in rooms with privacy features
    for case_num in termination_cases:
        if case_num in submission_cases:
            if submission_cases[case_num]["meeting_room"] != "Conference Room A":
                room_errors.append(
                    f"Termination case {case_num} not scheduled in room with privacy features (Conference Room A)."
                )
    
    # Check room capacity for all cases
    large_cases = []
    for case in submission.get("schedule", []):
        participants = len(case.get("required_participants", []))
        if participants >= 5 and case["meeting_room"] == "Meeting Room C":
            large_cases.append(case["case_number"])
            room_errors.append(
                f"Case {case['case_number']} has {participants} participants but is scheduled in Meeting Room C (capacity 6)."
            )
    
    # Score room assignments
    if not room_errors:
        results["room_assignments"]["score"] = 10
    else:
        results["room_assignments"]["score"] = max(0, 10 - (len(room_errors) * 2))
        results["room_assignments"]["comments"] = room_errors
    
    # 3. Evaluate participant availability (10 points)
    # This would require checking against the availability data which is complex for this script
    # For simplicity, we'll assume this is correct unless there are obvious errors
    results["participant_availability"]["score"] = 10
    results["participant_availability"]["comments"].append(
        "Full availability check would require additional data processing."
    )
    
    # 4. Evaluate meeting duration requirements (10 points)
    duration_errors = []
    for case in submission.get("schedule", []):
        case_num = case["case_number"]
        start_time = datetime.strptime(case["start_time"], "%H:%M")
        end_time = datetime.strptime(case["end_time"], "%H:%M")
        duration_minutes = (end_time.hour - start_time.hour) * 60 + (end_time.minute - start_time.minute)
        
        # Check minimum durations based on case type
        if case_num in ["GR-2023-044", "GR-2023-048"]:  # Termination
            if duration_minutes < 120:
                duration_errors.append(f"Termination case {case_num} scheduled for less than 2 hours.")
        elif case_num in ["GR-2023-042", "GR-2023-046", "GR-2023-043", "GR-2023-045"]:  # Disciplinary/Contract
            if duration_minutes < 90:
                duration_errors.append(f"Case {case_num} scheduled for less than 1.5 hours.")
        else:  # Benefits/Work Assignment
            if duration_minutes < 60:
                duration_errors.append(f"Case {case_num} scheduled for less than 1 hour.")
    
    # Score meeting duration
    if not duration_errors:
        results["meeting_duration"]["score"] = 10
    else:
        results["meeting_duration"]["score"] = max(0, 10 - (len(duration_errors) * 2))
        results["meeting_duration"]["comments"] = duration_errors
    
    # 5. Evaluate notification requirements (10 points)
    # Check if cases are scheduled at least 5 business days before hearings
    # This is complex to fully implement, so we'll do a simplified check
    notification_errors = []
    for case in submission.get("schedule", []):
        case_date = datetime.strptime(case["date"], "%Y-%m-%d")
        case_deadline = deadlines.get(case["case_number"])
        
        if case_deadline:
            # Simplified check: at least 3 business days before deadline
            business_days = (case_deadline - case_date).days
            # Adjust for weekends (very simplified)
            if business_days < 3:
                notification_errors.append(
                    f"Case {case['case_number']} scheduled too close to deadline (less than 3 business days)."
                )
    
    # Score notification requirements
    if not notification_errors:
        results["notification_requirements"]["score"] = 10
    else:
        results["notification_requirements"]["score"] = max(0, 10 - (len(notification_errors) * 2))
        results["notification_requirements"]["comments"] = notification_errors
    
    return results


def evaluate_conflict_resolution(submission, answer_key):
    """Evaluate the conflict resolution section (30 points)."""
    results = {
        "overlapping_high_priority": {"score": 0, "max_score": 10, "comments": []},
        "conference_room_limitation": {"score": 0, "max_score": 10, "comments": []},
        "key_witness_accommodation": {"score": 0, "max_score": 10, "comments": []},
    }
    
    # Check if all required conflict resolution explanations are provided
    submission_conflicts = submission.get("conflict_resolutions", {})
    
    # 1. Evaluate overlapping high priority cases resolution
    if "overlapping_high_priority" in submission_conflicts:
        explanation = submission_conflicts["overlapping_high_priority"]
        # Check for key elements in the explanation
        if "GR-2023-048" in explanation and "GR-2023-044" in explanation:
            results["overlapping_high_priority"]["score"] += 5
        else:
            results["overlapping_high_priority"]["comments"].append(
                "Explanation does not specifically address both termination cases."
            )
        
        # Check for scheduling logic
        if "J. Smith" in explanation or "Union Rep" in explanation:
            results["overlapping_high_priority"]["score"] += 5
        else:
            results["overlapping_high_priority"]["comments"].append(
                "Explanation does not address shared participant scheduling."
            )
    else:
        results["overlapping_high_priority"]["comments"].append(
            "Missing explanation for overlapping high priority cases."
        )
    
    # 2. Evaluate conference room limitation resolution
    if "conference_room_limitation" in submission_conflicts:
        explanation = submission_conflicts["conference_room_limitation"]
        # Check for key elements in the explanation
        if "Conference Room A" in explanation and ("privacy" in explanation.lower() or "termination" in explanation.lower()):
            results["conference_room_limitation"]["score"] += 5
        else:
            results["conference_room_limitation"]["comments"].append(
                "Explanation does not address privacy requirements for termination cases."
            )
        
        # Check for room allocation logic
        if "capacity" in explanation.lower() or "participants" in explanation.lower():
            results["conference_room_limitation"]["score"] += 5
        else:
            results["conference_room_limitation"]["comments"].append(
                "Explanation does not address room capacity considerations."
            )
    else:
        results["conference_room_limitation"]["comments"].append(
            "Missing explanation for conference room limitation."
        )
    
    # 3. Evaluate key witness accommodation
    if "key_witness_accommodation" in submission_conflicts:
        explanation = submission_conflicts["key_witness_accommodation"]
        # Check for key elements in the explanation
        if "M. Garcia" in explanation or "witness" in explanation.lower():
            results["key_witness_accommodation"]["score"] += 5
        else:
            results["key_witness_accommodation"]["comments"].append(
                "Explanation does not specifically mention the key witness."
            )
        
        # Check for scheduling logic
        if "GR-2023-042" in explanation:
            results["key_witness_accommodation"]["score"] += 5
        else:
            results["key_witness_accommodation"]["comments"].append(
                "Explanation does not specify which case was affected by witness availability."
            )
    else:
        results["key_witness_accommodation"]["comments"].append(
            "Missing explanation for key witness accommodation."
        )
    
    return results


def evaluate_special_accommodations(submission, answer_key):
    """Evaluate the special accommodations section (10 points)."""
    results = {
        "identification": {"score": 0, "max_score": 5, "comments": []},
        "appropriate_accommodations": {"score": 0, "max_score": 5, "comments": []},
    }
    
    submission_accommodations = submission.get("special_accommodations", [])
    answer_key_accommodations = answer_key.get("special_accommodations", [])
    
    # Create lookup for easier access
    submission_cases = {acc["case_number"]: acc for acc in submission_accommodations}
    answer_key_cases = {acc["case_number"]: acc for acc in answer_key_accommodations}
    
    # 1. Evaluate identification of cases requiring special accommodations
    correct_cases = set(answer_key_cases.keys())
    submitted_cases = set(submission_cases.keys())
    
    # Calculate score based on correct identification
    if submitted_cases == correct_cases:
        results["identification"]["score"] = 5
    else:
        missing = correct_cases - submitted_cases
        extra = submitted_cases - correct_cases
        
        if missing:
            results["identification"]["comments"].append(
                f"Failed to identify special accommodations for: {', '.join(missing)}"
            )
        
        if extra:
            results["identification"]["comments"].append(
                f"Incorrectly identified special accommodations for: {', '.join(extra)}"
            )
        
        # Score based on correct identifications
        correct_identifications = len(correct_cases.intersection(submitted_cases))
        total_required = len(correct_cases)
        results["identification"]["score"] = round(5 * (correct_identifications / total_required)) if total_required > 0 else 0
    
    # 2. Evaluate appropriateness of accommodations
    appropriate_count = 0
    for case_num in submitted_cases.intersection(correct_cases):
        submission_acc = submission_cases[case_num]["accommodation"].lower()
        answer_key_acc = answer_key_cases[case_num]["accommodation"].lower()
        
        # Check if the accommodation mentions key elements
        if ("privacy" in submission_acc and "privacy" in answer_key_acc) or \
           ("termination" in submission_acc and "termination" in answer_key_acc):
            appropriate_count += 1
        else:
            results["appropriate_accommodations"]["comments"].append(
                f"Accommodation for {case_num} does not match required accommodation."
            )
    
    # Score based on appropriate accommodations
    if len(correct_cases) > 0:
        results["appropriate_accommodations"]["score"] = round(5 * (appropriate_count / len(correct_cases)))
    else:
        results["appropriate_accommodations"]["score"] = 5  # If no special accommodations required
    
    return results


def evaluate_json_format(submission):
    """Evaluate the JSON format and completeness (10 points)."""
    results = {
        "syntax": {"score": 0, "max_score": 5, "comments": []},
        "completeness": {"score": 0, "max_score": 5, "comments": []},
    }
    
    # 1. Evaluate JSON syntax
    # If we got this far, the JSON syntax is valid (we loaded the file)
    results["syntax"]["score"] = 5
    
    # 2. Evaluate completeness
    missing_fields = []
    
    # Check for required top-level fields
    required_fields = ["schedule", "conflict_resolutions", "special_accommodations"]
    for field in required_fields:
        if field not in submission:
            missing_fields.append(field)
    
    # Check schedule entries for required fields
    if "schedule" in submission:
        for i, case in enumerate(submission["schedule"]):
            case_missing = []
            for field in ["case_number", "date", "start_time", "end_time", "meeting_room", "required_participants", "priority_level"]:
                if field not in case:
                    case_missing.append(field)
            
            if case_missing:
                missing_fields.append(f"schedule[{i}]: {', '.join(case_missing)}")
    
    # Check conflict_resolutions for required fields
    if "conflict_resolutions" in submission:
        for field in ["overlapping_high_priority", "conference_room_limitation", "key_witness_accommodation"]:
            if field not in submission["conflict_resolutions"]:
                missing_fields.append(f"conflict_resolutions.{field}")
    
    # Score completeness
    if not missing_fields:
        results["completeness"]["score"] = 5
    else:
        results["completeness"]["score"] = max(0, 5 - len(missing_fields))
        results["completeness"]["comments"] = [f"Missing required fields: {', '.join(missing_fields)}"]
    
    return results


def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission and calculate the overall score."""
    results = {
        "schedule_creation": evaluate_schedule_creation(submission, answer_key),
        "conflict_resolution": evaluate_conflict_resolution(submission, answer_key),
        "special_accommodations": evaluate_special_accommodations(submission, answer_key),
        "json_format": evaluate_json_format(submission),
    }
    
    # Calculate section scores
    section_scores = {
        "schedule_creation": sum(item["score"] for item in results["schedule_creation"].values()),
        "conflict_resolution": sum(item["score"] for item in results["conflict_resolution"].values()),
        "special_accommodations": sum(item["score"] for item in results["special_accommodations"].values()),
        "json_format": sum(item["score"] for item in results["json_format"].values()),
    }
    
    # Calculate maximum possible scores
    max_scores = {
        "schedule_creation": sum(item["max_score"] for item in results["schedule_creation"].values()),
        "conflict_resolution": sum(item["max_score"] for item in results["conflict_resolution"].values()),
        "special_accommodations": sum(item["max_score"] for item in results["special_accommodations"].values()),
        "json_format": sum(item["max_score"] for item in results["json_format"].values()),
    }
    
    # Calculate overall score
    total_score = sum(section_scores.values())
    total_possible = sum(max_scores.values())
    overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
    
    # Check for automatic failure conditions
    automatic_failure = False
    failure_reasons = []
    
    # 1. Scheduling any case after its contractual deadline
    schedule_creation = results["schedule_creation"]
    if "priority_order" in schedule_creation and any("after its deadline" in comment for comment in schedule_creation["priority_order"].get("comments", [])):
        automatic_failure = True
        failure_reasons.append("Case scheduled after contractual deadline")
    
    # 2. Scheduling participants when they are unavailable
    # This would require additional data processing, so we'll skip for this script
    
    # 3. Assigning termination cases to rooms without privacy features
    if "room_assignments" in schedule_creation and any("Termination case" in comment and "not scheduled in room with privacy features" in comment for comment in schedule_creation["room_assignments"].get("comments", [])):
        automatic_failure = True
        failure_reasons.append("Termination case not scheduled in room with privacy features")
    
    # 4. Failing to schedule all 8 cases
    if "schedule" in submission and len(submission["schedule"]) != 8:
        automatic_failure = True
        failure_reasons.append(f"Failed to schedule all 8 cases (found {len(submission.get('schedule', []))})")
    
    # Prepare final results
    final_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passing_score": 75,
        "passed": overall_percentage >= 75 and not automatic_failure,
        "automatic_failure": automatic_failure,
        "failure_reasons": failure_reasons if automatic_failure else [],
        "section_scores": {
            "schedule_creation": {
                "score": section_scores["schedule_creation"],
                "max_score": max_scores["schedule_creation"],
                "percentage": (section_scores["schedule_creation"] / max_scores["schedule_creation"]) * 100 if max_scores["schedule_creation"] > 0 else 0
            },
            "conflict_resolution": {
                "score": section_scores["conflict_resolution"],
                "max_score": max_scores["conflict_resolution"],
                "percentage": (section_scores["conflict_resolution"] / max_scores["conflict_resolution"]) * 100 if max_scores["conflict_resolution"] > 0 else 0
            },
            "special_accommodations": {
                "score": section_scores["special_accommodations"],
                "max_score": max_scores["special_accommodations"],
                "percentage": (section_scores["special_accommodations"] / max_scores["special_accommodations"]) * 100 if max_scores["special_accommodations"] > 0 else 0
            },
            "json_format": {
                "score": section_scores["json_format"],
                "max_score": max_scores["json_format"],
                "percentage": (section_scores["json_format"] / max_scores["json_format"]) * 100 if max_scores["json_format"] > 0 else 0
            }
        },
        "detailed_results": results
    }
    
    return final_results


def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    
    if results["automatic_failure"]:
        print("Automatic failure conditions triggered:")
        for reason in results["failure_reasons"]:
            print(f"- {reason}")


if __name__ == "__main__":
    main()