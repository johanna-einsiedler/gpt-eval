import json
import os

def load_json_file(filename):
    """Load and return the contents of a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File {filename} contains invalid JSON.")
        return None

def validate_answer(question_number, candidate_answer, correct_answer):
    """Validate a candidate's answer against the answer key with special handling for certain questions."""
    
    # Convert question number to question ID format (q1, q2, etc.)
    q_id = f"q{question_number}"
    
    if q_id == "q3":
        # Check performance statistics is in position 1 or 2
        perf_stats_valid = candidate_answer[0] == "Performance statistics" or candidate_answer[1] == "Performance statistics"
        # Check personal story is not higher than position 4
        personal_story_valid = candidate_answer.index("Personal story/background") >= 3 if "Personal story/background" in candidate_answer else False
        # Check professional photos is in positions 1-3
        prof_photos_valid = candidate_answer.index("Professional photos") <= 2 if "Professional photos" in candidate_answer else False
        
        return perf_stats_valid and personal_story_valid and prof_photos_valid
    
    elif q_id == "q7":
        # Accept a range of 8-12 works
        try:
            num_works = int(candidate_answer)
            return 8 <= num_works <= 12
        except (ValueError, TypeError):
            return False
    
    elif q_id == "q9":
        # Accept a range of 3-7 business days
        try:
            days = int(candidate_answer)
            return 3 <= days <= 7
        except (ValueError, TypeError):
            return False
    
    # Default case: exact match required
    return candidate_answer == correct_answer

def evaluate_submission(submission, answer_key):
    """Evaluate a candidate's submission against the answer key."""
    
    if not submission or not answer_key:
        return 0
    
    # Extract answers from both documents
    candidate_answers = submission.get("answers", {})
    correct_answers = answer_key.get("answers", {})
    
    # Initialize counters
    correct_count = 0
    total_questions = len(correct_answers)
    
    # Check each answer
    for question_number in range(1, total_questions + 1):
        q_id = f"q{question_number}"
        
        if q_id in candidate_answers and q_id in correct_answers:
            if validate_answer(question_number, candidate_answers[q_id], correct_answers[q_id]):
                correct_count += 1
    
    # Calculate percentage score
    if total_questions > 0:
        percentage_score = (correct_count / total_questions) * 100
    else:
        percentage_score = 0
    
    return percentage_score

def main():
    """Main function to evaluate the test submission."""
    
    # Load the JSON files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    # Evaluate the submission
    overall_score = evaluate_submission(submission, answer_key)
    
    # Prepare the results
    results = {
        "overall_score": overall_score
    }
    
    # Save the results to a file
    try:
        with open("test_results.json", 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation complete. Overall score: {overall_score:.2f}%")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()