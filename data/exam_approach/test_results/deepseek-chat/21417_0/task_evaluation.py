import json

def load_json_file(filename):
    """Load a JSON file and return its contents."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def calculate_score(candidate, answer_key, acceptable_variations):
    """Calculate the score based on the candidate's submission and answer key."""
    total_points = 0
    earned_points = 0
    detailed_results = {}
    
    # Policy Details (30 points)
    policy_details_score = 0
    policy_max = 30
    
    # Required exact matches (4 fields, 3 points each)
    exact_fields = ['policy_number', 'coverage_type', 'effective_date', 'expiration_date']
    for field in exact_fields:
        if candidate['policy_details'][field] == answer_key['policy_details'][field]:
            policy_details_score += 3
    
    # Coverage limits (3 fields, 4 points each)
    coverage_limits_correct = 0
    for limit in answer_key['policy_details']['coverage_limits']:
        if (limit in candidate['policy_details']['coverage_limits'] and 
            candidate['policy_details']['coverage_limits'][limit] == answer_key['policy_details']['coverage_limits'][limit]):
            coverage_limits_correct += 1
    policy_details_score += coverage_limits_correct * 4
    
    # Exclusions (3 items, 2 points each)
    exclusions_correct = 0
    if set(candidate['policy_details']['exclusions']) == set(answer_key['policy_details']['exclusions']):
        exclusions_correct = 3
    policy_details_score += exclusions_correct * 2
    
    detailed_results['policy_details'] = {
        'score': policy_details_score,
        'max_score': policy_max,
        'details': {
            'exact_fields': {field: candidate['policy_details'][field] == answer_key['policy_details'][field] 
                             for field in exact_fields},
            'coverage_limits': coverage_limits_correct == 3,
            'exclusions': exclusions_correct == 3
        }
    }
    total_points += policy_max
    earned_points += policy_details_score
    
    # Claim Details (20 points)
    claim_details_score = 0
    claim_max = 20
    
    # Required exact matches (3 fields, 4 points each)
    exact_fields = ['claimant_name', 'incident_date', 'estimated_loss']
    for field in exact_fields:
        if candidate['claim_details'][field] == answer_key['claim_details'][field]:
            claim_details_score += 4
    
    # Claimed damages (3 items, 8 points total)
    if set(candidate['claim_details']['claimed_damages']) == set(answer_key['claim_details']['claimed_damages']):
        claim_details_score += 8
    
    detailed_results['claim_details'] = {
        'score': claim_details_score,
        'max_score': claim_max,
        'details': {
            'exact_fields': {field: candidate['claim_details'][field] == answer_key['claim_details'][field] 
                           for field in exact_fields},
            'claimed_damages': set(candidate['claim_details']['claimed_damages']) == set(answer_key['claim_details']['claimed_damages'])
        }
    }
    total_points += claim_max
    earned_points += claim_details_score
    
    # Coverage Determination (50 points)
    coverage_score = 0
    coverage_max = 50
    
    # Boolean fields (3 fields, 10 points each)
    bool_fields = ['within_policy_period', 'damage_covered', 'exclusions_applicable']
    bool_correct = 0
    for field in bool_fields:
        if candidate['coverage_determination'][field] == answer_key['coverage_determination'][field]:
            bool_correct += 1
    coverage_score += bool_correct * 10
    
    # Notes field (20 points)
    notes = candidate['coverage_determination']['notes'].lower()
    if any(keyword in notes for keyword in ['sudden', 'accidental', 'not flood', 'no flood']):
        coverage_score += 20
    
    detailed_results['coverage_determination'] = {
        'score': coverage_score,
        'max_score': coverage_max,
        'details': {
            'boolean_fields': {field: candidate['coverage_determination'][field] == answer_key['coverage_determination'][field] 
                             for field in bool_fields},
            'notes': any(keyword in notes for keyword in ['sudden', 'accidental', 'not flood', 'no flood'])
        }
    }
    total_points += coverage_max
    earned_points += coverage_score
    
    # Calculate overall score
    overall_score = round((earned_points / total_points) * 100, 2)
    
    return {
        'overall_score': overall_score,
        'detailed_results': detailed_results,
        'total_points': total_points,
        'earned_points': earned_points
    }

def main():
    # Load candidate submission and answer key
    candidate_submission = load_json_file('test_submission.json')
    if not candidate_submission:
        return
    
    answer_key = load_json_file('answer_key.json')
    if not answer_key:
        return
    
    # Calculate score
    results = calculate_score(candidate_submission, answer_key['answer_key'], answer_key.get('acceptable_variations', {}))
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")

if __name__ == "__main__":
    main()