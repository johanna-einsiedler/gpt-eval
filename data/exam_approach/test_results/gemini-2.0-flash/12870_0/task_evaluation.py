import json
from urllib.parse import urlparse

def validate_basic_exam(answer_key_file="answer_key.json", submission_file="test_submission.json"):
    try:
        with open(answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
            answer_key = answer_key_data['answer_key']
    except FileNotFoundError:
        return {"error": f"Answer key file not found: {answer_key_file}"}, 0
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file: {answer_key_file}"}, 0

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file not found: {submission_file}"}, 0
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file: {submission_file}"}, 0

    validation_results = {"task1": [], "task2": {}}
    score = 0
    max_score = 0

    # --- Task 1 Validation ---
    max_score += 6 # Task 1 has max 6 points
    for trend_data in submission.get('task1_trends', []):
        trend_num = trend_data.get('trend_number')
        if trend_num is None:
            validation_results['task1'].append({"error": "Trend number missing"})
            continue

        trend_validation = {"trend_number": trend_num, "points": 0, "feedback": []}
        key_trend_answer = None
        try:
            key_trend_answer = answer_key['task1_trends'][trend_num - 1] # Assuming trend_number starts from 1
        except IndexError:
            trend_validation["feedback"].append(f"Trend {trend_num}: No answer key found for this trend number.")
            validation_results['task1'].append(trend_validation)
            continue

        # Source URL Domain Check
        url = trend_data.get('source_url', '')
        domain = urlparse(url).netloc
        if domain in key_trend_answer['acceptable_source_domains']:
            trend_validation["points"] += 1
            trend_validation["feedback"].append(f"Trend {trend_num}: Source domain OK ({domain})")
        else:
            trend_validation["feedback"].append(f"Trend {trend_num}: Source domain NOT ACCEPTABLE ({domain}). Should be from: {key_trend_answer['acceptable_source_domains']}")

        # Keyword Matching (Trend Description)
        description = trend_data.get('trend_description', '').lower()
        description_keywords_matched = sum(1 for keyword in key_trend_answer['trend_description_keywords'] if keyword in description)
        if description_keywords_matched >= 1: # Reduced threshold to 1 for basic exam, can be adjusted
            trend_validation["points"] += 2 # Increased points for description relevance
            trend_validation["feedback"].append(f"Trend {trend_num}: Description relevant (keywords matched: {description_keywords_matched})")
        else:
            trend_validation["feedback"].append(f"Trend {trend_num}: Description keywords insufficient ({description_keywords_matched} matched, need >= 1)")

        # Keyword Matching (Impact)
        impact = trend_data.get('impact', '').lower()
        impact_keywords_matched = sum(1 for keyword in key_trend_answer['impact_keywords'] if keyword in impact)
        if impact_keywords_matched >= 1: # Reduced threshold to 1 for basic exam, can be adjusted
            trend_validation["points"] += 3 # Increased points for impact relevance
            trend_validation["feedback"].append(f"Trend {trend_num}: Impact relevant (keywords matched: {impact_keywords_matched})")
        else:
            trend_validation["feedback"].append(f"Trend {trend_num}: Impact keywords insufficient ({impact_keywords_matched} matched, need >= 1)")

        score += trend_validation["points"]
        validation_results['task1'].append(trend_validation)

    # --- Task 2 Validation ---
    max_score += 4 # Task 2 has max 4 points
    deal_data = submission.get('task2_deal', {})
    task2_validation = {"points": 0, "feedback": []}

    key_deal_answer = answer_key['task2_deal']

    # Source URL Domain Check
    url = deal_data.get('source_url', '')
    domain = urlparse(url).netloc
    if domain in key_deal_answer['acceptable_source_domains']:
        task2_validation["points"] += 1
        task2_validation["feedback"].append(f"Deal: Source domain OK ({domain})")
    else:
        task2_validation["feedback"].append(f"Deal: Source domain NOT ACCEPTABLE ({domain}). Should be from: {key_deal_answer['acceptable_source_domains']}")

    # Keyword Matching (Deal Summary)
    deal_summary = deal_data.get('deal_summary', '').lower()
    deal_summary_keywords_matched = sum(1 for keyword in key_deal_answer['deal_summary_keywords'] if keyword in deal_summary)
    if deal_summary_keywords_matched >= 1: # Reduced threshold to 1 for basic exam, can be adjusted
        task2_validation["points"] += 2 # Increased points for deal summary relevance
        task2_validation["feedback"].append(f"Deal: Summary relevant (keywords matched: {deal_summary_keywords_matched})")
    else:
        task2_validation["feedback"].append(f"Deal: Summary keywords insufficient ({deal_summary_keywords_matched} matched, need >= 1)")

    # Key Terms Check (Simplified - just checking if something is provided or "Not Publicly Available")
    key_terms = deal_data.get('key_terms', '')
    if key_terms and key_terms.lower() != "not publicly available":
        task2_validation["points"] += 1
        task2_validation["feedback"].append("Deal: Key terms provided")
    elif key_terms.lower() == "not publicly available":
        task2_validation["points"] += 1 # Award point even if not available if correctly stated
        task2_validation["feedback"].append("Deal: Key terms correctly stated as 'Not Publicly Available'")
    else:
        task2_validation["feedback"].append("Deal: Key terms missing")


    score += task2_validation["points"]
    validation_results['task2'] = task2_validation

    overall_score_percentage = (score / max_score) * 100 if max_score > 0 else 0

    results = {
        "candidate_id": submission.get('candidate_id', 'N/A'),
        "candidate_name": submission.get('candidate_name', 'N/A'),
        "model_version": submission.get('model_version', 'N/A'),
        "overall_score": overall_score_percentage,
        "detailed_results": validation_results,
        "total_points": score,
        "max_points": max_score
    }
    return results, overall_score_percentage

if __name__ == "__main__":
    evaluation_results, overall_score = validate_basic_exam()

    if "error" in evaluation_results:
        print(f"Error during evaluation: {evaluation_results['error']}")
    else:
        with open("test_results.json", 'w') as outfile:
            json.dump(evaluation_results, outfile, indent=4)
        print(f"Evaluation completed. Results saved to 'test_results.json'. Overall Score: {overall_score:.2f}%")