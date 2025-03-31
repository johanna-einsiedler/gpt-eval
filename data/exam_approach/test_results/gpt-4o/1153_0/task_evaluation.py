import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def compare_lists(candidate_list, answer_list):
    return set(candidate_list) == set(answer_list)

def compare_dicts(candidate_dict, answer_dict):
    return all(candidate_dict.get(k) == v for k, v in answer_dict.items())

def evaluate_task_1(candidate, answer):
    score = 0
    max_score = 4

    # High Demand Products
    if compare_lists(candidate.get("high_demand_products", []), answer.get("high_demand_products", [])):
        score += 1

    # Seasonal Variations
    if compare_dicts(candidate.get("seasonal_variations", {}), answer.get("seasonal_variations", {})):
        score += 1

    # Inventory Turnover Rates
    candidate_turnover = candidate.get("inventory_turnover_rates", {})
    answer_turnover = answer.get("inventory_turnover_rates", {})
    if all(abs(float(candidate_turnover.get(k, 0)) - float(v)) < 0.01 for k, v in answer_turnover.items()):
        score += 1

    # Potential Issues
    if compare_lists(candidate.get("potential_issues", []), answer.get("potential_issues", [])):
        score += 1

    return score, max_score

def evaluate_task_2(candidate, answer):
    score = 0
    max_score = 3

    # Actions
    candidate_actions = candidate.get("strategic_plan", {}).get("actions", [])
    answer_actions = answer.get("strategic_plan", {}).get("actions", [])

    matched_actions = 0
    for c_action in candidate_actions:
        for a_action in answer_actions:
            if (c_action.get("action") == a_action.get("action") and
                c_action.get("product_id") == a_action.get("product_id") and
                c_action.get("justification") == a_action.get("justification")):
                matched_actions += 1
                break

    if matched_actions >= 2:
        score += 1

    # Overall Strategy
    if candidate.get("strategic_plan", {}).get("overall_strategy") == answer.get("strategic_plan", {}).get("overall_strategy"):
        score += 1

    return score, max_score

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_max = evaluate_task_1(candidate_submission.get("task_1", {}), answer_key.get("task_1", {}))
    task_2_score, task_2_max = evaluate_task_2(candidate_submission.get("task_2", {}), answer_key.get("task_2", {}))

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