#!/usr/bin/env python3
"""
Corrected GRN-Transaction Analysis Methods
These methods replace the incorrect analysis in enhanced_dashboard.py
Uses proper PDF → GRN → Voucher linkage for accurate results
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import os

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

def create_corrected_grn_transaction_summary(grn_df, voucher_df):
    """Create corrected GRN-Transaction analysis summary with proper PDF linkage."""
    st.markdown("### 📊 GRN-Transaction Analysis Summary (Corrected)")
    st.info("✅ **Using Corrected Linkage**: PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
    
    # Load PDF data if available
    pdf_df = None
    if os.path.exists('output/individual_hr185_transactions.csv'):
        pdf_df = pd.read_csv('output/individual_hr185_transactions.csv')
        pdf_df['reference_normalized'] = pdf_df['reference'].apply(normalize_reference)
    
    # Normalize GRN data
    grn_analysis = grn_df.copy()
    grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(normalize_reference)
    grn_analysis['voucher_normalized'] = grn_analysis['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    
    # Normalize voucher data
    voucher_analysis = voucher_df.copy()
    voucher_analysis['voucher_no_normalized'] = voucher_analysis['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total GRNs", f"{len(grn_df):,}")
    
    with col2:
        st.metric("Total Vouchers", f"{len(voucher_df):,}")
    
    with col3:
        grn_value = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce').sum()
        st.metric("Total GRN Value", f"R{grn_value:,.2f}")
    
    with col4:
        voucher_value = pd.to_numeric(voucher_df['cheq_amt'], errors='coerce').sum()
        st.metric("Total Voucher Value", f"R{voucher_value:,.2f}")
    
    # PDF Linkage Analysis
    if pdf_df is not None:
        st.markdown("### 🔗 PDF Linkage Analysis")
        
        # Find PDF-linked GRNs
        pdf_linked_grns = grn_analysis[grn_analysis['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
        non_pdf_linked_grns = grn_analysis[~grn_analysis['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📄 PDF-Linked GRNs", f"{len(pdf_linked_grns):,}")
            pdf_linked_value = pd.to_numeric(pdf_linked_grns['nett_grn_amt'], errors='coerce').sum()
            st.metric("📄 PDF-Linked Value", f"R{pdf_linked_value:,.2f}")
        
        with col2:
            st.metric("📋 Non-PDF-Linked GRNs", f"{len(non_pdf_linked_grns):,}")
            non_pdf_linked_value = pd.to_numeric(non_pdf_linked_grns['nett_grn_amt'], errors='coerce').sum()
            st.metric("📋 Non-PDF-Linked Value", f"R{non_pdf_linked_value:,.2f}")
        
        # PDF linkage chart
        linkage_data = pd.DataFrame({
            'Type': ['PDF-Linked', 'Non-PDF-Linked'],
            'Count': [len(pdf_linked_grns), len(non_pdf_linked_grns)],
            'Value': [pdf_linked_value, non_pdf_linked_value]
        })
        
        fig = px.pie(linkage_data, values='Value', names='Type', 
                     title="GRN Value Distribution by PDF Linkage")
        st.plotly_chart(fig, use_container_width=True)
    
    # Voucher Validation Analysis
    st.markdown("### ✅ Voucher Validation Analysis")
    
    # Find valid and invalid voucher references
    grn_voucher_refs = set(grn_analysis['voucher_normalized'].dropna())
    actual_vouchers = set(voucher_analysis['voucher_no_normalized'].dropna())
    
    valid_voucher_refs = grn_voucher_refs & actual_vouchers
    invalid_voucher_refs = grn_voucher_refs - actual_vouchers
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Valid Voucher References", f"{len(valid_voucher_refs):,}")
        validity_rate = len(valid_voucher_refs) / len(grn_voucher_refs) * 100 if grn_voucher_refs else 0
        st.metric("📈 Validity Rate", f"{validity_rate:.1f}%")
    
    with col2:
        st.metric("❌ Invalid Voucher References", f"{len(invalid_voucher_refs):,}")
        # Calculate value of invalid voucher GRNs
        invalid_grns = grn_analysis[grn_analysis['voucher_normalized'].isin(invalid_voucher_refs)]
        invalid_value = pd.to_numeric(invalid_grns['nett_grn_amt'], errors='coerce').sum()
        st.metric("💰 Invalid Voucher Value", f"R{invalid_value:,.2f}")
    
    with col3:
        # Break down invalid vouchers by PDF linkage
        if pdf_df is not None:
            invalid_pdf_linked = invalid_grns[invalid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
            invalid_non_pdf = invalid_grns[~invalid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
            
            st.metric("❌ Invalid (PDF-Linked)", f"{len(invalid_pdf_linked):,}")
            st.metric("❌ Invalid (Non-PDF)", f"{len(invalid_non_pdf):,}")
    
    # Risk Assessment
    st.markdown("### 🚨 Risk Assessment (Corrected)")
    
    risk_items = []
    
    # Corrected value mismatch calculation
    if grn_value > 0 and voucher_value > 0:
        value_diff_pct = abs(grn_value - voucher_value) / grn_value * 100
        if value_diff_pct > 10:
            risk_items.append({
                'Risk Type': 'Total Value Mismatch',
                'Severity': 'High' if value_diff_pct > 25 else 'Medium',
                'Description': f'Total GRN vs Voucher value difference: {value_diff_pct:.1f}%',
                'Recommendation': 'Expected due to timing differences and invalid vouchers',
                'Note': 'This is normal - not all GRNs have immediate payments'
            })
    
    # Invalid voucher risk
    if len(invalid_voucher_refs) > 0:
        invalid_rate = len(invalid_voucher_refs) / len(grn_voucher_refs) * 100
        if invalid_rate > 5:
            risk_items.append({
                'Risk Type': 'Invalid Voucher References',
                'Severity': 'High' if invalid_rate > 10 else 'Medium',
                'Description': f'{len(invalid_voucher_refs)} invalid voucher refs ({invalid_rate:.1f}%)',
                'Recommendation': 'Review invalid voucher analysis for details',
                'Note': f'R{invalid_value:,.2f} value affected'
            })
    
    # PDF linkage coverage
    if pdf_df is not None:
        pdf_coverage = len(pdf_linked_grns) / len(grn_analysis) * 100
        if pdf_coverage < 50:
            risk_items.append({
                'Risk Type': 'Low PDF Documentation',
                'Severity': 'Medium',
                'Description': f'Only {pdf_coverage:.1f}% of GRNs have PDF transaction links',
                'Recommendation': 'Many transactions may not be documented in HR185 PDFs',
                'Note': 'This may be normal for different transaction types'
            })
    
    # Display risk summary
    if risk_items:
        risk_df = pd.DataFrame(risk_items)
        
        # Color code by severity
        def highlight_severity(row):
            if row['Severity'] == 'High':
                return ['background-color: #ffebee'] * len(row)
            elif row['Severity'] == 'Medium':
                return ['background-color: #fff3e0'] * len(row)
            else:
                return [''] * len(row)
        
        styled_risk = risk_df.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_risk, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No major risks detected in corrected GRN-Transaction analysis")
    
    # Corrected Recommendations
    st.markdown("### 💡 Corrected Recommendations")
    
    recommendations = [
        "✅ **Analysis Updated**: Now uses proper PDF → GRN → Voucher linkage",
        "🔍 **Focus on Invalid Vouchers**: Review detailed invalid voucher analysis",
        "📄 **PDF Coverage**: Understand which transactions are documented in PDFs",
        "📊 **Regular Monitoring**: Track invalid voucher rates and PDF linkage coverage",
        "🔄 **Process Improvement**: Ensure proper document traceability for all transactions"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

def analyze_corrected_payment_status(grn_df, voucher_df):
    """Corrected payment status analysis using proper linkage."""
    st.markdown("### 🔍 GRN Payment Status Analysis (Corrected)")
    st.info("✅ **Corrected Logic**: Uses proper voucher reference validation")
    
    # Load corrected invalid voucher analysis if available
    corrected_file = 'output/invalid_voucher_references_corrected.csv'
    if os.path.exists(corrected_file):
        invalid_df = pd.read_csv(corrected_file)
        
        st.markdown("#### 📊 Payment Status Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_grns = len(grn_df)
            st.metric("Total GRNs", f"{total_grns:,}")
        
        with col2:
            invalid_grns = len(invalid_df)
            st.metric("GRNs with Invalid Vouchers", f"{invalid_grns:,}")
            invalid_rate = (invalid_grns / total_grns) * 100 if total_grns > 0 else 0
            st.metric("Invalid Rate", f"{invalid_rate:.1f}%")
        
        with col3:
            paid_grns = total_grns - invalid_grns
            st.metric("GRNs with Valid Vouchers", f"{paid_grns:,}")
            paid_rate = (paid_grns / total_grns) * 100 if total_grns > 0 else 0
            st.metric("Valid Rate", f"{paid_rate:.1f}%")
        
        # Value analysis
        st.markdown("#### 💰 Value Analysis")
        
        total_grn_value = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce').sum()
        invalid_value = invalid_df['nett_grn_amt'].sum()
        valid_value = total_grn_value - invalid_value
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total GRN Value", f"R{total_grn_value:,.2f}")
            st.metric("Valid Voucher Value", f"R{valid_value:,.2f}")
        
        with col2:
            st.metric("Invalid Voucher Value", f"R{invalid_value:,.2f}")
            invalid_value_pct = (invalid_value / total_grn_value) * 100 if total_grn_value > 0 else 0
            st.metric("Invalid Value %", f"{invalid_value_pct:.1f}%")
        
        # PDF linkage breakdown if available
        if 'has_pdf_link' in invalid_df.columns:
            st.markdown("#### 🔗 Invalid Vouchers by PDF Linkage")
            
            pdf_breakdown = invalid_df.groupby('has_pdf_link').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            pdf_breakdown.columns = ['Count', 'Value_R']
            
            st.dataframe(pdf_breakdown, use_container_width=True)
        
        # Show top invalid vouchers
        st.markdown("#### 🔍 Top Invalid Vouchers by Value")
        top_invalid = invalid_df.nlargest(10, 'nett_grn_amt')[
            ['grn_no', 'voucher', 'supplier_name', 'nett_grn_amt', 'invalid_reason']
        ]
        st.dataframe(top_invalid, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ Corrected invalid voucher analysis not found. Run: `python analyze_corrected_voucher_linkage.py`")

if __name__ == "__main__":
    print("This file contains corrected GRN-Transaction analysis methods.")
    print("These should replace the incorrect methods in enhanced_dashboard.py")
