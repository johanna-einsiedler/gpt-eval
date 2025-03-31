import json

def evaluate_submission(submission_file, answer_key_file, result_file):
    with open(submission_file, 'r') as sub_file, open(answer_key_file, 'r') as ans_file:
        submission = json.load(sub_file)
        answer_key = json.load(ans_file)
        
        results = {
            "task_1": {},
            "task_2": {},
            "overall_score": 0
        }
        
        correct_count = 0
        total_count = 0
        
        for task in ['task_1', 'task_2']:
            results[task] = {}
            for product, answers in answer_key[task].items():
                results[task][product] = {}
                for key, correct_value in answers.items():
                    total_count += 1
                    candidate_value = submission[task].get(product, {}).get(key)
                    is_correct = candidate_value == correct_value
                    results[task][product][key] = {
                        "candidate_value": candidate_value,
                        "correct_value": correct_value,
                        "is_correct": is_correct
                    }
                    if is_correct:
                        correct_count += 1
        
        overall_score = (correct_count / total_count) * 100
        results["overall_score"] = overall_score
        
        with open(result_file, 'w') as res_file:
            json.dump(results, res_file, indent=4)
        
        print(f"Evaluation complete. Results saved to {result_file}")

# Example usage
evaluate_submission('test_submission.json', 'answer_key.json', 'test_results.json')