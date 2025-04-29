import json
import os
import re
from datetime import datetime

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return None

def calculate_section1_scores(submission, answer_key):
    """Calculate scores for Section 1: Scenario Analysis."""
    scores = {}
    
    # Question 1.1.1 (8 points)
    question = "question1_1_1"
    scores[question] = {"max_points": 8, "points": 0, "comments": []}
    
    try:
        # Check if numeric values are close to answer key
        supplier_a = abs(submission["section1"][question]["supplier_a_total_cost"] - 
                          answer_key["section1"][question]["supplier_a_total_cost"])
        supplier_b = abs(submission["section1"][question]["supplier_b_total_cost"] - 
                          answer_key["section1"][question]["supplier_b_total_cost"])
        supplier_c = abs(submission["section1"][question]["supplier_c_total_cost"] - 
                          answer_key["section1"][question]["supplier_c_total_cost"])
        
        # Calculations present
        has_calculations = bool(submission["section1"][question].get("calculations", "").strip())
        
        # Determine score
        if max(supplier_a, supplier_b, supplier_c) < 100 and has_calculations:
            scores[question]["points"] = 8
            scores[question]["comments"].append("Correct calculations with work shown.")
        elif max(supplier_a, supplier_b, supplier_c) < 1000 and has_calculations:
            scores[question]["points"] = 5.6  # 70% credit
            scores[question]["comments"].append("Correct methodology with minor calculation errors.")
        elif has_calculations:
            scores[question]["points"] = 2.4  # 30% credit
            scores[question]["comments"].append("Incorrect methodology but some understanding demonstrated.")
        else:
            scores[question]["comments"].append("Missing calculations or completely incorrect approach.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 1.1.2 (6 points)
    question = "question1_1_2"
    scores[question] = {"max_points": 6, "points": 0, "comments": []}
    
    try:
        correct_ranking = answer_key["section1"][question]["ranking"]
        submission_ranking = submission["section1"][question]["ranking"]
        has_justification = bool(submission["section1"][question].get("justification", "").strip())
        
        if submission_ranking == correct_ranking and has_justification:
            scores[question]["points"] = 6
            scores[question]["comments"].append("Correct ranking with appropriate justification.")
        elif has_justification:
            scores[question]["points"] = 3  # 50% credit
            scores[question]["comments"].append("Ranking errors with reasonable justification.")
        else:
            scores[question]["comments"].append("Incorrect ranking without logical justification.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 1.2.1 (6 points)
    question = "question1_2_1"
    scores[question] = {"max_points": 6, "points": 0, "comments": []}
    
    try:
        # Check if numeric values are close to answer key
        supplier_x = abs(submission["section1"][question]["supplier_x_landed_cost"] - 
                         answer_key["section1"][question]["supplier_x_landed_cost"])
        supplier_y = abs(submission["section1"][question]["supplier_y_landed_cost"] - 
                         answer_key["section1"][question]["supplier_y_landed_cost"])
        supplier_z = abs(submission["section1"][question]["supplier_z_landed_cost"] - 
                         answer_key["section1"][question]["supplier_z_landed_cost"])
        
        # Calculations present
        has_calculations = bool(submission["section1"][question].get("calculations", "").strip())
        
        # Determine score
        if max(supplier_x, supplier_y, supplier_z) < 0.1 and has_calculations:
            scores[question]["points"] = 6
            scores[question]["comments"].append("Correct calculations with work shown.")
        elif max(supplier_x, supplier_y, supplier_z) < 0.5 and has_calculations:
            scores[question]["points"] = 4.2  # 70% credit
            scores[question]["comments"].append("Correct methodology with minor calculation errors.")
        elif has_calculations:
            scores[question]["points"] = 1.8  # 30% credit
            scores[question]["comments"].append("Incorrect methodology but some understanding demonstrated.")
        else:
            scores[question]["comments"].append("Missing calculations or completely incorrect approach.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 1.2.2 (10 points) - Critical question
    question = "question1_2_2"
    scores[question] = {"max_points": 10, "points": 0, "comments": [], "critical": True}
    
    try:
        # Compare supplier selection
        correct_supplier = answer_key["section1"][question]["most_economical_supplier"]
        submission_supplier = submission["section1"][question]["most_economical_supplier"]
        
        # Check calculations
        has_calculations = bool(submission["section1"][question].get("calculations", "").strip())
        calc_text = submission["section1"][question].get("calculations", "")
        
        # Check for consideration of key factors
        factors_considered = 0
        key_factors = ["minimum order", "defect", "on-time delivery", "storage"]
        for factor in key_factors:
            if factor.lower() in calc_text.lower():
                factors_considered += 1
        
        if submission_supplier == correct_supplier and has_calculations and factors_considered >= 3:
            scores[question]["points"] = 10
            scores[question]["comments"].append("Correct supplier selection with thorough analysis.")
        elif has_calculations and factors_considered >= 2:
            # If they selected a different supplier but showed good work
            if submission_supplier != correct_supplier:
                scores[question]["points"] = 7  # 70% credit
                scores[question]["comments"].append("Different supplier selected but reasonable analysis approach.")
            else:
                scores[question]["points"] = 8  # 80% credit
                scores[question]["comments"].append("Correct supplier with some factors missing from analysis.")
        elif has_calculations:
            scores[question]["points"] = 3  # 30% credit
            scores[question]["comments"].append("Basic calculations present but incomplete analysis.")
        else:
            scores[question]["comments"].append("Missing calculations or completely incorrect approach.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    return scores

def calculate_section2_scores(submission, answer_key):
    """Calculate scores for Section 2: Evaluation Methodology."""
    scores = {}
    
    # Question 2.1 (10 points)
    question = "question2_1"
    scores[question] = {"max_points": 10, "points": 0, "comments": []}
    
    try:
        # Check if 5 criteria are provided
        criteria_count = len(submission["section2"][question]["criteria"])
        
        if criteria_count == 5:
            # Check if each criterion has an explanation
            valid_criteria = 0
            for criterion in submission["section2"][question]["criteria"]:
                if (criterion.get("criterion", "").strip() and 
                    criterion.get("explanation", "").strip()):
                    valid_criteria += 1
            
            # Score based on valid criteria with explanations
            scores[question]["points"] = (valid_criteria / 5) * 10
            
            if valid_criteria == 5:
                scores[question]["comments"].append("Complete list of criteria with thorough explanations.")
            elif valid_criteria >= 3:
                scores[question]["comments"].append("Most criteria provided with explanations.")
            else:
                scores[question]["comments"].append("Several criteria missing or lacking explanations.")
        else:
            proportion = min(criteria_count / 5, 1.0)
            scores[question]["points"] = proportion * 7  # Max 7 points if count is wrong
            scores[question]["comments"].append(f"Expected 5 criteria, found {criteria_count}.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 2.2 (8 points) - Critical question
    question = "question2_2"
    scores[question] = {"max_points": 8, "points": 0, "comments": [], "critical": True}
    
    try:
        # Check explanation
        has_explanation = bool(submission["section2"][question].get("method_explanation", "").strip())
        
        # Check calculations
        supplier1_total = submission["section2"][question]["supplier1_calculation"]["total_score"]
        supplier2_total = submission["section2"][question]["supplier2_calculation"]["total_score"]
        
        key_supplier1_total = answer_key["section2"][question]["supplier1_calculation"]["total_score"]
        key_supplier2_total = answer_key["section2"][question]["supplier2_calculation"]["total_score"]
        
        selected_supplier = submission["section2"][question]["selected_supplier"]
        correct_supplier = answer_key["section2"][question]["selected_supplier"]
        
        # Calculate accuracy
        total_diff = abs(supplier1_total - key_supplier1_total) + abs(supplier2_total - key_supplier2_total)
        
        if total_diff < 0.1 and selected_supplier == correct_supplier and has_explanation:
            scores[question]["points"] = 8
            scores[question]["comments"].append("Correct calculations and supplier selection with good explanation.")
        elif total_diff < 0.5 and selected_supplier == correct_supplier and has_explanation:
            scores[question]["points"] = 6  # 75% credit
            scores[question]["comments"].append("Minor calculation errors but correct supplier selection.")
        elif selected_supplier == correct_supplier and has_explanation:
            scores[question]["points"] = 4  # 50% credit
            scores[question]["comments"].append("Calculation errors but correct supplier selection.")
        elif has_explanation:
            scores[question]["points"] = 2.4  # 30% credit
            scores[question]["comments"].append("Incorrect methodology but attempt at explanation.")
        else:
            scores[question]["comments"].append("Missing explanation or completely incorrect approach.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 2.3 (7 points)
    question = "question2_3"
    scores[question] = {"max_points": 7, "points": 0, "comments": []}
    
    try:
        # Check if 3 indicators are provided
        indicators_count = len(submission["section2"][question])
        
        if indicators_count == 3:
            # Check if each indicator has an explanation
            valid_indicators = 0
            for indicator in submission["section2"][question]:
                if (indicator.get("indicator", "").strip() and 
                    indicator.get("explanation", "").strip()):
                    valid_indicators += 1
            
            # Score based on valid indicators with explanations
            scores[question]["points"] = (valid_indicators / 3) * 7
            
            if valid_indicators == 3:
                scores[question]["comments"].append("Complete list of indicators with thorough explanations.")
            elif valid_indicators >= 2:
                scores[question]["comments"].append("Most indicators provided with explanations.")
            else:
                scores[question]["comments"].append("Several indicators missing or lacking explanations.")
        else:
            proportion = min(indicators_count / 3, 1.0)
            scores[question]["points"] = proportion * 5  # Max 5 points if count is wrong
            scores[question]["comments"].append(f"Expected 3 indicators, found {indicators_count}.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    return scores

def calculate_section3_scores(submission, answer_key):
    """Calculate scores for Section 3: Information Gathering."""
    scores = {}
    
    # Question 3.1 (5 points)
    question = "question3_1"
    scores[question] = {"max_points": 5, "points": 0, "comments": []}
    
    try:
        # Check if 5 sources are provided
        sources_count = len(submission["section3"][question])
        
        if sources_count == 5:
            # Check if each source is non-empty
            valid_sources = 0
            for source in submission["section3"][question]:
                if source.strip():
                    valid_sources += 1
            
            # Score based on valid sources
            scores[question]["points"] = (valid_sources / 5) * 5
            
            if valid_sources == 5:
                scores[question]["comments"].append("Complete list of 5 relevant information sources.")
            else:
                scores[question]["comments"].append(f"{valid_sources} valid sources provided out of 5.")
        else:
            proportion = min(sources_count / 5, 1.0)
            scores[question]["points"] = proportion * 4  # Max 4 points if count is wrong
            scores[question]["comments"].append(f"Expected 5 sources, found {sources_count}.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 3.2 (10 points)
    question = "question3_2"
    scores[question] = {"max_points": 10, "points": 0, "comments": []}
    
    try:
        methods = ["supplier_site_visits", "third_party_audits", "customer_references", 
                  "industry_certifications", "sample_testing"]
        
        # Check each verification method
        valid_methods = 0
        for method in methods:
            if (method in submission["section3"][question] and
                submission["section3"][question][method].get("strength", "").strip() and
                submission["section3"][question][method].get("limitation", "").strip()):
                valid_methods += 1
        
        # Score based on valid methods
        scores[question]["points"] = (valid_methods / 5) * 10
        
        if valid_methods == 5:
            scores[question]["comments"].append("All verification methods analyzed with strengths and limitations.")
        else:
            scores[question]["comments"].append(f"{valid_methods} methods correctly analyzed out of 5.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 3.3 (5 points)
    question = "question3_3"
    scores[question] = {"max_points": 5, "points": 0, "comments": []}
    
    try:
        # Check steps
        steps_count = len(submission["section3"][question]["steps"])
        
        if steps_count >= 4:
            # Check if steps are non-empty
            valid_steps = 0
            for step in submission["section3"][question]["steps"]:
                if step.strip():
                    valid_steps += 1
            
            if valid_steps >= 4:
                scores[question]["points"] = 5
                scores[question]["comments"].append("Complete and logical steps for resolving the discrepancy.")
            else:
                scores[question]["points"] = (valid_steps / 4) * 5
                scores[question]["comments"].append(f"{valid_steps} valid steps provided out of at least 4 expected.")
        else:
            scores[question]["points"] = (steps_count / 4) * 4  # Max 4 points if fewer steps
            scores[question]["comments"].append(f"Expected at least 4 steps, found {steps_count}.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    return scores

def calculate_section4_scores(submission, answer_key):
    """Calculate scores for Section 4: Decision Making."""
    scores = {}
    
    # Question 4.1 (9 points)
    question = "question4_1"
    scores[question] = {"max_points": 9, "points": 0, "comments": []}
    
    try:
        scenarios = ["medical_devices", "consumer_electronics", "military_equipment"]
        scenario_scores = []
        
        for scenario in scenarios:
            # Check ranking and justification
            has_ranking = "ranking" in submission["section4"][question][scenario]
            has_factors = "factors_in_order" in submission["section4"][question][scenario]
            has_justification = bool(submission["section4"][question][scenario].get("justification", "").strip())
            
            if has_ranking and has_factors and has_justification:
                # Check for logical patterns (don't require exact match)
                if scenario == "medical_devices":
                    # Medical devices should prioritize quality
                    quality_position = None
                    for i, factor in enumerate(submission["section4"][question][scenario]["factors_in_order"]):
                        if "quality" in factor.lower():
                            quality_position = i
                            break
                    
                    if quality_position is not None and quality_position < 2:  # Quality in top 2
                        scenario_scores.append(3)  # Full credit
                    elif quality_position is not None:
                        scenario_scores.append(1.5)  # Partial credit
                    else:
                        scenario_scores.append(1)  # Minimal credit
                
                elif scenario == "consumer_electronics":
                    # Consumer electronics should prioritize price
                    price_position = None
                    for i, factor in enumerate(submission["section4"][question][scenario]["factors_in_order"]):
                        if "price" in factor.lower():
                            price_position = i
                            break
                    
                    if price_position is not None and price_position < 2:  # Price in top 2
                        scenario_scores.append(3)  # Full credit
                    elif price_position is not None:
                        scenario_scores.append(1.5)  # Partial credit
                    else:
                        scenario_scores.append(1)  # Minimal credit
                
                elif scenario == "military_equipment":
                    # Military should prioritize quality/reliability
                    quality_position = None
                    for i, factor in enumerate(submission["section4"][question][scenario]["factors_in_order"]):
                        if "quality" in factor.lower():
                            quality_position = i
                            break
                    
                    if quality_position is not None and quality_position < 2:  # Quality in top 2
                        scenario_scores.append(3)  # Full credit
                    elif quality_position is not None:
                        scenario_scores.append(1.5)  # Partial credit
                    else:
                        scenario_scores.append(1)  # Minimal credit
            else:
                scenario_scores.append(0)
        
        scores[question]["points"] = sum(scenario_scores)
        
        if scores[question]["points"] == 9:
            scores[question]["comments"].append("All rankings logical with appropriate justifications.")
        elif scores[question]["points"] >= 6:
            scores[question]["comments"].append("Most rankings logical with appropriate justifications.")
        elif scores[question]["points"] >= 3:
            scores[question]["comments"].append("Some rankings logical with appropriate justifications.")
        else:
            scores[question]["comments"].append("Few or no logical rankings with appropriate justifications.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 4.2 (8 points) - Critical question
    question = "question4_2"
    scores[question] = {"max_points": 8, "points": 0, "comments": [], "critical": True}
    
    try:
        # Check calculations
        suppliers = ["p", "q", "r"]
        categories = ["price_weighted", "quality_weighted", "delivery_weighted", 
                     "technical_weighted", "stability_weighted"]
        
        calculation_errors = 0
        for supplier in suppliers:
            supplier_key = f"supplier_{supplier}_calculation"
            
            # Check if individual weighted scores are close to correct
            for category in categories:
                submission_value = submission["section4"][question][supplier_key][category]
                answer_key_value = answer_key["section4"][question][supplier_key][category]
                
                if abs(submission_value - answer_key_value) > 0.1:
                    calculation_errors += 1
            
            # Check total score
            submission_total = submission["section4"][question][supplier_key]["total_score"]
            answer_key_total = answer_key["section4"][question][supplier_key]["total_score"]
            
            if abs(submission_total - answer_key_total) > 0.1:
                calculation_errors += 1
        
        # Check selected supplier
        selected_supplier = submission["section4"][question]["selected_supplier"]
        correct_supplier = answer_key["section4"][question]["selected_supplier"]
        
        has_justification = bool(submission["section4"][question].get("justification", "").strip())
        
        if calculation_errors == 0 and selected_supplier == correct_supplier and has_justification:
            scores[question]["points"] = 8
            scores[question]["comments"].append("Correct calculations and supplier selection with justification.")
        elif calculation_errors <= 3 and selected_supplier == correct_supplier and has_justification:
            scores[question]["points"] = 6  # 75% credit
            scores[question]["comments"].append("Minor calculation errors but correct supplier selection.")
        elif selected_supplier == correct_supplier and has_justification:
            scores[question]["points"] = 4  # 50% credit
            scores[question]["comments"].append("Calculation errors but correct supplier selection.")
        elif has_justification:
            scores[question]["points"] = 2.4  # 30% credit
            scores[question]["comments"].append("Incorrect methodology but attempt at justification.")
        else:
            scores[question]["comments"].append("Missing justification or completely incorrect approach.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    # Question 4.3 (8 points)
    question = "question4_3"
    scores[question] = {"max_points": 8, "points": 0, "comments": []}
    
    try:
        # Check if 3 scenarios are provided
        scenarios_count = len(submission["section4"][question])
        
        if scenarios_count == 3:
            # Check if each scenario has description and factors
            valid_scenarios = 0
            for scenario in submission["section4"][question]:
                if (scenario.get("scenario", "").strip() and 
                    scenario.get("factors_outweighing_price", "").strip()):
                    valid_scenarios += 1
            
            # Score based on valid scenarios
            scores[question]["points"] = (valid_scenarios / 3) * 8
            
            if valid_scenarios == 3:
                scores[question]["comments"].append("Three complete scenarios with factors outweighing price.")
            else:
                scores[question]["comments"].append(f"{valid_scenarios} valid scenarios provided out of 3.")
        else:
            proportion = min(scenarios_count / 3, 1.0)
            scores[question]["points"] = proportion * 6  # Max 6 points if count is wrong
            scores[question]["comments"].append(f"Expected 3 scenarios, found {scenarios_count}.")
    except Exception as e:
        scores[question]["comments"].append(f"Error evaluating: {str(e)}")
    
    return scores

def calculate_overall_score(section_scores):
    """Calculate overall score and section totals."""
    section_totals = {
        "section1": {"max_points": 30, "points": 0},
        "section2": {"max_points": 25, "points": 0},
        "section3": {"max_points": 20, "points": 0},
        "section4": {"max_points": 25, "points": 0}
    }
    
    # Calculate section totals
    for section, questions in section_scores.items():
        for question, data in questions.items():
            section_totals[section]["points"] += data["points"]
    
    # Calculate overall score
    total_points = sum(section["points"] for section in section_totals.values())
    max_points = sum(section["max_points"] for section in section_totals.values())
    overall_score_percentage = (total_points / max_points) * 100
    
    # Check if passed minimum requirements
    passed_overall = overall_score_percentage >= 70
    
    passed_sections = True
    for section, data in section_totals.items():
        section_percentage = (data["points"] / data["max_points"]) * 100
        if section_percentage < 60:
            passed_sections = False
    
    # Check critical questions
    critical_questions_passed = True
    critical_questions = []
    
    for section, questions in section_scores.items():
        for question, data in questions.items():
            if data.get("critical", False):
                question_percentage = (data["points"] / data["max_points"]) * 100
                critical_questions.append({
                    "question": f"{section}_{question}",
                    "percentage": question_percentage,
                    "passed": question_percentage >= 70
                })
                if question_percentage < 70:
                    critical_questions_passed = False
    
    return {
        "overall_score": round(overall_score_percentage, 2),
        "section_scores": section_totals,
        "passed_overall_minimum": passed_overall,
        "passed_section_minimums": passed_sections,
        "critical_questions": critical_questions,
        "passed_critical_questions": critical_questions_passed,
        "final_result": "PASS" if (passed_overall and passed_sections and critical_questions_passed) else "FAIL"
    }

def evaluate_submission(submission_file, answer_key_file):
    """Evaluate the candidate's submission against the answer key."""
    # Load submission and answer key
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    if not submission or not answer_key:
        return {"error": "Failed to load submission or answer key files."}
    
    # Calculate scores for each section
    section_scores = {
        "section1": calculate_section1_scores(submission, answer_key),
        "section2": calculate_section2_scores(submission, answer_key),
        "section3": calculate_section3_scores(submission, answer_key),
        "section4": calculate_section4_scores(submission, answer_key)
    }
    
    # Calculate overall score
    overall_result = calculate_overall_score(section_scores)
    
    # Compile results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question_scores": section_scores,
        "overall_result": overall_result,
        "overall_score": overall_result["overall_score"]
    }
    
    return results

def main():
    """Main function to evaluate submission and save results."""
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"
    
    # Evaluate submission
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results
    try:
        with open(results_file, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    main()