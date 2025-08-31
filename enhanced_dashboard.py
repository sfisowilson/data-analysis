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
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Optional
import calendar

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

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
        grn_df = self.load_filtered_data("hr995_grn.csv", filters)
        issue_df = self.load_filtered_data("hr995_issue.csv", filters)
        voucher_df = self.load_data("hr995_voucher.csv")
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
    
    def create_financial_analytics(self, filters=None):
        """Create comprehensive financial analytics section."""
        st.header("💰 Financial Analytics")
        
        grn_df = self.load_filtered_data("hr995_grn.csv", filters)
        voucher_df = self.load_filtered_data("hr995_voucher.csv", filters)
        
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
                st.plotly_chart(fig1, use_container_width=True)
                
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
                st.plotly_chart(fig2, use_container_width=True)
                
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
                st.plotly_chart(fig3, use_container_width=True)
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
                st.plotly_chart(fig1, width="stretch")
            
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
                st.plotly_chart(fig2, width="stretch")
            
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
            st.plotly_chart(fig3, width="stretch")
    
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
                st.plotly_chart(fig1, width="stretch")
            
            with col2:
                fig2 = px.bar(category_analysis, x='category', y='count',
                             title='Transaction Count by Category')
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, width="stretch")
    
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
                st.plotly_chart(fig1, width="stretch")
        
        with col2:
            if not voucher_df.empty and 'cheq_amt' in voucher_df.columns:
                voucher_df = self.clean_financial_data(voucher_df, 'cheq_amt')
                fig2 = px.box(voucher_df, y='cheq_amt',
                             title='Voucher Amount Distribution')
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, width="stretch")
    
    def create_inventory_analytics(self, filters=None):
        """Create inventory analytics section."""
        st.header("📦 Inventory Analytics")
        
        grn_df = self.load_filtered_data("hr995_grn.csv", filters)
        issue_df = self.load_filtered_data("hr995_issue.csv", filters)
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
                
                fig1 = px.bar(x=top_items.values, y=top_items.index,
                             title='Top 20 Items by Total Movement',
                             labels={'x': 'Total Quantity', 'y': 'Item ID'},
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
                st.plotly_chart(fig1, width="stretch")
                
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
                st.plotly_chart(fig2, width="stretch")
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
            st.plotly_chart(fig1, width="stretch")
            
            # Turnover distribution
            fig2 = px.scatter(turnover_df, x='received', y='issued',
                             hover_data=['item_id'],
                             title='Received vs Issued Quantities',
                             labels={'received': 'Received Quantity', 'issued': 'Issued Quantity'})
            st.plotly_chart(fig2, width="stretch")
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
                
                fig = px.bar(x=adjustment_summary.values, y=adjustment_summary.index,
                           title='Stock Adjustments by Source',
                           orientation='h')
                st.plotly_chart(fig, width="stretch")
        else:
            st.warning("No stock adjustment data available")
    
    def create_supplier_analytics(self, filters=None):
        """Create supplier analytics section."""
        st.header("🏪 Supplier Analytics")
        
        suppliers_df = self.load_filtered_data("suppliers.csv", filters)
        grn_df = self.load_filtered_data("hr995_grn.csv", filters)
        
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
            st.plotly_chart(fig, width="stretch")
            
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
                
                fig = px.pie(values=supplier_sources.values, names=supplier_sources.index,
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
                st.plotly_chart(fig, width="stretch")
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
                st.plotly_chart(fig, width="stretch")
    
    def create_operational_analytics(self, filters=None):
        """Create operational analytics section."""
        st.header("⚙️ Operational Analytics")
        
        audit_df = self.load_filtered_data("objective_2_stock_audit_trail.csv", filters)
        process_df = self.load_filtered_data("objective_4_end_to_end_process.csv", filters)
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        tab1, tab2, tab3 = st.tabs(["🔍 Audit Trail", "🔄 Process Flow", "📊 Efficiency"])
        
        with tab1:
            self.create_audit_analysis(audit_df)
        
        with tab2:
            self.create_process_analysis(process_df)
        
        with tab3:
            self.create_efficiency_analysis(audit_df)
    
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
                st.plotly_chart(fig1, width="stretch")
            
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
                    st.plotly_chart(fig2, width="stretch")
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
                st.plotly_chart(fig, width="stretch")
            
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
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Efficiency analysis requires official data")
    
    def create_sidebar_filters(self):
        """Create sidebar with filters and navigation."""
        st.sidebar.markdown("## 🎛️ Dashboard Controls")
        
        # Supplier filter
        st.sidebar.markdown("### 🏪 Supplier Filter")
        
        # Get all unique suppliers from GRN data
        grn_df = self.load_data("hr995_grn.csv")
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
            'min_value': min_value
        }
    
    def create_anomaly_detection(self, filters=None):
        """Create comprehensive anomaly detection and alerts section."""
        st.header("🚨 Anomaly Detection & Risk Analysis")
        st.markdown("*Identify unusual patterns, outliers, and potential issues in your stock data*")
        
        # Show filter status
        if filters and filters.get('supplier') and filters['supplier'] != "All Suppliers":
            st.info(f"📊 Filtered by Supplier: **{filters['supplier']}**")
        
        # Load data for anomaly detection
        grn_df = self.load_filtered_data("hr995_grn.csv", filters)
        issue_df = self.load_filtered_data("hr995_issue.csv", filters)
        voucher_df = self.load_filtered_data("hr995_voucher.csv", filters)
        stock_df = self.load_filtered_data("all_stock_data.csv", filters)
        
        if not any(len(df) > 0 for df in [grn_df, issue_df, voucher_df, stock_df]):
            st.warning("No data available for anomaly detection.")
            return
        
        # Create anomaly detection subsections
        anomaly_tab1, anomaly_tab2, anomaly_tab3, anomaly_tab4 = st.tabs([
            "💸 Financial Anomalies",
            "📊 Volume Anomalies", 
            "⏰ Time-based Anomalies",
            "🎯 Pattern Anomalies"
        ])
        
        with anomaly_tab1:
            self.create_financial_anomalies(grn_df, voucher_df)
        
        with anomaly_tab2:
            self.create_volume_anomalies(grn_df, issue_df)
        
        with anomaly_tab3:
            self.create_time_anomalies(grn_df, issue_df)
        
        with anomaly_tab4:
            self.create_pattern_anomalies(grn_df, issue_df, stock_df)
    
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                    
                    st.plotly_chart(fig, use_container_width=True)
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
                    
                    st.plotly_chart(fig, use_container_width=True)
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                            
                            st.plotly_chart(fig, use_container_width=True)
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
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
                    
                    st.plotly_chart(fig, use_container_width=True)
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
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
                <p>Check for negative stock levels, unusual date patterns, and data inconsistencies</p>
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
                
                st.plotly_chart(fig, use_container_width=True)
        
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
                
                st.plotly_chart(fig, use_container_width=True)
        
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
            
            st.plotly_chart(fig, use_container_width=True)
            
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
                
                st.plotly_chart(fig, use_container_width=True)
        
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
                
                st.plotly_chart(fig, use_container_width=True)
        
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
            
            st.plotly_chart(fig, use_container_width=True)
    
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
                
                st.plotly_chart(fig, use_container_width=True)
        
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
            ("Objective 5: Stock Balances by Year", "objective_5_stock_balances_by_year.csv")
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
