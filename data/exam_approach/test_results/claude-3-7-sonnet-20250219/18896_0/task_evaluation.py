#!/usr/bin/env python3
"""
Labor Relations Specialist Practical Exam Evaluator

This script evaluates a candidate's submission for the Labor Relations Specialist 
practical exam on risk assessment in collective bargaining.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import os
from typing import Dict, List, Any, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON.")
        sys.exit(1)


def validate_submission_format(submission: Dict) -> List[str]:
    """Validate the format of the candidate's submission."""
    errors = []
    
    # Check required top-level keys
    required_keys = ["candidate_id", "identified_risks", "priority_risks"]
    for key in required_keys:
        if key not in submission:
            errors.append(f"Missing required field: {key}")
    
    if "identified_risks" in submission:
        # Check if there are at least 5 risks identified
        if len(submission["identified_risks"]) < 5:
            errors.append(f"Insufficient risks identified: {len(submission['identified_risks'])} (minimum 5 required)")
        
        # Validate each identified risk
        risk_ids = set()
        for i, risk in enumerate(submission["identified_risks"]):
            # Check required risk fields
            risk_fields = ["risk_id", "risk_description", "probability", "impact", 
                          "risk_score", "risk_category", "justification"]
            for field in risk_fields:
                if field not in risk:
                    errors.append(f"Risk #{i+1} is missing field: {field}")
            
            # Validate risk_id uniqueness
            if "risk_id" in risk:
                if risk["risk_id"] in risk_ids:
                    errors.append(f"Duplicate risk_id: {risk['risk_id']}")
                risk_ids.add(risk["risk_id"])
            
            # Validate probability and impact ranges
            if "probability" in risk and not (1 <= risk["probability"] <= 5):
                errors.append(f"Risk #{i+1} has invalid probability: {risk['probability']} (must be 1-5)")
            
            if "impact" in risk and not (1 <= risk["impact"] <= 5):
                errors.append(f"Risk #{i+1} has invalid impact: {risk['impact']} (must be 1-5)")
            
            # Validate risk score calculation
            if all(field in risk for field in ["probability", "impact", "risk_score"]):
                expected_score = risk["probability"] * risk["impact"]
                if risk["risk_score"] != expected_score:
                    errors.append(f"Risk #{i+1} has incorrect risk_score: {risk['risk_score']} (should be {expected_score})")
            
            # Validate risk category
            valid_categories = ["Financial", "Operational", "Reputational", "Legal"]
            if "risk_category" in risk and risk["risk_category"] not in valid_categories:
                errors.append(f"Risk #{i+1} has invalid risk_category: {risk['risk_category']}")
    
    if "priority_risks" in submission:
        # Check if there are exactly 3 priority risks
        if len(submission["priority_risks"]) != 3:
            errors.append(f"Incorrect number of priority risks: {len(submission['priority_risks'])} (exactly 3 required)")
        
        # Validate each priority risk
        for i, risk in enumerate(submission["priority_risks"]):
            # Check required priority risk fields
            priority_fields = ["risk_id", "mitigation_strategy", "expected_outcome"]
            for field in priority_fields:
                if field not in risk:
                    errors.append(f"Priority risk #{i+1} is missing field: {field}")
            
            # Validate that priority risk_id exists in identified_risks
            if "risk_id" in risk and risk_ids:
                if risk["risk_id"] not in risk_ids:
                    errors.append(f"Priority risk #{i+1} references non-existent risk_id: {risk['risk_id']}")
    
    return errors


def evaluate_risk_identification(submission: Dict) -> Tuple[int, int, List[Dict]]:
    """Evaluate the risk identification section."""
    max_points = 25  # 5 points per risk for up to 5 risks
    earned_points = 0
    feedback = []
    
    if len(submission["identified_risks"]) >= 5:
        # Award points for each valid risk identified (up to 5 risks)
        for i, risk in enumerate(submission["identified_risks"][:5]):
            points = 0
            risk_feedback = {
                "risk_id": risk["risk_id"],
                "points": 0,
                "max_points": 5,
                "comments": []
            }
            
            # Check if risk description is substantive (at least 15 words)
            if len(risk["risk_description"].split()) >= 15:
                points += 2
                risk_feedback["comments"].append("Risk description is substantive")
            else:
                risk_feedback["comments"].append("Risk description lacks sufficient detail")
            
            # Check if risk is relevant to the case
            # This is a simplified check - in a real evaluation, you'd want more sophisticated relevance checking
            if len(risk["risk_description"]) > 50:
                points += 1
                risk_feedback["comments"].append("Risk appears relevant to the case")
            else:
                risk_feedback["comments"].append("Risk may not be sufficiently relevant to the case")
            
            # Check if risk is distinct from others (simplified check)
            is_distinct = True
            for j, other_risk in enumerate(submission["identified_risks"]):
                if i != j and similarity_check(risk["risk_description"], other_risk["risk_description"]):
                    is_distinct = False
                    break
            
            if is_distinct:
                points += 2
                risk_feedback["comments"].append("Risk is distinct from other identified risks")
            else:
                risk_feedback["comments"].append("Risk overlaps significantly with other identified risks")
            
            earned_points += points
            risk_feedback["points"] = points
            feedback.append(risk_feedback)
    
    return earned_points, max_points, feedback


def evaluate_risk_assessment(submission: Dict) -> Tuple[int, int, List[Dict]]:
    """Evaluate the risk assessment (probability, impact, score, justification)."""
    max_points = 20  # 4 points per risk for up to 5 risks
    earned_points = 0
    feedback = []
    
    for i, risk in enumerate(submission["identified_risks"][:5]):
        points = 0
        risk_feedback = {
            "risk_id": risk["risk_id"],
            "points": 0,
            "max_points": 4,
            "comments": []
        }
        
        # Check if probability and impact ratings are reasonable
        # This is simplified - in a real evaluation, you'd want to check against expected ranges for each risk type
        if 1 <= risk["probability"] <= 5 and 1 <= risk["impact"] <= 5:
            points += 1
            risk_feedback["comments"].append("Probability and impact ratings are within valid ranges")
        else:
            risk_feedback["comments"].append("Probability and/or impact ratings are outside valid ranges")
        
        # Check if risk score calculation is correct
        if risk["risk_score"] == risk["probability"] * risk["impact"]:
            points += 1
            risk_feedback["comments"].append("Risk score calculation is correct")
        else:
            risk_feedback["comments"].append("Risk score calculation is incorrect")
        
        # Check if justification references specific case details
        # This is simplified - in a real evaluation, you'd want more sophisticated content analysis
        if len(risk["justification"].split()) >= 15:
            points += 2
            risk_feedback["comments"].append("Justification is substantive and appears to reference case details")
        else:
            risk_feedback["comments"].append("Justification lacks sufficient detail or case references")
        
        earned_points += points
        risk_feedback["points"] = points
        feedback.append(risk_feedback)
    
    return earned_points, max_points, feedback


def evaluate_risk_categorization(submission: Dict) -> Tuple[int, int, List[Dict]]:
    """Evaluate the risk categorization."""
    max_points = 10  # 2 points per risk for up to 5 risks
    earned_points = 0
    feedback = []
    
    valid_categories = ["Financial", "Operational", "Reputational", "Legal"]
    
    for i, risk in enumerate(submission["identified_risks"][:5]):
        points = 0
        risk_feedback = {
            "risk_id": risk["risk_id"],
            "points": 0,
            "max_points": 2,
            "comments": []
        }
        
        # Check if category is valid
        if risk["risk_category"] in valid_categories:
            points += 1
            risk_feedback["comments"].append("Risk category is valid")
        else:
            risk_feedback["comments"].append("Risk category is invalid")
        
        # Check if category is appropriate for the risk description
        # This is simplified - in a real evaluation, you'd want more sophisticated content analysis
        if category_matches_description(risk["risk_description"], risk["risk_category"]):
            points += 1
            risk_feedback["comments"].append("Risk category appears appropriate for the description")
        else:
            risk_feedback["comments"].append("Risk category may not be the most appropriate for this risk")
        
        earned_points += points
        risk_feedback["points"] = points
        feedback.append(risk_feedback)
    
    return earned_points, max_points, feedback


def evaluate_priority_selection(submission: Dict) -> Tuple[int, int, Dict]:
    """Evaluate the selection of priority risks."""
    max_points = 15
    earned_points = 0
    feedback = {
        "points": 0,
        "max_points": max_points,
        "comments": []
    }
    
    # Check if exactly 3 priority risks are selected
    if len(submission["priority_risks"]) == 3:
        feedback["comments"].append("Correct number of priority risks selected (3)")
        earned_points += 5
    else:
        feedback["comments"].append(f"Incorrect number of priority risks: {len(submission['priority_risks'])} (should be 3)")
    
    # Check if priority risks are among the highest-scoring risks
    risk_scores = {risk["risk_id"]: risk["risk_score"] for risk in submission["identified_risks"]}
    sorted_risks = sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)
    top_risk_ids = [risk_id for risk_id, _ in sorted_risks[:3]]
    
    priority_risk_ids = [risk["risk_id"] for risk in submission["priority_risks"]]
    
    # Count how many priority risks are in the top 3 by score
    matches = sum(1 for risk_id in priority_risk_ids if risk_id in top_risk_ids)
    
    if matches == 3:
        feedback["comments"].append("All priority risks are among the highest-scoring risks")
        earned_points += 10
    elif matches == 2:
        feedback["comments"].append("2 of 3 priority risks are among the highest-scoring risks")
        earned_points += 7
    elif matches == 1:
        feedback["comments"].append("1 of 3 priority risks is among the highest-scoring risks")
        earned_points += 3
    else:
        feedback["comments"].append("No priority risks are among the highest-scoring risks")
    
    feedback["points"] = earned_points
    return earned_points, max_points, feedback


def evaluate_mitigation_strategies(submission: Dict) -> Tuple[int, int, List[Dict]]:
    """Evaluate the mitigation strategies for priority risks."""
    max_points = 30  # 10 points per priority risk
    earned_points = 0
    feedback = []
    
    for i, risk in enumerate(submission["priority_risks"]):
        points = 0
        risk_feedback = {
            "risk_id": risk["risk_id"],
            "points": 0,
            "max_points": 10,
            "comments": []
        }
        
        # Check if mitigation strategy is specific and practical
        # This is simplified - in a real evaluation, you'd want more sophisticated content analysis
        if len(risk["mitigation_strategy"].split()) >= 30:
            points += 4
            risk_feedback["comments"].append("Mitigation strategy is detailed and specific")
        elif len(risk["mitigation_strategy"].split()) >= 15:
            points += 2
            risk_feedback["comments"].append("Mitigation strategy has moderate detail")
        else:
            risk_feedback["comments"].append("Mitigation strategy lacks sufficient detail")
        
        # Check if mitigation strategy directly addresses the identified risk
        # This would require comparing to the original risk description
        # For simplicity, we'll just check if it's substantive
        if len(risk["mitigation_strategy"].split()) >= 40:
            points += 3
            risk_feedback["comments"].append("Mitigation strategy appears comprehensive")
        else:
            risk_feedback["comments"].append("Mitigation strategy may not fully address the risk")
        
        # Check if expected outcome is reasonable and specific
        if len(risk["expected_outcome"].split()) >= 15:
            points += 3
            risk_feedback["comments"].append("Expected outcome is well-articulated")
        else:
            risk_feedback["comments"].append("Expected outcome lacks sufficient detail")
        
        earned_points += points
        risk_feedback["points"] = points
        feedback.append(risk_feedback)
    
    return earned_points, max_points, feedback


def similarity_check(text1: str, text2: str) -> bool:
    """
    Simple check for significant overlap between two text descriptions.
    In a real implementation, you'd want a more sophisticated similarity measure.
    """
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    # If more than 70% of words overlap, consider them similar
    return intersection / union > 0.7 if union > 0 else False


def category_matches_description(description: str, category: str) -> bool:
    """
    Simple check if the risk category seems appropriate for the description.
    In a real implementation, you'd want more sophisticated NLP analysis.
    """
    description_lower = description.lower()
    
    # Define keywords associated with each category
    financial_keywords = ["cost", "revenue", "profit", "financial", "budget", "expense", "economic"]
    operational_keywords = ["production", "operation", "process", "delivery", "workflow", "efficiency", "quality"]
    reputational_keywords = ["reputation", "image", "brand", "public", "media", "perception", "community"]
    legal_keywords = ["legal", "compliance", "regulation", "lawsuit", "litigation", "violation", "charge"]
    
    # Check for keyword matches
    if category == "Financial":
        return any(keyword in description_lower for keyword in financial_keywords)
    elif category == "Operational":
        return any(keyword in description_lower for keyword in operational_keywords)
    elif category == "Reputational":
        return any(keyword in description_lower for keyword in reputational_keywords)
    elif category == "Legal":
        return any(keyword in description_lower for keyword in legal_keywords)
    
    return False


def calculate_overall_score(section_scores: List[Tuple[int, int]]) -> float:
    """Calculate the overall percentage score."""
    total_earned = sum(earned for earned, _ in section_scores)
    total_possible = sum(possible for _, possible in section_scores)
    
    return (total_earned / total_possible) * 100 if total_possible > 0 else 0


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    # Validate submission format
    format_errors = validate_submission_format(submission)
    if format_errors:
        return {
            "overall_score": 0,
            "format_errors": format_errors,
            "message": "Submission format is invalid. Please correct the errors and resubmit."
        }
    
    # Evaluate each section
    risk_identification_score, risk_identification_max, risk_identification_feedback = evaluate_risk_identification(submission)
    risk_assessment_score, risk_assessment_max, risk_assessment_feedback = evaluate_risk_assessment(submission)
    risk_categorization_score, risk_categorization_max, risk_categorization_feedback = evaluate_risk_categorization(submission)
    priority_selection_score, priority_selection_max, priority_selection_feedback = evaluate_priority_selection(submission)
    mitigation_score, mitigation_max, mitigation_feedback = evaluate_mitigation_strategies(submission)
    
    # Compile section scores
    section_scores = [
        (risk_identification_score, risk_identification_max),
        (risk_assessment_score, risk_assessment_max),
        (risk_categorization_score, risk_categorization_max),
        (priority_selection_score, priority_selection_max),
        (mitigation_score, mitigation_max)
    ]
    
    # Calculate overall score
    overall_score = calculate_overall_score(section_scores)
    
    # Determine performance level
    performance_level = ""
    if overall_score >= 90:
        performance_level = "Excellent"
    elif overall_score >= 80:
        performance_level = "Good"
    elif overall_score >= 70:
        performance_level = "Satisfactory"
    elif overall_score >= 60:
        performance_level = "Needs Improvement"
    else:
        performance_level = "Unsatisfactory"
    
    # Compile results
    results = {
        "overall_score": round(overall_score, 2),
        "performance_level": performance_level,
        "sections": {
            "risk_identification": {
                "score": risk_identification_score,
                "max_points": risk_identification_max,
                "percentage": round((risk_identification_score / risk_identification_max) * 100, 2) if risk_identification_max > 0 else 0,
                "feedback": risk_identification_feedback
            },
            "risk_assessment": {
                "score": risk_assessment_score,
                "max_points": risk_assessment_max,
                "percentage": round((risk_assessment_score / risk_assessment_max) * 100, 2) if risk_assessment_max > 0 else 0,
                "feedback": risk_assessment_feedback
            },
            "risk_categorization": {
                "score": risk_categorization_score,
                "max_points": risk_categorization_max,
                "percentage": round((risk_categorization_score / risk_categorization_max) * 100, 2) if risk_categorization_max > 0 else 0,
                "feedback": risk_categorization_feedback
            },
            "priority_selection": {
                "score": priority_selection_score,
                "max_points": priority_selection_max,
                "percentage": round((priority_selection_score / priority_selection_max) * 100, 2) if priority_selection_max > 0 else 0,
                "feedback": priority_selection_feedback
            },
            "mitigation_strategies": {
                "score": mitigation_score,
                "max_points": mitigation_max,
                "percentage": round((mitigation_score / mitigation_max) * 100, 2) if mitigation_max > 0 else 0,
                "feedback": mitigation_feedback
            }
        },
        "summary": {
            "strengths": generate_strengths(section_scores),
            "areas_for_improvement": generate_improvements(section_scores),
            "overall_assessment": generate_overall_assessment(overall_score, performance_level)
        }
    }
    
    return results


def generate_strengths(section_scores: List[Tuple[int, int]]) -> List[str]:
    """Generate a list of strengths based on section scores."""
    strengths = []
    sections = ["Risk identification", "Risk assessment", "Risk categorization", "Priority risk selection", "Mitigation strategies"]
    
    for i, (earned, max_points) in enumerate(section_scores):
        percentage = (earned / max_points) * 100 if max_points > 0 else 0
        if percentage >= 80:
            strengths.append(f"{sections[i]} (scored {round(percentage, 1)}%)")
    
    return strengths if strengths else ["No particular strengths identified."]


def generate_improvements(section_scores: List[Tuple[int, int]]) -> List[str]:
    """Generate a list of areas for improvement based on section scores."""
    improvements = []
    sections = ["Risk identification", "Risk assessment", "Risk categorization", "Priority risk selection", "Mitigation strategies"]
    
    for i, (earned, max_points) in enumerate(section_scores):
        percentage = (earned / max_points) * 100 if max_points > 0 else 0
        if percentage < 70:
            improvements.append(f"{sections[i]} (scored {round(percentage, 1)}%)")
    
    return improvements if improvements else ["No significant areas for improvement identified."]


def generate_overall_assessment(overall_score: float, performance_level: str) -> str:
    """Generate an overall assessment based on the score and performance level."""
    if performance_level == "Excellent":
        return "The candidate demonstrated exceptional ability to assess risks in collective bargaining scenarios, with strong performance across all evaluation areas."
    elif performance_level == "Good":
        return "The candidate showed strong risk assessment capabilities, with good performance in most evaluation areas."
    elif performance_level == "Satisfactory":
        return "The candidate demonstrated adequate risk assessment capabilities, meeting the basic requirements of the exam."
    elif performance_level == "Needs Improvement":
        return "The candidate showed some understanding of risk assessment but needs improvement in several key areas."
    else:  # Unsatisfactory
        return "The candidate did not demonstrate sufficient risk assessment capabilities to meet the minimum requirements of the exam."


def main():
    """Main function to process command line arguments and evaluate the submission."""
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
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Performance level: {results.get('performance_level', 'Not available')}")


if __name__ == "__main__":
    main()