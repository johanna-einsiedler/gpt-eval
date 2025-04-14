import json
import sys
import math

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def calculate_percentage_difference(candidate_value, key_value):
    """Calculate the percentage difference between two values."""
    if key_value == 0:
        return float('inf') if candidate_value != 0 else 0
    return abs(candidate_value - key_value) / key_value

def evaluate_initial_markup(candidate_data, key_data):
    """Evaluate the initial markup section (30 points total)."""
    results = {"points": 0, "max_points": 30, "details": {}}
    
    # 6 points per product (5 products)
    # 3 points for markup percentage, 3 points for retail price
    points_per_product = 6
    
    for product_id in key_data:
        product_results = {"points": 0, "max_points": points_per_product, "details": {}}
        
        # Check if product exists in candidate submission
        if product_id not in candidate_data:
            product_results["details"]["error"] = f"Missing product {product_id}"
            results["details"][product_id] = product_results
            continue
            
        # Evaluate markup percentage (3 points)
        key_markup = key_data[product_id]["markup_percentage"]
        candidate_markup = candidate_data[product_id]["markup_percentage"]
        markup_diff = calculate_percentage_difference(candidate_markup, key_markup)
        
        if markup_diff == 0:
            product_results["points"] += 3
            product_results["details"]["markup_percentage"] = "Correct"
        elif markup_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.5
            product_results["details"]["markup_percentage"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["markup_percentage"] = "Incorrect"
            
        # Evaluate retail price (3 points)
        key_price = key_data[product_id]["retail_price"]
        candidate_price = candidate_data[product_id]["retail_price"]
        price_diff = calculate_percentage_difference(candidate_price, key_price)
        
        if price_diff == 0:
            product_results["points"] += 3
            product_results["details"]["retail_price"] = "Correct"
        elif price_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.5
            product_results["details"]["retail_price"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["retail_price"] = "Incorrect"
            
        results["points"] += product_results["points"]
        results["details"][product_id] = product_results
        
    return results

def evaluate_seasonal_markdown(candidate_data, key_data):
    """Evaluate the seasonal markdown section (30 points total)."""
    results = {"points": 0, "max_points": 30, "details": {}}
    
    # 7.5 points per product (4 products)
    # 2.5 points for markdown percentage, 2.5 for new price, 2.5 for second markdown
    points_per_product = 7.5
    
    for product_id in key_data:
        product_results = {"points": 0, "max_points": points_per_product, "details": {}}
        
        # Check if product exists in candidate submission
        if product_id not in candidate_data:
            product_results["details"]["error"] = f"Missing product {product_id}"
            results["details"][product_id] = product_results
            continue
            
        # Evaluate markdown percentage (2.5 points)
        key_markdown = key_data[product_id]["markdown_percentage"]
        candidate_markdown = candidate_data[product_id]["markdown_percentage"]
        markdown_diff = calculate_percentage_difference(candidate_markdown, key_markdown)
        
        if markdown_diff == 0:
            product_results["points"] += 2.5
            product_results["details"]["markdown_percentage"] = "Correct"
        elif markdown_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.25
            product_results["details"]["markdown_percentage"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["markdown_percentage"] = "Incorrect"
            
        # Evaluate new price (2.5 points)
        key_price = key_data[product_id]["new_price"]
        candidate_price = candidate_data[product_id]["new_price"]
        price_diff = calculate_percentage_difference(candidate_price, key_price)
        
        if price_diff == 0:
            product_results["points"] += 2.5
            product_results["details"]["new_price"] = "Correct"
        elif price_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.25
            product_results["details"]["new_price"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["new_price"] = "Incorrect"
            
        # Evaluate second markdown (2.5 points)
        key_second = key_data[product_id]["second_markdown"]
        candidate_second = candidate_data[product_id]["second_markdown"]
        second_diff = calculate_percentage_difference(candidate_second, key_second)
        
        if second_diff == 0:
            product_results["points"] += 2.5
            product_results["details"]["second_markdown"] = "Correct"
        elif second_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.25
            product_results["details"]["second_markdown"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["second_markdown"] = "Incorrect"
            
        results["points"] += product_results["points"]
        results["details"][product_id] = product_results
        
    return results

def evaluate_promotional_pricing(candidate_data, key_data):
    """Evaluate the promotional pricing section (20 points total)."""
    results = {"points": 0, "max_points": 20, "details": {}}
    
    # 6.67 points per product (3 products)
    # 3.33 points for discount percentage, 3.33 for breakeven volume increase
    points_per_product = 6.67
    
    for product_id in key_data:
        product_results = {"points": 0, "max_points": points_per_product, "details": {}}
        
        # Check if product exists in candidate submission
        if product_id not in candidate_data:
            product_results["details"]["error"] = f"Missing product {product_id}"
            results["details"][product_id] = product_results
            continue
            
        # Evaluate discount percentage (3.33 points)
        key_discount = key_data[product_id]["discount_percentage"]
        candidate_discount = candidate_data[product_id]["discount_percentage"]
        
        if candidate_discount == key_discount:
            product_results["points"] += 3.33
            product_results["details"]["discount_percentage"] = "Correct"
        else:
            product_results["details"]["discount_percentage"] = "Incorrect"
            
        # Evaluate breakeven volume increase (3.33 points)
        key_breakeven = key_data[product_id]["breakeven_volume_increase"]
        candidate_breakeven = candidate_data[product_id]["breakeven_volume_increase"]
        breakeven_diff = calculate_percentage_difference(candidate_breakeven, key_breakeven)
        
        if breakeven_diff == 0:
            product_results["points"] += 3.33
            product_results["details"]["breakeven_volume_increase"] = "Correct"
        elif breakeven_diff <= 0.05:  # Within 5%
            product_results["points"] += 1.665
            product_results["details"]["breakeven_volume_increase"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["breakeven_volume_increase"] = "Incorrect"
            
        results["points"] += product_results["points"]
        results["details"][product_id] = product_results
        
    return results

def evaluate_competitive_repricing(candidate_data, key_data):
    """Evaluate the competitive repricing section (20 points total)."""
    results = {"points": 0, "max_points": 20, "details": {}}
    
    # 6.67 points per product (3 products)
    points_per_product = 6.67
    
    for product_id in key_data:
        product_results = {"points": 0, "max_points": points_per_product, "details": {}}
        
        # Check if product exists in candidate submission
        if product_id not in candidate_data:
            product_results["details"]["error"] = f"Missing product {product_id}"
            results["details"][product_id] = product_results
            continue
            
        # Evaluate new price (6.67 points)
        key_price = key_data[product_id]["new_price"]
        candidate_price = candidate_data[product_id]["new_price"]
        price_diff = calculate_percentage_difference(candidate_price, key_price)
        
        if price_diff == 0:
            product_results["points"] += 6.67
            product_results["details"]["new_price"] = "Correct"
        elif price_diff <= 0.05:  # Within 5%
            product_results["points"] += 3.335
            product_results["details"]["new_price"] = "Partial credit (within 5%)"
        else:
            product_results["details"]["new_price"] = "Incorrect"
            
        results["points"] += product_results["points"]
        results["details"][product_id] = product_results
        
    return results

def evaluate_submission(candidate_file, key_file):
    """Evaluate the full submission against the answer key."""
    candidate_data = load_json_file(candidate_file)
    key_data = load_json_file(key_file)
    
    results = {
        "candidate_id": candidate_data.get("candidate_id", "Unknown"),
        "overall_score": 0,
        "total_points": 0,
        "max_points": 100,
        "sections": {}
    }
    
    # Evaluate each section
    results["sections"]["initial_markup"] = evaluate_initial_markup(
        candidate_data.get("initial_markup", {}), 
        key_data.get("initial_markup", {})
    )
    
    results["sections"]["seasonal_markdown"] = evaluate_seasonal_markdown(
        candidate_data.get("seasonal_markdown", {}), 
        key_data.get("seasonal_markdown", {})
    )
    
    results["sections"]["promotional_pricing"] = evaluate_promotional_pricing(
        candidate_data.get("promotional_pricing", {}), 
        key_data.get("promotional_pricing", {})
    )
    
    results["sections"]["competitive_repricing"] = evaluate_competitive_repricing(
        candidate_data.get("competitive_repricing", {}), 
        key_data.get("competitive_repricing", {})
    )
    
    # Calculate total points
    for section in results["sections"].values():
        results["total_points"] += section["points"]
    
    # Calculate overall score as a percentage
    results["overall_score"] = round((results["total_points"] / results["max_points"]) * 100, 2)
    
    return results

def main():
    """Main function to run the evaluation script."""
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
        
    candidate_file = sys.argv[1]
    key_file = sys.argv[2]
    
    # Evaluate submission
    results = evaluate_submission(candidate_file, key_file)
    
    # Save results to file
    with open("test_results.json", "w") as file:
        json.dump(results, file, indent=2)
        
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")

if __name__ == "__main__":
    main()