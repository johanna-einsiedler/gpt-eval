import json
import re
import os

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def evaluate_product_identification(submission, answer_key, results):
    """Evaluate the product identification section (10 points)."""
    section_score = 0
    section_feedback = {}
    
    # Name (3 points)
    if submission.get("name"):
        name_score = 0
        name = submission["name"].lower()
        if "ergonomic" in name and ("chair" in name or "seating" in name):
            name_score += 1
        if any(term in name for term in ["adjustable", "mesh", "office"]):
            name_score += 1
        if len(name.split()) >= 3:  # Check if name is descriptive enough
            name_score += 1
        section_score += name_score
        section_feedback["name"] = {
            "score": name_score,
            "max_points": 3,
            "feedback": "Name should be specific, descriptive, and mention key features"
        }
    
    # Category (3 points)
    if submission.get("category"):
        category_score = 0
        category = submission["category"].lower()
        if "office" in category:
            category_score += 1
        if "furniture" in category or "seating" in category:
            category_score += 1
        if "chair" in category or "seating" in category:
            category_score += 1
        section_score += category_score
        section_feedback["category"] = {
            "score": category_score,
            "max_points": 3,
            "feedback": "Category should follow standard classification"
        }
    
    # Intended use (4 points)
    if submission.get("intended_use"):
        use_score = 0
        use = submission["intended_use"].lower()
        if "office" in use or "workplace" in use or "work" in use:
            use_score += 1
        if any(term in use for term in ["ergonomic", "comfort", "support"]):
            use_score += 1
        if any(term in use for term in ["hour", "daily", "duration", "period"]):
            use_score += 1
        if len(use.split()) >= 10:  # Check if use description is detailed enough
            use_score += 1
        section_score += use_score
        section_feedback["intended_use"] = {
            "score": use_score,
            "max_points": 4,
            "feedback": "Intended use should clearly describe environment and purpose"
        }
    
    results["task1_scores"]["product_identification"] = {
        "score": section_score,
        "max_points": 10,
        "details": section_feedback
    }
    return section_score

def evaluate_technical_requirements(submission, answer_key, results):
    """Evaluate the technical requirements section (15 points)."""
    section_score = 0
    section_feedback = {}
    
    # Dimensions (5 points)
    if submission.get("dimensions"):
        dim_score = 0
        dimensions = submission["dimensions"].lower()
        
        # Check for imperial units
        if any(unit in dimensions for unit in ["inch", "inches", "\""]):
            dim_score += 1
        
        # Check for metric units
        if any(unit in dimensions for unit in ["cm", "mm", "centimeter"]):
            dim_score += 1
        
        # Check for key measurements
        key_dimensions = ["height", "width", "depth"]
        for dim in key_dimensions:
            if dim in dimensions:
                dim_score += 1
                if dim_score >= 5:  # Cap at 5 points
                    break
        
        section_score += min(dim_score, 5)
        section_feedback["dimensions"] = {
            "score": min(dim_score, 5),
            "max_points": 5,
            "feedback": "Must include all key measurements with proper units"
        }
    
    # Weight Capacity (3 points)
    if submission.get("weight_capacity"):
        weight_score = 0
        weight = submission["weight_capacity"].lower()
        
        # Check for numerical value
        if re.search(r'\d+', weight):
            weight_score += 1
        
        # Check for units
        if "lb" in weight or "pound" in weight:
            weight_score += 1
        if "kg" in weight or "kilogram" in weight:
            weight_score += 1
        
        # Check if meets minimum standards (250 lbs)
        weight_values = re.findall(r'\d+', weight)
        if weight_values:
            if "kg" in weight and int(weight_values[0]) >= 113:  # ~250 lbs in kg
                weight_score += 1
            elif int(weight_values[0]) >= 250:  # Assuming lbs if no kg
                weight_score += 1
        
        section_score += min(weight_score, 3)
        section_feedback["weight_capacity"] = {
            "score": min(weight_score, 3),
            "max_points": 3,
            "feedback": "Must meet minimum standards"
        }
    
    # Materials (7 points)
    if submission.get("materials") and isinstance(submission["materials"], list):
        materials = submission["materials"]
        materials_score = min(len(materials), 7)  # 1 point per material, max 7
        
        # Check for specificity in materials
        specific_count = 0
        for material in materials:
            material_lower = material.lower()
            # Check if material description is specific (mentions type and grade/standard)
            if len(material_lower.split()) >= 4 and any(term in material_lower for term in ["grade", "type", "quality", "standard", "strength", "density"]):
                specific_count += 1
        
        # Adjust score based on specificity
        materials_score = min(materials_score, specific_count + 3)  # Allow some leeway
        
        section_score += materials_score
        section_feedback["materials"] = {
            "score": materials_score,
            "max_points": 7,
            "feedback": "Must specify at least 5 materials with proper grades/standards"
        }
    
    results["task1_scores"]["technical_requirements"] = {
        "score": section_score,
        "max_points": 15,
        "details": section_feedback
    }
    return section_score

def evaluate_performance_requirements(submission, answer_key, results):
    """Evaluate the performance requirements section (10 points)."""
    section_score = 0
    section_feedback = {}
    
    # Adjustability Features (6 points)
    if submission.get("adjustability_features") and isinstance(submission["adjustability_features"], list):
        features = submission["adjustability_features"]
        features_score = 0
        
        # Count features with specific ranges
        specific_features = 0
        for feature in features:
            feature_lower = feature.lower()
            # Check if feature includes specific measurements or ranges
            if re.search(r'\d+', feature_lower) and any(term in feature_lower for term in ["adjust", "height", "depth", "angle", "tilt", "recline"]):
                specific_features += 1
        
        features_score = min(specific_features, 6)
        section_score += features_score
        section_feedback["adjustability_features"] = {
            "score": features_score,
            "max_points": 6,
            "feedback": "Must include at least 5 features with specific ranges"
        }
    
    # Ergonomic Standards (4 points)
    if submission.get("ergonomic_standards") and isinstance(submission["ergonomic_standards"], list):
        standards = submission["ergonomic_standards"]
        standards_score = 0
        
        # Check for specific standards
        specific_standards = 0
        for standard in standards:
            standard_lower = standard.lower()
            # Check if standard references specific certification or standard
            if any(term in standard_lower for term in ["ansi", "bifma", "iso", "en", "din", "osha"]) and re.search(r'[A-Z0-9]+-\d+', standard):
                specific_standards += 1
        
        standards_score = min(specific_standards, 4)
        section_score += standards_score
        section_feedback["ergonomic_standards"] = {
            "score": standards_score,
            "max_points": 4,
            "feedback": "Must reference at least 3 specific standards"
        }
    
    results["task1_scores"]["performance_requirements"] = {
        "score": section_score,
        "max_points": 10,
        "details": section_feedback
    }
    return section_score

def evaluate_quality_standards(submission, answer_key, results):
    """Evaluate the quality standards section (10 points)."""
    section_score = 0
    section_feedback = {}
    
    # Certifications (5 points)
    if submission.get("certifications") and isinstance(submission["certifications"], list):
        certifications = submission["certifications"]
        cert_score = 0
        
        # Check for specific certifications
        specific_certs = 0
        for cert in certifications:
            cert_lower = cert.lower()
            # Check if certification includes specific standard and version
            if any(term in cert_lower for term in ["ansi", "bifma", "iso", "greenguard", "ul", "astm"]) and re.search(r'[A-Z0-9]+-\d+', cert):
                specific_certs += 1
        
        cert_score = min(specific_certs, 5)
        section_score += cert_score
        section_feedback["certifications"] = {
            "score": cert_score,
            "max_points": 5,
            "feedback": "Must include at least 3 specific certifications"
        }
    
    # Testing Requirements (5 points)
    if submission.get("testing_requirements") and isinstance(submission["testing_requirements"], list):
        tests = submission["testing_requirements"]
        test_score = 0
        
        # Check for specific tests
        specific_tests = 0
        for test in tests:
            test_lower = test.lower()
            # Check if test includes specific criteria or measurements
            if re.search(r'\d+', test_lower) and any(term in test_lower for term in ["test", "durability", "cycle", "verification", "standard"]):
                specific_tests += 1
        
        test_score = min(specific_tests, 5)
        section_score += test_score
        section_feedback["testing_requirements"] = {
            "score": test_score,
            "max_points": 5,
            "feedback": "Must include at least 3 specific tests"
        }
    
    results["task1_scores"]["quality_standards"] = {
        "score": section_score,
        "max_points": 10,
        "details": section_feedback
    }
    return section_score

def evaluate_compliance_requirements(submission, answer_key, results):
    """Evaluate the compliance requirements section (5 points)."""
    section_score = 0
    section_feedback = {}
    
    # Safety Standards (3 points)
    if submission.get("safety_standards") and isinstance(submission["safety_standards"], list):
        standards = submission["safety_standards"]
        safety_score = 0
        
        # Check for specific safety standards
        specific_standards = 0
        for standard in standards:
            standard_lower = standard.lower()
            # Check if standard references specific regulation
            if any(term in standard_lower for term in ["ansi", "bifma", "iso", "ul", "en", "astm", "cpsc", "osha"]):
                specific_standards += 1
        
        safety_score = min(specific_standards, 3)
        section_score += safety_score
        section_feedback["safety_standards"] = {
            "score": safety_score,
            "max_points": 3,
            "feedback": "Must include at least 2 specific standards"
        }
    
    # Environmental Considerations (2 points)
    if submission.get("environmental_considerations") and isinstance(submission["environmental_considerations"], list):
        considerations = submission["environmental_considerations"]
        env_score = 0
        
        # Check for specific environmental considerations
        specific_considerations = 0
        for consideration in considerations:
            consideration_lower = consideration.lower()
            # Check if consideration includes specific criteria
            if any(term in consideration_lower for term in ["recycl", "voc", "emission", "sustainable", "rohs", "reach"]):
                specific_considerations += 1
        
        env_score = min(specific_considerations, 2)
        section_score += env_score
        section_feedback["environmental_considerations"] = {
            "score": env_score,
            "max_points": 2,
            "feedback": "Must include at least 2 specific requirements"
        }
    
    results["task1_scores"]["compliance_requirements"] = {
        "score": section_score,
        "max_points": 5,
        "details": section_feedback
    }
    return section_score

def evaluate_task1(submission, answer_key, results):
    """Evaluate Task 1: Chair Specification (50 points total)."""
    task1_score = 0
    
    # Initialize task1_scores in results
    results["task1_scores"] = {}
    
    # Evaluate each section
    if "product_identification" in submission:
        task1_score += evaluate_product_identification(submission["product_identification"], 
                                                     answer_key["task1"]["product_identification"], 
                                                     results)
    
    if "technical_requirements" in submission:
        task1_score += evaluate_technical_requirements(submission["technical_requirements"], 
                                                     answer_key["task1"]["technical_requirements"], 
                                                     results)
    
    if "performance_requirements" in submission:
        task1_score += evaluate_performance_requirements(submission["performance_requirements"], 
                                                       answer_key["task1"]["performance_requirements"], 
                                                       results)
    
    if "quality_standards" in submission:
        task1_score += evaluate_quality_standards(submission["quality_standards"], 
                                                answer_key["task1"]["quality_standards"], 
                                                results)
    
    if "compliance_requirements" in submission:
        task1_score += evaluate_compliance_requirements(submission["compliance_requirements"], 
                                                      answer_key["task1"]["compliance_requirements"], 
                                                      results)
    
    results["task1_total"] = {
        "score": task1_score,
        "max_points": 50,
        "percentage": (task1_score / 50) * 100
    }
    
    return task1_score

def evaluate_identified_issue(issue, results_issues):
    """Evaluate a single identified issue (10 points per issue)."""
    issue_score = 0
    issue_feedback = {}
    
    # Issue Description (2 points)
    if issue.get("issue_description"):
        desc_score = 0
        description = issue["issue_description"].lower()
        
        # Check if description clearly identifies a problem
        if len(description.split()) >= 5:  # Minimum length
            desc_score += 1
        
        # Check if description mentions technical aspects
        if any(term in description for term in ["vague", "subjective", "missing", "unclear", "ambiguous", "imprecise"]):
            desc_score += 1
        
        issue_score += desc_score
        issue_feedback["issue_description"] = {
            "score": desc_score,
            "max_points": 2,
            "feedback": "Clearly identifies the problem"
        }
    
    # Location (1 point)
    if issue.get("location_in_document"):
        loc_score = 0
        location = issue["location_in_document"].lower()
        
        # Check if location is specific
        if "section" in location and re.search(r'\d+', location):
            loc_score += 1
        
        issue_score += loc_score
        issue_feedback["location_in_document"] = {
            "score": loc_score,
            "max_points": 1,
            "feedback": "Correctly identifies where the issue appears"
        }
    
    # Correction (7 points)
    if issue.get("correction"):
        corr_score = 0
        correction = issue["correction"].lower()
        
        # Check if correction is specific and technical
        if len(correction.split()) >= 8:  # Minimum length
            corr_score += 1
        
        # Check for numerical values
        if re.search(r'\d+', correction):
            corr_score += 2
        
        # Check for units or standards
        if any(unit in correction for unit in ["inch", "cm", "mm", "hz", "ms", "nit", "cd/m", "pixel", "bit", "port"]):
            corr_score += 2
        
        # Check for technical terminology
        if any(term in correction for term in ["resolution", "refresh rate", "response time", "brightness", "contrast", "color gamut", "viewing angle", "connectivity"]):
            corr_score += 2
        
        issue_score += min(corr_score, 7)
        issue_feedback["correction"] = {
            "score": min(corr_score, 7),
            "max_points": 7,
            "feedback": "Provides technically accurate, specific correction"
        }
    
    return {
        "score": issue_score,
        "max_points": 10,
        "details": issue_feedback
    }

def evaluate_task2(submission, answer_key, results):
    """Evaluate Task 2: Monitor Specification Review (50 points total)."""
    task2_score = 0
    
    # Initialize task2_scores in results
    results["task2_scores"] = {
        "identified_issues": []
    }
    
    # Evaluate each identified issue
    if "identified_issues" in submission and isinstance(submission["identified_issues"], list):
        issues = submission["identified_issues"]
        
        for i, issue in enumerate(issues[:5]):  # Evaluate up to 5 issues
            issue_result = evaluate_identified_issue(issue, results["task2_scores"]["identified_issues"])
            results["task2_scores"]["identified_issues"].append(issue_result)
            task2_score += issue_result["score"]
    
    results["task2_total"] = {
        "score": task2_score,
        "max_points": 50,
        "percentage": (task2_score / 50) * 100
    }
    
    return task2_score

def evaluate_submission(submission_file, answer_key_file):
    """Evaluate the candidate's submission against the answer key."""
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    if not submission or not answer_key:
        return {"error": "Failed to load submission or answer key"}
    
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown")
    }
    
    # Evaluate Task 1
    task1_score = evaluate_task1(submission.get("task1", {}), answer_key, results)
    
    # Evaluate Task 2
    task2_score = evaluate_task2(submission.get("task2", {}), answer_key, results)
    
    # Calculate overall score
    total_score = task1_score + task2_score
    max_points = 100  # 50 points for each task
    overall_percentage = (total_score / max_points) * 100
    
    results["overall_score"] = overall_percentage
    results["overall_result"] = {
        "score": total_score,
        "max_points": max_points,
        "percentage": overall_percentage,
        "pass": overall_percentage >= 70  # Passing threshold is 70%
    }
    
    return results

def main():
    """Main function to run the evaluation."""
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results_file = "test_results.json"
    
    # Check if files exist
    if not os.path.exists(submission_file):
        print(f"Error: {submission_file} not found")
        return
    
    if not os.path.exists(answer_key_file):
        print(f"Error: {answer_key_file} not found")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission_file, answer_key_file)
    
    # Save results
    try:
        with open(results_file, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation completed. Results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()