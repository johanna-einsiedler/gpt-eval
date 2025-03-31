import json
import math

def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def evaluate_exercise1(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 25,
        "details": {
            "imu_calculation": {"score": 0, "max_score": 5, "comments": []},
            "mmu_calculation": {"score": 0, "max_score": 5, "comments": []},
            "target_margins": {"score": 0, "max_score": 5, "comments": []},
            "competitive_positioning": {"score": 0, "max_score": 5, "comments": []},
            "justification_quality": {"score": 0, "max_score": 5, "comments": []}
        }
    }
    
    # Extract product data
    sub_products = {p["product_id"]: p for p in submission["exercise1"]["product_markup_rates"]}
    key_products = {p["product_id"]: p for p in answer_key["exercise1"]["product_markup_rates"]}
    
    # Check IMU calculation
    imu_correct = 0
    for product_id, key_product in key_products.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            # Allow for small differences due to rounding
            if abs(sub_product["initial_markup"] - key_product["initial_markup"]) <= 2:
                imu_correct += 1
            else:
                results["details"]["imu_calculation"]["comments"].append(
                    f"{product_id}: Expected IMU around {key_product['initial_markup']}%, got {sub_product['initial_markup']}%"
                )
    
    results["details"]["imu_calculation"]["score"] = round(5 * (imu_correct / len(key_products)))
    
    # Check MMU calculation
    mmu_correct = 0
    for product_id, key_product in key_products.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            # Allow for small differences due to rounding
            if abs(sub_product["maintained_markup"] - key_product["maintained_markup"]) <= 5:
                mmu_correct += 1
            else:
                results["details"]["mmu_calculation"]["comments"].append(
                    f"{product_id}: Expected MMU around {key_product['maintained_markup']}%, got {sub_product['maintained_markup']}%"
                )
    
    results["details"]["mmu_calculation"]["score"] = round(5 * (mmu_correct / len(key_products)))
    
    # Check target margins (based on recommended markup rates)
    margins_correct = 0
    target_margins = {
        "KA001": 40,
        "KA002": 35,
        "KA003": 42,
        "KA004": 38,
        "KA005": 45
    }
    
    for product_id, target in target_margins.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            # IMU should be at least the target margin
            if sub_product["recommended_markup_rate"] >= target:
                margins_correct += 1
            else:
                results["details"]["target_margins"]["comments"].append(
                    f"{product_id}: Recommended markup {sub_product['recommended_markup_rate']}% doesn't meet target margin of {target}%"
                )
    
    results["details"]["target_margins"]["score"] = round(5 * (margins_correct / len(target_margins)))
    
    # Check competitive positioning
    positioning_score = 0
    industry_averages = {
        "KA001": 45,
        "KA002": 40,
        "KA003": 50,
        "KA004": 42,
        "KA005": 48
    }
    
    for product_id, avg in industry_averages.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            # Check if markup is within 5% of industry average or justified
            if abs(sub_product["recommended_markup_rate"] - avg) <= 5:
                positioning_score += 1
            elif len(sub_product["justification"]) > 50:  # Assume justified if explanation is substantial
                positioning_score += 0.5
                results["details"]["competitive_positioning"]["comments"].append(
                    f"{product_id}: Markup deviates from industry average but may be justified"
                )
            else:
                results["details"]["competitive_positioning"]["comments"].append(
                    f"{product_id}: Markup {sub_product['recommended_markup_rate']}% deviates from industry average {avg}%"
                )
    
    results["details"]["competitive_positioning"]["score"] = round(5 * (positioning_score / len(industry_averages)))
    
    # Evaluate justification quality
    justification_score = 0
    for product_id in key_products:
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            justification = sub_product["justification"]
            
            # Basic scoring based on length and content
            if len(justification) >= 50:
                points = 0.5
                
                # Check for key terms that should be in justifications
                key_terms = ["margin", "competitor", "position", "markup", "industry"]
                for term in key_terms:
                    if term.lower() in justification.lower():
                        points += 0.1
                
                justification_score += min(points, 1.0)
            else:
                results["details"]["justification_quality"]["comments"].append(
                    f"{product_id}: Justification too brief"
                )
    
    results["details"]["justification_quality"]["score"] = round(5 * (justification_score / len(key_products)))
    
    # Calculate total score for Exercise 1
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_exercise2(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 25,
        "details": {
            "progressive_schedule": {"score": 0, "max_score": 5, "comments": []},
            "projected_units": {"score": 0, "max_score": 5, "comments": []},
            "projected_revenue": {"score": 0, "max_score": 5, "comments": []},
            "special_events": {"score": 0, "max_score": 5, "comments": []},
            "strategy_explanation": {"score": 0, "max_score": 5, "comments": []}
        }
    }
    
    sub_schedule = submission["exercise2"]["markdown_schedule"]
    key_schedule = answer_key["exercise2"]["markdown_schedule"]
    
    # Check progressive markdown schedule
    is_progressive = True
    prev_markdown = 0
    for week in sub_schedule:
        if week["markdown_percentage"] < prev_markdown:
            is_progressive = False
            results["details"]["progressive_schedule"]["comments"].append(
                f"Week {week['week']}: Markdown decreased from {prev_markdown}% to {week['markdown_percentage']}%"
            )
        prev_markdown = week["markdown_percentage"]
    
    # Check if markdowns are within acceptable ranges (15-75%)
    all_in_range = all(15 <= week["markdown_percentage"] <= 75 for week in sub_schedule)
    
    if is_progressive and all_in_range:
        results["details"]["progressive_schedule"]["score"] = 5
    elif is_progressive:
        results["details"]["progressive_schedule"]["score"] = 3
        results["details"]["progressive_schedule"]["comments"].append("Some markdowns outside acceptable range (15-75%)")
    elif all_in_range:
        results["details"]["progressive_schedule"]["score"] = 2
        results["details"]["progressive_schedule"]["comments"].append("Markdowns not consistently progressive")
    else:
        results["details"]["progressive_schedule"]["score"] = 1
        results["details"]["progressive_schedule"]["comments"].append("Markdowns neither progressive nor in acceptable range")
    
    # Check projected units calculation
    units_score = 0
    for i, (sub_week, key_week) in enumerate(zip(sub_schedule, key_schedule)):
        # Allow for differences up to 20% due to different calculation methods
        expected_units = key_week["projected_units_sold"]
        submitted_units = sub_week["projected_units_sold"]
        
        if abs(submitted_units - expected_units) <= 0.2 * expected_units:
            units_score += 1
        else:
            results["details"]["projected_units"]["comments"].append(
                f"Week {i+1}: Expected around {expected_units} units, got {submitted_units}"
            )
    
    results["details"]["projected_units"]["score"] = round(5 * (units_score / len(key_schedule)))
    
    # Check projected revenue calculation
    revenue_score = 0
    for i, (sub_week, key_week) in enumerate(zip(sub_schedule, key_schedule)):
        # Allow for differences up to 20% due to different calculation methods
        expected_revenue = key_week["projected_revenue"]
        submitted_revenue = sub_week["projected_revenue"]
        
        if abs(submitted_revenue - expected_revenue) <= 0.2 * expected_revenue:
            revenue_score += 1
        else:
            results["details"]["projected_revenue"]["comments"].append(
                f"Week {i+1}: Expected around ${expected_revenue}, got ${submitted_revenue}"
            )
    
    results["details"]["projected_revenue"]["score"] = round(5 * (revenue_score / len(key_schedule)))
    
    # Check consideration of special events (Labor Day)
    labor_day_week = 5  # Week 5 is Labor Day weekend
    labor_day_considered = False
    
    # Check if Labor Day week has appropriate markdown
    if sub_schedule[labor_day_week-1]["markdown_percentage"] >= 50:
        labor_day_considered = True
    
    # Check if strategy explanation mentions Labor Day
    if "labor day" in submission["exercise2"]["strategy_explanation"].lower():
        labor_day_considered = True
    
    if labor_day_considered:
        results["details"]["special_events"]["score"] = 5
    else:
        results["details"]["special_events"]["score"] = 2
        results["details"]["special_events"]["comments"].append("No clear consideration of Labor Day weekend")
    
    # Evaluate strategy explanation
    strategy = submission["exercise2"]["strategy_explanation"]
    
    if len(strategy) >= 100:
        strategy_score = 3
        
        # Check for key terms that should be in the strategy
        key_terms = ["markdown", "inventory", "revenue", "sales", "clearance", "deadline"]
        for term in key_terms:
            if term.lower() in strategy.lower():
                strategy_score += 0.5
        
        results["details"]["strategy_explanation"]["score"] = min(strategy_score, 5)
    else:
        results["details"]["strategy_explanation"]["score"] = 2
        results["details"]["strategy_explanation"]["comments"].append("Strategy explanation too brief")
    
    # Calculate total score for Exercise 2
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_exercise3(submission, answer_key):
    results = {
        "score": 0,
        "max_score": 25,
        "details": {
            "minimum_markup": {"score": 0, "max_score": 5, "comments": []},
            "implied_markup_calculation": {"score": 0, "max_score": 5, "comments": []},
            "competitor_positioning": {"score": 0, "max_score": 5, "comments": []},
            "price_sensitivity": {"score": 0, "max_score": 5, "comments": []},
            "positioning_strategy": {"score": 0, "max_score": 5, "comments": []}
        }
    }
    
    # Extract product data
    sub_products = {p["product_id"]: p for p in submission["exercise3"]["product_pricing"]}
    key_products = {p["product_id"]: p for p in answer_key["exercise3"]["product_pricing"]}
    
    # Minimum required markups
    min_markups = {
        "E001": 35,
        "E002": 30,
        "E003": 40,
        "E004": 25,
        "E005": 45
    }
    
    # Check minimum markup requirements
    markup_met = 0
    for product_id, min_markup in min_markups.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            if sub_product["implied_markup_rate"] >= min_markup:
                markup_met += 1
            else:
                results["details"]["minimum_markup"]["comments"].append(
                    f"{product_id}: Markup {sub_product['implied_markup_rate']}% below minimum requirement of {min_markup}%"
                )
    
    results["details"]["minimum_markup"]["score"] = round(5 * (markup_met / len(min_markups)))
    
    # Check implied markup calculation
    markup_calc_correct = 0
    for product_id, key_product in key_products.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            
            # Calculate expected markup based on submitted price
            wholesale_cost = sub_product["wholesale_cost"]
            recommended_price = sub_product["recommended_price"]
            expected_markup = ((recommended_price - wholesale_cost) / wholesale_cost) * 100
            
            # Allow for small differences due to rounding
            if abs(sub_product["implied_markup_rate"] - expected_markup) <= 1:
                markup_calc_correct += 1
            else:
                results["details"]["implied_markup_calculation"]["comments"].append(
                    f"{product_id}: Expected implied markup {expected_markup:.1f}%, got {sub_product['implied_markup_rate']}%"
                )
    
    results["details"]["implied_markup_calculation"]["score"] = round(5 * (markup_calc_correct / len(key_products)))
    
    # Check competitor positioning
    competitor_prices = {
        "E001": {"budget": 59.99, "mid": 89.99, "premium": 149.99},
        "E002": {"budget": 49.99, "mid": 79.99, "premium": 129.99},
        "E003": {"budget": 79.99, "mid": 119.99, "premium": 199.99},
        "E004": {"budget": 34.99, "mid": 49.99, "premium": 69.99},
        "E005": {"budget": 99.99, "mid": 159.99, "premium": 249.99}
    }
    
    positioning_correct = 0
    for product_id, prices in competitor_prices.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            price = sub_product["recommended_price"]
            
            # Check if price is between budget and premium
            if prices["budget"] <= price <= prices["premium"]:
                positioning_correct += 1
            else:
                results["details"]["competitor_positioning"]["comments"].append(
                    f"{product_id}: Price ${price} outside competitive range (${prices['budget']}-${prices['premium']})"
                )
    
    results["details"]["competitor_positioning"]["score"] = round(5 * (positioning_correct / len(competitor_prices)))
    
    # Check price sensitivity consideration
    sensitivity_ratings = {
        "E001": 7,  # Wireless Headphones
        "E002": 8,  # Bluetooth Speaker
        "E003": 6,  # Fitness Tracker
        "E004": 9,  # Power Bank
        "E005": 5   # Smart Watch
    }
    
    # Expected relationship: higher sensitivity should correlate with more competitive pricing
    sensitivity_considered = 0
    for product_id, sensitivity in sensitivity_ratings.items():
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            prices = competitor_prices[product_id]
            price = sub_product["recommended_price"]
            
            # For high sensitivity (8-9), price should be closer to budget
            # For medium sensitivity (6-7), price should be mid-range
            # For low sensitivity (5), price can be higher
            
            if sensitivity >= 8 and price <= (prices["budget"] + prices["mid"]) / 2:
                sensitivity_considered += 1
            elif 6 <= sensitivity <= 7 and prices["budget"] < price < prices["premium"]:
                sensitivity_considered += 1
            elif sensitivity <= 5 and price >= (prices["mid"] + prices["budget"]) / 2:
                sensitivity_considered += 1
            elif "sensitivity" in sub_product["positioning_strategy"].lower():
                # If they mention sensitivity in their strategy, give partial credit
                sensitivity_considered += 0.5
                results["details"]["price_sensitivity"]["comments"].append(
                    f"{product_id}: Price may not fully reflect sensitivity rating of {sensitivity}/10"
                )
            else:
                results["details"]["price_sensitivity"]["comments"].append(
                    f"{product_id}: Price doesn't appear to consider sensitivity rating of {sensitivity}/10"
                )
    
    results["details"]["price_sensitivity"]["score"] = round(5 * (sensitivity_considered / len(sensitivity_ratings)))
    
    # Evaluate positioning strategy quality
    strategy_score = 0
    for product_id in key_products:
        if product_id in sub_products:
            sub_product = sub_products[product_id]
            strategy = sub_product["positioning_strategy"]
            
            # Basic scoring based on length and content
            if len(strategy) >= 30:
                points = 0.5
                
                # Check for key terms that should be in strategies
                key_terms = ["position", "price", "competitor", "quality", "value", "market"]
                for term in key_terms:
                    if term.lower() in strategy.lower():
                        points += 0.1
                
                strategy_score += min(points, 1.0)
            else:
                results["details"]["positioning_strategy"]["comments"].append(
                    f"{product_id}: Positioning strategy too brief"
                )
    
    results["details"]["positioning_strategy"]["score"] = round(5 * (strategy_score / len(key_products)))
    
    # Calculate total score for Exercise 3
    results["score"] = sum(detail["score"] for detail in results["details"].values())
    
    return results

def evaluate_submission(submission, answer_key):
    results = {
        "candidate_id": submission.get("candidate_id", "Unknown"),
        "exercise1_results": evaluate_exercise1(submission, answer_key),
        "exercise2_results": evaluate_exercise2(submission, answer_key),
        "exercise3_results": evaluate_exercise3(submission, answer_key),
        "overall_score": 0
    }
    
    # Calculate overall score as percentage
    total_score = (
        results["exercise1_results"]["score"] +
        results["exercise2_results"]["score"] +
        results["exercise3_results"]["score"]
    )
    
    total_possible = (
        results["exercise1_results"]["max_score"] +
        results["exercise2_results"]["max_score"] +
        results["exercise3_results"]["max_score"]
    )
    
    results["overall_score"] = round((total_score / total_possible) * 100, 1)
    
    # Add pass/fail status based on criteria (45/75 points or 60%)
    results["passed"] = results["overall_score"] >= 60
    
    return results

def main():
    # Load submission and answer key
    submission = load_json("test_submission.json")
    answer_key = load_json("answer_key.json")
    
    if not submission or not answer_key:
        print("Error: Could not load required files")
        return
    
    # Evaluate submission
    results = evaluate_submission(submission, answer_key)
    
    # Save results
    save_json(results, "test_results.json")

if __name__ == "__main__":
    main()