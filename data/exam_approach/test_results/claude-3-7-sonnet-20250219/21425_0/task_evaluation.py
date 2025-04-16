#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Union, Tuple

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' contains invalid JSON.")
        sys.exit(1)

def evaluate_coverage_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the coverage analysis section (35% of total score)."""
    sub_coverage = submission.get("coverage_analysis", {})
    key_coverage = answer_key.get("coverage_analysis", {})
    
    results = {
        "section_name": "Coverage Analysis",
        "weight": 35,
        "items": [],
        "section_score": 0
    }
    
    # Coverage determination (yes/no) - Critical element
    correct_determination = sub_coverage.get("coverage_determination") == key_coverage.get("coverage_determination")
    results["items"].append({
        "name": "Coverage Determination",
        "correct": correct_determination,
        "weight": 10,
        "score": 10 if correct_determination else 0,
        "expected": key_coverage.get("coverage_determination"),
        "submitted": sub_coverage.get("coverage_determination"),
        "critical_element": True
    })
    
    # Coverage issues
    sub_issues = set(issue.lower().strip() for issue in sub_coverage.get("coverage_issues", []))
    key_issues = set(issue.lower().strip() for issue in key_coverage.get("coverage_issues", []))
    
    # Calculate coverage issues overlap
    identified_issues = len(sub_issues.intersection(key_issues))
    total_key_issues = len(key_issues)
    issues_score = 10 * (identified_issues / total_key_issues) if total_key_issues > 0 else 0
    
    business_use_identified = any("business" in issue.lower() and ("delivery" in issue.lower() or "delivering" in issue.lower()) 
                                for issue in sub_issues)
    
    results["items"].append({
        "name": "Coverage Issues Identification",
        "correct": business_use_identified,
        "weight": 10,
        "score": issues_score,
        "expected": key_coverage.get("coverage_issues"),
        "submitted": sub_coverage.get("coverage_issues"),
        "critical_element": True,
        "notes": "Business use exclusion identification is critical"
    })
    
    # Applicable policy sections
    sub_sections = set(section.lower().strip() for section in sub_coverage.get("applicable_policy_sections", []))
    key_sections = set(section.lower().strip() for section in key_coverage.get("applicable_policy_sections", []))
    
    sections_overlap = len(sub_sections.intersection(key_sections))
    total_key_sections = len(key_sections)
    sections_score = 8 * (sections_overlap / total_key_sections) if total_key_sections > 0 else 0
    
    results["items"].append({
        "name": "Policy Sections Applied",
        "correct": sections_overlap == total_key_sections,
        "weight": 8,
        "score": sections_score,
        "expected": key_coverage.get("applicable_policy_sections"),
        "submitted": sub_coverage.get("applicable_policy_sections")
    })
    
    # Exclusions applied
    sub_exclusions = set(excl.lower().strip() for excl in sub_coverage.get("exclusions_applied", []))
    key_exclusions = set(excl.lower().strip() for excl in key_coverage.get("exclusions_applied", []))
    
    exclusions_overlap = len(sub_exclusions.intersection(key_exclusions))
    total_key_exclusions = len(key_exclusions)
    exclusions_score = 7 * (exclusions_overlap / total_key_exclusions) if total_key_exclusions > 0 else 0
    
    results["items"].append({
        "name": "Exclusions Applied",
        "correct": exclusions_overlap == total_key_exclusions,
        "weight": 7,
        "score": exclusions_score,
        "expected": key_coverage.get("exclusions_applied"),
        "submitted": sub_coverage.get("exclusions_applied")
    })
    
    # Calculate section score
    results["section_score"] = sum(item["score"] for item in results["items"])
    
    return results

def evaluate_liability_assessment(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the liability assessment section (25% of total score)."""
    sub_liability = submission.get("liability_assessment", {})
    key_liability = answer_key.get("liability_assessment", {})
    
    results = {
        "section_name": "Liability Assessment",
        "weight": 25,
        "items": [],
        "section_score": 0
    }
    
    # Insured liability percentage - Critical element
    sub_insured_liability = sub_liability.get("insured_liability_percentage", 0)
    key_insured_liability = key_liability.get("insured_liability_percentage", 0)
    
    # Allow 15% variance in liability assessment
    liability_variance = abs(sub_insured_liability - key_insured_liability)
    liability_acceptable = liability_variance <= 15
    
    # Check if insured has majority liability (critical error)
    insured_majority_liability = sub_insured_liability > 50
    
    liability_score = 0
    if liability_acceptable:
        # Calculate score based on how close to the key value
        max_variance = 15
        liability_score = 10 * (1 - (liability_variance / max_variance)) if liability_variance < max_variance else 0
    
    results["items"].append({
        "name": "Insured Liability Percentage",
        "correct": liability_acceptable,
        "weight": 10,
        "score": liability_score,
        "expected": key_insured_liability,
        "submitted": sub_insured_liability,
        "critical_element": True,
        "critical_failure": insured_majority_liability,
        "notes": "Assigning majority liability to insured is an automatic failure"
    })
    
    # Other parties' liability
    sub_others = {party.get("name", "").lower().strip(): party.get("percentage", 0) 
                 for party in sub_liability.get("other_parties_liability", [])}
    key_others = {party.get("name", "").lower().strip(): party.get("percentage", 0) 
                 for party in key_liability.get("other_parties_liability", [])}
    
    # Check for each key party
    other_party_score = 0
    max_other_score = 10
    parties_evaluated = 0
    
    for key_name, key_percentage in key_others.items():
        # Find closest matching name in submission
        best_match = None
        best_match_score = 0
        
        for sub_name in sub_others.keys():
            # Simple name matching logic
            if key_name in sub_name or sub_name in key_name:
                match_score = len(set(key_name.split()).intersection(set(sub_name.split()))) / max(len(key_name.split()), len(sub_name.split()))
                if match_score > best_match_score:
                    best_match = sub_name
                    best_match_score = match_score
        
        if best_match and best_match_score > 0.5:
            sub_percentage = sub_others[best_match]
            percentage_variance = abs(sub_percentage - key_percentage)
            percentage_acceptable = percentage_variance <= 15
            
            if percentage_acceptable:
                max_variance = 15
                party_score = (1 - (percentage_variance / max_variance)) if percentage_variance < max_variance else 0
                other_party_score += party_score
            
            parties_evaluated += 1
    
    # Calculate average score if any parties were evaluated
    if parties_evaluated > 0:
        other_party_score = (other_party_score / parties_evaluated) * max_other_score
    
    results["items"].append({
        "name": "Other Parties Liability",
        "correct": other_party_score >= max_other_score * 0.8,
        "weight": 10,
        "score": other_party_score,
        "expected": key_liability.get("other_parties_liability"),
        "submitted": sub_liability.get("other_parties_liability")
    })
    
    # Liability rationale
    sub_rationale = sub_liability.get("liability_rationale", "").lower()
    key_elements = ["red light", "citation", "witness"]
    
    rationale_score = 0
    max_rationale_score = 5
    
    # Check for key elements in rationale
    elements_found = sum(1 for element in key_elements if element in sub_rationale)
    if elements_found > 0:
        rationale_score = max_rationale_score * (elements_found / len(key_elements))
    
    results["items"].append({
        "name": "Liability Rationale",
        "correct": rationale_score >= 0.6 * max_rationale_score,
        "weight": 5,
        "score": rationale_score,
        "expected": key_liability.get("liability_rationale"),
        "submitted": sub_liability.get("liability_rationale")
    })
    
    # Calculate section score
    results["section_score"] = sum(item["score"] for item in results["items"])
    
    return results

def evaluate_damages(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the damages evaluation section (20% of total score)."""
    sub_damages = submission.get("damages_evaluation", {})
    key_damages = answer_key.get("damages_evaluation", {})
    
    results = {
        "section_name": "Damages Evaluation",
        "weight": 20,
        "items": [],
        "section_score": 0
    }
    
    # Process claimant reserves
    sub_reserves = {res.get("claimant_name", "").lower().strip(): res 
                   for res in sub_damages.get("claimant_reserves", [])}
    key_reserves = {res.get("claimant_name", "").lower().strip(): res 
                   for res in key_damages.get("claimant_reserves", [])}
    
    claimant_scores = []
    sarah_jones_adequately_reserved = False
    
    for key_name, key_reserve in key_reserves.items():
        # Find closest matching name in submission
        best_match = None
        best_match_score = 0
        
        for sub_name in sub_reserves.keys():
            # Simple name matching logic
            if key_name in sub_name or sub_name in key_name:
                match_score = len(set(key_name.split()).intersection(set(sub_name.split()))) / max(len(key_name.split()), len(sub_name.split()))
                if match_score > best_match_score:
                    best_match = sub_name
                    best_match_score = match_score
        
        if best_match and best_match_score > 0.5:
            sub_reserve = sub_reserves[best_match]
            
            # Check total reserve
            key_total = key_reserve.get("total_reserve", 0)
            sub_total = sub_reserve.get("total_reserve", 0)
            
            # Calculate variance percentage
            variance_pct = abs(sub_total - key_total) / key_total if key_total > 0 else 1
            reserve_acceptable = variance_pct <= 0.3  # 30% variance allowed
            
            # Special check for Sarah Jones (critical element)
            if "sarah" in key_name and "jones" in key_name:
                sarah_jones_adequately_reserved = sub_total >= key_total * 0.7  # Within 30% of expected
                
                claimant_scores.append({
                    "name": key_name,
                    "correct": reserve_acceptable,
                    "expected": key_total,
                    "submitted": sub_total,
                    "score": 1 - min(variance_pct, 0.3) / 0.3 if reserve_acceptable else 0,
                    "critical_element": True,
                    "critical_failure": not sarah_jones_adequately_reserved,
                    "notes": "Sarah Jones must be adequately reserved (within 30% of expected)"
                })
            else:
                claimant_scores.append({
                    "name": key_name,
                    "correct": reserve_acceptable,
                    "expected": key_total,
                    "submitted": sub_total,
                    "score": 1 - min(variance_pct, 0.3) / 0.3 if reserve_acceptable else 0
                })
        else:
            # Claimant not found in submission
            claimant_scores.append({
                "name": key_name,
                "correct": False,
                "expected": key_reserve.get("total_reserve", 0),
                "submitted": "Not found",
                "score": 0
            })
            
            # Check if missing claimant is Sarah Jones
            if "sarah" in key_name and "jones" in key_name:
                sarah_jones_adequately_reserved = False
    
    # Calculate overall claimant score
    total_claimant_score = sum(item["score"] for item in claimant_scores)
    max_claimant_score = len(claimant_scores)
    claimant_percentage = (total_claimant_score / max_claimant_score) if max_claimant_score > 0 else 0
    final_claimant_score = 15 * claimant_percentage
    
    results["items"].append({
        "name": "Claimant Reserve Accuracy",
        "correct": claimant_percentage >= 0.7,
        "weight": 15,
        "score": final_claimant_score,
        "expected": key_damages.get("claimant_reserves"),
        "submitted": sub_damages.get("claimant_reserves"),
        "details": claimant_scores
    })
    
    # Total claim reserve
    key_total = key_damages.get("total_claim_reserve", 0)
    sub_total = sub_damages.get("total_claim_reserve", 0)
    
    # Calculate variance percentage
    total_variance_pct = abs(sub_total - key_total) / key_total if key_total > 0 else 1
    total_acceptable = total_variance_pct <= 0.2  # 20% variance allowed
    
    total_score = 0
    if total_acceptable:
        total_score = 5 * (1 - (total_variance_pct / 0.2))
    
    results["items"].append({
        "name": "Total Claim Reserve",
        "correct": total_acceptable,
        "weight": 5,
        "score": total_score,
        "expected": key_total,
        "submitted": sub_total
    })
    
    # Calculate section score
    results["section_score"] = sum(item["score"] for item in results["items"])
    
    return results, sarah_jones_adequately_reserved

def evaluate_settlement_strategy(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the settlement strategy section (15% of total score)."""
    sub_strategy = submission.get("settlement_strategy", {})
    key_strategy = answer_key.get("settlement_strategy", {})
    
    results = {
        "section_name": "Settlement Strategy",
        "weight": 15,
        "items": [],
        "section_score": 0
    }
    
    # Process settlement recommendations
    sub_settlements = {rec.get("claimant_name", "").lower().strip(): rec 
                      for rec in sub_strategy.get("settlement_recommendations", [])}
    key_settlements = {rec.get("claimant_name", "").lower().strip(): rec 
                      for rec in key_strategy.get("settlement_recommendations", [])}
    
    settlement_scores = []
    
    for key_name, key_settlement in key_settlements.items():
        # Find closest matching name in submission
        best_match = None
        best_match_score = 0
        
        for sub_name in sub_settlements.keys():
            # Simple name matching logic
            if key_name in sub_name or sub_name in key_name:
                match_score = len(set(key_name.split()).intersection(set(sub_name.split()))) / max(len(key_name.split()), len(sub_name.split()))
                if match_score > best_match_score:
                    best_match = sub_name
                    best_match_score = match_score
        
        if best_match and best_match_score > 0.5:
            sub_settlement = sub_settlements[best_match]
            
            # Check min and max settlement values
            key_min = key_settlement.get("minimum_settlement", 0)
            key_max = key_settlement.get("maximum_settlement", 0)
            sub_min = sub_settlement.get("minimum_settlement", 0)
            sub_max = sub_settlement.get("maximum_settlement", 0)
            
            # Calculate variance percentages
            min_variance_pct = abs(sub_min - key_min) / key_min if key_min > 0 else 1
            max_variance_pct = abs(sub_max - key_max) / key_max if key_max > 0 else 1
            
            min_acceptable = min_variance_pct <= 0.3  # 30% variance allowed
            max_acceptable = max_variance_pct <= 0.3  # 30% variance allowed
            
            min_score = 1 - min(min_variance_pct, 0.3) / 0.3 if min_acceptable else 0
            max_score = 1 - min(max_variance_pct, 0.3) / 0.3 if max_acceptable else 0
            
            # Check settlement factors
            sub_factors = [f.lower().strip() for f in sub_settlement.get("settlement_factors", [])]
            key_factors = [f.lower().strip() for f in key_settlement.get("settlement_factors", [])]
            
            factor_matches = 0
            for key_factor in key_factors:
                # Check for partial matches in any submission factor
                if any(key_factor in sub_factor or sub_factor in key_factor for sub_factor in sub_factors):
                    factor_matches += 1
            
            factor_score = factor_matches / len(key_factors) if key_factors else 0
            
            # Overall score for this claimant
            claimant_score = (min_score + max_score + factor_score) / 3
            
            settlement_scores.append({
                "name": key_name,
                "correct": claimant_score >= 0.7,
                "expected_min": key_min,
                "expected_max": key_max,
                "submitted_min": sub_min,
                "submitted_max": sub_max,
                "score": claimant_score
            })
        else:
            # Claimant not found in submission
            settlement_scores.append({
                "name": key_name,
                "correct": False,
                "expected_min": key_settlement.get("minimum_settlement", 0),
                "expected_max": key_settlement.get("maximum_settlement", 0),
                "submitted_min": "Not found",
                "submitted_max": "Not found",
                "score": 0
            })
    
    # Calculate overall settlement score
    total_settlement_score = sum(item["score"] for item in settlement_scores)
    max_settlement_score = len(settlement_scores)
    settlement_percentage = (total_settlement_score / max_settlement_score) if max_settlement_score > 0 else 0
    final_settlement_score = 15 * settlement_percentage
    
    results["items"].append({
        "name": "Settlement Recommendations",
        "correct": settlement_percentage >= 0.7,
        "weight": 15,
        "score": final_settlement_score,
        "expected": key_strategy.get("settlement_recommendations"),
        "submitted": sub_strategy.get("settlement_recommendations"),
        "details": settlement_scores
    })
    
    # Calculate section score
    results["section_score"] = sum(item["score"] for item in results["items"])
    
    return results

def evaluate_claim_classification(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the claim classification section (5% of total score)."""
    sub_class = submission.get("claim_classification", {})
    key_class = answer_key.get("claim_classification", {})
    
    results = {
        "section_name": "Claim Classification",
        "weight": 5,
        "items": [],
        "section_score": 0
    }
    
    # Liability code
    liability_correct = sub_class.get("liability_code") == key_class.get("liability_code")
    results["items"].append({
        "name": "Liability Code",
        "correct": liability_correct,
        "weight": 1,
        "score": 1 if liability_correct else 0,
        "expected": key_class.get("liability_code"),
        "submitted": sub_class.get("liability_code")
    })
    
    # Severity code
    severity_correct = sub_class.get("severity_code") == key_class.get("severity_code")
    results["items"].append({
        "name": "Severity Code",
        "correct": severity_correct,
        "weight": 1,
        "score": 1 if severity_correct else 0,
        "expected": key_class.get("severity_code"),
        "submitted": sub_class.get("severity_code")
    })
    
    # Coverage code
    coverage_correct = sub_class.get("coverage_code") == key_class.get("coverage_code")
    results["items"].append({
        "name": "Coverage Code",
        "correct": coverage_correct,
        "weight": 1,
        "score": 1 if coverage_correct else 0,
        "expected": key_class.get("coverage_code"),
        "submitted": sub_class.get("coverage_code")
    })
    
    # Final classification
    final_correct = sub_class.get("final_classification") == key_class.get("final_classification")
    results["items"].append({
        "name": "Final Classification",
        "correct": final_correct,
        "weight": 2,
        "score": 2 if final_correct else 0,
        "expected": key_class.get("final_classification"),
        "submitted": sub_class.get("final_classification")
    })
    
    # Calculate section score
    results["section_score"] = sum(item["score"] for item in results["items"])
    
    return results

def check_critical_elements(sections: List[Dict[str, Any]], sarah_jones_adequately_reserved: bool) -> Tuple[bool, List[str]]:
    """Check if any critical elements failed."""
    critical_failures = []
    
    for section in sections:
        for item in section.get("items", []):
            if item.get("critical_element") and item.get("critical_failure", False):
                critical_failures.append(f"{section['section_name']} - {item['name']}: {item.get('notes', 'Critical failure')}")
    
    # Special check for Sarah Jones reserves
    if not sarah_jones_adequately_reserved:
        critical_failures.append("Damages Evaluation - Sarah Jones reserves are grossly inadequate (automatic failure)")
    
    return len(critical_failures) == 0, critical_failures

def evaluate_submission(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the complete submission."""
    # Run individual section evaluations
    coverage_results = evaluate_coverage_analysis(submission, answer_key)
    liability_results = evaluate_liability_assessment(submission, answer_key)
    damages_results, sarah_jones_adequately_reserved = evaluate_damages(submission, answer_key)
    settlement_results = evaluate_settlement_strategy(submission, answer_key)
    classification_results = evaluate_claim_classification(submission, answer_key)
    
    # Combine all sections
    sections = [
        coverage_results,
        liability_results,
        damages_results,
        settlement_results,
        classification_results
    ]
    
    # Check critical elements
    passed_critical, critical_failures = check_critical_elements(sections, sarah_jones_adequately_reserved)
    
    # Calculate overall score
    total_score = sum(section["section_score"] for section in sections)
    total_possible = sum(section["weight"] for section in sections)
    overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
    
    # Determine final result
    passed = overall_percentage >= 80 and passed_critical
    
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": overall_percentage,
        "passed": passed,
        "sections": sections,
        "critical_failures": critical_failures if not passed_critical else []
    }
    
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
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']:.2f}%")
    if results["passed"]:
        print("PASSED")
    else:
        print("FAILED")
        if results["critical_failures"]:
            print("Critical failures:")
            for failure in results["critical_failures"]:
                print(f"- {failure}")

if __name__ == "__main__":
    main()