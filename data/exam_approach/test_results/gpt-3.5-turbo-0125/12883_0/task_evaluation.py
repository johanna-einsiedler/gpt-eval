import json
import os

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def evaluate_submission(submission, answer_key):
    results = {
        "task_1": {
            "updated_spreadsheet": False
        },
        "task_2": {
            "completed_report": False,
            "total_transactions": False,
            "total_inventory_value": False,
            "inventory_discrepancies": False
        },
        "overall_score": 0
    }

    # Check if the file paths are provided (assuming existence check is part of the evaluation)
    if os.path.exists(submission['task_1']['updated_spreadsheet']):
        results['task_1']['updated_spreadsheet'] = True

    if os.path.exists(submission['task_2']['completed_report']):
        results['task_2']['completed_report'] = True

    # Validate task 2 answers
    if submission['task_2']['total_transactions'] == answer_key['task_2']['total_transactions']:
        results['task_2']['total_transactions'] = True

    if abs(submission['task_2']['total_inventory_value'] - answer_key['task_2']['total_inventory_value']) < 0.01:
        results['task_2']['total_inventory_value'] = True

    if submission['task_2']['inventory_discrepancies'] == answer_key['task_2']['inventory_discrepancies']:
        results['task_2']['inventory_discrepancies'] = True

    # Calculate overall score
    total_checks = 5
    passed_checks = sum([
        results['task_1']['updated_spreadsheet'],
        results['task_2']['completed_report'],
        results['task_2']['total_transactions'],
        results['task_2']['total_inventory_value'],
        results['task_2']['inventory_discrepancies']
    ])
    results['overall_score'] = (passed_checks / total_checks) * 100

    return results

def main():
    # Load the submission and answer key
    submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)

    # Save the results to a JSON file
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()