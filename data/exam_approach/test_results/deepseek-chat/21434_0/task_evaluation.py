import json
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the current directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return None

def calculate_categorization_score(submission, answer_key):
    max_score = 0
    earned_score = 0
    
    # Check each category
    for category in ["settled_claims", "open_claims", "claims_requiring_analysis"]:
        correct_answers = set(answer_key["correct_answers"][category])
        submitted_answers = set(submission.get(category, []))
        
        # Calculate correct matches
        correct_matches = correct_answers.intersection(submitted_answers)
        incorrect_matches = submitted_answers.difference(correct_answers)
        
        # Partial credit for each correct match
        category_max = len(correct_answers)
        category_earned = len(correct_matches)
        
        # Penalize incorrect classifications
        if len(incorrect_matches) > 1:
            category_earned = max(0, category_earned - len(incorrect_matches))
        
        max_score += category_max
        earned_score += category_earned
    
    return (earned_score / max_score) * 100 if max_score > 0 else 0

def calculate_data_issues_score(submission, answer_key):
    required_issues = {
        'E500': ['settlement amount', 'missing'],
        'F600': ['investigation', 'resolution date'],
        'G700': ['resolution date', 'missing']
    }
    
    correct_count = 0
    submitted_records = submission.get("incomplete_records", [])
    
    # Check each required issue
    for claim_id, keywords in required_issues.items():
        found = False
        for record in submitted_records:
            if record["Claim_ID"] == claim_id:
                issue_text = record["Issue"].lower()
                if all(keyword.lower() in issue_text for keyword in keywords):
                    correct_count += 1
                    found = True
                    break
        if not found:
            # Check if alternative description is acceptable
            for alt_desc in answer_key["alternative_acceptable_answers"]["issue_descriptions"]:
                if all(keyword.lower() in alt_desc.lower() for keyword in keywords):
                    correct_count += 1
                    break
    
    return (correct_count / len(required_issues)) * 100

def calculate_calculation_score(submission, answer_key):
    score = 0
    correct_summary = answer_key["correct_answers"]["settlement_summary"]
    submitted_summary = submission.get("settlement_summary", {})
    
    # Check total settled amount
    correct_amount = correct_summary["total_settled_amount"]
    submitted_amount = submitted_summary.get("total_settled_amount", 0)
    if abs(submitted_amount - correct_amount) <= 500:
        score += 50
    
    # Check average settlement days
    correct_days = correct_summary["average_settlement_days"]
    submitted_days = submitted_summary.get("average_settlement_days", 0)
    if abs(submitted_days - correct_days) <= 5:
        score += 50
    
    return score

def evaluate_submission():
    # Load files
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')
    
    if not submission or not answer_key:
        return
    
    # Calculate scores for each section
    categorization_score = calculate_categorization_score(submission, answer_key)
    data_issues_score = calculate_data_issues_score(submission, answer_key)
    calculation_score = calculate_calculation_score(submission, answer_key)
    
    # Calculate overall weighted score
    overall_score = round((
        0.6 * categorization_score + 
        0.2 * data_issues_score + 
        0.2 * calculation_score
    ), 2)
    
    # Prepare results
    results = {
        "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "section_scores": {
            "claim_categorization": categorization_score,
            "data_issues_identification": data_issues_score,
            "settlement_calculations": calculation_score
        },
        "overall_score": overall_score,
        "pass_status": "Pass" if overall_score >= 75 else "Fail",
        "detailed_feedback": {
            "claim_categorization": f"Correctly categorized {round(categorization_score)}% of claims",
            "data_issues": f"Identified {round(data_issues_score)}% of data issues correctly",
            "calculations": f"Scored {round(calculation_score)}% on settlement calculations"
        }
    }
    
    # Save results
    with open('test_results.json', 'w') as outfile:
        json.dump(results, outfile, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    evaluate_submission()