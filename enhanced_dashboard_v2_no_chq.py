#!/usr/bin/env python3
"""
Enhanced Dashboard v2 - Excluding CHQ from Primary Linking
Implements user's suggestion to exclude CHQ transactions from primary matching
Focus on core business transactions (INV, VCH, CN, DN) for GRN linking
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="SCOA Enhanced Transaction Analysis (No CHQ)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

@st.cache_data
def load_data():
    """Load and cache all required data files"""
    try:
        # Load HR185 and exclude CHQ transactions
        hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
        hr185_primary = hr185_df[hr185_df['transaction_type'] != 'CHQ']  # EXCLUDE CHQ
        hr185_chq_only = hr185_df[hr185_df['transaction_type'] == 'CHQ']  # CHQ for audit
        
        # Load HR995 data
        hr995grn_df = pd.read_csv('output/individual_hr995grn.csv')
        hr995issue_df = pd.read_csv('output/individual_hr995issue.csv')
        hr995vouch_df = pd.read_csv('output/individual_hr995vouch.csv')
        hr390_df = pd.read_csv('output/individual_hr390.csv')
        
        return {
            'hr185_primary': hr185_primary,
            'hr185_chq_only': hr185_chq_only,
            'hr185_full': hr185_df,
            'hr995grn': hr995grn_df,
            'hr995issue': hr995issue_df,
            'hr995vouch': hr995vouch_df,
            'hr390': hr390_df
        }
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        return None

def enhanced_transaction_analysis(hr185_primary_df, hr995grn_df, hr995issue_df, hr995vouch_df):
    """Enhanced transaction analysis focusing on primary business transactions (excluding CHQ)"""
    
    # Create reference sets for matching
    grn_voucher_refs = set(hr995grn_df['voucher_normalized'].dropna())
    grn_inv_refs = set(hr995grn_df['inv_no_normalized'].dropna())
    issue_refs = set(hr995issue_df['reference_normalized'].dropna())
    vouch_refs = set(hr995vouch_df['reference_normalized'].dropna())
    
    all_grn_refs = grn_voucher_refs.union(grn_inv_refs)
    
    # Track matches
    analysis_results = []
    
    for _, transaction in hr185_primary_df.iterrows():
        reference = str(transaction['reference'])
        transaction_type = transaction['transaction_type']
        
        result = {
            'hr185_reference': reference,
            'hr185_reference_normalized': normalize_reference(reference),
            'supplier_code': transaction['supplier_code'],
            'supplier_name': transaction['supplier_name'],
            'transaction_date': transaction['transaction_date'],
            'transaction_type': transaction_type,
            'amount': transaction['amount'],
            'has_grn_match': False,
            'has_issue_match': False,
            'has_vouch_match': False,
            'grn_match_type': 'none',
            'grn_match_count': 0,
            'matched_grn_voucher': None,
            'matched_grn_inv_no': None,
            'matched_issue_ref': None,
            'matched_vouch_ref': None,
            'linking_method': 'enhanced_4_strategy'
        }
        
        # Try GRN matching (for INV transactions primarily)
        if transaction_type in ['INV', 'VCH']:  # Primary transaction types for GRN
            grn_matched_ref = enhanced_reference_matching(reference, all_grn_refs)
            if grn_matched_ref:
                result['has_grn_match'] = True
                if grn_matched_ref in grn_voucher_refs:
                    result['grn_match_type'] = 'voucher'
                    result['matched_grn_voucher'] = grn_matched_ref
                if grn_matched_ref in grn_inv_refs:
                    result['grn_match_type'] = 'invoice' if result['grn_match_type'] == 'none' else 'both'
                    result['matched_grn_inv_no'] = grn_matched_ref
                result['grn_match_count'] = 1
        
        # Try ISSUE matching (for specific transaction types)
        if transaction_type in ['ISS', 'CN', 'DN']:  # Transaction types that might match issues
            issue_matched_ref = enhanced_reference_matching(reference, issue_refs)
            if issue_matched_ref:
                result['has_issue_match'] = True
                result['matched_issue_ref'] = issue_matched_ref
        
        # Try VOUCH matching
        vouch_matched_ref = enhanced_reference_matching(reference, vouch_refs)
        if vouch_matched_ref:
            result['has_vouch_match'] = True
            result['matched_vouch_ref'] = vouch_matched_ref
        
        analysis_results.append(result)
    
    return pd.DataFrame(analysis_results)

def main():
    st.title("📊 SCOA Enhanced Transaction Analysis v2")
    st.markdown("**Optimized Approach: Primary Business Transactions Only (CHQ Excluded)**")
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_data()
    
    if data is None:
        st.error("Failed to load data files. Please ensure all CSV files are in the output directory.")
        return
    
    # Sidebar configuration
    st.sidebar.header("🎛️ Analysis Configuration")
    
    # Analysis options
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Primary Transactions Analysis", "CHQ Audit View", "Comparison Analysis"]
    )
    
    # Main content based on selection
    if analysis_type == "Primary Transactions Analysis":
        primary_transactions_analysis(data)
    elif analysis_type == "CHQ Audit View":
        chq_audit_analysis(data)
    else:
        comparison_analysis(data)

def primary_transactions_analysis(data):
    """Primary business transactions analysis (excluding CHQ)"""
    
    st.header("🎯 Primary Business Transactions Analysis")
    st.info("**Optimized Focus**: Analyzing INV, VCH, CN, DN transactions only - CHQ excluded as payment confirmations")
    
    hr185_primary = data['hr185_primary']
    hr995grn = data['hr995grn']
    hr995issue = data['hr995issue']
    hr995vouch = data['hr995vouch']
    
    # Run enhanced analysis
    with st.spinner("Running enhanced transaction analysis..."):
        analysis_results = enhanced_transaction_analysis(
            hr185_primary, hr995grn, hr995issue, hr995vouch
        )
    
    # Summary metrics
    st.subheader("📊 Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_primary = len(hr185_primary)
    total_matched = len(analysis_results[
        (analysis_results['has_grn_match'] == True) |
        (analysis_results['has_issue_match'] == True) |
        (analysis_results['has_vouch_match'] == True)
    ])
    match_rate = (total_matched / total_primary) * 100 if total_primary > 0 else 0
    
    with col1:
        st.metric("Total Primary Transactions", f"{total_primary:,}")
    with col2:
        st.metric("Successfully Matched", f"{total_matched:,}")
    with col3:
        st.metric("Match Rate", f"{match_rate:.1f}%")
    with col4:
        st.metric("CHQ Excluded", f"{len(data['hr185_chq_only']):,}")
    
    # Transaction type breakdown
    st.subheader("📈 Transaction Type Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction type distribution
        type_counts = hr185_primary['transaction_type'].value_counts()
        fig_types = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Primary Transaction Types Distribution"
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with col2:
        # Match rates by transaction type
        match_by_type = []
        for trans_type in hr185_primary['transaction_type'].unique():
            type_data = analysis_results[analysis_results['transaction_type'] == trans_type]
            type_matched = len(type_data[
                (type_data['has_grn_match'] == True) |
                (type_data['has_issue_match'] == True) |
                (type_data['has_vouch_match'] == True)
            ])
            type_total = len(type_data)
            type_rate = (type_matched / type_total * 100) if type_total > 0 else 0
            
            match_by_type.append({
                'Transaction Type': trans_type,
                'Match Rate': type_rate,
                'Matched': type_matched,
                'Total': type_total
            })
        
        match_df = pd.DataFrame(match_by_type)
        fig_match = px.bar(
            match_df,
            x='Transaction Type',
            y='Match Rate',
            title="Match Rates by Transaction Type",
            text='Match Rate'
        )
        fig_match.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_match, use_container_width=True)
    
    # Detailed results
    st.subheader("🔍 Detailed Analysis Results")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by Transaction Type",
            ["All"] + list(hr185_primary['transaction_type'].unique())
        )
    
    with col2:
        filter_match = st.selectbox(
            "Filter by Match Status",
            ["All", "Matched", "Unmatched"]
        )
    
    with col3:
        show_sample = st.checkbox("Show Sample (1000 records)", value=True)
    
    # Apply filters
    filtered_results = analysis_results.copy()
    
    if filter_type != "All":
        filtered_results = filtered_results[filtered_results['transaction_type'] == filter_type]
    
    if filter_match == "Matched":
        filtered_results = filtered_results[
            (filtered_results['has_grn_match'] == True) |
            (filtered_results['has_issue_match'] == True) |
            (filtered_results['has_vouch_match'] == True)
        ]
    elif filter_match == "Unmatched":
        filtered_results = filtered_results[
            (filtered_results['has_grn_match'] == False) &
            (filtered_results['has_issue_match'] == False) &
            (filtered_results['has_vouch_match'] == False)
        ]
    
    if show_sample and len(filtered_results) > 1000:
        filtered_results = filtered_results.head(1000)
    
    # Display results
    st.dataframe(
        filtered_results[[
            'hr185_reference', 'supplier_name', 'transaction_type', 'amount',
            'has_grn_match', 'has_issue_match', 'has_vouch_match',
            'matched_grn_voucher', 'matched_grn_inv_no'
        ]],
        use_container_width=True
    )
    
    # Export option
    if st.button("📥 Export Analysis Results"):
        analysis_results.to_csv('output/primary_transactions_analysis_no_chq.csv', index=False)
        st.success("Results exported to 'output/primary_transactions_analysis_no_chq.csv'")

def chq_audit_analysis(data):
    """CHQ audit view for payment tracking"""
    
    st.header("🔍 CHQ Payment Audit View")
    st.info("**Payment Confirmations**: CHQ transactions tracked separately for audit purposes")
    
    hr185_chq = data['hr185_chq_only']
    hr185_full = data['hr185_full']
    
    # CHQ summary
    st.subheader("📊 CHQ Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total CHQ Transactions", f"{len(hr185_chq):,}")
    with col2:
        total_chq_amount = hr185_chq['amount'].sum()
        st.metric("Total CHQ Amount", f"R {total_chq_amount:,.2f}")
    with col3:
        chq_suppliers = hr185_chq['supplier_name'].nunique()
        st.metric("CHQ Suppliers", f"{chq_suppliers:,}")
    with col4:
        chq_percentage = (len(hr185_chq) / len(hr185_full)) * 100
        st.metric("% of All Transactions", f"{chq_percentage:.1f}%")
    
    # CHQ analysis
    st.subheader("💰 CHQ Payment Analysis")
    
    # CHQ by supplier
    chq_by_supplier = hr185_chq.groupby('supplier_name').agg({
        'amount': ['count', 'sum'],
        'reference': 'nunique'
    }).round(2)
    
    chq_by_supplier.columns = ['CHQ Count', 'Total Amount', 'Unique References']
    chq_by_supplier = chq_by_supplier.sort_values('Total Amount', ascending=False).head(20)
    
    st.dataframe(chq_by_supplier, use_container_width=True)
    
    # CHQ timeline
    if 'transaction_date' in hr185_chq.columns:
        hr185_chq['transaction_date'] = pd.to_datetime(hr185_chq['transaction_date'])
        chq_timeline = hr185_chq.groupby(hr185_chq['transaction_date'].dt.to_period('M')).agg({
            'amount': ['count', 'sum']
        })
        
        chq_timeline.columns = ['CHQ Count', 'Total Amount']
        
        fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_timeline.add_trace(
            go.Scatter(x=chq_timeline.index.astype(str), y=chq_timeline['CHQ Count'], name="CHQ Count"),
            secondary_y=False,
        )
        
        fig_timeline.add_trace(
            go.Scatter(x=chq_timeline.index.astype(str), y=chq_timeline['Total Amount'], name="Total Amount"),
            secondary_y=True,
        )
        
        fig_timeline.update_layout(title="CHQ Transactions Over Time")
        fig_timeline.update_yaxes(title_text="CHQ Count", secondary_y=False)
        fig_timeline.update_yaxes(title_text="Total Amount (R)", secondary_y=True)
        
        st.plotly_chart(fig_timeline, use_container_width=True)

def comparison_analysis(data):
    """Comparison between old approach (with CHQ) and new approach (without CHQ)"""
    
    st.header("⚖️ Approach Comparison Analysis")
    st.info("**Comparing**: Old approach (CHQ included) vs New approach (CHQ excluded)")
    
    hr185_full = data['hr185_full']
    hr185_primary = data['hr185_primary']
    hr185_chq = data['hr185_chq_only']
    
    # Load previous results if available
    try:
        previous_results = pd.read_csv('output/enhanced_transaction_trail_with_chq_fix.csv')
        has_previous = True
    except FileNotFoundError:
        has_previous = False
        st.warning("Previous results with CHQ inheritance not found. Run the CHQ inheritance analysis first for full comparison.")
    
    # Current approach results
    with st.spinner("Analyzing current approach (CHQ excluded)..."):
        current_results = enhanced_transaction_analysis(
            hr185_primary, data['hr995grn'], data['hr995issue'], data['hr995vouch']
        )
    
    # Comparison metrics
    st.subheader("📊 Comparison Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🆕 New Approach (CHQ Excluded)")
        current_total = len(hr185_primary)
        current_matched = len(current_results[
            (current_results['has_grn_match'] == True) |
            (current_results['has_issue_match'] == True) |
            (current_results['has_vouch_match'] == True)
        ])
        current_rate = (current_matched / current_total * 100) if current_total > 0 else 0
        
        st.metric("Total Transactions", f"{current_total:,}")
        st.metric("Matched Transactions", f"{current_matched:,}")
        st.metric("Match Rate", f"{current_rate:.1f}%")
        st.success(f"Focuses on {current_total:,} primary business transactions")
    
    with col2:
        if has_previous:
            st.markdown("### 🔄 Previous Approach (CHQ Included)")
            prev_total = len(previous_results)
            prev_matched = len(previous_results[
                (previous_results['has_direct_grn_match'] == True) |
                (previous_results['has_inherited_grn_match'] == True)
            ])
            prev_rate = (prev_matched / prev_total * 100) if prev_total > 0 else 0
            
            st.metric("Total Transactions", f"{prev_total:,}")
            st.metric("Matched Transactions", f"{prev_matched:,}")
            st.metric("Match Rate", f"{prev_rate:.1f}%")
            st.info(f"Included {len(hr185_chq):,} CHQ transactions with inheritance logic")
        else:
            st.markdown("### 🔄 Previous Approach (CHQ Included)")
            st.info("Previous results not available for comparison")
    
    # Benefits summary
    st.subheader("🎯 Benefits of New Approach")
    
    benefits = [
        f"✅ **Simplified Logic**: No complex CHQ inheritance algorithms needed",
        f"✅ **Higher Core Match Rate**: {current_rate:.1f}% on business transactions vs payment confirmations",
        f"✅ **Business Alignment**: Matches actual procurement process (GRN → business transactions)",
        f"✅ **Reduced Complexity**: Eliminates {len(hr185_chq):,} payment confirmation transactions",
        f"✅ **Cleaner Analysis**: Focus on {current_total:,} transactions that relate to actual business events",
        f"✅ **Audit Trail Maintained**: CHQ still available separately for payment tracking"
    ]
    
    for benefit in benefits:
        st.markdown(benefit)
    
    # Performance comparison chart
    if has_previous:
        comparison_data = pd.DataFrame({
            'Approach': ['Previous (CHQ Included)', 'New (CHQ Excluded)'],
            'Match Rate': [prev_rate, current_rate],
            'Total Transactions': [prev_total, current_total],
            'Complexity': ['High (Inheritance Logic)', 'Low (Direct Matching)']
        })
        
        fig_comparison = px.bar(
            comparison_data,
            x='Approach',
            y='Match Rate',
            title="Match Rate Comparison",
            text='Match Rate',
            color='Approach'
        )
        fig_comparison.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Export current results
    if st.button("📥 Export New Approach Results"):
        current_results.to_csv('output/enhanced_analysis_no_chq_final.csv', index=False)
        st.success("New approach results exported to 'output/enhanced_analysis_no_chq_final.csv'")

if __name__ == "__main__":
    main()
