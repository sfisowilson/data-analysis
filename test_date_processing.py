#!/usr/bin/env python3
"""
Test the new date processing functionality
"""

import pandas as pd
import sys
sys.path.append('.')

def test_date_processing():
    print("=== TESTING NEW DATE PROCESSING ===")
    
    # Test GRN data
    try:
        df = pd.read_csv('output/hr995_grn.csv', low_memory=False)
        print(f"Loaded GRN data: {len(df)} rows")
        
        # Test fin_period conversion
        if 'fin_period' in df.columns:
            fin_period_series = pd.to_numeric(df['fin_period'], errors='coerce')
            valid_periods = fin_period_series.dropna()
            print(f"Valid periods found: {len(valid_periods)}")
            
            if len(valid_periods) > 0:
                print("Sample periods:", valid_periods.head(5).tolist())
                
                # Test conversion
                sample_period = valid_periods.iloc[0]
                year = int(sample_period // 100)
                month = int(sample_period % 100)
                print(f"Sample conversion: {sample_period} -> {year}-{month:02d}")
                
                # Test creating period_date
                df['period_date'] = pd.NaT
                for idx in valid_periods.head(10).index:
                    try:
                        year = int(valid_periods.loc[idx] // 100)
                        month = int(valid_periods.loc[idx] % 100)
                        if 1 <= month <= 12 and year >= 2000:
                            df.loc[idx, 'period_date'] = pd.Timestamp(year=year, month=month, day=1)
                    except Exception as e:
                        print(f"Error converting {valid_periods.loc[idx]}: {e}")
                
                # Test period_display
                df['period_display'] = df['period_date'].dt.strftime('%Y-%m')
                
                print("\nFirst 5 converted dates:")
                test_df = df[['fin_period', 'period_date', 'period_display']].head(10)
                print(test_df.dropna(subset=['period_date']))
        
        print("\n" + "="*50)
        print("✅ Date processing test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing date processing: {e}")

if __name__ == "__main__":
    test_date_processing()
