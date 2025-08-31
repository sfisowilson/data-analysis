#!/usr/bin/env python3
"""
Invalid Voucher Reference Analysis Script with Leading Zeros Normalization
Analyzes reasons for invalid voucher references and creates detailed reports
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
        # Keep leading zeros for prefixed vouchers as they might be significant for some systems
        return f"{prefix}{number}"
    
    return ref_str

def analyze_invalid_vouchers():
    """Analyze invalid voucher references and determine reasons with normalization."""
    
    print("=== INVALID VOUCHER REFERENCE DETAILED ANALYSIS (WITH ZERO NORMALIZATION) ===")
    
    # Load data
    grn_df = pd.read_csv('output/hr995_grn.csv')
    voucher_df = pd.read_csv('output/hr995_voucher.csv')
    
    print(f"📊 Loaded GRN records: {len(grn_df):,}")
    print(f"📊 Loaded Voucher records: {len(voucher_df):,}")
    
    # Apply normalization to handle leading zeros
    print("\n🔧 Applying reference normalization...")
    grn_df['voucher_normalized'] = grn_df['voucher'].apply(normalize_reference)
    voucher_df['voucher_no_normalized'] = voucher_df['voucher_no'].apply(normalize_reference)
    
    # Clean and prepare data (use normalized versions)
    grn_voucher_refs = set(grn_df['voucher_normalized'].dropna())
    actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
    
    # Also keep track of raw references for comparison
    grn_raw_refs = set(grn_df['voucher'].dropna().astype(str).str.strip().str.upper())
    voucher_raw_refs = set(voucher_df['voucher_no'].dropna().astype(str).str.strip().str.upper())
    
    invalid_refs_raw = grn_raw_refs - voucher_raw_refs
    invalid_refs_normalized = grn_voucher_refs - actual_vouchers
    
    print(f"❌ Invalid references (before normalization): {len(invalid_refs_raw):,}")
    print(f"✅ Invalid references (after normalization): {len(invalid_refs_normalized):,}")
    print(f"🎯 References fixed by normalization: {len(invalid_refs_raw) - len(invalid_refs_normalized):,}")
    
    # Get GRNs with invalid references (using normalized data)
    invalid_grns = grn_df[grn_df['voucher_normalized'].isin(invalid_refs_normalized)].copy()
    
    print(f"📊 Total GRN voucher references: {len(grn_voucher_refs):,}")
    print(f"📊 Valid voucher numbers in payments: {len(actual_vouchers):,}")
    print(f"❌ Invalid voucher references: {len(invalid_refs_normalized):,}")
    print(f"📈 Invalid rate: {len(invalid_refs_normalized)/len(grn_voucher_refs)*100:.1f}%")
    print(f"💰 Total value of invalid references: R{invalid_grns['nett_grn_amt'].sum():,.2f}")
    
    # Analyze patterns
    print("\n=== PATTERN ANALYSIS ===")
    invalid_list = list(invalid_refs_normalized)
    
    patterns = {
        'INVI': [ref for ref in invalid_list if str(ref).startswith('INVI')],
        '999I': [ref for ref in invalid_list if str(ref).startswith('999I')],
        'SINA': [ref for ref in invalid_list if str(ref).startswith('SINA')],
        'Numeric': [ref for ref in invalid_list if str(ref).isdigit()],
        'Other': [ref for ref in invalid_list if not any(str(ref).startswith(prefix) for prefix in ['INVI', '999I', 'SINA']) and not str(ref).isdigit()]
    }
    
    for pattern, refs in patterns.items():
        if refs:
            count = len(refs)
            percentage = (count / len(invalid_list)) * 100
            print(f"🔍 {pattern} prefix: {count} references ({percentage:.1f}%)")
            print(f"   Examples: {refs[:3]}")
    
    # Analyze potential reasons
    print("\n=== POTENTIAL REASONS FOR INVALID REFERENCES ===")
    
    # Reason 1: Date range mismatch
    grn_dates = pd.to_datetime(grn_df['date'], errors='coerce')
    voucher_dates = pd.to_datetime(voucher_df['date'], errors='coerce')
    
    if not grn_dates.empty and not voucher_dates.empty:
        grn_date_range = f"{grn_dates.min().strftime('%Y-%m-%d')} to {grn_dates.max().strftime('%Y-%m-%d')}"
        voucher_date_range = f"{voucher_dates.min().strftime('%Y-%m-%d')} to {voucher_dates.max().strftime('%Y-%m-%d')}"
        
        print(f"📅 GRN date range: {grn_date_range}")
        print(f"📅 Voucher date range: {voucher_date_range}")
        
        # Check if invalid GRNs are outside voucher date range
        invalid_grn_dates = pd.to_datetime(invalid_grns['date'], errors='coerce')
        voucher_min = voucher_dates.min()
        voucher_max = voucher_dates.max()
        
        outside_range = invalid_grn_dates[(invalid_grn_dates < voucher_min) | (invalid_grn_dates > voucher_max)]
        if len(outside_range) > 0:
            print(f"🚨 Reason 1: {len(outside_range)} invalid GRNs are outside voucher date range")
    
    # Reason 2: Numbering sequence gaps
    voucher_numbers = voucher_df['voucher_no_normalized'].dropna().astype(str)
    
    # Check for INVI sequence gaps
    invi_vouchers = [v for v in voucher_numbers if str(v).startswith('INVI')]
    invi_invalid = [ref for ref in invalid_list if str(ref).startswith('INVI')]
    
    if invi_vouchers and invi_invalid:
        # Extract numbers from INVI vouchers
        try:
            invi_nums = sorted([int(v[4:]) for v in invi_vouchers if len(str(v)) > 4 and v[4:].isdigit()])
            invi_invalid_nums = [int(v[4:]) for v in invi_invalid if len(str(v)) > 4 and str(v)[4:].isdigit()]
            
            if invi_nums and invi_invalid_nums:
                print(f"🔢 INVI voucher range: INVI{min(invi_nums):06d} to INVI{max(invi_nums):06d}")
                print(f"🚨 Reason 2: {len(invi_invalid_nums)} INVI references appear to be in sequence gaps")
        except:
            pass
    
    # Reason 3: Different processing systems
    prefix_analysis = {}
    for prefix in ['INVI', 'SINA', '999I', 'KEDA', 'WATA', '300B', 'STNS']:
        count = sum(1 for v in voucher_numbers if str(v).startswith(prefix))
        if count > 0:
            prefix_analysis[prefix] = count
    
    print(f"🏢 Voucher prefixes in payment system: {prefix_analysis}")
    print(f"🚨 Reason 3: Some GRN references may use different numbering systems")
    
    # Create detailed invalid voucher report
    create_invalid_voucher_report(invalid_grns, invalid_refs_normalized)
    
    return invalid_grns, invalid_refs_normalized

def create_invalid_voucher_report(invalid_grns, invalid_refs):
    """Create a detailed CSV report of invalid voucher references."""
    
    print("\n=== CREATING DETAILED INVALID VOUCHER REPORT ===")
    
    # Add analysis columns using normalized voucher references
    invalid_grns['invalid_reason'] = invalid_grns['voucher_normalized'].apply(determine_invalid_reason)
    invalid_grns['voucher_prefix'] = invalid_grns['voucher_normalized'].astype(str).str.extract(r'^([A-Z]*)')
    invalid_grns['voucher_number'] = invalid_grns['voucher_normalized'].astype(str).str.extract(r'(\d+)$')
    
    # Select relevant columns for the report
    report_columns = [
        'grn_no', 'voucher', 'voucher_normalized', 'supplier_name', 'date', 'nett_grn_amt', 
        'invalid_reason', 'voucher_prefix', 'voucher_number', 
        'fin_period', 'item_no', 'description'
    ]
    
    # Create report with available columns
    available_columns = [col for col in report_columns if col in invalid_grns.columns]
    report_df = invalid_grns[available_columns].copy()
    report_df = report_df.sort_values(['invalid_reason', 'voucher_normalized', 'nett_grn_amt'], ascending=[True, True, False])
    
    # Save to CSV
    output_file = 'output/invalid_voucher_references.csv'
    report_df.to_csv(output_file, index=False)
    
    print(f"📄 Saved detailed report to: {output_file}")
    print(f"📊 Report contains {len(report_df)} records")
    
    # Summary by reason
    print("\n=== INVALID VOUCHER SUMMARY BY REASON ===")
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

if __name__ == "__main__":
    invalid_grns, invalid_refs = analyze_invalid_vouchers()
    
    print("\n" + "="*60)
    print("📋 UPDATED RECOMMENDATIONS")
    print("="*60)
    print("1. ✅ Leading zero normalization implemented")
    print("2. 🔍 Review remaining INVI sequence gaps with finance team")
    print("3. 📅 Check if GRNs are processed before voucher creation")
    print("4. 🏢 Verify different voucher numbering systems")
    print("5. 📊 Update dashboard to use normalized reference matching")
    print("6. 🚨 Set up alerts for high invalid voucher rates")
    print("\n✅ Invalid voucher reference analysis complete with normalization!")
