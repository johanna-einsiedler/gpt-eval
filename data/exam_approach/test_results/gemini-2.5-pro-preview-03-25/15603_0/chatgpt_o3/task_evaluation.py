# task_evaluation.py
import json
import argparse
import os
import re # Using regex for slightly more flexible keyword checking

def load_json(filepath):
    """Loads a JSON file with error handling."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}. Details: {e}")
        return None

def check_keywords(text, keywords, required_count=1, case_sensitive=False):
    """Checks if a minimum number of keywords are present in the text."""
    if not text or not keywords:
        return False
    
    found_count = 0
    flags = 0 if case_sensitive else re.IGNORECASE
    
    # Ensure text is a string
    text_str = str(text)

    for keyword in keywords:
        # Use word boundaries (\b) to avoid partial matches within words
        # Escape special regex characters in keyword if necessary
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_str, flags):
            found_count += 1
            
    return found_count >= required_count

def evaluate_submission(submission_data, key_data):
    """Evaluates the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission_data.get("candidate_id", "ID_MISSING"),
        "overall_score": 0.0,
        "evaluation_details": [],
        "feedback": []
    }

    # --- Basic Structure Validation ---
    if not isinstance(submission_data, dict):
        results["feedback"].append("Submission is not a valid JSON object.")
        return results # Cannot proceed
    if "identified_issues" not in submission_data:
        results["feedback"].append("Submission JSON missing required 'identified_issues' key.")
        return results # Cannot proceed
    if not isinstance(submission_data["identified_issues"], list):
         results["feedback"].append("'identified_issues' should be a list/array.")
         # Attempt to proceed if possible, but score might be 0
         submission_data["identified_issues"] = []


    key_issues = key_data.get("identified_issues", [])
    submitted_issues = submission_data.get("identified_issues", [])
    
    if not key_issues:
        results["feedback"].append("Answer key is missing 'identified_issues'. Cannot evaluate.")
        return results

    max_score = len(key_issues)
    achieved_score = 0
    
    # Keep track of which submitted issues have been matched to avoid double counting
    matched_submission_indices = set()

    # Define keywords for matching each key issue (adjust as needed for robustness)
    # These keywords target the core concept of each expected answer.
    key_issue_match_criteria = {
        "ISSUE_01": {"ref": ["4.1.3"], "summary": ["prior history", "treatment", "ambiguous", "unclear", "vague"], "next_step": ["PI", "Investigator", "clarification", "query sponsor"]},
        "ISSUE_02": {"ref": ["6.2", "footnote"], "summary": ["fasting", "post-dose", "PK", "safety", "conflict", "contradiction", "Visit 2", "sample"], "next_step": ["PI", "Investigator", "clarification", "sponsor"]},
        "ISSUE_03": {"ref": ["6.2", "diary"], "summary": ["diary", "review", "missing detail", "unclear", "no details", "lack of detail"], "next_step": ["PI", "Investigator", "clarification", "monitor"]},
        "ISSUE_04": {"ref": ["Scenario 1", "4.2.2"], "summary": ["Scenario 1", "pseudoephedrine", "OTC", "eligibility", "BP", "anti-hypertensive", "ambiguity"], "next_step": ["PI", "Investigator", "assessment", "decision"]},
        "ISSUE_05": {"ref": ["Scenario 2", "6.2"], "summary": ["Scenario 2", "diary", "missing", "forgot", "data", "entries"], "next_step": ["PI", "Investigator", "instruct", "document", "notify"]},
        "ISSUE_06": {"ref": ["Scenario 3", "6.2"], "summary": ["Scenario 3", "ECG", "QT", "borderline", "safety", "finding", "notify"], "next_step": ["PI", "Investigator", "notify", "assessment", "immediately"]},
    }

    # --- Evaluate each key issue ---
    for key_issue in key_issues:
        key_id = key_issue.get("issue_id")
        key_desc = key_issue.get("problem_summary", "No description in key")
        
        detail = {
            "key_issue_id": key_id,
            "key_issue_description": f"{key_issue.get('source_description', '')}: {key_desc[:70]}...", # Short description
            "identified_by_candidate": False,
            "matching_candidate_issue_id": None,
            "evaluation_notes": []
        }

        criteria = key_issue_match_criteria.get(key_id)
        if not criteria:
            detail["evaluation_notes"].append(f"Warning: No matching criteria defined for key issue {key_id}.")
            results["evaluation_details"].append(detail)
            continue # Cannot evaluate this key issue

        found_match = False
        for idx, sub_issue in enumerate(submitted_issues):
            if idx in matched_submission_indices:
                continue # Skip already matched submission issue

            # --- Check individual fields of the submitted issue ---
            # Ensure sub_issue is a dictionary and has expected keys
            if not isinstance(sub_issue, dict):
                detail["evaluation_notes"].append(f"Candidate entry at index {idx} is not a valid object.")
                continue

            sub_id = sub_issue.get("issue_id", f"MISSING_ID_{idx}")
            sub_ref = sub_issue.get("protocol_reference", "")
            sub_summary = sub_issue.get("problem_summary", "")
            sub_next_step = sub_issue.get("recommended_next_step", "")
            sub_comm_person = sub_issue.get("communication_point_person", "")

            # Apply matching logic based on keywords
            match_ref = check_keywords(sub_ref, criteria["ref"], required_count=1)
            match_summary = check_keywords(sub_summary, criteria["summary"], required_count=2) # Require at least 2 keywords for summary
            match_step = check_keywords(sub_next_step, criteria["next_step"], required_count=1)
            match_person = check_keywords(sub_comm_person, ["Principal Investigator", "PI"], required_count=1)

            # Define conditions for a successful match (adjust strictness here)
            # Example: Must match reference context, summary concept, next step involves PI, and comms person is PI.
            is_a_match = match_ref and match_summary and match_step and match_person

            if is_a_match:
                detail["identified_by_candidate"] = True
                detail["matching_candidate_issue_id"] = sub_id
                detail["evaluation_notes"].append(f"Matched with candidate issue '{sub_id}'. Criteria met.")
                achieved_score += 1
                matched_submission_indices.add(idx)
                found_match = True
                break # Stop searching for a match for this key_issue

        if not found_match:
             detail["evaluation_notes"].append("No matching issue found in candidate submission.")
             
        results["evaluation_details"].append(detail)

    # --- Calculate Overall Score ---
    if max_score > 0:
        results["overall_score"] = round((achieved_score / max_score) * 100, 2)
    else:
        results["overall_score"] = 0.0
        results["feedback"].append("Max score is zero, cannot calculate percentage.")
        
    results["feedback"].append(f"Candidate correctly identified {achieved_score} out of {max_score} key issues.")

    # --- Add check for minimum passing criteria (as per evaluation info) ---
    min_correct_issues = 4
    if achieved_score >= min_correct_issues:
         results["feedback"].append(f"Result: PASS (Met minimum requirement of {min_correct_issues} correctly identified issues).")
    else:
         results["feedback"].append(f"Result: FAIL (Did not meet minimum requirement of {min_correct_issues} correctly identified issues).")
         
    # --- Check for extra issues submitted ---
    unmatched_submission_count = len(submitted_issues) - len(matched_submission_indices)
    if unmatched_submission_count > 0:
        results["feedback"].append(f"Candidate submitted {unmatched_submission_count} issue(s) that did not match any key issues.")


    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluate CRC Basic Practical Exam Submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    print(f"Loading submission file: {args.submission_file}")
    submission_data = load_json(args.submission_file)
    if submission_data is None:
        return # Error message already printed by load_json

    print(f"Loading answer key file: {args.key_file}")
    key_data = load_json(args.key_file)
    if key_data is None:
        return # Error message already printed by load_json

    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_data, key_data)

    output_filename = "test_results.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
        print(f"Evaluation complete. Results saved to {output_filename}")
    except Exception as e:
        print(f"Error writing results to {output_filename}. Details: {e}")

if __name__ == "__main__":
    main()