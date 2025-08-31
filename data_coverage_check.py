#!/usr/bin/env python3
"""
Check data coverage and identify missing visualizations.
"""

import pandas as pd
import os
from pathlib import Path

def analyze_data_coverage():
    """Analyze what data we have and what might be missing from charts."""
    output_dir = Path('output')
    
    print("=== DATA COVERAGE ANALYSIS ===")
    print("=" * 50)
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    print(f"📊 Total CSV files: {len(csv_files)}")
    
    # Categorize files
    individual_files = [f for f in csv_files if f.startswith('individual_')]
    grouped_files = [f for f in csv_files if not f.startswith('individual_') and not f.startswith('objective_') and f != 'all_stock_data.csv']
    objective_files = [f for f in csv_files if f.startswith('objective_')]
    
    print(f"\n📁 File Categories:")
    print(f"  Individual sources: {len(individual_files)}")
    print(f"  Grouped sources: {len(grouped_files)}")
    print(f"  Analytics reports: {len(objective_files)}")
    print(f"  Master file: 1 (all_stock_data.csv)")
    
    # Check individual files
    print(f"\n📋 Individual Source Files:")
    for f in sorted(individual_files):
        try:
            df = pd.read_csv(output_dir / f)
            print(f"  ✅ {f:<40} {len(df):>8,} records")
        except Exception as e:
            print(f"  ❌ {f:<40} Error: {e}")
    
    # Check if master file includes all data
    print(f"\n🔍 Master File Analysis:")
    try:
        master_df = pd.read_csv(output_dir / 'all_stock_data.csv')
        print(f"  Total records in master: {len(master_df):,}")
        
        if 'source_file' in master_df.columns:
            print(f"  Unique source files: {master_df['source_file'].nunique()}")
            print(f"  Source breakdown:")
            for source, count in master_df['source_file'].value_counts().head(10).items():
                print(f"    {source:<35} {count:>8,}")
            
            # Check if new PDF data is included
            pdf_data = master_df[master_df['source_file'].str.contains('HR185|HR990', na=False)]
            print(f"\n📄 PDF data in master: {len(pdf_data):,} records")
            
        else:
            print("  ⚠️ No 'source_file' column found")
            
    except Exception as e:
        print(f"  ❌ Error reading master file: {e}")
    
    # Check for new data types that might need charts
    print(f"\n🎯 New Data Types Requiring Charts:")
    
    # Check HR185 transaction data
    try:
        hr185_df = pd.read_csv(output_dir / 'individual_hr185_transactions.csv')
        print(f"  ✅ HR185 Transactions: {len(hr185_df):,} records")
        if not hr185_df.empty:
            print(f"    - Transaction types: {hr185_df['transaction_type'].nunique() if 'transaction_type' in hr185_df.columns else 'N/A'}")
            print(f"    - Suppliers: {hr185_df['supplier_name'].nunique() if 'supplier_name' in hr185_df.columns else 'N/A'}")
            print(f"    - Date range: {hr185_df['transaction_date'].min() if 'transaction_date' in hr185_df.columns else 'N/A'} to {hr185_df['transaction_date'].max() if 'transaction_date' in hr185_df.columns else 'N/A'}")
    except:
        print(f"  ❌ HR185 Transactions: Not found or error")
    
    # Check HR990 statistics data
    try:
        hr990_df = pd.read_csv(output_dir / 'individual_hr990_expenditure.csv')
        print(f"  ✅ HR990 Statistics: {len(hr990_df):,} records")
        if not hr990_df.empty:
            print(f"    - Sections: {hr990_df['section'].nunique() if 'section' in hr990_df.columns else 'N/A'}")
            print(f"    - Document types: {hr990_df['document_type'].nunique() if 'document_type' in hr990_df.columns else 'N/A'}")
    except:
        print(f"  ❌ HR990 Statistics: Not found or error")
    
    return individual_files, grouped_files, objective_files

if __name__ == "__main__":
    analyze_data_coverage()
