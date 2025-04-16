#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any, List, Union, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        sys.exit(1)

def evaluate_exercise1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Evaluate Exercise 1: Regulatory Compliance Analysis."""
    max_points = 8
    points = 0
    details = {}
    
    for scenario in ["scenario1", "scenario2", "scenario3", "scenario4"]:
        details[scenario] = {"points": 0, "max_points": 2, "feedback": []}
        
        # Check if compliance determination is correct
        if submission["exercise1"][scenario]["compliant"] == answer_key["exercise1"][scenario]["compliant"]:
            points += 1
            details[scenario]["points"] += 1
            details[scenario]["feedback"].append("Correct compliance determination.")
        else:
            details[scenario]["feedback"].append("Incorrect compliance determination.")
        
        # Check if regulation violated is correct
        sub_reg = submission["exercise1"][scenario]["regulation_violated"]
        key_reg = answer_key["exercise1"][scenario]["regulation_violated"]
        
        if (sub_reg == key_reg) or (sub_reg is None and key_reg is None):
            points += 1
            details[scenario]["points"] += 1
            details[scenario]["feedback"].append("Correct regulation identification.")
        else:
            details[scenario]["feedback"].append(f"Incorrect regulation identification. Expected: {key_reg}, Got: {sub_reg}")
    
    return points, details

def evaluate_exercise2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Evaluate Exercise 2: Contract Review for Regulatory Compliance."""
    max_points = 6
    points = 0
    details = {}
    
    for issue in ["issue1", "issue2", "issue3"]:
        details[issue] = {"points": 0, "max_points": 2, "feedback": []}
        
        # Check if clause number is correct
        if submission["exercise2"][issue]["clause_number"] == answer_key["exercise2"][issue]["clause_number"]:
            points += 1
            details[issue]["points"] += 1
            details[issue]["feedback"].append("Correct clause number identification.")
        else:
            sub_clause = submission["exercise2"][issue]["clause_number"]
            key_clause = answer_key["exercise2"][issue]["clause_number"]
            details[issue]["feedback"].append(f"Incorrect clause number. Expected: {key_clause}, Got: {sub_clause}")
        
        # Check if regulation violated is correct
        if submission["exercise2"][issue]["regulation_violated"] == answer_key["exercise2"][issue]["regulation_violated"]:
            points += 1
            details[issue]["points"] += 1
            details[issue]["feedback"].append("Correct regulation identification.")
        else:
            sub_reg = submission["exercise2"][issue]["regulation_violated"]
            key_reg = answer_key["exercise2"][issue]["regulation_violated"]
            details[issue]["feedback"].append(f"Incorrect regulation identification. Expected: {key_reg}, Got: {sub_reg}")
    
    return points, details

def evaluate_exercise3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Evaluate Exercise 3: Compliance Documentation Requirements."""
    max_points = 3
    points = 0
    details = {}
    
    # Check required fields
    details["required_fields"] = {"points": 0, "max_points": 1, "feedback": []}
    submission_fields_set = set(submission["exercise3"]["required_fields"])
    answer_fields_set = set(answer_key["exercise3"]["required_fields"])
    
    if submission_fields_set == answer_fields_set:
        points += 1
        details["required_fields"]["points"] = 1
        details["required_fields"]["feedback"].append("Correct required fields identified.")
    else:
        missing = answer_fields_set - submission_fields_set
        extra = submission_fields_set - answer_fields_set
        feedback = []
        if missing:
            feedback.append(f"Missing fields: {', '.join(missing)}")
        if extra:
            feedback.append(f"Extra fields: {', '.join(extra)}")
        details["required_fields"]["feedback"] = feedback if feedback else ["Incorrect required fields."]
    
    # Check retention period
    details["retention_period"] = {"points": 0, "max_points": 1, "feedback": []}
    if submission["exercise3"]["retention_period"] == answer_key["exercise3"]["retention_period"]:
        points += 1
        details["retention_period"]["points"] = 1
        details["retention_period"]["feedback"].append("Correct retention period identified.")
    else:
        sub_period = submission["exercise3"]["retention_period"]
        key_period = answer_key["exercise3"]["retention_period"]
        details["retention_period"]["feedback"].append(f"Incorrect retention period. Expected: {key_period}, Got: {sub_period}")
    
    # Check approval level
    details["approval_level"] = {"points": 0, "max_points": 1, "feedback": []}
    if submission["exercise3"]["approval_level"] == answer_key["exercise3"]["approval_level"]:
        points += 1
        details["approval_level"]["points"] = 1
        details["approval_level"]["feedback"].append("Correct approval level identified.")
    else:
        sub_level = submission["exercise3"]["approval_level"]
        key_level = answer_key["exercise3"]["approval_level"]
        details["approval_level"]["feedback"].append(f"Incorrect approval level. Expected: {key_level}, Got: {sub_level}")
    
    return points, details

def evaluate_exercise4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Evaluate Exercise 4: Regulatory Change Response."""
    max_points = 3
    points = 0
    details = {}
    
    # Check affected processes
    details["affected_processes"] = {"points": 0, "max_points": 1, "feedback": []}
    submission_processes_set = set(submission["exercise4"]["affected_processes"])
    answer_processes_set = set(answer_key["exercise4"]["affected_processes"])
    
    if submission_processes_set == answer_processes_set:
        points += 1
        details["affected_processes"]["points"] = 1
        details["affected_processes"]["feedback"].append("Correct affected processes identified.")
    else:
        missing = answer_processes_set - submission_processes_set
        extra = submission_processes_set - answer_processes_set
        feedback = []
        if missing:
            feedback.append(f"Missing processes: {', '.join(missing)}")
        if extra:
            feedback.append(f"Extra processes: {', '.join(extra)}")
        details["affected_processes"]["feedback"] = feedback if feedback else ["Incorrect affected processes."]
    
    # Check required actions
    details["required_actions"] = {"points": 0, "max_points": 1, "feedback": []}
    submission_actions_set = set(submission["exercise4"]["required_actions"])
    answer_actions_set = set(answer_key["exercise4"]["required_actions"])
    
    if submission_actions_set == answer_actions_set:
        points += 1
        details["required_actions"]["points"] = 1
        details["required_actions"]["feedback"].append("Correct required actions identified.")
    else:
        missing = answer_actions_set - submission_actions_set
        extra = submission_actions_set - answer_actions_set
        feedback = []
        if missing:
            feedback.append(f"Missing actions: {', '.join(missing)}")
        if extra:
            feedback.append(f"Extra actions: {', '.join(extra)}")
        details["required_actions"]["feedback"] = feedback if feedback else ["Incorrect required actions."]
    
    # Check implementation deadline
    details["implementation_deadline"] = {"points": 0, "max_points": 1, "feedback": []}
    if submission["exercise4"]["implementation_deadline"] == answer_key["exercise4"]["implementation_deadline"]:
        points += 1
        details["implementation_deadline"]["points"] = 1
        details["implementation_deadline"]["feedback"].append("Correct implementation deadline identified.")
    else:
        sub_deadline = submission["exercise4"]["implementation_deadline"]
        key_deadline = answer_key["exercise4"]["implementation_deadline"]
        details["implementation_deadline"]["feedback"].append(f"Incorrect implementation deadline. Expected: {key_deadline}, Got: {sub_deadline}")
    
    return points, details

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the complete submission against the answer key."""
    results = {
        "overall_score": 0,
        "total_points": 0,
        "max_points": 20,
        "passed": False,
        "exercises": {}
    }
    
    # Evaluate each exercise
    ex1_points, ex1_details = evaluate_exercise1(submission, answer_key)
    ex2_points, ex2_details = evaluate_exercise2(submission, answer_key)
    ex3_points, ex3_details = evaluate_exercise3(submission, answer_key)
    ex4_points, ex4_details = evaluate_exercise4(submission, answer_key)
    
    # Store individual exercise results
    results["exercises"]["exercise1"] = {
        "points": ex1_points,
        "max_points": 8,
        "details": ex1_details
    }
    
    results["exercises"]["exercise2"] = {
        "points": ex2_points,
        "max_points": 6,
        "details": ex2_details
    }
    
    results["exercises"]["exercise3"] = {
        "points": ex3_points,
        "max_points": 3,
        "details": ex3_details
    }
    
    results["exercises"]["exercise4"] = {
        "points": ex4_points,
        "max_points": 3,
        "details": ex4_details
    }
    
    # Calculate total points
    total_points = ex1_points + ex2_points + ex3_points + ex4_points
    results["total_points"] = total_points
    
    # Calculate percentage score
    results["overall_score"] = (total_points / 20) * 100
    
    # Determine if passed based on criteria
    passed = (
        total_points >= 16 and  # At least 80% overall
        ex1_points >= 6 and     # At least 75% in Exercise 1
        ex2_points >= 4 and     # At least 67% in Exercise 2
        ex3_points >= 1 and     # At least 1 point in Exercise 3
        ex4_points >= 1         # At least 1 point in Exercise 4
    )
    
    results["passed"] = passed
    
    # Add candidate ID if available
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
    return results

def main():
    """Main function to parse arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}% ({results['total_points']}/{results['max_points']} points)")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()