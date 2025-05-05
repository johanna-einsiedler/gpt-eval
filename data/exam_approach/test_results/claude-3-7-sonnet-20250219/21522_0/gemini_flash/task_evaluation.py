import json
import sys
import math

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def is_within_percentage(candidate_value, correct_value, percentage):
    """Check if candidate value is within given percentage of correct value"""
    if correct_value == 0:
        return candidate_value == 0
    
    difference = abs(candidate_value - correct_value)
    return (difference / abs(correct_value)) <= (percentage / 100)

def calculate_partial_credit(candidate_value, correct_value, points):
    """Calculate partial credit based on how close the answer is"""
    if candidate_value == correct_value:
        return points
    elif is_within_percentage(candidate_value, correct_value, 1):
        return points * 0.9
    elif is_within_percentage(candidate_value, correct_value, 5):
        return points * 0.7
    elif is_within_percentage(candidate_value, correct_value, 10):
        return points * 0.5
    else:
        return points * 0.3  # Assuming some work was shown in spreadsheet

def evaluate_task1(candidate, answer_key):
    results = {"points_possible": 15, "points_earned": 0, "details": {}}
    
    # Total annual interest (5 points)
    total_interest_points = 5
    candidate_total = candidate["task1"]["total_annual_interest"]
    correct_total = answer_key["task1"]["total_annual_interest"]
    earned = calculate_partial_credit(candidate_total, correct_total, total_interest_points)
    results["points_earned"] += earned
    results["details"]["total_annual_interest"] = {
        "points_possible": total_interest_points,
        "points_earned": earned,
        "candidate_answer": candidate_total,
        "correct_answer": correct_total
    }
    
    # Taxable interest income (5 points)
    taxable_interest_points = 5
    candidate_taxable = candidate["task1"]["taxable_interest_income"]
    correct_taxable = answer_key["task1"]["taxable_interest_income"]
    earned = calculate_partial_credit(candidate_taxable, correct_taxable, taxable_interest_points)
    results["points_earned"] += earned
    results["details"]["taxable_interest_income"] = {
        "points_possible": taxable_interest_points,
        "points_earned": earned,
        "candidate_answer": candidate_taxable,
        "correct_answer": correct_taxable
    }
    
    # Effective yields (5 points total, split across 3 investments)
    yields_points = 5
    points_per_yield = yields_points / 3
    
    yields_earned = 0
    yields_details = {}
    
    for investment in ["corporate_bond", "certificate_of_deposit", "municipal_bond"]:
        candidate_yield = candidate["task1"]["effective_yields"][investment]
        correct_yield = answer_key["task1"]["effective_yields"][investment]
        earned = calculate_partial_credit(candidate_yield, correct_yield, points_per_yield)
        yields_earned += earned
        yields_details[investment] = {
            "points_possible": points_per_yield,
            "points_earned": earned,
            "candidate_answer": candidate_yield,
            "correct_answer": correct_yield
        }
    
    results["points_earned"] += yields_earned
    results["details"]["effective_yields"] = {
        "points_possible": yields_points,
        "points_earned": yields_earned,
        "details": yields_details
    }
    
    return results

def evaluate_task2(candidate, answer_key):
    results = {"points_possible": 20, "points_earned": 0, "details": {}}
    
    # Fair market value (6 points)
    fmv_points = 6
    candidate_fmv = candidate["task2"]["fair_market_value"]
    correct_fmv = answer_key["task2"]["fair_market_value"]
    earned = calculate_partial_credit(candidate_fmv, correct_fmv, fmv_points)
    results["points_earned"] += earned
    results["details"]["fair_market_value"] = {
        "points_possible": fmv_points,
        "points_earned": earned,
        "candidate_answer": candidate_fmv,
        "correct_answer": correct_fmv
    }
    
    # Annual taxable interest (4 points)
    interest_points = 4
    candidate_interest = candidate["task2"]["annual_taxable_interest"]
    correct_interest = answer_key["task2"]["annual_taxable_interest"]
    earned = calculate_partial_credit(candidate_interest, correct_interest, interest_points)
    results["points_earned"] += earned
    results["details"]["annual_taxable_interest"] = {
        "points_possible": interest_points,
        "points_earned": earned,
        "candidate_answer": candidate_interest,
        "correct_answer": correct_interest
    }
    
    # Amortizable amount (4 points)
    amort_points = 4
    candidate_amort = candidate["task2"]["amortizable_amount"]
    correct_amort = answer_key["task2"]["amortizable_amount"]
    earned = calculate_partial_credit(candidate_amort, correct_amort, amort_points)
    results["points_earned"] += earned
    results["details"]["amortizable_amount"] = {
        "points_possible": amort_points,
        "points_earned": earned,
        "candidate_answer": candidate_amort,
        "correct_answer": correct_amort
    }
    
    # Adjusted tax basis (6 points)
    basis_points = 6
    candidate_basis = candidate["task2"]["adjusted_tax_basis"]
    correct_basis = answer_key["task2"]["adjusted_tax_basis"]
    earned = calculate_partial_credit(candidate_basis, correct_basis, basis_points)
    results["points_earned"] += earned
    results["details"]["adjusted_tax_basis"] = {
        "points_possible": basis_points,
        "points_earned": earned,
        "candidate_answer": candidate_basis,
        "correct_answer": correct_basis
    }
    
    return results

def evaluate_task3(candidate, answer_key):
    results = {"points_possible": 20, "points_earned": 0, "details": {}}
    
    # Present value of annuity (5 points)
    pv_points = 5
    candidate_pv = candidate["task3"]["present_value_annuity"]
    correct_pv = answer_key["task3"]["present_value_annuity"]
    earned = calculate_partial_credit(candidate_pv, correct_pv, pv_points)
    results["points_earned"] += earned
    results["details"]["present_value_annuity"] = {
        "points_possible": pv_points,
        "points_earned": earned,
        "candidate_answer": candidate_pv,
        "correct_answer": correct_pv
    }
    
    # Better economic value (3 points)
    value_points = 3
    candidate_value = candidate["task3"]["better_economic_value"]
    correct_value = answer_key["task3"]["better_economic_value"]
    earned = value_points if candidate_value == correct_value else 0
    results["points_earned"] += earned
    results["details"]["better_economic_value"] = {
        "points_possible": value_points,
        "points_earned": earned,
        "candidate_answer": candidate_value,
        "correct_answer": correct_value
    }
    
    # Tax liability (6 points)
    tax_points = 6
    tax_earned = 0
    tax_details = {}
    
    # Lump sum tax (3 points)
    lump_points = tax_points / 2
    candidate_lump = candidate["task3"]["tax_liability"]["lump_sum"]
    correct_lump = answer_key["task3"]["tax_liability"]["lump_sum"]
    lump_earned = calculate_partial_credit(candidate_lump, correct_lump, lump_points)
    tax_earned += lump_earned
    tax_details["lump_sum"] = {
        "points_possible": lump_points,
        "points_earned": lump_earned,
        "candidate_answer": candidate_lump,
        "correct_answer": correct_lump
    }
    
    # Annuity tax (3 points)
    annuity_points = tax_points / 2
    candidate_annuity = candidate["task3"]["tax_liability"]["annuity_total_present_value"]
    correct_annuity = answer_key["task3"]["tax_liability"]["annuity_total_present_value"]
    annuity_earned = calculate_partial_credit(candidate_annuity, correct_annuity, annuity_points)
    tax_earned += annuity_earned
    tax_details["annuity_total_present_value"] = {
        "points_possible": annuity_points,
        "points_earned": annuity_earned,
        "candidate_answer": candidate_annuity,
        "correct_answer": correct_annuity
    }
    
    results["points_earned"] += tax_earned
    results["details"]["tax_liability"] = {
        "points_possible": tax_points,
        "points_earned": tax_earned,
        "details": tax_details
    }
    
    # After-tax present value (6 points)
    after_tax_points = 6
    after_tax_earned = 0
    after_tax_details = {}
    
    # Lump sum after-tax (3 points)
    lump_at_points = after_tax_points / 2
    candidate_lump_at = candidate["task3"]["after_tax_present_value"]["lump_sum"]
    correct_lump_at = answer_key["task3"]["after_tax_present_value"]["lump_sum"]
    lump_at_earned = calculate_partial_credit(candidate_lump_at, correct_lump_at, lump_at_points)
    after_tax_earned += lump_at_earned
    after_tax_details["lump_sum"] = {
        "points_possible": lump_at_points,
        "points_earned": lump_at_earned,
        "candidate_answer": candidate_lump_at,
        "correct_answer": correct_lump_at
    }
    
    # Annuity after-tax (3 points)
    annuity_at_points = after_tax_points / 2
    candidate_annuity_at = candidate["task3"]["after_tax_present_value"]["annuity"]
    correct_annuity_at = answer_key["task3"]["after_tax_present_value"]["annuity"]
    annuity_at_earned = calculate_partial_credit(candidate_annuity_at, correct_annuity_at, annuity_at_points)
    after_tax_earned += annuity_at_earned
    after_tax_details["annuity"] = {
        "points_possible": annuity_at_points,
        "points_earned": annuity_at_earned,
        "candidate_answer": candidate_annuity_at,
        "correct_answer": correct_annuity_at
    }
    
    results["points_earned"] += after_tax_earned
    results["details"]["after_tax_present_value"] = {
        "points_possible": after_tax_points,
        "points_earned": after_tax_earned,
        "details": after_tax_details
    }
    
    return results

def evaluate_task4(candidate, answer_key):
    results = {"points_possible": 20, "points_earned": 0, "details": {}}
    
    # Cost basis (5 points)
    basis_points = 5
    candidate_basis = candidate["task4"]["cost_basis"]
    correct_basis = answer_key["task4"]["cost_basis"]
    earned = calculate_partial_credit(candidate_basis, correct_basis, basis_points)
    results["points_earned"] += earned
    results["details"]["cost_basis"] = {
        "points_possible": basis_points,
        "points_earned": earned,
        "candidate_answer": candidate_basis,
        "correct_answer": correct_basis
    }
    
    # Capital gain/loss (5 points)
    gain_points = 5
    candidate_gain = candidate["task4"]["capital_gain_loss"]
    correct_gain = answer_key["task4"]["capital_gain_loss"]
    earned = calculate_partial_credit(candidate_gain, correct_gain, gain_points)
    results["points_earned"] += earned
    results["details"]["capital_gain_loss"] = {
        "points_possible": gain_points,
        "points_earned": earned,
        "candidate_answer": candidate_gain,
        "correct_answer": correct_gain
    }
    
    # Dividend income (4 points)
    dividend_points = 4
    candidate_dividend = candidate["task4"]["dividend_income"]
    correct_dividend = answer_key["task4"]["dividend_income"]
    earned = calculate_partial_credit(candidate_dividend, correct_dividend, dividend_points)
    results["points_earned"] += earned
    results["details"]["dividend_income"] = {
        "points_possible": dividend_points,
        "points_earned": earned,
        "candidate_answer": candidate_dividend,
        "correct_answer": correct_dividend
    }
    
    # Total tax liability (6 points)
    tax_points = 6
    candidate_tax = candidate["task4"]["total_tax_liability"]
    correct_tax = answer_key["task4"]["total_tax_liability"]
    earned = calculate_partial_credit(candidate_tax, correct_tax, tax_points)
    results["points_earned"] += earned
    results["details"]["total_tax_liability"] = {
        "points_possible": tax_points,
        "points_earned": earned,
        "candidate_answer": candidate_tax,
        "correct_answer": correct_tax
    }
    
    return results

def evaluate_task5(candidate, answer_key):
    results = {"points_possible": 25, "points_earned": 0, "details": {}}
    
    # Cost depletion (5 points)
    cost_points = 5
    candidate_cost = candidate["task5"]["cost_depletion"]
    correct_cost = answer_key["task5"]["cost_depletion"]
    earned = calculate_partial_credit(candidate_cost, correct_cost, cost_points)
    results["points_earned"] += earned
    results["details"]["cost_depletion"] = {
        "points_possible": cost_points,
        "points_earned": earned,
        "candidate_answer": candidate_cost,
        "correct_answer": correct_cost
    }
    
    # Percentage depletion (5 points)
    pct_points = 5
    candidate_pct = candidate["task5"]["percentage_depletion"]
    correct_pct = answer_key["task5"]["percentage_depletion"]
    earned = calculate_partial_credit(candidate_pct, correct_pct, pct_points)
    results["points_earned"] += earned
    results["details"]["percentage_depletion"] = {
        "points_possible": pct_points,
        "points_earned": earned,
        "candidate_answer": candidate_pct,
        "correct_answer": correct_pct
    }
    
    # Maximum depletion deduction (5 points)
    max_points = 5
    candidate_max = candidate["task5"]["maximum_depletion_deduction"]
    correct_max = answer_key["task5"]["maximum_depletion_deduction"]
    earned = calculate_partial_credit(candidate_max, correct_max, max_points)
    results["points_earned"] += earned
    results["details"]["maximum_depletion_deduction"] = {
        "points_possible": max_points,
        "points_earned": earned,
        "candidate_answer": candidate_max,
        "correct_answer": correct_max
    }
    
    # Adjusted basis (5 points)
    basis_points = 5
    candidate_basis = candidate["task5"]["adjusted_basis"]
    correct_basis = answer_key["task5"]["adjusted_basis"]
    earned = calculate_partial_credit(candidate_basis, correct_basis, basis_points)
    results["points_earned"] += earned
    results["details"]["adjusted_basis"] = {
        "points_possible": basis_points,
        "points_earned": earned,
        "candidate_answer": candidate_basis,
        "correct_answer": correct_basis
    }
    
    # Taxable income (5 points)
    income_points = 5
    candidate_income = candidate["task5"]["taxable_income"]
    correct_income = answer_key["task5"]["taxable_income"]
    earned = calculate_partial_credit(candidate_income, correct_income, income_points)
    results["points_earned"] += earned
    results["details"]["taxable_income"] = {
        "points_possible": income_points,
        "points_earned": earned,
        "candidate_answer": candidate_income,
        "correct_answer": correct_income
    }
    
    return results

def evaluate_submission(candidate, answer_key):
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "total_points_possible": 100,
        "total_points_earned": 0,
        "tasks": {}
    }
    
    # Evaluate each task
    task_evaluators = {
        "task1": evaluate_task1,
        "task2": evaluate_task2,
        "task3": evaluate_task3,
        "task4": evaluate_task4,
        "task5": evaluate_task5
    }
    
    for task_name, evaluator in task_evaluators.items():
        task_results = evaluator(candidate, answer_key)
        results["tasks"][task_name] = task_results
        results["total_points_earned"] += task_results["points_earned"]
    
    # Calculate overall score as a percentage
    results["overall_score"] = (results["total_points_earned"] / results["total_points_possible"]) * 100
    
    # Determine if the candidate passed
    results["passed"] = results["overall_score"] >= 70
    
    # Determine performance level
    if results["overall_score"] >= 85:
        results["performance"] = "Excellent"
    elif results["overall_score"] >= 70:
        results["performance"] = "Satisfactory"
    else:
        results["performance"] = "Needs Improvement"
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(candidate, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Performance: {results['performance']}")

if __name__ == "__main__":
    main()