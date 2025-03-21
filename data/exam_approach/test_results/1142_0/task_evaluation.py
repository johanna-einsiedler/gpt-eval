import json
import re
from datetime import datetime

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
        return None

def check_keyword_presence(justification, keywords):
    """Check if any of the keywords are present in the justification."""
    justification_lower = justification.lower()
    return any(keyword.lower() in justification_lower for keyword in keywords)

def validate_justification(question_number, justification):
    """Validate justification based on specific criteria for each question."""
    question_specific_validations = {
        1: check_keyword_presence(justification, ["warranty", "delivery time", "total value", "total cost of ownership"]),
        2: check_keyword_presence(justification, ["MTBF", "industry standard", "discount"]),
        3: check_keyword_presence(justification, ["EOQ", "formula", "safety stock", "economic order quantity"]),
        5: check_keyword_presence(justification, ["annualized", "discount"]) and bool(re.search(r'\d+\.?\d*\s*%', justification)),
        8: check_keyword_presence(justification, ["short-term", "long-term", "risk"]),
    }
    
    # If there's a specific validation for this question, use it, otherwise return True
    return question_specific_validations.get(question_number, True)

def has_coherent_justification(justification):
    """Check if justification is coherent (basic check)."""
    # Check if justification has at least 2 sentences
    sentences = re.split(r'[.!?]+', justification)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return False
    
    # Check if justification has reasonable length
    word_count = len(justification.split())
    return word_count >= 15

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "candidate_name": submission.get("candidate_name", "Unknown"),
        "exam_date": submission.get("exam_date", datetime.now().strftime("%Y-%m-%d")),
        "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
        "question_results": [],
        "core_competency_results": {
            "price_cost_analysis": False,  # Questions 1, 5, 7
            "quality_assessment": False,   # Question 2
            "supply_inventory_management": False,  # Questions 3, 9
            "supplier_evaluation": False,  # Question 4
            "ethics_compliance": False,    # Question 6
            "risk_management": False       # Question 8
        },
        "total_correct": 0,
        "total_questions": len(answer_key),
        "passing_threshold": 7,
        "overall_score": 0.0,
        "passed": False
    }

    # Process each answer
    for answer_item in answer_key:
        question_number = answer_item["question_number"]
        correct_option = answer_item["correct_option"]
        
        # Find corresponding submission answer
        submission_answer = next(
            (a for a in submission.get("answers", []) if a.get("question_number") == question_number), 
            None
        )
        
        if not submission_answer:
            question_result = {
                "question_number": question_number,
                "correct_option": correct_option,
                "submitted_option": None,
                "is_correct": False,
                "justification_valid": False,
                "feedback": "No answer submitted for this question."
            }
        else:
            submitted_option = submission_answer.get("selected_option", "").lower()
            justification = submission_answer.get("justification", "")
            
            is_correct = submitted_option == correct_option.lower()
            justification_valid = (
                validate_justification(question_number, justification) and 
                has_coherent_justification(justification)
            )
            
            # Check for alternative answers with good justification
            alternative_credit = 0
            if not is_correct:
                # Question 1: Alternative answers
                if question_number == 1 and submitted_option in ['a', 'b']:
                    if check_keyword_presence(justification, ["business needs", "cost-sensitivity", "delivery speed"]):
                        alternative_credit = 0.5
                
                # Question 2: Alternative answers
                elif question_number == 2 and submitted_option == 'd':
                    if check_keyword_presence(justification, ["MTBF", "supplier improvement", "improvement plan"]):
                        alternative_credit = 0.5
                
                # Question 8: Alternative answers
                elif question_number == 8 and submitted_option == 'b':
                    if check_keyword_presence(justification, ["long-term risk", "short-term exposure"]):
                        alternative_credit = 0.5
            
            feedback = ""
            if not is_correct and alternative_credit == 0:
                feedback = f"Incorrect option. The correct option is {correct_option}. {answer_item['explanation']}"
            elif alternative_credit > 0:
                feedback = f"Partial credit awarded. While the recommended answer is {correct_option}, your justification demonstrates understanding. {answer_item['explanation']}"
            elif not justification_valid:
                feedback = "Your justification does not adequately explain your reasoning or is missing key concepts."
            else:
                feedback = "Correct! Your justification demonstrates good understanding."
            
            question_result = {
                "question_number": question_number,
                "correct_option": correct_option,
                "submitted_option": submitted_option,
                "is_correct": is_correct,
                "justification_valid": justification_valid,
                "partial_credit": alternative_credit,
                "points_earned": 1 if is_correct else alternative_credit,
                "feedback": feedback
            }
            
            # Update core competency results
            if is_correct or alternative_credit > 0:
                if question_number in [1, 5, 7]:
                    results["core_competency_results"]["price_cost_analysis"] = True
                elif question_number == 2:
                    results["core_competency_results"]["quality_assessment"] = True
                elif question_number in [3, 9]:
                    results["core_competency_results"]["supply_inventory_management"] = True
                elif question_number == 4:
                    results["core_competency_results"]["supplier_evaluation"] = True
                elif question_number == 6:
                    results["core_competency_results"]["ethics_compliance"] = True
                elif question_number == 8:
                    results["core_competency_results"]["risk_management"] = True
                
                results["total_correct"] += (1 if is_correct else alternative_credit)
        
        results["question_results"].append(question_result)
    
    # Calculate overall percentage score
    results["overall_score"] = (results["total_correct"] / results["total_questions"]) * 100
    
    # Determine if passed
    core_competency_requirement = all([
        results["core_competency_results"]["price_cost_analysis"],
        results["core_competency_results"]["quality_assessment"],
        results["core_competency_results"]["supply_inventory_management"],
        results["core_competency_results"]["supplier_evaluation"],
        results["core_competency_results"]["ethics_compliance"],
        results["core_competency_results"]["risk_management"]
    ])
    
    results["passed"] = (
        results["total_correct"] >= results["passing_threshold"] and 
        core_competency_requirement
    )
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Extract answer key items
    if "answer_key" in answer_key:
        answer_key = answer_key["answer_key"]
    
    # Evaluate the submission
    evaluation_results = evaluate_submission(submission, answer_key)
    
    # Save the results
    with open("test_results.json", "w") as file:
        json.dump(evaluation_results, file, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {evaluation_results['overall_score']:.2f}%")
    print(f"Pass status: {'Passed' if evaluation_results['passed'] else 'Failed'}")

if __name__ == "__main__":
    main()