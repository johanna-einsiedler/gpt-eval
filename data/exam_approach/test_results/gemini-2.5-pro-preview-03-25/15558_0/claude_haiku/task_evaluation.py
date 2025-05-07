import json
import sys
import os
from typing import List, Dict, Any, Tuple, Set

# --- Configuration ---
OUTPUT_FILENAME = "test_results.json"

# Define points for each check
POINTS_CONFIG = {
    "task1": {
        "conflict_identified": 1,
        "conflict_description": 1,
        "updated_schedule_match": 3,
        "max": 5
    },
    "task2": {
        "record_structure": 1, # Points for having the correct number of records
        "record_content_match_per_record": 1, # Points per fully correct record
        "max": 4 # 1 for structure + 3 records * 1 point/record
    },
    "task3": {
        "summary_structure": 1, # Points for having the correct number of summaries
        "summary_content_match_per_item": 1, # Points per fully correct summary item
        "max": 4 # 1 for structure + 3 summaries * 1 point/item
    }
}
# Calculate total possible points dynamically
TOTAL_POSSIBLE_POINTS = sum(v['max'] for v in POINTS_CONFIG.values())

# --- Helper Functions ---

def load_json(filepath: str) -> Dict[str, Any]:
    """Loads a JSON file and returns its content."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read file {filepath}. Details: {e}", file=sys.stderr)
        sys.exit(1)

def create_set_from_list_of_dicts(data_list: List[Dict[str, Any]]) -> Set[frozenset]:
    """Converts a list of dictionaries into a set of frozensets for order-agnostic comparison."""
    try:
        return {frozenset(item.items()) for item in data_list}
    except Exception:
        # Handle cases where items might not be hashable (e.g., lists within dict values)
        # For this specific exam structure, this shouldn't happen if format is followed.
        return set() # Return empty set to indicate comparison failure

def create_set_from_attendance_records(records: List[Dict[str, Any]]) -> Set[Tuple[str, str, frozenset]]:
    """Converts attendance records into a set of tuples with frozenset for attendees."""
    record_set = set()
    for record in records:
        try:
            # Ensure attendees list exists and is a list before creating frozenset
            attendees = record.get("attendees", [])
            if not isinstance(attendees, list):
                 attendees = [] # Treat non-list attendees as empty for comparison

            # Ensure required keys exist
            class_name = record.get("class_name", "MISSING_CLASS_NAME")
            date = record.get("date", "MISSING_DATE")

            record_set.add(
                (
                    class_name,
                    date,
                    frozenset(attendees) # Order of attendees doesn't matter
                )
            )
        except Exception:
            # Handle potential errors if record structure is severely broken
            continue # Skip malformed records
    return record_set

# --- Evaluation Functions ---

def evaluate_task1(candidate_task1: Dict, key_task1: Dict) -> Tuple[int, Dict]:
    """Evaluates Task 1: Scheduling."""
    score = 0
    details = {}
    max_points = POINTS_CONFIG["task1"]["max"]

    # Check 1: conflict_identified
    candidate_conflict_id = candidate_task1.get("conflict_identified")
    key_conflict_id = key_task1.get("conflict_identified")
    if candidate_conflict_id == key_conflict_id and isinstance(candidate_conflict_id, bool):
        score += POINTS_CONFIG["task1"]["conflict_identified"]
        details["conflict_identified"] = f"Correct ({key_conflict_id}). +{POINTS_CONFIG['task1']['conflict_identified']} points."
    else:
        details["conflict_identified"] = f"Incorrect. Expected '{key_conflict_id}', Got '{candidate_conflict_id}'. +0 points."

    # Check 2: conflict_description
    # Basic check: if conflict is true, description should not be the 'no conflict' message.
    # If conflict is false, description should be the 'no conflict' message.
    # More robust: Compare against key description (allowing for minor variations is hard, so we'll be strict or check presence)
    candidate_desc = candidate_task1.get("conflict_description", "")
    key_desc = key_task1.get("conflict_description", "")
    no_conflict_msg = "No conflict identified." # Assuming this exact phrase is used

    description_correct = False
    if key_conflict_id is True:
        # Check if candidate description is present and not the 'no conflict' message.
        # A simple check: is it reasonably similar or at least not the negative case?
        # For simplicity, we check if it's not empty and not the 'no conflict' message.
        # A stricter check could compare content, but let's be lenient for basic.
        # Let's check if it's *exactly* the key description for simplicity here.
        if candidate_desc == key_desc:
             description_correct = True
        # Lenient alternative: if candidate_desc and candidate_desc != no_conflict_msg: description_correct = True
    elif key_conflict_id is False:
        if candidate_desc == no_conflict_msg:
            description_correct = True

    if description_correct:
        score += POINTS_CONFIG["task1"]["conflict_description"]
        details["conflict_description"] = f"Correct. +{POINTS_CONFIG['task1']['conflict_description']} points."
    else:
        details["conflict_description"] = f"Incorrect. Description does not match expectation based on conflict status. Expected logic based on '{key_desc}', Got '{candidate_desc}'. +0 points."


    # Check 3: updated_schedule
    candidate_schedule = candidate_task1.get("updated_schedule", [])
    key_schedule = key_task1.get("updated_schedule", [])

    if not isinstance(candidate_schedule, list):
        details["updated_schedule"] = "Incorrect format. Expected a list. +0 points."
    else:
        candidate_schedule_set = create_set_from_list_of_dicts(candidate_schedule)
        key_schedule_set = create_set_from_list_of_dicts(key_schedule)

        if candidate_schedule_set == key_schedule_set:
            score += POINTS_CONFIG["task1"]["updated_schedule_match"]
            details["updated_schedule"] = f"Correct. Schedule matches expected content. +{POINTS_CONFIG['task1']['updated_schedule_match']} points."
        else:
            details["updated_schedule"] = f"Incorrect. Schedule content does not match expected. Expected {len(key_schedule)} items, Got {len(candidate_schedule)}. Content mismatch. +0 points."
            # Provide more detail for debugging/feedback
            details["updated_schedule_expected_items"] = [dict(fs) for fs in key_schedule_set]
            details["updated_schedule_candidate_items"] = [dict(fs) for fs in candidate_schedule_set]


    return score, {"score": score, "max_points": max_points, "details": details}

def evaluate_task2(candidate_task2: Dict, key_task2: Dict) -> Tuple[int, Dict]:
    """Evaluates Task 2: Record Keeping."""
    score = 0
    details = {}
    max_points = POINTS_CONFIG["task2"]["max"]

    candidate_records = candidate_task2.get("attendance_records", [])
    key_records = key_task2.get("attendance_records", [])

    if not isinstance(candidate_records, list):
        details["attendance_records_structure"] = "Incorrect format. Expected a list. +0 points."
        details["attendance_records_content"] = "Cannot evaluate content due to incorrect structure."
        return 0, {"score": 0, "max_points": max_points, "details": details}

    # Check 1: Structure (correct number of records)
    if len(candidate_records) == len(key_records):
        score += POINTS_CONFIG["task2"]["record_structure"]
        details["attendance_records_structure"] = f"Correct number of records ({len(key_records)}). +{POINTS_CONFIG['task2']['record_structure']} points."
    else:
        details["attendance_records_structure"] = f"Incorrect number of records. Expected {len(key_records)}, Got {len(candidate_records)}. +0 points."
        # Stop content evaluation if structure is wrong? Or try partial matching? Let's try partial.

    # Check 2: Content (match records individually)
    candidate_records_set = create_set_from_attendance_records(candidate_records)
    key_records_set = create_set_from_attendance_records(key_records)

    correct_records_count = len(candidate_records_set.intersection(key_records_set))
    content_score = correct_records_count * POINTS_CONFIG["task2"]["record_content_match_per_record"]
    score += content_score

    details["attendance_records_content"] = f"Found {correct_records_count} correctly matching records out of {len(key_records)}. +{content_score} points."

    if correct_records_count != len(key_records):
         details["attendance_records_content"] += " Mismatches detected."
         # Optional: Add details on missing/extra records if needed for feedback
         missing_records = key_records_set - candidate_records_set
         extra_records = candidate_records_set - key_records_set
         if missing_records:
             details["missing_records"] = [f"Class: {r[0]}, Date: {r[1]}, Attendees: {sorted(list(r[2]))}" for r in missing_records]
         if extra_records:
             details["extra_or_incorrect_records"] = [f"Class: {r[0]}, Date: {r[1]}, Attendees: {sorted(list(r[2]))}" for r in extra_records]


    # Ensure score doesn't exceed max points for the task
    score = min(score, max_points)

    return score, {"score": score, "max_points": max_points, "details": details}


def evaluate_task3(candidate_task3: Dict, key_task3: Dict) -> Tuple[int, Dict]:
    """Evaluates Task 3: Reporting."""
    score = 0
    details = {}
    max_points = POINTS_CONFIG["task3"]["max"]

    candidate_summary = candidate_task3.get("attendance_summary", [])
    key_summary = key_task3.get("attendance_summary", [])

    if not isinstance(candidate_summary, list):
        details["attendance_summary_structure"] = "Incorrect format. Expected a list. +0 points."
        details["attendance_summary_content"] = "Cannot evaluate content due to incorrect structure."
        return 0, {"score": 0, "max_points": max_points, "details": details}

    # Check 1: Structure (correct number of summary items)
    if len(candidate_summary) == len(key_summary):
        score += POINTS_CONFIG["task3"]["summary_structure"]
        details["attendance_summary_structure"] = f"Correct number of summary items ({len(key_summary)}). +{POINTS_CONFIG['task3']['summary_structure']} points."
    else:
        details["attendance_summary_structure"] = f"Incorrect number of summary items. Expected {len(key_summary)}, Got {len(candidate_summary)}. +0 points."

    # Check 2: Content (match summary items individually)
    candidate_summary_set = create_set_from_list_of_dicts(candidate_summary)
    key_summary_set = create_set_from_list_of_dicts(key_summary)

    correct_items_count = len(candidate_summary_set.intersection(key_summary_set))
    content_score = correct_items_count * POINTS_CONFIG["task3"]["summary_content_match_per_item"]
    score += content_score

    details["attendance_summary_content"] = f"Found {correct_items_count} correctly matching summary items out of {len(key_summary)}. +{content_score} points."

    if correct_items_count != len(key_summary):
         details["attendance_summary_content"] += " Mismatches detected."
         # Optional: Add details on missing/extra items
         missing_items = key_summary_set - candidate_summary_set
         extra_items = candidate_summary_set - key_summary_set
         if missing_items:
             details["missing_summary_items"] = [dict(fs) for fs in missing_items]
         if extra_items:
             details["extra_or_incorrect_summary_items"] = [dict(fs) for fs in extra_items]

    # Ensure score doesn't exceed max points for the task
    score = min(score, max_points)

    return score, {"score": score, "max_points": max_points, "details": details}

# --- Main Execution ---

def main():
    """Main function to orchestrate the evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <candidate_submission.json> <answer_key.json>", file=sys.stderr)
        sys.exit(1)

    candidate_file = sys.argv[1]
    key_file = sys.argv[2]

    print(f"Loading candidate submission from: {candidate_file}")
    candidate_data = load_json(candidate_file)
    print(f"Loading answer key from: {key_file}")
    key_data = load_json(key_file)

    results = {
        "candidate_file": candidate_file,
        "answer_key_file": key_file,
        "candidate_id": candidate_data.get("candidate_id", "ID_MISSING"),
        "evaluation_details": {},
        "overall_score": 0.0,
        "total_score_achieved": 0,
        "total_possible_points": TOTAL_POSSIBLE_POINTS
    }

    total_score_achieved = 0

    # --- Evaluate Task 1 ---
    print("Evaluating Task 1: Scheduling...")
    try:
        task1_score, task1_results = evaluate_task1(
            candidate_data.get("task_1_scheduling", {}),
            key_data.get("task_1_scheduling", {})
        )
        results["evaluation_details"]["task_1_scheduling"] = task1_results
        total_score_achieved += task1_score
        print(f"Task 1 Score: {task1_score}/{task1_results['max_points']}")
    except Exception as e:
        print(f"Error evaluating Task 1: {e}", file=sys.stderr)
        results["evaluation_details"]["task_1_scheduling"] = {"error": str(e), "score": 0, "max_points": POINTS_CONFIG["task1"]["max"]}

    # --- Evaluate Task 2 ---
    print("Evaluating Task 2: Record Keeping...")
    try:
        task2_score, task2_results = evaluate_task2(
            candidate_data.get("task_2_record_keeping", {}),
            key_data.get("task_2_record_keeping", {})
        )
        results["evaluation_details"]["task_2_record_keeping"] = task2_results
        total_score_achieved += task2_score
        print(f"Task 2 Score: {task2_score}/{task2_results['max_points']}")
    except Exception as e:
        print(f"Error evaluating Task 2: {e}", file=sys.stderr)
        results["evaluation_details"]["task_2_record_keeping"] = {"error": str(e), "score": 0, "max_points": POINTS_CONFIG["task2"]["max"]}

    # --- Evaluate Task 3 ---
    print("Evaluating Task 3: Reporting...")
    try:
        task3_score, task3_results = evaluate_task3(
            candidate_data.get("task_3_reporting", {}),
            key_data.get("task_3_reporting", {})
        )
        results["evaluation_details"]["task_3_reporting"] = task3_results
        total_score_achieved += task3_score
        print(f"Task 3 Score: {task3_score}/{task3_results['max_points']}")
    except Exception as e:
        print(f"Error evaluating Task 3: {e}", file=sys.stderr)
        results["evaluation_details"]["task_3_reporting"] = {"error": str(e), "score": 0, "max_points": POINTS_CONFIG["task3"]["max"]}

    # --- Calculate Final Score ---
    results["total_score_achieved"] = total_score_achieved
    if TOTAL_POSSIBLE_POINTS > 0:
        overall_percentage = round((total_score_achieved / TOTAL_POSSIBLE_POINTS) * 100, 2)
    else:
        overall_percentage = 0.0
    results["overall_score"] = overall_percentage

    print(f"\nTotal Score: {total_score_achieved}/{TOTAL_POSSIBLE_POINTS}")
    print(f"Overall Percentage: {overall_percentage}%")

    # --- Save Results ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to: {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error: Could not write results to {OUTPUT_FILENAME}. Details: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()