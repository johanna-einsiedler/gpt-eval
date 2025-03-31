import json
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_top_requested_items(submission_items, key_items):
    """Evaluate the top requested items section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key items for easier lookup
    key_items_dict = {item["item_id"]: item for item in key_items}
    
    for i, item in enumerate(submission_items):
        item_id = item.get("item_id", "")
        if item_id in key_items_dict:
            key_item = key_items_dict[item_id]
            submission_demand = item.get("monthly_demand", 0)
            key_demand = key_item.get("monthly_demand", 0)
            
            # Check if demand is within 5% of expected value
            if abs(submission_demand - key_demand) <= key_demand * 0.05:
                correct_count += 1
                feedback.append(f"Item {item_id}: Correct demand value")
            else:
                feedback.append(f"Item {item_id}: Incorrect demand value. Got {submission_demand}, expected {key_demand}")
        else:
            feedback.append(f"Item {item_id}: Not in top 10 requested items")
    
    score = (correct_count / len(key_items)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_items),
        "feedback": feedback
    }

def evaluate_inventory_turnover(submission_turnover, key_turnover):
    """Evaluate the inventory turnover section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key turnover for easier lookup
    key_turnover_dict = {item["category"]: item for item in key_turnover}
    
    for item in submission_turnover:
        category = item.get("category", "")
        if category in key_turnover_dict:
            key_item = key_turnover_dict[category]
            submission_rate = item.get("turnover_rate", 0)
            key_rate = key_item.get("turnover_rate", 0)
            
            # Check if turnover rate is within 0.5 of expected value
            if abs(submission_rate - key_rate) <= 0.5:
                correct_count += 1
                feedback.append(f"Category {category}: Correct turnover rate")
            else:
                feedback.append(f"Category {category}: Incorrect turnover rate. Got {submission_rate}, expected {key_rate}")
        else:
            feedback.append(f"Category {category}: Not found in answer key")
    
    score = (correct_count / len(key_turnover)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_turnover),
        "feedback": feedback
    }

def evaluate_stockout_items(submission_items, key_items):
    """Evaluate the stockout items section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key items for easier lookup
    key_items_dict = {item["item_id"]: item for item in key_items}
    submission_items_dict = {item["item_id"]: item for item in submission_items}
    
    # Check for items in submission that are in the key
    for item_id, item in submission_items_dict.items():
        if item_id in key_items_dict:
            stockout_count = item.get("stockout_count", 0)
            if stockout_count >= 3:
                correct_count += 1
                feedback.append(f"Item {item_id}: Correctly identified as stockout item")
            else:
                feedback.append(f"Item {item_id}: Incorrect stockout count. Got {stockout_count}, expected ≥3")
        else:
            feedback.append(f"Item {item_id}: Incorrectly identified as stockout item")
    
    # Check for items in key that are missing from submission
    for item_id in key_items_dict:
        if item_id not in submission_items_dict:
            feedback.append(f"Item {item_id}: Missing stockout item")
    
    score = (correct_count / len(key_items)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_items),
        "feedback": feedback
    }

def evaluate_critical_lead_times(submission_times, key_times):
    """Evaluate the critical lead times section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key times for easier lookup
    key_times_dict = {item["supplier_id"]: item for item in key_times}
    
    for item in submission_times:
        supplier_id = item.get("supplier_id", "")
        if supplier_id in key_times_dict:
            key_item = key_times_dict[supplier_id]
            submission_lead_time = item.get("avg_lead_time_days", 0)
            key_lead_time = key_item.get("avg_lead_time_days", 0)
            
            # Check if lead time matches exactly
            if submission_lead_time == key_lead_time:
                correct_count += 1
                feedback.append(f"Supplier {supplier_id}: Correct lead time")
            else:
                feedback.append(f"Supplier {supplier_id}: Incorrect lead time. Got {submission_lead_time}, expected {key_lead_time}")
        else:
            feedback.append(f"Supplier {supplier_id}: Not a critical supplier")
    
    score = (correct_count / len(key_times)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_times),
        "feedback": feedback
    }

def evaluate_optimal_reorder_points(submission_points, key_points):
    """Evaluate the optimal reorder points section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key points for easier lookup
    key_points_dict = {item["item_id"]: item for item in key_points}
    
    for item in submission_points:
        item_id = item.get("item_id", "")
        if item_id in key_points_dict:
            key_item = key_points_dict[item_id]
            submission_point = item.get("reorder_point", 0)
            key_point = key_item.get("reorder_point", 0)
            
            # Check if reorder point is within 20% of expected value
            if abs(submission_point - key_point) <= key_point * 0.2:
                correct_count += 1
                feedback.append(f"Item {item_id}: Correct reorder point")
            else:
                feedback.append(f"Item {item_id}: Incorrect reorder point. Got {submission_point}, expected {key_point}")
        else:
            feedback.append(f"Item {item_id}: Not in top 15 items by volume")
    
    score = (correct_count / len(key_points)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_points),
        "feedback": feedback
    }

def evaluate_delayed_delivery_suppliers(submission_suppliers, key_suppliers):
    """Evaluate the delayed delivery suppliers section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key suppliers for easier lookup
    key_suppliers_dict = {item["supplier_id"]: item for item in key_suppliers}
    submission_suppliers_dict = {item["supplier_id"]: item for item in submission_suppliers}
    
    # Check for suppliers in submission that are in the key
    for supplier_id, item in submission_suppliers_dict.items():
        if supplier_id in key_suppliers_dict:
            key_item = key_suppliers_dict[supplier_id]
            submission_frequency = item.get("delay_frequency", 0)
            key_frequency = key_item.get("delay_frequency", 0)
            
            # Check if delay frequency is within 0.05 of expected value
            if abs(submission_frequency - key_frequency) <= 0.05:
                correct_count += 1
                feedback.append(f"Supplier {supplier_id}: Correct delay frequency")
            else:
                feedback.append(f"Supplier {supplier_id}: Incorrect delay frequency. Got {submission_frequency}, expected {key_frequency}")
        else:
            feedback.append(f"Supplier {supplier_id}: Incorrectly identified as delayed supplier")
    
    # Check for suppliers in key that are missing from submission
    for supplier_id in key_suppliers_dict:
        if supplier_id not in submission_suppliers_dict:
            feedback.append(f"Supplier {supplier_id}: Missing delayed supplier")
    
    score = (correct_count / len(key_suppliers)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_suppliers),
        "feedback": feedback
    }

def evaluate_purchasing_schedule(submission_schedule, key_schedule):
    """Evaluate the purchasing schedule section."""
    correct_count = 0
    feedback = []
    
    # Create a dictionary from key schedule for easier lookup
    key_schedule_dict = {item["item_id"]: item for item in key_schedule}
    
    for item in submission_schedule:
        item_id = item.get("item_id", "")
        if item_id in key_schedule_dict:
            key_item = key_schedule_dict[item_id]
            
            # Check order frequency
            submission_frequency = item.get("order_frequency", "")
            key_frequency = key_item.get("order_frequency", "")
            frequency_correct = submission_frequency == key_frequency
            
            # Check order quantity (within 20% of expected)
            submission_quantity = item.get("order_quantity", 0)
            key_quantity = key_item.get("order_quantity", 0)
            quantity_correct = abs(submission_quantity - key_quantity) <= key_quantity * 0.2
            
            if frequency_correct and quantity_correct:
                correct_count += 1
                feedback.append(f"Item {item_id}: Correct schedule")
            else:
                issues = []
                if not frequency_correct:
                    issues.append(f"frequency (got {submission_frequency}, expected {key_frequency})")
                if not quantity_correct:
                    issues.append(f"quantity (got {submission_quantity}, expected {key_quantity})")
                feedback.append(f"Item {item_id}: Incorrect {' and '.join(issues)}")
        else:
            feedback.append(f"Item {item_id}: Not in top 20 items by demand")
    
    score = (correct_count / len(key_schedule)) * 10
    return {
        "score": score,
        "max_score": 10,
        "correct_count": correct_count,
        "total_count": len(key_schedule),
        "feedback": feedback
    }

def evaluate_seasonal_inventory_approach(submission_approach, key_approach):
    """Evaluate the seasonal inventory approach section."""
    score = 0
    feedback = []
    
    # Check winter items strategy
    if "winter_items" in submission_approach and "winter_items" in key_approach:
        submission_winter = submission_approach["winter_items"]
        key_winter = key_approach["winter_items"]
        
        if "strategy" in submission_winter and "strategy" in key_winter:
            # Check if strategy mentions reducing inventory and includes a percentage
            submission_strategy = submission_winter["strategy"].lower()
            if "reduce" in submission_strategy and any(str(i) in submission_strategy for i in range(10, 40)):
                score += 2.5
                feedback.append("Winter strategy: Correctly identifies reduction in inventory")
            else:
                feedback.append("Winter strategy: Does not clearly identify reduction or specific percentage")
        
        if "rationale" in submission_winter and "rationale" in key_winter:
            # Check if rationale mentions lower demand in winter months
            submission_rationale = submission_winter["rationale"].lower()
            if "lower demand" in submission_rationale or "decreased demand" in submission_rationale:
                score += 2.5
                feedback.append("Winter rationale: Correctly identifies lower demand in winter")
            else:
                feedback.append("Winter rationale: Does not clearly explain lower demand in winter")
    else:
        feedback.append("Missing winter items strategy or rationale")
    
    # Check summer items strategy
    if "summer_items" in submission_approach and "summer_items" in key_approach:
        submission_summer = submission_approach["summer_items"]
        key_summer = key_approach["summer_items"]
        
        if "strategy" in submission_summer and "strategy" in key_summer:
            # Check if strategy mentions increasing inventory and includes a percentage
            submission_strategy = submission_summer["strategy"].lower()
            if "increase" in submission_strategy and any(str(i) in submission_strategy for i in range(15, 35)):
                score += 2.5
                feedback.append("Summer strategy: Correctly identifies increase in inventory")
            else:
                feedback.append("Summer strategy: Does not clearly identify increase or specific percentage")
        
        if "rationale" in submission_summer and "rationale" in key_summer:
            # Check if rationale mentions higher demand in Q3 or summer
            submission_rationale = submission_summer["rationale"].lower()
            if ("higher demand" in submission_rationale or "increased demand" in submission_rationale) and ("q3" in submission_rationale or "summer" in submission_rationale):
                score += 2.5
                feedback.append("Summer rationale: Correctly identifies higher demand in summer/Q3")
            else:
                feedback.append("Summer rationale: Does not clearly explain higher demand in summer/Q3")
    else:
        feedback.append("Missing summer items strategy or rationale")
    
    return {
        "score": score,
        "max_score": 10,
        "feedback": feedback
    }

def evaluate_process_improvements(submission_improvements, key_improvements):
    """Evaluate the process improvements section."""
    score = 0
    feedback = []
    
    # Check if there are at least 3 improvements
    if len(submission_improvements) >= 3:
        score += 2
        feedback.append("Provided at least 3 process improvements")
    else:
        feedback.append(f"Provided only {len(submission_improvements)} improvements, expected at least 3")
    
    # Check for stockout-related improvement
    has_stockout_improvement = False
    for improvement in submission_improvements:
        current = improvement.get("current_process", "").lower()
        recommended = improvement.get("recommended_change", "").lower()
        benefit = improvement.get("expected_benefit", "").lower()
        
        if ("stockout" in current or "stockout" in recommended or "stockout" in benefit or
            "out of stock" in current or "out of stock" in recommended or "out of stock" in benefit):
            has_stockout_improvement = True
            break
    
    if has_stockout_improvement:
        score += 3
        feedback.append("Included improvement related to stockouts")
    else:
        feedback.append("No improvement specifically addressing stockouts")
    
    # Check for ordering efficiency improvement
    has_ordering_improvement = False
    for improvement in submission_improvements:
        current = improvement.get("current_process", "").lower()
        recommended = improvement.get("recommended_change", "").lower()
        benefit = improvement.get("expected_benefit", "").lower()
        
        if ("order" in current or "order" in recommended or 
            "purchas" in current or "purchas" in recommended or
            "consolidat" in current or "consolidat" in recommended):
            has_ordering_improvement = True
            break
    
    if has_ordering_improvement:
        score += 3
        feedback.append("Included improvement related to ordering efficiency")
    else:
        feedback.append("No improvement specifically addressing ordering efficiency")
    
    # Check for quantifiable benefits
    has_quantifiable_benefit = False
    for improvement in submission_improvements:
        benefit = improvement.get("expected_benefit", "").lower()
        
        # Check for percentages or numbers in the benefit
        if any(str(i) in benefit for i in range(10, 100)) or "%" in benefit:
            has_quantifiable_benefit = True
            break
    
    if has_quantifiable_benefit:
        score += 2
        feedback.append("Included quantifiable expected benefits")
    else:
        feedback.append("No quantifiable benefits provided")
    
    return {
        "score": score,
        "max_score": 10,
        "feedback": feedback
    }

def evaluate_projected_outcomes(submission_outcomes, key_outcomes):
    """Evaluate the projected outcomes section."""
    score = 0
    feedback = []
    
    # Check cost savings (within 20% of expected)
    submission_savings = submission_outcomes.get("cost_savings", 0)
    key_savings = key_outcomes.get("cost_savings", 0)
    if abs(submission_savings - key_savings) <= key_savings * 0.2:
        score += 3
        feedback.append("Cost savings: Within acceptable range")
    else:
        feedback.append(f"Cost savings: Outside acceptable range. Got {submission_savings}, expected {key_savings}")
    
    # Check service level improvement (within 20% of expected)
    submission_service = submission_outcomes.get("service_level_improvement", 0)
    key_service = key_outcomes.get("service_level_improvement", 0)
    if abs(submission_service - key_service) <= key_service * 0.2:
        score += 3
        feedback.append("Service level improvement: Within acceptable range")
    else:
        feedback.append(f"Service level improvement: Outside acceptable range. Got {submission_service}, expected {key_service}")
    
    # Check stockout reduction (within 20% of expected)
    submission_reduction = submission_outcomes.get("stockout_reduction", 0)
    key_reduction = key_outcomes.get("stockout_reduction", 0)
    if abs(submission_reduction - key_reduction) <= key_reduction * 0.2:
        score += 4
        feedback.append("Stockout reduction: Within acceptable range")
    else:
        feedback.append(f"Stockout reduction: Outside acceptable range. Got {submission_reduction}, expected {key_reduction}")
    
    return {
        "score": score,
        "max_score": 10,
        "feedback": feedback
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "data_analysis": {
            "top_requested_items": evaluate_top_requested_items(
                submission.get("data_analysis", {}).get("top_requested_items", []),
                answer_key.get("data_analysis", {}).get("top_requested_items", [])
            ),
            "inventory_turnover": evaluate_inventory_turnover(
                submission.get("data_analysis", {}).get("inventory_turnover", []),
                answer_key.get("data_analysis", {}).get("inventory_turnover", [])
            ),
            "stockout_items": evaluate_stockout_items(
                submission.get("data_analysis", {}).get("stockout_items", []),
                answer_key.get("data_analysis", {}).get("stockout_items", [])
            )
        },
        "supply_chain_assessment": {
            "critical_lead_times": evaluate_critical_lead_times(
                submission.get("supply_chain_assessment", {}).get("critical_lead_times", []),
                answer_key.get("supply_chain_assessment", {}).get("critical_lead_times", [])
            ),
            "optimal_reorder_points": evaluate_optimal_reorder_points(
                submission.get("supply_chain_assessment", {}).get("optimal_reorder_points", []),
                answer_key.get("supply_chain_assessment", {}).get("optimal_reorder_points", [])
            ),
            "delayed_delivery_suppliers": evaluate_delayed_delivery_suppliers(
                submission.get("supply_chain_assessment", {}).get("delayed_delivery_suppliers", []),
                answer_key.get("supply_chain_assessment", {}).get("delayed_delivery_suppliers", [])
            )
        },
        "strategic_purchasing_program": {
            "purchasing_schedule": evaluate_purchasing_schedule(
                submission.get("strategic_purchasing_program", {}).get("purchasing_schedule", []),
                answer_key.get("strategic_purchasing_program", {}).get("purchasing_schedule", [])
            ),
            "seasonal_inventory_approach": evaluate_seasonal_inventory_approach(
                submission.get("strategic_purchasing_program", {}).get("seasonal_inventory_approach", {}),
                answer_key.get("strategic_purchasing_program", {}).get("seasonal_inventory_approach", {})
            ),
            "process_improvements": evaluate_process_improvements(
                submission.get("strategic_purchasing_program", {}).get("process_improvements", []),
                answer_key.get("strategic_purchasing_program", {}).get("process_improvements", [])
            )
        },
        "projected_outcomes": evaluate_projected_outcomes(
            submission.get("projected_outcomes", {}),
            answer_key.get("projected_outcomes", {})
        )
    }
    
    # Calculate section scores
    data_analysis_score = (
        results["data_analysis"]["top_requested_items"]["score"] +
        results["data_analysis"]["inventory_turnover"]["score"] +
        results["data_analysis"]["stockout_items"]["score"]
    )
    
    supply_chain_score = (
        results["supply_chain_assessment"]["critical_lead_times"]["score"] +
        results["supply_chain_assessment"]["optimal_reorder_points"]["score"] +
        results["supply_chain_assessment"]["delayed_delivery_suppliers"]["score"]
    )
    
    strategic_program_score = (
        results["strategic_purchasing_program"]["purchasing_schedule"]["score"] +
        results["strategic_purchasing_program"]["seasonal_inventory_approach"]["score"] +
        results["strategic_purchasing_program"]["process_improvements"]["score"]
    )
    
    outcomes_score = results["projected_outcomes"]["score"]
    
    # Calculate total score
    total_score = data_analysis_score + supply_chain_score + strategic_program_score + outcomes_score
    
    # Calculate overall percentage
    overall_percentage = (total_score / 100) * 100
    
    # Add summary to results
    results["summary"] = {
        "data_analysis_score": data_analysis_score,
        "supply_chain_score": supply_chain_score,
        "strategic_program_score": strategic_program_score,
        "outcomes_score": outcomes_score,
        "total_score": total_score,
        "overall_score": overall_percentage,
        "passed": total_score >= 70
    }
    
    return results

def main():
    # File paths
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    try:
        with open(results_file, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation complete. Results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()