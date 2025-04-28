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

def evaluate_department_allocations(submission, answer_key, results):
    points = 0
    details = {}
    
    for dept in answer_key["department_allocations"]:
        expected = answer_key["department_allocations"][dept]
        submitted = submission["department_allocations"][dept]
        
        # Calculate tolerance (5% of expected value)
        tolerance = expected * 0.05
        
        # Check if within tolerance
        if abs(submitted - expected) <= tolerance:
            dept_points = 5
            status = "correct"
        else:
            dept_points = 0
            status = "incorrect"
            
        points += dept_points
        details[dept] = {
            "expected": expected,
            "submitted": submitted,
            "points_earned": dept_points,
            "status": status
        }
    
    # Check for critical error: department allocation constraints
    critical_error = False
    total_budget = submission["total_budget"]
    
    for dept, value in submission["department_allocations"].items():
        dept_percentage = value / total_budget
        if dept_percentage < 0.10 or dept_percentage > 0.40:
            critical_error = True
            details["critical_error"] = f"Department {dept} allocation ({dept_percentage:.2%}) violates 10%-40% constraint"
            break
    
    results["department_allocations"] = {
        "points_possible": 25,
        "points_earned": 0 if critical_error else points,
        "details": details,
        "critical_error": critical_error
    }
    
    return 0 if critical_error else points

def evaluate_training_category_costs(submission, answer_key, results):
    points = 0
    details = {}
    
    # Minimum required percentages for each category
    min_requirements = {
        "technical_skills": 0.25,
        "soft_skills": 0.15,
        "compliance": 0.15,
        "leadership": 0.10,
        "onboarding": 0.05
    }
    
    critical_error = False
    total_budget = submission["total_budget"]
    
    for category in answer_key["training_category_costs"]:
        expected = answer_key["training_category_costs"][category]
        submitted = submission["training_category_costs"][category]
        
        # Calculate tolerance (5% of expected value)
        tolerance = expected * 0.05
        
        # Check if within tolerance
        if abs(submitted - expected) <= tolerance:
            cat_points = 5
            status = "correct"
        else:
            cat_points = 0
            status = "incorrect"
            
        points += cat_points
        details[category] = {
            "expected": expected,
            "submitted": submitted,
            "points_earned": cat_points,
            "status": status
        }
        
        # Check for minimum percentage requirement
        category_percentage = submitted / total_budget
        min_required = min_requirements[category]
        
        if category_percentage < min_required:
            critical_error = True
            details["critical_error"] = f"Category {category} allocation ({category_percentage:.2%}) is below minimum requirement of {min_required:.2%}"
            break
    
    results["training_category_costs"] = {
        "points_possible": 25,
        "points_earned": 0 if critical_error else points,
        "details": details,
        "critical_error": critical_error
    }
    
    return 0 if critical_error else points

def evaluate_per_employee_costs(submission, answer_key, results):
    points = 0
    details = {}
    
    for dept in answer_key["per_employee_costs"]:
        expected = answer_key["per_employee_costs"][dept]
        submitted = submission["per_employee_costs"][dept]
        
        # Tolerance is $10
        tolerance = 10
        
        if abs(submitted - expected) <= tolerance:
            dept_points = 3
            status = "correct"
        else:
            dept_points = 0
            status = "incorrect"
            
        points += dept_points
        details[dept] = {
            "expected": expected,
            "submitted": submitted,
            "points_earned": dept_points,
            "status": status
        }
    
    results["per_employee_costs"] = {
        "points_possible": 15,
        "points_earned": points,
        "details": details
    }
    
    return points

def evaluate_roi_calculations(submission, answer_key, results):
    points = 0
    details = {}
    critical_error = False
    
    for category in answer_key["roi_calculations"]:
        expected = answer_key["roi_calculations"][category]
        submitted = submission["roi_calculations"][category]
        
        # Tolerance is 0.2
        tolerance = 0.2
        
        if abs(submitted - expected) <= tolerance:
            cat_points = 3
            status = "correct"
        else:
            cat_points = 0
            status = "incorrect"
            
        points += cat_points
        details[category] = {
            "expected": expected,
            "submitted": submitted,
            "points_earned": cat_points,
            "status": status
        }
        
        # Check for critical error: non-compliance training with ROI below 1.5
        if category != "compliance" and submitted < 1.5:
            critical_error = True
            details["critical_error"] = f"Category {category} has ROI ({submitted}) below minimum requirement of 1.5"
    
    results["roi_calculations"] = {
        "points_possible": 15,
        "points_earned": 0 if critical_error else points,
        "details": details,
        "critical_error": critical_error
    }
    
    return 0 if critical_error else points

def evaluate_budget_variance(submission, answer_key, results):
    expected = answer_key["budget_variance_percentage"]
    submitted = submission["budget_variance_percentage"]
    
    # Tolerance is 0.001
    tolerance = 0.001
    
    if abs(submitted - expected) <= tolerance:
        points = 5
        status = "correct"
    else:
        points = 0
        status = "incorrect"
    
    results["budget_variance_percentage"] = {
        "points_possible": 5,
        "points_earned": points,
        "details": {
            "expected": expected,
            "submitted": submitted,
            "status": status
        }
    }
    
    return points

def evaluate_cost_saving_opportunities(submission, answer_key, results):
    points = 0
    details = {}
    
    expected_opportunities = answer_key["cost_saving_opportunities"]
    submitted_opportunities = submission["cost_saving_opportunities"]
    
    for i in range(min(len(expected_opportunities), len(submitted_opportunities))):
        expected = expected_opportunities[i]
        submitted = submitted_opportunities[i]
        
        if submitted == expected:
            opp_points = 5
            status = "correct"
        else:
            opp_points = 0
            status = "incorrect"
            
        points += opp_points
        details[f"opportunity_{i+1}"] = {
            "expected": expected,
            "submitted": submitted,
            "points_earned": opp_points,
            "status": status
        }
    
    results["cost_saving_opportunities"] = {
        "points_possible": 15,
        "points_earned": points,
        "details": details
    }
    
    return points

def check_total_budget(submission, answer_key, results):
    if submission["total_budget"] > answer_key["total_budget"]:
        results["critical_errors"] = results.get("critical_errors", [])
        results["critical_errors"].append("Total budget exceeds maximum allowed amount of $175,000")
        return True
    return False

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_points_possible": 100,
        "total_points_earned": 0,
        "passing_threshold": 75,
        "distinction_threshold": 90
    }
    
    # Check for critical error: exceeding total budget
    if check_total_budget(submission, answer_key, results):
        results["total_points_earned"] = 0
        results["result"] = "FAIL (Critical Error)"
        results["overall_score"] = 0
        return results
    
    # Evaluate each section
    points = 0
    
    # Department allocations (25 points)
    points += evaluate_department_allocations(submission, answer_key, results)
    
    # Training category costs (25 points)
    points += evaluate_training_category_costs(submission, answer_key, results)
    
    # Per-employee costs (15 points)
    points += evaluate_per_employee_costs(submission, answer_key, results)
    
    # ROI calculations (15 points)
    points += evaluate_roi_calculations(submission, answer_key, results)
    
    # Budget variance percentage (5 points)
    points += evaluate_budget_variance(submission, answer_key, results)
    
    # Cost-saving opportunities (15 points)
    points += evaluate_cost_saving_opportunities(submission, answer_key, results)
    
    # Calculate final score and result
    results["total_points_earned"] = points
    results["overall_score"] = (points / 100) * 100  # Convert to percentage
    
    # Check for any critical errors in the sections
    has_critical_error = any(
        results.get(section, {}).get("critical_error", False) 
        for section in ["department_allocations", "training_category_costs", "roi_calculations"]
    ) or "critical_errors" in results
    
    if has_critical_error:
        results["result"] = "FAIL (Critical Error)"
    elif points >= results["distinction_threshold"]:
        results["result"] = "PASS with DISTINCTION"
    elif points >= results["passing_threshold"]:
        results["result"] = "PASS"
    else:
        results["result"] = "FAIL"
    
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
    print(f"Result: {results['result']}")

if __name__ == "__main__":
    main()