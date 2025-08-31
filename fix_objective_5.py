#!/usr/bin/env python3
"""
Fix Objective 5 report: Stock balances by year.
"""

import pandas as pd
from pathlib import Path

def fix_objective_5():
    """Generate Objective 5: Stock balances by year."""
    print("🔧 Fixing Objective 5 report...")
    
    output_folder = Path("output")
    
    # Load stock balance files
    stock_files = [
        "individual_final_stock_listing_2023.csv",
        "individual_final_stock_list_2324.csv",
        "individual_stock_adjustment_item_2024.csv"
    ]
    
    all_stock_data = []
    
    for file in stock_files:
        file_path = output_folder / file
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                
                # Add year info
                if '2023' in file:
                    df['year'] = 2023
                elif '2024' in file or '2324' in file:
                    df['year'] = 2024
                
                df['source_file'] = file
                all_stock_data.append(df)
                print(f"  ✅ Loaded {len(df):,} records from {file}")
            except Exception as e:
                print(f"  ❌ Error loading {file}: {e}")
    
    if all_stock_data:
        # Combine stock data
        combined_df = pd.concat(all_stock_data, ignore_index=True)
        
        # Create year-based summary
        stock_summary = combined_df.groupby(['year', 'source_file']).agg({
            combined_df.columns[0]: 'count'  # Count records
        }).reset_index()
        
        stock_summary.columns = ['year', 'source_file', 'record_count']
        
        # Save
        output_file = output_folder / "objective_5_stock_balances_by_year.csv"
        stock_summary.to_csv(output_file, index=False)
        
        print(f"  ✅ Objective 5 report saved: {output_file}")
        print(f"  📊 Generated {len(stock_summary):,} year-based records")
        return stock_summary
    else:
        print("  ❌ No stock files found!")
        return None

if __name__ == "__main__":
    fix_objective_5()
