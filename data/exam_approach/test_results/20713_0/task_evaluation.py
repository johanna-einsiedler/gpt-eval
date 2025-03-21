#!/usr/bin/env python3
import json
import re
import math

def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def parse_dollar_amount(value):
    """Extract dollar amount from string and convert to float"""
    if isinstance(value, str):
        match = re.search(r'\$?(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
    return None

def parse_percentage(value):
    """Extract percentage from string and convert to float"""
    if isinstance(value, str):
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', value)
        if match:
            return float(match.group(1))
    return None

def is_close_enough(value1, value2, tolerance):
    """Check if values are within tolerance of each other"""
    return abs(value1 - value2) <= tolerance

def is_dollar_match(candidate_answer, correct_answer, tolerance=0.02):
    """Check if dollar amounts match within tolerance"""
    candidate_value = parse_dollar_amount(candidate_answer)
    correct_value = parse_dollar_amount(correct_answer)
    
    if candidate_value is None or correct_value is None:
        return False
    
    return is_close_enough(candidate_value, correct_value, tolerance)

def is_percentage_match(candidate_answer, correct_answer, tolerance=0.2):
    """Check if percentages match within tolerance"""
    candidate_value = parse_percentage(candidate_answer)
    correct_value = parse_percentage(correct_answer)
    
    if candidate_value is None or correct_value is None:
        return False
    
    return is_close_enough(candidate_value, correct_value, tolerance)

def evaluate_section1(candidate, answer_key):
    results = {"points": 0, "max_points": 3, "questions": {}}
    
    # Question 1
    q1_correct = is_dollar_match(candidate["section1"]["q1"]["answer"], answer_key["section1"]["q1"]["answer"])
    results["questions"]["q1"] = {
        "correct": q1_correct,
        "points_earned": 1 if q1_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section1"]["q1"]["answer"],
        "correct_answer": answer_key["section1"]["q1"]["answer"]
    }
    
    # Question 2
    q2_correct = is_dollar_match(candidate["section1"]["q2"]["answer"], answer_key["section1"]["q2"]["answer"])
    results["questions"]["q2"] = {
        "correct": q2_correct,
        "points_earned": 1 if q2_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section1"]["q2"]["answer"],
        "correct_answer": answer_key["section1"]["q2"]["answer"]
    }
    
    # Question 3
    q3_correct = is_dollar_match(candidate["section1"]["q3"]["answer"], answer_key["section1"]["q3"]["answer"])
    results["questions"]["q3"] = {
        "correct": q3_correct,
        "points_earned": 1 if q3_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section1"]["q3"]["answer"],
        "correct_answer": answer_key["section1"]["q3"]["answer"]
    }
    
    # Calculate total points
    results["points"] = sum(q["points_earned"] for q in results["questions"].values())
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_section2(candidate, answer_key):
    results = {"points": 0, "max_points": 3, "questions": {}}
    
    # Question 1
    q1_correct = is_percentage_match(candidate["section2"]["q1"]["answer"], answer_key["section2"]["q1"]["answer"])
    results["questions"]["q1"] = {
        "correct": q1_correct,
        "points_earned": 1 if q1_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section2"]["q1"]["answer"],
        "correct_answer": answer_key["section2"]["q1"]["answer"]
    }
    
    # Question 2
    try:
        price_correct = is_dollar_match(
            candidate["section2"]["q2"]["answer"]["price"], 
            answer_key["section2"]["q2"]["answer"]["price"]
        )
        margin_correct = is_percentage_match(
            candidate["section2"]["q2"]["answer"]["margin"], 
            answer_key["section2"]["q2"]["answer"]["margin"]
        )
        q2_correct = price_correct and margin_correct
        q2_points = 1 if q2_correct else (0.5 if (price_correct or margin_correct) else 0)
    except (KeyError, TypeError):
        q2_correct = False
        q2_points = 0
    
    results["questions"]["q2"] = {
        "correct": q2_correct,
        "points_earned": q2_points,
        "max_points": 1,
        "candidate_answer": candidate["section2"]["q2"]["answer"] if "answer" in candidate["section2"]["q2"] else "Invalid format",
        "correct_answer": answer_key["section2"]["q2"]["answer"]
    }
    
    # Question 3
    q3_correct = is_percentage_match(candidate["section2"]["q3"]["answer"], answer_key["section2"]["q3"]["answer"])
    results["questions"]["q3"] = {
        "correct": q3_correct,
        "points_earned": 1 if q3_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section2"]["q3"]["answer"],
        "correct_answer": answer_key["section2"]["q3"]["answer"]
    }
    
    # Calculate total points
    results["points"] = sum(q["points_earned"] for q in results["questions"].values())
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_section3(candidate, answer_key):
    results = {"points": 0, "max_points": 2, "questions": {}}
    
    # Question 1
    try:
        candidate_q1 = candidate["section3"]["q1"]["answer"].lower()
        answer_key_q1 = answer_key["section3"]["q1"]["answer"].lower()
        
        # Check if Yes/No part matches
        yes_no_match = ("yes" in candidate_q1 and "yes" in answer_key_q1) or ("no" in candidate_q1 and "no" in answer_key_q1)
        
        # If "No", also check the dollar amount
        if "no" in answer_key_q1:
            amount_match = is_dollar_match(candidate_q1, answer_key_q1)
            q1_correct = yes_no_match and amount_match
        else:
            q1_correct = yes_no_match
    except (KeyError, AttributeError):
        q1_correct = False
    
    results["questions"]["q1"] = {
        "correct": q1_correct,
        "points_earned": 1 if q1_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section3"]["q1"]["answer"],
        "correct_answer": answer_key["section3"]["q1"]["answer"]
    }
    
    # Question 2
    try:
        candidate_q2 = candidate["section3"]["q2"]["answer"].lower()
        answer_key_q2 = answer_key["section3"]["q2"]["answer"].lower()
        
        # Check if Yes/No part matches
        yes_no_match = ("yes" in candidate_q2 and "yes" in answer_key_q2) or ("no" in candidate_q2 and "no" in answer_key_q2)
        
        # Check price range if needed
        if "-" in answer_key_q2:
            # Extract price range
            correct_range = re.search(r'\$?(\d+\.\d+)-\$?(\d+\.\d+)', answer_key_q2)
            candidate_range = re.search(r'\$?(\d+\.\d+)-\$?(\d+\.\d+)', candidate_q2)
            
            if correct_range and candidate_range:
                correct_low = float(correct_range.group(1))
                correct_high = float(correct_range.group(2))
                candidate_low = float(candidate_range.group(1))
                candidate_high = float(candidate_range.group(2))
                
                range_match = (is_close_enough(candidate_low, correct_low, 0.02) and 
                              is_close_enough(candidate_high, correct_high, 0.02))
                q2_correct = yes_no_match and range_match
            else:
                q2_correct = False
        else:
            q2_correct = yes_no_match
    except (KeyError, AttributeError):
        q2_correct = False
    
    results["questions"]["q2"] = {
        "correct": q2_correct,
        "points_earned": 1 if q2_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section3"]["q2"]["answer"],
        "correct_answer": answer_key["section3"]["q2"]["answer"]
    }
    
    # Calculate total points
    results["points"] = sum(q["points_earned"] for q in results["questions"].values())
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_section4(candidate, answer_key):
    results = {"points": 0, "max_points": 2, "questions": {}}
    
    # Question 1
    q1_correct = is_dollar_match(candidate["section4"]["q1"]["answer"], answer_key["section4"]["q1"]["answer"])
    results["questions"]["q1"] = {
        "correct": q1_correct,
        "points_earned": 1 if q1_correct else 0,
        "max_points": 1,
        "candidate_answer": candidate["section4"]["q1"]["answer"],
        "correct_answer": answer_key["section4"]["q1"]["answer"]
    }
    
    # Question 2
    try:
        current_margin_correct = is_percentage_match(
            candidate["section4"]["q2"]["answer"]["current_margin"], 
            answer_key["section4"]["q2"]["answer"]["current_margin"]
        )
        recommended_markup_correct = is_percentage_match(
            candidate["section4"]["q2"]["answer"]["recommended_markup"], 
            answer_key["section4"]["q2"]["answer"]["recommended_markup"]
        )
        q2_correct = current_margin_correct and recommended_markup_correct
        q2_points = 1 if q2_correct else (0.5 if (current_margin_correct or recommended_markup_correct) else 0)
    except (KeyError, TypeError):
        q2_correct = False
        q2_points = 0
    
    results["questions"]["q2"] = {
        "correct": q2_correct,
        "points_earned": q2_points,
        "max_points": 1,
        "candidate_answer": candidate["section4"]["q2"]["answer"] if "answer" in candidate["section4"]["q2"] else "Invalid format",
        "correct_answer": answer_key["section4"]["q2"]["answer"]
    }
    
    # Calculate total points
    results["points"] = sum(q["points_earned"] for q in results["questions"].values())
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_section5(candidate, answer_key):
    results = {"points": 0, "max_points": 5, "questions": {}}
    
    # Question 1 (2 points)
    try:
        # Extract Option A/B and check if it matches
        candidate_option = re.search(r'Option\s+([AB])', candidate["section5"]["q1"]["answer"], re.IGNORECASE)
        correct_option = re.search(r'Option\s+([AB])', answer_key["section5"]["q1"]["answer"], re.IGNORECASE)
        
        if candidate_option and correct_option:
            option_match = candidate_option.group(1).upper() == correct_option.group(1).upper()
        else:
            option_match = False
        
        # Check if profit calculations are reasonably close
        candidate_profits = re.findall(r'\$(\d+)', candidate["section5"]["q1"]["answer"])
        correct_profits = re.findall(r'\$(\d+)', answer_key["section5"]["q1"]["answer"])
        
        if len(candidate_profits) >= 2 and len(correct_profits) >= 2:
            # Convert to integers for comparison
            candidate_profits = [int(p) for p in candidate_profits]
            correct_profits = [int(p) for p in correct_profits]
            
            # Check if the numbers are within reasonable range (±5%)
            profits_match = all(
                is_close_enough(candidate_val, correct_val, 0.05 * correct_val)
                for candidate_val, correct_val in zip(candidate_profits, correct_profits)
            )
        else:
            profits_match = False
        
        # Full points if option and profits match, partial if just option matches
        if option_match and profits_match:
            q1_points = 2
            q1_correct = True
        elif option_match:
            q1_points = 1
            q1_correct = False
        else:
            q1_points = 0
            q1_correct = False
            
    except (KeyError, AttributeError):
        q1_correct = False
        q1_points = 0
    
    results["questions"]["q1"] = {
        "correct": q1_correct,
        "points_earned": q1_points,
        "max_points": 2,
        "candidate_answer": candidate["section5"]["q1"]["answer"],
        "correct_answer": answer_key["section5"]["q1"]["answer"]
    }
    
    # Question 2 (3 points)
    try:
        # Extract vendor choice
        candidate_vendor = re.search(r'Vendor\s+([AB])', candidate["section5"]["q2"]["answer"], re.IGNORECASE)
        correct_vendor = re.search(r'Vendor\s+([AB])', answer_key["section5"]["q2"]["answer"], re.IGNORECASE)
        
        if candidate_vendor and correct_vendor:
            vendor_match = candidate_vendor.group(1).upper() == correct_vendor.group(1).upper()
        else:
            vendor_match = False
        
        # Check reasoning quality - this is subjective, so we'll do a basic check
        candidate_reasoning = candidate["section5"]["q2"]["reasoning"].lower()
        reasoning_quality = 0
        
        # Check for key concepts in reasoning
        if "inventory" in candidate_reasoning:
            reasoning_quality += 1
        if "cash flow" in candidate_reasoning:
            reasoning_quality += 1
        if "discount" in candidate_reasoning or "6%" in candidate_reasoning:
            reasoning_quality += 1
        
        # Determine points based on vendor match and reasoning quality
        if vendor_match:
            if reasoning_quality >= 2:
                q2_points = 3  # Full points
                q2_correct = True
            elif reasoning_quality == 1:
                q2_points = 2  # Partial points
                q2_correct = False
            else:
                q2_points = 1  # Minimal points - right answer, poor reasoning
                q2_correct = False
        else:
            if reasoning_quality >= 2:
                q2_points = 1  # Wrong vendor but good reasoning
                q2_correct = False
            else:
                q2_points = 0  # Wrong vendor, poor reasoning
                q2_correct = False
                
    except (KeyError, AttributeError):
        q2_correct = False
        q2_points = 0
    
    results["questions"]["q2"] = {
        "correct": q2_correct,
        "points_earned": q2_points,
        "max_points": 3,
        "candidate_answer": candidate["section5"]["q2"]["answer"],
        "correct_answer": answer_key["section5"]["q2"]["answer"]
    }
    
    # Calculate total points
    results["points"] = sum(q["points_earned"] for q in results["questions"].values())
    results["percentage"] = (results["points"] / results["max_points"]) * 100
    
    return results

def evaluate_test(candidate_submission, answer_key):
    results = {
        "section1": evaluate_section1(candidate_submission, answer_key),
        "section2": evaluate_section2(candidate_submission, answer_key),
        "section3": evaluate_section3(candidate_submission, answer_key),
        "section4": evaluate_section4(candidate_submission, answer_key),
        "section5": evaluate_section5(candidate_submission, answer_key)
    }
    
    # Calculate overall score
    total_points = sum(section["points"] for section in results.values())
    max_points = sum(section["max_points"] for section in results.values())
    overall_percentage = (total_points / max_points) * 100
    
    # Add overall results
    results["overall_score"] = round(overall_percentage, 1)
    results["total_points"] = total_points
    results["max_points"] = max_points
    
    # Check if candidate passed (70% overall, 60% in each section)
    section_pass = all(section["percentage"] >= 60 for section in results.values() if "percentage" in section)
    overall_pass = overall_percentage >= 70
    results["passed"] = section_pass and overall_pass
    
    # Add candidate ID if available
    if "candidate_id" in candidate_submission:
        results["candidate_id"] = candidate_submission["candidate_id"]
    
    return results

def main():
    # Load the files
    candidate_submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not candidate_submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate the test
    results = evaluate_test(candidate_submission, answer_key)
    
    # Save results
    save_json(results, "test_results.json")

if __name__ == "__main__":
    main()