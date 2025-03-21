import json
import os

def evaluate_section1(candidate_answers, answer_key):
    """Evaluate Section 1: Policy Interpretation"""
    section_score = 0
    section_feedback = {}
    
    for question in ["question1", "question2", "question3", "question4"]:
        if candidate_answers.get(question) == answer_key.get(question):
            section_score += 6.25
            section_feedback[question] = {
                "score": 6.25,
                "max_score": 6.25,
                "feedback": "Correct answer."
            }
        else:
            section_feedback[question] = {
                "score": 0,
                "max_score": 6.25,
                "feedback": f"Incorrect. The correct answer is '{answer_key.get(question)}'."
            }
    
    return section_score, section_feedback

def evaluate_section2(candidate_answers, answer_key):
    """Evaluate Section 2: Claims Form Analysis"""
    section_score = 0
    section_feedback = {}
    
    # Question 5: Identify elements from claim form (15 points)
    q5_score = 0
    q5_feedback = {}
    
    if "question5" in candidate_answers:
        candidate_q5 = candidate_answers["question5"]
        answer_key_q5 = answer_key["question5"]
        
        for element in ["date_of_loss", "policy_number", "property_address", "loss_type", "estimated_damage", "deductible"]:
            if candidate_q5.get(element) == answer_key_q5.get(element):
                q5_score += 2.5
                q5_feedback[element] = {
                    "score": 2.5,
                    "max_score": 2.5,
                    "feedback": "Correct."
                }
            else:
                q5_feedback[element] = {
                    "score": 0,
                    "max_score": 2.5,
                    "feedback": f"Incorrect. Expected: {answer_key_q5.get(element)}"
                }
    
    section_score += q5_score
    section_feedback["question5"] = {
        "score": q5_score,
        "max_score": 15,
        "details": q5_feedback
    }
    
    # Question 6: Determine if policy was active (10 points)
    q6_score = 0
    q6_feedback = {}
    
    if "question6" in candidate_answers:
        candidate_q6 = candidate_answers["question6"]
        answer_key_q6 = answer_key["question6"]
        
        # Check policy_active determination (5 points)
        if candidate_q6.get("policy_active") == answer_key_q6.get("policy_active"):
            q6_score += 5
            q6_feedback["policy_active"] = {
                "score": 5,
                "max_score": 5,
                "feedback": "Correct determination."
            }
        else:
            q6_feedback["policy_active"] = {
                "score": 0,
                "max_score": 5,
                "feedback": "Incorrect determination."
            }
        
        # Check reasoning (5 points)
        # For reasoning, we'll check if key elements are present
        candidate_reasoning = candidate_q6.get("reasoning", "").lower()
        key_elements = ["date of loss", "policy period"]
        
        if all(element in candidate_reasoning for element in key_elements):
            q6_score += 5
            q6_feedback["reasoning"] = {
                "score": 5,
                "max_score": 5,
                "feedback": "Reasoning includes all key elements."
            }
        else:
            q6_feedback["reasoning"] = {
                "score": 0,
                "max_score": 5,
                "feedback": "Reasoning is missing key elements. Should mention date of loss falling within policy period."
            }
    
    section_score += q6_score
    section_feedback["question6"] = {
        "score": q6_score,
        "max_score": 10,
        "details": q6_feedback
    }
    
    return section_score, section_feedback

def evaluate_section3(candidate_answers, answer_key):
    """Evaluate Section 3: Coverage Determination"""
    section_score = 0
    section_feedback = {}
    
    # Question 7: Determine coverage for roof and interior (15 points)
    q7_score = 0
    q7_feedback = {}
    
    if "question7" in candidate_answers:
        candidate_q7 = candidate_answers["question7"]
        answer_key_q7 = answer_key["question7"]
        
        # Check roof_replacement determination (3.75 points)
        if candidate_q7.get("roof_replacement") == answer_key_q7.get("roof_replacement"):
            q7_score += 1.875
            q7_feedback["roof_replacement"] = {
                "score": 1.875,
                "max_score": 1.875,
                "feedback": "Correct determination."
            }
        else:
            q7_feedback["roof_replacement"] = {
                "score": 0,
                "max_score": 1.875,
                "feedback": f"Incorrect. The correct determination is '{answer_key_q7.get('roof_replacement')}'."
            }
        
        # Check roof reasoning (3.75 points)
        candidate_roof_reasoning = candidate_q7.get("roof_reasoning", "").lower()
        key_elements_roof = ["storm", "wear and tear", "pre-existing"]
        
        reasoning_score = 0
        missing_elements = []
        for element in key_elements_roof:
            if element in candidate_roof_reasoning:
                reasoning_score += 1.875 / len(key_elements_roof)
            else:
                missing_elements.append(element)
        
        q7_score += reasoning_score
        q7_feedback["roof_reasoning"] = {
            "score": reasoning_score,
            "max_score": 1.875,
            "feedback": "Reasoning complete." if not missing_elements else f"Missing key elements in reasoning: {', '.join(missing_elements)}"
        }
        
        # Check interior_damage determination (3.75 points)
        if candidate_q7.get("interior_damage") == answer_key_q7.get("interior_damage"):
            q7_score += 1.875
            q7_feedback["interior_damage"] = {
                "score": 1.875,
                "max_score": 1.875,
                "feedback": "Correct determination."
            }
        else:
            q7_feedback["interior_damage"] = {
                "score": 0,
                "max_score": 1.875,
                "feedback": f"Incorrect. The correct determination is '{answer_key_q7.get('interior_damage')}'."
            }
        
        # Check interior reasoning (3.75 points)
        candidate_interior_reasoning = candidate_q7.get("interior_reasoning", "").lower()
        key_elements_interior = ["covered peril", "storm"]
        
        reasoning_score = 0
        missing_elements = []
        for element in key_elements_interior:
            if element in candidate_interior_reasoning:
                reasoning_score += 1.875 / len(key_elements_interior)
            else:
                missing_elements.append(element)
        
        q7_score += reasoning_score
        q7_feedback["interior_reasoning"] = {
            "score": reasoning_score,
            "max_score": 1.875,
            "feedback": "Reasoning complete." if not missing_elements else f"Missing key elements in reasoning: {', '.join(missing_elements)}"
        }
    
    section_score += q7_score
    section_feedback["question7"] = {
        "score": q7_score,
        "max_score": 15,
        "details": q7_feedback
    }
    
    # Question 8: Calculate payment amount (10 points)
    q8_score = 0
    q8_feedback = {}
    
    if "question8" in candidate_answers:
        candidate_q8 = candidate_answers["question8"]
        answer_key_q8 = answer_key["question8"]
        
        # Check calculation approach (5 points)
        candidate_calculation = candidate_q8.get("calculation", "").lower()
        key_elements_calc = ["3,100", "2,550", "1,500", "4,150"]
        
        calc_score = 0
        missing_elements = []
        for element in key_elements_calc:
            # Remove commas for numeric comparison
            clean_element = element.replace(",", "")
            if clean_element in candidate_calculation.replace(",", ""):
                calc_score += 5 / len(key_elements_calc)
            else:
                missing_elements.append(element)
        
        q8_score += calc_score
        q8_feedback["calculation"] = {
            "score": calc_score,
            "max_score": 5,
            "feedback": "Calculation approach correct." if not missing_elements else f"Missing key elements in calculation: {', '.join(missing_elements)}"
        }
        
        # Check payment amount (5 points)
        if candidate_q8.get("payment_amount") == answer_key_q8.get("payment_amount"):
            q8_score += 5
            q8_feedback["payment_amount"] = {
                "score": 5,
                "max_score": 5,
                "feedback": "Correct payment amount."
            }
        else:
            q8_feedback["payment_amount"] = {
                "score": 0,
                "max_score": 5,
                "feedback": f"Incorrect. The correct payment amount is {answer_key_q8.get('payment_amount')}."
            }
    
    section_score += q8_score
    section_feedback["question8"] = {
        "score": q8_score,
        "max_score": 10,
        "details": q8_feedback
    }
    
    return section_score, section_feedback

def evaluate_section4(candidate_answers, answer_key):
    """Evaluate Section 4: Documentation Requirements"""
    section_score = 0
    section_feedback = {}
    
    # Question 9: Identify 5 essential documents (12.5 points)
    q9_score = 0
    q9_feedback = {}
    
    if "question9" in candidate_answers:
        candidate_q9 = candidate_answers["question9"]
        answer_key_q9 = answer_key["question9"]
        
        # Make lowercase versions for more flexible matching
        candidate_docs_lower = [doc.lower() if isinstance(doc, str) else "" for doc in candidate_q9]
        answer_key_docs_lower = [doc.lower() for doc in answer_key_q9]
        
        # Check if each candidate document matches or is equivalent to an answer key document
        matched_docs = []
        key_docs_matched = []
        
        for i, candidate_doc in enumerate(candidate_docs_lower):
            for j, key_doc in enumerate(answer_key_docs_lower):
                if j not in key_docs_matched:
                    # Check for exact match or if key terms are present
                    if candidate_doc == key_doc or (
                        ("police" in candidate_doc and "police" in key_doc) or
                        ("medical" in candidate_doc and "medical" in key_doc) or
                        ("statement" in candidate_doc and "statement" in key_doc and "other driver" in candidate_doc and "other driver" in key_doc) or
                        ("witness" in candidate_doc and "witness" in key_doc) or
                        ("repair" in candidate_doc and "estimate" in candidate_doc and "repair" in key_doc and "estimate" in key_doc)
                    ):
                        matched_docs.append(i)
                        key_docs_matched.append(j)
                        break
        
        # Award 2.5 points for each correctly identified document (up to 5)
        q9_score = min(len(matched_docs), 5) * 2.5
        
        # Provide feedback on each document
        for i, doc in enumerate(candidate_q9):
            if i in matched_docs:
                q9_feedback[f"document{i+1}"] = {
                    "score": 2.5,
                    "max_score": 2.5,
                    "feedback": "Valid document identified."
                }
            else:
                q9_feedback[f"document{i+1}"] = {
                    "score": 0,
                    "max_score": 2.5,
                    "feedback": "Document not recognized as essential for this claim type."
                }
    
    section_score += q9_score
    section_feedback["question9"] = {
        "score": q9_score,
        "max_score": 12.5,
        "details": q9_feedback
    }
    
    # Question 10: Explain why each document is necessary (12.5 points)
    q10_score = 0
    q10_feedback = {}
    
    if "question10" in candidate_answers and "question9" in candidate_answers:
        candidate_q10 = candidate_answers["question10"]
        
        # For each document identified in question9, check if explanation is valid
        for i, doc in enumerate(candidate_answers["question9"]):
            if i >= 5:  # Only evaluate the first 5 documents
                break
                
            if doc in candidate_q10:
                explanation = candidate_q10.get(doc, "").lower()
                
                # Check if explanation contains key terms based on document type
                valid_explanation = False
                
                if "police" in doc.lower():
                    valid_explanation = any(term in explanation for term in ["verify", "fault", "official", "record"])
                elif "medical" in doc.lower():
                    valid_explanation = any(term in explanation for term in ["injury", "treatment", "extent", "evaluate"])
                elif "statement" in doc.lower() and "other driver" in doc.lower():
                    valid_explanation = any(term in explanation for term in ["perspective", "liability", "fault", "determination"])
                elif "witness" in doc.lower():
                    valid_explanation = any(term in explanation for term in ["verify", "independent", "perspective", "confirm"])
                elif "repair" in doc.lower() or "estimate" in doc.lower():
                    valid_explanation = any(term in explanation for term in ["damage", "cost", "payment", "amount", "quantif"])
                else:
                    # For other document types, check for general relevance
                    valid_explanation = any(term in explanation for term in ["coverage", "claim", "verify", "determine", "evaluate"])
                
                if valid_explanation:
                    q10_score += 2.5
                    q10_feedback[doc] = {
                        "score": 2.5,
                        "max_score": 2.5,
                        "feedback": "Valid explanation provided."
                    }
                else:
                    q10_feedback[doc] = {
                        "score": 0,
                        "max_score": 2.5,
                        "feedback": "Explanation insufficient or does not demonstrate understanding of document's purpose."
                    }
            else:
                q10_feedback[doc] = {
                    "score": 0,
                    "max_score": 2.5,
                    "feedback": "No explanation provided for this document."
                }
    
    section_score += q10_score
    section_feedback["question10"] = {
        "score": q10_score,
        "max_score": 12.5,
        "details": q10_feedback
    }
    
    return section_score, section_feedback

def evaluate_submission(submission_path, answer_key_path):
    """Evaluate the candidate's submission against the answer key"""
    try:
        with open(submission_path, 'r') as f:
            candidate_submission = json.load(f)
        
        with open(answer_key_path, 'r') as f:
            answer_key = json.load(f)
        
        results = {
            "candidate_id": candidate_submission.get("candidate_id", "Unknown"),
            "sections": {},
            "section_scores": {},
            "overall_score": 0
        }
        
        total_score = 0
        
        # Evaluate Section 1
        section1_score, section1_feedback = evaluate_section1(
            candidate_submission.get("section1", {}),
            answer_key.get("section1", {})
        )
        total_score += section1_score
        results["sections"]["section1"] = section1_feedback
        results["section_scores"]["section1"] = {
            "score": section1_score,
            "max_score": 25,
            "percentage": (section1_score / 25) * 100
        }
        
        # Evaluate Section 2
        section2_score, section2_feedback = evaluate_section2(
            candidate_submission.get("section2", {}),
            answer_key.get("section2", {})
        )
        total_score += section2_score
        results["sections"]["section2"] = section2_feedback
        results["section_scores"]["section2"] = {
            "score": section2_score,
            "max_score": 25,
            "percentage": (section2_score / 25) * 100
        }
        
        # Evaluate Section 3
        section3_score, section3_feedback = evaluate_section3(
            candidate_submission.get("section3", {}),
            answer_key.get("section3", {})
        )
        total_score += section3_score
        results["sections"]["section3"] = section3_feedback
        results["section_scores"]["section3"] = {
            "score": section3_score,
            "max_score": 25,
            "percentage": (section3_score / 25) * 100
        }
        
        # Evaluate Section 4
        section4_score, section4_feedback = evaluate_section4(
            candidate_submission.get("section4", {}),
            answer_key.get("section4", {})
        )
        total_score += section4_score
        results["sections"]["section4"] = section4_feedback
        results["section_scores"]["section4"] = {
            "score": section4_score,
            "max_score": 25,
            "percentage": (section4_score / 25) * 100
        }
        
        # Calculate overall score as percentage
        overall_percentage = (total_score / 100) * 100
        results["overall_score"] = overall_percentage
        results["pass_fail"] = "PASS" if overall_percentage >= 70 else "FAIL"
        results["total_points"] = total_score
        results["max_points"] = 100
        
        return results
        
    except Exception as e:
        return {
            "error": str(e),
            "overall_score": 0,
            "pass_fail": "FAIL"
        }

if __name__ == "__main__":
    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    submission_path = os.path.join(current_dir, "test_submission.json")
    answer_key_path = os.path.join(current_dir, "answer_key.json")
    results_path = os.path.join(current_dir, "test_results.json")
    
    # Evaluate the submission
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Save the results
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to {results_path}")
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Result: {results['pass_fail']}")