import json
import sys
import os
from typing import Dict, List, Any, Tuple, Optional

# --- Constants ---
OUTPUT_FILENAME = "test_results.json"
EXPECTED_TOP_LEVEL_KEYS = {"candidate_id", "exam_version", "interview_questions"}
EXPECTED_QUESTION_KEYS = {"id", "category", "reasoning", "question_text"}
VALID_CATEGORIES = {
    "Income - W2/Employment",
    "Income - Self-Employment",
    "Income - Other",
    "Deductions - Education",
    "Deductions - Charitable",
    "Deductions - Medical",
    "Deductions - Homeowner",
    "Deductions - Other",
    "General/Missing Forms"
}

# --- Helper Functions ---

def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Loads a JSON file and returns its content or None if error."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read file {filepath}. Details: {e}", file=sys.stderr)
        return None

def validate_submission_format(submission_data: Dict[str, Any]) -> List[str]:
    """Validates the structure and basic format of the submission JSON."""
    errors = []
    # 1. Check top-level keys
    missing_keys = EXPECTED_TOP_LEVEL_KEYS - set(submission_data.keys())
    if missing_keys:
        errors.append(f"Missing top-level keys: {', '.join(missing_keys)}")
    extra_keys = set(submission_data.keys()) - EXPECTED_TOP_LEVEL_KEYS
    if extra_keys:
        errors.append(f"Unexpected top-level keys found: {', '.join(extra_keys)}")

    # 2. Check 'interview_questions' format
    if "interview_questions" in submission_data:
        if not isinstance(submission_data["interview_questions"], list):
            errors.append("'interview_questions' should be an array (list).")
        else:
            # 3. Check individual question format
            q_ids = set()
            for i, question in enumerate(submission_data["interview_questions"]):
                q_num = i + 1
                if not isinstance(question, dict):
                    errors.append(f"Item {q_num} in 'interview_questions' is not a dictionary.")
                    continue # Skip further checks for this item

                missing_q_keys = EXPECTED_QUESTION_KEYS - set(question.keys())
                if missing_q_keys:
                    errors.append(f"Question {q_num} (ID: {question.get('id', 'N/A')}) is missing keys: {', '.join(missing_q_keys)}")
                extra_q_keys = set(question.keys()) - EXPECTED_QUESTION_KEYS
                if extra_q_keys:
                     errors.append(f"Question {q_num} (ID: {question.get('id', 'N/A')}) has unexpected keys: {', '.join(extra_q_keys)}")

                # Check data types and values
                q_id = question.get("id")
                if not isinstance(q_id, int):
                    errors.append(f"Question {q_num} has non-integer 'id': {q_id}")
                elif q_id in q_ids:
                     errors.append(f"Question {q_num} has duplicate 'id': {q_id}")
                else:
                    q_ids.add(q_id)

                q_cat = question.get("category")
                if not isinstance(q_cat, str):
                    errors.append(f"Question {q_num} (ID: {q_id}) has non-string 'category'.")
                elif q_cat not in VALID_CATEGORIES:
                    errors.append(f"Question {q_num} (ID: {q_id}) has invalid 'category': '{q_cat}'. Must be one of: {', '.join(VALID_CATEGORIES)}")

                if not isinstance(question.get("reasoning"), str):
                     errors.append(f"Question {q_num} (ID: {q_id}) has non-string 'reasoning'.")
                if not isinstance(question.get("question_text"), str):
                     errors.append(f"Question {q_num} (ID: {q_id}) has non-string 'question_text'.")

    # 4. Check other top-level types (basic)
    if "candidate_id" in submission_data and not isinstance(submission_data["candidate_id"], str):
        errors.append("'candidate_id' should be a string.")
    if "exam_version" in submission_data and not isinstance(submission_data["exam_version"], str):
        errors.append("'exam_version' should be a string.")

    return errors

def evaluate_questions(submission_questions: List[Dict[str, Any]],
                       answer_key_questions: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict], List[Dict]]:
    """
    Compares submission questions against the answer key.

    Returns:
        - score: Number of correctly identified areas.
        - max_score: Total number of areas in the answer key.
        - matched_areas: List of answer key questions matched by the submission.
        - missed_areas: List of answer key questions not matched.
    """
    max_score = len(answer_key_questions)
    score = 0
    matched_areas = []
    missed_areas = []
    submission_question_indices_used = set() # Track used submission questions

    # Create a lookup for faster category matching from submission
    submission_by_category: Dict[str, List[int]] = {}
    for idx, sub_q in enumerate(submission_questions):
        cat = sub_q.get("category")
        if isinstance(cat, str) and cat in VALID_CATEGORIES:
            if cat not in submission_by_category:
                submission_by_category[cat] = []
            submission_by_category[cat].append(idx)

    # Iterate through each required area (answer key question)
    for key_q in answer_key_questions:
        key_category = key_q.get("category")
        key_id = key_q.get("id")
        found_match = False

        if key_category in submission_by_category:
            # Check available submission questions in this category
            for sub_q_idx in submission_by_category[key_category]:
                if sub_q_idx not in submission_question_indices_used:
                    # Found a match for this area
                    score += 1
                    matched_areas.append({
                        "key_question_id": key_id,
                        "key_category": key_category,
                        "matched_submission_question_id": submission_questions[sub_q_idx].get("id"),
                        "matched_submission_question_text": submission_questions[sub_q_idx].get("question_text")
                    })
                    submission_question_indices_used.add(sub_q_idx)
                    found_match = True
                    break # Stop looking for matches for this key question once one is found

        if not found_match:
            missed_areas.append({
                "key_question_id": key_id,
                "key_category": key_category,
                "reasoning": key_q.get("reasoning") # Provide context why it was needed
            })

    return score, max_score, matched_areas, missed_areas

def save_results(results: Dict[str, Any], filepath: str):
    """Saves the evaluation results to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to {filepath}")
    except Exception as e:
        print(f"Error: Could not write results to {filepath}. Details: {e}", file=sys.stderr)

# --- Main Execution ---

def main():
    # 1. Argument Parsing
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_json_file> <answer_key_json_file>", file=sys.stderr)
        sys.exit(1)

    submission_filepath = sys.argv[1]
    answer_key_filepath = sys.argv[2]

    # 2. Load Files
    submission_data = load_json_file(submission_filepath)
    answer_key_data = load_json_file(answer_key_filepath)

    if submission_data is None or answer_key_data is None:
        sys.exit(1) # Errors already printed by load_json_file

    # 3. Initialize Results Structure
    results = {
        "submission_file": submission_filepath,
        "answer_key_file": answer_key_filepath,
        "candidate_id": submission_data.get("candidate_id", "N/A"),
        "exam_version_submitted": submission_data.get("exam_version", "N/A"),
        "exam_version_expected": answer_key_data.get("exam_version", "N/A"),
        "format_validation": {
            "passed": False,
            "errors": []
        },
        "scoring": {
            "score": 0,
            "max_score": 0,
            "matched_areas": [],
            "missed_areas": []
        },
        "overall_score": 0.0 # Percentage
    }

    # 4. Format Validation
    format_errors = validate_submission_format(submission_data)
    if not format_errors:
        results["format_validation"]["passed"] = True
    else:
        results["format_validation"]["errors"] = format_errors
        # Optionally, decide if format errors prevent scoring
        # For now, we'll proceed to score even with minor format issues,
        # but major ones (like missing 'interview_questions') will naturally result in a low score.
        print(f"Warning: Format validation errors found in {submission_filepath}.")


    # 5. Evaluate Questions (only if basic structure allows)
    submission_questions = submission_data.get("interview_questions", [])
    answer_key_questions = answer_key_data.get("interview_questions", [])

    if not isinstance(submission_questions, list):
         results["format_validation"]["errors"].append("Cannot score: 'interview_questions' is not a list.")
         print("Error: Cannot score submission because 'interview_questions' is not a list.", file=sys.stderr)
    elif not isinstance(answer_key_questions, list) or not answer_key_questions:
         print("Error: Cannot score because answer key 'interview_questions' is invalid or empty.", file=sys.stderr)
         # Add error to results? Maybe not, as it's an issue with the key, not submission.
    else:
        score, max_score, matched, missed = evaluate_questions(submission_questions, answer_key_questions)
        results["scoring"]["score"] = score
        results["scoring"]["max_score"] = max_score
        results["scoring"]["matched_areas"] = matched
        results["scoring"]["missed_areas"] = missed

        # 6. Calculate Overall Score
        if max_score > 0:
            results["overall_score"] = round((score / max_score) * 100, 2)
        else:
             results["overall_score"] = 0.0 # Avoid division by zero if key is empty

    # 7. Save Results
    save_results(results, OUTPUT_FILENAME)

if __name__ == "__main__":
    main()