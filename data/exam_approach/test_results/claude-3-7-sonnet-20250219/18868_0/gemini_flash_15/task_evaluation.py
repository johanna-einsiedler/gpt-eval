#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Set, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_qualifications(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the identification of required and preferred qualifications."""
    results = {
        "required_qualifications": {
            "score": 0,
            "max_score": 15,
            "details": {
                "identified_count": 0,
                "expected_count": len(answer_key["required_qualifications"]),
                "matches": []
            }
        },
        "preferred_qualifications": {
            "score": 0,
            "max_score": 15,
            "details": {
                "identified_count": 0,
                "expected_count": len(answer_key["preferred_qualifications"]),
                "matches": []
            }
        }
    }
    
    # Check required qualifications
    submission_req = set(q.lower() for q in submission.get("required_qualifications", []))
    answer_req = set(q.lower() for q in answer_key["required_qualifications"])
    
    # Find matches using fuzzy matching (contains or is contained)
    matches = []
    for sub_q in submission_req:
        for ans_q in answer_req:
            if sub_q in ans_q or ans_q in sub_q:
                matches.append((sub_q, ans_q))
                break
    
    # Calculate score for required qualifications
    identified_count = min(len(matches), 5)  # Cap at 5 as per requirements
    results["required_qualifications"]["details"]["identified_count"] = identified_count
    results["required_qualifications"]["details"]["matches"] = matches
    results["required_qualifications"]["score"] = (identified_count / 5) * 15
    
    # Check preferred qualifications
    submission_pref = set(q.lower() for q in submission.get("preferred_qualifications", []))
    answer_pref = set(q.lower() for q in answer_key["preferred_qualifications"])
    
    # Find matches using fuzzy matching
    matches = []
    for sub_q in submission_pref:
        for ans_q in answer_pref:
            if sub_q in ans_q or ans_q in sub_q:
                matches.append((sub_q, ans_q))
                break
    
    # Calculate score for preferred qualifications
    identified_count = min(len(matches), 3)  # Cap at 3 as per requirements
    results["preferred_qualifications"]["details"]["identified_count"] = identified_count
    results["preferred_qualifications"]["details"]["matches"] = matches
    results["preferred_qualifications"]["score"] = (identified_count / 3) * 15
    
    return results

def evaluate_candidate_assessments(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate assessments."""
    results = {
        "candidate_evaluations": {
            "score": 0,
            "max_score": 40,
            "details": {
                "qualification_match_accuracy": 0,
                "score_calculation_accuracy": 0,
                "candidate_evaluations": {}
            }
        }
    }
    
    # Get submission and answer key evaluations
    sub_evals = {e["candidate_id"]: e for e in submission.get("candidate_evaluations", [])}
    ans_evals = {e["candidate_id"]: e for e in answer_key["candidate_evaluations"]}
    
    # Count total qualification assessments
    total_req_assessments = 0
    total_pref_assessments = 0
    correct_req_assessments = 0
    correct_pref_assessments = 0
    score_deviations = []
    
    candidate_results = {}
    
    # Check each candidate
    for candidate_id in ans_evals:
        candidate_result = {
            "required_qualification_accuracy": 0,
            "preferred_qualification_accuracy": 0,
            "score_deviation": 0,
            "meets_minimum_requirements_correct": False
        }
        
        if candidate_id not in sub_evals:
            candidate_results[candidate_id] = candidate_result
            continue
        
        # Check required qualifications
        sub_req = sub_evals[candidate_id].get("required_met", [])
        ans_req = ans_evals[candidate_id]["required_met"]
        
        # Adjust for potential length mismatch
        min_req_len = min(len(sub_req), len(ans_req))
        if min_req_len > 0:
            req_correct = sum(1 for i in range(min_req_len) if sub_req[i] == ans_req[i])
            total_req_assessments += min_req_len
            correct_req_assessments += req_correct
            candidate_result["required_qualification_accuracy"] = req_correct / min_req_len
        
        # Check preferred qualifications
        sub_pref = sub_evals[candidate_id].get("preferred_met", [])
        ans_pref = ans_evals[candidate_id]["preferred_met"]
        
        # Adjust for potential length mismatch
        min_pref_len = min(len(sub_pref), len(ans_pref))
        if min_pref_len > 0:
            pref_correct = sum(1 for i in range(min_pref_len) if sub_pref[i] == ans_pref[i])
            total_pref_assessments += min_pref_len
            correct_pref_assessments += pref_correct
            candidate_result["preferred_qualification_accuracy"] = pref_correct / min_pref_len
        
        # Check score calculation
        sub_score = sub_evals[candidate_id].get("match_score", 0)
        ans_score = ans_evals[candidate_id]["match_score"]
        score_deviation = abs(sub_score - ans_score)
        score_deviations.append(score_deviation)
        candidate_result["score_deviation"] = score_deviation
        
        # Check if correctly identified whether candidate meets minimum requirements
        # Minimum requirements met if all required qualifications are met
        sub_meets_min = all(sub_evals[candidate_id].get("required_met", []))
        ans_meets_min = all(ans_evals[candidate_id]["required_met"])
        candidate_result["meets_minimum_requirements_correct"] = (sub_meets_min == ans_meets_min)
        
        candidate_results[candidate_id] = candidate_result
    
    # Calculate overall qualification match accuracy
    total_assessments = total_req_assessments + total_pref_assessments
    correct_assessments = correct_req_assessments + correct_pref_assessments
    
    if total_assessments > 0:
        qualification_match_accuracy = correct_assessments / total_assessments
    else:
        qualification_match_accuracy = 0
    
    # Calculate score calculation accuracy
    avg_score_deviation = sum(score_deviations) / len(score_deviations) if score_deviations else 0
    score_calculation_accuracy = max(0, 1 - (avg_score_deviation / 100))
    
    # Calculate overall score for candidate evaluations
    # 80% from qualification match accuracy, 20% from score calculation accuracy
    evaluation_score = (qualification_match_accuracy * 0.8 + score_calculation_accuracy * 0.2) * 40
    
    results["candidate_evaluations"]["details"]["qualification_match_accuracy"] = qualification_match_accuracy
    results["candidate_evaluations"]["details"]["score_calculation_accuracy"] = score_calculation_accuracy
    results["candidate_evaluations"]["details"]["candidate_evaluations"] = candidate_results
    results["candidate_evaluations"]["score"] = evaluation_score
    
    return results

def evaluate_candidate_selection(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate selection."""
    results = {
        "candidate_selection": {
            "score": 0,
            "max_score": 30,
            "details": {
                "top_candidates_accuracy": 0,
                "ranking_accuracy": 0,
                "strengths_relevance": 0,
                "top_candidates_comparison": {},
                "strengths_evaluation": {}
            }
        }
    }
    
    # Check top candidates selection
    sub_top = submission.get("top_candidates", [])
    ans_top = answer_key["top_candidates"]
    
    # Calculate top candidates accuracy (15 points)
    common_candidates = set(sub_top) & set(ans_top)
    top_candidates_accuracy = len(common_candidates) / 3 if sub_top else 0
    
    # Calculate ranking accuracy (5 points)
    ranking_accuracy = 0
    if len(sub_top) >= 3:
        # Check if the order is exactly correct
        if sub_top == ans_top:
            ranking_accuracy = 1.0
        # Check if the top candidate is correct
        elif sub_top[0] == ans_top[0]:
            ranking_accuracy = 0.6
        # Check if the top 2 candidates are correct but in wrong order
        elif set(sub_top[:2]) == set(ans_top[:2]):
            ranking_accuracy = 0.4
        # Some ranking is correct but not optimal
        elif len(common_candidates) > 0:
            ranking_accuracy = 0.2
    
    # Evaluate strengths relevance (10 points)
    strengths_relevance = 0
    strengths_evaluation = {}
    
    for candidate_id in common_candidates:
        if candidate_id in submission.get("top_candidate_strengths", {}) and candidate_id in answer_key["top_candidate_strengths"]:
            sub_strengths = submission["top_candidate_strengths"][candidate_id]
            ans_strengths = answer_key["top_candidate_strengths"][candidate_id]
            
            # Check if at least 3 strengths are provided
            has_min_strengths = len(sub_strengths) >= 3
            
            # Check relevance of strengths
            relevant_count = 0
            for sub_str in sub_strengths:
                for ans_str in ans_strengths:
                    if any(keyword in sub_str.lower() for keyword in ans_str.lower().split()):
                        relevant_count += 1
                        break
            
            relevance_score = min(1.0, relevant_count / 3)
            
            strengths_evaluation[candidate_id] = {
                "has_minimum_strengths": has_min_strengths,
                "relevance_score": relevance_score
            }
            
            # Add to overall strengths relevance score
            strengths_relevance += relevance_score / 3  # Divide by 3 for the 3 candidates
    
    # Calculate overall candidate selection score
    selection_score = (
        (top_candidates_accuracy * 15) +
        (ranking_accuracy * 5) +
        (strengths_relevance * 10)
    )
    
    # Populate results
    results["candidate_selection"]["details"]["top_candidates_accuracy"] = top_candidates_accuracy
    results["candidate_selection"]["details"]["ranking_accuracy"] = ranking_accuracy
    results["candidate_selection"]["details"]["strengths_relevance"] = strengths_relevance
    results["candidate_selection"]["details"]["top_candidates_comparison"] = {
        "submission": sub_top,
        "answer_key": ans_top,
        "common_candidates": list(common_candidates)
    }
    results["candidate_selection"]["details"]["strengths_evaluation"] = strengths_evaluation
    results["candidate_selection"]["score"] = selection_score
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_sections": {}
    }
    
    # Evaluate each section
    qualification_results = evaluate_qualifications(submission, answer_key)
    assessment_results = evaluate_candidate_assessments(submission, answer_key)
    selection_results = evaluate_candidate_selection(submission, answer_key)
    
    # Combine results
    results["evaluation_sections"].update(qualification_results)
    results["evaluation_sections"].update(assessment_results)
    results["evaluation_sections"].update(selection_results)
    
    # Calculate overall score
    total_score = (
        qualification_results["required_qualifications"]["score"] +
        qualification_results["preferred_qualifications"]["score"] +
        assessment_results["candidate_evaluations"]["score"] +
        selection_results["candidate_selection"]["score"]
    )
    
    max_score = (
        qualification_results["required_qualifications"]["max_score"] +
        qualification_results["preferred_qualifications"]["max_score"] +
        assessment_results["candidate_evaluations"]["max_score"] +
        selection_results["candidate_selection"]["max_score"]
    )
    
    results["overall_score"] = (total_score / max_score) * 100
    results["passing_threshold"] = 75
    results["passed"] = results["overall_score"] >= 75
    
    return results

def main():
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
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()