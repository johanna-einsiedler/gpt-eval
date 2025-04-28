#!/usr/bin/env python3
"""
WBS Development Practical Exam Evaluator

This script evaluates a candidate's WBS submission against an answer key.
It checks for proper WBS structure, completeness, and correctness of calculations.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import os
from collections import defaultdict

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def validate_wbs_structure(submission):
    """Validate the basic structure of the WBS submission."""
    results = {
        "structure_validation": {
            "has_required_fields": True,
            "wbs_elements_present": True,
            "total_project_effort_present": True,
            "issues": []
        },
        "score": 0
    }
    
    # Check for required top-level fields
    if "wbs_elements" not in submission:
        results["structure_validation"]["wbs_elements_present"] = False
        results["structure_validation"]["issues"].append("Missing 'wbs_elements' field")
    
    if "total_project_effort" not in submission:
        results["structure_validation"]["total_project_effort_present"] = False
        results["structure_validation"]["issues"].append("Missing 'total_project_effort' field")
    
    # Check if wbs_elements is a list with at least one element
    if results["structure_validation"]["wbs_elements_present"]:
        if not isinstance(submission["wbs_elements"], list) or len(submission["wbs_elements"]) == 0:
            results["structure_validation"]["issues"].append("'wbs_elements' must be a non-empty list")
    
    # Check if total_project_effort is an integer
    if results["structure_validation"]["total_project_effort_present"]:
        if not isinstance(submission["total_project_effort"], int):
            results["structure_validation"]["issues"].append("'total_project_effort' must be an integer")
    
    # Calculate score for structure validation (10% of total)
    if not results["structure_validation"]["issues"]:
        results["score"] = 10
    else:
        # Partial credit based on number of issues
        results["score"] = max(0, 10 - 2 * len(results["structure_validation"]["issues"]))
    
    return results

def validate_wbs_elements(submission):
    """Validate each WBS element for required fields and proper formatting."""
    results = {
        "element_validation": {
            "all_elements_valid": True,
            "element_issues": []
        },
        "score": 0
    }
    
    if "wbs_elements" not in submission:
        results["element_validation"]["all_elements_valid"] = False
        results["element_validation"]["element_issues"].append("No WBS elements to validate")
        results["score"] = 0
        return results
    
    required_fields = ["wbs_code", "description", "level", "effort_hours", "percentage", "deliverable_type"]
    valid_deliverable_types = ["DOC", "SW", "HW", "TR", "TST", ""]
    
    total_elements = len(submission["wbs_elements"])
    valid_elements = 0
    
    for i, element in enumerate(submission["wbs_elements"]):
        element_issues = []
        
        # Check for required fields
        for field in required_fields:
            if field not in element:
                element_issues.append(f"Missing required field: {field}")
        
        if not element_issues:
            # Validate wbs_code format (e.g., "1.0", "1.1", "1.1.1")
            if not isinstance(element["wbs_code"], str) or not all(part.isdigit() for part in element["wbs_code"].replace(".", "")):
                element_issues.append(f"Invalid WBS code format: {element['wbs_code']}")
            
            # Validate level is an integer between 1 and 4
            if not isinstance(element["level"], int) or element["level"] < 1 or element["level"] > 4:
                element_issues.append(f"Invalid level: {element['level']}")
            
            # Validate effort_hours is a non-negative integer
            if not isinstance(element["effort_hours"], int) or element["effort_hours"] < 0:
                element_issues.append(f"Invalid effort_hours: {element['effort_hours']}")
            
            # Validate percentage is a non-negative integer
            if not isinstance(element["percentage"], int) or element["percentage"] < 0:
                element_issues.append(f"Invalid percentage: {element['percentage']}")
            
            # Validate deliverable_type is one of the allowed values
            if element["deliverable_type"] not in valid_deliverable_types:
                element_issues.append(f"Invalid deliverable_type: {element['deliverable_type']}")
            
            # Check if level matches WBS code depth
            code_parts = element["wbs_code"].split(".")
            if len(code_parts) != element["level"]:
                element_issues.append(f"WBS code depth ({len(code_parts)}) doesn't match level ({element['level']})")
            
            # For parent elements, deliverable_type should be empty
            if element["level"] < 3 and element["deliverable_type"] != "":
                element_issues.append(f"Parent element has non-empty deliverable_type: {element['deliverable_type']}")
        
        if element_issues:
            results["element_validation"]["all_elements_valid"] = False
            results["element_validation"]["element_issues"].append({
                "element_index": i,
                "wbs_code": element.get("wbs_code", "unknown"),
                "issues": element_issues
            })
        else:
            valid_elements += 1
    
    # Calculate score for element validation (15% of total)
    if valid_elements == total_elements:
        results["score"] = 15
    else:
        # Partial credit based on percentage of valid elements
        results["score"] = round(15 * (valid_elements / total_elements), 1)
    
    return results

def validate_wbs_hierarchy(submission):
    """Validate the hierarchical structure of the WBS."""
    results = {
        "hierarchy_validation": {
            "valid_hierarchy": True,
            "has_required_levels": False,
            "has_required_work_packages": False,
            "level_counts": {1: 0, 2: 0, 3: 0, 4: 0},
            "issues": []
        },
        "score": 0
    }
    
    if "wbs_elements" not in submission:
        results["hierarchy_validation"]["valid_hierarchy"] = False
        results["hierarchy_validation"]["issues"].append("No WBS elements to validate hierarchy")
        return results
    
    # Count elements at each level
    for element in submission["wbs_elements"]:
        if "level" in element and isinstance(element["level"], int) and 1 <= element["level"] <= 4:
            results["hierarchy_validation"]["level_counts"][element["level"]] += 1
    
    # Check if there are at least 3 levels of detail
    if results["hierarchy_validation"]["level_counts"][3] > 0:
        results["hierarchy_validation"]["has_required_levels"] = True
    else:
        results["hierarchy_validation"]["issues"].append("WBS does not have at least 3 levels of detail")
    
    # Check if there are at least 15 work packages (level 3 or 4 elements)
    work_packages = results["hierarchy_validation"]["level_counts"][3] + results["hierarchy_validation"]["level_counts"][4]
    if work_packages >= 15:
        results["hierarchy_validation"]["has_required_work_packages"] = True
    else:
        results["hierarchy_validation"]["issues"].append(f"WBS has only {work_packages} work packages, minimum 15 required")
    
    # Build a dictionary to check parent-child relationships
    elements_by_code = {element["wbs_code"]: element for element in submission["wbs_elements"] if "wbs_code" in element}
    
    # Check parent-child relationships
    for code, element in elements_by_code.items():
        if "." in code:
            parent_code = ".".join(code.split(".")[:-1])
            if parent_code not in elements_by_code:
                results["hierarchy_validation"]["valid_hierarchy"] = False
                results["hierarchy_validation"]["issues"].append(f"Element {code} has no parent element {parent_code}")
    
    # Calculate score for hierarchy validation (20% of total)
    score = 0
    if results["hierarchy_validation"]["valid_hierarchy"]:
        score += 10
    if results["hierarchy_validation"]["has_required_levels"]:
        score += 5
    if results["hierarchy_validation"]["has_required_work_packages"]:
        score += 5
    
    results["score"] = score
    return results

def validate_wbs_calculations(submission):
    """Validate effort calculations and percentages in the WBS."""
    results = {
        "calculation_validation": {
            "valid_effort_rollup": True,
            "valid_percentages": True,
            "total_effort_matches": True,
            "issues": []
        },
        "score": 0
    }
    
    if "wbs_elements" not in submission or "total_project_effort" not in submission:
        results["calculation_validation"]["valid_effort_rollup"] = False
        results["calculation_validation"]["valid_percentages"] = False
        results["calculation_validation"]["total_effort_matches"] = False
        results["calculation_validation"]["issues"].append("Missing required fields for calculation validation")
        return results
    
    # Build a dictionary of elements by code
    elements_by_code = {element["wbs_code"]: element for element in submission["wbs_elements"] 
                        if all(key in element for key in ["wbs_code", "level", "effort_hours", "percentage"])}
    
    # Check effort rollup (parent effort should equal sum of child efforts)
    for code, element in elements_by_code.items():
        # Skip leaf nodes
        if not any(other_code.startswith(code + ".") for other_code in elements_by_code):
            continue
        
        # Calculate sum of direct children
        children_sum = sum(
            elements_by_code[other_code]["effort_hours"]
            for other_code in elements_by_code
            if other_code.startswith(code + ".") and other_code.count(".") == code.count(".") + 1
        )
        
        if element["effort_hours"] != children_sum:
            results["calculation_validation"]["valid_effort_rollup"] = False
            results["calculation_validation"]["issues"].append(
                f"Element {code} effort ({element['effort_hours']}) doesn't match sum of children ({children_sum})"
            )
    
    # Check percentages within each level under the same parent
    for parent_code, parent in elements_by_code.items():
        # Get direct children
        children = [
            elements_by_code[code] for code in elements_by_code
            if code.startswith(parent_code + ".") and code.count(".") == parent_code.count(".") + 1
        ]
        
        if children:
            children_percentage_sum = sum(child["percentage"] for child in children)
            if abs(children_percentage_sum - 100) > 1:  # Allow 1% tolerance for rounding
                results["calculation_validation"]["valid_percentages"] = False
                results["calculation_validation"]["issues"].append(
                    f"Children of {parent_code} have percentages that sum to {children_percentage_sum}, not 100%"
                )
    
    # Check if level 1 efforts sum to total project effort
    level1_sum = sum(
        element["effort_hours"] for element in elements_by_code.values()
        if element["level"] == 1
    )
    
    if level1_sum != submission["total_project_effort"]:
        results["calculation_validation"]["total_effort_matches"] = False
        results["calculation_validation"]["issues"].append(
            f"Sum of level 1 efforts ({level1_sum}) doesn't match total project effort ({submission['total_project_effort']})"
        )
    
    # Calculate score for calculation validation (25% of total)
    score = 0
    if results["calculation_validation"]["valid_effort_rollup"]:
        score += 10
    if results["calculation_validation"]["valid_percentages"]:
        score += 10
    if results["calculation_validation"]["total_effort_matches"]:
        score += 5
    
    results["score"] = score
    return results

def validate_wbs_content(submission, answer_key):
    """Validate the content of the WBS against the answer key."""
    results = {
        "content_validation": {
            "coverage_score": 0,
            "phase_coverage": {},
            "missing_key_elements": [],
            "issues": []
        },
        "score": 0
    }
    
    if "wbs_elements" not in submission or "wbs_elements" not in answer_key:
        results["content_validation"]["issues"].append("Missing required fields for content validation")
        return results
    
    # Extract phase names from level 1 elements in the answer key
    key_phases = {
        element["wbs_code"]: element["description"]
        for element in answer_key["wbs_elements"]
        if element["level"] == 1
    }
    
    # Extract phase names from level 1 elements in the submission
    submission_phases = {
        element["wbs_code"]: element["description"]
        for element in submission["wbs_elements"]
        if "level" in element and element["level"] == 1
    }
    
    # Check coverage of key phases
    phase_coverage = {}
    for phase_code, phase_name in key_phases.items():
        # Check if a similar phase exists in the submission
        found = False
        for sub_code, sub_name in submission_phases.items():
            # Check for exact match or similar name (contains key words)
            if sub_name.lower() == phase_name.lower() or any(
                keyword.lower() in sub_name.lower() 
                for keyword in phase_name.lower().split()
                if len(keyword) > 3  # Only consider significant words
            ):
                found = True
                break
        
        phase_coverage[phase_name] = found
        if not found:
            results["content_validation"]["missing_key_elements"].append(phase_name)
    
    results["content_validation"]["phase_coverage"] = phase_coverage
    
    # Calculate coverage score (percentage of key phases covered)
    coverage_percentage = sum(1 for covered in phase_coverage.values() if covered) / len(phase_coverage) if phase_coverage else 0
    results["content_validation"]["coverage_score"] = round(coverage_percentage * 100)
    
    # Calculate score for content validation (30% of total)
    results["score"] = round(30 * coverage_percentage, 1)
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the WBS submission against the answer key."""
    evaluation = {
        "structure_validation": validate_wbs_structure(submission),
        "element_validation": validate_wbs_elements(submission),
        "hierarchy_validation": validate_wbs_hierarchy(submission),
        "calculation_validation": validate_wbs_calculations(submission),
        "content_validation": validate_wbs_content(submission, answer_key),
        "overall_score": 0
    }
    
    # Calculate overall score
    overall_score = (
        evaluation["structure_validation"]["score"] +
        evaluation["element_validation"]["score"] +
        evaluation["hierarchy_validation"]["score"] +
        evaluation["calculation_validation"]["score"] +
        evaluation["content_validation"]["score"]
    )
    
    evaluation["overall_score"] = overall_score
    
    return evaluation

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {evaluation_results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()