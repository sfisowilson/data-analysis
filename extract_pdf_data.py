#!/usr/bin/env python3
"""
Extract and parse data from HR185 and HR990 PDF reports.
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

def extract_hr185_data(pdf_path):
    """Extract supplier transaction data from HR185 PDFs."""
    print(f"\n=== Extracting HR185 data from: {pdf_path.name} ===")
    
    all_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                # Look for data lines that contain supplier information
                for line in lines:
                    line = line.strip()
                    
                    # Skip headers and empty lines
                    if not line or 'HR185' in line or 'Page' in line or '---' in line:
                        continue
                    
                    # Look for lines with supplier codes and amounts
                    # Pattern: supplier_code, supplier_name, amounts...
                    if re.search(r'\d+\.\d+', line):  # Contains decimal numbers
                        parts = re.split(r'\s{2,}', line)  # Split on multiple spaces
                        
                        if len(parts) >= 3:  # At least supplier code, name, amount
                            try:
                                data_row = {
                                    'source_file': pdf_path.name,
                                    'page_number': page_num + 1,
                                    'raw_line': line,
                                    'supplier_code': parts[0] if parts[0] else None,
                                    'supplier_name': parts[1] if len(parts) > 1 else None,
                                    'document_type': 'HR185_transactions',
                                    'report_period': extract_period_from_filename(pdf_path.name)
                                }
                                
                                # Try to extract amounts
                                amounts = []
                                for part in parts[2:]:
                                    if re.search(r'\d+\.\d+', part):
                                        amounts.append(part)
                                
                                if amounts:
                                    data_row['amount_1'] = amounts[0] if len(amounts) > 0 else None
                                    data_row['amount_2'] = amounts[1] if len(amounts) > 1 else None
                                    data_row['amount_3'] = amounts[2] if len(amounts) > 2 else None
                                
                                all_data.append(data_row)
                                
                            except Exception as e:
                                print(f"Error parsing line: {line[:50]}... - {e}")
                                continue
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return all_data

def extract_hr990_data(pdf_path):
    """Extract expenditure statistics from HR990 PDFs."""
    print(f"\n=== Extracting HR990 data from: {pdf_path.name} ===")
    
    all_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                # Look for expenditure data lines
                for line in lines:
                    line = line.strip()
                    
                    # Skip headers and empty lines
                    if not line or 'HR990' in line or 'Page' in line or '---' in line:
                        continue
                    
                    # Look for lines with expenditure data
                    if re.search(r'\d+\.\d+', line):  # Contains decimal numbers
                        parts = re.split(r'\s{2,}', line)  # Split on multiple spaces
                        
                        if len(parts) >= 2:
                            try:
                                data_row = {
                                    'source_file': pdf_path.name,
                                    'page_number': page_num + 1,
                                    'raw_line': line,
                                    'category': parts[0] if parts[0] else None,
                                    'description': parts[1] if len(parts) > 1 else None,
                                    'document_type': 'HR990_expenditure',
                                    'report_period': extract_period_from_filename(pdf_path.name)
                                }
                                
                                # Try to extract expenditure amounts
                                amounts = []
                                for part in parts[2:]:
                                    if re.search(r'\d+\.\d+', part):
                                        amounts.append(part)
                                
                                if amounts:
                                    data_row['expenditure_1'] = amounts[0] if len(amounts) > 0 else None
                                    data_row['expenditure_2'] = amounts[1] if len(amounts) > 1 else None
                                    data_row['expenditure_3'] = amounts[2] if len(amounts) > 2 else None
                                
                                all_data.append(data_row)
                                
                            except Exception as e:
                                print(f"Error parsing line: {line[:50]}... - {e}")
                                continue
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return all_data

def extract_period_from_filename(filename):
    """Extract date period from filename."""
    # Extract patterns like 202207-202306
    match = re.search(r'(\d{6})\s*-\s*(\d{6})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def process_all_pdfs():
    """Process all PDF files and create CSV outputs."""
    output_folder = Path("output")
    
    # Process HR185 files
    hr185_data = []
    hr185_folder = Path("Data Hand-Over/HR185")
    
    for pdf_file in hr185_folder.glob("*.pdf"):
        data = extract_hr185_data(pdf_file)
        hr185_data.extend(data)
        print(f"Extracted {len(data)} records from {pdf_file.name}")
    
    if hr185_data:
        df = pd.DataFrame(hr185_data)
        output_file = output_folder / "individual_hr185_transactions.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ HR185 data saved: {output_file} ({len(df)} records)")
    
    # Process HR990 files
    hr990_data = []
    hr990_folder = Path("Data Hand-Over/HR990")
    
    for pdf_file in hr990_folder.glob("*.pdf"):
        data = extract_hr990_data(pdf_file)
        hr990_data.extend(data)
        print(f"Extracted {len(data)} records from {pdf_file.name}")
    
    if hr990_data:
        df = pd.DataFrame(hr990_data)
        output_file = output_folder / "individual_hr990_expenditure.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ HR990 data saved: {output_file} ({len(df)} records)")
    
    return len(hr185_data), len(hr990_data)

if __name__ == "__main__":
    hr185_count, hr990_count = process_all_pdfs()
    print(f"\n🎉 PDF Processing Complete!")
    print(f"HR185 records extracted: {hr185_count}")
    print(f"HR990 records extracted: {hr990_count}")
    print(f"Total PDF records: {hr185_count + hr990_count}")
