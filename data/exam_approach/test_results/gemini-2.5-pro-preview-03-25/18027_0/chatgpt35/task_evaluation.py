import json
import sys
import os
from collections import OrderedDict

# --- Constants for Scoring ---
MAX_POINTS_PRIORITIZATION = 35
MAX_POINTS_ALLOCATION = 40
MAX_POINTS_RESOURCE_SUMMARY = 15
MAX_POINTS_FORMATTING = 10
TOTAL_MAX_POINTS = MAX_POINTS_PRIORITIZATION + MAX_POINTS_ALLOCATION + MAX_POINTS_RESOURCE_SUMMARY + MAX_POINTS_FORMATTING

# --- Helper Functions ---

def load_json(file_path):
    """Loads JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=OrderedDict) # Keep order for array checks
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def get_task_details(data, section_key):
    """Extracts task details into a dictionary keyed by task_id."""
    details = OrderedDict()
    if section_key in data and isinstance(data[section_key], list):
        for item in data[section_key]:
            if isinstance(item, dict) and 'task_id' in item:
                details[item['task_id']] = item
    return details

def get_resource_summary_details(data):
    """Extracts resource summary details into a dictionary keyed by resource_id."""
    details = OrderedDict()
    if 'resource_summary' in data and isinstance(data['resource_summary'], list):
        for item in data['resource_summary']:
            if isinstance(item, dict) and 'resource_id' in item:
                details[item['resource_id']] = item
    return details

# --- Scoring Functions ---

def score_formatting(candidate_data, key_data):
    """Scores the JSON formatting and basic compliance."""
    score = 0
    details = {}
    max_points = MAX_POINTS_FORMATTING

    # 1. Valid JSON Structure (3 points) - Implicitly checked by load_json success
    # If the script reaches here, JSON is valid.
    score += 3
    details['valid_json_structure'] = {'score': 3, 'max': 3, 'comment': 'JSON loaded successfully.'}

    # 2. Correct Keys, Data Types, Predefined Strings (basic check) (3 points)
    basic_compliance_score = 0
    required_keys = ["exam_level", "candidate_id", "planning_period_weeks",
                     "prioritized_allocation", "unallocated_tasks", "resource_summary"]
    keys_present = all(key in candidate_data for key in required_keys)
    types_correct = (
        isinstance(candidate_data.get("exam_level"), str) and
        isinstance(candidate_data.get("candidate_id"), str) and
        isinstance(candidate_data.get("planning_period_weeks"), int) and
        isinstance(candidate_data.get("prioritized_allocation"), list) and
        isinstance(candidate_data.get("unallocated_tasks"), list) and
        isinstance(candidate_data.get("resource_summary"), list)
    )
    predefined_values_correct = (
        candidate_data.get("exam_level") == "basic" and
        candidate_data.get("planning_period_weeks") == 4
    )

    if keys_present and types_correct and predefined_values_correct:
        basic_compliance_score = 3
        comment = "All required top-level keys present with correct types and basic values."
    else:
        missing = [key for key in required_keys if key not in candidate_data]
        comment = f"Failed basic structure/value checks. Missing keys: {missing}" if missing else "Failed basic structure/value checks (types or predefined values)."

    score += basic_compliance_score
    details['basic_structure_compliance'] = {'score': basic_compliance_score, 'max': 3, 'comment': comment}


    # 3. Correct Ordering within Arrays (3 points)
    ordering_score = 0
    ordering_comments = []

    # Check prioritized_allocation order by assigned_priority
    key_prio_order = [t.get('assigned_priority') for t in key_data.get('prioritized_allocation', []) if t.get('assigned_priority') is not None]
    cand_prio_order = [t.get('assigned_priority') for t in candidate_data.get('prioritized_allocation', []) if t.get('assigned_priority') is not None]
    if key_prio_order == cand_prio_order and key_prio_order == sorted(key_prio_order):
        ordering_score += 1
    else:
         ordering_comments.append("prioritized_allocation not correctly ordered by assigned_priority.")

    # Check unallocated_tasks order by assigned_priority
    key_unalloc_order = [t.get('assigned_priority') for t in key_data.get('unallocated_tasks', []) if t.get('assigned_priority') is not None]
    cand_unalloc_order = [t.get('assigned_priority') for t in candidate_data.get('unallocated_tasks', []) if t.get('assigned_priority') is not None]
    # Need to handle cases where candidate might miss some unallocated tasks but get order right for the ones they have
    cand_unalloc_priorities_present = [p for p in cand_unalloc_order if p in key_unalloc_order]
    expected_order_subset = sorted([p for p in key_unalloc_order if p in cand_unalloc_priorities_present])

    if cand_unalloc_order == expected_order_subset:
         ordering_score += 1
    else:
         ordering_comments.append("unallocated_tasks not correctly ordered by assigned_priority.")


    # Check resource_summary order by resource_id
    key_res_order = [r.get('resource_id') for r in key_data.get('resource_summary', []) if r.get('resource_id')]
    cand_res_order = [r.get('resource_id') for r in candidate_data.get('resource_summary', []) if r.get('resource_id')]
    if key_res_order == cand_res_order and key_res_order == sorted(key_res_order):
        ordering_score += 1
    else:
        ordering_comments.append("resource_summary not correctly ordered by resource_id.")

    score += ordering_score
    details['array_ordering'] = {'score': ordering_score, 'max': 3, 'comment': " ".join(ordering_comments) if ordering_comments else "All arrays correctly ordered."}

    # 4. File Name Check (1 point) - Cannot be reliably checked automatically here. Awarded manually or assumed.
    # We will award this point if the script is run with the expected filename argument.
    # This check is more about process compliance than content.
    # Let's assume the evaluator ran it correctly.
    filename_score = 1
    score += filename_score
    details['file_naming'] = {'score': filename_score, 'max': 1, 'comment': 'Assumed correct filename used based on script execution.'}


    return {'total_score': score, 'max_points': max_points, 'details': details}

def score_prioritization(candidate_data, key_data):
    """Scores the task prioritization."""
    score = 0
    details = {'correctly_prioritized': [], 'incorrectly_prioritized': []}
    max_points = MAX_POINTS_PRIORITIZATION

    key_alloc_tasks = get_task_details(key_data, 'prioritized_allocation')
    key_unalloc_tasks = get_task_details(key_data, 'unallocated_tasks')
    key_all_tasks_prio = {tid: task.get('assigned_priority') for tid, task in key_alloc_tasks.items()}
    key_all_tasks_prio.update({tid: task.get('assigned_priority') for tid, task in key_unalloc_tasks.items()})

    cand_alloc_tasks = get_task_details(candidate_data, 'prioritized_allocation')
    cand_unalloc_tasks = get_task_details(candidate_data, 'unallocated_tasks')
    cand_all_tasks_prio = {tid: task.get('assigned_priority') for tid, task in cand_alloc_tasks.items()}
    cand_all_tasks_prio.update({tid: task.get('assigned_priority') for tid, task in cand_unalloc_tasks.items()})

    total_tasks_in_key = len(key_all_tasks_prio)
    correct_priorities = 0

    if total_tasks_in_key == 0: # Avoid division by zero if key is empty
        return {'total_score': 0, 'max_points': max_points, 'details': {'comment': 'Answer key has no tasks.'}}

    for task_id, key_priority in key_all_tasks_prio.items():
        cand_priority = cand_all_tasks_prio.get(task_id)
        if cand_priority == key_priority:
            correct_priorities += 1
            details['correctly_prioritized'].append(f"{task_id} (Prio: {key_priority})")
        else:
            details['incorrectly_prioritized'].append(f"{task_id} (Expected Prio: {key_priority}, Got: {cand_priority})")

    score = round((correct_priorities / total_tasks_in_key) * max_points)

    details['summary'] = f"Correctly prioritized {correct_priorities} out of {total_tasks_in_key} tasks."
    return {'total_score': score, 'max_points': max_points, 'details': details}


def score_allocation(candidate_data, key_data):
    """Scores the task allocation and unallocated task identification."""
    score = 0
    details = {}
    max_points = MAX_POINTS_ALLOCATION

    key_alloc_tasks = get_task_details(key_data, 'prioritized_allocation')
    key_unalloc_tasks = get_task_details(key_data, 'unallocated_tasks')
    cand_alloc_tasks = get_task_details(candidate_data, 'prioritized_allocation')
    cand_unalloc_tasks = get_task_details(candidate_data, 'unallocated_tasks')

    # 1. Correct Resource Assignment (20 points)
    resource_assignment_score = 0
    max_resource_points = 20
    correct_assignments = 0
    assignment_details = {'correct': [], 'incorrect': []}
    total_key_allocations = len(key_alloc_tasks)

    if total_key_allocations > 0:
        for task_id, key_task in key_alloc_tasks.items():
            key_resource = key_task.get('assigned_resource_id')
            cand_task = cand_alloc_tasks.get(task_id)
            if cand_task:
                cand_resource = cand_task.get('assigned_resource_id')
                if cand_resource == key_resource:
                    correct_assignments += 1
                    assignment_details['correct'].append(f"{task_id} -> {key_resource}")
                else:
                    assignment_details['incorrect'].append(f"{task_id} (Expected: {key_resource}, Got: {cand_resource})")
            else:
                # Candidate didn't allocate a task that should have been allocated
                 assignment_details['incorrect'].append(f"{task_id} (Expected: {key_resource}, Got: Not Allocated/Missing)")

        resource_assignment_score = round((correct_assignments / total_key_allocations) * max_resource_points)
    else:
        assignment_details['comment'] = "No tasks allocated in the answer key."

    score += resource_assignment_score
    details['resource_assignment'] = {'score': resource_assignment_score, 'max': max_resource_points, 'details': assignment_details}

    # 2. Correct Unallocated Identification (10 points)
    unallocated_id_score = 0
    max_unallocated_id_points = 10
    correct_unallocated_ids = 0
    id_details = {'correct': [], 'incorrect': []}
    key_unalloc_ids = set(key_unalloc_tasks.keys())
    cand_unalloc_ids = set(cand_unalloc_tasks.keys())
    total_key_unallocated = len(key_unalloc_ids)

    if total_key_unallocated > 0:
        correctly_identified = key_unalloc_ids.intersection(cand_unalloc_ids)
        missed_unallocated = key_unalloc_ids.difference(cand_unalloc_ids)
        wrongly_marked_unallocated = cand_unalloc_ids.difference(key_unalloc_ids)

        correct_unallocated_ids = len(correctly_identified)
        unallocated_id_score = round((correct_unallocated_ids / total_key_unallocated) * max_unallocated_id_points)

        id_details['correct'] = list(correctly_identified)
        id_details['missed'] = list(missed_unallocated) # Should have been unallocated, but wasn't
        id_details['wrongly_marked'] = list(wrongly_marked_unallocated) # Marked unallocated, but shouldn't have been
    elif not cand_unalloc_ids: # Key has no unallocated, candidate also has none
         unallocated_id_score = max_unallocated_id_points
         id_details['comment'] = "Correctly identified that no tasks should be unallocated."
    else: # Key has no unallocated, but candidate marked some
        id_details['wrongly_marked'] = list(cand_unalloc_ids)
        id_details['comment'] = "Incorrectly marked tasks as unallocated."


    score += unallocated_id_score
    details['unallocated_identification'] = {'score': unallocated_id_score, 'max': max_unallocated_id_points, 'details': id_details}

    # 3. Correct Unallocated Reason (10 points)
    unallocated_reason_score = 0
    max_unallocated_reason_points = 10
    correct_reasons = 0
    reason_details = {'correct': [], 'incorrect': []}
    # Only score reasons for tasks correctly identified as unallocated
    tasks_to_check_reason = key_unalloc_ids.intersection(cand_unalloc_ids)
    num_tasks_for_reason_check = len(tasks_to_check_reason)


    if num_tasks_for_reason_check > 0:
        for task_id in tasks_to_check_reason:
            key_reason = key_unalloc_tasks[task_id].get('reason')
            cand_reason = cand_unalloc_tasks[task_id].get('reason')
            if key_reason == cand_reason:
                correct_reasons += 1
                reason_details['correct'].append(f"{task_id} (Reason: {key_reason})")
            else:
                reason_details['incorrect'].append(f"{task_id} (Expected Reason: {key_reason}, Got: {cand_reason})")
        unallocated_reason_score = round((correct_reasons / num_tasks_for_reason_check) * max_unallocated_reason_points)
    elif total_key_unallocated == 0 and not cand_unalloc_ids: # No unallocated tasks expected or submitted
        unallocated_reason_score = max_unallocated_reason_points # Perfect score if none were expected and none given
        reason_details['comment'] = "No unallocated tasks expected or submitted."
    elif total_key_unallocated > 0 and num_tasks_for_reason_check == 0: # Unallocated tasks expected, but none correctly identified by candidate
        reason_details['comment'] = "No tasks correctly identified as unallocated to check reasons for."
        unallocated_reason_score = 0
    elif total_key_unallocated == 0 and cand_unalloc_ids: # No unallocated tasks expected, but candidate submitted some
         reason_details['comment'] = "Reasons not applicable as tasks were wrongly marked unallocated."
         unallocated_reason_score = 0


    score += unallocated_reason_score
    details['unallocated_reason'] = {'score': unallocated_reason_score, 'max': max_unallocated_reason_points, 'details': reason_details}


    return {'total_score': score, 'max_points': max_points, 'details': details}


def score_resource_summary(candidate_data, key_data):
    """Scores the resource summary section."""
    score = 0
    details = {}
    max_points = MAX_POINTS_RESOURCE_SUMMARY

    key_resources = get_resource_summary_details(key_data)
    cand_resources = get_resource_summary_details(candidate_data)

    # 1. Correct Total Allocated Days (9 points)
    allocated_days_score = 0
    max_allocated_days_points = 9
    correct_days_count = 0
    days_details = {'correct': [], 'incorrect': []}
    total_resources_in_key = len(key_resources)

    if total_resources_in_key > 0:
        points_per_resource_days = max_allocated_days_points / total_resources_in_key
        for res_id, key_res in key_resources.items():
            key_days = key_res.get('total_allocated_days')
            cand_res = cand_resources.get(res_id)
            if cand_res:
                cand_days = cand_res.get('total_allocated_days')
                if isinstance(cand_days, int) and cand_days == key_days:
                    correct_days_count += 1
                    days_details['correct'].append(f"{res_id} (Days: {key_days})")
                else:
                    days_details['incorrect'].append(f"{res_id} (Expected Days: {key_days}, Got: {cand_days})")
            else:
                days_details['incorrect'].append(f"{res_id} (Resource summary missing)")
        allocated_days_score = round(correct_days_count * points_per_resource_days)
    else:
        days_details['comment'] = "No resources found in answer key summary."


    score += allocated_days_score
    details['total_allocated_days'] = {'score': allocated_days_score, 'max': max_allocated_days_points, 'details': days_details}

    # 2. Correct Workload Status (6 points)
    workload_status_score = 0
    max_workload_status_points = 6
    correct_status_count = 0
    status_details = {'correct': [], 'incorrect': []}

    if total_resources_in_key > 0:
        points_per_resource_status = max_workload_status_points / total_resources_in_key
        for res_id, key_res in key_resources.items():
            key_status = key_res.get('workload_status')
            cand_res = cand_resources.get(res_id)
            if cand_res:
                cand_status = cand_res.get('workload_status')
                # Check if candidate status is one of the allowed strings
                allowed_statuses = ["Over-allocated", "Under-allocated", "Within Capacity"]
                if cand_status in allowed_statuses and cand_status == key_status:
                    correct_status_count += 1
                    status_details['correct'].append(f"{res_id} (Status: {key_status})")
                else:
                     status_details['incorrect'].append(f"{res_id} (Expected Status: {key_status}, Got: {cand_status})")
            else:
                # Resource missing in candidate data, already penalized in days check implicitly
                 status_details['incorrect'].append(f"{res_id} (Resource summary missing)")

        workload_status_score = round(correct_status_count * points_per_resource_status)
    else:
        status_details['comment'] = "No resources found in answer key summary."


    score += workload_status_score
    details['workload_status'] = {'score': workload_status_score, 'max': max_workload_status_points, 'details': status_details}

    return {'total_score': score, 'max_points': max_points, 'details': details}

# --- Main Execution ---

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <candidate_submission.json> <answer_key.json>")
        sys.exit(1)

    candidate_file = sys.argv[1]
    key_file = sys.argv[2]
    results_file = "test_results.json"

    print(f"Loading candidate submission from: {candidate_file}")
    candidate_data = load_json(candidate_file)
    print(f"Loading answer key from: {key_file}")
    key_data = load_json(key_file)

    print("Evaluating...")

    # Perform scoring
    formatting_results = score_formatting(candidate_data, key_data)
    prioritization_results = score_prioritization(candidate_data, key_data)
    allocation_results = score_allocation(candidate_data, key_data)
    resource_summary_results = score_resource_summary(candidate_data, key_data)

    # Aggregate results
    total_score = (
        formatting_results['total_score'] +
        prioritization_results['total_score'] +
        allocation_results['total_score'] +
        resource_summary_results['total_score']
    )

    overall_percentage = round((total_score / TOTAL_MAX_POINTS) * 100, 2) if TOTAL_MAX_POINTS > 0 else 0

    final_results = {
        "candidate_file": candidate_file,
        "answer_key_file": key_file,
        "overall_score": overall_percentage,
        "total_score": total_score,
        "max_total_points": TOTAL_MAX_POINTS,
        "scoring_details": {
            "formatting": formatting_results,
            "prioritization": prioritization_results,
            "allocation": allocation_results,
            "resource_summary": resource_summary_results
        }
    }

    # Save results
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=4)
        print(f"Evaluation complete. Results saved to: {results_file}")
        print(f"Overall Score: {overall_percentage}% ({total_score}/{TOTAL_MAX_POINTS} points)")
    except Exception as e:
        print(f"Error writing results file {results_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()