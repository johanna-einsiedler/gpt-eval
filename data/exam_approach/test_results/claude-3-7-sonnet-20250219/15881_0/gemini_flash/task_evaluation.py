#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_data_analysis(submission, answer_key):
    """Evaluate the data analysis section."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "details": {}
    }
    
    # Evaluate excess_inventory_skus (10 points)
    correct_skus = set(answer_key["excess_inventory_skus"])
    submitted_skus = set(submission.get("excess_inventory_skus", []))
    
    # Calculate points based on correct SKUs identified
    correct_count = len(correct_skus.intersection(submitted_skus))
    if len(submitted_skus) > 10:
        # Penalize for submitting more than 10 SKUs
        excess_points = max(0, min(10, correct_count - (len(submitted_skus) - 10)))
    else:
        excess_points = (correct_count / 10) * 10
    
    results["details"]["excess_inventory_skus"] = {
        "points_earned": excess_points,
        "points_possible": 10,
        "correct_answer": answer_key["excess_inventory_skus"],
        "submitted_answer": submission.get("excess_inventory_skus", []),
        "comments": f"Identified {correct_count} out of 10 correct SKUs."
    }
    results["points_earned"] += excess_points
    
    # Evaluate high_days_supply_count (5 points)
    correct_count = answer_key["high_days_supply_count"]
    submitted_count = submission.get("high_days_supply_count", 0)
    
    if submitted_count == correct_count:
        high_days_points = 5
    else:
        high_days_points = 0
    
    results["details"]["high_days_supply_count"] = {
        "points_earned": high_days_points,
        "points_possible": 5,
        "correct_answer": correct_count,
        "submitted_answer": submitted_count,
        "comments": "Correct" if high_days_points == 5 else "Incorrect count"
    }
    results["points_earned"] += high_days_points
    
    # Evaluate obsolete_inventory_skus (5 points)
    correct_obsolete = set(answer_key["obsolete_inventory_skus"])
    submitted_obsolete = set(submission.get("obsolete_inventory_skus", []))
    
    # Calculate points based on correct obsolete SKUs identified
    correct_obsolete_count = len(correct_obsolete.intersection(submitted_obsolete))
    incorrect_obsolete_count = len(submitted_obsolete - correct_obsolete)
    
    if len(correct_obsolete) > 0:
        obsolete_points = (correct_obsolete_count / len(correct_obsolete)) * 5
        # Penalize for incorrect SKUs
        obsolete_points = max(0, obsolete_points - (incorrect_obsolete_count / len(correct_obsolete)) * 2.5)
    else:
        obsolete_points = 5 if len(submitted_obsolete) == 0 else 0
    
    results["details"]["obsolete_inventory_skus"] = {
        "points_earned": obsolete_points,
        "points_possible": 5,
        "correct_answer": answer_key["obsolete_inventory_skus"],
        "submitted_answer": submission.get("obsolete_inventory_skus", []),
        "comments": f"Identified {correct_obsolete_count} out of {len(correct_obsolete)} correct obsolete SKUs."
    }
    results["points_earned"] += obsolete_points
    
    # Evaluate total_excess_value (10 points)
    correct_value = answer_key["total_excess_value"]
    submitted_value = submission.get("total_excess_value", 0)
    
    # Calculate points based on how close the value is (within 5% is full credit, within 10% is half credit)
    if abs(submitted_value - correct_value) <= correct_value * 0.05:
        value_points = 10
    elif abs(submitted_value - correct_value) <= correct_value * 0.10:
        value_points = 5
    else:
        value_points = 0
    
    results["details"]["total_excess_value"] = {
        "points_earned": value_points,
        "points_possible": 10,
        "correct_answer": correct_value,
        "submitted_answer": submitted_value,
        "comments": "Within 5% of correct value" if value_points == 10 else 
                    "Within 10% of correct value" if value_points == 5 else
                    "More than 10% deviation from correct value"
    }
    results["points_earned"] += value_points
    
    return results

def evaluate_root_causes(submission, answer_key):
    """Evaluate the root causes section."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "details": {}
    }
    
    # Each scenario is worth 6 points
    for i in range(1, 6):
        scenario_key = f"scenario{i}"
        correct_answer = answer_key.get(scenario_key, "")
        submitted_answer = submission.get(scenario_key, "")
        
        points = 6 if correct_answer == submitted_answer else 0
        
        results["details"][scenario_key] = {
            "points_earned": points,
            "points_possible": 6,
            "correct_answer": correct_answer,
            "submitted_answer": submitted_answer,
            "comments": "Correct" if points == 6 else "Incorrect"
        }
        results["points_earned"] += points
    
    return results

def evaluate_reduction_strategies(submission, answer_key):
    """Evaluate the reduction strategies section."""
    results = {
        "points_earned": 0,
        "points_possible": 40,
        "details": {}
    }
    
    # Evaluate potential_value_reduction (10 points)
    correct_value = answer_key["potential_value_reduction"]
    submitted_value = submission.get("potential_value_reduction", 0)
    
    # Calculate points based on how close the value is (within 5% is full credit, within 10% is half credit)
    if abs(submitted_value - correct_value) <= correct_value * 0.05:
        value_points = 10
    elif abs(submitted_value - correct_value) <= correct_value * 0.10:
        value_points = 5
    else:
        value_points = 0
    
    results["details"]["potential_value_reduction"] = {
        "points_earned": value_points,
        "points_possible": 10,
        "correct_answer": correct_value,
        "submitted_answer": submitted_value,
        "comments": "Within 5% of correct value" if value_points == 10 else 
                    "Within 10% of correct value" if value_points == 5 else
                    "More than 10% deviation from correct value"
    }
    results["points_earned"] += value_points
    
    # Evaluate top_opportunity_skus (10 points)
    correct_skus = set(answer_key["top_opportunity_skus"])
    submitted_skus = set(submission.get("top_opportunity_skus", []))
    
    # Calculate points based on correct SKUs identified
    correct_count = len(correct_skus.intersection(submitted_skus))
    if len(submitted_skus) > 5:
        # Penalize for submitting more than 5 SKUs
        opportunity_points = max(0, min(10, (correct_count / 5) * 10 - (len(submitted_skus) - 5) * 2))
    else:
        opportunity_points = (correct_count / 5) * 10
    
    results["details"]["top_opportunity_skus"] = {
        "points_earned": opportunity_points,
        "points_possible": 10,
        "correct_answer": answer_key["top_opportunity_skus"],
        "submitted_answer": submission.get("top_opportunity_skus", []),
        "comments": f"Identified {correct_count} out of 5 correct opportunity SKUs."
    }
    results["points_earned"] += opportunity_points
    
    # Evaluate slow_moving_strategies (15 points, 3 points per SKU)
    correct_strategies = answer_key["slow_moving_strategies"]
    submitted_strategies = submission.get("slow_moving_strategies", {})
    
    strategy_points = 0
    strategy_details = {}
    
    for sku, correct_strategy in correct_strategies.items():
        submitted_strategy = submitted_strategies.get(sku, "")
        sku_points = 3 if submitted_strategy == correct_strategy else 0
        
        strategy_details[sku] = {
            "points_earned": sku_points,
            "points_possible": 3,
            "correct_answer": correct_strategy,
            "submitted_answer": submitted_strategy,
            "comments": "Correct" if sku_points == 3 else "Incorrect"
        }
        strategy_points += sku_points
    
    results["details"]["slow_moving_strategies"] = {
        "points_earned": strategy_points,
        "points_possible": 15,
        "details": strategy_details,
        "comments": f"Correctly matched {strategy_points/3} out of 5 strategies."
    }
    results["points_earned"] += strategy_points
    
    # Evaluate carrying_cost_savings (5 points)
    correct_savings = answer_key["carrying_cost_savings"]
    submitted_savings = submission.get("carrying_cost_savings", 0)
    
    # Calculate points based on how close the value is (within 5% is full credit, within 10% is half credit)
    if abs(submitted_savings - correct_savings) <= correct_savings * 0.05:
        savings_points = 5
    elif abs(submitted_savings - correct_savings) <= correct_savings * 0.10:
        savings_points = 2.5
    else:
        savings_points = 0
    
    results["details"]["carrying_cost_savings"] = {
        "points_earned": savings_points,
        "points_possible": 5,
        "correct_answer": correct_savings,
        "submitted_answer": submitted_savings,
        "comments": "Within 5% of correct value" if savings_points == 5 else 
                    "Within 10% of correct value" if savings_points == 2.5 else
                    "More than 10% deviation from correct value"
    }
    results["points_earned"] += savings_points
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    results = {
        "overall_score": 0,
        "total_points_earned": 0,
        "total_points_possible": 100,
        "sections": {}
    }
    
    # Evaluate data analysis section
    data_analysis_results = evaluate_data_analysis(
        submission.get("data_analysis", {}), 
        answer_key.get("data_analysis", {})
    )
    results["sections"]["data_analysis"] = data_analysis_results
    results["total_points_earned"] += data_analysis_results["points_earned"]
    
    # Evaluate root causes section
    root_causes_results = evaluate_root_causes(
        submission.get("root_causes", {}), 
        answer_key.get("root_causes", {})
    )
    results["sections"]["root_causes"] = root_causes_results
    results["total_points_earned"] += root_causes_results["points_earned"]
    
    # Evaluate reduction strategies section
    reduction_strategies_results = evaluate_reduction_strategies(
        submission.get("reduction_strategies", {}), 
        answer_key.get("reduction_strategies", {})
    )
    results["sections"]["reduction_strategies"] = reduction_strategies_results
    results["total_points_earned"] += reduction_strategies_results["points_earned"]
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points_earned"] / results["total_points_possible"]) * 100
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
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

if __name__ == "__main__":
    main()