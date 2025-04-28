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

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Sampling Location Identification."""
    score = 0
    results = {}
    
    for i in range(1, 6):
        key = f"location{i}"
        correct = answer_key["section1"][key]
        submitted = submission["section1"].get(key, "")
        is_correct = submitted == correct
        
        if is_correct:
            score += 5
            
        results[key] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": is_correct,
            "points_earned": 5 if is_correct else 0,
            "points_possible": 5
        }
    
    return {
        "score": score,
        "max_score": 25,
        "details": results
    }

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Sampling Method Selection."""
    score = 0
    results = {}
    
    for i in range(1, 6):
        key = f"method{i}"
        correct = answer_key["section2"][key]
        submitted = submission["section2"].get(key, "")
        is_correct = submitted == correct
        
        if is_correct:
            score += 5
            
        results[key] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": is_correct,
            "points_earned": 5 if is_correct else 0,
            "points_possible": 5
        }
    
    return {
        "score": score,
        "max_score": 25,
        "details": results
    }

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Sample Container and Preservation Selection."""
    score = 0
    results = {}
    
    for i in range(1, 6):
        key = f"parameter{i}"
        correct_container = answer_key["section3"][key]["container"]
        correct_preservation = answer_key["section3"][key]["preservation"]
        
        submitted_container = submission["section3"].get(key, {}).get("container", "")
        submitted_preservation = submission["section3"].get(key, {}).get("preservation", "")
        
        container_correct = submitted_container == correct_container
        preservation_correct = submitted_preservation == correct_preservation
        
        container_points = 2.5 if container_correct else 0
        preservation_points = 2.5 if preservation_correct else 0
        total_points = container_points + preservation_points
        
        score += total_points
            
        results[key] = {
            "submitted": {
                "container": submitted_container,
                "preservation": submitted_preservation
            },
            "correct": {
                "container": correct_container,
                "preservation": correct_preservation
            },
            "is_correct": {
                "container": container_correct,
                "preservation": preservation_correct
            },
            "points_earned": total_points,
            "points_possible": 5
        }
    
    return {
        "score": score,
        "max_score": 25,
        "details": results
    }

def evaluate_section4(submission, answer_key):
    """Evaluate Section 4: Sampling Protocol Application."""
    score = 0
    results = {}
    
    # Questions 1-4 (5 points each)
    for i in range(1, 5):
        key = f"question{i}"
        correct = answer_key["section4"][key]
        submitted = submission["section4"].get(key, "")
        is_correct = submitted == correct
        
        if is_correct:
            score += 5
            
        results[key] = {
            "submitted": submitted,
            "correct": correct,
            "is_correct": is_correct,
            "points_earned": 5 if is_correct else 0,
            "points_possible": 5
        }
    
    # Question 5 (array of answers, 1 point per correct item, max 5 points)
    key = "question5"
    correct_set = set(answer_key["section4"][key])
    submitted_list = submission["section4"].get(key, [])
    submitted_set = set(submitted_list)
    
    # Calculate points for question 5
    correct_items = submitted_set.intersection(correct_set)
    incorrect_items = submitted_set - correct_set
    missing_items = correct_set - submitted_set
    
    q5_points = min(len(correct_items), 5)
    score += q5_points
    
    results[key] = {
        "submitted": submitted_list,
        "correct": answer_key["section4"][key],
        "correct_items": list(correct_items),
        "incorrect_items": list(incorrect_items),
        "missing_items": list(missing_items),
        "points_earned": q5_points,
        "points_possible": 5
    }
    
    return {
        "score": score,
        "max_score": 25,
        "details": results
    }

def check_automatic_failure(submission, answer_key, section_scores):
    """Check for automatic failure conditions."""
    failures = []
    
    # Check for section scores below 15 points (60%)
    for section, data in section_scores.items():
        if data["score"] < 15:
            failures.append(f"{section} score below 60% (scored {data['score']} out of 25)")
    
    # Critical error: Selecting acid preservation for cyanide samples
    cyanide_preservation = submission.get("section3", {}).get("parameter5", {}).get("preservation", "")
    if cyanide_preservation in ["2", "3"]:  # HNO₃ or H₂SO₄
        failures.append("Critical safety error: Selected acid preservation for cyanide samples")
    
    # Critical error: Wrong sampling location for NPDES compliance monitoring
    npdes_location = submission.get("section1", {}).get("location1", "")
    if npdes_location != "F":
        failures.append("Critical compliance error: Selected wrong sampling location for NPDES compliance monitoring")
    
    # Critical error: Grab sampling for characterizing average pollutant loading
    pollutant_method = submission.get("section2", {}).get("method2", "")
    if pollutant_method == "A":  # Grab sample
        failures.append("Critical methodology error: Selected grab sampling for characterizing average pollutant loading")
    
    return failures

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    section_scores = {
        "section1": evaluate_section1(submission, answer_key),
        "section2": evaluate_section2(submission, answer_key),
        "section3": evaluate_section3(submission, answer_key),
        "section4": evaluate_section4(submission, answer_key)
    }
    
    # Calculate total score
    total_score = sum(section["score"] for section in section_scores.values())
    max_score = sum(section["max_score"] for section in section_scores.values())
    overall_percentage = (total_score / max_score) * 100
    
    # Check for automatic failure conditions
    failure_reasons = check_automatic_failure(submission, answer_key, section_scores)
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_score,
        "section_scores": section_scores,
        "pass_fail": {
            "passed": overall_percentage >= 70 and not failure_reasons,
            "minimum_required": 70,
            "automatic_failure": bool(failure_reasons),
            "failure_reasons": failure_reasons
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    if failure_reasons:
        print("FAILED: Automatic failure conditions detected:")
        for reason in failure_reasons:
            print(f"- {reason}")
    elif overall_percentage >= 70:
        print("PASSED")
    else:
        print(f"FAILED: Score below 70% minimum")

if __name__ == "__main__":
    main()