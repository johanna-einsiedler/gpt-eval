import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def validate_submission(submission, answer_key):
    errors = []
    score = 100
    
    # Extract answer key components
    ak = answer_key.get("answer_key", {})
    
    # Numeric validation
    if submission.get("recommended_reserve") != ak.get("recommended_reserve"):
        errors.append(f"Reserve amount error: Expected {ak.get('recommended_reserve')}, got {submission.get('recommended_reserve')}")
        score -= 40
    
    # Policy reference validation
    if submission.get("policy_reference") != ak.get("policy_reference"):
        errors.append(f"Policy reference error: Expected '{ak.get('policy_reference')}'")
        score -= 30
    
    # Adjustment reason validation
    reason = submission.get("adjustment_reason", "")
    for phrase in ak.get("adjustment_reason", {}).get("required_phrases", []):
        if phrase not in reason:
            errors.append(f"Missing required phrase: '{phrase}'")
            score -= 10
    if len(reason) > ak.get("adjustment_reason", {}).get("max_length", 200):
        errors.append(f"Reason exceeds {ak.get('adjustment_reason', {}).get('max_length', 200)} characters")
        score -= 5
    
    # Supporting data validation
    if sorted(submission.get("supporting_data", [])) != sorted(ak.get("supporting_data", [])):
        errors.append(f"Supporting data error: Expected {ak.get('supporting_data')}")
        score -= 20
    
    # Rounding validation
    if submission.get("recommended_reserve", 0) % 1000 != 0:
        errors.append("Reserve not rounded to nearest $1000")
        score -= 5
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    return {
        "passed": score >= 80,
        "overall_score": score,
        "errors": errors
    }

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        return
    
    # Validate the submission
    results = validate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()