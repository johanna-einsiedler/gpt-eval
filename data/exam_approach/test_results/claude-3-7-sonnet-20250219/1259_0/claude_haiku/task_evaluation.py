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

def evaluate_submission(submission, answer_key):
    results = {
        "overall_score": 0,
        "points_earned": 0,
        "total_possible_points": 16,
        "passed": False,
        "sections": {},
        "critical_calculations": {},
        "categorical_scores": {},
        "disqualification": None
    }
    
    # Track missing fields
    missing_fields = []
    
    # Evaluate income growth analysis
    results["sections"]["income_growth_analysis"] = {}
    section = results["sections"]["income_growth_analysis"]
    
    # CAGR Revenue (critical calculation)
    if "cagr_revenue" in submission["income_growth_analysis"]:
        sub_val = submission["income_growth_analysis"]["cagr_revenue"]
        key_val = answer_key["income_growth_analysis"]["cagr_revenue"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.03:  # Within 3%
            section["cagr_revenue"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["cagr_revenue"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["cagr_revenue"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
        
        results["critical_calculations"]["cagr_revenue"] = percent_diff <= 0.03
    else:
        section["cagr_revenue"] = {"status": "missing", "points": 0}
        missing_fields.append("cagr_revenue")
    
    # CAGR Net Income
    if "cagr_net_income" in submission["income_growth_analysis"]:
        sub_val = submission["income_growth_analysis"]["cagr_net_income"]
        key_val = answer_key["income_growth_analysis"]["cagr_net_income"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["cagr_net_income"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["cagr_net_income"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["cagr_net_income"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["cagr_net_income"] = {"status": "missing", "points": 0}
        missing_fields.append("cagr_net_income")
    
    # Revenue Growth Consistency Score (categorical)
    if "revenue_growth_consistency_score" in submission["income_growth_analysis"]:
        sub_val = submission["income_growth_analysis"]["revenue_growth_consistency_score"]
        key_val = answer_key["income_growth_analysis"]["revenue_growth_consistency_score"]
        
        if sub_val == key_val:
            section["revenue_growth_consistency_score"] = {"status": "correct", "points": 2, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 2
        else:
            section["revenue_growth_consistency_score"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
        
        results["categorical_scores"]["revenue_growth_consistency_score"] = sub_val == key_val
    else:
        section["revenue_growth_consistency_score"] = {"status": "missing", "points": 0}
        missing_fields.append("revenue_growth_consistency_score")
    
    # Evaluate management quality
    results["sections"]["management_quality"] = {}
    section = results["sections"]["management_quality"]
    
    # Executive Turnover Rate
    if "executive_turnover_rate" in submission["management_quality"]:
        sub_val = submission["management_quality"]["executive_turnover_rate"]
        key_val = answer_key["management_quality"]["executive_turnover_rate"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["executive_turnover_rate"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["executive_turnover_rate"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["executive_turnover_rate"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["executive_turnover_rate"] = {"status": "missing", "points": 0}
        missing_fields.append("executive_turnover_rate")
    
    # Compensation to Revenue Ratio
    if "compensation_to_revenue_ratio" in submission["management_quality"]:
        sub_val = submission["management_quality"]["compensation_to_revenue_ratio"]
        key_val = answer_key["management_quality"]["compensation_to_revenue_ratio"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["compensation_to_revenue_ratio"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["compensation_to_revenue_ratio"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["compensation_to_revenue_ratio"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["compensation_to_revenue_ratio"] = {"status": "missing", "points": 0}
        missing_fields.append("compensation_to_revenue_ratio")
    
    # ROI Score (categorical)
    if "roi_score" in submission["management_quality"]:
        sub_val = submission["management_quality"]["roi_score"]
        key_val = answer_key["management_quality"]["roi_score"]
        
        if sub_val == key_val:
            section["roi_score"] = {"status": "correct", "points": 2, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 2
        else:
            section["roi_score"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
        
        results["categorical_scores"]["roi_score"] = sub_val == key_val
    else:
        section["roi_score"] = {"status": "missing", "points": 0}
        missing_fields.append("roi_score")
    
    # Evaluate market position
    results["sections"]["market_position"] = {}
    section = results["sections"]["market_position"]
    
    # Market Share Percentage
    if "market_share_percentage" in submission["market_position"]:
        sub_val = submission["market_position"]["market_share_percentage"]
        key_val = answer_key["market_position"]["market_share_percentage"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["market_share_percentage"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["market_share_percentage"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["market_share_percentage"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["market_share_percentage"] = {"status": "missing", "points": 0}
        missing_fields.append("market_share_percentage")
    
    # Market Share Trend (categorical)
    if "market_share_trend" in submission["market_position"]:
        sub_val = submission["market_position"]["market_share_trend"]
        key_val = answer_key["market_position"]["market_share_trend"]
        
        if sub_val == key_val:
            section["market_share_trend"] = {"status": "correct", "points": 2, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 2
        else:
            section["market_share_trend"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
        
        results["categorical_scores"]["market_share_trend"] = sub_val == key_val
    else:
        section["market_share_trend"] = {"status": "missing", "points": 0}
        missing_fields.append("market_share_trend")
    
    # Competitive Position Score
    if "competitive_position_score" in submission["market_position"]:
        sub_val = submission["market_position"]["competitive_position_score"]
        key_val = answer_key["market_position"]["competitive_position_score"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["competitive_position_score"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["competitive_position_score"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["competitive_position_score"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["competitive_position_score"] = {"status": "missing", "points": 0}
        missing_fields.append("competitive_position_score")
    
    # Evaluate loan profitability
    results["sections"]["loan_profitability"] = {}
    section = results["sections"]["loan_profitability"]
    
    # Debt Service Coverage Ratio (critical calculation)
    dscr_disqualify = False
    if "debt_service_coverage_ratio" in submission["loan_profitability"]:
        sub_val = submission["loan_profitability"]["debt_service_coverage_ratio"]
        key_val = answer_key["loan_profitability"]["debt_service_coverage_ratio"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.03:  # Within 3%
            section["debt_service_coverage_ratio"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["debt_service_coverage_ratio"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["debt_service_coverage_ratio"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
            dscr_disqualify = True
        
        results["critical_calculations"]["debt_service_coverage_ratio"] = percent_diff <= 0.03
    else:
        section["debt_service_coverage_ratio"] = {"status": "missing", "points": 0}
        missing_fields.append("debt_service_coverage_ratio")
        dscr_disqualify = True
    
    # Interest Coverage Ratio
    if "interest_coverage_ratio" in submission["loan_profitability"]:
        sub_val = submission["loan_profitability"]["interest_coverage_ratio"]
        key_val = answer_key["loan_profitability"]["interest_coverage_ratio"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.05:  # Within 5%
            section["interest_coverage_ratio"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["interest_coverage_ratio"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["interest_coverage_ratio"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
    else:
        section["interest_coverage_ratio"] = {"status": "missing", "points": 0}
        missing_fields.append("interest_coverage_ratio")
    
    # Probability of Default (critical calculation)
    pod_disqualify = False
    if "probability_of_default" in submission["loan_profitability"]:
        sub_val = submission["loan_profitability"]["probability_of_default"]
        key_val = answer_key["loan_profitability"]["probability_of_default"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.03:  # Within 3%
            section["probability_of_default"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["probability_of_default"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["probability_of_default"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
            pod_disqualify = True
        
        results["critical_calculations"]["probability_of_default"] = percent_diff <= 0.03
    else:
        section["probability_of_default"] = {"status": "missing", "points": 0}
        missing_fields.append("probability_of_default")
        pod_disqualify = True
    
    # Expected Loan Profitability Score (critical calculation)
    if "expected_loan_profitability_score" in submission["loan_profitability"]:
        sub_val = submission["loan_profitability"]["expected_loan_profitability_score"]
        key_val = answer_key["loan_profitability"]["expected_loan_profitability_score"]
        percent_diff = abs((sub_val - key_val) / key_val)
        
        if percent_diff <= 0.03:  # Within 3%
            section["expected_loan_profitability_score"] = {"status": "correct", "points": 1, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 1
        elif percent_diff <= 0.10:  # Within 10%
            section["expected_loan_profitability_score"] = {"status": "partial", "points": 0.5, "submitted": sub_val, "expected": key_val}
            results["points_earned"] += 0.5
        else:
            section["expected_loan_profitability_score"] = {"status": "incorrect", "points": 0, "submitted": sub_val, "expected": key_val}
        
        results["critical_calculations"]["expected_loan_profitability_score"] = percent_diff <= 0.03
    else:
        section["expected_loan_profitability_score"] = {"status": "missing", "points": 0}
        missing_fields.append("expected_loan_profitability_score")
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["points_earned"] / results["total_possible_points"]) * 100
    
    # Check for disqualification conditions
    if len(missing_fields) > 3:
        results["disqualification"] = "Missing more than 3 required fields"
    elif dscr_disqualify:
        results["disqualification"] = "Incorrect calculation of Debt Service Coverage Ratio by more than ±10%"
    elif pod_disqualify:
        results["disqualification"] = "Incorrect calculation of Probability of Default by more than ±10%"
    
    # Check if passed
    all_critical_correct = all(results["critical_calculations"].values())
    all_categorical_correct = all(results["categorical_scores"].values())
    score_sufficient = results["overall_score"] >= 81
    
    results["passed"] = all_critical_correct and all_categorical_correct and score_sufficient and not results["disqualification"]
    
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
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()