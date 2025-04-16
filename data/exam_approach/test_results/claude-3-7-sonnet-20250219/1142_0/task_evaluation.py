import json
import sys
import math


def load_json_file(filename):
    """Load and return JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)


def evaluate_exercise1(submission, answer_key):
    """Evaluate Exercise 1: Vendor Evaluation."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check vendor selection (15 points)
    if submission.get("selected_vendor") == answer_key.get("selected_vendor"):
        score += 15
        feedback.append("Correct vendor selection.")
    else:
        feedback.append(f"Incorrect vendor selection. Expected: {answer_key.get('selected_vendor')}")
    
    # Check total score calculation (8 points)
    submission_score = submission.get("total_score")
    answer_score = answer_key.get("total_score")
    
    if submission_score is not None and answer_score is not None:
        # Allow for slight rounding differences (within 0.05)
        if abs(float(submission_score) - float(answer_score)) <= 0.05:
            score += 8
            feedback.append("Correct total score calculation.")
        else:
            feedback.append(f"Incorrect total score. Expected: {answer_score}")
    else:
        feedback.append("Missing total score.")
    
    # Check calculation method explanation (2 points)
    if submission.get("calculation_method") and len(submission.get("calculation_method", "")) > 10:
        score += 2
        feedback.append("Appropriate calculation method explanation provided.")
    else:
        feedback.append("Missing or insufficient calculation method explanation.")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback
    }


def evaluate_exercise2(submission, answer_key):
    """Evaluate Exercise 2: Price Negotiation."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check supplier percentage differences (9 points, 3 each)
    suppliers = ["supplier_1_difference", "supplier_2_difference", "supplier_3_difference"]
    for supplier in suppliers:
        submission_diff = submission.get(supplier)
        answer_diff = answer_key.get(supplier)
        
        if submission_diff is not None and answer_diff is not None:
            # Allow for slight rounding differences (within 0.2%)
            if abs(float(submission_diff) - float(answer_diff)) <= 0.2:
                score += 3
                feedback.append(f"Correct {supplier} calculation.")
            else:
                feedback.append(f"Incorrect {supplier}. Expected: {answer_diff}")
        else:
            feedback.append(f"Missing {supplier}.")
    
    # Check highest savings supplier (5 points)
    if submission.get("highest_savings_supplier") == answer_key.get("highest_savings_supplier"):
        score += 5
        feedback.append("Correct highest savings supplier identification.")
    else:
        feedback.append(f"Incorrect highest savings supplier. Expected: {answer_key.get('highest_savings_supplier')}")
    
    # Check potential savings amount (9 points)
    submission_savings = submission.get("potential_savings_amount")
    answer_savings = answer_key.get("potential_savings_amount")
    
    if submission_savings is not None and answer_savings is not None:
        # Allow for slight rounding differences (within 1%)
        diff_percentage = abs(float(submission_savings) - float(answer_savings)) / float(answer_savings) * 100
        if diff_percentage <= 1:
            score += 9
            feedback.append("Correct potential savings calculation.")
        else:
            feedback.append(f"Incorrect potential savings. Expected: {answer_savings}")
    else:
        feedback.append("Missing potential savings amount.")
    
    # Check calculation method explanation (2 points)
    if submission.get("calculation_method") and len(submission.get("calculation_method", "")) > 10:
        score += 2
        feedback.append("Appropriate calculation method explanation provided.")
    else:
        feedback.append("Missing or insufficient calculation method explanation.")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback
    }


def evaluate_exercise3(submission, answer_key):
    """Evaluate Exercise 3: Quantity Optimization."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check optimal quantities (15 points, 5 each)
    products = ["product_a_optimal_quantity", "product_b_optimal_quantity", "product_c_optimal_quantity"]
    for product in products:
        if submission.get(product) == answer_key.get(product):
            score += 5
            feedback.append(f"Correct {product}.")
        else:
            feedback.append(f"Incorrect {product}. Expected: {answer_key.get(product)}")
    
    # Check total annual cost (8 points)
    submission_cost = submission.get("total_annual_cost")
    answer_cost = answer_key.get("total_annual_cost")
    
    if submission_cost is not None and answer_cost is not None:
        # Allow for some rounding differences (within 1%)
        diff_percentage = abs(float(submission_cost) - float(answer_cost)) / float(answer_cost) * 100
        if diff_percentage <= 1:
            score += 8
            feedback.append("Correct total annual cost calculation.")
        elif diff_percentage <= 5:  # Partial credit for close answers
            score += 4
            feedback.append(f"Total annual cost close but not exact. Expected: {answer_cost}")
        else:
            feedback.append(f"Incorrect total annual cost. Expected: {answer_cost}")
    else:
        feedback.append("Missing total annual cost.")
    
    # Check calculation method explanation (2 points)
    if submission.get("calculation_method") and len(submission.get("calculation_method", "")) > 10:
        score += 2
        feedback.append("Appropriate calculation method explanation provided.")
    else:
        feedback.append("Missing or insufficient calculation method explanation.")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback
    }


def evaluate_exercise4(submission, answer_key):
    """Evaluate Exercise 4: Purchase Requisition Processing."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check approved requisitions (15 points)
    # Allow for optimal or near-optimal solutions
    submission_reqs = set(submission.get("approved_requisitions", []))
    answer_reqs = set(answer_key.get("approved_requisitions", []))
    
    if submission_reqs == answer_reqs:
        score += 15
        feedback.append("Optimal requisition selection.")
    else:
        # Check overlap percentage
        if len(answer_reqs) > 0:
            overlap = len(submission_reqs.intersection(answer_reqs))
            overlap_percentage = (overlap / len(answer_reqs)) * 100
            
            if overlap_percentage >= 90:
                score += 13  # Near perfect
                feedback.append("Near-optimal requisition selection.")
            elif overlap_percentage >= 80:
                score += 11
                feedback.append("Good requisition selection, but not optimal.")
            elif overlap_percentage >= 70:
                score += 9
                feedback.append("Acceptable requisition selection, but not optimal.")
            elif overlap_percentage >= 60:
                score += 7
                feedback.append("Suboptimal requisition selection.")
            else:
                feedback.append("Poor requisition selection.")
        else:
            feedback.append("Could not evaluate requisition selection due to missing answer key data.")
    
    # Check total cost (4 points)
    submission_cost = submission.get("total_cost")
    answer_cost = answer_key.get("total_cost")
    budget_limit = 50000  # from the problem statement
    
    if submission_cost is not None and answer_cost is not None:
        # First check if within budget
        if float(submission_cost) > budget_limit:
            feedback.append(f"Total cost exceeds budget limit of {budget_limit}.")
        else:
            # Check accuracy
            diff_percentage = abs(float(submission_cost) - float(answer_cost)) / float(answer_cost) * 100
            if diff_percentage <= 1:
                score += 4
                feedback.append("Correct total cost calculation.")
            elif diff_percentage <= 5:
                score += 2
                feedback.append(f"Total cost close but not exact. Expected: {answer_cost}")
            else:
                feedback.append(f"Incorrect total cost. Expected: {answer_cost}")
    else:
        feedback.append("Missing total cost.")
    
    # Check total priority score (4 points)
    submission_priority = submission.get("total_priority_score")
    answer_priority = answer_key.get("total_priority_score")
    
    if submission_priority is not None and answer_priority is not None:
        if int(submission_priority) == int(answer_priority):
            score += 4
            feedback.append("Correct total priority score.")
        elif int(submission_priority) >= int(answer_priority) * 0.9:
            score += 2
            feedback.append(f"Total priority score close but not optimal. Expected: {answer_priority}")
        else:
            feedback.append(f"Suboptimal total priority score. Expected: {answer_priority}")
    else:
        feedback.append("Missing total priority score.")
    
    # Check selection strategy explanation (2 points)
    if submission.get("selection_strategy") and len(submission.get("selection_strategy", "")) > 10:
        score += 2
        feedback.append("Appropriate selection strategy explanation provided.")
    else:
        feedback.append("Missing or insufficient selection strategy explanation.")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round((score / max_score) * 100, 2),
        "feedback": feedback
    }


def evaluate_submission(submission, answer_key):
    """Evaluate the full submission against the answer key."""
    results = {}
    
    # Evaluate each exercise
    results["exercise1"] = evaluate_exercise1(submission.get("exercise1", {}), answer_key.get("exercise1", {}))
    results["exercise2"] = evaluate_exercise2(submission.get("exercise2", {}), answer_key.get("exercise2", {}))
    results["exercise3"] = evaluate_exercise3(submission.get("exercise3", {}), answer_key.get("exercise3", {}))
    results["exercise4"] = evaluate_exercise4(submission.get("exercise4", {}), answer_key.get("exercise4", {}))
    
    # Calculate overall score
    total_points = 0
    total_possible = 0
    
    for exercise, data in results.items():
        total_points += data["score"]
        total_possible += data["max_score"]
    
    # Check critical element: must score at least 15 points on Exercise 3
    critical_element_passed = results["exercise3"]["score"] >= 15
    
    # Calculate overall percentage
    overall_percentage = round((total_points / total_possible) * 100, 2) if total_possible > 0 else 0
    
    # Determine pass/fail status
    passed = overall_percentage >= 70 and critical_element_passed
    
    # Add summary to results
    results["summary"] = {
        "total_points": total_points,
        "total_possible": total_possible,
        "overall_score": overall_percentage,
        "critical_element_passed": critical_element_passed,
        "passed": passed,
        "performance_level": "Excellent" if overall_percentage >= 85 else ("Satisfactory" if passed else "Unsatisfactory")
    }
    
    return results


def main():
    # Check command line arguments
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
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['summary']['overall_score']}%")
    print(f"Result: {'PASS' if results['summary']['passed'] else 'FAIL'}")


if __name__ == "__main__":
    main()