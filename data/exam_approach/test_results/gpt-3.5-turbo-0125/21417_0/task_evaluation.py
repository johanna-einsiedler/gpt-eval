import json

def evaluate_task_1(candidate_discrepancies, answer_discrepancies):
    # Check if the candidate's discrepancies match the answer key
    correct_discrepancies = set(answer_discrepancies)
    candidate_discrepancies_set = set(candidate_discrepancies)
    
    # Calculate score for Task 1
    if candidate_discrepancies_set == correct_discrepancies:
        return 1.0  # Full score
    else:
        return 0.0  # No score

def evaluate_task_2(candidate_coverage, candidate_explanation, answer_coverage, answer_explanation):
    # Check if the coverage determination is correct
    coverage_score = 1.0 if candidate_coverage == answer_coverage else 0.0
    
    # Check if the explanation contains necessary elements
    explanation_score = 0.0
    if coverage_score == 1.0:  # Only check explanation if coverage is correct
        required_terms = ["Vehicle Accident", "within the maximum claim amount of $10,000"]
        if all(term in candidate_explanation for term in required_terms):
            explanation_score = 1.0
    
    # Calculate total score for Task 2
    return (coverage_score + explanation_score) / 2

def main():
    # Load candidate submission
    with open('test_submission.json', 'r') as file:
        candidate_submission = json.load(file)
    
    # Load answer key
    with open('answer_key.json', 'r') as file:
        answer_key = json.load(file)
    
    # Evaluate Task 1
    task_1_score = evaluate_task_1(
        candidate_submission['task_1']['discrepancies'],
        answer_key['task_1']['discrepancies']
    )
    
    # Evaluate Task 2
    task_2_score = evaluate_task_2(
        candidate_submission['task_2']['coverage_determination'],
        candidate_submission['task_2']['explanation'],
        answer_key['task_2']['coverage_determination'],
        answer_key['task_2']['explanation']
    )
    
    # Calculate overall score
    overall_score = (task_1_score + task_2_score) / 2 * 100  # Convert to percentage
    
    # Prepare results
    results = {
        "task_1_score": task_1_score,
        "task_2_score": task_2_score,
        "overall_score": overall_score
    }
    
    # Save results to JSON
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    main()