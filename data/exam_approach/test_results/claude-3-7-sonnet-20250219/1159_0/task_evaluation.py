import json
import sys
from typing import Dict, List, Any, Union

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_bid_thresholds(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the bid thresholds section."""
    sub_thresholds = submission.get("bidThreshold", {})
    key_thresholds = answer_key.get("bidThreshold", {})
    
    total_items = 0
    correct_items = 0
    details = {}
    
    for category in key_thresholds:
        if category not in sub_thresholds:
            details[category] = "Missing category"
            continue
        
        for tier in key_thresholds[category]:
            total_items += 1
            if tier in sub_thresholds[category] and sub_thresholds[category][tier] == key_thresholds[category][tier]:
                correct_items += 1
                details[f"{category}_{tier}"] = "Correct"
            else:
                details[f"{category}_{tier}"] = f"Incorrect: Expected '{key_thresholds[category].get(tier, 'Missing')}', got '{sub_thresholds[category].get(tier, 'Missing')}'"
    
    percentage = (correct_items / total_items * 100) if total_items > 0 else 0
    return {
        "score": percentage,
        "correct_items": correct_items,
        "total_items": total_items,
        "details": details
    }

def evaluate_approval_process(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the approval process section."""
    sub_process = submission.get("approvalProcess", {})
    key_process = answer_key.get("approvalProcess", {})
    
    total_tiers = len(key_process)
    correct_tiers = 0
    details = {}
    
    for tier in key_process:
        if tier not in sub_process:
            details[tier] = "Missing tier"
            continue
        
        # Check if steps are in the correct sequence and all are present
        key_steps = key_process[tier]
        sub_steps = sub_process[tier]
        
        # Count correct steps in proper sequence
        correct_steps = 0
        total_steps = len(key_steps)
        
        # Check if all key steps are in the submission in correct order
        for i, step in enumerate(key_steps):
            if i < len(sub_steps) and step == sub_steps[i]:
                correct_steps += 1
        
        step_percentage = (correct_steps / total_steps * 100) if total_steps > 0 else 0
        if step_percentage >= 80:  # At least 80% correct steps
            correct_tiers += 1
            details[tier] = f"Correct ({correct_steps}/{total_steps} steps correct, {step_percentage:.1f}%)"
        else:
            details[tier] = f"Incorrect ({correct_steps}/{total_steps} steps correct, {step_percentage:.1f}%)"
    
    percentage = (correct_tiers / total_tiers * 100) if total_tiers > 0 else 0
    return {
        "score": percentage,
        "correct_tiers": correct_tiers,
        "total_tiers": total_tiers,
        "details": details
    }

def evaluate_required_documents(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the required documents section."""
    sub_docs = submission.get("requiredDocuments", {})
    key_docs = answer_key.get("requiredDocuments", {})
    
    total_tiers = len(key_docs)
    correct_tiers = 0
    details = {}
    
    for tier in key_docs:
        if tier not in sub_docs:
            details[tier] = "Missing tier"
            continue
        
        key_tier_docs = set(key_docs[tier])
        sub_tier_docs = set(sub_docs[tier])
        
        correct_docs = len(key_tier_docs.intersection(sub_tier_docs))
        total_docs = len(key_tier_docs)
        
        percentage = (correct_docs / total_docs * 100) if total_docs > 0 else 0
        
        if percentage >= 75:  # At least 75% correct documents
            correct_tiers += 1
            details[tier] = f"Correct ({correct_docs}/{total_docs} docs correct, {percentage:.1f}%)"
        else:
            details[tier] = f"Incorrect ({correct_docs}/{total_docs} docs correct, {percentage:.1f}%)"
    
    score_percentage = (correct_tiers / total_tiers * 100) if total_tiers > 0 else 0
    return {
        "score": score_percentage,
        "correct_tiers": correct_tiers,
        "total_tiers": total_tiers,
        "details": details
    }

def evaluate_evaluation_criteria(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the evaluation criteria section."""
    sub_criteria = submission.get("evaluationCriteria", {})
    key_criteria = answer_key.get("evaluationCriteria", {})
    
    # Check if criteria percentages sum to 100
    sub_total = sum(sub_criteria.values())
    key_total = sum(key_criteria.values())
    
    # Check if at least 3 of 5 correct criteria are included
    correct_criteria = set(sub_criteria.keys()).intersection(set(key_criteria.keys()))
    correct_count = len(correct_criteria)
    
    # Check if criteria values match
    matching_values = 0
    for criterion in correct_criteria:
        if sub_criteria[criterion] == key_criteria[criterion]:
            matching_values += 1
    
    details = {
        "sum_to_100": sub_total == 100,
        "criteria_included": f"{correct_count}/5 correct criteria included",
        "matching_values": f"{matching_values}/{correct_count} criteria have correct values"
    }
    
    # Determine score based on criteria
    if sub_total != 100:  # Critical fail
        score = 0
    elif correct_count < 3:  # Not enough correct criteria
        score = 25  # Partial credit
    else:
        # Base score on matching values if at least 3 criteria are correct
        score = (matching_values / len(key_criteria)) * 100
    
    return {
        "score": score,
        "details": details
    }

def evaluate_task1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1 with all its components."""
    bid_thresholds = evaluate_bid_thresholds(submission.get("task1", {}), answer_key.get("task1", {}))
    approval_process = evaluate_approval_process(submission.get("task1", {}), answer_key.get("task1", {}))
    required_documents = evaluate_required_documents(submission.get("task1", {}), answer_key.get("task1", {}))
    evaluation_criteria = evaluate_evaluation_criteria(submission.get("task1", {}), answer_key.get("task1", {}))
    
    # Calculate overall score for Task 1 (equal weighting of components)
    score = (
        bid_thresholds["score"] * 0.25 +
        approval_process["score"] * 0.25 +
        required_documents["score"] * 0.25 +
        evaluation_criteria["score"] * 0.25
    )
    
    # Check for critical fail conditions
    if evaluation_criteria["details"]["sum_to_100"] is False:
        critical_fail = "Evaluation criteria don't total 100%"
    else:
        critical_fail = None
    
    return {
        "score": score,
        "bid_thresholds": bid_thresholds,
        "approval_process": approval_process,
        "required_documents": required_documents,
        "evaluation_criteria": evaluation_criteria,
        "critical_fail": critical_fail
    }

def evaluate_vendor_selection(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the vendor selection section of Task 2."""
    sub_vendor = submission.get("vendorSelection", "")
    key_vendor = answer_key.get("vendorSelection", "")
    
    is_correct = sub_vendor == key_vendor
    
    return {
        "score": 100 if is_correct else 0,
        "details": "Correct" if is_correct else f"Incorrect: Expected '{key_vendor}', got '{sub_vendor}'"
    }

def evaluate_total_cost(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the total cost section of Task 2."""
    sub_cost = submission.get("totalCost", 0)
    key_cost = answer_key.get("totalCost", 0)
    
    # Must be within $1,000 of correct amount
    is_within_range = abs(sub_cost - key_cost) <= 1000
    
    return {
        "score": 100 if is_within_range else 0,
        "details": f"Within acceptable range" if is_within_range else f"Outside acceptable range: Expected '{key_cost}', got '{sub_cost}'"
    }

def evaluate_compliance_status(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the compliance status section of Task 2."""
    sub_status = submission.get("complianceStatus", None)
    key_status = answer_key.get("complianceStatus", None)
    
    is_correct = sub_status == key_status
    
    return {
        "score": 100 if is_correct else 0,
        "details": "Correct" if is_correct else f"Incorrect: Expected '{key_status}', got '{sub_status}'"
    }

def evaluate_documentation_needed(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the documentation needed section of Task 2."""
    sub_docs = set(submission.get("documentationNeeded", []))
    key_docs = set(answer_key.get("documentationNeeded", []))
    
    correct_docs = len(sub_docs.intersection(key_docs))
    total_docs = len(key_docs)
    
    # Need at least 5 of 7 correct documents
    meets_criteria = correct_docs >= 5
    percentage = (correct_docs / total_docs * 100) if total_docs > 0 else 0
    
    return {
        "score": percentage,
        "details": f"{correct_docs}/{total_docs} correct documents identified ({percentage:.1f}%)"
    }

def evaluate_task2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2 with all its components."""
    vendor_selection = evaluate_vendor_selection(submission.get("task2", {}), answer_key.get("task2", {}))
    total_cost = evaluate_total_cost(submission.get("task2", {}), answer_key.get("task2", {}))
    compliance_status = evaluate_compliance_status(submission.get("task2", {}), answer_key.get("task2", {}))
    documentation_needed = evaluate_documentation_needed(submission.get("task2", {}), answer_key.get("task2", {}))
    
    # Calculate overall score for Task 2 (equal weighting of components)
    score = (
        vendor_selection["score"] * 0.3 +
        total_cost["score"] * 0.2 +
        compliance_status["score"] * 0.3 +
        documentation_needed["score"] * 0.2
    )
    
    # Check for critical fail condition
    sub_status = submission.get("task2", {}).get("complianceStatus", None)
    critical_fail = "Selected non-compliant vendor" if sub_status is False else None
    
    return {
        "score": score,
        "vendor_selection": vendor_selection,
        "total_cost": total_cost,
        "compliance_status": compliance_status,
        "documentation_needed": documentation_needed,
        "critical_fail": critical_fail
    }

def evaluate_policy_statement(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the policy statement section of Task 3."""
    sub_policy = submission.get("policyStatement", "")
    key_policy = answer_key.get("policyStatement", "")
    
    is_correct = sub_policy == key_policy
    
    # Critical fail if they selected policy statement #1 (too permissive)
    is_critical_fail = sub_policy == "Emergency procurements are exempt from all standard procurement procedures."
    
    return {
        "score": 100 if is_correct else 0,
        "details": "Correct" if is_correct else "Incorrect",
        "critical_fail": "Selected overly permissive policy" if is_critical_fail else None
    }

def evaluate_procedure_steps(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the procedure steps section of Task 3."""
    sub_steps = submission.get("procedureSteps", [])
    key_steps = answer_key.get("procedureSteps", [])
    
    # Check how many steps from the key are in the submission
    common_steps = set(sub_steps).intersection(set(key_steps))
    correct_step_count = len(common_steps)
    total_steps = len(key_steps)
    
    # Need at least 7 of 10 steps in reasonable sequence
    meets_criteria = correct_step_count >= 7
    percentage = (correct_step_count / total_steps * 100) if total_steps > 0 else 0
    
    return {
        "score": percentage,
        "details": f"{correct_step_count}/{total_steps} correct steps ({percentage:.1f}%)"
    }

def evaluate_compliance_rating(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the compliance rating section of Task 3."""
    sub_ratings = submission.get("complianceRating", {})
    key_ratings = answer_key.get("complianceRating", {})
    
    # Calculate average rating if sufficient steps are provided
    if len(sub_ratings) > 0:
        avg_rating = sum(sub_ratings.values()) / len(sub_ratings)
    else:
        avg_rating = 0
    
    # Average rating must be at least 4.0
    meets_criteria = avg_rating >= 4.0
    
    return {
        "score": 100 if meets_criteria else (avg_rating / 4.0) * 100,
        "details": f"Average rating: {avg_rating:.2f}"
    }

def evaluate_task3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3 with all its components."""
    policy_statement = evaluate_policy_statement(submission.get("task3", {}), answer_key.get("task3", {}))
    procedure_steps = evaluate_procedure_steps(submission.get("task3", {}), answer_key.get("task3", {}))
    compliance_rating = evaluate_compliance_rating(submission.get("task3", {}), answer_key.get("task3", {}))
    
    # Calculate overall score for Task 3 (equal weighting of components)
    score = (
        policy_statement["score"] * 0.4 +
        procedure_steps["score"] * 0.3 +
        compliance_rating["score"] * 0.3
    )
    
    # Check for critical fail from policy statement
    critical_fail = policy_statement.get("critical_fail")
    
    return {
        "score": score,
        "policy_statement": policy_statement,
        "procedure_steps": procedure_steps,
        "compliance_rating": compliance_rating,
        "critical_fail": critical_fail
    }

def check_enterprise_approval(submission: Dict) -> bool:
    """Check if board approval is properly included for enterprise purchases."""
    enterprise_approvals = submission.get("task1", {}).get("approvalProcess", {}).get("Enterprise", [])
    return "Board Vote" in enterprise_approvals

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Additional critical fail check for enterprise approval
    board_approval_fail = None if check_enterprise_approval(submission) else "Failed to recognize need for Board approval for enterprise-level purchases"
    
    # Collect all critical fails
    critical_fails = []
    if task1_results.get("critical_fail"):
        critical_fails.append(task1_results["critical_fail"])
    if task2_results.get("critical_fail"):
        critical_fails.append(task2_results["critical_fail"])
    if task3_results.get("critical_fail"):
        critical_fails.append(task3_results["critical_fail"])
    if board_approval_fail:
        critical_fails.append(board_approval_fail)
    
    # Calculate overall score (equal weighting of tasks)
    # If there are critical fails, cap the score at 65%
    raw_score = (
        task1_results["score"] * (1/3) +
        task2_results["score"] * (1/3) +
        task3_results["score"] * (1/3)
    )
    
    overall_score = min(raw_score, 65.0) if critical_fails else raw_score
    passed = overall_score >= 75.0 and not critical_fails
    
    return {
        "overall_score": overall_score,
        "passed": passed,
        "critical_fails": critical_fails,
        "task1_results": task1_results,
        "task2_results": task2_results,
        "task3_results": task3_results
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
    if results["critical_fails"]:
        print("Critical fails detected:")
        for fail in results["critical_fails"]:
            print(f"- {fail}")
    print(f"Test {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()