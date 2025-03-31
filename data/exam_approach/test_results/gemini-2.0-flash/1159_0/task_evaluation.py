import json
import re

def evaluate_basic_exam():
    """
    Evaluates the basic exam for Purchasing Agents based on submission and answer key.
    """

    submission_file = 'test_submission.json'
    answer_key_file = 'answer_key.json'
    results_file = 'test_results.json'

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {submission_file} or {answer_key_file}. Make sure they are in the same directory.")
        return

    procedure_keywords = answer_key['answer_key']['procedure_document_keywords']
    answer_q1_key = answer_key['answer_key']['answer_q1']
    answer_q2_key = answer_key['answer_key']['answer_q2']
    answer_q3_key = answer_key['answer_key']['answer_q3']

    procedure_document = submission.get('procedure_document', '')
    answer_q1 = submission.get('answer_q1', '')
    answer_q2 = submission.get('answer_q2', '')
    answer_q3 = submission.get('answer_q3', '')
    candidate_id = submission.get('candidate_id', 'N/A')
    model_version = submission.get('model_version', 'N/A')


    # Evaluate Procedure Document (Keyword Check)
    procedure_keyword_points = 0
    found_keywords = []
    procedure_text_lower = procedure_document.lower()
    for keyword in procedure_keywords:
        if keyword.lower() in procedure_text_lower:
            procedure_keyword_points += 1
            found_keywords.append(keyword)

    # Evaluate Short Answer Questions
    q1_correct = normalize_text(answer_q1) == normalize_text(answer_q1_key)
    q2_correct = normalize_text(answer_q2) == normalize_text(answer_q2_key)
    q3_correct = normalize_text(answer_q3) == normalize_text(answer_q3_key)

    short_answer_points = 0
    if q1_correct: short_answer_points += 1
    if q2_correct: short_answer_points += 1
    if q3_correct: short_answer_points += 1

    # Calculate Overall Score
    max_procedure_points = len(procedure_keywords)
    max_short_answer_points = 3
    max_total_points = max_procedure_points + max_short_answer_points
    total_points_achieved = procedure_keyword_points + short_answer_points
    overall_score_percentage = (total_points_achieved / max_total_points) * 100 if max_total_points > 0 else 0

    # Prepare Results JSON
    results = {
        "candidate_id": candidate_id,
        "model_version": model_version,
        "procedure_document_evaluation": {
            "keyword_points": procedure_keyword_points,
            "max_keyword_points": max_procedure_points,
            "found_keywords": found_keywords,
            "logical_flow_manual_check_required": True, # Flag for manual logical flow check
            "comment": "Manual review needed for logical flow and overall procedure quality."
        },
        "short_answer_evaluation": {
            "q1_correct": q1_correct,
            "q2_correct": q2_correct,
            "q3_correct": q3_correct,
            "short_answer_points": short_answer_points,
            "max_short_answer_points": max_short_answer_points
        },
        "overall_score": round(overall_score_percentage, 2),
        "total_points_achieved": total_points_achieved,
        "max_possible_points": max_total_points
    }

    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation completed. Results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results to {results_file}: {e}")

def normalize_text(text):
    """
    Normalizes text for comparison by lowercasing and removing extra whitespace.
    """
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with single space
    return text

if __name__ == "__main__":
    evaluate_basic_exam()