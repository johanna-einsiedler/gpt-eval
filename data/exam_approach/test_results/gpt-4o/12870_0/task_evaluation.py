import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_trends(candidate_trends, answer_trends):
    score = 0
    max_score = len(answer_trends)
    detailed_results = []

    for candidate_trend, answer_trend in zip(candidate_trends, answer_trends):
        trend_score = 0
        if candidate_trend['trend_summary'].strip().lower() == answer_trend['trend_summary'].strip().lower():
            trend_score += 0.5
        if candidate_trend['impact'].strip().lower() == answer_trend['impact'].strip().lower():
            trend_score += 0.5
        score += trend_score
        detailed_results.append({
            "candidate_trend": candidate_trend,
            "answer_trend": answer_trend,
            "trend_score": trend_score
        })

    return score, max_score, detailed_results

def evaluate_deal(candidate_deal, answer_deal):
    score = 0
    max_score = 3
    detailed_results = {}

    if candidate_deal['parties_involved'].strip().lower() == answer_deal['parties_involved'].strip().lower():
        score += 1
    if candidate_deal['nature_of_deal'].strip().lower() == answer_deal['nature_of_deal'].strip().lower():
        score += 1
    if candidate_deal['significance'].strip().lower() == answer_deal['significance'].strip().lower():
        score += 1

    detailed_results = {
        "candidate_deal": candidate_deal,
        "answer_deal": answer_deal,
        "deal_score": score
    }

    return score, max_score, detailed_results

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate industry trends
    trend_score, trend_max_score, trend_results = evaluate_trends(
        candidate_submission['industry_trends'],
        answer_key['industry_trends']
    )

    # Evaluate deal analysis
    deal_score, deal_max_score, deal_results = evaluate_deal(
        candidate_submission['deal_analysis'],
        answer_key['deal_analysis']
    )

    # Calculate overall score
    total_score = trend_score + deal_score
    total_max_score = trend_max_score + deal_max_score
    overall_score = (total_score / total_max_score) * 100

    # Prepare results
    results = {
        "trend_results": trend_results,
        "deal_results": deal_results,
        "overall_score": overall_score
    }

    # Save results to a JSON file
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()