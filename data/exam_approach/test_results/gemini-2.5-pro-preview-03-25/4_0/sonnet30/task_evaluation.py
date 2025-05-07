import json
import sys
import os
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

# --- Configuration ---
OUTPUT_FILENAME = "test_results.json"
EXPECTED_BASE_PRICE_COUNT = 10
EXPECTED_VOLUME_SCENARIO_COUNT = 3
EXPECTED_CUSTOMER_SCENARIO_COUNT = 3
REQUIRED_TOP_LEVEL_KEYS = [
    "candidate_id",
    "base_prices",
    "volume_discount_scenarios",
    "customer_discount_scenarios",
]
REQUIRED_BASE_PRICE_KEYS = ["product_id", "base_price"]
REQUIRED_VOLUME_KEYS = [
    "order_id",
    "product_id",
    "quantity",
    "final_unit_price_volume_discount",
]
REQUIRED_CUSTOMER_KEYS = [
    "order_id",
    "product_id",
    "customer_type",
    "final_unit_price_customer_discount",
]

# --- Helper Functions ---

def load_json(filepath):
    """Loads a JSON file with error handling."""
    if not os.path.exists(filepath):
        return None, f"Error: File not found at '{filepath}'"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON format in '{filepath}'. Details: {e}"
    except Exception as e:
        return None, f"Error: Could not read file '{filepath}'. Details: {e}"

def safe_round(value):
    """Safely rounds a value to 2 decimal places using Decimal for accuracy."""
    try:
        # Convert potential floats or strings representing numbers to Decimal
        dec_value = Decimal(str(value))
        # Round to 2 decimal places, rounding halves up (standard rounding)
        return dec_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        # Handle cases where value is not a number (e.g., None, non-numeric string)
        return None

def compare_values(actual, expected, context, results, points_possible, points_achieved):
    """Compares a single value, updates results and points."""
    is_correct = False
    details = {"expected": expected, "actual": actual}

    # Handle numeric comparison with rounding
    if isinstance(expected, (int, float, Decimal)):
        actual_rounded = safe_round(actual)
        expected_rounded = safe_round(expected) # Should already be correct in key, but round for safety
        if actual_rounded is not None and expected_rounded is not None and actual_rounded == expected_rounded:
            is_correct = True
            # Store the rounded value for clarity in results if correct
            details["actual_rounded"] = float(actual_rounded) # Convert back to float for JSON
            details["expected_rounded"] = float(expected_rounded)
        elif actual_rounded is None:
             details["error"] = "Actual value is not a valid number or could not be rounded."
        else:
             details["error"] = f"Numeric mismatch (Expected rounded: {expected_rounded}, Actual rounded: {actual_rounded})"

    # Handle string comparison (case-sensitive)
    elif isinstance(expected, str):
        if isinstance(actual, str) and actual == expected:
            is_correct = True
        elif not isinstance(actual, str):
            details["error"] = f"Type mismatch: Expected string, got {type(actual).__name__}"
        else:
            details["error"] = "String mismatch"

    # Handle integer comparison (specifically for quantity)
    elif isinstance(expected, int):
         try:
             if int(actual) == expected:
                 is_correct = True
             else:
                 details["error"] = "Integer mismatch"
         except (ValueError, TypeError):
             details["error"] = f"Type mismatch or invalid integer: Expected integer, got {type(actual).__name__} ('{actual}')"

    else:
        # Fallback for other types if needed, though not expected here
        if actual == expected:
            is_correct = True
        else:
            details["error"] = f"Mismatch for type {type(expected).__name__}"


    results[context] = {"correct": is_correct, "details": details}
    points_possible[0] += 1
    if is_correct:
        points_achieved[0] += 1

# --- Main Evaluation Logic ---

def evaluate_submission(submission_path, answer_key_path):
    """Loads submission and key, performs evaluation, returns results."""

    submission_data, error = load_json(submission_path)
    if error:
        return {"error": error, "overall_score": 0, "evaluation_details": {}}

    answer_key_data, error = load_json(answer_key_path)
    if error:
        # If the key is broken, we can't evaluate
        return {"error": f"CRITICAL: {error}", "overall_score": 0, "evaluation_details": {}}

    results = {
        "candidate_id_submission": submission_data.get("candidate_id", "MISSING"),
        "file_validation": {"errors": [], "warnings": []},
        "structure_check": {},
        "base_price_check": {},
        "volume_scenario_check": {},
        "customer_scenario_check": {},
    }
    points_achieved = [0] # Use list to pass by reference
    points_possible = [0] # Use list to pass by reference

    # 1. File Validation & Basic Structure Check
    # ------------------------------------------
    valid_structure = True
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in submission_data:
            results["file_validation"]["errors"].append(f"Missing required top-level key: '{key}'")
            valid_structure = False
        elif key.endswith("_prices") or key.endswith("_scenarios"):
             if not isinstance(submission_data[key], list):
                 results["file_validation"]["errors"].append(f"Key '{key}' should be a list, but found {type(submission_data[key]).__name__}")
                 valid_structure = False

    if not valid_structure:
        results["error"] = "Submission failed basic structure validation. Cannot proceed with detailed checks."
        results["overall_score"] = 0
        return results

    # Check array lengths
    bp_len = len(submission_data.get("base_prices", []))
    vol_len = len(submission_data.get("volume_discount_scenarios", []))
    cust_len = len(submission_data.get("customer_discount_scenarios", []))

    results["structure_check"]["base_prices_count"] = {"actual": bp_len, "expected": EXPECTED_BASE_PRICE_COUNT, "correct": bp_len == EXPECTED_BASE_PRICE_COUNT}
    results["structure_check"]["volume_scenarios_count"] = {"actual": vol_len, "expected": EXPECTED_VOLUME_SCENARIO_COUNT, "correct": vol_len == EXPECTED_VOLUME_SCENARIO_COUNT}
    results["structure_check"]["customer_scenarios_count"] = {"actual": cust_len, "expected": EXPECTED_CUSTOMER_SCENARIO_COUNT, "correct": cust_len == EXPECTED_CUSTOMER_SCENARIO_COUNT}

    if not results["structure_check"]["base_prices_count"]["correct"]:
        results["file_validation"]["warnings"].append(f"Incorrect number of base price entries found.")
    if not results["structure_check"]["volume_scenarios_count"]["correct"]:
         results["file_validation"]["warnings"].append(f"Incorrect number of volume scenario entries found.")
    if not results["structure_check"]["customer_scenarios_count"]["correct"]:
         results["file_validation"]["warnings"].append(f"Incorrect number of customer scenario entries found.")


    # 2. Detailed Checks (Proceed even with count warnings, but check item existence)
    # -----------------------------------------------------------------------------

    # Convert lists to dicts for easier lookup (handle potential duplicates by taking the last one)
    key_base_prices = {item['product_id']: item for item in answer_key_data.get("base_prices", [])}
    sub_base_prices = {item.get('product_id'): item for item in submission_data.get("base_prices", []) if isinstance(item, dict)}

    key_volume_scenarios = {item['order_id']: item for item in answer_key_data.get("volume_discount_scenarios", [])}
    sub_volume_scenarios = {item.get('order_id'): item for item in submission_data.get("volume_discount_scenarios", []) if isinstance(item, dict)}

    key_customer_scenarios = {item['order_id']: item for item in answer_key_data.get("customer_discount_scenarios", [])}
    sub_customer_scenarios = {item.get('order_id'): item for item in submission_data.get("customer_discount_scenarios", []) if isinstance(item, dict)}

    # --- Base Price Check ---
    results["base_price_check"]["items"] = {}
    for prod_id, key_item in key_base_prices.items():
        item_results = {}
        sub_item = sub_base_prices.get(prod_id)

        if sub_item and isinstance(sub_item, dict):
             # Check required keys exist in submission item
             missing_keys = [k for k in REQUIRED_BASE_PRICE_KEYS if k not in sub_item]
             if missing_keys:
                 item_results["structure_error"] = f"Missing keys in submission item: {missing_keys}"
                 points_possible[0] += len(REQUIRED_BASE_PRICE_KEYS) # Increment possible points even if structure fails
             else:
                # Compare product_id (should always match if found by key)
                compare_values(sub_item['product_id'], key_item['product_id'], 'product_id_check', item_results, points_possible, points_achieved)
                # Compare base_price
                compare_values(sub_item['base_price'], key_item['base_price'], 'base_price_check', item_results, points_possible, points_achieved)
        else:
            item_results["error"] = "Product ID not found in submission or item is not a valid dictionary."
            points_possible[0] += len(REQUIRED_BASE_PRICE_KEYS) # Increment possible points even if missing

        results["base_price_check"]["items"][prod_id] = item_results

    # --- Volume Scenario Check ---
    results["volume_scenario_check"]["items"] = {}
    for order_id, key_item in key_volume_scenarios.items():
        item_results = {}
        sub_item = sub_volume_scenarios.get(order_id)

        if sub_item and isinstance(sub_item, dict):
            missing_keys = [k for k in REQUIRED_VOLUME_KEYS if k not in sub_item]
            if missing_keys:
                 item_results["structure_error"] = f"Missing keys in submission item: {missing_keys}"
                 points_possible[0] += len(REQUIRED_VOLUME_KEYS)
            else:
                compare_values(sub_item['order_id'], key_item['order_id'], 'order_id_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['product_id'], key_item['product_id'], 'product_id_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['quantity'], key_item['quantity'], 'quantity_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['final_unit_price_volume_discount'], key_item['final_unit_price_volume_discount'], 'price_check', item_results, points_possible, points_achieved)
        else:
            item_results["error"] = "Order ID not found in submission or item is not a valid dictionary."
            points_possible[0] += len(REQUIRED_VOLUME_KEYS)

        results["volume_scenario_check"]["items"][order_id] = item_results

    # --- Customer Scenario Check ---
    results["customer_scenario_check"]["items"] = {}
    for order_id, key_item in key_customer_scenarios.items():
        item_results = {}
        sub_item = sub_customer_scenarios.get(order_id)

        if sub_item and isinstance(sub_item, dict):
            missing_keys = [k for k in REQUIRED_CUSTOMER_KEYS if k not in sub_item]
            if missing_keys:
                 item_results["structure_error"] = f"Missing keys in submission item: {missing_keys}"
                 points_possible[0] += len(REQUIRED_CUSTOMER_KEYS)
            else:
                compare_values(sub_item['order_id'], key_item['order_id'], 'order_id_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['product_id'], key_item['product_id'], 'product_id_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['customer_type'], key_item['customer_type'], 'customer_type_check', item_results, points_possible, points_achieved)
                compare_values(sub_item['final_unit_price_customer_discount'], key_item['final_unit_price_customer_discount'], 'price_check', item_results, points_possible, points_achieved)
        else:
            item_results["error"] = "Order ID not found in submission or item is not a valid dictionary."
            points_possible[0] += len(REQUIRED_CUSTOMER_KEYS)

        results["customer_scenario_check"]["items"][order_id] = item_results

    # 3. Calculate Final Score
    # ------------------------
    total_possible = points_possible[0]
    total_achieved = points_achieved[0]

    if total_possible > 0:
        overall_score_percent = round((total_achieved / total_possible) * 100, 2)
    else:
        overall_score_percent = 0 # Avoid division by zero if no points were possible (e.g., broken key)

    results["score_summary"] = {
        "points_achieved": total_achieved,
        "points_possible": total_possible,
    }
    results["overall_score"] = overall_score_percent # Add the required overall_score variable

    return results

# --- Script Execution ---

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file.json> <answer_key_file.json>")
        sys.exit(1)

    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]

    print(f"Evaluating '{submission_file}' against '{answer_key_file}'...")

    evaluation_results = evaluate_submission(submission_file, answer_key_file)

    # Ensure results are serializable (convert Decimals back to floats if any remain)
    # Although safe_round returns Decimal, compare_values stores float representations
    # This is more of a safeguard.
    def default_serializer(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=4, default=default_serializer)
        print(f"Evaluation complete. Results saved to '{OUTPUT_FILENAME}'")
        # Optionally print the score to console
        if "overall_score" in evaluation_results:
             print(f"Overall Score: {evaluation_results['overall_score']}%")
        if evaluation_results.get("error"):
            print(f"Evaluation Error: {evaluation_results['error']}")

    except Exception as e:
        print(f"Error: Could not write results to '{OUTPUT_FILENAME}'. Details: {e}")
        # Print results to console as a fallback
        print("\n--- Evaluation Results (Fallback Console Output) ---")
        try:
            print(json.dumps(evaluation_results, indent=4, default=default_serializer))
        except Exception as json_e:
             print(f"Could not even serialize results for console output: {json_e}")
             print(evaluation_results) # Raw print if serialization fails
        print("--- End Fallback Console Output ---")
        sys.exit(1)

    sys.exit(0)