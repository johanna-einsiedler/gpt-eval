import json

def evaluate_submission():
    # Load the submission and answer key
    try:
        with open('test_submission.json', 'r') as f_sub, open('answer_key.json', 'r') as f_ans:
            submission = json.load(f_sub)
            answer_key = json.load(f_ans)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

    results = {
        "overall_score": 0,
        "task_1": {"score": 0, "total": len(answer_key["task_1"]), "details": []},
        "task_2": {"score": 0, "total": len(answer_key["task_2"]), "details": []},
        "task_3": {"score": 0, "total": len(answer_key["task_3"]), "details": []}
    }

    # Evaluate Task 1
    for i, (sub_entry, ans_entry) in enumerate(zip(submission["task_1"], answer_key["task_1"])):
        correct = True
        errors = []
        for key in ans_entry:
            if sub_entry.get(key) != ans_entry[key]:
                correct = False
                errors.append(f"{key}: expected {ans_entry[key]}, got {sub_entry.get(key)}")
        
        if correct:
            results["task_1"]["score"] += 1
            results["task_1"]["details"].append({"entry": i+1, "status": "correct"})
        else:
            results["task_1"]["details"].append({"entry": i+1, "status": "incorrect", "errors": errors})

    # Evaluate Task 2
    for i, (sub_entry, ans_entry) in enumerate(zip(submission["task_2"], answer_key["task_2"])):
        correct = True
        errors = []
        for key in ans_entry:
            if sub_entry.get(key) != ans_entry[key]:
                correct = False
                errors.append(f"{key}: expected {ans_entry[key]}, got {sub_entry.get(key)}")
        
        if correct:
            results["task_2"]["score"] += 1
            results["task_2"]["details"].append({"entry": i+1, "status": "correct"})
        else:
            results["task_2"]["details"].append({"entry": i+1, "status": "incorrect", "errors": errors})

    # Evaluate Task 3
    for i, (sub_entry, ans_entry) in enumerate(zip(submission["task_3"], answer_key["task_3"])):
        correct = True
        errors = []
        for key in ans_entry:
            if sub_entry.get(key) != ans_entry[key]:
                correct = False
                errors.append(f"{key}: expected {ans_entry[key]}, got {sub_entry.get(key)}")
        
        if correct:
            results["task_3"]["score"] += 1
            results["task_3"]["details"].append({"entry": i+1, "status": "correct"})
        else:
            results["task_3"]["details"].append({"entry": i+1, "status": "incorrect", "errors": errors})

    # Calculate overall score
    total_possible = (
        results["task_1"]["total"] + 
        results["task_2"]["total"] + 
        results["task_3"]["total"]
    )
    total_achieved = (
        results["task_1"]["score"] + 
        results["task_2"]["score"] + 
        results["task_3"]["score"]
    )
    results["overall_score"] = round((total_achieved / total_possible) * 100, 2)

    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    evaluation_results = evaluate_submission()
    if evaluation_results:
        print(f"Evaluation complete. Overall score: {evaluation_results['overall_score']}%")
        print("Detailed results saved to 'test_results.json'")