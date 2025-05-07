import json
import argparse
import sys
import os
import re

# --- Configuration ---

# Define points for each criterion
POINTS_CONFIG = {
    "format_valid_json": 5, # Basic check if file loads
    "format_candidate_id_present": 1,
    "format_case_reference_correct": 1,
    "core_facts_complainant_name": 1,
    "core_facts_respondent_name": 1,
    "core_facts_allegation_basis": 1,
    "core_facts_policy_name": 1,
    "summarization_complaint_desc": 2,
    "summarization_policy_section": 2,
    "key_statements_complainant_min_count": 2,
    "key_statements_respondent_min_count": 2,
    "key_issues_identified": 3, # Points for identifying the core issues
}

# Calculate total possible points
TOTAL_POSSIBLE_POINTS = sum(POINTS_CONFIG.values())

# Minimum required counts for key statements
MIN_COMPLAINANT_STATEMENTS = 3
MIN_RESPONDENT_STATEMENTS = 4

# Placeholder texts to check against (should not be present in submission)
PLACEHOLDER_STRINGS = [
    "Identify from Case File",
    "Provide a 1-2 sentence summary",
    "Summarize key point",
    "Identify the name/title",
    "Briefly summarize the main point",
    "Note any direct contradictions",
    "YOUR_ID_HERE"
]

# Keywords to look for in identified issues (case-insensitive)
ISSUE_KEYWORDS = {
    "contradiction_comment": [r"comment", r"contradict|denial|denied|disagree"],
    "missing_email": [r"email", r"missing|provide|recall|sent|receive"]
}

# --- Helper Functions ---

def load_json_file(filepath):
    """Loads a JSON file and returns its content."""
    if not os.path.exists(filepath):
        return None, f"Error: File not found at {filepath}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON format in {filepath}. Details: {e}"
    except Exception as e:
        return None, f"Error: Could not read file {filepath}. Details: {e}"

def check_placeholder(value):
    """Checks if a string value contains any placeholder text."""
    if not isinstance(value, str):
        return False # Not a string, can't contain placeholder text
    value_lower = value.lower()
    for placeholder in PLACEHOLDER_STRINGS:
        if placeholder.lower() in value_lower:
            return True
    return False

def check_keywords(text_list, keyword_sets):
    """Checks if a list of strings contains required keyword combinations."""
    if not isinstance(text_list, list):
        return False

    found_sets = set()
    combined_text = " ".join(text_list).lower() # Combine all strings for easier searching

    for key, patterns in keyword_sets.items():
        # Check if all patterns for a given key are found in the combined text
        if all(re.search(pattern, combined_text) for pattern in patterns):
            found_sets.add(key)

    return len(found_sets) == len(keyword_sets) # Return True only if all required sets are found

# --- Evaluation Functions ---

def evaluate_submission(submission_data, key_data):
    """Evaluates the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission_data.get("candidate_id", "MISSING"),
        "evaluation_details": {},
        "achieved_points": 0,
        "total_possible_points": TOTAL_POSSIBLE_POINTS,
        "overall_score": 0.0,
        "errors": []
    }
    points = 0

    # --- Requirement 1: Valid Submission Format ---
    # JSON validity is checked during loading. Add points for loading successfully.
    results["evaluation_details"]["format_valid_json"] = {
        "description": "Submission file is valid JSON",
        "points_earned": POINTS_CONFIG["format_valid_json"],
        "max_points": POINTS_CONFIG["format_valid_json"],
        "passed": True
    }
    points += POINTS_CONFIG["format_valid_json"]

    # Check candidate_id presence and non-placeholder value
    candidate_id = submission_data.get("candidate_id")
    candidate_id_present = bool(candidate_id) and not check_placeholder(candidate_id)
    points_candidate_id = POINTS_CONFIG["format_candidate_id_present"] if candidate_id_present else 0
    results["evaluation_details"]["format_candidate_id_present"] = {
        "description": "Candidate ID is present and not a placeholder",
        "points_earned": points_candidate_id,
        "max_points": POINTS_CONFIG["format_candidate_id_present"],
        "passed": candidate_id_present
    }
    points += points_candidate_id

    # Check case_reference correctness
    sub_case_ref = submission_data.get("case_reference")
    key_case_ref = key_data.get("case_reference")
    case_ref_correct = sub_case_ref == key_case_ref
    points_case_ref = POINTS_CONFIG["format_case_reference_correct"] if case_ref_correct else 0
    results["evaluation_details"]["format_case_reference_correct"] = {
        "description": f"Case Reference matches key ('{key_case_ref}')",
        "points_earned": points_case_ref,
        "max_points": POINTS_CONFIG["format_case_reference_correct"],
        "passed": case_ref_correct,
        "submitted_value": sub_case_ref
    }
    points += points_case_ref

    # --- Requirement 2: Accurate Extraction of Core Facts ---
    sub_summary = submission_data.get("complaint_summary", {})
    key_summary = key_data.get("complaint_summary", {})

    # Complainant Name
    sub_comp_name = sub_summary.get("complainant_name")
    key_comp_name = key_summary.get("complainant_name")
    comp_name_correct = sub_comp_name == key_comp_name and not check_placeholder(sub_comp_name)
    points_comp_name = POINTS_CONFIG["core_facts_complainant_name"] if comp_name_correct else 0
    results["evaluation_details"]["core_facts_complainant_name"] = {
        "description": f"Complainant Name matches key ('{key_comp_name}')",
        "points_earned": points_comp_name,
        "max_points": POINTS_CONFIG["core_facts_complainant_name"],
        "passed": comp_name_correct,
        "submitted_value": sub_comp_name
    }
    points += points_comp_name

    # Respondent Name
    sub_resp_name = sub_summary.get("respondent_name")
    key_resp_name = key_summary.get("respondent_name")
    resp_name_correct = sub_resp_name == key_resp_name and not check_placeholder(sub_resp_name)
    points_resp_name = POINTS_CONFIG["core_facts_respondent_name"] if resp_name_correct else 0
    results["evaluation_details"]["core_facts_respondent_name"] = {
        "description": f"Respondent Name matches key ('{key_resp_name}')",
        "points_earned": points_resp_name,
        "max_points": POINTS_CONFIG["core_facts_respondent_name"],
        "passed": resp_name_correct,
        "submitted_value": sub_resp_name
    }
    points += points_resp_name

    # Allegation Basis
    sub_basis = sub_summary.get("allegation_basis")
    key_basis = key_summary.get("allegation_basis")
    basis_correct = sub_basis == key_basis and not check_placeholder(sub_basis)
    points_basis = POINTS_CONFIG["core_facts_allegation_basis"] if basis_correct else 0
    results["evaluation_details"]["core_facts_allegation_basis"] = {
        "description": f"Allegation Basis matches key ('{key_basis}')",
        "points_earned": points_basis,
        "max_points": POINTS_CONFIG["core_facts_allegation_basis"],
        "passed": basis_correct,
        "submitted_value": sub_basis
    }
    points += points_basis

    # Policy Name
    sub_policy = submission_data.get("relevant_policy", {})
    key_policy = key_data.get("relevant_policy", {})
    sub_policy_name = sub_policy.get("policy_name")
    key_policy_name = key_policy.get("policy_name")
    policy_name_correct = sub_policy_name == key_policy_name and not check_placeholder(sub_policy_name)
    points_policy_name = POINTS_CONFIG["core_facts_policy_name"] if policy_name_correct else 0
    results["evaluation_details"]["core_facts_policy_name"] = {
        "description": f"Policy Name matches key ('{key_policy_name}')",
        "points_earned": points_policy_name,
        "max_points": POINTS_CONFIG["core_facts_policy_name"],
        "passed": policy_name_correct,
        "submitted_value": sub_policy_name
    }
    points += points_policy_name

    # --- Requirement 3: Adequate Summarization ---
    # Complaint Description Summary
    sub_comp_desc = sub_summary.get("brief_description")
    # Check if it's a non-empty string and not a placeholder
    comp_desc_adequate = isinstance(sub_comp_desc, str) and len(sub_comp_desc.strip()) > 10 and not check_placeholder(sub_comp_desc)
    points_comp_desc = POINTS_CONFIG["summarization_complaint_desc"] if comp_desc_adequate else 0
    results["evaluation_details"]["summarization_complaint_desc"] = {
        "description": "Complaint Description is summarized (non-empty, non-placeholder, >10 chars)",
        "points_earned": points_comp_desc,
        "max_points": POINTS_CONFIG["summarization_complaint_desc"],
        "passed": comp_desc_adequate,
        "submitted_value": sub_comp_desc
    }
    points += points_comp_desc

    # Policy Section Summary
    sub_policy_summary = sub_policy.get("relevant_section_summary")
    # Check if it's a non-empty string and not a placeholder
    policy_summary_adequate = isinstance(sub_policy_summary, str) and len(sub_policy_summary.strip()) > 10 and not check_placeholder(sub_policy_summary)
    points_policy_summary = POINTS_CONFIG["summarization_policy_section"] if policy_summary_adequate else 0
    results["evaluation_details"]["summarization_policy_section"] = {
        "description": "Policy Section is summarized (non-empty, non-placeholder, >10 chars)",
        "points_earned": points_policy_summary,
        "max_points": POINTS_CONFIG["summarization_policy_section"],
        "passed": policy_summary_adequate,
        "submitted_value": sub_policy_summary
    }
    points += points_policy_summary

    # --- Requirement 4: Identification of Key Statements (Minimum Count) ---
    sub_statements = submission_data.get("key_statements", {})
    sub_comp_statements = sub_statements.get("complainant", [])
    sub_resp_statements = sub_statements.get("respondent", [])

    # Check complainant statements count
    comp_statements_count_met = isinstance(sub_comp_statements, list) and len(sub_comp_statements) >= MIN_COMPLAINANT_STATEMENTS
    points_comp_statements = POINTS_CONFIG["key_statements_complainant_min_count"] if comp_statements_count_met else 0
    results["evaluation_details"]["key_statements_complainant_min_count"] = {
        "description": f"Complainant Key Statements meet minimum count ({MIN_COMPLAINANT_STATEMENTS})",
        "points_earned": points_comp_statements,
        "max_points": POINTS_CONFIG["key_statements_complainant_min_count"],
        "passed": comp_statements_count_met,
        "submitted_count": len(sub_comp_statements) if isinstance(sub_comp_statements, list) else 0
    }
    points += points_comp_statements

    # Check respondent statements count
    resp_statements_count_met = isinstance(sub_resp_statements, list) and len(sub_resp_statements) >= MIN_RESPONDENT_STATEMENTS
    points_resp_statements = POINTS_CONFIG["key_statements_respondent_min_count"] if resp_statements_count_met else 0
    results["evaluation_details"]["key_statements_respondent_min_count"] = {
        "description": f"Respondent Key Statements meet minimum count ({MIN_RESPONDENT_STATEMENTS})",
        "points_earned": points_resp_statements,
        "max_points": POINTS_CONFIG["key_statements_respondent_min_count"],
        "passed": resp_statements_count_met,
        "submitted_count": len(sub_resp_statements) if isinstance(sub_resp_statements, list) else 0
    }
    points += points_resp_statements

    # --- Requirement 5: Identification of Key Issues ---
    sub_issues = submission_data.get("identified_inconsistencies_or_missing_info", [])
    key_issues = key_data.get("identified_inconsistencies_or_missing_info", [])

    # Check if the submission is just the "None identified" placeholder
    is_none_identified = any("none identified" in str(item).lower() for item in sub_issues)

    # Check if the key issues are mentioned using keywords
    issues_identified_correctly = False
    if isinstance(sub_issues, list) and not is_none_identified:
        issues_identified_correctly = check_keywords(sub_issues, ISSUE_KEYWORDS)

    points_key_issues = POINTS_CONFIG["key_issues_identified"] if issues_identified_correctly else 0
    results["evaluation_details"]["key_issues_identified"] = {
        "description": "Key inconsistencies/missing info identified (Comment contradiction AND Email issue)",
        "points_earned": points_key_issues,
        "max_points": POINTS_CONFIG["key_issues_identified"],
        "passed": issues_identified_correctly,
        "submitted_value": sub_issues
    }
    points += points_key_issues

    # --- Final Score Calculation ---
    results["achieved_points"] = points
    if TOTAL_POSSIBLE_POINTS > 0:
        results["overall_score"] = round((points / TOTAL_POSSIBLE_POINTS) * 100, 2)
    else:
        results["overall_score"] = 0.0 # Avoid division by zero

    return results

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Evaluate EO Basic Report Preparation Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file (e.g., test_submission.json)")
    parser.add_argument("key_file", help="Path to the answer key JSON file (e.g., answer_key.json)")
    args = parser.parse_args()

    # Load submission file
    submission_data, error = load_json_file(args.submission_file)
    if error:
        print(error, file=sys.stderr)
        # Create a basic error result file
        error_results = {
            "candidate_id": "UNKNOWN",
            "evaluation_details": {
                 "format_valid_json": {
                    "description": "Submission file is valid JSON",
                    "points_earned": 0,
                    "max_points": POINTS_CONFIG["format_valid_json"],
                    "passed": False,
                    "error": error
                }
            },
            "achieved_points": 0,
            "total_possible_points": TOTAL_POSSIBLE_POINTS,
            "overall_score": 0.0,
            "errors": [error]
        }
        try:
            with open("test_results.json", 'w', encoding='utf-8') as f:
                json.dump(error_results, f, indent=2)
            print("Evaluation failed. Basic results saved to test_results.json")
        except Exception as write_e:
             print(f"Failed to write error results file: {write_e}", file=sys.stderr)
        sys.exit(1)


    # Load answer key file
    key_data, error = load_json_file(args.key_file)
    if error:
        print(error, file=sys.stderr)
        # Cannot proceed without the key
        sys.exit(1)

    # Perform evaluation
    evaluation_results = evaluate_submission(submission_data, key_data)

    # Save results
    try:
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2)
        print("Evaluation complete. Results saved to test_results.json")
    except Exception as e:
        print(f"Error saving results to test_results.json: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()