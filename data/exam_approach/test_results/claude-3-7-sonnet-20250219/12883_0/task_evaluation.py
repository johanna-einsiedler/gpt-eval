#!/usr/bin/env python3
"""
Evaluator for Farm Products Buyer Record Maintenance Assessment.
This script compares a candidate's submission with the answer key and scores it.

Usage:
    python task_evaluation.py <submission_file> <answer_key_file>
"""

import json
import sys
import math
from typing import Dict, List, Any, Union, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading file {file_path}: {e}")
        sys.exit(1)


def compare_numeric_values(candidate_value: Union[int, float], answer_value: Union[int, float], 
                           is_monetary: bool = False) -> bool:
    """Compare numeric values with tolerance for monetary values."""
    if is_monetary:
        # Allow $0.05 tolerance for monetary values
        return abs(candidate_value - answer_value) <= 0.05
    return candidate_value == answer_value


def evaluate_transaction_summary(candidate: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate the transaction summary section."""
    max_points = 30
    earned_points = 0
    feedback = []
    
    # Get relevant sections from both dictionaries
    candidate_summary = candidate.get("transaction_summary", {}).get("total_expenditure_by_category", {})
    answer_summary = answer_key.get("transaction_summary", {}).get("total_expenditure_by_category", {})
    
    # Check each category (5 points per category, 20 total)
    categories = ["Grains", "Produce", "Protein", "Dairy"]
    for category in categories:
        candidate_value = candidate_summary.get(category, 0)
        answer_value = answer_summary.get(category, 0)
        
        if compare_numeric_values(candidate_value, answer_value, is_monetary=True):
            earned_points += 5
            feedback.append(f"Correct {category} expenditure calculation: {candidate_value}")
        else:
            feedback.append(f"Incorrect {category} expenditure: got {candidate_value}, expected {answer_value}")
    
    # Check proper categorization (5 points)
    if len(candidate_summary) == 4 and all(category in candidate_summary for category in categories):
        earned_points += 5
        feedback.append("Correct product categorization")
    else:
        feedback.append("Incorrect product categorization")
    
    # Check for accurate arithmetic (5 points)
    # We'll assume arithmetic is correct if all category totals are correct
    if earned_points >= 20:  # If all 4 categories are correct
        earned_points += 5
        feedback.append("Accurate arithmetic in all calculations")
    else:
        # If some categories are wrong, we'll give partial credit for arithmetic
        correct_categories = sum(1 for category in categories 
                              if category in candidate_summary and 
                              compare_numeric_values(candidate_summary.get(category, 0), 
                                                   answer_summary.get(category, 0), 
                                                   is_monetary=True))
        arithmetic_points = math.floor(correct_categories / 4 * 5)
        earned_points += arithmetic_points
        if arithmetic_points > 0:
            feedback.append(f"Partially accurate arithmetic ({arithmetic_points} of 5 points)")
        else:
            feedback.append("Inaccurate arithmetic")
    
    return earned_points, max_points, feedback


def evaluate_inventory_reconciliation(candidate: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate the inventory reconciliation section."""
    max_points = 25
    earned_points = 0
    feedback = []
    
    # Get relevant sections
    candidate_inventory = candidate.get("inventory_reconciliation", {})
    answer_inventory = answer_key.get("inventory_reconciliation", {})
    
    # Check ending inventory (15 points)
    candidate_ending = candidate_inventory.get("ending_inventory", {})
    answer_ending = answer_inventory.get("ending_inventory", {})
    
    # Count correct ending inventory entries
    correct_entries = 0
    total_entries = len(answer_ending)
    
    for product_code, expected_value in answer_ending.items():
        candidate_value = candidate_ending.get(product_code)
        if candidate_value == expected_value:
            correct_entries += 1
    
    # Calculate points for ending inventory (15 points possible)
    inventory_score = round(15 * (correct_entries / total_entries))
    earned_points += inventory_score
    
    if inventory_score == 15:
        feedback.append("All ending inventory calculations correct")
    else:
        feedback.append(f"Ending inventory: {correct_entries}/{total_entries} products correct ({inventory_score} of 15 points)")
    
    # Check discrepancies (10 points)
    candidate_discrepancies = candidate_inventory.get("discrepancies", [])
    answer_discrepancies = answer_inventory.get("discrepancies", [])
    
    # We need to normalize the discrepancies to compare them
    def normalize_discrepancies(discrepancies):
        result = {}
        for item in discrepancies:
            product_code = item.get("product_code")
            if not product_code:
                # Try alternate key name
                product_code = item.get("product")
            
            amount = item.get("discrepancy_amount")
            if amount is None:
                # Try alternate key name
                amount = item.get("amount")
                
            if product_code and amount is not None:
                result[product_code] = amount
        return result
    
    candidate_disc_dict = normalize_discrepancies(candidate_discrepancies)
    answer_disc_dict = normalize_discrepancies(answer_discrepancies)
    
    # Compare discrepancies
    if candidate_disc_dict == answer_disc_dict:
        earned_points += 10
        feedback.append("Correct identification of all inventory discrepancies")
    elif len(candidate_disc_dict) == len(answer_disc_dict):
        # Same number but different values
        common_products = set(candidate_disc_dict.keys()) & set(answer_disc_dict.keys())
        if common_products:
            matching_values = sum(1 for p in common_products if candidate_disc_dict[p] == answer_disc_dict[p])
            partial_points = round(10 * (matching_values / len(answer_disc_dict)))
            earned_points += partial_points
            feedback.append(f"Partially correct discrepancies ({partial_points} of 10 points)")
        else:
            feedback.append("Incorrect discrepancy identification")
    else:
        # Partial credit if they found some discrepancies but missed others or added extra
        common_products = set(candidate_disc_dict.keys()) & set(answer_disc_dict.keys())
        matching_values = sum(1 for p in common_products if candidate_disc_dict[p] == answer_disc_dict[p])
        
        if matching_values > 0:
            partial_points = round(10 * (matching_values / len(answer_disc_dict)))
            earned_points += partial_points
            feedback.append(f"Partially correct discrepancies ({partial_points} of 10 points)")
        else:
            feedback.append("Incorrect discrepancy identification")
    
    return earned_points, max_points, feedback


def evaluate_regulatory_report(candidate: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate the regulatory report section."""
    max_points = 25
    earned_points = 0
    feedback = []
    
    # Get relevant sections
    candidate_report = candidate.get("regulatory_report", {})
    answer_report = answer_key.get("regulatory_report", {})
    
    # Check commodity volumes (5 points)
    candidate_volumes = candidate_report.get("commodity_volumes", {})
    answer_volumes = answer_report.get("commodity_volumes", {})
    
    correct_volumes = 0
    total_volumes = len(answer_volumes)
    
    for commodity, expected_value in answer_volumes.items():
        candidate_value = candidate_volumes.get(commodity)
        if candidate_value == expected_value:
            correct_volumes += 1
    
    volume_score = round(5 * (correct_volumes / total_volumes))
    earned_points += volume_score
    
    if volume_score == 5:
        feedback.append("All commodity volumes correct")
    else:
        feedback.append(f"Commodity volumes: {correct_volumes}/{total_volumes} correct ({volume_score} of 5 points)")
    
    # Check price ranges (5 points)
    candidate_prices = candidate_report.get("price_ranges", {})
    answer_prices = answer_report.get("price_ranges", {})
    
    correct_prices = 0
    total_prices = len(answer_prices)
    
    for commodity, expected_range in answer_prices.items():
        candidate_range = candidate_prices.get(commodity, {})
        expected_min = expected_range.get("min")
        expected_max = expected_range.get("max")
        candidate_min = candidate_range.get("min")
        candidate_max = candidate_range.get("max")
        
        if (compare_numeric_values(candidate_min, expected_min, is_monetary=True) and 
            compare_numeric_values(candidate_max, expected_max, is_monetary=True)):
            correct_prices += 1
    
    price_score = round(5 * (correct_prices / total_prices))
    earned_points += price_score
    
    if price_score == 5:
        feedback.append("All price ranges correct")
    else:
        feedback.append(f"Price ranges: {correct_prices}/{total_prices} correct ({price_score} of 5 points)")
    
    # Check certification summary (5 points)
    candidate_cert = candidate_report.get("certification_summary", {})
    answer_cert = answer_report.get("certification_summary", {})
    
    correct_certs = 0
    total_certs = len(answer_cert)
    
    for cert_type, expected_count in answer_cert.items():
        candidate_count = candidate_cert.get(cert_type)
        if candidate_count == expected_count:
            correct_certs += 1
    
    cert_score = round(5 * (correct_certs / total_certs))
    earned_points += cert_score
    
    if cert_score == 5:
        feedback.append("Certification summary correct")
    else:
        feedback.append(f"Certification summary: {correct_certs}/{total_certs} correct ({cert_score} of 5 points)")
    
    # Check origin verification (5 points)
    candidate_origin = candidate_report.get("origin_verification", {})
    answer_origin = answer_report.get("origin_verification", {})
    
    origin_points = 0
    
    # Check structure and count values
    correct_structure = True
    correct_counts = 0
    correct_commodities = 0
    total_origins = len(answer_origin)
    
    for state, expected_data in answer_origin.items():
        candidate_data = candidate_origin.get(state, {})
        
        # Check purchase counts
        if candidate_data.get("purchase_count") == expected_data.get("purchase_count"):
            correct_counts += 1
        
        # Check commodities lists (we'll allow any order)
        expected_commodities = set(expected_data.get("commodities", []))
        candidate_commodities = set(candidate_data.get("commodities", []))
        
        if expected_commodities == candidate_commodities:
            correct_commodities += 1
    
    # Award points for origin verification
    origin_score = round(2.5 * (correct_counts / total_origins) + 2.5 * (correct_commodities / total_origins))
    earned_points += origin_score
    
    if origin_score == 5:
        feedback.append("Origin verification correct")
    else:
        feedback.append(f"Origin verification: {origin_score} of 5 points")
    
    # Check proper data aggregation (5 points)
    # We'll consider this correct if the commodity volumes are correct,
    # since that's the most critical aggregation task
    if volume_score >= 4:  # 80% correct
        earned_points += 5
        feedback.append("Proper data aggregation across product types")
    else:
        # Partial credit based on commodity volume score
        aggregation_score = round(volume_score)
        earned_points += aggregation_score
        if aggregation_score > 0:
            feedback.append(f"Partially correct data aggregation ({aggregation_score} of 5 points)")
        else:
            feedback.append("Incorrect data aggregation")
    
    return earned_points, max_points, feedback


def evaluate_audit_response(candidate: Dict, answer_key: Dict) -> Tuple[int, int, List[str]]:
    """Evaluate the audit response section."""
    max_points = 20
    earned_points = 0
    feedback = []
    
    # Get relevant sections
    candidate_audit = candidate.get("audit_response", {})
    answer_audit = answer_key.get("audit_response", {})
    
    # Check transaction records (8 points)
    candidate_transactions = candidate_audit.get("transaction_records", [])
    answer_transactions = answer_audit.get("transaction_records", [])
    
    # Create a map of transaction IDs to records for easier comparison
    candidate_trans_map = {t.get("transaction_id"): t for t in candidate_transactions}
    answer_trans_map = {t.get("transaction_id"): t for t in answer_transactions}
    
    transaction_ids = set(answer_trans_map.keys())
    correct_transactions = 0
    
    for trans_id in transaction_ids:
        candidate_trans = candidate_trans_map.get(trans_id, {})
        answer_trans = answer_trans_map.get(trans_id, {})
        
        # Consider a transaction correct if all fields match
        if candidate_trans == answer_trans:
            correct_transactions += 1
    
    transaction_score = round(8 * (correct_transactions / len(transaction_ids)))
    earned_points += transaction_score
    
    if transaction_score == 8:
        feedback.append("All transaction records correct")
    else:
        feedback.append(f"Transaction records: {correct_transactions}/{len(transaction_ids)} correct ({transaction_score} of 8 points)")
    
    # Check product traceability (8 points)
    candidate_trace = candidate_audit.get("product_traceability", {})
    answer_trace = answer_audit.get("product_traceability", {})
    
    product_codes = set(answer_trace.keys())
    correct_traceable = 0
    
    for product_code in product_codes:
        candidate_product = candidate_trace.get(product_code, {})
        answer_product = answer_trace.get(product_code, {})
        
        if candidate_product == answer_product:
            correct_traceable += 1
    
    trace_score = round(8 * (correct_traceable / len(product_codes)))
    earned_points += trace_score
    
    if trace_score == 8:
        feedback.append("All product traceability information correct")
    else:
        feedback.append(f"Product traceability: {correct_traceable}/{len(product_codes)} correct ({trace_score} of 8 points)")
    
    # Check certification codes (4 points)
    candidate_codes = set(candidate_audit.get("certification_codes", []))
    answer_codes = set(answer_audit.get("certification_codes", []))
    
    if candidate_codes == answer_codes:
        earned_points += 4
        feedback.append("All certification codes correct")
    else:
        # Partial credit for certification codes
        common_codes = candidate_codes.intersection(answer_codes)
        cert_score = round(4 * (len(common_codes) / len(answer_codes)))
        earned_points += cert_score
        
        if cert_score > 0:
            feedback.append(f"Partially correct certification codes ({cert_score} of 4 points)")
        else:
            feedback.append("Incorrect certification codes")
    
    return earned_points, max_points, feedback


def check_critical_elements(candidate: Dict, answer_key: Dict) -> Tuple[bool, List[str]]:
    """Check if the candidate met all critical elements required to pass."""
    critical_elements_met = True
    feedback = []
    
    # 1. Must correctly identify the inventory discrepancy
    candidate_inventory = candidate.get("inventory_reconciliation", {})
    answer_inventory = answer_key.get("inventory_reconciliation", {})
    
    candidate_discrepancies = candidate_inventory.get("discrepancies", [])
    answer_discrepancies = answer_inventory.get("discrepancies", [])
    
    # Normalize discrepancies for comparison
    def normalize_discrepancies(discrepancies):
        result = {}
        for item in discrepancies:
            product_code = item.get("product_code")
            if not product_code:
                product_code = item.get("product")
            
            amount = item.get("discrepancy_amount")
            if amount is None:
                amount = item.get("amount")
                
            if product_code and amount is not None:
                result[product_code] = amount
        return result
    
    candidate_disc_dict = normalize_discrepancies(candidate_discrepancies)
    answer_disc_dict = normalize_discrepancies(answer_discrepancies)
    
    if candidate_disc_dict != answer_disc_dict:
        critical_elements_met = False
        feedback.append("CRITICAL FAIL: Did not correctly identify inventory discrepancy")
    
    # 2. Must correctly complete at least 80% of the regulatory report
    candidate_report = candidate.get("regulatory_report", {})
    answer_report = answer_key.get("regulatory_report", {})
    
    # Check each component of the regulatory report
    report_sections = [
        ("commodity_volumes", lambda c, a: sum(1 for k in a if c.get(k) == a.get(k)) / len(a)),
        ("price_ranges", lambda c, a: sum(1 for k in a if c.get(k, {}).get("min") == a.get(k, {}).get("min") and 
                                                     c.get(k, {}).get("max") == a.get(k, {}).get("max")) / len(a)),
        ("certification_summary", lambda c, a: sum(1 for k in a if c.get(k) == a.get(k)) / len(a)),
        ("origin_verification", lambda c, a: sum(1 for k in a if c.get(k, {}).get("purchase_count") == a.get(k, {}).get("purchase_count") and
                                                        set(c.get(k, {}).get("commodities", [])) == set(a.get(k, {}).get("commodities", []))) / len(a))
    ]
    
    section_scores = []
    for section_name, scoring_func in report_sections:
        candidate_section = candidate_report.get(section_name, {})
        answer_section = answer_report.get(section_name, {})
        
        if answer_section:  # Only if there's an expected answer
            section_score = scoring_func(candidate_section, answer_section)
            section_scores.append(section_score)
    
    # Calculate overall regulatory report score
    if section_scores:
        report_score = sum(section_scores) / len(section_scores)
        
        if report_score < 0.8:  # Less than 80%
            critical_elements_met = False
            feedback.append(f"CRITICAL FAIL: Regulatory report only {report_score:.1%} complete (80% required)")
    
    # 3. Must provide accurate traceability information for all requested products
    candidate_trace = candidate.get("audit_response", {}).get("product_traceability", {})
    answer_trace = answer_key.get("audit_response", {}).get("product_traceability", {})
    
    product_codes = set(answer_trace.keys())
    correct_traceable = 0
    
    for product_code in product_codes:
        candidate_product = candidate_trace.get(product_code, {})
        answer_product = answer_trace.get(product_code, {})
        
        if candidate_product == answer_product:
            correct_traceable += 1
    
    if correct_traceable < len(product_codes):
        critical_elements_met = False
        feedback.append(f"CRITICAL FAIL: Only provided accurate traceability for {correct_traceable}/{len(product_codes)} products (all required)")
    
    return critical_elements_met, feedback


def check_section_minimums(scores: Dict[str, int], max_scores: Dict[str, int]) -> Tuple[bool, List[str]]:
    """Check if the candidate met the minimum score requirements for each section."""
    minimums_met = True
    feedback = []
    
    # Define minimum score requirements for each section
    min_requirements = {
        "Transaction Recording": 20,
        "Inventory Reconciliation": 15,
        "Regulatory Compliance Reporting": 15,
        "Audit Trail Documentation": 10
    }
    
    for section, min_score in min_requirements.items():
        earned = scores.get(section, 0)
        maximum = max_scores.get(section, 0)
        
        if earned < min_score:
            minimums_met = False
            feedback.append(f"SECTION MINIMUM NOT MET: {section} scored {earned}/{maximum} (minimum {min_score} required)")
    
    return minimums_met, feedback


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    candidate = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    transaction_points, transaction_max, transaction_feedback = evaluate_transaction_summary(candidate, answer_key)
    inventory_points, inventory_max, inventory_feedback = evaluate_inventory_reconciliation(candidate, answer_key)
    regulatory_points, regulatory_max, regulatory_feedback = evaluate_regulatory_report(candidate, answer_key)
    audit_points, audit_max, audit_feedback = evaluate_audit_response(candidate, answer_key)
    
    # Compile scores
    section_scores = {
        "Transaction Recording": transaction_points,
        "Inventory Reconciliation": inventory_points,
        "Regulatory Compliance Reporting": regulatory_points,
        "Audit Trail Documentation": audit_points
    }
    
    section_max_scores = {
        "Transaction Recording": transaction_max,
        "Inventory Reconciliation": inventory_max,
        "Regulatory Compliance Reporting": regulatory_max,
        "Audit Trail Documentation": audit_max
    }
    
    # Check critical elements
    critical_elements_met, critical_feedback = check_critical_elements(candidate, answer_key)
    
    # Check section minimums
    minimums_met, minimum_feedback = check_section_minimums(section_scores, section_max_scores)
    
    # Calculate overall score
    total_points = sum(section_scores.values())
    total_possible = sum(section_max_scores.values())
    overall_percentage = (total_points / total_possible) * 100
    
    # Determine if the candidate passed
    passed = critical_elements_met and minimums_met and overall_percentage >= 70
    
    # Create results dictionary
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "total_points": total_points,
        "total_possible": total_possible,
        "passed": passed,
        "sections": {
            "Transaction Recording": {
                "points": transaction_points,
                "max_points": transaction_max,
                "feedback": transaction_feedback
            },
            "Inventory Reconciliation": {
                "points": inventory_points,
                "max_points": inventory_max,
                "feedback": inventory_feedback
            },
            "Regulatory Compliance Reporting": {
                "points": regulatory_points,
                "max_points": regulatory_max,
                "feedback": regulatory_feedback
            },
            "Audit Trail Documentation": {
                "points": audit_points,
                "max_points": audit_max,
                "feedback": audit_feedback
            }
        },
        "critical_elements_met": critical_elements_met,
        "critical_feedback": critical_feedback,
        "section_minimums_met": minimums_met,
        "minimum_feedback": minimum_feedback
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    print(f"Result: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    main()