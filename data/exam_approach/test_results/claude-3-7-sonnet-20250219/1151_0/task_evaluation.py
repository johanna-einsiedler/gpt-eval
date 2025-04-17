#!/usr/bin/env python3
"""
Evaluates a candidate's purchasing agent exam submission against an answer key.
Usage: python task_evaluation.py test_submission.json answer_key.json
"""

import sys
import json
import os
from typing import Dict, List, Any, Tuple

def load_json(filename: str) -> Dict:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def check_list_match(candidate_list: List, answer_list: List) -> Tuple[float, int, List]:
    """
    Compare candidate list with answer list and return percentage match,
    number of correct items, and missing items.
    """
    if not answer_list:
        return 1.0, 0, []
    
    correct_items = [item for item in candidate_list if item in answer_list]
    correct_count = len(correct_items)
    missing_items = [item for item in answer_list if item not in candidate_list]
    
    # Calculate percentage of correct items
    percentage = correct_count / len(answer_list) if answer_list else 1.0
    
    return percentage, correct_count, missing_items

def check_numerical_value(candidate_value: float, answer_value: float) -> float:
    """
    Compare candidate's numerical value with answer value and return score.
    Full points if within 1%, half points if within 5%, zero otherwise.
    """
    if answer_value == 0:  # Avoid division by zero
        return 1.0 if candidate_value == 0 else 0.0
    
    percentage_diff = abs((candidate_value - answer_value) / answer_value)
    
    if percentage_diff <= 0.01:  # Within 1%
        return 1.0
    elif percentage_diff <= 0.05:  # Within 5%
        return 0.5
    else:
        return 0.0

def evaluate_inventory_analysis(candidate: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the inventory analysis section of the submission."""
    score = 0
    details = {}
    
    # Items below threshold (10 points)
    candidate_items = candidate.get("items_below_threshold", [])
    answer_items = answer_key.get("items_below_threshold", [])
    percentage, correct_count, missing = check_list_match(candidate_items, answer_items)
    points = 10 * percentage
    score += points
    details["items_below_threshold"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_items),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_items)} items correctly"
    }
    
    # Items requiring reorder (10 points)
    candidate_items = candidate.get("items_requiring_reorder", [])
    answer_items = answer_key.get("items_requiring_reorder", [])
    percentage, correct_count, missing = check_list_match(candidate_items, answer_items)
    points = 10 * percentage
    score += points
    details["items_requiring_reorder"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_items),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_items)} items correctly"
    }
    
    # Current inventory levels (10 points)
    candidate_levels = candidate.get("current_inventory_levels", {})
    answer_levels = answer_key.get("current_inventory_levels", {})
    
    inventory_score = 0
    inventory_details = {}
    
    for category, answer_value in answer_levels.items():
        candidate_value = candidate_levels.get(category, 0)
        category_score = check_numerical_value(candidate_value, answer_value)
        inventory_score += category_score * (10 / len(answer_levels))
        
        inventory_details[category] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "score": category_score,
            "comments": "Correct" if category_score == 1.0 else 
                       "Within 5% margin" if category_score == 0.5 else 
                       "Incorrect"
        }
    
    score += inventory_score
    details["current_inventory_levels"] = {
        "score": inventory_score,
        "max_points": 10,
        "category_details": inventory_details,
        "comments": "Inventory levels analysis"
    }
    
    return score, details

def evaluate_vendor_performance(candidate: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the vendor performance section of the submission."""
    score = 0
    details = {}
    
    # Top vendors (10 points)
    candidate_vendors = candidate.get("top_vendors", [])
    answer_vendors = answer_key.get("top_vendors", [])
    percentage, correct_count, missing = check_list_match(candidate_vendors, answer_vendors)
    points = 10 * percentage
    score += points
    details["top_vendors"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_vendors),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_vendors)} top vendors correctly"
    }
    
    # Bottom vendors (10 points)
    candidate_vendors = candidate.get("bottom_vendors", [])
    answer_vendors = answer_key.get("bottom_vendors", [])
    percentage, correct_count, missing = check_list_match(candidate_vendors, answer_vendors)
    points = 10 * percentage
    score += points
    details["bottom_vendors"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_vendors),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_vendors)} bottom vendors correctly"
    }
    
    # Delivery metrics (20 points: 6 for on-time, 7 for delivery days, 7 for defect rate)
    candidate_metrics = candidate.get("avg_delivery_metrics", {})
    answer_metrics = answer_key.get("avg_delivery_metrics", {})
    
    on_time_score = 0
    delivery_days_score = 0
    defect_rate_score = 0
    metrics_details = {}
    
    for vendor_id, answer_values in answer_metrics.items():
        vendor_details = {}
        candidate_values = candidate_metrics.get(vendor_id, {})
        
        # On-time rate (6 points)
        candidate_on_time = candidate_values.get("on_time_rate", 0)
        answer_on_time = answer_values.get("on_time_rate", 0)
        on_time_score_vendor = check_numerical_value(candidate_on_time, answer_on_time)
        on_time_score += on_time_score_vendor * (6 / len(answer_metrics))
        
        vendor_details["on_time_rate"] = {
            "candidate_value": candidate_on_time,
            "correct_value": answer_on_time,
            "score": on_time_score_vendor,
            "comments": "Correct" if on_time_score_vendor == 1.0 else 
                       "Within 5% margin" if on_time_score_vendor == 0.5 else 
                       "Incorrect"
        }
        
        # Avg delivery days (7 points)
        candidate_days = candidate_values.get("avg_delivery_days", 0)
        answer_days = answer_values.get("avg_delivery_days", 0)
        days_score_vendor = check_numerical_value(candidate_days, answer_days)
        delivery_days_score += days_score_vendor * (7 / len(answer_metrics))
        
        vendor_details["avg_delivery_days"] = {
            "candidate_value": candidate_days,
            "correct_value": answer_days,
            "score": days_score_vendor,
            "comments": "Correct" if days_score_vendor == 1.0 else 
                       "Within 5% margin" if days_score_vendor == 0.5 else 
                       "Incorrect"
        }
        
        # Defect rate (7 points)
        candidate_defect = candidate_values.get("defect_rate", 0)
        answer_defect = answer_values.get("defect_rate", 0)
        defect_score_vendor = check_numerical_value(candidate_defect, answer_defect)
        defect_rate_score += defect_score_vendor * (7 / len(answer_metrics))
        
        vendor_details["defect_rate"] = {
            "candidate_value": candidate_defect,
            "correct_value": answer_defect,
            "score": defect_score_vendor,
            "comments": "Correct" if defect_score_vendor == 1.0 else 
                       "Within 5% margin" if defect_score_vendor == 0.5 else 
                       "Incorrect"
        }
        
        metrics_details[vendor_id] = vendor_details
    
    score += on_time_score + delivery_days_score + defect_rate_score
    
    details["avg_delivery_metrics"] = {
        "on_time_rate_score": on_time_score,
        "on_time_rate_max": 6,
        "avg_delivery_days_score": delivery_days_score,
        "avg_delivery_days_max": 7,
        "defect_rate_score": defect_rate_score,
        "defect_rate_max": 7,
        "vendor_details": metrics_details,
        "comments": "Vendor delivery metrics analysis"
    }
    
    return score, details

def evaluate_cost_analysis(candidate: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the cost analysis section of the submission."""
    score = 0
    details = {}
    
    # Highest cost products (10 points)
    candidate_products = candidate.get("highest_cost_products", [])
    answer_products = answer_key.get("highest_cost_products", [])
    percentage, correct_count, missing = check_list_match(candidate_products, answer_products)
    points = 10 * percentage
    score += points
    details["highest_cost_products"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_products),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_products)} highest cost products correctly"
    }
    
    # Products with price increases (10 points)
    candidate_products = candidate.get("products_with_price_increases", [])
    answer_products = answer_key.get("products_with_price_increases", [])
    percentage, correct_count, missing = check_list_match(candidate_products, answer_products)
    points = 10 * percentage
    score += points
    details["products_with_price_increases"] = {
        "score": points,
        "max_points": 10,
        "correct_count": correct_count,
        "total_count": len(answer_products),
        "missing_items": missing,
        "comments": f"Identified {correct_count}/{len(answer_products)} products with price increases correctly"
    }
    
    # Total monthly spend (10 points)
    candidate_spend = candidate.get("total_monthly_spend", {})
    answer_spend = answer_key.get("total_monthly_spend", {})
    
    spend_score = 0
    spend_details = {}
    
    for month, answer_value in answer_spend.items():
        candidate_value = candidate_spend.get(month, 0)
        month_score = check_numerical_value(candidate_value, answer_value)
        spend_score += month_score * (10 / len(answer_spend))
        
        spend_details[month] = {
            "candidate_value": candidate_value,
            "correct_value": answer_value,
            "score": month_score,
            "comments": "Correct" if month_score == 1.0 else 
                       "Within 5% margin" if month_score == 0.5 else 
                       "Incorrect"
        }
    
    score += spend_score
    details["total_monthly_spend"] = {
        "score": spend_score,
        "max_points": 10,
        "month_details": spend_details,
        "comments": "Monthly spending analysis"
    }
    
    return score, details

def evaluate_submission(candidate: Dict, answer_key: Dict) -> Dict:
    """Evaluate the full candidate submission against the answer key."""
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "section_scores": {},
        "detailed_feedback": {}
    }
    
    total_score = 0
    
    # Evaluate inventory analysis (30 points)
    inventory_score, inventory_details = evaluate_inventory_analysis(
        candidate.get("inventory_analysis", {}),
        answer_key.get("inventory_analysis", {})
    )
    total_score += inventory_score
    results["section_scores"]["inventory_analysis"] = {
        "score": inventory_score,
        "max_points": 30,
        "percentage": (inventory_score / 30) * 100
    }
    results["detailed_feedback"]["inventory_analysis"] = inventory_details
    
    # Evaluate vendor performance (40 points)
    vendor_score, vendor_details = evaluate_vendor_performance(
        candidate.get("vendor_performance", {}),
        answer_key.get("vendor_performance", {})
    )
    total_score += vendor_score
    results["section_scores"]["vendor_performance"] = {
        "score": vendor_score,
        "max_points": 40,
        "percentage": (vendor_score / 40) * 100
    }
    results["detailed_feedback"]["vendor_performance"] = vendor_details
    
    # Evaluate cost analysis (30 points)
    cost_score, cost_details = evaluate_cost_analysis(
        candidate.get("cost_analysis", {}),
        answer_key.get("cost_analysis", {})
    )
    total_score += cost_score
    results["section_scores"]["cost_analysis"] = {
        "score": cost_score,
        "max_points": 30,
        "percentage": (cost_score / 30) * 100
    }
    results["detailed_feedback"]["cost_analysis"] = cost_details
    
    # Calculate overall score
    overall_percentage = (total_score / 100) * 100
    results["overall_score"] = overall_percentage
    
    # Determine performance level
    if overall_percentage >= 90:
        performance = "Excellent"
    elif overall_percentage >= 80:
        performance = "Good"
    elif overall_percentage >= 70:
        performance = "Satisfactory"
    elif overall_percentage >= 60:
        performance = "Needs Improvement"
    else:
        performance = "Unsatisfactory"
    
    results["performance_level"] = performance
    results["pass_fail"] = "Pass" if overall_percentage >= 70 else "Fail"
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", 'w') as outfile:
        json.dump(results, outfile, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.1f}%. Results saved to test_results.json")

if __name__ == "__main__":
    main()