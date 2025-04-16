#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, Tuple

def load_json(filename: str) -> Dict[str, Any]:
    """Load JSON data from file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 1: Sales Trend Analysis."""
    score = 0
    max_score = 4
    feedback = {}
    
    # Check highest growth category
    if submission['highest_growth_category'] == answer_key['highest_growth_category']:
        score += 1
        feedback['highest_growth_category'] = "Correct"
    else:
        feedback['highest_growth_category'] = f"Incorrect. Expected: {answer_key['highest_growth_category']}"
    
    # Check average monthly sales with 1% tolerance
    avg_sales_correct = True
    avg_sales_feedback = {}
    for category in answer_key['average_monthly_sales_q4']:
        submitted = submission['average_monthly_sales_q4'].get(category, 0)
        expected = answer_key['average_monthly_sales_q4'][category]
        
        # Check if within 1% of correct value
        if abs((submitted - expected) / expected) <= 0.01:
            avg_sales_feedback[category] = "Correct"
        else:
            avg_sales_correct = False
            avg_sales_feedback[category] = f"Incorrect. Expected: {expected:.2f}, got: {submitted:.2f}"
    
    if avg_sales_correct:
        score += 1
    
    feedback['average_monthly_sales_q4'] = avg_sales_feedback
    
    # Check lowest sales month
    if submission['lowest_sales_month'] == answer_key['lowest_sales_month']:
        score += 1
        feedback['lowest_sales_month'] = "Correct"
    else:
        feedback['lowest_sales_month'] = f"Incorrect. Expected: {answer_key['lowest_sales_month']}"
    
    # Check percentage decrease with 0.5 percentage point tolerance
    submitted_pct = submission['percentage_decrease']
    expected_pct = answer_key['percentage_decrease']
    if abs(submitted_pct - expected_pct) <= 0.5:
        score += 1
        feedback['percentage_decrease'] = "Correct"
    else:
        feedback['percentage_decrease'] = f"Incorrect. Expected: {expected_pct:.2f}, got: {submitted_pct:.2f}"
    
    return score / max_score, feedback

def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 2: Economic Indicator Interpretation."""
    score = 0
    max_score = 3
    feedback = {}
    
    # Check interest rate values (must be 100% accurate)
    interest_rate_correct = True
    if submission['current_interest_rate'] == answer_key['current_interest_rate']:
        feedback['current_interest_rate'] = "Correct"
    else:
        interest_rate_correct = False
        feedback['current_interest_rate'] = f"Incorrect. Expected: {answer_key['current_interest_rate']}, got: {submission['current_interest_rate']}"
    
    if submission['interest_rate_change'] == answer_key['interest_rate_change']:
        feedback['interest_rate_change'] = "Correct"
    else:
        interest_rate_correct = False
        feedback['interest_rate_change'] = f"Incorrect. Expected: {answer_key['interest_rate_change']}, got: {submission['interest_rate_change']}"
    
    if interest_rate_correct:
        score += 1
    
    # Check consumer confidence index and direction (must be 100% accurate)
    confidence_correct = True
    if submission['consumer_confidence_index'] == answer_key['consumer_confidence_index']:
        feedback['consumer_confidence_index'] = "Correct"
    else:
        confidence_correct = False
        feedback['consumer_confidence_index'] = f"Incorrect. Expected: {answer_key['consumer_confidence_index']}, got: {submission['consumer_confidence_index']}"
    
    if submission['confidence_index_direction'] == answer_key['confidence_index_direction']:
        feedback['confidence_index_direction'] = "Correct"
    else:
        confidence_correct = False
        feedback['confidence_index_direction'] = f"Incorrect. Expected: {answer_key['confidence_index_direction']}, got: {submission['confidence_index_direction']}"
    
    if confidence_correct:
        score += 1
    
    # Check economic impacts (need 4 of 5 correct)
    correct_impacts = 0
    impact_feedback = {}
    
    for indicator in answer_key['economic_impacts']:
        submitted_impact = submission['economic_impacts'].get(indicator, "")
        expected_impact = answer_key['economic_impacts'][indicator]
        
        if submitted_impact == expected_impact:
            correct_impacts += 1
            impact_feedback[indicator] = "Correct"
        else:
            impact_feedback[indicator] = f"Incorrect. Expected: {expected_impact}, got: {submitted_impact}"
    
    if correct_impacts >= 4:
        score += 1
        
    feedback['economic_impacts'] = impact_feedback
    feedback['economic_impacts_score'] = f"{correct_impacts}/5 correct"
    
    return score / max_score, feedback

def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 3: Sales Forecasting."""
    score = 0
    max_score = 3
    feedback = {}
    
    # Check monthly forecasts (within 2% of correct values)
    forecast_months = ['forecast_july', 'forecast_august', 'forecast_september']
    forecast_correct = True
    
    for month in forecast_months:
        month_feedback = {}
        for category in answer_key[month]:
            submitted = submission[month].get(category, 0)
            expected = answer_key[month][category]
            
            # Check if within 2% of correct value
            if abs((submitted - expected) / expected) <= 0.02:
                month_feedback[category] = "Correct"
            else:
                forecast_correct = False
                month_feedback[category] = f"Incorrect. Expected: {expected:.2f}, got: {submitted:.2f}"
        
        feedback[month] = month_feedback
    
    if forecast_correct:
        score += 1
    
    # Check regional sales projections (within 2% of correct values)
    regional_correct = True
    regional_feedback = {}
    
    for region in answer_key['q3_regional_sales']:
        submitted = submission['q3_regional_sales'].get(region, 0)
        expected = answer_key['q3_regional_sales'][region]
        
        # Check if within 2% of correct value
        if abs((submitted - expected) / expected) <= 0.02:
            regional_feedback[region] = "Correct"
        else:
            regional_correct = False
            regional_feedback[region] = f"Incorrect. Expected: {expected:.2f}, got: {submitted:.2f}"
    
    feedback['q3_regional_sales'] = regional_feedback
    
    if regional_correct:
        score += 1
    
    # Check highest August category
    if submission['highest_august_category'] == answer_key['highest_august_category']:
        score += 1
        feedback['highest_august_category'] = "Correct"
    else:
        feedback['highest_august_category'] = f"Incorrect. Expected: {answer_key['highest_august_category']}"
    
    return score / max_score, feedback

def evaluate_task4(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate Task 4: Inventory Planning."""
    score = 0
    max_score = 3
    feedback = {}
    
    # Check if the candidate identified the correct top 3 categories
    correct_categories = set(answer_key['inventory_allocation'].keys())
    submitted_categories = set(submission['inventory_allocation'].keys())
    
    categories_correct = correct_categories == submitted_categories
    if categories_correct:
        score += 1
        feedback['top_categories'] = "Correct"
    else:
        missing = correct_categories - submitted_categories
        extra = submitted_categories - correct_categories
        feedback['top_categories'] = f"Incorrect. Missing: {missing if missing else 'None'}, Extra: {extra if extra else 'None'}"
    
    # Check optimal stock calculations (within 3% of correct values)
    if categories_correct:
        stock_correct = True
        stock_feedback = {}
        
        for category in answer_key['optimal_stock_levels']:
            submitted = submission['optimal_stock_levels'].get(category, 0)
            expected = answer_key['optimal_stock_levels'][category]
            
            # Check if within 3% of correct value
            if abs((submitted - expected) / expected) <= 0.03:
                stock_feedback[category] = "Correct"
            else:
                stock_correct = False
                stock_feedback[category] = f"Incorrect. Expected: {expected:.2f}, got: {submitted:.2f}"
        
        if stock_correct:
            score += 1
    else:
        stock_feedback = "Cannot evaluate due to incorrect categories"
    
    feedback['optimal_stock_levels'] = stock_feedback
    
    # Check maximum investment (within 5% of correct value)
    submitted_investment = submission['maximum_investment']
    expected_investment = answer_key['maximum_investment']
    
    if abs((submitted_investment - expected_investment) / expected_investment) <= 0.05:
        score += 1
        feedback['maximum_investment'] = "Correct"
    else:
        feedback['maximum_investment'] = f"Incorrect. Expected: {expected_investment:.2f}, got: {submitted_investment:.2f}"
    
    return score / max_score, feedback

def check_methodology(submission: Dict[str, Any], scores: Dict[str, float]) -> Tuple[bool, Dict[str, Any]]:
    """Check if the candidate correctly applied at least 3 of 4 analytical techniques."""
    correct_techniques = 0
    technique_feedback = {}
    
    # Consider a technique correctly applied if the task score is at least 0.75
    if scores['task1'] >= 0.75:
        correct_techniques += 1
        technique_feedback['Sales Trend Analysis'] = "Correctly applied"
    else:
        technique_feedback['Sales Trend Analysis'] = "Not correctly applied"
        
    if scores['task2'] >= 0.67:  # 2 out of 3 or better
        correct_techniques += 1
        technique_feedback['Economic Indicator Interpretation'] = "Correctly applied"
    else:
        technique_feedback['Economic Indicator Interpretation'] = "Not correctly applied"
        
    if scores['task3'] >= 0.67:  # 2 out of 3 or better
        correct_techniques += 1
        technique_feedback['Sales Forecasting'] = "Correctly applied"
    else:
        technique_feedback['Sales Forecasting'] = "Not correctly applied"
        
    if scores['task4'] >= 0.67:  # 2 out of 3 or better
        correct_techniques += 1
        technique_feedback['Inventory Planning'] = "Correctly applied"
    else:
        technique_feedback['Inventory Planning'] = "Not correctly applied"
    
    return correct_techniques >= 3, technique_feedback

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Not provided"),
        "task_scores": {},
        "task_feedback": {},
        "analytical_techniques": {},
        "overall_score": 0
    }
    
    # Evaluate each task
    task1_score, task1_feedback = evaluate_task1(submission["task1"], answer_key["task1"])
    task2_score, task2_feedback = evaluate_task2(submission["task2"], answer_key["task2"])
    task3_score, task3_feedback = evaluate_task3(submission["task3"], answer_key["task3"])
    task4_score, task4_feedback = evaluate_task4(submission["task4"], answer_key["task4"])
    
    # Store scores and feedback
    results["task_scores"] = {
        "task1": task1_score,
        "task2": task2_score,
        "task3": task3_score,
        "task4": task4_score
    }
    
    results["task_feedback"] = {
        "task1": task1_feedback,
        "task2": task2_feedback,
        "task3": task3_feedback,
        "task4": task4_feedback
    }
    
    # Check methodology
    methodology_correct, technique_feedback = check_methodology(submission, results["task_scores"])
    results["analytical_techniques"] = technique_feedback
    results["methodology_correct"] = methodology_correct
    
    # Calculate overall score (80% required to pass)
    # Equal weight for each task (25% each)
    raw_score = (task1_score + task2_score + task3_score + task4_score) / 4
    
    # Critical error check - if any task is completely failed, the overall score is capped
    critical_error = False
    for task_score in results["task_scores"].values():
        if task_score == 0:
            critical_error = True
    
    # Factor in methodology requirement
    if not methodology_correct:
        critical_error = True
    
    # Calculate final score
    results["overall_score"] = raw_score * 100  # Convert to percentage
    
    # Determine pass/fail status (need 80% and no critical errors)
    results["passed"] = results["overall_score"] >= 80 and not critical_error
    
    if critical_error:
        results["critical_error"] = True
        results["critical_error_message"] = "Critical error detected: either completely failed a task or did not correctly apply at least 3 analytical techniques"
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()