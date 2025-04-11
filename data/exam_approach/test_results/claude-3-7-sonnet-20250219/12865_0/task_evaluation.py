import json
import os
from decimal import Decimal

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        exit(1)

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "tasks": {},
        "task_scores": {},
        "total_points": 0,
        "max_points": 20,
        "tasks_fully_correct": 0,
        "overall_score": 0
    }
    
    # Task 1 evaluation (3 points)
    task1_results = {"points": 0, "max_points": 3, "details": {}}
    for client in ["clientA", "clientB", "clientC"]:
        key = f"{client}_commission"
        submitted = Decimal(str(submission.get("task1", {}).get(key, 0)))
        expected = Decimal(str(answer_key.get("task1", {}).get(key, 0)))
        
        # Allow for small rounding differences (±$0.10)
        is_correct = abs(submitted - expected) <= Decimal('0.10')
        task1_results["details"][key] = {
            "submitted": float(submitted),
            "expected": float(expected),
            "correct": is_correct
        }
        if is_correct:
            task1_results["points"] += 1
    
    task1_results["fully_correct"] = task1_results["points"] == task1_results["max_points"]
    results["tasks"]["task1"] = task1_results
    results["task_scores"]["task1"] = task1_results["points"]
    results["total_points"] += task1_results["points"]
    if task1_results["fully_correct"]:
        results["tasks_fully_correct"] += 1
    
    # Task 2 evaluation (4 points)
    task2_results = {"points": 0, "max_points": 4, "details": {}}
    
    # Check client discrepancies (3 points)
    for client in ["clientA", "clientB", "clientC"]:
        key = f"{client}_discrepancy"
        submitted = Decimal(str(submission.get("task2", {}).get(key, 0)))
        expected = Decimal(str(answer_key.get("task2", {}).get(key, 0)))
        
        # Allow for small rounding differences (±$0.10)
        is_correct = abs(submitted - expected) <= Decimal('0.10')
        task2_results["details"][key] = {
            "submitted": float(submitted),
            "expected": float(expected),
            "correct": is_correct
        }
        if is_correct:
            task2_results["points"] += 1
    
    # Check underpaid clients list (1 point)
    submitted_underpaid = set(submission.get("task2", {}).get("underpaid_clients", []))
    expected_underpaid = set(answer_key.get("task2", {}).get("underpaid_clients", []))
    underpaid_correct = submitted_underpaid == expected_underpaid
    
    task2_results["details"]["underpaid_clients"] = {
        "submitted": list(submitted_underpaid),
        "expected": list(expected_underpaid),
        "correct": underpaid_correct
    }
    
    if underpaid_correct:
        task2_results["points"] += 1
    
    task2_results["fully_correct"] = task2_results["points"] == task2_results["max_points"]
    results["tasks"]["task2"] = task2_results
    results["task_scores"]["task2"] = task2_results["points"]
    results["total_points"] += task2_results["points"]
    if task2_results["fully_correct"]:
        results["tasks_fully_correct"] += 1
    
    # Task 3 evaluation (6 points)
    task3_results = {"points": 0, "max_points": 6, "details": {}}
    
    # Check due dates (3 points)
    for client in ["clientA", "clientB", "clientC"]:
        date_key = f"{client}_due_date"
        submitted_date = submission.get("task3", {}).get(date_key, "")
        expected_date = answer_key.get("task3", {}).get(date_key, "")
        
        date_correct = submitted_date == expected_date
        task3_results["details"][date_key] = {
            "submitted": submitted_date,
            "expected": expected_date,
            "correct": date_correct
        }
        if date_correct:
            task3_results["points"] += 1
    
    # Check late fees (3 points)
    for client in ["clientA", "clientB", "clientC"]:
        fee_key = f"{client}_late_fee"
        submitted_fee = Decimal(str(submission.get("task3", {}).get(fee_key, 0)))
        expected_fee = Decimal(str(answer_key.get("task3", {}).get(fee_key, 0)))
        
        # Allow for small rounding differences (±$0.10)
        fee_correct = abs(submitted_fee - expected_fee) <= Decimal('0.10')
        task3_results["details"][fee_key] = {
            "submitted": float(submitted_fee),
            "expected": float(expected_fee),
            "correct": fee_correct
        }
        if fee_correct:
            task3_results["points"] += 1
    
    task3_results["fully_correct"] = task3_results["points"] == task3_results["max_points"]
    results["tasks"]["task3"] = task3_results
    results["task_scores"]["task3"] = task3_results["points"]
    results["total_points"] += task3_results["points"]
    if task3_results["fully_correct"]:
        results["tasks_fully_correct"] += 1
    
    # Task 4 evaluation (4 points)
    task4_results = {"points": 0, "max_points": 4, "details": {}}
    
    for key in ["late_fees_allocation", "current_commission_allocation", 
                "previous_commission_allocation", "remaining_balance"]:
        submitted = Decimal(str(submission.get("task4", {}).get(key, 0)))
        expected = Decimal(str(answer_key.get("task4", {}).get(key, 0)))
        
        # Allow for small rounding differences (±$0.10)
        is_correct = abs(submitted - expected) <= Decimal('0.10')
        task4_results["details"][key] = {
            "submitted": float(submitted),
            "expected": float(expected),
            "correct": is_correct
        }
        if is_correct:
            task4_results["points"] += 1
    
    task4_results["fully_correct"] = task4_results["points"] == task4_results["max_points"]
    results["tasks"]["task4"] = task4_results
    results["task_scores"]["task4"] = task4_results["points"]
    results["total_points"] += task4_results["points"]
    if task4_results["fully_correct"]:
        results["tasks_fully_correct"] += 1
    
    # Task 5 evaluation (3 points)
    task5_results = {"points": 0, "max_points": 3, "details": {}}
    
    for client in ["clientA", "clientB", "clientC"]:
        key = f"{client}_compliant"
        submitted = submission.get("task5", {}).get(key, None)
        expected = answer_key.get("task5", {}).get(key, None)
        
        # Boolean values must match exactly
        is_correct = submitted == expected
        task5_results["details"][key] = {
            "submitted": submitted,
            "expected": expected,
            "correct": is_correct
        }
        if is_correct:
            task5_results["points"] += 1
    
    task5_results["fully_correct"] = task5_results["points"] == task5_results["max_points"]
    results["tasks"]["task5"] = task5_results
    results["task_scores"]["task5"] = task5_results["points"]
    results["total_points"] += task5_results["points"]
    if task5_results["fully_correct"]:
        results["tasks_fully_correct"] += 1
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Determine if candidate passed
    min_score_to_pass = 80  # 80% minimum
    min_tasks_fully_correct = 3  # At least 3 tasks must be 100% correct
    
    results["passed"] = (results["overall_score"] >= min_score_to_pass and 
                         results["tasks_fully_correct"] >= min_tasks_fully_correct)
    
    return results

def save_results(results, filename):
    """Save the evaluation results to a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_results(results, "test_results.json")
    
    # Print summary
    print(f"\nEvaluation Summary for {results['candidate_id']}:")
    print(f"Total Score: {results['total_points']}/{results['max_points']} ({results['overall_score']:.2f}%)")
    print(f"Tasks fully correct: {results['tasks_fully_correct']}/5")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()