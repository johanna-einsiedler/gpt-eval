import json
import math
from pathlib import Path

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    """Save data to JSON file"""
    with open(file_path, 'w') as file:
        json.dump(data, ensure_ascii=False, indent=2, fp=file)

def evaluate_section1(submission, key):
    """Evaluate Section 1: Market Indicators Recognition"""
    results = {
        "points_possible": 10,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Question 1: Identify indicators suggesting supply constraints (2 points)
    key_indicators = set(key["section1"]["question1"].lower().split(", "))
    submission_indicators = set(submission["section1"]["question1"].lower().split(", "))
    
    if "manufacturing pmi" in submission_indicators:
        if len(submission_indicators.intersection(key_indicators)) >= 2:
            results["breakdown"]["question1"] = {"points_earned": 1, "points_possible": 2, "comment": "Correctly identified at least 2 indicators"}
            results["points_earned"] += 1
        if len(submission_indicators.intersection(key_indicators)) >= 3:
            results["breakdown"]["question1"] = {"points_earned": 2, "points_possible": 2, "comment": "Correctly identified all 3 indicators"}
            results["points_earned"] += 2
    else:
        results["breakdown"]["question1"] = {"points_earned": 0, "points_possible": 2, "comment": "Failed to identify Manufacturing PMI as a key indicator"}
    
    # Question 2: Price direction and evidence (3 points)
    submission_q2 = submission["section1"]["question2"].lower()
    key_q2 = key["section1"]["question2"].lower()
    
    if submission_q2.startswith("rise") and key_q2.startswith("rise"):
        points = 1
        if "producer price index" in submission_q2 and "increas" in submission_q2:
            points += 2
        elif "producer price" in submission_q2 or "ppi" in submission_q2:
            points += 1
        
        results["breakdown"]["question2"] = {"points_earned": points, "points_possible": 3, 
                                           "comment": "Correct direction with " + ("complete" if points == 3 else "partial") + " evidence"}
        results["points_earned"] += points
    else:
        results["breakdown"]["question2"] = {"points_earned": 0, "points_possible": 3, "comment": "Incorrect price direction"}
    
    # Question 3: Interpret Inventory-to-Sales Ratio (2 points)
    submission_q3 = submission["section1"]["question3"].lower()
    
    points = 0
    if "inventory" in submission_q3 and "sales" in submission_q3:
        if "increase" in submission_q3 or "higher" in submission_q3 or "buildup" in submission_q3:
            points += 1
        if "demand" in submission_q3 or "economic" in submission_q3 or "slowdown" in submission_q3:
            points += 1
    
    results["breakdown"]["question3"] = {"points_earned": points, "points_possible": 2, 
                                       "comment": "Provided " + ("complete" if points == 2 else "partial" if points == 1 else "insufficient") + " interpretation"}
    results["points_earned"] += points
    
    # Question 4: Identify actions (3 points)
    actions = submission["section1"]["question4"]
    points = 0
    
    valid_keywords = ["contract", "negotiat", "supplier", "inventory", "purchas", "price", "stock", "diversif"]
    
    for i, action in enumerate(actions[:2]):
        action_lower = action.lower()
        if any(keyword in action_lower for keyword in valid_keywords) and len(action) > 20:
            points += 1.5
            results["breakdown"][f"question4_action{i+1}"] = {"points_earned": 1.5, "points_possible": 1.5, "comment": "Valid action proposed"}
        else:
            results["breakdown"][f"question4_action{i+1}"] = {"points_earned": 0, "points_possible": 1.5, "comment": "Invalid or insufficient action"}
    
    results["points_earned"] += points
    
    return results

def evaluate_section2(submission, key):
    """Evaluate Section 2: Price Trend Analysis"""
    results = {
        "points_possible": 10,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Question 1: Calculate average prices (3 points)
    submission_avg = submission["section2"]["question1"]
    key_avg = key["section2"]["question1"]
    
    points = 0
    for year in ["2021", "2022", "2023"]:
        # 2% tolerance
        tolerance = key_avg[year] * 0.02
        if abs(submission_avg[year] - key_avg[year]) <= tolerance:
            points += 1
            results["breakdown"][f"question1_{year}"] = {"points_earned": 1, "points_possible": 1, "comment": "Correct average calculation"}
        else:
            results["breakdown"][f"question1_{year}"] = {"points_earned": 0, "points_possible": 1, "comment": "Incorrect average calculation"}
    
    results["points_earned"] += points
    
    # Question 2: Month with highest volatility (2 points)
    submission_q2 = submission["section2"]["question2"].lower()
    key_q2 = key["section2"]["question2"].lower()
    
    if "march" in submission_q2 and "7.5" in submission_q2:
        results["breakdown"]["question2"] = {"points_earned": 2, "points_possible": 2, "comment": "Correctly identified month and volatility"}
        results["points_earned"] += 2
    elif "march" in submission_q2:
        results["breakdown"]["question2"] = {"points_earned": 1, "points_possible": 2, "comment": "Correctly identified month but incorrect volatility"}
        results["points_earned"] += 1
    else:
        results["breakdown"]["question2"] = {"points_earned": 0, "points_possible": 2, "comment": "Incorrect month identification"}
    
    # Question 3: Calculate overall trend percentage (2 points)
    submission_q3 = float(submission["section2"]["question3"])
    key_q3 = float(key["section2"]["question3"])
    
    # 2% tolerance of the absolute value
    tolerance = abs(key_q3) * 0.02
    
    if abs(submission_q3 - key_q3) <= tolerance:
        results["breakdown"]["question3"] = {"points_earned": 2, "points_possible": 2, "comment": "Correct percentage calculation"}
        results["points_earned"] += 2
    else:
        results["breakdown"]["question3"] = {"points_earned": 0, "points_possible": 2, "comment": "Incorrect percentage calculation"}
    
    # Question 4: Predict price range and justify (3 points)
    submission_range = submission["section2"]["question4"]["predicted_range"]
    submission_justification = submission["section2"]["question4"]["justification"]
    
    # Check if range is between $2,100 and $2,300 and width ≤ $150
    range_points = 0
    if (2100 <= submission_range[0] <= 2300 and 
        2100 <= submission_range[1] <= 2300 and
        submission_range[1] - submission_range[0] <= 150):
        range_points = 1
    
    # Check justification
    justification_points = 0
    if len(submission_justification) > 20:
        if ("trend" in submission_justification.lower() and 
            any(term in submission_justification.lower() for term in ["historical", "pattern", "previous", "year"])):
            justification_points = 2
        else:
            justification_points = 1
    
    results["breakdown"]["question4_range"] = {"points_earned": range_points, "points_possible": 1, "comment": "Price range " + ("acceptable" if range_points else "unacceptable")}
    results["breakdown"]["question4_justification"] = {"points_earned": justification_points, "points_possible": 2, "comment": "Justification " + ("complete" if justification_points == 2 else "partial" if justification_points == 1 else "insufficient")}
    
    results["points_earned"] += range_points + justification_points
    
    return results

def evaluate_section3(submission, key):
    """Evaluate Section 3: Supply Chain Disruption Assessment"""
    results = {
        "points_possible": 10,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Question 1: Rank factors (3 points)
    submission_ranking = [item.lower() for item in submission["section3"]["question1"]]
    
    points = 0
    
    # Typhoon must be in top 2
    if any("typhoon" in item for item in submission_ranking[:2]):
        points += 1
    else:
        results["breakdown"]["question1_typhoon"] = {"points_earned": 0, "points_possible": 1, "comment": "Failed to rank typhoon in top 2 concerns"}
    
    # Low inventory must be in top 3
    if any("inventory" in item for item in submission_ranking[:3]):
        points += 1
    else:
        results["breakdown"]["question1_inventory"] = {"points_earned": 0, "points_possible": 1, "comment": "Failed to rank low inventory in top 3 concerns"}
    
    # Competitor's product launch must be 4th or 5th
    if any("competitor" in item or "product launch" in item for item in submission_ranking[3:5]):
        points += 1
    else:
        results["breakdown"]["question1_competitor"] = {"points_earned": 0, "points_possible": 1, "comment": "Failed to rank competitor's product launch as 4th or 5th concern"}
    
    results["breakdown"]["question1"] = {"points_earned": points, "points_possible": 3, "comment": "Ranked " + str(points) + " out of 3 factors correctly"}
    results["points_earned"] += points
    
    # Question 2: Calculate additional inventory needed (2 points)
    submission_q2 = int(submission["section3"]["question2"])
    key_q2 = int(key["section3"]["question2"])
    
    # 5% tolerance
    tolerance = key_q2 * 0.05
    
    if abs(submission_q2 - key_q2) <= tolerance:
        results["breakdown"]["question2"] = {"points_earned": 2, "points_possible": 2, "comment": "Correct calculation of additional inventory"}
        results["points_earned"] += 2
    else:
        results["breakdown"]["question2"] = {"points_earned": 0, "points_possible": 2, "comment": "Incorrect calculation of additional inventory"}
    
    # Question 3: Identify data points to monitor (2 points)
    submission_data_points = [point.lower() for point in submission["section3"]["question3"]]
    
    points = 0
    typhoon_keywords = ["typhoon", "storm", "weather", "natural disaster"]
    supplier_keywords = ["supplier", "production", "semiconductor", "chip"]
    logistics_keywords = ["port", "shipping", "logistics", "transportation", "labor", "strike", "union"]
    
    # At least one data point must relate to the typhoon situation
    if any(any(keyword in data_point for keyword in typhoon_keywords) for data_point in submission_data_points):
        points += 1
    
    # At least one data point must relate to either supplier or logistics
    if any(any(keyword in data_point for keyword in supplier_keywords + logistics_keywords) for data_point in submission_data_points):
        points += 1
    
    results["breakdown"]["question3"] = {"points_earned": points, "points_possible": 2, "comment": "Identified " + str(points) + " out of 2 required data point categories"}
    results["points_earned"] += points
    
    # Question 4: Predict price impact range and rationale (3 points)
    submission_range = submission["section3"]["question4"]["percentage_range"]
    submission_rationale = submission["section3"]["question4"]["rationale"]
    
    # Check if range is reasonable (between 10% and 40%)
    range_points = 0
    if 10 <= submission_range[0] <= 40 and 10 <= submission_range[1] <= 40 and submission_range[0] < submission_range[1]:
        range_points = 1
    
    # Check rationale
    rationale_points = 0
    rationale_lower = submission_rationale.lower()
    
    if len(rationale_lower) > 20:
        if ("inventory" in rationale_lower or "supply" in rationale_lower) and ("typhoon" in rationale_lower or "disruption" in rationale_lower):
            rationale_points = 2
        else:
            rationale_points = 1
    
    results["breakdown"]["question4_range"] = {"points_earned": range_points, "points_possible": 1, "comment": "Price impact range " + ("acceptable" if range_points else "unacceptable")}
    results["breakdown"]["question4_rationale"] = {"points_earned": rationale_points, "points_possible": 2, "comment": "Rationale " + ("complete" if rationale_points == 2 else "partial" if rationale_points == 1 else "insufficient")}
    
    results["points_earned"] += range_points + rationale_points
    
    return results

def evaluate_section4(submission, key):
    """Evaluate Section 4: Futures Market Basics"""
    results = {
        "points_possible": 10,
        "points_earned": 0,
        "breakdown": {}
    }
    
    # Question 1: Identify market structure and explain (3 points)
    submission_q1 = submission["section4"]["question1"].lower()
    
    points = 0
    if "contango" in submission_q1:
        points += 1
        
        if "supply" in submission_q1 and "demand" in submission_q1:
            points += 1
        elif "expect" in submission_q1 or "anticipat" in submission_q1:
            points += 1
            
    results["breakdown"]["question1"] = {"points_earned": points, "points_possible": 3, "comment": "Market structure identification " + ("correct with good explanation" if points >= 2 else "partially correct" if points == 1 else "incorrect")}
    results["points_earned"] += points
    
    # Question 2: Calculate percentage premium/discount (2 points)
    submission_q2 = float(submission["section4"]["question2"])
    key_q2 = float(key["section4"]["question2"])
    
    # 2% tolerance of the absolute value
    tolerance = abs(key_q2) * 0.02
    
    if abs(submission_q2 - key_q2) <= tolerance:
        results["breakdown"]["question2"] = {"points_earned": 2, "points_possible": 2, "comment": "Correct percentage calculation"}
        results["points_earned"] += 2
    else:
        results["breakdown"]["question2"] = {"points_earned": 0, "points_possible": 2, "comment": "Incorrect percentage calculation"}
    
    # Question 3: Interpret declining open interest and volume (2 points)
    submission_q3 = submission["section4"]["question3"].lower()
    
    points = 0
    if "liquidity" in submission_q3 or "volume" in submission_q3 or "interest" in submission_q3:
        points += 1
    if "uncertain" in submission_q3 or "future" in submission_q3 or "long-term" in submission_q3:
        points += 1
    
    results["breakdown"]["question3"] = {"points_earned": points, "points_possible": 2, "comment": "Interpretation " + ("complete" if points == 2 else "partial" if points == 1 else "insufficient")}
    results["points_earned"] += points
    
    # Question 4: Recommend hedging strategy (3 points)
    submission_q4 = submission["section4"]["question4"].lower()
    
    points = 0
    if "contango" in submission_q4 or "backwardation" in submission_q4 or "structur" in submission_q4:
        points += 1
    if "percent" in submission_q4 or "allocation" in submission_q4 or "proportion" in submission_q4:
        points += 1
    if "risk" in submission_q4 or "hedg" in submission_q4:
        points += 1
    
    results["breakdown"]["question4"] = {"points_earned": points, "points_possible": 3, "comment": "Strategy recommendation " + ("complete" if points == 3 else "partial" if points > 0 else "insufficient")}
    results["points_earned"] += points
    
    return results

def main():
    # Paths
    submission_path = Path("test_submission.json")
    key_path = Path("answer_key.json")
    results_path = Path("test_results.json")
    
    # Load files
    try:
        submission = load_json(submission_path)
        key = load_json(key_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in input file")
        return
    
    # Evaluate each section
    section1_results = evaluate_section1(submission, key)
    section2_results = evaluate_section2(submission, key)
    section3_results = evaluate_section3(submission, key)
    section4_results = evaluate_section4(submission, key)
    
    # Calculate total points and percentages
    total_possible = (section1_results["points_possible"] + 
                      section2_results["points_possible"] + 
                      section3_results["points_possible"] + 
                      section4_results["points_possible"])
    
    total_earned = (section1_results["points_earned"] + 
                    section2_results["points_earned"] + 
                    section3_results["points_earned"] + 
                    section4_results["points_earned"])
    
    overall_percentage = (total_earned / total_possible) * 100
    
    # Determine if passed (70% overall and 60% in each section)
    section1_percentage = (section1_results["points_earned"] / section1_results["points_possible"]) * 100
    section2_percentage = (section2_results["points_earned"] / section2_results["points_possible"]) * 100
    section3_percentage = (section3_results["points_earned"] / section3_results["points_possible"]) * 100
    section4_percentage = (section4_results["points_earned"] / section4_results["points_possible"]) * 100
    
    passed = (overall_percentage >= 70 and 
              section1_percentage >= 60 and 
              section2_percentage >= 60 and 
              section3_percentage >= 60 and 
              section4_percentage >= 60)
    
    # Compile results
    results = {
        "candidate_id": submission["candidate_id"],
        "overall_score": round(overall_percentage, 2),
        "passed": passed,
        "total_points": {
            "earned": total_earned,
            "possible": total_possible,
            "percentage": round(overall_percentage, 2)
        },
        "section_scores": {
            "section1": {
                "earned": section1_results["points_earned"],
                "possible": section1_results["points_possible"],
                "percentage": round(section1_percentage, 2),
                "passed": section1_percentage >= 60,
                "details": section1_results["breakdown"]
            },
            "section2": {
                "earned": section2_results["points_earned"],
                "possible": section2_results["points_possible"],
                "percentage": round(section2_percentage, 2),
                "passed": section2_percentage >= 60,
                "details": section2_results["breakdown"]
            },
            "section3": {
                "earned": section3_results["points_earned"],
                "possible": section3_results["points_possible"],
                "percentage": round(section3_percentage, 2),
                "passed": section3_percentage >= 60,
                "details": section3_results["breakdown"]
            },
            "section4": {
                "earned": section4_results["points_earned"],
                "possible": section4_results["points_possible"],
                "percentage": round(section4_percentage, 2),
                "passed": section4_percentage >= 60,
                "details": section4_results["breakdown"]
            }
        }
    }
    
    # Save results
    save_json(results, results_path)
    print(f"Evaluation completed. Results saved to {results_path}")

if __name__ == "__main__":
    main()