import json

def evaluate_task_1(submission, answer_key):
    correct_prioritizations = 0
    detailed_results = []

    for sub, ans in zip(submission['task_1']['prioritization'], answer_key['task_1']['prioritization']):
        is_correct = sub['priority'] == ans['priority']
        if is_correct:
            correct_prioritizations += 1
        detailed_results.append({
            "claim_id": sub['claim_id'],
            "submitted_priority": sub['priority'],
            "correct_priority": ans['priority'],
            "is_correct": is_correct,
            "submitted_explanation": sub['explanation'],
            "correct_explanation": ans['explanation']
        })

    return correct_prioritizations, detailed_results

def evaluate_task_2(submission, answer_key):
    sub_task_2 = submission['task_2']['resolution_strategy']
    ans_task_2 = answer_key['task_2']['resolution_strategy']

    steps_correct = len(sub_task_2['steps']) >= len(ans_task_2['steps'])
    considerations_correct = len(sub_task_2['considerations']) >= len(ans_task_2['considerations'])
    challenges_correct = len(sub_task_2['challenges_and_solutions']) >= len(ans_task_2['challenges_and_solutions'])

    detailed_results = {
        "steps": {
            "submitted": sub_task_2['steps'],
            "required": ans_task_2['steps'],
            "is_correct": steps_correct
        },
        "considerations": {
            "submitted": sub_task_2['considerations'],
            "required": ans_task_2['considerations'],
            "is_correct": considerations_correct
        },
        "challenges_and_solutions": {
            "submitted": sub_task_2['challenges_and_solutions'],
            "required": ans_task_2['challenges_and_solutions'],
            "is_correct": challenges_correct
        }
    }

    return steps_correct and considerations_correct and challenges_correct, detailed_results

def calculate_overall_score(task_1_score, task_2_score):
    total_possible = 2  # One point for each task
    total_achieved = task_1_score + task_2_score
    return (total_achieved / total_possible) * 100

def main():
    with open('test_submission.json', 'r') as sub_file, open('answer_key.json', 'r') as ans_file:
        submission = json.load(sub_file)
        answer_key = json.load(ans_file)['answer_key']

        # Evaluate Task 1
        task_1_correct, task_1_details = evaluate_task_1(submission, answer_key)
        task_1_score = 1 if task_1_correct >= 4 else 0

        # Evaluate Task 2
        task_2_correct, task_2_details = evaluate_task_2(submission, answer_key)
        task_2_score = 1 if task_2_correct else 0

        # Calculate overall score
        overall_score = calculate_overall_score(task_1_score, task_2_score)

        # Prepare results
        results = {
            "task_1": {
                "correct_prioritizations": task_1_correct,
                "details": task_1_details
            },
            "task_2": {
                "is_correct": task_2_correct,
                "details": task_2_details
            },
            "overall_score": overall_score
        }

        # Save results to JSON
        with open('test_results.json', 'w') as result_file:
            json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()