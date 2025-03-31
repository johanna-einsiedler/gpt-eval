import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_task1(submission, answer_key):
    correct_adjustments = 0
    for claim in submission:
        for correct_claim in answer_key:
            if claim["ClaimID"] == correct_claim["ClaimID"]:
                if abs(claim["AdjustedReserve"] - correct_claim["AdjustedReserve"]) <= 0.05 * correct_claim["AdjustedReserve"]:
                    correct_adjustments += 1
                break
    return correct_adjustments, len(answer_key)

def validate_task2(submission, answer_key):
    if (submission["ScenarioID"] == answer_key["ScenarioID"] and
        submission["Recommendation"] == answer_key["Recommendation"] and
        "corporate policy section 3.2" in submission["Justification"]):
        return True
    return False

def evaluate_submission(submission, answer_key):
    task1_correct, task1_total = validate_task1(submission["AdjustedReserves"], answer_key["AdjustedReserves"])
    task1_score = (task1_correct / task1_total) * 100

    task2_correct = validate_task2(submission["ReserveRecommendation"], answer_key["ReserveRecommendation"])
    task2_score = 100 if task2_correct else 0

    overall_score = (task1_score * 0.5) + (task2_score * 0.5)  # Assuming equal weight for both tasks

    return {
        "Task1": {
            "CorrectAdjustments": task1_correct,
            "TotalAdjustments": task1_total,
            "Score": task1_score
        },
        "Task2": {
            "Correct": task2_correct,
            "Score": task2_score
        },
        "OverallScore": overall_score
    }

def save_results(results, file_name):
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    results = evaluate_submission(submission, answer_key)
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()