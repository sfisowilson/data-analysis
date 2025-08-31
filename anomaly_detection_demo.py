#!/usr/bin/env python3
"""
Anomaly Detection Demo
Quick showcase of the new anomaly detection features in the enhanced dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def demo_anomaly_detection():
    """Demonstrate the anomaly detection capabilities."""
    print("🚨 ANOMALY DETECTION DEMO")
    print("=" * 50)
    
    # Load data
    output_folder = Path("output")
    grn_df = pd.read_csv(output_folder / "hr995_grn.csv")
    issue_df = pd.read_csv(output_folder / "hr995_issue.csv")
    
    print(f"📊 Data Loaded:")
    print(f"   - GRN Records: {len(grn_df):,}")
    print(f"   - Issue Records: {len(issue_df):,}")
    print()
    
    # 1. Financial Anomalies Demo
    print("💸 FINANCIAL ANOMALY DETECTION")
    print("-" * 30)
    
    if 'gross_value' in grn_df.columns:
        # High-value outliers
        Q1 = grn_df['gross_value'].quantile(0.25)
        Q3 = grn_df['gross_value'].quantile(0.75)
        IQR = Q3 - Q1
        outlier_threshold = Q3 + 1.5 * IQR
        
        outliers = grn_df[grn_df['gross_value'] > outlier_threshold]
        total_outlier_value = outliers['gross_value'].sum()
        
        print(f"🔍 High-Value Transaction Analysis:")
        print(f"   - Outlier Threshold: R{outlier_threshold:,.2f}")
        print(f"   - High-Value Transactions: {len(outliers)}")
        print(f"   - Total Outlier Value: R{total_outlier_value:,.2f}")
        print(f"   - Largest Transaction: R{outliers['gross_value'].max():,.2f}")
        
        if len(outliers) > 0:
            print(f"   🚨 ALERT: {len(outliers)} transactions exceed normal spending patterns!")
        print()
    
    # 2. Volume Anomalies Demo
    print("📊 VOLUME ANOMALY DETECTION")
    print("-" * 30)
    
    if 'grn_qty' in grn_df.columns:
        valid_grn = grn_df[grn_df['grn_qty'] > 0]
        Q1_qty = valid_grn['grn_qty'].quantile(0.25)
        Q3_qty = valid_grn['grn_qty'].quantile(0.75)
        IQR_qty = Q3_qty - Q1_qty
        qty_threshold = Q3_qty + 2 * IQR_qty
        
        qty_outliers = valid_grn[valid_grn['grn_qty'] > qty_threshold]
        
        print(f"📦 Quantity Analysis:")
        print(f"   - Normal Quantity Range: 1 - {qty_threshold:,.0f}")
        print(f"   - Unusual Quantities Detected: {len(qty_outliers)}")
        print(f"   - Largest Quantity: {qty_outliers['grn_qty'].max():,.0f}" if len(qty_outliers) > 0 else "   - Largest Quantity: Normal range")
        
        if len(qty_outliers) > 0:
            print(f"   ⚠️ WARNING: {len(qty_outliers)} transactions have unusually high quantities!")
        print()
    
    # 3. Time-based Anomalies Demo
    print("⏰ TIME-BASED ANOMALY DETECTION")
    print("-" * 30)
    
    if 'grn_date' in grn_df.columns:
        grn_df_copy = grn_df.copy()
        grn_df_copy['grn_date'] = pd.to_datetime(grn_df_copy['grn_date'], errors='coerce')
        grn_df_copy = grn_df_copy.dropna(subset=['grn_date'])
        
        if len(grn_df_copy) > 0:
            grn_df_copy['is_weekend'] = grn_df_copy['grn_date'].dt.dayofweek >= 5
            weekend_transactions = grn_df_copy[grn_df_copy['is_weekend']]
            weekend_pct = (len(weekend_transactions) / len(grn_df_copy)) * 100
            
            print(f"📅 Weekend Activity Analysis:")
            print(f"   - Total Transactions: {len(grn_df_copy):,}")
            print(f"   - Weekend Transactions: {len(weekend_transactions):,}")
            print(f"   - Weekend Activity: {weekend_pct:.1f}%")
            
            if len(weekend_transactions) > 0:
                weekend_value = weekend_transactions['gross_value'].sum() if 'gross_value' in weekend_transactions.columns else 0
                print(f"   - Weekend Transaction Value: R{weekend_value:,.2f}")
                print(f"   🚨 ALERT: Business activity detected on weekends!")
            else:
                print(f"   ✅ No weekend activity detected")
            print()
    
    # 4. Pattern Anomalies Demo
    print("🎯 PATTERN ANOMALY DETECTION")
    print("-" * 30)
    
    # Stock level analysis
    if len(grn_df) > 0 and len(issue_df) > 0:
        item_col_grn = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
        item_col_issue = 'item_no' if 'item_no' in issue_df.columns else 'item_code'
        qty_col_issue = 'issue_qty' if 'issue_qty' in issue_df.columns else 'qty'
        
        if (item_col_grn in grn_df.columns and item_col_issue in issue_df.columns and 
            'grn_qty' in grn_df.columns and qty_col_issue in issue_df.columns):
            
            # Calculate stock balances
            grn_totals = grn_df.groupby(item_col_grn)['grn_qty'].sum().reset_index()
            grn_totals.columns = ['item_code', 'total_received']
            
            issue_totals = issue_df.groupby(item_col_issue)[qty_col_issue].sum().reset_index()
            issue_totals.columns = ['item_code', 'total_issued']
            
            stock_balance = grn_totals.merge(issue_totals, on='item_code', how='outer').fillna(0)
            stock_balance['current_stock'] = stock_balance['total_received'] - stock_balance['total_issued']
            
            negative_stock = stock_balance[stock_balance['current_stock'] < 0]
            zero_stock = stock_balance[stock_balance['current_stock'] == 0]
            
            print(f"📦 Stock Balance Analysis:")
            print(f"   - Total Items Analyzed: {len(stock_balance):,}")
            print(f"   - Items with Negative Stock: {len(negative_stock):,}")
            print(f"   - Items with Zero Stock: {len(zero_stock):,}")
            
            if len(negative_stock) > 0:
                print(f"   🚨 CRITICAL: {len(negative_stock)} items have impossible negative stock levels!")
                print(f"   📋 Most Negative: {negative_stock['current_stock'].min():,.0f} units")
            else:
                print(f"   ✅ No negative stock levels detected")
            print()
    
    # 5. Multi-supplier analysis
    if 'supplier_name' in grn_df.columns:
        item_col = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
        if item_col in grn_df.columns:
            supplier_item_counts = grn_df.groupby(item_col)['supplier_name'].nunique().reset_index()
            supplier_item_counts.columns = ['item_code', 'supplier_count']
            
            multi_supplier_items = supplier_item_counts[supplier_item_counts['supplier_count'] > 3]
            
            print(f"🏪 Supplier Relationship Analysis:")
            print(f"   - Total Items: {len(supplier_item_counts):,}")
            print(f"   - Items with Multiple Suppliers: {len(multi_supplier_items):,}")
            print(f"   - Max Suppliers per Item: {supplier_item_counts['supplier_count'].max()}")
            
            if len(multi_supplier_items) > 0:
                print(f"   ⚠️ WARNING: {len(multi_supplier_items)} items have excessive supplier diversity!")
                print(f"   💡 Consider supplier consolidation for better quality control")
            else:
                print(f"   ✅ Supplier relationships appear well-managed")
            print()
    
    # Summary
    print("📋 ANOMALY DETECTION SUMMARY")
    print("=" * 50)
    print("✅ Financial anomaly detection: HIGH-VALUE OUTLIERS identified")
    print("✅ Volume anomaly detection: QUANTITY OUTLIERS analyzed")
    print("✅ Time-based anomaly detection: WEEKEND ACTIVITY monitored")
    print("✅ Pattern anomaly detection: STOCK LEVELS & SUPPLIER PATTERNS reviewed")
    print()
    print("🚨 KEY BENEFITS:")
    print("   - Proactive risk identification")
    print("   - Data quality monitoring")
    print("   - Operational efficiency insights")
    print("   - Fraud detection capabilities")
    print("   - Supplier relationship optimization")
    print()
    print("🌐 Access full anomaly detection dashboard at:")
    print("   http://localhost:8502 → 🚨 Anomaly Detection tab")
    print()
    print("🎯 ANOMALY DETECTION IS NOW LIVE IN YOUR ENHANCED DASHBOARD!")

if __name__ == "__main__":
    try:
        demo_anomaly_detection()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure you're in the correct directory and data files exist.")
