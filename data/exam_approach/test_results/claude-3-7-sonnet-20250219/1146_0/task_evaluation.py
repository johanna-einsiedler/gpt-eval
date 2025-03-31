import json
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

def text_similarity(text1, text2):
    """Calculate similarity between two text strings"""
    if not text1 or not text2:
        return 0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def evaluate_exercise1(candidate_answers, key_answers):
    """Evaluate the regulatory research exercise"""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Check if the candidate provided the correct number of provisions
    candidate_provisions = candidate_answers.get("relevantProvisions", [])
    key_provisions = key_answers.get("relevantProvisions", [])
    
    # Track which key provisions have been matched
    matched_key_provisions = [False] * len(key_provisions)
    
    # For each candidate provision, find the best matching key provision
    for candidate_provision in candidate_provisions:
        candidate_far = candidate_provision.get("farReference", "")
        candidate_title = candidate_provision.get("title", "")
        candidate_application = candidate_provision.get("applicationToScenario", "")
        
        best_match_index = -1
        best_match_score = 0
        
        # Find the best matching key provision
        for i, key_provision in enumerate(key_provisions):
            if matched_key_provisions[i]:
                continue  # Skip already matched provisions
                
            key_far = key_provision.get("farReference", "")
            
            # If FAR reference matches exactly, this is a strong match
            if candidate_far == key_far:
                match_score = 0.8  # High base score for matching FAR reference
                
                # Add points for title similarity
                title_similarity = text_similarity(candidate_title, key_provision.get("title", ""))
                match_score += 0.1 * title_similarity
                
                # Add points for application explanation similarity
                app_similarity = text_similarity(candidate_application, key_provision.get("applicationToScenario", ""))
                match_score += 0.1 * app_similarity
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_index = i
            else:
                # Check for partial matches
                far_similarity = text_similarity(candidate_far, key_far)
                title_similarity = text_similarity(candidate_title, key_provision.get("title", ""))
                app_similarity = text_similarity(candidate_application, key_provision.get("applicationToScenario", ""))
                
                match_score = 0.5 * far_similarity + 0.2 * title_similarity + 0.3 * app_similarity
                
                if match_score > 0.7 and match_score > best_match_score:
                    best_match_score = match_score
                    best_match_index = i
        
        # Record the results for this provision
        provision_result = {
            "candidateProvision": candidate_provision,
            "matchScore": round(best_match_score, 2),
            "points": 0
        }
        
        if best_match_index >= 0:
            provision_result["matchedKeyProvision"] = key_provisions[best_match_index]
            matched_key_provisions[best_match_index] = True
            
            # Calculate points (max 3.33 points per provision)
            far_correct = candidate_far == key_provisions[best_match_index].get("farReference", "")
            title_correct = text_similarity(candidate_title, key_provisions[best_match_index].get("title", "")) > 0.8
            app_correct = text_similarity(candidate_application, key_provisions[best_match_index].get("applicationToScenario", "")) > 0.7
            
            points = 0
            if far_correct:
                points += 1.33
            if title_correct:
                points += 1
            if app_correct:
                points += 1
                
            provision_result["points"] = round(points, 2)
            results["score"] += points
        else:
            provision_result["matchedKeyProvision"] = None
            provision_result["points"] = 0
            
        results["details"].append(provision_result)
    
    # Round the final score
    results["score"] = round(min(results["score"], 10), 2)
    return results

def evaluate_exercise2(candidate_answers, key_answers):
    """Evaluate the compliance analysis case study"""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Check if the candidate provided the correct number of issues
    candidate_issues = candidate_answers.get("complianceIssues", [])
    key_issues = key_answers.get("complianceIssues", [])
    
    # Track which key issues have been matched
    matched_key_issues = [False] * len(key_issues)
    
    # For each candidate issue, find the best matching key issue
    for candidate_issue in candidate_issues:
        candidate_desc = candidate_issue.get("issueDescription", "")
        candidate_reg = candidate_issue.get("regulationViolated", "")
        candidate_action = candidate_issue.get("correctiveAction", "")
        
        best_match_index = -1
        best_match_score = 0
        
        # Find the best matching key issue
        for i, key_issue in enumerate(key_issues):
            if matched_key_issues[i]:
                continue  # Skip already matched issues
                
            key_desc = key_issue.get("issueDescription", "")
            key_reg = key_issue.get("regulationViolated", "")
            key_action = key_issue.get("correctiveAction", "")
            
            # Calculate similarity scores
            desc_similarity = text_similarity(candidate_desc, key_desc)
            reg_similarity = text_similarity(candidate_reg, key_reg)
            action_similarity = text_similarity(candidate_action, key_action)
            
            # Weight the scores
            match_score = 0.4 * desc_similarity + 0.3 * reg_similarity + 0.3 * action_similarity
            
            if match_score > 0.6 and match_score > best_match_score:
                best_match_score = match_score
                best_match_index = i
        
        # Record the results for this issue
        issue_result = {
            "candidateIssue": candidate_issue,
            "matchScore": round(best_match_score, 2),
            "points": 0
        }
        
        if best_match_index >= 0:
            issue_result["matchedKeyIssue"] = key_issues[best_match_index]
            matched_key_issues[best_match_index] = True
            
            # Calculate points (max 3.33 points per issue)
            desc_correct = text_similarity(candidate_desc, key_issues[best_match_index].get("issueDescription", "")) > 0.7
            reg_correct = text_similarity(candidate_reg, key_issues[best_match_index].get("regulationViolated", "")) > 0.7
            action_correct = text_similarity(candidate_action, key_issues[best_match_index].get("correctiveAction", "")) > 0.7
            
            points = 0
            if desc_correct:
                points += 1.11
            if reg_correct:
                points += 1.11
            if action_correct:
                points += 1.11
                
            issue_result["points"] = round(points, 2)
            results["score"] += points
        else:
            issue_result["matchedKeyIssue"] = None
            issue_result["points"] = 0
            
        results["details"].append(issue_result)
    
    # Round the final score
    results["score"] = round(min(results["score"], 10), 2)
    return results

def evaluate_exercise3(candidate_answers, key_answers):
    """Evaluate the regulatory decision-making simulation"""
    results = {
        "score": 0,
        "max_score": 10,
        "details": []
    }
    
    # Get candidate and key scenarios
    candidate_scenarios = candidate_answers.get("scenarioDecisions", [])
    key_scenarios = key_answers.get("scenarioDecisions", [])
    
    # Create a dictionary of key scenarios by scenario number
    key_scenarios_dict = {scenario.get("scenarioNumber"): scenario for scenario in key_scenarios}
    
    # Evaluate each candidate scenario
    for candidate_scenario in candidate_scenarios:
        scenario_num = candidate_scenario.get("scenarioNumber")
        
        if scenario_num not in key_scenarios_dict:
            continue
            
        key_scenario = key_scenarios_dict[scenario_num]
        
        # Evaluate each aspect of the scenario
        is_compliant_correct = candidate_scenario.get("isCompliant") == key_scenario.get("isCompliant")
        
        # Evaluate applicable regulations
        candidate_regs = set(candidate_scenario.get("applicableRegulations", []))
        key_regs = set(key_scenario.get("applicableRegulations", []))
        
        # Calculate regulation match score
        reg_match_score = 0
        if len(candidate_regs) > 0 and len(key_regs) > 0:
            # Check for exact matches
            exact_matches = candidate_regs.intersection(key_regs)
            
            # Check for partial matches in remaining regulations
            remaining_candidate_regs = candidate_regs - exact_matches
            remaining_key_regs = key_regs - exact_matches
            
            partial_matches = 0
            for c_reg in remaining_candidate_regs:
                for k_reg in remaining_key_regs:
                    if text_similarity(c_reg, k_reg) > 0.7:
                        partial_matches += 1
                        break
            
            reg_match_score = (len(exact_matches) + 0.7 * partial_matches) / max(len(key_regs), 1)
        
        # Evaluate correct action
        action_similarity = text_similarity(
            candidate_scenario.get("correctAction", ""),
            key_scenario.get("correctAction", "")
        )
        
        # Calculate points for this scenario (max 2.5 points per scenario)
        points = 0
        if is_compliant_correct:
            points += 0.75
        
        points += 0.75 * min(reg_match_score, 1)
        
        if action_similarity > 0.7:
            points += 1
        
        # Record the results for this scenario
        scenario_result = {
            "scenarioNumber": scenario_num,
            "candidateScenario": candidate_scenario,
            "keyScenario": key_scenario,
            "isCompliantCorrect": is_compliant_correct,
            "regulationMatchScore": round(reg_match_score, 2),
            "actionSimilarity": round(action_similarity, 2),
            "points": round(points, 2)
        }
        
        results["score"] += points
        results["details"].append(scenario_result)
    
    # Round the final score
    results["score"] = round(min(results["score"], 10), 2)
    return results

def main():
    # Load the candidate submission and answer key
    candidate_submission = load_json_file("test_submission.json")
    answer_key = load_json_file("answer_key.json")
    
    if not candidate_submission or not answer_key:
        print("Failed to load required files. Exiting.")
        return
    
    # Initialize results structure
    results = {
        "candidateId": candidate_submission.get("candidateId", "Unknown"),
        "exercise1": evaluate_exercise1(
            candidate_submission.get("exercise1", {}),
            answer_key.get("exercise1", {})
        ),
        "exercise2": evaluate_exercise2(
            candidate_submission.get("exercise2", {}),
            answer_key.get("exercise2", {})
        ),
        "exercise3": evaluate_exercise3(
            candidate_submission.get("exercise3", {}),
            answer_key.get("exercise3", {})
        )
    }
    
    # Calculate overall score
    total_score = results["exercise1"]["score"] + results["exercise2"]["score"] + results["exercise3"]["score"]
    total_possible = results["exercise1"]["max_score"] + results["exercise2"]["max_score"] + results["exercise3"]["max_score"]
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    # Add pass/fail status based on 70% threshold
    results["passed"] = results["overall_score"] >= 70
    
    # Save the results
    save_json_file(results, "test_results.json")

if __name__ == "__main__":
    main()