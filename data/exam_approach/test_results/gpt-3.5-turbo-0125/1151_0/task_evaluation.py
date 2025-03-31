import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    candidate_total_costs = candidate['task_1']['summary_table']['total_costs']
    candidate_average_delivery_time = candidate['task_1']['summary_table']['average_delivery_time']
    
    answer_total_costs = answer_key['task_1']['summary_table']['total_costs']
    answer_average_delivery_time = answer_key['task_1']['summary_table']['average_delivery_time']
    
    total_costs_correct = abs(answer_total_costs - candidate_total_costs) < 0.01
    average_delivery_time_correct = abs(answer_average_delivery_time - candidate_average_delivery_time) < 0.1
    
    return total_costs_correct, average_delivery_time_correct

def evaluate_task_2(candidate, answer_key):
    trends_correct = candidate['task_2']['analysis']['trends'] == answer_key['task_2']['analysis']['trends']
    issues_correct = candidate['task_2']['analysis']['issues'] == answer_key['task_2']['analysis']['issues']
    recommendations_correct = candidate['task_2']['analysis']['recommendations'] == answer_key['task_2']['analysis']['recommendations']
    
    return trends_correct, issues_correct, recommendations_correct

def calculate_overall_score(results):
    total_points = sum(results.values())
    max_points = len(results)
    return (total_points / max_points) * 100

def main():
    candidate = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    task_1_results = evaluate_task_1(candidate, answer_key)
    task_2_results = evaluate_task_2(candidate, answer_key)
    
    results = {
        "task_1_total_costs_correct": task_1_results[0],
        "task_1_average_delivery_time_correct": task_1_results[1],
        "task_2_trends_correct": task_2_results[0],
        "task_2_issues_correct": task_2_results[1],
        "task_2_recommendations_correct": task_2_results[2]
    }
    
    overall_score = calculate_overall_score(results)
    
    results['overall_score'] = overall_score
    
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()