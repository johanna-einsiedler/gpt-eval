#!/usr/bin/env python3

import json
import sys
import os
from typing import Dict, Any, List, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{filename}' contains invalid JSON.")
        sys.exit(1)

def evaluate_task_1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 1: Supplier Quote Analysis"""
    score = 0
    max_points = 20
    feedback = []
    
    # Check calculations (10 points)
    calc_points = 0
    expected_costs = answer_key["total_cost_calculation"]
    submitted_costs = submission.get("total_cost_calculation", {})
    
    suppliers = ["BearingPro", "GlobalBearing", "PrecisionParts"]
    for supplier in suppliers:
        expected = expected_costs.get(supplier)
        submitted = submitted_costs.get(supplier)
        
        if submitted is not None and abs(submitted - expected) <= 0.01:  # Allow small rounding differences
            calc_points += (10 / 3)  # 10 points divided by 3 suppliers
            feedback.append(f"Correct calculation for {supplier}: ${submitted:.2f}")
        else:
            feedback.append(f"Incorrect calculation for {supplier}. Expected: ${expected:.2f}, Got: ${submitted if submitted is not None else 'missing'}")
    
    # Round to avoid floating point precision issues
    calc_points = round(calc_points, 2)
    score += calc_points
    
    # Check supplier selection (8 points)
    selected_supplier = submission.get("selected_supplier")
    expected_supplier = answer_key["selected_supplier"]
    alternative = answer_key.get("acceptable_alternate", {}).get("comment", "")
    
    if selected_supplier == expected_supplier:
        score += 8
        feedback.append(f"Correct supplier selection: {selected_supplier}")
    elif "PrecisionParts" in selected_supplier and "justification" in submission:
        # Check if justification is strong for choosing PrecisionParts
        justification = submission.get("selection_justification", "")
        if len(justification) >= 100 and ("quality" in justification.lower() or "delivery" in justification.lower()):
            score += 8
            feedback.append(f"Alternative supplier selection ({selected_supplier}) accepted with strong justification.")
        else:
            feedback.append(f"Incorrect supplier selection. Expected: {expected_supplier}, Got: {selected_supplier}")
    else:
        feedback.append(f"Incorrect supplier selection. Expected: {expected_supplier}, Got: {selected_supplier}")
    
    # Check negotiation points (2 points)
    negotiation_points = submission.get("negotiation_points", [])
    if len(negotiation_points) >= 2:
        score += 2
        feedback.append(f"Provided {len(negotiation_points)} negotiation points.")
    else:
        feedback.append(f"Insufficient negotiation points. Needed at least 2, got {len(negotiation_points)}.")
    
    return score, {"score": score, "max_points": max_points, "feedback": feedback}

def evaluate_task_2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 2: Quality Specification Review"""
    score = 0
    max_points = 20
    feedback = []
    
    # Check compliance issues identification (12 points)
    expected_issues = set(issue.lower() for issue in answer_key["compliance_issues"])
    submitted_issues = set(issue.lower() for issue in submission.get("compliance_issues", []))
    
    correct_issues = submitted_issues.intersection(expected_issues)
    issues_score = min(len(correct_issues) * 3, 12)  # 3 points per issue, max 12
    score += issues_score
    
    found_issues = len(correct_issues)
    total_issues = len(expected_issues)
    
    if found_issues == total_issues:
        feedback.append(f"Correctly identified all {total_issues} compliance issues.")
    else:
        feedback.append(f"Identified {found_issues} of {total_issues} compliance issues.")
        missed = expected_issues - submitted_issues
        if missed:
            feedback.append(f"Missed issues: {', '.join(missed)}")
    
    # Check recommendation (4 points)
    expected_recommendation = answer_key["recommendation"]
    submitted_recommendation = submission.get("recommendation", "")
    
    if submitted_recommendation.lower() == expected_recommendation.lower():
        score += 4
        feedback.append(f"Correct recommendation: {submitted_recommendation}")
    else:
        feedback.append(f"Incorrect recommendation. Expected: {expected_recommendation}, Got: {submitted_recommendation}")
    
    # Check critical failing identification (4 points)
    expected_critical = answer_key["critical_failing"].lower()
    submitted_justification = submission.get("justification", "").lower()
    
    if "weight capacity" in submitted_justification and "275" in submitted_justification:
        score += 4
        feedback.append("Correctly identified weight capacity as critical failing.")
    else:
        feedback.append(f"Failed to identify the critical failing: {expected_critical}")
    
    return score, {"score": score, "max_points": max_points, "feedback": feedback}

def evaluate_task_3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 3: Economic Order Quantity Calculation"""
    score = 0
    max_points = 20
    feedback = []
    
    # Check EOQ calculation (5 points)
    expected_eoq = answer_key["eoq_calculation"]
    submitted_eoq_string = submission.get("eoq_calculation", "")
    
    # Try to extract a numeric value from the EOQ calculation string
    import re
    submitted_eoq = None
    eoq_matches = re.findall(r'=\s*(\d+\.?\d*)', submitted_eoq_string)
    if eoq_matches:
        submitted_eoq = float(eoq_matches[-1])  # Take the last number as the final result
    else:
        try:
            # Try to convert the whole string in case it's just a number
            submitted_eoq = float(submitted_eoq_string)
        except ValueError:
            pass
    
    if submitted_eoq is not None and abs(submitted_eoq - expected_eoq) / expected_eoq <= 0.05:  # Within 5%
        score += 5
        feedback.append(f"Correct EOQ calculation: {submitted_eoq}")
    else:
        feedback.append(f"Incorrect EOQ calculation. Expected around {expected_eoq}, Got: {submitted_eoq_string}")
    
    # Check recommended order quantity (5 points)
    expected_quantity = answer_key["recommended_order_quantity"]
    submitted_quantity = submission.get("recommended_order_quantity")
    
    if submitted_quantity == expected_quantity:
        score += 5
        feedback.append(f"Correct recommended order quantity: {submitted_quantity}")
    else:
        feedback.append(f"Incorrect recommended order quantity. Expected: {expected_quantity}, Got: {submitted_quantity}")
    
    # Check orders per year and frequency (4 points)
    expected_orders = answer_key["orders_per_year"]
    submitted_orders = submission.get("orders_per_year")
    
    expected_frequency = answer_key["order_frequency_days"]
    submitted_frequency = submission.get("order_frequency_days")
    
    if submitted_orders == expected_orders and submitted_frequency == expected_frequency:
        score += 4
        feedback.append(f"Correct orders per year ({submitted_orders}) and frequency ({submitted_frequency} days)")
    elif submitted_orders == expected_orders:
        score += 2
        feedback.append(f"Correct orders per year ({submitted_orders}), but incorrect frequency")
    elif submitted_frequency == expected_frequency:
        score += 2
        feedback.append(f"Correct order frequency ({submitted_frequency} days), but incorrect orders per year")
    else:
        feedback.append(f"Incorrect orders per year and frequency. Expected: {expected_orders} orders, {expected_frequency} days")
    
    # Check total annual cost (4 points)
    expected_cost = answer_key["total_annual_cost"]
    submitted_cost = submission.get("total_annual_cost")
    
    if submitted_cost is not None and abs(submitted_cost - expected_cost) <= 50:  # Allow for small differences
        score += 4
        feedback.append(f"Correct total annual cost: ${submitted_cost:.2f}")
    else:
        feedback.append(f"Incorrect total annual cost. Expected: ${expected_cost:.2f}, Got: ${submitted_cost if submitted_cost is not None else 'missing'}")
    
    # Check discount analysis (2 points)
    expected_discount = answer_key["take_quantity_discount"]
    discount_analysis = submission.get("discount_analysis", "").lower()
    
    if ((expected_discount and "take" in discount_analysis or "recommend" in discount_analysis) or
        (not expected_discount and "not" in discount_analysis)):
        score += 2
        feedback.append("Correct discount analysis.")
    else:
        feedback.append("Incorrect or missing discount analysis.")
    
    return score, {"score": score, "max_points": max_points, "feedback": feedback}

def evaluate_task_4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 4: Supplier Negotiation Scenario"""
    score = 0
    max_points = 20
    feedback = []
    
    # Check justified increase percentage (5 points)
    expected_increase = answer_key["justified_increase_percentage"]
    price_analysis = submission.get("price_increase_analysis", "").lower()
    
    if "7" in price_analysis and "8" in price_analysis and "material" in price_analysis:
        score += 5
        feedback.append("Correctly identified 7-8% as the justified increase range based on market research.")
    else:
        feedback.append(f"Failed to identify {expected_increase}% as the justified increase percentage.")
    
    # Check counter-offer percentage (5 points)
    expected_counter = answer_key["counter_offer_percentage"]
    strategy = submission.get("negotiation_strategy", {})
    target_outcome = strategy.get("target_outcome", "").lower()
    
    # Look for counter-offer in either negotiation strategy or email response
    email_response = submission.get("email_response", "").lower()
    counter_offer_found = False
    
    if "5%" in target_outcome or "5%" in email_response:
        counter_offer_found = True
    elif "4%" in target_outcome or "4%" in email_response or "6%" in target_outcome or "6%" in email_response:
        # Accept 4-6% as reasonable alternatives
        counter_offer_found = True
    
    if counter_offer_found:
        score += 5
        feedback.append("Proposed reasonable counter-offer percentage (4-6%).")
    else:
        feedback.append(f"Failed to propose the expected 5% counter-offer or a reasonable alternative.")
    
    # Check primary negotiation leverage (4 points)
    expected_leverage = answer_key["primary_negotiation_leverage"]
    leverage_points = strategy.get("key_leverage_points", [])
    
    leverage_found = False
    for point in leverage_points:
        if expected_leverage.lower() in point.lower() or "15%" in point or "increase" in point.lower() and "volume" in point.lower():
            leverage_found = True
            break
    
    if leverage_found:
        score += 4
        feedback.append(f"Correctly identified {expected_leverage} as primary negotiation leverage.")
    else:
        feedback.append(f"Failed to identify {expected_leverage} as primary negotiation leverage.")
    
    # Check negotiation approach (3 points)
    expected_approach = answer_key["negotiation_approach"]
    submitted_approach = strategy.get("approach", "").lower()
    
    if expected_approach.lower() in submitted_approach:
        score += 3
        feedback.append(f"Correct negotiation approach: {expected_approach}")
    else:
        feedback.append(f"Incorrect negotiation approach. Expected: {expected_approach}, Got: {submitted_approach}")
    
    # Check concession requests (3 points)
    expected_concessions = [c.lower() for c in answer_key["prioritized_concessions_to_request"]]
    min_acceptable = strategy.get("minimum_acceptable_terms", "").lower()
    
    concessions_found = 0
    for expected in expected_concessions:
        if any(expected in email_response or 
               expected in min_acceptable or
               expected in conc.lower() for conc in leverage_points):
            concessions_found += 1
    
    concessions_score = min(concessions_found, 3)
    score += concessions_score
    
    if concessions_found > 0:
        feedback.append(f"Identified {concessions_found} appropriate concessions to request.")
    else:
        feedback.append("Failed to identify appropriate concessions to request.")
    
    return score, {"score": score, "max_points": max_points, "feedback": feedback}

def evaluate_task_5(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 5: Procurement Planning"""
    score = 0
    max_points = 20
    feedback = []
    
    # Check procurement timeline (8 points)
    expected_timeline = answer_key["procurement_timeline"]
    submitted_timeline = submission.get("procurement_timeline", [])
    
    # Check if all required stages are present
    expected_stages = [stage["stage"] for stage in expected_timeline]
    submitted_stages = [stage["stage"] for stage in submitted_timeline]
    
    # Check if timeline allows first delivery by day 23
    first_delivery_possible = False
    total_days_before_delivery = 0
    
    for stage in submitted_timeline:
        stage_name = stage["stage"].lower()
        if "delivery" in stage_name:
            # Check if delivery starts by day 23 or earlier
            start_day = stage.get("start_day")
            if start_day is not None and start_day <= 23:
                first_delivery_possible = True
            break
        else:
            # Count days in previous stages
            duration = stage.get("duration", 0)
            total_days_before_delivery += duration
    
    # Alternative check if start_day isn't provided
    if not first_delivery_possible and total_days_before_delivery <= 23:
        first_delivery_possible = True
    
    # Score the timeline
    timeline_score = 0
    
    # 3 points for including all required stages
    all_stages_present = all(stage.lower() in ' '.join(submitted_stages).lower() for stage in expected_stages)
    if all_stages_present:
        timeline_score += 3
        feedback.append("Included all required procurement stages.")
    else:
        feedback.append("Missing one or more required procurement stages.")
    
    # 5 points for feasible timeline meeting the first delivery deadline
    if first_delivery_possible:
        timeline_score += 5
        feedback.append("Timeline allows for first delivery by day 23 (meeting the deadline).")
    else:
        feedback.append("Timeline does not allow for first delivery by day 23 (missing the deadline).")
    
    score += timeline_score
    
    # Check evaluation criteria (4 points)
    expected_criteria = set(c.lower() for c in answer_key["top_evaluation_criteria"])
    submitted_criteria = []
    
    for criterion in submission.get("evaluation_criteria", []):
        submitted_criteria.append(criterion.get("criterion", "").lower())
    
    correct_criteria = set(submitted_criteria).intersection(expected_criteria)
    criteria_score = min(len(correct_criteria) * 1.5, 4)  # 1.5 points per correct criterion, max 4
    score += criteria_score
    
    if len(correct_criteria) > 0:
        feedback.append(f"Identified {len(correct_criteria)} of {len(expected_criteria)} key evaluation criteria.")
    else:
        feedback.append("Failed to identify any key evaluation criteria.")
    
    # Check delivery schedule (4 points)
    delivery_schedule = submission.get("delivery_schedule", "").lower()
    
    if "30" in delivery_schedule and "15" in delivery_schedule:
        score += 4
        feedback.append("Delivery schedule correctly accounts for the first group arrival (15 laptops by day 30).")
    elif "stagger" in delivery_schedule and ("first" in delivery_schedule or "initial" in delivery_schedule):
        score += 2
        feedback.append("Delivery schedule mentions staggered delivery but lacks specific details.")
    else:
        feedback.append("Delivery schedule does not address first group arrival requirements.")
    
    # Check risk assessment (4 points)
    expected_risk = answer_key["primary_procurement_risk"]
    risks = submission.get("risk_assessment", [])
    
    risk_score = 0
    risk_found = False
    
    for risk in risks:
        risk_name = risk.get("risk", "").lower()
        if expected_risk in risk_name or "time" in risk_name or "delay" in risk_name or "deadline" in risk_name:
            risk_found = True
            
            # Check if there's a mitigation strategy
            if "mitigation" in risk and len(risk["mitigation"]) > 10:
                risk_score = 4
            else:
                risk_score = 2
            break
    
    if not risk_found and len(risks) > 0:
        risk_score = 1  # At least identified some risks
    
    score += risk_score
    
    if risk_found:
        feedback.append(f"Correctly identified {expected_risk} as primary procurement risk.")
    else:
        feedback.append(f"Failed to identify {expected_risk} as primary procurement risk.")
    
    return score, {"score": score, "max_points": max_points, "feedback": feedback}

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "tasks": {}
    }
    
    # Evaluate Task 1
    task1_score, task1_details = evaluate_task_1(submission.get("task_1", {}), answer_key.get("task_1", {}))
    results["tasks"]["task_1"] = task1_details
    results["total_points"] += task1_score
    
    # Evaluate Task 2
    task2_score, task2_details = evaluate_task_2(submission.get("task_2", {}), answer_key.get("task_2", {}))
    results["tasks"]["task_2"] = task2_details
    results["total_points"] += task2_score
    
    # Evaluate Task 3
    task3_score, task3_details = evaluate_task_3(submission.get("task_3", {}), answer_key.get("task_3", {}))
    results["tasks"]["task_3"] = task3_details
    results["total_points"] += task3_score
    
    # Evaluate Task 4
    task4_score, task4_details = evaluate_task_4(submission.get("task_4", {}), answer_key.get("task_4", {}))
    results["tasks"]["task_4"] = task4_details
    results["total_points"] += task4_score
    
    # Evaluate Task 5
    task5_score, task5_details = evaluate_task_5(submission.get("task_5", {}), answer_key.get("task_5", {}))
    results["tasks"]["task_5"] = task5_details
    results["total_points"] += task5_score
    
    # Calculate overall percentage score
    results["overall_score"] = round((results["total_points"] / results["max_points"]) * 100, 2)
    
    # Check for passing criteria
    results["passed"] = results["overall_score"] >= 70
    
    # Check for task minimum scores (60% per task)
    task_min_scores = all([
        task1_score >= 12,
        task2_score >= 12,
        task3_score >= 12,
        task4_score >= 12,
        task5_score >= 12
    ])
    
    if not task_min_scores:
        results["passed"] = False
        results["fail_reason"] = "Did not achieve minimum score of 60% on one or more tasks"
    
    # Check for critical failures
    critical_failures = []
    
    # Task 1 critical failure: Selecting a supplier without proper cost calculation
    if not all(key in submission.get("task_1", {}).get("total_cost_calculation", {}) for key in ["BearingPro", "GlobalBearing", "PrecisionParts"]):
        critical_failures.append("Selecting a supplier in Task 1 without proper cost calculation")
    
    # Task 2 critical failure: Accepting a chair that fails weight capacity
    if (submission.get("task_2", {}).get("recommendation", "").lower() == "accept" and 
        "weight capacity" not in " ".join(submission.get("task_2", {}).get("compliance_issues", []))):
        critical_failures.append("Accepting a chair in Task 2 that fails the critical weight capacity requirement")
    
    # Task 3 critical failure: Recommending an order quantity that exceeds constraints
    if submission.get("task_3", {}).get("recommended_order_quantity", 0) > 500:
        critical_failures.append("Recommending an order quantity in Task 3 that exceeds warehouse constraints")
    
    # Task 5 critical failure: Timeline that can't meet first delivery deadline
    for stage in submission.get("task_5", {}).get("procurement_timeline", []):
        if "delivery" in stage.get("stage", "").lower():
            if stage.get("start_day", 999) > 23:
                critical_failures.append("Creating a timeline in Task 5 that cannot meet the critical first delivery deadline")
            break
    
    if critical_failures:
        results["passed"] = False
        results["critical_failures"] = critical_failures
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key_raw = load_json_file(answer_key_file)
    
    # The answer key might be nested under "answer_key" key
    answer_key = answer_key_raw.get("answer_key", answer_key_raw)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save the results to test_results.json
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}% ({results['total_points']}/{results['max_points']} points)")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()