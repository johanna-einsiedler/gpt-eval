import json

def validate_submission(submission_file, answer_key_file):
    """
    Evaluates the candidate's submission against the answer key and generates a test results JSON.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the test results.
    """

    try:
        with open(submission_file, 'r') as f_sub, open(answer_key_file, 'r') as f_key:
            submission = json.load(f_sub)
            answer_key = json.load(f_key)
    except FileNotFoundError:
        return {"error": "File not found. Ensure 'test_submission.json' and 'answer_key.json' are in the same directory."}
    except json.JSONDecodeError:
        return {"error": "JSONDecodeError: Invalid JSON format in submission or answer key file."}

    results = {
        "task1_result": {},
        "task2_result": {},
        "overall_score": 0.0
    }

    # Task 1 Evaluation
    expected_transaction_count = answer_key['answer_key']['task1_transactions_processed_count']
    submitted_transaction_count = submission.get('task1_transactions_processed_count')

    task1_score = 0
    task1_passed = False
    if submitted_transaction_count == expected_transaction_count:
        task1_score = 1
        task1_passed = True

    results["task1_result"] = {
        "expected_transactions_processed_count": expected_transaction_count,
        "submitted_transactions_processed_count": submitted_transaction_count,
        "task_1_score": task1_score,
        "task_1_passed": task1_passed
    }

    # Task 2 Evaluation
    answer_key_inventory = answer_key['answer_key']['task2_end_of_day_inventory']
    submission_inventory = submission.get('task2_end_of_day_inventory', [])
    product_level_results = []
    task2_score = 0
    inventory_items_evaluated = 0
    inventory_items_correct = 0
    task2_passed = True # Initialize to true, will be set to false if any product is incorrect

    answer_key_inventory_dict = {(item['product_name'], item['unit']): item['current_quantity'] for item in answer_key_inventory}
    inventory_items_evaluated = len(answer_key_inventory)

    for answer_item in answer_key_inventory:
        product_name = answer_item['product_name']
        unit = answer_item['unit']
        expected_quantity = answer_item['current_quantity']
        submitted_quantity = None
        product_score = 0
        product_passed = False

        for submitted_item in submission_inventory:
            if submitted_item['product_name'] == product_name and submitted_item['unit'] == unit:
                submitted_quantity = submitted_item['current_quantity']
                break

        if submitted_quantity == expected_quantity:
            product_score = 1
            product_passed = True
            task2_score += 1
            inventory_items_correct += 1
        else:
            task2_passed = False # If any product is incorrect, task 2 is not passed

        product_level_results.append({
            "product_name": product_name,
            "unit": unit,
            "expected_quantity": expected_quantity,
            "submitted_quantity": submitted_quantity,
            "product_score": product_score,
            "product_passed": product_passed
        })

    results["task2_result"] = {
        "inventory_items_evaluated": inventory_items_evaluated,
        "inventory_items_correct": inventory_items_correct,
        "task_2_score": task2_score,
        "task_2_passed": task2_passed,
        "product_level_results": product_level_results
    }

    # Overall Score Calculation
    total_possible_points = 1 + inventory_items_evaluated # 1 for task 1, and number of products for task 2
    achieved_points = task1_score + task2_score
    results["overall_score"] = (achieved_points / total_possible_points) * 100 if total_possible_points > 0 else 0.0

    return results

if __name__ == "__main__":
    submission_file = 'test_submission.json'
    answer_key_file = 'answer_key.json'
    test_results = validate_submission(submission_file, answer_key_file)

    if "error" in test_results:
        print(f"Error during evaluation: {test_results['error']}")
    else:
        try:
            with open('test_results.json', 'w') as outfile:
                json.dump(test_results, outfile, indent=4)
            print("Test results saved to 'test_results.json'")
        except Exception as e:
            print(f"Error saving results to JSON: {e}")
            print("Test Results:")
            print(json.dumps(test_results, indent=4))