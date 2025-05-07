import json
import argparse
import sys
import math
import os

# --- Configuration ---
MAX_POINTS_TOTAL = 10
POINTS_STRUCTURE = 1
POINTS_YEAR_1 = 2
POINTS_YEAR_2 = 2
POINTS_CHANGE = 3
POINTS_SUMMARY = 2

# Tolerance for floating point comparisons (accounts for minor rounding differences)
FLOAT_TOLERANCE = 0.015 # Slightly more than 0.01 to allow for intermediate rounding variations

# Expected attendance values for critical failure check
EXPECTED_ATTENDANCE_Y1 = 260
EXPECTED_ATTENDANCE_Y2 = 410
# Significantly wrong attendance values indicating misinterpretation
WRONG_ATTENDANCE_Y1 = 780 # Example: 260 * 3
WRONG_ATTENDANCE_Y2 = 1230 # Example: 410 * 3
ATTENDANCE_TOLERANCE = 5 # Allow slight deviation in case of manual summing error, but catch gross errors

# Keywords for summary evaluation (case-insensitive)
SUMMARY_KEYWORDS_POSITIVE = {
    "cost": ["cost increased", "costs increased", "cost rose", "costs rose"],
    "attendance": ["attendance increased", "attendance grew", "attendance rise"],
    "effectiveness": ["effectiveness improved", "cost per attendance decreased", "cost effective", "efficiency improved", "lower cost per"]
}
SUMMARY_KEYWORDS_NEGATIVE = { # Check if candidate incorrectly states worsening effectiveness
     "effectiveness_worsened": ["effectiveness worsened", "less effective", "cost per attendance increased"]
}

# --- Helper Functions ---

def load_json_file(filepath):
    """Loads a JSON file and returns its content as a Python dictionary."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read file {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)

def compare_floats(val1, val2, tolerance=FLOAT_TOLERANCE):
    """Compares two floats within a given absolute tolerance."""
    if val1 is None or val2 is None:
        return False
    try:
        # Use math.isclose for robust comparison
        return math.isclose(float(val1), float(val2), abs_tol=tolerance)
    except (ValueError, TypeError):
        return False # Cannot compare if values are not numbers

def compare_integers(val1, val2):
    """Compares two integers exactly."""
    if val1 is None or val2 is None:
        return False
    try:
        return int(val1) == int(val2)
    except (ValueError, TypeError):
        return False

def check_attendance_critical_error(candidate_y1_attendance, candidate_y2_attendance):
    """Checks for the critical error of grossly miscalculating attendance."""
    y1_correct = False
    y2_correct = False
    y1_grossly_wrong = False
    y2_grossly_wrong = False

    try:
        cand_y1 = int(candidate_y1_attendance)
        if abs(cand_y1 - EXPECTED_ATTENDANCE_Y1) <= ATTENDANCE_TOLERANCE:
            y1_correct = True
        elif abs(cand_y1 - WRONG_ATTENDANCE_Y1) <= ATTENDANCE_TOLERANCE * 3: # Wider tolerance for the wrong value
             y1_grossly_wrong = True
    except (ValueError, TypeError, AttributeError):
        pass # Handled by regular scoring

    try:
        cand_y2 = int(candidate_y2_attendance)
        if abs(cand_y2 - EXPECTED_ATTENDANCE_Y2) <= ATTENDANCE_TOLERANCE:
            y2_correct = True
        elif abs(cand_y2 - WRONG_ATTENDANCE_Y2) <= ATTENDANCE_TOLERANCE * 3:
             y2_grossly_wrong = True
    except (ValueError, TypeError, AttributeError):
        pass # Handled by regular scoring

    # Critical failure if *either* year shows the specific gross miscalculation pattern
    if y1_grossly_wrong or y2_grossly_wrong:
        return True, "Critical Failure: Attendance calculation indicates fundamental misinterpretation of data structure (likely triple counting)."

    # Return False if no critical error, even if numbers are simply incorrect but not the specific wrong pattern
    return False, "Attendance calculation seems structurally correct or has non-critical errors."


def evaluate_summary(candidate_summary, key_summary):
    """Evaluates the summary based on keywords and objectivity."""
    score = 0
    feedback = []
    max_score = POINTS_SUMMARY

    if not isinstance(candidate_summary, str) or not candidate_summary.strip():
        feedback.append("Summary is missing or not a string.")
        return score, feedback, max_score

    summary_lower = candidate_summary.lower()

    # 1. Check for correct trend identification (improved effectiveness)
    effectiveness_improved = any(kw in summary_lower for kw in SUMMARY_KEYWORDS_POSITIVE["effectiveness"])
    effectiveness_worsened = any(kw in summary_lower for kw in SUMMARY_KEYWORDS_NEGATIVE["effectiveness_worsened"])

    if effectiveness_improved and not effectiveness_worsened:
        score += 1
        feedback.append("Correctly identified improved cost-effectiveness trend.")
    elif effectiveness_worsened:
        feedback.append("Incorrectly identified cost-effectiveness trend (stated it worsened).")
    else:
        feedback.append("Did not clearly state the overall cost-effectiveness trend.")

    # 2. Check for mention of contributing factors (cost & attendance changes) and objectivity
    cost_mentioned = any(kw in summary_lower for kw in SUMMARY_KEYWORDS_POSITIVE["cost"])
    attendance_mentioned = any(kw in summary_lower for kw in SUMMARY_KEYWORDS_POSITIVE["attendance"])

    # Basic check for objectivity (avoiding speculative words - very basic check)
    speculative_words = ["should", "recommend", "could improve", "suggest", "maybe because"]
    is_objective = not any(word in summary_lower for word in speculative_words)

    if cost_mentioned and attendance_mentioned and is_objective:
        score += 1
        feedback.append("Correctly mentioned contributing factors (cost/attendance changes) objectively.")
    elif not is_objective:
        feedback.append("Summary may contain speculation or recommendations, not just objective findings.")
    else:
        missing = []
        if not cost_mentioned: missing.append("cost changes")
        if not attendance_mentioned: missing.append("attendance changes")
        if missing:
             feedback.append(f"Did not clearly mention contributing factors ({' and '.join(missing)}).")

    # Check conciseness (simple check based on sentence count - approximate)
    num_sentences = summary_lower.count('.') + summary_lower.count('!') + summary_lower.count('?')
    if num_sentences == 0 and len(summary_lower) > 10: # Handle run-on sentences
        num_sentences = 1
    if not (1 <= num_sentences <= 2):
         feedback.append(f"Summary length ({num_sentences} sentences) is outside the recommended 1-2 sentences.")
         # Optional: Penalize slightly? For now, just feedback.

    return score, feedback, max_score

def get_nested_value(data_dict, keys, default=None):
    """Safely retrieves a nested value from a dictionary."""
    current = data_dict
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError, IndexError):
        return default

# --- Main Evaluation Logic ---

def evaluate_submission(submission_data, answer_key_data):
    """Compares submission data against the answer key and calculates score."""
    results = {
        "overall_score": 0.0,
        "max_points_total": MAX_POINTS_TOTAL,
        "score_details": {},
        "feedback": [],
        "critical_failure": False,
        "critical_failure_reason": None
    }
    total_score = 0

    # --- 1. JSON Structure and Basic Keys (Implicitly checked by loading, add explicit check) ---
    structure_score = 0
    structure_feedback = []
    required_top_keys = ["program_name", "analysis_period", "year_1_metrics", "year_2_metrics", "year_over_year_change_percent", "evaluation_summary"]
    required_y1_keys = ["total_cost", "total_attendance", "cost_per_attendance"]
    required_y2_keys = ["total_cost", "total_attendance", "cost_per_attendance"]
    required_change_keys = ["total_cost_change_percent", "total_attendance_change_percent", "cost_per_attendance_change_percent"]

    missing_keys = []
    if not all(key in submission_data for key in required_top_keys):
        missing_keys.extend([k for k in required_top_keys if k not in submission_data])
    if not all(key in get_nested_value(submission_data, ["year_1_metrics"], {}) for key in required_y1_keys):
         missing_keys.append("year_1_metrics keys")
    if not all(key in get_nested_value(submission_data, ["year_2_metrics"], {}) for key in required_y2_keys):
         missing_keys.append("year_2_metrics keys")
    if not all(key in get_nested_value(submission_data, ["year_over_year_change_percent"], {}) for key in required_change_keys):
         missing_keys.append("year_over_year_change_percent keys")

    if not missing_keys:
        structure_score = POINTS_STRUCTURE
        structure_feedback.append("JSON structure is valid and all required keys are present.")
    else:
        structure_feedback.append(f"JSON structure is invalid or missing required keys: {', '.join(missing_keys)}.")

    total_score += structure_score
    results["score_details"]["structure"] = {
        "score": structure_score,
        "max_score": POINTS_STRUCTURE,
        "feedback": structure_feedback
    }

    # --- Critical Failure Check: Attendance ---
    cand_y1_att = get_nested_value(submission_data, ["year_1_metrics", "total_attendance"])
    cand_y2_att = get_nested_value(submission_data, ["year_2_metrics", "total_attendance"])
    is_critical_failure, critical_reason = check_attendance_critical_error(cand_y1_att, cand_y2_att)

    if is_critical_failure:
        results["critical_failure"] = True
        results["critical_failure_reason"] = critical_reason
        results["feedback"].append(f"CRITICAL FAILURE DETECTED: {critical_reason}. Score capped.")
        # Score is effectively 0 due to critical failure, but we can still evaluate other parts for feedback
        # Set total score to 0 at the end if critical failure is true.

    # --- 2. Year 1 Metrics ---
    y1_score = 0
    y1_feedback = []
    y1_metrics_sub = get_nested_value(submission_data, ["year_1_metrics"], {})
    y1_metrics_key = get_nested_value(answer_key_data, ["year_1_metrics"], {})
    y1_max_score = POINTS_YEAR_1

    # Attendance (1 point of Y1) - check even if critical failure for feedback
    y1_att_sub = get_nested_value(y1_metrics_sub, ["total_attendance"])
    y1_att_key = get_nested_value(y1_metrics_key, ["total_attendance"])
    y1_att_correct = compare_integers(y1_att_sub, y1_att_key)
    if y1_att_correct:
        y1_score += 1
        y1_feedback.append("Year 1 Total Attendance: Correct.")
    else:
        y1_feedback.append(f"Year 1 Total Attendance: Incorrect (Submitted: {y1_att_sub}, Expected: {y1_att_key}).")
        if is_critical_failure and "Year 1" in critical_reason: # Add specific feedback if this caused critical failure
             y1_feedback.append(f"-> This value triggered/contributed to the critical failure: {critical_reason}")


    # Costs (1 point of Y1)
    y1_cost_sub = get_nested_value(y1_metrics_sub, ["total_cost"])
    y1_cost_key = get_nested_value(y1_metrics_key, ["total_cost"])
    y1_cpa_sub = get_nested_value(y1_metrics_sub, ["cost_per_attendance"])
    y1_cpa_key = get_nested_value(y1_metrics_key, ["cost_per_attendance"])

    y1_cost_correct = compare_floats(y1_cost_sub, y1_cost_key)
    y1_cpa_correct = compare_floats(y1_cpa_sub, y1_cpa_key)

    if y1_cost_correct and y1_cpa_correct:
        y1_score += 1
        y1_feedback.append("Year 1 Total Cost & Cost Per Attendance: Correct.")
    else:
        if not y1_cost_correct:
            y1_feedback.append(f"Year 1 Total Cost: Incorrect (Submitted: {y1_cost_sub}, Expected: {y1_cost_key}).")
        if not y1_cpa_correct:
            y1_feedback.append(f"Year 1 Cost Per Attendance: Incorrect (Submitted: {y1_cpa_sub}, Expected: {y1_cpa_key}).")

    total_score += y1_score
    results["score_details"]["year_1_metrics"] = {
        "score": y1_score,
        "max_score": y1_max_score,
        "feedback": y1_feedback
    }

    # --- 3. Year 2 Metrics ---
    y2_score = 0
    y2_feedback = []
    y2_metrics_sub = get_nested_value(submission_data, ["year_2_metrics"], {})
    y2_metrics_key = get_nested_value(answer_key_data, ["year_2_metrics"], {})
    y2_max_score = POINTS_YEAR_2

    # Attendance (1 point of Y2)
    y2_att_sub = get_nested_value(y2_metrics_sub, ["total_attendance"])
    y2_att_key = get_nested_value(y2_metrics_key, ["total_attendance"])
    y2_att_correct = compare_integers(y2_att_sub, y2_att_key)
    if y2_att_correct:
        y2_score += 1
        y2_feedback.append("Year 2 Total Attendance: Correct.")
    else:
        y2_feedback.append(f"Year 2 Total Attendance: Incorrect (Submitted: {y2_att_sub}, Expected: {y2_att_key}).")
        if is_critical_failure and "Year 2" in critical_reason: # Add specific feedback if this caused critical failure
             y2_feedback.append(f"-> This value triggered/contributed to the critical failure: {critical_reason}")


    # Costs (1 point of Y2)
    y2_cost_sub = get_nested_value(y2_metrics_sub, ["total_cost"])
    y2_cost_key = get_nested_value(y2_metrics_key, ["total_cost"])
    y2_cpa_sub = get_nested_value(y2_metrics_sub, ["cost_per_attendance"])
    y2_cpa_key = get_nested_value(y2_metrics_key, ["cost_per_attendance"])

    y2_cost_correct = compare_floats(y2_cost_sub, y2_cost_key)
    y2_cpa_correct = compare_floats(y2_cpa_sub, y2_cpa_key)

    if y2_cost_correct and y2_cpa_correct:
        y2_score += 1
        y2_feedback.append("Year 2 Total Cost & Cost Per Attendance: Correct.")
    else:
        if not y2_cost_correct:
            y2_feedback.append(f"Year 2 Total Cost: Incorrect (Submitted: {y2_cost_sub}, Expected: {y2_cost_key}).")
        if not y2_cpa_correct:
            y2_feedback.append(f"Year 2 Cost Per Attendance: Incorrect (Submitted: {y2_cpa_sub}, Expected: {y2_cpa_key}).")

    total_score += y2_score
    results["score_details"]["year_2_metrics"] = {
        "score": y2_score,
        "max_score": y2_max_score,
        "feedback": y2_feedback
    }

    # --- 4. Year-over-Year Change Percent ---
    change_score = 0
    change_feedback = []
    change_metrics_sub = get_nested_value(submission_data, ["year_over_year_change_percent"], {})
    change_metrics_key = get_nested_value(answer_key_data, ["year_over_year_change_percent"], {})
    change_max_score = POINTS_CHANGE

    fields_to_check = [
        ("total_cost_change_percent", "Total Cost Change %"),
        ("total_attendance_change_percent", "Total Attendance Change %"),
        ("cost_per_attendance_change_percent", "Cost Per Attendance Change %")
    ]

    for key, name in fields_to_check:
        sub_val = get_nested_value(change_metrics_sub, [key])
        key_val = get_nested_value(change_metrics_key, [key])
        if compare_floats(sub_val, key_val):
            change_score += 1
            change_feedback.append(f"{name}: Correct.")
        else:
            change_feedback.append(f"{name}: Incorrect (Submitted: {sub_val}, Expected: {key_val}).")

    total_score += change_score
    results["score_details"]["year_over_year_change"] = {
        "score": change_score,
        "max_score": change_max_score,
        "feedback": change_feedback
    }

    # --- 5. Evaluation Summary ---
    summary_sub = get_nested_value(submission_data, ["evaluation_summary"])
    summary_key = get_nested_value(answer_key_data, ["evaluation_summary"]) # Key summary not strictly needed for eval, but good practice
    summary_score, summary_feedback_list, summary_max_score = evaluate_summary(summary_sub, summary_key)

    # Check for critical misinterpretation in summary
    summary_lower = str(summary_sub).lower()
    effectiveness_worsened = any(kw in summary_lower for kw in SUMMARY_KEYWORDS_NEGATIVE["effectiveness_worsened"])
    if effectiveness_worsened:
         results["critical_failure"] = True # Also flag critical if summary contradicts data fundamentally
         critical_reason_summary = "Critical Failure: Evaluation summary incorrectly states cost-effectiveness worsened, contradicting the data."
         results["critical_failure_reason"] = critical_reason_summary if not results["critical_failure_reason"] else results["critical_failure_reason"] + "; " + critical_reason_summary
         results["feedback"].append(f"CRITICAL FAILURE DETECTED: {critical_reason_summary}. Score capped.")
         summary_score = 0 # Override summary score if critically wrong


    total_score += summary_score
    results["score_details"]["evaluation_summary"] = {
        "score": summary_score,
        "max_score": summary_max_score,
        "feedback": summary_feedback_list
    }

    # --- Final Score Calculation ---
    if results["critical_failure"]:
        final_score_points = 0
        results["feedback"].append("Overall score set to 0 due to critical failure.")
    else:
        # Ensure score doesn't exceed max points due to potential logic overlaps
        final_score_points = min(total_score, MAX_POINTS_TOTAL)


    results["final_score_points"] = final_score_points
    results["overall_score"] = round((final_score_points / MAX_POINTS_TOTAL) * 100, 2) if MAX_POINTS_TOTAL > 0 else 0

    return results

# --- Script Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Fitness and Wellness Coordinator practical exam submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")
    parser.add_argument("-o", "--output", default="test_results.json", help="Path to save the evaluation results JSON file (default: test_results.json)")

    args = parser.parse_args()

    print(f"Loading submission file: {args.submission_file}")
    submission_data = load_json_file(args.submission_file)

    print(f"Loading answer key file: {args.answer_key_file}")
    answer_key_data = load_json_file(args.answer_key_file)

    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_data, answer_key_data)

    # Add input filenames to results for context
    evaluation_results["input_files"] = {
        "submission": os.path.basename(args.submission_file),
        "answer_key": os.path.basename(args.answer_key_file)
    }

    output_file = args.output
    print(f"Saving evaluation results to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2)
        print("Evaluation complete.")
        # Optionally print summary to console
        print(f"\n--- Evaluation Summary ---")
        print(f"Overall Score: {evaluation_results['overall_score']}% ({evaluation_results['final_score_points']}/{evaluation_results['max_points_total']} points)")
        if evaluation_results['critical_failure']:
            print(f"Critical Failure Detected: {evaluation_results['critical_failure_reason']}")
        print(f"Detailed results saved in {output_file}")
        print("------------------------")

    except Exception as e:
        print(f"Error: Could not write results file {output_file}. Details: {e}", file=sys.stderr)
        sys.exit(1)