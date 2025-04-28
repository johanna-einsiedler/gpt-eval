import json
import sys
import math

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    results = {
        "ratio_calculations": {"score": 0, "max_score": 40, "details": {}},
        "company_rankings": {"score": 0, "max_score": 8, "details": {}},
        "regional_comparison": {"score": 0, "max_score": 6, "details": {}}
    }
    
    # Evaluate ratio calculations (40 points total, 1 point per ratio)
    correct_ratios = 0
    total_ratios = 0
    ratio_details = {}
    
    for company in answer_key["task1"]["ratio_calculations"]:
        ratio_details[company] = {}
        for ratio, correct_value in answer_key["task1"]["ratio_calculations"][company].items():
            total_ratios += 1
            
            if company in submission["task1"]["ratio_calculations"] and ratio in submission["task1"]["ratio_calculations"][company]:
                submitted_value = submission["task1"]["ratio_calculations"][company][ratio]
                difference = abs(submitted_value - correct_value)
                
                if difference <= 0.05:
                    correct_ratios += 1
                    ratio_details[company][ratio] = {"correct": True, "submitted": submitted_value, "expected": correct_value}
                else:
                    ratio_details[company][ratio] = {"correct": False, "submitted": submitted_value, "expected": correct_value}
            else:
                ratio_details[company][ratio] = {"correct": False, "submitted": "missing", "expected": correct_value}
    
    results["ratio_calculations"]["score"] = int((correct_ratios / total_ratios) * 40)
    results["ratio_calculations"]["details"] = ratio_details
    
    # Evaluate company rankings (8 points total, 1 point per correct ranking)
    correct_rankings = 0
    ranking_details = {}
    
    # Create dictionaries for easy lookup
    submitted_rankings = {item["rank"]: item["company"] for item in submission["task1"]["company_rankings"]}
    correct_rankings_dict = {item["rank"]: item["company"] for item in answer_key["task1"]["company_rankings"]}
    
    for rank in range(1, 9):
        if rank in submitted_rankings and rank in correct_rankings_dict:
            if submitted_rankings[rank] == correct_rankings_dict[rank]:
                correct_rankings += 1
                ranking_details[rank] = {"correct": True, "submitted": submitted_rankings[rank], "expected": correct_rankings_dict[rank]}
            else:
                ranking_details[rank] = {"correct": False, "submitted": submitted_rankings[rank], "expected": correct_rankings_dict[rank]}
        else:
            ranking_details[rank] = {"correct": False, "submitted": "missing", "expected": correct_rankings_dict.get(rank, "missing")}
    
    results["company_rankings"]["score"] = correct_rankings
    results["company_rankings"]["details"] = ranking_details
    
    # Evaluate regional comparison (6 points total, 1 point per correct average)
    correct_averages = 0
    regional_details = {}
    
    for region in answer_key["task1"]["regional_comparison"]:
        regional_details[region] = {}
        for metric, correct_value in answer_key["task1"]["regional_comparison"][region].items():
            if region in submission["task1"]["regional_comparison"] and metric in submission["task1"]["regional_comparison"][region]:
                submitted_value = submission["task1"]["regional_comparison"][region][metric]
                difference = abs(submitted_value - correct_value)
                
                if difference <= 0.10:
                    correct_averages += 1
                    regional_details[region][metric] = {"correct": True, "submitted": submitted_value, "expected": correct_value}
                else:
                    regional_details[region][metric] = {"correct": False, "submitted": submitted_value, "expected": correct_value}
            else:
                regional_details[region][metric] = {"correct": False, "submitted": "missing", "expected": correct_value}
    
    results["regional_comparison"]["score"] = correct_averages
    results["regional_comparison"]["details"] = regional_details
    
    # Calculate total score for Task 1
    task1_score = results["ratio_calculations"]["score"] + results["company_rankings"]["score"] + results["regional_comparison"]["score"]
    task1_max_score = results["ratio_calculations"]["max_score"] + results["company_rankings"]["max_score"] + results["regional_comparison"]["max_score"]
    
    return {
        "details": results,
        "score": task1_score,
        "max_score": task1_max_score,
        "percentage": round((task1_score / task1_max_score) * 100, 2)
    }

def evaluate_task2(submission, answer_key):
    results = {
        "credit_risk_scores": {"score": 0, "max_score": 8, "details": {}},
        "highest_risk_region": {"score": 0, "max_score": 1, "details": {}},
        "days_past_due_pct_diff": {"score": 0, "max_score": 3, "details": {}}
    }
    
    # Evaluate credit risk scores (8 points total, 1 point per correct score)
    correct_scores = 0
    score_details = {}
    
    # Create dictionaries for easy lookup
    submitted_scores = {item["company"]: item["risk_score"] for item in submission["task2"]["credit_risk_scores"]}
    correct_scores_dict = {item["company"]: item["risk_score"] for item in answer_key["task2"]["credit_risk_scores"]}
    
    for company, correct_value in correct_scores_dict.items():
        if company in submitted_scores:
            submitted_value = submitted_scores[company]
            difference = abs(submitted_value - correct_value)
            
            if difference <= 0.50:
                correct_scores += 1
                score_details[company] = {"correct": True, "submitted": submitted_value, "expected": correct_value}
            else:
                score_details[company] = {"correct": False, "submitted": submitted_value, "expected": correct_value}
        else:
            score_details[company] = {"correct": False, "submitted": "missing", "expected": correct_value}
    
    results["credit_risk_scores"]["score"] = correct_scores
    results["credit_risk_scores"]["details"] = score_details
    
    # Evaluate highest risk region (1 point)
    submitted_region = submission["task2"]["regional_patterns"]["highest_risk_region"]
    correct_region = answer_key["task2"]["regional_patterns"]["highest_risk_region"]
    
    if submitted_region == correct_region:
        results["highest_risk_region"]["score"] = 1
        results["highest_risk_region"]["details"] = {"correct": True, "submitted": submitted_region, "expected": correct_region}
    else:
        results["highest_risk_region"]["details"] = {"correct": False, "submitted": submitted_region, "expected": correct_region}
    
    # Evaluate days past due percentage differences (3 points total, 1 point per correct difference)
    correct_diffs = 0
    diff_details = {}
    
    for region, correct_value in answer_key["task2"]["regional_patterns"]["days_past_due_pct_diff"].items():
        if region in submission["task2"]["regional_patterns"]["days_past_due_pct_diff"]:
            submitted_value = submission["task2"]["regional_patterns"]["days_past_due_pct_diff"][region]
            difference = abs(submitted_value - correct_value)
            
            if difference <= 1.00:
                correct_diffs += 1
                diff_details[region] = {"correct": True, "submitted": submitted_value, "expected": correct_value}
            else:
                diff_details[region] = {"correct": False, "submitted": submitted_value, "expected": correct_value}
        else:
            diff_details[region] = {"correct": False, "submitted": "missing", "expected": correct_value}
    
    results["days_past_due_pct_diff"]["score"] = correct_diffs
    results["days_past_due_pct_diff"]["details"] = diff_details
    
    # Calculate total score for Task 2
    task2_score = results["credit_risk_scores"]["score"] + results["highest_risk_region"]["score"] + results["days_past_due_pct_diff"]["score"]
    task2_max_score = results["credit_risk_scores"]["max_score"] + results["highest_risk_region"]["max_score"] + results["days_past_due_pct_diff"]["max_score"]
    
    return {
        "details": results,
        "score": task2_score,
        "max_score": task2_max_score,
        "percentage": round((task2_score / task2_max_score) * 100, 2)
    }

def evaluate_task3(submission, answer_key):
    results = {
        "matched_pairs": {"score": 0, "max_score": 4, "details": {}},
        "performance_metrics": {"score": 0, "max_score": 12, "details": {}},
        "largest_positive_roe_deviation": {"score": 0, "max_score": 3, "details": {}}
    }
    
    # Evaluate matched pairs (4 points total, 1 point per correct pair)
    correct_pairs = 0
    pair_details = {}
    
    # Create sets of pairs for comparison (order doesn't matter)
    submitted_pairs = []
    for pair in submission["task3"]["matched_pairs"]:
        companies = sorted([pair["company1"], pair["company2"]])
        submitted_pairs.append(tuple(companies))
    
    correct_pairs_list = []
    for pair in answer_key["task3"]["matched_pairs"]:
        companies = sorted([pair["company1"], pair["company2"]])
        correct_pairs_list.append(tuple(companies))
    
    for i, correct_pair in enumerate(correct_pairs_list):
        pair_found = False
        for submitted_pair in submitted_pairs:
            if set(submitted_pair) == set(correct_pair):
                correct_pairs += 1
                pair_details[f"pair{i+1}"] = {"correct": True, "submitted": list(submitted_pair), "expected": list(correct_pair)}
                pair_found = True
                break
        
        if not pair_found:
            pair_details[f"pair{i+1}"] = {"correct": False, "submitted": "not matched", "expected": list(correct_pair)}
    
    results["matched_pairs"]["score"] = correct_pairs
    results["matched_pairs"]["details"] = pair_details
    
    # Evaluate performance metrics (12 points total, 1 point per correct difference)
    correct_metrics = 0
    metric_details = {}
    
    for pair_key in ["pair1", "pair2", "pair3", "pair4"]:
        if pair_key in answer_key["task3"]["performance_metrics"] and pair_key in submission["task3"]["performance_metrics"]:
            metric_details[pair_key] = {}
            
            for metric in ["current_ratio_diff", "roa_diff", "credit_utilization_diff"]:
                if metric in answer_key["task3"]["performance_metrics"][pair_key] and metric in submission["task3"]["performance_metrics"][pair_key]:
                    correct_value = answer_key["task3"]["performance_metrics"][pair_key][metric]
                    submitted_value = submission["task3"]["performance_metrics"][pair_key][metric]
                    difference = abs(submitted_value - correct_value)
                    
                    if difference <= 0.10:
                        correct_metrics += 1
                        metric_details[pair_key][metric] = {"correct": True, "submitted": submitted_value, "expected": correct_value}
                    else:
                        metric_details[pair_key][metric] = {"correct": False, "submitted": submitted_value, "expected": correct_value}
                else:
                    metric_details[pair_key][metric] = {"correct": False, "submitted": "missing", "expected": answer_key["task3"]["performance_metrics"][pair_key].get(metric, "missing")}
    
    results["performance_metrics"]["score"] = correct_metrics
    results["performance_metrics"]["details"] = metric_details
    
    # Evaluate largest positive ROE deviation (3 points total, 1 point per correct company)
    correct_deviations = 0
    deviation_details = {}
    
    for region in answer_key["task3"]["performance_metrics"]["largest_positive_roe_deviation"]:
        correct_company = answer_key["task3"]["performance_metrics"]["largest_positive_roe_deviation"][region]
        
        if "largest_positive_roe_deviation" in submission["task3"]["performance_metrics"] and region in submission["task3"]["performance_metrics"]["largest_positive_roe_deviation"]:
            submitted_company = submission["task3"]["performance_metrics"]["largest_positive_roe_deviation"][region]
            
            if submitted_company == correct_company:
                correct_deviations += 1
                deviation_details[region] = {"correct": True, "submitted": submitted_company, "expected": correct_company}
            else:
                deviation_details[region] = {"correct": False, "submitted": submitted_company, "expected": correct_company}
        else:
            deviation_details[region] = {"correct": False, "submitted": "missing", "expected": correct_company}
    
    results["largest_positive_roe_deviation"]["score"] = correct_deviations
    results["largest_positive_roe_deviation"]["details"] = deviation_details
    
    # Calculate total score for Task 3
    task3_score = results["matched_pairs"]["score"] + results["performance_metrics"]["score"] + results["largest_positive_roe_deviation"]["score"]
    task3_max_score = results["matched_pairs"]["max_score"] + results["performance_metrics"]["max_score"] + results["largest_positive_roe_deviation"]["max_score"]
    
    return {
        "details": results,
        "score": task3_score,
        "max_score": task3_max_score,
        "percentage": round((task3_score / task3_max_score) * 100, 2)
    }

def check_automatic_failure(submission, task_results):
    # Check if submission is in the required JSON format
    if not isinstance(submission, dict):
        return True, "Submission is not in the required JSON format"
    
    # Check if at least 75% of required calculations are completed
    total_calculations = 0
    completed_calculations = 0
    
    # Count ratio calculations
    if "task1" in submission and "ratio_calculations" in submission["task1"]:
        for company in submission["task1"]["ratio_calculations"]:
            for ratio in submission["task1"]["ratio_calculations"][company]:
                total_calculations += 1
                if submission["task1"]["ratio_calculations"][company][ratio] != "missing":
                    completed_calculations += 1
    
    # Count credit risk scores
    if "task2" in submission and "credit_risk_scores" in submission["task2"]:
        total_calculations += len(submission["task2"]["credit_risk_scores"])
        completed_calculations += len(submission["task2"]["credit_risk_scores"])
    
    # Count performance metrics
    if "task3" in submission and "performance_metrics" in submission["task3"]:
        for pair_key in ["pair1", "pair2", "pair3", "pair4"]:
            if pair_key in submission["task3"]["performance_metrics"]:
                for metric in ["current_ratio_diff", "roa_diff", "credit_utilization_diff"]:
                    if metric in submission["task3"]["performance_metrics"][pair_key]:
                        total_calculations += 1
                        if submission["task3"]["performance_metrics"][pair_key][metric] != "missing":
                            completed_calculations += 1
    
    if total_calculations > 0 and (completed_calculations / total_calculations) < 0.75:
        return True, f"Less than 75% of required calculations completed ({completed_calculations}/{total_calculations})"
    
    # Check for significant conceptual errors
    # This is more subjective, but we can use the task scores as a proxy
    task1_percentage = task_results["task1"]["percentage"]
    task2_percentage = task_results["task2"]["percentage"]
    task3_percentage = task_results["task3"]["percentage"]
    
    if task1_percentage < 30 or task2_percentage < 30 or task3_percentage < 30:
        return True, "Significant conceptual errors detected in one or more tasks"
    
    return False, ""

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json(submission_file)
    answer_key = load_json(answer_key_file)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    task1_weighted = task1_results["percentage"] * 0.4  # 40% weight
    task2_weighted = task2_results["percentage"] * 0.3  # 30% weight
    task3_weighted = task3_results["percentage"] * 0.3  # 30% weight
    
    overall_score = task1_weighted + task2_weighted + task3_weighted
    
    # Check for automatic failure conditions
    auto_fail, fail_reason = check_automatic_failure(submission, {
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    })
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passing_score": 70.0,
        "passed": overall_score >= 70.0 and not auto_fail,
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results,
        "automatic_failure": {
            "failed": auto_fail,
            "reason": fail_reason if auto_fail else "N/A"
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    if auto_fail:
        print(f"Automatic failure: {fail_reason}")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()