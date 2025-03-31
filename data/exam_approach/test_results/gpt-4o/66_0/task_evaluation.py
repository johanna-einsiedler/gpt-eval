import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 3  # 1 point for each correct top product, 1 for correct peak month, 1 for reasonable analysis

    # Evaluate top products
    candidate_top_products = set(candidate['task_1']['top_products'])
    answer_top_products = set(answer_key['task_1']['top_products'])
    correct_top_products = candidate_top_products.intersection(answer_top_products)
    score += len(correct_top_products)

    # Evaluate peak month
    if candidate['task_1']['peak_month'] == answer_key['task_1']['peak_month']:
        score += 1

    # Evaluate peak month analysis
    # Simple check for presence of key terms (e.g., "holiday", "promotion") in the analysis
    analysis_keywords = ["holiday", "promotion", "seasonal"]
    candidate_analysis = candidate['task_1']['peak_month_analysis'].lower()
    if any(keyword in candidate_analysis for keyword in analysis_keywords):
        score += 1

    return score, max_score

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = 4  # 1 point for each correct economic condition, 1 for logical prediction

    # Evaluate economic conditions
    candidate_conditions = candidate['task_2']['economic_conditions']
    answer_conditions = answer_key['task_2']['economic_conditions']

    for key in candidate_conditions:
        if candidate_conditions[key] == answer_conditions[key]:
            score += 1

    # Evaluate buying pattern prediction
    # Simple check for logical consistency based on economic conditions
    prediction_keywords = ["cautious", "essential", "boost", "spending"]
    candidate_prediction = candidate['task_2']['buying_pattern_prediction'].lower()
    if any(keyword in candidate_prediction for keyword in prediction_keywords):
        score += 1

    return score, max_score

def main():
    candidate = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_max = evaluate_task_1(candidate, answer_key)
    task_2_score, task_2_max = evaluate_task_2(candidate, answer_key)

    total_score = task_1_score + task_2_score
    total_max_score = task_1_max + task_2_max
    overall_score = (total_score / total_max_score) * 100

    results = {
        "task_1_score": task_1_score,
        "task_1_max": task_1_max,
        "task_2_score": task_2_score,
        "task_2_max": task_2_max,
        "overall_score": overall_score
    }

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()