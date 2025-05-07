import json
import sys
import os
from collections import defaultdict

# --- Comparison Helper Functions ---

def normalize_string(text):
    """Normalize string for comparison: lower case and strip whitespace."""
    if isinstance(text, str):
        return text.strip().lower()
    return text # Return as is if not a string (e.g., None)

def compare_strings(candidate_val, key_val, case_sensitive=False):
    """Compares two strings, optionally case-sensitive, after stripping whitespace."""
    if not isinstance(candidate_val, str) or not isinstance(key_val, str):
        return False # Cannot compare if not strings
    
    c_val = candidate_val.strip()
    k_val = key_val.strip()

    if not case_sensitive:
        c_val = c_val.lower()
        k_val = k_val.lower()
        
    return c_val == k_val

def compare_lists_exact_order(candidate_list, key_list, case_sensitive=False):
    """Compares two lists for exact element match in the same order."""
    if not isinstance(candidate_list, list) or not isinstance(key_list, list):
        return 0, len(key_list) # Treat as 0 matches if types are wrong
        
    max_score = len(key_list)
    score = 0
    
    # Compare element by element up to the length of the shorter list
    for i in range(min(len(candidate_list), len(key_list))):
        if compare_strings(candidate_list[i], key_list[i], case_sensitive):
            score += 1
            
    # Alternative: Check if lists are identical after normalization (if order matters)
    # normalized_candidate = [normalize_string(item) for item in candidate_list]
    # normalized_key = [normalize_string(item) for item in key_list]
    # if normalized_candidate == normalized_key:
    #     score = max_score
    # else:
    #     # Partial credit (count matching elements at same position) - implemented above
    #     pass 

    return score, max_score

def compare_lists_any_order(candidate_list, key_list, case_sensitive=False):
    """Compares lists, awarding points for each key item found in the candidate list (order insensitive)."""
    if not isinstance(candidate_list, list) or not isinstance(key_list, list):
        return 0, len(key_list) if isinstance(key_list, list) else 0

    max_score = len(key_list)
    score = 0
    
    # Normalize candidate items for efficient lookup
    normalized_candidate_items = set()
    for item in candidate_list:
         if isinstance(item, str):
             normalized_candidate_items.add(normalize_string(item) if not case_sensitive else item.strip())

    # Check each key item against the normalized candidate set
    for key_item in key_list:
        if isinstance(key_item, str):
            normalized_key_item = normalize_string(key_item) if not case_sensitive else key_item.strip()
            if normalized_key_item in normalized_candidate_items:
                score += 1
                # Optional: remove from set if each candidate item can only match one key item
                # normalized_candidate_items.remove(normalized_key_item) 
                
    return score, max_score

# --- Evaluation Logic ---

def evaluate_submission(candidate_data, key_data):
    """Evaluates the candidate submission against the answer key."""
    results = {
        "candidate_id": candidate_data.get("candidate_id", "MISSING"),
        "scores": {},
        "overall_score": 0.0,
        "max_score": 0,
        "achieved_score": 0
    }
    max_total_score = 0
    achieved_total_score = 0

    # --- 1. Internal Audit Report Review ---
    results["scores"]["internal_audit_report_review"] = {}
    cand_ia = candidate_data.get("internal_audit_report_review", {})
    key_ia = key_data.get("internal_audit_report_review", {})
    
    # 1.1 report_identifier (Exact match, case insensitive)
    field = "report_identifier"
    max_total_score += 1
    results["scores"]["internal_audit_report_review"][field] = {"score": 0, "max_score": 1, "match": False}
    if compare_strings(cand_ia.get(field), key_ia.get(field), case_sensitive=False):
        results["scores"]["internal_audit_report_review"][field]["score"] = 1
        results["scores"]["internal_audit_report_review"][field]["match"] = True
        achieved_total_score += 1

    # 1.2 scope_analysis
    results["scores"]["internal_audit_report_review"]["scope_analysis"] = {}
    cand_ia_scope = cand_ia.get("scope_analysis", {})
    key_ia_scope = key_ia.get("scope_analysis", {})

    # 1.2.1 stated_scope (Approximate match - check non-empty for basic auto-score, compare normalized for better)
    field = "stated_scope"
    max_total_score += 1
    results["scores"]["internal_audit_report_review"]["scope_analysis"][field] = {"score": 0, "max_score": 1, "match": False}
    # Simple check: is it non-empty? More advanced: compare_strings normalized
    if compare_strings(cand_ia_scope.get(field), key_ia_scope.get(field), case_sensitive=False):
        results["scores"]["internal_audit_report_review"]["scope_analysis"][field]["score"] = 1
        results["scores"]["internal_audit_report_review"]["scope_analysis"][field]["match"] = True
        achieved_total_score += 1
        
    # 1.2.2 procedures_summary (List comparison, any order, case insensitive)
    field = "procedures_summary"
    cand_list = cand_ia_scope.get(field, [])
    key_list = key_ia_scope.get(field, [])
    score, max_score = compare_lists_any_order(cand_list, key_list, case_sensitive=False)
    results["scores"]["internal_audit_report_review"]["scope_analysis"][field] = {"score": score, "max_score": max_score}
    achieved_total_score += score
    max_total_score += max_score

    # 1.2.3 explicit_scope_limitations (Exact match, case insensitive)
    field = "explicit_scope_limitations"
    max_total_score += 1
    results["scores"]["internal_audit_report_review"]["scope_analysis"][field] = {"score": 0, "max_score": 1, "match": False}
    if compare_strings(cand_ia_scope.get(field), key_ia_scope.get(field), case_sensitive=False):
        results["scores"]["internal_audit_report_review"]["scope_analysis"][field]["score"] = 1
        results["scores"]["internal_audit_report_review"]["scope_analysis"][field]["match"] = True
        achieved_total_score += 1

    # 1.3 weakness_identification (List of Objects)
    field = "weakness_identification"
    results["scores"]["internal_audit_report_review"][field] = {"findings": [], "summary_score": 0, "summary_max_score": 0}
    cand_findings = cand_ia.get(field, [])
    key_findings = key_ia.get(field, [])
    
    # Create lookup dictionaries based on finding_reference (case insensitive)
    cand_findings_dict = {normalize_string(f.get("finding_reference")): f for f in cand_findings if isinstance(f, dict) and f.get("finding_reference")}
    key_findings_dict = {normalize_string(f.get("finding_reference")): f for f in key_findings if isinstance(f, dict) and f.get("finding_reference")}

    section_max_score = 0
    section_achieved_score = 0

    for key_ref_norm, key_finding in key_findings_dict.items():
        finding_result = {"finding_reference": key_finding.get("finding_reference"), "score": 0, "max_score": 0, "fields": {}}
        
        cand_finding = cand_findings_dict.get(key_ref_norm)
        
        # Score finding_reference match (implicitly matched if cand_finding exists)
        finding_result["max_score"] += 1
        if cand_finding:
             # Check if the *original* case reference matches the key's original case (optional stricter check)
             # if compare_strings(cand_finding.get("finding_reference"), key_finding.get("finding_reference"), case_sensitive=True):
             #      finding_result["score"] +=1 # Award point only if case matches too
             # else: # Award point if normalized matches (already confirmed by lookup)
             finding_result["score"] += 1 # Award point for finding the reference match (case insensitive)
             
             # Score weakness_description (Normalized comparison)
             finding_result["max_score"] += 1
             finding_result["fields"]["weakness_description"] = {"score": 0, "max_score": 1, "match": False}
             if compare_strings(cand_finding.get("weakness_description"), key_finding.get("weakness_description"), case_sensitive=False):
                 finding_result["fields"]["weakness_description"]["score"] = 1
                 finding_result["fields"]["weakness_description"]["match"] = True
                 finding_result["score"] += 1

             # Score recommendation_summary (Normalized comparison)
             finding_result["max_score"] += 1
             finding_result["fields"]["recommendation_summary"] = {"score": 0, "max_score": 1, "match": False}
             if compare_strings(cand_finding.get("recommendation_summary"), key_finding.get("recommendation_summary"), case_sensitive=False):
                 finding_result["fields"]["recommendation_summary"]["score"] = 1
                 finding_result["fields"]["recommendation_summary"]["match"] = True
                 finding_result["score"] += 1
        else:
            # Candidate did not provide this finding at all
            finding_result["max_score"] += 2 # Add max score for the two fields missed
            finding_result["fields"]["weakness_description"] = {"score": 0, "max_score": 1, "match": False, "status": "Missing Finding"}
            finding_result["fields"]["recommendation_summary"] = {"score": 0, "max_score": 1, "match": False, "status": "Missing Finding"}


        results["scores"]["internal_audit_report_review"][field]["findings"].append(finding_result)
        section_achieved_score += finding_result["score"]
        section_max_score += finding_result["max_score"]

    results["scores"]["internal_audit_report_review"][field]["summary_score"] = section_achieved_score
    results["scores"]["internal_audit_report_review"][field]["summary_max_score"] = section_max_score
    achieved_total_score += section_achieved_score
    max_total_score += section_max_score

    # --- 2. External Audit Report Section Review ---
    results["scores"]["external_audit_report_section_review"] = {}
    cand_ea = candidate_data.get("external_audit_report_section_review", {})
    key_ea = key_data.get("external_audit_report_section_review", {})

    # 2.1 report_section_identifier (Exact match, case insensitive)
    field = "report_section_identifier"
    max_total_score += 1
    results["scores"]["external_audit_report_section_review"][field] = {"score": 0, "max_score": 1, "match": False}
    if compare_strings(cand_ea.get(field), key_ea.get(field), case_sensitive=False):
        results["scores"]["external_audit_report_section_review"][field]["score"] = 1
        results["scores"]["external_audit_report_section_review"][field]["match"] = True
        achieved_total_score += 1

    # 2.2 scope_analysis
    results["scores"]["external_audit_report_section_review"]["scope_analysis"] = {}
    cand_ea_scope = cand_ea.get("scope_analysis", {})
    key_ea_scope = key_ea.get("scope_analysis", {})

    # 2.2.1 stated_purpose_or_scope (Normalized comparison)
    field = "stated_purpose_or_scope"
    max_total_score += 1
    results["scores"]["external_audit_report_section_review"]["scope_analysis"][field] = {"score": 0, "max_score": 1, "match": False}
    if compare_strings(cand_ea_scope.get(field), key_ea_scope.get(field), case_sensitive=False):
        results["scores"]["external_audit_report_section_review"]["scope_analysis"][field]["score"] = 1
        results["scores"]["external_audit_report_section_review"]["scope_analysis"][field]["match"] = True
        achieved_total_score += 1

    # 2.2.2 scope_limitation_language (Exact match, case insensitive - should capture the core phrase)
    field = "scope_limitation_language"
    max_total_score += 1
    results["scores"]["external_audit_report_section_review"]["scope_analysis"][field] = {"score": 0, "max_score": 1, "match": False}
    # Allow some flexibility by checking if key phrase is contained within candidate answer
    key_phrase = normalize_string(key_ea_scope.get(field, ""))
    cand_phrase = normalize_string(cand_ea_scope.get(field, ""))
    # Simple containment check might be too lenient, exact (normalized) match is better per instructions
    # if key_phrase and key_phrase in cand_phrase: 
    if compare_strings(cand_ea_scope.get(field), key_ea_scope.get(field), case_sensitive=False):
        results["scores"]["external_audit_report_section_review"]["scope_analysis"][field]["score"] = 1
        results["scores"]["external_audit_report_section_review"]["scope_analysis"][field]["match"] = True
        achieved_total_score += 1

    # 2.2.3 areas_with_findings (List comparison, any order, case insensitive)
    field = "areas_with_findings"
    cand_list = cand_ea_scope.get(field, [])
    key_list = key_ea_scope.get(field, [])
    score, max_score = compare_lists_any_order(cand_list, key_list, case_sensitive=False)
    results["scores"]["external_audit_report_section_review"]["scope_analysis"][field] = {"score": score, "max_score": max_score}
    achieved_total_score += score
    max_total_score += max_score

    # 2.3 weakness_identification (List of Objects)
    field = "weakness_identification"
    results["scores"]["external_audit_report_section_review"][field] = {"findings": [], "summary_score": 0, "summary_max_score": 0}
    cand_findings = cand_ea.get(field, [])
    key_findings = key_ea.get(field, [])
    
    cand_findings_dict = {normalize_string(f.get("finding_reference")): f for f in cand_findings if isinstance(f, dict) and f.get("finding_reference")}
    key_findings_dict = {normalize_string(f.get("finding_reference")): f for f in key_findings if isinstance(f, dict) and f.get("finding_reference")}

    section_max_score = 0
    section_achieved_score = 0

    for key_ref_norm, key_finding in key_findings_dict.items():
        finding_result = {"finding_reference": key_finding.get("finding_reference"), "score": 0, "max_score": 0, "fields": {}}
        
        cand_finding = cand_findings_dict.get(key_ref_norm)
        
        # Score finding_reference match
        finding_result["max_score"] += 1
        if cand_finding:
             finding_result["score"] += 1 # Award point for finding the reference match (case insensitive)
             
             # Score weakness_description (Normalized comparison)
             finding_result["max_score"] += 1
             finding_result["fields"]["weakness_description"] = {"score": 0, "max_score": 1, "match": False}
             if compare_strings(cand_finding.get("weakness_description"), key_finding.get("weakness_description"), case_sensitive=False):
                 finding_result["fields"]["weakness_description"]["score"] = 1
                 finding_result["fields"]["weakness_description"]["match"] = True
                 finding_result["score"] += 1

             # Score classification_if_stated (Exact match, case insensitive - handles "Not Classified")
             finding_result["max_score"] += 1
             finding_result["fields"]["classification_if_stated"] = {"score": 0, "max_score": 1, "match": False}
             if compare_strings(cand_finding.get("classification_if_stated"), key_finding.get("classification_if_stated"), case_sensitive=False):
                 finding_result["fields"]["classification_if_stated"]["score"] = 1
                 finding_result["fields"]["classification_if_stated"]["match"] = True
                 finding_result["score"] += 1
        else:
             # Candidate did not provide this finding at all
            finding_result["max_score"] += 2 # Add max score for the two fields missed
            finding_result["fields"]["weakness_description"] = {"score": 0, "max_score": 1, "match": False, "status": "Missing Finding"}
            finding_result["fields"]["classification_if_stated"] = {"score": 0, "max_score": 1, "match": False, "status": "Missing Finding"}

        results["scores"]["external_audit_report_section_review"][field]["findings"].append(finding_result)
        section_achieved_score += finding_result["score"]
        section_max_score += finding_result["max_score"]

    results["scores"]["external_audit_report_section_review"][field]["summary_score"] = section_achieved_score
    results["scores"]["external_audit_report_section_review"][field]["summary_max_score"] = section_max_score
    achieved_total_score += section_achieved_score
    max_total_score += section_max_score

    # --- Final Calculations ---
    results["achieved_score"] = achieved_total_score
    results["max_score"] = max_total_score
    if max_total_score > 0:
        results["overall_score"] = round((achieved_total_score / max_total_score) * 100, 2)
    else:
        results["overall_score"] = 0.0

    return results

# --- File Handling ---

def load_json_file(filepath):
    """Loads JSON data from a file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {filepath}. Details: {e}")
        sys.exit(1)

def save_json_file(data, filepath):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) # Use indent for readability
        print(f"Evaluation results saved to {filepath}")
    except Exception as e:
        print(f"Error writing results to {filepath}. Details: {e}")
        sys.exit(1)

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Check command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <candidate_submission.json> <answer_key.json>")
        sys.exit(1)

    candidate_file = sys.argv[1]
    key_file = sys.argv[2]
    results_file = "test_results.json"

    # 2. Load JSON files
    print(f"Loading candidate submission from: {candidate_file}")
    candidate_data = load_json_file(candidate_file)
    
    print(f"Loading answer key from: {key_file}")
    key_data = load_json_file(key_file)

    # 3. Perform evaluation
    print("Evaluating submission...")
    evaluation_results = evaluate_submission(candidate_data, key_data)

    # 4. Save results
    save_json_file(evaluation_results, results_file)

    # 5. Print summary to console
    print("\n--- Evaluation Summary ---")
    print(f"Candidate ID: {evaluation_results.get('candidate_id', 'N/A')}")
    print(f"Achieved Score: {evaluation_results.get('achieved_score', 0)}")
    print(f"Maximum Score: {evaluation_results.get('max_score', 0)}")
    print(f"Overall Score: {evaluation_results.get('overall_score', 0.0)}%")
    print("--------------------------")