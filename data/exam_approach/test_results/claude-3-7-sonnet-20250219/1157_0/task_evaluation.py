#!/usr/bin/env python3
"""
Evaluation script for Purchasing Agent practical exam.
Compares candidate submission against answer key and generates detailed scoring results.
"""

import json
import sys
import os
from typing import Dict, List, Any, Union, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not valid JSON.")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 1: Review and Identify Issues in a Product Specification."""
    result = {
        "identified_issues_score": 0,
        "identified_issues_feedback": [],
        "missing_elements_score": 0,
        "missing_elements_feedback": [],
        "total_score": 0,
        "max_score": 30
    }
    
    # Check identified issues (20 points)
    max_issues = 5
    points_per_issue = 4
    
    # Extract correct issue types from answer key
    key_issue_types = {issue["issue_type"] for issue in answer_key["task1"]["identified_issues"]}
    
    # Check each submitted issue
    correct_issues = 0
    seen_issue_types = set()
    
    if "identified_issues" not in submission["task1"]:
        result["identified_issues_feedback"].append("No identified issues were submitted.")
    else:
        for issue in submission["task1"]["identified_issues"][:max_issues]:
            if "issue_type" not in issue:
                result["identified_issues_feedback"].append(f"Issue {issue.get('issue_id', 'unknown')} missing issue_type.")
                continue
                
            issue_type = issue["issue_type"]
            
            # Check if this is a duplicate issue type
            if issue_type in seen_issue_types:
                result["identified_issues_feedback"].append(f"Duplicate issue type: {issue_type}.")
                continue
                
            seen_issue_types.add(issue_type)
            
            # Check if the issue type is valid
            if issue_type in key_issue_types:
                correct_issues += 1
                result["identified_issues_feedback"].append(f"Correct issue type: {issue_type}.")
            else:
                result["identified_issues_feedback"].append(f"Invalid issue type: {issue_type}.")
    
    result["identified_issues_score"] = correct_issues * points_per_issue
    
    # Check missing elements (10 points)
    max_elements = 3
    points_per_element = 10 / max_elements
    
    key_missing_elements = [element.lower().strip() for element in answer_key["task1"]["missing_elements"]]
    
    correct_elements = 0
    
    if "missing_elements" not in submission["task1"]:
        result["missing_elements_feedback"].append("No missing elements were submitted.")
    else:
        for element in submission["task1"]["missing_elements"][:max_elements]:
            element_lower = element.lower().strip()
            
            # Check if the element is valid (partial matching for flexibility)
            found_match = False
            for key_element in key_missing_elements:
                if (element_lower in key_element) or (key_element in element_lower):
                    found_match = True
                    break
            
            if found_match:
                correct_elements += 1
                result["missing_elements_feedback"].append(f"Correct missing element: {element}.")
            else:
                result["missing_elements_feedback"].append(f"Invalid missing element: {element}.")
    
    result["missing_elements_score"] = round(correct_elements * points_per_element, 2)
    
    # Calculate total score
    result["total_score"] = round(result["identified_issues_score"] + result["missing_elements_score"], 2)
    
    return result

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 2: Draft a Product Specification."""
    result = {
        "scores": {},
        "feedback": {},
        "total_score": 0,
        "max_score": 40
    }
    
    # Initialize scoring components
    categories = {
        "product_name": 0,  # Just for feedback, not scored
        "category": 5,
        "material": 5,
        "dimensions": 5,
        "weight_capacity": 5,
        "finish_type": 5,
        "certifications": 5,
        "additional_features": 5,
        "warranty": 5
    }
    
    # Set the key and submission paths for easy access
    key_spec = answer_key["task2"]["product_specification"]
    
    if "task2" not in submission or "product_specification" not in submission["task2"]:
        result["feedback"] = {"error": "Product specification missing from submission"}
        return result
        
    sub_spec = submission["task2"]["product_specification"]
    
    # Evaluate product name (no points, just feedback)
    if "product_name" in sub_spec:
        result["feedback"]["product_name"] = "Acceptable name provided."
    else:
        result["feedback"]["product_name"] = "Product name missing."
    
    # Evaluate category (5 points)
    if "category" in sub_spec:
        if sub_spec["category"] == key_spec["category"]:
            result["scores"]["category"] = categories["category"]
            result["feedback"]["category"] = "Correct category selected."
        else:
            result["scores"]["category"] = 0
            result["feedback"]["category"] = f"Incorrect category. Selected: {sub_spec['category']}. Expected: {key_spec['category']}."
    else:
        result["scores"]["category"] = 0
        result["feedback"]["category"] = "Category missing."
    
    # Evaluate material (5 points)
    if "material" in sub_spec:
        if sub_spec["material"] == key_spec["material"]:
            result["scores"]["material"] = categories["material"]
            result["feedback"]["material"] = "Correct material selected."
        else:
            result["scores"]["material"] = 0
            result["feedback"]["material"] = f"Incorrect material. Selected: {sub_spec['material']}. Expected: {key_spec['material']}."
    else:
        result["scores"]["material"] = 0
        result["feedback"]["material"] = "Material missing."
    
    # Evaluate dimensions (5 points)
    if "dimensions" in sub_spec:
        dimensions_correct = True
        dimension_feedback = []
        
        # Check each dimension
        for dim in ["length", "width", "height"]:
            if dim not in sub_spec["dimensions"]:
                dimensions_correct = False
                dimension_feedback.append(f"{dim.capitalize()} is missing.")
            elif sub_spec["dimensions"][dim] != key_spec["dimensions"][dim]:
                dimensions_correct = False
                dimension_feedback.append(f"Incorrect {dim}: {sub_spec['dimensions'][dim]}. Expected: {key_spec['dimensions'][dim]}.")
            else:
                dimension_feedback.append(f"Correct {dim}: {sub_spec['dimensions'][dim]}.")
        
        if dimensions_correct:
            result["scores"]["dimensions"] = categories["dimensions"]
            result["feedback"]["dimensions"] = "All dimensions are correct."
        else:
            result["scores"]["dimensions"] = 0
            result["feedback"]["dimensions"] = "; ".join(dimension_feedback)
    else:
        result["scores"]["dimensions"] = 0
        result["feedback"]["dimensions"] = "Dimensions missing."
    
    # Evaluate weight capacity (5 points)
    if "weight_capacity" in sub_spec:
        if sub_spec["weight_capacity"] == key_spec["weight_capacity"]:
            result["scores"]["weight_capacity"] = categories["weight_capacity"]
            result["feedback"]["weight_capacity"] = "Correct weight capacity specified."
        else:
            result["scores"]["weight_capacity"] = 0
            result["feedback"]["weight_capacity"] = f"Incorrect weight capacity. Specified: {sub_spec['weight_capacity']}. Expected: {key_spec['weight_capacity']}."
    else:
        result["scores"]["weight_capacity"] = 0
        result["feedback"]["weight_capacity"] = "Weight capacity missing."
    
    # Evaluate finish type (5 points)
    if "finish_type" in sub_spec:
        if sub_spec["finish_type"] == key_spec["finish_type"]:
            result["scores"]["finish_type"] = categories["finish_type"]
            result["feedback"]["finish_type"] = "Correct finish type selected."
        else:
            result["scores"]["finish_type"] = 0
            result["feedback"]["finish_type"] = f"Incorrect finish type. Selected: {sub_spec['finish_type']}. Expected: {key_spec['finish_type']}."
    else:
        result["scores"]["finish_type"] = 0
        result["feedback"]["finish_type"] = "Finish type missing."
    
    # Evaluate certifications (5 points)
    if "certifications" in sub_spec:
        key_certs = set(key_spec["certifications"])
        sub_certs = set(sub_spec["certifications"])
        
        correct_certs = sub_certs.intersection(key_certs)
        incorrect_certs = sub_certs - key_certs
        
        min_required = 3  # Must include at least 3 of the 4 correct certifications
        
        if len(correct_certs) >= min_required:
            result["scores"]["certifications"] = categories["certifications"]
            cert_feedback = f"Included {len(correct_certs)} correct certifications."
            if incorrect_certs:
                cert_feedback += f" Also included {len(incorrect_certs)} incorrect certifications: {', '.join(incorrect_certs)}."
            result["feedback"]["certifications"] = cert_feedback
        else:
            result["scores"]["certifications"] = 0
            result["feedback"]["certifications"] = f"Insufficient correct certifications. Found {len(correct_certs)} of {min_required} required."
    else:
        result["scores"]["certifications"] = 0
        result["feedback"]["certifications"] = "Certifications missing."
    
    # Evaluate additional features (5 points)
    if "additional_features" in sub_spec:
        key_features = set(key_spec["additional_features"])
        sub_features = set(sub_spec["additional_features"])
        
        correct_features = sub_features.intersection(key_features)
        incorrect_features = sub_features - key_features
        
        min_required = 5  # Must include at least 5 of the 6 correct features
        
        if len(correct_features) >= min_required:
            result["scores"]["additional_features"] = categories["additional_features"]
            feature_feedback = f"Included {len(correct_features)} correct features."
            if incorrect_features:
                feature_feedback += f" Also included {len(incorrect_features)} incorrect features: {', '.join(incorrect_features)}."
            result["feedback"]["additional_features"] = feature_feedback
        else:
            result["scores"]["additional_features"] = 0
            result["feedback"]["additional_features"] = f"Insufficient correct features. Found {len(correct_features)} of {min_required} required."
    else:
        result["scores"]["additional_features"] = 0
        result["feedback"]["additional_features"] = "Additional features missing."
    
    # Evaluate warranty (5 points)
    if "warranty" in sub_spec:
        # Convert both to strings for comparison
        sub_warranty = str(sub_spec["warranty"])
        key_warranty = str(key_spec["warranty"])
        
        if sub_warranty == key_warranty:
            result["scores"]["warranty"] = categories["warranty"]
            result["feedback"]["warranty"] = "Correct warranty duration specified."
        else:
            result["scores"]["warranty"] = 0
            result["feedback"]["warranty"] = f"Incorrect warranty. Specified: {sub_warranty} months. Expected: {key_warranty} months."
    else:
        result["scores"]["warranty"] = 0
        result["feedback"]["warranty"] = "Warranty missing."
    
    # Calculate total score
    result["total_score"] = sum(result["scores"].values())
    
    return result

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict[str, Any]:
    """Evaluate Task 3: Technical Specification Evaluation."""
    result = {
        "calculation_scores": {
            "total_cost_of_ownership": 0,
            "cost_efficiency_scores": 0
        },
        "calculation_feedback": {
            "total_cost_of_ownership": [],
            "cost_efficiency_scores": []
        },
        "selection_score": 0,
        "selection_feedback": "",
        "compliance_score": 0,
        "compliance_feedback": "",
        "total_score": 0,
        "max_score": 30
    }
    
    # Check if task3 exists in submission
    if "task3" not in submission:
        result["calculation_feedback"]["total_cost_of_ownership"].append("Task 3 missing from submission.")
        return result
    
    # Evaluate total cost of ownership calculations (7.5 points)
    points_per_calculation = 1.25
    max_calculations = 6
    
    key_tco = answer_key["task3"]["calculations"]["total_cost_of_ownership"]
    
    if "calculations" not in submission["task3"] or "total_cost_of_ownership" not in submission["task3"]["calculations"]:
        result["calculation_feedback"]["total_cost_of_ownership"].append("Total cost of ownership calculations missing.")
    else:
        sub_tco = submission["task3"]["calculations"]["total_cost_of_ownership"]
        correct_tco = 0
        
        for product_id, key_value in key_tco.items():
            if product_id not in sub_tco:
                result["calculation_feedback"]["total_cost_of_ownership"].append(f"Calculation missing for {product_id}.")
                continue
                
            # Convert to float for comparison and allow 1% tolerance
            key_float = float(key_value)
            try:
                sub_float = float(sub_tco[product_id])
                
                # Check if within tolerance
                if abs(sub_float - key_float) / key_float <= 0.01:  # 1% tolerance
                    correct_tco += 1
                    result["calculation_feedback"]["total_cost_of_ownership"].append(f"Correct calculation for {product_id}: {sub_tco[product_id]}.")
                else:
                    result["calculation_feedback"]["total_cost_of_ownership"].append(
                        f"Incorrect calculation for {product_id}: {sub_tco[product_id]}. Expected: {key_value}."
                    )
            except ValueError:
                result["calculation_feedback"]["total_cost_of_ownership"].append(
                    f"Invalid number format for {product_id}: {sub_tco[product_id]}."
                )
        
        result["calculation_scores"]["total_cost_of_ownership"] = min(correct_tco * points_per_calculation, 7.5)
    
    # Evaluate cost efficiency score calculations (7.5 points)
    key_ces = answer_key["task3"]["calculations"]["cost_efficiency_scores"]
    
    if "calculations" not in submission["task3"] or "cost_efficiency_scores" not in submission["task3"]["calculations"]:
        result["calculation_feedback"]["cost_efficiency_scores"].append("Cost efficiency score calculations missing.")
    else:
        sub_ces = submission["task3"]["calculations"]["cost_efficiency_scores"]
        correct_ces = 0
        
        for product_id, key_value in key_ces.items():
            if product_id not in sub_ces:
                result["calculation_feedback"]["cost_efficiency_scores"].append(f"Calculation missing for {product_id}.")
                continue
                
            # Convert to float for comparison and allow 1% tolerance
            key_float = float(key_value)
            try:
                sub_float = float(sub_ces[product_id])
                
                # Check if within tolerance
                if abs(sub_float - key_float) / key_float <= 0.01:  # 1% tolerance
                    correct_ces += 1
                    result["calculation_feedback"]["cost_efficiency_scores"].append(f"Correct calculation for {product_id}: {sub_ces[product_id]}.")
                else:
                    result["calculation_feedback"]["cost_efficiency_scores"].append(
                        f"Incorrect calculation for {product_id}: {sub_ces[product_id]}. Expected: {key_value}."
                    )
            except ValueError:
                result["calculation_feedback"]["cost_efficiency_scores"].append(
                    f"Invalid number format for {product_id}: {sub_ces[product_id]}."
                )
        
        result["calculation_scores"]["cost_efficiency_scores"] = min(correct_ces * points_per_calculation, 7.5)
    
    # Evaluate selected product (10 points)
    if "selected_product" not in submission["task3"]:
        result["selection_feedback"] = "Selected product is missing."
    else:
        if submission["task3"]["selected_product"] == answer_key["task3"]["selected_product"]:
            result["selection_score"] = 10
            result["selection_feedback"] = f"Correct product selected: {submission['task3']['selected_product']}."
        else:
            result["selection_score"] = 0
            result["selection_feedback"] = (
                f"Incorrect product selected: {submission['task3']['selected_product']}. "
                f"Expected: {answer_key['task3']['selected_product']}."
            )
    
    # Evaluate specification compliance (5 points)
    if "specification_compliance" not in submission["task3"]:
        result["compliance_feedback"] = "Specification compliance is missing."
    else:
        key_compliance = answer_key["task3"]["specification_compliance"]
        sub_compliance = submission["task3"]["specification_compliance"]
        
        # Check if all specs match
        all_match = True
        mismatch_specs = []
        
        for spec, key_value in key_compliance.items():
            if spec not in sub_compliance:
                all_match = False
                mismatch_specs.append(f"{spec} is missing")
            elif sub_compliance[spec] != key_value:
                all_match = False
                mismatch_specs.append(f"{spec} is {sub_compliance[spec]}, expected {key_value}")
        
        if all_match:
            result["compliance_score"] = 5
            result["compliance_feedback"] = "All specification compliance checks are correct."
        else:
            result["compliance_score"] = 0
            result["compliance_feedback"] = f"Specification compliance has errors: {'; '.join(mismatch_specs)}."
    
    # Calculate total score
    result["total_score"] = (
        result["calculation_scores"]["total_cost_of_ownership"] +
        result["calculation_scores"]["cost_efficiency_scores"] +
        result["selection_score"] +
        result["compliance_score"]
    )
    
    return result

def calculate_overall_score(task_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Calculate the overall score and determine pass/fail status."""
    total_points = sum(task["total_score"] for task in task_results.values())
    max_points = sum(task["max_score"] for task in task_results.values())
    
    overall_percent = (total_points / max_points) * 100 if max_points > 0 else 0
    
    # Determine if each task was passed (>=70%)
    task_status = {}
    for task_name, task_result in task_results.items():
        task_percent = (task_result["total_score"] / task_result["max_score"]) * 100 if task_result["max_score"] > 0 else 0
        task_status[task_name] = {
            "score": task_result["total_score"],
            "max_score": task_result["max_score"],
            "percentage": round(task_percent, 2),
            "passed": task_percent >= 70
        }
    
    # Determine overall status (need >=70% overall)
    passed = overall_percent >= 70
    
    return {
        "overall_score": round(overall_percent, 2),
        "total_points": round(total_points, 2),
        "max_points": max_points,
        "passed": passed,
        "task_status": task_status
    }

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Compile all results
    task_results = {
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    }
    
    overall_results = calculate_overall_score(task_results)
    
    # Create final results object
    final_results = {
        "candidate_id": submission.get("candidate_id", "unknown"),
        "overall_score": overall_results["overall_score"],
        "total_points": overall_results["total_points"],
        "max_points": overall_results["max_points"],
        "passed": overall_results["passed"],
        "task_status": overall_results["task_status"],
        "detailed_results": task_results
    }
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_results['overall_score']}% ({overall_results['total_points']}/{overall_results['max_points']} points)")
    print(f"Pass status: {'PASSED' if overall_results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()