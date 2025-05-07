import json
import argparse
import os
from datetime import datetime

# --- Configuration ---

# Define points allocation based on evaluation criteria
POINTS_ALLOCATION = {
    "json_validity_structure": 15,
    "scope_in_accuracy": 15,
    "scope_out_accuracy": 10,
    "approach_logic": 10,
    "prioritization_logic": 15,
    "schedule_date_format_window": 10,
    "schedule_activity_feasibility": 15,
    "risks_assumptions_relevance": 10,
}
TOTAL_POSSIBLE_POINTS = sum(POINTS_ALLOCATION.values())

# Define QA window dates from Project Brief
QA_START_DATE_STR = "2024-07-30"
QA_END_DATE_STR = "2024-08-09"
QA_START_DATE = datetime.strptime(QA_START_DATE_STR, "%Y-%m-%d").date()
QA_END_DATE = datetime.strptime(QA_END_DATE_STR, "%Y-%m-%d").date()

# Define core requirements/expectations derived from the key
EXPECTED_RG_IDS = {"RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06"}
EXPECTED_IN_SCOPE_KEYWORDS = {"chrome", "firefox", "usability"} # Lowercase
EXPECTED_OUT_SCOPE_KEYWORDS = {"mobile", "authentication", "performance", "safari", "edge", "ie", "migration"} # Lowercase
EXPECTED_APPROACH_FOCUS = {"functional testing", "browser compatibility testing"} # Lowercase
EXPECTED_SCHEDULE_ACTIVITIES = {"design", "plan", "functional", "execution", "browser", "compatibility", "regression", "buffer", "retest", "report"} # Lowercase
MIN_ASSUMPTIONS = 2
MIN_RISKS = 2

# --- Helper Functions ---

def load_json_file(filepath):
    """Loads a JSON file safely."""
    if not os.path.exists(filepath):
        return None, f"Error: File not found at {filepath}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON format in {filepath}. Details: {e}"
    except Exception as e:
        return None, f"Error: Could not read file {filepath}. Details: {e}"

def check_keys(data, required_keys, section_name):
    """Checks if all required keys are present in a dictionary."""
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys in section '{section_name}': {', '.join(missing_keys)}"
    return True, None

def validate_date_str(date_str):
    """Validates date string format YYYY-MM-DD and returns date object or None."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def extract_rg_ids(scope_list):
    """Extracts RG-XX IDs from a list of strings."""
    ids = set()
    if isinstance(scope_list, list):
        for item in scope_list:
            if isinstance(item, str) and item.strip().startswith("RG-"):
                # Extract the first word assuming it's the ID like "RG-01:"
                parts = item.strip().split(":", 1)
                potential_id = parts[0].strip()
                # Basic check if it looks like an RG ID
                if potential_id.startswith("RG-") and potential_id[3:].isdigit():
                     ids.add(potential_id)
    return ids

# --- Evaluation Functions ---

def evaluate_json_structure(candidate_data, key_data):
    """Evaluates the basic structure and validity (already checked by loading)."""
    score = 0
    details = []
    max_points = POINTS_ALLOCATION["json_validity_structure"]

    # Check top-level keys
    required_top_keys = key_data.keys()
    struct_ok, msg = check_keys(candidate_data, required_top_keys, "root")
    if not struct_ok:
        details.append(f"FAIL: {msg}. Cannot proceed with detailed evaluation.")
        return 0, details

    # Check basic types (simple check)
    valid_types = True
    for key, value in key_data.items():
        if key not in candidate_data: continue # Already handled above
        if type(candidate_data[key]) != type(value):
             # Allow candidate_id to be different type if needed, focus on structure
             if key != 'candidate_id':
                 details.append(f"FAIL: Type mismatch for key '{key}'. Expected {type(value).__name__}, got {type(candidate_data[key]).__name__}.")
                 valid_types = False

    if valid_types:
        score = max_points
        details.append(f"PASS: Basic JSON structure and types appear correct ({score}/{max_points} points).")
    else:
        details.append(f"FAIL: Structural or type issues detected ({score}/{max_points} points).")

    return score, details


def evaluate_scope(candidate_scope, key_scope):
    """Evaluates the 'testing_scope' section."""
    score = 0
    details = []
    max_points_in = POINTS_ALLOCATION["scope_in_accuracy"]
    max_points_out = POINTS_ALLOCATION["scope_out_accuracy"]
    total_max = max_points_in + max_points_out

    # Default to empty lists if keys are missing or not lists
    candidate_in = candidate_scope.get("in_scope", []) if isinstance(candidate_scope, dict) else []
    candidate_out = candidate_scope.get("out_of_scope", []) if isinstance(candidate_scope, dict) else []
    if not isinstance(candidate_in, list): candidate_in = []
    if not isinstance(candidate_out, list): candidate_out = []

    key_in = key_scope.get("in_scope", [])
    key_out = key_scope.get("out_of_scope", [])

    # --- In Scope Evaluation ---
    in_score = 0
    # 1. Check RG IDs
    candidate_rg_ids = extract_rg_ids(candidate_in)
    missing_rg_ids = EXPECTED_RG_IDS - candidate_rg_ids
    correct_rg_ids_count = len(EXPECTED_RG_IDS) - len(missing_rg_ids)
    rg_id_points = (correct_rg_ids_count / len(EXPECTED_RG_IDS)) * (max_points_in * 0.6) # 60% weight for RG IDs
    in_score += rg_id_points
    if not missing_rg_ids:
        details.append(f"PASS (In-Scope): All {len(EXPECTED_RG_IDS)} required RG IDs found.")
    else:
        details.append(f"PARTIAL (In-Scope): Found {correct_rg_ids_count}/{len(EXPECTED_RG_IDS)} required RG IDs. Missing: {', '.join(missing_rg_ids)}.")

    # 2. Check other keywords (browsers, usability)
    in_scope_text = " ".join(candidate_in).lower() if candidate_in else ""
    found_keywords_count = sum(1 for keyword in EXPECTED_IN_SCOPE_KEYWORDS if keyword in in_scope_text)
    keyword_points = (found_keywords_count / len(EXPECTED_IN_SCOPE_KEYWORDS)) * (max_points_in * 0.4) # 40% weight for keywords
    in_score += keyword_points
    details.append(f"INFO (In-Scope): Found {found_keywords_count}/{len(EXPECTED_IN_SCOPE_KEYWORDS)} expected keywords (e.g., browsers, usability).")

    # --- Out of Scope Evaluation ---
    out_score = 0
    out_scope_text = " ".join(candidate_out).lower() if candidate_out else ""
    found_out_keywords = {keyword for keyword in EXPECTED_OUT_SCOPE_KEYWORDS if keyword in out_scope_text}
    found_out_count = len(found_out_keywords)
    # Simple scoring: points proportional to number of distinct keywords found, max points if >= 4 found
    min_expected_out_keywords = 4
    out_score = min(1.0, found_out_count / min_expected_out_keywords) * max_points_out
    if found_out_count >= min_expected_out_keywords:
         details.append(f"PASS (Out-Scope): Found {found_out_count} relevant out-of-scope items (e.g., mobile, auth, perf).")
    else:
         details.append(f"PARTIAL (Out-Scope): Found {found_out_count} relevant out-of-scope items. Expected at least {min_expected_out_keywords}.")

    score = round(in_score + out_score)
    details.append(f"Scope Score: {score}/{total_max} points.")
    return score, details

def evaluate_approach(candidate_approach, key_approach):
    """Evaluates the 'test_approach_summary' section."""
    score = 0
    details = []
    max_points = POINTS_ALLOCATION["approach_logic"]

    candidate_focus = candidate_approach.get("primary_focus", []) if isinstance(candidate_approach, dict) else []
    candidate_methodology = candidate_approach.get("methodology", "") if isinstance(candidate_approach, dict) else ""
    if not isinstance(candidate_focus, list): candidate_focus = []
    if not isinstance(candidate_methodology, str): candidate_methodology = ""

    # Check primary focus
    focus_score = 0
    focus_text = " ".join(item.lower() for item in candidate_focus if isinstance(item, str))
    found_focus_count = sum(1 for keyword in EXPECTED_APPROACH_FOCUS if keyword in focus_text)
    focus_score = (found_focus_count / len(EXPECTED_APPROACH_FOCUS)) * (max_points * 0.7) # 70% weight
    details.append(f"INFO (Approach Focus): Found {found_focus_count}/{len(EXPECTED_APPROACH_FOCUS)} expected focus areas.")

    # Check methodology
    methodology_score = 0
    if candidate_methodology and ("manual" in candidate_methodology.lower() or "requirements" in candidate_methodology.lower()):
        methodology_score = max_points * 0.3 # 30% weight
        details.append("PASS (Approach Methodology): Plausible methodology described.")
    else:
        details.append("FAIL (Approach Methodology): Methodology description missing or not clearly relevant.")

    score = round(focus_score + methodology_score)
    details.append(f"Approach Score: {score}/{max_points} points.")
    return score, details

def evaluate_prioritization(candidate_prio, key_prio):
    """Evaluates the 'prioritized_requirements' section."""
    score = 0
    details = []
    max_points = POINTS_ALLOCATION["prioritization_logic"]

    if not isinstance(candidate_prio, list):
        details.append("FAIL (Prioritization): 'prioritized_requirements' is not a list.")
        return 0, details

    candidate_rg_ids_in_prio = set()
    valid_format = True
    priorities = []
    candidate_order = []

    for item in candidate_prio:
        if not isinstance(item, dict):
            valid_format = False; details.append("FAIL (Prioritization): Item is not a dictionary."); break
        if "requirement_id" not in item or "priority" not in item:
            valid_format = False; details.append("FAIL (Prioritization): Item missing 'requirement_id' or 'priority'."); break
        if not isinstance(item["requirement_id"], str) or not item["requirement_id"].startswith("RG-"):
            valid_format = False; details.append(f"FAIL (Prioritization): Invalid requirement_id format: {item['requirement_id']}."); break
        if not isinstance(item["priority"], int):
            valid_format = False; details.append(f"FAIL (Prioritization): Priority for {item['requirement_id']} is not an integer."); break

        candidate_rg_ids_in_prio.add(item["requirement_id"])
        priorities.append(item["priority"])
        candidate_order.append(item["requirement_id"])

    if not valid_format:
        return 0, details # Stop if basic format is wrong

    # Check if all expected RG IDs are present
    missing_ids = EXPECTED_RG_IDS - candidate_rg_ids_in_prio
    extra_ids = candidate_rg_ids_in_prio - EXPECTED_RG_IDS
    coverage_score = 0
    if not missing_ids and not extra_ids:
        coverage_score = max_points * 0.5 # 50% for correct coverage
        details.append(f"PASS (Prioritization): All {len(EXPECTED_RG_IDS)} expected requirements listed.")
    else:
        details.append(f"FAIL (Prioritization): Incorrect set of requirements listed. Missing: {missing_ids}, Extra: {extra_ids}.")
        # No points for order if coverage is wrong
        details.append(f"Prioritization Score: {round(coverage_score)}/{max_points} points.")
        return round(coverage_score), details

    # Check if priorities are sequential (basic check: sorted list == range(1, N+1))
    if sorted(priorities) != list(range(1, len(EXPECTED_RG_IDS) + 1)):
         details.append("WARN (Prioritization): Priority numbers are not sequential integers starting from 1.")
         # Allow non-sequential but penalize slightly if needed, or just warn for basic

    # Check logical order (simple check: top 2 match key's top 2?)
    order_score = 0
    key_order = [item["requirement_id"] for item in key_prio]
    if candidate_order and key_order and candidate_order[0] == key_order[0]:
        order_score += max_points * 0.25 # 25% for correct #1
        details.append("PASS (Prioritization): Top priority requirement matches key.")
        if len(candidate_order) > 1 and len(key_order) > 1 and candidate_order[1] == key_order[1]:
             order_score += max_points * 0.25 # 25% for correct #2
             details.append("PASS (Prioritization): Second priority requirement matches key.")
        else:
             details.append("FAIL (Prioritization): Second priority requirement does not match key.")
    else:
        details.append("FAIL (Prioritization): Top priority requirement does not match key.")

    score = round(coverage_score + order_score)
    details.append(f"Prioritization Score: {score}/{max_points} points.")
    return score, details


def evaluate_schedule(candidate_schedule):
    """Evaluates the 'test_schedule' section."""
    score_format_window = 0
    score_activity = 0
    details = []
    max_points_format = POINTS_ALLOCATION["schedule_date_format_window"]
    max_points_activity = POINTS_ALLOCATION["schedule_activity_feasibility"]
    total_max = max_points_format + max_points_activity

    if not isinstance(candidate_schedule, list) or not candidate_schedule:
        details.append("FAIL (Schedule): 'test_schedule' is not a non-empty list.")
        return 0, 0, details # Return tuple for two scores

    all_dates_valid_format = True
    all_dates_in_window = True
    all_start_before_end = True
    activity_texts = []

    for item in candidate_schedule:
        if not isinstance(item, dict):
            details.append("FAIL (Schedule): Activity item is not a dictionary."); all_dates_valid_format=False; break
        if "activity" not in item or "start" not in item or "end" not in item:
            details.append("FAIL (Schedule): Activity item missing 'activity', 'start', or 'end' key."); all_dates_valid_format=False; break
        if not isinstance(item["activity"], str) or not item["activity"]:
             details.append("FAIL (Schedule): Activity description is not a non-empty string."); # Don't fail format for this
        activity_texts.append(item["activity"].lower())

        start_date_str = item["start"]
        end_date_str = item["end"]
        start_date = validate_date_str(start_date_str)
        end_date = validate_date_str(end_date_str)

        if start_date is None or end_date is None:
            details.append(f"FAIL (Schedule): Invalid date format for activity '{item['activity']}'. Start: '{start_date_str}', End: '{end_date_str}'. Expected YYYY-MM-DD.")
            all_dates_valid_format = False
            # Don't check window/order if format is wrong for this item
            continue

        if not (QA_START_DATE <= start_date <= QA_END_DATE and QA_START_DATE <= end_date <= QA_END_DATE):
            details.append(f"FAIL (Schedule): Dates for activity '{item['activity']}' ({start_date_str} to {end_date_str}) fall outside the allowed QA window ({QA_START_DATE_STR} to {QA_END_DATE_STR}).")
            all_dates_in_window = False

        if start_date > end_date:
            details.append(f"FAIL (Schedule): Start date ({start_date_str}) is after end date ({end_date_str}) for activity '{item['activity']}'.")
            all_start_before_end = False

    # Score for date format, window, and start <= end
    if all_dates_valid_format and all_dates_in_window and all_start_before_end:
        score_format_window = max_points_format
        details.append(f"PASS (Schedule Dates): All dates have correct format, fall within QA window, and start <= end ({score_format_window}/{max_points_format} points).")
    else:
        details.append(f"FAIL (Schedule Dates): Issues found with date formats, window constraints, or start/end order ({score_format_window}/{max_points_format} points).")


    # Score for activity coverage and feasibility (basic check)
    schedule_text = " ".join(activity_texts)
    found_activity_keywords = {keyword for keyword in EXPECTED_SCHEDULE_ACTIVITIES if keyword in schedule_text}
    coverage_ratio = len(found_activity_keywords) / 6 # Check for at least 6 distinct keyword types
    score_activity = min(1.0, coverage_ratio) * max_points_activity
    details.append(f"INFO (Schedule Activities): Found {len(found_activity_keywords)} types of expected activities mentioned (e.g., design, execution, browser, regression, buffer, report).")
    details.append(f"Schedule Activity Score: {round(score_activity)}/{max_points_activity} points.")

    return round(score_format_window), round(score_activity), details


def evaluate_risks_assumptions(candidate_ra):
    """Evaluates the 'risks_and_assumptions' section."""
    score = 0
    details = []
    max_points = POINTS_ALLOCATION["risks_assumptions_relevance"]

    candidate_assumptions = candidate_ra.get("assumptions", []) if isinstance(candidate_ra, dict) else []
    candidate_risks = candidate_ra.get("risks", []) if isinstance(candidate_ra, dict) else []
    if not isinstance(candidate_assumptions, list): candidate_assumptions = []
    if not isinstance(candidate_risks, list): candidate_risks = []

    # Filter out empty strings
    valid_assumptions = [a for a in candidate_assumptions if isinstance(a, str) and a.strip()]
    valid_risks = [r for r in candidate_risks if isinstance(r, str) and r.strip()]

    assumptions_ok = len(valid_assumptions) >= MIN_ASSUMPTIONS
    risks_ok = len(valid_risks) >= MIN_RISKS

    if assumptions_ok:
        score += max_points * 0.5
        details.append(f"PASS (Assumptions): Found {len(valid_assumptions)} valid assumptions (minimum {MIN_ASSUMPTIONS} required).")
    else:
        details.append(f"FAIL (Assumptions): Found only {len(valid_assumptions)} valid assumptions (minimum {MIN_ASSUMPTIONS} required).")

    if risks_ok:
        score += max_points * 0.5
        details.append(f"PASS (Risks): Found {len(valid_risks)} valid risks (minimum {MIN_RISKS} required).")
    else:
        details.append(f"FAIL (Risks): Found only {len(valid_risks)} valid risks (minimum {MIN_RISKS} required).")

    score = round(score)
    details.append(f"Risks & Assumptions Score: {score}/{max_points} points.")
    return score, details

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate QA Planning Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    results = {
        "evaluation_details": {},
        "overall_score": 0.0,
        "total_score_achieved": 0,
        "total_score_possible": TOTAL_POSSIBLE_POINTS
    }
    total_score = 0

    # Load files
    candidate_data, error = load_json_file(args.submission_file)
    if error:
        results["evaluation_details"]["file_load_error"] = error
        print(error)
        # Write partial results and exit
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        return

    key_data, error = load_json_file(args.key_file)
    if error:
        # This is an evaluator setup error, print and exit differently
        print(f"CRITICAL ERROR: Could not load answer key file '{args.key_file}'. {error}")
        # Optionally write an error marker to results if desired
        results["evaluation_details"]["key_load_error"] = f"CRITICAL ERROR: Could not load answer key file '{args.key_file}'. {error}"
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        return

    # --- Start Evaluation ---

    # 1. JSON Validity and Structure
    score, details = evaluate_json_structure(candidate_data, key_data)
    total_score += score
    results["evaluation_details"]["json_validity_structure"] = {"score": score, "max_score": POINTS_ALLOCATION["json_validity_structure"], "details": details}
    # If structure is fundamentally flawed, we might stop here or proceed cautiously
    if score < POINTS_ALLOCATION["json_validity_structure"]:
        print("Warning: Basic JSON structure issues detected. Subsequent evaluations might be affected.")
        # Decide whether to stop or continue based on severity - for now, continue

    # Helper to safely get sections, defaulting to None if keys missing
    def get_section(data, key):
        return data.get(key) if isinstance(data, dict) else None

    # 2. Scope
    candidate_scope_section = get_section(candidate_data, "testing_scope")
    key_scope_section = get_section(key_data, "testing_scope")
    if candidate_scope_section and key_scope_section:
         score, details = evaluate_scope(candidate_scope_section, key_scope_section)
         total_score += score
         results["evaluation_details"]["scope"] = {"score": score, "max_score": POINTS_ALLOCATION["scope_in_accuracy"] + POINTS_ALLOCATION["scope_out_accuracy"], "details": details}
    else:
         results["evaluation_details"]["scope"] = {"score": 0, "max_score": POINTS_ALLOCATION["scope_in_accuracy"] + POINTS_ALLOCATION["scope_out_accuracy"], "details": ["FAIL: 'testing_scope' section missing or invalid in submission or key."]}


    # 3. Approach
    candidate_approach_section = get_section(candidate_data, "test_approach_summary")
    key_approach_section = get_section(key_data, "test_approach_summary")
    if candidate_approach_section and key_approach_section:
        score, details = evaluate_approach(candidate_approach_section, key_approach_section)
        total_score += score
        results["evaluation_details"]["approach"] = {"score": score, "max_score": POINTS_ALLOCATION["approach_logic"], "details": details}
    else:
         results["evaluation_details"]["approach"] = {"score": 0, "max_score": POINTS_ALLOCATION["approach_logic"], "details": ["FAIL: 'test_approach_summary' section missing or invalid in submission or key."]}

    # 4. Prioritization
    candidate_prio_section = get_section(candidate_data, "prioritized_requirements")
    key_prio_section = get_section(key_data, "prioritized_requirements")
    if candidate_prio_section is not None and key_prio_section is not None: # Check for None explicitly as empty list is valid but maybe not intended
        score, details = evaluate_prioritization(candidate_prio_section, key_prio_section)
        total_score += score
        results["evaluation_details"]["prioritization"] = {"score": score, "max_score": POINTS_ALLOCATION["prioritization_logic"], "details": details}
    else:
         results["evaluation_details"]["prioritization"] = {"score": 0, "max_score": POINTS_ALLOCATION["prioritization_logic"], "details": ["FAIL: 'prioritized_requirements' section missing or invalid in submission or key."]}


    # 5. Schedule
    candidate_schedule_section = get_section(candidate_data, "test_schedule")
    if candidate_schedule_section is not None: # Check for None explicitly
        score_format, score_activity, details = evaluate_schedule(candidate_schedule_section)
        total_score += score_format + score_activity
        results["evaluation_details"]["schedule"] = {"score": score_format + score_activity, "max_score": POINTS_ALLOCATION["schedule_date_format_window"] + POINTS_ALLOCATION["schedule_activity_feasibility"], "details": details}
    else:
         results["evaluation_details"]["schedule"] = {"score": 0, "max_score": POINTS_ALLOCATION["schedule_date_format_window"] + POINTS_ALLOCATION["schedule_activity_feasibility"], "details": ["FAIL: 'test_schedule' section missing or invalid in submission."]}


    # 6. Risks & Assumptions
    candidate_ra_section = get_section(candidate_data, "risks_and_assumptions")
    if candidate_ra_section:
        score, details = evaluate_risks_assumptions(candidate_ra_section)
        total_score += score
        results["evaluation_details"]["risks_assumptions"] = {"score": score, "max_score": POINTS_ALLOCATION["risks_assumptions_relevance"], "details": details}
    else:
         results["evaluation_details"]["risks_assumptions"] = {"score": 0, "max_score": POINTS_ALLOCATION["risks_assumptions_relevance"], "details": ["FAIL: 'risks_and_assumptions' section missing or invalid in submission."]}


    # --- Final Calculation ---
    results["total_score_achieved"] = total_score
    if TOTAL_POSSIBLE_POINTS > 0:
        results["overall_score"] = round((total_score / TOTAL_POSSIBLE_POINTS) * 100, 2)
    else:
        results["overall_score"] = 0.0

    # --- Save Results ---
    try:
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Evaluation complete. Results saved to test_results.json")
        print(f"Overall Score: {results['overall_score']}% ({total_score}/{TOTAL_POSSIBLE_POINTS})")
    except Exception as e:
        print(f"Error: Could not write results to file. Details: {e}")
        # Print results to console as fallback
        # print("\n--- Evaluation Results ---")
        # print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()