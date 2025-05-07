import json
import argparse
import re
import os
from decimal import Decimal, InvalidOperation

# --- Configuration ---
MAX_SCORE = 100

# Points allocation
POINTS_STRUCTURE = 10
POINTS_ISSUE_IDENTIFIED = 5 # Per issue, max 4 issues = 20
POINTS_FEE_AMOUNT = 15
POINTS_FEE_LOGIC = 10
POINTS_DATE_VALID = 10
POINTS_DATE_REFERENCE = 10
POINTS_TRAVEL_AMOUNT = 10
POINTS_TRAVEL_REFERENCE = 5
POINTS_SURCHARGE_ISSUE = 5
POINTS_SURCHARGE_PROPOSAL = 5

# Keywords for issue identification (lowercase)
ISSUE_KEYWORDS = {
    "budget_fee": ["budget", "fee", "cost", "price", "4500", "7302.50", "gap", "discrepancy"],
    "date_conflict": ["date", "schedule", "september", "unavailable", "availability", "conflict", "sep 9", "sep 13"],
    "surcharge_trigger": ["participant", "18", "15", "surcharge", "group size", "exceeds", "maximum"],
    "travel_costs": ["travel", "on-site", "techcity", "400", "expense"]
}

# Keywords for reference checking (lowercase)
REFERENCE_KEYWORDS = {
    "fee": ["section 2", "rate", "material", "surcharge", "calculation", "participant"],
    "date": ["section 4", "availability", "unavailable", "schedule", "dr. reed", "alex reed"],
    "travel": ["section 3", "travel", "techcity", "400", "on-site", "estimate"],
    "surcharge": ["section 2", "surcharge", "15%", "group size", "16-20"]
}

# Valid date pairs from the key (derived from Section 4 availability)
VALID_DATE_PAIRS = [
    ("2024-09-16", "2024-09-17"),
    ("2024-09-18", "2024-09-19"), # Assuming 2 consecutive days needed
    ("2024-09-19", "2024-09-20"),
    ("2024-09-23", "2024-09-24"),
    ("2024-09-25", "2024-09-26"),
    ("2024-09-26", "2024-09-27"),
]

# --- Helper Functions ---

def load_json(filepath):
    """Loads a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {filepath}: {e}")
        return None

def save_json(data, filepath):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Results saved to {filepath}")
    except Exception as e:
        print(f"Error: Could not write results to {filepath}. Details: {e}")

def extract_decimal(text):
    """Extracts the first decimal number found in a string."""
    if not isinstance(text, str):
        return None
    # Remove currency symbols, commas, etc.
    cleaned_text = re.sub(r'[$,]', '', text)
    # Find numbers like XXXX.XX or XXXX
    match = re.search(r'\b\d+(\.\d+)?\b', cleaned_text)
    if match:
        try:
            return Decimal(match.group(0))
        except InvalidOperation:
            return None
    return None

def extract_dates(text):
    """Extracts YYYY-MM-DD dates from a string."""
    if not isinstance(text, str):
        return []
    return re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text)

def check_keywords(text, keywords):
    """Checks if any of the keywords are present in the text (case-insensitive)."""
    if not isinstance(text, str) or not keywords:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

def get_proposal_by_point(proposed_terms, point_name):
    """Finds a proposal item by its 'point' name (case-insensitive partial match)."""
    if not isinstance(proposed_terms, list):
        return None
    point_name_lower = point_name.lower()
    for term in proposed_terms:
        if isinstance(term, dict) and 'point' in term and isinstance(term['point'], str):
            if point_name_lower in term['point'].lower():
                return term
    return None

# --- Evaluation Functions ---

def evaluate_structure(submission_data):
    """Checks if the main keys exist in the submission."""
    score = 0
    details = {}
    required_keys = ["scenario_analysis", "negotiation_points", "proposed_terms"]
    missing_keys = [key for key in required_keys if key not in submission_data]

    if not missing_keys and \
       isinstance(submission_data.get("scenario_analysis"), dict) and \
       isinstance(submission_data.get("negotiation_points"), list) and \
       isinstance(submission_data.get("proposed_terms"), list):
        score = POINTS_STRUCTURE
        details["structure_check"] = "All main sections present and have correct basic types."
    else:
        details["structure_check"] = f"Missing or incorrect type for main sections: {missing_keys}"

    return score, details

def evaluate_issues(submission_data):
    """Evaluates the identification of potential issues."""
    score = 0
    details = {"identified_issues": {}}
    issues_found_count = 0
    issues_list = submission_data.get("scenario_analysis", {}).get("potential_issues_or_deviations", [])

    if not isinstance(issues_list, list):
        details["issues_check"] = "potential_issues_or_deviations is not a list or is missing."
        return score, details, issues_found_count

    identified_flags = {key: False for key in ISSUE_KEYWORDS}

    for issue_text in issues_list:
        if not isinstance(issue_text, str): continue
        text_lower = issue_text.lower()
        for key, keywords in ISSUE_KEYWORDS.items():
            if not identified_flags[key] and any(kw in text_lower for kw in keywords):
                details["identified_issues"][key] = f"Correctly identified ({issue_text[:50]}...)"
                identified_flags[key] = True
                score += POINTS_ISSUE_IDENTIFIED
                issues_found_count += 1
                break # Avoid double counting if one string matches multiple issues

    for key, identified in identified_flags.items():
        if not identified:
            details["identified_issues"][key] = "Not identified or description insufficient."

    details["issues_summary"] = f"Identified {issues_found_count} out of 4 core issues."
    return score, details, issues_found_count

def evaluate_fee(submission_data, key_data):
    """Evaluates the proposed fee amount and supporting reference."""
    score = 0
    details = {}
    amount_correct = False
    logic_reference_present = False

    proposal_item = get_proposal_by_point(submission_data.get("proposed_terms"), "Fee/Budget")
    key_item = get_proposal_by_point(key_data.get("proposed_terms"), "Fee/Budget")

    if not proposal_item or not key_item:
        details["fee_check"] = "Fee/Budget proposal not found in submission or key."
        return score, details, amount_correct

    # Check Amount
    key_fee_str = key_item.get("proposal")
    key_fee = extract_decimal(key_fee_str)
    submission_fee_str = proposal_item.get("proposal")
    submission_fee = extract_decimal(submission_fee_str)

    if key_fee is not None and submission_fee is not None and submission_fee == key_fee:
        score += POINTS_FEE_AMOUNT
        details["fee_amount"] = f"Correct fee amount proposed (${key_fee})."
        amount_correct = True
    else:
        details["fee_amount"] = f"Incorrect or missing fee amount. Expected approx. ${key_fee}, Found: ${submission_fee} in '{submission_fee_str}'."

    # Check Reference Logic
    reference = proposal_item.get("supporting_data_reference")
    if check_keywords(reference, REFERENCE_KEYWORDS["fee"]):
        score += POINTS_FEE_LOGIC
        details["fee_reference"] = "Supporting reference includes relevant keywords (rates, surcharge, etc.)."
        logic_reference_present = True
    else:
        details["fee_reference"] = "Supporting reference missing or lacks keywords indicating correct logic."

    return score, details, amount_correct

def evaluate_dates(submission_data, key_data):
    """Evaluates the proposed dates and supporting reference."""
    score = 0
    details = {}
    valid_date_proposed = False
    reference_present = False

    proposal_item = get_proposal_by_point(submission_data.get("proposed_terms"), "Training Dates")

    if not proposal_item:
        details["date_check"] = "Training Dates proposal not found."
        return score, details, valid_date_proposed

    # Check Dates
    proposal_text = proposal_item.get("proposal")
    proposed_dates = extract_dates(proposal_text)

    # Check if any proposed pair matches a valid pair
    for i in range(len(proposed_dates) - 1):
        pair = (proposed_dates[i], proposed_dates[i+1])
        if pair in VALID_DATE_PAIRS:
            score += POINTS_DATE_VALID
            details["date_proposal"] = f"Valid date pair proposed: {pair}."
            valid_date_proposed = True
            break # Found one valid pair

    if not valid_date_proposed:
         details["date_proposal"] = f"No valid date pair found in proposal: '{proposal_text}'. Valid pairs: {VALID_DATE_PAIRS}"

    # Check Reference
    reference = proposal_item.get("supporting_data_reference")
    if check_keywords(reference, REFERENCE_KEYWORDS["date"]):
        score += POINTS_DATE_REFERENCE
        details["date_reference"] = "Supporting reference includes relevant keywords (Section 4, availability, etc.)."
        reference_present = True
    else:
        details["date_reference"] = "Supporting reference missing or lacks keywords about availability."

    return score, details, valid_date_proposed

def evaluate_travel(submission_data, key_data):
    """Evaluates the proposed travel costs and reference."""
    score = 0
    details = {}
    amount_correct = False

    proposal_item = get_proposal_by_point(submission_data.get("proposed_terms"), "Travel Costs")
    key_item = get_proposal_by_point(key_data.get("proposed_terms"), "Travel Costs")

    if not proposal_item or not key_item:
        # Also check if travel cost was mentioned within the Fee/Budget proposal
        fee_proposal_item = get_proposal_by_point(submission_data.get("proposed_terms"), "Fee/Budget")
        if fee_proposal_item and check_keywords(fee_proposal_item.get("proposal",""), ["travel", "400"]):
             proposal_item = fee_proposal_item # Evaluate travel within fee proposal
             details["travel_check"] = "Travel cost mentioned within Fee/Budget proposal."
        else:
            details["travel_check"] = "Travel Costs proposal point not found (or travel not mentioned in Fee proposal)."
            return score, details, amount_correct

    # Check Amount
    key_travel_str = key_item.get("proposal")
    key_travel = extract_decimal(key_travel_str)
    submission_travel_str = proposal_item.get("proposal") # Might be fee proposal string now
    submission_travel = extract_decimal(submission_travel_str) # Might extract main fee

    # More robust check for travel cost within the string
    if key_travel is not None and check_keywords(submission_travel_str, [str(int(key_travel))]):
        score += POINTS_TRAVEL_AMOUNT
        details["travel_amount"] = f"Correct travel amount (${key_travel}) mentioned."
        amount_correct = True
    else:
        details["travel_amount"] = f"Incorrect or missing travel amount. Expected approx. ${key_travel} to be mentioned in '{submission_travel_str}'."

    # Check Reference
    reference = proposal_item.get("supporting_data_reference")
    if check_keywords(reference, REFERENCE_KEYWORDS["travel"]):
        score += POINTS_TRAVEL_REFERENCE
        details["travel_reference"] = "Supporting reference includes relevant keywords (Section 3, travel, etc.)."
    else:
        details["travel_reference"] = "Supporting reference missing or lacks keywords about travel cost source."

    return score, details, amount_correct

def evaluate_surcharge(submission_data):
    """Evaluates identification and addressing of the surcharge."""
    score = 0
    details = {}
    issue_identified = False
    proposal_addressed = False

    # Check if identified as issue
    issues_list = submission_data.get("scenario_analysis", {}).get("potential_issues_or_deviations", [])
    if isinstance(issues_list, list):
        for issue_text in issues_list:
             if check_keywords(issue_text, ISSUE_KEYWORDS["surcharge_trigger"]):
                 score += POINTS_SURCHARGE_ISSUE
                 details["surcharge_issue"] = "Surcharge trigger correctly identified as an issue."
                 issue_identified = True
                 break
    if not issue_identified:
        # Check negotiation points as alternative
        neg_points = submission_data.get("negotiation_points", [])
        if isinstance(neg_points, list):
            for point in neg_points:
                if isinstance(point, dict) and check_keywords(point.get("point","") + point.get("details",""), ISSUE_KEYWORDS["surcharge_trigger"]):
                    score += POINTS_SURCHARGE_ISSUE
                    details["surcharge_issue"] = "Surcharge trigger correctly identified as a negotiation point."
                    issue_identified = True
                    break

    if not issue_identified:
        details["surcharge_issue"] = "Surcharge trigger (due to 18 participants) not clearly identified as an issue/negotiation point."

    # Check if addressed in proposal (usually within Fee or as separate point)
    fee_proposal = get_proposal_by_point(submission_data.get("proposed_terms"), "Fee/Budget")
    surcharge_proposal = get_proposal_by_point(submission_data.get("proposed_terms"), "Surcharge") # Allow specific point name
    participant_proposal = get_proposal_by_point(submission_data.get("proposed_terms"), "Participant") # Allow specific point name

    addressed_text = ""
    if fee_proposal: addressed_text += fee_proposal.get("proposal","") + fee_proposal.get("supporting_data_reference","")
    if surcharge_proposal: addressed_text += surcharge_proposal.get("proposal","") + surcharge_proposal.get("supporting_data_reference","")
    if participant_proposal: addressed_text += participant_proposal.get("proposal","") + participant_proposal.get("supporting_data_reference","")

    if check_keywords(addressed_text, REFERENCE_KEYWORDS["surcharge"]):
        score += POINTS_SURCHARGE_PROPOSAL
        details["surcharge_proposal"] = "Surcharge correctly mentioned/referenced in proposed terms."
        proposal_addressed = True
    else:
        details["surcharge_proposal"] = "Surcharge not clearly addressed or referenced in proposed terms."

    return score, details

def determine_pass_fail(results, issues_found_count, fee_amount_correct, valid_date_proposed, travel_amount_correct):
    """Determines pass/fail status based on critical criteria."""

    fail_reasons = []

    # Automatic Fail Conditions from evaluation_information
    if not fee_amount_correct:
        # Check if fee is grossly incorrect (more than 5% deviation - arbitrary threshold for 'grossly')
        # This requires extracting the proposed fee again, handle carefully if missing
        key_fee = extract_decimal(results["evaluation_details"]["fee"]["fee_amount"].split('$')[-1].split('.')[0] if "fee_amount" in results["evaluation_details"]["fee"] else "0")
        submission_fee_str = get_proposal_by_point(results.get("submission_data_preview",{}).get("proposed_terms"), "Fee/Budget")
        submission_fee = extract_decimal(submission_fee_str.get("proposal","0") if submission_fee_str else "0")
        if key_fee and submission_fee and abs(submission_fee - key_fee) / key_fee > Decimal('0.05'):
             fail_reasons.append("Grossly incorrect fee calculation (>5% deviation).")
        elif not fee_amount_correct: # If not grossly wrong, just note it wasn't exact
             fail_reasons.append("Fee calculation was not exactly correct.")


    if not valid_date_proposed:
        fail_reasons.append("Did not propose any valid alternative dates.")

    # Check if critical issues were missed (Budget and Date are critical)
    budget_issue_identified = "Correctly identified" in results["evaluation_details"]["issues"]["identified_issues"].get("budget_fee", "")
    date_issue_identified = "Correctly identified" in results["evaluation_details"]["issues"]["identified_issues"].get("date_conflict", "")

    if not budget_issue_identified:
        fail_reasons.append("Failed to identify the critical Budget vs. Fee issue.")
    if not date_issue_identified:
        fail_reasons.append("Failed to identify the critical Date Conflict issue.")

    # Check if travel cost was completely omitted (check if amount was correct OR if point existed)
    travel_point_exists = get_proposal_by_point(results.get("submission_data_preview",{}).get("proposed_terms"), "Travel Costs") is not None
    travel_in_fee = check_keywords(get_proposal_by_point(results.get("submission_data_preview",{}).get("proposed_terms"), "Fee/Budget").get("proposal","") if get_proposal_by_point(results.get("submission_data_preview",{}).get("proposed_terms"), "Fee/Budget") else "", ["travel", "400"])

    if not travel_amount_correct and not travel_point_exists and not travel_in_fee:
         fail_reasons.append("Completely omitted mentioning/proposing the mandatory travel costs.")

    # Check minimum identified issues (as per passing criteria)
    min_issues_required = 3
    if issues_found_count < min_issues_required:
        fail_reasons.append(f"Failed to identify minimum required issues (found {issues_found_count}, need {min_issues_required}).")


    if not fail_reasons:
        return "Pass", "Candidate met minimum requirements for critical items."
    else:
        return "Fail", "Candidate failed to meet critical requirements: " + " | ".join(fail_reasons)


# --- Main Evaluation Script ---

def evaluate_submission(submission_data, key_data):
    """Performs the full evaluation."""
    results = {
        "overall_score": 0,
        "pass_status": "Fail",
        "pass_fail_reason": "Evaluation did not complete.",
        "score_details": {},
        "evaluation_details": {},
        "submission_data_preview": { # Include parts of submission for context
             "scenario_analysis": submission_data.get("scenario_analysis",{}),
             "negotiation_points": submission_data.get("negotiation_points",[]),
             "proposed_terms": submission_data.get("proposed_terms",[])
        }
    }
    total_score = 0

    # 1. Evaluate Structure
    structure_score, structure_details = evaluate_structure(submission_data)
    total_score += structure_score
    results["score_details"]["structure"] = structure_score
    results["evaluation_details"]["structure"] = structure_details
    if structure_score == 0:
        results["pass_fail_reason"] = "Failed basic structure check (missing sections)."
        return results # Cannot proceed if structure is wrong

    # 2. Evaluate Issue Identification
    issues_score, issues_details, issues_found_count = evaluate_issues(submission_data)
    total_score += issues_score
    results["score_details"]["issues_identified"] = issues_score
    results["evaluation_details"]["issues"] = issues_details

    # 3. Evaluate Fee Proposal
    fee_score, fee_details, fee_amount_correct = evaluate_fee(submission_data, key_data)
    total_score += fee_score
    results["score_details"]["fee_proposal"] = fee_score
    results["evaluation_details"]["fee"] = fee_details

    # 4. Evaluate Date Proposal
    date_score, date_details, valid_date_proposed = evaluate_dates(submission_data, key_data)
    total_score += date_score
    results["score_details"]["date_proposal"] = date_score
    results["evaluation_details"]["date"] = date_details

    # 5. Evaluate Travel Cost Proposal
    travel_score, travel_details, travel_amount_correct = evaluate_travel(submission_data, key_data)
    total_score += travel_score
    results["score_details"]["travel_cost_proposal"] = travel_score
    results["evaluation_details"]["travel"] = travel_details

    # 6. Evaluate Surcharge Handling
    surcharge_score, surcharge_details = evaluate_surcharge(submission_data)
    total_score += surcharge_score
    results["score_details"]["surcharge_handling"] = surcharge_score
    results["evaluation_details"]["surcharge"] = surcharge_details

    # Calculate Overall Score
    # Ensure score doesn't exceed max due to potential overlaps or future changes
    total_score = min(total_score, MAX_SCORE)
    results["overall_score"] = round((total_score / MAX_SCORE) * 100, 2)

    # Determine Pass/Fail Status
    pass_status, reason = determine_pass_fail(results, issues_found_count, fee_amount_correct, valid_date_proposed, travel_amount_correct)
    results["pass_status"] = pass_status
    results["pass_fail_reason"] = reason

    return results

# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Training Contract Negotiation (Basic) Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    submission_data = load_json(args.submission_file)
    key_data = load_json(args.key_file)

    results_json = {
        "overall_score": 0,
        "pass_status": "Fail",
        "pass_fail_reason": "Error during processing.",
        "score_details": {},
        "evaluation_details": {"error": "Could not load input files or critical error occurred."}
    }

    if submission_data and key_data:
        # Basic check for JSON validity passed during load
        # Check candidate ID format (simple check if it's not the placeholder)
        candidate_id = submission_data.get("candidate_id", "CANDIDATE_UNIQUE_ID")
        if candidate_id == "CANDIDATE_UNIQUE_ID" or not isinstance(candidate_id, str) or not candidate_id.strip():
             print("Warning: Candidate ID is missing or uses the placeholder value.")
             # Optionally add this warning to results

        results_json = evaluate_submission(submission_data, key_data)
    elif not submission_data:
         results_json["pass_fail_reason"] = "Failed to load or parse submission file."
         results_json["evaluation_details"]["error"] = f"Could not load or parse {args.submission_file}"
    elif not key_data:
         results_json["pass_fail_reason"] = "Failed to load or parse key file."
         results_json["evaluation_details"]["error"] = f"Could not load or parse {args.key_file}"


    # Save results
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_filepath = os.path.join(script_dir, "test_results.json")
    save_json(results_json, results_filepath)