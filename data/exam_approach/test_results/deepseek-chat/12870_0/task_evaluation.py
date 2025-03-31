import json
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def validate_submission(submission_file, answer_key_file):
    with open(submission_file) as f:
        submission = json.load(f)
    
    with open(answer_key_file) as f:
        answer_key = json.load(f)
    
    # Initialize results structure
    results = {
        "industry_trends": {
            "score": 0,
            "max_score": 3,
            "details": []
        },
        "notable_deals": {
            "score": 0,
            "max_score": 3,
            "details": []
        },
        "overall_score": 0
    }
    
    # Validate Industry Trends (exact match required)
    trend_score = 0
    for i in range(3):
        trend_match = True
        for field in ['trend', 'description', 'impact']:
            sub_val = submission['industry_trends'][i][field].strip()
            ans_val = answer_key['answer_key']['industry_trends'][i][field].strip()
            if sub_val != ans_val:
                trend_match = False
                break
        
        if trend_match:
            trend_score += 1
            results['industry_trends']['details'].append({
                "trend": submission['industry_trends'][i]['trend'],
                "status": "correct"
            })
        else:
            results['industry_trends']['details'].append({
                "trend": submission['industry_trends'][i]['trend'],
                "status": "incorrect",
                "expected": answer_key['answer_key']['industry_trends'][i]
            })
    
    results['industry_trends']['score'] = trend_score
    
    # Validate Notable Deals (partial credit allowed)
    deal_score = 0
    for i in range(3):
        deal_correct = 0
        max_fields = 3  # parties_involved, deal_value, significance
        
        # Check parties_involved (exact match)
        parties_match = (submission['notable_deals'][i]['parties_involved'] == 
                        answer_key['answer_key']['notable_deals'][i]['parties_involved'])
        
        # Check deal_value (exact match)
        value_match = (submission['notable_deals'][i]['deal_value'] == 
                      answer_key['answer_key']['notable_deals'][i]['deal_value'])
        
        # Check significance (fuzzy match)
        sig_similarity = similarity(
            submission['notable_deals'][i]['significance'].lower(),
            answer_key['answer_key']['notable_deals'][i]['significance'].lower()
        )
        sig_match = sig_similarity > 0.6  # 60% similarity threshold
        
        if parties_match:
            deal_correct += 1
        if value_match:
            deal_correct += 1
        if sig_match:
            deal_correct += 1
        
        deal_score += deal_correct / max_fields
        
        results['notable_deals']['details'].append({
            "parties": submission['notable_deals'][i]['parties_involved'],
            "parties_match": parties_match,
            "value_match": value_match,
            "significance_match": sig_match,
            "significance_similarity": round(sig_similarity * 100)
        })
    
    results['notable_deals']['score'] = round(deal_score)
    
    # Calculate overall score (weighted average)
    max_possible = (results['industry_trends']['max_score'] + 
                   results['notable_deals']['max_score'])
    total_score = (results['industry_trends']['score'] + 
                  results['notable_deals']['score'])
    results['overall_score'] = round((total_score / max_possible) * 100)
    
    return results

if __name__ == "__main__":
    # Evaluate the submission
    evaluation_results = validate_submission(
        'test_submission.json',
        'answer_key.json'
    )
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")