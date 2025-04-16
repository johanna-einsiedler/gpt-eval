import json
import sys
import math

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {str(e)}")
        sys.exit(1)

def evaluate_average_monthly_consumption(submission, answer_key):
    submission_values = submission.get('task1', {}).get('average_monthly_consumption', {})
    answer_key_values = answer_key.get('task1', {}).get('average_monthly_consumption', {})
    
    points = 10
    errors = 0
    
    for product_id, correct_value in answer_key_values.items():
        if product_id not in submission_values:
            errors += 1
            continue
            
        submitted_value = submission_values.get(product_id, 0)
        if not isinstance(submitted_value, (int, float)):
            errors += 1
            continue
            
        # Check if within ±5% of correct value
        if abs(submitted_value - correct_value) > (correct_value * 0.05):
            errors += 1
    
    points_deducted = min(points, errors * 0.5)
    score = points - points_deducted
    
    return {
        "score": score,
        "max_points": points,
        "errors": errors,
        "comments": f"Found {errors} values outside the acceptable range (±5%)"
    }

def evaluate_top_products(submission, answer_key):
    submission_values = submission.get('task1', {}).get('top_products', [])
    answer_key_values = answer_key.get('task1', {}).get('top_products', [])
    
    points = 8
    correct_order = 0
    correct_products = 0
    
    # Check products in correct order
    for i, product_id in enumerate(answer_key_values):
        if i < len(submission_values) and submission_values[i] == product_id:
            correct_order += 1
    
    # Check correct products regardless of order
    submission_set = set(submission_values[:10])
    answer_key_set = set(answer_key_values[:10])
    correct_products = len(submission_set.intersection(answer_key_set))
    
    # Scoring: full points if at least 8 products match and are in correct order
    if correct_order >= 8:
        score = points
    else:
        # Partial credit for having correct products but wrong order
        order_score = (correct_order / 10) * (points * 0.7)  # 70% weight for correct order
        product_score = (correct_products / 10) * (points * 0.3)  # 30% weight for having correct products
        score = order_score + product_score
    
    return {
        "score": score,
        "max_points": points,
        "correct_order": correct_order,
        "correct_products": correct_products,
        "comments": f"Identified {correct_products}/10 correct products with {correct_order}/10 in correct order"
    }

def evaluate_seasonal_products(submission, answer_key):
    submission_values = set(submission.get('task1', {}).get('seasonal_products', []))
    answer_key_values = set(answer_key.get('task1', {}).get('seasonal_products', []))
    
    points = 7
    correct_identified = len(submission_values.intersection(answer_key_values))
    
    # Full points if at least 4 of 5 key seasonal products are identified
    if correct_identified >= 4:
        score = points
    else:
        # Partial points based on proportion identified
        score = (correct_identified / 5) * points
    
    return {
        "score": score,
        "max_points": points,
        "correct_identified": correct_identified,
        "comments": f"Correctly identified {correct_identified}/5 seasonal products"
    }

def evaluate_stock_coverage(submission, answer_key):
    submission_values = submission.get('task2', {}).get('stock_coverage', {})
    answer_key_values = answer_key.get('task2', {}).get('stock_coverage', {})
    
    points = 10
    errors = 0
    
    for product_id, correct_value in answer_key_values.items():
        if product_id not in submission_values:
            errors += 1
            continue
            
        submitted_value = submission_values.get(product_id, 0)
        if not isinstance(submitted_value, (int, float)):
            errors += 1
            continue
            
        # Check if within ±5% of correct value
        if abs(submitted_value - correct_value) > (correct_value * 0.05):
            errors += 1
    
    points_deducted = min(points, errors * 0.5)
    score = points - points_deducted
    
    return {
        "score": score,
        "max_points": points,
        "errors": errors,
        "comments": f"Found {errors} values outside the acceptable range (±5%)"
    }

def evaluate_low_inventory_products(submission, answer_key):
    submission_values = set(submission.get('task2', {}).get('low_inventory_products', []))
    answer_key_values = set(answer_key.get('task2', {}).get('low_inventory_products', []))
    
    points = 8
    incorrect = 0
    
    missing = answer_key_values - submission_values
    extra = submission_values - answer_key_values
    
    incorrect = len(missing) + len(extra)
    points_deducted = min(points, incorrect * 2)
    score = points - points_deducted
    
    return {
        "score": score,
        "max_points": points,
        "missing": list(missing),
        "extra": list(extra),
        "comments": f"Missing {len(missing)} required products, incorrectly included {len(extra)} products"
    }

def evaluate_excess_inventory_products(submission, answer_key):
    submission_values = set(submission.get('task2', {}).get('excess_inventory_products', []))
    answer_key_values = set(answer_key.get('task2', {}).get('excess_inventory_products', []))
    
    points = 7
    
    # The answer key says there are no excess inventory products
    if len(answer_key_values) == 0 and len(submission_values) == 0:
        score = points
        comments = "Correctly identified that there are no excess inventory products"
    else:
        score = 0
        comments = "Incorrectly identified products as excess when there should be none"
    
    return {
        "score": score,
        "max_points": points,
        "comments": comments
    }

def evaluate_recommended_order_quantities(submission, answer_key):
    submission_values = submission.get('task3', {}).get('recommended_order_quantities', {})
    answer_key_values = answer_key.get('task3', {}).get('recommended_order_quantities', {})
    
    points = 10
    errors = 0
    
    for product_id, correct_value in answer_key_values.items():
        if product_id not in submission_values:
            errors += 1
            continue
            
        submitted_value = submission_values.get(product_id, 0)
        if not isinstance(submitted_value, (int, float)):
            errors += 1
            continue
            
        # Check if within ±15% of correct value
        if abs(submitted_value - correct_value) > (correct_value * 0.15):
            errors += 1
    
    # Calculate score: full points if all recommendations are within range
    # Partial points based on proportion of correct recommendations
    total_products = len(answer_key_values)
    correct_products = total_products - errors
    score = (correct_products / total_products) * points
    
    return {
        "score": score,
        "max_points": points,
        "errors": errors,
        "comments": f"Found {errors}/{total_products} values outside the acceptable range (±15%)"
    }

def evaluate_order_frequency(submission, answer_key):
    submission_values = submission.get('task3', {}).get('order_frequency', {})
    answer_key_values = answer_key.get('task3', {}).get('order_frequency', {})
    
    points = 8
    correct = 0
    total = len(answer_key_values)
    
    for category, correct_value in answer_key_values.items():
        if category not in submission_values:
            continue
            
        submitted_value = submission_values.get(category, 0)
        if not isinstance(submitted_value, (int, float)):
            continue
            
        # Consider a match if exactly equal or within ±1 for reasonable variation
        if submitted_value == correct_value or abs(submitted_value - correct_value) <= 1:
            correct += 1
    
    score = (correct / total) * points
    
    return {
        "score": score,
        "max_points": points,
        "correct": correct,
        "total": total,
        "comments": f"Correctly determined order frequency for {correct}/{total} categories"
    }

def evaluate_quarterly_cost(submission, answer_key):
    submission_value = submission.get('task3', {}).get('quarterly_cost', 0)
    answer_key_value = answer_key.get('task3', {}).get('quarterly_cost', 0)
    
    points = 7
    
    if not isinstance(submission_value, (int, float)):
        score = 0
        comments = "Invalid quarterly cost value"
    else:
        # Full points if within ±10% of correct value
        percentage_diff = abs(submission_value - answer_key_value) / answer_key_value
        
        if percentage_diff <= 0.10:
            score = points
            comments = f"Quarterly cost within acceptable range of correct value"
        else:
            # Scale points based on how far off the estimate is
            score_multiplier = max(0, 1 - (percentage_diff - 0.10) * 2)  # Lose points more rapidly beyond 10%
            score = points * score_multiplier
            comments = f"Quarterly cost outside acceptable range (±10%), off by {percentage_diff:.1%}"
    
    return {
        "score": score,
        "max_points": points,
        "submitted_value": submission_value,
        "correct_value": answer_key_value,
        "comments": comments
    }

def evaluate_critical_products(submission, answer_key):
    submission_values = submission.get('task4', {}).get('critical_products', {})
    answer_key_values = answer_key.get('task4', {}).get('critical_products', {})
    
    points = 8
    errors = 0
    departments_evaluated = 0
    
    for dept_id, correct_products in answer_key_values.items():
        departments_evaluated += 1
        if dept_id not in submission_values:
            errors += 1
            continue
            
        submitted_products = set(submission_values.get(dept_id, []))
        correct_products_set = set(correct_products)
        
        if submitted_products != correct_products_set:
            errors += 1
    
    points_deducted = min(points, errors)
    score = points - points_deducted
    
    return {
        "score": score,
        "max_points": points,
        "errors": errors,
        "departments_evaluated": departments_evaluated,
        "comments": f"Found errors in {errors}/{departments_evaluated} departments' critical product lists"
    }

def evaluate_service_levels(submission, answer_key):
    submission_values = submission.get('task4', {}).get('service_levels', {})
    answer_key_values = answer_key.get('task4', {}).get('service_levels', {})
    
    points = 8
    errors = 0
    total_products = len(answer_key_values)
    
    for product_id, correct_value in answer_key_values.items():
        if product_id not in submission_values:
            errors += 1
            continue
            
        submitted_value = submission_values.get(product_id, 0)
        if not isinstance(submitted_value, (int, float)):
            errors += 1
            continue
            
        # Service levels should be within a reasonable range (±3%)
        if abs(submitted_value - correct_value) > 3:
            errors += 1
    
    correct_products = total_products - errors
    score = (correct_products / total_products) * points
    
    return {
        "score": score,
        "max_points": points,
        "correct": correct_products,
        "total": total_products,
        "comments": f"Service levels appropriate for {correct_products}/{total_products} products"
    }

def evaluate_safety_stock_adjustments(submission, answer_key):
    submission_values = submission.get('task4', {}).get('safety_stock_adjustments', {})
    answer_key_values = answer_key.get('task4', {}).get('safety_stock_adjustments', {})
    
    points = 9
    errors = 0
    total_products = len(answer_key_values)
    
    for product_id, correct_value in answer_key_values.items():
        if product_id not in submission_values:
            errors += 1
            continue
            
        submitted_value = submission_values.get(product_id, 0)
        if not isinstance(submitted_value, (int, float)):
            errors += 1
            continue
            
        # Safety stock should be within a reasonable range (±30%)
        if abs(submitted_value - correct_value) > (correct_value * 0.3):
            errors += 1
    
    correct_products = total_products - errors
    score = (correct_products / total_products) * points
    
    return {
        "score": score,
        "max_points": points,
        "correct": correct_products,
        "total": total_products,
        "comments": f"Safety stock adjustments appropriate for {correct_products}/{total_products} products"
    }

def evaluate_submission(submission, answer_key):
    results = {
        "task1": {
            "average_monthly_consumption": evaluate_average_monthly_consumption(submission, answer_key),
            "top_products": evaluate_top_products(submission, answer_key),
            "seasonal_products": evaluate_seasonal_products(submission, answer_key)
        },
        "task2": {
            "stock_coverage": evaluate_stock_coverage(submission, answer_key),
            "low_inventory_products": evaluate_low_inventory_products(submission, answer_key),
            "excess_inventory_products": evaluate_excess_inventory_products(submission, answer_key)
        },
        "task3": {
            "recommended_order_quantities": evaluate_recommended_order_quantities(submission, answer_key),
            "order_frequency": evaluate_order_frequency(submission, answer_key),
            "quarterly_cost": evaluate_quarterly_cost(submission, answer_key)
        },
        "task4": {
            "critical_products": evaluate_critical_products(submission, answer_key),
            "service_levels": evaluate_service_levels(submission, answer_key),
            "safety_stock_adjustments": evaluate_safety_stock_adjustments(submission, answer_key)
        }
    }
    
    # Calculate total score
    total_points = 0
    max_points = 0
    
    for task, subtasks in results.items():
        for subtask, evaluation in subtasks.items():
            total_points += evaluation["score"]
            max_points += evaluation["max_points"]
    
    # Calculate percentage
    percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    
    # Add overall score to results
    results["overall_score"] = round(percentage, 2)
    results["total_points"] = total_points
    results["max_points"] = max_points
    results["passed"] = percentage >= 75
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as results_file:
        json.dump(evaluation_results, results_file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {evaluation_results['overall_score']}%")
    print(f"Result: {'PASSED' if evaluation_results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()