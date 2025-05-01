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
    """Evaluate Task 1: Contract Analysis"""
    score = 0
    feedback = {}
    
    # Evaluate key requirements (5 points)
    correct_requirements = set([req.lower() for req in answer_key["task1"]["keyRequirements"]])
    submitted_requirements = set([req.lower() for req in submission["task1"]["keyRequirements"]])
    correct_req_count = sum(1 for req in submitted_requirements if any(req in correct_req.lower() for correct_req in correct_requirements))
    req_score = min(5, correct_req_count * 5 / 5)  # 5 points max
    feedback["keyRequirements"] = {
        "score": req_score,
        "max_score": 5,
        "feedback": f"Identified {correct_req_count}/5 key requirements correctly."
    }
    score += req_score
    
    # Evaluate potential challenges (5 points)
    correct_challenges = set([ch.lower() for ch in answer_key["task1"]["potentialChallenges"]])
    submitted_challenges = set([ch.lower() for ch in submission["task1"]["potentialChallenges"]])
    correct_ch_count = sum(1 for ch in submitted_challenges if any(ch in correct_ch.lower() for correct_ch in correct_challenges))
    ch_score = min(5, correct_ch_count * 5 / 3)  # 5 points max
    feedback["potentialChallenges"] = {
        "score": ch_score,
        "max_score": 5,
        "feedback": f"Identified {correct_ch_count}/3 potential challenges correctly."
    }
    score += ch_score
    
    # Evaluate non-negotiable points (7.5 points)
    correct_non_neg = set([p.lower() for p in answer_key["task1"]["nonNegotiablePoints"]])
    submitted_non_neg = set([p.lower() for p in submission["task1"]["nonNegotiablePoints"]])
    correct_non_neg_count = sum(1 for p in submitted_non_neg if any(p in correct_p.lower() for correct_p in correct_non_neg))
    non_neg_score = min(7.5, correct_non_neg_count * 7.5 / 5)  # 7.5 points max
    feedback["nonNegotiablePoints"] = {
        "score": non_neg_score,
        "max_score": 7.5,
        "feedback": f"Identified {correct_non_neg_count}/5 non-negotiable points correctly."
    }
    score += non_neg_score
    
    # Evaluate flexible points (7.5 points)
    correct_flex = set([p.lower() for p in answer_key["task1"]["flexiblePoints"]])
    submitted_flex = set([p.lower() for p in submission["task1"]["flexiblePoints"]])
    correct_flex_count = sum(1 for p in submitted_flex if any(p in correct_p.lower() for correct_p in correct_flex))
    flex_score = min(7.5, correct_flex_count * 7.5 / 4)  # 7.5 points max
    feedback["flexiblePoints"] = {
        "score": flex_score,
        "max_score": 7.5,
        "feedback": f"Identified {correct_flex_count}/4 flexible points correctly."
    }
    score += flex_score
    
    return score, feedback

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Negotiation Strategy"""
    score = 0
    feedback = {}
    
    # Evaluate proposed fee (5 points)
    proposed_fee = submission["task2"]["proposedFee"]
    if proposed_fee <= 75000:
        fee_score = 5
        fee_feedback = "Proposed fee is within budget constraint."
    else:
        fee_score = 0
        fee_feedback = "Proposed fee exceeds the $75,000 budget constraint."
    
    feedback["proposedFee"] = {
        "score": fee_score,
        "max_score": 5,
        "feedback": fee_feedback
    }
    score += fee_score
    
    # Evaluate cost breakdown (7.5 points)
    breakdown = submission["task2"]["breakdownOfCosts"]
    total_costs = sum(breakdown.values())
    
    # Check if breakdown is realistic and sums correctly
    if abs(total_costs - (proposed_fee / (1 + submission["task2"]["profitMargin"]/100))) < 0.01:
        breakdown_score = 7.5
        breakdown_feedback = "Cost breakdown is realistic and sums correctly."
    else:
        breakdown_score = 0
        breakdown_feedback = "Cost breakdown does not sum correctly with the profit margin."
    
    feedback["breakdownOfCosts"] = {
        "score": breakdown_score,
        "max_score": 7.5,
        "feedback": breakdown_feedback
    }
    score += breakdown_score
    
    # Evaluate profit margin (5 points)
    profit_margin = submission["task2"]["profitMargin"]
    if profit_margin >= 25:
        margin_score = 5
        margin_feedback = "Profit margin meets or exceeds the 25% requirement."
    else:
        margin_score = 0
        margin_feedback = "Profit margin is below the required 25%."
    
    feedback["profitMargin"] = {
        "score": margin_score,
        "max_score": 5,
        "feedback": margin_feedback
    }
    score += margin_score
    
    # Evaluate value justification (7.5 points)
    correct_justifications = set([j.lower() for j in answer_key["task2"]["valueJustification"]])
    submitted_justifications = set([j.lower() for j in submission["task2"]["valueJustification"]])
    correct_just_count = sum(1 for j in submitted_justifications if any(j in correct_j.lower() for correct_j in correct_justifications))
    just_score = min(7.5, correct_just_count * 7.5 / 4)  # 7.5 points max
    
    feedback["valueJustification"] = {
        "score": just_score,
        "max_score": 7.5,
        "feedback": f"Provided {correct_just_count}/4 relevant and compelling value justification points."
    }
    score += just_score
    
    return score, feedback

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Objection Handling"""
    score = 0
    feedback = {}
    
    # Check each objection response (5 points each)
    for i in range(1, 6):
        objection_key = f"objection{i}Response"
        if submission["task3"][objection_key] == answer_key["task3"][objection_key]:
            obj_score = 5
            obj_feedback = f"Correct response selected for Objection {i}."
        else:
            obj_score = 0
            obj_feedback = f"Incorrect response selected for Objection {i}."
        
        feedback[objection_key] = {
            "score": obj_score,
            "max_score": 5,
            "feedback": obj_feedback
        }
        score += obj_score
    
    return score, feedback

def evaluate_task4(submission, answer_key):
    """Evaluate Task 4: Contract Proposal"""
    score = 0
    feedback = {}
    
    # Evaluate deliverables (5 points)
    correct_deliverables = set([d.lower() for d in answer_key["task4"]["deliverables"]])
    submitted_deliverables = set([d.lower() for d in submission["task4"]["deliverables"]])
    correct_del_count = sum(1 for d in submitted_deliverables if any(d in correct_d.lower() for correct_d in correct_deliverables))
    del_score = min(5, correct_del_count * 5 / 5)  # 5 points max
    
    feedback["deliverables"] = {
        "score": del_score,
        "max_score": 5,
        "feedback": f"Included {correct_del_count}/5 deliverables that align with client requirements."
    }
    score += del_score
    
    # Evaluate timeline (5 points)
    timeline = submission["task4"]["timeline"]
    completion_date = timeline["completionDate"]
    
    if completion_date <= "2023-12-31":
        timeline_score = 5
        timeline_feedback = "Timeline meets fiscal year end requirement."
    else:
        timeline_score = 0
        timeline_feedback = "Timeline extends beyond the December 31, 2023 fiscal year end."
    
    feedback["timeline"] = {
        "score": timeline_score,
        "max_score": 5,
        "feedback": timeline_feedback
    }
    score += timeline_score
    
    # Evaluate payment structure (5 points)
    payment_structure = submission["task4"]["paymentStructure"]
    total_payment = sum(payment_structure.values())
    
    if abs(total_payment - submission["task2"]["proposedFee"]) < 0.01:
        # Check if payment structure follows the milestone code
        milestone_code = timeline["milestoneCode"]
        payment_score = 5
        payment_feedback = "Payment structure sums to proposed fee and follows milestone code."
    else:
        payment_score = 0
        payment_feedback = "Payment structure does not sum to the proposed fee."
    
    feedback["paymentStructure"] = {
        "score": payment_score,
        "max_score": 5,
        "feedback": payment_feedback
    }
    score += payment_score
    
    # Evaluate contract term code (5 points)
    if submission["task4"]["contractTermCode"] == answer_key["task4"]["contractTermCode"]:
        term_score = 5
        term_feedback = "Appropriate contract term code selected."
    else:
        # Allow for some flexibility in contract terms
        term_score = 2.5
        term_feedback = "Contract term code differs from recommended, but may be acceptable."
    
    feedback["contractTermCode"] = {
        "score": term_score,
        "max_score": 5,
        "feedback": term_feedback
    }
    score += term_score
    
    # Evaluate cancellation terms (5 points)
    if submission["task4"]["cancellationTerms"] == answer_key["task4"]["cancellationTerms"]:
        cancel_score = 5
        cancel_feedback = "Appropriate cancellation terms selected."
    else:
        # Allow for some flexibility in cancellation terms
        cancel_score = 2.5
        cancel_feedback = "Cancellation terms differ from recommended, but may be acceptable."
    
    feedback["cancellationTerms"] = {
        "score": cancel_score,
        "max_score": 5,
        "feedback": cancel_feedback
    }
    score += cancel_score
    
    return score, feedback

def check_critical_failures(submission):
    """Check for critical failures that result in automatic fail"""
    critical_failures = []
    
    # Check proposed fee
    if submission["task2"]["proposedFee"] > 75000:
        critical_failures.append("Proposed fee exceeds $75,000 budget")
    
    # Check profit margin
    if submission["task2"]["profitMargin"] < 25:
        critical_failures.append("Profit margin is below 25%")
    
    # Check timeline
    if submission["task4"]["timeline"]["completionDate"] > "2023-12-31":
        critical_failures.append("Timeline extends beyond December 31, 2023")
    
    # Check payment structure
    payment_total = sum(submission["task4"]["paymentStructure"].values())
    if abs(payment_total - submission["task2"]["proposedFee"]) > 0.01:
        critical_failures.append("Payment structure doesn't sum to the proposed fee")
    
    # Note: We can't directly check for coaching sessions from the JSON structure
    # This would require content analysis of the deliverables
    
    return critical_failures

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key"""
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "task_scores": {},
        "critical_failures": check_critical_failures(submission)
    }
    
    # Evaluate each task
    task1_score, task1_feedback = evaluate_task1(submission, answer_key)
    task2_score, task2_feedback = evaluate_task2(submission, answer_key)
    task3_score, task3_feedback = evaluate_task3(submission, answer_key)
    task4_score, task4_feedback = evaluate_task4(submission, answer_key)
    
    # Store task scores and feedback
    results["task_scores"]["task1"] = {
        "score": task1_score,
        "max_score": 25,
        "feedback": task1_feedback
    }
    
    results["task_scores"]["task2"] = {
        "score": task2_score,
        "max_score": 25,
        "feedback": task2_feedback
    }
    
    results["task_scores"]["task3"] = {
        "score": task3_score,
        "max_score": 25,
        "feedback": task3_feedback
    }
    
    results["task_scores"]["task4"] = {
        "score": task4_score,
        "max_score": 25,
        "feedback": task4_feedback
    }
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score + task4_score
    results["overall_score"] = round((total_score / 100) * 100, 2)  # Percentage
    
    # Determine pass/fail status
    if results["critical_failures"]:
        results["status"] = "FAIL"
        results["reason"] = "Critical failure(s): " + ", ".join(results["critical_failures"])
    elif results["overall_score"] >= 75:
        results["status"] = "PASS"
        results["reason"] = f"Score of {results['overall_score']}% meets or exceeds the 75% passing threshold."
    else:
        results["status"] = "FAIL"
        results["reason"] = f"Score of {results['overall_score']}% is below the 75% passing threshold."
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission"""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Status: {results['status']}")
    print(f"Reason: {results['reason']}")

if __name__ == "__main__":
    main()