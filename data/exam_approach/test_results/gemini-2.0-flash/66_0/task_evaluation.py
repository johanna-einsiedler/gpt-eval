import json

def evaluate_exam(submission_file="test_submission.json", answer_key_file="answer_key.json"):
    """
    Evaluates the candidate's submission against the answer key and generates a test results JSON.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the test results.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file not found: {submission_file}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file: {submission_file}"}

    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
        validation_guidelines = answer_key.get('validation_guidelines', {})
        correct_answers = answer_key.get('answer_key', {})
    except FileNotFoundError:
        return {"error": f"Answer key file not found: {answer_key_file}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file: {answer_key_file}"}

    test_results = {}
    total_correct_questions = 0
    total_questions = 0

    for q_num in ["Question 1", "Question 2", "Question 3", "Question 4"]:
        test_results[q_num] = {}
        if q_num in submission and q_num in correct_answers and q_num in validation_guidelines:
            for part in correct_answers[q_num]:
                total_questions += 1
                candidate_answer = submission.get(q_num, {}).get(part)
                correct_answer = correct_answers[q_num][part]
                validation_method_config = validation_guidelines.get(q_num, {}).get(part)

                is_correct = False
                if validation_method_config:
                    validation_type = validation_method_config.get('type')

                    if validation_type == 'exact_numerical_match':
                        try:
                            candidate_value = float(candidate_answer) if candidate_answer is not None else None
                            correct_value = float(correct_answer)
                            is_correct = abs(candidate_value - correct_value) < 1e-6 if candidate_value is not None else False # Using a small tolerance for float comparison
                        except (ValueError, TypeError):
                            is_correct = False
                    elif validation_type == 'exact_text_match':
                        is_correct = str(candidate_answer) == str(correct_answer) if candidate_answer is not None else False
                    elif validation_type == 'keyword_and_concept_match':
                        # Simple keyword check for now - can be improved
                        if candidate_answer is not None and correct_answer is not None:
                            candidate_lower = str(candidate_answer).lower()
                            correct_keywords = [keyword.lower() for keyword in str(correct_answer).split() if len(keyword) > 2] #basic keyword split
                            is_correct = all(keyword in candidate_lower for keyword in correct_keywords)
                        else:
                            is_correct = False

                    elif validation_type == 'numerical_range_match':
                        try:
                            candidate_value = int(candidate_answer) if candidate_answer is not None else None
                            correct_value = int(correct_answer)
                            is_correct = candidate_value == correct_value if candidate_value is not None else False # Exact match for now, can be range later
                        except (ValueError, TypeError):
                            is_correct = False
                    elif validation_type == 'concept_match':
                        # Simple concept check - can be improved
                        if candidate_answer is not None and correct_answer is not None:
                            candidate_lower = str(candidate_answer).lower()
                            correct_keywords = [keyword.lower() for keyword in str(correct_answer).split() if len(keyword) > 2] #basic keyword split
                            is_correct = any(keyword in candidate_lower for keyword in correct_keywords)
                        else:
                            is_correct = False


                test_results[q_num][part] = {
                    "candidate_answer": candidate_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct
                }
                if is_correct:
                    total_correct_questions += 1
        else:
            test_results[q_num] = {"error": "Question data or validation missing in answer key"}

    overall_score = (total_correct_questions / total_questions) * 100 if total_questions > 0 else 0
    test_results["overall_score"] = round(overall_score, 2)

    return test_results

if __name__ == "__main__":
    results = evaluate_exam()

    if "error" in results:
        print(f"Error during evaluation: {results['error']}")
    else:
        try:
            with open("test_results.json", 'w') as outfile:
                json.dump(results, outfile, indent=2)
            print("Test results saved to test_results.json")
        except Exception as e:
            print(f"Error saving results to JSON: {e}")
            print(json.dumps(results, indent=2)) # Print results to console if saving fails