import json

def validate_part1(specification_text):
    score = 0
    criteria_keywords = {
        "ink_color": ["ink color", "color of ink", "ink shade"],
        "writing_point": ["writing point", "point size", "line width"],
        "ink_type": ["ink type", "ink properties", "ink characteristics", "smudge", "drying"],
        "barrel_material": ["barrel material", "pen body material", "material of barrel"],
        "writing_length": ["writing length", "ink lifespan", "writing distance"],
        "packaging": ["packaging", "box quantity", "delivery"] # Added packaging as a key area
    }
    found_criteria = 0
    measurable_criteria = 0

    specification_lower = specification_text.lower()

    for category, keywords in criteria_keywords.items():
        for keyword in keywords:
            if keyword in specification_lower:
                found_criteria += 1
                if category in ["ink_color", "writing_point", "writing_length", "ink_type"]: # Example of categories that should be measurable
                    measurable_criteria += 1 # Simple check - needs more sophisticated measurability check in real scenario
                break # Only count each category once

    if found_criteria >= 5: score += 3 # Award points for number of criteria
    if measurable_criteria >= 4: score += 4 # Award points for measurability

    return score


def validate_part2(review_comments, revised_specification_text, answer_revised_specification_text):
    review_score = 0
    revised_score = 0

    expected_weakness_types = ["vague capacity", "vague material", "missing compatibility"] # Example weakness types

    identified_weakness_types = []
    for comment in review_comments:
        description_lower = comment['description'].lower()
        if "capacity" in description_lower and "vague" in description_lower:
            identified_weakness_types.append("vague capacity")
        elif "material" in description_lower and "vague" in description_lower or "generic" in description_lower:
            identified_weakness_types.append("vague material")
        elif "staple" in description_lower and "compatibility" in description_lower or "type" in description_lower and "missing" in description_lower:
            identified_weakness_types.append("missing compatibility")


    valid_weaknesses_count = len(set(expected_weakness_types) & set(identified_weakness_types)) # Count correctly identified weakness types

    if valid_weaknesses_count >= 2: review_score += 4 # Points for identifying weaknesses
    if len(review_comments) >= 3: review_score += 2 # Points for providing enough comments

    revised_specification_lower = revised_specification_text.lower()
    answer_revised_lower = answer_revised_specification_text.lower()

    improvement_keywords = {
        "capacity_improved": ["sheet capacity", "sheets of paper", "gsm paper", "stapling capacity", "sheets"],
        "material_improved": ["abs plastic", "steel mechanism", "material specification", "thickness"],
        "compatibility_improved": ["staple type", "compatible staples", "24/6", "26/6", "staple compatibility"]
    }

    improvements_made = 0
    for category, keywords in improvement_keywords.items():
        for keyword in keywords:
            if keyword in revised_specification_lower:
                improvements_made += 1
                break # Count each improvement type once

    if improvements_made >= 2: revised_score += 4
    return review_score, revised_score


def validate_basic_exam(submission_file, answer_key_file="answer_key.json"):
    with open(submission_file, 'r') as f:
        submission = json.load(f)
    with open(answer_key_file, 'r') as f:
        answer_key = json.load(f)

    part1_score = validate_part1(submission['part1_specification'])
    part2_review_score, part2_revised_score = validate_part2(submission['part2_review_comments'], submission['part2_revised_specification'], answer_key['part2_revised_specification'])

    total_score = part1_score + part2_review_score + part2_revised_score
    # Define passing threshold based on total_score or individual part scores
    passing_score = 7  # Example threshold - adjust as needed
    max_possible_score = 17 # Calculated max score

    overall_score_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0

    is_passing = total_score >= passing_score

    return {
        "total_score": total_score,
        "overall_score": overall_score_percentage,
        "is_passing": is_passing,
        "part1_score": part1_score,
        "part2_review_score": part2_review_score,
        "part2_revised_score": part2_revised_score
    }

if __name__ == "__main__":
    submission_file = "test_submission.json"
    answer_key_file = "answer_key.json"
    results = validate_basic_exam(submission_file, answer_key_file)

    # Prepare results for JSON output, rounding percentage
    results_output = {
        "candidate_id": "N/A", # You might want to extract this from submission if available
        "model_version": "N/A", # You might want to extract this from submission if available
        "test_results": {
            "total_score": results["total_score"],
            "overall_score_percentage": round(results["overall_score"], 2),
            "is_passing": results["is_passing"],
            "part1_score": results["part1_score"],
            "part2_review_score": results["part2_review_score"],
            "part2_revised_score": results["part2_revised_score"]
        }
    }

    try:
        with open("test_results.json", 'w') as outfile:
            json.dump(results_output, outfile, indent=4)
        print("Test results saved to test_results.json")
    except Exception as e:
        print(f"Error saving test_results.json: {e}")
        print("Raw results:")
        print(json.dumps(results_output, indent=4))