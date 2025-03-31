import json
import os
from decimal import Decimal

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        return None

def evaluate_coverage_determination(candidate_answer, correct_answer, scenario_id):
    """Evaluate the coverage determination."""
    # Special case for scenario 5
    if scenario_id == 5:
        if candidate_answer in ["partially_covered", "additional_investigation_needed"]:
            return True, "Correct determination"
        else:
            return False, f"Incorrect determination. Expected 'partially_covered' or 'additional_investigation_needed', got '{candidate_answer}'"
    
    # For other scenarios
    if candidate_answer == correct_answer:
        return True, "Correct determination"
    else:
        return False, f"Incorrect determination. Expected '{correct_answer}', got '{candidate_answer}'"

def evaluate_payment_calculation(candidate_payment, correct_payment, scenario_id):
    """Evaluate the payment calculation with acceptable variance."""
    acceptable_variance = 100.00
    
    # Convert to Decimal for precise comparison
    candidate_payment = Decimal(str(candidate_payment))
    correct_payment = Decimal(str(correct_payment))
    
    # Define valid ranges for each scenario
    valid_ranges = {
        1: (Decimal('3667.65'), Decimal('3668.00')),
        2: (Decimal('14730.00'), Decimal('15730.00')),
        3: (Decimal('17880.00'), Decimal('17880.80')),
        4: (Decimal('566.67'), Decimal('567.00')),
        5: (Decimal('0.00'), Decimal('0.00'))
    }
    
    min_valid, max_valid = valid_ranges.get(scenario_id, (correct_payment - acceptable_variance, correct_payment + acceptable_variance))
    
    if min_valid <= candidate_payment <= max_valid:
        return True, "Correct payment calculation"
    else:
        return False, f"Incorrect payment calculation. Expected between {min_valid} and {max_valid}, got {candidate_payment}"

def evaluate_coverage_category(candidate_category, correct_category, scenario_id):
    """Evaluate the coverage category with multiple valid options."""
    valid_categories = {
        1: ["Collision", "Auto Collision"],
        2: ["Dwelling", "Property", "Water Damage"],
        3: ["Hospital Inpatient", "Medical", "Surgical"],
        4: ["Temporary Total Disability", "TTD", "Workers' Compensation"],
        5: []  # Any category is acceptable for scenario 5
    }
    
    if scenario_id == 5:
        return True, "Any category is acceptable for this scenario due to incomplete information"
    
    if candidate_category in valid_categories.get(scenario_id, [correct_category]):
        return True, "Correct coverage category"
    else:
        return False, f"Incorrect coverage category. Expected one of {valid_categories.get(scenario_id, [correct_category])}, got '{candidate_category}'"

def evaluate_policy_section(candidate_section, correct_section, scenario_id):
    """Evaluate the applicable policy section."""
    if scenario_id == 5:
        # For scenario 5, any value is acceptable since information is incomplete
        return True, "Any policy section is acceptable for this scenario due to incomplete information"
    
    if candidate_section == correct_section:
        return True, "Correct policy section"
    else:
        return False, f"Incorrect policy section. Expected '{correct_section}', got '{candidate_section}'"

def evaluate_investigation_needs(candidate_investigation, correct_investigation, scenario_id):
    """Evaluate recognition of investigation needs."""
    if candidate_investigation == correct_investigation:
        return True, "Correct identification of investigation needs"
    else:
        return False, f"Incorrect identification of investigation needs. Expected '{correct_investigation}', got '{candidate_investigation}'"

def evaluate_submission(candidate, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "scenario_results": [],
        "summary": {
            "coverage_determination": {"correct": 0, "total": 5},
            "payment_calculation": {"correct": 0, "total": 5},
            "coverage_category": {"correct": 0, "total": 5},
            "policy_section": {"correct": 0, "total": 5},
            "investigation_needs": {"correct": 0, "total": 5},
            "overall_score": 0.0
        }
    }
    
    # Map candidate scenarios by ID for easier access
    candidate_scenarios = {s["scenario_id"]: s for s in candidate.get("scenarios", [])}
    key_scenarios = {s["scenario_id"]: s for s in answer_key.get("scenarios", [])}
    
    # Evaluate each scenario
    for scenario_id in range(1, 6):
        candidate_scenario = candidate_scenarios.get(scenario_id, {})
        key_scenario = key_scenarios.get(scenario_id, {})
        
        if not candidate_scenario or not key_scenario:
            results["scenario_results"].append({
                "scenario_id": scenario_id,
                "evaluation": "Missing scenario data",
                "score": 0.0
            })
            continue
        
        scenario_result = {
            "scenario_id": scenario_id,
            "evaluations": {}
        }
        
        # Evaluate coverage determination
        correct, message = evaluate_coverage_determination(
            candidate_scenario.get("coverage_determination", ""),
            key_scenario.get("coverage_determination", ""),
            scenario_id
        )
        scenario_result["evaluations"]["coverage_determination"] = {
            "correct": correct,
            "message": message
        }
        if correct:
            results["summary"]["coverage_determination"]["correct"] += 1
        
        # Evaluate payment calculation
        correct, message = evaluate_payment_calculation(
            candidate_scenario.get("calculated_payment", 0.0),
            key_scenario.get("calculated_payment", 0.0),
            scenario_id
        )
        scenario_result["evaluations"]["payment_calculation"] = {
            "correct": correct,
            "message": message
        }
        if correct:
            results["summary"]["payment_calculation"]["correct"] += 1
        
        # Evaluate coverage category
        correct, message = evaluate_coverage_category(
            candidate_scenario.get("coverage_category", ""),
            key_scenario.get("coverage_category", ""),
            scenario_id
        )
        scenario_result["evaluations"]["coverage_category"] = {
            "correct": correct,
            "message": message
        }
        if correct:
            results["summary"]["coverage_category"]["correct"] += 1
        
        # Evaluate policy section
        correct, message = evaluate_policy_section(
            candidate_scenario.get("applicable_policy_section", ""),
            key_scenario.get("applicable_policy_section", ""),
            scenario_id
        )
        scenario_result["evaluations"]["policy_section"] = {
            "correct": correct,
            "message": message
        }
        if correct:
            results["summary"]["policy_section"]["correct"] += 1
        
        # Evaluate investigation needs
        correct, message = evaluate_investigation_needs(
            candidate_scenario.get("additional_investigation_needed", False),
            key_scenario.get("additional_investigation_needed", False),
            scenario_id
        )
        scenario_result["evaluations"]["investigation_needs"] = {
            "correct": correct,
            "message": message
        }
        if correct:
            results["summary"]["investigation_needs"]["correct"] += 1
        
        # Calculate scenario score
        correct_count = sum(1 for eval_result in scenario_result["evaluations"].values() if eval_result["correct"])
        scenario_result["score"] = (correct_count / 5) * 100  # 5 evaluation criteria per scenario
        
        results["scenario_results"].append(scenario_result)
    
    # Calculate overall score
    total_correct = sum(category["correct"] for category in results["summary"].values() if isinstance(category, dict))
    total_possible = sum(category["total"] for category in results["summary"].values() if isinstance(category, dict))
    results["summary"]["overall_score"] = (total_correct / total_possible) * 100 if total_possible > 0 else 0.0
    
    # Check passing criteria
    results["summary"]["passed"] = (
        results["summary"]["coverage_determination"]["correct"] >= 4 and
        results["summary"]["payment_calculation"]["correct"] >= 3 and
        results["summary"]["policy_section"]["correct"] >= 3 and
        results["summary"]["investigation_needs"]["correct"] >= 1 and
        results["summary"]["overall_score"] >= 80.0
    )
    
    return results

def main():
    # Load the candidate submission and answer key
    candidate = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not candidate or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(candidate, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['summary']['overall_score']:.2f}%")
    print(f"Results saved to 'test_results.json'")

if __name__ == "__main__":
    main()