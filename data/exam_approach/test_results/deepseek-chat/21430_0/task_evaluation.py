import json

def evaluate_submission():
    # Load the answer key and submission
    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)['answer_key']
    
    with open('test_submission.json', 'r') as f:
        submission = json.load(f)
    
    # Initialize results structure
    results = {
        'overall_score': 0,
        'case_1': {
            'red_flags': {'score': 0, 'max_score': 2, 'details': []},
            'referral_reason': {'score': 0, 'max_score': 1, 'details': ''},
            'recommended_action': {'score': 0, 'max_score': 1, 'details': ''},
            'case_score': 0
        },
        'case_2': {
            'red_flags': {'score': 0, 'max_score': 2, 'details': []},
            'referral_reason': {'score': 0, 'max_score': 1, 'details': ''},
            'recommended_action': {'score': 0, 'max_score': 1, 'details': ''},
            'case_score': 0
        }
    }
    
    # Define key terms for referral reason validation
    key_terms = {
        'case_1': ['witness', 'conflict', 'late', 'camera'],
        'case_2': ['policy', 'increase', 'town', 'kitchen']
    }
    
    # Evaluate each case
    for case in ['case_1', 'case_2']:
        # Evaluate red flags
        submitted_flags = submission[case]['red_flags']
        expected_flags = answer_key[case]['red_flags']
        
        # Check if submitted flags match expected concepts
        correct_flags = 0
        flag_details = []
        for i, flag in enumerate(submitted_flags):
            # Check if flag matches any of the expected flags (case insensitive)
            flag_lower = flag.lower()
            matches = any(any(phrase.lower() in flag_lower for phrase in expected_flag.split(':')) 
                         for expected_flag in expected_flags)
            
            if matches and i < 2:  # Only count first 2 flags
                correct_flags += 1
                flag_details.append(f"Flag {i+1}: Correct")
            else:
                flag_details.append(f"Flag {i+1}: Incorrect or extra")
        
        results[case]['red_flags']['score'] = min(correct_flags, 2)
        results[case]['red_flags']['details'] = flag_details
        
        # Evaluate referral reason
        submitted_reason = submission[case]['referral_reason'].lower()
        # Check if contains at least the first two key terms
        if all(term in submitted_reason for term in key_terms[case][:2]):
            results[case]['referral_reason']['score'] = 1
            results[case]['referral_reason']['details'] = "Correct - contains key concepts"
        else:
            results[case]['referral_reason']['details'] = "Incorrect - missing key concepts"
        
        # Evaluate recommended action
        if submission[case]['recommended_action'] == answer_key[case]['recommended_action']:
            results[case]['recommended_action']['score'] = 1
            results[case]['recommended_action']['details'] = "Correct"
        else:
            results[case]['recommended_action']['details'] = "Incorrect"
        
        # Calculate case score
        case_max = (results[case]['red_flags']['max_score'] + 
                    results[case]['referral_reason']['max_score'] + 
                    results[case]['recommended_action']['max_score'])
        case_score = (results[case]['red_flags']['score'] + 
                     results[case]['referral_reason']['score'] + 
                     results[case]['recommended_action']['score'])
        results[case]['case_score'] = case_score / case_max * 100
    
    # Calculate overall score
    total_max = 8  # 2 cases × (2 flags + 1 reason + 1 action)
    total_score = (sum(results['case_1'][field]['score'] for field in ['red_flags', 'referral_reason', 'recommended_action']) +
                  sum(results['case_2'][field]['score'] for field in ['red_flags', 'referral_reason', 'recommended_action'])
    results['overall_score'] = total_score / total_max * 100
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    evaluate_submission()