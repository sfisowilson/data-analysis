#!/usr/bin/env python3
"""
Advanced Stock Data Analytics Dashboard
A comprehensive web-based dashboard with detailed drill-down capabilities and extensive visualizations.

This application provides 25+ interactive charts and graphs for deep analysis of stock data,
including financial trends, supplier analytics, inventory management, and operational insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import os
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Optional
import calendar

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Hide Streamlit style elements
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    .stApp > header {display: none;}
    .css-1y4p8pa {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Advanced Stock Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .sidebar-section {
        padding: 1rem 0;
        border-bottom: 1px solid #e6e6e6;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedStockDashboard:
    """Advanced dashboard class with comprehensive analytics and drill-down capabilities."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.output_folder = Path("output")
        self.data_cache = {}
        # Data source mapping for tooltips
        self.data_sources = {
            'hr995_grn.csv': 'GRN (Goods Received Notes) - Items received from suppliers',
            'hr995_issue.csv': 'Issue Records - Items issued from inventory', 
            'hr995_voucher.csv': 'Voucher Records - Payment and authorization data',
            'hr995_redundant.csv': 'Redundant Records - Duplicate or obsolete entries',
            'all_stock_data.csv': 'Combined Stock Data - All consolidated inventory records',
            'suppliers.csv': 'Supplier Master Data - Supplier information and details',
            'stock_adjustments.csv': 'Stock Adjustments - Inventory corrections and modifications',
            'individual_hr185_transactions.csv': 'HR185 Transaction Reports - Supplier transaction history from PDF reports',
            'individual_hr990_expenditure.csv': 'HR990 Expenditure Statistics - Expenditure analysis from PDF reports',
            'variance_report.csv': 'Variance Reports - Stock variance and discrepancy analysis',
            'hr450_data.csv': 'HR450 Data - Additional inventory tracking data',
            'objective_1_item_frequency_by_supplier.csv': 'Analysis Report - Item frequency by supplier',
            'objective_2_stock_audit_trail.csv': 'Analysis Report - Stock audit trail',
            'objective_3_hr995_report.csv': 'Analysis Report - HR995 comprehensive report',
            'objective_4_end_to_end_process.csv': 'Analysis Report - End-to-end process analysis',
            'objective_5_stock_balances_by_year.csv': 'Analysis Report - Stock balances by year'
        }
    
    def get_data_source_tooltip(self, data_files):
        """Generate tooltip text explaining data sources."""
        if isinstance(data_files, str):
            data_files = [data_files]
        
        sources = []
        for file in data_files:
            if file in self.data_sources:
                sources.append(f"• {self.data_sources[file]}")
        
        if sources:
            return f"Data Sources:<br>{'<br>'.join(sources)}"
        return "Data source information not available"
        
    @st.cache_data
    def load_data(_self, filename):
        """Load and cache data files with improved date handling for multiple formats."""
        file_path = _self.output_folder / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                
                # Handle different date formats
                for col in df.columns:
                    if 'date' in col.lower():
                        if df[col].dtype == 'object':
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                        
                        # Check if dates are invalid (showing as 1900-01-01 or similar)
                        if df[col].notna().any():
                            valid_dates = df[col].dropna()
                            if len(valid_dates) > 0:
                                # If most dates are 1900-01-01, they're likely corrupted
                                year_1900_count = (valid_dates.dt.year == 1900).sum()
                                if year_1900_count > len(valid_dates) * 0.8:
                                    # Try to convert as YYYYMMDD format
                                    numeric_dates = pd.to_numeric(df[col].astype(str).str.replace('-', ''), errors='coerce')
                                    valid_numeric = numeric_dates.dropna()
                                    
                                    if len(valid_numeric) > 0:
                                        df[f'{col}_converted'] = pd.NaT
                                        for idx in valid_numeric.index:
                                            try:
                                                date_str = str(int(valid_numeric.loc[idx]))
                                                if len(date_str) == 8:  # YYYYMMDD
                                                    year = int(date_str[:4])
                                                    month = int(date_str[4:6])
                                                    day = int(date_str[6:8])
                                                    if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                                                        df.loc[idx, f'{col}_converted'] = pd.Timestamp(year=year, month=month, day=day)
                                            except:
                                                continue
                                        
                                        # Replace original column if conversion successful
                                        if df[f'{col}_converted'].notna().sum() > 0:
                                            df[col] = df[f'{col}_converted']
                                            df = df.drop(columns=[f'{col}_converted'])
                
                # Convert fin_period to proper dates (YYYYMM format)
                if 'fin_period' in df.columns:
                    fin_period_series = pd.to_numeric(df['fin_period'], errors='coerce')
                    valid_periods = fin_period_series.dropna()
                    
                    if len(valid_periods) > 0:
                        # Convert YYYYMM to datetime
                        df['period_date'] = pd.NaT
                        for idx in valid_periods.index:
                            try:
                                year = int(valid_periods.loc[idx] // 100)
                                month = int(valid_periods.loc[idx] % 100)
                                if 1 <= month <= 12 and year >= 2000:
                                    df.loc[idx, 'period_date'] = pd.Timestamp(year=year, month=month, day=1)
                            except:
                                continue
                        
                        # Format period for display
                        df['period_display'] = df['period_date'].dt.strftime('%Y-%m')
                        
                        # If original date column is mostly empty, use period_date as primary date
                        if 'date' in df.columns and df['date'].isna().sum() > len(df) * 0.8:
                            df['date'] = df['period_date']
                
                # Handle other YYYYMMDD date columns that might not have been caught
                for col in df.columns:
                    if any(term in col.lower() for term in ['grn_date', 'cheq_date', 'last_move_date', 'issue_date']):
                        if df[col].dtype in ['object', 'int64', 'float64']:
                            # Try to convert YYYYMMDD format
                            numeric_dates = pd.to_numeric(df[col], errors='coerce')
                            valid_numeric = numeric_dates.dropna()
                            
                            if len(valid_numeric) > 0:
                                df[f'{col}_converted'] = pd.NaT
                                for idx in valid_numeric.index:
                                    try:
                                        date_val = int(valid_numeric.loc[idx])
                                        date_str = str(date_val)
                                        
                                        if len(date_str) == 8:  # YYYYMMDD
                                            year = int(date_str[:4])
                                            month = int(date_str[4:6])
                                            day = int(date_str[6:8])
                                            if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                                                df.loc[idx, f'{col}_converted'] = pd.Timestamp(year=year, month=month, day=day)
                                    except:
                                        continue
                                
                                # Replace original column if conversion successful
                                if df[f'{col}_converted'].notna().sum() > 0:
                                    df[col] = df[f'{col}_converted']
                                    df = df.drop(columns=[f'{col}_converted'])
                
                return df
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
                return pd.DataFrame()
        else:
            st.warning(f"File {filename} not found. Please run the data processor first.")
            return pd.DataFrame()
    
    def apply_filters(self, df, filters):
        """Apply sidebar filters to dataframe."""
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Apply supplier filter
        if filters.get('supplier') and filters['supplier'] != "All Suppliers":
            if 'supplier_name' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['supplier_name'] == filters['supplier']]
            elif 'supplier' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['supplier'] == filters['supplier']]
        
        # Apply department filter
        if filters.get('department') and filters['department'] != "All Departments":
            if 'store_no' in filtered_df.columns:
                if filters['department'] == "Main Store":
                    filtered_df = filtered_df[filtered_df['store_no'].str.contains('MAIN', case=False, na=False)]
                elif filters['department'] == "Direct":
                    filtered_df = filtered_df[filtered_df['store_no'].str.contains('DIRECT', case=False, na=False)]
        
        # Apply value filter
        if filters.get('min_value', 0) > 0:
            value_cols = ['nett_grn_amt', 'amount', 'value', 'total_value']
            for col in value_cols:
                if col in filtered_df.columns:
                    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
                    filtered_df = filtered_df[filtered_df[col] >= filters['min_value']]
                    break
        
        return filtered_df
    
    def normalize_reference(self, ref):
        """Normalize reference numbers for proper data linkage."""
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
    
    def normalize_hr185_reference(self, ref):
        """Normalize HR185 reference for linking to HR995grn Inv No.
        HR185 references have leading zeros (e.g., '0001015578') that link to
        HR995grn Inv No without leading zeros (e.g., '1015578').
        """
        if pd.isna(ref):
            return ref
        
        ref_str = str(ref).strip()
        
        # Remove leading zeros for HR185 INV reference linking
        if ref_str.startswith('000') and len(ref_str) >= 7:
            try:
                # Convert to int to remove leading zeros, then back to string
                return str(int(ref_str))
            except:
                return ref_str
        
        return ref_str
    
    def load_linked_data(self, filters=None):
        """Load all data with proper business logic linkages applied."""
        # Load base datasets
        grn_df = self.load_data("individual_hr995grn.csv")
        issue_df = self.load_data("individual_hr995issue.csv") 
        voucher_df = self.load_data("individual_hr995vouch.csv")
        hr390_df = self.load_data("individual_hr390_movement_data.csv")
        hr185_df = self.load_data("individual_hr185_transactions.csv")
        
        # Apply normalization for proper linkages
        if not grn_df.empty:
            grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(self.normalize_reference)
            grn_df['voucher_normalized'] = grn_df['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        
        if not issue_df.empty:
            # HR995Issue 'Requisition No' links with HR390 'reference number'
            issue_df['requisition_no_normalized'] = issue_df['requisition_no'].apply(self.normalize_reference)
        
        if not voucher_df.empty:
            voucher_df['voucher_no_normalized'] = voucher_df['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        
        if hr390_df is not None and not hr390_df.empty:
            hr390_df['reference_normalized'] = hr390_df['reference'].apply(self.normalize_reference)
        
        if hr185_df is not None and not hr185_df.empty:
            # Special handling for HR185: INV transactions link to HR995grn Inv No
            # HR185 reference (e.g., '0001015578') → HR995grn Inv No (e.g., '1015578')
            hr185_df['reference_normalized'] = hr185_df['reference'].apply(self.normalize_hr185_reference)
            
            # Apply CHQ exclusion if requested
            if filters and filters.get('exclude_chq', False):
                # Focus on primary business transactions only (exclude CHQ payment confirmations)
                primary_transaction_types = ['INV', 'VCH', 'CN', 'DN']
                if 'transaction_type' in hr185_df.columns:
                    hr185_df = hr185_df[hr185_df['transaction_type'].str.upper().isin(primary_transaction_types)].copy()
                    # Add performance indicator
                    hr185_df['is_primary_transaction'] = True
            
            # Filter for INV transactions only (these link to HR995grn)
            if 'transaction_type' in hr185_df.columns:
                hr185_df['is_inv_transaction'] = hr185_df['transaction_type'].str.upper() == 'INV'
        
        # Create linked datasets with proper relationships
        linked_data = {
            'grn': grn_df,
            'issue': issue_df,
            'voucher': voucher_df,
            'hr390': hr390_df,
            'hr185': hr185_df
        }
        
        # Apply filters to all datasets
        if filters:
            for key, df in linked_data.items():
                if df is not None and not df.empty:
                    linked_data[key] = self.apply_filters(df, filters)
        
        return linked_data
    
    def enhanced_reference_matching(self, hr390_ref, hr995_refs):
        """4-Strategy Enhanced Reference Matching as documented.
        Handles leading zero mismatches between HR390 and HR995 systems.
        """
        if pd.isna(hr390_ref):
            return None
            
        hr390_str = str(hr390_ref).strip()
        
        for hr995_ref in hr995_refs:
            if pd.isna(hr995_ref):
                continue
                
            hr995_str = str(hr995_ref).strip()
            
            # Strategy 1: Direct string match
            if hr390_str == hr995_str:
                return hr995_ref
            
            # Strategy 2: Remove leading zeros from HR390 reference
            try:
                hr390_no_zeros = str(int(hr390_str.lstrip('0'))) if hr390_str.lstrip('0') else '0'
                if hr390_no_zeros == hr995_str:
                    return hr995_ref
            except:
                pass
            
            # Strategy 3: Add leading zeros to HR995 data (6-digit padding)
            try:
                hr995_padded = hr995_str.zfill(6)
                if hr390_str == hr995_padded:
                    return hr995_ref
            except:
                pass
            
            # Strategy 4: Integer comparison
            try:
                if int(hr390_str) == int(hr995_str):
                    return hr995_ref
            except:
                pass
        
        return None
    
    def get_hr995_dataset_for_transaction_type(self, transaction_type, linked_data):
        """Route HR390 transaction types to correct HR995 datasets.
        Based on documentation: ISS→HR995issue, GRN→HR995grn, VOUCH→HR995vouch
        """
        transaction_type = str(transaction_type).upper().strip()
        
        if transaction_type == 'ISS' or 'ISSUE' in transaction_type:
            return linked_data.get('issue')
        elif transaction_type == 'GRN' or 'GOODS' in transaction_type:
            return linked_data.get('grn')
        elif transaction_type == 'VOUCH' or 'VOUCHER' in transaction_type:
            return linked_data.get('voucher')
        else:
            return None
    
    def identify_inv_chq_payment_pairs(self, hr185_df):
        """Identify INV-CHQ payment pairs for inheritance linking."""
        if hr185_df is None or hr185_df.empty:
            return []
        
        # Find suppliers with both INV and CHQ transactions
        suppliers_with_inv = set(hr185_df[hr185_df['transaction_type'] == 'INV']['supplier_code'])
        suppliers_with_chq = set(hr185_df[hr185_df['transaction_type'] == 'CHQ']['supplier_code'])
        common_suppliers = suppliers_with_inv.intersection(suppliers_with_chq)
        
        payment_pairs = []
        
        for supplier_code in common_suppliers:
            supplier_data = hr185_df[hr185_df['supplier_code'] == supplier_code].copy()
            supplier_data = supplier_data.sort_values(['transaction_date', 'transaction_type'])
            
            # Find matching INV-CHQ pairs within supplier
            for i, inv_row in supplier_data[supplier_data['transaction_type'] == 'INV'].iterrows():
                # Look for CHQ transactions with same date and amount
                matching_chq = supplier_data[
                    (supplier_data['transaction_type'] == 'CHQ') &
                    (supplier_data['transaction_date'] == inv_row['transaction_date']) &
                    (abs(supplier_data['amount'] - inv_row['amount']) < 0.01)
                ]
                
                for j, chq_row in matching_chq.iterrows():
                    payment_pairs.append({
                        'supplier_code': supplier_code,
                        'supplier_name': inv_row['supplier_name'],
                        'date': inv_row['transaction_date'],
                        'inv_reference': inv_row['reference'],
                        'chq_reference': chq_row['reference'],
                        'amount': inv_row['amount'],
                        'inv_ref_normalized': inv_row.get('reference_normalized', ''),
                        'chq_ref_normalized': chq_row.get('reference_normalized', '')
                    })
        
        return payment_pairs
    
    def enhanced_hr185_transaction_analysis(self, linked_data):
        """Enhanced HR185 transaction analysis with CHQ inheritance linking."""
        hr185_df = linked_data.get('hr185')
        grn_df = linked_data.get('grn')
        
        if hr185_df is None or hr185_df.empty or grn_df is None or grn_df.empty:
            return {}
        
        # Normalize reference function
        def normalize_reference(ref):
            if pd.isna(ref):
                return ''
            ref_str = str(ref).strip()
            try:
                return str(int(ref_str))
            except ValueError:
                return ref_str
        
        # Ensure normalized columns exist
        if 'reference_normalized' not in hr185_df.columns:
            hr185_df['reference_normalized'] = hr185_df['reference'].apply(normalize_reference)
        if 'inv_no_normalized' not in grn_df.columns:
            grn_df['inv_no_normalized'] = grn_df['inv_no'].apply(normalize_reference)
        
        # Identify INV-CHQ payment pairs
        payment_pairs = self.identify_inv_chq_payment_pairs(hr185_df)
        
        # Create mapping for quick lookup
        chq_to_inv_map = {}
        for pair in payment_pairs:
            chq_to_inv_map[str(pair['chq_reference'])] = pair['inv_reference']
        
        # Analyze each transaction
        analysis_results = {
            'total_transactions': len(hr185_df),
            'inv_transactions': len(hr185_df[hr185_df['transaction_type'] == 'INV']),
            'chq_transactions': len(hr185_df[hr185_df['transaction_type'] == 'CHQ']),
            'direct_matches': 0,
            'inherited_matches': 0,
            'unmatched': 0,
            'payment_pairs_identified': len(payment_pairs),
            'chq_fixed': 0,
            'detailed_results': []
        }
        
        for _, row in hr185_df.iterrows():
            ref = str(row['reference'])
            ref_norm = normalize_reference(ref)
            transaction_type = row['transaction_type']
            
            # Check for direct GRN match
            direct_match = len(grn_df[grn_df['inv_no_normalized'] == ref_norm]) > 0
            inherited_match = False
            match_notes = ''
            
            if direct_match:
                analysis_results['direct_matches'] += 1
                match_notes = 'Direct GRN match'
            elif transaction_type == 'CHQ' and ref in chq_to_inv_map:
                # CHQ inheritance logic
                paired_inv_ref = chq_to_inv_map[ref]
                paired_inv_norm = normalize_reference(paired_inv_ref)
                
                # Check if paired INV has GRN match
                if len(grn_df[grn_df['inv_no_normalized'] == paired_inv_norm]) > 0:
                    inherited_match = True
                    analysis_results['inherited_matches'] += 1
                    analysis_results['chq_fixed'] += 1
                    match_notes = f'Payment for INV {paired_inv_ref} (inherited GRN match)'
                else:
                    analysis_results['unmatched'] += 1
                    match_notes = f'Payment for INV {paired_inv_ref} (INV also unmatched)'
            else:
                analysis_results['unmatched'] += 1
                if transaction_type == 'CHQ':
                    match_notes = 'Standalone CHQ transaction'
                else:
                    match_notes = f'{transaction_type} transaction'
            
            analysis_results['detailed_results'].append({
                'reference': ref,
                'transaction_type': transaction_type,
                'supplier_name': row['supplier_name'],
                'amount': row['amount'],
                'has_direct_match': direct_match,
                'has_inherited_match': inherited_match,
                'match_notes': match_notes
            })
        
        return analysis_results
    
    def enhanced_transaction_trail_analysis(self, linked_data):
        """Perform transaction-type-specific enhanced matching analysis."""
        hr390_df = linked_data.get('hr390')
        
        if hr390_df is None or hr390_df.empty:
            return {}
        
        trail_results = {
            'ISS': {'total': 0, 'matched': 0, 'unmatched': []},
            'GRN': {'total': 0, 'matched': 0, 'unmatched': []},
            'VOUCH': {'total': 0, 'matched': 0, 'unmatched': []}
        }
        
        # Group HR390 transactions by type
        if 'transaction_type' in hr390_df.columns:
            for transaction_type in trail_results.keys():
                type_df = hr390_df[hr390_df['transaction_type'].str.upper() == transaction_type]
                
                if not type_df.empty:
                    trail_results[transaction_type]['total'] = len(type_df)
                    
                    # Get corresponding HR995 dataset
                    hr995_df = self.get_hr995_dataset_for_transaction_type(transaction_type, linked_data)
                    
                    if hr995_df is not None and not hr995_df.empty:
                        # Perform enhanced matching
                        hr390_refs = type_df['reference'].dropna().unique()
                        
                        if transaction_type == 'ISS':
                            hr995_refs = hr995_df['requisition_no'].dropna().unique()
                        elif transaction_type == 'GRN':
                            hr995_refs = hr995_df['grn_no'].dropna().unique() if 'grn_no' in hr995_df.columns else []
                        elif transaction_type == 'VOUCH':
                            hr995_refs = hr995_df['voucher_no'].dropna().unique() if 'voucher_no' in hr995_df.columns else []
                        else:
                            hr995_refs = []
                        
                        # Enhanced matching for each reference
                        for hr390_ref in hr390_refs:
                            match = self.enhanced_reference_matching(hr390_ref, [str(x) for x in hr995_refs])
                            if match:
                                trail_results[transaction_type]['matched'] += 1
                            else:
                                trail_results[transaction_type]['unmatched'].append(hr390_ref)
        
        return trail_results
    
    def create_relationship_analysis(self, linked_data):
        """Analyze data relationships using corrected business logic."""
        grn_df = linked_data['grn']
        issue_df = linked_data['issue']
        voucher_df = linked_data['voucher']
        hr390_df = linked_data['hr390']
        hr185_df = linked_data['hr185']
        
        st.subheader("🔗 Data Relationship Analysis (Corrected)")
        st.info("✅ **Enhanced Business Logic Linkages**: HR995Issue ↔ HR390 (4-strategy reference matching), HR995GRN ↔ HR185 INV (invoice payment tracking), HR995GRN ↔ HR995Voucher")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📋 Issue → HR390 Linkage (Enhanced)")
            if not issue_df.empty and hr390_df is not None and not hr390_df.empty:
                # Enhanced 4-strategy matching for HR995Issue 'Requisition No' ↔ HR390 'reference'
                
                # Get unique references for enhanced matching
                issue_refs = issue_df['requisition_no'].dropna().unique()
                hr390_refs = hr390_df['reference'].dropna().unique()
                
                # Apply enhanced matching
                enhanced_matches = 0
                unmatched_issues = []
                
                for issue_ref in issue_refs:
                    match = self.enhanced_reference_matching(str(issue_ref), [str(x) for x in hr390_refs])
                    if match:
                        enhanced_matches += 1
                    else:
                        unmatched_issues.append(issue_ref)
                
                st.metric("Issues with Enhanced HR390 Link", enhanced_matches)
                st.metric("Issues without HR390 Link", len(unmatched_issues))
                
                if len(issue_refs) > 0:
                    enhanced_rate = enhanced_matches / len(issue_refs) * 100
                    st.metric("Enhanced Linkage Rate", f"{enhanced_rate:.1f}%")
                    
                    # Compare with basic matching
                    basic_matches = len(set(issue_df['requisition_no_normalized'].dropna()) & 
                                       set(hr390_df['reference_normalized'].dropna()))
                    basic_rate = basic_matches / len(issue_refs) * 100 if len(issue_refs) > 0 else 0
                    
                    improvement = enhanced_rate - basic_rate
                    if improvement > 0:
                        st.success(f"🚀 Enhanced matching improved by {improvement:.1f}%")
                    
                    st.info(f"💡 Basic matching: {basic_rate:.1f}% → Enhanced: {enhanced_rate:.1f}%")
            else:
                st.warning("Issue or HR390 data not available")
        
        with col2:
            st.markdown("### 📦 GRN → HR185 Invoice Linkage")
            if not grn_df.empty and hr185_df is not None and not hr185_df.empty:
                # HR995GRN 'Inv No' links to HR185 INV 'reference' column (with leading zeros)
                # Only consider INV transactions in HR185
                hr185_inv_df = hr185_df
                if 'transaction_type' in hr185_df.columns:
                    hr185_inv_df = hr185_df[hr185_df['transaction_type'].str.upper() == 'INV']
                
                if not hr185_inv_df.empty:
                    # Compare normalized invoice numbers
                    grn_inv_nos = set(grn_df['inv_no_normalized'].astype(str).dropna())
                    hr185_refs = set(hr185_inv_df['reference_normalized'].astype(str).dropna())
                    
                    linked_invoices = grn_inv_nos & hr185_refs
                    unlinked_grns = grn_inv_nos - hr185_refs
                    unlinked_hr185 = hr185_refs - grn_inv_nos
                    
                    st.metric("GRN Invoices with HR185 Payment", len(linked_invoices))
                    st.metric("GRN Invoices without Payment", len(unlinked_grns))
                    st.metric("HR185 Payments without GRN", len(unlinked_hr185))
                    
                    if len(grn_inv_nos) > 0:
                        payment_rate = len(linked_invoices) / len(grn_inv_nos) * 100
                        st.metric("Invoice → Payment Rate", f"{payment_rate:.1f}%")
                        
                    # Show payment analysis
                    if len(linked_invoices) > 0:
                        st.success(f"✅ Found {len(linked_invoices)} confirmed invoice payments")
                        
                        # Show sample links
                        sample_links = []
                        for inv_no in list(linked_invoices)[:5]:  # Show first 5
                            grn_row = grn_df[grn_df['inv_no_normalized'].astype(str) == inv_no].iloc[0]
                            hr185_row = hr185_inv_df[hr185_inv_df['reference_normalized'].astype(str) == inv_no].iloc[0]
                            
                            sample_links.append({
                                'GRN_Inv_No': grn_row.get('inv_no', 'N/A'),
                                'HR185_Reference': hr185_row.get('reference', 'N/A'),
                                'Supplier': hr185_row.get('supplier_name', grn_row.get('supplier_name', 'N/A')),
                                'Amount': hr185_row.get('amount', 'N/A')
                            })
                        
                        if sample_links:
                            st.markdown("**Sample Invoice-Payment Links:**")
                            st.dataframe(pd.DataFrame(sample_links), use_container_width=True, hide_index=True)
                else:
                    st.warning("No INV transactions found in HR185 data")
            else:
                st.warning("GRN or HR185 data not available")
        
        with col3:
            st.markdown("### 💳 GRN → Voucher Linkage")
            if not grn_df.empty and not voucher_df.empty:
                # HR995GRN 'Voucher' links to HR995VOUCHER 'Voucher No'
                grn_vouchers = set(grn_df['voucher_normalized'].dropna())
                actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
                
                linked_vouchers = grn_vouchers & actual_vouchers
                unlinked_vouchers = grn_vouchers - actual_vouchers
                
                st.metric("GRNs with Voucher Link", len(linked_vouchers))
                st.metric("GRNs without Voucher Link", len(unlinked_vouchers))
                
                if len(grn_vouchers) > 0:
                    linkage_rate = len(linked_vouchers) / len(grn_vouchers) * 100
                    st.metric("GRN → Voucher Linkage Rate", f"{linkage_rate:.1f}%")
            else:
                st.warning("GRN or Voucher data not available")
        
        # Enhanced Transaction Trail Analysis
        st.markdown("---")
        st.subheader("🔍 Enhanced Transaction Trail Analysis")
        st.info("📋 **Transaction-Type-Specific Matching**: Routes HR390 transactions to correct HR995 datasets (ISS→Issue, GRN→GRN, VOUCH→Voucher)")
        
        trail_results = self.enhanced_transaction_trail_analysis(linked_data)
        
        if trail_results:
            trail_col1, trail_col2, trail_col3 = st.columns(3)
            
            with trail_col1:
                st.markdown("### 📤 ISS (Issue) Transactions")
                iss_data = trail_results.get('ISS', {})
                if iss_data.get('total', 0) > 0:
                    st.metric("Total ISS Transactions", iss_data['total'])
                    st.metric("Enhanced Matches Found", iss_data['matched'])
                    match_rate = (iss_data['matched'] / iss_data['total'] * 100) if iss_data['total'] > 0 else 0
                    st.metric("ISS Match Rate", f"{match_rate:.1f}%")
                else:
                    st.info("No ISS transactions found")
            
            with trail_col2:
                st.markdown("### 📦 GRN Transactions")
                grn_data = trail_results.get('GRN', {})
                if grn_data.get('total', 0) > 0:
                    st.metric("Total GRN Transactions", grn_data['total'])
                    st.metric("Enhanced Matches Found", grn_data['matched'])
                    match_rate = (grn_data['matched'] / grn_data['total'] * 100) if grn_data['total'] > 0 else 0
                    st.metric("GRN Match Rate", f"{match_rate:.1f}%")
                else:
                    st.info("No GRN transactions found")
            
            with trail_col3:
                st.markdown("### 💳 VOUCH Transactions")
                vouch_data = trail_results.get('VOUCH', {})
                if vouch_data.get('total', 0) > 0:
                    st.metric("Total VOUCH Transactions", vouch_data['total'])
                    st.metric("Enhanced Matches Found", vouch_data['matched'])
                    match_rate = (vouch_data['matched'] / vouch_data['total'] * 100) if vouch_data['total'] > 0 else 0
                    st.metric("VOUCH Match Rate", f"{match_rate:.1f}%")
                else:
                    st.info("No VOUCH transactions found")
        
        # Enhanced HR185 CHQ Analysis (NEW - Fixes unmatched CHQ issue)
        st.markdown("---")
        st.subheader("💰 Enhanced HR185 Payment Analysis (CHQ Fix)")
        st.info("🔧 **CHQ Inheritance Linking**: Resolves unmatched CHQ transactions by linking them to paired INV transactions with GRN matches")
        
        hr185_analysis = self.enhanced_hr185_transaction_analysis(linked_data)
        
        if hr185_analysis:
            hr185_col1, hr185_col2, hr185_col3, hr185_col4 = st.columns(4)
            
            with hr185_col1:
                st.markdown("### 📊 Overall HR185 Analysis")
                st.metric("Total HR185 Transactions", hr185_analysis['total_transactions'])
                st.metric("Direct GRN Matches", hr185_analysis['direct_matches'])
                
                total_matched = hr185_analysis['direct_matches'] + hr185_analysis['inherited_matches']
                match_rate = (total_matched / hr185_analysis['total_transactions'] * 100) if hr185_analysis['total_transactions'] > 0 else 0
                st.metric("Total Match Rate", f"{match_rate:.1f}%")
            
            with hr185_col2:
                st.markdown("### 📋 INV Transactions")
                st.metric("Total INV Transactions", hr185_analysis['inv_transactions'])
                
                # Most INV transactions should have direct matches
                inv_match_rate = (hr185_analysis['direct_matches'] / hr185_analysis['inv_transactions'] * 100) if hr185_analysis['inv_transactions'] > 0 else 0
                st.metric("INV Match Rate", f"{inv_match_rate:.1f}%")
            
            with hr185_col3:
                st.markdown("### 💳 CHQ Transactions")
                st.metric("Total CHQ Transactions", hr185_analysis['chq_transactions'])
                st.metric("CHQ Fixed (Inherited)", hr185_analysis['chq_fixed'])
                
                chq_fix_rate = (hr185_analysis['chq_fixed'] / hr185_analysis['chq_transactions'] * 100) if hr185_analysis['chq_transactions'] > 0 else 0
                st.metric("CHQ Fix Rate", f"{chq_fix_rate:.1f}%")
                
                if hr185_analysis['chq_fixed'] > 0:
                    st.success(f"✅ Fixed {hr185_analysis['chq_fixed']} unmatched CHQ!")
            
            with hr185_col4:
                st.markdown("### 🔗 Payment Pairs")
                st.metric("INV-CHQ Pairs Found", hr185_analysis['payment_pairs_identified'])
                st.metric("Inherited Matches", hr185_analysis['inherited_matches'])
                st.metric("Still Unmatched", hr185_analysis['unmatched'])
                
                if hr185_analysis['payment_pairs_identified'] > 0:
                    st.info(f"💡 {hr185_analysis['payment_pairs_identified']} payment cycles identified")
            
            # Show improvement summary
            if hr185_analysis['chq_fixed'] > 0:
                st.markdown("---")
                st.success(f"""
                🎯 **CHQ Linking Improvement Summary:**
                - **Before Fix**: {hr185_analysis['chq_transactions'] - hr185_analysis['chq_fixed']} CHQ transactions unmatched
                - **After Fix**: {hr185_analysis['chq_transactions'] - hr185_analysis['chq_fixed']} CHQ transactions still unmatched  
                - **Improvement**: +{hr185_analysis['chq_fixed']} CHQ transactions now properly linked via INV inheritance
                - **Business Impact**: Enhanced audit trail completeness and payment cycle traceability
                """)
            
            # Sample fixed CHQ transactions
            fixed_chqs = [result for result in hr185_analysis['detailed_results'] 
                         if result['has_inherited_match'] and result['transaction_type'] == 'CHQ']
            
            if fixed_chqs:
                st.markdown("---")
                st.markdown("### 🔧 Sample Fixed CHQ Transactions")
                sample_fixed = pd.DataFrame(fixed_chqs[:10])  # Show first 10
                st.dataframe(
                    sample_fixed[['reference', 'supplier_name', 'amount', 'match_notes']],
                    use_container_width=True,
                    hide_index=True
                )

    def load_filtered_data(self, filename, filters=None):
        """Load data and apply filters if provided."""
        df = self.load_data(filename)
        if filters:
            df = self.apply_filters(df, filters)
        return df
    
    def clean_financial_data(self, df, amount_col):
        """Clean financial data for better analysis."""
        if amount_col in df.columns:
            df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')
            df = df[df[amount_col] > 0]  # Remove zero or negative amounts
        return df
    
    def get_time_period_data(self, df, date_col, period='monthly'):
        """Extract time period data for trend analysis with improved date handling."""
        # Try multiple date column options
        available_date_cols = []
        for col in ['period_date', 'date', date_col]:
            if col in df.columns and df[col].notna().any():
                available_date_cols.append(col)
        
        if not available_date_cols:
            # Use period_display if available
            if 'period_display' in df.columns:
                df['period'] = df['period_display']
                return df
            return df
        
        # Use the best available date column
        best_date_col = available_date_cols[0]
        df = df.dropna(subset=[best_date_col])
        
        if period == 'monthly':
            df['period'] = df[best_date_col].dt.to_period('M')
        elif period == 'quarterly':
            df['period'] = df[best_date_col].dt.to_period('Q')
        elif period == 'yearly':
            df['period'] = df[best_date_col].dt.to_period('Y')
        
        return df
    
    def create_executive_summary(self, filters=None):
        """Create executive summary with key metrics."""
        st.markdown('<h1 class="main-header">📊 Advanced Stock Analytics Dashboard</h1>', unsafe_allow_html=True)
        
        # Load key datasets
        grn_df = self.load_filtered_data("individual_hr995grn.csv", filters)
        issue_df = self.load_filtered_data("individual_hr995issue.csv", filters)
        voucher_df = self.load_data("individual_hr995vouch.csv")
        audit_df = self.load_data("objective_2_stock_audit_trail.csv")
        
        # Load PDF datasets
        hr185_df = self.load_data("individual_hr185_transactions.csv")
        hr990_df = self.load_data("individual_hr990_expenditure.csv")
        
        # Executive metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            if not grn_df.empty and 'nett_grn_amt' in grn_df.columns:
                total_grn_value = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce').sum()
                st.metric("Total GRN Value", f"R{total_grn_value:,.0f}")
            else:
                st.metric("Total GRN Value", "N/A")
        
        with col2:
            total_transactions = len(grn_df) + len(issue_df) + len(voucher_df)
            st.metric("Total Transactions", f"{total_transactions:,}")
        
        with col3:
            if not grn_df.empty and 'supplier_name' in grn_df.columns:
                unique_suppliers = grn_df['supplier_name'].nunique()
                st.metric("Active Suppliers", f"{unique_suppliers:,}")
            else:
                st.metric("Active Suppliers", "N/A")
        
        with col4:
            # PDF data metrics
            pdf_records = 0
            if hr185_df is not None and not hr185_df.empty:
                pdf_records += len(hr185_df)
            if hr990_df is not None and not hr990_df.empty:
                pdf_records += len(hr990_df)
            st.metric("PDF Records", f"{pdf_records:,}")
        
        with col5:
            # HR185 transaction value
            if hr185_df is not None and not hr185_df.empty and 'amount' in hr185_df.columns:
                hr185_value = pd.to_numeric(hr185_df['amount'], errors='coerce').sum()
                st.metric("HR185 Value", f"R{hr185_value:,.0f}")
            else:
                st.metric("HR185 Value", "N/A")
        
        with col6:
            if not audit_df.empty:
                st.metric("Audit Trail Records", f"{len(audit_df):,}")
            else:
                st.metric("Audit Trail Records", "N/A")
        
        # Data coverage information
        st.markdown("---")
        st.markdown("### 📊 Data Coverage Overview")
        
        # Check for item identification columns
        item_col = None
        if not grn_df.empty:
            if 'item_no' in grn_df.columns:
                item_col = 'item_no'
            elif 'item_code' in grn_df.columns:
                item_col = 'item_code'
        
        # Additional summary info
        coverage_col1, coverage_col2, coverage_col3 = st.columns(3)
        
        with coverage_col1:
            if item_col and not grn_df.empty:
                unique_items = grn_df[item_col].nunique()
                st.metric("Unique Items", f"{unique_items:,}")
            else:
                st.metric("Unique Items", "N/A")
        
        with coverage_col2:
            # Data sources count
            data_sources = 0
            if not grn_df.empty:
                data_sources += 1
            if not issue_df.empty:
                data_sources += 1
            if not voucher_df.empty:
                data_sources += 1
            if hr185_df is not None and not hr185_df.empty:
                data_sources += 1
            if hr990_df is not None and not hr990_df.empty:
                data_sources += 1
            st.metric("Active Data Sources", f"{data_sources}")
        
        with coverage_col3:
            # Date range - use period_date or fin_period for better date display
            date_range = "N/A"
            
            if not grn_df.empty:
                # Try period_date first, then fin_period
                if 'period_date' in grn_df.columns and grn_df['period_date'].notna().any():
                    min_date = grn_df['period_date'].min()
                    max_date = grn_df['period_date'].max()
                    date_range = f"{min_date.strftime('%Y-%m')} to {max_date.strftime('%Y-%m')}"
                elif 'fin_period' in grn_df.columns and grn_df['fin_period'].notna().any():
                    fin_periods = grn_df['fin_period'].dropna()
                    min_period = fin_periods.min()
                    max_period = fin_periods.max()
                    
                    # Convert YYYYMM to readable format
                    try:
                        min_year, min_month = divmod(int(min_period), 100)
                        max_year, max_month = divmod(int(max_period), 100)
                        date_range = f"{min_year}-{min_month:02d} to {max_year}-{max_month:02d}"
                    except:
                        date_range = f"{min_period} to {max_period}"
                elif 'date' in grn_df.columns and grn_df['date'].notna().any():
                    min_date = grn_df['date'].min()
                    max_date = grn_df['date'].max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        date_range = f"{min_date.strftime('%Y-%m')} to {max_date.strftime('%Y-%m')}"
            
            st.metric("Data Range", date_range)
        
        # CHQ Analysis Mode Indicator
        if filters and filters.get('exclude_chq', False):
            st.markdown("---")
            st.success("🎯 **Primary Transaction Analysis Mode**: Analyzing core business transactions (INV, VCH, CN, DN) only. CHQ payment confirmations excluded for optimal performance.")
            
            # Show performance benefit
            if hr185_df is not None and not hr185_df.empty:
                total_hr185 = len(hr185_df)
                primary_types = ['INV', 'VCH', 'CN', 'DN']
                if 'transaction_type' in hr185_df.columns:
                    primary_count = len(hr185_df[hr185_df['transaction_type'].str.upper().isin(primary_types)])
                    chq_count = total_hr185 - primary_count
                    
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    with perf_col1:
                        st.metric("Primary Transactions", f"{primary_count:,}", help="INV, VCH, CN, DN transactions")
                    with perf_col2:
                        st.metric("CHQ Excluded", f"{chq_count:,}", help="CHQ payment confirmations excluded")
                    with perf_col3:
                        improvement = "Expected: 95.6% vs 77.5% with CHQ"
                        st.metric("Match Rate Improvement", improvement, help="Performance boost from focusing on primary business transactions")
        elif filters and filters.get('exclude_chq') == False:
            st.info("📊 **Standard Analysis Mode**: Analyzing all transaction types including CHQ payment confirmations.")
    
    def create_financial_analytics(self, filters=None):
        """Create comprehensive financial analytics section."""
        st.header("💰 Financial Analytics")
        
        grn_df = self.load_filtered_data("individual_hr995grn.csv", filters)
        voucher_df = self.load_filtered_data("individual_hr995vouch.csv", filters)
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        if grn_df.empty:
            if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
                st.warning(f"No GRN data available for supplier: {filters['supplier']}")
            else:
                st.warning("No GRN data available for financial analysis")
            return
        
        # Clean and prepare data
        grn_df = self.clean_financial_data(grn_df, 'nett_grn_amt')
        
        # Create tabs for different financial views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "💳 By Supplier", "📊 Categories", "🔍 Detailed Analysis"])
        
        with tab1:
            self.create_financial_trends(grn_df)
        
        with tab2:
            self.create_supplier_financial_analysis(grn_df)
        
        with tab3:
            self.create_category_analysis(grn_df)
        
        with tab4:
            self.create_detailed_financial_analysis(grn_df, voucher_df)
    
    def create_financial_trends(self, grn_df):
        """Create financial trend charts with proper date handling."""
        st.subheader("Financial Trends Over Time")
        
        # Determine the best time column to use
        time_col = None
        period_display_col = None
        
        if 'period_date' in grn_df.columns and grn_df['period_date'].notna().any():
            time_col = 'period_date'
            grn_df = grn_df.dropna(subset=['period_date'])
            grn_df['period_display'] = grn_df['period_date'].dt.strftime('%Y-%m')
            period_display_col = 'period_display'
        elif 'fin_period' in grn_df.columns and grn_df['fin_period'].notna().any():
            time_col = 'fin_period'
            grn_df = grn_df[grn_df['fin_period'].notna()]
            # Convert YYYYMM to readable format
            grn_df['period_display'] = grn_df['fin_period'].apply(lambda x: f"{int(x)//100}-{int(x)%100:02d}" if pd.notna(x) else "Unknown")
            period_display_col = 'period_display'
        elif 'date' in grn_df.columns and grn_df['date'].notna().any():
            time_col = 'date'
            grn_df['date'] = pd.to_datetime(grn_df['date'], errors='coerce')
            grn_df = grn_df.dropna(subset=['date'])
            grn_df['period_display'] = grn_df['date'].dt.strftime('%Y-%m')
            period_display_col = 'period_display'
        
        if time_col and 'nett_grn_amt' in grn_df.columns and not grn_df.empty:
            # Create proper aggregation
            if time_col == 'period_date':
                # Group by period_date (already monthly)
                grn_df['year_month'] = grn_df['period_date'].dt.to_period('M')
                trends = grn_df.groupby(['year_month', 'period_display'])['nett_grn_amt'].agg(['sum', 'count', 'mean']).reset_index()
            elif time_col == 'fin_period':
                # Group by financial period
                trends = grn_df.groupby(['fin_period', 'period_display'])['nett_grn_amt'].agg(['sum', 'count', 'mean']).reset_index()
            else:
                # Group by month for date
                grn_df['year_month'] = grn_df['date'].dt.to_period('M')
                trends = grn_df.groupby(['year_month', 'period_display'])['nett_grn_amt'].agg(['sum', 'count', 'mean']).reset_index()
            
            if len(trends) > 0:
                # Sort by period for proper display
                trends = trends.sort_values(trends.columns[0])
                
                # Monthly value trend
                fig1 = px.line(trends, x='period_display', y='sum',
                              title='GRN Value Trend by Period',
                              labels={'sum': 'Total Value (R)', 'period_display': 'Period'})
                
                # Add custom hover template with proper date formatting
                fig1.update_traces(
                    hovertemplate='<b>Period:</b> %{x}<br>' +
                                  '<b>Total Value:</b> R%{y:,.2f}<br>' +
                                  '<extra></extra>'
                )
                
                fig1.update_layout(
                    height=400,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('hr995_grn.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig1.update_xaxes(tickangle=45, title="Period")
                fig1.update_yaxes(title="Total Value (R)")
                st.plotly_chart(fig1, use_container_width=True, key="grn_total_value_trend")
                
                # Transaction count trend
                fig2 = px.bar(trends, x='period_display', y='count',
                             title='Transaction Count by Period',
                             labels={'count': 'Number of Transactions', 'period_display': 'Period'})
                
                fig2.update_traces(
                    hovertemplate='<b>Period:</b> %{x}<br>' +
                                  '<b>Transactions:</b> %{y}<br>' +
                                  '<b>Data Source:</b> GRN Records<br>' +
                                  '<extra></extra>'
                )
                
                fig2.update_layout(
                    height=400,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('hr995_grn.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig2.update_xaxes(tickangle=45, title="Period")
                fig2.update_yaxes(title="Number of Transactions")
                st.plotly_chart(fig2, use_container_width=True, key="grn_transaction_count_trend")
                
                # Average transaction value
                fig3 = px.line(trends, x='period_display', y='mean',
                              title='Average Transaction Value Trend',
                              labels={'mean': 'Average Value (R)', 'period_display': 'Period'})
                
                fig3.update_traces(
                    hovertemplate='<b>Period:</b> %{x}<br>' +
                                  '<b>Average Value:</b> R%{y:,.2f}<br>' +
                                  '<b>Data Source:</b> GRN Records<br>' +
                                  '<extra></extra>'
                )
                
                fig3.update_layout(
                    height=400,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('hr995_grn.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig3.update_xaxes(tickangle=45, title="Period")
                fig3.update_yaxes(title="Average Value (R)")
                st.plotly_chart(fig3, use_container_width=True, key="grn_avg_transaction_value_trend")
            else:
                st.warning("No valid time period data found for trend analysis")
        else:
            st.warning("No valid time or financial data found for trend analysis")
    
    def create_supplier_financial_analysis(self, grn_df):
        """Create supplier financial analysis charts."""
        st.subheader("Supplier Financial Performance")
        
        if 'supplier_name' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
            # Top suppliers by value
            supplier_totals = grn_df.groupby('supplier_name')['nett_grn_amt'].agg(['sum', 'count', 'mean']).reset_index()
            supplier_totals = supplier_totals.sort_values('sum', ascending=False).head(15)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(supplier_totals, x='sum', y='supplier_name',
                             title='Top 15 Suppliers by Total Value',
                             labels={'sum': 'Total Value (R)', 'supplier_name': 'Supplier'},
                             orientation='h')
                fig1.update_layout(
                    height=500,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('hr995_grn.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig1.update_traces(
                    hovertemplate="<b>Supplier:</b> %{y}<br>" +
                                  "<b>Total Value:</b> R%{x:,.2f}<br>" +
                                  "<b>Data Source:</b> GRN Records<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig1, width="stretch", key="supplier_top_performers")
            
            with col2:
                fig2 = px.scatter(supplier_totals, x='count', y='mean', 
                                 hover_data=['supplier_name'],
                                 title='Supplier Performance: Volume vs Average Value',
                                 labels={'count': 'Number of Transactions', 'mean': 'Average Value (R)'})
                fig2.update_layout(
                    height=500,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('hr995_grn.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig2.update_traces(
                    hovertemplate="<b>Supplier:</b> %{customdata[0]}<br>" +
                                  "<b>Transactions:</b> %{x}<br>" +
                                  "<b>Average Value:</b> R%{y:,.2f}<br>" +
                                  "<b>Data Source:</b> GRN Records<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig2, width="stretch", key="supplier_volume_vs_value")
            
            # Supplier concentration analysis
            fig3 = px.pie(supplier_totals.head(10), values='sum', names='supplier_name',
                         title='Top 10 Suppliers - Value Distribution')
            fig3.update_layout(
                annotations=[
                    dict(
                        text=self.get_data_source_tooltip('hr995_grn.csv'),
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.02, y=0.98,
                        xanchor="left", yanchor="top",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="gray",
                        borderwidth=1,
                        font=dict(size=10)
                    )
                ]
            )
            fig3.update_traces(
                hovertemplate="<b>Supplier:</b> %{label}<br>" +
                              "<b>Total Value:</b> R%{value:,.2f}<br>" +
                              "<b>Percentage:</b> %{percent}<br>" +
                              "<b>Data Source:</b> GRN Records<br>" +
                              "<extra></extra>"
            )
            st.plotly_chart(fig3, width="stretch", key="supplier_concentration_pie")
    
    def create_category_analysis(self, grn_df):
        """Create category-based analysis."""
        st.subheader("Item Category Analysis")
        
        if 'description' in grn_df.columns:
            # Extract category from description
            grn_df['category'] = grn_df['description'].str.extract(r'^([A-Z]+)', expand=False)
            grn_df['category'] = grn_df['category'].fillna('OTHER')
            
            category_analysis = grn_df.groupby('category')['nett_grn_amt'].agg(['sum', 'count']).reset_index()
            category_analysis = category_analysis.sort_values('sum', ascending=False).head(12)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.treemap(category_analysis, path=['category'], values='sum',
                                 title='Category Spending Distribution (Treemap)')
                st.plotly_chart(fig1, width="stretch", key="category_spending_treemap")
            
            with col2:
                fig2 = px.bar(category_analysis, x='category', y='count',
                             title='Transaction Count by Category')
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, width="stretch", key="category_transaction_count")
    
    def create_detailed_financial_analysis(self, grn_df, voucher_df):
        """Create detailed financial analysis."""
        st.subheader("Detailed Financial Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'nett_grn_amt' in grn_df.columns:
                # Value distribution
                fig1 = px.histogram(grn_df, x='nett_grn_amt', nbins=50,
                                   title='GRN Value Distribution')
                fig1.update_layout(height=400)
                st.plotly_chart(fig1, width="stretch", key="grn_value_distribution")
        
        with col2:
            if not voucher_df.empty and 'cheq_amt' in voucher_df.columns:
                voucher_df = self.clean_financial_data(voucher_df, 'cheq_amt')
                fig2 = px.box(voucher_df, y='cheq_amt',
                             title='Voucher Amount Distribution')
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, width="stretch", key="voucher_amount_distribution")
    
    def create_inventory_analytics(self, filters=None):
        """Create inventory analytics section."""
        st.header("📦 Inventory Analytics")
        
        grn_df = self.load_filtered_data("individual_hr995grn.csv", filters)
        issue_df = self.load_filtered_data("individual_hr995issue.csv", filters)
        stock_df = self.load_filtered_data("stock_adjustments.csv", filters)
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        tab1, tab2, tab3 = st.tabs(["📈 Stock Movement", "🔄 Turnover Analysis", "⚠️ Stock Alerts"])
        
        with tab1:
            self.create_stock_movement_analysis(grn_df, issue_df)
        
        with tab2:
            self.create_turnover_analysis(grn_df, issue_df)
        
        with tab3:
            self.create_stock_alerts(stock_df)
    
    def create_stock_movement_analysis(self, grn_df, issue_df):
        """Create stock movement analysis."""
        st.subheader("Stock Movement Analysis")
        
        if not grn_df.empty and not issue_df.empty:
            # Handle different column names for item identification
            grn_item_col = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
            issue_item_col = 'item_code' if 'item_code' in issue_df.columns else 'item_no'
            
            # Check if required columns exist
            if grn_item_col in grn_df.columns and issue_item_col in issue_df.columns and 'quantity' in grn_df.columns and 'quantity' in issue_df.columns:
                # Combine GRN and Issues for movement analysis
                grn_summary = grn_df.groupby(grn_item_col)['quantity'].sum().reset_index()
                grn_summary['movement_type'] = 'Received'
                grn_summary = grn_summary.rename(columns={'quantity': 'total_quantity', grn_item_col: 'item_id'})
                
                issue_summary = issue_df.groupby(issue_item_col)['quantity'].sum().reset_index()
                issue_summary['movement_type'] = 'Issued'
                issue_summary = issue_summary.rename(columns={'quantity': 'total_quantity', issue_item_col: 'item_id'})
                
                movement_df = pd.concat([grn_summary, issue_summary])
                
                # Top moving items
                top_items = movement_df.groupby('item_id')['total_quantity'].sum().sort_values(ascending=False).head(20)
                top_items_df = pd.DataFrame({'item_id': top_items.index, 'total_quantity': top_items.values})
                
                fig1 = px.bar(top_items_df, x='total_quantity', y='item_id',
                             title='Top 20 Items by Total Movement',
                             labels={'total_quantity': 'Total Quantity', 'item_id': 'Item ID'},
                             orientation='h')
                fig1.update_layout(
                    height=600,
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip(['hr995_grn.csv', 'hr995_issue.csv']),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig1.update_traces(
                    hovertemplate="<b>Item ID:</b> %{y}<br>" +
                                  "<b>Total Movement:</b> %{x:,.0f}<br>" +
                                  "<b>Data Sources:</b> GRN & Issue Records<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig1, width="stretch", key="top_stock_movement_items")
                
                # Movement by type
                movement_summary = movement_df.groupby('movement_type')['total_quantity'].sum().reset_index()
                fig2 = px.pie(movement_summary, values='total_quantity', names='movement_type',
                             title='Stock Movement Distribution')
                fig2.update_layout(
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip(['hr995_grn.csv', 'hr995_issue.csv']),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig2.update_traces(
                    hovertemplate="<b>Movement Type:</b> %{label}<br>" +
                                  "<b>Total Quantity:</b> %{value:,.0f}<br>" +
                                  "<b>Percentage:</b> %{percent}<br>" +
                                  "<b>Data Sources:</b> GRN & Issue Records<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig2, width="stretch", key="stock_movement_distribution")
            else:
                st.warning("Required columns for stock movement analysis not found")
        else:
            st.warning("No stock movement data available")
    
    def create_turnover_analysis(self, grn_df, issue_df):
        """Create inventory turnover analysis."""
        st.subheader("Inventory Turnover Analysis")
        
        # Handle different column names for item identification
        grn_item_col = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
        issue_item_col = 'item_code' if 'item_code' in issue_df.columns else 'item_no'
        
        if grn_item_col in grn_df.columns and issue_item_col in issue_df.columns and 'quantity' in grn_df.columns and 'quantity' in issue_df.columns:
            # Calculate turnover ratio
            received = grn_df.groupby(grn_item_col)['quantity'].sum()
            issued = issue_df.groupby(issue_item_col)['quantity'].sum()
            
            # Create unified item index
            all_items = set(received.index) | set(issued.index)
            turnover_data = []
            
            for item in all_items:
                received_qty = received.get(item, 0)
                issued_qty = issued.get(item, 0)
                turnover_ratio = issued_qty / (received_qty + 0.001) if received_qty > 0 else 0
                turnover_data.append({
                    'item_id': item,
                    'received': received_qty,
                    'issued': issued_qty,
                    'turnover_ratio': turnover_ratio
                })
            
            turnover_df = pd.DataFrame(turnover_data)
            
            # High turnover items
            high_turnover = turnover_df.nlargest(15, 'turnover_ratio')
            
            fig1 = px.bar(high_turnover, x='item_id', y='turnover_ratio',
                         title='Top 15 Items by Turnover Ratio',
                         labels={'turnover_ratio': 'Turnover Ratio', 'item_id': 'Item ID'})
            fig1.update_xaxes(tickangle=45)
            st.plotly_chart(fig1, width="stretch", key="top_turnover_items")
            
            # Turnover distribution
            fig2 = px.scatter(turnover_df, x='received', y='issued',
                             hover_data=['item_id'],
                             title='Received vs Issued Quantities',
                             labels={'received': 'Received Quantity', 'issued': 'Issued Quantity'})
            st.plotly_chart(fig2, width="stretch", key="received_vs_issued_scatter")
        else:
            st.warning("Required columns for turnover analysis not found")
    
    def create_stock_alerts(self, stock_df):
        """Create stock alert analysis."""
        st.subheader("Stock Level Alerts")
        
        if not stock_df.empty:
            st.info("Stock adjustment data loaded. Detailed alert analysis would require current stock levels.")
            
            # Show stock adjustments summary
            if 'source_file' in stock_df.columns:
                adjustment_summary = stock_df['source_file'].value_counts()
                adjustment_df = pd.DataFrame({'source_file': adjustment_summary.index, 'count': adjustment_summary.values})
                
                fig = px.bar(adjustment_df, x='count', y='source_file',
                           title='Stock Adjustments by Source',
                           orientation='h')
                st.plotly_chart(fig, width="stretch", key="stock_adjustments_by_source")
        else:
            st.warning("No stock adjustment data available")
    
    def create_supplier_analytics(self, filters=None):
        """Create supplier analytics section."""
        st.header("🏪 Supplier Analytics")
        
        suppliers_df = self.load_filtered_data("suppliers.csv", filters)
        grn_df = self.load_filtered_data("individual_hr995grn.csv", filters)
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        tab1, tab2, tab3 = st.tabs(["📊 Performance", "🤝 Relationships", "📈 Trends"])
        
        with tab1:
            self.create_supplier_performance(grn_df)
        
        with tab2:
            self.create_supplier_relationships(suppliers_df, grn_df)
        
        with tab3:
            self.create_supplier_trends(grn_df)
    
    def create_supplier_performance(self, grn_df):
        """Create supplier performance analysis."""
        st.subheader("Supplier Performance Metrics")
        
        if 'supplier_name' in grn_df.columns:
            performance_metrics = grn_df.groupby('supplier_name').agg({
                'nett_grn_amt': ['sum', 'mean', 'count'],
                'quantity': 'sum'
            }).round(2)
            
            performance_metrics.columns = ['Total_Value', 'Avg_Value', 'Transaction_Count', 'Total_Quantity']
            performance_metrics = performance_metrics.reset_index()
            performance_metrics = performance_metrics.sort_values('Total_Value', ascending=False).head(20)
            
            # Performance matrix
            fig = px.scatter(performance_metrics, 
                           x='Transaction_Count', 
                           y='Avg_Value',
                           size='Total_Value',
                           hover_data=['supplier_name'],
                           title='Supplier Performance Matrix',
                           labels={
                               'Transaction_Count': 'Number of Transactions',
                               'Avg_Value': 'Average Transaction Value (R)'
                           })
            fig.update_layout(
                annotations=[
                    dict(
                        text=self.get_data_source_tooltip('hr995_grn.csv'),
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.02, y=0.98,
                        xanchor="left", yanchor="top",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="gray",
                        borderwidth=1,
                        font=dict(size=10)
                    )
                ]
            )
            fig.update_traces(
                hovertemplate="<b>Supplier:</b> %{customdata[0]}<br>" +
                              "<b>Transactions:</b> %{x}<br>" +
                              "<b>Avg Value:</b> R%{y:,.2f}<br>" +
                              "<b>Total Value:</b> R%{marker.size:,.2f}<br>" +
                              "<b>Data Source:</b> GRN Records<br>" +
                              "<extra></extra>"
            )
            st.plotly_chart(fig, width="stretch", key="supplier_performance_bubble")
            
            # Top performers table
            st.subheader("Top 20 Suppliers by Value")
            st.dataframe(performance_metrics[['supplier_name', 'Total_Value', 'Transaction_Count', 'Avg_Value']], 
                        width="stretch")
    
    def create_supplier_relationships(self, suppliers_df, grn_df):
        """Create supplier relationship analysis."""
        st.subheader("Supplier Relationship Analysis")
        
        if not suppliers_df.empty:
            st.info(f"Loaded {len(suppliers_df)} supplier records")
            
            # Show supplier data summary
            if 'source_file' in suppliers_df.columns:
                supplier_sources = suppliers_df['source_file'].value_counts()
                supplier_sources_df = pd.DataFrame({'source_file': supplier_sources.index, 'count': supplier_sources.values})
                
                fig = px.pie(supplier_sources_df, values='count', names='source_file',
                           title='Supplier Data Sources')
                fig.update_layout(
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('suppliers.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig.update_traces(
                    hovertemplate="<b>Source File:</b> %{label}<br>" +
                                  "<b>Supplier Count:</b> %{value}<br>" +
                                  "<b>Percentage:</b> %{percent}<br>" +
                                  "<b>Data Source:</b> Supplier Master Data<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig, width="stretch", key="supplier_type_distribution")
        else:
            st.warning("No supplier master data available")
    
    def create_supplier_trends(self, grn_df):
        """Create supplier trend analysis."""
        st.subheader("Supplier Engagement Trends")
        
        if 'supplier_name' in grn_df.columns and 'date' in grn_df.columns:
            grn_df['date'] = pd.to_datetime(grn_df['date'], errors='coerce')
            grn_df = grn_df.dropna(subset=['date'])
            
            if not grn_df.empty:
                # Monthly supplier activity
                grn_df['year_month'] = grn_df['date'].dt.to_period('M')
                supplier_monthly = grn_df.groupby(['year_month', 'supplier_name']).size().reset_index(name='transactions')
                
                # Top suppliers over time
                top_suppliers = grn_df['supplier_name'].value_counts().head(5).index
                supplier_trends = supplier_monthly[supplier_monthly['supplier_name'].isin(top_suppliers)]
                supplier_trends['year_month_str'] = supplier_trends['year_month'].astype(str)
                
                fig = px.line(supplier_trends, 
                            x='year_month_str', 
                            y='transactions',
                            color='supplier_name',
                            title='Top 5 Suppliers - Monthly Activity Trends')
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, width="stretch", key="supplier_monthly_trends")
    
    def create_operational_analytics(self, filters=None):
        """Create operational analytics with corrected relationship analysis and authorization."""
        st.header("⚙️ Operational Analytics")
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        # Load linked data with corrected relationships
        linked_data = self.load_linked_data(filters)
        
        # Load additional operational datasets
        audit_df = self.load_data("objective_2_stock_audit_trail.csv")
        process_df = self.load_data("objective_4_end_to_end_process.csv")
        voucher_df = self.load_data("individual_hr995vouch.csv")
        
        # Create tabs for different operational views
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔗 Data Relationships",
            "🔄 Process Flow", 
            "🔐 Authorization & SCOA",
            "📋 Audit Trail", 
            "⏱️ Processing Times", 
            "🎯 Performance Metrics"
        ])
        
        with tab1:
            self.create_relationship_analysis(linked_data)
        
        with tab2:
            self.create_process_flow_analysis(linked_data['grn'], linked_data['issue'], process_df)
        
        with tab3:
            if voucher_df is not None and not voucher_df.empty:
                self.create_authorization_analysis(voucher_df)
            else:
                st.warning("Voucher data not available for authorization and SCOA analysis.")
        
        with tab4:
            self.create_audit_trail_analysis(audit_df)
        
        with tab5:
            self.create_processing_time_analysis(linked_data['grn'], linked_data['issue'])
        
        with tab6:
            self.create_performance_metrics(linked_data['grn'], linked_data['issue'])
    
    def create_process_flow_analysis(self, grn_df, issue_df, process_df):
        """Analyze process flow with corrected data relationships."""
        st.subheader("🔄 Process Flow Analysis (Corrected)")
        st.info("✅ Analysis using corrected data relationships and linkages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📦 GRN → Issue Process")
            if not grn_df.empty and not issue_df.empty:
                # Match items between GRN and Issue using item codes
                item_col_grn = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
                item_col_issue = 'item_no' if 'item_no' in issue_df.columns else 'item_code'
                
                if item_col_grn in grn_df.columns and item_col_issue in issue_df.columns:
                    grn_items = set(grn_df[item_col_grn].dropna())
                    issue_items = set(issue_df[item_col_issue].dropna())
                    
                    common_items = grn_items & issue_items
                    grn_only_items = grn_items - issue_items
                    issue_only_items = issue_items - grn_items
                    
                    st.metric("Items in Both GRN & Issue", len(common_items))
                    st.metric("Items GRN Only", len(grn_only_items))
                    st.metric("Items Issue Only", len(issue_only_items))
                    
                    # Process completion rate
                    if len(grn_items) > 0:
                        completion_rate = len(common_items) / len(grn_items) * 100
                        st.metric("Process Completion Rate", f"{completion_rate:.1f}%")
            else:
                st.warning("GRN or Issue data not available")
        
        with col2:
            st.markdown("### 💳 Payment Process Status")
            if not grn_df.empty and 'voucher_normalized' in grn_df.columns:
                # Payment status analysis
                grns_with_vouchers = grn_df['voucher_normalized'].notna().sum()
                grns_without_vouchers = grn_df['voucher_normalized'].isna().sum()
                
                st.metric("GRNs with Vouchers", grns_with_vouchers)
                st.metric("GRNs without Vouchers", grns_without_vouchers)
                
                if len(grn_df) > 0:
                    voucher_rate = grns_with_vouchers / len(grn_df) * 100
                    st.metric("Voucher Assignment Rate", f"{voucher_rate:.1f}%")
        
        # Process timing analysis
        if process_df is not None and not process_df.empty:
            st.markdown("### ⏱️ Process Timing Analysis")
            
            if 'process_step' in process_df.columns and 'duration' in process_df.columns:
                step_timing = process_df.groupby('process_step')['duration'].agg(['mean', 'median', 'std']).round(2)
                
                fig = px.bar(
                    x=step_timing.index,
                    y=step_timing['mean'],
                    title="Average Process Step Duration",
                    labels={'x': 'Process Step', 'y': 'Average Duration'}
                )
                st.plotly_chart(fig, use_container_width=True, key="process_step_duration")
    
    def create_audit_trail_analysis(self, audit_df):
        """Analyze audit trail data with enhanced insights."""
        st.subheader("📋 Audit Trail Analysis")
        
        if audit_df is None or audit_df.empty:
            st.warning("No audit trail data available.")
            return
        
        # Key audit metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Audit Records", f"{len(audit_df):,}")
        
        with col2:
            if 'transaction_type' in audit_df.columns:
                st.metric("Transaction Types", audit_df['transaction_type'].nunique())
        
        with col3:
            if 'user_id' in audit_df.columns:
                st.metric("Unique Users", audit_df['user_id'].nunique())
        
        with col4:
            if 'date' in audit_df.columns:
                date_range = audit_df['date'].max() - audit_df['date'].min()
                st.metric("Audit Period (Days)", f"{date_range.days}")
        
        # Audit activity over time
        if 'date' in audit_df.columns:
            st.markdown("### 📅 Audit Activity Timeline")
            
            audit_df['date'] = pd.to_datetime(audit_df['date'], errors='coerce')
            daily_activity = audit_df.groupby(audit_df['date'].dt.date).size().reset_index()
            daily_activity.columns = ['date', 'activity_count']
            
            fig = px.line(
                daily_activity,
                x='date',
                y='activity_count',
                title="Daily Audit Activity",
                labels={'activity_count': 'Number of Audit Records'}
            )
            st.plotly_chart(fig, use_container_width=True, key="daily_audit_activity")
    
    def create_processing_time_analysis(self, grn_df, issue_df):
        """Analyze processing times between related transactions."""
        st.subheader("⏱️ Processing Time Analysis")
        
        if grn_df.empty or issue_df.empty:
            st.warning("Insufficient data for processing time analysis.")
            return
        
        # Date columns for analysis
        grn_date_col = None
        issue_date_col = None
        
        for col in ['period_date', 'date', 'grn_date']:
            if col in grn_df.columns and grn_df[col].notna().any():
                grn_date_col = col
                break
        
        for col in ['period_date', 'date', 'issue_date']:
            if col in issue_df.columns and issue_df[col].notna().any():
                issue_date_col = col
                break
        
        if grn_date_col and issue_date_col:
            st.markdown("### 📦 GRN to Issue Processing Time")
            
            # Find matching items with timing
            item_col_grn = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
            item_col_issue = 'item_no' if 'item_no' in issue_df.columns else 'item_code'
            
            if item_col_grn in grn_df.columns and item_col_issue in issue_df.columns:
                # Merge on item code to find processing times
                grn_summary = grn_df.groupby(item_col_grn)[grn_date_col].min().reset_index()
                grn_summary.columns = ['item_code', 'grn_date']
                
                issue_summary = issue_df.groupby(item_col_issue)[issue_date_col].max().reset_index()
                issue_summary.columns = ['item_code', 'issue_date']
                
                timing_analysis = grn_summary.merge(issue_summary, on='item_code', how='inner')
                timing_analysis['processing_days'] = (timing_analysis['issue_date'] - timing_analysis['grn_date']).dt.days
                
                # Filter reasonable processing times
                timing_analysis = timing_analysis[
                    (timing_analysis['processing_days'] >= 0) & 
                    (timing_analysis['processing_days'] <= 365)
                ]
                
                if len(timing_analysis) > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_processing = timing_analysis['processing_days'].mean()
                        st.metric("Average Processing Time", f"{avg_processing:.1f} days")
                    
                    with col2:
                        median_processing = timing_analysis['processing_days'].median()
                        st.metric("Median Processing Time", f"{median_processing:.1f} days")
                    
                    with col3:
                        max_processing = timing_analysis['processing_days'].max()
                        st.metric("Longest Processing Time", f"{max_processing:.0f} days")
                    
                    # Distribution chart
                    fig = px.histogram(
                        timing_analysis,
                        x='processing_days',
                        title="Processing Time Distribution",
                        labels={'processing_days': 'Processing Time (Days)', 'count': 'Number of Items'}
                    )
                    st.plotly_chart(fig, use_container_width=True, key="processing_time_distribution")
                else:
                    st.info("No matching items found between GRN and Issue data for timing analysis.")
        else:
            st.warning("Date columns not available for processing time analysis.")
    
    def create_performance_metrics(self, grn_df, issue_df):
        """Create comprehensive performance metrics dashboard."""
        st.subheader("🎯 Performance Metrics")
        
        # Key performance indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if not grn_df.empty:
                avg_grn_value = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce').mean()
                st.metric("Avg GRN Value", f"R{avg_grn_value:,.2f}")
        
        with col2:
            if not issue_df.empty and 'quantity' in issue_df.columns:
                avg_issue_qty = pd.to_numeric(issue_df['quantity'], errors='coerce').mean()
                st.metric("Avg Issue Quantity", f"{avg_issue_qty:.2f}")
        
        with col3:
            # Transaction efficiency
            if not grn_df.empty and not issue_df.empty:
                efficiency = len(issue_df) / len(grn_df) * 100 if len(grn_df) > 0 else 0
                st.metric("Transaction Efficiency", f"{efficiency:.1f}%")
        
        with col4:
            # Data quality score
            quality_score = 100  # Start with perfect score
            if not grn_df.empty:
                # Deduct for missing vouchers
                missing_vouchers = grn_df['voucher'].isna().sum() / len(grn_df) * 20
                quality_score -= missing_vouchers
                
                # Deduct for missing suppliers
                missing_suppliers = grn_df['supplier_name'].isna().sum() / len(grn_df) * 15
                quality_score -= missing_suppliers
            
            st.metric("Data Quality Score", f"{max(0, quality_score):.1f}/100")
        
        # Performance trends
        st.markdown("### 📈 Performance Trends")
        
        if not grn_df.empty and 'period_date' in grn_df.columns:
            monthly_performance = grn_df.groupby(grn_df['period_date'].dt.to_period('M')).agg({
                'nett_grn_amt': ['sum', 'count', 'mean']
            }).round(2)
            
            monthly_performance.columns = ['Total_Value', 'Transaction_Count', 'Avg_Value']
            monthly_performance = monthly_performance.reset_index()
            monthly_performance['period'] = monthly_performance['period_date'].astype(str)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Monthly Transaction Value', 'Monthly Transaction Count'),
                specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
            )
            
            fig.add_trace(
                go.Scatter(
                    x=monthly_performance['period'],
                    y=monthly_performance['Total_Value'],
                    mode='lines+markers',
                    name='Total Value'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=monthly_performance['period'],
                    y=monthly_performance['Transaction_Count'],
                    mode='lines+markers',
                    name='Transaction Count',
                    line=dict(color='orange')
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=600, title_text="Monthly Performance Metrics")
            st.plotly_chart(fig, use_container_width=True, key="monthly_performance_metrics")

    def create_audit_analysis(self, audit_df):
        """Create audit trail analysis."""
        st.subheader("Audit Trail Analysis")
        
        if not audit_df.empty:
            # Transaction type distribution
            if 'transaction_type' in audit_df.columns:
                transaction_dist = audit_df['transaction_type'].value_counts()
                
                fig1 = px.pie(values=transaction_dist.values, names=transaction_dist.index,
                             title='Transaction Type Distribution')
                fig1.update_layout(
                    annotations=[
                        dict(
                            text=self.get_data_source_tooltip('objective_2_stock_audit_trail.csv'),
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            xanchor="left", yanchor="top",
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="gray",
                            borderwidth=1,
                            font=dict(size=10)
                        )
                    ]
                )
                fig1.update_traces(
                    hovertemplate="<b>Transaction Type:</b> %{label}<br>" +
                                  "<b>Count:</b> %{value}<br>" +
                                  "<b>Percentage:</b> %{percent}<br>" +
                                  "<b>Data Source:</b> Audit Trail Records<br>" +
                                  "<extra></extra>"
                )
                st.plotly_chart(fig1, width="stretch", key="audit_transaction_types")
            
            # Audit timeline
            if 'date' in audit_df.columns:
                audit_df['date'] = pd.to_datetime(audit_df['date'], errors='coerce')
                audit_df = audit_df.dropna(subset=['date'])
                
                if not audit_df.empty:
                    audit_df['year_month'] = audit_df['date'].dt.to_period('M')
                    monthly_audit = audit_df.groupby('year_month').size().reset_index(name='count')
                    monthly_audit['year_month_str'] = monthly_audit['year_month'].astype(str)
                    
                    fig2 = px.bar(monthly_audit, x='year_month_str', y='count',
                                 title='Monthly Audit Activity')
                    st.plotly_chart(fig2, width="stretch", key="monthly_audit_activity")
        else:
            st.warning("No audit trail data available")
    
    def create_process_analysis(self, process_df):
        """Create process flow analysis."""
        st.subheader("End-to-End Process Analysis")
        
        if not process_df.empty:
            # Process stage distribution
            if 'process_stage' in process_df.columns:
                stage_dist = process_df['process_stage'].value_counts()
                
                fig = px.funnel(y=stage_dist.index, x=stage_dist.values,
                               title='Process Stage Distribution')
                st.plotly_chart(fig, width="stretch", key="process_stage_distribution")
            
            st.info(f"Analyzed {len(process_df)} process records")
        else:
            st.warning("No process data available")
    
    def create_efficiency_analysis(self, audit_df):
        """Create efficiency analysis."""
        st.subheader("Operational Efficiency Metrics")
        
        if not audit_df.empty and 'official' in audit_df.columns:
            # Official productivity
            official_productivity = audit_df['official'].value_counts().head(10)
            
            fig = px.bar(x=official_productivity.values, y=official_productivity.index,
                        title='Top 10 Officials by Transaction Volume',
                        orientation='h')
            st.plotly_chart(fig, width="stretch", key="top_officials_by_volume")
        else:
            st.info("Efficiency analysis requires official data")
    
    def create_sidebar_filters(self):
        """Create sidebar with filters and navigation."""
        st.sidebar.markdown("## 🎛️ Dashboard Controls")
        
        # Supplier filter
        st.sidebar.markdown("### 🏪 Supplier Filter")
        
        # Get all unique suppliers from GRN data
        grn_df = self.load_data("individual_hr995grn.csv")
        supplier_options = ["All Suppliers"]
        
        if not grn_df.empty and 'supplier_name' in grn_df.columns:
            unique_suppliers = grn_df['supplier_name'].dropna().unique()
            supplier_options.extend(sorted(unique_suppliers))
        
        selected_supplier = st.sidebar.selectbox(
            "Select Supplier",
            supplier_options,
            help="Filter all charts and analysis by specific supplier"
        )
        
        # Show supplier stats if selected
        if selected_supplier != "All Suppliers" and not grn_df.empty:
            supplier_data = grn_df[grn_df['supplier_name'] == selected_supplier]
            if not supplier_data.empty:
                st.sidebar.markdown(f"**📊 {selected_supplier} Stats:**")
                st.sidebar.markdown(f"• Transactions: {len(supplier_data):,}")
                if 'nett_grn_amt' in supplier_data.columns:
                    total_value = pd.to_numeric(supplier_data['nett_grn_amt'], errors='coerce').sum()
                    st.sidebar.markdown(f"• Total Value: R{total_value:,.0f}")
                st.sidebar.markdown("---")
        
        # Date range filter
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.selectbox(
            "Select Period",
            ["All Time", "Last 12 Months", "Last 6 Months", "Last 3 Months", "Custom Range"]
        )
        
        # Department filter
        st.sidebar.markdown("### 🏢 Department")
        department = st.sidebar.selectbox(
            "Select Department",
            ["All Departments", "Main Store", "Direct", "Other"]
        )
        
        # CHQ Analysis Mode
        st.sidebar.markdown("### 💳 Transaction Analysis Mode")
        exclude_chq = st.sidebar.selectbox(
            "CHQ Transaction Analysis",
            ["Include CHQ (Standard)", "Exclude CHQ (Primary Business Transactions Only)"],
            index=1,  # Default to excluding CHQ for better performance
            help="CHQ transactions are payment confirmations. Excluding them focuses analysis on primary business transactions (INV, VCH, CN, DN) and achieves 95.6% match rate vs 77.5% with CHQ included."
        )
        
        # Value threshold
        st.sidebar.markdown("### 💰 Value Filter")
        min_value = st.sidebar.number_input("Minimum Transaction Value (R)", min_value=0, value=0)
        
        # Refresh data
        st.sidebar.markdown("### 🔄 Data Management")
        if st.sidebar.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        # Export options
        st.sidebar.markdown("### 📁 Export Options")
        if st.sidebar.button("Export Current View"):
            st.sidebar.success("Export functionality coming soon!")
        
        return {
            'supplier': selected_supplier,
            'date_range': date_range,
            'department': department,
            'exclude_chq': exclude_chq == "Exclude CHQ (Primary Business Transactions Only)",
            'min_value': min_value
        }
    
    def create_anomaly_detection(self, filters=None):
        """Create comprehensive anomaly detection with corrected data relationships."""
        st.header("🚨 Anomaly Detection & Risk Analysis")
        st.markdown("*Advanced anomaly detection using corrected data relationships and business logic*")
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        # Load linked data with corrected relationships
        linked_data = self.load_linked_data(filters)
        grn_df = linked_data['grn']
        issue_df = linked_data['issue']
        hr390_df = linked_data['hr390']
        hr185_df = linked_data['hr185']
        
        # Load voucher data separately (not filtered for anomaly detection)
        voucher_df = self.load_data("individual_hr995vouch.csv")
        
        if not any(len(df) > 0 if df is not None else False for df in [grn_df, issue_df, voucher_df]):
            st.warning("No data available for anomaly detection.")
            return
        
        # Create tabs for different anomaly types
        anomaly_tab1, anomaly_tab2, anomaly_tab3, anomaly_tab4, anomaly_tab5 = st.tabs([
            "� Financial Anomalies",
            "� Relationship Anomalies", 
            "📊 Data Quality Issues",
            "⏱️ Timing Anomalies",
            "🎯 Pattern Anomalies"
        ])
        
        with anomaly_tab1:
            self.create_financial_anomalies(grn_df, voucher_df)
            self.create_volume_anomalies(grn_df, issue_df)
        
        with anomaly_tab2:
            self.create_relationship_anomalies(linked_data)
        
        with anomaly_tab3:
            self.create_data_quality_anomalies(grn_df, issue_df)
        
        with anomaly_tab4:
            self.create_timing_anomalies(grn_df, issue_df)
        
        with anomaly_tab5:
            self.create_pattern_anomalies(grn_df, issue_df, hr390_df)
    
    
    def create_relationship_anomalies(self, linked_data):
        """Detect anomalies in data relationships using corrected business logic."""
        st.subheader("🔗 Relationship Anomalies (Corrected)")
        st.info("✅ Analysis using corrected data relationships: Issue ↔ HR390, GRN ↔ HR185, GRN ↔ Voucher")
        
        grn_df = linked_data['grn']
        issue_df = linked_data['issue']
        voucher_df = linked_data['voucher']
        hr390_df = linked_data['hr390']
        hr185_df = linked_data['hr185']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Orphaned Records Analysis")
            
            # Orphaned Issues (no HR390 link)
            if not issue_df.empty and hr390_df is not None and not hr390_df.empty:
                issue_refs = set(issue_df['requisition_no_normalized'].dropna())
                hr390_refs = set(hr390_df['reference_normalized'].dropna())
                
                orphaned_issues = issue_refs - hr390_refs
                if len(orphaned_issues) > 0:
                    st.metric("🔴 Orphaned Issues (No HR390)", len(orphaned_issues))
                    
                    # Calculate value impact
                    orphaned_issue_records = issue_df[issue_df['requisition_no_normalized'].isin(orphaned_issues)]
                    if 'amount' in orphaned_issue_records.columns:
                        orphaned_value = pd.to_numeric(orphaned_issue_records['amount'], errors='coerce').sum()
                        st.metric("💰 Orphaned Issue Value", f"R{orphaned_value:,.2f}")
                else:
                    st.success("✅ All Issues linked to HR390")
            
            # Orphaned GRNs (no HR185 link)
            if not grn_df.empty and hr185_df is not None and not hr185_df.empty:
                grn_refs = set(grn_df['inv_no_normalized'].dropna())
                hr185_refs = set(hr185_df['reference_normalized'].dropna())
                
                orphaned_grns = grn_refs - hr185_refs
                if len(orphaned_grns) > 0:
                    st.metric("🔴 Orphaned GRNs (No HR185)", len(orphaned_grns))
                    
                    # Calculate value impact
                    orphaned_grn_records = grn_df[grn_df['inv_no_normalized'].isin(orphaned_grns)]
                    if 'nett_grn_amt' in orphaned_grn_records.columns:
                        orphaned_value = pd.to_numeric(orphaned_grn_records['nett_grn_amt'], errors='coerce').sum()
                        st.metric("💰 Orphaned GRN Value", f"R{orphaned_value:,.2f}")
                else:
                    st.success("✅ All GRNs linked to HR185")
        
        with col2:
            st.markdown("### ⚠️ Invalid References")
            
            # Invalid voucher references
            if not grn_df.empty and voucher_df is not None and not voucher_df.empty:
                grn_voucher_refs = set(grn_df['voucher_normalized'].dropna())
                actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
                
                invalid_vouchers = grn_voucher_refs - actual_vouchers
                if len(invalid_vouchers) > 0:
                    st.metric("❌ Invalid Voucher References", len(invalid_vouchers))
                    
                    # Calculate value impact
                    invalid_grn_records = grn_df[grn_df['voucher_normalized'].isin(invalid_vouchers)]
                    if 'nett_grn_amt' in invalid_grn_records.columns:
                        invalid_value = pd.to_numeric(invalid_grn_records['nett_grn_amt'], errors='coerce').sum()
                        st.metric("💰 Invalid Voucher Value", f"R{invalid_value:,.2f}")
                        
                        # Show validation rate
                        if len(grn_voucher_refs) > 0:
                            validation_rate = len(actual_vouchers & grn_voucher_refs) / len(grn_voucher_refs) * 100
                            st.metric("📈 Voucher Validation Rate", f"{validation_rate:.1f}%")
                else:
                    st.success("✅ All voucher references valid")
        
        # Relationship coverage summary
        st.markdown("### 📊 Relationship Coverage Summary")
        
        coverage_data = []
        
        # Issue → HR390 coverage
        if not issue_df.empty and hr390_df is not None and not hr390_df.empty:
            issue_coverage = len(set(issue_df['requisition_no_normalized'].dropna()) & 
                               set(hr390_df['reference_normalized'].dropna())) / len(set(issue_df['requisition_no_normalized'].dropna())) * 100
            coverage_data.append({'Relationship': 'Issue → HR390', 'Coverage': issue_coverage})
        
        # GRN → HR185 coverage
        if not grn_df.empty and hr185_df is not None and not hr185_df.empty:
            grn_coverage = len(set(grn_df['inv_no_normalized'].dropna()) & 
                              set(hr185_df['reference_normalized'].dropna())) / len(set(grn_df['inv_no_normalized'].dropna())) * 100
            coverage_data.append({'Relationship': 'GRN → HR185', 'Coverage': grn_coverage})
        
        # GRN → Voucher coverage
        if not grn_df.empty and voucher_df is not None and not voucher_df.empty:
            voucher_coverage = len(set(grn_df['voucher_normalized'].dropna()) & 
                                 set(voucher_df['voucher_no_normalized'].dropna())) / len(set(grn_df['voucher_normalized'].dropna())) * 100
            coverage_data.append({'Relationship': 'GRN → Voucher', 'Coverage': voucher_coverage})
        
        if coverage_data:
            coverage_df = pd.DataFrame(coverage_data)
            
            fig = px.bar(
                coverage_df,
                x='Relationship',
                y='Coverage',
                title="Data Relationship Coverage Analysis",
                color='Coverage',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig.update_layout(yaxis_title="Coverage Percentage (%)")
            st.plotly_chart(fig, use_container_width=True, key="data_coverage_metrics")
    
    def create_data_quality_anomalies(self, grn_df, issue_df):
        """Detect data quality issues and inconsistencies."""
        st.subheader("📊 Data Quality Issues")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 Missing Data Analysis")
            
            # GRN missing data
            if not grn_df.empty:
                missing_analysis = []
                for col in ['supplier_name', 'item_no', 'voucher', 'nett_grn_amt']:
                    if col in grn_df.columns:
                        missing_count = grn_df[col].isna().sum()
                        missing_pct = missing_count / len(grn_df) * 100
                        missing_analysis.append({
                            'Column': col,
                            'Missing Count': missing_count,
                            'Missing %': f"{missing_pct:.1f}%"
                        })
                
                if missing_analysis:
                    st.dataframe(pd.DataFrame(missing_analysis), use_container_width=True, hide_index=True)
            
            # Issue missing data
            if not issue_df.empty:
                st.markdown("#### Issue Data Missing Fields")
                issue_missing = []
                for col in ['requisition_no', 'item_no', 'quantity']:
                    if col in issue_df.columns:
                        missing_count = issue_df[col].isna().sum()
                        missing_pct = missing_count / len(issue_df) * 100
                        issue_missing.append({
                            'Column': col,
                            'Missing Count': missing_count,
                            'Missing %': f"{missing_pct:.1f}%"
                        })
                
                if issue_missing:
                    st.dataframe(pd.DataFrame(issue_missing), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📊 Data Quality Overview")
            
            # True inconsistencies (negative values that shouldn't exist)
            true_issues = []
            
            if not grn_df.empty and 'nett_grn_amt' in grn_df.columns:
                negative_grn = (pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce') < 0).sum()
                if negative_grn > 0:
                    true_issues.append(f"🔴 {negative_grn} GRN records with negative amounts")
            
            if not issue_df.empty and 'quantity' in issue_df.columns:
                negative_qty = (pd.to_numeric(issue_df['quantity'], errors='coerce') < 0).sum()
                if negative_qty > 0:
                    true_issues.append(f"🔴 {negative_qty} Issue records with negative quantities")
            
            # Normal business patterns (not inconsistencies)
            st.markdown("#### 📋 Normal Business Patterns")
            business_patterns = []
            
            if not grn_df.empty and 'grn_no' in grn_df.columns:
                duplicate_grns = grn_df['grn_no'].duplicated().sum()
                if duplicate_grns > 0:
                    business_patterns.append(f"✅ {duplicate_grns} GRN line items (multiple items per GRN)")
            
            if not issue_df.empty and 'requisition_no' in issue_df.columns:
                duplicate_reqs = issue_df['requisition_no'].duplicated().sum()
                if duplicate_reqs > 0:
                    business_patterns.append(f"✅ {duplicate_reqs} Requisition line items (multiple items per requisition)")
            
            # Display results
            if true_issues:
                st.markdown("#### ⚠️ Data Issues Requiring Attention")
                for issue in true_issues:
                    st.markdown(f"- {issue}")
            else:
                st.success("✅ No data quality issues detected")
                
            if business_patterns:
                for pattern in business_patterns:
                    st.markdown(f"- {pattern}")
            
            st.info("💡 **Note**: Multiple line items per document (GRN/Requisition) are normal business practice, not data inconsistencies.")
    
    def create_timing_anomalies(self, grn_df, issue_df):
        """Detect timing-related anomalies in transaction processing."""
        st.subheader("⏱️ Timing Anomalies")
        
        # Weekend transactions
        weekend_anomalies = []
        
        if not grn_df.empty:
            date_cols = [col for col in grn_df.columns if 'date' in col.lower()]
            for date_col in date_cols:
                if grn_df[date_col].notna().any():
                    grn_df[f'{date_col}_parsed'] = pd.to_datetime(grn_df[date_col], errors='coerce')
                    weekend_grns = grn_df[grn_df[f'{date_col}_parsed'].dt.weekday >= 5]
                    if len(weekend_grns) > 0:
                        weekend_anomalies.append(f"🟡 {len(weekend_grns)} GRN transactions on weekends")
        
        if not issue_df.empty:
            date_cols = [col for col in issue_df.columns if 'date' in col.lower()]
            for date_col in date_cols:
                if issue_df[date_col].notna().any():
                    issue_df[f'{date_col}_parsed'] = pd.to_datetime(issue_df[date_col], errors='coerce')
                    weekend_issues = issue_df[issue_df[f'{date_col}_parsed'].dt.weekday >= 5]
                    if len(weekend_issues) > 0:
                        weekend_anomalies.append(f"🟡 {len(weekend_issues)} Issue transactions on weekends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Weekend Activity Analysis")
            if weekend_anomalies:
                for anomaly in weekend_anomalies:
                    st.markdown(f"- {anomaly}")
            else:
                st.success("✅ No weekend transaction anomalies detected")
        
        with col2:
            st.markdown("### ⏰ Processing Time Anomalies")
            # This would be enhanced with more sophisticated timing analysis
            st.info("Processing time analysis available in Operational Analytics → Processing Times")

    def create_financial_anomalies(self, grn_df, voucher_df):
        """Detect financial anomalies and unusual spending patterns."""
        st.subheader("💸 Financial Anomalies & Unusual Spending")
        
        if len(grn_df) == 0:
            st.warning("No GRN data available for financial anomaly detection.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # High-value transactions (outliers)
            st.markdown("### 💰 High-Value Transaction Outliers")
            
            # Use the correct column name for GRN values
            value_col = None
            for col in ['gross_value', 'nett_grn_amt', 'value', 'amount']:
                if col in grn_df.columns:
                    value_col = col
                    break
            
            if value_col and len(grn_df[grn_df[value_col].notna()]) > 0:
                # Filter out null values
                valid_values = grn_df[grn_df[value_col].notna()]
                
                Q1 = valid_values[value_col].quantile(0.25)
                Q3 = valid_values[value_col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_threshold = Q3 + 1.5 * IQR
                
                outliers = valid_values[valid_values[value_col] > outlier_threshold].copy()
                
                if len(outliers) > 0:
                    # Create outlier visualization
                    fig = go.Figure()
                    
                    # Add normal transactions
                    normal_data = valid_values[valid_values[value_col] <= outlier_threshold]
                    fig.add_trace(go.Scatter(
                        x=normal_data.index,
                        y=normal_data[value_col],
                        mode='markers',
                        name='Normal Transactions',
                        marker=dict(color='lightblue', size=4)
                    ))
                    
                    # Add outliers
                    fig.add_trace(go.Scatter(
                        x=outliers.index,
                        y=outliers[value_col],
                        mode='markers',
                        name='High-Value Outliers',
                        marker=dict(color='red', size=8, symbol='diamond'),
                        text=[f"Item: {item}<br>Value: R{value:,.2f}<br>Supplier: {supp}" 
                              for item, value, supp in zip(
                                  outliers.get('item_no', outliers.get('item_code', 'Unknown')),
                                  outliers[value_col],
                                  outliers.get('supplier_name', 'Unknown')
                              )],
                        hovertemplate='%{text}<extra></extra>'
                    ))
                    
                    fig.add_hline(y=outlier_threshold, line_dash="dash", line_color="red",
                                annotation_text=f"Outlier Threshold: R{outlier_threshold:,.2f}")
                    
                    fig.update_layout(
                        title="High-Value Transaction Detection",
                        xaxis_title="Transaction Index",
                        yaxis_title=f"{value_col.replace('_', ' ').title()} (R)",
                        height=400,
                        annotations=[
                            dict(
                                text=self.get_data_source_tooltip('hr995_grn.csv'),
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.02, y=0.98,
                                xanchor="left", yanchor="top",
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="gray",
                                borderwidth=1,
                                font=dict(size=10)
                            )
                        ]
                    )
                    
                    # Update hover templates
                    fig.update_traces(
                        selector=dict(name='Normal Transactions'),
                        hovertemplate="<b>Transaction Index:</b> %{x}<br>" +
                                      f"<b>{value_col.replace('_', ' ').title()}:</b> R%{{y:,.2f}}<br>" +
                                      "<b>Data Source:</b> GRN Records<br>" +
                                      "<extra></extra>"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="financial_outliers_scatter")
                    
                    # Show outlier summary
                    st.markdown("#### 🚨 Alert Summary:")
                    total_outlier_value = outliers[value_col].sum()
                    avg_outlier_value = outliers[value_col].mean()
                    
                    alert_col1, alert_col2, alert_col3 = st.columns(3)
                    with alert_col1:
                        st.metric("High-Value Transactions", len(outliers))
                    with alert_col2:
                        st.metric("Total Outlier Value", f"R{total_outlier_value:,.2f}")
                    with alert_col3:
                        st.metric("Average Outlier Value", f"R{avg_outlier_value:,.2f}")
                    
                    # Show top outliers table
                    st.markdown("#### 📊 Top High-Value Transactions:")
                    display_outliers = outliers.nlargest(10, value_col)[
                        ['item_no' if 'item_no' in outliers.columns else 'item_code',
                         'supplier_name', value_col, 'date']
                    ].copy()
                    display_outliers[value_col] = display_outliers[value_col].apply(lambda x: f"R{x:,.2f}")
                    st.dataframe(display_outliers, use_container_width=True)
                else:
                    st.info("No high-value outliers detected in the current dataset.")
            else:
                st.warning("No value column found for financial analysis. Available columns: " + ", ".join(grn_df.columns))
        
        with col2:
            # Price volatility analysis
            st.markdown("### 📈 Price Volatility Alerts")
            
            if 'unit_price' in grn_df.columns:
                # Group by item and calculate price volatility
                item_col = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
                if item_col in grn_df.columns:
                    price_stats = grn_df.groupby(item_col)['unit_price'].agg([
                        'count', 'mean', 'std', 'min', 'max'
                    ]).reset_index()
                    
                    # Calculate coefficient of variation for volatility
                    price_stats['cv'] = (price_stats['std'] / price_stats['mean']) * 100
                    price_stats = price_stats[price_stats['count'] >= 3]  # Need at least 3 transactions
                    
                    # High volatility items (CV > 50%)
                    volatile_items = price_stats[price_stats['cv'] > 50].sort_values('cv', ascending=False)
                    
                    if len(volatile_items) > 0:
                        # Create volatility chart
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=volatile_items[item_col].head(15),
                            y=volatile_items['cv'].head(15),
                            name='Price Volatility (CV%)',
                            marker_color='orange',
                            text=volatile_items['cv'].head(15).round(1),
                            textposition='outside'
                        ))
                        
                        fig.add_hline(y=50, line_dash="dash", line_color="red",
                                    annotation_text="High Volatility Threshold (50%)")
                        
                        fig.update_layout(
                            title="Items with High Price Volatility",
                            xaxis_title="Item Code",
                            yaxis_title="Coefficient of Variation (%)",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="price_volatility_analysis")
                        
                        # Volatility metrics
                        vol_col1, vol_col2, vol_col3 = st.columns(3)
                        with vol_col1:
                            st.metric("Volatile Items", len(volatile_items))
                        with vol_col2:
                            st.metric("Avg Volatility", f"{volatile_items['cv'].mean():.1f}%")
                        with vol_col3:
                            st.metric("Max Volatility", f"{volatile_items['cv'].max():.1f}%")
                        
                        # Show volatile items table
                        st.markdown("#### 📊 Most Volatile Items:")
                        display_volatile = volatile_items.head(10)[
                            [item_col, 'count', 'mean', 'cv', 'min', 'max']
                        ].copy()
                        display_volatile['mean'] = display_volatile['mean'].apply(lambda x: f"R{x:.2f}")
                        display_volatile['min'] = display_volatile['min'].apply(lambda x: f"R{x:.2f}")
                        display_volatile['max'] = display_volatile['max'].apply(lambda x: f"R{x:.2f}")
                        display_volatile['cv'] = display_volatile['cv'].apply(lambda x: f"{x:.1f}%")
                        display_volatile.columns = ['Item Code', 'Transactions', 'Avg Price', 'Volatility', 'Min Price', 'Max Price']
                        st.dataframe(display_volatile, use_container_width=True)
                    else:
                        st.info("No items with high price volatility detected.")
        
        # Supplier spending anomalies
        st.markdown("### 🏪 Supplier Spending Anomalies")
        
        if 'supplier_name' in grn_df.columns and 'gross_value' in grn_df.columns:
            supplier_spending = grn_df.groupby('supplier_name')['gross_value'].agg([
                'sum', 'count', 'mean'
            ]).reset_index()
            
            # Detect suppliers with unusually high spending
            spending_Q3 = supplier_spending['sum'].quantile(0.75)
            spending_IQR = supplier_spending['sum'].quantile(0.75) - supplier_spending['sum'].quantile(0.25)
            spending_threshold = spending_Q3 + 1.5 * spending_IQR
            
            high_spending_suppliers = supplier_spending[
                supplier_spending['sum'] > spending_threshold
            ].sort_values('sum', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if len(high_spending_suppliers) > 0:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=high_spending_suppliers['supplier_name'],
                        y=high_spending_suppliers['sum'],
                        name='High Spending Suppliers',
                        marker_color='red',
                        text=[f"R{x:,.0f}" for x in high_spending_suppliers['sum']],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title="Suppliers with Unusually High Spending",
                        xaxis_title="Supplier",
                        yaxis_title="Total Spending (R)",
                        height=400,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="high_spending_suppliers")
                else:
                    st.info("No suppliers with unusually high spending detected.")
            
            with col2:
                # Transaction frequency anomalies
                avg_transactions = supplier_spending['count'].mean()
                high_freq_threshold = avg_transactions + 2 * supplier_spending['count'].std()
                
                high_freq_suppliers = supplier_spending[
                    supplier_spending['count'] > high_freq_threshold
                ].sort_values('count', ascending=False)
                
                if len(high_freq_suppliers) > 0:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=high_freq_suppliers['supplier_name'],
                        y=high_freq_suppliers['count'],
                        name='High Frequency Suppliers',
                        marker_color='orange',
                        text=high_freq_suppliers['count'],
                        textposition='outside'
                    ))
                    
                    fig.add_hline(y=high_freq_threshold, line_dash="dash", line_color="red",
                                annotation_text=f"High Frequency Threshold: {high_freq_threshold:.0f}")
                    
                    fig.update_layout(
                        title="Suppliers with Unusually High Transaction Frequency",
                        xaxis_title="Supplier",
                        yaxis_title="Number of Transactions",
                        height=400,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="high_frequency_suppliers")
                else:
                    st.info("No suppliers with unusually high transaction frequency detected.")
    
    def create_volume_anomalies(self, grn_df, issue_df):
        """Detect volume and quantity anomalies."""
        st.subheader("📊 Volume & Quantity Anomalies")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # GRN quantity outliers
            st.markdown("### 📈 Unusual GRN Quantities")
            
            # Use the correct quantity column name
            qty_col_grn = None
            for col in ['grn_qty', 'quantity', 'qty']:
                if col in grn_df.columns:
                    qty_col_grn = col
                    break
            
            if qty_col_grn and len(grn_df) > 0:
                # Remove zero and negative quantities
                valid_grn = grn_df[grn_df[qty_col_grn] > 0].copy()
                
                if len(valid_grn) > 0:
                    # Calculate outliers
                    Q1 = valid_grn[qty_col_grn].quantile(0.25)
                    Q3 = valid_grn[qty_col_grn].quantile(0.75)
                    IQR = Q3 - Q1
                    upper_threshold = Q3 + 2 * IQR  # More sensitive threshold
                    
                    qty_outliers = valid_grn[valid_grn[qty_col_grn] > upper_threshold].copy()
                    
                    if len(qty_outliers) > 0:
                        # Create box plot with outliers
                        fig = go.Figure()
                        
                        fig.add_trace(go.Box(
                            y=valid_grn[qty_col_grn],
                            name='GRN Quantities',
                            boxpoints='outliers',
                            jitter=0.3,
                            pointpos=-1.8,
                            marker_color='lightblue'
                        ))
                        
                        fig.update_layout(
                            title="GRN Quantity Distribution with Outliers",
                            yaxis_title="Quantity",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="grn_quantity_outliers")
                        
                        # Outlier metrics
                        qty_col1, qty_col2, qty_col3 = st.columns(3)
                        with qty_col1:
                            st.metric("Quantity Outliers", len(qty_outliers))
                        with qty_col2:
                            st.metric("Max Quantity", f"{qty_outliers[qty_col_grn].max():,.0f}")
                        with qty_col3:
                            st.metric("Threshold", f"{upper_threshold:,.0f}")
                        
                        # Show outliers table
                        if len(qty_outliers) > 0:
                            st.markdown("#### 🚨 Unusual Quantity Transactions:")
                            item_col = 'item_no' if 'item_no' in qty_outliers.columns else 'item_code'
                            display_cols = [item_col, 'supplier_name', qty_col_grn]
                            
                            # Add value column if available
                            value_col = None
                            for col in ['gross_value', 'nett_grn_amt', 'value', 'amount']:
                                if col in qty_outliers.columns:
                                    value_col = col
                                    display_cols.append(col)
                                    break
                            
                            display_cols = [col for col in display_cols if col in qty_outliers.columns]
                            
                            display_qty = qty_outliers.nlargest(10, qty_col_grn)[display_cols].copy()
                            if value_col and value_col in display_qty.columns:
                                display_qty[value_col] = display_qty[value_col].apply(lambda x: f"R{x:,.2f}")
                            st.dataframe(display_qty, use_container_width=True)
                    else:
                        st.info("No unusual GRN quantities detected.")
                else:
                    st.warning("No valid GRN quantity data available.")
            else:
                st.warning("No quantity column found in GRN data.")
        
        with col2:
            # Issue quantity outliers
            st.markdown("### 📉 Unusual Issue Quantities")
            
            # Use the correct quantity column name for issues
            qty_col_issue = None
            for col in ['issue_qty', 'quantity', 'qty']:
                if col in issue_df.columns:
                    qty_col_issue = col
                    break
            
            if qty_col_issue and len(issue_df) > 0:
                valid_issue = issue_df[issue_df[qty_col_issue] > 0].copy()
                
                if len(valid_issue) > 0:
                    # Calculate outliers
                    Q1 = valid_issue[qty_col_issue].quantile(0.25)
                    Q3 = valid_issue[qty_col_issue].quantile(0.75)
                    IQR = Q3 - Q1
                    upper_threshold = Q3 + 2 * IQR
                    
                    issue_outliers = valid_issue[valid_issue[qty_col_issue] > upper_threshold].copy()
                    
                    if len(issue_outliers) > 0:
                        # Create histogram with outliers highlighted
                        fig = go.Figure()
                        
                        # Normal data
                        normal_issues = valid_issue[valid_issue[qty_col_issue] <= upper_threshold]
                        fig.add_trace(go.Histogram(
                            x=normal_issues[qty_col_issue],
                            name='Normal Issues',
                            opacity=0.7,
                            marker_color='lightgreen'
                        ))
                        
                        # Outliers
                        fig.add_trace(go.Histogram(
                            x=issue_outliers[qty_col_issue],
                            name='Outlier Issues',
                            opacity=0.7,
                            marker_color='red'
                        ))
                        
                        fig.update_layout(
                            title="Issue Quantity Distribution",
                            xaxis_title="Issue Quantity",
                            yaxis_title="Frequency",
                            height=400,
                            barmode='overlay'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="issue_quantity_outliers")
                        
                        # Outlier metrics
                        issue_col1, issue_col2, issue_col3 = st.columns(3)
                        with issue_col1:
                            st.metric("Issue Outliers", len(issue_outliers))
                        with issue_col2:
                            st.metric("Max Issue Qty", f"{issue_outliers[qty_col_issue].max():,.0f}")
                        with issue_col3:
                            st.metric("Threshold", f"{upper_threshold:,.0f}")
                    else:
                        st.info("No unusual issue quantities detected.")
                else:
                    st.warning("No valid issue quantity data available.")
            else:
                st.warning("No quantity column found in Issue data.")
        
        # Stock level anomalies
        st.markdown("### 📦 Stock Level Anomalies")
        
        if len(grn_df) > 0 and len(issue_df) > 0:
            # Get correct column names
            item_col_grn = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
            item_col_issue = 'item_no' if 'item_no' in issue_df.columns else 'item_code'
            
            qty_col_grn = None
            for col in ['grn_qty', 'quantity', 'qty']:
                if col in grn_df.columns:
                    qty_col_grn = col
                    break
            
            qty_col_issue = None
            for col in ['issue_qty', 'quantity', 'qty']:
                if col in issue_df.columns:
                    qty_col_issue = col
                    break
            
            if (item_col_grn in grn_df.columns and item_col_issue in issue_df.columns and 
                qty_col_grn and qty_col_issue):
                
                # Sum GRN quantities by item
                grn_totals = grn_df.groupby(item_col_grn)[qty_col_grn].sum().reset_index()
                grn_totals.columns = ['item_code', 'total_received']
                
                # Sum issue quantities by item
                issue_totals = issue_df.groupby(item_col_issue)[qty_col_issue].sum().reset_index()
                issue_totals.columns = ['item_code', 'total_issued']
                
                # Merge and calculate current stock
                stock_balance = grn_totals.merge(issue_totals, on='item_code', how='outer').fillna(0)
                stock_balance['current_stock'] = stock_balance['total_received'] - stock_balance['total_issued']
                
                # Detect negative stock (impossible situation)
                negative_stock = stock_balance[stock_balance['current_stock'] < 0].copy()
                
                # Detect zero stock items that had recent activity
                zero_stock = stock_balance[stock_balance['current_stock'] == 0].copy()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if len(negative_stock) > 0:
                        st.markdown("#### 🚨 CRITICAL: Negative Stock Levels")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=negative_stock['item_code'].head(15),
                            y=negative_stock['current_stock'].head(15),
                            name='Negative Stock',
                            marker_color='red',
                            text=negative_stock['current_stock'].head(15),
                            textposition='outside'
                        ))
                        
                        fig.update_layout(
                            title="Items with Negative Stock Levels",
                            xaxis_title="Item Code",
                            yaxis_title="Stock Level",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="negative_stock_levels")
                        
                        st.error(f"🚨 ALERT: {len(negative_stock)} items have negative stock levels!")
                        st.dataframe(negative_stock.head(10), use_container_width=True)
                    else:
                        st.success("✅ No negative stock levels detected.")
                
                with col2:
                    if len(zero_stock) > 0:
                        st.markdown("#### ⚠️ Zero Stock Items")
                        
                        st.metric("Items with Zero Stock", len(zero_stock))
                        
                        # Show items with highest issued quantities but zero stock
                        zero_high_activity = zero_stock.nlargest(10, 'total_issued')
                        
                        if len(zero_high_activity) > 0:
                            fig = go.Figure()
                            
                            fig.add_trace(go.Bar(
                                x=zero_high_activity['item_code'],
                                y=zero_high_activity['total_issued'],
                                name='Total Issued',
                                marker_color='orange'
                            ))
                            
                            fig.update_layout(
                                title="High-Activity Items with Zero Stock",
                                xaxis_title="Item Code",
                                yaxis_title="Total Issued Quantity",
                                height=400,
                                xaxis_tickangle=-45
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="zero_stock_high_activity")
                    else:
                        st.info("All items have positive stock levels.")
            else:
                st.warning("Unable to perform stock level analysis due to missing columns.")
    
    def create_time_anomalies(self, grn_df, issue_df):
        """Detect time-based anomalies and unusual patterns."""
        st.subheader("⏰ Time-based Anomalies & Unusual Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekend/Holiday activity detection
            st.markdown("### 📅 Weekend & Holiday Activity")
            
            # Use correct date column name
            date_col = None
            for col in ['grn_date', 'date', 'transaction_date']:
                if col in grn_df.columns:
                    date_col = col
                    break
            
            if date_col and len(grn_df) > 0:
                grn_df_copy = grn_df.copy()
                grn_df_copy[date_col] = pd.to_datetime(grn_df_copy[date_col], errors='coerce')
                grn_df_copy = grn_df_copy.dropna(subset=[date_col])
                
                if len(grn_df_copy) > 0:
                    grn_df_copy['day_of_week'] = grn_df_copy[date_col].dt.day_name()
                    grn_df_copy['is_weekend'] = grn_df_copy[date_col].dt.dayofweek >= 5
                    
                    # Weekend transactions
                    weekend_transactions = grn_df_copy[grn_df_copy['is_weekend']].copy()
                    
                    if len(weekend_transactions) > 0:
                        # Create day of week activity chart
                        daily_activity = grn_df_copy.groupby('day_of_week').size().reset_index()
                        daily_activity.columns = ['day', 'count']
                        
                        # Order days properly
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        daily_activity['day'] = pd.Categorical(daily_activity['day'], categories=day_order, ordered=True)
                        daily_activity = daily_activity.sort_values('day')
                        
                        # Color weekend days differently
                        colors = ['lightblue' if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] 
                                else 'red' for day in daily_activity['day']]
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=daily_activity['day'],
                            y=daily_activity['count'],
                            name='Transactions by Day',
                            marker_color=colors,
                            text=daily_activity['count'],
                            textposition='outside'
                        ))
                        
                        fig.update_layout(
                            title="Transaction Activity by Day of Week",
                            xaxis_title="Day of Week",
                            yaxis_title="Number of Transactions",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="weekly_transaction_activity")
                        
                        # Weekend metrics
                        weekend_col1, weekend_col2, weekend_col3 = st.columns(3)
                        with weekend_col1:
                            st.metric("Weekend Transactions", len(weekend_transactions))
                        with weekend_col2:
                            # Use correct value column
                            value_col = None
                            for col in ['gross_value', 'nett_grn_amt', 'value', 'amount']:
                                if col in weekend_transactions.columns:
                                    value_col = col
                                    break
                            weekend_value = weekend_transactions[value_col].sum() if value_col else 0
                            st.metric("Weekend Value", f"R{weekend_value:,.2f}")
                        with weekend_col3:
                            weekend_pct = (len(weekend_transactions) / len(grn_df_copy)) * 100
                            st.metric("Weekend %", f"{weekend_pct:.1f}%")
                        
                        if len(weekend_transactions) > 0:
                            st.warning(f"⚠️ {len(weekend_transactions)} transactions occurred on weekends")
                    else:
                        st.success("✅ No weekend transaction activity detected")
                else:
                    st.info("No valid date data available for analysis")
            else:
                st.warning("No date column found for time-based analysis")
        
        with col2:
            # After-hours activity (if time data available)
            st.markdown("### 🌙 After-Hours Activity Analysis")
            
            # Late/early transaction patterns
            if date_col and len(grn_df) > 0:
                grn_df_copy = grn_df.copy()
                
                # Check for unusual time patterns in transaction sequences
                grn_df_copy[date_col] = pd.to_datetime(grn_df_copy[date_col], errors='coerce')
                grn_df_copy = grn_df_copy.dropna(subset=[date_col])
                
                if len(grn_df_copy) > 0:
                    # Check for multiple transactions on same day by same supplier
                    grn_df_copy['date_only'] = grn_df_copy[date_col].dt.date
                    
                    if 'supplier_name' in grn_df_copy.columns:
                        daily_supplier_activity = grn_df_copy.groupby(['date_only', 'supplier_name']).size().reset_index()
                        daily_supplier_activity.columns = ['date', 'supplier', 'transaction_count']
                        
                        # Multiple transactions per day per supplier
                        multiple_daily = daily_supplier_activity[daily_supplier_activity['transaction_count'] > 3]
                        
                        if len(multiple_daily) > 0:
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=multiple_daily['date'],
                                y=multiple_daily['transaction_count'],
                                mode='markers',
                                marker=dict(
                                    size=multiple_daily['transaction_count'] * 3,
                                    color='red',
                                    opacity=0.7
                                ),
                                text=[f"Supplier: {supp}<br>Transactions: {count}" 
                                      for supp, count in zip(multiple_daily['supplier'], multiple_daily['transaction_count'])],
                                hovertemplate='%{text}<br>Date: %{x}<extra></extra>',
                                name='High Daily Activity'
                            ))
                            
                            fig.update_layout(
                                title="Days with Unusually High Transaction Activity",
                                xaxis_title="Date",
                                yaxis_title="Transactions per Day (per Supplier)",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="same_day_multi_supplier")
                            
                            # Activity metrics
                            activity_col1, activity_col2, activity_col3 = st.columns(3)
                            with activity_col1:
                                st.metric("High Activity Days", len(multiple_daily))
                            with activity_col2:
                                st.metric("Max Daily Transactions", multiple_daily['transaction_count'].max())
                            with activity_col3:
                                st.metric("Avg High Activity", f"{multiple_daily['transaction_count'].mean():.1f}")
                            
                            if len(multiple_daily) > 0:
                                st.warning(f"⚠️ {len(multiple_daily)} instances of high daily transaction activity detected")
                        else:
                            st.info("No unusual daily transaction patterns detected")
                    else:
                        st.info("Supplier information not available for activity analysis")
                else:
                    st.info("No valid date data available for activity analysis")
        
        # Seasonal anomalies
        st.markdown("### 🍂 Seasonal & Monthly Anomalies")
        
        if date_col and len(grn_df) > 0:
            grn_df_copy = grn_df.copy()
            grn_df_copy[date_col] = pd.to_datetime(grn_df_copy[date_col], errors='coerce')
            grn_df_copy = grn_df_copy.dropna(subset=[date_col])
            
            if len(grn_df_copy) > 0:
                grn_df_copy['month'] = grn_df_copy[date_col].dt.month
                grn_df_copy['month_name'] = grn_df_copy[date_col].dt.strftime('%B')
                
                # Use correct value column
                value_col = None
                for col in ['gross_value', 'nett_grn_amt', 'value', 'amount']:
                    if col in grn_df_copy.columns:
                        value_col = col
                        break
                
                # Monthly activity analysis
                if value_col:
                    monthly_stats = grn_df_copy.groupby(['month', 'month_name']).agg({
                        value_col: ['sum', 'count', 'mean']
                    }).reset_index()
                    monthly_stats.columns = ['month', 'month_name', 'total_value', 'transaction_count', 'avg_value']
                    
                    # Detect outlier months
                    value_mean = monthly_stats['total_value'].mean()
                    value_std = monthly_stats['total_value'].std()
                    outlier_threshold = value_mean + 2 * value_std
                    
                    outlier_months = monthly_stats[monthly_stats['total_value'] > outlier_threshold]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Monthly spending pattern
                        fig = go.Figure()
                        
                        colors = ['red' if value > outlier_threshold else 'lightblue' 
                                for value in monthly_stats['total_value']]
                        
                        fig.add_trace(go.Bar(
                            x=monthly_stats['month_name'],
                            y=monthly_stats['total_value'],
                            name='Monthly Spending',
                            marker_color=colors,
                            text=[f"R{x:,.0f}" for x in monthly_stats['total_value']],
                            textposition='outside'
                        ))
                        
                        if len(outlier_months) > 0:
                            fig.add_hline(y=outlier_threshold, line_dash="dash", line_color="red",
                                        annotation_text=f"Outlier Threshold: R{outlier_threshold:,.0f}")
                        
                        fig.update_layout(
                            title="Monthly Spending Patterns",
                            xaxis_title="Month",
                            yaxis_title=f"Total {value_col.replace('_', ' ').title()} (R)",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="after_hours_transactions")
                    
                    with col2:
                        # Transaction count by month
                        count_mean = monthly_stats['transaction_count'].mean()
                        count_std = monthly_stats['transaction_count'].std()
                        count_threshold = count_mean + 2 * count_std
                        
                        outlier_count_months = monthly_stats[monthly_stats['transaction_count'] > count_threshold]
                        
                        colors = ['orange' if count > count_threshold else 'lightgreen' 
                                for count in monthly_stats['transaction_count']]
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=monthly_stats['month_name'],
                            y=monthly_stats['transaction_count'],
                            name='Monthly Transactions',
                            marker_color=colors,
                            text=monthly_stats['transaction_count'],
                            textposition='outside'
                        ))
                        
                        if len(outlier_count_months) > 0:
                            fig.add_hline(y=count_threshold, line_dash="dash", line_color="orange",
                                        annotation_text=f"High Activity Threshold: {count_threshold:.0f}")
                        
                        fig.update_layout(
                            title="Monthly Transaction Volume",
                            xaxis_title="Month",
                            yaxis_title="Number of Transactions",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="bulk_transaction_pattern")
                    
                    # Summary of anomalies
                    if len(outlier_months) > 0 or len(outlier_count_months) > 0:
                        st.markdown("#### 🚨 Monthly Anomaly Summary:")
                        
                        anom_col1, anom_col2, anom_col3 = st.columns(3)
                        with anom_col1:
                            st.metric("High Spending Months", len(outlier_months))
                        with anom_col2:
                            st.metric("High Activity Months", len(outlier_count_months))
                        with anom_col3:
                            if len(outlier_months) > 0:
                                max_spending_month = outlier_months.loc[outlier_months['total_value'].idxmax(), 'month_name']
                                st.metric("Peak Spending Month", max_spending_month)
                        
                        # Show anomalous months
                        if len(outlier_months) > 0:
                            st.markdown("**High Spending Months:**")
                            display_outlier_months = outlier_months[['month_name', 'total_value', 'transaction_count']].copy()
                            display_outlier_months['total_value'] = display_outlier_months['total_value'].apply(lambda x: f"R{x:,.2f}")
                            st.dataframe(display_outlier_months, use_container_width=True)
                else:
                    # Just show transaction count analysis if no value column
                    monthly_counts = grn_df_copy.groupby(['month', 'month_name']).size().reset_index()
                    monthly_counts.columns = ['month', 'month_name', 'transaction_count']
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=monthly_counts['month_name'],
                        y=monthly_counts['transaction_count'],
                        name='Monthly Transactions',
                        marker_color='lightblue',
                        text=monthly_counts['transaction_count'],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title="Monthly Transaction Volume",
                        xaxis_title="Month",
                        yaxis_title="Number of Transactions",
                        height=400,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="rapid_successive_transactions")
            else:
                st.info("No valid date data available for seasonal analysis")
        else:
            st.warning("No date column found for seasonal analysis")
    
    def create_pattern_anomalies(self, grn_df, issue_df, stock_df):
        """Detect pattern anomalies and unusual behaviors."""
        st.subheader("🎯 Pattern Anomalies & Behavioral Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Unusual supplier-item relationships
            st.markdown("### 🔗 Unusual Supplier-Item Patterns")
            
            if len(grn_df) > 0 and 'supplier_name' in grn_df.columns:
                item_col = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
                if item_col in grn_df.columns:
                    # Find items supplied by multiple suppliers
                    supplier_item_counts = grn_df.groupby(item_col)['supplier_name'].nunique().reset_index()
                    supplier_item_counts.columns = ['item_code', 'supplier_count']
                    
                    # Items with many suppliers (potential quality/consistency issues)
                    multi_supplier_items = supplier_item_counts[
                        supplier_item_counts['supplier_count'] > 3
                    ].sort_values('supplier_count', ascending=False)
                    
                    if len(multi_supplier_items) > 0:
                        # Create visualization
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=multi_supplier_items['item_code'].head(15),
                            y=multi_supplier_items['supplier_count'].head(15),
                            name='Supplier Count per Item',
                            marker_color='purple',
                            text=multi_supplier_items['supplier_count'].head(15),
                            textposition='outside'
                        ))
                        
                        fig.update_layout(
                            title="Items with Multiple Suppliers",
                            xaxis_title="Item Code",
                            yaxis_title="Number of Suppliers",
                            height=400,
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key="multi_supplier_items")
                        
                        # Multi-supplier metrics
                        multi_col1, multi_col2, multi_col3 = st.columns(3)
                        with multi_col1:
                            st.metric("Multi-Supplier Items", len(multi_supplier_items))
                        with multi_col2:
                            st.metric("Max Suppliers", multi_supplier_items['supplier_count'].max())
                        with multi_col3:
                            st.metric("Avg Suppliers", f"{multi_supplier_items['supplier_count'].mean():.1f}")
                        
                        # Show details
                        st.markdown("#### 📊 Items with Most Suppliers:")
                        st.dataframe(multi_supplier_items.head(10), use_container_width=True)
                        
                        st.warning(f"⚠️ {len(multi_supplier_items)} items are supplied by multiple suppliers. Consider supplier consolidation or quality standardization.")
                    else:
                        st.info("No items with excessive multiple suppliers detected.")
                else:
                    st.warning("No item column found for supplier analysis.")
            else:
                st.warning("Supplier data not available for pattern analysis.")
        
        with col2:
            # Unusual quantity patterns
            st.markdown("### 📏 Unusual Quantity Patterns")
            
            if len(grn_df) > 0 and len(issue_df) > 0:
                item_col_grn = 'item_no' if 'item_no' in grn_df.columns else 'item_code'
                item_col_issue = 'item_no' if 'item_no' in issue_df.columns else 'item_code'
                
                # Get correct quantity column names
                qty_col_grn = None
                for col in ['grn_qty', 'quantity', 'qty']:
                    if col in grn_df.columns:
                        qty_col_grn = col
                        break
                
                qty_col_issue = None
                for col in ['issue_qty', 'quantity', 'qty']:
                    if col in issue_df.columns:
                        qty_col_issue = col
                        break
                
                if (item_col_grn in grn_df.columns and item_col_issue in issue_df.columns and 
                    qty_col_grn and qty_col_issue):
                    # Calculate GRN vs Issue ratios
                    grn_totals = grn_df.groupby(item_col_grn)[qty_col_grn].sum().reset_index()
                    grn_totals.columns = ['item_code', 'total_grn']
                    
                    issue_totals = issue_df.groupby(item_col_issue)[qty_col_issue].sum().reset_index()
                    issue_totals.columns = ['item_code', 'total_issue']
                    
                    # Merge and calculate ratios
                    ratio_analysis = grn_totals.merge(issue_totals, on='item_code', how='inner')
                    
                    # Only analyze items with non-zero issues to avoid division by zero
                    ratio_analysis = ratio_analysis[ratio_analysis['total_issue'] > 0]
                    
                    if len(ratio_analysis) > 0:
                        ratio_analysis['grn_issue_ratio'] = ratio_analysis['total_grn'] / ratio_analysis['total_issue']
                        
                        # Find unusual ratios
                        # Very high ratio (much more received than issued - potential waste)
                        high_ratio_items = ratio_analysis[ratio_analysis['grn_issue_ratio'] > 5].copy()
                        
                        # Very low ratio (more issued than received - potential data error)
                        low_ratio_items = ratio_analysis[ratio_analysis['grn_issue_ratio'] < 0.5].copy()
                        
                        if len(high_ratio_items) > 0 or len(low_ratio_items) > 0:
                            # Create scatter plot of ratios
                            fig = go.Figure()
                            
                            # Normal ratios
                            normal_ratios = ratio_analysis[
                                (ratio_analysis['grn_issue_ratio'] >= 0.5) & 
                                (ratio_analysis['grn_issue_ratio'] <= 5)
                            ]
                            
                            fig.add_trace(go.Scatter(
                                x=normal_ratios['total_grn'],
                                y=normal_ratios['total_issue'],
                                mode='markers',
                                name='Normal Items',
                                marker=dict(color='lightblue', size=6),
                                text=[f"Item: {item}<br>Ratio: {ratio:.2f}" 
                                      for item, ratio in zip(normal_ratios['item_code'], normal_ratios['grn_issue_ratio'])],
                                hovertemplate='%{text}<br>GRN: %{x}<br>Issue: %{y}<extra></extra>'
                            ))
                            
                            # High ratio items
                            if len(high_ratio_items) > 0:
                                fig.add_trace(go.Scatter(
                                    x=high_ratio_items['total_grn'],
                                    y=high_ratio_items['total_issue'],
                                    mode='markers',
                                    name='Over-Stocked Items',
                                    marker=dict(color='red', size=10, symbol='diamond'),
                                    text=[f"Item: {item}<br>Ratio: {ratio:.2f}" 
                                          for item, ratio in zip(high_ratio_items['item_code'], high_ratio_items['grn_issue_ratio'])],
                                    hovertemplate='%{text}<br>GRN: %{x}<br>Issue: %{y}<extra></extra>'
                                ))
                            
                            # Low ratio items
                            if len(low_ratio_items) > 0:
                                fig.add_trace(go.Scatter(
                                    x=low_ratio_items['total_grn'],
                                    y=low_ratio_items['total_issue'],
                                    mode='markers',
                                    name='Under-Stocked Items',
                                    marker=dict(color='orange', size=10, symbol='square'),
                                    text=[f"Item: {item}<br>Ratio: {ratio:.2f}" 
                                          for item, ratio in zip(low_ratio_items['item_code'], low_ratio_items['grn_issue_ratio'])],
                                    hovertemplate='%{text}<br>GRN: %{x}<br>Issue: %{y}<extra></extra>'
                                ))
                            
                            # Add diagonal line for reference
                            max_val = max(ratio_analysis['total_grn'].max(), ratio_analysis['total_issue'].max())
                            fig.add_trace(go.Scatter(
                                x=[0, max_val],
                                y=[0, max_val],
                                mode='lines',
                                name='Equal Ratio Line',
                                line=dict(dash='dash', color='gray'),
                                showlegend=False
                            ))
                            
                            fig.update_layout(
                                title="GRN vs Issue Quantity Analysis",
                                xaxis_title="Total GRN Quantity",
                                yaxis_title="Total Issue Quantity",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="duplicate_transactions_analysis")
                            
                            # Ratio metrics
                            ratio_col1, ratio_col2, ratio_col3 = st.columns(3)
                            with ratio_col1:
                                st.metric("Over-Stocked Items", len(high_ratio_items))
                            with ratio_col2:
                                st.metric("Under-Stocked Items", len(low_ratio_items))
                            with ratio_col3:
                                if len(high_ratio_items) > 0:
                                    st.metric("Max Over-Stock Ratio", f"{high_ratio_items['grn_issue_ratio'].max():.1f}x")
                            
                            # Show problem items
                            if len(high_ratio_items) > 0:
                                st.markdown("#### 🚨 Over-Stocked Items (Potential Waste):")
                                display_high = high_ratio_items.nlargest(10, 'grn_issue_ratio')[
                                    ['item_code', 'total_grn', 'total_issue', 'grn_issue_ratio']
                                ].copy()
                                display_high['grn_issue_ratio'] = display_high['grn_issue_ratio'].apply(lambda x: f"{x:.2f}x")
                                st.dataframe(display_high, use_container_width=True)
                            
                            if len(low_ratio_items) > 0:
                                st.markdown("#### ⚠️ Under-Stocked Items (Potential Data Issues):")
                                display_low = low_ratio_items.nsmallest(10, 'grn_issue_ratio')[
                                    ['item_code', 'total_grn', 'total_issue', 'grn_issue_ratio']
                                ].copy()
                                display_low['grn_issue_ratio'] = display_low['grn_issue_ratio'].apply(lambda x: f"{x:.2f}x")
                                st.dataframe(display_low, use_container_width=True)
                        else:
                            st.success("✅ All GRN/Issue ratios appear normal.")
                    else:
                        st.info("No common items found between GRN and Issue data for ratio analysis.")
                else:
                    st.warning("Unable to perform quantity pattern analysis due to missing columns.")
            else:
                st.warning("Insufficient data for quantity pattern analysis.")
        
        # Overall anomaly summary
        st.markdown("### 📋 Overall Anomaly Summary & Recommendations")
        
        # Create summary cards
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🔍 Data Quality</h4>
                <p>Check for negative stock levels, unusual date patterns, and actual data quality issues</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown("""
            <div class="metric-card">
                <h4>💰 Financial Risks</h4>
                <p>Monitor high-value outliers, price volatility, and unusual spending patterns</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📦 Inventory Issues</h4>
                <p>Track over-stocking, under-stocking, and quantity anomalies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col4:
            st.markdown("""
            <div class="metric-card">
                <h4>🏪 Supplier Concerns</h4>
                <p>Identify supplier consolidation opportunities and relationship risks</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("#### 💡 Recommended Actions:")
        st.markdown("""
        - **🚨 Immediate**: Investigate negative stock levels and weekend transactions
        - **📊 Weekly**: Review high-value transaction outliers and price volatility
        - **📅 Monthly**: Analyze seasonal patterns and supplier performance
        - **🔄 Quarterly**: Assess supplier consolidation opportunities and inventory optimization
        - **📋 Ongoing**: Implement automated alerts for detected anomaly patterns
        """)

    def create_authorization_analysis(self, voucher_df):
        """Create comprehensive authorization analysis with SCOA integration."""
        st.subheader("🔐 Authorization & SCOA Analysis")
        st.markdown("*Analysis of authorization patterns, officials, and SCOA compliance*")
        
        if voucher_df is None or len(voucher_df) == 0:
            st.warning("Voucher data is required for authorization analysis.")
            return
        
        # Create analysis tabs
        auth_tab1, auth_tab2, auth_tab3, auth_tab4 = st.tabs([
            "👤 Authorization Officials",
            "📊 SCOA Analysis", 
            "🏗️ PPE & Electrical Materials",
            "🔍 Authorization Patterns"
        ])
        
        with auth_tab1:
            self.analyze_authorization_officials(voucher_df)
        
        with auth_tab2:
            self.analyze_scoa_structure(voucher_df)
        
        with auth_tab3:
            self.analyze_ppe_electrical_materials(voucher_df)
        
        with auth_tab4:
            self.analyze_authorization_patterns(voucher_df)

    def analyze_authorization_officials(self, voucher_df):
        """Analyze authorization officials and patterns."""
        st.markdown("### 👤 Authorization Officials Analysis")
        
        # Check for authorization columns
        auth_cols = ['official', 'vouch_auth_name', 'vouch_auth_user']
        available_auth_cols = [col for col in auth_cols if col in voucher_df.columns]
        
        if not available_auth_cols:
            st.warning("No authorization columns found in voucher data.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Official analysis
            if 'official' in voucher_df.columns:
                st.markdown("#### 📋 Officials Distribution")
                
                official_stats = voucher_df.groupby('official').agg({
                    'voucher_no': 'count',
                    'cheq_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                official_stats.columns = ['Transaction_Count', 'Total_Amount']
                official_stats = official_stats.sort_values('Total_Amount', ascending=False)
                
                # Display metrics
                st.metric("Unique Officials", voucher_df['official'].nunique())
                st.metric("Total Authorizations", len(voucher_df))
                
                # Top officials chart
                fig = px.bar(
                    x=official_stats.head(10).index,
                    y=official_stats.head(10)['Total_Amount'],
                    title="Top 10 Officials by Authorization Value",
                    labels={'x': 'Official', 'y': 'Total Amount (R)'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="authorization_patterns_overview")
                
                # Show official stats table
                st.markdown("**Top Officials Summary:**")
                display_stats = official_stats.head(10).copy()
                display_stats['Total_Amount'] = display_stats['Total_Amount'].apply(lambda x: f"R{x:,.2f}")
                st.dataframe(display_stats, use_container_width=True)
        
        with col2:
            # Vouch Auth Name analysis
            if 'vouch_auth_name' in voucher_df.columns:
                st.markdown("#### 🔐 Authorization Names Distribution")
                
                auth_name_stats = voucher_df.groupby('vouch_auth_name').agg({
                    'voucher_no': 'count',
                    'cheq_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                auth_name_stats.columns = ['Transaction_Count', 'Total_Amount']
                auth_name_stats = auth_name_stats.sort_values('Total_Amount', ascending=False)
                
                # Display metrics
                st.metric("Unique Auth Names", voucher_df['vouch_auth_name'].nunique())
                
                # Top auth names chart
                fig = px.pie(
                    values=auth_name_stats.head(8)['Transaction_Count'],
                    names=auth_name_stats.head(8).index,
                    title="Top Authorization Names (by Count)",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True, key="authorization_compliance_metrics")
                
                # Show auth name stats table
                st.markdown("**Top Authorization Names:**")
                display_auth = auth_name_stats.head(8).copy()
                display_auth['Total_Amount'] = display_auth['Total_Amount'].apply(lambda x: f"R{x:,.2f}")
                st.dataframe(display_auth, use_container_width=True)
        
        # Cross-reference analysis
        if 'official' in voucher_df.columns and 'vouch_auth_name' in voucher_df.columns:
            st.markdown("### 🔗 Official vs Authorization Name Cross-Reference")
            
            # Create cross-tabulation
            cross_tab = pd.crosstab(voucher_df['official'], voucher_df['vouch_auth_name'], margins=True)
            
            # Show sample of cross-reference
            st.markdown("**Authorization Cross-Reference (Sample):**")
            sample_cross = cross_tab.head(10).iloc[:, :8]  # Show first 10 officials, first 8 auth names
            st.dataframe(sample_cross, use_container_width=True)
            
            # Check for inconsistencies
            unique_combinations = voucher_df.groupby('official')['vouch_auth_name'].nunique()
            multiple_auth_officials = unique_combinations[unique_combinations > 1]
            
            if len(multiple_auth_officials) > 0:
                st.warning(f"⚠️ {len(multiple_auth_officials)} officials have multiple authorization names - potential inconsistency")
                st.dataframe(multiple_auth_officials.head(10), use_container_width=True)

    def analyze_scoa_structure(self, voucher_df):
        """Analyze SCOA (Standard Chart of Accounts) structure and compliance."""
        st.markdown("### 📊 SCOA (Standard Chart of Accounts) Analysis")
        st.info("🇿🇦 **SCOA**: South African public sector Standard Chart of Accounts with vote structure AAAABBBBBBCCCDDDDD")
        
        # Check for vote number column
        vote_col = None
        possible_vote_cols = ['vote_number', 'vote', 'vote_no', 'account', 'account_no']
        
        for col in possible_vote_cols:
            if col in voucher_df.columns:
                vote_col = col
                break
        
        if not vote_col:
            st.warning("No vote number column found. SCOA analysis requires vote number data.")
            return
        
        # Parse vote numbers
        voucher_analysis = voucher_df.copy()
        voucher_analysis['vote_parsed'] = voucher_analysis[vote_col].apply(self.parse_vote_number)
        
        # Extract SCOA components
        voucher_analysis['vote_length'] = voucher_analysis[vote_col].astype(str).str.len()
        voucher_analysis['is_valid_scoa'] = voucher_analysis['vote_length'] >= 18  # SCOA should be 18+ digits
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📏 Vote Number Structure Analysis")
            
            # Vote length distribution
            vote_lengths = voucher_analysis['vote_length'].value_counts().sort_index()
            
            fig = px.bar(
                x=vote_lengths.index,
                y=vote_lengths.values,
                title="Vote Number Length Distribution",
                labels={'x': 'Vote Number Length', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True, key="authorization_trends_timeline")
            
            # SCOA compliance metrics
            scoa_compliant = voucher_analysis['is_valid_scoa'].sum()
            scoa_rate = (scoa_compliant / len(voucher_analysis)) * 100
            
            st.metric("SCOA Compliant Votes", f"{scoa_compliant:,}")
            st.metric("SCOA Compliance Rate", f"{scoa_rate:.1f}%")
            
            if scoa_rate < 90:
                st.warning(f"⚠️ Low SCOA compliance rate: {scoa_rate:.1f}%")
        
        with col2:
            st.markdown("#### 🏛️ SCOA Component Analysis")
            
            # Parse valid SCOA votes
            valid_scoa = voucher_analysis[voucher_analysis['is_valid_scoa']].copy()
            
            if len(valid_scoa) > 0:
                # Extract SCOA components (AAAABBBBBBCCCDDDDD)
                valid_scoa['vote_str'] = valid_scoa[vote_col].astype(str)
                valid_scoa['department'] = valid_scoa['vote_str'].str[:4]      # AAAA - Department
                valid_scoa['programme'] = valid_scoa['vote_str'].str[4:10]     # BBBBBB - Programme  
                valid_scoa['sub_programme'] = valid_scoa['vote_str'].str[10:13] # CCC - Sub-programme
                valid_scoa['economic_class'] = valid_scoa['vote_str'].str[13:18] # DDDDD - Economic classification
                
                # Department analysis
                dept_analysis = valid_scoa.groupby('department').agg({
                    'voucher_no': 'count',
                    'cheq_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                dept_analysis.columns = ['Count', 'Amount']
                dept_analysis = dept_analysis.sort_values('Amount', ascending=False)
                
                st.markdown("**Top Departments by Spending:**")
                display_dept = dept_analysis.head(8).copy()
                display_dept['Amount'] = display_dept['Amount'].apply(lambda x: f"R{x:,.2f}")
                st.dataframe(display_dept, use_container_width=True)
                
                # Economic classification analysis
                econ_analysis = valid_scoa.groupby('economic_class').agg({
                    'voucher_no': 'count',
                    'cheq_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                econ_analysis.columns = ['Count', 'Amount']
                econ_analysis = econ_analysis.sort_values('Amount', ascending=False)
                
                # Show economic classification pie chart
                fig = px.pie(
                    values=econ_analysis.head(6)['Amount'],
                    names=econ_analysis.head(6).index,
                    title="Spending by Economic Classification",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True, key="authorization_inconsistencies")
        
        # SCOA compliance issues
        st.markdown("### 🚨 SCOA Compliance Issues")
        
        non_compliant = voucher_analysis[~voucher_analysis['is_valid_scoa']]
        
        if len(non_compliant) > 0:
            st.error(f"🚨 {len(non_compliant):,} transactions have non-compliant vote numbers")
            
            # Show sample non-compliant votes
            non_compliant_sample = non_compliant.groupby(vote_col).agg({
                'voucher_no': 'count',
                'cheq_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
            }).round(2)
            non_compliant_sample.columns = ['Count', 'Amount']
            non_compliant_sample = non_compliant_sample.sort_values('Amount', ascending=False)
            
            st.markdown("**Non-Compliant Vote Numbers (Top Issues):**")
            display_non_compliant = non_compliant_sample.head(10).copy()
            display_non_compliant['Amount'] = display_non_compliant['Amount'].apply(lambda x: f"R{x:,.2f}")
            st.dataframe(display_non_compliant, use_container_width=True)
        else:
            st.success("✅ All vote numbers are SCOA compliant")

    def parse_vote_number(self, vote):
        """Parse SCOA vote number structure."""
        if pd.isna(vote):
            return None
        
        vote_str = str(vote).strip()
        
        if len(vote_str) >= 18:
            return {
                'department': vote_str[:4],
                'programme': vote_str[4:10],
                'sub_programme': vote_str[10:13],
                'economic_class': vote_str[13:18],
                'full_vote': vote_str
            }
        
        return {'invalid': vote_str}

    def analyze_ppe_electrical_materials(self, voucher_df):
        """Analyze PPE and electrical materials with corrected data relationships."""
        st.markdown("### 🏗️ PPE & Electrical Materials Analysis")
        st.info("🎯 **Focus Area**: Personal Protective Equipment (PPE) and Electrical materials for inconsistency detection")
        
        # Load GRN data for item details
        grn_df = self.load_data('individual_hr995grn.csv')
        
        if grn_df is None:
            st.warning("GRN data required for PPE/Electrical analysis.")
            return
        
        # Use corrected linkage: voucher_no ← GRN voucher ← GRN items
        grn_df['voucher_normalized'] = grn_df['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        voucher_df['voucher_no_normalized'] = voucher_df['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        
        # Join vouchers with GRN items using corrected linkage
        voucher_items = voucher_df.merge(
            grn_df[['voucher_normalized', 'item_no', 'description', 'supplier_name', 'nett_grn_amt']],
            left_on='voucher_no_normalized',
            right_on='voucher_normalized',
            how='inner'
        )
        
        if len(voucher_items) == 0:
            st.warning("No voucher-item linkages found using corrected methodology.")
            return
        
        # PPE identification keywords
        ppe_keywords = [
            'helmet', 'hard hat', 'safety boot', 'safety shoe', 'glove', 'goggle',
            'mask', 'respirator', 'harness', 'vest', 'hi-vis', 'high-vis',
            'protective', 'safety', 'ppe', 'coverall', 'overall'
        ]
        
        # Electrical identification keywords  
        electrical_keywords = [
            'cable', 'wire', 'electrical', 'switch', 'plug', 'socket', 'circuit',
            'breaker', 'fuse', 'transformer', 'conductor', 'insulator', 'voltage',
            'amp', 'watt', 'motor', 'generator', 'battery', 'led', 'light'
        ]
        
        # Categorize items
        voucher_items['description_lower'] = voucher_items['description'].str.lower()
        
        # PPE identification
        ppe_mask = voucher_items['description_lower'].str.contains('|'.join(ppe_keywords), na=False)
        voucher_items['is_ppe'] = ppe_mask
        
        # Electrical identification  
        electrical_mask = voucher_items['description_lower'].str.contains('|'.join(electrical_keywords), na=False)
        voucher_items['is_electrical'] = electrical_mask
        
        # Both categories
        voucher_items['category'] = 'Other'
        voucher_items.loc[voucher_items['is_ppe'], 'category'] = 'PPE'
        voucher_items.loc[voucher_items['is_electrical'], 'category'] = 'Electrical'
        voucher_items.loc[voucher_items['is_ppe'] & voucher_items['is_electrical'], 'category'] = 'PPE & Electrical'
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛡️ PPE Materials Analysis")
            
            ppe_items = voucher_items[voucher_items['is_ppe']]
            
            if len(ppe_items) > 0:
                ppe_value = pd.to_numeric(ppe_items['nett_grn_amt'], errors='coerce').sum()
                ppe_count = len(ppe_items)
                ppe_suppliers = ppe_items['supplier_name'].nunique()
                
                st.metric("PPE Transactions", f"{ppe_count:,}")
                st.metric("PPE Value", f"R{ppe_value:,.2f}")
                st.metric("PPE Suppliers", f"{ppe_suppliers:,}")
                
                # Top PPE suppliers
                ppe_supplier_analysis = ppe_items.groupby('supplier_name').agg({
                    'voucher_no': 'count',
                    'nett_grn_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                ppe_supplier_analysis.columns = ['Transactions', 'Total_Value']
                ppe_supplier_analysis = ppe_supplier_analysis.sort_values('Total_Value', ascending=False)
                
                fig = px.bar(
                    x=ppe_supplier_analysis.head(8).index,
                    y=ppe_supplier_analysis.head(8)['Total_Value'],
                    title="Top PPE Suppliers by Value",
                    labels={'x': 'Supplier', 'y': 'Total Value (R)'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="scoa_structure_compliance")
                
                # PPE inconsistency checks
                st.markdown("**PPE Inconsistency Checks:**")
                
                # Check for PPE price variations
                ppe_price_analysis = ppe_items.groupby(['item_no', 'description']).agg({
                    'nett_grn_amt': ['count', 'mean', 'std', 'min', 'max']
                }).round(2)
                ppe_price_analysis.columns = ['Count', 'Mean_Price', 'Std_Price', 'Min_Price', 'Max_Price']
                ppe_price_analysis['CV'] = (ppe_price_analysis['Std_Price'] / ppe_price_analysis['Mean_Price']) * 100
                
                high_variation_ppe = ppe_price_analysis[
                    (ppe_price_analysis['Count'] >= 3) & 
                    (ppe_price_analysis['CV'] > 30)
                ].sort_values('CV', ascending=False)
                
                if len(high_variation_ppe) > 0:
                    st.warning(f"⚠️ {len(high_variation_ppe)} PPE items show high price variation (>30% CV)")
                    st.dataframe(high_variation_ppe.head(5), use_container_width=True)
                else:
                    st.success("✅ PPE pricing appears consistent")
            else:
                st.info("No PPE items identified in the data.")
        
        with col2:
            st.markdown("#### ⚡ Electrical Materials Analysis")
            
            electrical_items = voucher_items[voucher_items['is_electrical']]
            
            if len(electrical_items) > 0:
                electrical_value = pd.to_numeric(electrical_items['nett_grn_amt'], errors='coerce').sum()
                electrical_count = len(electrical_items)
                electrical_suppliers = electrical_items['supplier_name'].nunique()
                
                st.metric("Electrical Transactions", f"{electrical_count:,}")
                st.metric("Electrical Value", f"R{electrical_value:,.2f}")
                st.metric("Electrical Suppliers", f"{electrical_suppliers:,}")
                
                # Top electrical suppliers
                elec_supplier_analysis = electrical_items.groupby('supplier_name').agg({
                    'voucher_no': 'count',
                    'nett_grn_amt': lambda x: pd.to_numeric(x, errors='coerce').sum()
                }).round(2)
                elec_supplier_analysis.columns = ['Transactions', 'Total_Value']
                elec_supplier_analysis = elec_supplier_analysis.sort_values('Total_Value', ascending=False)
                
                fig = px.pie(
                    values=elec_supplier_analysis.head(6)['Total_Value'],
                    names=elec_supplier_analysis.head(6).index,
                    title="Top Electrical Suppliers by Value",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True, key="vote_structure_breakdown")
                
                # Electrical inconsistency checks
                st.markdown("**Electrical Inconsistency Checks:**")
                
                # Check for electrical supplier concentration
                elec_total_value = elec_supplier_analysis['Total_Value'].sum()
                top_supplier_value = elec_supplier_analysis.iloc[0]['Total_Value'] if len(elec_supplier_analysis) > 0 else 0
                concentration_ratio = (top_supplier_value / elec_total_value * 100) if elec_total_value > 0 else 0
                
                if concentration_ratio > 70:
                    st.warning(f"⚠️ High supplier concentration: Top supplier has {concentration_ratio:.1f}% of electrical spending")
                else:
                    st.success(f"✅ Supplier concentration acceptable: {concentration_ratio:.1f}%")
                
                # Check for electrical item frequency
                elec_item_freq = electrical_items['item_no'].value_counts()
                high_freq_items = elec_item_freq[elec_item_freq > 10]
                
                if len(high_freq_items) > 0:
                    st.info(f"📊 {len(high_freq_items)} electrical items appear frequently (>10 transactions)")
                    st.dataframe(high_freq_items.head(5), use_container_width=True)
            else:
                st.info("No electrical items identified in the data.")
        
        # Combined analysis
        st.markdown("### 🔍 Combined PPE & Electrical Insights")
        
        category_summary = voucher_items.groupby('category').agg({
            'voucher_no': 'count',
            'nett_grn_amt': lambda x: pd.to_numeric(x, errors='coerce').sum(),
            'supplier_name': 'nunique'
        }).round(2)
        category_summary.columns = ['Transactions', 'Total_Value', 'Unique_Suppliers']
        
        # Category breakdown chart
        fig = px.bar(
            x=category_summary.index,
            y=category_summary['Total_Value'],
            title="Spending by Material Category",
            labels={'x': 'Category', 'y': 'Total Value (R)'}
        )
        st.plotly_chart(fig, use_container_width=True, key="scoa_validation_summary")
        
        # Summary table
        st.markdown("**Category Summary:**")
        display_summary = category_summary.copy()
        display_summary['Total_Value'] = display_summary['Total_Value'].apply(lambda x: f"R{x:,.2f}")
        st.dataframe(display_summary, use_container_width=True)

    def analyze_authorization_patterns(self, voucher_df):
        """Analyze authorization patterns and identify potential inconsistencies."""
        st.markdown("### 🔍 Authorization Pattern Analysis")
        st.info("🎯 **Focus**: Identifying inconsistencies in authorization patterns, officials, and approval workflows")
        
        if 'official' not in voucher_df.columns or 'vouch_auth_name' not in voucher_df.columns:
            st.warning("Authorization analysis requires 'official' and 'vouch_auth_name' columns.")
            return
        
        # Prepare data for analysis
        auth_analysis = voucher_df.copy()
        auth_analysis['cheq_amt_numeric'] = pd.to_numeric(auth_analysis['cheq_amt'], errors='coerce')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Authorization by Amount Ranges")
            
            # Define amount ranges for authorization analysis
            amount_ranges = [
                (0, 1000, "R0 - R1,000"),
                (1000, 10000, "R1,000 - R10,000"),
                (10000, 50000, "R10,000 - R50,000"),
                (50000, 100000, "R50,000 - R100,000"),
                (100000, 500000, "R100,000 - R500,000"),
                (500000, float('inf'), "R500,000+")
            ]
            
            # Categorize by amount ranges
            auth_analysis['amount_range'] = 'Unknown'
            for min_amt, max_amt, label in amount_ranges:
                mask = (auth_analysis['cheq_amt_numeric'] >= min_amt) & (auth_analysis['cheq_amt_numeric'] < max_amt)
                auth_analysis.loc[mask, 'amount_range'] = label
            
            # Authorization by amount range
            range_auth = auth_analysis.groupby(['amount_range', 'official']).size().reset_index(name='count')
            range_summary = auth_analysis.groupby('amount_range').agg({
                'voucher_no': 'count',
                'official': 'nunique',
                'cheq_amt_numeric': 'sum'
            }).round(2)
            range_summary.columns = ['Transactions', 'Unique_Officials', 'Total_Amount']
            
            fig = px.bar(
                x=range_summary.index,
                y=range_summary['Unique_Officials'],
                title="Officials by Authorization Amount Range",
                labels={'x': 'Amount Range', 'y': 'Number of Officials'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True, key="ppe_category_distribution")
            
            st.markdown("**Authorization Range Summary:**")
            display_range = range_summary.copy()
            display_range['Total_Amount'] = display_range['Total_Amount'].apply(lambda x: f"R{x:,.2f}")
            st.dataframe(display_range, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Official Authorization Frequency")
            
            # Official frequency analysis
            official_freq = auth_analysis.groupby('official').agg({
                'voucher_no': 'count',
                'cheq_amt_numeric': ['sum', 'mean', 'std']
            }).round(2)
            official_freq.columns = ['Transaction_Count', 'Total_Amount', 'Mean_Amount', 'Std_Amount']
            official_freq['CV'] = (official_freq['Std_Amount'] / official_freq['Mean_Amount']) * 100
            official_freq = official_freq.sort_values('Transaction_Count', ascending=False)
            
            # High-frequency officials
            high_freq_threshold = official_freq['Transaction_Count'].quantile(0.8)
            high_freq_officials = official_freq[official_freq['Transaction_Count'] > high_freq_threshold]
            
            fig = px.scatter(
                official_freq,
                x='Transaction_Count',
                y='Mean_Amount',
                hover_name=official_freq.index,
                title="Official Authorization Patterns",
                labels={'Transaction_Count': 'Transaction Count', 'Mean_Amount': 'Mean Authorization Amount (R)'},
                size='Total_Amount',
                color='CV'
            )
            st.plotly_chart(fig, use_container_width=True, key="electrical_materials_breakdown")
            
            if len(high_freq_officials) > 0:
                st.warning(f"⚠️ {len(high_freq_officials)} officials have high authorization frequency")
                st.dataframe(high_freq_officials.head(5), use_container_width=True)
        
        # Inconsistency detection
        st.markdown("### 🚨 Authorization Inconsistency Detection")
        
        inconsistency_findings = []
        
        # 1. Officials with highly variable authorization amounts
        variable_officials = official_freq[official_freq['CV'] > 200]  # CV > 200%
        if len(variable_officials) > 0:
            inconsistency_findings.append({
                'Type': 'High Amount Variability',
                'Count': len(variable_officials),
                'Description': f'{len(variable_officials)} officials show high variability in authorization amounts (CV > 200%)',
                'Severity': 'Medium'
            })
        
        # 2. Multiple authorization names per official
        official_auth_names = auth_analysis.groupby('official')['vouch_auth_name'].nunique()
        multiple_auth_officials = official_auth_names[official_auth_names > 1]
        if len(multiple_auth_officials) > 0:
            inconsistency_findings.append({
                'Type': 'Multiple Auth Names',
                'Count': len(multiple_auth_officials),
                'Description': f'{len(multiple_auth_officials)} officials have multiple authorization names',
                'Severity': 'High'
            })
        
        # 3. Unusual authorization patterns by date
        if 'date' in auth_analysis.columns:
            auth_analysis['date_parsed'] = pd.to_datetime(auth_analysis['date'], errors='coerce')
            auth_analysis['hour'] = auth_analysis['date_parsed'].dt.hour
            auth_analysis['day_of_week'] = auth_analysis['date_parsed'].dt.dayofweek
            
            # Weekend authorizations
            weekend_auths = auth_analysis[auth_analysis['day_of_week'] >= 5]
            if len(weekend_auths) > 0:
                inconsistency_findings.append({
                    'Type': 'Weekend Authorizations',
                    'Count': len(weekend_auths),
                    'Description': f'{len(weekend_auths)} authorizations occurred on weekends',
                    'Severity': 'Low'
                })
        
        # 4. High-value single authorizations
        high_value_threshold = auth_analysis['cheq_amt_numeric'].quantile(0.95)
        high_value_auths = auth_analysis[auth_analysis['cheq_amt_numeric'] > high_value_threshold]
        if len(high_value_auths) > 0:
            inconsistency_findings.append({
                'Type': 'High-Value Authorizations',
                'Count': len(high_value_auths),
                'Description': f'{len(high_value_auths)} authorizations exceed 95th percentile (R{high_value_threshold:,.2f})',
                'Severity': 'Medium'
            })
        
        # Display inconsistency findings
        if inconsistency_findings:
            findings_df = pd.DataFrame(inconsistency_findings)
            
            # Color code by severity
            def highlight_severity(row):
                if row['Severity'] == 'High':
                    return ['background-color: #ffebee'] * len(row)
                elif row['Severity'] == 'Medium':
                    return ['background-color: #fff3e0'] * len(row)
                else:
                    return ['background-color: #e8f5e8'] * len(row)
            
            styled_findings = findings_df.style.apply(highlight_severity, axis=1)
            st.dataframe(styled_findings, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No major authorization inconsistencies detected")
        
        # Recommendations
        st.markdown("### 💡 Authorization Recommendations")
        
        recommendations = [
            "🔍 **Review High Variability**: Investigate officials with high authorization amount variability",
            "📊 **Standardize Auth Names**: Ensure consistent authorization naming conventions",
            "⏰ **Monitor Weekend Activity**: Review weekend authorizations for policy compliance",
            "💰 **High-Value Controls**: Implement additional controls for high-value authorizations",
            "📋 **Regular Audits**: Conduct monthly authorization pattern reviews",
            "🔐 **Access Controls**: Review authorization limits and delegation of authority"
        ]
        
        for rec in recommendations:
            st.markdown(f"- {rec}")

    def create_grn_transaction_analysis(self, grn_df, voucher_df):
        """Comprehensive GRN vs Transaction analysis with corrected PDF linkage."""
        st.subheader("🔗 GRN-Transaction Analysis (Corrected)")
        st.markdown("*Using corrected PDF → GRN → Voucher linkage methodology*")
        
        if len(grn_df) == 0 or len(voucher_df) == 0:
            st.warning("Both GRN and voucher data are required for this analysis.")
            return
        
        # Create analysis tabs
        grn_tab1, grn_tab2, grn_tab3, grn_tab4 = st.tabs([
            "🔍 Payment Status Analysis",
            "💳 Multiple Payment Detection", 
            "🔗 Supplier Linking Issues",
            "📊 Summary Dashboard"
        ])
        
        with grn_tab1:
            self.analyze_payment_status(grn_df, voucher_df)
        
        with grn_tab2:
            self.analyze_multiple_payments(grn_df, voucher_df)
        
        with grn_tab3:
            self.analyze_supplier_linking(grn_df, voucher_df)
        
        with grn_tab4:
            self.create_grn_transaction_summary(grn_df, voucher_df)

    def analyze_payment_status(self, grn_df, voucher_df):
        """Analyze payment status with corrected PDF linkage logic."""
        st.markdown("### � Payment Status Analysis (Corrected)")
        st.info("✅ **Using Corrected Linkage**: PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
        
        # Load PDF data if available
        pdf_df = None
        if os.path.exists('output/individual_hr185_transactions.csv'):
            pdf_df = pd.read_csv('output/individual_hr185_transactions.csv')
            pdf_df['reference_normalized'] = pdf_df['reference'].apply(self.normalize_reference)
        
        # Normalize data
        grn_analysis = grn_df.copy()
        grn_analysis['voucher_normalized'] = grn_analysis['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(self.normalize_reference)
        
        voucher_analysis = voucher_df.copy()
        voucher_analysis['voucher_no_normalized'] = voucher_analysis['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        
        # Find payment status for each GRN
        grn_voucher_refs = set(grn_analysis['voucher_normalized'].dropna())
        actual_vouchers = set(voucher_analysis['voucher_no_normalized'].dropna())
        
        # Categorize GRNs
        paid_grns = grn_analysis[grn_analysis['voucher_normalized'].isin(actual_vouchers)]
        unpaid_grns = grn_analysis[~grn_analysis['voucher_normalized'].isin(actual_vouchers)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Paid GRNs", f"{len(paid_grns):,}")
            paid_value = pd.to_numeric(paid_grns['nett_grn_amt'], errors='coerce').sum()
            st.metric("💰 Paid Value", f"R{paid_value:,.2f}")
        
        with col2:
            st.metric("❌ Unpaid GRNs", f"{len(unpaid_grns):,}")
            unpaid_value = pd.to_numeric(unpaid_grns['nett_grn_amt'], errors='coerce').sum()
            st.metric("💸 Unpaid Value", f"R{unpaid_value:,.2f}")
        
        with col3:
            total_grns = len(grn_analysis)
            payment_rate = len(paid_grns) / total_grns * 100 if total_grns > 0 else 0
            st.metric("📈 Payment Rate", f"{payment_rate:.1f}%")
        
        # PDF linkage breakdown for unpaid GRNs
        if pdf_df is not None:
            st.markdown("### 📄 Unpaid GRNs by PDF Linkage")
            
            unpaid_pdf_linked = unpaid_grns[unpaid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
            unpaid_non_pdf = unpaid_grns[~unpaid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📄 Unpaid (PDF-Linked)", f"{len(unpaid_pdf_linked):,}")
                unpaid_pdf_value = pd.to_numeric(unpaid_pdf_linked['nett_grn_amt'], errors='coerce').sum()
                st.metric("💰 Value (PDF-Linked)", f"R{unpaid_pdf_value:,.2f}")
            
            with col2:
                st.metric("📋 Unpaid (Non-PDF)", f"{len(unpaid_non_pdf):,}")
                unpaid_non_pdf_value = pd.to_numeric(unpaid_non_pdf['nett_grn_amt'], errors='coerce').sum()
                st.metric("💰 Value (Non-PDF)", f"R{unpaid_non_pdf_value:,.2f}")
            
            # Visualization
            if len(unpaid_grns) > 0:
                unpaid_breakdown = pd.DataFrame({
                    'Category': ['PDF-Linked Unpaid', 'Non-PDF Unpaid'],
                    'Count': [len(unpaid_pdf_linked), len(unpaid_non_pdf)],
                    'Value': [unpaid_pdf_value, unpaid_non_pdf_value]
                })
                
                fig = px.bar(unpaid_breakdown, x='Category', y='Value',
                            title="Unpaid GRN Value by PDF Linkage",
                            color='Category',
                            color_discrete_map={'PDF-Linked Unpaid': '#ff7f7f', 'Non-PDF Unpaid': '#ffb366'})
                st.plotly_chart(fig, use_container_width=True, key="ppe_electrical_trends")
        
        # Payment timing analysis
        st.markdown("### ⏰ Payment Timing Analysis")
        
        if 'date' in grn_analysis.columns and 'date' in voucher_analysis.columns:
            try:
                # Convert dates
                grn_analysis['grn_date'] = pd.to_datetime(grn_analysis['date'], errors='coerce')
                voucher_analysis['voucher_date'] = pd.to_datetime(voucher_analysis['date'], errors='coerce')
                
                # Join GRNs with their payments
                paid_with_timing = grn_analysis[grn_analysis['voucher_normalized'].isin(actual_vouchers)].merge(
                    voucher_analysis[['voucher_no_normalized', 'voucher_date']], 
                    left_on='voucher_normalized', right_on='voucher_no_normalized', 
                    how='left'
                )
                
                # Calculate payment delays
                paid_with_timing['payment_delay'] = (paid_with_timing['voucher_date'] - paid_with_timing['grn_date']).dt.days
                
                # Summary statistics
                if len(paid_with_timing) > 0:
                    avg_delay = paid_with_timing['payment_delay'].mean()
                    median_delay = paid_with_timing['payment_delay'].median()
                    max_delay = paid_with_timing['payment_delay'].max()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Average Delay", f"{avg_delay:.1f} days")
                    
                    with col2:
                        st.metric("📊 Median Delay", f"{median_delay:.1f} days")
                    
                    with col3:
                        st.metric("📊 Max Delay", f"{max_delay:.0f} days")
                    
                    # Payment delay distribution
                    delay_ranges = ['0-30 days', '31-60 days', '61-90 days', '91+ days']
                    delay_counts = [
                        len(paid_with_timing[paid_with_timing['payment_delay'] <= 30]),
                        len(paid_with_timing[(paid_with_timing['payment_delay'] > 30) & (paid_with_timing['payment_delay'] <= 60)]),
                        len(paid_with_timing[(paid_with_timing['payment_delay'] > 60) & (paid_with_timing['payment_delay'] <= 90)]),
                        len(paid_with_timing[paid_with_timing['payment_delay'] > 90])
                    ]
                    
                    delay_df = pd.DataFrame({
                        'Range': delay_ranges,
                        'Count': delay_counts
                    })
                    
                    fig = px.bar(delay_df, x='Range', y='Count',
                                title="Payment Delay Distribution",
                                color='Range')
                    st.plotly_chart(fig, use_container_width=True, key="supplier_ppe_specialization")
                    
            except Exception as e:
                st.warning(f"Could not analyze payment timing: {str(e)}")
        
        # Action items
        st.markdown("### 🎯 Action Items")
        
        action_items = []
        
        if len(unpaid_grns) > 0:
            unpaid_pct = len(unpaid_grns) / len(grn_analysis) * 100
            if unpaid_pct > 10:
                action_items.append(f"🚨 **High Unpaid Rate**: {unpaid_pct:.1f}% of GRNs are unpaid - Review payment processes")
        
        if pdf_df is not None and len(unpaid_pdf_linked) > 0:
            action_items.append(f"📄 **PDF-Linked Unpaid**: {len(unpaid_pdf_linked)} PDF-documented GRNs remain unpaid")
        
        if len(unpaid_non_pdf) > 0:
            action_items.append(f"📋 **Non-PDF Unpaid**: {len(unpaid_non_pdf)} GRNs without PDF documentation remain unpaid")
        
        if not action_items:
            st.success("✅ No major payment issues detected")
        else:
            for item in action_items:
                st.markdown(f"- {item}")

    def analyze_multiple_payments(self, grn_df, voucher_df):
        """Detect multiple payments with corrected PDF linkage context."""
        st.markdown("### 💳 Multiple Payment Detection (Corrected)")
        st.info("✅ **Using Corrected Linkage**: PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
        
        # Load PDF data if available
        pdf_df = None
        if os.path.exists('output/individual_hr185_transactions.csv'):
            pdf_df = pd.read_csv('output/individual_hr185_transactions.csv')
            pdf_df['reference_normalized'] = pdf_df['reference'].apply(self.normalize_reference)
        
        # Normalize data
        grn_analysis = grn_df.copy()
        grn_analysis['voucher_normalized'] = grn_analysis['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(self.normalize_reference)
        
        voucher_analysis = voucher_df.copy()
        voucher_analysis['voucher_no_normalized'] = voucher_analysis['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        voucher_analysis['cheq_amt_num'] = pd.to_numeric(voucher_analysis['cheq_amt'], errors='coerce')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Duplicate Payment Analysis")
            
            # Method 1: Multiple payments to same voucher reference
            voucher_counts = voucher_analysis['voucher_no_normalized'].value_counts()
            duplicate_vouchers = voucher_counts[voucher_counts > 1]
            
            if len(duplicate_vouchers) > 0:
                st.metric("Voucher Numbers with Multiple Payments", len(duplicate_vouchers))
                
                # Calculate potential overpayment
                duplicate_details = []
                total_overpayment = 0
                
                for voucher_no, count in duplicate_vouchers.head(10).items():
                    voucher_payments = voucher_analysis[voucher_analysis['voucher_no_normalized'] == voucher_no]
                    total_paid = voucher_payments['cheq_amt_num'].sum()
                    expected_payment = voucher_payments['cheq_amt_num'].iloc[0]  # Assume first payment is correct
                    overpayment = total_paid - expected_payment
                    total_overpayment += overpayment
                    
                    duplicate_details.append({
                        'Voucher No': voucher_no,
                        'Payment Count': count,
                        'Total Paid': f"R{total_paid:,.2f}",
                        'Expected': f"R{expected_payment:,.2f}",
                        'Overpayment': f"R{overpayment:,.2f}"
                    })
                
                st.metric("Potential Overpayment (Top 10)", f"R{total_overpayment:,.2f}")
                
                # Show duplicate details
                if duplicate_details:
                    st.markdown("**Duplicate Voucher Payments:**")
                    st.dataframe(pd.DataFrame(duplicate_details), use_container_width=True, hide_index=True)
            else:
                st.success("✅ No duplicate voucher payments detected")
            
            # Method 2: Same supplier, same amount, same date
            st.markdown("#### 📅 Same-Day Duplicate Analysis")
            
            if 'date' in voucher_analysis.columns:
                voucher_analysis['date_parsed'] = pd.to_datetime(voucher_analysis['date'], errors='coerce')
                
                # Group by supplier, amount, and date
                same_day_groups = voucher_analysis.groupby([
                    'payee_name', 'cheq_amt_num', 'date_parsed'
                ]).agg({
                    'voucher_no_normalized': 'count',
                    'cheq_amt': 'first'
                }).reset_index()
                
                same_day_groups.columns = ['Supplier', 'Amount', 'Date', 'Payment Count', 'Amount Display']
                suspicious_same_day = same_day_groups[same_day_groups['Payment Count'] > 1]
                
                if len(suspicious_same_day) > 0:
                    st.metric("Suspicious Same-Day Payments", len(suspicious_same_day))
                    
                    # Calculate potential duplicate value
                    suspicious_value = suspicious_same_day['Amount'].sum()
                    st.metric("Potential Duplicate Value", f"R{suspicious_value:,.2f}")
                    
                    # Show details
                    display_suspicious = suspicious_same_day.copy()
                    display_suspicious['Amount Display'] = display_suspicious['Amount'].apply(lambda x: f"R{x:,.2f}")
                    st.dataframe(
                        display_suspicious[['Supplier', 'Amount Display', 'Date', 'Payment Count']].head(10),
                        use_container_width=True, hide_index=True
                    )
                else:
                    st.success("✅ No suspicious same-day payments detected")
        
        with col2:
            st.markdown("#### 📊 Payment Pattern Analysis")
            
            # Link with PDF data for enhanced analysis
            if pdf_df is not None:
                # Find payments linked to PDF transactions
                pdf_linked_grns = grn_analysis[grn_analysis['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
                pdf_linked_vouchers = pdf_linked_grns['voucher_normalized'].dropna()
                
                pdf_payments = voucher_analysis[voucher_analysis['voucher_no_normalized'].isin(pdf_linked_vouchers)]
                non_pdf_payments = voucher_analysis[~voucher_analysis['voucher_no_normalized'].isin(pdf_linked_vouchers)]
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("📄 PDF-Linked Payments", len(pdf_payments))
                    pdf_payment_value = pdf_payments['cheq_amt_num'].sum()
                    st.metric("💰 PDF-Linked Value", f"R{pdf_payment_value:,.2f}")
                
                with col_b:
                    st.metric("📋 Non-PDF Payments", len(non_pdf_payments))
                    non_pdf_payment_value = non_pdf_payments['cheq_amt_num'].sum()
                    st.metric("💰 Non-PDF Value", f"R{non_pdf_payment_value:,.2f}")
                
                # Visualization of payment distribution
                payment_breakdown = pd.DataFrame({
                    'Type': ['PDF-Linked Payments', 'Non-PDF Payments'],
                    'Count': [len(pdf_payments), len(non_pdf_payments)],
                    'Value': [pdf_payment_value, non_pdf_payment_value]
                })
                
                fig = px.pie(payment_breakdown, values='Value', names='Type',
                            title="Payment Value Distribution by PDF Linkage")
                st.plotly_chart(fig, use_container_width=True, key="materials_seasonal_patterns")
            
            # Supplier payment frequency analysis
            st.markdown("#### 🏢 Supplier Payment Frequency")
            
            supplier_freq = voucher_analysis.groupby('payee_name').agg({
                'cheq_amt_num': ['count', 'sum', 'mean'],
                'voucher_no_normalized': 'nunique'
            }).reset_index()
            
            supplier_freq.columns = ['Supplier', 'Payment Count', 'Total Value', 'Avg Payment', 'Unique Vouchers']
            
            # Find suppliers with high payment frequency
            high_freq_threshold = supplier_freq['Payment Count'].quantile(0.9)
            high_freq_suppliers = supplier_freq[supplier_freq['Payment Count'] > high_freq_threshold]
            
            if len(high_freq_suppliers) > 0:
                st.metric("High-Frequency Suppliers", len(high_freq_suppliers))
                
                # Show top high-frequency suppliers
                st.markdown("**High-Frequency Payment Suppliers:**")
                display_suppliers = high_freq_suppliers.copy()
                display_suppliers['Total Value'] = display_suppliers['Total Value'].apply(lambda x: f"R{x:,.2f}")
                display_suppliers['Avg Payment'] = display_suppliers['Avg Payment'].apply(lambda x: f"R{x:,.2f}")
                
                st.dataframe(
                    display_suppliers.head(10),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("No unusually high-frequency payment suppliers detected")
        
        # Risk assessment
        st.markdown("### 🚨 Multiple Payment Risk Assessment")
        
        risk_items = []
        
        if len(duplicate_vouchers) > 0:
            risk_items.append(f"🔴 **Duplicate Voucher Payments**: {len(duplicate_vouchers)} voucher numbers have multiple payments")
        
        if 'suspicious_same_day' in locals() and len(suspicious_same_day) > 0:
            risk_items.append(f"🟡 **Same-Day Duplicates**: {len(suspicious_same_day)} potential same-day duplicate payments")
        
        if pdf_df is not None:
            pdf_payment_rate = len(pdf_payments) / len(voucher_analysis) * 100 if len(voucher_analysis) > 0 else 0
            if pdf_payment_rate < 50:
                risk_items.append(f"🟡 **Low PDF Coverage**: Only {pdf_payment_rate:.1f}% of payments are linked to PDF documents")
        
        if risk_items:
            for item in risk_items:
                st.markdown(f"- {item}")
        else:
            st.success("✅ No major multiple payment risks detected")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        recommendations = [
            "🔍 **Review Duplicate Vouchers**: Investigate voucher numbers with multiple payments",
            "📅 **Monitor Same-Day Payments**: Review payments made on same day to same supplier",
            "📊 **Enhance Controls**: Implement automated duplicate payment detection",
            "🔗 **Improve Traceability**: Ensure all payments are properly linked to source documents"
        ]
        
        if pdf_df is not None:
            recommendations.append("📄 **PDF Documentation**: Improve PDF documentation coverage for all transactions")
        
        for rec in recommendations:
            st.markdown(f"- {rec}")

    def analyze_supplier_linking(self, grn_df, voucher_df):
        """Analyze supplier linking with corrected PDF linkage context."""
        st.markdown("### 🔗 Supplier Linking Analysis (Corrected)")
        st.info("✅ **Using Corrected Linkage**: PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
        
        # Load PDF data if available
        pdf_df = None
        if os.path.exists('output/individual_hr185_transactions.csv'):
            pdf_df = pd.read_csv('output/individual_hr185_transactions.csv')
            pdf_df['reference_normalized'] = pdf_df['reference'].apply(self.normalize_reference)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Cross-Reference Analysis")
            
            # Get supplier lists from both datasets
            grn_supplier_col = 'supplier_name'
            voucher_supplier_col = 'payee_name'
            
            # Clean and normalize supplier names
            grn_suppliers = set(grn_df[grn_supplier_col].dropna().astype(str).str.strip().str.upper())
            voucher_suppliers = set(voucher_df[voucher_supplier_col].dropna().astype(str).str.strip().str.upper())
            
            # Find mismatches
            grn_only = grn_suppliers - voucher_suppliers
            voucher_only = voucher_suppliers - grn_suppliers
            common_suppliers = grn_suppliers & voucher_suppliers
            
            st.metric("Common Suppliers", len(common_suppliers))
            st.metric("GRN-Only Suppliers", len(grn_only))
            st.metric("Payment-Only Suppliers", len(voucher_only))
            
            # Calculate coverage
            if len(grn_suppliers) > 0:
                coverage_rate = len(common_suppliers) / len(grn_suppliers) * 100
                st.metric("GRN Supplier Coverage", f"{coverage_rate:.1f}%")
            
            # PDF linkage supplier analysis
            if pdf_df is not None:
                st.markdown("#### 📄 PDF-Linked Supplier Analysis")
                
                # Get suppliers from PDF-linked GRNs
                grn_df_analysis = grn_df.copy()
                grn_df_analysis['inv_no_normalized'] = grn_df_analysis['inv_no'].apply(self.normalize_reference)
                
                pdf_linked_grns = grn_df_analysis[grn_df_analysis['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
                pdf_linked_suppliers = set(pdf_linked_grns[grn_supplier_col].dropna().astype(str).str.strip().str.upper())
                
                # Compare PDF-linked suppliers with payment suppliers
                pdf_payment_overlap = pdf_linked_suppliers & voucher_suppliers
                pdf_only_suppliers = pdf_linked_suppliers - voucher_suppliers
                
                st.metric("PDF-Linked Suppliers", len(pdf_linked_suppliers))
                st.metric("PDF → Payment Overlap", len(pdf_payment_overlap))
                st.metric("PDF-Only (No Payments)", len(pdf_only_suppliers))
                
                if len(pdf_linked_suppliers) > 0:
                    pdf_coverage = len(pdf_payment_overlap) / len(pdf_linked_suppliers) * 100
                    st.metric("PDF Supplier Payment Rate", f"{pdf_coverage:.1f}%")
            
            # Show unmatched suppliers (limited sample)
            if len(grn_only) > 0:
                st.markdown("**Sample GRN-Only Suppliers:**")
                grn_only_sample = pd.DataFrame(list(grn_only)[:5], columns=['Supplier'])
                st.dataframe(grn_only_sample, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 🎯 Data Quality Analysis")
            
            # Voucher reference integrity check with corrected logic
            st.markdown("#### 🔗 Voucher Reference Integrity")
            
            if 'voucher' in grn_df.columns and 'voucher_no' in voucher_df.columns:
                # Use corrected linkage
                grn_analysis = grn_df.copy()
                grn_analysis['voucher_normalized'] = grn_analysis['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
                grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(self.normalize_reference)
                
                voucher_analysis = voucher_df.copy()
                voucher_analysis['voucher_no_normalized'] = voucher_analysis['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
                
                grn_voucher_refs = set(grn_analysis['voucher_normalized'].dropna())
                actual_vouchers = set(voucher_analysis['voucher_no_normalized'].dropna())
                
                valid_refs = grn_voucher_refs & actual_vouchers
                invalid_refs = grn_voucher_refs - actual_vouchers
                
                st.metric("Valid Voucher References", len(valid_refs))
                st.metric("Invalid Voucher References", len(invalid_refs))
                
                if len(grn_voucher_refs) > 0:
                    validity_rate = len(valid_refs) / len(grn_voucher_refs) * 100
                    st.metric("Reference Validity Rate", f"{validity_rate:.1f}%")
                
                # Break down invalid references by PDF linkage
                if pdf_df is not None and len(invalid_refs) > 0:
                    invalid_grns = grn_analysis[grn_analysis['voucher_normalized'].isin(invalid_refs)]
                    invalid_pdf_linked = invalid_grns[invalid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
                    invalid_non_pdf = invalid_grns[~invalid_grns['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
                    
                    st.markdown("**Invalid Reference Breakdown:**")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("📄 Invalid (PDF-Linked)", len(invalid_pdf_linked))
                        if len(invalid_pdf_linked) > 0:
                            invalid_pdf_value = pd.to_numeric(invalid_pdf_linked['nett_grn_amt'], errors='coerce').sum()
                            st.metric("💰 PDF Invalid Value", f"R{invalid_pdf_value:,.2f}")
                    
                    with col_b:
                        st.metric("📋 Invalid (Non-PDF)", len(invalid_non_pdf))
                        if len(invalid_non_pdf) > 0:
                            invalid_non_pdf_value = pd.to_numeric(invalid_non_pdf['nett_grn_amt'], errors='coerce').sum()
                            st.metric("� Non-PDF Invalid Value", f"R{invalid_non_pdf_value:,.2f}")
                
                if len(invalid_refs) > 0:
                    # Show value impact of invalid references
                    invalid_grns = grn_analysis[grn_analysis['voucher_normalized'].isin(invalid_refs)]
                    invalid_value = pd.to_numeric(invalid_grns['nett_grn_amt'], errors='coerce').sum()
                    st.metric("Total Invalid Reference Value", f"R{invalid_value:,.2f}")
                else:
                    st.success("✅ All voucher references are valid")
            
            # Supplier name quality analysis
            st.markdown("#### 🔤 Supplier Name Quality")
            
            # Check for potential supplier name variations
            grn_supplier_lengths = grn_df[grn_supplier_col].str.len()
            voucher_supplier_lengths = voucher_df[voucher_supplier_col].str.len()
            
            avg_grn_name_length = grn_supplier_lengths.mean()
            avg_voucher_name_length = voucher_supplier_lengths.mean()
            
            st.metric("Avg GRN Supplier Name Length", f"{avg_grn_name_length:.1f}")
            st.metric("Avg Payment Supplier Name Length", f"{avg_voucher_name_length:.1f}")
            
            # Check for suppliers with very short or very long names (potential data quality issues)
            short_names_grn = len(grn_df[grn_supplier_lengths < 5])
            long_names_grn = len(grn_df[grn_supplier_lengths > 50])
            
            if short_names_grn > 0 or long_names_grn > 0:
                st.markdown("**Potential Name Quality Issues:**")
                if short_names_grn > 0:
                    st.metric("Very Short Names (GRN)", short_names_grn)
                if long_names_grn > 0:
                    st.metric("Very Long Names (GRN)", long_names_grn)
        
        # Recommendations
        st.markdown("### 💡 Supplier Linking Recommendations")
        
        recommendations = []
        
        if len(grn_only) > 0:
            recommendations.append(f"🔍 **Review GRN-Only Suppliers**: {len(grn_only)} suppliers have GRNs but no payments")
        
        if len(voucher_only) > 0:
            recommendations.append(f"💳 **Review Payment-Only Suppliers**: {len(voucher_only)} suppliers have payments but no GRNs")
        
        if pdf_df is not None and 'pdf_only_suppliers' in locals() and len(pdf_only_suppliers) > 0:
            recommendations.append(f"📄 **PDF Documentation Gap**: {len(pdf_only_suppliers)} PDF-documented suppliers have no payments")
        
        if 'validity_rate' in locals() and validity_rate < 95:
            recommendations.append(f"🔧 **Improve Reference Quality**: Only {validity_rate:.1f}% of voucher references are valid")
        
        recommendations.extend([
            "📊 **Standardize Names**: Implement consistent supplier naming conventions",
            "🔗 **Enhance Linkage**: Improve document traceability across all systems",
            "🔍 **Regular Audits**: Conduct monthly supplier linkage quality checks"
        ])
        
        for rec in recommendations:
            st.markdown(f"- {rec}")

    def create_grn_transaction_summary(self, grn_df, voucher_df):
        """Create corrected GRN-Transaction analysis summary with proper PDF linkage."""
        st.markdown("### 📊 GRN-Transaction Analysis Summary (Corrected)")
        st.info("✅ **Using Corrected Linkage**: PDF Reference → GRN inv_no → GRN voucher → Payment voucher_no")
        
        # Load PDF data if available
        pdf_df = None
        if os.path.exists('output/individual_hr185_transactions.csv'):
            pdf_df = pd.read_csv('output/individual_hr185_transactions.csv')
            pdf_df['reference_normalized'] = pdf_df['reference'].apply(self.normalize_reference)
        
        # Normalize GRN data
        grn_analysis = grn_df.copy()
        grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(self.normalize_reference)
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
            st.plotly_chart(fig, use_container_width=True, key="enhanced_anomaly_detection")
        
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
        
        # Corrected value mismatch explanation
        if grn_value > 0 and voucher_value > 0:
            value_diff_pct = abs(grn_value - voucher_value) / grn_value * 100
            if value_diff_pct > 10:
                risk_items.append({
                    'Risk Type': 'Total Value Mismatch',
                    'Severity': 'Information' if value_diff_pct < 50 else 'Medium',
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
                    return ['background-color: #e8f5e8'] * len(row)
            
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
            "� **Process Improvement**: Ensure proper document traceability for all transactions"
        ]
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
    
    def normalize_reference(self, ref):
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

    def create_pdf_analytics(self, filters=None):
        """Create comprehensive analytics for PDF-extracted data."""
        st.header("📄 PDF Reports Analytics")
        st.markdown("Analysis of data extracted from HR185 and HR990 PDF reports")
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        # Load PDF data
        hr185_df = self.load_filtered_data('individual_hr185_transactions.csv', filters)
        hr990_df = self.load_filtered_data('individual_hr990_expenditure.csv', filters)
        
        if hr185_df is None and hr990_df is None:
            st.warning("No PDF data available. Please ensure PDF files have been processed.")
            return
        
        # Create tabs for different PDF report types
        pdf_tab1, pdf_tab2, pdf_tab3 = st.tabs([
            "📊 HR185 Transactions", 
            "📈 HR990 Statistics", 
            "🔍 Combined Analysis"
        ])
        
        with pdf_tab1:
            self.create_hr185_analytics(hr185_df)
        
        with pdf_tab2:
            self.create_hr990_analytics(hr990_df)
        
        with pdf_tab3:
            self.create_combined_pdf_analytics(hr185_df, hr990_df)
    
    def create_hr185_analytics(self, hr185_df):
        """Create analytics for HR185 transaction data."""
        if hr185_df is None or hr185_df.empty:
            st.warning("No HR185 transaction data available.")
            return
        
        st.subheader("📊 HR185 Supplier Transactions Analysis")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", f"{len(hr185_df):,}")
        
        with col2:
            if 'supplier_name' in hr185_df.columns:
                st.metric("Unique Suppliers", hr185_df['supplier_name'].nunique())
        
        with col3:
            if 'amount' in hr185_df.columns:
                total_amount = hr185_df['amount'].sum()
                st.metric("Total Amount", f"R{total_amount:,.2f}")
        
        with col4:
            if 'transaction_date' in hr185_df.columns:
                date_range = hr185_df['transaction_date'].max() - hr185_df['transaction_date'].min()
                st.metric("Date Range", f"{date_range.days} days")
        
        # Transaction analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction types distribution
            if 'transaction_type' in hr185_df.columns:
                st.markdown("### 📋 Transaction Types")
                type_counts = hr185_df['transaction_type'].value_counts()
                
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=type_counts.index,
                    values=type_counts.values,
                    hole=0.4,
                    hovertemplate="<b>%{label}</b><br>" +
                                "Count: %{value}<br>" +
                                "Percentage: %{percent}<br>" +
                                "<extra>Data Source: HR185 Transaction Reports from PDF files</extra>"
                ))
                
                fig.update_layout(
                    title="Distribution of Transaction Types",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key="authorization_official_patterns")
        
        with col2:
            # Monthly transaction volume
            if 'transaction_date' in hr185_df.columns:
                st.markdown("### 📅 Monthly Transaction Volume")
                
                # Group by month
                hr185_df['month'] = hr185_df['transaction_date'].dt.to_period('M')
                monthly_counts = hr185_df.groupby('month').size().reset_index(name='count')
                monthly_counts['month_str'] = monthly_counts['month'].astype(str)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=monthly_counts['month_str'],
                    y=monthly_counts['count'],
                    name='Transactions',
                    marker_color='lightblue',
                    hovertemplate="<b>%{x}</b><br>" +
                                "Transactions: %{y}<br>" +
                                "<extra>Data Source: HR185 Transaction Reports from PDF files</extra>"
                ))
                
                fig.update_layout(
                    title="Monthly Transaction Volume",
                    xaxis_title="Month",
                    yaxis_title="Number of Transactions",
                    height=400,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True, key="authorization_value_analysis")
        
        # Top suppliers analysis
        if 'supplier_name' in hr185_df.columns and 'amount' in hr185_df.columns:
            st.markdown("### 🏪 Top Suppliers by Transaction Value")
            
            supplier_amounts = hr185_df.groupby('supplier_name')['amount'].agg(['sum', 'count']).reset_index()
            supplier_amounts.columns = ['supplier_name', 'total_amount', 'transaction_count']
            supplier_amounts = supplier_amounts.sort_values('total_amount', ascending=False).head(15)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=supplier_amounts['supplier_name'],
                y=supplier_amounts['total_amount'],
                name='Total Amount',
                marker_color='green',
                text=[f"R{val:,.0f}" for val in supplier_amounts['total_amount']],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>" +
                            "Total Amount: R%{y:,.2f}<br>" +
                            "Transactions: %{customdata}<br>" +
                            "<extra>Data Source: HR185 Transaction Reports from PDF files</extra>",
                customdata=supplier_amounts['transaction_count']
            ))
            
            fig.update_layout(
                title="Top 15 Suppliers by Transaction Value",
                xaxis_title="Supplier",
                yaxis_title="Total Amount (R)",
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True, key="authorization_monthly_trends")
            
            # Show data table
            st.markdown("#### 📊 Detailed Supplier Breakdown")
            display_df = supplier_amounts.copy()
            display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"R{x:,.2f}")
            st.dataframe(display_df, use_container_width=True)
    
    def create_hr990_analytics(self, hr990_df):
        """Create analytics for HR990 expenditure statistics."""
        if hr990_df is None or hr990_df.empty:
            st.warning("No HR990 statistics data available.")
            return
        
        st.subheader("📈 HR990 Expenditure Statistics Analysis")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{len(hr990_df):,}")
        
        with col2:
            if 'section' in hr990_df.columns:
                st.metric("Report Sections", hr990_df['section'].nunique())
        
        with col3:
            if 'count' in hr990_df.columns:
                total_count = hr990_df['count'].sum()
                st.metric("Total Count", f"{total_count:,}")
        
        with col4:
            if 'document_type' in hr990_df.columns:
                st.metric("Document Types", hr990_df['document_type'].nunique())
        
        # Section analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Sections distribution
            if 'section' in hr990_df.columns and 'count' in hr990_df.columns:
                st.markdown("### 📋 Statistics by Section")
                
                section_totals = hr990_df.groupby('section')['count'].sum().sort_values(ascending=False)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=section_totals.index,
                    x=section_totals.values,
                    orientation='h',
                    marker_color='orange',
                    text=[f"{val:,}" for val in section_totals.values],
                    textposition='outside',
                    hovertemplate="<b>%{y}</b><br>" +
                                "Count: %{x:,}<br>" +
                                "<extra>Data Source: HR990 Expenditure Statistics from PDF files</extra>"
                ))
                
                fig.update_layout(
                    title="Count by Report Section",
                    xaxis_title="Count",
                    yaxis_title="Section",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key="authorization_threshold_analysis")
        
        with col2:
            # Document types
            if 'document_type' in hr990_df.columns:
                st.markdown("### 📄 Document Types")
                
                doc_counts = hr990_df['document_type'].value_counts()
                
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=doc_counts.index,
                    values=doc_counts.values,
                    hole=0.4,
                    hovertemplate="<b>%{label}</b><br>" +
                                "Count: %{value}<br>" +
                                "Percentage: %{percent}<br>" +
                                "<extra>Data Source: HR990 Expenditure Statistics from PDF files</extra>"
                ))
                
                fig.update_layout(
                    title="Distribution of Document Types",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key="multi_official_authorizations")
        
        # Reference analysis
        if 'reference' in hr990_df.columns and 'count' in hr990_df.columns:
            st.markdown("### 🔍 Top References by Count")
            
            ref_totals = hr990_df.groupby('reference')['count'].sum().sort_values(ascending=False).head(20)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=ref_totals.index,
                y=ref_totals.values,
                marker_color='purple',
                text=[f"{val:,}" for val in ref_totals.values],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>" +
                            "Total Count: %{y:,}<br>" +
                            "<extra>Data Source: HR990 Expenditure Statistics from PDF files</extra>"
            ))
            
            fig.update_layout(
                title="Top 20 References by Count",
                xaxis_title="Reference",
                yaxis_title="Count",
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True, key="authorization_processing_time")
    
    def create_combined_pdf_analytics(self, hr185_df, hr990_df):
        """Create combined analytics for both PDF data sources."""
        st.subheader("🔍 Combined PDF Reports Analysis")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 HR185 Summary")
            if hr185_df is not None and not hr185_df.empty:
                st.metric("Transactions", f"{len(hr185_df):,}")
                if 'amount' in hr185_df.columns:
                    st.metric("Total Value", f"R{hr185_df['amount'].sum():,.2f}")
            else:
                st.info("No HR185 data available")
        
        with col2:
            st.markdown("### 📈 HR990 Summary")
            if hr990_df is not None and not hr990_df.empty:
                st.metric("Statistics", f"{len(hr990_df):,}")
                if 'count' in hr990_df.columns:
                    st.metric("Total Count", f"{hr990_df['count'].sum():,}")
            else:
                st.info("No HR990 data available")
        
        with col3:
            st.markdown("### 📋 Combined Total")
            total_records = 0
            if hr185_df is not None and not hr185_df.empty:
                total_records += len(hr185_df)
            if hr990_df is not None and not hr990_df.empty:
                total_records += len(hr990_df)
            st.metric("Total PDF Records", f"{total_records:,}")
        
        # Data coverage timeline
        if hr185_df is not None and not hr185_df.empty and 'transaction_date' in hr185_df.columns:
            st.markdown("### 📅 Data Coverage Timeline")
            
            # Create timeline visualization
            timeline_data = []
            
            # Add HR185 date range
            hr185_min_date = hr185_df['transaction_date'].min()
            hr185_max_date = hr185_df['transaction_date'].max()
            timeline_data.append({
                'Report': 'HR185 Transactions',
                'Start': hr185_min_date,
                'End': hr185_max_date,
                'Records': len(hr185_df)
            })
            
            # Add HR990 periods (from report_period if available)
            if hr990_df is not None and not hr990_df.empty and 'report_period' in hr990_df.columns:
                unique_periods = hr990_df['report_period'].unique()
                for period in unique_periods:
                    if pd.notna(period) and '-' in str(period):
                        try:
                            start_str, end_str = str(period).split('-')
                            start_date = pd.to_datetime(start_str, format='%Y%m')
                            end_date = pd.to_datetime(end_str, format='%Y%m')
                            period_records = len(hr990_df[hr990_df['report_period'] == period])
                            timeline_data.append({
                                'Report': f'HR990 {period}',
                                'Start': start_date,
                                'End': end_date,
                                'Records': period_records
                            })
                        except:
                            continue
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                
                fig = go.Figure()
                
                for i, row in timeline_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['Start'], row['End']],
                        y=[row['Report'], row['Report']],
                        mode='lines+markers',
                        name=row['Report'],
                        line=dict(width=10),
                        hovertemplate="<b>%{y}</b><br>" +
                                    "Period: %{x}<br>" +
                                    f"Records: {row['Records']:,}<br>" +
                                    "<extra>Data Source: PDF Reports Timeline</extra>"
                    ))
                
                fig.update_layout(
                    title="PDF Data Coverage Timeline",
                    xaxis_title="Date",
                    yaxis_title="Report Type",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, key="authorization_risk_assessment")
        
        # Recommendations
        st.markdown("### 💡 PDF Data Insights & Recommendations")
        
        recommendations = []
        
        if hr185_df is not None and not hr185_df.empty:
            if 'supplier_name' in hr185_df.columns:
                top_supplier = hr185_df['supplier_name'].value_counts().index[0]
                recommendations.append(f"📊 **Top Supplier in HR185**: {top_supplier} - Monitor for concentration risk")
        
        if hr990_df is not None and not hr990_df.empty:
            if 'section' in hr990_df.columns:
                top_section = hr990_df['section'].value_counts().index[0]
                recommendations.append(f"📈 **Most Active HR990 Section**: {top_section}")
        
        recommendations.extend([
            "🔍 **Data Quality**: PDF extraction successful - consider automating this process",
            "📋 **Integration**: PDF data complements existing Excel/CSV data sources",
            "⚡ **Performance**: 3,000+ additional records enhance analysis depth"
        ])
        
        for rec in recommendations:
            st.markdown(f"- {rec}")

    def create_data_tables(self, filters=None):
        """Create comprehensive data tables section with filtering capabilities."""
        st.header("📋 Data Tables")
        
        # Get list of available CSV files
        csv_files = [
            ("HR995 GRN Records", "hr995_grn.csv"),
            ("HR995 Issue Records", "hr995_issue.csv"),
            ("HR995 Voucher Records", "hr995_voucher.csv"),
            ("HR995 Redundant Records", "hr995_redundant.csv"),
            ("All Stock Data (Combined)", "all_stock_data.csv"),
            ("Suppliers Master Data", "suppliers.csv"),
            ("Stock Adjustments", "stock_adjustments.csv"),
            ("HR185 Transactions (PDF)", "individual_hr185_transactions.csv"),
            ("HR990 Expenditure (PDF)", "individual_hr990_expenditure.csv"),
            ("Variance Report", "variance_report.csv"),
            ("HR450 Data", "hr450_data.csv"),
            ("2023 Suppliers List", "individual_2023_list_of_suppliers.csv"),
            ("2024 Suppliers List", "individual_2024_list_of_suppliers.csv"),
            ("Final Stock Listing 2023", "individual_final_stock_listing_2023.csv"),
            ("Stock Balance 2023-2024", "individual_final_stock_list_2324.csv"),
            ("Stock Adjustments 2024", "individual_stock_adjustment_item_2024.csv"),
            ("Objective 1: Item Frequency", "objective_1_item_frequency_by_supplier.csv"),
            ("Objective 2: Audit Trail", "objective_2_stock_audit_trail.csv"),
            ("Objective 3: HR995 Report", "objective_3_hr995_report.csv"),
            ("Objective 4: End-to-End Process", "objective_4_end_to_end_process.csv"),
            ("Objective 5: Stock Balances by Year", "objective_5_stock_balances_by_year.csv"),
            ("❌ Invalid Voucher References", "invalid_voucher_references.csv")
        ]
        
        # Table selector
        st.subheader("📊 Select Data Table")
        selected_table = st.selectbox(
            "Choose a data table to view:",
            options=[display_name for display_name, _ in csv_files],
            index=0
        )
        
        # Find the corresponding filename
        selected_file = next(filename for display_name, filename in csv_files if display_name == selected_table)
        
        # Load the selected data
        df = self.load_data(selected_file)
        
        if df is not None and not df.empty:
            # Special handling for Invalid Voucher References
            if selected_file == "invalid_voucher_references.csv":
                # Try to load corrected version first
                corrected_file = 'output/invalid_voucher_references_corrected.csv'
                if os.path.exists(corrected_file):
                    corrected_df = pd.read_csv(corrected_file)
                    st.info("📊 **Using Corrected Analysis**: PDF → GRN → Voucher linkage applied")
                    self.display_invalid_voucher_analysis(corrected_df)
                else:
                    st.warning("⚠️ **Original Analysis**: Run corrected linkage analysis for updated results")
                    self.display_invalid_voucher_analysis(df)
                return
            
            # Apply supplier filter if active
            if filters and filters.get('suppliers') and 'All Suppliers' not in filters['suppliers']:
                supplier_cols = [col for col in df.columns if 'supplier' in col.lower()]
                if supplier_cols:
                    supplier_col = supplier_cols[0]
                    df = df[df[supplier_col].isin(filters['suppliers'])]
            
            st.success(f"✅ Loaded {len(df):,} records from {selected_table}")
            
            # Display data source information
            if selected_file in self.data_sources:
                st.info(f"📋 **Data Source**: {self.data_sources[selected_file]}")
            
            # Table filtering options
            st.subheader("🔍 Table Filters")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Search functionality
                search_term = st.text_input("🔍 Search in all columns:", 
                                          placeholder="Enter search term...")
                
            with col2:
                # Column filter
                if len(df.columns) > 0:
                    filter_column = st.selectbox("Filter by column:", 
                                               options=["No filter"] + list(df.columns))
                else:
                    filter_column = "No filter"
            
            with col3:
                # Number of rows to display
                max_rows = st.number_input("Max rows to display:", 
                                         min_value=10, max_value=10000, value=100, step=50)
            
            # Apply search filter
            filtered_df = df.copy()
            
            if search_term:
                # Search across all text columns
                text_columns = df.select_dtypes(include=['object', 'string']).columns
                if len(text_columns) > 0:
                    search_mask = df[text_columns].astype(str).apply(
                        lambda x: x.str.contains(search_term, case=False, na=False)
                    ).any(axis=1)
                    filtered_df = df[search_mask]
                    st.info(f"🔍 Search results: {len(filtered_df):,} records match '{search_term}'")
            
            # Apply column filter
            if filter_column != "No filter" and filter_column in df.columns:
                unique_values = sorted(df[filter_column].dropna().unique())
                if len(unique_values) <= 50:  # Only show filter for columns with reasonable number of unique values
                    selected_values = st.multiselect(
                        f"Filter {filter_column}:",
                        options=unique_values,
                        default=unique_values[:10] if len(unique_values) > 10 else unique_values
                    )
                    if selected_values:
                        filtered_df = filtered_df[filtered_df[filter_column].isin(selected_values)]
                        st.info(f"🎯 Column filter applied: {len(filtered_df):,} records")
                else:
                    st.warning(f"⚠️ Too many unique values in {filter_column} ({len(unique_values)}) to show filter")
            
            # Display summary statistics
            st.subheader("📈 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", f"{len(filtered_df):,}")
            with col2:
                st.metric("Total Columns", len(filtered_df.columns))
            with col3:
                numeric_cols = len(filtered_df.select_dtypes(include=[np.number]).columns)
                st.metric("Numeric Columns", numeric_cols)
            with col4:
                text_cols = len(filtered_df.select_dtypes(include=['object', 'string']).columns)
                st.metric("Text Columns", text_cols)
            
            # Column information
            with st.expander("📋 Column Information"):
                col_info = []
                for col in filtered_df.columns:
                    dtype = str(filtered_df[col].dtype)
                    non_null = filtered_df[col].notna().sum()
                    null_count = filtered_df[col].isna().sum()
                    unique_count = filtered_df[col].nunique()
                    
                    col_info.append({
                        'Column': col,
                        'Data Type': dtype,
                        'Non-Null Count': f"{non_null:,}",
                        'Null Count': f"{null_count:,}",
                        'Unique Values': f"{unique_count:,}"
                    })
                
                col_info_df = pd.DataFrame(col_info)
                st.dataframe(col_info_df, use_container_width=True)
            
            # Display the filtered data table
            st.subheader(f"📊 {selected_table} Data")
            
            # Limit rows for performance
            display_df = filtered_df.head(max_rows)
            
            if len(filtered_df) > max_rows:
                st.warning(f"⚠️ Showing first {max_rows:,} rows out of {len(filtered_df):,} total records")
            
            # Display the table with pagination-like functionality
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600
            )
            
            # Download options
            st.subheader("💾 Download Options")
            col1, col2 = st.columns(2)
            
            with col1:
                # Download filtered data as CSV
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data (CSV)",
                    data=csv_data,
                    file_name=f"filtered_{selected_file}",
                    mime="text/csv"
                )
            
            with col2:
                # Download column info
                col_info_csv = pd.DataFrame(col_info).to_csv(index=False)
                st.download_button(
                    label="📋 Download Column Info (CSV)",
                    data=col_info_csv,
                    file_name=f"column_info_{selected_file}",
                    mime="text/csv"
                )
            
            # Quick data analysis
            if st.checkbox("🔬 Show Quick Analysis"):
                st.subheader("🔬 Quick Data Analysis")
                
                # Numeric column analysis
                numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.write("**Numeric Columns Summary:**")
                    st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
                
                # Categorical analysis
                text_cols = filtered_df.select_dtypes(include=['object', 'string']).columns
                if len(text_cols) > 0:
                    st.write("**Categorical Columns (Top Values):**")
                    for col in text_cols[:5]:  # Show first 5 text columns
                        if filtered_df[col].notna().sum() > 0:
                            top_values = filtered_df[col].value_counts().head(10)
                            st.write(f"*{col}:*")
                            st.bar_chart(top_values)
                
                # Missing data analysis
                missing_data = filtered_df.isnull().sum()
                missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
                if len(missing_data) > 0:
                    st.write("**Missing Data by Column:**")
                    st.bar_chart(missing_data)
        
        else:
            st.error(f"❌ Could not load data from {selected_file}")
            st.info("📋 Available files in output folder:")
            
            # List available files
            try:
                output_files = list(self.output_folder.glob("*.csv"))
                for file in output_files[:10]:  # Show first 10 files
                    st.text(f"  • {file.name}")
                if len(output_files) > 10:
                    st.text(f"  ... and {len(output_files) - 10} more files")
            except Exception as e:
                st.error(f"Error listing files: {e}")

    def run_dashboard(self):
        """Run the main dashboard application."""
        # Create sidebar filters
        filters = self.create_sidebar_filters()
        
        # Main content
        self.create_executive_summary(filters)
        
        # Navigation tabs for main sections
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "💰 Financial Analytics", 
            "📦 Inventory Analytics", 
            "🏪 Supplier Analytics", 
            "⚙️ Operational Analytics",
            "🚨 Anomaly Detection",
            "📄 PDF Reports Analytics",
            "📋 Data Tables"
        ])
        
        with tab1:
            self.create_financial_analytics(filters)
        
        with tab2:
            self.create_inventory_analytics(filters)
        
        with tab3:
            self.create_supplier_analytics(filters)
        
        with tab4:
            self.create_operational_analytics(filters)
        
        with tab5:
            self.create_anomaly_detection(filters)
        
        with tab6:
            self.create_pdf_analytics(filters)
        
        with tab7:
            self.create_data_tables(filters)
        
        # Footer
        st.markdown("---")
        st.markdown("*Dashboard powered by Streamlit and Plotly* | *Data processed by Stock Data Processor*")

    def display_invalid_voucher_analysis(self, invalid_df):
        """Display comprehensive analysis of invalid voucher references."""
        st.header("❌ Invalid Voucher References Analysis")
        
        # Check if this is corrected analysis
        is_corrected = 'has_pdf_link' in invalid_df.columns
        if is_corrected:
            st.markdown("*Detailed analysis using corrected PDF → GRN → Voucher linkage*")
        else:
            st.markdown("*Detailed analysis of GRN voucher references that don't have corresponding payment vouchers*")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Invalid GRN Records", f"{len(invalid_df):,}")
        
        with col2:
            total_value = invalid_df['nett_grn_amt'].sum()
            st.metric("Total Value", f"R{total_value:,.2f}")
        
        with col3:
            # Handle both voucher and voucher_normalized columns
            if 'voucher' in invalid_df.columns:
                unique_vouchers = invalid_df['voucher'].nunique()
            elif 'voucher_normalized' in invalid_df.columns:
                unique_vouchers = invalid_df['voucher_normalized'].nunique()
            else:
                unique_vouchers = 0
            st.metric("Unique Invalid Vouchers", f"{unique_vouchers:,}")
        
        with col4:
            avg_value = invalid_df['nett_grn_amt'].mean()
            st.metric("Average Value", f"R{avg_value:,.2f}")
        
        # Alert box for high value
        if total_value > 10000000:  # 10 million
            st.error(f"🚨 **HIGH VALUE ALERT**: R{total_value:,.2f} in invalid voucher references requires immediate attention!")
        
        # PDF Linkage Analysis (if corrected analysis)
        if is_corrected:
            st.subheader("🔗 PDF Linkage Breakdown")
            
            pdf_summary = invalid_df.groupby('has_pdf_link').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            pdf_summary.columns = ['Count', 'Total_Value_R']
            pdf_summary['Percentage'] = (pdf_summary['Count'] / len(invalid_df) * 100).round(1)
            
            st.dataframe(pdf_summary, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # PDF linkage pie chart
                fig_pdf = px.pie(
                    values=pdf_summary['Count'],
                    names=pdf_summary.index,
                    title="Invalid Vouchers by PDF Linkage",
                    color_discrete_sequence=['#ff9999', '#66b3ff']
                )
                st.plotly_chart(fig_pdf, use_container_width=True, key="pdf_document_patterns")
            
            with col2:
                # Value breakdown
                fig_value = px.bar(
                    x=pdf_summary.index,
                    y=pdf_summary['Total_Value_R'],
                    title="Invalid Voucher Value by PDF Linkage",
                    color=pdf_summary['Total_Value_R'],
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_value, use_container_width=True, key="pdf_value_correlation")
            
            # Insights for corrected analysis
            st.info("""
            **PDF Linkage Insights:**
            - PDF-linked invalid vouchers have proper document traceability from HR185 → GRN → Voucher
            - Non-PDF-linked invalid vouchers may be from different transaction streams or systems
            - Lower PDF-linked invalid amounts suggest better controls for PDF-documented transactions
            """)
        
        # Reason breakdown
        st.subheader("📊 Breakdown by Invalid Reason")
        
        if 'invalid_reason' in invalid_df.columns:
            reason_summary = invalid_df.groupby('invalid_reason').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            reason_summary.columns = ['Count', 'Total_Value_R']
            reason_summary['Percentage'] = (reason_summary['Count'] / len(invalid_df) * 100).round(1)
            reason_summary = reason_summary.sort_values('Total_Value_R', ascending=False)
            
            st.dataframe(reason_summary, width='stretch')
            
            # Pie chart for reasons
            fig_pie = px.pie(
                values=reason_summary['Count'], 
                names=reason_summary.index,
                title="Invalid Voucher References by Reason"
            )
            st.plotly_chart(fig_pie, use_container_width=True, key="pdf_type_distribution")
        
        # Explanation of reasons
        st.subheader("🔍 Explanation of Invalid Reasons")
        
        explanations = {
            "INVI sequence gap or timing issue": {
                "icon": "⏰",
                "explanation": "These are INVI-prefixed vouchers that fall within the expected sequence range but don't exist in the payment system. This typically indicates timing issues where GRNs are created before vouchers are processed, or sequence gaps in the voucher numbering system.",
                "action": "Review with finance team to verify if these vouchers are pending processing or if there are sequence gaps in the INVI numbering system."
            },
            "Special/manual voucher not in payment system": {
                "icon": "📝",
                "explanation": "These vouchers with '999I' prefix typically indicate special, manual, or temporary vouchers that may not follow the standard payment processing workflow.",
                "action": "Verify with finance team if these are legitimate manual entries or if they require special processing outside the standard payment system."
            },
            "Different supplier/system voucher": {
                "icon": "🏢",
                "explanation": "These vouchers use different prefixes (like SINA, KEDA, WATA) suggesting they may belong to different supplier systems or payment processing streams.",
                "action": "Confirm if these vouchers are processed through different systems or if they require separate reconciliation processes."
            },
            "Unknown voucher system or data entry error": {
                "icon": "❓",
                "explanation": "These vouchers don't match any recognized pattern and may indicate data entry errors or vouchers from unknown systems.",
                "action": "Investigate individual cases to determine if they are data entry errors or legitimate vouchers from unrecognized systems."
            }
        }
        
        for reason, details in explanations.items():
            if reason in invalid_df['invalid_reason'].values:
                with st.expander(f"{details['icon']} {reason}"):
                    st.markdown(f"**Explanation**: {details['explanation']}")
                    st.markdown(f"**Recommended Action**: {details['action']}")
        
        # Voucher prefix analysis
        st.subheader("🏷️ Voucher Prefix Analysis")
        
        if 'voucher_prefix' in invalid_df.columns:
            prefix_summary = invalid_df.groupby('voucher_prefix').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            prefix_summary.columns = ['Count', 'Total_Value_R']
            prefix_summary = prefix_summary.sort_values('Total_Value_R', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Prefix Summary:**")
                st.dataframe(prefix_summary, width='stretch')
            
            with col2:
                # Bar chart for prefixes
                fig_bar = px.bar(
                    x=prefix_summary.index,
                    y=prefix_summary['Total_Value_R'],
                    title="Invalid Voucher Value by Prefix",
                    labels={'x': 'Voucher Prefix', 'y': 'Total Value (R)'}
                )
                st.plotly_chart(fig_bar, use_container_width=True, key="pdf_monthly_processing")
        
        # Date analysis
        st.subheader("📅 Date Analysis")
        
        if 'date' in invalid_df.columns:
            invalid_df['date_parsed'] = pd.to_datetime(invalid_df['date'], errors='coerce')
            
            # Monthly breakdown
            invalid_df['year_month'] = invalid_df['date_parsed'].dt.to_period('M')
            monthly_summary = invalid_df.groupby('year_month').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            monthly_summary.columns = ['Count', 'Total_Value_R']
            
            if len(monthly_summary) > 0:
                # Time series chart
                fig_time = px.line(
                    x=monthly_summary.index.astype(str),
                    y=monthly_summary['Total_Value_R'],
                    title="Invalid Voucher References Over Time",
                    labels={'x': 'Month', 'y': 'Total Value (R)'}
                )
                st.plotly_chart(fig_time, use_container_width=True, key="pdf_processing_timeline")
        
        # Top invalid vouchers by value
        st.subheader("💰 Top Invalid Vouchers by Value")
        
        top_invalid = invalid_df.nlargest(10, 'nett_grn_amt')[
            ['voucher', 'supplier_name', 'date', 'nett_grn_amt', 'invalid_reason', 'description']
        ]
        st.dataframe(top_invalid, width='stretch')
        
        # Supplier impact analysis
        st.subheader("🏪 Supplier Impact Analysis")
        
        if 'supplier_name' in invalid_df.columns:
            supplier_impact = invalid_df.groupby('supplier_name').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum',
                'voucher': 'nunique'
            }).round(2)
            supplier_impact.columns = ['GRN_Count', 'Total_Value_R', 'Unique_Vouchers']
            supplier_impact = supplier_impact.sort_values('Total_Value_R', ascending=False)
            
            st.markdown("**Top 10 Suppliers by Invalid Voucher Value:**")
            st.dataframe(supplier_impact.head(10), width='stretch')
        
        # Recommendations
        st.subheader("💡 Recommendations")
        
        recommendations = [
            "🔍 **Immediate Action**: Investigate high-value invalid vouchers (>R100,000) individually",
            "📅 **Weekly Review**: Set up weekly monitoring of invalid voucher rates and values",
            "🏢 **System Integration**: Work with finance team to understand different voucher numbering systems",
            "⏰ **Timing Alignment**: Review GRN creation vs voucher processing timing to reduce sequence gaps",
            "📊 **Automated Alerts**: Implement alerts when invalid voucher rate exceeds 5% or value exceeds R1M",
            "🔄 **Process Improvement**: Establish standardized voucher numbering across all systems",
            "📋 **Regular Reconciliation**: Schedule monthly reconciliation of GRN vs payment vouchers"
        ]
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
        
        # Detailed data table
        st.subheader("📋 Detailed Invalid Voucher Data")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            reason_filter = st.multiselect(
                "Filter by Reason:",
                options=invalid_df['invalid_reason'].unique(),
                default=invalid_df['invalid_reason'].unique()
            )
        
        with col2:
            min_value = st.number_input("Minimum Value (R):", value=0, step=1000)
        
        with col3:
            max_rows = st.number_input("Max rows to display:", value=100, min_value=10, max_value=1000)
        
        # Apply filters
        filtered_invalid = invalid_df[
            (invalid_df['invalid_reason'].isin(reason_filter)) &
            (invalid_df['nett_grn_amt'] >= min_value)
        ]
        
        st.info(f"📊 Showing {min(len(filtered_invalid), max_rows):,} of {len(filtered_invalid):,} filtered records")
        
        # Display filtered data
        display_columns = [
            'grn_no', 'voucher', 'supplier_name', 'date', 'nett_grn_amt', 
            'invalid_reason', 'voucher_prefix', 'item_no', 'description'
        ]
        display_columns = [col for col in display_columns if col in filtered_invalid.columns]
        
        st.dataframe(
            filtered_invalid[display_columns].head(max_rows),
            width='stretch'
        )
        
        # Download option
        st.subheader("💾 Download Invalid Voucher Report")
        
        csv_data = filtered_invalid.to_csv(index=False)
        st.download_button(
            label="📥 Download Invalid Voucher Analysis (CSV)",
            data=csv_data,
            file_name=f"invalid_voucher_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def main():
    """Main function to run the dashboard."""
    try:
        dashboard = AdvancedStockDashboard()
        dashboard.run_dashboard()
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        st.info("Please ensure the stock data processor has been run first to generate the required data files.")

if __name__ == "__main__":
    main()
