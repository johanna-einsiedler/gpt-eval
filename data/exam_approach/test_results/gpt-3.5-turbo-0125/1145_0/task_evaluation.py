import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def calculate_percentage_difference(value1, value2):
    return abs((value1 - value2) / value2) * 100

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 5  # 1 point for each component and 1 for total cost and suggested price

    # Evaluate cost components
    for component in ['materials', 'labor', 'overhead', 'profit_margin']:
        candidate_value = float(candidate['cost_components'][component])
        answer_value = float(answer_key['cost_components'][component])
        if calculate_percentage_difference(candidate_value, answer_value) <= 5:
            score += 1

    # Evaluate total cost
    candidate_total_cost = float(candidate['total_cost'])
    answer_total_cost = float(answer_key['total_cost'])
    if calculate_percentage_difference(candidate_total_cost, answer_total_cost) <= 5:
        score += 1

    # Evaluate suggested price
    candidate_suggested_price = float(candidate['suggested_price'])
    answer_suggested_price = float(answer_key['suggested_price'])
    if calculate_percentage_difference(candidate_suggested_price, answer_suggested_price) <= 5:
        score += 1

    return score, max_score

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = 2  # 1 point for analysis and 1 for pricing strategy

    # Evaluate analysis
    if candidate['analysis'].strip().lower() == answer_key['analysis'].strip().lower():
        score += 1

    # Evaluate pricing strategy
    if candidate['pricing_strategy'].strip().lower() == answer_key['pricing_strategy'].strip().lower():
        score += 1

    return score, max_score

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    results = {
        "candidate_id": candidate_submission["candidate_id"],
        "task_1": {},
        "task_2": {},
        "overall_score": 0
    }

    # Evaluate Task 1
    task_1_score, task_1_max_score = evaluate_task_1(candidate_submission['task_1'], answer_key['task_1'])
    results['task_1']['score'] = task_1_score
    results['task_1']['max_score'] = task_1_max_score

    # Evaluate Task 2
    task_2_score, task_2_max_score = evaluate_task_2(candidate_submission['task_2'], answer_key['task_2'])
    results['task_2']['score'] = task_2_score
    results['task_2']['max_score'] = task_2_max_score

    # Calculate overall score
    total_score = task_1_score + task_2_score
    total_max_score = task_1_max_score + task_2_max_score
    results['overall_score'] = (total_score / total_max_score) * 100

    # Save results
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()