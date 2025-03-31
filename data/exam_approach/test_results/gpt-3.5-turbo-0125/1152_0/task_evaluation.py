import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_task_1(candidate_items, answer_items):
    correct_items = 0
    for candidate_item in candidate_items:
        for answer_item in answer_items:
            if (candidate_item['name'] == answer_item['name'] and
                candidate_item['price'] == answer_item['price'] and
                candidate_item['supplier'] == answer_item['supplier'] and
                candidate_item['source'] == answer_item['source']):
                correct_items += 1
                break
    return correct_items

def validate_task_2(candidate_suppliers, answer_suppliers):
    correct_suppliers = 0
    for candidate_supplier in candidate_suppliers:
        for answer_supplier in answer_suppliers:
            if (candidate_supplier['name'] == answer_supplier['name'] and
                candidate_supplier['url'] == answer_supplier['url'] and
                candidate_supplier['contact_info'] == answer_supplier['contact_info']):
                correct_suppliers += 1
                break
    return correct_suppliers

def evaluate_submission(candidate_submission, answer_key):
    task_1_score = validate_task_1(candidate_submission['task_1']['items'], answer_key['task_1']['items'])
    task_2_score = validate_task_2(candidate_submission['task_2']['suppliers'], answer_key['task_2']['suppliers'])

    # Calculate the total possible correct answers
    total_task_1_items = len(answer_key['task_1']['items'])
    total_task_2_suppliers = len(answer_key['task_2']['suppliers'])

    # Calculate the overall score
    total_correct = task_1_score + task_2_score
    total_possible = total_task_1_items + total_task_2_suppliers
    overall_score = (total_correct / total_possible) * 100

    return {
        "task_1_score": task_1_score,
        "task_2_score": task_2_score,
        "overall_score": overall_score
    }

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')['answer_key']

    results = evaluate_submission(candidate_submission, answer_key)

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()