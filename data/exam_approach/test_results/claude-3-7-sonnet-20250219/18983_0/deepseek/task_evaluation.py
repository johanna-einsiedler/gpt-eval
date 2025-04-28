#!/usr/bin/env python3
import json
import sys
import math
from typing import Dict, Any, List, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def evaluate_schedule(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the schedule section (30% of total score)."""
    max_score = 30
    score = 0
    details = {}
    
    # Check project duration (within ±2 days)
    sub_duration = submission.get("schedule", {}).get("project_duration", 0)
    key_duration = answer_key.get("schedule", {}).get("project_duration", 0)
    duration_diff = abs(sub_duration - key_duration)
    
    if duration_diff <= 2:
        score += 10
        details["project_duration"] = {"score": 10, "max": 10, "comment": "Correct project duration"}
    else:
        details["project_duration"] = {
            "score": max(0, 10 - duration_diff),
            "max": 10,
            "comment": f"Project duration off by {duration_diff} days"
        }
        score += max(0, 10 - duration_diff)
    
    # Check critical path (at least 8 of 10 tasks)
    sub_path = submission.get("schedule", {}).get("critical_path", [])
    key_path = answer_key.get("schedule", {}).get("critical_path", [])
    
    correct_tasks = set(sub_path).intersection(set(key_path))
    correct_order = sum(1 for i, task in enumerate(sub_path) if i < len(key_path) and task == key_path[i])
    
    path_score = 0
    if len(correct_tasks) >= 8:
        path_score += 5  # For identifying correct tasks
    else:
        path_score += (len(correct_tasks) / len(key_path)) * 5
    
    if correct_order >= 8:
        path_score += 5  # For correct order
    else:
        path_score += (correct_order / len(key_path)) * 5
    
    score += path_score
    details["critical_path"] = {
        "score": path_score,
        "max": 10,
        "comment": f"Identified {len(correct_tasks)}/{len(key_path)} tasks correctly, with {correct_order} in correct order"
    }
    
    # Check task dates (no more than 3 errors)
    sub_dates = submission.get("schedule", {}).get("task_dates", {})
    key_dates = answer_key.get("schedule", {}).get("task_dates", {})
    
    date_errors = 0
    for task_id, dates in key_dates.items():
        if task_id not in sub_dates:
            date_errors += 1
            continue
            
        sub_earliest = sub_dates[task_id].get("earliest_start", "")
        key_earliest = dates.get("earliest_start", "")
        
        sub_latest = sub_dates[task_id].get("latest_start", "")
        key_latest = dates.get("latest_start", "")
        
        if sub_earliest != key_earliest:
            date_errors += 0.5
            
        if sub_latest != key_latest:
            date_errors += 0.5
    
    date_score = 10 if date_errors <= 3 else max(0, 10 - (date_errors - 3) * 2)
    score += date_score
    
    details["task_dates"] = {
        "score": date_score,
        "max": 10,
        "comment": f"Found {date_errors} errors in task dates"
    }
    
    return (score, details)

def evaluate_budget(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the budget section (30% of total score)."""
    max_score = 30
    score = 0
    details = {}
    
    # Calculate total budget (within ±5%)
    sub_total = submission.get("budget", {}).get("total_budget", 0)
    key_total = answer_key.get("budget", {}).get("total_budget", 0)
    
    total_pct_diff = abs(sub_total - key_total) / key_total * 100 if key_total else 100
    
    if total_pct_diff <= 5:
        score += 10
        details["total_budget"] = {"score": 10, "max": 10, "comment": "Total budget within 5% of correct amount"}
    else:
        total_score = max(0, 10 - (total_pct_diff - 5))
        score += total_score
        details["total_budget"] = {
            "score": total_score,
            "max": 10,
            "comment": f"Total budget off by {total_pct_diff:.2f}%"
        }
    
    # Calculate labor costs (within ±7%)
    sub_labor = submission.get("budget", {}).get("labor_costs", 0)
    key_labor = answer_key.get("budget", {}).get("labor_costs", 0)
    
    labor_pct_diff = abs(sub_labor - key_labor) / key_labor * 100 if key_labor else 100
    
    if labor_pct_diff <= 7:
        score += 7
        details["labor_costs"] = {"score": 7, "max": 7, "comment": "Labor costs within 7% of correct amount"}
    else:
        labor_score = max(0, 7 - (labor_pct_diff - 7) / 2)
        score += labor_score
        details["labor_costs"] = {
            "score": labor_score,
            "max": 7,
            "comment": f"Labor costs off by {labor_pct_diff:.2f}%"
        }
    
    # Calculate equipment costs (within ±3%)
    sub_equip = submission.get("budget", {}).get("equipment_costs", 0)
    key_equip = answer_key.get("budget", {}).get("equipment_costs", 0)
    
    equip_pct_diff = abs(sub_equip - key_equip) / key_equip * 100 if key_equip else 100
    
    if equip_pct_diff <= 3:
        score += 7
        details["equipment_costs"] = {"score": 7, "max": 7, "comment": "Equipment costs within 3% of correct amount"}
    else:
        equip_score = max(0, 7 - (equip_pct_diff - 3))
        score += equip_score
        details["equipment_costs"] = {
            "score": equip_score,
            "max": 7,
            "comment": f"Equipment costs off by {equip_pct_diff:.2f}%"
        }
    
    # Phase allocations (directionally correct)
    sub_phases = submission.get("budget", {}).get("phase_allocation", {})
    key_phases = answer_key.get("budget", {}).get("phase_allocation", {})
    
    # Check if Phase 2 has the largest allocation
    phase_score = 0
    
    if len(sub_phases) >= 3:
        sub_phase_values = list(sub_phases.values())
        if sub_phase_values.index(max(sub_phase_values)) == 1:  # Phase 2 should be largest
            phase_score += 3
            details["phase_allocation"] = {"score": 6, "max": 6, "comment": "Phase allocations directionally correct"}
        else:
            details["phase_allocation"] = {
                "score": 3,
                "max": 6,
                "comment": "Phase 2 not identified as largest allocation"
            }
            phase_score += 3
    else:
        details["phase_allocation"] = {
            "score": 0,
            "max": 6,
            "comment": "Missing phase allocations"
        }
    
    # Check if allocations are within reasonable range
    if phase_score > 0:
        reasonable_allocations = True
        for phase, key_amount in key_phases.items():
            if phase in sub_phases:
                sub_amount = sub_phases[phase]
                if abs(sub_amount - key_amount) / key_amount > 0.15:  # More than 15% off
                    reasonable_allocations = False
                    break
        
        if reasonable_allocations:
            phase_score += 3
            details["phase_allocation"]["score"] = phase_score
            details["phase_allocation"]["comment"] = "Phase allocations directionally correct and within reasonable range"
    
    score += phase_score
    
    return (score, details)

def evaluate_cost_control(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the cost control section (20% of total score)."""
    max_score = 20
    score = 0
    details = {}
    
    # Check variance thresholds
    sub_thresholds = submission.get("cost_control", {}).get("variance_thresholds", {})
    key_thresholds = answer_key.get("cost_control", {}).get("variance_thresholds", {})
    
    threshold_score = 0
    
    # Check CV percentage
    sub_cv = sub_thresholds.get("acceptable_cv_percentage", 0)
    key_cv = key_thresholds.get("acceptable_cv_percentage", 0)
    
    if abs(sub_cv - key_cv) <= 1:  # Within 1 percentage point
        threshold_score += 4
    else:
        threshold_score += max(0, 4 - abs(sub_cv - key_cv))
    
    # Check SV percentage
    sub_sv = sub_thresholds.get("acceptable_sv_percentage", 0)
    key_sv = key_thresholds.get("acceptable_sv_percentage", 0)
    
    if abs(sub_sv - key_sv) <= 1:  # Within 1 percentage point
        threshold_score += 4
    else:
        threshold_score += max(0, 4 - abs(sub_sv - key_sv))
    
    # Check corrective action trigger
    sub_trigger = sub_thresholds.get("corrective_action_trigger", "")
    key_trigger = key_thresholds.get("corrective_action_trigger", "")
    
    if "consecutive" in sub_trigger.lower() and "2" in sub_trigger:
        threshold_score += 2
    
    score += threshold_score
    details["variance_thresholds"] = {
        "score": threshold_score,
        "max": 10,
        "comment": f"Variance thresholds identified with {10-threshold_score} points deducted"
    }
    
    # Check planned value at milestones
    sub_pv = submission.get("cost_control", {}).get("planned_value", {})
    key_pv = answer_key.get("cost_control", {}).get("planned_value", {})
    
    pv_errors = 0
    for milestone, key_value in key_pv.items():
        if milestone in sub_pv:
            sub_value = sub_pv[milestone]
            pct_diff = abs(sub_value - key_value) / key_value * 100 if key_value else 100
            if pct_diff > 5:
                pv_errors += 1
    
    pv_score = 10 - (pv_errors * 2.5)
    pv_score = max(0, pv_score)
    
    score += pv_score
    details["planned_value"] = {
        "score": pv_score,
        "max": 10,
        "comment": f"Planned value calculations had {pv_errors} significant errors"
    }
    
    return (score, details)

def evaluate_variance_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the variance analysis section (20% of total score)."""
    max_score = 20
    score = 0
    details = {}
    
    # Check SV and CV (within ±$2,000)
    sub_sv = submission.get("variance_analysis", {}).get("schedule_variance", 0)
    key_sv = answer_key.get("variance_analysis", {}).get("schedule_variance", 0)
    
    sub_cv = submission.get("variance_analysis", {}).get("cost_variance", 0)
    key_cv = answer_key.get("variance_analysis", {}).get("cost_variance", 0)
    
    sv_diff = abs(sub_sv - key_sv)
    cv_diff = abs(sub_cv - key_cv)
    
    variance_score = 0
    if sv_diff <= 2000:
        variance_score += 4
    else:
        variance_score += max(0, 4 - (sv_diff - 2000) / 1000)
    
    if cv_diff <= 2000:
        variance_score += 4
    else:
        variance_score += max(0, 4 - (cv_diff - 2000) / 1000)
    
    score += variance_score
    details["sv_cv"] = {
        "score": variance_score,
        "max": 8,
        "comment": f"SV off by ${sv_diff:.2f}, CV off by ${cv_diff:.2f}"
    }
    
    # Check SPI and CPI (within ±0.05)
    sub_spi = submission.get("variance_analysis", {}).get("spi", 0)
    key_spi = answer_key.get("variance_analysis", {}).get("spi", 0)
    
    sub_cpi = submission.get("variance_analysis", {}).get("cpi", 0)
    key_cpi = answer_key.get("variance_analysis", {}).get("cpi", 0)
    
    spi_diff = abs(sub_spi - key_spi)
    cpi_diff = abs(sub_cpi - key_cpi)
    
    index_score = 0
    if spi_diff <= 0.05:
        index_score += 3
    else:
        index_score += max(0, 3 - (spi_diff - 0.05) * 10)
    
    if cpi_diff <= 0.05:
        index_score += 3
    else:
        index_score += max(0, 3 - (cpi_diff - 0.05) * 10)
    
    score += index_score
    details["spi_cpi"] = {
        "score": index_score,
        "max": 6,
        "comment": f"SPI off by {spi_diff:.3f}, CPI off by {cpi_diff:.3f}"
    }
    
    # Check EAC (within ±7%)
    sub_eac = submission.get("variance_analysis", {}).get("eac", 0)
    key_eac = answer_key.get("variance_analysis", {}).get("eac", 0)
    
    eac_pct_diff = abs(sub_eac - key_eac) / key_eac * 100 if key_eac else 100
    
    if eac_pct_diff <= 7:
        eac_score = 6
    else:
        eac_score = max(0, 6 - (eac_pct_diff - 7) / 2)
    
    score += eac_score
    details["eac"] = {
        "score": eac_score,
        "max": 6,
        "comment": f"EAC off by {eac_pct_diff:.2f}%"
    }
    
    return (score, details)

def check_section_minimum(section_score: float, section_max: float, min_percentage: float = 60) -> bool:
    """Check if a section meets the minimum required percentage."""
    return (section_score / section_max * 100) >= min_percentage

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each section
    schedule_score, schedule_details = evaluate_schedule(submission, answer_key)
    budget_score, budget_details = evaluate_budget(submission, answer_key)
    cost_control_score, cost_control_details = evaluate_cost_control(submission, answer_key)
    variance_score, variance_details = evaluate_variance_analysis(submission, answer_key)
    
    # Calculate overall score
    total_score = schedule_score + budget_score + cost_control_score + variance_score
    total_possible = 30 + 30 + 20 + 20  # 100 points total
    overall_percentage = (total_score / total_possible) * 100
    
    # Check if each section meets minimum requirements
    sections_passed = {
        "schedule": check_section_minimum(schedule_score, 30),
        "budget": check_section_minimum(budget_score, 30),
        "cost_control": check_section_minimum(cost_control_score, 20),
        "variance_analysis": check_section_minimum(variance_score, 20)
    }
    
    # Determine if candidate passed overall
    passed_overall = overall_percentage >= 70 and all(sections_passed.values())
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 2),
        "passed": passed_overall,
        "section_scores": {
            "schedule": {
                "score": round(schedule_score, 2),
                "max": 30,
                "percentage": round((schedule_score / 30) * 100, 2),
                "passed_minimum": sections_passed["schedule"],
                "details": schedule_details
            },
            "budget": {
                "score": round(budget_score, 2),
                "max": 30,
                "percentage": round((budget_score / 30) * 100, 2),
                "passed_minimum": sections_passed["budget"],
                "details": budget_details
            },
            "cost_control": {
                "score": round(cost_control_score, 2),
                "max": 20,
                "percentage": round((cost_control_score / 20) * 100, 2),
                "passed_minimum": sections_passed["cost_control"],
                "details": cost_control_details
            },
            "variance_analysis": {
                "score": round(variance_score, 2),
                "max": 20,
                "percentage": round((variance_score / 20) * 100, 2),
                "passed_minimum": sections_passed["variance_analysis"],
                "details": variance_details
            }
        },
        "feedback": "The candidate has " + ("passed" if passed_overall else "failed") + " the exam."
    }
    
    # If any section failed, add specific feedback
    if not passed_overall:
        failed_sections = [section for section, passed in sections_passed.items() if not passed]
        if failed_sections:
            results["feedback"] += f" The following sections did not meet the minimum 60% requirement: {', '.join(failed_sections)}."
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    print(f"Result: {'PASS' if passed_overall else 'FAIL'}")

if __name__ == "__main__":
    main()