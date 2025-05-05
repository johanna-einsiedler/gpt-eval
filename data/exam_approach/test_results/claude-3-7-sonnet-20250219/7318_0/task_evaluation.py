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

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Authority Identification."""
    results = {"score": 0, "max_score": 30, "details": {}}
    positions = ["CEO", "CFO", "Treasurer", "Controller", "Department_Heads"]
    
    for position in positions:
        position_results = {"score": 0, "max_score": 6, "details": {}}
        sub_pos = submission["section1_authority_identification"].get(position, {})
        key_pos = answer_key["section1_authority_identification"].get(position, {})
        
        # Check independent approval threshold
        sub_val = sub_pos.get("independent_approval_threshold", 0)
        key_val = key_pos.get("independent_approval_threshold", 0)
        if sub_val == key_val:
            position_results["details"]["independent_approval_threshold"] = {"score": 2, "max_score": 2, "correct": True}
            position_results["score"] += 2
        elif abs(sub_val - key_val) <= 0.2 * key_val:  # Within 20%
            position_results["details"]["independent_approval_threshold"] = {
                "score": 1, "max_score": 2, "correct": False, 
                "note": f"Partial credit: within 20% of correct value ({key_val})"
            }
            position_results["score"] += 1
        else:
            position_results["details"]["independent_approval_threshold"] = {
                "score": 0, "max_score": 2, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        # Check secondary approval threshold
        sub_val = sub_pos.get("secondary_approval_threshold", 0)
        key_val = key_pos.get("secondary_approval_threshold", 0)
        if sub_val == key_val:
            position_results["details"]["secondary_approval_threshold"] = {"score": 2, "max_score": 2, "correct": True}
            position_results["score"] += 2
        elif abs(sub_val - key_val) <= 0.2 * max(key_val, 1):  # Within 20%, avoid div by 0
            position_results["details"]["secondary_approval_threshold"] = {
                "score": 1, "max_score": 2, "correct": False, 
                "note": f"Partial credit: within 20% of correct value ({key_val})"
            }
            position_results["score"] += 1
        else:
            position_results["details"]["secondary_approval_threshold"] = {
                "score": 0, "max_score": 2, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        # Check board notification requirement
        sub_val = sub_pos.get("board_notification_requirement", 0)
        key_val = key_pos.get("board_notification_requirement", 0)
        if sub_val == key_val:
            position_results["details"]["board_notification_requirement"] = {"score": 2, "max_score": 2, "correct": True}
            position_results["score"] += 2
        elif abs(sub_val - key_val) <= 0.2 * max(key_val, 1):  # Within 20%, avoid div by 0
            position_results["details"]["board_notification_requirement"] = {
                "score": 1, "max_score": 2, "correct": False, 
                "note": f"Partial credit: within 20% of correct value ({key_val})"
            }
            position_results["score"] += 1
        else:
            position_results["details"]["board_notification_requirement"] = {
                "score": 0, "max_score": 2, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        results["details"][position] = position_results
        results["score"] += position_results["score"]
    
    return results

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Compliance Assessment."""
    results = {"score": 0, "max_score": 40, "details": {}}
    transactions = [
        "TX-2023-0127-A", "TX-2023-0205-B", "TX-2023-0212-C", "TX-2023-0220-D", "TX-2023-0228-E",
        "TX-2023-0305-F", "TX-2023-0312-G", "TX-2023-0318-H", "TX-2023-0325-I", "TX-2023-0330-J"
    ]
    
    for tx in transactions:
        tx_results = {"score": 0, "max_score": 4, "details": {}}
        sub_tx = submission["section2_compliance_assessment"].get(tx, {})
        key_tx = answer_key["section2_compliance_assessment"].get(tx, {})
        
        # Check properly authorized
        sub_val = sub_tx.get("properly_authorized", "")
        key_val = key_tx.get("properly_authorized", "")
        if sub_val == key_val:
            tx_results["details"]["properly_authorized"] = {"score": 1, "max_score": 1, "correct": True}
            tx_results["score"] += 1
        else:
            tx_results["details"]["properly_authorized"] = {
                "score": 0, "max_score": 1, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        # Check authority reference
        sub_val = sub_tx.get("authority_reference", "")
        key_val = key_tx.get("authority_reference", "")
        if sub_val == key_val:
            tx_results["details"]["authority_reference"] = {"score": 1, "max_score": 1, "correct": True}
            tx_results["score"] += 1
        else:
            tx_results["details"]["authority_reference"] = {
                "score": 0, "max_score": 1, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        # Check approval level required
        sub_val = sub_tx.get("approval_level_required", "")
        key_val = key_tx.get("approval_level_required", "")
        if sub_val == key_val:
            tx_results["details"]["approval_level_required"] = {"score": 2, "max_score": 2, "correct": True}
            tx_results["score"] += 2
        elif any(part.strip() in sub_val for part in key_val.split("plus")):
            # Partial credit if at least one approval level is correct
            tx_results["details"]["approval_level_required"] = {
                "score": 1, "max_score": 2, "correct": False,
                "note": f"Partial credit: partially correct approval level. Expected: {key_val}, Got: {sub_val}"
            }
            tx_results["score"] += 1
        else:
            tx_results["details"]["approval_level_required"] = {
                "score": 0, "max_score": 2, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        results["details"][tx] = tx_results
        results["score"] += tx_results["score"]
    
    return results

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Governance Gap Analysis."""
    results = {"score": 0, "max_score": 30, "details": {}}
    issues = [
        "insufficient_secondary_approval", "exceeded_authority_limits", "missing_board_notification",
        "improper_committee_authorization", "conflicting_authority_delegations", 
        "temporary_authority_not_properly_terminated", "retroactive_approval",
        "absent_quorum_for_key_decisions", "delegation_without_reporting_requirements",
        "special_project_authority_without_sunset_provision"
    ]
    
    for issue in issues:
        issue_results = {"score": 0, "max_score": 3, "details": {}}
        sub_issue = submission["section3_governance_gap_analysis"].get(issue, {})
        key_issue = answer_key["section3_governance_gap_analysis"].get(issue, {})
        
        # Check present (Yes/No)
        sub_val = sub_issue.get("present", "")
        key_val = key_issue.get("present", "")
        if sub_val == key_val:
            issue_results["details"]["present"] = {"score": 1, "max_score": 1, "correct": True}
            issue_results["score"] += 1
        else:
            issue_results["details"]["present"] = {
                "score": 0, "max_score": 1, "correct": False,
                "note": f"Incorrect value. Expected: {key_val}, Got: {sub_val}"
            }
        
        # Check reference (only if present is "Yes")
        if key_val == "Yes":
            sub_ref = sub_issue.get("reference", "")
            key_ref = key_issue.get("reference", "")
            if sub_ref == key_ref:
                issue_results["details"]["reference"] = {"score": 2, "max_score": 2, "correct": True}
                issue_results["score"] += 2
            elif sub_ref and (key_ref.split(",")[0] in sub_ref):
                # Partial credit if meeting date is correct
                issue_results["details"]["reference"] = {
                    "score": 1, "max_score": 2, "correct": False,
                    "note": f"Partial credit: partially correct reference. Expected: {key_ref}, Got: {sub_ref}"
                }
                issue_results["score"] += 1
            else:
                issue_results["details"]["reference"] = {
                    "score": 0, "max_score": 2, "correct": False,
                    "note": f"Incorrect value. Expected: {key_ref}, Got: {sub_ref}"
                }
        else:
            # If present is "No", reference should be empty
            sub_ref = sub_issue.get("reference", "")
            if sub_ref == "":
                issue_results["details"]["reference"] = {"score": 2, "max_score": 2, "correct": True}
                issue_results["score"] += 2
            else:
                issue_results["details"]["reference"] = {
                    "score": 0, "max_score": 2, "correct": False,
                    "note": "Reference should be empty when 'present' is 'No'"
                }
        
        results["details"][issue] = issue_results
        results["score"] += issue_results["score"]
    
    return results

def check_critical_elements(section_results, submission, answer_key):
    """Check if critical elements are met."""
    critical_elements = {
        "passed": True,
        "details": {}
    }
    
    # Critical Element 1: Correctly identifying at least 3 of the 5 positions' independent approval thresholds
    correct_thresholds = 0
    positions = ["CEO", "CFO", "Treasurer", "Controller", "Department_Heads"]
    for position in positions:
        sub_val = submission["section1_authority_identification"].get(position, {}).get("independent_approval_threshold", 0)
        key_val = answer_key["section1_authority_identification"].get(position, {}).get("independent_approval_threshold", 0)
        if sub_val == key_val:
            correct_thresholds += 1
    
    critical_elements["details"]["correct_approval_thresholds"] = {
        "passed": correct_thresholds >= 3,
        "note": f"Correctly identified {correct_thresholds}/5 positions' independent approval thresholds (minimum 3 required)"
    }
    if correct_thresholds < 3:
        critical_elements["passed"] = False
    
    # Critical Element 2: Correctly determining proper authorization for at least 7 of the 10 transactions
    correct_authorizations = 0
    transactions = [
        "TX-2023-0127-A", "TX-2023-0205-B", "TX-2023-0212-C", "TX-2023-0220-D", "TX-2023-0228-E",
        "TX-2023-0305-F", "TX-2023-0312-G", "TX-2023-0318-H", "TX-2023-0325-I", "TX-2023-0330-J"
    ]
    for tx in transactions:
        sub_val = submission["section2_compliance_assessment"].get(tx, {}).get("properly_authorized", "")
        key_val = answer_key["section2_compliance_assessment"].get(tx, {}).get("properly_authorized", "")
        if sub_val == key_val:
            correct_authorizations += 1
    
    critical_elements["details"]["correct_authorizations"] = {
        "passed": correct_authorizations >= 7,
        "note": f"Correctly determined proper authorization for {correct_authorizations}/10 transactions (minimum 7 required)"
    }
    if correct_authorizations < 7:
        critical_elements["passed"] = False
    
    # Critical Element 3: Correctly identifying at least 7 of the 10 governance issues as present or not present
    correct_issues = 0
    issues = [
        "insufficient_secondary_approval", "exceeded_authority_limits", "missing_board_notification",
        "improper_committee_authorization", "conflicting_authority_delegations", 
        "temporary_authority_not_properly_terminated", "retroactive_approval",
        "absent_quorum_for_key_decisions", "delegation_without_reporting_requirements",
        "special_project_authority_without_sunset_provision"
    ]
    for issue in issues:
        sub_val = submission["section3_governance_gap_analysis"].get(issue, {}).get("present", "")
        key_val = answer_key["section3_governance_gap_analysis"].get(issue, {}).get("present", "")
        if sub_val == key_val:
            correct_issues += 1
    
    critical_elements["details"]["correct_governance_issues"] = {
        "passed": correct_issues >= 7,
        "note": f"Correctly identified {correct_issues}/10 governance issues as present or not present (minimum 7 required)"
    }
    if correct_issues < 7:
        critical_elements["passed"] = False
    
    return critical_elements

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate each section
    section1_results = evaluate_section1(submission, answer_key)
    section2_results = evaluate_section2(submission, answer_key)
    section3_results = evaluate_section3(submission, answer_key)
    
    # Check critical elements
    critical_elements = check_critical_elements(
        {
            "section1": section1_results,
            "section2": section2_results,
            "section3": section3_results
        },
        submission,
        answer_key
    )
    
    # Calculate overall score
    total_score = section1_results["score"] + section2_results["score"] + section3_results["score"]
    total_possible = section1_results["max_score"] + section2_results["max_score"] + section3_results["max_score"]
    overall_percentage = (total_score / total_possible) * 100
    
    # Determine if passed based on score and critical elements
    passed = overall_percentage >= 70 and critical_elements["passed"]
    performance_level = "Excellent" if overall_percentage >= 85 else "Satisfactory" if passed else "Failed"
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passed": passed,
        "performance_level": performance_level,
        "total_points": total_score,
        "total_possible": total_possible,
        "critical_elements_passed": critical_elements["passed"],
        "critical_elements_details": critical_elements["details"],
        "section_scores": {
            "section1_authority_identification": {
                "score": section1_results["score"],
                "max_score": section1_results["max_score"],
                "percentage": round((section1_results["score"] / section1_results["max_score"]) * 100, 2)
            },
            "section2_compliance_assessment": {
                "score": section2_results["score"],
                "max_score": section2_results["max_score"],
                "percentage": round((section2_results["score"] / section2_results["max_score"]) * 100, 2)
            },
            "section3_governance_gap_analysis": {
                "score": section3_results["score"],
                "max_score": section3_results["max_score"],
                "percentage": round((section3_results["score"] / section3_results["max_score"]) * 100, 2)
            }
        },
        "detailed_results": {
            "section1_authority_identification": section1_results["details"],
            "section2_compliance_assessment": section2_results["details"],
            "section3_governance_gap_analysis": section3_results["details"]
        }
    }
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {overall_percentage:.2f}%")
    print(f"Performance Level: {performance_level}")
    print(f"Critical Elements Passed: {critical_elements['passed']}")

if __name__ == "__main__":
    main()