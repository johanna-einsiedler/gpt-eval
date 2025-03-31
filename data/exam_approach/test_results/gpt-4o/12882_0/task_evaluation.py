import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def calculate_score(candidate_data, answer_key):
    score = {
        "task1": {
            "total_quantities_score": 0,
            "trends_score": 0
        },
        "task2": {
            "forecasted_demand_score": 0,
            "factors_score": 0
        },
        "overall_score": 0
    }
    
    # Task 1: Total Quantities
    correct_totals = answer_key["task1"]["total_quantities"]
    candidate_totals = candidate_data["task1"]["total_quantities"]
    
    correct_count = 0
    for product, correct_quantity in correct_totals.items():
        candidate_quantity = candidate_totals.get(product, 0)
        if abs(candidate_quantity - correct_quantity) <= 0.05 * correct_quantity:
            correct_count += 1
    
    score["task1"]["total_quantities_score"] = (correct_count / len(correct_totals)) * 100
    
    # Task 1: Trends
    correct_trends = answer_key["task1"]["trends"]
    candidate_trends = candidate_data["task1"]["trends"]
    
    if any(keyword in candidate_trends for keyword in correct_trends.split()):
        score["task1"]["trends_score"] = 100
    
    # Task 2: Forecasted Demand
    correct_forecasts = answer_key["task2"]["forecasted_demand"]
    candidate_forecasts = candidate_data["task2"]["forecasted_demand"]
    
    correct_count = 0
    for product, correct_quantity in correct_forecasts.items():
        candidate_quantity = candidate_forecasts.get(product, 0)
        if abs(candidate_quantity - correct_quantity) <= 0.10 * correct_quantity:
            correct_count += 1
    
    score["task2"]["forecasted_demand_score"] = (correct_count / len(correct_forecasts)) * 100
    
    # Task 2: Factors
    correct_factors = answer_key["task2"]["factors"]
    candidate_factors = candidate_data["task2"]["factors"]
    
    if any(keyword in candidate_factors for keyword in correct_factors.split()):
        score["task2"]["factors_score"] = 100
    
    # Calculate overall score
    total_possible_score = 400  # 100 for each of the 4 components
    total_achieved_score = (
        score["task1"]["total_quantities_score"] +
        score["task1"]["trends_score"] +
        score["task2"]["forecasted_demand_score"] +
        score["task2"]["factors_score"]
    )
    
    score["overall_score"] = (total_achieved_score / total_possible_score) * 100
    
    return score

def main():
    candidate_data = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    results = calculate_score(candidate_data, answer_key)
    
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()