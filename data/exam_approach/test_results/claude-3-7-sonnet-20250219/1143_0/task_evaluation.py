import json
import sys
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        sys.exit(1)

def evaluate_scenario1(submission: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate Purchase Order Preparation scenario"""
    max_score = 30
    score = 0
    feedback = []
    
    # Vendor selection (5 points)
    if submission.get("vendor_id") == answer_key.get("vendor_id"):
        score += 5
        feedback.append("✓ Correct vendor selected")
    else:
        feedback.append(f"✗ Incorrect vendor selected. Expected: {answer_key.get('vendor_id')}, Got: {submission.get('vendor_id')}")
    
    # Check line items
    submission_items = {item.get("item_code"): item for item in submission.get("line_items", [])}
    key_items = {item.get("item_code"): item for item in answer_key.get("line_items", [])}
    
    # Item codes (8 points, 2 points each)
    expected_codes = set(key_items.keys())
    submitted_codes = set(submission_items.keys())
    
    correct_codes = expected_codes.intersection(submitted_codes)
    for code in correct_codes:
        score += 2
        feedback.append(f"✓ Correct item code: {code}")
    
    for code in expected_codes - submitted_codes:
        feedback.append(f"✗ Missing item code: {code}")
    
    for code in submitted_codes - expected_codes:
        feedback.append(f"✗ Unexpected item code: {code}")
    
    # Quantities, unit prices, account codes (12 points total, 1 point each per item)
    for code in correct_codes:
        # Check quantity (1 point each)
        if submission_items[code].get("quantity") == key_items[code].get("quantity"):
            score += 1
            feedback.append(f"✓ Correct quantity for {code}")
        else:
            feedback.append(f"✗ Incorrect quantity for {code}. Expected: {key_items[code].get('quantity')}, Got: {submission_items[code].get('quantity')}")
        
        # Check unit price (1 point each)
        if submission_items[code].get("unit_price") == key_items[code].get("unit_price"):
            score += 1
            feedback.append(f"✓ Correct unit price for {code}")
        else:
            feedback.append(f"✗ Incorrect unit price for {code}. Expected: {key_items[code].get('unit_price')}, Got: {submission_items[code].get('unit_price')}")
        
        # Check account code (1 point each)
        if submission_items[code].get("account_code") == key_items[code].get("account_code"):
            score += 1
            feedback.append(f"✓ Correct account code for {code}")
        else:
            feedback.append(f"✗ Incorrect account code for {code}. Expected: {key_items[code].get('account_code')}, Got: {submission_items[code].get('account_code')}")
    
    # Total amount calculation (3 points)
    # Allow for small differences due to rounding
    if abs(submission.get("total_amount", 0) - answer_key.get("total_amount", 0)) < 0.1:
        score += 3
        feedback.append("✓ Correct total amount")
    elif abs(submission.get("total_amount", 0) - answer_key.get("total_amount", 0)) < 5:
        score += 2
        feedback.append("⚠ Total amount is slightly off, possibly due to rounding")
    else:
        feedback.append(f"✗ Incorrect total amount. Expected: {answer_key.get('total_amount')}, Got: {submission.get('total_amount')}")
    
    # Delivery date (2 points)
    if submission.get("delivery_date") == answer_key.get("delivery_date"):
        score += 2
        feedback.append("✓ Correct delivery date")
    else:
        feedback.append(f"✗ Incorrect delivery date. Expected: {answer_key.get('delivery_date')}, Got: {submission.get('delivery_date')}")
    
    # Check if passing score (21 points, 70%)
    passed = score >= 21
    
    return score, max_score, feedback

def evaluate_scenario2(submission: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate Bid Solicitation scenario"""
    max_score = 30
    score = 0
    feedback = []
    
    # RFP specifications accuracy (12 points, 2 points per specification)
    rfp_specs = submission.get("rfp_specifications", {})
    key_specs = answer_key.get("rfp_specifications", {})
    
    spec_keys = ["print_speed", "monthly_volume", "network_capabilities", 
                 "security_features", "mobile_printing", "additional_features"]
    
    for key in spec_keys:
        # Check if the required specification exists and is correct
        if key in rfp_specs and rfp_specs[key] == key_specs[key]:
            score += 2
            feedback.append(f"✓ Correct RFP specification: {key}")
        else:
            feedback.append(f"✗ Incorrect RFP specification: {key}. Expected: {key_specs.get(key)}, Got: {rfp_specs.get(key)}")
    
    # Vendor selection (6 points)
    vendor_analysis = submission.get("vendor_analysis", {})
    key_analysis = answer_key.get("vendor_analysis", {})
    
    if vendor_analysis.get("selected_vendor") == key_analysis.get("selected_vendor"):
        score += 6
        feedback.append("✓ Correct vendor selected")
    else:
        feedback.append(f"✗ Incorrect vendor selected. Expected: {key_analysis.get('selected_vendor')}, Got: {vendor_analysis.get('selected_vendor')}")
    
    # Cost analysis (4 points)
    if abs(vendor_analysis.get("total_cost", 0) - key_analysis.get("total_cost", 0)) < 0.1:
        score += 4
        feedback.append("✓ Correct total cost")
    elif abs(vendor_analysis.get("total_cost", 0) - key_analysis.get("total_cost", 0)) < 5:
        score += 3
        feedback.append("⚠ Total cost is slightly off, possibly due to rounding")
    else:
        feedback.append(f"✗ Incorrect total cost. Expected: {key_analysis.get('total_cost')}, Got: {vendor_analysis.get('total_cost')}")
    
    # Delivery timeframe (2 points)
    if vendor_analysis.get("delivery_timeframe") == key_analysis.get("delivery_timeframe"):
        score += 2
        feedback.append("✓ Correct delivery timeframe")
    else:
        feedback.append(f"✗ Incorrect delivery timeframe. Expected: {key_analysis.get('delivery_timeframe')}, Got: {vendor_analysis.get('delivery_timeframe')}")
    
    # Warranty evaluation (3 points)
    if vendor_analysis.get("warranty_period") == key_analysis.get("warranty_period"):
        score += 3
        feedback.append("✓ Correct warranty period")
    else:
        feedback.append(f"✗ Incorrect warranty period. Expected: {key_analysis.get('warranty_period')}, Got: {vendor_analysis.get('warranty_period')}")
    
    # Selection justification (3 points)
    if "selection_justification" in submission and len(submission["selection_justification"]) > 20:
        score += 3
        feedback.append("✓ Provided reasonable selection justification")
    elif "selection_justification" in submission:
        score += 1
        feedback.append("⚠ Selection justification provided but insufficient detail")
    else:
        feedback.append("✗ Missing selection justification")
    
    # Check if passing score (21 points, 70%)
    passed = score >= 21
    
    return score, max_score, feedback

def evaluate_scenario3(submission: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate Requisition Review scenario"""
    max_score = 30
    score = 0
    feedback = []
    
    for i in range(1, 4):
        req_key = f"requisition{i}"
        
        # Status determination (4 points per requisition, 12 points total)
        sub_status = submission.get(req_key, {}).get("status")
        key_status = answer_key.get(req_key, {}).get("status")
        
        if sub_status == key_status:
            score += 4
            feedback.append(f"✓ Correct status for {req_key}: {sub_status}")
        else:
            feedback.append(f"✗ Incorrect status for {req_key}. Expected: {key_status}, Got: {sub_status}")
        
        # Issue identification (approximately 2 points per correct issue, 12 points total)
        sub_issues = set(submission.get(req_key, {}).get("issues", []))
        key_issues = set(answer_key.get(req_key, {}).get("issues", []))
        
        # Calculate points for issues based on proportion of correct issues
        num_key_issues = len(key_issues)
        if num_key_issues > 0:
            correct_issues = len(sub_issues.intersection(key_issues))
            points_per_issue = 2 if num_key_issues > 0 else 0
            issue_points = min(points_per_issue * correct_issues, 4)  # Max 4 points per requisition for issues
            score += issue_points
            
            if correct_issues == num_key_issues:
                feedback.append(f"✓ Correctly identified all issues for {req_key}")
            elif correct_issues > 0:
                feedback.append(f"⚠ Identified {correct_issues} out of {num_key_issues} issues for {req_key}")
            else:
                feedback.append(f"✗ Failed to identify any issues for {req_key}")
        
        # Required corrections (approximately 1 point per correction, 6 points total)
        sub_corrections = set(submission.get(req_key, {}).get("required_corrections", []))
        key_corrections = set(answer_key.get(req_key, {}).get("required_corrections", []))
        
        # Calculate points for corrections based on proportion of correct corrections
        num_key_corrections = len(key_corrections)
        if num_key_corrections > 0:
            correct_corrections = len(sub_corrections.intersection(key_corrections))
            points_per_correction = 1 if num_key_corrections > 0 else 0
            correction_points = min(points_per_correction * correct_corrections, 2)  # Max 2 points per requisition for corrections
            score += correction_points
            
            if correct_corrections == num_key_corrections:
                feedback.append(f"✓ Correctly identified all required corrections for {req_key}")
            elif correct_corrections > 0:
                feedback.append(f"⚠ Identified {correct_corrections} out of {num_key_corrections} required corrections for {req_key}")
            else:
                feedback.append(f"✗ Failed to identify any required corrections for {req_key}")
    
    # Check if passing score (21 points, 70%)
    passed = score >= 21
    
    return score, max_score, feedback

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key"""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "scenarios": {}
    }
    
    # Evaluate each scenario
    scenario1_score, scenario1_max, scenario1_feedback = evaluate_scenario1(
        submission.get("scenario1", {}), answer_key.get("scenario1", {})
    )
    results["scenarios"]["scenario1"] = {
        "score": scenario1_score,
        "max_score": scenario1_max,
        "percentage": round(scenario1_score / scenario1_max * 100, 2),
        "passed": scenario1_score >= 21,
        "feedback": scenario1_feedback
    }
    
    scenario2_score, scenario2_max, scenario2_feedback = evaluate_scenario2(
        submission.get("scenario2", {}), answer_key.get("scenario2", {})
    )
    results["scenarios"]["scenario2"] = {
        "score": scenario2_score,
        "max_score": scenario2_max,
        "percentage": round(scenario2_score / scenario2_max * 100, 2),
        "passed": scenario2_score >= 21,
        "feedback": scenario2_feedback
    }
    
    scenario3_score, scenario3_max, scenario3_feedback = evaluate_scenario3(
        submission.get("scenario3", {}), answer_key.get("scenario3", {})
    )
    results["scenarios"]["scenario3"] = {
        "score": scenario3_score,
        "max_score": scenario3_max,
        "percentage": round(scenario3_score / scenario3_max * 100, 2),
        "passed": scenario3_score >= 21,
        "feedback": scenario3_feedback
    }
    
    # Calculate total score
    total_score = scenario1_score + scenario2_score + scenario3_score
    total_max = scenario1_max + scenario2_max + scenario3_max
    total_percentage = round(total_score / total_max * 100, 2)
    
    # Count passed scenarios
    passed_scenarios = sum([
        1 if results["scenarios"]["scenario1"]["passed"] else 0,
        1 if results["scenarios"]["scenario2"]["passed"] else 0,
        1 if results["scenarios"]["scenario3"]["passed"] else 0
    ])
    
    # Determine overall pass/fail status
    passed = passed_scenarios >= 2 and total_percentage >= 70
    
    results["total_score"] = total_score
    results["total_max_score"] = total_max
    results["overall_score"] = total_percentage
    results["passed_scenarios"] = passed_scenarios
    results["overall_passed"] = passed
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_filename = sys.argv[1]
    answer_key_filename = sys.argv[2]
    
    submission = load_json_file(submission_filename)
    answer_key = load_json_file(answer_key_filename)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Overall status: {'PASSED' if results['overall_passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()