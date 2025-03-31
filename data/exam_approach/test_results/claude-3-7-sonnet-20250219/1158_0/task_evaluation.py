import json
import math
from typing import Dict, List, Any, Union

def load_json(file_path: str) -> Dict:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json(data: Dict, file_path: str) -> None:
    """Save data as JSON to a file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving results to {file_path}: {e}")

def evaluate_market_trend_analysis(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the market trend analysis section."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # High volatility commodities (6 points)
    high_vol_score = 0
    high_vol_details = []
    
    key_commodities = [item["commodity"] for item in answer_key["market_trend_analysis"]["high_volatility_commodities"]]
    submission_commodities = [item["commodity"] for item in submission.get("market_trend_analysis", {}).get("high_volatility_commodities", [])]
    
    for commodity in submission_commodities:
        if commodity in key_commodities:
            high_vol_score += 2
            high_vol_details.append(f"Correctly identified {commodity} as high volatility (+2)")
        else:
            high_vol_details.append(f"Incorrectly identified {commodity} as high volatility (+0)")
    
    results["details"]["high_volatility_commodities"] = {
        "score": high_vol_score,
        "max_score": 6,
        "details": high_vol_details
    }
    
    # Price changes (8 points)
    price_change_score = 0
    price_change_details = []
    
    key_price_changes = {item["commodity"]: item["percentage_change"] for item in answer_key["market_trend_analysis"]["price_changes"]}
    submission_price_changes = {item["commodity"]: item["percentage_change"] for item in submission.get("market_trend_analysis", {}).get("price_changes", [])}
    
    for commodity, key_value in key_price_changes.items():
        if commodity in submission_price_changes:
            submission_value = submission_price_changes[commodity]
            # Allow for small differences in calculation
            if abs(submission_value - key_value) <= 0.5:
                price_change_score += 0.8
                price_change_details.append(f"{commodity}: Correct calculation {submission_value}% (+0.8)")
            else:
                price_change_details.append(f"{commodity}: Incorrect calculation {submission_value}% vs expected {key_value}% (+0)")
        else:
            price_change_details.append(f"{commodity}: Missing calculation (+0)")
    
    results["details"]["price_changes"] = {
        "score": price_change_score,
        "max_score": 8,
        "details": price_change_details
    }
    
    # Seasonal patterns (6 points)
    seasonal_score = 0
    seasonal_details = []
    
    key_patterns = [item["commodity"] for item in answer_key["market_trend_analysis"]["seasonal_patterns"]]
    submission_patterns = submission.get("market_trend_analysis", {}).get("seasonal_patterns", [])
    
    for pattern in submission_patterns:
        commodity = pattern.get("commodity", "")
        if commodity in key_patterns:
            seasonal_score += 3
            seasonal_details.append(f"Correctly identified seasonal pattern for {commodity} (+3)")
        else:
            seasonal_details.append(f"Unrecognized seasonal pattern for {commodity} (+0)")
    
    results["details"]["seasonal_patterns"] = {
        "score": seasonal_score,
        "max_score": 6,
        "details": seasonal_details
    }
    
    results["score"] = high_vol_score + price_change_score + seasonal_score
    return results

def evaluate_supply_risk_assessment(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the supply risk assessment section."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # Disruption risks (9 points)
    risk_score = 0
    risk_details = []
    
    key_risks = [item["risk"].lower() for item in answer_key["supply_risk_assessment"]["disruption_risks"]]
    submission_risks = submission.get("supply_risk_assessment", {}).get("disruption_risks", [])
    
    for i, risk_item in enumerate(submission_risks[:3]):  # Evaluate up to 3 risks
        risk_text = risk_item.get("risk", "").lower()
        # Check if risk description contains key terms from any of the expected risks
        matched = False
        for key_risk in key_risks:
            # Check for keyword matches
            if ("port strike" in risk_text and "port strike" in key_risk) or \
               ("copper mine" in risk_text and "copper mine" in key_risk) or \
               ("silicon" in risk_text and "energy" in risk_text and "silicon" in key_risk):
                risk_score += 3
                risk_details.append(f"Risk {i+1}: Correctly identified disruption risk (+3)")
                matched = True
                break
        
        if not matched:
            risk_details.append(f"Risk {i+1}: Unrecognized disruption risk (+0)")
    
    results["details"]["disruption_risks"] = {
        "score": risk_score,
        "max_score": 9,
        "details": risk_details
    }
    
    # Affected commodities (6 points)
    commodities_score = 0
    commodities_details = []
    
    key_risk_commodities = {item["risk"].lower(): set(item["affected_commodities"]) 
                           for item in answer_key["supply_risk_assessment"]["disruption_risks"]}
    
    for i, risk_item in enumerate(submission_risks[:3]):
        risk_text = risk_item.get("risk", "").lower()
        submission_commodities = set(risk_item.get("affected_commodities", []))
        
        # Match the risk to the correct key risk
        matched_key = None
        for key_risk in key_risk_commodities:
            if ("port strike" in risk_text and "port strike" in key_risk) or \
               ("copper mine" in risk_text and "copper mine" in key_risk) or \
               ("silicon" in risk_text and "energy" in risk_text and "silicon" in key_risk):
                matched_key = key_risk
                break
        
        if matched_key:
            expected_commodities = key_risk_commodities[matched_key]
            if submission_commodities == expected_commodities:
                commodities_score += 2
                commodities_details.append(f"Risk {i+1}: Correctly identified all affected commodities (+2)")
            elif submission_commodities.intersection(expected_commodities):
                commodities_score += 1
                commodities_details.append(f"Risk {i+1}: Partially identified affected commodities (+1)")
            else:
                commodities_details.append(f"Risk {i+1}: Incorrectly identified affected commodities (+0)")
        else:
            commodities_details.append(f"Risk {i+1}: Could not match risk to evaluate commodities (+0)")
    
    results["details"]["affected_commodities"] = {
        "score": commodities_score,
        "max_score": 6,
        "details": commodities_details
    }
    
    # Price impact (5 points)
    impact_score = 0
    impact_details = []
    
    key_risk_impacts = {}
    for item in answer_key["supply_risk_assessment"]["disruption_risks"]:
        key_risk_impacts[item["risk"].lower()] = item["potential_price_impact"]
    
    for i, risk_item in enumerate(submission_risks[:3]):
        risk_text = risk_item.get("risk", "").lower()
        submission_impact = risk_item.get("potential_price_impact", 0)
        
        # Match the risk to the correct key risk
        matched_key = None
        for key_risk in key_risk_impacts:
            if ("port strike" in risk_text and "port strike" in key_risk) or \
               ("copper mine" in risk_text and "copper mine" in key_risk) or \
               ("silicon" in risk_text and "energy" in risk_text and "silicon" in key_risk):
                matched_key = key_risk
                break
        
        if matched_key:
            expected_impact = key_risk_impacts[matched_key]
            if abs(submission_impact - expected_impact) <= 2.5:
                impact_score += 5/3  # 5 points divided by 3 risks
                impact_details.append(f"Risk {i+1}: Price impact within acceptable range (+{5/3:.2f})")
            else:
                impact_details.append(f"Risk {i+1}: Price impact outside acceptable range (+0)")
        else:
            impact_details.append(f"Risk {i+1}: Could not match risk to evaluate price impact (+0)")
    
    results["details"]["price_impact"] = {
        "score": impact_score,
        "max_score": 5,
        "details": impact_details
    }
    
    results["score"] = risk_score + commodities_score + impact_score
    return results

def evaluate_demand_supply_gap(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the demand-supply gap analysis section."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # Inventory coverage (10 points)
    coverage_score = 0
    coverage_details = []
    
    key_coverage = {item["commodity"]: item["coverage_weeks"] 
                   for item in answer_key["demand_supply_gap"]["inventory_coverage"]}
    submission_coverage = {item["commodity"]: item["coverage_weeks"] 
                          for item in submission.get("demand_supply_gap", {}).get("inventory_coverage", [])}
    
    for commodity, key_value in key_coverage.items():
        if commodity in submission_coverage:
            submission_value = submission_coverage[commodity]
            # Allow for small differences in calculation
            if abs(submission_value - key_value) <= 0.5:
                coverage_score += 1
                coverage_details.append(f"{commodity}: Correct calculation {submission_value} weeks (+1)")
            else:
                coverage_details.append(f"{commodity}: Incorrect calculation {submission_value} vs expected {key_value} weeks (+0)")
        else:
            coverage_details.append(f"{commodity}: Missing calculation (+0)")
    
    results["details"]["inventory_coverage"] = {
        "score": coverage_score,
        "max_score": 10,
        "details": coverage_details
    }
    
    # Stockout risk commodities (10 points)
    stockout_score = 0
    stockout_details = []
    
    key_stockout = set(answer_key["demand_supply_gap"]["stockout_risk_commodities"])
    submission_stockout = set(submission.get("demand_supply_gap", {}).get("stockout_risk_commodities", []))
    
    # Calculate points for each correct commodity (3.33 points each)
    correct_count = len(key_stockout.intersection(submission_stockout))
    stockout_score = correct_count * (10/3)
    
    stockout_details.append(f"Correctly identified {correct_count} out of 3 high stockout risk commodities (+{stockout_score:.2f})")
    
    if correct_count < 3:
        missing = key_stockout - submission_stockout
        extra = submission_stockout - key_stockout
        if missing:
            stockout_details.append(f"Missing stockout risk commodities: {', '.join(missing)}")
        if extra:
            stockout_details.append(f"Incorrectly included commodities: {', '.join(extra)}")
    
    results["details"]["stockout_risk_commodities"] = {
        "score": stockout_score,
        "max_score": 10,
        "details": stockout_details
    }
    
    results["score"] = coverage_score + stockout_score
    return results

def evaluate_futures_analysis(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the futures market interpretation section."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # Price increase indicators (8 points)
    indicators_score = 0
    indicators_details = []
    
    key_indicators = set(answer_key["futures_analysis"]["price_increase_indicators"])
    submission_indicators = set(submission.get("futures_analysis", {}).get("price_increase_indicators", []))
    
    correct_count = len(key_indicators.intersection(submission_indicators))
    
    # Full points if at least 6 correct
    if correct_count >= 6:
        indicators_score = 8
        indicators_details.append(f"Correctly identified at least 6 commodities with price increase indicators (+8)")
    else:
        # Partial points based on correct count
        indicators_score = (correct_count / 6) * 8
        indicators_details.append(f"Correctly identified {correct_count} out of 8 commodities with price increase indicators (+{indicators_score:.2f})")
    
    results["details"]["price_increase_indicators"] = {
        "score": indicators_score,
        "max_score": 8,
        "details": indicators_details
    }
    
    # Price spreads (6 points)
    spreads_score = 0
    spreads_details = []
    
    key_spreads = {item["commodity"]: item["spread_percentage"] 
                  for item in answer_key["futures_analysis"]["price_spreads"]}
    submission_spreads = {item["commodity"]: item["spread_percentage"] 
                         for item in submission.get("futures_analysis", {}).get("price_spreads", [])}
    
    for commodity, key_value in key_spreads.items():
        if commodity in submission_spreads:
            submission_value = submission_spreads[commodity]
            # Allow for small differences in calculation
            if abs(submission_value - key_value) <= 0.5:
                spreads_score += 0.6
                spreads_details.append(f"{commodity}: Correct calculation {submission_value}% (+0.6)")
            else:
                spreads_details.append(f"{commodity}: Incorrect calculation {submission_value}% vs expected {key_value}% (+0)")
        else:
            spreads_details.append(f"{commodity}: Missing calculation (+0)")
    
    results["details"]["price_spreads"] = {
        "score": spreads_score,
        "max_score": 6,
        "details": spreads_details
    }
    
    # Forward contract recommendations (6 points)
    contract_score = 0
    contract_details = []
    
    key_recommendations = set(answer_key["futures_analysis"]["forward_contract_recommendations"])
    submission_recommendations = set(submission.get("futures_analysis", {}).get("forward_contract_recommendations", []))
    
    # Check for valid recommendations (must be in the key recommendations or have high spread)
    valid_recommendations = []
    high_spread_commodities = [commodity for commodity, spread in key_spreads.items() if spread >= 5]
    
    for commodity in submission_recommendations:
        if commodity in key_recommendations or commodity in high_spread_commodities:
            valid_recommendations.append(commodity)
    
    # 2 points per valid recommendation, up to 3 recommendations
    valid_count = min(len(valid_recommendations), 3)
    contract_score = valid_count * 2
    
    contract_details.append(f"Made {valid_count} valid forward contract recommendations (+{contract_score})")
    
    results["details"]["forward_contract_recommendations"] = {
        "score": contract_score,
        "max_score": 6,
        "details": contract_details
    }
    
    results["score"] = indicators_score + spreads_score + contract_score
    return results

def evaluate_purchasing_recommendations(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the purchasing recommendations section."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": {}
    }
    
    # Get critical commodities from answer key
    key_critical_commodities = [item["commodity"] for item in answer_key["purchasing_recommendations"]]
    submission_recommendations = submission.get("purchasing_recommendations", [])
    
    # Correct commodities (5 points)
    commodities_score = 0
    commodities_details = []
    
    submission_commodities = [item["commodity"] for item in submission_recommendations]
    correct_commodities = [c for c in submission_commodities if c in key_critical_commodities]
    
    commodities_score = len(correct_commodities)
    commodities_details.append(f"Recommended {len(correct_commodities)} out of 5 critical commodities (+{commodities_score})")
    
    if len(correct_commodities) < 5:
        missing = set(key_critical_commodities) - set(submission_commodities)
        commodities_details.append(f"Missing recommendations for: {', '.join(missing)}")
    
    results["details"]["correct_commodities"] = {
        "score": commodities_score,
        "max_score": 5,
        "details": commodities_details
    }
    
    # Create lookup for key recommendations
    key_recommendations = {item["commodity"]: item for item in answer_key["purchasing_recommendations"]}
    
    # Appropriate timing (5 points)
    timing_score = 0
    timing_details = []
    
    for item in submission_recommendations:
        commodity = item.get("commodity")
        if commodity in key_critical_commodities:
            submission_timing = item.get("timing")
            key_timing = key_recommendations[commodity]["timing"]
            
            # Check if timing is reasonable
            if submission_timing == key_timing:
                timing_score += 1
                timing_details.append(f"{commodity}: Correct timing recommendation '{submission_timing}' (+1)")
            # Allow for one level of difference (immediate vs 30days, or 30days vs 60days)
            elif (submission_timing == "immediate" and key_timing == "30days") or \
                 (submission_timing == "30days" and key_timing == "immediate") or \
                 (submission_timing == "30days" and key_timing == "60days") or \
                 (submission_timing == "60days" and key_timing == "30days"):
                timing_score += 0.5
                timing_details.append(f"{commodity}: Reasonable timing recommendation '{submission_timing}' (+0.5)")
            else:
                timing_details.append(f"{commodity}: Incorrect timing recommendation '{submission_timing}' vs expected '{key_timing}' (+0)")
    
    results["details"]["appropriate_timing"] = {
        "score": timing_score,
        "max_score": 5,
        "details": timing_details
    }
    
    # Reasonable quantity (5 points)
    quantity_score = 0
    quantity_details = []
    
    for item in submission_recommendations:
        commodity = item.get("commodity")
        if commodity in key_critical_commodities:
            submission_quantity = item.get("quantity_percentage")
            key_quantity = key_recommendations[commodity]["quantity_percentage"]
            
            # Check if quantity is reasonable (within 15% of key quantity)
            if submission_quantity is not None and abs(submission_quantity - key_quantity) <= 15:
                quantity_score += 1
                quantity_details.append(f"{commodity}: Reasonable quantity recommendation {submission_quantity}% (+1)")
            else:
                quantity_details.append(f"{commodity}: Questionable quantity recommendation {submission_quantity}% vs expected {key_quantity}% (+0)")
    
    results["details"]["reasonable_quantity"] = {
        "score": quantity_score,
        "max_score": 5,
        "details": quantity_details
    }
    
    # Justified max price (5 points)
    price_score = 0
    price_details = []
    
    for item in submission_recommendations:
        commodity = item.get("commodity")
        if commodity in key_critical_commodities:
            submission_price = item.get("max_price")
            key_price = key_recommendations[commodity]["max_price"]
            
            # Check if price is reasonable (within 5% of key price)
            if submission_price is not None and abs(submission_price - key_price) / key_price <= 0.05:
                price_score += 1
                price_details.append(f"{commodity}: Reasonable max price recommendation ${submission_price} (+1)")
            else:
                price_details.append(f"{commodity}: Questionable max price recommendation ${submission_price} vs expected ${key_price} (+0)")
    
    results["details"]["justified_max_price"] = {
        "score": price_score,
        "max_score": 5,
        "details": price_details
    }
    
    results["score"] = commodities_score + timing_score + quantity_score + price_score
    return results

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "section_results": {}
    }
    
    # Evaluate each section
    results["section_results"]["market_trend_analysis"] = evaluate_market_trend_analysis(submission, answer_key)
    results["section_results"]["supply_risk_assessment"] = evaluate_supply_risk_assessment(submission, answer_key)
    results["section_results"]["demand_supply_gap"] = evaluate_demand_supply_gap(submission, answer_key)
    results["section_results"]["futures_analysis"] = evaluate_futures_analysis(submission, answer_key)
    results["section_results"]["purchasing_recommendations"] = evaluate_purchasing_recommendations(submission, answer_key)
    
    # Calculate total points and overall score
    for section, section_results in results["section_results"].items():
        results["total_points"] += section_results["score"]
    
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Add pass/fail status
    results["passed"] = results["overall_score"] >= 75
    
    # Check section minimums (60% in each section)
    section_minimums_passed = True
    section_minimum_details = []
    
    for section, section_results in results["section_results"].items():
        section_score_percentage = (section_results["score"] / section_results["max_score"]) * 100
        if section_score_percentage < 60:
            section_minimums_passed = False
            section_minimum_details.append(f"{section}: {section_score_percentage:.2f}% (below 60% minimum)")
    
    results["section_minimums_passed"] = section_minimums_passed
    if not section_minimums_passed:
        results["section_minimum_details"] = section_minimum_details
        results["passed"] = False
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load submission or answer key.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json(results, "test_results.json")
    
    # Print summary
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Total Points: {results['total_points']:.2f} / {results['max_points']}")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()