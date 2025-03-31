import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_task_1(candidate_answers, answer_key):
    correct_count = 0
    for candidate, correct in zip(candidate_answers, answer_key):
        if candidate['chosen_supplier'] == correct['chosen_supplier']:
            correct_count += 1
    return correct_count, len(answer_key)

def validate_task_2(candidate_answers, answer_key, total_budget):
    total_spent = 0
    correct_count = 0
    for candidate, correct in zip(candidate_answers, answer_key):
        if (candidate['quantity_purchased'] == correct['quantity_purchased'] and
            candidate['total_cost'] == correct['total_cost']):
            correct_count += 1
        total_spent += candidate['total_cost']
    return correct_count, len(answer_key), total_spent <= total_budget

def calculate_overall_score(task_1_score, task_2_score, task_1_total, task_2_total):
    total_correct = task_1_score + task_2_score
    total_possible = task_1_total + task_2_total
    return (total_correct / total_possible) * 100

def main():
    candidate_data = load_json('test_submission.json')
    answer_key_data = load_json('answer_key.json')

    # Validate Task 1
    task_1_correct, task_1_total = validate_task_1(candidate_data['task_1'], answer_key_data['task_1'])

    # Validate Task 2
    task_2_correct, task_2_total, within_budget = validate_task_2(candidate_data['task_2'], answer_key_data['task_2'], total_budget=1000.00)

    # Calculate overall score
    overall_score = calculate_overall_score(task_1_correct, task_2_correct, task_1_total, task_2_total)

    # Prepare results
    results = {
        "task_1": {
            "correct": task_1_correct,
            "total": task_1_total,
            "score": (task_1_correct / task_1_total) * 100
        },
        "task_2": {
            "correct": task_2_correct,
            "total": task_2_total,
            "score": (task_2_correct / task_2_total) * 100,
            "within_budget": within_budget
        },
        "overall_score": overall_score
    }

    # Save results to JSON
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()