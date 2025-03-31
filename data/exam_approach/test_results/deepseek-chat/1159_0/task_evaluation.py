import json

def validate_submission(submission, answer_key):
    score = 0
    total_fields = 0
    feedback = {}
    
    for task in ["task_1", "task_2"]:
        for field in answer_key["answer_key"][task]:
            total_fields += 1
            response = submission[task][field].lower()
            keywords = answer_key["answer_key"][task][field]["required_keywords"]
            min_words = answer_key["answer_key"][task][field]["min_words"]
            
            # Check word count
            word_count = len(response.split())
            if word_count < min_words:
                feedback[f"{task}.{field}"] = {
                    "status": "FAIL",
                    "reason": f"Word count too low ({word_count}/{min_words})"
                }
                continue
            
            # Check keywords
            missing_keywords = [kw for kw in keywords if kw not in response]
            if not missing_keywords:
                score += 1
                feedback[f"{task}.{field}"] = {
                    "status": "PASS",
                    "missing_keywords": []
                }
            else:
                feedback[f"{task}.{field}"] = {
                    "status": "FAIL",
                    "missing_keywords": missing_keywords
                }
    
    overall_score = (score / total_fields) * 100 if total_fields > 0 else 0
    
    return {
        "overall_score": f"{overall_score:.1f}%",
        "score": f"{score}/{total_fields}",
        "feedback": feedback
    }

def main():
    try:
        # Load submission and answer key
        with open('test_submission.json', 'r') as f:
            submission = json.load(f)
        
        with open('answer_key.json', 'r') as f:
            answer_key = json.load(f)
        
        # Validate submission
        results = validate_submission(submission, answer_key)
        
        # Save results
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("Evaluation completed successfully. Results saved to test_results.json")
    
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure both test_submission.json and answer_key.json exist in the same directory.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in input files. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()