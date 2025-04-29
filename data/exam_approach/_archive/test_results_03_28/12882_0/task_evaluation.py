import json
import re
import os
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_question_1(submission, answer_key):
    """Evaluate Question 1: Apple cases calculation."""
    score = 0
    max_score = 20
    
    # Check product selection (6 points)
    product_score = 0
    expected_products = [p["product"] for p in answer_key["question1"]["requiredProducts"]]
    submitted_products = [p["product"] for p in submission["question1"]["requiredProducts"]]
    
    for product in expected_products:
        if product in submitted_products:
            product_score += 2
    
    # Check quantity calculation (8 points)
    quantity_score = 0
    expected_quantities = {p["product"]: p["quantity"] for p in answer_key["question1"]["requiredProducts"]}
    submitted_quantities = {p["product"]: p["quantity"] for p in submission["question1"]["requiredProducts"]}
    
    for product, expected_qty in expected_quantities.items():
        if product in submitted_quantities and submitted_quantities[product] == expected_qty:
            quantity_score += (8/3)  # 8 points divided by 3 products
    
    # Check reasoning (4 points)
    reasoning_score = 0
    if submission["question1"].get("reasoning") and len(submission["question1"]["reasoning"]) > 20:
        if "divid" in submission["question1"]["reasoning"].lower() and "round" in submission["question1"]["reasoning"].lower():
            reasoning_score += 4
        elif "divid" in submission["question1"]["reasoning"].lower() or "round" in submission["question1"]["reasoning"].lower():
            reasoning_score += 2
    
    # Check format (2 points)
    format_score = 0
    if "requiredProducts" in submission["question1"] and isinstance(submission["question1"]["requiredProducts"], list):
        if all(isinstance(p, dict) and "product" in p and "quantity" in p and "unit" in p for p in submission["question1"]["requiredProducts"]):
            format_score += 2
    
    score = product_score + quantity_score + reasoning_score + format_score
    return min(score, max_score)  # Cap at maximum score

def evaluate_question_2(submission, answer_key):
    """Evaluate Question 2: Tomato supplier selection."""
    score = 0
    max_score = 20
    
    # Check product selection (6 points)
    product_score = 0
    # Check if they excluded Supplier C (which doesn't meet specs)
    submitted_products = [p["product"].lower() for p in submission["question2"]["requiredProducts"]]
    if not any("supplier c" in p for p in submitted_products):
        product_score += 3
    
    # Check that they used Suppliers A and B
    if any("supplier a" in p for p in submitted_products) and any("supplier b" in p for p in submitted_products):
        product_score += 3
    
    # Check quantity calculation (8 points)
    quantity_score = 0
    total_quantity = sum(p["quantity"] for p in submission["question2"]["requiredProducts"])
    
    # Check if total quantity meets required 18,500 lbs
    if total_quantity == 18500:
        quantity_score += 4
    
    # Check if they maximized the usage of the lower cost supplier (B)
    b_quantity = 0
    for p in submission["question2"]["requiredProducts"]:
        if "supplier b" in p["product"].lower():
            b_quantity = p["quantity"]
    
    if b_quantity == 9000:  # Maximum available from Supplier B
        quantity_score += 4
    
    # Check reasoning (4 points)
    reasoning_score = 0
    reasoning = submission["question2"].get("reasoning", "").lower()
    if reasoning and len(reasoning) > 20:
        if "6.1%" in reasoning and "doesn't meet" in reasoning:
            reasoning_score += 2
        if "lowest" in reasoning and "cost" in reasoning:
            reasoning_score += 2
    
    # Check format (2 points)
    format_score = 0
    if "requiredProducts" in submission["question2"] and isinstance(submission["question2"]["requiredProducts"], list):
        if all(isinstance(p, dict) and "product" in p and "quantity" in p and "unit" in p for p in submission["question2"]["requiredProducts"]):
            format_score += 2
    
    score = product_score + quantity_score + reasoning_score + format_score
    return min(score, max_score)  # Cap at maximum score

def evaluate_question_3(submission, answer_key):
    """Evaluate Question 3: Feed grain order calculation."""
    score = 0
    max_score = 20
    
    # Check product selection (6 points)
    product_score = 0
    if len(submission["question3"]["requiredProducts"]) == 2:
        product_score += 3
        
        # Check that they ordered from both suppliers
        submitted_products = [p["product"].lower() for p in submission["question3"]["requiredProducts"]]
        if any("primary" in p for p in submitted_products) and any("secondary" in p for p in submitted_products):
            product_score += 3
    
    # Check quantity calculation (8 points)
    quantity_score = 0
    primary_qty = 0
    secondary_qty = 0
    
    for p in submission["question3"]["requiredProducts"]:
        if "primary" in p["product"].lower():
            primary_qty = p["quantity"]
        elif "secondary" in p["product"].lower():
            secondary_qty = p["quantity"]
    
    if primary_qty == 40:  # Maximum from primary
        quantity_score += 4
    
    if secondary_qty == 25:  # Correct amount from secondary
        quantity_score += 4
    
    # Check reasoning (4 points)
    reasoning_score = 0
    reasoning = submission["question3"].get("reasoning", "").lower()
    if reasoning and len(reasoning) > 20:
        if "79" in reasoning and "14" in reasoning and "65" in reasoning:
            reasoning_score += 2
        if "lead time" in reasoning or "delivery" in reasoning:
            reasoning_score += 2
    
    # Check format (2 points)
    format_score = 0
    if "requiredProducts" in submission["question3"] and isinstance(submission["question3"]["requiredProducts"], list):
        if all(isinstance(p, dict) and "product" in p and "quantity" in p and "unit" in p for p in submission["question3"]["requiredProducts"]):
            format_score += 2
    
    score = product_score + quantity_score + reasoning_score + format_score
    return min(score, max_score)  # Cap at maximum score

def evaluate_question_4(submission, answer_key):
    """Evaluate Question 4: Berry container calculation."""
    score = 0
    max_score = 20
    
    # Check product selection (6 points)
    product_score = 0
    expected_products = ["Strawberry flats", "Blueberry containers", "Raspberry containers"]
    submitted_products = [p["product"] for p in submission["question4"]["requiredProducts"]]
    
    for product in expected_products:
        if any(product.lower() in p.lower() for p in submitted_products):
            product_score += 2
    
    # Check quantity calculation (8 points)
    quantity_score = 0
    expected_quantities = {
        "Strawberry flats": 53,
        "Blueberry containers": 56,
        "Raspberry containers": 40
    }
    
    for product_name, expected_qty in expected_quantities.items():
        for submitted_product in submission["question4"]["requiredProducts"]:
            if product_name.lower() in submitted_product["product"].lower():
                if submitted_product["quantity"] == expected_qty:
                    quantity_score += (8/3)  # 8 points divided by 3 products
    
    # Check reasoning (4 points)
    reasoning_score = 0
    reasoning = submission["question4"].get("reasoning", "").lower()
    if reasoning and len(reasoning) > 20:
        if "weekly" in reasoning:
            reasoning_score += 2
        if "divided" in reasoning or "÷" in reasoning:
            reasoning_score += 2
    
    # Check format (2 points)
    format_score = 0
    if "requiredProducts" in submission["question4"] and isinstance(submission["question4"]["requiredProducts"], list):
        if all(isinstance(p, dict) and "product" in p and "quantity" in p and "unit" in p for p in submission["question4"]["requiredProducts"]):
            format_score += 2
    
    score = product_score + quantity_score + reasoning_score + format_score
    return min(score, max_score)  # Cap at maximum score

def evaluate_question_5(submission, answer_key):
    """Evaluate Question 5: Olive oil container optimization."""
    score = 0
    max_score = 20
    
    # For Q5, multiple valid solutions exist, need to validate based on criteria
    
    # Extract submitted products for each grade
    extra_virgin_products = []
    virgin_products = []
    pure_products = []
    
    for p in submission["question5"]["requiredProducts"]:
        product_name = p["product"].lower()
        if "extra virgin" in product_name:
            extra_virgin_products.append(p)
        elif "virgin" in product_name and "extra" not in product_name:
            virgin_products.append(p)
        elif "pure" in product_name:
            pure_products.append(p)
    
    # Calculate total gallons per grade and total containers
    ev_gallons = 0
    v_gallons = 0
    p_gallons = 0
    total_containers = 0
    
    for p in extra_virgin_products:
        if "55" in p["unit"]:
            ev_gallons += p["quantity"] * 55
        elif "35" in p["unit"]:
            ev_gallons += p["quantity"] * 35
        elif "5" in p["unit"]:
            ev_gallons += p["quantity"] * 5
        total_containers += p["quantity"]
    
    for p in virgin_products:
        if "55" in p["unit"]:
            v_gallons += p["quantity"] * 55
        elif "35" in p["unit"]:
            v_gallons += p["quantity"] * 35
        elif "5" in p["unit"]:
            v_gallons += p["quantity"] * 5
        total_containers += p["quantity"]
    
    for p in pure_products:
        if "55" in p["unit"]:
            p_gallons += p["quantity"] * 55
        elif "35" in p["unit"]:
            p_gallons += p["quantity"] * 35
        elif "5" in p["unit"]:
            p_gallons += p["quantity"] * 5
        total_containers += p["quantity"]
    
    # Check product selection and volumes (6 points)
    product_score = 0
    if ev_gallons == 860:
        product_score += 2
    if v_gallons == 520:
        product_score += 2
    if p_gallons == 340:
        product_score += 2
    
    # Check container count constraint (8 points)
    quantity_score = 0
    if total_containers <= 40:
        quantity_score += 8
    elif total_containers <= 45:  # Close but not perfect
        quantity_score += 4
    
    # Check reasoning (4 points)
    reasoning_score = 0
    reasoning = submission["question5"].get("reasoning", "").lower()
    if reasoning and len(reasoning) > 20:
        if "container" in reasoning and "limit" in reasoning:
            reasoning_score += 2
        if any(unit in reasoning for unit in ["55", "35", "5"]):
            reasoning_score += 2
    
    # Check format (2 points)
    format_score = 0
    if "requiredProducts" in submission["question5"] and isinstance(submission["question5"]["requiredProducts"], list):
        if all(isinstance(p, dict) and "product" in p and "quantity" in p and "unit" in p for p in submission["question5"]["requiredProducts"]):
            format_score += 2
    
    score = product_score + quantity_score + reasoning_score + format_score
    return min(score, max_score)  # Cap at maximum score

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    results = {
        "question1_score": evaluate_question_1(submission, answer_key),
        "question2_score": evaluate_question_2(submission, answer_key),
        "question3_score": evaluate_question_3(submission, answer_key),
        "question4_score": evaluate_question_4(submission, answer_key),
        "question5_score": evaluate_question_5(submission, answer_key)
    }
    
    # Calculate overall score as percentage
    total_score = sum(results.values())
    results["overall_score"] = total_score
    results["overall_percentage"] = (total_score / 100) * 100  # 100 is max possible score
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load necessary files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Create output file
    output = {"overall_score": results["overall_percentage"]}
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_percentage']}%")

if __name__ == "__main__":
    main()