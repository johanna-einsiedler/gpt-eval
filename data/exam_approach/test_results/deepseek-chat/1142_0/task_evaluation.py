import json

def validate_submission(submission, answer_key):
    score = 0
    detailed_results = {
        "task_1": {"points": 0, "max_points": 30, "feedback": ""},
        "task_2": {"points": 0, "max_points": 40, "feedback": ""},
        "task_3": {"points": 0, "max_points": 30, "feedback": ""}
    }
    
    # Task 1 Validation
    if submission["task_1"]["selected_supplier"] == answer_key["task_1"]["correct_supplier"]:
        score += 20
        detailed_results["task_1"]["points"] += 20
        justification = submission["task_1"]["justification"].lower()
        if all(kw in justification for kw in answer_key["task_1"]["required_keywords"]):
            score += 10
            detailed_results["task_1"]["points"] += 10
        else:
            detailed_results["task_1"]["feedback"] = "Justification missing required keywords"
    else:
        detailed_results["task_1"]["feedback"] = "Incorrect supplier selected"
    
    # Task 2 Validation
    try:
        target_price = float(submission["task_2"]["target_price"].replace('$','').replace(',',''))
        price_min = float(answer_key["task_2"]["price_range"][0].replace('$',''))
        price_max = float(answer_key["task_2"]["price_range"][1].replace('$',''))
        
        if price_min <= target_price <= price_max:
            score += 15
            detailed_results["task_2"]["points"] += 15
        else:
            detailed_results["task_2"]["feedback"] = "Target price out of valid range"
    except:
        detailed_results["task_2"]["feedback"] = "Invalid target price format"
    
    strategy = submission["task_2"]["negotiation_strategy"].lower()
    if any(kw in strategy for kw in answer_key["task_2"]["required_strategy_keywords"]):
        score += 15
        detailed_results["task_2"]["points"] += 15
    else:
        if not detailed_results["task_2"]["feedback"]:
            detailed_results["task_2"]["feedback"] = "Negotiation strategy missing required elements"
    
    try:
        savings = float(submission["task_2"]["potential_savings"].replace('$','').replace(',',''))
        if savings >= answer_key["task_2"]["min_savings"]:
            score += 10
            detailed_results["task_2"]["points"] += 10
        else:
            if not detailed_results["task_2"]["feedback"]:
                detailed_results["task_2"]["feedback"] = "Potential savings below minimum threshold"
    except:
        if not detailed_results["task_2"]["feedback"]:
            detailed_results["task_2"]["feedback"] = "Invalid savings format"
    
    # Task 3 Validation
    try:
        quantity = int(submission["task_3"]["order_quantity"].split()[0])
        if answer_key["task_3"]["quantity_range"][0] <= quantity <= answer_key["task_3"]["quantity_range"][1]:
            score += 15
            detailed_results["task_3"]["points"] += 15
        else:
            detailed_results["task_3"]["feedback"] = "Order quantity out of valid range"
    except:
        detailed_results["task_3"]["feedback"] = "Invalid order quantity format"
    
    reasoning = submission["task_3"]["reasoning"].lower()
    if all(kw in reasoning for kw in answer_key["task_3"]["required_reasoning_keywords"]):
        score += 15
        detailed_results["task_3"]["points"] += 15
    else:
        if not detailed_results["task_3"]["feedback"]:
            detailed_results["task_3"]["feedback"] = "Reasoning missing required elements"
    
    # Calculate overall score percentage
    max_score = sum([v["max_points"] for v in detailed_results.values()])
    overall_score = (score / max_score) * 100
    
    # Prepare final results
    results = {
        "overall_score": round(overall_score, 2),
        "detailed_results": detailed_results,
        "pass_status": "Pass" if score >= 60 else "Fail"
    }
    
    return results

def main():
    try:
        # Load submission and answer key
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
        
        # Evaluate submission
        results = validate_submission(submission, answer_key)
        
        # Save results
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Evaluation completed successfully. Results saved to test_results.json")
    
    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found in the current directory")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in submission or answer key")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()