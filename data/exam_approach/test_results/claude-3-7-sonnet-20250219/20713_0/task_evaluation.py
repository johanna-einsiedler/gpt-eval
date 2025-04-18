#!/usr/bin/env python3
"""
Evaluation script for the Wholesale and Retail Buyers pricing practical exam.
This script compares a candidate's submission against an answer key and produces
a detailed scoring report.
"""

import json
import sys
import math
from typing import Dict, Any, Tuple, List


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def is_close(candidate_value: float, answer_value: float, tolerance: float = 0.01) -> Tuple[bool, float]:
    """
    Check if candidate value is close to the answer value within tolerance.
    Returns (is_exact_match, percentage_of_points)
    """
    if candidate_value is None or answer_value is None:
        return False, 0
    
    # Check for exact match (rounding to handle floating point issues)
    if round(candidate_value, 2) == round(answer_value, 2):
        return True, 1.0
    
    # Calculate percentage difference
    difference = abs(candidate_value - answer_value)
    relative_diff = difference / max(abs(answer_value), 0.001)  # Avoid division by zero
    
    # Assign partial credit
    if relative_diff <= 0.01:  # Within 1%
        return False, 0.8
    elif relative_diff <= 0.03:  # Within 3%
        return False, 0.5
    else:
        return False, 0.0


def evaluate_text_answer(candidate_text: str, expected_length: int = 30) -> float:
    """
    Evaluate a text answer (justification or explanation).
    Returns percentage of points based on answer completeness.
    """
    if not candidate_text:
        return 0.0
    
    # Basic assessment based on length (as a proxy for completeness)
    # In a real scenario, this would be more sophisticated
    if len(candidate_text) >= expected_length:
        return 1.0
    elif len(candidate_text) >= expected_length // 2:
        return 0.75
    elif len(candidate_text) >= expected_length // 4:
        return 0.5
    else:
        return 0.25


def evaluate_task1(candidate: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 1: Mark-up Calculation"""
    results = {"points_earned": 0, "points_possible": 25, "product_scores": {}}
    points_per_product = 5
    
    for product in ["product_A", "product_B", "product_C", "product_D", "product_E"]:
        product_score = {"points_earned": 0, "points_possible": points_per_product, "details": {}}
        
        # Cost-based markup (1 point)
        exact_match, credit = is_close(
            candidate["task1_markup_calculation"][product]["cost_based_markup_percent"],
            answer_key["task1_markup_calculation"][product]["cost_based_markup_percent"]
        )
        markup_points = 1 * credit
        product_score["details"]["cost_based_markup"] = {
            "points_earned": markup_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Retail-based markup (1 point)
        exact_match, credit = is_close(
            candidate["task1_markup_calculation"][product]["retail_based_markup_percent"],
            answer_key["task1_markup_calculation"][product]["retail_based_markup_percent"]
        )
        retail_markup_points = 1 * credit
        product_score["details"]["retail_based_markup"] = {
            "points_earned": retail_markup_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Recommended selling price (2 points)
        exact_match, credit = is_close(
            candidate["task1_markup_calculation"][product]["recommended_selling_price"],
            answer_key["task1_markup_calculation"][product]["recommended_selling_price"]
        )
        price_points = 2 * credit
        product_score["details"]["recommended_price"] = {
            "points_earned": price_points,
            "points_possible": 2,
            "exact_match": exact_match
        }
        
        # Justification (1 point)
        justification_credit = evaluate_text_answer(
            candidate["task1_markup_calculation"][product]["justification"]
        )
        justification_points = 1 * justification_credit
        product_score["details"]["justification"] = {
            "points_earned": justification_points,
            "points_possible": 1,
            "quality": justification_credit
        }
        
        # Sum up points for this product
        product_score["points_earned"] = markup_points + retail_markup_points + price_points + justification_points
        results["points_earned"] += product_score["points_earned"]
        results["product_scores"][product] = product_score
    
    return results


def evaluate_task2(candidate: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 2: Markdown Strategy"""
    results = {"points_earned": 0, "points_possible": 25, "product_scores": {}}
    points_per_product = 25/3  # Approximately 8.33 points per product
    
    for product in ["product_F", "product_G", "product_H"]:
        product_score = {"points_earned": 0, "points_possible": points_per_product, "details": {}}
        
        # Required markdown percentage (3 points)
        exact_match, credit = is_close(
            candidate["task2_markdown_strategy"][product]["required_markdown_percent"],
            answer_key["task2_markdown_strategy"][product]["required_markdown_percent"]
        )
        markdown_points = 3 * credit
        product_score["details"]["required_markdown_percent"] = {
            "points_earned": markdown_points,
            "points_possible": 3,
            "exact_match": exact_match
        }
        
        # Recommended markdown price (3 points)
        exact_match, credit = is_close(
            candidate["task2_markdown_strategy"][product]["recommended_markdown_price"],
            answer_key["task2_markdown_strategy"][product]["recommended_markdown_price"]
        )
        price_points = 3 * credit
        product_score["details"]["recommended_markdown_price"] = {
            "points_earned": price_points,
            "points_possible": 3,
            "exact_match": exact_match
        }
        
        # Units expected to sell (1 point)
        exact_match = candidate["task2_markdown_strategy"][product]["units_expected_to_sell"] == answer_key["task2_markdown_strategy"][product]["units_expected_to_sell"]
        units_points = 1 if exact_match else 0
        product_score["details"]["units_expected_to_sell"] = {
            "points_earned": units_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Justification (1.33 points)
        justification_credit = evaluate_text_answer(
            candidate["task2_markdown_strategy"][product]["justification"]
        )
        justification_points = 1.33 * justification_credit
        product_score["details"]["justification"] = {
            "points_earned": justification_points,
            "points_possible": 1.33,
            "quality": justification_credit
        }
        
        # Sum up points for this product
        product_score["points_earned"] = markdown_points + price_points + units_points + justification_points
        results["points_earned"] += product_score["points_earned"]
        results["product_scores"][product] = product_score
    
    return results


def evaluate_task3(candidate: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 3: Competitive Price Positioning"""
    results = {"points_earned": 0, "points_possible": 25, "product_scores": {}}
    points_per_product = 6.25  # 25/4 points per product
    
    for product in ["product_I", "product_J", "product_K", "product_L"]:
        product_score = {"points_earned": 0, "points_possible": points_per_product, "details": {}}
        
        # Competitor average price (1 point)
        exact_match, credit = is_close(
            candidate["task3_competitive_pricing"][product]["competitor_average_price"],
            answer_key["task3_competitive_pricing"][product]["competitor_average_price"]
        )
        avg_price_points = 1 * credit
        product_score["details"]["competitor_average_price"] = {
            "points_earned": avg_price_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Recommended price (2 points)
        exact_match, credit = is_close(
            candidate["task3_competitive_pricing"][product]["recommended_price"],
            answer_key["task3_competitive_pricing"][product]["recommended_price"]
        )
        rec_price_points = 2 * credit
        product_score["details"]["recommended_price"] = {
            "points_earned": rec_price_points,
            "points_possible": 2,
            "exact_match": exact_match
        }
        
        # Percent difference from average (1 point)
        exact_match, credit = is_close(
            candidate["task3_competitive_pricing"][product]["percent_difference_from_average"],
            answer_key["task3_competitive_pricing"][product]["percent_difference_from_average"]
        )
        diff_points = 1 * credit
        product_score["details"]["percent_difference_from_average"] = {
            "points_earned": diff_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Achieved margin percent (1 point)
        exact_match, credit = is_close(
            candidate["task3_competitive_pricing"][product]["achieved_margin_percent"],
            answer_key["task3_competitive_pricing"][product]["achieved_margin_percent"]
        )
        margin_points = 1 * credit
        product_score["details"]["achieved_margin_percent"] = {
            "points_earned": margin_points,
            "points_possible": 1,
            "exact_match": exact_match
        }
        
        # Justification (1.25 points)
        justification_credit = evaluate_text_answer(
            candidate["task3_competitive_pricing"][product]["justification"]
        )
        justification_points = 1.25 * justification_credit
        product_score["details"]["justification"] = {
            "points_earned": justification_points,
            "points_possible": 1.25,
            "quality": justification_credit
        }
        
        # Sum up points for this product
        product_score["points_earned"] = avg_price_points + rec_price_points + diff_points + margin_points + justification_points
        results["points_earned"] += product_score["points_earned"]
        results["product_scores"][product] = product_score
    
    return results


def evaluate_task4(candidate: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 4: Margin Analysis and Price Adjustment"""
    results = {"points_earned": 0, "points_possible": 25, "product_scores": {}}
    points_per_product = 6.25  # 25/4 points per product
    
    for product in ["product_M", "product_N", "product_O", "product_P"]:
        product_score = {"points_earned": 0, "points_possible": points_per_product, "details": {}}
        
        # Required price adjustment percent (2 points)
        exact_match, credit = is_close(
            candidate["task4_margin_adjustment"][product]["required_price_adjustment_percent"],
            answer_key["task4_margin_adjustment"][product]["required_price_adjustment_percent"]
        )
        adjustment_points = 2 * credit
        product_score["details"]["required_price_adjustment_percent"] = {
            "points_earned": adjustment_points,
            "points_possible": 2,
            "exact_match": exact_match
        }
        
        # New recommended price (2 points)
        exact_match, credit = is_close(
            candidate["task4_margin_adjustment"][product]["new_recommended_price"],
            answer_key["task4_margin_adjustment"][product]["new_recommended_price"]
        )
        price_points = 2 * credit
        product_score["details"]["new_recommended_price"] = {
            "points_earned": price_points,
            "points_possible": 2,
            "exact_match": exact_match
        }
        
        # Expected impact on sales (1 point)
        impact_credit = evaluate_text_answer(
            candidate["task4_margin_adjustment"][product]["expected_impact_on_sales"]
        )
        impact_points = 1 * impact_credit
        product_score["details"]["expected_impact_on_sales"] = {
            "points_earned": impact_points,
            "points_possible": 1,
            "quality": impact_credit
        }
        
        # Justification (1.25 points)
        justification_credit = evaluate_text_answer(
            candidate["task4_margin_adjustment"][product]["justification"]
        )
        justification_points = 1.25 * justification_credit
        product_score["details"]["justification"] = {
            "points_earned": justification_points,
            "points_possible": 1.25,
            "quality": justification_credit
        }
        
        # Sum up points for this product
        product_score["points_earned"] = adjustment_points + price_points + impact_points + justification_points
        results["points_earned"] += product_score["points_earned"]
        results["product_scores"][product] = product_score
    
    return results


def evaluate_submission(candidate: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate the complete submission against the answer key."""
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "task1_results": evaluate_task1(candidate, answer_key),
        "task2_results": evaluate_task2(candidate, answer_key),
        "task3_results": evaluate_task3(candidate, answer_key),
        "task4_results": evaluate_task4(candidate, answer_key),
    }
    
    # Calculate overall score
    total_points_earned = (
        results["task1_results"]["points_earned"] +
        results["task2_results"]["points_earned"] +
        results["task3_results"]["points_earned"] +
        results["task4_results"]["points_earned"]
    )
    total_points_possible = 100  # Fixed total
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 1)
    
    # Determine pass/fail status
    if results["overall_score"] >= 90:
        results["result"] = "Pass with Distinction"
    elif results["overall_score"] >= 75:
        results["result"] = "Pass"
    elif results["overall_score"] >= 65:
        results["result"] = "Conditional Pass"
    else:
        results["result"] = "Fail"
    
    return results


def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the candidate submission and answer key
    candidate = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(candidate, answer_key)
    
    # Write the results to a file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Result: {results['result']}")


if __name__ == "__main__":
    main()