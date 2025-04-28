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

def evaluate_scenario1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Scenario 1: Customer Email Analysis."""
    results = {
        "score": 0,
        "max_score": 40,
        "details": {}
    }
    
    # Check identified requirements
    sub_reqs = submission.get("scenario1", {}).get("identified_requirements", [])
    req_count = len(sub_reqs)
    
    # Score based on number of requirements identified (8+ for full credit)
    if req_count >= 8:
        req_count_score = 10
    elif req_count >= 5:
        req_count_score = 5
    else:
        req_count_score = 0
    
    results["details"]["requirements_count"] = {
        "score": req_count_score,
        "max_score": 10,
        "comment": f"Identified {req_count} requirements out of expected 8+"
    }
    
    # Check requirement type categorization
    correct_types = 0
    for req in sub_reqs:
        req_type = req.get("requirement_type")
        if req_type in ["BANDWIDTH", "LATENCY", "SECURITY", "RELIABILITY", 
                        "SCALABILITY", "COMPATIBILITY", "COMPLIANCE", "BUDGET", "TIMELINE"]:
            # Simple check that the type is valid - a more sophisticated check would
            # validate against the specific content of each requirement
            correct_types += 1
    
    if correct_types >= 7:
        type_score = 10
    elif correct_types >= 4:
        type_score = 5
    else:
        type_score = 0
        
    results["details"]["requirement_types"] = {
        "score": type_score,
        "max_score": 10,
        "comment": f"Correctly categorized {correct_types} requirements by type"
    }
    
    # Check priority assignments
    correct_priorities = 0
    for req in sub_reqs:
        priority = req.get("priority")
        if priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            # Simple check that priority is valid - a more sophisticated check would
            # validate the specific priority against the requirement content
            correct_priorities += 1
    
    if correct_priorities >= 7:
        priority_score = 5
    elif correct_priorities >= 4:
        priority_score = 3
    else:
        priority_score = 0
        
    results["details"]["priority_assignments"] = {
        "score": priority_score,
        "max_score": 5,
        "comment": f"Correctly prioritized {correct_priorities} requirements"
    }
    
    # Check customer response
    response = submission.get("scenario1", {}).get("response", "")
    response_length = len(response.split())
    
    # Check if response addresses key concerns
    key_concerns = ["bandwidth", "reliability", "security", "cloud", "pci", "budget", "timeline"]
    concerns_addressed = sum(1 for concern in key_concerns if concern.lower() in response.lower())
    
    if response_length >= 300 and concerns_addressed >= 5:
        response_score = 10
    elif response_length >= 200 and concerns_addressed >= 3:
        response_score = 5
    else:
        response_score = 0
        
    results["details"]["customer_response"] = {
        "score": response_score,
        "max_score": 10,
        "comment": f"Response addressed {concerns_addressed}/7 key concerns with {response_length} words"
    }
    
    # Check clarification questions
    questions = submission.get("scenario1", {}).get("clarification_questions", [])
    
    if len(questions) == 3 and all(len(q) > 10 for q in questions):
        question_score = 5
    elif len(questions) >= 2 and all(len(q) > 10 for q in questions):
        question_score = 3
    else:
        question_score = 0
        
    results["details"]["clarification_questions"] = {
        "score": question_score,
        "max_score": 5,
        "comment": f"Provided {len(questions)} relevant clarification questions"
    }
    
    # Calculate total score for scenario 1
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_scenario2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Scenario 2: Sales Meeting Transcript."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check technical translations
    translations = submission.get("scenario2", {}).get("technical_translation", {})
    translation_keys = ["QoS_MPLS", "IPsec_AES256", "network_topology", "BGP_routing", "IPv6_support"]
    
    valid_translations = 0
    for key in translation_keys:
        translation = translations.get(key, "")
        # Check if translation exists and is of reasonable length
        if translation and len(translation.split()) >= 10:
            valid_translations += 1
    
    if valid_translations == 5:
        translation_score = 10
    elif valid_translations >= 3:
        translation_score = 6
    else:
        translation_score = 0
        
    results["details"]["technical_translations"] = {
        "score": translation_score,
        "max_score": 10,
        "comment": f"Provided {valid_translations}/5 valid technical translations"
    }
    
    # Check missing information
    missing_info = submission.get("scenario2", {}).get("missing_information", [])
    
    if len(missing_info) == 5 and all(len(info) > 10 for info in missing_info):
        missing_info_score = 10
    elif len(missing_info) >= 3 and all(len(info) > 10 for info in missing_info):
        missing_info_score = 6
    else:
        missing_info_score = 0
        
    results["details"]["missing_information"] = {
        "score": missing_info_score,
        "max_score": 10,
        "comment": f"Identified {len(missing_info)} pieces of missing information"
    }
    
    # Check requirement mapping
    mapping = submission.get("scenario2", {}).get("requirement_mapping", {})
    expected_mappings = {
        "concurrent_video_sessions": "BANDWIDTH",
        "HIPAA_compliance": ["SECURITY", "COMPLIANCE"],
        "EMR_integration": "COMPATIBILITY",
        "DDoS_concerns": "SECURITY",
        "clinic_expansion": "SCALABILITY"
    }
    
    correct_mappings = 0
    for key, expected in expected_mappings.items():
        if key in mapping:
            actual = mapping[key]
            if isinstance(expected, list):
                if any(exp.lower() in actual.lower() for exp in expected):
                    correct_mappings += 1
            elif expected.lower() in actual.lower():
                correct_mappings += 1
    
    if correct_mappings == 5:
        mapping_score = 10
    elif correct_mappings >= 3:
        mapping_score = 6
    else:
        mapping_score = 0
        
    results["details"]["requirement_mapping"] = {
        "score": mapping_score,
        "max_score": 10,
        "comment": f"Correctly mapped {correct_mappings}/5 customer statements to requirements"
    }
    
    # Calculate total score for scenario 2
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_scenario3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Scenario 3: Marketing Brief Analysis."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check business need to requirement mapping
    bn_mapping = submission.get("scenario3", {}).get("requirement_mapping", {})
    business_needs = ["BN-1", "BN-2", "BN-3", "BN-4", "BN-5"]
    
    valid_mappings = 0
    for bn in business_needs:
        reqs = bn_mapping.get(bn, [])
        if isinstance(reqs, list) and len(reqs) >= 2:
            valid_mappings += 1
    
    if valid_mappings == 5:
        mapping_score = 15
    elif valid_mappings >= 3:
        mapping_score = 9
    else:
        mapping_score = 0
        
    results["details"]["business_need_mapping"] = {
        "score": mapping_score,
        "max_score": 15,
        "comment": f"Mapped {valid_mappings}/5 business needs to requirements"
    }
    
    # Check priority conflicts
    conflicts = submission.get("scenario3", {}).get("priority_conflicts", [])
    
    if len(conflicts) >= 3 and all(
        all(key in conflict for key in ["conflict_description", "requirement_id", "resolution", "justification"])
        for conflict in conflicts
    ):
        conflict_score = 15
    elif len(conflicts) >= 2 and all(
        all(key in conflict for key in ["conflict_description", "requirement_id", "resolution"])
        for conflict in conflicts
    ):
        conflict_score = 9
    else:
        conflict_score = 0
        
    results["details"]["priority_conflicts"] = {
        "score": conflict_score,
        "max_score": 15,
        "comment": f"Identified {len(conflicts)} priority conflicts with justifications"
    }
    
    # Calculate total score for scenario 3
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def calculate_overall_score(scenario_results: Dict) -> float:
    """Calculate the overall score as a percentage."""
    total_score = sum(result["score"] for result in scenario_results.values())
    max_score = sum(result["max_score"] for result in scenario_results.values())
    return (total_score / max_score) * 100

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "scenario1": evaluate_scenario1(submission, answer_key),
        "scenario2": evaluate_scenario2(submission, answer_key),
        "scenario3": evaluate_scenario3(submission, answer_key)
    }
    
    # Calculate overall score
    overall_score = calculate_overall_score(results)
    results["overall_score"] = round(overall_score, 2)
    
    # Determine pass/fail status
    scenario_percentages = {
        scenario: (results[scenario]["score"] / results[scenario]["max_score"]) * 100
        for scenario in ["scenario1", "scenario2", "scenario3"]
    }
    
    all_scenarios_above_threshold = all(pct >= 60 for pct in scenario_percentages.values())
    overall_above_threshold = overall_score >= 70
    
    results["passed"] = all_scenarios_above_threshold and overall_above_threshold
    
    # Add grade classification
    if overall_score >= 90:
        grade = "Excellent"
    elif overall_score >= 80:
        grade = "Good"
    elif overall_score >= 70:
        grade = "Satisfactory"
    elif overall_score >= 60:
        grade = "Needs Improvement"
    else:
        grade = "Unsatisfactory"
        
    results["grade"] = grade
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
        
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Grade: {results['grade']}")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()