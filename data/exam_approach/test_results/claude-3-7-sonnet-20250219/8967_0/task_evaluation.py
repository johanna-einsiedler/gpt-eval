#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate Task 1: Probability Theory Examination and Sampling Method Improvement."""
    score = 0
    feedback = []
    
    # Check distribution analysis
    if "distribution_analysis" in submission:
        content = submission["distribution_analysis"].lower()
        if ("skewed" in content or "skew" in content) and "right" in content:
            if any(cat in content for cat in ["categor", "electronics", "groceries", "furniture"]):
                score += 1
                feedback.append("Correctly identified skewed distribution and category patterns")
            else:
                score += 0.5
                feedback.append("Identified skewed distribution but missed category-specific patterns")
        else:
            feedback.append("Failed to identify the right-skewed nature of the distribution")
    else:
        feedback.append("Missing distribution analysis")
    
    # Check limitations
    if "current_method_limitations" in submission and isinstance(submission["current_method_limitations"], list):
        limitations = submission["current_method_limitations"]
        if len(limitations) >= 2:
            has_value_point = any("value" in lim.lower() or "high" in lim.lower() for lim in limitations)
            has_skew_point = any("skew" in lim.lower() or "distribut" in lim.lower() for lim in limitations)
            
            if has_value_point and has_skew_point:
                score += 0.5
                feedback.append("Identified key limitations related to transaction values and distribution")
            elif has_value_point or has_skew_point:
                score += 0.25
                feedback.append("Partially identified limitations of simple random sampling")
            else:
                feedback.append("Limitations identified were not relevant to the problem")
        else:
            feedback.append("Insufficient number of limitations identified")
    else:
        feedback.append("Missing or invalid limitations section")
    
    # Check proposed method
    if "proposed_method" in submission:
        method = submission["proposed_method"].lower()
        if ("stratif" in method or "mus" in method or "monetary unit" in method):
            if "probability" in method and ("size" in method or "proportion" in method):
                score += 0.5
                feedback.append("Proposed appropriate stratified sampling with probability proportional to size")
            else:
                score += 0.25
                feedback.append("Proposed stratification but without clear probability proportional to size approach")
        else:
            feedback.append("Proposed method does not address the key issues")
    else:
        feedback.append("Missing proposed method")
    
    # Check theoretical foundation
    if "theoretical_foundation" in submission:
        theory = submission["theoretical_foundation"].lower()
        if any(term in theory for term in ["neyman", "optimal allocation", "variance"]):
            score += 0.5
            feedback.append("Provided sound theoretical foundation")
        else:
            score += 0.25
            feedback.append("Theoretical foundation present but lacks key concepts")
    else:
        feedback.append("Missing theoretical foundation")
    
    # Check metrics and code
    if "improvement_metrics" in submission and isinstance(submission["improvement_metrics"], dict):
        if len(submission["improvement_metrics"]) >= 2:
            score += 0.25
            feedback.append("Provided multiple relevant metrics")
        else:
            feedback.append("Insufficient metrics provided")
    else:
        feedback.append("Missing or invalid improvement metrics")
    
    if "code_snippet" in submission and len(submission["code_snippet"]) > 0:
        code = submission["code_snippet"].lower()
        if "import" in code and ("sample" in code or "stratif" in code):
            score += 0.25
            feedback.append("Provided relevant code implementation")
        else:
            feedback.append("Code snippet lacks key implementation details")
    else:
        feedback.append("Missing code snippet")
    
    # Determine final score level (0-3)
    final_score = 0
    if score >= 2.5:
        final_score = 3  # Excellent
    elif score >= 1.5:
        final_score = 2  # Satisfactory
    elif score >= 0.5:
        final_score = 1  # Needs Improvement
    
    result = {
        "score": final_score,
        "max_score": 3,
        "level": ["Failing", "Needs Improvement", "Satisfactory", "Excellent"][final_score],
        "feedback": feedback
    }
    
    return final_score, result

def evaluate_task2(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate Task 2: Inference Theory Examination."""
    score = 0
    feedback = []
    
    # Check method summary
    if "method_summary" in submission:
        summary = submission["method_summary"].lower()
        if "bootstrap" in summary and "adjust" in summary and "skew" in summary:
            score += 0.5
            feedback.append("Correctly summarized the Adjusted Percentile Bootstrap method")
        else:
            score += 0.25
            feedback.append("Method summary incomplete or partially incorrect")
    else:
        feedback.append("Missing method summary")
    
    # Check theoretical limitations
    if "theoretical_limitations" in submission and isinstance(submission["theoretical_limitations"], list):
        limitations = submission["theoretical_limitations"]
        if len(limitations) >= 3:
            has_adjustment_issue = any("adjust" in lim.lower() and "function" in lim.lower() for lim in limitations)
            has_sample_size_issue = any("sample size" in lim.lower() or "small sample" in lim.lower() for lim in limitations)
            
            if has_adjustment_issue and has_sample_size_issue:
                score += 0.5
                feedback.append("Identified key limitations including adjustment function and sample size issues")
            elif has_adjustment_issue or has_sample_size_issue:
                score += 0.25
                feedback.append("Partially identified theoretical limitations")
            else:
                feedback.append("Limitations identified were not the most relevant")
        else:
            feedback.append("Insufficient number of limitations identified")
    else:
        feedback.append("Missing or invalid theoretical limitations")
    
    # Check mathematical assumptions
    if "mathematical_assumptions" in submission and isinstance(submission["mathematical_assumptions"], list):
        if len(submission["mathematical_assumptions"]) >= 3:
            score += 0.5
            feedback.append("Identified multiple relevant mathematical assumptions")
        else:
            score += 0.25
            feedback.append("Insufficient mathematical assumptions identified")
    else:
        feedback.append("Missing or invalid mathematical assumptions")
    
    # Check empirical results
    if "empirical_results" in submission and isinstance(submission["empirical_results"], dict):
        empirical = submission["empirical_results"]
        has_proposed_ci = "proposed_method_CI" in empirical and isinstance(empirical["proposed_method_CI"], list) and len(empirical["proposed_method_CI"]) == 2
        has_standard_ci = "standard_method_CI" in empirical and isinstance(empirical["standard_method_CI"], list) and len(empirical["standard_method_CI"]) == 2
        
        if has_proposed_ci and has_standard_ci:
            score += 0.5
            feedback.append("Correctly implemented and compared both confidence interval methods")
        elif has_proposed_ci or has_standard_ci:
            score += 0.25
            feedback.append("Partially implemented confidence interval methods")
        else:
            feedback.append("Failed to properly implement confidence interval methods")
    else:
        feedback.append("Missing or invalid empirical results")
    
    # Check theoretical improvement
    if "theoretical_improvement" in submission:
        improvement = submission["theoretical_improvement"].lower()
        if any(term in improvement for term in ["edgeworth", "expansion", "asymptotic"]):
            score += 0.5
            feedback.append("Proposed theoretically sound improvement based on asymptotic theory")
        else:
            score += 0.25
            feedback.append("Proposed improvement lacks strong theoretical justification")
    else:
        feedback.append("Missing theoretical improvement")
    
    # Check code snippet
    if "code_snippet" in submission and len(submission["code_snippet"]) > 0:
        code = submission["code_snippet"].lower()
        if "bootstrap" in code and "percentile" in code:
            score += 0.5
            feedback.append("Provided relevant code implementation for bootstrap confidence intervals")
        else:
            score += 0.25
            feedback.append("Code snippet lacks key implementation details")
    else:
        feedback.append("Missing code snippet")
    
    # Determine final score level (0-3)
    final_score = 0
    if score >= 2.5:
        final_score = 3  # Excellent
    elif score >= 1.5:
        final_score = 2  # Satisfactory
    elif score >= 0.5:
        final_score = 1  # Needs Improvement
    
    result = {
        "score": final_score,
        "max_score": 3,
        "level": ["Failing", "Needs Improvement", "Satisfactory", "Excellent"][final_score],
        "feedback": feedback
    }
    
    return final_score, result

def evaluate_task3(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate Task 3: Method Development Based on Theory."""
    score = 0
    feedback = []
    
    # Check theoretical analysis
    if "theoretical_analysis" in submission:
        analysis = submission["theoretical_analysis"].lower()
        if "cluster" in analysis and any(term in analysis for term in ["spherical", "feature", "subspace"]):
            score += 0.5
            feedback.append("Correctly analyzed limitations of standard clustering methods")
        else:
            score += 0.25
            feedback.append("Analysis of standard method limitations is incomplete")
    else:
        feedback.append("Missing theoretical analysis")
    
    # Check proposed method
    if "proposed_method" in submission:
        method = submission["proposed_method"].lower()
        if "cluster" in method and any(term in method for term in ["feature", "weight", "subspace", "adaptive"]):
            score += 0.5
            feedback.append("Proposed appropriate clustering method addressing feature relevance")
        else:
            score += 0.25
            feedback.append("Proposed method does not clearly address the identified limitations")
    else:
        feedback.append("Missing proposed method")
    
    # Check mathematical foundation
    if "mathematical_foundation" in submission:
        foundation = submission["mathematical_foundation"].lower()
        if "distance" in foundation and any(term in foundation for term in ["weight", "metric", "feature"]):
            score += 0.5
            feedback.append("Provided sound mathematical foundation for the proposed method")
        else:
            score += 0.25
            feedback.append("Mathematical foundation lacks key theoretical concepts")
    else:
        feedback.append("Missing mathematical foundation")
    
    # Check implementation results
    if "implementation_results" in submission and isinstance(submission["implementation_results"], dict):
        results = submission["implementation_results"]
        if "accuracy" in results:
            try:
                accuracy = float(results["accuracy"])
                if accuracy > 0.8:
                    score += 0.5
                    feedback.append("Demonstrated high accuracy in implementation results")
                else:
                    score += 0.25
                    feedback.append("Implementation results show moderate accuracy")
            except (ValueError, TypeError):
                feedback.append("Invalid accuracy value")
        else:
            feedback.append("Missing accuracy metric in implementation results")
    else:
        feedback.append("Missing or invalid implementation results")
    
    # Check comparison to standard
    if "comparison_to_standard" in submission:
        comparison = submission["comparison_to_standard"].lower()
        if any(method in comparison for method in ["k-means", "hierarchical", "dbscan"]):
            score += 0.5
            feedback.append("Provided meaningful comparison to standard clustering methods")
        else:
            score += 0.25
            feedback.append("Comparison to standard methods lacks specificity")
    else:
        feedback.append("Missing comparison to standard methods")
    
    # Check code snippet
    if "code_snippet" in submission and len(submission["code_snippet"]) > 0:
        code = submission["code_snippet"].lower()
        if "cluster" in code and any(term in code for term in ["weight", "feature", "distance"]):
            score += 0.5
            feedback.append("Provided relevant code implementation for the proposed method")
        else:
            score += 0.25
            feedback.append("Code snippet lacks key implementation details")
    else:
        feedback.append("Missing code snippet")
    
    # Determine final score level (0-3)
    final_score = 0
    if score >= 2.5:
        final_score = 3  # Excellent
    elif score >= 1.5:
        final_score = 2  # Satisfactory
    elif score >= 0.5:
        final_score = 1  # Needs Improvement
    
    result = {
        "score": final_score,
        "max_score": 3,
        "level": ["Failing", "Needs Improvement", "Satisfactory", "Excellent"][final_score],
        "feedback": feedback
    }
    
    return final_score, result

def evaluate_task4(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """Evaluate Task 4: Critical Analysis Using Theoretical Principles."""
    score = 0
    feedback = []
    
    # Check study design analysis
    if "study_design_analysis" in submission:
        analysis = submission["study_design_analysis"].lower()
        if "confound" in analysis and "age" in analysis:
            score += 0.5
            feedback.append("Correctly identified age as a key confounder")
        elif "confound" in analysis:
            score += 0.25
            feedback.append("Identified confounding but didn't specifically highlight age")
        else:
            feedback.append("Failed to identify confounding as a key issue")
    else:
        feedback.append("Missing study design analysis")
    
    # Check theoretical issues
    if "theoretical_issues" in submission and isinstance(submission["theoretical_issues"], list):
        issues = submission["theoretical_issues"]
        if len(issues) >= 3:
            has_confounding = any("confound" in issue.lower() and "age" in issue.lower() for issue in issues)
            has_selection_bias = any("selection" in issue.lower() and "bias" in issue.lower() for issue in issues)
            
            if has_confounding and has_selection_bias:
                score += 0.5
                feedback.append("Identified key theoretical issues including confounding by age and selection bias")
            elif has_confounding or has_selection_bias:
                score += 0.25
                feedback.append("Partially identified theoretical issues")
            else:
                feedback.append("Issues identified were not the most relevant")
        else:
            feedback.append("Insufficient number of theoretical issues identified")
    else:
        feedback.append("Missing or invalid theoretical issues")
    
    # Check alternative analysis
    if "alternative_analysis" in submission and isinstance(submission["alternative_analysis"], dict):
        alternative = submission["alternative_analysis"]
        
        # Check method
        if "method" in alternative:
            method = alternative["method"].lower()
            if any(term in method for term in ["propensity", "matching", "adjustment", "stratif"]):
                score += 0.5
                feedback.append("Proposed appropriate causal inference method")
            else:
                score += 0.25
                feedback.append("Proposed method is not optimal for addressing confounding")
        else:
            feedback.append("Missing alternative method")
        
        # Check theoretical justification
        if "theoretical_justification" in alternative:
            justification = alternative["theoretical_justification"].lower()
            if any(term in justification for term in ["causal", "confound", "bias"]):
                score += 0.5
                feedback.append("Provided sound theoretical justification for the alternative method")
            else:
                score += 0.25
                feedback.append("Theoretical justification lacks key causal inference concepts")
        else:
            feedback.append("Missing theoretical justification")
        
        # Check results
        if "results" in alternative:
            results = alternative["results"].lower()
            if "effect" in results and any(char.isdigit() for char in results):
                score += 0.25
                feedback.append("Reported quantitative results from alternative analysis")
            else:
                feedback.append("Results lack quantitative findings")
        else:
            feedback.append("Missing results from alternative analysis")
    else:
        feedback.append("Missing or invalid alternative analysis")
    
    # Check validity conclusion
    if "validity_conclusion" in submission:
        conclusion = submission["validity_conclusion"].lower()
        if "overestimate" in conclusion or "bias" in conclusion or "confound" in conclusion:
            score += 0.5
            feedback.append("Drew appropriate conclusions about the validity of the claimed effect")
        else:
            score += 0.25
            feedback.append("Conclusion does not clearly address the validity of the claimed effect")
    else:
        feedback.append("Missing validity conclusion")
    
    # Check code snippet
    if "code_snippet" in submission and len(submission["code_snippet"]) > 0:
        code = submission["code_snippet"].lower()
        if any(term in code for term in ["propensity", "match", "regress", "adjust"]):
            score += 0.25
            feedback.append("Provided relevant code implementation for causal inference")
        else:
            feedback.append("Code snippet lacks key implementation details")
    else:
        feedback.append("Missing code snippet")
    
    # Determine final score level (0-3)
    final_score = 0
    if score >= 2.5:
        final_score = 3  # Excellent
    elif score >= 1.5:
        final_score = 2  # Satisfactory
    elif score >= 0.5:
        final_score = 1  # Needs Improvement
    
    result = {
        "score": final_score,
        "max_score": 3,
        "level": ["Failing", "Needs Improvement", "Satisfactory", "Excellent"][final_score],
        "feedback": feedback
    }
    
    return final_score, result

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {"task_results": {}}
    
    # Evaluate each task
    task1_score, task1_result = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    task2_score, task2_result = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    task3_score, task3_result = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    task4_score, task4_result = evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    
    # Store individual task results
    results["task_results"]["task1"] = task1_result
    results["task_results"]["task2"] = task2_result
    results["task_results"]["task3"] = task3_result
    results["task_results"]["task4"] = task4_result
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score + task4_score
    max_possible_score = 12
    percentage_score = (total_score / max_possible_score) * 100
    
    # Check passing criteria
    excellent_count = sum(1 for score in [task1_score, task2_score, task3_score, task4_score] if score == 3)
    all_satisfactory = all(score >= 2 for score in [task1_score, task2_score, task3_score, task4_score])
    passed = all_satisfactory and excellent_count >= 2 and total_score >= 9
    
    # Add overall results
    results["overall_score"] = round(percentage_score, 2)
    results["total_points"] = total_score
    results["max_possible_points"] = max_possible_score
    results["passed"] = passed
    results["excellent_count"] = excellent_count
    results["all_satisfactory"] = all_satisfactory
    
    # Add summary
    if passed:
        results["summary"] = f"PASSED: Scored {total_score}/{max_possible_score} points ({percentage_score:.2f}%). " \
                            f"Achieved 'Excellent' in {excellent_count} tasks and at least 'Satisfactory' in all tasks."
    else:
        if not all_satisfactory:
            results["summary"] = f"FAILED: Scored {total_score}/{max_possible_score} points ({percentage_score:.2f}%). " \
                                f"Did not achieve at least 'Satisfactory' in all tasks."
        elif excellent_count < 2:
            results["summary"] = f"FAILED: Scored {total_score}/{max_possible_score} points ({percentage_score:.2f}%). " \
                                f"Did not achieve 'Excellent' in at least 2 tasks."
        else:
            results["summary"] = f"FAILED: Scored {total_score}/{max_possible_score} points ({percentage_score:.2f}%). " \
                                f"Did not meet the minimum passing threshold of 9 points."
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
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
    
    # Save results
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(results["summary"])

if __name__ == "__main__":
    main()