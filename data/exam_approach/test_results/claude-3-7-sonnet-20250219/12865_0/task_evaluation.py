#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, List

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        sys.exit(1)

def is_close(val1: float, val2: float, tolerance: float = 0.01) -> bool:
    """Check if two values are within a specified tolerance."""
    if val1 == 0 and val2 == 0:
        return True
    return abs((val1 - val2) / max(abs(val1), abs(val2))) <= tolerance if max(abs(val1), abs(val2)) > 0 else True

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Commission Calculation."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": [],
        "feedback": ""
    }
    
    sub_commissions = {item["transaction_id"]: item["commission_amount"] 
                       for item in submission["task1"]["commission_amounts"]}
    key_commissions = {item["transaction_id"]: item["commission_amount"] 
                       for item in answer_key["task1"]["commission_amounts"]}
    
    # Check individual commission amounts
    correct_count = 0
    for trans_id in range(1, 14):
        sub_amount = sub_commissions.get(trans_id, 0)
        key_amount = key_commissions.get(trans_id, 0)
        
        is_correct = is_close(sub_amount, key_amount)
        if is_correct:
            correct_count += 1
            
        results["details"].append({
            "transaction_id": trans_id,
            "submitted_amount": sub_amount,
            "correct_amount": key_amount,
            "is_correct": is_correct
        })
    
    # Check total commission calculation
    sub_total = submission["task1"]["total_commission"]
    key_total = answer_key["task1"]["total_commission"]
    total_accuracy = 1 - min(abs(sub_total - key_total) / key_total, 0.05) / 0.05 if key_total != 0 else 0
    
    # Score calculation (70% for individual commissions, 30% for total)
    individual_score = (correct_count / 13) * 0.7 * results["max_score"]
    total_score = total_accuracy * 0.3 * results["max_score"]
    results["score"] = round(individual_score + total_score)
    
    # Feedback
    if correct_count >= 10 and total_accuracy >= 0.95:
        results["feedback"] = "Excellent job calculating commissions accurately."
    elif correct_count >= 8:
        results["feedback"] = "Good work on most commissions, but some calculations need improvement."
    else:
        results["feedback"] = "Significant issues with commission calculations. Review contract terms carefully."
    
    return results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Payment Reconciliation."""
    results = {
        "score": 0,
        "max_score": 25,
        "details": [],
        "feedback": ""
    }
    
    sub_discrepancies = {item["payment_id"]: {
        "correct_rate": item["correct_rate"],
        "correct_commission": item["correct_commission"],
        "difference": item["difference"]
    } for item in submission["task2"]["discrepancies"]}
    
    key_discrepancies = {item["payment_id"]: {
        "correct_rate": item["correct_rate"],
        "correct_commission": item["correct_commission"],
        "difference": item["difference"]
    } for item in answer_key["task2"]["discrepancies"]}
    
    # Check individual discrepancies
    correct_count = 0
    for payment_id in range(1, 10):
        sub_data = sub_discrepancies.get(payment_id, {})
        key_data = key_discrepancies.get(payment_id, {})
        
        rate_correct = is_close(sub_data.get("correct_rate", 0), key_data.get("correct_rate", 0))
        commission_correct = is_close(sub_data.get("correct_commission", 0), key_data.get("correct_commission", 0))
        difference_correct = is_close(sub_data.get("difference", 0), key_data.get("difference", 0))
        
        item_correct = rate_correct and commission_correct and difference_correct
        if item_correct:
            correct_count += 1
            
        results["details"].append({
            "payment_id": payment_id,
            "rate_correct": rate_correct,
            "commission_correct": commission_correct,
            "difference_correct": difference_correct,
            "is_correct": item_correct
        })
    
    # Check total adjustment calculation
    sub_total = submission["task2"]["total_adjustment_needed"]
    key_total = answer_key["task2"]["total_adjustment_needed"]
    total_accuracy = 1 - min(abs(sub_total - key_total) / key_total, 0.1) / 0.1 if key_total != 0 else 0
    
    # Score calculation (60% for individual discrepancies, 40% for total)
    individual_score = (correct_count / 9) * 0.6 * results["max_score"]
    total_score = total_accuracy * 0.4 * results["max_score"]
    results["score"] = round(individual_score + total_score)
    
    # Feedback
    if correct_count >= 7 and total_accuracy >= 0.9:
        results["feedback"] = "Excellent job identifying and calculating payment discrepancies."
    elif correct_count >= 5:
        results["feedback"] = "Good work on most discrepancies, but some issues with rate application."
    else:
        results["feedback"] = "Significant issues with discrepancy identification. Review contract terms carefully."
    
    return results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Royalty Processing."""
    results = {
        "score": 0,
        "max_score": 25,
        "details": [],
        "client_scores": {}
    }
    
    # Helper function to evaluate a client's royalty calculation
    def evaluate_client(client_key, sub_data, key_data):
        client_details = {
            "tiers_correct": 0,
            "total_correct": False,
            "special_provision_applied": False,
            "score": 0
        }
        
        # Check if special provisions were correctly applied
        if client_key == "client1_royalty":
            sub_merch = sub_data.get("merchandise_sales", {}).get("royalty", 0)
            key_merch = key_data.get("merchandise_sales", {}).get("royalty", 0)
            client_details["special_provision_applied"] = is_close(sub_merch, key_merch)
        
        elif client_key == "client2_royalty":
            sub_min = sub_data.get("minimum_guarantee", {}).get("applies", False)
            key_min = key_data.get("minimum_guarantee", {}).get("applies", False)
            client_details["special_provision_applied"] = sub_min == key_min
        
        elif client_key == "client3_royalty":
            # Check if international rates were correctly incremented by 1%
            int_tiers = sub_data.get("international_sales", {})
            key_int_tiers = key_data.get("international_sales", {})
            
            tier_rates_correct = all(
                is_close(int_tiers.get(f"tier{i}", {}).get("rate", 0), 
                        key_int_tiers.get(f"tier{i}", {}).get("rate", 0))
                for i in range(1, 5) if f"tier{i}" in key_int_tiers
            )
            client_details["special_provision_applied"] = tier_rates_correct
        
        # Check tier calculations
        for tier_type in ["regular_sales", "domestic_sales"]:
            if tier_type in key_data:
                for i in range(1, 5):
                    tier_key = f"tier{i}"
                    if tier_key in key_data.get(tier_type, {}):
                        sub_tier = sub_data.get(tier_type, {}).get(tier_key, {})
                        key_tier = key_data.get(tier_type, {}).get(tier_key, {})
                        
                        if is_close(sub_tier.get("royalty", 0), key_tier.get("royalty", 0)):
                            client_details["tiers_correct"] += 1
        
        # Check international sales tiers if applicable
        if "international_sales" in key_data:
            for i in range(1, 5):
                tier_key = f"tier{i}"
                if tier_key in key_data.get("international_sales", {}):
                    sub_tier = sub_data.get("international_sales", {}).get(tier_key, {})
                    key_tier = key_data.get("international_sales", {}).get(tier_key, {})
                    
                    if is_close(sub_tier.get("royalty", 0), key_tier.get("royalty", 0)):
                        client_details["tiers_correct"] += 1
        
        # Check total royalty
        sub_total = sub_data.get("total_royalty", 0)
        key_total = key_data.get("total_royalty", 0)
        client_details["total_correct"] = is_close(sub_total, key_total)
        
        # Calculate client score (50% tiers, 25% special provision, 25% total)
        max_tiers = sum(1 for tier_type in ["regular_sales", "domestic_sales", "international_sales"] 
                      if tier_type in key_data
                      for i in range(1, 5) 
                      if f"tier{i}" in key_data.get(tier_type, {}) and key_data.get(tier_type, {}).get(f"tier{i}", {}).get("amount", 0) > 0)
        
        tier_score = (client_details["tiers_correct"] / max(max_tiers, 1)) * 0.5
        special_score = 0.25 if client_details["special_provision_applied"] else 0
        total_score = 0.25 if client_details["total_correct"] else 0
        
        client_details["score"] = tier_score + special_score + total_score
        return client_details
    
    # Evaluate each client
    clients = ["client1_royalty", "client2_royalty", "client3_royalty"]
    client_evaluation = {}
    
    for client in clients:
        sub_data = submission["task3"].get(client, {})
        key_data = answer_key["task3"].get(client, {})
        client_evaluation[client] = evaluate_client(client, sub_data, key_data)
    
    # Calculate overall score for Task 3
    client_scores = [details["score"] for details in client_evaluation.values()]
    results["client_scores"] = client_evaluation
    
    # Equal weighting for all clients
    results["score"] = round(sum(client_scores) / len(clients) * results["max_score"])
    
    # Calculate how many clients had correct totals
    correct_clients = sum(1 for details in client_evaluation.values() if details["total_correct"])
    
    # Feedback
    if correct_clients == 3:
        results["feedback"] = "Excellent work on royalty calculations for all clients."
    elif correct_clients >= 2:
        results["feedback"] = "Good job on most royalty calculations, with minor issues."
    else:
        results["feedback"] = "Significant issues with royalty calculations. Review tiered structure and special provisions."
    
    return results

def evaluate_task4(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 4: Payment Collection Schedule."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {
            "correct_payments": 0,
            "missed_payments": [],
            "incorrect_dates": [],
            "incorrect_amounts": [],
            "total_accuracy": 0
        },
        "feedback": ""
    }
    
    # Extract key payment data
    key_payments = {f"{p['project']}-{p['milestone_type']}": {
        "date": p["date"],
        "amount": p["amount"]
    } for p in answer_key["task4"]["payment_schedule"]}
    
    # Count correct payments, identify wrong dates/amounts
    correct_payments = 0
    incorrect_dates = []
    incorrect_amounts = []
    found_keys = set()
    
    for payment in submission["task4"].get("payment_schedule", []):
        payment_key = f"{payment.get('project', '')}-{payment.get('milestone_type', '')}"
        
        if payment_key in key_payments:
            found_keys.add(payment_key)
            key_payment = key_payments[payment_key]
            
            date_correct = payment.get("date", "") == key_payment["date"]
            amount_correct = is_close(payment.get("amount", 0), key_payment["amount"])
            
            if date_correct and amount_correct:
                correct_payments += 1
            if not date_correct:
                incorrect_dates.append({
                    "payment": payment_key,
                    "submitted_date": payment.get("date", ""),
                    "correct_date": key_payment["date"]
                })
            if not amount_correct:
                incorrect_amounts.append({
                    "payment": payment_key,
                    "submitted_amount": payment.get("amount", 0),
                    "correct_amount": key_payment["amount"]
                })
    
    # Identify missed payments
    missed_payments = [key for key in key_payments if key not in found_keys]
    
    # Check total expected amount
    sub_total = submission["task4"].get("total_expected_q4", 0)
    key_total = answer_key["task4"].get("total_expected_q4", 0)
    total_accuracy = 1 - min(abs(sub_total - key_total) / key_total, 0.1) / 0.1 if key_total != 0 else 0
    
    # Update results details
    results["details"]["correct_payments"] = correct_payments
    results["details"]["missed_payments"] = missed_payments
    results["details"]["incorrect_dates"] = incorrect_dates
    results["details"]["incorrect_amounts"] = incorrect_amounts
    results["details"]["total_accuracy"] = total_accuracy
    
    # Calculate score (60% for correct payments, 40% for total amount)
    payment_score = (correct_payments / len(key_payments)) * 0.6 * results["max_score"]
    total_score = total_accuracy * 0.4 * results["max_score"]
    results["score"] = round(payment_score + total_score)
    
    # Feedback
    if correct_payments >= 6 and total_accuracy >= 0.9:
        results["feedback"] = "Excellent job creating an accurate payment collection schedule."
    elif correct_payments >= 4:
        results["feedback"] = "Good job identifying most payments, but some dates or amounts need correction."
    else:
        results["feedback"] = "Significant issues with the payment schedule. Review milestone terms carefully."
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": evaluate_task1(submission, answer_key),
        "task2": evaluate_task2(submission, answer_key),
        "task3": evaluate_task3(submission, answer_key),
        "task4": evaluate_task4(submission, answer_key)
    }
    
    # Calculate overall score
    total_score = sum(results[f"task{i}"]["score"] for i in range(1, 5))
    total_possible = sum(results[f"task{i}"]["max_score"] for i in range(1, 5))
    results["overall_score"] = round((total_score / total_possible) * 100)
    
    # Add overall assessment
    if results["overall_score"] >= 90:
        results["overall_assessment"] = "Excellent"
    elif results["overall_score"] >= 80:
        results["overall_assessment"] = "Good"
    elif results["overall_score"] >= 70:
        results["overall_assessment"] = "Satisfactory"
    elif results["overall_score"] >= 60:
        results["overall_assessment"] = "Needs Improvement"
    else:
        results["overall_assessment"] = "Failing"
    
    return results

def main():
    """Main function to handle command line arguments and execute evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Write results to output file
    output_file = "test_results.json"
    try:
        with open(output_file, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation completed. Results saved to {output_file}")
        print(f"Overall Score: {results['overall_score']}% - {results['overall_assessment']}")
    except Exception as e:
        print(f"Error writing results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()