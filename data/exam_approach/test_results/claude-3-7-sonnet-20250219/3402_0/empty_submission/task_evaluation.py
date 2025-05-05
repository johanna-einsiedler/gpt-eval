#!/usr/bin/env python3
import json
import sys
import re
from collections import defaultdict

def normalize_text(text):
    """Normalize text for comparison by removing whitespace, punctuation, and converting to lowercase."""
    if not isinstance(text, str):
        return str(text).lower()
    # Remove dollar signs, commas, extra spaces, and convert to lowercase
    return re.sub(r'[\s\$,]+', '', text.lower())

def calculate_similarity(candidate_item, key_item, field):
    """Calculate similarity between candidate and key item for a specific field."""
    if field not in candidate_item or field not in key_item:
        return 0
    
    candidate_value = normalize_text(candidate_item[field])
    key_value = normalize_text(key_item[field])
    
    # Simple exact match after normalization
    if candidate_value == key_value:
        return 1.0
    
    # For location and issue fields, check for partial matches
    if field in ['location', 'issue', 'description']:
        # If key text is found within candidate text
        if key_value in candidate_value or candidate_value in key_value:
            return 0.7
    
    return 0

def match_items(candidate_items, key_items, category):
    """Match candidate items to key items and calculate scores."""
    matches = []
    used_candidate_indices = set()
    used_key_indices = set()
    
    # Define fields to compare based on category
    if category == "calculation_errors":
        fields = ["location", "current_value", "correct_value"]
    elif category == "missing_information":
        fields = ["requirement_id", "description"]
    else:  # compliance_issues
        fields = ["regulation_id", "location", "issue"]
    
    # Calculate similarity scores between all pairs
    similarity_matrix = []
    for i, candidate_item in enumerate(candidate_items):
        row = []
        for j, key_item in enumerate(key_items):
            # Calculate average similarity across all fields
            field_similarities = [calculate_similarity(candidate_item, key_item, field) for field in fields]
            avg_similarity = sum(field_similarities) / len(fields) if field_similarities else 0
            row.append((avg_similarity, i, j))
        similarity_matrix.append(row)
    
    # Flatten and sort by similarity score (highest first)
    all_similarities = [item for row in similarity_matrix for item in row]
    all_similarities.sort(reverse=True)
    
    # Greedy matching
    for similarity, candidate_idx, key_idx in all_similarities:
        if similarity >= 0.5 and candidate_idx not in used_candidate_indices and key_idx not in used_key_indices:
            matches.append({
                "candidate_item": candidate_items[candidate_idx],
                "key_item": key_items[key_idx],
                "similarity": similarity
            })
            used_candidate_indices.add(candidate_idx)
            used_key_indices.add(key_idx)
    
    # Calculate points
    points_per_item = 5 if category == "calculation_errors" else 3
    earned_points = sum(match["similarity"] * points_per_item for match in matches)
    max_points = len(key_items) * points_per_item
    
    # Identify unmatched items
    unmatched_candidate = [item for i, item in enumerate(candidate_items) if i not in used_candidate_indices]
    unmatched_key = [item for i, item in enumerate(key_items) if i not in used_key_indices]
    
    return {
        "matches": matches,
        "unmatched_candidate": unmatched_candidate,
        "unmatched_key": unmatched_key,
        "earned_points": earned_points,
        "max_points": max_points
    }

def evaluate_submission(candidate_path, key_path):
    """Evaluate a candidate's submission against the answer key."""
    try:
        with open(candidate_path, 'r') as f:
            candidate_data = json.load(f)
        
        with open(key_path, 'r') as f:
            key_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {
            "error": f"Error loading JSON files: {str(e)}",
            "overall_score": 0
        }
    
    results = {
        "candidate_id": candidate_data.get("candidate_id", "Unknown"),
        "format_score": 5 if is_format_correct(candidate_data) else 0,
        "categories": {}
    }
    
    total_earned = 0
    total_possible = 5  # Start with format points
    
    # Evaluate each category
    for category in ["calculation_errors", "missing_information", "compliance_issues"]:
        candidate_items = candidate_data.get(category, [])
        key_items = key_data.get(category, [])
        
        category_results = match_items(candidate_items, key_items, category)
        results["categories"][category] = category_results
        
        total_earned += category_results["earned_points"]
        total_possible += category_results["max_points"]
    
    # Add format points to total earned
    total_earned += results["format_score"]
    
    # Calculate overall score as percentage
    results["overall_score"] = round((total_earned / total_possible) * 100, 1) if total_possible > 0 else 0
    results["total_earned_points"] = total_earned
    results["total_possible_points"] = total_possible
    
    # Determine if candidate passed
    results["passed"] = results["overall_score"] >= 60
    
    return results

def is_format_correct(candidate_data):
    """Check if the candidate submission follows the required JSON format."""
    required_keys = ["candidate_id", "calculation_errors", "missing_information", "compliance_issues"]
    
    # Check if all required top-level keys exist
    if not all(key in candidate_data for key in required_keys):
        return False
    
    # Check if arrays are present for each category
    for key in required_keys[1:]:
        if not isinstance(candidate_data[key], list):
            return False
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    candidate_path = sys.argv[1]
    key_path = sys.argv[2]
    
    results = evaluate_submission(candidate_path, key_path)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Pass/Fail: {'PASS' if results.get('passed', False) else 'FAIL'}")

if __name__ == "__main__":
    main()