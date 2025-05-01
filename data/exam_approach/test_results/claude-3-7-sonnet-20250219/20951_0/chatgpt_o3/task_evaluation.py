#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_treaty_analysis(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the treaty analysis section."""
    score = 0
    max_score = 25
    feedback = []
    
    # Extract key terms from both submission and answer key
    sub_terms = {term["term_id"]: term for term in submission.get("treaty_analysis", {}).get("key_terms", [])}
    key_terms = {term["term_id"]: term for term in answer_key.get("treaty_analysis", {}).get("key_terms", [])}
    
    # Check if the correct number of terms were identified
    if len(sub_terms) != 5:
        feedback.append(f"Expected 5 key terms, found {len(sub_terms)}.")
    
    # Count correctly identified terms
    correct_terms = 0
    for term_id, term_data in sub_terms.items():
        if term_id in key_terms:
            correct_terms += 1
            
            # Check if favorable assessment is correct
            if term_data.get("favorable") == key_terms[term_id].get("favorable"):
                score += 2.5  # 2.5 points for correct favorable/unfavorable assessment
                feedback.append(f"Correctly identified {term_id} as {'favorable' if term_data.get('favorable') else 'unfavorable'}.")
            else:
                feedback.append(f"Incorrectly assessed {term_id} as {'favorable' if term_data.get('favorable') else 'unfavorable'}.")
            
            # Check rationale quality (subjective, simplified scoring)
            sub_rationale = term_data.get("rationale", "").lower()
            key_rationale_keywords = set(key_terms[term_id].get("rationale", "").lower().split())
            
            # Count matching keywords to assess rationale quality
            matching_keywords = sum(1 for word in key_rationale_keywords if word in sub_rationale)
            rationale_score = min(2.5, (matching_keywords / max(1, len(key_rationale_keywords))) * 2.5)
            score += rationale_score
            
            if rationale_score >= 1.5:
                feedback.append(f"Provided good rationale for {term_id}.")
            else:
                feedback.append(f"Rationale for {term_id} could be improved.")
        else:
            feedback.append(f"Term {term_id} was not identified as a key term in the answer key.")
    
    # Adjust score based on number of correctly identified terms
    if correct_terms < 4:
        score = score * (correct_terms / 4)
        feedback.append(f"Only identified {correct_terms} of the 5 key terms correctly.")
    
    return score, {"score": score, "max_score": max_score, "feedback": feedback}

def evaluate_financial_assessment(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the financial assessment section."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check expected ceded losses calculation
    sub_losses = submission.get("financial_assessment", {}).get("expected_ceded_losses", 0)
    key_losses = answer_key.get("financial_assessment", {}).get("expected_ceded_losses", 0)
    
    # Allow for 10% margin of error
    if abs(sub_losses - key_losses) <= 0.1 * key_losses:
        score += 6
        feedback.append(f"Expected ceded losses calculation is within acceptable range.")
    else:
        error_percentage = abs(sub_losses - key_losses) / key_losses * 100
        feedback.append(f"Expected ceded losses calculation is off by {error_percentage:.1f}%.")
        # Partial credit based on how close they were
        if error_percentage <= 20:
            score += 3
    
    # Check market comparison
    sub_rating = submission.get("financial_assessment", {}).get("market_comparison", {}).get("overall_rating", "")
    key_rating = answer_key.get("financial_assessment", {}).get("market_comparison", {}).get("overall_rating", "")
    
    if sub_rating == key_rating:
        score += 6
        feedback.append(f"Correctly assessed overall market rating as {key_rating}.")
    else:
        feedback.append(f"Incorrectly assessed overall market rating as {sub_rating} instead of {key_rating}.")
    
    # Check alternative impacts
    sub_alts = {alt["alternative_id"]: alt for alt in submission.get("financial_assessment", {}).get("alternative_impacts", [])}
    key_alts = {alt["alternative_id"]: alt for alt in answer_key.get("financial_assessment", {}).get("alternative_impacts", [])}
    
    alt_score = 0
    for alt_id, key_alt in key_alts.items():
        if alt_id in sub_alts:
            sub_alt = sub_alts[alt_id]
            
            # Check financial impact calculation
            if abs(sub_alt.get("financial_impact", 0) - key_alt.get("financial_impact", 0)) <= 50000:  # Allow $50k margin
                alt_score += 1
                feedback.append(f"Correctly calculated financial impact for {alt_id}.")
            else:
                feedback.append(f"Incorrect financial impact calculation for {alt_id}.")
            
            # Check pros and cons
            sub_pros = set(p.lower() for p in sub_alt.get("pros", []))
            key_pros = set(p.lower() for p in key_alt.get("pros", []))
            sub_cons = set(c.lower() for c in sub_alt.get("cons", []))
            key_cons = set(c.lower() for c in key_alt.get("cons", []))
            
            # Simple overlap check for pros and cons
            pros_overlap = any(any(key_p in sub_p for key_p in key_pros) for sub_p in sub_pros)
            cons_overlap = any(any(key_c in sub_c for key_c in key_cons) for sub_c in sub_cons)
            
            if pros_overlap:
                alt_score += 1
                feedback.append(f"Identified relevant pros for {alt_id}.")
            else:
                feedback.append(f"Pros for {alt_id} could be improved.")
                
            if cons_overlap:
                alt_score += 1
                feedback.append(f"Identified relevant cons for {alt_id}.")
            else:
                feedback.append(f"Cons for {alt_id} could be improved.")
    
    # Scale alternative score to 13 points (remaining points for this section)
    score += min(13, (alt_score / 9) * 13)  # 9 possible points (3 alts * 3 criteria)
    
    return score, {"score": score, "max_score": max_score, "feedback": feedback}

def evaluate_negotiation_strategy(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the negotiation strategy section."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check priority ranking
    sub_ranking = submission.get("negotiation_strategy", {}).get("priority_ranking", [])
    key_ranking = answer_key.get("negotiation_strategy", {}).get("priority_ranking", [])
    
    # Calculate priority ranking score based on position differences
    ranking_score = 0
    for i, term in enumerate(sub_ranking):
        if term in key_ranking:
            key_pos = key_ranking.index(term)
            pos_diff = abs(i - key_pos)
            if pos_diff == 0:
                ranking_score += 1  # Perfect position
            elif pos_diff == 1:
                ranking_score += 0.5  # Off by one position
    
    # Scale ranking score to 8 points
    ranking_points = min(8, (ranking_score / 5) * 8)
    score += ranking_points
    
    if ranking_points >= 6:
        feedback.append("Priority ranking is well aligned with the answer key.")
    elif ranking_points >= 4:
        feedback.append("Priority ranking has some alignment with the answer key.")
    else:
        feedback.append("Priority ranking needs significant improvement.")
    
    # Check positions (target and minimum)
    sub_positions = submission.get("negotiation_strategy", {}).get("positions", {})
    key_positions = answer_key.get("negotiation_strategy", {}).get("positions", {})
    
    position_score = 0
    for term_id, key_pos in key_positions.items():
        if term_id in sub_positions:
            sub_pos = sub_positions[term_id]
            
            # Simple text comparison for target and minimum positions
            # This is simplified - in a real evaluation, you'd want more sophisticated comparison
            sub_target = sub_pos.get("target", "").lower()
            key_target = key_pos.get("target", "").lower()
            sub_min = sub_pos.get("minimum", "").lower()
            key_min = key_pos.get("minimum", "").lower()
            
            target_match = any(word in sub_target for word in key_target.split() if len(word) > 4)
            min_match = any(word in sub_min for word in key_min.split() if len(word) > 4)
            
            if target_match:
                position_score += 1
            if min_match:
                position_score += 1
    
    # Scale position score to 10 points
    position_points = min(10, (position_score / 10) * 10)  # 10 possible points (5 terms * 2 positions)
    score += position_points
    
    if position_points >= 7:
        feedback.append("Target and minimum positions are well defined and reasonable.")
    elif position_points >= 4:
        feedback.append("Some target and minimum positions need refinement.")
    else:
        feedback.append("Target and minimum positions need significant improvement.")
    
    # Check concessions
    sub_concessions = submission.get("negotiation_strategy", {}).get("concessions", [])
    key_concessions = answer_key.get("negotiation_strategy", {}).get("concessions", [])
    
    # Check if the correct number of concessions were provided
    if len(sub_concessions) != 3:
        feedback.append(f"Expected 3 concessions, found {len(sub_concessions)}.")
    
    # Simple check for reasonable concessions
    concession_score = 0
    for sub_con in sub_concessions:
        sub_item = sub_con.get("concession_item", "").lower()
        sub_rationale = sub_con.get("rationale", "").lower()
        
        # Check if this concession appears reasonable compared to any in the key
        for key_con in key_concessions:
            key_item = key_con.get("concession_item", "").lower()
            
            if any(word in sub_item for word in key_item.split() if len(word) > 4):
                concession_score += 1
                break
        
        # Check if rationale is provided and reasonable
        if len(sub_rationale) > 20:  # Simple length check
            concession_score += 0.5
    
    # Scale concession score to 7 points
    concession_points = min(7, (concession_score / 4.5) * 7)  # 4.5 possible points (3 concessions * 1.5)
    score += concession_points
    
    if concession_points >= 5:
        feedback.append("Concessions are reasonable and well justified.")
    elif concession_points >= 3:
        feedback.append("Some concessions need better justification.")
    else:
        feedback.append("Concessions need significant improvement.")
    
    return score, {"score": score, "max_score": max_score, "feedback": feedback}

def evaluate_counterparty_response(submission: Dict, answer_key: Dict) -> Tuple[float, Dict]:
    """Evaluate the counterparty response section."""
    score = 0
    max_score = 25
    feedback = []
    
    # Check key points
    sub_points = submission.get("counterparty_response", {}).get("key_points", [])
    key_points = answer_key.get("counterparty_response", {}).get("key_points", [])
    
    # Check if an appropriate number of key points were identified
    if not 3 <= len(sub_points) <= 5:
        feedback.append(f"Expected 3-5 key points, found {len(sub_points)}.")
    
    # Simple check for overlap in key points
    point_score = 0
    for sub_point in sub_points:
        sub_point_lower = sub_point.lower()
        
        # Check if this point appears similar to any in the key
        for key_point in key_points:
            key_point_lower = key_point.lower()
            
            # Simple word overlap check
            if any(word in sub_point_lower for word in key_point_lower.split() if len(word) > 4):
                point_score += 1
                break
    
    # Scale point score to 10 points
    point_points = min(10, (point_score / 5) * 10)  # 5 possible points (5 key points)
    score += point_points
    
    if point_points >= 7:
        feedback.append("Key points effectively address the counterparty's concerns.")
    elif point_points >= 4:
        feedback.append("Some key points need refinement to better address counterparty concerns.")
    else:
        feedback.append("Key points need significant improvement.")
    
    # Check proposed modifications
    sub_mods = submission.get("counterparty_response", {}).get("proposed_modifications", [])
    key_mods = answer_key.get("counterparty_response", {}).get("proposed_modifications", [])
    
    # Check if at least 3 modifications were proposed
    if len(sub_mods) < 3:
        feedback.append(f"Expected at least 3 proposed modifications, found {len(sub_mods)}.")
    
    # Evaluate each proposed modification
    mod_score = 0
    for sub_mod in sub_mods:
        sub_term = sub_mod.get("term_id", "")
        
        # Find matching term in key
        matching_key_mod = next((m for m in key_mods if m.get("term_id") == sub_term), None)
        
        if matching_key_mod:
            # Check if current language is correctly identified
            if sub_mod.get("current_language", "").lower() in matching_key_mod.get("current_language", "").lower():
                mod_score += 1
                feedback.append(f"Correctly identified current language for {sub_term}.")
            
            # Check if proposed language is reasonable
            sub_proposed = sub_mod.get("proposed_language", "").lower()
            key_proposed = matching_key_mod.get("proposed_language", "").lower()
            
            # Simple check for similarity in proposed language
            if any(word in sub_proposed for word in key_proposed.split() if len(word) > 4):
                mod_score += 1
                feedback.append(f"Proposed reasonable alternative language for {sub_term}.")
            
            # Check justification
            sub_justification = sub_mod.get("justification", "").lower()
            key_justification = matching_key_mod.get("justification", "").lower()
            
            # Simple check for justification quality
            if len(sub_justification) > 50 and any(word in sub_justification for word in key_justification.split() if len(word) > 4):
                mod_score += 1
                feedback.append(f"Provided good justification for {sub_term} modification.")
        else:
            feedback.append(f"Term {sub_term} was not identified as a key modification in the answer key.")
    
    # Scale modification score to 15 points
    mod_points = min(15, (mod_score / 12) * 15)  # 12 possible points (4 mods * 3 criteria)
    score += mod_points
    
    if mod_points >= 10:
        feedback.append("Proposed modifications are well structured and justified.")
    elif mod_points >= 6:
        feedback.append("Some proposed modifications need better justification or language.")
    else:
        feedback.append("Proposed modifications need significant improvement.")
    
    return score, {"score": score, "max_score": max_score, "feedback": feedback}

def evaluate_submission(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate the entire submission against the answer key."""
    results = {
        "overall_score": 0,
        "sections": {}
    }
    
    # Evaluate each section
    treaty_score, treaty_results = evaluate_treaty_analysis(submission, answer_key)
    financial_score, financial_results = evaluate_financial_assessment(submission, answer_key)
    negotiation_score, negotiation_results = evaluate_negotiation_strategy(submission, answer_key)
    counterparty_score, counterparty_results = evaluate_counterparty_response(submission, answer_key)
    
    # Store section results
    results["sections"]["treaty_analysis"] = treaty_results
    results["sections"]["financial_assessment"] = financial_results
    results["sections"]["negotiation_strategy"] = negotiation_results
    results["sections"]["counterparty_response"] = counterparty_results
    
    # Calculate overall score
    total_score = treaty_score + financial_score + negotiation_score + counterparty_score
    total_possible = 100  # 25 points per section * 4 sections
    
    results["overall_score"] = round((total_score / total_possible) * 100, 2)
    
    # Add pass/fail determination
    results["passed"] = results["overall_score"] >= 70 and all(
        section["score"] / section["max_score"] >= 0.6 
        for section in results["sections"].values()
    )
    
    # Add overall feedback
    if results["passed"]:
        if results["overall_score"] >= 90:
            results["overall_feedback"] = "Exceptional performance! Demonstrates sophisticated understanding of reinsurance negotiation."
        elif results["overall_score"] >= 80:
            results["overall_feedback"] = "Strong performance. Shows good understanding of reinsurance negotiation principles."
        else:
            results["overall_feedback"] = "Satisfactory performance. Demonstrates basic competency in reinsurance negotiation."
    else:
        if results["overall_score"] >= 60:
            results["overall_feedback"] = "Not passing. Shows some understanding but needs improvement in specific areas."
        else:
            results["overall_feedback"] = "Not passing. Significant improvement needed across multiple areas."
    
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
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()