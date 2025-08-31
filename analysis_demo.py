#!/usr/bin/env python3
"""
Stock Data Analysis Demo Script
This script demonstrates the analytical capabilities of the Stock Data Processor.
"""

import pandas as pd
import os
from pathlib import Path

def analyze_generated_reports():
    """Analyze the generated reports and show key insights."""
    
    output_folder = Path("output")
    
    if not output_folder.exists():
        print("Error: Output folder not found. Please run the stock_data_processor.py first.")
        return
    
    print("="*60)
    print("STOCK DATA ANALYSIS SUMMARY")
    print("="*60)
    
    # 1. Master Data Summary
    if (output_folder / "all_stock_data.csv").exists():
        master_df = pd.read_csv(output_folder / "all_stock_data.csv")
        print(f"\n📊 MASTER DATA OVERVIEW:")
        print(f"   • Total records processed: {len(master_df):,}")
        print(f"   • Total columns: {len(master_df.columns)}")
        print(f"   • Unique source files: {master_df['source_file'].nunique()}")
        print(f"   • File types processed: {', '.join(master_df['file_type'].dropna().unique())}")
    
    # 2. HR995 Data Analysis
    hr995_files = ['hr995_grn.csv', 'hr995_issue.csv', 'hr995_voucher.csv', 'hr995_redundant.csv']
    hr995_summary = {}
    
    print(f"\n📋 HR995 TRANSACTION SUMMARY:")
    for file in hr995_files:
        if (output_folder / file).exists():
            df = pd.read_csv(output_folder / file)
            report_type = file.replace('.csv', '').replace('hr995_', '').upper()
            hr995_summary[report_type] = len(df)
            print(f"   • {report_type:12}: {len(df):,} transactions")
    
    # 3. Stock Balance Analysis
    if (output_folder / "stock_adjustments.csv").exists():
        stock_df = pd.read_csv(output_folder / "stock_adjustments.csv")
        print(f"\n📦 STOCK BALANCE SUMMARY:")
        print(f"   • Stock records: {len(stock_df):,}")
        if 'source_file' in stock_df.columns:
            print(f"   • Stock files processed: {stock_df['source_file'].nunique()}")
    
    # 4. Supplier Analysis
    if (output_folder / "suppliers.csv").exists():
        supplier_df = pd.read_csv(output_folder / "suppliers.csv")
        print(f"\n🏪 SUPPLIER SUMMARY:")
        print(f"   • Supplier records: {len(supplier_df):,}")
    
    # 5. Objective Reports Analysis
    print(f"\n🎯 ANALYTICAL REPORTS GENERATED:")
    
    objective_files = [
        ("objective_1_item_frequency_by_supplier.csv", "Item Frequency Analysis"),
        ("objective_2_stock_audit_trail.csv", "Stock Audit Trail"),
        ("objective_3_hr995_report.csv", "HR995 Comprehensive Report"),
        ("objective_4_end_to_end_process.csv", "End-to-End Process Report"),
        ("objective_5_stock_balances_by_year.csv", "Stock Balances by Year")
    ]
    
    for file, description in objective_files:
        if (output_folder / file).exists():
            df = pd.read_csv(output_folder / file)
            print(f"   • {description}: {len(df):,} records")
        else:
            print(f"   • {description}: Not generated")
    
    print("\n" + "="*60)
    print("NEXT STEPS & RECOMMENDATIONS:")
    print("="*60)
    print("1. Review the master consolidated file (all_stock_data.csv)")
    print("2. Analyze individual report types for specific insights")
    print("3. Use the objective reports for business intelligence")
    print("4. Cross-reference audit trail with financial records")
    print("5. Validate stock balances against physical counts")
    
    return hr995_summary

def generate_quick_insights():
    """Generate quick insights from the processed data."""
    
    output_folder = Path("output")
    
    # Quick insight: HR995 GRN analysis
    if (output_folder / "hr995_grn.csv").exists():
        grn_df = pd.read_csv(output_folder / "hr995_grn.csv")
        
        print(f"\n💡 QUICK INSIGHTS - GRN DATA:")
        
        # Top suppliers by transaction count
        if 'supplier_name' in grn_df.columns:
            top_suppliers = grn_df['supplier_name'].value_counts().head(5)
            print(f"   Top 5 Suppliers by GRN Count:")
            for supplier, count in top_suppliers.items():
                print(f"   • {supplier}: {count:,} GRNs")
        
        # Total value analysis
        if 'nett_grn_amt' in grn_df.columns:
            grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
            total_value = grn_df['nett_grn_amt'].sum()
            print(f"   Total GRN Value: R{total_value:,.2f}")
    
    # Quick insight: Stock movement
    if (output_folder / "objective_2_stock_audit_trail.csv").exists():
        audit_df = pd.read_csv(output_folder / "objective_2_stock_audit_trail.csv")
        
        print(f"\n📊 QUICK INSIGHTS - STOCK MOVEMENT:")
        print(f"   • Total stock movements tracked: {len(audit_df):,}")
        
        if 'transaction_type' in audit_df.columns:
            movement_types = audit_df['transaction_type'].value_counts()
            for movement_type, count in movement_types.items():
                print(f"   • {movement_type}: {count:,} transactions")

def main():
    """Main function to run the analysis demo."""
    
    print("Stock Data Analysis Demo")
    print("This script analyzes the reports generated by stock_data_processor.py")
    print("-" * 60)
    
    # Check if reports exist
    output_folder = Path("output")
    if not output_folder.exists():
        print("❌ Output folder not found!")
        print("Please run 'python stock_data_processor.py' first to generate reports.")
        return
    
    # Run analysis
    hr995_data = analyze_generated_reports()
    generate_quick_insights()
    
    print(f"\n📁 All reports are available in the '{output_folder}' folder.")
    print("You can open these CSV files in Excel or any data analysis tool.")

if __name__ == "__main__":
    main()
