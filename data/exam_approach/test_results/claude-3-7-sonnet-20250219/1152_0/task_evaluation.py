import json
import re

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_task1(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 3,
        "details": []
    }
    
    if "product_selections" not in submission:
        results["details"].append("Missing product_selections section")
        return results
    
    # Create a lookup dictionary from answer key
    valid_options = {}
    justification_keywords = {}
    for item in answer_key["product_selections"]:
        req_id = item["requirement_id"]
        valid_options[req_id] = item["valid_options"]
        justification_keywords[req_id] = item["justification_keywords"]
    
    # Check each submission entry
    for entry in submission["product_selections"]:
        req_id = entry.get("requirement_id")
        if req_id not in valid_options:
            results["details"].append(f"Invalid requirement_id: {req_id}")
            continue
        
        # Check if product selection is valid
        product_valid = False
        for option in valid_options[req_id]:
            if (entry.get("catalog_id") == option["catalog_id"] and 
                entry.get("product_code") == option["product_code"] and 
                entry.get("price") == option["price"]):
                product_valid = True
                break
        
        # Check justification
        justification = entry.get("justification", "").lower()
        keywords_found = sum(1 for keyword in justification_keywords[req_id] 
                            if keyword.lower() in justification)
        justification_valid = keywords_found >= 2  # At least 2 keywords
        
        # Score this entry
        if product_valid and justification_valid:
            results["score"] += 1
            results["details"].append(f"{req_id}: Correct product and justification")
        elif product_valid:
            results["score"] += 0.5
            results["details"].append(f"{req_id}: Correct product but insufficient justification")
        elif justification_valid:
            results["score"] += 0.25
            results["details"].append(f"{req_id}: Invalid product but reasonable justification")
        else:
            results["details"].append(f"{req_id}: Incorrect product and insufficient justification")
    
    return results

def evaluate_task2(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 4,  # 2 suppliers for each of 2 requirements
        "details": []
    }
    
    if "suppliers" not in submission:
        results["details"].append("Missing suppliers section")
        return results
    
    # Group submissions by requirement
    submissions_by_req = {}
    for entry in submission["suppliers"]:
        req_id = entry.get("requirement_id")
        if req_id not in submissions_by_req:
            submissions_by_req[req_id] = []
        submissions_by_req[req_id].append(entry)
    
    # Check each requirement
    for req_id, req_data in answer_key["suppliers"].items():
        if req_id not in submissions_by_req:
            results["details"].append(f"Missing entries for {req_id}")
            continue
        
        valid_entries = 0
        for entry in submissions_by_req[req_id]:
            # Check required fields
            fields_valid = all(entry.get(field) for field in req_data["required_fields"])
            
            # Check source
            source_valid = entry.get("source") in req_data["source_options"]
            
            # Check keywords
            entry_text = " ".join(str(value).lower() for value in entry.values())
            keywords_found = sum(1 for keyword in req_data["keywords"] 
                                if keyword.lower() in entry_text)
            keywords_valid = keywords_found >= 2  # At least 2 keywords
            
            if fields_valid and source_valid and keywords_valid:
                valid_entries += 1
                results["details"].append(f"{req_id}: Valid supplier entry")
            else:
                missing = []
                if not fields_valid:
                    missing.append("required fields")
                if not source_valid:
                    missing.append("valid source")
                if not keywords_valid:
                    missing.append("relevant keywords")
                results["details"].append(f"{req_id}: Invalid entry - missing {', '.join(missing)}")
        
        # Score based on valid entries (max 2 per requirement)
        results["score"] += min(valid_entries, 2)
    
    return results

def evaluate_task3(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 3,  # 1 for table, 2 for recommendation
        "details": []
    }
    
    # Check comparison table
    table_correct = True
    if "comparison_table" not in submission:
        results["details"].append("Missing comparison_table section")
        table_correct = False
    else:
        # Convert answer key table to a lookup dictionary
        expected_table = {f"{item['supplier']}_{item['product']}": item 
                         for item in answer_key["comparison_table"]}
        
        # Check each entry in submission
        for entry in submission["comparison_table"]:
            key = f"{entry.get('supplier')}_{entry.get('product')}"
            if key not in expected_table:
                results["details"].append(f"Unexpected table entry: {key}")
                table_correct = False
                continue
            
            expected = expected_table[key]
            for field in ["price", "delivery_time", "warranty", "rating"]:
                if entry.get(field) != expected[field]:
                    results["details"].append(f"Incorrect {field} for {key}")
                    table_correct = False
    
    if table_correct:
        results["score"] += 1
        results["details"].append("Comparison table is correct")
    
    # Check recommendation
    recommendation = submission.get("recommendation", "")
    justification = submission.get("justification", "").lower()
    
    # Check if recommendation is valid
    rec_valid = any(valid_rec in recommendation 
                   for valid_rec in answer_key["valid_recommendations"])
    
    # Check justification
    keywords_found = sum(1 for keyword in answer_key["justification_keywords"] 
                        if keyword.lower() in justification)
    justification_valid = keywords_found >= 3  # At least 3 keywords
    
    # Score recommendation and justification
    if rec_valid and justification_valid:
        results["score"] += 2
        results["details"].append("Valid recommendation with good justification")
    elif rec_valid:
        results["score"] += 1
        results["details"].append("Valid recommendation but insufficient justification")
    elif justification_valid:
        results["score"] += 0.5
        results["details"].append("Invalid recommendation but reasonable justification")
    else:
        results["details"].append("Invalid recommendation and insufficient justification")
    
    return results

def evaluate_task4(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 5,  # 3 for questions, 2 for information needed
        "details": []
    }
    
    # Evaluate clarification questions
    if "clarification_questions" not in submission:
        results["details"].append("Missing clarification_questions section")
    else:
        questions = submission["clarification_questions"]
        valid_categories = answer_key["clarification_questions"]["valid_categories"]
        
        # Count questions that are properly formatted and relevant
        valid_questions = 0
        categories_covered = set()
        
        for question in questions:
            # Check if it's a proper question
            is_question = question.strip().endswith("?")
            
            # Check if it covers a valid category
            category_match = None
            for category in valid_categories:
                if category.lower() in question.lower():
                    category_match = category
                    categories_covered.add(category)
                    break
            
            if is_question and category_match:
                valid_questions += 1
                results["details"].append(f"Valid question covering: {category_match}")
            elif is_question:
                results["details"].append("Question format correct but category unclear")
            else:
                results["details"].append("Invalid question format")
        
        # Score based on valid questions and category coverage
        question_score = min(valid_questions, 5) * 0.4 + min(len(categories_covered), 3) * 0.4
        results["score"] += min(question_score, 3)  # Max 3 points
    
    # Evaluate information needed
    if "information_needed" not in submission:
        results["details"].append("Missing information_needed section")
    else:
        info_items = submission["information_needed"]
        valid_categories = answer_key["information_needed"]["valid_categories"]
        
        # Count valid information items
        valid_items = 0
        categories_covered = set()
        
        for item in info_items:
            # Check if it covers a valid category
            category_match = None
            for category in valid_categories:
                if category.lower() in item.lower():
                    category_match = category
                    categories_covered.add(category)
                    break
            
            # Check if it's stated as information, not a question
            is_info = not item.strip().endswith("?")
            
            if is_info and category_match:
                valid_items += 1
                results["details"].append(f"Valid information need: {category_match}")
            elif is_info:
                results["details"].append("Information format correct but category unclear")
            else:
                results["details"].append("Invalid information format (appears to be a question)")
        
        # Score based on valid items and category coverage
        info_score = min(valid_items, 3) * 0.4 + min(len(categories_covered), 2) * 0.4
        results["score"] += min(info_score, 2)  # Max 2 points
    
    return results

def calculate_overall_score(task_results):
    total_score = sum(task["score"] for task in task_results.values())
    max_score = sum(task["max_score"] for task in task_results.values())
    return (total_score / max_score) * 100

def evaluate_submission():
    # Load files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate each task
    results = {
        "task1": evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {})),
        "task2": evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {})),
        "task3": evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {})),
        "task4": evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    }
    
    # Calculate overall score
    overall_score = calculate_overall_score(results)
    
    # Determine if candidate passed
    tasks_passed = sum(1 for task in results.values() 
                      if task["score"] >= 0.7 * task["max_score"])
    passed = tasks_passed >= 3
    
    # Prepare final results
    final_results = {
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "tasks_passed": tasks_passed,
        "task_results": results,
        "candidate_id": submission.get("candidate_id", "Unknown")
    }
    
    # Save results
    with open("test_results.json", "w") as file:
        json.dump(final_results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {overall_score:.2f}%")
    print(f"Candidate {'passed' if passed else 'failed'} the exam")

if __name__ == "__main__":
    evaluate_submission()