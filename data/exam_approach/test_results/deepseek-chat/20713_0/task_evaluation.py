import json
import os

def load_json_file(filename):
    """Load a JSON file from the current directory."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found in the current directory")
    with open(filename, 'r') as file:
        return json.load(file)

def validate_task_1(submission, answer_key):
    """Validate Task 1 calculations and justification."""
    task_sub = submission.get('task_1', {})
    task_key = answer_key.get('task_1', {})
    
    # Check calculations with tolerance for floating point rounding
    calc_checks = [
        round(task_sub.get('mark_up_rate_percentage', 0), 2) == round(task_key['mark_up_rate_percentage'], 2),
        round(task_sub.get('selling_price', 0), 2) == round(task_key['selling_price'], 2)
    ]
    
    # Check justification is present (content is evaluated manually)
    justification_check = bool(task_sub.get('pricing_justification', '').strip())
    
    return {
        'mark_up_rate_correct': calc_checks[0],
        'selling_price_correct': calc_checks[1],
        'justification_provided': justification_check,
        'task_score': sum(calc_checks) + int(justification_check),
        'max_score': 3  # 2 calcs + 1 justification
    }

def validate_task_2(submission, answer_key):
    """Validate Task 2 calculations and justification."""
    task_sub = submission.get('task_2', {})
    task_key = answer_key.get('task_2', {})
    
    # Check calculations with tolerance for floating point rounding
    calc_check = round(task_sub.get('mark_down_rate_percentage', 0), 2) == round(task_key['mark_down_rate_percentage'], 2)
    
    # Check reason is present (content is evaluated manually)
    reason_check = bool(task_sub.get('reason_for_mark_down', '').strip())
    
    return {
        'mark_down_rate_correct': calc_check,
        'reason_provided': reason_check,
        'task_score': int(calc_check) + int(reason_check),
        'max_score': 2  # 1 calc + 1 reason
    }

def evaluate_submission():
    """Main evaluation function."""
    try:
        # Load files
        submission = load_json_file('test_submission.json')
        answer_key = load_json_file('answer_key.json')
        
        # Validate tasks
        task1_results = validate_task_1(submission, answer_key)
        task2_results = validate_task_2(submission, answer_key)
        
        # Calculate overall score
        total_score = task1_results['task_score'] + task2_results['task_score']
        max_score = task1_results['max_score'] + task2_results['max_score']
        overall_score = round((total_score / max_score) * 100, 2)
        
        # Prepare results
        results = {
            'overall_score': overall_score,
            'task_1_results': task1_results,
            'task_2_results': task2_results,
            'total_score': total_score,
            'max_score': max_score,
            'submission_details': {
                'candidate_id': submission.get('candidate_id', 'unknown'),
                'submission_time': None  # Could be added if timestamp is needed
            }
        }
        
        # Save results
        with open('test_results.json', 'w') as outfile:
            json.dump(results, outfile, indent=2)
        
        print("Evaluation completed successfully. Results saved to test_results.json")
        return True
        
    except Exception as e:
        print(f"Evaluation failed: {str(e)}")
        return False

if __name__ == "__main__":
    evaluate_submission()