import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    score = 0
    max_score = 2  # One point for trends, one for anomalies

    # Evaluate Trends
    if "Trends" in candidate and candidate["Trends"]:
        if any(term in candidate["Trends"].lower() for term in ["increase", "decrease", "rise", "fall", "spike", "drop"]):
            score += 1

    # Evaluate Anomalies
    if "Anomalies" in candidate and candidate["Anomalies"]:
        if any(term in candidate["Anomalies"].lower() for term in ["spike", "drop", "unusual", "anomaly"]):
            score += 1

    return score, max_score

def evaluate_task_2(candidate, answer_key):
    score = 0
    max_score = 2  # One point for summary, one for sources

    # Evaluate Summary
    if "Summary" in candidate and candidate["Summary"]:
        if any(term in candidate["Summary"].lower() for term in ["geopolitical", "weather", "policy", "supply", "demand"]):
            score += 1

    # Evaluate Sources
    if "Sources" in candidate and len(candidate["Sources"]) >= 3:
        score += 1

    return score, max_score

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_score, task_1_max = evaluate_task_1(candidate_submission.get("Task 1", {}), answer_key.get("Task 1", {}))
    task_2_score, task_2_max = evaluate_task_2(candidate_submission.get("Task 2", {}), answer_key.get("Task 2", {}))

    total_score = task_1_score + task_2_score
    total_max_score = task_1_max + task_2_max
    overall_score = (total_score / total_max_score) * 100

    results = {
        "Task 1 Score": task_1_score,
        "Task 2 Score": task_2_score,
        "Overall Score": overall_score
    }

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()