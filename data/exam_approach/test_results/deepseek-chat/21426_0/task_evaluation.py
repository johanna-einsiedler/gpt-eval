import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        exit(1)

def validate_structure(submission, answer_key):
    required_structure = {
        "task_1": ["claim_covered", "coverage_limit", "deductible", "within_authority"],
        "task_2": ["total_claim_amount", "deductible_applied", "depreciation_applied", 
                  "final_payable_amount", "within_authority"],
        "task_3": ["decision", "justification"]
    }
    
    # Check if all tasks are present
    for task in required_structure.keys():
        if task not in submission:
            return False, f"Missing task: {task}"
    
    # Check if all fields are present in each task
    for task, fields in required_structure.items():
        for field in fields:
            if field not in submission[task]:
                return False, f"Missing field: {task}.{field}"
    
    return True, "Structure is valid"

def evaluate_task_1(submission, answer_key):
    results = {}
    score = 0
    max_score = 4
    
    # Check each field
    for field in answer_key["task_1"].keys():
        if submission["task_1"][field] == answer_key["task_1"][field]:
            results[field] = {"correct": True, "expected": answer_key["task_1"][field], "actual": submission["task_1"][field]}
            score += 1
        else:
            results[field] = {"correct": False, "expected": answer_key["task_1"][field], "actual": submission["task_1"][field]}
    
    return {"score": score, "max_score": max_score, "details": results}

def evaluate_task_2(submission, answer_key):
    results = {}
    score = 0
    max_score = 5
    tolerance = 0.01  # For floating point comparisons
    
    # Check each monetary field with tolerance
    monetary_fields = ["total_claim_amount", "deductible_applied", "depreciation_applied", "final_payable_amount"]
    for field in monetary_fields:
        try:
            sub_value = float(submission["task_2"][field].strip('$').replace(',', ''))
            ans_value = float(answer_key["task_2"][field].strip('$').replace(',', ''))
            if abs(sub_value - ans_value) <= tolerance:
                results[field] = {"correct": True, "expected": answer_key["task_2"][field], "actual": submission["task_2"][field]}
                score += 1
            else:
                results[field] = {"correct": False, "expected": answer_key["task_2"][field], "actual": submission["task_2"][field]}
        except (ValueError, AttributeError):
            results[field] = {"correct": False, "expected": answer_key["task_2"][field], "actual": submission["task_2"][field]}
    
    # Check within_authority (exact match)
    if submission["task_2"]["within_authority"] == answer_key["task_2"]["within_authority"]:
        results["within_authority"] = {"correct": True, "expected": answer_key["task_2"]["within_authority"], "actual": submission["task_2"]["within_authority"]}
        score += 1
    else:
        results["within_authority"] = {"correct": False, "expected": answer_key["task_2"]["within_authority"], "actual": submission["task_2"]["within_authority"]}
    
    return {"score": score, "max_score": max_score, "details": results}

def evaluate_task_3(submission, answer_key):
    results = {}
    score = 0
    max_score = 2
    
    # Check decision (exact match)
    if submission["task_3"]["decision"] == answer_key["task_3"]["decision"]:
        results["decision"] = {"correct": True, "expected": answer_key["task_3"]["decision"], "actual": submission["task_3"]["decision"]}
        score += 1
    else:
        results["decision"] = {"correct": False, "expected": answer_key["task_3"]["decision"], "actual": submission["task_3"]["decision"]}
    
    # Check justification (flexible matching)
    expected_justification = answer_key["task_3"]["justification"].lower()
    actual_justification = submission["task_3"]["justification"].lower()
    
    # Check if justification contains key terms
    key_terms = ["conflict", "dispute", "inconsistent", "witness", "statement"]
    if (any(term in actual_justification for term in key_terms) and len(actual_justification.split()) <= 20:
        results["justification"] = {"correct": True, "expected": "Justification mentioning conflict", "actual": submission["task_3"]["justification"]}
        score += 1
    else:
        results["justification"] = {"correct": False, "expected": "Justification mentioning conflict", "actual": submission["task_3"]["justification"]}
    
    return {"score": score, "max_score": max_score, "details": results}

def main():
    # Load files
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')['answer_key']  # Access the nested answer_key
    
    # Validate structure first
    is_valid, message = validate_structure(submission, answer_key)
    if not is_valid:
        print(f"Invalid submission: {message}")
        exit(1)
    
    # Evaluate each task
    task1_results = evaluate_task_1(submission, answer_key)
    task2_results = evaluate_task_2(submission, answer_key)
    task3_results = evaluate_task_3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_results['score'] + task2_results['score'] + task3_results['score']
    max_total_score = task1_results['max_score'] + task2_results['max_score'] + task3_results['max_score']
    overall_score = round((total_score / max_total_score) * 100, 2)
    
    # Prepare results
    test_results = {
        "overall_score": overall_score,
        "total_score": total_score,
        "max_total_score": max_total_score,
        "task_1": task1_results,
        "task_2": task2_results,
        "task_3": task3_results,
        "pass_status": "Pass" if overall_score >= 80 else "Fail"
    }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()