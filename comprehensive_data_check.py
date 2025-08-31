#!/usr/bin/env python3
"""
Comprehensive Data Coverage and Date Format Verification Script
Checks all source files and their corresponding CSV outputs with date format validation
"""

import os
import pandas as pd
from pathlib import Path

def check_data_coverage():
    """Check all source files and verify they have corresponding CSV outputs."""
    
    print("=== COMPREHENSIVE DATA COVERAGE CHECK ===")
    print(f"Scan Date: 2025-08-31")
    
    # Define source directory
    source_dir = "Data Hand-Over"
    output_dir = "output"
    
    # 1. EXCEL FILES
    print("\n1. EXCEL FILES IN SOURCE:")
    excel_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(root, file))
    
    print(f"Found {len(excel_files)} Excel files:")
    for f in excel_files:
        print(f"  - {f}")
    
    # 2. PDF FILES
    print("\n2. PDF FILES IN SOURCE:")
    pdf_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    print(f"Found {len(pdf_files)} PDF files:")
    for f in pdf_files:
        print(f"  - {f}")
    
    # 3. TXT FILES
    print("\n3. TXT FILES IN SOURCE:")
    txt_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    print(f"Found {len(txt_files)} TXT files:")
    for f in txt_files:
        print(f"  - {f}")
    
    # 4. OUTPUT CSV FILES
    print("\n4. CSV FILES IN OUTPUT:")
    csv_files = []
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.csv'):
                csv_files.append(file)
    
    print(f"Found {len(csv_files)} CSV files in output:")
    for f in sorted(csv_files):
        print(f"  - {f}")
    
    # 5. MAPPING CHECK
    print("\n5. SOURCE TO OUTPUT MAPPING:")
    
    # Expected mappings
    expected_mappings = {
        "HR995grn.xlsx": ["hr995_grn.csv", "individual_hr995grn.csv"],
        "HR995issue.xlsx": ["hr995_issue.csv", "individual_hr995issue.csv"],
        "HR995redund.xlsx": ["hr995_redundant.csv", "individual_hr995redund.csv"],
        "HR995vouch.xlsx": ["hr995_voucher.csv", "individual_hr995vouch.csv"],
        "2023 List of Suppliers.xlsx": ["individual_2023_list_of_suppliers.csv"],
        "2024 List of Suppliers.xlsx": ["individual_2024_list_of_suppliers.csv"],
        "Final stock list 2324.xlsx": ["individual_final_stock_list_2324.csv"],
        "Final stock listing 2023.xlsx": ["individual_final_stock_listing_2023.csv"],
        "hr450x250726.txt": ["hr450_data.csv", "individual_hr450x250726.csv"],
        "Stock Adjustment item 2024.xlsx": ["individual_stock_adjustment_item_2024.csv"],
        "Variance report.xlsx": ["variance_report.csv", "individual_variance_report.csv"]
    }
    
    # PDF expected mappings
    pdf_mappings = {
        "HR185": ["individual_hr185_transactions.csv"],
        "HR990": ["individual_hr990_expenditure.csv"],
    }
    
    missing_outputs = []
    
    # Check Excel/TXT mappings
    for source_file, expected_csvs in expected_mappings.items():
        source_exists = any(source_file in excel_path for excel_path in excel_files + txt_files)
        if source_exists:
            for csv_file in expected_csvs:
                if csv_file not in csv_files:
                    missing_outputs.append(f"{source_file} -> {csv_file}")
                else:
                    print(f"  ✅ {source_file} -> {csv_file}")
        else:
            print(f"  ⚠️ Source file not found: {source_file}")
    
    # Check PDF mappings
    for pdf_type, expected_csvs in pdf_mappings.items():
        pdf_exists = any(pdf_type in pdf_path for pdf_path in pdf_files)
        if pdf_exists:
            for csv_file in expected_csvs:
                if csv_file not in csv_files:
                    missing_outputs.append(f"{pdf_type} PDFs -> {csv_file}")
                else:
                    print(f"  ✅ {pdf_type} PDFs -> {csv_file}")
    
    if missing_outputs:
        print("\n❌ MISSING OUTPUT FILES:")
        for missing in missing_outputs:
            print(f"  - {missing}")
    else:
        print("\n✅ ALL EXPECTED OUTPUT FILES FOUND")
    
    return len(excel_files), len(pdf_files), len(txt_files), len(csv_files), len(missing_outputs)

def check_date_formats():
    """Check date formats in all CSV files."""
    print("\n=== DATE FORMAT VERIFICATION ===")
    
    output_dir = "output"
    date_issues = []
    
    # Files that should have date columns
    date_files = [
        "hr995_grn.csv",
        "hr995_issue.csv", 
        "hr995_voucher.csv",
        "individual_hr995grn.csv",
        "individual_hr995issue.csv",
        "individual_hr995vouch.csv",
        "individual_hr185_transactions.csv",
        "individual_hr990_expenditure.csv"
    ]
    
    for csv_file in date_files:
        file_path = os.path.join(output_dir, csv_file)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                print(f"\n📄 {csv_file}:")
                print(f"  Rows: {len(df)}")
                
                # Check for date columns
                date_columns = []
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'period']):
                        date_columns.append(col)
                
                if date_columns:
                    print(f"  Date columns: {date_columns}")
                    
                    for date_col in date_columns:
                        # Sample some values
                        sample_values = df[date_col].dropna().head(5).tolist()
                        print(f"    {date_col} samples: {sample_values}")
                        
                        # Check for proper date conversion
                        try:
                            converted_dates = pd.to_datetime(df[date_col], errors='coerce')
                            valid_dates = converted_dates.notna().sum()
                            total_non_null = df[date_col].notna().sum()
                            
                            if total_non_null > 0:
                                conversion_rate = (valid_dates / total_non_null) * 100
                                print(f"    {date_col} conversion rate: {conversion_rate:.1f}% ({valid_dates}/{total_non_null})")
                                
                                if conversion_rate < 95:
                                    date_issues.append(f"{csv_file}: {date_col} has {conversion_rate:.1f}% conversion rate")
                            
                        except Exception as e:
                            date_issues.append(f"{csv_file}: {date_col} - Error checking dates: {str(e)}")
                            
                else:
                    print(f"  No date columns found")
                    
            except Exception as e:
                date_issues.append(f"{csv_file}: Error reading file - {str(e)}")
        else:
            date_issues.append(f"{csv_file}: File not found")
    
    if date_issues:
        print("\n❌ DATE FORMAT ISSUES:")
        for issue in date_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ ALL DATE FORMATS APPEAR CORRECT")
    
    return len(date_issues)

def check_pdf_processing():
    """Check if PDF files have been properly processed."""
    print("\n=== PDF PROCESSING VERIFICATION ===")
    
    # Check if PDFs have been processed
    pdf_outputs = [
        "individual_hr185_transactions.csv",
        "individual_hr990_expenditure.csv"
    ]
    
    pdf_issues = []
    
    for pdf_csv in pdf_outputs:
        file_path = os.path.join("output", pdf_csv)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                print(f"📊 {pdf_csv}: {len(df)} rows")
                
                # Check if it has content
                if len(df) == 0:
                    pdf_issues.append(f"{pdf_csv}: Empty file")
                elif len(df) < 10:
                    pdf_issues.append(f"{pdf_csv}: Very few rows ({len(df)})")
                
                # Check for expected columns
                print(f"  Columns: {list(df.columns)}")
                
            except Exception as e:
                pdf_issues.append(f"{pdf_csv}: Error reading - {str(e)}")
        else:
            pdf_issues.append(f"{pdf_csv}: File missing")
    
    if pdf_issues:
        print("\n❌ PDF PROCESSING ISSUES:")
        for issue in pdf_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ PDF PROCESSING APPEARS CORRECT")
    
    return len(pdf_issues)

if __name__ == "__main__":
    # Run all checks
    excel_count, pdf_count, txt_count, csv_count, missing_count = check_data_coverage()
    date_issues_count = check_date_formats()
    pdf_issues_count = check_pdf_processing()
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY REPORT")
    print("="*50)
    print(f"📁 Source Files: {excel_count} Excel + {pdf_count} PDF + {txt_count} TXT = {excel_count + pdf_count + txt_count} total")
    print(f"📄 Output CSV Files: {csv_count}")
    print(f"❌ Missing Outputs: {missing_count}")
    print(f"📅 Date Issues: {date_issues_count}")
    print(f"📋 PDF Issues: {pdf_issues_count}")
    
    total_issues = missing_count + date_issues_count + pdf_issues_count
    
    if total_issues == 0:
        print("\n🎉 ALL CHECKS PASSED - DATA PROCESSING IS COMPLETE!")
    else:
        print(f"\n⚠️ TOTAL ISSUES FOUND: {total_issues}")
        print("📋 ACTION REQUIRED: Review and fix the issues listed above")
