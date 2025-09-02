#!/usr/bin/env python3
"""
CHQ Exclusion Analysis - Implementing user's suggestion
Testing the approach of excluding CHQ from primary linking analysis
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def analyze_without_chq():
    """Analyze transaction matching excluding CHQ transactions"""
    
    print("🎯 Transaction Analysis EXCLUDING CHQ")
    print("=" * 45)
    print("Testing user's suggestion: 'should we maybe just not consider the type CHQ from 185'")
    print()
    
    # Load HR185 data
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
    
    # Current analysis WITH CHQ
    total_with_chq = len(hr185_df)
    chq_count = len(hr185_df[hr185_df['transaction_type'] == 'CHQ'])
    
    # Analysis WITHOUT CHQ
    hr185_no_chq = hr185_df[hr185_df['transaction_type'] != 'CHQ']
    total_without_chq = len(hr185_no_chq)
    
    print("📊 TRANSACTION COUNTS:")
    print("-" * 25)
    print(f"Total HR185 transactions (with CHQ): {total_with_chq:,}")
    print(f"CHQ transactions: {chq_count:,} ({chq_count/total_with_chq*100:.1f}%)")
    print(f"Total HR185 transactions (without CHQ): {total_without_chq:,}")
    print(f"Reduction: {chq_count:,} transactions ({chq_count/total_with_chq*100:.1f}%)")
    print()
    
    # Transaction type distribution without CHQ
    print("📊 TRANSACTION TYPES (WITHOUT CHQ):")
    print("-" * 35)
    type_counts = hr185_no_chq['transaction_type'].value_counts()
    for trans_type, count in type_counts.items():
        percentage = (count / len(hr185_no_chq)) * 100
        print(f"  {trans_type}: {count:,} ({percentage:.1f}%)")
    print()
    
    # Simulate matching without CHQ complications
    print("🔍 MATCHING ANALYSIS WITHOUT CHQ:")
    print("-" * 35)
    
    # Create reference sets for matching
    voucher_refs = set(hr995grn_df['voucher_normalized'].dropna())
    inv_refs = set(hr995grn_df['inv_no_normalized'].dropna())
    all_grn_refs = voucher_refs.union(inv_refs)
    
    def normalize_reference(ref):
        """Normalize reference for matching"""
        if pd.isna(ref):
            return ''
        ref_str = str(ref).strip().lstrip('0')
        return ref_str if ref_str else '0'
    
    # Test direct matching on non-CHQ transactions
    direct_matches = 0
    for _, transaction in hr185_no_chq.iterrows():
        reference = normalize_reference(transaction['reference'])
        if reference in all_grn_refs:
            direct_matches += 1
    
    print(f"Direct GRN matches (non-CHQ): {direct_matches:,}")
    print(f"Direct match rate (non-CHQ): {direct_matches/total_without_chq*100:.1f}%")
    print()
    
    # Compare with current approach (including CHQ inheritance)
    try:
        enhanced_df = pd.read_csv('output/enhanced_transaction_trail_with_chq_fix.csv')
        current_total_matched = len(enhanced_df[
            (enhanced_df['has_direct_grn_match'] == True) |
            (enhanced_df['has_inherited_grn_match'] == True)
        ])
        current_match_rate = current_total_matched / len(enhanced_df) * 100
        
        # Calculate what the match rate would be without CHQ
        enhanced_no_chq = enhanced_df[enhanced_df['transaction_type'] != 'CHQ']
        enhanced_no_chq_matched = len(enhanced_no_chq[
            enhanced_no_chq['has_direct_grn_match'] == True
        ])
        no_chq_match_rate = enhanced_no_chq_matched / len(enhanced_no_chq) * 100
        
        print("📈 APPROACH COMPARISON:")
        print("-" * 25)
        print(f"Current approach (with CHQ inheritance):")
        print(f"  Total matched: {current_total_matched:,}/{len(enhanced_df):,} ({current_match_rate:.1f}%)")
        print()
        print(f"Proposed approach (exclude CHQ):")
        print(f"  Total matched: {enhanced_no_chq_matched:,}/{len(enhanced_no_chq):,} ({no_chq_match_rate:.1f}%)")
        print()
        
        # Calculate improvement by excluding CHQ
        print("💡 BENEFITS OF EXCLUDING CHQ:")
        print("-" * 30)
        print(f"✅ Eliminates {chq_count:,} complex CHQ inheritance cases")
        print(f"✅ Focuses on {total_without_chq:,} primary business transactions")
        print(f"✅ Achieves {no_chq_match_rate:.1f}% match rate on core transactions")
        print(f"✅ Removes payment confirmation complexity")
        print(f"✅ Simplifies audit trail to primary transactions only")
        
        if no_chq_match_rate > 90:
            print(f"🎉 EXCELLENT: {no_chq_match_rate:.1f}% match rate on core transactions!")
        elif no_chq_match_rate > 80:
            print(f"✅ GOOD: {no_chq_match_rate:.1f}% match rate on core transactions")
        else:
            print(f"⚠️  {no_chq_match_rate:.1f}% match rate - may need additional strategies")
            
    except FileNotFoundError:
        print("Enhanced transaction trail not found for comparison")
    
    print(f"\n🎯 RECOMMENDATION:")
    print("=" * 20)
    print("✅ STRONGLY SUPPORT excluding CHQ from primary linking analysis")
    print()
    print("REASONS:")
    print("1. CHQ transactions are payment confirmations, not primary business events")
    print("2. They don't directly link to GRN/procurement data")
    print("3. Creates unnecessary complexity in matching logic")
    print("4. Primary transactions (INV, VCH, etc.) provide the real business value")
    print("5. CHQ can be included as metadata/audit trail without affecting matching")
    print()
    print("SUGGESTED IMPLEMENTATION:")
    print("- Filter out CHQ transactions before running matching analysis")
    print("- Include CHQ in separate payment tracking/audit reports")
    print("- Focus matching logic on procurement-related transactions")
    print("- Achieve cleaner, more accurate business transaction matching")

if __name__ == "__main__":
    analyze_without_chq()
