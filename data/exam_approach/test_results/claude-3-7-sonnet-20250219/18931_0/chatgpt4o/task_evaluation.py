#!/usr/bin/env python3
import json
import sys
import re
from datetime import datetime

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_required_elements(letter, donor_type):
    points = 0
    max_points = 15
    
    # Check date format (1 point)
    if re.search(r'\d{4}-\d{2}-\d{2}', letter):
        points += 1
    
    # Check for proper salutation (2 points)
    if re.search(r'Dear\s+\w+,', letter):
        points += 2
    
    # Check for donation acknowledgment (2 points)
    if re.search(r'(gift|donation|contribution)\s+of\s+\$[\d,.]+', letter):
        points += 2
    
    # Check for program reference (2 points)
    if any(program in letter for program in ["Youth Programs", "Education Program", "Medical Research", "General Fund", "Community Outreach"]):
        points += 2
    
    # Check for impact statement (2 points)
    impact_phrases = [
        "help provide", "continue to offer", "supports our", "enables us", 
        "directly support", "safe spaces", "learning materials", "educational resources"
    ]
    if any(phrase in letter for phrase in impact_phrases):
        points += 2
    
    # Check for tax language (2 points)
    if "tax-deductible to the extent allowed by law" in letter and "No goods or services were provided" in letter:
        points += 2
    
    # Check for closing/signature (2 points)
    closing_phrases = ["With deepest gratitude", "With sincere appreciation", "Thank you for your generosity", "With heartfelt thanks"]
    if any(phrase in letter for phrase in closing_phrases) and "[Your" in letter:
        points += 2
    
    # Check for proper formatting (2 points)
    if letter.count('\n') >= 10:  # Simple check for proper paragraph breaks
        points += 2
    
    return points, max_points

def evaluate_personalization(letter, donor_id, donor_type):
    points = 0
    max_points = 10
    
    # Donor-specific personalization (5 points)
    if donor_id == "donor_4_letter":
        if "teenage children" in letter and "volunteer" in letter:
            points += 5
        elif "children" in letter:
            points += 3
    elif donor_id == "donor_7_letter":
        if "teacher" in letter and "education" in letter.lower():
            points += 5
        elif "teacher" in letter or "education" in letter.lower():
            points += 3
    elif donor_id == "donor_12_letter":
        if "former educator" in letter and "educational equity" in letter:
            points += 5
        elif "educator" in letter:
            points += 3
    
    # Donor-type language (5 points)
    if donor_type == "first-time" and any(phrase in letter for phrase in ["welcome you", "first gift", "new supporter"]):
        points += 5
    elif donor_type == "recurring" and any(phrase in letter for phrase in ["continued support", "ongoing generosity", "loyal supporter"]):
        points += 5
    elif donor_type == "major" and any(phrase in letter for phrase in ["leadership gift", "transformative", "inspiring example"]):
        points += 5
    
    return points, max_points

def evaluate_writing_quality(letter):
    points = 0
    max_points = 8
    
    # Appropriate tone and professionalism (4 points)
    professional_phrases = [
        "thank you", "grateful", "appreciate", "support", "mission", 
        "impact", "community", "difference", "generous"
    ]
    professionalism_score = sum(1 for phrase in professional_phrases if phrase in letter.lower())
    points += min(4, professionalism_score)
    
    # Clarity and effectiveness (4 points)
    # Check for well-structured paragraphs and clear communication
    paragraphs = [p for p in letter.split('\n\n') if p.strip()]
    if len(paragraphs) >= 4:  # Has multiple well-defined paragraphs
        points += 2
    
    # Check for varied sentence structure
    sentences = re.split(r'[.!?]+', letter)
    if len(sentences) >= 8:
        points += 2
    
    return points, max_points

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "letters": {}
    }
    
    # Define donor types
    donor_types = {
        "donor_4_letter": "first-time",
        "donor_7_letter": "recurring",
        "donor_12_letter": "major"
    }
    
    # Evaluate each letter
    total_points = 0
    
    for donor_id in ["donor_4_letter", "donor_7_letter", "donor_12_letter"]:
        letter_results = {"points": 0, "max_points": 33, "feedback": []}
        
        if donor_id not in submission:
            letter_results["feedback"].append(f"Missing {donor_id}")
            results["letters"][donor_id] = letter_results
            continue
        
        letter = submission[donor_id]
        donor_type = donor_types[donor_id]
        
        # Evaluate required elements
        req_points, req_max = evaluate_required_elements(letter, donor_type)
        letter_results["required_elements"] = {
            "points": req_points,
            "max_points": req_max
        }
        
        # Evaluate personalization
        pers_points, pers_max = evaluate_personalization(letter, donor_id, donor_type)
        letter_results["personalization"] = {
            "points": pers_points,
            "max_points": pers_max
        }
        
        # Evaluate writing quality
        writing_points, writing_max = evaluate_writing_quality(letter)
        letter_results["writing_quality"] = {
            "points": writing_points,
            "max_points": writing_max
        }
        
        # Calculate total points for this letter
        letter_points = req_points + pers_points + writing_points
        letter_results["points"] = letter_points
        total_points += letter_points
        
        # Add feedback based on performance
        if req_points < req_max * 0.7:
            letter_results["feedback"].append("Missing required elements")
        if pers_points < pers_max * 0.7:
            letter_results["feedback"].append("Insufficient personalization")
        if writing_points < writing_max * 0.7:
            letter_results["feedback"].append("Writing quality needs improvement")
        
        # Check critical requirements
        critical_failures = []
        
        # 1. Correct donor name and donation amount
        if donor_id == "donor_4_letter" and not ("Sarah" in letter and "$250" in letter):
            critical_failures.append("Missing correct donor name or donation amount")
        elif donor_id == "donor_7_letter" and not ("Jim" in letter and "$150" in letter):
            critical_failures.append("Missing correct donor name or donation amount")
        elif donor_id == "donor_12_letter" and not ("Elizabeth" in letter and "$5,000" in letter and not "$5000" in letter):
            critical_failures.append("Missing correct donor name or donation amount")
        
        # 2. Specific acknowledgment of donation date
        dates = {
            "donor_4_letter": "September 22, 2023",
            "donor_7_letter": "September 30, 2023",
            "donor_12_letter": "October 12, 2023"
        }
        if dates[donor_id] not in letter:
            critical_failures.append("Missing specific donation date")
        
        # 3. Reference to correct program/fund
        programs = {
            "donor_4_letter": "Youth Programs",
            "donor_7_letter": "Education Program",
            "donor_12_letter": "Education Program"
        }
        if programs[donor_id] not in letter:
            critical_failures.append("Missing reference to correct program/fund")
        
        # 4. Tax-deductible language
        if "tax-deductible to the extent allowed by law" not in letter:
            critical_failures.append("Missing tax-deductible language")
        
        # Add critical failures to feedback
        if critical_failures:
            letter_results["feedback"].extend(critical_failures)
            letter_results["critical_failures"] = critical_failures
        
        results["letters"][donor_id] = letter_results
    
    # Add 1 point for proper JSON format if submission is valid
    if isinstance(submission, dict) and all(key in submission for key in ["donor_4_letter", "donor_7_letter", "donor_12_letter"]):
        total_points += 1
        results["json_format"] = {"points": 1, "max_points": 1}
    else:
        results["json_format"] = {"points": 0, "max_points": 1, "feedback": ["Improper JSON format"]}
    
    # Calculate overall score
    results["total_points"] = total_points
    results["overall_score"] = round((total_points / 100) * 100, 2)
    
    # Add passing status
    if total_points >= 90:
        results["status"] = "Excellent"
    elif total_points >= 75:
        results["status"] = "Satisfactory"
    else:
        results["status"] = "Not passing"
    
    # Check if any letter has critical failures
    has_critical_failures = any("critical_failures" in letter_data for letter_data in results["letters"].values())
    if has_critical_failures and results["status"] != "Not passing":
        results["status"] = "Not passing - Critical requirements not met"
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Status: {results['status']}")

if __name__ == "__main__":
    main()