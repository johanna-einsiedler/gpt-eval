import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 3

    # Evaluate top 3 products
    candidate_products = set(candidate['top_3_products'])
    answer_products = set(answer_key['top_3_products'])
    correct_products = candidate_products.intersection(answer_products)
    score += len(correct_products)

    # Evaluate highest sales month
    if candidate['highest_sales_month'] == answer_key['highest_sales_month']:
        score += 1

    # Evaluate analysis (basic check for relevant keywords)
    analysis_keywords = ["holiday", "promotion", "seasonal"]
    if any(keyword in candidate['analysis'].lower() for keyword in analysis_keywords):
        score += 1

    return score, max_score

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = 2

    # Evaluate economic conditions (basic check for relevant keywords)
    economic_keywords = ["inflation", "consumer confidence", "employment"]
    if all(keyword in candidate['economic_conditions'].lower() for keyword in economic_keywords):
        score += 1

    # Evaluate predicted impact (basic check for logical prediction)
    if "spending" in candidate['predicted_impact'].lower():
        score += 1

    return score, max_score

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_max = evaluate_task_1(candidate_submission['task_1'], answer_key['task_1'])
    task_2_score, task_2_max = evaluate_task_2(candidate_submission['task_2'], answer_key['task_2'])

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