#!/usr/bin/env python3
"""
Loan Officer Practical Exam Evaluation Script

This script evaluates a candidate's loan agreement review submission against an answer key.
It scores the submission based on predefined criteria and generates a detailed results file.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from collections import defaultdict

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def calculate_similarity(candidate_issue, answer_issue):
    """
    Calculate similarity score between candidate issue and answer issue.
    Returns a score between 0 and 1.
    """
    # Check if issue types match
    type_match = candidate_issue["issue_type"] == answer_issue["issue_type"]
    
    # Check if locations are similar (partial match is acceptable)
    location_match = candidate_issue["location"].lower() in answer_issue["location"].lower() or \
                    answer_issue["location"].lower() in candidate_issue["location"].lower()
    
    # Check if descriptions have significant overlap
    candidate_desc_words = set(candidate_issue["description"].lower().split())
    answer_desc_words = set(answer_issue["description"].lower().split())
    common_words = candidate_desc_words.intersection(answer_desc_words)
    
    # Calculate description similarity as proportion of common words
    desc_similarity = len(common_words) / max(len(candidate_desc_words), len(answer_desc_words))
    
    # Weight the components
    similarity = (0.3 * int(type_match)) + (0.3 * int(location_match)) + (0.4 * desc_similarity)
    
    return similarity

def match_issues(candidate_issues, answer_issues):
    """
    Match candidate issues to answer key issues based on similarity.
    Returns a list of (candidate_issue, answer_issue, similarity_score) tuples.
    """
    matches = []
    
    # For each candidate issue, find the best matching answer issue
    for candidate_issue in candidate_issues:
        best_match = None
        best_score = 0
        
        for answer_issue in answer_issues:
            similarity = calculate_similarity(candidate_issue, answer_issue)
            if similarity > best_score:
                best_score = similarity
                best_match = answer_issue
        
        if best_match and best_score > 0.3:  # Threshold for considering it a match
            matches.append((candidate_issue, best_match, best_score))
    
    return matches

def evaluate_submission(submission, answer_key):
    """
    Evaluate the candidate's submission against the answer key.
    Returns detailed evaluation results.
    """
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_score": 0,
        "max_possible_score": 15,
        "agreements": {},
        "issue_type_coverage": defaultdict(int),
        "critical_issues_identified": 0,
        "critical_issues_total": 5,
        "issues_by_agreement": defaultdict(int),
        "detailed_feedback": []
    }
    
    # Define critical issues
    critical_issues = {
        "Agreement_A": [
            "Default Interest Rate policy violation",
            "Monthly payment calculation error"
        ],
        "Agreement_B": [
            "Missing environmental assessment information",
            "Balloon payment calculation error"
        ],
        "Agreement_C": [
            "Contradictory minimum draw requirements"
        ]
    }
    
    # Evaluate each agreement
    for agreement_id in ["Agreement_A", "Agreement_B", "Agreement_C"]:
        candidate_issues = submission.get(agreement_id, [])
        answer_issues = answer_key.get(agreement_id, [])
        
        matches = match_issues(candidate_issues, answer_issues)
        
        agreement_score = 0
        agreement_results = []
        
        # Process matches
        matched_answer_issues = set()
        
        for candidate_issue, answer_issue, similarity in matches:
            # Determine points based on similarity
            if similarity >= 0.8:
                points = 1.0  # Full credit
            elif similarity >= 0.5:
                points = 0.5  # Partial credit
            else:
                points = 0.0  # No credit
            
            # Track issue type coverage
            if points > 0:
                results["issue_type_coverage"][answer_issue["issue_type"]] += 1
                results["issues_by_agreement"][agreement_id] += 1
                
                # Check if this is a critical issue
                for critical_desc in critical_issues.get(agreement_id, []):
                    if critical_desc.lower() in answer_issue["description"].lower():
                        results["critical_issues_identified"] += 1
            
            agreement_score += points
            matched_answer_issues.add(json.dumps(answer_issue))
            
            # Add detailed feedback
            agreement_results.append({
                "candidate_issue": candidate_issue,
                "matched_to": answer_issue,
                "similarity": similarity,
                "points": points,
                "feedback": get_feedback(similarity, candidate_issue, answer_issue)
            })
        
        # Add unmatched answer issues
        for answer_issue in answer_issues:
            if json.dumps(answer_issue) not in matched_answer_issues:
                agreement_results.append({
                    "candidate_issue": None,
                    "matched_to": answer_issue,
                    "similarity": 0,
                    "points": 0,
                    "feedback": "Issue not identified by candidate."
                })
        
        # Add unmatched candidate issues
        matched_candidate_issues = {json.dumps(match[0]) for match in matches}
        for candidate_issue in candidate_issues:
            if json.dumps(candidate_issue) not in matched_candidate_issues:
                agreement_results.append({
                    "candidate_issue": candidate_issue,
                    "matched_to": None,
                    "similarity": 0,
                    "points": 0,
                    "feedback": "This issue does not match any in the answer key. It may be invalid or incorrectly described."
                })
        
        results["agreements"][agreement_id] = {
            "score": agreement_score,
            "max_score": len(answer_issues),
            "issues_identified": len(matches),
            "total_issues": len(answer_issues),
            "detailed_results": agreement_results
        }
        
        results["total_score"] += agreement_score
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_score"] / results["max_possible_score"]) * 100
    
    # Determine if passing criteria are met
    results["passing_criteria"] = {
        "minimum_correct_identifications": {
            "required": 10,
            "achieved": results["total_score"],
            "passed": results["total_score"] >= 10
        },
        "distribution_requirement": {
            "required": "At least 2 issues in each agreement",
            "achieved": {agreement: count for agreement, count in results["issues_by_agreement"].items()},
            "passed": all(count >= 2 for count in results["issues_by_agreement"].values())
        },
        "issue_type_coverage": {
            "required": "At least one issue of each type",
            "achieved": dict(results["issue_type_coverage"]),
            "passed": len(results["issue_type_coverage"]) == 5
        },
        "critical_issues": {
            "required": "At least 3 of 5 critical issues",
            "achieved": results["critical_issues_identified"],
            "passed": results["critical_issues_identified"] >= 3
        }
    }
    
    # Overall pass/fail determination
    results["passed"] = all(criterion["passed"] for criterion in results["passing_criteria"].values())
    
    return results

def get_feedback(similarity, candidate_issue, answer_issue):
    """Generate feedback based on similarity score and issue comparison."""
    if similarity >= 0.8:
        return "Excellent identification of the issue."
    elif similarity >= 0.5:
        if candidate_issue["issue_type"] != answer_issue["issue_type"]:
            return f"Issue identified but incorrectly categorized as '{candidate_issue['issue_type']}' instead of '{answer_issue['issue_type']}'."
        else:
            return "Issue partially identified. Description could be more precise."
    else:
        return "Issue poorly identified. The description does not clearly explain the problem."

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
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Pass/Fail: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()