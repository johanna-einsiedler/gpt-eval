import json
import os

def validate_submission(submission_file, answer_key_file):
    """
    Validates a candidate's submission against an answer key.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the validation results, including:
            - results (dict): Detailed results for each question.
            - total_correct_questions (int): Number of correct questions.
            - overall_score (float): Percentage of correct answers.
            - pass (bool): True if the candidate passed, False otherwise.
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
    except FileNotFoundError:
        return {"error": f"Answer key file not found: {answer_key_file}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file: {answer_key_file}"}

    results = {}
    total_correct = 0
    total_questions = 0

    for scenario_name in ["scenario_1", "scenario_2", "scenario_3"]:
        results[scenario_name] = {}
        if scenario_name not in answer_key:
            results[scenario_name]["error"] = "Scenario not found in answer key"
            continue
        if scenario_name not in submission:
            results[scenario_name]["error"] = "Scenario not found in submission"
            continue

        for question_name in answer_key[scenario_name]:
            total_questions += 1
            candidate_answer = submission.get(scenario_name, {}).get(question_name, "").strip()
            correct_answer = answer_key[scenario_name][question_name].strip()

            if candidate_answer == correct_answer:
                is_correct = True
                total_correct += 1
            else:
                is_correct = False

            results[scenario_name][question_name] = {
                "candidate_answer": candidate_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }

    pass_fail = total_correct >= 7  # Passing criteria: 7 or more correct
    overall_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0

    return {
        "results": results,
        "total_correct_questions": total_correct,
        "overall_score": overall_score,
        "pass": pass_fail
    }

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    submission_file = os.path.join(script_dir, "test_submission.json")
    answer_key_file = os.path.join(script_dir, "answer_key.json")
    results_file = os.path.join(script_dir, "test_results.json")

    validation_report = validate_submission(submission_file, answer_key_file)

    if "error" in validation_report:
        print(f"Error during validation: {validation_report['error']}")
    else:
        validation_report_for_json = validation_report.copy() # Create a copy to avoid modifying original dict
        validation_report_for_json['overall_score'] = round(validation_report_for_json['overall_score'], 2) # Round percentage for json output

        with open(results_file, 'w') as outfile:
            json.dump(validation_report_for_json, outfile, indent=2)

        print(f"Validation results saved to '{results_file}'")
        print(json.dumps(validation_report_for_json, indent=2))

        if validation_report["pass"]:
            print("\nResult: PASS")
        else:
            print("\nResult: FAIL")