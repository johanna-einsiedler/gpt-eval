import json
from collections import defaultdict

def load_json_file(filename):
    """Load JSON file and return its content."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        exit(1)

def calculate_category_score(submitted, expected, category_name):
    """Calculate the score for a specific category."""
    score = 0
    max_score = len(expected)
    details = []
    
    if max_score == 0:
        return 1.0, details  # Full points if no entries expected
    
    # Convert lists to dictionaries with claim_id as key for easier comparison
    submitted_dict = {entry['claim_id']: entry for entry in submitted}
    expected_dict = {entry['claim_id']: entry for entry in expected}
    
    # Check for correct entries
    for claim_id, expected_entry in expected_dict.items():
        if claim_id in submitted_dict:
            submitted_entry = submitted_dict[claim_id]
            if submitted_entry == expected_entry:
                score += 1
                details.append({
                    'claim_id': claim_id,
                    'status': 'correct',
                    'message': f"Correct {category_name[:-1]} found"
                })
            else:
                details.append({
                    'claim_id': claim_id,
                    'status': 'incorrect',
                    'message': f"Incorrect entry for {category_name[:-1]}",
                    'expected': expected_entry,
                    'submitted': submitted_entry
                })
        else:
            details.append({
                'claim_id': claim_id,
                'status': 'missing',
                'message': f"Missing {category_name[:-1]}",
                'expected': expected_entry
            })
    
    # Check for extra entries (not in expected)
    for claim_id, submitted_entry in submitted_dict.items():
        if claim_id not in expected_dict:
            score -= 0.5  # Penalty for incorrect extra entries
            details.append({
                'claim_id': claim_id,
                'status': 'extra',
                'message': f"Unexpected {category_name[:-1]} submitted",
                'submitted': submitted_entry
            })
    
    # Ensure score doesn't go negative
    score = max(0, score)
    
    return score / max_score, details

def validate_json_structure(submission):
    """Validate the basic structure of the submission JSON."""
    required_fields = ["overpayments", "underpayments", "irregularities"]
    for field in required_fields:
        if field not in submission:
            return False, f"Missing required field: {field}"
    
    # Check all entries have required fields
    for category in required_fields:
        for entry in submission.get(category, []):
            if category in ["overpayments", "underpayments"]:
                required_entry_fields = ["claim_id", "amount_paid", "approved_amount", "discrepancy"]
            else:
                required_entry_fields = ["claim_id", "issue_description"]
            
            for field in required_entry_fields:
                if field not in entry:
                    return False, f"Missing field '{field}' in {category} entry"
    
    return True, "JSON structure is valid"

def evaluate_submission():
    """Main function to evaluate the submission."""
    # Load files
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')
    
    # Validate JSON structure first
    structure_valid, structure_message = validate_json_structure(submission)
    if not structure_valid:
        results = {
            'overall_score': 0,
            'error': structure_message,
            'details': {
                'structure_error': structure_message
            }
        }
    else:
        # Calculate scores for each category
        overpayment_score, overpayment_details = calculate_category_score(
            submission['overpayments'],
            answer_key['expected_overpayments'],
            'overpayments'
        )
        
        underpayment_score, underpayment_details = calculate_category_score(
            submission['underpayments'],
            answer_key['expected_underpayments'],
            'underpayments'
        )
        
        irregularity_score, irregularity_details = calculate_category_score(
            submission['irregularities'],
            answer_key['expected_irregularities'],
            'irregularities'
        )
        
        # Calculate overall score (weighted average)
        category_weights = {
            'overpayments': 0.3,
            'underpayments': 0.4,
            'irregularities': 0.3
        }
        
        overall_score = (
            overpayment_score * category_weights['overpayments'] +
            underpayment_score * category_weights['underpayments'] +
            irregularity_score * category_weights['irregularities']
        ) * 100  # Convert to percentage
        
        # Prepare results
        results = {
            'overall_score': round(overall_score, 2),
            'category_scores': {
                'overpayments': round(overpayment_score * 100, 2),
                'underpayments': round(underpayment_score * 100, 2),
                'irregularities': round(irregularity_score * 100, 2)
            },
            'details': {
                'overpayments': overpayment_details,
                'underpayments': underpayment_details,
                'irregularities': irregularity_details
            }
        }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    evaluate_submission()