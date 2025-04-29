import json
import math
import os

def load_json_file(filename):
    """Load and return JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON")
        return None

def validate_answer(candidate_answer, correct_answer, question_num):
    """Validate the candidate's answer against the correct answer."""
    # For calculation questions (2, 4, 7, 10)
    if question_num in ["q2", "q4", "q7", "q10"]:
        try:
            candidate_value = float(candidate_answer)
            correct_value = float(correct_answer)
            # Allow for rounding differences within $1.00
            return math.isclose(candidate_value, correct_value, abs_tol=1.0)
        except (ValueError, TypeError):
            return False
    # For boolean question (q9)
    elif question_num == "q9":
        if isinstance(candidate_answer, bool) and isinstance(correct_answer, bool):
            return candidate_answer == correct_answer
        # Handle string "true"/"false" vs boolean true/false
        if isinstance(candidate_answer, str) and isinstance(correct_answer, bool):
            return (candidate_answer.lower() == "true" and correct_answer is True) or \
                   (candidate_answer.lower() == "false" and correct_answer is False)
        return False
    # For multiple choice questions (1, 3, 5, 6, 8)
    else:
        if isinstance(candidate_answer, str) and isinstance(correct_answer, str):
            return candidate_answer.lower() == correct_answer.lower()
        return candidate_answer == correct_answer

def evaluate_submission(submission, answer_key):
    """Evaluate the candidate's submission against the answer key."""
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "total_questions": 10,
        "correct_answers": 0,
        "calculation_questions_correct": 0,
        "question_results": {}
    }
    
    # Calculate scores for each question
    for q_num in range(1, 11):
        q_key = f"q{q_num}"
        
        if q_key in submission and q_key in answer_key:
            is_correct = validate_answer(submission[q_key], answer_key[q_key], q_key)
            results["question_results"][q_key] = {
                "candidate_answer": submission[q_key],
                "correct_answer": answer_key[q_key],
                "is_correct": is_correct
            }
            
            if is_correct:
                results["correct_answers"] += 1
                # Track correct calculation questions
                if q_key in ["q2", "q4", "q7", "q10"]:
                    results["calculation_questions_correct"] += 1
        else:
            results["question_results"][q_key] = {
                "candidate_answer": "Not provided" if q_key not in submission else submission[q_key],
                "correct_answer": "Not available" if q_key not in answer_key else answer_key[q_key],
                "is_correct": False
            }
    
    # Calculate overall score
    if results["total_questions"] > 0:
        results["overall_score"] = round((results["correct_answers"] / results["total_questions"]) * 100, 2)
    
    # Add pass/fail status
    results["passed"] = (results["correct_answers"] >= 7 and results["calculation_questions_correct"] >= 2)
    
    return results

def main():
    """Main function to run the evaluation."""
    # Load the files
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Evaluation could not be completed due to missing files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
    
    print(f"Evaluation completed. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Passed: {results['passed']}")

if __name__ == "__main__":
    main()