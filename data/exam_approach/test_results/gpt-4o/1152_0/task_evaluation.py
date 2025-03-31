import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task1(submission, answer_key):
    correct_count = 0
    task1_results = []

    for i, product in enumerate(answer_key['task1']):
        submission_product = submission['task1'][i]
        is_correct = (
            submission_product['product_name'] == product['product_name'] and
            submission_product['description'] == product['description'] and
            submission_product['supplier_contact'] == product['supplier_contact']
        )
        task1_results.append({
            "product_name": submission_product['product_name'],
            "is_correct": is_correct
        })
        if is_correct:
            correct_count += 1

    return correct_count, task1_results

def evaluate_task2(submission, answer_key):
    correct_count = 0
    task2_results = []

    for i, article in enumerate(answer_key['task2']):
        submission_article = submission['task2'][i]
        is_correct = (
            submission_article['article_title'] == article['article_title'] and
            submission_article['summary'] == article['summary'] and
            submission_article['source'] == article['source']
        )
        task2_results.append({
            "article_title": submission_article['article_title'],
            "is_correct": is_correct
        })
        if is_correct:
            correct_count += 1

    return correct_count, task2_results

def main():
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task1_correct, task1_results = evaluate_task1(submission, answer_key)
    task2_correct, task2_results = evaluate_task2(submission, answer_key)

    total_correct = task1_correct + task2_correct
    total_possible = len(answer_key['task1']) + len(answer_key['task2'])
    overall_score = (total_correct / total_possible) * 100

    results = {
        "task1_results": task1_results,
        "task2_results": task2_results,
        "overall_score": overall_score
    }

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()