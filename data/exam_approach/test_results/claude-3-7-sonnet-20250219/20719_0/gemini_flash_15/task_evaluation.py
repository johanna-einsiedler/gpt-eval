#!/usr/bin/env python3
import json
import sys
import re
from datetime import datetime

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def evaluate_format_requirements(submission, answer_key):
    score = 0
    max_score = 20
    feedback = []
    
    # Check JSON structure
    required_fields = ["candidate_id", "report"]
    report_fields = ["case_number", "report_date", "complaint_summary", "allegations", 
                     "findings_summary", "procedural_actions"]
    
    # Check top-level fields
    for field in required_fields:
        if field in submission:
            score += 1
            feedback.append(f"✓ Included required field: {field}")
        else:
            feedback.append(f"✗ Missing required field: {field}")
    
    # Check report fields
    if "report" in submission:
        for field in report_fields:
            if field in submission["report"]:
                score += 1
                feedback.append(f"✓ Included required report field: {field}")
            else:
                feedback.append(f"✗ Missing required report field: {field}")
    
    # Check case number
    if "report" in submission and "case_number" in submission["report"]:
        if submission["report"]["case_number"] == answer_key["report"]["case_number"]:
            score += 1
            feedback.append("✓ Case number is correct")
        else:
            feedback.append("✗ Case number is incorrect")
    
    # Check date format
    if "report" in submission and "report_date" in submission["report"]:
        if validate_date_format(submission["report"]["report_date"]):
            score += 1
            feedback.append("✓ Report date format is correct (YYYY-MM-DD)")
        else:
            feedback.append("✗ Report date format is incorrect (should be YYYY-MM-DD)")
    
    # Check word counts
    if "report" in submission:
        if "complaint_summary" in submission["report"]:
            word_count = count_words(submission["report"]["complaint_summary"])
            if 150 <= word_count <= 300:
                score += 1
                feedback.append(f"✓ Complaint summary word count is within limits ({word_count} words)")
            else:
                feedback.append(f"✗ Complaint summary word count is outside limits: {word_count} words (should be 150-300)")
        
        if "findings_summary" in submission["report"]:
            word_count = count_words(submission["report"]["findings_summary"])
            if 150 <= word_count <= 300:
                score += 1
                feedback.append(f"✓ Findings summary word count is within limits ({word_count} words)")
            else:
                feedback.append(f"✗ Findings summary word count is outside limits: {word_count} words (should be 150-300)")
    
    # Check allegations format
    if "report" in submission and "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
        allegation = submission["report"]["allegations"][0]
        
        # Check allegation fields
        allegation_fields = ["allegation_number", "protected_category", "allegation_description", 
                            "relevant_evidence", "applicable_regulations"]
        for field in allegation_fields:
            if field in allegation:
                score += 0.5
                feedback.append(f"✓ Allegation includes required field: {field}")
            else:
                feedback.append(f"✗ Allegation missing required field: {field}")
        
        # Check allegation description word count
        if "allegation_description" in allegation:
            word_count = count_words(allegation["allegation_description"])
            if 100 <= word_count <= 200:
                score += 1
                feedback.append(f"✓ Allegation description word count is within limits ({word_count} words)")
            else:
                feedback.append(f"✗ Allegation description word count is outside limits: {word_count} words (should be 100-200)")
        
        # Check relevant_evidence format (should have line breaks)
        if "relevant_evidence" in allegation:
            if "\n" in allegation["relevant_evidence"]:
                score += 1
                feedback.append("✓ Relevant evidence formatted with line breaks")
            else:
                feedback.append("✗ Relevant evidence should be formatted with line breaks (\\n)")
        
        # Check applicable_regulations format
        if "applicable_regulations" in allegation and isinstance(allegation["applicable_regulations"], list):
            if all(isinstance(reg, str) for reg in allegation["applicable_regulations"]):
                score += 1
                feedback.append("✓ Applicable regulations formatted correctly as a list of strings")
            else:
                feedback.append("✗ Applicable regulations should be a list of strings")
    
    # Check procedural_actions format
    if "report" in submission and "procedural_actions" in submission["report"]:
        if isinstance(submission["report"]["procedural_actions"], list):
            if all(isinstance(action, str) for action in submission["report"]["procedural_actions"]):
                score += 1
                feedback.append("✓ Procedural actions formatted correctly as a list of strings")
            else:
                feedback.append("✗ Procedural actions should be a list of strings")
    
    # Calculate percentage score
    percentage_score = (score / max_score) * 100
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage_score,
        "feedback": feedback
    }

def evaluate_content_accuracy(submission, answer_key):
    score = 0
    max_score = 50
    feedback = []
    
    # Check protected category
    if "report" in submission and "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
        if "protected_category" in submission["report"]["allegations"][0]:
            submitted_category = submission["report"]["allegations"][0]["protected_category"].lower()
            expected_category = answer_key["report"]["allegations"][0]["protected_category"].lower()
            
            if submitted_category == expected_category:
                score += 10
                feedback.append("✓ Correctly identified 'Family Status' as the protected category")
            else:
                feedback.append(f"✗ Incorrectly identified protected category as '{submission['report']['allegations'][0]['protected_category']}' instead of 'Family Status'")
                # Critical error - automatic failure
                feedback.append("CRITICAL ERROR: Identifying the wrong protected category")
    
    # Check applicable regulations
    if "report" in submission and "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
        if "applicable_regulations" in submission["report"]["allegations"][0]:
            submitted_regs = set(submission["report"]["allegations"][0]["applicable_regulations"])
            expected_regs = set(answer_key["report"]["allegations"][0]["applicable_regulations"])
            
            # Check for the three key regulations
            key_regs = {"Reg-AGY-001", "Reg-AGY-005", "Reg-AGY-006"}
            found_key_regs = key_regs.intersection(submitted_regs)
            
            if len(found_key_regs) == 3:
                score += 10
                feedback.append("✓ Referenced all three key agency regulations (Reg-AGY-001, 005, and 006)")
            elif len(found_key_regs) >= 2:
                score += 5
                feedback.append(f"◑ Referenced {len(found_key_regs)} of 3 key agency regulations")
            else:
                feedback.append("✗ Failed to reference key agency regulations")
    
    # Check relevant evidence
    key_evidence_points = [
        "family situation",
        "availability constraints",
        "performance review",
        "lisa chen",
        "witness",
        "email",
        "travel records",
        "comparison matrix"
    ]
    
    if "report" in submission and "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
        if "relevant_evidence" in submission["report"]["allegations"][0]:
            evidence_text = submission["report"]["allegations"][0]["relevant_evidence"].lower()
            
            found_evidence = 0
            for point in key_evidence_points:
                if point in evidence_text:
                    found_evidence += 1
                    feedback.append(f"✓ Included evidence point: {point}")
                else:
                    feedback.append(f"✗ Missing evidence point: {point}")
            
            if found_evidence >= 6:
                score += 15
                feedback.append(f"✓ Included {found_evidence} of 8 key evidence points")
            elif found_evidence >= 4:
                score += 10
                feedback.append(f"◑ Included {found_evidence} of 8 key evidence points")
            else:
                feedback.append(f"✗ Included only {found_evidence} of 8 key evidence points")
                if found_evidence < 3:
                    # Critical error - automatic failure
                    feedback.append("CRITICAL ERROR: Failing to include key evidence that supports the allegation")
    
    # Check procedural actions
    key_procedural_actions = [
        "complaint filed",
        "interview with complainant",
        "interview with respondent",
        "interview with witness lisa chen",
        "interview with witness robert johnson",
        "review of job posting",
        "review of candidate comparison",
        "review of performance review",
        "review of email",
        "analysis of travel records"
    ]
    
    if "report" in submission and "procedural_actions" in submission["report"]:
        actions_text = " ".join(submission["report"]["procedural_actions"]).lower()
        
        found_actions = 0
        for action in key_procedural_actions:
            if action in actions_text:
                found_actions += 1
                feedback.append(f"✓ Included procedural action: {action}")
            else:
                feedback.append(f"✗ Missing procedural action: {action}")
        
        if found_actions >= 8:
            score += 10
            feedback.append(f"✓ Included {found_actions} of 10 key procedural actions")
        elif found_actions >= 6:
            score += 5
            feedback.append(f"◑ Included {found_actions} of 10 key procedural actions")
        else:
            feedback.append(f"✗ Included only {found_actions} of 10 key procedural actions")
    
    # Check findings summary for balanced presentation
    if "report" in submission and "findings_summary" in submission["report"]:
        findings_text = submission["report"]["findings_summary"].lower()
        
        # Check for balanced presentation
        has_complainant_perspective = any(term in findings_text for term in ["morgan", "complainant", "allegation"])
        has_respondent_perspective = any(term in findings_text for term in ["wilson", "respondent", "denied"])
        has_qualification_mention = any(term in findings_text for term in ["qualification", "technical", "score", "experience"])
        
        if has_complainant_perspective and has_respondent_perspective and has_qualification_mention:
            score += 5
            feedback.append("✓ Findings summary presents a balanced view including both perspectives and qualification factors")
        elif has_complainant_perspective and has_respondent_perspective:
            score += 3
            feedback.append("◑ Findings summary includes both perspectives but lacks discussion of qualification factors")
        else:
            feedback.append("✗ Findings summary lacks balanced presentation of perspectives")
    
    # Calculate percentage score
    percentage_score = (score / max_score) * 100
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage_score,
        "feedback": feedback
    }

def evaluate_professional_quality(submission, answer_key):
    score = 0
    max_score = 30
    feedback = []
    
    # Check for objectivity
    if "report" in submission:
        # Check complaint summary for objectivity
        if "complaint_summary" in submission["report"]:
            complaint_text = submission["report"]["complaint_summary"].lower()
            biased_terms = ["clearly", "obviously", "definitely", "without doubt", "certainly", "discriminated", "violated", "illegal"]
            
            found_biased_terms = [term for term in biased_terms if term in complaint_text]
            if not found_biased_terms:
                score += 5
                feedback.append("✓ Complaint summary maintains objectivity")
            else:
                feedback.append(f"✗ Complaint summary contains potentially biased terms: {', '.join(found_biased_terms)}")
        
        # Check findings summary for objectivity
        if "findings_summary" in submission["report"]:
            findings_text = submission["report"]["findings_summary"].lower()
            conclusion_terms = ["conclude", "conclusion", "determined", "guilty", "innocent", "violated", "discriminated against"]
            
            found_conclusion_terms = [term for term in conclusion_terms if term in findings_text]
            if not found_conclusion_terms:
                score += 5
                feedback.append("✓ Findings summary avoids making definitive conclusions")
            else:
                feedback.append(f"✗ Findings summary makes definitive conclusions: {', '.join(found_conclusion_terms)}")
                # Check for critical error
                if any(term in findings_text for term in ["guilty", "violated", "discriminated against"]):
                    feedback.append("CRITICAL ERROR: Making definitive conclusions about discrimination that go beyond evidence presentation")
    
    # Check for fictional details
    if "report" in submission:
        fictional_indicators = [
            "not mentioned in case materials",
            "additional investigation",
            "further interviews",
            "recommended actions",
            "disciplinary"
        ]
        
        all_text = ""
        if "complaint_summary" in submission["report"]:
            all_text += submission["report"]["complaint_summary"].lower() + " "
        
        if "findings_summary" in submission["report"]:
            all_text += submission["report"]["findings_summary"].lower() + " "
        
        if "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
            if "allegation_description" in submission["report"]["allegations"][0]:
                all_text += submission["report"]["allegations"][0]["allegation_description"].lower() + " "
            
            if "relevant_evidence" in submission["report"]["allegations"][0]:
                all_text += submission["report"]["allegations"][0]["relevant_evidence"].lower() + " "
        
        found_fictional = [term for term in fictional_indicators if term in all_text]
        if not found_fictional:
            score += 5
            feedback.append("✓ Report avoids adding fictional details not in case materials")
        else:
            feedback.append(f"✗ Report may contain fictional details: {', '.join(found_fictional)}")
            # Critical error
            feedback.append("CRITICAL ERROR: Adding fictional details not present in the case materials")
    
    # Check for logical organization
    if "report" in submission and "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
        if "relevant_evidence" in submission["report"]["allegations"][0]:
            evidence_text = submission["report"]["allegations"][0]["relevant_evidence"]
            evidence_points = evidence_text.split("\n")
            
            if len(evidence_points) >= 5:
                score += 5
                feedback.append("✓ Evidence is organized in a logical, structured manner")
            elif len(evidence_points) >= 3:
                score += 3
                feedback.append("◑ Evidence has some structure but could be more organized")
            else:
                feedback.append("✗ Evidence lacks logical organization")
    
    # Check for professional language
    if "report" in submission:
        unprofessional_terms = ["terrible", "awful", "ridiculous", "stupid", "idiot", "incompetent", "bad", "good", "best", "worst"]
        
        all_text = ""
        if "complaint_summary" in submission["report"]:
            all_text += submission["report"]["complaint_summary"].lower() + " "
        
        if "findings_summary" in submission["report"]:
            all_text += submission["report"]["findings_summary"].lower() + " "
        
        if "allegations" in submission["report"] and len(submission["report"]["allegations"]) > 0:
            if "allegation_description" in submission["report"]["allegations"][0]:
                all_text += submission["report"]["allegations"][0]["allegation_description"].lower() + " "
        
        found_unprofessional = [term for term in unprofessional_terms if term in all_text.split()]
        if not found_unprofessional:
            score += 5
            feedback.append("✓ Report uses professional, neutral language")
        else:
            feedback.append(f"✗ Report contains unprofessional language: {', '.join(found_unprofessional)}")
    
    # Check for inclusion of respondent's perspective
    if "report" in submission:
        respondent_indicators = ["wilson", "respondent", "denied", "explained", "stated"]
        
        respondent_mentioned = False
        if "findings_summary" in submission["report"]:
            findings_text = submission["report"]["findings_summary"].lower()
            respondent_mentioned = any(term in findings_text for term in respondent_indicators)
        
        if respondent_mentioned:
            score += 5
            feedback.append("✓ Report includes the respondent's perspective")
        else:
            feedback.append("✗ Report omits the respondent's perspective")
            # Critical error
            feedback.append("CRITICAL ERROR: Omitting the respondent's perspective entirely")
    
    # Calculate percentage score
    percentage_score = (score / max_score) * 100
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage_score,
        "feedback": feedback
    }

def check_for_critical_errors(results):
    critical_errors = []
    
    for category in ["format_requirements", "content_accuracy", "professional_quality"]:
        for feedback_item in results[category]["feedback"]:
            if feedback_item.startswith("CRITICAL ERROR:"):
                critical_errors.append(feedback_item)
    
    return critical_errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each category
    format_results = evaluate_format_requirements(submission, answer_key)
    content_results = evaluate_content_accuracy(submission, answer_key)
    quality_results = evaluate_professional_quality(submission, answer_key)
    
    # Check for critical errors
    results = {
        "format_requirements": format_results,
        "content_accuracy": content_results,
        "professional_quality": quality_results
    }
    
    critical_errors = check_for_critical_errors(results)
    
    # Calculate overall score
    total_score = format_results["score"] + content_results["score"] + quality_results["score"]
    total_max = format_results["max_score"] + content_results["max_score"] + quality_results["max_score"]
    overall_percentage = (total_score / total_max) * 100
    
    # Check if passing criteria are met
    passed_format = format_results["percentage"] >= 70
    passed_content = content_results["percentage"] >= 70
    passed_quality = quality_results["percentage"] >= 70
    passed_overall = overall_percentage >= 75
    
    passed = passed_format and passed_content and passed_quality and passed_overall and not critical_errors
    
    # Prepare final results
    final_results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_percentage,
        "passed": passed,
        "critical_errors": critical_errors,
        "category_scores": {
            "format_requirements": {
                "score": format_results["score"],
                "max_score": format_results["max_score"],
                "percentage": format_results["percentage"],
                "passed": passed_format
            },
            "content_accuracy": {
                "score": content_results["score"],
                "max_score": content_results["max_score"],
                "percentage": content_results["percentage"],
                "passed": passed_content
            },
            "professional_quality": {
                "score": quality_results["score"],
                "max_score": quality_results["max_score"],
                "percentage": quality_results["percentage"],
                "passed": passed_quality
            }
        },
        "detailed_feedback": {
            "format_requirements": format_results["feedback"],
            "content_accuracy": content_results["feedback"],
            "professional_quality": quality_results["feedback"]
        }
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {overall_percentage:.2f}%")
    print(f"Result: {'PASSED' if passed else 'FAILED'}")
    if critical_errors:
        print("Critical errors found:")
        for error in critical_errors:
            print(f"  - {error}")

if __name__ == "__main__":
    main()