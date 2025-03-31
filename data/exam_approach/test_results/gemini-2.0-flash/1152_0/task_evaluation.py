import json

def evaluate_exam(submission_file="test_submission.json", answer_key_file="answer_key.json"):
    """
    Evaluates the candidate's submission against the answer key and generates a score report.

    Args:
        submission_file (str): Path to the candidate's submission JSON file.
        answer_key_file (str): Path to the answer key JSON file.

    Returns:
        dict: A dictionary containing the test results and overall score.
    """

    try:
        with open(submission_file, 'r') as f:
            submission = json.load(f)
    except FileNotFoundError:
        return {"error": f"Submission file '{submission_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in submission file '{submission_file}'."}

    try:
        with open(answer_key_file, 'r') as f:
            answer_key = json.load(f)
    except FileNotFoundError:
        return {"error": f"Answer key file '{answer_key_file}' not found."}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON format in answer key file '{answer_key_file}'."}

    test_results = {}
    total_possible_score = 0
    candidate_score = 0

    for item_name, item_answer_key in answer_key['answer_key'].items():
        test_results[item_name] = {}
        item_total_possible_score = 0
        item_candidate_score = 0

        if item_name in submission:
            submitted_item = submission[item_name]
            test_results[item_name]['description'] = submitted_item.get('description', 'N/A')
        else:
            test_results[item_name]['description'] = 'N/A - Item not found in submission'

        for supplier_num in ['supplier_1', 'supplier_2']:
            test_results[item_name][supplier_num] = {
                "supplier_name_score": 0,
                "product_code_score": 0,
                "catalog_reference_score": 0,
                "notes_score": 0, # Notes are not automatically scored in basic exam
                "total_supplier_score": 0
            }
            supplier_total_possible_score = 3 # supplier_name, product_code, catalog_reference
            supplier_candidate_score = 0

            if supplier_num in item_answer_key and supplier_num in submitted_item:
                answer_supplier = item_answer_key[supplier_num]
                submitted_supplier = submitted_item[supplier_num]

                # Supplier Name Score
                if 'supplier_name' in submitted_supplier and 'supplier_name' in answer_supplier:
                    submitted_supplier_name = submitted_supplier['supplier_name'].strip()
                    answer_supplier_name_options = [answer_supplier['supplier_name'].strip()]
                    if answer_supplier_name_options[0] == 'Supplier A - Industrial Components':
                        answer_supplier_name_options.append('Supplier A')
                    elif answer_supplier_name_options[0] == 'Supplier B - Office Furniture Solutions':
                        answer_supplier_name_options.append('Supplier B')
                    elif answer_supplier_name_options[0] == 'Supplier C - General Supplies':
                        answer_supplier_name_options.append('Supplier C')
                    elif answer_supplier_name_options[0] == 'Industrial Fasteners Inc.':
                        answer_supplier_name_options.append('Industrial Fasteners Inc')
                    elif answer_supplier_name_options[0] == 'Office Chairs Direct':
                        answer_supplier_name_options.append('Office Chairs Direct')
                    elif answer_supplier_name_options[0] == 'Allied Supplies Corp.':
                        answer_supplier_name_options.append('Allied Supplies Corp')


                    if submitted_supplier_name in answer_supplier_name_options:
                        test_results[item_name][supplier_num]["supplier_name_score"] = 1
                        supplier_candidate_score += 1

                # Product Code Score
                if 'product_code' in submitted_supplier and 'product_code' in answer_supplier:
                    submitted_product_code = submitted_supplier['product_code'].strip()
                    answer_product_code = answer_supplier['product_code'].strip()
                    if submitted_product_code == answer_product_code:
                        test_results[item_name][supplier_num]["product_code_score"] = 1
                        supplier_candidate_score += 1
                    elif answer_product_code == 'Need to check website' and submitted_product_code.lower() in ['need to check website', 'check website', 'website']:
                         test_results[item_name][supplier_num]["product_code_score"] = 1
                         supplier_candidate_score += 1


                # Catalog Reference Score
                if 'catalog_reference' in submitted_supplier and 'catalog_reference' in answer_supplier:
                    submitted_catalog_reference = submitted_supplier['catalog_reference'].strip()
                    answer_catalog_reference = answer_supplier['catalog_reference'].strip()
                    if submitted_catalog_reference == answer_catalog_reference:
                        test_results[item_name][supplier_num]["catalog_reference_score"] = 1
                        supplier_candidate_score += 1
                    elif answer_catalog_reference == 'Industry Directory' and submitted_catalog_reference.lower() in ['industry directory', 'directory']:
                        test_results[item_name][supplier_num]["catalog_reference_score"] = 1
                        supplier_candidate_score += 1


                test_results[item_name][supplier_num]["total_supplier_score"] = supplier_candidate_score
                item_candidate_score += supplier_candidate_score
                item_total_possible_score += supplier_total_possible_score


        test_results[item_name]['total_item_score'] = item_candidate_score
        total_possible_score += item_total_possible_score
        candidate_score += item_candidate_score

    overall_score = (candidate_score / total_possible_score) * 100 if total_possible_score > 0 else 0
    test_results['overall_score'] = round(overall_score, 2)

    return test_results

if __name__ == "__main__":
    evaluation_results = evaluate_exam()

    if "error" in evaluation_results:
        print(f"Error during evaluation: {evaluation_results['error']}")
    else:
        try:
            with open("test_results.json", 'w') as outfile:
                json.dump(evaluation_results, outfile, indent=4)
            print("Evaluation completed and results saved to 'test_results.json'")
        except Exception as e:
            print(f"Error saving results to 'test_results.json': {e}")
            print(json.dumps(evaluation_results, indent=4)) # Print results to console if saving fails