import json

def load_json(filename):
    """Loads JSON data from a file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filename}")
        return None

def evaluate_part1(candidate_answers, answer_key):
    """Evaluates Part 1 of the exam."""
    results_part1 = {}
    score_part1 = 0
    max_score_part1 = 0

    for question_id in ["question1", "question2", "question3", "question4"]:
        max_score_part1 += 1
        results_part1[question_id] = {"correct": False, "candidate_answer": "", "correct_answer": ""}
        candidate_answer = candidate_answers.get("part1_market_report_analysis", {}).get(f"answer{question_id[8:]}", "").strip()
        correct_answer = answer_key.get("part1_market_report_analysis", {}).get(f"answer{question_id[8:]}", "").strip()

        results_part1[question_id]["candidate_answer"] = candidate_answer
        results_part1[question_id]["correct_answer"] = correct_answer

        if question_id in ["question1", "question2", "question3"]:
            if candidate_answer.lower() == correct_answer.lower():
                results_part1[question_id]["correct"] = True
                score_part1 += 1
        elif question_id == "question4":
            # Basic keyword check for question 4 (can be improved with NLP techniques)
            if "commodity x" in candidate_answer.lower() or "commodity X" in candidate_answer.lower() or "tariff" in candidate_answer.lower() or "trade" in candidate_answer.lower(): # Simplified keyword check
                results_part1[question_id]["correct"] = True # Subjective, needs manual review for better accuracy
                score_part1 += 1
            else:
                results_part1[question_id]["correct"] = False # Subjective, needs manual review for better accuracy

    return results_part1, score_part1, max_score_part1

def evaluate_part2(candidate_answers, answer_key):
    """Evaluates Part 2 of the exam."""
    results_part2 = {}
    score_part2 = 0
    max_score_part2 = 0

    for question_id in ["question5", "question6", "question7", "question8"]:
        max_score_part2 += 1
        results_part2[question_id] = {"correct": False, "candidate_answer": "", "correct_answer": ""}
        candidate_answer = candidate_answers.get("part2_price_trend_analysis", {}).get(f"answer{question_id[8:]}", "").strip()
        correct_answer = answer_key.get("part2_price_trend_analysis", {}).get(f"answer{question_id[8:]}", "").strip()

        results_part2[question_id]["candidate_answer"] = candidate_answer
        results_part2[question_id]["correct_answer"] = correct_answer

        if question_id in ["question5", "question6", "question7"]:
            if candidate_answer.lower() == correct_answer.lower():
                results_part2[question_id]["correct"] = True
                score_part2 += 1
        elif question_id == "question8":
            try:
                candidate_percentage = float(candidate_answer.replace("%", "").strip())
                correct_percentage = float(correct_answer.replace("%", "").strip())
                if abs(candidate_percentage - correct_percentage) <= 0.01:
                    results_part2[question_id]["correct"] = True
                    score_part2 += 1
            except ValueError:
                results_part2[question_id]["correct"] = False

    return results_part2, score_part2, max_score_part2

def evaluate_part3(candidate_answers, answer_key):
    """Evaluates Part 3 of the exam."""
    results_part3 = {}
    score_part3 = 0
    max_score_part3 = 0

    for question_id in ["question9", "question10", "question11"]:
        max_score_part3 += 1
        results_part3[question_id] = {"correct": False, "candidate_answer": "", "correct_answer": ""}
        candidate_answer = candidate_answers.get("part3_supply_demand_factors", {}).get(f"answer{question_id[8:]}", "").strip()
        correct_answer = answer_key.get("part3_supply_demand_factors", {}).get(f"answer{question_id[8:]}", "").strip()

        results_part3[question_id]["candidate_answer"] = candidate_answer
        results_part3[question_id]["correct_answer"] = correct_answer

        if question_id in ["question9", "question10"]:
            if candidate_answer.lower() == correct_answer.lower():
                results_part3[question_id]["correct"] = True
                score_part3 += 1
        elif question_id == "question11":
            # Basic keyword check for question 11 (can be improved with NLP techniques)
            keywords = ["price", "increase", "volatility", "supply", "disrupt", "concern"]
            if all(keyword in candidate_answer.lower() for keyword in keywords): # Simplified keyword check
                results_part3[question_id]["correct"] = True # Subjective, needs manual review for better accuracy
                score_part3 += 1
            else:
                results_part3[question_id]["correct"] = False # Subjective, needs manual review for better accuracy

    return results_part3, score_part3, max_score_part3


def main():
    """Main function to evaluate the test and save results."""
    candidate_submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")

    if not candidate_submission or not answer_key:
        return

    results_part1, score_part1, max_score_part1 = evaluate_part1(candidate_submission, answer_key)
    results_part2, score_part2, max_score_part2 = evaluate_part2(candidate_submission, answer_key)
    results_part3, score_part3, max_score_part3 = evaluate_part3(candidate_submission, answer_key)

    overall_score = (score_part1 + score_part2 + score_part3) / (max_score_part1 + max_score_part2 + max_score_part3) * 100

    test_results = {
        "candidate_id": candidate_submission.get("candidate_id", "N/A"),
        "model_version": candidate_submission.get("model_version", "N/A"),
        "part1_market_report_analysis_results": results_part1,
        "part2_price_trend_analysis_results": results_part2,
        "part3_supply_demand_factors_results": results_part3,
        "overall_score": round(overall_score, 2),
        "scores_per_part": {
            "part1_score": score_part1,
            "part1_max_score": max_score_part1,
            "part2_score": score_part2,
            "part2_max_score": max_score_part2,
            "part3_score": score_part3,
            "part3_max_score": max_score_part3
        },
        "total_score": score_part1 + score_part2 + score_part3,
        "total_max_score": max_score_part1 + max_score_part2 + max_score_part3
    }

    with open("test_results.json", 'w') as outfile:
        json.dump(test_results, outfile, indent=4)

    print("Test evaluation completed. Results saved to test_results.json")
    print(f"Overall Score: {test_results['overall_score']}%")


if __name__ == "__main__":
    main()