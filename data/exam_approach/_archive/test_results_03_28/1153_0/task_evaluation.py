import json
import math
from pathlib import Path

def load_json(filename):
    """Load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def save_json(data, filename):
    """Save data as JSON to a file."""
    with open(filename, 'w') as file:
        json.dump(data, indent=2, sort_keys=False, file=file)

def evaluate_numeric_value(candidate_value, answer_key_value, tolerance=0.02):
    """Evaluate a numeric value with tolerance for rounding differences."""
    if candidate_value is None or answer_key_value is None:
        return False
    
    try:
        candidate_num = float(candidate_value)
        answer_key_num = float(answer_key_value)
        
        # Handle zero or very small numbers
        if abs(answer_key_num) < 0.0001:
            return abs(candidate_num) < 0.0001
        
        # Calculate relative difference
        relative_diff = abs(candidate_num - answer_key_num) / abs(answer_key_num)
        return relative_diff <= tolerance
    except (ValueError, TypeError):
        return False

def evaluate_list(candidate_list, answer_key_list):
    """Evaluate if two lists contain the same elements (order-independent)."""
    if not isinstance(candidate_list, list) or not isinstance(answer_key_list, list):
        return False
    
    # Convert lists to sets for order-independent comparison
    return set(candidate_list) == set(answer_key_list)

def evaluate_dict(candidate_dict, answer_key_dict, tolerance=0.02):
    """Evaluate if two dictionaries have the same keys and similar numeric values."""
    if not isinstance(candidate_dict, dict) or not isinstance(answer_key_dict, dict):
        return False
    
    if set(candidate_dict.keys()) != set(answer_key_dict.keys()):
        return False
    
    for key in answer_key_dict:
        if isinstance(answer_key_dict[key], (int, float)):
            if not evaluate_numeric_value(candidate_dict[key], answer_key_dict[key], tolerance):
                return False
        elif candidate_dict[key] != answer_key_dict[key]:
            return False
    
    return True

def evaluate_section1_q1(candidate, answer_key):
    """Evaluate Section 1, Question 1."""
    score = 0
    feedback = []
    
    # Check average consumption calculations
    if evaluate_dict(candidate.get('average_consumption', {}), answer_key.get('average_consumption', {})):
        score += 5
        feedback.append("Correct average consumption calculations.")
    else:
        feedback.append("Incorrect average consumption calculations.")
    
    # Check strongest upward trend identification
    if candidate.get('strongest_upward_trend') == answer_key.get('strongest_upward_trend'):
        score += 3
        feedback.append("Correctly identified item with strongest upward trend.")
    else:
        feedback.append("Failed to identify correct item with strongest upward trend.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section1_q2(candidate, answer_key):
    """Evaluate Section 1, Question 2."""
    score = 0
    feedback = []
    
    # Check percentage change calculations
    if evaluate_dict(candidate.get('percentage_changes', {}), answer_key.get('percentage_changes', {})):
        score += 5
        feedback.append("Correct percentage change calculations.")
    else:
        feedback.append("Incorrect percentage change calculations.")
    
    # Check priority department
    if candidate.get('priority_department') == answer_key.get('priority_department'):
        score += 3
        feedback.append("Correctly identified priority department.")
    else:
        feedback.append("Failed to identify correct priority department.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section1_q3(candidate, answer_key):
    """Evaluate Section 1, Question 3."""
    score = 0
    feedback = []
    
    # Check predicted replacement
    if candidate.get('predicted_replacement') == answer_key.get('predicted_replacement'):
        score += 4
        feedback.append("Correctly identified item needing replacement first.")
    else:
        feedback.append("Failed to identify correct item needing replacement first.")
    
    # Check calculation method
    if candidate.get('calculation') and "safety_glasses" in candidate.get('calculation', "").lower() and "1.8" in candidate.get('calculation', ""):
        score += 3
        feedback.append("Demonstrated correct calculation method.")
    else:
        feedback.append("Incorrect or insufficient calculation method shown.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 3
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section2_q4(candidate, answer_key):
    """Evaluate Section 2, Question 4."""
    score = 0
    feedback = []
    
    # Check items needing reorder
    if evaluate_list(candidate.get('items_needing_reorder', []), answer_key.get('items_needing_reorder', [])):
        score += 4
        feedback.append("Correctly identified items needing reorder.")
    elif "clipboards" in candidate.get('items_needing_reorder', []):
        score += 2
        feedback.append("Correctly identified clipboards need reordering, but list is incomplete or has extra items.")
    else:
        feedback.append("Failed to identify correct items needing reorder.")
    
    # Check optimal quantities
    if evaluate_dict(candidate.get('optimal_quantities', {}), answer_key.get('optimal_quantities', {})):
        score += 4
        feedback.append("Calculated correct optimal order quantities.")
    else:
        feedback.append("Incorrect optimal order quantities.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section2_q5(candidate, answer_key):
    """Evaluate Section 2, Question 5."""
    score = 0
    feedback = []
    
    # Check turnover rate calculations
    if evaluate_dict(candidate.get('turnover_rates', {}), answer_key.get('turnover_rates', {})):
        score += 5
        feedback.append("Correctly calculated inventory turnover rates.")
    else:
        feedback.append("Incorrect inventory turnover rate calculations.")
    
    # Check healthiest category identification
    if candidate.get('healthiest_category') == answer_key.get('healthiest_category'):
        score += 3
        feedback.append("Correctly identified healthiest inventory category.")
    else:
        feedback.append("Failed to identify correct healthiest inventory category.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section2_q6(candidate, answer_key):
    """Evaluate Section 2, Question 6."""
    score = 0
    feedback = []
    
    # Check service level calculations
    if evaluate_dict(candidate.get('service_levels', {}), answer_key.get('service_levels', {})):
        score += 5
        feedback.append("Correctly calculated service levels.")
    else:
        feedback.append("Incorrect service level calculations.")
    
    # Check urgent improvement item
    if candidate.get('urgent_improvement_needed') == answer_key.get('urgent_improvement_needed'):
        score += 3
        feedback.append("Correctly identified item needing urgent improvement.")
    else:
        feedback.append("Failed to identify correct item needing urgent improvement.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section3_q7(candidate, answer_key):
    """Evaluate Section 3, Question 7."""
    score = 0
    feedback = []
    
    # Check potential monthly savings
    if evaluate_numeric_value(candidate.get('potential_monthly_savings'), answer_key.get('potential_monthly_savings')):
        score += 4
        feedback.append("Correctly calculated potential monthly savings.")
    else:
        feedback.append("Incorrect calculation of potential monthly savings.")
    
    # Check department priority order
    if evaluate_list(candidate.get('department_priority_order', []), answer_key.get('department_priority_order', [])):
        score += 4
        feedback.append("Correctly prioritized departments.")
    else:
        feedback.append("Incorrect department prioritization.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section3_q8(candidate, answer_key):
    """Evaluate Section 3, Question 8."""
    score = 0
    feedback = []
    
    # Check supplier scores
    # Allow for different scoring methods as long as relative ranking is preserved
    if evaluate_dict(candidate.get('supplier_scores', {}), answer_key.get('supplier_scores', {})):
        score += 5
        feedback.append("Correct supplier evaluation scores.")
    else:
        # Check if ranking is still correct even if absolute scores differ
        candidate_scores = candidate.get('supplier_scores', {})
        if (candidate_scores.get('supplier_c', 0) > candidate_scores.get('supplier_a', 0) and
            candidate_scores.get('supplier_a', 0) > candidate_scores.get('supplier_b', 0) and
            candidate_scores.get('supplier_b', 0) > candidate_scores.get('supplier_d', 0)):
            score += 3
            feedback.append("Supplier ranking is correct but scores differ from expected values.")
        else:
            feedback.append("Incorrect supplier evaluation scores.")
    
    # Check recommended supplier
    if candidate.get('recommended_supplier') == answer_key.get('recommended_supplier'):
        score += 3
        feedback.append("Correctly identified recommended supplier.")
    else:
        feedback.append("Failed to identify correct recommended supplier.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section3_q9(candidate, answer_key):
    """Evaluate Section 3, Question 9."""
    score = 0
    feedback = []
    
    # Check projected annual consumption
    if evaluate_numeric_value(candidate.get('projected_annual_consumption'), answer_key.get('projected_annual_consumption')):
        score += 3
        feedback.append("Correctly calculated projected annual consumption.")
    else:
        feedback.append("Incorrect calculation of projected annual consumption.")
    
    # Check budgeted expenditure
    if evaluate_numeric_value(candidate.get('budgeted_expenditure'), answer_key.get('budgeted_expenditure')):
        score += 3
        feedback.append("Correctly calculated budgeted expenditure.")
    else:
        feedback.append("Incorrect calculation of budgeted expenditure.")
    
    # Check optimal purchasing frequency - accept a range of valid answers
    candidate_freq = candidate.get('optimal_purchasing_frequency')
    answer_freq = answer_key.get('optimal_purchasing_frequency')
    
    if candidate_freq is not None and answer_freq is not None:
        if isinstance(candidate_freq, (int, float)) and 4 <= float(candidate_freq) <= 12:
            score += 2
            feedback.append("Provided reasonable optimal purchasing frequency.")
        else:
            feedback.append("Optimal purchasing frequency outside reasonable range.")
    else:
        feedback.append("Missing optimal purchasing frequency calculation.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_section3_q10(candidate, answer_key):
    """Evaluate Section 3, Question 10."""
    score = 0
    feedback = []
    
    # Check current monthly processing cost
    if evaluate_numeric_value(candidate.get('current_monthly_processing_cost'), answer_key.get('current_monthly_processing_cost')):
        score += 3
        feedback.append("Correctly calculated current monthly processing cost.")
    else:
        feedback.append("Incorrect calculation of current monthly processing cost.")
    
    # Check potential savings
    if evaluate_numeric_value(candidate.get('potential_savings'), answer_key.get('potential_savings')):
        score += 3
        feedback.append("Correctly calculated potential savings.")
    else:
        feedback.append("Incorrect calculation of potential savings.")
    
    # Check optimal approval threshold
    if evaluate_numeric_value(candidate.get('optimal_approval_threshold'), answer_key.get('optimal_approval_threshold')):
        score += 2
        feedback.append("Correctly determined optimal approval threshold.")
    else:
        feedback.append("Incorrect determination of optimal approval threshold.")
    
    # Check justification
    if candidate.get('justification') and len(candidate.get('justification', "")) > 10:
        score += 2
        feedback.append("Provided adequate justification.")
    else:
        feedback.append("Insufficient justification provided.")
    
    return score, feedback

def evaluate_test(candidate_submission, answer_key):
    """Evaluate the entire test submission against the answer key."""
    results = {
        "candidate_id": candidate_submission.get("candidate_id", "Unknown"),
        "sections": {
            "section1": {
                "questions": {},
                "score": 0,
                "max_score": 30,
                "percentage": 0
            },
            "section2": {
                "questions": {},
                "score": 0,
                "max_score": 30,
                "percentage": 0
            },
            "section3": {
                "questions": {},
                "score": 0,
                "max_score": 40,
                "percentage": 0
            }
        },
        "overall_score": 0,
        "max_overall_score": 100,
        "overall_percentage": 0,
        "pass_status": False,
        "section_pass_status": {
            "section1": False,
            "section2": False,
            "section3": False
        }
    }
    
    # Define evaluation functions for each question
    evaluators = {
        "section1": {
            "q1": evaluate_section1_q1,
            "q2": evaluate_section1_q2,
            "q3": evaluate_section1_q3
        },
        "section2": {
            "q4": evaluate_section2_q4,
            "q5": evaluate_section2_q5,
            "q6": evaluate_section2_q6
        },
        "section3": {
            "q7": evaluate_section3_q7,
            "q8": evaluate_section3_q8,
            "q9": evaluate_section3_q9,
            "q10": evaluate_section3_q10
        }
    }
    
    # Evaluate each section and question
    for section_name, questions in evaluators.items():
        section_score = 0
        
        for question_name, evaluator_func in questions.items():
            candidate_answer = candidate_submission.get(section_name, {}).get(question_name, {})
            key_answer = answer_key.get(section_name, {}).get(question_name, {})
            
            question_score, question_feedback = evaluator_func(candidate_answer, key_answer)
            section_score += question_score
            
            results["sections"][section_name]["questions"][question_name] = {
                "score": question_score,
                "max_score": 10,
                "percentage": (question_score / 10) * 100,
                "feedback": question_feedback
            }
        
        # Calculate section scores and percentages
        results["sections"][section_name]["score"] = section_score
        results["sections"][section_name]["percentage"] = (section_score / results["sections"][section_name]["max_score"]) * 100
        
        # Determine if section passes (60% or higher)
        results["section_pass_status"][section_name] = results["sections"][section_name]["percentage"] >= 60
    
    # Calculate overall score and percentage
    total_score = sum(section["score"] for section in results["sections"].values())
    results["overall_score"] = total_score
    results["overall_percentage"] = (total_score / results["max_overall_score"]) * 100
    
    # Determine overall pass status (70% overall and 60% in each section)
    results["pass_status"] = (results["overall_percentage"] >= 70 and 
                             all(results["section_pass_status"].values()))
    
    return results

def main():
    try:
        # Load the candidate submission and answer key
        candidate_submission = load_json("test_submission.json")
        answer_key = load_json("answer_key.json")
        
        # Evaluate the test
        results = evaluate_test(candidate_submission, answer_key)
        
        # Save results to a file
        save_json(results, "test_results.json")
        
        print(f"Evaluation complete. Results saved to test_results.json")
        print(f"Overall score: {results['overall_percentage']:.2f}%")
        print(f"Pass status: {'PASSED' if results['pass_status'] else 'FAILED'}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        raise

if __name__ == "__main__":
    main()