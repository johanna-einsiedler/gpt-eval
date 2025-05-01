#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    score = 0
    feedback = {}
    
    # Late deliveries percentage
    sub_late = submission.get("late_deliveries_percentage")
    key_late = answer_key.get("late_deliveries_percentage")
    if sub_late is not None and key_late is not None:
        if abs(sub_late - key_late) <= key_late * 0.01:  # Within 1%
            score += 5
            feedback["late_deliveries_percentage"] = {"points": 5, "comment": "Correct"}
        elif abs(sub_late - key_late) <= key_late * 0.05:  # Within 5%
            score += 2.5
            feedback["late_deliveries_percentage"] = {"points": 2.5, "comment": "Close (within 5%)"}
        else:
            feedback["late_deliveries_percentage"] = {"points": 0, "comment": f"Incorrect. Expected: {key_late}"}
    else:
        feedback["late_deliveries_percentage"] = {"points": 0, "comment": "Missing value"}
    
    # Most common carrier
    sub_carrier = submission.get("most_common_carrier", "")
    key_carrier = answer_key.get("most_common_carrier", "")
    
    # Split by comma for multiple carriers
    sub_carriers = set(c.strip() for c in sub_carrier.split(","))
    key_carriers = set(c.strip() for c in key_carrier.split(","))
    
    if sub_carriers == key_carriers:
        score += 5
        feedback["most_common_carrier"] = {"points": 5, "comment": "Correct"}
    elif any(c in key_carriers for c in sub_carriers):
        score += 2.5
        feedback["most_common_carrier"] = {"points": 2.5, "comment": "Partially correct"}
    else:
        feedback["most_common_carrier"] = {"points": 0, "comment": f"Incorrect. Expected: {key_carrier}"}
    
    # Average shipping cost
    sub_avg = submission.get("average_shipping_cost")
    key_avg = answer_key.get("average_shipping_cost")
    if sub_avg is not None and key_avg is not None:
        if abs(sub_avg - key_avg) <= key_avg * 0.01:  # Within 1%
            score += 5
            feedback["average_shipping_cost"] = {"points": 5, "comment": "Correct"}
        elif abs(sub_avg - key_avg) <= key_avg * 0.05:  # Within 5%
            score += 2.5
            feedback["average_shipping_cost"] = {"points": 2.5, "comment": "Close (within 5%)"}
        else:
            feedback["average_shipping_cost"] = {"points": 0, "comment": f"Incorrect. Expected: {key_avg}"}
    else:
        feedback["average_shipping_cost"] = {"points": 0, "comment": "Missing value"}
    
    return score, feedback

def evaluate_task2(submission, answer_key):
    score = 0
    feedback = {}
    
    # Route with highest cost per km
    sub_route = submission.get("route_with_highest_cost_per_km", "")
    key_route = answer_key.get("route_with_highest_cost_per_km", "")
    if sub_route == key_route:
        score += 5
        feedback["route_with_highest_cost_per_km"] = {"points": 5, "comment": "Correct"}
    else:
        feedback["route_with_highest_cost_per_km"] = {"points": 0, "comment": f"Incorrect. Expected: {key_route}"}
    
    # Cost per km
    sub_cost = submission.get("cost_per_km")
    key_cost = answer_key.get("cost_per_km")
    if sub_cost is not None and key_cost is not None:
        if abs(sub_cost - key_cost) <= key_cost * 0.01:  # Within 1%
            score += 5
            feedback["cost_per_km"] = {"points": 5, "comment": "Correct"}
        elif abs(sub_cost - key_cost) <= key_cost * 0.05:  # Within 5%
            score += 2.5
            feedback["cost_per_km"] = {"points": 2.5, "comment": "Close (within 5%)"}
        else:
            feedback["cost_per_km"] = {"points": 0, "comment": f"Incorrect. Expected: {key_cost}"}
    else:
        feedback["cost_per_km"] = {"points": 0, "comment": "Missing value"}
    
    # Total distance
    sub_dist = submission.get("total_distance_all_shipments")
    key_dist = answer_key.get("total_distance_all_shipments")
    if sub_dist is not None and key_dist is not None:
        if abs(sub_dist - key_dist) <= key_dist * 0.01:  # Within 1%
            score += 5
            feedback["total_distance_all_shipments"] = {"points": 5, "comment": "Correct"}
        elif abs(sub_dist - key_dist) <= key_dist * 0.05:  # Within 5%
            score += 2.5
            feedback["total_distance_all_shipments"] = {"points": 2.5, "comment": "Close (within 5%)"}
        else:
            feedback["total_distance_all_shipments"] = {"points": 0, "comment": f"Incorrect. Expected: {key_dist}"}
    else:
        feedback["total_distance_all_shipments"] = {"points": 0, "comment": "Missing value"}
    
    return score, feedback

def evaluate_task3(submission, answer_key):
    score = 0
    feedback = {}
    
    # Carrier on-time rates
    sub_rates = submission.get("carrier_on_time_rates", {})
    key_rates = answer_key.get("carrier_on_time_rates", {})
    
    if sub_rates and key_rates:
        rate_score = 0
        rate_feedback = {}
        
        for carrier, key_rate in key_rates.items():
            sub_rate = sub_rates.get(carrier)
            if sub_rate is not None:
                if abs(sub_rate - key_rate) <= key_rate * 0.01:  # Within 1%
                    rate_score += 10/3  # 10 points divided by 3 carriers
                    rate_feedback[carrier] = {"points": round(10/3, 2), "comment": "Correct"}
                elif abs(sub_rate - key_rate) <= key_rate * 0.05:  # Within 5%
                    rate_score += 5/3  # 5 points divided by 3 carriers
                    rate_feedback[carrier] = {"points": round(5/3, 2), "comment": "Close (within 5%)"}
                else:
                    rate_feedback[carrier] = {"points": 0, "comment": f"Incorrect. Expected: {key_rate}"}
            else:
                rate_feedback[carrier] = {"points": 0, "comment": "Missing value"}
        
        score += min(10, rate_score)  # Cap at 10 points
        feedback["carrier_on_time_rates"] = rate_feedback
    else:
        feedback["carrier_on_time_rates"] = {"points": 0, "comment": "Missing values"}
    
    # Most efficient carrier
    sub_carrier = submission.get("most_efficient_carrier", "")
    key_carrier = answer_key.get("most_efficient_carrier", "")
    if sub_carrier == key_carrier:
        score += 5
        feedback["most_efficient_carrier"] = {"points": 5, "comment": "Correct"}
    else:
        feedback["most_efficient_carrier"] = {"points": 0, "comment": f"Incorrect. Expected: {key_carrier}"}
    
    # Efficiency score
    sub_score = submission.get("efficiency_score")
    key_score = answer_key.get("efficiency_score")
    if sub_score is not None and key_score is not None:
        if abs(sub_score - key_score) <= key_score * 0.01:  # Within 1%
            score += 5
            feedback["efficiency_score"] = {"points": 5, "comment": "Correct"}
        elif abs(sub_score - key_score) <= key_score * 0.05:  # Within 5%
            score += 2.5
            feedback["efficiency_score"] = {"points": 2.5, "comment": "Close (within 5%)"}
        else:
            feedback["efficiency_score"] = {"points": 0, "comment": f"Incorrect. Expected: {key_score}"}
    else:
        feedback["efficiency_score"] = {"points": 0, "comment": "Missing value"}
    
    return score, feedback

def evaluate_task4(submission, answer_key):
    score = 0
    feedback = {}
    
    # Monthly shipping costs
    sub_costs = submission.get("monthly_shipping_costs", [])
    key_costs = answer_key.get("monthly_shipping_costs", [])
    
    if len(sub_costs) == len(key_costs) == 12:
        month_score = 0
        month_feedback = {}
        
        for i, (sub_cost, key_cost) in enumerate(zip(sub_costs, key_costs)):
            month_name = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"][i]
            
            if abs(sub_cost - key_cost) <= key_cost * 0.01:  # Within 1%
                month_score += 1
                month_feedback[month_name] = {"points": 1, "comment": "Correct"}
            elif abs(sub_cost - key_cost) <= key_cost * 0.05:  # Within 5%
                month_score += 0.5
                month_feedback[month_name] = {"points": 0.5, "comment": "Close (within 5%)"}
            else:
                month_feedback[month_name] = {"points": 0, "comment": f"Incorrect. Expected: {key_cost}"}
        
        score += min(10, month_score)  # Cap at 10 points
        feedback["monthly_shipping_costs"] = month_feedback
    else:
        feedback["monthly_shipping_costs"] = {"points": 0, "comment": "Missing or incorrect number of values"}
    
    # Peak shipping month
    sub_peak = submission.get("peak_shipping_month", "")
    key_peak = answer_key.get("peak_shipping_month", "")
    if sub_peak == key_peak:
        score += 5
        feedback["peak_shipping_month"] = {"points": 5, "comment": "Correct"}
    else:
        feedback["peak_shipping_month"] = {"points": 0, "comment": f"Incorrect. Expected: {key_peak}"}
    
    # Lowest shipping month
    sub_lowest = submission.get("lowest_shipping_month", "")
    key_lowest = answer_key.get("lowest_shipping_month", "")
    if sub_lowest == key_lowest:
        score += 5
        feedback["lowest_shipping_month"] = {"points": 5, "comment": "Correct"}
    else:
        feedback["lowest_shipping_month"] = {"points": 0, "comment": f"Incorrect. Expected: {key_lowest}"}
    
    return score, feedback

def evaluate_task5(submission, answer_key):
    score = 0
    feedback = {}
    
    # Potential savings
    sub_savings = submission.get("potential_savings")
    key_savings = answer_key.get("potential_savings")
    if sub_savings is not None and key_savings is not None:
        # Special case for zero savings
        if key_savings == 0:
            if sub_savings == 0:
                score += 5
                feedback["potential_savings"] = {"points": 5, "comment": "Correct"}
            else:
                feedback["potential_savings"] = {"points": 0, "comment": f"Incorrect. Expected: {key_savings}"}
        else:
            if abs(sub_savings - key_savings) <= key_savings * 0.01:  # Within 1%
                score += 5
                feedback["potential_savings"] = {"points": 5, "comment": "Correct"}
            elif abs(sub_savings - key_savings) <= key_savings * 0.05:  # Within 5%
                score += 2.5
                feedback["potential_savings"] = {"points": 2.5, "comment": "Close (within 5%)"}
            else:
                feedback["potential_savings"] = {"points": 0, "comment": f"Incorrect. Expected: {key_savings}"}
    else:
        feedback["potential_savings"] = {"points": 0, "comment": "Missing value"}
    
    # Recommended carrier
    sub_carrier = submission.get("recommended_carrier", "")
    key_carrier = answer_key.get("recommended_carrier", "")
    
    # Split by comma for multiple carriers
    sub_carriers = set(c.strip() for c in sub_carrier.split(","))
    key_carriers = set(c.strip() for c in key_carrier.split(","))
    
    if sub_carriers == key_carriers:
        score += 5
        feedback["recommended_carrier"] = {"points": 5, "comment": "Correct"}
    elif any(c in key_carriers for c in sub_carriers):
        score += 2.5
        feedback["recommended_carrier"] = {"points": 2.5, "comment": "Partially correct"}
    else:
        feedback["recommended_carrier"] = {"points": 0, "comment": f"Incorrect. Expected: {key_carrier}"}
    
    return score, feedback

def evaluate_submission(submission, answer_key):
    results = {
        "task_scores": {},
        "detailed_feedback": {},
        "passing_criteria": {
            "minimum_score_required": 56,
            "minimum_task3_score_required": 10,
            "at_least_one_correct_per_task": True
        }
    }
    
    # Evaluate each task
    task1_score, task1_feedback = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    task2_score, task2_feedback = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    task3_score, task3_feedback = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    task4_score, task4_feedback = evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    task5_score, task5_feedback = evaluate_task5(submission.get("task5", {}), answer_key.get("task5", {}))
    
    # Store scores and feedback
    results["task_scores"] = {
        "task1": task1_score,
        "task2": task2_score,
        "task3": task3_score,
        "task4": task4_score,
        "task5": task5_score,
        "total": task1_score + task2_score + task3_score + task4_score + task5_score
    }
    
    results["detailed_feedback"] = {
        "task1": task1_feedback,
        "task2": task2_feedback,
        "task3": task3_feedback,
        "task4": task4_feedback,
        "task5": task5_feedback
    }
    
    # Calculate overall score as percentage
    total_possible = 80  # As per the evaluation criteria
    results["overall_score"] = round((results["task_scores"]["total"] / total_possible) * 100, 2)
    
    # Check passing criteria
    at_least_one_correct = all([
        any(item["points"] > 0 for item in task1_feedback.values()),
        any(item["points"] > 0 for item in task2_feedback.values()),
        any(item.get("points", 0) > 0 if isinstance(item, dict) else False for item in task3_feedback.values()),
        any(item.get("points", 0) > 0 if isinstance(item, dict) else False for item in task4_feedback.values()),
        any(item["points"] > 0 for item in task5_feedback.values())
    ])
    
    results["passing_criteria"]["at_least_one_correct_per_task_met"] = at_least_one_correct
    results["passing_criteria"]["minimum_score_met"] = results["task_scores"]["total"] >= 56
    results["passing_criteria"]["task3_minimum_met"] = task3_score >= 10
    
    results["passed"] = (results["task_scores"]["total"] >= 56 and 
                         task3_score >= 10 and 
                         at_least_one_correct)
    
    # Add candidate ID if available
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
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()