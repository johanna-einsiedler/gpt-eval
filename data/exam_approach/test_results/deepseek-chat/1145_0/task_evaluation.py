import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def evaluate_part1(submission, answer_key):
    results = {}
    score = 0
    total = len(answer_key["part1"])
    
    for key in answer_key["part1"]:
        submission_value = submission["part1"].get(key)
        correct_value = answer_key["part1"][key]
        
        # Special handling for numerical values to account for potential float rounding
        if isinstance(correct_value, (int, float)):
            try:
                submission_float = float(submission_value)
                correct_float = float(correct_value)
                is_correct = abs(submission_float - correct_float) < 0.01  # Allow small rounding differences
            except (ValueError, TypeError):
                is_correct = False
        else:
            is_correct = str(submission_value).strip() == str(correct_value).strip()
        
        results[key] = {
            "submitted": submission_value,
            "correct": correct_value,
            "is_correct": is_correct
        }
        
        if is_correct:
            score += 1
    
    return {
        "results": results,
        "score": score,
        "total": total,
        "percentage": (score / total) * 100 if total > 0 else 0
    }

def evaluate_part2(submission, answer_key):
    results = {}
    score = 0
    total = 2  # Two components to evaluate: boolean and reasoning
    
    # Evaluate boolean answer
    bool_correct = submission["part2"]["price_increase_justified"] == answer_key["part2"]["price_increase_justified"]
    results["price_increase_justified"] = {
        "submitted": submission["part2"]["price_increase_justified"],
        "correct": answer_key["part2"]["price_increase_justified"],
        "is_correct": bool_correct
    }
    if bool_correct:
        score += 1
    
    # Evaluate reasoning (case insensitive comparison, allow minor phrasing differences)
    submitted_reason = str(submission["part2"]["reasoning"]).strip().lower()
    correct_reason = str(answer_key["part2"]["reasoning"]).strip().lower()
    reason_correct = (submitted_reason == correct_reason) or \
                     (correct_reason in submitted_reason) or \
                     (submitted_reason in correct_reason)
    
    results["reasoning"] = {
        "submitted": submission["part2"]["reasoning"],
        "correct": answer_key["part2"]["reasoning"],
        "is_correct": reason_correct
    }
    if reason_correct:
        score += 1
    
    return {
        "results": results,
        "score": score,
        "total": total,
        "percentage": (score / total) * 100 if total > 0 else 0
    }

def calculate_overall_score(part1_results, part2_results):
    total_score = part1_results["score"] + part2_results["score"]
    total_possible = part1_results["total"] + part2_results["total"]
    return (total_score / total_possible) * 100 if total_possible > 0 else 0

def main():
    # Load files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        return
    
    # Evaluate each part
    part1_results = evaluate_part1(submission, answer_key["answer_key"])
    part2_results = evaluate_part2(submission, answer_key["answer_key"])
    
    # Calculate overall score
    overall_score = calculate_overall_score(part1_results, part2_results)
    
    # Prepare final results
    test_results = {
        "part1": part1_results,
        "part2": part2_results,
        "overall_score": overall_score,
        "pass_status": overall_score >= 75  # 75% is passing threshold
    }
    
    # Save results
    with open("test_results.json", 'w') as file:
        json.dump(test_results, file, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()