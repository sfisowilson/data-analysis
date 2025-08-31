#!/usr/bin/env python3
"""
Find and test YYYYMMDD date columns across all files
"""

import pandas as pd
import os
from pathlib import Path

def find_date_columns():
    print("=== SEARCHING FOR YYYYMMDD DATE COLUMNS ===")
    
    output_folder = Path("output")
    csv_files = ['hr995_grn.csv', 'hr995_issue.csv', 'hr995_voucher.csv', 'all_stock_data.csv']
    
    for filename in csv_files:
        file_path = output_folder / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                print(f"\n=== {filename} ===")
                print(f"Total rows: {len(df)}")
                
                # Look for potential date columns
                potential_date_cols = []
                for col in df.columns:
                    if any(term in col.lower() for term in ['date', 'cheq', 'move', 'last', 'grn', 'issue']):
                        potential_date_cols.append(col)
                
                print(f"Potential date columns: {potential_date_cols}")
                
                for col in potential_date_cols:
                    if col in df.columns:
                        non_null_count = df[col].notna().sum()
                        print(f"\n--- {col} ---")
                        print(f"Non-null values: {non_null_count}/{len(df)}")
                        
                        if non_null_count > 0:
                            sample_values = df[col].dropna().head(5).tolist()
                            print(f"Sample values: {sample_values}")
                            
                            # Check if they could be YYYYMMDD
                            numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_values) > 0:
                                sample_numeric = numeric_values.head(3).tolist()
                                print(f"Sample numeric: {sample_numeric}")
                                
                                # Test YYYYMMDD conversion
                                for val in sample_numeric:
                                    try:
                                        val_str = str(int(val))
                                        if len(val_str) == 8:
                                            year = int(val_str[:4])
                                            month = int(val_str[4:6])
                                            day = int(val_str[6:8])
                                            print(f"  {val} -> {year}-{month:02d}-{day:02d} ✓")
                                        elif len(val_str) == 6:
                                            year = int(val_str[:4])
                                            month = int(val_str[4:6])
                                            print(f"  {val} -> {year}-{month:02d} (YYYYMM format) ✓")
                                        else:
                                            print(f"  {val} -> {len(val_str)} digits (unknown format)")
                                    except Exception as e:
                                        print(f"  {val} -> Error: {e}")
                
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    find_date_columns()
