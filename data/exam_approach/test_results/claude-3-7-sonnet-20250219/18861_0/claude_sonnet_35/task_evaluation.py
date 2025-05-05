#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Policy Interpretation (30 points)"""
    results = {}
    total_points = 0
    points_per_question = 6
    
    # Question 1: Waiting period for health benefits
    if submission.get("question1") == answer_key.get("question1"):
        results["question1"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question1", "").strip() == "60":
        # Partial credit for correct number without units
        results["question1"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Missing 'calendar days'"}
        total_points += points_per_question/2
    else:
        results["question1"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question1')}"}
    
    # Question 2: Documentation for bereavement leave
    if submission.get("question2") == answer_key.get("question2"):
        results["question2"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif all(key_term in submission.get("question2", "").lower() for key_term in 
             ["bereavement leave request form", "documentation", "death", "7"]):
        # Partial credit if all key elements are present but not exact wording
        results["question2"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Contains key information but not exact wording"}
        total_points += points_per_question/2
    else:
        results["question2"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question2')}"}
    
    # Question 3: Progressive disciplinary steps
    sub_q3 = submission.get("question3", [])
    key_q3 = answer_key.get("question3", [])
    
    if isinstance(sub_q3, list) and len(sub_q3) >= 3:
        if sub_q3[:3] == key_q3:
            # Correct first three steps
            results["question3"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
            total_points += points_per_question
        elif len(sub_q3) == 4 and sub_q3[:3] == key_q3:
            # Listed all four steps instead of three, but first three are correct
            results["question3"] = {"score": points_per_question/2, "max": points_per_question, 
                                   "feedback": "Partially correct. Listed all four steps instead of three requested"}
            total_points += points_per_question/2
        else:
            results["question3"] = {"score": 0, "max": points_per_question, 
                                   "feedback": f"Incorrect. Expected: {key_q3}"}
    else:
        results["question3"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect format or missing answer. Expected a list with 3 items"}
    
    # Question 4: Maximum paid sick days
    if submission.get("question4") == answer_key.get("question4"):
        results["question4"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question4") == "8 days" or submission.get("question4") == "8 paid sick days":
        # Partial credit for correct number with different units
        results["question4"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Expected just the number '8'"}
        total_points += points_per_question/2
    else:
        results["question4"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question4')}"}
    
    # Question 5: Overtime approval procedure
    if submission.get("question5") == answer_key.get("question5"):
        results["question5"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif all(key_term in submission.get("question5", "").lower() for key_term in 
             ["overtime request form", "24 hours", "supervisor", "approve", "payroll"]):
        # Partial credit if all key elements are present but not exact wording
        results["question5"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Contains key information but not exact wording"}
        total_points += points_per_question/2
    else:
        results["question5"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question5')}"}
    
    return {"results": results, "total_points": total_points, "max_points": 30}

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Regulatory Compliance (30 points)"""
    results = {}
    total_points = 0
    points_per_question = 6
    
    # Question 1: Maximum weeks for FMLA leave
    if submission.get("question1") == answer_key.get("question1"):
        results["question1"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question1") == "12 weeks" or submission.get("question1") == "12 workweeks":
        # Partial credit for correct number with units
        results["question1"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Expected just the number '12'"}
        total_points += points_per_question/2
    else:
        results["question1"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question1')}"}
    
    # Question 2: Steps in ADA interactive accommodation process
    sub_q2 = submission.get("question2", [])
    key_q2 = answer_key.get("question2", [])
    
    if isinstance(sub_q2, list) and sub_q2 == key_q2:
        results["question2"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif isinstance(sub_q2, list) and set(sub_q2) == set(key_q2):
        # Partial credit if all steps are present but in wrong order
        results["question2"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. All steps present but in wrong order"}
        total_points += points_per_question/2
    else:
        results["question2"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {key_q2}"}
    
    # Question 3: HR response time for harassment complaints
    if submission.get("question3") == answer_key.get("question3"):
        results["question3"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question3") == "2":
        # Partial credit for correct number without units
        results["question3"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Missing 'business days'"}
        total_points += points_per_question/2
    else:
        results["question3"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question3')}"}
    
    # Question 4: Required workplace postings
    sub_q4 = submission.get("question4", [])
    key_q4 = answer_key.get("question4", [])
    
    if isinstance(sub_q4, list) and sub_q4 == key_q4:
        results["question4"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif isinstance(sub_q4, list) and len(sub_q4) > 3 and all(item in sub_q4 for item in key_q4):
        # Partial credit if listed more than three but includes the correct three
        results["question4"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Listed more than three postings"}
        total_points += points_per_question/2
    else:
        results["question4"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {key_q4}"}
    
    # Question 5: Minimum employees for FMLA
    if submission.get("question5") == answer_key.get("question5"):
        results["question5"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question5") == "50 employees":
        # Partial credit for correct number with units
        results["question5"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Expected just the number '50'"}
        total_points += points_per_question/2
    else:
        results["question5"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question5')}"}
    
    return {"results": results, "total_points": total_points, "max_points": 30}

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Policy Application (40 points)"""
    results = {}
    total_points = 0
    points_per_question = 8
    
    # Question 1: FMLA eligibility with 11 months employment
    if submission.get("question1") == answer_key.get("question1"):
        results["question1"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question1", "").lower() == "no":
        # Case insensitive match
        results["question1"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    else:
        results["question1"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question1')}"}
    
    # Question 2: Correct response to ADA accommodation request
    if submission.get("question2") == answer_key.get("question2"):
        results["question2"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    else:
        results["question2"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question2')}"}
    
    # Question 3: Timeframe for reporting harassment
    if submission.get("question3") == answer_key.get("question3"):
        results["question3"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif "90" in submission.get("question3", ""):
        # Partial credit if the number is correct but format is different
        results["question3"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Contains '90' but not exact format"}
        total_points += points_per_question/2
    else:
        results["question3"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question3')}"}
    
    # Question 4: Leave type for child with serious health condition
    if submission.get("question4") == answer_key.get("question4"):
        results["question4"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif "family" in submission.get("question4", "").lower() and "medical" in submission.get("question4", "").lower():
        # Partial credit if contains key terms but not exact match
        results["question4"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Contains key terms but not exact match"}
        total_points += points_per_question/2
    else:
        results["question4"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question4')}"}
    
    # Question 5: Minimum meal break for 8-hour shift
    if submission.get("question5") == answer_key.get("question5"):
        results["question5"] = {"score": points_per_question, "max": points_per_question, "feedback": "Correct"}
        total_points += points_per_question
    elif submission.get("question5") == "45":
        # Partial credit for correct number without units
        results["question5"] = {"score": points_per_question/2, "max": points_per_question, 
                               "feedback": "Partially correct. Missing 'minutes'"}
        total_points += points_per_question/2
    else:
        results["question5"] = {"score": 0, "max": points_per_question, 
                               "feedback": f"Incorrect. Expected: {answer_key.get('question5')}"}
    
    return {"results": results, "total_points": total_points, "max_points": 40}

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    section1_results = evaluate_section1(submission.get("section1", {}), answer_key.get("section1", {}))
    section2_results = evaluate_section2(submission.get("section2", {}), answer_key.get("section2", {}))
    section3_results = evaluate_section3(submission.get("section3", {}), answer_key.get("section3", {}))
    
    # Calculate overall score
    total_points = section1_results["total_points"] + section2_results["total_points"] + section3_results["total_points"]
    max_points = section1_results["max_points"] + section2_results["max_points"] + section3_results["max_points"]
    overall_score = (total_points / max_points) * 100
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "section1": section1_results["results"],
        "section2": section2_results["results"],
        "section3": section3_results["results"],
        "section_scores": {
            "section1": {
                "points": section1_results["total_points"],
                "max_points": section1_results["max_points"],
                "percentage": (section1_results["total_points"] / section1_results["max_points"]) * 100
            },
            "section2": {
                "points": section2_results["total_points"],
                "max_points": section2_results["max_points"],
                "percentage": (section2_results["total_points"] / section2_results["max_points"]) * 100
            },
            "section3": {
                "points": section3_results["total_points"],
                "max_points": section3_results["max_points"],
                "percentage": (section3_results["total_points"] / section3_results["max_points"]) * 100
            }
        },
        "total_points": total_points,
        "max_points": max_points,
        "overall_score": overall_score,
        "pass_fail": "PASS" if overall_score >= 75 else "FAIL"
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {overall_score:.2f}% - {results['pass_fail']}")

if __name__ == "__main__":
    main()