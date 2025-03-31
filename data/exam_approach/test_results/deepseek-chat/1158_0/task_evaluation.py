import json
import re

def validate_task_1(submission, answer_key):
    errors = []
    score = 0
    max_score = 4  # 2 commodities * 2 points each (name/price + trend/factor)
    
    for commodity in ['commodity_1', 'commodity_2']:
        entry = submission['task_1'][commodity]
        
        # Validate name
        if not 3 <= len(entry['name']) <= 50:
            errors.append(f"{commodity} name length invalid (3-50 chars required)")
        else:
            score += 0.5
        
        # Validate price format
        if not re.match(r'^\$?\d{1,3}(,\d{3})*(\.\d{1,2})?/\w+$', entry['current_price']):
            errors.append(f"{commodity} price format invalid (should be like '$850/ton' or '3.85/pound')")
        else:
            score += 0.5
        
        # Validate trend
        if entry['trend'] not in ['rising', 'falling', 'stable']:
            errors.append(f"{commodity} trend value invalid (must be 'rising', 'falling', or 'stable')")
        else:
            score += 0.5
        
        # Validate influencing factor
        if not 10 <= len(entry['influencing_factor']) <= 150:
            errors.append(f"{commodity} factor length invalid (10-150 chars required)")
        else:
            score += 0.5
    
    return score, max_score, errors

def validate_task_2(submission, answer_key):
    errors = []
    score = 0
    max_score = 5  # 4 exact values + 1 trend analysis
    
    exact_values = answer_key['task_2']['exact_values']
    trend_rules = answer_key['task_2']['trend_analysis']
    
    # Check exact values
    for field, expected in exact_values.items():
        # Allow some formatting variations
        submitted = submission['task_2'][field]
        if field == 'price_change_percentage':
            if submitted not in [expected, expected.replace('+', '')]:
                errors.append(f"Task 2 {field} should be {expected} (got {submitted})")
            else:
                score += 1
        else:
            if submitted.replace(',', '') != expected.replace(',', ''):
                errors.append(f"Task 2 {field} should be {expected} (got {submitted})")
            else:
                score += 1
    
    # Check trend analysis
    analysis = submission['task_2']['trend_analysis'].lower()
    has_positive = any(kw in analysis for kw in trend_rules['required_keywords'])
    has_negative = any(kw in analysis for kw in trend_rules['prohibited_keywords'])
    
    if not has_positive or has_negative:
        errors.append("Trend analysis should suggest a buying opportunity (got: '{}')".format(
            submission['task_2']['trend_analysis']))
    else:
        score += 1
    
    return score, max_score, errors

def main():
    # Load files
    with open('test_submission.json', 'r') as f:
        submission = json.load(f)
    
    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)['answer_key']
    
    # Evaluate tasks
    task1_score, task1_max, task1_errors = validate_task_1(submission, answer_key)
    task2_score, task2_max, task2_errors = validate_task_2(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score
    total_max = task1_max + task2_max
    overall_score = round((total_score / total_max) * 100)
    
    # Prepare results
    results = {
        'overall_score': overall_score,
        'task_1': {
            'score': task1_score,
            'max_score': task1_max,
            'errors': task1_errors,
            'passed': task1_score >= task1_max * 0.8  # 80% threshold
        },
        'task_2': {
            'score': task2_score,
            'max_score': task2_max,
            'errors': task2_errors,
            'passed': task2_score >= task2_max * 0.8  # 80% threshold
        },
        'passed': overall_score >= 80
    }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {overall_score}%")

if __name__ == '__main__':
    main()