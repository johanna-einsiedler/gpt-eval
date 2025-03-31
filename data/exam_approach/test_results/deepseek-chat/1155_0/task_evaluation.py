import json

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found in the directory.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        exit(1)

def calculate_score(submission, answer_key):
    score = 0
    max_score = 100
    details = {
        "task_1": {"points": 0, "max_points": 50, "errors": []},
        "task_2": {"points": 0, "max_points": 50, "errors": []},
        "formatting": {"points": 0, "max_points": 10, "errors": []}
    }
    
    # Check JSON formatting (10 points)
    try:
        required_fields = {
            "task_1": ["hs_code", "product_value", "duty_rate", "total_duty"],
            "task_2": ["incoterm", "responsible_party", "payment_method", "required_documents"]
        }
        
        for task, fields in required_fields.items():
            if task not in submission:
                details["formatting"]["errors"].append(f"Missing {task} in submission")
                continue
            for field in fields:
                if field not in submission[task]:
                    details["formatting"]["errors"].append(f"Missing {field} in {task}")
        
        if not details["formatting"]["errors"]:
            details["formatting"]["points"] = 10
            score += 10
    except Exception as e:
        details["formatting"]["errors"].append(f"JSON structure validation failed: {str(e)}")
    
    # Task 1 Evaluation (50 points)
    try:
        t1 = submission["task_1"]
        ak1 = answer_key["task_1"]
        task1_points = 0
        
        # HS Code (15 points)
        if t1["hs_code"] == ak1["hs_code"]:
            task1_points += 15
        else:
            details["task_1"]["errors"].append("Incorrect HS Code")
        
        # Product Value (5 points)
        if float(t1["product_value"]) == float(ak1["product_value"]):
            task1_points += 5
        else:
            details["task_1"]["errors"].append("Incorrect product value")
        
        # Duty Rate (5 points)
        if float(t1["duty_rate"]) == float(ak1["duty_rate"]):
            task1_points += 5
        else:
            details["task_1"]["errors"].append("Incorrect duty rate")
        
        # Total Duty (25 points)
        expected_duty = float(ak1["product_value"]) * float(ak1["duty_rate"]) / 100
        submitted_duty = float(t1["total_duty"])
        
        if abs(submitted_duty - expected_duty) < 0.01:  # Allow for floating point precision
            task1_points += 25
        else:
            details["task_1"]["errors"].append(f"Incorrect duty calculation. Expected: {expected_duty:.2f}, Got: {submitted_duty:.2f}")
        
        details["task_1"]["points"] = task1_points
        score += task1_points
    except KeyError as e:
        details["task_1"]["errors"].append(f"Missing required field: {str(e)}")
    except Exception as e:
        details["task_1"]["errors"].append(f"Task 1 evaluation error: {str(e)}")
    
    # Task 2 Evaluation (50 points)
    try:
        t2 = submission["task_2"]
        ak2 = answer_key["task_2"]
        task2_points = 0
        
        # Incoterm (10 points)
        if t2["incoterm"].upper() == ak2["incoterm"].upper():
            task2_points += 10
        else:
            details["task_2"]["errors"].append("Incorrect Incoterm")
        
        # Responsible Party (10 points)
        if t2["responsible_party"].lower() == ak2["responsible_party"].lower():
            task2_points += 10
        else:
            details["task_2"]["errors"].append("Incorrect responsible party")
        
        # Payment Method (10 points)
        if t2["payment_method"].lower() == ak2["payment_method"].lower():
            task2_points += 10
        else:
            details["task_2"]["errors"].append("Incorrect payment method")
        
        # Required Documents (20 points)
        submitted_docs = set(doc.lower() for doc in t2["required_documents"])
        expected_docs = set(doc.lower() for doc in ak2["required_documents"])
        
        if submitted_docs == expected_docs:
            task2_points += 20
        else:
            missing = expected_docs - submitted_docs
            extra = submitted_docs - expected_docs
            if missing:
                details["task_2"]["errors"].append(f"Missing documents: {', '.join(missing)}")
            if extra:
                details["task_2"]["errors"].append(f"Extra documents: {', '.join(extra)}")
        
        details["task_2"]["points"] = task2_points
        score += task2_points
    except KeyError as e:
        details["task_2"]["errors"].append(f"Missing required field: {str(e)}")
    except Exception as e:
        details["task_2"]["errors"].append(f"Task 2 evaluation error: {str(e)}")
    
    # Calculate overall score percentage
    overall_score = (score / max_score) * 100
    
    return {
        "overall_score": round(overall_score, 2),
        "total_score": score,
        "max_score": max_score,
        "details": details
    }

def save_results(results):
    with open('test_results.json', 'w') as file:
        json.dump(results, file, indent=2)

def main():
    # Load submission and answer key
    submission = load_json_file('test_submission.json')
    answer_key = load_json_file('answer_key.json')
    
    # Calculate score
    results = calculate_score(submission, answer_key)
    
    # Save results
    save_results(results)
    
    print(f"Evaluation complete. Overall score: {results['overall_score']}%")
    print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    main()