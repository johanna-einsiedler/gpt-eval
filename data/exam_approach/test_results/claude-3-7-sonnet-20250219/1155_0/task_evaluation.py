#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timedelta

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, indent=2, sort_keys=True, fp=f)

def calculate_deadline_date(answer_key_date):
    """Convert a date string like 'CURRENT_DATE+12' to an actual date"""
    if not answer_key_date.startswith('CURRENT_DATE+'):
        return answer_key_date
    
    days_to_add = int(answer_key_date.split('+')[1])
    current_date = datetime.now().date()
    deadline_date = current_date + timedelta(days=days_to_add)
    return deadline_date.strftime('%Y-%m-%d')

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "UNKNOWN"),
        "scores": {
            "scenario1": {},
            "scenario2": {},
            "scenario3": {},
        },
        "point_totals": {
            "duty_amounts": 0,
            "freight_amounts": 0,
            "payment_responsibility": 0,
            "payment_method": 0,
            "payment_deadline": 0,
            "customs_reference": 0,
            "total_points": 0
        },
        "comments": []
    }
    
    total_possible_points = 20
    
    # Convert answer key dates to actual dates
    for scenario in ["scenario1", "scenario2", "scenario3"]:
        if scenario in answer_key:
            date_str = answer_key[scenario].get("paymentDeadline", "")
            if date_str.startswith("CURRENT_DATE+"):
                answer_key[scenario]["paymentDeadline"] = calculate_deadline_date(date_str)
    
    # Evaluate each scenario
    for scenario in ["scenario1", "scenario2", "scenario3"]:
        if scenario not in submission or scenario not in answer_key:
            results["comments"].append(f"Missing {scenario} in submission or answer key")
            continue
        
        sub_scenario = submission[scenario]
        key_scenario = answer_key[scenario]
        scenario_scores = {}
        
        # Duty Amount (2 points each)
        sub_duty = float(sub_scenario.get("dutyAmount", 0))
        key_duty = float(key_scenario.get("dutyAmount", 0))
        if abs(sub_duty - key_duty) < 0.01:  # Allow for small float differences
            scenario_scores["dutyAmount"] = 2
            results["point_totals"]["duty_amounts"] += 2
        else:
            scenario_scores["dutyAmount"] = 0
            results["comments"].append(f"{scenario}: Incorrect duty amount. Got {sub_duty}, expected {key_duty}")
        
        # Freight Amount (2 points each)
        sub_freight = float(sub_scenario.get("freightAmount", 0))
        key_freight = float(key_scenario.get("freightAmount", 0))
        if abs(sub_freight - key_freight) < 0.01:  # Allow for small float differences
            scenario_scores["freightAmount"] = 2
            results["point_totals"]["freight_amounts"] += 2
        else:
            scenario_scores["freightAmount"] = 0
            results["comments"].append(f"{scenario}: Incorrect freight amount. Got {sub_freight}, expected {key_freight}")
        
        # Payment Responsibility (1 point each)
        sub_resp = sub_scenario.get("paymentResponsibility", "").lower()
        key_resp = key_scenario.get("paymentResponsibility", "").lower()
        if sub_resp == key_resp:
            scenario_scores["paymentResponsibility"] = 1
            results["point_totals"]["payment_responsibility"] += 1
        else:
            scenario_scores["paymentResponsibility"] = 0
            results["comments"].append(f"{scenario}: Incorrect payment responsibility. Got {sub_resp}, expected {key_resp}")
        
        # Payment Method (1 point each)
        sub_method = sub_scenario.get("paymentMethod", "").lower()
        key_method = key_scenario.get("paymentMethod", "").lower()
        
        # Special case for scenario 1 and 2 where multiple methods could be acceptable
        if scenario == "scenario1" and sub_method in ["wire", "ach"]:
            scenario_scores["paymentMethod"] = 1
            results["point_totals"]["payment_method"] += 1
        elif scenario == "scenario2" and sub_method in ["wire", "credit"]:
            scenario_scores["paymentMethod"] = 1
            results["point_totals"]["payment_method"] += 1
        elif sub_method == key_method:
            scenario_scores["paymentMethod"] = 1
            results["point_totals"]["payment_method"] += 1
        else:
            scenario_scores["paymentMethod"] = 0
            results["comments"].append(f"{scenario}: Incorrect payment method. Got {sub_method}, expected {key_method}")
        
        # Payment Deadline (0.5 points each)
        sub_date = sub_scenario.get("paymentDeadline", "")
        key_date = key_scenario.get("paymentDeadline", "")
        
        try:
            sub_date_obj = datetime.strptime(sub_date, "%Y-%m-%d").date()
            key_date_obj = datetime.strptime(key_date, "%Y-%m-%d").date()
            
            # Allow for +/- 1 day variation
            if abs((sub_date_obj - key_date_obj).days) <= 1:
                scenario_scores["paymentDeadline"] = 0.5
                results["point_totals"]["payment_deadline"] += 0.5
            else:
                scenario_scores["paymentDeadline"] = 0
                results["comments"].append(f"{scenario}: Incorrect payment deadline. Got {sub_date}, expected {key_date}")
        except ValueError:
            scenario_scores["paymentDeadline"] = 0
            results["comments"].append(f"{scenario}: Invalid date format. Got {sub_date}, expected format YYYY-MM-DD")
        
        # Customs Reference (0.5 points each)
        sub_ref = sub_scenario.get("customsReferenceNumber", "")
        key_ref = key_scenario.get("customsReferenceNumber", "")
        if sub_ref == key_ref:
            scenario_scores["customsReferenceNumber"] = 0.5
            results["point_totals"]["customs_reference"] += 0.5
        else:
            scenario_scores["customsReferenceNumber"] = 0
            results["comments"].append(f"{scenario}: Incorrect customs reference. Got {sub_ref}, expected {key_ref}")
        
        results["scores"][scenario] = scenario_scores
    
    # Calculate total points
    total_points = (
        results["point_totals"]["duty_amounts"] +
        results["point_totals"]["freight_amounts"] +
        results["point_totals"]["payment_responsibility"] +
        results["point_totals"]["payment_method"] +
        results["point_totals"]["payment_deadline"] +
        results["point_totals"]["customs_reference"]
    )
    
    results["point_totals"]["total_points"] = total_points
    results["overall_score"] = (total_points / total_possible_points) * 100
    
    # Determine if candidate passed
    passed = results["overall_score"] >= 80
    
    # Check for critical errors
    has_critical_errors = False
    if results["point_totals"]["duty_amounts"] < 4:  # Less than 2 correct duty calculations
        has_critical_errors = True
        results["comments"].append("CRITICAL ERROR: Multiple incorrect duty calculations")
    
    if results["point_totals"]["customs_reference"] < 1.5:  # Not all customs references correct
        has_critical_errors = True
        results["comments"].append("CRITICAL ERROR: Incorrect customs reference numbers")
    
    results["passed"] = passed and not has_critical_errors
    
    if results["passed"]:
        results["comments"].append(f"PASSED with a score of {results['overall_score']:.1f}%")
    else:
        results["comments"].append(f"FAILED with a score of {results['overall_score']:.1f}%")
        if has_critical_errors:
            results["comments"].append("Candidate had critical errors that prevent passing regardless of overall score")
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    try:
        submission = load_json(submission_file)
        answer_key = load_json(answer_key_file)
        
        results = evaluate_submission(submission, answer_key)
        save_json(results, "test_results.json")
        
        print(f"Evaluation complete. Results saved to test_results.json")
        print(f"Overall Score: {results['overall_score']:.1f}%")
        print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()