import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(submission, answer_key):
    task_1_results = {}
    task_1_correct = 0
    total_items_correct = submission['task_1_summary']['total_items'] == answer_key['task_1_summary']['total_items']
    total_cost_correct = abs(submission['task_1_summary']['total_cost'] - answer_key['task_1_summary']['total_cost']) < 0.01
    earliest_date_correct = submission['task_1_summary']['earliest_delivery_date'] == answer_key['task_1_summary']['earliest_delivery_date']
    latest_date_correct = submission['task_1_summary']['latest_delivery_date'] == answer_key['task_1_summary']['latest_delivery_date']
    
    task_1_results['total_items_correct'] = total_items_correct
    task_1_results['total_cost_correct'] = total_cost_correct
    task_1_results['earliest_date_correct'] = earliest_date_correct
    task_1_results['latest_date_correct'] = latest_date_correct
    
    task_1_correct += total_items_correct + total_cost_correct + earliest_date_correct + latest_date_correct
    task_1_results['task_1_score'] = task_1_correct / 4 * 100  # Percentage score for Task 1
    
    return task_1_results, task_1_correct >= 3

def evaluate_task_2(submission, answer_key):
    task_2_results = []
    task_2_correct = 0
    
    for analysis in submission['task_2_analysis']:
        for correct_analysis in answer_key['task_2_analysis']:
            if (analysis['product_name'] == correct_analysis['product_name'] and
                analysis['issues'] == correct_analysis['issues'] and
                analysis['recommendations'] == correct_analysis['recommendations']):
                task_2_results.append({
                    'product_name': analysis['product_name'],
                    'correct': True
                })
                task_2_correct += 1
                break
        else:
            task_2_results.append({
                'product_name': analysis['product_name'],
                'correct': False
            })
    
    task_2_score = task_2_correct / len(answer_key['task_2_analysis']) * 100  # Percentage score for Task 2
    return task_2_results, task_2_correct >= 1, task_2_score

def main():
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    task_1_results, task_1_pass = evaluate_task_1(submission, answer_key)
    task_2_results, task_2_pass, task_2_score = evaluate_task_2(submission, answer_key)
    
    overall_pass = task_1_pass and task_2_pass
    overall_score = (task_1_results['task_1_score'] + task_2_score) / 2  # Average of both tasks
    
    results = {
        'task_1_results': task_1_results,
        'task_2_results': task_2_results,
        'overall_pass': overall_pass,
        'overall_score': overall_score
    }
    
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()