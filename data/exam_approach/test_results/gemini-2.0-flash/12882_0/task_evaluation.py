import json

def load_json(filename):
    """Loads JSON data from a file."""
    with open(filename, 'r') as f:
        return json.load(f)

def evaluate_categories(submission_categories, answer_key_categories):
    """Evaluates product categories and returns detailed results and accuracy."""
    category_results = []
    correct_count = 0
    answer_key_categories_dict = {item['product_name']: item['category'] for item in answer_key_categories}
    submission_categories_dict = {item['product_name']: item['category'] for item in submission_categories}

    for product_name, correct_category in answer_key_categories_dict.items():
        result = {"product_name": product_name}
        if product_name in submission_categories_dict:
            submitted_category = submission_categories_dict[product_name]
            if submitted_category == correct_category:
                result["category_correct"] = True
                correct_count += 1
            else:
                result["category_correct"] = False
                result["submitted_category"] = submitted_category
                result["correct_category"] = correct_category
        else:
            result["category_correct"] = False
            result["submitted_category"] = None # or "Not Found"
            result["correct_category"] = correct_category
        category_results.append(result)

    accuracy = (correct_count / len(answer_key_categories)) * 100 if len(answer_key_categories) > 0 else 0
    return category_results, accuracy

def evaluate_demand_analysis(submission_demand_analysis, answer_key_demand_analysis):
    """Evaluates demand sufficiency analysis and returns detailed results and accuracy."""
    demand_results = []
    correct_count = 0
    answer_key_demand_dict = {item['product_name']: item for item in answer_key_demand_analysis}
    submission_demand_dict = {item['product_name']: item for item in submission_demand_analysis}

    for product_name, correct_demand_data in answer_key_demand_dict.items():
        result = {"product_name": product_name, "fields_correct": []}
        if product_name in submission_demand_dict:
            submission_demand_data = submission_demand_dict[product_name]
            is_product_correct = True

            fields_to_check = ["total_ordered_quantity", "demand_quantity", "demand_status", "additional_quantity_needed"]
            for field in fields_to_check:
                field_result = {"field_name": field}
                if submission_demand_data[field] == correct_demand_data[field]:
                    field_result["correct"] = True
                    result["fields_correct"].append(field_result)
                else:
                    field_result["correct"] = False
                    field_result["submitted_value"] = submission_demand_data[field]
                    field_result["correct_value"] = correct_demand_data[field]
                    result["fields_correct"].append(field_result)
                    is_product_correct = False # If any field is incorrect, the whole product analysis is not fully correct

            if is_product_correct:
                correct_count += 1
                result["product_analysis_correct"] = True
            else:
                 result["product_analysis_correct"] = False

        else:
            result["product_analysis_correct"] = False
            result["error"] = "Product not found in submission"
            for field in ["total_ordered_quantity", "demand_quantity", "demand_status", "additional_quantity_needed"]:
                result["fields_correct"].append({"field_name": field, "correct": False, "error": "Product not found in submission"})


        demand_results.append(result)

    accuracy = (correct_count / len(answer_key_demand_analysis)) * 100 if len(answer_key_demand_analysis) > 0 else 0
    return demand_results, accuracy

def save_results_json(results, filename):
    """Saves results to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    submission_file = 'test_submission.json'
    answer_key_file = 'answer_key.json'
    results_file = 'test_results.json'

    answer_key_data = load_json(answer_key_file)
    submission_data = load_json(submission_file)

    category_results, category_accuracy = evaluate_categories(submission_data.get("product_categories", []), answer_key_data["product_categories"])
    demand_results, demand_accuracy = evaluate_demand_analysis(submission_data.get("demand_sufficiency_analysis", []), answer_key_data["demand_sufficiency_analysis"])

    overall_score = (category_accuracy + demand_accuracy) / 2

    test_results = {
        "overall_score": round(overall_score, 2),
        "category_accuracy": round(category_accuracy, 2),
        "demand_accuracy": round(demand_accuracy, 2),
        "category_results": category_results,
        "demand_results": demand_results
    }

    save_results_json(test_results, results_file)
    print(f"Test results saved to '{results_file}'")