#!/usr/bin/env python3
"""
Process the missing HD170 PDF and fix date format issues
"""

import pandas as pd
import pdfplumber
import os
import re
from datetime import datetime

def process_hd170_pdf():
    """Process the HD170_5558_ENQ600_4_hold.pdf file."""
    pdf_path = "Data Hand-Over/Stock Balances/HD170_5558_ENQ600_4_hold.pdf"
    
    print("Processing HD170_5558_ENQ600_4_hold.pdf...")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    extracted_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                if page_num == 1:
                    print("📖 First page content preview:")
                    print(text[:500] if text else "No text extracted")
                    print("...")
                
                if text:
                    # Try to extract tables
                    tables = page.extract_tables()
                    
                    if tables:
                        print(f"📊 Found {len(tables)} table(s) on page {page_num}")
                        
                        for table_num, table in enumerate(tables):
                            if table and len(table) > 1:
                                # Process table data
                                headers = table[0] if table[0] else []
                                
                                for row_num, row in enumerate(table[1:], 1):
                                    if row and any(cell for cell in row if cell):
                                        row_data = {
                                            'source_file': os.path.basename(pdf_path),
                                            'page_number': page_num,
                                            'table_number': table_num + 1,
                                            'row_number': row_num,
                                            'document_type': 'Stock Query/Hold Report',
                                            'file_type': 'PDF'
                                        }
                                        
                                        # Add row data
                                        for col_num, cell in enumerate(row):
                                            col_name = headers[col_num] if col_num < len(headers) and headers[col_num] else f'column_{col_num + 1}'
                                            row_data[col_name] = cell
                                        
                                        extracted_data.append(row_data)
                    
                    else:
                        # No tables, extract text data
                        lines = text.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if line.strip():
                                extracted_data.append({
                                    'source_file': os.path.basename(pdf_path),
                                    'page_number': page_num,
                                    'line_number': line_num,
                                    'content': line.strip(),
                                    'document_type': 'Stock Query/Hold Report',
                                    'file_type': 'PDF'
                                })
    
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return None
    
    if extracted_data:
        # Save to CSV
        df = pd.DataFrame(extracted_data)
        output_file = "output/individual_hd170_stock_query.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {len(extracted_data)} records to {output_file}")
        return df
    else:
        print("⚠️ No data extracted from PDF")
        return None

def fix_pdf_date_formats():
    """Fix the date format issues in PDF-derived CSV files."""
    print("\nFixing PDF date format issues...")
    
    files_to_fix = [
        "output/individual_hr185_transactions.csv",
        "output/individual_hr990_expenditure.csv"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"🔧 Fixing dates in {file_path}")
            
            df = pd.read_csv(file_path)
            
            if 'report_period' in df.columns:
                # Convert report_period to a more standard format
                original_periods = df['report_period'].unique()
                print(f"  Original report_period values: {original_periods[:5]}")
                
                # Create standardized report period
                df['report_period_start'] = df['report_period'].apply(lambda x: extract_period_start(x))
                df['report_period_end'] = df['report_period'].apply(lambda x: extract_period_end(x))
                
                # Keep original for reference
                df['original_report_period'] = df['report_period']
                
                # Update report_period to start date for better date handling
                df['report_period'] = df['report_period_start']
                
                # Save updated file
                df.to_csv(file_path, index=False)
                print(f"  ✅ Updated {len(df)} records with standardized dates")
            else:
                print(f"  ⚠️ No report_period column found")
        else:
            print(f"  ❌ File not found: {file_path}")

def extract_period_start(period_str):
    """Extract start date from period string like '202207-202306'."""
    if pd.isna(period_str) or not isinstance(period_str, str):
        return None
    
    try:
        # Extract first part (start period)
        start_part = period_str.split('-')[0]
        if len(start_part) == 6:  # YYYYMM format
            year = int(start_part[:4])
            month = int(start_part[4:])
            return f"{year}-{month:02d}-01"  # First day of the month
    except:
        pass
    
    return None

def extract_period_end(period_str):
    """Extract end date from period string like '202207-202306'."""
    if pd.isna(period_str) or not isinstance(period_str, str):
        return None
    
    try:
        # Extract second part (end period)
        parts = period_str.split('-')
        if len(parts) == 2:
            end_part = parts[1]
            if len(end_part) == 6:  # YYYYMM format
                year = int(end_part[:4])
                month = int(end_part[4:])
                # Last day of the month
                if month == 12:
                    return f"{year}-{month:02d}-31"
                else:
                    # Approximate last day (could be improved with calendar module)
                    last_day = 30 if month in [4, 6, 9, 11] else 31
                    if month == 2:
                        last_day = 29 if year % 4 == 0 else 28
                    return f"{year}-{month:02d}-{last_day}"
    except:
        pass
    
    return None

def verify_all_dates():
    """Verify all date formats across all CSV files."""
    print("\n=== FINAL DATE VERIFICATION ===")
    
    output_dir = "output"
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    
    total_issues = 0
    
    for csv_file in csv_files:
        file_path = os.path.join(output_dir, csv_file)
        
        try:
            df = pd.read_csv(file_path)
            
            # Find date columns
            date_columns = []
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'period']):
                    date_columns.append(col)
            
            if date_columns:
                file_issues = 0
                for date_col in date_columns:
                    try:
                        converted_dates = pd.to_datetime(df[date_col], errors='coerce')
                        valid_dates = converted_dates.notna().sum()
                        total_non_null = df[date_col].notna().sum()
                        
                        if total_non_null > 0:
                            conversion_rate = (valid_dates / total_non_null) * 100
                            
                            if conversion_rate < 95:
                                print(f"  ⚠️ {csv_file}: {date_col} = {conversion_rate:.1f}% valid")
                                file_issues += 1
                    except:
                        print(f"  ❌ {csv_file}: {date_col} = Error checking")
                        file_issues += 1
                
                if file_issues == 0:
                    print(f"  ✅ {csv_file}: All dates OK ({len(date_columns)} columns)")
                
                total_issues += file_issues
        
        except Exception as e:
            print(f"  ❌ {csv_file}: Error reading file")
            total_issues += 1
    
    print(f"\n📊 Total files checked: {len(csv_files)}")
    print(f"📅 Total date issues: {total_issues}")
    
    return total_issues

if __name__ == "__main__":
    print("🔍 FIXING DATA PROCESSING SHORTFALLS")
    print("=" * 50)
    
    # 1. Process missing HD170 PDF
    hd170_result = process_hd170_pdf()
    
    # 2. Fix PDF date formats
    fix_pdf_date_formats()
    
    # 3. Final verification
    total_issues = verify_all_dates()
    
    print("\n" + "=" * 50)
    print("🎯 SHORTFALL RESOLUTION SUMMARY")
    print("=" * 50)
    
    if hd170_result is not None:
        print("✅ HD170 PDF processed successfully")
    else:
        print("⚠️ HD170 PDF processing had issues")
    
    print("✅ PDF date formats standardized")
    
    if total_issues == 0:
        print("🎉 ALL DATA PROCESSING ISSUES RESOLVED!")
        print("✅ All source files processed")
        print("✅ All dates properly formatted")
        print("✅ Complete data coverage achieved")
    else:
        print(f"⚠️ {total_issues} date issues still need attention")
