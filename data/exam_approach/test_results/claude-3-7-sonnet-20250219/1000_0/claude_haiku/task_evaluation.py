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

def calculate_percentage_difference(candidate_value, answer_value):
    """Calculate percentage difference between candidate and answer values"""
    if answer_value == 0:
        return 100 if candidate_value == 0 else 0
    return abs(candidate_value - answer_value) / abs(answer_value) * 100

def evaluate_avg_monthly_change(candidate_data, answer_data):
    """Evaluate the average monthly change section"""
    score = 0
    max_score = 10
    details = {}
    
    candidate_values = candidate_data.get("avg_monthly_change", {})
    answer_values = answer_data.get("avg_monthly_change", {})
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing avg_monthly_change data"}
    
    for dept, answer_value in answer_values.items():
        candidate_value = candidate_values.get(dept, 0)
        diff_percentage = calculate_percentage_difference(candidate_value, answer_value)
        
        # Score based on accuracy
        dept_score = 0
        if diff_percentage <= 2:
            dept_score = 2  # Full points
        elif diff_percentage <= 5:
            dept_score = 1.5  # 75% points
        elif diff_percentage <= 10:
            dept_score = 1  # 50% points
        elif diff_percentage <= 20:
            dept_score = 0.5  # 25% points
        
        score += dept_score
        details[dept] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "difference_percentage": round(diff_percentage, 2),
            "points": dept_score,
            "max_points": 2
        }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_highest_turnover(candidate_data, answer_data):
    """Evaluate the highest turnover departments section"""
    score = 0
    max_score = 10
    details = {}
    
    candidate_values = candidate_data.get("highest_turnover_departments", [])
    answer_values = answer_data.get("highest_turnover_departments", [])
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing highest_turnover_departments data"}
    
    # Check if the correct departments are identified (regardless of order)
    correct_depts = set(answer_values)
    candidate_depts = set(candidate_values[:3])  # Only consider first 3
    
    # Calculate how many departments are correctly identified
    correct_count = len(correct_depts.intersection(candidate_depts))
    
    # Check if the order is correct for the identified departments
    order_correct = 0
    for i in range(min(len(candidate_values), len(answer_values))):
        if i < len(candidate_values) and candidate_values[i] == answer_values[i]:
            order_correct += 1
    
    # Score: 6 points for correct departments, 4 points for correct order
    dept_score = (correct_count / 3) * 6
    order_score = (order_correct / 3) * 4
    score = dept_score + order_score
    
    details = {
        "correct_departments": correct_count,
        "correct_order": order_correct,
        "candidate_values": candidate_values,
        "correct_values": answer_values,
        "department_points": dept_score,
        "order_points": order_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_current_gaps(candidate_data, answer_data):
    """Evaluate the current gaps section"""
    score = 0
    max_score = 7.5
    details = {}
    
    candidate_values = candidate_data.get("current_gaps", {})
    answer_values = answer_data.get("current_gaps", {})
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing current_gaps data"}
    
    for dept, answer_value in answer_values.items():
        candidate_value = candidate_values.get(dept, 0)
        
        # For gaps, we want exact matches since these are simple calculations
        dept_score = 0
        if candidate_value == answer_value:
            dept_score = 1.5  # Full points
        else:
            dept_score = 0  # No points for incorrect gap values
        
        score += dept_score
        details[dept] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "points": dept_score,
            "max_points": 1.5
        }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_largest_percentage_gap(candidate_data, answer_data):
    """Evaluate the largest percentage gap section"""
    score = 0
    max_score = 7.5
    
    candidate_value = candidate_data.get("largest_percentage_gap", "")
    answer_value = answer_data.get("largest_percentage_gap", "")
    
    if not candidate_value:
        return {"score": 0, "max_score": max_score, "details": "Missing largest_percentage_gap data"}
    
    # This is a direct comparison - either correct or incorrect
    if candidate_value == answer_value:
        score = max_score
    
    details = {
        "candidate_value": candidate_value,
        "correct_value": answer_value,
        "points": score,
        "max_points": max_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_end_of_period_headcount(candidate_data, answer_data):
    """Evaluate the end of period headcount section"""
    score = 0
    max_score = 10
    details = {}
    
    candidate_values = candidate_data.get("end_of_period_headcount", {})
    answer_values = answer_data.get("end_of_period_headcount", {})
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing end_of_period_headcount data"}
    
    for dept, answer_value in answer_values.items():
        candidate_value = candidate_values.get(dept, 0)
        diff_percentage = calculate_percentage_difference(candidate_value, answer_value)
        
        # Score based on accuracy
        dept_score = 0
        if diff_percentage <= 2:
            dept_score = 2  # Full points
        elif diff_percentage <= 5:
            dept_score = 1.5  # 75% points
        elif diff_percentage <= 10:
            dept_score = 1  # 50% points
        elif diff_percentage <= 15:
            dept_score = 0.5  # 25% points
        
        score += dept_score
        details[dept] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "difference_percentage": round(diff_percentage, 2),
            "points": dept_score,
            "max_points": 2
        }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_total_new_hires(candidate_data, answer_data):
    """Evaluate the total new hires needed section"""
    score = 0
    max_score = 7.5
    details = {}
    
    candidate_values = candidate_data.get("total_new_hires_needed", {})
    answer_values = answer_data.get("total_new_hires_needed", {})
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing total_new_hires_needed data"}
    
    for dept, answer_value in answer_values.items():
        candidate_value = candidate_values.get(dept, 0)
        diff_percentage = calculate_percentage_difference(candidate_value, answer_value)
        
        # Score based on accuracy
        dept_score = 0
        if diff_percentage <= 2:
            dept_score = 1.5  # Full points
        elif diff_percentage <= 5:
            dept_score = 1.125  # 75% points
        elif diff_percentage <= 10:
            dept_score = 0.75  # 50% points
        elif diff_percentage <= 15:
            dept_score = 0.375  # 25% points
        
        score += dept_score
        details[dept] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "difference_percentage": round(diff_percentage, 2),
            "points": dept_score,
            "max_points": 1.5
        }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_month_with_highest_hiring(candidate_data, answer_data):
    """Evaluate the month with highest hiring need section"""
    score = 0
    max_score = 2.5
    
    candidate_value = candidate_data.get("month_with_highest_hiring_need", "")
    answer_value = answer_data.get("month_with_highest_hiring_need", "")
    
    if not candidate_value:
        return {"score": 0, "max_score": max_score, "details": "Missing month_with_highest_hiring_need data"}
    
    # This is a direct comparison - either correct or incorrect
    if candidate_value.lower() == answer_value.lower():
        score = max_score
    
    details = {
        "candidate_value": candidate_value,
        "correct_value": answer_value,
        "points": score,
        "max_points": max_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_total_projected_headcount(candidate_data, answer_data):
    """Evaluate the total projected headcount section"""
    score = 0
    max_score = 5
    
    candidate_value = candidate_data.get("total_projected_headcount", 0)
    answer_value = answer_data.get("total_projected_headcount", 0)
    
    if candidate_value == 0:
        return {"score": 0, "max_score": max_score, "details": "Missing total_projected_headcount data"}
    
    diff_percentage = calculate_percentage_difference(candidate_value, answer_value)
    
    # Score based on accuracy
    if diff_percentage <= 2:
        score = 5  # Full points
    elif diff_percentage <= 5:
        score = 3.75  # 75% points
    elif diff_percentage <= 10:
        score = 2.5  # 50% points
    elif diff_percentage <= 15:
        score = 1.25  # 25% points
    
    details = {
        "candidate_value": candidate_value,
        "correct_value": answer_value,
        "difference_percentage": round(diff_percentage, 2),
        "points": score,
        "max_points": max_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_workforce_percentage_change(candidate_data, answer_data):
    """Evaluate the total workforce percentage change section"""
    score = 0
    max_score = 5
    
    candidate_value = candidate_data.get("total_workforce_percentage_change", 0)
    answer_value = answer_data.get("total_workforce_percentage_change", 0)
    
    if candidate_value == 0:
        return {"score": 0, "max_score": max_score, "details": "Missing total_workforce_percentage_change data"}
    
    diff_percentage = calculate_percentage_difference(candidate_value, answer_value)
    
    # Score based on accuracy
    if diff_percentage <= 2:
        score = 5  # Full points
    elif diff_percentage <= 5:
        score = 3.75  # 75% points
    elif diff_percentage <= 10:
        score = 2.5  # 50% points
    elif diff_percentage <= 15:
        score = 1.25  # 25% points
    
    details = {
        "candidate_value": candidate_value,
        "correct_value": answer_value,
        "difference_percentage": round(diff_percentage, 2),
        "points": score,
        "max_points": max_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_highest_growth_departments(candidate_data, answer_data):
    """Evaluate the highest growth departments section"""
    score = 0
    max_score = 5
    details = {}
    
    candidate_values = candidate_data.get("highest_growth_departments", [])
    answer_values = answer_data.get("highest_growth_departments", [])
    
    if not candidate_values:
        return {"score": 0, "max_score": max_score, "details": "Missing highest_growth_departments data"}
    
    # Check if the correct departments are identified (regardless of order)
    correct_depts = set(answer_values)
    candidate_depts = set(candidate_values[:3])  # Only consider first 3
    
    # Calculate how many departments are correctly identified
    correct_count = len(correct_depts.intersection(candidate_depts))
    
    # Check if the order is correct for the identified departments
    order_correct = 0
    for i in range(min(len(candidate_values), len(answer_values))):
        if i < len(candidate_values) and candidate_values[i] == answer_values[i]:
            order_correct += 1
    
    # Score: 3 points for correct departments, 2 points for correct order
    dept_score = (correct_count / 3) * 3
    order_score = (order_correct / 3) * 2
    score = dept_score + order_score
    
    details = {
        "correct_departments": correct_count,
        "correct_order": order_correct,
        "candidate_values": candidate_values,
        "correct_values": answer_values,
        "department_points": dept_score,
        "order_points": order_score
    }
    
    return {"score": score, "max_score": max_score, "details": details}

def evaluate_submission(candidate_data, answer_data):
    """Evaluate the entire submission"""
    results = {
        "historical_analysis": {
            "avg_monthly_change": evaluate_avg_monthly_change(
                candidate_data.get("historical_analysis", {}), 
                answer_data.get("historical_analysis", {})
            ),
            "highest_turnover_departments": evaluate_highest_turnover(
                candidate_data.get("historical_analysis", {}), 
                answer_data.get("historical_analysis", {})
            )
        },
        "gap_analysis": {
            "current_gaps": evaluate_current_gaps(
                candidate_data.get("gap_analysis", {}), 
                answer_data.get("gap_analysis", {})
            ),
            "largest_percentage_gap": evaluate_largest_percentage_gap(
                candidate_data.get("gap_analysis", {}), 
                answer_data.get("gap_analysis", {})
            )
        },
        "forecast": {
            "end_of_period_headcount": evaluate_end_of_period_headcount(
                candidate_data.get("forecast", {}), 
                answer_data.get("forecast", {})
            ),
            "total_new_hires_needed": evaluate_total_new_hires(
                candidate_data.get("forecast", {}), 
                answer_data.get("forecast", {})
            ),
            "month_with_highest_hiring_need": evaluate_month_with_highest_hiring(
                candidate_data.get("forecast", {}), 
                answer_data.get("forecast", {})
            )
        },
        "resource_planning": {
            "total_projected_headcount": evaluate_total_projected_headcount(
                candidate_data.get("resource_planning", {}), 
                answer_data.get("resource_planning", {})
            ),
            "total_workforce_percentage_change": evaluate_workforce_percentage_change(
                candidate_data.get("resource_planning", {}), 
                answer_data.get("resource_planning", {})
            ),
            "highest_growth_departments": evaluate_highest_growth_departments(
                candidate_data.get("resource_planning", {}), 
                answer_data.get("resource_planning", {})
            )
        }
    }
    
    # Calculate section scores
    section_scores = {
        "historical_analysis": {
            "score": results["historical_analysis"]["avg_monthly_change"]["score"] + 
                     results["historical_analysis"]["highest_turnover_departments"]["score"],
            "max_score": results["historical_analysis"]["avg_monthly_change"]["max_score"] + 
                         results["historical_analysis"]["highest_turnover_departments"]["max_score"]
        },
        "gap_analysis": {
            "score": results["gap_analysis"]["current_gaps"]["score"] + 
                     results["gap_analysis"]["largest_percentage_gap"]["score"],
            "max_score": results["gap_analysis"]["current_gaps"]["max_score"] + 
                         results["gap_analysis"]["largest_percentage_gap"]["max_score"]
        },
        "forecast": {
            "score": results["forecast"]["end_of_period_headcount"]["score"] + 
                     results["forecast"]["total_new_hires_needed"]["score"] + 
                     results["forecast"]["month_with_highest_hiring_need"]["score"],
            "max_score": results["forecast"]["end_of_period_headcount"]["max_score"] + 
                         results["forecast"]["total_new_hires_needed"]["max_score"] + 
                         results["forecast"]["month_with_highest_hiring_need"]["max_score"]
        },
        "resource_planning": {
            "score": results["resource_planning"]["total_projected_headcount"]["score"] + 
                     results["resource_planning"]["total_workforce_percentage_change"]["score"] + 
                     results["resource_planning"]["highest_growth_departments"]["score"],
            "max_score": results["resource_planning"]["total_projected_headcount"]["max_score"] + 
                         results["resource_planning"]["total_workforce_percentage_change"]["max_score"] + 
                         results["resource_planning"]["highest_growth_departments"]["max_score"]
        }
    }
    
    # Calculate overall score
    total_score = sum(section["score"] for section in section_scores.values())
    total_max_score = sum(section["max_score"] for section in section_scores.values())
    overall_score = (total_score / total_max_score) * 100
    
    # Check if any section is below 50%
    section_percentages = {
        section: (scores["score"] / scores["max_score"]) * 100 
        for section, scores in section_scores.items()
    }
    
    any_section_below_threshold = any(percentage < 50 for percentage in section_percentages.values())
    
    # Check automatic failing conditions
    automatic_fail = False
    fail_reasons = []
    
    # Check for missing sections
    required_sections = ["historical_analysis", "gap_analysis", "forecast", "resource_planning"]
    for section in required_sections:
        if section not in candidate_data:
            automatic_fail = True
            fail_reasons.append(f"Missing required section: {section}")
    
    # Check if total projected headcount is off by more than 15%
    if "resource_planning" in candidate_data and "total_projected_headcount" in candidate_data["resource_planning"]:
        candidate_headcount = candidate_data["resource_planning"]["total_projected_headcount"]
        answer_headcount = answer_data["resource_planning"]["total_projected_headcount"]
        headcount_diff = calculate_percentage_difference(candidate_headcount, answer_headcount)
        if headcount_diff > 15:
            automatic_fail = True
            fail_reasons.append(f"Total projected headcount off by more than 15% ({headcount_diff:.2f}%)")
    
    # Final evaluation
    final_result = {
        "detailed_results": results,
        "section_scores": section_scores,
        "section_percentages": {k: round(v, 2) for k, v in section_percentages.items()},
        "total_score": total_score,
        "total_max_score": total_max_score,
        "overall_score": round(overall_score, 2),
        "any_section_below_threshold": any_section_below_threshold,
        "automatic_fail": automatic_fail,
        "fail_reasons": fail_reasons,
        "candidate_id": candidate_data.get("candidate_id", "Unknown")
    }
    
    return final_result

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate_data = load_json_file(submission_file)
    answer_data = load_json_file(answer_key_file)
    
    results = evaluate_submission(candidate_data, answer_data)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    
    if results["automatic_fail"]:
        print("AUTOMATIC FAIL due to:")
        for reason in results["fail_reasons"]:
            print(f"- {reason}")
    elif results["any_section_below_threshold"]:
        print("FAIL: One or more sections scored below 50%")
    elif results["overall_score"] < 70:
        print("FAIL: Overall score below 70%")
    else:
        print("PASS")

if __name__ == "__main__":
    main()