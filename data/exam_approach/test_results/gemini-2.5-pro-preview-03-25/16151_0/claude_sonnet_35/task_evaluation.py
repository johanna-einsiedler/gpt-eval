import json
import argparse
import sys
from pathlib import Path
import re
from collections import defaultdict

# --- Configuration ---

# Define Likelihood/Impact mapping and predefined lists from instructions
LIKELIHOOD_MAP = {"Low": 1, "Medium": 2, "High": 3}
IMPACT_MAP = {"Low": 1, "Medium": 2, "High": 3}
VALID_CATEGORIES = {"Technical", "Resource", "Schedule", "Budget", "Scope", "External"}
VALID_RESPONSE_TYPES = {"Avoid", "Mitigate", "Transfer", "Accept"}
REQUIRED_ROOT_KEYS = {"exam_candidate_id", "exam_level", "risk_register"}
REQUIRED_RISK_KEYS = {
    "risk_id", "description", "category", "likelihood", "impact",
    "risk_score", "response_strategy_type", "response_strategy_description",
    "potential_owner_role"
}

# Define keywords for matching key risks (adjust based on key risk descriptions)
# Using lowercase for case-insensitive matching
KEY_RISK_KEYWORDS = {
    "Tech Lead Availability": {"technical lead", "john smith", "availability", "50%", "allocation", "resource", "half"},
    "Fixed Budget": {"budget", "fixed", "cost", "funding", "5000", "$5,000", "flexibility", "overrun"},
    "App Bugs": {"bug", "error", "defect", "application", "empdir", "code", "quality", "assumption", "bug-free"},
    "Dev Support": {"developer", "development team", "support", "documentation", "minimal", "reassigned"},
    "DBA Backlog": {"dba", "database", "backlog", "priya khan", "connectivity", "access"},
    # Add more key risks if needed from the key
}

# Scoring Weights
MAX_POINTS = 100
POINTS_CONFIG = {
    "formatting": {
        "valid_json": 5,
        "root_keys": 5,
        "risk_keys": 5,
        "data_types": 5,
        "total": 20
    },
    "identification": {
        "min_risk_count": 10, # Points for identifying >= 4 risks
        "key_risk_coverage": 10, # Points for identifying >= 2 high-priority key risks
        "total": 20
    },
    "analysis": {
        "score_calculation": 10, # Points for correct risk_score calculation (per risk)
        "li_reasonableness": 10, # Points for reasonable L/I assessment (per matched risk)
        "category_correctness": 10, # Points for correct category (per matched risk)
        "total": 30
    },
    "prioritization_response": {
        "top_3_identification": 10, # Points for correctly identifying own top risks for response
        "response_type_logic": 10, # Points for logical response type (per matched top risk)
        "response_desc_relevance": 5, # Points for non-empty description (per top risk)
        "owner_role_plausibility": 5, # Points for plausible owner role (per top risk)
        "total": 30
    }
}

# --- Helper Functions ---

def load_json(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}", file=sys.stderr)
        # Return a structure indicating failure, allowing partial grading if desired later
        return {"error": "Invalid JSON", "details": str(e)}
    except Exception as e:
        print(f"Error: Could not read file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def validate_string_enum(value, valid_set, field_name, risk_id):
    """Checks if a string value is in a predefined set."""
    if value is None: # Allow null where appropriate (checked later)
        return True, ""
    if not isinstance(value, str):
        return False, f"Risk {risk_id}: Field '{field_name}' must be a string, got {type(value).__name__}."
    if value not in valid_set:
        return False, f"Risk {risk_id}: Invalid value '{value}' for field '{field_name}'. Allowed: {valid_set}."
    return True, ""

def calculate_expected_score(likelihood_str, impact_str):
    """Calculates the expected risk score based on L/I strings."""
    l_val = LIKELIHOOD_MAP.get(likelihood_str)
    i_val = IMPACT_MAP.get(impact_str)
    if l_val is None or i_val is None:
        return None # Cannot calculate if L or I is invalid
    return l_val * i_val

def match_risks(candidate_risks, key_risks_data):
    """Matches candidate risks to key risks based on keywords."""
    matched_pairs = {} # key: candidate_risk_id, value: key_risk_id
    key_risk_map = {r['risk_id']: r for r in key_risks_data}
    key_risk_ids_by_concept = defaultdict(list)
    for kr_id, kr in key_risk_map.items():
         # Attempt to find a matching concept based on keywords
         found_concept = None
         kr_desc_lower = kr['description'].lower()
         for concept, keywords in KEY_RISK_KEYWORDS.items():
             # Simple keyword count matching - adjust threshold as needed
             if sum(1 for keyword in keywords if keyword in kr_desc_lower) >= 2: # Require at least 2 keywords
                 found_concept = concept
                 break
         if found_concept:
             key_risk_ids_by_concept[found_concept].append(kr_id)

    # Try to match candidate risks
    candidate_matched_status = {r['risk_id']: False for r in candidate_risks}
    key_matched_status = {kr_id: False for kr_id in key_risk_map}

    for cr in candidate_risks:
        cr_desc_lower = cr.get('description', '').lower()
        best_match_concept = None
        highest_keyword_count = 0

        for concept, keywords in KEY_RISK_KEYWORDS.items():
            current_keyword_count = sum(1 for keyword in keywords if keyword in cr_desc_lower)
            # Prefer concepts with more matching keywords
            if current_keyword_count >= 2 and current_keyword_count > highest_keyword_count:
                 # Check if any key risks for this concept are still available
                 available_key_risks = [kr_id for kr_id in key_risk_ids_by_concept.get(concept, []) if not key_matched_status[kr_id]]
                 if available_key_risks:
                     highest_keyword_count = current_keyword_count
                     best_match_concept = concept

        if best_match_concept:
            # Find the first available key risk ID for the best matching concept
            key_risk_id_to_match = None
            for kr_id in key_risk_ids_by_concept[best_match_concept]:
                if not key_matched_status[kr_id]:
                    key_risk_id_to_match = kr_id
                    break

            if key_risk_id_to_match and not candidate_matched_status[cr['risk_id']]:
                matched_pairs[cr['risk_id']] = key_risk_id_to_match
                candidate_matched_status[cr['risk_id']] = True
                key_matched_status[key_risk_id_to_match] = True

    # Create reverse mapping for convenience
    reverse_matched_pairs = {v: k for k, v in matched_pairs.items()}
    return matched_pairs, reverse_matched_pairs

def get_key_risk_by_id(key_risks_data, key_risk_id):
    """Finds a key risk by its ID."""
    for r in key_risks_data:
        if r['risk_id'] == key_risk_id:
            return r
    return None

# --- Evaluation Functions ---

def evaluate_formatting(submission_data):
    """Evaluates JSON structure, keys, and basic data types."""
    score = 0
    feedback = []
    max_points = POINTS_CONFIG["formatting"]["total"]

    if submission_data.get("error") == "Invalid JSON":
        feedback.append(f"Fatal Error: Submission is not valid JSON. {submission_data.get('details', '')}")
        return 0, feedback, max_points # Cannot proceed

    score += POINTS_CONFIG["formatting"]["valid_json"] # Assumed valid if no error

    # Check root keys
    submitted_root_keys = set(submission_data.keys())
    if REQUIRED_ROOT_KEYS.issubset(submitted_root_keys):
        score += POINTS_CONFIG["formatting"]["root_keys"]
    else:
        missing = REQUIRED_ROOT_KEYS - submitted_root_keys
        feedback.append(f"Formatting Error: Missing required root keys: {missing}")

    # Check risk register structure and keys (check first risk if available)
    risk_register = submission_data.get("risk_register")
    if isinstance(risk_register, list) and len(risk_register) > 0:
        first_risk = risk_register[0]
        if isinstance(first_risk, dict):
            submitted_risk_keys = set(first_risk.keys())
            if REQUIRED_RISK_KEYS.issubset(submitted_risk_keys):
                score += POINTS_CONFIG["formatting"]["risk_keys"]
            else:
                missing = REQUIRED_RISK_KEYS - submitted_risk_keys
                feedback.append(f"Formatting Error: Missing required keys in risk objects: {missing} (checked first risk)")

            # Check basic data types (spot check first risk)
            type_errors = []
            if not isinstance(first_risk.get('risk_id'), int): type_errors.append("'risk_id' not integer")
            if not isinstance(first_risk.get('description'), str): type_errors.append("'description' not string")
            if not isinstance(first_risk.get('category'), str): type_errors.append("'category' not string")
            if not isinstance(first_risk.get('likelihood'), str): type_errors.append("'likelihood' not string")
            if not isinstance(first_risk.get('impact'), str): type_errors.append("'impact' not string")
            if not isinstance(first_risk.get('risk_score'), int) and not isinstance(first_risk.get('risk_score'), float): type_errors.append("'risk_score' not number")
            # Response fields can be null or string, harder to check type rigidly here, focus on enum validation later

            if not type_errors:
                score += POINTS_CONFIG["formatting"]["data_types"]
            else:
                feedback.append(f"Formatting Error: Incorrect data types found (checked first risk): {', '.join(type_errors)}")
        else:
            feedback.append("Formatting Error: Items in 'risk_register' are not objects (dictionaries).")
            score += 0 # Penalize risk_keys and data_types if structure is wrong
    elif not isinstance(risk_register, list):
         feedback.append("Formatting Error: 'risk_register' is not a list.")
         score += 0 # Penalize risk_keys and data_types if structure is wrong
    # else: risk_register is empty list, no keys/types to check

    return min(score, max_points), feedback, max_points

def evaluate_identification(candidate_risks, key_risks_data, matched_pairs):
    """Evaluates the number and relevance of identified risks."""
    score = 0
    feedback = []
    max_points = POINTS_CONFIG["identification"]["total"]
    candidate_risk_count = len(candidate_risks)

    # Check minimum risk count
    if candidate_risk_count >= 4:
        score += POINTS_CONFIG["identification"]["min_risk_count"]
    else:
        feedback.append(f"Identification: Identified {candidate_risk_count} risks, less than the minimum requirement of 4.")

    # Check coverage of high-priority key risks
    high_priority_key_risk_ids = {r['risk_id'] for r in key_risks_data if r['risk_score'] >= 6} # Example threshold
    identified_high_priority_count = 0
    identified_key_concepts = set()

    for cr_id, kr_id in matched_pairs.items():
        if kr_id in high_priority_key_risk_ids:
            identified_high_priority_count += 1
            # Find concept for feedback
            key_risk = get_key_risk_by_id(key_risks_data, kr_id)
            kr_desc_lower = key_risk['description'].lower()
            for concept, keywords in KEY_RISK_KEYWORDS.items():
                 if sum(1 for keyword in keywords if keyword in kr_desc_lower) >= 2:
                     identified_key_concepts.add(concept)
                     break


    if identified_high_priority_count >= 2:
        score += POINTS_CONFIG["identification"]["key_risk_coverage"]
    else:
        feedback.append(f"Identification: Identified only {identified_high_priority_count} high-priority key risks (Score >= 6). Minimum requirement is 2.")
        # List missing concepts for feedback
        all_high_priority_concepts = set()
        for kr in key_risks_data:
            if kr['risk_id'] in high_priority_key_risk_ids:
                 kr_desc_lower = kr['description'].lower()
                 for concept, keywords in KEY_RISK_KEYWORDS.items():
                     if sum(1 for keyword in keywords if keyword in kr_desc_lower) >= 2:
                         all_high_priority_concepts.add(concept)
                         break
        missing_concepts = all_high_priority_concepts - identified_key_concepts
        if missing_concepts:
             feedback.append(f"Identification: Key high-priority concepts potentially missed: {', '.join(missing_concepts)}")


    return min(score, max_points), feedback, max_points

def evaluate_analysis(candidate_risks, key_risks_data, matched_pairs):
    """Evaluates risk score calculation, L/I reasonableness, and category correctness."""
    score_calc_points = 0
    li_points = 0
    cat_points = 0
    feedback = []
    max_points = POINTS_CONFIG["analysis"]["total"]
    max_score_calc = POINTS_CONFIG["analysis"]["score_calculation"]
    max_li = POINTS_CONFIG["analysis"]["li_reasonableness"]
    max_cat = POINTS_CONFIG["analysis"]["category_correctness"]

    total_risks_evaluated = 0
    matched_risks_evaluated = 0

    for cr in candidate_risks:
        total_risks_evaluated += 1
        cr_id = cr.get('risk_id', 'N/A')
        cr_l = cr.get('likelihood')
        cr_i = cr.get('impact')
        cr_score = cr.get('risk_score')

        # 1. Score Calculation Check (for all candidate risks)
        valid_l, msg_l = validate_string_enum(cr_l, LIKELIHOOD_MAP.keys(), 'likelihood', cr_id)
        valid_i, msg_i = validate_string_enum(cr_i, IMPACT_MAP.keys(), 'impact', cr_id)
        if not valid_l: feedback.append(msg_l)
        if not valid_i: feedback.append(msg_i)

        if valid_l and valid_i:
            expected_score = calculate_expected_score(cr_l, cr_i)
            if expected_score is not None and cr_score == expected_score:
                score_calc_points += 1 # Increment points per correct calculation
            else:
                feedback.append(f"Analysis: Risk {cr_id}: Incorrect risk_score calculation. Expected {expected_score} based on L='{cr_l}', I='{cr_i}', but got {cr_score}.")
        else:
             feedback.append(f"Analysis: Risk {cr_id}: Cannot check risk_score calculation due to invalid Likelihood/Impact.")

        # 2. L/I Reasonableness and Category Correctness (only for matched risks)
        if cr_id in matched_pairs:
            matched_risks_evaluated += 1
            kr_id = matched_pairs[cr_id]
            key_risk = get_key_risk_by_id(key_risks_data, kr_id)
            if key_risk:
                kr_l = key_risk['likelihood']
                kr_i = key_risk['impact']
                kr_cat = key_risk['category']
                cr_cat = cr.get('category')

                # L/I Reasonableness (Allow +/- 1 level difference)
                l_diff = abs(LIKELIHOOD_MAP.get(cr_l, 0) - LIKELIHOOD_MAP.get(kr_l, 0))
                i_diff = abs(IMPACT_MAP.get(cr_i, 0) - IMPACT_MAP.get(kr_i, 0))
                if l_diff <= 1 and i_diff <= 1:
                    li_points += 1
                else:
                    feedback.append(f"Analysis: Risk {cr_id} (Matched Key Risk {kr_id}): Likelihood/Impact assessment differs significantly from key. Candidate: L={cr_l}, I={cr_i}. Key: L={kr_l}, I={kr_i}.")

                # Category Correctness
                valid_cat, msg_cat = validate_string_enum(cr_cat, VALID_CATEGORIES, 'category', cr_id)
                if not valid_cat:
                    feedback.append(msg_cat)
                elif cr_cat == kr_cat:
                    cat_points += 1
                else:
                    feedback.append(f"Analysis: Risk {cr_id} (Matched Key Risk {kr_id}): Category mismatch. Candidate: '{cr_cat}'. Key: '{kr_cat}'.")
            else:
                 feedback.append(f"Internal Error: Could not find key risk data for matched ID {kr_id}")


    # Normalize scores based on number of risks evaluated
    final_score_calc_points = (score_calc_points / total_risks_evaluated * max_score_calc) if total_risks_evaluated > 0 else 0
    final_li_points = (li_points / matched_risks_evaluated * max_li) if matched_risks_evaluated > 0 else 0
    final_cat_points = (cat_points / matched_risks_evaluated * max_cat) if matched_risks_evaluated > 0 else 0

    total_score = round(final_score_calc_points + final_li_points + final_cat_points)

    return min(total_score, max_points), feedback, max_points

def evaluate_prioritization_response(candidate_risks, key_risks_data, matched_pairs, reverse_matched_pairs):
    """Evaluates identification of top risks and the quality of their responses."""
    score = 0
    feedback = []
    max_points = POINTS_CONFIG["prioritization_response"]["total"]
    max_top_3_id = POINTS_CONFIG["prioritization_response"]["top_3_identification"]
    max_resp_type = POINTS_CONFIG["prioritization_response"]["response_type_logic"]
    max_resp_desc = POINTS_CONFIG["prioritization_response"]["response_desc_relevance"]
    max_owner = POINTS_CONFIG["prioritization_response"]["owner_role_plausibility"]

    if not candidate_risks:
        return 0, ["Prioritization/Response: No risks identified."], max_points

    # 1. Identify Candidate's Top Risks
    candidate_risks.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
    top_score = candidate_risks[0].get('risk_score', 0) if candidate_risks else 0
    top_risk_ids_candidate = set()
    if top_score > 0:
        # Find the score of the 3rd distinct highest score, handling ties
        scores = sorted(list(set(r.get('risk_score', 0) for r in candidate_risks)), reverse=True)
        cutoff_score = scores[2] if len(scores) >= 3 else (scores[-1] if scores else 0)
        # Include all risks with score >= cutoff_score, ensuring at least top 3 scores are covered
        # Refined logic: Get top 3 scores, find the minimum of these, include all risks >= that minimum
        top_3_scores = scores[:3]
        min_top_score = min(top_3_scores) if top_3_scores else 0
        top_risk_ids_candidate = {r['risk_id'] for r in candidate_risks if r.get('risk_score', 0) >= min_top_score and r.get('risk_score', 0) > 0}


    # 2. Check if response fields are correctly populated (null/non-null)
    correct_population_count = 0
    incorrect_population_details = []
    for cr in candidate_risks:
        cr_id = cr.get('risk_id')
        is_top = cr_id in top_risk_ids_candidate
        has_response = (cr.get('response_strategy_type') is not None or
                        cr.get('response_strategy_description') is not None or
                        cr.get('potential_owner_role') is not None)

        if is_top and has_response:
            correct_population_count += 1
        elif not is_top and not has_response:
            correct_population_count += 1
        elif is_top and not has_response:
            incorrect_population_details.append(f"Risk {cr_id} identified as top risk (score {cr.get('risk_score')}) but lacks response details.")
        elif not is_top and has_response:
             incorrect_population_details.append(f"Risk {cr_id} not identified as top risk (score {cr.get('risk_score')}) but has response details.")

    if not incorrect_population_details:
        score += max_top_3_id
    else:
        feedback.append("Prioritization/Response: Mismatch between identified top risks and provided response details:")
        feedback.extend(incorrect_population_details)
        # Partial credit maybe? For now, all or nothing for this part.
        score += max_top_3_id * (correct_population_count / len(candidate_risks)) # Proportional score


    # 3. Evaluate Response Quality for Candidate's Top Risks
    resp_type_points = 0
    resp_desc_points = 0
    owner_points = 0
    top_risks_evaluated_count = 0

    for cr_id in top_risk_ids_candidate:
        # Find the candidate risk object
        cr = next((r for r in candidate_risks if r.get('risk_id') == cr_id), None)
        if not cr: continue # Should not happen if logic is correct

        top_risks_evaluated_count += 1

        # Check Response Type Logic (compare to key if matched)
        cr_resp_type = cr.get('response_strategy_type')
        valid_resp_type, msg_resp_type = validate_string_enum(cr_resp_type, VALID_RESPONSE_TYPES, 'response_strategy_type', cr_id)
        if not valid_resp_type:
            feedback.append(msg_resp_type)
        else:
            # Compare to key if possible
            if cr_id in matched_pairs:
                kr_id = matched_pairs[cr_id]
                key_risk = get_key_risk_by_id(key_risks_data, kr_id)
                # Check if the key risk *should* have a response (i.e., is top in the key)
                key_top_scores = sorted(list(set(r.get('risk_score', 0) for r in key_risks_data)), reverse=True)
                key_min_top_score = min(key_top_scores[:3]) if len(key_top_scores) >=3 else (key_top_scores[-1] if key_top_scores else 0)

                if key_risk and key_risk.get('risk_score', 0) >= key_min_top_score:
                    kr_resp_type = key_risk.get('response_strategy_type')
                    if cr_resp_type == kr_resp_type:
                        resp_type_points += 1
                    else:
                        # Allow some flexibility? e.g. Mitigate vs Avoid might be debatable
                        # For now, strict match
                        feedback.append(f"Prioritization/Response: Risk {cr_id} (Key {kr_id}): Response type '{cr_resp_type}' differs from key '{kr_resp_type}'.")
                else:
                    # Candidate provided response for a risk that wasn't top in the key (or wasn't matched)
                    # Or key risk didn't have response. If type is valid, give partial credit?
                    resp_type_points += 0.5 # Give half point for valid type even if not matching key's top
            elif cr_resp_type: # Unmatched risk, but valid response type provided
                 resp_type_points += 0.5 # Give half point for valid type

        # Check Response Description Relevance (non-empty check)
        cr_resp_desc = cr.get('response_strategy_description')
        if isinstance(cr_resp_desc, str) and len(cr_resp_desc.strip()) > 10: # Require more than just a few chars
            resp_desc_points += 1
        else:
            feedback.append(f"Prioritization/Response: Risk {cr_id}: Response description is missing or too brief.")

        # Check Owner Role Plausibility (non-empty check, maybe check against scenario roles later)
        cr_owner = cr.get('potential_owner_role')
        if isinstance(cr_owner, str) and len(cr_owner.strip()) > 2:
            owner_points += 1
            # Future enhancement: Check if role exists in scenario
        else:
            feedback.append(f"Prioritization/Response: Risk {cr_id}: Potential owner role is missing or invalid.")


    # Normalize scores
    final_resp_type_points = (resp_type_points / top_risks_evaluated_count * max_resp_type) if top_risks_evaluated_count > 0 else 0
    final_resp_desc_points = (resp_desc_points / top_risks_evaluated_count * max_resp_desc) if top_risks_evaluated_count > 0 else 0
    final_owner_points = (owner_points / top_risks_evaluated_count * max_owner) if top_risks_evaluated_count > 0 else 0

    score += round(final_resp_type_points + final_resp_desc_points + final_owner_points)

    return min(score, max_points), feedback, max_points


# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate IT Project Manager Basic Risk Assessment Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    submission_path = Path(args.submission_file)
    key_path = Path(args.key_file)
    results_path = Path("test_results.json")

    # Load data
    submission_data = load_json(submission_path)
    key_data = load_json(key_path)

    # Initialize results structure
    results = {
        "candidate_file": str(submission_path.name),
        "key_file": str(key_path.name),
        "overall_score": 0,
        "scores_by_category": {},
        "feedback": [],
        "risk_matching": {}
    }

    # Handle JSON loading errors
    if submission_data.get("error") == "Invalid JSON":
        results["feedback"].append(f"Fatal Error: Could not parse submission file {submission_path.name}. Evaluation halted.")
        results["scores_by_category"]["formatting"] = {"score": 0, "max_points": POINTS_CONFIG["formatting"]["total"], "feedback": [submission_data.get("details", "Unknown JSON error")]}
        # Write results and exit
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation results saved to {results_path}")
        sys.exit(1) # Indicate failure

    if key_data.get("error") == "Invalid JSON":
        print(f"Fatal Error: Could not parse key file {key_path.name}. Evaluation halted.", file=sys.stderr)
        sys.exit(1)


    # --- Start Evaluation ---
    total_score = 0
    total_max_points = 0

    # 1. Formatting Evaluation
    fmt_score, fmt_feedback, fmt_max = evaluate_formatting(submission_data)
    results["scores_by_category"]["formatting"] = {"score": fmt_score, "max_points": fmt_max, "feedback": fmt_feedback}
    results["feedback"].extend(fmt_feedback)
    total_score += fmt_score
    total_max_points += fmt_max

    # Proceed only if basic structure is somewhat okay
    candidate_risks = submission_data.get("risk_register", [])
    key_risks = key_data.get("risk_register", [])

    if not isinstance(candidate_risks, list):
         results["feedback"].append("Fatal Error: 'risk_register' is not a list in submission. Cannot evaluate further.")
         candidate_risks = [] # Prevent errors later

    # Match risks between submission and key
    matched_pairs, reverse_matched_pairs = match_risks(candidate_risks, key_risks)
    results["risk_matching"] = {
        "candidate_to_key": matched_pairs,
        "key_to_candidate": reverse_matched_pairs,
        "unmatched_candidate_ids": [r['risk_id'] for r in candidate_risks if r['risk_id'] not in matched_pairs],
        "unmatched_key_ids": [r['risk_id'] for r in key_risks if r['risk_id'] not in reverse_matched_pairs]
        }


    # 2. Identification Evaluation
    id_score, id_feedback, id_max = evaluate_identification(candidate_risks, key_risks, matched_pairs)
    results["scores_by_category"]["identification"] = {"score": id_score, "max_points": id_max, "feedback": id_feedback}
    results["feedback"].extend(id_feedback)
    total_score += id_score
    total_max_points += id_max

    # 3. Analysis Evaluation
    an_score, an_feedback, an_max = evaluate_analysis(candidate_risks, key_risks, matched_pairs)
    results["scores_by_category"]["analysis"] = {"score": an_score, "max_points": an_max, "feedback": an_feedback}
    results["feedback"].extend(an_feedback)
    total_score += an_score
    total_max_points += an_max

    # 4. Prioritization & Response Evaluation
    pr_score, pr_feedback, pr_max = evaluate_prioritization_response(candidate_risks, key_risks, matched_pairs, reverse_matched_pairs)
    results["scores_by_category"]["prioritization_response"] = {"score": pr_score, "max_points": pr_max, "feedback": pr_feedback}
    results["feedback"].extend(pr_feedback)
    total_score += pr_score
    total_max_points += pr_max

    # Calculate Overall Score
    if total_max_points > 0:
        results["overall_score"] = round((total_score / total_max_points) * 100, 2)
    else:
        results["overall_score"] = 0

    # Save results
    try:
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Evaluation results saved to {results_path}")
    except Exception as e:
        print(f"Error: Could not write results to {results_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()