import json
import os

def load_json_file(file_path):
    """Load and return JSON data from a file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' contains invalid JSON.")
        return None

def validate_calculation(expected, submitted):
    """Validate calculation answers with a ±$1.00 tolerance."""
    return abs(expected - submitted) <= 1

def evaluate_question1_1(answer_key, submission):
    """Evaluate the multi-select question 1.1."""
    correct_answers = set(answer_key['question1_1'])
    submitted_answers = set(submission.get('question1_1', []))
    
    points_earned = 0
    max_points = len(correct_answers)
    incorrect_selections = len(submitted_answers - correct_answers)
    
    # Award points for correct selections but deduct for incorrect ones
    points_earned = max(0, len(correct_answers & submitted_answers) - incorrect_selections)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_answers': list(correct_answers),
        'submitted_answers': list(submitted_answers),
        'is_correct': correct_answers == submitted_answers
    }

def evaluate_question1_2(answer_key, submission):
    """Evaluate the true/false question 1.2."""
    correct_answers = answer_key['question1_2']
    submitted_answers = submission.get('question1_2', {})
    
    points_earned = 0
    max_points = len(correct_answers)
    
    correct_items = []
    incorrect_items = []
    
    for key in correct_answers:
        if key in submitted_answers and submitted_answers[key] == correct_answers[key]:
            points_earned += 1
            correct_items.append(key)
        else:
            incorrect_items.append(key)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_items': correct_items,
        'incorrect_items': incorrect_items,
        'is_correct': points_earned == max_points
    }

def evaluate_question2_1(answer_key, submission):
    """Evaluate the sequence question 2.1."""
    correct_sequence = answer_key['question2_1']
    submitted_sequence = submission.get('question2_1', [])
    
    points_earned = 0
    max_points = len(correct_sequence)
    
    # Check each position in the sequence
    correct_positions = []
    incorrect_positions = []
    
    for i in range(min(len(correct_sequence), len(submitted_sequence))):
        if i < len(submitted_sequence) and submitted_sequence[i] == correct_sequence[i]:
            points_earned += 1
            correct_positions.append(i)
        else:
            incorrect_positions.append(i)
    
    # Penalize for missing positions
    if len(submitted_sequence) < len(correct_sequence):
        incorrect_positions.extend(range(len(submitted_sequence), len(correct_sequence)))
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_positions': correct_positions,
        'incorrect_positions': incorrect_positions,
        'is_correct': correct_sequence == submitted_sequence
    }

def evaluate_question2_2(answer_key, submission):
    """Evaluate the matching question 2.2."""
    correct_matches = answer_key['question2_2']
    submitted_matches = submission.get('question2_2', {})
    
    points_earned = 0
    max_points = len(correct_matches)
    
    correct_scenarios = []
    incorrect_scenarios = []
    
    for scenario, correct_answer in correct_matches.items():
        if scenario in submitted_matches and submitted_matches[scenario] == correct_answer:
            points_earned += 1
            correct_scenarios.append(scenario)
        else:
            incorrect_scenarios.append(scenario)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_scenarios': correct_scenarios,
        'incorrect_scenarios': incorrect_scenarios,
        'is_correct': points_earned == max_points
    }

def evaluate_question3_1(answer_key, submission):
    """Evaluate the calculation question 3.1."""
    correct_calculations = answer_key['question3_1']
    submitted_calculations = submission.get('question3_1', {})
    
    points_earned = 0
    max_points = len(correct_calculations)
    
    correct_clients = []
    incorrect_clients = []
    
    for client, correct_value in correct_calculations.items():
        if client in submitted_calculations and validate_calculation(correct_value, submitted_calculations[client]):
            points_earned += 1
            correct_clients.append(client)
        else:
            incorrect_clients.append(client)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_clients': correct_clients,
        'incorrect_clients': incorrect_clients,
        'is_correct': points_earned == max_points
    }

def evaluate_question3_2(answer_key, submission):
    """Evaluate the royalty calculation question 3.2."""
    correct_calculations = answer_key['question3_2']
    submitted_calculations = submission.get('question3_2', {})
    
    points_earned = 0
    max_points = len(correct_calculations)
    
    correct_categories = []
    incorrect_categories = []
    
    for category, correct_value in correct_calculations.items():
        if category in submitted_calculations and validate_calculation(correct_value, submitted_calculations[category]):
            points_earned += 1
            correct_categories.append(category)
        else:
            incorrect_categories.append(category)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_categories': correct_categories,
        'incorrect_categories': incorrect_categories,
        'is_correct': points_earned == max_points
    }

def evaluate_question4_1(answer_key, submission):
    """Evaluate the document matching question 4.1."""
    correct_matches = answer_key['question4_1']
    submitted_matches = submission.get('question4_1', {})
    
    points_earned = 0
    max_points = len(correct_matches)
    
    correct_items = []
    incorrect_items = []
    
    for item, correct_purpose in correct_matches.items():
        if item in submitted_matches and submitted_matches[item] == correct_purpose:
            points_earned += 1
            correct_items.append(item)
        else:
            incorrect_items.append(item)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_items': correct_items,
        'incorrect_items': incorrect_items,
        'is_correct': points_earned == max_points
    }

def evaluate_question4_2(answer_key, submission):
    """Evaluate the multi-select question 4.2."""
    correct_answers = set(answer_key['question4_2'])
    submitted_answers = set(submission.get('question4_2', []))
    
    # Calculate correct selections and incorrect selections
    correct_selections = correct_answers & submitted_answers
    incorrect_selections = submitted_answers - correct_answers
    
    # Points earned are correct selections minus incorrect selections, minimum 0
    points_earned = max(0, len(correct_selections) - len(incorrect_selections))
    max_points = len(correct_answers)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_selections': list(correct_selections),
        'incorrect_selections': list(incorrect_selections),
        'missing_selections': list(correct_answers - submitted_answers),
        'is_correct': correct_answers == submitted_answers
    }

def evaluate_question5_1(answer_key, submission):
    """Evaluate the ethical practices multi-select question 5.1."""
    correct_answers = set(answer_key['question5_1'])
    submitted_answers = set(submission.get('question5_1', []))
    
    # Calculate correct selections and incorrect selections
    correct_selections = correct_answers & submitted_answers
    incorrect_selections = submitted_answers - correct_answers
    
    # Points earned are correct selections minus incorrect selections, minimum 0
    points_earned = max(0, len(correct_selections) - len(incorrect_selections))
    max_points = len(correct_answers)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_selections': list(correct_selections),
        'incorrect_selections': list(incorrect_selections),
        'missing_selections': list(correct_answers - submitted_answers),
        'is_correct': correct_answers == submitted_answers
    }

def evaluate_question5_2(answer_key, submission):
    """Evaluate the ethical scenario judgments question 5.2."""
    correct_judgments = answer_key['question5_2']
    submitted_judgments = submission.get('question5_2', {})
    
    points_earned = 0
    max_points = len(correct_judgments)
    
    correct_scenarios = []
    incorrect_scenarios = []
    
    for scenario, correct_judgment in correct_judgments.items():
        if scenario in submitted_judgments and submitted_judgments[scenario] == correct_judgment:
            points_earned += 1
            correct_scenarios.append(scenario)
        else:
            incorrect_scenarios.append(scenario)
    
    return {
        'points_earned': points_earned,
        'max_points': max_points,
        'correct_scenarios': correct_scenarios,
        'incorrect_scenarios': incorrect_scenarios,
        'is_correct': points_earned == max_points
    }

def evaluate_test(answer_key, submission):
    """Evaluate the full test against the answer key."""
    results = {
        'candidate_id': submission.get('candidate_id', 'Unknown'),
        'model': submission.get('model', 'Unknown'),
        'section_results': {}
    }
    
    # Evaluate each section
    section1 = {
        'question1_1': evaluate_question1_1(answer_key, submission),
        'question1_2': evaluate_question1_2(answer_key, submission)
    }
    
    section2 = {
        'question2_1': evaluate_question2_1(answer_key, submission),
        'question2_2': evaluate_question2_2(answer_key, submission)
    }
    
    section3 = {
        'question3_1': evaluate_question3_1(answer_key, submission),
        'question3_2': evaluate_question3_2(answer_key, submission)
    }
    
    section4 = {
        'question4_1': evaluate_question4_1(answer_key, submission),
        'question4_2': evaluate_question4_2(answer_key, submission)
    }
    
    section5 = {
        'question5_1': evaluate_question5_1(answer_key, submission),
        'question5_2': evaluate_question5_2(answer_key, submission)
    }
    
    # Store section results
    results['section_results'] = {
        'section1': section1,
        'section2': section2,
        'section3': section3,
        'section4': section4,
        'section5': section5
    }
    
    # Calculate section scores
    section_scores = {
        'section1': sum(q['points_earned'] for q in section1.values()),
        'section2': sum(q['points_earned'] for q in section2.values()),
        'section3': sum(q['points_earned'] for q in section3.values()),
        'section4': sum(q['points_earned'] for q in section4.values()),
        'section5': sum(q['points_earned'] for q in section5.values())
    }
    
    section_max_scores = {
        'section1': sum(q['max_points'] for q in section1.values()),
        'section2': sum(q['max_points'] for q in section2.values()),
        'section3': sum(q['max_points'] for q in section3.values()),
        'section4': sum(q['max_points'] for q in section4.values()),
        'section5': sum(q['max_points'] for q in section5.values())
    }
    
    # Store section scores
    results['section_scores'] = {
        section: {
            'points_earned': section_scores[section],
            'max_points': section_max_scores[section],
            'percentage': (section_scores[section] / section_max_scores[section]) * 100 if section_max_scores[section] > 0 else 0
        }
        for section in section_scores
    }
    
    # Calculate total score
    total_points_earned = sum(section_scores.values())
    total_max_points = sum(section_max_scores.values())
    
    results['total_points_earned'] = total_points_earned
    results['total_max_points'] = total_max_points
    results['overall_score'] = (total_points_earned / total_max_points) * 100 if total_max_points > 0 else 0
    
    # Determine if the candidate passed
    # Passing criteria: 80% overall (35/44 points) and at least 50% in each section
    passing_threshold = 80
    section_minimum_threshold = 50
    
    section_percentages = {
        section: results['section_scores'][section]['percentage']
        for section in results['section_scores']
    }
    
    results['passed_overall_threshold'] = results['overall_score'] >= passing_threshold
    results['passed_section_thresholds'] = all(percentage >= section_minimum_threshold for percentage in section_percentages.values())
    
    # Special check for section3 (calculation accuracy)
    calculation_failure = section_scores['section3'] < section_max_scores['section3'] / 2
    
    results['calculation_failure'] = calculation_failure
    results['passed_exam'] = (
        results['passed_overall_threshold'] and 
        results['passed_section_thresholds'] and 
        not results['calculation_failure']
    )
    
    return results

def main():
    # Define file paths
    answer_key_path = 'answer_key.json'
    submission_path = 'test_submission.json'
    results_path = 'test_results.json'
    
    # Load answer key and submission
    answer_key = load_json_file(answer_key_path)
    submission = load_json_file(submission_path)
    
    # Check if files were loaded successfully
    if not answer_key or not submission:
        print("Error: Could not evaluate test due to missing or invalid files.")
        return
    
    # Evaluate the test
    results = evaluate_test(answer_key, submission)
    
    # Save results to JSON file
    try:
        with open(results_path, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Evaluation completed successfully. Results saved to '{results_path}'.")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()