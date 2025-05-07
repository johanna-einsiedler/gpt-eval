# task_evaluation.py

import json
import sys
import argparse
import math
from typing import Any, Dict, Tuple, Optional

def load_json(filepath: str) -> Optional[Dict]:
    """Loads a JSON file from the given filepath."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {filepath}: {e}", file=sys.stderr)
        return None

def compare_values(candidate_val: Any, expected_val: Any) -> bool:
    """
    Compares candidate value with expected value, handling specific types.
    - Floats are compared directly (assuming exact rounding was required).
    - Lists are sorted before comparison.
    """
    if type(candidate_val) != type(expected_val):
        # Allow comparison between int and float if they represent the same number
        if isinstance(candidate_val, (int, float)) and isinstance(expected_val, (int, float)):
            return math.isclose(float(candidate_val), float(expected_val), abs_tol=1e-9) # Use tolerance for float comparison
        return False

    if isinstance(expected_val, float):
         # Use isclose for float comparison to handle potential minor representation differences
         # The tolerance should be small if exact rounding was expected.
         # Example: expected 44.5, candidate 44.500000001 -> should be True
         # Example: expected 44.5, candidate 44.6 -> should be False
        return math.isclose(candidate_val, expected_val, rel_tol=1e-9, abs_tol=1e-9)
    elif isinstance(expected_val, list):
        # Sort both lists before comparing if they contain comparable items
        try:
            return sorted(candidate_val) == sorted(expected_val)
        except TypeError:
            # If lists contain unorderable types, compare as is
            return candidate_val == expected_val
    else:
        # Direct comparison for other types (int, str, bool, dict, etc.)
        return candidate_val == expected_val

def evaluate_submission(candidate_data: Dict, answer_key: Dict) -> Tuple[Dict, int, int]:
    """
    Compares the candidate's results against the answer key.

    Returns:
        A tuple containing:
        - detailed_results (dict): A dictionary with comparison details for each check.
        - correct_count (int): The number of correctly answered checks.
        - total_checks (int): The total number of checks performed.
    """
    detailed_results = {}
    correct_count = 0
    total_checks = 0

    expected_results = answer_key.get("results", {})
    candidate_results = candidate_data.get("results", {})

    # Iterate through tasks defined in the answer key
    for task_key, task_checks in expected_results.items():
        detailed_results[task_key] = {}
        candidate_task_results = candidate_results.get(task_key, {})

        # Iterate through specific checks within each task
        for check_key, expected_value in task_checks.items():
            total_checks += 1
            candidate_value = candidate_task_results.get(check_key, None) # Use None if key is missing

            is_correct = compare_values(candidate_value, expected_value)

            if is_correct:
                correct_count += 1

            detailed_results[task_key][check_key] = {
                "expected": expected_value,
                "actual": candidate_value,
                "correct": is_correct
            }

    return detailed_results, correct_count, total_checks

def main():
    """Main function to parse arguments, run evaluation, and save results."""
    parser = argparse.ArgumentParser(description="Evaluate candidate submission against an answer key.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    print(f"Loading submission file: {args.submission_file}")
    candidate_data = load_json(args.submission_file)
    if candidate_data is None:
        sys.exit(1) # Exit if loading failed

    print(f"Loading answer key file: {args.answer_key_file}")
    answer_key = load_json(args.answer_key_file)
    if answer_key is None:
        sys.exit(1) # Exit if loading failed

    # Perform the evaluation
    detailed_results, correct_count, total_checks = evaluate_submission(candidate_data, answer_key)

    # Calculate overall score
    if total_checks > 0:
        overall_score = round((correct_count / total_checks) * 100, 2)
    else:
        overall_score = 0.0

    print(f"\nEvaluation Complete:")
    print(f"  Correct answers: {correct_count}")
    print(f"  Total checks: {total_checks}")
    print(f"  Overall score: {overall_score}%")

    # Prepare final results structure
    final_results = {
        "candidate_id": candidate_data.get("candidate_id", "Not Provided"),
        "submission_file": args.submission_file,
        "answer_key_file": args.answer_key_file,
        "overall_score": overall_score,
        "correct_count": correct_count,
        "total_checks": total_checks,
        "detailed_results": detailed_results
    }

    # Save results to file
    output_filename = "test_results.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2)
        print(f"\nResults saved to {output_filename}")
    except Exception as e:
        print(f"\nError: Could not save results to {output_filename}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()