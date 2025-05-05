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

def evaluate_scenario1(submission, answer_key):
    results = {
        "email_subject": {"score": 0, "max_score": 5, "comments": ""},
        "responsibilities": {"score": 0, "max_score": 10, "comments": ""},
        "working_conditions": {"score": 0, "max_score": 10, "comments": ""},
        "application_process": {"score": 0, "max_score": 10, "comments": ""},
        "professional_format": {"score": 0, "max_score": 5, "comments": ""}
    }
    
    # Check email subject
    if "email_subject" in submission["scenario1"]:
        subject = submission["scenario1"]["email_subject"]
        if "Marketing Specialist" in subject and "TechInnovate" in subject:
            results["email_subject"]["score"] = 5
            results["email_subject"]["comments"] = "Subject clearly indicates purpose and mentions position and company."
        elif "Marketing" in subject or "position" in subject.lower():
            results["email_subject"]["score"] = 3
            results["email_subject"]["comments"] = "Subject mentions position but lacks specificity."
        else:
            results["email_subject"]["score"] = 1
            results["email_subject"]["comments"] = "Subject lacks clarity about purpose."
    
    # Check email body for responsibilities
    if "email_body" in submission["scenario1"]:
        body = submission["scenario1"]["email_body"].lower()
        
        # Key responsibilities to check for
        responsibilities = [
            "social media",
            "metrics" or "analytics",
            "design team" or "marketing materials",
            "events" or "marketing events",
            "market research",
            "seo" or "sem",
            "product launch"
        ]
        
        found_resp = sum(1 for r in responsibilities if any(term in body for term in (r if isinstance(r, list) else [r])))
        
        if found_resp >= 7:
            results["responsibilities"]["score"] = 10
            results["responsibilities"]["comments"] = "All key responsibilities accurately conveyed."
        elif found_resp >= 5:
            results["responsibilities"]["score"] = 7
            results["responsibilities"]["comments"] = f"Included {found_resp}/7 key responsibilities."
        elif found_resp >= 3:
            results["responsibilities"]["score"] = 4
            results["responsibilities"]["comments"] = f"Included only {found_resp}/7 key responsibilities."
        else:
            results["responsibilities"]["score"] = 1
            results["responsibilities"]["comments"] = "Missing most key responsibilities."
        
        # Working conditions
        conditions = [
            "office-based" or "office based",
            "2 days" and "remote",
            "9 am" and "5 pm",
            "laptop" and "monitor",
            "open-plan" or "open plan"
        ]
        
        found_cond = sum(1 for c in conditions if any(term in body for term in (c if isinstance(c, list) else [c])))
        
        if found_cond >= 5:
            results["working_conditions"]["score"] = 10
            results["working_conditions"]["comments"] = "All working conditions accurately described."
        elif found_cond >= 3:
            results["working_conditions"]["score"] = 6
            results["working_conditions"]["comments"] = f"Included {found_cond}/5 working conditions."
        else:
            results["working_conditions"]["score"] = 3
            results["working_conditions"]["comments"] = "Missing most working conditions."
        
        # Application process
        process_steps = [
            "application review",
            "phone screening",
            "skills assessment" or "case study",
            "panel interview",
            "final interview" or "director",
            "reference" or "offer"
        ]
        
        found_steps = sum(1 for s in process_steps if any(term in body for term in (s if isinstance(s, list) else [s])))
        
        if found_steps >= 6:
            results["application_process"]["score"] = 10
            results["application_process"]["comments"] = "All application steps accurately described."
        elif found_steps >= 4:
            results["application_process"]["score"] = 7
            results["application_process"]["comments"] = f"Included {found_steps}/6 application steps."
        elif found_steps >= 2:
            results["application_process"]["score"] = 4
            results["application_process"]["comments"] = f"Included only {found_steps}/6 application steps."
        else:
            results["application_process"]["score"] = 1
            results["application_process"]["comments"] = "Missing most application steps."
        
        # Professional format
        has_greeting = "dear" in body or "hello" in body or "hi" in body
        has_closing = "regards" in body or "sincerely" in body or "thank you" in body
        well_organized = body.count("\n") >= 5  # Simple check for paragraphs/structure
        
        if has_greeting and has_closing and well_organized:
            results["professional_format"]["score"] = 5
            results["professional_format"]["comments"] = "Proper greeting, organization, and closing."
        elif (has_greeting or has_closing) and well_organized:
            results["professional_format"]["score"] = 3
            results["professional_format"]["comments"] = "Missing either greeting or closing, but well organized."
        else:
            results["professional_format"]["score"] = 1
            results["professional_format"]["comments"] = "Lacks professional email format."
    
    # Calculate total score for scenario 1
    total_score = sum(item["score"] for item in results.values())
    max_score = sum(item["max_score"] for item in results.values())
    
    return {
        "details": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 2)
    }

def evaluate_scenario2(submission, answer_key):
    results = {
        "compensation_summary": {"score": 0, "max_score": 15, "comments": ""},
        "benefits_summary": {"score": 0, "max_score": 15, "comments": ""},
        "schedule_summary": {"score": 0, "max_score": 10, "comments": ""}
    }
    
    # Check compensation summary
    if "compensation_summary" in submission["scenario2"]:
        comp_summary = submission["scenario2"]["compensation_summary"].lower()
        
        comp_elements = [
            "120,000" and "150,000",
            "15%" and "bonus",
            "10,000" and "signing",
            "2,000" and ("rsu" or "stock"),
            "profit sharing" and ("3" or "5%"),
            "annual" and "review",
            "7,500" and "relocation"
        ]
        
        found_comp = sum(1 for c in comp_elements if all(term in comp_summary for term in c if isinstance(c, tuple) else [c]))
        
        if found_comp >= 7:
            results["compensation_summary"]["score"] = 15
            results["compensation_summary"]["comments"] = "All compensation elements accurately included."
        elif found_comp >= 5:
            results["compensation_summary"]["score"] = 10
            results["compensation_summary"]["comments"] = f"Included {found_comp}/7 compensation elements."
        elif found_comp >= 3:
            results["compensation_summary"]["score"] = 6
            results["compensation_summary"]["comments"] = f"Included only {found_comp}/7 compensation elements."
        else:
            results["compensation_summary"]["score"] = 3
            results["compensation_summary"]["comments"] = "Missing most compensation elements."
    
    # Check benefits summary
    if "benefits_summary" in submission["scenario2"]:
        benefits_summary = submission["scenario2"]["benefits_summary"].lower()
        
        benefit_elements = [
            "90%" and "75%" and "health",
            "401" and "6%",
            "20" and "vacation" and "10" and "holiday" and "5" and "sick",
            "12 weeks" and "parental" and "4 weeks",
            "5,000" and "professional development",
            "50" and "wellness",
            "life" and "disability" and "2x",
            "employee assistance"
        ]
        
        found_benefits = sum(1 for b in benefit_elements if all(term in benefits_summary for term in b if isinstance(b, tuple) else [b]))
        
        if found_benefits >= 7:
            results["benefits_summary"]["score"] = 15
            results["benefits_summary"]["comments"] = "All benefits accurately described."
        elif found_benefits >= 5:
            results["benefits_summary"]["score"] = 10
            results["benefits_summary"]["comments"] = f"Included {found_benefits}/8 benefit elements."
        elif found_benefits >= 3:
            results["benefits_summary"]["score"] = 6
            results["benefits_summary"]["comments"] = f"Included only {found_benefits}/8 benefit elements."
        else:
            results["benefits_summary"]["score"] = 3
            results["benefits_summary"]["comments"] = "Missing most benefit elements."
    
    # Check schedule summary
    if "schedule_summary" in submission["scenario2"]:
        schedule_summary = submission["scenario2"]["schedule_summary"].lower()
        
        schedule_elements = [
            "10 am" and "3 pm" and "core hours",
            "flexible" and ("start" or "end"),
            "2 days" and "office",
            "time tracking" and "client",
            "evening" and "critical",
            "on-call" and "8 weeks",
            "stand-up" and "10:30" and "sprint"
        ]
        
        found_schedule = sum(1 for s in schedule_elements if all(term in schedule_summary for term in s if isinstance(s, tuple) else [s]))
        
        if found_schedule >= 6:
            results["schedule_summary"]["score"] = 10
            results["schedule_summary"]["comments"] = "All schedule aspects accurately conveyed."
        elif found_schedule >= 4:
            results["schedule_summary"]["score"] = 7
            results["schedule_summary"]["comments"] = f"Included {found_schedule}/7 schedule elements."
        elif found_schedule >= 2:
            results["schedule_summary"]["score"] = 4
            results["schedule_summary"]["comments"] = f"Included only {found_schedule}/7 schedule elements."
        else:
            results["schedule_summary"]["score"] = 1
            results["schedule_summary"]["comments"] = "Missing most schedule elements."
    
    # Calculate total score for scenario 2
    total_score = sum(item["score"] for item in results.values())
    max_score = sum(item["max_score"] for item in results.values())
    
    return {
        "details": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 2)
    }

def evaluate_scenario3(submission, answer_key):
    results = {
        "question1": {"score": 0, "max_score": 4, "comments": ""},
        "question2": {"score": 0, "max_score": 4, "comments": ""},
        "question3": {"score": 0, "max_score": 4, "comments": ""},
        "question4": {"score": 0, "max_score": 4, "comments": ""},
        "question5": {"score": 0, "max_score": 4, "comments": ""}
    }
    
    # Question 1: Next position level
    if "question1_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question1_answer"]
        correct = answer_key["scenario3"]["question1_answer"]
        
        if answer.lower() == correct.lower():
            results["question1"]["score"] = 4
            results["question1"]["comments"] = "Correct position identified."
        else:
            results["question1"]["score"] = 0
            results["question1"]["comments"] = f"Incorrect. Expected: {correct}"
    
    # Question 2: Years of experience
    if "question2_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question2_answer"]
        correct = answer_key["scenario3"]["question2_answer"]
        
        # Convert to string for comparison if needed
        if str(answer) == str(correct):
            results["question2"]["score"] = 4
            results["question2"]["comments"] = "Correct years of experience identified."
        else:
            results["question2"]["score"] = 0
            results["question2"]["comments"] = f"Incorrect. Expected: {correct}"
    
    # Question 3: Required certification
    if "question3_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question3_answer"].lower()
        correct = answer_key["scenario3"]["question3_answer"].lower()
        
        if "pmp" in answer and "aws" in answer and "solutions architect" in answer:
            results["question3"]["score"] = 4
            results["question3"]["comments"] = "Both required certifications correctly identified."
        elif "pmp" in answer or ("aws" in answer and "solutions architect" in answer):
            results["question3"]["score"] = 2
            results["question3"]["comments"] = "Only one of the required certifications identified."
        else:
            results["question3"]["score"] = 0
            results["question3"]["comments"] = f"Incorrect. Expected: {correct}"
    
    # Question 4: Salary increase percentage
    if "question4_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question4_answer"]
        correct = answer_key["scenario3"]["question4_answer"]
        
        # Clean up formatting for comparison
        answer_clean = re.sub(r'[^0-9\-]', '', answer)
        correct_clean = re.sub(r'[^0-9\-]', '', correct)
        
        if answer_clean == correct_clean:
            results["question4"]["score"] = 4
            results["question4"]["comments"] = "Correct percentage range identified."
        else:
            results["question4"]["score"] = 0
            results["question4"]["comments"] = f"Incorrect. Expected: {correct}"
    
    # Question 5: Core competencies
    if "question5_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question5_answer"]
        
        # Valid competencies from the materials
        valid_competencies = [
            "strategic planning",
            "financial management",
            "risk management",
            "stakeholder management",
            "team leadership"
        ]
        
        # Parse the answer and check if it contains exactly 3 valid competencies
        answer_comps = [comp.strip().lower() for comp in answer.split(',')]
        valid_answers = [comp for comp in answer_comps if any(valid_comp in comp for valid_comp in valid_competencies)]
        
        if len(valid_answers) == 3 and len(answer_comps) == 3:
            results["question5"]["score"] = 4
            results["question5"]["comments"] = "Correctly identified 3 core competencies."
        elif len(valid_answers) == 3 and len(answer_comps) > 3:
            results["question5"]["score"] = 2
            results["question5"]["comments"] = "Identified 3 valid competencies but listed more than required."
        elif len(valid_answers) > 0:
            results["question5"]["score"] = 1
            results["question5"]["comments"] = f"Only identified {len(valid_answers)} valid competencies out of 3 required."
        else:
            results["question5"]["score"] = 0
            results["question5"]["comments"] = "No valid competencies identified."
    
    # Calculate total score for scenario 3
    total_score = sum(item["score"] for item in results.values())
    max_score = sum(item["max_score"] for item in results.values())
    
    return {
        "details": results,
        "score": total_score,
        "max_score": max_score,
        "percentage": round((total_score / max_score) * 100, 2)
    }

def check_critical_errors(submission, answer_key, scenario_results):
    critical_errors = []
    
    # Check for significantly incorrect salary information
    if "compensation_summary" in submission["scenario2"]:
        comp_summary = submission["scenario2"]["compensation_summary"].lower()
        if not ("120,000" in comp_summary and "150,000" in comp_summary):
            if any(str(n) in comp_summary for n in range(70000, 110000)) or any(str(n) in comp_summary for n in range(160000, 200000)):
                critical_errors.append("Provided significantly incorrect salary information that would mislead applicants")
    
    # Check for omission of major job responsibilities
    if "email_body" in submission["scenario1"]:
        body = submission["scenario1"]["email_body"].lower()
        responsibilities = [
            "social media",
            "metrics" or "analytics",
            "design team" or "marketing materials",
            "events" or "marketing events",
            "market research",
            "seo" or "sem",
            "product launch"
        ]
        
        found_resp = sum(1 for r in responsibilities if any(term in body for term in (r if isinstance(r, list) else [r])))
        if found_resp < 4:  # Less than half of the responsibilities
            critical_errors.append("Omitted major job responsibilities that would give an incomplete picture of the role")
    
    # Check for incorrect certification information
    if "question3_answer" in submission["scenario3"]:
        answer = submission["scenario3"]["question3_answer"].lower()
        if not ("pmp" in answer and "aws" in answer and "solutions architect" in answer):
            critical_errors.append("Provided incorrect information about required certifications")
    
    return critical_errors

def evaluate_submission(submission, answer_key):
    # Evaluate each scenario
    scenario1_results = evaluate_scenario1(submission, answer_key)
    scenario2_results = evaluate_scenario2(submission, answer_key)
    scenario3_results = evaluate_scenario3(submission, answer_key)
    
    # Check for critical errors
    critical_errors = check_critical_errors(submission, answer_key, {
        "scenario1": scenario1_results,
        "scenario2": scenario2_results,
        "scenario3": scenario3_results
    })
    
    # Calculate overall score
    total_score = scenario1_results["score"] + scenario2_results["score"] + scenario3_results["score"]
    max_score = scenario1_results["max_score"] + scenario2_results["max_score"] + scenario3_results["max_score"]
    overall_percentage = round((total_score / max_score) * 100, 2)
    
    # Check if minimum section requirements are met
    section_requirements_met = (
        scenario1_results["score"] >= 25 and  # At least 25 points (62.5%) in Scenario 1
        scenario2_results["score"] >= 25 and  # At least 25 points (62.5%) in Scenario 2
        scenario3_results["score"] >= 12      # At least 12 points (60%) in Scenario 3
    )
    
    # Determine if candidate passed
    passed = overall_percentage >= 75 and section_requirements_met and not critical_errors
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_percentage,
        "passed": passed,
        "total_points": total_score,
        "max_points": max_score,
        "scenario1": scenario1_results,
        "scenario2": scenario2_results,
        "scenario3": scenario3_results,
        "section_requirements_met": section_requirements_met,
        "critical_errors": critical_errors
    }
    
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")

if __name__ == "__main__":
    main()