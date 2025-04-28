#!/usr/bin/env python3
import json
import sys
import os
from typing import Dict, Any, List, Tuple

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_data_exploration(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the data exploration section (20 points)."""
    score = 0
    feedback = {}
    
    # Summary statistics (5 points)
    stats_score = 0
    stats_feedback = []
    
    try:
        sub_stats_a = submission["data_exploration"]["summary_statistics"]["campaign_a"]
        key_stats_a = answer_key["data_exploration"]["summary_statistics"]["campaign_a"]
        sub_stats_b = submission["data_exploration"]["summary_statistics"]["campaign_b"]
        key_stats_b = answer_key["data_exploration"]["summary_statistics"]["campaign_b"]
        
        # Check if all required statistics are present
        required_stats = ["mean", "median", "std_dev", "min", "max"]
        if all(stat in sub_stats_a and stat in sub_stats_b for stat in required_stats):
            # Check accuracy of statistics (within 5% tolerance)
            correct_stats = 0
            total_stats = len(required_stats) * 2  # For both campaigns
            
            for stat in required_stats:
                if abs(sub_stats_a[stat] - key_stats_a[stat]) <= 0.05 * abs(key_stats_a[stat]):
                    correct_stats += 1
                else:
                    stats_feedback.append(f"Campaign A {stat} is outside acceptable range")
                
                if abs(sub_stats_b[stat] - key_stats_b[stat]) <= 0.05 * abs(key_stats_b[stat]):
                    correct_stats += 1
                else:
                    stats_feedback.append(f"Campaign B {stat} is outside acceptable range")
            
            stats_score = 5 * (correct_stats / total_stats)
        else:
            stats_feedback.append("Missing required statistics")
            stats_score = 0
    except KeyError:
        stats_feedback.append("Missing or incorrectly structured summary statistics")
    
    score += stats_score
    feedback["summary_statistics"] = {
        "score": stats_score,
        "max_score": 5,
        "feedback": stats_feedback if stats_feedback else "Correct"
    }
    
    # Outliers (5 points)
    outliers_score = 0
    outliers_feedback = []
    
    try:
        sub_outliers = submission["data_exploration"]["outliers"]
        key_outliers = answer_key["data_exploration"]["outliers"]
        
        # Check if outliers were identified correctly
        if sub_outliers["identified"] == key_outliers["identified"]:
            outliers_score += 2.5
        else:
            outliers_feedback.append("Incorrect identification of outliers")
        
        # Check description of outliers
        if key_outliers["identified"]:
            # If there are outliers, check if the description mentions the key values
            if "650.30" in sub_outliers["description"] and "580.70" in sub_outliers["description"]:
                outliers_score += 2.5
            else:
                outliers_feedback.append("Description does not mention specific outlier values")
    except KeyError:
        outliers_feedback.append("Missing or incorrectly structured outliers information")
    
    score += outliers_score
    feedback["outliers"] = {
        "score": outliers_score,
        "max_score": 5,
        "feedback": outliers_feedback if outliers_feedback else "Correct"
    }
    
    # Visualization insights (10 points)
    viz_score = 0
    viz_feedback = []
    
    try:
        sub_viz = submission["data_exploration"]["visualization_insights"]
        
        # Check for key insights
        key_points = [
            "variability" in sub_viz.lower() or "standard deviation" in sub_viz.lower(),
            "distribution" in sub_viz.lower(),
            "campaign b" in sub_viz.lower() and "higher" in sub_viz.lower(),
            "income" in sub_viz.lower()
        ]
        
        viz_score = 10 * (sum(key_points) / len(key_points))
        
        if viz_score < 10:
            viz_feedback.append("Missing some key insights about distributions")
    except KeyError:
        viz_feedback.append("Missing visualization insights")
    
    score += viz_score
    feedback["visualization_insights"] = {
        "score": viz_score,
        "max_score": 10,
        "feedback": viz_feedback if viz_feedback else "Good insights provided"
    }
    
    return score, feedback

def evaluate_hypothesis_testing(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the hypothesis testing section (30 points)."""
    score = 0
    feedback = {}
    
    # Campaign difference (15 points)
    campaign_score = 0
    campaign_feedback = []
    
    try:
        sub_campaign = submission["hypothesis_testing"]["campaign_difference"]
        key_campaign = answer_key["hypothesis_testing"]["campaign_difference"]
        
        # Check test selection (5 points)
        valid_tests = ["t-test", "t test", "independent samples t-test", "independent t-test", "welch", "student"]
        if any(test.lower() in sub_campaign["test_used"].lower() for test in valid_tests):
            campaign_score += 5
        else:
            campaign_feedback.append("Inappropriate statistical test selected")
        
        # Check p-value and significance (5 points)
        if abs(sub_campaign["p_value"] - key_campaign["p_value"]) <= 0.01:
            campaign_score += 2.5
        else:
            campaign_feedback.append("P-value is incorrect")
            
        if sub_campaign["significant_difference"] == key_campaign["significant_difference"]:
            campaign_score += 2.5
        else:
            campaign_feedback.append("Incorrect conclusion about significance")
        
        # Check interpretation (5 points)
        key_interpretation_points = [
            "campaign b" in sub_campaign["interpretation"].lower() and "higher" in sub_campaign["interpretation"].lower(),
            "significant" in sub_campaign["interpretation"].lower(),
            "difference" in sub_campaign["interpretation"].lower()
        ]
        
        interp_score = 5 * (sum(key_interpretation_points) / len(key_interpretation_points))
        campaign_score += interp_score
        
        if interp_score < 5:
            campaign_feedback.append("Interpretation missing key points")
    except KeyError:
        campaign_feedback.append("Missing or incorrectly structured campaign difference information")
    
    score += campaign_score
    feedback["campaign_difference"] = {
        "score": campaign_score,
        "max_score": 15,
        "feedback": campaign_feedback if campaign_feedback else "Correct"
    }
    
    # Regional differences (15 points)
    regional_score = 0
    regional_feedback = []
    
    try:
        sub_regional = submission["hypothesis_testing"]["regional_differences"]
        key_regional = answer_key["hypothesis_testing"]["regional_differences"]
        
        # Check test selection (5 points)
        valid_tests = ["anova", "two-way anova", "two way anova", "factorial anova"]
        if any(test.lower() in sub_regional["test_used"].lower() for test in valid_tests):
            regional_score += 5
        else:
            regional_feedback.append("Inappropriate statistical test selected for regional analysis")
        
        # Check significance (5 points)
        if sub_regional["significant_difference"] == key_regional["significant_difference"]:
            regional_score += 5
        else:
            regional_feedback.append("Incorrect conclusion about regional significance")
        
        # Check interpretation (5 points)
        key_interpretation_points = [
            "south" in sub_regional["interpretation"].lower(),
            "west" in sub_regional["interpretation"].lower(),
            "regional" in sub_regional["interpretation"].lower() and "differ" in sub_regional["interpretation"].lower()
        ]
        
        interp_score = 5 * (sum(key_interpretation_points) / len(key_interpretation_points))
        regional_score += interp_score
        
        if interp_score < 5:
            regional_feedback.append("Regional interpretation missing key points")
    except KeyError:
        regional_feedback.append("Missing or incorrectly structured regional differences information")
    
    score += regional_score
    feedback["regional_differences"] = {
        "score": regional_score,
        "max_score": 15,
        "feedback": regional_feedback if regional_feedback else "Correct"
    }
    
    return score, feedback

def evaluate_relationship_analysis(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the relationship analysis section (30 points)."""
    score = 0
    feedback = {}
    
    # Demographics impact (10 points)
    demographics_score = 0
    demographics_feedback = []
    
    try:
        sub_demographics = submission["relationship_analysis"]["demographics_impact"]
        
        # Age group relationship (5 points)
        age_key_points = [
            "u" in sub_demographics["age_group"]["relationship_type"].lower() or 
            "middle" in sub_demographics["age_group"]["relationship_type"].lower(),
            "35" in sub_demographics["age_group"]["relationship_type"] or 
            "45" in sub_demographics["age_group"]["relationship_type"],
            sub_demographics["age_group"]["significance"] == True
        ]
        
        age_score = 5 * (sum(age_key_points) / len(age_key_points))
        demographics_score += age_score
        
        if age_score < 5:
            demographics_feedback.append("Age group relationship description incomplete")
        
        # Income level relationship (5 points)
        income_key_points = [
            "positive" in sub_demographics["income_level"]["relationship_type"].lower() or 
            "higher" in sub_demographics["income_level"]["relationship_type"].lower(),
            "strong" in sub_demographics["income_level"]["relationship_type"].lower(),
            sub_demographics["income_level"]["significance"] == True
        ]
        
        income_score = 5 * (sum(income_key_points) / len(income_key_points))
        demographics_score += income_score
        
        if income_score < 5:
            demographics_feedback.append("Income level relationship description incomplete")
    except KeyError:
        demographics_feedback.append("Missing or incorrectly structured demographics information")
    
    score += demographics_score
    feedback["demographics_impact"] = {
        "score": demographics_score,
        "max_score": 10,
        "feedback": demographics_feedback if demographics_feedback else "Correct"
    }
    
    # Satisfaction correlation (10 points)
    satisfaction_score = 0
    satisfaction_feedback = []
    
    try:
        sub_satisfaction = submission["relationship_analysis"]["satisfaction_correlation"]
        key_satisfaction = answer_key["relationship_analysis"]["satisfaction_correlation"]
        
        # Check correlation coefficient (3 points)
        if abs(sub_satisfaction["correlation_coefficient"] - key_satisfaction["correlation_coefficient"]) <= 0.1:
            satisfaction_score += 3
        else:
            satisfaction_feedback.append("Correlation coefficient is outside acceptable range")
        
        # Check p-value (2 points)
        if sub_satisfaction["p_value"] <= 0.05:  # Just checking if it's significant
            satisfaction_score += 2
        else:
            satisfaction_feedback.append("P-value indicates incorrect significance level")
        
        # Check interpretation (5 points)
        key_interpretation_points = [
            "positive" in sub_satisfaction["interpretation"].lower(),
            "strong" in sub_satisfaction["interpretation"].lower(),
            "higher" in sub_satisfaction["interpretation"].lower() and 
            "satisfaction" in sub_satisfaction["interpretation"].lower()
        ]
        
        interp_score = 5 * (sum(key_interpretation_points) / len(key_interpretation_points))
        satisfaction_score += interp_score
        
        if interp_score < 5:
            satisfaction_feedback.append("Satisfaction correlation interpretation incomplete")
    except KeyError:
        satisfaction_feedback.append("Missing or incorrectly structured satisfaction correlation information")
    
    score += satisfaction_score
    feedback["satisfaction_correlation"] = {
        "score": satisfaction_score,
        "max_score": 10,
        "feedback": satisfaction_feedback if satisfaction_feedback else "Correct"
    }
    
    # Strongest predictors (10 points)
    predictors_score = 0
    predictors_feedback = []
    
    try:
        sub_predictors = submission["relationship_analysis"]["strongest_predictors"]
        key_predictors = answer_key["relationship_analysis"]["strongest_predictors"]
        
        # Check if the top predictor is correct (4 points)
        if sub_predictors[0].lower() == key_predictors[0].lower():
            predictors_score += 4
        else:
            predictors_feedback.append("Top predictor is incorrect")
        
        # Check if the second predictor is correct (3 points)
        if len(sub_predictors) > 1 and sub_predictors[1].lower() == key_predictors[1].lower():
            predictors_score += 3
        else:
            predictors_feedback.append("Second predictor is incorrect")
        
        # Check if the remaining predictors are in the correct order (3 points)
        remaining_correct = 0
        for i in range(2, min(len(sub_predictors), len(key_predictors))):
            if sub_predictors[i].lower() == key_predictors[i].lower():
                remaining_correct += 1
        
        predictors_score += 3 * (remaining_correct / max(1, len(key_predictors) - 2))
        
        if remaining_correct < len(key_predictors) - 2:
            predictors_feedback.append("Some predictors are in incorrect order")
    except (KeyError, IndexError):
        predictors_feedback.append("Missing or incorrectly structured strongest predictors information")
    
    score += predictors_score
    feedback["strongest_predictors"] = {
        "score": predictors_score,
        "max_score": 10,
        "feedback": predictors_feedback if predictors_feedback else "Correct"
    }
    
    return score, feedback

def evaluate_conclusions(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Evaluate the conclusions section (20 points)."""
    score = 0
    feedback = {}
    
    # Most effective campaign (5 points)
    campaign_score = 0
    campaign_feedback = []
    
    try:
        sub_campaign = submission["conclusions"]["most_effective_campaign"]
        
        # Check if Campaign B is identified as most effective
        if "campaign b" in sub_campaign.lower() and "effective" in sub_campaign.lower():
            campaign_score += 3
        else:
            campaign_feedback.append("Did not correctly identify Campaign B as most effective")
        
        # Check for justification
        justification_points = [
            "higher" in sub_campaign.lower() and "sales" in sub_campaign.lower(),
            "income" in sub_campaign.lower() or "demographic" in sub_campaign.lower()
        ]
        
        justification_score = 2 * (sum(justification_points) / len(justification_points))
        campaign_score += justification_score
        
        if justification_score < 2:
            campaign_feedback.append("Justification for most effective campaign is incomplete")
    except KeyError:
        campaign_feedback.append("Missing most effective campaign conclusion")
    
    score += campaign_score
    feedback["most_effective_campaign"] = {
        "score": campaign_score,
        "max_score": 5,
        "feedback": campaign_feedback if campaign_feedback else "Correct"
    }
    
    # Regional insights (5 points)
    regional_score = 0
    regional_feedback = []
    
    try:
        sub_regional = submission["conclusions"]["regional_insights"]
        
        key_points = [
            "south" in sub_regional.lower(),
            "west" in sub_regional.lower(),
            "regional" in sub_regional.lower() and "differ" in sub_regional.lower(),
            "campaign b" in sub_regional.lower() and "perform" in sub_regional.lower()
        ]
        
        regional_score = 5 * (sum(key_points) / len(key_points))
        
        if regional_score < 5:
            regional_feedback.append("Regional insights are incomplete")
    except KeyError:
        regional_feedback.append("Missing regional insights")
    
    score += regional_score
    feedback["regional_insights"] = {
        "score": regional_score,
        "max_score": 5,
        "feedback": regional_feedback if regional_feedback else "Good insights"
    }
    
    # Demographic insights (5 points)
    demographic_score = 0
    demographic_feedback = []
    
    try:
        sub_demographic = submission["conclusions"]["demographic_insights"]
        
        key_points = [
            "income" in sub_demographic.lower() and "strong" in sub_demographic.lower(),
            "high" in sub_demographic.lower() and "income" in sub_demographic.lower(),
            "age" in sub_demographic.lower() or "middle" in sub_demographic.lower(),
            "35" in sub_demographic or "45" in sub_demographic
        ]
        
        demographic_score = 5 * (sum(key_points) / len(key_points))
        
        if demographic_score < 5:
            demographic_feedback.append("Demographic insights are incomplete")
    except KeyError:
        demographic_feedback.append("Missing demographic insights")
    
    score += demographic_score
    feedback["demographic_insights"] = {
        "score": demographic_score,
        "max_score": 5,
        "feedback": demographic_feedback if demographic_feedback else "Good insights"
    }
    
    # Recommendations (5 points)
    recommendations_score = 0
    recommendations_feedback = []
    
    try:
        sub_recommendations = submission["conclusions"]["recommendations"]
        
        # Check number of recommendations
        if len(sub_recommendations) >= 3:
            recommendations_score += 1
        else:
            recommendations_feedback.append("Fewer than 3 recommendations provided")
        
        # Check quality of recommendations
        key_recommendation_themes = [
            any("campaign b" in rec.lower() and ("target" in rec.lower() or "focus" in rec.lower()) for rec in sub_recommendations),
            any("high" in rec.lower() and "income" in rec.lower() for rec in sub_recommendations),
            any("region" in rec.lower() or "south" in rec.lower() or "west" in rec.lower() for rec in sub_recommendations),
            any("age" in rec.lower() or "middle" in rec.lower() or "35" in rec or "45" in rec for rec in sub_recommendations),
            any("satisfaction" in rec.lower() for rec in sub_recommendations)
        ]
        
        theme_score = 4 * (sum(key_recommendation_themes) / len(key_recommendation_themes))
        recommendations_score += theme_score
        
        if theme_score < 4:
            recommendations_feedback.append("Recommendations missing key themes from the analysis")
    except KeyError:
        recommendations_feedback.append("Missing recommendations")
    
    score += recommendations_score
    feedback["recommendations"] = {
        "score": recommendations_score,
        "max_score": 5,
        "feedback": recommendations_feedback if recommendations_feedback else "Good recommendations"
    }
    
    return score, feedback

def check_critical_errors(submission: Dict[str, Any], answer_key: Dict[str, Any]) -> List[str]:
    """Check for critical errors that would result in automatic failure."""
    critical_errors = []
    
    # 1. Using inappropriate statistical tests
    try:
        campaign_test = submission["hypothesis_testing"]["campaign_difference"]["test_used"].lower()
        regional_test = submission["hypothesis_testing"]["regional_differences"]["test_used"].lower()
        
        valid_campaign_tests = ["t-test", "t test", "independent", "welch", "student", "mann-whitney", "wilcoxon"]
        valid_regional_tests = ["anova", "kruskal", "factorial"]
        
        if not any(test in campaign_test for test in valid_campaign_tests):
            critical_errors.append("Critical Error: Inappropriate statistical test for campaign comparison")
        
        if not any(test in regional_test for test in valid_regional_tests):
            critical_errors.append("Critical Error: Inappropriate statistical test for regional analysis")
    except KeyError:
        critical_errors.append("Critical Error: Missing required statistical tests")
    
    # 2. Making conclusions that directly contradict the statistical evidence
    try:
        campaign_significant = submission["hypothesis_testing"]["campaign_difference"]["significant_difference"]
        most_effective = submission["conclusions"]["most_effective_campaign"].lower()
        
        if campaign_significant and "campaign a" in most_effective and "effective" in most_effective:
            critical_errors.append("Critical Error: Conclusion contradicts statistical evidence about most effective campaign")
    except KeyError:
        pass
    
    # 3. Failing to identify the significant difference between campaigns
    try:
        if not submission["hypothesis_testing"]["campaign_difference"]["significant_difference"]:
            if answer_key["hypothesis_testing"]["campaign_difference"]["significant_difference"]:
                critical_errors.append("Critical Error: Failed to identify significant difference between campaigns")
    except KeyError:
        critical_errors.append("Critical Error: Missing conclusion about campaign significance")
    
    return critical_errors

def evaluate_submission(submission_path: str, answer_key_path: str) -> Dict[str, Any]:
    """Evaluate a candidate's submission against the answer key."""
    submission = load_json(submission_path)
    answer_key = load_json(answer_key_path)
    
    # Check for critical errors first
    critical_errors = check_critical_errors(submission, answer_key)
    
    # Evaluate each section
    data_exploration_score, data_exploration_feedback = evaluate_data_exploration(submission, answer_key)
    hypothesis_testing_score, hypothesis_testing_feedback = evaluate_hypothesis_testing(submission, answer_key)
    relationship_analysis_score, relationship_analysis_feedback = evaluate_relationship_analysis(submission, answer_key)
    conclusions_score, conclusions_feedback = evaluate_conclusions(submission, answer_key)
    
    # Calculate total score
    max_score = 100
    total_score = data_exploration_score + hypothesis_testing_score + relationship_analysis_score + conclusions_score
    
    # Apply automatic failure for critical errors
    if critical_errors:
        overall_score = 0
    else:
        overall_score = (total_score / max_score) * 100
    
    # Prepare results
    results = {
        "overall_score": round(overall_score, 2),
        "passing_threshold": 70,
        "passed": overall_score >= 70,
        "critical_errors": critical_errors,
        "section_scores": {
            "data_exploration": {
                "score": round(data_exploration_score, 2),
                "max_score": 20,
                "percentage": round((data_exploration_score / 20) * 100, 2),
                "feedback": data_exploration_feedback
            },
            "hypothesis_testing": {
                "score": round(hypothesis_testing_score, 2),
                "max_score": 30,
                "percentage": round((hypothesis_testing_score / 30) * 100, 2),
                "feedback": hypothesis_testing_feedback
            },
            "relationship_analysis": {
                "score": round(relationship_analysis_score, 2),
                "max_score": 30,
                "percentage": round((relationship_analysis_score / 30) * 100, 2),
                "feedback": relationship_analysis_feedback
            },
            "conclusions": {
                "score": round(conclusions_score, 2),
                "max_score": 20,
                "percentage": round((conclusions_score / 20) * 100, 2),
                "feedback": conclusions_feedback
            }
        }
    }
    
    return results

def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    results = evaluate_submission(submission_path, answer_key_path)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print(f"Results saved to test_results.json")

if __name__ == "__main__":
    main()