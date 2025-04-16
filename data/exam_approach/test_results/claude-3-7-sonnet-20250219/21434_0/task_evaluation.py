#!/usr/bin/env python3
"""
Task Evaluation Script for Claims File Maintenance Exam

This script evaluates a candidate's submission against an answer key and
generates a detailed assessment report.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
import os


def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not valid JSON.")
        sys.exit(1)


def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Settled Claims Record Management (35% of total)."""
    results = {
        "points_earned": 0,
        "max_points": 35,
        "details": {
            "settlement_codes": {"correct": 0, "total": 5, "errors": []},
            "document_locations": {"correct": 0, "total": 5, "errors": []},
            "quarterly_report": {"correct": 0, "total": 7, "errors": []}
        }
    }
    
    # Check settlement codes and document locations (15 points total)
    submission_claims = {claim["claim_number"]: claim for claim in submission["task_1"]["settled_claims"]}
    answer_claims = {claim["claim_number"]: claim for claim in answer_key["task_1"]["settled_claims"]}
    
    for claim_number, answer_claim in answer_claims.items():
        if claim_number in submission_claims:
            sub_claim = submission_claims[claim_number]
            
            # Check settlement code (10 points / 5 claims = 2 points each)
            if sub_claim["settlement_code"] == answer_claim["settlement_code"]:
                results["details"]["settlement_codes"]["correct"] += 1
                results["points_earned"] += 2
            else:
                results["details"]["settlement_codes"]["errors"].append({
                    "claim": claim_number,
                    "submitted": sub_claim["settlement_code"],
                    "expected": answer_claim["settlement_code"]
                })
            
            # Check document location (5 points / 5 claims = 1 point each)
            if sub_claim["document_location"] == answer_claim["document_location"]:
                results["details"]["document_locations"]["correct"] += 1
                results["points_earned"] += 1
            else:
                results["details"]["document_locations"]["errors"].append({
                    "claim": claim_number,
                    "submitted": sub_claim["document_location"],
                    "expected": answer_claim["document_location"]
                })
    
    # Check quarterly report (20 points)
    sub_report = submission["task_1"]["quarterly_report"]
    ans_report = answer_key["task_1"]["quarterly_report"]
    
    # Total claims (3 points)
    if sub_report["total_claims_settled"] == ans_report["total_claims_settled"]:
        results["details"]["quarterly_report"]["correct"] += 1
        results["points_earned"] += 3
    else:
        results["details"]["quarterly_report"]["errors"].append({
            "field": "total_claims_settled",
            "submitted": sub_report["total_claims_settled"],
            "expected": ans_report["total_claims_settled"]
        })
    
    # Total settlement amount (3 points)
    if sub_report["total_settlement_amount"] == ans_report["total_settlement_amount"]:
        results["details"]["quarterly_report"]["correct"] += 1
        results["points_earned"] += 3
    else:
        # Allow ±5% tolerance
        try:
            sub_amount = float(sub_report["total_settlement_amount"])
            ans_amount = float(ans_report["total_settlement_amount"])
            if abs(sub_amount - ans_amount) / ans_amount <= 0.05:
                results["details"]["quarterly_report"]["correct"] += 1
                results["points_earned"] += 1.5  # Partial credit
            else:
                results["details"]["quarterly_report"]["errors"].append({
                    "field": "total_settlement_amount",
                    "submitted": sub_report["total_settlement_amount"],
                    "expected": ans_report["total_settlement_amount"],
                    "note": "Outside ±5% tolerance"
                })
        except (ValueError, TypeError):
            results["details"]["quarterly_report"]["errors"].append({
                "field": "total_settlement_amount",
                "submitted": sub_report["total_settlement_amount"],
                "expected": ans_report["total_settlement_amount"],
                "note": "Invalid format"
            })
    
    # Average settlement amount (3 points)
    if sub_report["average_settlement_amount"] == ans_report["average_settlement_amount"]:
        results["details"]["quarterly_report"]["correct"] += 1
        results["points_earned"] += 3
    else:
        # Allow ±5% tolerance
        try:
            sub_avg = float(sub_report["average_settlement_amount"])
            ans_avg = float(ans_report["average_settlement_amount"])
            if abs(sub_avg - ans_avg) / ans_avg <= 0.05:
                results["details"]["quarterly_report"]["correct"] += 1
                results["points_earned"] += 1.5  # Partial credit
            else:
                results["details"]["quarterly_report"]["errors"].append({
                    "field": "average_settlement_amount",
                    "submitted": sub_report["average_settlement_amount"],
                    "expected": ans_report["average_settlement_amount"],
                    "note": "Outside ±5% tolerance"
                })
        except (ValueError, TypeError):
            results["details"]["quarterly_report"]["errors"].append({
                "field": "average_settlement_amount",
                "submitted": sub_report["average_settlement_amount"],
                "expected": ans_report["average_settlement_amount"],
                "note": "Invalid format"
            })
    
    # Claims by type (8 points)
    claim_types = {"STL-AC", "STL-BI", "STL-FP", "STL-TH", "STL-WD"}
    correct_types = 0
    
    for claim_type in claim_types:
        if sub_report["claims_by_type"].get(claim_type) == ans_report["claims_by_type"].get(claim_type):
            correct_types += 1
        else:
            results["details"]["quarterly_report"]["errors"].append({
                "field": f"claims_by_type.{claim_type}",
                "submitted": sub_report["claims_by_type"].get(claim_type),
                "expected": ans_report["claims_by_type"].get(claim_type)
            })
    
    # 8 points split across 5 types (1.6 points each)
    results["points_earned"] += (correct_types * 1.6)
    results["details"]["quarterly_report"]["correct"] += correct_types
    
    # Check for critical failures
    results["critical_failures"] = []
    
    # Settlement codes incorrect for more than 2 claims
    if results["details"]["settlement_codes"]["correct"] < 3:
        results["critical_failures"].append("Settlement codes incorrect for more than 2 claims")
    
    return results


def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Claims Inventory Management (35% of total)."""
    results = {
        "points_earned": 0,
        "max_points": 35,
        "details": {
            "claims_identification": {"correct": 0, "total": 9, "errors": []},
            "priority_assignment": {"correct": 0, "total": 9, "errors": []},
            "priority_counts": {"correct": 0, "total": 4, "errors": []}
        }
    }
    
    # Identify claims requiring analysis (15 points)
    sub_claims = {claim["claim_number"]: claim for claim in submission["task_2"]["claims_requiring_analysis"]}
    answer_claims = {claim["claim_number"]: claim for claim in answer_key["task_2"]["claims_requiring_analysis"]}
    
    # Check which claims were correctly identified (15 points / 9 claims ≈ 1.67 points each)
    for claim_number in answer_claims:
        if claim_number in sub_claims:
            results["details"]["claims_identification"]["correct"] += 1
            results["points_earned"] += (15 / 9)  # 1.67 points per correct claim identified
        else:
            results["details"]["claims_identification"]["errors"].append({
                "claim": claim_number,
                "error": "Claim requiring analysis not identified"
            })
    
    # Check for false positives (claims incorrectly identified as requiring analysis)
    for claim_number in sub_claims:
        if claim_number not in answer_claims:
            results["details"]["claims_identification"]["errors"].append({
                "claim": claim_number,
                "error": "Claim incorrectly identified as requiring analysis"
            })
    
    # Check priority assignments (10 points / 9 claims ≈ 1.11 points each)
    for claim_number, answer_claim in answer_claims.items():
        if claim_number in sub_claims:
            sub_claim = sub_claims[claim_number]
            if sub_claim["analysis_priority"] == answer_claim["analysis_priority"]:
                results["details"]["priority_assignment"]["correct"] += 1
                results["points_earned"] += (10 / 9)  # 1.11 points per correct priority
            else:
                results["details"]["priority_assignment"]["errors"].append({
                    "claim": claim_number,
                    "submitted": sub_claim["analysis_priority"],
                    "expected": answer_claim["analysis_priority"]
                })
    
    # Check priority counts (10 points / 4 priority levels = 2.5 points each)
    for priority_level in ["priority_1", "priority_2", "priority_3", "priority_4"]:
        if submission["task_2"]["priority_counts"][priority_level] == answer_key["task_2"]["priority_counts"][priority_level]:
            results["details"]["priority_counts"]["correct"] += 1
            results["points_earned"] += 2.5
        else:
            results["details"]["priority_counts"]["errors"].append({
                "level": priority_level,
                "submitted": submission["task_2"]["priority_counts"][priority_level],
                "expected": answer_key["task_2"]["priority_counts"][priority_level]
            })
    
    # Check for critical failures
    results["critical_failures"] = []
    
    # Failure to identify any Priority 1 claims
    priority_1_claims_identified = False
    for claim in submission["task_2"]["claims_requiring_analysis"]:
        if claim["analysis_priority"] == "1":
            priority_1_claims_identified = True
            break
    
    if not priority_1_claims_identified and answer_key["task_2"]["priority_counts"]["priority_1"] != "0":
        results["critical_failures"].append("Failure to identify any Priority 1 claims requiring immediate attention")
    
    return results


def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Claim File Audit and Remediation (30% of total)."""
    results = {
        "points_earned": 0,
        "max_points": 30,
        "details": {
            "file_status": {"correct": 0, "total": 5, "errors": []},
            "deficiency_identification": {"correct": 0, "total": 11, "errors": []},
            "remediation_required": {"correct": 0, "total": 5, "errors": []},
            "summary_statistics": {"correct": 0, "total": 5, "errors": []}
        }
    }
    
    # Check file status (10 points / 5 files = 2 points each)
    sub_audit = {result["claim_number"]: result for result in submission["task_3"]["audit_results"]}
    answer_audit = {result["claim_number"]: result for result in answer_key["task_3"]["audit_results"]}
    
    for claim_number, answer_result in answer_audit.items():
        if claim_number in sub_audit:
            sub_result = sub_audit[claim_number]
            
            # Check file status
            if sub_result["file_status"] == answer_result["file_status"]:
                results["details"]["file_status"]["correct"] += 1
                results["points_earned"] += 2
            else:
                results["details"]["file_status"]["errors"].append({
                    "claim": claim_number,
                    "submitted": sub_result["file_status"],
                    "expected": answer_result["file_status"]
                })
            
            # Check remediation required (5 points / 5 files = 1 point each)
            if sub_result["remediation_required"] == answer_result["remediation_required"]:
                results["details"]["remediation_required"]["correct"] += 1
                results["points_earned"] += 1
            else:
                results["details"]["remediation_required"]["errors"].append({
                    "claim": claim_number,
                    "submitted": sub_result["remediation_required"],
                    "expected": answer_result["remediation_required"]
                })
            
            # Check deficiency identification (total 11 deficiencies, 10 points total ≈ 0.91 points each)
            # First count how many correct deficiencies were identified
            sub_deficiencies = set(sub_result["deficiency_codes"])
            answer_deficiencies = set(answer_result["deficiency_codes"])
            
            correct_deficiencies = len(sub_deficiencies & answer_deficiencies)
            false_positives = sub_deficiencies - answer_deficiencies
            false_negatives = answer_deficiencies - sub_deficiencies
            
            # Track correct/incorrect deficiencies for this file
            results["details"]["deficiency_identification"]["correct"] += correct_deficiencies
            
            if false_positives:
                results["details"]["deficiency_identification"]["errors"].append({
                    "claim": claim_number,
                    "error": "False positive deficiencies",
                    "codes": list(false_positives)
                })
                
            if false_negatives:
                results["details"]["deficiency_identification"]["errors"].append({
                    "claim": claim_number,
                    "error": "Missed deficiencies",
                    "codes": list(false_negatives)
                })
    
    # Award points for correctly identified deficiencies
    total_deficiencies = int(answer_key["task_3"]["summary_statistics"]["total_deficiencies_found"])
    results["points_earned"] += (results["details"]["deficiency_identification"]["correct"] / total_deficiencies) * 10
    
    # Check summary statistics (5 points for all 5 statistics ≈ 1 point each)
    for stat in ["files_complete", "files_with_minor_deficiencies", 
                "files_with_major_deficiencies", "files_with_critical_deficiencies", 
                "total_deficiencies_found"]:
        if submission["task_3"]["summary_statistics"][stat] == answer_key["task_3"]["summary_statistics"][stat]:
            results["details"]["summary_statistics"]["correct"] += 1
            results["points_earned"] += 1
        else:
            results["details"]["summary_statistics"]["errors"].append({
                "statistic": stat,
                "submitted": submission["task_3"]["summary_statistics"][stat],
                "expected": answer_key["task_3"]["summary_statistics"][stat]
            })
    
    # Check for critical failures
    results["critical_failures"] = []
    
    # Identifying a complete claim file as having deficiencies (false positives)
    for claim_number in ["AUD-2023-002", "AUD-2023-004"]:  # These are the complete files
        if claim_number in sub_audit:
            sub_result = sub_audit[claim_number]
            if sub_result["file_status"] != "Complete" or len(sub_result["deficiency_codes"]) > 0:
                results["critical_failures"].append(f"Identified a complete claim file ({claim_number}) as having deficiencies")
    
    return results


def check_format_errors(submission):
    """Check for structural errors in the submission format."""
    format_errors = []
    
    required_top_keys = ["candidate_id", "task_1", "task_2", "task_3"]
    for key in required_top_keys:
        if key not in submission:
            format_errors.append(f"Missing required top-level key: {key}")
    
    if "task_1" in submission:
        task1 = submission["task_1"]
        if "settled_claims" not in task1:
            format_errors.append("Missing task_1.settled_claims")
        elif not isinstance(task1["settled_claims"], list):
            format_errors.append("task_1.settled_claims must be a list")
        
        if "quarterly_report" not in task1:
            format_errors.append("Missing task_1.quarterly_report")
    
    if "task_2" in submission:
        task2 = submission["task_2"]
        if "claims_requiring_analysis" not in task2:
            format_errors.append("Missing task_2.claims_requiring_analysis")
        elif not isinstance(task2["claims_requiring_analysis"], list):
            format_errors.append("task_2.claims_requiring_analysis must be a list")
        
        if "priority_counts" not in task2:
            format_errors.append("Missing task_2.priority_counts")
    
    if "task_3" in submission:
        task3 = submission["task_3"]
        if "audit_results" not in task3:
            format_errors.append("Missing task_3.audit_results")
        elif not isinstance(task3["audit_results"], list):
            format_errors.append("task_3.audit_results must be a list")
        
        if "summary_statistics" not in task3:
            format_errors.append("Missing task_3.summary_statistics")
    
    return format_errors


def main():
    """Main function to evaluate the candidate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Check for format errors
    format_errors = check_format_errors(submission)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission, answer_key)
    task2_results = evaluate_task2(submission, answer_key)
    task3_results = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    max_total = task1_results["max_points"] + task2_results["max_points"] + task3_results["max_points"]
    earned_total = task1_results["points_earned"] + task2_results["points_earned"] + task3_results["points_earned"]
    overall_percentage = (earned_total / max_total) * 100 if max_total > 0 else 0
    
    # Check for minimum requirements
    passed_minimums = (
        task1_results["points_earned"] >= 24 and  # Min 24/35 for Task 1
        task2_results["points_earned"] >= 24 and  # Min 24/35 for Task 2
        task3_results["points_earned"] >= 21      # Min 21/30 for Task 3
    )
    
    # Compile all critical failures
    all_critical_failures = (
        format_errors +
        task1_results.get("critical_failures", []) +
        task2_results.get("critical_failures", []) +
        task3_results.get("critical_failures", [])
    )
    
    # Determine if the candidate passed
    passed = (overall_percentage >= 70 and 
              passed_minimums and 
              not all_critical_failures)
    
    # Create the results object
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passed": passed,
        "task_1": task1_results,
        "task_2": task2_results,
        "task_3": task3_results,
        "format_errors": format_errors,
        "critical_failures": all_critical_failures,
        "minimum_requirements_met": passed_minimums
    }
    
    # Write the results to a file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")


if __name__ == "__main__":
    main()