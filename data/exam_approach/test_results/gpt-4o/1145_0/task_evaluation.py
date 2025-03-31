import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_discrepancies(candidate_discrepancies, answer_discrepancies):
    correct_discrepancies = 0
    for discrepancy in candidate_discrepancies:
        if discrepancy in answer_discrepancies:
            correct_discrepancies += 1
    return correct_discrepancies, len(answer_discrepancies)

def evaluate_total_cost(candidate_cost, answer_cost):
    return candidate_cost == answer_cost

def evaluate_financial_ratios(candidate_ratios, answer_ratios):
    correct_ratios = 0
    for key in answer_ratios:
        if candidate_ratios.get(key) == answer_ratios[key]:
            correct_ratios += 1
    return correct_ratios, len(answer_ratios)

def evaluate_conclusion(candidate_conclusion, answer_conclusion):
    return candidate_conclusion.lower() == answer_conclusion.lower()

def evaluate_recommendation(candidate_recommendation, answer_recommendation):
    return candidate_recommendation.lower() == answer_recommendation.lower()

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    results = {
        "task_1": {
            "discrepancies": 0,
            "total_cost": 0,
            "conclusion": 0
        },
        "task_2": {
            "financial_ratios": 0,
            "financial_health": 0,
            "recommendation": 0
        }
    }

    # Task 1 Evaluation
    correct_discrepancies, total_discrepancies = evaluate_discrepancies(
        candidate_submission['task_1']['discrepancies'],
        answer_key['task_1']['discrepancies']
    )
    results['task_1']['discrepancies'] = correct_discrepancies / total_discrepancies

    results['task_1']['total_cost'] = evaluate_total_cost(
        candidate_submission['task_1']['total_cost'],
        answer_key['task_1']['total_cost']
    )

    results['task_1']['conclusion'] = evaluate_conclusion(
        candidate_submission['task_1']['conclusion'],
        answer_key['task_1']['conclusion']
    )

    # Task 2 Evaluation
    correct_ratios, total_ratios = evaluate_financial_ratios(
        candidate_submission['task_2']['financial_ratios'],
        answer_key['task_2']['financial_ratios']
    )
    results['task_2']['financial_ratios'] = correct_ratios / total_ratios

    results['task_2']['financial_health'] = evaluate_conclusion(
        candidate_submission['task_2']['financial_health'],
        answer_key['task_2']['financial_health']
    )

    results['task_2']['recommendation'] = evaluate_recommendation(
        candidate_submission['task_2']['recommendation'],
        answer_key['task_2']['recommendation']
    )

    # Calculate overall score
    total_points = 6  # 1 for each evaluation point
    achieved_points = (
        results['task_1']['discrepancies'] +
        results['task_1']['total_cost'] +
        results['task_1']['conclusion'] +
        results['task_2']['financial_ratios'] +
        results['task_2']['financial_health'] +
        results['task_2']['recommendation']
    )
    overall_score = (achieved_points / total_points) * 100

    results['overall_score'] = overall_score

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()