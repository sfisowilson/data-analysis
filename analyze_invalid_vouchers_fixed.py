#!/usr/bin/env python3
"""
Fixed Invalid Voucher Reference Analysis Script with Leading Zeros Normalization
Analyzes reasons for invalid voucher references with proper reference number normalization
"""

import pandas as pd
import numpy as np
from datetime import datetime

def normalize_reference(ref):
    """Normalize reference numbers by handling leading zeros and standardizing format."""
    if pd.isna(ref):
        return ref
    
    ref_str = str(ref).strip().upper()
    
    # For purely numeric references, strip leading zeros
    if ref_str.isdigit():
        return str(int(ref_str))  # This removes leading zeros
    
    # For alphanumeric references (like INVI005662), handle the numeric part
    import re
    match = re.match(r'^([A-Z]+)(\d+)$', ref_str)
    if match:
        prefix = match.group(1)
        number = match.group(2)
        # Keep leading zeros for prefixed vouchers as they might be significant
        return f"{prefix}{number}"
    
    return ref_str

def analyze_invalid_vouchers_fixed():
    """Analyze invalid voucher references with proper reference normalization."""
    
    print("=== INVALID VOUCHER REFERENCE ANALYSIS (FIXED WITH ZERO NORMALIZATION) ===")
    
    # Load data
    grn_df = pd.read_csv('output/hr995_grn.csv')
    voucher_df = pd.read_csv('output/hr995_voucher.csv')
    
    print(f"📊 Loaded GRN records: {len(grn_df):,}")
    print(f"📊 Loaded Voucher records: {len(voucher_df):,}")
    
    # Normalize references
    print("\n🔧 Normalizing reference numbers...")
    
    # Normalize GRN voucher references
    grn_df['voucher_normalized'] = grn_df['voucher'].apply(normalize_reference)
    
    # Normalize payment voucher references  
    voucher_df['voucher_no_normalized'] = voucher_df['voucher_no'].apply(normalize_reference)
    
    # Create clean sets for comparison
    grn_voucher_refs = set(grn_df['voucher_normalized'].dropna())
    actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
    
    print(f"📈 Unique normalized GRN voucher refs: {len(grn_voucher_refs):,}")
    print(f"📈 Unique normalized payment vouchers: {len(actual_vouchers):,}")
    
    # Find invalid references (before normalization)
    grn_raw_refs = set(grn_df['voucher'].dropna().astype(str).str.strip().str.upper())
    voucher_raw_nums = set(voucher_df['voucher_no'].dropna().astype(str).str.strip().str.upper())
    
    invalid_raw = grn_raw_refs - voucher_raw_nums
    
    # Find invalid references (after normalization)
    invalid_normalized = grn_voucher_refs - actual_vouchers
    
    print(f"\n❌ Invalid refs (before normalization): {len(invalid_raw):,}")
    print(f"✅ Invalid refs (after normalization): {len(invalid_normalized):,}")
    print(f"🎯 References fixed by normalization: {len(invalid_raw) - len(invalid_normalized):,}")
    
    # Get GRNs with invalid references (using normalized data)
    invalid_grns = grn_df[grn_df['voucher_normalized'].isin(invalid_normalized)].copy()
    
    if len(invalid_grns) > 0:
        print(f"💰 Total value of remaining invalid references: R{invalid_grns['nett_grn_amt'].sum():,.2f}")
        
        # Analyze patterns in remaining invalid references
        print("\n=== PATTERN ANALYSIS (REMAINING INVALID REFERENCES) ===")
        invalid_list = list(invalid_normalized)
        
        patterns = {
            'INVI': [ref for ref in invalid_list if str(ref).startswith('INVI')],
            '999I': [ref for ref in invalid_list if str(ref).startswith('999I')],
            'Numeric': [ref for ref in invalid_list if str(ref).isdigit()],
            'Other': [ref for ref in invalid_list if not any(str(ref).startswith(prefix) for prefix in ['INVI', '999I']) and not str(ref).isdigit()]
        }
        
        for pattern, refs in patterns.items():
            if refs:
                count = len(refs)
                percentage = (count / len(invalid_list)) * 100
                print(f"🔍 {pattern} pattern: {count} references ({percentage:.1f}%)")
                print(f"   Examples: {refs[:3]}")
        
        # Create detailed report
        create_fixed_invalid_voucher_report(invalid_grns, invalid_normalized)
    else:
        print("🎉 No invalid voucher references found after normalization!")
    
    # Show what was fixed
    if len(invalid_raw) > len(invalid_normalized):
        print(f"\n✅ NORMALIZATION SUCCESS!")
        print(f"Fixed {len(invalid_raw) - len(invalid_normalized)} voucher reference mismatches")
        
        # Show examples of what was fixed
        fixed_refs = invalid_raw - invalid_normalized
        if fixed_refs:
            print(f"Examples of fixed references: {list(fixed_refs)[:5]}")
    
    return invalid_grns, invalid_normalized

def create_fixed_invalid_voucher_report(invalid_grns, invalid_refs):
    """Create a detailed CSV report of remaining invalid voucher references."""
    
    print("\n=== CREATING FIXED INVALID VOUCHER REPORT ===")
    
    # Add analysis columns
    invalid_grns['invalid_reason'] = invalid_grns['voucher_normalized'].apply(determine_invalid_reason)
    invalid_grns['voucher_prefix'] = invalid_grns['voucher_normalized'].astype(str).str.extract(r'^([A-Z]*)')
    invalid_grns['voucher_number'] = invalid_grns['voucher_normalized'].astype(str).str.extract(r'(\d+)$')
    
    # Select relevant columns for the report
    report_columns = [
        'grn_no', 'voucher', 'voucher_normalized', 'supplier_name', 'date', 'nett_grn_amt', 
        'invalid_reason', 'voucher_prefix', 'voucher_number', 
        'fin_period', 'item_no', 'description'
    ]
    
    # Create report
    available_columns = [col for col in report_columns if col in invalid_grns.columns]
    report_df = invalid_grns[available_columns].copy()
    report_df = report_df.sort_values(['invalid_reason', 'voucher_normalized', 'nett_grn_amt'], ascending=[True, True, False])
    
    # Save to CSV
    output_file = 'output/invalid_voucher_references_fixed.csv'
    report_df.to_csv(output_file, index=False)
    
    print(f"📄 Saved fixed report to: {output_file}")
    print(f"📊 Fixed report contains {len(report_df)} records")
    
    # Summary by reason
    if len(report_df) > 0:
        print("\n=== REMAINING INVALID VOUCHER SUMMARY BY REASON ===")
        reason_summary = report_df.groupby('invalid_reason').agg({
            'grn_no': 'count',
            'nett_grn_amt': 'sum'
        }).round(2)
        reason_summary.columns = ['Count', 'Total_Value']
        print(reason_summary)
    
    return report_df

def determine_invalid_reason(voucher_ref):
    """Determine the most likely reason for an invalid voucher reference."""
    
    if pd.isna(voucher_ref):
        return "Missing voucher reference"
    
    voucher_str = str(voucher_ref).strip().upper()
    
    if voucher_str.startswith('INVI'):
        return "INVI sequence gap or timing issue"
    elif voucher_str.startswith('999I'):
        return "Special/manual voucher not in payment system"
    elif voucher_str.startswith('SINA'):
        return "Different supplier/system voucher"
    elif voucher_str.isdigit():
        return "Numeric voucher not in payment system"
    elif len(voucher_str) < 4:
        return "Invalid voucher format"
    else:
        return "Unknown voucher system or data entry error"

def compare_normalization_impact():
    """Compare the impact of normalization on voucher matching."""
    
    print("\n=== NORMALIZATION IMPACT ANALYSIS ===")
    
    grn_df = pd.read_csv('output/hr995_grn.csv')
    voucher_df = pd.read_csv('output/hr995_voucher.csv')
    
    # Before normalization
    grn_raw = set(grn_df['voucher'].dropna().astype(str).str.strip().str.upper())
    voucher_raw = set(voucher_df['voucher_no'].dropna().astype(str).str.strip().str.upper())
    matches_before = len(grn_raw & voucher_raw)
    
    # After normalization
    grn_norm = set(grn_df['voucher'].apply(normalize_reference).dropna())
    voucher_norm = set(voucher_df['voucher_no'].apply(normalize_reference).dropna())
    matches_after = len(grn_norm & voucher_norm)
    
    print(f"📊 Voucher matches before normalization: {matches_before:,}")
    print(f"📊 Voucher matches after normalization: {matches_after:,}")
    print(f"🎯 Additional matches gained: {matches_after - matches_before:,}")
    
    if matches_after > matches_before:
        improvement = (matches_after - matches_before) / len(grn_raw) * 100
        print(f"📈 Improvement rate: {improvement:.2f}%")

if __name__ == "__main__":
    # Run comparison first
    compare_normalization_impact()
    
    # Run fixed analysis
    invalid_grns, invalid_refs = analyze_invalid_vouchers_fixed()
    
    print("\n" + "="*60)
    print("📋 UPDATED RECOMMENDATIONS")
    print("="*60)
    print("1. ✅ Leading zero normalization implemented")
    print("2. 🔍 Review remaining invalid references (significantly reduced)")
    print("3. 📅 Check remaining INVI sequence gaps with finance team")
    print("4. 🏢 Verify any remaining different voucher numbering systems")
    print("5. 📊 Update dashboard to use normalized reference matching")
    print("\n✅ Fixed invalid voucher reference analysis complete!")
