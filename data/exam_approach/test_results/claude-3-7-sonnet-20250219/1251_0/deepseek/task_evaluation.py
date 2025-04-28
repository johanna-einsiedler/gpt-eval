#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_financial_ratios(submission, answer_key, tolerance=0.05):
    correct_ratios = 0
    ratio_results = {}
    
    for ratio_name, ratio_data in answer_key["financial_ratios"].items():
        if ratio_name not in submission["financial_ratios"]:
            ratio_results[ratio_name] = {
                "correct": False,
                "reason": "Missing ratio"
            }
            continue
            
        years_correct = 0
        year_results = {}
        
        for year in ["year1", "year2", "year3"]:
            if year not in submission["financial_ratios"][ratio_name]:
                year_results[year] = {
                    "correct": False,
                    "expected": ratio_data[year],
                    "submitted": None,
                    "reason": "Missing year data"
                }
                continue
                
            expected = ratio_data[year]
            submitted = submission["financial_ratios"][ratio_name][year]
            
            # Check if the values are within tolerance
            if isinstance(submitted, (int, float)) and abs(submitted - expected) <= tolerance:
                years_correct += 1
                year_results[year] = {
                    "correct": True,
                    "expected": expected,
                    "submitted": submitted
                }
            else:
                year_results[year] = {
                    "correct": False,
                    "expected": expected,
                    "submitted": submitted,
                    "reason": "Value outside tolerance range"
                }
        
        # A ratio is correct only if all three years are correct
        ratio_correct = years_correct == 3
        if ratio_correct:
            correct_ratios += 1
            
        ratio_results[ratio_name] = {
            "correct": ratio_correct,
            "years": year_results
        }
    
    score = (correct_ratios / 10) * 50  # 50% of total score
    
    return {
        "score": score,
        "max_score": 50,
        "correct_ratios": correct_ratios,
        "details": ratio_results
    }

def evaluate_industry_comparison(submission, answer_key):
    expected_deviations = set(answer_key["industry_comparison"]["significant_deviations"])
    
    if "industry_comparison" not in submission or "significant_deviations" not in submission["industry_comparison"]:
        return {
            "score": 0,
            "max_score": 10,
            "correct_deviations": 0,
            "expected_deviations": list(expected_deviations),
            "submitted_deviations": [],
            "reason": "Missing industry_comparison or significant_deviations"
        }
    
    submitted_deviations = set(submission["industry_comparison"]["significant_deviations"])
    
    # Count correct deviations (those that appear in both sets)
    correct_deviations = len(expected_deviations.intersection(submitted_deviations))
    
    # Need at least 4 of 6 correct deviations for full points
    score = min(correct_deviations, 4) / 4 * 10  # 10% of total score
    
    return {
        "score": score,
        "max_score": 10,
        "correct_deviations": correct_deviations,
        "expected_deviations": list(expected_deviations),
        "submitted_deviations": list(submitted_deviations)
    }

def evaluate_risk_factors(submission, answer_key):
    expected_factors = set(answer_key["top_risk_factors"])
    
    if "top_risk_factors" not in submission:
        return {
            "score": 0,
            "max_score": 15,
            "correct_factors": 0,
            "expected_factors": list(expected_factors),
            "submitted_factors": [],
            "reason": "Missing top_risk_factors"
        }
    
    submitted_factors = set(submission["top_risk_factors"])
    
    # Count correct factors (those that appear in both sets)
    correct_factors = len(expected_factors.intersection(submitted_factors))
    
    # Need at least 2 of 3 correct factors for full points
    score = min(correct_factors, 2) / 2 * 15  # 15% of total score
    
    return {
        "score": score,
        "max_score": 15,
        "correct_factors": correct_factors,
        "expected_factors": list(expected_factors),
        "submitted_factors": list(submitted_factors)
    }

def evaluate_dscr(submission, answer_key, tolerance=0.10):
    expected_dscr = answer_key["debt_service_coverage_ratio"]
    
    if "debt_service_coverage_ratio" not in submission:
        return {
            "score": 0,
            "max_score": 10,
            "correct": False,
            "expected": expected_dscr,
            "submitted": None,
            "reason": "Missing debt_service_coverage_ratio"
        }
    
    submitted_dscr = submission["debt_service_coverage_ratio"]
    
    # Check if DSCR is within tolerance
    if isinstance(submitted_dscr, (int, float)) and abs(submitted_dscr - expected_dscr) <= tolerance:
        return {
            "score": 10,  # 10% of total score
            "max_score": 10,
            "correct": True,
            "expected": expected_dscr,
            "submitted": submitted_dscr
        }
    else:
        return {
            "score": 0,
            "max_score": 10,
            "correct": False,
            "expected": expected_dscr,
            "submitted": submitted_dscr,
            "reason": "Value outside tolerance range"
        }

def evaluate_risk_rating_recommendation(submission, answer_key):
    expected_rating = answer_key["risk_rating"]
    expected_recommendation = answer_key["recommendation"]
    
    rating_missing = "risk_rating" not in submission
    recommendation_missing = "recommendation" not in submission
    
    if rating_missing and recommendation_missing:
        return {
            "score": 0,
            "max_score": 15,
            "rating_correct": False,
            "recommendation_correct": False,
            "expected_rating": expected_rating,
            "submitted_rating": None,
            "expected_recommendation": expected_recommendation,
            "submitted_recommendation": None,
            "reason": "Missing risk_rating and recommendation"
        }
    
    submitted_rating = submission.get("risk_rating")
    submitted_recommendation = submission.get("recommendation")
    
    # Check if rating is correct (must be 4 or 5)
    rating_correct = submitted_rating in [4, 5]
    
    # Check if recommendation is correct (must be "Decline")
    recommendation_correct = submitted_recommendation == "Decline"
    
    # Both must be correct for full points
    if rating_correct and recommendation_correct:
        score = 15  # 15% of total score
    elif rating_correct or recommendation_correct:
        score = 7.5  # Half points if only one is correct
    else:
        score = 0
    
    return {
        "score": score,
        "max_score": 15,
        "rating_correct": rating_correct,
        "recommendation_correct": recommendation_correct,
        "expected_rating": expected_rating,
        "submitted_rating": submitted_rating,
        "expected_recommendation": expected_recommendation,
        "submitted_recommendation": submitted_recommendation
    }

def evaluate_submission(submission, answer_key):
    results = {
        "financial_ratios": evaluate_financial_ratios(submission, answer_key),
        "industry_comparison": evaluate_industry_comparison(submission, answer_key),
        "risk_factors": evaluate_risk_factors(submission, answer_key),
        "debt_service_coverage_ratio": evaluate_dscr(submission, answer_key),
        "risk_rating_recommendation": evaluate_risk_rating_recommendation(submission, answer_key)
    }
    
    # Calculate overall score
    total_score = sum(section["score"] for section in results.values())
    max_score = sum(section["max_score"] for section in results.values())
    overall_score = (total_score / max_score) * 100
    
    # Add overall score to results
    results["overall_score"] = round(overall_score, 2)
    
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
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print("Results saved to test_results.json")

if __name__ == "__main__":
    main()