#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)

def evaluate_supplier_rankings(submission, answer_key):
    """Evaluate the supplier rankings section."""
    score = 0
    max_score = 25
    
    # Get the submission and answer key rankings
    sub_rankings = {item["supplier_id"]: {"rank": item["rank"], "score": item["score"]} 
                    for item in submission["supplier_rankings"]}
    key_rankings = {item["supplier_id"]: {"rank": item["rank"], "score": item["score"]} 
                    for item in answer_key["supplier_rankings"]}
    
    # Check if rankings match the answer key
    correct_ordering = True
    for supplier_id, data in key_rankings.items():
        if supplier_id not in sub_rankings:
            correct_ordering = False
            break
        if sub_rankings[supplier_id]["rank"] != data["rank"]:
            correct_ordering = False
            break
    
    # Award points for correct ranking order (15 points)
    if correct_ordering:
        score += 15
        details = "Correct ranking order (+15 points)"
    else:
        details = "Incorrect ranking order (0 out of 15 points)"
    
    # Award points for appropriate weighted scores (10 points)
    weighted_score_points = 0
    weighted_score_details = []
    
    for supplier_id, data in key_rankings.items():
        if supplier_id in sub_rankings:
            key_score = data["score"]
            sub_score = sub_rankings[supplier_id]["score"]
            
            # Check if score is within ±0.5 of the key
            if abs(key_score - sub_score) <= 0.5:
                weighted_score_points += 2  # 2 points per supplier (10 points total for 5 suppliers)
                weighted_score_details.append(f"{supplier_id}: Score within tolerance (+2 points)")
            else:
                weighted_score_details.append(f"{supplier_id}: Score outside tolerance (0 points)")
    
    score += weighted_score_points
    details += f"; Weighted scores: {weighted_score_points}/10 points - " + ", ".join(weighted_score_details)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "details": details
    }

def evaluate_metrics(submission, answer_key):
    """Evaluate the evaluation metrics section."""
    score = 0
    max_score = 35
    
    # Get the evaluation metrics from submission and answer key
    metrics = [
        "price_score", "quality_score", "selection_score", "service_score", 
        "support_score", "reliability_score", "production_score", 
        "distribution_score", "reputation_score"
    ]
    
    category_score_details = []
    ordering_score_details = []
    
    category_score_points = 0
    ordering_score_points = 0
    
    for metric in metrics:
        # Check if metric exists in both submission and answer key
        if metric not in submission["evaluation_metrics"] or metric not in answer_key["evaluation_metrics"]:
            category_score_details.append(f"{metric}: Missing metric (0 points)")
            ordering_score_details.append(f"{metric}: Missing metric (0 points)")
            continue
        
        # Get the submission and answer key scores for this metric
        sub_scores = {item["supplier_id"]: item["score"] 
                      for item in submission["evaluation_metrics"][metric]}
        key_scores = {item["supplier_id"]: item["score"] 
                      for item in answer_key["evaluation_metrics"][metric]}
        
        # Check individual category scores (within ±1.0)
        metric_score_correct = True
        for supplier_id, key_score in key_scores.items():
            if supplier_id not in sub_scores:
                metric_score_correct = False
                break
            if abs(key_score - sub_scores[supplier_id]) > 1.0:
                metric_score_correct = False
                break
        
        # Each metric is worth approximately 2.22 points (20 points / 9 metrics)
        if metric_score_correct:
            category_score_points += 2.22
            category_score_details.append(f"{metric}: Scores within tolerance")
        else:
            category_score_details.append(f"{metric}: Scores outside tolerance")
        
        # Check correct relative ordering
        # Get ordered lists of supplier IDs from highest to lowest score
        try:
            key_ordered = [item["supplier_id"] for item in sorted(
                answer_key["evaluation_metrics"][metric], 
                key=lambda x: x["score"], 
                reverse=True
            )]
            
            sub_ordered = [item["supplier_id"] for item in sorted(
                submission["evaluation_metrics"][metric], 
                key=lambda x: x["score"], 
                reverse=True
            )]
            
            # Each metric is worth approximately 1.67 points (15 points / 9 metrics)
            if key_ordered == sub_ordered:
                ordering_score_points += 1.67
                ordering_score_details.append(f"{metric}: Correct ordering")
            else:
                ordering_score_details.append(f"{metric}: Incorrect ordering")
        except Exception as e:
            ordering_score_details.append(f"{metric}: Error checking ordering - {str(e)}")
    
    # Round the scores to avoid floating point issues and cap at max possible
    category_score_points = min(round(category_score_points), 20)
    ordering_score_points = min(round(ordering_score_points), 15)
    
    score = category_score_points + ordering_score_points
    
    details = f"Individual category scores: {category_score_points}/20 points - " + "; ".join(category_score_details)
    details += f"; Relative ordering: {ordering_score_points}/15 points - " + "; ".join(ordering_score_details)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "details": details
    }

def evaluate_cost_analysis(submission, answer_key):
    """Evaluate the cost analysis section."""
    score = 0
    max_score = 10
    
    # Check annual spend calculations (5 points)
    annual_spend_score = 0
    annual_spend_details = []
    
    key_annual_spend = {item["supplier_id"]: item["amount"] 
                       for item in answer_key["cost_analysis"]["annual_spend"]}
    sub_annual_spend = {item["supplier_id"]: item["amount"] 
                       for item in submission["cost_analysis"]["annual_spend"]}
    
    correct_annual_spend = True
    for supplier_id, amount in key_annual_spend.items():
        if supplier_id not in sub_annual_spend:
            correct_annual_spend = False
            annual_spend_details.append(f"{supplier_id}: Missing from submission")
            break
        
        # Allow for slight differences due to rounding
        if abs(amount - sub_annual_spend[supplier_id]) > 1:
            correct_annual_spend = False
            annual_spend_details.append(f"{supplier_id}: Incorrect calculation (expected {amount}, got {sub_annual_spend[supplier_id]})")
    
    if correct_annual_spend:
        annual_spend_score = 5
        annual_spend_details = ["All annual spend calculations correct"]
    
    # Check unit price reporting (5 points)
    unit_price_score = 0
    unit_price_details = []
    
    key_unit_price = {item["supplier_id"]: item["price"] 
                     for item in answer_key["cost_analysis"]["unit_price"]}
    sub_unit_price = {item["supplier_id"]: item["price"] 
                     for item in submission["cost_analysis"]["unit_price"]}
    
    correct_unit_price = True
    for supplier_id, price in key_unit_price.items():
        if supplier_id not in sub_unit_price:
            correct_unit_price = False
            unit_price_details.append(f"{supplier_id}: Missing from submission")
            break
        
        # Check exact match for unit price (should be copied directly from materials)
        if abs(price - sub_unit_price[supplier_id]) > 0.01:
            correct_unit_price = False
            unit_price_details.append(f"{supplier_id}: Incorrect price (expected {price}, got {sub_unit_price[supplier_id]})")
    
    if correct_unit_price:
        unit_price_score = 5
        unit_price_details = ["All unit prices correct"]
    
    score = annual_spend_score + unit_price_score
    details = f"Annual spend calculations: {annual_spend_score}/5 points - " + "; ".join(annual_spend_details)
    details += f"; Unit price reporting: {unit_price_score}/5 points - " + "; ".join(unit_price_details)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "details": details
    }

def evaluate_optimal_supplier(submission, answer_key):
    """Evaluate the optimal supplier identification."""
    score = 0
    max_score = 15
    
    key_optimal = answer_key["optimal_supplier"]
    sub_optimal = submission["optimal_supplier"]
    
    if sub_optimal == key_optimal:
        score = 15
        details = f"Correctly identified {key_optimal} as the optimal supplier"
    # Allow for QualityTech with proper justification (check would need evaluation of methodology, simplified here)
    elif sub_optimal == "SUP842":
        score = 12
        details = f"Identified QualityTech (SUP842) instead of CircuitTech (SUP417); partial credit assigned"
    else:
        details = f"Incorrectly identified {sub_optimal} as the optimal supplier; correct answer is {key_optimal}"
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "details": details
    }

def evaluate_risk_assessment(submission, answer_key):
    """Evaluate the risk assessment section."""
    score = 0
    max_score = 15
    
    key_high_risk = set(answer_key["risk_assessment"]["high_risk_suppliers"])
    sub_high_risk = set(submission["risk_assessment"]["high_risk_suppliers"])
    
    # Check if high-risk suppliers are correctly identified (10 points)
    if key_high_risk == sub_high_risk:
        score += 10
        details = "Correctly identified all high-risk suppliers (+10 points)"
    elif "SUP631" in sub_high_risk:
        # Give partial credit if at least SUP631 is identified as high-risk
        score += 8
        details = "Correctly identified SUP631 as high-risk but missed or added others (+8 points)"
    else:
        details = "Failed to identify SUP631 as a high-risk supplier (0 points)"
    
    # Check for appropriate risk reasons (5 points)
    sub_reasons = submission["risk_assessment"]["risk_reasons"]
    
    # Check if risk reasons mention quality and reliability issues
    quality_mentioned = False
    reliability_mentioned = False
    
    for reason in sub_reasons:
        lower_reason = reason.lower()
        if "quality" in lower_reason or "defect" in lower_reason:
            quality_mentioned = True
        if "reliability" in lower_reason or "on-time" in lower_reason or "delivery" in lower_reason:
            reliability_mentioned = True
    
    reason_score = 0
    reason_details = []
    
    if "SUP631" in sub_high_risk:
        if quality_mentioned and reliability_mentioned:
            reason_score = 5
            reason_details.append("Provided complete reasoning mentioning both quality and reliability issues")
        elif quality_mentioned or reliability_mentioned:
            reason_score = 3
            reason_details.append("Mentioned some key issues but not all (quality or reliability)")
        else:
            reason_details.append("Failed to mention key quality and reliability issues")
    else:
        reason_details.append("No credit for reasons as SUP631 not identified as high-risk")
    
    score += reason_score
    details += f"; Risk reasons: {reason_score}/5 points - " + "; ".join(reason_details)
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "details": details
    }

def check_automatic_failures(submission):
    """Check for automatic failing conditions."""
    failures = []
    
    # 1. Failure to identify AsiaComponents (SUP631) as a high-risk supplier
    if "SUP631" not in submission["risk_assessment"]["high_risk_suppliers"]:
        failures.append("Failed to identify AsiaComponents (SUP631) as a high-risk supplier")
    
    # 2. Recommending AsiaComponents (SUP631) as the optimal supplier
    if submission["optimal_supplier"] == "SUP631":
        failures.append("Incorrectly recommended AsiaComponents (SUP631) as the optimal supplier")
    
    # 3. Major calculation errors - checked in individual sections
    
    # 4. Incomplete submission - check for missing required sections
    required_sections = ["supplier_rankings", "evaluation_metrics", "cost_analysis", 
                        "optimal_supplier", "risk_assessment"]
    
    for section in required_sections:
        if section not in submission:
            failures.append(f"Incomplete submission: Missing {section} section")
    
    return failures

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    results = {
        "supplier_rankings": evaluate_supplier_rankings(submission, answer_key),
        "evaluation_metrics": evaluate_metrics(submission, answer_key),
        "cost_analysis": evaluate_cost_analysis(submission, answer_key),
        "optimal_supplier": evaluate_optimal_supplier(submission, answer_key),
        "risk_assessment": evaluate_risk_assessment(submission, answer_key),
    }
    
    # Calculate total score and max possible score
    total_score = sum(section["score"] for section in results.values())
    max_score = sum(section["max_score"] for section in results.values())
    
    # Check for automatic failing conditions
    automatic_failures = check_automatic_failures(submission)
    
    if automatic_failures:
        overall_score = 0
        failure_message = "AUTOMATIC FAILURE: " + "; ".join(automatic_failures)
    else:
        overall_score = (total_score / max_score) * 100
    
    # Add overall results
    results["total"] = {
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100,
        "details": f"Total points: {total_score}/{max_score}"
    }
    
    results["overall_score"] = overall_score
    
    if automatic_failures:
        results["automatic_failures"] = automatic_failures
    
    # Determine qualification level
    if overall_score >= 90:
        results["qualification_level"] = "Excellent"
    elif overall_score >= 80:
        results["qualification_level"] = "Good"
    elif overall_score >= 70:
        results["qualification_level"] = "Satisfactory"
    else:
        results["qualification_level"] = "Needs Improvement"
    
    return results

def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Qualification level: {results['qualification_level']}")
    
    if "automatic_failures" in results:
        print("AUTOMATIC FAILURE CONDITIONS DETECTED:")
        for failure in results["automatic_failures"]:
            print(f"- {failure}")

if __name__ == "__main__":
    main()