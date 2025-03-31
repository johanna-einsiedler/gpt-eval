import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_submission(candidate_json, answer_key):
    results = {
        "candidate_id": candidate_json["candidate_id"],
        "suppliers": [],
        "overall_score": 0
    }
    
    total_possible_score = 0
    total_achieved_score = 0
    
    for candidate_supplier in candidate_json['suppliers']:
        key_supplier = next(s for s in answer_key['suppliers'] if s['name'] == candidate_supplier['name'])
        
        supplier_result = {
            "name": candidate_supplier['name'],
            "research": {},
            "evaluation": {
                "score": 0,
                "rank": 0,
                "correct_score": False,
                "correct_rank": False
            }
        }
        
        # Validate research findings
        for criterion, value in candidate_supplier['research'].items():
            expected_value = key_supplier['research'][criterion]
            supplier_result["research"][criterion] = {
                "candidate_value": value,
                "expected_value": expected_value,
                "correct": value == expected_value
            }
        
        # Validate score
        candidate_score = candidate_supplier['evaluation']['score']
        expected_score = key_supplier['evaluation']['score']
        supplier_result["evaluation"]["score"] = candidate_score
        supplier_result["evaluation"]["correct_score"] = (candidate_score == expected_score)
        
        # Validate rank
        candidate_rank = candidate_supplier['evaluation']['rank']
        expected_rank = key_supplier['evaluation']['rank']
        supplier_result["evaluation"]["rank"] = candidate_rank
        supplier_result["evaluation"]["correct_rank"] = (candidate_rank == expected_rank)
        
        # Calculate total scores
        total_possible_score += expected_score
        if supplier_result["evaluation"]["correct_score"]:
            total_achieved_score += candidate_score
        
        results["suppliers"].append(supplier_result)
    
    # Calculate overall score as a percentage
    if total_possible_score > 0:
        results["overall_score"] = (total_achieved_score / total_possible_score) * 100
    
    return results

def save_results(results, file_name):
    with open(file_name, 'w') as file:
        json.dump(results, file, indent=4)

def main():
    candidate_json = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    results = validate_submission(candidate_json, answer_key)
    save_results(results, 'test_results.json')

if __name__ == "__main__":
    main()