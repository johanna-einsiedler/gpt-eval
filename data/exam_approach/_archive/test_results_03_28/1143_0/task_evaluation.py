import json
import os
import math

def load_json(filename):
    """Load and return JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def evaluate_section1(submission, answer_key):
    """Evaluate Section 1: Knowledge Assessment (25 points)"""
    score = 0
    results = {"total_points": 25, "points_earned": 0, "questions": {}}
    
    # Q1: Definitions (10 points - 2 points per term)
    results["questions"]["q1"] = {"possible": 10, "earned": 0, "feedback": {}}
    for term in ["a", "b", "c", "d", "e"]:
        if term in submission["section1"]["q1"] and term in answer_key["section1"]["q1"]:
            # Check if key terms are in the definition
            sub_def = submission["section1"]["q1"][term].lower()
            key_points = answer_key["section1"]["q1"][term].lower()
            
            # Simple keyword matching approach
            if term == "a":  # Blanket Purchase Order
                if "multiple" in sub_def and ("period" in sub_def or "long" in sub_def):
                    results["questions"]["q1"]["earned"] += 2
                    results["questions"]["q1"]["feedback"][term] = "Correct"
                else:
                    results["questions"]["q1"]["feedback"][term] = "Missing key concepts: multiple purchases over a period"
            elif term == "b":  # RFP
                if "proposal" in sub_def and ("detailed" in sub_def or "complex" in sub_def):
                    results["questions"]["q1"]["earned"] += 2
                    results["questions"]["q1"]["feedback"][term] = "Correct"
                else:
                    results["questions"]["q1"]["feedback"][term] = "Missing key concepts: detailed proposals for complex requirements"
            elif term == "c":  # Terms and Conditions
                if "legal" in sub_def and ("rights" in sub_def or "obligations" in sub_def):
                    results["questions"]["q1"]["earned"] += 2
                    results["questions"]["q1"]["feedback"][term] = "Correct"
                else:
                    results["questions"]["q1"]["feedback"][term] = "Missing key concepts: legal provisions defining rights/obligations"
            elif term == "d":  # FOB
                if ("ownership" in sub_def or "transfer" in sub_def) and "shipping" in sub_def:
                    results["questions"]["q1"]["earned"] += 2
                    results["questions"]["q1"]["feedback"][term] = "Correct"
                else:
                    results["questions"]["q1"]["feedback"][term] = "Missing key concepts: ownership transfer and shipping responsibility"
            elif term == "e":  # Net 30
                if "30" in sub_def and "payment" in sub_def and ("days" in sub_def or "due" in sub_def):
                    results["questions"]["q1"]["earned"] += 2
                    results["questions"]["q1"]["feedback"][term] = "Correct"
                else:
                    results["questions"]["q1"]["feedback"][term] = "Missing key concepts: payment due in 30 days"
        else:
            results["questions"]["q1"]["feedback"][term] = "Missing answer"
    
    # Q2-Q5: Multiple choice and True/False (15 points)
    mc_questions = {
        "q2": {"possible": 3, "answer": "b"},
        "q3": {"possible": 3, "answer": "c"},
        "q4": {"possible": 3, "answer": True},
        "q5": {"possible": 6, "answer": "c"}
    }
    
    for q, details in mc_questions.items():
        results["questions"][q] = {"possible": details["possible"], "earned": 0}
        if q in submission["section1"] and submission["section1"][q] == answer_key["section1"][q]:
            results["questions"][q]["earned"] = details["possible"]
            results["questions"][q]["feedback"] = "Correct"
        else:
            results["questions"][q]["feedback"] = f"Incorrect. Expected: {details['answer']}"
    
    # Calculate total section score
    for q in results["questions"]:
        results["points_earned"] += results["questions"][q]["earned"]
    
    return results

def evaluate_section2(submission, answer_key):
    """Evaluate Section 2: Purchase Order Preparation (25 points)"""
    results = {"total_points": 25, "points_earned": 0, "questions": {}}
    
    # Q1: Essential elements (5 points - 1 point per element)
    results["questions"]["q1"] = {"possible": 5, "earned": 0, "feedback": ""}
    correct_elements = set([element.lower() for element in answer_key["section2"]["q1"]])
    alternative_elements = {
        "vendor information", "delivery information", "item descriptions", "pricing", 
        "payment terms", "po number", "authorization", "ship-to address", 
        "bill-to address", "buyer information", "date of issue", "terms and conditions"
    }
    
    if "q1" in submission["section2"]:
        submitted_elements = [element.lower() for element in submission["section2"]["q1"]]
        count = 0
        for element in submitted_elements:
            # Check if element is in the correct list or acceptable alternatives
            if element in correct_elements or any(alt in element for alt in alternative_elements):
                count += 1
        
        # Cap at 5 points maximum
        results["questions"]["q1"]["earned"] = min(count, 5)
        if results["questions"]["q1"]["earned"] == 5:
            results["questions"]["q1"]["feedback"] = "All elements correctly identified"
        else:
            results["questions"]["q1"]["feedback"] = f"Identified {results['questions']['q1']['earned']} out of 5 required elements"
    else:
        results["questions"]["q1"]["feedback"] = "Missing answer"
    
    # Q2: Calculations (6 points - 2 points per calculation)
    results["questions"]["q2"] = {"possible": 6, "earned": 0, "feedback": {}}
    
    if "q2" in submission["section2"]:
        for part in ["a", "b", "c"]:
            if part in submission["section2"]["q2"] and part in answer_key["section2"]["q2"]:
                # Allow for minor rounding differences
                submitted = float(submission["section2"]["q2"][part])
                expected = float(answer_key["section2"]["q2"][part])
                
                if abs(submitted - expected) < 0.1:  # Tolerance for rounding
                    results["questions"]["q2"]["earned"] += 2
                    results["questions"]["q2"]["feedback"][part] = "Correct"
                else:
                    results["questions"]["q2"]["feedback"][part] = f"Incorrect. Expected: {expected}"
            else:
                results["questions"]["q2"]["feedback"][part] = "Missing answer"
    else:
        results["questions"]["q2"]["feedback"] = "Missing all calculations"
    
    # Q3: Categorization (5 points - 1 point per categorization)
    results["questions"]["q3"] = {"possible": 5, "earned": 0, "feedback": {}}
    
    if "q3" in submission["section2"]:
        for part in ["a", "b", "c", "d", "e"]:
            if part in submission["section2"]["q3"] and part in answer_key["section2"]["q3"]:
                if submission["section2"]["q3"][part] == answer_key["section2"]["q3"][part]:
                    results["questions"]["q3"]["earned"] += 1
                    results["questions"]["q3"]["feedback"][part] = "Correct"
                else:
                    results["questions"]["q3"]["feedback"][part] = f"Incorrect. Expected: {answer_key['section2']['q3'][part]}"
            else:
                results["questions"]["q3"]["feedback"][part] = "Missing answer"
    else:
        results["questions"]["q3"]["feedback"] = "Missing all categorizations"
    
    # Q4: Total calculation (5 points)
    results["questions"]["q4"] = {"possible": 5, "earned": 0, "feedback": ""}
    
    if "q4" in submission["section2"]:
        submitted = float(submission["section2"]["q4"])
        expected = float(answer_key["section2"]["q4"])
        
        if abs(submitted - expected) < 0.1:  # Tolerance for rounding
            results["questions"]["q4"]["earned"] = 5
            results["questions"]["q4"]["feedback"] = "Correct"
        else:
            results["questions"]["q4"]["feedback"] = f"Incorrect. Expected: {expected}"
    else:
        results["questions"]["q4"]["feedback"] = "Missing answer"
    
    # Q5: Multiple choice (4 points)
    results["questions"]["q5"] = {"possible": 4, "earned": 0, "feedback": ""}
    
    if "q5" in submission["section2"] and submission["section2"]["q5"] == answer_key["section2"]["q5"]:
        results["questions"]["q5"]["earned"] = 4
        results["questions"]["q5"]["feedback"] = "Correct"
    else:
        results["questions"]["q5"]["feedback"] = f"Incorrect. Expected: {answer_key['section2']['q5']}"
    
    # Calculate total section score
    for q in results["questions"]:
        results["points_earned"] += results["questions"][q]["earned"]
    
    return results

def evaluate_section3(submission, answer_key):
    """Evaluate Section 3: Bid Solicitation (25 points)"""
    results = {"total_points": 25, "points_earned": 0, "questions": {}}
    
    # Q1: Key components (4 points - 1 point per component)
    results["questions"]["q1"] = {"possible": 4, "earned": 0, "feedback": ""}
    acceptable_components = {
        "scope of work", "specifications", "evaluation criteria", "timeline", "submission requirements",
        "terms and conditions", "background information", "pricing format", "contract terms",
        "qualification requirements"
    }
    
    if "q1" in submission["section3"]:
        count = 0
        for component in submission["section3"]["q1"]:
            # Check if any acceptable component is part of the answer
            if any(acc.lower() in component.lower() for acc in acceptable_components):
                count += 1
        
        # Cap at 4 points maximum
        results["questions"]["q1"]["earned"] = min(count, 4)
        if results["questions"]["q1"]["earned"] == 4:
            results["questions"]["q1"]["feedback"] = "All components correctly identified"
        else:
            results["questions"]["q1"]["feedback"] = f"Identified {results['questions']['q1']['earned']} out of 4 required components"
    else:
        results["questions"]["q1"]["feedback"] = "Missing answer"
    
    # Q2: Vendor selection (7 points - 2 for selection, 5 for justification)
    results["questions"]["q2"] = {"possible": 7, "earned": 0, "feedback": {}}
    
    if "q2" in submission["section3"]:
        # Check vendor selection (2 points)
        if "selectedVendor" in submission["section3"]["q2"]:
            selected_vendor = submission["section3"]["q2"]["selectedVendor"]
            if selected_vendor == answer_key["section3"]["q2"]["selectedVendor"]:
                results["questions"]["q2"]["earned"] += 2
                results["questions"]["q2"]["feedback"]["selectedVendor"] = "Correct"
            else:
                results["questions"]["q2"]["feedback"]["selectedVendor"] = f"Incorrect. Expected: {answer_key['section3']['q2']['selectedVendor']}"
        else:
            results["questions"]["q2"]["feedback"]["selectedVendor"] = "Missing vendor selection"
        
        # Check justification (5 points)
        if "justification" in submission["section3"]["q2"]:
            justification = submission["section3"]["q2"]["justification"].lower()
            
            # Award points based on key elements in the justification
            points = 0
            if "warranty" in justification and ("longest" in justification or "3" in justification):
                points += 3  # Mentioning warranty as primary criterion
            if "primary" in justification or "criterion" in justification or "priority" in justification:
                points += 1  # Explicitly mentioning prioritization
            if ("price" in justification and "delivery" in justification) or "trade" in justification:
                points += 1  # Acknowledging trade-offs
            
            results["questions"]["q2"]["earned"] += points
            
            if points == 5:
                results["questions"]["q2"]["feedback"]["justification"] = "Excellent justification"
            elif points >= 3:
                results["questions"]["q2"]["feedback"]["justification"] = "Good justification, but missing some elements"
            else:
                results["questions"]["q2"]["feedback"]["justification"] = "Justification lacks key reasoning elements"
        else:
            results["questions"]["q2"]["feedback"]["justification"] = "Missing justification"
    else:
        results["questions"]["q2"]["feedback"] = "Missing entire answer"
    
    # Q3: Multiple choice (3 points)
    results["questions"]["q3"] = {"possible": 3, "earned": 0, "feedback": ""}
    
    if "q3" in submission["section3"] and submission["section3"]["q3"] == answer_key["section3"]["q3"]:
        results["questions"]["q3"]["earned"] = 3
        results["questions"]["q3"]["feedback"] = "Correct"
    else:
        results["questions"]["q3"]["feedback"] = f"Incorrect. Expected: {answer_key['section3']['q3']}"
    
    # Q4: True/False (4 points)
    results["questions"]["q4"] = {"possible": 4, "earned": 0, "feedback": ""}
    
    if "q4" in submission["section3"] and submission["section3"]["q4"] == answer_key["section3"]["q4"]:
        results["questions"]["q4"]["earned"] = 4
        results["questions"]["q4"]["feedback"] = "Correct"
    else:
        results["questions"]["q4"]["feedback"] = f"Incorrect. Expected: {answer_key['section3']['q4']}"
    
    # Q5: Qualification criteria (7 points - ~2.33 points per criterion)
    results["questions"]["q5"] = {"possible": 7, "earned": 0, "feedback": ""}
    acceptable_criteria = {
        "experience", "certification", "license", "financial stability", "bonding", 
        "safety", "references", "insurance", "qualifications", "project management"
    }
    
    if "q5" in submission["section3"]:
        count = 0
        for criterion in submission["section3"]["q5"]:
            # Check if any acceptable criterion is part of the answer
            if any(acc.lower() in criterion.lower() for acc in acceptable_criteria):
                count += 1
        
        # Award ~2.33 points per correct criterion, rounded to nearest point
        points_per_criterion = 7 / 3
        results["questions"]["q5"]["earned"] = round(count * points_per_criterion)
        
        if count == 3:
            results["questions"]["q5"]["feedback"] = "All criteria correctly identified"
        else:
            results["questions"]["q5"]["feedback"] = f"Identified {count} out of 3 required criteria"
    else:
        results["questions"]["q5"]["feedback"] = "Missing answer"
    
    # Calculate total section score
    for q in results["questions"]:
        results["points_earned"] += results["questions"][q]["earned"]
    
    return results

def evaluate_section4(submission, answer_key):
    """Evaluate Section 4: Requisition Review (25 points)"""
    results = {"total_points": 25, "points_earned": 0, "questions": {}}
    
    # Q1: Key elements (8 points - 2 points per element)
    results["questions"]["q1"] = {"possible": 8, "earned": 0, "feedback": ""}
    acceptable_elements = {
        "budget", "authorization", "approval", "specifications", "completeness",
        "justification", "necessity", "coding", "compliance", "vendor selection",
        "price", "delivery", "timeline"
    }
    
    if "q1" in submission["section4"]:
        count = 0
        for element in submission["section4"]["q1"]:
            # Check if any acceptable element is part of the answer
            if any(acc.lower() in element.lower() for acc in acceptable_elements):
                count += 1
        
        # Cap at 4 elements maximum (2 points each)
        results["questions"]["q1"]["earned"] = min(count, 4) * 2
        if count >= 4:
            results["questions"]["q1"]["feedback"] = "All elements correctly identified"
        else:
            results["questions"]["q1"]["feedback"] = f"Identified {count} out of 4 required elements"
    else:
        results["questions"]["q1"]["feedback"] = "Missing answer"
    
    # Q2: Multiple choice (5 points)
    results["questions"]["q2"] = {"possible": 5, "earned": 0, "feedback": ""}
    
    if "q2" in submission["section4"] and submission["section4"]["q2"] == answer_key["section4"]["q2"]:
        results["questions"]["q2"]["earned"] = 5
        results["questions"]["q2"]["feedback"] = "Correct"
    else:
        results["questions"]["q2"]["feedback"] = f"Incorrect. Expected: {answer_key['section4']['q2']}"
    
    # Q3: Calculation check (5 points - 2 for correctness check, 3 for calculation)
    results["questions"]["q3"] = {"possible": 5, "earned": 0, "feedback": {}}
    
    if "q3" in submission["section4"]:
        # Check isCorrect boolean (2 points)
        if "isCorrect" in submission["section4"]["q3"]:
            if submission["section4"]["q3"]["isCorrect"] == answer_key["section4"]["q3"]["isCorrect"]:
                results["questions"]["q3"]["earned"] += 2
                results["questions"]["q3"]["feedback"]["isCorrect"] = "Correct"
            else:
                results["questions"]["q3"]["feedback"]["isCorrect"] = f"Incorrect. Expected: {answer_key['section4']['q3']['isCorrect']}"
        else:
            results["questions"]["q3"]["feedback"]["isCorrect"] = "Missing correctness check"
        
        # Check calculation (3 points)
        if "correctTotal" in submission["section4"]["q3"]:
            submitted = float(submission["section4"]["q3"]["correctTotal"])
            expected = float(answer_key["section4"]["q3"]["correctTotal"])
            
            if abs(submitted - expected) < 0.1:  # Tolerance for rounding
                results["questions"]["q3"]["earned"] += 3
                results["questions"]["q3"]["feedback"]["correctTotal"] = "Correct"
            else:
                results["questions"]["q3"]["feedback"]["correctTotal"] = f"Incorrect. Expected: {expected}"
        else:
            results["questions"]["q3"]["feedback"]["correctTotal"] = "Missing calculation"
    else:
        results["questions"]["q3"]["feedback"] = "Missing entire answer"
    
    # Q4: Multiple choice (4 points)
    results["questions"]["q4"] = {"possible": 4, "earned": 0, "feedback": ""}
    
    if "q4" in submission["section4"] and submission["section4"]["q4"] == answer_key["section4"]["q4"]:
        results["questions"]["q4"]["earned"] = 4
        results["questions"]["q4"]["feedback"] = "Correct"
    else:
        results["questions"]["q4"]["feedback"] = f"Incorrect. Expected: {answer_key['section4']['q4']}"
    
    # Q5: True/False (3 points)
    results["questions"]["q5"] = {"possible": 3, "earned": 0, "feedback": ""}
    
    if "q5" in submission["section4"] and submission["section4"]["q5"] == answer_key["section4"]["q5"]:
        results["questions"]["q5"]["earned"] = 3
        results["questions"]["q5"]["feedback"] = "Correct"
    else:
        results["questions"]["q5"]["feedback"] = f"Incorrect. Expected: {answer_key['section4']['q5']}"
    
    # Calculate total section score
    for q in results["questions"]:
        results["points_earned"] += results["questions"][q]["earned"]
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission and calculate overall score."""
    results = {
        "candidateID": submission.get("candidateID", "Unknown"),
        "section1": evaluate_section1(submission, answer_key),
        "section2": evaluate_section2(submission, answer_key),
        "section3": evaluate_section3(submission, answer_key),
        "section4": evaluate_section4(submission, answer_key)
    }
    
    # Calculate total score
    total_possible = 0
    total_earned = 0
    for section in ["section1", "section2", "section3", "section4"]:
        total_possible += results[section]["total_points"]
        total_earned += results[section]["points_earned"]
    
    # Calculate percentage score
    results["overall_score"] = round((total_earned / total_possible) * 100, 2)
    
    # Add pass/fail status
    results["passed"] = results["overall_score"] >= 70
    
    # Add section summary
    results["section_summary"] = {
        "section1": {
            "name": "Knowledge Assessment",
            "score": results["section1"]["points_earned"],
            "possible": results["section1"]["total_points"],
            "percentage": round((results["section1"]["points_earned"] / results["section1"]["total_points"]) * 100, 2)
        },
        "section2": {
            "name": "Purchase Order Preparation",
            "score": results["section2"]["points_earned"],
            "possible": results["section2"]["total_points"],
            "percentage": round((results["section2"]["points_earned"] / results["section2"]["total_points"]) * 100, 2)
        },
        "section3": {
            "name": "Bid Solicitation",
            "score": results["section3"]["points_earned"],
            "possible": results["section3"]["total_points"],
            "percentage": round((results["section3"]["points_earned"] / results["section3"]["total_points"]) * 100, 2)
        },
        "section4": {
            "name": "Requisition Review",
            "score": results["section4"]["points_earned"],
            "possible": results["section4"]["total_points"],
            "percentage": round((results["section4"]["points_earned"] / results["section4"]["total_points"]) * 100, 2)
        }
    }
    
    return results

def main():
    # Load files
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json.")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()