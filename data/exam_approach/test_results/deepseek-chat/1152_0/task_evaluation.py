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

def validate_task1(submission, answer_key):
    task1_score = 0
    task1_feedback = {"correct": [], "incorrect": []}
    
    for ans_supplier in answer_key["task_1"]["suppliers"]:
        found = False
        for sub_supplier in submission["task_1"]["suppliers"]:
            if (sub_supplier["name"] == ans_supplier["name"] and
                ans_supplier["contact"] in sub_supplier["contact"] and
                sub_supplier["product"] == ans_supplier["product"]):
                found = True
                break
        
        if found:
            task1_score += 1
            task1_feedback["correct"].append(ans_supplier["name"])
        else:
            task1_feedback["incorrect"].append(ans_supplier["name"])
    
    return task1_score / len(answer_key["task_1"]["suppliers"]), task1_feedback

def validate_task2(submission, answer_key):
    task2_score = 0
    task2_feedback = {"comparison_correct": False, "recommendation_correct": False, "reason_valid": False}
    
    # Check printer comparison
    if (len(submission["task_2"]["printer_comparison"]) == 2 and
        all(p["model"] in ["Printer Alpha", "Printer Beta"] 
            for p in submission["task_2"]["printer_comparison"])):
        task2_score += 0.5
        task2_feedback["comparison_correct"] = True
    
    # Check recommendation and reason
    if (submission["task_2"]["recommendation"] in answer_key["task_2"]["valid_recommendations"] and
        any(keyword in submission["task_2"]["reason"].lower() 
            for keyword in ["cost", "speed", "warranty", "performance"])):
        task2_score += 0.5
        task2_feedback["recommendation_correct"] = True
        task2_feedback["reason_valid"] = True
    
    return task2_score, task2_feedback

def validate_task3(submission, answer_key):
    task3_score = 0
    task3_feedback = {"providers_valid": False, "recommendation_valid": False}
    
    # Check providers meet requirements
    if (len(submission["task_3"]["cloud_storage_options"]) >= 2 and
        all(float(opt["storage_limit"].replace("TB","").replace("GB","000")) >= 1000 and
        float(opt["price"].replace("$","").split("/")[0]) <= 20 for opt in 
        submission["task_3"]["cloud_storage_options"])):
        task3_score += 0.5
        task3_feedback["providers_valid"] = True
    
    # Check recommendation is valid
    if (submission["task_3"]["recommendation"] in [opt["provider"] for opt in 
        submission["task_3"]["cloud_storage_options"]] and
        any(keyword in submission["task_3"]["reason"].lower() 
            for keyword in answer_key["task_3"]["minimum_requirements"]["security_features"])):
        task3_score += 0.5
        task3_feedback["recommendation_valid"] = True
    
    return task3_score, task3_feedback

def main():
    # Load files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Validate tasks
    task1_score, task1_feedback = validate_task1(submission, answer_key)
    task2_score, task2_feedback = validate_task2(submission, answer_key)
    task3_score, task3_feedback = validate_task3(submission, answer_key)
    
    # Calculate overall score (weighted 35%-35%-30%)
    overall_score = round((task1_score * 35 + task2_score * 35 + task3_score * 30), 2)
    
    # Prepare results
    results = {
        "overall_score": overall_score,
        "task_1": {
            "score": f"{task1_score * 100:.0f}%",
            "feedback": task1_feedback,
            "max_score": "35%"
        },
        "task_2": {
            "score": f"{task2_score * 100:.0f}%",
            "feedback": task2_feedback,
            "max_score": "35%"
        },
        "task_3": {
            "score": f"{task3_score * 100:.0f}%",
            "feedback": task3_feedback,
            "max_score": "30%"
        },
        "pass_status": "Pass" if overall_score >= 80 else "Fail"
    }
    
    # Save results
    with open("test_results.json", "w") as outfile:
        json.dump(results, outfile, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()