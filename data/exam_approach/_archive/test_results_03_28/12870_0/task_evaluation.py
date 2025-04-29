import json
import re
from pathlib import Path

def load_json_file(file_path):
    """Load and return JSON content from the specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save data as JSON to the specified file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving results to {file_path}: {e}")

def semantic_match_score(answer, key_point):
    """
    Simple implementation of semantic matching.
    Checks if key terms from the key_point appear in the answer.
    
    A more sophisticated implementation would use NLP techniques.
    """
    # Extract key terms (simplistic approach)
    key_terms = re.findall(r'\b\w+\b', key_point.lower())
    key_terms = [term for term in key_terms if len(term) > 3]  # Filter out short words
    
    # Count matches
    matches = sum(1 for term in key_terms if term in answer.lower())
    
    # Calculate score (0.0 to 1.0)
    return matches / len(key_terms) if key_terms else 0.0

def contains_key_point(answer, key_point, threshold=0.6):
    """Check if the answer contains the key point using semantic matching."""
    return semantic_match_score(answer, key_point) > threshold

def apply_custom_validation(answer, validation_notes, base_score):
    """
    Apply custom validation rules based on validation notes.
    This is a simplified implementation.
    """
    # Example rule: Accept ranges within certain percentage points
    if "Accept accurate ranges within" in validation_notes:
        # Assume compliance unless clearly wrong (simplified)
        return base_score
    
    # Example rule: Must identify at least one shift/change
    if "must identify at least one" in validation_notes.lower():
        indicators = ["shift", "change", "increase", "decrease", "growth", "reduction"]
        if not any(indicator in answer.lower() for indicator in indicators):
            return base_score * 0.7
    
    # Default: return the base score
    return base_score

def validate_answer(candidate_answer, question_key):
    """
    Validate a candidate's answer against the expected key points.
    Returns a score between 0 and 6.25.
    """
    max_score = 6.25
    
    # Count key points identified
    key_points_identified = 0
    total_key_points = len(question_key["key_points"])
    
    for key_point in question_key["key_points"]:
        if contains_key_point(candidate_answer, key_point):
            key_points_identified += 1
    
    # Calculate coverage percentage
    coverage_percentage = key_points_identified / total_key_points
    base_score = coverage_percentage * max_score
    
    # Apply custom validation if available
    if "validation_notes" in question_key:
        return apply_custom_validation(candidate_answer, question_key["validation_notes"], base_score)
    
    return base_score

def evaluate_submission(submission, answer_key):
    """
    Evaluate the candidate's submission against the answer key.
    Returns the overall score (0-100).
    """
    total_score = 0
    
    # Evaluate each section
    for section_name in ["section1", "section2", "section3", "section4"]:
        if section_name in submission and section_name in answer_key:
            for question_num, question_key in answer_key[section_name].items():
                if question_num in submission[section_name]:
                    candidate_answer = submission[section_name][question_num]
                    score = validate_answer(candidate_answer, question_key)
                    total_score += score
                    print(f"{section_name}.{question_num}: {score:.2f}/6.25")
                else:
                    print(f"{section_name}.{question_num}: Missing answer")
        else:
            print(f"{section_name}: Missing section")
    
    # Calculate overall score as a percentage
    overall_score = (total_score / 100) * 100
    return overall_score

def main():
    # Define file paths
    current_dir = Path(__file__).parent
    submission_path = current_dir / "test_submission.json"
    answer_key_path = current_dir / "answer_key.json"
    results_path = current_dir / "test_results.json"
    
    # Load files
    submission = load_json_file(submission_path)
    answer_key_data = load_json_file(answer_key_path)
    
    if not submission or not answer_key_data:
        print("Error: Could not load required files")
        return
    
    # Extract answer key from the loaded data
    answer_key = answer_key_data.get("answer_key", {})
    if not answer_key:
        print("Error: Answer key format is invalid")
        return
    
    # Evaluate submission
    print("Starting evaluation...")
    overall_score = evaluate_submission(submission, answer_key)
    print(f"Overall Score: {overall_score:.2f}%")
    
    # Determine pass status
    pass_status = "Fail"
    if overall_score >= 85:
        pass_status = "Pass with Distinction"
    elif overall_score >= 70:
        pass_status = "Pass"
    elif overall_score >= 60:
        pass_status = "Conditional Pass (requires follow-up interview)"
    
    # Save results
    results = {
        "overall_score": overall_score,
        "pass_status": pass_status,
        "candidate_name": submission.get("candidate_name", "Unknown"),
        "date": submission.get("date", "Unknown")
    }
    
    save_json_file(results, results_path)

if __name__ == "__main__":
    main()