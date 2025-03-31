import json
import pandas as pd
import os
from PyPDF2 import PdfReader

def validate_csv(candidate_csv_path, answer_csv_path):
    candidate_df = pd.read_csv(candidate_csv_path)
    answer_df = pd.read_csv(answer_csv_path)

    # Check Product A inventory
    candidate_product_a_inventory = candidate_df.loc[candidate_df['Product'] == 'Product A', 'Inventory'].values[0]
    answer_product_a_inventory = answer_df.loc[answer_df['Product'] == 'Product A', 'Inventory'].values[0]
    inventory_correct = candidate_product_a_inventory == answer_product_a_inventory

    # Check Transaction ID 102 date
    candidate_transaction_date = candidate_df.loc[candidate_df['Transaction ID'] == 102, 'Date'].values[0]
    answer_transaction_date = answer_df.loc[answer_df['Transaction ID'] == 102, 'Date'].values[0]
    date_correct = candidate_transaction_date == answer_transaction_date

    # Check monetary formatting
    candidate_monetary_format_correct = all(candidate_df['Monetary Value'].apply(lambda x: isinstance(x, float) and len(str(x).split('.')[1]) == 2))
    answer_monetary_format_correct = all(answer_df['Monetary Value'].apply(lambda x: isinstance(x, float) and len(str(x).split('.')[1]) == 2))
    monetary_format_correct = candidate_monetary_format_correct == answer_monetary_format_correct

    return inventory_correct, date_correct, monetary_format_correct

def validate_pdf(candidate_pdf_path, answer_pdf_path):
    candidate_reader = PdfReader(candidate_pdf_path)
    answer_reader = PdfReader(answer_pdf_path)

    candidate_text = ''.join([page.extract_text() for page in candidate_reader.pages])
    answer_text = ''.join([page.extract_text() for page in answer_reader.pages])

    # Check if the text content matches
    return candidate_text.strip() == answer_text.strip()

def main():
    # Load the candidate's submission and the answer key
    with open('test_submission.json', 'r') as f:
        candidate_submission = json.load(f)

    with open('answer_key.json', 'r') as f:
        answer_key = json.load(f)

    # Paths to the candidate's files
    candidate_csv_path = candidate_submission['task_1']['updated_csv']
    candidate_pdf_path = candidate_submission['task_2']['report_pdf']

    # Paths to the answer key files
    answer_csv_path = answer_key['task_1']['updated_csv']
    answer_pdf_path = answer_key['task_2']['report_pdf']

    # Validate CSV
    inventory_correct, date_correct, monetary_format_correct = validate_csv(candidate_csv_path, answer_csv_path)

    # Validate PDF
    pdf_correct = validate_pdf(candidate_pdf_path, answer_pdf_path)

    # Calculate overall score
    total_criteria = 4
    correct_criteria = sum([inventory_correct, date_correct, monetary_format_correct, pdf_correct])
    overall_score = (correct_criteria / total_criteria) * 100

    # Prepare the results
    results = {
        "task_1": {
            "inventory_correct": inventory_correct,
            "date_correct": date_correct,
            "monetary_format_correct": monetary_format_correct
        },
        "task_2": {
            "pdf_correct": pdf_correct
        },
        "overall_score": overall_score
    }

    # Save the results to a JSON file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()