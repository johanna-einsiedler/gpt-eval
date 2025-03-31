import json

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_data, answer_key_data):
    correct_count = 0
    candidate_discrepancies = candidate_data.get('task_1', {}).get('discrepancies', [])
    answer_discrepancies = answer_key_data.get('task_1', {}).get('discrepancies', [])
    
    for candidate_discrepancy in candidate_discrepancies:
        for answer_discrepancy in answer_discrepancies:
            if (candidate_discrepancy['claim_id'] == answer_discrepancy['claim_id'] and
                candidate_discrepancy['issue'] == answer_discrepancy['issue']):
                correct_count += 1
                break
    
    return correct_count, len(answer_discrepancies)

def evaluate_task_2(candidate_data, answer_key_data):
    correct_count = 0
    candidate_analysis = candidate_data.get('task_2', {}).get('analysis', [])
    answer_analysis = answer_key_data.get('task_2', {}).get('analysis', [])
    
    for candidate_claim in candidate_analysis:
        for answer_claim in answer_analysis:
            if (candidate_claim['claim_id'] == answer_claim['claim_id'] and
                candidate_claim['validity'] == answer_claim['validity'] and
                candidate_claim['recommendation'] == answer_claim['recommendation']):
                correct_count += 1
                break
    
    return correct_count, len(answer_analysis)

def calculate_overall_score(task_1_score, task_1_total, task_2_score, task_2_total):
    total_score = task_1_score + task_2_score
    total_possible = task_1_total + task_2_total
    return (total_score / total_possible) * 100 if total_possible > 0 else 0

def main():
    candidate_data = load_json('test_submission.json')
    answer_key_data = load_json('answer_key.json')
    
    task_1_score, task_1_total = evaluate_task_1(candidate_data, answer_key_data)
    task_2_score, task_2_total = evaluate_task_2(candidate_data, answer_key_data)
    
    overall_score = calculate_overall_score(task_1_score, task_1_total, task_2_score, task_2_total)
    
    results = {
        "task_1": {
            "correct": task_1_score,
            "total": task_1_total
        },
        "task_2": {
            "correct": task_2_score,
            "total": task_2_total
        },
        "overall_score": overall_score
    }
    
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()