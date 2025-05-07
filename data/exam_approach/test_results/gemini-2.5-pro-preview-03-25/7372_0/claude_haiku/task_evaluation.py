import json
import sys
import os
from collections import defaultdict

# --- Configuration ---
MAX_SCORE = 18
POTENTIAL_CONSEQUENCES = ["C1", "C2", "C3", "C4", "C5", "C6"]
OUTPUT_FILENAME = "test_results.json"

# --- Helper Functions ---

def load_json(filepath):
    """Loads JSON data from a file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

def compare_assumption_lists(list1, list2):
    """Compares two lists of assumptions, ignoring order."""
    if not isinstance(list1, list) or not isinstance(list2, list):
        return False
    return set(list1) == set(list2)

def safe_get(data, keys, default=None):
    """Safely get nested dictionary values."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
             current = current[key]
        else:
            return default
    return current

# --- Main Evaluation Logic ---

def evaluate_submission(submission_data, key_data):
    """Evaluates the candidate's submission against the answer key."""
    results = {
        "candidate_id": safe_get(submission_data, ["candidate_id"], "MISSING_OR_INVALID"),
        "overall_score": 0.0,
        "max_score": MAX_SCORE,
        "total_points_achieved": 0,
        "evaluation_details": {}
    }
    total_score = 0

    # --- Prepare Key Data for easier lookup ---
    key_sets_map = {item['set_id']: item for item in safe_get(key_data, ["assumption_sets"], [])}

    # --- Prepare Submission Data for easier lookup ---
    submission_sets_map = {item['set_id']: item for item in safe_get(submission_data, ["assumption_sets"], [])}

    # --- Iterate through sets defined in the KEY ---
    for set_id, key_set_data in key_sets_map.items():
        set_results = {
            "points_achieved": 0,
            "max_points_for_set": 0, # Will be calculated dynamically
            "assumption_set_match": {"correct": False, "points": 0},
            "consequences": {}
        }
        max_points_this_set = 0

        submission_set_data = submission_sets_map.get(set_id)

        if not submission_set_data:
            set_results["error"] = f"Submission data for '{set_id}' not found or invalid."
            results["evaluation_details"][set_id] = set_results
            # Max points for this set are still counted towards the total max score
            # but the candidate gets 0 for this section.
            # Calculate max points for this set based on key:
            max_points_this_set += 1 # For assumption_set_match
            key_derived_consequences_map = {
                item['consequence_id']: item['minimal_required_assumptions']
                for item in safe_get(key_set_data, ["derived_consequences"], [])
            }
            for consequence_id in POTENTIAL_CONSEQUENCES:
                 if consequence_id in key_derived_consequences_map:
                     max_points_this_set += 2 # 1 for derivability, 1 for minimal assumptions
                 else:
                     max_points_this_set += 1 # 1 for correctly identifying as non-derivable
            set_results["max_points_for_set"] = max_points_this_set
            continue # Skip evaluation for this set

        # 1. Compare 'assumptions_in_set' (1 point)
        max_points_this_set += 1
        key_assumptions = safe_get(key_set_data, ["assumptions_in_set"], [])
        sub_assumptions = safe_get(submission_set_data, ["assumptions_in_set"], [])
        assumptions_match = compare_assumption_lists(key_assumptions, sub_assumptions)
        set_results["assumption_set_match"]["correct"] = assumptions_match
        if assumptions_match:
            set_results["assumption_set_match"]["points"] = 1
            set_results["points_achieved"] += 1
            total_score += 1
        set_results["assumption_set_match"]["submitted"] = sub_assumptions
        set_results["assumption_set_match"]["expected"] = key_assumptions


        # 2. Compare 'derived_consequences' (Max 8 points per set)
        key_derived_consequences_map = {
            item['consequence_id']: item['minimal_required_assumptions']
            for item in safe_get(key_set_data, ["derived_consequences"], [])
        }
        sub_derived_consequences_map = {
            item['consequence_id']: safe_get(item, ["minimal_required_assumptions"], None) # Handle missing key
            for item in safe_get(submission_set_data, ["derived_consequences"], [])
            if isinstance(item, dict) and 'consequence_id' in item # Ensure item is dict with id
        }

        for consequence_id in POTENTIAL_CONSEQUENCES:
            consequence_result = {
                "expected_derivable": consequence_id in key_derived_consequences_map,
                "submitted_derivable": consequence_id in sub_derived_consequences_map,
                "points_derivable": 0,
                "minimal_assumptions_match": None, # None, True, False
                "points_minimal_assumptions": 0,
                "submitted_minimal_assumptions": sub_derived_consequences_map.get(consequence_id),
                "expected_minimal_assumptions": key_derived_consequences_map.get(consequence_id)
            }

            should_be_derivable = consequence_result["expected_derivable"]
            is_submitted_as_derivable = consequence_result["submitted_derivable"]

            # Score point for correctly identifying derivability (or non-derivability)
            if should_be_derivable == is_submitted_as_derivable:
                consequence_result["points_derivable"] = 1
                set_results["points_achieved"] += 1
                total_score += 1
            max_points_this_set += 1 # Max 1 point for derivability check

            # If it should be derivable AND was submitted as derivable, check minimal assumptions
            if should_be_derivable and is_submitted_as_derivable:
                max_points_this_set += 1 # Max 1 point for minimal assumptions check
                key_min_assumptions = consequence_result["expected_minimal_assumptions"]
                sub_min_assumptions = consequence_result["submitted_minimal_assumptions"]

                # Check if submission provided a valid list for minimal assumptions
                if isinstance(sub_min_assumptions, list):
                    assumptions_match = compare_assumption_lists(key_min_assumptions, sub_min_assumptions)
                    consequence_result["minimal_assumptions_match"] = assumptions_match
                    if assumptions_match:
                        consequence_result["points_minimal_assumptions"] = 1
                        set_results["points_achieved"] += 1
                        total_score += 1
                else:
                    # Submitted as derivable, but minimal assumptions format is wrong/missing
                    consequence_result["minimal_assumptions_match"] = False
                    consequence_result["error"] = "Submitted minimal assumptions is not a list or is missing."


            set_results["consequences"][consequence_id] = consequence_result

        set_results["max_points_for_set"] = max_points_this_set
        results["evaluation_details"][set_id] = set_results

    # --- Calculate Final Score ---
    results["total_points_achieved"] = total_score
    if MAX_SCORE > 0:
        results["overall_score"] = round((total_score / MAX_SCORE) * 100, 2)
    else:
         results["overall_score"] = 0.0 # Avoid division by zero if MAX_SCORE is somehow 0

    # Add check for total max points calculated vs configured MAX_SCORE
    calculated_max_score = sum(v.get("max_points_for_set", 0) for v in results["evaluation_details"].values())
    if calculated_max_score != MAX_SCORE:
         print(f"Warning: Calculated max score ({calculated_max_score}) does not match configured MAX_SCORE ({MAX_SCORE}). Check configuration and key.", file=sys.stderr)
         results["warning"] = f"Calculated max score ({calculated_max_score}) != configured MAX_SCORE ({MAX_SCORE})"
         # Use calculated max score for percentage if mismatch occurs, might be more accurate
         if calculated_max_score > 0:
             results["overall_score"] = round((total_score / calculated_max_score) * 100, 2)
             results["max_score"] = calculated_max_score # Update max_score in results
         else:
             results["overall_score"] = 0.0


    return results

# --- Script Execution ---

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file.json> <answer_key_file.json>", file=sys.stderr)
        sys.exit(1)

    submission_filepath = sys.argv[1]
    key_filepath = sys.argv[2]

    print(f"Loading submission file: {submission_filepath}")
    submission_content = load_json(submission_filepath)

    print(f"Loading answer key file: {key_filepath}")
    key_content = load_json(key_filepath)

    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_content, key_content)

    # --- Save Results ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=4)
        print(f"Evaluation complete. Results saved to {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error writing results to {OUTPUT_FILENAME}: {e}", file=sys.stderr)
        sys.exit(1)