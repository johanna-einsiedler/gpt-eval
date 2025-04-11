import json
import os
from decimal import Decimal, ROUND_HALF_UP

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        return None

def round_decimal(value, places=2):
    """Round a decimal value to the specified number of places."""
    if isinstance(value, (int, float)):
        value = Decimal(str(value))
    return float(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def evaluate_inventory_summary(candidate, answer_key):
    """Evaluate the inventory summary section."""
    score = 0
    details = {}
    
    # Check total_apple_inventory_kg
    candidate_apple = candidate.get("total_apple_inventory_kg", 0)
    key_apple = answer_key.get("total_apple_inventory_kg", 0)
    apple_correct = abs(candidate_apple - key_apple) <= key_apple * 0.01  # 1% margin
    if apple_correct:
        score += 1
    details["total_apple_inventory_kg"] = {
        "candidate_answer": candidate_apple,
        "correct_answer": key_apple,
        "is_correct": apple_correct
    }
    
    # Check total_corn_inventory_kg
    candidate_corn = candidate.get("total_corn_inventory_kg", 0)
    key_corn = answer_key.get("total_corn_inventory_kg", 0)
    corn_correct = abs(candidate_corn - key_corn) <= key_corn * 0.01  # 1% margin
    if corn_correct:
        score += 1
    details["total_corn_inventory_kg"] = {
        "candidate_answer": candidate_corn,
        "correct_answer": key_corn,
        "is_correct": corn_correct
    }
    
    # Check highest_inventory_product
    candidate_highest = candidate.get("highest_inventory_product", "")
    key_highest = answer_key.get("highest_inventory_product", "")
    highest_correct = candidate_highest == key_highest
    if highest_correct:
        score += 1
    details["highest_inventory_product"] = {
        "candidate_answer": candidate_highest,
        "correct_answer": key_highest,
        "is_correct": highest_correct
    }
    
    # Check lowest_inventory_product - Note: Accept CRN-03 as correct answer
    candidate_lowest = candidate.get("lowest_inventory_product", "")
    key_lowest = "CRN-03"  # Override the answer key as per the note
    lowest_correct = candidate_lowest == key_lowest
    if lowest_correct:
        score += 1
    details["lowest_inventory_product"] = {
        "candidate_answer": candidate_lowest,
        "correct_answer": key_lowest,
        "is_correct": lowest_correct
    }
    
    return score, details

def evaluate_transaction_analysis(candidate, answer_key):
    """Evaluate the transaction analysis section."""
    score = 0
    details = {}
    
    # Check total_transactions
    candidate_total = candidate.get("total_transactions", 0)
    key_total = answer_key.get("total_transactions", 0)
    total_correct = candidate_total == key_total
    if total_correct:
        score += 1
    details["total_transactions"] = {
        "candidate_answer": candidate_total,
        "correct_answer": key_total,
        "is_correct": total_correct
    }
    
    # Check highest_value_transaction_id
    candidate_highest = candidate.get("highest_value_transaction_id", "")
    key_highest = answer_key.get("highest_value_transaction_id", "")
    highest_correct = candidate_highest == key_highest
    if highest_correct:
        score += 1
    details["highest_value_transaction_id"] = {
        "candidate_answer": candidate_highest,
        "correct_answer": key_highest,
        "is_correct": highest_correct
    }
    
    # Check total_expenditure
    candidate_expenditure = round_decimal(candidate.get("total_expenditure", 0))
    key_expenditure = round_decimal(answer_key.get("total_expenditure", 0))
    expenditure_correct = abs(candidate_expenditure - key_expenditure) <= key_expenditure * 0.01  # 1% margin
    if expenditure_correct:
        score += 1
    details["total_expenditure"] = {
        "candidate_answer": candidate_expenditure,
        "correct_answer": key_expenditure,
        "is_correct": expenditure_correct
    }
    
    # Check average_transaction_value
    candidate_avg = round_decimal(candidate.get("average_transaction_value", 0))
    key_avg = round_decimal(answer_key.get("average_transaction_value", 0))
    avg_correct = abs(candidate_avg - key_avg) <= key_avg * 0.01  # 1% margin
    if avg_correct:
        score += 1
    details["average_transaction_value"] = {
        "candidate_answer": candidate_avg,
        "correct_answer": key_avg,
        "is_correct": avg_correct
    }
    
    return score, details

def evaluate_reporting_compliance(candidate, answer_key):
    """Evaluate the reporting compliance section."""
    score = 0
    details = {}
    
    # Check quarterly_report_date
    candidate_date = candidate.get("quarterly_report_date", "")
    key_date = answer_key.get("quarterly_report_date", "")
    date_correct = candidate_date == key_date
    if date_correct:
        score += 1
    details["quarterly_report_date"] = {
        "candidate_answer": candidate_date,
        "correct_answer": key_date,
        "is_correct": date_correct
    }
    
    # Check required_fields
    candidate_fields = set(candidate.get("required_fields", []))
    key_fields = set(answer_key.get("required_fields", []))
    
    # Calculate percentage of correct fields
    if len(key_fields) > 0:
        correct_fields = candidate_fields.intersection(key_fields)
        fields_percentage = len(correct_fields) / len(key_fields)
        fields_correct = fields_percentage >= 0.75  # 75% or more correct
        if fields_correct:
            score += 1
    else:
        fields_correct = False
    
    details["required_fields"] = {
        "candidate_answer": sorted(list(candidate_fields)),
        "correct_answer": sorted(list(key_fields)),
        "is_correct": fields_correct,
        "percentage_correct": round(fields_percentage * 100, 2) if 'fields_percentage' in locals() else 0
    }
    
    # Check retention_period_years
    candidate_period = candidate.get("retention_period_years", 0)
    key_period = answer_key.get("retention_period_years", 0)
    period_correct = candidate_period == key_period
    if period_correct:
        score += 1
    details["retention_period_years"] = {
        "candidate_answer": candidate_period,
        "correct_answer": key_period,
        "is_correct": period_correct
    }
    
    return score, details

def evaluate_data_verification(candidate, answer_key):
    """Evaluate the data verification section."""
    score = 0
    details = {}
    
    # Check duplicate_transaction_ids
    candidate_duplicates = set(candidate.get("duplicate_transaction_ids", []))
    key_duplicates = set(answer_key.get("duplicate_transaction_ids", []))
    duplicates_correct = candidate_duplicates == key_duplicates
    if duplicates_correct:
        score += 1
    details["duplicate_transaction_ids"] = {
        "candidate_answer": sorted(list(candidate_duplicates)),
        "correct_answer": sorted(list(key_duplicates)),
        "is_correct": duplicates_correct
    }
    
    # Check missing_data_fields
    candidate_missing = set(candidate.get("missing_data_fields", []))
    key_missing = set(answer_key.get("missing_data_fields", []))
    missing_correct = candidate_missing == key_missing
    if missing_correct:
        score += 1
    details["missing_data_fields"] = {
        "candidate_answer": sorted(list(candidate_missing)),
        "correct_answer": sorted(list(key_missing)),
        "is_correct": missing_correct
    }
    
    return score, details

def evaluate_json_format(candidate):
    """Evaluate if the JSON format is correct."""
    required_sections = [
        "inventory_summary", 
        "transaction_analysis", 
        "reporting_compliance", 
        "data_verification"
    ]
    
    # Check if all required sections are present
    for section in required_sections:
        if section not in candidate:
            return 0, {"format_correct": False, "reason": f"Missing section: {section}"}
    
    return 1, {"format_correct": True}

def evaluate_submission(candidate_data, answer_key_data):
    """Evaluate the entire submission."""
    results = {
        "candidate_id": candidate_data.get("candidate_id", "Unknown"),
        "sections": {}
    }
    
    total_score = 0
    max_score = 0
    
    # Evaluate JSON format (1 point)
    format_score, format_details = evaluate_json_format(candidate_data)
    total_score += format_score
    max_score += 1
    results["sections"]["json_format"] = {
        "score": format_score,
        "max_score": 1,
        "details": format_details
    }
    
    # Only continue evaluation if JSON format is correct
    if format_score > 0:
        # Evaluate inventory summary (4 points)
        inventory_score, inventory_details = evaluate_inventory_summary(
            candidate_data.get("inventory_summary", {}),
            answer_key_data.get("inventory_summary", {})
        )
        total_score += inventory_score
        max_score += 4
        results["sections"]["inventory_summary"] = {
            "score": inventory_score,
            "max_score": 4,
            "details": inventory_details
        }
        
        # Evaluate transaction analysis (4 points)
        transaction_score, transaction_details = evaluate_transaction_analysis(
            candidate_data.get("transaction_analysis", {}),
            answer_key_data.get("transaction_analysis", {})
        )
        total_score += transaction_score
        max_score += 4
        results["sections"]["transaction_analysis"] = {
            "score": transaction_score,
            "max_score": 4,
            "details": transaction_details
        }
        
        # Evaluate reporting compliance (3 points)
        compliance_score, compliance_details = evaluate_reporting_compliance(
            candidate_data.get("reporting_compliance", {}),
            answer_key_data.get("reporting_compliance", {})
        )
        total_score += compliance_score
        max_score += 3
        results["sections"]["reporting_compliance"] = {
            "score": compliance_score,
            "max_score": 3,
            "details": compliance_details
        }
        
        # Evaluate data verification (2 points)
        verification_score, verification_details = evaluate_data_verification(
            candidate_data.get("data_verification", {}),
            answer_key_data.get("data_verification", {})
        )
        total_score += verification_score
        max_score += 2
        results["sections"]["data_verification"] = {
            "score": verification_score,
            "max_score": 2,
            "details": verification_details
        }
    
    # Calculate overall score as a percentage
    overall_score = (total_score / max_score * 100) if max_score > 0 else 0
    results["total_score"] = total_score
    results["max_score"] = max_score
    results["overall_score"] = round(overall_score, 2)
    results["passed"] = overall_score >= 80  # 80% is passing
    
    return results

def main():
    # Load the candidate submission and answer key
    candidate_data = load_json_file("test_submission.json")
    answer_key_data = load_json_file("answer_key.json")
    
    if not candidate_data or not answer_key_data:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(candidate_data, answer_key_data)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to 'test_results.json'.")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()