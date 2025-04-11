import json
import os
from typing import Dict, Any, List, Union

def load_json(filename: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        return {}

def save_json(data: Dict[str, Any], filename: str) -> None:
    """Save data as JSON to a file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def evaluate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 1: Industry News Analysis."""
    results = {
        "score": 0,
        "max_score": 30,
        "feedback": [],
        "details": {}
    }
    
    # Check if all three trends are present
    for i in range(1, 4):
        trend_key = f"trend{i}"
        if trend_key not in submission.get("task1", {}):
            results["feedback"].append(f"Missing {trend_key} in task1")
            continue
            
        trend_results = {"points": 0, "max_points": 10, "feedback": []}
        
        # Check if trend title is valid (from the materials)
        valid_titles = [
            "Streaming Platforms Shift to Sports Rights Acquisition",
            "AI-Generated Content Disrupting Production Economics",
            "Brand Integration Deals Surpass Traditional Endorsements",
            "Olympic Sponsorship Rates Surge Ahead of 2024 Paris Games",
            "Podcast Talent Acquisition Heats Up"
        ]
        
        title = submission["task1"][trend_key].get("title", "")
        if any(title.lower() in valid_title.lower() for valid_title in valid_titles):
            trend_results["points"] += 2
            trend_results["feedback"].append("Correctly identified a valid trend")
        else:
            trend_results["feedback"].append("Trend title not found in provided materials")
        
        # Check source citation
        valid_sources = [
            "Entertainment Business Weekly",
            "Digital Media Today", 
            "Marketing Insider",
            "Sports Business Journal",
            "Audio Industry Report"
        ]
        
        source = submission["task1"][trend_key].get("source", "")
        if any(source.lower() in valid_source.lower() for valid_source in valid_sources):
            trend_results["points"] += 2
            trend_results["feedback"].append("Correctly cited a valid source")
        else:
            trend_results["feedback"].append("Source citation does not match materials")
        
        # Check impact score
        impact_score = submission["task1"][trend_key].get("impact_score", 0)
        if isinstance(impact_score, int) and 1 <= impact_score <= 10:
            if 6 <= impact_score <= 10:
                trend_results["points"] += 2
                trend_results["feedback"].append("Provided reasonable impact score (6-10)")
            else:
                trend_results["points"] += 1
                trend_results["feedback"].append("Impact score (1-5) seems low for a major trend")
        else:
            trend_results["feedback"].append("Impact score must be an integer between 1-10")
        
        # Check implications
        implications = submission["task1"][trend_key].get("key_implications", [])
        if len(implications) == 3:
            implication_points = min(4, sum(1 for imp in implications if len(imp) > 10))
            trend_results["points"] += implication_points
            if implication_points == 4:
                trend_results["feedback"].append("Provided 3 substantive implications")
            else:
                trend_results["feedback"].append(f"Provided {implication_points} substantive implications")
        else:
            trend_results["feedback"].append(f"Expected 3 implications, found {len(implications)}")
        
        results["score"] += trend_results["points"]
        results["details"][trend_key] = trend_results
    
    return results

def evaluate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 2: Deal Structure Comparison."""
    results = {
        "score": 0,
        "max_score": 35,
        "feedback": [],
        "details": {}
    }
    
    if "deal_comparison" not in submission.get("task2", {}):
        results["feedback"].append("Missing deal_comparison in task2")
        return results
    
    deal_comp = submission["task2"]["deal_comparison"]
    key_comp = answer_key["task2"]["deal_comparison"]
    
    # Check compensation calculations
    comp_results = {"points": 0, "max_points": 10, "feedback": []}
    
    # Deal 1 compensation
    deal1_comp = deal_comp.get("deal1_compensation", 0)
    if isinstance(deal1_comp, int):
        # Allow 10% margin of error
        if abs(deal1_comp - key_comp["deal1_compensation"]) <= key_comp["deal1_compensation"] * 0.1:
            comp_results["points"] += 5
            comp_results["feedback"].append("Deal 1 compensation correctly calculated")
        else:
            comp_results["feedback"].append("Deal 1 compensation calculation incorrect")
    else:
        comp_results["feedback"].append("Deal 1 compensation must be an integer")
    
    # Deal 2 compensation
    deal2_comp = deal_comp.get("deal2_compensation", 0)
    if isinstance(deal2_comp, int):
        # Allow 10% margin of error
        if abs(deal2_comp - key_comp["deal2_compensation"]) <= key_comp["deal2_compensation"] * 0.1:
            comp_results["points"] += 5
            comp_results["feedback"].append("Deal 2 compensation correctly calculated (including performance bonus)")
        else:
            # Check if they missed the performance bonus
            if abs(deal2_comp - 3000000) <= 300000:
                comp_results["points"] += 2
                comp_results["feedback"].append("Deal 2 base compensation correct but missed performance bonus")
            else:
                comp_results["feedback"].append("Deal 2 compensation calculation incorrect")
    else:
        comp_results["feedback"].append("Deal 2 compensation must be an integer")
    
    results["score"] += comp_results["points"]
    results["details"]["compensation"] = comp_results
    
    # Check term lengths
    term_results = {"points": 0, "max_points": 10, "feedback": []}
    
    # Deal 1 term
    deal1_term = deal_comp.get("deal1_term_length", 0)
    if deal1_term == key_comp["deal1_term_length"]:
        term_results["points"] += 5
        term_results["feedback"].append("Deal 1 term length correct (36 months)")
    else:
        term_results["feedback"].append(f"Deal 1 term length incorrect (should be 36 months, got {deal1_term})")
    
    # Deal 2 term
    deal2_term = deal_comp.get("deal2_term_length", 0)
    if deal2_term == key_comp["deal2_term_length"]:
        term_results["points"] += 5
        term_results["feedback"].append("Deal 2 term length correct (24 months)")
    else:
        term_results["feedback"].append(f"Deal 2 term length incorrect (should be 24 months, got {deal2_term})")
    
    results["score"] += term_results["points"]
    results["details"]["term_length"] = term_results
    
    # Check rights retained
    rights_results = {"points": 0, "max_points": 10, "feedback": []}
    
    # Deal 1 rights
    deal1_rights = deal_comp.get("deal1_rights_retained", [])
    if len(deal1_rights) >= 2:
        valid_rights_count = sum(1 for right in deal1_rights if len(right) > 10)
        if valid_rights_count >= 2:
            rights_results["points"] += 5
            rights_results["feedback"].append("Listed at least 2 substantive rights for Deal 1")
        else:
            rights_results["points"] += valid_rights_count
            rights_results["feedback"].append(f"Listed only {valid_rights_count} substantive rights for Deal 1")
    else:
        rights_results["feedback"].append("Insufficient rights listed for Deal 1")
    
    # Deal 2 rights
    deal2_rights = deal_comp.get("deal2_rights_retained", [])
    if len(deal2_rights) >= 2:
        valid_rights_count = sum(1 for right in deal2_rights if len(right) > 10)
        if valid_rights_count >= 2:
            rights_results["points"] += 5
            rights_results["feedback"].append("Listed at least 2 substantive rights for Deal 2")
        else:
            rights_results["points"] += valid_rights_count
            rights_results["feedback"].append(f"Listed only {valid_rights_count} substantive rights for Deal 2")
    else:
        rights_results["feedback"].append("Insufficient rights listed for Deal 2")
    
    results["score"] += rights_results["points"]
    results["details"]["rights_retained"] = rights_results
    
    # Check more favorable deal
    favorable_results = {"points": 0, "max_points": 5, "feedback": []}
    
    more_favorable = deal_comp.get("more_favorable_deal", "")
    if more_favorable == key_comp["more_favorable_deal"]:
        favorable_results["points"] += 5
        favorable_results["feedback"].append("Correctly identified Deal 2 as more favorable")
    else:
        favorable_results["feedback"].append("Failed to identify Deal 2 as the more favorable deal")
    
    results["score"] += favorable_results["points"]
    results["details"]["more_favorable"] = favorable_results
    
    return results

def evaluate_task3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Task 3: Client Advisory Scenario."""
    results = {
        "score": 0,
        "max_score": 35,
        "feedback": [],
        "details": {}
    }
    
    # Check platform selection
    platform_results = {"points": 0, "max_points": 10, "feedback": []}
    
    platform = submission.get("task3", {}).get("platform_selection", "")
    high_reach_platforms = ["TikTok Creator Marketplace", "YouTube Shorts"]
    medium_reach_platforms = ["Twitch"]
    low_reach_platforms = ["Substack", "Clubhouse", "Twitter Spaces"]
    
    if any(p.lower() in platform.lower() for p in high_reach_platforms):
        platform_results["points"] += 10
        platform_results["feedback"].append(f"Excellent choice of {platform} for audience expansion (1B+ users)")
    elif any(p.lower() in platform.lower() for p in medium_reach_platforms):
        platform_results["points"] += 5
        platform_results["feedback"].append(f"{platform} is a reasonable choice but has smaller reach than optimal options")
    elif any(p.lower() in platform.lower() for p in low_reach_platforms):
        platform_results["points"] += 2
        platform_results["feedback"].append(f"{platform} has limited reach for audience expansion purposes")
    else:
        platform_results["feedback"].append(f"Platform '{platform}' not found in provided materials")
    
    results["score"] += platform_results["points"]
    results["details"]["platform_selection"] = platform_results
    
    # Check compensation recommendation
    comp_results = {"points": 0, "max_points": 10, "feedback": []}
    
    comp_rec = submission.get("task3", {}).get("compensation_recommendation", 0)
    
    # Define appropriate ranges based on platform
    platform_ranges = {
        "tiktok": (25000, 50000),
        "youtube": (20000, 45000),
        "twitch": (10000, 30000),
        "substack": (5000, 20000),
        "clubhouse": (5000, 15000),
        "twitter": (5000, 15000)
    }
    
    # Determine which platform range to use
    selected_range = None
    for p_key, p_range in platform_ranges.items():
        if p_key.lower() in platform.lower():
            selected_range = p_range
            break
    
    if selected_range and isinstance(comp_rec, int):
        if selected_range[0] <= comp_rec <= selected_range[1]:
            comp_results["points"] += 10
            comp_results["feedback"].append(f"Compensation recommendation ({comp_rec}) is appropriate for mid-tier talent on {platform}")
        elif comp_rec > 0:
            # Outside range but still reasonable
            comp_results["points"] += 5
            comp_results["feedback"].append(f"Compensation recommendation ({comp_rec}) is outside typical range for mid-tier talent")
        else:
            comp_results["feedback"].append("Compensation must be a positive integer")
    else:
        comp_results["feedback"].append("Could not evaluate compensation recommendation")
    
    results["score"] += comp_results["points"]
    results["details"]["compensation_recommendation"] = comp_results
    
    # Check rights recommendation
    rights_results = {"points": 0, "max_points": 7, "feedback": []}
    
    rights_rec = submission.get("task3", {}).get("rights_recommendation", [])
    if len(rights_rec) == 2:
        valid_rights_count = sum(1 for right in rights_rec if len(right) > 10)
        if valid_rights_count == 2:
            rights_results["points"] += 7
            rights_results["feedback"].append("Provided 2 substantive rights recommendations")
        else:
            rights_results["points"] += valid_rights_count * 3
            rights_results["feedback"].append(f"Provided {valid_rights_count} substantive rights recommendations")
    else:
        rights_results["feedback"].append(f"Expected 2 rights recommendations, found {len(rights_rec)}")
    
    results["score"] += rights_results["points"]
    results["details"]["rights_recommendation"] = rights_results
    
    # Check supporting trend evidence
    trend_results = {"points": 0, "max_points": 8, "feedback": []}
    
    trend_evidence = submission.get("task3", {}).get("supporting_trend_evidence", [])
    if len(trend_evidence) == 2:
        valid_trends_count = sum(1 for trend in trend_evidence if len(trend) > 10)
        if valid_trends_count == 2:
            trend_results["points"] += 8
            trend_results["feedback"].append("Provided 2 substantive supporting trends")
        else:
            trend_results["points"] += valid_trends_count * 4
            trend_results["feedback"].append(f"Provided {valid_trends_count} substantive supporting trends")
    else:
        trend_results["feedback"].append(f"Expected 2 supporting trends, found {len(trend_evidence)}")
    
    results["score"] += trend_results["points"]
    results["details"]["supporting_trend_evidence"] = trend_results
    
    return results

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "task1_results": evaluate_task1(submission, answer_key),
        "task2_results": evaluate_task2(submission, answer_key),
        "task3_results": evaluate_task3(submission, answer_key),
        "overall_feedback": []
    }
    
    # Calculate overall score
    total_score = (
        results["task1_results"]["score"] + 
        results["task2_results"]["score"] + 
        results["task3_results"]["score"]
    )
    
    total_possible = (
        results["task1_results"]["max_score"] + 
        results["task2_results"]["max_score"] + 
        results["task3_results"]["max_score"]
    )
    
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    # Determine if the candidate passed
    passed = results["overall_score"] >= 70
    results["passed"] = passed
    
    # Generate overall feedback
    if passed:
        results["overall_feedback"].append(f"PASSED with a score of {results['overall_score']}%")
    else:
        results["overall_feedback"].append(f"FAILED with a score of {results['overall_score']}%")
    
    # Add task-specific feedback
    for task_num, task_name in [(1, "Industry News Analysis"), (2, "Deal Structure Comparison"), (3, "Client Advisory Scenario")]:
        task_key = f"task{task_num}_results"
        task_score = results[task_key]["score"]
        task_max = results[task_key]["max_score"]
        task_percent = round((task_score / task_max) * 100, 2)
        
        results["overall_feedback"].append(f"Task {task_num} ({task_name}): {task_score}/{task_max} points ({task_percent}%)")
    
    # Check for critical errors
    critical_errors = []
    
    # Critical error 1: Missing performance bonus in Deal 2
    deal2_comp = submission.get("task2", {}).get("deal_comparison", {}).get("deal2_compensation", 0)
    if abs(deal2_comp - 3000000) <= 300000:  # They only counted base compensation
        critical_errors.append("Failed to account for performance bonus in Deal 2 compensation")
    
    # Critical error 2: Incorrect favorable deal identification
    more_favorable = submission.get("task2", {}).get("deal_comparison", {}).get("more_favorable_deal", "")
    if more_favorable != "deal2":
        critical_errors.append("Failed to identify Deal 2 as the more favorable deal")
    
    # Critical error 3: Poor platform selection for audience expansion
    platform = submission.get("task3", {}).get("platform_selection", "")
    high_reach_platforms = ["TikTok Creator Marketplace", "YouTube Shorts"]
    if not any(p.lower() in platform.lower() for p in high_reach_platforms):
        critical_errors.append(f"Selected {platform} which has limited reach when audience expansion was the goal")
    
    if critical_errors:
        results["critical_errors"] = critical_errors
        results["overall_feedback"].append("CRITICAL ERRORS IDENTIFIED:")
        for error in critical_errors:
            results["overall_feedback"].append(f"- {error}")
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json(results, "test_results.json")
    print(f"Evaluation complete. Results saved to 'test_results.json'.")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results.get('passed', False) else 'FAILED'}")

if __name__ == "__main__":
    main()