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

def evaluate_resource_gap_analysis(submission: List, answer_key: List) -> Tuple[int, List[Dict]]:
    """Evaluate the resource gap analysis section."""
    max_points = 40
    points_per_gap = 5
    max_gaps = 8
    
    # Count the number of valid gaps (up to max_gaps)
    num_gaps = min(len(submission), max_gaps)
    
    # Check if there are at least 5 gaps identified
    if num_gaps < 5:
        feedback = "Failed to identify at least 5 resource gaps."
        return 0, [{"feedback": feedback, "points_earned": 0, "max_points": max_points}]
    
    # Check if there are at least 2 high-priority gaps
    high_priority_gaps = sum(1 for gap in submission if gap.get("priority_level") == "high")
    if high_priority_gaps < 2:
        feedback = f"Only identified {high_priority_gaps} high-priority gaps. At least 2 required."
        return 0, [{"feedback": feedback, "points_earned": 0, "max_points": max_points}]
    
    # Check if at least 2 different resource categories are covered
    categories = set(gap.get("resource_category") for gap in submission)
    if len(categories) < 2:
        feedback = f"Only covered {len(categories)} resource categories. At least 2 different categories required."
        return 0, [{"feedback": feedback, "points_earned": 0, "max_points": max_points}]
    
    # Evaluate each gap
    gap_evaluations = []
    total_points = 0
    
    for i, gap in enumerate(submission[:max_gaps]):
        gap_points = 0
        gap_feedback = []
        
        # Check if resource category is valid
        if gap.get("resource_category") in ["human", "technical", "material"]:
            gap_points += 1
        else:
            gap_feedback.append("Invalid resource category")
        
        # Check if resource type is provided
        if gap.get("resource_type"):
            gap_points += 1
        else:
            gap_feedback.append("Missing resource type")
        
        # Check if gap description is provided and has sufficient length
        description = gap.get("gap_description", "")
        if description and 50 <= len(description) <= 200:
            gap_points += 1
        else:
            gap_feedback.append("Gap description missing or invalid length (should be 50-200 characters)")
        
        # Check if impact is provided and has sufficient length
        impact = gap.get("impact_if_not_addressed", "")
        if impact and 50 <= len(impact) <= 200:
            gap_points += 1
        else:
            gap_feedback.append("Impact description missing or invalid length (should be 50-200 characters)")
        
        # Check if supporting evidence references specific document and section
        evidence = gap.get("supporting_evidence", "")
        if evidence and ":" in evidence and any(doc in evidence for doc in ["Project Charter", "Project Requirements", "Budget Constraints", "Stakeholder Expectations", "Resource Allocation Matrix"]):
            gap_points += 1
        else:
            gap_feedback.append("Supporting evidence should reference specific document and section")
        
        # Calculate points for this gap
        points_earned = gap_points * (points_per_gap / 5)
        total_points += points_earned
        
        # Create evaluation for this gap
        if gap_feedback:
            feedback = f"Gap {i+1}: " + "; ".join(gap_feedback)
        else:
            feedback = f"Gap {i+1}: All criteria met"
        
        gap_evaluations.append({
            "gap_number": i+1,
            "feedback": feedback,
            "points_earned": points_earned,
            "max_points": points_per_gap
        })
    
    return total_points, gap_evaluations

def evaluate_resource_recommendations(submission: List, answer_key: List) -> Tuple[int, List[Dict]]:
    """Evaluate the resource recommendations section."""
    max_points = 40
    points_per_recommendation = 5
    max_recommendations = 8
    
    # Count the number of valid recommendations (up to max_recommendations)
    num_recommendations = min(len(submission), max_recommendations)
    
    # Check if there are at least 5 recommendations
    if num_recommendations < 5:
        feedback = "Failed to provide at least 5 resource recommendations."
        return 0, [{"feedback": feedback, "points_earned": 0, "max_points": max_points}]
    
    # Evaluate each recommendation
    recommendation_evaluations = []
    total_points = 0
    
    for i, rec in enumerate(submission[:max_recommendations]):
        rec_points = 0
        rec_feedback = []
        
        # Check if resource description is provided
        if rec.get("resource_description"):
            rec_points += 1
        else:
            rec_feedback.append("Missing resource description")
        
        # Check if quantity is provided and is a number
        quantity = rec.get("quantity_needed")
        if quantity is not None and isinstance(quantity, (int, float)) and quantity > 0:
            rec_points += 1
        else:
            rec_feedback.append("Invalid or missing quantity")
        
        # Check if skills are provided (2-5 skills)
        skills = rec.get("skills_required", [])
        if isinstance(skills, list) and 2 <= len(skills) <= 5:
            rec_points += 1
        else:
            rec_feedback.append("Skills should include 2-5 items")
        
        # Check if timing is valid
        timing = rec.get("timing_required")
        if timing in ["Q1", "Q2", "Q3", "Q4"]:
            rec_points += 1
        else:
            rec_feedback.append("Invalid timing (should be Q1, Q2, Q3, or Q4)")
        
        # Check if justification is provided and has sufficient length
        justification = rec.get("justification", "")
        if justification and 50 <= len(justification) <= 200:
            rec_points += 1
        else:
            rec_feedback.append("Justification missing or invalid length (should be 50-200 characters)")
        
        # Calculate points for this recommendation
        points_earned = rec_points * (points_per_recommendation / 5)
        total_points += points_earned
        
        # Create evaluation for this recommendation
        if rec_feedback:
            feedback = f"Recommendation {i+1}: " + "; ".join(rec_feedback)
        else:
            feedback = f"Recommendation {i+1}: All criteria met"
        
        recommendation_evaluations.append({
            "recommendation_number": i+1,
            "feedback": feedback,
            "points_earned": points_earned,
            "max_points": points_per_recommendation
        })
    
    return total_points, recommendation_evaluations

def evaluate_budget_impact(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate the budget impact summary section."""
    max_points = 20
    budget_points = 0
    budget_feedback = []
    
    # Check if total estimated cost is provided and is a number
    total_cost = submission.get("total_estimated_cost")
    if total_cost is not None and isinstance(total_cost, (int, float)):
        budget_points += 7
    else:
        budget_feedback.append("Invalid or missing total estimated cost")
    
    # Check if alignment with constraints is provided
    alignment = submission.get("alignment_with_constraints", "")
    if alignment and (alignment == "within_budget" or alignment.startswith("exceeds_budget_by_")):
        budget_points += 7
    else:
        budget_feedback.append("Invalid alignment with constraints format")
    
    # Check if cost saving measures are provided
    if submission.get("cost_saving_measures"):
        budget_points += 6
    else:
        budget_feedback.append("Missing cost saving measures")
    
    # Check if total cost exceeds available budget by more than 10%
    # For simplicity, we'll assume available budget is $615,000 (as mentioned in evaluation info)
    available_budget = 615000
    if total_cost is not None and isinstance(total_cost, (int, float)) and total_cost > available_budget * 1.1:
        budget_feedback.append(f"Total cost ({total_cost}) exceeds available budget ({available_budget}) by more than 10%")
        return 0, {"feedback": "; ".join(budget_feedback), "points_earned": 0, "max_points": max_points}
    
    # Create evaluation for budget impact
    if budget_feedback:
        feedback = "; ".join(budget_feedback)
    else:
        feedback = "All budget criteria met"
    
    return budget_points, {"feedback": feedback, "points_earned": budget_points, "max_points": max_points}

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_sections": {}
    }
    
    # Evaluate resource gap analysis
    gap_points, gap_evaluations = evaluate_resource_gap_analysis(
        submission.get("resource_gap_analysis", []),
        answer_key.get("resource_gap_analysis", [])
    )
    results["evaluation_sections"]["resource_gap_analysis"] = {
        "points_earned": gap_points,
        "max_points": 40,
        "evaluations": gap_evaluations
    }
    
    # Evaluate resource recommendations
    rec_points, rec_evaluations = evaluate_resource_recommendations(
        submission.get("resource_recommendations", []),
        answer_key.get("resource_recommendations", [])
    )
    results["evaluation_sections"]["resource_recommendations"] = {
        "points_earned": rec_points,
        "max_points": 40,
        "evaluations": rec_evaluations
    }
    
    # Evaluate budget impact summary
    budget_points, budget_evaluation = evaluate_budget_impact(
        submission.get("budget_impact_summary", {}),
        answer_key.get("budget_impact_summary", {})
    )
    results["evaluation_sections"]["budget_impact_summary"] = {
        "points_earned": budget_points,
        "max_points": 20,
        "evaluation": budget_evaluation
    }
    
    # Calculate overall score
    total_points = gap_points + rec_points + budget_points
    max_points = 100
    overall_score = (total_points / max_points) * 100
    
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["overall_score"] = overall_score
    results["pass_fail"] = "PASS" if overall_score >= 70 else "FAIL"
    
    # Check for critical failures
    critical_failures = []
    
    # Check if any high-priority gaps were identified
    high_priority_gaps = any(gap.get("priority_level") == "high" for gap in submission.get("resource_gap_analysis", []))
    if not high_priority_gaps:
        critical_failures.append("Failed to identify any high-priority resource gaps")
    
    # Check if budget is exceeded by more than 10%
    available_budget = 615000  # From evaluation info
    total_cost = submission.get("budget_impact_summary", {}).get("total_estimated_cost")
    if total_cost is not None and isinstance(total_cost, (int, float)) and total_cost > available_budget * 1.1:
        critical_failures.append(f"Recommended resources exceed available budget by more than 10%")
    
    # Update pass/fail status based on critical failures
    if critical_failures:
        results["pass_fail"] = "FAIL"
        results["critical_failures"] = critical_failures
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    output_file = "test_results.json"
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {results['pass_fail']}")

if __name__ == "__main__":
    main()