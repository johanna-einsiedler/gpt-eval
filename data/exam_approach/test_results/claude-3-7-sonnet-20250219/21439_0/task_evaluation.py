#!/usr/bin/env python3
"""
Script to evaluate candidate submissions for the Claims Irregularity Reporting Assessment.
Usage: python task_evaluation.py test_submission.json answer_key.json
"""

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

def evaluate_scenario(candidate_answer, correct_answer, scenario_name):
    """Evaluate a single scenario and return the score details."""
    results = {
        "scenario": scenario_name,
        "points_possible": 33,
        "points_earned": 0,
        "breakdown": {
            "irregularity_identification": {"possible": 10, "earned": 0, "notes": ""},
            "amount_in_question": {"possible": 8, "earned": 0, "notes": ""},
            "affected_benefit": {"possible": 5, "earned": 0, "notes": ""},
            "regulation_violated": {"possible": 5, "earned": 0, "notes": ""},
            "explanation": {"possible": 5, "earned": 0, "notes": ""}
        }
    }
    
    # Evaluate irregularity type (10 points)
    if candidate_answer.get("irregularityType") == correct_answer.get("irregularityType"):
        results["breakdown"]["irregularity_identification"]["earned"] = 10
        results["points_earned"] += 10
    else:
        results["breakdown"]["irregularity_identification"]["notes"] = (
            f"Expected: {correct_answer.get('irregularityType')}, "
            f"Got: {candidate_answer.get('irregularityType')}"
        )
    
    # Evaluate amount in question (8 points)
    candidate_amount = float(candidate_answer.get("amountInQuestion", 0))
    correct_amount = float(correct_answer.get("amountInQuestion", 0))
    
    if abs(candidate_amount - correct_amount) <= 10:
        # Within $10 tolerance
        results["breakdown"]["amount_in_question"]["earned"] = 8
        results["points_earned"] += 8
    elif abs(candidate_amount - correct_amount) <= 100:
        # Within $100 tolerance - partial credit
        results["breakdown"]["amount_in_question"]["earned"] = 4
        results["points_earned"] += 4
        results["breakdown"]["amount_in_question"]["notes"] = (
            f"Amount is off by ${abs(candidate_amount - correct_amount):.2f}. "
            f"Expected: ${correct_amount:.2f}, Got: ${candidate_amount:.2f}"
        )
    else:
        # Off by more than $100
        results["breakdown"]["amount_in_question"]["notes"] = (
            f"Amount is off by ${abs(candidate_amount - correct_amount):.2f}. "
            f"Expected: ${correct_amount:.2f}, Got: ${candidate_amount:.2f}"
        )
    
    # Evaluate affected benefit (5 points)
    if candidate_answer.get("affectedBenefit") == correct_answer.get("affectedBenefit"):
        results["breakdown"]["affected_benefit"]["earned"] = 5
        results["points_earned"] += 5
    else:
        results["breakdown"]["affected_benefit"]["notes"] = (
            f"Expected: {correct_answer.get('affectedBenefit')}, "
            f"Got: {candidate_answer.get('affectedBenefit')}"
        )
    
    # Evaluate regulation violated (5 points)
    if candidate_answer.get("regulationViolated") == correct_answer.get("regulationViolated"):
        results["breakdown"]["regulation_violated"]["earned"] = 5
        results["points_earned"] += 5
    else:
        results["breakdown"]["regulation_violated"]["notes"] = (
            f"Expected: {correct_answer.get('regulationViolated')}, "
            f"Got: {candidate_answer.get('regulationViolated')}"
        )
    
    # Evaluate explanation (5 points)
    # Simple check if explanation exists and is not empty
    if "explanation" in candidate_answer and candidate_answer["explanation"].strip():
        # Basic check - we give at least some credit for having an explanation
        min_points = 2
        
        # Full points if the explanation contains key elements from the correct explanation
        correct_explanation = correct_answer.get("explanation", "").lower()
        candidate_explanation = candidate_answer.get("explanation", "").lower()
        
        # Define key terms to look for based on the scenario
        key_terms = {
            "scenario1": ["deductible", "overpayment", "rental"],
            "scenario2": ["duplicate", "personal property", "twice"],
            "scenario3": ["calculation", "laboratory", "underpayment"]
        }
        
        terms_found = sum(1 for term in key_terms.get(scenario_name, []) 
                         if term.lower() in candidate_explanation)
        
        # Calculate points based on how many key terms are found
        if scenario_name in key_terms:
            points = min(5, min_points + (3 * terms_found / len(key_terms[scenario_name])))
        else:
            points = min_points
            
        results["breakdown"]["explanation"]["earned"] = round(points)
        results["points_earned"] += round(points)
    else:
        results["breakdown"]["explanation"]["notes"] = "No explanation provided"
    
    return results

def calculate_formatting_score(submission):
    """Check if the JSON is properly formatted and return 1 point if it is."""
    # Basic check that it could be loaded as JSON
    if isinstance(submission, dict):
        # Check that all required scenarios are present
        if all(f"scenario{i}" in submission for i in range(1, 4)):
            return 1
    return 0

def calculate_overall_score(scenario_results, formatting_score):
    """Calculate the overall score based on scenario results and formatting."""
    total_points_possible = sum(result["points_possible"] for result in scenario_results) + 1
    total_points_earned = sum(result["points_earned"] for result in scenario_results) + formatting_score
    
    # Calculate percentage score (0-100)
    if total_points_possible > 0:
        percentage_score = (total_points_earned / total_points_possible) * 100
    else:
        percentage_score = 0
    
    return {
        "total_points_possible": total_points_possible,
        "total_points_earned": total_points_earned,
        "percentage_score": round(percentage_score, 2),
        "passing_threshold": 70,
        "passed": percentage_score >= 70
    }

def count_correct_identifications(scenario_results):
    """Count how many irregularities were correctly identified."""
    correct_count = 0
    for result in scenario_results:
        if result["breakdown"]["irregularity_identification"]["earned"] > 0:
            correct_count += 1
    return correct_count

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    candidate_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    candidate_submission = load_json_file(candidate_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each scenario
    scenario_results = []
    for i in range(1, 4):
        scenario_name = f"scenario{i}"
        if scenario_name in candidate_submission and scenario_name in answer_key:
            result = evaluate_scenario(
                candidate_submission[scenario_name], 
                answer_key[scenario_name], 
                scenario_name
            )
            scenario_results.append(result)
        else:
            print(f"Error: {scenario_name} not found in either submission or answer key")
            sys.exit(1)
    
    # Check formatting
    formatting_score = calculate_formatting_score(candidate_submission)
    
    # Calculate overall score
    overall_score_details = calculate_overall_score(scenario_results, formatting_score)
    
    # Count correctly identified irregularities
    correct_identifications = count_correct_identifications(scenario_results)
    
    # Create the final results object
    evaluation_results = {
        "candidate_id": candidate_submission.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
        "scenario_results": scenario_results,
        "formatting_score": formatting_score,
        "overall_score_details": overall_score_details,
        "overall_score": overall_score_details["percentage_score"],
        "correct_identifications": correct_identifications,
        "minimum_identifications_required": 2,
        "final_result": "PASS" if (
            overall_score_details["passed"] and 
            correct_identifications >= 2
        ) else "FAIL",
        "feedback": generate_feedback(
            scenario_results, 
            formatting_score, 
            overall_score_details,
            correct_identifications
        )
    }
    
    # Save results to file
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall Score: {overall_score_details['percentage_score']}%")
    print(f"Final Result: {evaluation_results['final_result']}")

def generate_feedback(scenario_results, formatting_score, overall_score_details, correct_identifications):
    """Generate overall feedback based on the results."""
    feedback = []
    
    # Check if passed the minimum requirements
    if correct_identifications < 2:
        feedback.append("CRITICAL: You identified fewer than the minimum required 2 irregularities correctly.")
    
    # Add scenario-specific feedback
    for result in scenario_results:
        scenario_feedback = []
        scenario_name = result["scenario"].capitalize().replace("scenario", "Scenario ")
        
        # Check for major issues in this scenario
        if result["breakdown"]["irregularity_identification"]["earned"] == 0:
            scenario_feedback.append(
                f"You did not correctly identify the irregularity type. "
                f"{result['breakdown']['irregularity_identification']['notes']}"
            )
        
        if result["breakdown"]["amount_in_question"]["earned"] == 0:
            scenario_feedback.append(
                f"The amount in question was significantly off. "
                f"{result['breakdown']['amount_in_question']['notes']}"
            )
        
        # Add scenario feedback if there were issues
        if scenario_feedback:
            feedback.append(f"{scenario_name}: " + " ".join(scenario_feedback))
    
    # Overall performance feedback
    if overall_score_details["passed"]:
        if overall_score_details["percentage_score"] >= 90:
            feedback.append(
                "Excellent performance! You demonstrated strong attention to detail and understanding of "
                "irregularity reporting procedures."
            )
        elif overall_score_details["percentage_score"] >= 80:
            feedback.append(
                "Good performance. You successfully identified most irregularities and "
                "showed good understanding of the reporting process."
            )
        else:
            feedback.append(
                "Satisfactory performance. While you met the minimum passing requirements, "
                "there is room for improvement in accuracy and detail."
            )
    else:
        feedback.append(
            "Your score did not meet the minimum passing threshold. Please review the "
            "specific feedback for each scenario and consider additional training on "
            "identifying and reporting claim irregularities."
        )
    
    return " ".join(feedback)

if __name__ == "__main__":
    main()