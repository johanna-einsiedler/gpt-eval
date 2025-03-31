import json
import os
import re
from math import isclose

def load_json_file(filename):
    """Load and return JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        return None

def calculate_cost_analysis_score(submission, answer_key, scenario):
    """Calculate score for cost analysis section."""
    correct_count = 0
    total_suppliers = 3 if scenario == "scenario1" else 4
    
    # Scenario 1 cost analysis
    if scenario == "scenario1":
        suppliers = {
            "modernOfficeSolutionsTotalCost": 119556.00,
            "ergonomicWorkspaceDesignsTotalCost": 116565.00,
            "corporateFurnishingsIncTotalCost": 114675.00
        }
        
        for supplier, expected_cost in suppliers.items():
            if supplier in submission[scenario]["costAnalysis"]:
                submitted_cost = submission[scenario]["costAnalysis"][supplier]
                # Allow 2% margin of error
                if isclose(submitted_cost, expected_cost, rel_tol=0.02):
                    correct_count += 1
    
    # Scenario 2 TCO calculation
    else:  # scenario2
        suppliers = {
            "precisionMachineryCorpTCO": 136500.00,
            "industrialSystemsInternationalTCO": 138000.00,
            "americanManufacturingTechnologiesTCO": 135700.00,
            "globalEquipmentSolutionsTCO": 139500.00
        }
        
        for supplier, expected_cost in suppliers.items():
            if supplier in submission[scenario]["totalCostOfOwnership"]:
                submitted_cost = submission[scenario]["totalCostOfOwnership"][supplier]
                # Allow 2% margin of error
                if isclose(submitted_cost, expected_cost, rel_tol=0.02):
                    correct_count += 1
    
    # Score based on correct calculations
    if correct_count == total_suppliers:
        return 10
    elif correct_count == total_suppliers - 1:
        return 7
    elif correct_count == total_suppliers - 2:
        return 5 if scenario == "scenario2" else 3
    elif correct_count == 1:
        return 3 if scenario == "scenario2" else 0
    else:
        return 0

def evaluate_supplier_recommendation(submission, answer_key, scenario):
    """Evaluate supplier recommendation and justification."""
    expected_supplier = answer_key[scenario]["recommendedSupplier"]
    submitted_supplier = submission[scenario]["recommendedSupplier"]
    justification = submission[scenario]["justification"].lower()
    
    # Check if recommendation matches answer key
    if submitted_supplier == expected_supplier:
        # Check justification quality
        if len(justification) >= 200 and contains_data_references(justification):
            return 15  # Strong justification
        else:
            return 8   # Weak justification
    else:
        # Check if alternative is well-justified
        if len(justification) >= 200 and contains_data_references(justification):
            # For scenario 1, valid alternative is Modern Office Solutions
            if scenario == "scenario1" and submitted_supplier == "Modern Office Solutions" and "on-time delivery" in justification:
                return 12
            # For scenario 2, valid alternative is Industrial Systems International
            elif scenario == "scenario2" and submitted_supplier == "Industrial Systems International" and "service centers" in justification and "cost" in justification:
                return 12
            else:
                return 4  # Different supplier with weak justification
        else:
            return 4  # Different supplier with weak justification

def contains_data_references(text):
    """Check if text contains references to specific data points."""
    data_indicators = [
        r'\d+%', r'\$\d+', r'\d+\.\d+', r'\d+ years', r'\d+ weeks',
        'quality rating', 'customer satisfaction', 'delivery rate',
        'defect rate', 'warranty', 'certification'
    ]
    
    for indicator in data_indicators:
        if re.search(indicator, text, re.IGNORECASE):
            return True
    return False

def evaluate_quality_delivery_assessment(submission, scenario):
    """Evaluate quality and delivery assessment."""
    if scenario == "scenario1":
        quality_text = submission[scenario]["qualityComparison"].lower()
        delivery_text = submission[scenario]["deliveryCapabilityAssessment"].lower()
        
        # Check for thorough analysis with specific metrics
        quality_metrics = ['quality rating', 'customer satisfaction', 'return rate', 'defect rate']
        delivery_metrics = ['on-time delivery', 'standard delivery', 'rush delivery', 'timeline']
        
        quality_count = sum(1 for metric in quality_metrics if metric in quality_text)
        delivery_count = sum(1 for metric in delivery_metrics if metric in delivery_text)
        
        if quality_count >= 3 and delivery_count >= 3:
            return 15  # Thorough analysis
        elif quality_count >= 2 and delivery_count >= 2:
            return 10  # Good analysis
        elif quality_count >= 1 and delivery_count >= 1:
            return 5   # Basic analysis
        else:
            return 0   # Superficial analysis
    else:  # scenario2
        production_text = submission[scenario]["productionCapabilityAssessment"].lower()
        reputation_text = submission[scenario]["reputationAnalysis"].lower()
        
        # Check for specific company data references
        company_data = ['manufacturing locations', 'lead time', 'annual revenue', 'years in business', 
                        'client', 'production capacity', 'facilities']
        
        data_count = sum(1 for data in company_data if data in production_text or data in reputation_text)
        
        if data_count >= 5:
            return 10  # Thorough analysis
        elif data_count >= 3:
            return 7   # Good analysis
        elif data_count >= 1:
            return 3   # Basic analysis
        else:
            return 0   # Superficial analysis

def evaluate_compliance_analysis(submission):
    """Evaluate compliance analysis for scenario 2."""
    compliance_scores = submission["scenario2"]["complianceAnalysis"]
    
    # Check if scores are provided for all suppliers
    if len(compliance_scores) < 4:
        return 0
    
    # Check if scores are reasonable (between 0-100)
    for supplier, score in compliance_scores.items():
        if not (0 <= score <= 100):
            return 0
    
    # Check if Global Equipment Solutions has highest score
    ges_score = None
    for supplier, score in compliance_scores.items():
        if "globalEquipmentSolutions" in supplier.lower():
            ges_score = score
    
    if ges_score is None:
        return 3  # Basic analysis
    
    # Check if scores align with expected ranking
    expected_ranking = ["Global Equipment Solutions", "Industrial Systems International", 
                        "Precision Machinery Corp", "American Manufacturing Technologies"]
    
    # Extract scores in expected ranking order
    try:
        scores = [
            next(score for supplier, score in compliance_scores.items() if "globalEquipmentSolutions" in supplier.lower()),
            next(score for supplier, score in compliance_scores.items() if "industrialSystems" in supplier.lower()),
            next(score for supplier, score in compliance_scores.items() if "precisionMachinery" in supplier.lower()),
            next(score for supplier, score in compliance_scores.items() if "americanManufacturing" in supplier.lower())
        ]
        
        # Check if scores follow expected pattern (higher to lower)
        if scores[0] >= scores[1] >= scores[2] >= scores[3]:
            return 10  # Thorough analysis with justified scores
        else:
            return 7   # Reasonable analysis
    except:
        return 3  # Basic analysis

def evaluate_risks_mitigation(submission, scenario):
    """Evaluate risk identification and mitigation strategies."""
    risks = submission[scenario]["identifiedRisks"]
    strategies = submission[scenario]["mitigationStrategies"]
    
    # Check number of risks and strategies
    if len(risks) >= 3 and len(strategies) >= 3:
        # Check if risks and strategies are specific (not generic)
        specific_risks = sum(1 for risk in risks if len(risk.split()) >= 5)
        specific_strategies = sum(1 for strategy in strategies if len(strategy.split()) >= 5)
        
        if specific_risks >= 3 and specific_strategies >= 3:
            return 10 if scenario == "scenario1" else 5  # Three relevant risks with specific strategies
        elif specific_risks >= 2 and specific_strategies >= 2:
            return 7 if scenario == "scenario1" else 3   # Two relevant risks with specific strategies
        elif specific_risks >= 1 and specific_strategies >= 1:
            return 3 if scenario == "scenario1" else 1   # One relevant risk with specific strategy
    
    return 0  # Generic risks or no mitigation strategies

def evaluate_submission(submission, answer_key):
    """Evaluate the complete submission and return scores."""
    results = {
        "scenario1": {
            "cost_analysis_score": 0,
            "supplier_recommendation_score": 0,
            "quality_delivery_assessment_score": 0,
            "risks_mitigation_score": 0,
            "total_scenario_score": 0
        },
        "scenario2": {
            "compliance_analysis_score": 0,
            "tco_calculation_score": 0,
            "supplier_recommendation_score": 0,
            "production_reputation_analysis_score": 0,
            "risks_mitigation_score": 0,
            "total_scenario_score": 0
        },
        "overall_score": 0
    }
    
    # Evaluate Scenario 1
    results["scenario1"]["cost_analysis_score"] = calculate_cost_analysis_score(submission, answer_key, "scenario1")
    results["scenario1"]["supplier_recommendation_score"] = evaluate_supplier_recommendation(submission, answer_key, "scenario1")
    results["scenario1"]["quality_delivery_assessment_score"] = evaluate_quality_delivery_assessment(submission, "scenario1")
    results["scenario1"]["risks_mitigation_score"] = evaluate_risks_mitigation(submission, "scenario1")
    
    # Calculate total score for Scenario 1
    results["scenario1"]["total_scenario_score"] = (
        results["scenario1"]["cost_analysis_score"] +
        results["scenario1"]["supplier_recommendation_score"] +
        results["scenario1"]["quality_delivery_assessment_score"] +
        results["scenario1"]["risks_mitigation_score"]
    )
    
    # Evaluate Scenario 2
    results["scenario2"]["compliance_analysis_score"] = evaluate_compliance_analysis(submission)
    results["scenario2"]["tco_calculation_score"] = calculate_cost_analysis_score(submission, answer_key, "scenario2")
    results["scenario2"]["supplier_recommendation_score"] = evaluate_supplier_recommendation(submission, answer_key, "scenario2")
    results["scenario2"]["production_reputation_analysis_score"] = evaluate_quality_delivery_assessment(submission, "scenario2")
    results["scenario2"]["risks_mitigation_score"] = evaluate_risks_mitigation(submission, "scenario2")
    
    # Calculate total score for Scenario 2
    results["scenario2"]["total_scenario_score"] = (
        results["scenario2"]["compliance_analysis_score"] +
        results["scenario2"]["tco_calculation_score"] +
        results["scenario2"]["supplier_recommendation_score"] +
        results["scenario2"]["production_reputation_analysis_score"] +
        results["scenario2"]["risks_mitigation_score"]
    )
    
    # Calculate overall score (percentage)
    total_points = results["scenario1"]["total_scenario_score"] + results["scenario2"]["total_scenario_score"]
    results["overall_score"] = round((total_points / 100) * 100, 2)  # Convert to percentage
    
    return results

def main():
    # Load submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print("Results saved to test_results.json")

if __name__ == "__main__":
    main()