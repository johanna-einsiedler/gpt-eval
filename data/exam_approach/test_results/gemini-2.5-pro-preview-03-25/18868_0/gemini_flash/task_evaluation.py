# task_evaluation.py

import json
import sys
import os

def load_json_file(file_path):
    """Loads a JSON file and returns its content."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def evaluate_submission(submission_data, key_data):
    """Compares submission data against the key and calculates the score."""
    results = {
        "overall_score": 0.0,
        "total_assessments": 0,
        "correct_assessments": 0,
        "details": []
    }
    correct_count = 0
    total_count = 0

    # Create dictionaries for easier lookup in the answer key
    key_job_map = {job['job_id']: job for job in key_data.get('job_matches', [])}

    # Check if submission has the required structure
    if 'job_matches' not in submission_data or not isinstance(submission_data['job_matches'], list):
        print("Error: Submission JSON is missing 'job_matches' list or has incorrect format.")
        # Return results with 0 score if structure is wrong
        return results

    # Iterate through jobs in the candidate's submission
    for sub_job in submission_data['job_matches']:
        job_id = sub_job.get('job_id')
        if not job_id:
            print(f"Warning: Submission contains a job entry without a 'job_id'. Skipping.")
            continue

        # Find the corresponding job in the answer key
        key_job = key_job_map.get(job_id)
        if not key_job:
            print(f"Warning: Job ID '{job_id}' from submission not found in answer key. Skipping assessments for this job.")
            # Count potential assessments in submission for total, but mark all as incorrect implicitly
            total_count += len(sub_job.get('applicant_assessments', []))
            for sub_assessment in sub_job.get('applicant_assessments', []):
                 results["details"].append({
                    "job_id": job_id,
                    "applicant_id": sub_assessment.get('applicant_id', 'UNKNOWN'),
                    "candidate_answer": sub_assessment.get('match_status', 'MISSING'),
                    "correct_answer": "N/A (Job ID not in key)",
                    "is_correct": False
                })
            continue # Skip to the next job in the submission

        # Create a dictionary for easier lookup of applicants within the key job
        key_applicant_map = {app['applicant_id']: app for app in key_job.get('applicant_assessments', [])}

        if 'applicant_assessments' not in sub_job or not isinstance(sub_job['applicant_assessments'], list):
             print(f"Warning: Job ID '{job_id}' in submission is missing 'applicant_assessments' list or has incorrect format. Skipping assessments.")
             continue

        # Iterate through applicant assessments in the candidate's submission for this job
        for sub_assessment in sub_job['applicant_assessments']:
            applicant_id = sub_assessment.get('applicant_id')
            candidate_answer = sub_assessment.get('match_status')
            total_count += 1 # Increment total count for every assessment attempted

            if not applicant_id:
                print(f"Warning: Submission contains an assessment without an 'applicant_id' for Job ID '{job_id}'. Marking as incorrect.")
                results["details"].append({
                    "job_id": job_id,
                    "applicant_id": "UNKNOWN",
                    "candidate_answer": candidate_answer,
                    "correct_answer": "N/A (Missing Applicant ID in submission)",
                    "is_correct": False
                })
                continue # Skip to next assessment

            # Find the corresponding applicant assessment in the answer key
            key_assessment = key_applicant_map.get(applicant_id)

            if not key_assessment:
                print(f"Warning: Applicant ID '{applicant_id}' for Job ID '{job_id}' from submission not found in answer key. Marking as incorrect.")
                results["details"].append({
                    "job_id": job_id,
                    "applicant_id": applicant_id,
                    "candidate_answer": candidate_answer,
                    "correct_answer": "N/A (Applicant ID not in key for this job)",
                    "is_correct": False
                })
                continue # Skip to next assessment

            correct_answer = key_assessment.get('match_status')
            is_correct = (candidate_answer == correct_answer)

            if is_correct:
                correct_count += 1

            results["details"].append({
                "job_id": job_id,
                "applicant_id": applicant_id,
                "candidate_answer": candidate_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

    # Calculate final score
    results["total_assessments"] = total_count
    results["correct_assessments"] = correct_count
    if total_count > 0:
        results["overall_score"] = round((correct_count / total_count) * 100, 2)
    else:
        results["overall_score"] = 0.0 # Avoid division by zero if no assessments found

    return results

def save_results(results, output_file="test_results.json"):
    """Saves the evaluation results to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Evaluation results saved to {output_file}")
    except Exception as e:
        print(f"Error writing results to file {output_file}: {e}")
        sys.exit(1)

def main():
    """Main function to handle arguments and run evaluation."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py <submission_file.json> <answer_key_file.json>")
        sys.exit(1)

    submission_file = sys.argv[1]
    key_file = sys.argv[2]
    output_file = "test_results.json"

    print(f"Loading submission file: {submission_file}")
    submission_data = load_json_file(submission_file)

    print(f"Loading answer key file: {key_file}")
    key_data = load_json_file(key_file)

    print("Evaluating submission...")
    evaluation_results = evaluate_submission(submission_data, key_data)

    save_results(evaluation_results, output_file)

if __name__ == "__main__":
    main()