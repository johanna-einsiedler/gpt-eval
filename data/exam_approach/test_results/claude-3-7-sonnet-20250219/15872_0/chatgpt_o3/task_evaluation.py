#!/usr/bin/env python3
"""
Logistics Engineer Practical Exam Evaluator

This script evaluates a candidate's submission against the answer key for the
Logistics Engineer practical exam on cost estimation and forecasting.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import math
from typing import Dict, List, Any, Tuple


def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_cost_per_mile(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the cost per mile calculations."""
    results = {
        "points_possible": 3,
        "points_earned": 0,
        "details": {}
    }
    
    submission_cpm = submission.get("current_cost_per_mile", {})
    answer_cpm = answer_key.get("current_cost_per_mile", {})
    
    for vehicle_type in ["vehicle_type_A", "vehicle_type_B", "vehicle_type_C"]:
        sub_value = submission_cpm.get(vehicle_type)
        key_value = answer_cpm.get(vehicle_type)
        
        if sub_value is None:
            results["details"][vehicle_type] = {
                "submitted": None,
                "expected": key_value,
                "correct": False,
                "message": "Missing value"
            }
        elif not isinstance(sub_value, (int, float)):
            results["details"][vehicle_type] = {
                "submitted": sub_value,
                "expected": key_value,
                "correct": False,
                "message": "Not a number"
            }
        else:
            difference = abs(sub_value - key_value)
            is_correct = difference <= 0.05
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"][vehicle_type] = {
                "submitted": sub_value,
                "expected": key_value,
                "correct": is_correct,
                "difference": difference,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
    
    return results


def evaluate_top_components(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the top cost components identification."""
    results = {
        "points_possible": 3,
        "points_earned": 0,
        "details": {}
    }
    
    submission_components = submission.get("top_cost_components", [])
    answer_components = answer_key.get("top_cost_components", [])
    
    # Check if the list exists and has 3 components
    if not isinstance(submission_components, list):
        results["details"]["format"] = {
            "submitted": type(submission_components).__name__,
            "expected": "list",
            "correct": False,
            "message": "Not a list"
        }
        return results
    
    if len(submission_components) != 3:
        results["details"]["count"] = {
            "submitted": len(submission_components),
            "expected": 3,
            "correct": False,
            "message": "Should contain exactly 3 components"
        }
    
    # Check each component
    for i, expected in enumerate(answer_components):
        if i < len(submission_components):
            submitted = submission_components[i]
            is_correct = submitted == expected
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"][f"component_{i+1}"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "message": "Correct" if is_correct else "Incorrect"
            }
        else:
            results["details"][f"component_{i+1}"] = {
                "submitted": None,
                "expected": expected,
                "correct": False,
                "message": "Missing component"
            }
    
    return results


def evaluate_component_percentages(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the cost component percentages."""
    results = {
        "points_possible": 3,
        "points_earned": 0,
        "details": {}
    }
    
    submission_percentages = submission.get("cost_component_percentages", {})
    answer_percentages = answer_key.get("cost_component_percentages", {})
    
    # Check if the dictionary exists
    if not isinstance(submission_percentages, dict):
        results["details"]["format"] = {
            "submitted": type(submission_percentages).__name__,
            "expected": "dict",
            "correct": False,
            "message": "Not a dictionary"
        }
        return results
    
    # Check each component percentage
    for component, expected in answer_percentages.items():
        if component in submission_percentages:
            submitted = submission_percentages[component]
            
            if not isinstance(submitted, (int, float)):
                results["details"][component] = {
                    "submitted": submitted,
                    "expected": expected,
                    "correct": False,
                    "message": "Not a number"
                }
                continue
                
            difference = abs(submitted - expected)
            is_correct = difference <= 0.02
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"][component] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "difference": difference,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
        else:
            results["details"][component] = {
                "submitted": None,
                "expected": expected,
                "correct": False,
                "message": "Missing component"
            }
    
    return results


def evaluate_forecast(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the six-month forecast."""
    results = {
        "points_possible": 2,
        "points_earned": 0,
        "details": {}
    }
    
    submission_forecast = submission.get("six_month_forecast", {})
    answer_forecast = answer_key.get("six_month_forecast", {})
    
    # Check if the dictionary exists
    if not isinstance(submission_forecast, dict):
        results["details"]["format"] = {
            "submitted": type(submission_forecast).__name__,
            "expected": "dict",
            "correct": False,
            "message": "Not a dictionary"
        }
        return results
    
    # Check total cost
    if "total_cost" in submission_forecast:
        submitted = submission_forecast["total_cost"]
        expected = answer_forecast["total_cost"]
        
        if not isinstance(submitted, (int, float)):
            results["details"]["total_cost"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": False,
                "message": "Not a number"
            }
        else:
            # Allow 5% tolerance
            difference_percentage = abs(submitted - expected) / expected
            is_correct = difference_percentage <= 0.05
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"]["total_cost"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "difference_percentage": difference_percentage,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
    else:
        results["details"]["total_cost"] = {
            "submitted": None,
            "expected": answer_forecast.get("total_cost"),
            "correct": False,
            "message": "Missing value"
        }
    
    # Check percentage change
    if "percentage_change" in submission_forecast:
        submitted = submission_forecast["percentage_change"]
        expected = answer_forecast["percentage_change"]
        
        if not isinstance(submitted, (int, float)):
            results["details"]["percentage_change"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": False,
                "message": "Not a number"
            }
        else:
            difference = abs(submitted - expected)
            is_correct = difference <= 0.02
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"]["percentage_change"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "difference": difference,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
    else:
        results["details"]["percentage_change"] = {
            "submitted": None,
            "expected": answer_forecast.get("percentage_change"),
            "correct": False,
            "message": "Missing value"
        }
    
    return results


def evaluate_sensitivity(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the sensitivity analysis."""
    results = {
        "points_possible": 3,
        "points_earned": 0,
        "details": {}
    }
    
    submission_sensitivity = submission.get("sensitivity_analysis", {})
    answer_sensitivity = answer_key.get("sensitivity_analysis", {})
    
    # Check if the dictionary exists
    if not isinstance(submission_sensitivity, dict):
        results["details"]["format"] = {
            "submitted": type(submission_sensitivity).__name__,
            "expected": "dict",
            "correct": False,
            "message": "Not a dictionary"
        }
        return results
    
    # Check fuel impact percentage
    if "fuel_impact_percentage" in submission_sensitivity:
        submitted = submission_sensitivity["fuel_impact_percentage"]
        expected = answer_sensitivity["fuel_impact_percentage"]
        
        if not isinstance(submitted, (int, float)):
            results["details"]["fuel_impact_percentage"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": False,
                "message": "Not a number"
            }
        else:
            difference = abs(submitted - expected)
            is_correct = difference <= 0.01
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"]["fuel_impact_percentage"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "difference": difference,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
    else:
        results["details"]["fuel_impact_percentage"] = {
            "submitted": None,
            "expected": answer_sensitivity.get("fuel_impact_percentage"),
            "correct": False,
            "message": "Missing value"
        }
    
    # Check wage impact percentage
    if "wage_impact_percentage" in submission_sensitivity:
        submitted = submission_sensitivity["wage_impact_percentage"]
        expected = answer_sensitivity["wage_impact_percentage"]
        
        if not isinstance(submitted, (int, float)):
            results["details"]["wage_impact_percentage"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": False,
                "message": "Not a number"
            }
        else:
            difference = abs(submitted - expected)
            is_correct = difference <= 0.01
            
            if is_correct:
                results["points_earned"] += 1
                
            results["details"]["wage_impact_percentage"] = {
                "submitted": submitted,
                "expected": expected,
                "correct": is_correct,
                "difference": difference,
                "message": "Within tolerance" if is_correct else "Outside tolerance"
            }
    else:
        results["details"]["wage_impact_percentage"] = {
            "submitted": None,
            "expected": answer_sensitivity.get("wage_impact_percentage"),
            "correct": False,
            "message": "Missing value"
        }
    
    # Check most sensitive factor
    if "most_sensitive_factor" in submission_sensitivity:
        submitted = submission_sensitivity["most_sensitive_factor"]
        expected = answer_sensitivity["most_sensitive_factor"]
        
        is_correct = submitted == expected
        
        if is_correct:
            results["points_earned"] += 1
            
        results["details"]["most_sensitive_factor"] = {
            "submitted": submitted,
            "expected": expected,
            "correct": is_correct,
            "message": "Correct" if is_correct else "Incorrect"
        }
    else:
        results["details"]["most_sensitive_factor"] = {
            "submitted": None,
            "expected": answer_sensitivity.get("most_sensitive_factor"),
            "correct": False,
            "message": "Missing value"
        }
    
    return results


def evaluate_json_format(submission: Dict) -> Dict:
    """Evaluate if the JSON submission is properly formatted."""
    results = {
        "points_possible": 1,
        "points_earned": 0,
        "details": {}
    }
    
    # Check for required fields
    required_fields = [
        "current_cost_per_mile",
        "top_cost_components",
        "cost_component_percentages",
        "six_month_forecast",
        "sensitivity_analysis"
    ]
    
    missing_fields = [field for field in required_fields if field not in submission]
    
    if missing_fields:
        results["details"]["missing_fields"] = {
            "submitted": list(submission.keys()),
            "missing": missing_fields,
            "correct": False,
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }
    else:
        results["points_earned"] = 1
        results["details"]["format"] = {
            "correct": True,
            "message": "All required fields present"
        }
    
    return results


def check_passing_criteria(evaluation_results: Dict) -> Dict:
    """Check if the candidate meets the passing criteria."""
    results = {
        "passed": False,
        "criteria": {}
    }
    
    # Criterion 1: Accuracy of Calculations
    total_numerical_points = (
        evaluation_results["cost_per_mile"]["points_earned"] +
        evaluation_results["component_percentages"]["points_earned"] +
        evaluation_results["forecast"]["points_earned"] +
        evaluation_results["sensitivity"]["points_earned"]
    )
    total_numerical_possible = (
        evaluation_results["cost_per_mile"]["points_possible"] +
        evaluation_results["component_percentages"]["points_possible"] +
        evaluation_results["forecast"]["points_possible"] +
        evaluation_results["sensitivity"]["points_possible"]
    )
    
    numerical_accuracy = total_numerical_points / total_numerical_possible if total_numerical_possible > 0 else 0
    
    results["criteria"]["numerical_accuracy"] = {
        "passed": numerical_accuracy >= 0.8,
        "score": numerical_accuracy,
        "requirement": "At least 80% of numerical values within acceptable ranges"
    }
    
    # Criterion 2: Most sensitive factor correctly identified
    most_sensitive_correct = False
    if "sensitivity" in evaluation_results and "details" in evaluation_results["sensitivity"]:
        if "most_sensitive_factor" in evaluation_results["sensitivity"]["details"]:
            most_sensitive_correct = evaluation_results["sensitivity"]["details"]["most_sensitive_factor"].get("correct", False)
    
    results["criteria"]["most_sensitive_factor"] = {
        "passed": most_sensitive_correct,
        "requirement": "Most sensitive factor correctly identified"
    }
    
    # Criterion 3: Top three cost components correctly identified
    top_components_correct = False
    if "top_components" in evaluation_results and "points_earned" in evaluation_results["top_components"]:
        top_components_correct = evaluation_results["top_components"]["points_earned"] == 3
    
    results["criteria"]["top_components"] = {
        "passed": top_components_correct,
        "requirement": "Top three cost components correctly identified"
    }
    
    # Criterion 4: JSON format
    json_format_correct = False
    if "json_format" in evaluation_results and "points_earned" in evaluation_results["json_format"]:
        json_format_correct = evaluation_results["json_format"]["points_earned"] == 1
    
    results["criteria"]["json_format"] = {
        "passed": json_format_correct,
        "requirement": "JSON submission properly formatted with all required fields"
    }
    
    # Overall pass/fail
    results["passed"] = (
        results["criteria"]["numerical_accuracy"]["passed"] and
        results["criteria"]["most_sensitive_factor"]["passed"] and
        results["criteria"]["top_components"]["passed"] and
        results["criteria"]["json_format"]["passed"]
    )
    
    return results


def calculate_overall_score(evaluation_results: Dict) -> float:
    """Calculate the overall score as a percentage."""
    total_points_earned = sum(section["points_earned"] for section in evaluation_results.values() if "points_earned" in section)
    total_points_possible = sum(section["points_possible"] for section in evaluation_results.values() if "points_possible" in section)
    
    if total_points_possible == 0:
        return 0.0
    
    return (total_points_earned / total_points_possible) * 100


def main():
    """Main function to evaluate the candidate's submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    evaluation_results = {
        "cost_per_mile": evaluate_cost_per_mile(submission, answer_key),
        "top_components": evaluate_top_components(submission, answer_key),
        "component_percentages": evaluate_component_percentages(submission, answer_key),
        "forecast": evaluate_forecast(submission, answer_key),
        "sensitivity": evaluate_sensitivity(submission, answer_key),
        "json_format": evaluate_json_format(submission)
    }
    
    # Check passing criteria
    passing_criteria = check_passing_criteria(evaluation_results)
    
    # Calculate overall score
    overall_score = calculate_overall_score(evaluation_results)
    
    # Prepare the results
    test_results = {
        "overall_score": round(overall_score, 2),
        "passing_criteria": passing_criteria,
        "evaluation_details": evaluation_results
    }
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    print(f"Passed: {passing_criteria['passed']}")


if __name__ == "__main__":
    main()