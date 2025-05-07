import json
import sys
import re
import argparse

# --- Configuration for Scoring ---
TASK1_MAX_SCORE = 40.0
TASK1_TITLE_MAX = 2.0
TASK1_AUDIENCE_MAX = 2.0
TASK1_INTRO_MAX = 6.0
TASK1_QUESTIONS_MAX = 30.0

TASK2_MAX_SCORE = 60.0
TASK2_SATISFACTION_SUMMARY_MAX = 20.0
TASK2_TOP_ENJOYED_MAX = 15.0
TASK2_TOP_IMPROVEMENT_MAX = 15.0
TASK2_RECOMMENDATION_MAX = 10.0

TOTAL_EXAM_MAX_SCORE = TASK1_MAX_SCORE + TASK2_MAX_SCORE

# Keywords for Task 1 (case-insensitive)
TITLE_KEYWORDS = ["survey", "interest", "mindfulness", "stretching", "innovatech", "wellness", "feedback"]
AUDIENCE_KEYWORDS = ["employee", "innovatech", "staff", "personnel", "all"]
INTRO_PURPOSE_KEYWORDS = ["feedback", "purpose", "survey", "input", "opinion", "understand", "gauge", "assess", "mindfulness", "stretching", "wellness", "program", "initiative"]
INTRO_TONE_KEYWORDS = ["please", "thank you", "valuable", "appreciate", "confidential", "anonymous", "help", "invite", "encourage"]
QUESTION_RELEVANCE_KEYWORDS = ["mindfulness", "stretching", "break", "interest", "schedule", "barrier", "preference", "well-being", "time", "day", "frequency", "duration", "participate", "benefit", "concern", "content", "format"]
ALLOWED_QUESTION_TYPES = [
    "Multiple Choice - Single Answer",
    "Multiple Choice - Multiple Answers",
    "Likert Scale (1-5)",
    "Open-ended Text"
]

# Keywords for Task 2 Recommendation (case-insensitive)
RECOMMENDATION_ACTION_KEYWORDS = ["consider", "improve", "add", "change", "explore", "recommend", "suggest", "implement", "offer", "provide", "ensure", "review", "adjust"]


def get_nested_value(data_dict, path, default=None):
    """Safely access nested dictionary values."""
    current = data_dict
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current

def contains_keywords(text, keywords, N=1):
    """Check if text contains at least N keywords (case-insensitive)."""
    if not isinstance(text, str) or not text:
        return False
    text_lower = text.lower()
    found_count = 0
    for kw in keywords:
        if kw.lower() in text_lower:
            found_count += 1
            if found_count >= N:
                return True
    return False

def score_task1_survey_title(candidate_title):
    score = 0
    comment = "Title: "
    if candidate_title and isinstance(candidate_title, str) and len(candidate_title.strip()) > 0:
        if contains_keywords(candidate_title, TITLE_KEYWORDS):
            score = TASK1_TITLE_MAX
            comment += "Relevant and clear title."
        else:
            score = TASK1_TITLE_MAX / 2
            comment += "Title present but could be more relevant or descriptive."
    else:
        comment += "Missing or empty."
    return score, comment

def score_task1_target_audience(candidate_desc):
    score = 0
    comment = "Target Audience: "
    if candidate_desc and isinstance(candidate_desc, str) and len(candidate_desc.strip()) > 0:
        if contains_keywords(candidate_desc, AUDIENCE_KEYWORDS):
            score = TASK1_AUDIENCE_MAX
            comment += "Accurate description."
        else:
            score = TASK1_AUDIENCE_MAX / 2
            comment += "Description present but could be more specific or accurate."
    else:
        comment += "Missing or empty."
    return score, comment

def score_task1_survey_introduction(candidate_intro):
    score = 0
    comments = []
    # Clarity and purpose (3 points)
    purpose_score = 0
    if candidate_intro and isinstance(candidate_intro, str) and len(candidate_intro.strip()) > 15: # Min length
        if contains_keywords(candidate_intro, INTRO_PURPOSE_KEYWORDS, N=2):
            purpose_score = 3.0
            comments.append("Clear purpose.")
        elif contains_keywords(candidate_intro, INTRO_PURPOSE_KEYWORDS, N=1):
            purpose_score = 1.5
            comments.append("Purpose somewhat clear.")
        else:
            comments.append("Purpose not clearly stated.")
    else:
        comments.append("Introduction missing, too short, or not a string.")
    score += purpose_score

    # Tone and encouragement (3 points)
    tone_score = 0
    if candidate_intro and isinstance(candidate_intro, str): # Already checked for presence
        if contains_keywords(candidate_intro, INTRO_TONE_KEYWORDS, N=1):
            tone_score = 3.0
            comments.append("Good tone and encouragement.")
        elif purpose_score > 0 : # If intro is somewhat valid
            tone_score = 1.5
            comments.append("Tone could be more encouraging.")
        else:
            comments.append("Tone and encouragement lacking.")
    score += tone_score
    
    return score, "Introduction: " + " ".join(comments)

def score_task1_survey_questions(candidate_questions_list):
    total_score = 0
    question_details_report = []
    num_q_submitted = 0
    quantity_comment = ""

    if not isinstance(candidate_questions_list, list):
        quantity_comment = "Survey questions not provided as a list."
        return 0, quantity_comment, question_details_report, num_q_submitted

    num_q_submitted = len(candidate_questions_list)

    if num_q_submitted == 0:
        quantity_comment = "No survey questions provided."
        return 0, quantity_comment, question_details_report, num_q_submitted

    # Points per sub-criterion if 6 questions were submitted (ideal for 5 points per question)
    # These are the max points for each sub-criterion for *each* question
    base_relevance_max = 2.0
    base_type_options_max = 2.0
    base_clarity_max = 1.0

    raw_achieved_score = 0

    for i, q_data in enumerate(candidate_questions_list):
        q_text = get_nested_value(q_data, ("question_text",))
        q_type = get_nested_value(q_data, ("question_type",))
        q_options = get_nested_value(q_data, ("options",)) # Default is None, handle if not list

        current_q_relevance_score = 0
        current_q_type_options_score = 0
        current_q_clarity_score = 0
        
        q_report = {
            "question_index": i + 1,
            "text": q_text if q_text else "N/A",
            "relevance_score": 0, "relevance_max": base_relevance_max, "relevance_comment": "",
            "type_options_score": 0, "type_options_max": base_type_options_max, "type_options_comment": "",
            "clarity_score": 0, "clarity_max": base_clarity_max, "clarity_comment": ""
        }

        # Score Relevance
        if q_text and isinstance(q_text, str) and contains_keywords(q_text, QUESTION_RELEVANCE_KEYWORDS):
            current_q_relevance_score = base_relevance_max
            q_report["relevance_comment"] = "Relevant."
        elif q_text and isinstance(q_text, str):
            current_q_relevance_score = base_relevance_max / 2
            q_report["relevance_comment"] = "Partially relevant or relevance unclear."
        else:
            q_report["relevance_comment"] = "Question text missing or not relevant."
        q_report["relevance_score"] = current_q_relevance_score
        raw_achieved_score += current_q_relevance_score

        # Score Type & Options
        type_options_comments = []
        if q_type and isinstance(q_type, str) and q_type in ALLOWED_QUESTION_TYPES:
            valid_type = True
            if q_type == "Likert Scale (1-5)":
                if isinstance(q_options, list) and len(q_options) == 5:
                    current_q_type_options_score = base_type_options_max
                    type_options_comments.append("Correct Likert scale format.")
                else:
                    current_q_type_options_score = base_type_options_max / 2
                    type_options_comments.append("Likert scale type, but options incorrect (expected 5).")
            elif "Multiple Choice" in q_type:
                if isinstance(q_options, list) and len(q_options) > 0:
                    current_q_type_options_score = base_type_options_max
                    type_options_comments.append("Correct Multiple Choice format.")
                else:
                    current_q_type_options_score = base_type_options_max / 2
                    type_options_comments.append("Multiple Choice type, but options missing or empty.")
            elif q_type == "Open-ended Text":
                if isinstance(q_options, list) and len(q_options) == 0:
                    current_q_type_options_score = base_type_options_max
                    type_options_comments.append("Correct Open-ended format.")
                else: # options should be an empty list
                    current_q_type_options_score = base_type_options_max / 2
                    type_options_comments.append("Open-ended type, but options field not an empty list.")
        else:
            type_options_comments.append(f"Invalid or missing question type: '{q_type}'.")
        
        q_report["type_options_score"] = current_q_type_options_score
        q_report["type_options_comment"] = " ".join(type_options_comments)
        raw_achieved_score += current_q_type_options_score

        # Score Clarity
        if q_text and isinstance(q_text, str) and len(q_text.split()) >= 5: # At least 5 words
            current_q_clarity_score = base_clarity_max
            q_report["clarity_comment"] = "Clear."
        elif q_text and isinstance(q_text, str) and len(q_text.strip()) > 0:
            current_q_clarity_score = base_clarity_max / 2
            q_report["clarity_comment"] = "Somewhat clear or too brief."
        else:
            q_report["clarity_comment"] = "Question text missing or unclear."
        q_report["clarity_score"] = current_q_clarity_score
        raw_achieved_score += current_q_clarity_score
        
        question_details_report.append(q_report)

    # Apply scaling based on number of questions
    # The raw_achieved_score is sum of (up to) 5 points per question.
    # Max possible raw score is num_q_submitted * 5.
    # We need to scale this to the 30 point max for the question section.
    
    # If num_q_submitted is ideal (5, 6, or 7), the total score is capped at 30.
    # Each question contributes proportionally.
    if 5 <= num_q_submitted <= 7:
        # Max possible score for these questions is num_q_submitted * 5.
        # We want to scale this to 30.
        # Example: 5 questions, max raw = 25. If they get 20 raw, final = (20/25)*30 = 24.
        # Example: 7 questions, max raw = 35. If they get 28 raw, final = (28/35)*30 = 24.
        if num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max) > 0: # Avoid division by zero
             total_score = (raw_achieved_score / (num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max))) * TASK1_QUESTIONS_MAX
        else:
            total_score = 0
        quantity_comment = f"Correct number of questions ({num_q_submitted}). Score scaled to fit {TASK1_QUESTIONS_MAX} points."
    elif num_q_submitted < 5 and num_q_submitted > 0:
        # Proportional penalty for too few questions
        # Calculate score as if they submitted 5 questions, then penalize.
        # Max raw score if they had 5 questions = 5 * 5 = 25.
        # Their score relative to this: raw_achieved_score / (num_q_submitted * 5)
        # This proportion applied to 30 points, then penalized.
        base_score_if_ideal_count = 0
        if num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max) > 0:
            base_score_if_ideal_count = (raw_achieved_score / (num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max))) * TASK1_QUESTIONS_MAX
        
        penalty_factor = num_q_submitted / 5.0
        total_score = base_score_if_ideal_count * penalty_factor
        quantity_comment = f"Too few questions ({num_q_submitted} vs 5-7 expected). Base score adjusted by factor {penalty_factor:.2f}."
    elif num_q_submitted > 7:
        # Proportional penalty for too many questions
        base_score_if_ideal_count = 0
        if num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max) > 0:
            base_score_if_ideal_count = (raw_achieved_score / (num_q_submitted * (base_relevance_max + base_type_options_max + base_clarity_max))) * TASK1_QUESTIONS_MAX

        penalty_factor = 7.0 / num_q_submitted
        total_score = base_score_if_ideal_count * penalty_factor
        quantity_comment = f"Too many questions ({num_q_submitted} vs 5-7 expected). Base score adjusted by factor {penalty_factor:.2f}."

    total_score = min(total_score, TASK1_QUESTIONS_MAX) # Cap at max
    total_score = max(total_score, 0) # Ensure non-negative

    return total_score, quantity_comment, question_details_report, num_q_submitted


def score_task2_satisfaction_summary(candidate_summary, key_summary):
    score = 0
    comments = []
    details = {}

    if not isinstance(candidate_summary, dict):
        return 0, "Satisfaction summary not provided as a dictionary.", details

    points_per_rating = TASK2_SATISFACTION_SUMMARY_MAX / 5.0 # 4 points per rating

    for rating in ["1", "2", "3", "4", "5"]:
        candidate_count = get_nested_value(candidate_summary, (rating,))
        key_count = get_nested_value(key_summary, (rating,))
        
        details[f"rating_{rating}"] = {"candidate": candidate_count, "key": key_count, "score": 0}

        if isinstance(candidate_count, int) and candidate_count == key_count:
            score += points_per_rating
            details[f"rating_{rating}"]["score"] = points_per_rating
            comments.append(f"Rating '{rating}': Correct count ({candidate_count}).")
        elif candidate_count is not None:
            comments.append(f"Rating '{rating}': Incorrect count (Candidate: {candidate_count}, Key: {key_count}).")
            details[f"rating_{rating}"]["score"] = 0
        else:
            comments.append(f"Rating '{rating}': Missing in submission.")
            details[f"rating_{rating}"]["score"] = 0
            
    return score, "Satisfaction Summary: " + " ".join(comments) if comments else "No valid ratings found.", details

def score_task2_top_list(candidate_list, key_primary, key_secondary_options, list_name):
    score = 0
    comment = f"{list_name}: "

    if not isinstance(candidate_list, list) or len(candidate_list) != 2:
        comment += "Not a list of 2 items."
        return 0, comment

    candidate_set = set(item.strip() if isinstance(item, str) else "" for item in candidate_list)
    
    # Remove empty strings that might result from stripping non-string items
    candidate_set = {s for s in candidate_set if s}
    if len(candidate_set) != 2 : # check if two distinct non-empty strings were provided
        comment += "Does not contain two distinct non-empty string items."
        return 0, comment


    valid_sets = [{key_primary.strip(), opt.strip()} for opt in key_secondary_options]

    if candidate_set in valid_sets:
        score = TASK2_TOP_ENJOYED_MAX # Max score for this type of list (15 pts)
        comment += "Correctly identified top 2 items."
    else:
        # Partial credit attempt: check if primary is there
        partial_match = False
        if key_primary.strip() in candidate_set:
            score = TASK2_TOP_ENJOYED_MAX / 2
            comment += f"Partially correct: '{key_primary}' identified, but the second item is incorrect or missing from valid options."
            partial_match = True
        
        # Check if one of the secondary options is there (if primary wasn't)
        if not partial_match:
            for opt in key_secondary_options:
                if opt.strip() in candidate_set:
                    score = TASK2_TOP_ENJOYED_MAX / 2 # Or a smaller partial credit
                    comment += f"Partially correct: One valid item ('{opt}') identified, but the other is incorrect or missing."
                    partial_match = True
                    break
        if not partial_match:
             comment += "Incorrect items."
             
    return score, comment

def score_task2_recommendation(candidate_rec, key_top_improvement_suggestions):
    score = 0
    comments = []

    if not isinstance(candidate_rec, str) or not candidate_rec.strip():
        return 0, "Recommendation: Missing or empty."

    # Data-driven (5 pts)
    data_driven_score = 0
    rec_lower = candidate_rec.lower()
    
    # Themes from top improvement suggestions (example themes)
    # key_top_improvement_suggestions is a list like ["More prize categories", "Better mobile app"]
    # We need to extract themes from these.
    themes_found = 0
    # Theme 1 (e.g., from "More prize categories")
    if any(kw in rec_lower for kw in ["prize", "reward", "category", "categories"]):
        data_driven_score += 2.5
        themes_found +=1
    
    # Theme 2 (e.g., from "Better mobile app" or "Shorter duration")
    if any(kw in rec_lower for kw in ["app", "mobile", "duration", "shorter", "length", "time"]):
        if themes_found == 0: # First theme found
             data_driven_score += 2.5
        elif data_driven_score < 5.0: # Second distinct theme
             data_driven_score = 5.0 
        themes_found +=1

    if data_driven_score > 0:
        comments.append(f"Data-driven aspects identified (Score: {data_driven_score}/5).")
    else:
        comments.append("Recommendation does not clearly reflect data findings (Score: 0/5).")
    score += data_driven_score

    # Clarity/Actionability (5 pts)
    clarity_score = 0
    word_count = len(candidate_rec.split())
    if 10 <= word_count <= 70:
        clarity_score += 2.5
        comments.append(f"Appropriate length ({word_count} words).")
    else:
        comments.append(f"Length not ideal ({word_count} words, expected 10-70).")

    if contains_keywords(candidate_rec, RECOMMENDATION_ACTION_KEYWORDS):
        clarity_score += 2.5
        comments.append("Contains actionable language.")
    else:
        comments.append("Lacks clear actionable language.")
    score += clarity_score
    
    return score, "Recommendation: " + " ".join(comments)


def evaluate_submission(submission_data, key_data):
    results = {
        "candidate_name": get_nested_value(submission_data, ("candidate_name",), "N/A"),
        "candidate_id": get_nested_value(submission_data, ("candidate_id",), "N/A"),
        "overall_score": 0.0,
        "task_1_scores": {
            "total_task_1_score": 0,
            "max_score": TASK1_MAX_SCORE
        },
        "task_2_scores": {
            "total_task_2_score": 0,
            "max_score": TASK2_MAX_SCORE
        },
        "total_exam_score": 0,
        "max_exam_score": TOTAL_EXAM_MAX_SCORE
    }

    # --- Task 1 Evaluation ---
    task1_submission = get_nested_value(submission_data, ("task_1_interest_survey_design",), {})
    
    s, c = score_task1_survey_title(get_nested_value(task1_submission, ("survey_title",)))
    results["task_1_scores"]["survey_title"] = {"score": s, "max_score": TASK1_TITLE_MAX, "comment": c}
    results["task_1_scores"]["total_task_1_score"] += s

    s, c = score_task1_target_audience(get_nested_value(task1_submission, ("target_audience_description",)))
    results["task_1_scores"]["target_audience_description"] = {"score": s, "max_score": TASK1_AUDIENCE_MAX, "comment": c}
    results["task_1_scores"]["total_task_1_score"] += s

    s, c = score_task1_survey_introduction(get_nested_value(task1_submission, ("survey_introduction_text",)))
    results["task_1_scores"]["survey_introduction_text"] = {"score": s, "max_score": TASK1_INTRO_MAX, "comment": c}
    results["task_1_scores"]["total_task_1_score"] += s

    s, c, q_details, num_q = score_task1_survey_questions(get_nested_value(task1_submission, ("survey_questions",)))
    results["task_1_scores"]["survey_questions"] = {
        "score": s, "max_score": TASK1_QUESTIONS_MAX, "comment": c,
        "num_questions_provided": num_q, "num_questions_expected": "5-7",
        "question_details": q_details
    }
    results["task_1_scores"]["total_task_1_score"] += s

    # --- Task 2 Evaluation ---
    task2_submission = get_nested_value(submission_data, ("task_2_satisfaction_data_analysis",), {})
    task2_key = get_nested_value(key_data, ("task_2_satisfaction_data_analysis",), {})

    s, c, summary_details = score_task2_satisfaction_summary(
        get_nested_value(task2_submission, ("satisfaction_rating_summary",)),
        get_nested_value(task2_key, ("satisfaction_rating_summary",))
    )
    results["task_2_scores"]["satisfaction_rating_summary"] = {"score": s, "max_score": TASK2_SATISFACTION_SUMMARY_MAX, "comment": c, "details": summary_details}
    results["task_2_scores"]["total_task_2_score"] += s

    # Top Enjoyed Aspects
    # Key provides one valid pair, e.g., ["Team competition", "Tracking daily progress"]
    # Alternative for 2nd item: "Feeling healthier"
    key_enjoyed_primary = get_nested_value(task2_key, ("top_enjoyed_aspects", 0), "") # "Team competition"
    key_enjoyed_secondary_in_key = get_nested_value(task2_key, ("top_enjoyed_aspects", 1), "") # "Tracking daily progress"
    # Based on evaluation guide, the alternative secondary is "Feeling healthier"
    enjoyed_alt_secondary = "Feeling healthier" 
    key_enjoyed_secondary_options = [key_enjoyed_secondary_in_key, enjoyed_alt_secondary]
    
    s, c = score_task2_top_list(
        get_nested_value(task2_submission, ("top_enjoyed_aspects",)),
        key_enjoyed_primary,
        key_enjoyed_secondary_options,
        "Top Enjoyed Aspects"
    )
    results["task_2_scores"]["top_enjoyed_aspects"] = {"score": s, "max_score": TASK2_TOP_ENJOYED_MAX, "comment": c}
    results["task_2_scores"]["total_task_2_score"] += s
    
    # Top Improvement Suggestions
    # Key provides one valid pair, e.g., ["More prize categories", "Better mobile app"]
    # Alternative for 2nd item: "Shorter duration"
    key_improvement_primary = get_nested_value(task2_key, ("top_improvement_suggestions", 0), "") # "More prize categories"
    key_improvement_secondary_in_key = get_nested_value(task2_key, ("top_improvement_suggestions", 1), "") # "Better mobile app"
    improvement_alt_secondary = "Shorter duration"
    key_improvement_secondary_options = [key_improvement_secondary_in_key, improvement_alt_secondary]

    s, c = score_task2_top_list(
        get_nested_value(task2_submission, ("top_improvement_suggestions",)),
        key_improvement_primary,
        key_improvement_secondary_options,
        "Top Improvement Suggestions"
    )
    results["task_2_scores"]["top_improvement_suggestions"] = {"score": s, "max_score": TASK2_TOP_IMPROVEMENT_MAX, "comment": c}
    results["task_2_scores"]["total_task_2_score"] += s

    s, c = score_task2_recommendation(
        get_nested_value(task2_submission, ("recommendation_for_next_year",)),
        # Pass the actual top suggestions from the key for keyword checking
        [key_improvement_primary, key_improvement_secondary_in_key, improvement_alt_secondary] 
    )
    results["task_2_scores"]["recommendation_for_next_year"] = {"score": s, "max_score": TASK2_RECOMMENDATION_MAX, "comment": c}
    results["task_2_scores"]["total_task_2_score"] += s

    # --- Final Scores ---
    results["total_exam_score"] = results["task_1_scores"]["total_task_1_score"] + results["task_2_scores"]["total_task_2_score"]
    if TOTAL_EXAM_MAX_SCORE > 0:
        results["overall_score"] = round((results["total_exam_score"] / TOTAL_EXAM_MAX_SCORE) * 100, 2)
    else:
        results["overall_score"] = 0.0
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Evaluate Fitness and Wellness Coordinator exam submission.")
    parser.add_argument("submission_file", help="Path to the candidate's submission JSON file.")
    parser.add_argument("key_file", help="Path to the answer key JSON file.")
    args = parser.parse_args()

    try:
        with open(args.submission_file, 'r') as f:
            submission_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Submission file '{args.submission_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from submission file '{args.submission_file}'.")
        sys.exit(1)

    try:
        with open(args.key_file, 'r') as f:
            key_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Answer key file '{args.key_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from answer key file '{args.key_file}'.")
        sys.exit(1)

    evaluation_results = evaluate_submission(submission_data, key_data)

    try:
        with open("test_results.json", 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        print("Evaluation complete. Results saved to 'test_results.json'")
    except IOError:
        print("Error: Could not write results to 'test_results.json'.")
        sys.exit(1)

if __name__ == "__main__":
    main()