# task_evaluation.py
import json
import argparse
import sys
import os
from decimal import Decimal, InvalidOperation

def load_json_file(filepath):
    """Loads a JSON file and returns its content as a dictionary."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

def compare_values(submitted_val, expected_val, key_path_str):
    """
    Compares submitted and expected values, handling types and precision.
    Returns True if they match according to rules, False otherwise.
    """
    # Type check: Ensure both are numbers (int or float) if expected is a number
    if isinstance(expected_val, (int, float)):
        if not isinstance(submitted_val, (int, float)):
            print(f"Warning: Type mismatch for '{key_path_str}'. Expected number, got {type(submitted_val).__name__}.", file=sys.stderr)
            return False

        # Use Decimal for precise comparison, especially after specified rounding
        try:
            # Convert both to Decimal for comparison
            # Handle potential floating point inaccuracies by converting to string first
            # if they are floats, otherwise direct conversion for ints
            dec_expected = Decimal(str(expected_val)) if isinstance(expected_val, float) else Decimal(expected_val)
            dec_submitted = Decimal(str(submitted_val)) if isinstance(submitted_val, float) else Decimal(submitted_val)

            # Check if the number of decimal places matches the expected precision implicitly defined by the answer key format
            # Note: This assumes the answer key values ARE correctly rounded as specified in instructions
            expected_tuple = dec_expected.as_tuple()
            submitted_tuple = dec_submitted.as_tuple()

            # Compare exponents (number of decimal places)
            if expected_tuple.exponent != submitted_tuple.exponent:
                 print(f"Warning: Precision mismatch for '{key_path_str}'. Submitted: {submitted_val} (Exponent: {submitted_tuple.exponent}), Expected: {expected_val} (Exponent: {expected_tuple.exponent}). Check rounding.", file=sys.stderr)
                 # Decide if this should fail the check - for strict adherence to rounding, it should.
                 # Let's consider it a failure if the *value* is correct but rounding isn't exact.
                 # However, a simple value comparison might be sufficient if rounding check is too strict.
                 # Let's stick to value comparison for now, assuming rounding was done before submission.
                 # return False # Uncomment this line for strict rounding check

            # Compare values
            return dec_submitted == dec_expected

        except InvalidOperation:
            print(f"Warning: Could not convert values for '{key_path_str}' to Decimal for comparison.", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Warning: Error comparing values for '{key_path_str}': {e}", file=sys.stderr)
            return False

    # Handle non-numeric types if necessary (though not expected for scoreable fields here)
    else:
        return submitted_val == expected_val


def main():
    parser = argparse.ArgumentParser(description="Evaluate Actuarial Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")
    args = parser.parse_args()

    print(f"Loading submission file: {args.submission_file}")
    submission_data = load_json_file(args.submission_file)
    print(f"Loading answer key file: {args.answer_key_file}")
    answer_key_data = load_json_file(args.answer_key_file)

    # --- Basic Structure Validation ---
    required_top_level_keys = ["candidate_id", "total_exposure", "total_deaths", "crude_mortality_rate", "age_band_40_59", "age_band_60_79"]
    required_band_keys = ["exposure", "deaths", "mortality_rate"]

    if not all(key in submission_data for key in required_top_level_keys):
        print("Error: Submission JSON is missing one or more required top-level keys.", file=sys.stderr)
        # Optionally create a results file indicating format error
        results = {
            "candidate_id": submission_data.get("candidate_id", "MISSING"),
            "evaluation_status": "FAILED_FORMATTING",
            "error_message": "Missing required top-level keys.",
            "overall_score": 0.0
        }
        with open("test_results.json", 'w') as f:
            json.dump(results, f, indent=4)
        sys.exit(1) # Exit if basic structure is wrong

    if not isinstance(submission_data["age_band_40_59"], dict) or not all(key in submission_data["age_band_40_59"] for key in required_band_keys):
         print("Error: Submission JSON 'age_band_40_59' is not a dictionary or is missing required keys.", file=sys.stderr)
         results = {
            "candidate_id": submission_data.get("candidate_id", "UNKNOWN"),
            "evaluation_status": "FAILED_FORMATTING",
            "error_message": "Invalid or incomplete 'age_band_40_59' structure.",
            "overall_score": 0.0
         }
         with open("test_results.json", 'w') as f:
            json.dump(results, f, indent=4)
         sys.exit(1) # Exit if basic structure is wrong

    if not isinstance(submission_data["age_band_60_79"], dict) or not all(key in submission_data["age_band_60_79"] for key in required_band_keys):
         print("Error: Submission JSON 'age_band_60_79' is not a dictionary or is missing required keys.", file=sys.stderr)
         results = {
            "candidate_id": submission_data.get("candidate_id", "UNKNOWN"),
            "evaluation_status": "FAILED_FORMATTING",
            "error_message": "Invalid or incomplete 'age_band_60_79' structure.",
            "overall_score": 0.0
         }
         with open("test_results.json", 'w') as f:
            json.dump(results, f, indent=4)
         sys.exit(1) # Exit if basic structure is wrong


    # --- Detailed Comparison ---
    results = {
        "candidate_id": submission_data.get("candidate_id", "MISSING_ID"),
        "comparison_details": {},
        "summary": {
             "correct_answers": 0,
             "total_fields_checked": 0
        }
        # overall_score will be added later
    }

    # Define the keys/paths to check for scoring
    # Using tuples for nested paths: (dict_key, nested_key)
    keys_to_check = [
        "total_exposure",
        "total_deaths",
        "crude_mortality_rate",
        ("age_band_40_59", "exposure"),
        ("age_band_40_59", "deaths"),
        ("age_band_40_59", "mortality_rate"),
        ("age_band_60_79", "exposure"),
        ("age_band_60_79", "deaths"),
        ("age_band_60_79", "mortality_rate"),
    ]

    correct_count = 0
    total_checked = len(keys_to_check)

    for key_path in keys_to_check:
        submitted_val = None
        expected_val = None
        is_correct = False
        key_path_str = ".".join(key_path) if isinstance(key_path, tuple) else key_path

        try:
            # Retrieve values using the path
            if isinstance(key_path, tuple):
                sub_dict = submission_data.get(key_path[0], {})
                submitted_val = sub_dict.get(key_path[1], "MISSING_KEY")
                exp_dict = answer_key_data.get(key_path[0], {})
                expected_val = exp_dict.get(key_path[1]) # Assume answer key is correct
            else:
                submitted_val = submission_data.get(key_path, "MISSING_KEY")
                expected_val = answer_key_data.get(key_path) # Assume answer key is correct

            if submitted_val == "MISSING_KEY":
                 print(f"Warning: Key '{key_path_str}' missing in submission.", file=sys.stderr)
                 is_correct = False
            elif expected_val is None:
                 print(f"Warning: Key '{key_path_str}' missing in answer key? Skipping comparison.", file=sys.stderr)
                 # This shouldn't happen if answer key is correct, maybe decrement total_checked?
                 # For now, treat as not comparable / not correct.
                 is_correct = False
            else:
                is_correct = compare_values(submitted_val, expected_val, key_path_str)

            if is_correct:
                correct_count += 1

        except Exception as e:
            print(f"Error processing key '{key_path_str}': {e}", file=sys.stderr)
            is_correct = False # Mark as incorrect if any error occurs during processing

        # Store comparison details
        results["comparison_details"][key_path_str] = {
            "submitted": submitted_val if submitted_val != "MISSING_KEY" else None,
            "expected": expected_val,
            "correct": is_correct
        }

    # --- Calculate Score and Finalize Results ---
    results["summary"]["correct_answers"] = correct_count
    results["summary"]["total_fields_checked"] = total_checked
    overall_score = (correct_count / total_checked) * 100 if total_checked > 0 else 0
    results["overall_score"] = round(overall_score, 2) # Store overall score as percentage rounded to 2 dp

    # Add pass/fail based on criteria (6/8 correct = 75%)
    # Note: The original criteria mentioned 6/8, but we check 9 fields.
    # Let's adjust: Pass if >= 7 out of 9 fields are correct (~77.8%)
    # Or stick to the original intent: 6 correct fields needed. Let's use 6.
    # Minimum correct fields for pass = 6
    min_correct_for_pass = 6
    if results["summary"]["correct_answers"] >= min_correct_for_pass:
         results["summary"]["result_status"] = "Pass"
    else:
         results["summary"]["result_status"] = "Fail"


    # --- Save Results ---
    output_filename = "test_results.json"
    try:
        with open(output_filename, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation complete. Results saved to {output_filename}")
    except Exception as e:
        print(f"Error writing results to {output_filename}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()