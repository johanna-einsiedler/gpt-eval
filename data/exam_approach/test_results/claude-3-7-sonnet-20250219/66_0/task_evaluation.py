import json
import math
from typing import Dict, List, Union, Any

def load_json(file_path: str) -> Dict:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json(data: Dict, file_path: str) -> None:
    """Save data as JSON to a file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")

def evaluate_top_growth_categories(submission: List, answer_key: List) -> Dict:
    """Evaluate the top growth categories answer."""
    score = 0
    max_score = 8
    
    # Check if the submission has the correct number of categories
    if len(submission) != 3:
        feedback = "Submission should contain exactly 3 categories."
    else:
        # Count correct categories
        correct_categories = set(submission).intersection(set(answer_key))
        score = (len(correct_categories) / 3) * max_score
        
        if score == max_score:
            feedback = "All categories correctly identified."
        else:
            feedback = f"Correctly identified {len(correct_categories)} out of 3 categories."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_highest_sales_months(submission: List, answer_key: List) -> Dict:
    """Evaluate the highest sales months answer."""
    score = 0
    max_score = 8
    
    # Check if the submission has the correct number of months
    if len(submission) != 3:
        feedback = "Submission should contain exactly 3 months."
    else:
        # Count correct months
        correct_months = set(submission).intersection(set(answer_key))
        score = (len(correct_months) / 3) * max_score
        
        if score == max_score:
            feedback = "All months correctly identified."
        else:
            feedback = f"Correctly identified {len(correct_months)} out of 3 months."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_profit_margins(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the profit margins answer."""
    score = 0
    max_score = 10
    tolerance = 0.02
    
    # Check if all categories are present
    missing_categories = set(answer_key.keys()) - set(submission.keys())
    if missing_categories:
        feedback = f"Missing categories: {', '.join(missing_categories)}"
        return {"score": 0, "max_score": max_score, "feedback": feedback}
    
    # Check each category's profit margin
    correct_margins = 0
    incorrect_margins = []
    
    for category, expected_margin in answer_key.items():
        submitted_margin = submission.get(category, 0)
        if abs(submitted_margin - expected_margin) <= tolerance:
            correct_margins += 1
        else:
            incorrect_margins.append(category)
    
    score = (correct_margins / len(answer_key)) * max_score
    
    if score == max_score:
        feedback = "All profit margins correctly calculated within tolerance."
    else:
        feedback = f"Incorrect profit margins for: {', '.join(incorrect_margins)}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_worst_performing_products(submission: List, answer_key: List) -> Dict:
    """Evaluate the worst performing products answer."""
    score = 0
    max_score = 9
    
    # Check if the submission has the correct number of products
    if len(submission) != 3:
        feedback = "Submission should contain exactly 3 products."
    else:
        # Count correct products
        correct_products = set(submission).intersection(set(answer_key))
        score = (len(correct_products) / 3) * max_score
        
        if score == max_score:
            feedback = "All worst-performing products correctly identified."
        else:
            feedback = f"Correctly identified {len(correct_products)} out of 3 products."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_correlation_coefficient(submission: float, answer_key: float) -> Dict:
    """Evaluate the correlation coefficient answer."""
    score = 0
    max_score = 10
    tolerance = 0.05
    
    if abs(submission - answer_key) <= tolerance:
        score = max_score
        feedback = "Correlation coefficient correctly calculated within tolerance."
    else:
        feedback = f"Correlation coefficient outside acceptable range. Expected around {answer_key}."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_strongest_correlated_category(submission: str, answer_key: str) -> Dict:
    """Evaluate the strongest correlated category answer."""
    score = 0
    max_score = 10
    
    if submission == answer_key:
        score = max_score
        feedback = "Strongest correlated category correctly identified."
    else:
        feedback = f"Incorrect category. Expected: {answer_key}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_lag_time(submission: int, answer_key: int) -> Dict:
    """Evaluate the average lag time answer."""
    score = 0
    max_score = 10
    
    # Accept values between 1-3 months if the answer key is 2
    if answer_key == 2 and 1 <= submission <= 3:
        score = max_score
        feedback = "Lag time within acceptable range."
    elif submission == answer_key:
        score = max_score
        feedback = "Lag time correctly identified."
    else:
        feedback = f"Incorrect lag time. Expected: {answer_key}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_q1_forecast(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the Q1 2023 forecast answer."""
    score = 0
    max_score = 10
    tolerance_percentage = 0.10  # 10% tolerance
    
    # Check if all categories are present
    missing_categories = set(answer_key.keys()) - set(submission.keys())
    if missing_categories:
        feedback = f"Missing categories: {', '.join(missing_categories)}"
        return {"score": 0, "max_score": max_score, "feedback": feedback}
    
    # Check each category's forecast
    correct_forecasts = 0
    incorrect_forecasts = []
    
    for category, expected_forecast in answer_key.items():
        submitted_forecast = submission.get(category, 0)
        tolerance = expected_forecast * tolerance_percentage
        
        if abs(submitted_forecast - expected_forecast) <= tolerance:
            correct_forecasts += 1
        else:
            incorrect_forecasts.append(category)
    
    score = (correct_forecasts / len(answer_key)) * max_score
    
    if score == max_score:
        feedback = "All forecasts within acceptable range."
    else:
        feedback = f"Forecasts outside acceptable range for: {', '.join(incorrect_forecasts)}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_inventory_recommendations(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the inventory recommendations answer."""
    score = 0
    max_score = 8
    
    # Check if all categories are present
    missing_categories = set(answer_key.keys()) - set(submission.keys())
    if missing_categories:
        feedback = f"Missing categories: {', '.join(missing_categories)}"
        return {"score": 0, "max_score": max_score, "feedback": feedback}
    
    # Check each category's recommendation
    correct_recommendations = 0
    incorrect_recommendations = []
    
    for category, expected_recommendation in answer_key.items():
        submitted_recommendation = submission.get(category, "")
        
        if submitted_recommendation == expected_recommendation:
            correct_recommendations += 1
        else:
            incorrect_recommendations.append(category)
    
    score = (correct_recommendations / len(answer_key)) * max_score
    
    if score == max_score:
        feedback = "All inventory recommendations correct."
    else:
        feedback = f"Incorrect recommendations for: {', '.join(incorrect_recommendations)}"
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_product_allocation(submission: List, answer_key: List, allocation_type: str) -> Dict:
    """Evaluate the product allocation answers (increase or decrease)."""
    score = 0
    max_score = 6
    
    # Check if the submission has the correct number of products
    if len(submission) != 3:
        feedback = f"Submission should contain exactly 3 products for {allocation_type} allocation."
    else:
        # Count correct products
        correct_products = set(submission).intersection(set(answer_key))
        score = (len(correct_products) / 3) * max_score
        
        if score == max_score:
            feedback = f"All {allocation_type} allocation products correctly identified."
        else:
            feedback = f"Correctly identified {len(correct_products)} out of 3 products for {allocation_type} allocation."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_economic_indicators(submission: List, answer_key: List) -> Dict:
    """Evaluate the influential economic indicators answer."""
    score = 0
    max_score = 5
    
    # Check if the submission has the correct number of indicators
    if len(submission) != 3:
        feedback = "Submission should contain exactly 3 economic indicators."
    else:
        # Count correct indicators
        correct_indicators = set(submission).intersection(set(answer_key))
        score = (len(correct_indicators) / 3) * max_score
        
        if score == max_score:
            feedback = "All economic indicators correctly identified."
        else:
            feedback = f"Correctly identified {len(correct_indicators)} out of 3 economic indicators."
    
    return {
        "score": score,
        "max_score": max_score,
        "feedback": feedback
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1": {},
        "task2": {},
        "task3": {},
        "task_scores": {},
        "overall_score": 0
    }
    
    # Task 1 evaluation
    task1 = submission.get("task1", {})
    task1_key = answer_key.get("task1", {})
    
    results["task1"]["top_growth_categories"] = evaluate_top_growth_categories(
        task1.get("top_growth_categories", []), 
        task1_key.get("top_growth_categories", [])
    )
    
    results["task1"]["highest_sales_months"] = evaluate_highest_sales_months(
        task1.get("highest_sales_months", []), 
        task1_key.get("highest_sales_months", [])
    )
    
    results["task1"]["profit_margins_2022"] = evaluate_profit_margins(
        task1.get("profit_margins_2022", {}), 
        task1_key.get("profit_margins_2022", {})
    )
    
    results["task1"]["worst_performing_products"] = evaluate_worst_performing_products(
        task1.get("worst_performing_products", []), 
        task1_key.get("worst_performing_products", [])
    )
    
    # Task 2 evaluation
    task2 = submission.get("task2", {})
    task2_key = answer_key.get("task2", {})
    
    results["task2"]["overall_correlation_coefficient"] = evaluate_correlation_coefficient(
        task2.get("overall_correlation_coefficient", 0), 
        task2_key.get("overall_correlation_coefficient", 0)
    )
    
    results["task2"]["strongest_correlated_category"] = evaluate_strongest_correlated_category(
        task2.get("strongest_correlated_category", ""), 
        task2_key.get("strongest_correlated_category", "")
    )
    
    results["task2"]["average_lag_time_months"] = evaluate_lag_time(
        task2.get("average_lag_time_months", 0), 
        task2_key.get("average_lag_time_months", 0)
    )
    
    # Task 3 evaluation
    task3 = submission.get("task3", {})
    task3_key = answer_key.get("task3", {})
    
    results["task3"]["q1_2023_forecast"] = evaluate_q1_forecast(
        task3.get("q1_2023_forecast", {}), 
        task3_key.get("q1_2023_forecast", {})
    )
    
    results["task3"]["inventory_recommendations"] = evaluate_inventory_recommendations(
        task3.get("inventory_recommendations", {}), 
        task3_key.get("inventory_recommendations", {})
    )
    
    results["task3"]["increase_allocation_products"] = evaluate_product_allocation(
        task3.get("increase_allocation_products", []), 
        task3_key.get("increase_allocation_products", []),
        "increase"
    )
    
    results["task3"]["decrease_allocation_products"] = evaluate_product_allocation(
        task3.get("decrease_allocation_products", []), 
        task3_key.get("decrease_allocation_products", []),
        "decrease"
    )
    
    results["task3"]["influential_economic_indicators"] = evaluate_economic_indicators(
        task3.get("influential_economic_indicators", []), 
        task3_key.get("influential_economic_indicators", [])
    )
    
    # Calculate task scores
    task1_score = sum(item["score"] for item in results["task1"].values())
    task1_max = sum(item["max_score"] for item in results["task1"].values())
    
    task2_score = sum(item["score"] for item in results["task2"].values())
    task2_max = sum(item["max_score"] for item in results["task2"].values())
    
    task3_score = sum(item["score"] for item in results["task3"].values())
    task3_max = sum(item["max_score"] for item in results["task3"].values())
    
    results["task_scores"] = {
        "task1": {
            "score": task1_score,
            "max_score": task1_max,
            "percentage": round((task1_score / task1_max) * 100, 2) if task1_max > 0 else 0
        },
        "task2": {
            "score": task2_score,
            "max_score": task2_max,
            "percentage": round((task2_score / task2_max) * 100, 2) if task2_max > 0 else 0
        },
        "task3": {
            "score": task3_score,
            "max_score": task3_max,
            "percentage": round((task3_score / task3_max) * 100, 2) if task3_max > 0 else 0
        }
    }
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    total_max = task1_max + task2_max + task3_max
    results["overall_score"] = round((total_score / total_max) * 100, 2) if total_max > 0 else 0
    
    # Determine if the candidate passed
    task1_subtasks_correct = sum(1 for item in results["task1"].values() if item["score"] == item["max_score"])
    task2_subtasks_correct = sum(1 for item in results["task2"].values() if item["score"] == item["max_score"])
    task3_subtasks_correct = sum(1 for item in results["task3"].values() if item["score"] == item["max_score"])
    
    passed_task1 = task1_subtasks_correct >= 3
    passed_task2 = task2_subtasks_correct >= 2
    passed_task3 = task3_subtasks_correct >= 3
    passed_overall = results["overall_score"] >= 75
    
    results["passing_criteria"] = {
        "task1_minimum_met": passed_task1,
        "task2_minimum_met": passed_task2,
        "task3_minimum_met": passed_task3,
        "overall_score_minimum_met": passed_overall,
        "passed": passed_task1 and passed_task2 and passed_task3 and passed_overall
    }
    
    return results

def main():
    """Main function to evaluate the submission."""
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load submission or answer key.")
        return
    
    results = evaluate_submission(submission, answer_key)
    save_json(results, "test_results.json")
    
    # Print summary
    print(f"\nEvaluation Summary for Candidate: {results['candidate_id']}")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Task 1 Score: {results['task_scores']['task1']['percentage']}%")
    print(f"Task 2 Score: {results['task_scores']['task2']['percentage']}%")
    print(f"Task 3 Score: {results['task_scores']['task3']['percentage']}%")
    print(f"Passed: {results['passing_criteria']['passed']}")

if __name__ == "__main__":
    main()