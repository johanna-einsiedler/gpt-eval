#!/usr/bin/env python3
"""
Data Warehousing Documentation Skills Assessment Evaluator

This script evaluates a candidate's submission against an answer key and
generates a detailed results file with scores for each task and an overall score.

Usage:
    python task_evaluation.py test_submission.json answer_key.json
"""

import json
import sys
from typing import Dict, List, Any, Tuple


def load_json_file(file_path: str) -> Dict:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def evaluate_metadata_documentation(submission: List[Dict], answer_key: List[Dict]) -> Dict:
    """Evaluate Task 1: Metadata Documentation."""
    results = {
        "total_fields": len(answer_key),
        "correct_fields": 0,
        "field_details": []
    }
    
    # Create a dictionary of answer key fields for easier lookup
    answer_key_dict = {field["field_name"]: field for field in answer_key}
    submission_dict = {field["field_name"]: field for field in submission}
    
    # Check each field in the answer key
    for field_name, expected in answer_key_dict.items():
        field_result = {
            "field_name": field_name,
            "found": field_name in submission_dict,
            "properties": {
                "data_type": False,
                "description": False,
                "sample_values": False,
                "business_rules": False
            },
            "correct_properties": 0
        }
        
        if field_name in submission_dict:
            submitted = submission_dict[field_name]
            
            # Check data type
            field_result["properties"]["data_type"] = submitted["data_type"] == expected["data_type"]
            
            # Check description (exact match)
            field_result["properties"]["description"] = submitted["description"] == expected["description"]
            
            # Check business rules (exact match)
            field_result["properties"]["business_rules"] = submitted["business_rules"] == expected["business_rules"]
            
            # Check sample values (should contain values from the dataset)
            # This is more flexible - we just check if the submitted values could be from the dataset
            submitted_samples = [s.strip() for s in submitted["sample_values"].split(",")]
            expected_samples = [s.strip() for s in expected["sample_values"].split(",")]
            
            # For sample values, we're more lenient - just check if they provided valid samples
            # The candidate can choose any samples from the dataset
            field_result["properties"]["sample_values"] = len(submitted_samples) >= 2
            
            # Count correct properties
            field_result["correct_properties"] = sum(field_result["properties"].values())
            
            # A field is considered correct if at least 4 out of 5 properties are correct
            # (field name + 4 other properties)
            if field_result["correct_properties"] >= 4:
                results["correct_fields"] += 1
        
        results["field_details"].append(field_result)
    
    # Calculate score
    results["score"] = results["correct_fields"] / results["total_fields"] * 100
    results["passed"] = results["correct_fields"] >= 7  # At least 7 out of 9 fields (78%)
    
    return results


def evaluate_entity_relationship(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 2: Entity-Relationship Diagram."""
    results = {
        "entities": {
            "total": len(answer_key["entities"]),
            "correct": 0,
            "details": []
        },
        "relationships": {
            "total": len(answer_key["relationships"]),
            "correct": 0,
            "details": []
        }
    }
    
    # Evaluate entities
    answer_key_entities = {entity["entity_name"]: entity for entity in answer_key["entities"]}
    submission_entities = {entity["entity_name"]: entity for entity in submission["entities"]}
    
    for entity_name, expected in answer_key_entities.items():
        entity_result = {
            "entity_name": entity_name,
            "found": entity_name in submission_entities,
            "attributes_correct": False,
            "primary_key_correct": False
        }
        
        if entity_name in submission_entities:
            submitted = submission_entities[entity_name]
            
            # Check attributes (sets to handle any order)
            expected_attrs = set(expected["attributes"])
            submitted_attrs = set(submitted["attributes"])
            entity_result["attributes_correct"] = expected_attrs == submitted_attrs
            
            # Check primary key
            entity_result["primary_key_correct"] = submitted["primary_key"] == expected["primary_key"]
            
            # Entity is correct if both attributes and primary key are correct
            if entity_result["attributes_correct"] and entity_result["primary_key_correct"]:
                results["entities"]["correct"] += 1
        
        results["entities"]["details"].append(entity_result)
    
    # Evaluate relationships
    # Create a unique identifier for each relationship for comparison
    def relationship_key(rel: Dict) -> str:
        return f"{rel['from_entity']}_{rel['to_entity']}_{rel['relationship_type']}_{rel['cardinality']}"
    
    answer_key_relationships = {relationship_key(rel): rel for rel in answer_key["relationships"]}
    
    for rel in submission["relationships"]:
        rel_id = relationship_key(rel)
        relationship_result = {
            "from_entity": rel["from_entity"],
            "to_entity": rel["to_entity"],
            "correct": rel_id in answer_key_relationships
        }
        
        if rel_id in answer_key_relationships:
            results["relationships"]["correct"] += 1
        
        results["relationships"]["details"].append(relationship_result)
    
    # Calculate scores
    results["entities"]["score"] = results["entities"]["correct"] / results["entities"]["total"] * 100
    results["relationships"]["score"] = results["relationships"]["correct"] / results["relationships"]["total"] * 100
    
    # Task passes if at least 5 out of 7 entities (71%) and 5 out of 7 relationships (71%) are correct
    results["entities"]["passed"] = results["entities"]["correct"] >= 5
    results["relationships"]["passed"] = results["relationships"]["correct"] >= 5
    results["passed"] = results["entities"]["passed"] and results["relationships"]["passed"]
    
    return results


def evaluate_process_documentation(submission: Dict, answer_key: Dict) -> Dict:
    """Evaluate Task 3: Business Process Documentation."""
    process_doc = submission["process_documentation"]
    expected_doc = answer_key["process_documentation"]
    
    results = {
        "process_info": {
            "name_correct": process_doc["process_name"] == expected_doc["process_name"],
            "owner_correct": process_doc["process_owner"] == expected_doc["process_owner"]
        },
        "process_steps": {
            "total": len(expected_doc["process_steps"]),
            "correct": 0,
            "details": []
        },
        "process_flow": {
            "total": len(expected_doc["process_flow"]),
            "correct": 0,
            "details": []
        }
    }
    
    # Evaluate process steps
    # Create a dictionary of steps by number for easier lookup
    expected_steps = {step["step_number"]: step for step in expected_doc["process_steps"]}
    submitted_steps = {step["step_number"]: step for step in process_doc["process_steps"]}
    
    for step_num, expected in expected_steps.items():
        step_result = {
            "step_number": step_num,
            "found": step_num in submitted_steps,
            "properties": {
                "step_name": False,
                "step_description": False,
                "input": False,
                "output": False,
                "system": False
            },
            "correct_properties": 0
        }
        
        if step_num in submitted_steps:
            submitted = submitted_steps[step_num]
            
            # Check each property
            for prop in ["step_name", "step_description", "input", "output", "system"]:
                step_result["properties"][prop] = submitted[prop] == expected[prop]
            
            step_result["correct_properties"] = sum(step_result["properties"].values())
            
            # A step is correct if all properties are correct
            if step_result["correct_properties"] == 5:
                results["process_steps"]["correct"] += 1
        
        results["process_steps"]["details"].append(step_result)
    
    # Evaluate process flow
    # Create a unique identifier for each flow connection
    def flow_key(flow: Dict) -> str:
        return f"{flow['from_step']}_{flow['to_step']}_{flow['condition']}"
    
    expected_flows = {flow_key(flow): flow for flow in expected_doc["process_flow"]}
    
    for flow in process_doc["process_flow"]:
        flow_id = flow_key(flow)
        flow_result = {
            "from_step": flow["from_step"],
            "to_step": flow["to_step"],
            "condition": flow["condition"],
            "correct": flow_id in expected_flows
        }
        
        if flow_id in expected_flows:
            results["process_flow"]["correct"] += 1
        
        results["process_flow"]["details"].append(flow_result)
    
    # Calculate scores
    results["process_steps"]["score"] = results["process_steps"]["correct"] / results["process_steps"]["total"] * 100
    results["process_flow"]["score"] = results["process_flow"]["correct"] / results["process_flow"]["total"] * 100
    
    # Task passes if:
    # - Process name and owner are correct
    # - At least 6 out of 8 process steps are correct (75%)
    # - At least 7 out of 10 process flow connections are correct (70%)
    basic_info_correct = results["process_info"]["name_correct"] and results["process_info"]["owner_correct"]
    steps_passed = results["process_steps"]["correct"] >= 6
    flow_passed = results["process_flow"]["correct"] >= 7
    
    results["passed"] = basic_info_correct and steps_passed and flow_passed
    
    return results


def calculate_overall_score(task_results: Dict) -> Tuple[float, bool]:
    """Calculate the overall score and determine if the candidate passed."""
    # Calculate weighted score across all tasks
    task1_weight = 0.33
    task2_weight = 0.33
    task3_weight = 0.34
    
    task1_score = task_results["task1"]["score"]
    
    # For task 2, average the entities and relationships scores
    task2_entities_score = task_results["task2"]["entities"]["score"]
    task2_relationships_score = task_results["task2"]["relationships"]["score"]
    task2_score = (task2_entities_score + task2_relationships_score) / 2
    
    # For task 3, average the process steps and flow scores
    task3_steps_score = task_results["task3"]["process_steps"]["score"]
    task3_flow_score = task_results["task3"]["process_flow"]["score"]
    # Deduct points if process name or owner is incorrect
    process_info_score = 100 if (task_results["task3"]["process_info"]["name_correct"] and 
                                task_results["task3"]["process_info"]["owner_correct"]) else 0
    task3_score = (process_info_score + task3_steps_score + task3_flow_score) / 3
    
    # Calculate weighted overall score
    overall_score = (
        task1_score * task1_weight +
        task2_score * task2_weight +
        task3_score * task3_weight
    )
    
    # Count passed tasks
    tasks_passed = sum([
        task_results["task1"]["passed"],
        task_results["task2"]["passed"],
        task_results["task3"]["passed"]
    ])
    
    # Candidate passes if they pass at least 2 out of 3 tasks and have an overall score of at least 75%
    passed = tasks_passed >= 2 and overall_score >= 75
    
    return overall_score, passed


def main():
    """Main function to evaluate the candidate submission."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    # Load the files
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    # Evaluate each task
    task_results = {
        "task1": evaluate_metadata_documentation(
            submission["task1"]["metadata_documentation"],
            answer_key["task1"]["metadata_documentation"]
        ),
        "task2": evaluate_entity_relationship(
            submission["task2"],
            answer_key["task2"]
        ),
        "task3": evaluate_process_documentation(
            submission["task3"],
            answer_key["task3"]
        )
    }
    
    # Calculate overall score
    overall_score, passed = calculate_overall_score(task_results)
    
    # Prepare results
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "overall_score": round(overall_score, 2),
        "passed": passed,
        "tasks_passed": sum([
            task_results["task1"]["passed"],
            task_results["task2"]["passed"],
            task_results["task3"]["passed"]
        ]),
        "task_results": task_results
    }
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    print(f"Result: {'PASSED' if results['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()