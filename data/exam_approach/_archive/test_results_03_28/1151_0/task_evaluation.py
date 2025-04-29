import json
import re
import os

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Purchase Record Analysis."""
    results = {
        "total_points": 20,
        "earned_points": 0,
        "questions": {}
    }
    
    # Q1: Total spend on item RM-1095
    q1_sub = submission.get("q1", "").strip().replace("$", "")
    q1_key = answer_key.get("q1", "").strip().replace("$", "")
    if q1_sub == q1_key:
        results["questions"]["q1"] = {"earned": 5, "possible": 5, "comment": "Correct total spend calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q1"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q1')}"}
    
    # Q2: Supplier with most consistent pricing
    q2_sub = submission.get("q2", "").strip()
    q2_key = answer_key.get("q2", "").strip()
    if q2_sub == q2_key:
        results["questions"]["q2"] = {"earned": 5, "possible": 5, "comment": "Correctly identified supplier with most consistent pricing."}
        results["earned_points"] += 5
    else:
        results["questions"]["q2"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q2')}"}
    
    # Q3: Average delivery time
    q3_sub = submission.get("q3", "").strip()
    q3_key = answer_key.get("q3", "").strip()
    if q3_sub == q3_key:
        results["questions"]["q3"] = {"earned": 5, "possible": 5, "comment": "Correct average delivery time calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q3')}"}
    
    # Q4: Total quantity of RM-2087 in Q1 2023
    q4_sub = submission.get("q4", "").strip()
    q4_key = answer_key.get("q4", "").strip()
    if q4_sub == q4_key:
        results["questions"]["q4"] = {"earned": 5, "possible": 5, "comment": "Correct total quantity calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q4')}"}
    
    return results

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Purchase Record Discrepancy Identification."""
    results = {
        "total_points": 20,
        "earned_points": 0,
        "questions": {}
    }
    
    # Q1: Identify all POs with discrepancies
    q1_sub = submission.get("q1", "").strip()
    q1_key = answer_key.get("q1", "").strip()
    
    # Handle JSON array strings
    try:
        # Extract PO numbers from strings
        sub_po_discrepancies = set()
        key_po_discrepancies = set()
        
        # Extract PO numbers from submission
        for po_match in re.finditer(r'PO-\d+-\d+', q1_sub):
            sub_po_discrepancies.add(po_match.group(0))
            
        # Extract PO numbers from answer key  
        for po_match in re.finditer(r'PO-\d+-\d+', q1_key):
            key_po_discrepancies.add(po_match.group(0))
        
        # Calculate correctness
        if sub_po_discrepancies == key_po_discrepancies:
            results["questions"]["q1"] = {"earned": 5, "possible": 5, "comment": "Correctly identified all POs with discrepancies."}
            results["earned_points"] += 5
        else:
            points = 0
            missing = key_po_discrepancies - sub_po_discrepancies
            extra = sub_po_discrepancies - key_po_discrepancies
            comment = ""
            
            if len(key_po_discrepancies) > 0:
                points = int(5 * len(sub_po_discrepancies.intersection(key_po_discrepancies)) / len(key_po_discrepancies))
            
            if missing:
                comment += f"Missing POs: {', '.join(missing)}. "
            if extra:
                comment += f"Incorrectly included POs: {', '.join(extra)}. "
                
            results["questions"]["q1"] = {"earned": points, "possible": 5, "comment": comment.strip()}
            results["earned_points"] += points
    except Exception as e:
        results["questions"]["q1"] = {"earned": 0, "possible": 5, "comment": f"Error parsing discrepancies: {str(e)}"}
    
    # Q2: Dollar value of PO-2023-2003 discrepancy
    q2_sub = submission.get("q2", "").strip().replace("$", "")
    q2_key = answer_key.get("q2", "").strip().replace("$", "")
    if q2_sub == q2_key:
        results["questions"]["q2"] = {"earned": 5, "possible": 5, "comment": "Correct discrepancy calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q2"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q2')}"}
    
    # Q3: Dollar value of PO-2023-2008 discrepancy
    q3_sub = submission.get("q3", "").strip().replace("$", "")
    q3_key = answer_key.get("q3", "").strip().replace("$", "")
    if q3_sub == q3_key:
        results["questions"]["q3"] = {"earned": 5, "possible": 5, "comment": "Correct discrepancy calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q3')}"}
    
    # Q4: POs requiring investigation
    q4_sub = submission.get("q4", "").strip()
    q4_key = answer_key.get("q4", "").strip()
    
    # Parse JSON arrays
    try:
        sub_pos = set()
        key_pos = set()
        
        # Extract PO numbers from submission
        for po_match in re.finditer(r'PO-\d+-\d+', q4_sub):
            sub_pos.add(po_match.group(0))
            
        # Extract PO numbers from answer key  
        for po_match in re.finditer(r'PO-\d+-\d+', q4_key):
            key_pos.add(po_match.group(0))
        
        if sub_pos == key_pos:
            results["questions"]["q4"] = {"earned": 5, "possible": 5, "comment": "Correctly identified all POs requiring investigation."}
            results["earned_points"] += 5
        else:
            results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q4')}"}
    except Exception as e:
        results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": f"Error parsing POs: {str(e)}"}
    
    return results

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Inventory Metrics Calculation."""
    results = {
        "total_points": 20,
        "earned_points": 0,
        "questions": {}
    }
    
    # Q1: Average monthly inventory turnover ratio
    q1_sub = submission.get("q1", "").strip()
    q1_key = answer_key.get("q1", "").strip()
    if q1_sub == q1_key:
        results["questions"]["q1"] = {"earned": 5, "possible": 5, "comment": "Correct inventory turnover calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q1"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q1')}"}
    
    # Q2: Total inventory value at end of June
    q2_sub = submission.get("q2", "").strip().replace("$", "")
    q2_key = answer_key.get("q2", "").strip().replace("$", "")
    if q2_sub == q2_key:
        results["questions"]["q2"] = {"earned": 5, "possible": 5, "comment": "Correct inventory value calculation."}
        results["earned_points"] += 5
    else:
        results["questions"]["q2"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q2')}"}
    
    # Q3: Month with highest DOH
    q3_sub = submission.get("q3", "").strip().lower()
    q3_key = answer_key.get("q3", "").strip().lower()
    
    # Check if the month is correct (focus on the month name)
    key_month = re.search(r'(\w+):', q3_key)
    if key_month:
        key_month = key_month.group(1).lower()
        if key_month in q3_sub:
            results["questions"]["q3"] = {"earned": 5, "possible": 5, "comment": "Correctly identified month with highest DOH."}
            results["earned_points"] += 5
        else:
            results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q3')}"}
    else:
        results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": "Could not parse expected answer."}
    
    # Q4: Units to purchase in July
    q4_sub = submission.get("q4", "").strip()
    q4_key = answer_key.get("q4", "").strip()
    if q4_sub == q4_key:
        results["questions"]["q4"] = {"earned": 5, "possible": 5, "comment": "Correct calculation of units to purchase."}
        results["earned_points"] += 5
    else:
        results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q4')}"}
    
    return results

def evaluate_section4(submission, answer_key):
    """Evaluate Section 4: Product Performance Evaluation."""
    results = {
        "total_points": 20,
        "earned_points": 0,
        "questions": {}
    }
    
    # Q1: On-time delivery performance percentage
    q1_sub = submission.get("q1", "").strip().lower()
    q1_key = answer_key.get("q1", "").strip().lower()
    
    # Extract percentages for each supplier
    sub_percentages = {}
    key_percentages = {}
    
    # Extract from submission
    for supplier_match in re.finditer(r'(sup-\d+).*?(\d+\.\d+)%', q1_sub):
        sub_percentages[supplier_match.group(1).lower()] = supplier_match.group(2)
        
    # Extract from answer key
    for supplier_match in re.finditer(r'(sup-\d+).*?(\d+\.\d+)%', q1_key):
        key_percentages[supplier_match.group(1).lower()] = supplier_match.group(2)
    
    if sub_percentages == key_percentages:
        results["questions"]["q1"] = {"earned": 5, "possible": 5, "comment": "Correct on-time delivery percentages."}
        results["earned_points"] += 5
    else:
        results["questions"]["q1"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q1')}"}
    
    # Q2: Balanced scorecard total performance scores
    q2_sub = submission.get("q2", "").strip().lower()
    q2_key = answer_key.get("q2", "").strip().lower()
    
    # Extract scores for each supplier
    sub_scores = {}
    key_scores = {}
    
    # Extract from submission
    for supplier_match in re.finditer(r'(sup-\d+).*?(\d+)', q2_sub):
        sub_scores[supplier_match.group(1).lower()] = supplier_match.group(2)
        
    # Extract from answer key
    for supplier_match in re.finditer(r'(sup-\d+).*?(\d+)', q2_key):
        key_scores[supplier_match.group(1).lower()] = supplier_match.group(2)
    
    if sub_scores == key_scores:
        results["questions"]["q2"] = {"earned": 5, "possible": 5, "comment": "Correct balanced scorecard performance scores."}
        results["earned_points"] += 5
    else:
        results["questions"]["q2"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q2')}"}
    
    # Q3: Supplier for rush order with quality priority (reasoning question)
    q3_sub = submission.get("q3", "").strip().lower()
    q3_key = answer_key.get("q3", "").strip().lower()
    
    # Look for supplier recommendation and key reasoning elements
    sup_002_mentioned = "sup-002" in q3_sub
    quality_mentioned = "quality" in q3_sub
    defect_rate_mentioned = "defect" in q3_sub
    
    if sup_002_mentioned and (quality_mentioned or defect_rate_mentioned):
        if len(q3_sub.split()) >= 10:  # Ensure there's enough reasoning
            results["questions"]["q3"] = {"earned": 5, "possible": 5, "comment": "Correct supplier recommendation with appropriate reasoning."}
            results["earned_points"] += 5
        else:
            results["questions"]["q3"] = {"earned": 3, "possible": 5, "comment": "Correct supplier but insufficient reasoning."}
            results["earned_points"] += 3
    elif sup_002_mentioned:
        results["questions"]["q3"] = {"earned": 2, "possible": 5, "comment": "Correct supplier but missing key reasoning."}
        results["earned_points"] += 2
    else:
        results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": "Incorrect supplier recommendation."}
    
    # Q4: Supplier for cost reduction with longer lead times (reasoning question)
    q4_sub = submission.get("q4", "").strip().lower()
    q4_key = answer_key.get("q4", "").strip().lower()
    
    # Look for supplier recommendation and key reasoning elements
    sup_003_mentioned = "sup-003" in q4_sub
    cost_mentioned = "cost" in q4_sub or "price" in q4_sub or "value" in q4_sub
    lead_time_mentioned = "lead time" in q4_sub
    
    if sup_003_mentioned and (cost_mentioned or lead_time_mentioned):
        if len(q4_sub.split()) >= 10:  # Ensure there's enough reasoning
            results["questions"]["q4"] = {"earned": 5, "possible": 5, "comment": "Correct supplier recommendation with appropriate reasoning."}
            results["earned_points"] += 5
        else:
            results["questions"]["q4"] = {"earned": 3, "possible": 5, "comment": "Correct supplier but insufficient reasoning."}
            results["earned_points"] += 3
    elif sup_003_mentioned:
        results["questions"]["q4"] = {"earned": 2, "possible": 5, "comment": "Correct supplier but missing key reasoning."}
        results["earned_points"] += 2
    else:
        results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": "Incorrect supplier recommendation."}
    
    return results

def evaluate_section5(submission, answer_key):
    """Evaluate Section 5: Record-Keeping Best Practices."""
    results = {
        "total_points": 20,
        "earned_points": 0,
        "questions": {}
    }
    
    # Q1: Identify errors in purchase record entry
    q1_sub = submission.get("q1", "").strip().lower()
    q1_key = answer_key.get("q1", "").strip().lower()
    
    # Key errors to look for
    key_errors = [
        "invalid date", "june 31", 
        "missing supplier id", 
        "unit price", "text format", "words",
        "calculation error", "toner", 
        "po #", "po number", "format"
    ]
    
    error_count = 0
    for error in key_errors:
        if error in q1_sub:
            error_count += 1
    
    if error_count >= 4:
        results["questions"]["q1"] = {"earned": 5, "possible": 5, "comment": "Correctly identified at least 4 errors."}
        results["earned_points"] += 5
    elif error_count >= 2:
        results["questions"]["q1"] = {"earned": 3, "possible": 5, "comment": f"Identified {error_count} errors correctly."}
        results["earned_points"] += 3
    elif error_count >= 1:
        results["questions"]["q1"] = {"earned": 1, "possible": 5, "comment": "Identified only 1 error correctly."}
        results["earned_points"] += 1
    else:
        results["questions"]["q1"] = {"earned": 0, "possible": 5, "comment": "Did not identify any errors correctly."}
    
    # Q2: Provide corrected values
    q2_sub = submission.get("q2", "").strip().lower()
    q2_key = answer_key.get("q2", "").strip().lower()
    
    # Key corrections to look for
    key_corrections = [
        "06/30/2023", "june 30", 
        "supplier id", 
        "22.50", 
        "1,140.00", "1140"
    ]
    
    correction_count = 0
    for correction in key_corrections:
        if correction in q2_sub:
            correction_count += 1
    
    if correction_count >= 4:
        results["questions"]["q2"] = {"earned": 5, "possible": 5, "comment": "Provided correct values for at least 4 errors."}
        results["earned_points"] += 5
    elif correction_count >= 2:
        results["questions"]["q2"] = {"earned": 3, "possible": 5, "comment": f"Provided correct values for {correction_count} errors."}
        results["earned_points"] += 3
    elif correction_count >= 1:
        results["questions"]["q2"] = {"earned": 1, "possible": 5, "comment": "Provided correct value for only 1 error."}
        results["earned_points"] += 1
    else:
        results["questions"]["q2"] = {"earned": 0, "possible": 5, "comment": "Did not provide any correct values."}
    
    # Q3: Essential missing fields
    q3_sub = submission.get("q3", "").strip().lower()
    q3_key = answer_key.get("q3", "").strip().lower()
    
    # Key missing fields to look for
    key_fields = [
        "approval status", 
        "delivery date", "schedule", 
        "item codes", "sku", 
        "contact", 
        "department", "cost center", 
        "expected delivery"
    ]
    
    field_count = 0
    for field in key_fields:
        if field in q3_sub:
            field_count += 1
    
    if field_count >= 3:
        results["questions"]["q3"] = {"earned": 5, "possible": 5, "comment": "Correctly identified at least 3 missing fields."}
        results["earned_points"] += 5
    elif field_count >= 2:
        results["questions"]["q3"] = {"earned": 3, "possible": 5, "comment": f"Identified {field_count} missing fields correctly."}
        results["earned_points"] += 3
    elif field_count >= 1:
        results["questions"]["q3"] = {"earned": 1, "possible": 5, "comment": "Identified only 1 missing field correctly."}
        results["earned_points"] += 1
    else:
        results["questions"]["q3"] = {"earned": 0, "possible": 5, "comment": "Did not identify any missing fields correctly."}
    
    # Q4: Proper document retention period
    q4_sub = submission.get("q4", "").strip()
    q4_key = answer_key.get("q4", "").strip()
    
    if q4_sub == q4_key:
        results["questions"]["q4"] = {"earned": 5, "possible": 5, "comment": "Correct document retention period."}
        results["earned_points"] += 5
    else:
        results["questions"]["q4"] = {"earned": 0, "possible": 5, "comment": f"Incorrect. Expected {answer_key.get('q4')}"}
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission and generate results."""
    results = {
        "overall_score": 0,
        "total_points": 100,
        "earned_points": 0,
        "sections": {}
    }
    
    # Evaluate each section
    section_evaluators = {
        "section1": evaluate_section1,
        "section2": evaluate_section2,
        "section3": evaluate_section3,
        "section4": evaluate_section4,
        "section5": evaluate_section5
    }
    
    for section_name, evaluator in section_evaluators.items():
        sub_section = submission.get(section_name, {})
        key_section = answer_key.get(section_name, {})
        
        section_results = evaluator(sub_section, key_section)
        results["sections"][section_name] = section_results
        results["earned_points"] += section_results["earned_points"]
    
    # Calculate overall score as a percentage
    if results["total_points"] > 0:
        results["overall_score"] = round((results["earned_points"] / results["total_points"]) * 100, 2)
    
    return results

def main():
    """Main function to evaluate the test submission."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load files
    submission_path = os.path.join(script_dir, 'test_submission.json')
    answer_key_path = os.path.join(script_dir, 'answer_key.json')
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    results_path = os.path.join(script_dir, 'test_results.json')
    with open(results_path, 'w') as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to {results_path}")
    print(f"Overall score: {results['overall_score']}%")

if __name__ == "__main__":
    main()