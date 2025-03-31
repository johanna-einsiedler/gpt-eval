import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_spec, answer_spec):
    score = 0
    max_score = 5
    feedback = {}

    # Check each field in the specification
    for key in answer_spec:
        if key in candidate_spec and candidate_spec[key] == answer_spec[key]:
            score += 1
        else:
            feedback[key] = f"Expected: {answer_spec[key]}, Found: {candidate_spec.get(key, 'Missing')}"

    return score, max_score, feedback

def evaluate_task_2(candidate_review, answer_review):
    score = 0
    max_score = len(answer_review)
    feedback = []

    # Check each issue identified
    for i, answer_issue in enumerate(answer_review):
        if i < len(candidate_review):
            candidate_issue = candidate_review[i]
            issue_score = 0
            issue_feedback = {}

            # Check issue description
            if candidate_issue.get("issue_description") == answer_issue["issue_description"]:
                issue_score += 0.5
            else:
                issue_feedback["issue_description"] = f"Expected: {answer_issue['issue_description']}, Found: {candidate_issue.get('issue_description', 'Missing')}"

            # Check suggested correction
            if candidate_issue.get("suggested_correction") == answer_issue["suggested_correction"]:
                issue_score += 0.5
            else:
                issue_feedback["suggested_correction"] = f"Expected: {answer_issue['suggested_correction']}, Found: {candidate_issue.get('suggested_correction', 'Missing')}"

            score += issue_score
            feedback.append(issue_feedback)
        else:
            feedback.append({"error": "Missing issue in candidate's review"})

    return score, max_score, feedback

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate Task 1
    task_1_score, task_1_max_score, task_1_feedback = evaluate_task_1(
        candidate_submission.get("task_1_specification", {}),
        answer_key["task_1_specification"]
    )

    # Evaluate Task 2
    task_2_score, task_2_max_score, task_2_feedback = evaluate_task_2(
        candidate_submission.get("task_2_review", []),
        answer_key["task_2_review"]
    )

    # Calculate overall score
    total_score = task_1_score + task_2_score
    total_max_score = task_1_max_score + task_2_max_score
    overall_score = (total_score / total_max_score) * 100

    # Prepare results
    results = {
        "task_1_score": task_1_score,
        "task_1_max_score": task_1_max_score,
        "task_1_feedback": task_1_feedback,
        "task_2_score": task_2_score,
        "task_2_max_score": task_2_max_score,
        "task_2_feedback": task_2_feedback,
        "overall_score": overall_score
    }

    # Save results to JSON
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()