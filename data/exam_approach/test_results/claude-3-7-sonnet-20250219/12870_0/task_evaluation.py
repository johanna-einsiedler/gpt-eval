import json
import re
import datetime
from urllib.parse import urlparse
from dateutil import parser as date_parser

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def validate_url(url):
    """Check if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_date_format(date_str):
    """Check if date is in YYYY-MM-DD format"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def validate_date_range(date_str):
    """Check if date range is properly formatted"""
    pattern = r'^\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def is_within_timeframe(date_str, months=3):
    """Check if date is within specified months from today"""
    try:
        if ' to ' in date_str:
            date_str = date_str.split(' to ')[0]  # Use start date for ranges
        
        date_obj = date_parser.parse(date_str)
        today = datetime.datetime.now()
        delta = today - date_obj
        return delta.days <= months * 30  # Approximate months
    except:
        return False

def is_future_date_within_months(date_str, months=6):
    """Check if date is in the future and within specified months"""
    try:
        if ' to ' in date_str:
            date_str = date_str.split(' to ')[0]  # Use start date for ranges
            
        date_obj = date_parser.parse(date_str)
        today = datetime.datetime.now()
        delta = date_obj - today
        return 0 <= delta.days <= months * 30  # Approximate months
    except:
        return False

def evaluate_task1(submission, answer_key):
    """Evaluate streaming platform analysis"""
    score = 0
    feedback = []
    
    # Check platform identification with market share (6 points)
    if "top_platforms" in submission and len(submission["top_platforms"]) == 3:
        platform_score = 0
        for platform in submission["top_platforms"]:
            if all(key in platform for key in ["name", "market_share", "recent_change"]):
                if platform["name"] and "%" in platform["market_share"]:
                    platform_score += 1
                    if len(platform["recent_change"]) > 20:  # Basic check for substantive content
                        platform_score += 1
        
        score += min(6, platform_score)
        feedback.append(f"Platform identification: {min(6, platform_score)}/6 points")
    else:
        feedback.append("Platform identification: 0/6 points - Missing or incomplete platform data")
    
    # Check impact analysis (8 points)
    if "impact_analysis" in submission and submission["impact_analysis"]:
        analysis_length = len(submission["impact_analysis"])
        if analysis_length > 300:
            analysis_score = 8
        elif analysis_length > 200:
            analysis_score = 6
        elif analysis_length > 100:
            analysis_score = 4
        elif analysis_length > 50:
            analysis_score = 2
        else:
            analysis_score = 0
        
        score += analysis_score
        feedback.append(f"Impact analysis: {analysis_score}/8 points")
    else:
        feedback.append("Impact analysis: 0/8 points - Missing or empty analysis")
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "feedback": feedback
    }

def evaluate_task2(submission, answer_key):
    """Evaluate recent major deal analysis"""
    score = 0
    feedback = []
    
    # Check deal identification and recency (5 points)
    if "deal_details" in submission:
        deal_details = submission["deal_details"]
        deal_score = 0
        
        # Check if all required fields are present
        required_fields = ["talent_name", "company_or_team", "deal_type", "approximate_value", "announcement_date"]
        if all(field in deal_details for field in required_fields):
            deal_score += 2
            
            # Check date format and recency
            if validate_date_format(deal_details["announcement_date"]):
                deal_score += 1
                if is_within_timeframe(deal_details["announcement_date"], 3):
                    deal_score += 2
        
        score += deal_score
        feedback.append(f"Deal identification and recency: {deal_score}/5 points")
    else:
        feedback.append("Deal identification: 0/5 points - Missing deal details")
    
    # Check significance analysis (5 points)
    if "significance" in submission and submission["significance"]:
        significance_length = len(submission["significance"])
        if significance_length > 200:
            significance_score = 5
        elif significance_length > 100:
            significance_score = 3
        elif significance_length > 50:
            significance_score = 1
        else:
            significance_score = 0
        
        score += significance_score
        feedback.append(f"Significance analysis: {significance_score}/5 points")
    else:
        feedback.append("Significance analysis: 0/5 points - Missing or empty analysis")
    
    # Check negotiation lessons (5 points)
    if "negotiation_lessons" in submission and submission["negotiation_lessons"]:
        lessons_length = len(submission["negotiation_lessons"])
        if lessons_length > 200:
            lessons_score = 5
        elif lessons_length > 100:
            lessons_score = 3
        elif lessons_length > 50:
            lessons_score = 1
        else:
            lessons_score = 0
        
        score += lessons_score
        feedback.append(f"Negotiation lessons: {lessons_score}/5 points")
    else:
        feedback.append("Negotiation lessons: 0/5 points - Missing or empty lessons")
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "feedback": feedback
    }

def evaluate_task3(submission, answer_key):
    """Evaluate industry publication review"""
    score = 0
    feedback = []
    
    # Check publication selection and articles (12 points)
    if "publications" in submission and len(submission["publications"]) == 3:
        pub_score = 0
        url_score = 0
        topic_score = 0
        
        for pub in submission["publications"]:
            if all(key in pub for key in ["publication_name", "trending_topic", "article_url", "key_points"]):
                # Publication name (1 point per valid publication)
                if pub["publication_name"]:
                    pub_score += 1
                
                # URL validation (1 point per valid URL)
                if validate_url(pub["article_url"]):
                    url_score += 1
                
                # Trending topic (2 points per substantive topic)
                if pub["trending_topic"] and len(pub["trending_topic"]) > 10:
                    topic_score += 2
        
        score += min(3, pub_score)
        score += min(3, url_score)
        score += min(6, topic_score)
        
        feedback.append(f"Publication selection: {min(3, pub_score)}/3 points")
        feedback.append(f"URL validation: {min(3, url_score)}/3 points")
        feedback.append(f"Trending topic identification: {min(6, topic_score)}/6 points")
    else:
        feedback.append("Publication review: 0/12 points - Missing or incomplete publication data")
    
    # Check key points analysis (8 points)
    if "publications" in submission:
        analysis_score = 0
        
        for pub in submission.get("publications", []):
            if "key_points" in pub and pub["key_points"]:
                points_length = len(pub["key_points"])
                if points_length > 100:
                    analysis_score += 2.5
                elif points_length > 50:
                    analysis_score += 1.5
                elif points_length > 20:
                    analysis_score += 0.5
        
        score += min(8, analysis_score)
        feedback.append(f"Key points analysis: {min(8, analysis_score)}/8 points")
    else:
        feedback.append("Key points analysis: 0/8 points - Missing publication data")
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "feedback": feedback
    }

def evaluate_task4(submission, answer_key):
    """Evaluate emerging revenue stream identification"""
    score = 0
    feedback = []
    
    # Check identification of opportunities (12 points)
    if "emerging_opportunities" in submission and len(submission["emerging_opportunities"]) == 2:
        opportunity_score = 0
        evidence_score = 0
        
        for opportunity in submission["emerging_opportunities"]:
            if all(key in opportunity for key in ["name", "description", "evidence_of_growth", "client_advice"]):
                # Name and description (3 points per opportunity)
                if opportunity["name"] and opportunity["description"]:
                    desc_length = len(opportunity["description"])
                    if desc_length > 100:
                        opportunity_score += 3
                    elif desc_length > 50:
                        opportunity_score += 2
                    elif desc_length > 20:
                        opportunity_score += 1
                
                # Evidence of growth (3 points per opportunity)
                if opportunity["evidence_of_growth"]:
                    evidence_length = len(opportunity["evidence_of_growth"])
                    if evidence_length > 100:
                        evidence_score += 3
                    elif evidence_length > 50:
                        evidence_score += 2
                    elif evidence_length > 20:
                        evidence_score += 1
        
        score += min(6, opportunity_score)
        score += min(6, evidence_score)
        
        feedback.append(f"Opportunity identification: {min(6, opportunity_score)}/6 points")
        feedback.append(f"Growth evidence: {min(6, evidence_score)}/6 points")
    else:
        feedback.append("Opportunity identification: 0/12 points - Missing or incomplete opportunity data")
    
    # Check client advice (8 points)
    if "emerging_opportunities" in submission:
        advice_score = 0
        
        for opportunity in submission.get("emerging_opportunities", []):
            if "client_advice" in opportunity and opportunity["client_advice"]:
                advice_length = len(opportunity["client_advice"])
                if advice_length > 150:
                    advice_score += 4
                elif advice_length > 100:
                    advice_score += 3
                elif advice_length > 50:
                    advice_score += 2
                elif advice_length > 20:
                    advice_score += 1
        
        score += min(8, advice_score)
        feedback.append(f"Client advice: {min(8, advice_score)}/8 points")
    else:
        feedback.append("Client advice: 0/8 points - Missing opportunity data")
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "feedback": feedback
    }

def evaluate_task5(submission, answer_key):
    """Evaluate industry event calendar creation"""
    score = 0
    feedback = []
    
    # Check event selection and details (15 points)
    if "industry_events" in submission and len(submission["industry_events"]) == 5:
        event_score = 0
        date_score = 0
        significance_score = 0
        
        for event in submission["industry_events"]:
            if all(key in event for key in ["event_name", "date", "location", "industry_significance", "relevant_client_types"]):
                # Event name and location (1 point per event)
                if event["event_name"] and event["location"]:
                    event_score += 1
                
                # Date validation (1 point per valid date)
                if validate_date_format(event["date"]) or validate_date_range(event["date"]):
                    date_score += 1
                
                # Industry significance (1 point per substantive description)
                if event["industry_significance"] and len(event["industry_significance"]) > 50:
                    significance_score += 1
        
        score += min(5, event_score)
        score += min(5, date_score)
        score += min(5, significance_score)
        
        feedback.append(f"Event selection: {min(5, event_score)}/5 points")
        feedback.append(f"Date validation: {min(5, date_score)}/5 points")
        feedback.append(f"Industry significance: {min(5, significance_score)}/5 points")
    else:
        feedback.append("Event calendar: 0/15 points - Missing or incomplete event data")
    
    # Check client type matching (5 points)
    if "industry_events" in submission:
        client_score = 0
        
        for event in submission.get("industry_events", []):
            if "relevant_client_types" in event and event["relevant_client_types"]:
                client_length = len(event["relevant_client_types"])
                if client_length > 50:
                    client_score += 1
                elif client_length > 20:
                    client_score += 0.5
        
        score += min(5, client_score)
        feedback.append(f"Client type matching: {min(5, client_score)}/5 points")
    else:
        feedback.append("Client type matching: 0/5 points - Missing event data")
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "feedback": feedback
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission"""
    results = {
        "task1": evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {})),
        "task2": evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {})),
        "task3": evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {})),
        "task4": evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {})),
        "task5": evaluate_task5(submission.get("task5", {}), answer_key.get("task5", {}))
    }
    
    # Calculate overall score
    total_score = sum(task["score"] for task in results.values())
    max_score = sum(task["max_score"] for task in results.values())
    overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    results["overall_score"] = overall_percentage
    results["total_points"] = total_score
    results["max_points"] = max_score
    results["pass_fail"] = "PASS" if overall_percentage >= 70 else "FAIL"
    
    return results

def main():
    # Load files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {results['pass_fail']}")

if __name__ == "__main__":
    main()