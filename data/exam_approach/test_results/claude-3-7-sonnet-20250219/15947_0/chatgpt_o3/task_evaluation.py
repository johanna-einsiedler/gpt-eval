#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_executive_summary(submission: str, answer_key: str) -> Tuple[int, str]:
    """Evaluate the executive summary section (10 points)."""
    # Check if submission is empty
    if not submission.strip():
        return 0, "Executive summary is empty"
    
    # Check word count (150-300 words)
    word_count = len(submission.split())
    if word_count < 150 or word_count > 300:
        note = f"Word count ({word_count}) outside required range (150-300)"
        score = max(5, 10 - abs(word_count - 225) // 30)  # Deduct points based on deviation
    else:
        note = "Word count within required range"
        score = 7  # Start with 7 points for correct length
    
    # Check for key content elements
    key_elements = [
        "test", "objectives", "recovery", "systems", "results", 
        "issues", "recommendations", "findings"
    ]
    
    elements_found = sum(1 for element in key_elements if element.lower() in submission.lower())
    content_score = min(3, elements_found * 3 // len(key_elements))
    
    score += content_score
    note += f"; Contains {elements_found}/{len(key_elements)} key elements"
    
    return min(10, score), note

def evaluate_test_objectives(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the test objectives section (5 points)."""
    score = 0
    notes = []
    
    # Check primary objective (2 points)
    if submission.get("primary_objective") == answer_key.get("primary_objective"):
        score += 2
        notes.append("Primary objective correctly identified")
    else:
        notes.append("Primary objective incorrect or missing")
    
    # Check secondary objectives (3 points)
    key_objectives = set(obj.lower() for obj in answer_key.get("secondary_objectives", []))
    submission_objectives = set(obj.lower() for obj in submission.get("secondary_objectives", []))
    
    if key_objectives == submission_objectives:
        score += 3
        notes.append("All secondary objectives correctly identified")
    else:
        # Calculate overlap
        overlap = key_objectives.intersection(submission_objectives)
        missing = key_objectives - submission_objectives
        extra = submission_objectives - key_objectives
        
        overlap_percentage = len(overlap) / len(key_objectives) if key_objectives else 0
        partial_score = min(3, round(overlap_percentage * 3))
        score += partial_score
        
        if missing:
            notes.append(f"Missing {len(missing)}/{len(key_objectives)} secondary objectives")
        if extra:
            notes.append(f"Included {len(extra)} incorrect secondary objectives")
        
        notes.append(f"Identified {len(overlap)}/{len(key_objectives)} correct secondary objectives")
    
    return score, "; ".join(notes)

def evaluate_test_planning(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the test planning section (10 points)."""
    score = 0
    notes = []
    
    # Check planning timeline (3 points)
    if submission.get("planning_timeline"):
        # Look for key dates from the answer key
        key_dates = ["September 15", "September 22", "October 10"]
        timeline = submission.get("planning_timeline", "")
        dates_found = sum(1 for date in key_dates if date in timeline)
        
        timeline_score = min(3, dates_found)
        score += timeline_score
        notes.append(f"Planning timeline includes {dates_found}/{len(key_dates)} key dates")
    else:
        notes.append("Planning timeline missing")
    
    # Check stakeholders (4 points)
    key_stakeholders = set(s.lower() for s in answer_key.get("stakeholders_involved", []))
    submission_stakeholders = set(s.lower() for s in submission.get("stakeholders_involved", []))
    
    if key_stakeholders and submission_stakeholders:
        overlap = key_stakeholders.intersection(submission_stakeholders)
        overlap_percentage = len(overlap) / len(key_stakeholders)
        stakeholder_score = min(4, round(overlap_percentage * 4))
        score += stakeholder_score
        notes.append(f"Identified {len(overlap)}/{len(key_stakeholders)} key stakeholders")
    else:
        notes.append("Stakeholders section incomplete or missing")
    
    # Check resource allocation (3 points)
    if submission.get("resource_allocation"):
        # Look for key resource terms
        key_resources = ["data center", "documentation", "backup", "communication", "emergency operations"]
        resource_text = submission.get("resource_allocation", "").lower()
        resources_found = sum(1 for resource in key_resources if resource in resource_text)
        
        resource_score = min(3, resources_found)
        score += resource_score
        notes.append(f"Resource allocation includes {resources_found}/{len(key_resources)} key resources")
    else:
        notes.append("Resource allocation missing")
    
    return score, "; ".join(notes)

def evaluate_test_schedule(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the test schedule section (10 points)."""
    score = 0
    notes = []
    
    # Check dates (4 points)
    correct_date = 0
    if submission.get("start_date") == answer_key.get("start_date"):
        correct_date += 1
    if submission.get("end_date") == answer_key.get("end_date"):
        correct_date += 1
    if submission.get("start_time") == answer_key.get("start_time"):
        correct_date += 1
    if submission.get("end_time") == answer_key.get("end_time"):
        correct_date += 1
    
    date_score = min(4, correct_date)
    score += date_score
    notes.append(f"Correctly identified {correct_date}/4 schedule dates/times")
    
    # Check key milestones (6 points)
    submission_milestones = submission.get("key_milestones", [])
    
    if submission_milestones:
        # Check for required milestone dates
        key_dates = ["2023-10-15", "2023-10-17", "2023-10-24"]
        dates_found = sum(1 for milestone in submission_milestones 
                         if any(date in milestone.get("date", "") for date in key_dates))
        
        # Check for key activities
        key_activities = ["test", "debrief", "review", "report"]
        activities_found = sum(1 for milestone in submission_milestones 
                              if any(activity in milestone.get("activity", "").lower() for activity in key_activities))
        
        milestone_score = min(6, dates_found + activities_found)
        score += milestone_score
        notes.append(f"Milestones include {dates_found}/{len(key_dates)} key dates and {activities_found}/{len(key_activities)} key activities")
    else:
        notes.append("Key milestones missing")
    
    return score, "; ".join(notes)

def evaluate_test_execution(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the test execution section (10 points)."""
    score = 0
    notes = []
    
    # Check methodology (3 points)
    if submission.get("methodology"):
        # Look for key methodology terms
        key_terms = ["simulation", "scenario", "emergency operations center", "alternate data center"]
        methodology_text = submission.get("methodology", "").lower()
        terms_found = sum(1 for term in key_terms if term in methodology_text)
        
        methodology_score = min(3, terms_found)
        score += methodology_score
        notes.append(f"Methodology includes {terms_found}/{len(key_terms)} key elements")
    else:
        notes.append("Methodology description missing")
    
    # Check participants (3 points)
    key_participants = set(p.lower() for p in answer_key.get("participants", []))
    submission_participants = set(p.lower() for p in submission.get("participants", []))
    
    if key_participants and submission_participants:
        overlap = key_participants.intersection(submission_participants)
        overlap_percentage = len(overlap) / len(key_participants)
        participant_score = min(3, round(overlap_percentage * 3))
        score += participant_score
        notes.append(f"Identified {len(overlap)}/{len(key_participants)} key participants")
    else:
        notes.append("Participants section incomplete or missing")
    
    # Check deviations from plan (4 points)
    key_deviations = set(d.lower() for d in answer_key.get("deviations_from_plan", []))
    submission_deviations = set(d.lower() for d in submission.get("deviations_from_plan", []))
    
    if key_deviations and submission_deviations:
        # Check for key deviation concepts rather than exact matches
        key_deviation_concepts = ["network administrator", "communication", "outdated", "vpn"]
        concepts_found = sum(1 for concept in key_deviation_concepts 
                            if any(concept in deviation for deviation in submission_deviations))
        
        deviation_score = min(4, concepts_found)
        score += deviation_score
        notes.append(f"Deviations include {concepts_found}/{len(key_deviation_concepts)} key issues")
    else:
        notes.append("Deviations from plan missing")
    
    return score, "; ".join(notes)

def evaluate_test_results(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the test results section (15 points)."""
    score = 0
    notes = []
    
    # Check recovery times (3 points)
    if submission.get("recovery_time_achieved") == answer_key.get("recovery_time_achieved"):
        score += 2
        notes.append("Recovery time correctly reported")
    else:
        notes.append("Recovery time incorrect")
    
    if submission.get("recovery_point_achieved") == answer_key.get("recovery_point_achieved"):
        score += 1
        notes.append("Recovery point correctly reported")
    else:
        notes.append("Recovery point incorrect")
    
    # Check system recovery rates (9 points)
    submission_systems = submission.get("system_recovery_rates", [])
    answer_systems = answer_key.get("system_recovery_rates", [])
    
    if submission_systems:
        # Check number of systems reported
        systems_count = min(len(submission_systems), len(answer_systems))
        systems_percentage = systems_count / len(answer_systems) if answer_systems else 0
        
        # Check accuracy of reported systems
        correct_systems = 0
        for sub_system in submission_systems:
            for ans_system in answer_systems:
                if (sub_system.get("system_name") == ans_system.get("system_name") and
                    sub_system.get("component") == ans_system.get("component") and
                    sub_system.get("target_time") == ans_system.get("target_time") and
                    sub_system.get("actual_time") == ans_system.get("actual_time") and
                    sub_system.get("status") == ans_system.get("status")):
                    correct_systems += 1
                    break
        
        accuracy_percentage = correct_systems / len(answer_systems) if answer_systems else 0
        
        systems_score = min(9, round((systems_percentage * 4) + (accuracy_percentage * 5)))
        score += systems_score
        notes.append(f"Reported {systems_count}/{len(answer_systems)} systems with {correct_systems} correctly detailed")
    else:
        notes.append("System recovery rates missing")
    
    # Check success rate (3 points)
    submission_rate = submission.get("success_rate", 0)
    answer_rate = answer_key.get("success_rate", 0)
    
    if abs(submission_rate - answer_rate) < 0.01:  # Allow small rounding differences
        score += 3
        notes.append("Success rate correctly calculated")
    else:
        # Partial credit for being close
        if abs(submission_rate - answer_rate) < 0.1:
            score += 1
            notes.append("Success rate calculation slightly off")
        else:
            notes.append("Success rate calculation incorrect")
    
    return score, "; ".join(notes)

def evaluate_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the analysis section (15 points)."""
    score = 0
    notes = []
    
    # Check key findings (5 points)
    submission_findings = submission.get("key_findings", [])
    if submission_findings:
        # Look for key concepts in findings
        key_concepts = [
            "69.2%", "recovery point", "documentation", "configuration", 
            "communication", "cross-training"
        ]
        
        concepts_found = 0
        for concept in key_concepts:
            if any(concept.lower() in finding.lower() for finding in submission_findings):
                concepts_found += 1
        
        findings_score = min(5, round(concepts_found * 5 / len(key_concepts)))
        score += findings_score
        notes.append(f"Key findings include {concepts_found}/{len(key_concepts)} important concepts")
    else:
        notes.append("Key findings missing")
    
    # Check gaps identified (5 points)
    submission_gaps = submission.get("gaps_identified", [])
    if submission_gaps:
        # Look for key gap concepts
        key_gaps = [
            "documentation", "configuration", "backup", "cross-training", 
            "escalation", "communication"
        ]
        
        gaps_found = 0
        for gap in key_gaps:
            if any(gap.lower() in g.lower() for g in submission_gaps):
                gaps_found += 1
        
        gaps_score = min(5, round(gaps_found * 5 / len(key_gaps)))
        score += gaps_score
        notes.append(f"Gaps identified include {gaps_found}/{len(key_gaps)} key issues")
    else:
        notes.append("Gaps identification missing")
    
    # Check root causes (5 points)
    submission_causes = submission.get("root_causes", [])
    if submission_causes:
        # Look for key root cause concepts
        key_causes = [
            "change management", "configuration management", "backup", 
            "previous test", "cross-training", "communication"
        ]
        
        causes_found = 0
        for cause in key_causes:
            if any(cause.lower() in c.lower() for c in submission_causes):
                causes_found += 1
        
        causes_score = min(5, round(causes_found * 5 / len(key_causes)))
        score += causes_score
        notes.append(f"Root causes include {causes_found}/{len(key_causes)} key factors")
    else:
        notes.append("Root causes missing")
    
    return score, "; ".join(notes)

def evaluate_conclusions(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the conclusions section (10 points)."""
    score = 0
    notes = []
    
    # Check overall assessment (4 points)
    if submission.get("overall_assessment"):
        # Look for key assessment concepts
        key_concepts = ["objectives", "69.2%", "documentation", "gaps"]
        assessment_text = submission.get("overall_assessment", "").lower()
        concepts_found = sum(1 for concept in key_concepts if concept.lower() in assessment_text)
        
        assessment_score = min(4, concepts_found)
        score += assessment_score
        notes.append(f"Overall assessment includes {concepts_found}/{len(key_concepts)} key elements")
    else:
        notes.append("Overall assessment missing")
    
    # Check compliance status (3 points)
    if submission.get("compliance_status"):
        # Look for key compliance concepts
        key_concepts = ["regulatory", "ffiec", "compliance", "risk"]
        compliance_text = submission.get("compliance_status", "").lower()
        concepts_found = sum(1 for concept in key_concepts if concept.lower() in compliance_text)
        
        compliance_score = min(3, concepts_found)
        score += compliance_score
        notes.append(f"Compliance status includes {concepts_found}/{len(key_concepts)} key elements")
    else:
        notes.append("Compliance status missing")
    
    # Check maturity level (3 points)
    if submission.get("maturity_level"):
        # Look for key maturity concepts
        key_concepts = ["maturity", "improvement", "recurring", "process"]
        maturity_text = submission.get("maturity_level", "").lower()
        concepts_found = sum(1 for concept in key_concepts if concept.lower() in maturity_text)
        
        maturity_score = min(3, concepts_found)
        score += maturity_score
        notes.append(f"Maturity level includes {concepts_found}/{len(key_concepts)} key elements")
    else:
        notes.append("Maturity level assessment missing")
    
    return score, "; ".join(notes)

def evaluate_recommendations(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, str]:
    """Evaluate the recommendations section (15 points)."""
    score = 0
    notes = []
    
    submission_recommendations = submission.get("recommendations", [])
    
    if not submission_recommendations:
        return 0, "Recommendations missing"
    
    # Check number of recommendations (3 points)
    rec_count = len(submission_recommendations)
    if rec_count >= 3:
        score += 3
        notes.append(f"Provided {rec_count} recommendations (minimum 3 required)")
    else:
        score += rec_count
        notes.append(f"Only provided {rec_count}/3 required recommendations")
    
    # Check recommendation quality (12 points)
    quality_score = 0
    
    # Check for priorities
    priorities_included = all("priority" in rec and rec["priority"] in ["High", "Medium", "Low"] 
                             for rec in submission_recommendations)
    if priorities_included:
        quality_score += 3
        notes.append("All recommendations include appropriate priorities")
    else:
        notes.append("Some recommendations missing proper priorities")
    
    # Check for specific descriptions
    specific_descriptions = all(len(rec.get("description", "")) > 20 for rec in submission_recommendations)
    if specific_descriptions:
        quality_score += 3
        notes.append("All recommendations include specific descriptions")
    else:
        notes.append("Some recommendations lack specific descriptions")
    
    # Check for owners
    owners_included = all("owner" in rec and len(rec["owner"]) > 0 for rec in submission_recommendations)
    if owners_included:
        quality_score += 3
        notes.append("All recommendations include owners")
    else:
        notes.append("Some recommendations missing owners")
    
    # Check for target dates
    date_format = True
    for rec in submission_recommendations:
        if "target_date" not in rec:
            date_format = False
            break
        date = rec["target_date"]
        if not isinstance(date, str) or len(date) != 10 or date[4] != '-' or date[7] != '-':
            date_format = False
            break
    
    if date_format:
        quality_score += 3
        notes.append("All recommendations include properly formatted target dates")
    else:
        notes.append("Some recommendations missing proper target dates")
    
    score += quality_score
    
    return score, "; ".join(notes)

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "sections": {},
        "total_score": 0,
        "max_possible": 100,
        "overall_score": 0.0,
        "passed": False
    }
    
    # Evaluate each section
    exec_score, exec_notes = evaluate_executive_summary(
        submission.get("executive_summary", ""), 
        answer_key.get("executive_summary", "")
    )
    results["sections"]["executive_summary"] = {
        "score": exec_score,
        "max_points": 10,
        "notes": exec_notes
    }
    results["total_score"] += exec_score
    
    obj_score, obj_notes = evaluate_test_objectives(
        submission.get("test_objectives", {}), 
        answer_key.get("test_objectives", {})
    )
    results["sections"]["test_objectives"] = {
        "score": obj_score,
        "max_points": 5,
        "notes": obj_notes
    }
    results["total_score"] += obj_score
    
    plan_score, plan_notes = evaluate_test_planning(
        submission.get("test_planning", {}), 
        answer_key.get("test_planning", {})
    )
    results["sections"]["test_planning"] = {
        "score": plan_score,
        "max_points": 10,
        "notes": plan_notes
    }
    results["total_score"] += plan_score
    
    sched_score, sched_notes = evaluate_test_schedule(
        submission.get("test_schedule", {}), 
        answer_key.get("test_schedule", {})
    )
    results["sections"]["test_schedule"] = {
        "score": sched_score,
        "max_points": 10,
        "notes": sched_notes
    }
    results["total_score"] += sched_score
    
    exec_score, exec_notes = evaluate_test_execution(
        submission.get("test_execution", {}), 
        answer_key.get("test_execution", {})
    )
    results["sections"]["test_execution"] = {
        "score": exec_score,
        "max_points": 10,
        "notes": exec_notes
    }
    results["total_score"] += exec_score
    
    res_score, res_notes = evaluate_test_results(
        submission.get("test_results", {}), 
        answer_key.get("test_results", {})
    )
    results["sections"]["test_results"] = {
        "score": res_score,
        "max_points": 15,
        "notes": res_notes
    }
    results["total_score"] += res_score
    
    ana_score, ana_notes = evaluate_analysis(
        submission.get("analysis", {}), 
        answer_key.get("analysis", {})
    )
    results["sections"]["analysis"] = {
        "score": ana_score,
        "max_points": 15,
        "notes": ana_notes
    }
    results["total_score"] += ana_score
    
    conc_score, conc_notes = evaluate_conclusions(
        submission.get("conclusions", {}), 
        answer_key.get("conclusions", {})
    )
    results["sections"]["conclusions"] = {
        "score": conc_score,
        "max_points": 10,
        "notes": conc_notes
    }
    results["total_score"] += conc_score
    
    rec_score, rec_notes = evaluate_recommendations(
        submission.get("recommendations", []), 
        answer_key.get("recommendations", [])
    )
    results["sections"]["recommendations"] = {
        "score": rec_score,
        "max_points": 15,
        "notes": rec_notes
    }
    results["total_score"] += rec_score
    
    # Calculate overall score as percentage
    results["overall_score"] = round((results["total_score"] / results["max_possible"]) * 100, 2)
    
    # Determine if passed (70% or higher)
    results["passed"] = results["overall_score"] >= 70.0
    
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
    print(f"Overall score: {results['overall_score']}% ({results['total_score']}/{results['max_possible']} points)")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()