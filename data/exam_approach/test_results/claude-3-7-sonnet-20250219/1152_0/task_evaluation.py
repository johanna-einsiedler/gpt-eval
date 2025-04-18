#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_exercise1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 1: Catalog & Trade Journal Analysis."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "component_scores": {},
        "critical_pass": False
    }
    
    components = ["circuit_breakers", "cable_connectors", "logic_controllers"]
    critical_count = 0
    
    for component in components:
        component_results = {
            "points_earned": 0,
            "points_possible": 10,
            "details": []
        }
        
        # Get the correct answers and submission answers
        correct_answers = answer_key["exercise1"][component]
        submission_answers = submission.get("exercise1", {}).get(component, [])
        
        # Check if at least one supplier was correctly identified
        correct_suppliers = [ans["supplier_name"] for ans in correct_answers]
        submission_suppliers = [ans.get("supplier_name", "") for ans in submission_answers]
        
        if any(supplier in correct_suppliers for supplier in submission_suppliers):
            critical_count += 1
        
        # Evaluate each submitted supplier
        for i, submitted in enumerate(submission_answers[:2]):  # Only consider first two entries
            supplier_result = {"points": 0, "max_points": 5, "notes": []}
            
            # Check if supplier is in the correct answers
            supplier_match = False
            for correct in correct_answers:
                if submitted.get("supplier_name", "") == correct["supplier_name"]:
                    supplier_match = True
                    supplier_result["points"] = 5  # Start with full points
                    
                    # Check each detail, deduct 0.5 points for each incorrect detail
                    for field in ["catalog_page", "product_code", "price"]:
                        if submitted.get(field, "") != correct[field]:
                            supplier_result["points"] -= 0.5
                            supplier_result["notes"].append(f"Incorrect {field}")
                    
                    break
            
            if not supplier_match and submitted.get("supplier_name"):
                # Partial credit for reasonable alternative (2-3 points)
                supplier_result["points"] = 2
                supplier_result["notes"].append("Alternative supplier selected")
            
            # Ensure points are not negative
            supplier_result["points"] = max(0, supplier_result["points"])
            component_results["points_earned"] += supplier_result["points"]
            component_results["details"].append(supplier_result)
        
        results["component_scores"][component] = component_results
        results["points_earned"] += component_results["points_earned"]
    
    # Critical pass if at least one correct supplier for each component
    results["critical_pass"] = critical_count >= 3
    
    return results


def evaluate_exercise2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 2: Online Resource Data Extraction."""
    results = {
        "points_earned": 0,
        "points_possible": 30,
        "component_scores": {},
        "critical_pass": False
    }
    
    products = ["desk_chair", "standing_desk", "conference_table", "filing_cabinet", "partition_system"]
    fields = ["dimensions", "materials", "warranty", "lead_time", "minimum_order"]
    
    products_correct = 0
    
    for product in products:
        product_results = {
            "points_earned": 0,
            "points_possible": 6,
            "details": {}
        }
        
        correct_product = answer_key["exercise2"].get(product, {})
        submitted_product = submission.get("exercise2", {}).get(product, {})
        
        field_correct_count = 0
        
        for field in fields:
            points_per_field = 1.2
            field_result = {
                "correct": False,
                "points": 0,
                "expected": correct_product.get(field, ""),
                "submitted": submitted_product.get(field, "")
            }
            
            if field_result["submitted"] == field_result["expected"]:
                field_result["correct"] = True
                field_result["points"] = points_per_field
                field_correct_count += 1
            
            product_results["points_earned"] += field_result["points"]
            product_results["details"][field] = field_result
        
        # Count this product as correctly extracted if at least 4 out of 5 fields are correct
        if field_correct_count >= 4:
            products_correct += 1
            
        results["component_scores"][product] = product_results
        results["points_earned"] += product_results["points_earned"]
    
    # Critical pass if at least 3 products are correctly extracted
    results["critical_pass"] = products_correct >= 3
    
    return results


def evaluate_exercise3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Exercise 3: Supplier Comparison Analysis."""
    results = {
        "points_earned": 0,
        "points_possible": 40,
        "component_scores": {},
        "critical_pass": False
    }
    
    # Question point values
    question_points = {
        "lowest_price_sc100": 6,
        "shortest_delivery_lab_chemicals": 6,
        "highest_quality_pharma_reagents": 6,
        "best_safety_certification": 10,
        "total_order_cost_supplier_b": 12
    }
    
    correct_count = 0
    calculation_correct = False
    
    for question, max_points in question_points.items():
        question_result = {
            "points_earned": 0,
            "points_possible": max_points,
            "correct": False,
            "expected": answer_key["exercise3"].get(question, ""),
            "submitted": submission.get("exercise3", {}).get(question, "")
        }
        
        # Full points for exact match
        if question_result["submitted"] == question_result["expected"]:
            question_result["points_earned"] = max_points
            question_result["correct"] = True
            correct_count += 1
            
            # Check if calculation question is correct
            if question == "total_order_cost_supplier_b":
                calculation_correct = True
        
        # Partial points for supplier identification questions
        elif question in ["lowest_price_sc100", "shortest_delivery_lab_chemicals", "highest_quality_pharma_reagents"]:
            # Extract supplier from expected and submitted answers
            expected_supplier = question_result["expected"].split(" at ")[0] if " at " in question_result["expected"] else ""
            submitted_supplier = question_result["submitted"].split(" at ")[0] if " at " in question_result["submitted"] else ""
            
            if expected_supplier and submitted_supplier and expected_supplier == submitted_supplier:
                question_result["points_earned"] = max_points / 2  # Half points for correct supplier only
                correct_count += 0.5  # Count as half correct for critical pass calculation
        
        # Partial credit for total cost calculation
        elif question == "total_order_cost_supplier_b":
            # Strip formatting to compare numeric values
            try:
                expected_value = float(question_result["expected"].replace("$", "").replace(",", ""))
                submitted_value = float(question_result["submitted"].replace("$", "").replace(",", ""))
                
                # If within 5% of correct answer, give partial credit
                if abs(submitted_value - expected_value) / expected_value <= 0.05:
                    question_result["points_earned"] = max_points * 0.75
                    correct_count += 0.5
                # If within 10% of correct answer, give some credit
                elif abs(submitted_value - expected_value) / expected_value <= 0.10:
                    question_result["points_earned"] = max_points * 0.5
                    correct_count += 0.25
            except (ValueError, TypeError):
                # If can't parse as number, no partial credit
                pass
        
        results["component_scores"][question] = question_result
        results["points_earned"] += question_result["points_earned"]
    
    # Critical pass if at least 3 questions correct including calculation
    results["critical_pass"] = correct_count >= 3 and calculation_correct
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "overall_score": 0,
        "total_points_earned": 0,
        "total_points_possible": 100,
        "pass_status": False,
        "performance_tier": "",
        "exercises": {}
    }
    
    # Evaluate each exercise
    exercise1_results = evaluate_exercise1(submission, answer_key)
    exercise2_results = evaluate_exercise2(submission, answer_key)
    exercise3_results = evaluate_exercise3(submission, answer_key)
    
    results["exercises"]["exercise1"] = exercise1_results
    results["exercises"]["exercise2"] = exercise2_results
    results["exercises"]["exercise3"] = exercise3_results
    
    # Calculate total points
    results["total_points_earned"] = (
        exercise1_results["points_earned"] +
        exercise2_results["points_earned"] +
        exercise3_results["points_earned"]
    )
    
    # Calculate overall percentage score
    results["overall_score"] = round(
        (results["total_points_earned"] / results["total_points_possible"]) * 100, 1
    )
    
    # Determine performance tier
    if results["overall_score"] >= 90:
        results["performance_tier"] = "Excellent"
    elif results["overall_score"] >= 80:
        results["performance_tier"] = "Good"
    elif results["overall_score"] >= 70:
        results["performance_tier"] = "Satisfactory"
    else:
        results["performance_tier"] = "Needs Improvement"
    
    # Determine pass status based on critical requirements and minimum score
    critical_pass = (
        exercise1_results["critical_pass"] and
        exercise2_results["critical_pass"] and
        exercise3_results["critical_pass"]
    )
    
    results["pass_status"] = critical_pass and results["overall_score"] >= 70
    
    return results


def main():
    """Main function to process command line arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Pass Status: {results['pass_status']}")
    print(f"Performance Tier: {results['performance_tier']}")


if __name__ == "__main__":
    main()