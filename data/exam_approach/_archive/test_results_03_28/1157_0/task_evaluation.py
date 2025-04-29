import json
import os

def load_json_file(filename):
    """Load a JSON file and return its contents as a Python dictionary."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json_file(data, filename):
    """Save Python dictionary as a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def evaluate_definition_question(candidate_answer, key_answer, question_id):
    """Evaluate definition questions like 1.1"""
    score = 0
    total_parts = len(key_answer)
    feedback = {}
    
    for term, def_key in key_answer.items():
        if term in candidate_answer:
            # Check if the key concepts are in the candidate's answer
            key_concepts = set(def_key.lower().split())
            candidate_concepts = set(candidate_answer[term].lower().split())
            
            # Calculate how many key words appear in the candidate's answer
            # We're looking for at least 40% of key words to consider it partially correct
            overlap = len(key_concepts.intersection(candidate_concepts))
            keyword_match_ratio = overlap / len(key_concepts) if key_concepts else 0
            
            if keyword_match_ratio >= 0.4:
                score += 1
                feedback[term] = "Correct"
            else:
                feedback[term] = "Incorrect - missing key concepts"
        else:
            feedback[term] = "Missing answer"
    
    return {
        "score": score / total_parts if total_parts > 0 else 0,
        "feedback": feedback
    }

def evaluate_matching_question(candidate_answer, key_answer, question_id):
    """Evaluate matching questions like 1.3"""
    score = 0
    total_parts = len(key_answer)
    feedback = {}
    
    for item, correct_match in key_answer.items():
        if item in candidate_answer:
            if candidate_answer[item] == correct_match:
                score += 1
                feedback[item] = "Correct"
            else:
                feedback[item] = f"Incorrect - should be {correct_match}"
        else:
            feedback[item] = "Missing answer"
    
    return {
        "score": score / total_parts if total_parts > 0 else 0,
        "feedback": feedback
    }

def evaluate_list_order_question(candidate_answer, key_answer, question_id):
    """Evaluate list order questions like 2.1"""
    score = 0
    total_parts = len(key_answer)
    feedback = {}
    
    # Compare each position in the list
    for i, correct_item in enumerate(key_answer):
        position_label = f"Position {i+1}"
        if i < len(candidate_answer):
            if candidate_answer[i] == correct_item:
                score += 1
                feedback[position_label] = "Correct"
            else:
                feedback[position_label] = f"Incorrect - should be {correct_item}"
        else:
            feedback[position_label] = "Missing answer"
    
    return {
        "score": score / total_parts if total_parts > 0 else 0,
        "feedback": feedback
    }

def evaluate_component_list_question(candidate_answer, key_answer, question_id):
    """Evaluate component list questions like 2.2, 4.1"""
    score = 0
    total_parts = len(key_answer)
    feedback = {}
    
    # Compare each item in the list by checking if key concepts are present
    for i, candidate_item in enumerate(candidate_answer):
        item_label = f"Item {i+1}"
        
        if i < len(key_answer):
            # Check if component name contains key concepts
            key_component = key_answer[i]["component"].lower() if "component" in key_answer[i] else key_answer[i]["standard"].lower()
            candidate_component = candidate_item["component"].lower() if "component" in candidate_item else candidate_item["standard"].lower()
            
            # Check if importance/purpose contains key concepts
            key_importance = key_answer[i]["importance"].lower() if "importance" in key_answer[i] else key_answer[i]["purpose"].lower()
            candidate_importance = candidate_item["importance"].lower() if "importance" in candidate_item else candidate_item["purpose"].lower()
            
            # Calculate similarity based on word overlap
            key_component_words = set(key_component.split())
            candidate_component_words = set(candidate_component.split())
            component_overlap = len(key_component_words.intersection(candidate_component_words)) / len(key_component_words) if key_component_words else 0
            
            key_importance_words = set(key_importance.split())
            candidate_importance_words = set(candidate_importance.split())
            importance_overlap = len(key_importance_words.intersection(candidate_importance_words)) / len(key_importance_words) if key_importance_words else 0
            
            # Award points based on overlap
            item_score = 0
            if component_overlap >= 0.3:
                item_score += 0.5
            if importance_overlap >= 0.3:
                item_score += 0.5
            
            score += item_score
            feedback[item_label] = f"Component: {'Acceptable' if component_overlap >= 0.3 else 'Inadequate'}, Explanation: {'Acceptable' if importance_overlap >= 0.3 else 'Inadequate'}"
        else:
            feedback[item_label] = "Excellent"
    
    return {
        "score": min(score / total_parts, 1.0) if total_parts > 0 else 0,
        "feedback": feedback
    }

def evaluate_error_correction_question(candidate_answer, key_answer, question_id):
    """Evaluate error identification and correction questions like 2.3, 5.1, 5.2"""
    score = 0
    total_parts = len(key_answer)
    feedback = {}
    
    # For each error identified, check if it's valid
    for i, candidate_item in enumerate(candidate_answer):
        item_label = f"Error {i+1}"
        
        if i < len(key_answer):
            # Check if the error identification is similar to any in the key
            error_identified = False
            correction_valid = False
            
            candidate_error = candidate_item["error"].lower()
            candidate_correction = candidate_item["correction"].lower()
            
            # Check against all errors in the key to find best match
            best_match_score = 0
            for key_item in key_answer:
                key_error = key_item["error"].lower()
                key_correction = key_item["correction"].lower()
                
                # Calculate similarity for error identification
                key_error_words = set(key_error.split())
                candidate_error_words = set(candidate_error.split())
                error_overlap = len(key_error_words.intersection(candidate_error_words)) / len(key_error_words) if key_error_words else 0
                
                # Calculate similarity for correction
                key_correction_words = set(key_correction.split())
                candidate_correction_words = set(candidate_correction.split())
                correction_overlap = len(key_correction_words.intersection(candidate_correction_words)) / len(key_correction_words) if key_correction_words else 0
                
                # Calculate total match score
                match_score = error_overlap * 0.5 + correction_overlap * 0.5
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    error_identified = error_overlap >= 0.3
                    correction_valid = correction_overlap >= 0.3
            
            # Award points based on identification and correction
            item_score = 0
            if error_identified:
                item_score += 0.5
            if correction_valid:
                item_score += 0.5
            
            score += item_score
            feedback[item_label] = f"Error identification: {'Acceptable' if error_identified else 'Inadequate'}, Correction: {'Acceptable' if correction_valid else 'Inadequate'}"
        else:
            feedback[item_label] = "Missing"
    
    return {
        "score": min(score / total_parts, 1.0) if total_parts > 0 else 0,
        "feedback": feedback
    }

def evaluate_parameters_question(candidate_answer, key_answer, question_id):
    """Evaluate technical parameter questions like 3.1"""
    score = 0
    total_items = len(key_answer)
    feedback = {}
    
    # Create set of valid parameters from key answer
    valid_parameters = set([param.lower() for param in key_answer])
    candidate_parameters = [param.lower() for param in candidate_answer]
    
    # Check how many of the candidate's parameters are valid
    valid_count = 0
    for i, param in enumerate(candidate_parameters):
        item_label = f"Parameter {i+1}"
        
        # Check if the parameter contains key concepts from any valid parameter
        is_valid = False
        for valid_param in valid_parameters:
            # Check if this candidate parameter is similar to this valid parameter
            valid_param_words = set(valid_param.split())
            candidate_param_words = set(param.split())
            overlap = len(valid_param_words.intersection(candidate_param_words)) / len(valid_param_words) if valid_param_words else 0
            
            if overlap >= 0.3:
                is_valid = True
                break
        
        if is_valid:
            valid_count += 1
            feedback[item_label] = "Valid parameter"
        else:
            feedback[item_label] = "Not a critical parameter"
    
    # Calculate score based on how many valid parameters were identified
    score = min(valid_count / total_items, 1.0)
    
    return {
        "score": score,
        "feedback": feedback
    }

def evaluate_explanation_question(candidate_answer, key_answer, question_id):
    """Evaluate explanation-type questions like 3.2"""
    score = 0
    feedback = {}
    
    # Check explanation
    if "problem_explanation" in candidate_answer and "problem_explanation" in key_answer:
        key_explanation = key_answer["problem_explanation"].lower()
        candidate_explanation = candidate_answer["problem_explanation"].lower()
        
        key_words = set(key_explanation.split())
        candidate_words = set(candidate_explanation.split())
        explanation_overlap = len(key_words.intersection(candidate_words)) / len(key_words) if key_words else 0
        
        if explanation_overlap >= 0.3:
            score += 0.5
            feedback["problem_explanation"] = "Acceptable explanation"
        else:
            feedback["problem_explanation"] = "Inadequate explanation"
    else:
        feedback["problem_explanation"] = "Missing explanation"
    
    # Check proper specification
    if "proper_specification" in candidate_answer and "proper_specification" in key_answer:
        key_spec = key_answer["proper_specification"].lower()
        candidate_spec = candidate_answer["proper_specification"].lower()
        
        key_spec_words = set(key_spec.split())
        candidate_spec_words = set(candidate_spec.split())
        spec_overlap = len(key_spec_words.intersection(candidate_spec_words)) / len(key_spec_words) if key_spec_words else 0
        
        if spec_overlap >= 0.3:
            score += 0.5
            feedback["proper_specification"] = "Acceptable specification"
        else:
            feedback["proper_specification"] = "Inadequate specification"
    else:
        feedback["proper_specification"] = "Missing specification"
    
    return {
        "score": score,
        "feedback": feedback
    }

def evaluate_precise_spec_question(candidate_answer, key_answer, question_id):
    """Evaluate questions requiring precise specifications like 3.3"""
    score = 0
    total_items = len(key_answer)
    feedback = {}
    
    for spec_type, key_spec in key_answer.items():
        if spec_type in candidate_answer:
            key_spec_lower = key_spec.lower()
            candidate_spec_lower = candidate_answer[spec_type].lower()
            
            # Check if candidate's spec includes units/measurements
            has_measurements = any(unit in candidate_spec_lower for unit in ["kwh", "w", "watt", "cubic", "feet", "inch", "cm", "mm", "db", "dba", "decibel"])
            is_specific = len(candidate_spec_lower.split()) >= 5  # At least 5 words to be considered specific
            
            # Keyword analysis
            key_words = set(key_spec_lower.split())
            candidate_words = set(candidate_spec_lower.split())
            concept_overlap = len(key_words.intersection(candidate_words)) / len(key_words) if key_words else 0
            
            # Calculate score for this specification
            spec_score = 0
            if has_measurements:
                spec_score += 0.4
            if is_specific:
                spec_score += 0.3
            if concept_overlap >= 0.2:
                spec_score += 0.3
            
            score += min(spec_score, 1.0)
            feedback[spec_type] = "Adequately specific" if spec_score >= 0.5 else "Not specific enough"
        else:
            feedback[spec_type] = "Missing specification"
    
    return {
        "score": score / total_items if total_items > 0 else 0,
        "feedback": feedback
    }

def evaluate_acceptance_criteria_question(candidate_answer, key_answer, question_id):
    """Evaluate acceptance criteria questions like 4.2"""
    score = 0
    total_items = len(key_answer)
    feedback = {}
    
    for i, candidate_criterion in enumerate(candidate_answer):
        item_label = f"Criterion {i+1}"
        
        if i < len(key_answer):
            candidate_criterion_lower = candidate_criterion.lower()
            
            # Check if criterion includes measurements
            has_measurements = any(unit in candidate_criterion_lower for unit in ["inch", "mm", "cm", "kg", "pound", "lb", "%", "percent", "degree"])
            is_specific = len(candidate_criterion_lower.split()) >= 8  # At least 8 words to be considered specific
            is_verifiable = any(word in candidate_criterion_lower for word in ["must", "shall", "required", "maximum", "minimum", "no more than", "at least", "between"])
            
            # Calculate score for this criterion
            criterion_score = 0
            if has_measurements:
                criterion_score += 0.4
            if is_specific:
                criterion_score += 0.3
            if is_verifiable:
                criterion_score += 0.3
            
            score += min(criterion_score, 1.0)
            
            if criterion_score >= 0.7:
                feedback[item_label] = "Excellent - specific and measurable"
            elif criterion_score >= 0.4:
                feedback[item_label] = "Acceptable - somewhat specific"
            else:
                feedback[item_label] = "Inadequate - too vague"
        else:
            feedback[item_label] = "Missing criterion"
    
    return {
        "score": score / total_items if total_items > 0 else 0,
        "feedback": feedback
    }

def evaluate_clarification_question(candidate_answer, key_answer, question_id):
    """Evaluate clarification response questions like 4.3"""
    # Check if response includes requests for specific information
    candidate_response = candidate_answer.lower()
    
    # Key elements to look for in a good response
    specificity_keywords = ["specific", "exactly", "precisely", "detail"]
    standards_keywords = ["standard", "certification", "designation", "code"]
    testing_keywords = ["test", "method", "verification", "validation", "evidence", "documentation"]
    
    # Check for presence of key elements
    has_specificity = any(keyword in candidate_response for keyword in specificity_keywords)
    requests_standards = any(keyword in candidate_response for keyword in standards_keywords)
    requests_testing = any(keyword in candidate_response for keyword in testing_keywords)
    
    # Calculate score
    score = 0
    if has_specificity:
        score += 0.3
    if requests_standards:
        score += 0.4
    if requests_testing:
        score += 0.3
    
    # Generate feedback
    feedback = {}
    if score >= 0.8:
        feedback["evaluation"] = "Excellent - requests specific standards, testing methods, and evidence"
    elif score >= 0.5:
        feedback["evaluation"] = "Acceptable - requests some specific information"
    else:
        feedback["evaluation"] = "Inadequate - doesn't request specific information"
    
    return {
        "score": score,
        "feedback": feedback
    }

def evaluate_multiple_choice_question(candidate_answer, key_answer, question_id):
    """Evaluate multiple choice questions like 5.3"""
    # Simple exact match
    if candidate_answer == key_answer:
        return {
            "score": 1.0,
            "feedback": {"evaluation": "Correct"}
        }
    else:
        return {
            "score": 0.0,
            "feedback": {"evaluation": f"Incorrect - correct answer is {key_answer}"}
        }

def evaluate_spec_types_question(candidate_answer, key_answer, question_id):
    """Evaluate specification type questions like 1.2"""
    score = 0
    total_items = len(key_answer)
    feedback = {}
    
    for item, key_data in key_answer.items():
        if item in candidate_answer:
            candidate_data = candidate_answer[item]
            
            # Check type match
            type_correct = candidate_data["type"].lower() == key_data["type"].lower()
            
            # Check justification quality
            justification_quality = 0
            if "justification" in candidate_data:
                key_justification = key_data["justification"].lower()
                candidate_justification = candidate_data["justification"].lower()
                
                key_just_words = set(key_justification.split())
                candidate_just_words = set(candidate_justification.split())
                
                concept_overlap = len(key_just_words.intersection(candidate_just_words)) / len(key_just_words) if key_just_words else 0
                justification_quality = min(concept_overlap * 2, 1.0)  # Scale up to 1.0
            
            # Calculate item score
            item_score = 0
            if type_correct:
                item_score += 0.5
            item_score += justification_quality * 0.5
            
            score += item_score
            
            if type_correct and justification_quality >= 0.5:
                feedback[item] = "Correct type with adequate justification"
            elif type_correct:
                feedback[item] = "Correct type but weak justification"
            elif justification_quality >= 0.5:
                feedback[item] = "Incorrect type but reasonable justification"
            else:
                feedback[item] = "Incorrect type with weak justification"
        else:
            feedback[item] = "Missing answer"
    
    return {
        "score": score / total_items if total_items > 0 else 0,
        "feedback": feedback
    }

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "section_scores": {},
        "question_scores": {}
    }
    
    total_score = 0
    
    # Define evaluation functions for each question type
    evaluation_functions = {
        "1.1": evaluate_definition_question,
        "1.2": evaluate_spec_types_question,
        "1.3": evaluate_matching_question,
        "2.1": evaluate_list_order_question,
        "2.2": evaluate_component_list_question,
        "2.3": evaluate_error_correction_question,
        "3.1": evaluate_parameters_question,
        "3.2": evaluate_explanation_question,
        "3.3": evaluate_precise_spec_question,
        "4.1": evaluate_component_list_question,
        "4.2": evaluate_acceptance_criteria_question,
        "4.3": evaluate_clarification_question,
        "5.1": evaluate_error_correction_question,
        "5.2": evaluate_error_correction_question,
        "5.3": evaluate_multiple_choice_question
    }
    
    # Track section scores
    section_scores = {
        "1": {"score": 0, "total": 3},
        "2": {"score": 0, "total": 3},
        "3": {"score": 0, "total": 3},
        "4": {"score": 0, "total": 3},
        "5": {"score": 0, "total": 3}
    }
    
    # Evaluate each question
    for question_id, eval_function in evaluation_functions.items():
        section = question_id.split('.')[0]
        
        if question_id in submission and question_id in answer_key:
            evaluation_result = eval_function(submission[question_id], answer_key[question_id], question_id)
            results["question_scores"][question_id] = {
                "score": evaluation_result["score"],
                "feedback": evaluation_result["feedback"]
            }
            
            # Add to section score
            section_scores[section]["score"] += evaluation_result["score"]
            total_score += evaluation_result["score"]
        else:
            results["question_scores"][question_id] = {
                "score": 0,
                "feedback": {"error": "Question not found in submission or answer key"}
            }
    
    # Calculate section percentages
    for section, data in section_scores.items():
        results["section_scores"][section] = {
            "score": data["score"],
            "total": data["total"],
            "percentage": (data["score"] / data["total"]) * 100 if data["total"] > 0 else 0
        }
    
    # Calculate overall percentage
    total_questions = sum(section["total"] for section in section_scores.values())
    results["overall_score"] = (total_score / total_questions) * 100 if total_questions > 0 else 0
    
    # Add pass/fail status
    overall_percentage = results["overall_score"]
    section_minimums_met = all(section["score"] >= 2 for section in results["section_scores"].values())
    
    results["pass"] = overall_percentage >= 70 and section_minimums_met
    
    return results

def main():
    # File paths
    candidate_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"
    
    # Load JSON files
    candidate_submission = load_json_file(candidate_file)
    answer_key = load_json_file(answer_key_file)
    
    # Check if files were loaded successfully
    if not candidate_submission or not answer_key:
        print("Error: Unable to load necessary files.")
        return
    
    # Evaluate submission
    results = evaluate_submission(candidate_submission, answer_key)
    
    # Save results
    save_json_file(results, results_file)

if __name__ == "__main__":
    main()