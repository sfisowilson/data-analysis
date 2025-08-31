#!/usr/bin/env python3
"""
Test the enhanced date processing functionality for both YYYYMM and YYYYMMDD formats
"""

import pandas as pd
import sys
sys.path.append('.')

def test_date_processing():
    print("=== TESTING ENHANCED DATE PROCESSING ===")
    print("Testing both YYYYMM (fin_period) and YYYYMMDD (date columns) formats")
    
    # Test GRN data
    try:
        df = pd.read_csv('output/hr995_grn.csv', low_memory=False)
        print(f"\nLoaded GRN data: {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        
        # Test fin_period conversion (YYYYMM format)
        if 'fin_period' in df.columns:
            fin_period_series = pd.to_numeric(df['fin_period'], errors='coerce')
            valid_periods = fin_period_series.dropna()
            print(f"\n📅 FIN_PERIOD (YYYYMM format):")
            print(f"Valid periods found: {len(valid_periods)}")
            
            if len(valid_periods) > 0:
                print("Sample periods:", valid_periods.head(5).tolist())
                
                # Test conversion
                sample_period = valid_periods.iloc[0]
                year = int(sample_period // 100)
                month = int(sample_period % 100)
                print(f"Sample conversion: {sample_period} -> {year}-{month:02d}")
        
        # Test YYYYMMDD date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        print(f"\n📅 DATE COLUMNS (should be YYYYMMDD format):")
        print(f"Date columns found: {date_columns}")
        
        for col in date_columns:
            if col in df.columns:
                print(f"\n--- {col} ---")
                sample_values = df[col].dropna().head(5)
                print(f"Sample raw values: {sample_values.tolist()}")
                
                # Check if they look like YYYYMMDD
                numeric_dates = pd.to_numeric(df[col], errors='coerce')
                valid_numeric = numeric_dates.dropna()
                
                if len(valid_numeric) > 0:
                    sample_numeric = valid_numeric.head(3)
                    print(f"Sample numeric values: {sample_numeric.tolist()}")
                    
                    # Test YYYYMMDD conversion
                    for val in sample_numeric:
                        try:
                            date_str = str(int(val))
                            if len(date_str) == 8:
                                year = int(date_str[:4])
                                month = int(date_str[4:6])
                                day = int(date_str[6:8])
                                print(f"  {val} -> {year}-{month:02d}-{day:02d}")
                            else:
                                print(f"  {val} -> Invalid length ({len(date_str)} digits)")
                        except Exception as e:
                            print(f"  {val} -> Error: {e}")
        
        print("\n" + "="*60)
        print("✅ Enhanced date processing test completed!")
        print("\nFormat Summary:")
        print("- fin_period: YYYYMM (e.g., 202211 = 2022-11)")
        print("- date columns: YYYYMMDD (e.g., 20221115 = 2022-11-15)")
        
    except Exception as e:
        print(f"❌ Error testing date processing: {e}")

if __name__ == "__main__":
    test_date_processing()
