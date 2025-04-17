#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_part1(submission, answer_key):
    """Evaluate Part 1: Data Analysis."""
    score = 0
    results = {}

    # Top 5 requested items (2 points each, max 10 points)
    correct_items = set(answer_key["part1"]["top_requested_items"])
    submitted_items = set(submission["part1"].get("top_requested_items", []))
    
    correct_count = len(correct_items.intersection(submitted_items))
    top_items_score = correct_count * 2
    
    results["top_requested_items"] = {
        "score": top_items_score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": 5,
        "details": f"Found {correct_count}/5 correct items"
    }
    score += top_items_score

    # Average monthly usage (1 point per correct calculation, max 5 points)
    usage_score = 0
    correct_usages = 0
    usage_details = []
    
    key_usages = answer_key["part1"]["average_monthly_usage"]
    submission_usages = submission["part1"].get("average_monthly_usage", {})
    
    for item_id, expected_usage in key_usages.items():
        submitted_usage = submission_usages.get(item_id)
        if submitted_usage is not None and submitted_usage == expected_usage:
            usage_score += 1
            correct_usages += 1
            usage_details.append(f"{item_id}: Correct ({submitted_usage})")
        else:
            submitted_value = "Missing" if submitted_usage is None else submitted_usage
            usage_details.append(f"{item_id}: Incorrect (submitted: {submitted_value}, expected: {expected_usage})")
    
    results["average_monthly_usage"] = {
        "score": usage_score,
        "max_score": 5,
        "correct_count": correct_usages,
        "total_count": 5,
        "details": usage_details
    }
    score += usage_score

    # Stockout items (2 points per correct item with frequency, max 18 points)
    stockout_score = 0
    correct_stockouts = 0
    stockout_details = []
    
    key_stockouts = answer_key["part1"]["stockout_items"]
    submission_stockouts = submission["part1"].get("stockout_items", {})
    
    for item_id, expected_frequency in key_stockouts.items():
        submitted_frequency = submission_stockouts.get(item_id)
        if submitted_frequency is not None and submitted_frequency == expected_frequency:
            stockout_score += 2
            correct_stockouts += 1
            stockout_details.append(f"{item_id}: Correct frequency ({submitted_frequency})")
        else:
            submitted_value = "Missing" if submitted_frequency is None else submitted_frequency
            stockout_details.append(f"{item_id}: Incorrect (submitted: {submitted_value}, expected: {expected_frequency})")
    
    # Check for additional items not in the answer key
    for item_id in submission_stockouts:
        if item_id not in key_stockouts:
            stockout_details.append(f"{item_id}: Incorrect (not a valid stockout item)")
    
    results["stockout_items"] = {
        "score": stockout_score,
        "max_score": 18,
        "correct_count": correct_stockouts,
        "total_count": len(key_stockouts),
        "details": stockout_details
    }
    score += stockout_score

    return {
        "score": score,
        "max_score": 33,
        "component_scores": results
    }

def evaluate_part2(submission, answer_key):
    """Evaluate Part 2: Supply Gap Identification."""
    score = 0
    results = {}

    # Stock coverage calculation (1 point per correct calculation, max 10 points)
    coverage_score = 0
    correct_coverages = 0
    coverage_details = []
    
    key_coverages = answer_key["part2"]["stock_coverage"]
    submission_coverages = submission["part2"].get("stock_coverage", {})
    
    for item_id, expected_coverage in key_coverages.items():
        submitted_coverage = submission_coverages.get(item_id)
        if submitted_coverage is not None and submitted_coverage == expected_coverage:
            coverage_score += 1
            correct_coverages += 1
            coverage_details.append(f"{item_id}: Correct ({submitted_coverage} days)")
        else:
            submitted_value = "Missing" if submitted_coverage is None else submitted_coverage
            coverage_details.append(f"{item_id}: Incorrect (submitted: {submitted_value}, expected: {expected_coverage})")
    
    results["stock_coverage"] = {
        "score": coverage_score,
        "max_score": 10,
        "correct_count": correct_coverages,
        "total_count": 10,
        "details": coverage_details
    }
    score += coverage_score

    # Insufficient stock items (3 points per correct item, max 9 points)
    insufficient_score = 0
    correct_items = set(answer_key["part2"]["insufficient_stock_items"])
    submitted_items = set(submission["part2"].get("insufficient_stock_items", []))
    
    common_items = correct_items.intersection(submitted_items)
    insufficient_score = len(common_items) * 3
    
    extra_items = submitted_items - correct_items
    missing_items = correct_items - submitted_items
    
    results["insufficient_stock_items"] = {
        "score": insufficient_score,
        "max_score": 9,
        "correct_count": len(common_items),
        "total_count": len(correct_items),
        "details": f"Correct: {list(common_items)}, Missing: {list(missing_items)}, Extra: {list(extra_items)}"
    }
    score += insufficient_score

    # Highest unfulfilled categories (4 points per correct category in correct order, max 16 points)
    unfulfilled_score = 0
    unfulfilled_details = []
    
    key_categories = answer_key["part2"]["highest_unfulfilled_categories"]
    submission_categories = submission["part2"].get("highest_unfulfilled_categories", [])
    
    for i, expected_category in enumerate(key_categories):
        if i < len(submission_categories) and submission_categories[i] == expected_category:
            unfulfilled_score += 4
            unfulfilled_details.append(f"Position {i+1}: Correct ({expected_category})")
        else:
            submitted_value = "Missing" if i >= len(submission_categories) else submission_categories[i]
            unfulfilled_details.append(f"Position {i+1}: Incorrect (submitted: {submitted_value}, expected: {expected_category})")
    
    results["highest_unfulfilled_categories"] = {
        "score": unfulfilled_score,
        "max_score": 16,
        "correct_count": unfulfilled_score // 4,
        "total_count": 3,
        "details": unfulfilled_details
    }
    score += unfulfilled_score

    return {
        "score": score,
        "max_score": 35,
        "component_scores": results
    }

def evaluate_part3(submission, answer_key):
    """Evaluate Part 3: Strategic Purchasing Plan."""
    score = 0
    results = {}

    # Optimal order quantities (1 point per reasonable quantity, max 10 points)
    quantities_score = 0
    quantities_details = []
    
    key_quantities = answer_key["part3"]["optimal_order_quantities"]
    submission_quantities = submission["part3"].get("optimal_order_quantities", {})
    
    for item_id, expected_quantity in key_quantities.items():
        submitted_quantity = submission_quantities.get(item_id)
        if submitted_quantity is not None:
            # Allow some flexibility in the quantities
            if abs(submitted_quantity - expected_quantity) <= expected_quantity * 0.2:  # Within 20%
                quantities_score += 1
                quantities_details.append(f"{item_id}: Reasonable ({submitted_quantity}, expected ~{expected_quantity})")
            else:
                quantities_details.append(f"{item_id}: Outside reasonable range (submitted: {submitted_quantity}, expected ~{expected_quantity})")
        else:
            quantities_details.append(f"{item_id}: Missing")
    
    results["optimal_order_quantities"] = {
        "score": quantities_score,
        "max_score": 10,
        "correct_count": quantities_score,
        "total_count": 10,
        "details": quantities_details
    }
    score += quantities_score

    # Monthly schedule (10 points for reasonable prioritization of at-risk items)
    schedule_score = 0
    schedule_details = []
    
    # Check if high-risk items (S002, S005, S008) are prioritized in month1
    key_schedule = answer_key["part3"]["monthly_schedule"]
    submission_schedule = submission["part3"].get("monthly_schedule", {})
    
    high_risk_items = {"S002", "S005", "S008"}
    month1_items = set(submission_schedule.get("month1", {}).keys())
    
    prioritized_count = len(high_risk_items.intersection(month1_items))
    
    if prioritized_count == 3:
        schedule_score = 10
        schedule_details.append("Excellent prioritization: All high-risk items in month1")
    elif prioritized_count == 2:
        schedule_score = 7
        schedule_details.append("Good prioritization: 2/3 high-risk items in month1")
    elif prioritized_count == 1:
        schedule_score = 4
        schedule_details.append("Fair prioritization: 1/3 high-risk items in month1")
    else:
        schedule_score = 0
        schedule_details.append("Poor prioritization: No high-risk items in month1")
    
    results["monthly_schedule"] = {
        "score": schedule_score,
        "max_score": 10,
        "details": schedule_details
    }
    score += schedule_score

    # Projected savings (12 points for reasonable calculation within ±15% of answer key)
    savings_score = 0
    key_savings = answer_key["part3"]["projected_savings"]
    submission_savings = submission["part3"].get("projected_savings", 0)
    
    # Calculate acceptable range (±15%)
    lower_bound = key_savings * 0.85
    upper_bound = key_savings * 1.15
    
    if lower_bound <= submission_savings <= upper_bound:
        savings_score = 12
        savings_details = f"Reasonable savings calculation: {submission_savings} (expected ~{key_savings})"
    else:
        savings_score = 0
        savings_details = f"Unreasonable savings calculation: {submission_savings} (expected range: {int(lower_bound)}-{int(upper_bound)})"
    
    results["projected_savings"] = {
        "score": savings_score,
        "max_score": 12,
        "details": savings_details
    }
    score += savings_score

    # Recommended vendors (5 points per reasonable vendor selection, max 25 points)
    vendors_score = 0
    vendors_details = []
    
    key_vendors = answer_key["part3"]["recommended_vendors"]
    submission_vendors = submission["part3"].get("recommended_vendors", {})
    
    for category, expected_vendor in key_vendors.items():
        submitted_vendor = submission_vendors.get(category)
        if submitted_vendor is not None:
            if submitted_vendor == expected_vendor:
                vendors_score += 5
                vendors_details.append(f"{category}: Optimal selection ({submitted_vendor})")
            else:
                # Check if vendor is valid for this category
                # This is a simplified check - in a real evaluation, this would reference the vendor list
                if submitted_vendor.startswith("V"):  # Assuming all valid vendors start with V
                    vendors_score += 3  # Partial credit for reasonable alternative
                    vendors_details.append(f"{category}: Alternative selection ({submitted_vendor}, expected: {expected_vendor})")
                else:
                    vendors_details.append(f"{category}: Invalid vendor ({submitted_vendor})")
        else:
            vendors_details.append(f"{category}: Missing")
    
    results["recommended_vendors"] = {
        "score": vendors_score,
        "max_score": 25,
        "details": vendors_details
    }
    score += vendors_score

    return {
        "score": score,
        "max_score": 57,
        "component_scores": results
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    # Evaluate each part
    part1_results = evaluate_part1(submission, answer_key)
    part2_results = evaluate_part2(submission, answer_key)
    part3_results = evaluate_part3(submission, answer_key)
    
    # Calculate overall score
    total_score = part1_results["score"] + part2_results["score"] + part3_results["score"]
    max_score = part1_results["max_score"] + part2_results["max_score"] + part3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Determine if the candidate passed
    passed = overall_percentage >= 60
    
    return {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_score,
        "passed": passed,
        "part1": part1_results,
        "part2": part2_results,
        "part3": part3_results
    }

def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()