#!/usr/bin/env python3
"""
Corrected Voucher Reference Analysis Script
Uses the correct linkage: HR185 Reference → GRN inv_no → GRN voucher → HR995_voucher voucher_no
"""

import pandas as pd
import numpy as np
from datetime import datetime

def normalize_reference(ref):
    """Normalize reference numbers by handling leading zeros."""
    if pd.isna(ref):
        return ref
    
    ref_str = str(ref).strip()
    
    # For numeric references, strip leading zeros and convert to int
    if ref_str.isdigit() or (ref_str.startswith('0') and ref_str.lstrip('0').isdigit()):
        try:
            return int(ref_str.lstrip('0')) if ref_str.lstrip('0') else 0
        except:
            return ref_str
    
    return ref_str.upper()

def analyze_pdf_grn_linkage():
    """Analyze the linkage between PDF references and GRN invoice numbers."""
    
    print("=== PDF TO GRN LINKAGE ANALYSIS ===")
    
    # Load data
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    grn_df = pd.read_csv('output/hr995_grn.csv')
    voucher_df = pd.read_csv('output/hr995_voucher.csv')
    
    print(f"📄 HR185 PDF records: {len(hr185_df):,}")
    print(f"📋 GRN records: {len(grn_df):,}")
    print(f"🧾 Voucher records: {len(voucher_df):,}")
    
    # Normalize PDF references
    hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
    grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(normalize_reference)
    
    # Get unique sets
    pdf_refs = set(hr185_df['reference_normalized'].dropna())
    grn_inv_nos = set(grn_df['inv_no_normalized'].dropna())
    
    print(f"\n📊 Unique PDF references (normalized): {len(pdf_refs):,}")
    print(f"📊 Unique GRN invoice numbers: {len(grn_inv_nos):,}")
    
    # Find matches between PDF references and GRN invoice numbers
    pdf_grn_matches = pdf_refs & grn_inv_nos
    pdf_refs_not_in_grn = pdf_refs - grn_inv_nos
    
    print(f"🎯 PDF references matching GRN invoice numbers: {len(pdf_grn_matches):,}")
    print(f"❌ PDF references NOT in GRN: {len(pdf_refs_not_in_grn):,}")
    print(f"📈 PDF-GRN match rate: {len(pdf_grn_matches)/len(pdf_refs)*100:.1f}%")
    
    return pdf_grn_matches, pdf_refs_not_in_grn

def analyze_corrected_voucher_references():
    """Analyze voucher references using the correct PDF → GRN → Voucher linkage."""
    
    print("\n=== CORRECTED VOUCHER REFERENCE ANALYSIS ===")
    
    # Load data
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    grn_df = pd.read_csv('output/hr995_grn.csv')
    voucher_df = pd.read_csv('output/hr995_voucher.csv')
    
    # Normalize references
    hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
    grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(normalize_reference)
    grn_df['voucher_normalized'] = grn_df['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    voucher_df['voucher_no_normalized'] = voucher_df['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    
    # Step 1: Link PDF references to GRNs via invoice numbers
    pdf_grn_links = grn_df[grn_df['inv_no_normalized'].isin(hr185_df['reference_normalized'])]
    print(f"📋 GRN records linked to PDF references: {len(pdf_grn_links):,}")
    
    # Step 2: Check which GRN vouchers exist in the payment system
    grn_voucher_refs = set(grn_df['voucher_normalized'].dropna())
    actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
    
    print(f"📊 Unique GRN voucher references: {len(grn_voucher_refs):,}")
    print(f"📊 Unique payment voucher numbers: {len(actual_vouchers):,}")
    
    # Find invalid voucher references
    invalid_voucher_refs = grn_voucher_refs - actual_vouchers
    valid_voucher_refs = grn_voucher_refs & actual_vouchers
    
    print(f"✅ Valid voucher references: {len(valid_voucher_refs):,}")
    print(f"❌ Invalid voucher references: {len(invalid_voucher_refs):,}")
    print(f"📈 Voucher validity rate: {len(valid_voucher_refs)/len(grn_voucher_refs)*100:.1f}%")
    
    # Step 3: Analyze PDF-linked transactions
    print(f"\n=== PDF-LINKED TRANSACTION ANALYSIS ===")
    
    # Get GRNs that are linked to PDFs
    pdf_linked_grns = grn_df[grn_df['inv_no_normalized'].isin(hr185_df['reference_normalized'])]
    pdf_linked_invalid_vouchers = pdf_linked_grns[pdf_linked_grns['voucher_normalized'].isin(invalid_voucher_refs)]
    
    print(f"📄 GRN records linked to PDF transactions: {len(pdf_linked_grns):,}")
    print(f"❌ PDF-linked GRNs with invalid vouchers: {len(pdf_linked_invalid_vouchers):,}")
    print(f"💰 Value of PDF-linked invalid vouchers: R{pdf_linked_invalid_vouchers['nett_grn_amt'].sum():,.2f}")
    
    # Step 4: Analyze non-PDF-linked invalid vouchers
    non_pdf_linked_invalid = grn_df[
        (~grn_df['inv_no_normalized'].isin(hr185_df['reference_normalized'])) &
        (grn_df['voucher_normalized'].isin(invalid_voucher_refs))
    ]
    
    print(f"❌ Non-PDF-linked GRNs with invalid vouchers: {len(non_pdf_linked_invalid):,}")
    print(f"💰 Value of non-PDF-linked invalid vouchers: R{non_pdf_linked_invalid['nett_grn_amt'].sum():,.2f}")
    
    # Create detailed analysis report
    create_corrected_analysis_report(pdf_linked_invalid_vouchers, non_pdf_linked_invalid, invalid_voucher_refs)
    
    return pdf_linked_invalid_vouchers, non_pdf_linked_invalid

def create_corrected_analysis_report(pdf_linked_invalid, non_pdf_invalid, all_invalid_refs):
    """Create a corrected analysis report with proper linkage."""
    
    print(f"\n=== CREATING CORRECTED ANALYSIS REPORT ===")
    
    # Load base data again for report
    grn_df = pd.read_csv('output/hr995_grn.csv')
    grn_df['voucher_normalized'] = grn_df['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    
    # Get all invalid voucher GRNs
    all_invalid_grns = grn_df[grn_df['voucher_normalized'].isin(all_invalid_refs)].copy()
    
    # Add analysis columns
    all_invalid_grns['invalid_reason'] = all_invalid_grns['voucher_normalized'].apply(determine_invalid_reason)
    all_invalid_grns['voucher_prefix'] = all_invalid_grns['voucher_normalized'].astype(str).str.extract(r'^([A-Z]*)')
    all_invalid_grns['has_pdf_link'] = all_invalid_grns['inv_no'].apply(
        lambda x: 'Yes' if has_pdf_reference(x) else 'No'
    )
    
    # Select columns for report
    report_columns = [
        'grn_no', 'inv_no', 'voucher', 'voucher_normalized', 'supplier_name', 'date', 
        'nett_grn_amt', 'invalid_reason', 'voucher_prefix', 'has_pdf_link',
        'fin_period', 'item_no', 'description'
    ]
    
    available_columns = [col for col in report_columns if col in all_invalid_grns.columns]
    report_df = all_invalid_grns[available_columns].copy()
    report_df = report_df.sort_values(['has_pdf_link', 'invalid_reason', 'voucher_normalized'], ascending=[False, True, True])
    
    # Save corrected report
    output_file = 'output/invalid_voucher_references_corrected.csv'
    report_df.to_csv(output_file, index=False)
    
    print(f"📄 Saved corrected report to: {output_file}")
    print(f"📊 Report contains {len(report_df)} records")
    
    # Summary statistics
    print(f"\n=== CORRECTED SUMMARY STATISTICS ===")
    
    summary_stats = report_df.groupby(['has_pdf_link', 'invalid_reason']).agg({
        'grn_no': 'count',
        'nett_grn_amt': 'sum'
    }).round(2)
    summary_stats.columns = ['Count', 'Total_Value_R']
    print(summary_stats)
    
    # PDF linkage summary
    pdf_summary = report_df.groupby('has_pdf_link').agg({
        'grn_no': 'count',
        'nett_grn_amt': 'sum'
    }).round(2)
    pdf_summary.columns = ['Count', 'Total_Value_R']
    print(f"\n=== PDF LINKAGE SUMMARY ===")
    print(pdf_summary)
    
    return report_df

def has_pdf_reference(inv_no):
    """Check if an invoice number has a corresponding PDF reference."""
    try:
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        normalized_inv = normalize_reference(inv_no)
        pdf_refs = hr185_df['reference'].apply(normalize_reference)
        return normalized_inv in pdf_refs.values
    except:
        return False

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

def create_validation_summary():
    """Create a summary of the validation improvements."""
    
    print(f"\n=== VALIDATION SUMMARY ===")
    
    # Compare old vs new approach
    print("🔄 OLD APPROACH (Incorrect):")
    print("   - PDF Reference → GRN Voucher (WRONG)")
    print("   - Led to false invalid voucher identifications")
    
    print("\n✅ NEW APPROACH (Correct):")
    print("   - PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
    print("   - Proper traceability from PDF to payment system")
    
    # Load data for comparison
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    grn_df = pd.read_csv('output/hr995_grn.csv')
    
    hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
    grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(normalize_reference)
    
    pdf_grn_matches = set(hr185_df['reference_normalized']) & set(grn_df['inv_no_normalized'])
    
    print(f"\n📊 LINKAGE STATISTICS:")
    print(f"   - PDF transactions with GRN matches: {len(pdf_grn_matches):,}")
    print(f"   - This represents proper document traceability")
    print(f"   - Leading zero normalization applied for accurate matching")

if __name__ == "__main__":
    print("🚀 CORRECTED VOUCHER REFERENCE ANALYSIS")
    print("=" * 60)
    
    # Step 1: Analyze PDF-GRN linkage
    pdf_grn_matches, pdf_not_in_grn = analyze_pdf_grn_linkage()
    
    # Step 2: Analyze voucher references with correct linkage
    pdf_invalid, non_pdf_invalid = analyze_corrected_voucher_references()
    
    # Step 3: Create validation summary
    create_validation_summary()
    
    print("\n" + "="*60)
    print("📋 UPDATED RECOMMENDATIONS")
    print("="*60)
    print("1. ✅ Corrected PDF → GRN → Voucher linkage implemented")
    print("2. ✅ Leading zero normalization for accurate reference matching")
    print("3. 🔍 PDF-linked vs non-PDF-linked invalid vouchers identified")
    print("4. 📊 Proper document traceability established")
    print("5. 🔄 Update dashboards to use corrected linkage")
    print("6. 📋 Review separated invalid voucher categories")
    
    print("\n✅ Corrected voucher reference analysis complete!")
