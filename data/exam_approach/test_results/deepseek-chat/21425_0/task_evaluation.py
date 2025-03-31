import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} is not a valid JSON file.")
        exit(1)

def validate_submission(submission, answer_key):
    score = 0
    max_score = 100
    detailed_results = {
        "task_1": {"score": 0, "max_score": 30, "details": {}},
        "task_2": {"score": 0, "max_score": 30, "details": {}},
        "task_3": {"score": 0, "max_score": 40, "details": {}}
    }
    
    # Task 1 Validation
    task1_score = 0
    task1_details = {}
    
    # Check exact matches for simple fields
    simple_fields = ["policyholder_name", "policy_number", "coverage_limit", "deductible"]
    for field in simple_fields:
        if submission["task_1"].get(field) == answer_key["answer_key"]["task_1"][field]:
            task1_score += 5
            task1_details[field] = {"correct": True, "expected": answer_key["answer_key"]["task_1"][field]}
        else:
            task1_details[field] = {
                "correct": False, 
                "expected": answer_key["answer_key"]["task_1"][field],
                "provided": submission["task_1"].get(field)
            }
    
    # Check coverage determination
    if submission["task_1"].get("coverage_determination") == answer_key["answer_key"]["task_1"]["coverage_determination"]:
        task1_score += 10
        task1_details["coverage_determination"] = {"correct": True, "expected": answer_key["answer_key"]["task_1"]["coverage_determination"]}
    else:
        task1_details["coverage_determination"] = {
            "correct": False,
            "expected": answer_key["answer_key"]["task_1"]["coverage_determination"],
            "provided": submission["task_1"].get("coverage_determination")
        }
    
    # Check justification (partial credit for mentioning pipe bursts)
    justification = submission["task_1"].get("justification", "").lower()
    if "pipe burst" in justification or "pipe bursts" in justification:
        task1_score += 10
        task1_details["justification"] = {"correct": True, "note": "Mentioned pipe bursts"}
    else:
        task1_details["justification"] = {
            "correct": False,
            "note": "Justification should mention pipe bursts",
            "provided": submission["task_1"].get("justification")
        }
    
    detailed_results["task_1"]["score"] = task1_score
    detailed_results["task_1"]["details"] = task1_details
    
    # Task 2 Validation
    task2_score = 0
    task2_details = {}
    
    # Check at-fault party
    if submission["task_2"].get("at_fault_party") == answer_key["answer_key"]["task_2"]["at_fault_party"]:
        task2_score += 10
        task2_details["at_fault_party"] = {"correct": True, "expected": answer_key["answer_key"]["task_2"]["at_fault_party"]}
    else:
        task2_details["at_fault_party"] = {
            "correct": False,
            "expected": answer_key["answer_key"]["task_2"]["at_fault_party"],
            "provided": submission["task_2"].get("at_fault_party")
        }
    
    # Check liability percentage (accept 60%, 70%, or 80%)
    liability_percent = submission["task_2"].get("liability_percentage", "0%")
    if liability_percent in ["60%", "70%", "80%"]:
        task2_score += 10
        task2_details["liability_percentage"] = {"correct": True, "accepted_values": ["60%", "70%", "80%"]}
    else:
        task2_details["liability_percentage"] = {
            "correct": False,
            "expected": "60%, 70%, or 80%",
            "provided": liability_percent
        }
    
    # Check next steps for mention of subrogation
    next_steps = submission["task_2"].get("next_steps", "").lower()
    if "subrogation" in next_steps:
        task2_score += 10
        task2_details["next_steps"] = {"correct": True, "note": "Mentioned subrogation"}
    else:
        task2_details["next_steps"] = {
            "correct": False,
            "note": "Should mention subrogation",
            "provided": submission["task_2"].get("next_steps")
        }
    
    detailed_results["task_2"]["score"] = task2_score
    detailed_results["task_2"]["details"] = task2_details
    
    # Task 3 Validation
    task3_score = 0
    task3_details = {}
    
    # Check for required keywords
    email = submission["task_3"].get("email_response", "").lower()
    keywords_matched = 0
    keyword_details = {}
    
    for keyword in answer_key["answer_key"]["task_3"]["required_keywords"]:
        if keyword in email:
            keywords_matched += 1
            keyword_details[keyword] = {"found": True}
        else:
            keyword_details[keyword] = {"found": False}
    
    task3_score += keywords_matched * 10
    task3_details["keywords"] = keyword_details
    
    # Check word count
    word_count = len(email.split())
    min_words, max_words = answer_key["answer_key"]["task_3"]["word_count_range"]
    if min_words <= word_count <= max_words:
        task3_score += 10
        task3_details["word_count"] = {"correct": True, "count": word_count, "required_range": [min_words, max_words]}
    else:
        task3_details["word_count"] = {
            "correct": False,
            "count": word_count,
            "required_range": [min_words, max_words]
        }
    
    detailed_results["task_3"]["score"] = task3_score
    detailed_results["task_3"]["details"] = task3_details
    
    # Calculate overall score
    overall_score = task1_score + task2_score + task3_score
    
    return {
        "overall_score": overall_score,
        "max_score": max_score,
        "detailed_results": detailed_results
    }

def save_results(results, filename="test_results.json"):
    with open(filename, 'w') as file:
        json.dump(results, file, indent=2)

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Validate the submission
    results = validate_submission(submission, answer_key)
    
    # Save the results
    save_results(results)
    print(f"Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()