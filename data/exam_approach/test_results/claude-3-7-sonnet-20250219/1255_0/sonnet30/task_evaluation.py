#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_ratio_calculations(submission, answer_key, tolerance=0.01):
    """Evaluate the ratio calculations in the submission."""
    results = {
        "liquidity_ratios": {},
        "solvency_ratios": {},
        "profitability_ratios": {},
        "efficiency_ratios": {}
    }
    
    total_correct = 0
    total_ratios = 0
    
    # Check each ratio category
    for category in results.keys():
        results[category] = {}
        
        # Check each ratio type within the category
        for ratio_type in answer_key["task1_ratios"][category].keys():
            results[category][ratio_type] = {}
            
            # Check each year's calculation
            for year in ["2020", "2021", "2022"]:
                submission_value = submission["task1_ratios"][category][ratio_type][year]
                answer_value = answer_key["task1_ratios"][category][ratio_type][year]
                
                # Check if the calculation is correct within tolerance
                is_correct = abs(submission_value - answer_value) <= tolerance
                
                results[category][ratio_type][year] = {
                    "submission_value": submission_value,
                    "correct_value": answer_value,
                    "is_correct": is_correct
                }
                
                if is_correct:
                    total_correct += 1
                total_ratios += 1
    
    # Calculate points for ratio calculations (1.5 points per correct calculation)
    ratio_points = total_correct * 1.5
    
    # Check if numerical values are properly formatted (rounded to 2 decimal places)
    formatting_correct = True
    for category in submission["task1_ratios"].keys():
        for ratio_type in submission["task1_ratios"][category].keys():
            for year in submission["task1_ratios"][category][ratio_type].keys():
                value = submission["task1_ratios"][category][ratio_type][year]
                # Check if the value is rounded to 2 decimal places
                if abs(value - round(value, 2)) > 1e-10:
                    formatting_correct = False
                    break
    
    # Award 1.5 points for proper formatting
    formatting_points = 1.5 if formatting_correct else 0
    
    return {
        "detailed_results": results,
        "total_correct": total_correct,
        "total_ratios": total_ratios,
        "ratio_points": ratio_points,
        "formatting_points": formatting_points,
        "total_points": ratio_points + formatting_points
    }

def evaluate_trend_analysis(submission, answer_key):
    """Evaluate the trend analysis in the submission."""
    results = {}
    total_correct = 0
    
    for trend_type in answer_key["task2_analysis"]["trend_analysis"].keys():
        submission_trend = submission["task2_analysis"]["trend_analysis"][trend_type]
        correct_trend = answer_key["task2_analysis"]["trend_analysis"][trend_type]
        
        is_correct = submission_trend == correct_trend
        
        results[trend_type] = {
            "submission_value": submission_trend,
            "correct_value": correct_trend,
            "is_correct": is_correct
        }
        
        if is_correct:
            total_correct += 1
    
    # Calculate points for trend analysis (7.5 points per correct trend)
    trend_points = total_correct * 7.5
    
    return {
        "detailed_results": results,
        "total_correct": total_correct,
        "total_trends": len(results),
        "trend_points": trend_points
    }

def evaluate_credit_risk(submission, answer_key):
    """Evaluate the credit risk assessment in the submission."""
    submission_risk = submission["task2_analysis"]["credit_risk_assessment"]
    correct_risk = answer_key["task2_analysis"]["credit_risk_assessment"]
    
    is_correct = submission_risk == correct_risk
    
    # Calculate points for credit risk assessment (10 points if correct)
    risk_points = 10 if is_correct else 0
    
    return {
        "submission_value": submission_risk,
        "correct_value": correct_risk,
        "is_correct": is_correct,
        "risk_points": risk_points
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    # Evaluate ratio calculations (Task 1)
    ratio_results = evaluate_ratio_calculations(submission, answer_key)
    
    # Evaluate trend analysis (Task 2 - Part 1)
    trend_results = evaluate_trend_analysis(submission, answer_key)
    
    # Evaluate credit risk assessment (Task 2 - Part 2)
    risk_results = evaluate_credit_risk(submission, answer_key)
    
    # Calculate total score
    total_points = ratio_results["total_points"] + trend_results["trend_points"] + risk_results["risk_points"]
    max_points = 60 + 30 + 10  # 60 for ratios, 30 for trends, 10 for risk assessment
    overall_score = (total_points / max_points) * 100
    
    # Check for automatic disqualification conditions
    missing_ratios = ratio_results["total_ratios"] - ratio_results["total_correct"]
    is_disqualified = missing_ratios > 5
    
    # Determine if the candidate passed
    passed = total_points >= 70 and not is_disqualified
    
    return {
        "candidate_name": submission.get("candidate_name", "Unknown"),
        "task1_results": ratio_results,
        "task2_trend_results": trend_results,
        "task2_risk_results": risk_results,
        "total_points": total_points,
        "max_points": max_points,
        "overall_score": round(overall_score, 2),
        "is_disqualified": is_disqualified,
        "passed": passed
    }

def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results to a JSON file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Pass/Fail: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()