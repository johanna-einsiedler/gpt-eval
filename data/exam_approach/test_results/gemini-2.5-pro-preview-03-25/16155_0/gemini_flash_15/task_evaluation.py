import json
import sys
import os
from typing import Dict, Any, List, Tuple, Optional

# --- Constants ---
EXPECTED_ASSESSMENT_AREA = "Customer Needs Assessment - Basic"
ALLOWED_QUESTION_TYPES = ["Rating Scale (1-5)", "Multiple Choice (Single Select)", "Multiple Choice (Multi-Select)", "Open Text"]
ALLOWED_PRIORITY_LEVELS = ["High", "Medium", "Low"]
MIN_THEMES = 3
MIN_VALID_THEMES = 3
MIN_QUESTIONS = 5
MAX_QUESTIONS = 7
MIN_VALID_QUESTIONS = 4
MIN_PRIORITIZED_ITEMS = 3
MAX_PRIORITIZED_ITEMS = 5
MIN_VALID_PRIORITIZED_ITEMS = 3

OUTPUT_FILENAME = "test_results.json"

# --- Helper Functions ---

def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Loads a JSON file and returns its content or None if error."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def check_structure(data: Any, expected_type: type, key_name: str) -> bool:
    """Checks if data is of the expected type."""
    if not isinstance(data, expected_type):
        print(f"Structure Error: '{key_name}' should be type {expected_type.__name__}, but found {type(data).__name__}.")
        return False
    return True

def check_string(data: Any, key_name: str, allow_empty: bool = False) -> bool:
    """Checks if data is a string and optionally non-empty."""
    if not isinstance(data, str):
        print(f"Type Error: '{key_name}' should be a string, but found {type(data).__name__}.")
        return False
    if not allow_empty and not data.strip():
        print(f"Content Error: '{key_name}' should not be empty.")
        return False
    return True

def check_list(data: Any, key_name: str, min_len: int = 0, max_len: Optional[int] = None, element_type: Optional[type] = None) -> bool:
    """Checks if data is a list with length constraints and optional element type check."""
    if not isinstance(data, list):
        print(f"Type Error: '{key_name}' should be a list, but found {type(data).__name__}.")
        return False
    if len(data) < min_len:
        print(f"Content Error: '{key_name}' list should have at least {min_len} elements, but found {len(data)}.")
        return False
    if max_len is not None and len(data) > max_len:
        print(f"Content Error: '{key_name}' list should have at most {max_len} elements, but found {len(data)}.")
        return False
    if element_type:
        for i, item in enumerate(data):
            if not isinstance(item, element_type):
                print(f"Type Error: Element {i} in '{key_name}' list should be type {element_type.__name__}, but found {type(item).__name__}.")
                return False
    return True

def check_allowed_values(data: Any, key_name: str, allowed: List[str]) -> bool:
    """Checks if data is a string and within the allowed list."""
    if not check_string(data, key_name):
        return False
    if data not in allowed:
        print(f"Value Error: '{key_name}' value '{data}' is not one of the allowed values: {allowed}.")
        return False
    return True

# --- Evaluation Functions ---

def evaluate_overall_structure(submission_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
    """Evaluates the basic structure and metadata of the submission."""
    results = {}
    score = 0
    max_score = 0

    # Check top-level keys
    max_score += 1
    required_keys = ["exam_candidate_id", "assessment_area", "task_1_feedback_analysis",
                     "task_2_survey_design", "task_3_preliminary_prioritization"]
    missing_keys = [key for key in required_keys if key not in submission_data]
    if not missing_keys:
        results["required_top_level_keys_present"] = {"achieved": 1, "max": 1, "passed": True, "comment": "All required keys present."}
        score += 1
    else:
        results["required_top_level_keys_present"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Missing keys: {', '.join(missing_keys)}"}
        # Cannot proceed reliably if top-level keys are missing
        return results, score, max_score

    # Check candidate ID
    max_score += 1
    candidate_id = submission_data.get("exam_candidate_id")
    if check_string(candidate_id, "exam_candidate_id", allow_empty=False) and candidate_id != "YOUR_ID_HERE":
         results["candidate_id_valid"] = {"achieved": 1, "max": 1, "passed": True, "comment": "Candidate ID is a non-empty string."}
         score += 1
    else:
         results["candidate_id_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": "Candidate ID is missing, empty, or placeholder."}

    # Check assessment area
    max_score += 1
    assessment_area = submission_data.get("assessment_area")
    if check_string(assessment_area, "assessment_area") and assessment_area == EXPECTED_ASSESSMENT_AREA:
        results["assessment_area_correct"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Assessment area matches '{EXPECTED_ASSESSMENT_AREA}'."}
        score += 1
    else:
        results["assessment_area_correct"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Assessment area is '{assessment_area}', expected '{EXPECTED_ASSESSMENT_AREA}'."}

    return results, score, max_score


def evaluate_task_1(task_data: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], int, int]:
    """Evaluates Task 1: Feedback Analysis."""
    results = {"checks": {}}
    score = 0
    max_score = 0
    valid_themes_count = 0

    if task_data is None or not isinstance(task_data, dict):
        results["checks"]["task_1_structure_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": "Task 1 data is missing or not a dictionary."}
        max_score += 1 # For structure check
        max_score += 1 # For min themes check
        max_score += 1 # For min valid themes check
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 1. Check structure: identified_themes is a list
    max_score += 1
    themes_list = task_data.get("identified_themes")
    if check_list(themes_list, "identified_themes", element_type=dict):
        results["checks"]["themes_list_is_list"] = {"achieved": 1, "max": 1, "passed": True, "comment": "'identified_themes' is a list of objects."}
        score += 1
    else:
        results["checks"]["themes_list_is_list"] = {"achieved": 0, "max": 1, "passed": False, "comment": "'identified_themes' is missing or not a list of objects."}
        # Cannot proceed if themes_list is invalid
        max_score += 1 # For min themes check
        max_score += 1 # For min valid themes check
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 2. Check minimum number of themes identified
    max_score += 1
    num_themes = len(themes_list)
    if num_themes >= MIN_THEMES:
        results["checks"]["min_themes_identified"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Identified {num_themes} themes (>= {MIN_THEMES})."}
        score += 1
    else:
        results["checks"]["min_themes_identified"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Identified {num_themes} themes (< {MIN_THEMES})."}

    # 3. Check validity of each theme and count valid ones
    theme_details = []
    for i, theme in enumerate(themes_list):
        is_valid = True
        detail = {"index": i, "checks": {}}
        if not isinstance(theme, dict):
            detail["checks"]["is_object"] = False
            is_valid = False
        else:
            detail["checks"]["is_object"] = True
            # Check theme_name
            theme_name = theme.get("theme_name")
            detail["checks"]["theme_name_valid"] = check_string(theme_name, f"theme[{i}].theme_name")
            if not detail["checks"]["theme_name_valid"]: is_valid = False

            # Check supporting_feedback_snippets
            snippets = theme.get("supporting_feedback_snippets")
            # Criteria: "provides at least one correct supporting feedback snippet reference" -> Check list exists and has >= 1 string
            detail["checks"]["snippets_valid"] = check_list(snippets, f"theme[{i}].supporting_feedback_snippets", min_len=1, element_type=str)
            if not detail["checks"]["snippets_valid"]: is_valid = False

            # Check inferred_need_or_pain_point
            need = theme.get("inferred_need_or_pain_point")
            detail["checks"]["need_valid"] = check_string(need, f"theme[{i}].inferred_need_or_pain_point")
            if not detail["checks"]["need_valid"]: is_valid = False

        detail["is_valid"] = is_valid
        if is_valid:
            valid_themes_count += 1
        theme_details.append(detail)

    results["theme_details"] = theme_details

    # 4. Check minimum number of *valid* themes
    max_score += 1
    if valid_themes_count >= MIN_VALID_THEMES:
        results["checks"]["min_valid_themes"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Found {valid_themes_count} valid themes (>= {MIN_VALID_THEMES})."}
        score += 1
    else:
        results["checks"]["min_valid_themes"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Found {valid_themes_count} valid themes (< {MIN_VALID_THEMES})."}

    results["score"] = score
    results["max_score"] = max_score
    return results, score, max_score


def evaluate_task_2(task_data: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], int, int]:
    """Evaluates Task 2: Survey Design."""
    results = {"checks": {}}
    score = 0
    max_score = 0
    valid_questions_count = 0

    if task_data is None or not isinstance(task_data, dict):
        results["checks"]["task_2_structure_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": "Task 2 data is missing or not a dictionary."}
        max_score += 1 # Structure
        max_score += 1 # Goal
        max_score += 1 # Question list
        max_score += 1 # Question count
        max_score += 1 # Min valid questions
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 1. Check survey_goal
    max_score += 1
    survey_goal = task_data.get("survey_goal")
    if check_string(survey_goal, "survey_goal"):
        results["checks"]["survey_goal_valid"] = {"achieved": 1, "max": 1, "passed": True, "comment": "Survey goal is present and non-empty."}
        score += 1
    else:
        results["checks"]["survey_goal_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": "Survey goal is missing or empty."}

    # 2. Check survey_questions is a list
    max_score += 1
    questions_list = task_data.get("survey_questions")
    if check_list(questions_list, "survey_questions", element_type=dict):
        results["checks"]["questions_list_is_list"] = {"achieved": 1, "max": 1, "passed": True, "comment": "'survey_questions' is a list of objects."}
        score += 1
    else:
        results["checks"]["questions_list_is_list"] = {"achieved": 0, "max": 1, "passed": False, "comment": "'survey_questions' is missing or not a list of objects."}
        # Cannot proceed if questions_list is invalid
        max_score += 1 # Question count
        max_score += 1 # Min valid questions
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 3. Check number of questions (5-7)
    max_score += 1
    num_questions = len(questions_list)
    if MIN_QUESTIONS <= num_questions <= MAX_QUESTIONS:
        results["checks"]["question_count_valid"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Number of questions is {num_questions} (between {MIN_QUESTIONS}-{MAX_QUESTIONS})."}
        score += 1
    else:
        results["checks"]["question_count_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Number of questions is {num_questions} (expected {MIN_QUESTIONS}-{MAX_QUESTIONS})."}

    # 4. Check validity of each question and count valid ones
    question_details = []
    for i, question in enumerate(questions_list):
        is_valid = True
        detail = {"index": i, "checks": {}}
        if not isinstance(question, dict):
            detail["checks"]["is_object"] = False
            is_valid = False
        else:
            detail["checks"]["is_object"] = True
            # Check question_number
            q_num = question.get("question_number")
            detail["checks"]["question_number_valid"] = isinstance(q_num, int)
            if not detail["checks"]["question_number_valid"]: is_valid = False

            # Check question_text
            q_text = question.get("question_text")
            detail["checks"]["question_text_valid"] = check_string(q_text, f"question[{i}].question_text")
            if not detail["checks"]["question_text_valid"]: is_valid = False

            # Check question_type
            q_type = question.get("question_type")
            detail["checks"]["question_type_valid"] = check_allowed_values(q_type, f"question[{i}].question_type", ALLOWED_QUESTION_TYPES)
            if not detail["checks"]["question_type_valid"]: is_valid = False

            # Check options based on type
            q_options = question.get("options")
            options_valid = False
            if q_type in ["Multiple Choice (Single Select)", "Multiple Choice (Multi-Select)"]:
                options_valid = check_list(q_options, f"question[{i}].options", min_len=1, element_type=str)
            elif q_type in ["Rating Scale (1-5)", "Open Text"]:
                options_valid = (q_options is None) # Must be Python None, not string "null"
                if not options_valid: print(f"Type Error: question[{i}].options should be null for type '{q_type}', but found {type(q_options).__name__}.")
            else: # Type was invalid or missing
                 options_valid = False # Cannot validate options if type is wrong
            detail["checks"]["options_valid"] = options_valid
            if not options_valid: is_valid = False

            # Check purpose
            q_purpose = question.get("purpose")
            detail["checks"]["purpose_valid"] = check_string(q_purpose, f"question[{i}].purpose")
            if not detail["checks"]["purpose_valid"]: is_valid = False

        detail["is_valid"] = is_valid
        if is_valid:
            valid_questions_count += 1
        question_details.append(detail)

    results["question_details"] = question_details

    # 5. Check minimum number of *valid* questions
    max_score += 1
    if valid_questions_count >= MIN_VALID_QUESTIONS:
        results["checks"]["min_valid_questions"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Found {valid_questions_count} valid questions (>= {MIN_VALID_QUESTIONS})."}
        score += 1
    else:
        results["checks"]["min_valid_questions"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Found {valid_questions_count} valid questions (< {MIN_VALID_QUESTIONS})."}

    results["score"] = score
    results["max_score"] = max_score
    return results, score, max_score


def evaluate_task_3(task_data: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], int, int]:
    """Evaluates Task 3: Preliminary Prioritization."""
    results = {"checks": {}}
    score = 0
    max_score = 0
    valid_items_count = 0

    if task_data is None or not isinstance(task_data, dict):
        results["checks"]["task_3_structure_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": "Task 3 data is missing or not a dictionary."}
        max_score += 1 # Structure
        max_score += 1 # Item list
        max_score += 1 # Item count
        max_score += 1 # Min valid items
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 1. Check prioritized_list is a list
    max_score += 1
    items_list = task_data.get("prioritized_list")
    if check_list(items_list, "prioritized_list", element_type=dict):
        results["checks"]["items_list_is_list"] = {"achieved": 1, "max": 1, "passed": True, "comment": "'prioritized_list' is a list of objects."}
        score += 1
    else:
        results["checks"]["items_list_is_list"] = {"achieved": 0, "max": 1, "passed": False, "comment": "'prioritized_list' is missing or not a list of objects."}
        # Cannot proceed if items_list is invalid
        max_score += 1 # Item count
        max_score += 1 # Min valid items
        results["score"] = score
        results["max_score"] = max_score
        return results, score, max_score

    # 2. Check number of items (3-5)
    max_score += 1
    num_items = len(items_list)
    if MIN_PRIORITIZED_ITEMS <= num_items <= MAX_PRIORITIZED_ITEMS:
        results["checks"]["item_count_valid"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Number of items is {num_items} (between {MIN_PRIORITIZED_ITEMS}-{MAX_PRIORITIZED_ITEMS})."}
        score += 1
    else:
        results["checks"]["item_count_valid"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Number of items is {num_items} (expected {MIN_PRIORITIZED_ITEMS}-{MAX_PRIORITIZED_ITEMS})."}

    # 3. Check validity of each item and count valid ones
    item_details = []
    for i, item in enumerate(items_list):
        is_valid = True
        detail = {"index": i, "checks": {}}
        if not isinstance(item, dict):
            detail["checks"]["is_object"] = False
            is_valid = False
        else:
            detail["checks"]["is_object"] = True
            # Check item_id
            item_id = item.get("item_id")
            detail["checks"]["item_id_valid"] = isinstance(item_id, int)
            if not detail["checks"]["item_id_valid"]: is_valid = False

            # Check requirement_or_focus_area
            req_area = item.get("requirement_or_focus_area")
            detail["checks"]["req_area_valid"] = check_string(req_area, f"item[{i}].requirement_or_focus_area")
            if not detail["checks"]["req_area_valid"]: is_valid = False

            # Check priority
            priority = item.get("priority")
            detail["checks"]["priority_valid"] = check_allowed_values(priority, f"item[{i}].priority", ALLOWED_PRIORITY_LEVELS)
            if not detail["checks"]["priority_valid"]: is_valid = False

            # Check supporting_evidence
            evidence = item.get("supporting_evidence")
            # Criteria: "contains at least one specific reference" -> Check list exists and has >= 1 string
            detail["checks"]["evidence_valid"] = check_list(evidence, f"item[{i}].supporting_evidence", min_len=1, element_type=str)
            if not detail["checks"]["evidence_valid"]: is_valid = False

        detail["is_valid"] = is_valid
        if is_valid:
            valid_items_count += 1
        item_details.append(detail)

    results["item_details"] = item_details

    # 4. Check minimum number of *valid* items
    max_score += 1
    if valid_items_count >= MIN_VALID_PRIORITIZED_ITEMS:
        results["checks"]["min_valid_items"] = {"achieved": 1, "max": 1, "passed": True, "comment": f"Found {valid_items_count} valid items (>= {MIN_VALID_PRIORITIZED_ITEMS})."}
        score += 1
    else:
        results["checks"]["min_valid_items"] = {"achieved": 0, "max": 1, "passed": False, "comment": f"Found {valid_items_count} valid items (< {MIN_VALID_PRIORITIZED_ITEMS})."}

    results["score"] = score
    results["max_score"] = max_score
    return results, score, max_score

# --- Main Execution ---

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file.json> <answer_key_file.json>")
        sys.exit(1)

    submission_filepath = sys.argv[1]
    key_filepath = sys.argv[2] # Key is loaded but not used in this version beyond existence check

    print(f"Evaluating submission: {submission_filepath}")
    print(f"Using key file (for reference): {key_filepath}")

    submission_data = load_json(submission_filepath)
    key_data = load_json(key_filepath) # Load key for potential future use/validation

    if submission_data is None or key_data is None:
        print("Evaluation cannot proceed due to file loading errors.")
        # Create minimal error output
        results = {
            "error": "Failed to load submission or key file.",
            "overall_score": 0,
            "total_achieved_points": 0,
            "total_possible_points": "N/A"
        }
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        sys.exit(1)

    # --- Start Evaluation ---
    evaluation_results = {}
    total_score = 0
    total_max_score = 0

    # Evaluate Overall Structure
    overall_res, overall_sco, overall_max = evaluate_overall_structure(submission_data)
    evaluation_results["overall_structure"] = overall_res
    total_score += overall_sco
    total_max_score += overall_max
    # Stop if basic structure is fundamentally broken
    if not overall_res.get("required_top_level_keys_present", {}).get("passed", False):
         print("Stopping evaluation: Missing required top-level keys in submission.")
         evaluation_results["error"] = "Missing required top-level keys."

    else:
        # Evaluate Task 1
        task1_res, task1_sco, task1_max = evaluate_task_1(submission_data.get("task_1_feedback_analysis"))
        evaluation_results["task_1_evaluation"] = task1_res
        total_score += task1_sco
        total_max_score += task1_max

        # Evaluate Task 2
        task2_res, task2_sco, task2_max = evaluate_task_2(submission_data.get("task_2_survey_design"))
        evaluation_results["task_2_evaluation"] = task2_res
        total_score += task2_sco
        total_max_score += task2_max

        # Evaluate Task 3
        task3_res, task3_sco, task3_max = evaluate_task_3(submission_data.get("task_3_preliminary_prioritization"))
        evaluation_results["task_3_evaluation"] = task3_res
        total_score += task3_sco
        total_max_score += task3_max

    # Calculate Overall Score
    overall_percentage = 0
    if total_max_score > 0:
        overall_percentage = round((total_score / total_max_score) * 100, 2)
    else: # Avoid division by zero if something went very wrong
        overall_percentage = 0

    evaluation_results["overall_score"] = overall_percentage
    evaluation_results["total_achieved_points"] = total_score
    evaluation_results["total_possible_points"] = total_max_score

    # --- Save Results ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=4)
        print(f"Evaluation complete. Results saved to {OUTPUT_FILENAME}")
        print(f"Overall Score: {overall_percentage}% ({total_score}/{total_max_score} points)")
    except Exception as e:
        print(f"Error writing results to {OUTPUT_FILENAME}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()