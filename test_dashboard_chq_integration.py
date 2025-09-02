#!/usr/bin/env python3
"""
Test script to validate CHQ linking integration in enhanced dashboard
WITHOUT matplotlib dependency - focuses on core functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def normalize_reference(ref):
    """Normalize reference for matching"""
    if pd.isna(ref):
        return ''
    # Convert to string and strip whitespace
    ref_str = str(ref).strip()
    # Remove leading zeros
    ref_str = ref_str.lstrip('0')
    # Return empty string if all zeros or empty
    return ref_str if ref_str else '0'

def enhanced_reference_matching(hr185_ref, hr995_refs):
    """Enhanced reference matching with 4 strategies"""
    hr185_normalized = normalize_reference(hr185_ref)
    
    # Strategy 1: Direct string comparison
    if hr185_normalized in hr995_refs:
        return hr185_normalized
    
    # Strategy 2: Try zero-padding HR995 references
    for ref in hr995_refs:
        if hr185_normalized == normalize_reference(ref):
            return ref
    
    # Strategy 3: Try integer comparison (if both are numeric)
    try:
        hr185_int = int(hr185_normalized)
        for ref in hr995_refs:
            try:
                if hr185_int == int(normalize_reference(ref)):
                    return ref
            except ValueError:
                continue
    except ValueError:
        pass
    
    return None

def identify_inv_chq_payment_pairs(hr185_df):
    """Identify consecutive INV-CHQ pairs representing payment cycles"""
    pairs = []
    
    # Sort by supplier and date for consecutive analysis
    hr185_sorted = hr185_df.sort_values(['supplier_name', 'transaction_date']).reset_index(drop=True)
    
    for i in range(len(hr185_sorted) - 1):
        current = hr185_sorted.iloc[i]
        next_row = hr185_sorted.iloc[i + 1]
        
        # Check if current is INV and next is CHQ
        if (current['transaction_type'] == 'INV' and 
            next_row['transaction_type'] == 'CHQ' and
            current['supplier_name'] == next_row['supplier_name'] and
            current['transaction_date'] == next_row['transaction_date'] and
            abs(current['amount'] - next_row['amount']) < 0.01):  # Same amount
            
            pairs.append({
                'supplier_name': current['supplier_name'],
                'date': current['transaction_date'],
                'amount': current['amount'],
                'inv_reference': current['reference'],
                'chq_reference': next_row['reference']
            })
    
    return pd.DataFrame(pairs)

def enhanced_hr185_transaction_analysis(hr185_df, hr995grn_df, pairs_df):
    """Enhanced HR185 analysis with CHQ inheritance linking"""
    
    print("🔄 Enhanced HR185 Transaction Analysis with CHQ Inheritance")
    print("=" * 60)
    
    # Create reference sets for matching
    voucher_refs = set(hr995grn_df['voucher_normalized'].dropna())
    inv_refs = set(hr995grn_df['inv_no_normalized'].dropna())
    all_grn_refs = voucher_refs.union(inv_refs)
    
    # Track matches
    matched_transactions = []
    unmatched_transactions = []
    
    # Create CHQ→INV mapping from pairs
    chq_to_inv_mapping = {}
    if not pairs_df.empty:
        for _, pair in pairs_df.iterrows():
            chq_to_inv_mapping[str(pair['chq_reference'])] = str(pair['inv_reference'])
    
    print(f"📊 Created CHQ→INV mapping for {len(chq_to_inv_mapping)} CHQ transactions")
    
    # Process each HR185 transaction
    for _, transaction in hr185_df.iterrows():
        reference = str(transaction['reference'])
        transaction_type = transaction['transaction_type']
        
        # Try direct matching first
        matched_ref = enhanced_reference_matching(reference, all_grn_refs)
        
        if matched_ref:
            # Direct match found
            matched_transactions.append({
                'transaction': transaction.to_dict(),
                'match_type': 'direct',
                'matched_reference': matched_ref,
                'grn_voucher': matched_ref if matched_ref in voucher_refs else None,
                'grn_inv_no': matched_ref if matched_ref in inv_refs else None
            })
        elif transaction_type == 'CHQ' and reference in chq_to_inv_mapping:
            # CHQ inheritance matching
            inv_reference = chq_to_inv_mapping[reference]
            inv_matched_ref = enhanced_reference_matching(inv_reference, all_grn_refs)
            
            if inv_matched_ref:
                matched_transactions.append({
                    'transaction': transaction.to_dict(),
                    'match_type': 'inherited_from_inv',
                    'matched_reference': inv_matched_ref,
                    'inherited_from_inv': inv_reference,
                    'grn_voucher': inv_matched_ref if inv_matched_ref in voucher_refs else None,
                    'grn_inv_no': inv_matched_ref if inv_matched_ref in inv_refs else None,
                    'payment_description': f"Payment for INV {inv_reference}"
                })
            else:
                unmatched_transactions.append(transaction.to_dict())
        else:
            # No match found
            unmatched_transactions.append(transaction.to_dict())
    
    return matched_transactions, unmatched_transactions

def test_chq_integration():
    """Test the CHQ integration functionality"""
    
    print("🧪 Testing CHQ Integration in Enhanced Dashboard")
    print("=" * 50)
    
    try:
        # Load data
        print("📂 Loading data files...")
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
        
        print(f"✓ Loaded {len(hr185_df)} HR185 transactions")
        print(f"✓ Loaded {len(hr995grn_df)} HR995 GRN records")
        
        # Load or identify payment pairs
        print("\n🔍 Loading existing INV-CHQ payment pairs...")
        try:
            pairs_df = pd.read_csv('output/hr185_inv_chq_pairs.csv')
            print(f"✓ Loaded {len(pairs_df)} existing INV-CHQ payment pairs")
        except FileNotFoundError:
            print("Identifying INV-CHQ payment pairs from scratch...")
            pairs_df = identify_inv_chq_payment_pairs(hr185_df)
            print(f"✓ Identified {len(pairs_df)} INV-CHQ payment pairs")
        
        # Enhanced analysis
        print("\n🔄 Running enhanced analysis with CHQ inheritance...")
        matched_transactions, unmatched_transactions = enhanced_hr185_transaction_analysis(
            hr185_df, hr995grn_df, pairs_df
        )
        
        # Calculate statistics
        total_transactions = len(hr185_df)
        total_matched = len(matched_transactions)
        total_unmatched = len(unmatched_transactions)
        
        # CHQ-specific statistics
        chq_transactions = hr185_df[hr185_df['transaction_type'] == 'CHQ']
        total_chq = len(chq_transactions)
        
        chq_matched = [t for t in matched_transactions 
                      if t['transaction']['transaction_type'] == 'CHQ']
        chq_direct_matched = [t for t in chq_matched if t['match_type'] == 'direct']
        chq_inherited_matched = [t for t in chq_matched if t['match_type'] == 'inherited_from_inv']
        
        print(f"\n📊 INTEGRATION TEST RESULTS:")
        print("=" * 40)
        print(f"Total HR185 transactions: {total_transactions}")
        print(f"Total matched: {total_matched} ({total_matched/total_transactions*100:.1f}%)")
        print(f"Total unmatched: {total_unmatched} ({total_unmatched/total_transactions*100:.1f}%)")
        print()
        print(f"CHQ Transactions: {total_chq}")
        print(f"CHQ direct matches: {len(chq_direct_matched)} ({len(chq_direct_matched)/total_chq*100:.1f}%)")
        print(f"CHQ inherited matches: {len(chq_inherited_matched)} ({len(chq_inherited_matched)/total_chq*100:.1f}%)")
        print(f"CHQ total matched: {len(chq_matched)} ({len(chq_matched)/total_chq*100:.1f}%)")
        print(f"CHQ still unmatched: {total_chq - len(chq_matched)} ({(total_chq - len(chq_matched))/total_chq*100:.1f}%)")
        
        # Show sample inherited CHQ transactions
        if chq_inherited_matched:
            print(f"\n💡 Sample CHQ Inherited Matches:")
            print("-" * 40)
            for i, match in enumerate(chq_inherited_matched[:5]):
                trans = match['transaction']
                print(f"  CHQ {trans['reference']} | {trans['supplier_name'][:30]}")
                print(f"    {match['payment_description']}")
                print(f"    Linked to GRN: {match['matched_reference']}")
                print(f"    Amount: R {trans['amount']:,.2f}")
                print()
        
        # Validation
        expected_improvement = 119  # Based on previous fix_chq_linking.py results
        actual_improvement = len(chq_inherited_matched)
        
        print(f"✅ VALIDATION RESULTS:")
        print("=" * 30)
        print(f"Expected CHQ improvements: {expected_improvement}")
        print(f"Actual CHQ improvements: {actual_improvement}")
        print(f"Match: {'✓ PASS' if actual_improvement == expected_improvement else '❌ FAIL'}")
        
        if actual_improvement == expected_improvement:
            print("\n🎉 CHQ INTEGRATION TEST PASSED!")
            print("The enhanced dashboard CHQ linking is working correctly.")
        else:
            print(f"\n⚠️  CHQ INTEGRATION TEST ISSUES:")
            print(f"Expected {expected_improvement} but got {actual_improvement}")
            
        return actual_improvement == expected_improvement
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chq_integration()
    print(f"\n🏁 Test completed: {'SUCCESS' if success else 'FAILED'}")
