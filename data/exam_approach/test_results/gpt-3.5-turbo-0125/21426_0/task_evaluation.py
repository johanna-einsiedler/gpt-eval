import json

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_submission(candidate_data, answer_key_data):
    """Validate the candidate's submission against the answer key."""
    # Initialize counters
    correct_document_reviews = 0
    correct_claim_decisions = 0
    
    # Validate document reviews
    for candidate_review in candidate_data['document_review']:
        for answer_review in answer_key_data['document_review']:
            if candidate_review['claim_id'] == answer_review['claim_id']:
                if (set(candidate_review['discrepancies']) == set(answer_review['discrepancies']) and
                    set(candidate_review['missing_information']) == set(answer_review['missing_information'])):
                    correct_document_reviews += 1
    
    # Validate claim decisions
    for candidate_decision in candidate_data['claim_decisions']:
        for answer_decision in answer_key_data['claim_decisions']:
            if candidate_decision['claim_id'] == answer_decision['claim_id']:
                if (candidate_decision['calculated_payable_amount'] == answer_decision['calculated_payable_amount'] and
                    candidate_decision['decision'] == answer_decision['decision'] and
                    candidate_decision['justification'] == answer_decision['justification']):
                    correct_claim_decisions += 1
    
    # Calculate accuracy
    document_review_accuracy = correct_document_reviews / len(answer_key_data['document_review'])
    claim_decision_accuracy = correct_claim_decisions / len(answer_key_data['claim_decisions'])
    
    # Calculate overall score
    overall_score = (document_review_accuracy + claim_decision_accuracy) / 2 * 100
    
    # Prepare results
    results = {
        "document_review_accuracy": document_review_accuracy * 100,
        "claim_decision_accuracy": claim_decision_accuracy * 100,
        "overall_score": overall_score
    }
    
    return results

def save_results(results, file_path):
    """Save the results to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    # Load candidate submission and answer key
    candidate_data = load_json('test_submission.json')
    answer_key_data = load_json('answer_key.json')
    
    # Validate submission and calculate results
    results = validate_submission(candidate_data, answer_key_data)
    
    # Save results to a JSON file
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()