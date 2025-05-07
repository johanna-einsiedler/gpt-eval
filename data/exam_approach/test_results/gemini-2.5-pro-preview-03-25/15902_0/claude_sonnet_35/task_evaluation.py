# task_evaluation.py

import json
import argparse
import sys
import os

def load_json_file(filepath):
    """Loads a JSON file and returns its content."""
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

def evaluate_submission(submission_data, answer_key_data):
    """Compares submission data against the answer key and calculates score."""
    results = {
        "candidate_id": submission_data.get("candidate_id", "Not Provided"), # Get candidate ID if present
        "detailed_comparison": {},
        "overall_score": 0.0
    }
    correct_count = 0
    total_metrics = len(answer_key_data)

    if total_metrics == 0:
        print("Warning: Answer key is empty. Cannot evaluate.", file=sys.stderr)
        return results # Return default results if answer key is empty

    # Iterate through the metrics defined in the answer key
    for key, expected_value in answer_key_data.items():
        submitted_value = submission_data.get(key, None) # Use .get() for safe access
        is_correct = False

        # Check if the key exists in submission and the value matches the expected value
        if key in submission_data:
            # Direct comparison should work given the specific rounding requirements
            if submitted_value == expected_value:
                is_correct = True
                correct_count += 1
            else:
                # Optional: Add a check for type mismatch if needed, but strict comparison is likely intended
                # print(f"Debug: Mismatch for {key}. Submitted: {submitted_value} ({type(submitted_value)}), Expected: {expected_value} ({type(expected_value)})")
                pass
        else:
            # Key missing in submission
            submitted_value = "Missing Key" # Indicate the key was not found

        results["detailed_comparison"][key] = {
            "submitted": submitted_value,
            "expected": expected_value,
            "correct": is_correct
        }

    # Calculate overall score percentage
    results["overall_score"] = round((correct_count / total_metrics) * 100, 2)

    return results

def save_results(results, output_filepath):
    """Saves the evaluation results to a JSON file."""
    try:
        with open(output_filepath, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to {output_filepath}")
    except IOError as e:
        print(f"Error: Could not write results to {output_filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while saving results: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to parse arguments, run evaluation, and save results."""
    parser = argparse.ArgumentParser(description="Evaluate Logistics Analyst practical exam submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")

    args = parser.parse_args()

    output_filename = "test_results.json"

    print(f"Loading submission file: {args.submission_file}")
    submission_data = load_json_file(args.submission_file)

    print(f"Loading answer key file: {args.answer_key_file}")
    answer_key_data = load_json_file(args.answer_key_file)

    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_data, answer_key_data)

    save_results(evaluation_results, output_filename)

if __name__ == "__main__":
    main()