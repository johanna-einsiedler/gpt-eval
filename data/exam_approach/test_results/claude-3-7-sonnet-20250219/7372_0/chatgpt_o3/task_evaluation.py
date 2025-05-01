#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Union

def load_json(file_path: str) -> Dict:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Identifying Assumptions."""
    results = {
        "points": 0,
        "max_points": 12,
        "details": {}
    }
    
    for statement_num in range(1, 4):
        statement_key = f"statement_{statement_num}"
        results["details"][statement_key] = {
            "explicit_assumptions": {
                "correct": [],
                "incorrect": [],
                "missing": []
            },
            "implicit_assumptions": {
                "correct": [],
                "incorrect": [],
                "missing": []
            }
        }
        
        # Check if statement exists in submission
        if statement_key not in submission.get("task1", {}):
            results["details"][statement_key]["status"] = "missing"
            continue
        
        # Evaluate explicit assumptions
        sub_explicit = submission["task1"][statement_key].get("explicit_assumptions", [])
        key_explicit = answer_key["task1"][statement_key].get("explicit_assumptions", [])
        
        # Simple string matching might be too strict, so we'll use a more flexible approach
        # For each submission assumption, check if it's similar to any key assumption
        for sub_assumption in sub_explicit:
            found_match = False
            for key_assumption in key_explicit:
                # Check if the submission assumption is similar to the key assumption
                # This is a simple check; in a real-world scenario, you might want to use NLP techniques
                if any(word.lower() in sub_assumption.lower() for word in key_assumption.lower().split()):
                    results["details"][statement_key]["explicit_assumptions"]["correct"].append(sub_assumption)
                    results["points"] += 1
                    found_match = True
                    break
            if not found_match:
                results["details"][statement_key]["explicit_assumptions"]["incorrect"].append(sub_assumption)
        
        # Check for missing key assumptions
        for key_assumption in key_explicit:
            if not any(any(word.lower() in sub_assumption.lower() for word in key_assumption.lower().split()) 
                      for sub_assumption in sub_explicit):
                results["details"][statement_key]["explicit_assumptions"]["missing"].append(key_assumption)
        
        # Evaluate implicit assumptions
        sub_implicit = submission["task1"][statement_key].get("implicit_assumptions", [])
        key_implicit = answer_key["task1"][statement_key].get("implicit_assumptions", [])
        
        for sub_assumption in sub_implicit:
            found_match = False
            for key_assumption in key_implicit:
                if any(word.lower() in sub_assumption.lower() for word in key_assumption.lower().split()):
                    results["details"][statement_key]["implicit_assumptions"]["correct"].append(sub_assumption)
                    results["points"] += 1
                    found_match = True
                    break
            if not found_match:
                results["details"][statement_key]["implicit_assumptions"]["incorrect"].append(sub_assumption)
        
        for key_assumption in key_implicit:
            if not any(any(word.lower() in sub_assumption.lower() for word in key_assumption.lower().split()) 
                      for sub_assumption in sub_implicit):
                results["details"][statement_key]["implicit_assumptions"]["missing"].append(key_assumption)
    
    # Cap points at max_points
    results["points"] = min(results["points"], results["max_points"])
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Exploring Consequences."""
    results = {
        "points": 0,
        "max_points": 16,
        "details": {
            "assumption_set_A": {
                "consequences": {
                    "correct": [],
                    "incorrect": [],
                    "missing": []
                },
                "statements": {
                    "correct": [],
                    "incorrect": []
                }
            },
            "assumption_set_B": {
                "consequences": {
                    "correct": [],
                    "incorrect": [],
                    "missing": []
                },
                "statements": {
                    "correct": [],
                    "incorrect": []
                }
            }
        }
    }
    
    for set_key in ["assumption_set_A", "assumption_set_B"]:
        # Check if set exists in submission
        if set_key not in submission.get("task2", {}):
            results["details"][set_key]["status"] = "missing"
            continue
        
        # Evaluate consequences
        sub_consequences = submission["task2"][set_key].get("consequences", [])
        key_consequences = answer_key["task2"][set_key].get("consequences", [])
        
        for sub_consequence in sub_consequences:
            found_match = False
            for key_consequence in key_consequences:
                # Check if the submission consequence is similar to the key consequence
                if any(word.lower() in sub_consequence.lower() for word in key_consequence.lower().split()):
                    results["details"][set_key]["consequences"]["correct"].append(sub_consequence)
                    results["points"] += 1
                    found_match = True
                    break
            if not found_match:
                results["details"][set_key]["consequences"]["incorrect"].append(sub_consequence)
        
        for key_consequence in key_consequences:
            if not any(any(word.lower() in sub_consequence.lower() for word in key_consequence.lower().split()) 
                      for sub_consequence in sub_consequences):
                results["details"][set_key]["consequences"]["missing"].append(key_consequence)
        
        # Evaluate valid statements
        sub_valid = set(submission["task2"][set_key].get("valid_statements", []))
        key_valid = set(answer_key["task2"][set_key].get("valid_statements", []))
        
        correct_valid = sub_valid.intersection(key_valid)
        incorrect_valid = sub_valid - key_valid
        
        results["details"][set_key]["statements"]["correct"].extend([f"Valid: {stmt}" for stmt in correct_valid])
        results["details"][set_key]["statements"]["incorrect"].extend([f"Invalid but marked valid: {stmt}" for stmt in incorrect_valid])
        results["points"] += len(correct_valid)
        
        # Evaluate invalid statements
        sub_invalid = set(submission["task2"][set_key].get("invalid_statements", []))
        key_invalid = set(answer_key["task2"][set_key].get("invalid_statements", []))
        
        correct_invalid = sub_invalid.intersection(key_invalid)
        incorrect_invalid = sub_invalid - key_invalid
        
        results["details"][set_key]["statements"]["correct"].extend([f"Invalid: {stmt}" for stmt in correct_invalid])
        results["details"][set_key]["statements"]["incorrect"].extend([f"Valid but marked invalid: {stmt}" for stmt in incorrect_invalid])
        results["points"] += len(correct_invalid)
    
    # Cap points at max_points
    results["points"] = min(results["points"], results["max_points"])
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Analyzing Assumption Changes."""
    results = {
        "points": 0,
        "max_points": 9,
        "details": {}
    }
    
    for scenario_num in range(1, 4):
        scenario_key = f"scenario{scenario_num}"
        results["details"][scenario_key] = {
            "original_conclusion": {
                "correct": False,
                "submitted": None,
                "expected": None
            },
            "modified_conclusion": {
                "correct": False,
                "submitted": None,
                "expected": None
            },
            "critical_assumption": {
                "correct": False,
                "submitted": None,
                "expected": None
            }
        }
        
        # Check if scenario exists in submission
        if scenario_key not in submission.get("task3", {}):
            results["details"][scenario_key]["status"] = "missing"
            continue
        
        # Evaluate original conclusion
        sub_original = submission["task3"][scenario_key].get("original_conclusion")
        key_original = answer_key["task3"][scenario_key].get("original_conclusion")
        
        results["details"][scenario_key]["original_conclusion"]["submitted"] = sub_original
        results["details"][scenario_key]["original_conclusion"]["expected"] = key_original
        
        if sub_original == key_original:
            results["details"][scenario_key]["original_conclusion"]["correct"] = True
            results["points"] += 1
        
        # Evaluate modified conclusion
        sub_modified = submission["task3"][scenario_key].get("modified_conclusion")
        key_modified = answer_key["task3"][scenario_key].get("modified_conclusion")
        
        results["details"][scenario_key]["modified_conclusion"]["submitted"] = sub_modified
        results["details"][scenario_key]["modified_conclusion"]["expected"] = key_modified
        
        if sub_modified == key_modified:
            results["details"][scenario_key]["modified_conclusion"]["correct"] = True
            results["points"] += 1
        
        # Evaluate critical assumption
        sub_critical = submission["task3"][scenario_key].get("critical_assumption")
        key_critical = answer_key["task3"][scenario_key].get("critical_assumption")
        
        results["details"][scenario_key]["critical_assumption"]["submitted"] = sub_critical
        results["details"][scenario_key]["critical_assumption"]["expected"] = key_critical
        
        if sub_critical == key_critical:
            results["details"][scenario_key]["critical_assumption"]["correct"] = True
            results["points"] += 1
    
    # Cap points at max_points
    results["points"] = min(results["points"], results["max_points"])
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission."""
    results = {
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key),
        "candidate_id": submission.get("candidate_id", "Unknown")
    }
    
    # Calculate overall score
    total_points = sum(results[task]["points"] for task in ["task1", "task2", "task3"])
    max_points = sum(results[task]["max_points"] for task in ["task1", "task2", "task3"])
    results["overall_score"] = (total_points / max_points) * 100
    
    # Determine if the candidate passed
    passing_threshold = 70
    results["passed"] = results["overall_score"] >= passing_threshold
    
    # Check specific passing criteria
    task1_min_correct = 4  # At least 2 correct explicit and 2 correct implicit assumptions
    task2_min_consequences = 4  # At least 4 correct consequences
    task2_min_statements = 7  # At least 7 correct statement classifications
    task3_min_correct = 6  # At least 2 correct for each of the 3 components
    
    # Count correct assumptions in Task 1
    task1_correct = 0
    for statement in results["task1"]["details"].values():
        if isinstance(statement, dict) and "explicit_assumptions" in statement:
            task1_correct += len(statement["explicit_assumptions"]["correct"])
            task1_correct += len(statement["implicit_assumptions"]["correct"])
    
    # Count correct consequences in Task 2
    task2_consequences_correct = 0
    for set_key in ["assumption_set_A", "assumption_set_B"]:
        if set_key in results["task2"]["details"]:
            task2_consequences_correct += len(results["task2"]["details"][set_key]["consequences"]["correct"])
    
    # Count correct statement classifications in Task 2
    task2_statements_correct = 0
    for set_key in ["assumption_set_A", "assumption_set_B"]:
        if set_key in results["task2"]["details"]:
            task2_statements_correct += len([s for s in results["task2"]["details"][set_key]["statements"]["correct"] 
                                           if s.startswith("Valid:") or s.startswith("Invalid:")])
    
    # Count correct answers in Task 3
    task3_correct = 0
    for scenario in results["task3"]["details"].values():
        if isinstance(scenario, dict):
            if scenario.get("original_conclusion", {}).get("correct", False):
                task3_correct += 1
            if scenario.get("modified_conclusion", {}).get("correct", False):
                task3_correct += 1
            if scenario.get("critical_assumption", {}).get("correct", False):
                task3_correct += 1
    
    # Check if all specific criteria are met
    criteria_passed = (
        task1_correct >= task1_min_correct and
        task2_consequences_correct >= task2_min_consequences and
        task2_statements_correct >= task2_min_statements and
        task3_correct >= task3_min_correct
    )
    
    results["criteria_details"] = {
        "task1_correct": task1_correct,
        "task1_min_required": task1_min_correct,
        "task1_passed": task1_correct >= task1_min_correct,
        
        "task2_consequences_correct": task2_consequences_correct,
        "task2_consequences_min_required": task2_min_consequences,
        "task2_consequences_passed": task2_consequences_correct >= task2_min_consequences,
        
        "task2_statements_correct": task2_statements_correct,
        "task2_statements_min_required": task2_min_statements,
        "task2_statements_passed": task2_statements_correct >= task2_min_statements,
        
        "task3_correct": task3_correct,
        "task3_min_required": task3_min_correct,
        "task3_passed": task3_correct >= task3_min_correct
    }
    
    results["all_criteria_passed"] = criteria_passed
    results["final_result"] = "PASS" if results["passed"] and criteria_passed else "FAIL"
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Final result: {results['final_result']}")

if __name__ == "__main__":
    main()