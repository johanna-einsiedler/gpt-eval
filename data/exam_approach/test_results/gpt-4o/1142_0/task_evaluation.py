import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_response, answer_key):
    score = 0
    max_score = 2  # 1 point for correct supplier, 1 point for justification

    # Check if the selected supplier is correct
    if candidate_response.get("selected_supplier") == answer_key.get("selected_supplier"):
        score += 1

    # Check if the justification is reasonable
    if candidate_response.get("justification") and "quality" in candidate_response["justification"].lower() and "price" in candidate_response["justification"].lower() and "quantity" in candidate_response["justification"].lower():
        score += 1

    return score, max_score

def evaluate_task_2(candidate_response, answer_key):
    score = 0
    max_score = 2  # 1 point for proposing a discount, 1 point for logical arguments

    # Check if the email proposes a discount
    if "discount" in candidate_response.get("negotiation_email", "").lower():
        score += 1

    # Check if the email contains logical arguments
    if any(keyword in candidate_response.get("negotiation_email", "").lower() for keyword in ["market conditions", "partnership", "industry standards"]):
        score += 1

    return score, max_score

def main():
    # Load the candidate's submission and the answer key
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate Task 1
    task_1_score, task_1_max_score = evaluate_task_1(candidate_submission.get("task_1", {}), answer_key.get("task_1", {}))

    # Evaluate Task 2
    task_2_score, task_2_max_score = evaluate_task_2(candidate_submission.get("task_2", {}), answer_key.get("task_2", {}))

    # Calculate overall score
    total_score = task_1_score + task_2_score
    total_max_score = task_1_max_score + task_2_max_score
    overall_score = (total_score / total_max_score) * 100

    # Prepare the results
    results = {
        "task_1_score": task_1_score,
        "task_1_max_score": task_1_max_score,
        "task_2_score": task_2_score,
        "task_2_max_score": task_2_max_score,
        "overall_score": overall_score
    }

    # Save the results to a JSON file
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()