import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate_data, answer_key):
    candidate_laws = candidate_data.get("task_1", {}).get("laws_and_regulations", [])
    answer_laws = answer_key.get("task_1", {}).get("laws_and_regulations", [])
    
    correct_count = 0
    detailed_results = []

    for candidate_law in candidate_laws:
        for answer_law in answer_laws:
            if candidate_law["name"].lower() == answer_law["name"].lower():
                correct_count += 1
                detailed_results.append({
                    "name": candidate_law["name"],
                    "correct": True,
                    "description_correct": candidate_law["description"].strip().lower() == answer_law["description"].strip().lower(),
                    "application_correct": candidate_law["application"].strip().lower() == answer_law["application"].strip().lower()
                })
                break
        else:
            detailed_results.append({
                "name": candidate_law["name"],
                "correct": False
            })

    return correct_count, detailed_results

def evaluate_task_2(candidate_data, answer_key):
    candidate_checklist = candidate_data.get("task_2", {}).get("compliance_checklist", [])
    answer_checklist = answer_key.get("task_2", {}).get("compliance_checklist", [])
    
    correct_count = 0
    detailed_results = []

    for candidate_item in candidate_checklist:
        for answer_item in answer_checklist:
            if candidate_item["law_or_regulation"].lower() == answer_item["law_or_regulation"].lower():
                correct_count += 1
                detailed_results.append({
                    "item": candidate_item["item"],
                    "correct": True,
                    "law_or_regulation_correct": candidate_item["law_or_regulation"].strip().lower() == answer_item["law_or_regulation"].strip().lower()
                })
                break
        else:
            detailed_results.append({
                "item": candidate_item["item"],
                "correct": False
            })

    return correct_count, detailed_results

def main():
    candidate_data = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')

    task_1_correct, task_1_results = evaluate_task_1(candidate_data, answer_key)
    task_2_correct, task_2_results = evaluate_task_2(candidate_data, answer_key)

    task_1_total = len(answer_key.get("task_1", {}).get("laws_and_regulations", []))
    task_2_total = len(answer_key.get("task_2", {}).get("compliance_checklist", []))

    overall_score = ((task_1_correct + task_2_correct) / (task_1_total + task_2_total)) * 100

    results = {
        "task_1_results": task_1_results,
        "task_2_results": task_2_results,
        "overall_score": overall_score
    }

    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()