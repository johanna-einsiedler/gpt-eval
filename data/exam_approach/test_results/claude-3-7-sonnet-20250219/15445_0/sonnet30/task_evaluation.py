#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, List, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_budget_structure(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Evaluate the budget structure and compliance (40 points)."""
    score = 0
    feedback = []
    
    # Check total annual budget (10 points)
    submission_total = submission.get("total_annual_budget", 0)
    expected_total = answer_key["total_annual_budget"]
    
    if submission_total == expected_total:
        score += 10
        feedback.append({
            "criterion": "Total Annual Budget",
            "points_earned": 10,
            "points_possible": 10,
            "feedback": "Correct total annual budget of $4,850,000."
        })
    else:
        feedback.append({
            "criterion": "Total Annual Budget",
            "points_earned": 0,
            "points_possible": 10,
            "feedback": f"Incorrect total annual budget. Expected: ${expected_total:,}, Got: ${submission_total:,}"
        })
    
    # Check minimum category allocations (15 points)
    min_allocations = {
        "staff_costs": 1843000,  # 38% of 4,850,000
        "maintenance_costs": 970000,  # 20% of 4,850,000
        "operational_supplies": 388000,  # 8% of 4,850,000
        "utilities": 291000,  # 6% of 4,850,000
        "regulatory_compliance": 291000,  # 6% of 4,850,000
        "equipment_upgrades": 436500,  # 9% of 4,850,000
    }
    max_allocations = {
        "contingency": 242500,  # 5% of 4,850,000
    }
    
    category_points = 0
    category_feedback = []
    
    for category, min_value in min_allocations.items():
        submission_value = submission.get("annual_category_totals", {}).get(category, 0)
        if submission_value >= min_value:
            category_points += 1
            category_feedback.append(f"{category.replace('_', ' ').title()}: Met minimum requirement (${min_value:,})")
        else:
            category_feedback.append(f"{category.replace('_', ' ').title()}: Failed to meet minimum requirement. Expected at least ${min_value:,}, Got: ${submission_value:,}")
    
    for category, max_value in max_allocations.items():
        submission_value = submission.get("annual_category_totals", {}).get(category, 0)
        if submission_value <= max_value:
            category_points += 1
            category_feedback.append(f"{category.replace('_', ' ').title()}: Within maximum limit (${max_value:,})")
        else:
            category_feedback.append(f"{category.replace('_', ' ').title()}: Exceeded maximum limit. Expected at most ${max_value:,}, Got: ${submission_value:,}")
    
    # Calculate points based on categories (7 categories total)
    allocation_score = round((category_points / 7) * 15)
    score += allocation_score
    
    feedback.append({
        "criterion": "Category Allocations",
        "points_earned": allocation_score,
        "points_possible": 15,
        "feedback": "\n".join(category_feedback)
    })
    
    # Check if monthly allocations reflect operational needs (15 points)
    monthly_score = 0
    monthly_feedback = []
    
    # Check if maintenance budget is higher in months with more maintenance days
    maintenance_days = {
        "january": 2, "february": 2, "march": 3, "april": 4, "may": 2,
        "june": 2, "july": 5, "august": 2, "september": 2, "october": 3,
        "november": 2, "december": 3
    }
    
    # Group months by maintenance days
    maintenance_groups = {}
    for month, days in maintenance_days.items():
        if days not in maintenance_groups:
            maintenance_groups[days] = []
        maintenance_groups[days].append(month)
    
    # Check if maintenance budget increases with maintenance days
    maintenance_correlation = True
    prev_avg = 0
    
    for days in sorted(maintenance_groups.keys()):
        months = maintenance_groups[days]
        month_values = [submission.get("monthly_budget", {}).get(month, {}).get("maintenance_costs", 0) for month in months]
        avg_value = sum(month_values) / len(month_values) if month_values else 0
        
        if prev_avg > 0 and avg_value <= prev_avg:
            maintenance_correlation = False
            monthly_feedback.append(f"Maintenance budget does not increase with maintenance days for {days} day group")
        
        prev_avg = avg_value
    
    if maintenance_correlation:
        monthly_score += 7
        monthly_feedback.append("Maintenance budget correctly increases with planned maintenance days")
    
    # Check if equipment upgrades are distributed evenly
    equipment_values = [submission.get("monthly_budget", {}).get(month, {}).get("equipment_upgrades", 0) 
                        for month in submission.get("monthly_budget", {})]
    
    if equipment_values and max(equipment_values) - min(equipment_values) <= max(equipment_values) * 0.1:
        monthly_score += 4
        monthly_feedback.append("Equipment upgrades are distributed appropriately across months")
    else:
        monthly_feedback.append("Equipment upgrades should be distributed more evenly across months")
    
    # Check if staff costs are distributed evenly
    staff_values = [submission.get("monthly_budget", {}).get(month, {}).get("staff_costs", 0) 
                    for month in submission.get("monthly_budget", {})]
    
    if staff_values and max(staff_values) - min(staff_values) <= max(staff_values) * 0.1:
        monthly_score += 4
        monthly_feedback.append("Staff costs are distributed appropriately across months")
    else:
        monthly_feedback.append("Staff costs should be distributed more evenly across months")
    
    score += monthly_score
    feedback.append({
        "criterion": "Monthly Budget Distribution",
        "points_earned": monthly_score,
        "points_possible": 15,
        "feedback": "\n".join(monthly_feedback)
    })
    
    return score, feedback

def evaluate_calculations(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Evaluate the calculations (30 points)."""
    score = 0
    feedback = []
    
    # Check monthly well maintenance cost (5 points)
    submission_well_cost = submission.get("calculations", {}).get("monthly_well_maintenance_cost", 0)
    expected_well_cost = answer_key["calculations"]["monthly_well_maintenance_cost"]
    
    if submission_well_cost == expected_well_cost:
        score += 5
        feedback.append({
            "criterion": "Monthly Well Maintenance Cost",
            "points_earned": 5,
            "points_possible": 5,
            "feedback": f"Correct monthly well maintenance cost of ${expected_well_cost:,}."
        })
    else:
        feedback.append({
            "criterion": "Monthly Well Maintenance Cost",
            "points_earned": 0,
            "points_possible": 5,
            "feedback": f"Incorrect monthly well maintenance cost. Expected: ${expected_well_cost:,}, Got: ${submission_well_cost:,}"
        })
    
    # Check preventive/reactive maintenance allocation (10 points)
    submission_preventive = submission.get("calculations", {}).get("preventive_maintenance_allocation", 0)
    submission_reactive = submission.get("calculations", {}).get("reactive_maintenance_allocation", 0)
    expected_preventive = answer_key["calculations"]["preventive_maintenance_allocation"]
    expected_reactive = answer_key["calculations"]["reactive_maintenance_allocation"]
    
    # Calculate total maintenance budget from submission
    submission_total_maintenance = submission.get("annual_category_totals", {}).get("maintenance_costs", 0)
    
    # Check if the split is close to 70/30
    maintenance_points = 0
    maintenance_feedback = []
    
    if submission_total_maintenance > 0:
        submission_preventive_pct = submission_preventive / submission_total_maintenance
        submission_reactive_pct = submission_reactive / submission_total_maintenance
        
        if abs(submission_preventive_pct - 0.7) <= 0.02 and abs(submission_reactive_pct - 0.3) <= 0.02:
            maintenance_points = 10
            maintenance_feedback.append(f"Correct 70/30 split for preventive/reactive maintenance.")
        elif abs(submission_preventive_pct - 0.7) <= 0.05 and abs(submission_reactive_pct - 0.3) <= 0.05:
            maintenance_points = 5
            maintenance_feedback.append(f"Close to 70/30 split for preventive/reactive maintenance, but not precise enough.")
        else:
            maintenance_feedback.append(f"Incorrect split for preventive/reactive maintenance. Expected: 70%/30%, Got: {submission_preventive_pct:.1%}/{submission_reactive_pct:.1%}")
    else:
        maintenance_feedback.append("Could not calculate maintenance split percentages due to missing or zero total maintenance budget.")
    
    score += maintenance_points
    feedback.append({
        "criterion": "Maintenance Allocation Split",
        "points_earned": maintenance_points,
        "points_possible": 10,
        "feedback": "\n".join(maintenance_feedback)
    })
    
    # Check cost per kWh calculation (10 points)
    submission_cost_kwh = submission.get("calculations", {}).get("cost_per_kwh", 0)
    expected_cost_kwh = answer_key["calculations"]["cost_per_kwh"]
    
    if abs(submission_cost_kwh - expected_cost_kwh) <= 0.0005:
        score += 10
        feedback.append({
            "criterion": "Cost per kWh",
            "points_earned": 10,
            "points_possible": 10,
            "feedback": f"Correct cost per kWh calculation of ${expected_cost_kwh:.4f}."
        })
    else:
        feedback.append({
            "criterion": "Cost per kWh",
            "points_earned": 0,
            "points_possible": 10,
            "feedback": f"Incorrect cost per kWh calculation. Expected: ${expected_cost_kwh:.4f}, Got: ${submission_cost_kwh:.4f}"
        })
    
    # Check balanced monthly budgets (5 points)
    monthly_budgets = submission.get("monthly_budget", {})
    monthly_totals = {}
    
    for month, categories in monthly_budgets.items():
        monthly_totals[month] = sum(categories.values())
    
    if monthly_totals:
        avg_monthly = sum(monthly_totals.values()) / len(monthly_totals)
        max_deviation = max([abs(total - avg_monthly) for total in monthly_totals.values()])
        
        if max_deviation <= avg_monthly * 0.1:
            score += 5
            feedback.append({
                "criterion": "Balanced Monthly Budgets",
                "points_earned": 5,
                "points_possible": 5,
                "feedback": "Monthly budgets are appropriately balanced."
            })
        else:
            feedback.append({
                "criterion": "Balanced Monthly Budgets",
                "points_earned": 0,
                "points_possible": 5,
                "feedback": "Monthly budgets show excessive variation. Each month should have a similar total budget."
            })
    else:
        feedback.append({
            "criterion": "Balanced Monthly Budgets",
            "points_earned": 0,
            "points_possible": 5,
            "feedback": "Could not evaluate monthly budget balance due to missing data."
        })
    
    return score, feedback

def evaluate_scenario_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Evaluate the scenario analysis (30 points)."""
    score = 0
    feedback = []
    
    # Check chemical cost increase impact (10 points)
    submission_chemical = submission.get("scenario_impacts", {}).get("chemical_cost_increase", 0)
    expected_chemical = answer_key["scenario_impacts"]["chemical_cost_increase"]
    
    if abs(submission_chemical - expected_chemical) <= expected_chemical * 0.02:
        score += 10
        feedback.append({
            "criterion": "Chemical Cost Increase Impact",
            "points_earned": 10,
            "points_possible": 10,
            "feedback": f"Correct chemical cost increase impact of ${expected_chemical:,}."
        })
    else:
        feedback.append({
            "criterion": "Chemical Cost Increase Impact",
            "points_earned": 0,
            "points_possible": 10,
            "feedback": f"Incorrect chemical cost increase impact. Expected: ${expected_chemical:,}, Got: ${submission_chemical:,}"
        })
    
    # Check monitoring frequency increase impact (10 points)
    submission_monitoring = submission.get("scenario_impacts", {}).get("monitoring_frequency_increase", 0)
    expected_monitoring = answer_key["scenario_impacts"]["monitoring_frequency_increase"]
    
    if abs(submission_monitoring - expected_monitoring) <= expected_monitoring * 0.02:
        score += 10
        feedback.append({
            "criterion": "Monitoring Frequency Increase Impact",
            "points_earned": 10,
            "points_possible": 10,
            "feedback": f"Correct monitoring frequency increase impact of ${expected_monitoring:,}."
        })
    else:
        feedback.append({
            "criterion": "Monitoring Frequency Increase Impact",
            "points_earned": 0,
            "points_possible": 10,
            "feedback": f"Incorrect monitoring frequency increase impact. Expected: ${expected_monitoring:,}, Got: ${submission_monitoring:,}"
        })
    
    # Check pump replacement impact (10 points)
    submission_pump = submission.get("scenario_impacts", {}).get("pump_replacement", 0)
    expected_pump = answer_key["scenario_impacts"]["pump_replacement"]
    
    if abs(submission_pump - expected_pump) <= expected_pump * 0.02:
        score += 10
        feedback.append({
            "criterion": "Pump Replacement Impact",
            "points_earned": 10,
            "points_possible": 10,
            "feedback": f"Correct pump replacement impact of ${expected_pump:,}."
        })
    else:
        feedback.append({
            "criterion": "Pump Replacement Impact",
            "points_earned": 0,
            "points_possible": 10,
            "feedback": f"Incorrect pump replacement impact. Expected: ${expected_pump:,}, Got: ${submission_pump:,}"
        })
    
    return score, feedback

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "sections": [],
        "total_points_earned": 0,
        "total_points_possible": 100,
        "overall_score": 0
    }
    
    # Evaluate budget structure and compliance (40 points)
    structure_score, structure_feedback = evaluate_budget_structure(submission, answer_key)
    results["sections"].append({
        "section_name": "Budget Structure and Compliance",
        "points_earned": structure_score,
        "points_possible": 40,
        "criteria": structure_feedback
    })
    results["total_points_earned"] += structure_score
    
    # Evaluate calculations (30 points)
    calculations_score, calculations_feedback = evaluate_calculations(submission, answer_key)
    results["sections"].append({
        "section_name": "Calculations",
        "points_earned": calculations_score,
        "points_possible": 30,
        "criteria": calculations_feedback
    })
    results["total_points_earned"] += calculations_score
    
    # Evaluate scenario analysis (30 points)
    scenario_score, scenario_feedback = evaluate_scenario_analysis(submission, answer_key)
    results["sections"].append({
        "section_name": "Scenario Analysis",
        "points_earned": scenario_score,
        "points_possible": 30,
        "criteria": scenario_feedback
    })
    results["total_points_earned"] += scenario_score
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points_earned"] / results["total_points_possible"]) * 100
    
    # Add pass/fail status
    results["passed"] = results["overall_score"] >= 70
    
    return results

def main():
    """Main function to evaluate a submission against an answer key."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()