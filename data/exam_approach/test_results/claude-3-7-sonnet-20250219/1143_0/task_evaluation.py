import json
import math
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json_file(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def is_close_enough(val1, val2, tolerance=0.05):
    """Check if two numeric values are close enough within tolerance"""
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) <= tolerance
    return val1 == val2

def validate_date_format(date_str):
    """Validate if string is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def evaluate_exercise1(submission, answer_key):
    """Evaluate the purchase order preparation exercise"""
    results = {
        "points_possible": 20,
        "points_earned": 0,
        "percentage": 0,
        "details": {}
    }
    
    # Check PO number format (1 point)
    if submission.get("poNumber") == answer_key.get("poNumber"):
        results["details"]["poNumber"] = {"earned": 1, "possible": 1, "comment": "Correct PO number"}
        results["points_earned"] += 1
    else:
        results["details"]["poNumber"] = {"earned": 0, "possible": 1, "comment": "Incorrect PO number"}
    
    # Check vendor information (2 points)
    if submission.get("vendorID") == answer_key.get("vendorID"):
        results["details"]["vendorInfo"] = {"earned": 2, "possible": 2, "comment": "Correct vendor information"}
        results["points_earned"] += 2
    else:
        results["details"]["vendorInfo"] = {"earned": 0, "possible": 2, "comment": "Incorrect vendor information"}
    
    # Check requisition reference (1 point)
    if submission.get("requisitionNumber") == answer_key.get("requisitionNumber"):
        results["details"]["requisitionNumber"] = {"earned": 1, "possible": 1, "comment": "Correct requisition reference"}
        results["points_earned"] += 1
    else:
        results["details"]["requisitionNumber"] = {"earned": 0, "possible": 1, "comment": "Incorrect requisition reference"}
    
    # Check order date (1 point)
    if validate_date_format(submission.get("orderDate", "")):
        results["details"]["orderDate"] = {"earned": 1, "possible": 1, "comment": "Valid order date format"}
        results["points_earned"] += 1
    else:
        results["details"]["orderDate"] = {"earned": 0, "possible": 1, "comment": "Invalid order date format"}
    
    # Check delivery date (1 point)
    if submission.get("deliveryDate") == answer_key.get("deliveryDate"):
        results["details"]["deliveryDate"] = {"earned": 1, "possible": 1, "comment": "Correct delivery date"}
        results["points_earned"] += 1
    else:
        results["details"]["deliveryDate"] = {"earned": 0, "possible": 1, "comment": "Incorrect delivery date"}
    
    # Check line items (3 points)
    sub_items = submission.get("lineItems", [])
    key_items = answer_key.get("lineItems", [])
    
    if len(sub_items) == len(key_items):
        item_points = 3
        results["details"]["lineItemsCount"] = {"earned": 3, "possible": 3, "comment": "All line items included"}
    else:
        item_points = round(3 * (len(sub_items) / max(1, len(key_items))))
        results["details"]["lineItemsCount"] = {
            "earned": item_points, 
            "possible": 3, 
            "comment": f"Missing line items: {len(key_items) - len(sub_items)}"
        }
    results["points_earned"] += item_points
    
    # Create a mapping of item numbers to check descriptions, quantities, and prices
    sub_items_map = {item.get("itemNumber"): item for item in sub_items}
    key_items_map = {item.get("itemNumber"): item for item in key_items}
    
    # Check item descriptions (2 points)
    desc_correct = sum(1 for item_num in key_items_map if 
                      item_num in sub_items_map and 
                      sub_items_map[item_num].get("description") == key_items_map[item_num].get("description"))
    desc_points = round(2 * (desc_correct / max(1, len(key_items))))
    results["details"]["itemDescriptions"] = {
        "earned": desc_points, 
        "possible": 2, 
        "comment": f"Correct descriptions: {desc_correct}/{len(key_items)}"
    }
    results["points_earned"] += desc_points
    
    # Check quantities (2 points)
    qty_correct = sum(1 for item_num in key_items_map if 
                     item_num in sub_items_map and 
                     sub_items_map[item_num].get("quantity") == key_items_map[item_num].get("quantity"))
    qty_points = round(2 * (qty_correct / max(1, len(key_items))))
    results["details"]["itemQuantities"] = {
        "earned": qty_points, 
        "possible": 2, 
        "comment": f"Correct quantities: {qty_correct}/{len(key_items)}"
    }
    results["points_earned"] += qty_points
    
    # Check unit prices (2 points)
    price_correct = sum(1 for item_num in key_items_map if 
                       item_num in sub_items_map and 
                       is_close_enough(sub_items_map[item_num].get("unitPrice"), key_items_map[item_num].get("unitPrice"), 0.01))
    price_points = round(2 * (price_correct / max(1, len(key_items))))
    results["details"]["unitPrices"] = {
        "earned": price_points, 
        "possible": 2, 
        "comment": f"Correct unit prices: {price_correct}/{len(key_items)}"
    }
    results["points_earned"] += price_points
    
    # Check calculations (4 points)
    calc_points = 0
    calc_comments = []
    
    # Subtotal check (1 point)
    if is_close_enough(submission.get("subtotal"), answer_key.get("subtotal"), 0.01):
        calc_points += 1
        calc_comments.append("Correct subtotal")
    else:
        calc_comments.append("Incorrect subtotal")
    
    # Tax check (1 point)
    if is_close_enough(submission.get("taxAmount"), answer_key.get("taxAmount"), 0.01):
        calc_points += 1
        calc_comments.append("Correct tax amount")
    else:
        calc_comments.append("Incorrect tax amount")
    
    # Shipping check (1 point)
    if is_close_enough(submission.get("shippingCost"), answer_key.get("shippingCost"), 0.01):
        calc_points += 1
        calc_comments.append("Correct shipping cost")
    else:
        calc_comments.append("Incorrect shipping cost")
    
    # Total check (1 point)
    if is_close_enough(submission.get("totalAmount"), answer_key.get("totalAmount"), 0.01):
        calc_points += 1
        calc_comments.append("Correct total amount")
    else:
        calc_comments.append("Incorrect total amount")
    
    results["details"]["calculations"] = {
        "earned": calc_points, 
        "possible": 4, 
        "comment": "; ".join(calc_comments)
    }
    results["points_earned"] += calc_points
    
    # Check payment terms (1 point)
    if submission.get("paymentTerms") == answer_key.get("paymentTerms"):
        results["details"]["paymentTerms"] = {"earned": 1, "possible": 1, "comment": "Correct payment terms"}
        results["points_earned"] += 1
    else:
        results["details"]["paymentTerms"] = {"earned": 0, "possible": 1, "comment": "Incorrect payment terms"}
    
    # Calculate percentage
    results["percentage"] = round((results["points_earned"] / results["points_possible"]) * 100, 2)
    
    return results

def evaluate_exercise2(submission, answer_key):
    """Evaluate the RFQ exercise"""
    results = {
        "points_possible": 15,
        "points_earned": 0,
        "percentage": 0,
        "details": {}
    }
    
    # Check RFQ number format (1 point)
    if submission.get("rfqNumber") == answer_key.get("rfqNumber"):
        results["details"]["rfqNumber"] = {"earned": 1, "possible": 1, "comment": "Correct RFQ number"}
        results["points_earned"] += 1
    else:
        results["details"]["rfqNumber"] = {"earned": 0, "possible": 1, "comment": "Incorrect RFQ number"}
    
    # Check issue date (1 point)
    if validate_date_format(submission.get("issueDate", "")):
        results["details"]["issueDate"] = {"earned": 1, "possible": 1, "comment": "Valid issue date format"}
        results["points_earned"] += 1
    else:
        results["details"]["issueDate"] = {"earned": 0, "possible": 1, "comment": "Invalid issue date format"}
    
    # Check submission deadline (1 point)
    # Ideally we'd check if it's 14 days from issue date, but for simplicity we'll just check format
    if validate_date_format(submission.get("submissionDeadline", "")):
        results["details"]["submissionDeadline"] = {"earned": 1, "possible": 1, "comment": "Valid submission deadline format"}
        results["points_earned"] += 1
    else:
        results["details"]["submissionDeadline"] = {"earned": 0, "possible": 1, "comment": "Invalid submission deadline format"}
    
    # Check items included (3 points)
    sub_items = submission.get("items", [])
    key_items = answer_key.get("items", [])
    
    # Create a mapping of item names
    sub_items_names = [item.get("itemName", "").lower() for item in sub_items]
    key_items_names = [item.get("itemName", "").lower() for item in key_items]
    
    # Count how many required items are included
    items_included = sum(1 for name in key_items_names if any(name in sub_name or sub_name in name for sub_name in sub_items_names))
    item_points = round(3 * (items_included / max(1, len(key_items))))
    
    results["details"]["itemsIncluded"] = {
        "earned": item_points, 
        "possible": 3, 
        "comment": f"Required items included: {items_included}/{len(key_items)}"
    }
    results["points_earned"] += item_points
    
    # Check quantities (3 points)
    # Match items by name and check quantities
    qty_correct = 0
    for key_item in key_items:
        key_name = key_item.get("itemName", "").lower()
        key_qty = key_item.get("quantity")
        
        for sub_item in sub_items:
            sub_name = sub_item.get("itemName", "").lower()
            if key_name in sub_name or sub_name in key_name:
                if sub_item.get("quantity") == key_qty:
                    qty_correct += 1
                break
    
    qty_points = round(3 * (qty_correct / max(1, len(key_items))))
    results["details"]["itemQuantities"] = {
        "earned": qty_points, 
        "possible": 3, 
        "comment": f"Correct quantities: {qty_correct}/{len(key_items)}"
    }
    results["points_earned"] += qty_points
    
    # Check specifications (3 points)
    # This is a simplified check - in reality, we'd need more sophisticated text matching
    spec_correct = 0
    for key_item in key_items:
        key_name = key_item.get("itemName", "").lower()
        key_spec = key_item.get("specifications", "").lower()
        
        for sub_item in sub_items:
            sub_name = sub_item.get("itemName", "").lower()
            if key_name in sub_name or sub_name in key_name:
                sub_spec = sub_item.get("specifications", "").lower()
                # Check if key terms from the answer key specs appear in the submission
                key_terms = ["adjustable", "warranty", "dimensions"]
                if any(term in sub_spec for term in key_terms):
                    spec_correct += 1
                break
    
    spec_points = round(3 * (spec_correct / max(1, len(key_items))))
    results["details"]["specifications"] = {
        "earned": spec_points, 
        "possible": 3, 
        "comment": f"Adequate specifications: {spec_correct}/{len(key_items)}"
    }
    results["points_earned"] += spec_points
    
    # Check evaluation criteria (2 points)
    sub_criteria = submission.get("evaluationCriteria", [])
    key_criteria = answer_key.get("evaluationCriteria", [])
    
    # Create mappings of criterion names to weights
    sub_criteria_map = {item.get("criterionName", "").lower(): item.get("weight") for item in sub_criteria}
    key_criteria_map = {item.get("criterionName", "").lower(): item.get("weight") for item in key_criteria}
    
    # Check if all required criteria are included with correct weights
    criteria_correct = sum(1 for name, weight in key_criteria_map.items() 
                          if name in sub_criteria_map and sub_criteria_map[name] == weight)
    
    criteria_points = round(2 * (criteria_correct / max(1, len(key_criteria))))
    results["details"]["evaluationCriteria"] = {
        "earned": criteria_points, 
        "possible": 2, 
        "comment": f"Correct evaluation criteria: {criteria_correct}/{len(key_criteria)}"
    }
    results["points_earned"] += criteria_points
    
    # Check inclusion of standard terms (1 point)
    if submission.get("termsIncluded") == answer_key.get("termsIncluded"):
        results["details"]["termsIncluded"] = {"earned": 1, "possible": 1, "comment": "Correctly indicated terms inclusion"}
        results["points_earned"] += 1
    else:
        results["details"]["termsIncluded"] = {"earned": 0, "possible": 1, "comment": "Incorrectly indicated terms inclusion"}
    
    # Calculate percentage
    results["percentage"] = round((results["points_earned"] / results["points_possible"]) * 100, 2)
    
    return results

def evaluate_exercise3(submission, answer_key):
    """Evaluate the requisition review exercise"""
    results = {
        "points_possible": 25,
        "points_earned": 0,
        "percentage": 0,
        "details": {}
    }
    
    sub_requisitions = submission.get("requisitions", [])
    key_requisitions = answer_key.get("requisitions", [])
    
    # Create mappings by requisition number
    sub_req_map = {req.get("requisitionNumber"): req for req in sub_requisitions}
    key_req_map = {req.get("requisitionNumber"): req for req in key_requisitions}
    
    # Check completeness assessment (3 points)
    completeness_correct = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and sub_req_map[req_num].get("isComplete") == key_req.get("isComplete"):
            completeness_correct += 1
    
    completeness_points = round(3 * (completeness_correct / max(1, len(key_requisitions))))
    results["details"]["completenessAssessment"] = {
        "earned": completeness_points, 
        "possible": 3, 
        "comment": f"Correct completeness assessments: {completeness_correct}/{len(key_requisitions)}"
    }
    results["points_earned"] += completeness_points
    
    # Check catalog compliance assessment (3 points)
    catalog_correct = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and sub_req_map[req_num].get("itemsInCatalog") == key_req.get("itemsInCatalog"):
            catalog_correct += 1
    
    catalog_points = round(3 * (catalog_correct / max(1, len(key_requisitions))))
    results["details"]["catalogCompliance"] = {
        "earned": catalog_points, 
        "possible": 3, 
        "comment": f"Correct catalog compliance assessments: {catalog_correct}/{len(key_requisitions)}"
    }
    results["points_earned"] += catalog_points
    
    # Check policy compliance assessment (3 points)
    policy_correct = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and sub_req_map[req_num].get("policyCompliant") == key_req.get("policyCompliant"):
            policy_correct += 1
    
    policy_points = round(3 * (policy_correct / max(1, len(key_requisitions))))
    results["details"]["policyCompliance"] = {
        "earned": policy_points, 
        "possible": 3, 
        "comment": f"Correct policy compliance assessments: {policy_correct}/{len(key_requisitions)}"
    }
    results["points_earned"] += policy_points
    
    # Check total calculations (3 points)
    total_correct = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and is_close_enough(sub_req_map[req_num].get("calculatedTotal"), key_req.get("calculatedTotal"), 0.05):
            total_correct += 1
    
    total_points = round(3 * (total_correct / max(1, len(key_requisitions))))
    results["details"]["totalCalculations"] = {
        "earned": total_points, 
        "possible": 3, 
        "comment": f"Correct total calculations: {total_correct}/{len(key_requisitions)}"
    }
    results["points_earned"] += total_points
    
    # Check decisions (6 points - 2 per requisition)
    decision_correct = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and sub_req_map[req_num].get("decision") == key_req.get("decision"):
            decision_correct += 1
    
    decision_points = round(6 * (decision_correct / max(1, len(key_requisitions))))
    results["details"]["decisions"] = {
        "earned": decision_points, 
        "possible": 6, 
        "comment": f"Correct decisions: {decision_correct}/{len(key_requisitions)}"
    }
    results["points_earned"] += decision_points
    
    # Check justifications (3 points)
    # This is a simplified check - in reality, we'd need more sophisticated text matching
    justification_score = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map:
            sub_just = sub_req_map[req_num].get("justification", "").lower()
            # Check if justification contains key terms based on the decision
            if sub_req_map[req_num].get("decision") == "approve" and "approv" in sub_just:
                justification_score += 1
            elif sub_req_map[req_num].get("decision") == "reject" and "reject" in sub_just:
                justification_score += 1
            elif sub_req_map[req_num].get("decision") == "return" and "return" in sub_just:
                justification_score += 1
    
    justification_points = round(3 * (justification_score / max(1, len(key_requisitions))))
    results["details"]["justifications"] = {
        "earned": justification_points, 
        "possible": 3, 
        "comment": f"Reasonable justifications: {justification_score}/{len(key_requisitions)}"
    }
    results["points_earned"] += justification_points
    
    # Check missing information identification (2 points)
    # Only relevant for incomplete requisitions
    missing_info_score = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map and not key_req.get("isComplete"):
            sub_missing = sub_req_map[req_num].get("missingInformation", "").lower()
            if sub_missing and len(sub_missing) > 5:  # Simple check that something meaningful was entered
                missing_info_score += 1
    
    # Count how many requisitions should have missing information identified
    incomplete_reqs = sum(1 for req in key_requisitions if not req.get("isComplete"))
    
    missing_info_points = 0
    if incomplete_reqs > 0:
        missing_info_points = round(2 * (missing_info_score / incomplete_reqs))
    elif missing_info_score == 0:  # If no requisitions should have missing info and none were identified
        missing_info_points = 2
    
    results["details"]["missingInformation"] = {
        "earned": missing_info_points, 
        "possible": 2, 
        "comment": f"Identified missing information where needed: {missing_info_score}/{max(1, incomplete_reqs)}"
    }
    results["points_earned"] += missing_info_points
    
    # Check vendor suggestions (2 points)
    vendor_score = 0
    for req_num, key_req in key_req_map.items():
        if req_num in sub_req_map:
            sub_vendor = sub_req_map[req_num].get("suggestedVendor", "").lower()
            key_vendor = key_req.get("suggestedVendor", "").lower()
            
            # Check if the suggested vendor contains the key vendor name
            if key_vendor and (key_vendor in sub_vendor or sub_vendor in key_vendor):
                vendor_score += 1
    
    vendor_points = round(2 * (vendor_score / max(1, len(key_requisitions))))
    results["details"]["vendorSuggestions"] = {
        "earned": vendor_points, 
        "possible": 2, 
        "comment": f"Appropriate vendor suggestions: {vendor_score}/{len(key_requisitions)}"
    }
    results["points_earned"] += vendor_points
    
    # Calculate percentage
    results["percentage"] = round((results["points_earned"] / results["points_possible"]) * 100, 2)
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission"""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "modelVersion": submission.get("modelVersion", "Unknown"),
        "exercise1": evaluate_exercise1(submission.get("exercise1", {}), answer_key.get("exercise1", {})),
        "exercise2": evaluate_exercise2(submission.get("exercise2", {}), answer_key.get("exercise2", {})),
        "exercise3": evaluate_exercise3(submission.get("exercise3", {}), answer_key.get("exercise3", {}))
    }
    
    # Calculate overall score
    total_points_possible = (
        results["exercise1"]["points_possible"] + 
        results["exercise2"]["points_possible"] + 
        results["exercise3"]["points_possible"]
    )
    
    total_points_earned = (
        results["exercise1"]["points_earned"] + 
        results["exercise2"]["points_earned"] + 
        results["exercise3"]["points_earned"]
    )
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    
    # Check if candidate passed
    min_overall_score = 80
    min_exercise_score = 70
    
    passed_overall = results["overall_score"] >= min_overall_score
    passed_ex1 = results["exercise1"]["percentage"] >= min_exercise_score
    passed_ex2 = results["exercise2"]["percentage"] >= min_exercise_score
    passed_ex3 = results["exercise3"]["percentage"] >= min_exercise_score
    
    results["passed"] = passed_overall and passed_ex1 and passed_ex2 and passed_ex3
    
    # Add pass/fail reasons
    results["pass_fail_details"] = {
        "overall_requirement": f"≥{min_overall_score}% overall",
        "overall_result": f"{results['overall_score']}% - {'PASS' if passed_overall else 'FAIL'}",
        "exercise_requirements": f"≥{min_exercise_score}% on each exercise",
        "exercise1_result": f"{results['exercise1']['percentage']}% - {'PASS' if passed_ex1 else 'FAIL'}",
        "exercise2_result": f"{results['exercise2']['percentage']}% - {'PASS' if passed_ex2 else 'FAIL'}",
        "exercise3_result": f"{results['exercise3']['percentage']}% - {'PASS' if passed_ex3 else 'FAIL'}"
    }
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json_file(results, "test_results.json")
    
    # Print summary
    print(f"\nEvaluation Summary for Candidate: {results['candidateId']}")
    print(f"Model Version: {results['modelVersion']}")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Exercise 1 Score: {results['exercise1']['percentage']}%")
    print(f"Exercise 2 Score: {results['exercise2']['percentage']}%")
    print(f"Exercise 3 Score: {results['exercise3']['percentage']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()