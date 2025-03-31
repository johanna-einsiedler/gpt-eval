import json
import os
import re

def count_words(text):
    """Count the number of words in a text string."""
    if not text:
        return 0
    return len(re.findall(r'\b\w+\b', text))

def validate_policy_statement(statement, answer_key_statement):
    """Validate the policy statement and assign points."""
    score = 0
    max_score = 6
    
    # Check if statement exists and has appropriate length
    if statement and 50 <= count_words(statement) <= 100:
        # Check for purpose elements (value, compliance, ethics)
        purpose_keywords = ['value', 'compliance', 'ethical', 'ethics', 'standards', 'maximize']
        if any(keyword in statement.lower() for keyword in purpose_keywords):
            score += 2
            
        # Check for scope elements (who and what it applies to)
        scope_keywords = ['all employees', 'all departments', 'all purchases', 'applies to', 'scope']
        if any(keyword in statement.lower() for keyword in scope_keywords):
            score += 2
            
        # Check if clear and concise
        if count_words(statement) <= 100 and statement.strip():
            score += 2
    
    return score, max_score

def validate_approval_thresholds(thresholds, answer_key_thresholds):
    """Validate the approval thresholds and assign points."""
    score = 0
    max_score = 12
    
    if not thresholds or len(thresholds) != 3:
        return score, max_score
    
    # Create a mapping for easier comparison
    threshold_map = {t.get('threshold', ''): t for t in thresholds}
    answer_key_map = {t.get('threshold', ''): t for t in answer_key_thresholds}
    
    # Check each threshold
    for threshold_key in ['under $5,000', '$5,000-$25,000', 'over $25,000']:
        if threshold_key in threshold_map and threshold_key in answer_key_map:
            # Threshold matches (+1 point)
            score += 1
            
            # Check approvers (+1 point)
            candidate_approvers = set(threshold_map[threshold_key].get('approvers', []))
            key_approvers = set(answer_key_map[threshold_key].get('approvers', []))
            if candidate_approvers and candidate_approvers.issubset(key_approvers):
                score += 1
            
            # Check documentation (+2 points)
            candidate_docs = set(threshold_map[threshold_key].get('documentation', []))
            key_docs = set(answer_key_map[threshold_key].get('documentation', []))
            if candidate_docs and len(candidate_docs.intersection(key_docs)) >= len(candidate_docs) * 0.7:
                score += 2
    
    return score, max_score

def validate_conflict_of_interest(policy, answer_key_policy):
    """Validate the conflict of interest policy and assign points."""
    score = 0
    max_score = 6
    
    if not policy:
        return score, max_score
    
    # Check if requires disclosure (+2 points)
    disclosure_keywords = ['disclose', 'disclosure', 'report', 'declare']
    if any(keyword in policy.lower() for keyword in disclosure_keywords):
        score += 2
    
    # Check if specifies when/how (+2 points)
    when_how_keywords = ['annual', 'yearly', 'when', 'form', 'process', 'procedure']
    if any(keyword in policy.lower() for keyword in when_how_keywords):
        score += 2
    
    # Check if addresses management of conflicts (+2 points)
    management_keywords = ['recuse', 'avoid', 'mitigate', 'manage', 'review']
    if any(keyword in policy.lower() for keyword in management_keywords):
        score += 2
    
    return score, max_score

def validate_emergency_purchases(policy, answer_key_policy):
    """Validate the emergency purchases policy and assign points."""
    score = 0
    max_score = 6
    
    if not policy:
        return score, max_score
    
    # Check if defines emergency (+2 points)
    emergency_keywords = ['immediate risk', 'health', 'safety', 'business continuity', 'urgent']
    if any(keyword in policy.lower() for keyword in emergency_keywords):
        score += 2
    
    # Check if includes approval requirements (+2 points)
    approval_keywords = ['certified', 'documented', 'approved', 'director', 'manager']
    if any(keyword in policy.lower() for keyword in approval_keywords):
        score += 2
    
    # Check if includes post-purchase review (+2 points)
    review_keywords = ['review', 'documentation', 'within 5', 'within five', '30 days', 'thirty days', 'compliance']
    if any(keyword in policy.lower() for keyword in review_keywords):
        score += 2
    
    return score, max_score

def validate_evaluation_criteria(criteria, answer_key_criteria):
    """Validate the evaluation criteria and assign points."""
    score = 0
    max_score = 15
    
    if not criteria:
        return score, max_score
    
    # Check if includes all 5 criteria (+5 points)
    expected_criteria = {'Price', 'Technical compliance', 'Vendor reliability', 'Delivery timeline', 'Warranty/support'}
    candidate_criteria = {c.get('criterion', '') for c in criteria}
    
    if candidate_criteria == expected_criteria:
        score += 5
    
    # Check if weights total exactly 1.0 (+5 points)
    total_weight = sum(c.get('weight', 0) for c in criteria)
    if 0.99 <= total_weight <= 1.01:  # Allow for small floating point errors
        score += 5
    
    # Check if scoring definitions are specific and measurable (+5 points)
    definition_count = 0
    meaningful_definitions = 0
    
    for criterion in criteria:
        definitions = criterion.get('scoring_definitions', {})
        for score_key in ['1', '2', '3', '4', '5']:
            if score_key in definitions:
                definition_count += 1
                definition = definitions[score_key]
                if definition and count_words(definition) >= 10:
                    meaningful_definitions += 1
    
    if definition_count == 25 and meaningful_definitions >= 20:
        score += 5
    elif definition_count >= 20 and meaningful_definitions >= 15:
        score += 3
    elif definition_count >= 15 and meaningful_definitions >= 10:
        score += 1
    
    return score, max_score

def validate_vendor_evaluations(evaluations, answer_key_evaluations):
    """Validate the vendor evaluations and assign points."""
    score = 0
    max_score = 9
    
    if not evaluations or len(evaluations) != 3:
        return score, max_score
    
    # Create mappings for easier comparison
    eval_map = {e.get('vendor_name', ''): e for e in evaluations}
    key_map = {e.get('vendor_name', ''): e for e in answer_key_evaluations}
    
    # Check each vendor
    for vendor_name in ['TechSupply Inc.', 'Global Electronics', 'Digital Solutions']:
        if vendor_name in eval_map and vendor_name in key_map:
            vendor_score = 0
            
            # Check if scores are justified by data (+1 point)
            candidate_scores = eval_map[vendor_name].get('criteria_scores', {})
            key_scores = key_map[vendor_name].get('criteria_scores', {})
            
            if candidate_scores and all(abs(candidate_scores.get(k, 0) - key_scores.get(k, 0)) <= 1 for k in key_scores):
                vendor_score += 1
            
            # Check if weighted calculation is correct (+2 points)
            candidate_total = eval_map[vendor_name].get('total_weighted_score', 0)
            
            # Calculate expected total
            expected_total = 0
            for criterion, score in candidate_scores.items():
                for c in evaluations[0].get('criteria_scores', {}):
                    if c.get('criterion') == criterion:
                        weight = c.get('weight', 0)
                        expected_total += score * weight
                        break
            
            if abs(candidate_total - expected_total) <= 0.1:
                vendor_score += 2
            
            score += vendor_score
    
    return score, max_score

def validate_winning_bid(winning_bid, evaluations, answer_key_winning_bid):
    """Validate the winning bid and assign points."""
    score = 0
    max_score = 6
    
    if not winning_bid or not evaluations:
        return score, max_score
    
    # Find the vendor with the highest score
    highest_score = 0
    highest_vendor = None
    
    for evaluation in evaluations:
        total_score = evaluation.get('total_weighted_score', 0)
        if total_score > highest_score:
            highest_score = total_score
            highest_vendor = evaluation.get('vendor_name', '')
    
    # Check if winning bid matches vendor with highest score
    if winning_bid == highest_vendor:
        score += 6
    
    return score, max_score

def validate_process_steps(steps, answer_key_steps):
    """Validate the process steps and assign points."""
    score = 0
    max_score = 15
    
    if not steps or len(steps) < 8:
        return score, max_score
    
    # Check if covers full procurement cycle (+5 points)
    procurement_stages = {
        'requisition': False,
        'approval': False,
        'sourcing': False,
        'evaluation': False,
        'order': False,
        'receipt': False,
        'payment': False
    }
    
    stage_keywords = {
        'requisition': ['requisition', 'request', 'need'],
        'approval': ['approval', 'review', 'authorize'],
        'sourcing': ['source', 'bid', 'quote', 'rfp', 'rfq'],
        'evaluation': ['evaluate', 'selection', 'compare'],
        'order': ['order', 'purchase order', 'po'],
        'receipt': ['receipt', 'receive', 'delivery', 'inspect'],
        'payment': ['payment', 'invoice', 'pay']
    }
    
    for step in steps:
        step_name = step.get('step_name', '').lower()
        step_desc = step.get('description', '').lower()
        combined_text = step_name + ' ' + step_desc
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                procurement_stages[stage] = True
    
    coverage_score = sum(1 for stage in procurement_stages.values() if stage)
    if coverage_score >= 6:
        score += 5
    elif coverage_score >= 5:
        score += 3
    elif coverage_score >= 4:
        score += 1
    
    # Check if follows logical sequence (+5 points)
    expected_sequence = ['requisition', 'approval', 'sourcing', 'evaluation', 'order', 'receipt', 'payment']
    found_stages = []
    
    for step in steps:
        step_name = step.get('step_name', '').lower()
        step_desc = step.get('description', '').lower()
        combined_text = step_name + ' ' + step_desc
        
        for stage in expected_sequence:
            if stage not in found_stages and any(keyword in combined_text for keyword in stage_keywords[stage]):
                found_stages.append(stage)
                break
    
    # Check if the found stages are in the correct order
    is_sequence_correct = True
    for i in range(len(found_stages) - 1):
        idx1 = expected_sequence.index(found_stages[i])
        idx2 = expected_sequence.index(found_stages[i + 1])
        if idx1 >= idx2:
            is_sequence_correct = False
            break
    
    if is_sequence_correct and len(found_stages) >= 5:
        score += 5
    elif is_sequence_correct and len(found_stages) >= 4:
        score += 3
    elif len(found_stages) >= 3:
        score += 1
    
    # Check if uses only specified roles (+3 points)
    allowed_roles = {'Requester', 'Purchasing Agent', 'Department Manager', 'Finance Director', 'CEO'}
    used_roles = {step.get('responsible_role', '') for step in steps}
    
    if used_roles.issubset(allowed_roles):
        score += 3
    
    # Check if timeframes are realistic (+2 points)
    realistic_timeframes = True
    for step in steps:
        timeframe = step.get('estimated_timeframe', '')
        try:
            timeframe = float(timeframe)
            if timeframe <= 0 or timeframe > 30:
                realistic_timeframes = False
                break
        except (ValueError, TypeError):
            realistic_timeframes = False
            break
    
    if realistic_timeframes:
        score += 2
    
    return score, max_score

def validate_decision_points(decision_points, process_steps, task1_thresholds):
    """Validate the decision points and assign points."""
    score = 0
    max_score = 9
    
    if not decision_points or len(decision_points) < 3:
        return score, max_score
    
    # Check if aligns with approval thresholds (+3 points)
    threshold_alignment = False
    for dp in decision_points:
        description = dp.get('description', '').lower()
        options = dp.get('options', [])
        option_texts = [opt.get('condition', '').lower() for opt in options]
        
        threshold_keywords = ['threshold', 'value', 'amount', 'cost', 'price']
        if any(keyword in description for keyword in threshold_keywords):
            if any('$5,000' in opt for opt in option_texts):
                threshold_alignment = True
                break
    
    if threshold_alignment:
        score += 3
    
    # Check if conditions are clear (+3 points)
    clear_conditions = True
    for dp in decision_points:
        options = dp.get('options', [])
        for option in options:
            condition = option.get('condition', '')
            if not condition or count_words(condition) < 3:
                clear_conditions = False
                break
    
    if clear_conditions:
        score += 3
    
    # Check if next steps are logical (+3 points)
    logical_next_steps = True
    max_step_number = max(step.get('step_number', 0) for step in process_steps) if process_steps else 0
    
    for dp in decision_points:
        options = dp.get('options', [])
        for option in options:
            next_step = option.get('next_step', 0)
            if not isinstance(next_step, (int, float)) or next_step <= 0 or next_step > max_step_number:
                logical_next_steps = False
                break
    
    if logical_next_steps:
        score += 3
    
    return score, max_score

def validate_roles_and_timeframes(process_steps):
    """Validate the roles and timeframes and assign points."""
    score = 0
    max_score = 6
    
    if not process_steps:
        return score, max_score
    
    # Check if roles are appropriate for steps (+3 points)
    role_appropriateness = {
        'Requester': ['requisition', 'need', 'receive', 'inspect'],
        'Purchasing Agent': ['source', 'bid', 'quote', 'evaluate', 'order', 'purchase'],
        'Department Manager': ['approve', 'review', 'authorize'],
        'Finance Director': ['budget', 'financial', 'payment', 'invoice'],
        'CEO': ['executive', 'final', 'high-value', 'strategic']
    }
    
    appropriate_roles = True
    for step in process_steps:
        role = step.get('responsible_role', '')
        step_name = step.get('step_name', '').lower()
        step_desc = step.get('description', '').lower()
        combined_text = step_name + ' ' + step_desc
        
        if role in role_appropriateness:
            if not any(keyword in combined_text for keyword in role_appropriateness[role]):
                appropriate_roles = False
                break
    
    if appropriate_roles:
        score += 3
    
    # Check if timeframes are appropriate for steps (+3 points)
    timeframe_appropriateness = {
        'requisition': (1, 3),
        'approval': (1, 5),
        'sourcing': (3, 10),
        'evaluation': (2, 7),
        'order': (1, 3),
        'receipt': (1, 5),
        'payment': (2, 10)
    }
    
    appropriate_timeframes = True
    for step in process_steps:
        timeframe = step.get('estimated_timeframe', '')
        step_name = step.get('step_name', '').lower()
        step_desc = step.get('description', '').lower()
        combined_text = step_name + ' ' + step_desc
        
        try:
            timeframe = float(timeframe)
            
            for stage, (min_time, max_time) in timeframe_appropriateness.items():
                stage_keywords = {
                    'requisition': ['requisition', 'request', 'need'],
                    'approval': ['approval', 'review', 'authorize'],
                    'sourcing': ['source', 'bid', 'quote', 'rfp', 'rfq'],
                    'evaluation': ['evaluate', 'selection', 'compare'],
                    'order': ['order', 'purchase order', 'po'],
                    'receipt': ['receipt', 'receive', 'delivery', 'inspect'],
                    'payment': ['payment', 'invoice', 'pay']
                }
                
                if any(keyword in combined_text for keyword in stage_keywords[stage]):
                    if timeframe < min_time or timeframe > max_time:
                        appropriate_timeframes = False
                        break
            
            if not appropriate_timeframes:
                break
                
        except (ValueError, TypeError):
            appropriate_timeframes = False
            break
    
    if appropriate_timeframes:
        score += 3
    
    return score, max_score

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Procurement Policy Framework."""
    task1_results = {
        "policy_statement": {
            "score": 0,
            "max_score": 6,
            "comments": ""
        },
        "approval_thresholds": {
            "score": 0,
            "max_score": 12,
            "comments": ""
        },
        "conflict_of_interest": {
            "score": 0,
            "max_score": 6,
            "comments": ""
        },
        "emergency_purchases": {
            "score": 0,
            "max_score": 6,
            "comments": ""
        },
        "total_score": 0,
        "max_score": 30,
        "passed": False
    }
    
    # Get task1 data
    task1 = submission.get('task1_policy_framework', {})
    key_task1 = answer_key.get('task1_policy_framework', {})
    
    # Validate policy statement
    policy_statement = task1.get('policy_statement', '')
    key_policy_statement = key_task1.get('policy_statement', '')
    score, max_score = validate_policy_statement(policy_statement, key_policy_statement)
    task1_results['policy_statement']['score'] = score
    task1_results['policy_statement']['max_score'] = max_score
    
    # Validate approval thresholds
    approval_thresholds = task1.get('approval_thresholds', [])
    key_approval_thresholds = key_task1.get('approval_thresholds', [])
    score, max_score = validate_approval_thresholds(approval_thresholds, key_approval_thresholds)
    task1_results['approval_thresholds']['score'] = score
    task1_results['approval_thresholds']['max_score'] = max_score
    
    # Validate conflict of interest
    conflict_of_interest = task1.get('conflict_of_interest', '')
    key_conflict_of_interest = key_task1.get('conflict_of_interest', '')
    score, max_score = validate_conflict_of_interest(conflict_of_interest, key_conflict_of_interest)
    task1_results['conflict_of_interest']['score'] = score
    task1_results['conflict_of_interest']['max_score'] = max_score
    
    # Validate emergency purchases
    emergency_purchases = task1.get('emergency_purchases', '')
    key_emergency_purchases = key_task1.get('emergency_purchases', '')
    score, max_score = validate_emergency_purchases(emergency_purchases, key_emergency_purchases)
    task1_results['emergency_purchases']['score'] = score
    task1_results['emergency_purchases']['max_score'] = max_score
    
    # Calculate total score
    task1_results['total_score'] = (
        task1_results['policy_statement']['score'] +
        task1_results['approval_thresholds']['score'] +
        task1_results['conflict_of_interest']['score'] +
        task1_results['emergency_purchases']['score']
    )
    
    # Check if passed
    task1_results['passed'] = task1_results['total_score'] >= 21
    
    return task1_results

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Bid Evaluation Matrix."""
    task2_results = {
        "evaluation_criteria": {
            "score": 0,
            "max_score": 15,
            "comments": ""
        },
        "vendor_evaluations": {
            "score": 0,
            "max_score": 9,
            "comments": ""
        },
        "winning_bid": {
            "score": 0,
            "max_score": 6,
            "comments": ""
        },
        "total_score": 0,
        "max_score": 40,
        "passed": False
    }
    
    # Get task2 data
    task2 = submission.get('task2_bid_evaluation', {})
    key_task2 = answer_key.get('task2_bid_evaluation', {})
    
    # Validate evaluation criteria
    evaluation_criteria = task2.get('evaluation_criteria', [])
    key_evaluation_criteria = key_task2.get('evaluation_criteria', [])
    score, max_score = validate_evaluation_criteria(evaluation_criteria, key_evaluation_criteria)
    task2_results['evaluation_criteria']['score'] = score
    task2_results['evaluation_criteria']['max_score'] = max_score
    
    # Validate vendor evaluations
    vendor_evaluations = task2.get('vendor_evaluations', [])
    key_vendor_evaluations = key_task2.get('vendor_evaluations', [])
    score, max_score = validate_vendor_evaluations(vendor_evaluations, key_vendor_evaluations)
    task2_results['vendor_evaluations']['score'] = score
    task2_results['vendor_evaluations']['max_score'] = max_score
    
    # Validate winning bid
    winning_bid = task2.get('winning_bid', '')
    key_winning_bid = key_task2.get('winning_bid', '')
    score, max_score = validate_winning_bid(winning_bid, vendor_evaluations, key_winning_bid)
    task2_results['winning_bid']['score'] = score
    task2_results['winning_bid']['max_score'] = max_score
    
    # Calculate total score
    task2_results['total_score'] = (
        task2_results['evaluation_criteria']['score'] +
        task2_results['vendor_evaluations']['score'] +
        task2_results['winning_bid']['score']
    )
    
    # Check if passed
    task2_results['passed'] = task2_results['total_score'] >= 28
    
    return task2_results

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Procurement Process Flowchart."""
    task3_results = {
        "process_steps": {
            "score": 0,
            "max_score": 15,
            "comments": ""
        },
        "decision_points": {
            "score": 0,
            "max_score": 9,
            "comments": ""
        },
        "roles_and_timeframes": {
            "score": 0,
            "max_score": 6,
            "comments": ""
        },
        "total_score": 0,
        "max_score": 30,
        "passed": False
    }
    
    # Get task3 data
    task3 = submission.get('task3_process_flowchart', {})
    key_task3 = answer_key.get('task3_process_flowchart', {})
    task1 = submission.get('task1_policy_framework', {})
    
    # Validate process steps
    process_steps = task3.get('process_steps', [])
    key_process_steps = key_task3.get('process_steps', [])
    score, max_score = validate_process_steps(process_steps, key_process_steps)
    task3_results['process_steps']['score'] = score
    task3_results['process_steps']['max_score'] = max_score
    
    # Validate decision points
    decision_points = task3.get('decision_points', [])
    key_decision_points = key_task3.get('decision_points', [])
    approval_thresholds = task1.get('approval_thresholds', [])
    score, max_score = validate_decision_points(decision_points, process_steps, approval_thresholds)
    task3_results['decision_points']['score'] = score
    task3_results['decision_points']['max_score'] = max_score
    
    # Validate roles and timeframes
    score, max_score = validate_roles_and_timeframes(process_steps)
    task3_results['roles_and_timeframes']['score'] = score
    task3_results['roles_and_timeframes']['max_score'] = max_score
    
    # Calculate total score
    task3_results['total_score'] = (
        task3_results['process_steps']['score'] +
        task3_results['decision_points']['score'] +
        task3_results['roles_and_timeframes']['score']
    )
    
    # Check if passed
    task3_results['passed'] = task3_results['total_score'] >= 21
    
    return task3_results

def evaluate_submission(submission_path, answer_key_path):
    """Evaluate the candidate's submission against the answer key."""
    try:
        with open(submission_path, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_path, 'r') as f:
            answer_key = json.load(f)
        
        # Evaluate each task
        task1_results = evaluate_task1(submission, answer_key)
        task2_results = evaluate_task2(submission, answer_key)
        task3_results = evaluate_task3(submission, answer_key)
        
        # Calculate overall score
        total_score = task1_results['total_score'] + task2_results['total_score'] + task3_results['total_score']
        max_score = task1_results['max_score'] + task2_results['max_score'] + task3_results['max_score']
        overall_score_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Check if overall passed
        passed = (
            task1_results['passed'] and
            task2_results['passed'] and
            task3_results['passed'] and
            overall_score_percentage >= 70
        )
        
        # Compile results
        results = {
            "candidate_id": submission.get('candidate_id', 'Unknown'),
            "task1_results": task1_results,
            "task2_results": task2_results,
            "task3_results": task3_results,
            "total_score": total_score,
            "max_score": max_score,
            "overall_score": round(overall_score_percentage, 2),
            "passed": passed
        }
        
        return results
    
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0,
            "passed": False
        }

def main():
    """Main function to run the evaluation."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    submission_path = os.path.join(script_dir, 'test_submission.json')
    answer_key_path = os.path.join(script_dir, 'answer_key.json')
    results_path = os.path.join(script_dir, 'test_results.json')
    
    # Evaluate the submission
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Save the results
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation completed. Results saved to {results_path}")
    print(f"Overall score: {results.get('overall_score', 0)}%")
    print(f"Passed: {results.get('passed', False)}")

if __name__ == "__main__":
    main()