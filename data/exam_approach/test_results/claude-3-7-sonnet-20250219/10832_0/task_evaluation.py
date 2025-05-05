#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_key_information(candidate_info, answer_info):
    """Evaluate the key information identified by the candidate."""
    correct_items = set(answer_info)
    candidate_items = set(candidate_info)
    
    correct_count = len(correct_items.intersection(candidate_items))
    incorrect_count = len(candidate_items - correct_items)
    
    score = correct_count - (0.5 * incorrect_count)
    max_score = len(correct_items)
    
    return {
        "correct_items": list(correct_items.intersection(candidate_items)),
        "incorrect_items": list(candidate_items - correct_items),
        "missing_items": list(correct_items - candidate_items),
        "score": max(0, score),
        "max_score": max_score
    }

def evaluate_violations(candidate_violations, answer_violations):
    """Evaluate the violation types identified by the candidate."""
    correct_violations = set(answer_violations)
    candidate_violations_set = set(candidate_violations)
    
    correct_count = len(correct_violations.intersection(candidate_violations_set))
    incorrect_count = len(candidate_violations_set - correct_violations)
    
    score = 2 * correct_count - (1 * incorrect_count)
    max_score = 2 * len(correct_violations)
    
    return {
        "correct_items": list(correct_violations.intersection(candidate_violations_set)),
        "incorrect_items": list(candidate_violations_set - correct_violations),
        "missing_items": list(correct_violations - candidate_violations_set),
        "score": max(0, score),
        "max_score": max_score
    }

def evaluate_evidence_items(candidate_items, answer_items):
    """Evaluate the evidence items identified by the candidate."""
    correct_items = set(answer_items)
    candidate_items_set = set(candidate_items)
    
    correct_count = len(correct_items.intersection(candidate_items_set))
    incorrect_count = len(candidate_items_set - correct_items)
    
    score = correct_count - (0.5 * incorrect_count)
    max_score = len(correct_items)
    
    return {
        "correct_items": list(correct_items.intersection(candidate_items_set)),
        "incorrect_items": list(candidate_items_set - correct_items),
        "missing_items": list(correct_items - candidate_items_set),
        "score": max(0, score),
        "max_score": max_score
    }

def evaluate_follow_up_actions(candidate_actions, answer_actions):
    """Evaluate the follow-up actions identified by the candidate."""
    if not answer_actions:  # For scenario 1 which has no follow-up actions
        return {
            "correct_items": [],
            "incorrect_items": [],
            "missing_items": [],
            "score": 0,
            "max_score": 0
        }
    
    correct_actions = set(answer_actions)
    candidate_actions_set = set(candidate_actions) if candidate_actions else set()
    
    correct_count = len(correct_actions.intersection(candidate_actions_set))
    incorrect_count = len(candidate_actions_set - correct_actions)
    
    score = correct_count - (0.5 * incorrect_count)
    max_score = len(correct_actions)
    
    return {
        "correct_items": list(correct_actions.intersection(candidate_actions_set)),
        "incorrect_items": list(candidate_actions_set - correct_actions),
        "missing_items": list(correct_actions - candidate_actions_set),
        "score": max(0, score),
        "max_score": max_score
    }

def evaluate_prepared_questions(questions):
    """Placeholder for manual evaluation of prepared questions.
    In a real implementation, this would require human review."""
    # For this implementation, we'll assume all questions are acceptable
    # and award a default score based on having the minimum required questions
    if len(questions) >= 5:
        return {
            "score": 7,  # Default score for having at least 5 questions
            "max_score": 10,
            "comments": "Automated scoring: Questions meet minimum quantity requirement. Manual review recommended."
        }
    else:
        return {
            "score": 3,  # Lower score for not meeting minimum
            "max_score": 10,
            "comments": "Automated scoring: Insufficient number of questions. Manual review recommended."
        }

def evaluate_scenario(scenario_num, candidate_data, answer_key):
    """Evaluate a single scenario."""
    candidate_scenario = candidate_data.get(f"scenario{scenario_num}", {})
    answer_scenario = answer_key.get(f"scenario{scenario_num}", {})
    
    # Evaluate key information
    key_info_result = evaluate_key_information(
        candidate_scenario.get("key_information_identified", []),
        answer_scenario.get("key_information_identified", [])
    )
    
    # Evaluate evidence documentation
    candidate_evidence = candidate_scenario.get("evidence_documentation", {})
    answer_evidence = answer_scenario.get("evidence_documentation", {})
    
    violation_result = evaluate_violations(
        candidate_evidence.get("violation_type", []),
        answer_evidence.get("violation_type", [])
    )
    
    evidence_items_result = evaluate_evidence_items(
        candidate_evidence.get("evidence_items", []),
        answer_evidence.get("evidence_items", [])
    )
    
    follow_up_result = evaluate_follow_up_actions(
        candidate_evidence.get("follow_up_actions", []),
        answer_evidence.get("follow_up_actions", []) if "follow_up_actions" in answer_evidence else []
    )
    
    # Evaluate prepared questions
    questions_result = evaluate_prepared_questions(
        candidate_scenario.get("prepared_questions", [])
    )
    
    # Calculate total score for this scenario
    total_score = (
        key_info_result["score"] +
        violation_result["score"] +
        evidence_items_result["score"] +
        follow_up_result["score"] +
        questions_result["score"]
    )
    
    max_score = (
        key_info_result["max_score"] +
        violation_result["max_score"] +
        evidence_items_result["max_score"] +
        follow_up_result["max_score"] +
        questions_result["max_score"]
    )
    
    return {
        "key_information": key_info_result,
        "violations": violation_result,
        "evidence_items": evidence_items_result,
        "follow_up_actions": follow_up_result,
        "prepared_questions": questions_result,
        "score": total_score,
        "max_score": max_score
    }

def calculate_overall_results(scenario_results):
    """Calculate overall test results and determine pass/fail status."""
    total_score = sum(result["score"] for result in scenario_results.values())
    max_score = sum(result["max_score"] for result in scenario_results.values())
    
    # Calculate percentage score
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    # Determine pass/fail status
    if percentage >= 88:
        status = "Pass with Distinction"
    elif percentage >= 70:
        status = "Pass"
    else:
        status = "Fail"
    
    # Calculate key information percentage across all scenarios
    total_key_info_score = sum(result["key_information"]["score"] for result in scenario_results.values())
    total_key_info_max = sum(result["key_information"]["max_score"] for result in scenario_results.values())
    key_info_percentage = (total_key_info_score / total_key_info_max) * 100 if total_key_info_max > 0 else 0
    
    # Calculate violations percentage across all scenarios
    total_violations_score = sum(result["violations"]["score"] for result in scenario_results.values())
    total_violations_max = sum(result["violations"]["max_score"] for result in scenario_results.values())
    violations_percentage = (total_violations_score / total_violations_max) * 100 if total_violations_max > 0 else 0
    
    # Check if minimum requirements for passing are met
    meets_minimum_requirements = (
        key_info_percentage >= 70 and
        violations_percentage >= 70 and
        all(len(result.get("prepared_questions", {}).get("comments", "").split()) >= 5 
            for result in scenario_results.values())
    )
    
    if not meets_minimum_requirements and status != "Fail":
        status = "Fail (Did not meet minimum requirements)"
    
    return {
        "total_score": total_score,
        "max_score": max_score,
        "overall_score": percentage,
        "status": status,
        "key_information_percentage": key_info_percentage,
        "violations_percentage": violations_percentage,
        "meets_minimum_requirements": meets_minimum_requirements
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the JSON files
    candidate_data = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each scenario
    scenario_results = {}
    for i in range(1, 4):  # Scenarios 1, 2, and 3
        scenario_results[f"scenario{i}"] = evaluate_scenario(i, candidate_data, answer_key)
    
    # Calculate overall results
    overall_results = calculate_overall_results(scenario_results)
    
    # Prepare final results
    final_results = {
        "candidate_id": candidate_data.get("candidate_id", "Unknown"),
        "scenario_results": scenario_results,
        "overall_results": overall_results,
        "overall_score": overall_results["overall_score"]  # Required output
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_results['overall_score']:.2f}%")
    print(f"Status: {overall_results['status']}")

if __name__ == "__main__":
    main()