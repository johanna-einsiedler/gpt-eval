import json
import sys
import re
from datetime import datetime, timedelta


def count_words(text):
    if not text:
        return 0
    return len(re.findall(r'\b\w+\b', text))


def is_date_within_range(date_str, months=6):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(days=30 * months)
        return date >= cutoff_date
    except (ValueError, TypeError):
        return False


def is_date_within_30_days(date_str):
    return is_date_within_range(date_str, months=1)


def validate_json_format(submission):
    required_structure = {
        "task1": {
            "developments": [
                {
                    "headline": str,
                    "source": str,
                    "date": str,
                    "summary": str,
                    "impact": str,
                    "significance_rating": int,
                    "rating_justification": str
                }
            ]
        },
        "task2": {
            "deal_comparison": {
                "deal1": {
                    "talent_name": str,
                    "industry_sector": str,
                    "deal_partner": str,
                    "announcement_date": str,
                    "structure": str,
                    "compensation_model": str,
                    "rights_arrangement": str,
                    "notable_terms": str,
                    "innovative_aspect": str,
                    "sources": list
                },
                "deal2": {
                    "talent_name": str,
                    "industry_sector": str,
                    "deal_partner": str,
                    "announcement_date": str,
                    "structure": str,
                    "compensation_model": str,
                    "rights_arrangement": str,
                    "notable_terms": str,
                    "innovative_aspect": str,
                    "sources": list
                },
                "comparison_insights": str
            }
        },
        "task3": {
            "trend_analysis": {
                "trend_name": str,
                "trend_description": str,
                "supporting_evidence": list,
                "business_impact": str,
                "client_opportunities": list,
                "recommended_actions": list,
                "monitoring_sources": list
            }
        }
    }
    
    format_score = 0
    max_format_score = 10
    
    # Check if all required keys are present
    try:
        if "task1" in submission and "developments" in submission["task1"]:
            if len(submission["task1"]["developments"]) == 3:
                format_score += 2
                
        if "task2" in submission and "deal_comparison" in submission["task2"]:
            if all(key in submission["task2"]["deal_comparison"] for key in ["deal1", "deal2", "comparison_insights"]):
                format_score += 4
                
        if "task3" in submission and "trend_analysis" in submission["task3"]:
            if all(key in submission["task3"]["trend_analysis"] for key in ["trend_name", "trend_description", 
                                                                           "supporting_evidence", "business_impact",
                                                                           "client_opportunities", "recommended_actions", 
                                                                           "monitoring_sources"]):
                format_score += 4
    except (KeyError, TypeError):
        pass
    
    return format_score


def evaluate_task1(submission):
    score = 0
    max_score = 30
    feedback = []
    
    try:
        developments = submission["task1"]["developments"]
        
        if not isinstance(developments, list) or len(developments) < 3:
            feedback.append("Task 1: Fewer than 3 developments provided")
            return score, max_score, feedback
        
        for i, dev in enumerate(developments[:3]):
            dev_score = 0
            dev_feedback = []
            
            # Check if recent (within 30 days)
            if is_date_within_30_days(dev.get("date")):
                dev_score += 2
            else:
                dev_feedback.append(f"Development {i+1}: Not within the past 30 days")
            
            # Check headline and source
            if dev.get("headline") and dev.get("source"):
                dev_score += 1
            else:
                dev_feedback.append(f"Development {i+1}: Missing headline or source")
            
            # Check summary word count (50-75 words)
            summary_words = count_words(dev.get("summary", ""))
            if 40 <= summary_words <= 85:  # Allow some flexibility
                dev_score += 1
            else:
                dev_feedback.append(f"Development {i+1}: Summary word count ({summary_words}) outside desired range (50-75)")
            
            # Check impact word count (75-100 words)
            impact_words = count_words(dev.get("impact", ""))
            if 65 <= impact_words <= 110:  # Allow some flexibility
                dev_score += 1
            else:
                dev_feedback.append(f"Development {i+1}: Impact word count ({impact_words}) outside desired range (75-100)")
            
            # Check significance rating (1-10)
            rating = dev.get("significance_rating")
            if isinstance(rating, int) and 1 <= rating <= 10:
                dev_score += 1
            else:
                dev_feedback.append(f"Development {i+1}: Invalid significance rating")
            
            # Check rating justification
            if dev.get("rating_justification") and len(dev.get("rating_justification", "")) > 10:
                dev_score += 1
            else:
                dev_feedback.append(f"Development {i+1}: Missing or inadequate rating justification")
            
            # Add quality score (subjective, but we'll base on length and completeness)
            quality_score = min(3, dev_score)  # Scale based on previous metrics
            dev_score += quality_score
            
            score += dev_score
            feedback.extend(dev_feedback)
    
    except (KeyError, TypeError):
        feedback.append("Task 1: Invalid or missing data structure")
    
    return score, max_score, feedback


def evaluate_task2(submission):
    score = 0
    max_score = 35
    feedback = []
    
    try:
        deal_comparison = submission["task2"]["deal_comparison"]
        
        # Evaluate deal1
        deal1_score = 0
        deal1 = deal_comparison.get("deal1", {})
        
        # Check if recent (within 6 months)
        if is_date_within_range(deal1.get("announcement_date")):
            deal1_score += 2
        else:
            feedback.append("Deal 1: Not within the past 6 months")
        
        # Check basic information
        if all(deal1.get(field) for field in ["talent_name", "industry_sector", "deal_partner"]):
            deal1_score += 2
        else:
            feedback.append("Deal 1: Missing basic information (talent, sector, or partner)")
        
        # Check deal components
        deal_components = ["structure", "compensation_model", "rights_arrangement", "notable_terms", "innovative_aspect"]
        for component in deal_components:
            if deal1.get(component) and count_words(deal1.get(component, "")) >= 30:
                deal1_score += 1
            else:
                feedback.append(f"Deal 1: Missing or inadequate {component}")
        
        # Check sources
        if isinstance(deal1.get("sources"), list) and len(deal1.get("sources", [])) >= 2:
            deal1_score += 2
        else:
            feedback.append("Deal 1: Fewer than 2 sources provided")
        
        # Quality score
        deal1_quality = min(3, deal1_score // 2)  # Scale based on previous metrics
        deal1_score += deal1_quality
        
        # Evaluate deal2
        deal2_score = 0
        deal2 = deal_comparison.get("deal2", {})
        
        # Check if recent (within 6 months)
        if is_date_within_range(deal2.get("announcement_date")):
            deal2_score += 2
        else:
            feedback.append("Deal 2: Not within the past 6 months")
        
        # Check basic information
        if all(deal2.get(field) for field in ["talent_name", "industry_sector", "deal_partner"]):
            deal2_score += 2
        else:
            feedback.append("Deal 2: Missing basic information (talent, sector, or partner)")
        
        # Check deal components
        for component in deal_components:
            if deal2.get(component) and count_words(deal2.get(component, "")) >= 30:
                deal2_score += 1
            else:
                feedback.append(f"Deal 2: Missing or inadequate {component}")
        
        # Check sources
        if isinstance(deal2.get("sources"), list) and len(deal2.get("sources", [])) >= 2:
            deal2_score += 2
        else:
            feedback.append("Deal 2: Fewer than 2 sources provided")
        
        # Quality score
        deal2_quality = min(3, deal2_score // 2)  # Scale based on previous metrics
        deal2_score += deal2_quality
        
        # Check if deals are from different sectors
        if deal1.get("industry_sector") and deal2.get("industry_sector") and \
           deal1.get("industry_sector").lower() != deal2.get("industry_sector").lower():
            score += 2
        else:
            feedback.append("Deals are not from different entertainment sectors")
        
        # Evaluate comparison insights
        insights = deal_comparison.get("comparison_insights", "")
        insights_words = count_words(insights)
        
        if insights_words >= 80:
            insights_score = 3
        elif insights_words >= 40:
            insights_score = 2
        elif insights_words > 0:
            insights_score = 1
        else:
            insights_score = 0
            feedback.append("Missing comparison insights")
        
        score += deal1_score + deal2_score + insights_score
        
    except (KeyError, TypeError):
        feedback.append("Task 2: Invalid or missing data structure")
    
    return score, max_score, feedback


def evaluate_task3(submission):
    score = 0
    max_score = 35
    feedback = []
    
    try:
        trend_analysis = submission["task3"]["trend_analysis"]
        
        # Check trend name and description
        if trend_analysis.get("trend_name") and len(trend_analysis.get("trend_name", "")) > 5:
            score += 2
        else:
            feedback.append("Missing or inadequate trend name")
        
        description_words = count_words(trend_analysis.get("trend_description", ""))
        if description_words >= 120:
            score += 3
        elif description_words >= 80:
            score += 2
        elif description_words > 0:
            score += 1
        else:
            feedback.append("Missing trend description")
        
        # Check supporting evidence
        evidence = trend_analysis.get("supporting_evidence", [])
        if isinstance(evidence, list) and len(evidence) >= 3:
            evidence_score = min(6, len(evidence) * 2)
            score += evidence_score
        else:
            feedback.append("Fewer than 3 pieces of supporting evidence provided")
        
        # Check business impact
        impact_words = count_words(trend_analysis.get("business_impact", ""))
        if impact_words >= 120:
            score += 4
        elif impact_words >= 80:
            score += 3
        elif impact_words > 0:
            score += 1
        else:
            feedback.append("Missing or inadequate business impact analysis")
        
        # Check client opportunities
        opportunities = trend_analysis.get("client_opportunities", [])
        if isinstance(opportunities, list) and len(opportunities) >= 3:
            opp_score = min(6, len(opportunities) * 2)
            score += opp_score
        else:
            feedback.append("Fewer than 3 client opportunities provided")
        
        # Check recommended actions
        actions = trend_analysis.get("recommended_actions", [])
        if isinstance(actions, list) and len(actions) >= 3:
            action_score = min(6, len(actions) * 2)
            score += action_score
        else:
            feedback.append("Fewer than 3 recommended actions provided")
        
        # Check monitoring sources
        sources = trend_analysis.get("monitoring_sources", [])
        if isinstance(sources, list) and len(sources) >= 3:
            source_score = min(5, len(sources))
            score += source_score
        else:
            feedback.append("Fewer than 3 monitoring sources provided")
        
        # Quality assessment (subjective element)
        quality_score = min(3, score // 10)  # Scale based on previous metrics
        score += quality_score
        
    except (KeyError, TypeError):
        feedback.append("Task 3: Invalid or missing data structure")
    
    return score, max_score, feedback


def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file> <answer_key_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find one of the input files")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in one of the input files")
        sys.exit(1)
    
    # Evaluate format of submission
    format_score = validate_json_format(submission)
    format_max = 10
    
    # Evaluate each task
    task1_score, task1_max, task1_feedback = evaluate_task1(submission)
    task2_score, task2_max, task2_feedback = evaluate_task2(submission)
    task3_score, task3_max, task3_feedback = evaluate_task3(submission)
    
    # Calculate overall score
    total_score = format_score + task1_score + task2_score + task3_score
    total_max = format_max + task1_max + task2_max + task3_max
    overall_percentage = (total_score / total_max) * 100
    
    # Generate result
    result = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "format_score": {
            "score": format_score,
            "max_score": format_max,
            "percentage": (format_score / format_max) * 100
        },
        "task1": {
            "score": task1_score,
            "max_score": task1_max,
            "percentage": (task1_score / task1_max) * 100,
            "feedback": task1_feedback
        },
        "task2": {
            "score": task2_score,
            "max_score": task2_max,
            "percentage": (task2_score / task2_max) * 100,
            "feedback": task2_feedback
        },
        "task3": {
            "score": task3_score,
            "max_score": task3_max,
            "percentage": (task3_score / task3_max) * 100,
            "feedback": task3_feedback
        },
        "total_score": total_score,
        "total_possible": total_max,
        "overall_score": overall_percentage,
        "result": "PASS" if overall_percentage >= 80 else "FAIL"
    }
    
    # Save result to file
    with open("test_results.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    print(f"Result: {result['result']}")


if __name__ == "__main__":
    main()