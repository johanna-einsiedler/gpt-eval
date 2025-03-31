import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def save_json(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def evaluate_task1(candidate, answer_key):
    score = 0
    max_score = 4  # 3 metrics + trends

    # Evaluate inventory turnover
    for product, value in answer_key['task1']['inventory_turnover'].items():
        if product in candidate['task1']['inventory_turnover']:
            if abs(float(candidate['task1']['inventory_turnover'][product]) - float(value)) < 0.01:
                score += 1

    # Evaluate average sales
    for product, value in answer_key['task1']['average_sales'].items():
        if product in candidate['task1']['average_sales']:
            if abs(float(candidate['task1']['average_sales'][product]) - float(value)) < 0.01:
                score += 1

    # Evaluate current inventory
    for product, value in answer_key['task1']['current_inventory'].items():
        if product in candidate['task1']['current_inventory']:
            if int(candidate['task1']['current_inventory'][product]) == int(value):
                score += 1

    # Evaluate trends
    if candidate['task1']['trends'].strip().lower() == answer_key['task1']['trends'].strip().lower():
        score += 1

    return score, max_score

def evaluate_task2(candidate, answer_key):
    score = 0
    max_score = 3  # objective alignment + 2 recommendations

    # Evaluate objective alignment
    if candidate['task2']['purchasing_plan']['objective_alignment'].strip().lower() == answer_key['task2']['purchasing_plan']['objective_alignment'].strip().lower():
        score += 1

    # Evaluate recommendations
    candidate_recommendations = set(map(str.strip, map(str.lower, candidate['task2']['purchasing_plan']['recommendations'])))
    answer_recommendations = set(map(str.strip, map(str.lower, answer_key['task2']['purchasing_plan']['recommendations'])))
    
    score += len(candidate_recommendations.intersection(answer_recommendations))

    return score, max_score

def main():
    candidate = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task1_score, task1_max = evaluate_task1(candidate, answer_key)
    task2_score, task2_max = evaluate_task2(candidate, answer_key)

    total_score = task1_score + task2_score
    total_max = task1_max + task2_max
    overall_score = (total_score / total_max) * 100

    results = {
        "task1_score": task1_score,
        "task1_max": task1_max,
        "task2_score": task2_score,
        "task2_max": task2_max,
        "overall_score": overall_score
    }

    save_json(results, 'test_results.json')

if __name__ == "__main__":
    main()