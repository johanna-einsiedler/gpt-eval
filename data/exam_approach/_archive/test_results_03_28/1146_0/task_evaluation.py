import json
import re
import os

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json(data, file_path):
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file_prettyify=True, indent=2)
        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving results: {e}")

def evaluate_multiple_choice(candidate_answer, correct_answer):
    """Evaluate multiple choice questions by comparing letter codes."""
    # Normalize answers by removing spaces and sorting the letters
    candidate_norm = ','.join(sorted(candidate_answer.upper().replace(' ', '').split(',')))
    correct_norm = ','.join(sorted(correct_answer.upper().replace(' ', '').split(',')))
    return 1.0 if candidate_norm == correct_norm else 0.0

def count_key_concepts(candidate_answer, key_concepts):
    """Count how many key concepts appear in the candidate's answer."""
    count = 0
    candidate_lower = candidate_answer.lower()
    for concept in key_concepts:
        if concept.lower() in candidate_lower:
            count += 1
    return count

def evaluate_section1(candidate, answer_key, max_points):
    """Evaluate Section 1: Regulatory Knowledge"""
    results = {"points_earned": 0, "comments": {}}
    
    # Q1: Primary federal law (5 points)
    if "federal acquisition regulation" in candidate["q1"].lower() or "far" in candidate["q1"].lower():
        # Check for two key requirements
        key_requirements = [
            "documentation", "record keeping", "transparency", "bidding", 
            "contract reporting", "competition", "certification"
        ]
        req_count = sum(1 for req in key_requirements if req in candidate["q1"].lower())
        points = min(5, 3 + req_count)  # 3 for FAR + up to 2 for requirements
        results["points_earned"] += points
        results["comments"]["q1"] = f"Identified FAR and {req_count} key requirements. Earned {points}/5 points."
    else:
        results["comments"]["q1"] = "Did not correctly identify FAR. Earned 0/5 points."
    
    # Q2: Multiple choice regulations (3 points)
    mc_score = evaluate_multiple_choice(candidate["q2"], answer_key["q2"])
    mc_points = int(mc_score * 3)
    results["points_earned"] += mc_points
    results["comments"]["q2"] = f"{'Correct' if mc_score == 1 else 'Incorrect'} selection. Earned {mc_points}/3 points."
    
    # Q3: Regulatory considerations (7 points)
    key_considerations = [
        "rohs", "hazardous substances", 
        "fcpa", "foreign corrupt practices", 
        "far", "federal acquisition", 
        "dfars", "defense federal", 
        "gdpr", "data privacy", 
        "export control", "itar", "ear",
        "ce marking", 
        "country of origin", "customs", 
        "conflict minerals"
    ]
    consideration_count = min(7, count_key_concepts(candidate["q3"], key_considerations))
    results["points_earned"] += consideration_count
    results["comments"]["q3"] = f"Identified {consideration_count} valid regulatory considerations. Earned {consideration_count}/7 points."
    
    return results

def evaluate_section2(candidate, answer_key, max_points):
    """Evaluate Section 2: Compliance Documentation"""
    results = {"points_earned": 0, "comments": {}}
    
    # Q1: Anti-corruption documents (6 points)
    key_documents = [
        "due diligence", "background check", 
        "certification", "compliance statement", 
        "gift log", "entertainment log", 
        "approval", "third-party agreement", 
        "intermediary agreement"
    ]
    doc_count = min(3, count_key_concepts(candidate["q1"], key_documents))
    doc_points = doc_count * 2  # 2 points per valid document, up to 6
    results["points_earned"] += doc_points
    results["comments"]["q1"] = f"Listed {doc_count} valid documents. Earned {doc_points}/6 points."
    
    # Q2: Record retention (4 points)
    if candidate["q2"].lower().startswith("yes"):
        # Check for regulatory references
        key_references = ["far", "sarbanes", "sox", "ucc", "6 years", "7 years"]
        ref_count = min(2, count_key_concepts(candidate["q2"], key_references))
        retention_points = 2 + ref_count  # 2 for correct yes + up to 2 for references
        results["points_earned"] += retention_points
        results["comments"]["q2"] = f"Correct answer with {ref_count} regulatory references. Earned {retention_points}/4 points."
    else:
        results["comments"]["q2"] = "Incorrect answer. Earned 0/4 points."
    
    # Q3: Purchase order information (5 points)
    key_po_elements = [
        "vendor", "supplier information", "tax id", 
        "product", "service description", "specification", 
        "price", "payment terms", 
        "delivery", "shipping", 
        "contract terms", "conditions", 
        "authorization", "signature", 
        "certification", "compliance"
    ]
    element_count = min(5, count_key_concepts(candidate["q3"], key_po_elements))
    results["points_earned"] += element_count
    results["comments"]["q3"] = f"Listed {element_count} valid PO elements. Earned {element_count}/5 points."
    
    return results

def evaluate_section3(candidate, answer_key, max_points):
    """Evaluate Section 3: Scenario Analysis"""
    results = {"points_earned": 0, "comments": {}}
    
    # Q1: Conflict of interest (10 points)
    coi_points = 0
    
    # Part A: Identify issue (3 points)
    if any(term in candidate["q1"].lower() for term in ["conflict of interest", "ethics", "corruption"]):
        coi_points += 3
        issue_comment = "Correctly identified conflict of interest issue."
    else:
        issue_comment = "Did not clearly identify conflict of interest issue."
    
    # Part B: Procedures (4 points)
    procedure_terms = ["disclosure", "review", "approval", "document", "justification"]
    procedure_count = min(4, count_key_concepts(candidate["q1"], procedure_terms))
    coi_points += procedure_count
    procedure_comment = f"Described {procedure_count}/4 appropriate procedures."
    
    # Part C: Regulations (3 points)
    regulation_terms = ["far", "sarbanes", "sox", "code of ethics", "anti-kickback"]
    regulation_count = min(3, count_key_concepts(candidate["q1"], regulation_terms))
    coi_points += regulation_count
    regulation_comment = f"Referenced {regulation_count}/3 relevant regulations."
    
    results["points_earned"] += coi_points
    results["comments"]["q1"] = f"{issue_comment} {procedure_comment} {regulation_comment} Earned {coi_points}/10 points."
    
    # Q2: Tariff scenario (10 points)
    tariff_points = 0
    
    # Part A: Actions (4 points)
    action_terms = ["review contract", "calculate impact", "alternative supplier", "accelerate", "deliver"]
    action_count = min(4, count_key_concepts(candidate["q2"], action_terms))
    tariff_points += action_count
    action_comment = f"Listed {action_count}/4 appropriate actions."
    
    # Part B: Departments (2 points)
    department_terms = ["finance", "accounting", "legal", "logistics", "supply chain"]
    dept_count = min(2, count_key_concepts(candidate["q2"], department_terms))
    tariff_points += dept_count
    dept_comment = f"Identified {dept_count}/2 relevant departments."
    
    # Part C: Documentation (4 points)
    doc_terms = ["amendment", "communication", "cost impact", "tariff classification", "update"]
    doc_count = min(4, count_key_concepts(candidate["q2"], doc_terms))
    tariff_points += doc_count
    doc_comment = f"Described {doc_count}/4 documentation requirements."
    
    results["points_earned"] += tariff_points
    results["comments"]["q2"] = f"{action_comment} {dept_comment} {doc_comment} Earned {tariff_points}/10 points."
    
    # Q3: Expired certification (5 points)
    cert_points = 0
    
    # Part A: Legal implications (1.5 points)
    if any(term in candidate["q3"].lower() for term in ["non-compliance", "liability", "violation"]):
        cert_points += 1.5
        legal_comment = "Correctly identified legal implications."
    else:
        legal_comment = "Did not clearly identify legal implications."
    
    # Part B: Required steps (2 points)
    step_terms = ["notify", "recertif", "suspend", "alternative"]
    step_count = min(2, count_key_concepts(candidate["q3"], step_terms))
    cert_points += step_count
    step_comment = f"Outlined {step_count}/2 appropriate steps."
    
    # Part C: Documentation (1.5 points)
    cert_doc_terms = ["document discovery", "communication", "incident report", "corrective action"]
    cert_doc_count = min(1.5, count_key_concepts(candidate["q3"], cert_doc_terms) * 0.5)
    cert_points += cert_doc_count
    cert_doc_comment = f"Described {cert_doc_count*2}/3 documentation requirements."
    
    results["points_earned"] += cert_points
    results["comments"]["q3"] = f"{legal_comment} {step_comment} {cert_doc_comment} Earned {cert_points}/5 points."
    
    return results

def evaluate_section4(candidate, answer_key, max_points):
    """Evaluate Section 4: Risk Assessment"""
    results = {"points_earned": 0, "comments": {}}
    
    # Q1: High-risk activities (6 points)
    mc_score = evaluate_multiple_choice(candidate["q1"], answer_key["q1"])
    mc_points = int(mc_score * 6)
    results["points_earned"] += mc_points
    results["comments"]["q1"] = f"{'Correct' if mc_score == 1 else 'Incorrect'} selection. Earned {mc_points}/6 points."
    
    # Q2: Risk areas (10 points) - Critical question requiring full points
    risk_areas = {
        "environmental": ["a"],
        "trade compliance": ["b"],
        "data privacy": ["c"],
        "labor/employment": ["d"],
        "financial/accounting": ["e"]
    }
    
    risk_points = 0
    risk_feedback = []
    
    # Check each part (a-e)
    candidate_q2 = candidate["q2"].lower()
    
    # Check part a (2 points)
    if any(area in candidate_q2 for area in ["environmental", "environment"]):
        risk_points += 2
        risk_feedback.append("Correctly identified Environmental risk for chemicals.")
    else:
        risk_feedback.append("Missed Environmental risk for chemicals.")
    
    # Check part b (2 points)
    if any(area in candidate_q2 for area in ["trade compliance", "trade", "export"]):
        risk_points += 2
        risk_feedback.append("Correctly identified Trade Compliance risk for sanctioned countries.")
    else:
        risk_feedback.append("Missed Trade Compliance risk for sanctioned countries.")
    
    # Check part c (2 points)
    if any(area in candidate_q2 for area in ["data privacy", "privacy", "gdpr"]):
        risk_points += 2
        risk_feedback.append("Correctly identified Data Privacy risk for customer information.")
    else:
        risk_feedback.append("Missed Data Privacy risk for customer information.")
    
    # Check part d (2 points)
    if any(area in candidate_q2 for area in ["labor", "employment"]):
        risk_points += 2
        risk_feedback.append("Correctly identified Labor/Employment risk for staffing services.")
    else:
        risk_feedback.append("Missed Labor/Employment risk for staffing services.")
    
    # Check part e (2 points)
    if any(area in candidate_q2 for area in ["financial", "accounting"]):
        risk_points += 2
        risk_feedback.append("Correctly identified Financial/Accounting risk for payment terms.")
    else:
        risk_feedback.append("Missed Financial/Accounting risk for payment terms.")
    
    results["points_earned"] += risk_points
    results["comments"]["q2"] = f"Identified {risk_points/2}/5 correct risk areas. Earned {risk_points}/10 points."
    
    # Q3: Warning signs (4 points)
    warning_terms = [
        "documentation refusal", "unwilling to provide", 
        "audit resistance", "refusal to allow", "inspection", 
        "below market", "pricing", 
        "regulatory violations", "history", "fines", 
        "unusual payment", "payment terms", 
        "certification resistance"
    ]
    warning_count = min(4, count_key_concepts(candidate["q3"], warning_terms))
    results["points_earned"] += warning_count
    results["comments"]["q3"] = f"Listed {warning_count} valid warning signs. Earned {warning_count}/4 points."
    
    return results

def evaluate_section5(candidate, answer_key, max_points):
    """Evaluate Section 5: Regulatory Monitoring"""
    results = {"points_earned": 0, "comments": {}}
    
    # Q1: Monitoring methods (9 points)
    method_terms = [
        "government agency", "subscription", 
        "association", "membership", 
        "legal", "consultation", "counsel", 
        "training", "webinar", 
        "tracking software", "service"
    ]
    frequency_terms = ["daily", "weekly", "monthly", "quarterly", "annually"]
    
    method_count = min(3, count_key_concepts(candidate["q1"], method_terms))
    frequency_count = min(3, count_key_concepts(candidate["q1"], frequency_terms))
    
    # Each method with frequency is worth 3 points (method + frequency)
    monitoring_points = min(9, method_count * 2 + frequency_count)
    results["points_earned"] += monitoring_points
    results["comments"]["q1"] = f"Described {method_count} methods with {frequency_count} frequencies. Earned {monitoring_points}/9 points."
    
    # Q2: International trade sources (6 points)
    mc_score = evaluate_multiple_choice(candidate["q2"], answer_key["q2"])
    mc_points = int(mc_score * 6)
    results["points_earned"] += mc_points
    results["comments"]["q2"] = f"{'Correct' if mc_score == 1 else 'Incorrect'} selection. Earned {mc_points}/6 points."
    
    # Q3: Industry-specific regulatory bodies (10 points)
    industry_points = 0
    industry_feedback = []
    
    # Electronics industry (up to 3.33 points)
    electronics_body_terms = ["epa", "environmental protection", "eu commission"]
    electronics_reg_terms = ["rohs", "hazardous", "weee"]
    electronics_freq_terms = ["3-5 years", "periodic", "annual"]
    
    if count_key_concepts(candidate["q3"], electronics_body_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified electronics regulatory body.")
    
    if count_key_concepts(candidate["q3"], electronics_reg_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified electronics regulation.")
    
    if count_key_concepts(candidate["q3"], electronics_freq_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly stated electronics update frequency.")
    
    # Medical devices (up to 3.33 points)
    medical_body_terms = ["fda", "food and drug", "medical device regulator"]
    medical_reg_terms = ["quality system", "iso 13485"]
    medical_freq_terms = ["2-3 years", "quarterly"]
    
    if count_key_concepts(candidate["q3"], medical_body_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified medical regulatory body.")
    
    if count_key_concepts(candidate["q3"], medical_reg_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified medical regulation.")
    
    if count_key_concepts(candidate["q3"], medical_freq_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly stated medical update frequency.")
    
    # Office furniture (up to 3.33 points)
    furniture_body_terms = ["bifma", "furniture manufacturers", "consumer product safety"]
    furniture_reg_terms = ["sustainability", "proposition 65", "prop 65"]
    furniture_freq_terms = ["annual", "3-5 years"]
    
    if count_key_concepts(candidate["q3"], furniture_body_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified furniture regulatory body.")
    
    if count_key_concepts(candidate["q3"], furniture_reg_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly identified furniture regulation.")
    
    if count_key_concepts(candidate["q3"], furniture_freq_terms) > 0:
        industry_points += 1
        industry_feedback.append("Correctly stated furniture update frequency.")
    
    # Cap at 10 points maximum
    industry_points = min(10, industry_points)
    results["points_earned"] += industry_points
    results["comments"]["q3"] = f"Earned {industry_points}/10 points for industry-specific regulatory information."
    
    return results

def evaluate_submission(candidate_data, answer_key):
    """Evaluate the entire submission."""
    section_max_points = {
        "section1": 15,
        "section2": 15,
        "section3": 25,
        "section4": 20,
        "section5": 25
    }
    
    results = {
        "candidate_id": candidate_data.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "passing_threshold": 70,
        "total_points": 0,
        "max_points": sum(section_max_points.values()),
        "sections": {}
    }
    
    # Evaluate each section
    evaluation_functions = {
        "section1": evaluate_section1,
        "section2": evaluate_section2,
        "section3": evaluate_section3,
        "section4": evaluate_section4,
        "section5": evaluate_section5
    }
    
    for section, evaluate_func in evaluation_functions.items():
        if section in candidate_data and section in answer_key:
            section_results = evaluate_func(
                candidate_data[section], 
                answer_key[section],
                section_max_points[section]
            )
            
            results["sections"][section] = {
                "max_points": section_max_points[section],
                "points_earned": section_results["points_earned"],
                "percentage": round(section_results["points_earned"] / section_max_points[section] * 100, 2),
                "comments": section_results["comments"]
            }
            
            results["total_points"] += section_results["points_earned"]
        else:
            results["sections"][section] = {
                "max_points": section_max_points[section],
                "points_earned": 0,
                "percentage": 0,
                "comments": {"error": f"Missing {section} data"}
            }
    
    # Calculate overall score
    results["overall_score"] = round(results["total_points"] / results["max_points"] * 100, 2)
    
    # Check passing criteria
    results["passed"] = results["overall_score"] >= results["passing_threshold"]
    
    # Check sectional requirements (at least 50% in each section)
    section_requirements_met = all(
        results["sections"][section]["percentage"] >= 50 
        for section in section_max_points.keys()
    )
    
    # Check critical questions (3.1 and 4.2)
    critical_q31 = results["sections"]["section3"]["comments"].get("q1", "").startswith("Correctly identified conflict")
    critical_q42 = results["sections"]["section4"]["points_earned"] == section_max_points["section4"]
    
    critical_questions_met = critical_q31 and critical_q42
    
    results["passed"] = results["passed"] and section_requirements_met and critical_questions_met
    
    if not section_requirements_met:
        results["failure_reason"] = "Failed to achieve 50% in one or more sections"
    elif not critical_questions_met:
        results["failure_reason"] = "Failed to achieve full points on critical questions (3.1 and 4.2)"
    
    return results

def main():
    """Main function to run the evaluation."""
    # Define file paths
    candidate_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"
    
    # Load data
    candidate_data = load_json(candidate_file)
    answer_key = load_json(answer_key_file)
    
    if not candidate_data or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(candidate_data, answer_key)
    
    # Save results
    save_json(results, results_file)

if __name__ == "__main__":
    main()