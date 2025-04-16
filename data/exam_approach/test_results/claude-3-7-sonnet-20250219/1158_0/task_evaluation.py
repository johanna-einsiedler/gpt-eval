import json
import sys

def evaluate_test(submission_file, answer_key_file):
    # Load submission and answer key
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading submission file: {e}")
        sys.exit(1)
    
    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading answer key file: {e}")
        sys.exit(1)
    
    # Initialize result structure
    results = {
        "candidate_id": submission.get("candidateID", "Unknown"),
        "exercise1": {
            "score": 0,
            "possible": 5,
            "details": {}
        },
        "exercise2": {
            "score": 0,
            "possible": 4,
            "details": {}
        },
        "exercise3": {
            "score": 0,
            "possible": 5,  # 4 items plus bonus
            "details": {}
        },
        "critical_elements_passed": True,
        "overall_score": 0
    }
    
    # Evaluate Exercise 1
    evaluate_exercise1(submission, answer_key, results)
    
    # Evaluate Exercise 2
    evaluate_exercise2(submission, answer_key, results)
    
    # Evaluate Exercise 3
    evaluate_exercise3(submission, answer_key, results)
    
    # Check critical elements
    check_critical_elements(results)
    
    # Calculate overall score as percentage
    total_score = results["exercise1"]["score"] + results["exercise2"]["score"] + results["exercise3"]["score"]
    total_possible = results["exercise1"]["possible"] + results["exercise2"]["possible"] + results["exercise3"]["possible"]
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    return results

def evaluate_exercise1(submission, answer_key, results):
    ex1_sub = submission.get("exercise1", {})
    ex1_key = answer_key.get("exercise1", {})
    
    # Price Pattern
    price_pattern = ex1_sub.get("pricePattern")
    if price_pattern == ex1_key.get("pricePattern"):
        results["exercise1"]["score"] += 1
        results["exercise1"]["details"]["pricePattern"] = {"correct": True, "score": 1}
    else:
        results["exercise1"]["details"]["pricePattern"] = {"correct": False, "score": 0, 
                                                         "expected": ex1_key.get("pricePattern"), 
                                                         "submitted": price_pattern}
    
    # Peak Month
    peak_month = ex1_sub.get("peakMonth")
    if peak_month == ex1_key.get("peakMonth"):
        results["exercise1"]["score"] += 1
        results["exercise1"]["details"]["peakMonth"] = {"correct": True, "score": 1}
    else:
        results["exercise1"]["details"]["peakMonth"] = {"correct": False, "score": 0, 
                                                      "expected": ex1_key.get("peakMonth"), 
                                                      "submitted": peak_month}
    
    # Lowest Price
    lowest_price = ex1_sub.get("lowestPrice")
    expected_price = ex1_key.get("lowestPrice")
    
    if lowest_price is not None and expected_price is not None:
        if abs(lowest_price - expected_price) < 0.01:  # Exact match
            results["exercise1"]["score"] += 1
            results["exercise1"]["details"]["lowestPrice"] = {"correct": True, "score": 1}
        elif abs((lowest_price - expected_price) / expected_price) <= 0.05:  # Within 5%
            results["exercise1"]["score"] += 0.5
            results["exercise1"]["details"]["lowestPrice"] = {"correct": "partial", "score": 0.5, 
                                                           "expected": expected_price, 
                                                           "submitted": lowest_price}
        else:
            results["exercise1"]["details"]["lowestPrice"] = {"correct": False, "score": 0, 
                                                           "expected": expected_price, 
                                                           "submitted": lowest_price}
    else:
        results["exercise1"]["details"]["lowestPrice"] = {"correct": False, "score": 0, 
                                                       "expected": expected_price, 
                                                       "submitted": lowest_price}
    
    # Percentage Change
    pct_change = ex1_sub.get("percentageChange")
    expected_pct = ex1_key.get("percentageChange")
    
    if pct_change is not None and expected_pct is not None:
        if abs(pct_change - expected_pct) < 0.1:  # Exact match with small tolerance
            results["exercise1"]["score"] += 1
            results["exercise1"]["details"]["percentageChange"] = {"correct": True, "score": 1}
        elif abs((pct_change - expected_pct) / expected_pct) <= 0.05:  # Within 5%
            results["exercise1"]["score"] += 0.5
            results["exercise1"]["details"]["percentageChange"] = {"correct": "partial", "score": 0.5, 
                                                                "expected": expected_pct, 
                                                                "submitted": pct_change}
        else:
            results["exercise1"]["details"]["percentageChange"] = {"correct": False, "score": 0, 
                                                                "expected": expected_pct, 
                                                                "submitted": pct_change}
    else:
        results["exercise1"]["details"]["percentageChange"] = {"correct": False, "score": 0, 
                                                            "expected": expected_pct, 
                                                            "submitted": pct_change}
    
    # Quarter with Highest Volatility
    quarter = ex1_sub.get("quarterWithHighestVolatility")
    if quarter == ex1_key.get("quarterWithHighestVolatility"):
        results["exercise1"]["score"] += 1
        results["exercise1"]["details"]["quarterWithHighestVolatility"] = {"correct": True, "score": 1}
    else:
        results["exercise1"]["details"]["quarterWithHighestVolatility"] = {"correct": False, "score": 0, 
                                                                         "expected": ex1_key.get("quarterWithHighestVolatility"), 
                                                                         "submitted": quarter}

def evaluate_exercise2(submission, answer_key, results):
    ex2_sub = submission.get("exercise2", {})
    ex2_key = answer_key.get("exercise2", {})
    
    # Impact Score
    impact_score = ex2_sub.get("impactScore")
    expected_score = ex2_key.get("impactScore")
    
    if impact_score == expected_score:
        results["exercise2"]["score"] += 1
        results["exercise2"]["details"]["impactScore"] = {"correct": True, "score": 1}
    else:
        results["exercise2"]["details"]["impactScore"] = {"correct": False, "score": 0, 
                                                        "expected": expected_score, 
                                                        "submitted": impact_score}
    
    # Expected Price Change
    price_change = ex2_sub.get("expectedPriceChange")
    expected_change = ex2_key.get("expectedPriceChange")
    
    if price_change is not None and expected_change is not None:
        if abs(price_change - expected_change) < 0.1:  # Exact match with small tolerance
            results["exercise2"]["score"] += 1
            results["exercise2"]["details"]["expectedPriceChange"] = {"correct": True, "score": 1}
        elif abs((price_change - expected_change) / expected_change) <= 0.05:  # Within 5%
            results["exercise2"]["score"] += 0.5
            results["exercise2"]["details"]["expectedPriceChange"] = {"correct": "partial", "score": 0.5, 
                                                                   "expected": expected_change, 
                                                                   "submitted": price_change}
        else:
            results["exercise2"]["details"]["expectedPriceChange"] = {"correct": False, "score": 0, 
                                                                   "expected": expected_change, 
                                                                   "submitted": price_change}
    else:
        results["exercise2"]["details"]["expectedPriceChange"] = {"correct": False, "score": 0, 
                                                               "expected": expected_change, 
                                                               "submitted": price_change}
    
    # Recommended Action - zero tolerance item
    action = ex2_sub.get("recommendedAction")
    if action == ex2_key.get("recommendedAction"):
        results["exercise2"]["score"] += 1
        results["exercise2"]["details"]["recommendedAction"] = {"correct": True, "score": 1}
    else:
        results["exercise2"]["details"]["recommendedAction"] = {"correct": False, "score": 0, 
                                                              "expected": ex2_key.get("recommendedAction"), 
                                                              "submitted": action}
    
    # Alternate Supplier Code
    supplier = ex2_sub.get("alternateSupplierCode")
    if supplier == ex2_key.get("alternateSupplierCode"):
        results["exercise2"]["score"] += 1
        results["exercise2"]["details"]["alternateSupplierCode"] = {"correct": True, "score": 1}
    else:
        results["exercise2"]["details"]["alternateSupplierCode"] = {"correct": False, "score": 0, 
                                                                  "expected": ex2_key.get("alternateSupplierCode"), 
                                                                  "submitted": supplier}

def evaluate_exercise3(submission, answer_key, results):
    ex3_sub = submission.get("exercise3", {})
    ex3_key = answer_key.get("exercise3", {})
    
    # Contract Recommendation - zero tolerance item
    contract = ex3_sub.get("contractRecommendation")
    if contract == ex3_key.get("contractRecommendation"):
        results["exercise3"]["score"] += 1
        results["exercise3"]["details"]["contractRecommendation"] = {"correct": True, "score": 1}
    elif contract in ["spot", "3month", "6month", "12month"]:  # Valid but not optimal
        results["exercise3"]["details"]["contractRecommendation"] = {"correct": "partial", "score": 0.5, 
                                                                   "expected": ex3_key.get("contractRecommendation"), 
                                                                   "submitted": contract}
        results["exercise3"]["score"] += 0.5
    else:
        results["exercise3"]["details"]["contractRecommendation"] = {"correct": False, "score": 0, 
                                                                   "expected": ex3_key.get("contractRecommendation"), 
                                                                   "submitted": contract}
    
    # Price Target
    price_target = ex3_sub.get("priceTarget")
    expected_target = ex3_key.get("priceTarget")
    
    if price_target is not None and expected_target is not None:
        if abs(price_target - expected_target) < 0.01:  # Exact match
            results["exercise3"]["score"] += 1
            results["exercise3"]["details"]["priceTarget"] = {"correct": True, "score": 1}
        elif abs((price_target - expected_target) / expected_target) <= 0.05:  # Within 5%
            results["exercise3"]["score"] += 0.5
            results["exercise3"]["details"]["priceTarget"] = {"correct": "partial", "score": 0.5, 
                                                           "expected": expected_target, 
                                                           "submitted": price_target}
        else:
            results["exercise3"]["details"]["priceTarget"] = {"correct": False, "score": 0, 
                                                           "expected": expected_target, 
                                                           "submitted": price_target}
    else:
        results["exercise3"]["details"]["priceTarget"] = {"correct": False, "score": 0, 
                                                       "expected": expected_target, 
                                                       "submitted": price_target}
    
    # Potential Savings
    savings = ex3_sub.get("potentialSavings")
    expected_savings = ex3_key.get("potentialSavings")
    
    if savings is not None and expected_savings is not None:
        if abs(savings - expected_savings) < 1:  # Small tolerance for rounding
            results["exercise3"]["score"] += 1
            results["exercise3"]["details"]["potentialSavings"] = {"correct": True, "score": 1}
        elif abs((savings - expected_savings) / expected_savings) <= 0.05:  # Within 5%
            results["exercise3"]["score"] += 0.5
            results["exercise3"]["details"]["potentialSavings"] = {"correct": "partial", "score": 0.5, 
                                                                "expected": expected_savings, 
                                                                "submitted": savings}
        else:
            results["exercise3"]["details"]["potentialSavings"] = {"correct": False, "score": 0, 
                                                                "expected": expected_savings, 
                                                                "submitted": savings}
    else:
        results["exercise3"]["details"]["potentialSavings"] = {"correct": False, "score": 0, 
                                                            "expected": expected_savings, 
                                                            "submitted": savings}
    
    # Risk Level
    risk_level = ex3_sub.get("riskLevel")
    if risk_level == ex3_key.get("riskLevel"):
        results["exercise3"]["score"] += 1
        results["exercise3"]["details"]["riskLevel"] = {"correct": True, "score": 1}
    else:
        results["exercise3"]["details"]["riskLevel"] = {"correct": False, "score": 0, 
                                                      "expected": ex3_key.get("riskLevel"), 
                                                      "submitted": risk_level}
    
    # Bonus point if all items in Exercise 3 are correct
    all_correct = all(item.get("correct") == True for item in results["exercise3"]["details"].values())
    if all_correct:
        results["exercise3"]["score"] += 1
        results["exercise3"]["details"]["bonus"] = {"description": "All items correct", "score": 1}

def check_critical_elements(results):
    # Check if candidate met the minimum requirements for each exercise
    ex1_score = results["exercise1"]["score"]
    ex2_score = results["exercise2"]["score"]
    ex3_score = results["exercise3"]["score"]
    
    # Critical elements requirement: at least 3/5 in Ex1, 3/4 in Ex2, 3/4 in Ex3
    if ex1_score < 3 or ex2_score < 3 or ex3_score < 3:
        results["critical_elements_passed"] = False
    
    # Zero tolerance items
    ex2_action = results["exercise2"]["details"].get("recommendedAction", {}).get("correct")
    ex3_contract = results["exercise3"]["details"].get("contractRecommendation", {}).get("correct")
    
    if ex2_action is not True or ex3_contract is not True:
        if ex3_contract == "partial":  # Allow partial credit for contract recommendation
            pass
        else:
            results["critical_elements_passed"] = False
    
    # Overall passing requirement: at least 11/14 points
    total_score = ex1_score + ex2_score + ex3_score
    if total_score < 11:
        results["critical_elements_passed"] = False

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_test(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed critical elements: {results['critical_elements_passed']}")

if __name__ == "__main__":
    main()