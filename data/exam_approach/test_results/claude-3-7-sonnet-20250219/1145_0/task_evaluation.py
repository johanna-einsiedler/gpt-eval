import json
import re
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def validate_reasonable_price(price, exercise="exercise1"):
    """Validate if the price is within acceptable range."""
    if exercise == "exercise1":
        return 1480.00 <= price <= 1500.00
    elif exercise == "exercise4":
        return 90.10 <= price <= 93.50
    return False

def validate_discrepancies(discrepancies):
    """Validate that all required discrepancies are identified."""
    required_items = [
        "Manufacturing Overhead", "R&D Allocation", "Packaging", 
        "Shipping & Handling", "Administrative Costs", "Profit Margin", 
        "Certification Fees", "Documentation"
    ]
    
    # Check if all required items are included (case-insensitive)
    for item in required_items:
        if not any(item.lower() in d.lower() for d in discrepancies):
            return False
    return True

def validate_justifications(acceptable, unacceptable):
    """Validate the classification of price justifications."""
    correct_acceptable = [
        "1", "2", "3", "4", "8"
    ]
    
    correct_unacceptable = [
        "5", "6", "7"
    ]
    
    # Extract numbers from justifications
    acceptable_nums = []
    for item in acceptable:
        match = re.search(r'(\d+)', item)
        if match:
            acceptable_nums.append(match.group(1))
    
    unacceptable_nums = []
    for item in unacceptable:
        match = re.search(r'(\d+)', item)
        if match:
            unacceptable_nums.append(match.group(1))
    
    # Check if all correct items are included
    acceptable_correct = all(num in acceptable_nums for num in correct_acceptable)
    unacceptable_correct = all(num in unacceptable_nums for num in correct_unacceptable)
    
    return acceptable_correct and unacceptable_correct

def count_key_elements(text, key_elements):
    """Count how many key elements are mentioned in the text."""
    count = 0
    for element in key_elements:
        if element.lower() in text.lower():
            count += 1
    return count

def evaluate_exercise1(submission, answer_key):
    """Evaluate Exercise 1: Historical Price Analysis."""
    results = {
        "reasonable_price": {
            "score": 0,
            "max_points": 10,
            "feedback": ""
        },
        "price_trend_analysis": {
            "score": 0,
            "max_points": 8,
            "feedback": ""
        },
        "recommendation": {
            "score": 0,
            "max_points": 7,
            "feedback": ""
        },
        "total_score": 0,
        "max_points": 25
    }
    
    # Evaluate reasonable price
    price = submission.get("reasonable_price", 0)
    if validate_reasonable_price(price):
        results["reasonable_price"]["score"] = 10
        results["reasonable_price"]["feedback"] = "Correct price within acceptable range."
    else:
        # Partial credit based on how close they are to the acceptable range
        if 1470 <= price <= 1510:
            results["reasonable_price"]["score"] = 5
            results["reasonable_price"]["feedback"] = "Price is close to acceptable range but not optimal."
        else:
            results["reasonable_price"]["score"] = 0
            results["reasonable_price"]["feedback"] = "Price is outside acceptable range."
    
    # Evaluate price trend analysis
    analysis = submission.get("price_trend_analysis", "")
    key_elements = [
        "upward trend", 
        "market index", 
        "purchase volume", 
        "seasonal pattern", 
        "material shortage"
    ]
    
    element_count = count_key_elements(analysis, key_elements)
    results["price_trend_analysis"]["score"] = min(8, element_count * 1.6)
    results["price_trend_analysis"]["feedback"] = f"Analysis includes {element_count} of 5 key elements."
    
    # Evaluate recommendation
    recommendation = submission.get("recommendation", "")
    key_elements = [
        "target price", 
        "justification", 
        "negotiation", 
        "price guarantee", 
        "timing"
    ]
    
    element_count = count_key_elements(recommendation, key_elements)
    results["recommendation"]["score"] = min(7, element_count * 1.4)
    results["recommendation"]["feedback"] = f"Recommendation includes {element_count} of 5 key elements."
    
    # Calculate total score
    results["total_score"] = (
        results["reasonable_price"]["score"] + 
        results["price_trend_analysis"]["score"] + 
        results["recommendation"]["score"]
    )
    
    return results

def evaluate_exercise2(submission, answer_key):
    """Evaluate Exercise 2: Supplier Proposal Evaluation."""
    results = {
        "recommended_supplier": {
            "score": 0,
            "max_points": 10,
            "feedback": ""
        },
        "ranking": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "justification": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "potential_savings": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "total_score": 0,
        "max_points": 25
    }
    
    # Evaluate recommended supplier
    recommended = submission.get("recommended_supplier", "")
    justification = submission.get("justification", "")
    
    if recommended == "Budget Office Supply":
        results["recommended_supplier"]["score"] = 10
        results["recommended_supplier"]["feedback"] = "Correct supplier recommendation."
    elif recommended == "Office Solutions Inc." and ("quality" in justification.lower() and "delivery" in justification.lower()):
        results["recommended_supplier"]["score"] = 8
        results["recommended_supplier"]["feedback"] = "Alternative supplier with adequate justification."
    else:
        results["recommended_supplier"]["score"] = 0
        results["recommended_supplier"]["feedback"] = "Incorrect supplier recommendation."
    
    # Evaluate ranking
    ranking = submission.get("ranking", [])
    correct_ranking = ["Budget Office Supply", "Office Solutions Inc.", "Furniture Plus", "Premium Furnishings"]
    
    if ranking == correct_ranking:
        results["ranking"]["score"] = 5
        results["ranking"]["feedback"] = "Correct ranking of suppliers."
    else:
        # Check how many positions are correct
        correct_positions = sum(1 for i, supplier in enumerate(ranking) if i < len(correct_ranking) and supplier == correct_ranking[i])
        results["ranking"]["score"] = correct_positions
        results["ranking"]["feedback"] = f"{correct_positions} of 4 suppliers ranked correctly."
    
    # Evaluate justification
    key_elements = ["price", "quality", "delivery", "warranty", "savings"]
    element_count = count_key_elements(justification, key_elements)
    results["justification"]["score"] = min(5, element_count)
    results["justification"]["feedback"] = f"Justification includes {element_count} of 5 key elements."
    
    # Evaluate potential savings
    savings = submission.get("potential_savings", 0)
    if recommended == "Budget Office Supply" and abs(savings - 6500.00) < 0.01:
        results["potential_savings"]["score"] = 5
        results["potential_savings"]["feedback"] = "Correct savings calculation."
    elif recommended == "Office Solutions Inc." and abs(savings - 4000.00) < 0.01:
        results["potential_savings"]["score"] = 5
        results["potential_savings"]["feedback"] = "Correct savings calculation for alternative supplier."
    else:
        results["potential_savings"]["score"] = 0
        results["potential_savings"]["feedback"] = "Incorrect savings calculation."
    
    # Calculate total score
    results["total_score"] = (
        results["recommended_supplier"]["score"] + 
        results["ranking"]["score"] + 
        results["justification"]["score"] + 
        results["potential_savings"]["score"]
    )
    
    return results

def evaluate_exercise3(submission, answer_key):
    """Evaluate Exercise 3: Cost Breakdown Analysis."""
    results = {
        "identified_discrepancies": {
            "score": 0,
            "max_points": 8,
            "feedback": ""
        },
        "total_overcharge": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "corrected_total_price": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "negotiation_points": {
            "score": 0,
            "max_points": 7,
            "feedback": ""
        },
        "total_score": 0,
        "max_points": 25
    }
    
    # Evaluate identified discrepancies
    discrepancies = submission.get("identified_discrepancies", [])
    if validate_discrepancies(discrepancies):
        results["identified_discrepancies"]["score"] = 8
        results["identified_discrepancies"]["feedback"] = "All discrepancies correctly identified."
    else:
        # Count how many of the required discrepancies are included
        required_items = [
            "Manufacturing Overhead", "R&D Allocation", "Packaging", 
            "Shipping & Handling", "Administrative Costs", "Profit Margin", 
            "Certification Fees", "Documentation"
        ]
        
        count = 0
        for item in required_items:
            if any(item.lower() in d.lower() for d in discrepancies):
                count += 1
        
        results["identified_discrepancies"]["score"] = count
        results["identified_discrepancies"]["feedback"] = f"{count} of 8 discrepancies correctly identified."
    
    # Evaluate total overcharge
    overcharge = submission.get("total_overcharge", 0)
    if abs(overcharge - 38000.00) < 0.01:
        results["total_overcharge"]["score"] = 5
        results["total_overcharge"]["feedback"] = "Correct total overcharge calculation."
    else:
        results["total_overcharge"]["score"] = 0
        results["total_overcharge"]["feedback"] = "Incorrect total overcharge calculation."
    
    # Evaluate corrected total price
    corrected_price = submission.get("corrected_total_price", 0)
    if abs(corrected_price - 122000.00) < 0.01:
        results["corrected_total_price"]["score"] = 5
        results["corrected_total_price"]["feedback"] = "Correct corrected total price calculation."
    else:
        results["corrected_total_price"]["score"] = 0
        results["corrected_total_price"]["feedback"] = "Incorrect corrected total price calculation."
    
    # Evaluate negotiation points
    negotiation_points = submission.get("negotiation_points", "")
    key_elements = [
        "manufacturing overhead", 
        "r&d allocation", 
        "packaging", 
        "administrative costs", 
        "profit margin", 
        "certification fees", 
        "documentation"
    ]
    
    element_count = count_key_elements(negotiation_points, key_elements)
    results["negotiation_points"]["score"] = min(7, element_count)
    results["negotiation_points"]["feedback"] = f"Negotiation points address {element_count} of 7 key areas."
    
    # Calculate total score
    results["total_score"] = (
        results["identified_discrepancies"]["score"] + 
        results["total_overcharge"]["score"] + 
        results["corrected_total_price"]["score"] + 
        results["negotiation_points"]["score"]
    )
    
    return results

def evaluate_exercise4(submission, answer_key):
    """Evaluate Exercise 4: Price Justification Evaluation."""
    results = {
        "acceptable_justifications": {
            "score": 0,
            "max_points": 7,
            "feedback": ""
        },
        "unacceptable_justifications": {
            "score": 0,
            "max_points": 7,
            "feedback": ""
        },
        "counter_proposal": {
            "score": 0,
            "max_points": 5,
            "feedback": ""
        },
        "negotiation_strategy": {
            "score": 0,
            "max_points": 6,
            "feedback": ""
        },
        "total_score": 0,
        "max_points": 25
    }
    
    # Evaluate acceptable and unacceptable justifications
    acceptable = submission.get("acceptable_justifications", [])
    unacceptable = submission.get("unacceptable_justifications", [])
    
    if validate_justifications(acceptable, unacceptable):
        results["acceptable_justifications"]["score"] = 7
        results["acceptable_justifications"]["feedback"] = "All acceptable justifications correctly identified."
        results["unacceptable_justifications"]["score"] = 7
        results["unacceptable_justifications"]["feedback"] = "All unacceptable justifications correctly identified."
    else:
        # Count correct acceptable justifications
        correct_acceptable = ["1", "2", "3", "4", "8"]
        acceptable_nums = []
        for item in acceptable:
            match = re.search(r'(\d+)', item)
            if match:
                acceptable_nums.append(match.group(1))
        
        acceptable_count = sum(1 for num in correct_acceptable if num in acceptable_nums)
        results["acceptable_justifications"]["score"] = min(7, acceptable_count * 1.4)
        results["acceptable_justifications"]["feedback"] = f"{acceptable_count} of 5 acceptable justifications correctly identified."
        
        # Count correct unacceptable justifications
        correct_unacceptable = ["5", "6", "7"]
        unacceptable_nums = []
        for item in unacceptable:
            match = re.search(r'(\d+)', item)
            if match:
                unacceptable_nums.append(match.group(1))
        
        unacceptable_count = sum(1 for num in correct_unacceptable if num in unacceptable_nums)
        results["unacceptable_justifications"]["score"] = min(7, unacceptable_count * 2.33)
        results["unacceptable_justifications"]["feedback"] = f"{unacceptable_count} of 3 unacceptable justifications correctly identified."
    
    # Evaluate counter proposal
    counter_proposal = submission.get("counter_proposal", 0)
    if validate_reasonable_price(counter_proposal, "exercise4"):
        results["counter_proposal"]["score"] = 5
        results["counter_proposal"]["feedback"] = "Counter proposal within acceptable range."
    else:
        # Partial credit based on how close they are to the acceptable range
        if 88.00 <= counter_proposal <= 95.00:
            results["counter_proposal"]["score"] = 2
            results["counter_proposal"]["feedback"] = "Counter proposal is close to acceptable range but not optimal."
        else:
            results["counter_proposal"]["score"] = 0
            results["counter_proposal"]["feedback"] = "Counter proposal is outside acceptable range."
    
    # Evaluate negotiation strategy
    strategy = submission.get("negotiation_strategy", "")
    key_elements = [
        "legitimate cost", 
        "unjustified increase", 
        "counter-proposal", 
        "concessions", 
        "phased implementation", 
        "review mechanism"
    ]
    
    element_count = count_key_elements(strategy, key_elements)
    results["negotiation_strategy"]["score"] = min(6, element_count)
    results["negotiation_strategy"]["feedback"] = f"Negotiation strategy includes {element_count} of 6 key elements."
    
    # Calculate total score
    results["total_score"] = (
        results["acceptable_justifications"]["score"] + 
        results["unacceptable_justifications"]["score"] + 
        results["counter_proposal"]["score"] + 
        results["negotiation_strategy"]["score"]
    )
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "exercise1": evaluate_exercise1(submission.get("exercise1", {}), answer_key.get("exercise1", {})),
        "exercise2": evaluate_exercise2(submission.get("exercise2", {}), answer_key.get("exercise2", {})),
        "exercise3": evaluate_exercise3(submission.get("exercise3", {}), answer_key.get("exercise3", {})),
        "exercise4": evaluate_exercise4(submission.get("exercise4", {}), answer_key.get("exercise4", {})),
        "overall_score": 0,
        "passing_threshold": 70,
        "passed": False,
        "feedback": ""
    }
    
    # Calculate overall score
    total_points = (
        results["exercise1"]["total_score"] +
        results["exercise2"]["total_score"] +
        results["exercise3"]["total_score"] +
        results["exercise4"]["total_score"]
    )
    
    max_points = (
        results["exercise1"]["max_points"] +
        results["exercise2"]["max_points"] +
        results["exercise3"]["max_points"] +
        results["exercise4"]["max_points"]
    )
    
    results["overall_score"] = round((total_points / max_points) * 100, 2)
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    
    # Check minimum requirements
    min_required_per_exercise = 15
    exercises_below_min = []
    
    for exercise in ["exercise1", "exercise2", "exercise3", "exercise4"]:
        if results[exercise]["total_score"] < min_required_per_exercise:
            exercises_below_min.append(exercise)
    
    if exercises_below_min:
        results["passed"] = False
        exercises_str = ", ".join(exercises_below_min)
        results["feedback"] = f"Failed to meet minimum score requirement in: {exercises_str}"
    else:
        if results["passed"]:
            results["feedback"] = "Passed assessment with satisfactory performance across all exercises."
        else:
            results["feedback"] = "Failed to meet overall passing threshold of 70%."
    
    return results

def main():
    # Load submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    print(f"Feedback: {results['feedback']}")

if __name__ == "__main__":
    main()