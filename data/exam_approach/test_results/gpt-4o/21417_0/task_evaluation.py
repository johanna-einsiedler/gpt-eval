import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_discrepancies, answer_discrepancies):
    correct_count = 0
    detailed_results = []

    for candidate_discrepancy in candidate_discrepancies:
        for answer_discrepancy in answer_discrepancies:
            if (candidate_discrepancy['field_name'] == answer_discrepancy['field_name'] and
                candidate_discrepancy['issue'] == answer_discrepancy['issue']):
                correct_count += 1
                detailed_results.append({
                    "field_name": candidate_discrepancy['field_name'],
                    "correct": True
                })
                break
        else:
            detailed_results.append({
                "field_name": candidate_discrepancy['field_name'],
                "correct": False
            })

    return correct_count, detailed_results

def evaluate_task_2(candidate_task_2, answer_task_2):
    is_covered_correct = candidate_task_2['is_covered'] == answer_task_2['is_covered']
    justification_correct = candidate_task_2['justification'] == answer_task_2['justification']
    
    return is_covered_correct, justification_correct

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate Task 1
    task_1_correct_count, task_1_detailed_results = evaluate_task_1(
        candidate_submission['task_1']['discrepancies'],
        answer_key['task_1']['discrepancies']
    )
    task_1_total = len(answer_key['task_1']['discrepancies'])

    # Evaluate Task 2
    is_covered_correct, justification_correct = evaluate_task_2(
        candidate_submission['task_2'],
        answer_key['task_2']
    )
    task_2_total = 2  # Two parts to evaluate: is_covered and justification
    task_2_correct_count = int(is_covered_correct) + int(justification_correct)

    # Calculate overall score
    total_correct = task_1_correct_count + task_2_correct_count
    total_possible = task_1_total + task_2_total
    overall_score = (total_correct / total_possible) * 100

    # Prepare results
    results = {
        "task_1": {
            "correct_count": task_1_correct_count,
            "total": task_1_total,
            "detailed_results": task_1_detailed_results
        },
        "task_2": {
            "is_covered_correct": is_covered_correct,
            "justification_correct": justification_correct,
            "correct_count": task_2_correct_count,
            "total": task_2_total
        },
        "overall_score": overall_score
    }

    # Save results to JSON
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()