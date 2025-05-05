#!/usr/bin/env python3
import json
import sys
import re
from collections import defaultdict

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_relevant_laws(candidate_laws, key_laws, scenario):
    """Evaluate the relevant laws section."""
    score = 0
    max_score = 4
    feedback = []
    
    # Check if candidate provided laws as a list
    if not isinstance(candidate_laws, list):
        feedback.append("Laws should be provided as a list")
        return 0, max_score, feedback
    
    # Check if candidate provided any laws
    if len(candidate_laws) == 0:
        feedback.append("No relevant laws provided")
        return 0, max_score, feedback
    
    # Count matching laws (case-insensitive partial matching)
    matches = 0
    for key_law in key_laws:
        key_law_lower = key_law.lower()
        for candidate_law in candidate_laws:
            if isinstance(candidate_law, str) and key_law_lower in candidate_law.lower():
                matches += 1
                break
    
    # Calculate score based on matches
    match_ratio = min(matches / len(key_laws), 1.0)
    score = round(match_ratio * max_score, 1)
    
    # Provide feedback
    if score == max_score:
        feedback.append("Correctly identified all relevant laws")
    elif score >= max_score * 0.75:
        feedback.append("Identified most relevant laws")
        feedback.append(f"Missing laws related to: {', '.join([law for law in key_laws if not any(law.lower() in c_law.lower() for c_law in candidate_laws)])}")
    elif score >= max_score * 0.5:
        feedback.append("Identified some relevant laws but missed several important ones")
        feedback.append(f"Missing laws related to: {', '.join([law for law in key_laws if not any(law.lower() in c_law.lower() for c_law in candidate_laws)])}")
    else:
        feedback.append("Failed to identify most relevant laws")
        feedback.append(f"Missing laws related to: {', '.join([law for law in key_laws if not any(law.lower() in c_law.lower() for c_law in candidate_laws)])}")
    
    return score, max_score, feedback

def evaluate_explanation(candidate_explanation, key_explanation, scenario):
    """Evaluate the explanation section."""
    score = 0
    max_score = 8
    feedback = []
    
    # Check if explanation is provided as a string
    if not isinstance(candidate_explanation, str):
        feedback.append("Explanation should be provided as a string")
        return 0, max_score, feedback
    
    # Check if explanation is too short
    if len(candidate_explanation) < 100:
        feedback.append("Explanation is too brief to adequately address the scenario")
        score = max(1, score)  # Give at least 1 point if something was provided
        return score, max_score, feedback
    
    # Define key concepts for each scenario
    key_concepts = {
        "scenario1": [
            "exclusive use", "principal place of business", "simplified method", 
            "regular method", "5 per square foot", "300 square feet", "1,500", 
            "20%", "mortgage", "utilities", "insurance", "repairs"
        ],
        "scenario2": [
            "ordinary income", "59½", "no penalty", "required minimum distribution", 
            "RMD", "73", "25% penalty", "tax bracket"
        ],
        "scenario3": [
            "2,000 per child", "4,000 total", "400,000", "phase out", 
            "refundable", "1,600", "social security", "dependent", "lived with you"
        ],
        "scenario4": [
            "short-term", "10 months", "less than one year", "ordinary income", 
            "7,000 gain", "long-term", "one year", "tax loss harvesting"
        ],
        "scenario5": [
            "california resident", "arizona non-resident", "physically present", 
            "double taxation", "credit for taxes", "file both states"
        ]
    }
    
    # Count matching concepts
    concepts_found = 0
    concepts_total = len(key_concepts[scenario])
    for concept in key_concepts[scenario]:
        if re.search(r'\b' + re.escape(concept) + r'\b', candidate_explanation.lower()):
            concepts_found += 1
    
    # Calculate base score based on concepts covered
    concept_ratio = concepts_found / concepts_total
    base_score = concept_ratio * max_score
    
    # Check for technical accuracy
    if "scenario1" in scenario:
        if "20%" in candidate_explanation and "$1,500" in candidate_explanation:
            score += 1  # Bonus for correct calculations
        elif "20%" not in candidate_explanation or "$1,500" not in candidate_explanation:
            base_score *= 0.8  # Penalty for missing key calculations
    
    elif "scenario2" in scenario:
        if "ordinary income" in candidate_explanation.lower() and "no penalty" in candidate_explanation.lower():
            score += 1  # Bonus for correct tax treatment
        if "73" not in candidate_explanation:
            base_score *= 0.8  # Penalty for incorrect RMD age
    
    elif "scenario3" in scenario:
        if "$2,000" in candidate_explanation and "$4,000" in candidate_explanation:
            score += 1  # Bonus for correct credit amounts
        else:
            base_score *= 0.8  # Penalty for incorrect credit amounts
    
    elif "scenario4" in scenario:
        if "short-term" in candidate_explanation.lower() and "$7,000" in candidate_explanation:
            score += 1  # Bonus for correct classification and calculation
        if "long-term" in candidate_explanation.lower() and "more favorable" not in candidate_explanation.lower():
            base_score *= 0.8  # Penalty for not explaining the difference
    
    elif "scenario5" in scenario:
        if "california resident" in candidate_explanation.lower() and "credit" in candidate_explanation.lower():
            score += 1  # Bonus for correct residency determination and credit mention
        if "double tax" not in candidate_explanation.lower():
            base_score *= 0.8  # Penalty for not addressing double taxation
    
    # Calculate final score
    score += base_score
    score = min(round(score, 1), max_score)  # Cap at max score
    
    # Provide feedback
    if score >= max_score * 0.9:
        feedback.append("Excellent explanation that covers all key concepts clearly")
    elif score >= max_score * 0.75:
        feedback.append("Good explanation covering most key concepts")
        feedback.append(f"Could improve by addressing: {', '.join([c for c in key_concepts[scenario] if not re.search(r'\b' + re.escape(c) + r'\b', candidate_explanation.lower())])[:3]}")
    elif score >= max_score * 0.5:
        feedback.append("Adequate explanation but missing several important concepts")
        feedback.append(f"Missing discussion of: {', '.join([c for c in key_concepts[scenario] if not re.search(r'\b' + re.escape(c) + r'\b', candidate_explanation.lower())])[:5]}")
    else:
        feedback.append("Explanation lacks many key concepts and clarity")
        feedback.append("Needs significant improvement in technical accuracy and completeness")
    
    # Check for jargon and clarity
    if len(candidate_explanation) > 1000:
        feedback.append("Explanation is unnecessarily long and could be more concise")
    
    return score, max_score, feedback

def evaluate_tax_implications(candidate_implications, key_implications, scenario):
    """Evaluate the tax implications section."""
    score = 0
    max_score = 4
    feedback = []
    
    # Check if implications are provided as a list
    if not isinstance(candidate_implications, list):
        feedback.append("Tax implications should be provided as a list")
        return 0, max_score, feedback
    
    # Check if any implications are provided
    if len(candidate_implications) == 0:
        feedback.append("No tax implications provided")
        return 0, max_score, feedback
    
    # Define key numbers and terms for each scenario
    key_terms = {
        "scenario1": ["1,500", "5", "300", "20%", "self-employment"],
        "scenario2": ["15,000", "ordinary income", "59½", "no penalty", "tax bracket"],
        "scenario3": ["2,000", "4,000", "1,600", "refundable", "400,000"],
        "scenario4": ["7,000", "25,000", "18,000", "short-term", "ordinary income"],
        "scenario5": ["california", "arizona", "credit", "double tax", "resident"]
    }
    
    # Count matching terms
    terms_found = 0
    for term in key_terms[scenario]:
        for implication in candidate_implications:
            if isinstance(implication, str) and term in implication.lower():
                terms_found += 1
                break
    
    # Calculate score based on terms covered
    term_ratio = min(terms_found / len(key_terms[scenario]), 1.0)
    score = round(term_ratio * max_score, 1)
    
    # Provide feedback
    if score == max_score:
        feedback.append("Correctly identified all key tax implications")
    elif score >= max_score * 0.75:
        feedback.append("Identified most key tax implications")
        feedback.append(f"Could also mention: {', '.join([term for term in key_terms[scenario] if not any(term in imp.lower() for imp in candidate_implications)])}")
    elif score >= max_score * 0.5:
        feedback.append("Identified some tax implications but missed several important ones")
        feedback.append(f"Missing important implications related to: {', '.join([term for term in key_terms[scenario] if not any(term in imp.lower() for imp in candidate_implications)])}")
    else:
        feedback.append("Failed to identify most key tax implications")
        feedback.append("Needs significant improvement in identifying financial impacts")
    
    return score, max_score, feedback

def evaluate_next_steps(candidate_steps, key_steps, scenario):
    """Evaluate the next steps section."""
    score = 0
    max_score = 4
    feedback = []
    
    # Check if steps are provided as a list
    if not isinstance(candidate_steps, list):
        feedback.append("Next steps should be provided as a list")
        return 0, max_score, feedback
    
    # Check if any steps are provided
    if len(candidate_steps) == 0:
        feedback.append("No next steps provided")
        return 0, max_score, feedback
    
    # Define key forms and actions for each scenario
    key_actions = {
        "scenario1": ["form 8829", "schedule c", "measure", "records", "expenses"],
        "scenario2": ["1099-r", "withholding", "estimated tax", "form 1040", "rmd"],
        "scenario3": ["social security", "birth certificate", "schedule 8812", "documentation", "residency"],
        "scenario4": ["form 8949", "schedule d", "1099-b", "documentation", "tax loss harvesting"],
        "scenario5": ["form 540", "form 140nr", "schedule s", "records", "dates"]
    }
    
    # Count matching actions
    actions_found = 0
    for action in key_actions[scenario]:
        for step in candidate_steps:
            if isinstance(step, str) and action in step.lower():
                actions_found += 1
                break
    
    # Calculate score based on actions covered
    action_ratio = min(actions_found / len(key_actions[scenario]), 1.0)
    score = round(action_ratio * max_score, 1)
    
    # Provide feedback
    if score == max_score:
        feedback.append("Provided comprehensive and appropriate next steps")
    elif score >= max_score * 0.75:
        feedback.append("Provided most key next steps")
        feedback.append(f"Could also recommend: {', '.join([action for action in key_actions[scenario] if not any(action in step.lower() for step in candidate_steps)])}")
    elif score >= max_score * 0.5:
        feedback.append("Provided some next steps but missed several important ones")
        feedback.append(f"Should also include: {', '.join([action for action in key_actions[scenario] if not any(action in step.lower() for step in candidate_steps)])}")
    else:
        feedback.append("Failed to provide most key next steps")
        feedback.append("Needs significant improvement in recommending client actions")
    
    return score, max_score, feedback

def evaluate_scenario(candidate_scenario, key_scenario, scenario_name):
    """Evaluate a complete scenario."""
    results = {}
    total_score = 0
    total_possible = 0
    
    # Check if all required sections are present
    required_sections = ["relevant_laws", "explanation", "tax_implications", "next_steps"]
    missing_sections = [section for section in required_sections if section not in candidate_scenario]
    
    if missing_sections:
        return {
            "score": 0,
            "max_score": 20,
            "feedback": f"Missing required sections: {', '.join(missing_sections)}",
            "section_scores": {}
        }
    
    # Evaluate each section
    section_scores = {}
    
    # Relevant Laws (4 points)
    laws_score, laws_max, laws_feedback = evaluate_relevant_laws(
        candidate_scenario["relevant_laws"], 
        key_scenario["relevant_laws"],
        scenario_name
    )
    section_scores["relevant_laws"] = {
        "score": laws_score,
        "max_score": laws_max,
        "feedback": laws_feedback
    }
    total_score += laws_score
    total_possible += laws_max
    
    # Explanation (8 points)
    explanation_score, explanation_max, explanation_feedback = evaluate_explanation(
        candidate_scenario["explanation"], 
        key_scenario["explanation"],
        scenario_name
    )
    section_scores["explanation"] = {
        "score": explanation_score,
        "max_score": explanation_max,
        "feedback": explanation_feedback
    }
    total_score += explanation_score
    total_possible += explanation_max
    
    # Tax Implications (4 points)
    implications_score, implications_max, implications_feedback = evaluate_tax_implications(
        candidate_scenario["tax_implications"], 
        key_scenario["tax_implications"],
        scenario_name
    )
    section_scores["tax_implications"] = {
        "score": implications_score,
        "max_score": implications_max,
        "feedback": implications_feedback
    }
    total_score += implications_score
    total_possible += implications_max
    
    # Next Steps (4 points)
    steps_score, steps_max, steps_feedback = evaluate_next_steps(
        candidate_scenario["next_steps"], 
        key_scenario["next_steps"],
        scenario_name
    )
    section_scores["next_steps"] = {
        "score": steps_score,
        "max_score": steps_max,
        "feedback": steps_feedback
    }
    total_score += steps_score
    total_possible += steps_max
    
    # Generate overall scenario feedback
    scenario_feedback = []
    if total_score >= total_possible * 0.9:
        scenario_feedback.append("Excellent response that demonstrates strong understanding of the tax laws and effective client communication")
    elif total_score >= total_possible * 0.75:
        scenario_feedback.append("Good response that covers most key aspects of the scenario")
    elif total_score >= total_possible * 0.6:
        scenario_feedback.append("Adequate response but needs improvement in some areas")
    else:
        scenario_feedback.append("Response needs significant improvement to meet professional standards")
    
    # Check for critical errors
    critical_errors = check_for_critical_errors(candidate_scenario, key_scenario, scenario_name)
    if critical_errors:
        scenario_feedback.extend(critical_errors)
    
    return {
        "score": round(total_score, 1),
        "max_score": total_possible,
        "feedback": scenario_feedback,
        "section_scores": section_scores,
        "has_critical_error": bool(critical_errors)
    }

def check_for_critical_errors(candidate_scenario, key_scenario, scenario_name):
    """Check for critical errors that would result in automatic failure."""
    critical_errors = []
    
    # Define scenario-specific critical error checks
    if scenario_name == "scenario1":
        # Check for incorrect home office qualification
        if "don't qualify" in candidate_scenario["explanation"].lower() or "not qualify" in candidate_scenario["explanation"].lower():
            critical_errors.append("CRITICAL ERROR: Incorrectly stated that client doesn't qualify for home office deduction")
    
    elif scenario_name == "scenario2":
        # Check for incorrect penalty information
        if "penalty" in candidate_scenario["explanation"].lower() and "59" in candidate_scenario["explanation"]:
            if not ("no penalty" in candidate_scenario["explanation"].lower() or "not subject to penalty" in candidate_scenario["explanation"].lower()):
                critical_errors.append("CRITICAL ERROR: Incorrectly suggested early withdrawal penalty applies to client over 59½")
    
    elif scenario_name == "scenario3":
        # Check for incorrect credit eligibility
        if "don't qualify" in candidate_scenario["explanation"].lower() or "not eligible" in candidate_scenario["explanation"].lower():
            critical_errors.append("CRITICAL ERROR: Incorrectly stated that client doesn't qualify for Child Tax Credit")
    
    elif scenario_name == "scenario4":
        # Check for incorrect capital gain classification
        if "long-term" in candidate_scenario["explanation"].lower() and "short-term" not in candidate_scenario["explanation"].lower():
            critical_errors.append("CRITICAL ERROR: Incorrectly classified 10-month stock holding as long-term capital gain")
    
    elif scenario_name == "scenario5":
        # Check for incorrect residency determination
        if "arizona resident" in candidate_scenario["explanation"].lower() and "california non-resident" in candidate_scenario["explanation"].lower():
            critical_errors.append("CRITICAL ERROR: Incorrectly determined client is an Arizona resident rather than California resident")
    
    return critical_errors

def evaluate_submission(candidate_submission, answer_key):
    """Evaluate the complete submission against the answer key."""
    results = {
        "overall_score": 0,
        "passing_threshold": 75,
        "total_score": 0,
        "total_possible": 0,
        "scenarios": {},
        "overall_feedback": [],
        "has_critical_error": False
    }
    
    # Check if all required scenarios are present
    required_scenarios = ["scenario1", "scenario2", "scenario3", "scenario4", "scenario5"]
    missing_scenarios = [scenario for scenario in required_scenarios if scenario not in candidate_submission]
    
    if missing_scenarios:
        results["overall_feedback"].append(f"Missing required scenarios: {', '.join(missing_scenarios)}")
        results["overall_feedback"].append("Automatic failure: All five scenarios must be completed")
        results["has_critical_error"] = True
        results["overall_score"] = 0
        return results
    
    # Evaluate each scenario
    for scenario in required_scenarios:
        results["scenarios"][scenario] = evaluate_scenario(
            candidate_submission[scenario],
            answer_key[scenario],
            scenario
        )
        
        results["total_score"] += results["scenarios"][scenario]["score"]
        results["total_possible"] += results["scenarios"][scenario]["max_score"]
        
        # Check for critical errors
        if results["scenarios"][scenario].get("has_critical_error", False):
            results["has_critical_error"] = True
    
    # Calculate overall score as percentage
    if results["total_possible"] > 0:
        results["overall_score"] = round((results["total_score"] / results["total_possible"]) * 100, 1)
    
    # Check if any scenario scored below minimum threshold (12 points)
    below_threshold_scenarios = []
    for scenario, data in results["scenarios"].items():
        if data["score"] < 12:
            below_threshold_scenarios.append(scenario)
    
    # Generate overall feedback
    if results["has_critical_error"]:
        results["overall_feedback"].append("AUTOMATIC FAILURE: Critical errors detected in one or more scenarios")
    elif below_threshold_scenarios:
        results["overall_feedback"].append(f"FAILURE: Scored below minimum threshold (12 points) in scenarios: {', '.join(below_threshold_scenarios)}")
    elif results["overall_score"] >= results["passing_threshold"]:
        results["overall_feedback"].append(f"PASS: Overall score of {results['overall_score']}% exceeds the passing threshold of {results['passing_threshold']}%")
    else:
        results["overall_feedback"].append(f"FAILURE: Overall score of {results['overall_score']}% is below the passing threshold of {results['passing_threshold']}%")
    
    # Add strengths and weaknesses
    strengths = []
    weaknesses = []
    
    # Identify strongest and weakest scenarios
    scenario_scores = [(scenario, data["score"], data["max_score"]) for scenario, data in results["scenarios"].items()]
    scenario_scores.sort(key=lambda x: x[1]/x[2], reverse=True)
    
    if scenario_scores:
        strongest_scenario = scenario_scores[0][0]
        weakest_scenario = scenario_scores[-1][0]
        
        strengths.append(f"Strongest performance in {strongest_scenario.replace('scenario', 'Scenario ')}")
        weaknesses.append(f"Weakest performance in {weakest_scenario.replace('scenario', 'Scenario ')}")
    
    # Identify strongest and weakest sections across all scenarios
    section_scores = defaultdict(list)
    for scenario, data in results["scenarios"].items():
        for section, section_data in data["section_scores"].items():
            section_scores[section].append((section_data["score"], section_data["max_score"]))
    
    section_averages = {}
    for section, scores in section_scores.items():
        if scores:
            total_score = sum(score[0] for score in scores)
            total_possible = sum(score[1] for score in scores)
            section_averages[section] = total_score / total_possible
    
    if section_averages:
        strongest_section = max(section_averages.items(), key=lambda x: x[1])[0]
        weakest_section = min(section_averages.items(), key=lambda x: x[1])[0]
        
        strengths.append(f"Strongest in {strongest_section.replace('_', ' ')}")
        weaknesses.append(f"Needs improvement in {weakest_section.replace('_', ' ')}")
    
    results["strengths"] = strengths
    results["weaknesses"] = weaknesses
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    candidate_submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(candidate_submission, answer_key)
    
    # Add candidate ID if available
    if "candidate_id" in candidate_submission:
        results["candidate_id"] = candidate_submission["candidate_id"]
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    for feedback in results["overall_feedback"]:
        print(feedback)

if __name__ == "__main__":
    main()