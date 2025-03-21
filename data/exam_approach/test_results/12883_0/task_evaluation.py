import json
import re
from typing import Dict, List, Union, Any

def load_json(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        exit(1)

def save_json(data: Dict, file_path: str) -> None:
    """Save data as JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def evaluate_single_choice(submission: str, answer_key: str) -> bool:
    """Evaluate a single choice answer."""
    return submission.lower() == answer_key.lower()

def evaluate_text_similarity(submission: str, answer_key: str) -> float:
    """
    Evaluate the similarity of text answers.
    Returns a score between 0 and 1.
    """
    # Convert to lowercase and remove punctuation for comparison
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return set(text.split())
    
    # If the answer key is very short, do a more strict comparison
    if len(answer_key) < 20:
        return 1.0 if submission.lower() == answer_key.lower() else 0.0
    
    sub_words = normalize(submission)
    key_words = normalize(answer_key)
    
    # Calculate Jaccard similarity
    if not sub_words or not key_words:
        return 0.0
    
    intersection = len(sub_words.intersection(key_words))
    union = len(sub_words.union(key_words))
    
    return intersection / union if union > 0 else 0.0

def evaluate_list_match(submission: List, answer_key: List) -> float:
    """Evaluate matching between two lists."""
    if not submission or not answer_key:
        return 0.0
    
    # Convert all elements to lowercase strings for comparison
    sub_list = [str(item).lower() for item in submission]
    key_list = [str(item).lower() for item in answer_key]
    
    # Count correct matches
    matches = sum(1 for item in sub_list if item in key_list)
    
    # Calculate percentage of correct matches
    return matches / len(key_list)

def evaluate_numeric(submission: Union[int, float], answer_key: Union[int, float], 
                    tolerance: float = 0.005) -> float:
    """
    Evaluate numeric answers with a tolerance for rounding.
    Returns 1.0 if within tolerance, 0.0 otherwise.
    """
    try:
        submission_val = float(submission)
        answer_key_val = float(answer_key)
        
        # Check if within tolerance
        if abs(submission_val - answer_key_val) <= (answer_key_val * tolerance):
            return 1.0
        return 0.0
    except (ValueError, TypeError):
        return 0.0

def evaluate_boolean(submission: bool, answer_key: bool) -> float:
    """Evaluate boolean answers."""
    return 1.0 if submission == answer_key else a0.0

def evaluate_section1(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 1: Transaction Record Keeping Fundamentals."""
    results = {"points_earned": 0, "points_possible": 20, "question_results": {}}
    
    # Q1 & Q2: Multiple choice (4 points each)
    for q in ["q1", "q2"]:
        correct = evaluate_single_choice(submission.get(q, ""), answer_key.get(q, ""))
        points = 4 if correct else 0
        results["points_earned"] += points
        results["question_results"][q] = {"correct": correct, "points_earned": points, "points_possible": 4}
    
    # Q3: Missing information (4 points)
    # Check for key terms: price/value, delivery/location, and one other field
    q3_sim = evaluate_text_similarity(submission.get("q3", ""), answer_key.get("q3", ""))
    q3_points = round(4 * min(q3_sim + 0.2, 1.0))  # Add a small bonus, max 4 points
    results["points_earned"] += q3_points
    results["question_results"]["q3"] = {
        "similarity": q3_sim,
        "points_earned": q3_points,
        "points_possible": 4
    }
    
    # Q4: Error identification (4 points)
    q4_sim = evaluate_text_similarity(submission.get("q4", ""), answer_key.get("q4", ""))
    q4_points = round(4 * min(q4_sim + 0.2, 1.0))
    results["points_earned"] += q4_points
    results["question_results"]["q4"] = {
        "similarity": q4_sim,
        "points_earned": q4_points,
        "points_possible": 4
    }
    
    # Q5: Multiple selection (4 points, 1 per correct option)
    sub_q5 = submission.get("q5", [])
    key_q5 = answer_key.get("q5", [])
    
    # Convert to sets for comparison
    sub_set = set(item.lower() for item in sub_q5)
    key_set = set(item.lower() for item in key_q5)
    
    correct_selections = sub_set.intersection(key_set)
    incorrect_selections = sub_set - key_set
    
    # 1 point per correct selection, max 4 points
    q5_points = min(len(correct_selections), 4)
    
    # Penalty for incorrect selections
    q5_points = max(0, q5_points - len(incorrect_selections))
    
    results["points_earned"] += q5_points
    results["question_results"]["q5"] = {
        "correct_selections": list(correct_selections),
        "incorrect_selections": list(incorrect_selections),
        "points_earned": q5_points,
        "points_possible": 4
    }
    
    return results

def evaluate_section2(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 2: Inventory Record Management."""
    results = {"points_earned": 0, "points_possible": 20, "question_results": {}}
    
    # Q1, Q3, Q5: Multiple choice (4 points each)
    for q in ["q1", "q3", "q5"]:
        correct = evaluate_single_choice(submission.get(q, ""), answer_key.get(q, ""))
        points = 4 if correct else 0
        results["points_earned"] += points
        results["question_results"][q] = {"correct": correct, "points_earned": points, "points_possible": 4}
    
    # Q2: Short answer - inventory tracking methods (4 points)
    q2_sim = evaluate_text_similarity(submission.get("q2", ""), answer_key.get("q2", ""))
    q2_points = round(4 * min(q2_sim + 0.1, 1.0))
    results["points_earned"] += q2_points
    results["question_results"]["q2"] = {
        "similarity": q2_sim,
        "points_earned": q2_points,
        "points_possible": 4
    }
    
    # Q4: Calculation (4 points)
    q4_sub = submission.get("q4", {})
    q4_key = answer_key.get("q4", {})
    q4_points = 0
    
    # Check value_per_unit (2 points)
    if "value_per_unit" in q4_sub and "value_per_unit" in q4_key:
        value_correct = evaluate_numeric(q4_sub["value_per_unit"], q4_key["value_per_unit"])
        q4_points += 2 * value_correct
    
    # Check total_inventory_value (2 points)
    if "total_inventory_value" in q4_sub and "total_inventory_value" in q4_key:
        total_correct = evaluate_numeric(q4_sub["total_inventory_value"], q4_key["total_inventory_value"])
        q4_points += 2 * total_correct
    
    results["points_earned"] += q4_points
    results["question_results"]["q4"] = {
        "points_earned": q4_points,
        "points_possible": 4
    }
    
    return results

def evaluate_section3(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 3: Data Reporting Scenarios."""
    results = {"points_earned": 0, "points_possible": 20, "question_results": {}}
    
    # Q1, Q4: Multiple choice (3 points each)
    for q, points in [("q1", 3), ("q4", 3)]:
        correct = evaluate_single_choice(submission.get(q, ""), answer_key.get(q, ""))
        earned = points if correct else 0
        results["points_earned"] += earned
        results["question_results"][q] = {"correct": correct, "points_earned": earned, "points_possible": points}
    
    # Q2: Short answer - import reporting (4 points)
    q2_sim = evaluate_text_similarity(submission.get("q2", ""), answer_key.get("q2", ""))
    q2_points = round(4 * min(q2_sim + 0.1, 1.0))
    results["points_earned"] += q2_points
    results["question_results"]["q2"] = {
        "similarity": q2_sim,
        "points_earned": q2_points,
        "points_possible": 4
    }
    
    # Q3: Scenario - milk reporting (5 points)
    q3_sim = evaluate_text_similarity(submission.get("q3", ""), answer_key.get("q3", ""))
    q3_points = round(5 * min(q3_sim + 0.1, 1.0))
    results["points_earned"] += q3_points
    results["question_results"]["q3"] = {
        "similarity": q3_sim,
        "points_earned": q3_points,
        "points_possible": 5
    }
    
    # Q5: Matching (5 points, 1 per correct match)
    q5_sub = submission.get("q5", {})
    q5_key = answer_key.get("q5", {})
    q5_points = 0
    
    for item in ["1", "2", "3", "4", "5"]:
        if item in q5_sub and item in q5_key:
            if q5_sub[item].lower() == q5_key[item].lower():
                q5_points += 1
    
    results["points_earned"] += q5_points
    results["question_results"]["q5"] = {
        "points_earned": q5_points,
        "points_possible": 5
    }
    
    return results

def evaluate_section4(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 4: Calculation and Reconciliation Exercise."""
    results = {"points_earned": 0, "points_possible": 20, "question_results": {}}
    
    # Q1: Calculation (4 points)
    q1_sub = submission.get("q1", {})
    q1_key = answer_key.get("q1", {})
    q1_points = 0
    
    # Check total_quantity (1 point)
    if "total_quantity" in q1_sub and "total_quantity" in q1_key:
        quantity_correct = evaluate_numeric(q1_sub["total_quantity"], q1_key["total_quantity"])
        q1_points += quantity_correct
    
    # Check total_cost (1 point)
    if "total_cost" in q1_sub and "total_cost" in q1_key:
        cost_correct = evaluate_numeric(q1_sub["total_cost"], q1_key["total_cost"])
        q1_points += cost_correct
    
    # Check average_price (2 points)
    if "average_price" in q1_sub and "average_price" in q1_key:
        price_correct = evaluate_numeric(q1_sub["average_price"], q1_key["average_price"])
        q1_points += 2 * price_correct
    
    results["points_earned"] += q1_points
    results["question_results"]["q1"] = {
        "points_earned": q1_points,
        "points_possible": 4
    }
    
    # Q2: Variance percentage and causes (4 points)
    q2_sub = submission.get("q2", {})
    q2_key = answer_key.get("q2", {})
    q2_points = 0
    
    # Check variance_percentage (1 point)
    if "variance_percentage" in q2_sub and "variance_percentage" in q2_key:
        variance_correct = evaluate_numeric(q2_sub["variance_percentage"], q2_key["variance_percentage"])
        q2_points += variance_correct
    
    # Check possible_causes (3 points, 1 per plausible cause)
    if "possible_causes" in q2_sub and "possible_causes" in q2_key:
        sub_causes = q2_sub["possible_causes"]
        key_causes = q2_key["possible_causes"]
        
        # For each submitted cause, check if it's reasonably similar to any key cause
        cause_scores = []
        for sub_cause in sub_causes[:3]:  # Only consider up to 3 causes
            best_match = max([evaluate_text_similarity(sub_cause, key_cause) for key_cause in key_causes], default=0)
            cause_scores.append(best_match > 0.3)  # Threshold for acceptance
        
        q2_points += sum(cause_scores)
    
    results["points_earned"] += q2_points
    results["question_results"]["q2"] = {
        "points_earned": q2_points,
        "points_possible": 4
    }
    
    # Q3: Shrinkage calculations (4 points)
    q3_sub = submission.get("q3", {})
    q3_key = answer_key.get("q3", {})
    q3_points = 0
    
    # Check expected_inventory (2 points)
    if "expected_inventory" in q3_sub and "expected_inventory" in q3_key:
        expected_correct = evaluate_numeric(q3_sub["expected_inventory"], q3_key["expected_inventory"])
        q3_points += 2 * expected_correct
    
    # Check acceptable ranges (1 point each)
    if "acceptable_minimum" in q3_sub and "acceptable_minimum" in q3_key:
        min_correct = evaluate_numeric(q3_sub["acceptable_minimum"], q3_key["acceptable_minimum"])
        q3_points += min_correct
    
    if "acceptable_maximum" in q3_sub and "acceptable_maximum" in q3_key:
        max_correct = evaluate_numeric(q3_sub["acceptable_maximum"], q3_key["acceptable_maximum"])
        q3_points += max_correct
    
    results["points_earned"] += q3_points
    results["question_results"]["q3"] = {
        "points_earned": q3_points,
        "points_possible": 4
    }
    
    # Q4: Discrepancy causes and reconciliation (4 points)
    q4_sub = submission.get("q4", {})
    q4_key = answer_key.get("q4", {})
    q4_points = 0
    
    # Check causes (2 points, up to 2 reasonable causes)
    if "causes" in q4_sub and "causes" in q4_key:
        sub_causes = q4_sub["causes"]
        key_causes = q4_key["causes"]
        
        cause_scores = []
        for sub_cause in sub_causes[:3]:  # Only consider up to 3 causes
            best_match = max([evaluate_text_similarity(sub_cause, key_cause) for key_cause in key_causes], default=0)
            cause_scores.append(best_match > 0.3)
        
        q4_points += min(sum(cause_scores), 2)  # Max 2 points for causes
    
    # Check reconciliation methods (2 points, up to 2 reasonable methods)
    if "reconciliation_methods" in q4_sub and "reconciliation_methods" in q4_key:
        sub_methods = q4_sub["reconciliation_methods"]
        key_methods = q4_key["reconciliation_methods"]
        
        method_scores = []
        for sub_method in sub_methods[:3]:  # Only consider up to 3 methods
            best_match = max([evaluate_text_similarity(sub_method, key_method) for key_method in key_methods], default=0)
            method_scores.append(best_match > 0.3)
        
        q4_points += min(sum(method_scores), 2)  # Max 2 points for methods
    
    results["points_earned"] += q4_points
    results["question_results"]["q4"] = {
        "points_earned": q4_points,
        "points_possible": 4
    }
    
    # Q5: Moisture adjustment calculation (4 points)
    q5_sub = submission.get("q5", {})
    q5_key = answer_key.get("q5", {})
    q5_points = 0
    
    # Check is_correct assessment (1 point)
    if "is_correct" in q5_sub and "is_correct" in q5_key:
        correct_assessment = q5_sub["is_correct"] == q5_key["is_correct"]
        q5_points += 1 if correct_assessment else 0
    
    # Check correct_deduction (1 point)
    if "correct_deduction" in q5_sub and "correct_deduction" in q5_key:
        deduction_correct = evaluate_numeric(q5_sub["correct_deduction"], q5_key["correct_deduction"])
        q5_points += deduction_correct
    
    # Check correct_payment (2 points)
    if "correct_payment" in q5_sub and "correct_payment" in q5_key:
        payment_correct = evaluate_numeric(q5_sub["correct_payment"], q5_key["correct_payment"])
        q5_points += 2 * payment_correct
    
    results["points_earned"] += q5_points
    results["question_results"]["q5"] = {
        "points_earned": q5_points,
        "points_possible": 4
    }
    
    return results

def evaluate_section5(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Section 5: Documentation and Compliance Assessment."""
    results = {"points_earned": 0, "points_possible": 20, "question_results": {}}
    
    # Q1, Q4: Multiple choice (3 points each)
    for q, points in [("q1", 3), ("q4", 3)]:
        correct = evaluate_single_choice(submission.get(q, ""), answer_key.get(q, ""))
        earned = points if correct else 0
        results["points_earned"] += earned
        results["question_results"][q] = {"correct": correct, "points_earned": earned, "points_possible": points}
    
    # Q2: List FSMA components (4 points, 1 point per component)
    q2_sub = submission.get("q2", [])
    q2_key = answer_key.get("q2", [])
    
    # Score each submitted component against the key components
    component_scores = []
    for sub_component in q2_sub[:4]:  # Only score up to 4 components
        best_match = max([evaluate_text_similarity(sub_component, key_component) for key_component in q2_key], default=0)
        component_scores.append(best_match > 0.4)  # Threshold for acceptance
    
    q2_points = sum(component_scores)
    results["points_earned"] += q2_points
    results["question_results"]["q2"] = {
        "points_earned": q2_points,
        "points_possible": 4
    }
    
    # Q3: Organic documentation (5 points)
    q3_sim = evaluate_text_similarity(submission.get("q3", ""), answer_key.get("q3", ""))
    q3_points = round(5 * min(q3_sim + 0.1, 1.0))
    results["points_earned"] += q3_points
    results["question_results"]["q3"] = {
        "similarity": q3_sim,
        "points_earned": q3_points,
        "points_possible": 5
    }
    
    # Q5: Corrective steps (5 points)
    q5_sim = evaluate_text_similarity(submission.get("q5", ""), answer_key.get("q5", ""))
    q5_points = round(5 * min(q5_sim + 0.1, 1.0))
    results["points_earned"] += q5_points
    results["question_results"]["q5"] = {
        "similarity": q5_sim,
        "points_earned": q5_points,
        "points_possible": 5
    }
    
    return results

def evaluate_test(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire test and generate final results."""
    # Check if candidate ID matches
    candidate_id = submission.get("candidate_id", "UNKNOWN")
    
    # Initialize results structure
    results = {
        "candidate_id": candidate_id,
        "overall_score": 0,
        "total_points_earned": 0,
        "total_points_possible": 100,
        "pass_fail": "FAIL",
        "section_results": {}
    }
    
    # Evaluate each section
    section_evaluators = {
        "section1": evaluate_section1,
        "section2": evaluate_section2,
        "section3": evaluate_section3,
        "section4": evaluate_section4,
        "section5": evaluate_section5
    }
    
    for section_name, evaluator in section_evaluators.items():
        if section_name in submission and section_name in answer_key:
            section_results = evaluator(submission[section_name], answer_key[section_name])
            results["section_results"][section_name] = section_results
            results["total_points_earned"] += section_results["points_earned"]
    
    # Calculate overall percentage score
    if results["total_points_possible"] > 0:
        results["overall_score"] = round((results["total_points_earned"] / results["total_points_possible"]) * 100, 2)
    
    # Determine if passed (must have 70% overall and at least 60% in each section)
    overall_passing = results["overall_score"] >= 70
    sections_passing = all(section["points_earned"] >= (section["points_possible"] * 0.6) 
                          for section in results["section_results"].values())
    
    results["pass_fail"] = "PASS" if (overall_passing and sections_passing) else "FAIL"
    
    return results

def main():
    # Load submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    # Evaluate the test
    results = evaluate_test(submission, answer_key)
    
    # Save results
    save_json(results, "test_results.json")
    
    # Print summary
    print(f"Evaluation complete! Overall score: {results['overall_score']}%")
    print(f"Result: {results['pass_fail']}")
    print(f"Points earned: {results['total_points_earned']} out of {results['total_points_possible']}")
    print("Section scores:")
    for section, data in results["section_results"].items():
        print(f"  {section}: {data['points_earned']} out of {data['points_possible']} points")

if __name__ == "__main__":
    main()