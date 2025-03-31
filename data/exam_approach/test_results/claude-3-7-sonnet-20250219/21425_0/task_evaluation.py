import json
import os
import re

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_claim_analysis(submission, answer_key):
    """Evaluate the claim analysis section."""
    score = 0
    feedback = []
    
    # Key Facts (5 points)
    if len(submission.get("key_facts", [])) >= 8:
        score += 5
    else:
        feedback.append("Insufficient key facts identified")
    
    # Discrepancies (5 points)
    if len(submission.get("discrepancies", [])) >= 5:
        score += 5
    else:
        feedback.append("Insufficient discrepancies identified")
    
    # Additional Information Needed (5 points)
    if len(submission.get("additional_information_needed", [])) >= 5:
        score += 5
    else:
        feedback.append("Insufficient additional information needs identified")
    
    # Potential Coverage Issues (5 points)
    if len(submission.get("potential_coverage_issues", [])) >= 3:
        score += 5
    else:
        feedback.append("Insufficient potential coverage issues identified")
    
    return score, feedback

def evaluate_coverage_determination(submission, answer_key):
    """Evaluate the coverage determination section."""
    score = 0
    feedback = []
    
    # Correct Coverage Determination (5 points)
    if submission.get("is_covered") == answer_key.get("is_covered"):
        score += 5
    else:
        feedback.append("Incorrect coverage determination")
    
    # Identification of Applicable Provisions (5 points)
    if len(submission.get("applicable_provisions", [])) >= 3:
        score += 5
    else:
        feedback.append("Insufficient applicable provisions identified")
    
    # Thorough Rationale (5 points)
    if len(submission.get("determination_rationale", "")) >= 100:
        score += 5
    else:
        feedback.append("Insufficient coverage determination rationale")
    
    return score, feedback

def evaluate_liability_assessment(submission, answer_key):
    """Evaluate the liability assessment section."""
    score = 0
    feedback = []
    
    # Reasonable Liability Percentages (10 points)
    insured_liability = submission.get("insured_liability_percentage", 0)
    claimant_liability = submission.get("claimant_liability_percentage", 0)
    third_party_liability = submission.get("third_party_liability_percentage", 0)
    
    # Check if insured liability is in reasonable range (5 points)
    if 60 <= insured_liability <= 80:
        score += 5
    else:
        feedback.append("Insured liability percentage outside reasonable range (60-80%)")
    
    # Check if claimant liability is in reasonable range (5 points)
    if 20 <= claimant_liability <= 40:
        score += 5
    else:
        feedback.append("Claimant liability percentage outside reasonable range (20-40%)")
    
    # Check if percentages sum to 100%
    if abs((insured_liability + claimant_liability + third_party_liability) - 100) > 1:  # Allow for rounding errors
        feedback.append("Liability percentages do not sum to 100%")
    
    # Thorough Liability Rationale (10 points)
    if len(submission.get("liability_rationale", "")) >= 150:
        score += 10
    else:
        feedback.append("Insufficient liability rationale")
    
    return score, feedback

def evaluate_damages_evaluation(submission, answer_key):
    """Evaluate the damages evaluation section."""
    score = 0
    feedback = []
    
    # Economic Damages (5 points)
    economic_damages = submission.get("economic_damages", {})
    
    # Medical Expenses (3 points)
    medical_expenses = economic_damages.get("medical_expenses", 0)
    if 275000 <= medical_expenses <= 295000:
        score += 3
    else:
        feedback.append(f"Medical expenses outside reasonable range (275,000-295,000): {medical_expenses}")
    
    # Wage Loss (1 point)
    wage_loss = economic_damages.get("wage_loss", 0)
    if 10000 <= wage_loss <= 25000:
        score += 1
    else:
        feedback.append(f"Wage loss outside reasonable range (10,000-25,000): {wage_loss}")
    
    # Property Damage (1 point)
    property_damage = economic_damages.get("property_damage", 0)
    if 30000 <= property_damage <= 35000:
        score += 1
    else:
        feedback.append(f"Property damage outside reasonable range (30,000-35,000): {property_damage}")
    
    # Non-Economic Damages (5 points)
    non_economic_damages = submission.get("non_economic_damages", {})
    pain_suffering = non_economic_damages.get("pain_suffering", 0)
    if 300000 <= pain_suffering <= 500000:
        score += 5
    else:
        feedback.append(f"Pain and suffering estimate outside reasonable range (300,000-500,000): {pain_suffering}")
    
    # Appropriate Reserve Recommendation (5 points)
    recommended_reserves = submission.get("recommended_reserves", 0)
    if 450000 <= recommended_reserves <= 500000:
        score += 5
    else:
        feedback.append(f"Recommended reserves outside reasonable range (450,000-500,000): {recommended_reserves}")
    
    # Thorough Evaluation Rationale (5 points)
    if len(submission.get("evaluation_rationale", "")) >= 150:
        score += 5
    else:
        feedback.append("Insufficient damages evaluation rationale")
    
    return score, feedback

def evaluate_resolution_strategy(submission, answer_key):
    """Evaluate the resolution strategy section."""
    score = 0
    feedback = []
    
    # Appropriate Settlement Authority (5 points)
    settlement_authority = submission.get("settlement_authority", 0)
    if 450000 <= settlement_authority <= 500000:
        score += 5
    else:
        feedback.append(f"Settlement authority outside reasonable range (450,000-500,000): {settlement_authority}")
    
    # Effective Negotiation Approach (5 points)
    negotiation_approach = submission.get("negotiation_approach", "")
    if (len(negotiation_approach) >= 150 and 
        ("excess" in negotiation_approach.lower()) and 
        any(term in negotiation_approach.lower() for term in ["pedestrian", "martinez", "claimant 2"])):
        score += 5
    else:
        feedback.append("Insufficient or inappropriate negotiation approach")
    
    # Comprehensive Timeline and Barriers (5 points)
    if (len(submission.get("potential_barriers", [])) >= 3 and 
        len(submission.get("proposed_timeline", "")) >= 100):
        score += 5
    else:
        feedback.append("Insufficient timeline or barriers identified")
    
    return score, feedback

def evaluate_communications(submission, answer_key):
    """Evaluate the communications section."""
    score = 0
    feedback = []
    
    # Professional Insured Update (3 points)
    insured_update = submission.get("insured_update", "")
    if (len(insured_update) >= 200 and 
        "excess" in insured_update.lower() and 
        "personal" in insured_update.lower() and 
        "attorney" in insured_update.lower()):
        score += 3
    else:
        feedback.append("Insufficient or inappropriate insured update")
    
    # Effective Claimant Attorney Request (3 points)
    claimant_request = submission.get("claimant_attorney_request", "")
    if (len(claimant_request) >= 200 and 
        "medical" in claimant_request.lower() and 
        "records" in claimant_request.lower()):
        score += 3
    else:
        feedback.append("Insufficient or inappropriate claimant attorney request")
    
    # Comprehensive File Note (4 points)
    file_note = submission.get("file_note", "")
    if (len(file_note) >= 300 and 
        "liability" in file_note.lower() and 
        "damages" in file_note.lower() and 
        "strategy" in file_note.lower()):
        score += 4
    else:
        feedback.append("Insufficient or inappropriate file note")
    
    return score, feedback

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "section_scores": {},
        "feedback": {}
    }
    
    total_score = 0
    max_score = 100
    
    # Evaluate Claim Analysis (20 points)
    score, feedback = evaluate_claim_analysis(submission.get("claim_analysis", {}), answer_key.get("claim_analysis", {}))
    total_score += score
    results["section_scores"]["claim_analysis"] = {"score": score, "max_score": 20}
    results["feedback"]["claim_analysis"] = feedback
    
    # Evaluate Coverage Determination (15 points)
    score, feedback = evaluate_coverage_determination(submission.get("coverage_determination", {}), answer_key.get("coverage_determination", {}))
    total_score += score
    results["section_scores"]["coverage_determination"] = {"score": score, "max_score": 15}
    results["feedback"]["coverage_determination"] = feedback
    
    # Evaluate Liability Assessment (20 points)
    score, feedback = evaluate_liability_assessment(submission.get("liability_assessment", {}), answer_key.get("liability_assessment", {}))
    total_score += score
    results["section_scores"]["liability_assessment"] = {"score": score, "max_score": 20}
    results["feedback"]["liability_assessment"] = feedback
    
    # Evaluate Damages Evaluation (20 points)
    score, feedback = evaluate_damages_evaluation(submission.get("damages_evaluation", {}), answer_key.get("damages_evaluation", {}))
    total_score += score
    results["section_scores"]["damages_evaluation"] = {"score": score, "max_score": 20}
    results["feedback"]["damages_evaluation"] = feedback
    
    # Evaluate Resolution Strategy (15 points)
    score, feedback = evaluate_resolution_strategy(submission.get("resolution_strategy", {}), answer_key.get("resolution_strategy", {}))
    total_score += score
    results["section_scores"]["resolution_strategy"] = {"score": score, "max_score": 15}
    results["feedback"]["resolution_strategy"] = feedback
    
    # Evaluate Communications (10 points)
    score, feedback = evaluate_communications(submission.get("communications", {}), answer_key.get("communications", {}))
    total_score += score
    results["section_scores"]["communications"] = {"score": score, "max_score": 10}
    results["feedback"]["communications"] = feedback
    
    # Calculate overall score as a percentage
    results["overall_score"] = round((total_score / max_score) * 100, 2)
    results["total_points"] = total_score
    results["max_points"] = max_score
    results["pass_fail"] = "PASS" if results["overall_score"] >= 70 else "FAIL"
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Result: {results['pass_fail']}")

if __name__ == "__main__":
    main()