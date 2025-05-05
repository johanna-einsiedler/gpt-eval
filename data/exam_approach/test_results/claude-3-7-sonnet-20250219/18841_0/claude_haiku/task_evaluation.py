#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_financial_analysis(submission, answer_key):
    """Evaluate the financial analysis section."""
    results = {
        "section_name": "Financial Analysis",
        "points_possible": 5,
        "points_earned": 0,
        "items": []
    }
    
    # Check highest increase categories
    sub_categories = submission.get("financial_analysis", {}).get("highest_increase_categories", [])
    key_categories = answer_key.get("financial_analysis", {}).get("highest_increase_categories", [])
    
    categories_correct = set(sub_categories) == set(key_categories)
    results["items"].append({
        "item_name": "highest_increase_categories",
        "correct": categories_correct,
        "submission": sub_categories,
        "expected": key_categories
    })
    if categories_correct:
        results["points_earned"] += 1
    
    # Check highest increase percentages
    sub_percentages = submission.get("financial_analysis", {}).get("highest_increase_percentages", [])
    key_percentages = answer_key.get("financial_analysis", {}).get("highest_increase_percentages", [])
    
    # Check if percentages are within 1.0 percentage point
    percentages_correct = True
    if len(sub_percentages) == len(key_percentages):
        for i in range(len(sub_percentages)):
            if abs(sub_percentages[i] - key_percentages[i]) > 1.0:
                percentages_correct = False
                break
    else:
        percentages_correct = False
    
    results["items"].append({
        "item_name": "highest_increase_percentages",
        "correct": percentages_correct,
        "submission": sub_percentages,
        "expected": key_percentages
    })
    if percentages_correct:
        results["points_earned"] += 1
    
    # Check service profit margins
    sub_margins = submission.get("financial_analysis", {}).get("service_profit_margins", {})
    key_margins = answer_key.get("financial_analysis", {}).get("service_profit_margins", {})
    
    margins_correct = True
    for service, key_margin in key_margins.items():
        if service not in sub_margins or abs(sub_margins[service] - key_margin) > 1.0:
            margins_correct = False
            break
    
    results["items"].append({
        "item_name": "service_profit_margins",
        "correct": margins_correct,
        "submission": sub_margins,
        "expected": key_margins
    })
    if margins_correct:
        results["points_earned"] += 1
    
    # Check lowest revenue month
    sub_month = submission.get("financial_analysis", {}).get("lowest_revenue_month", "")
    key_month = answer_key.get("financial_analysis", {}).get("lowest_revenue_month", "")
    
    month_correct = sub_month == key_month
    results["items"].append({
        "item_name": "lowest_revenue_month",
        "correct": month_correct,
        "submission": sub_month,
        "expected": key_month
    })
    if month_correct:
        results["points_earned"] += 1
    
    # Check monthly difference percentage
    sub_diff = submission.get("financial_analysis", {}).get("monthly_difference_percentage", 0)
    key_diff = answer_key.get("financial_analysis", {}).get("monthly_difference_percentage", 0)
    
    diff_correct = abs(sub_diff - key_diff) <= 1.0
    results["items"].append({
        "item_name": "monthly_difference_percentage",
        "correct": diff_correct,
        "submission": sub_diff,
        "expected": key_diff
    })
    if diff_correct:
        results["points_earned"] += 1
    
    return results

def evaluate_sales_performance(submission, answer_key):
    """Evaluate the sales performance section."""
    results = {
        "section_name": "Sales Performance",
        "points_possible": 5,
        "points_earned": 0,
        "items": []
    }
    
    # Check highest margin service
    sub_service = submission.get("sales_performance", {}).get("highest_margin_service", "")
    key_service = answer_key.get("sales_performance", {}).get("highest_margin_service", "")
    
    # Both Pre-Need Basic Plan and Pre-Need Premium Plan are acceptable
    service_correct = sub_service == key_service or (
        sub_service == "Pre-Need Premium Plan" and key_service == "Pre-Need Basic Plan"
    )
    
    results["items"].append({
        "item_name": "highest_margin_service",
        "correct": service_correct,
        "submission": sub_service,
        "expected": key_service + " (or Pre-Need Premium Plan)" if key_service == "Pre-Need Basic Plan" else key_service
    })
    if service_correct:
        results["points_earned"] += 1
    
    # Check highest margin percentage
    sub_margin = submission.get("sales_performance", {}).get("highest_margin_percentage", 0)
    key_margin = answer_key.get("sales_performance", {}).get("highest_margin_percentage", 0)
    
    margin_correct = abs(sub_margin - key_margin) <= 1.0
    results["items"].append({
        "item_name": "highest_margin_percentage",
        "correct": margin_correct,
        "submission": sub_margin,
        "expected": key_margin
    })
    if margin_correct:
        results["points_earned"] += 1
    
    # Check cremation growth rate
    sub_rate = submission.get("sales_performance", {}).get("cremation_growth_rate", 0)
    key_rate = answer_key.get("sales_performance", {}).get("cremation_growth_rate", 0)
    
    rate_correct = abs(sub_rate - key_rate) <= 1.0
    results["items"].append({
        "item_name": "cremation_growth_rate",
        "correct": rate_correct,
        "submission": sub_rate,
        "expected": key_rate
    })
    if rate_correct:
        results["points_earned"] += 1
    
    # Check top demographic segment
    sub_segment = submission.get("sales_performance", {}).get("top_demographic_segment", "")
    key_segment = answer_key.get("sales_performance", {}).get("top_demographic_segment", "")
    
    segment_correct = sub_segment == key_segment
    results["items"].append({
        "item_name": "top_demographic_segment",
        "correct": segment_correct,
        "submission": sub_segment,
        "expected": key_segment
    })
    if segment_correct:
        results["points_earned"] += 1
    
    # Check top segment revenue
    sub_revenue = submission.get("sales_performance", {}).get("top_segment_revenue", 0)
    key_revenue = answer_key.get("sales_performance", {}).get("top_segment_revenue", 0)
    
    # For monetary values, allow a small percentage difference
    revenue_correct = abs(sub_revenue - key_revenue) <= (key_revenue * 0.01)  # 1% tolerance
    results["items"].append({
        "item_name": "top_segment_revenue",
        "correct": revenue_correct,
        "submission": sub_revenue,
        "expected": key_revenue
    })
    if revenue_correct:
        results["points_earned"] += 1
    
    return results

def evaluate_operational_efficiency(submission, answer_key):
    """Evaluate the operational efficiency section."""
    results = {
        "section_name": "Operational Efficiency",
        "points_possible": 5,
        "points_earned": 0,
        "items": []
    }
    
    # Check lowest utilization department
    sub_dept = submission.get("operational_efficiency", {}).get("lowest_utilization_department", "")
    key_dept = answer_key.get("operational_efficiency", {}).get("lowest_utilization_department", "")
    
    dept_correct = sub_dept == key_dept
    results["items"].append({
        "item_name": "lowest_utilization_department",
        "correct": dept_correct,
        "submission": sub_dept,
        "expected": key_dept
    })
    if dept_correct:
        results["points_earned"] += 1
    
    # Check utilization rate
    sub_rate = submission.get("operational_efficiency", {}).get("utilization_rate", 0)
    key_rate = answer_key.get("operational_efficiency", {}).get("utilization_rate", 0)
    
    rate_correct = abs(sub_rate - key_rate) <= 1.0
    results["items"].append({
        "item_name": "utilization_rate",
        "correct": rate_correct,
        "submission": sub_rate,
        "expected": key_rate
    })
    if rate_correct:
        results["points_earned"] += 1
    
    # Check unused facility percentage
    sub_percent = submission.get("operational_efficiency", {}).get("unused_facility_percentage", 0)
    key_percent = answer_key.get("operational_efficiency", {}).get("unused_facility_percentage", 0)
    
    percent_correct = abs(sub_percent - key_percent) <= 1.0
    results["items"].append({
        "item_name": "unused_facility_percentage",
        "correct": percent_correct,
        "submission": sub_percent,
        "expected": key_percent
    })
    if percent_correct:
        results["points_earned"] += 1
    
    # Check lowest satisfaction service
    sub_service = submission.get("operational_efficiency", {}).get("lowest_satisfaction_service", "")
    key_service = answer_key.get("operational_efficiency", {}).get("lowest_satisfaction_service", "")
    
    service_correct = sub_service == key_service
    results["items"].append({
        "item_name": "lowest_satisfaction_service",
        "correct": service_correct,
        "submission": sub_service,
        "expected": key_service
    })
    if service_correct:
        results["points_earned"] += 1
    
    # Check satisfaction score
    sub_score = submission.get("operational_efficiency", {}).get("satisfaction_score", 0)
    key_score = answer_key.get("operational_efficiency", {}).get("satisfaction_score", 0)
    
    score_correct = abs(sub_score - key_score) <= 0.1  # Smaller tolerance for satisfaction scores
    results["items"].append({
        "item_name": "satisfaction_score",
        "correct": score_correct,
        "submission": sub_score,
        "expected": key_score
    })
    if score_correct:
        results["points_earned"] += 1
    
    return results

def evaluate_cost_reduction(submission, answer_key):
    """Evaluate the cost reduction section."""
    results = {
        "section_name": "Cost Reduction",
        "points_possible": 2,
        "points_earned": 0,
        "items": []
    }
    
    # Check reduction areas
    sub_areas = submission.get("cost_reduction", {}).get("reduction_areas", [])
    key_areas = answer_key.get("cost_reduction", {}).get("reduction_areas", [])
    
    areas_correct = set(sub_areas) == set(key_areas)
    results["items"].append({
        "item_name": "reduction_areas",
        "correct": areas_correct,
        "submission": sub_areas,
        "expected": key_areas
    })
    if areas_correct:
        results["points_earned"] += 1
    
    # Check potential annual savings
    sub_savings = submission.get("cost_reduction", {}).get("potential_annual_savings", 0)
    key_savings = answer_key.get("cost_reduction", {}).get("potential_annual_savings", 0)
    
    # For monetary values, allow a small percentage difference
    savings_correct = abs(sub_savings - key_savings) <= (key_savings * 0.01)  # 1% tolerance
    results["items"].append({
        "item_name": "potential_annual_savings",
        "correct": savings_correct,
        "submission": sub_savings,
        "expected": key_savings
    })
    if savings_correct:
        results["points_earned"] += 1
    
    return results

def evaluate_service_improvements(submission, answer_key):
    """Evaluate the service improvements section."""
    results = {
        "section_name": "Service Improvements",
        "points_possible": 3,
        "points_earned": 0,
        "items": []
    }
    
    # Check highest correlation service
    sub_service = submission.get("service_improvements", {}).get("highest_correlation_service", "")
    key_service = answer_key.get("service_improvements", {}).get("highest_correlation_service", "")
    
    service_correct = sub_service == key_service
    results["items"].append({
        "item_name": "highest_correlation_service",
        "correct": service_correct,
        "submission": sub_service,
        "expected": key_service
    })
    if service_correct:
        results["points_earned"] += 1
    
    # Check correlation value
    sub_value = submission.get("service_improvements", {}).get("correlation_value", 0)
    key_value = answer_key.get("service_improvements", {}).get("correlation_value", 0)
    
    value_correct = abs(sub_value - key_value) <= 0.01  # Small tolerance for correlation values
    results["items"].append({
        "item_name": "correlation_value",
        "correct": value_correct,
        "submission": sub_value,
        "expected": key_value
    })
    if value_correct:
        results["points_earned"] += 1
    
    # Check most requested additional service
    sub_requested = submission.get("service_improvements", {}).get("most_requested_additional_service", "")
    key_requested = answer_key.get("service_improvements", {}).get("most_requested_additional_service", "")
    
    requested_correct = sub_requested == key_requested
    results["items"].append({
        "item_name": "most_requested_additional_service",
        "correct": requested_correct,
        "submission": sub_requested,
        "expected": key_requested
    })
    if requested_correct:
        results["points_earned"] += 1
    
    # Check request frequency
    sub_freq = submission.get("service_improvements", {}).get("request_frequency", 0)
    key_freq = answer_key.get("service_improvements", {}).get("request_frequency", 0)
    
    freq_correct = abs(sub_freq - key_freq) <= 1.0
    results["items"].append({
        "item_name": "request_frequency",
        "correct": freq_correct,
        "submission": sub_freq,
        "expected": key_freq
    })
    if freq_correct:
        results["points_earned"] += 1
    
    return results

def evaluate_critical_items(sections, answer_key):
    """Evaluate the critical items required for passing."""
    critical_items = {
        "highest_increase_categories": False,
        "highest_margin_service": False,
        "potential_annual_savings": False,
        "most_requested_additional_service": False
    }
    
    # Check if critical items are correct
    for section in sections:
        for item in section["items"]:
            if item["item_name"] == "highest_increase_categories" and item["correct"]:
                critical_items["highest_increase_categories"] = True
            elif item["item_name"] == "highest_margin_service" and item["correct"]:
                critical_items["highest_margin_service"] = True
            elif item["item_name"] == "potential_annual_savings" and item["correct"]:
                critical_items["potential_annual_savings"] = True
            elif item["item_name"] == "most_requested_additional_service" and item["correct"]:
                critical_items["most_requested_additional_service"] = True
    
    # Count correct critical items
    correct_count = sum(critical_items.values())
    
    return {
        "critical_items_required": 4,
        "critical_items_correct": correct_count,
        "critical_items_passed": correct_count >= 4,
        "items": critical_items
    }

def check_section_requirements(sections):
    """Check if the candidate meets the section requirements."""
    section_requirements = {
        "Financial Analysis": {"required": 3, "earned": 0, "passed": False},
        "Sales Performance": {"required": 3, "earned": 0, "passed": False},
        "Operational Efficiency": {"required": 3, "earned": 0, "passed": False},
        "Cost Reduction": {"required": 1, "earned": 0, "passed": False},
        "Service Improvements": {"required": 2, "earned": 0, "passed": False}
    }
    
    # Count points earned in each section
    for section in sections:
        section_name = section["section_name"]
        if section_name in section_requirements:
            section_requirements[section_name]["earned"] = section["points_earned"]
            section_requirements[section_name]["passed"] = (
                section["points_earned"] >= section_requirements[section_name]["required"]
            )
    
    # Check if all section requirements are met
    all_sections_passed = all(req["passed"] for req in section_requirements.values())
    
    return {
        "all_sections_passed": all_sections_passed,
        "sections": section_requirements
    }

def calculate_overall_score(sections):
    """Calculate the overall score as a percentage."""
    total_points_possible = sum(section["points_possible"] for section in sections)
    total_points_earned = sum(section["points_earned"] for section in sections)
    
    return (total_points_earned / total_points_possible) * 100

def determine_pass_fail(overall_score, section_requirements, critical_items):
    """Determine if the candidate passed or failed the exam."""
    # Criteria for passing:
    # 1. Overall score of at least 75%
    # 2. Meet minimum requirements for each section
    # 3. Correctly identify at least 4 of 6 critical items
    
    overall_passed = overall_score >= 75.0
    sections_passed = section_requirements["all_sections_passed"]
    critical_passed = critical_items["critical_items_passed"]
    
    passed = overall_passed and sections_passed and critical_passed
    
    return {
        "passed": passed,
        "overall_score_requirement": {"required": 75.0, "achieved": overall_score, "passed": overall_passed},
        "section_requirements_passed": sections_passed,
        "critical_items_passed": critical_passed
    }

def main():
    """Main function to evaluate the candidate's submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    financial_analysis = evaluate_financial_analysis(submission, answer_key)
    sales_performance = evaluate_sales_performance(submission, answer_key)
    operational_efficiency = evaluate_operational_efficiency(submission, answer_key)
    cost_reduction = evaluate_cost_reduction(submission, answer_key)
    service_improvements = evaluate_service_improvements(submission, answer_key)
    
    sections = [
        financial_analysis,
        sales_performance,
        operational_efficiency,
        cost_reduction,
        service_improvements
    ]
    
    # Calculate overall score
    overall_score = calculate_overall_score(sections)
    
    # Check section requirements
    section_requirements = check_section_requirements(sections)
    
    # Evaluate critical items
    critical_items = evaluate_critical_items(sections, answer_key)
    
    # Determine if the candidate passed or failed
    pass_fail = determine_pass_fail(overall_score, section_requirements, critical_items)
    
    # Prepare the results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 1),
        "pass_fail": pass_fail,
        "section_requirements": section_requirements,
        "critical_items": critical_items,
        "sections": sections
    }
    
    # Save the results to a file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {round(overall_score, 1)}%")
    print(f"Result: {'PASS' if pass_fail['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()