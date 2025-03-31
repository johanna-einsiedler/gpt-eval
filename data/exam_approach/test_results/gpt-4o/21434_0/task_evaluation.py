import json
import os

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_links(candidate_data):
    # Placeholder for link validation logic
    # In a real-world scenario, you would check if the links are accessible
    return True

def evaluate_task_1(candidate_data, answer_key):
    candidate_summary = candidate_data['task_1']['summary']
    answer_summary = answer_key['task_1']['summary']
    
    total_claims_correct = candidate_summary['total_claims'] == answer_summary['total_claims']
    total_settlement_correct = candidate_summary['total_settlement_amount'] == answer_summary['total_settlement_amount']
    average_settlement_correct = candidate_summary['average_settlement_amount'] == answer_summary['average_settlement_amount']
    
    score = sum([total_claims_correct, total_settlement_correct, average_settlement_correct])
    return score, total_claims_correct, total_settlement_correct, average_settlement_correct

def evaluate_task_2(candidate_data, answer_key):
    # Placeholder for text document content validation
    # In a real-world scenario, you would check the content of the text document
    notes_correct = candidate_data['task_2']['notes'] == answer_key['task_2']['notes']
    
    score = 1 if notes_correct else 0
    return score, notes_correct

def main():
    candidate_file = 'test_submission.json'
    answer_key_file = 'answer_key.json'
    
    if not os.path.exists(candidate_file) or not os.path.exists(answer_key_file):
        print("Required files are missing.")
        return
    
    candidate_data = load_json(candidate_file)
    answer_key = load_json(answer_key_file)
    
    # Validate links
    links_valid = validate_links(candidate_data)
    
    # Evaluate Task 1
    task_1_score, total_claims_correct, total_settlement_correct, average_settlement_correct = evaluate_task_1(candidate_data, answer_key)
    
    # Evaluate Task 2
    task_2_score, notes_correct = evaluate_task_2(candidate_data, answer_key)
    
    # Calculate overall score
    total_possible_score = 4  # 3 for Task 1 and 1 for Task 2
    overall_score = ((task_1_score + task_2_score) / total_possible_score) * 100
    
    # Prepare results
    results = {
        "task_1": {
            "total_claims_correct": total_claims_correct,
            "total_settlement_correct": total_settlement_correct,
            "average_settlement_correct": average_settlement_correct,
            "score": task_1_score
        },
        "task_2": {
            "notes_correct": notes_correct,
            "score": task_2_score
        },
        "links_valid": links_valid,
        "overall_score": overall_score
    }
    
    # Save results to JSON
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)
    
    print("Evaluation complete. Results saved to 'test_results.json'.")

if __name__ == "__main__":
    main()