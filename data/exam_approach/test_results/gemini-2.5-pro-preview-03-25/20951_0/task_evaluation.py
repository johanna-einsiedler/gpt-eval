import json
import argparse
import sys
import os
import math

# --- Scoring Configuration ---
# Based on the provided <evaluation_information>

# Total possible points
TOTAL_POSSIBLE_POINTS = 100.0

# Point allocation
POINTS = {
    "json_validity_structure": {
        "total": 10,
        "file_named_correctly": 0, # Checked by user running script, not auto-scored here
        "valid_json_format": 4,
        "correct_structure": 6, # Includes top-level keys, list types
    },
    "calculated_metric": {
        "total": 10,
        "correct_metric_name": 2,
        "correct_value": 8,
        "tolerance": 0.1 # Allow +/- 0.1 for rounding diffs
    },
    "negotiation_points": {
        # Points per *key* negotiation point item
        "term_commission": {
            "total": 20,
            "term_value_match": 2,
            "assessment_match": 4,
            "action_match": 4,
            "proposal_match": 5,
            "evidence_match": 5,
        },
        "term_exclusion": {
            "total": 20,
            "term_value_match": 2,
            "assessment_match": 4,
            "action_match": 4,
            "proposal_match": 5,
            "evidence_match": 5,
        },
        "term_claims_control": {
            "total": 20,
            "term_value_match": 2,
            "assessment_match": 4,
            "action_match": 4,
            "proposal_match": 5,
            "evidence_match": 5,
        },
        "acceptable_terms": {
            # Points for correctly identifying specific acceptable terms from the key
            "total": 10,
            "points_per_term": 5,
            "required_terms": ["Cession Percentage", "Business Covered"] # Terms to check for
        },
    },
    "adherence_specificity": {
        "total": 10,
        "predefined_values_used": 5, # For assessment & action across all analyzed points
        "specific_evidence_format": 5, # Check if evidence strings look specific enough
    }
}

# Predefined values for validation
PREDEFINED_ASSESSMENTS = [
    "Acceptable", "Below Guideline", "Above Guideline", "Unclear", "Potentially Problematic"
]
PREDEFINED_ACTIONS = [
    "Accept", "Request Change", "Request Clarification", "Request Removal"
]

# --- Helper Functions ---

def load_json(file_path):
    """Loads a JSON file with error handling."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}. Details: {e}", file=sys.stderr)
        # Return None to indicate failure, allowing partial scoring for structure
        return None
    except Exception as e:
        print(f"Error reading file {file_path}. Details: {e}", file=sys.stderr)
        sys.exit(1)

def check_structure(data):
    """Checks the basic structure of the submission."""
    if not isinstance(data, dict):
        return False, "Root element is not a dictionary."

    required_keys = ["candidate_id", "exam_part", "calculated_metrics", "negotiation_points"]
    for key in required_keys:
        if key not in data:
            return False, f"Missing required top-level key: '{key}'."

    if not isinstance(data.get("calculated_metrics"), list):
        return False, "'calculated_metrics' should be a list."
    if not isinstance(data.get("negotiation_points"), list):
        return False, "'negotiation_points' should be a list."

    # Check structure within metrics list (at least one item with required keys)
    metrics = data.get("calculated_metrics", [])
    if not metrics:
         return False, "'calculated_metrics' list is empty."
    if not all(isinstance(m, dict) and "metric_name" in m and "value" in m for m in metrics):
         return False, "Items in 'calculated_metrics' lack required keys ('metric_name', 'value')."

    # Check structure within negotiation points list (if not empty)
    points = data.get("negotiation_points", [])
    required_point_keys = ["term_quoted", "quoted_value", "assessment", "proposed_action", "proposed_value_or_request", "supporting_evidence_reference"]
    if points and not all(isinstance(p, dict) and all(key in p for key in required_point_keys) for p in points):
        return False, "Some items in 'negotiation_points' lack required keys."

    return True, "Structure appears correct."


def compare_values(candidate_val, key_val, tolerance=0.0):
    """Compares values, allowing tolerance for floats."""
    if isinstance(key_val, float):
        return math.isclose(float(candidate_val), key_val, abs_tol=tolerance)
    elif isinstance(key_val, str):
         # Strict comparison for strings as per rubric (case-sensitive)
        return str(candidate_val) == key_val
    else:
        # General comparison for other types (int, bool, etc.)
        return candidate_val == key_val

# --- Scoring Functions ---

def score_structure_validity(candidate_data):
    """Scores JSON validity and basic structure."""
    score = 0
    details = {}
    max_points = POINTS["json_validity_structure"]["total"]

    if candidate_data is None:
        details["valid_json_format"] = f"0 / {POINTS['json_validity_structure']['valid_json_format']} (Invalid JSON)"
        details["correct_structure"] = f"0 / {POINTS['json_validity_structure']['correct_structure']} (Cannot check structure)"
        return 0, details

    # Score validity (already passed if candidate_data is not None)
    score += POINTS["json_validity_structure"]["valid_json_format"]
    details["valid_json_format"] = f"{POINTS['json_validity_structure']['valid_json_format']} / {POINTS['json_validity_structure']['valid_json_format']}"

    # Score structure
    is_correct, message = check_structure(candidate_data)
    if is_correct:
        score += POINTS["json_validity_structure"]["correct_structure"]
        details["correct_structure"] = f"{POINTS['json_validity_structure']['correct_structure']} / {POINTS['json_validity_structure']['correct_structure']}"
    else:
        details["correct_structure"] = f"0 / {POINTS['json_validity_structure']['correct_structure']} ({message})"

    return score, details

def score_calculated_metric(candidate_metrics, key_metrics):
    """Scores the calculated metric section."""
    score = 0
    details = {}
    max_points = POINTS["calculated_metric"]["total"]
    points_name = POINTS["calculated_metric"]["correct_metric_name"]
    points_value = POINTS["calculated_metric"]["correct_value"]
    tolerance = POINTS["calculated_metric"]["tolerance"]

    if not isinstance(candidate_metrics, list) or not candidate_metrics:
        details["metric_found"] = f"0 / {max_points} (No metrics list or empty)"
        return 0, details

    # Assume only one metric is expected as per instructions
    key_metric = key_metrics[0]
    candidate_metric = None
    # Find the metric by name in candidate's submission
    for cm in candidate_metrics:
        if isinstance(cm, dict) and cm.get("metric_name") == key_metric.get("metric_name"):
            candidate_metric = cm
            break

    if candidate_metric is None:
        details[key_metric.get("metric_name")] = f"0 / {max_points} (Metric not found or name mismatch)"
        return 0, details

    metric_name = key_metric.get("metric_name")
    metric_details = {}

    # Score name match (already confirmed if candidate_metric was found)
    score += points_name
    metric_details["name_match"] = f"{points_name} / {points_name}"

    # Score value match
    candidate_value = candidate_metric.get("value")
    key_value = key_metric.get("value")
    try:
        # Attempt conversion for comparison, handle potential errors
        candidate_value_float = float(candidate_value) if candidate_value is not None else None
        if candidate_value_float is not None and compare_values(candidate_value_float, key_value, tolerance):
            score += points_value
            metric_details["value_match"] = f"{points_value} / {points_value} (Value: {candidate_value})"
        else:
            metric_details["value_match"] = f"0 / {points_value} (Expected: {key_value}, Got: {candidate_value})"
    except (ValueError, TypeError):
         metric_details["value_match"] = f"0 / {points_value} (Invalid value format: {candidate_value})"


    details[metric_name] = metric_details
    return score, details


def score_negotiation_points(candidate_points, key_points):
    """Scores the negotiation points section."""
    total_score = 0
    details = {}
    adherence_details = {"valid_assessments": True, "valid_actions": True, "specific_evidence": True}
    acceptable_terms_found = 0
    max_acceptable_terms = len(POINTS["negotiation_points"]["acceptable_terms"]["required_terms"])
    points_per_acceptable = POINTS["negotiation_points"]["acceptable_terms"]["points_per_term"]

    # Create dicts for faster lookup
    candidate_points_dict = {p.get("term_quoted"): p for p in candidate_points if isinstance(p, dict) and "term_quoted" in p}
    key_points_dict = {p.get("term_quoted"): p for p in key_points if isinstance(p, dict) and "term_quoted" in p}

    # Iterate through the KEY points to ensure all required items are evaluated
    for term, key_item in key_points_dict.items():
        item_score = 0
        item_details = {}
        candidate_item = candidate_points_dict.get(term)

        # Determine scoring category (commission, exclusion, claims, or acceptable)
        term_category_key = None
        if "Ceding Commission" in term:
            term_category_key = "term_commission"
        elif "Exclusion" in term:
            term_category_key = "term_exclusion"
        elif "Claims Control" in term:
            term_category_key = "term_claims_control"
        elif term in POINTS["negotiation_points"]["acceptable_terms"]["required_terms"]:
             term_category_key = "acceptable_term" # Special handling below
        else:
             term_category_key = "other" # Generic term, might be acceptable

        # Get points allocation for this category (if defined)
        category_points = POINTS["negotiation_points"].get(term_category_key, {})
        max_item_points = category_points.get("total", 0) if term_category_key != "acceptable_term" else points_per_acceptable

        if candidate_item:
            # --- Score individual fields ---
            fields_to_score = {
                "quoted_value": "term_value_match",
                "assessment": "assessment_match",
                "proposed_action": "action_match",
                "proposed_value_or_request": "proposal_match",
                "supporting_evidence_reference": "evidence_match",
            }

            for field, score_key in fields_to_score.items():
                field_points = category_points.get(score_key, 0) if term_category_key != "acceptable_term" else (max_item_points // len(fields_to_score)) # Distribute points for acceptable terms
                candidate_val = candidate_item.get(field)
                key_val = key_item.get(field)

                # Special check for proposal when action is "Accept"
                is_accept_action = key_item.get("proposed_action") == "Accept"
                if field == "proposed_value_or_request" and is_accept_action:
                    key_val = "N/A" # Expect "N/A" for accepted items

                if compare_values(candidate_val, key_val):
                    item_score += field_points
                    item_details[score_key] = f"{field_points} / {field_points}"
                else:
                    item_details[score_key] = f"0 / {field_points} (Expected: '{key_val}', Got: '{candidate_val}')"

                # --- Check adherence for non-acceptable terms ---
                if term_category_key != "acceptable_term":
                    if field == "assessment" and candidate_val not in PREDEFINED_ASSESSMENTS:
                        adherence_details["valid_assessments"] = False
                        item_details[score_key] += " [INVALID_PREDEFINED]"
                    if field == "proposed_action" and candidate_val not in PREDEFINED_ACTIONS:
                        adherence_details["valid_actions"] = False
                        item_details[score_key] += " [INVALID_PREDEFINED]"
                    if field == "supporting_evidence_reference":
                        # Basic check for specificity (contains ' - ' and not too short)
                        if not isinstance(candidate_val, str) or " - " not in candidate_val or len(candidate_val) < 15:
                             adherence_details["specific_evidence"] = False
                             item_details[score_key] += " [NON_SPECIFIC_FORMAT]"

            # Handle scoring for specifically required acceptable terms
            if term_category_key == "acceptable_term":
                 # Only add score if all fields matched for this acceptable term
                 if item_score >= max_item_points: # Check if fully correct
                     acceptable_terms_found += 1
                     item_details["status"] = "Correctly identified as acceptable"
                 else:
                     item_details["status"] = "Incorrectly identified or details mismatch"
                     item_score = 0 # Reset score if not fully correct for acceptable term
            else:
                 total_score += item_score # Add score for major negotiation points

            details[term] = {"score": f"{item_score} / {max_item_points}", "breakdown": item_details}

        else:
            # Candidate did not include this term from the key
            details[term] = {"score": f"0 / {max_item_points}", "breakdown": "Term not found in submission"}
            # Mark adherence checks as failed if a required term is missing
            if term_category_key != "acceptable_term":
                 adherence_details["valid_assessments"] = False
                 adherence_details["valid_actions"] = False
                 adherence_details["specific_evidence"] = False


    # Add score for acceptable terms based on count found
    acceptable_terms_score = min(acceptable_terms_found, max_acceptable_terms) * points_per_acceptable
    total_score += acceptable_terms_score
    details["acceptable_terms_summary"] = {
        "score": f"{acceptable_terms_score} / {POINTS['negotiation_points']['acceptable_terms']['total']}",
        "found_correctly": acceptable_terms_found,
        "required": max_acceptable_terms
    }

    return total_score, details, adherence_details


def score_adherence(adherence_details):
    """Scores adherence to predefined values and specificity."""
    score = 0
    details = {}
    max_points = POINTS["adherence_specificity"]["total"]
    points_predefined = POINTS["adherence_specificity"]["predefined_values_used"]
    points_specific = POINTS["adherence_specificity"]["specific_evidence_format"]

    if adherence_details["valid_assessments"] and adherence_details["valid_actions"]:
        score += points_predefined
        details["predefined_values_used"] = f"{points_predefined} / {points_predefined}"
    else:
        details["predefined_values_used"] = f"0 / {points_predefined} (Incorrect/missing assessment/action values found)"

    if adherence_details["specific_evidence"]:
        score += points_specific
        details["specific_evidence_format"] = f"{points_specific} / {points_specific}"
    else:
        details["specific_evidence_format"] = f"0 / {points_specific} (Non-specific/missing evidence references found)"

    return score, details

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate Actuarial Reinsurance Negotiation Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    # Load files
    candidate_data = load_json(args.submission_file)
    key_data = load_json(args.key_file)

    # Initialize results
    results = {
        "candidate_file": args.submission_file,
        "key_file": args.key_file,
        "scores": {},
        "overall_score": 0.0
    }
    total_score = 0

    # --- Score Sections ---
    # 1. Structure and Validity
    structure_score, structure_details = score_structure_validity(candidate_data)
    total_score += structure_score
    results["scores"]["1_json_validity_structure"] = {
        "score": structure_score,
        "max_points": POINTS["json_validity_structure"]["total"],
        "details": structure_details
    }
    # Stop if basic structure is invalid and prevents further scoring
    if candidate_data is None or not check_structure(candidate_data)[0]:
         print("Warning: Basic JSON structure is invalid or file unreadable. Scoring may be incomplete.", file=sys.stderr)
         # Allow scoring to continue for what's possible, but negotiation points might fail

    # 2. Calculated Metric
    metric_score = 0 # Default score
    metric_details = {"error": "Could not score due to structure issues or missing data."}
    if candidate_data and "calculated_metrics" in candidate_data and "calculated_metrics" in key_data:
        metric_score, metric_details = score_calculated_metric(
            candidate_data.get("calculated_metrics", []),
            key_data.get("calculated_metrics", [])
        )
    total_score += metric_score
    results["scores"]["2_calculated_metric"] = {
        "score": metric_score,
        "max_points": POINTS["calculated_metric"]["total"],
        "details": metric_details
    }

    # 3. Negotiation Points & Adherence
    negotiation_score = 0 # Default score
    negotiation_details = {"error": "Could not score due to structure issues or missing data."}
    adherence_score = 0 # Default score
    adherence_details_summary = {"error": "Could not score due to structure issues or missing data."}

    if candidate_data and "negotiation_points" in candidate_data and "negotiation_points" in key_data:
        negotiation_score, negotiation_details, adherence_runtime_details = score_negotiation_points(
            candidate_data.get("negotiation_points", []),
            key_data.get("negotiation_points", [])
        )
        # Calculate adherence score based on findings during negotiation point scoring
        adherence_score, adherence_details_summary = score_adherence(adherence_runtime_details)

    total_score += negotiation_score
    total_score += adherence_score

    # Calculate total max points for negotiation section dynamically based on key
    negotiation_max_points = sum(POINTS["negotiation_points"].get(cat, {}).get("total", 0)
                                 for cat in ["term_commission", "term_exclusion", "term_claims_control"]) \
                           + POINTS["negotiation_points"]["acceptable_terms"]["total"]

    results["scores"]["3_negotiation_points"] = {
        "score": negotiation_score,
        # Note: Max points here combines major terms + acceptable terms points
        "max_points": negotiation_max_points,
        "details": negotiation_details
    }
    results["scores"]["4_adherence_specificity"] = {
        "score": adherence_score,
        "max_points": POINTS["adherence_specificity"]["total"],
        "details": adherence_details_summary
    }


    # --- Final Score ---
    # Ensure total score doesn't exceed max possible points due to rounding or logic errors
    total_score = min(total_score, TOTAL_POSSIBLE_POINTS)
    overall_percentage = (total_score / TOTAL_POSSIBLE_POINTS) * 100 if TOTAL_POSSIBLE_POINTS > 0 else 0
    results["overall_score"] = round(overall_percentage, 2)
    results["total_points_achieved"] = round(total_score, 2)
    results["total_possible_points"] = TOTAL_POSSIBLE_POINTS


    # --- Save Results ---
    output_file = "test_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation complete. Results saved to {output_file}")
        print(f"Overall Score: {results['overall_score']:.2f}%")
    except Exception as e:
        print(f"Error writing results to {output_file}. Details: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()