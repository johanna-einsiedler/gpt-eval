import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_submission(candidate_json, answer_key_json):
    correct_duty_count = 0
    correct_freight_count = 0
    
    # Validate duty payments
    duty_results = []
    for candidate_item in candidate_json['duty_payments']:
        for answer_item in answer_key_json['duty_payments']:
            if candidate_item['item_id'] == answer_item['item_id']:
                is_correct = abs(candidate_item['total_duty'] - answer_item['total_duty']) < 0.01
                duty_results.append({
                    "item_id": candidate_item['item_id'],
                    "candidate_total_duty": candidate_item['total_duty'],
                    "correct_total_duty": answer_item['total_duty'],
                    "is_correct": is_correct
                })
                if is_correct:
                    correct_duty_count += 1
    
    # Validate freight charges
    freight_results = []
    for candidate_shipment in candidate_json['freight_charges']:
        for answer_shipment in answer_key_json['freight_charges']:
            if candidate_shipment['shipment_id'] == answer_shipment['shipment_id']:
                is_correct = abs(candidate_shipment['freight_charge'] - answer_shipment['freight_charge']) < 0.01
                freight_results.append({
                    "shipment_id": candidate_shipment['shipment_id'],
                    "candidate_freight_charge": candidate_shipment['freight_charge'],
                    "correct_freight_charge": answer_shipment['freight_charge'],
                    "is_correct": is_correct
                })
                if is_correct:
                    correct_freight_count += 1
    
    total_duty_items = len(answer_key_json['duty_payments'])
    total_freight_items = len(answer_key_json['freight_charges'])
    
    duty_accuracy = correct_duty_count / total_duty_items
    freight_accuracy = correct_freight_count / total_freight_items
    
    overall_score = (duty_accuracy + freight_accuracy) / 2 * 100
    
    return {
        "duty_results": duty_results,
        "freight_results": freight_results,
        "duty_accuracy": duty_accuracy,
        "freight_accuracy": freight_accuracy,
        "overall_score": overall_score
    }

def main():
    candidate_json = load_json('test_submission.json')
    answer_key_json = load_json('answer_key.json')
    
    results = validate_submission(candidate_json, answer_key_json)
    
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()