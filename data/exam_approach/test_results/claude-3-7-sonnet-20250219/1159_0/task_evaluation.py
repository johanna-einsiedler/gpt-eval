#!/usr/bin/env python3
import json
import sys
import os
from collections import Counter

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def calculate_structure_score(submission):
    """Check if the JSON has the correct overall structure."""
    score = 20  # Starting with full points
    deductions = []
    
    required_sections = ["policy_framework", "bid_evaluation", "vendor_procedure"]
    for section in required_sections:
        if section not in submission:
            score -= 7
            deductions.append(f"Missing main section: {section} (-7)")
    
    # Check subsections
    subsections = {
        "policy_framework": ["policy_sections", "approval_workflow", "compliance_checklist"],
        "bid_evaluation": ["scoring_criteria", "weighted_formula", "minimum_thresholds"],
        "vendor_procedure": ["qualification_steps", "performance_metrics", "corrective_actions"]
    }
    
    for main_section, sub_sections in subsections.items():
        if main_section in submission:
            for sub in sub_sections:
                if sub not in submission[main_section]:
                    score -= 3
                    deductions.append(f"Missing subsection: {main_section}.{sub} (-3)")
    
    # Ensure score is not negative
    score = max(0, score)
    
    return {
        "score": score,
        "max_score": 20,
        "percentage": (score / 20) * 100,
        "deductions": deductions
    }

def evaluate_policy_framework(submission, answer_key):
    """Evaluate the policy framework section."""
    score = 25  # Starting with full points
    deductions = []
    
    # Extract policy framework sections from submission
    policy_framework = submission.get("policy_framework", {})
    
    # Check policy sections
    expected_source = "company_requirements.txt"
    valid_policy_sections = set([
        "Procurement Authority Delegation",
        "Competitive Bidding Requirements",
        "Sole Source Justification",
        "Ethical Standards and Conflict of Interest",
        "Sustainable Procurement Guidelines",
        "Emergency Procurement Procedures",
        "Contract Management Guidelines",
        "Vendor Diversity and Inclusion",
        "Budget Approval Process",
        "Purchase Order Documentation"
    ])
    
    policy_sections = policy_framework.get("policy_sections", [])
    if len(policy_sections) != 5:
        deductions.append(f"Wrong number of policy sections: expected 5, got {len(policy_sections)} (-3)")
        score -= 3
    
    for section in policy_sections:
        if section not in valid_policy_sections:
            deductions.append(f"Invalid policy section: {section} (-5)")
            score -= 5
    
    # Check approval workflow
    approval_workflow = policy_framework.get("approval_workflow", [])
    expected_levels = [
        {"level": "Level 1", "threshold": "$0 - $5,000"},
        {"level": "Level 2", "threshold": "$5,001 - $25,000"},
        {"level": "Level 3", "threshold": "$25,001 - $100,000"},
        {"level": "Level 4", "threshold": "$100,001+"}
    ]
    
    if len(approval_workflow) != 4:
        deductions.append(f"Wrong number of approval workflow levels: expected 4, got {len(approval_workflow)} (-3)")
        score -= 3
    
    for i, level in enumerate(approval_workflow):
        if i < len(expected_levels):
            if level.get("level") != expected_levels[i]["level"] or level.get("threshold") != expected_levels[i]["threshold"]:
                deductions.append(f"Incorrect approval workflow level or threshold at position {i+1} (-2)")
                score -= 2
    
    # Check compliance checklist
    valid_compliance_items = set([
        "Documented Approval Authority Matrix",
        "Supplier Code of Conduct Acknowledgment",
        "Competitive Bidding for Purchases Over $25,000",
        "Conflict of Interest Disclosure Requirements",
        "Documentation Retention (7 Years Minimum)",
        "Supplier Diversity Reporting",
        "Contract Review Process",
        "Fair Labor Standards Compliance",
        "Environmental Impact Assessment",
        "Cybersecurity Requirements for Data-Sharing Vendors"
    ])
    
    compliance_checklist = policy_framework.get("compliance_checklist", [])
    if len(compliance_checklist) != 5:
        deductions.append(f"Wrong number of compliance items: expected 5, got {len(compliance_checklist)} (-3)")
        score -= 3
    
    for item in compliance_checklist:
        if item not in valid_compliance_items:
            deductions.append(f"Invalid compliance item: {item} (-5)")
            score -= 5
    
    # Ensure score is not negative
    score = max(0, score)
    
    return {
        "score": score,
        "max_score": 25,
        "percentage": (score / 25) * 100,
        "deductions": deductions
    }

def evaluate_bid_evaluation(submission, answer_key):
    """Evaluate the bid evaluation section."""
    score = 30  # Starting with full points
    deductions = []
    
    # Extract bid evaluation from submission
    bid_evaluation = submission.get("bid_evaluation", {})
    
    # Check scoring criteria
    valid_criteria = set([
        "Price Competitiveness",
        "Technical Capability",
        "Delivery Performance",
        "Quality Management System",
        "Financial Stability",
        "Customer Service Responsiveness",
        "Warranty Terms",
        "Geographic Location",
        "Innovation Capability",
        "Environmental Compliance"
    ])
    
    valid_thresholds = {
        "Price Competitiveness": 70,
        "Technical Capability": 75,
        "Delivery Performance": 80,
        "Quality Management System": 75,
        "Financial Stability": 80,
        "Customer Service Responsiveness": 70,
        "Warranty Terms": 65,
        "Geographic Location": 60,
        "Innovation Capability": 70,
        "Environmental Compliance": 75
    }
    
    scoring_criteria = bid_evaluation.get("scoring_criteria", [])
    if len(scoring_criteria) != 5:
        deductions.append(f"Wrong number of scoring criteria: expected 5, got {len(scoring_criteria)} (-3)")
        score -= 3
    
    # Check if criteria are valid and sum to 100%
    total_weight = 0
    for criterion in scoring_criteria:
        if "criterion" not in criterion or "weight" not in criterion:
            deductions.append(f"Missing 'criterion' or 'weight' in scoring criterion (-2)")
            score -= 2
            continue
            
        criterion_name = criterion["criterion"]
        if criterion_name not in valid_criteria:
            deductions.append(f"Invalid scoring criterion: {criterion_name} (-5)")
            score -= 5
        
        total_weight += criterion.get("weight", 0)
    
    if total_weight != 100:
        deductions.append(f"Scoring criteria weights do not sum to 100%: got {total_weight}% (-10)")
        score -= 10
    
    # Check weighted formula
    if "weighted_formula" not in bid_evaluation or not bid_evaluation["weighted_formula"]:
        deductions.append("Missing or empty weighted formula (-5)")
        score -= 5
    
    # Check minimum thresholds
    min_thresholds = bid_evaluation.get("minimum_thresholds", {})
    if len(min_thresholds) != len(scoring_criteria):
        deductions.append(f"Number of minimum thresholds does not match number of criteria (-3)")
        score -= 3
    
    for criterion_name, threshold in min_thresholds.items():
        if criterion_name not in valid_criteria:
            deductions.append(f"Invalid criterion in minimum thresholds: {criterion_name} (-2)")
            score -= 2
        elif valid_thresholds.get(criterion_name) != threshold:
            deductions.append(f"Incorrect threshold for {criterion_name}: expected {valid_thresholds.get(criterion_name)}, got {threshold} (-2)")
            score -= 2
    
    # Ensure score is not negative
    score = max(0, score)
    
    return {
        "score": score,
        "max_score": 30,
        "percentage": (score / 30) * 100,
        "deductions": deductions
    }

def evaluate_vendor_procedure(submission, answer_key):
    """Evaluate the vendor procedure section."""
    score = 25  # Starting with full points
    deductions = []
    
    # Extract vendor procedure from submission
    vendor_procedure = submission.get("vendor_procedure", {})
    
    # Check qualification steps
    valid_qualification_steps = set([
        "Initial Capability Assessment",
        "Financial Stability Verification",
        "Reference Checks",
        "Quality Management System Review",
        "Compliance Certification Verification",
        "Site Visit/Facility Inspection",
        "Information Security Assessment",
        "Sustainability/Environmental Audit",
        "Sample/Prototype Evaluation",
        "Insurance Coverage Verification"
    ])
    
    qualification_steps = vendor_procedure.get("qualification_steps", [])
    if len(qualification_steps) != 5:
        deductions.append(f"Wrong number of qualification steps: expected 5, got {len(qualification_steps)} (-3)")
        score -= 3
    
    for step in qualification_steps:
        if step not in valid_qualification_steps:
            deductions.append(f"Invalid qualification step: {step} (-5)")
            score -= 5
    
    # Check performance metrics
    valid_metrics = set([
        "On-Time Delivery Rate",
        "Quality Acceptance Rate",
        "Cost Variance",
        "Response Time",
        "Invoice Accuracy",
        "Contract Compliance",
        "Resolution Time",
        "Returns Rate",
        "Continuous Improvement",
        "Order Fulfillment Accuracy",
        "Sustainability Index",
        "Technology Integration"
    ])
    
    valid_benchmarks = {
        "On-Time Delivery Rate": "95%",
        "Quality Acceptance Rate": "98%",
        "Cost Variance": "<2%",
        "Response Time": "<24 hours",
        "Invoice Accuracy": "99%",
        "Contract Compliance": "100%",
        "Resolution Time": "<5 days",
        "Returns Rate": "<1%",
        "Continuous Improvement": ">3",
        "Order Fulfillment Accuracy": "97%",
        "Sustainability Index": ">85",
        "Technology Integration": ">7"
    }
    
    performance_metrics = vendor_procedure.get("performance_metrics", [])
    if len(performance_metrics) != 6:
        deductions.append(f"Wrong number of performance metrics: expected 6, got {len(performance_metrics)} (-3)")
        score -= 3
    
    for metric in performance_metrics:
        if "metric" not in metric or "benchmark" not in metric:
            deductions.append(f"Missing 'metric' or 'benchmark' in performance metric (-2)")
            score -= 2
            continue
            
        metric_name = metric["metric"]
        if metric_name not in valid_metrics:
            deductions.append(f"Invalid performance metric: {metric_name} (-5)")
            score -= 5
        
        if valid_benchmarks.get(metric_name) != metric.get("benchmark"):
            deductions.append(f"Incorrect benchmark for {metric_name}: expected {valid_benchmarks.get(metric_name)}, got {metric.get('benchmark')} (-2)")
            score -= 2
    
    # Check corrective actions
    valid_corrective_actions = set([
        "Performance Improvement Plan (PIP) Implementation",
        "Increased Inspection Frequency",
        "Payment Term Adjustment",
        "Probationary Status Assignment",
        "Mandatory Training/Certification",
        "Regular Progress Review Meetings",
        "Shipment Lot Testing",
        "Financial Penalties as Per Contract Terms",
        "Secondary Source Development",
        "Contract Termination Process"
    ])
    
    corrective_actions = vendor_procedure.get("corrective_actions", [])
    if len(corrective_actions) != 3:
        deductions.append(f"Wrong number of corrective actions: expected 3, got {len(corrective_actions)} (-3)")
        score -= 3
    
    for action in corrective_actions:
        if action not in valid_corrective_actions:
            deductions.append(f"Invalid corrective action: {action} (-5)")
            score -= 5
    
    # Ensure score is not negative
    score = max(0, score)
    
    return {
        "score": score,
        "max_score": 25,
        "percentage": (score / 25) * 100,
        "deductions": deductions
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the full submission and calculate overall score."""
    # Evaluate each section
    structure_results = calculate_structure_score(submission)
    policy_framework_results = evaluate_policy_framework(submission, answer_key)
    bid_evaluation_results = evaluate_bid_evaluation(submission, answer_key)
    vendor_procedure_results = evaluate_vendor_procedure(submission, answer_key)
    
    # Calculate overall score
    total_score = (
        structure_results["score"] +
        policy_framework_results["score"] +
        bid_evaluation_results["score"] +
        vendor_procedure_results["score"]
    )
    
    max_total = (
        structure_results["max_score"] +
        policy_framework_results["max_score"] +
        bid_evaluation_results["max_score"] +
        vendor_procedure_results["max_score"]
    )
    
    overall_percentage = (total_score / max_total) * 100
    
    # Check if student passes based on criteria:
    # - Overall score of at least 75%
    # - No individual section below 60%
    passed = overall_percentage >= 75
    section_percentages = [
        structure_results["percentage"],
        policy_framework_results["percentage"],
        bid_evaluation_results["percentage"],
        vendor_procedure_results["percentage"]
    ]
    
    if any(percentage < 60 for percentage in section_percentages):
        passed = False
        failing_sections = []
        if structure_results["percentage"] < 60:
            failing_sections.append("Structure")
        if policy_framework_results["percentage"] < 60:
            failing_sections.append("Policy Framework")
        if bid_evaluation_results["percentage"] < 60:
            failing_sections.append("Bid Evaluation")
        if vendor_procedure_results["percentage"] < 60:
            failing_sections.append("Vendor Procedure")
    else:
        failing_sections = []
    
    # Compile results
    results = {
        "overall_score": round(overall_percentage, 2),
        "total_points": total_score,
        "max_points": max_total,
        "passed": passed,
        "failing_sections": failing_sections,
        "section_scores": {
            "structure": {
                "points": structure_results["score"],
                "max_points": structure_results["max_score"],
                "percentage": round(structure_results["percentage"], 2),
                "deductions": structure_results["deductions"]
            },
            "policy_framework": {
                "points": policy_framework_results["score"],
                "max_points": policy_framework_results["max_score"],
                "percentage": round(policy_framework_results["percentage"], 2),
                "deductions": policy_framework_results["deductions"]
            },
            "bid_evaluation": {
                "points": bid_evaluation_results["score"],
                "max_points": bid_evaluation_results["max_score"],
                "percentage": round(bid_evaluation_results["percentage"], 2),
                "deductions": bid_evaluation_results["deductions"]
            },
            "vendor_procedure": {
                "points": vendor_procedure_results["score"],
                "max_points": vendor_procedure_results["max_score"],
                "percentage": round(vendor_procedure_results["percentage"], 2),
                "deductions": vendor_procedure_results["deductions"]
            }
        }
    }
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py submission_file.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Write results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASS' if results['passed'] else 'FAIL'}")
    
    if results['failing_sections']:
        print(f"Failed sections: {', '.join(results['failing_sections'])}")

if __name__ == "__main__":
    main()