#!/usr/bin/env python3
import json
import sys
import re
from collections import Counter

def count_words(text):
    """Count the number of words in a text string."""
    return len(re.findall(r'\b\w+\b', text))

def check_word_count_requirements(submission):
    """Check if all word count requirements are met in the submission."""
    word_count_issues = []
    
    # Task 1: 150-250 words for explanations
    for scenario in ["scenario1", "scenario2", "scenario3"]:
        if scenario in submission["task1"]:
            explanation = submission["task1"][scenario].get("explanation", "")
            word_count = count_words(explanation)
            if word_count < 150 or word_count > 250:
                word_count_issues.append(f"Task 1 {scenario} explanation: {word_count} words (required: 150-250)")
    
    # Task 2: 10-25 words for each field
    for service in ["credit_counseling", "debt_management_program", "debt_settlement"]:
        if service in submission["task2"]:
            for field in ["primary_benefit", "main_disadvantage", "typical_timeline", "credit_score_impact"]:
                if field in submission["task2"][service]:
                    text = submission["task2"][service][field]
                    word_count = count_words(text)
                    if word_count < 10 or word_count > 25:
                        word_count_issues.append(f"Task 2 {service} {field}: {word_count} words (required: 10-25)")
    
    # Task 3: 50-75 words for each rule explanation
    for rule in ["rule1", "rule2", "rule3"]:
        if rule in submission["task3"]:
            explanation = submission["task3"][rule]
            word_count = count_words(explanation)
            if word_count < 50 or word_count > 75:
                word_count_issues.append(f"Task 3 {rule}: {word_count} words (required: 50-75)")
    
    return word_count_issues

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Client Scenario Responses."""
    results = {
        "scenario1": {"score": 0, "max_score": 10, "feedback": []},
        "scenario2": {"score": 0, "max_score": 10, "feedback": []},
        "scenario3": {"score": 0, "max_score": 10, "feedback": []}
    }
    
    # Key elements to check for in each scenario
    key_elements = {
        "scenario1": [
            "notation on credit report",
            "closing accounts impact",
            "positive payment history",
            "improved debt-to-income ratio",
            "balanced view of impacts"
        ],
        "scenario2": [
            "grace period",
            "impact on concessions",
            "three missed payments termination",
            "re-enrollment requirements",
            "actionable advice"
        ],
        "scenario3": [
            "fee deduction",
            "pro-rata distribution",
            "example of distribution",
            "disbursement timeline",
            "payment tracking"
        ]
    }
    
    # Check each scenario
    for scenario, elements in key_elements.items():
        if scenario not in submission["task1"]:
            results[scenario]["feedback"].append("Missing response")
            continue
            
        # Check explanation content
        explanation = submission["task1"][scenario].get("explanation", "")
        if not explanation:
            results[scenario]["feedback"].append("Missing explanation")
        else:
            # Check for key elements (simplified check)
            found_elements = []
            for element in elements:
                # This is a simplified check - in a real evaluation, you'd want more sophisticated matching
                if any(keyword in explanation.lower() for keyword in element.split()):
                    found_elements.append(element)
            
            element_score = min(5, len(found_elements))
            results[scenario]["score"] += element_score
            
            if len(found_elements) < len(elements):
                missing = set(elements) - set(found_elements)
                results[scenario]["feedback"].append(f"Missing key elements: {', '.join(missing)}")
        
        # Check key points
        key_points = submission["task1"][scenario].get("key_points", [])
        if not key_points or len(key_points) < 2:
            results[scenario]["feedback"].append("Missing or insufficient key points")
        else:
            # Check if key points match those in answer key
            answer_key_points = set(answer_key["task1"][scenario]["key_points"])
            matching_points = 0
            
            for point in key_points:
                # Check for substantial similarity to any answer key point
                if any(similarity_check(point, key_point) for key_point in answer_key_points):
                    matching_points += 1
            
            point_score = min(5, matching_points * 2.5)
            results[scenario]["score"] += point_score
            
            if matching_points < 2:
                results[scenario]["feedback"].append(f"Only {matching_points}/2 key points match reference answer")
        
        # Add general feedback if score is perfect
        if results[scenario]["score"] == results[scenario]["max_score"] and not results[scenario]["feedback"]:
            results[scenario]["feedback"].append("Excellent response that covers all required elements")
    
    # Calculate overall task score
    total_score = sum(scenario["score"] for scenario in results.values())
    max_score = sum(scenario["max_score"] for scenario in results.values())
    
    return {
        "scenarios": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100 if max_score > 0 else 0
    }

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Service Comparison Analysis."""
    results = {
        "credit_counseling": {
            "primary_benefit": {"score": 0, "max_score": 1, "feedback": []},
            "main_disadvantage": {"score": 0, "max_score": 1, "feedback": []},
            "typical_timeline": {"score": 0, "max_score": 1, "feedback": []},
            "credit_score_impact": {"score": 0, "max_score": 1, "feedback": []}
        },
        "debt_management_program": {
            "primary_benefit": {"score": 0, "max_score": 1, "feedback": []},
            "main_disadvantage": {"score": 0, "max_score": 1, "feedback": []},
            "typical_timeline": {"score": 0, "max_score": 1, "feedback": []},
            "credit_score_impact": {"score": 0, "max_score": 1, "feedback": []}
        },
        "debt_settlement": {
            "primary_benefit": {"score": 0, "max_score": 1, "feedback": []},
            "main_disadvantage": {"score": 0, "max_score": 1, "feedback": []},
            "typical_timeline": {"score": 0, "max_score": 1, "feedback": []},
            "credit_score_impact": {"score": 0, "max_score": 1, "feedback": []}
        }
    }
    
    # Check each service and field
    for service in results.keys():
        if service not in submission["task2"]:
            for field in results[service]:
                results[service][field]["feedback"].append("Missing service information")
            continue
            
        for field in results[service]:
            if field not in submission["task2"][service]:
                results[service][field]["feedback"].append("Missing field")
                continue
                
            candidate_answer = submission["task2"][service][field]
            key_answer = answer_key["task2"][service][field]
            
            # Check for substantial similarity
            if similarity_check(candidate_answer, key_answer):
                results[service][field]["score"] = 1
                results[service][field]["feedback"].append("Correct information")
            else:
                results[service][field]["feedback"].append("Information does not match reference answer")
    
    # Calculate overall task score
    total_score = 0
    max_score = 0
    
    for service in results:
        for field in results[service]:
            total_score += results[service][field]["score"]
            max_score += results[service][field]["max_score"]
    
    return {
        "services": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100 if max_score > 0 else 0
    }

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Program Rules Translation."""
    results = {
        "rule1": {"score": 0, "max_score": 10, "feedback": []},
        "rule2": {"score": 0, "max_score": 10, "feedback": []},
        "rule3": {"score": 0, "max_score": 10, "feedback": []}
    }
    
    # Key elements to check for in each rule translation
    key_elements = {
        "rule1": [
            "creditor concessions explained",
            "three consecutive payments requirement",
            "benefits mentioned",
            "plain language",
            "rationale explained"
        ],
        "rule2": [
            "pro-rata explained simply",
            "proportional distribution",
            "example provided",
            "fair treatment mentioned",
            "no technical jargon"
        ],
        "rule3": [
            "termination explained",
            "supervisory authorization explained",
            "rationale for rule",
            "client-friendly language",
            "constructive framing"
        ]
    }
    
    # Check each rule
    for rule, elements in key_elements.items():
        if rule not in submission["task3"]:
            results[rule]["feedback"].append("Missing response")
            continue
            
        explanation = submission["task3"][rule]
        if not explanation:
            results[rule]["feedback"].append("Missing explanation")
            continue
        
        # Check for jargon and technical terms
        jargon_terms = ["pro-rata", "concession eligibility", "supervisory authorization"]
        has_jargon = any(term in explanation.lower() for term in jargon_terms)
        
        if has_jargon:
            results[rule]["feedback"].append("Contains industry jargon")
        
        # Check for key elements
        found_elements = []
        for element in elements:
            if any(keyword in explanation.lower() for keyword in element.split()):
                found_elements.append(element)
        
        element_score = min(10, len(found_elements) * 2)
        results[rule]["score"] = element_score
        
        if len(found_elements) < len(elements):
            missing = set(elements) - set(found_elements)
            results[rule]["feedback"].append(f"Missing key elements: {', '.join(missing)}")
        
        # Add general feedback if score is perfect
        if results[rule]["score"] == results[rule]["max_score"] and not results[rule]["feedback"]:
            results[rule]["feedback"].append("Excellent translation that covers all required elements")
    
    # Calculate overall task score
    total_score = sum(rule["score"] for rule in results.values())
    max_score = sum(rule["max_score"] for rule in results.values())
    
    return {
        "rules": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100 if max_score > 0 else 0
    }

def similarity_check(text1, text2):
    """
    Check if two texts are substantially similar.
    This is a simplified implementation - in a real evaluation, 
    you might use more sophisticated NLP techniques.
    """
    # Convert to lowercase and tokenize
    words1 = Counter(re.findall(r'\b\w+\b', text1.lower()))
    words2 = Counter(re.findall(r'\b\w+\b', text2.lower()))
    
    # Find common words
    common_words = sum((words1 & words2).values())
    
    # Calculate similarity as percentage of common words relative to shorter text
    min_length = min(sum(words1.values()), sum(words2.values()))
    if min_length == 0:
        return False
    
    similarity = common_words / min_length
    
    # Consider texts similar if they share at least 40% of words
    return similarity >= 0.4

def evaluate_submission(submission_file, answer_key_file):
    """Evaluate the candidate's submission against the answer key."""
    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
        
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
        
        # Check word count requirements
        word_count_issues = check_word_count_requirements(submission)
        
        # Evaluate each task
        task1_results = evaluate_task1(submission, answer_key)
        task2_results = evaluate_task2(submission, answer_key)
        task3_results = evaluate_task3(submission, answer_key)
        
        # Calculate overall score with weighting
        # Task 1: 40%, Task 2: 30%, Task 3: 30%
        overall_percentage = (
            task1_results["percentage"] * 0.4 +
            task2_results["percentage"] * 0.3 +
            task3_results["percentage"] * 0.3
        )
        
        # Determine if candidate passed
        passed = overall_percentage >= 70 and (
            task1_results["percentage"] >= 60 and
            task2_results["percentage"] >= 60 and
            task3_results["percentage"] >= 60
        )
        
        # Prepare results
        results = {
            "candidate_id": submission.get("candidate_id", "Unknown"),
            "word_count_issues": word_count_issues,
            "task1_results": task1_results,
            "task2_results": task2_results,
            "task3_results": task3_results,
            "overall_score": overall_percentage,
            "passed": passed,
            "feedback": generate_overall_feedback(task1_results, task2_results, task3_results, overall_percentage, passed)
        }
        
        return results
        
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0,
            "passed": False
        }

def generate_overall_feedback(task1_results, task2_results, task3_results, overall_percentage, passed):
    """Generate overall feedback based on the evaluation results."""
    feedback = []
    
    # Add general assessment
    if overall_percentage >= 90:
        feedback.append("Excellent performance demonstrating strong client communication skills.")
    elif overall_percentage >= 80:
        feedback.append("Very good performance with solid understanding of credit counseling concepts.")
    elif overall_percentage >= 70:
        feedback.append("Good performance meeting the basic requirements for client communication.")
    else:
        feedback.append("Performance needs improvement to meet the standards for client communication.")
    
    # Add task-specific feedback
    if task1_results["percentage"] < 70:
        feedback.append("Needs improvement in explaining credit counseling concepts to clients.")
    
    if task2_results["percentage"] < 70:
        feedback.append("Needs improvement in comparing and contrasting different debt relief options.")
    
    if task3_results["percentage"] < 70:
        feedback.append("Needs improvement in translating technical program rules into client-friendly language.")
    
    # Add pass/fail statement
    if passed:
        feedback.append("PASSED: Candidate has demonstrated the basic skills required for explaining credit counseling services and policies to clients.")
    else:
        feedback.append("NOT PASSED: Candidate needs additional training before being ready to explain credit counseling services and policies to clients.")
    
    return feedback

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results to file
    with open("test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results.get('passed', False) else 'NOT PASSED'}")

if __name__ == "__main__":
    main()