#!/usr/bin/env python3
"""
Evaluator for Purchase Agent Practical Exam
Usage: python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from pathlib import Path


def load_json_file(file_path):
    """Load a JSON file and return the content."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)


def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Purchase Order Preparation (40 points)"""
    score = 0
    feedback = []
    
    # Correct vendor selection: 5 points
    if submission["section1"]["purchase_order"]["vendor_id"] == answer_key["section1"]["purchase_order"]["vendor_id"]:
        score += 5
        feedback.append("Correctly selected Dell Enterprise as the vendor")
    else:
        feedback.append("Incorrect vendor selection")
    
    # Accurate item transfer (all 5 items): 10 points
    # Check if all items are present with correct information
    item_transfer_score = 0
    item_errors = []
    
    sub_items = submission["section1"]["item_list"]
    key_items = answer_key["section1"]["item_list"]
    
    if len(sub_items) == len(key_items):
        # Check each item
        for i, (sub_item, key_item) in enumerate(zip(sub_items, key_items)):
            if (sub_item["item_code"] == key_item["item_code"] and
                sub_item["description"] == key_item["description"] and
                sub_item["quantity"] == key_item["quantity"] and
                abs(sub_item["unit_price"] - key_item["unit_price"]) < 0.01):
                item_transfer_score += 2  # 2 points per correct item (5 items * 2 = 10 points)
            else:
                item_errors.append(f"Item {i+1} ({key_item['item_code']}) has incorrect information")
    else:
        item_errors.append(f"Expected {len(key_items)} items, found {len(sub_items)}")
    
    score += item_transfer_score
    if item_transfer_score == 10:
        feedback.append("All items transferred correctly")
    else:
        feedback.append(f"Item transfer issues ({item_transfer_score}/10 points): {', '.join(item_errors)}")
    
    # Correct calculations (subtotal, tax, shipping, total): 15 points
    calc_score = 0
    calc_errors = []
    
    # Check subtotal (5 points)
    if abs(submission["section1"]["order_totals"]["subtotal"] - answer_key["section1"]["order_totals"]["subtotal"]) < 0.5:
        calc_score += 5
    else:
        calc_errors.append(f"Incorrect subtotal: {submission['section1']['order_totals']['subtotal']} vs expected {answer_key['section1']['order_totals']['subtotal']}")
    
    # Check tax (5 points)
    if abs(submission["section1"]["order_totals"]["tax"] - answer_key["section1"]["order_totals"]["tax"]) < 0.01:
        calc_score += 5
    else:
        calc_errors.append(f"Incorrect tax: {submission['section1']['order_totals']['tax']} vs expected {answer_key['section1']['order_totals']['tax']}")
    
    # Check total (5 points)
    if abs(submission["section1"]["order_totals"]["total"] - answer_key["section1"]["order_totals"]["total"]) < 0.5:
        calc_score += 5
    else:
        calc_errors.append(f"Incorrect total: {submission['section1']['order_totals']['total']} vs expected {answer_key['section1']['order_totals']['total']}")
    
    score += calc_score
    if calc_score == 15:
        feedback.append("All calculations correct")
    else:
        feedback.append(f"Calculation issues ({calc_score}/15 points): {', '.join(calc_errors)}")
    
    # Identifying tax exemption status: 5 points (critical element)
    if submission["section1"]["tax_exempt_applied"] == answer_key["section1"]["tax_exempt_applied"]:
        score += 5
        feedback.append("Correctly identified tax exemption status")
    else:
        feedback.append("Failed to identify tax exemption status (critical element)")
    
    # Appropriate shipping selection: 5 points
    if submission["section1"]["purchase_order"]["shipping_method"] == answer_key["section1"]["purchase_order"]["shipping_method"]:
        score += 5
        feedback.append("Selected appropriate shipping method")
    else:
        # Allow some flexibility in shipping selection
        if submission["section1"]["purchase_order"]["shipping_method"] in ["Standard", "Express", "Vendor Shipping"]:
            score += 3
            feedback.append("Selected acceptable shipping method (partial credit)")
        else:
            feedback.append("Inappropriate shipping selection")
    
    # Check for critical element: tax exemption
    critical_fail = submission["section1"]["tax_exempt_applied"] != answer_key["section1"]["tax_exempt_applied"]
    
    return {
        "score": score,
        "max_score": 40,
        "percentage": (score / 40) * 100,
        "feedback": feedback,
        "critical_fail": critical_fail
    }


def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Bid Solicitation and Analysis (30 points)"""
    score = 0
    feedback = []
    
    # Vendor analysis (comparing all 3 bids): 10 points
    analysis_score = 0
    analysis_errors = []
    
    # Check if all vendors are analyzed
    sub_vendors = [v["vendor"] for v in submission["section2"]["cost_comparison"]]
    key_vendors = [v["vendor"] for v in answer_key["section2"]["cost_comparison"]]
    
    if set(sub_vendors) == set(key_vendors):
        analysis_score += 3
    else:
        analysis_errors.append("Missing vendor analysis")
    
    # Check if technical compliance is correctly identified for each vendor
    compliance_correct = True
    for sub_vendor in submission["section2"]["cost_comparison"]:
        vendor_name = sub_vendor["vendor"]
        key_vendor = next((v for v in answer_key["section2"]["cost_comparison"] if v["vendor"] == vendor_name), None)
        
        if key_vendor and sub_vendor.get("meets_specifications") != key_vendor.get("meets_specifications"):
            compliance_correct = False
            analysis_errors.append(f"Incorrect compliance assessment for {vendor_name}")
    
    if compliance_correct:
        analysis_score += 7
    
    score += analysis_score
    if analysis_score == 10:
        feedback.append("Thorough vendor analysis with correct specification compliance assessment")
    else:
        feedback.append(f"Vendor analysis issues ({analysis_score}/10 points): {', '.join(analysis_errors)}")
    
    # Correct vendor selection: 5 points (critical element)
    if submission["section2"]["selected_vendor"] == answer_key["section2"]["selected_vendor"]:
        score += 5
        feedback.append("Correctly selected TechnoSource Inc. as the vendor")
    else:
        feedback.append("Incorrect vendor selection (critical element)")
    
    # Selection justification based on policy: 5 points
    justification = submission["section2"]["selection_justification"].lower()
    if ("technical compliance" in justification or "specifications" in justification) and \
       ("officemax" in justification and "28 ppm" in justification) and \
       ("technosource" in justification):
        score += 5
        feedback.append("Excellent justification referencing policy criteria")
    elif "technosource" in justification and ("specifications" in justification or "compliance" in justification):
        score += 3
        feedback.append("Adequate justification but missing some key policy references")
    else:
        feedback.append("Insufficient justification for vendor selection")
    
    # RFQ answers (2 points each): 10 points
    rfq_score = 0
    rfq_errors = []
    
    for q_num in range(1, 6):
        q_key = f"question{q_num}"
        if submission["section2"]["rfq_answers"][q_key] == answer_key["section2"]["rfq_answers"][q_key]:
            rfq_score += 2
        else:
            rfq_errors.append(f"Incorrect answer for {q_key}")
    
    score += rfq_score
    if rfq_score == 10:
        feedback.append("All RFQ questions answered correctly")
    else:
        feedback.append(f"RFQ answer issues ({rfq_score}/10 points): {', '.join(rfq_errors)}")
    
    # Check for critical element: disqualification of OfficeMax
    officemax_disqualified = False
    for vendor in submission["section2"]["cost_comparison"]:
        if vendor["vendor"] == "OfficeMax Business" and vendor.get("meets_specifications") is False:
            officemax_disqualified = True
            break
    
    critical_fail = not officemax_disqualified or submission["section2"]["selected_vendor"] != answer_key["section2"]["selected_vendor"]
    
    return {
        "score": score,
        "max_score": 30,
        "percentage": (score / 30) * 100,
        "feedback": feedback,
        "critical_fail": critical_fail
    }


def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Requisition Review and Processing (30 points)"""
    score = 0
    feedback = []
    
    # Requisition 1
    req1_score = 0
    req1_feedback = []
    
    # Correct status: 3 points
    if submission["section3"]["requisition1"]["status"] == answer_key["section3"]["requisition1"]["status"]:
        req1_score += 3
        req1_feedback.append("Correct status identification")
    else:
        req1_feedback.append("Incorrect status for Requisition 1")
    
    # Identifying all errors: 5 points (critical element)
    key_errors = set([err.lower() for err in answer_key["section3"]["requisition1"]["errors"]])
    sub_errors = set([err.lower() for err in submission["section3"]["requisition1"]["errors"]])
    
    # Count how many of the key errors were found
    errors_found = len(key_errors.intersection(sub_errors))
    errors_extra = len(sub_errors - key_errors)
    
    if errors_found == len(key_errors) and errors_extra == 0:
        req1_score += 5
        req1_feedback.append("Correctly identified all errors")
    elif errors_found >= 2:  # Partial credit for finding at least 2 of 3 errors
        req1_score += 3
        req1_feedback.append(f"Found {errors_found} of {len(key_errors)} errors with {errors_extra} incorrect identifications")
    else:
        req1_feedback.append("Failed to identify critical errors")
    
    # Correct account code: 3 points
    if submission["section3"]["requisition1"]["account_code"] == answer_key["section3"]["requisition1"]["account_code"]:
        req1_score += 3
        req1_feedback.append("Correct account code assignment")
    else:
        req1_feedback.append("Incorrect account code")
    
    # Correct approval workflow: 3 points
    sub_workflow = submission["section3"]["requisition1"]["approval_workflow"]
    key_workflow = answer_key["section3"]["requisition1"]["approval_workflow"]
    
    if sub_workflow == key_workflow:
        req1_score += 3
        req1_feedback.append("Correct approval workflow")
    else:
        req1_feedback.append("Incorrect approval workflow")
    
    score += req1_score
    feedback.append(f"Requisition 1: {req1_score}/14 points - {', '.join(req1_feedback)}")
    
    # Requisition 2
    req2_score = 0
    req2_feedback = []
    
    # Correct status: 3 points
    if submission["section3"]["requisition2"]["status"] == answer_key["section3"]["requisition2"]["status"]:
        req2_score += 3
        req2_feedback.append("Correct status identification")
    else:
        req2_feedback.append("Incorrect status for Requisition 2")
    
    # Correct account code: 3 points
    if submission["section3"]["requisition2"]["account_code"] == answer_key["section3"]["requisition2"]["account_code"]:
        req2_score += 3
        req2_feedback.append("Correct account code assignment")
    else:
        req2_feedback.append("Incorrect account code")
    
    # Correct approval workflow: 3 points
    sub_workflow = submission["section3"]["requisition2"]["approval_workflow"]
    key_workflow = answer_key["section3"]["requisition2"]["approval_workflow"]
    
    if sub_workflow == key_workflow:
        req2_score += 3
        req2_feedback.append("Correct approval workflow")
    else:
        req2_feedback.append("Incorrect approval workflow")
    
    # Identifying all rush process steps: 7 points (critical element)
    key_steps = set([step.lower() for step in answer_key["section3"]["requisition2"]["rush_process_steps"]])
    sub_steps = set([step.lower() for step in submission["section3"]["requisition2"]["rush_process_steps"]])
    
    # Count how many of the key steps were found
    steps_found = len(key_steps.intersection(sub_steps))
    steps_extra = len(sub_steps - key_steps)
    
    if steps_found == len(key_steps) and steps_extra == 0:
        req2_score += 7
        req2_feedback.append("Correctly identified all rush process steps")
    elif steps_found >= 3:  # Partial credit for finding at least 3 of 5 steps
        req2_score += 4
        req2_feedback.append(f"Found {steps_found} of {len(key_steps)} rush process steps with {steps_extra} incorrect steps")
    else:
        req2_feedback.append("Failed to identify critical rush process steps")
    
    score += req2_score
    feedback.append(f"Requisition 2: {req2_score}/16 points - {', '.join(req2_feedback)}")
    
    # Check for critical elements
    all_req1_errors_identified = errors_found == len(key_errors)
    all_rush_steps_identified = steps_found >= 4  # Allow missing 1 of the 5 steps
    
    critical_fail = not all_req1_errors_identified or not all_rush_steps_identified
    
    return {
        "score": score,
        "max_score": 30,
        "percentage": (score / 30) * 100,
        "feedback": feedback,
        "critical_fail": critical_fail
    }


def evaluate_test(submission, answer_key):
    """Evaluate the entire test and calculate the overall score."""
    section1_results = evaluate_section1(submission, answer_key)
    section2_results = evaluate_section2(submission, answer_key)
    section3_results = evaluate_section3(submission, answer_key)
    
    total_score = section1_results["score"] + section2_results["score"] + section3_results["score"]
    max_score = section1_results["max_score"] + section2_results["max_score"] + section3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Check critical elements
    critical_failures = []
    if section1_results["critical_fail"]:
        critical_failures.append("Failed to identify tax exemption status in Section 1")
    if section2_results["critical_fail"]:
        critical_failures.append("Failed to disqualify non-compliant vendor or select correct vendor in Section 2")
    if section3_results["critical_fail"]:
        critical_failures.append("Failed to identify critical errors in requisitions or rush procedures in Section 3")
    
    # If any critical elements failed, candidate fails regardless of score
    passed = overall_percentage >= 70 and not critical_failures
    
    return {
        "section1": section1_results,
        "section2": section2_results,
        "section3": section3_results,
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_score,
        "critical_failures": critical_failures,
        "passed": passed,
        "grade": "Excellent" if overall_percentage >= 90 else "Pass" if passed else "Fail"
    }


def main():
    """Main function to process arguments and evaluate the test."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_test(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as outfile:
        json.dump(results, outfile, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Grade: {results['grade']}")
    
    if results["critical_failures"]:
        print("Critical failures detected:")
        for failure in results["critical_failures"]:
            print(f"- {failure}")


if __name__ == "__main__":
    main()