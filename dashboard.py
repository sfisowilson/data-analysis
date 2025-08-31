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
        
    @st.cache_data
    def load_data(_self, filename):
        """Load and cache data files with better error handling."""
        file_path = _self.output_folder / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                # Convert date columns
                for col in df.columns:
                    if 'date' in col.lower() and df[col].dtype == 'object':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                return df
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
                return pd.DataFrame()
        else:
            st.warning(f"File {filename} not found. Please run stock_data_processor.py first.")
            return pd.DataFrame()
    
    def create_overview_metrics(self):
        """Create overview metrics cards."""
        st.header("📊 Stock Data Overview")
        
        # Load master data for overview
        master_df = self.load_data("all_stock_data.csv")
        
        if not master_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Records",
                    value=f"{len(master_df):,}",
                    delta="All processed data"
                )
            
            with col2:
                unique_files = master_df['source_file'].nunique() if 'source_file' in master_df.columns else 0
                st.metric(
                    label="Source Files",
                    value=unique_files,
                    delta="Multiple formats"
                )
            
            with col3:
                columns_count = len(master_df.columns)
                st.metric(
                    label="Data Points",
                    value=f"{columns_count} columns",
                    delta="Comprehensive data"
                )
            
            with col4:
                # Calculate data completeness
                completeness = (1 - master_df.isnull().sum().sum() / (len(master_df) * len(master_df.columns))) * 100
                st.metric(
                    label="Data Quality",
                    value=f"{completeness:.1f}%",
                    delta="Completeness score"
                )
    
    def create_financial_analysis(self):
        """Create financial analysis charts."""
        st.header("💰 Financial Analysis")
        
        grn_df = self.load_data("hr995_grn.csv")
        voucher_df = self.load_data("hr995_voucher.csv")
        
        if not grn_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # GRN Value Analysis
                if 'nett_grn_amt' in grn_df.columns:
                    grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
                    total_grn_value = grn_df['nett_grn_amt'].sum()
                    
                    st.subheader("GRN Financial Summary")
                    st.metric(
                        label="Total GRN Value",
                        value=f"R{total_grn_value:,.2f}",
                        delta="Goods Received"
                    )
                    
                    # Top value transactions
                    top_grn = grn_df.nlargest(10, 'nett_grn_amt')[['supplier_name', 'nett_grn_amt', 'description']]
                    if not top_grn.empty:
                        fig = px.bar(
                            top_grn,
                            x='nett_grn_amt',
                            y='supplier_name',
                            title="Top 10 GRN Transactions by Value",
                            labels={'nett_grn_amt': 'GRN Amount (R)', 'supplier_name': 'Supplier'},
                            orientation='h'
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Monthly GRN trend
                if 'date' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
                    grn_df['date'] = pd.to_datetime(grn_df['date'], errors='coerce')
                    grn_df['month_year'] = grn_df['date'].dt.to_period('M').astype(str)
                    
                    monthly_grn = grn_df.groupby('month_year')['nett_grn_amt'].sum().reset_index()
                    monthly_grn = monthly_grn.sort_values('month_year')
                    
                    if len(monthly_grn) > 1:
                        fig = px.line(
                            monthly_grn,
                            x='month_year',
                            y='nett_grn_amt',
                            title="Monthly GRN Value Trend",
                            labels={'nett_grn_amt': 'GRN Amount (R)', 'month_year': 'Month'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, width="stretch")
    
    def create_supplier_analysis(self):
        """Create supplier performance analysis."""
        st.header("🏪 Supplier Performance Analysis")
        
        grn_df = self.load_data("hr995_grn.csv")
        supplier_df = self.load_data("suppliers.csv")
        
        if not grn_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top suppliers by transaction count
                if 'supplier_name' in grn_df.columns:
                    supplier_counts = grn_df['supplier_name'].value_counts().head(15)
                    
                    fig = px.pie(
                        values=supplier_counts.values,
                        names=supplier_counts.index,
                        title="Top 15 Suppliers by Transaction Count"
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Supplier value distribution
                if 'supplier_name' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
                    grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
                    supplier_values = grn_df.groupby('supplier_name')['nett_grn_amt'].sum().nlargest(10)
                    
                    fig = px.treemap(
                        names=supplier_values.index,
                        values=supplier_values.values,
                        title="Top 10 Suppliers by Total Value"
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, width="stretch")
        
        # Supplier performance table
        if not grn_df.empty and 'supplier_name' in grn_df.columns:
            st.subheader("Supplier Performance Summary")
            
            grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
            supplier_summary = grn_df.groupby('supplier_name').agg({
                'grn_no': 'count',
                'nett_grn_amt': ['sum', 'mean'],
                'quantity': 'sum'
            }).round(2)
            
            supplier_summary.columns = ['Transaction_Count', 'Total_Value', 'Avg_Value', 'Total_Quantity']
            supplier_summary = supplier_summary.sort_values('Total_Value', ascending=False).head(20)
            
            st.dataframe(supplier_summary, width="stretch")
    
    def create_stock_movement_analysis(self):
        """Create stock movement analysis charts."""
        st.header("📦 Stock Movement Analysis")
        
        audit_df = self.load_data("objective_2_stock_audit_trail.csv")
        issue_df = self.load_data("hr995_issue.csv")
        grn_df = self.load_data("hr995_grn.csv")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction type distribution
            if not audit_df.empty and 'transaction_type' in audit_df.columns:
                transaction_counts = audit_df['transaction_type'].value_counts()
                
                fig = px.bar(
                    x=transaction_counts.index,
                    y=transaction_counts.values,
                    title="Stock Movement by Transaction Type",
                    labels={'x': 'Transaction Type', 'y': 'Count'},
                    color=transaction_counts.values,
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Daily stock movement trend
            if not audit_df.empty and 'date' in audit_df.columns:
                audit_df['date'] = pd.to_datetime(audit_df['date'], errors='coerce')
                audit_df['date_only'] = audit_df['date'].dt.date
                
                daily_movements = audit_df.groupby('date_only').size().reset_index(name='count')
                daily_movements = daily_movements.sort_values('date_only').tail(30)  # Last 30 days
                
                if not daily_movements.empty:
                    fig = px.line(
                        daily_movements,
                        x='date_only',
                        y='count',
                        title="Daily Stock Movements (Last 30 Days)",
                        labels={'date_only': 'Date', 'count': 'Number of Movements'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width="stretch")
        
        # Stock movement heatmap
        if not audit_df.empty and 'date' in audit_df.columns:
            st.subheader("Stock Movement Heatmap")
            
            audit_df['date'] = pd.to_datetime(audit_df['date'], errors='coerce')
            audit_df['hour'] = audit_df['date'].dt.hour
            audit_df['day_of_week'] = audit_df['date'].dt.day_name()
            
            heatmap_data = audit_df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
            
            if not heatmap_data.empty:
                fig = px.imshow(
                    heatmap_data.values,
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    title="Stock Movement Heatmap (Day vs Hour)",
                    labels={'x': 'Hour of Day', 'y': 'Day of Week', 'color': 'Movement Count'},
                    aspect='auto'
                )
                st.plotly_chart(fig, width="stretch")
    
    def create_inventory_analysis(self):
        """Create inventory and stock balance analysis."""
        st.header("📋 Inventory Analysis")
        
        stock_df = self.load_data("stock_adjustments.csv")
        hr995_df = self.load_data("objective_3_hr995_report.csv")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not hr995_df.empty:
                # HR995 report breakdown
                if 'hr995_type' in hr995_df.columns:
                    hr995_breakdown = hr995_df['hr995_type'].value_counts()
                    
                    fig = px.donut(
                        values=hr995_breakdown.values,
                        names=hr995_breakdown.index,
                        title="HR995 Report Breakdown"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Stock value distribution
            if not stock_df.empty and any(col in stock_df.columns for col in ['value_on_hand', 'amount', 'unit_price']):
                value_col = None
                for col in ['value_on_hand', 'amount', 'unit_price']:
                    if col in stock_df.columns:
                        value_col = col
                        break
                
                if value_col:
                    stock_df[value_col] = pd.to_numeric(stock_df[value_col], errors='coerce')
                    stock_values = stock_df[value_col].dropna()
                    
                    if not stock_values.empty:
                        fig = px.histogram(
                            stock_values,
                            title=f"Stock Value Distribution ({value_col})",
                            labels={'value': value_col, 'count': 'Frequency'},
                            nbins=20
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, width="stretch")
    
    def create_trends_analysis(self):
        """Create trend analysis over time."""
        st.header("📈 Trends Analysis")
        
        # Load multiple datasets for trend analysis
        grn_df = self.load_data("hr995_grn.csv")
        issue_df = self.load_data("hr995_issue.csv")
        voucher_df = self.load_data("hr995_voucher.csv")
        
        # Create combined trends chart
        if not grn_df.empty or not issue_df.empty or not voucher_df.empty:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Monthly Transaction Counts', 'Quarterly Value Trends', 
                              'Supplier Performance Over Time', 'Stock Movement Patterns'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Monthly transaction counts
            for df, name, color in [(grn_df, 'GRN', 'blue'), (issue_df, 'Issue', 'red'), (voucher_df, 'Voucher', 'green')]:
                if not df.empty and 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df['month'] = df['date'].dt.to_period('M').astype(str)
                    monthly_counts = df.groupby('month').size()
                    
                    fig.add_trace(
                        go.Scatter(x=monthly_counts.index, y=monthly_counts.values, 
                                 name=f'{name} Count', line=dict(color=color)),
                        row=1, col=1
                    )
            
            st.plotly_chart(fig, width="stretch")
    
    def create_data_quality_report(self):
        """Create data quality analysis."""
        st.header("🔍 Data Quality Report")
        
        master_df = self.load_data("all_stock_data.csv")
        
        if not master_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Missing data analysis
                missing_data = master_df.isnull().sum()
                missing_percentage = (missing_data / len(master_df)) * 100
                missing_df = pd.DataFrame({
                    'Column': missing_data.index,
                    'Missing_Count': missing_data.values,
                    'Missing_Percentage': missing_percentage.values
                }).sort_values('Missing_Percentage', ascending=False).head(20)
                
                fig = px.bar(
                    missing_df,
                    x='Missing_Percentage',
                    y='Column',
                    title="Top 20 Columns by Missing Data %",
                    orientation='h'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                # File source distribution
                if 'source_file' in master_df.columns:
                    file_counts = master_df['source_file'].value_counts()
                    
                    fig = px.bar(
                        x=file_counts.values,
                        y=file_counts.index,
                        title="Records by Source File",
                        orientation='h',
                        labels={'x': 'Record Count', 'y': 'Source File'}
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, width="stretch")

def main():
    """Main function to run the dashboard."""
    
    # Dashboard title and description
    st.title("📊 Stock Data Analytics Dashboard")
    st.markdown("""
    Welcome to the Stock Data Analytics Dashboard! This interactive application provides comprehensive 
    visualizations and insights from your stock data processing pipeline.
    """)
    
    # Initialize dashboard
    dashboard = StockDataDashboard()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        [
            "📊 Overview",
            "💰 Financial Analysis", 
            "🏪 Supplier Performance",
            "📦 Stock Movements",
            "📋 Inventory Analysis",
            "📈 Trends Analysis",
            "🔍 Data Quality"
        ]
    )
    
    # Page routing
    if page == "📊 Overview":
        dashboard.create_overview_metrics()
        st.markdown("---")
        st.markdown("### Quick Statistics")
        
        # Load key metrics
        grn_df = dashboard.load_data("hr995_grn.csv")
        if not grn_df.empty and 'nett_grn_amt' in grn_df.columns:
            grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
            total_value = grn_df['nett_grn_amt'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total GRN Value", f"R{total_value:,.2f}")
            with col2:
                st.metric("Total GRN Transactions", f"{len(grn_df):,}")
            with col3:
                avg_value = grn_df['nett_grn_amt'].mean()
                st.metric("Average GRN Value", f"R{avg_value:,.2f}")
    
    elif page == "💰 Financial Analysis":
        dashboard.create_financial_analysis()
    
    elif page == "🏪 Supplier Performance":
        dashboard.create_supplier_analysis()
    
    elif page == "📦 Stock Movements":
        dashboard.create_stock_movement_analysis()
    
    elif page == "📋 Inventory Analysis":
        dashboard.create_inventory_analysis()
    
    elif page == "📈 Trends Analysis":
        dashboard.create_trends_analysis()
    
    elif page == "🔍 Data Quality":
        dashboard.create_data_quality_report()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Stock Data Analytics Dashboard | Generated from stock_data_processor.py output</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
