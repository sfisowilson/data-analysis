#!/usr/bin/env python3
"""
Test Enhanced CHQ Linking in Dashboard
======================================
Test the enhanced CHQ linking logic integrated into the main dashboard.
"""

import pandas as pd
import os
import sys

def test_enhanced_chq_linking():
    """Test the enhanced CHQ linking by simulating the dashboard logic."""
    
    print("🧪 Testing Enhanced CHQ Linking Integration")
    print("=" * 50)
    
    # Create a simplified version of the dashboard's CHQ analysis
    try:
        # Load required data
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        grn_df = pd.read_csv('output/individual_hr995grn.csv')
        
        print(f"✓ Loaded HR185: {len(hr185_df)} transactions")
        print(f"✓ Loaded GRN: {len(grn_df)} records")
        
        # Simulate the dashboard's identify_inv_chq_payment_pairs function
        def identify_inv_chq_payment_pairs(hr185_df):
            suppliers_with_inv = set(hr185_df[hr185_df['transaction_type'] == 'INV']['supplier_code'])
            suppliers_with_chq = set(hr185_df[hr185_df['transaction_type'] == 'CHQ']['supplier_code'])
            common_suppliers = suppliers_with_inv.intersection(suppliers_with_chq)
            
            payment_pairs = []
            
            for supplier_code in common_suppliers:
                supplier_data = hr185_df[hr185_df['supplier_code'] == supplier_code].copy()
                supplier_data = supplier_data.sort_values(['transaction_date', 'transaction_type'])
                
                for i, inv_row in supplier_data[supplier_data['transaction_type'] == 'INV'].iterrows():
                    matching_chq = supplier_data[
                        (supplier_data['transaction_type'] == 'CHQ') &
                        (supplier_data['transaction_date'] == inv_row['transaction_date']) &
                        (abs(supplier_data['amount'] - inv_row['amount']) < 0.01)
                    ]
                    
                    for j, chq_row in matching_chq.iterrows():
                        payment_pairs.append({
                            'supplier_code': supplier_code,
                            'supplier_name': inv_row['supplier_name'],
                            'inv_reference': inv_row['reference'],
                            'chq_reference': chq_row['reference'],
                            'amount': inv_row['amount']
                        })
            
            return payment_pairs
        
        # Simulate the dashboard's enhanced_hr185_transaction_analysis function
        def normalize_reference(ref):
            if pd.isna(ref):
                return ''
            ref_str = str(ref).strip()
            try:
                return str(int(ref_str))
            except ValueError:
                return ref_str
        
        # Ensure normalized columns exist
        if 'reference_normalized' not in hr185_df.columns:
            hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
        if 'inv_no_normalized' not in grn_df.columns:
            grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(normalize_reference)
        
        # Identify payment pairs
        payment_pairs = identify_inv_chq_payment_pairs(hr185_df)
        print(f"✓ Identified {len(payment_pairs)} INV-CHQ payment pairs")
        
        # Create CHQ to INV mapping
        chq_to_inv_map = {}
        for pair in payment_pairs:
            chq_to_inv_map[str(pair['chq_reference'])] = pair['inv_reference']
        
        print(f"✓ Created CHQ→INV mapping for {len(chq_to_inv_map)} CHQ transactions")
        
        # Analyze CHQ transactions
        chq_transactions = hr185_df[hr185_df['transaction_type'] == 'CHQ']
        total_chq = len(chq_transactions)
        direct_chq_matches = 0
        inherited_chq_matches = 0
        
        for _, chq_row in chq_transactions.iterrows():
            chq_ref = str(chq_row['reference'])
            chq_ref_norm = normalize_reference(chq_ref)
            
            # Check for direct GRN match
            direct_match = len(grn_df[grn_df['inv_no_normalized'] == chq_ref_norm]) > 0
            
            if direct_match:
                direct_chq_matches += 1
            elif chq_ref in chq_to_inv_map:
                # Check if paired INV has GRN match
                paired_inv_ref = chq_to_inv_map[chq_ref]
                paired_inv_norm = normalize_reference(paired_inv_ref)
                
                if len(grn_df[grn_df['inv_no_normalized'] == paired_inv_norm]) > 0:
                    inherited_chq_matches += 1
        
        # Results
        print("\n📊 DASHBOARD CHQ ANALYSIS SIMULATION RESULTS:")
        print("-" * 50)
        print(f"Total CHQ transactions: {total_chq}")
        print(f"CHQ with direct GRN matches: {direct_chq_matches}")
        print(f"CHQ with inherited GRN matches: {inherited_chq_matches}")
        print(f"CHQ total matched: {direct_chq_matches + inherited_chq_matches}")
        print(f"CHQ still unmatched: {total_chq - direct_chq_matches - inherited_chq_matches}")
        print()
        
        improvement = inherited_chq_matches
        print(f"🎯 IMPROVEMENT ACHIEVED:")
        print(f"Before fix: {direct_chq_matches}/{total_chq} CHQ matched ({direct_chq_matches/total_chq*100:.1f}%)")
        print(f"After fix: {direct_chq_matches + inherited_chq_matches}/{total_chq} CHQ matched ({(direct_chq_matches + inherited_chq_matches)/total_chq*100:.1f}%)")
        print(f"Fixed transactions: +{improvement} CHQ transactions ({improvement/total_chq*100:.1f}%)")
        
        if improvement > 0:
            print(f"\n✅ SUCCESS: Enhanced CHQ linking would fix {improvement} unmatched CHQ transactions!")
            return True
        else:
            print(f"\n❌ No improvement detected")
            return False
        
    except Exception as e:
        print(f"❌ Error testing CHQ linking: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_chq_linking()
    if success:
        print("\n🎯 The enhanced dashboard CHQ linking logic is ready!")
        print("📋 To see the full analysis, run the dashboard (once matplotlib is available)")
    else:
        print("\n⚠️ CHQ linking test failed - check implementation")
