import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def save_json(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def evaluate_submission(candidate_data, answer_key):
    results = {
        "updated_suppliers": [],
        "evaluated_suppliers": [],
        "overall_score": 0
    }
    
    total_fields = 0
    correct_fields = 0

    # Evaluate updated suppliers
    for candidate_supplier in candidate_data['updated_suppliers']:
        supplier_id = candidate_supplier['supplier_id']
        answer_supplier = next((s for s in answer_key['updated_suppliers'] if s['supplier_id'] == supplier_id), None)
        
        if answer_supplier:
            supplier_result = {"supplier_id": supplier_id, "correct_fields": 0, "total_fields": 5}
            for field in ['name', 'reputation', 'history', 'reviews', 'additional_info']:
                total_fields += 1
                if candidate_supplier.get(field) == answer_supplier.get(field):
                    correct_fields += 1
                    supplier_result['correct_fields'] += 1
            results['updated_suppliers'].append(supplier_result)

    # Evaluate evaluated suppliers
    for candidate_supplier in candidate_data['evaluated_suppliers']:
        supplier_id = candidate_supplier['supplier_id']
        answer_supplier = next((s for s in answer_key['evaluated_suppliers'] if s['supplier_id'] == supplier_id), None)
        
        if answer_supplier:
            supplier_result = {"supplier_id": supplier_id, "correct_fields": 0, "total_fields": 3}
            for field in ['name', 'score', 'rank']:
                total_fields += 1
                if candidate_supplier.get(field) == answer_supplier.get(field):
                    correct_fields += 1
                    supplier_result['correct_fields'] += 1
            results['evaluated_suppliers'].append(supplier_result)

    # Calculate overall score
    results['overall_score'] = (correct_fields / total_fields) * 100 if total_fields > 0 else 0

    return results

def main():
    candidate_data = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    results = evaluate_submission(candidate_data, answer_key)
    
    save_json(results, 'test_results.json')
    print("Evaluation complete. Results saved to 'test_results.json'.")

if __name__ == "__main__":
    main()