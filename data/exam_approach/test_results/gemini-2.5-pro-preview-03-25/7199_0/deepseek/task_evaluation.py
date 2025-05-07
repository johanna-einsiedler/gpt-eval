import json
import argparse
import sys
import os
from typing import Dict, Any, List, Optional, Tuple

def compare_findings(finding1: Dict[str, Any], finding2: Dict[str, Any]) -> bool:
    """
    Compares two finding objects based on key fields.

    Args:
        finding1: The first finding dictionary.
        finding2: The second finding dictionary.

    Returns:
        True if the findings are considered a match, False otherwise.
    """
    # Define the keys to compare for a match
    # We focus on the core identifiers of the finding. Description is often
    # too variable for reliable automated exact matching in a basic script.
    keys_to_match = [
        "task_ref",
        "document_reviewed",
        "location_details",
        "finding_type",
        "compared_document" # Handles None/null correctly via .get()
    ]

    for key in keys_to_match:
        # Use .get() to avoid KeyError and handle missing keys gracefully
        # (treating missing as None, which matches JSON null)
        if finding1.get(key) != finding2.get(key):
            return False
    return True

def evaluate_submission(submission_data: Dict[str, Any], answer_key_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates the candidate's submission against the answer key.

    Args:
        submission_data: Parsed JSON data from the candidate's submission file.
        answer_key_data: Parsed JSON data from the answer key file.

    Returns:
        A dictionary containing the detailed evaluation results and overall score.
    """
    results: Dict[str, Any] = {
        "candidate_id": submission_data.get("candidate_id", "N/A"),
        "exam_level": submission_data.get("exam_level", "N/A"),
        "overall_score": 0.0,
        "total_possible_findings": 0,
        "correctly_identified_findings": 0,
        "missed_findings_count": 0,
        "extra_findings_count": 0,
        "matched_findings": [],
        "missed_findings": [],
        "extra_findings": []
    }

    candidate_findings: List[Dict[str, Any]] = submission_data.get("findings", [])
    key_findings: List[Dict[str, Any]] = answer_key_data.get("findings", [])

    results["total_possible_findings"] = len(key_findings)

    if not key_findings:
        # No findings in the key, score is 100% if submission is also empty, 0% otherwise
        if not candidate_findings:
            results["overall_score"] = 100.0
        else:
            results["overall_score"] = 0.0
            results["extra_findings"] = candidate_findings
            results["extra_findings_count"] = len(candidate_findings)
        return results

    if not candidate_findings:
        # No findings submitted, score is 0%
        results["overall_score"] = 0.0
        results["missed_findings"] = key_findings
        results["missed_findings_count"] = len(key_findings)
        return results

    # --- Matching Logic ---
    matched_key_indices = set()
    matched_submission_indices = set()

    # Iterate through each answer key finding
    for key_idx, key_finding in enumerate(key_findings):
        # Try to find a match in the candidate's submission
        for sub_idx, sub_finding in enumerate(candidate_findings):
            # Skip submission findings that have already been matched
            if sub_idx in matched_submission_indices:
                continue

            if compare_findings(key_finding, sub_finding):
                # Found a match
                results["matched_findings"].append(sub_finding)
                matched_key_indices.add(key_idx)
                matched_submission_indices.add(sub_idx)
                # Break inner loop once a match is found for the current key_finding
                break

    # Identify missed findings (key findings not matched)
    for key_idx, key_finding in enumerate(key_findings):
        if key_idx not in matched_key_indices:
            results["missed_findings"].append(key_finding)

    # Identify extra findings (submission findings not matched to any key finding)
    for sub_idx, sub_finding in enumerate(candidate_findings):
        if sub_idx not in matched_submission_indices:
            results["extra_findings"].append(sub_finding)

    # --- Calculate Score ---
    results["correctly_identified_findings"] = len(results["matched_findings"])
    results["missed_findings_count"] = len(results["missed_findings"])
    results["extra_findings_count"] = len(results["extra_findings"])

    if results["total_possible_findings"] > 0:
        results["overall_score"] = round(
            (results["correctly_identified_findings"] / results["total_possible_findings"]) * 100,
            2
        )
    elif not results["extra_findings"]: # Handle case where key is empty and submission is empty
         results["overall_score"] = 100.0
    else: # Handle case where key is empty but submission is not
        results["overall_score"] = 0.0


    return results

def main():
    """
    Main function to parse arguments, load files, evaluate, and save results.
    """
    parser = argparse.ArgumentParser(description="Evaluate Gambling Manager Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file.")

    if len(sys.argv) != 3:
        parser.print_help(sys.stderr)
        sys.exit(1)

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
        sys.exit(1)
    except Exception as e:
        print(f"Error reading submission file '{args.submission_file}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.answer_key_file, 'r', encoding='utf-8') as f:
            answer_key_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file not found at '{args.answer_key_file}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in answer key file '{args.answer_key_file}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading answer key file '{args.answer_key_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Validate basic structure ---
    if "findings" not in submission_data or not isinstance(submission_data["findings"], list):
         print(f"Error: Submission file '{args.submission_file}' is missing 'findings' array or it's not a list.", file=sys.stderr)
         # Allow evaluation to proceed but it will likely result in 0 score if key has findings
         submission_data["findings"] = [] # Ensure findings key exists as empty list

    if "findings" not in answer_key_data or not isinstance(answer_key_data["findings"], list):
         print(f"Error: Answer key file '{args.answer_key_file}' is missing 'findings' array or it's not a list.", file=sys.stderr)
         sys.exit(1) # Cannot evaluate without a valid key structure


    # --- Evaluate ---
    evaluation_results = evaluate_submission(submission_data, answer_key_data)

    # --- Save Results ---
    output_filename = "test_results.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
        print(f"Evaluation complete. Results saved to '{output_filename}'")
    except IOError as e:
        print(f"Error: Could not write results to file '{output_filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while writing results: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()