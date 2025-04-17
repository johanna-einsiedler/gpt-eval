#!/usr/bin/env python3
"""
Task Evaluation Script for Farm Product Buyers and Purchasing Agents Exam

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from collections import defaultdict

def load_json_file(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON.")
        sys.exit(1)

def evaluate_top_products(submission, answer_key):
    """Evaluate the top products section."""
    correct_products = {item["product_id"]: item["sales_volume"] for item in answer_key["top_products"]}
    submitted_products = {item["product_id"]: item["sales_volume"] for item in submission.get("top_products", [])}
    
    # Count correct products (within 5% of correct sales volume)
    correct_count = 0
    for product_id, expected_volume in correct_products.items():
        if product_id in submitted_products:
            submitted_volume = submitted_products[product_id]
            # Check if within 5% of correct value
            if abs(submitted_volume - expected_volume) <= 0.05 * expected_volume:
                correct_count += 1
    
    max_score = 20
    score = (correct_count / 5) * max_score
    
    return {
        "score": score,
        "max_score": max_score,
        "details": {
            "correct_products": correct_count,
            "total_products": 5,
            "percentage": (correct_count / 5) * 100
        }
    }

def evaluate_inventory_below_threshold(submission, answer_key):
    """Evaluate the inventory below threshold section."""
    correct_items = {item["product_id"] for item in answer_key["inventory_below_threshold"]}
    submitted_items = {item["product_id"] for item in submission.get("inventory_below_threshold", [])}
    
    true_positives = len(correct_items.intersection(submitted_items))
    false_positives = len(submitted_items - correct_items)
    
    max_score = 20
    # Score based on true positives and penalize for false positives
    score = min(max_score, 
                ((true_positives / len(correct_items)) * 0.7 * max_score) + 
                (max(0, (1 - (false_positives / max(1, len(submitted_items)))) * 0.3 * max_score)))
    
    return {
        "score": score,
        "max_score": max_score,
        "details": {
            "correctly_identified": true_positives,
            "total_items_below_threshold": len(correct_items),
            "false_positives": false_positives
        }
    }

def evaluate_unfulfillable_orders(submission, answer_key):
    """Evaluate the unfulfillable orders section."""
    correct_orders = {item["order_id"] + "-" + item["product_id"]: item["shortage"] 
                    for item in answer_key["unfulfillable_orders"]}
    submitted_orders = {item["order_id"] + "-" + item["product_id"]: item["shortage"] 
                      for item in submission.get("unfulfillable_orders", [])}
    
    correct_count = 0
    for order_key, expected_shortage in correct_orders.items():
        if order_key in submitted_orders:
            submitted_shortage = submitted_orders[order_key]
            # Check if within 10% of correct shortage
            if abs(submitted_shortage - expected_shortage) <= 0.1 * expected_shortage:
                correct_count += 1
    
    max_score = 20
    score = (correct_count / len(correct_orders)) * max_score
    
    return {
        "score": score,
        "max_score": max_score,
        "details": {
            "correctly_identified": correct_count,
            "total_unfulfillable_orders": len(correct_orders),
            "percentage": (correct_count / len(correct_orders)) * 100
        }
    }

def evaluate_purchase_recommendations(submission, answer_key):
    """Evaluate the purchase recommendations section."""
    correct_recs = {item["product_id"]: item for item in answer_key["purchase_recommendations"]}
    submitted_recs = {item["product_id"]: item for item in submission.get("purchase_recommendations", [])}
    
    # Check quantities are within 15% of optimal
    quantity_correct = 0
    for product_id, correct_item in correct_recs.items():
        if product_id in submitted_recs:
            submitted_item = submitted_recs[product_id]
            correct_quantity = correct_item["purchase_quantity"]
            submitted_quantity = submitted_item["purchase_quantity"]
            
            if abs(submitted_quantity - correct_quantity) <= 0.15 * correct_quantity:
                quantity_correct += 1
    
    # Check supplier selections
    supplier_correct = 0
    for product_id, correct_item in correct_recs.items():
        if product_id in submitted_recs:
            submitted_item = submitted_recs[product_id]
            if submitted_item["supplier_id"] == correct_item["supplier_id"]:
                supplier_correct += 1
    
    # Check total purchase cost is within 15% of optimal
    correct_total = answer_key["total_purchase_cost"]
    submitted_total = submission.get("total_purchase_cost", 0)
    total_cost_correct = abs(submitted_total - correct_total) <= 0.15 * correct_total
    
    max_score = 30
    # Calculate score based on criteria weights
    quantity_score = (quantity_correct / len(correct_recs)) * 0.4 * max_score
    supplier_score = (supplier_correct / len(correct_recs)) * 0.4 * max_score
    cost_score = total_cost_correct * 0.2 * max_score
    
    score = quantity_score + supplier_score + cost_score
    
    return {
        "score": score,
        "max_score": max_score,
        "details": {
            "products_with_correct_quantity": quantity_correct,
            "products_with_correct_supplier": supplier_correct,
            "total_purchase_cost_correct": total_cost_correct,
            "total_products_requiring_purchase": len(correct_recs)
        }
    }

def evaluate_format_completeness(submission, answer_key):
    """Evaluate the format and completeness of the submission."""
    max_score = 10
    score = max_score  # Start with full score and deduct as needed
    
    details = {
        "valid_json": True,
        "all_required_fields_present": True,
        "proper_units_specified": True,
        "supplier_explanations_provided": True,
        "deductions": []
    }
    
    # Check for required top-level fields
    required_fields = ["top_products", "inventory_below_threshold", 
                       "unfulfillable_orders", "purchase_recommendations", 
                       "total_purchase_cost"]
    
    for field in required_fields:
        if field not in submission:
            details["all_required_fields_present"] = False
            details["deductions"].append(f"Missing required field: {field}")
            score -= 2  # Deduct 2 points for each missing field
    
    # Check for proper units in applicable fields
    if "purchase_recommendations" in submission:
        for item in submission["purchase_recommendations"]:
            if "units" not in item:
                details["proper_units_specified"] = False
                details["deductions"].append("Missing units in purchase recommendations")
                score -= 1
                break
    
    if "unfulfillable_orders" in submission:
        for item in submission["unfulfillable_orders"]:
            if "units" not in item:
                details["proper_units_specified"] = False
                details["deductions"].append("Missing units in unfulfillable orders")
                score -= 1
                break
    
    # Check for supplier explanations
    if "purchase_recommendations" in submission:
        for item in submission["purchase_recommendations"]:
            if "reason" not in item or not item["reason"]:
                details["supplier_explanations_provided"] = False
                details["deductions"].append("Missing supplier explanations")
                score -= 2
                break
    
    return {
        "score": max(0, score),  # Ensure score doesn't go below 0
        "max_score": max_score,
        "details": details
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the complete submission against the answer key."""
    results = {
        "top_products": evaluate_top_products(submission, answer_key),
        "inventory_below_threshold": evaluate_inventory_below_threshold(submission, answer_key),
        "unfulfillable_orders": evaluate_unfulfillable_orders(submission, answer_key),
        "purchase_recommendations": evaluate_purchase_recommendations(submission, answer_key),
        "format_completeness": evaluate_format_completeness(submission, answer_key)
    }
    
    # Calculate overall score
    total_score = sum(section["score"] for section in results.values())
    total_possible = sum(section["max_score"] for section in results.values())
    overall_percentage = (total_score / total_possible) * 100
    
    results["overall_score"] = round(overall_percentage, 2)
    results["passing_threshold"] = 70.0
    results["passed"] = overall_percentage >= 70.0
    
    return results

def main():
    """Main function to run the evaluation."""
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
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()