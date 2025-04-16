#!/usr/bin/env python3
import json
import sys
import os

def evaluate_task1(submission, answer_key):
    results = {
        "points": 0,
        "max_points": 40,
        "details": {}
    }
    
    # Check chair selection within price range (5 points per chair, 15 total)
    valid_chairs = {
        "OfficeMax": ["OM-EC550", "OM-EC720"],
        "Staples": ["US-DX450", "SP-1500TF", "ST-HY100"],
        "Corporate Furnishings": ["CF-TM400", "CF-EP800"]
    }
    
    results["details"]["chair_selection"] = {"points": 0, "max_points": 15, "notes": []}
    
    for chair in submission.get("chair_comparison", []):
        supplier = chair.get("supplier")
        model = chair.get("model")
        
        if supplier in valid_chairs and model in valid_chairs[supplier]:
            results["details"]["chair_selection"]["points"] += 5
            results["details"]["chair_selection"]["notes"].append(f"Correct: {supplier} {model} is within price range")
        else:
            results["details"]["chair_selection"]["notes"].append(f"Incorrect: {supplier} {model} is not a valid selection")
    
    # Check model numbers (3 points per chair, 9 total)
    results["details"]["model_numbers"] = {"points": 0, "max_points": 9, "notes": []}
    
    for chair in submission.get("chair_comparison", []):
        supplier = chair.get("supplier")
        model = chair.get("model")
        
        # Check if the model number is provided and formatted correctly
        if model and isinstance(model, str) and model.strip():
            results["details"]["model_numbers"]["points"] += 3
            results["details"]["model_numbers"]["notes"].append(f"Correct: Model {model} for {supplier} is properly formatted")
        else:
            results["details"]["model_numbers"]["notes"].append(f"Incorrect: Model for {supplier} is missing or improperly formatted")
    
    # Check price values (2 points per chair, 6 total)
    results["details"]["price_values"] = {"points": 0, "max_points": 6, "notes": []}
    
    for chair in submission.get("chair_comparison", []):
        supplier = chair.get("supplier")
        price = chair.get("price")
        
        # Check if price is a number and in the valid range ($200-$500)
        if isinstance(price, (int, float)) and 200 <= price <= 500:
            results["details"]["price_values"]["points"] += 2
            results["details"]["price_values"]["notes"].append(f"Correct: Price ${price} for {supplier} is within range")
        else:
            results["details"]["price_values"]["notes"].append(f"Incorrect: Price for {supplier} is missing or outside the valid range")
    
    # Check warranty information (2 points per chair, 6 total)
    results["details"]["warranty_info"] = {"points": 0, "max_points": 6, "notes": []}
    
    for chair in submission.get("chair_comparison", []):
        supplier = chair.get("supplier")
        warranty = chair.get("warranty_years")
        
        # Check if warranty is a positive integer
        if isinstance(warranty, int) and warranty > 0:
            results["details"]["warranty_info"]["points"] += 2
            results["details"]["warranty_info"]["notes"].append(f"Correct: Warranty {warranty} years for {supplier} is valid")
        else:
            results["details"]["warranty_info"]["notes"].append(f"Incorrect: Warranty for {supplier} is missing or invalid")
    
    # Check lowest price chair (2 points)
    results["details"]["lowest_price_chair"] = {"points": 0, "max_points": 2, "notes": []}
    
    lowest_price_chair = submission.get("lowest_price_chair", {})
    lowest_supplier = lowest_price_chair.get("supplier")
    lowest_model = lowest_price_chair.get("model")
    
    if lowest_supplier == "Staples" and lowest_model == "US-DX450":
        results["details"]["lowest_price_chair"]["points"] = 2
        results["details"]["lowest_price_chair"]["notes"].append("Correct: Identified Staples US-DX450 as lowest price chair")
    elif lowest_supplier == "Staples" and lowest_model == "ST-HY100":
        # Alternative correct answer if all chairs are considered
        results["details"]["lowest_price_chair"]["points"] = 2
        results["details"]["lowest_price_chair"]["notes"].append("Correct: Identified Staples ST-HY100 as lowest price chair")
    else:
        results["details"]["lowest_price_chair"]["notes"].append(f"Incorrect: {lowest_supplier} {lowest_model} is not the lowest price chair")
    
    # Check best warranty chair (2 points)
    results["details"]["best_warranty_chair"] = {"points": 0, "max_points": 2, "notes": []}
    
    best_warranty_chair = submission.get("best_warranty_chair", {})
    best_supplier = best_warranty_chair.get("supplier")
    best_model = best_warranty_chair.get("model")
    
    if best_supplier == "Staples" and best_model == "SP-1500TF":
        results["details"]["best_warranty_chair"]["points"] = 2
        results["details"]["best_warranty_chair"]["notes"].append("Correct: Identified Staples SP-1500TF as best warranty chair")
    else:
        results["details"]["best_warranty_chair"]["notes"].append(f"Incorrect: {best_supplier} {best_model} is not the best warranty chair")
    
    # Calculate total points for Task 1
    results["points"] = sum(detail["points"] for detail in results["details"].values())
    
    return results

def evaluate_task2(submission, answer_key):
    results = {
        "points": 0,
        "max_points": 30,
        "details": {}
    }
    
    # Check safety standard (10 points)
    results["details"]["safety_standard"] = {"points": 0, "max_points": 10, "notes": []}
    
    submitted_standard = submission.get("safety_standard", "")
    correct_standard = answer_key.get("safety_standard", "")
    
    if submitted_standard == correct_standard:
        results["details"]["safety_standard"]["points"] = 10
        results["details"]["safety_standard"]["notes"].append(f"Correct: Identified {correct_standard} as the safety standard")
    else:
        results["details"]["safety_standard"]["notes"].append(f"Incorrect: Submitted {submitted_standard} instead of {correct_standard}")
    
    # Check certification (10 points)
    results["details"]["certification"] = {"points": 0, "max_points": 10, "notes": []}
    
    submitted_certification = submission.get("certification_required", "")
    correct_certification = answer_key.get("certification_required", "")
    
    if submitted_certification == correct_certification:
        results["details"]["certification"]["points"] = 10
        results["details"]["certification"]["notes"].append(f"Correct: Identified {correct_certification} as the required certification")
    else:
        results["details"]["certification"]["notes"].append(f"Incorrect: Submitted {submitted_certification} instead of {correct_certification}")
    
    # Check minimum thickness (10 points)
    results["details"]["minimum_thickness"] = {"points": 0, "max_points": 10, "notes": []}
    
    submitted_thickness = submission.get("minimum_thickness_mm")
    correct_thickness = answer_key.get("minimum_thickness_mm")
    
    if submitted_thickness == correct_thickness:
        results["details"]["minimum_thickness"]["points"] = 10
        results["details"]["minimum_thickness"]["notes"].append(f"Correct: Identified {correct_thickness}mm as the minimum thickness")
    else:
        results["details"]["minimum_thickness"]["notes"].append(f"Incorrect: Submitted {submitted_thickness}mm instead of {correct_thickness}mm")
    
    # Calculate total points for Task 2
    results["points"] = sum(detail["points"] for detail in results["details"].values())
    
    return results

def evaluate_task3(submission, answer_key):
    results = {
        "points": 0,
        "max_points": 30,
        "details": {}
    }
    
    # Check supplier identification (5 points per supplier, 15 total)
    results["details"]["supplier_identification"] = {"points": 0, "max_points": 15, "notes": []}
    
    suppliers = submission.get("suppliers", [])
    
    for i, supplier in enumerate(suppliers):
        if i >= 3:  # Only evaluate up to 3 suppliers
            break
            
        name = supplier.get("name", "")
        
        if name and isinstance(name, str) and len(name) > 3:
            results["details"]["supplier_identification"]["points"] += 5
            results["details"]["supplier_identification"]["notes"].append(f"Supplier {i+1}: {name} - Valid supplier name")
        else:
            results["details"]["supplier_identification"]["notes"].append(f"Supplier {i+1}: {name} - Invalid or missing name")
    
    # Check supplier information completeness (3 points per supplier, 9 total)
    results["details"]["supplier_information"] = {"points": 0, "max_points": 9, "notes": []}
    
    for i, supplier in enumerate(suppliers):
        if i >= 3:  # Only evaluate up to 3 suppliers
            break
            
        name = supplier.get("name", "")
        location = supplier.get("location", "")
        min_order = supplier.get("minimum_order")
        lead_time = supplier.get("lead_time_days")
        
        # Award points only if all required information is provided and valid
        if (name and isinstance(name, str) and 
            location and isinstance(location, str) and 
            isinstance(min_order, int) and min_order > 0 and
            isinstance(lead_time, int) and lead_time > 0):
            
            results["details"]["supplier_information"]["points"] += 3
            results["details"]["supplier_information"]["notes"].append(f"Supplier {i+1}: Complete and valid information")
        else:
            results["details"]["supplier_information"]["notes"].append(f"Supplier {i+1}: Incomplete or invalid information")
    
    # Check fastest delivery supplier (3 points)
    results["details"]["fastest_delivery"] = {"points": 0, "max_points": 3, "notes": []}
    
    fastest_supplier = submission.get("fastest_delivery_supplier", "")
    
    # Find the supplier with the lowest lead time
    min_lead_time = float('inf')
    actual_fastest = ""
    
    for supplier in suppliers:
        name = supplier.get("name", "")
        lead_time = supplier.get("lead_time_days")
        
        if isinstance(lead_time, int) and lead_time < min_lead_time:
            min_lead_time = lead_time
            actual_fastest = name
    
    if fastest_supplier == actual_fastest and fastest_supplier:
        results["details"]["fastest_delivery"]["points"] = 3
        results["details"]["fastest_delivery"]["notes"].append(f"Correct: {fastest_supplier} has the fastest delivery time ({min_lead_time} days)")
    else:
        results["details"]["fastest_delivery"]["notes"].append(f"Incorrect: Submitted {fastest_supplier} but {actual_fastest} has the fastest delivery time ({min_lead_time} days)")
    
    # Check lowest minimum order supplier (3 points)
    results["details"]["lowest_minimum_order"] = {"points": 0, "max_points": 3, "notes": []}
    
    lowest_min_order_supplier = submission.get("lowest_minimum_order_supplier", "")
    
    # Find the supplier with the lowest minimum order
    min_order = float('inf')
    actual_lowest = ""
    
    for supplier in suppliers:
        name = supplier.get("name", "")
        order = supplier.get("minimum_order")
        
        if isinstance(order, int) and order < min_order:
            min_order = order
            actual_lowest = name
    
    if lowest_min_order_supplier == actual_lowest and lowest_min_order_supplier:
        results["details"]["lowest_minimum_order"]["points"] = 3
        results["details"]["lowest_minimum_order"]["notes"].append(f"Correct: {lowest_min_order_supplier} has the lowest minimum order ({min_order} units)")
    else:
        results["details"]["lowest_minimum_order"]["notes"].append(f"Incorrect: Submitted {lowest_min_order_supplier} but {actual_lowest} has the lowest minimum order ({min_order} units)")
    
    # Calculate total points for Task 3
    results["points"] = sum(detail["points"] for detail in results["details"].values())
    
    return results

def evaluate_submission(submission_data, answer_key_data):
    results = {
        "task1": evaluate_task1(submission_data.get("task1", {}), answer_key_data.get("task1", {})),
        "task2": evaluate_task2(submission_data.get("task2", {}), answer_key_data.get("task2", {})),
        "task3": evaluate_task3(submission_data.get("task3", {}), answer_key_data.get("task3", {}))
    }
    
    # Calculate total score
    total_points = sum(task["points"] for task in results.values())
    max_points = sum(task["max_points"] for task in results.values())
    overall_score = (total_points / max_points) * 100 if max_points > 0 else 0
    
    # Determine pass status
    pass_status = "Strong Pass" if overall_score >= 90 else "Pass" if overall_score >= 75 else "Fail"
    
    # Check critical requirements
    critical_requirements_met = True
    task1_chairs_correct = results["task1"]["details"]["chair_selection"]["points"] >= 10  # At least 2 chairs correct
    task2_standard_correct = results["task2"]["details"]["safety_standard"]["points"] > 0
    task2_thickness_correct = results["task2"]["details"]["minimum_thickness"]["points"] > 0
    task3_suppliers_identified = results["task3"]["details"]["supplier_identification"]["points"] >= 10  # At least 2 suppliers identified
    
    if not (task1_chairs_correct and task2_standard_correct and task2_thickness_correct and task3_suppliers_identified):
        critical_requirements_met = False
        pass_status = "Fail (Critical Requirements Not Met)"
    
    # Compile final results
    final_results = {
        "candidate_id": submission_data.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "total_points": total_points,
        "max_points": max_points,
        "pass_status": pass_status,
        "critical_requirements_met": critical_requirements_met,
        "task_results": results
    }
    
    return final_results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Check if files exist
    for file_path in [submission_file, answer_key_file]:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            sys.exit(1)
    
    # Load submission and answer key
    try:
        with open(submission_file, 'r') as f:
            submission_data = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)
    
    # Evaluate submission
    results = evaluate_submission(submission_data, answer_key_data)
    
    # Save results to file
    try:
        with open("test_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        print("Evaluation completed. Results saved to test_results.json")
    except Exception as e:
        print(f"Error writing results file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()