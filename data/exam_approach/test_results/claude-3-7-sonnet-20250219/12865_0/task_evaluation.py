import json
import math
import re
from difflib import SequenceMatcher

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json_file(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Successfully saved {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def is_close(val1, val2, tolerance=0.01):
    """Check if two numerical values are close within tolerance"""
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) <= tolerance
    return val1 == val2

def text_similarity(text1, text2):
    """Calculate similarity between two text strings"""
    if not text1 or not text2:
        return 0
    return SequenceMatcher(None, text1, text2).ratio()

def contains_key_elements(text, key_elements, threshold=0.7):
    """Check if text contains required key elements"""
    if not text:
        return False
    
    text = text.lower()
    count = 0
    for element in key_elements:
        if element.lower() in text:
            count += 1
    
    return count / len(key_elements) >= threshold

def evaluate_task1(submission, answer_key):
    score = 0
    feedback = []
    
    # Check festival commission calculation (5 points)
    try:
        festival = next((calc for calc in submission["commission_calculations"] 
                         if calc["performance_type"] == "Festival appearance"), None)
        answer_festival = next((calc for calc in answer_key["commission_calculations"] 
                               if calc["performance_type"] == "Festival appearance"), None)
        
        if festival and answer_festival:
            if is_close(festival["commission_amount"], answer_festival["commission_amount"]):
                score += 5
                feedback.append("Correct festival commission calculation: +5 points")
            else:
                feedback.append(f"Incorrect festival commission calculation. Expected: {answer_festival['commission_amount']}, Got: {festival['commission_amount']}")
        else:
            feedback.append("Missing festival commission calculation")
    except Exception as e:
        feedback.append(f"Error evaluating festival commission: {e}")
    
    # Check endorsement deal commission (7 points)
    try:
        endorsement = next((calc for calc in submission["commission_calculations"] 
                           if calc["performance_type"] == "Brand endorsement deal"), None)
        answer_endorsement = next((calc for calc in answer_key["commission_calculations"] 
                                  if calc["performance_type"] == "Brand endorsement deal"), None)
        
        if endorsement and answer_endorsement:
            if is_close(endorsement["total_commission"], answer_endorsement["total_commission"]):
                score += 7
                feedback.append("Correct endorsement deal commission calculation: +7 points")
            else:
                feedback.append(f"Incorrect endorsement commission calculation. Expected: {answer_endorsement['total_commission']}, Got: {endorsement['total_commission']}")
        else:
            feedback.append("Missing endorsement deal commission calculation")
    except Exception as e:
        feedback.append(f"Error evaluating endorsement commission: {e}")
    
    # Check streaming royalty commission (5 points)
    try:
        streaming = next((calc for calc in submission["commission_calculations"] 
                         if calc["performance_type"] == "Streaming royalty payment"), None)
        answer_streaming = next((calc for calc in answer_key["commission_calculations"] 
                               if calc["performance_type"] == "Streaming royalty payment"), None)
        
        if streaming and answer_streaming:
            if is_close(streaming["commission_amount"], answer_streaming["commission_amount"]):
                score += 5
                feedback.append("Correct streaming royalty commission calculation: +5 points")
            else:
                feedback.append(f"Incorrect streaming royalty calculation. Expected: {answer_streaming['commission_amount']}, Got: {streaming['commission_amount']}")
        else:
            feedback.append("Missing streaming royalty commission calculation")
    except Exception as e:
        feedback.append(f"Error evaluating streaming royalty commission: {e}")
    
    # Check explanation with contract clause references (3 points)
    try:
        explanation = submission.get("explanation", "")
        if explanation:
            # Check for contract clause references
            has_clauses = re.search(r'clause [0-9\.]+', explanation.lower()) is not None
            
            # Check for explanation quality
            key_terms = ["festival", "endorsement", "tiered", "streaming", "platform fee"]
            has_key_terms = contains_key_elements(explanation, key_terms)
            
            if has_clauses and has_key_terms:
                score += 3
                feedback.append("Clear explanation with contract clause references: +3 points")
            elif has_clauses:
                score += 1.5
                feedback.append("Explanation includes contract clauses but lacks detail: +1.5 points")
            elif has_key_terms:
                score += 1.5
                feedback.append("Explanation has good detail but lacks contract clause references: +1.5 points")
            else:
                feedback.append("Explanation lacks both detail and contract clause references")
        else:
            feedback.append("Missing explanation")
    except Exception as e:
        feedback.append(f"Error evaluating explanation: {e}")
    
    return score, feedback

def evaluate_task2(submission, answer_key):
    score = 0
    feedback = []
    
    # Check identification of discrepancies (6 points)
    try:
        discrepancies = submission.get("discrepancies", [])
        answer_discrepancies = answer_key.get("discrepancies", [])
        
        if len(discrepancies) == 3:
            # Check each discrepancy is correctly identified
            events = [d.get("event") for d in discrepancies]
            answer_events = [d.get("event") for d in answer_discrepancies]
            
            correct_events = 0
            for event in answer_events:
                if event in events:
                    correct_events += 1
            
            points = (correct_events / 3) * 6
            score += points
            if points == 6:
                feedback.append("Correctly identified all three discrepancies: +6 points")
            else:
                feedback.append(f"Identified {correct_events}/3 discrepancies correctly: +{points} points")
        else:
            feedback.append(f"Expected 3 discrepancies, found {len(discrepancies)}")
    except Exception as e:
        feedback.append(f"Error evaluating discrepancy identification: {e}")
    
    # Check calculation of commission impacts (6 points)
    try:
        correct_impacts = 0
        for discrepancy in discrepancies:
            event = discrepancy.get("event")
            answer_discrepancy = next((d for d in answer_discrepancies if d.get("event") == event), None)
            
            if answer_discrepancy and is_close(discrepancy.get("commission_impact", 0), 
                                              answer_discrepancy.get("commission_impact", 0)):
                correct_impacts += 1
        
        points = (correct_impacts / 3) * 6
        score += points
        if points == 6:
            feedback.append("Correctly calculated all commission impacts: +6 points")
        else:
            feedback.append(f"Calculated {correct_impacts}/3 commission impacts correctly: +{points} points")
    except Exception as e:
        feedback.append(f"Error evaluating commission impacts: {e}")
    
    # Check resolution steps (8 points)
    try:
        resolution_steps = submission.get("resolution_steps", "")
        
        if resolution_steps:
            # Check for key elements in resolution steps
            key_elements = ["contact", "verify", "document", "follow up", "email", "contract", "record"]
            quality_score = 0
            
            # Check word count (200-400 words expected)
            word_count = len(resolution_steps.split())
            if 200 <= word_count <= 400:
                quality_score += 2
            elif 150 <= word_count < 200 or 400 < word_count <= 450:
                quality_score += 1
            
            # Check for key elements
            element_count = sum(1 for element in key_elements if element in resolution_steps.lower())
            element_score = min(6, (element_count / len(key_elements)) * 6)
            quality_score += element_score
            
            score += quality_score
            feedback.append(f"Resolution steps quality: +{quality_score} points out of 8")
        else:
            feedback.append("Missing resolution steps")
    except Exception as e:
        feedback.append(f"Error evaluating resolution steps: {e}")
    
    return score, feedback

def evaluate_task3(submission, answer_key):
    score = 0
    feedback = []
    
    # Check payment schedule completeness (10 points)
    try:
        schedule = submission.get("payment_schedule", [])
        answer_schedule = answer_key.get("payment_schedule", [])
        
        # Check if all required projects are included
        expected_projects = set(item["project_name"] for item in answer_schedule)
        found_projects = set(item["project_name"] for item in schedule)
        
        project_coverage = len(found_projects.intersection(expected_projects)) / len(expected_projects)
        project_points = project_coverage * 5
        score += project_points
        
        if project_points == 5:
            feedback.append("All required projects included in schedule: +5 points")
        else:
            feedback.append(f"Schedule includes {project_coverage*100:.0f}% of required projects: +{project_points} points")
        
        # Check payment details accuracy
        correct_details = 0
        total_details = 0
        
        for answer_item in answer_schedule:
            project = answer_item["project_name"]
            payment_type = answer_item["payment_type"]
            
            matching_items = [item for item in schedule 
                             if item.get("project_name") == project and item.get("payment_type") == payment_type]
            
            if matching_items:
                item = matching_items[0]
                # Check amount, commission rate, and commission amount
                if is_close(item.get("amount", 0), answer_item.get("amount", 0)):
                    correct_details += 1
                total_details += 1
                
                if is_close(item.get("commission_rate", 0), answer_item.get("commission_rate", 0)):
                    correct_details += 1
                total_details += 1
                
                if is_close(item.get("commission_amount", 0), answer_item.get("commission_amount", 0)):
                    correct_details += 1
                total_details += 1
        
        if total_details > 0:
            detail_points = (correct_details / total_details) * 5
            score += detail_points
            feedback.append(f"Payment details accuracy: {correct_details}/{total_details} correct: +{detail_points} points")
        else:
            feedback.append("Could not evaluate payment details")
    except Exception as e:
        feedback.append(f"Error evaluating payment schedule: {e}")
    
    # Check prioritization and organization (5 points)
    try:
        # Check if deposits are marked as high priority
        deposits = [item for item in schedule if "deposit" in item.get("payment_type", "").lower()]
        high_priority_deposits = [item for item in deposits if "high" in item.get("priority_level", "").lower()]
        
        if deposits and len(high_priority_deposits) / len(deposits) >= 0.8:
            score += 2.5
            feedback.append("Correctly prioritized deposits as high priority: +2.5 points")
        elif deposits and len(high_priority_deposits) / len(deposits) >= 0.5:
            score += 1.5
            feedback.append("Some deposits correctly prioritized: +1.5 points")
        else:
            feedback.append("Deposits not correctly prioritized")
        
        # Check chronological organization
        is_chronological = True
        last_date = None
        
        for item in sorted(schedule, key=lambda x: x.get("due_date", "")):
            current_date = item.get("due_date", "")
            if last_date and current_date < last_date:
                is_chronological = False
                break
            last_date = current_date
        
        if is_chronological:
            score += 2.5
            feedback.append("Schedule is properly organized chronologically: +2.5 points")
        else:
            feedback.append("Schedule is not properly organized chronologically")
    except Exception as e:
        feedback.append(f"Error evaluating prioritization: {e}")
    
    # Check collection strategy (5 points)
    try:
        strategy = submission.get("collection_strategy", "")
        
        if strategy:
            # Check for key elements in strategy
            key_elements = ["priority", "deposit", "reminder", "follow up", "track", "schedule", "communication"]
            quality_score = 0
            
            # Check word count (200-400 words expected)
            word_count = len(strategy.split())
            if 200 <= word_count <= 400:
                quality_score += 2
            elif 150 <= word_count < 200 or 400 < word_count <= 450:
                quality_score += 1
            
            # Check for key elements
            element_count = sum(1 for element in key_elements if element in strategy.lower())
            element_score = min(3, (element_count / len(key_elements)) * 3)
            quality_score += element_score
            
            score += quality_score
            feedback.append(f"Collection strategy quality: +{quality_score} points out of 5")
        else:
            feedback.append("Missing collection strategy")
    except Exception as e:
        feedback.append(f"Error evaluating collection strategy: {e}")
    
    return score, feedback

def evaluate_task4(submission, answer_key):
    score = 0
    feedback = []
    
    # Check initial collection email (10 points)
    try:
        email = submission.get("collection_email", "")
        answer_email = answer_key.get("collection_email", "")
        
        if email:
            # Check for required elements
            required_elements = [
                "FilmVision", "Gala", "payment", "due", "September 15", 
                "$35,000", "15 days", "invoice", "contract"
            ]
            
            element_count = sum(1 for element in required_elements if element.lower() in email.lower())
            element_score = min(6, (element_count / len(required_elements)) * 6)
            
            # Check tone and professionalism
            tone_score = 0
            if "please" in email.lower() and "thank you" in email.lower():
                tone_score += 2
            
            if "best regards" in email.lower() or "sincerely" in email.lower():
                tone_score += 1
            
            if not any(term in email.lower() for term in ["angry", "frustrated", "disappointed", "demand"]):
                tone_score += 1
            
            email_score = element_score + tone_score
            score += email_score
            
            feedback.append(f"Initial collection email quality: +{email_score} points out of 10")
            feedback.append(f"  - Required elements: {element_count}/{len(required_elements)}")
            feedback.append(f"  - Tone and professionalism: {tone_score}/4")
        else:
            feedback.append("Missing initial collection email")
    except Exception as e:
        feedback.append(f"Error evaluating initial email: {e}")
    
    # Check follow-up email (10 points)
    try:
        follow_up = submission.get("follow_up_email", "")
        answer_follow_up = answer_key.get("follow_up_email", "")
        
        if follow_up:
            # Check for required elements
            required_elements = [
                "FilmVision", "Gala", "45 days", "past due", "late", "fee", 
                "1.5%", "interest", "escalate", "urgent"
            ]
            
            element_count = sum(1 for element in required_elements if element.lower() in follow_up.lower())
            element_score = min(6, (element_count / len(required_elements)) * 6)
            
            # Check escalation and professionalism
            escalation_score = 0
            
            if any(term in follow_up.lower() for term in ["escalate", "urgent", "immediate"]):
                escalation_score += 2
            
            if "business relationship" in follow_up.lower() or "professional" in follow_up.lower():
                escalation_score += 1
            
            if "7 business days" in follow_up.lower() or "7 days" in follow_up.lower():
                escalation_score += 1
            
            follow_up_score = element_score + escalation_score
            score += follow_up_score
            
            feedback.append(f"Follow-up email quality: +{follow_up_score} points out of 10")
            feedback.append(f"  - Required elements: {element_count}/{len(required_elements)}")
            feedback.append(f"  - Escalation and professionalism: {escalation_score}/4")
        else:
            feedback.append("Missing follow-up email")
    except Exception as e:
        feedback.append(f"Error evaluating follow-up email: {e}")
    
    return score, feedback

def evaluate_task5(submission, answer_key):
    score = 0
    feedback = []
    
    # Check payment log accuracy (12 points)
    try:
        log = submission.get("payment_log", [])
        answer_log = answer_key.get("payment_log", [])
        
        if len(log) == 5:
            # Check each payment entry
            correct_entries = 0
            total_checks = 0
            
            for answer_entry in answer_log:
                payment_id = answer_entry.get("payment_id")
                entry = next((e for e in log if e.get("payment_id") == payment_id), None)
                
                if entry:
                    # Check key fields
                    fields_to_check = [
                        "date_received", "source", "contracted_amount", "actual_amount", 
                        "commission_rate", "commission_amount", "payment_method", "status"
                    ]
                    
                    for field in fields_to_check:
                        if field in entry and field in answer_entry:
                            if isinstance(entry[field], (int, float)) and isinstance(answer_entry[field], (int, float)):
                                if is_close(entry[field], answer_entry[field]):
                                    correct_entries += 1
                            elif entry[field] == answer_entry[field]:
                                correct_entries += 1
                            total_checks += 1
            
            if total_checks > 0:
                log_points = min(12, (correct_entries / total_checks) * 12)
                score += log_points
                feedback.append(f"Payment log accuracy: {correct_entries}/{total_checks} correct fields: +{log_points} points")
            else:
                feedback.append("Could not evaluate payment log fields")
        else:
            feedback.append(f"Expected 5 payment log entries, found {len(log)}")
    except Exception as e:
        feedback.append(f"Error evaluating payment log: {e}")
    
    # Check reconciliation notes (8 points)
    try:
        notes = submission.get("reconciliation_notes", "")
        
        if notes:
            # Check for key elements in notes
            key_elements = [
                "late", "platform fee", "tiered", "commission", "follow up", 
                "shortfall", "partial payment", "discrepancy"
            ]
            
            # Check word count (200-400 words expected)
            word_count = len(notes.split())
            word_score = 0
            if 200 <= word_count <= 400:
                word_score = 2
            elif 150 <= word_count < 200 or 400 < word_count <= 450:
                word_score = 1
            
            # Check for key elements
            element_count = sum(1 for element in key_elements if element in notes.lower())
            element_score = min(4, (element_count / len(key_elements)) * 4)
            
            # Check for recommendations
            recommendation_score = 0
            if any(term in notes.lower() for term in ["recommend", "suggest", "implement", "follow up"]):
                recommendation_score = 2
            
            notes_score = word_score + element_score + recommendation_score
            score += notes_score
            
            feedback.append(f"Reconciliation notes quality: +{notes_score} points out of 8")
            feedback.append(f"  - Word count ({word_count}): {word_score}/2")
            feedback.append(f"  - Key elements: {element_count}/{len(key_elements)}: {element_score}/4")
            feedback.append(f"  - Recommendations: {recommendation_score}/2")
        else:
            feedback.append("Missing reconciliation notes")
    except Exception as e:
        feedback.append(f"Error evaluating reconciliation notes: {e}")
    
    return score, feedback

def evaluate_submission(submission, answer_key):
    results = {
        "overall_score": 0,
        "total_points": 100,
        "passing_threshold": 70,
        "tasks": {}
    }
    
    # Task 1: Contract Interpretation (20 points)
    score1, feedback1 = evaluate_task1(submission.get("task1", {}), answer_key.get("task1", {}))
    results["tasks"]["task1"] = {
        "score": score1,
        "max_points": 20,
        "percentage": (score1 / 20) * 100,
        "feedback": feedback1
    }
    
    # Task 2: Payment Discrepancy (20 points)
    score2, feedback2 = evaluate_task2(submission.get("task2", {}), answer_key.get("task2", {}))
    results["tasks"]["task2"] = {
        "score": score2,
        "max_points": 20,
        "percentage": (score2 / 20) * 100,
        "feedback": feedback2
    }
    
    # Task 3: Payment Schedule (20 points)
    score3, feedback3 = evaluate_task3(submission.get("task3", {}), answer_key.get("task3", {}))
    results["tasks"]["task3"] = {
        "score": score3,
        "max_points": 20,
        "percentage": (score3 / 20) * 100,
        "feedback": feedback3
    }
    
    # Task 4: Collection Communication (20 points)
    score4, feedback4 = evaluate_task4(submission.get("task4", {}), answer_key.get("task4", {}))
    results["tasks"]["task4"] = {
        "score": score4,
        "max_points": 20,
        "percentage": (score4 / 20) * 100,
        "feedback": feedback4
    }
    
    # Task 5: Payment Documentation (20 points)
    score5, feedback5 = evaluate_task5(submission.get("task5", {}), answer_key.get("task5", {}))
    results["tasks"]["task5"] = {
        "score": score5,
        "max_points": 20,
        "percentage": (score5 / 20) * 100,
        "feedback": feedback5
    }
    
    # Calculate overall score
    total_score = score1 + score2 + score3 + score4 + score5
    results["overall_score"] = (total_score / 100) * 100
    results["passed"] = total_score >= 70
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json_file(results, "test_results.json")
    
    # Print summary
    print(f"\nEvaluation complete!")
    print(f"Overall score: {results['overall_score']:.2f}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")
    print("\nTask scores:")
    for task, data in results["tasks"].items():
        print(f"  {task}: {data['score']:.2f}/{data['max_points']} ({data['percentage']:.2f}%)")

if __name__ == "__main__":
    main()