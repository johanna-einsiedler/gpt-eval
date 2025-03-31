import json
import re
from pathlib import Path

def validate_submission(submission_path, answer_key_path):
    # Load the submission and answer key
    with open(submission_path) as f:
        submission = json.load(f)
    with open(answer_key_path) as f:
        answer_key = json.load(f)
    
    # Initialize counters and result structure
    results = {
        "detailed_results": [],
        "summary": {
            "total_products": len(answer_key["expected_answers"]),
            "correct_quantity": 0,
            "correct_reason": 0,
            "onions_correct": False
        },
        "overall_score": 0
    }
    
    # Check each expected product
    for expected in answer_key["expected_answers"]:
        product_result = {
            "product_name": expected["product_name"],
            "expected_quantity": expected["quantity_needed_lbs"],
            "submitted_quantity": None,
            "quantity_correct": False,
            "reason_correct": False,
            "reason_feedback": ""
        }
        
        # Find the corresponding submission for this product
        submitted_product = None
        for submitted in submission["products_required"]:
            if submitted["product_name"].lower() == expected["product_name"].lower():
                submitted_product = submitted
                break
        
        if submitted_product:
            product_result["submitted_quantity"] = submitted_product["quantity_needed_lbs"]
            
            # Check quantity
            if submitted_product["quantity_needed_lbs"] == expected["quantity_needed_lbs"]:
                product_result["quantity_correct"] = True
                results["summary"]["correct_quantity"] += 1
            
            # Check reason with regex
            if re.search(expected["reason_validation_regex"], submitted_product["reason"], re.IGNORECASE):
                product_result["reason_correct"] = True
                results["summary"]["correct_reason"] += 1
            else:
                product_result["reason_feedback"] = f"Reason should reference: {expected['reason_validation_regex']}"
            
            # Special check for Onions
            if expected["product_name"] == "Onions":
                results["summary"]["onions_correct"] = product_result["quantity_correct"]
        
        results["detailed_results"].append(product_result)
    
    # Calculate overall score (weighted: 70% quantity, 30% reason)
    total_possible = results["summary"]["total_products"]
    quantity_score = results["summary"]["correct_quantity"] / total_possible * 70
    reason_score = results["summary"]["correct_reason"] / total_possible * 30
    
    # Onions is critical - if wrong, cap score at 50%
    if not results["summary"]["onions_correct"]:
        overall_score = min(50, quantity_score + reason_score)
    else:
        overall_score = quantity_score + reason_score
    
    results["overall_score"] = round(overall_score, 1)
    
    return results

def main():
    # Define file paths
    submission_path = Path("test_submission.json")
    answer_key_path = Path("answer_key.json")
    results_path = Path("test_results.json")
    
    # Validate the submission
    if not submission_path.exists():
        print(f"Error: Submission file '{submission_path}' not found.")
        return
    if not answer_key_path.exists():
        print(f"Error: Answer key file '{answer_key_path}' not found.")
        return
    
    try:
        evaluation_results = validate_submission(submission_path, answer_key_path)
        
        # Save results
        with open(results_path, "w") as f:
            json.dump(evaluation_results, f, indent=2)
        
        print(f"Evaluation complete. Results saved to '{results_path}'.")
        print(f"Overall Score: {evaluation_results['overall_score']}%")
    
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")

if __name__ == "__main__":
    main()