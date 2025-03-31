import json

def evaluate_submission():
    # Load the submission and answer key
    try:
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": "Submission file not found. Please ensure 'test_submission.json' exists."}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in submission file."}

    try:
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)['answer_key']
    except FileNotFoundError:
        return {"error": "Answer key not found. Please ensure 'answer_key.json' exists."}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in answer key."}

    # Initialize results structure
    results = {
        "overall_score": 0,
        "task_1": {
            "score": 0,
            "max_score": 0,
            "details": []
        },
        "task_2": {
            "score": 0,
            "max_score": 0,
            "details": []
        },
        "total_points": 0,
        "max_points": 0
    }

    # Evaluate Task 1
    task1_key = answer_key['task_1']['supplier_comparison']
    task1_sub = submission['task_1']['supplier_comparison']
    task1_max = len(task1_key) * 6  # 6 fields per supplier (name, price, quality, delivery, reviews, ranking)
    task1_score = 0

    for i in range(len(task1_key)):
        expected = task1_key[i]
        submitted = task1_sub[i]
        supplier_name = expected['supplier_name']
        
        # Check if supplier names match (order matters)
        if submitted['supplier_name'] != supplier_name:
            results['task_1']['details'].append(f"Supplier order mismatch at position {i+1}")
            continue
        
        # Check each field
        fields = ['price', 'quality', 'delivery_time', 'customer_reviews', 'ranking']
        for field in fields:
            if submitted[field] == expected[field]:
                task1_score += 1
            else:
                results['task_1']['details'].append(
                    f"Incorrect {field} for {supplier_name}: submitted '{submitted[field]}', expected '{expected[field]}'"
                )
        
        # Check justification (more lenient)
        if "justification" not in submitted or not submitted["justification"]:
            results['task_1']['details'].append(f"Missing justification for {supplier_name}")
    
    results['task_1']['score'] = task1_score
    results['task_1']['max_score'] = task1_max

    # Evaluate Task 2
    task2_key = answer_key['task_2']['reliability_assessment']
    task2_sub = submission['task_2']['reliability_assessment']
    task2_max = len(task2_key) * 5  # 5 fields per supplier
    task2_score = 0

    for i in range(len(task2_key)):
        expected = task2_key[i]
        submitted = task2_sub[i]
        supplier_name = expected['supplier_name']
        
        if submitted['supplier_name'] != supplier_name:
            results['task_2']['details'].append(f"Supplier order mismatch at position {i+1}")
            continue
        
        # Check each field
        fields = ['on_time_delivery_rate', 'defect_rate', 'response_time', 'recommendation']
        for field in fields:
            if submitted[field] == expected[field]:
                task2_score += 1
            else:
                results['task_2']['details'].append(
                    f"Incorrect {field} for {supplier_name}: submitted '{submitted[field]}', expected '{expected[field]}'"
                )
        
        # Check red flags (more lenient)
        if "red_flags" not in submitted:
            results['task_2']['details'].append(f"Missing red flags for {supplier_name}")
    
    results['task_2']['score'] = task2_score
    results['task_2']['max_score'] = task2_max

    # Calculate overall score
    total_points = task1_score + task2_score
    max_points = task1_max + task2_max
    overall_score = round((total_points / max_points) * 100, 2) if max_points > 0 else 0

    results['total_points'] = total_points
    results['max_points'] = max_points
    results['overall_score'] = overall_score

    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    evaluation_results = evaluate_submission()
    if "error" in evaluation_results:
        print(f"Error: {evaluation_results['error']}")
    else:
        print(f"Evaluation complete. Overall score: {evaluation_results['overall_score']}%")
        print("Detailed results saved to 'test_results.json'")