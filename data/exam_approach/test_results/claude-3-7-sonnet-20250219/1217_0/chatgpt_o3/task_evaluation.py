#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_core_financials(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """Evaluate core financial calculations (50% of score)."""
    core_items = [
        {
            "name": "total_expenses",
            "description": "Total expenses calculation",
            "submission": submission.get("total_expenses"),
            "expected": answer_key.get("total_expenses"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "total_revenue",
            "description": "Total revenue calculation",
            "submission": submission.get("total_revenue"),
            "expected": answer_key.get("total_revenue"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "net_profit_loss",
            "description": "Net profit/loss calculation",
            "submission": submission.get("net_profit_loss"),
            "expected": answer_key.get("net_profit_loss"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "largest_expense_category",
            "description": "Largest expense category identification",
            "submission": submission.get("largest_expense_category"),
            "expected": answer_key.get("largest_expense_category"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "largest_expense_amount",
            "description": "Largest expense amount calculation",
            "submission": submission.get("largest_expense_amount"),
            "expected": answer_key.get("largest_expense_amount"),
            "correct": False,
            "points": 5,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "outstanding_payments",
            "description": "Outstanding payments identification",
            "submission": submission.get("outstanding_payments"),
            "expected": answer_key.get("outstanding_payments"),
            "correct": False,
            "points": 5,
            "earned": 0,
            "notes": ""
        }
    ]
    
    total_points = 0
    max_points = 0
    
    for item in core_items:
        max_points += item["points"]
        
        # For numerical values, allow small rounding differences
        if isinstance(item["submission"], (int, float)) and isinstance(item["expected"], (int, float)):
            if abs(item["submission"] - item["expected"]) <= 0.01:
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            else:
                item["notes"] = f"Expected {item['expected']}, got {item['submission']}"
        # For string values, case-insensitive comparison
        elif isinstance(item["submission"], str) and isinstance(item["expected"], str):
            if item["submission"].upper() == item["expected"].upper():
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            else:
                item["notes"] = f"Expected {item['expected']}, got {item['submission']}"
        # For other types, direct comparison
        elif item["submission"] == item["expected"]:
            item["correct"] = True
            item["earned"] = item["points"]
            total_points += item["points"]
        else:
            item["notes"] = f"Expected {item['expected']}, got {item['submission']}"
    
    score_percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    return score_percentage, core_items

def evaluate_error_detection(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """Evaluate error detection and resolution (30% of score)."""
    error_items = [
        {
            "name": "duplicate_transactions",
            "description": "Identification of duplicate transactions",
            "submission": submission.get("duplicate_transactions", []),
            "expected": answer_key.get("duplicate_transactions", []),
            "correct": False,
            "points": 15,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "errors_identified",
            "description": "Identification of all three intentional errors",
            "submission": submission.get("errors_identified", []),
            "expected": answer_key.get("errors_identified", []),
            "correct": False,
            "points": 15,
            "earned": 0,
            "notes": ""
        }
    ]
    
    total_points = 0
    max_points = 0
    
    for item in error_items:
        max_points += item["points"]
        
        if item["name"] == "duplicate_transactions":
            # Check if the submitted list contains the same elements as the expected list
            submitted_set = set([tx.upper() for tx in item["submission"]])
            expected_set = set([tx.upper() for tx in item["expected"]])
            
            if submitted_set == expected_set:
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            else:
                missing = expected_set - submitted_set
                extra = submitted_set - expected_set
                notes = []
                if missing:
                    notes.append(f"Missing: {', '.join(missing)}")
                if extra:
                    notes.append(f"Extra: {', '.join(extra)}")
                item["notes"] = "; ".join(notes)
        
        elif item["name"] == "errors_identified":
            # For error descriptions, check if the candidate identified all three key issues
            # This is more flexible as wording may vary
            key_issues = [
                ("duplicate venue", "venue final payment"),
                ("duplicate marketing", "marketing materials printing"),
                ("staff accommodations", "discrepancy")
            ]
            
            found_issues = 0
            missing_issues = []
            
            for issue_keywords in key_issues:
                issue_found = False
                for error_desc in item["submission"]:
                    if all(keyword.lower() in error_desc.lower() for keyword in issue_keywords):
                        issue_found = True
                        break
                
                if issue_found:
                    found_issues += 1
                else:
                    missing_issues.append(" & ".join(issue_keywords))
            
            # Partial credit based on number of issues found
            if found_issues == 3:
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            elif found_issues > 0:
                item["earned"] = (found_issues / 3) * item["points"]
                total_points += item["earned"]
                item["notes"] = f"Found {found_issues}/3 issues. Missing: {', '.join(missing_issues)}"
            else:
                item["notes"] = "No issues correctly identified"
    
    score_percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    return score_percentage, error_items

def evaluate_budget_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """Evaluate budget analysis (20% of score)."""
    budget_items = [
        {
            "name": "budget_variance_percentage",
            "description": "Budget variance percentage calculation",
            "submission": submission.get("budget_variance_percentage"),
            "expected": answer_key.get("budget_variance_percentage"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        },
        {
            "name": "most_over_budget_category",
            "description": "Identification of category closest to exceeding budget",
            "submission": submission.get("most_over_budget_category"),
            "expected": answer_key.get("most_over_budget_category"),
            "correct": False,
            "points": 10,
            "earned": 0,
            "notes": ""
        }
    ]
    
    total_points = 0
    max_points = 0
    
    for item in budget_items:
        max_points += item["points"]
        
        if item["name"] == "budget_variance_percentage":
            # Allow for small rounding differences in percentage calculation
            if abs(item["submission"] - item["expected"]) <= 0.1:
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            else:
                item["notes"] = f"Expected {item['expected']}, got {item['submission']}"
        
        elif item["name"] == "most_over_budget_category":
            # Case-insensitive comparison for category code
            if item["submission"].upper() == item["expected"].upper():
                item["correct"] = True
                item["earned"] = item["points"]
                total_points += item["points"]
            else:
                item["notes"] = f"Expected {item['expected']}, got {item['submission']}"
    
    score_percentage = (total_points / max_points) * 100 if max_points > 0 else 0
    return score_percentage, budget_items

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the candidate's submission against the answer key."""
    # Evaluate each section
    core_score, core_items = evaluate_core_financials(submission, answer_key)
    error_score, error_items = evaluate_error_detection(submission, answer_key)
    budget_score, budget_items = evaluate_budget_analysis(submission, answer_key)
    
    # Calculate weighted overall score
    overall_score = (
        (core_score * 0.5) +  # Core financials: 50%
        (error_score * 0.3) +  # Error detection: 30%
        (budget_score * 0.2)   # Budget analysis: 20%
    )
    
    # Determine if candidate passed based on criteria
    passed_core = core_score >= 80  # At least 80% on core financials
    passed_error = error_score >= 67  # At least 67% on error detection
    passed_budget = budget_score >= 67  # At least 67% on budget analysis
    passed_overall = overall_score >= 75  # Overall score of at least 75%
    
    passed = passed_core and passed_error and passed_budget and passed_overall
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "section_scores": {
            "core_financials": {
                "score": round(core_score, 2),
                "weight": 50,
                "passed": passed_core,
                "items": core_items
            },
            "error_detection": {
                "score": round(error_score, 2),
                "weight": 30,
                "passed": passed_error,
                "items": error_items
            },
            "budget_analysis": {
                "score": round(budget_score, 2),
                "weight": 20,
                "passed": passed_budget,
                "items": budget_items
            }
        },
        "passing_criteria": {
            "core_financials_minimum": 80,
            "error_detection_minimum": 67,
            "budget_analysis_minimum": 67,
            "overall_minimum": 75
        }
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_file}")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()