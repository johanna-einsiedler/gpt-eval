import json
import math

def validate_answer(candidate_answer, correct_answer, answer_type):
    """
    Validates candidate's answer against the correct answer with specified tolerance
    
    Parameters:
        candidate_answer (str): The candidate's submitted answer
        correct_answer (str): The expected correct answer
        answer_type (str): Type of answer - "multiple_values", "percentage", or "single_value"
        
    Returns:
        bool: True if answer is within tolerance, False otherwise
    """
    if answer_type == "multiple_values":
        # Split both answers into arrays
        candidate_values = [float(val.strip()) for val in candidate_answer.split(",")]
        correct_values = [float(val.strip()) for val in correct_answer.split(",")]
        
        # Compare each value with tolerance
        for i in range(len(correct_values)):
            tolerance = correct_values[i] * 0.005  # 0.5% tolerance
            if abs(candidate_values[i] - correct_values[i]) > tolerance:
                return False
        return True
    
    elif answer_type == "percentage":
        # Convert to numbers
        candidate_num = float(candidate_answer)
        correct_num = float(correct_answer)
        
        # 0.2 percentage point tolerance
        return abs(candidate_num - correct_num) <= 0.2
    
    else:  # single_value
        # Convert to numbers
        candidate_num = float(candidate_answer)
        correct_num = float(correct_answer)
        
        # 0.5% tolerance
        tolerance = correct_num * 0.005
        return abs(candidate_num - correct_num) <= tolerance

def evaluate_submission(submission, answer_key):
    """
    Evaluates a candidate's submission against the answer key
    
    Parameters:
        submission (dict): Candidate's submission
        answer_key (dict): The answer key
        
    Returns:
        dict: Evaluation results
    """
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "total_score": 0,
        "max_score": 0,
        "section_scores": {},
        "question_results": {}
    }
    
    # Define answer types for each question
    answer_types = {
        "section1": {
            "question1": "multiple_values",
            "question2": "multiple_values",
            "question3": "multiple_values"
        },
        "section2": {
            "question1": "single_value",
            "question2": "single_value",
            "question3": "single_value"
        },
        "section3": {
            "question1": "single_value",
            "question2": "single_value",
            "question3": "percentage"
        },
        "section4": {
            "question1": "single_value",
            "question2": "percentage",
            "question3": "single_value"
        },
        "section5": {
            "question1": "single_value",
            "question2": "single_value",
            "question3": "single_value"
        }
    }
    
    # Evaluate each section
    for section in range(1, 6):
        section_key = f"section{section}"
        section_score = 0
        section_max = 0
        
        if section_key in submission and section_key in answer_key:
            results["question_results"][section_key] = {}
            
            # Evaluate each question in the section
            for question in range(1, 4):
                question_key = f"question{question}"
                correct = False
                
                if question_key in submission[section_key] and question_key in answer_key[section_key]:
                    candidate_answer = submission[section_key][question_key]
                    correct_answer = answer_key[section_key][question_key]
                    answer_type = answer_types[section_key][question_key]
                    
                    correct = validate_answer(candidate_answer, correct_answer, answer_type)
                    
                    if correct:
                        section_score += 1
                    
                    section_max += 1
                    
                    results["question_results"][section_key][question_key] = {
                        "correct": correct,
                        "candidate_answer": candidate_answer,
                        "expected_answer": correct_answer
                    }
            
            results["section_scores"][section_key] = {
                "score": section_score,
                "max_score": section_max,
                "percentage": (section_score / section_max * 100) if section_max > 0 else 0
            }
            
            results["total_score"] += section_score
            results["max_score"] += section_max
    
    # Calculate overall percentage score
    results["overall_score"] = (results["total_score"] / results["max_score"] * 100) if results["max_score"] > 0 else 0
    
    # Determine if candidate passed based on criteria
    sections_passed = sum(1 for section in results["section_scores"].values() if section["score"] >= 2)
    results["passed"] = (results["total_score"] >= 11) and (sections_passed >= 4)
    
    return results

def main():
    try:
        # Load candidate submission
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        # Load answer key
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
        
        # Evaluate submission
        results = evaluate_submission(submission, answer_key)
        
        # Save results
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Evaluation complete. Overall score: {results['overall_score']:.2f}%")
        print(f"Results saved to test_results.json")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure test_submission.json and answer_key.json are in the same directory.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in one of the input files.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()