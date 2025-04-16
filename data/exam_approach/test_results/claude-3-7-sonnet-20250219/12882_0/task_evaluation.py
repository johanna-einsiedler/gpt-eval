#!/usr/bin/env python3

import json
import sys
import math
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_product_requirements(submission: List[Dict], answer_key: List[Dict]) -> Dict[str, Any]:
    """Evaluate the product requirements section (40% of score)."""
    results = {
        "score": 0,
        "max_score": 40,
        "details": {}
    }
    
    # Create dictionaries for easier comparison
    submission_dict = {item["product_id"]: item for item in submission}
    answer_key_dict = {item["product_id"]: item for item in answer_key}
    
    total_products = len(answer_key)
    points_per_product = results["max_score"] / total_products
    correct_count = 0
    
    for product_id, expected in answer_key_dict.items():
        if product_id not in submission_dict:
            results["details"][product_id] = {
                "status": "missing",
                "points": 0,
                "expected": expected,
                "submitted": None
            }
            continue
        
        submitted = submission_dict[product_id]
        product_result = {
            "status": "incorrect",
            "points": 0,
            "expected": expected,
            "submitted": submitted
        }
        
        # Check if quantity is within 5% margin
        quantity_match = False
        if abs(submitted["quantity_required"] - expected["quantity_required"]) <= 0.05 * expected["quantity_required"]:
            quantity_match = True
        
        # All other fields should match exactly
        other_fields_match = (
            submitted["product_name"] == expected["product_name"] and
            submitted["unit"] == expected["unit"] and
            submitted["supplier_id"] == expected["supplier_id"]
        )
        
        if quantity_match and other_fields_match:
            product_result["status"] = "correct"
            product_result["points"] = points_per_product
            correct_count += 1
        
        results["details"][product_id] = product_result
    
    results["score"] = correct_count * points_per_product
    results["passed"] = correct_count >= 5  # Need at least 5 out of 7 correct
    
    return results

def evaluate_demand_changes(submission: List[Dict], answer_key: List[Dict]) -> Dict[str, Any]:
    """Evaluate the demand changes section (20% of score)."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # Create dictionaries for easier comparison
    submission_dict = {item["product_id"]: item for item in submission}
    answer_key_dict = {item["product_id"]: item for item in answer_key}
    
    total_products = len(answer_key)
    points_per_product = results["max_score"] / total_products
    correct_count = 0
    
    for product_id, expected in answer_key_dict.items():
        if product_id not in submission_dict:
            results["details"][product_id] = {
                "status": "missing",
                "points": 0,
                "expected": expected["percentage_change"],
                "submitted": None
            }
            continue
        
        submitted = submission_dict[product_id]
        product_result = {
            "status": "incorrect",
            "points": 0,
            "expected": expected["percentage_change"],
            "submitted": submitted["percentage_change"]
        }
        
        # Check if percentage is within 1% margin
        if abs(submitted["percentage_change"] - expected["percentage_change"]) <= 1.0:
            product_result["status"] = "correct"
            product_result["points"] = points_per_product
            correct_count += 1
        
        results["details"][product_id] = product_result
    
    results["score"] = correct_count * points_per_product
    results["passed"] = correct_count >= 5  # Need at least 5 out of 7 correct
    
    return results

def evaluate_supplier_selection(submission: List[Dict], answer_key: List[Dict]) -> Dict[str, Any]:
    """Evaluate the supplier selection (15% of score)."""
    results = {
        "score": 0,
        "max_score": 15,
        "details": {}
    }
    
    # Create dictionaries for easier comparison
    submission_dict = {item["product_id"]: item["supplier_id"] for item in submission}
    answer_key_dict = {item["product_id"]: item["supplier_id"] for item in answer_key}
    
    total_products = len(answer_key)
    points_per_product = results["max_score"] / total_products
    correct_count = 0
    
    for product_id, expected_supplier in answer_key_dict.items():
        if product_id not in submission_dict:
            results["details"][product_id] = {
                "status": "missing",
                "points": 0,
                "expected": expected_supplier,
                "submitted": None
            }
            continue
        
        submitted_supplier = submission_dict[product_id]
        product_result = {
            "status": "incorrect",
            "points": 0,
            "expected": expected_supplier,
            "submitted": submitted_supplier
        }
        
        if submitted_supplier == expected_supplier:
            product_result["status"] = "correct"
            product_result["points"] = points_per_product
            correct_count += 1
        
        results["details"][product_id] = product_result
    
    results["score"] = correct_count * points_per_product
    results["passed"] = correct_count >= 5  # Need at least 5 out of 7 correct
    
    return results

def evaluate_procurement_cost(submission: float, answer_key: float) -> Dict[str, Any]:
    """Evaluate the total procurement cost (10% of score)."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": {
            "expected": answer_key,
            "submitted": submission,
            "difference": abs(submission - answer_key),
            "percentage_diff": (abs(submission - answer_key) / answer_key) * 100
        }
    }
    
    # Check if cost is within 2% of correct total
    if abs(submission - answer_key) <= 250:
        results["score"] = results["max_score"]
        results["details"]["status"] = "correct"
        results["passed"] = True
    else:
        results["details"]["status"] = "incorrect"
        results["passed"] = False
    
    return results

def evaluate_priority_products(submission: List[str], answer_key: List[str]) -> Dict[str, Any]:
    """Evaluate the priority products section (15% of score)."""
    results = {
        "score": 0,
        "max_score": 15,
        "details": {
            "expected": answer_key,
            "submitted": submission
        }
    }
    
    # Count correct priority products
    correct_count = sum(1 for product in submission if product in answer_key)
    points_per_product = results["max_score"] / len(answer_key)
    
    results["score"] = correct_count * points_per_product
    results["details"]["correct_count"] = correct_count
    results["passed"] = correct_count >= 2  # Need at least 2 out of 3 correct
    
    return results

def evaluate_submission(submission_path: str, answer_key_path: str) -> Dict[str, Any]:
    """Evaluate a candidate's submission against the answer key."""
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "sections": {},
        "critical_tasks_passed": False,
        "overall_score": 0
    }
    
    # Evaluate each section
    results["sections"]["product_requirements"] = evaluate_product_requirements(
        submission.get("product_requirements", []),
        answer_key.get("product_requirements", [])
    )
    
    results["sections"]["demand_changes"] = evaluate_demand_changes(
        submission.get("demand_changes", []),
        answer_key.get("demand_changes", [])
    )
    
    results["sections"]["supplier_selection"] = evaluate_supplier_selection(
        submission.get("product_requirements", []),
        answer_key.get("product_requirements", [])
    )
    
    results["sections"]["procurement_cost"] = evaluate_procurement_cost(
        submission.get("total_procurement_cost", 0),
        answer_key.get("total_procurement_cost", 0)
    )
    
    results["sections"]["priority_products"] = evaluate_priority_products(
        submission.get("priority_products", []),
        answer_key.get("priority_products", [])
    )
    
    # Calculate overall score
    total_score = sum(section["score"] for section in results["sections"].values())
    total_possible = sum(section["max_score"] for section in results["sections"].values())
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    # Check if critical tasks are passed
    results["critical_tasks_passed"] = (
        results["sections"]["product_requirements"]["passed"] and
        results["sections"]["priority_products"]["passed"]
    )
    
    # Determine overall pass/fail
    results["passed"] = results["critical_tasks_passed"] and results["overall_score"] >= 70
    
    return results

def main():
    """Main function to parse arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()