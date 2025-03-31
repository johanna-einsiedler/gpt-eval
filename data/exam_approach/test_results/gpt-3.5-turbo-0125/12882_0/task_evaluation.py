import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def compare_answers(candidate_answers, correct_answers):
    """Compare candidate answers with the correct answers and calculate the score."""
    results = {
        "task_1": {},
        "task_2": {},
        "overall_score": 0
    }
    total_questions = 0
    correct_answers_count = 0

    # Compare Task 1 answers
    for product_type, correct_data in correct_answers.get("task_1", {}).items():
        total_questions += 1
        candidate_quantity = candidate_answers.get("task_1", {}).get(product_type, {}).get("total_quantity")
        correct_quantity = correct_data.get("total_quantity")
        if candidate_quantity == correct_quantity:
            results["task_1"][product_type] = "correct"
            correct_answers_count += 1
        else:
            results["task_1"][product_type] = "incorrect"

    # Compare Task 2 answers
    for product_type, correct_data in correct_answers.get("task_2", {}).items():
        total_questions += 1
        candidate_quantity = candidate_answers.get("task_2", {}).get(product_type, {}).get("adjusted_quantity")
        correct_quantity = correct_data.get("adjusted_quantity")
        if candidate_quantity == correct_quantity:
            results["task_2"][product_type] = "correct"
            correct_answers_count += 1
        else:
            results["task_2"][product_type] = "incorrect"

    # Calculate overall score
    if total_questions > 0:
        results["overall_score"] = (correct_answers_count / total_questions) * 100

    return results

def main():
    # Load candidate submission and answer key
    candidate_answers = load_json('test_submission.json')
    correct_answers = load_json('answer_key.json')

    # Compare answers and calculate results
    results = compare_answers(candidate_answers, correct_answers)

    # Save results to a JSON file
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()