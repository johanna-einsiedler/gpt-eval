import json
import re
from typing import Dict, Any

def normalize_text(text: str) -> str:
    """Normalize text for comparison by removing special chars and lowercasing."""
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def validate_task1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Task 1: Drafting a Product Specification."""
    results = {
        "score": 0,
        "max_score": 1,
        "details": {},
        "missing_fields": [],
        "invalid_subfields": []
    }
    
    # Check required top-level fields
    task1_sub = submission.get("task_1", {})
    missing_fields = [field for field in answer_key["task_1"]["required_fields"] 
                     if field not in task1_sub]
    
    if missing_fields:
        results["missing_fields"] = missing_fields
        return results
    
    results["score"] += 0.4
    
    # Validate key attributes subfields
    key_attrs = task1_sub.get("key_attributes", {})
    subfield_score = 0
    subfield_max = len(answer_key["task_1"]["key_attributes"]["required_subfields"]) * 0.12
    
    for subfield in answer_key["task_1"]["key_attributes"]["required_subfields"]:
        if subfield not in key_attrs:
            results["invalid_subfields"].append(f"Missing subfield: {subfield}")
            continue
        
        # Check for required content in subfields
        value = str(key_attrs[subfield]).lower()
        validation_rule = answer_key["task_1"]["key_attributes"]["validation_rules"][subfield]
        
        if subfield == "standards":
            if "en388" not in normalize_text(value) or "en374" not in normalize_text(value):
                results["invalid_subfields"].append(f"Invalid {subfield}: {value}")
                continue
        elif subfield == "temperature_range":
            if "50" not in value and "fifty" not in value:
                results["invalid_subfields"].append(f"Invalid {subfield}: {value}")
                continue
        
        subfield_score += 0.12
    
    results["score"] += min(subfield_score, 0.6)
    results["details"] = {
        "fields_present": True,
        "subfield_score": subfield_score,
        "subfield_max": subfield_max
    }
    
    return results

def validate_task2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Task 2: Reviewing a Specification for Errors."""
    results = {
        "score": 0,
        "max_score": 1,
        "details": {},
        "missing_errors": [],
        "invalid_corrections": []
    }
    
    task2_sub = submission.get("task_2", {})
    errors_found = task2_sub.get("errors_found", [])
    corrected_spec = task2_sub.get("corrected_spec", {})
    
    # Check minimum errors found
    if len(errors_found) < answer_key["task_2"]["minimum_errors"]:
        results["missing_errors"] = ["Not enough errors identified"]
        return results
    
    results["score"] += 0.3
    
    # Check required error types were detected
    error_score = 0
    required_errors = answer_key["task_2"]["required_corrections"]
    detected_errors = []
    
    for req_error in required_errors:
        req_normalized = normalize_text(req_error)
        for error in errors_found:
            if req_normalized in normalize_text(error):
                detected_errors.append(req_error)
                error_score += 0.1
                break
    
    if len(detected_errors) < len(required_errors):
        results["missing_errors"] = [err for err in required_errors if err not in detected_errors]
    
    # Validate corrections
    correction_score = 0
    for req_error in required_errors:
        if "license" in req_error.lower():
            if "license_type" in corrected_spec:
                if "50" in str(corrected_spec["license_type"]):
                    correction_score += 0.1
        elif "compliance" in req_error.lower():
            if "compliance" in corrected_spec:
                if any(term in normalize_text(str(corrected_spec["compliance"])) 
                   for term in ["gdpr", "soc2", "iso27001", "iso 27001"]):
                    correction_score += 0.1
        elif "support" in req_error.lower():
            if "support" in corrected_spec:
                if any(term in normalize_text(str(corrected_spec["support"])) 
                       for term in ["24/7", "sl", "response"]):
                    correction_score += 0.1
    
    results["score"] += min(error_score + correction_score, 0.7)
    results["details"] = {
        "errors_detected": detected_errors,
        "error_score": error_score,
        "correction_score": correction_score
    }
    
    return results

def main():
    # Load submission and answer key
    try:
        with open("test_submission.json", "r") as f:
            submission = json.load(f)
        
        with open("answer_key.json", "r") as f:
            answer_key = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return
    
    # Validate tasks
    task1_results = validate_task1(submission, answer_key)
    task2_results = validate_task2(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"]
    overall_score = (total_score / max_score) * 100
    
    # Prepare results
    test_results = {
        "overall_score": round(overall_score, 2),
        "task1": {
            "score": task1_results["score"],
            "max_score": task1_results["max_score"],
            "passed": task1_results["score"] >= task1_results["max_score"] * 0.8,
            "details": task1_results["details"],
            "issues": {
                "missing_fields": task1_results["missing_fields"],
                "invalid_subfields": task1_results["invalid_subfields"]
            }
        },
        "task2": {
            "score": task2_results["score"],
            "max_score": task2_results["max_score"],
            "passed": task2_results["score"] >= task2_results["max_score"] * 0.8,
            "details": task2_results["details"],
            "issues": {
                "missing_errors": task2_results["missing_errors"],
                "invalid_corrections": task2_results["invalid_corrections"]
            }
        },
        "passed": overall_score >= 80
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("Evaluation completed. Results saved to test_results.json")

if __name__ == "__main__":
    main()