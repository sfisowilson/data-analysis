#!/usr/bin/env python3
"""
Verify that the YYYYMMDD dates are now properly extracted
"""

import pandas as pd

def verify_extracted_dates():
    print("=== VERIFYING EXTRACTED DATES ===")
    
    files_to_check = [
        ('hr995_grn.csv', 'GRN Date'),
        ('hr995_issue.csv', 'Issue Date'),
        ('hr995_voucher.csv', 'Cheq Date')
    ]
    
    for filename, expected_date_col in files_to_check:
        try:
            df = pd.read_csv(f'output/{filename}')
            print(f"\n=== {filename} ===")
            print(f"Total rows: {len(df)}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Check for date columns
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            print(f"Date columns found: {date_cols}")
            
            for col in date_cols:
                non_null_count = df[col].notna().sum()
                print(f"{col}: {non_null_count}/{len(df)} non-null values")
                
                if non_null_count > 0:
                    sample_dates = df[col].dropna().head(5).tolist()
                    print(f"  Sample dates: {sample_dates}")
                    
                    # Check if they're properly formatted
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        valid_dates = df[col].dropna()
                        if len(valid_dates) > 0:
                            print(f"  Date range: {valid_dates.min()} to {valid_dates.max()}")
                        else:
                            print("  No valid datetime objects found")
                    except Exception as e:
                        print(f"  Error parsing dates: {e}")
        
        except Exception as e:
            print(f"Error checking {filename}: {e}")
    
    print("\n" + "="*60)
    print("✅ Date verification completed!")

if __name__ == "__main__":
    verify_extracted_dates()
