import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 5
    results = {}

    for key in answer_key['task_1']:
        candidate_value = candidate['task_1'].get(key, "").lower()
        answer_value = answer_key['task_1'][key].lower()
        if answer_value in candidate_value:
            score += 1
            results[key] = "Correct"
        else:
            results[key] = "Incorrect"

    return score, max_score, results

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = len(answer_key['task_2'])
    results = []

    for answer_issue in answer_key['task_2']:
        issue_found = False
        for candidate_issue in candidate['task_2']:
            if (answer_issue['issue'].lower() in candidate_issue['issue'].lower() and
                answer_issue['explanation'].lower() in candidate_issue['explanation'].lower() and
                answer_issue['suggestion'].lower() in candidate_issue['suggestion'].lower()):
                issue_found = True
                break
        if issue_found:
            score += 1
            results.append({"issue": answer_issue['issue'], "result": "Correct"})
        else:
            results.append({"issue": answer_issue['issue'], "result": "Incorrect"})

    return score, max_score, results

def main():
    candidate = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_max, task_1_results = evaluate_task_1(candidate, answer_key)
    task_2_score, task_2_max, task_2_results = evaluate_task_2(candidate, answer_key)

    overall_score = ((task_1_score + task_2_score) / (task_1_max + task_2_max)) * 100

    results = {
        "task_1_results": task_1_results,
        "task_2_results": task_2_results,
        "overall_score": overall_score
    }

    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()