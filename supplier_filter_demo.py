#!/usr/bin/env python3
"""
Demonstration of Supplier Filtering Functionality
Shows available suppliers and sample filtered data.
"""

import pandas as pd
from pathlib import Path

def demonstrate_supplier_filtering():
    """Demonstrate the supplier filtering functionality."""
    print("🏪 SUPPLIER FILTERING DEMONSTRATION")
    print("=" * 60)
    
    # Load GRN data
    grn_file = Path("output/hr995_grn.csv")
    if not grn_file.exists():
        print("❌ GRN data file not found. Please run the data processor first.")
        return
    
    grn_df = pd.read_csv(grn_file)
    
    # Show available suppliers
    if 'supplier_name' in grn_df.columns:
        suppliers = grn_df['supplier_name'].value_counts()
        
        print(f"\n📊 AVAILABLE SUPPLIERS ({len(suppliers)} total):")
        print("-" * 40)
        
        # Show top 10 suppliers by transaction count
        top_suppliers = suppliers.head(10)
        for i, (supplier, count) in enumerate(top_suppliers.items(), 1):
            # Get value stats for this supplier
            supplier_data = grn_df[grn_df['supplier_name'] == supplier]
            if 'nett_grn_amt' in supplier_data.columns:
                total_value = pd.to_numeric(supplier_data['nett_grn_amt'], errors='coerce').sum()
                avg_value = pd.to_numeric(supplier_data['nett_grn_amt'], errors='coerce').mean()
                print(f"{i:2d}. {supplier}")
                print(f"     📈 Transactions: {count:,}")
                print(f"     💰 Total Value: R{total_value:,.0f}")
                print(f"     📊 Avg Value: R{avg_value:,.0f}")
                print()
            else:
                print(f"{i:2d}. {supplier} ({count:,} transactions)")
        
        # Demonstrate filtering for a specific supplier
        if len(top_suppliers) > 0:
            demo_supplier = top_suppliers.index[0]
            print(f"\n🔍 FILTERING EXAMPLE - Supplier: '{demo_supplier}'")
            print("-" * 60)
            
            # Filter data for this supplier
            filtered_data = grn_df[grn_df['supplier_name'] == demo_supplier]
            
            print(f"📋 Original dataset: {len(grn_df):,} records")
            print(f"🎯 Filtered dataset: {len(filtered_data):,} records")
            print(f"📊 Reduction: {((len(grn_df) - len(filtered_data)) / len(grn_df) * 100):.1f}%")
            
            # Show sample filtered data
            if not filtered_data.empty:
                print(f"\n📄 SAMPLE FILTERED DATA (First 5 records):")
                print("-" * 60)
                
                # Show key columns
                display_cols = []
                for col in ['date', 'item_no', 'description', 'quantity', 'nett_grn_amt']:
                    if col in filtered_data.columns:
                        display_cols.append(col)
                
                if display_cols:
                    sample_data = filtered_data[display_cols].head(5)
                    print(sample_data.to_string(index=False))
                
                # Show time range
                if 'date' in filtered_data.columns:
                    filtered_data['date'] = pd.to_datetime(filtered_data['date'], errors='coerce')
                    date_range = filtered_data['date'].dropna()
                    if not date_range.empty:
                        print(f"\n📅 Date Range: {date_range.min().strftime('%Y-%m-%d')} to {date_range.max().strftime('%Y-%m-%d')}")
                
                # Show unique items
                if 'item_no' in filtered_data.columns:
                    unique_items = filtered_data['item_no'].nunique()
                    print(f"🔢 Unique Items: {unique_items:,}")
    
    else:
        print("❌ No supplier_name column found in the data")
    
    print(f"\n" + "=" * 60)
    print("🎯 HOW TO USE SUPPLIER FILTERING IN DASHBOARD:")
    print("1. Launch: python -m streamlit run enhanced_dashboard.py")
    print("2. Look for '🏪 Supplier Filter' in the left sidebar")
    print("3. Select any supplier from the dropdown")
    print("4. All charts and analysis will update automatically")
    print("5. Filter applies to ALL tabs: Financial, Inventory, Supplier, etc.")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_supplier_filtering()
