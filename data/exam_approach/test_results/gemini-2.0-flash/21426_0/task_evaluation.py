import json
import re

def evaluate_basic_exam(submission_file="test_submission.json", answer_key_file="answer_key.json"):
    """
    Evaluates the basic claims adjuster exam based on a candidate submission and answer key.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the detailed test results and overall score.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": "Could not find submission or answer key file."}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in submission or answer key file."}

    results = {
        "candidate_name": submission.get("candidate_name", "N/A"),
        "candidate_id": submission.get("candidate_id", "N/A"),
        "model_version": submission.get("model_version", "N/A"),
        "exam_type": submission.get("exam_type", "Basic Claims Adjuster Exam"),
        "submission_date": submission.get("submission_date", "N/A"),
        "question_results": {},
        "overall_score": 0.0
    }

    answers_submission = submission.get("answers", {})
    answers_key = answer_key.get("answer_key", {}).get("answers", {})
    validation_guidance = answer_key.get("validation_guidance", {}).get("specific_validation", {})

    question_ids = ["1a", "2a", "2b", "3a", "3b", "4a", "4b", "5a"]
    total_questions = len(question_ids)
    correct_answers_count = 0
    max_score_per_question = 1 # For simplicity, each question is worth 1 point

    for q_id in question_ids:
        results["question_results"][q_id] = {"correct": False, "score": 0, "feedback": ""}
        candidate_answer = answers_submission.get(q_id)
        correct_answer = answers_key.get(q_id)
        guidance = validation_guidance.get(q_id, {})

        if q_id == "1a":
            is_correct = True
            feedback_parts = []
            for sub_q in ["claimant_name", "policy_number", "date_of_loss", "type_of_loss", "policyholder_name", "policy_status", "coverage_type"]:
                if candidate_answer and correct_answer and candidate_answer.get(sub_q) == correct_answer.get(sub_q):
                    feedback_parts.append(f"1a - {sub_q}: Correct")
                else:
                    is_correct = False
                    feedback_parts.append(f"1a - {sub_q}: Incorrect. Expected: '{correct_answer.get(sub_q, 'N/A')}', Got: '{candidate_answer.get(sub_q, 'N/A')}'")
            if is_correct:
                results["question_results"][q_id]["correct"] = True
                results["question_results"][q_id]["score"] = max_score_per_question
                correct_answers_count += 1
            results["question_results"][q_id]["feedback"] = "; ".join(feedback_parts)

        elif q_id == "2a" or q_id == "3a":
            if candidate_answer and correct_answer and str(candidate_answer).lower() == str(correct_answer).lower():
                results["question_results"][q_id]["correct"] = True
                results["question_results"][q_id]["score"] = max_score_per_question
                correct_answers_count += 1
                results["question_results"][q_id]["feedback"] = "Correct."
            else:
                results["question_results"][q_id]["feedback"] = f"Incorrect. Expected: '{correct_answer}', Got: '{candidate_answer}'"

        elif q_id == "2b":
            keywords = ['covered perils', 'dwelling fire coverage', 'fire', 'policy_document_basic.pdf']
            if candidate_answer:
                answer_lower = str(candidate_answer).lower()
                all_keywords_present = all(keyword in answer_lower for keyword in keywords)
                if all_keywords_present:
                    results["question_results"][q_id]["correct"] = True
                    results["question_results"][q_id]["score"] = max_score_per_question
                    correct_answers_count += 1
                    results["question_results"][q_id]["feedback"] = "Justification contains relevant keywords and references policy document."
                else:
                    results["question_results"][q_id]["feedback"] = f"Incorrect or incomplete justification. Expected keywords: {keywords}"
            else:
                 results["question_results"][q_id]["feedback"] = "No justification provided."

        elif q_id == "3b":
            if candidate_answer and correct_answer and str(candidate_answer).strip() == str(correct_answer).strip():
                results["question_results"][q_id]["correct"] = True
                results["question_results"][q_id]["score"] = max_score_per_question
                correct_answers_count += 1
                results["question_results"][q_id]["feedback"] = "Correct authority limit."
            else:
                results["question_results"][q_id]["feedback"] = f"Incorrect authority limit. Expected: '{correct_answer}', Got: '{candidate_answer}'"

        elif q_id == "4a":
            try:
                candidate_value = str(candidate_answer).replace("$", "").replace(",", "")
                correct_value = str(correct_answer).replace("$", "").replace(",", "")
                if candidate_value.isdigit() and correct_value.isdigit() and int(candidate_value) == int(correct_value):
                    results["question_results"][q_id]["correct"] = True
                    results["question_results"][q_id]["score"] = max_score_per_question
                    correct_answers_count += 1
                    results["question_results"][q_id]["feedback"] = "Correct payable amount."
                else:
                    results["question_results"][q_id]["feedback"] = f"Incorrect payable amount. Expected: '{correct_answer}', Got: '{candidate_answer}'"
            except:
                results["question_results"][q_id]["feedback"] = f"Invalid format for payable amount. Expected numerical value. Got: '{candidate_answer}'"

        elif q_id == "4b":
            keywords = ['payment_calculation_template.xlsx', 'b1', 'b2', 'b3', 'assessed damage', 'deductible', 'payable amount', 'formula', 'subtraction']
            if candidate_answer:
                answer_lower = str(candidate_answer).lower()
                all_keywords_present = all(keyword in answer_lower for keyword in keywords)
                if all_keywords_present:
                    results["question_results"][q_id]["correct"] = True
                    results["question_results"][q_id]["score"] = max_score_per_question
                    correct_answers_count += 1
                    results["question_results"][q_id]["feedback"] = "Explanation contains relevant keywords describing spreadsheet calculation."
                else:
                    results["question_results"][q_id]["feedback"] = f"Incomplete explanation of calculation. Expected keywords: {keywords}"
            else:
                results["question_results"][q_id]["feedback"] = "No calculation explanation provided."

        elif q_id == "5a":
            keywords = ['document claim system', 'contact claimant', 'gather information', 'damage assessment', 'acknowledge claim']
            if candidate_answer:
                answer_lower = str(candidate_answer).lower()
                any_keyword_present = any(keyword in answer_lower for keyword in keywords) # Changed to ANY keyword for 5a, as it's about next steps, not all steps necessarily
                if any_keyword_present:
                    results["question_results"][q_id]["correct"] = True
                    results["question_results"][q_id]["score"] = max_score_per_question
                    correct_answers_count += 1
                    results["question_results"][q_id]["feedback"] = "Description of next steps contains relevant concepts."
                else:
                    results["question_results"][q_id]["feedback"] = f"Description of next steps is missing key concepts. Looking for concepts like: {keywords}"
            else:
                results["question_results"][q_id]["feedback"] = "No next steps described."


    results["overall_score"] = (correct_answers_count / total_questions) * 100

    return results


if __name__ == "__main__":
    evaluation_results = evaluate_basic_exam()

    if "error" in evaluation_results:
        print(f"Error during evaluation: {evaluation_results['error']}")
    else:
        results_for_json = {
            "candidate_name": evaluation_results["candidate_name"],
            "candidate_id": evaluation_results["candidate_id"],
            "model_version": evaluation_results["model_version"],
            "exam_type": evaluation_results["exam_type"],
            "submission_date": evaluation_results["submission_date"],
            "overall_score": f"{evaluation_results['overall_score']:.2f}%",
            "detailed_results": evaluation_results["question_results"]
        }
        with open("test_results.json", 'w') as outfile:
            json.dump(results_for_json, outfile, indent=4)
        print("Evaluation completed. Results saved to test_results.json")