#!/usr/bin/env python3
import json
import sys
import math
import numpy as np

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def is_within_tolerance(value, expected, tolerance=0.05):
    """Check if a value is within the specified tolerance of the expected value."""
    if expected == 0:
        return abs(value) < tolerance
    return abs((value - expected) / expected) <= tolerance

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Simple Random Sampling."""
    score = 0
    feedback = []
    
    # Check sample size
    sample_ids = submission.get('sample_ids', [])
    if len(sample_ids) == 500:
        score += 5
        feedback.append("Correct sample size of 500.")
    else:
        feedback.append(f"Incorrect sample size. Expected 500, got {len(sample_ids)}.")
    
    # Check if sample IDs are valid (just check if they're integers)
    if all(isinstance(id, int) for id in sample_ids) and len(sample_ids) > 0:
        score += 5
        feedback.append("Valid sample IDs provided.")
    else:
        feedback.append("Invalid sample IDs. Expected integers.")
    
    # Check sample mean
    sample_mean = submission.get('sample_mean', 0)
    expected_mean = answer_key.get('sample_mean', 0)
    if is_within_tolerance(sample_mean, expected_mean):
        score += 5
        feedback.append("Sample mean is within acceptable range.")
    else:
        feedback.append(f"Sample mean is outside acceptable range. Got {sample_mean}, expected approximately {expected_mean}.")
    
    # Check sample variance
    sample_variance = submission.get('sample_variance', 0)
    expected_variance = answer_key.get('sample_variance', 0)
    if is_within_tolerance(sample_variance, expected_variance):
        score += 5
        feedback.append("Sample variance is within acceptable range.")
    else:
        feedback.append(f"Sample variance is outside acceptable range. Got {sample_variance}, expected approximately {expected_variance}.")
    
    # Check sampling error
    sampling_error = submission.get('sampling_error', 0)
    expected_error = answer_key.get('sampling_error', 0)
    if is_within_tolerance(sampling_error, expected_error):
        score += 10
        feedback.append("Sampling error is within acceptable range.")
    else:
        feedback.append(f"Sampling error is outside acceptable range. Got {sampling_error}, expected approximately {expected_error}.")
    
    return score, feedback

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Stratified Sampling."""
    score = 0
    feedback = []
    
    # Check strata counts
    strata_counts = submission.get('strata_counts', {})
    expected_counts = answer_key.get('strata_counts', {})
    
    if set(strata_counts.keys()) == set(expected_counts.keys()):
        count_correct = True
        for region in expected_counts:
            if strata_counts.get(region, 0) != expected_counts.get(region, 0):
                count_correct = False
                feedback.append(f"Incorrect count for {region}. Got {strata_counts.get(region, 0)}, expected {expected_counts.get(region, 0)}.")
        
        if count_correct:
            score += 5
            feedback.append("All strata counts are correct.")
    else:
        feedback.append("Missing or incorrect strata regions.")
    
    # Check sample IDs
    sample_ids = submission.get('sample_ids', [])
    if len(sample_ids) == 800:
        score += 10
        feedback.append("Correct total sample size of 800.")
    else:
        feedback.append(f"Incorrect total sample size. Expected 800, got {len(sample_ids)}.")
    
    # Check if sample IDs are valid
    if all(isinstance(id, int) for id in sample_ids) and len(sample_ids) > 0:
        score += 5
        feedback.append("Valid sample IDs provided.")
    else:
        feedback.append("Invalid sample IDs. Expected integers.")
    
    # Check stratum means
    stratum_means = submission.get('stratum_means', {})
    expected_means = answer_key.get('stratum_means', {})
    
    if set(stratum_means.keys()) == set(expected_means.keys()):
        means_correct = True
        for region in expected_means:
            if not is_within_tolerance(stratum_means.get(region, 0), expected_means.get(region, 0)):
                means_correct = False
                feedback.append(f"Mean for {region} is outside acceptable range. Got {stratum_means.get(region, 0)}, expected approximately {expected_means.get(region, 0)}.")
        
        if means_correct:
            score += 15
            feedback.append("All stratum means are within acceptable ranges.")
    else:
        feedback.append("Missing or incorrect stratum regions for means calculation.")
    
    return score, feedback

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Cluster Sampling."""
    score = 0
    feedback = []
    
    # Check required sample size
    required_size = submission.get('required_sample_size', 0)
    expected_size = answer_key.get('required_sample_size', 0)
    if is_within_tolerance(required_size, expected_size):
        score += 10
        feedback.append("Required sample size is within acceptable range.")
    else:
        feedback.append(f"Required sample size is outside acceptable range. Got {required_size}, expected approximately {expected_size}.")
    
    # Check cluster IDs
    cluster_ids = submission.get('cluster_ids', [])
    if len(cluster_ids) > 0 and all(isinstance(id, str) for id in cluster_ids):
        score += 10
        feedback.append("Valid cluster IDs provided.")
    else:
        feedback.append("Invalid or missing cluster IDs.")
    
    # Check total respondents
    total_respondents = submission.get('total_respondents', 0)
    # For this, we're more lenient since it depends on which clusters were selected
    if total_respondents > 0:
        score += 5
        feedback.append("Total respondents value provided.")
    else:
        feedback.append("Missing or invalid total respondents value.")
    
    # Check design effect
    design_effect = submission.get('design_effect', 0)
    expected_effect = answer_key.get('design_effect', 0)
    if is_within_tolerance(design_effect, expected_effect):
        score += 10
        feedback.append("Design effect is within acceptable range.")
    else:
        feedback.append(f"Design effect is outside acceptable range. Got {design_effect}, expected approximately {expected_effect}.")
    
    return score, feedback

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "tasks": {}
    }
    
    # Evaluate Task 1
    task1_score, task1_feedback = evaluate_task1(submission.get('task1', {}), answer_key.get('task1', {}))
    results["tasks"]["task1"] = {
        "score": task1_score,
        "max_score": 30,
        "feedback": task1_feedback
    }
    
    # Evaluate Task 2
    task2_score, task2_feedback = evaluate_task2(submission.get('task2', {}), answer_key.get('task2', {}))
    results["tasks"]["task2"] = {
        "score": task2_score,
        "max_score": 35,
        "feedback": task2_feedback
    }
    
    # Evaluate Task 3
    task3_score, task3_feedback = evaluate_task3(submission.get('task3', {}), answer_key.get('task3', {}))
    results["tasks"]["task3"] = {
        "score": task3_score,
        "max_score": 35,
        "feedback": task3_feedback
    }
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    max_score = 100
    overall_percentage = (total_score / max_score) * 100
    
    # Check minimum requirements
    passed_minimum = (task1_score >= 15 and task2_score >= 18 and task3_score >= 18)
    
    results["total_score"] = total_score
    results["max_score"] = max_score
    results["overall_score"] = round(overall_percentage, 2)
    results["passed_minimum_requirements"] = passed_minimum
    results["passed_exam"] = overall_percentage >= 70 and passed_minimum
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed exam: {results['passed_exam']}")

if __name__ == "__main__":
    main()