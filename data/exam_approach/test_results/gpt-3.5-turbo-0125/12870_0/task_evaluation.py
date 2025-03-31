import json
from datetime import datetime

def validate_json_structure(candidate_data, answer_key):
    results = {
        "candidate_id": False,
        "industry_trends": [],
        "recent_deals": [],
        "overall_score": 0
    }
    
    # Check candidate ID
    if candidate_data.get("candidate_id") == answer_key.get("candidate_id"):
        results["candidate_id"] = True

    # Validate industry trends
    industry_trends = candidate_data.get("industry_trends", [])
    if isinstance(industry_trends, list) and len(industry_trends) > 0:
        for trend in industry_trends:
            trend_result = {
                "title": False,
                "source": False,
                "summary": False
            }
            if all(key in trend for key in ["title", "source", "summary"]):
                if all(isinstance(trend[key], str) for key in ["title", "source", "summary"]):
                    trend_result = {key: True for key in trend_result}
            results["industry_trends"].append(trend_result)

    # Validate recent deals
    recent_deals = candidate_data.get("recent_deals", [])
    if isinstance(recent_deals, list) and len(recent_deals) > 0:
        for deal in recent_deals:
            deal_result = {
                "deal_title": False,
                "parties_involved": False,
                "date": False,
                "deal_summary": False
            }
            if all(key in deal for key in ["deal_title", "parties_involved", "date", "deal_summary"]):
                if all(isinstance(deal[key], str) for key in ["deal_title", "parties_involved", "deal_summary"]):
                    try:
                        datetime.strptime(deal["date"], "%Y-%m-%d")
                        deal_result = {key: True for key in deal_result}
                    except ValueError:
                        pass
            results["recent_deals"].append(deal_result)

    # Calculate overall score
    total_checks = 1 + len(results["industry_trends"]) * 3 + len(results["recent_deals"]) * 4
    passed_checks = sum(results["candidate_id"]) + sum(
        sum(trend.values()) for trend in results["industry_trends"]
    ) + sum(
        sum(deal.values()) for deal in results["recent_deals"]
    )
    results["overall_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

    return results

def main():
    # Load candidate submission
    with open("test_submission.json", "r") as file:
        candidate_data = json.load(file)

    # Load answer key
    with open("answer_key.json", "r") as file:
        answer_key = json.load(file)

    # Validate and score the submission
    results = validate_json_structure(candidate_data, answer_key)

    # Save results to a JSON file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()