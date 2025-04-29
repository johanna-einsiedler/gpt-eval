#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, List, Union

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def save_json_file(data: Dict[str, Any], filename: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        sys.exit(1)

def is_close(val1: float, val2: float, tolerance: float = 0.05) -> bool:
    """Check if two float values are close within a tolerance."""
    return abs(val1 - val2) <= tolerance

def evaluate_selection_rates(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the selection rates calculation."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    categories = ["gender", "race_ethnicity"]
    groups = {
        "gender": ["male", "female"],
        "race_ethnicity": ["white", "black", "hispanic", "asian"]
    }
    
    points_per_group = results["max_score"] / sum(len(groups[cat]) for cat in categories)
    
    for category in categories:
        results["details"][category] = {}
        for group in groups[category]:
            submission_value = submission["task1"]["selection_rates"][category].get(group, 0)
            key_value = answer_key["task1"]["selection_rates"][category].get(group, 0)
            
            is_correct = is_close(submission_value, key_value)
            points = points_per_group if is_correct else 0
            results["score"] += points
            
            results["details"][category][group] = {
                "submission": submission_value,
                "correct": key_value,
                "is_correct": is_correct,
                "points": points
            }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_adverse_impact(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the adverse impact identification."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    categories = ["gender", "race_ethnicity"]
    fields = ["group_with_lowest_rate", "adverse_impact_ratio", "adverse_impact_exists"]
    
    points_per_category = results["max_score"] / len(categories)
    
    for category in categories:
        results["details"][category] = {}
        category_score = 0
        points_per_field = points_per_category / len(fields)
        
        for field in fields:
            submission_value = submission["task1"]["adverse_impact_identified"][category].get(field)
            key_value = answer_key["task1"]["adverse_impact_identified"][category].get(field)
            
            is_correct = False
            if field == "group_with_lowest_rate":
                is_correct = submission_value == key_value
            elif field == "adverse_impact_ratio":
                is_correct = is_close(submission_value, key_value)
            else:  # adverse_impact_exists
                is_correct = submission_value == key_value
            
            points = points_per_field if is_correct else 0
            category_score += points
            
            results["details"][category][field] = {
                "submission": submission_value,
                "correct": key_value,
                "is_correct": is_correct,
                "points": points
            }
        
        results["score"] += category_score
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_qualified_hire_percentages(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the qualified applicant hire percentages."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    categories = ["gender", "race_ethnicity"]
    groups = {
        "gender": ["male", "female"],
        "race_ethnicity": ["white", "black", "hispanic", "asian"]
    }
    
    points_per_group = results["max_score"] / sum(len(groups[cat]) for cat in categories)
    
    for category in categories:
        results["details"][category] = {}
        for group in groups[category]:
            submission_value = submission["task1"]["qualified_applicant_hire_percentages"][category].get(group, 0)
            key_value = answer_key["task1"]["qualified_applicant_hire_percentages"][category].get(group, 0)
            
            is_correct = is_close(submission_value, key_value)
            points = points_per_group if is_correct else 0
            results["score"] += points
            
            results["details"][category][group] = {
                "submission": submission_value,
                "correct": key_value,
                "is_correct": is_correct,
                "points": points
            }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_policy_sections(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the policy section identification."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    areas = ["recruitment", "hiring", "promotion"]
    points_per_area = results["max_score"] / len(areas)
    
    for area in areas:
        submission_sections = set(submission["task2"]["policy_sections"].get(area, []))
        key_sections = set(answer_key["task2"]["policy_sections"].get(area, []))
        
        # Calculate correctness based on overlap
        if submission_sections and key_sections:
            overlap = submission_sections.intersection(key_sections)
            correctness = len(overlap) / max(len(submission_sections), len(key_sections))
        else:
            correctness = 0 if submission_sections or key_sections else 1
        
        points = points_per_area * correctness
        results["score"] += points
        
        results["details"][area] = {
            "submission": list(submission_sections),
            "correct": list(key_sections),
            "correctness": correctness,
            "points": points
        }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_policy_implementation(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the policy implementation assessment."""
    results = {"score": 0, "max_score": 20, "details": {}}
    
    # Evaluate policy_followed (5 points)
    submission_followed = submission["task2"]["policy_implementation_assessment"].get("policy_followed")
    key_followed = answer_key["task2"]["policy_implementation_assessment"].get("policy_followed")
    policy_followed_correct = submission_followed == key_followed
    policy_followed_points = 5 if policy_followed_correct else 0
    results["score"] += policy_followed_points
    
    results["details"]["policy_followed"] = {
        "submission": submission_followed,
        "correct": key_followed,
        "is_correct": policy_followed_correct,
        "points": policy_followed_points
    }
    
    # Evaluate justification (5 points)
    # This is subjective, so we'll check for key phrases
    submission_justification = submission["task2"]["policy_implementation_assessment"].get("justification", "")
    key_justification = answer_key["task2"]["policy_implementation_assessment"].get("justification", "")
    
    key_phrases = ["disparate impact", "80%", "selection rate"]
    phrase_points = 5 / len(key_phrases)
    justification_points = 0
    
    for phrase in key_phrases:
        if phrase.lower() in submission_justification.lower():
            justification_points += phrase_points
    
    results["score"] += justification_points
    
    results["details"]["justification"] = {
        "submission": submission_justification,
        "correct": key_justification,
        "points": justification_points,
        "max_points": 5
    }
    
    # Evaluate specific_violations (5 points)
    submission_violations = submission["task2"]["policy_implementation_assessment"].get("specific_violations", [])
    key_violations = answer_key["task2"]["policy_implementation_assessment"].get("specific_violations", [])
    
    violation_count = min(len(submission_violations), len(key_violations))
    max_violation_count = max(len(key_violations), 1)  # Avoid division by zero
    violation_points = 5 * (violation_count / max_violation_count)
    
    results["score"] += violation_points
    
    results["details"]["specific_violations"] = {
        "submission": submission_violations,
        "correct": key_violations,
        "points": violation_points,
        "max_points": 5
    }
    
    # Evaluate recommended_actions (5 points)
    submission_actions = submission["task2"]["policy_implementation_assessment"].get("recommended_actions", [])
    key_actions = answer_key["task2"]["policy_implementation_assessment"].get("recommended_actions", [])
    
    action_count = min(len(submission_actions), len(key_actions))
    max_action_count = max(len(key_actions), 1)  # Avoid division by zero
    action_points = 5 * (action_count / max_action_count)
    
    results["score"] += action_points
    
    results["details"]["recommended_actions"] = {
        "submission": submission_actions,
        "correct": key_actions,
        "points": action_points,
        "max_points": 5
    }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_complaints_by_department(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the complaints by department counts."""
    results = {"score": 0, "max_score": 8, "details": {}}
    
    departments = ["sales", "it", "hr", "finance"]
    points_per_dept = results["max_score"] / len(departments)
    
    for dept in departments:
        submission_count = submission["task3"]["complaints_by_department"].get(dept, 0)
        key_count = answer_key["task3"]["complaints_by_department"].get(dept, 0)
        
        is_correct = submission_count == key_count
        points = points_per_dept if is_correct else 0
        results["score"] += points
        
        results["details"][dept] = {
            "submission": submission_count,
            "correct": key_count,
            "is_correct": is_correct,
            "points": points
        }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_most_common_complaint(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the most common complaint identification."""
    results = {"score": 0, "max_score": 8, "details": {}}
    
    submission_value = submission["task3"].get("most_common_complaint", "")
    key_value = answer_key["task3"].get("most_common_complaint", "")
    
    is_correct = submission_value == key_value
    points = results["max_score"] if is_correct else 0
    results["score"] = points
    
    results["details"] = {
        "submission": submission_value,
        "correct": key_value,
        "is_correct": is_correct,
        "points": points
    }
    
    return results

def evaluate_average_resolution_time(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the average resolution time calculation."""
    results = {"score": 0, "max_score": 8, "details": {}}
    
    submission_value = submission["task3"].get("average_resolution_time", 0)
    key_value = answer_key["task3"].get("average_resolution_time", 0)
    
    is_correct = is_close(submission_value, key_value)
    points = results["max_score"] if is_correct else 0
    results["score"] = points
    
    results["details"] = {
        "submission": submission_value,
        "correct": key_value,
        "is_correct": is_correct,
        "points": points
    }
    
    return results

def evaluate_disproportionate_departments(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the disproportionate departments identification."""
    results = {"score": 0, "max_score": 8, "details": {}}
    
    submission_depts = set(submission["task3"].get("disproportionate_departments", []))
    key_depts = set(answer_key["task3"].get("disproportionate_departments", []))
    
    # Calculate correctness based on overlap
    if submission_depts and key_depts:
        overlap = submission_depts.intersection(key_depts)
        correctness = len(overlap) / max(len(submission_depts), len(key_depts))
    else:
        correctness = 0 if submission_depts or key_depts else 1
    
    points = results["max_score"] * correctness
    results["score"] = points
    
    results["details"] = {
        "submission": list(submission_depts),
        "correct": list(key_depts),
        "correctness": correctness,
        "points": points
    }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_complaint_trends(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the complaint trends analysis."""
    results = {"score": 0, "max_score": 8, "details": {}}
    
    # This is somewhat subjective, so we'll check for key elements
    submission_increasing = set(submission["task3"]["complaint_trends"].get("increasing_types", []))
    key_increasing = set(answer_key["task3"]["complaint_trends"].get("increasing_types", []))
    
    submission_decreasing = set(submission["task3"]["complaint_trends"].get("decreasing_types", []))
    key_decreasing = set(answer_key["task3"]["complaint_trends"].get("decreasing_types", []))
    
    submission_seasonal = submission["task3"]["complaint_trends"].get("seasonal_patterns", "")
    key_seasonal = answer_key["task3"]["complaint_trends"].get("seasonal_patterns", "")
    
    # Check increasing types (2 points)
    if submission_increasing == key_increasing:
        increasing_points = 2
    else:
        increasing_points = 0
    
    # Check decreasing types (2 points)
    if submission_decreasing == key_decreasing:
        decreasing_points = 2
    else:
        decreasing_points = 0
    
    # Check seasonal patterns (4 points)
    # Look for key phrases like "no clear seasonal patterns"
    if "no" in submission_seasonal.lower() and "pattern" in submission_seasonal.lower():
        seasonal_points = 4
    else:
        seasonal_points = 0
    
    results["score"] = increasing_points + decreasing_points + seasonal_points
    
    results["details"] = {
        "increasing_types": {
            "submission": list(submission_increasing),
            "correct": list(key_increasing),
            "is_correct": submission_increasing == key_increasing,
            "points": increasing_points
        },
        "decreasing_types": {
            "submission": list(submission_decreasing),
            "correct": list(key_decreasing),
            "is_correct": submission_decreasing == key_decreasing,
            "points": decreasing_points
        },
        "seasonal_patterns": {
            "submission": submission_seasonal,
            "correct": key_seasonal,
            "points": seasonal_points
        }
    }
    
    return results

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_name": submission.get("candidate_name", ""),
        "date": submission.get("date", ""),
        "task1": {
            "selection_rates": evaluate_selection_rates(submission, answer_key),
            "adverse_impact": evaluate_adverse_impact(submission, answer_key),
            "qualified_hire_percentages": evaluate_qualified_hire_percentages(submission, answer_key)
        },
        "task2": {
            "policy_sections": evaluate_policy_sections(submission, answer_key),
            "policy_implementation": evaluate_policy_implementation(submission, answer_key)
        },
        "task3": {
            "complaints_by_department": evaluate_complaints_by_department(submission, answer_key),
            "most_common_complaint": evaluate_most_common_complaint(submission, answer_key),
            "average_resolution_time": evaluate_average_resolution_time(submission, answer_key),
            "disproportionate_departments": evaluate_disproportionate_departments(submission, answer_key),
            "complaint_trends": evaluate_complaint_trends(submission, answer_key)
        }
    }
    
    # Calculate task scores
    task1_score = (
        results["task1"]["selection_rates"]["score"] +
        results["task1"]["adverse_impact"]["score"] +
        results["task1"]["qualified_hire_percentages"]["score"]
    )
    task1_max = (
        results["task1"]["selection_rates"]["max_score"] +
        results["task1"]["adverse_impact"]["max_score"] +
        results["task1"]["qualified_hire_percentages"]["max_score"]
    )
    
    task2_score = (
        results["task2"]["policy_sections"]["score"] +
        results["task2"]["policy_implementation"]["score"]
    )
    task2_max = (
        results["task2"]["policy_sections"]["max_score"] +
        results["task2"]["policy_implementation"]["max_score"]
    )
    
    task3_score = (
        results["task3"]["complaints_by_department"]["score"] +
        results["task3"]["most_common_complaint"]["score"] +
        results["task3"]["average_resolution_time"]["score"] +
        results["task3"]["disproportionate_departments"]["score"] +
        results["task3"]["complaint_trends"]["score"]
    )
    task3_max = (
        results["task3"]["complaints_by_department"]["max_score"] +
        results["task3"]["most_common_complaint"]["max_score"] +
        results["task3"]["average_resolution_time"]["max_score"] +
        results["task3"]["disproportionate_departments"]["max_score"] +
        results["task3"]["complaint_trends"]["max_score"]
    )
    
    total_score = task1_score + task2_score + task3_score
    total_max = task1_max + task2_max + task3_max
    
    # Add summary scores
    results["summary"] = {
        "task1": {
            "score": round(task1_score, 2),
            "max_score": task1_max,
            "percentage": round((task1_score / task1_max) * 100, 2)
        },
        "task2": {
            "score": round(task2_score, 2),
            "max_score": task2_max,
            "percentage": round((task2_score / task2_max) * 100, 2)
        },
        "task3": {
            "score": round(task3_score, 2),
            "max_score": task3_max,
            "percentage": round((task3_score / task3_max) * 100, 2)
        },
        "total": {
            "score": round(total_score, 2),
            "max_score": total_max,
            "percentage": round((total_score / total_max) * 100, 2)
        }
    }
    
    # Check if candidate passed based on criteria
    passed_task1 = task1_score >= 20
    passed_task2 = task2_score >= 20
    passed_task3 = task3_score >= 25
    passed_overall = total_score >= 70
    
    # Check critical elements
    adverse_impact_gender = submission["task1"]["adverse_impact_identified"]["gender"]["adverse_impact_exists"]
    adverse_impact_race = submission["task1"]["adverse_impact_identified"]["race_ethnicity"]["adverse_impact_exists"]
    policy_followed = not submission["task2"]["policy_implementation_assessment"]["policy_followed"]
    most_common_complaint_correct = (
        submission["task3"]["most_common_complaint"] == 
        answer_key["task3"]["most_common_complaint"]
    )
    
    critical_elements_passed = (
        adverse_impact_gender and 
        adverse_impact_race and 
        policy_followed and 
        most_common_complaint_correct
    )
    
    results["summary"]["passed"] = (
        passed_task1 and 
        passed_task2 and 
        passed_task3 and 
        passed_overall and 
        critical_elements_passed
    )
    
    results["summary"]["critical_elements"] = {
        "adverse_impact_gender": adverse_impact_gender,
        "adverse_impact_race": adverse_impact_race,
        "policy_not_followed": policy_followed,
        "most_common_complaint": most_common_complaint_correct,
        "all_critical_passed": critical_elements_passed
    }
    
    # Add overall score as a percentage
    results["overall_score"] = results["summary"]["total"]["percentage"]
    
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
    
    save_json_file(results, "test_results.json")
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {'Yes' if results['summary']['passed'] else 'No'}")

if __name__ == "__main__":
    main()