#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_negotiation_strategy(submission, answer_key):
    """Evaluate the negotiation strategy section."""
    score = 0
    max_score = 20
    feedback = []
    
    # Check if the selected approach matches
    if submission.get("negotiation_strategy", {}).get("selected_approach") == answer_key["negotiation_strategy"]["selected_approach"]:
        score += 10
        feedback.append("Correct negotiation approach selected.")
    else:
        feedback.append("Incorrect negotiation approach. The transparent, educational approach (B) is most appropriate for this client.")
    
    # Check justification (subjective, but we'll look for key concepts)
    justification = submission.get("negotiation_strategy", {}).get("justification", "").lower()
    key_concepts = ["transparent", "trust", "education", "concern", "advantage", "price", "value"]
    concept_count = sum(1 for concept in key_concepts if concept in justification)
    
    justification_score = min(10, concept_count * 2)  # Max 10 points
    score += justification_score
    
    if justification_score >= 6:
        feedback.append("Good justification that demonstrates understanding of client-centered negotiation.")
    else:
        feedback.append("Justification lacks sufficient explanation of why this approach is appropriate for the client's needs and concerns.")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "feedback": feedback
    }

def evaluate_package_details(submission, answer_key):
    """Evaluate the package details section."""
    score = 0
    max_score = 40
    feedback = []
    
    # Get submission values
    sub_package = submission.get("package_details", {})
    sub_services = set(sub_package.get("selected_services", []))
    sub_merchandise = set(sub_package.get("selected_merchandise", []))
    sub_additional = set(sub_package.get("selected_additional_services", []))
    sub_price = float(sub_package.get("total_package_price", 0))
    sub_margin = float(sub_package.get("profit_margin_percentage", 0))
    
    # Essential services for traditional funeral with viewing
    essential_services = {"S1", "S3"}  # Basic services and embalming are absolutely essential
    
    # Check if essential services are included
    if essential_services.issubset(sub_services):
        score += 10
        feedback.append("Package includes essential basic services and embalming.")
    else:
        feedback.append("Package is missing essential services required for a traditional funeral with viewing.")
    
    # Check for specifically requested elements (military honors, music, religious service)
    requested_elements = []
    if "S7" in sub_services:
        requested_elements.append("religious service")
    if "A7" in sub_additional:
        requested_elements.append("military honors")
    if "A9" in sub_additional:
        requested_elements.append("music")
    
    elements_score = min(10, len(requested_elements) * 3.33)
    score += elements_score
    
    if len(requested_elements) == 3:
        feedback.append("Package includes all specifically requested elements: religious service, military honors, and music.")
    else:
        feedback.append(f"Package includes {len(requested_elements)}/3 specifically requested elements: {', '.join(requested_elements) if requested_elements else 'none'}.")
    
    # Check budget compliance (4000-6000)
    if 4000 <= sub_price <= 6000:
        score += 10
        feedback.append(f"Package price (${sub_price:.2f}) is within client's budget range ($4,000-$6,000).")
    elif sub_price < 4000:
        score += 5
        feedback.append(f"Package price (${sub_price:.2f}) is below client's budget range, potentially missing important elements.")
    elif 6000 < sub_price <= 6900:  # Allow up to 15% over budget
        score += 5
        feedback.append(f"Package price (${sub_price:.2f}) exceeds client's budget range but is within 15% of maximum.")
    else:
        feedback.append(f"Package price (${sub_price:.2f}) significantly exceeds client's budget range.")
    
    # Check profit margin (minimum 22%)
    if sub_margin >= 22:
        score += 10
        feedback.append(f"Profit margin ({sub_margin:.1f}%) meets or exceeds the minimum requirement of 22%.")
    else:
        feedback.append(f"Profit margin ({sub_margin:.1f}%) is below the minimum requirement of 22%.")
    
    # Critical failure checks
    critical_failures = []
    if sub_price > 6900:  # More than 15% over budget
        critical_failures.append("Package exceeds client's budget by more than 15% without justification")
    
    if sub_margin < 15:
        critical_failures.append("Package has a profit margin below 15% (unsustainable business practice)")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "feedback": feedback,
        "critical_failures": critical_failures
    }

def evaluate_objection_responses(submission, answer_key):
    """Evaluate the objection responses section."""
    score = 0
    max_score = 25
    feedback = []
    
    # Get submission values
    sub_objections = submission.get("objection_responses", {})
    key_objections = answer_key["objection_responses"]
    
    # Check each objection (objection1 is most important)
    if sub_objections.get("objection1") == key_objections["objection1"]:
        score += 10
        feedback.append("Correct response to price concerns objection.")
    else:
        feedback.append("Incorrect response to price concerns objection. The best approach is to acknowledge concerns, explain value, and offer to adjust the package.")
    
    if sub_objections.get("objection2") == key_objections["objection2"]:
        score += 7.5
        feedback.append("Correct response to prepayment concerns objection.")
    else:
        feedback.append("Incorrect response to prepayment concerns objection. The best approach is to explain the safeguards and flexibility options available.")
    
    if sub_objections.get("objection3") == key_objections["objection3"]:
        score += 7.5
        feedback.append("Correct response to family involvement objection.")
    else:
        feedback.append("Incorrect response to family involvement objection. The best approach is to encourage family participation in the planning process.")
    
    # Check for dismissive or unethical responses
    dismissive_responses = {
        "objection1": "C",  # Suggesting premium options when client has budget concerns
        "objection2": "A",  # Dismissing valid concerns as "unlikely"
        "objection3": "B"   # Dismissing family involvement
    }
    
    critical_failures = []
    for objection, response in sub_objections.items():
        if response == dismissive_responses.get(objection):
            critical_failures.append(f"Selected a dismissive response to {objection}")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "feedback": feedback,
        "critical_failures": critical_failures
    }

def evaluate_contract_completion(submission, answer_key):
    """Evaluate the contract completion section."""
    score = 0
    max_score = 15
    feedback = []
    
    # Get submission values
    sub_contract = submission.get("contract_completion", {})
    key_contract = answer_key["contract_completion"]
    
    # Check client name
    if sub_contract.get("client_name") == key_contract["client_name"]:
        score += 3
        feedback.append("Correct client name identified.")
    else:
        feedback.append("Incorrect client name. The client is Margaret Wilson.")
    
    # Check payment plan
    # Any installment plan (P4, P5, P6) is acceptable given client's preference for monthly payments
    acceptable_plans = ["P4", "P5", "P6"]
    if sub_contract.get("payment_plan_selected") in acceptable_plans:
        score += 4
        feedback.append("Selected an appropriate installment payment plan.")
    else:
        feedback.append("Selected payment plan does not align with client's preference for monthly installments.")
    
    # Check required disclosures
    sub_disclosures = sub_contract.get("required_disclosures", [])
    
    # Key disclosure concepts to look for
    key_concepts = [
        "trust", "insurance", "regulated", "transfer", "relocate", 
        "modify", "change", "cancel", "refund", "fee"
    ]
    
    # Count how many key concepts are covered in the disclosures
    concept_coverage = set()
    for disclosure in sub_disclosures:
        disclosure_lower = disclosure.lower()
        for concept in key_concepts:
            if concept in disclosure_lower:
                concept_coverage.add(concept)
    
    disclosure_score = min(8, len(concept_coverage) * 2)  # Max 8 points
    score += disclosure_score
    
    if len(sub_disclosures) >= 3 and disclosure_score >= 6:
        feedback.append("Included comprehensive required disclosures that address key consumer protections.")
    elif len(sub_disclosures) >= 3:
        feedback.append("Included required number of disclosures, but some key consumer protections are missing.")
    else:
        feedback.append("Insufficient number of required disclosures. At least 3 are needed.")
    
    # Check for critical omissions in disclosures
    critical_failures = []
    essential_concepts = ["trust", "transfer", "cancel"]
    missing_essential = [concept for concept in essential_concepts if concept not in concept_coverage]
    
    if missing_essential:
        critical_failures.append(f"Omitted critical consumer protections: {', '.join(missing_essential)}")
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": (score / max_score) * 100,
        "feedback": feedback,
        "critical_failures": critical_failures
    }

def calculate_overall_results(section_results):
    """Calculate the overall test results."""
    total_score = sum(section["score"] for section in section_results.values())
    total_max = sum(section["max_score"] for section in section_results.values())
    overall_percentage = (total_score / total_max) * 100
    
    # Check section minimums (each section must be at least 50% of its allocated points)
    section_minimums_met = all(section["percentage"] >= 50 for section in section_results.values())
    
    # Collect all critical failures
    all_critical_failures = []
    for section_name, section in section_results.items():
        if "critical_failures" in section and section["critical_failures"]:
            for failure in section["critical_failures"]:
                all_critical_failures.append(f"{section_name}: {failure}")
    
    # Determine if candidate passed
    passed = overall_percentage >= 75 and section_minimums_met and not all_critical_failures
    
    return {
        "overall_score": overall_percentage,
        "total_points": total_score,
        "max_points": total_max,
        "section_minimums_met": section_minimums_met,
        "critical_failures": all_critical_failures,
        "passed": passed
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    results = {
        "negotiation_strategy": evaluate_negotiation_strategy(submission, answer_key),
        "package_details": evaluate_package_details(submission, answer_key),
        "objection_responses": evaluate_objection_responses(submission, answer_key),
        "contract_completion": evaluate_contract_completion(submission, answer_key)
    }
    
    # Calculate overall results
    overall_results = calculate_overall_results(results)
    
    # Combine all results
    final_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_results["overall_score"],
        "passed": overall_results["passed"],
        "section_scores": {
            "negotiation_strategy": results["negotiation_strategy"]["percentage"],
            "package_details": results["package_details"]["percentage"],
            "objection_responses": results["objection_responses"]["percentage"],
            "contract_completion": results["contract_completion"]["percentage"]
        },
        "total_points": f"{overall_results['total_points']}/{overall_results['max_points']}",
        "section_details": results,
        "critical_failures": overall_results["critical_failures"],
        "section_minimums_met": overall_results["section_minimums_met"]
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if overall_results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()