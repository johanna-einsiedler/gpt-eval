import json

def load_json(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def evaluate_task_1(candidate, answer_key):
    candidate_regulations = candidate.get("task_1", {}).get("regulations", [])
    answer_regulations = answer_key.get("task_1", {}).get("regulations", [])
    
    correct_count = 0
    for candidate_reg in candidate_regulations:
        for answer_reg in answer_regulations:
            if candidate_reg["name"] == answer_reg["name"]:
                correct_count += 1
                break
    
    return correct_count, len(answer_regulations)

def evaluate_task_2(candidate, answer_key):
    candidate_checklist = candidate.get("task_2", {}).get("compliance_checklist", [])
    answer_checklist = answer_key.get("task_2", {}).get("compliance_checklist", [])
    
    correct_count = 0
    for candidate_step in candidate_checklist:
        for answer_step in answer_checklist:
            if candidate_step.startswith(answer_step.split(":")[0]):
                correct_count += 1
                break
    
    return correct_count, len(answer_checklist)

def calculate_overall_score(task_1_score, task_2_score, task_1_total, task_2_total):
    total_score = task_1_score + task_2_score
    total_possible = task_1_total + task_2_total
    return (total_score / total_possible) * 100

def main():
    candidate = load_json('test_submission.json')
    answer_key = load_json('answer_key.json')
    
    task_1_score, task_1_total = evaluate_task_1(candidate, answer_key)
    task_2_score, task_2_total = evaluate_task_2(candidate, answer_key)
    
    overall_score = calculate_overall_score(task_1_score, task_2_score, task_1_total, task_2_total)
    
    results = {
        "task_1_score": task_1_score,
        "task_1_total": task_1_total,
        "task_2_score": task_2_score,
        "task_2_total": task_2_total,
        "overall_score": overall_score
    }
    
    with open('test_results.json', 'w') as result_file:
        json.dump(results, result_file, indent=4)

if __name__ == "__main__":
    main()