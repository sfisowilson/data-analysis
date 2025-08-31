#!/usr/bin/env python3
"""
Check original Excel files for YYYYMMDD date columns
"""

import pandas as pd
import os
from pathlib import Path

def check_excel_dates():
    print("=== CHECKING ORIGINAL EXCEL FILES FOR DATE COLUMNS ===")
    
    excel_files = [
        'Data Hand-Over/HR995grn.xlsx',
        'Data Hand-Over/HR995issue.xlsx', 
        'Data Hand-Over/HR995vouch.xlsx'
    ]
    
    for file_path in excel_files:
        if os.path.exists(file_path):
            try:
                print(f"\n=== {file_path} ===")
                
                # Read all sheets
                df_dict = pd.read_excel(file_path, sheet_name=None)
                print(f"Sheets found: {list(df_dict.keys())}")
                
                for sheet_name, df in df_dict.items():
                    print(f"\n--- Sheet: {sheet_name} ---")
                    print(f"Shape: {df.shape}")
                    print(f"Columns: {df.columns.tolist()}")
                    
                    # Look for date-like columns
                    date_cols = []
                    for col in df.columns:
                        if any(term in str(col).lower() for term in ['date', 'cheq', 'grn', 'issue', 'move', 'last']):
                            date_cols.append(col)
                    
                    if date_cols:
                        print(f"Potential date columns: {date_cols}")
                        
                        for col in date_cols:
                            sample_data = df[col].dropna().head(3)
                            print(f"  {col}: {sample_data.tolist()}")
                            
                            # Check for YYYYMMDD format
                            for val in sample_data:
                                try:
                                    if isinstance(val, (int, float)):
                                        val_str = str(int(val))
                                        if len(val_str) == 8:
                                            year = int(val_str[:4])
                                            month = int(val_str[4:6])
                                            day = int(val_str[6:8])
                                            print(f"    {val} -> {year}-{month:02d}-{day:02d} (YYYYMMDD) ✓")
                                        elif len(val_str) == 6:
                                            year = int(val_str[:4])
                                            month = int(val_str[4:6])
                                            print(f"    {val} -> {year}-{month:02d} (YYYYMM) ✓")
                                    elif hasattr(val, 'strftime'):
                                        print(f"    {val} -> {val.strftime('%Y-%m-%d')} (datetime) ✓")
                                except Exception as e:
                                    pass
                    
                    # Only check first sheet to avoid too much output
                    break
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    check_excel_dates()
