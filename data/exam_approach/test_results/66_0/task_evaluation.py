import json
import re
import os

def load_json_file(file_path):
    """Load and return the contents of a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File {file_path} is not valid JSON.")
        return None

def extract_percentage(text):
    """Extract percentage value from text."""
    if text:
        match = re.search(r'(-?\d+\.?\d*)%', text)
        if match:
            return float(match.group(1))
    return None

def extract_dollar_amount(text):
    """Extract dollar amount from text."""
    if text:
        match = re.search(r'\$(\d+,?\d*)', text.replace(',', ''))
        if match:
            return int(match.group(1))
    return None

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Sales Data Interpretation."""
    results = {
        "question1": {"score": 0, "max_score": 1, "comments": ""},
        "question2": {"score": 0, "max_score": 1, "comments": ""},
        "question3": {"score": 0, "max_score": 1, "comments": ""}
    }
    
    # Question 1: Department with most consistent sales
    if submission["question1"].lower() == answer_key["question1"].lower():
        results["question1"]["score"] = 1
        results["question1"]["comments"] = "Correct department identified."
    else:
        results["question1"]["comments"] = f"Incorrect. The correct answer is {answer_key['question1']}."
    
    # Question 2: YoY growth percentage
    submitted_percentage = extract_percentage(submission["question2"])
    correct_percentage = extract_percentage(answer_key["question2"])
    
    if submitted_percentage is not None and correct_percentage is not None:
        if abs(submitted_percentage - correct_percentage) <= 0.1:
            results["question2"]["score"] = 1
            results["question2"]["comments"] = "Correct growth percentage calculation."
        else:
            results["question2"]["comments"] = f"Incorrect calculation. The correct answer is {answer_key['question2']}."
    else:
        results["question2"]["comments"] = "Could not parse percentage value or format is incorrect."
    
    # Question 3: Highest percentage increase
    if answer_key["question3"].lower() in submission["question3"].lower():
        # Extract and check percentage
        submitted_percentage = extract_percentage(submission["question3"])
        correct_percentage = extract_percentage(answer_key["question3"])
        
        if submitted_percentage is not None and correct_percentage is not None:
            if abs(submitted_percentage - correct_percentage) <= 0.1:
                results["question3"]["score"] = 1
                results["question3"]["comments"] = "Correct department and percentage increase identified."
            else:
                results["question3"]["score"] = 0.5
                results["question3"]["comments"] = f"Correct department but incorrect percentage. The correct answer is {answer_key['question3']}."
        else:
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "Correct department but could not parse percentage."
    else:
        results["question3"]["comments"] = f"Incorrect. The correct answer is {answer_key['question3']}."
    
    return results

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Trend Identification."""
    results = {
        "question1": {"score": 0, "max_score": 1, "comments": ""},
        "question2": {"score": 0, "max_score": 1, "comments": ""},
        "question3": {"score": 0, "max_score": 1, "comments": ""}
    }
    
    # Question 1: Product category with strongest seasonal pattern
    correct_category = answer_key["question1"].split(" - ")[0]
    if correct_category.lower() in submission["question1"].lower():
        # Check if there's a reasonably good description
        if len(submission["question1"].split(" - ")) > 1 and len(submission["question1"]) > len(correct_category) + 10:
            results["question1"]["score"] = 1
            results["question1"]["comments"] = "Correct category and seasonal pattern identified."
        else:
            results["question1"]["score"] = 0.5
            results["question1"]["comments"] = "Correct category but insufficient explanation of the pattern."
    else:
        alt_correct = "Home Goods"  # As specified in the evaluation guide
        if alt_correct.lower() in submission["question1"].lower() and len(submission["question1"]) > len(alt_correct) + 10:
            results["question1"]["score"] = 0.5
            results["question1"]["comments"] = "Alternate acceptable answer with justification."
        else:
            results["question1"]["comments"] = f"Incorrect. The correct answer is {correct_category} with clear seasonal pattern."
    
    # Question 2: 3-month moving average
    try:
        submitted_value = float(submission["question2"])
        correct_value = float(answer_key["question2"])
        
        if abs(submitted_value - correct_value) <= 0.01:
            results["question2"]["score"] = 1
            results["question2"]["comments"] = "Correct moving average calculation."
        else:
            results["question2"]["comments"] = f"Incorrect calculation. The correct answer is {answer_key['question2']}."
    except (ValueError, TypeError):
        results["question2"]["comments"] = "Could not parse the submitted value as a decimal number."
    
    # Question 3: Month recommendation for inventory increase
    correct_month = answer_key["question3"].split(" - ")[0]
    if correct_month.lower() in submission["question3"].lower():
        # Check if there's a reasonably good justification
        if len(submission["question3"].split(" - ")) > 1 and len(submission["question3"]) > len(correct_month) + 20:
            results["question3"]["score"] = 1
            results["question3"]["comments"] = "Correct month and justification provided."
        else:
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "Correct month but insufficient justification."
    else:
        alt_correct = "October"  # As specified in the evaluation guide
        if alt_correct.lower() in submission["question3"].lower() and "preparing ahead" in submission["question3"].lower():
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "Alternate acceptable answer with valid justification."
        else:
            results["question3"]["comments"] = f"Incorrect. The correct recommendation is {correct_month} with proper justification."
    
    return results

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Economic Indicator Analysis."""
    results = {
        "question1": {"score": 0, "max_score": 1, "comments": ""},
        "question2": {"score": 0, "max_score": 1, "comments": ""},
        "question3": {"score": 0, "max_score": 1, "comments": ""}
    }
    
    # Question 1: Economic indicator with strongest correlation
    correct_indicator = answer_key["question1"].split(" - ")[0]
    if correct_indicator.lower() in submission["question1"].lower():
        # Check if there's a reasonably good explanation
        if len(submission["question1"].split(" - ")) > 1 and len(submission["question1"]) > len(correct_indicator) + 15:
            results["question1"]["score"] = 1
            results["question1"]["comments"] = "Correct indicator identified with supporting explanation."
        else:
            results["question1"]["score"] = 0.5
            results["question1"]["comments"] = "Correct indicator but insufficient explanation."
    else:
        # Check if they provided any other indicator with strong reasoning
        if " - " in submission["question1"] and len(submission["question1"]) > 40:
            results["question1"]["score"] = 0.5
            results["question1"]["comments"] = "Alternative indicator accepted with credible correlation analysis."
        else:
            results["question1"]["comments"] = f"Incorrect. The indicator with strongest correlation is {correct_indicator}."
    
    # Question 2: Sales impact based on CCI forecast
    if "positive" in submission["question2"].lower():
        # Extract and check percentage
        submitted_percentage = extract_percentage(submission["question2"])
        if submitted_percentage is not None and 1.5 <= submitted_percentage <= 4.0:
            results["question2"]["score"] = 1
            results["question2"]["comments"] = "Correct impact direction and reasonable percentage estimate."
        else:
            results["question2"]["score"] = 0.5
            results["question2"]["comments"] = "Correct impact direction but percentage outside acceptable range or not clearly specified."
    else:
        results["question2"]["comments"] = "Incorrect. Impact should be positive with percentage in 1.5-4.0% range."
    
    # Question 3: Most vulnerable department
    correct_dept = answer_key["question3"].split(" - ")[0]
    alt_correct_depts = ["Women's Casual", "Footwear"]  # As specified in evaluation guide
    
    if correct_dept.lower() in submission["question3"].lower():
        if len(submission["question3"].split(" - ")) > 1 and len(submission["question3"]) > len(correct_dept) + 15:
            results["question3"]["score"] = 1
            results["question3"]["comments"] = "Correct department identified with good explanation."
        else:
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "Correct department but insufficient explanation."
    else:
        # Check for alternative acceptable departments
        for alt_dept in alt_correct_depts:
            if alt_dept.lower() in submission["question3"].lower() and len(submission["question3"]) > len(alt_dept) + 15:
                results["question3"]["score"] = 0.5
                results["question3"]["comments"] = f"Alternative acceptable department ({alt_dept}) with reasonable explanation."
                break
        else:
            results["question3"]["comments"] = f"Incorrect. The most vulnerable department is {correct_dept}."
    
    return results

def evaluate_section4(submission, answer_key):
    """Evaluate Section 4: Inventory Planning."""
    results = {
        "question1": {"score": 0, "max_score": 1, "comments": ""},
        "question2": {"score": 0, "max_score": 1, "comments": ""},
        "question3": {"score": 0, "max_score": 1, "comments": ""}
    }
    
    # Question 1: Weeks of supply calculation
    correct_weeks = {
        "Product A": 12.0,
        "Product B": 6.7,
        "Product C": 20.0,
        "Product D": 5.6,
        "Product E": 8.7
    }
    
    all_correct = True
    products_mentioned = 0
    
    for product, weeks in correct_weeks.items():
        if product.lower() in submission["question1"].lower():
            products_mentioned += 1
            # Try to extract the number of weeks
            match = re.search(fr"{product}.*?(\d+\.?\d*)", submission["question1"])
            if match:
                submitted_weeks = float(match.group(1))
                if abs(submitted_weeks - weeks) > 0.1:
                    all_correct = False
            else:
                all_correct = False
    
    if products_mentioned == 5 and all_correct:
        results["question1"]["score"] = 1
        results["question1"]["comments"] = "All weeks of supply correctly calculated."
    elif products_mentioned >= 3:
        results["question1"]["score"] = 0.5
        results["question1"]["comments"] = "Some products' weeks of supply correctly calculated, but not all."
    else:
        results["question1"]["comments"] = "Insufficient or incorrect weeks of supply calculations."
    
    # Question 2: Product requiring immediate reorder
    correct_product = answer_key["question2"].split(" - ")[0]
    if correct_product.lower() in submission["question2"].lower() and "immediate" in submission["question2"].lower():
        results["question2"]["score"] = 1
        results["question2"]["comments"] = "Correct product and timing identified."
    elif correct_product.lower() in submission["question2"].lower():
        results["question2"]["score"] = 0.5
        results["question2"]["comments"] = "Correct product identified but timing not clearly specified."
    else:
        results["question2"]["comments"] = f"Incorrect. {correct_product} requires the most immediate reorder."
    
    # Question 3: Budget allocation
    # This is complex to parse precisely, so we'll check for key elements
    try:
        # Check if all products are mentioned
        all_products_mentioned = all(f"Product {chr(65+i)}" in submission["question3"] for i in range(5))
        
        # Check if total is under budget
        total_mentioned = re.search(r"total.*?\$(\d+,?\d*)", submission["question3"].lower())
        if total_mentioned:
            total = int(total_mentioned.group(1).replace(',', ''))
            under_budget = total <= 15000
        else:
            # Try to add up the individual allocations
            product_allocations = {}
            for i in range(5):
                product = f"Product {chr(65+i)}"
                match = re.search(fr"{product}.*?(\d+).*?\$(\d+,?\d*)", submission["question3"])
                if match:
                    units = int(match.group(1))
                    unit_cost = int(match.group(2).replace(',', ''))
                    product_allocations[product] = units * unit_cost
            
            if product_allocations:
                total = sum(product_allocations.values())
                under_budget = total <= 15000
            else:
                under_budget = None
        
        # Make scoring decision
        if all_products_mentioned and under_budget:
            results["question3"]["score"] = 1
            results["question3"]["comments"] = "Good budget allocation with all products covered."
        elif all_products_mentioned:
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "All products included but budget allocation issues."
        else:
            results["question3"]["comments"] = "Insufficient or incorrect budget allocation."
    
    except Exception as e:
        results["question3"]["comments"] = f"Could not fully evaluate budget allocation response. Error: {str(e)}"
    
    return results

def evaluate_section5(submission, answer_key):
    """Evaluate Section 5: Forecasting Scenario."""
    results = {
        "question1": {"score": 0, "max_score": 1, "comments": ""},
        "question2": {"score": 0, "max_score": 1, "comments": ""},
        "question3": {"score": 0, "max_score": 1, "comments": ""}
    }
    
    # Question 1: Expected sales based on historical trend
    submitted_amount = extract_dollar_amount(submission["question1"])
    correct_amount = extract_dollar_amount(answer_key["question1"])
    
    if submitted_amount is not None and correct_amount is not None:
        # Allow range as per evaluation guidelines
        if 310000 <= submitted_amount <= 314000:
            results["question1"]["score"] = 1
            results["question1"]["comments"] = "Correct sales projection based on historical trend."
        else:
            results["question1"]["comments"] = f"Incorrect calculation. The expected sales should be around {answer_key['question1']}."
    else:
        results["question1"]["comments"] = "Could not parse dollar amount or format is incorrect."
    
    # Question 2: Forecast adjustment
    if "up" in submission["question2"].lower():
        submitted_percentage = extract_percentage(submission["question2"])
        if submitted_percentage is not None and 5.0 <= submitted_percentage <= 10.0:
            results["question2"]["score"] = 1
            results["question2"]["comments"] = "Appropriate upward adjustment within acceptable range."
        elif submitted_percentage is not None:
            results["question2"]["score"] = 0.5
            results["question2"]["comments"] = "Correct direction (up) but percentage outside optimal range."
        else:
            results["question2"]["score"] = 0.5
            results["question2"]["comments"] = "Correct direction (up) but percentage not clearly specified."
    else:
        results["question2"]["comments"] = "Incorrect. Forecast should be adjusted upward by 5-10%."
    
    # Question 3: Recommended inventory value
    submitted_amount = extract_dollar_amount(submission["question3"])
    
    if submitted_amount is not None and 130000 <= submitted_amount <= 138000:
        if "$" in submission["question3"] and len(submission["question3"]) > 8:
            results["question3"]["score"] = 1
            results["question3"]["comments"] = "Correct inventory value with explanation."
        else:
            results["question3"]["score"] = 0.5
            results["question3"]["comments"] = "Correct inventory value but insufficient explanation."
    else:
        results["question3"]["comments"] = "Incorrect inventory value. Should be in range $130,000-$138,000."
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    evaluations = {
        "section1": evaluate_section1(submission["section1"], answer_key["section1"]),
        "section2": evaluate_section2(submission["section2"], answer_key["section2"]),
        "section3": evaluate_section3(submission["section3"], answer_key["section3"]),
        "section4": evaluate_section4(submission["section4"], answer_key["section4"]),
        "section5": evaluate_section5(submission["section5"], answer_key["section5"])
    }
    
    # Calculate total score
    total_score = 0
    total_possible = 0
    
    for section, questions in evaluations.items():
        section_score = 0
        section_possible = 0
        
        for question, details in questions.items():
            section_score += details["score"]
            section_possible += details["max_score"]
        
        evaluations[section]["section_score"] = section_score
        evaluations[section]["section_possible"] = section_possible
        evaluations[section]["section_percentage"] = (section_score / section_possible) * 100
        
        total_score += section_score
        total_possible += section_possible
    
    overall_percentage = (total_score / total_possible) * 100
    
    # Add pass/fail information based on 73% passing threshold
    passed = overall_percentage >= 73
    
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_score": total_score,
        "total_possible": total_possible,
        "overall_score": overall_percentage,
        "passed": passed,
        "sections": evaluations
    }
    
    return results

def main():
    # Define file paths
    submission_path = "test_submission.json"
    answer_key_path = "answer_key.json"
    results_path = "test_results.json"
    
    # Load files
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    if not submission or not answer_key:
        print("Error: Could not proceed with evaluation due to missing files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open(results_path, 'w') as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation completed. Results saved to {results_path}")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")

if __name__ == "__main__":
    main()