import json
import os

def evaluate_submission(candidate_answers_path, answer_key_path):
    # Read the candidate's submission
    try:
        with open(candidate_answers_path, 'r') as f:
            candidate_answers = json.load(f)
    except FileNotFoundError:
        return {"error": f"Candidate submission file '{candidate_answers_path}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in candidate submission file '{candidate_answers_path}'."}
    
    # Read the answer key
    try:
        with open(answer_key_path, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": f"Answer key file '{answer_key_path}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file '{answer_key_path}'."}
    
    # Calculate the score
    results = {
        "candidate_id": candidate_answers.get("candidate_id", "Unknown"),
        "section_scores": {},
        "question_results": {},
        "performance_summary": {}
    }
    
    total_score = 0
    total_questions = 0
    points_per_question = 4
    
    # Loop through each section in the answer key
    for section in answer_key:
        if section == "candidate_id":
            continue
            
        section_score = 0
        results["question_results"][section] = {}
        
        # Loop through each question in the section
        for question, correct_answer in answer_key[section].items():
            # Check if the section and question exist in candidate's answers
            candidate_answer = None
            if section in candidate_answers and question in candidate_answers[section]:
                candidate_answer = candidate_answers[section][question].upper()
            
            # Compare candidate answer with correct answer (case-insensitive)
            is_correct = candidate_answer == correct_answer.upper()
            question_score = points_per_question if is_correct else 0
            
            # Record result for this question
            results["question_results"][section][question] = {
                "candidate_answer": candidate_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "score": question_score
            }
            
            section_score += question_score
            total_score += question_score
            total_questions += 1
        
        # Record score for this section
        max_section_score = len(answer_key[section]) * points_per_question
        results["section_scores"][section] = {
            "points": section_score,
            "max_points": max_section_score,
            "percentage": (section_score / max_section_score) * 100
        }
    
    # Calculate overall score
    max_possible_score = total_questions * points_per_question
    overall_score_percentage = (total_score / max_possible_score) * 100
    
    # Determine performance level
    if overall_score_percentage >= 85:
        performance_level = "Excellent"
    elif overall_score_percentage >= 70:
        performance_level = "Satisfactory"
    elif overall_score_percentage >= 60:
        performance_level = "Needs improvement"
    else:
        performance_level = "Unsatisfactory"
    
    # Add performance summary
    results["performance_summary"] = {
        "total_score": total_score,
        "max_possible_score": max_possible_score,
        "overall_score": overall_score_percentage,
        "performance_level": performance_level,
        "passing_grade": overall_score_percentage >= 70
    }
    
    return results

def main():
    candidate_submission_path = 'test_submission.json'
    answer_key_path = 'answer_key.json'
    results_path = 'test_results.json'
    
    # Evaluate the submission
    results = evaluate_submission(candidate_submission_path, answer_key_path)
    
    # Save the results
    try:
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Evaluation completed. Results saved to '{results_path}'.")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    main()