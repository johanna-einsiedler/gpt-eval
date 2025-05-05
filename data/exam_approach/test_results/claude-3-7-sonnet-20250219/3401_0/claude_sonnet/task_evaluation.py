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

def evaluate_trends(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the identified trends section."""
    max_score = 30
    score = 0
    feedback = {}
    
    # Create dictionaries for easier lookup
    key_trends = {trend["trend_id"]: trend for trend in answer_key["identified_trends"]}
    sub_trends = {trend["trend_id"]: trend for trend in submission.get("identified_trends", [])}
    
    # Check if trends were identified
    if not sub_trends:
        return 0, {"feedback": "No trends identified."}
    
    # Evaluate each trend
    for trend_id, key_trend in key_trends.items():
        trend_feedback = {}
        trend_score = 0
        max_trend_score = max_score / len(key_trends)
        
        if trend_id in sub_trends:
            sub_trend = sub_trends[trend_id]
            
            # Check affected departments (2 points)
            dept_score = 0
            key_depts = set(key_trend["affected_departments"])
            sub_depts = set(sub_trend.get("affected_departments", []))
            if key_depts == sub_depts:
                dept_score = 2
            elif len(key_depts.intersection(sub_depts)) > 0:
                dept_score = 1
            trend_score += dept_score
            trend_feedback["departments"] = f"Score: {dept_score}/2"
            
            # Check affected categories (2 points)
            cat_score = 0
            key_cats = set(key_trend["affected_categories"])
            sub_cats = set(sub_trend.get("affected_categories", []))
            if key_cats == sub_cats:
                cat_score = 2
            elif len(key_cats.intersection(sub_cats)) > 0:
                cat_score = 1
            trend_score += cat_score
            trend_feedback["categories"] = f"Score: {cat_score}/2"
            
            # Check percentage change (3 points)
            pct_score = 0
            key_pct = key_trend["percentage_change_first_to_last"]
            sub_pct = sub_trend.get("percentage_change_first_to_last", 0)
            if abs(key_pct - sub_pct) <= 2:
                pct_score = 3
            elif abs(key_pct - sub_pct) <= 5:
                pct_score = 2
            elif abs(key_pct - sub_pct) <= 10:
                pct_score = 1
            trend_score += pct_score
            trend_feedback["percentage_change"] = f"Score: {pct_score}/3 (Expected: {key_pct}, Got: {sub_pct})"
            
            # Check growth rate (3 points)
            growth_score = 0
            key_growth = key_trend["average_quarterly_growth_rate"]
            sub_growth = sub_trend.get("average_quarterly_growth_rate", 0)
            if abs(key_growth - sub_growth) <= 0.5:
                growth_score = 3
            elif abs(key_growth - sub_growth) <= 1:
                growth_score = 2
            elif abs(key_growth - sub_growth) <= 2:
                growth_score = 1
            trend_score += growth_score
            trend_feedback["growth_rate"] = f"Score: {growth_score}/3 (Expected: {key_growth}, Got: {sub_growth})"
            
            # Check trend description and supporting data (max 2 points)
            desc_score = 0
            if sub_trend.get("trend_description") and len(sub_trend.get("trend_description", "")) >= 50:
                desc_score += 1
            if sub_trend.get("supporting_data_points") and len(sub_trend.get("supporting_data_points", "")) >= 50:
                desc_score += 1
            trend_score += desc_score
            trend_feedback["description"] = f"Score: {desc_score}/2"
            
            # Calculate percentage of max trend score
            trend_percentage = (trend_score / max_trend_score) * 100
            trend_feedback["trend_score"] = f"{trend_score}/{max_trend_score} ({trend_percentage:.2f}%)"
            score += trend_score
        else:
            trend_feedback["feedback"] = "Trend not identified."
        
        feedback[f"Trend {trend_id}"] = trend_feedback
    
    # Calculate overall percentage for trends section
    percentage = (score / max_score) * 100
    feedback["overall"] = f"{score}/{max_score} ({percentage:.2f}%)"
    
    return score, feedback

def evaluate_variances(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the variance analysis section."""
    max_score = 25
    score = 0
    feedback = {}
    
    # Create dictionaries for easier lookup
    key_variances = {var["variance_id"]: var for var in answer_key["variance_analysis"]}
    sub_variances = {var["variance_id"]: var for var in submission.get("variance_analysis", [])}
    
    # Check if variances were identified
    if not sub_variances:
        return 0, {"feedback": "No variances identified."}
    
    # Evaluate each variance
    for var_id, key_var in key_variances.items():
        var_feedback = {}
        var_score = 0
        max_var_score = max_score / len(key_variances)
        
        if var_id in sub_variances:
            sub_var = sub_variances[var_id]
            
            # Check quarter, department, category identification (3 points)
            id_score = 0
            if sub_var.get("quarter") == key_var["quarter"]:
                id_score += 1
            if sub_var.get("department") == key_var["department"]:
                id_score += 1
            if sub_var.get("category") == key_var["category"]:
                id_score += 1
            var_score += id_score
            var_feedback["identification"] = f"Score: {id_score}/3"
            
            # Check variance amount calculation (3 points)
            amount_score = 0
            key_amount = key_var["variance_amount"]
            sub_amount = sub_var.get("variance_amount", 0)
            if abs(key_amount - sub_amount) <= 100:
                amount_score = 3
            elif abs(key_amount - sub_amount) <= 500:
                amount_score = 2
            elif abs(key_amount - sub_amount) <= 1000:
                amount_score = 1
            var_score += amount_score
            var_feedback["variance_amount"] = f"Score: {amount_score}/3 (Expected: {key_amount}, Got: {sub_amount})"
            
            # Check variance percentage calculation (2 points)
            pct_score = 0
            key_pct = key_var["variance_percentage"]
            sub_pct = sub_var.get("variance_percentage", 0)
            if abs(key_pct - sub_pct) <= 1:
                pct_score = 2
            elif abs(key_pct - sub_pct) <= 3:
                pct_score = 1
            var_score += pct_score
            var_feedback["variance_percentage"] = f"Score: {pct_score}/2 (Expected: {key_pct}, Got: {sub_pct})"
            
            # Check primary cause explanation (max 2 points)
            cause_score = 0
            if sub_var.get("primary_cause"):
                cause_length = len(sub_var.get("primary_cause", ""))
                if cause_length >= 25:
                    cause_score += 1
                if cause_length >= 50:
                    cause_score += 1
            var_score += cause_score
            var_feedback["primary_cause"] = f"Score: {cause_score}/2"
            
            # Calculate percentage of max variance score
            var_percentage = (var_score / max_var_score) * 100
            var_feedback["variance_score"] = f"{var_score}/{max_var_score} ({var_percentage:.2f}%)"
            score += var_score
        else:
            var_feedback["feedback"] = "Variance not identified."
        
        feedback[f"Variance {var_id}"] = var_feedback
    
    # Calculate overall percentage for variances section
    percentage = (score / max_score) * 100
    feedback["overall"] = f"{score}/{max_score} ({percentage:.2f}%)"
    
    return score, feedback

def evaluate_forecasts(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the forecasted expenses section."""
    max_score = 25
    score = 0
    feedback = {}
    
    # Check if forecasts were provided
    if "forecasted_expenses" not in submission:
        return 0, {"feedback": "No forecasts provided."}
    
    sub_forecasts = submission["forecasted_expenses"]
    key_forecasts = answer_key["forecasted_expenses"]
    
    # Count total number of forecast values for scoring
    total_forecasts = 0
    for quarter in key_forecasts:
        for dept in key_forecasts[quarter]:
            total_forecasts += len(key_forecasts[quarter][dept])
    
    points_per_forecast = max_score / total_forecasts
    
    # Evaluate each forecast
    for quarter in key_forecasts:
        quarter_feedback = {}
        
        if quarter in sub_forecasts:
            for dept in key_forecasts[quarter]:
                dept_feedback = {}
                
                if dept in sub_forecasts[quarter]:
                    for category, key_value in key_forecasts[quarter][dept].items():
                        if category in sub_forecasts[quarter][dept]:
                            sub_value = sub_forecasts[quarter][dept][category]
                            
                            # Calculate percentage difference
                            if key_value != 0:
                                pct_diff = abs((sub_value - key_value) / key_value) * 100
                            else:
                                pct_diff = 100 if sub_value != 0 else 0
                            
                            # Score based on accuracy
                            cat_score = 0
                            if pct_diff <= 5:
                                cat_score = points_per_forecast
                            elif pct_diff <= 10:
                                cat_score = points_per_forecast * 0.75
                            elif pct_diff <= 15:
                                cat_score = points_per_forecast * 0.5
                            elif pct_diff <= 20:
                                cat_score = points_per_forecast * 0.25
                            
                            score += cat_score
                            dept_feedback[category] = f"Score: {cat_score:.2f}/{points_per_forecast:.2f} (Expected: {key_value}, Got: {sub_value}, Diff: {pct_diff:.2f}%)"
                        else:
                            dept_feedback[category] = f"Missing forecast"
                    
                    quarter_feedback[dept] = dept_feedback
                else:
                    quarter_feedback[dept] = "Department forecasts missing"
            
            feedback[quarter] = quarter_feedback
        else:
            feedback[quarter] = "Quarter forecasts missing"
    
    # Calculate overall percentage for forecasts section
    percentage = (score / max_score) * 100
    feedback["overall"] = f"{score:.2f}/{max_score} ({percentage:.2f}%)"
    
    return score, feedback

def evaluate_cost_reduction(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the cost reduction targets section."""
    max_score = 20
    score = 0
    feedback = {}
    
    # Create dictionaries for easier lookup
    key_targets = {target["target_id"]: target for target in answer_key["cost_reduction_targets"]}
    sub_targets = {target["target_id"]: target for target in submission.get("cost_reduction_targets", [])}
    
    # Check if targets were identified
    if not sub_targets:
        return 0, {"feedback": "No cost reduction targets identified."}
    
    # Evaluate each target
    for target_id, key_target in key_targets.items():
        target_feedback = {}
        target_score = 0
        max_target_score = max_score / len(key_targets)
        
        if target_id in sub_targets:
            sub_target = sub_targets[target_id]
            
            # Check department and category identification (2 points)
            id_score = 0
            if sub_target.get("department") == key_target["department"]:
                id_score += 1
            if sub_target.get("category") == key_target["category"]:
                id_score += 1
            target_score += id_score
            target_feedback["identification"] = f"Score: {id_score}/2"
            
            # Check current expense accuracy (2 points)
            expense_score = 0
            key_expense = key_target["current_quarterly_expense"]
            sub_expense = sub_target.get("current_quarterly_expense", 0)
            if abs(key_expense - sub_expense) <= 1000:
                expense_score = 2
            elif abs(key_expense - sub_expense) <= 5000:
                expense_score = 1
            target_score += expense_score
            target_feedback["current_expense"] = f"Score: {expense_score}/2 (Expected: {key_expense}, Got: {sub_expense})"
            
            # Check savings percentage reasonableness (2 points)
            savings_score = 0
            key_pct = key_target["potential_savings_percentage"]
            sub_pct = sub_target.get("potential_savings_percentage", 0)
            
            # Special case for HR Training where 0% is expected
            if key_target["department"] == "HR" and key_target["category"] == "Training":
                if sub_pct <= 5:  # Allow small percentage as reasonable
                    savings_score = 2
                elif sub_pct <= 10:
                    savings_score = 1
            else:
                if abs(key_pct - sub_pct) <= 3:
                    savings_score = 2
                elif abs(key_pct - sub_pct) <= 7:
                    savings_score = 1
            
            target_score += savings_score
            target_feedback["savings_percentage"] = f"Score: {savings_score}/2 (Expected: {key_pct}, Got: {sub_pct})"
            
            # Check justification (max 2 points)
            just_score = 0
            if sub_target.get("justification"):
                just_length = len(sub_target.get("justification", ""))
                if just_length >= 50:
                    just_score += 1
                if just_length >= 100:
                    just_score += 1
            target_score += just_score
            target_feedback["justification"] = f"Score: {just_score}/2"
            
            # Calculate percentage of max target score
            target_percentage = (target_score / max_target_score) * 100
            target_feedback["target_score"] = f"{target_score}/{max_target_score} ({target_percentage:.2f}%)"
            score += target_score
        else:
            target_feedback["feedback"] = "Target not identified."
        
        feedback[f"Target {target_id}"] = target_feedback
    
    # Calculate overall percentage for cost reduction section
    percentage = (score / max_score) * 100
    feedback["overall"] = f"{score}/{max_score} ({percentage:.2f}%)"
    
    return score, feedback

def calculate_overall_score(section_scores: Dict[str, float], max_scores: Dict[str, float]) -> float:
    """Calculate the overall score as a percentage."""
    total_score = sum(section_scores.values())
    total_max = sum(max_scores.values())
    return (total_score / total_max) * 100 if total_max > 0 else 0

def evaluate_submission(submission_file: str, answer_key_file: str) -> Dict:
    """Evaluate a candidate's submission against the answer key."""
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Define maximum scores for each section
    max_scores = {
        "trends": 30,
        "variances": 25,
        "forecasts": 25,
        "cost_reduction": 20
    }
    
    # Evaluate each section
    trends_score, trends_feedback = evaluate_trends(submission, answer_key)
    variances_score, variances_feedback = evaluate_variances(submission, answer_key)
    forecasts_score, forecasts_feedback = evaluate_forecasts(submission, answer_key)
    cost_reduction_score, cost_reduction_feedback = evaluate_cost_reduction(submission, answer_key)
    
    # Calculate section scores as percentages
    section_scores = {
        "trends": trends_score,
        "variances": variances_score,
        "forecasts": forecasts_score,
        "cost_reduction": cost_reduction_score
    }
    
    section_percentages = {
        "trends": (trends_score / max_scores["trends"]) * 100,
        "variances": (variances_score / max_scores["variances"]) * 100,
        "forecasts": (forecasts_score / max_scores["forecasts"]) * 100,
        "cost_reduction": (cost_reduction_score / max_scores["cost_reduction"]) * 100
    }
    
    # Calculate overall score
    overall_score = calculate_overall_score(section_scores, max_scores)
    
    # Determine if the candidate passed
    passed = overall_score >= 60 and all(pct >= 30 for pct in section_percentages.values())
    
    # Prepare results
    results = {
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "section_scores": {
            "trends": {
                "score": round(trends_score, 2),
                "percentage": round(section_percentages["trends"], 2),
                "max_score": max_scores["trends"],
                "feedback": trends_feedback
            },
            "variances": {
                "score": round(variances_score, 2),
                "percentage": round(section_percentages["variances"], 2),
                "max_score": max_scores["variances"],
                "feedback": variances_feedback
            },
            "forecasts": {
                "score": round(forecasts_score, 2),
                "percentage": round(section_percentages["forecasts"], 2),
                "max_score": max_scores["forecasts"],
                "feedback": forecasts_feedback
            },
            "cost_reduction": {
                "score": round(cost_reduction_score, 2),
                "percentage": round(section_percentages["cost_reduction"], 2),
                "max_score": max_scores["cost_reduction"],
                "feedback": cost_reduction_feedback
            }
        }
    }
    
    return results

def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()