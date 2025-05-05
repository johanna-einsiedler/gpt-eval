#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def is_close_enough(candidate_value, correct_value, field_name):
    if isinstance(candidate_value, str) or isinstance(correct_value, str):
        return candidate_value == correct_value
    
    # Special margin of error for correlation calculations
    if field_name == "tenure_cost_correlation":
        return abs(candidate_value - correct_value) <= 0.02
    
    # Default margin of error for numerical values
    return abs(candidate_value - correct_value) <= 0.05

def evaluate_submission(submission, answer_key):
    results = {
        "task1": {},
        "task2": {},
        "task3": {},
        "section_scores": {},
        "critical_analysis": {},
        "overall_score": 0
    }
    
    total_points = 0
    earned_points = 0
    
    # Track correct answers per section
    section_correct = {"task1": 0, "task2": 0, "task3": 0}
    
    # Critical analysis requirements
    critical_fields = {
        "task1": ["highest_cost_benefit"],
        "task2": ["lowest_cost_scenario"],
        "task3": ["group_a_compensation_ratio", "group_b_compensation_ratio", "group_c_compensation_ratio"]
    }
    critical_correct = {field: False for section in critical_fields for field in critical_fields[section]}
    
    # Evaluate each task
    for task in ["task1", "task2", "task3"]:
        if task in submission and task in answer_key:
            for field, correct_value in answer_key[task].items():
                total_points += 1
                
                if field in submission[task]:
                    candidate_value = submission[task][field]
                    is_correct = is_close_enough(candidate_value, correct_value, field)
                    
                    results[task][field] = {
                        "candidate_answer": candidate_value,
                        "correct_answer": correct_value,
                        "is_correct": is_correct
                    }
                    
                    if is_correct:
                        earned_points += 1
                        section_correct[task] += 1
                        
                        # Check if this is a critical field
                        for crit_section, crit_fields in critical_fields.items():
                            if task == crit_section and field in crit_fields:
                                critical_correct[field] = True
                else:
                    results[task][field] = {
                        "candidate_answer": None,
                        "correct_answer": correct_value,
                        "is_correct": False,
                        "error": "Field missing in submission"
                    }
    
    # Calculate section scores
    for task, correct_count in section_correct.items():
        total_in_section = len(answer_key[task])
        results["section_scores"][task] = {
            "correct": correct_count,
            "total": total_in_section,
            "percentage": round(correct_count / total_in_section * 100, 2)
        }
    
    # Evaluate critical analysis requirements
    results["critical_analysis"]["highest_cost_benefit"] = critical_correct["highest_cost_benefit"]
    results["critical_analysis"]["lowest_cost_scenario"] = critical_correct["lowest_cost_scenario"]
    
    # Check if at least one compensation ratio is correct
    comp_ratio_correct = any([
        critical_correct["group_a_compensation_ratio"],
        critical_correct["group_b_compensation_ratio"],
        critical_correct["group_c_compensation_ratio"]
    ])
    results["critical_analysis"]["compensation_ratio"] = comp_ratio_correct
    
    # Calculate overall score
    overall_percentage = round(earned_points / total_points * 100, 2)
    results["overall_score"] = overall_percentage
    
    # Determine if candidate passed
    min_score_requirement = earned_points >= 12  # At least 12 out of 17 correct (70%)
    min_section_requirement = all(count >= 2 for count in section_correct.values())  # At least 2 correct in each section
    critical_requirement = (
        critical_correct["highest_cost_benefit"] and 
        critical_correct["lowest_cost_scenario"] and 
        comp_ratio_correct
    )
    
    results["passed"] = min_score_requirement and min_section_requirement and critical_requirement
    results["pass_criteria"] = {
        "min_score_requirement": min_score_requirement,
        "min_section_requirement": min_section_requirement,
        "critical_requirement": critical_requirement
    }
    
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
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()