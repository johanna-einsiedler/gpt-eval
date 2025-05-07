# task_evaluation.py
import json
import argparse
import os
import re
from collections import defaultdict

# --- Constants ---
EXPECTED_EXAM_TYPE = "basic_logistics_pm_tools"
MIN_TASKS = 5
DEADLINE_DAY = 10
VALID_RACI_CODES = {"R", "A", "C", "I", "N/A"}
OUTPUT_FILENAME = "test_results.json"

# --- Helper Functions ---

def load_json(filepath):
    """Loads JSON data from a file."""
    if not os.path.exists(filepath):
        return None, f"Error: File not found at {filepath}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON format in {filepath}. Details: {e}"
    except Exception as e:
        return None, f"Error: Could not read file {filepath}. Details: {e}"

def check_data_type(data, expected_type, key_name):
    """Checks if data is of the expected type."""
    if not isinstance(data, expected_type):
        return f"Invalid type for '{key_name}'. Expected {expected_type.__name__}, got {type(data).__name__}."
    return None

def validate_task_id(task_id):
    """Checks if task_id format is 'T' followed by digits."""
    return re.fullmatch(r"T\d+", task_id) is not None

def parse_predecessors(pred_string):
    """Parses the predecessor string into a list of IDs."""
    if not pred_string:
        return []
    # Handles "T01" or "T01,T02" etc., removes potential whitespace
    return [p.strip() for p in pred_string.split(',') if p.strip()]

# --- Evaluation Functions ---

def evaluate_structure(data):
    """Evaluates the basic structure and types of the submission."""
    results = {"passed": True, "points": 0, "max_points": 15, "details": []}
    required_keys = ["exam_type", "candidate_id", "project_schedule", "responsibility_matrix", "assumptions_made"]
    expected_types = {
        "exam_type": str,
        "candidate_id": str,
        "project_schedule": list,
        "responsibility_matrix": list,
        "assumptions_made": list
    }
    points_per_check = results["max_points"] / (len(required_keys) + 1) # +1 for exam_type value check
    current_points = 0

    # Check presence of required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        results["passed"] = False
        results["details"].append(f"Missing required top-level keys: {', '.join(missing_keys)}")
        # Cannot proceed reliably if structure is wrong
        results["points"] = 0
        return results

    # Check top-level types
    type_errors = []
    for key, expected_type in expected_types.items():
        error = check_data_type(data.get(key), expected_type, key)
        if error:
            type_errors.append(error)
    if type_errors:
        results["passed"] = False
        results["details"].extend(type_errors)
    else:
        current_points += points_per_check * len(required_keys) # Points for structure/types

    # Check exam_type value
    if data.get("exam_type") != EXPECTED_EXAM_TYPE:
        results["passed"] = False
        results["details"].append(f"Incorrect 'exam_type'. Expected '{EXPECTED_EXAM_TYPE}', got '{data.get('exam_type')}'")
    else:
         current_points += points_per_check

    results["points"] = round(current_points)
    if not results["details"]:
         results["details"].append("Basic structure and types are correct.")

    return results

def evaluate_project_schedule(schedule_data):
    """Evaluates the project_schedule section."""
    results = {"passed": True, "points": 0, "max_points": 30, "details": [], "task_map": {}}
    if not isinstance(schedule_data, list):
        results["passed"] = False
        results["details"].append("project_schedule is not a list.")
        return results # Cannot proceed

    points_per_section = results["max_points"] / 6 # 6 sections: min_tasks, deadline, structure/types, task_id_fmt, duration, logic
    current_points = 0
    task_map = {} # Store task info for later checks {task_id: task_object}
    all_task_ids = set()
    max_end_day = 0
    schedule_logic_ok = True

    # 1. Minimum Task Check
    if len(schedule_data) >= MIN_TASKS:
        current_points += points_per_section
        results["details"].append(f"Met minimum task requirement (>= {MIN_TASKS}). Found {len(schedule_data)} tasks.")
    else:
        results["passed"] = False
        results["details"].append(f"FAIL: Did not meet minimum task requirement. Expected >= {MIN_TASKS}, found {len(schedule_data)}.")

    task_structure_ok = True
    task_id_format_ok = True
    duration_ok = True

    for i, task in enumerate(schedule_data):
        task_id = task.get("task_id")
        task_name = task.get("task_name")
        duration = task.get("duration_days")
        predecessors_str = task.get("predecessors")
        start_day = task.get("start_day")
        end_day = task.get("end_day")

        # 2. Task Structure and Type Check (applied to first error found per task)
        if not isinstance(task, dict):
             results["passed"] = False; task_structure_ok = False
             results["details"].append(f"Task {i+1}: Item is not a dictionary.")
             continue # Skip further checks for this item

        required_task_keys = ["task_id", "task_name", "duration_days", "predecessors", "start_day", "end_day"]
        missing_task_keys = [key for key in required_task_keys if key not in task]
        if missing_task_keys:
             results["passed"] = False; task_structure_ok = False
             results["details"].append(f"Task {i+1} (ID: {task_id or 'N/A'}): Missing keys: {', '.join(missing_task_keys)}")

        type_errors = []
        if task_id is not None and not isinstance(task_id, str): type_errors.append("task_id not string")
        if task_name is not None and not isinstance(task_name, str): type_errors.append("task_name not string")
        if duration is not None and not isinstance(duration, int): type_errors.append("duration_days not integer")
        if predecessors_str is not None and not isinstance(predecessors_str, str): type_errors.append("predecessors not string")
        if start_day is not None and not isinstance(start_day, int): type_errors.append("start_day not integer")
        if end_day is not None and not isinstance(end_day, int): type_errors.append("end_day not integer")
        if type_errors:
            results["passed"] = False; task_structure_ok = False
            results["details"].append(f"Task {i+1} (ID: {task_id or 'N/A'}): Type errors: {', '.join(type_errors)}")

        # 3. Task ID Format Check
        if task_id and isinstance(task_id, str):
            if not validate_task_id(task_id):
                results["passed"] = False; task_id_format_ok = False
                results["details"].append(f"Task {i+1}: Invalid task_id format '{task_id}'. Expected 'T' followed by digits.")
            elif task_id in all_task_ids:
                 results["passed"] = False; task_id_format_ok = False
                 results["details"].append(f"Task {i+1}: Duplicate task_id '{task_id}' found.")
            else:
                 all_task_ids.add(task_id)
                 task_map[task_id] = task # Store valid task
        elif task_id is None:
             results["passed"] = False; task_id_format_ok = False
             results["details"].append(f"Task {i+1}: Missing task_id.")


        # 4. Duration Check
        if duration is not None and isinstance(duration, int) and duration < 0:
            results["passed"] = False; duration_ok = False
            results["details"].append(f"Task '{task_id}': Duration cannot be negative ({duration}).")

        # Update max end day for deadline check
        if end_day is not None and isinstance(end_day, int):
            max_end_day = max(max_end_day, end_day)

    # Add points for structure/types if all tasks passed
    if task_structure_ok:
        current_points += points_per_section
        results["details"].append("All schedule tasks have correct structure and types.")
    else:
        results["details"].append("FAIL: One or more schedule tasks have structure/type errors.")

    # Add points for task_id format if all passed
    if task_id_format_ok:
        current_points += points_per_section
        results["details"].append("All task_ids have correct format and are unique.")
    else:
        results["details"].append("FAIL: One or more task_ids have format errors or duplicates.")

    # Add points for duration if all passed
    if duration_ok:
        current_points += points_per_section
        results["details"].append("All task durations are valid (non-negative integers).")
    else:
        results["details"].append("FAIL: One or more tasks have invalid durations.")


    # 5. Deadline Check
    if max_end_day <= DEADLINE_DAY:
        current_points += points_per_section
        results["details"].append(f"Project finishes on Day {max_end_day}, meeting the Day {DEADLINE_DAY} deadline.")
    else:
        results["passed"] = False
        results["details"].append(f"FAIL: Project finishes on Day {max_end_day}, exceeding the Day {DEADLINE_DAY} deadline.")

    # 6. Basic Schedule Logic Check (Start Day vs Predecessor End Day)
    logic_errors = []
    for task_id, task in task_map.items():
        start_day = task.get("start_day")
        predecessors_str = task.get("predecessors", "")
        pred_ids = parse_predecessors(predecessors_str)

        if start_day is None or not isinstance(start_day, int): continue # Skip if start_day invalid

        max_pred_end_day = 0
        valid_preds = True
        for pred_id in pred_ids:
            if pred_id not in task_map:
                logic_errors.append(f"Task '{task_id}': Predecessor '{pred_id}' not found in schedule.")
                valid_preds = False
                break
            pred_task = task_map[pred_id]
            pred_end_day = pred_task.get("end_day")
            if pred_end_day is None or not isinstance(pred_end_day, int):
                 logic_errors.append(f"Task '{task_id}': Predecessor '{pred_id}' has invalid end_day.")
                 valid_preds = False
                 break
            max_pred_end_day = max(max_pred_end_day, pred_end_day)

        if valid_preds and pred_ids: # Only check if predecessors exist and are valid
             # Basic check: Start day must be >= end day of latest predecessor + 1 (assuming work starts next day)
             expected_min_start = max_pred_end_day + 1
             if start_day < expected_min_start:
                 logic_errors.append(f"Task '{task_id}': Starts on Day {start_day} but latest predecessor ('{pred_ids}') ends Day {max_pred_end_day}. Expected start >= Day {expected_min_start}.")
                 schedule_logic_ok = False
        elif valid_preds and not pred_ids: # Task with no predecessors
             if start_day < 1:
                 logic_errors.append(f"Task '{task_id}': No predecessors, but starts before Day 1 ({start_day}).")
                 schedule_logic_ok = False

        # Also check if end_day makes sense with start_day and duration
        duration = task.get("duration_days")
        if start_day is not None and duration is not None and task.get("end_day") is not None:
             if task["end_day"] != (start_day + duration - 1):
                  logic_errors.append(f"Task '{task_id}': End day ({task['end_day']}) doesn't match start ({start_day}) + duration ({duration}) - 1.")
                  schedule_logic_ok = False


    if not logic_errors:
        current_points += points_per_section
        results["details"].append("Basic schedule logic (start day vs predecessor end day, end day calculation) appears consistent.")
    else:
        results["passed"] = False # Logic errors mean failure
        results["details"].append("FAIL: Schedule logic errors found:")
        results["details"].extend([f"  - {err}" for err in logic_errors])

    results["points"] = round(current_points)
    results["task_map"] = task_map # Pass task map for next evaluation step
    return results


def evaluate_responsibility_matrix(matrix_data, task_map):
    """Evaluates the responsibility_matrix section."""
    results = {"passed": True, "points": 0, "max_points": 40, "details": []}
    if not isinstance(matrix_data, list):
        results["passed"] = False
        results["details"].append("responsibility_matrix is not a list.")
        return results # Cannot proceed

    points_per_section = results["max_points"] / 5 # 5 sections: structure/types, valid_codes, single_A, consistency, compliance_presence
    current_points = 0

    required_roles = ["Logistics_Manager", "Procurement_Specialist", "Site_Coordinator", "Transport_Partner", "Volunteer_Team_Lead"]
    required_matrix_keys = ["task_id", "task_name"] + required_roles + ["compliance_check_method"]
    matrix_task_ids = set()

    structure_types_ok = True
    valid_codes_ok = True
    single_a_ok = True
    consistency_ok = True
    compliance_ok = True

    if len(matrix_data) != len(task_map):
         consistency_ok = False
         results["details"].append(f"Warning: Number of tasks in matrix ({len(matrix_data)}) doesn't match schedule ({len(task_map)}).")
         # Don't fail outright, but consistency check below will likely fail.

    for i, item in enumerate(matrix_data):
        task_id = item.get("task_id")
        task_name = item.get("task_name")
        compliance = item.get("compliance_check_method")

        # 1. Structure and Type Check
        if not isinstance(item, dict):
             results["passed"] = False; structure_types_ok = False
             results["details"].append(f"Matrix Item {i+1}: Item is not a dictionary.")
             continue

        missing_keys = [key for key in required_matrix_keys if key not in item]
        if missing_keys:
             results["passed"] = False; structure_types_ok = False
             results["details"].append(f"Matrix Item {i+1} (ID: {task_id or 'N/A'}): Missing keys: {', '.join(missing_keys)}")

        type_errors = []
        for key in required_matrix_keys:
            if key in item and not isinstance(item[key], str):
                type_errors.append(f"'{key}' is not string")
        if type_errors:
            results["passed"] = False; structure_types_ok = False
            results["details"].append(f"Matrix Item {i+1} (ID: {task_id or 'N/A'}): Type errors: {', '.join(type_errors)}")

        if task_id:
            matrix_task_ids.add(task_id)

        # 2. Valid RACI Codes Check
        accountable_count = 0
        raci_errors = []
        for role in required_roles:
            code = item.get(role)
            if code not in VALID_RACI_CODES:
                raci_errors.append(f"Invalid code '{code}' for role '{role}'")
            if code == "A":
                accountable_count += 1
        if raci_errors:
            results["passed"] = False; valid_codes_ok = False
            results["details"].append(f"Matrix Item (ID: {task_id or 'N/A'}): Invalid RACI codes: {', '.join(raci_errors)}")

        # 3. Single Accountable Check
        if accountable_count != 1:
            results["passed"] = False; single_a_ok = False
            results["details"].append(f"Matrix Item (ID: {task_id or 'N/A'}): Expected exactly one 'A' (Accountable), found {accountable_count}.")

        # 4. Consistency Check (Task ID and Name match schedule)
        if task_id not in task_map:
            results["passed"] = False; consistency_ok = False
            results["details"].append(f"Matrix Item (ID: {task_id or 'N/A'}): Task ID '{task_id}' not found in project_schedule.")
        elif task_map[task_id].get("task_name") != task_name:
            results["passed"] = False; consistency_ok = False
            results["details"].append(f"Matrix Item (ID: {task_id}): Task name '{task_name}' does not match schedule name '{task_map[task_id].get('task_name')}'.")

        # 5. Compliance Check Method Presence
        if not compliance or not compliance.strip():
             # Don't fail the whole test, but mark as incomplete and withhold points for this section
             compliance_ok = False
             results["details"].append(f"Matrix Item (ID: {task_id or 'N/A'}): Compliance check method is missing or empty.")


    # Check if all schedule tasks are in the matrix
    missing_matrix_tasks = [tid for tid in task_map if tid not in matrix_task_ids]
    if missing_matrix_tasks:
        results["passed"] = False; consistency_ok = False
        results["details"].append(f"FAIL: Tasks from schedule missing in matrix: {', '.join(missing_matrix_tasks)}")


    # Award points based on section checks
    if structure_types_ok: current_points += points_per_section; results["details"].append("Matrix items have correct structure and types.")
    else: results["details"].append("FAIL: One or more matrix items have structure/type errors.")

    if valid_codes_ok: current_points += points_per_section; results["details"].append("All RACI codes used are valid.")
    else: results["details"].append("FAIL: One or more invalid RACI codes found.")

    if single_a_ok: current_points += points_per_section; results["details"].append("Single 'Accountable' rule followed for all tasks.")
    else: results["details"].append("FAIL: Single 'Accountable' rule violated for one or more tasks.")

    if consistency_ok: current_points += points_per_section; results["details"].append("Task IDs and Names are consistent between schedule and matrix.")
    else: results["details"].append("FAIL: Task ID/Name consistency errors found between schedule and matrix.")

    if compliance_ok: current_points += points_per_section; results["details"].append("Compliance check methods are present for all tasks.")
    else: results["details"].append("FAIL: One or more tasks are missing compliance check methods.")


    results["points"] = round(current_points)
    return results

def evaluate_assumptions(assumptions_data):
    """Evaluates the assumptions_made section."""
    results = {"passed": True, "points": 0, "max_points": 5, "details": []}
    if not isinstance(assumptions_data, list):
        results["passed"] = False
        results["details"].append("assumptions_made is not a list.")
        return results

    all_strings = True
    if not assumptions_data:
         results["details"].append("Warning: No assumptions listed.")
         # No points awarded if empty, but not a hard fail
    else:
        for i, assumption in enumerate(assumptions_data):
            if not isinstance(assumption, str):
                results["passed"] = False # Consider non-string assumption a format fail
                results["details"].append(f"Assumption {i+1}: Item is not a string.")
                all_strings = False
            elif not assumption.strip():
                 results["details"].append(f"Warning: Assumption {i+1} is empty.")
                 # Don't fail, but maybe note quality issue

    if all_strings and assumptions_data: # Award points only if list is present, non-empty and contains strings
        results["points"] = results["max_points"]
        results["details"].append("Assumptions list is present and contains strings.")
    elif not assumptions_data:
         pass # No points, already warned
    else: # Contained non-strings
         results["points"] = 0 # Failed format check

    return results

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate Logistician Basic PM Tools Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("key_file", help="Path to the answer key JSON file (e.g., answer_key.json) - currently unused but required argument.")
    args = parser.parse_args()

    # Load submission data
    submission_data, error = load_json(args.submission_file)
    if error:
        print(error)
        # Create a minimal error result file
        results = {
            "overall_score": 0,
            "evaluation_error": error,
            "checks": {}
        }
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        return

    # Load key data (currently unused in logic but loaded as per requirement)
    key_data, error = load_json(args.key_file)
    if error:
        print(f"Warning: Could not load key file: {error}")
        # Continue evaluation without the key if submission loaded ok

    # --- Run Evaluations ---
    all_results = {}
    total_points = 0
    total_max_points = 0

    # 1. Structure Check
    structure_results = evaluate_structure(submission_data)
    all_results["structure_check"] = structure_results
    total_points += structure_results["points"]
    total_max_points += structure_results["max_points"]

    # Proceed only if basic structure is somewhat valid
    task_map = {}
    if structure_results["passed"] and isinstance(submission_data.get("project_schedule"), list):
        # 2. Project Schedule Check
        schedule_results = evaluate_project_schedule(submission_data.get("project_schedule"))
        all_results["project_schedule_check"] = schedule_results
        total_points += schedule_results["points"]
        total_max_points += schedule_results["max_points"]
        task_map = schedule_results.get("task_map", {}) # Get task map for matrix check

        # 3. Responsibility Matrix Check (depends on schedule check)
        if isinstance(submission_data.get("responsibility_matrix"), list):
             matrix_results = evaluate_responsibility_matrix(submission_data.get("responsibility_matrix"), task_map)
             all_results["responsibility_matrix_check"] = matrix_results
             total_points += matrix_results["points"]
             total_max_points += matrix_results["max_points"]
        else:
             all_results["responsibility_matrix_check"] = {"passed": False, "points": 0, "max_points": 40, "details": ["Responsibility matrix data is missing or not a list."]}
             total_max_points += 40 # Still counts towards max possible points

    else:
        # Add placeholders if schedule couldn't be evaluated
        all_results["project_schedule_check"] = {"passed": False, "points": 0, "max_points": 30, "details": ["Skipped due to structural errors."]}
        all_results["responsibility_matrix_check"] = {"passed": False, "points": 0, "max_points": 40, "details": ["Skipped due to structural errors."]}
        total_max_points += 30 + 40

    # 4. Assumptions Check
    if isinstance(submission_data.get("assumptions_made"), list):
        assumptions_results = evaluate_assumptions(submission_data.get("assumptions_made"))
        all_results["assumptions_check"] = assumptions_results
        total_points += assumptions_results["points"]
        total_max_points += assumptions_results["max_points"]
    else:
        all_results["assumptions_check"] = {"passed": False, "points": 0, "max_points": 5, "details": ["Assumptions data is missing or not a list."]}
        total_max_points += 5


    # --- Calculate Final Score ---
    overall_score_percent = round((total_points / total_max_points) * 100) if total_max_points > 0 else 0

    # --- Prepare Final Output ---
    final_results = {
        "candidate_file": args.submission_file,
        "key_file": args.key_file,
        "overall_score": overall_score_percent,
        "total_points_achieved": total_points,
        "total_max_points": total_max_points,
        "evaluation_details": all_results
    }

    # --- Save Results ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2)
        print(f"Evaluation complete. Results saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error: Could not write results to {OUTPUT_FILENAME}. Details: {e}")

if __name__ == "__main__":
    main()