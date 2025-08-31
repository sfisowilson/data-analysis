#!/usr/bin/env python3
"""
Fix and regenerate objective reports with correct column mapping.
"""

import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

def fix_objective_1_report():
    """Generate proper Objective 1 report: Item frequency by supplier."""
    print("🔧 Fixing Objective 1 report...")
    
    output_folder = Path("output")
    
    # Load HR995 data files
    hr995_files = [
        "hr995_grn.csv",
        "hr995_issue.csv", 
        "hr995_voucher.csv"
    ]
    
    all_data = []
    
    for file in hr995_files:
        file_path = output_folder / file
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                df['source_type'] = file.replace('.csv', '').replace('hr995_', '').upper()
                all_data.append(df)
                print(f"  ✅ Loaded {len(df):,} records from {file}")
            except Exception as e:
                print(f"  ❌ Error loading {file}: {e}")
    
    if not all_data:
        print("  ❌ No data files found!")
        return
    
    # Combine all data
    master_df = pd.concat(all_data, ignore_index=True)
    print(f"  📊 Combined data: {len(master_df):,} total records")
    
    # Check available columns
    print(f"  📋 Available columns: {list(master_df.columns)}")
    
    # Map columns correctly
    item_col = None
    supplier_col = None
    description_col = None
    quantity_col = None
    date_col = None
    
    # Find the right column names
    for col in master_df.columns:
        if 'item' in col.lower() and 'no' in col.lower():
            item_col = col
        elif 'supplier' in col.lower() and 'name' in col.lower():
            supplier_col = col
        elif 'description' in col.lower():
            description_col = col
        elif 'quantity' in col.lower() and 'return' not in col.lower():
            quantity_col = col
        elif 'date' in col.lower():
            date_col = col
    
    print(f"  🎯 Using columns: item={item_col}, supplier={supplier_col}, quantity={quantity_col}, date={date_col}")
    
    if not all([item_col, supplier_col, quantity_col]):
        print("  ❌ Required columns not found!")
        return
    
    # Filter for 2022-2025 if date column exists
    if date_col:
        master_df[date_col] = pd.to_datetime(master_df[date_col], errors='coerce')
        # Filter by financial period or date
        if 'fin_period' in master_df.columns:
            # Use financial period (format: YYYYMM)
            master_df['fin_period'] = pd.to_numeric(master_df['fin_period'], errors='coerce')
            mask = (master_df['fin_period'] >= 202201) & (master_df['fin_period'] <= 202512)
            filtered_df = master_df[mask]
        else:
            mask = (master_df[date_col].dt.year >= 2022) & (master_df[date_col].dt.year <= 2025)
            filtered_df = master_df[mask]
    else:
        filtered_df = master_df
    
    print(f"  📅 Filtered data (2022-2025): {len(filtered_df):,} records")
    
    # Remove null values
    filtered_df = filtered_df.dropna(subset=[item_col, supplier_col])
    print(f"  🧹 After removing nulls: {len(filtered_df):,} records")
    
    # Group by item and supplier
    group_cols = [item_col, supplier_col]
    if description_col:
        group_cols.append(description_col)
    
    group_cols.append('source_type')  # Add source type for tracking
    
    # Create frequency analysis
    agg_dict = {quantity_col: ['count', 'sum', 'mean']}
    if date_col:
        agg_dict[date_col] = ['min', 'max']
    
    frequency_analysis = filtered_df.groupby(group_cols).agg(agg_dict).round(2)
    
    # Flatten column names
    if date_col:
        frequency_analysis.columns = ['request_count', 'total_quantity', 'avg_quantity', 'first_request', 'last_request']
    else:
        frequency_analysis.columns = ['request_count', 'total_quantity', 'avg_quantity']
    
    frequency_analysis = frequency_analysis.reset_index()
    frequency_analysis = frequency_analysis.sort_values('request_count', ascending=False)
    
    # Rename columns for clarity
    column_mapping = {
        item_col: 'item_code',
        supplier_col: 'supplier_name'
    }
    if description_col:
        column_mapping[description_col] = 'item_description'
    
    frequency_analysis = frequency_analysis.rename(columns=column_mapping)
    
    # Save the report
    output_file = output_folder / "objective_1_item_frequency_by_supplier.csv"
    frequency_analysis.to_csv(output_file, index=False)
    
    print(f"  ✅ Objective 1 report saved: {output_file}")
    print(f"  📊 Generated {len(frequency_analysis):,} item-supplier frequency records")
    
    # Show top 10 results
    print(f"\n  🔝 Top 10 Most Frequently Requested Items:")
    print(frequency_analysis.head(10)[['item_code', 'supplier_name', 'request_count', 'total_quantity']].to_string(index=False))
    
    return frequency_analysis

def fix_other_objectives():
    """Fix other objective reports if they're empty."""
    print("\n🔧 Checking other objective reports...")
    
    output_folder = Path("output")
    
    # Check each objective file
    objective_files = [
        "objective_2_stock_audit_trail.csv",
        "objective_3_hr995_report.csv", 
        "objective_4_end_to_end_process.csv",
        "objective_5_stock_balances_by_year.csv"
    ]
    
    for file in objective_files:
        file_path = output_folder / file
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                if len(df) > 0:
                    print(f"  ✅ {file}: {len(df):,} records")
                else:
                    print(f"  ⚠️  {file}: Empty - needs regeneration")
            except Exception as e:
                print(f"  ❌ {file}: Error reading - {e}")
        else:
            print(f"  ❌ {file}: Missing")

def main():
    """Main function to fix objective reports."""
    print("🎯 FIXING OBJECTIVE REPORTS")
    print("=" * 50)
    
    # Fix Objective 1
    obj1_result = fix_objective_1_report()
    
    # Check others
    fix_other_objectives()
    
    print("\n" + "=" * 50)
    print("✅ Objective report fixing completed!")
    
    if obj1_result is not None:
        print(f"🎯 Objective 1 now has {len(obj1_result):,} records")
    
    print("🔄 Try refreshing the dashboard Data Tables tab")

if __name__ == "__main__":
    main()
