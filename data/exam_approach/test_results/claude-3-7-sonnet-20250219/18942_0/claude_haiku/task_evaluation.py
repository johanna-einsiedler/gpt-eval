#!/usr/bin/env python3
"""
Credit Counselor Written Communication Skills Assessment Evaluator

This script evaluates a candidate's submission against an answer key and generates
a detailed assessment report with scores.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import re
from typing import Dict, List, Any


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_task1(submission: str, required_elements: List[str]) -> Dict:
    """Evaluate the client recommendation letter task."""
    results = {
        "score": 0,
        "max_score": 100,
        "elements_found": [],
        "elements_missing": [],
        "feedback": ""
    }
    
    # Convert submission to lowercase for case-insensitive matching
    submission_lower = submission.lower()
    
    # Check for each required element
    for element in required_elements:
        found = False
        
        if element == "debt_consolidation_plan" and re.search(r'consolidat(e|ion)', submission_lower) and re.search(r'(plan|option)', submission_lower):
            found = True
        elif element == "debt_snowball_avalanche_comparison" and "snowball" in submission_lower and "avalanche" in submission_lower:
            found = True
        elif element == "budget_recommendations" and "budget" in submission_lower and re.search(r'(recommend|suggest)', submission_lower):
            found = True
        elif element == "total_debt_amount_28000" and "$28,000" in submission or "$28000" in submission:
            found = True
        elif element == "specific_monthly_payment_recommendation" and re.search(r'\$\d+(\.\d{2})? (per month|monthly|each month)', submission_lower):
            found = True
        elif element == "entertainment_dining_reduction" and re.search(r'(entertainment|dining)', submission_lower) and re.search(r'(reduc|cut|lower|decrease)', submission_lower):
            found = True
        elif element == "bonus_recommendation" and "$3,000" in submission and re.search(r'bonus', submission_lower):
            found = True
        elif element == "projected_timeline" and re.search(r'(month|year|time|timeline)', submission_lower) and re.search(r'\d+', submission_lower):
            found = True
        elif element == "professional_tone" and not re.search(r'(slang|inappropriate|unprofessional)', submission_lower):
            found = True
        elif element == "personalized_to_client" and "Michael" in submission and "Rodriguez" in submission:
            found = True
        
        if found:
            results["elements_found"].append(element)
            results["score"] += 10
        else:
            results["elements_missing"].append(element)
    
    # Generate feedback
    if results["score"] >= 80:
        results["feedback"] = "Excellent work on the recommendation letter. Most required elements were included with good personalization."
    elif results["score"] >= 60:
        results["feedback"] = "Good effort on the recommendation letter, but missing some key elements that would make it more effective."
    else:
        results["feedback"] = "The recommendation letter needs significant improvement. Many required elements are missing."
    
    return results


def evaluate_task2(submission: str, required_elements: List[str]) -> Dict:
    """Evaluate the payment plan agreement task."""
    results = {
        "score": 0,
        "max_score": 100,
        "elements_found": [],
        "elements_missing": [],
        "feedback": ""
    }
    
    # Convert submission to lowercase for case-insensitive matching
    submission_lower = submission.lower()
    
    # Points per element (100 / 14 = ~7.14)
    points_per_element = 100 / len(required_elements)
    
    # Check for each required element
    for element in required_elements:
        found = False
        
        if element == "client_name_michael_rodriguez" and "Michael Rodriguez" in submission:
            found = True
        elif element == "setup_fee_50" and re.search(r'\$50', submission):
            found = True
        elif element == "monthly_service_fee_25" and re.search(r'\$25', submission_lower) and re.search(r'(monthly service|service fee)', submission_lower):
            found = True
        elif element == "monthly_payment_475" and re.search(r'\$475', submission):
            found = True
        elif element == "start_date_november_1_2023" and re.search(r'november 1.{0,3}2023', submission_lower):
            found = True
        elif element == "capital_one_payment_145" and re.search(r'capital one', submission_lower) and re.search(r'\$145', submission):
            found = True
        elif element == "chase_payment_120" and re.search(r'chase', submission_lower) and re.search(r'\$120', submission):
            found = True
        elif element == "bank_of_america_payment_110" and re.search(r'bank of america', submission_lower) and re.search(r'\$110', submission):
            found = True
        elif element == "discover_payment_100" and re.search(r'discover', submission_lower) and re.search(r'\$100', submission):
            found = True
        elif element == "30_day_cancellation_notice" and re.search(r'30.{0,5}day', submission_lower) and re.search(r'(cancel|terminat)', submission_lower):
            found = True
        elif element == "client_responsibilities_complete" and re.search(r'client responsibilities', submission_lower) and re.search(r'make all payments on time', submission_lower):
            found = True
        elif element == "agency_responsibilities_complete" and re.search(r'agency responsibilities', submission_lower) and re.search(r'distribute payments', submission_lower):
            found = True
        elif element == "term_and_termination_complete" and re.search(r'term and termination', submission_lower) and re.search(r'shall remain in effect', submission_lower):
            found = True
        elif element == "disclaimers_complete" and re.search(r'disclaimer', submission_lower) and re.search(r'not guarantee', submission_lower):
            found = True
        
        if found:
            results["elements_found"].append(element)
            results["score"] += points_per_element
        else:
            results["elements_missing"].append(element)
    
    # Round the score to nearest integer
    results["score"] = round(results["score"])
    
    # Generate feedback
    if results["score"] >= 85:
        results["feedback"] = "Excellent work on the payment plan agreement. All or most required elements were included accurately."
    elif results["score"] >= 70:
        results["feedback"] = "Good effort on the payment plan agreement, but some important details were missing."
    else:
        results["feedback"] = "The payment plan agreement needs significant improvement. Many required elements are missing."
    
    return results


def evaluate_task3(submission: str, required_elements: List[str]) -> Dict:
    """Evaluate the educational handout task."""
    results = {
        "score": 0,
        "max_score": 100,
        "elements_found": [],
        "elements_missing": [],
        "feedback": ""
    }
    
    # Convert submission to lowercase for case-insensitive matching
    submission_lower = submission.lower()
    
    # Check for each required element
    for element in required_elements:
        found = False
        
        if element == "payment_history_35_percent" and re.search(r'payment history', submission_lower) and re.search(r'35\s*%', submission_lower):
            found = True
        elif element == "credit_utilization_30_percent" and re.search(r'(credit utilization|amount of credit)', submission_lower) and re.search(r'30\s*%', submission_lower):
            found = True
        elif element == "length_of_credit_history_15_percent" and re.search(r'(length|history).{0,20}credit', submission_lower) and re.search(r'15\s*%', submission_lower):
            found = True
        elif element == "credit_mix_10_percent" and re.search(r'credit mix', submission_lower) and re.search(r'10\s*%', submission_lower):
            found = True
        elif element == "new_credit_10_percent" and re.search(r'new credit', submission_lower) and re.search(r'10\s*%', submission_lower):
            found = True
        elif element == "minimum_5_improvement_actions":
            # Count the number of improvement actions
            improvement_section = re.search(r'(improve|boost|raise|increase).{0,50}(credit score|score).{0,500}(harm|damage|lower|hurt|reduce)', submission_lower, re.DOTALL)
            if improvement_section:
                improvement_text = improvement_section.group(0)
                bullet_points = len(re.findall(r'(\n[-•*]\s|\n\d+\.\s)', improvement_text))
                if bullet_points >= 5:
                    found = True
        elif element == "minimum_5_harmful_actions":
            # Count the number of harmful actions
            harmful_section = re.search(r'(harm|damage|lower|hurt|reduce).{0,50}(credit score|score).{0,500}', submission_lower, re.DOTALL)
            if harmful_section:
                harmful_text = harmful_section.group(0)
                bullet_points = len(re.findall(r'(\n[-•*]\s|\n\d+\.\s)', harmful_text))
                if bullet_points >= 5:
                    found = True
        elif element == "agency_contact_information_complete" and re.search(r'financial wellness', submission) and re.search(r'800.{0,5}555.{0,5}debt', submission_lower, re.DOTALL):
            found = True
        elif element == "three_next_steps_complete" and re.search(r'next steps', submission_lower) and re.search(r'(follow-up|follow up) appointment', submission_lower):
            found = True
        elif element == "professional_formatting" and re.search(r'(credit score|components|improve|harm|next steps)', submission_lower) and not re.search(r'(slang|inappropriate)', submission_lower):
            found = True
        
        if found:
            results["elements_found"].append(element)
            results["score"] += 10
        else:
            results["elements_missing"].append(element)
    
    # Generate feedback
    if results["score"] >= 80:
        results["feedback"] = "Excellent work on the educational handout. Most required elements were included with good formatting."
    elif results["score"] >= 60:
        results["feedback"] = "Good effort on the educational handout, but missing some key elements that would make it more effective."
    else:
        results["feedback"] = "The educational handout needs significant improvement. Many required elements are missing."
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "time_spent": submission.get("time_spent", {}),
        "task1_results": evaluate_task1(submission.get("task1_recommendation_letter", ""), answer_key.get("task1_required_elements", [])),
        "task2_results": evaluate_task2(submission.get("task2_payment_plan", ""), answer_key.get("task2_required_elements", [])),
        "task3_results": evaluate_task3(submission.get("task3_educational_handout", ""), answer_key.get("task3_required_elements", [])),
    }
    
    # Calculate total score
    total_score = results["task1_results"]["score"] + results["task2_results"]["score"] + results["task3_results"]["score"]
    max_score = results["task1_results"]["max_score"] + results["task2_results"]["max_score"] + results["task3_results"]["max_score"]
    results["overall_score"] = round((total_score / max_score) * 100)
    
    # Determine if candidate passed
    tasks_passed = 0
    if results["task1_results"]["score"] >= 80:
        tasks_passed += 1
    if results["task2_results"]["score"] >= 85:  # ~12 out of 14 elements
        tasks_passed += 1
    if results["task3_results"]["score"] >= 80:
        tasks_passed += 1
    
    results["tasks_passed"] = tasks_passed
    results["passed_assessment"] = tasks_passed >= 2 and results["overall_score"] >= 80
    
    # Add overall feedback
    if results["passed_assessment"]:
        results["overall_feedback"] = f"Congratulations! You passed the assessment with an overall score of {results['overall_score']}%. You passed {tasks_passed} out of 3 tasks."
    else:
        results["overall_feedback"] = f"You did not pass the assessment. Your overall score was {results['overall_score']}% and you passed {tasks_passed} out of 3 tasks. Please review the feedback for each task."
    
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
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Tasks passed: {results['tasks_passed']} out of 3")
    print(f"Assessment passed: {results['passed_assessment']}")


if __name__ == "__main__":
    main()