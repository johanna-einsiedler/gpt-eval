#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Union

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_exercise1(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 1: Directive Interpretation."""
    results = {
        "points_possible": 30,
        "points_earned": 0,
        "details": []
    }
    
    # Get directives from submission and answer key
    sub_directives = submission.get("exercise1", {}).get("keyDirectives", [])
    key_directives = answer_key.get("exercise1", {}).get("keyDirectives", [])
    
    # Create a mapping of directive numbers to directives in the answer key
    key_directives_map = {d["directiveNumber"]: d for d in key_directives}
    
    # Points for each directive (5 points each, 25 total)
    directive_points = 0
    
    for sub_directive in sub_directives:
        directive_num = sub_directive.get("directiveNumber")
        if directive_num not in key_directives_map:
            results["details"].append({
                "directive": directive_num,
                "status": "Invalid directive number",
                "points": 0,
                "max_points": 5
            })
            continue
        
        key_directive = key_directives_map[directive_num]
        points = 5
        errors = []
        
        # Check each field
        if sub_directive.get("directiveText") != key_directive.get("directiveText"):
            points -= 1
            errors.append("Incorrect directive text")
        
        if sub_directive.get("priority") != key_directive.get("priority"):
            points -= 1
            errors.append("Incorrect priority")
        
        if sub_directive.get("implementationDeadline") != key_directive.get("implementationDeadline"):
            points -= 1
            errors.append("Incorrect implementation deadline")
        
        # Check department codes
        sub_depts = set(sub_directive.get("affectedDepartmentCodes", []))
        key_depts = set(key_directive.get("affectedDepartmentCodes", []))
        
        if sub_depts != key_depts:
            points -= 1
            errors.append("Incorrect department codes")
        
        directive_points += points
        
        results["details"].append({
            "directive": directive_num,
            "status": "Correct" if not errors else ", ".join(errors),
            "points": points,
            "max_points": 5
        })
    
    # Check if all directives were included
    if len(sub_directives) < len(key_directives):
        results["details"].append({
            "status": f"Missing {len(key_directives) - len(sub_directives)} directives",
            "points": 0,
            "max_points": 5 * (len(key_directives) - len(sub_directives))
        })
    
    # Add points for complete accuracy if all directives are perfect
    accuracy_points = 5 if directive_points == 25 else 0
    results["details"].append({
        "status": "Complete accuracy across all directives" if accuracy_points == 5 else "Errors in one or more directives",
        "points": accuracy_points,
        "max_points": 5
    })
    
    results["points_earned"] = directive_points + accuracy_points
    return results

def evaluate_exercise2(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 2: Budget Analysis."""
    results = {
        "points_possible": 40,
        "points_earned": 0,
        "details": []
    }
    
    # Get budget impacts from submission and answer key
    sub_impacts = submission.get("exercise2", {}).get("budgetImpacts", [])
    key_impacts = answer_key.get("exercise2", {}).get("budgetImpacts", [])
    
    # Create a mapping of directive numbers to impacts in the answer key
    key_impacts_map = {d["directiveNumber"]: d for d in key_impacts}
    
    # Points for each directive's total cost (5 points each, 25 total)
    total_cost_points = 0
    
    for sub_impact in sub_impacts:
        directive_num = sub_impact.get("directiveNumber")
        if directive_num not in key_impacts_map:
            results["details"].append({
                "directive": directive_num,
                "status": "Invalid directive number",
                "points": 0,
                "max_points": 5
            })
            continue
        
        key_impact = key_impacts_map[directive_num]
        
        # Check total cost
        sub_total = sub_impact.get("totalCost", 0)
        key_total = key_impact.get("totalCost", 0)
        
        if sub_total == key_total:
            points = 5
            status = "Correct total cost"
        elif abs(sub_total - key_total) <= key_total * 0.1:  # Within 10%
            points = 3
            status = f"Total cost within 10% of correct value ({key_total})"
        else:
            points = 1
            status = f"Incorrect total cost (should be {key_total})"
        
        total_cost_points += points
        
        results["details"].append({
            "directive": directive_num,
            "status": status,
            "points": points,
            "max_points": 5
        })
    
    # Check if all directives were included
    if len(sub_impacts) < len(key_impacts):
        results["details"].append({
            "status": f"Missing {len(key_impacts) - len(sub_impacts)} directive impacts",
            "points": 0,
            "max_points": 5 * (len(key_impacts) - len(sub_impacts))
        })
    
    # Check department-level adjustments (5 points)
    dept_adjustment_points = 5
    dept_errors = []
    
    for sub_impact in sub_impacts:
        directive_num = sub_impact.get("directiveNumber")
        if directive_num not in key_impacts_map:
            continue
        
        key_impact = key_impacts_map[directive_num]
        
        # Create mappings of department codes to adjustments
        sub_depts = {d["departmentCode"]: d for d in sub_impact.get("affectedDepartments", [])}
        key_depts = {d["departmentCode"]: d for d in key_impact.get("affectedDepartments", [])}
        
        # Check for missing departments
        missing_depts = set(key_depts.keys()) - set(sub_depts.keys())
        if missing_depts:
            dept_adjustment_points -= min(1, len(missing_depts))
            dept_errors.append(f"Directive {directive_num}: Missing departments {', '.join(missing_depts)}")
        
        # Check adjustment values
        for dept_code, key_dept in key_depts.items():
            if dept_code not in sub_depts:
                continue
                
            sub_dept = sub_depts[dept_code]
            key_adj = key_dept.get("requiredAdjustment", 0)
            sub_adj = sub_dept.get("requiredAdjustment", 0)
            
            if key_adj != sub_adj and abs(key_adj - sub_adj) > abs(key_adj * 0.1):
                dept_adjustment_points -= 0.5
                dept_errors.append(f"Directive {directive_num}, Dept {dept_code}: Incorrect adjustment")
    
    dept_adjustment_points = max(0, dept_adjustment_points)
    
    results["details"].append({
        "status": "Department-level adjustments" + (": " + "; ".join(dept_errors) if dept_errors else ": All correct"),
        "points": dept_adjustment_points,
        "max_points": 5
    })
    
    # Check compliance calculations (5 points)
    sub_compliance = submission.get("exercise2", {}).get("complianceCalculations", {})
    key_compliance = answer_key.get("exercise2", {}).get("complianceCalculations", {})
    
    compliance_points = 5
    compliance_errors = []
    
    # Check total budget adjustment
    sub_total_adj = sub_compliance.get("totalBudgetAdjustment", 0)
    key_total_adj = key_compliance.get("totalBudgetAdjustment", 0)
    
    if sub_total_adj != key_total_adj and abs(sub_total_adj - key_total_adj) > key_total_adj * 0.1:
        compliance_points -= 1
        compliance_errors.append(f"Incorrect total budget adjustment (should be {key_total_adj})")
    
    # Check percentage of total budget
    sub_pct = sub_compliance.get("percentageOfTotalBudget", 0)
    key_pct = key_compliance.get("percentageOfTotalBudget", 0)
    
    if abs(sub_pct - key_pct) > 0.5:  # Allow 0.5% difference
        compliance_points -= 1
        compliance_errors.append(f"Incorrect percentage of total budget (should be {key_pct})")
    
    # Check highest impact directive
    if sub_compliance.get("highestImpactDirectiveNumber") != key_compliance.get("highestImpactDirectiveNumber"):
        compliance_points -= 1
        compliance_errors.append(f"Incorrect highest impact directive (should be {key_compliance.get('highestImpactDirectiveNumber')})")
    
    # Check lowest impact directive
    if sub_compliance.get("lowestImpactDirectiveNumber") != key_compliance.get("lowestImpactDirectiveNumber"):
        compliance_points -= 1
        compliance_errors.append(f"Incorrect lowest impact directive (should be {key_compliance.get('lowestImpactDirectiveNumber')})")
    
    results["details"].append({
        "status": "Compliance calculations" + (": " + "; ".join(compliance_errors) if compliance_errors else ": All correct"),
        "points": compliance_points,
        "max_points": 5
    })
    
    # Check highest/lowest impact directives (5 points)
    impact_points = 5
    if sub_compliance.get("highestImpactDirectiveNumber") != key_compliance.get("highestImpactDirectiveNumber"):
        impact_points -= 2.5
    if sub_compliance.get("lowestImpactDirectiveNumber") != key_compliance.get("lowestImpactDirectiveNumber"):
        impact_points -= 2.5
    
    results["details"].append({
        "status": "Identification of highest/lowest impact directives" + 
                 (": Correct" if impact_points == 5 else ": Incorrect"),
        "points": impact_points,
        "max_points": 5
    })
    
    results["points_earned"] = total_cost_points + dept_adjustment_points + compliance_points + impact_points
    return results

def evaluate_exercise3(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate Exercise 3: Policy Development."""
    results = {
        "points_possible": 30,
        "points_earned": 0,
        "details": []
    }
    
    # Get policies from submission and answer key
    sub_policies = submission.get("exercise3", {}).get("policies", [])
    key_policies = answer_key.get("exercise3", {}).get("policies", [])
    
    # Check if the correct high-priority directives were selected (5 points)
    key_directive_nums = {p["directiveNumber"] for p in key_policies}
    sub_directive_nums = {p["directiveNumber"] for p in sub_policies}
    
    # Critical directives (2 and 5) must be included
    critical_directives = {2, 5}
    missing_critical = critical_directives - sub_directive_nums
    
    # Either directive 1 or 4 (both High priority) can be included
    high_directives = {1, 4}
    has_high_directive = bool(high_directives & sub_directive_nums)
    
    priority_points = 5
    priority_errors = []
    
    if missing_critical:
        priority_points -= 2 * len(missing_critical)
        priority_errors.append(f"Missing critical directive(s): {', '.join(map(str, missing_critical))}")
    
    if not has_high_directive:
        priority_points -= 2
        priority_errors.append("Missing high priority directive (should include either 1 or 4)")
    
    # Check for incorrect directives
    incorrect_directives = sub_directive_nums - (critical_directives | high_directives)
    if incorrect_directives:
        priority_points -= 1 * len(incorrect_directives)
        priority_errors.append(f"Included incorrect directive(s): {', '.join(map(str, incorrect_directives))}")
    
    results["details"].append({
        "status": "Selection of highest-priority directives" + 
                 (": Correct" if not priority_errors else ": " + "; ".join(priority_errors)),
        "points": max(0, priority_points),
        "max_points": 5
    })
    
    # Create a mapping of directive numbers to expected policy codes
    expected_policy_codes = {
        1: "POL-RED-01",
        2: "POL-SEC-01",
        4: "POL-ZBB-01",
        5: "POL-RES-01"
    }
    
    # Check policy codes (5 points)
    policy_code_points = 5
    policy_code_errors = []
    
    for policy in sub_policies:
        directive_num = policy.get("directiveNumber")
        if directive_num not in expected_policy_codes:
            continue
            
        expected_code = expected_policy_codes[directive_num]
        actual_code = policy.get("policyCode")
        
        if actual_code != expected_code:
            policy_code_points -= 1
            policy_code_errors.append(f"Directive {directive_num}: Incorrect policy code (should be {expected_code})")
    
    results["details"].append({
        "status": "Selection of appropriate policy codes" + 
                 (": Correct" if not policy_code_errors else ": " + "; ".join(policy_code_errors)),
        "points": max(0, policy_code_points),
        "max_points": 5
    })
    
    # Check implementation steps (5 points)
    # This is more subjective, so we'll just check that they selected 3 steps for each policy
    impl_steps_points = 5
    impl_steps_errors = []
    
    for policy in sub_policies:
        directive_num = policy.get("directiveNumber")
        steps = policy.get("implementationSteps", [])
        
        if len(steps) != 3:
            impl_steps_points -= 1
            impl_steps_errors.append(f"Directive {directive_num}: Should have exactly 3 implementation steps")
        
        # Check that all steps start with "STEP-"
        invalid_steps = [step for step in steps if not step.startswith("STEP-")]
        if invalid_steps:
            impl_steps_points -= 1
            impl_steps_errors.append(f"Directive {directive_num}: Invalid step code(s)")
    
    results["details"].append({
        "status": "Selection of logical implementation steps" + 
                 (": Correct" if not impl_steps_errors else ": " + "; ".join(impl_steps_errors)),
        "points": max(0, impl_steps_points),
        "max_points": 5
    })
    
    # Check required resources (5 points)
    resources_points = 5
    resources_errors = []
    
    for policy in sub_policies:
        directive_num = policy.get("directiveNumber")
        resources = policy.get("requiredResources", {})
        
        # Check personnel hours
        if "personnelHours" not in resources or not isinstance(resources["personnelHours"], int) or resources["personnelHours"] <= 0:
            resources_points -= 0.5
            resources_errors.append(f"Directive {directive_num}: Missing or invalid personnel hours")
        
        # Check system changes
        system_changes = resources.get("systemChanges", [])
        if not system_changes or len(system_changes) > 3:
            resources_points -= 0.5
            resources_errors.append(f"Directive {directive_num}: Should have 1-3 system changes")
        
        # Check that all system changes start with "SYS-"
        invalid_sys = [sys for sys in system_changes if not sys.startswith("SYS-")]
        if invalid_sys:
            resources_points -= 0.5
            resources_errors.append(f"Directive {directive_num}: Invalid system change code(s)")
        
        # Check training requirements
        training_reqs = resources.get("trainingRequirements", [])
        if not training_reqs or len(training_reqs) > 3:
            resources_points -= 0.5
            resources_errors.append(f"Directive {directive_num}: Should have 1-3 training requirements")
        
        # Check that all training requirements start with "TRAIN-"
        invalid_train = [train for train in training_reqs if not train.startswith("TRAIN-")]
        if invalid_train:
            resources_points -= 0.5
            resources_errors.append(f"Directive {directive_num}: Invalid training requirement code(s)")
    
    results["details"].append({
        "status": "Specification of appropriate required resources" + 
                 (": Correct" if not resources_errors else ": " + "; ".join(resources_errors)),
        "points": max(0, resources_points),
        "max_points": 5
    })
    
    # Check monitoring metrics (5 points)
    metrics_points = 5
    metrics_errors = []
    
    for policy in sub_policies:
        directive_num = policy.get("directiveNumber")
        metrics = policy.get("monitoringMetrics", [])
        
        if not metrics or len(metrics) < 2 or len(metrics) > 3:
            metrics_points -= 1
            metrics_errors.append(f"Directive {directive_num}: Should have 2-3 monitoring metrics")
        
        # Check that all metrics start with "METRIC-"
        invalid_metrics = [metric for metric in metrics if not metric.startswith("METRIC-")]
        if invalid_metrics:
            metrics_points -= 1
            metrics_errors.append(f"Directive {directive_num}: Invalid monitoring metric code(s)")
    
    results["details"].append({
        "status": "Selection of relevant monitoring metrics" + 
                 (": Correct" if not metrics_errors else ": " + "; ".join(metrics_errors)),
        "points": max(0, metrics_points),
        "max_points": 5
    })
    
    # Overall policy coherence (5 points)
    # This is subjective, but we'll check for basic alignment between directives and policies
    coherence_points = 5
    
    # For simplicity, we'll just check if the previous sections scored well
    if priority_points < 3 or policy_code_points < 3:
        coherence_points -= 2
    
    if impl_steps_points < 3 or resources_points < 3 or metrics_points < 3:
        coherence_points -= 2
    
    results["details"].append({
        "status": "Overall policy coherence and alignment with directives",
        "points": max(0, coherence_points),
        "max_points": 5
    })
    
    results["points_earned"] = (
        max(0, priority_points) + 
        max(0, policy_code_points) + 
        max(0, impl_steps_points) + 
        max(0, resources_points) + 
        max(0, metrics_points) + 
        max(0, coherence_points)
    )
    
    return results

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidateInfo": submission.get("candidateInfo", {}),
        "exercise1": evaluate_exercise1(submission, answer_key),
        "exercise2": evaluate_exercise2(submission, answer_key),
        "exercise3": evaluate_exercise3(submission, answer_key)
    }
    
    # Calculate overall score
    total_points_possible = (
        results["exercise1"]["points_possible"] +
        results["exercise2"]["points_possible"] +
        results["exercise3"]["points_possible"]
    )
    
    total_points_earned = (
        results["exercise1"]["points_earned"] +
        results["exercise2"]["points_earned"] +
        results["exercise3"]["points_earned"]
    )
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    results["total_points_earned"] = total_points_earned
    results["total_points_possible"] = total_points_possible
    results["pass_fail"] = "PASS" if results["overall_score"] >= 70 else "FAIL"
    
    return results

def main():
    """Main function to process command line arguments and evaluate the submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}% ({results['total_points_earned']}/{results['total_points_possible']} points)")
    print(f"Result: {results['pass_fail']}")

if __name__ == "__main__":
    main()