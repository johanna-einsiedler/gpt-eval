# task_evaluation.py

import json
import math
from pathlib import Path

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, indent=2, sort_keys=False)

def is_close(val1, val2, tolerance=0.05):
    """Check if two numerical values are close within a tolerance."""
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) <= tolerance
    return val1 == val2

def evaluate_transaction_management(submission, answer_key):
    """Evaluate the transaction record management section."""
    score = 0
    feedback = []
    
    # Check total transactions (3 points)
    if submission["transaction_summary"]["total_transactions"] == answer_key["transaction_summary"]["total_transactions"]:
        score += 3
        feedback.append("Correctly identified total number of transactions.")
    else:
        feedback.append(f"Incorrect total transactions. Expected: {answer_key['transaction_summary']['total_transactions']}, Got: {submission['transaction_summary']['total_transactions']}")
    
    # Check total purchase amount (7 points)
    if is_close(submission["transaction_summary"]["total_purchase_amount"], answer_key["transaction_summary"]["total_purchase_amount"]):
        score += 7
        feedback.append("Correctly calculated total purchase amount.")
    else:
        feedback.append(f"Incorrect total purchase amount. Expected: {answer_key['transaction_summary']['total_purchase_amount']}, Got: {submission['transaction_summary']['total_purchase_amount']}")
    
    # Check transactions with issues (5 points)
    if submission["transaction_summary"]["transactions_with_issues"] == answer_key["transaction_summary"]["transactions_with_issues"]:
        score += 5
        feedback.append("Correctly identified number of transactions with issues.")
    else:
        feedback.append(f"Incorrect number of transactions with issues. Expected: {answer_key['transaction_summary']['transactions_with_issues']}, Got: {submission['transaction_summary']['transactions_with_issues']}")
    
    # Check issue details (5 points)
    expected_issues = {issue["transaction_id"]: issue["issue_type"] for issue in answer_key["transaction_summary"]["issue_details"]}
    submitted_issues = {issue["transaction_id"]: issue["issue_type"] for issue in submission["transaction_summary"]["issue_details"]}
    
    issue_score = 0
    for transaction_id, issue_type in expected_issues.items():
        if transaction_id in submitted_issues and submitted_issues[transaction_id] == issue_type:
            issue_score += 1
    
    issue_points = min(5, round(5 * (issue_score / len(expected_issues))))
    score += issue_points
    
    if issue_points == 5:
        feedback.append("Correctly identified all transaction issues.")
    else:
        feedback.append(f"Partially identified transaction issues ({issue_score}/{len(expected_issues)}).")
    
    # Check data organization (10 points) - This is more subjective, but we'll check for presence of all required fields
    required_fields = ["total_transactions", "total_purchase_amount", "transactions_with_issues", "issue_details"]
    if all(field in submission["transaction_summary"] for field in required_fields):
        score += 10
        feedback.append("Transaction data properly organized with all required fields.")
    else:
        missing = [field for field in required_fields if field not in submission["transaction_summary"]]
        feedback.append(f"Missing required transaction fields: {', '.join(missing)}")
    
    return score, feedback

def evaluate_inventory_tracking(submission, answer_key):
    """Evaluate the inventory tracking section."""
    score = 0
    feedback = []
    
    # Check total inventory value (5 points)
    if is_close(submission["inventory_analysis"]["total_inventory_value"], answer_key["inventory_analysis"]["total_inventory_value"]):
        score += 5
        feedback.append("Correctly calculated total inventory value.")
    else:
        feedback.append(f"Incorrect total inventory value. Expected: {answer_key['inventory_analysis']['total_inventory_value']}, Got: {submission['inventory_analysis']['total_inventory_value']}")
    
    # Check product categories (15 points)
    category_score = 0
    expected_categories = answer_key["inventory_analysis"]["product_categories"]
    submitted_categories = submission["inventory_analysis"]["product_categories"]
    
    for category_name, expected_data in expected_categories.items():
        if category_name not in submitted_categories:
            feedback.append(f"Missing category: {category_name}")
            continue
            
        submitted_data = submitted_categories[category_name]
        
        # Check total quantity (1.25 points per category)
        if is_close(submitted_data["total_quantity"], expected_data["total_quantity"]):
            category_score += 1.25
        else:
            feedback.append(f"Incorrect total quantity for {category_name}. Expected: {expected_data['total_quantity']}, Got: {submitted_data['total_quantity']}")
        
        # Check average price (1.25 points per category)
        if is_close(submitted_data["average_price"], expected_data["average_price"]):
            category_score += 1.25
        else:
            feedback.append(f"Incorrect average price for {category_name}. Expected: {expected_data['average_price']}, Got: {submitted_data['average_price']}")
        
        # Check total value (1.25 points per category)
        if is_close(submitted_data["total_value"], expected_data["total_value"]):
            category_score += 1.25
        else:
            feedback.append(f"Incorrect total value for {category_name}. Expected: {expected_data['total_value']}, Got: {submitted_data['total_value']}")
    
    category_points = min(15, round(category_score))
    score += category_points
    
    if category_points == 15:
        feedback.append("Correctly calculated all category totals, averages, and values.")
    else:
        feedback.append(f"Partially correct category calculations ({category_points}/15 points).")
    
    # Check top volume products (5 points)
    expected_top_volume = set(answer_key["inventory_analysis"]["top_volume_products"])
    submitted_top_volume = set(submission["inventory_analysis"]["top_volume_products"])
    
    volume_match = len(expected_top_volume.intersection(submitted_top_volume))
    volume_points = min(5, round(5 * (volume_match / len(expected_top_volume))))
    score += volume_points
    
    if volume_points == 5:
        feedback.append("Correctly identified top products by volume.")
    else:
        feedback.append(f"Partially identified top products by volume ({volume_match}/{len(expected_top_volume)}).")
    
    # Check top cost products (5 points)
    expected_top_cost = set(answer_key["inventory_analysis"]["top_cost_products"])
    submitted_top_cost = set(submission["inventory_analysis"]["top_cost_products"])
    
    cost_match = len(expected_top_cost.intersection(submitted_top_cost))
    cost_points = min(5, round(5 * (cost_match / len(expected_top_cost))))
    score += cost_points
    
    if cost_points == 5:
        feedback.append("Correctly identified top products by cost.")
    else:
        feedback.append(f"Partially identified top products by cost ({cost_match}/{len(expected_top_cost)}).")
    
    return score, feedback

def evaluate_report_generation(submission, answer_key):
    """Evaluate the report generation section."""
    score = 0
    feedback = []
    
    # Check monthly summary (15 points)
    monthly_score = 0
    expected_months = answer_key["monthly_summary"]
    submitted_months = submission["monthly_summary"]
    
    for month_name, expected_data in expected_months.items():
        if month_name not in submitted_months:
            feedback.append(f"Missing month: {month_name}")
            continue
            
        submitted_data = submitted_months[month_name]
        
        # Check total purchases (1.67 points per month)
        if is_close(submitted_data["total_purchases"], expected_data["total_purchases"]):
            monthly_score += 1.67
        else:
            feedback.append(f"Incorrect total purchases for {month_name}. Expected: {expected_data['total_purchases']}, Got: {submitted_data['total_purchases']}")
        
        # Check largest category (1.67 points per month)
        if submitted_data["largest_category"] == expected_data["largest_category"]:
            monthly_score += 1.67
        else:
            feedback.append(f"Incorrect largest category for {month_name}. Expected: {expected_data['largest_category']}, Got: {submitted_data['largest_category']}")
        
        # Check largest category value (1.67 points per month)
        if is_close(submitted_data["largest_category_value"], expected_data["largest_category_value"]):
            monthly_score += 1.67
        else:
            feedback.append(f"Incorrect largest category value for {month_name}. Expected: {expected_data['largest_category_value']}, Got: {submitted_data['largest_category_value']}")
    
    monthly_points = min(15, round(monthly_score))
    score += monthly_points
    
    if monthly_points == 15:
        feedback.append("Correctly generated monthly summary report.")
    else:
        feedback.append(f"Partially correct monthly summary ({monthly_points}/15 points).")
    
    # Check compliance report (15 points)
    compliance_score = 0
    
    # Check regulated products total (3 points)
    if submission["compliance_report"]["regulated_products_total"] == answer_key["compliance_report"]["regulated_products_total"]:
        compliance_score += 3
        feedback.append("Correctly identified total regulated products.")
    else:
        feedback.append(f"Incorrect regulated products total. Expected: {answer_key['compliance_report']['regulated_products_total']}, Got: {submission['compliance_report']['regulated_products_total']}")
    
    # Check origin tracking complete (3 points)
    if submission["compliance_report"]["origin_tracking_complete"] == answer_key["compliance_report"]["origin_tracking_complete"]:
        compliance_score += 3
        feedback.append("Correctly assessed origin tracking completeness.")
    else:
        feedback.append(f"Incorrect origin tracking assessment. Expected: {answer_key['compliance_report']['origin_tracking_complete']}, Got: {submission['compliance_report']['origin_tracking_complete']}")
    
    # Check certification documentation complete (3 points)
    if submission["compliance_report"]["certification_documentation_complete"] == answer_key["compliance_report"]["certification_documentation_complete"]:
        compliance_score += 3
        feedback.append("Correctly assessed certification documentation completeness.")
    else:
        feedback.append(f"Incorrect certification documentation assessment. Expected: {answer_key['compliance_report']['certification_documentation_complete']}, Got: {submission['compliance_report']['certification_documentation_complete']}")
    
    # Check reporting issues (6 points)
    expected_issues = {(issue["product_code"], issue["transaction_id"]): issue["issue_type"] 
                      for issue in answer_key["compliance_report"]["reporting_issues"]}
    submitted_issues = {(issue["product_code"], issue["transaction_id"]): issue["issue_type"] 
                       for issue in submission["compliance_report"]["reporting_issues"]}
    
    issue_match = 0
    for key, issue_type in expected_issues.items():
        if key in submitted_issues and submitted_issues[key] == issue_type:
            issue_match += 1
    
    issue_points = min(6, round(6 * (issue_match / max(1, len(expected_issues)))))
    compliance_score += issue_points
    
    if issue_points == 6:
        feedback.append("Correctly identified all compliance reporting issues.")
    else:
        feedback.append(f"Partially identified compliance reporting issues ({issue_match}/{len(expected_issues)}).")
    
    compliance_points = min(15, compliance_score)
    score += compliance_points
    
    # Check JSON formatting (10 points)
    # This is a bit subjective, but we'll check for presence of all required sections
    required_sections = ["transaction_summary", "inventory_analysis", "monthly_summary", "compliance_report"]
    if all(section in submission for section in required_sections):
        score += 10
        feedback.append("JSON properly formatted with all required sections.")
    else:
        missing = [section for section in required_sections if section not in submission]
        feedback.append(f"Missing required JSON sections: {', '.join(missing)}")
    
    return score, feedback

def evaluate_submission(submission_path, answer_key_path):
    """Evaluate a candidate's submission against the answer key."""
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    if not submission or not answer_key:
        return {"error": "Failed to load submission or answer key"}
    
    # Evaluate each section
    transaction_score, transaction_feedback = evaluate_transaction_management(submission, answer_key)
    inventory_score, inventory_feedback = evaluate_inventory_tracking(submission, answer_key)
    report_score, report_feedback = evaluate_report_generation(submission, answer_key)
    
    # Calculate total score
    total_score = transaction_score + inventory_score + report_score
    max_score = 30 + 30 + 40  # Based on the evaluation criteria
    percentage_score = round((total_score / max_score) * 100, 2)
    
    # Prepare results
    results = {
        "overall_score": percentage_score,
        "passing_threshold": 70,
        "passed": percentage_score >= 70,
        "section_scores": {
            "transaction_record_management": {
                "score": transaction_score,
                "max_score": 30,
                "percentage": round((transaction_score / 30) * 100, 2),
                "feedback": transaction_feedback
            },
            "inventory_tracking": {
                "score": inventory_score,
                "max_score": 30,
                "percentage": round((inventory_score / 30) * 100, 2),
                "feedback": inventory_feedback
            },
            "report_generation": {
                "score": report_score,
                "max_score": 40,
                "percentage": round((report_score / 40) * 100, 2),
                "feedback": report_feedback
            }
        },
        "total_points": total_score,
        "max_points": max_score
    }
    
    return results

def main():
    """Main function to run the evaluation."""
    current_dir = Path.cwd()
    submission_path = current_dir / "test_submission.json"
    answer_key_path = current_dir / "answer_key.json"
    results_path = current_dir / "test_results.json"
    
    results = evaluate_submission(submission_path, answer_key_path)
    save_json_file(results, results_path)
    
    print(f"Evaluation complete. Results saved to {results_path}")
    print(f"Overall score: {results['overall_score']}%")
    if results.get("passed"):
        print("PASSED")
    else:
        print("FAILED")

if __name__ == "__main__":
    main()