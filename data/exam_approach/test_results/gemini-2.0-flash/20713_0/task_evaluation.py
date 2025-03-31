import json

def validate_basic_exam(submission_file, answer_key_file):
    """
    Validates the basic exam submission against the answer key.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the validation results, correct count, and pass/fail status.
    """
    with open(submission_file, 'r') as f:
        try:
            submission = json.load(f)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in submission file"}
    with open(answer_key_file, 'r') as f:
        try:
            answer_key = json.load(f)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in answer key file"}

    results = {}
    correct_count = 0

    for q_num in range(1, 5):
        q_key_markup = f"markup_rate_q{q_num}"
        q_key_markdown = f"markdown_rate_q{q_num}"
        q_key_price = f"selling_price_q{q_num}"

        if q_key_markup in answer_key and q_key_markup in submission:
            try:
                submission_value = float(submission[q_key_markup])
                answer_value = float(answer_key[q_key_markup])
                if abs(submission_value - answer_value) < 0.01: # Tolerance for percentage
                    results[q_key_markup] = "correct"
                    correct_count += 1
                else:
                    results[q_key_markup] = "incorrect"
            except (ValueError, TypeError):
                results[q_key_markup] = "invalid_format"

        elif q_key_markdown in answer_key and q_key_markdown in submission:
            try:
                submission_value = float(submission[q_key_markdown])
                answer_value = float(answer_key[q_key_markdown])
                if abs(submission_value - answer_value) < 0.01: # Tolerance for percentage
                    results[q_key_markdown] = "correct"
                    correct_count += 1
                else:
                    results[q_key_markdown] = "incorrect"
            except (ValueError, TypeError):
                results[q_key_markdown] = "invalid_format"

        elif q_key_price in answer_key and q_key_price in submission:
            try:
                submission_value = float(submission[q_key_price])
                answer_value = float(answer_key[q_key_price])
                if abs(submission_value - answer_value) < 0.01: # Tolerance for price
                    results[q_key_price] = "correct"
                    correct_count += 1
                else:
                    results[q_key_price] = "incorrect"
            except (ValueError, TypeError):
                results[q_key_price] = "invalid_format"
        elif q_key_markup in answer_key or q_key_markdown in answer_key or q_key_price in answer_key:
            # Handle cases where the key is in answer_key but missing in submission
            if q_key_markup in answer_key: results[q_key_markup] = "missing"
            if q_key_markdown in answer_key: results[q_key_markdown] = "missing"
            if q_key_price in answer_key: results[q_key_price] = "missing"


    # Question 5 Validation (Justification and Price)
    q5_justification_key = "justification_q5"
    q5_price_key = "selling_price_q5"
    if q5_justification_key in submission and q5_price_key in submission:
        justification = submission[q5_justification_key].lower()
        keywords = ["competitive", "below competition", "margin", "profit", "price"] # Example keywords
        if any(keyword in justification for keyword in keywords): # Basic keyword check
            results[q5_justification_key] = "justification_reasonable" # Needs manual review for full assessment
            try:
                submission_price_q5 = float(submission["selling_price_q5"])
                answer_price_q5 = float(answer_key["selling_price_q5"])
                if 3.20 <= submission_price_q5 <= 3.49: # wider acceptable range for Q5 price
                    results["selling_price_q5"] = "correct" # price within wider acceptable range
                    correct_count += 1 # count Q5 as correct if price is reasonable and justification is present
                else:
                    results["selling_price_q5"] = "incorrect_price_q5" # price outside acceptable range
            except (ValueError, TypeError):
                results["selling_price_q5"] = "invalid_price_format_q5"

        else:
            results[q5_justification_key] = "justification_unclear" # Needs manual review - justification missing keywords
            results["selling_price_q5"] = "not_evaluated_price_q5" # price not evaluated due to justification issue
    else:
        if q5_justification_key not in submission:
            results[q5_justification_key] = "justification_missing" # Justification not provided
        if q5_price_key not in submission:
            results["selling_price_q5"] = "selling_price_q5_missing" # selling price for Q5 missing
        results["selling_price_q5"] = "not_evaluated_price_q5" # price not evaluated due to justification issue


    passed = correct_count >= 4
    overall_score = (correct_count / 5) * 100 if not isinstance(correct_count, str) else 0 # handle potential error string in correct_count

    return {"results": results, "correct_count": correct_count, "passed": passed, "overall_score": overall_score}

if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"

    validation_result = validate_basic_exam(submission_file, answer_key_file)

    if "error" in validation_result:
        print(f"Error during validation: {validation_result['error']}")
    else:
        print(json.dumps(validation_result, indent=2))

        try:
            with open(results_file, 'w') as f:
                json.dump(validation_result, f, indent=2)
            print(f"\nValidation results saved to '{results_file}'")
        except Exception as e:
            print(f"Error saving results to '{results_file}': {e}")