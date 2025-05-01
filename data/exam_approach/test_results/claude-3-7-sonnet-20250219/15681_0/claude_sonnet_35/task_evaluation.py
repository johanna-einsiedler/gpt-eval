#!/usr/bin/env python3
import json
import sys
import os

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)

def evaluate_task1(submission, answer_key):
    """Evaluate Task 1: Basic Supply Chain Flow Diagram."""
    score = 0
    feedback = []
    
    # Check entities count (10 points)
    expected_count = answer_key["entities_count"]
    submitted_count = submission.get("entities_count", 0)
    
    if submitted_count == expected_count:
        score += 10
        feedback.append("Correctly identified all entities: 10/10 points")
    else:
        points = max(0, 10 - abs(expected_count - submitted_count) * 2)
        score += points
        feedback.append(f"Entity count mismatch. Expected {expected_count}, got {submitted_count}: {points}/10 points")
    
    # Check flow representation (15 points)
    diagram = submission.get("diagram", "")
    
    # Check for key elements in the diagram
    flow_points = 0
    
    # Check for suppliers
    if "[S]" in diagram and ("Supplier A" in diagram or "Supplier B" in diagram):
        flow_points += 3
    
    # Check for warehouse
    if "[W]" in diagram and "Warehouse" in diagram:
        flow_points += 3
    
    # Check for manufacturing plants
    if "[M]" in diagram and "Plant" in diagram:
        flow_points += 3
    
    # Check for distribution center
    if "[DC]" in diagram and "Distribution Center" in diagram:
        flow_points += 3
    
    # Check for retail outlets
    if "[R]" in diagram and "Retail" in diagram:
        flow_points += 3
    
    score += flow_points
    feedback.append(f"Flow representation: {flow_points}/15 points")
    
    # Check returns process (5 points)
    if "<--" in diagram:
        score += 5
        feedback.append("Returns process clearly shown: 5/5 points")
    else:
        feedback.append("Returns process not clearly shown: 0/5 points")
    
    return {
        "score": score,
        "max_score": 30,
        "feedback": feedback
    }

def evaluate_task2(submission, answer_key):
    """Evaluate Task 2: Data Visualization in Supply Chain Context."""
    score = 0
    feedback = []
    
    # Check inventory flow representation (10 points)
    diagram = submission.get("diagram", "")
    flow_points = 0
    
    if "Raw Materials" in diagram:
        flow_points += 2.5
    if "Work-in-Progress" in diagram:
        flow_points += 2.5
    if "Finished Goods" in diagram:
        flow_points += 2.5
    if "Distribution Center" in diagram:
        flow_points += 2.5
    
    score += flow_points
    feedback.append(f"Inventory flow representation: {flow_points}/10 points")
    
    # Check trend representation (10 points)
    trend_points = 0
    
    # Check if numbers are present in the diagram
    if any(str(num) in diagram for num in range(500, 1600)):
        trend_points += 5
    
    # Check if trends are shown (arrows, direction indicators, etc.)
    if "->" in diagram or "→" in diagram:
        trend_points += 5
    
    score += trend_points
    feedback.append(f"Trend representation: {trend_points}/10 points")
    
    # Check percentage changes (10 points)
    percentage_points = 0
    submitted_percentages = submission.get("percentage_changes", {})
    expected_percentages = answer_key["percentage_changes"]
    
    for key, expected_value in expected_percentages.items():
        if key in submitted_percentages:
            submitted_value = submitted_percentages[key]
            # Allow for small rounding differences (±0.1%)
            if abs(submitted_value - expected_value) <= 0.1:
                percentage_points += 2.5
            else:
                feedback.append(f"Incorrect percentage for {key}. Expected {expected_value}, got {submitted_value}")
        else:
            feedback.append(f"Missing percentage for {key}")
    
    score += percentage_points
    feedback.append(f"Percentage calculations: {percentage_points}/10 points")
    
    return {
        "score": score,
        "max_score": 30,
        "feedback": feedback
    }

def evaluate_task3(submission, answer_key):
    """Evaluate Task 3: Bottleneck Identification and Representation."""
    score = 0
    feedback = []
    
    # Check production flow diagram (10 points)
    diagram = submission.get("diagram", "")
    flow_points = 0
    
    if "Ingredient Mixing" in diagram:
        flow_points += 2
    if "Filling & Packaging" in diagram:
        flow_points += 2
    if "Quality Testing" in diagram:
        flow_points += 2
    if "Labeling" in diagram:
        flow_points += 2
    if "Palletizing" in diagram:
        flow_points += 2
    
    score += flow_points
    feedback.append(f"Production flow diagram: {flow_points}/10 points")
    
    # Check bottleneck identification (10 points)
    if "[!]" in diagram and "Filling & Packaging" in diagram and diagram.find("[!]") < diagram.find("Filling & Packaging") + 30:
        score += 10
        feedback.append("Bottleneck correctly identified: 10/10 points")
    else:
        feedback.append("Bottleneck not correctly identified: 0/10 points")
    
    # Check maximum throughput (10 points)
    expected_throughput = answer_key["max_throughput"]
    submitted_throughput = submission.get("max_throughput", 0)
    
    if submitted_throughput == expected_throughput:
        score += 10
        feedback.append(f"Maximum throughput correctly calculated: 10/10 points")
    else:
        feedback.append(f"Incorrect maximum throughput. Expected {expected_throughput}, got {submitted_throughput}: 0/10 points")
    
    # Check over-capacity stages (10 points)
    expected_stages = set(answer_key["over_capacity_stages"])
    submitted_stages = set(submission.get("over_capacity_stages", []))
    
    if submitted_stages == expected_stages:
        score += 10
        feedback.append("Over-capacity stages correctly identified: 10/10 points")
    else:
        feedback.append(f"Incorrect over-capacity stages. Expected {expected_stages}, got {submitted_stages}: 0/10 points")
    
    return {
        "score": score,
        "max_score": 40,
        "feedback": feedback
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_path = sys.argv[1]
    answer_key_path = sys.argv[2]
    
    submission = load_json_file(submission_path)
    answer_key = load_json_file(answer_key_path)
    
    # Evaluate each task
    task1_results = evaluate_task1(submission.get("task1", {}), answer_key["task1"])
    task2_results = evaluate_task2(submission.get("task2", {}), answer_key["task2"])
    task3_results = evaluate_task3(submission.get("task3", {}), answer_key["task3"])
    
    # Calculate overall score
    total_score = task1_results["score"] + task2_results["score"] + task3_results["score"]
    max_score = task1_results["max_score"] + task2_results["max_score"] + task3_results["max_score"]
    overall_percentage = (total_score / max_score) * 100
    
    # Determine if the candidate passed
    passed = (
        total_score >= 70 and
        task1_results["score"] >= 21 and
        task2_results["score"] >= 21 and
        task3_results["score"] >= 28
    )
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_percentage, 1),
        "total_points": total_score,
        "max_points": max_score,
        "passed": passed,
        "task1": task1_results,
        "task2": task2_results,
        "task3": task3_results
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {round(overall_percentage, 1)}%")
    print(f"Pass status: {'PASSED' if passed else 'FAILED'}")

if __name__ == "__main__":
    main()