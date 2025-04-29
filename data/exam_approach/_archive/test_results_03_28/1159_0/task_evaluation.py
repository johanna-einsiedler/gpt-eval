import json
import os
from typing import Dict, Any, List, Union

def load_json(file_path: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def evaluate_multiple_choice(candidate_answer: str, correct_answer: str) -> float:
    """Evaluate a multiple choice question (questions 1, 2, 5)."""
    return 1.0 if candidate_answer == correct_answer else 0.0

def evaluate_multiple_select(candidate_answer: List[str], correct_answer: List[str]) -> float:
    """Evaluate a multiple select question (question 3)."""
    score = 0.0
    # All possible options
    all_options = ['a', 'b', 'c', 'd', 'e']
    
    for option in all_options:
        # If option is in correct answers and candidate selected it, or
        # if option is not in correct answers and candidate didn't select it
        if ((option in correct_answer and option in candidate_answer) or
            (option not in correct_answer and option not in candidate_answer)):
            score += 0.25  # 2.5 points per correct selection/omission with 10 total points
    
    return score

def evaluate_components_list(candidate_answer: List[str], length_limit: int = None) -> float:
    """Evaluate a list of components (question 4)."""
    score = 0.0
    max_components = 4  # Expected number of components
    
    if len(candidate_answer) < max_components:
        # Partial credit for fewer components
        score = len(candidate_answer) / max_components
    else:
        # Check if each component is within word limit
        valid_components = 0
        for component in candidate_answer[:max_components]:  # Only evaluate required number
            if length_limit is None or len(component.split()) <= length_limit:
                valid_components += 1
        
        score = valid_components / max_components
    
    return score

def evaluate_procedural_elements(candidate_answer: List[str]) -> float:
    """Evaluate critical procedural elements (question 6)."""
    # We're looking for 3 critical elements
    expected_count = 3
    provided_count = min(len(candidate_answer), expected_count)
    
    return provided_count / expected_count

def evaluate_text_response(candidate_answer: str, word_limit: int = None) -> float:
    """Evaluate a text response (question 7)."""
    if not candidate_answer:
        return 0.0
    
    # Check if answer is within word limit
    if word_limit and len(candidate_answer.split()) > word_limit:
        return 0.8  # Penalize for exceeding word limit but still give substantial credit
    
    # We'll give full credit if an answer is provided within the word limit
    # A more sophisticated evaluation would analyze the content
    return 1.0

def evaluate_workflow_steps(candidate_answer: List[str], min_steps: int) -> float:
    """Evaluate workflow steps (question 8)."""
    # Check if the minimum number of steps is provided
    if len(candidate_answer) < min_steps:
        return len(candidate_answer) / min_steps
    
    # We'll give full credit if minimum steps are provided
    # A more sophisticated evaluation would analyze the content and sequence
    return 1.0

def evaluate_policy_framework(candidate_answer: Dict[str, str]) -> float:
    """Evaluate policy framework (question 9)."""
    # Check if 5 sections are provided with descriptions
    expected_sections = 5
    sections_with_descriptions = 0
    
    for section, description in candidate_answer.items():
        if section and description:
            sections_with_descriptions += 1
    
    return min(sections_with_descriptions / expected_sections, 1.0)

def evaluate_evaluation_matrix(candidate_answer: Dict[str, Any]) -> float:
    """Evaluate bid evaluation matrix (question 10)."""
    score = 0.0
    
    # Check if the required keys are present
    required_keys = ["Criteria", "Weights", "Descriptions"]
    if not all(key in candidate_answer for key in required_keys):
        return 0.0
    
    # Check if 4 criteria are provided
    criteria = candidate_answer.get("Criteria", [])
    weights = candidate_answer.get("Weights", [])
    descriptions = candidate_answer.get("Descriptions", [])
    
    if len(criteria) == 4:
        score += 0.25
    
    # Check if 4 weights are provided and they sum to 100
    if len(weights) == 4:
        score += 0.25
        if sum(weights) == 100:
            score += 0.25
    
    # Check if 4 descriptions are provided
    if len(descriptions) == 4:
        score += 0.25
    
    return score

def evaluate_protest_procedure(candidate_answer: List[str], min_steps: int) -> float:
    """Evaluate protest procedure (question 11)."""
    # Check if the minimum number of steps is provided
    if len(candidate_answer) < min_steps:
        return len(candidate_answer) / min_steps
    
    # Check if each step includes a timeframe
    steps_with_timeframe = 0
    for step in candidate_answer[:min_steps]:  # Only evaluate required number
        # Simple check for timeframe: contains words like "days", "weeks", "hours"
        timeframe_keywords = ["day", "week", "hour", "month", "business"]
        if any(keyword in step.lower() for keyword in timeframe_keywords):
            steps_with_timeframe += 1
    
    return steps_with_timeframe / min_steps

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "section_scores": {},
        "question_scores": {},
        "total_points": 0,
        "max_points": 100,
        "overall_score": 0
    }
    
    # Define point values for each question
    point_values = {
        "1": 5,   # Multiple choice
        "2": 5,   # Multiple choice
        "3": 10,  # Multiple select
        "4": 15,  # Components list
        "5": 5,   # Multiple choice
        "6": 9,   # Procedural elements
        "7": 10,  # Text response
        "8": 11,  # Workflow steps
        "9": 10,  # Policy framework
        "10": 10, # Evaluation matrix
        "11": 10  # Protest procedure
    }
    
    # Section scores
    section_scores = {
        "Section 1": 0,  # Questions 1-5
        "Section 2": 0,  # Questions 6-8
        "Section 3": 0   # Questions 9-11
    }
    
    # Evaluate each question
    for q_num in point_values:
        candidate_answer = submission.get(q_num)
        correct_answer = answer_key.get(q_num)
        
        if candidate_answer is None:
            raw_score = 0.0
        elif q_num in ["1", "2", "5"]:  # Multiple choice
            raw_score = evaluate_multiple_choice(candidate_answer, correct_answer)
        elif q_num == "3":  # Multiple select
            raw_score = evaluate_multiple_select(candidate_answer, correct_answer)
        elif q_num == "4":  # Components list
            raw_score = evaluate_components_list(candidate_answer, length_limit=10)
        elif q_num == "6":  # Procedural elements
            raw_score = evaluate_procedural_elements(candidate_answer)
        elif q_num == "7":  # Text response
            raw_score = evaluate_text_response(candidate_answer, word_limit=100)
        elif q_num == "8":  # Workflow steps
            raw_score = evaluate_workflow_steps(candidate_answer, min_steps=4)
        elif q_num == "9":  # Policy framework
            raw_score = evaluate_policy_framework(candidate_answer)
        elif q_num == "10":  # Evaluation matrix
            raw_score = evaluate_evaluation_matrix(candidate_answer)
        elif q_num == "11":  # Protest procedure
            raw_score = evaluate_protest_procedure(candidate_answer, min_steps=5)
        else:
            raw_score = 0.0
        
        # Calculate points for this question
        points = raw_score * point_values[q_num]
        results["question_scores"][q_num] = {
            "raw_score": raw_score,
            "points": points,
            "max_points": point_values[q_num]
        }
        
        # Add to total points
        results["total_points"] += points
        
        # Add to section scores
        if q_num in ["1", "2", "3", "4", "5"]:
            section_scores["Section 1"] += points
        elif q_num in ["6", "7", "8"]:
            section_scores["Section 2"] += points
        elif q_num in ["9", "10", "11"]:
            section_scores["Section 3"] += points
    
    # Calculate section percentages
    section_max_points = {
        "Section 1": 40,
        "Section 2": 30,
        "Section 3": 30
    }
    
    for section, score in section_scores.items():
        results["section_scores"][section] = {
            "points": score,
            "max_points": section_max_points[section],
            "percentage": (score / section_max_points[section]) * 100
        }
    
    # Calculate overall score
    results["overall_score"] = (results["total_points"] / results["max_points"]) * 100
    
    # Determine pass/fail status
    passing_score = 70
    results["passed"] = results["overall_score"] >= passing_score
    
    # Determine performance level
    if results["overall_score"] >= 85:
        results["performance_level"] = "Excellent"
    elif results["overall_score"] >= 70:
        results["performance_level"] = "Satisfactory"
    else:
        results["performance_level"] = "Needs Improvement"
    
    return results

def main():
    # File paths
    submission_path = "test_submission.json"
    answer_key_path = "answer_key.json"
    results_path = "test_results.json"
    
    # Load files
    submission = load_json(submission_path)
    answer_key = load_json(answer_key_path)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {results_path}")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Performance level: {results['performance_level']}")

if __name__ == "__main__":
    main()