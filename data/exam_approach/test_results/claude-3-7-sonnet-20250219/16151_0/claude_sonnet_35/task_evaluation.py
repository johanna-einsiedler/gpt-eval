#!/usr/bin/env python3
"""
IT Project Manager Risk Assessment Exam Evaluator

This script evaluates a candidate's submission against an answer key for the
IT Project Manager Risk Assessment practical exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any, Tuple


def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_risk_identification(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the risk identification section."""
    identified_risks = submission.get("identified_risks", [])
    
    # Check if at least 8 risks were identified
    num_risks = len(identified_risks)
    min_risks_score = min(1.0, num_risks / 8) * 10
    
    # Check if all categories are represented
    categories = set(risk.get("risk_category", "") for risk in identified_risks)
    expected_categories = {"Technical", "Schedule", "Resource", "Financial", "External"}
    category_coverage = len(categories.intersection(expected_categories)) / len(expected_categories)
    category_score = category_coverage * 10
    
    # Check risk descriptions for clarity and specificity
    description_scores = []
    for risk in identified_risks:
        desc = risk.get("risk_description", "")
        # Simple heuristic: descriptions between 25-100 chars are likely specific enough
        if 25 <= len(desc) <= 100 and desc.strip():
            description_scores.append(1.0)
        elif desc.strip():
            description_scores.append(0.5)
        else:
            description_scores.append(0.0)
    
    avg_description_score = sum(description_scores) / max(1, len(description_scores))
    description_quality_score = avg_description_score * 20
    
    # Calculate total score for risk identification (40% of total)
    total_score = min_risks_score + category_score + description_quality_score
    
    return {
        "num_risks_identified": num_risks,
        "min_risks_score": min_risks_score,
        "category_coverage": category_coverage,
        "category_score": category_score,
        "description_quality_score": description_quality_score,
        "total_score": total_score,
        "max_possible": 40,
        "percentage": (total_score / 40) * 100
    }


def evaluate_risk_analysis(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the risk analysis section."""
    identified_risks = submission.get("identified_risks", [])
    risk_matrix = submission.get("risk_matrix", {})
    
    # Check if probability and impact scores are reasonable
    score_accuracy = []
    for risk in identified_risks:
        prob = risk.get("probability_score", 0)
        impact = risk.get("impact_score", 0)
        risk_score = risk.get("risk_score", 0)
        
        # Check if risk score calculation is correct
        if prob * impact == risk_score and 1 <= prob <= 5 and 1 <= impact <= 5:
            score_accuracy.append(1.0)
        elif 1 <= prob <= 5 and 1 <= impact <= 5:
            score_accuracy.append(0.5)  # Scores in range but calculation error
        else:
            score_accuracy.append(0.0)  # Invalid scores
    
    avg_score_accuracy = sum(score_accuracy) / max(1, len(score_accuracy))
    score_accuracy_points = avg_score_accuracy * 15
    
    # Check risk matrix categorization
    matrix_errors = 0
    risk_ids_by_category = {
        "high_impact_high_probability": [],
        "high_impact_low_probability": [],
        "low_impact_high_probability": [],
        "low_impact_low_probability": []
    }
    
    # Build the correct risk matrix based on the submitted risks
    for risk in identified_risks:
        risk_id = risk.get("risk_id", "")
        prob = risk.get("probability_score", 0)
        impact = risk.get("impact_score", 0)
        
        if impact >= 4 and prob >= 4:
            risk_ids_by_category["high_impact_high_probability"].append(risk_id)
        elif impact >= 4 and prob <= 3:
            risk_ids_by_category["high_impact_low_probability"].append(risk_id)
        elif impact <= 3 and prob >= 4:
            risk_ids_by_category["low_impact_high_probability"].append(risk_id)
        elif impact <= 3 and prob <= 3:
            risk_ids_by_category["low_impact_low_probability"].append(risk_id)
    
    # Compare with submitted matrix
    for category, correct_ids in risk_ids_by_category.items():
        submitted_ids = set(risk_matrix.get(category, []))
        correct_ids_set = set(correct_ids)
        
        # Count misplaced risks
        matrix_errors += len(submitted_ids.symmetric_difference(correct_ids_set))
    
    matrix_accuracy = max(0, 1 - (matrix_errors / (2 * max(1, len(identified_risks)))))
    matrix_score = matrix_accuracy * 10
    
    # Calculate total score for risk analysis (25% of total)
    total_score = score_accuracy_points + matrix_score
    
    return {
        "score_accuracy": avg_score_accuracy,
        "score_accuracy_points": score_accuracy_points,
        "matrix_accuracy": matrix_accuracy,
        "matrix_score": matrix_score,
        "total_score": total_score,
        "max_possible": 25,
        "percentage": (total_score / 25) * 100
    }


def evaluate_response_strategies(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the response strategy development section."""
    identified_risks = submission.get("identified_risks", [])
    priority_risks = submission.get("priority_risks", [])
    
    # Check if response strategies are appropriate
    strategy_scores = []
    for risk in identified_risks:
        category = risk.get("risk_category", "")
        prob = risk.get("probability_score", 0)
        impact = risk.get("impact_score", 0)
        risk_score = risk.get("risk_score", 0)
        strategy = risk.get("response_strategy", "")
        actions = risk.get("response_actions", "")
        
        # Simple heuristic for strategy appropriateness
        strategy_appropriate = False
        if strategy in ["Mitigate", "Avoid", "Transfer", "Accept"]:
            if risk_score >= 16 and strategy != "Accept":
                strategy_appropriate = True
            elif 8 <= risk_score <= 15 and strategy in ["Mitigate", "Transfer", "Avoid"]:
                strategy_appropriate = True
            elif risk_score < 8:
                strategy_appropriate = True  # Any strategy can be appropriate for low risks
        
        # Check if actions are specific and actionable
        actions_appropriate = len(actions) >= 50 and len(actions) <= 200
        
        if strategy_appropriate and actions_appropriate:
            strategy_scores.append(1.0)
        elif strategy_appropriate or actions_appropriate:
            strategy_scores.append(0.5)
        else:
            strategy_scores.append(0.0)
    
    avg_strategy_score = sum(strategy_scores) / max(1, len(strategy_scores))
    strategy_points = avg_strategy_score * 15
    
    # Check priority risks selection
    if len(priority_risks) == 3:
        # Get the top 3 risks by score from the submission
        risk_scores = [(risk.get("risk_id", ""), risk.get("risk_score", 0)) 
                      for risk in identified_risks]
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        top_risks = [risk_id for risk_id, _ in risk_scores[:3]]
        
        # Count how many of the submitted priority risks are in the top 3
        priority_accuracy = len(set(priority_risks).intersection(set(top_risks))) / 3
    else:
        priority_accuracy = 0
    
    priority_points = priority_accuracy * 10
    
    # Calculate total score for response strategies (25% of total)
    total_score = strategy_points + priority_points
    
    return {
        "strategy_appropriateness": avg_strategy_score,
        "strategy_points": strategy_points,
        "priority_accuracy": priority_accuracy,
        "priority_points": priority_points,
        "total_score": total_score,
        "max_possible": 25,
        "percentage": (total_score / 25) * 100
    }


def evaluate_contingency_budget(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the contingency budget calculation."""
    identified_risks = submission.get("identified_risks", [])
    submitted_budget = submission.get("contingency_budget", 0)
    
    # Calculate the correct contingency budget based on the submitted risks
    high_medium_risk_sum = 0
    for risk in identified_risks:
        risk_score = risk.get("risk_score", 0)
        if risk_score >= 8:  # High or medium risk
            high_medium_risk_sum += risk_score * 1000
    
    project_budget = 450000
    correct_budget = high_medium_risk_sum + (project_budget * 0.05)
    
    # Calculate accuracy as percentage difference
    if correct_budget > 0:
        budget_accuracy = max(0, 1 - abs(submitted_budget - correct_budget) / correct_budget)
    else:
        budget_accuracy = 0
    
    budget_score = budget_accuracy * 10
    
    return {
        "submitted_budget": submitted_budget,
        "correct_budget": correct_budget,
        "budget_accuracy": budget_accuracy,
        "total_score": budget_score,
        "max_possible": 10,
        "percentage": (budget_score / 10) * 100
    }


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    # Evaluate each section
    risk_identification = evaluate_risk_identification(submission, answer_key)
    risk_analysis = evaluate_risk_analysis(submission, answer_key)
    response_strategies = evaluate_response_strategies(submission, answer_key)
    contingency_budget = evaluate_contingency_budget(submission, answer_key)
    
    # Calculate overall score
    total_score = (
        risk_identification["total_score"] +
        risk_analysis["total_score"] +
        response_strategies["total_score"] +
        contingency_budget["total_score"]
    )
    max_possible = 100  # 40 + 25 + 25 + 10
    overall_percentage = (total_score / max_possible) * 100
    
    # Check if minimum passing criteria are met
    section_percentages = [
        risk_identification["percentage"],
        risk_analysis["percentage"],
        response_strategies["percentage"],
        contingency_budget["percentage"]
    ]
    
    passed_minimum = all(percentage >= 60 for percentage in section_percentages)
    passed_overall = overall_percentage >= 70
    passed = passed_minimum and passed_overall
    
    return {
        "risk_identification": risk_identification,
        "risk_analysis": risk_analysis,
        "response_strategies": response_strategies,
        "contingency_budget": contingency_budget,
        "total_score": total_score,
        "max_possible": max_possible,
        "overall_score": overall_percentage,
        "passed_minimum_section_requirements": passed_minimum,
        "passed_overall_threshold": passed_overall,
        "passed": passed
    }


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
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()