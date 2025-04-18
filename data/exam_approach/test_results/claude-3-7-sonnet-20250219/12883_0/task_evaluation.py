#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, List, Any, Union, Tuple

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate Task 1 performance."""
    results = {"points": 0, "max_points": 30, "details": {}}
    
    # Check valid transaction count (10 points)
    sub_count = submission["task1"].get("valid_transactions_count", 0)
    key_count = answer_key["task1"]["valid_transactions_count"]
    count_diff = abs(sub_count - key_count)
    
    if count_diff == 0:
        count_score = 10
    elif count_diff == 1:
        count_score = 7
    else:
        count_score = max(0, 10 - 2 * count_diff)
    
    results["details"]["valid_transactions_count"] = {
        "score": count_score,
        "max_points": 10,
        "submitted": sub_count,
        "expected": key_count
    }
    
    # Check total value (10 points)
    sub_value = submission["task1"].get("total_value_valid_transactions", 0)
    key_value = answer_key["task1"]["total_value_valid_transactions"]
    value_diff = abs(sub_value - key_value)
    
    if value_diff == 0:
        value_score = 10
    elif value_diff <= 100:
        value_score = 7
    else:
        value_score = max(0, 10 - (value_diff / 100))
    
    results["details"]["total_value"] = {
        "score": value_score,
        "max_points": 10,
        "submitted": sub_value,
        "expected": key_value
    }
    
    # Check error transactions (10 points)
    sub_errors = submission["task1"].get("error_transactions", {})
    key_errors = answer_key["task1"]["error_transactions"]
    
    correct_errors = 0
    for tx_id, error_code in key_errors.items():
        if tx_id in sub_errors and sub_errors[tx_id] == error_code:
            correct_errors += 1
    
    error_score = (correct_errors / len(key_errors)) * 10
    
    results["details"]["error_transactions"] = {
        "score": error_score,
        "max_points": 10,
        "correct_identifications": correct_errors,
        "total_errors": len(key_errors)
    }
    
    # Calculate total score for Task 1
    total_score = count_score + value_score + error_score
    results["points"] = total_score
    
    return total_score, results

def evaluate_task2(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate Task 2 performance."""
    results = {"points": 0, "max_points": 35, "details": {}}
    
    # Check updated inventory (15 points)
    sub_inventory = submission["task2"].get("updated_inventory", {})
    key_inventory = answer_key["task2"]["updated_inventory"]
    
    correct_inventory = 0
    for prod_id, qty in key_inventory.items():
        if prod_id in sub_inventory and sub_inventory[prod_id] == qty:
            correct_inventory += 1
    
    inventory_score = (correct_inventory / len(key_inventory)) * 15
    
    results["details"]["updated_inventory"] = {
        "score": inventory_score,
        "max_points": 15,
        "correct_items": correct_inventory,
        "total_items": len(key_inventory)
    }
    
    # Check variance percentages (10 points)
    sub_variances = submission["task2"].get("variance_percentages", {})
    key_variances = answer_key["task2"]["variance_percentages"]
    
    correct_variances = 0
    for prod_id, variance in key_variances.items():
        if prod_id in sub_variances:
            # Allow 1% margin of error
            if abs(sub_variances[prod_id] - variance) <= 1.0:
                correct_variances += 1
    
    variance_score = (correct_variances / len(key_variances)) * 10
    
    results["details"]["variance_percentages"] = {
        "score": variance_score,
        "max_points": 10,
        "correct_items": correct_variances,
        "total_items": len(key_variances)
    }
    
    # Check highest variance products (10 points)
    sub_highest = submission["task2"].get("highest_variance_products", [])
    key_highest = answer_key["task2"]["highest_variance_products"]
    
    correct_highest = 0
    for i, prod_id in enumerate(key_highest):
        if i < len(sub_highest) and prod_id == sub_highest[i]:
            correct_highest += 1
        elif prod_id in sub_highest:
            correct_highest += 0.5  # Partial credit for correct but wrong position
    
    highest_score = (correct_highest / len(key_highest)) * 10
    
    results["details"]["highest_variance_products"] = {
        "score": highest_score,
        "max_points": 10,
        "correct_items": correct_highest,
        "total_items": len(key_highest)
    }
    
    # Calculate total score for Task 2
    total_score = inventory_score + variance_score + highest_score
    results["points"] = total_score
    
    return total_score, results

def evaluate_task3(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate Task 3 performance."""
    results = {"points": 0, "max_points": 35, "details": {}}
    
    # Check USDA category totals (20 points)
    sub_categories = submission["task3"].get("usda_category_totals", {})
    key_categories = answer_key["task3"]["usda_category_totals"]
    
    category_score = 0
    category_details = {}
    
    for category, key_data in key_categories.items():
        if category not in sub_categories:
            category_details[category] = {
                "score": 0,
                "max_points": 20 / len(key_categories),
                "details": "Category missing"
            }
            continue
            
        sub_data = sub_categories[category]
        cat_score = 0
        cat_details = {}
        
        # Check volume (within 5%)
        key_volume = key_data["total_volume"]
        sub_volume = sub_data.get("total_volume", 0)
        volume_pct_diff = abs(sub_volume - key_volume) / max(1, key_volume) * 100
        
        if volume_pct_diff <= 5:
            volume_score = 1
        else:
            volume_score = max(0, 1 - (volume_pct_diff - 5) / 95)
            
        cat_details["volume"] = {
            "score": volume_score,
            "submitted": sub_volume,
            "expected": key_volume
        }
        cat_score += volume_score
        
        # Check value
        key_value = key_data["total_value"]
        sub_value = sub_data.get("total_value", 0)
        value_pct_diff = abs(sub_value - key_value) / max(1, key_value) * 100
        
        if value_pct_diff <= 5:
            value_score = 1
        else:
            value_score = max(0, 1 - (value_pct_diff - 5) / 95)
            
        cat_details["value"] = {
            "score": value_score,
            "submitted": sub_value,
            "expected": key_value
        }
        cat_score += value_score
        
        # Check transaction count
        key_count = key_data["transaction_count"]
        sub_count = sub_data.get("transaction_count", 0)
        
        count_score = 1 if key_count == sub_count else 0
            
        cat_details["transaction_count"] = {
            "score": count_score,
            "submitted": sub_count,
            "expected": key_count
        }
        cat_score += count_score
        
        # Check organic volume
        key_organic = key_data["organic_volume"]
        sub_organic = sub_data.get("organic_volume", 0)
        
        organic_score = 1 if key_organic == sub_organic else 0.5 if abs(key_organic - sub_organic) / max(1, key_organic) <= 0.1 else 0
            
        cat_details["organic_volume"] = {
            "score": organic_score,
            "submitted": sub_organic,
            "expected": key_organic
        }
        cat_score += organic_score
        
        # Check conventional volume
        key_conv = key_data["conventional_volume"]
        sub_conv = sub_data.get("conventional_volume", 0)
        
        conv_score = 1 if key_conv == sub_conv else 0.5 if abs(key_conv - sub_conv) / max(1, key_conv) <= 0.1 else 0
            
        cat_details["conventional_volume"] = {
            "score": conv_score,
            "submitted": sub_conv,
            "expected": key_conv
        }
        cat_score += conv_score
        
        # Calculate total category score (out of 5 possible points)
        cat_total = (cat_score / 5) * (20 / len(key_categories))
        category_score += cat_total
        
        category_details[category] = {
            "score": cat_total,
            "max_points": 20 / len(key_categories),
            "details": cat_details
        }
    
    results["details"]["usda_category_totals"] = {
        "score": category_score,
        "max_points": 20,
        "category_details": category_details
    }
    
    # Check compliance issues (5 points)
    sub_issues = submission["task3"].get("compliance_issues", [])
    key_issues = answer_key["task3"]["compliance_issues"]
    
    # For empty lists, score is 5 if both are empty, 0 otherwise
    if not key_issues:
        compliance_score = 5 if not sub_issues else 0
    else:
        correct_issues = 0
        for issue in key_issues:
            if issue in sub_issues:
                correct_issues += 1
        
        compliance_score = (correct_issues / len(key_issues)) * 5
    
    results["details"]["compliance_issues"] = {
        "score": compliance_score,
        "max_points": 5,
        "submitted": sub_issues,
        "expected": key_issues
    }
    
    # Check verification code (10 points)
    sub_code = submission["task3"].get("verification_code", "")
    key_code = answer_key["task3"]["verification_code"]
    
    if sub_code == key_code:
        code_score = 10
    elif len(sub_code) == len(key_code) and sub_code[2:] == key_code[2:]:  # Correct format, wrong entity
        code_score = 5
    elif len(sub_code) == len(key_code):  # Correct format, wrong values
        code_score = 2
    else:
        code_score = 0
    
    results["details"]["verification_code"] = {
        "score": code_score,
        "max_points": 10,
        "submitted": sub_code,
        "expected": key_code
    }
    
    # Calculate total score for Task 3
    total_score = category_score + compliance_score + code_score
    results["points"] = total_score
    
    return total_score, results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "task1": {},
        "task2": {},
        "task3": {},
        "overall_score": 0,
        "points": 0,
        "max_points": 100
    }
    
    # Evaluate each task
    task1_score, results["task1"] = evaluate_task1(submission, answer_key)
    task2_score, results["task2"] = evaluate_task2(submission, answer_key)
    task3_score, results["task3"] = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    results["points"] = total_score
    results["overall_score"] = round(total_score)
    
    return results

def main():
    """Main function to process command line arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load JSON files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")

if __name__ == "__main__":
    main()