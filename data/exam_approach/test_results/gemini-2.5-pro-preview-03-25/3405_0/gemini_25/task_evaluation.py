import json
import argparse
import sys
import os
from decimal import Decimal, InvalidOperation

# Define the maximum possible points for scoring
TOTAL_POSSIBLE_POINTS = 100

# Define points allocation for different checks
POINTS_ALLOCATION = {
    "valid_json": 5,
    "correct_structure": 15, # Includes top-level keys, array types, breakdown item structure
    "correct_data_types_monetary": 15, # Checks all cost fields are numbers
    "total_cost_correct": 20,
    "venue_cost_correct": 15, # Key decision check
    "admin_cost_correct": 15, # Complex calculation check
    "instructor_cost_correct": 5,
    "materials_cost_correct": 5,
    "refreshments_cost_correct": 5,
}

# Ensure the sum of points equals TOTAL_POSSIBLE_POINTS
assert sum(POINTS_ALLOCATION.values()) == TOTAL_POSSIBLE_POINTS, \
    f"Points allocation ({sum(POINTS_ALLOCATION.values())}) does not match TOTAL_POSSIBLE_POINTS ({TOTAL_POSSIBLE_POINTS})"

def format_decimal(value):
    """Convert value to Decimal with two decimal places."""
    try:
        # Handle potential strings like "$150.00" if needed, though spec says numbers
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').strip()
        # Use Decimal for precision
        dec_value = Decimal(value)
        # Ensure two decimal places
        return dec_value.quantize(Decimal("0.00"))
    except (InvalidOperation, TypeError, ValueError):
        return None # Indicate conversion failure

def compare_costs(submitted_cost, key_cost):
    """Compares two cost values after formatting to Decimal(0.00)."""
    sub_decimal = format_decimal(submitted_cost)
    key_decimal = format_decimal(key_cost)

    if sub_decimal is None:
        return False # Submitted value wasn't a valid number

    # Direct comparison should be safe with Decimal
    return sub_decimal == key_decimal

def evaluate_submission(submission_data, key_data):
    """Evaluates the candidate's submission against the answer key."""
    results = {
        "checks": {},
        "achieved_points": 0,
        "overall_score": 0.0,
        "feedback": []
    }
    achieved_points = 0

    # --- Basic Structure and Data Type Checks ---

    # 1. Valid JSON check (already passed if submission_data is loaded)
    achieved_points += POINTS_ALLOCATION["valid_json"]
    results["checks"]["valid_json"] = {
        "passed": True,
        "points": POINTS_ALLOCATION["valid_json"],
        "message": "Submission is valid JSON."
    }

    # 2. Correct Structure Check
    structure_passed = True
    structure_points = 0
    structure_feedback = []
    required_keys = ["exam_id", "program_name", "total_estimated_cost", "cost_breakdown", "notes_or_assumptions"]
    missing_keys = [key for key in required_keys if key not in submission_data]

    if missing_keys:
        structure_passed = False
        structure_feedback.append(f"Missing required top-level keys: {', '.join(missing_keys)}")
    else:
        if not isinstance(submission_data.get("cost_breakdown"), list):
            structure_passed = False
            structure_feedback.append("'cost_breakdown' should be an array/list.")
        else:
            # Check structure of items within cost_breakdown
            required_item_keys = ["category", "estimated_cost", "calculation_basis"]
            for i, item in enumerate(submission_data["cost_breakdown"]):
                if not isinstance(item, dict):
                    structure_passed = False
                    structure_feedback.append(f"Item {i} in 'cost_breakdown' is not an object/dictionary.")
                    break # Stop checking items if one is fundamentally wrong type
                missing_item_keys = [key for key in required_item_keys if key not in item]
                if missing_item_keys:
                    structure_passed = False
                    structure_feedback.append(f"Item {i} in 'cost_breakdown' is missing keys: {', '.join(missing_item_keys)}")

        if not isinstance(submission_data.get("notes_or_assumptions"), list):
            structure_passed = False
            structure_feedback.append("'notes_or_assumptions' should be an array/list.")

    if structure_passed:
        structure_points = POINTS_ALLOCATION["correct_structure"]
        structure_feedback.append("Core JSON structure is correct.")
    else:
        structure_feedback.append("JSON structure has errors.")

    achieved_points += structure_points
    results["checks"]["correct_structure"] = {
        "passed": structure_passed,
        "points": structure_points,
        "message": " ".join(structure_feedback)
    }
    results["feedback"].extend(structure_feedback[:-1]) # Add detailed errors if any

    # If basic structure is wrong, further checks might fail or be unreliable
    if not structure_passed:
        results["feedback"].append("Further checks may be inaccurate due to structural errors.")
        # We can decide to stop here or try to continue cautiously

    # 3. Correct Data Types (Monetary) Check
    # Only proceed if structure allows safe access
    monetary_types_passed = True
    monetary_points = 0
    monetary_feedback = []
    if structure_passed: # Check only if basic structure seems okay
        # Check total_estimated_cost type
        total_cost_val = submission_data.get("total_estimated_cost")
        if not isinstance(total_cost_val, (int, float)):
             # Allow strings only if they can be perfectly converted to Decimal
            if format_decimal(total_cost_val) is None:
                monetary_types_passed = False
                monetary_feedback.append("'total_estimated_cost' is not a valid number.")

        # Check estimated_cost types in breakdown
        for i, item in enumerate(submission_data.get("cost_breakdown", [])):
             # Check if item is a dict before accessing keys
            if isinstance(item, dict):
                cost_val = item.get("estimated_cost")
                category = item.get("category", f"Item {i}")
                if not isinstance(cost_val, (int, float)):
                    if format_decimal(cost_val) is None:
                        monetary_types_passed = False
                        monetary_feedback.append(f"'estimated_cost' for '{category}' is not a valid number.")
            else:
                 # This case was already caught by structure check, but double-check
                 monetary_types_passed = False
                 monetary_feedback.append(f"Item {i} in 'cost_breakdown' is not a dictionary, cannot check 'estimated_cost' type.")


        if monetary_types_passed:
            monetary_points = POINTS_ALLOCATION["correct_data_types_monetary"]
            monetary_feedback.append("All monetary fields have correct numeric data types.")
        else:
            monetary_feedback.append("One or more monetary fields have incorrect data types (must be numbers).")

    else: # Structure failed, cannot reliably check types
        monetary_types_passed = False
        monetary_feedback.append("Cannot check monetary data types due to structural errors.")

    achieved_points += monetary_points
    results["checks"]["correct_data_types_monetary"] = {
        "passed": monetary_types_passed,
        "points": monetary_points,
        "message": " ".join(monetary_feedback)
    }
    results["feedback"].extend(monetary_feedback[:-1])

    # --- Content Accuracy Checks ---
    # Only proceed if structure allows safe access

    submitted_breakdown = {item.get('category'): item for item in submission_data.get('cost_breakdown', []) if isinstance(item, dict)}
    key_breakdown = {item['category']: item for item in key_data['cost_breakdown']}

    # 4. Total Estimated Cost
    total_cost_passed = False
    total_cost_points = 0
    if "total_estimated_cost" in submission_data and monetary_types_passed: # Check only if type was okay
        submitted_total = submission_data["total_estimated_cost"]
        key_total = key_data["total_estimated_cost"]
        if compare_costs(submitted_total, key_total):
            total_cost_passed = True
            total_cost_points = POINTS_ALLOCATION["total_cost_correct"]
            total_cost_msg = f"Total estimated cost is correct ({format_decimal(key_total)})."
        else:
            total_cost_msg = f"Total estimated cost is incorrect. Submitted: {format_decimal(submitted_total)}, Expected: {format_decimal(key_total)}."
            results["feedback"].append(total_cost_msg)
    else:
        total_cost_msg = "Cannot check total estimated cost due to missing key or incorrect data type."
        results["feedback"].append(total_cost_msg)

    achieved_points += total_cost_points
    results["checks"]["total_cost_correct"] = {
        "passed": total_cost_passed,
        "points": total_cost_points,
        "message": total_cost_msg
    }

    # 5. Individual Category Cost Checks
    categories_to_check = [
        ("Venue Rental", "venue_cost_correct"),
        ("Admin Support", "admin_cost_correct"),
        ("Instructor Fees", "instructor_cost_correct"),
        ("Training Materials", "materials_cost_correct"),
        ("Refreshments", "refreshments_cost_correct"),
    ]

    for category_name, check_key in categories_to_check:
        category_passed = False
        category_points = 0
        category_msg = f"Cannot check '{category_name}' cost." # Default message

        submitted_item = submitted_breakdown.get(category_name)
        key_item = key_breakdown.get(category_name)

        if submitted_item and key_item and monetary_types_passed: # Check only if category exists and types were okay
            submitted_cost = submitted_item.get("estimated_cost")
            key_cost = key_item["estimated_cost"]

            if compare_costs(submitted_cost, key_cost):
                category_passed = True
                category_points = POINTS_ALLOCATION[check_key]
                category_msg = f"'{category_name}' cost is correct ({format_decimal(key_cost)})."
            else:
                category_msg = f"'{category_name}' cost is incorrect. Submitted: {format_decimal(submitted_cost)}, Expected: {format_decimal(key_cost)}."
                results["feedback"].append(category_msg)
        elif not submitted_item:
             category_msg = f"Category '{category_name}' not found or item structure incorrect in submission."
             results["feedback"].append(category_msg)
        elif not monetary_types_passed:
             category_msg = f"Cannot accurately check '{category_name}' cost due to data type errors."
             # Feedback already added in type check section

        achieved_points += category_points
        results["checks"][check_key] = {
            "passed": category_passed,
            "points": category_points,
            "message": category_msg
        }

    # --- Final Score Calculation ---
    results["achieved_points"] = achieved_points
    results["overall_score"] = round((achieved_points / TOTAL_POSSIBLE_POINTS) * 100, 2) if TOTAL_POSSIBLE_POINTS > 0 else 0

    # Add overall feedback message
    if results["overall_score"] == 100:
        results["feedback"].insert(0, "Excellent! All checks passed.")
    elif results["overall_score"] >= 70: # Example threshold for good performance
         results["feedback"].insert(0, "Good performance, most checks passed.")
    else:
         results["feedback"].insert(0, "Submission requires improvement. See specific feedback messages.")


    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluate Budget Analyst Basic Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")
    args = parser.parse_args()

    submission_path = args.submission_file
    key_path = args.key_file
    results_path = "test_results.json"

    # --- Load Submission File ---
    try:
        with open(submission_path, 'r', encoding='utf-8') as f:
            submission_data = json.load(f)
        print(f"Successfully loaded submission file: {submission_path}")
    except FileNotFoundError:
        print(f"Error: Submission file not found at {submission_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in submission file {submission_path}. {e}", file=sys.stderr)
        # Create a basic result file indicating the JSON error
        error_result = {
            "checks": {"valid_json": {"passed": False, "points": 0, "message": f"Invalid JSON: {e}"}},
            "achieved_points": 0,
            "overall_score": 0.0,
            "feedback": [f"Submission file '{submission_path}' is not valid JSON and could not be parsed."]
        }
        with open(results_path, 'w', encoding='utf-8') as f_res:
            json.dump(error_result, f_res, indent=2)
        print(f"Evaluation results saved to {results_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading {submission_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Load Answer Key File ---
    try:
        with open(key_path, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
        print(f"Successfully loaded answer key file: {key_path}")
    except FileNotFoundError:
        print(f"Error: Answer key file not found at {key_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in answer key file {key_path}. {e}", file=sys.stderr)
        sys.exit(1) # Cannot evaluate without a valid key
    except Exception as e:
        print(f"An unexpected error occurred while reading {key_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Perform Evaluation ---
    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_data, key_data)
    print("Evaluation complete.")

    # --- Save Results ---
    try:
        with open(results_path, 'w', encoding='utf-8') as f_res:
            json.dump(evaluation_results, f_res, indent=2)
        print(f"Evaluation results saved to {results_path}")
    except IOError as e:
        print(f"Error: Could not write results to {results_path}. {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while writing results: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()