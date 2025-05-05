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

def evaluate_task1(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 15,
        "details": {}
    }
    
    # Annual growth rates (4 points, 2 per rate)
    growth_rates_points = 0
    growth_rates_details = []
    
    for i, (submitted, expected) in enumerate(zip(submission.get("annual_growth_rates", []), answer_key["annual_growth_rates"])):
        if submitted is None:
            growth_rates_details.append({"expected": expected, "submitted": None, "points": 0, "comment": "Missing value"})
        else:
            error_pct = abs((submitted - expected) / expected) if expected != 0 else abs(submitted)
            if error_pct <= 0.01:  # Within 1%
                points = 2
                comment = "Correct"
            elif error_pct <= 0.03:  # Within 3%
                points = 1
                comment = "Close (within 3%)"
            else:
                points = 0
                comment = "Incorrect"
            
            growth_rates_points += points
            growth_rates_details.append({
                "expected": expected, 
                "submitted": submitted, 
                "points": points, 
                "comment": comment
            })
    
    results["details"]["annual_growth_rates"] = {
        "points_earned": growth_rates_points,
        "points_possible": 4,
        "item_details": growth_rates_details
    }
    
    # Cost categories ranking (5 points, 1 per correctly ranked category)
    ranking_points = 0
    ranking_details = []
    
    expected_ranking = answer_key["cost_categories_ranking"]
    submitted_ranking = submission.get("cost_categories_ranking", [])
    
    for i, expected_category in enumerate(expected_ranking):
        if i < len(submitted_ranking):
            if submitted_ranking[i] == expected_category:
                points = 1
                comment = "Correct"
            else:
                points = 0
                comment = f"Incorrect (expected {expected_category})"
        else:
            points = 0
            comment = "Missing value"
        
        ranking_points += points
        ranking_details.append({
            "position": i+1,
            "expected": expected_category,
            "submitted": submitted_ranking[i] if i < len(submitted_ranking) else None,
            "points": points,
            "comment": comment
        })
    
    results["details"]["cost_categories_ranking"] = {
        "points_earned": ranking_points,
        "points_possible": 5,
        "item_details": ranking_details
    }
    
    # Projected total costs (3 points)
    projected_costs = submission.get("projected_total_costs")
    expected_costs = answer_key["projected_total_costs"]
    
    if projected_costs is None:
        projected_costs_points = 0
        projected_costs_comment = "Missing value"
    else:
        error_pct = abs((projected_costs - expected_costs) / expected_costs)
        if error_pct <= 0.01:  # Within 1%
            projected_costs_points = 3
            projected_costs_comment = "Correct"
        elif error_pct <= 0.03:  # Within 3%
            projected_costs_points = 1.5
            projected_costs_comment = "Close (within 3%)"
        else:
            projected_costs_points = 0
            projected_costs_comment = "Incorrect"
    
    results["details"]["projected_total_costs"] = {
        "points_earned": projected_costs_points,
        "points_possible": 3,
        "expected": expected_costs,
        "submitted": projected_costs,
        "comment": projected_costs_comment
    }
    
    # Efficiency score (3 points)
    efficiency_score = submission.get("efficiency_score")
    expected_score = answer_key["efficiency_score"]
    
    if efficiency_score is None:
        efficiency_points = 0
        efficiency_comment = "Missing value"
    else:
        error_pct = abs((efficiency_score - expected_score) / expected_score)
        if error_pct <= 0.01:  # Within 1%
            efficiency_points = 3
            efficiency_comment = "Correct"
        elif error_pct <= 0.03:  # Within 3%
            efficiency_points = 1.5
            efficiency_comment = "Close (within 3%)"
        else:
            efficiency_points = 0
            efficiency_comment = "Incorrect"
    
    results["details"]["efficiency_score"] = {
        "points_earned": efficiency_points,
        "points_possible": 3,
        "expected": expected_score,
        "submitted": efficiency_score,
        "comment": efficiency_comment
    }
    
    # Calculate total points for Task 1
    results["points_earned"] = (
        growth_rates_points + 
        ranking_points + 
        projected_costs_points + 
        efficiency_points
    )
    
    return results

def evaluate_task2(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 15,
        "details": {}
    }
    
    # Total variance (3 points)
    total_variance = submission.get("total_variance")
    expected_variance = answer_key["total_variance"]
    
    if total_variance is None:
        variance_points = 0
        variance_comment = "Missing value"
    else:
        error_pct = abs((total_variance - expected_variance) / expected_variance) if expected_variance != 0 else abs(total_variance)
        if error_pct <= 0.01:  # Within 1%
            variance_points = 3
            variance_comment = "Correct"
        elif error_pct <= 0.03:  # Within 3%
            variance_points = 1.5
            variance_comment = "Close (within 3%)"
        else:
            variance_points = 0
            variance_comment = "Incorrect"
    
    results["details"]["total_variance"] = {
        "points_earned": variance_points,
        "points_possible": 3,
        "expected": expected_variance,
        "submitted": total_variance,
        "comment": variance_comment
    }
    
    # Variance percentages (5 points, 1 per category)
    variance_pct_points = 0
    variance_pct_details = []
    
    expected_percentages = answer_key["variance_percentages"]
    submitted_percentages = submission.get("variance_percentages", [])
    
    for i, expected_pct in enumerate(expected_percentages):
        if i < len(submitted_percentages):
            submitted_pct = submitted_percentages[i]
            if submitted_pct is None:
                points = 0
                comment = "Missing value"
            else:
                error = abs(submitted_pct - expected_pct)
                if error <= 0.1:  # Within 0.1 percentage point
                    points = 1
                    comment = "Correct"
                elif error <= 0.3:  # Within 0.3 percentage point
                    points = 0.5
                    comment = "Close"
                else:
                    points = 0
                    comment = "Incorrect"
        else:
            submitted_pct = None
            points = 0
            comment = "Missing value"
        
        variance_pct_points += points
        variance_pct_details.append({
            "category_index": i,
            "expected": expected_pct,
            "submitted": submitted_pct,
            "points": points,
            "comment": comment
        })
    
    results["details"]["variance_percentages"] = {
        "points_earned": variance_pct_points,
        "points_possible": 5,
        "item_details": variance_pct_details
    }
    
    # Highest variance category (3 points)
    highest_category = submission.get("highest_variance_category")
    expected_category = answer_key["highest_variance_category"]
    
    if highest_category is None:
        category_points = 0
        category_comment = "Missing value"
    elif highest_category == expected_category:
        category_points = 3
        category_comment = "Correct"
    else:
        category_points = 0
        category_comment = f"Incorrect (expected {expected_category})"
    
    results["details"]["highest_variance_category"] = {
        "points_earned": category_points,
        "points_possible": 3,
        "expected": expected_category,
        "submitted": highest_category,
        "comment": category_comment
    }
    
    # Cost saving opportunity (4 points)
    saving_opportunity = submission.get("cost_saving_opportunity")
    expected_opportunity = answer_key["cost_saving_opportunity"]
    
    if saving_opportunity is None:
        saving_points = 0
        saving_comment = "Missing value"
    else:
        error_pct = abs((saving_opportunity - expected_opportunity) / expected_opportunity) if expected_opportunity != 0 else abs(saving_opportunity)
        if error_pct <= 0.01:  # Within 1%
            saving_points = 4
            saving_comment = "Correct"
        elif error_pct <= 0.03:  # Within 3%
            saving_points = 2
            saving_comment = "Close (within 3%)"
        else:
            saving_points = 0
            saving_comment = "Incorrect"
    
    results["details"]["cost_saving_opportunity"] = {
        "points_earned": saving_points,
        "points_possible": 4,
        "expected": expected_opportunity,
        "submitted": saving_opportunity,
        "comment": saving_comment
    }
    
    # Calculate total points for Task 2
    results["points_earned"] = (
        variance_points + 
        variance_pct_points + 
        category_points + 
        saving_points
    )
    
    return results

def evaluate_task3(submission, answer_key):
    results = {
        "points_earned": 0,
        "points_possible": 10,
        "details": {},
        "critical_errors": []
    }
    
    # Check for critical errors
    
    # 1. Budget exceeds cap
    total_budget = submission.get("total_annual_budget", 0)
    if total_budget > 1200000:
        results["critical_errors"].append(f"Budget exceeds $1,200,000 cap (submitted: ${total_budget})")
    
    # 2. Quarterly distribution
    q1 = submission.get("q1_budget", 0)
    q2 = submission.get("q2_budget", 0)
    q3 = submission.get("q3_budget", 0)
    q4 = submission.get("q4_budget", 0)
    
    if total_budget > 0:
        q1_pct = round(q1 / total_budget * 100, 1)
        q2_pct = round(q2 / total_budget * 100, 1)
        q3_pct = round(q3 / total_budget * 100, 1)
        q4_pct = round(q4 / total_budget * 100, 1)
        
        if abs(q1_pct - 22.0) > 0.1:
            results["critical_errors"].append(f"Q1 budget does not match required 22% (submitted: {q1_pct}%)")
        if abs(q2_pct - 28.0) > 0.1:
            results["critical_errors"].append(f"Q2 budget does not match required 28% (submitted: {q2_pct}%)")
        if abs(q3_pct - 30.0) > 0.1:
            results["critical_errors"].append(f"Q3 budget does not match required 30% (submitted: {q3_pct}%)")
        if abs(q4_pct - 20.0) > 0.1:
            results["critical_errors"].append(f"Q4 budget does not match required 20% (submitted: {q4_pct}%)")
    
    # 3. Minimum allocation requirements
    allocation_pcts = submission.get("allocation_percentages", [])
    if len(allocation_pcts) >= 5:
        if allocation_pcts[0] < 35.0:
            results["critical_errors"].append(f"Materials allocation below 35% minimum (submitted: {allocation_pcts[0]}%)")
        if allocation_pcts[1] < 25.0:
            results["critical_errors"].append(f"Labor allocation below 25% minimum (submitted: {allocation_pcts[1]}%)")
        if allocation_pcts[2] < 15.0:
            results["critical_errors"].append(f"Overhead allocation below 15% minimum (submitted: {allocation_pcts[2]}%)")
        if allocation_pcts[3] < 10.0:
            results["critical_errors"].append(f"Equipment allocation below 10% minimum (submitted: {allocation_pcts[3]}%)")
        if allocation_pcts[4] < 5.0:
            results["critical_errors"].append(f"Administrative allocation below 5% minimum (submitted: {allocation_pcts[4]}%)")
    
    # Quarterly budget allocation (4 points, 1 per quarter)
    quarterly_points = 0
    quarterly_details = []
    
    quarters = [
        {"name": "q1_budget", "expected": answer_key["q1_budget"], "submitted": q1},
        {"name": "q2_budget", "expected": answer_key["q2_budget"], "submitted": q2},
        {"name": "q3_budget", "expected": answer_key["q3_budget"], "submitted": q3},
        {"name": "q4_budget", "expected": answer_key["q4_budget"], "submitted": q4}
    ]
    
    for quarter in quarters:
        expected = quarter["expected"]
        submitted = quarter["submitted"]
        
        if submitted is None:
            points = 0
            comment = "Missing value"
        else:
            error_pct = abs((submitted - expected) / expected) if expected != 0 else abs(submitted)
            if error_pct <= 0.01:  # Within 1%
                points = 1
                comment = "Correct"
            elif error_pct <= 0.03:  # Within 3%
                points = 0.5
                comment = "Close (within 3%)"
            else:
                points = 0
                comment = "Incorrect"
        
        quarterly_points += points
        quarterly_details.append({
            "quarter": quarter["name"],
            "expected": expected,
            "submitted": submitted,
            "points": points,
            "comment": comment
        })
    
    results["details"]["quarterly_budget"] = {
        "points_earned": quarterly_points,
        "points_possible": 4,
        "item_details": quarterly_details
    }
    
    # Total annual budget (1 point)
    expected_total = answer_key["total_annual_budget"]
    
    if total_budget is None:
        total_points = 0
        total_comment = "Missing value"
    else:
        error_pct = abs((total_budget - expected_total) / expected_total) if expected_total != 0 else abs(total_budget)
        if error_pct <= 0.01:  # Within 1%
            total_points = 1
            total_comment = "Correct"
        elif error_pct <= 0.03:  # Within 3%
            total_points = 0.5
            total_comment = "Close (within 3%)"
        else:
            total_points = 0
            total_comment = "Incorrect"
    
    results["details"]["total_annual_budget"] = {
        "points_earned": total_points,
        "points_possible": 1,
        "expected": expected_total,
        "submitted": total_budget,
        "comment": total_comment
    }
    
    # Category allocation percentages (5 points, 1 per category)
    allocation_points = 0
    allocation_details = []
    
    expected_allocations = answer_key["allocation_percentages"]
    
    # For Task 3, we need to be more flexible with the allocation percentages
    # as long as they meet the minimum requirements and sum to 100%
    
    categories = ["Materials", "Labor", "Overhead", "Equipment", "Administrative"]
    min_requirements = [35.0, 25.0, 15.0, 10.0, 5.0]
    
    for i, (category, min_req) in enumerate(zip(categories, min_requirements)):
        if i < len(allocation_pcts):
            submitted_pct = allocation_pcts[i]
            if submitted_pct is None:
                points = 0
                comment = "Missing value"
            elif submitted_pct >= min_req:
                points = 1
                comment = "Meets minimum requirement"
            else:
                points = 0
                comment = f"Below minimum requirement of {min_req}%"
        else:
            submitted_pct = None
            points = 0
            comment = "Missing value"
        
        allocation_points += points
        allocation_details.append({
            "category": category,
            "minimum_required": min_req,
            "submitted": submitted_pct,
            "points": points,
            "comment": comment
        })
    
    # Check if percentages sum to 100%
    if allocation_pcts and abs(sum(allocation_pcts) - 100.0) > 0.1:
        for detail in allocation_details:
            detail["comment"] += "; Percentages don't sum to 100%"
    
    results["details"]["allocation_percentages"] = {
        "points_earned": allocation_points,
        "points_possible": 5,
        "item_details": allocation_details
    }
    
    # Calculate total points for Task 3
    results["points_earned"] = (
        quarterly_points + 
        total_points + 
        allocation_points
    )
    
    # If there are critical errors, set points to 0
    if results["critical_errors"]:
        results["points_earned"] = 0
    
    return results

def evaluate_submission(submission, answer_key):
    results = {
        "task1": evaluate_task1(submission.get("task1", {}), answer_key["task1"]),
        "task2": evaluate_task2(submission.get("task2", {}), answer_key["task2"]),
        "task3": evaluate_task3(submission.get("task3", {}), answer_key["task3"]),
    }
    
    # Calculate overall score
    total_points_possible = 40  # 15 + 15 + 10
    total_points_earned = (
        results["task1"]["points_earned"] +
        results["task2"]["points_earned"] +
        results["task3"]["points_earned"]
    )
    
    # Check minimum task performance requirements
    passed_minimum_requirements = (
        results["task1"]["points_earned"] >= 10 and  # 67% of 15
        results["task2"]["points_earned"] >= 10 and  # 67% of 15
        results["task3"]["points_earned"] >= 6       # 60% of 10
    )
    
    overall_percentage = (total_points_earned / total_points_possible) * 100
    
    results["overall_score"] = round(overall_percentage, 1)
    results["total_points_earned"] = total_points_earned
    results["total_points_possible"] = total_points_possible
    results["passed_minimum_requirements"] = passed_minimum_requirements
    results["passed_exam"] = overall_percentage >= 75 and passed_minimum_requirements
    
    if "candidate_id" in submission:
        results["candidate_id"] = submission["candidate_id"]
    
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
    print(f"Passed exam: {results['passed_exam']}")

if __name__ == "__main__":
    main()