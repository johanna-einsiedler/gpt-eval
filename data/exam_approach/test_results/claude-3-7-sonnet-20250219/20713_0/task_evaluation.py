#!/usr/bin/env python3
import json
import sys
import math

def evaluate_submission(submission_file, answer_key_file):
    """
    Evaluate a candidate's test submission against the answer key.
    Returns detailed evaluation results and overall score.
    """
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in one of the input files")
        sys.exit(1)
    
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_points": 0,
        "max_points": 100,
        "overall_score": 0,
        "pass_status": False,
        "exercise1": {
            "points": 0,
            "max_points": 30,
            "details": {}
        },
        "exercise2": {
            "points": 0,
            "max_points": 35,
            "details": {}
        },
        "exercise3": {
            "points": 0,
            "max_points": 35,
            "details": {}
        },
        "critical_requirements_met": {
            "markup_formula_correct": True,
            "markdown_considers_inventory": True,
            "prices_meet_margin_requirements": True,
            "prices_within_range": True
        }
    }
    
    # Evaluate Exercise 1: Markup Rates (30 points)
    markup_products = ["product_a_markup", "product_b_markup", "product_c_markup", 
                       "product_d_markup", "product_e_markup"]
    
    for product in markup_products:
        submitted_value = submission.get("exercise1", {}).get(product, 0)
        correct_value = answer_key.get("exercise1", {}).get(product, 0)
        
        diff = abs(submitted_value - correct_value)
        details = {
            "submitted": submitted_value,
            "correct": correct_value,
            "difference": diff,
            "points": 0
        }
        
        # Check if the markup rate is within tolerance
        if diff <= 0.02:
            details["points"] = 6
            details["evaluation"] = "Correct (within ±0.02 tolerance)"
        elif diff <= 0.05:
            details["points"] = 3
            details["evaluation"] = "Partially correct (within ±0.05 tolerance)"
        else:
            details["points"] = 0
            details["evaluation"] = "Incorrect"
            
            # Check if the formula seems to be applied incorrectly
            if abs(submitted_value - 0) < 0.01 or submitted_value < 0:
                results["critical_requirements_met"]["markup_formula_correct"] = False
        
        results["exercise1"]["details"][product] = details
        results["exercise1"]["points"] += details["points"]
    
    # Evaluate Exercise 2: Markdown Rates (35 points)
    markdown_items = ["item1_markdown", "item2_markdown", "item3_markdown", "item4_markdown"]
    
    for item in markdown_items:
        submitted_value = submission.get("exercise2", {}).get(item, 0)
        correct_value = answer_key.get("exercise2", {}).get(item, 0)
        
        diff = abs(submitted_value - correct_value)
        details = {
            "submitted": submitted_value,
            "correct": correct_value,
            "difference": diff,
            "points": 0
        }
        
        # Check if the markdown rate is within tolerance
        if diff <= 0.05:
            details["points"] = 7
            details["evaluation"] = "Correct (within ±0.05 tolerance)"
        elif 0.05 < diff <= 0.15 and 0 <= submitted_value <= 1:
            details["points"] = 4
            details["evaluation"] = "Partially correct (sound logic but different rate)"
        else:
            details["points"] = 0
            details["evaluation"] = "Incorrect"
            
            # Check if markdown doesn't consider inventory needs
            if submitted_value == 0 or submitted_value > 0.90:
                results["critical_requirements_met"]["markdown_considers_inventory"] = False
        
        results["exercise2"]["details"][item] = details
        results["exercise2"]["points"] += details["points"]
    
    # Evaluate clearance revenue
    submitted_clearance = submission.get("exercise2", {}).get("expected_clearance", 0)
    correct_clearance = answer_key.get("exercise2", {}).get("expected_clearance", 0)
    
    clearance_diff_pct = abs(submitted_clearance - correct_clearance) / correct_clearance
    clearance_details = {
        "submitted": submitted_clearance,
        "correct": correct_clearance,
        "difference_pct": round(clearance_diff_pct * 100, 2),
        "points": 0
    }
    
    if clearance_diff_pct <= 0.05:
        clearance_details["points"] = 7
        clearance_details["evaluation"] = "Correct (within ±5% tolerance)"
    elif 0.05 < clearance_diff_pct <= 0.15:
        clearance_details["points"] = 3
        clearance_details["evaluation"] = "Partially correct"
    else:
        clearance_details["points"] = 0
        clearance_details["evaluation"] = "Incorrect"
    
    results["exercise2"]["details"]["expected_clearance"] = clearance_details
    results["exercise2"]["points"] += clearance_details["points"]
    
    # Evaluate Exercise 3: Price Setting (35 points)
    pricing_products = ["product_x_price", "product_y_price", "product_z_price"]
    
    # Manually define margin requirements and competitor ranges for verification
    margin_requirements = {
        "product_x_price": 0.60,  # 60% markup minimum
        "product_y_price": 0.40,  # 40% gross profit margin minimum 
        "product_z_price": 0.35   # 35% minimum category margin
    }
    
    competitor_ranges = {
        "product_x_price": (39.99, 45.99),
        "product_y_price": (59.99, 69.99),
        "product_z_price": (79.99, 89.99)
    }
    
    product_costs = {
        "product_x_price": 24.50,
        "product_y_price": 36.75,
        "product_z_price": 52.25
    }
    
    for product in pricing_products:
        submitted_price = submission.get("exercise3", {}).get(product, 0)
        correct_price = answer_key.get("exercise3", {}).get(product, 0)
        cost = product_costs.get(product, 0)
        
        # Calculate margin percentage
        if submitted_price > 0:
            submitted_margin_pct = (submitted_price - cost) / submitted_price
        else:
            submitted_margin_pct = 0
            
        price_diff_pct = abs(submitted_price - correct_price) / correct_price
        details = {
            "submitted": submitted_price,
            "correct": correct_price,
            "submitted_margin_pct": round(submitted_margin_pct * 100, 2),
            "required_margin_pct": round(margin_requirements.get(product, 0) * 100, 2),
            "difference_pct": round(price_diff_pct * 100, 2),
            "points": 0
        }
        
        # Check if the price is within competitor range
        min_price, max_price = competitor_ranges.get(product, (0, 0))
        in_range = min_price <= submitted_price <= max_price
        details["in_competitor_range"] = in_range
        
        # Check if margin requirements are met
        margin_met = submitted_margin_pct >= margin_requirements.get(product, 0)
        details["margin_requirement_met"] = margin_met
        
        if not margin_met:
            results["critical_requirements_met"]["prices_meet_margin_requirements"] = False
        
        if not in_range:
            results["critical_requirements_met"]["prices_within_range"] = False
        
        # Score based on price setting accuracy
        if price_diff_pct <= 0.05 and margin_met:
            details["points"] = 7
            details["evaluation"] = "Correct (within ±5% tolerance)"
        elif in_range and margin_met:
            details["points"] = 4
            details["evaluation"] = "Partially correct (within range, meets margin, but not optimal)"
        else:
            details["points"] = 0
            if not margin_met:
                details["evaluation"] = "Incorrect (doesn't meet margin requirement)"
            elif not in_range:
                details["evaluation"] = "Incorrect (outside competitor range)"
            else:
                details["evaluation"] = "Incorrect"
        
        results["exercise3"]["details"][product] = details
        results["exercise3"]["points"] += details["points"]
    
    # Evaluate total revenue and profit
    for metric in ["total_revenue", "total_profit"]:
        submitted_value = submission.get("exercise3", {}).get(metric, 0)
        correct_value = answer_key.get("exercise3", {}).get(metric, 0)
        
        diff_pct = abs(submitted_value - correct_value) / correct_value
        details = {
            "submitted": submitted_value,
            "correct": correct_value,
            "difference_pct": round(diff_pct * 100, 2),
            "points": 0
        }
        
        if diff_pct <= 0.05:
            details["points"] = 7
            details["evaluation"] = "Correct (within ±5% tolerance)"
        elif 0.05 < diff_pct <= 0.15:
            details["points"] = 3
            details["evaluation"] = "Partially correct"
        else:
            details["points"] = 0
            details["evaluation"] = "Incorrect"
        
        results["exercise3"]["details"][metric] = details
        results["exercise3"]["points"] += details["points"]
    
    # Calculate total score
    results["total_points"] = (
        results["exercise1"]["points"] + 
        results["exercise2"]["points"] + 
        results["exercise3"]["points"]
    )
    
    # Calculate percentage score rounded to nearest integer
    results["overall_score"] = round((results["total_points"] / results["max_points"]) * 100)
    
    # Determine if the candidate passed (70% required with critical requirements met)
    critical_requirements_met = all(results["critical_requirements_met"].values())
    results["pass_status"] = results["overall_score"] >= 70 and critical_requirements_met
    
    if results["overall_score"] >= 85 and critical_requirements_met:
        results["performance_level"] = "Excellent"
    elif results["pass_status"]:
        results["performance_level"] = "Pass"
    else:
        results["performance_level"] = "Fail"
    
    # Add reason for failure if applicable
    if not results["pass_status"]:
        failed_requirements = [
            req.replace("_", " ").capitalize() 
            for req, met in results["critical_requirements_met"].items() 
            if not met
        ]
        
        if failed_requirements:
            results["failure_reason"] = f"Failed critical requirements: {', '.join(failed_requirements)}"
        elif results["overall_score"] < 70:
            results["failure_reason"] = f"Overall score below 70% passing threshold"
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Write results to test_results.json
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {results['performance_level']}")
    print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()