import json
import math
from datetime import datetime

def within_percent(candidate_value, correct_value, percent):
    """Check if candidate value is within specified percent of correct value"""
    if correct_value == 0:
        return candidate_value == 0
    return abs(candidate_value - correct_value) / abs(correct_value) <= percent/100

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Duty Calculation"""
    results = {
        "max_points": 5,
        "points_earned": 0,
        "feedback": {}
    }
    
    # Check calculated duty
    if submission["calculatedDuty"] == answer_key["calculatedDuty"]:
        results["points_earned"] += 1.25
        results["feedback"]["calculatedDuty"] = "Correct"
    elif within_percent(submission["calculatedDuty"], answer_key["calculatedDuty"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["calculatedDuty"] = "Within 5% of correct value"
    elif within_percent(submission["calculatedDuty"], answer_key["calculatedDuty"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["calculatedDuty"] = "Within 10% of correct value"
    else:
        results["feedback"]["calculatedDuty"] = "Incorrect"
    
    # Check MPF
    if submission["mpf"] == answer_key["mpf"]:
        results["points_earned"] += 1.25
        results["feedback"]["mpf"] = "Correct"
    elif within_percent(submission["mpf"], answer_key["mpf"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["mpf"] = "Within 5% of correct value"
    elif within_percent(submission["mpf"], answer_key["mpf"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["mpf"] = "Within 10% of correct value"
    else:
        results["feedback"]["mpf"] = "Incorrect"
    
    # Check HMF
    if submission["hmf"] == answer_key["hmf"]:
        results["points_earned"] += 1.25
        results["feedback"]["hmf"] = "Correct"
    elif within_percent(submission["hmf"], answer_key["hmf"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["hmf"] = "Within 5% of correct value"
    elif within_percent(submission["hmf"], answer_key["hmf"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["hmf"] = "Within 10% of correct value"
    else:
        results["feedback"]["hmf"] = "Incorrect"
    
    # Check total duty and fees
    if submission["totalDutyAndFees"] == answer_key["totalDutyAndFees"]:
        results["points_earned"] += 1.25
        results["feedback"]["totalDutyAndFees"] = "Correct"
    elif within_percent(submission["totalDutyAndFees"], answer_key["totalDutyAndFees"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["totalDutyAndFees"] = "Within 5% of correct value"
    elif within_percent(submission["totalDutyAndFees"], answer_key["totalDutyAndFees"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["totalDutyAndFees"] = "Within 10% of correct value"
    else:
        results["feedback"]["totalDutyAndFees"] = "Incorrect"
    
    return results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Customs Documentation"""
    results = {
        "max_points": 4,
        "points_earned": 0,
        "feedback": {}
    }
    
    # Check entry number format
    if submission["entryNumber"].startswith("280-") and len(submission["entryNumber"]) >= 11:
        results["points_earned"] += 1
        results["feedback"]["entryNumber"] = "Correct format"
    else:
        results["feedback"]["entryNumber"] = "Incorrect format. Should be 280-XXXXXXX-X"
    
    # Check bond type
    valid_bond_types = ["Single Transaction", "Continuous"]
    if submission["bondType"] in valid_bond_types:
        results["points_earned"] += 1
        results["feedback"]["bondType"] = "Valid bond type selected"
    else:
        results["feedback"]["bondType"] = "Invalid bond type. Should be 'Single Transaction' or 'Continuous'"
    
    # Check payment method
    if submission["paymentMethod"] == answer_key["paymentMethod"]:
        results["points_earned"] += 1
        results["feedback"]["paymentMethod"] = "Correct payment method"
    else:
        results["feedback"]["paymentMethod"] = f"Incorrect payment method. Expected: {answer_key['paymentMethod']}"
    
    # Check justification
    if len(submission["justification"]) >= 50 and len(submission["justification"]) <= 200:
        if "ach" in submission["justification"].lower() and "china" in submission["justification"].lower():
            results["points_earned"] += 1
            results["feedback"]["justification"] = "Adequate justification provided"
        else:
            results["feedback"]["justification"] = "Justification missing key elements (ACH and China)"
    else:
        results["feedback"]["justification"] = "Justification length outside required range (50-200 characters)"
    
    return results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Freight Charge Discrepancy Resolution"""
    results = {
        "max_points": 3,
        "points_earned": 0,
        "feedback": {}
    }
    
    # Check responsible party
    if submission["responsibleParty"] == answer_key["responsibleParty"]:
        results["points_earned"] += 1
        results["feedback"]["responsibleParty"] = "Correct"
    else:
        results["feedback"]["responsibleParty"] = f"Incorrect. Expected: {answer_key['responsibleParty']}"
    
    # Check correct amount
    if submission["correctAmount"] == answer_key["correctAmount"]:
        results["points_earned"] += 1
        results["feedback"]["correctAmount"] = "Correct"
    elif within_percent(submission["correctAmount"], answer_key["correctAmount"], 5):
        results["points_earned"] += 0.5
        results["feedback"]["correctAmount"] = "Within 5% of correct value"
    else:
        results["feedback"]["correctAmount"] = f"Incorrect. Expected: {answer_key['correctAmount']}"
    
    # Check documentation required
    valid_docs = [
        "Carrier's Freight Bill", "Commercial Invoice", "Bill of Lading", 
        "Proof of Delivery", "Freight Rate Agreement", "Carrier Rate Confirmation"
    ]
    
    if len(submission["documentationRequired"]) >= 2:
        valid_count = sum(1 for doc in submission["documentationRequired"] if any(valid_doc.lower() in doc.lower() for valid_doc in valid_docs))
        if valid_count >= 3:
            results["points_earned"] += 1
            results["feedback"]["documentationRequired"] = "Sufficient valid documentation listed"
        elif valid_count >= 2:
            results["points_earned"] += 0.5
            results["feedback"]["documentationRequired"] = "Some valid documentation listed, but incomplete"
        else:
            results["feedback"]["documentationRequired"] = "Insufficient valid documentation listed"
    else:
        results["feedback"]["documentationRequired"] = "Not enough documentation items listed (minimum 2)"
    
    return results

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Landed Cost Calculation"""
    results = {
        "max_points": 5,
        "points_earned": 0,
        "feedback": {}
    }
    
    # Check freight charges
    if submission["freightCharges"] == answer_key["freightCharges"]:
        results["points_earned"] += 1.25
        results["feedback"]["freightCharges"] = "Correct"
    elif within_percent(submission["freightCharges"], answer_key["freightCharges"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["freightCharges"] = "Within 5% of correct value"
    elif within_percent(submission["freightCharges"], answer_key["freightCharges"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["freightCharges"] = "Within 10% of correct value"
    else:
        results["feedback"]["freightCharges"] = f"Incorrect. Expected: {answer_key['freightCharges']}"
    
    # Check insurance cost
    if submission["insuranceCost"] == answer_key["insuranceCost"]:
        results["points_earned"] += 1.25
        results["feedback"]["insuranceCost"] = "Correct"
    elif within_percent(submission["insuranceCost"], answer_key["insuranceCost"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["insuranceCost"] = "Within 5% of correct value"
    elif within_percent(submission["insuranceCost"], answer_key["insuranceCost"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["insuranceCost"] = "Within 10% of correct value"
    else:
        results["feedback"]["insuranceCost"] = f"Incorrect. Expected: {answer_key['insuranceCost']}"
    
    # Check landed cost
    if submission["landedCost"] == answer_key["landedCost"]:
        results["points_earned"] += 1.25
        results["feedback"]["landedCost"] = "Correct"
    elif within_percent(submission["landedCost"], answer_key["landedCost"], 5):
        results["points_earned"] += 0.625
        results["feedback"]["landedCost"] = "Within 5% of correct value"
    elif within_percent(submission["landedCost"], answer_key["landedCost"], 10):
        results["points_earned"] += 0.3125
        results["feedback"]["landedCost"] = "Within 10% of correct value"
    else:
        results["feedback"]["landedCost"] = f"Incorrect. Expected: {answer_key['landedCost']}"
    
    # Check payment due date
    try:
        submission_date = datetime.strptime(submission["paymentDueDate"], "%Y-%m-%d")
        answer_date = datetime.strptime(answer_key["paymentDueDate"], "%Y-%m-%d")
        
        if submission_date == answer_date:
            results["points_earned"] += 1.25
            results["feedback"]["paymentDueDate"] = "Correct"
        elif abs((submission_date - answer_date).days) <= 2:
            results["points_earned"] += 0.625
            results["feedback"]["paymentDueDate"] = "Within 2 days of correct date"
        else:
            results["feedback"]["paymentDueDate"] = f"Incorrect. Expected: {answer_key['paymentDueDate']}"
    except ValueError:
        results["feedback"]["paymentDueDate"] = "Invalid date format. Use YYYY-MM-DD"
    
    return results

def evaluate_task5(submission, answer_key):
    """Evaluate Task 5: Payment Issue Resolution"""
    results = {
        "max_points": 3,
        "points_earned": 0,
        "feedback": {}
    }
    
    # Valid options with their reason codes
    valid_options = {
        "Resubmit with Corrected HTS Code": "RC-001",
        "Provide Additional Documentation": "RC-004",
        "Request Administrative Review": "RC-005"
    }
    
    # Check selected option
    if submission["selectedOption"] in valid_options:
        results["points_earned"] += 1
        results["feedback"]["selectedOption"] = "Valid option selected"
    else:
        results["feedback"]["selectedOption"] = "Invalid option selected"
    
    # Check reason code
    if submission["selectedOption"] in valid_options:
        expected_code = valid_options[submission["selectedOption"]]
        if submission["reasonCode"] == expected_code:
            results["points_earned"] += 1
            results["feedback"]["reasonCode"] = "Correct reason code for selected option"
        else:
            results["feedback"]["reasonCode"] = f"Incorrect reason code. Expected: {expected_code} for {submission['selectedOption']}"
    else:
        if submission["reasonCode"] in [code for code in valid_options.values()]:
            results["points_earned"] += 0.5
            results["feedback"]["reasonCode"] = "Valid reason code, but doesn't match selected option"
        else:
            results["feedback"]["reasonCode"] = "Invalid reason code"
    
    # Check estimated resolution time
    # Get expected time range based on reason code
    time_ranges = {
        "RC-001": (1, 2),
        "RC-004": (3, 5),
        "RC-005": (7, 10)
    }
    
    if submission["reasonCode"] in time_ranges:
        min_time, max_time = time_ranges[submission["reasonCode"]]
        if min_time <= submission["estimatedResolutionTime"] <= max_time:
            results["points_earned"] += 1
            results["feedback"]["estimatedResolutionTime"] = "Correct resolution time for selected reason code"
        else:
            results["feedback"]["estimatedResolutionTime"] = f"Incorrect resolution time. Expected: {min_time}-{max_time} days for {submission['reasonCode']}"
    else:
        results["feedback"]["estimatedResolutionTime"] = "Cannot evaluate resolution time for invalid reason code"
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission"""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task_results": {}
    }
    
    # Evaluate each task
    results["task_results"]["task1"] = evaluate_task1(submission["task1"], answer_key["task1"])
    results["task_results"]["task2"] = evaluate_task2(submission["task2"], answer_key["task2"])
    results["task_results"]["task3"] = evaluate_task3(submission["task3"], answer_key["task3"])
    results["task_results"]["task4"] = evaluate_task4(submission["task4"], answer_key["task4"])
    results["task_results"]["task5"] = evaluate_task5(submission["task5"], answer_key["task5"])
    
    # Calculate total score
    total_points = sum(task["points_earned"] for task in results["task_results"].values())
    max_points = sum(task["max_points"] for task in results["task_results"].values())
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["overall_score"] = round((total_points / max_points) * 100, 2)
    
    # Check if any task has zero points
    has_zero_task = any(task["points_earned"] == 0 for task in results["task_results"].values())
    
    # Determine if passed (80% overall and no complete failures)
    results["passed"] = results["overall_score"] >= 80 and not has_zero_task
    
    # Add overall feedback
    if results["passed"]:
        results["overall_feedback"] = "Congratulations! You have passed the basic practical exam."
    else:
        if results["overall_score"] < 80:
            results["overall_feedback"] = "You did not achieve the minimum required score of 80%."
        if has_zero_task:
            results["overall_feedback"] = "You must score points in every task to pass the exam."
    
    return results

def main():
    try:
        # Load submission and answer key
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
        
        # Evaluate submission
        results = evaluate_submission(submission, answer_key)
        
        # Save results
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Evaluation complete. Overall score: {results['overall_score']}%")
        print(f"Results saved to test_results.json")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure both test_submission.json and answer_key.json are in the current directory.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in one of the input files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()