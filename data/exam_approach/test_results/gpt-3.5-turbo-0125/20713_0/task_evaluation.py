import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_answers(candidate_answers, correct_answers):
    results = {
        "mark_up_rates": {},
        "mark_down_rates": {},
        "new_selling_prices": {},
        "overall_score": 0
    }
    correct_count = 0
    total_count = 0

    # Validate mark-up rates
    for product_id, correct_rate in correct_answers['mark_up_rates'].items():
        candidate_rate = float(candidate_answers['mark_up_rates'].get(product_id, 0))
        if abs(candidate_rate - float(correct_rate)) <= 0.01:
            results["mark_up_rates"][product_id] = True
            correct_count += 1
        else:
            results["mark_up_rates"][product_id] = False
        total_count += 1

    # Validate mark-down rates and new selling prices
    for product_id, correct_rate in correct_answers['mark_down_rates'].items():
        candidate_rate = float(candidate_answers['mark_down_rates'].get(product_id, 0))
        if abs(candidate_rate - float(correct_rate)) <= 0.01:
            results["mark_down_rates"][product_id] = True
            correct_count += 1
        else:
            results["mark_down_rates"][product_id] = False
        total_count += 1

        correct_price = float(correct_answers['new_selling_prices'][product_id])
        candidate_price = float(candidate_answers['new_selling_prices'].get(product_id, 0))
        if abs(candidate_price - correct_price) <= 0.01:
            results["new_selling_prices"][product_id] = True
            correct_count += 1
        else:
            results["new_selling_prices"][product_id] = False
        total_count += 1

    results["overall_score"] = (correct_count / total_count) * 100
    return results

def save_results(results, file_name):
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    candidate_answers = load_json('test_submission.json')
    correct_answers = load_json('answer_key.json')
    results = validate_answers(candidate_answers, correct_answers)
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()