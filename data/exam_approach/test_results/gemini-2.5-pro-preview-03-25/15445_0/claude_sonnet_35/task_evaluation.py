import json
import argparse
import math
import os

# Define the paths to the fields that need to be scored
# Using tuples to represent the path of keys
SCORED_FIELDS_PATHS = [
    ("task_1_initial_calculations", "original_total_q1_opex"),
    ("task_1_initial_calculations", "original_q1_net_operating_income"),
    ("task_2_budget_adjustments", "well_maintenance", "original_budget"),
    ("task_2_budget_adjustments", "well_maintenance", "adjusted_budget"),
    ("task_2_budget_adjustments", "well_maintenance", "variance"),
    ("task_2_budget_adjustments", "electricity_sales_revenue", "original_budget"),
    ("task_2_budget_adjustments", "electricity_sales_revenue", "adjusted_budget"),
    ("task_2_budget_adjustments", "electricity_sales_revenue", "variance"),
    ("task_2_budget_adjustments", "plant_consumables", "original_budget"),
    ("task_2_budget_adjustments", "plant_consumables", "adjusted_budget"),
    ("task_2_budget_adjustments", "plant_consumables", "variance"),
    ("task_2_budget_adjustments", "revised_total_q1_opex"),
    ("task_2_budget_adjustments", "revised_q1_net_operating_income"),
]

TOTAL_POSSIBLE_POINTS = len(SCORED_FIELDS_PATHS)
# Passing criteria from <evaluation_information>: "at least 9 out of these 13 numerical fields correct"
PASSING_SCORE_THRESHOLD_POINTS = 9

def get_nested_value(data_dict, path_keys, default=None):
    """
    Safely retrieves a value from a nested dictionary.
    :param data_dict: The dictionary to search.
    :param path_keys: A tuple or list of keys representing the path.
    :param default: The value to return if the path is not found or an intermediate key is missing.
    :return: The value at the nested path or the default value.
    """
    current_level = data_dict
    for key in path_keys:
        if isinstance(current_level, dict) and key in current_level:
            current_level = current_level[key]
        else:
            return default
    return current_level

def compare_values(val1, val2, tolerance=1e-9):
    """
    Compares two numerical values, typically monetary, expecting precision to two decimal places.
    Rounds both values to 2 decimal places before comparing with absolute tolerance.
    """
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        # For monetary values, comparison after rounding to 2 decimal places is robust.
        # math.isclose with rel_tol=0 and a small abs_tol checks for "exactness" after rounding.
        return math.isclose(round(val1, 2), round(val2, 2), rel_tol=0, abs_tol=tolerance)
    # If not both numbers, use direct equality (e.g., for strings, booleans, or if one is None)
    return val1 == val2

def initialize_detailed_scores_structure(results_dict, paths):
    """
    Initializes the nested structure for detailed_scores in the results dictionary.
    """
    for path in paths:
        current_level_results = results_dict["detailed_scores"]
        for key_part in path[:-1]: # Iterate up to the second to last key
            if key_part not in current_level_results:
                current_level_results[key_part] = {}
            current_level_results = current_level_results[key_part]
        # The last key in the path is where the score details will go
        current_level_results[path[-1]] = {
            "expected": None,
            "submitted": None,
            "correct": False,
            "points": 0
        }

def check_submission_structure(submission_data, answer_key_data, errors_list):
    """
    Performs basic structural checks on the submission data.
    """
    if submission_data.get("exam_part") != answer_key_data.get("exam_part"):
        errors_list.append(
            f"Exam part mismatch. Submitted: '{submission_data.get('exam_part', 'N/A')}', "
            f"Expected: '{answer_key_data.get('exam_part', 'N/A')}'."
        )

    required_top_level_keys = ["candidate_id", "exam_part", "task_1_initial_calculations", "task_2_budget_adjustments"]
    for key in required_top_level_keys:
        if key not in submission_data:
            errors_list.append(f"Submission is missing required top-level key: '{key}'.")
            # If a top-level key is missing, further checks depending on it might not be possible or meaningful
            if key == "task_1_initial_calculations" or key == "task_2_budget_adjustments":
                return # Stop further structural checks for these missing sections

    # Check structure of task_1_initial_calculations
    task1_data = submission_data.get("task_1_initial_calculations")
    if isinstance(task1_data, dict):
        required_task1_keys = ["original_total_q1_opex", "original_q1_net_operating_income"]
        for key in required_task1_keys:
            if key not in task1_data:
                 errors_list.append(f"Submission is missing required key in 'task_1_initial_calculations': '{key}'.")
    elif "task_1_initial_calculations" in submission_data : # Key exists but is not a dict
        errors_list.append(f"'task_1_initial_calculations' in submission is not a dictionary, found {type(task1_data).__name__}.")

    # Check structure of task_2_budget_adjustments
    task2_data = submission_data.get("task_2_budget_adjustments")
    if isinstance(task2_data, dict):
        required_task2_top_keys = ["well_maintenance", "electricity_sales_revenue", "plant_consumables", "revised_total_q1_opex", "revised_q1_net_operating_income"]
        for key in required_task2_top_keys:
            if key not in task2_data:
                errors_list.append(f"Submission is missing required key in 'task_2_budget_adjustments': '{key}'.")
        
        sub_objects_task2 = {
            "well_maintenance": ["original_budget", "adjusted_budget", "variance"],
            "electricity_sales_revenue": ["original_budget", "adjusted_budget", "variance"],
            "plant_consumables": ["original_budget", "adjusted_budget", "variance"]
        }
        for parent_key, child_keys_list in sub_objects_task2.items():
            parent_data = task2_data.get(parent_key)
            if isinstance(parent_data, dict):
                for child_key in child_keys_list:
                    if child_key not in parent_data:
                        errors_list.append(f"Submission is missing required key in 'task_2_budget_adjustments.{parent_key}': '{child_key}'.")
            elif parent_key in task2_data: # Parent key exists but is not a dict
                 errors_list.append(f"'task_2_budget_adjustments.{parent_key}' in submission is not a dictionary, found {type(parent_data).__name__}.")
            # If parent_key itself is missing, it's caught by required_task2_top_keys check
    elif "task_2_budget_adjustments" in submission_data: # Key exists but is not a dict
        errors_list.append(f"'task_2_budget_adjustments' in submission is not a dictionary, found {type(task2_data).__name__}.")


def evaluate_submission(submission_data, answer_key_data):
    """
    Evaluates the candidate's submission against the answer key.
    """
    results = {
        "candidate_id_submission": submission_data.get("candidate_id", "N/A"),
        "candidate_id_key": answer_key_data.get("candidate_id", "N/A"),
        "exam_part_submission": submission_data.get("exam_part", "N/A"),
        "exam_part_key": answer_key_data.get("exam_part", "N/A"),
        "overall_score": 0.0,
        "total_possible_points": TOTAL_POSSIBLE_POINTS,
        "total_achieved_points": 0,
        "detailed_scores": {},
        "evaluation_summary": {},
        "errors": []
    }

    initialize_detailed_scores_structure(results, SCORED_FIELDS_PATHS)
    check_submission_structure(submission_data, answer_key_data, results["errors"])
        
    achieved_points = 0

    for field_path in SCORED_FIELDS_PATHS:
        expected_value = get_nested_value(answer_key_data, field_path)
        submitted_value = get_nested_value(submission_data, field_path, default="<MISSING>") # Use a distinct default

        # Navigate to the correct place in results["detailed_scores"] to store this field's result
        current_result_dict_level = results["detailed_scores"]
        for key in field_path[:-1]:
            current_result_dict_level = current_result_dict_level[key]
        field_result_dict = current_result_dict_level[field_path[-1]]

        field_result_dict["expected"] = expected_value
        field_result_dict["submitted"] = submitted_value if submitted_value != "<MISSING>" else None
        
        if expected_value is None: # Should not happen if answer key is complete and correct
            results["errors"].append(f"Critical Error: Missing expected value in answer key for field: {'.'.join(field_path)}")
            field_result_dict["correct"] = False
            field_result_dict["points"] = 0
            continue # Cannot score this field

        if submitted_value == "<MISSING>":
            # This error is already noted by structural checks if the key was expected.
            # If it's a field that was optional and not submitted, this is fine.
            # However, all SCORED_FIELDS_PATHS are mandatory.
            # The structural check should have added an error. Here we just mark as incorrect.
            field_result_dict["correct"] = False
            field_result_dict["points"] = 0
            continue
        
        # Type check: ensure submitted value is a number if expected is a number
        # All scored fields in this exam are numbers.
        if not isinstance(submitted_value, (int, float)):
            results["errors"].append(
                f"Type mismatch for field: {'.'.join(field_path)}. "
                f"Expected a number, got {type(submitted_value).__name__} (value: {submitted_value})."
            )
            field_result_dict["correct"] = False
            field_result_dict["points"] = 0
            continue
        
        is_correct = compare_values(submitted_value, expected_value)
        field_result_dict["correct"] = is_correct
        if is_correct:
            field_result_dict["points"] = 1
            achieved_points += 1
        else:
            field_result_dict["points"] = 0

    results["total_achieved_points"] = achieved_points
    if TOTAL_POSSIBLE_POINTS > 0:
        results["overall_score"] = round((achieved_points / TOTAL_POSSIBLE_POINTS) * 100, 2)
    else:
        results["overall_score"] = 0.0

    # Pass/Fail status
    if achieved_points >= PASSING_SCORE_THRESHOLD_POINTS:
        results["evaluation_summary"]["pass_status"] = "PASS"
        results["evaluation_summary"]["message"] = (
            f"Candidate passed with {achieved_points}/{TOTAL_POSSIBLE_POINTS} correct fields. "
            f"Minimum required: {PASSING_SCORE_THRESHOLD_POINTS}."
        )
    else:
        results["evaluation_summary"]["pass_status"] = "FAIL"
        results["evaluation_summary"]["message"] = (
            f"Candidate failed. Achieved {achieved_points}/{TOTAL_POSSIBLE_POINTS} correct fields. "
            f"Minimum required: {PASSING_SCORE_THRESHOLD_POINTS}."
        )
    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluate a candidate's JSON submission against an answer key.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    output_filename = "test_results.json"
    
    # Initialize results with error state in case of early exit
    # This base structure will be written if critical errors occur before full evaluation.
    base_results = {
        "candidate_id_submission": "N/A",
        "candidate_id_key": "N/A",
        "exam_part_submission": "N/A",
        "exam_part_key": "N/A",
        "overall_score": 0.0,
        "total_possible_points": TOTAL_POSSIBLE_POINTS,
        "total_achieved_points": 0,
        "detailed_scores": {},
        "evaluation_summary": {"pass_status": "ERROR", "message": "Evaluation could not be completed due to file/JSON errors."},
        "errors": []
    }
    initialize_detailed_scores_structure(base_results, SCORED_FIELDS_PATHS)


    try:
        with open(args.submission_file, 'r', encoding='utf-8') as f:
            submission_data = json.load(f)
        base_results["candidate_id_submission"] = submission_data.get("candidate_id", "N/A")
        base_results["exam_part_submission"] = submission_data.get("exam_part", "N/A")
    except FileNotFoundError:
        error_msg = f"Submission file not found: {args.submission_file}"
        print(f"Error: {error_msg}")
        base_results["errors"].append(error_msg)
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            json.dump(base_results, f_out, indent=2)
        return
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in submission file: {args.submission_file}. Details: {e}"
        print(f"Error: {error_msg}")
        base_results["errors"].append(error_msg)
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            json.dump(base_results, f_out, indent=2)
        return

    try:
        with open(args.answer_key_file, 'r', encoding='utf-8') as f:
            answer_key_data = json.load(f)
        base_results["candidate_id_key"] = answer_key_data.get("candidate_id", "N/A")
        base_results["exam_part_key"] = answer_key_data.get("exam_part", "N/A")
    except FileNotFoundError:
        error_msg = f"Answer key file not found: {args.answer_key_file}"
        print(f"Error: {error_msg}")
        base_results["errors"].append(error_msg)
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            json.dump(base_results, f_out, indent=2)
        return
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in answer key file: {args.answer_key_file}. Details: {e}"
        print(f"Error: {error_msg}")
        base_results["errors"].append(error_msg)
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            json.dump(base_results, f_out, indent=2)
        return

    # Perform evaluation
    evaluation_results = evaluate_submission(submission_data, answer_key_data)

    # Save results
    try:
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            json.dump(evaluation_results, f_out, indent=2)
        print(f"Evaluation complete. Results saved to {output_filename}")
    except IOError as e:
        print(f"Error: Could not write results to {output_filename}. Details: {e}")
        # Optionally, print results to console if file write fails
        # print(json.dumps(evaluation_results, indent=2))

if __name__ == "__main__":
    main()