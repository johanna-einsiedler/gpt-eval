import json
import re
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def evaluate_submission(submission, answer_key):
    results = {}
    total_points = 3
    points_earned = 0

    # Task 1: Evaluate Purchase Order Link
    if is_valid_url(submission.get("purchase_order_link", "")):
        results["purchase_order_link"] = "Valid URL"
        points_earned += 1
    else:
        results["purchase_order_link"] = "Invalid or missing URL"

    # Task 2: Evaluate RFP Text
    rfp_text = submission.get("rfp_text", "").lower()
    if all(keyword in rfp_text for keyword in ["office cleaning services", "evaluation criteria", "submission deadline"]):
        results["rfp_text"] = "RFP text is complete"
        points_earned += 1
    else:
        results["rfp_text"] = "RFP text is incomplete or missing key sections"

    # Task 3: Evaluate Requisition Review Summary
    requisition_summary = submission.get("requisition_review_summary", "").lower()
    discrepancies = len(re.findall(r"missing|incorrect|incomplete", requisition_summary))
    if discrepancies >= 2:
        results["requisition_review_summary"] = "Requisition review summary is sufficient"
        points_earned += 1
    else:
        results["requisition_review_summary"] = "Requisition review summary is insufficient"

    # Calculate overall score
    overall_score = (points_earned / total_points) * 100
    results["overall_score"] = overall_score

    return results

def main():
    # Load the candidate's submission
    with open('test_submission.json', 'r') as f:
        submission = json.load(f)

    # Load the answer key
    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)

    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)

    # Save the results
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()