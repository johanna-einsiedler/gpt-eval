import json

def evaluate_exam(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    """
    Evaluates the candidate's exam submission against the answer key and saves the results to a JSON file.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.
        results_file (str): Path to save the test results JSON file.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        print(f"Error: Submission file '{submission_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in submission file '{submission_file}'.")
        return

    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file '{answer_key_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in answer key file '{answer_key_file}'.")
        return

    test_results = {"sections": {}, "overall_score": 0, "total_possible_score": 0, "achieved_score": 0}

    for section_name, section_answers in answer_key.items():
        if section_name not in submission:
            print(f"Warning: Section '{section_name}' not found in submission.")
            test_results["sections"][section_name] = {"score": 0, "possible_score": len(section_answers), "questions": {}}
            test_results["total_possible_score"] += len(section_answers)
            continue

        section_submission = submission[section_name]
        section_score = 0
        possible_section_score = 0
        question_results = {}

        for question_key, correct_answer in section_answers.items():
            possible_section_score += 1
            test_results["total_possible_score"] += 1
            question_score = 0

            if question_key not in section_submission:
                print(f"Warning: Question '{question_key}' in section '{section_name}' not found in submission.")
                question_results[question_key] = {"score": 0, "correct_answer": correct_answer, "candidate_answer": None, "feedback": "Question not answered"}
                continue

            candidate_answer = section_submission[question_key]

            if isinstance(correct_answer, list):
                if isinstance(candidate_answer, list):
                    correct_items = 0
                    for item in candidate_answer:
                        if item in correct_answer:
                            correct_items += 1
                    question_score = correct_items / len(correct_answer) if len(correct_answer) > 0 else 0 # Proportional score for lists
                    feedback = f"Correct items: {correct_items}/{len(correct_answer)}"
                else:
                    question_score = 0
                    feedback = "Expected a list, got different type."

            elif isinstance(correct_answer, str):
                if isinstance(candidate_answer, str):
                    if correct_answer.strip().lower() == candidate_answer.strip().lower(): # Case-insensitive string comparison
                        question_score = 1
                        feedback = "Correct answer"
                    else:
                        question_score = 0
                        feedback = f"Incorrect answer. Correct answer: '{correct_answer}'"
                else:
                    question_score = 0
                    feedback = "Expected a string, got different type."
            else:
                # Handle other answer types if needed, for now assume string or list
                if correct_answer == candidate_answer: # For non-string/list, direct comparison
                    question_score = 1
                    feedback = "Correct answer"
                else:
                    question_score = 0
                    feedback = f"Incorrect answer. Correct answer: '{correct_answer}'"

            section_score += question_score
            test_results["achieved_score"] += question_score
            question_results[question_key] = {"score": question_score, "correct_answer": correct_answer, "candidate_answer": candidate_answer, "feedback": feedback}


        test_results["sections"][section_name] = {"score": section_score, "possible_score": possible_section_score, "questions": question_results}

    overall_percentage = (test_results["achieved_score"] / test_results["total_possible_score"]) * 100 if test_results["total_possible_score"] > 0 else 0
    test_results["overall_score"] = round(overall_percentage, 2)

    try:
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"Test results saved to '{results_file}'")
    except Exception as e:
        print(f"Error saving results to '{results_file}': {e}")


if __name__ == "__main__":
    evaluate_exam()