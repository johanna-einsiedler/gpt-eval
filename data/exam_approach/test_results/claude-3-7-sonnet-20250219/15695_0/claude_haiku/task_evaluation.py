#!/usr/bin/env python3
"""
Supply Chain Performance Metrics Exam Evaluator

This script evaluates a candidate's submission against an answer key for the
Supply Chain Performance Metrics practical exam.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_metric_selection(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the metric selection and calculation (40% of total score).
    
    Criteria:
    - At least 7 out of 9 key metrics correctly identified across all scenarios
    - Calculations must be accurate within ±5% of the expected values
    - Formulas must be correctly specified
    """
    results = {
        "correct_metrics": 0,
        "accurate_calculations": 0,
        "correct_formulas": 0,
        "total_metrics": 0,
        "details": []
    }
    
    # Get scenarios from both submission and answer key
    sub_scenarios = {s["scenario_id"]: s for s in submission.get("scenario_analyses", [])}
    key_scenarios = {s["scenario_id"]: s for s in answer_key.get("scenario_analyses", [])}
    
    # Check each scenario in the answer key
    for scenario_id, key_scenario in key_scenarios.items():
        if scenario_id not in sub_scenarios:
            results["details"].append(f"Missing scenario {scenario_id}")
            continue
            
        sub_scenario = sub_scenarios[scenario_id]
        
        # Get key metrics from both
        key_metrics = {m["metric_name"].lower(): m for m in key_scenario.get("key_metrics", [])}
        sub_metrics = {m["metric_name"].lower(): m for m in sub_scenario.get("key_metrics", [])}
        
        results["total_metrics"] += len(key_metrics)
        
        # Check each key metric
        for metric_name, key_metric in key_metrics.items():
            metric_result = {
                "scenario_id": scenario_id,
                "metric_name": key_metric["metric_name"],
                "identified": False,
                "calculation_accurate": False,
                "formula_correct": False
            }
            
            # Check if metric was identified
            if metric_name in sub_metrics:
                metric_result["identified"] = True
                results["correct_metrics"] += 1
                
                sub_metric = sub_metrics[metric_name]
                
                # Check calculation accuracy (within ±5%)
                key_value = float(key_metric["current_value"])
                sub_value = float(sub_metric["current_value"])
                
                # Calculate percentage difference
                if key_value != 0:
                    pct_diff = abs((sub_value - key_value) / key_value) * 100
                    if pct_diff <= 5:
                        metric_result["calculation_accurate"] = True
                        results["accurate_calculations"] += 1
                else:
                    # Handle case where key value is 0
                    if abs(sub_value) < 0.01:  # Small absolute difference
                        metric_result["calculation_accurate"] = True
                        results["accurate_calculations"] += 1
                
                # Check formula correctness (simple string comparison for now)
                # This is a simplified approach - in a real evaluation, you might want more sophisticated matching
                key_calc = key_metric["calculation"].lower().replace(" ", "")
                sub_calc = sub_metric["calculation"].lower().replace(" ", "")
                
                # Check if the calculation contains key elements
                key_elements = [term.strip() for term in key_calc.split("/")]
                sub_elements = [term.strip() for term in sub_calc.split("/")]
                
                if (len(key_elements) == len(sub_elements) and
                    all(any(ke in se for se in sub_elements) for ke in key_elements)):
                    metric_result["formula_correct"] = True
                    results["correct_formulas"] += 1
            
            results["details"].append(metric_result)
    
    # Calculate score (40% of total)
    max_score = 40
    metrics_score = (results["correct_metrics"] / results["total_metrics"]) * (max_score * 0.4)
    calc_score = (results["accurate_calculations"] / results["total_metrics"]) * (max_score * 0.4)
    formula_score = (results["correct_formulas"] / results["total_metrics"]) * (max_score * 0.2)
    
    results["score"] = metrics_score + calc_score + formula_score
    results["max_score"] = max_score
    
    return results


def evaluate_gap_analysis(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the gap analysis (30% of total score).
    
    Criteria:
    - Correctly identify at least 7 out of 9 performance gaps
    - Impact assessments must be reasonable based on the gap size and business context
    """
    results = {
        "correct_gaps": 0,
        "reasonable_impacts": 0,
        "total_gaps": 0,
        "details": []
    }
    
    # Get scenarios from both submission and answer key
    sub_scenarios = {s["scenario_id"]: s for s in submission.get("scenario_analyses", [])}
    key_scenarios = {s["scenario_id"]: s for s in answer_key.get("scenario_analyses", [])}
    
    # Check each scenario in the answer key
    for scenario_id, key_scenario in key_scenarios.items():
        if scenario_id not in sub_scenarios:
            continue
            
        sub_scenario = sub_scenarios[scenario_id]
        
        # Get key metrics from both
        key_metrics = {m["metric_name"].lower(): m for m in key_scenario.get("key_metrics", [])}
        sub_metrics = {m["metric_name"].lower(): m for m in sub_scenario.get("key_metrics", [])}
        
        # Check each key metric
        for metric_name, key_metric in key_metrics.items():
            results["total_gaps"] += 1
            
            gap_result = {
                "scenario_id": scenario_id,
                "metric_name": key_metric["metric_name"],
                "gap_correct": False,
                "impact_reasonable": False
            }
            
            # Check if metric was identified
            if metric_name in sub_metrics:
                sub_metric = sub_metrics[metric_name]
                
                # Check gap calculation
                key_gap = float(key_metric["gap"])
                sub_gap = float(sub_metric["gap"])
                
                # Allow for small differences in gap calculation
                if abs(key_gap - sub_gap) <= 0.5:
                    gap_result["gap_correct"] = True
                    results["correct_gaps"] += 1
                
                # Check impact assessment
                key_impact = key_metric["impact"].lower()
                sub_impact = sub_metric["impact"].lower()
                
                # Define reasonable impact ranges based on gap size and direction
                # This is a simplified approach - in a real evaluation, you might want more context-specific logic
                if key_impact == sub_impact:
                    gap_result["impact_reasonable"] = True
                    results["reasonable_impacts"] += 1
                elif (key_impact == "high" and sub_impact == "medium") or (key_impact == "medium" and sub_impact == "high"):
                    # Allow for some subjectivity between high and medium
                    gap_result["impact_reasonable"] = True
                    results["reasonable_impacts"] += 1
                elif (key_impact == "medium" and sub_impact == "low") or (key_impact == "low" and sub_impact == "medium"):
                    # Allow for some subjectivity between medium and low
                    gap_result["impact_reasonable"] = True
                    results["reasonable_impacts"] += 1
            
            results["details"].append(gap_result)
    
    # Calculate score (30% of total)
    max_score = 30
    gaps_score = (results["correct_gaps"] / results["total_gaps"]) * (max_score * 0.6)
    impact_score = (results["reasonable_impacts"] / results["total_gaps"]) * (max_score * 0.4)
    
    results["score"] = gaps_score + impact_score
    results["max_score"] = max_score
    
    return results


def evaluate_monitoring_recommendations(submission: Dict, answer_key: Dict) -> Dict:
    """
    Evaluate the monitoring recommendations (20% of total score).
    
    Criteria:
    - At least 12 out of 15 monitoring metrics must be appropriate for the scenarios
    - Frequency recommendations must be logical for each metric type
    """
    results = {
        "appropriate_metrics": 0,
        "logical_frequencies": 0,
        "total_metrics": 0,
        "details": []
    }
    
    # Get scenarios from both submission and answer key
    sub_scenarios = {s["scenario_id"]: s for s in submission.get("scenario_analyses", [])}
    key_scenarios = {s["scenario_id"]: s for s in answer_key.get("scenario_analyses", [])}
    
    # Check each scenario in the answer key
    for scenario_id, key_scenario in key_scenarios.items():
        if scenario_id not in sub_scenarios:
            continue
            
        sub_scenario = sub_scenarios[scenario_id]
        
        # Get monitoring metrics from submission
        sub_metrics = sub_scenario.get("monitoring_metrics", [])
        
        # Expected number of monitoring metrics per scenario
        expected_count = 5
        results["total_metrics"] += expected_count
        
        # Check if the right number of metrics is provided
        if len(sub_metrics) != expected_count:
            results["details"].append({
                "scenario_id": scenario_id,
                "issue": f"Expected {expected_count} monitoring metrics, got {len(sub_metrics)}"
            })
        
        # Get the recommended metrics for this scenario
        key_metrics = key_scenario.get("monitoring_metrics", [])
        key_metric_names = [m["metric_name"].lower() for m in key_metrics]
        key_frequencies = {m["metric_name"].lower(): m["frequency"].lower() for m in key_metrics}
        
        # Check each submitted metric
        for sub_metric in sub_metrics:
            metric_result = {
                "scenario_id": scenario_id,
                "metric_name": sub_metric["metric_name"],
                "appropriate": False,
                "frequency_logical": False
            }
            
            # Check if metric is appropriate (either matches a key metric or is relevant to scenario)
            sub_name = sub_metric["metric_name"].lower()
            if sub_name in key_metric_names or any(key_term in sub_name for key_term in ["inventory", "order", "delivery", "supplier", "quality"]):
                metric_result["appropriate"] = True
                results["appropriate_metrics"] += 1
            
            # Check if frequency is logical
            sub_freq = sub_metric["frequency"].lower()
            if sub_name in key_frequencies:
                key_freq = key_frequencies[sub_name]
                
                # Exact match or reasonable alternative
                if sub_freq == key_freq:
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
                elif (key_freq == "daily" and sub_freq == "weekly") or (key_freq == "weekly" and sub_freq == "daily"):
                    # Allow for some flexibility between daily and weekly
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
                elif (key_freq == "weekly" and sub_freq == "monthly") or (key_freq == "monthly" and sub_freq == "weekly"):
                    # Allow for some flexibility between weekly and monthly
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
            else:
                # For metrics not in the key, use some heuristics
                if "inventory" in sub_name and sub_freq in ["weekly", "monthly"]:
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
                elif "order" in sub_name and sub_freq in ["daily", "weekly"]:
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
                elif "supplier" in sub_name and sub_freq in ["weekly", "monthly"]:
                    metric_result["frequency_logical"] = True
                    results["logical_frequencies"] += 1
            
            results["details"].append(metric_result)
    
    # Calculate score (20% of total)
    max_score = 20
    metrics_score = (results["appropriate_metrics"] / results["total_metrics"]) * (max_score * 0.6)
    freq_score = (results["logical_frequencies"] / results["total_metrics"]) * (max_score * 0.4)
    
    results["score"] = metrics_score + freq_score
    results["max_score"] = max_score
    
    return results


def evaluate_format_structure(submission: Dict) -> Dict:
    """
    Evaluate the format and structure (10% of total score).
    
    Criteria:
    - Submission must follow the required JSON format
    - All required fields must be present and properly formatted
    """
    results = {
        "format_correct": True,
        "missing_fields": [],
        "details": []
    }
    
    # Check for required top-level fields
    required_top_fields = ["candidate_id", "scenario_analyses"]
    for field in required_top_fields:
        if field not in submission:
            results["format_correct"] = False
            results["missing_fields"].append(field)
    
    # Check scenario analyses
    if "scenario_analyses" in submission:
        scenarios = submission["scenario_analyses"]
        
        # Check if we have the expected number of scenarios (3)
        if len(scenarios) != 3:
            results["details"].append(f"Expected 3 scenarios, got {len(scenarios)}")
            results["format_correct"] = False
        
        # Check each scenario
        for i, scenario in enumerate(scenarios):
            scenario_result = {
                "scenario_index": i,
                "format_correct": True,
                "missing_fields": []
            }
            
            # Check required scenario fields
            required_scenario_fields = ["scenario_id", "key_metrics", "monitoring_metrics"]
            for field in required_scenario_fields:
                if field not in scenario:
                    scenario_result["format_correct"] = False
                    scenario_result["missing_fields"].append(field)
                    results["format_correct"] = False
            
            # Check key metrics
            if "key_metrics" in scenario:
                key_metrics = scenario["key_metrics"]
                
                # Check if we have the expected number of key metrics (3)
                if len(key_metrics) != 3:
                    scenario_result["details"] = f"Expected 3 key metrics, got {len(key_metrics)}"
                    scenario_result["format_correct"] = False
                    results["format_correct"] = False
                
                # Check each key metric
                for j, metric in enumerate(key_metrics):
                    metric_result = {
                        "metric_index": j,
                        "format_correct": True,
                        "missing_fields": []
                    }
                    
                    # Check required metric fields
                    required_metric_fields = ["metric_name", "calculation", "current_value", 
                                             "target_value", "gap", "impact"]
                    for field in required_metric_fields:
                        if field not in metric:
                            metric_result["format_correct"] = False
                            metric_result["missing_fields"].append(field)
                            scenario_result["format_correct"] = False
                            results["format_correct"] = False
                    
                    # Check impact value
                    if "impact" in metric:
                        impact = metric["impact"].lower()
                        if impact not in ["high", "medium", "low"]:
                            metric_result["format_correct"] = False
                            metric_result["details"] = f"Impact must be High, Medium, or Low, got {metric['impact']}"
                            scenario_result["format_correct"] = False
                            results["format_correct"] = False
                    
                    if not metric_result["format_correct"]:
                        if "details" not in scenario_result:
                            scenario_result["details"] = []
                        scenario_result["details"].append(metric_result)
            
            # Check monitoring metrics
            if "monitoring_metrics" in scenario:
                monitoring_metrics = scenario["monitoring_metrics"]
                
                # Check if we have the expected number of monitoring metrics (5)
                if len(monitoring_metrics) != 5:
                    if "details" not in scenario_result:
                        scenario_result["details"] = []
                    scenario_result["details"].append(f"Expected 5 monitoring metrics, got {len(monitoring_metrics)}")
                    scenario_result["format_correct"] = False
                    results["format_correct"] = False
                
                # Check each monitoring metric
                for j, metric in enumerate(monitoring_metrics):
                    metric_result = {
                        "metric_index": j,
                        "format_correct": True,
                        "missing_fields": []
                    }
                    
                    # Check required metric fields
                    required_metric_fields = ["metric_name", "formula", "frequency"]
                    for field in required_metric_fields:
                        if field not in metric:
                            metric_result["format_correct"] = False
                            metric_result["missing_fields"].append(field)
                            scenario_result["format_correct"] = False
                            results["format_correct"] = False
                    
                    # Check frequency value
                    if "frequency" in metric:
                        frequency = metric["frequency"].lower()
                        if frequency not in ["daily", "weekly", "monthly"]:
                            metric_result["format_correct"] = False
                            metric_result["details"] = f"Frequency must be Daily, Weekly, or Monthly, got {metric['frequency']}"
                            scenario_result["format_correct"] = False
                            results["format_correct"] = False
                    
                    if not metric_result["format_correct"]:
                        if "details" not in scenario_result:
                            scenario_result["details"] = []
                        scenario_result["details"].append(metric_result)
            
            if not scenario_result["format_correct"]:
                results["details"].append(scenario_result)
    
    # Calculate score (10% of total)
    max_score = 10
    if results["format_correct"]:
        results["score"] = max_score
    else:
        # Deduct points based on severity of format issues
        deduction = len(results["missing_fields"]) * 2  # 2 points per missing top-level field
        
        # Deduct for scenario issues
        for detail in results["details"]:
            if isinstance(detail, dict) and "missing_fields" in detail:
                deduction += len(detail["missing_fields"])
        
        results["score"] = max(0, max_score - deduction)
    
    results["max_score"] = max_score
    
    return results


def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {
        "metric_selection": evaluate_metric_selection(submission, answer_key),
        "gap_analysis": evaluate_gap_analysis(submission, answer_key),
        "monitoring_recommendations": evaluate_monitoring_recommendations(submission, answer_key),
        "format_structure": evaluate_format_structure(submission)
    }
    
    # Calculate overall score
    total_score = (
        results["metric_selection"]["score"] +
        results["gap_analysis"]["score"] +
        results["monitoring_recommendations"]["score"] +
        results["format_structure"]["score"]
    )
    
    max_score = (
        results["metric_selection"]["max_score"] +
        results["gap_analysis"]["max_score"] +
        results["monitoring_recommendations"]["max_score"] +
        results["format_structure"]["max_score"]
    )
    
    results["overall_score"] = round((total_score / max_score) * 100, 1)
    results["passed"] = results["overall_score"] >= 70.0
    
    return results


def main():
    """Main function to run the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    print("Detailed results saved to test_results.json")


if __name__ == "__main__":
    main()