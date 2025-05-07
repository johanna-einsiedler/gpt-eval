import json
import argparse
import sys
import os
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

# Define the expected structure and keys based on the answer key format
EXPECTED_TOP_LEVEL_KEY = "exam_submission"
EXPECTED_SUBMISSION_KEYS = ["candidate_id", "exam_part", "budget_data"]
EXPECTED_BUDGET_DATA_KEYS = ["q2_actual_costs", "q3_budgeted_costs"]
EXPECTED_COST_KEYS = [
    "fuel",
    "warehouse_labour",
    "driver_labour",
    "vehicle_maintenance",
    "packaging_materials",
    "warehouse_lease",
    "utilities",
    # Totals are also compared numerically
    "total_q2_actual",
    "total_q3_budget"
]
# Separate keys for easier iteration
Q2_COST_KEYS = [
    "fuel", "warehouse_labour", "driver_labour", "vehicle_maintenance",
    "packaging_materials", "warehouse_lease", "utilities", "total_q2_actual"
]
Q3_COST_KEYS = [
    "fuel", "warehouse_labour", "driver_labour", "vehicle_maintenance",
    "packaging_materials", "warehouse_lease", "utilities", "total_q3_budget"
]

# Placeholder IDs to check against
PLACEHOLDER_IDS = ["CANDIDATE_ID_PLACEHOLDER", "YOUR_ID_HERE"]

def load_json_file(filepath):
    """Loads a JSON file and returns the data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read file {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)

def validate_structure(data, results):
    """Validates the basic structure of the submission JSON."""
    valid = True
    structure_checks = []

    if EXPECTED_TOP_LEVEL_KEY not in data:
        structure_checks.append({"check": "Top level key 'exam_submission'", "status": "FAIL", "detail": "Missing"})
        return False, structure_checks # Cannot proceed if top level is missing

    submission_data = data[EXPECTED_TOP_LEVEL_KEY]
    structure_checks.append({"check": "Top level key 'exam_submission'", "status": "PASS"})

    for key in EXPECTED_SUBMISSION_KEYS:
        if key not in submission_data:
            structure_checks.append({"check": f"Key '{key}' in 'exam_submission'", "status": "FAIL", "detail": "Missing"})
            valid = False
        else:
            structure_checks.append({"check": f"Key '{key}' in 'exam_submission'", "status": "PASS"})

    if "budget_data" in submission_data and isinstance(submission_data["budget_data"], dict):
        budget_data = submission_data["budget_data"]
        for key in EXPECTED_BUDGET_DATA_KEYS:
             if key not in budget_data:
                 structure_checks.append({"check": f"Key '{key}' in 'budget_data'", "status": "FAIL", "detail": "Missing"})
                 valid = False
             else:
                 structure_checks.append({"check": f"Key '{key}' in 'budget_data'", "status": "PASS"})

             # Check nested cost keys only if the parent key exists
             if key in budget_data and isinstance(budget_data[key], dict):
                 cost_keys_to_check = Q2_COST_KEYS if key == "q2_actual_costs" else Q3_COST_KEYS
                 nested_dict = budget_data[key]
                 for cost_key in cost_keys_to_check:
                     if cost_key not in nested_dict:
                         structure_checks.append({"check": f"Key '{cost_key}' in '{key}'", "status": "FAIL", "detail": "Missing"})
                         valid = False
                     else:
                         structure_checks.append({"check": f"Key '{cost_key}' in '{key}'", "status": "PASS"})
             elif key in budget_data: # Parent key exists but is not a dict
                 structure_checks.append({"check": f"Structure of '{key}'", "status": "FAIL", "detail": f"Expected a dictionary, found {type(budget_data[key]).__name__}"})
                 valid = False

    elif "budget_data" in submission_data: # budget_data exists but is not a dict
        structure_checks.append({"check": "Structure of 'budget_data'", "status": "FAIL", "detail": f"Expected a dictionary, found {type(submission_data['budget_data']).__name__}"})
        valid = False
    # else: budget_data missing check already added

    results["structure_checks"] = structure_checks
    return valid, structure_checks

def validate_format(data, results):
    """Validates specific formatting rules (candidate ID, exam part, numeric types)."""
    if not results.get("structure_valid", False):
         results["format_checks"] = [{"check": "Overall Format", "status": "SKIPPED", "detail": "Skipped due to structure errors."}]
         return False # Cannot validate format if structure is invalid

    valid = True
    format_checks = []
    submission_data = data[EXPECTED_TOP_LEVEL_KEY]

    # Check candidate_id
    candidate_id = submission_data.get("candidate_id", "")
    if not candidate_id or candidate_id in PLACEHOLDER_IDS:
        format_checks.append({"check": "Candidate ID populated", "status": "FAIL", "detail": f"ID is missing or placeholder ('{candidate_id}')"})
        valid = False
    else:
        format_checks.append({"check": "Candidate ID populated", "status": "PASS", "value": candidate_id})

    # Check exam_part
    exam_part = submission_data.get("exam_part", "")
    if exam_part != "basic_budgeting":
        format_checks.append({"check": "Exam Part value", "status": "FAIL", "detail": f"Expected 'basic_budgeting', found '{exam_part}'"})
        valid = False
    else:
        format_checks.append({"check": "Exam Part value", "status": "PASS"})

    # Check numeric types for cost values
    budget_data = submission_data["budget_data"]
    all_numeric_keys = Q2_COST_KEYS + Q3_COST_KEYS
    unique_keys = list(dict.fromkeys(all_numeric_keys)) # Ensure unique keys like 'fuel' are checked once per section

    for section_key in EXPECTED_BUDGET_DATA_KEYS:
        if section_key in budget_data and isinstance(budget_data[section_key], dict):
            section_data = budget_data[section_key]
            keys_in_section = Q2_COST_KEYS if section_key == "q2_actual_costs" else Q3_COST_KEYS
            for cost_key in keys_in_section:
                if cost_key in section_data:
                    value = section_data[cost_key]
                    if not isinstance(value, (int, float)):
                        format_checks.append({"check": f"Data type for '{section_key}.{cost_key}'", "status": "FAIL", "detail": f"Expected Number (int/float), found {type(value).__name__}"})
                        valid = False
                    else:
                         format_checks.append({"check": f"Data type for '{section_key}.{cost_key}'", "status": "PASS"})
                # else: Missing key already handled by structure check

    results["format_checks"] = format_checks
    return valid

def compare_values(submission_data, key_data, results):
    """Compares the numerical values between submission and key, rounding to 2 decimal places."""
    if not results.get("structure_valid", False) or not results.get("format_valid", False):
        results["value_comparison"] = {"status": "SKIPPED", "detail": "Skipped due to structure or format errors."}
        return 0, 0 # No points awarded

    comparisons = []
    correct_count = 0
    total_possible = 0

    sub_budget = submission_data[EXPECTED_TOP_LEVEL_KEY]["budget_data"]
    key_budget = key_data[EXPECTED_TOP_LEVEL_KEY]["budget_data"]

    # Use Decimal for precise rounding
    quantize_format = Decimal("0.00")

    for section_key in EXPECTED_BUDGET_DATA_KEYS:
        if section_key in sub_budget and section_key in key_budget:
            sub_section = sub_budget[section_key]
            key_section = key_budget[section_key]
            keys_in_section = Q2_COST_KEYS if section_key == "q2_actual_costs" else Q3_COST_KEYS

            for cost_key in keys_in_section:
                total_possible += 1
                comparison_result = {
                    "key": f"{section_key}.{cost_key}",
                    "expected": None,
                    "actual": None,
                    "correct": False
                }

                key_value = key_section.get(cost_key)
                sub_value = sub_section.get(cost_key)

                # Store expected value regardless of submission
                if key_value is not None:
                     try:
                         comparison_result["expected"] = float(Decimal(str(key_value)).quantize(quantize_format, rounding=ROUND_HALF_UP))
                     except (TypeError, ValueError, InvalidOperation):
                         comparison_result["expected"] = f"Invalid Key Value ({key_value})"


                if sub_value is None:
                    comparison_result["detail"] = "Value missing in submission"
                elif not isinstance(sub_value, (int, float)):
                     comparison_result["detail"] = f"Invalid data type in submission: {type(sub_value).__name__}"
                     comparison_result["actual"] = str(sub_value) # Store the incorrect value as string
                else:
                    try:
                        # Round both submission and key values to 2 decimal places using Decimal for accuracy
                        sub_decimal = Decimal(str(sub_value)).quantize(quantize_format, rounding=ROUND_HALF_UP)
                        key_decimal = Decimal(str(key_value)).quantize(quantize_format, rounding=ROUND_HALF_UP)

                        comparison_result["actual"] = float(sub_decimal) # Store rounded float value

                        if sub_decimal == key_decimal:
                            comparison_result["correct"] = True
                            correct_count += 1
                        else:
                            comparison_result["detail"] = "Value mismatch"

                    except (TypeError, ValueError, InvalidOperation) as e:
                         comparison_result["detail"] = f"Error processing submission value: {e}"
                         comparison_result["actual"] = str(sub_value) # Store the problematic value

                comparisons.append(comparison_result)
        else:
             # Handle case where whole section (q2/q3) might be missing - structure check should catch this
             keys_in_section = Q2_COST_KEYS if section_key == "q2_actual_costs" else Q3_COST_KEYS
             total_possible += len(keys_in_section) # Add expected points for the section
             comparisons.append({
                 "key": section_key,
                 "expected": "Section Data",
                 "actual": "Section Missing/Invalid",
                 "correct": False,
                 "detail": f"Section '{section_key}' missing or invalid in submission."
             })


    results["value_comparison"] = comparisons
    results["correct_count"] = correct_count
    results["total_possible"] = total_possible

    return correct_count, total_possible


def main():
    parser = argparse.ArgumentParser(description="Evaluate TSD Manager Basic Budgeting Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    submission_data = load_json_file(args.submission_file)
    key_data = load_json_file(args.key_file)

    results = {
        "submission_file": args.submission_file,
        "key_file": args.key_file,
        "structure_valid": False,
        "format_valid": False,
        "structure_checks": [],
        "format_checks": [],
        "value_comparison": [],
        "correct_count": 0,
        "total_possible": 0,
        "overall_score": 0.0
    }

    # 1. Validate Structure
    structure_valid, _ = validate_structure(submission_data, results)
    results["structure_valid"] = structure_valid

    # 2. Validate Format (only if structure is valid)
    format_valid = False
    if structure_valid:
        format_valid = validate_format(submission_data, results)
        results["format_valid"] = format_valid

    # 3. Compare Values (only if structure and format are valid)
    correct_count, total_possible = compare_values(submission_data, key_data, results)

    # 4. Calculate Overall Score
    if total_possible > 0:
        overall_score = round((correct_count / total_possible) * 100, 2)
        results["overall_score"] = overall_score
    else:
        # Handle case where key might be malformed leading to 0 possible points
         results["overall_score"] = 0.0
         if not results.get("value_comparison"): # Add note if comparison was skipped
             results["value_comparison"] = {"status": "ERROR", "detail": "Evaluation error or invalid key prevented comparison."}


    # 5. Save Results
    output_filename = "test_results.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation complete. Results saved to {output_filename}")
    except IOError as e:
        print(f"Error: Could not write results to {output_filename}. Details: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during result saving: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()