import json
import math
import re

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_exercise1(submission, answer_key):
    results = {
        "points_earned": 0,
        "max_points": 25,
        "breakdown": {
            "supplier_selection": {"earned": 0, "max": 10, "comments": ""},
            "score_calculations": {"earned": 0, "max": 10, "comments": ""},
            "justification": {"earned": 0, "max": 5, "comments": ""}
        }
    }
    
    # Check supplier selection (10 points)
    if submission.get("selectedSupplier") == answer_key.get("selectedSupplier"):
        results["breakdown"]["supplier_selection"]["earned"] = 10
        results["breakdown"]["supplier_selection"]["comments"] = "Correct supplier selected."
    else:
        # Check if it's PremiumWork which could be an acceptable alternative
        if submission.get("selectedSupplier") == "PremiumWork Spaces":
            results["breakdown"]["supplier_selection"]["earned"] = 8
            results["breakdown"]["supplier_selection"]["comments"] = "Alternative supplier selected with highest quality but higher price."
        else:
            results["breakdown"]["supplier_selection"]["earned"] = 0
            results["breakdown"]["supplier_selection"]["comments"] = "Incorrect supplier selected."
    
    # Check score calculations (10 points, 2.5 each)
    score_points = 0
    score_comments = []
    
    # Quality score (2.5 points)
    if abs(submission.get("qualityScore", 0) - answer_key.get("qualityScore", 0)) <= 0.1:
        score_points += 2.5
    else:
        score_comments.append("Quality score calculation incorrect.")
    
    # Cost score (2.5 points)
    if abs(submission.get("costScore", 0) - answer_key.get("costScore", 0)) <= 0.1:
        score_points += 2.5
    else:
        score_comments.append("Cost score calculation incorrect.")
    
    # Reliability score (2.5 points)
    if abs(submission.get("reliabilityScore", 0) - answer_key.get("reliabilityScore", 0)) <= 0.1:
        score_points += 2.5
    else:
        score_comments.append("Reliability score calculation incorrect.")
    
    # Total score (2.5 points)
    if abs(submission.get("totalScore", 0) - answer_key.get("totalScore", 0)) <= 0.1:
        score_points += 2.5
    else:
        score_comments.append("Total score calculation incorrect.")
    
    results["breakdown"]["score_calculations"]["earned"] = score_points
    results["breakdown"]["score_calculations"]["comments"] = "; ".join(score_comments) if score_comments else "All score calculations correct."
    
    # Check justification (5 points)
    justification = submission.get("justification", "")
    if len(justification) >= 50:  # Ensure minimum length
        if "quality" in justification.lower() and "price" in justification.lower() and "reliability" in justification.lower():
            if "balance" in justification.lower() or "optimal" in justification.lower():
                results["breakdown"]["justification"]["earned"] = 5
                results["breakdown"]["justification"]["comments"] = "Excellent justification with all key factors."
            else:
                results["breakdown"]["justification"]["earned"] = 4
                results["breakdown"]["justification"]["comments"] = "Good justification but missing some reasoning."
        else:
            results["breakdown"]["justification"]["earned"] = 3
            results["breakdown"]["justification"]["comments"] = "Justification missing key evaluation factors."
    else:
        results["breakdown"]["justification"]["earned"] = 0
        results["breakdown"]["justification"]["comments"] = "Insufficient justification."
    
    # Calculate total points earned
    results["points_earned"] = (
        results["breakdown"]["supplier_selection"]["earned"] +
        results["breakdown"]["score_calculations"]["earned"] +
        results["breakdown"]["justification"]["earned"]
    )
    
    return results

def evaluate_exercise2(submission, answer_key):
    results = {
        "points_earned": 0,
        "max_points": 25,
        "breakdown": {
            "order_quantities": {"earned": 0, "max": 10, "comments": ""},
            "cost_calculations": {"earned": 0, "max": 10, "comments": ""},
            "calculation_breakdown": {"earned": 0, "max": 5, "comments": ""}
        }
    }
    
    # Check order quantities (10 points, 5 each)
    order_points = 0
    order_comments = []
    
    # Floor cleaner quantity (5 points)
    sub_fc_qty = submission.get("optimalOrderQuantity", {}).get("floorCleaner", 0)
    key_fc_qty = answer_key.get("optimalOrderQuantity", {}).get("floorCleaner", 0)
    
    if sub_fc_qty == key_fc_qty:
        order_points += 5
    elif 24 <= sub_fc_qty <= 40:  # Allow for reasonable range
        order_points += 3
        order_comments.append("Floor cleaner quantity reasonable but not optimal.")
    else:
        order_comments.append("Floor cleaner quantity incorrect.")
    
    # Disinfectant quantity (5 points)
    sub_d_qty = submission.get("optimalOrderQuantity", {}).get("disinfectant", 0)
    key_d_qty = answer_key.get("optimalOrderQuantity", {}).get("disinfectant", 0)
    
    if sub_d_qty == key_d_qty:
        order_points += 5
    elif 25 <= sub_d_qty <= 35:  # Allow for reasonable range
        order_points += 3
        order_comments.append("Disinfectant quantity reasonable but not optimal.")
    else:
        order_comments.append("Disinfectant quantity incorrect.")
    
    results["breakdown"]["order_quantities"]["earned"] = order_points
    results["breakdown"]["order_quantities"]["comments"] = "; ".join(order_comments) if order_comments else "All order quantities correct."
    
    # Check cost calculations (10 points, 5 each)
    cost_points = 0
    cost_comments = []
    
    # Floor cleaner cost and savings (5 points)
    sub_fc_cost = submission.get("totalAnnualCost", {}).get("floorCleaner", 0)
    key_fc_cost = answer_key.get("totalAnnualCost", {}).get("floorCleaner", 0)
    sub_fc_savings = submission.get("costSavings", {}).get("floorCleaner", 0)
    key_fc_savings = answer_key.get("costSavings", {}).get("floorCleaner", 0)
    
    if abs(sub_fc_cost - key_fc_cost) <= 50 and abs(sub_fc_savings - key_fc_savings) <= 50:
        cost_points += 5
    elif abs(sub_fc_cost - key_fc_cost) <= 100 or abs(sub_fc_savings - key_fc_savings) <= 100:
        cost_points += 3
        cost_comments.append("Floor cleaner cost calculations slightly off.")
    else:
        cost_comments.append("Floor cleaner cost calculations incorrect.")
    
    # Disinfectant cost and savings (5 points)
    sub_d_cost = submission.get("totalAnnualCost", {}).get("disinfectant", 0)
    key_d_cost = answer_key.get("totalAnnualCost", {}).get("disinfectant", 0)
    sub_d_savings = submission.get("costSavings", {}).get("disinfectant", 0)
    key_d_savings = answer_key.get("costSavings", {}).get("disinfectant", 0)
    
    if abs(sub_d_cost - key_d_cost) <= 50 and abs(sub_d_savings - key_d_savings) <= 50:
        cost_points += 5
    elif abs(sub_d_cost - key_d_cost) <= 100 or abs(sub_d_savings - key_d_savings) <= 100:
        cost_points += 3
        cost_comments.append("Disinfectant cost calculations slightly off.")
    else:
        cost_comments.append("Disinfectant cost calculations incorrect.")
    
    results["breakdown"]["cost_calculations"]["earned"] = cost_points
    results["breakdown"]["cost_calculations"]["comments"] = "; ".join(cost_comments) if cost_comments else "All cost calculations correct."
    
    # Check calculation breakdown (5 points)
    breakdown = submission.get("breakdownCalculations", "")
    if "EOQ" in breakdown and "formula" in breakdown.lower():
        if "sqrt" in breakdown or "√" in breakdown:
            if "discount" in breakdown.lower() and "annual" in breakdown.lower():
                results["breakdown"]["calculation_breakdown"]["earned"] = 5
                results["breakdown"]["calculation_breakdown"]["comments"] = "Excellent calculation breakdown with formula and reasoning."
            else:
                results["breakdown"]["calculation_breakdown"]["earned"] = 4
                results["breakdown"]["calculation_breakdown"]["comments"] = "Good calculation breakdown but missing some details."
        else:
            results["breakdown"]["calculation_breakdown"]["earned"] = 3
            results["breakdown"]["calculation_breakdown"]["comments"] = "Calculation breakdown missing formula details."
    else:
        results["breakdown"]["calculation_breakdown"]["earned"] = 0
        results["breakdown"]["calculation_breakdown"]["comments"] = "Insufficient calculation breakdown."
    
    # Calculate total points earned
    results["points_earned"] = (
        results["breakdown"]["order_quantities"]["earned"] +
        results["breakdown"]["cost_calculations"]["earned"] +
        results["breakdown"]["calculation_breakdown"]["earned"]
    )
    
    return results

def evaluate_exercise3(submission, answer_key):
    results = {
        "points_earned": 0,
        "max_points": 25,
        "breakdown": {
            "line_items": {"earned": 0, "max": 10, "comments": ""},
            "totals": {"earned": 0, "max": 10, "comments": ""},
            "po_format": {"earned": 0, "max": 5, "comments": ""}
        }
    }
    
    # Check line item calculations (10 points)
    line_points = 0
    line_comments = []
    
    # Check if all line items are present
    sub_items = submission.get("lineItems", [])
    key_items = answer_key.get("lineItems", [])
    
    if len(sub_items) == len(key_items):
        # Check each line item's calculations
        correct_items = 0
        for sub_item in sub_items:
            item_number = sub_item.get("itemNumber", "")
            # Find matching item in answer key
            key_item = next((item for item in key_items if item.get("itemNumber") == item_number), None)
            
            if key_item:
                # Check quantity, unit price, and total price
                if (sub_item.get("quantity") == key_item.get("quantity") and
                    abs(sub_item.get("unitPrice", 0) - key_item.get("unitPrice", 0)) <= 0.01 and
                    abs(sub_item.get("totalPrice", 0) - key_item.get("totalPrice", 0)) <= 0.1):
                    correct_items += 1
        
        # Award points based on correct items (2.5 points per item)
        line_points = (correct_items / len(key_items)) * 10
        
        if correct_items < len(key_items):
            line_comments.append(f"{len(key_items) - correct_items} line items have calculation errors.")
    else:
        line_comments.append("Missing or extra line items.")
    
    results["breakdown"]["line_items"]["earned"] = line_points
    results["breakdown"]["line_items"]["comments"] = "; ".join(line_comments) if line_comments else "All line items calculated correctly."
    
    # Check totals calculations (10 points)
    total_points = 0
    total_comments = []
    
    # Subtotal (3.33 points)
    if abs(submission.get("subtotal", 0) - answer_key.get("subtotal", 0)) <= 0.1:
        total_points += 3.33
    else:
        total_comments.append("Subtotal calculation incorrect.")
    
    # Tax (3.33 points)
    if abs(submission.get("tax", 0) - answer_key.get("tax", 0)) <= 0.1:
        total_points += 3.33
    else:
        total_comments.append("Tax calculation incorrect.")
    
    # Grand total (3.34 points)
    if abs(submission.get("grandTotal", 0) - answer_key.get("grandTotal", 0)) <= 0.1:
        total_points += 3.34
    else:
        total_comments.append("Grand total calculation incorrect.")
    
    results["breakdown"]["totals"]["earned"] = total_points
    results["breakdown"]["totals"]["comments"] = "; ".join(total_comments) if total_comments else "All totals calculated correctly."
    
    # Check PO format (5 points)
    format_points = 0
    
    # Check PO number
    if submission.get("poNumber") == answer_key.get("poNumber"):
        format_points += 1
    
    # Check if all required fields are present
    required_fields = ["poNumber", "lineItems", "subtotal", "tax", "shipping", "grandTotal"]
    missing_fields = [field for field in required_fields if field not in submission]
    
    if not missing_fields:
        format_points += 2
    
    # Check if line items have all required fields
    if sub_items:
        required_item_fields = ["itemNumber", "description", "quantity", "unitPrice", "totalPrice"]
        all_fields_present = all(all(field in item for field in required_item_fields) for item in sub_items)
        
        if all_fields_present:
            format_points += 2
    
    results["breakdown"]["po_format"]["earned"] = format_points
    
    if format_points == 5:
        results["breakdown"]["po_format"]["comments"] = "PO format is complete and correct."
    elif format_points >= 3:
        results["breakdown"]["po_format"]["comments"] = "PO format is mostly correct with minor issues."
    else:
        results["breakdown"]["po_format"]["comments"] = "PO format has significant issues."
    
    # Calculate total points earned
    results["points_earned"] = (
        results["breakdown"]["line_items"]["earned"] +
        results["breakdown"]["totals"]["earned"] +
        results["breakdown"]["po_format"]["earned"]
    )
    
    return results

def evaluate_exercise4(submission, answer_key):
    results = {
        "points_earned": 0,
        "max_points": 25,
        "breakdown": {
            "counteroffer_price": {"earned": 0, "max": 10, "comments": ""},
            "requested_terms": {"earned": 0, "max": 5, "comments": ""},
            "justification": {"earned": 0, "max": 5, "comments": ""},
            "savings_calculation": {"earned": 0, "max": 5, "comments": ""}
        }
    }
    
    # Check counteroffer price (10 points)
    sub_price = submission.get("counterofferPrice", 0)
    key_price = answer_key.get("counterofferPrice", 0)
    
    if abs(sub_price - key_price) <= 0.05:
        results["breakdown"]["counteroffer_price"]["earned"] = 10
        results["breakdown"]["counteroffer_price"]["comments"] = "Excellent counteroffer price."
    elif 3.45 <= sub_price <= 3.65:
        # Within reasonable market range
        results["breakdown"]["counteroffer_price"]["earned"] = 8
        results["breakdown"]["counteroffer_price"]["comments"] = "Reasonable counteroffer price within market range."
    elif 3.40 <= sub_price <= 3.70:
        # Slightly outside optimal range
        results["breakdown"]["counteroffer_price"]["earned"] = 5
        results["breakdown"]["counteroffer_price"]["comments"] = "Counteroffer price slightly outside optimal range."
    else:
        results["breakdown"]["counteroffer_price"]["earned"] = 0
        results["breakdown"]["counteroffer_price"]["comments"] = "Counteroffer price unreasonable."
    
    # Check requested terms (5 points)
    sub_terms = submission.get("requestedTerms", [])
    
    valid_term_keywords = [
        "net 30", "net30", "payment terms", 
        "delivery", "timeframe", "lead time", "week",
        "minimum order", "order quantity", "quantity"
    ]
    
    valid_terms_count = 0
    for term in sub_terms:
        term_lower = term.lower()
        for keyword in valid_term_keywords:
            if keyword in term_lower:
                valid_terms_count += 1
                break
    
    if valid_terms_count >= 3:
        results["breakdown"]["requested_terms"]["earned"] = 5
        results["breakdown"]["requested_terms"]["comments"] = "Excellent negotiation terms requested."
    elif valid_terms_count == 2:
        results["breakdown"]["requested_terms"]["earned"] = 4
        results["breakdown"]["requested_terms"]["comments"] = "Good negotiation terms requested."
    elif valid_terms_count == 1:
        results["breakdown"]["requested_terms"]["earned"] = 2
        results["breakdown"]["requested_terms"]["comments"] = "Only one valid negotiation term requested."
    else:
        results["breakdown"]["requested_terms"]["earned"] = 0
        results["breakdown"]["requested_terms"]["comments"] = "No valid negotiation terms requested."
    
    # Check justification (5 points)
    justification = submission.get("justification", "")
    
    if len(justification) >= 50:  # Ensure minimum length
        key_phrases = ["market", "price", "terms", "relationship", "history", "standard"]
        phrase_count = sum(1 for phrase in key_phrases if phrase in justification.lower())
        
        if phrase_count >= 4:
            results["breakdown"]["justification"]["earned"] = 5
            results["breakdown"]["justification"]["comments"] = "Excellent justification with market context."
        elif phrase_count >= 2:
            results["breakdown"]["justification"]["earned"] = 3
            results["breakdown"]["justification"]["comments"] = "Adequate justification but missing some market context."
        else:
            results["breakdown"]["justification"]["earned"] = 1
            results["breakdown"]["justification"]["comments"] = "Weak justification with minimal market context."
    else:
        results["breakdown"]["justification"]["earned"] = 0
        results["breakdown"]["justification"]["comments"] = "Insufficient justification."
    
    # Check savings calculation (5 points)
    sub_savings = submission.get("expectedSavings", 0)
    
    # Calculate expected savings based on submitted counteroffer
    expected_savings = (3.85 - sub_price) * 5000
    
    if abs(sub_savings - expected_savings) <= 10:
        results["breakdown"]["savings_calculation"]["earned"] = 5
        results["breakdown"]["savings_calculation"]["comments"] = "Savings calculation is correct."
    elif abs(sub_savings - expected_savings) <= 100:
        results["breakdown"]["savings_calculation"]["earned"] = 3
        results["breakdown"]["savings_calculation"]["comments"] = "Savings calculation has minor errors."
    else:
        results["breakdown"]["savings_calculation"]["earned"] = 0
        results["breakdown"]["savings_calculation"]["comments"] = "Savings calculation is incorrect."
    
    # Calculate total points earned
    results["points_earned"] = (
        results["breakdown"]["counteroffer_price"]["earned"] +
        results["breakdown"]["requested_terms"]["earned"] +
        results["breakdown"]["justification"]["earned"] +
        results["breakdown"]["savings_calculation"]["earned"]
    )
    
    return results

def main():
    # Load submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate each exercise
    results = {
        "candidateID": submission.get("candidateID", "Unknown"),
        "exercise1": evaluate_exercise1(submission.get("exercise1", {}), answer_key.get("exercise1", {})),
        "exercise2": evaluate_exercise2(submission.get("exercise2", {}), answer_key.get("exercise2", {})),
        "exercise3": evaluate_exercise3(submission.get("exercise3", {}), answer_key.get("exercise3", {})),
        "exercise4": evaluate_exercise4(submission.get("exercise4", {}), answer_key.get("exercise4", {})),
    }
    
    # Calculate overall score
    total_points = sum(results[f"exercise{i}"]["points_earned"] for i in range(1, 5))
    max_points = sum(results[f"exercise{i}"]["max_points"] for i in range(1, 5))
    overall_percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    
    results["overall_score"] = round(overall_percentage, 2)
    results["total_points"] = total_points
    results["max_points"] = max_points
    
    # Determine if candidate passed
    min_overall = 70
    min_per_exercise = 15
    
    exercise_scores = [results[f"exercise{i}"]["points_earned"] for i in range(1, 5)]
    passed_overall = overall_percentage >= min_overall
    passed_exercises = all(score >= min_per_exercise for score in exercise_scores)
    
    results["passed"] = passed_overall and passed_exercises
    
    if not passed_overall:
        results["failure_reason"] = f"Overall score {overall_percentage:.2f}% is below the required {min_overall}%"
    elif not passed_exercises:
        failed_exercises = [f"Exercise {i+1}" for i, score in enumerate(exercise_scores) if score < min_per_exercise]
        results["failure_reason"] = f"Failed to meet minimum score in: {', '.join(failed_exercises)}"
    else:
        results["failure_reason"] = None
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {overall_percentage:.2f}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()