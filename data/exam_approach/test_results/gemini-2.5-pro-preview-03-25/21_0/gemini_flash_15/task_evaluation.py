import json
import argparse
import sys
import os
from collections import Counter

# --- Normalization Functions ---

def normalize_string(text):
    """Lowercase and strip whitespace for comparison."""
    if isinstance(text, str):
        return text.lower().strip()
    return text # Return as is if not a string (e.g., for numbers)

def normalize_location(loc):
    """Normalize location strings for comparison (lowercase, strip, handle 'column x')."""
    if not isinstance(loc, str):
        return loc
    loc = loc.lower().strip()
    # Simple normalization for column references
    if loc.startswith("column"):
        parts = loc.split()
        if len(parts) == 2:
            return f"column {parts[1]}" # Ensure consistent spacing
    # Remove spaces within cell references like 'E 10' -> 'e10'
    loc = ''.join(loc.split())
    return loc

def normalize_finding(finding):
    """Normalize a single report finding object."""
    if not isinstance(finding, dict):
        return None # Invalid finding format
    return {
        "location": normalize_location(finding.get("location")),
        "error_type": normalize_string(finding.get("error_type")),
        # Description comparison is tricky, normalize basic aspects
        "description": normalize_string(finding.get("description"))
    }

def normalize_unscheduled(req):
    """Normalize an unscheduled request object."""
    if not isinstance(req, dict):
        return None
    return {
        # Normalize the request identifier slightly (lowercase, strip)
        "request": normalize_string(req.get("request")),
        # Normalize the reason (lowercase, strip)
        "reason": normalize_string(req.get("reason"))
    }

# --- Comparison Functions ---

def compare_findings(submitted_finding, key_finding):
    """
    Compares a normalized submitted finding against a normalized key finding.
    Allows for some flexibility in description.
    """
    if not submitted_finding or not key_finding:
        return False

    # Strict check for location and error type
    if submitted_finding["location"] != key_finding["location"]:
        return False
    if submitted_finding["error_type"] != key_finding["error_type"]:
        return False

    # Basic check for description (exact match after normalization)
    # More sophisticated checks (keywords, similarity) could be added here if needed.
    if submitted_finding["description"] != key_finding["description"]:
        # Allow minor variations if location and type match (e.g., slight rephrasing)
        # For this basic script, we'll stick to near-exact match after normalization.
        # Consider a more lenient check if required in future versions.
        # For now, require description match too for simplicity and strictness.
         return False # Sticking to stricter check for now

    return True

def compare_unscheduled_lists(submitted_list, key_list):
    """
    Compares lists of normalized unscheduled requests. Order doesn't matter.
    Returns True if the lists contain the same items.
    """
    if not isinstance(submitted_list, list) or not isinstance(key_list, list):
        return False # Invalid format

    if len(submitted_list) != len(key_list):
        return False

    # Convert lists to comparable format (e.g., tuples of sorted items)
    submitted_set = set(tuple(sorted(d.items())) for d in submitted_list if d)
    key_set = set(tuple(sorted(d.items())) for d in key_list if d)

    return submitted_set == key_set

# --- Main Evaluation Logic ---

def evaluate_submission(submission_data, key_data):
    """Evaluates the candidate's submission against the answer key."""
    results = {
        "overall_score": 0.0,
        "pass_status": False,
        "criteria_met": {
            "valid_json_structure": False,
            "report_findings_quantity_correct": False,
            "report_findings_accuracy_met": False,
            "schedule_meeting_count_correct": False,
            "schedule_unscheduled_requests_match": False,
        },
        "details": {
            "report_review": {
                "submitted_findings_count": 0,
                "correct_findings_count": 0,
                "max_correct_findings": 0,
                "matched_findings": [],
                "missed_findings": [],
                "extra_findings": [] # Findings submitted but not in key
            },
            "schedule_preparation": {
                "submitted_total_meetings": None,
                "key_total_meetings": None,
                "meeting_count_match": False,
                "submitted_unscheduled_count": 0,
                "key_unscheduled_count": 0,
                "unscheduled_list_match": False,
                "submitted_unscheduled_list": [],
                "key_unscheduled_list": []
            }
        },
        "scoring": {
            "report_findings_points": 0,
            "schedule_meeting_count_points": 0,
            "schedule_unscheduled_match_points": 0,
            "total_achieved_points": 0,
            "max_possible_points": 0
        },
        "errors": []
    }

    # --- Basic Structure Validation ---
    if not isinstance(submission_data, dict) or \
       "report_review_findings" not in submission_data or \
       "schedule_preparation" not in submission_data or \
       not isinstance(submission_data["report_review_findings"], list) or \
       not isinstance(submission_data["schedule_preparation"], dict):
        results["errors"].append("Invalid basic JSON structure in submission.")
        # Cannot proceed further
        return results
    results["criteria_met"]["valid_json_structure"] = True

    # --- Task 1: Report Review Evaluation ---
    submitted_findings_raw = submission_data.get("report_review_findings", [])
    key_findings_raw = key_data.get("report_review_findings", [])

    # Normalize findings
    submitted_findings = [normalize_finding(f) for f in submitted_findings_raw if f]
    key_findings = [normalize_finding(f) for f in key_findings_raw if f]

    # Filter out any invalid format findings after normalization
    submitted_findings = [f for f in submitted_findings if f]
    key_findings = [f for f in key_findings if f]

    results["details"]["report_review"]["submitted_findings_count"] = len(submitted_findings)
    results["details"]["report_review"]["max_correct_findings"] = len(key_findings)
    results["scoring"]["max_possible_points"] += len(key_findings) # 1 point per finding

    # Check quantity requirement (exactly 5 for this specific exam)
    expected_findings_count = 5 # As per instructions
    if len(submitted_findings_raw) == expected_findings_count: # Check raw count before filtering invalid formats
         results["criteria_met"]["report_findings_quantity_correct"] = True
    else:
         results["errors"].append(f"Expected exactly {expected_findings_count} findings in 'report_review_findings', found {len(submitted_findings_raw)}.")


    # Compare findings
    correct_count = 0
    matched_key_indices = set()
    submitted_matched_indices = set()

    for i, sub_f in enumerate(submitted_findings):
        match_found = False
        for j, key_f in enumerate(key_findings):
            if j not in matched_key_indices: # Check against unmatched key findings
                # Using a simple comparison for this basic version
                # Location and Type must match exactly (after normalization)
                # Description must match exactly (after normalization)
                if sub_f['location'] == key_f['location'] and \
                   sub_f['error_type'] == key_f['error_type'] and \
                   sub_f['description'] == key_f['description']:
                    correct_count += 1
                    matched_key_indices.add(j)
                    submitted_matched_indices.add(i)
                    results["details"]["report_review"]["matched_findings"].append({
                        "submitted": submission_data["report_review_findings"][i], # Original format
                        "key": key_data["report_review_findings"][j] # Original format
                    })
                    match_found = True
                    break # Move to the next submitted finding
        if not match_found:
             # Store the finding submitted by the candidate that didn't match any key finding
             if i not in submitted_matched_indices:
                 results["details"]["report_review"]["extra_findings"].append(submission_data["report_review_findings"][i])


    results["details"]["report_review"]["correct_findings_count"] = correct_count
    results["scoring"]["report_findings_points"] = correct_count

    # Identify missed findings
    for j, key_f_orig in enumerate(key_data["report_review_findings"]):
        if j not in matched_key_indices:
            results["details"]["report_review"]["missed_findings"].append(key_f_orig)

    # Check accuracy requirement (at least 4 out of 5 correct)
    min_correct_findings = 4 # As per instructions
    if correct_count >= min_correct_findings:
        results["criteria_met"]["report_findings_accuracy_met"] = True

    # --- Task 2: Schedule Preparation Evaluation ---
    submitted_schedule = submission_data.get("schedule_preparation", {})
    key_schedule = key_data.get("schedule_preparation", {})

    # Max points for schedule JSON part: 1 for count, 1 for unscheduled list match
    results["scoring"]["max_possible_points"] += 2

    # Compare total meetings scheduled
    sub_total = submitted_schedule.get("total_meetings_scheduled")
    key_total = key_schedule.get("total_meetings_scheduled")
    results["details"]["schedule_preparation"]["submitted_total_meetings"] = sub_total
    results["details"]["schedule_preparation"]["key_total_meetings"] = key_total
    if isinstance(sub_total, int) and sub_total == key_total:
        results["details"]["schedule_preparation"]["meeting_count_match"] = True
        results["criteria_met"]["schedule_meeting_count_correct"] = True
        results["scoring"]["schedule_meeting_count_points"] = 1
    else:
        results["errors"].append(f"Scheduled meeting count mismatch. Submitted: {sub_total}, Expected: {key_total}")

    # Compare unscheduled requests
    sub_unscheduled_raw = submitted_schedule.get("unscheduled_requests", [])
    key_unscheduled_raw = key_schedule.get("unscheduled_requests", [])

    # Normalize lists
    sub_unscheduled = [normalize_unscheduled(req) for req in sub_unscheduled_raw if req]
    key_unscheduled = [normalize_unscheduled(req) for req in key_unscheduled_raw if req]
    sub_unscheduled = [req for req in sub_unscheduled if req] # Filter None
    key_unscheduled = [req for req in key_unscheduled if req] # Filter None


    results["details"]["schedule_preparation"]["submitted_unscheduled_count"] = len(sub_unscheduled)
    results["details"]["schedule_preparation"]["key_unscheduled_count"] = len(key_unscheduled)
    results["details"]["schedule_preparation"]["submitted_unscheduled_list"] = sub_unscheduled_raw # Store original
    results["details"]["schedule_preparation"]["key_unscheduled_list"] = key_unscheduled_raw # Store original


    if compare_unscheduled_lists(sub_unscheduled, key_unscheduled):
        results["details"]["schedule_preparation"]["unscheduled_list_match"] = True
        results["criteria_met"]["schedule_unscheduled_requests_match"] = True
        results["scoring"]["schedule_unscheduled_match_points"] = 1
    else:
         results["errors"].append("Unscheduled requests list mismatch.")
         # Provide more detail on mismatch if needed (e.g., items only in submitted, items only in key)


    # --- Calculate Final Score and Pass Status ---
    results["scoring"]["total_achieved_points"] = (
        results["scoring"]["report_findings_points"] +
        results["scoring"]["schedule_meeting_count_points"] +
        results["scoring"]["schedule_unscheduled_match_points"]
    )

    max_points = results["scoring"]["max_possible_points"]
    if max_points > 0:
        results["overall_score"] = round((results["scoring"]["total_achieved_points"] / max_points) * 100, 2)
    else:
        results["overall_score"] = 0.0

    # Determine overall pass status based on criteria
    # Must meet ALL mandatory requirements and BOTH task-specific minimums
    results["pass_status"] = (
        results["criteria_met"]["valid_json_structure"] and
        results["criteria_met"]["report_findings_quantity_correct"] and # Explicitly check quantity
        results["criteria_met"]["report_findings_accuracy_met"] and
        results["criteria_met"]["schedule_meeting_count_correct"] and
        results["criteria_met"]["schedule_unscheduled_requests_match"]
    )

    return results

# --- Main Script Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Administrative Services Manager Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")
    parser.add_argument("-o", "--output", default="test_results.json", help="Path to save the evaluation results JSON file (default: test_results.json)")

    args = parser.parse_args()

    # --- Load Files ---
    try:
        with open(args.submission_file, 'r', encoding='utf-8') as f:
            submission_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Submission file not found at '{args.submission_file}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in submission file '{args.submission_file}': {e}", file=sys.stderr)
        # Still try to produce a results file indicating the JSON error
        results = {
            "overall_score": 0.0,
            "pass_status": False,
            "criteria_met": {"valid_json_structure": False},
            "details": {},
            "scoring": {},
            "errors": [f"Invalid JSON in submission file: {e}"]
        }
        with open(args.output, 'w', encoding='utf-8') as f_out:
            json.dump(results, f_out, indent=2)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading submission file '{args.submission_file}': {e}", file=sys.stderr)
        sys.exit(1)


    try:
        with open(args.key_file, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file not found at '{args.key_file}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in answer key file '{args.key_file}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading answer key file '{args.key_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Perform Evaluation ---
    evaluation_results = evaluate_submission(submission_data, key_data)

    # --- Save Results ---
    try:
        with open(args.output, 'w', encoding='utf-8') as f_out:
            json.dump(evaluation_results, f_out, indent=2)
        print(f"Evaluation complete. Results saved to '{args.output}'")
    except IOError as e:
        print(f"Error: Could not write results to file '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while saving results: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)