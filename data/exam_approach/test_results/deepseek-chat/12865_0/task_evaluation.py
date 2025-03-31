import json
from pathlib import Path

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def evaluate_task_1(submission, answer_key):
    errors = []
    score = 0
    total_fields = len(answer_key["task_1"])
    
    for field in answer_key["task_1"]:
        if submission["task_1"].get(field) == answer_key["task_1"][field]:
            score += 1
        else:
            errors.append({
                "field": field,
                "submitted": submission["task_1"].get(field),
                "expected": answer_key["task_1"][field]
            })
    
    return {
        "score": score,
        "max_score": total_fields,
        "errors": errors
    }

def evaluate_task_2(submission, answer_key):
    errors = []
    score = 0
    total_transactions = len(answer_key["task_2"]["calculated_commissions"])
    
    # Create a dictionary of expected commissions for easy lookup
    expected_commissions = {
        entry["transaction_id"]: {
            "expected": float(entry["expected_commission"][1:]),
            "actual": float(entry["actual_payment"][1:]),
            "discrepancy": float(entry["discrepancy"][1:])
        }
        for entry in answer_key["task_2"]["calculated_commissions"]
    }
    
    for submitted_entry in submission["task_2"]["calculated_commissions"]:
        tid = submitted_entry["transaction_id"]
        submitted_expected = float(submitted_entry["expected_commission"][1:])
        submitted_actual = float(submitted_entry["actual_payment"][1:])
        submitted_disc = float(submitted_entry["discrepancy"][1:])
        
        expected_data = expected_commissions.get(tid)
        if not expected_data:
            errors.append({
                "transaction_id": tid,
                "error": "Transaction ID not found in answer key"
            })
            continue
        
        # Check expected commission
        if abs(submitted_expected - expected_data["expected"]) <= 0.01:
            score += 0.5  # Half point for correct expected commission
        else:
            errors.append({
                "transaction_id": tid,
                "field": "expected_commission",
                "submitted": f"${submitted_expected:.2f}",
                "expected": f"${expected_data['expected']:.2f}"
            })
        
        # Check discrepancy
        expected_disc = expected_data["expected"] - expected_data["actual"]
        if abs(submitted_disc - expected_disc) <= 0.01:
            score += 0.5  # Half point for correct discrepancy
        else:
            errors.append({
                "transaction_id": tid,
                "field": "discrepancy",
                "submitted": f"${submitted_disc:.2f}",
                "expected": f"${expected_disc:.2f}"
            })
    
    # Check total discrepancies
    submitted_total = float(submission["task_2"]["total_discrepancies"][1:])
    expected_total = sum(abs(float(e["discrepancy"][1:])) for e in answer_key["task_2"]["calculated_commissions"])
    
    if abs(submitted_total - expected_total) <= 0.01:
        score += 1  # Bonus point for correct total
    else:
        errors.append({
            "field": "total_discrepancies",
            "submitted": f"${submitted_total:.2f}",
            "expected": f"${expected_total:.2f}"
        })
    
    return {
        "score": score,
        "max_score": total_transactions * 1 + 1,  # 1 point per transaction (0.5+0.5) + 1 for total
        "errors": errors
    }

def evaluate_task_3(submission, answer_key):
    errors = []
    score = 0
    total_transactions = len(answer_key["task_3"]["late_payments"])
    
    # Create a dictionary of expected penalties for easy lookup
    expected_penalties = {
        entry["transaction_id"]: {
            "days_late": entry["days_late"],
            "penalty": float(entry["penalty_applied"])
        }
        for entry in answer_key["task_3"]["late_payments"]
    }
    
    for submitted_entry in submission["task_3"]["late_payments"]:
        tid = submitted_entry["transaction_id"]
        submitted_days = submitted_entry["days_late"]
        submitted_penalty = float(submitted_entry["penalty_applied"])
        
        expected_data = expected_penalties.get(tid)
        if not expected_data:
            errors.append({
                "transaction_id": tid,
                "error": "Transaction ID not found in answer key"
            })
            continue
        
        # Check days late
        if submitted_days == expected_data["days_late"]:
            score += 0.5  # Half point for correct days late
        else:
            errors.append({
                "transaction_id": tid,
                "field": "days_late",
                "submitted": submitted_days,
                "expected": expected_data["days_late"]
            })
        
        # Check penalty
        if abs(submitted_penalty - expected_data["penalty"]) <= 0.01:
            score += 0.5  # Half point for correct penalty
        else:
            errors.append({
                "transaction_id": tid,
                "field": "penalty_applied",
                "submitted": f"${submitted_penalty:.2f}",
                "expected": f"${expected_data['penalty']:.2f}"
            })
    
    # Check total penalties
    submitted_total = float(submission["task_3"]["total_penalties"])
    expected_total = sum(float(e["penalty_applied"]) for e in answer_key["task_3"]["late_payments"])
    
    if abs(submitted_total - expected_total) <= 0.01:
        score += 1  # Bonus point for correct total
    else:
        errors.append({
            "field": "total_penalties",
            "submitted": f"${submitted_total:.2f}",
            "expected": f"${expected_total:.2f}"
        })
    
    return {
        "score": score,
        "max_score": total_transactions * 1 + 1,  # 1 point per transaction (0.5+0.5) + 1 for total
        "errors": errors
    }

def main():
    # Load files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        return
    
    # Evaluate each task
    task1_results = evaluate_task_1(submission, answer_key)
    task2_results = evaluate_task_2(submission, answer_key)
    task3_results = evaluate_task_3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    total_max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_score = round((total_score / total_max_score) * 100, 2)
    
    # Prepare results
    results = {
        "overall_score": overall_score,
        "task_1": task1_results,
        "task_2": task2_results,
        "task_3": task3_results
    }
    
    # Save results
    with open("test_results.json", 'w') as file:
        json.dump(results, file, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()