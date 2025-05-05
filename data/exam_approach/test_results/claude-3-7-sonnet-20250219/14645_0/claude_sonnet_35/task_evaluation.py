#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_test_schedule(submission, answer_key):
    """Evaluate the test schedule section."""
    score = 0
    feedback = []
    
    # Check if there are at least 4 distinct testing phases
    if len(submission.get("testSchedule", [])) >= 4:
        score += 5
        feedback.append("Provided at least 4 distinct testing phases.")
    else:
        feedback.append("Failed to provide at least 4 distinct testing phases.")
    
    # Check logical sequencing aligned with development schedule
    logical_sequencing = True
    for phase in submission.get("testSchedule", []):
        # Basic validation of dates and sequence
        try:
            start_date = datetime.strptime(phase.get("startDate", ""), "%Y-%m-%d")
            end_date = datetime.strptime(phase.get("endDate", ""), "%Y-%m-%d")
            if start_date > end_date:
                logical_sequencing = False
                feedback.append(f"Phase '{phase.get('phase')}' has start date after end date.")
        except ValueError:
            logical_sequencing = False
            feedback.append(f"Phase '{phase.get('phase')}' has invalid date format.")
    
    # Simplified check for alignment with development schedule
    if logical_sequencing:
        score += 10
        feedback.append("Test schedule shows logical sequencing aligned with development schedule.")
    else:
        feedback.append("Test schedule has sequencing issues.")
    
    # Check for appropriate resource allocation
    resource_allocation = True
    for phase in submission.get("testSchedule", []):
        if not phase.get("resources"):
            resource_allocation = False
            feedback.append(f"Phase '{phase.get('phase')}' is missing resource allocation.")
    
    if resource_allocation:
        score += 10
        feedback.append("Appropriate resource allocation based on expertise.")
    else:
        feedback.append("Issues with resource allocation in test schedule.")
    
    # Check for clear deliverables
    deliverables_check = True
    for phase in submission.get("testSchedule", []):
        if not phase.get("deliverables"):
            deliverables_check = False
            feedback.append(f"Phase '{phase.get('phase')}' is missing clear deliverables.")
    
    if deliverables_check:
        score += 5
        feedback.append("Clear and relevant deliverables for each phase.")
    else:
        feedback.append("Issues with deliverables specification.")
    
    return {
        "score": score,
        "max_score": 30,
        "feedback": feedback
    }

def evaluate_risk_assessment(submission, answer_key):
    """Evaluate the risk assessment section."""
    score = 0
    feedback = []
    
    submission_risks = submission.get("riskAssessment", [])
    key_risks = answer_key.get("riskAssessment", [])
    
    # Check if exactly 5 risks are selected
    if len(submission_risks) == 5:
        score += 5
        feedback.append("Selected exactly 5 risks as required.")
    else:
        feedback.append(f"Selected {len(submission_risks)} risks instead of the required 5.")
    
    # Check for selection of appropriate top risks
    key_risk_ids = [risk["riskId"] for risk in key_risks]
    submission_risk_ids = [risk["riskId"] for risk in submission_risks]
    
    matching_risks = set(submission_risk_ids).intersection(set(key_risk_ids))
    risk_selection_score = len(matching_risks) * 2  # 2 points per matching risk, max 10
    score += risk_selection_score
    
    if risk_selection_score > 0:
        feedback.append(f"Selected {len(matching_risks)} of the appropriate top risks.")
    else:
        feedback.append("Failed to select appropriate top risks.")
    
    # Check for reasonable probability and impact ratings
    reasonable_ratings = True
    for risk in submission_risks:
        if not (1 <= risk.get("probability", 0) <= 5 and 1 <= risk.get("impact", 0) <= 5):
            reasonable_ratings = False
            feedback.append(f"Risk ID {risk.get('riskId')} has invalid probability or impact rating.")
    
    if reasonable_ratings:
        score += 5
        feedback.append("Provided reasonable probability and impact ratings.")
    else:
        feedback.append("Issues with probability and impact ratings.")
    
    return {
        "score": score,
        "max_score": 20,
        "feedback": feedback
    }

def evaluate_test_coverage(submission, answer_key):
    """Evaluate the test coverage section."""
    score = 0
    feedback = []
    
    submission_coverage = submission.get("testCoverage", {})
    key_coverage = answer_key.get("testCoverage", {})
    
    # Check if total equals 100%
    total = sum([
        submission_coverage.get("functionalCoverage", 0),
        submission_coverage.get("performanceCoverage", 0),
        submission_coverage.get("securityCoverage", 0),
        submission_coverage.get("usabilityCoverage", 0)
    ])
    
    if total == 100:
        score += 5
        feedback.append("Test coverage percentages sum to 100% as required.")
    else:
        feedback.append(f"Test coverage percentages sum to {total}% instead of 100%.")
    
    # Check for balanced allocation reflecting project priorities
    # Simplified approach: check if functional > security > performance > usability
    functional = submission_coverage.get("functionalCoverage", 0)
    security = submission_coverage.get("securityCoverage", 0)
    performance = submission_coverage.get("performanceCoverage", 0)
    usability = submission_coverage.get("usabilityCoverage", 0)
    
    if functional > security and security >= performance and functional > usability:
        score += 10
        feedback.append("Balanced allocation reflecting project priorities.")
    else:
        # Partial credit for somewhat reasonable allocation
        if functional > 40:
            score += 5
            feedback.append("Functional testing given appropriate priority, but overall balance could be improved.")
        else:
            feedback.append("Test coverage allocation does not reflect project priorities.")
    
    return {
        "score": score,
        "max_score": 15,
        "feedback": feedback
    }

def evaluate_resource_allocation(submission, answer_key):
    """Evaluate the resource allocation section."""
    score = 0
    feedback = []
    
    submission_resources = submission.get("resourceAllocation", [])
    
    # Check if all 5 resources are allocated
    resource_ids = [resource.get("resourceId") for resource in submission_resources]
    expected_resources = ["QA1", "QA2", "QA3", "DEV1", "BA1"]
    
    if set(resource_ids) == set(expected_resources):
        score += 5
        feedback.append("Allocated all 5 resources as required.")
    else:
        missing = set(expected_resources) - set(resource_ids)
        feedback.append(f"Missing resource allocation for: {', '.join(missing)}")
    
    # Check if allocation respects resource availability constraints
    # This would require the original test_resources.xlsx data
    # For simplicity, we'll assume the answer key has correct allocations
    respects_constraints = True
    for resource in submission_resources:
        resource_id = resource.get("resourceId")
        for week_alloc in resource.get("allocation", []):
            week = week_alloc.get("week")
            percentage = week_alloc.get("percentage")
            
            # Find the corresponding resource in the answer key
            key_resource = next((r for r in answer_key.get("resourceAllocation", []) 
                               if r.get("resourceId") == resource_id), None)
            
            if key_resource:
                key_week_alloc = next((w for w in key_resource.get("allocation", []) 
                                     if w.get("week") == week), None)
                
                if key_week_alloc and percentage > key_week_alloc.get("percentage", 0):
                    respects_constraints = False
                    feedback.append(f"Resource {resource_id} is overallocated in week {week}.")
    
    if respects_constraints:
        score += 10
        feedback.append("Resource allocation respects availability constraints.")
    else:
        feedback.append("Resource allocation exceeds availability constraints.")
    
    # Check for appropriate assignment based on expertise
    # This is a subjective assessment, so we'll use a simplified approach
    appropriate_assignment = True
    for resource in submission_resources:
        resource_id = resource.get("resourceId")
        if resource_id == "QA1":  # Senior QA with security expertise
            # Check if they're assigned to security-related tasks
            weeks_5_to_8 = [w.get("percentage", 0) for w in resource.get("allocation", []) 
                           if 5 <= w.get("week", 0) <= 8]
            if not all(p >= 75 for p in weeks_5_to_8):
                appropriate_assignment = False
                feedback.append("Senior QA (QA1) not adequately allocated to critical testing phases.")
    
    if appropriate_assignment:
        score += 10
        feedback.append("Resources appropriately assigned based on expertise.")
    else:
        feedback.append("Resource assignment could be better aligned with expertise.")
    
    return {
        "score": score,
        "max_score": 25,
        "feedback": feedback
    }

def evaluate_testing_approach(submission, answer_key):
    """Evaluate the testing approach selection."""
    score = 0
    feedback = []
    
    submission_approach = submission.get("testingApproach")
    key_approach = answer_key.get("testingApproach")
    
    if submission_approach == key_approach:
        score += 10
        feedback.append("Selected the most appropriate testing approach for the project context.")
    else:
        feedback.append(f"Selected approach '{submission_approach}' instead of the more appropriate '{key_approach}'.")
    
    return {
        "score": score,
        "max_score": 10,
        "feedback": feedback
    }

def check_automatic_failure(submission, answer_key):
    """Check for conditions that would result in automatic failure."""
    failures = []
    
    # Check for resource overallocation
    for resource in submission.get("resourceAllocation", []):
        resource_id = resource.get("resourceId")
        for week_alloc in resource.get("allocation", []):
            week = week_alloc.get("week")
            percentage = week_alloc.get("percentage")
            
            # Find the corresponding resource in the answer key
            key_resource = next((r for r in answer_key.get("resourceAllocation", []) 
                               if r.get("resourceId") == resource_id), None)
            
            if key_resource:
                key_week_alloc = next((w for w in key_resource.get("allocation", []) 
                                     if w.get("week") == week), None)
                
                if key_week_alloc and percentage > key_week_alloc.get("percentage", 0):
                    failures.append(f"Resource {resource_id} is overallocated in week {week}.")
    
    # Other automatic failure conditions would require more context
    # For simplicity, we'll focus on resource overallocation
    
    return failures

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    test_schedule_result = evaluate_test_schedule(submission, answer_key)
    risk_assessment_result = evaluate_risk_assessment(submission, answer_key)
    test_coverage_result = evaluate_test_coverage(submission, answer_key)
    resource_allocation_result = evaluate_resource_allocation(submission, answer_key)
    testing_approach_result = evaluate_testing_approach(submission, answer_key)
    
    # Check for automatic failure conditions
    automatic_failures = check_automatic_failure(submission, answer_key)
    
    # Calculate overall score
    total_score = (
        test_schedule_result["score"] +
        risk_assessment_result["score"] +
        test_coverage_result["score"] +
        resource_allocation_result["score"] +
        testing_approach_result["score"]
    )
    
    max_score = (
        test_schedule_result["max_score"] +
        risk_assessment_result["max_score"] +
        test_coverage_result["max_score"] +
        resource_allocation_result["max_score"] +
        testing_approach_result["max_score"]
    )
    
    overall_percentage = (total_score / max_score) * 100
    
    # Determine pass level
    if automatic_failures:
        pass_level = "FAIL (Automatic)"
    elif overall_percentage >= 95:
        pass_level = "DISTINCTION"
    elif overall_percentage >= 85:
        pass_level = "MERIT PASS"
    elif overall_percentage >= 70:
        pass_level = "PASS"
    else:
        pass_level = "FAIL"
    
    # Compile results
    results = {
        "candidateId": submission.get("candidateId", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "pass_level": pass_level,
        "total_points": total_score,
        "max_points": max_score,
        "automatic_failures": automatic_failures,
        "section_scores": {
            "testSchedule": test_schedule_result,
            "riskAssessment": risk_assessment_result,
            "testCoverage": test_coverage_result,
            "resourceAllocation": resource_allocation_result,
            "testingApproach": testing_approach_result
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {round(overall_percentage, 2)}% - {pass_level}")

if __name__ == "__main__":
    main()