import json
import os

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def validate_graph_image():
    return os.path.exists('price_trend_graph.png')

def validate_word_count(text, min_words, max_words):
    word_count = len(text.split())
    return min_words <= word_count <= max_words

def validate_urls(urls):
    return all(url.startswith("http") for url in urls)

def evaluate_submission(candidate_submission, answer_key):
    results = {
        "Task1": {
            "graph_image": False,
            "analysis": False
        },
        "Task2": {
            "sources": False,
            "report": False
        },
        "overall_score": 0
    }

    # Task 1 Evaluation
    if validate_graph_image():
        results["Task1"]["graph_image"] = True

    if validate_word_count(candidate_submission["Task1"]["analysis"], 100, 200):
        results["Task1"]["analysis"] = True

    # Task 2 Evaluation
    if validate_urls(candidate_submission["Task2"]["sources"]):
        results["Task2"]["sources"] = True

    if validate_word_count(candidate_submission["Task2"]["report"], 150, 250):
        results["Task2"]["report"] = True

    # Calculate overall score
    total_criteria = 4
    passed_criteria = sum([
        results["Task1"]["graph_image"],
        results["Task1"]["analysis"],
        results["Task2"]["sources"],
        results["Task2"]["report"]
    ])
    results["overall_score"] = (passed_criteria / total_criteria) * 100

    return results

def main():
    candidate_submission = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')  # Assuming the answer key is provided as 'answer_key.json'

    results = evaluate_submission(candidate_submission, answer_key)

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()