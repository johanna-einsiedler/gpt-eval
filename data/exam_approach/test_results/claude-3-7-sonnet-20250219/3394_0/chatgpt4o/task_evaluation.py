#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_q1_variance(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the Q1 variance calculations."""
    results = {
        "score": 0,
        "max_score": 40,  # 20 categories, 2 points each (dollar and percentage)
        "details": []
    }
    
    correct_count = 0
    total_items = 0
    
    for dept in answer_key["q1_variance"]:
        if dept not in submission["q1_variance"]:
            results["details"].append(f"Missing department: {dept}")
            continue
            
        for category in answer_key["q1_variance"][dept]:
            if category not in submission["q1_variance"][dept]:
                results["details"].append(f"Missing category: {dept} - {category}")
                continue
                
            # Check dollar variance
            key_dollar = answer_key["q1_variance"][dept][category]["dollar_variance"]
            sub_dollar = submission["q1_variance"][dept][category]["dollar_variance"]
            dollar_correct = abs(key_dollar - sub_dollar) <= 1  # Allow for rounding differences
            
            # Check percentage variance
            key_pct = answer_key["q1_variance"][dept][category]["percentage_variance"]
            sub_pct = submission["q1_variance"][dept][category]["percentage_variance"]
            pct_correct = abs(key_pct - sub_pct) <= 0.2  # Allow for rounding differences
            
            if dollar_correct:
                correct_count += 1
            else:
                results["details"].append(f"Incorrect dollar variance for {dept} - {category}: got {sub_dollar}, expected {key_dollar}")
                
            if pct_correct:
                correct_count += 1
            else:
                results["details"].append(f"Incorrect percentage variance for {dept} - {category}: got {sub_pct}, expected {key_pct}")
                
            total_items += 2
    
    # Calculate score
    if total_items > 0:
        results["score"] = round((correct_count / total_items) * results["max_score"])
        results["accuracy"] = round((correct_count / total_items) * 100, 1)
    
    return results

def evaluate_top_overbudget(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the top 3 over-budget categories identification."""
    results = {
        "score": 0,
        "max_score": 15,  # 5 points per correct category
        "details": []
    }
    
    # Extract just the category and department for comparison
    key_categories = [(item["category"], item["department"]) for item in answer_key["q1_top_overbudget_categories"]]
    sub_categories = [(item["category"], item["department"]) for item in submission["q1_top_overbudget_categories"]]
    
    # Check if the right categories are identified
    correct_count = 0
    for i, key_cat in enumerate(key_categories):
        if i < len(sub_categories) and key_cat in sub_categories:
            correct_count += 1
        else:
            results["details"].append(f"Missing or incorrect overbudget category: {key_cat[1]} - {key_cat[0]}")
    
    # Check if they're in the right order (most negative to least)
    if len(sub_categories) >= 3:
        # Get the dollar variances from the submission
        sub_variances = [item["dollar_variance"] for item in submission["q1_top_overbudget_categories"]]
        
        # Check if they're in ascending order (most negative first)
        if not all(sub_variances[i] <= sub_variances[i+1] for i in range(len(sub_variances)-1)):
            results["details"].append("Overbudget categories are not sorted correctly from most negative to least negative")
            correct_count -= 0.5  # Partial penalty for incorrect sorting
    
    results["score"] = round((correct_count / 3) * results["max_score"])
    results["accuracy"] = round((correct_count / 3) * 100, 1)
    
    return results

def evaluate_june_forecast(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the June forecasts."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": []
    }
    
    correct_count = 0
    total_items = 0
    
    for dept in answer_key["june_forecast"]:
        if dept not in submission["june_forecast"]:
            results["details"].append(f"Missing department: {dept}")
            continue
            
        for category in answer_key["june_forecast"][dept]:
            if category == "Total":  # Skip the total for now
                continue
                
            if category not in submission["june_forecast"][dept]:
                results["details"].append(f"Missing category: {dept} - {category}")
                continue
                
            key_forecast = answer_key["june_forecast"][dept][category]
            sub_forecast = submission["june_forecast"][dept][category]
            
            # Allow for reasonable variation in forecasts (within 10%)
            if key_forecast == 0:
                forecast_correct = sub_forecast == 0
            else:
                forecast_correct = abs((sub_forecast - key_forecast) / key_forecast) <= 0.10
                
            if forecast_correct:
                correct_count += 1
            else:
                results["details"].append(f"Unreasonable June forecast for {dept} - {category}: got {sub_forecast}, expected around {key_forecast}")
                
            total_items += 1
    
    # Calculate score
    if total_items > 0:
        results["score"] = round((correct_count / total_items) * results["max_score"])
        results["accuracy"] = round((correct_count / total_items) * 100, 1)
    
    return results

def evaluate_yearend_variance(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the projected year-end variance."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Check dollar variance
    key_dollar = answer_key["projected_yearend_variance"]["dollar_variance"]
    sub_dollar = submission["projected_yearend_variance"]["dollar_variance"]
    dollar_correct = abs(key_dollar - sub_dollar) <= (abs(key_dollar) * 0.15)  # Allow 15% variation
    
    # Check percentage variance
    key_pct = answer_key["projected_yearend_variance"]["percentage_variance"]
    sub_pct = submission["projected_yearend_variance"]["percentage_variance"]
    pct_correct = abs(key_pct - sub_pct) <= 0.5  # Allow 0.5 percentage point variation
    
    correct_count = 0
    if dollar_correct:
        correct_count += 1
    else:
        results["details"].append(f"Incorrect year-end dollar variance: got {sub_dollar}, expected around {key_dollar}")
        
    if pct_correct:
        correct_count += 1
    else:
        results["details"].append(f"Incorrect year-end percentage variance: got {sub_pct}, expected around {key_pct}")
    
    results["score"] = round((correct_count / 2) * results["max_score"])
    results["accuracy"] = round((correct_count / 2) * 100, 1)
    
    return results

def evaluate_exceeding_budget(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the categories exceeding budget identification."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Extract category-department pairs for comparison
    key_categories = set((item["category"], item["department"]) for item in answer_key["categories_exceeding_budget"])
    sub_categories = set((item["category"], item["department"]) for item in submission["categories_exceeding_budget"])
    
    # Calculate correct identifications
    correct_identifications = key_categories.intersection(sub_categories)
    false_positives = sub_categories - key_categories
    false_negatives = key_categories - correct_identifications
    
    # Calculate score based on correct identifications minus penalties for errors
    accuracy = len(correct_identifications) / len(key_categories) if key_categories else 0
    
    # Apply penalties for false positives
    if false_positives:
        results["details"].append(f"Incorrectly identified {len(false_positives)} categories as exceeding budget")
        accuracy -= min(0.2, 0.05 * len(false_positives))  # Penalty capped at 20%
    
    # Note false negatives
    if false_negatives:
        results["details"].append(f"Failed to identify {len(false_negatives)} categories that exceed budget")
    
    results["score"] = round(max(0, accuracy * results["max_score"]))
    results["accuracy"] = round(max(0, accuracy) * 100, 1)
    
    return results

def evaluate_best_adherence(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the best budget adherence department identification."""
    results = {
        "score": 0,
        "max_score": 5,
        "details": []
    }
    
    key_dept = answer_key["best_budget_adherence_department"]["department"]
    sub_dept = submission["best_budget_adherence_department"]["department"]
    
    if key_dept == sub_dept:
        results["score"] = results["max_score"]
        results["accuracy"] = 100.0
    else:
        results["details"].append(f"Incorrect best adherence department: got {sub_dept}, expected {key_dept}")
        results["accuracy"] = 0.0
    
    return results

def evaluate_avg_expenditure(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the average monthly expenditure calculations."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    correct_count = 0
    total_depts = len(answer_key["q1_average_monthly_expenditure"])
    
    for dept, key_avg in answer_key["q1_average_monthly_expenditure"].items():
        if dept not in submission["q1_average_monthly_expenditure"]:
            results["details"].append(f"Missing department: {dept}")
            continue
            
        sub_avg = submission["q1_average_monthly_expenditure"][dept]
        
        # Allow for small rounding differences
        if abs(key_avg - sub_avg) <= 100:  # $100 tolerance
            correct_count += 1
        else:
            results["details"].append(f"Incorrect average expenditure for {dept}: got {sub_avg}, expected {key_avg}")
    
    results["score"] = round((correct_count / total_depts) * results["max_score"])
    results["accuracy"] = round((correct_count / total_depts) * 100, 1)
    
    return results

def evaluate_monthly_fluctuations(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the unusual monthly fluctuations identification."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Create sets of (period, category, department) tuples for comparison
    key_fluctuations = set((item["period"], item["category"], item["department"]) 
                           for item in answer_key["unusual_monthly_fluctuations"])
    
    sub_fluctuations = set((item["period"], item["category"], item["department"]) 
                           for item in submission["unusual_monthly_fluctuations"])
    
    # Calculate correct identifications
    correct_identifications = key_fluctuations.intersection(sub_fluctuations)
    false_positives = sub_fluctuations - key_fluctuations
    false_negatives = key_fluctuations - correct_identifications
    
    # Calculate score based on correct identifications
    min_required = 5  # Need to identify at least 5 of 7 fluctuations
    total_key_fluctuations = len(key_fluctuations)
    
    if len(correct_identifications) >= min_required:
        accuracy = len(correct_identifications) / total_key_fluctuations
    else:
        accuracy = (len(correct_identifications) / min_required) * 0.7  # Max 70% if below minimum
    
    # Apply small penalty for false positives
    if false_positives:
        results["details"].append(f"Incorrectly identified {len(false_positives)} fluctuations that weren't unusual")
        accuracy -= min(0.2, 0.03 * len(false_positives))  # Small penalty, capped at 20%
    
    # Note false negatives
    if false_negatives:
        results["details"].append(f"Failed to identify {len(false_negatives)} unusual fluctuations")
    
    results["score"] = round(max(0, accuracy * results["max_score"]))
    results["accuracy"] = round(max(0, accuracy) * 100, 1)
    
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "max_possible_score": 120,
        "sections": {}
    }
    
    # Evaluate each section
    results["sections"]["q1_variance"] = evaluate_q1_variance(submission, answer_key)
    results["sections"]["q1_top_overbudget_categories"] = evaluate_top_overbudget(submission, answer_key)
    results["sections"]["june_forecast"] = evaluate_june_forecast(submission, answer_key)
    results["sections"]["projected_yearend_variance"] = evaluate_yearend_variance(submission, answer_key)
    results["sections"]["categories_exceeding_budget"] = evaluate_exceeding_budget(submission, answer_key)
    results["sections"]["best_budget_adherence_department"] = evaluate_best_adherence(submission, answer_key)
    results["sections"]["q1_average_monthly_expenditure"] = evaluate_avg_expenditure(submission, answer_key)
    results["sections"]["unusual_monthly_fluctuations"] = evaluate_monthly_fluctuations(submission, answer_key)
    
    # Calculate total score
    total_score = sum(section["score"] for section in results["sections"].values())
    results["total_score"] = total_score
    results["overall_score"] = round((total_score / results["max_possible_score"]) * 100, 1)
    
    # Check for passing criteria
    results["passed"] = results["overall_score"] >= 80
    
    # Check critical competencies
    critical_sections = ["q1_variance", "q1_top_overbudget_categories", 
                         "june_forecast", "best_budget_adherence_department"]
    
    critical_passed = True
    for section in critical_sections:
        if results["sections"][section]["accuracy"] < 70:  # Must get at least 70% in critical sections
            critical_passed = False
            results["critical_failure"] = f"Failed critical section: {section}"
            break
    
    # Check minimum section requirements
    if results["sections"]["q1_variance"]["accuracy"] < 85:
        results["passed"] = False
        results["section_failure"] = "Q1 variance calculations below 85% accuracy requirement"
    
    if results["sections"]["june_forecast"]["accuracy"] < 75:
        results["passed"] = False
        results["section_failure"] = "June forecasts below 75% accuracy requirement"
    
    if results["sections"]["unusual_monthly_fluctuations"]["accuracy"] < 70:  # Approximation for 5/7 correct
        results["passed"] = False
        results["section_failure"] = "Unusual monthly fluctuations below minimum requirement"
    
    if not critical_passed:
        results["passed"] = False
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()