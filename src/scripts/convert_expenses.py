#!/usr/bin/env python3
"""
Script to convert Excel expense data to JSON format.
"""
import json
from pathlib import Path
import openpyxl

def convert_excel_to_json():
    """Convert the Excel file to JSON format."""
    excel_path = Path(__file__).parent.parent.parent / "docs" / "Załącznik nr 2 Przykładowa tabela stosowana w procesie planowania budżetu.xlsx"
    
    # Load the workbook
    wb = openpyxl.load_workbook(excel_path)
    # Use the 'podział limitów' sheet which contains the actual expense data
    sheet = wb['podział limitów']
    
    expenses = []
    
    def safe_int(value):
        """Safely convert value to int."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return int(value)
        try:
            return int(str(value).strip())
        except (ValueError, AttributeError):
            return None
    
    def safe_str(value):
        """Safely convert value to string."""
        if value is None or value == '':
            return None
        return str(value).strip()
    
    # Skip header row, start from row 2
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # Skip empty rows
        if not any(row):
            continue
        
        # Extract required fields
        chapter = safe_int(row[7]) if len(row) > 7 else None  # paragraf
        task_name = safe_str(row[11]) if len(row) > 11 else None  # nazwa zadania
        financial_needs = safe_int(row[14]) if len(row) > 14 else None  # 2026
        
        # Skip if essential data is missing
        if not chapter or not task_name or not financial_needs or financial_needs <= 0:
            continue
        
        # Extract all additional fields
        expense_data = {
            "chapter": chapter,
            "task_name": task_name,
            "financial_needs": financial_needs,
            # Additional fields
            "czesc": safe_int(row[0]) if len(row) > 0 else None,
            "departament": safe_str(row[1]) if len(row) > 1 else None,
            "rodzaj_projektu": safe_str(row[2]) if len(row) > 2 else None,
            "opis_projektu": safe_str(row[3]) if len(row) > 3 else None,
            "data_zlozenia": safe_str(row[4]) if len(row) > 4 else None,
            "program_operacyjny": safe_str(row[5]) if len(row) > 5 else None,
            "termin_realizacji": safe_str(row[6]) if len(row) > 6 else None,
            "zrodlo_fin": safe_int(row[8]) if len(row) > 8 else None,
            "bz": safe_str(row[9]) if len(row) > 9 else None,
            "beneficjent": safe_str(row[10]) if len(row) > 10 else None,
            "szczegolowe_uzasadnienie": safe_str(row[12]) if len(row) > 12 else None,
            "budget_2025": safe_int(row[13]) if len(row) > 13 else None,
            "budget_2026": safe_int(row[14]) if len(row) > 14 else None,
            "budget_2027": safe_int(row[15]) if len(row) > 15 else None,
            "budget_2028": safe_int(row[16]) if len(row) > 16 else None,
            "budget_2029": safe_int(row[17]) if len(row) > 17 else None,
            "etap_dzialan": safe_str(row[18]) if len(row) > 18 else None,
            "umowy": safe_str(row[19]) if len(row) > 19 else None,
            "nr_umowy": safe_str(row[20]) if len(row) > 20 else None,
            "z_kim_zawarta": safe_str(row[21]) if len(row) > 21 else None,
            "uwagi": safe_str(row[22]) if len(row) > 22 else None,
        }
        
        expenses.append(expense_data)
    
    # Save to JSON
    json_path = Path(__file__).parent / "data" / "expenses_template.json"
    json_path.parent.mkdir(exist_ok=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)
    
    print(f"Converted {len(expenses)} expenses to {json_path}")
    return expenses

if __name__ == "__main__":
    convert_excel_to_json()
