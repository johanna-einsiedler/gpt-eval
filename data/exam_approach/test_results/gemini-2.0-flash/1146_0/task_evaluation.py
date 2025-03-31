import json
import re
from urllib.parse import urlparse

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def evaluate_question_1(candidate_answer, correct_answer_data):
    score = 0
    feedback = ""
    regulation_name_candidate = ""
    url_candidate = ""

    try:
        parts = candidate_answer.split(", URL: ")
        regulation_name_candidate = parts[0].replace("Regulation Name: ", "").strip() if len(parts) > 0 and "Regulation Name: " in parts[0] else ""
        url_candidate = parts[1].strip() if len(parts) > 1 else ""
    except:
        feedback = "Answer format incorrect."
        return score, feedback

    regulation_name_expected_keywords = ["ISO 14001", "EMAS", "LEED", "FSC", "sustainable procurement", "environmental"] # Example keywords, can be expanded
    regulation_name_found = False
    for keyword in regulation_name_expected_keywords:
        if keyword.lower() in regulation_name_candidate.lower():
            regulation_name_found = True
            break

    url_valid = validate_url(url_candidate)

    if regulation_name_found and url_valid:
        score = 1
        feedback = "Correct regulation name and valid URL provided."
    elif regulation_name_found and not url_valid:
        score = 0.5
        feedback = "Correct regulation name but invalid URL."
    elif not regulation_name_found and url_valid:
        score = 0.3 # Partial for effort, if URL is valid but regulation name is wrong
        feedback = "Regulation name not clearly identified, but valid URL provided."
    else:
        feedback = "Incorrect regulation name and/or invalid URL."

    return score, feedback

def evaluate_keyword_based_question(candidate_answer, correct_answer_data):
    score = 0
    feedback = ""
    correct_keywords = correct_answer_data.get("correct_answer_keywords", [])
    negative_keywords = correct_answer_data.get("negative_keywords", [])

    if not candidate_answer:
        feedback = "No answer provided."
        return score, feedback

    answer_lower = candidate_answer.lower()
    correct_keyword_count = 0
    negative_keyword_found = False

    for keyword in correct_keywords:
        if keyword.lower() in answer_lower:
            correct_keyword_count += 1

    for keyword in negative_keywords:
        if keyword.lower() in answer_lower:
            negative_keyword_found = True
            break

    if negative_keyword_found:
        feedback = "Answer contains negative keywords, indicating misunderstanding."
    elif correct_keyword_count >= len(correct_keywords) * 0.6: # Adjust threshold as needed, e.g., require 60% of keywords
        score = 1
        feedback = "Correct answer - contains most key concepts."
    elif correct_keyword_count > 0:
        score = 0.5
        feedback = "Partially correct - mentions some key concepts but missing others."
    else:
        feedback = "Incorrect answer - missing key concepts."

    return score, feedback

def evaluate_question_4(candidate_answer, correct_answer_data):
    score = 0
    feedback = ""
    step1_keywords_expected = correct_answer_data.get("correct_answer_step1_keywords", [])
    step2_keywords_expected = correct_answer_data.get("correct_answer_step2_keywords", [])

    step1_text = ""
    step2_text = ""

    try:
        parts = candidate_answer.split(", Step 2: ")
        step1_text = parts[0].replace("Step 1: ", "").strip() if len(parts) > 0 and "Step 1: " in parts[0] else ""
        step2_text = parts[1].strip() if len(parts) > 1 else ""
    except:
        feedback = "Answer format for steps is incorrect."
        return score, feedback

    step1_keywords_found = 0
    for keyword in step1_keywords_expected:
        if keyword.lower() in step1_text.lower():
            step1_keywords_found += 1

    step2_keywords_found = 0
    for keyword in step2_keywords_expected:
        if keyword.lower() in step2_text.lower():
            step2_keywords_found += 1

    if step1_keywords_found >= len(step1_keywords_expected) * 0.5 and step2_keywords_found >= len(step2_keywords_expected) * 0.5: # Adjust thresholds
        score = 1
        feedback = "Correct steps described - general search followed by official source."
    elif step1_keywords_found >= len(step1_keywords_expected) * 0.5:
        score = 0.5
        feedback = "Partially correct - Step 1 (general search) is well described, but Step 2 is weaker."
    elif step2_keywords_found >= len(step2_keywords_expected) * 0.5:
        score = 0.5
        feedback = "Partially correct - Step 2 (official source) is well described, but Step 1 is weaker."
    else:
        feedback = "Incorrect steps described - does not follow a logical research strategy."

    return score, feedback


def main():
    try:
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        print("Error: test_submission.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in test_submission.json.")
        return

    try:
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        print("Error: answer_key.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in answer_key.json.")
        return

    question_results = {}
    total_score = 0
    max_score = 0 # Initialize max_score

    for question_num_str in ["1", "2", "3", "4"]:
        question_num = int(question_num_str)
        max_score += 1 # Increment max_score for each question
        candidate_answer = submission.get(question_num_str, "")
        correct_answer_data = answer_key["answer_key"].get(question_num_str, {})
        question_type = correct_answer_data.get("type", "")
        question_score = 0
        question_feedback = ""

        if question_type == "Information Retrieval & Identification":
            question_score, question_feedback = evaluate_question_1(candidate_answer, correct_answer_data)
        elif question_type == "Interpretation of Regulatory Text":
            question_score, question_feedback = evaluate_keyword_based_question(candidate_answer, correct_answer_data)
        elif question_type == "Application of Regulation to Scenario":
            question_score, question_feedback = evaluate_keyword_based_question(candidate_answer, correct_answer_data)
        elif question_type == "Basic Legal Research Strategy":
            question_score, question_feedback = evaluate_question_4(candidate_answer, correct_answer_data)
        else:
            question_feedback = "Question type not recognized for evaluation."

        question_results[question_num] = {"score": question_score, "feedback": question_feedback}
        total_score += question_score

    overall_score_percentage = (total_score / max_score) * 100 if max_score > 0 else 0

    test_results = {
        "candidate_id": submission.get("candidate_id", "N/A"),
        "model_version": submission.get("model_version", "N/A"),
        "question_results": question_results,
        "overall_score": overall_score_percentage
    }

    try:
        with open('test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        print("Test results saved to test_results.json")
    except Exception as e:
        print(f"Error saving test_results.json: {e}")


if __name__ == "__main__":
    main()