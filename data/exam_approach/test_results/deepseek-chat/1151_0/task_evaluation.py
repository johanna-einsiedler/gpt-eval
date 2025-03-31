import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        exit(1)

def compare_records(sub_record, ans_record, task_name):
    errors = []
    for key in ans_record:
        if key not in sub_record:
            errors.append(f"Missing field: {key}")
            continue
        
        # Special handling for average cost (allow floating point tolerance)
        if task_name == "task_3" and key == "average_cost_per_order":
            if abs(float(sub_record[key]) - float(ans_record[key])) > 0.01:
                errors.append(f"Incorrect {key}: expected {ans_record[key]}, got {sub_record[key]}")
        # Special handling for late deliveries (order doesn't matter)
        elif task_name == "task_3" and key == "late_deliveries":
            if set(sub_record[key]) != set(ans_record[key]):
                errors.append(f"Incorrect {key}: expected {ans_record[key]}, got {sub_record[key]}")
        # Normal comparison for other fields
        elif sub_record[key] != ans_record[key]:
            errors.append(f"Incorrect {key}: expected {ans_record[key]}, got {sub_record[key]}")
    
    # Check for extra fields in submission
    for key in sub_record:
        if key not in ans_record:
            errors.append(f"Unexpected field: {key}")
    
    return errors

def evaluate_task(submission, answer_key, task_name):
    results = {
        "correct": True,
        "errors": [],
        "details": {}
    }
    
    if task_name not in submission:
        results["correct"] = False
        results["errors"].append(f"Missing task: {task_name}")
        return results
    
    sub_task = submission[task_name]
    ans_task = answer_key[task_name]
    
    if isinstance(ans_task, list):
        # For tasks with arrays (task_1 records, task_2 updated_inventory)
        if not isinstance(sub_task, dict) or "records" not in sub_task:
            results["correct"] = False
            results["errors"].append(f"Invalid structure for {task_name}")
            return results
        
        for i, ans_record in enumerate(ans_task["records"]):
            if i >= len(sub_task["records"]):
                results["correct"] = False
                results["errors"].append(f"Missing record {i} in {task_name}")
                continue
            
            record_errors = compare_records(sub_task["records"][i], ans_record, task_name)
            if record_errors:
                results["correct"] = False
                results["errors"].extend([f"Record {i}: {e}" for e in record_errors])
                results["details"][f"record_{i}"] = {
                    "submitted": sub_task["records"][i],
                    "expected": ans_record
                }
    else:
        # For task_3 which is a direct comparison
        task_errors = compare_records(sub_task, ans_task, task_name)
        if task_errors:
            results["correct"] = False
            results["errors"].extend(task_errors)
            results["details"] = {
                "submitted": sub_task,
                "expected": ans_task
            }
    
    return results

def calculate_score(results):
    total_fields = 0
    correct_fields = 0
    
    # Count fields in answer_key
    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)
    
    # Task 1 fields
    total_fields += len(answer_key['answer_key']['task_1']['records']) * 6  # 6 fields per record
    
    # Task 2 fields
    total_fields += len(answer_key['answer_key']['task_2']['updated_inventory']) * 5  # 5 fields per item
    
    # Task 3 fields
    # most_expensive_purchase has 3 fields, average_cost_per_order, late_deliveries counts as 1
    total_fields += 4
    
    # Calculate correct fields by subtracting errors
    error_count = sum(len(task_result['errors']) for task_result in results.values())
    correct_fields = total_fields - error_count
    
    return (correct_fields / total_fields) * 100

def main():
    # Load files
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')['answer_key']
    
    # Evaluate each task
    results = {
        "task_1": evaluate_task(submission, answer_key, "task_1"),
        "task_2": evaluate_task(submission, answer_key, "task_2"),
        "task_3": evaluate_task(submission, answer_key, "task_3")
    }
    
    # Calculate overall score
    overall_score = calculate_score(results)
    results["overall_score"] = round(overall_score, 2)
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()