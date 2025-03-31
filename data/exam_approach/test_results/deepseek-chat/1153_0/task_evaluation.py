import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} is not a valid JSON file.")
        return None

def validate_submission(submission, answer_key):
    results = {
        "low_stock_items_correct": False,
        "reorder_quantities_correct": False,
        "purchase_priority_correct": False,
        "justification_correct": False,
        "overall_score": 0
    }
    
    # Check low_stock_items (unordered)
    if set(submission.get("low_stock_items", [])) == set(answer_key["answer_key"].get("low_stock_items", [])):
        results["low_stock_items_correct"] = True
    
    # Check reorder_quantities (exact match)
    if submission.get("reorder_quantities", {}) == answer_key["answer_key"].get("reorder_quantities", {}):
        results["reorder_quantities_correct"] = True
    
    # Check purchase_priority (ordered)
    if submission.get("purchase_priority", []) == answer_key["answer_key"].get("purchase_priority", []):
        results["purchase_priority_correct"] = True
    
    # Check justification keywords
    justification = submission.get("justification", "").lower()
    all_keywords_present = True
    for keyword in answer_key["answer_key"].get("required_justification_keywords", []):
        if keyword.lower() not in justification:
            all_keywords_present = False
            break
    results["justification_correct"] = all_keywords_present
    
    # Calculate overall score (percentage of correct tasks)
    correct_tasks = sum(results.values()) - 1  # subtract 1 because overall_score is included in values
    total_tasks = 4
    results["overall_score"] = int((correct_tasks / total_tasks) * 100)
    
    return results

def save_results(results):
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=2)
    print("Evaluation completed. Results saved to test_results.json")

def main():
    # Load submission and answer key
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')
    
    if submission and answer_key:
        # Validate the submission
        results = validate_submission(submission, answer_key)
        
        # Save the results
        save_results(results)

if __name__ == "__main__":
    main()