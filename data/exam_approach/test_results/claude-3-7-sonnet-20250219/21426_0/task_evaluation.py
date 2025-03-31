import json
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

def evaluate_coverage_determination(submission, answer_key, scenario):
    """Evaluate if the coverage determination is correct (2 points)."""
    if submission[scenario]["claim_covered"] == answer_key[scenario]["claim_covered"]:
        return 2, "Correct coverage determination"
    else:
        return 0, "Incorrect coverage determination"

def evaluate_payment_calculation(submission, answer_key, scenario):
    """Evaluate if the payment calculation is correct (3 points)."""
    correct_amount = answer_key[scenario]["payment_amount"]
    submitted_amount = submission[scenario]["payment_amount"]
    
    # Calculate percentage difference
    if correct_amount == 0:
        percentage_diff = 0 if submitted_amount == 0 else 100
    else:
        percentage_diff = abs((submitted_amount - correct_amount) / correct_amount * 100)
    
    if percentage_diff == 0:
        return 3, "Correct payment calculation"
    elif percentage_diff <= 5:
        return 2, f"Payment calculation within 5% of correct amount (submitted: ${submitted_amount:.2f}, correct: ${correct_amount:.2f})"
    elif percentage_diff <= 10:
        return 1, f"Payment calculation within 10% of correct amount (submitted: ${submitted_amount:.2f}, correct: ${correct_amount:.2f})"
    else:
        return 0, f"Payment calculation error exceeds 10% (submitted: ${submitted_amount:.2f}, correct: ${correct_amount:.2f})"

def evaluate_deductible_application(submission, answer_key, scenario):
    """Evaluate if the deductible was correctly applied (1 point)."""
    if submission[scenario]["deductible_applied"] == answer_key[scenario]["deductible_applied"]:
        return 1, "Correct deductible application"
    else:
        return 0, f"Incorrect deductible application (submitted: ${submission[scenario]['deductible_applied']:.2f}, correct: ${answer_key[scenario]['deductible_applied']:.2f})"

def evaluate_decision_rationale(submission, answer_key, scenario):
    """Evaluate the decision rationale (2 points)."""
    # This is a simplified evaluation - in reality, this would require more sophisticated text analysis
    # or human review. Here we're just checking if the rationale is of sufficient length and contains
    # key terms that should be present in a good rationale.
    
    rationale = submission[scenario]["decision_rationale"].lower()
    
    # Check if rationale is of sufficient length (at least 50 words)
    word_count = len(rationale.split())
    if word_count < 50:
        return 0, f"Decision rationale too brief ({word_count} words, minimum 50 required)"
    
    # Check for key terms based on the scenario
    key_terms = {
        "scenario_1": ["collision", "coverage", "deductible", "repair"],
        "scenario_2": ["water", "damage", "pipe", "burst", "freezing"],
        "scenario_3": ["medical", "deductible", "coinsurance", "in-network"],
        "scenario_4": ["business", "interruption", "income", "expenses"],
        "scenario_5": ["theft", "stolen", "property", "deductible"]
    }
    
    terms_found = sum(1 for term in key_terms[scenario] if term in rationale)
    
    if terms_found >= len(key_terms[scenario]) - 1:
        return 2, "Comprehensive decision rationale with relevant policy references"
    elif terms_found >= len(key_terms[scenario]) / 2:
        return 1, "Adequate decision rationale but missing some key policy references"
    else:
        return 0, "Insufficient decision rationale lacking key policy references"

def evaluate_authority_level(submission, answer_key, scenario):
    """Evaluate if authority level determination is correct (1 point)."""
    if submission[scenario]["exceeds_authority"] == answer_key[scenario]["exceeds_authority"]:
        return 1, "Correct authority level determination"
    else:
        # This is a critical error if they fail to escalate a claim that exceeds authority
        if answer_key[scenario]["exceeds_authority"] and not submission[scenario]["exceeds_authority"]:
            return 0, "CRITICAL ERROR: Failed to escalate claim that exceeds authority level"
        else:
            return 0, "Incorrect authority level determination"

def evaluate_fraud_indicators(submission, answer_key, scenario):
    """Evaluate fraud indicator identification (1 point)."""
    # In this exam, none of the scenarios have clear fraud indicators
    # But we'll check if the candidate falsely identified fraud where none exists
    
    answer_key_indicators = answer_key[scenario]["fraud_indicators"]
    submission_indicators = submission[scenario]["fraud_indicators"]
    
    if len(answer_key_indicators) == 0 and len(submission_indicators) == 0:
        return 1, "Correctly identified no fraud indicators"
    elif len(answer_key_indicators) == 0 and len(submission_indicators) > 0:
        # The candidate may have reasonable suspicions, so we'll accept with justification
        # This is a simplified check - in reality, would need human review
        if len(submission[scenario]["documentation_notes"]) > 30:
            return 1, "Identified potential fraud indicators with proper justification"
        else:
            return 0, "Incorrectly identified fraud indicators without proper justification"
    else:
        # Compare the identified indicators with the expected ones
        matches = sum(1 for ind in submission_indicators if any(ind.lower() in key_ind.lower() for key_ind in answer_key_indicators))
        if matches >= len(answer_key_indicators) / 2:
            return 1, "Correctly identified most fraud indicators"
        else:
            return 0, "Failed to identify key fraud indicators"

def check_critical_errors(results):
    """Check for critical errors that would result in automatic failure."""
    critical_errors = []
    
    for scenario in results:
        if scenario.startswith("scenario_"):
            # Check for approving a claim that should be denied
            if "coverage determination" in results[scenario] and "Incorrect" in results[scenario]["coverage determination"]["feedback"]:
                critical_errors.append(f"{scenario}: Approved a claim that should be denied or vice versa")
            
            # Check for failing to escalate (already captured in authority level evaluation)
            if "authority level" in results[scenario] and "CRITICAL ERROR" in results[scenario]["authority level"]["feedback"]:
                critical_errors.append(f"{scenario}: {results[scenario]['authority level']['feedback']}")
            
            # Check for payment calculation error exceeding 10%
            if "payment calculation" in results[scenario] and "exceeds 10%" in results[scenario]["payment calculation"]["feedback"]:
                critical_errors.append(f"{scenario}: {results[scenario]['payment calculation']['feedback']}")
    
    return critical_errors

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_points": 0,
        "max_points": 50,
        "overall_score": 0,
        "critical_errors": []
    }
    
    # Evaluate each scenario
    for i in range(1, 6):
        scenario = f"scenario_{i}"
        scenario_results = {
            "total_points": 0,
            "max_points": 10
        }
        
        # Evaluate each aspect of the scenario
        evaluations = [
            ("coverage determination", evaluate_coverage_determination),
            ("payment calculation", evaluate_payment_calculation),
            ("deductible application", evaluate_deductible_application),
            ("decision rationale", evaluate_decision_rationale),
            ("authority level", evaluate_authority_level),
            ("fraud indicators", evaluate_fraud_indicators)
        ]
        
        for aspect, evaluation_func in evaluations:
            points, feedback = evaluation_func(submission, answer_key, scenario)
            scenario_results[aspect] = {
                "points": points,
                "feedback": feedback
            }
            scenario_results["total_points"] += points
        
        results[scenario] = scenario_results
        results["total_points"] += scenario_results["total_points"]
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Check for critical errors
    results["critical_errors"] = check_critical_errors(results)
    
    # If there are critical errors, the candidate fails regardless of score
    if results["critical_errors"]:
        results["pass"] = False
        results["result_summary"] = "FAIL - Critical errors detected"
    else:
        # Pass if score is at least 80%
        results["pass"] = results["overall_score"] >= 80
        results["result_summary"] = "PASS" if results["pass"] else "FAIL"
    
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
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {results['result_summary']}")
    if results["critical_errors"]:
        print("Critical errors:")
        for error in results["critical_errors"]:
            print(f"- {error}")

if __name__ == "__main__":
    main()