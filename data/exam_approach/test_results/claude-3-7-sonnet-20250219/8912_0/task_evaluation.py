#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Any, Tuple

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_trauma_identification(submission: List[str], answer_key: List[str]) -> Tuple[int, int]:
    """
    Evaluate trauma identification answers.
    Returns (points_earned, max_points)
    """
    max_points = 4
    
    # Check if all correct trauma types are identified (no extras, no missing)
    if sorted(submission) == sorted(answer_key):
        return max_points, max_points
    
    # Partial credit: 1 point for each correct trauma type, up to max_points
    correct_count = sum(1 for item in submission if item in answer_key)
    return min(correct_count, max_points), max_points

def evaluate_postmortem_interval(submission: str, answer_key: str) -> Tuple[int, int]:
    """
    Evaluate postmortem interval answers.
    Returns (points_earned, max_points)
    """
    max_points = 4
    return (max_points if submission == answer_key else 0), max_points

def evaluate_victim_characteristics(submission: str, answer_key: str) -> Tuple[int, int]:
    """
    Evaluate victim characteristics answers.
    Returns (points_earned, max_points)
    """
    max_points = 4
    return (max_points if submission == answer_key else 0), max_points

def evaluate_error_identification(submission: str, answer_key: str) -> Tuple[int, int]:
    """
    Evaluate error identification answers.
    Returns (points_earned, max_points)
    """
    max_points = 3
    return (max_points if submission == answer_key else 0), max_points

def evaluate_procedure_sequencing(submission: int, answer_key: int) -> Tuple[int, int]:
    """
    Evaluate procedure sequencing answers.
    Returns (points_earned, max_points)
    """
    max_points = 2
    
    # Full points if exact position
    if submission == answer_key:
        return max_points, max_points
    
    # Partial credit (1 point) if within ±1 position
    if abs(submission - answer_key) == 1:
        return 1, max_points
    
    # No points if more than 1 position away
    return 0, max_points

def evaluate_documentation_exercise(submission: Dict, answer_key: Dict) -> Tuple[int, Dict]:
    """
    Evaluate documentation exercise answers.
    Returns (points_earned, detailed_results)
    """
    results = {
        "decedent_information": 0,
        "scene_findings": 0,
        "postmortem_changes": 0,
        "preliminary_cause_of_death": 0,
        "preliminary_manner_of_death": 0
    }
    
    # Decedent information (3 points)
    if (submission["decedent_information"]["age"] == answer_key["decedent_information"]["age"] and
        submission["decedent_information"]["sex"] == answer_key["decedent_information"]["sex"] and
        sorted(submission["decedent_information"]["identifying_features"]) == 
        sorted(answer_key["decedent_information"]["identifying_features"])):
        results["decedent_information"] = 3
    
    # Scene findings (4 points)
    scene_points = 0
    if submission["scene_findings"]["position_of_body"] == answer_key["scene_findings"]["position_of_body"]:
        scene_points += 1
    if submission["scene_findings"]["surrounding_environment"] == answer_key["scene_findings"]["surrounding_environment"]:
        scene_points += 1
    
    # Check relevant items (2 points)
    relevant_items_match = True
    for item in answer_key["scene_findings"]["relevant_items"]:
        if item not in submission["scene_findings"]["relevant_items"]:
            relevant_items_match = False
            break
    if relevant_items_match and len(submission["scene_findings"]["relevant_items"]) == len(answer_key["scene_findings"]["relevant_items"]):
        scene_points += 2
    
    results["scene_findings"] = scene_points
    
    # Postmortem changes (5 points)
    pm_points = 0
    if submission["postmortem_changes"]["rigor_mortis"] == answer_key["postmortem_changes"]["rigor_mortis"]:
        pm_points += 2
    if submission["postmortem_changes"]["livor_mortis"] == answer_key["postmortem_changes"]["livor_mortis"]:
        pm_points += 1
    if submission["postmortem_changes"]["estimated_pmi"] == answer_key["postmortem_changes"]["estimated_pmi"]:
        pm_points += 2
    
    results["postmortem_changes"] = pm_points
    
    # Preliminary cause of death (3 points)
    if submission["preliminary_cause_of_death"] == answer_key["preliminary_cause_of_death"]:
        results["preliminary_cause_of_death"] = 3
    
    # Preliminary manner of death (2 points)
    if submission["preliminary_manner_of_death"] == answer_key["preliminary_manner_of_death"]:
        results["preliminary_manner_of_death"] = 2
    
    total_points = sum(results.values())
    return total_points, results

def check_critical_errors(submission: Dict, answer_key: Dict) -> List[str]:
    """Check for critical errors that result in automatic failure."""
    critical_errors = []
    
    # 1. Failure to identify asphyxial injury (AS) in Case A
    if "AS" not in submission["section1"]["caseA"]["trauma_identification"]:
        critical_errors.append("Failed to identify asphyxial injury (AS) in Case A")
    
    # 2. Failure to identify blunt force trauma (BL) and gunshot wound (GS) in Case C
    if "BL" not in submission["section1"]["caseC"]["trauma_identification"]:
        critical_errors.append("Failed to identify blunt force trauma (BL) in Case C")
    if "GS" not in submission["section1"]["caseC"]["trauma_identification"]:
        critical_errors.append("Failed to identify gunshot wound (GS) in Case C")
    
    # 3. Estimating postmortem interval as less than 72 hours for Case D
    if submission["section1"]["caseD"]["postmortem_interval"] != ">72 hours":
        critical_errors.append("Incorrectly estimated postmortem interval for Case D as less than 72 hours")
    
    # 4. Placing procedure step G before step C
    if (submission["section2"]["procedure_sequencing"]["G"] < 
        submission["section2"]["procedure_sequencing"]["C"]):
        critical_errors.append("Incorrectly placed procedure step G before step C")
    
    # 5. Indicating a definitive manner of death as "Suicide" for Case E
    if submission["section2"]["documentation_exercise"]["preliminary_manner_of_death"] == "Suicide":
        critical_errors.append("Incorrectly indicated a definitive manner of death as 'Suicide' for Case E without toxicology")
    
    return critical_errors

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "section1": {
            "caseA": {},
            "caseB": {},
            "caseC": {},
            "caseD": {},
            "total_points": 0,
            "max_points": 48
        },
        "section2": {
            "error_identification": {},
            "procedure_sequencing": {},
            "documentation_exercise": {},
            "total_points": 0,
            "max_points": 52
        },
        "critical_errors": [],
        "overall_score": 0,
        "passing_status": "FAIL"
    }
    
    # Section 1: Case Analysis
    section1_points = 0
    
    # Case A
    results["section1"]["caseA"]["trauma_identification_points"], _ = evaluate_trauma_identification(
        submission["section1"]["caseA"]["trauma_identification"],
        answer_key["section1"]["caseA"]["trauma_identification"]
    )
    
    results["section1"]["caseA"]["postmortem_interval_points"], _ = evaluate_postmortem_interval(
        submission["section1"]["caseA"]["postmortem_interval"],
        answer_key["section1"]["caseA"]["postmortem_interval"]
    )
    
    results["section1"]["caseA"]["victim_characteristics_points"], _ = evaluate_victim_characteristics(
        submission["section1"]["caseA"]["victim_characteristics"],
        answer_key["section1"]["caseA"]["victim_characteristics"]
    )
    
    results["section1"]["caseA"]["total_points"] = (
        results["section1"]["caseA"]["trauma_identification_points"] +
        results["section1"]["caseA"]["postmortem_interval_points"] +
        results["section1"]["caseA"]["victim_characteristics_points"]
    )
    section1_points += results["section1"]["caseA"]["total_points"]
    
    # Case B
    results["section1"]["caseB"]["trauma_identification_points"], _ = evaluate_trauma_identification(
        submission["section1"]["caseB"]["trauma_identification"],
        answer_key["section1"]["caseB"]["trauma_identification"]
    )
    
    results["section1"]["caseB"]["postmortem_interval_points"], _ = evaluate_postmortem_interval(
        submission["section1"]["caseB"]["postmortem_interval"],
        answer_key["section1"]["caseB"]["postmortem_interval"]
    )
    
    results["section1"]["caseB"]["victim_characteristics_points"], _ = evaluate_victim_characteristics(
        submission["section1"]["caseB"]["victim_characteristics"],
        answer_key["section1"]["caseB"]["victim_characteristics"]
    )
    
    results["section1"]["caseB"]["total_points"] = (
        results["section1"]["caseB"]["trauma_identification_points"] +
        results["section1"]["caseB"]["postmortem_interval_points"] +
        results["section1"]["caseB"]["victim_characteristics_points"]
    )
    section1_points += results["section1"]["caseB"]["total_points"]
    
    # Case C
    results["section1"]["caseC"]["trauma_identification_points"], _ = evaluate_trauma_identification(
        submission["section1"]["caseC"]["trauma_identification"],
        answer_key["section1"]["caseC"]["trauma_identification"]
    )
    
    results["section1"]["caseC"]["postmortem_interval_points"], _ = evaluate_postmortem_interval(
        submission["section1"]["caseC"]["postmortem_interval"],
        answer_key["section1"]["caseC"]["postmortem_interval"]
    )
    
    results["section1"]["caseC"]["victim_characteristics_points"], _ = evaluate_victim_characteristics(
        submission["section1"]["caseC"]["victim_characteristics"],
        answer_key["section1"]["caseC"]["victim_characteristics"]
    )
    
    results["section1"]["caseC"]["total_points"] = (
        results["section1"]["caseC"]["trauma_identification_points"] +
        results["section1"]["caseC"]["postmortem_interval_points"] +
        results["section1"]["caseC"]["victim_characteristics_points"]
    )
    section1_points += results["section1"]["caseC"]["total_points"]
    
    # Case D
    results["section1"]["caseD"]["trauma_identification_points"], _ = evaluate_trauma_identification(
        submission["section1"]["caseD"]["trauma_identification"],
        answer_key["section1"]["caseD"]["trauma_identification"]
    )
    
    results["section1"]["caseD"]["postmortem_interval_points"], _ = evaluate_postmortem_interval(
        submission["section1"]["caseD"]["postmortem_interval"],
        answer_key["section1"]["caseD"]["postmortem_interval"]
    )
    
    results["section1"]["caseD"]["victim_characteristics_points"], _ = evaluate_victim_characteristics(
        submission["section1"]["caseD"]["victim_characteristics"],
        answer_key["section1"]["caseD"]["victim_characteristics"]
    )
    
    results["section1"]["caseD"]["total_points"] = (
        results["section1"]["caseD"]["trauma_identification_points"] +
        results["section1"]["caseD"]["postmortem_interval_points"] +
        results["section1"]["caseD"]["victim_characteristics_points"]
    )
    section1_points += results["section1"]["caseD"]["total_points"]
    
    results["section1"]["total_points"] = section1_points
    
    # Section 2: Procedural Assessment
    section2_points = 0
    
    # Error Identification
    error_id_points = 0
    for video_num in range(1, 6):
        video_key = f"video{video_num}"
        points, _ = evaluate_error_identification(
            submission["section2"]["error_identification"][video_key],
            answer_key["section2"]["error_identification"][video_key]
        )
        results["section2"]["error_identification"][video_key] = points
        error_id_points += points
    
    results["section2"]["error_identification"]["total_points"] = error_id_points
    section2_points += error_id_points
    
    # Procedure Sequencing
    proc_seq_points = 0
    for step in "ABCDEFGHIJ":
        points, _ = evaluate_procedure_sequencing(
            submission["section2"]["procedure_sequencing"][step],
            answer_key["section2"]["procedure_sequencing"][step]
        )
        results["section2"]["procedure_sequencing"][step] = points
        proc_seq_points += points
    
    results["section2"]["procedure_sequencing"]["total_points"] = proc_seq_points
    section2_points += proc_seq_points
    
    # Documentation Exercise
    doc_points, doc_details = evaluate_documentation_exercise(
        submission["section2"]["documentation_exercise"],
        answer_key["section2"]["documentation_exercise"]
    )
    results["section2"]["documentation_exercise"] = doc_details
    results["section2"]["documentation_exercise"]["total_points"] = doc_points
    section2_points += doc_points
    
    results["section2"]["total_points"] = section2_points
    
    # Check for critical errors
    results["critical_errors"] = check_critical_errors(submission, answer_key)
    
    # Calculate overall score
    total_points = section1_points + section2_points
    max_points = results["section1"]["max_points"] + results["section2"]["max_points"]
    results["overall_score"] = round((total_points / max_points) * 100, 2)
    
    # Determine passing status
    if results["critical_errors"]:
        results["passing_status"] = "FAIL (Critical Error)"
    elif total_points >= 75 and section1_points >= 36 and section2_points >= 39:
        if results["overall_score"] >= 90:
            results["passing_status"] = "PASS (Excellent)"
        elif results["overall_score"] >= 80:
            results["passing_status"] = "PASS (Good)"
        else:
            results["passing_status"] = "PASS (Satisfactory)"
    else:
        results["passing_status"] = "FAIL (Unsatisfactory)"
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
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
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Status: {results['passing_status']}")
    
    if results["critical_errors"]:
        print("\nCritical Errors:")
        for error in results["critical_errors"]:
            print(f"- {error}")

if __name__ == "__main__":
    main()