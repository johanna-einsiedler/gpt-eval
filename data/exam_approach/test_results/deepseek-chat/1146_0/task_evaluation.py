import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        exit(1)

def evaluate_task1(submission, answer_key):
    score = 0
    max_score = 2  # 1 for laws, 1 for justification
    feedback = []
    
    # Check applicable laws
    correct_laws = set(answer_key['acceptable_variations']['task_1']['applicable_laws'])
    submitted_laws = set(submission['task_1']['applicable_laws'])
    law_matches = correct_laws.intersection(submitted_laws)
    
    if law_matches:
        score += 1
        feedback.append(f"Correctly identified laws: {', '.join(law_matches)}")
    else:
        feedback.append("No correct laws identified.")
    
    # Check justification
    justification_phrases = answer_key['acceptable_variations']['task_1']['justification']
    justification = submission['task_1']['justification'].lower()
    all_phrases_present = all(phrase.lower() in justification for phrase in justification_phrases)
    
    if all_phrases_present:
        score += 1
        feedback.append("Justification meets requirements.")
    else:
        feedback.append("Justification missing required elements.")
    
    return score, max_score, feedback

def evaluate_task2(submission, answer_key):
    score = 0
    max_score = len(answer_key['answer_key']['task_2']['non_compliant_terms'])
    feedback = []
    
    required_keywords = answer_key['acceptable_variations']['task_2']['non_compliant_terms']['required_keywords']
    min_matches = answer_key['acceptable_variations']['task_2']['non_compliant_terms']['minimum_matches']
    
    found_issues = 0
    for term in submission['task_2']['non_compliant_terms']:
        if any(keyword.lower() in term.lower() for keyword in required_keywords):
            found_issues += 1
    
    score = min(found_issues, max_score)
    
    if found_issues >= min_matches:
        feedback.append(f"Identified {found_issues} of {max_score} compliance issues (minimum {min_matches} required).")
    else:
        feedback.append(f"Insufficient compliance issues identified ({found_issues} of minimum {min_matches}).")
    
    # Check corrective actions
    if len(submission['task_2']['corrective_action']) >= found_issues:
        feedback.append("Appropriate corrective actions provided.")
    else:
        feedback.append("Missing some corrective actions for identified issues.")
    
    return score, max_score, feedback

def evaluate_task3(submission, answer_key):
    score = 0
    max_score = len(answer_key['answer_key']['task_3']['legal_risks'])
    feedback = []
    
    required_concepts = answer_key['acceptable_variations']['task_3']['legal_risks']['required_concepts']
    min_matches = len(required_concepts)
    
    found_risks = 0
    for risk in submission['task_3']['legal_risks']:
        if any(concept.lower() in risk.lower() for concept in required_concepts):
            found_risks += 1
    
    if found_risks >= min_matches:
        score = max_score
        feedback.append(f"Identified all {max_score} required legal risks.")
    else:
        feedback.append(f"Only identified {found_risks} of {max_score} required legal risks.")
    
    # Check mitigation strategies
    if len(submission['task_3']['mitigation_strategy']) >= found_risks:
        feedback.append("Appropriate mitigation strategies provided.")
    else:
        feedback.append("Missing some mitigation strategies for identified risks.")
    
    return score, max_score, feedback

def main():
    # Load files
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')
    
    # Evaluate each task
    task1_score, task1_max, task1_feedback = evaluate_task1(submission, answer_key)
    task2_score, task2_max, task2_feedback = evaluate_task2(submission, answer_key)
    task3_score, task3_max, task3_feedback = evaluate_task3(submission, answer_key)
    
    # Calculate overall score
    total_score = task1_score + task2_score + task3_score
    total_max = task1_max + task2_max + task3_max
    overall_score = round((total_score / total_max) * 100, 2)
    
    # Prepare results
    results = {
        "overall_score": overall_score,
        "task_1": {
            "score": task1_score,
            "max_score": task1_max,
            "feedback": task1_feedback
        },
        "task_2": {
            "score": task2_score,
            "max_score": task2_max,
            "feedback": task2_feedback
        },
        "task_3": {
            "score": task3_score,
            "max_score": task3_max,
            "feedback": task3_feedback
        },
        "pass_status": "Pass" if overall_score >= 70 else "Fail"
    }
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Evaluation complete. Results saved to test_results.json")

if __name__ == "__main__":
    main()