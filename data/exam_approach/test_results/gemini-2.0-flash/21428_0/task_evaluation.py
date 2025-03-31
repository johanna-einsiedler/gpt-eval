import json

def validate_claimant_information_consistency(submission_answer, correct_answer):
    return submission_answer == correct_answer

def validate_policy_coverage_verification(submission_answer, correct_answer):
    return submission_answer == correct_answer

def validate_open_claim_count(submission_answer, correct_answer):
    try:
        submission_count = int(submission_answer)
        return submission_count == correct_answer
    except (ValueError, TypeError):
        return False

def validate_average_closed_claim_payment(submission_answer, correct_answer):
    try:
        submission_payment = float(submission_answer)
        correct_payment = float(correct_answer)
        return abs(submission_payment - correct_payment) < 0.005 # Using a small tolerance for float comparison
    except (ValueError, TypeError):
        return False

def validate_top_claim_types(submission_answer, correct_answer):
    if not isinstance(submission_answer, dict) or not isinstance(correct_answer, dict):
        return False

    submission_keys = list(submission_answer.keys())
    correct_keys = list(correct_answer.keys())

    if submission_keys != correct_keys: # Order and keys must be the same for basic validation
        return False

    for key in correct_keys:
        try:
            submission_count = int(submission_answer[key])
            correct_count = int(correct_answer[key])
            if submission_count != correct_count:
                return False
        except (ValueError, TypeError, KeyError):
            return False
    return True

def validate_supervisor_approval_required(submission_answer, correct_answer):
    return submission_answer == correct_answer

def validate_approval_reasoning(submission_answer, correct_answer):
    # Basic keyword check for reasoning - can be improved with NLP for more robust evaluation
    keywords_correct = ["section 2.1", "vehicle collision claims", "$3,000", "$2,800", "below", "adjuster authority"]
    submission_lower = submission_answer.lower()
    all_keywords_present = all(keyword in submission_lower for keyword in keywords_correct)
    return all_keywords_present and submission_answer.strip() != "" # Ensure not just keywords but some reasoning


def evaluate_test(submission_file="test_submission.json", answer_key_file="answer_key.json", results_file="test_results.json"):
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file '{submission_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file '{submission_file}'."}

    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": f"Answer key file '{answer_key_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file '{answer_key_file}'."}

    results = {}
    results_detail = {}
    total_questions = 0
    correct_answers = 0

    validation_functions = {
        "claimant_information_consistency": validate_claimant_information_consistency,
        "policy_coverage_verification": validate_policy_coverage_verification,
        "open_claim_count": validate_open_claim_count,
        "average_closed_claim_payment": validate_average_closed_claim_payment,
        "top_claim_types": validate_top_claim_types,
        "supervisor_approval_required": validate_supervisor_approval_required,
        "approval_reasoning": validate_approval_reasoning,
    }

    for question_key, correct_answer in answer_key.items():
        total_questions += 1
        submission_answer = submission.get(question_key)
        validator = validation_functions.get(question_key)

        if validator:
            is_correct = validator(submission_answer, correct_answer)
            if is_correct:
                correct_answers += 1
            results_detail[question_key] = {
                "submission": submission_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }
        else:
            results_detail[question_key] = {
                "submission": submission_answer,
                "correct_answer": correct_answer,
                "is_correct": False,
                "error": "No validation function found for this question type"
            }

    overall_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    results["overall_score"] = round(overall_score, 2)
    results["detailed_results"] = results_detail

    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Test results saved to '{results_file}'")
    except Exception as e:
        return {"error": f"Error saving results to '{results_file}': {e}"}

    return results

if __name__ == "__main__":
    # Example usage:
    # Assuming 'answer_key.json' and 'test_submission.json' are in the same directory
    evaluation_results = evaluate_test()
    if "error" in evaluation_results:
        print(f"Error during evaluation: {evaluation_results['error']}")
    else:
        print(f"Overall Score: {evaluation_results['overall_score']}%")