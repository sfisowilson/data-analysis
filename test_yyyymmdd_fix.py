#!/usr/bin/env python3
"""
Test the new YYYYMMDD date processing fix
"""

import pandas as pd
import numpy as np

def test_yyyymmdd_processing():
    print("=== TESTING YYYYMMDD DATE PROCESSING FIX ===")
    
    # Load original Excel file
    try:
        df = pd.read_excel('Data Hand-Over/HR995grn.xlsx')
        print(f"Loaded GRN Excel data: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        
        # Check GRN Date column
        if 'GRN Date' in df.columns:
            print(f"\n--- Testing GRN Date column ---")
            grn_dates = df['GRN Date'].dropna().head(10)
            print(f"Sample GRN Date values: {grn_dates.tolist()}")
            
            # Apply the new processing logic
            col = 'GRN Date'
            numeric_dates = pd.to_numeric(df[col], errors='coerce')
            df[f'{col}_converted'] = pd.NaT
            
            for idx in numeric_dates.dropna().head(10).index:
                try:
                    date_val = int(numeric_dates.loc[idx])
                    date_str = str(date_val)
                    
                    if len(date_str) == 8:  # YYYYMMDD format
                        year = int(date_str[:4])
                        month = int(date_str[4:6])
                        day = int(date_str[6:8])
                        
                        if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                            df.loc[idx, f'{col}_converted'] = pd.Timestamp(year=year, month=month, day=day)
                            print(f"  {date_val} -> {year}-{month:02d}-{day:02d} ✓")
                        
                except Exception as e:
                    print(f"  Error converting {date_val}: {e}")
            
            # Show results
            converted_count = df[f'{col}_converted'].notna().sum()
            total_count = len(df)
            print(f"\nConversion results: {converted_count}/{total_count} dates converted successfully")
            
            if converted_count > 0:
                print("Sample converted dates:")
                sample_converted = df[[col, f'{col}_converted']].dropna(subset=[f'{col}_converted']).head(5)
                print(sample_converted)
        
        print("\n" + "="*60)
        print("✅ YYYYMMDD date processing test completed!")
        
    except Exception as e:
        print(f"❌ Error testing YYYYMMDD processing: {e}")

if __name__ == "__main__":
    test_yyyymmdd_processing()
