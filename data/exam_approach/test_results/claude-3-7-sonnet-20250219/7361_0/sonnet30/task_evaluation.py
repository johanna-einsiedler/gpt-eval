#!/usr/bin/env python3
"""
Tax Preparer Client Interview Skills Assessment Evaluator

This script evaluates a candidate's submission for the Tax Preparer Client Interview Skills Assessment
by comparing it against an answer key and scoring according to the defined rubric.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import os
from typing import Dict, List, Any


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_missing_information(candidate_items: List[str], key_items: List[str]) -> int:
    """
    Evaluate the missing information identification.
    
    5 points: Correctly identifies all critical missing information
    3 points: Identifies most critical missing information
    1 point: Identifies only obvious missing information
    0 points: Fails to identify critical missing information
    """
    # Convert to lowercase for case-insensitive comparison
    candidate_items_lower = [item.lower() for item in candidate_items]
    key_items_lower = [item.lower() for item in key_items]
    
    # Count matches using keyword matching
    matches = 0
    for key_item in key_items_lower:
        key_words = set(key_item.split())
        for candidate_item in candidate_items_lower:
            candidate_words = set(candidate_item.split())
            # If there's significant overlap in keywords, count as a match
            if len(key_words.intersection(candidate_words)) >= min(2, len(key_words) // 2):
                matches += 1
                break
    
    match_ratio = matches / len(key_items)
    
    if match_ratio >= 0.8:  # Identifies most or all critical items
        return 5
    elif match_ratio >= 0.5:  # Identifies many critical items
        return 3
    elif match_ratio > 0:  # Identifies at least some items
        return 1
    else:  # Fails to identify critical information
        return 0


def evaluate_interview_questions(candidate_questions: List[str], key_questions: List[str]) -> int:
    """
    Evaluate the interview questions.
    
    5 points: Questions are specific, professionally phrased, and would effectively elicit needed information
    3 points: Questions are adequate but may lack specificity or professional phrasing
    1 point: Questions are too general or poorly phrased
    0 points: Questions would not elicit needed information
    """
    # Check if questions are properly formed (end with question mark, complete sentences)
    properly_formed = all(q.strip().endswith('?') for q in candidate_questions)
    
    # Check for specificity (avoid general questions)
    specificity_score = 0
    general_terms = ['tell me more', 'anything else', 'can you explain', 'additional information']
    for question in candidate_questions:
        q_lower = question.lower()
        if not any(term in q_lower for term in general_terms) and len(question.split()) >= 6:
            specificity_score += 1
    
    specificity_ratio = specificity_score / len(candidate_questions)
    
    # Check for coverage of key topics from answer key
    key_topics = []
    for question in key_questions:
        # Extract main topic words from each key question
        words = question.lower().split()
        # Filter out common words
        topic_words = [w for w in words if len(w) > 3 and w not in ('what', 'when', 'where', 'which', 'would', 'could', 'should', 'have', 'from', 'with', 'your', 'during', 'these', 'those', 'this', 'that', 'there', 'their', 'they')]
        if topic_words:
            key_topics.append(set(topic_words))
    
    topic_matches = 0
    for candidate_q in candidate_questions:
        candidate_words = set(candidate_q.lower().split())
        for topic_set in key_topics:
            if len(topic_set.intersection(candidate_words)) >= min(2, len(topic_set) // 2):
                topic_matches += 1
                break
    
    topic_coverage = topic_matches / len(key_topics) if key_topics else 0
    
    # Calculate final score
    if properly_formed and specificity_ratio >= 0.8 and topic_coverage >= 0.7:
        return 5
    elif properly_formed and specificity_ratio >= 0.5 and topic_coverage >= 0.5:
        return 3
    elif properly_formed or specificity_ratio > 0 or topic_coverage > 0:
        return 1
    else:
        return 0


def evaluate_tax_form(candidate_form: str, key_form: str) -> int:
    """
    Evaluate the tax form identification.
    
    5 points: Correctly identifies the primary tax form/schedule
    2 points: Identifies a related but not primary form
    0 points: Incorrectly identifies tax form
    """
    candidate_form_lower = candidate_form.lower()
    key_form_lower = key_form.lower()
    
    # Exact match
    if candidate_form_lower == key_form_lower:
        return 5
    
    # Check if the candidate identified a related form
    key_form_parts = key_form_lower.split()
    candidate_form_parts = candidate_form_lower.split()
    
    # Check for partial matches (e.g., "Schedule C" vs "Form 1040 Schedule C")
    common_parts = set(key_form_parts).intersection(set(candidate_form_parts))
    if common_parts and ('form' in common_parts or 'schedule' in common_parts):
        return 2
    
    return 0


def evaluate_documentation(candidate_docs: List[str], key_docs: List[str]) -> int:
    """
    Evaluate the documentation requests.
    
    5 points: Requests all necessary documentation with specific descriptions
    3 points: Requests most necessary documentation
    1 point: Requests are too general or miss key documents
    0 points: Fails to request critical documentation
    """
    # Convert to lowercase for case-insensitive comparison
    candidate_docs_lower = [doc.lower() for doc in candidate_docs]
    key_docs_lower = [doc.lower() for doc in key_docs]
    
    # Check for specificity in candidate docs
    specificity_score = sum(1 for doc in candidate_docs if len(doc.split()) >= 3)
    specificity_ratio = specificity_score / len(candidate_docs)
    
    # Count matches using keyword matching
    matches = 0
    for key_doc in key_docs_lower:
        key_words = set(key_doc.split())
        for candidate_doc in candidate_docs_lower:
            candidate_words = set(candidate_doc.split())
            # If there's significant overlap in keywords, count as a match
            if len(key_words.intersection(candidate_words)) >= min(2, len(key_words) // 3):
                matches += 1
                break
    
    match_ratio = matches / len(key_docs)
    
    if match_ratio >= 0.7 and specificity_ratio >= 0.8:
        return 5
    elif match_ratio >= 0.5 and specificity_ratio >= 0.5:
        return 3
    elif match_ratio > 0 or specificity_ratio > 0:
        return 1
    else:
        return 0


def evaluate_scenario(candidate_scenario: Dict, key_scenario: Dict) -> Dict:
    """Evaluate a single scenario and return the scores."""
    missing_info_score = evaluate_missing_information(
        candidate_scenario.get('missing_information', []),
        key_scenario.get('missing_information', [])
    )
    
    interview_questions_score = evaluate_interview_questions(
        candidate_scenario.get('interview_questions', []),
        key_scenario.get('interview_questions', [])
    )
    
    tax_form_score = evaluate_tax_form(
        candidate_scenario.get('tax_form', ''),
        key_scenario.get('tax_form', '')
    )
    
    documentation_score = evaluate_documentation(
        candidate_scenario.get('documentation_needed', []),
        key_scenario.get('documentation_needed', [])
    )
    
    total_score = missing_info_score + interview_questions_score + tax_form_score + documentation_score
    
    return {
        'missing_information_score': missing_info_score,
        'interview_questions_score': interview_questions_score,
        'tax_form_score': tax_form_score,
        'documentation_score': documentation_score,
        'total_scenario_score': total_score
    }


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        'candidate_id': submission.get('candidate_id', 'Unknown'),
        'scenario_results': [],
        'overall_score': 0,
        'passing_status': '',
        'detailed_feedback': {}
    }
    
    # Create a mapping of scenario numbers to scenarios for easier lookup
    submission_scenarios = {s['scenario_number']: s for s in submission.get('scenarios', [])}
    key_scenarios = {s['scenario_number']: s for s in answer_key.get('scenarios', [])}
    
    total_points = 0
    max_points = 0
    
    # Evaluate each scenario
    for scenario_num in sorted(key_scenarios.keys()):
        if scenario_num in submission_scenarios:
            scenario_result = evaluate_scenario(
                submission_scenarios[scenario_num],
                key_scenarios[scenario_num]
            )
            
            scenario_result['scenario_number'] = scenario_num
            results['scenario_results'].append(scenario_result)
            
            total_points += scenario_result['total_scenario_score']
            max_points += 20  # Maximum 20 points per scenario
    
    # Calculate overall percentage score
    if max_points > 0:
        percentage_score = (total_points / max_points) * 100
        results['overall_score'] = round(percentage_score, 2)
    
    # Determine passing status
    if results['overall_score'] >= 90:
        results['passing_status'] = 'Excellent'
    elif results['overall_score'] >= 75:
        results['passing_status'] = 'Proficient'
    elif results['overall_score'] >= 60:
        results['passing_status'] = 'Passing'
    else:
        results['passing_status'] = 'Failing'
    
    # Check additional passing criteria
    scenarios_with_min_score = sum(1 for s in results['scenario_results'] if s['total_scenario_score'] >= 10)
    correct_tax_forms = sum(1 for s in results['scenario_results'] if s['tax_form_score'] == 5)
    
    results['detailed_feedback'] = {
        'total_points': total_points,
        'max_possible_points': max_points,
        'scenarios_with_minimum_score': scenarios_with_min_score,
        'correct_tax_forms_identified': correct_tax_forms,
        'additional_criteria_met': {
            'minimum_10_points_per_scenario': scenarios_with_min_score >= 5,
            'correct_tax_forms_for_4_scenarios': correct_tax_forms >= 4
        }
    }
    
    return results


def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    output_file = 'test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall Score: {results['overall_score']}% - {results['passing_status']}")


if __name__ == "__main__":
    main()