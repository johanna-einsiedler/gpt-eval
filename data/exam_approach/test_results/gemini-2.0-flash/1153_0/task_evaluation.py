import json

def load_data(submission_file, answer_key_file):
    """Loads submission and answer key JSON files."""
    with open(submission_file, 'r') as f:
        submission = json.load(f)
    with open(answer_key_file, 'r') as f:
        answer_key = json.load(f)
    return submission, answer_key

def get_data_from_files():
    """Reads data from the provided xlsx files (simulated as CSV content)."""
    sales_data_csv = """Item Name,Quantity Sold
Black Pens,250
Blue Pens,100
Red Pens,50
A4 Paper,120
Stapler,15
Sticky Notes,80
Printer Paper,90
Paper Clips,60
Envelopes,70
Highlighters,40
File Folders,55
Scissors,20
Tape,30
Ruler,10
Calculator,5
Desk Organizer,25
Whiteboard Markers,35
Correction Tape,45
Staple Remover,12
Puncher,8"""

    inventory_data_csv = """Item Name,Current Stock Level
Black Pens,30
Blue Pens,80
Red Pens,60
A4 Paper,25
Stapler,150
Sticky Notes,50
Printer Paper,70
Paper Clips,100
Envelopes,120
Highlighters,70
File Folders,80
Scissors,40
Tape,60
Ruler,30
Calculator,20
Desk Organizer,40
Whiteboard Markers,60
Correction Tape,75
Staple Remover,35
Puncher,25"""

    sales_data = {}
    for line in sales_data_csv.strip().split('\n')[1:]:
        item, quantity_sold = line.split(',')
        sales_data[item] = int(quantity_sold)

    inventory_data = {}
    for line in inventory_data_csv.strip().split('\n')[1:]:
        item, current_stock = line.split(',')
        inventory_data[item] = int(current_stock)

    return sales_data, inventory_data

def evaluate_identified_issues(submission, answer_key, sales_data, inventory_data):
    """Evaluates the 'identified_supply_issues' section."""
    score = 0
    results = []
    expected_critical_items = ["Black Pens", "A4 Paper"]
    submitted_items = [issue['item_name'] for issue in submission['identified_supply_issues']]

    for issue in submission['identified_supply_issues']:
        item_name = issue['item_name']
        reasoning = issue['reasoning'].lower()
        item_score = 0

        if item_name in expected_critical_items:
            item_score += 1  # 1 point for identifying critical item

        if any(keyword in reasoning for keyword in ["sales", "demand", "sold", "volume", "inventory", "stock", "feedback", "employee"]):
            item_score += 1 # 1 point for mentioning relevant keywords in reasoning

        results.append({"item_name": item_name, "score": item_score, "possible_score": 2})
        score += item_score

    return score, results

def evaluate_purchasing_plan(submission, answer_key, sales_data, inventory_data):
    """Evaluates the 'purchasing_plan' section."""
    score = 0
    results = []

    for item_plan in submission['purchasing_plan']['item_plans']:
        item_name = item_plan['item_name']
        target_level = item_plan['target_inventory_level']
        reorder_point = item_plan['reorder_point']
        target_level_reasoning = item_plan['target_level_reasoning'].lower()
        reorder_point_reasoning = item_plan['reorder_point_reasoning'].lower()

        item_score = 0
        possible_score = 4 # 2 for target level and reasoning, 2 for reorder point and reasoning

        if isinstance(target_level, int) and target_level > inventory_data.get(item_name, 0):
            item_score += 1 # 1 point for target level > current stock
        if any(keyword in target_level_reasoning for keyword in ["sales", "demand", "stock", "safety", "month", "buffer"]):
            item_score += 1 # 1 point for target level reasoning keywords

        if isinstance(reorder_point, int) and reorder_point < target_level:
            item_score += 1 # 1 point for reorder point < target level
        if any(keyword in reorder_point_reasoning for keyword in ["sales", "demand", "lead time", "restock", "weekly", "reorder"]):
            item_score += 1 # 1 point for reorder point reasoning keywords

        results.append({"item_name": item_name, "score": item_score, "possible_score": possible_score})
        score += item_score

    review_frequency_score = 0
    possible_review_frequency_score = 1
    if submission['purchasing_plan']['review_frequency'].lower() in ["monthly", "quarterly", "weekly", "bi-weekly"]:
        review_frequency_score = 1

    return score + review_frequency_score, results, possible_review_frequency_score

def evaluate_submission(submission_file, answer_key_file):
    """Evaluates the entire submission and returns scores."""
    submission, answer_key = load_data(submission_file, answer_key_file)
    sales_data, inventory_data = get_data_from_files()

    identified_issues_score, identified_issues_results = evaluate_identified_issues(submission, answer_key, sales_data, inventory_data)
    purchasing_plan_score, purchasing_plan_results, possible_review_frequency_score = evaluate_purchasing_plan(submission, answer_key, sales_data, inventory_data)

    max_identified_issues_score = 3 * 2 # 3 items, max 2 points each
    max_purchasing_plan_score = 3 * 4 + possible_review_frequency_score # 3 items, max 4 points each + 1 for review frequency
    total_possible_score = max_identified_issues_score + max_purchasing_plan_score

    overall_score_percentage = ( (identified_issues_score + purchasing_plan_score) / total_possible_score) * 100 if total_possible_score > 0 else 0

    results = {
        "candidate_id": submission.get("candidate_id", "N/A"),
        "model_version": submission.get("model_version", "N/A"),
        "data_analysis_summary": {"score": "Manual Review Required", "possible_score": 2}, # Placeholder for manual review
        "identified_supply_issues": {"score": identified_issues_score, "possible_score": max_identified_issues_score, "details": identified_issues_results},
        "purchasing_plan": {"score": purchasing_plan_score, "possible_score": max_purchasing_plan_score, "details": purchasing_plan_results, "review_frequency_possible_score": possible_review_frequency_score},
        "employee_access_strategy": {"score": "Manual Review Required", "possible_score": 2}, # Placeholder for manual review
        "overall_score": round(overall_score_percentage, 2)
    }
    return results

if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    evaluation_results = evaluate_submission(submission_file, answer_key_file)

    with open("test_results.json", 'w') as outfile:
        json.dump(evaluation_results, outfile, indent=4)

    print("Evaluation completed. Results saved to test_results.json")