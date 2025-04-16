import json
import sys
import math

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def check_exercise1(submission, answer_key):
    results = {"score": 0, "max_score": 4, "details": {}}
    
    # Check lowestTotalCost (within 1% tolerance)
    correct_cost = answer_key["lowestTotalCost"]
    submission_cost = submission.get("lowestTotalCost", 0)
    tolerance = correct_cost * 0.01
    cost_correct = abs(submission_cost - correct_cost) <= tolerance
    results["details"]["lowestTotalCost"] = {
        "correct": cost_correct,
        "submitted": submission_cost,
        "expected": correct_cost
    }
    if cost_correct:
        results["score"] += 1
    
    # Check recommendedSupplier
    correct_supplier = answer_key["recommendedSupplier"]
    submission_supplier = submission.get("recommendedSupplier", "")
    supplier_correct = submission_supplier == correct_supplier
    results["details"]["recommendedSupplier"] = {
        "correct": supplier_correct,
        "submitted": submission_supplier,
        "expected": correct_supplier
    }
    if supplier_correct:
        results["score"] += 1
    
    # Check priceVariance (within 1% tolerance)
    correct_variance = answer_key["priceVariance"]
    submission_variance = submission.get("priceVariance", 0)
    tolerance = max(correct_variance * 0.01, 0.1)  # At least 0.1 for small percentages
    variance_correct = abs(submission_variance - correct_variance) <= tolerance
    results["details"]["priceVariance"] = {
        "correct": variance_correct,
        "submitted": submission_variance,
        "expected": correct_variance
    }
    if variance_correct:
        results["score"] += 1
    
    # Check volumeDiscountSavings (within 1% tolerance)
    correct_savings = answer_key["volumeDiscountSavings"]
    submission_savings = submission.get("volumeDiscountSavings", 0)
    tolerance = correct_savings * 0.01
    savings_correct = abs(submission_savings - correct_savings) <= tolerance
    results["details"]["volumeDiscountSavings"] = {
        "correct": savings_correct,
        "submitted": submission_savings,
        "expected": correct_savings
    }
    if savings_correct:
        results["score"] += 1
    
    return results

def check_exercise2(submission, answer_key):
    results = {"score": 0, "max_score": 4, "details": {}}
    
    # Check overchargedComponents
    correct_components = set(answer_key["overchargedComponents"])
    submission_components = set(submission.get("overchargedComponents", []))
    
    # At least 2/3 of correct components must be identified
    min_required = math.ceil(len(correct_components) * 2/3)
    correct_matches = len(correct_components.intersection(submission_components))
    incorrect_matches = len(submission_components - correct_components)
    
    components_correct = correct_matches >= min_required and incorrect_matches == 0
    results["details"]["overchargedComponents"] = {
        "correct": components_correct,
        "submitted": sorted(list(submission_components)),
        "expected": sorted(list(correct_components)),
        "matches": correct_matches,
        "required_matches": min_required
    }
    if components_correct:
        results["score"] += 1
    
    # Check totalOvercharge (within 1% tolerance)
    correct_overcharge = answer_key["totalOvercharge"]
    submission_overcharge = submission.get("totalOvercharge", 0)
    tolerance = max(correct_overcharge * 0.01, 0.1)  # At least 0.1 for small values
    overcharge_correct = abs(submission_overcharge - correct_overcharge) <= tolerance
    results["details"]["totalOvercharge"] = {
        "correct": overcharge_correct,
        "submitted": submission_overcharge,
        "expected": correct_overcharge
    }
    if overcharge_correct:
        results["score"] += 1
    
    # Check marketRateCompliantComponents
    correct_market_components = set(answer_key["marketRateCompliantComponents"])
    submission_market_components = set(submission.get("marketRateCompliantComponents", []))
    
    # At least 2/3 of correct components must be identified
    min_required = math.ceil(len(correct_market_components) * 2/3)
    correct_matches = len(correct_market_components.intersection(submission_market_components))
    incorrect_matches = len(submission_market_components - correct_market_components)
    
    market_components_correct = correct_matches >= min_required and incorrect_matches == 0
    results["details"]["marketRateCompliantComponents"] = {
        "correct": market_components_correct,
        "submitted": sorted(list(submission_market_components)),
        "expected": sorted(list(correct_market_components)),
        "matches": correct_matches,
        "required_matches": min_required
    }
    if market_components_correct:
        results["score"] += 1
    
    # Check revisedTotalPrice (within 1% tolerance)
    correct_price = answer_key["revisedTotalPrice"]
    submission_price = submission.get("revisedTotalPrice", 0)
    tolerance = correct_price * 0.01
    price_correct = abs(submission_price - correct_price) <= tolerance
    results["details"]["revisedTotalPrice"] = {
        "correct": price_correct,
        "submitted": submission_price,
        "expected": correct_price
    }
    if price_correct:
        results["score"] += 1
    
    return results

def check_exercise3(submission, answer_key):
    results = {"score": 0, "max_score": 4, "details": {}}
    
    # Check averageQ4Price (within 1% tolerance)
    correct_q4_price = answer_key["averageQ4Price"]
    submission_q4_price = submission.get("averageQ4Price", 0)
    tolerance = correct_q4_price * 0.01
    q4_price_correct = abs(submission_q4_price - correct_q4_price) <= tolerance
    results["details"]["averageQ4Price"] = {
        "correct": q4_price_correct,
        "submitted": submission_q4_price,
        "expected": correct_q4_price
    }
    if q4_price_correct:
        results["score"] += 1
    
    # Check projectedQ1Price (special range)
    correct_q1_price = answer_key["projectedQ1Price"]
    submission_q1_price = submission.get("projectedQ1Price", 0)
    # Accept answers in the range of $49.50-$51.50
    q1_price_correct = 49.50 <= submission_q1_price <= 51.50
    results["details"]["projectedQ1Price"] = {
        "correct": q1_price_correct,
        "submitted": submission_q1_price,
        "expected": correct_q1_price,
        "acceptable_range": [49.50, 51.50]
    }
    if q1_price_correct:
        results["score"] += 1
    
    # Check sixMonthTrend
    correct_trend = answer_key["sixMonthTrend"]
    submission_trend = submission.get("sixMonthTrend", "")
    trend_correct = submission_trend == correct_trend
    results["details"]["sixMonthTrend"] = {
        "correct": trend_correct,
        "submitted": submission_trend,
        "expected": correct_trend
    }
    if trend_correct:
        results["score"] += 1
    
    # Check optimalPurchaseMonth
    correct_month = answer_key["optimalPurchaseMonth"]
    submission_month = submission.get("optimalPurchaseMonth", "")
    # Both "June" and "May" are acceptable answers
    month_correct = submission_month in ["June", "May"]
    results["details"]["optimalPurchaseMonth"] = {
        "correct": month_correct,
        "submitted": submission_month,
        "expected": correct_month,
        "acceptable_values": ["June", "May"]
    }
    if month_correct:
        results["score"] += 1
    
    return results

def evaluate_submission(submission, answer_key):
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "Exercise1": check_exercise1(submission.get("Exercise1", {}), answer_key["Exercise1"]),
        "Exercise2": check_exercise2(submission.get("Exercise2", {}), answer_key["Exercise2"]),
        "Exercise3": check_exercise3(submission.get("Exercise3", {}), answer_key["Exercise3"])
    }
    
    # Calculate total score
    total_score = (
        results["Exercise1"]["score"] +
        results["Exercise2"]["score"] +
        results["Exercise3"]["score"]
    )
    max_score = (
        results["Exercise1"]["max_score"] +
        results["Exercise2"]["max_score"] +
        results["Exercise3"]["max_score"]
    )
    
    results["total_score"] = total_score
    results["max_score"] = max_score
    results["overall_score"] = (total_score / max_score) * 100
    results["passed"] = total_score >= 9  # Passing threshold is 9 out of 12
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}% ({results['total_score']}/{results['max_score']} points)")
    print(f"Pass status: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()