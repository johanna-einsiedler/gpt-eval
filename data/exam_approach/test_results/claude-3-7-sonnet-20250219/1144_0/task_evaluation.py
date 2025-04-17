#!/usr/bin/env python3
import json
import sys
import os

def load_json(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_meets_requirements(candidate, answer_key):
    """Evaluate if candidate correctly identified suppliers meeting requirements."""
    specs_score = 0
    budget_score = 0
    
    # Check specifications
    for supplier in answer_key["meets_specifications"]:
        if candidate["meets_specifications"].get(supplier) == answer_key["meets_specifications"][supplier]:
            specs_score += 1
    
    # Check budget
    for supplier in answer_key["meets_budget"]:
        if candidate["meets_budget"].get(supplier) == answer_key["meets_budget"][supplier]:
            budget_score += 1
    
    specs_score = (specs_score / 5) * 10  # 10 points total for specifications
    budget_score = (budget_score / 5) * 10  # 10 points total for budget
    
    return {
        "specifications_score": specs_score,
        "budget_score": budget_score,
        "total_essential_score": specs_score + budget_score
    }

def evaluate_supplier_scores(candidate, answer_key):
    """Evaluate if candidate's scores are within acceptable ranges."""
    # Define acceptable ranges for each supplier and criterion
    acceptable_ranges = {
        "supplier_A": {
            "price": (6, 8),
            "quality": (5, 7),
            "delivery_reliability": (6, 8),
            "production_capacity": (6, 8),
            "technical_support": (5, 7),
            "financial_stability": (6, 8)
        },
        "supplier_B": {
            "price": (5, 7),
            "quality": (8, 10),
            "delivery_reliability": (8, 10),
            "production_capacity": (7, 9),
            "technical_support": (8, 10),
            "financial_stability": (7, 9)
        },
        "supplier_C": {
            "price": (2, 4),
            "quality": (3, 5),
            "delivery_reliability": (2, 4),
            "production_capacity": (2, 4),
            "technical_support": (3, 5),
            "financial_stability": (4, 6)
        },
        "supplier_D": {
            "price": (8, 10),
            "quality": (7, 9),
            "delivery_reliability": (7, 9),
            "production_capacity": (9, 10),
            "technical_support": (7, 9),
            "financial_stability": (8, 10)
        },
        "supplier_E": {
            "price": (4, 6),
            "quality": (6, 8),
            "delivery_reliability": (5, 7),
            "production_capacity": (5, 7),
            "technical_support": (5, 7),
            "financial_stability": (5, 7)
        }
    }
    
    score_details = {}
    total_correct = 0
    total_criteria = 0
    
    for supplier in candidate["supplier_scores"]:
        supplier_result = {"criteria_scores": {}}
        supplier_correct = 0
        supplier_total = 0
        
        for criterion in candidate["supplier_scores"][supplier]:
            if criterion == "total_score":
                continue
            
            supplier_total += 1
            total_criteria += 1
            
            min_val, max_val = acceptable_ranges[supplier][criterion]
            score = candidate["supplier_scores"][supplier][criterion]
            
            is_in_range = min_val <= score <= max_val
            
            if is_in_range:
                supplier_correct += 1
                total_correct += 1
                
            supplier_result["criteria_scores"][criterion] = {
                "score": score,
                "acceptable_range": (min_val, max_val),
                "is_correct": is_in_range
            }
        
        # Check if total score matches sum of individual scores
        individual_sum = sum(candidate["supplier_scores"][supplier][c] for c in candidate["supplier_scores"][supplier] if c != "total_score")
        reported_total = candidate["supplier_scores"][supplier]["total_score"]
        total_score_correct = individual_sum == reported_total
        
        supplier_result["total_score"] = {
            "reported": reported_total,
            "calculated": individual_sum,
            "is_correct": total_score_correct
        }
        
        supplier_result["accuracy"] = supplier_correct / supplier_total
        score_details[supplier] = supplier_result
    
    overall_accuracy = total_correct / total_criteria if total_criteria > 0 else 0
    score = overall_accuracy * 40  # 40 points total for supplier scores
    
    return {
        "score": score,
        "overall_accuracy": overall_accuracy,
        "details": score_details
    }

def evaluate_price_comparison(candidate, answer_key):
    """Evaluate if candidate's price comparison is accurate."""
    correct_prices = 0
    details = {}
    
    for supplier in answer_key["price_comparison"]:
        correct_price = answer_key["price_comparison"][supplier]
        candidate_price = candidate["price_comparison"].get(supplier, 0)
        
        # Allow for small float precision differences
        is_correct = abs(candidate_price - correct_price) < 0.01
        
        if is_correct:
            correct_prices += 1
            
        details[supplier] = {
            "candidate_price": candidate_price,
            "correct_price": correct_price,
            "is_correct": is_correct
        }
    
    accuracy = correct_prices / len(answer_key["price_comparison"]) if answer_key["price_comparison"] else 0
    score = accuracy * 15  # 15 points total for price comparison
    
    return {
        "score": score,
        "accuracy": accuracy,
        "details": details
    }

def evaluate_recommended_suppliers(candidate, answer_key):
    """Evaluate if candidate recommended the correct suppliers."""
    correct_recommendations = 0
    details = {"recommendations": []}
    
    for i, supplier in enumerate(answer_key["recommended_suppliers"]):
        if i < len(candidate["recommended_suppliers"]) and candidate["recommended_suppliers"][i] == supplier:
            correct_recommendations += 1
            details["recommendations"].append({
                "position": i + 1,
                "candidate_choice": candidate["recommended_suppliers"][i],
                "correct_choice": supplier,
                "is_correct": True
            })
        else:
            candidate_choice = candidate["recommended_suppliers"][i] if i < len(candidate["recommended_suppliers"]) else "None"
            details["recommendations"].append({
                "position": i + 1,
                "candidate_choice": candidate_choice,
                "correct_choice": supplier,
                "is_correct": False
            })
    
    accuracy = correct_recommendations / len(answer_key["recommended_suppliers"]) if answer_key["recommended_suppliers"] else 0
    score = accuracy * 20  # 20 points total for recommended suppliers
    
    return {
        "score": score,
        "accuracy": accuracy,
        "details": details
    }

def evaluate_justifications(candidate, answer_key):
    """Evaluate quality of candidate's justifications based on length and content."""
    # This is a simplified assessment as true qualitative evaluation needs human judgment
    justification_scores = {}
    total_score = 0
    
    # Check if justifications exist for all suppliers
    suppliers_covered = 0
    for supplier in answer_key["justification"]:
        if supplier == "final_recommendation":
            continue
            
        if supplier in candidate["justification"] and len(candidate["justification"][supplier]) > 20:
            suppliers_covered += 1
    
    # Data-driven reasoning - check for mentions of specific metrics
    metrics = [
        "price", "cost", "$", "quality", "rejection", "delivery", "on-time", 
        "lead time", "capacity", "production", "technical", "support", 
        "response time", "financial", "stability"
    ]
    
    metrics_used = 0
    total_metrics = len(metrics) if "justification" in candidate else 0
    
    if "justification" in candidate:
        all_text = " ".join(candidate["justification"].values()).lower()
        for metric in metrics:
            if metric.lower() in all_text:
                metrics_used += 1
    
    # Completeness - check for final recommendation
    has_final_recommendation = (
        "justification" in candidate and 
        "final_recommendation" in candidate["justification"] and
        len(candidate["justification"]["final_recommendation"]) > 50
    )
    
    # Calculate scores
    supplier_coverage_score = (suppliers_covered / 5) * 10  # 10 points
    data_driven_score = (metrics_used / total_metrics) * 10 if total_metrics > 0 else 0  # 10 points
    completeness_score = 5 if has_final_recommendation else 0  # 5 points
    
    total_score = supplier_coverage_score + data_driven_score + completeness_score
    
    return {
        "score": total_score,
        "supplier_coverage_score": supplier_coverage_score,
        "data_driven_score": data_driven_score,
        "completeness_score": completeness_score,
        "suppliers_covered": suppliers_covered,
        "metrics_used": metrics_used,
        "has_final_recommendation": has_final_recommendation
    }

def evaluate_submission(candidate, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    # Check if JSON is in valid format
    is_valid_format = (
        "supplier_scores" in candidate and 
        "recommended_suppliers" in candidate and
        "price_comparison" in candidate and
        "meets_specifications" in candidate and
        "meets_budget" in candidate
    )
    
    if not is_valid_format:
        return {
            "overall_score": 0,
            "is_valid_format": False,
            "message": "Submission is not in the required format"
        }

    # Evaluate different sections
    essential_elements = evaluate_meets_requirements(candidate, answer_key)
    supplier_scores = evaluate_supplier_scores(candidate, answer_key)
    price_comparison = evaluate_price_comparison(candidate, answer_key)
    recommended_suppliers = evaluate_recommended_suppliers(candidate, answer_key)
    justifications = evaluate_justifications(candidate, answer_key)
    
    # Calculate overall score (out of 100)
    overall_score = (
        essential_elements["total_essential_score"] +  # 20 points
        supplier_scores["score"] +                     # 40 points
        price_comparison["score"] +                    # 15 points
        recommended_suppliers["score"] +               # 20 points
        justifications["score"]                        # 25 points
    )
    
    # Apply pass/fail criteria
    passed_essential = (
        essential_elements["specifications_score"] == 10 and
        essential_elements["budget_score"] == 10 and
        is_valid_format
    )
    
    passed_overall = overall_score >= 75
    
    passed = passed_essential and passed_overall
    
    return {
        "overall_score": overall_score,
        "percentage_score": overall_score,  # Already out of 100
        "passed": passed,
        "passed_essential": passed_essential,
        "passed_overall": passed_overall,
        "is_valid_format": is_valid_format,
        "essential_elements": essential_elements,
        "supplier_scores": supplier_scores,
        "price_comparison": price_comparison,
        "recommended_suppliers": recommended_suppliers,
        "justifications": justifications
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    candidate_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate = load_json(candidate_file)
    answer_key = load_json(answer_key_file)
    
    results = evaluate_submission(candidate, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()