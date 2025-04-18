import json
import sys
import math

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {str(e)}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    results = {
        "points_possible": 30,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Check lowest total cost supplier (10 points)
    if submission.get("lowest_total_cost_supplier") == answer_key.get("lowest_total_cost_supplier"):
        results["breakdown"]["lowest_total_cost_supplier"] = {
            "correct": True,
            "points_earned": 10,
            "points_possible": 10,
            "submitted_answer": submission.get("lowest_total_cost_supplier"),
            "correct_answer": answer_key.get("lowest_total_cost_supplier")
        }
        results["points_earned"] += 10
    else:
        results["breakdown"]["lowest_total_cost_supplier"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 10,
            "submitted_answer": submission.get("lowest_total_cost_supplier"),
            "correct_answer": answer_key.get("lowest_total_cost_supplier")
        }
    
    # Check high variance items (10 points - 5 per item)
    submitted_high_variance = set(submission.get("high_variance_items", []))
    correct_high_variance = set(answer_key.get("high_variance_items", []))
    
    common_items = submitted_high_variance.intersection(correct_high_variance)
    points_earned = len(common_items) * 5
    
    results["breakdown"]["high_variance_items"] = {
        "correct": submitted_high_variance == correct_high_variance,
        "points_earned": points_earned,
        "points_possible": 10,
        "submitted_answer": list(submitted_high_variance),
        "correct_answer": list(correct_high_variance),
        "common_items": list(common_items)
    }
    results["points_earned"] += points_earned
    
    # Check supplier with most lowest prices (5 points)
    if submission.get("supplier_with_most_lowest_prices") == answer_key.get("supplier_with_most_lowest_prices"):
        results["breakdown"]["supplier_with_most_lowest_prices"] = {
            "correct": True,
            "points_earned": 5,
            "points_possible": 5,
            "submitted_answer": submission.get("supplier_with_most_lowest_prices"),
            "correct_answer": answer_key.get("supplier_with_most_lowest_prices")
        }
        results["points_earned"] += 5
    else:
        results["breakdown"]["supplier_with_most_lowest_prices"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("supplier_with_most_lowest_prices"),
            "correct_answer": answer_key.get("supplier_with_most_lowest_prices")
        }
    
    # Check count of lowest prices (5 points)
    if submission.get("count_of_lowest_prices") == answer_key.get("count_of_lowest_prices"):
        results["breakdown"]["count_of_lowest_prices"] = {
            "correct": True,
            "points_earned": 5,
            "points_possible": 5,
            "submitted_answer": submission.get("count_of_lowest_prices"),
            "correct_answer": answer_key.get("count_of_lowest_prices")
        }
        results["points_earned"] += 5
    else:
        results["breakdown"]["count_of_lowest_prices"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("count_of_lowest_prices"),
            "correct_answer": answer_key.get("count_of_lowest_prices")
        }
    
    return results

def evaluate_task2(submission, answer_key):
    results = {
        "points_possible": 35,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Check price changes (10 points - 2 per material)
    submitted_price_changes = submission.get("price_changes", {})
    correct_price_changes = answer_key.get("price_changes", {})
    
    price_change_points = 0
    price_change_details = {}
    
    for material in correct_price_changes:
        if material in submitted_price_changes:
            submitted_value = submitted_price_changes[material]
            correct_value = correct_price_changes[material]
            
            # Within tolerance of ±0.2%
            if abs(submitted_value - correct_value) <= 0.2:
                price_change_points += 2
                is_correct = True
            else:
                is_correct = False
            
            price_change_details[material] = {
                "correct": is_correct,
                "points_earned": 2 if is_correct else 0,
                "points_possible": 2,
                "submitted_answer": submitted_value,
                "correct_answer": correct_value
            }
        else:
            price_change_details[material] = {
                "correct": False,
                "points_earned": 0,
                "points_possible": 2,
                "submitted_answer": None,
                "correct_answer": correct_price_changes[material]
            }
    
    results["breakdown"]["price_changes"] = {
        "correct": price_change_points == 10,
        "points_earned": price_change_points,
        "points_possible": 10,
        "details": price_change_details
    }
    results["points_earned"] += price_change_points
    
    # Check most stable material (10 points)
    if submission.get("most_stable_material") == answer_key.get("most_stable_material"):
        results["breakdown"]["most_stable_material"] = {
            "correct": True,
            "points_earned": 10,
            "points_possible": 10,
            "submitted_answer": submission.get("most_stable_material"),
            "correct_answer": answer_key.get("most_stable_material")
        }
        results["points_earned"] += 10
    else:
        results["breakdown"]["most_stable_material"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 10,
            "submitted_answer": submission.get("most_stable_material"),
            "correct_answer": answer_key.get("most_stable_material")
        }
    
    # Check average prices (10 points - 2 per material)
    submitted_avg_prices = submission.get("average_prices", {})
    correct_avg_prices = answer_key.get("average_prices", {})
    
    avg_price_points = 0
    avg_price_details = {}
    
    for material in correct_avg_prices:
        if material in submitted_avg_prices:
            submitted_value = submitted_avg_prices[material]
            correct_value = correct_avg_prices[material]
            
            # Within tolerance of ±0.05
            if abs(submitted_value - correct_value) <= 0.05:
                avg_price_points += 2
                is_correct = True
            else:
                is_correct = False
            
            avg_price_details[material] = {
                "correct": is_correct,
                "points_earned": 2 if is_correct else 0,
                "points_possible": 2,
                "submitted_answer": submitted_value,
                "correct_answer": correct_value
            }
        else:
            avg_price_details[material] = {
                "correct": False,
                "points_earned": 0,
                "points_possible": 2,
                "submitted_answer": None,
                "correct_answer": correct_avg_prices[material]
            }
    
    results["breakdown"]["average_prices"] = {
        "correct": avg_price_points == 10,
        "points_earned": avg_price_points,
        "points_possible": 10,
        "details": avg_price_details
    }
    results["points_earned"] += avg_price_points
    
    # Check highest price quarter (5 points)
    if submission.get("highest_price_quarter") == answer_key.get("highest_price_quarter"):
        results["breakdown"]["highest_price_quarter"] = {
            "correct": True,
            "points_earned": 5,
            "points_possible": 5,
            "submitted_answer": submission.get("highest_price_quarter"),
            "correct_answer": answer_key.get("highest_price_quarter")
        }
        results["points_earned"] += 5
    else:
        results["breakdown"]["highest_price_quarter"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("highest_price_quarter"),
            "correct_answer": answer_key.get("highest_price_quarter")
        }
    
    return results

def evaluate_task3(submission, answer_key):
    results = {
        "points_possible": 35,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Check above market components (10 points - 5 per component)
    submitted_components = set(submission.get("above_market_components", []))
    correct_components = set(answer_key.get("above_market_components", []))
    
    common_components = submitted_components.intersection(correct_components)
    points_earned = len(common_components) * 5
    
    results["breakdown"]["above_market_components"] = {
        "correct": submitted_components == correct_components,
        "points_earned": points_earned,
        "points_possible": 10,
        "submitted_answer": list(submitted_components),
        "correct_answer": list(correct_components),
        "common_components": list(common_components)
    }
    results["points_earned"] += points_earned
    
    # Check benchmark adjusted price (10 points)
    if "benchmark_adjusted_price" in submission and "benchmark_adjusted_price" in answer_key:
        submitted_price = submission["benchmark_adjusted_price"]
        correct_price = answer_key["benchmark_adjusted_price"]
        
        # Within tolerance of ±0.5
        if abs(submitted_price - correct_price) <= 0.5:
            price_points = 10
            price_correct = True
        else:
            price_points = 0
            price_correct = False
        
        results["breakdown"]["benchmark_adjusted_price"] = {
            "correct": price_correct,
            "points_earned": price_points,
            "points_possible": 10,
            "submitted_answer": submitted_price,
            "correct_answer": correct_price
        }
        results["points_earned"] += price_points
    else:
        results["breakdown"]["benchmark_adjusted_price"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 10,
            "submitted_answer": submission.get("benchmark_adjusted_price"),
            "correct_answer": answer_key.get("benchmark_adjusted_price")
        }
    
    # Check savings percentage (5 points)
    if "savings_percentage" in submission and "savings_percentage" in answer_key:
        submitted_savings = submission["savings_percentage"]
        correct_savings = answer_key["savings_percentage"]
        
        # Within tolerance of ±0.2%
        if abs(submitted_savings - correct_savings) <= 0.2:
            savings_points = 5
            savings_correct = True
        else:
            savings_points = 0
            savings_correct = False
        
        results["breakdown"]["savings_percentage"] = {
            "correct": savings_correct,
            "points_earned": savings_points,
            "points_possible": 5,
            "submitted_answer": submitted_savings,
            "correct_answer": correct_savings
        }
        results["points_earned"] += savings_points
    else:
        results["breakdown"]["savings_percentage"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("savings_percentage"),
            "correct_answer": answer_key.get("savings_percentage")
        }
    
    # Check materials percentage (5 points)
    if "materials_percentage" in submission and "materials_percentage" in answer_key:
        submitted_materials = submission["materials_percentage"]
        correct_materials = answer_key["materials_percentage"]
        
        # Within tolerance of ±0.5%
        if abs(submitted_materials - correct_materials) <= 0.5:
            materials_points = 5
            materials_correct = True
        else:
            materials_points = 0
            materials_correct = False
        
        results["breakdown"]["materials_percentage"] = {
            "correct": materials_correct,
            "points_earned": materials_points,
            "points_possible": 5,
            "submitted_answer": submitted_materials,
            "correct_answer": correct_materials
        }
        results["points_earned"] += materials_points
    else:
        results["breakdown"]["materials_percentage"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("materials_percentage"),
            "correct_answer": answer_key.get("materials_percentage")
        }
    
    # Check labor percentage (5 points)
    if "labor_percentage" in submission and "labor_percentage" in answer_key:
        submitted_labor = submission["labor_percentage"]
        correct_labor = answer_key["labor_percentage"]
        
        # Within tolerance of ±0.5%
        if abs(submitted_labor - correct_labor) <= 0.5:
            labor_points = 5
            labor_correct = True
        else:
            labor_points = 0
            labor_correct = False
        
        results["breakdown"]["labor_percentage"] = {
            "correct": labor_correct,
            "points_earned": labor_points,
            "points_possible": 5,
            "submitted_answer": submitted_labor,
            "correct_answer": correct_labor
        }
        results["points_earned"] += labor_points
    else:
        results["breakdown"]["labor_percentage"] = {
            "correct": False,
            "points_earned": 0,
            "points_possible": 5,
            "submitted_answer": submission.get("labor_percentage"),
            "correct_answer": answer_key.get("labor_percentage")
        }
    
    return results

def check_automatic_failure(evaluation_results, submission, answer_key):
    failure_conditions = []
    
    # Check for missing required answers
    required_sections = ["task1", "task2", "task3"]
    for section in required_sections:
        if section not in submission:
            failure_conditions.append(f"Missing required section: {section}")
    
    # Check if incorrect supplier identified as having lowest total cost
    if "task1" in submission and "task1" in answer_key:
        if submission["task1"].get("lowest_total_cost_supplier") != answer_key["task1"].get("lowest_total_cost_supplier"):
            failure_conditions.append("Identified incorrect supplier as having lowest total cost")
    
    # Check if missing more than one high variance item
    if "task1" in submission and "task1" in answer_key:
        submitted_high_variance = set(submission["task1"].get("high_variance_items", []))
        correct_high_variance = set(answer_key["task1"].get("high_variance_items", []))
        common_items = submitted_high_variance.intersection(correct_high_variance)
        
        if len(correct_high_variance) - len(common_items) > 1:
            failure_conditions.append("Missing more than one high variance item")
    
    # Check if incorrect most stable material identified
    if "task2" in submission and "task2" in answer_key:
        if submission["task2"].get("most_stable_material") != answer_key["task2"].get("most_stable_material"):
            failure_conditions.append("Identified incorrect most stable material")
    
    return failure_conditions

def evaluate_exam(submission_data, answer_key_data):
    # Extract task data
    submission_task1 = submission_data.get("task1", {})
    submission_task2 = submission_data.get("task2", {})
    submission_task3 = submission_data.get("task3", {})
    
    answer_key_task1 = answer_key_data.get("task1", {})
    answer_key_task2 = answer_key_data.get("task2", {})
    answer_key_task3 = answer_key_data.get("task3", {})
    
    # Evaluate each task
    task1_results = evaluate_task1(submission_task1, answer_key_task1)
    task2_results = evaluate_task2(submission_task2, answer_key_task2)
    task3_results = evaluate_task3(submission_task3, answer_key_task3)
    
    # Calculate overall score
    total_points_possible = task1_results["points_possible"] + task2_results["points_possible"] + task3_results["points_possible"]
    total_points_earned = task1_results["points_earned"] + task2_results["points_earned"] + task3_results["points_earned"]
    overall_score = (total_points_earned / total_points_possible) * 100 if total_points_possible > 0 else 0
    
    # Check for automatic failure conditions
    failure_conditions = check_automatic_failure({
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    }, submission_data, answer_key_data)
    
    # Determine if passed (70% threshold and no automatic failure conditions)
    passed = overall_score >= 70 and not failure_conditions
    
    # Create final results
    results = {
        "candidate_id": submission_data.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 1),
        "total_points_earned": total_points_earned,
        "total_points_possible": total_points_possible,
        "passed": passed,
        "failure_conditions": failure_conditions,
        "task_results": {
            "task1": task1_results,
            "task2": task2_results,
            "task3": task3_results
        }
    }
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission_data = load_json_file(submission_file)
    answer_key_data = load_json_file(answer_key_file)
    
    # Evaluate exam
    results = evaluate_exam(submission_data, answer_key_data)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    if results['passed']:
        print("Status: PASSED")
    else:
        print("Status: FAILED")
        if results['failure_conditions']:
            print("Failure conditions:")
            for condition in results['failure_conditions']:
                print(f"- {condition}")

if __name__ == "__main__":
    main()