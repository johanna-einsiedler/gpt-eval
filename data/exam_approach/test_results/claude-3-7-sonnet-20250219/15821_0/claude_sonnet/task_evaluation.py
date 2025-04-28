#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Annual O&M Budget Development (40 points)"""
    points = 0
    details = {}
    
    # Total Annual Budget (10 points)
    sub_budget = submission.get('total_annual_budget', 0)
    key_budget = answer_key.get('total_annual_budget', 0)
    
    budget_percent_diff = abs((sub_budget - key_budget) / key_budget) * 100
    if budget_percent_diff <= 5:
        points += 10
        details['total_annual_budget'] = {'points': 10, 'max': 10, 'note': 'Within 5% of model answer'}
    elif budget_percent_diff <= 10:
        points += 5
        details['total_annual_budget'] = {'points': 5, 'max': 10, 'note': 'Within 10% of model answer'}
    else:
        details['total_annual_budget'] = {'points': 0, 'max': 10, 'note': 'Outside acceptable range'}
    
    # Cost per MW (5 points)
    sub_cost_per_mw = submission.get('cost_per_MW', 0)
    key_cost_per_mw = answer_key.get('cost_per_MW', 0)
    
    cost_percent_diff = abs((sub_cost_per_mw - key_cost_per_mw) / key_cost_per_mw) * 100
    if cost_percent_diff <= 5:
        points += 5
        details['cost_per_MW'] = {'points': 5, 'max': 5, 'note': 'Within 5% of model answer'}
    elif 38000 <= sub_cost_per_mw <= 45000:  # Industry benchmark range
        points += 3
        details['cost_per_MW'] = {'points': 3, 'max': 5, 'note': 'Within industry benchmark range'}
    else:
        details['cost_per_MW'] = {'points': 0, 'max': 5, 'note': 'Outside acceptable range'}
    
    # Largest Expense Category (5 points)
    sub_category = submission.get('largest_expense_category', '')
    key_category = answer_key.get('largest_expense_category', '')
    
    if sub_category.lower() == key_category.lower():
        points += 5
        details['largest_expense_category'] = {'points': 5, 'max': 5, 'note': 'Correctly identified'}
    else:
        details['largest_expense_category'] = {'points': 0, 'max': 5, 'note': 'Incorrectly identified'}
    
    # Largest Expense Amount (10 points)
    sub_amount = submission.get('largest_expense_amount', 0)
    key_amount = answer_key.get('largest_expense_amount', 0)
    
    amount_percent_diff = abs((sub_amount - key_amount) / key_amount) * 100
    if amount_percent_diff <= 5:
        points += 10
        details['largest_expense_amount'] = {'points': 10, 'max': 10, 'note': 'Within 5% of model answer'}
    elif amount_percent_diff <= 10:
        points += 5
        details['largest_expense_amount'] = {'points': 5, 'max': 10, 'note': 'Within 10% of model answer'}
    else:
        details['largest_expense_amount'] = {'points': 0, 'max': 10, 'note': 'Outside acceptable range'}
    
    # Quarterly Distribution (10 points)
    sub_dist = submission.get('quarterly_distribution', {})
    key_dist = answer_key.get('quarterly_distribution', {})
    
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    quarter_points = 0
    quarter_details = {}
    
    # Check if quarters sum to 100%
    sub_total = sum(sub_dist.get(q, 0) for q in quarters)
    if abs(sub_total - 100.0) > 0.1:  # Allow 0.1% tolerance
        quarter_details['total'] = {'points': 0, 'max': 10, 'note': f'Quarters do not sum to 100% (sum: {sub_total})'}
    else:
        for q in quarters:
            sub_q = sub_dist.get(q, 0)
            key_q = key_dist.get(q, 0)
            
            if abs(sub_q - key_q) <= 5:
                quarter_points += 2.5
                quarter_details[q] = {'points': 2.5, 'max': 2.5, 'note': 'Within 5 percentage points'}
            else:
                quarter_details[q] = {'points': 0, 'max': 2.5, 'note': 'Outside acceptable range'}
    
    points += quarter_points
    details['quarterly_distribution'] = quarter_details
    
    return {'points': points, 'max_points': 40, 'details': details}

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Budget Variance Analysis (30 points)"""
    points = 0
    details = {}
    
    # Variance Contributors (15 points)
    sub_contributors = submission.get('variance_contributors', [])
    key_contributors = answer_key.get('variance_contributors', [])
    
    # Create a set of key categories for easy lookup
    key_categories = {item['category'].lower() for item in key_contributors}
    
    contributor_points = 0
    contributor_details = {}
    
    for i, contributor in enumerate(sub_contributors[:3]):  # Evaluate up to 3 contributors
        category = contributor.get('category', '')
        root_cause = contributor.get('root_cause', '')
        
        item_points = 0
        item_notes = []
        
        # Check category (3 points)
        if category.lower() in key_categories:
            item_points += 3
            item_notes.append('Correctly identified category')
        else:
            item_notes.append('Incorrectly identified category')
        
        # Check root cause (2 points)
        if root_cause and len(root_cause.split()) >= 10:  # Simple check for a substantive explanation
            item_points += 2
            item_notes.append('Provided plausible root cause')
        else:
            item_notes.append('Insufficient root cause explanation')
        
        contributor_points += item_points
        contributor_details[f'contributor_{i+1}'] = {
            'points': item_points, 
            'max': 5, 
            'note': '; '.join(item_notes)
        }
    
    points += contributor_points
    details['variance_contributors'] = contributor_details
    
    # Revised Budget Total (5 points)
    sub_revised = submission.get('revised_budget_total', 0)
    key_revised = answer_key.get('revised_budget_total', 0)
    
    revised_percent_diff = abs((sub_revised - key_revised) / key_revised) * 100
    if revised_percent_diff <= 5:
        points += 5
        details['revised_budget_total'] = {'points': 5, 'max': 5, 'note': 'Within 5% of model answer'}
    elif revised_percent_diff <= 10:
        points += 3
        details['revised_budget_total'] = {'points': 3, 'max': 5, 'note': 'Within 10% of model answer'}
    else:
        details['revised_budget_total'] = {'points': 0, 'max': 5, 'note': 'Outside acceptable range'}
    
    # Contingency Amount and Percentage (10 points)
    sub_contingency_pct = submission.get('contingency_percentage', 0)
    sub_contingency_amt = submission.get('contingency_amount', 0)
    sub_budget = submission.get('revised_budget_total', 0)
    
    # Verify that contingency amount and percentage are consistent
    calculated_pct = (sub_contingency_amt / sub_budget * 100) if sub_budget else 0
    pct_consistent = abs(calculated_pct - sub_contingency_pct) <= 0.5  # Allow 0.5% tolerance
    
    if 8 <= sub_contingency_pct <= 12 and pct_consistent:
        points += 10
        details['contingency'] = {'points': 10, 'max': 10, 'note': 'Within recommended range (8-12%)'}
    elif 5 <= sub_contingency_pct <= 15 and pct_consistent:
        points += 5
        details['contingency'] = {'points': 5, 'max': 10, 'note': 'Within acceptable range (5-15%)'}
    else:
        details['contingency'] = {'points': 0, 'max': 10, 'note': 'Outside acceptable range or inconsistent values'}
    
    return {'points': points, 'max_points': 30, 'details': details}

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Budget Justification (30 points)"""
    points = 0
    details = {}
    
    # Key Budget Priorities (9 points)
    sub_priorities = submission.get('key_budget_priorities', [])
    
    priority_points = 0
    priority_details = {}
    
    # Check for critical maintenance needs in priorities
    critical_keywords = [
        'preventive', 'maintenance', 'repair', 'turbine', 'wt-05', 'wt-12', 
        'gearbox', 'blade', 'generator', 'bearing', 'inspection', 'upgrade',
        'spare parts', 'inventory', '5-year', 'control system'
    ]
    
    for i, priority in enumerate(sub_priorities[:3]):  # Evaluate up to 3 priorities
        if any(keyword.lower() in priority.lower() for keyword in critical_keywords):
            priority_points += 3
            priority_details[f'priority_{i+1}'] = {'points': 3, 'max': 3, 'note': 'Addresses critical maintenance needs'}
        else:
            priority_details[f'priority_{i+1}'] = {'points': 0, 'max': 3, 'note': 'Does not align with critical needs'}
    
    points += priority_points
    details['key_budget_priorities'] = priority_details
    
    # Cost-Saving Measures (6 points)
    sub_measures = submission.get('cost_saving_measures', [])
    
    measure_points = 0
    measure_details = {}
    
    # Check for realistic cost-saving measures
    realistic_keywords = [
        'monitor', 'preventive', 'schedule', 'cluster', 'in-house', 'training',
        'efficiency', 'optimize', 'reduce', 'inventory', 'predictive', 'condition',
        'contractor', 'subcontractor', 'vendor', 'negotiate', 'standardize'
    ]
    
    for i, measure in enumerate(sub_measures[:3]):  # Evaluate up to 3 measures
        if any(keyword.lower() in measure.lower() for keyword in realistic_keywords):
            measure_points += 2
            measure_details[f'measure_{i+1}'] = {'points': 2, 'max': 2, 'note': 'Realistic and aligned with benchmarks'}
        else:
            measure_details[f'measure_{i+1}'] = {'points': 0, 'max': 2, 'note': 'Unrealistic or counterproductive'}
    
    points += measure_points
    details['cost_saving_measures'] = measure_details
    
    # Major Maintenance ROI (6 points)
    sub_roi = submission.get('major_maintenance_ROI', {})
    
    roi_points = 0
    roi_details = {}
    
    # Check maintenance item
    maintenance_items = [
        'gearbox', 'generator', 'bearing', 'blade', 'control system', 
        'vibration', 'monitoring', 'oil analysis', 'inspection', 'upgrade'
    ]
    
    item = sub_roi.get('item', '')
    if any(m_item.lower() in item.lower() for m_item in maintenance_items):
        roi_points += 2
        roi_details['item'] = {'points': 2, 'max': 2, 'note': 'Valid maintenance item'}
    else:
        roi_details['item'] = {'points': 0, 'max': 2, 'note': 'Invalid or missing maintenance item'}
    
    # Check cost calculation
    cost = sub_roi.get('cost', 0)
    if 5000 <= cost <= 200000:  # Reasonable range for maintenance costs
        roi_points += 2
        roi_details['cost'] = {'points': 2, 'max': 2, 'note': 'Realistic cost calculation'}
    else:
        roi_details['cost'] = {'points': 0, 'max': 2, 'note': 'Unrealistic cost'}
    
    # Check return and payback
    expected_return = sub_roi.get('expected_return', 0)
    payback_period = sub_roi.get('payback_period', 0)
    
    if expected_return > cost and 0 < payback_period <= 36:  # Reasonable payback period (up to 3 years)
        roi_points += 2
        roi_details['return'] = {'points': 2, 'max': 2, 'note': 'Realistic return and payback period'}
    else:
        roi_details['return'] = {'points': 0, 'max': 2, 'note': 'Unrealistic return or payback period'}
    
    points += roi_points
    details['major_maintenance_ROI'] = roi_details
    
    # Five-Year Projection (9 points)
    sub_projection = submission.get('five_year_projection', {})
    
    # Check for appropriate annual increases
    years = ['year1', 'year2', 'year3', 'year4', 'year5']
    values = [sub_projection.get(year, 0) for year in years]
    
    if len(values) == 5 and all(values[i] > 0 for i in range(5)):
        # Calculate annual increase percentages
        increases = [(values[i] - values[i-1]) / values[i-1] * 100 for i in range(1, 5)]
        
        if all(3 <= inc <= 5 for inc in increases):
            points += 9
            details['five_year_projection'] = {'points': 9, 'max': 9, 'note': 'Appropriate annual increases (3-5%)'}
        elif all(inc > 0 for inc in increases):
            points += 5
            details['five_year_projection'] = {'points': 5, 'max': 9, 'note': 'Consistent increases but not at appropriate rates'}
        else:
            details['five_year_projection'] = {'points': 0, 'max': 9, 'note': 'Inconsistent increases'}
    else:
        details['five_year_projection'] = {'points': 0, 'max': 9, 'note': 'Missing or invalid projection values'}
    
    return {'points': points, 'max_points': 30, 'details': details}

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        'candidate_id': submission.get('candidate_id', 'Unknown'),
        'task1': evaluate_task1(submission.get('task1', {}), answer_key.get('task1', {})),
        'task2': evaluate_task2(submission.get('task2', {}), answer_key.get('task2', {})),
        'task3': evaluate_task3(submission.get('task3', {}), answer_key.get('task3', {}))
    }
    
    # Calculate total points and overall score
    total_points = sum(task['points'] for task in [results['task1'], results['task2'], results['task3']])
    max_points = sum(task['max_points'] for task in [results['task1'], results['task2'], results['task3']])
    overall_score = (total_points / max_points) * 100 if max_points > 0 else 0
    
    # Check minimum section requirements (60% in each task)
    task1_percent = (results['task1']['points'] / results['task1']['max_points']) * 100 if results['task1']['max_points'] > 0 else 0
    task2_percent = (results['task2']['points'] / results['task2']['max_points']) * 100 if results['task2']['max_points'] > 0 else 0
    task3_percent = (results['task3']['points'] / results['task3']['max_points']) * 100 if results['task3']['max_points'] > 0 else 0
    
    passed_minimum = all([
        task1_percent >= 60,
        task2_percent >= 60,
        task3_percent >= 60
    ])
    
    # Determine if candidate passed overall
    passed_overall = overall_score >= 70 and passed_minimum
    
    results.update({
        'total_points': total_points,
        'max_points': max_points,
        'overall_score': round(overall_score, 2),
        'passed_minimum_requirements': passed_minimum,
        'passed': passed_overall,
        'task1_percent': round(task1_percent, 2),
        'task2_percent': round(task2_percent, 2),
        'task3_percent': round(task3_percent, 2)
    })
    
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
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()