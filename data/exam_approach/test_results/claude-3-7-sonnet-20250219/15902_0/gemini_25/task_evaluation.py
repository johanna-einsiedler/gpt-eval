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

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "scores": {
            "on_time_delivery": {
                "overall_rate": 0,
                "monthly_rates": 0,
                "highest_lowest": 0,
                "total": 0
            },
            "order_fulfillment": {
                "overall_rate": 0,
                "category_rates": 0,
                "lowest_category": 0,
                "total": 0
            },
            "inventory_turns": {
                "average_turns": 0,
                "sku_turns": 0,
                "top_performers": 0,
                "total": 0
            }
        },
        "overall_score": 0,
        "details": {
            "on_time_delivery": {},
            "order_fulfillment": {},
            "inventory_turns": {}
        }
    }
    
    # Evaluate On-Time Delivery (30 points)
    # Overall rate (10 points)
    if abs(submission["on_time_delivery"]["overall_rate"] - answer_key["on_time_delivery"]["overall_rate"]) <= 0.01:
        results["scores"]["on_time_delivery"]["overall_rate"] = 10
    
    # Monthly rates (15 points, 3.75 points each)
    monthly_rate_score = 0
    monthly_rate_details = {}
    for month in ["Jan", "Feb", "Mar", "Apr"]:
        sub_rate = submission["on_time_delivery"]["monthly_rates"].get(month, 0)
        key_rate = answer_key["on_time_delivery"]["monthly_rates"].get(month, 0)
        is_correct = abs(sub_rate - key_rate) <= 0.01
        monthly_rate_details[month] = {
            "submitted": sub_rate,
            "expected": key_rate,
            "correct": is_correct
        }
        if is_correct:
            monthly_rate_score += 3.75
    
    results["scores"]["on_time_delivery"]["monthly_rates"] = monthly_rate_score
    results["details"]["on_time_delivery"]["monthly_rates"] = monthly_rate_details
    
    # Highest/lowest month (5 points)
    highest_correct = submission["on_time_delivery"]["highest_month"] == answer_key["on_time_delivery"]["highest_month"]
    lowest_correct = submission["on_time_delivery"]["lowest_month"] == answer_key["on_time_delivery"]["lowest_month"]
    
    if highest_correct and lowest_correct:
        results["scores"]["on_time_delivery"]["highest_lowest"] = 5
    
    results["details"]["on_time_delivery"]["highest_lowest"] = {
        "highest": {
            "submitted": submission["on_time_delivery"]["highest_month"],
            "expected": answer_key["on_time_delivery"]["highest_month"],
            "correct": highest_correct
        },
        "lowest": {
            "submitted": submission["on_time_delivery"]["lowest_month"],
            "expected": answer_key["on_time_delivery"]["lowest_month"],
            "correct": lowest_correct
        }
    }
    
    # Calculate total for on-time delivery
    results["scores"]["on_time_delivery"]["total"] = (
        results["scores"]["on_time_delivery"]["overall_rate"] +
        results["scores"]["on_time_delivery"]["monthly_rates"] +
        results["scores"]["on_time_delivery"]["highest_lowest"]
    )
    
    # Evaluate Order Fulfillment (30 points)
    # Overall rate (10 points)
    if abs(submission["order_fulfillment"]["overall_rate"] - answer_key["order_fulfillment"]["overall_rate"]) <= 0.01:
        results["scores"]["order_fulfillment"]["overall_rate"] = 10
    
    # Category rates (15 points, 5 points each)
    category_rate_score = 0
    category_rate_details = {}
    for category in ["Electronics", "Furniture", "Apparel"]:
        sub_rate = submission["order_fulfillment"]["category_rates"].get(category, 0)
        key_rate = answer_key["order_fulfillment"]["category_rates"].get(category, 0)
        is_correct = abs(sub_rate - key_rate) <= 0.01
        category_rate_details[category] = {
            "submitted": sub_rate,
            "expected": key_rate,
            "correct": is_correct
        }
        if is_correct:
            category_rate_score += 5
    
    results["scores"]["order_fulfillment"]["category_rates"] = category_rate_score
    results["details"]["order_fulfillment"]["category_rates"] = category_rate_details
    
    # Lowest category (5 points)
    lowest_category_correct = submission["order_fulfillment"]["lowest_category"] == answer_key["order_fulfillment"]["lowest_category"]
    if lowest_category_correct:
        results["scores"]["order_fulfillment"]["lowest_category"] = 5
    
    results["details"]["order_fulfillment"]["lowest_category"] = {
        "submitted": submission["order_fulfillment"]["lowest_category"],
        "expected": answer_key["order_fulfillment"]["lowest_category"],
        "correct": lowest_category_correct
    }
    
    # Calculate total for order fulfillment
    results["scores"]["order_fulfillment"]["total"] = (
        results["scores"]["order_fulfillment"]["overall_rate"] +
        results["scores"]["order_fulfillment"]["category_rates"] +
        results["scores"]["order_fulfillment"]["lowest_category"]
    )
    
    # Evaluate Inventory Turns (40 points)
    # Average turns (10 points)
    if abs(submission["inventory_turns"]["average_turns"] - answer_key["inventory_turns"]["average_turns"]) <= 0.01:
        results["scores"]["inventory_turns"]["average_turns"] = 10
    
    # SKU turns (20 points, ~3.33 points each)
    sku_turns_score = 0
    sku_turns_details = {}
    
    # Check if sku_turns exists in submission
    if "sku_turns" in submission["inventory_turns"]:
        for sku in ["E001", "E002", "F001", "F002", "A001", "A002"]:
            sub_turn = submission["inventory_turns"]["sku_turns"].get(sku, 0)
            key_turn = answer_key["inventory_turns"]["sku_turns"].get(sku, 0)
            is_correct = abs(sub_turn - key_turn) <= 0.05  # Allowing a margin of ±0.05
            sku_turns_details[sku] = {
                "submitted": sub_turn,
                "expected": key_turn,
                "correct": is_correct
            }
            if is_correct:
                sku_turns_score += 3.33
    
    results["scores"]["inventory_turns"]["sku_turns"] = min(20, sku_turns_score)  # Cap at 20 points
    results["details"]["inventory_turns"]["sku_turns"] = sku_turns_details
    
    # Top performers (10 points)
    top_performers_correct = submission["inventory_turns"]["top_performers"] == answer_key["inventory_turns"]["top_performers"]
    if top_performers_correct:
        results["scores"]["inventory_turns"]["top_performers"] = 10
    
    results["details"]["inventory_turns"]["top_performers"] = {
        "submitted": submission["inventory_turns"]["top_performers"],
        "expected": answer_key["inventory_turns"]["top_performers"],
        "correct": top_performers_correct
    }
    
    # Calculate total for inventory turns
    results["scores"]["inventory_turns"]["total"] = (
        results["scores"]["inventory_turns"]["average_turns"] +
        results["scores"]["inventory_turns"]["sku_turns"] +
        results["scores"]["inventory_turns"]["top_performers"]
    )
    
    # Calculate overall score (out of 100)
    overall_score = (
        results["scores"]["on_time_delivery"]["total"] +
        results["scores"]["order_fulfillment"]["total"] +
        results["scores"]["inventory_turns"]["total"]
    )
    
    results["overall_score"] = round(overall_score, 2)
    results["pass"] = overall_score >= 80
    
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
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['pass'] else 'FAIL'}")
    print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()