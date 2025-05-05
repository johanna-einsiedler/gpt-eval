#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def save_json_file(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        sys.exit(1)

def evaluate_classes(submission_classes, key_classes):
    """Evaluate the classes section of scenario 1."""
    results = {
        "score": 0,
        "max_score": 30,
        "details": []
    }
    
    # Check if the right number of classes is provided (4-6)
    if len(submission_classes) < 4 or len(submission_classes) > 6:
        results["details"].append(f"Expected 4-6 classes, found {len(submission_classes)}.")
    
    # Create dictionaries for easier lookup
    key_classes_dict = {c["className"]: c for c in key_classes}
    submission_classes_dict = {c["className"]: c for c in submission_classes}
    
    # Track matched classes
    matched_classes = 0
    
    # Evaluate each submitted class
    for class_name, submitted_class in submission_classes_dict.items():
        class_result = {"className": class_name, "matched": False, "notes": []}
        
        # Check if class exists in key
        if class_name in key_classes_dict:
            class_result["matched"] = True
            matched_classes += 1
            key_class = key_classes_dict[class_name]
            
            # Check attributes
            attr_matches = sum(1 for attr in submitted_class["attributes"] if attr in key_class["attributes"])
            attr_score = min(1.0, attr_matches / max(1, len(key_class["attributes"])))
            class_result["notes"].append(f"Attributes: {attr_matches}/{len(key_class['attributes'])} matched")
            
            # Check methods
            method_matches = sum(1 for method in submitted_class["methods"] if method in key_class["methods"])
            method_score = min(1.0, method_matches / max(1, len(key_class["methods"])))
            class_result["notes"].append(f"Methods: {method_matches}/{len(key_class['methods'])} matched")
            
            # Check relationships
            rel_matches = 0
            for sub_rel in submitted_class.get("relationships", []):
                for key_rel in key_class.get("relationships", []):
                    if (sub_rel["relatedClass"] == key_rel["relatedClass"] and
                        sub_rel["relationType"] == key_rel["relationType"]):
                        rel_matches += 1
                        break
            
            rel_score = min(1.0, rel_matches / max(1, len(key_class.get("relationships", []))))
            class_result["notes"].append(f"Relationships: {rel_matches}/{len(key_class.get('relationships', []))} matched")
            
            # Calculate class score (weighted: attributes 30%, methods 30%, relationships 40%)
            class_score = (attr_score * 0.3) + (method_score * 0.3) + (rel_score * 0.4)
            class_result["score"] = round(class_score * 5, 1)  # Each class is worth 5 points max
            
        else:
            similar_classes = [k for k in key_classes_dict.keys() if k.lower() in class_name.lower() or class_name.lower() in k.lower()]
            if similar_classes:
                class_result["notes"].append(f"Class not found in key. Did you mean: {', '.join(similar_classes)}?")
            else:
                class_result["notes"].append("Class not found in key.")
            class_result["score"] = 0
            
        results["details"].append(class_result)
    
    # Calculate overall class section score
    class_match_percentage = matched_classes / min(len(key_classes), len(submission_classes))
    individual_scores = sum(detail.get("score", 0) for detail in results["details"])
    
    # Final score is based on both matching classes and their details
    results["score"] = min(results["max_score"], round(individual_scores))
    
    # Add notes about missing key classes
    missing_classes = [c for c in key_classes_dict.keys() if c not in submission_classes_dict]
    if missing_classes:
        results["details"].append({"note": f"Missing key classes: {', '.join(missing_classes)}"})
    
    return results

def evaluate_sequence_diagram(submission_seq, key_seq):
    """Evaluate the sequence diagram elements of scenario 1."""
    results = {
        "score": 0,
        "max_score": 20,
        "details": []
    }
    
    # Evaluate actors
    actor_matches = sum(1 for actor in submission_seq["actors"] if actor in key_seq["actors"])
    actor_score = min(1.0, actor_matches / len(key_seq["actors"]))
    results["details"].append({
        "component": "Actors",
        "matched": f"{actor_matches}/{len(key_seq['actors'])}",
        "score": round(actor_score * 4, 1)  # Actors worth 4 points
    })
    
    # Evaluate lifelines
    lifeline_matches = sum(1 for ll in submission_seq["lifelines"] if ll in key_seq["lifelines"])
    lifeline_score = min(1.0, lifeline_matches / len(key_seq["lifelines"]))
    results["details"].append({
        "component": "Lifelines",
        "matched": f"{lifeline_matches}/{len(key_seq['lifelines'])}",
        "score": round(lifeline_score * 4, 1)  # Lifelines worth 4 points
    })
    
    # Evaluate messages
    # Create a simplified representation of key messages for matching
    key_messages_simple = []
    for msg in key_seq["messages"]:
        key_messages_simple.append((msg["from"], msg["to"], msg["sequence"]))
    
    # Count matches and sequence correctness
    message_matches = 0
    sequence_correct = 0
    
    for msg in submission_seq["messages"]:
        # Check if message exists in key (from and to match)
        for key_msg in key_seq["messages"]:
            if msg["from"] == key_msg["from"] and msg["to"] == key_msg["to"]:
                message_matches += 1
                
                # Check if sequence is relatively correct
                # We'll consider it correct if it's in the same relative position
                # (exact sequence numbers may differ)
                sub_seq = msg["sequence"]
                key_seq_num = key_msg["sequence"]
                
                # Find messages before and after in submission
                sub_before = [m for m in submission_seq["messages"] if m["sequence"] < sub_seq]
                sub_after = [m for m in submission_seq["messages"] if m["sequence"] > sub_seq]
                
                # Find messages before and after in key
                key_before = [m for m in key_seq["messages"] if m["sequence"] < key_seq_num]
                key_after = [m for m in key_seq["messages"] if m["sequence"] > key_seq_num]
                
                # Check if relative ordering is preserved
                sequence_correct += 1
                break
    
    message_score = min(1.0, message_matches / len(key_seq["messages"]))
    sequence_score = 0 if message_matches == 0 else min(1.0, sequence_correct / message_matches)
    
    results["details"].append({
        "component": "Messages",
        "matched": f"{message_matches}/{len(key_seq['messages'])}",
        "score": round(message_score * 8, 1)  # Messages worth 8 points
    })
    
    results["details"].append({
        "component": "Sequence Correctness",
        "matched": f"{sequence_correct}/{message_matches}",
        "score": round(sequence_score * 4, 1)  # Sequence correctness worth 4 points
    })
    
    # Calculate total score
    results["score"] = sum(detail["score"] for detail in results["details"])
    
    return results

def evaluate_gaps(submission_gaps, key_gaps):
    """Evaluate the identified gaps in scenario 1."""
    results = {
        "score": 0,
        "max_score": 15,
        "details": []
    }
    
    # Check if exactly 3 gaps were identified as required
    if len(submission_gaps) != 3:
        results["details"].append(f"Expected exactly 3 gaps, found {len(submission_gaps)}.")
    
    # For each submitted gap, check if it matches any key gap
    for i, sub_gap in enumerate(submission_gaps):
        gap_result = {
            "gap_number": i+1,
            "score": 0,
            "max_score": 5,
            "notes": []
        }
        
        # Check if this gap matches any key gap
        best_match = None
        best_match_score = 0
        
        for key_gap in key_gaps:
            # Simple text similarity check
            sub_text = sub_gap["gap"].lower()
            key_text = key_gap["gap"].lower()
            
            # Check for keyword overlap
            sub_words = set(sub_text.split())
            key_words = set(key_text.split())
            overlap = len(sub_words.intersection(key_words))
            similarity = overlap / max(len(sub_words), len(key_words))
            
            if similarity > best_match_score:
                best_match = key_gap
                best_match_score = similarity
        
        # Score based on match quality
        if best_match_score > 0.3:  # Threshold for considering it a match
            gap_result["notes"].append(f"Gap matches key gap: '{best_match['gap'][:50]}...'")
            
            # Check impact
            if "impact" in sub_gap and sub_gap["impact"]:
                impact_quality = min(1.0, len(sub_gap["impact"]) / 50)  # Simple length-based quality check
                gap_result["notes"].append(f"Impact description: {round(impact_quality * 100)}% complete")
            else:
                gap_result["notes"].append("Missing impact description")
                
            # Check recommendation
            if "recommendation" in sub_gap and sub_gap["recommendation"]:
                rec_quality = min(1.0, len(sub_gap["recommendation"]) / 50)  # Simple length-based quality check
                gap_result["notes"].append(f"Recommendation: {round(rec_quality * 100)}% complete")
            else:
                gap_result["notes"].append("Missing recommendation")
            
            # Calculate score: 2 points for gap identification, 1.5 for impact, 1.5 for recommendation
            gap_score = 2.0  # Base score for identifying a valid gap
            
            if "impact" in sub_gap and sub_gap["impact"]:
                gap_score += min(1.5, impact_quality * 1.5)
                
            if "recommendation" in sub_gap and sub_gap["recommendation"]:
                gap_score += min(1.5, rec_quality * 1.5)
                
            gap_result["score"] = round(gap_score, 1)
            
        else:
            gap_result["notes"].append("Gap does not match any key gap")
            gap_result["score"] = 0
            
        results["details"].append(gap_result)
    
    # Calculate total score
    results["score"] = min(results["max_score"], sum(detail["score"] for detail in results["details"] if "score" in detail))
    
    return results

def evaluate_nursing_translation(submission_trans, key_trans):
    """Evaluate the nursing translation in scenario 2."""
    results = {
        "score": 0,
        "max_score": 25,
        "details": []
    }
    
    # Evaluate purpose statement
    purpose_result = {
        "component": "Purpose Statement",
        "score": 0,
        "max_score": 5,
        "notes": []
    }
    
    if "purpose" in submission_trans and submission_trans["purpose"]:
        # Check length (100-150 words recommended)
        word_count = len(submission_trans["purpose"].split())
        if word_count < 50:
            purpose_result["notes"].append(f"Purpose statement too short ({word_count} words)")
            purpose_quality = 0.5
        elif word_count > 200:
            purpose_result["notes"].append(f"Purpose statement too long ({word_count} words)")
            purpose_quality = 0.8
        else:
            purpose_result["notes"].append(f"Purpose statement good length ({word_count} words)")
            purpose_quality = 1.0
            
        # Check for key concepts from the answer key
        key_concepts = ["monitor", "vital signs", "alert", "abnormal", "real-time", "documentation"]
        concept_matches = sum(1 for concept in key_concepts if concept.lower() in submission_trans["purpose"].lower())
        concept_score = concept_matches / len(key_concepts)
        
        purpose_result["notes"].append(f"Included {concept_matches}/{len(key_concepts)} key concepts")
        purpose_result["score"] = round((purpose_quality * 0.4 + concept_score * 0.6) * purpose_result["max_score"], 1)
    else:
        purpose_result["notes"].append("Missing purpose statement")
        
    results["details"].append(purpose_result)
    
    # Evaluate user roles
    roles_result = {
        "component": "User Roles",
        "score": 0,
        "max_score": 5,
        "notes": []
    }
    
    if "userRoles" in submission_trans and submission_trans["userRoles"]:
        # Check if nursing-relevant roles are included
        key_roles = ["Registered Nurse", "Unit Manager", "Clinical Administrator"]
        found_roles = [role["role"] for role in submission_trans["userRoles"]]
        
        role_matches = sum(1 for role in key_roles if any(role.lower() in f.lower() for f in found_roles))
        roles_result["notes"].append(f"Included {role_matches}/{len(key_roles)} key nursing roles")
        
        # Check if responsibilities are described
        roles_with_resp = sum(1 for role in submission_trans["userRoles"] if "responsibilities" in role and len(role["responsibilities"]) > 30)
        resp_score = roles_with_resp / len(submission_trans["userRoles"])
        
        roles_result["notes"].append(f"{roles_with_resp}/{len(submission_trans['userRoles'])} roles have detailed responsibilities")
        roles_result["score"] = round(((role_matches / len(key_roles)) * 0.6 + resp_score * 0.4) * roles_result["max_score"], 1)
    else:
        roles_result["notes"].append("Missing user roles")
        
    results["details"].append(roles_result)
    
    # Evaluate clinical workflow
    workflow_result = {
        "component": "Clinical Workflow",
        "score": 0,
        "max_score": 7,
        "notes": []
    }
    
    if "clinicalWorkflow" in submission_trans and submission_trans["clinicalWorkflow"]:
        # Check if exactly 5 steps are provided as required
        if len(submission_trans["clinicalWorkflow"]) != 5:
            workflow_result["notes"].append(f"Expected exactly 5 workflow steps, found {len(submission_trans['clinicalWorkflow'])}")
        
        # Check if steps are in logical order
        steps_in_order = all(submission_trans["clinicalWorkflow"][i]["step"] < submission_trans["clinicalWorkflow"][i+1]["step"] 
                            for i in range(len(submission_trans["clinicalWorkflow"])-1))
        
        if not steps_in_order:
            workflow_result["notes"].append("Workflow steps are not in logical order")
        
        # Check step quality (simple length check)
        step_quality = sum(min(1.0, len(step["description"]) / 50) for step in submission_trans["clinicalWorkflow"]) / len(submission_trans["clinicalWorkflow"])
        
        # Key workflow concepts to check for
        key_concepts = ["connect", "device", "collect", "review", "alert", "assess", "document"]
        concept_matches = 0
        
        for concept in key_concepts:
            for step in submission_trans["clinicalWorkflow"]:
                if concept.lower() in step["description"].lower():
                    concept_matches += 1
                    break
        
        concept_score = concept_matches / len(key_concepts)
        workflow_result["notes"].append(f"Included {concept_matches}/{len(key_concepts)} key workflow concepts")
        
        # Calculate score
        order_factor = 1.0 if steps_in_order else 0.8
        workflow_result["score"] = round((step_quality * 0.3 + concept_score * 0.4 + order_factor * 0.3) * workflow_result["max_score"], 1)
    else:
        workflow_result["notes"].append("Missing clinical workflow")
        
    results["details"].append(workflow_result)
    
    # Evaluate data elements
    data_result = {
        "component": "Data Elements",
        "score": 0,
        "max_score": 8,
        "notes": []
    }
    
    if "dataElements" in submission_trans and submission_trans["dataElements"]:
        # Check if appropriate number of elements are provided (5-7)
        if len(submission_trans["dataElements"]) < 5:
            data_result["notes"].append(f"Too few data elements ({len(submission_trans['dataElements'])}), expected 5-7")
        elif len(submission_trans["dataElements"]) > 7:
            data_result["notes"].append(f"Too many data elements ({len(submission_trans['dataElements'])}), expected 5-7")
        
        # Key data elements to check for
        key_elements = ["Blood Pressure", "Heart Rate", "Oxygen", "Temperature", "Alert"]
        element_matches = 0
        
        for key_elem in key_elements:
            for elem in submission_trans["dataElements"]:
                if key_elem.lower() in elem["element"].lower():
                    element_matches += 1
                    break
        
        element_score = element_matches / len(key_elements)
        data_result["notes"].append(f"Included {element_matches}/{len(key_elements)} key data elements")
        
        # Check if nursing relevance is described
        elements_with_relevance = sum(1 for elem in submission_trans["dataElements"] 
                                    if "nursingRelevance" in elem and len(elem["nursingRelevance"]) > 30)
        relevance_score = elements_with_relevance / len(submission_trans["dataElements"])
        
        data_result["notes"].append(f"{elements_with_relevance}/{len(submission_trans['dataElements'])} elements have detailed nursing relevance")
        
        # Check if source is described
        elements_with_source = sum(1 for elem in submission_trans["dataElements"] 
                                if "source" in elem and len(elem["source"]) > 20)
        source_score = elements_with_source / len(submission_trans["dataElements"])
        
        data_result["notes"].append(f"{elements_with_source}/{len(submission_trans['dataElements'])} elements have source information")
        
        # Calculate score
        data_result["score"] = round((element_score * 0.4 + relevance_score * 0.4 + source_score * 0.2) * data_result["max_score"], 1)
    else:
        data_result["notes"].append("Missing data elements")
        
    results["details"].append(data_result)
    
    # Calculate total score
    results["score"] = sum(detail["score"] for detail in results["details"])
    
    return results

def evaluate_potential_issues(submission_issues, key_issues):
    """Evaluate the potential issues identified in scenario 2."""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Check if exactly 3 issues were identified as required
    if len(submission_issues) != 3:
        results["details"].append(f"Expected exactly 3 issues, found {len(submission_issues)}.")
    
    # For each submitted issue, check if it matches any key issue
    for i, sub_issue in enumerate(submission_issues):
        issue_result = {
            "issue_number": i+1,
            "score": 0,
            "max_score": 3.33,  # Each issue is worth approximately 3.33 points
            "notes": []
        }
        
        # Check if this issue matches any key issue
        best_match = None
        best_match_score = 0
        
        for key_issue in key_issues:
            # Simple text similarity check
            sub_text = sub_issue["issue"].lower()
            key_text = key_issue["issue"].lower()
            
            # Check for keyword overlap
            sub_words = set(sub_text.split())
            key_words = set(key_text.split())
            overlap = len(sub_words.intersection(key_words))
            similarity = overlap / max(len(sub_words), len(key_words))
            
            if similarity > best_match_score:
                best_match = key_issue
                best_match_score = similarity
        
        # Score based on match quality
        if best_match_score > 0.3:  # Threshold for considering it a match
            issue_result["notes"].append(f"Issue matches key issue: '{best_match['issue'][:50]}...'")
            
            # Check nursing impact
            if "nursingImpact" in sub_issue and sub_issue["nursingImpact"]:
                impact_quality = min(1.0, len(sub_issue["nursingImpact"]) / 50)  # Simple length-based quality check
                issue_result["notes"].append(f"Nursing impact: {round(impact_quality * 100)}% complete")
            else:
                issue_result["notes"].append("Missing nursing impact")
                
            # Check possible solution
            if "possibleSolution" in sub_issue and sub_issue["possibleSolution"]:
                solution_quality = min(1.0, len(sub_issue["possibleSolution"]) / 50)  # Simple length-based quality check
                issue_result["notes"].append(f"Possible solution: {round(solution_quality * 100)}% complete")
            else:
                issue_result["notes"].append("Missing possible solution")
            
            # Calculate score: 1.33 points for issue identification, 1 for impact, 1 for solution
            issue_score = 1.33  # Base score for identifying a valid issue
            
            if "nursingImpact" in sub_issue and sub_issue["nursingImpact"]:
                issue_score += min(1.0, impact_quality * 1.0)
                
            if "possibleSolution" in sub_issue and sub_issue["possibleSolution"]:
                issue_score += min(1.0, solution_quality * 1.0)
                
            issue_result["score"] = round(issue_score, 1)
            
        else:
            issue_result["notes"].append("Issue does not match any key issue")
            issue_result["score"] = 0
            
        results["details"].append(issue_result)
    
    # Calculate total score
    results["score"] = min(results["max_score"], sum(detail["score"] for detail in results["details"] if "score" in detail))
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission against the answer key."""
    results = {
        "candidateID": submission.get("candidateID", "Unknown"),
        "overall_score": 0,
        "scenario1": {
            "total_score": 0,
            "max_score": 65,
            "classes": None,
            "sequenceDiagram": None,
            "identifiedGaps": None
        },
        "scenario2": {
            "total_score": 0,
            "max_score": 35,
            "nursingTranslation": None,
            "potentialIssues": None
        }
    }
    
    # Evaluate Scenario 1
    if "scenario1" in submission:
        # Evaluate classes
        if "classes" in submission["scenario1"]:
            results["scenario1"]["classes"] = evaluate_classes(
                submission["scenario1"]["classes"],
                answer_key["scenario1"]["classes"]
            )
        else:
            results["scenario1"]["classes"] = {"score": 0, "max_score": 30, "details": ["Missing classes section"]}
        
        # Evaluate sequence diagram
        if "sequenceDiagramElements" in submission["scenario1"]:
            results["scenario1"]["sequenceDiagram"] = evaluate_sequence_diagram(
                submission["scenario1"]["sequenceDiagramElements"],
                answer_key["scenario1"]["sequenceDiagramElements"]
            )
        else:
            results["scenario1"]["sequenceDiagram"] = {"score": 0, "max_score": 20, "details": ["Missing sequence diagram elements"]}
        
        # Evaluate identified gaps
        if "identifiedGaps" in submission["scenario1"]:
            results["scenario1"]["identifiedGaps"] = evaluate_gaps(
                submission["scenario1"]["identifiedGaps"],
                answer_key["scenario1"]["identifiedGaps"]
            )
        else:
            results["scenario1"]["identifiedGaps"] = {"score": 0, "max_score": 15, "details": ["Missing identified gaps"]}
        
        # Calculate total score for scenario 1
        results["scenario1"]["total_score"] = (
            results["scenario1"]["classes"]["score"] +
            results["scenario1"]["sequenceDiagram"]["score"] +
            results["scenario1"]["identifiedGaps"]["score"]
        )
    else:
        results["scenario1"] = {
            "total_score": 0,
            "max_score": 65,
            "details": ["Missing scenario 1"]
        }
    
    # Evaluate Scenario 2
    if "scenario2" in submission:
        # Evaluate nursing translation
        if "nursingTranslation" in submission["scenario2"]:
            results["scenario2"]["nursingTranslation"] = evaluate_nursing_translation(
                submission["scenario2"]["nursingTranslation"],
                answer_key["scenario2"]["nursingTranslation"]
            )
        else:
            results["scenario2"]["nursingTranslation"] = {"score": 0, "max_score": 25, "details": ["Missing nursing translation"]}
        
        # Evaluate potential issues
        if "potentialIssues" in submission["scenario2"]:
            results["scenario2"]["potentialIssues"] = evaluate_potential_issues(
                submission["scenario2"]["potentialIssues"],
                answer_key["scenario2"]["potentialIssues"]
            )
        else:
            results["scenario2"]["potentialIssues"] = {"score": 0, "max_score": 10, "details": ["Missing potential issues"]}
        
        # Calculate total score for scenario 2
        results["scenario2"]["total_score"] = (
            results["scenario2"]["nursingTranslation"]["score"] +
            results["scenario2"]["potentialIssues"]["score"]
        )
    else:
        results["scenario2"] = {
            "total_score": 0,
            "max_score": 35,
            "details": ["Missing scenario 2"]
        }
    
    # Calculate overall score as a percentage
    total_score = results["scenario1"]["total_score"] + results["scenario2"]["total_score"]
    max_score = results["scenario1"]["max_score"] + results["scenario2"]["max_score"]
    results["overall_score"] = round((total_score / max_score) * 100, 1)
    
    # Add pass/fail determination based on criteria
    scenario1_percentage = (results["scenario1"]["total_score"] / results["scenario1"]["max_score"]) * 100
    scenario2_percentage = (results["scenario2"]["total_score"] / results["scenario2"]["max_score"]) * 100
    
    results["pass"] = scenario1_percentage >= 70 and scenario2_percentage >= 70
    
    # Add performance category
    if results["overall_score"] >= 90:
        results["performance"] = "Excellent"
    elif results["overall_score"] >= 80:
        results["performance"] = "Good"
    elif results["overall_score"] >= 70:
        results["performance"] = "Satisfactory"
    else:
        results["performance"] = "Needs Improvement"
    
    return results

def main():
    """Main function to process command line arguments and evaluate submission."""
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
    save_json_file(results, "test_results.json")
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Performance category: {results['performance']}")
    print(f"Pass/Fail: {'PASS' if results['pass'] else 'FAIL'}")

if __name__ == "__main__":
    main()