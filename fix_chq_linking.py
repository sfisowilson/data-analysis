#!/usr/bin/env python3
"""
Enhanced CHQ Linking Logic
==========================
Fix the issue where CHQ transactions appear unmatched despite being part of 
INV-CHQ payment pairs where the INV has a GRN match.

This implements inheritance-based linking where CHQ transactions inherit the 
linkage from their paired INV transactions.
"""

import pandas as pd
import os

def implement_chq_linking_fix():
    """Implement enhanced CHQ linking logic to fix unmatched CHQ transactions."""
    
    print("🔧 Implementing Enhanced CHQ Linking Logic")
    print("=" * 50)
    
    try:
        # Load required data
        pairs_df = pd.read_csv('output/hr185_inv_chq_pairs.csv')
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
        
        print(f"✓ Loaded {len(pairs_df)} INV-CHQ payment pairs")
        print(f"✓ Loaded {len(hr185_df)} HR185 transactions")
        print(f"✓ Loaded {len(hr995grn_df)} HR995 GRN records")
        print()
        
        # Normalize reference function
        def normalize_reference(ref):
            if pd.isna(ref):
                return ''
            ref_str = str(ref).strip()
            try:
                return str(int(ref_str))
            except ValueError:
                return ref_str
        
        # Create enhanced transaction trail with CHQ inheritance
        hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
        hr995grn_df['inv_no_normalized'] = hr995grn_df['inv_no'].apply(normalize_reference)
        
        enhanced_trail = []
        
        # Process each HR185 transaction
        for _, hr185_row in hr185_df.iterrows():
            hr185_ref = hr185_row['reference']
            hr185_ref_norm = normalize_reference(hr185_ref)
            transaction_type = hr185_row['transaction_type']
            
            # Standard linking logic for all transactions
            grn_matches = hr995grn_df[hr995grn_df['inv_no_normalized'] == hr185_ref_norm]
            has_direct_match = len(grn_matches) > 0
            
            trail_entry = {
                'hr185_reference': hr185_ref,
                'hr185_reference_normalized': hr185_ref_norm,
                'supplier_code': hr185_row['supplier_code'],
                'supplier_name': hr185_row['supplier_name'],
                'transaction_date': hr185_row['transaction_date'],
                'transaction_type': transaction_type,
                'amount': hr185_row['amount'],
                'has_direct_grn_match': has_direct_match,
                'grn_match_type': 'direct' if has_direct_match else 'none',
                'grn_match_count': len(grn_matches),
                'linking_method': 'standard'
            }
            
            if has_direct_match:
                trail_entry['grn_voucher'] = grn_matches.iloc[0]['voucher']
                trail_entry['grn_inv_no'] = grn_matches.iloc[0]['inv_no']
                trail_entry['grn_supplier'] = grn_matches.iloc[0]['supplier_name']
            
            # Enhanced CHQ linking logic
            if transaction_type == 'CHQ' and not has_direct_match:
                # Check if this CHQ is part of an INV-CHQ pair
                chq_pair = pairs_df[pairs_df['chq_reference'].astype(str) == str(hr185_ref)]
                
                if len(chq_pair) > 0:
                    # Get the paired INV reference
                    paired_inv_ref = chq_pair.iloc[0]['inv_reference']
                    paired_inv_ref_norm = normalize_reference(paired_inv_ref)
                    
                    # Check if the paired INV has a GRN match
                    paired_grn_matches = hr995grn_df[hr995grn_df['inv_no_normalized'] == paired_inv_ref_norm]
                    
                    if len(paired_grn_matches) > 0:
                        # CHQ inherits the match from its paired INV
                        trail_entry['has_direct_grn_match'] = False
                        trail_entry['has_inherited_grn_match'] = True
                        trail_entry['grn_match_type'] = 'inherited_from_inv'
                        trail_entry['grn_match_count'] = len(paired_grn_matches)
                        trail_entry['linking_method'] = 'inv_chq_inheritance'
                        trail_entry['paired_inv_reference'] = paired_inv_ref
                        trail_entry['grn_voucher'] = paired_grn_matches.iloc[0]['voucher']
                        trail_entry['grn_inv_no'] = paired_grn_matches.iloc[0]['inv_no']
                        trail_entry['grn_supplier'] = paired_grn_matches.iloc[0]['supplier_name']
                        trail_entry['match_notes'] = f'Payment for INV {paired_inv_ref}'
                    else:
                        trail_entry['has_inherited_grn_match'] = False
                        trail_entry['paired_inv_reference'] = paired_inv_ref
                        trail_entry['match_notes'] = f'Payment for INV {paired_inv_ref} (INV also unmatched)'
                else:
                    trail_entry['has_inherited_grn_match'] = False
                    trail_entry['match_notes'] = 'Standalone CHQ transaction'
            else:
                trail_entry['has_inherited_grn_match'] = False
                if transaction_type == 'INV':
                    trail_entry['match_notes'] = 'Invoice transaction'
                elif transaction_type == 'CHQ' and has_direct_match:
                    trail_entry['match_notes'] = 'CHQ with direct GRN match'
                else:
                    trail_entry['match_notes'] = f'{transaction_type} transaction'
            
            enhanced_trail.append(trail_entry)
        
        # Convert to DataFrame
        enhanced_trail_df = pd.DataFrame(enhanced_trail)
        
        # Calculate summary statistics
        total_transactions = len(enhanced_trail_df)
        direct_matches = enhanced_trail_df['has_direct_grn_match'].sum()
        inherited_matches = enhanced_trail_df.get('has_inherited_grn_match', pd.Series([False]*total_transactions)).sum()
        total_matched = direct_matches + inherited_matches
        
        chq_transactions = enhanced_trail_df[enhanced_trail_df['transaction_type'] == 'CHQ']
        chq_total = len(chq_transactions)
        chq_direct = chq_transactions['has_direct_grn_match'].sum()
        chq_inherited = chq_transactions.get('has_inherited_grn_match', pd.Series([False]*chq_total)).sum()
        chq_matched = chq_direct + chq_inherited
        
        print("📊 ENHANCED LINKING RESULTS:")
        print("-" * 40)
        print(f"Total HR185 transactions: {total_transactions}")
        print(f"Direct GRN matches: {direct_matches} ({direct_matches/total_transactions*100:.1f}%)")
        print(f"Inherited GRN matches: {inherited_matches} ({inherited_matches/total_transactions*100:.1f}%)")
        print(f"Total matched: {total_matched} ({total_matched/total_transactions*100:.1f}%)")
        print()
        print(f"CHQ transactions: {chq_total}")
        print(f"CHQ direct matches: {chq_direct} ({chq_direct/chq_total*100:.1f}%)")
        print(f"CHQ inherited matches: {chq_inherited} ({chq_inherited/chq_total*100:.1f}%)")
        print(f"CHQ total matched: {chq_matched} ({chq_matched/chq_total*100:.1f}%)")
        print()
        
        # Show examples of fixed CHQ transactions
        chq_fixed = enhanced_trail_df[
            (enhanced_trail_df['transaction_type'] == 'CHQ') &
            (enhanced_trail_df.get('has_inherited_grn_match', False) == True)
        ]
        
        print(f"🔧 FIXED CHQ TRANSACTIONS: {len(chq_fixed)}")
        print("-" * 40)
        if len(chq_fixed) > 0:
            print("Sample fixed CHQ transactions:")
            for i, row in chq_fixed.head(5).iterrows():
                print(f"  CHQ {row['hr185_reference']} | {row['supplier_name'][:30]}")
                print(f"    {row['match_notes']}")
                print(f"    Linked to GRN voucher: {row['grn_voucher']}")
                print(f"    Amount: R {row['amount']:,.2f}")
                print()
        
        # Save enhanced transaction trail
        output_file = 'output/enhanced_transaction_trail_with_chq_fix.csv'
        enhanced_trail_df.to_csv(output_file, index=False)
        print(f"💾 Saved enhanced transaction trail to '{output_file}'")
        
        return enhanced_trail_df
        
    except Exception as e:
        print(f"❌ Error implementing CHQ linking fix: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_summary_report(enhanced_trail_df):
    """Generate a summary report of the CHQ linking improvements."""
    
    if enhanced_trail_df is None:
        return
    
    print("\n" + "=" * 60)
    print("📈 CHQ LINKING IMPROVEMENT SUMMARY")
    print("=" * 60)
    
    # Before and after comparison
    chq_transactions = enhanced_trail_df[enhanced_trail_df['transaction_type'] == 'CHQ']
    
    before_matched = chq_transactions['has_direct_grn_match'].sum()
    after_matched = before_matched + chq_transactions.get('has_inherited_grn_match', pd.Series([False]*len(chq_transactions))).sum()
    improvement = after_matched - before_matched
    
    print(f"CHQ Transactions Analysis:")
    print(f"  Total CHQ transactions: {len(chq_transactions)}")
    print(f"  Before fix - Matched: {before_matched} ({before_matched/len(chq_transactions)*100:.1f}%)")
    print(f"  After fix - Matched: {after_matched} ({after_matched/len(chq_transactions)*100:.1f}%)")
    print(f"  Improvement: +{improvement} transactions ({improvement/len(chq_transactions)*100:.1f}%)")
    print()
    
    print(f"Business Impact:")
    print(f"  ✓ Resolved {improvement} 'unmatched' CHQ transactions")
    print(f"  ✓ Established clear INV→CHQ payment cycle traceability")
    print(f"  ✓ Improved audit trail completeness") 
    print(f"  ✓ Enhanced financial reconciliation accuracy")

if __name__ == "__main__":
    enhanced_trail_df = implement_chq_linking_fix()
    generate_summary_report(enhanced_trail_df)
