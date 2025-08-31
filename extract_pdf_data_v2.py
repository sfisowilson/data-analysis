#!/usr/bin/env python3
"""
Proper PDF data extraction based on actual structure analysis.
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path
from datetime import datetime

def extract_hr185_transactions(pdf_path):
    """Extract HR185 transaction data from PDFs."""
    print(f"\n=== Processing HR185: {pdf_path.name} ===")
    
    all_transactions = []
    current_supplier = None
    current_supplier_code = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Extract supplier information
                    supplier_match = re.search(r'Supplier\s*:\s*(\d+)\s+(.+?)\s+Date From', line)
                    if supplier_match:
                        current_supplier_code = supplier_match.group(1)
                        current_supplier = supplier_match.group(2).strip()
                        continue
                    
                    # Extract transaction lines (Date, Type, Reference, Amount, etc.)
                    # Pattern: 20220721 CHQ 27949 84588.37 777
                    transaction_match = re.match(r'^(\d{8})\s+(\w+)\s+(\w+)\s+([\d.-]+)\s+(.*)$', line)
                    if transaction_match and current_supplier:
                        try:
                            date_str = transaction_match.group(1)
                            transaction_date = datetime.strptime(date_str, '%Y%m%d').date()
                            
                            transaction = {
                                'source_file': pdf_path.name,
                                'page_number': page_num + 1,
                                'supplier_code': current_supplier_code,
                                'supplier_name': current_supplier,
                                'transaction_date': transaction_date,
                                'transaction_type': transaction_match.group(2),
                                'reference': transaction_match.group(3),
                                'amount': float(transaction_match.group(4)),
                                'additional_info': transaction_match.group(5).strip(),
                                'document_type': 'HR185_transaction',
                                'report_period': extract_period_from_filename(pdf_path.name),
                                'file_type': 'PDF'
                            }
                            
                            all_transactions.append(transaction)
                            
                        except (ValueError, IndexError) as e:
                            # Skip malformed lines
                            continue
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    print(f"Extracted {len(all_transactions)} transactions")
    return all_transactions

def extract_hr990_statistics(pdf_path):
    """Extract HR990 expenditure statistics from PDFs."""
    print(f"\n=== Processing HR990: {pdf_path.name} ===")
    
    all_statistics = []
    current_section = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Identify sections
                    if re.match(r'^\d+\.\s+(.+)$', line):
                        current_section = line
                        continue
                    
                    # Extract count/statistics lines
                    # Pattern: 25 ENQ131 - 96000 - N.G. MOTSIRI (SCM)
                    stats_match = re.match(r'^(\d+)\s+(.+?)\s+-\s+(\d+)\s+-\s+(.+)$', line)
                    if stats_match and current_section:
                        try:
                            statistic = {
                                'source_file': pdf_path.name,
                                'page_number': page_num + 1,
                                'section': current_section,
                                'count': int(stats_match.group(1)),
                                'reference': stats_match.group(2).strip(),
                                'code': stats_match.group(3),
                                'description': stats_match.group(4).strip(),
                                'document_type': 'HR990_statistic',
                                'report_period': extract_period_from_filename(pdf_path.name),
                                'file_type': 'PDF'
                            }
                            
                            all_statistics.append(statistic)
                            
                        except (ValueError, IndexError) as e:
                            continue
                    
                    # Extract total lines
                    # Pattern: Total Count of Supplier Additions 240
                    total_match = re.match(r'^Total\s+(.+?)\s+(\d+)$', line)
                    if total_match and current_section:
                        try:
                            statistic = {
                                'source_file': pdf_path.name,
                                'page_number': page_num + 1,
                                'section': current_section,
                                'count': int(total_match.group(2)),
                                'reference': 'TOTAL',
                                'code': 'TOTAL',
                                'description': total_match.group(1).strip(),
                                'document_type': 'HR990_total',
                                'report_period': extract_period_from_filename(pdf_path.name),
                                'file_type': 'PDF'
                            }
                            
                            all_statistics.append(statistic)
                            
                        except (ValueError, IndexError) as e:
                            continue
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    print(f"Extracted {len(all_statistics)} statistics")
    return all_statistics

def extract_period_from_filename(filename):
    """Extract date period from filename."""
    match = re.search(r'(\d{6})\s*-\s*(\d{6})', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def process_all_pdfs():
    """Process all PDF files and create CSV outputs."""
    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)
    
    # Process HR185 files
    print("🔍 Processing HR185 Transaction Reports...")
    hr185_data = []
    hr185_folder = Path("Data Hand-Over/HR185")
    
    for pdf_file in hr185_folder.glob("*.pdf"):
        data = extract_hr185_transactions(pdf_file)
        hr185_data.extend(data)
    
    if hr185_data:
        df = pd.DataFrame(hr185_data)
        output_file = output_folder / "individual_hr185_transactions.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ HR185 data saved: {output_file} ({len(df)} records)")
    else:
        print("⚠️  No HR185 transaction data extracted")
    
    # Process HR990 files
    print("\n🔍 Processing HR990 Expenditure Statistics...")
    hr990_data = []
    hr990_folder = Path("Data Hand-Over/HR990")
    
    for pdf_file in hr990_folder.glob("*.pdf"):
        data = extract_hr990_statistics(pdf_file)
        hr990_data.extend(data)
    
    if hr990_data:
        df = pd.DataFrame(hr990_data)
        output_file = output_folder / "individual_hr990_expenditure.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ HR990 data saved: {output_file} ({len(df)} records)")
    else:
        print("⚠️  No HR990 statistics data extracted")
    
    return len(hr185_data), len(hr990_data)

if __name__ == "__main__":
    print("🚀 Starting PDF Data Extraction...")
    print("=" * 60)
    
    hr185_count, hr990_count = process_all_pdfs()
    
    print("\n" + "=" * 60)
    print("🎉 PDF Processing Complete!")
    print(f"📊 HR185 transaction records: {hr185_count:,}")
    print(f"📈 HR990 statistic records: {hr990_count:,}")
    print(f"📋 Total PDF records: {hr185_count + hr990_count:,}")
    
    if hr185_count + hr990_count > 0:
        print(f"\n✅ CSV files created in 'output' folder")
        print(f"   - individual_hr185_transactions.csv")
        print(f"   - individual_hr990_expenditure.csv")
    else:
        print(f"\n⚠️  No data extracted - check PDF format compatibility")
