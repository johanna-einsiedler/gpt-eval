import json
import sys
import numpy as np
import re

def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check if code snippet exists and implements SIR model correctly
    code_snippet = submission.get("task1", {}).get("model_implementation", {}).get("code_snippet", "")
    
    # Check for key components in the code
    sir_implementation_score = 0
    if "dS/dt" in code_snippet or "S[t+1] = S[t]" in code_snippet or re.search(r'S\[\w+\+1\]\s*=\s*S\[\w+\]', code_snippet):
        sir_implementation_score += 5
    if "dI/dt" in code_snippet or "I[t+1] = I[t]" in code_snippet or re.search(r'I\[\w+\+1\]\s*=\s*I\[\w+\]', code_snippet):
        sir_implementation_score += 5
    if "dR/dt" in code_snippet or "R[t+1] = R[t]" in code_snippet or re.search(r'R\[\w+\+1\]\s*=\s*R\[\w+\]', code_snippet):
        sir_implementation_score += 5
    
    results["details"]["sir_model_implementation"] = {
        "score": sir_implementation_score,
        "max_score": 15,
        "comments": "Evaluation of SIR model implementation in code"
    }
    
    # Check if tracking daily new infections correctly
    tracking_score = 0
    if "new_infections" in code_snippet or "new_cases" in code_snippet:
        tracking_score += 10
    
    results["details"]["tracking_new_infections"] = {
        "score": tracking_score,
        "max_score": 10,
        "comments": "Evaluation of tracking daily new infections"
    }
    
    # Check initial simulation results
    initial_sim = submission.get("task1", {}).get("initial_simulation", [])
    answer_sim = answer_key.get("task1", {}).get("initial_simulation", [])
    
    sim_score = 0
    if len(initial_sim) > 0:
        # Check if the peak is in a reasonable range
        submission_peak_day = np.argmax(initial_sim) + 1 if len(initial_sim) > 0 else 0
        answer_peak_day = np.argmax(answer_sim) + 1 if len(answer_sim) > 0 else 0
        
        # Allow for some variation in peak day (±5 days)
        if abs(submission_peak_day - answer_peak_day) <= 5:
            sim_score += 3
            
        # Check if the peak magnitude is reasonable (within 30%)
        submission_peak = max(initial_sim) if len(initial_sim) > 0 else 0
        answer_peak = max(answer_sim) if len(answer_sim) > 0 else 0
        
        if answer_peak > 0 and 0.7 * answer_peak <= submission_peak <= 1.3 * answer_peak:
            sim_score += 2
    
    results["details"]["initial_simulation_quality"] = {
        "score": sim_score,
        "max_score": 5,
        "comments": "Evaluation of initial simulation results"
    }
    
    # Calculate total score for Task 1
    results["score"] = sir_implementation_score + tracking_score + sim_score
    
    return results

def evaluate_task2(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 40,
        "details": {}
    }
    
    # Check calibrated parameters
    param_score = 0
    sub_beta = submission.get("task2", {}).get("calibrated_parameters", {}).get("beta", 0)
    sub_gamma = submission.get("task2", {}).get("calibrated_parameters", {}).get("gamma", 0)
    
    key_beta = answer_key.get("task2", {}).get("calibrated_parameters", {}).get("beta", 0)
    key_gamma = answer_key.get("task2", {}).get("calibrated_parameters", {}).get("gamma", 0)
    
    # Check if beta is within acceptable range (0.38-0.42)
    if 0.38 <= sub_beta <= 0.42:
        param_score += 10
    elif 0.35 <= sub_beta <= 0.45:  # Slightly wider range for partial credit
        param_score += 5
    
    # Check if gamma is within acceptable range (0.14-0.16)
    if 0.14 <= sub_gamma <= 0.16:
        param_score += 10
    elif 0.13 <= sub_gamma <= 0.17:  # Slightly wider range for partial credit
        param_score += 5
    
    results["details"]["parameter_calibration"] = {
        "score": param_score,
        "max_score": 20,
        "comments": f"Evaluation of calibrated parameters. Submitted: β={sub_beta}, γ={sub_gamma}. Expected: β≈{key_beta}, γ≈{key_gamma}"
    }
    
    # Check peak identification
    peak_score = 0
    sub_peak_day = submission.get("task2", {}).get("peak_day", 0)
    sub_peak_cases = submission.get("task2", {}).get("peak_cases", 0)
    
    key_peak_day = answer_key.get("task2", {}).get("peak_day", 0)
    key_peak_cases = answer_key.get("task2", {}).get("peak_cases", 0)
    
    # Check peak day (allow ±2 days)
    if abs(sub_peak_day - key_peak_day) <= 2:
        peak_score += 5
    
    # Check peak cases (allow ±10%)
    if key_peak_cases > 0 and 0.9 * key_peak_cases <= sub_peak_cases <= 1.1 * key_peak_cases:
        peak_score += 5
    
    results["details"]["peak_identification"] = {
        "score": peak_score,
        "max_score": 10,
        "comments": f"Evaluation of peak identification. Submitted: day={sub_peak_day}, cases={sub_peak_cases}. Expected: day≈{key_peak_day}, cases≈{key_peak_cases}"
    }
    
    # Check total cases
    total_score = 0
    sub_total_cases = submission.get("task2", {}).get("total_cases", 0)
    key_total_cases = answer_key.get("task2", {}).get("total_cases", 0)
    
    # Check total cases (allow ±10%)
    if key_total_cases > 0 and 0.9 * key_total_cases <= sub_total_cases <= 1.1 * key_total_cases:
        total_score += 10
    elif key_total_cases > 0 and 0.8 * key_total_cases <= sub_total_cases <= 1.2 * key_total_cases:
        total_score += 5  # Partial credit for being within 20%
    
    results["details"]["total_cases_calculation"] = {
        "score": total_score,
        "max_score": 10,
        "comments": f"Evaluation of total cases calculation. Submitted: {sub_total_cases}. Expected: ≈{key_total_cases}"
    }
    
    # Calculate total score for Task 2
    results["score"] = param_score + peak_score + total_score
    
    return results

def evaluate_task3(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 30,
        "details": {}
    }
    
    # Check intervention implementation
    intervention_score = 0
    intervention_sim = submission.get("task3", {}).get("intervention_simulation", [])
    
    # Check if intervention simulation exists and has reasonable length
    if len(intervention_sim) > 0:
        # Check if the intervention actually reduces the peak compared to task2
        task2_sim = submission.get("task2", {}).get("calibrated_simulation", [])
        if len(task2_sim) > 0 and max(intervention_sim) < max(task2_sim):
            intervention_score += 10
        elif len(task2_sim) > 0 and max(intervention_sim) < 0.9 * max(task2_sim):
            intervention_score += 5  # Partial credit
    
    results["details"]["intervention_implementation"] = {
        "score": intervention_score,
        "max_score": 10,
        "comments": "Evaluation of intervention implementation"
    }
    
    # Check peak reduction
    peak_reduction_score = 0
    sub_peak_reduction = submission.get("task3", {}).get("reduction_peak_percentage", 0)
    
    # Check if peak reduction is at least 45%
    if sub_peak_reduction >= 45:
        peak_reduction_score += 10
    elif sub_peak_reduction >= 30:  # Partial credit
        peak_reduction_score += 5
    
    results["details"]["peak_reduction"] = {
        "score": peak_reduction_score,
        "max_score": 10,
        "comments": f"Evaluation of peak reduction. Submitted: {sub_peak_reduction}%. Required: ≥45%"
    }
    
    # Check calculation accuracy
    calc_score = 0
    sub_total_reduction = submission.get("task3", {}).get("reduction_total_percentage", 0)
    sub_threshold = submission.get("task3", {}).get("recommended_threshold", 0)
    
    # Check if threshold is in a reasonable range (25-35)
    if 25 <= sub_threshold <= 35:
        calc_score += 5
    elif 20 <= sub_threshold <= 40:  # Wider range for partial credit
        calc_score += 3
    
    # Check if total reduction percentage is reasonable (30-40%)
    if 30 <= sub_total_reduction <= 40:
        calc_score += 5
    elif 25 <= sub_total_reduction <= 45:  # Wider range for partial credit
        calc_score += 3
    
    results["details"]["calculation_accuracy"] = {
        "score": calc_score,
        "max_score": 10,
        "comments": f"Evaluation of calculation accuracy. Threshold: {sub_threshold}, Total reduction: {sub_total_reduction}%"
    }
    
    # Calculate total score for Task 3
    results["score"] = intervention_score + peak_reduction_score + calc_score
    
    return results

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "passing_threshold": 70,
        "tasks": {}
    }
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    results["tasks"]["task1"] = task1_results
    results["tasks"]["task2"] = task2_results
    results["tasks"]["task3"] = task3_results
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    total_possible = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    # Check if each task meets the minimum 60% requirement
    task1_percent = (task1_results["score"] / task1_results["max_score"]) * 100
    task2_percent = (task2_results["score"] / task2_results["max_score"]) * 100
    task3_percent = (task3_results["score"] / task3_results["max_score"]) * 100
    
    results["task_percentages"] = {
        "task1": round(task1_percent, 2),
        "task2": round(task2_percent, 2),
        "task3": round(task3_percent, 2)
    }
    
    # Determine if the candidate passed
    passed = results["overall_score"] >= results["passing_threshold"] and \
             task1_percent >= 60 and task2_percent >= 60 and task3_percent >= 60
    
    results["passed"] = passed
    
    if not passed:
        if results["overall_score"] < results["passing_threshold"]:
            results["failure_reason"] = "Overall score below passing threshold"
        elif task1_percent < 60:
            results["failure_reason"] = "Task 1 score below 60% requirement"
        elif task2_percent < 60:
            results["failure_reason"] = "Task 2 score below 60% requirement"
        elif task3_percent < 60:
            results["failure_reason"] = "Task 3 score below 60% requirement"
    
    return results

def main():
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
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()