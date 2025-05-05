# task_evaluation.py

import json
import argparse
import sys
import math
from typing import Any, Dict, Tuple, Union

# --- Configuration ---
EXPECTED_FILENAME = "test_submission.json"
OUTPUT_FILENAME = "test_results.json"
PASSING_THRESHOLD_PERCENT = 82.0 # Corresponds to 14/17 items

# --- Helper Functions ---

def load_json_file(filepath: str) -> Union[Dict, None]:
    """Loads a JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read file {filepath}. Details: {e}", file=sys.stderr)
        return None

def compare_values(candidate_val: Any, key_val: Any) -> bool:
    """Compares two values, handling floats with tolerance."""
    if isinstance(key_val, float):
        # Check if candidate value is also a number (int or float)
        if not isinstance(candidate_val, (int, float)):
            return False
        # Compare floats based on the key's precision (implicitly via direct comparison)
        # The key should have the correctly rounded value.
        # A small tolerance could be added, but strict adherence to rounding is preferred.
        # return math.isclose(float(candidate_val), key_val, rel_tol=1e-9, abs_tol=1e-9)
        # Let's stick to exact comparison assuming correct rounding by candidate:
        return float(candidate_val) == key_val
    elif isinstance(key_val, (int, str, bool)) or key_val is None:
        return candidate_val == key_val
    else:
        # Fallback for unexpected types in key (shouldn't happen with provided key)
        return candidate_val == key_val

def evaluate_submission(candidate_data: Dict, key_data: Dict) -> Tuple[Dict, int, int]:
    """
    Recursively compares candidate data against the key data.
    Returns the detailed results, score achieved, and total possible score.
    """
    results = {}
    score = 0
    total_possible = 0

    # Iterate through the keys defined in the ANSWER KEY
    for key, key_value in key_data.items():
        # Skip candidate_id comparison
        if key == "candidate_id":
            results[key] = {
                "submitted": candidate_data.get(key, "MISSING"),
                "expected": key_value,
                "correct": "N/A" # Not scored
            }
            continue

        candidate_value = candidate_data.get(key) # Use .get() to handle missing keys

        if isinstance(key_value, dict):
            # Recurse for nested dictionaries
            if isinstance(candidate_value, dict):
                nested_results, nested_score, nested_total = evaluate_submission(candidate_value, key_value)
                results[key] = nested_results
                score += nested_score
                total_possible += nested_total
            else:
                # Structure mismatch: candidate provided non-dict or None where dict expected
                # Mark all items within this branch as incorrect
                nested_results, _, nested_total = evaluate_submission({}, key_value) # Get structure and total
                results[key] = mark_branch_incorrect(nested_results, candidate_value)
                total_possible += nested_total
                # Score remains unchanged (0 points for this branch)

        elif isinstance(key_value, (int, float, str, bool)) or key_value is None:
            # Leaf node - perform comparison
            total_possible += 1
            is_correct = False
            if candidate_value is not None: # Check if key exists in submission implicitly
                 is_correct = compare_values(candidate_value, key_value)

            if is_correct:
                score += 1

            results[key] = {
                "submitted": candidate_value if candidate_value is not None else "MISSING",
                "expected": key_value,
                "correct": is_correct,
                "points": 1 if is_correct else 0
            }
        else:
             # Handle unexpected types in key if necessary (e.g., lists)
             print(f"Warning: Unsupported type '{type(key_value)}' encountered for key '{key}' in answer key.", file=sys.stderr)
             results[key] = {
                 "submitted": candidate_value,
                 "expected": key_value,
                 "correct": False, # Cannot evaluate unsupported types
                 "points": 0
             }

    # Check for extra keys in candidate submission (optional, not scored)
    # for key in candidate_data:
    #     if key not in key_data and key != "candidate_id":
    #         if key not in results: # Avoid overwriting evaluated keys
    #              results[key] = {"submitted": candidate_data[key], "expected": "NOT_EXPECTED", "correct": "N/A"}

    return results, score, total_possible

def mark_branch_incorrect(key_results_structure: Dict, submitted_value: Any) -> Dict:
    """Marks all leaf nodes in a results structure branch as incorrect."""
    marked_results = {}
    for key, value in key_results_structure.items():
        if "expected" in value and "submitted" in value: # Leaf node structure
            marked_results[key] = {
                "submitted": submitted_value if isinstance(submitted_value, (int, float, str, bool)) or submitted_value is None else type(submitted_value).__name__, # Show what was submitted at this level
                "expected": value["expected"],
                "correct": False,
                "points": 0
            }
        elif isinstance(value, dict): # Nested dict
             marked_results[key] = mark_branch_incorrect(value, submitted_value) # Recurse
        else:
             marked_results[key] = value # Keep other potential metadata
    return marked_results


# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate Biostatistician practical exam submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    print(f"Loading submission file: {args.submission_file}")
    candidate_data = load_json_file(args.submission_file)
    if candidate_data is None:
        sys.exit(1) # Exit if loading failed

    print(f"Loading answer key file: {args.key_file}")
    key_data = load_json_file(args.key_file)
    if key_data is None:
        sys.exit(1) # Exit if loading failed

    # --- Basic Structure Validation ---
    if not isinstance(candidate_data, dict):
        print(f"Error: Submission file '{args.submission_file}' does not contain a root JSON object.", file=sys.stderr)
        sys.exit(1)

    # Check filename (optional, but good practice based on instructions)
    # submission_basename = os.path.basename(args.submission_file)
    # if submission_basename != EXPECTED_FILENAME:
    #     print(f"Warning: Submission filename '{submission_basename}' does not match expected '{EXPECTED_FILENAME}'.", file=sys.stderr)

    # --- Evaluation ---
    print("Evaluating submission...")
    detailed_results, final_score, total_possible_score = evaluate_submission(candidate_data, key_data)

    if total_possible_score == 0:
        print("Error: No scorable items found in the answer key.", file=sys.stderr)
        overall_percentage = 0.0
    else:
        overall_percentage = round((final_score / total_possible_score) * 100, 2)

    # Determine pass/fail status
    passed = overall_percentage >= PASSING_THRESHOLD_PERCENT

    # --- Prepare Final Output ---
    final_output = {
        "candidate_id": candidate_data.get("candidate_id", "MISSING"),
        "overall_score_points": final_score,
        "total_possible_points": total_possible_score,
        "overall_score_percentage": overall_percentage,
        "passing_threshold_percentage": PASSING_THRESHOLD_PERCENT,
        "passed": passed,
        "detailed_results": detailed_results
    }

    # --- Save Results ---
    print(f"Saving evaluation results to {OUTPUT_FILENAME}...")
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2)
        print("Evaluation complete.")
        print(f"Overall Score: {final_score}/{total_possible_score} ({overall_percentage}%) - {'PASSED' if passed else 'FAILED'}")
    except IOError as e:
        print(f"Error: Could not write results file {OUTPUT_FILENAME}. Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during result saving: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()