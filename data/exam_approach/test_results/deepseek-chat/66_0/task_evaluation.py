import json

def load_json_file(filename):
    """Load a JSON file and return its content."""
    with open(filename, 'r') as file:
        return json.load(file)

def evaluate_task_1(submission, answer_key):
    """Evaluate Task 1: Sales Data Analysis."""
    results = {}
    task1_sub = submission["task_1"]
    task1_key = answer_key["expected_answers"]["task_1"]
    
    # Evaluate sales trend analysis
    trend_analysis = task1_sub["sales_trend_analysis"].lower()
    required_keywords = task1_key["sales_trend_analysis"]["required_keywords"]
    required_metrics = task1_key["sales_trend_analysis"]["required_metrics"]
    
    keyword_score = all(keyword in trend_analysis for keyword in required_keywords)
    metric_score = all(metric in trend_analysis for metric in required_metrics)
    
    results["sales_trend_analysis"] = {
        "keywords_found": keyword_score,
        "metrics_found": metric_score,
        "passed": keyword_score and metric_score
    }
    
    # Evaluate inventory recommendation
    inventory_rec = task1_sub["inventory_recommendation"].lower()
    required_keywords = task1_key["inventory_recommendation"]["required_keywords"]
    required_metrics = task1_key["inventory_recommendation"]["required_metrics"]
    
    keyword_score = all(keyword in inventory_rec for keyword in required_keywords)
    metric_score = any(metric in inventory_rec for metric in required_metrics)
    
    results["inventory_recommendation"] = {
        "keywords_found": keyword_score,
        "metrics_found": metric_score,
        "passed": keyword_score and metric_score
    }
    
    return results

def evaluate_task_2(submission, answer_key):
    """Evaluate Task 2: Market Trend Research."""
    results = {}
    task2_sub = submission["task_2"]
    task2_key = answer_key["expected_answers"]["task_2"]
    
    # Evaluate market trend research
    trend_research = task2_sub["market_trend_research"].lower()
    required_keywords = task2_key["market_trend_research"]["required_keywords"]
    banned_keywords = task2_key["market_trend_research"]["banned_keywords"]
    
    keyword_score = all(keyword in trend_research for keyword in required_keywords)
    banned_score = not any(banned in trend_research for banned in banned_keywords)
    
    results["market_trend_research"] = {
        "keywords_found": keyword_score,
        "no_banned_keywords": banned_score,
        "passed": keyword_score and banned_score
    }
    
    # Evaluate impact on demand
    impact = task2_sub["impact_on_demand"].lower()
    required_keywords = task2_key["impact_on_demand"]["required_keywords"]
    banned_keywords = task2_key["impact_on_demand"]["banned_keywords"]
    
    keyword_score = all(keyword in impact for keyword in required_keywords)
    banned_score = not any(banned in impact for banned in banned_keywords)
    
    results["impact_on_demand"] = {
        "keywords_found": keyword_score,
        "no_banned_keywords": banned_score,
        "passed": keyword_score and banned_score
    }
    
    return results

def calculate_overall_score(task1_results, task2_results):
    """Calculate the overall score based on evaluation results."""
    total_criteria = 0
    passed_criteria = 0
    
    # Count passed criteria for Task 1
    for criterion in task1_results.values():
        total_criteria += 1
        if criterion["passed"]:
            passed_criteria += 1
    
    # Count passed criteria for Task 2
    for criterion in task2_results.values():
        total_criteria += 1
        if criterion["passed"]:
            passed_criteria += 1
    
    return (passed_criteria / total_criteria) * 100

def main():
    # Load submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Evaluate both tasks
    task1_results = evaluate_task_1(submission, answer_key)
    task2_results = evaluate_task_2(submission, answer_key)
    
    # Calculate overall score
    overall_score = calculate_overall_score(task1_results, task2_results)
    
    # Prepare results dictionary
    test_results = {
        "task_1": task1_results,
        "task_2": task2_results,
        "overall_score": overall_score
    }
    
    # Save results to JSON file
    with open("test_results.json", 'w') as file:
        json.dump(test_results, file, indent=2)
    
    print("Evaluation completed. Results saved to test_results.json")

if __name__ == "__main__":
    main()