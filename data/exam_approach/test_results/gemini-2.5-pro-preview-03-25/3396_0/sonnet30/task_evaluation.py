import json
import sys
import os
import argparse
from collections import defaultdict

# --- Scoring Configuration ---
# Adjust points based on the importance of each check, aiming for a total max_points of 100.
POINTS_CONFIG = {
    "valid_json_structure": 5,
    "budget_constraint": {
        "original_total_correct": 5,
        "adjusted_total_correct": 10, # Compared to key's expected adjusted total
        "constraint_met_true": 15,    # Candidate explicitly states constraint is met
        "internal_consistency": 5,   # Candidate's adjusted total matches sum of their adjusted lines
    },
    "analysis_summary": {
        "points_per_correct_impact": 5, # 4 impacts total = 20 points max
    },
    "proposed_adjustments": {
        "travel_reallocation_correct": 15, # Specific check for the critical reallocation rule
        "points_per_correct_other_adjustment": 3, # 4 other adjustments * 3 = 12 points max
        "points_per_correct_adjusted_budget": 1, # 5 adjusted budgets * 1 = 5 points max
        "points_per_correct_original_budget": 1, # 5 original budgets * 1 = 5 points max
        "includes_only_adjusted_categories": 3,
    },
    "calculation_notes_format": 0 # Check format but no points assigned as per instructions
}
# Calculate total max points dynamically
MAX_POINTS = (
    POINTS_CONFIG["valid_json_structure"] +
    POINTS_CONFIG["budget_constraint"]["original_total_correct"] +
    POINTS_CONFIG["budget_constraint"]["adjusted_total_correct"] +
    POINTS_CONFIG["budget_constraint"]["constraint_met_true"] +
    POINTS_CONFIG["budget_constraint"]["internal_consistency"] +
    (POINTS_CONFIG["analysis_summary"]["points_per_correct_impact"] * 4) + # Assuming 4 impacts in key
    POINTS_CONFIG["proposed_adjustments"]["travel_reallocation_correct"] +
    (POINTS_CONFIG["proposed_adjustments"]["points_per_correct_other_adjustment"] * 4) + # Assuming 4 'other' adjustments
    (POINTS_CONFIG["proposed_adjustments"]["points_per_correct_adjusted_budget"] * 5) + # Assuming 5 total adjustments
    (POINTS_CONFIG["proposed_adjustments"]["points_per_correct_original_budget"] * 5) + # Assuming 5 total adjustments
    POINTS_CONFIG["proposed_adjustments"]["includes_only_adjusted_categories"] +
    POINTS_CONFIG["calculation_notes_format"]
)
# Ensure MAX_POINTS is 100, adjust config if needed. If not 100, print a warning.
if MAX_POINTS != 100:
    print(f"Warning: MAX_POINTS calculated ({MAX_POINTS}) does not equal 100. Please check POINTS_CONFIG.", file=sys.stderr)


# --- Helper Functions ---

def load_json_file(filepath):
    """Loads a JSON file and returns the data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format in {filepath}: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred while reading {filepath}: {e}"}

def compare_floats(a, b, tolerance=1e-6):
    """Compares two floats within a small tolerance."""
    # In this specific case, inputs are likely integers or simple decimals,
    # but using a tolerance is good practice for potential float comparisons.
    return abs(a - b) < tolerance

def safe_get(data, key, default=None):
    """Safely get a key from a dictionary."""
    return data.get(key, default) if isinstance(data, dict) else default

# --- Evaluation Functions ---

def check_json_structure(candidate_data):
    """Checks if the main keys exist and have the correct basic types."""
    required_keys = {
        "analysis_summary": list,
        "proposed_adjustments": list,
        "budget_constraint_check": dict,
        "calculation_notes": list
    }
    errors = []
    valid = True
    score = 0
    details = {"keys_found": [], "keys_missing": [], "type_errors": []}

    if not isinstance(candidate_data, dict):
        return False, 0, {"error": "Root element is not a JSON object."}

    for key, expected_type in required_keys.items():
        if key not in candidate_data:
            valid = False
            errors.append(f"Missing required key: '{key}'")
            details["keys_missing"].append(key)
        elif not isinstance(candidate_data[key], expected_type):
            valid = False
            errors.append(f"Key '{key}' has incorrect type (expected {expected_type.__name__}, got {type(candidate_data[key]).__name__})")
            details["type_errors"].append({"key": key, "expected": expected_type.__name__, "actual": type(candidate_data[key]).__name__})
            details["keys_found"].append(key) # Found, but wrong type
        else:
             details["keys_found"].append(key)

    if valid:
        score = POINTS_CONFIG["valid_json_structure"]

    details["valid"] = valid
    details["errors"] = errors
    return valid, score, details

def check_budget_constraint(candidate_bc, answer_key_bc, candidate_adjustments):
    """Evaluates the budget_constraint_check section."""
    points = 0
    results = {
        "original_total_correct": False,
        "adjusted_total_correct": False,
        "constraint_met_check": False,
        "internal_consistency_check": False,
        "candidate_value": safe_get(candidate_bc, 'adjusted_total_budget', 'N/A'),
        "key_value": safe_get(answer_key_bc, 'adjusted_total_budget', 'N/A'),
        "candidate_constraint_met": safe_get(candidate_bc, 'constraint_met', 'N/A'),
        "calculated_sum_adjustments": "N/A",
        "errors": []
    }

    if not isinstance(candidate_bc, dict):
        results["errors"].append("budget_constraint_check is not a dictionary.")
        return points, results

    # 1. Original Total Budget Check
    cand_orig = safe_get(candidate_bc, 'original_total_budget')
    key_orig = safe_get(answer_key_bc, 'original_total_budget')
    if isinstance(cand_orig, (int, float)) and isinstance(key_orig, (int, float)) and compare_floats(cand_orig, key_orig):
        results["original_total_correct"] = True
        points += POINTS_CONFIG["budget_constraint"]["original_total_correct"]
    else:
        results["errors"].append(f"Original total budget mismatch (Candidate: {cand_orig}, Key: {key_orig})")

    # 2. Adjusted Total Budget Check (against key)
    cand_adj = safe_get(candidate_bc, 'adjusted_total_budget')
    key_adj = safe_get(answer_key_bc, 'adjusted_total_budget')
    if isinstance(cand_adj, (int, float)) and isinstance(key_adj, (int, float)) and compare_floats(cand_adj, key_adj):
        results["adjusted_total_correct"] = True
        points += POINTS_CONFIG["budget_constraint"]["adjusted_total_correct"]
    else:
         results["errors"].append(f"Adjusted total budget mismatch (Candidate: {cand_adj}, Key: {key_adj})")

    # 3. Constraint Met Flag Check
    cand_met = safe_get(candidate_bc, 'constraint_met')
    if cand_met is True: # Must be explicitly true
        results["constraint_met_check"] = True
        points += POINTS_CONFIG["budget_constraint"]["constraint_met_true"]
    else:
        results["errors"].append(f"Candidate 'constraint_met' is not true (Value: {cand_met})")

    # 4. Internal Consistency Check
    calculated_sum = 0
    valid_sum = True
    if isinstance(candidate_adjustments, list):
        try:
            # Need original total to calculate sum correctly (add unchanged categories)
            # This is complex. Let's simplify: check if candidate's stated adjusted total
            # equals their stated original total IF constraint_met is true.
            # A better check: sum candidate's *own* adjusted_budget values.
            cand_adj_lines_sum = sum(item.get('adjusted_budget', 0) for item in candidate_adjustments if isinstance(item.get('adjusted_budget'), (int, float)))

            # We need to add budgets of categories *not* mentioned in adjustments.
            # This requires the original budget data, which isn't directly passed here.
            # Let's stick to comparing candidate's stated adjusted total vs key's adjusted total (done above)
            # and candidate's stated adjusted total vs candidate's stated original total if constraint_met is true.

            if cand_met is True and isinstance(cand_adj, (int, float)) and isinstance(cand_orig, (int, float)):
                 if compare_floats(cand_adj, cand_orig):
                     results["internal_consistency_check"] = True
                     points += POINTS_CONFIG["budget_constraint"]["internal_consistency"]
                 else:
                     results["errors"].append(f"Internal inconsistency: 'constraint_met' is true, but candidate's adjusted total ({cand_adj}) != original total ({cand_orig})")
            elif cand_met is not True:
                 # If constraint_met is false, internal consistency check is N/A in this context
                 results["internal_consistency_check"] = "N/A (constraint_met is not true)"
            else:
                 results["errors"].append("Could not perform internal consistency check due to missing/invalid values.")

        except Exception as e:
            results["errors"].append(f"Error during internal consistency check: {e}")
            valid_sum = False
    else:
        results["errors"].append("Cannot perform internal consistency check: proposed_adjustments is not a list.")
        valid_sum = False

    # results["calculated_sum_adjustments"] = calculated_sum if valid_sum else "Error" # Removed complex sum check

    return points, results


def check_analysis_summary(candidate_summary, answer_key_summary):
    """Evaluates the analysis_summary section."""
    points = 0
    results = {
        "correct_impacts": 0,
        "total_impacts_in_key": 0,
        "details": [],
        "errors": []
    }

    if not isinstance(candidate_summary, list):
        results["errors"].append("analysis_summary is not a list.")
        return points, results
    if not isinstance(answer_key_summary, list):
        results["errors"].append("Answer key analysis_summary is not a list.")
        return points, results # Cannot compare

    # Create lookup dictionaries for easier comparison
    key_lookup = {}
    for item in answer_key_summary:
        ref = safe_get(item, 'program_change_ref')
        cats = safe_get(item, 'affected_categories', [])
        if ref and isinstance(cats, list):
            cat_lookup = {cat.get('category_name'): cat.get('estimated_impact') for cat in cats if isinstance(cat, dict)}
            key_lookup[ref] = cat_lookup
            results["total_impacts_in_key"] += len(cat_lookup)

    cand_lookup = {}
    for item in candidate_summary:
        ref = safe_get(item, 'program_change_ref')
        cats = safe_get(item, 'affected_categories', [])
        if ref and isinstance(cats, list):
            cat_lookup = {cat.get('category_name'): cat.get('estimated_impact') for cat in cats if isinstance(cat, dict)}
            cand_lookup[ref] = cat_lookup
        elif ref:
             results["errors"].append(f"Invalid 'affected_categories' format for ref '{ref}' in candidate submission.")


    # Compare entries
    for ref, key_cats in key_lookup.items():
        detail = {"program_change_ref": ref, "matches": [], "mismatches": []}
        cand_cats = cand_lookup.get(ref, {})

        for cat_name, key_impact in key_cats.items():
            cand_impact = cand_cats.get(cat_name)
            match_info = {"category_name": cat_name, "key_impact": key_impact}

            if cand_impact is None:
                match_info["candidate_impact"] = "Missing"
                match_info["match"] = False
                detail["mismatches"].append(match_info)
            elif isinstance(cand_impact, (int, float)) and isinstance(key_impact, (int, float)) and compare_floats(cand_impact, key_impact):
                 match_info["candidate_impact"] = cand_impact
                 match_info["match"] = True
                 detail["matches"].append(match_info)
                 results["correct_impacts"] += 1
                 points += POINTS_CONFIG["analysis_summary"]["points_per_correct_impact"]
            else:
                match_info["candidate_impact"] = cand_impact
                match_info["match"] = False
                detail["mismatches"].append(match_info)

        # Check for extra categories in candidate submission for this ref
        extra_cats = set(cand_cats.keys()) - set(key_cats.keys())
        for extra_cat in extra_cats:
             detail["mismatches"].append({
                 "category_name": extra_cat,
                 "key_impact": "Not Expected",
                 "candidate_impact": cand_cats[extra_cat],
                 "match": False
             })

        results["details"].append(detail)

    # Check for extra program_change_ref in candidate submission
    extra_refs = set(cand_lookup.keys()) - set(key_lookup.keys())
    for extra_ref in extra_refs:
        results["errors"].append(f"Extra program_change_ref found in candidate submission: '{extra_ref}'")


    return points, results


def check_proposed_adjustments(candidate_adjustments, answer_key_adjustments):
    """Evaluates the proposed_adjustments section."""
    points = 0
    results = {
        "travel_reallocation_correct": False,
        "correct_other_adjustments": 0,
        "correct_adjusted_budgets": 0,
        "correct_original_budgets": 0,
        "includes_only_adjusted_categories": False,
        "details": [],
        "errors": []
    }
    travel_category_name = "Travel" # As defined in the scenario

    if not isinstance(candidate_adjustments, list):
        results["errors"].append("proposed_adjustments is not a list.")
        return points, results
    if not isinstance(answer_key_adjustments, list):
        results["errors"].append("Answer key proposed_adjustments is not a list.")
        return points, results # Cannot compare

    key_lookup = {item.get('category_name'): item for item in answer_key_adjustments if isinstance(item, dict)}
    cand_lookup = {item.get('category_name'): item for item in candidate_adjustments if isinstance(item, dict)}

    key_categories = set(key_lookup.keys())
    cand_categories = set(cand_lookup.keys())

    # Check if candidate included only adjusted categories (compared to key)
    if key_categories == cand_categories:
        results["includes_only_adjusted_categories"] = True
        points += POINTS_CONFIG["proposed_adjustments"]["includes_only_adjusted_categories"]
    else:
        missing_cats = key_categories - cand_categories
        extra_cats = cand_categories - key_categories
        if missing_cats:
            results["errors"].append(f"Missing expected adjusted categories: {list(missing_cats)}")
        if extra_cats:
             results["errors"].append(f"Included non-adjusted or unexpected categories: {list(extra_cats)}")


    # Compare each adjustment
    for cat_name, key_adj_item in key_lookup.items():
        cand_adj_item = cand_lookup.get(cat_name)
        detail = {"category_name": cat_name, "match_status": {}}

        if cand_adj_item is None:
            detail["match_status"] = "Category missing in submission"
            results["details"].append(detail)
            continue # Skip comparison if category is missing

        # Compare original_budget
        key_orig = safe_get(key_adj_item, 'original_budget')
        cand_orig = safe_get(cand_adj_item, 'original_budget')
        orig_match = isinstance(cand_orig, (int, float)) and isinstance(key_orig, (int, float)) and compare_floats(cand_orig, key_orig)
        detail["match_status"]["original_budget"] = {"match": orig_match, "candidate": cand_orig, "key": key_orig}
        if orig_match:
            results["correct_original_budgets"] += 1
            points += POINTS_CONFIG["proposed_adjustments"]["points_per_correct_original_budget"]

        # Compare adjustment amount
        key_adjust = safe_get(key_adj_item, 'adjustment')
        cand_adjust = safe_get(cand_adj_item, 'adjustment')
        adjust_match = isinstance(cand_adjust, (int, float)) and isinstance(key_adjust, (int, float)) and compare_floats(cand_adjust, key_adjust)
        detail["match_status"]["adjustment"] = {"match": adjust_match, "candidate": cand_adjust, "key": key_adjust}
        if adjust_match:
            if cat_name == travel_category_name:
                results["travel_reallocation_correct"] = True
                points += POINTS_CONFIG["proposed_adjustments"]["travel_reallocation_correct"]
            else:
                results["correct_other_adjustments"] += 1
                points += POINTS_CONFIG["proposed_adjustments"]["points_per_correct_other_adjustment"]

        # Compare adjusted_budget
        key_adj_bud = safe_get(key_adj_item, 'adjusted_budget')
        cand_adj_bud = safe_get(cand_adj_item, 'adjusted_budget')
        adj_bud_match = isinstance(cand_adj_bud, (int, float)) and isinstance(key_adj_bud, (int, float)) and compare_floats(cand_adj_bud, key_adj_bud)
        detail["match_status"]["adjusted_budget"] = {"match": adj_bud_match, "candidate": cand_adj_bud, "key": key_adj_bud}
        if adj_bud_match:
            results["correct_adjusted_budgets"] += 1
            points += POINTS_CONFIG["proposed_adjustments"]["points_per_correct_adjusted_budget"]

        # Check internal consistency for the candidate's line item
        if isinstance(cand_orig, (int, float)) and isinstance(cand_adjust, (int, float)) and isinstance(cand_adj_bud, (int, float)):
            detail["match_status"]["internal_line_consistency"] = compare_floats(cand_orig + cand_adjust, cand_adj_bud)
        else:
            detail["match_status"]["internal_line_consistency"] = "N/A (invalid types)"


        results["details"].append(detail)

    return points, results

def check_calculation_notes(candidate_notes):
    """Checks if calculation_notes exists and is a list of strings."""
    points = 0 # No points assigned for this check
    results = {
        "present_and_list": False,
        "is_list_of_strings": False,
        "notes_content": None,
        "errors": []
    }

    if candidate_notes is None:
        results["errors"].append("calculation_notes key is missing.")
        return points, results

    if not isinstance(candidate_notes, list):
        results["errors"].append("calculation_notes is not a list.")
        results["notes_content"] = candidate_notes
        return points, results

    results["present_and_list"] = True
    results["notes_content"] = candidate_notes

    # Check if all elements are strings
    all_strings = all(isinstance(item, str) for item in candidate_notes)
    if all_strings:
        results["is_list_of_strings"] = True
        # Assign points based on config if needed in the future
        # points += POINTS_CONFIG["calculation_notes_format"]
    else:
        results["errors"].append("Not all items in calculation_notes are strings.")

    return points, results

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate Budget Analyst Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    # Load files
    candidate_data = load_json_file(args.submission_file)
    answer_key_data = load_json_file(args.answer_key_file)

    # Initialize results structure
    results = {
        "submission_file": args.submission_file,
        "answer_key_file": args.answer_key_file,
        "overall_score": 0,
        "total_possible_points": MAX_POINTS,
        "evaluation_details": {}
    }

    # Handle loading errors
    if "error" in candidate_data:
        results["evaluation_details"]["error"] = f"Failed to load submission file: {candidate_data['error']}"
        print(f"Error: {results['evaluation_details']['error']}", file=sys.stderr)
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        sys.exit(1)

    if "error" in answer_key_data:
        results["evaluation_details"]["error"] = f"Failed to load answer key file: {answer_key_data['error']}"
        print(f"Error: {results['evaluation_details']['error']}", file=sys.stderr)
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        sys.exit(1)

    # --- Start Evaluation ---
    total_score = 0

    # 1. Check Basic JSON Structure
    structure_valid, structure_score, structure_details = check_json_structure(candidate_data)
    total_score += structure_score
    results["evaluation_details"]["json_structure"] = structure_details
    results["evaluation_details"]["json_structure"]["points"] = structure_score
    if not structure_valid:
        results["evaluation_details"]["error"] = "Submission failed basic structure check. Further evaluation may be inaccurate."
        print("Error: Submission failed basic structure check.", file=sys.stderr)
        # Decide whether to stop or continue evaluation
        # For now, continue but results might be partial

    # Get sections safely, defaulting to None if structure check failed or key missing
    candidate_bc = safe_get(candidate_data, 'budget_constraint_check', {})
    answer_key_bc = safe_get(answer_key_data, 'budget_constraint_check', {})
    candidate_summary = safe_get(candidate_data, 'analysis_summary', [])
    answer_key_summary = safe_get(answer_key_data, 'analysis_summary', [])
    candidate_adjustments = safe_get(candidate_data, 'proposed_adjustments', [])
    answer_key_adjustments = safe_get(answer_key_data, 'proposed_adjustments', [])
    candidate_notes = safe_get(candidate_data, 'calculation_notes', None) # Use None to check presence

    # 2. Check Budget Constraint
    bc_score, bc_details = check_budget_constraint(candidate_bc, answer_key_bc, candidate_adjustments)
    total_score += bc_score
    results["evaluation_details"]["budget_constraint"] = bc_details
    results["evaluation_details"]["budget_constraint"]["points"] = bc_score

    # 3. Check Analysis Summary
    summary_score, summary_details = check_analysis_summary(candidate_summary, answer_key_summary)
    total_score += summary_score
    results["evaluation_details"]["analysis_summary"] = summary_details
    results["evaluation_details"]["analysis_summary"]["points"] = summary_score

    # 4. Check Proposed Adjustments
    adjustments_score, adjustments_details = check_proposed_adjustments(candidate_adjustments, answer_key_adjustments)
    total_score += adjustments_score
    results["evaluation_details"]["proposed_adjustments"] = adjustments_details
    results["evaluation_details"]["proposed_adjustments"]["points"] = adjustments_score

    # 5. Check Calculation Notes Format
    notes_score, notes_details = check_calculation_notes(candidate_notes)
    total_score += notes_score # Currently 0 points
    results["evaluation_details"]["calculation_notes"] = notes_details
    results["evaluation_details"]["calculation_notes"]["points"] = notes_score

    # Calculate Overall Score Percentage
    if MAX_POINTS > 0:
        overall_percentage = round((total_score / MAX_POINTS) * 100, 2)
    else:
        overall_percentage = 0

    results["overall_score"] = overall_percentage
    results["total_achieved_points"] = total_score


    # Save results
    try:
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print("Evaluation complete. Results saved to test_results.json")
    except Exception as e:
        print(f"Error saving results to test_results.json: {e}", file=sys.stderr)
        # Also print results to stdout as a fallback
        print("\n--- Results ---")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()