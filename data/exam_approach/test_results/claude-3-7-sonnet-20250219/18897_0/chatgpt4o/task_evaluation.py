#!/usr/bin/env python3
import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_financial_impact(submission, answer_key):
    """Evaluate the financial impact section (30 points)."""
    score = 0
    details = {}
    
    # Wage increase total cost (10 points)
    correct = answer_key["wage_increase_total_cost"]
    submitted = submission["wage_increase_total_cost"]
    percent_diff = abs(submitted - correct) / correct * 100
    
    if percent_diff <= 5:
        wage_score = 10
    elif percent_diff <= 10:
        wage_score = 5
    else:
        wage_score = 0
    
    score += wage_score
    details["wage_increase_total_cost"] = {
        "submitted": submitted,
        "correct": correct,
        "percent_diff": percent_diff,
        "points_earned": wage_score,
        "points_possible": 10
    }
    
    # Benefit cost percentage increase (10 points)
    correct = answer_key["benefit_cost_percentage_increase"]
    submitted = submission["benefit_cost_percentage_increase"]
    abs_diff = abs(submitted - correct)
    
    if abs_diff <= 2:
        benefit_score = 10
    elif abs_diff <= 4:
        benefit_score = 5
    else:
        benefit_score = 0
    
    score += benefit_score
    details["benefit_cost_percentage_increase"] = {
        "submitted": submitted,
        "correct": correct,
        "absolute_diff": abs_diff,
        "points_earned": benefit_score,
        "points_possible": 10
    }
    
    # Per-unit cost impact (10 points)
    correct = answer_key["per_unit_cost_impact"]
    submitted = submission["per_unit_cost_impact"]
    abs_diff = abs(submitted - correct)
    
    if abs_diff <= 0.1:
        unit_score = 10
    elif abs_diff <= 0.2:
        unit_score = 5
    else:
        unit_score = 0
    
    score += unit_score
    details["per_unit_cost_impact"] = {
        "submitted": submitted,
        "correct": correct,
        "absolute_diff": abs_diff,
        "points_earned": unit_score,
        "points_possible": 10
    }
    
    return {
        "score": score,
        "possible": 30,
        "details": details
    }

def evaluate_operational_impact(submission, answer_key):
    """Evaluate the operational impact section (15 points)."""
    score = 0
    details = {}
    
    for rule in ["work_rule_1", "work_rule_2", "work_rule_3"]:
        correct = answer_key[rule]
        submitted = submission[rule]
        rule_score = 5 if submitted == correct else 0
        score += rule_score
        
        details[rule] = {
            "submitted": submitted,
            "correct": correct,
            "points_earned": rule_score,
            "points_possible": 5
        }
    
    return {
        "score": score,
        "possible": 15,
        "details": details
    }

def evaluate_compliance_precedent(submission, answer_key):
    """Evaluate the compliance and precedent section (30 points)."""
    score = 0
    details = {}
    
    for item in range(1, 11):
        item_key = f"proposal_item_{item}"
        
        # Precedent concern (1.5 points each)
        correct_precedent = answer_key[item_key]["precedent_concern"]
        submitted_precedent = submission[item_key]["precedent_concern"]
        precedent_score = 1.5 if submitted_precedent == correct_precedent else 0
        score += precedent_score
        
        # Compliance issue (1.5 points each)
        correct_compliance = answer_key[item_key]["compliance_issue"]
        submitted_compliance = submission[item_key]["compliance_issue"]
        compliance_score = 1.5 if submitted_compliance == correct_compliance else 0
        score += compliance_score
        
        details[item_key] = {
            "precedent_concern": {
                "submitted": submitted_precedent,
                "correct": correct_precedent,
                "points_earned": precedent_score,
                "points_possible": 1.5
            },
            "compliance_issue": {
                "submitted": submitted_compliance,
                "correct": correct_compliance,
                "points_earned": compliance_score,
                "points_possible": 1.5
            }
        }
    
    return {
        "score": score,
        "possible": 30,
        "details": details
    }

def evaluate_impact_ranking(submission, answer_key):
    """Evaluate the impact ranking section (25 points)."""
    correct_positions = {}
    submitted_positions = {}
    
    for item in range(1, 11):
        item_key = f"proposal_item_{item}"
        correct_positions[item_key] = answer_key[item_key]
        submitted_positions[item_key] = submission[item_key]
    
    # Count items within ±1 position of correct ranking
    items_within_range = 0
    details = {}
    
    for item_key, correct_rank in correct_positions.items():
        submitted_rank = submitted_positions[item_key]
        within_range = abs(submitted_rank - correct_rank) <= 1
        if within_range:
            items_within_range += 1
        
        details[item_key] = {
            "submitted": submitted_rank,
            "correct": correct_rank,
            "within_range": within_range
        }
    
    # Determine score based on items within range
    if items_within_range == 10:
        score = 25
    elif items_within_range >= 8:
        score = 20
    elif items_within_range >= 6:
        score = 15
    elif items_within_range >= 4:
        score = 10
    elif items_within_range >= 2:
        score = 5
    else:
        score = 0
    
    return {
        "score": score,
        "possible": 25,
        "items_within_range": items_within_range,
        "details": details
    }

def check_critical_elements(submission, answer_key, financial_results):
    """Check if candidate meets critical elements requirements."""
    critical_elements = {
        "most_severe_impact": submission["impact_ranking"]["proposal_item_10"] == 1,
        "financial_impact": financial_results["score"] >= 15,  # At least 50% of financial section
        "compliance_issues": False
    }
    
    # Check if at least one compliance issue is correctly identified
    for item in range(1, 11):
        item_key = f"proposal_item_{item}"
        if (answer_key["compliance_precedent"][item_key]["compliance_issue"] and 
            submission["compliance_precedent"][item_key]["compliance_issue"]):
            critical_elements["compliance_issues"] = True
            break
    
    return critical_elements

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load submission and answer key
    submission_data = load_json_file(submission_file)
    answer_key_data = load_json_file(answer_key_file)
    
    # Extract relevant sections
    submission = {
        "financial_impact": submission_data["financial_impact"],
        "operational_impact": submission_data["operational_impact"],
        "compliance_precedent": submission_data["compliance_precedent"],
        "impact_ranking": submission_data["impact_ranking"]
    }
    
    answer_key = {
        "financial_impact": answer_key_data["financial_impact"],
        "operational_impact": answer_key_data["operational_impact"],
        "compliance_precedent": answer_key_data["compliance_precedent"],
        "impact_ranking": answer_key_data["impact_ranking"]
    }
    
    # Evaluate each section
    financial_results = evaluate_financial_impact(
        submission["financial_impact"], 
        answer_key["financial_impact"]
    )
    
    operational_results = evaluate_operational_impact(
        submission["operational_impact"], 
        answer_key["operational_impact"]
    )
    
    compliance_results = evaluate_compliance_precedent(
        submission["compliance_precedent"], 
        answer_key["compliance_precedent"]
    )
    
    ranking_results = evaluate_impact_ranking(
        submission["impact_ranking"], 
        answer_key["impact_ranking"]
    )
    
    # Calculate total score
    total_score = (
        financial_results["score"] + 
        operational_results["score"] + 
        compliance_results["score"] + 
        ranking_results["score"]
    )
    total_possible = 100
    
    # Check critical elements
    critical_elements = check_critical_elements(
        submission_data, 
        answer_key_data, 
        financial_results
    )
    
    # Determine if candidate passed
    passed_score = total_score >= 70
    passed_critical = all(critical_elements.values())
    passed = passed_score and passed_critical
    
    # Calculate overall percentage
    overall_score = (total_score / total_possible) * 100
    
    # Prepare results
    results = {
        "candidate_id": submission_data.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "total_points": total_score,
        "possible_points": total_possible,
        "passed": passed,
        "sections": {
            "financial_impact": financial_results,
            "operational_impact": operational_results,
            "compliance_precedent": compliance_results,
            "impact_ranking": ranking_results
        },
        "critical_elements": critical_elements,
        "passed_score_threshold": passed_score,
        "passed_critical_elements": passed_critical
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_score:.2f}%")
    print(f"Pass status: {'PASSED' if passed else 'FAILED'}")

if __name__ == "__main__":
    main()