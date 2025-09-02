#!/usr/bin/env python3
"""
Test the new CHQ-excluded approach
Validates the core functionality of the enhanced dashboard v2
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def normalize_reference(ref):
    """Normalize reference for matching - handles leading zeros and formatting"""
    if pd.isna(ref):
        return ''
    ref_str = str(ref).strip()
    ref_str = ref_str.lstrip('0')
    return ref_str if ref_str else '0'

def enhanced_reference_matching(hr185_ref, hr995_refs):
    """Enhanced reference matching with 4 strategies for leading zero issues"""
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

def enhanced_transaction_analysis_no_chq():
    """Test the enhanced transaction analysis excluding CHQ"""
    
    print("🚀 Testing Enhanced Transaction Analysis v2 (CHQ Excluded)")
    print("=" * 65)
    
    # Load data
    print("📂 Loading data...")
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
    hr995issue_df = pd.read_csv('output/individual_hr995issue.csv')
    hr995vouch_df = pd.read_csv('output/individual_hr995vouch.csv')
    
    # Separate CHQ from primary transactions
    hr185_chq = hr185_df[hr185_df['transaction_type'] == 'CHQ']
    hr185_primary = hr185_df[hr185_df['transaction_type'] != 'CHQ']  # EXCLUDE CHQ
    
    print(f"✓ Total HR185 transactions: {len(hr185_df):,}")
    print(f"✓ CHQ transactions (excluded): {len(hr185_chq):,}")
    print(f"✓ Primary transactions (for analysis): {len(hr185_primary):,}")
    print(f"✓ HR995 GRN records: {len(hr995grn_df):,}")
    print()
    
    # Create reference sets
    print("🔍 Creating reference sets for matching...")
    grn_voucher_refs = set(hr995grn_df['voucher_normalized'].dropna())
    grn_inv_refs = set(hr995grn_df['inv_no_normalized'].dropna())
    issue_refs = set(hr995issue_df['reference_normalized'].dropna()) if 'reference_normalized' in hr995issue_df.columns else set()
    vouch_refs = set(hr995vouch_df['reference_normalized'].dropna()) if 'reference_normalized' in hr995vouch_df.columns else set()
    
    all_grn_refs = grn_voucher_refs.union(grn_inv_refs)
    
    print(f"✓ GRN voucher references: {len(grn_voucher_refs):,}")
    print(f"✓ GRN invoice references: {len(grn_inv_refs):,}")
    print(f"✓ Total GRN references: {len(all_grn_refs):,}")
    print()
    
    # Analyze primary transactions
    print("⚡ Analyzing primary transactions...")
    
    matched_transactions = []
    unmatched_transactions = []
    
    for i, (_, transaction) in enumerate(hr185_primary.iterrows()):
        reference = str(transaction['reference'])
        transaction_type = transaction['transaction_type']
        
        # Try GRN matching
        grn_matched_ref = enhanced_reference_matching(reference, all_grn_refs)
        
        transaction_result = {
            'hr185_reference': reference,
            'supplier_name': transaction['supplier_name'],
            'transaction_type': transaction_type,
            'amount': transaction['amount'],
            'has_grn_match': bool(grn_matched_ref),
            'matched_reference': grn_matched_ref,
            'match_type': 'grn' if grn_matched_ref else None
        }
        
        if grn_matched_ref:
            matched_transactions.append(transaction_result)
        else:
            unmatched_transactions.append(transaction_result)
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1:,} transactions...")
    
    print(f"✓ Analysis complete!")
    print()
    
    # Results summary
    total_primary = len(hr185_primary)
    total_matched = len(matched_transactions)
    total_unmatched = len(unmatched_transactions)
    match_rate = (total_matched / total_primary * 100) if total_primary > 0 else 0
    
    print("📊 RESULTS SUMMARY:")
    print("=" * 20)
    print(f"Primary transactions analyzed: {total_primary:,}")
    print(f"Successfully matched: {total_matched:,}")
    print(f"Unmatched: {total_unmatched:,}")
    print(f"Match rate: {match_rate:.1f}%")
    print()
    
    # Transaction type breakdown
    print("📈 MATCH RATES BY TRANSACTION TYPE:")
    print("-" * 38)
    
    for trans_type in hr185_primary['transaction_type'].unique():
        type_transactions = hr185_primary[hr185_primary['transaction_type'] == trans_type]
        type_matched = [t for t in matched_transactions if t['transaction_type'] == trans_type]
        type_total = len(type_transactions)
        type_matched_count = len(type_matched)
        type_rate = (type_matched_count / type_total * 100) if type_total > 0 else 0
        
        print(f"  {trans_type}: {type_matched_count}/{type_total} ({type_rate:.1f}%)")
    
    print()
    
    # Sample results
    print("🔬 SAMPLE MATCHED TRANSACTIONS:")
    print("-" * 32)
    
    for i, match in enumerate(matched_transactions[:5], 1):
        print(f"  {i}. {match['transaction_type']} {match['hr185_reference']} | {match['supplier_name'][:40]}")
        print(f"     Matched to: {match['matched_reference']} | Amount: R {match['amount']:,.2f}")
        print()
    
    # CHQ summary for context
    print("📋 CHQ TRANSACTIONS SUMMARY (Excluded from Analysis):")
    print("-" * 52)
    print(f"Total CHQ transactions: {len(hr185_chq):,}")
    print(f"CHQ total amount: R {hr185_chq['amount'].sum():,.2f}")
    print(f"CHQ suppliers: {hr185_chq['supplier_name'].nunique():,}")
    print("Status: Available for separate payment audit analysis")
    print()
    
    # Comparison with previous approach
    try:
        previous_results = pd.read_csv('output/enhanced_transaction_trail_with_chq_fix.csv')
        prev_total = len(previous_results)
        prev_matched = len(previous_results[
            (previous_results['has_direct_grn_match'] == True) |
            (previous_results['has_inherited_grn_match'] == True)
        ])
        prev_rate = (prev_matched / prev_total * 100) if prev_total > 0 else 0
        
        print("⚖️  APPROACH COMPARISON:")
        print("-" * 25)
        print(f"Previous approach (CHQ included):")
        print(f"  Total: {prev_total:,} transactions")
        print(f"  Matched: {prev_matched:,} ({prev_rate:.1f}%)")
        print(f"  Complexity: High (inheritance logic)")
        print()
        print(f"New approach (CHQ excluded):")
        print(f"  Total: {total_primary:,} transactions")
        print(f"  Matched: {total_matched:,} ({match_rate:.1f}%)")
        print(f"  Complexity: Low (direct matching)")
        print()
        print(f"🎯 IMPROVEMENT:")
        if match_rate > prev_rate:
            improvement = match_rate - prev_rate
            print(f"✅ {improvement:.1f} percentage point improvement in match rate")
        print(f"✅ Eliminated {len(hr185_chq):,} complex CHQ cases")
        print(f"✅ Simplified logic and improved focus on business transactions")
        
    except FileNotFoundError:
        print("Previous results not available for comparison")
    
    print()
    
    # Save results
    results_df = pd.DataFrame(matched_transactions + unmatched_transactions)
    results_df.to_csv('output/enhanced_analysis_no_chq_test.csv', index=False)
    print(f"💾 Results saved to 'output/enhanced_analysis_no_chq_test.csv'")
    
    # Final recommendation
    print()
    print("🏆 FINAL ASSESSMENT:")
    print("=" * 20)
    
    if match_rate >= 95:
        print("🎉 EXCELLENT! Match rate ≥ 95% - Outstanding performance")
    elif match_rate >= 90:
        print("✅ VERY GOOD! Match rate ≥ 90% - Strong performance")
    elif match_rate >= 80:
        print("👍 GOOD! Match rate ≥ 80% - Solid performance")
    else:
        print("📈 Room for improvement - consider additional matching strategies")
    
    print(f"The CHQ exclusion approach achieves {match_rate:.1f}% matching on")
    print(f"{total_primary:,} primary business transactions, successfully eliminating")
    print(f"the complexity of {len(hr185_chq):,} payment confirmation records.")
    
    return match_rate >= 90

if __name__ == "__main__":
    success = enhanced_transaction_analysis_no_chq()
    print(f"\n🏁 Test completed: {'SUCCESS' if success else 'REVIEW NEEDED'}")
