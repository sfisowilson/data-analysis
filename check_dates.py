#!/usr/bin/env python3
"""
Check date columns and formats in all CSV files
"""

import pandas as pd
import os
from pathlib import Path

def check_dates():
    output_folder = Path("output")
    csv_files = list(output_folder.glob("*.csv"))
    
    print("=== DATE COLUMN ANALYSIS ===")
    print()
    
    for csv_file in csv_files[:5]:  # Check first 5 files
        try:
            df = pd.read_csv(csv_file)
            print(f"File: {csv_file.name}")
            
            # Find date columns
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            print(f"Date columns: {date_cols}")
            
            if date_cols:
                for col in date_cols:
                    non_null = df[col].notna().sum()
                    total = len(df)
                    print(f"  {col}: {non_null}/{total} non-null values")
                    
                    if non_null > 0:
                        sample_values = df[col].dropna().head(5).tolist()
                        print(f"  Sample values: {sample_values}")
            
            # Also check for any column that might contain dates
            potential_date_cols = []
            for col in df.columns:
                if any(term in col.lower() for term in ['period', 'time', 'year', 'month']):
                    potential_date_cols.append(col)
            
            if potential_date_cols:
                print(f"Potential date/time columns: {potential_date_cols}")
                for col in potential_date_cols:
                    sample_values = df[col].dropna().head(3).tolist()
                    print(f"  {col} samples: {sample_values}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
            print("-" * 50)

if __name__ == "__main__":
    check_dates()
