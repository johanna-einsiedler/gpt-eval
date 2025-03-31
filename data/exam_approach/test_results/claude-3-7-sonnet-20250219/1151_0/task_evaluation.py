import json
import re
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10

def load_json(filename):
    """Load JSON data from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json(data, filename):
    """Save data as JSON to a file."""
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def within_tolerance(value1, value2, tolerance):
    """Check if two values are within a specified tolerance."""
    if isinstance(value1, str) or isinstance(value2, str):
        return value1 == value2
    return abs(float(value1) - float(value2)) <= float(tolerance)

def matches_pattern(text, pattern):
    """Check if text matches a regex pattern."""
    return bool(re.match(pattern, text))

def evaluate_exercise1(submission, answer_key):
    """Evaluate Exercise 1 (35 points total)."""
    results = {
        "points_earned": 0,
        "max_points": 35,
        "details": {}
    }
    
    # Check product code identification (6 points)
    product_codes_correct = True
    missing_codes = ["TU-6543", "RS-4321", "VW-8765"]
    submission_codes = [record["productCode"] for record in submission["updatedRecords"]]
    
    for code in missing_codes:
        if code not in submission_codes:
            product_codes_correct = False
            
    if product_codes_correct:
        results["details"]["product_code_identification"] = {
            "earned": 6,
            "max": 6,
            "comment": "All product codes correctly identified"
        }
        results["points_earned"] += 6
    else:
        results["details"]["product_code_identification"] = {
            "earned": 0,
            "max": 6,
            "comment": "Missing or incorrect product codes"
        }
    
    # Check total value calculations (8 points)
    total_value_errors = 0
    for sub_record in submission["updatedRecords"]:
        expected_total = float(sub_record["quantity"]) * float(sub_record["unitCost"])
        if not within_tolerance(sub_record["totalValue"], expected_total, 0.02):
            total_value_errors += 1
    
    total_value_score = 8 - min(total_value_errors, 8)
    results["points_earned"] += total_value_score
    results["details"]["total_value_calculations"] = {
        "earned": total_value_score,
        "max": 8,
        "comment": f"{total_value_errors} errors in total value calculations"
    }
    
    # Check reorder status identification (7 points)
    # Create a mapping of product codes to minimum stock from answer key
    min_stock_map = {}
    for record in answer_key["exercise1"]["updatedRecords"]:
        product_code = record["productCode"]
        status = record["status"]
        # Find the corresponding record in the original data to get min stock
        for orig_record in submission["updatedRecords"]:
            if orig_record["productCode"] == product_code:
                min_stock_map[product_code] = status
                break
    
    reorder_errors = 0
    for sub_record in submission["updatedRecords"]:
        product_code = sub_record["productCode"]
        if product_code in min_stock_map:
            expected_status = min_stock_map[product_code]
            if sub_record["status"] != expected_status:
                reorder_errors += 1
    
    reorder_score = 7 - min(reorder_errors, 7)
    results["points_earned"] += reorder_score
    results["details"]["reorder_status_identification"] = {
        "earned": reorder_score,
        "max": 7,
        "comment": f"{reorder_errors} errors in reorder status identification"
    }
    
    # Check summary statistics (8 points)
    summary_points = 0
    
    # Total items (2 points)
    if submission["totalItems"] == answer_key["exercise1"]["totalItems"]:
        summary_points += 2
        results["details"]["total_items"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct total items count"
        }
    else:
        results["details"]["total_items"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect total items: got {submission['totalItems']}, expected {answer_key['exercise1']['totalItems']}"
        }
    
    # Total value (2 points)
    if within_tolerance(submission["totalValue"], answer_key["exercise1"]["totalValue"], 0.02):
        summary_points += 2
        results["details"]["total_value"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct total inventory value"
        }
    else:
        results["details"]["total_value"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect total value: got {submission['totalValue']}, expected {answer_key['exercise1']['totalValue']}"
        }
    
    # Reorder count (2 points)
    if submission["reorderCount"] == answer_key["exercise1"]["reorderCount"]:
        summary_points += 2
        results["details"]["reorder_count"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct reorder count"
        }
    else:
        results["details"]["reorder_count"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect reorder count: got {submission['reorderCount']}, expected {answer_key['exercise1']['reorderCount']}"
        }
    
    # Most expensive item (2 points)
    if (submission["mostExpensiveItem"]["productCode"] == answer_key["exercise1"]["mostExpensiveItem"]["productCode"] and
        within_tolerance(submission["mostExpensiveItem"]["unitCost"], 
                         answer_key["exercise1"]["mostExpensiveItem"]["unitCost"], 0.02)):
        summary_points += 2
        results["details"]["most_expensive_item"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correctly identified most expensive item"
        }
    else:
        results["details"]["most_expensive_item"] = {
            "earned": 0,
            "max": 2,
            "comment": "Incorrectly identified most expensive item"
        }
    
    results["points_earned"] += summary_points
    
    # Check JSON formatting (6 points)
    # This is a simplified check - in a real scenario, you might want more detailed validation
    json_format_score = 6  # Assume correct format initially
    
    # Check if all required fields are present
    required_fields = ["totalItems", "totalValue", "reorderCount", "mostExpensiveItem", "updatedRecords"]
    for field in required_fields:
        if field not in submission:
            json_format_score -= 2
            break
    
    # Check if mostExpensiveItem has the correct structure
    if "mostExpensiveItem" in submission:
        if not all(key in submission["mostExpensiveItem"] for key in ["productCode", "unitCost"]):
            json_format_score -= 2
    
    # Check if updatedRecords has the correct structure
    if "updatedRecords" in submission:
        for record in submission["updatedRecords"]:
            if not all(key in record for key in ["productCode", "quantity", "unitCost", "totalValue", "status"]):
                json_format_score -= 2
                break
    
    results["points_earned"] += json_format_score
    results["details"]["json_formatting"] = {
        "earned": json_format_score,
        "max": 6,
        "comment": "JSON formatting evaluation"
    }
    
    return results

def evaluate_exercise2(submission, answer_key):
    """Evaluate Exercise 2 (35 points total)."""
    results = {
        "points_earned": 0,
        "max_points": 35,
        "details": {}
    }
    
    # Check delivery status identification (8 points)
    delivery_status_errors = 0
    
    # Create a mapping of PO numbers to expected delivery status
    status_map = {}
    for record in answer_key["exercise2"]["orderAnalysis"]:
        status_map[record["poNumber"]] = record["deliveryStatus"]
    
    for sub_record in submission["exercise2"]["orderAnalysis"]:
        po_number = sub_record["poNumber"]
        if po_number in status_map:
            if sub_record["deliveryStatus"] != status_map[po_number]:
                delivery_status_errors += 1
    
    delivery_status_score = 8 - min(delivery_status_errors, 8)
    results["points_earned"] += delivery_status_score
    results["details"]["delivery_status_identification"] = {
        "earned": delivery_status_score,
        "max": 8,
        "comment": f"{delivery_status_errors} errors in delivery status identification"
    }
    
    # Check delivery days calculation (7 points)
    delivery_days_errors = 0
    
    # Create a mapping of PO numbers to expected delivery days
    days_map = {}
    for record in answer_key["exercise2"]["orderAnalysis"]:
        days_map[record["poNumber"]] = record["deliveryDays"]
    
    for sub_record in submission["exercise2"]["orderAnalysis"]:
        po_number = sub_record["poNumber"]
        if po_number in days_map:
            if sub_record["deliveryDays"] != days_map[po_number]:
                delivery_days_errors += 1
    
    delivery_days_score = 7 - min(delivery_days_errors, 7)
    results["points_earned"] += delivery_days_score
    results["details"]["delivery_days_calculation"] = {
        "earned": delivery_days_score,
        "max": 7,
        "comment": f"{delivery_days_errors} errors in delivery days calculation"
    }
    
    # Check price variance calculation (7 points)
    price_variance_errors = 0
    
    # Create a mapping of PO numbers to expected price variance
    variance_map = {}
    for record in answer_key["exercise2"]["orderAnalysis"]:
        variance_map[record["poNumber"]] = record["priceVariance"]
    
    for sub_record in submission["exercise2"]["orderAnalysis"]:
        po_number = sub_record["poNumber"]
        if po_number in variance_map:
            if not within_tolerance(sub_record["priceVariance"], variance_map[po_number], 0.02):
                price_variance_errors += 1
    
    price_variance_score = 7 - min(price_variance_errors, 7)
    results["points_earned"] += price_variance_score
    results["details"]["price_variance_calculation"] = {
        "earned": price_variance_score,
        "max": 7,
        "comment": f"{price_variance_errors} errors in price variance calculation"
    }
    
    # Check summary statistics (8 points)
    summary_points = 0
    
    # Total orders (2 points)
    if submission["exercise2"]["totalOrders"] == answer_key["exercise2"]["totalOrders"]:
        summary_points += 2
        results["details"]["total_orders"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct total orders count"
        }
    else:
        results["details"]["total_orders"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect total orders: got {submission['exercise2']['totalOrders']}, expected {answer_key['exercise2']['totalOrders']}"
        }
    
    # Late delivery percentage (2 points)
    if within_tolerance(submission["exercise2"]["lateDeliveryPercentage"], 
                        answer_key["exercise2"]["lateDeliveryPercentage"], 0.1):
        summary_points += 2
        results["details"]["late_delivery_percentage"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct late delivery percentage"
        }
    else:
        results["details"]["late_delivery_percentage"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect late delivery percentage: got {submission['exercise2']['lateDeliveryPercentage']}, expected {answer_key['exercise2']['lateDeliveryPercentage']}"
        }
    
    # Fastest supplier (2 points)
    if (submission["exercise2"]["fastestSupplier"]["supplierName"] == 
        answer_key["exercise2"]["fastestSupplier"]["supplierName"] and
        within_tolerance(submission["exercise2"]["fastestSupplier"]["avgDeliveryDays"],
                         answer_key["exercise2"]["fastestSupplier"]["avgDeliveryDays"], 0.1)):
        summary_points += 2
        results["details"]["fastest_supplier"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correctly identified fastest supplier"
        }
    else:
        results["details"]["fastest_supplier"] = {
            "earned": 0,
            "max": 2,
            "comment": "Incorrectly identified fastest supplier"
        }
    
    # Total price variance (2 points)
    if within_tolerance(submission["exercise2"]["totalPriceVariance"], 
                        answer_key["exercise2"]["totalPriceVariance"], 0.02):
        summary_points += 2
        results["details"]["total_price_variance"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct total price variance"
        }
    else:
        results["details"]["total_price_variance"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect total price variance: got {submission['exercise2']['totalPriceVariance']}, expected {answer_key['exercise2']['totalPriceVariance']}"
        }
    
    results["points_earned"] += summary_points
    
    # Check JSON formatting (5 points)
    json_format_score = 5  # Assume correct format initially
    
    # Check if all required fields are present
    required_fields = ["totalOrders", "lateDeliveryPercentage", "fastestSupplier", "totalPriceVariance", "orderAnalysis"]
    for field in required_fields:
        if field not in submission["exercise2"]:
            json_format_score -= 2
            break
    
    # Check if fastestSupplier has the correct structure
    if "fastestSupplier" in submission["exercise2"]:
        if not all(key in submission["exercise2"]["fastestSupplier"] for key in ["supplierName", "avgDeliveryDays"]):
            json_format_score -= 1
    
    # Check if orderAnalysis has the correct structure
    if "orderAnalysis" in submission["exercise2"]:
        for record in submission["exercise2"]["orderAnalysis"]:
            if not all(key in record for key in ["poNumber", "deliveryStatus", "deliveryDays", "priceVariance"]):
                json_format_score -= 2
                break
    
    results["points_earned"] += json_format_score
    results["details"]["json_formatting"] = {
        "earned": json_format_score,
        "max": 5,
        "comment": "JSON formatting evaluation"
    }
    
    return results

def evaluate_exercise3(submission, answer_key):
    """Evaluate Exercise 3 (30 points total)."""
    results = {
        "points_earned": 0,
        "max_points": 30,
        "details": {}
    }
    
    # Check defect rate calculations (8 points)
    # For this, we'll check if the highest and lowest defect rates are correctly identified
    defect_rate_points = 8  # Start with full points
    
    # Check lowest defect product
    valid_lowest_defect_products = ["AB-1002", "MN-6789", "UV-5566"]  # Any of these is acceptable
    if submission["exercise3"]["lowestDefectProduct"]["productCode"] not in valid_lowest_defect_products:
        defect_rate_points -= 4
        results["details"]["lowest_defect_product"] = {
            "earned": 0,
            "max": 4,
            "comment": f"Incorrect lowest defect product: got {submission['exercise3']['lowestDefectProduct']['productCode']}, expected one of {valid_lowest_defect_products}"
        }
    else:
        results["details"]["lowest_defect_product"] = {
            "earned": 4,
            "max": 4,
            "comment": "Correctly identified lowest defect product"
        }
    
    # Check highest defect product
    if submission["exercise3"]["highestDefectProduct"]["productCode"] != answer_key["exercise3"]["highestDefectProduct"]["productCode"]:
        defect_rate_points -= 4
        results["details"]["highest_defect_product"] = {
            "earned": 0,
            "max": 4,
            "comment": f"Incorrect highest defect product: got {submission['exercise3']['highestDefectProduct']['productCode']}, expected {answer_key['exercise3']['highestDefectProduct']['productCode']}"
        }
    else:
        results["details"]["highest_defect_product"] = {
            "earned": 4,
            "max": 4,
            "comment": "Correctly identified highest defect product"
        }
    
    results["points_earned"] += defect_rate_points
    
    # Check identification of quality review products (7 points)
    # Create a set of product codes that should be in quality review
    expected_review_products = set()
    for product in answer_key["exercise3"]["qualityReviewProducts"]:
        expected_review_products.add(product["productCode"])
    
    # Create a set of product codes that the candidate identified for quality review
    submitted_review_products = set()
    for product in submission["exercise3"]["qualityReviewProducts"]:
        submitted_review_products.add(product["productCode"])
    
    # Calculate false positives and false negatives
    false_positives = submitted_review_products - expected_review_products
    false_negatives = expected_review_products - submitted_review_products
    
    quality_review_errors = len(false_positives) + len(false_negatives)
    quality_review_score = 7 - min(quality_review_errors, 7)
    
    results["points_earned"] += quality_review_score
    results["details"]["quality_review_identification"] = {
        "earned": quality_review_score,
        "max": 7,
        "comment": f"{quality_review_errors} errors in quality review product identification"
    }
    
    # Check summary statistics (10 points)
    summary_points = 0
    
    # Lowest defect rate (2 points)
    if within_tolerance(submission["exercise3"]["lowestDefectProduct"]["defectRate"], 0.00, 0.001):
        summary_points += 2
        results["details"]["lowest_defect_rate"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct lowest defect rate"
        }
    else:
        results["details"]["lowest_defect_rate"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect lowest defect rate: got {submission['exercise3']['lowestDefectProduct']['defectRate']}, expected 0.00"
        }
    
    # Highest defect rate (3 points)
    if within_tolerance(submission["exercise3"]["highestDefectProduct"]["defectRate"], 
                        answer_key["exercise3"]["highestDefectProduct"]["defectRate"], 0.01):
        summary_points += 3
        results["details"]["highest_defect_rate"] = {
            "earned": 3,
            "max": 3,
            "comment": "Correct highest defect rate"
        }
    else:
        results["details"]["highest_defect_rate"] = {
            "earned": 0,
            "max": 3,
            "comment": f"Incorrect highest defect rate: got {submission['exercise3']['highestDefectProduct']['defectRate']}, expected {answer_key['exercise3']['highestDefectProduct']['defectRate']}"
        }
    
    # Average supplier quality (3 points)
    if within_tolerance(submission["exercise3"]["avgSupplierQuality"], 
                        answer_key["exercise3"]["avgSupplierQuality"], 0.1):
        summary_points += 3
        results["details"]["avg_supplier_quality"] = {
            "earned": 3,
            "max": 3,
            "comment": "Correct average supplier quality"
        }
    else:
        results["details"]["avg_supplier_quality"] = {
            "earned": 0,
            "max": 3,
            "comment": f"Incorrect average supplier quality: got {submission['exercise3']['avgSupplierQuality']}, expected {answer_key['exercise3']['avgSupplierQuality']}"
        }
    
    # Quality review products count (2 points)
    if len(submission["exercise3"]["qualityReviewProducts"]) == len(answer_key["exercise3"]["qualityReviewProducts"]):
        summary_points += 2
        results["details"]["quality_review_count"] = {
            "earned": 2,
            "max": 2,
            "comment": "Correct number of quality review products"
        }
    else:
        results["details"]["quality_review_count"] = {
            "earned": 0,
            "max": 2,
            "comment": f"Incorrect number of quality review products: got {len(submission['exercise3']['qualityReviewProducts'])}, expected {len(answer_key['exercise3']['qualityReviewProducts'])}"
        }
    
    results["points_earned"] += summary_points
    
    # Check JSON formatting (5 points)
    json_format_score = 5  # Assume correct format initially
    
    # Check if all required fields are present
    required_fields = ["lowestDefectProduct", "highestDefectProduct", "avgSupplierQuality", "qualityReviewProducts"]
    for field in required_fields:
        if field not in submission["exercise3"]:
            json_format_score -= 2
            break
    
    # Check if defect products have the correct structure
    for field in ["lowestDefectProduct", "highestDefectProduct"]:
        if field in submission["exercise3"]:
            if not all(key in submission["exercise3"][field] for key in ["productCode", "defectRate"]):
                json_format_score -= 1
    
    # Check if qualityReviewProducts has the correct structure
    if "qualityReviewProducts" in submission["exercise3"]:
        for product in submission["exercise3"]["qualityReviewProducts"]:
            if not all(key in product for key in ["productCode", "defectRate", "supplier"]):
                json_format_score -= 2
                break
    
    results["points_earned"] += json_format_score
    results["details"]["json_formatting"] = {
        "earned": json_format_score,
        "max": 5,
        "comment": "JSON formatting evaluation"
    }
    
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the entire submission."""
    results = {
        "overall_score": 0,
        "passing_threshold": 70,
        "exercise_results": {}
    }
    
    # Evaluate each exercise
    results["exercise_results"]["exercise1"] = evaluate_exercise1(submission, answer_key)
    results["exercise_results"]["exercise2"] = evaluate_exercise2(submission, answer_key)
    results["exercise_results"]["exercise3"] = evaluate_exercise3(submission, answer_key)
    
    # Calculate total points and overall score
    total_points_earned = (
        results["exercise_results"]["exercise1"]["points_earned"] +
        results["exercise_results"]["exercise2"]["points_earned"] +
        results["exercise_results"]["exercise3"]["points_earned"]
    )
    
    total_points_possible = (
        results["exercise_results"]["exercise1"]["max_points"] +
        results["exercise_results"]["exercise2"]["max_points"] +
        results["exercise_results"]["exercise3"]["max_points"]
    )
    
    results["overall_score"] = round((total_points_earned / total_points_possible) * 100, 2)
    
    # Determine if the candidate passed
    exercise1_percent = (results["exercise_results"]["exercise1"]["points_earned"] / 
                         results["exercise_results"]["exercise1"]["max_points"]) * 100
    exercise2_percent = (results["exercise_results"]["exercise2"]["points_earned"] / 
                         results["exercise_results"]["exercise2"]["max_points"]) * 100
    exercise3_percent = (results["exercise_results"]["exercise3"]["points_earned"] / 
                         results["exercise_results"]["exercise3"]["max_points"]) * 100
    
    passed_exercise1 = exercise1_percent >= 60
    passed_exercise2 = exercise2_percent >= 60
    passed_exercise3 = exercise3_percent >= 60
    passed_overall = results["overall_score"] >= 70
    
    results["passed"] = passed_exercise1 and passed_exercise2 and passed_exercise3 and passed_overall
    
    results["exercise_percentages"] = {
        "exercise1": round(exercise1_percent, 2),
        "exercise2": round(exercise2_percent, 2),
        "exercise3": round(exercise3_percent, 2)
    }
    
    results["passing_criteria"] = {
        "overall_threshold": 70,
        "exercise_threshold": 60,
        "exercise1_passed": passed_exercise1,
        "exercise2_passed": passed_exercise2,
        "exercise3_passed": passed_exercise3,
        "overall_passed": passed_overall
    }
    
    return results

def main():
    # Load the submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files.")
        return
    
    # Evaluate the submission
    results = evaluate_submission(submission, answer_key)
    
    # Save the results
    save_json(results, "test_results.json")

if __name__ == "__main__":
    main()