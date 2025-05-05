# task_evaluation.py
import json
import sys
import os
from collections import defaultdict

# --- Configuration ---

# Define the key risks from the answer key for identification checking
# Using simplified keywords and expected category for mapping
# Tuple: (Keywords (lowercase list), Expected Category, Key Risk ID for reference)
KEY_RISK_DEFINITIONS = [
    (["technical lead", "availability", "allocation", "john smith"], "Resource", "KeyRisk_TechLead"),
    (["budget", "fixed", "cost", "funding", "$5,000"], "Budget", "KeyRisk_Budget"),
    (["bug", "application", "empdir", "software", "code"], "Technical", "KeyRisk_AppBugs"),
    (["developer", "support", "documentation", "dev team"], "External", "KeyRisk_DevSupport"),
    (["dba", "database", "backlog", "priya khan"], "External", "KeyRisk_DBA"),
    (["deployment", "off-hours", "outside business hours"], "Schedule", "KeyRisk_DeploymentTime"),
    (["user acceptance", "uat", "end-user", "david lee"], "Resource", "KeyRisk_UAT"),
]

# Define expected values from instructions
ALLOWED_CATEGORIES = {"technical", "resource", "schedule", "budget", "scope", "external"}
ALLOWED_LIKELIHOOD_IMPACT = {"low", "medium", "high"}
ALLOWED_RESPONSE_TYPES = {"avoid", "mitigate", "transfer", "accept"}
EXPECTED_EXAM_LEVEL = "Basic"

# Scoring Weights (Total points = 100)
POINTS_CONFIG = {
    "valid_json": 5, # Foundational
    "base_structure": 5, # Foundational
    "risk_identification_min_count": 10, # Identified at least 4 risks
    "risk_identification_key_risks": 15, # Identified at least 2 key risks
    "analysis_likelihood_impact_reasonableness": 15, # Reasonable L/I for mapped risks
    "analysis_score_calculation": 10, # Correct L*I calculation internally
    "prioritization_top_3_identification": 10, # Correctly identified own Top 3/ties
    "response_fields_null_handling": 10, # Correct use of null for non-top risks
    "response_strategy_logic": 10, # Valid type & presence of desc/owner for top risks
    "formatting_adherence": 10, # Correct categories, response types, level, data types
}
MIN_RISKS_TO_IDENTIFY = 4
MIN_KEY_RISKS_TO_IDENTIFY = 2

# --- Helper Functions ---

def load_json(file_path):
    """Loads a JSON file and returns the data or None if error."""
    if not os.path.exists(file_path):
        return None, f"Error: File not found at {file_path}"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON format in {file_path}. Details: {e}"
    except Exception as e:
        return None, f"Error: Could not read file {file_path}. Details: {e}"

def get_likelihood_impact_value(level_str):
    """Maps Low/Medium/High string to 1/2/3."""
    level_str_lower = level_str.lower() if isinstance(level_str, str) else ""
    if level_str_lower == "low":
        return 1
    if level_str_lower == "medium":
        return 2
    if level_str_lower == "high":
        return 3
    return 0 # Invalid value

def map_candidate_risk_to_key(candidate_risk):
    """Attempts to map a candidate risk to one of the KEY_RISK_DEFINITIONS."""
    description = candidate_risk.get("description", "").lower()
    category = candidate_risk.get("category", "").lower()

    best_match = None
    highest_keyword_match_count = 0

    for keywords, key_category, key_id in KEY_RISK_DEFINITIONS:
        # Basic category check (optional, could be lenient if description is strong)
        # if category != key_category.lower():
        #     continue

        current_match_count = sum(1 for keyword in keywords if keyword in description)

        # Prioritize matches with more keywords, potentially combined with category match
        if current_match_count > 0 and current_match_count >= highest_keyword_match_count:
             # Simple heuristic: if categories match OR this has more keywords than previous best match
            if category == key_category.lower() or current_match_count > highest_keyword_match_count:
                 highest_keyword_match_count = current_match_count
                 best_match = key_id

    return best_match


# --- Evaluation Functions ---

def evaluate_structure_and_validity(submission_data):
    """Checks basic JSON validity and structure."""
    score = 0
    feedback = []
    is_valid = True

    if submission_data is None:
        # Error handled during loading, just return 0
        return 0, ["Submission file is invalid or could not be read."], False

    score += POINTS_CONFIG["valid_json"] # Points for being valid JSON

    if not isinstance(submission_data, dict):
        feedback.append("Submission is not a JSON object.")
        is_valid = False
    else:
        if "exam_candidate_id" not in submission_data:
            feedback.append("Missing 'exam_candidate_id' field.")
            is_valid = False
        if submission_data.get("exam_level") != EXPECTED_EXAM_LEVEL:
             feedback.append(f"Incorrect 'exam_level'. Expected '{EXPECTED_EXAM_LEVEL}', found '{submission_data.get('exam_level')}'.")
             # Don't mark as invalid structure for this, but note for formatting score later
        if "risk_register" not in submission_data or not isinstance(submission_data.get("risk_register"), list):
            feedback.append("Missing or invalid 'risk_register' field (must be a list).")
            is_valid = False

    if is_valid:
        score += POINTS_CONFIG["base_structure"]
        feedback.append("Base structure (candidate_id, level, risk_register list) is valid.")
    else:
         feedback.append("Basic structure validation failed.")
         # If structure fails, further evaluation is unreliable
         return score, feedback, False

    return score, feedback, True


def evaluate_risk_identification(risk_register, key_risk_map):
    """Evaluates if enough risks and key risks were identified."""
    score = 0
    feedback = []
    num_risks_identified = len(risk_register)
    identified_key_risk_ids = set(key_risk_map.values()) # Get unique key risk IDs mapped

    # Score for minimum total risks
    if num_risks_identified >= MIN_RISKS_TO_IDENTIFY:
        score += POINTS_CONFIG["risk_identification_min_count"]
        feedback.append(f"Sufficient risks identified ({num_risks_identified} >= {MIN_RISKS_TO_IDENTIFY}).")
    else:
        points_lost = POINTS_CONFIG["risk_identification_min_count"] * (1 - num_risks_identified / MIN_RISKS_TO_IDENTIFY)
        score += POINTS_CONFIG["risk_identification_min_count"] - points_lost
        feedback.append(f"Insufficient risks identified ({num_risks_identified} < {MIN_RISKS_TO_IDENTIFY}). Identified: {num_risks_identified}")


    # Score for minimum key risks
    num_key_risks_identified = len(identified_key_risk_ids)
    if num_key_risks_identified >= MIN_KEY_RISKS_TO_IDENTIFY:
        score += POINTS_CONFIG["risk_identification_key_risks"]
        feedback.append(f"Sufficient key risks identified ({num_key_risks_identified} >= {MIN_KEY_RISKS_TO_IDENTIFY}). Mapped IDs: {list(identified_key_risk_ids)}")
    else:
        points_lost = POINTS_CONFIG["risk_identification_key_risks"] * (1 - num_key_risks_identified / MIN_KEY_RISKS_TO_IDENTIFY)
        score += POINTS_CONFIG["risk_identification_key_risks"] - points_lost
        feedback.append(f"Insufficient key risks identified ({num_key_risks_identified} < {MIN_KEY_RISKS_TO_IDENTIFY}). Mapped IDs: {list(identified_key_risk_ids)}")

    return score, feedback

def evaluate_risk_analysis(risk_register, key_risk_map, answer_key_risks_dict):
    """Evaluates Likelihood/Impact reasonableness and score calculation."""
    l_i_score = 0
    calc_score = 0
    l_i_feedback = []
    calc_feedback = []
    checked_risks_count = 0
    reasonable_l_i_count = 0
    correct_calc_count = 0

    for i, risk in enumerate(risk_register):
        risk_id = risk.get("risk_id", f"Risk_{i+1}")
        candidate_l_str = risk.get("likelihood", "").lower()
        candidate_i_str = risk.get("impact", "").lower()
        candidate_score = risk.get("risk_score")

        # 1. Check Score Calculation
        calculated_expected_score = get_likelihood_impact_value(candidate_l_str) * get_likelihood_impact_value(candidate_i_str)
        if isinstance(candidate_score, (int, float)) and calculated_expected_score > 0 and candidate_score == calculated_expected_score:
            correct_calc_count += 1
        elif calculated_expected_score > 0: # Only penalize if L/I were valid enough to calculate
             calc_feedback.append(f"Risk {risk_id}: Incorrect score calculation. L='{candidate_l_str}', I='{candidate_i_str}' should yield score {calculated_expected_score}, but found {candidate_score}.")
        # else: L/I were invalid, calculation cannot be checked reliably

        # 2. Check L/I Reasonableness (only for mapped risks)
        key_risk_id = key_risk_map.get(risk_id)
        if key_risk_id and key_risk_id in answer_key_risks_dict:
            checked_risks_count += 1
            key_risk = answer_key_risks_dict[key_risk_id]
            key_l_val = get_likelihood_impact_value(key_risk.get("likelihood", ""))
            key_i_val = get_likelihood_impact_value(key_risk.get("impact", ""))
            candidate_l_val = get_likelihood_impact_value(candidate_l_str)
            candidate_i_val = get_likelihood_impact_value(candidate_i_str)

            # Allow +/- 1 level difference for reasonableness
            l_reasonable = abs(candidate_l_val - key_l_val) <= 1 if candidate_l_val > 0 and key_l_val > 0 else False
            i_reasonable = abs(candidate_i_val - key_i_val) <= 1 if candidate_i_val > 0 and key_i_val > 0 else False

            if l_reasonable and i_reasonable:
                reasonable_l_i_count += 1
            else:
                l_i_feedback.append(f"Risk {risk_id} (Mapped to {key_risk_id}): L/I assessment deviates significantly from key. Candidate L='{candidate_l_str}'({candidate_l_val}), I='{candidate_i_str}'({candidate_i_val}). Key L='{key_risk.get('likelihood')}'({key_l_val}), I='{key_risk.get('impact')}'({key_i_val}).")

    # Calculate Scores
    if checked_risks_count > 0:
        l_i_score = POINTS_CONFIG["analysis_likelihood_impact_reasonableness"] * (reasonable_l_i_count / checked_risks_count)
        l_i_feedback.insert(0, f"L/I Reasonableness: {reasonable_l_i_count}/{checked_risks_count} mapped risks assessed reasonably (+/- 1 level).")
    else:
        l_i_feedback.insert(0, "L/I Reasonableness: No risks could be reliably mapped to key for comparison.")

    if len(risk_register) > 0:
        calc_score = POINTS_CONFIG["analysis_score_calculation"] * (correct_calc_count / len(risk_register))
        calc_feedback.insert(0, f"Score Calculation: {correct_calc_count}/{len(risk_register)} risks calculated score correctly based on own L*I.")
    else:
        calc_feedback.insert(0, "Score Calculation: No risks identified to check calculation.")


    return l_i_score + calc_score, l_i_feedback + calc_feedback


def evaluate_prioritization_and_response(risk_register):
    """Evaluates Top 3 identification and response strategy fields."""
    top_3_score = 0
    null_handling_score = 0
    response_logic_score = 0
    top_3_feedback = []
    null_handling_feedback = []
    response_logic_feedback = []

    if not risk_register:
        return 0, ["No risks identified, cannot evaluate prioritization/response."]

    # Sort risks by candidate's score
    try:
        sorted_risks = sorted([r for r in risk_register if isinstance(r.get("risk_score"), (int, float))],
                              key=lambda x: x["risk_score"], reverse=True)
    except Exception as e:
         return 0, [f"Error sorting risks by score: {e}. Ensure risk_score is a number."]


    # Determine the threshold score for Top 3 (handling ties)
    top_score_threshold = -1
    if len(sorted_risks) > 0:
        if len(sorted_risks) <= 3:
            top_score_threshold = sorted_risks[-1]["risk_score"] if sorted_risks else -1
        else:
            top_score_threshold = sorted_risks[2]["risk_score"] # Score of the 3rd item

    # Identify candidate's intended Top risks
    candidate_top_risk_ids = {r.get("risk_id") for r in sorted_risks if r.get("risk_score") >= top_score_threshold}
    if not candidate_top_risk_ids:
         top_3_feedback.append("Could not determine Top 3 risks based on scores.")


    top_risks_correctly_identified = 0
    non_top_risks_correctly_null = 0
    top_risks_with_valid_response = 0
    checked_non_top_count = 0
    checked_top_count = 0

    for i, risk in enumerate(risk_register):
        risk_id = risk.get("risk_id", f"Risk_{i+1}")
        is_candidate_top = risk_id in candidate_top_risk_ids
        response_type = risk.get("response_strategy_type")
        response_desc = risk.get("response_strategy_description")
        response_owner = risk.get("potential_owner_role")

        has_response_data = response_type is not None or response_desc is not None or response_owner is not None
        response_fields_are_null = response_type is None and response_desc is None and response_owner is None

        if is_candidate_top:
            checked_top_count += 1
            # Check if response fields are present for top risks
            if has_response_data:
                top_risks_correctly_identified += 1
                # Check response logic (valid type, non-empty desc/owner)
                type_valid = isinstance(response_type, str) and response_type.lower() in ALLOWED_RESPONSE_TYPES
                desc_present = isinstance(response_desc, str) and bool(response_desc.strip())
                owner_present = isinstance(response_owner, str) and bool(response_owner.strip())

                if type_valid and desc_present and owner_present:
                    top_risks_with_valid_response += 1
                else:
                    errs = []
                    if not type_valid: errs.append(f"Invalid/missing type ('{response_type}')")
                    if not desc_present: errs.append("Missing/empty description")
                    if not owner_present: errs.append("Missing/empty owner")
                    response_logic_feedback.append(f"Risk {risk_id} (Top Risk): Issues - {'; '.join(errs)}.")
            else:
                top_3_feedback.append(f"Risk {risk_id} (Identified as Top Risk by score {risk.get('risk_score')}): Missing response strategy fields.")
        else:
            checked_non_top_count += 1
            # Check if response fields are null for non-top risks
            if response_fields_are_null:
                non_top_risks_correctly_null += 1
            else:
                null_handling_feedback.append(f"Risk {risk_id} (Not Top Risk): Response fields should be null but found data (Type: {response_type}, Desc: {response_desc}, Owner: {response_owner}).")

    # Calculate Scores
    if checked_top_count > 0:
        top_3_score = POINTS_CONFIG["prioritization_top_3_identification"] * (top_risks_correctly_identified / checked_top_count)
        response_logic_score = POINTS_CONFIG["response_strategy_logic"] * (top_risks_with_valid_response / checked_top_count)
        top_3_feedback.insert(0, f"Top Risk Identification: {top_risks_correctly_identified}/{checked_top_count} top risks had response fields populated.")
        response_logic_feedback.insert(0, f"Response Logic: {top_risks_with_valid_response}/{checked_top_count} top risks had valid response type, description, and owner.")
    else:
        top_3_feedback.insert(0, "Top Risk Identification: No top risks found or processed.")
        response_logic_feedback.insert(0, "Response Logic: No top risks found or processed.")


    if checked_non_top_count > 0:
        null_handling_score = POINTS_CONFIG["response_fields_null_handling"] * (non_top_risks_correctly_null / checked_non_top_count)
        null_handling_feedback.insert(0, f"Null Handling: {non_top_risks_correctly_null}/{checked_non_top_count} non-top risks correctly had null response fields.")
    else:
         # If all risks are top risks (e.g., <=3 identified), this score is maxed out by default
         if checked_top_count > 0 and checked_top_count == len(risk_register):
              null_handling_score = POINTS_CONFIG["response_fields_null_handling"]
              null_handling_feedback.insert(0, "Null Handling: All identified risks were Top risks, so null handling check is N/A (awarded full points).")
         else:
              null_handling_feedback.insert(0, "Null Handling: No non-top risks found or processed.")


    return top_3_score + null_handling_score + response_logic_score, top_3_feedback + null_handling_feedback + response_logic_feedback


def evaluate_formatting(submission_data, risk_register):
    """Checks adherence to specified formats (categories, types, data types)."""
    score = POINTS_CONFIG["formatting_adherence"] # Start with full points
    feedback = []
    issues_found = 0
    total_checks = 1 # Start with 1 check for exam_level

    # Check exam_level (already partially checked in structure)
    if submission_data.get("exam_level") != EXPECTED_EXAM_LEVEL:
        # Feedback already added in structure check
        issues_found +=1

    if not risk_register:
         feedback.append("Formatting: No risks to check formatting details.")
         # Return partial score if base structure was okay but no risks
         return score * (1 / total_checks) if total_checks > 0 else 0, feedback

    for i, risk in enumerate(risk_register):
        risk_id = risk.get("risk_id", f"Risk_{i+1}")
        category = risk.get("category", "")
        likelihood = risk.get("likelihood", "")
        impact = risk.get("impact", "")
        risk_score = risk.get("risk_score")
        response_type = risk.get("response_strategy_type")

        # Check Category
        total_checks += 1
        if not isinstance(category, str) or category.lower() not in ALLOWED_CATEGORIES:
            feedback.append(f"Risk {risk_id}: Invalid category '{category}'. Allowed: {ALLOWED_CATEGORIES}.")
            issues_found += 1

        # Check Likelihood/Impact format
        total_checks += 2
        if not isinstance(likelihood, str) or likelihood.lower() not in ALLOWED_LIKELIHOOD_IMPACT:
             feedback.append(f"Risk {risk_id}: Invalid likelihood format '{likelihood}'. Allowed: {ALLOWED_LIKELIHOOD_IMPACT}.")
             issues_found += 1
        if not isinstance(impact, str) or impact.lower() not in ALLOWED_LIKELIHOOD_IMPACT:
             feedback.append(f"Risk {risk_id}: Invalid impact format '{impact}'. Allowed: {ALLOWED_LIKELIHOOD_IMPACT}.")
             issues_found += 1

        # Check Risk Score data type
        total_checks += 1
        if not isinstance(risk_score, (int, float)):
             feedback.append(f"Risk {risk_id}: Invalid risk_score data type '{type(risk_score)}'. Expected number.")
             issues_found += 1

        # Check Response Type format (if not null)
        if response_type is not None:
            total_checks += 1
            if not isinstance(response_type, str) or response_type.lower() not in ALLOWED_RESPONSE_TYPES:
                feedback.append(f"Risk {risk_id}: Invalid response_strategy_type '{response_type}'. Allowed: {ALLOWED_RESPONSE_TYPES}.")
                issues_found += 1
        # Null check is handled in prioritization/response section

    # Calculate final formatting score
    if total_checks > 0:
        final_score = POINTS_CONFIG["formatting_adherence"] * (1 - (issues_found / total_checks))
    else:
        final_score = 0 # Should not happen if structure is valid

    if issues_found == 0:
        feedback.insert(0,"Formatting: All checked fields adhere to specified formats and constraints.")
    else:
         feedback.insert(0,f"Formatting: Found {issues_found} issues across {total_checks} checks.")

    return final_score, feedback


# --- Main Execution ---

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file.json> <answer_key_file.json>")
        sys.exit(1)

    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    results_file = "test_results.json"

    # Load files
    submission_data, error = load_json(submission_file)
    if error:
        print(error)
        # Create a minimal results file indicating the load error
        results = {"overall_score": 0, "error": error, "details": {}}
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        sys.exit(1)

    answer_key_data, error = load_json(answer_key_file)
    if error:
        print(error)
        # Create a minimal results file indicating the load error
        results = {"overall_score": 0, "error": error, "details": {}}
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        sys.exit(1)

    # --- Initialize Results ---
    total_score = 0
    results_details = {}

    # --- Evaluate ---

    # 1. Structure and Validity
    score, feedback, structure_valid = evaluate_structure_and_validity(submission_data)
    total_score += score
    results_details["structure_and_validity"] = {"score": round(score, 2), "feedback": feedback}

    if not structure_valid:
        print("Critical error: Submission structure is invalid. Evaluation halted.")
        results = {
            "overall_score": round(total_score, 2),
            "error": "Submission structure invalid.",
            "details": results_details
        }
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        sys.exit(1)

    # Prepare data for subsequent checks
    candidate_risk_register = submission_data.get("risk_register", [])
    answer_key_risks = answer_key_data.get("risk_register", [])
    # Create a dict for easy lookup of key risks by their description/category mapping
    # Also create a dict for easy lookup of key risk details by the mapped ID
    key_risk_map = {} # Maps candidate risk_id to KeyRisk_ID
    answer_key_risks_dict = {} # Maps KeyRisk_ID to the key risk data
    temp_key_risk_mapping = {} # Maps KeyRisk_ID to key risk data for initial population
    for i, risk in enumerate(answer_key_risks):
         # Use a generated ID if key risk doesn't have one (though our key does)
         key_id_ref = f"KeyRisk_Internal_{i+1}"
         # Attempt to map based on description/category from KEY_RISK_DEFINITIONS
         mapped_key_id = None
         desc_lower = risk.get("description","").lower()
         cat_lower = risk.get("category","").lower()
         for keywords, key_category, defined_key_id in KEY_RISK_DEFINITIONS:
              match_count = sum(1 for keyword in keywords if keyword in desc_lower)
              if match_count > 0 and cat_lower == key_category.lower():
                   mapped_key_id = defined_key_id
                   break # Assume first good match is enough for the key
         if mapped_key_id:
              temp_key_risk_mapping[mapped_key_id] = risk
              answer_key_risks_dict[mapped_key_id] = risk # Populate the final lookup dict


    # Map candidate risks
    for risk in candidate_risk_register:
        candidate_risk_id = risk.get("risk_id")
        if candidate_risk_id is not None:
            mapped_key_id = map_candidate_risk_to_key(risk)
            if mapped_key_id:
                key_risk_map[candidate_risk_id] = mapped_key_id


    # 2. Risk Identification
    score, feedback = evaluate_risk_identification(candidate_risk_register, key_risk_map)
    total_score += score
    results_details["risk_identification"] = {"score": round(score, 2), "feedback": feedback}

    # 3. Risk Analysis
    score, feedback = evaluate_risk_analysis(candidate_risk_register, key_risk_map, answer_key_risks_dict)
    total_score += score
    results_details["risk_analysis"] = {"score": round(score, 2), "feedback": feedback}

    # 4. Prioritization and Response
    score, feedback = evaluate_prioritization_and_response(candidate_risk_register)
    total_score += score
    results_details["prioritization_and_response"] = {"score": round(score, 2), "feedback": feedback}

    # 5. Formatting Adherence
    score, feedback = evaluate_formatting(submission_data, candidate_risk_register)
    total_score += score
    results_details["formatting_adherence"] = {"score": round(score, 2), "feedback": feedback}


    # --- Finalize Results ---
    # Ensure score doesn't exceed 100 due to potential rounding or logic overlaps
    overall_percentage = min(round(total_score, 2), 100.0)

    final_results = {
        "overall_score": overall_percentage,
        "details": results_details
    }

    # Save results
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2)
        print(f"Evaluation complete. Results saved to {results_file}")
    except Exception as e:
        print(f"Error writing results file: {e}")
        # Also print results to console as fallback
        print("\n--- Results ---")
        print(json.dumps(final_results, indent=2))

    sys.exit(0)