#!/usr/bin/env python3

import json
import sys
import re
from typing import Dict, List, Union, Any

def load_json_file(filename: str) -> Dict:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not a valid JSON file.")
        sys.exit(1)

def evaluate_price_trends(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 1: Price Trend Analysis."""
    score = 0
    max_score = 25
    feedback = {}
    
    # Price trends (6 points - 2 per commodity)
    price_trends_score = 0
    price_trends_feedback = {}
    
    for commodity in ["steel", "aluminum", "copper"]:
        if commodity in submission["task1"]["price_trends"]:
            # Check if the key patterns are mentioned
            key_patterns = answer_key["task1"]["price_trends"][commodity].lower().split()
            submission_text = submission["task1"]["price_trends"][commodity].lower()
            
            pattern_matches = sum(1 for pattern in key_patterns if pattern in submission_text)
            commodity_score = min(2, (pattern_matches / len(key_patterns)) * 2)
            
            price_trends_score += commodity_score
            price_trends_feedback[commodity] = commodity_score
        else:
            price_trends_feedback[commodity] = 0
    
    # Volatility calculations (6 points - 2 per commodity)
    volatility_score = 0
    volatility_feedback = {}
    
    for commodity in ["steel", "aluminum", "copper"]:
        if commodity in submission["task1"]["volatility_calculations"]:
            correct_value = answer_key["task1"]["volatility_calculations"][commodity]
            submitted_value = submission["task1"]["volatility_calculations"][commodity]
            
            # Allow for some margin of error (within 10%)
            error_margin = abs(correct_value * 0.1)
            if abs(submitted_value - correct_value) <= error_margin:
                volatility_score += 2
                volatility_feedback[commodity] = 2
            else:
                # Partial credit based on how close they are
                accuracy = max(0, 1 - abs(submitted_value - correct_value) / correct_value)
                partial_score = accuracy * 2
                volatility_score += partial_score
                volatility_feedback[commodity] = partial_score
        else:
            volatility_feedback[commodity] = 0
    
    # Production-price correlation (4 points)
    correlation_score = 0
    if submission["task1"]["production_price_correlation"].lower() == answer_key["task1"]["production_price_correlation"].lower():
        correlation_score = 4
    
    # Price increase prediction (4 points)
    prediction_score = 0
    if submission["task1"]["price_increase_prediction"].lower() == answer_key["task1"]["price_increase_prediction"].lower():
        prediction_score = 4
    
    # Prediction justification (5 points)
    justification_score = 0
    key_justification = answer_key["task1"]["prediction_justification"].lower()
    submission_justification = submission["task1"]["prediction_justification"].lower()
    
    # Check for key elements in justification
    key_elements = [
        "consecutive monthly increases",
        "upward trend",
        "increasing production",
        "three months",
        "q4"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_justification)
    justification_score = min(5, (element_matches / len(key_elements)) * 5)
    
    # Calculate total score for Task 1
    task1_score = price_trends_score + volatility_score + correlation_score + prediction_score + justification_score
    
    feedback["price_trends"] = {
        "score": price_trends_score,
        "max_score": 6,
        "details": price_trends_feedback
    }
    
    feedback["volatility_calculations"] = {
        "score": volatility_score,
        "max_score": 6,
        "details": volatility_feedback
    }
    
    feedback["production_price_correlation"] = {
        "score": correlation_score,
        "max_score": 4,
        "correct_answer": answer_key["task1"]["production_price_correlation"]
    }
    
    feedback["price_increase_prediction"] = {
        "score": prediction_score,
        "max_score": 4,
        "correct_answer": answer_key["task1"]["price_increase_prediction"]
    }
    
    feedback["prediction_justification"] = {
        "score": justification_score,
        "max_score": 5
    }
    
    return {
        "score": task1_score,
        "max_score": max_score,
        "passing_score": 18,
        "passed": task1_score >= 18,
        "feedback": feedback
    }

def evaluate_disruption_analysis(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Supply Chain Disruption Analysis."""
    score = 0
    max_score = 25
    feedback = {}
    
    # Disruption impact analysis (9 points - 3 per disruption)
    impact_score = 0
    impact_feedback = {}
    
    for disruption in ["logistics_bottleneck", "geopolitical_conflict", "natural_disaster"]:
        if disruption in submission["task2"]["disruption_impact_analysis"]:
            key_elements = answer_key["task2"]["disruption_impact_analysis"][disruption].lower().split(". ")
            submission_text = submission["task2"]["disruption_impact_analysis"][disruption].lower()
            
            # Check for key elements (price impact, duration, affected materials)
            elements_found = 0
            for element in key_elements:
                if any(key_term in submission_text for key_term in element.split()[:3]):
                    elements_found += 1
            
            disruption_score = min(3, (elements_found / len(key_elements)) * 3)
            impact_score += disruption_score
            impact_feedback[disruption] = disruption_score
        else:
            impact_feedback[disruption] = 0
    
    # Price sensitive materials (5 points)
    sensitive_materials_score = 0
    correct_materials = set(m.lower() for m in answer_key["task2"]["price_sensitive_materials"])
    submitted_materials = set(m.lower() for m in submission["task2"]["price_sensitive_materials"] if m)
    
    if submitted_materials:
        # Calculate intersection of correct and submitted materials
        matching_materials = correct_materials.intersection(submitted_materials)
        sensitive_materials_score = min(5, (len(matching_materials) / len(correct_materials)) * 5)
    
    # Longest recovery disruption (3 points)
    recovery_score = 0
    if submission["task2"]["longest_recovery_disruption"].lower() == answer_key["task2"]["longest_recovery_disruption"].lower():
        recovery_score = 3
    
    # Mitigation recommendations (8 points)
    mitigation_score = 0
    if submission["task2"]["mitigation_recommendations"]:
        key_strategies = [s.lower() for s in answer_key["task2"]["mitigation_recommendations"]]
        submitted_strategies = [s.lower() for s in submission["task2"]["mitigation_recommendations"] if s]
        
        # Check for conceptual matches rather than exact wording
        strategy_matches = 0
        for submitted in submitted_strategies:
            for key in key_strategies:
                # If enough key terms match, consider it a match
                key_terms = set(re.findall(r'\b\w+\b', key))
                submitted_terms = set(re.findall(r'\b\w+\b', submitted))
                overlap = len(key_terms.intersection(submitted_terms))
                
                if overlap >= len(key_terms) * 0.3:  # 30% match threshold
                    strategy_matches += 1
                    break
        
        mitigation_score = min(8, (strategy_matches / len(key_strategies)) * 8)
    
    # Calculate total score for Task 2
    task2_score = impact_score + sensitive_materials_score + recovery_score + mitigation_score
    
    feedback["disruption_impact_analysis"] = {
        "score": impact_score,
        "max_score": 9,
        "details": impact_feedback
    }
    
    feedback["price_sensitive_materials"] = {
        "score": sensitive_materials_score,
        "max_score": 5,
        "correct_materials": answer_key["task2"]["price_sensitive_materials"]
    }
    
    feedback["longest_recovery_disruption"] = {
        "score": recovery_score,
        "max_score": 3,
        "correct_answer": answer_key["task2"]["longest_recovery_disruption"]
    }
    
    feedback["mitigation_recommendations"] = {
        "score": mitigation_score,
        "max_score": 8
    }
    
    return {
        "score": task2_score,
        "max_score": max_score,
        "passing_score": 18,
        "passed": task2_score >= 18,
        "feedback": feedback
    }

def evaluate_futures_market(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Futures Market Interpretation."""
    score = 0
    max_score = 25
    feedback = {}
    
    # Futures-spot comparison (6 points)
    comparison_score = 0
    key_comparison = answer_key["task3"]["futures_spot_comparison"].lower()
    submission_comparison = submission["task3"]["futures_spot_comparison"].lower()
    
    # Check for key elements in comparison
    key_elements = [
        "poor predictors",
        "volatile periods",
        "3-month futures",
        "more accurate",
        "backwardation",
        "contango"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_comparison)
    comparison_score = min(6, (element_matches / len(key_elements)) * 6)
    
    # Market patterns (6 points)
    patterns_score = 0
    
    # Check backwardation commodities
    correct_backwardation = set(c.lower() for c in answer_key["task3"]["market_patterns"]["backwardation_commodities"])
    submitted_backwardation = set(c.lower() for c in submission["task3"]["market_patterns"]["backwardation_commodities"] if c)
    
    backwardation_score = 0
    if submitted_backwardation:
        matching = correct_backwardation.intersection(submitted_backwardation)
        backwardation_score = min(3, (len(matching) / len(correct_backwardation)) * 3)
    
    # Check contango commodities
    correct_contango = set(c.lower() for c in answer_key["task3"]["market_patterns"]["contango_commodities"])
    submitted_contango = set(c.lower() for c in submission["task3"]["market_patterns"]["contango_commodities"] if c)
    
    contango_score = 0
    # Special case: if correct_contango is empty and submitted_contango is empty, full points
    if not correct_contango and not submitted_contango:
        contango_score = 3
    elif correct_contango:
        matching = correct_contango.intersection(submitted_contango)
        contango_score = min(3, (len(matching) / len(correct_contango)) * 3)
    
    patterns_score = backwardation_score + contango_score
    
    # Current futures research (5 points)
    # This requires evaluating the quality of web research, which is subjective
    # Checking if it contains meaningful content
    research_score = 0
    if "current_futures_research" in submission["task3"] and submission["task3"]["current_futures_research"].strip():
        research_content = submission["task3"]["current_futures_research"].lower()
        # Check if it contains relevant terms
        relevant_terms = ["aluminum", "price", "market", "futures", "contract"]
        term_matches = sum(1 for term in relevant_terms if term in research_content)
        research_score = min(5, (term_matches / len(relevant_terms)) * 5)
    
    # Purchase timing recommendation (8 points)
    recommendation_score = 0
    key_recommendation = answer_key["task3"]["purchase_timing_recommendation"].lower()
    submission_recommendation = submission["task3"]["purchase_timing_recommendation"].lower()
    
    # Check for key elements in recommendation
    key_elements = [
        "backwardation",
        "immediate",
        "spot purchases",
        "strategic",
        "contracts",
        "hedge"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_recommendation)
    recommendation_score = min(8, (element_matches / len(key_elements)) * 8)
    
    # Calculate total score for Task 3
    task3_score = comparison_score + patterns_score + research_score + recommendation_score
    
    feedback["futures_spot_comparison"] = {
        "score": comparison_score,
        "max_score": 6
    }
    
    feedback["market_patterns"] = {
        "score": patterns_score,
        "max_score": 6,
        "details": {
            "backwardation_commodities": backwardation_score,
            "contango_commodities": contango_score
        }
    }
    
    feedback["current_futures_research"] = {
        "score": research_score,
        "max_score": 5
    }
    
    feedback["purchase_timing_recommendation"] = {
        "score": recommendation_score,
        "max_score": 8
    }
    
    return {
        "score": task3_score,
        "max_score": max_score,
        "passing_score": 17,
        "passed": task3_score >= 17,
        "feedback": feedback
    }

def evaluate_market_conditions(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 4: Market Conditions Assessment."""
    score = 0
    max_score = 25
    feedback = {}
    
    # Market condition summary (5 points)
    summary_score = 0
    key_summary = answer_key["task4"]["market_condition_summary"].lower()
    submission_summary = submission["task4"]["market_condition_summary"].lower()
    
    # Check for key elements in summary
    key_elements = [
        "electronic components",
        "severe constraints",
        "stainless steel",
        "lead times",
        "inventory levels"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_summary)
    summary_score = min(5, (element_matches / len(key_elements)) * 5)
    
    # Supply constrained materials (6 points)
    constrained_score = 0
    correct_materials = set(m.lower() for m in answer_key["task4"]["supply_constrained_materials"])
    submitted_materials = set(m.lower() for m in submission["task4"]["supply_constrained_materials"] if m)
    
    if submitted_materials:
        # Calculate intersection of correct and submitted materials
        matching_materials = correct_materials.intersection(submitted_materials)
        constrained_score = min(6, (len(matching_materials) / len(correct_materials)) * 6)
    
    # Market research findings (4 points)
    # This requires evaluating the quality of web research, which is subjective
    research_score = 0
    if "market_research_findings" in submission["task4"] and submission["task4"]["market_research_findings"].strip():
        research_content = submission["task4"]["market_research_findings"].lower()
        # Check if it contains relevant terms
        relevant_terms = ["market", "supply", "electronic", "components", "steel", "manufacturing"]
        term_matches = sum(1 for term in relevant_terms if term in research_content)
        research_score = min(4, (term_matches / len(relevant_terms)) * 4)
    
    # Procurement strategy (6 points)
    strategy_score = 0
    key_strategy = answer_key["task4"]["procurement_strategy"].lower()
    submission_strategy = submission["task4"]["procurement_strategy"].lower()
    
    # Check for key elements in strategy
    key_elements = [
        "tiered",
        "approach",
        "electronic components",
        "immediate",
        "buffer stock",
        "domestic suppliers",
        "inventory"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_strategy)
    strategy_score = min(6, (element_matches / len(key_elements)) * 6)
    
    # Strategy justification (4 points)
    justification_score = 0
    key_justification = answer_key["task4"]["strategy_justification"].lower()
    submission_justification = submission["task4"]["strategy_justification"].lower()
    
    # Check for key elements in justification
    key_elements = [
        "warehouse capacity",
        "constraints",
        "suppliers",
        "delivery",
        "90%",
        "production"
    ]
    
    element_matches = sum(1 for element in key_elements if element in submission_justification)
    justification_score = min(4, (element_matches / len(key_elements)) * 4)
    
    # Calculate total score for Task 4
    task4_score = summary_score + constrained_score + research_score + strategy_score + justification_score
    
    feedback["market_condition_summary"] = {
        "score": summary_score,
        "max_score": 5
    }
    
    feedback["supply_constrained_materials"] = {
        "score": constrained_score,
        "max_score": 6,
        "correct_materials": answer_key["task4"]["supply_constrained_materials"]
    }
    
    feedback["market_research_findings"] = {
        "score": research_score,
        "max_score": 4
    }
    
    feedback["procurement_strategy"] = {
        "score": strategy_score,
        "max_score": 6
    }
    
    feedback["strategy_justification"] = {
        "score": justification_score,
        "max_score": 4
    }
    
    return {
        "score": task4_score,
        "max_score": max_score,
        "passing_score": 17,
        "passed": task4_score >= 17,
        "feedback": feedback
    }

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the complete submission against the answer key."""
    results = {}
    
    # Evaluate each task
    task1_results = evaluate_price_trends(submission, answer_key)
    task2_results = evaluate_disruption_analysis(submission, answer_key)
    task3_results = evaluate_futures_market(submission, answer_key)
    task4_results = evaluate_market_conditions(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"] + task4_results["score"]
    total_max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"] + task4_results["max_score"]
    overall_percentage = (total_score / total_max_score) * 100
    
    # Determine if overall passing criteria met
    passed_overall = (
        overall_percentage >= 70 and
        task1_results["passed"] and
        task2_results["passed"] and
        task3_results["passed"] and
        task4_results["passed"]
    )
    
    results["candidate_id"] = submission.get("candidate_id", "unknown")
    results["task1"] = task1_results
    results["task2"] = task2_results
    results["task3"] = task3_results
    results["task4"] = task4_results
    results["overall_score"] = round(overall_percentage, 2)
    results["passed"] = passed_overall
    results["total_points"] = total_score
    results["max_points"] = total_max_score
    
    return results

def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()