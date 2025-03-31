import json
import os
from datetime import datetime

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json_file(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Order Analysis"""
    results = {
        "points_possible": 25,
        "points_earned": 0,
        "breakdown": {
            "top_5_products": {"points_possible": 10, "points_earned": 0},
            "average_monthly_demand": {"points_possible": 5, "points_earned": 0},
            "seasonal_patterns": {"points_possible": 10, "points_earned": 0}
        }
    }
    
    # Evaluate top 5 products by volume (10 points)
    top5_score = 0
    top5_details = {}
    
    for month in answer_key["task1_order_analysis"]["top_5_products_by_volume"]:
        correct_products = answer_key["task1_order_analysis"]["top_5_products_by_volume"][month]
        submitted_products = submission["task1_order_analysis"]["top_5_products_by_volume"].get(month, [])
        
        # Calculate overlap
        correct_set = set(correct_products)
        submitted_set = set(submitted_products)
        overlap = len(correct_set.intersection(submitted_set))
        
        month_score = (overlap / 5) * (10/6)  # 10 points divided by 6 months
        top5_score += month_score
        
        top5_details[month] = {
            "correct_products": correct_products,
            "submitted_products": submitted_products,
            "overlap": overlap,
            "points_earned": round(month_score, 2)
        }
    
    results["breakdown"]["top_5_products"]["points_earned"] = round(top5_score, 2)
    results["breakdown"]["top_5_products"]["details"] = top5_details
    
    # Evaluate average monthly demand (5 points)
    avg_demand_score = 0
    avg_demand_details = {}
    
    for category in answer_key["task1_order_analysis"]["average_monthly_demand"]:
        correct_value = answer_key["task1_order_analysis"]["average_monthly_demand"][category]
        submitted_value = submission["task1_order_analysis"]["average_monthly_demand"].get(category, 0)
        
        # Check if within 5% tolerance
        is_correct = abs(submitted_value - correct_value) <= correct_value * 0.05
        category_score = 5 / len(answer_key["task1_order_analysis"]["average_monthly_demand"]) if is_correct else 0
        avg_demand_score += category_score
        
        avg_demand_details[category] = {
            "correct_value": correct_value,
            "submitted_value": submitted_value,
            "within_tolerance": is_correct,
            "points_earned": round(category_score, 2)
        }
    
    results["breakdown"]["average_monthly_demand"]["points_earned"] = round(avg_demand_score, 2)
    results["breakdown"]["average_monthly_demand"]["details"] = avg_demand_details
    
    # Evaluate seasonal patterns (10 points)
    seasonal_score = 0
    seasonal_details = {}
    
    key_terms = ["increase", "decrease", "stable", "peak", "seasonal", "summer", "winter", "spring", "fall"]
    
    for product in answer_key["task1_order_analysis"]["seasonal_patterns"]:
        correct_pattern = answer_key["task1_order_analysis"]["seasonal_patterns"][product].lower()
        submitted_pattern = submission["task1_order_analysis"]["seasonal_patterns"].get(product, "").lower()
        
        # Extract key terms matches
        term_matches = sum(1 for term in key_terms if (term in correct_pattern and term in submitted_pattern))
        product_score = min(1.0, term_matches / 3) * (10 / len(answer_key["task1_order_analysis"]["seasonal_patterns"]))
        seasonal_score += product_score
        
        seasonal_details[product] = {
            "term_matches": term_matches,
            "points_earned": round(product_score, 2)
        }
    
    results["breakdown"]["seasonal_patterns"]["points_earned"] = round(seasonal_score, 2)
    results["breakdown"]["seasonal_patterns"]["details"] = seasonal_details
    
    # Calculate total points for Task 1
    results["points_earned"] = round(top5_score + avg_demand_score + seasonal_score, 2)
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Inventory Assessment"""
    results = {
        "points_possible": 15,
        "points_earned": 0,
        "breakdown": {
            "product_identification": {"points_possible": 5, "points_earned": 0},
            "shortage_quantities": {"points_possible": 10, "points_earned": 0}
        }
    }
    
    # Get sets of product codes for comparison
    correct_products = {item["product_code"] for item in answer_key["task2_inventory_assessment"]["products_with_insufficient_inventory"]}
    submitted_products = {item["product_code"] for item in submission["task2_inventory_assessment"].get("products_with_insufficient_inventory", [])}
    
    # Evaluate product identification (5 points)
    overlap = correct_products.intersection(submitted_products)
    identification_score = len(overlap) / len(correct_products) * 5 if correct_products else 0
    
    results["breakdown"]["product_identification"]["points_earned"] = round(identification_score, 2)
    results["breakdown"]["product_identification"]["details"] = {
        "correct_products": list(correct_products),
        "submitted_products": list(submitted_products),
        "correctly_identified": list(overlap),
        "missed_products": list(correct_products - submitted_products),
        "extra_products": list(submitted_products - correct_products)
    }
    
    # Evaluate shortage quantities (10 points)
    shortage_score = 0
    shortage_details = {}
    
    # Create a dictionary for quick lookup of correct shortage quantities
    correct_shortages = {item["product_code"]: item["shortage_quantity"] 
                         for item in answer_key["task2_inventory_assessment"]["products_with_insufficient_inventory"]}
    
    for submitted_item in submission["task2_inventory_assessment"].get("products_with_insufficient_inventory", []):
        product_code = submitted_item.get("product_code", "")
        
        if product_code in correct_products:
            correct_shortage = correct_shortages.get(product_code, 0)
            submitted_shortage = submitted_item.get("shortage_quantity", 0)
            
            is_correct = submitted_shortage == correct_shortage
            item_score = 10 / len(correct_products) if is_correct else 0
            shortage_score += item_score
            
            shortage_details[product_code] = {
                "correct_shortage": correct_shortage,
                "submitted_shortage": submitted_shortage,
                "is_correct": is_correct,
                "points_earned": round(item_score, 2)
            }
    
    results["breakdown"]["shortage_quantities"]["points_earned"] = round(shortage_score, 2)
    results["breakdown"]["shortage_quantities"]["details"] = shortage_details
    
    # Calculate total points for Task 2
    results["points_earned"] = round(identification_score + shortage_score, 2)
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Purchase Planning"""
    results = {
        "points_possible": 30,
        "points_earned": 0,
        "breakdown": {
            "purchase_recommendations": {"points_possible": 15, "points_earned": 0},
            "budget_compliance": {"points_possible": 5, "points_earned": 0},
            "storage_compliance": {"points_possible": 10, "points_earned": 0}
        }
    }
    
    # Evaluate purchase recommendations (15 points)
    purchase_score = 0
    purchase_details = {}
    
    # Get sets of product codes for comparison
    correct_purchases = {item["product_code"] for item in answer_key["task3_purchase_planning"]["recommended_purchases"]}
    submitted_purchases = {item["product_code"] for item in submission["task3_purchase_planning"].get("recommended_purchases", [])}
    
    # Check if all required products are included (5 points)
    overlap = correct_purchases.intersection(submitted_purchases)
    products_included_score = len(overlap) / len(correct_purchases) * 5 if correct_purchases else 0
    
    purchase_details["product_coverage"] = {
        "correct_products": list(correct_purchases),
        "submitted_products": list(submitted_purchases),
        "correctly_included": list(overlap),
        "missed_products": list(correct_purchases - submitted_purchases),
        "extra_products": list(submitted_purchases - correct_purchases),
        "points_earned": round(products_included_score, 2)
    }
    
    # Create dictionaries for quick lookups
    correct_shortages = {item["product_code"]: item["shortage_quantity"] 
                         for item in answer_key["task2_inventory_assessment"]["products_with_insufficient_inventory"]}
    
    # Get supplier information from the answer key's recommended purchases
    supplier_info = {}
    for item in answer_key["task3_purchase_planning"]["recommended_purchases"]:
        supplier_info[item["product_code"]] = {
            "supplier_id": item["supplier_id"],
            "min_order_qty": 0  # This would need to be extracted from the materials
        }
    
    # Check if quantities meet requirements (10 points)
    quantity_score = 0
    quantity_details = {}
    
    for submitted_item in submission["task3_purchase_planning"].get("recommended_purchases", []):
        product_code = submitted_item.get("product_code", "")
        
        if product_code in correct_purchases:
            shortage = correct_shortages.get(product_code, 0)
            purchase_qty = submitted_item.get("purchase_quantity", 0)
            
            # Check if quantity covers shortage (5 points)
            covers_shortage = purchase_qty >= shortage
            shortage_score = 5 / len(correct_purchases) if covers_shortage else 0
            
            # Check if supplier and minimum order quantity are appropriate (5 points)
            # For simplicity, we'll just check if a supplier was specified
            has_supplier = bool(submitted_item.get("supplier_id", ""))
            supplier_score = 5 / len(correct_purchases) if has_supplier else 0
            
            item_score = shortage_score + supplier_score
            quantity_score += item_score
            
            quantity_details[product_code] = {
                "required_shortage_coverage": shortage,
                "submitted_purchase_quantity": purchase_qty,
                "covers_shortage": covers_shortage,
                "has_valid_supplier": has_supplier,
                "points_earned": round(item_score, 2)
            }
    
    purchase_score = products_included_score + quantity_score
    results["breakdown"]["purchase_recommendations"]["points_earned"] = round(purchase_score, 2)
    results["breakdown"]["purchase_recommendations"]["details"] = {
        "product_coverage": purchase_details["product_coverage"],
        "quantity_requirements": quantity_details
    }
    
    # Evaluate budget compliance (5 points)
    budget_score = 0
    budget_details = {}
    
    submitted_budget_compliance = submission["task3_purchase_planning"].get("budget_analysis", {}).get("budget_compliance", False)
    submitted_total_cost = submission["task3_purchase_planning"].get("budget_analysis", {}).get("total_purchase_cost", 0)
    budget_allocation = answer_key["task3_purchase_planning"]["budget_analysis"]["budget_allocation"]
    
    is_within_budget = submitted_total_cost <= budget_allocation
    budget_score = 5 if submitted_budget_compliance and is_within_budget else 0
    
    budget_details = {
        "submitted_total_cost": submitted_total_cost,
        "budget_allocation": budget_allocation,
        "is_within_budget": is_within_budget,
        "claimed_compliance": submitted_budget_compliance,
        "actual_compliance": is_within_budget,
        "points_earned": budget_score
    }
    
    results["breakdown"]["budget_compliance"]["points_earned"] = budget_score
    results["breakdown"]["budget_compliance"]["details"] = budget_details
    
    # Evaluate storage compliance (10 points)
    storage_score = 0
    storage_details = {}
    
    for location, correct_data in answer_key["task3_purchase_planning"]["storage_analysis"].items():
        submitted_data = submission["task3_purchase_planning"].get("storage_analysis", {}).get(location, {})
        
        submitted_compliance = submitted_data.get("capacity_compliance", False)
        submitted_total = submitted_data.get("total_capacity_after_purchases_kg", 0)
        max_capacity = correct_data["total_capacity_kg"]
        
        is_within_capacity = submitted_total <= max_capacity
        location_score = 10 / len(answer_key["task3_purchase_planning"]["storage_analysis"]) if submitted_compliance and is_within_capacity else 0
        storage_score += location_score
        
        storage_details[location] = {
            "submitted_total_after_purchases": submitted_total,
            "maximum_capacity": max_capacity,
            "is_within_capacity": is_within_capacity,
            "claimed_compliance": submitted_compliance,
            "actual_compliance": is_within_capacity,
            "points_earned": round(location_score, 2)
        }
    
    results["breakdown"]["storage_compliance"]["points_earned"] = round(storage_score, 2)
    results["breakdown"]["storage_compliance"]["details"] = storage_details
    
    # Calculate total points for Task 3
    results["points_earned"] = round(purchase_score + budget_score + storage_score, 2)
    
    return results

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Priority Assessment"""
    results = {
        "points_possible": 15,
        "points_earned": 0,
        "breakdown": {
            "priority_ranking": {"points_possible": 15, "points_earned": 0}
        }
    }
    
    # This is a more subjective assessment, so we'll use a simplified approach
    # We'll check if high priority items from the answer key are also ranked highly in the submission
    
    # Extract product codes and ranks from both answer key and submission
    correct_rankings = {}
    for item in answer_key["task4_priority_assessment"]["priority_ranking"]:
        correct_rankings[item["product_code"]] = item["rank"]
    
    submitted_rankings = {}
    for item in submission.get("task4_priority_assessment", {}).get("priority_ranking", []):
        submitted_rankings[item.get("product_code", "")] = item.get("rank", 999)
    
    # Calculate a score based on how closely the rankings match
    # We'll focus on the top 5 priority items from the answer key
    top_priority_items = sorted(correct_rankings.items(), key=lambda x: x[1])[:5]
    
    ranking_score = 0
    ranking_details = {}
    
    for product_code, correct_rank in top_priority_items:
        if product_code in submitted_rankings:
            submitted_rank = submitted_rankings[product_code]
            
            # Calculate a score based on rank difference
            # Perfect match gets full points, larger differences get fewer points
            rank_diff = abs(correct_rank - submitted_rank)
            item_score = 3 * max(0, 1 - (rank_diff / 5))  # 3 points per item, scaled by difference
            ranking_score += item_score
            
            ranking_details[product_code] = {
                "correct_rank": correct_rank,
                "submitted_rank": submitted_rank,
                "rank_difference": rank_diff,
                "points_earned": round(item_score, 2)
            }
        else:
            ranking_details[product_code] = {
                "correct_rank": correct_rank,
                "submitted_rank": "Not ranked",
                "rank_difference": "N/A",
                "points_earned": 0
            }
    
    results["breakdown"]["priority_ranking"]["points_earned"] = round(ranking_score, 2)
    results["breakdown"]["priority_ranking"]["details"] = ranking_details
    
    # Calculate total points for Task 4
    results["points_earned"] = round(ranking_score, 2)
    
    return results

def evaluate_task5(submission, answer_key):
    """Evaluate Task 5: Documentation"""
    results = {
        "points_possible": 15,
        "points_earned": 0,
        "breakdown": {
            "top_priority_justifications": {"points_possible": 10, "points_earned": 0},
            "seasonal_adjustments": {"points_possible": 5, "points_earned": 0}
        }
    }
    
    # Evaluate top priority justifications (10 points)
    justification_score = 0
    justification_details = {}
    
    correct_justifications = answer_key["task5_documentation"]["top_priority_justifications"]
    submitted_justifications = submission.get("task5_documentation", {}).get("top_priority_justifications", {})
    
    # Key terms that should be present in justifications
    key_terms = ["inventory", "shortage", "lead time", "season", "profit", "margin", "order", "quantity"]
    
    for product_code, correct_text in correct_justifications.items():
        submitted_text = submitted_justifications.get(product_code, "")
        
        # Check for presence of key terms
        term_matches = sum(1 for term in key_terms if term.lower() in submitted_text.lower())
        
        # Check for appropriate length (100-200 words)
        word_count = len(submitted_text.split())
        appropriate_length = 100 <= word_count <= 200
        
        # Calculate score based on term matches and length
        term_score = min(1.0, term_matches / 5) * 7  # Up to 7 points for content
        length_score = 3 if appropriate_length else 0  # 3 points for appropriate length
        
        product_score = (term_score + length_score) / len(correct_justifications)
        justification_score += product_score
        
        justification_details[product_code] = {
            "term_matches": term_matches,
            "word_count": word_count,
            "appropriate_length": appropriate_length,
            "points_earned": round(product_score, 2)
        }
    
    results["breakdown"]["top_priority_justifications"]["points_earned"] = round(justification_score, 2)
    results["breakdown"]["top_priority_justifications"]["details"] = justification_details
    
    # Evaluate seasonal adjustments (5 points)
    adjustment_score = 0
    adjustment_details = {}
    
    correct_adjustments = answer_key["task5_documentation"]["seasonal_adjustments"]
    submitted_adjustments = submission.get("task5_documentation", {}).get("seasonal_adjustments", {})
    
    # Key terms for seasonal adjustments
    seasonal_terms = ["season", "peak", "off-season", "price", "increase", "decrease"]
    
    for product_code, correct_text in correct_adjustments.items():
        submitted_text = submitted_adjustments.get(product_code, "")
        
        # Check for presence of seasonal terms
        term_matches = sum(1 for term in seasonal_terms if term.lower() in submitted_text.lower())
        
        # Check for appropriate length (50-100 words)
        word_count = len(submitted_text.split())
        appropriate_length = 50 <= word_count <= 100
        
        # Calculate score
        term_score = min(1.0, term_matches / 3) * 4  # Up to 4 points for content
        length_score = 1 if appropriate_length else 0  # 1 point for appropriate length
        
        product_score = (term_score + length_score) / len(correct_adjustments)
        adjustment_score += product_score
        
        adjustment_details[product_code] = {
            "term_matches": term_matches,
            "word_count": word_count,
            "appropriate_length": appropriate_length,
            "points_earned": round(product_score, 2)
        }
    
    results["breakdown"]["seasonal_adjustments"]["points_earned"] = round(adjustment_score, 2)
    results["breakdown"]["seasonal_adjustments"]["details"] = adjustment_details
    
    # Calculate total points for Task 5
    results["points_earned"] = round(justification_score + adjustment_score, 2)
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    task4_results = evaluate_task4(submission, answer_key)
    task5_results = evaluate_task5(submission, answer_key)
    
    # Calculate overall score
    total_points_possible = (
        task1_results["points_possible"] +
        task2_results["points_possible"] +
        task3_results["points_possible"] +
        task4_results["points_possible"] +
        task5_results["points_possible"]
    )
    
    total_points_earned = (
        task1_results["points_earned"] +
        task2_results["points_earned"] +
        task3_results["points_earned"] +
        task4_results["points_earned"] +
        task5_results["points_earned"]
    )
    
    overall_score_percentage = (total_points_earned / total_points_possible) * 100 if total_points_possible > 0 else 0
    
    # Check if each task meets the minimum 60% requirement
    task_percentages = {
        "Task 1": (task1_results["points_earned"] / task1_results["points_possible"]) * 100 if task1_results["points_possible"] > 0 else 0,
        "Task 2": (task2_results["points_earned"] / task2_results["points_possible"]) * 100 if task2_results["points_possible"] > 0 else 0,
        "Task 3": (task3_results["points_earned"] / task3_results["points_possible"]) * 100 if task3_results["points_possible"] > 0 else 0,
        "Task 4": (task4_results["points_earned"] / task4_results["points_possible"]) * 100 if task4_results["points_possible"] > 0 else 0,
        "Task 5": (task5_results["points_earned"] / task5_results["points_possible"]) * 100 if task5_results["points_possible"] > 0 else 0
    }
    
    all_tasks_pass_minimum = all(percentage >= 60 for percentage in task_percentages.values())
    overall_pass = overall_score_percentage >= 70 and all_tasks_pass_minimum
    
    # Prepare the results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": round(overall_score_percentage, 2),
        "passing_score": 70,
        "passed": overall_pass,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results,
            "task4": task4_results,
            "task5": task5_results
        },
        "task_percentages": {k: round(v, 2) for k, v in task_percentages.items()},
        "all_tasks_meet_minimum_60_percent": all_tasks_pass_minimum,
        "total_points_possible": total_points_possible,
        "total_points_earned": round(total_points_earned, 2)
    }
    
    # Save the results
    save_json_file(results, "test_results.json")
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {round(overall_score_percentage, 2)}%")
    print(f"Result: {'PASS' if overall_pass else 'FAIL'}")

if __name__ == "__main__":
    main()