#!/usr/bin/env python3
import json
import sys
import re
from collections import Counter

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def count_words(text):
    if not text:
        return 0
    return len(re.findall(r'\b\w+\b', text))

def evaluate_survey_introduction(candidate_intro):
    """Evaluate the survey introduction (10 points)"""
    score = 0
    feedback = []
    
    # Check word count (100-150 words)
    word_count = count_words(candidate_intro)
    if 100 <= word_count <= 150:
        score += 2
        feedback.append("Introduction has appropriate length (100-150 words)")
    else:
        feedback.append(f"Introduction length ({word_count} words) outside recommended range (100-150 words)")
    
    # Check for key elements
    key_elements = {
        "purpose": ["purpose", "assess", "survey", "feedback", "information"],
        "new initiatives": ["new", "initiative", "program", "plan", "upcoming", "future"],
        "data use": ["use", "data", "design", "develop", "create", "improve", "help"],
        "confidentiality": ["confidential", "anonymous", "privacy", "private"],
        "thanks": ["thank", "appreciate", "grateful", "value"]
    }
    
    for element, keywords in key_elements.items():
        if any(keyword.lower() in candidate_intro.lower() for keyword in keywords):
            score += 1.6  # 8 points distributed across 5 elements
            feedback.append(f"Introduction includes {element}")
        else:
            feedback.append(f"Introduction missing {element}")
    
    return {
        "score": min(10, score),  # Cap at 10 points
        "feedback": feedback
    }

def evaluate_question_coverage(candidate_questions):
    """Evaluate question coverage across required categories (20 points)"""
    score = 0
    feedback = []
    
    # Check total number of questions (minimum 15)
    if len(candidate_questions) >= 15:
        score += 5
        feedback.append(f"Sufficient number of questions ({len(candidate_questions)})")
    else:
        feedback.append(f"Insufficient number of questions ({len(candidate_questions)}), minimum 15 required")
    
    # Check category distribution
    categories = {
        "current habits": 0,
        "program interest": 0,
        "scheduling preferences": 0,
        "participation barriers": 0,
        "demographics": 0
    }
    
    for question in candidate_questions:
        category = question.get("category", "").lower()
        if category in categories:
            categories[category] += 1
    
    # Evaluate category coverage
    required_counts = {
        "current habits": 3,
        "program interest": 3,
        "scheduling preferences": 3,
        "participation barriers": 2,
        "demographics": 2
    }
    
    for category, count in categories.items():
        required = required_counts.get(category, 0)
        if count >= required:
            score += 3  # 15 points distributed across 5 categories
            feedback.append(f"Sufficient {category} questions ({count})")
        else:
            feedback.append(f"Insufficient {category} questions ({count}), minimum {required} required")
    
    return {
        "score": min(20, score),  # Cap at 20 points
        "feedback": feedback,
        "categories": categories
    }

def evaluate_question_types(candidate_questions):
    """Evaluate variety of question types (10 points)"""
    score = 0
    feedback = []
    
    # Count different question types
    question_types = Counter()
    for question in candidate_questions:
        q_type = question.get("question_type", "").lower()
        if q_type:
            question_types[q_type] += 1
    
    # Evaluate variety
    if len(question_types) >= 4:
        score += 5
        feedback.append(f"Excellent variety of question types ({len(question_types)} different types)")
    elif len(question_types) == 3:
        score += 4
        feedback.append(f"Good variety of question types ({len(question_types)} different types)")
    elif len(question_types) == 2:
        score += 2
        feedback.append(f"Limited variety of question types ({len(question_types)} different types)")
    else:
        feedback.append(f"Poor variety of question types ({len(question_types)} different types)")
    
    # Check for specific question types
    expected_types = ["multiple choice", "rating scale", "open-ended", "checkbox"]
    for q_type in expected_types:
        if question_types[q_type] > 0:
            score += 1.25  # 5 points distributed across 4 expected types
            feedback.append(f"Includes {q_type} questions ({question_types[q_type]})")
        else:
            feedback.append(f"Missing {q_type} questions")
    
    return {
        "score": min(10, score),  # Cap at 10 points
        "feedback": feedback,
        "question_types": dict(question_types)
    }

def evaluate_question_quality(candidate_questions):
    """Evaluate quality of questions (10 points)"""
    score = 0
    feedback = []
    
    # Check for questions with options
    questions_with_options = 0
    for question in candidate_questions:
        q_type = question.get("question_type", "").lower()
        options = question.get("options", [])
        
        if q_type in ["multiple choice", "checkbox", "dropdown", "rating scale"] and options:
            questions_with_options += 1
    
    # Calculate percentage of questions with appropriate options
    if candidate_questions:
        option_percentage = questions_with_options / len(candidate_questions)
        if option_percentage >= 0.9:
            score += 3
            feedback.append("Excellent provision of options for appropriate question types")
        elif option_percentage >= 0.7:
            score += 2
            feedback.append("Good provision of options for appropriate question types")
        else:
            feedback.append("Insufficient options provided for question types")
    
    # Check for clear question text
    clear_questions = 0
    for question in candidate_questions:
        q_text = question.get("question_text", "")
        if q_text and len(q_text.split()) >= 3 and "?" in q_text:
            clear_questions += 1
    
    if candidate_questions:
        clear_percentage = clear_questions / len(candidate_questions)
        if clear_percentage >= 0.9:
            score += 3
            feedback.append("Questions are clearly worded")
        elif clear_percentage >= 0.7:
            score += 2
            feedback.append("Most questions are clearly worded")
        else:
            feedback.append("Many questions lack clear wording")
    
    # Check for logical numbering
    has_logical_numbering = True
    for i, question in enumerate(candidate_questions):
        if question.get("question_number") != i + 1:
            has_logical_numbering = False
            break
    
    if has_logical_numbering:
        score += 2
        feedback.append("Questions follow logical numbering")
    else:
        feedback.append("Questions lack logical numbering")
    
    # Check for demographic questions
    demographic_questions = sum(1 for q in candidate_questions if q.get("category") == "demographics")
    if 2 <= demographic_questions <= 3:
        score += 2
        feedback.append(f"Appropriate number of demographic questions ({demographic_questions})")
    else:
        feedback.append(f"Inappropriate number of demographic questions ({demographic_questions}), 2-3 required")
    
    return {
        "score": min(10, score),  # Cap at 10 points
        "feedback": feedback
    }

def evaluate_key_findings(candidate_findings):
    """Evaluate key findings (20 points)"""
    score = 0
    feedback = []
    
    # Check word count (max 250 words)
    word_count = count_words(candidate_findings)
    if word_count <= 250:
        score += 2
        feedback.append(f"Key findings within word limit ({word_count}/250)")
    else:
        feedback.append(f"Key findings exceed word limit ({word_count}/250)")
    
    # Check for key patterns that should be identified
    key_patterns = {
        "departmental preferences": ["department", "hr", "it", "finance", "marketing", "operations"],
        "attendance correlation": ["attendance", "weekly", "monthly", "rarely", "frequency", "correlation"],
        "scheduling issues": ["schedule", "timing", "time", "conflict", "convenient", "inconvenient"],
        "skill level concerns": ["beginner", "advanced", "level", "difficulty", "skill"],
        "program-specific feedback": ["yoga", "nutrition", "stress", "walking", "fitness challenge"]
    }
    
    for pattern, keywords in key_patterns.items():
        if any(keyword.lower() in candidate_findings.lower() for keyword in keywords):
            score += 3.6  # 18 points distributed across 5 patterns
            feedback.append(f"Findings identify {pattern}")
        else:
            feedback.append(f"Findings miss {pattern}")
    
    return {
        "score": min(20, score),  # Cap at 20 points
        "feedback": feedback
    }

def evaluate_recommendations(candidate_recommendations):
    """Evaluate recommendations (20 points)"""
    score = 0
    feedback = []
    
    # Check number of recommendations (3-5)
    num_recommendations = len(candidate_recommendations)
    if 3 <= num_recommendations <= 5:
        score += 4
        feedback.append(f"Appropriate number of recommendations ({num_recommendations})")
    else:
        feedback.append(f"Inappropriate number of recommendations ({num_recommendations}), 3-5 required")
    
    # Check recommendation quality
    specific_count = 0
    actionable_count = 0
    justified_count = 0
    
    for rec in candidate_recommendations:
        # Check if specific
        rec_text = rec.get("recommendation", "")
        if rec_text and len(rec_text.split()) >= 5:
            specific_count += 1
        
        # Check if actionable
        action_words = ["implement", "create", "develop", "offer", "introduce", "redesign", "improve", "increase", "add"]
        if any(word in rec_text.lower() for word in action_words):
            actionable_count += 1
        
        # Check if justified
        justification = rec.get("justification", "")
        if justification and len(justification.split()) >= 30:
            justified_count += 1
    
    # Score based on quality metrics
    if num_recommendations > 0:
        specific_percentage = specific_count / num_recommendations
        if specific_percentage >= 0.8:
            score += 5
            feedback.append("Recommendations are specific")
        elif specific_percentage >= 0.6:
            score += 3
            feedback.append("Most recommendations are specific")
        else:
            feedback.append("Recommendations lack specificity")
        
        actionable_percentage = actionable_count / num_recommendations
        if actionable_percentage >= 0.8:
            score += 5
            feedback.append("Recommendations are actionable")
        elif actionable_percentage >= 0.6:
            score += 3
            feedback.append("Most recommendations are actionable")
        else:
            feedback.append("Recommendations lack actionability")
        
        justified_percentage = justified_count / num_recommendations
        if justified_percentage >= 0.8:
            score += 6
            feedback.append("Recommendations are well-justified")
        elif justified_percentage >= 0.6:
            score += 4
            feedback.append("Most recommendations are justified")
        else:
            feedback.append("Recommendations lack proper justification")
    
    return {
        "score": min(20, score),  # Cap at 20 points
        "feedback": feedback
    }

def evaluate_visual_presentation(candidate_visual):
    """Evaluate visual presentation (10 points)"""
    score = 0
    feedback = []
    
    # Check for chart type
    if "chart_type" in candidate_visual and candidate_visual["chart_type"]:
        score += 3
        feedback.append(f"Specifies chart type ({candidate_visual['chart_type']})")
    else:
        feedback.append("Missing chart type")
    
    # Check for data represented
    if "data_represented" in candidate_visual and candidate_visual["data_represented"]:
        data_rep = candidate_visual["data_represented"]
        if len(data_rep.split()) >= 5:
            score += 3
            feedback.append("Clearly describes data to be represented")
        else:
            score += 1
            feedback.append("Data representation description is too brief")
    else:
        feedback.append("Missing data representation description")
    
    # Check for purpose
    if "purpose" in candidate_visual and candidate_visual["purpose"]:
        purpose = candidate_visual["purpose"]
        if len(purpose.split()) >= 10:
            score += 4
            feedback.append("Clearly explains visualization purpose")
        else:
            score += 2
            feedback.append("Visualization purpose explanation is too brief")
    else:
        feedback.append("Missing visualization purpose")
    
    return {
        "score": min(10, score),  # Cap at 10 points
        "feedback": feedback
    }

def evaluate_submission(candidate, answer_key):
    results = {
        "candidate_id": candidate.get("candidate_id", "Unknown"),
        "candidate_name": candidate.get("candidate_name", "Unknown"),
        "part1_survey_design": {},
        "part2_data_analysis": {},
        "overall_score": 0
    }
    
    # Part 1: Survey Design (50 points)
    # Introduction (10 points)
    candidate_intro = candidate.get("part1_survey_design", {}).get("survey_introduction", "")
    intro_eval = evaluate_survey_introduction(candidate_intro)
    results["part1_survey_design"]["introduction"] = intro_eval
    
    # Question Coverage (20 points)
    candidate_questions = candidate.get("part1_survey_design", {}).get("survey_questions", [])
    coverage_eval = evaluate_question_coverage(candidate_questions)
    results["part1_survey_design"]["question_coverage"] = coverage_eval
    
    # Question Types (10 points)
    types_eval = evaluate_question_types(candidate_questions)
    results["part1_survey_design"]["question_types"] = types_eval
    
    # Question Quality (10 points)
    quality_eval = evaluate_question_quality(candidate_questions)
    results["part1_survey_design"]["question_quality"] = quality_eval
    
    # Calculate Part 1 total
    part1_score = (
        intro_eval["score"] +
        coverage_eval["score"] +
        types_eval["score"] +
        quality_eval["score"]
    )
    results["part1_survey_design"]["total_score"] = part1_score
    results["part1_survey_design"]["max_score"] = 50
    results["part1_survey_design"]["percentage"] = (part1_score / 50) * 100
    
    # Part 2: Data Analysis (50 points)
    # Key Findings (20 points)
    candidate_findings = candidate.get("part2_data_analysis", {}).get("key_findings", "")
    findings_eval = evaluate_key_findings(candidate_findings)
    results["part2_data_analysis"]["key_findings"] = findings_eval
    
    # Recommendations (20 points)
    candidate_recommendations = candidate.get("part2_data_analysis", {}).get("recommendations", [])
    recommendations_eval = evaluate_recommendations(candidate_recommendations)
    results["part2_data_analysis"]["recommendations"] = recommendations_eval
    
    # Visual Presentation (10 points)
    candidate_visual = candidate.get("part2_data_analysis", {}).get("visual_presentation", {})
    visual_eval = evaluate_visual_presentation(candidate_visual)
    results["part2_data_analysis"]["visual_presentation"] = visual_eval
    
    # Calculate Part 2 total
    part2_score = (
        findings_eval["score"] +
        recommendations_eval["score"] +
        visual_eval["score"]
    )
    results["part2_data_analysis"]["total_score"] = part2_score
    results["part2_data_analysis"]["max_score"] = 50
    results["part2_data_analysis"]["percentage"] = (part2_score / 50) * 100
    
    # Calculate overall score
    total_score = part1_score + part2_score
    results["total_score"] = total_score
    results["max_score"] = 100
    results["overall_score"] = (total_score / 100) * 100
    
    # Determine if passed
    passed = (
        results["overall_score"] >= 70 and
        results["part1_survey_design"]["percentage"] >= 70 and
        results["part2_data_analysis"]["percentage"] >= 70 and
        intro_eval["score"] >= 5 and
        coverage_eval["score"] >= 10 and
        types_eval["score"] >= 5 and
        quality_eval["score"] >= 5 and
        findings_eval["score"] >= 10 and
        recommendations_eval["score"] >= 10 and
        visual_eval["score"] >= 5
    )
    
    results["passed"] = passed
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    candidate = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(candidate, answer_key)
    
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()