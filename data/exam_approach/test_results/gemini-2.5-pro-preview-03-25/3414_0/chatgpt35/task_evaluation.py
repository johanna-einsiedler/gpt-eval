import json
import argparse
import math

# Tolerances from evaluation criteria
TOLERANCE_MONTHLY_PAYMENT = 0.01
TOLERANCE_TOTAL_INTEREST = 0.05
TOLERANCE_SCHEDULE_INTEREST_PRINCIPAL = 0.01
TOLERANCE_SCHEDULE_BALANCE_REGULAR = 0.02
TOLERANCE_SCHEDULE_BALANCE_LAST_MIN = -0.05
TOLERANCE_SCHEDULE_BALANCE_LAST_MAX = 0.05

TOTAL_POSSIBLE_POINTS = 22
PASSING_THRESHOLD_POINTS = 19

def is_close_custom(val1, val2, tolerance):
    """Checks if val1 is within val2 +/- tolerance. Handles None and type issues."""
    if val1 is None or val2 is None:
        return False
    if not (isinstance(val1, (int, float)) and isinstance(val2, (int, float))):
        return False
    return abs(val1 - val2) <= tolerance

def check_last_balance(val, min_val, max_val):
    """Checks if val is within [min_val, max_val]. Handles None and type issues."""
    if val is None:
        return False
    if not isinstance(val, (int, float)):
        return False
    return min_val <= val <= max_val

def evaluate_submission(submission_data, answer_key_data):
    results = {
        "overall_score_percentage": 0.0,
        "achieved_points": 0,
        "total_possible_points": TOTAL_POSSIBLE_POINTS,
        "pass_status": "FAIL", # Default, will be updated
        "critical_monthly_payment_check": {},
        "evaluation_details": [],
        "structural_warnings": []
    }
    
    achieved_points = 0
    all_critical_monthly_payments_correct = True # Assume true until a failure

    # --- Top-level structural checks on submission ---
    if not isinstance(submission_data, dict):
        results["structural_warnings"].append("Submission is not a valid JSON object.")
        # Cannot proceed if the root is not a dict
        return results # Return early with structural error

    # Check for candidate_id and exam_version (as per submission format)
    if "candidate_id" not in submission_data:
        results["structural_warnings"].append("Submission missing 'candidate_id' field.")
    if submission_data.get("exam_version") != answer_key_data.get("exam_version"): # Compare with key's version
        results["structural_warnings"].append(
            f"Submission 'exam_version' ('{submission_data.get('exam_version')}') "
            f"does not match expected ('{answer_key_data.get('exam_version')}')."
        )

    if not isinstance(submission_data.get("loan_scenarios"), list):
        results["structural_warnings"].append("Submission 'loan_scenarios' is not a list or is missing.")
        # If loan_scenarios is fundamentally broken, further evaluation is difficult.
        # All points effectively lost for loan data.
        all_critical_monthly_payments_correct = False # No scenarios means no correct monthly payments
        # Add placeholders for expected scenarios to show what was missed
        for key_scenario_placeholder in answer_key_data.get("loan_scenarios", []):
            placeholder_loan_id = key_scenario_placeholder.get("loan_id", "UNKNOWN_LOAN_ID")
            results["critical_monthly_payment_check"][placeholder_loan_id] = "FAIL"
            results["evaluation_details"].append({
                "loan_id": placeholder_loan_id,
                "error": "Loan scenario data missing or 'loan_scenarios' is not a list in submission."
            })
        # Update pass status based on current (likely zero) points and critical check
        if achieved_points >= PASSING_THRESHOLD_POINTS and all_critical_monthly_payments_correct:
            results["pass_status"] = "PASS"
        else:
            results["pass_status"] = "FAIL" # Already default, but explicit
            if achieved_points < PASSING_THRESHOLD_POINTS:
                 results["fail_reason_points"] = f"Achieved {achieved_points} points, required {PASSING_THRESHOLD_POINTS}."
            if not all_critical_monthly_payments_correct:
                 results["fail_reason_critical"] = "Critical monthly payments were incorrect or missing due to structural issues."
        return results
    
    # --- Iterate through answer key scenarios to ensure all expected items are checked ---
    for key_scenario in answer_key_data["loan_scenarios"]:
        key_loan_id = key_scenario["loan_id"]
        results["critical_monthly_payment_check"][key_loan_id] = "FAIL" # Default to fail for this loan's critical check

        # Find corresponding submission scenario by loan_id
        sub_scenario = None
        for s_scen in submission_data.get("loan_scenarios", []): # Default to empty list if key missing
            if isinstance(s_scen, dict) and s_scen.get("loan_id") == key_loan_id:
                sub_scenario = s_scen
                break
        
        loan_eval_details = {"loan_id": key_loan_id}
        results["evaluation_details"].append(loan_eval_details)

        if sub_scenario is None:
            results["structural_warnings"].append(f"Loan scenario '{key_loan_id}' missing in submission.")
            all_critical_monthly_payments_correct = False # Missing scenario means its monthly payment is not correct
            loan_eval_details["error"] = "Loan scenario missing in submission."
            # All points for this scenario are lost
            continue # Move to the next key_scenario

        # --- Monthly Payment (Critical) ---
        sub_mp = sub_scenario.get("monthly_payment")
        key_mp = key_scenario["monthly_payment"]
        mp_correct = is_close_custom(sub_mp, key_mp, TOLERANCE_MONTHLY_PAYMENT)
        loan_eval_details["monthly_payment"] = {
            "submitted": sub_mp, "expected": key_mp, "correct": mp_correct, "points": 0
        }
        if not isinstance(sub_mp, (int, float)):
             loan_eval_details["monthly_payment"]["error"] = "Invalid data type for monthly_payment."
             mp_correct = False # Override if type is wrong
             loan_eval_details["monthly_payment"]["correct"] = False
        
        if mp_correct:
            loan_eval_details["monthly_payment"]["points"] = 1
            achieved_points += 1
            results["critical_monthly_payment_check"][key_loan_id] = "PASS"
        else:
            all_critical_monthly_payments_correct = False
            if "error" not in loan_eval_details["monthly_payment"] and sub_mp is not None:
                 loan_eval_details["monthly_payment"]["difference"] = round(sub_mp - key_mp, 4) if isinstance(sub_mp, (int,float)) else "N/A"

        # --- Total Interest Paid ---
        sub_tip = sub_scenario.get("total_interest_paid")
        key_tip = key_scenario["total_interest_paid"]
        tip_correct = is_close_custom(sub_tip, key_tip, TOLERANCE_TOTAL_INTEREST)
        loan_eval_details["total_interest_paid"] = {
            "submitted": sub_tip, "expected": key_tip, "correct": tip_correct, "points": 0
        }
        if not isinstance(sub_tip, (int, float)):
             loan_eval_details["total_interest_paid"]["error"] = "Invalid data type for total_interest_paid."
             tip_correct = False
             loan_eval_details["total_interest_paid"]["correct"] = False

        if tip_correct:
            loan_eval_details["total_interest_paid"]["points"] = 1
            achieved_points += 1
        elif "error" not in loan_eval_details["total_interest_paid"] and sub_tip is not None:
            loan_eval_details["total_interest_paid"]["difference"] = round(sub_tip - key_tip, 4) if isinstance(sub_tip, (int,float)) else "N/A"

        # --- Schedule Points ---
        loan_eval_details["schedule_points_evaluation"] = []
        key_schedule_points = key_scenario.get("schedule_points", [])
        sub_schedule_points = sub_scenario.get("schedule_points", [])

        if not isinstance(sub_schedule_points, list) or len(sub_schedule_points) != len(key_schedule_points):
            results["structural_warnings"].append(
                f"Schedule points for '{key_loan_id}' has incorrect structure or count. "
                f"Expected {len(key_schedule_points)}, got {len(sub_schedule_points) if isinstance(sub_schedule_points, list) else 'not a list'}."
            )
            for k_sp_idx_warn, k_sp_warn in enumerate(key_schedule_points):
                sp_eval_warn = {
                    "payment_number_expected": k_sp_warn.get("payment_number"),
                    "error": "Missing or malformed schedule point data in submission.",
                    "points_sum": 0
                }
                # Add expected values for clarity on what was missed
                for field_key_warn in ["interest_paid", "principal_paid", "remaining_balance"]:
                    sp_eval_warn[field_key_warn] = {"submitted": None, "expected": k_sp_warn.get(field_key_warn), "correct": False, "points": 0}
                loan_eval_details["schedule_points_evaluation"].append(sp_eval_warn)
        else:
            for sp_idx, key_sp in enumerate(key_schedule_points):
                # sub_sp should exist due to len check, but good to be safe with .get() for its fields
                sub_sp = sub_schedule_points[sp_idx] if isinstance(sub_schedule_points[sp_idx], dict) else {}
                
                sp_eval = {
                    "payment_number_submitted": sub_sp.get("payment_number"),
                    "payment_number_expected": key_sp["payment_number"],
                    "points_sum": 0
                }
                loan_eval_details["schedule_points_evaluation"].append(sp_eval)

                pn_match = (isinstance(sub_sp.get("payment_number"), int) and 
                            sub_sp.get("payment_number") == key_sp["payment_number"])
                sp_eval["payment_number_match"] = pn_match

                if not pn_match:
                    sp_eval["error"] = (f"Payment number mismatch or invalid type. "
                                        f"Expected {key_sp['payment_number']} (int), Got {sub_sp.get('payment_number')}")
                    for field_key_err in ["interest_paid", "principal_paid", "remaining_balance"]:
                        sp_eval[field_key_err] = {"submitted": sub_sp.get(field_key_err), "expected": key_sp[field_key_err], "correct": False, "points": 0}
                    continue 

                # Interest Paid
                sub_val_ip = sub_sp.get("interest_paid")
                key_val_ip = key_sp["interest_paid"]
                ip_correct = is_close_custom(sub_val_ip, key_val_ip, TOLERANCE_SCHEDULE_INTEREST_PRINCIPAL)
                sp_eval["interest_paid"] = {"submitted": sub_val_ip, "expected": key_val_ip, "correct": ip_correct, "points": 0}
                if not isinstance(sub_val_ip, (int, float)): 
                    sp_eval["interest_paid"]["error"] = "Invalid data type"; ip_correct = False; sp_eval["interest_paid"]["correct"] = False
                if ip_correct: sp_eval["interest_paid"]["points"] = 1; sp_eval["points_sum"] += 1
                elif "error" not in sp_eval["interest_paid"] and sub_val_ip is not None: sp_eval["interest_paid"]["difference"] = round(sub_val_ip - key_val_ip, 4) if isinstance(sub_val_ip, (int,float)) else "N/A"

                # Principal Paid
                sub_val_pp = sub_sp.get("principal_paid")
                key_val_pp = key_sp["principal_paid"]
                pp_correct = is_close_custom(sub_val_pp, key_val_pp, TOLERANCE_SCHEDULE_INTEREST_PRINCIPAL)
                sp_eval["principal_paid"] = {"submitted": sub_val_pp, "expected": key_val_pp, "correct": pp_correct, "points": 0}
                if not isinstance(sub_val_pp, (int, float)): 
                    sp_eval["principal_paid"]["error"] = "Invalid data type"; pp_correct = False; sp_eval["principal_paid"]["correct"] = False
                if pp_correct: sp_eval["principal_paid"]["points"] = 1; sp_eval["points_sum"] += 1
                elif "error" not in sp_eval["principal_paid"] and sub_val_pp is not None: sp_eval["principal_paid"]["difference"] = round(sub_val_pp - key_val_pp, 4) if isinstance(sub_val_pp, (int,float)) else "N/A"

                # Remaining Balance
                sub_val_rb = sub_sp.get("remaining_balance")
                key_val_rb = key_sp["remaining_balance"]
                # Check if this key_sp is the last one in the key_scenario's schedule_points list
                is_last_payment_point = (key_sp == key_schedule_points[-1])

                rb_correct = False
                if is_last_payment_point:
                    rb_correct = check_last_balance(sub_val_rb, TOLERANCE_SCHEDULE_BALANCE_LAST_MIN, TOLERANCE_SCHEDULE_BALANCE_LAST_MAX)
                else:
                    rb_correct = is_close_custom(sub_val_rb, key_val_rb, TOLERANCE_SCHEDULE_BALANCE_REGULAR)
                
                sp_eval["remaining_balance"] = {"submitted": sub_val_rb, "expected": key_val_rb, "correct": rb_correct, "points": 0}
                if not isinstance(sub_val_rb, (int, float)): 
                    sp_eval["remaining_balance"]["error"] = "Invalid data type"; rb_correct = False; sp_eval["remaining_balance"]["correct"] = False
                if rb_correct: sp_eval["remaining_balance"]["points"] = 1; sp_eval["points_sum"] += 1
                elif "error" not in sp_eval["remaining_balance"] and sub_val_rb is not None: 
                    sp_eval["remaining_balance"]["difference"] = round(sub_val_rb - key_val_rb, 4) if isinstance(sub_val_rb, (int,float)) else "N/A"
                
                achieved_points += sp_eval["points_sum"]

    results["achieved_points"] = achieved_points
    if TOTAL_POSSIBLE_POINTS > 0:
        results["overall_score_percentage"] = round((achieved_points / TOTAL_POSSIBLE_POINTS) * 100, 2)
    else: # Avoid division by zero if somehow TOTAL_POSSIBLE_POINTS is 0
        results["overall_score_percentage"] = 0.0 if achieved_points == 0 else 100.0


    # Determine final pass status
    if achieved_points >= PASSING_THRESHOLD_POINTS and all_critical_monthly_payments_correct:
        results["pass_status"] = "PASS"
    else:
        results["pass_status"] = "FAIL"
        # Add reasons for failure
        if achieved_points < PASSING_THRESHOLD_POINTS:
             results["fail_reason_points"] = f"Achieved {achieved_points} points, required {PASSING_THRESHOLD_POINTS}."
        if not all_critical_monthly_payments_correct:
             results["fail_reason_critical"] = "One or more critical monthly payments were incorrect, missing, or part of a missing loan scenario."
    
    # Ensure overall_score key is present as per prompt
    results["overall_score"] = results["overall_score_percentage"]


    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluate loan officer exam submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("answer_key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    output_filename = "test_results.json"

    try:
        with open(args.submission_file, 'r') as f:
            submission_data = json.load(f)
    except FileNotFoundError:
        error_msg = f"Error: Submission file '{args.submission_file}' not found."
        print(error_msg)
        error_result = {"error": error_msg, "overall_score": 0.0, "pass_status": "FAIL", "achieved_points":0, "total_possible_points":TOTAL_POSSIBLE_POINTS}
        with open(output_filename, 'w') as f_out:
            json.dump(error_result, f_out, indent=2)
        return
    except json.JSONDecodeError as e:
        error_msg = f"Error: Could not decode JSON from submission file '{args.submission_file}'. Details: {e}"
        print(error_msg)
        error_result = {"error": error_msg, "overall_score": 0.0, "pass_status": "FAIL", "achieved_points":0, "total_possible_points":TOTAL_POSSIBLE_POINTS}
        with open(output_filename, 'w') as f_out:
            json.dump(error_result, f_out, indent=2)
        return

    try:
        with open(args.answer_key_file, 'r') as f:
            answer_key_data = json.load(f)
    except FileNotFoundError:
        error_msg = f"Error: Answer key file '{args.answer_key_file}' not found. Evaluation cannot proceed."
        print(error_msg)
        # This is a setup error, but we should still output a result file.
        error_result = {"error": error_msg, "overall_score": 0.0, "pass_status": "FAIL", "achieved_points":0, "total_possible_points":TOTAL_POSSIBLE_POINTS}
        with open(output_filename, 'w') as f_out:
            json.dump(error_result, f_out, indent=2)
        return
    except json.JSONDecodeError as e:
        error_msg = f"Error: Could not decode JSON from answer key file '{args.answer_key_file}'. Details: {e}. Evaluation cannot proceed."
        print(error_msg)
        error_result = {"error": error_msg, "overall_score": 0.0, "pass_status": "FAIL", "achieved_points":0, "total_possible_points":TOTAL_POSSIBLE_POINTS}
        with open(output_filename, 'w') as f_out:
            json.dump(error_result, f_out, indent=2)
        return

    evaluation_results = evaluate_submission(submission_data, answer_key_data)

    with open(output_filename, 'w') as f_out:
        json.dump(evaluation_results, f_out, indent=2)
    
    print(f"Evaluation complete. Results saved to {output_filename}")
    print(f"Overall Score: {evaluation_results.get('overall_score', 0.0)}%") # Use .get for safety
    print(f"Achieved Points: {evaluation_results.get('achieved_points',0)} / {evaluation_results.get('total_possible_points',TOTAL_POSSIBLE_POINTS)}")
    print(f"Pass Status: {evaluation_results.get('pass_status', 'FAIL')}")
    if "structural_warnings" in evaluation_results and evaluation_results["structural_warnings"]:
        print("\nStructural Warnings:")
        for warning in evaluation_results["structural_warnings"]:
            print(f"- {warning}")

if __name__ == "__main__":
    main()