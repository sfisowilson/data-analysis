#!/usr/bin/env python3
"""
Check CHQ Transaction Matching
==============================
Analyze how CHQ transactions from INV-CHQ pairs are being matched in the current linking logic.
"""

import pandas as pd
import os

def check_chq_transaction_matching():
    """Check how CHQ transactions are matched using current linking logic."""
    
    print("🔍 CHQ Transaction Matching Analysis")
    print("=" * 50)
    
    try:
        # Load INV-CHQ pairs
        pairs_df = pd.read_csv('output/hr185_inv_chq_pairs.csv')
        print(f"✓ Loaded {len(pairs_df)} INV-CHQ payment pairs")
        
        # Load HR185 and HR995 data for matching analysis
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
        
        print(f"✓ HR185 transactions: {len(hr185_df)}")
        print(f"✓ HR995 GRN records: {len(hr995grn_df)}")
        print()
        
        # Analyze CHQ reference matching
        chq_refs = list(pairs_df['chq_reference'].astype(str))
        print(f"🔍 Analyzing {len(set(chq_refs))} unique CHQ references...")
        
        # Check direct reference matches
        def normalize_reference(ref):
            """Normalize reference by removing leading zeros."""
            if pd.isna(ref):
                return ''
            ref_str = str(ref).strip()
            try:
                return str(int(ref_str))  # Remove leading zeros
            except ValueError:
                return ref_str
        
        # Normalize GRN references  
        hr995grn_df['inv_no_norm'] = hr995grn_df['inv_no'].apply(normalize_reference)
        
        matches = []
        for _, pair in pairs_df.iterrows():
            chq_ref = str(pair['chq_reference'])
            inv_ref = str(pair['inv_reference'])
            inv_ref_norm = normalize_reference(inv_ref)
            
            # Check if INV reference matches any GRN inv_no
            grn_matches = hr995grn_df[hr995grn_df['inv_no_norm'] == inv_ref_norm]
            
            # Check if CHQ reference matches any GRN field
            chq_voucher_matches = hr995grn_df[hr995grn_df['voucher'].astype(str) == chq_ref]
            chq_invno_matches = hr995grn_df[hr995grn_df['inv_no_norm'] == chq_ref]
            
            match_info = {
                'supplier_name': pair['supplier_name'],
                'date': pair['date'],
                'inv_reference': inv_ref,
                'chq_reference': chq_ref,
                'inv_ref_normalized': inv_ref_norm,
                'amount': pair['amount'],
                'inv_has_grn_match': len(grn_matches) > 0,
                'chq_matches_voucher': len(chq_voucher_matches) > 0,
                'chq_matches_invno': len(chq_invno_matches) > 0,
                'grn_match_count': len(grn_matches)
            }
            
            if len(grn_matches) > 0:
                match_info['grn_voucher'] = grn_matches.iloc[0]['voucher']
                match_info['grn_supplier'] = grn_matches.iloc[0].get('supplier_name', 'N/A')
            
            matches.append(match_info)
        
        matches_df = pd.DataFrame(matches)
        
        # Analysis summary
        print("📊 MATCHING ANALYSIS RESULTS:")
        print("-" * 40)
        
        inv_with_grn = matches_df['inv_has_grn_match'].sum()
        chq_voucher_matches = matches_df['chq_matches_voucher'].sum()
        chq_invno_matches = matches_df['chq_matches_invno'].sum()
        
        print(f"INV references with GRN matches: {inv_with_grn}/{len(matches_df)} ({inv_with_grn/len(matches_df)*100:.1f}%)")
        print(f"CHQ references matching GRN vouchers: {chq_voucher_matches}/{len(matches_df)} ({chq_voucher_matches/len(matches_df)*100:.1f}%)")
        print(f"CHQ references matching GRN inv_no: {chq_invno_matches}/{len(matches_df)} ({chq_invno_matches/len(matches_df)*100:.1f}%)")
        print()
        
        # Show examples of the problem
        print("🔍 PROBLEM EXAMPLES:")
        print("-" * 40)
        
        # INV matched but CHQ not matched
        problem_cases = matches_df[
            (matches_df['inv_has_grn_match'] == True) & 
            (matches_df['chq_matches_voucher'] == False) & 
            (matches_df['chq_matches_invno'] == False)
        ]
        
        print(f"Cases where INV is matched but CHQ is not: {len(problem_cases)}")
        if len(problem_cases) > 0:
            print("\nSample problem cases:")
            for i, case in problem_cases.head(5).iterrows():
                print(f"  {case['supplier_name'][:30]:<30} | {case['date']}")
                print(f"    INV: {case['inv_reference']} (norm: {case['inv_ref_normalized']}) ✓ Has GRN match")
                print(f"    CHQ: {case['chq_reference']} ❌ No GRN match")
                print(f"    Amount: R {case['amount']:,.2f}")
                print()
        
        # Save detailed analysis
        matches_df.to_csv('output/chq_matching_analysis.csv', index=False)
        print(f"💾 Saved detailed analysis to 'output/chq_matching_analysis.csv'")
        
        return matches_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def propose_solution(matches_df):
    """Propose solution for CHQ transaction linking."""
    
    if matches_df is None:
        return
    
    print("\n" + "=" * 50)
    print("💡 PROPOSED SOLUTION")
    print("=" * 50)
    
    print("The problem: CHQ transactions appear unmatched because they don't directly")
    print("link to GRN records. However, they are part of INV-CHQ payment pairs.")
    print()
    print("Solution: Enhanced CHQ linking logic that:")
    print("1. Identifies INV-CHQ payment pairs (same supplier, date, amount)")
    print("2. When INV has GRN match, inherit that match for the CHQ")
    print("3. Mark CHQ as 'Payment for INV [reference]' in transaction trail")
    print("4. Update dashboard to show CHQ-INV linkage explicitly")
    print()
    
    problem_cases = matches_df[
        (matches_df['inv_has_grn_match'] == True) & 
        (matches_df['chq_matches_voucher'] == False) & 
        (matches_df['chq_matches_invno'] == False)
    ]
    
    print(f"This would resolve {len(problem_cases)} CHQ transactions that currently")
    print("appear unmatched despite being linked to matched INV records.")

if __name__ == "__main__":
    matches_df = check_chq_transaction_matching()
    propose_solution(matches_df)
