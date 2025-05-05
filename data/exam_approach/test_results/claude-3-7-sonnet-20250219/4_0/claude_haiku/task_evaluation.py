#!/usr/bin/env python3
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

def evaluate_product_margins(submission, answer_key):
    """Evaluate the product margins calculation."""
    results = {"score": 0, "max_score": 10, "details": {}}
    tolerance = 0.02
    
    for product in answer_key["product_margins"]:
        submitted_value = submission["product_margins"].get(product)
        expected_value = answer_key["product_margins"][product]
        
        if submitted_value is None:
            results["details"][product] = {
                "submitted": None,
                "expected": expected_value,
                "correct": False,
                "message": "Missing value"
            }
        elif abs(submitted_value - expected_value) <= tolerance:
            results["score"] += 10 / len(answer_key["product_margins"])
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": True,
                "message": "Correct within tolerance"
            }
        else:
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": False,
                "message": f"Outside tolerance of {tolerance}"
            }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_minimum_prices(submission, answer_key):
    """Evaluate the minimum prices calculation."""
    results = {"score": 0, "max_score": 10, "details": {}}
    tolerance = 1.00
    
    for product in answer_key["minimum_prices"]:
        submitted_value = submission["minimum_prices"].get(product)
        expected_value = answer_key["minimum_prices"][product]
        
        if submitted_value is None:
            results["details"][product] = {
                "submitted": None,
                "expected": expected_value,
                "correct": False,
                "message": "Missing value"
            }
        elif abs(submitted_value - expected_value) <= tolerance:
            results["score"] += 10 / len(answer_key["minimum_prices"])
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": True,
                "message": "Correct within tolerance"
            }
        else:
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": False,
                "message": f"Outside tolerance of ${tolerance}"
            }
    
    results["score"] = round(results["score"], 2)
    return results

def check_margin_requirement(tiered_price, cost, product, tier):
    """Check if a price meets the 40% margin requirement."""
    if tiered_price is None:
        return False, "Missing value"
    
    # Extract cost from product name
    costs = {
        "techpro_basic": 30.00,
        "techpro_professional": 50.00,
        "techpro_enterprise": 80.00
    }
    
    product_cost = costs.get(product)
    if product_cost is None:
        return False, f"Unknown product: {product}"
    
    margin = (tiered_price - product_cost) / tiered_price
    if margin < 0.40:
        return False, f"Margin of {margin:.2%} is below 40% minimum"
    return True, f"Margin of {margin:.2%} meets requirement"

def evaluate_tiered_pricing(submission, answer_key, costs):
    """Evaluate the tiered pricing structure."""
    results = {"score": 0, "max_score": 15, "details": {}}
    
    # Define costs for margin checking
    product_costs = {
        "techpro_basic": 30.00,
        "techpro_professional": 50.00,
        "techpro_enterprise": 80.00
    }
    
    total_tiers = 0
    correct_tiers = 0
    
    for product in answer_key["tiered_pricing"]:
        results["details"][product] = {}
        
        for tier in answer_key["tiered_pricing"][product]:
            total_tiers += 1
            submitted_value = submission["tiered_pricing"].get(product, {}).get(tier)
            expected_value = answer_key["tiered_pricing"][product][tier]
            
            # Check if price exists
            if submitted_value is None:
                results["details"][product][tier] = {
                    "submitted": None,
                    "expected": expected_value,
                    "correct": False,
                    "message": "Missing value"
                }
                continue
            
            # Check margin requirement
            meets_margin, margin_message = check_margin_requirement(
                submitted_value, product_costs[product], product, tier
            )
            
            # Check if pricing is logical (higher tiers should have lower prices)
            logical_pricing = True
            tier_number = int(tier.split('_')[1])
            
            if tier_number > 1:
                previous_tier = f"tier_{tier_number-1}_" + tier.split('_', 2)[2]
                previous_price = submission["tiered_pricing"].get(product, {}).get(previous_tier)
                
                if previous_price is not None and submitted_value > previous_price:
                    logical_pricing = False
            
            # Evaluate the tier
            if meets_margin and logical_pricing:
                # We're not checking exact match with answer key, just that it meets requirements
                correct_tiers += 1
                results["details"][product][tier] = {
                    "submitted": submitted_value,
                    "expected": expected_value,
                    "correct": True,
                    "message": margin_message
                }
            else:
                message = margin_message
                if not logical_pricing:
                    message += "; Illogical pricing (higher price for larger volume)"
                
                results["details"][product][tier] = {
                    "submitted": submitted_value,
                    "expected": expected_value,
                    "correct": False,
                    "message": message
                }
    
    if total_tiers > 0:
        results["score"] = round((correct_tiers / total_tiers) * results["max_score"], 2)
    
    return results

def evaluate_discount_rates(submission, answer_key):
    """Evaluate the discount rates."""
    results = {"score": 0, "max_score": 10, "details": {}}
    tolerance = 0.05  # Allow some flexibility in discount rates
    
    for segment in answer_key["discount_rates"]:
        submitted_value = submission["discount_rates"].get(segment)
        expected_value = answer_key["discount_rates"][segment]
        
        if submitted_value is None:
            results["details"][segment] = {
                "submitted": None,
                "expected": expected_value,
                "correct": False,
                "message": "Missing value"
            }
        elif abs(submitted_value - expected_value) <= tolerance:
            results["score"] += 10 / len(answer_key["discount_rates"])
            results["details"][segment] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": True,
                "message": "Within acceptable range"
            }
        else:
            # Check if discount rates align with segment characteristics
            # Enterprise should have highest discount, small business lowest
            aligned_with_characteristics = True
            
            if segment == "enterprise" and submitted_value < submission["discount_rates"].get("mid_market", 0):
                aligned_with_characteristics = False
            elif segment == "small_business" and submitted_value > submission["discount_rates"].get("mid_market", 1):
                aligned_with_characteristics = False
            
            if aligned_with_characteristics:
                # If the discount rate aligns with segment characteristics, award partial credit
                results["score"] += (5 / len(answer_key["discount_rates"]))
                results["details"][segment] = {
                    "submitted": submitted_value,
                    "expected": expected_value,
                    "correct": False,
                    "message": "Different from expected but aligns with segment characteristics"
                }
            else:
                results["details"][segment] = {
                    "submitted": submitted_value,
                    "expected": expected_value,
                    "correct": False,
                    "message": "Does not align with segment characteristics"
                }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_volume_thresholds(submission, answer_key):
    """Evaluate the volume thresholds."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    # Define acceptable ranges for thresholds based on sales data
    acceptable_ranges = {
        "discount_tier_1": (8, 12),    # Around 10
        "discount_tier_2": (45, 55),   # Around 50
        "discount_tier_3": (95, 105)   # Around 100
    }
    
    for tier in answer_key["volume_thresholds"]:
        submitted_value = submission["volume_thresholds"].get(tier)
        expected_value = answer_key["volume_thresholds"][tier]
        
        if submitted_value is None:
            results["details"][tier] = {
                "submitted": None,
                "expected": expected_value,
                "correct": False,
                "message": "Missing value"
            }
        elif acceptable_ranges[tier][0] <= submitted_value <= acceptable_ranges[tier][1]:
            results["score"] += 10 / len(answer_key["volume_thresholds"])
            results["details"][tier] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": True,
                "message": "Within acceptable range"
            }
        else:
            results["details"][tier] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": False,
                "message": f"Outside acceptable range {acceptable_ranges[tier]}"
            }
    
    # Check if thresholds are in ascending order
    if all(key in submission["volume_thresholds"] for key in ["discount_tier_1", "discount_tier_2", "discount_tier_3"]):
        t1 = submission["volume_thresholds"]["discount_tier_1"]
        t2 = submission["volume_thresholds"]["discount_tier_2"]
        t3 = submission["volume_thresholds"]["discount_tier_3"]
        
        if not (t1 < t2 < t3):
            results["score"] = max(0, results["score"] - 5)  # Penalty for non-ascending thresholds
            results["details"]["order_check"] = {
                "correct": False,
                "message": "Thresholds are not in ascending order"
            }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_competitive_price_index(submission, answer_key):
    """Evaluate the competitive price index."""
    results = {"score": 0, "max_score": 5, "details": {}}
    tolerance = 0.05
    
    for product in answer_key["competitive_price_index"]:
        submitted_value = submission["competitive_price_index"].get(product)
        expected_value = answer_key["competitive_price_index"][product]
        
        if submitted_value is None:
            results["details"][product] = {
                "submitted": None,
                "expected": expected_value,
                "correct": False,
                "message": "Missing value"
            }
        elif abs(submitted_value - expected_value) <= tolerance:
            results["score"] += 5 / len(answer_key["competitive_price_index"])
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": True,
                "message": "Correct within tolerance"
            }
        else:
            results["details"][product] = {
                "submitted": submitted_value,
                "expected": expected_value,
                "correct": False,
                "message": f"Outside tolerance of {tolerance}"
            }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_pricing_strategy_rationale(submission):
    """Evaluate the pricing strategy rationale."""
    results = {"score": 0, "max_score": 10, "details": {}}
    
    rationale = submission.get("pricing_strategy_rationale", "")
    
    # Check if rationale exists
    if not rationale:
        results["details"]["rationale"] = {
            "correct": False,
            "message": "No pricing strategy rationale provided"
        }
        return results
    
    # Check word count (100-200 words)
    word_count = len(rationale.split())
    if word_count < 50:
        results["details"]["word_count"] = {
            "correct": False,
            "message": f"Rationale too short ({word_count} words, minimum 50 recommended)"
        }
        results["score"] = 2  # Minimal points for very short rationale
    else:
        results["details"]["word_count"] = {
            "correct": True,
            "message": f"Acceptable length ({word_count} words)"
        }
        
        # Award points based on content quality indicators
        # This is a simplified evaluation - in a real scenario, this would require human judgment
        key_concepts = [
            "margin", "profit", "competitive", "segment", "volume", "discount", 
            "tier", "price sensitivity", "customer lifetime value", "market"
        ]
        
        concept_count = sum(1 for concept in key_concepts if concept.lower() in rationale.lower())
        concept_score = min(8, concept_count)
        
        results["score"] = concept_score
        results["details"]["content"] = {
            "message": f"Rationale addresses {concept_count} of {len(key_concepts)} key pricing concepts"
        }
    
    results["score"] = round(results["score"], 2)
    return results

def evaluate_submission(submission, answer_key):
    """Evaluate the full submission against the answer key."""
    results = {
        "product_margins": evaluate_product_margins(submission, answer_key),
        "minimum_prices": evaluate_minimum_prices(submission, answer_key),
        "tiered_pricing": evaluate_tiered_pricing(submission, answer_key, None),
        "discount_rates": evaluate_discount_rates(submission, answer_key),
        "volume_thresholds": evaluate_volume_thresholds(submission, answer_key),
        "competitive_price_index": evaluate_competitive_price_index(submission, answer_key),
    }
    
    # Add pricing strategy rationale evaluation if it exists in the submission
    if "pricing_strategy_rationale" in submission:
        results["pricing_strategy_rationale"] = evaluate_pricing_strategy_rationale(submission)
    
    # Calculate overall score
    total_score = sum(section["score"] for section in results.values())
    total_possible = sum(section["max_score"] for section in results.values())
    overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
    
    # Check for automatic failing conditions
    failing_conditions = []
    
    # Check if any tiered price falls below 40% margin
    product_costs = {
        "techpro_basic": 30.00,
        "techpro_professional": 50.00,
        "techpro_enterprise": 80.00
    }
    
    for product in submission.get("tiered_pricing", {}):
        for tier, price in submission["tiered_pricing"][product].items():
            if price is not None:
                margin = (price - product_costs.get(product, 0)) / price
                if margin < 0.40:
                    failing_conditions.append(
                        f"{product} {tier} price (${price}) has margin of {margin:.2%}, below 40% minimum"
                    )
    
    # Check for illogical pricing structure
    for product in submission.get("tiered_pricing", {}):
        tiers = sorted(submission["tiered_pricing"][product].keys())
        for i in range(1, len(tiers)):
            current_tier = tiers[i]
            previous_tier = tiers[i-1]
            current_price = submission["tiered_pricing"][product][current_tier]
            previous_price = submission["tiered_pricing"][product][previous_tier]
            
            if current_price is not None and previous_price is not None and current_price > previous_price:
                failing_conditions.append(
                    f"Illogical pricing: {product} {current_tier} (${current_price}) > {previous_tier} (${previous_price})"
                )
    
    # Final results
    final_results = {
        "section_scores": results,
        "overall_score": round(overall_percentage, 2),
        "passing_score": 75.00,
        "passed": overall_percentage >= 75.00 and not failing_conditions,
        "failing_conditions": failing_conditions
    }
    
    return final_results

def main():
    if len(sys.argv) != 3:
        print("Usage: python task_evaluation.py test_submission.json answer_key.json")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    answer_key_file = sys.argv[2]
    
    submission = load_json_file(submission_file)
    answer_key = load_json_file(answer_key_file)
    
    results = evaluate_submission(submission, answer_key)
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation complete. Results saved to test_results.json")
    print(f"Overall score: {results['overall_score']}%")
    if results['passed']:
        print("PASSED")
    else:
        print("FAILED")
        if results['failing_conditions']:
            print("Failing conditions:")
            for condition in results['failing_conditions']:
                print(f"- {condition}")

if __name__ == "__main__":
    main()