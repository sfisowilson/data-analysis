#!/usr/bin/env python3
"""
Analyze HR185 INV-CHQ payment pairs
"""

import pandas as pd
import numpy as np

def analyze_inv_chq_pairs():
    """Find INV-CHQ pairs in HR185 data that represent complete payment cycles."""
    
    # Load HR185 data
    hr185_df = pd.read_csv("output/individual_hr185_transactions.csv")
    
    print("📊 HR185 INV-CHQ Payment Pair Analysis")
    print("=" * 50)
    
    # Convert date and amount for comparison
    hr185_df['transaction_date'] = pd.to_datetime(hr185_df['transaction_date'])
    hr185_df['amount'] = pd.to_numeric(hr185_df['amount'], errors='coerce')
    
    # Sort by supplier, date, and transaction type for sequential analysis
    hr185_df = hr185_df.sort_values(['supplier_code', 'transaction_date', 'transaction_type'])
    
    # Find suppliers with both INV and CHQ transactions
    suppliers_with_inv = set(hr185_df[hr185_df['transaction_type'] == 'INV']['supplier_code'])
    suppliers_with_chq = set(hr185_df[hr185_df['transaction_type'] == 'CHQ']['supplier_code'])
    common_suppliers = suppliers_with_inv.intersection(suppliers_with_chq)
    
    print(f"🔍 Found {len(common_suppliers)} suppliers with both INV and CHQ transactions")
    
    # Find INV-CHQ pairs within each supplier
    inv_chq_pairs = []
    
    for supplier_code in common_suppliers:
        supplier_data = hr185_df[hr185_df['supplier_code'] == supplier_code].copy()
        supplier_data = supplier_data.sort_values(['transaction_date', 'transaction_type'])
        
        # Find matching INV-CHQ pairs within supplier
        for i, inv_row in supplier_data[supplier_data['transaction_type'] == 'INV'].iterrows():
            # Look for CHQ transactions with same date and amount
            matching_chq = supplier_data[
                (supplier_data['transaction_type'] == 'CHQ') &
                (supplier_data['transaction_date'] == inv_row['transaction_date']) &
                (abs(supplier_data['amount'] - inv_row['amount']) < 0.01)
            ]
            
            for j, chq_row in matching_chq.iterrows():
                inv_chq_pairs.append({
                    'supplier_code': supplier_code,
                    'supplier_name': inv_row['supplier_name'],
                    'date': inv_row['transaction_date'],
                    'inv_reference': inv_row['reference'],
                    'chq_reference': chq_row['reference'],
                    'amount': inv_row['amount'],
                    'inv_normalized': inv_row.get('reference_normalized', ''),
                    'chq_normalized': chq_row.get('reference_normalized', '')
                })
    
    pairs_df = pd.DataFrame(inv_chq_pairs)
    
    if not pairs_df.empty:
        print(f"✅ Found {len(pairs_df)} INV-CHQ payment pairs")
        print()
        
        print("🔍 Sample INV-CHQ Pairs:")
        sample_pairs = pairs_df.head(10)
        for _, pair in sample_pairs.iterrows():
            print(f"📋 {pair['supplier_name'][:40]:<40}")
            print(f"   Date: {pair['date'].strftime('%Y-%m-%d')}")
            print(f"   INV: {pair['inv_reference']} → CHQ: {pair['chq_reference']}")
            print(f"   Amount: R {pair['amount']:,.2f}")
            print(f"   INV Normalized: {pair['inv_normalized']} → CHQ Normalized: {pair['chq_normalized']}")
            print()
        
        # Check if CHQ references can be linked back to GRN
        print("🔗 CHQ Reference Analysis:")
        print(f"CHQ reference range: {pairs_df['chq_normalized'].min()} to {pairs_df['chq_normalized'].max()}")
        print(f"CHQ reference pattern: All numeric? {pairs_df['chq_reference'].str.isdigit().all()}")
        
        # Save results
        pairs_df.to_csv("output/hr185_inv_chq_pairs.csv", index=False)
        print(f"💾 Saved {len(pairs_df)} pairs to output/hr185_inv_chq_pairs.csv")
        
        return pairs_df
    else:
        print("❌ No INV-CHQ pairs found")
        return pd.DataFrame()

def analyze_chq_grn_linking(pairs_df):
    """Analyze if CHQ references can link to GRN voucher numbers."""
    
    if pairs_df.empty:
        return
    
    print("\n" + "=" * 50)
    print("🔗 CHQ → GRN Voucher Linking Analysis")
    print("=" * 50)
    
    # Load GRN data to check voucher linking
    try:
        grn_df = pd.read_csv("output/individual_hr995grn.csv")
        
        if 'voucher' in grn_df.columns:
            grn_vouchers = set(grn_df['voucher'].astype(str).str.strip())
            chq_refs = set(pairs_df['chq_reference'].astype(str).str.strip())
            
            # Direct matches
            direct_matches = chq_refs & grn_vouchers
            
            print(f"CHQ references: {len(chq_refs)}")
            print(f"GRN vouchers: {len(grn_vouchers)}")
            print(f"Direct CHQ→GRN matches: {len(direct_matches)}")
            
            if direct_matches:
                print("\n✅ Sample CHQ→GRN Voucher Matches:")
                for match in list(direct_matches)[:5]:
                    chq_row = pairs_df[pairs_df['chq_reference'].astype(str) == match].iloc[0]
                    grn_row = grn_df[grn_df['voucher'].astype(str) == match].iloc[0]
                    print(f"CHQ {match} → GRN Voucher {match}")
                    print(f"  Supplier: {chq_row['supplier_name']}")
                    print(f"  Amount: R {chq_row['amount']:,.2f}")
                    if 'supplier_name' in grn_row:
                        print(f"  GRN Supplier: {grn_row.get('supplier_name', 'N/A')}")
                    print()
        else:
            print("❌ No 'voucher' column found in GRN data")
            
    except FileNotFoundError:
        print("❌ GRN data file not found")

if __name__ == "__main__":
    pairs_df = analyze_inv_chq_pairs()
    analyze_chq_grn_linking(pairs_df)
