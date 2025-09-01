#!/usr/bin/env python3
"""
Clean Streamlit Dashboard for Stock Management Analytics
Created: August 31, 2025
Purpose: Error-free dashboard with unique plotly chart keys
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import logging
from datetime import datetime, timedelta
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Stock Management Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    .stApp > div:first-child {
        margin-top: -75px;
    }
</style>
""", unsafe_allow_html=True)

class StockDashboard:
    """Clean, simple dashboard with unique chart keys."""
    
    def __init__(self):
        self.output_folder = Path("output")
        self.data_cache = {}
        
    def load_data(self, filename):
        """Load and cache data files."""
        if filename not in self.data_cache:
            file_path = self.output_folder / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    self.data_cache[filename] = df
                    return df
                except Exception as e:
                    st.error(f"Error loading {filename}: {str(e)}")
                    return pd.DataFrame()
            else:
                st.warning(f"File not found: {filename}")
                return pd.DataFrame()
        return self.data_cache[filename]
    
    def clean_numeric_data(self, df, column):
        """Clean and convert numeric columns."""
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')
            df = df.dropna(subset=[column])
        return df
    
    def normalize_reference(self, ref):
        """Normalize reference numbers for proper linking."""
        if pd.isna(ref):
            return ""
        ref_str = str(ref).strip()
        if ref_str.replace('.', '').replace('-', '').isdigit():
            return ref_str.zfill(6)
        return ref_str
    
    def create_overview_metrics(self):
        """Create overview metrics section."""
        st.header("📊 Stock Management Overview")
        
        # Load key datasets
        grn_df = self.load_data("hr995_grn.csv")
        issue_df = self.load_data("hr995_issue.csv")
        voucher_df = self.load_data("hr995_voucher.csv")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("GRN Records", f"{len(grn_df):,}" if not grn_df.empty else "0")
        
        with col2:
            st.metric("Issue Records", f"{len(issue_df):,}" if not issue_df.empty else "0")
        
        with col3:
            st.metric("Voucher Records", f"{len(voucher_df):,}" if not voucher_df.empty else "0")
        
        with col4:
            if not grn_df.empty and 'nett_grn_amt' in grn_df.columns:
                grn_df = self.clean_numeric_data(grn_df, 'nett_grn_amt')
                total_value = grn_df['nett_grn_amt'].sum()
                st.metric("Total GRN Value", f"R{total_value:,.2f}")
            else:
                st.metric("Total GRN Value", "R0.00")
    
    def create_financial_analysis(self):
        """Create financial analysis section."""
        st.header("💰 Financial Analysis")
        
        grn_df = self.load_data("hr995_grn.csv")
        voucher_df = self.load_data("hr995_voucher.csv")
        
        if grn_df.empty:
            st.warning("No GRN data available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("GRN Value Distribution")
            if 'nett_grn_amt' in grn_df.columns:
                grn_df = self.clean_numeric_data(grn_df, 'nett_grn_amt')
                
                fig = px.histogram(
                    grn_df, 
                    x='nett_grn_amt', 
                    nbins=50,
                    title='GRN Amount Distribution',
                    labels={'nett_grn_amt': 'GRN Amount (R)', 'count': 'Frequency'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key="grn_value_histogram")
        
        with col2:
            st.subheader("Top Suppliers by Value")
            if 'supplier_name' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
                supplier_totals = grn_df.groupby('supplier_name')['nett_grn_amt'].sum().nlargest(10)
                
                fig = px.bar(
                    x=supplier_totals.values,
                    y=supplier_totals.index,
                    orientation='h',
                    title='Top 10 Suppliers by Total Value',
                    labels={'x': 'Total Value (R)', 'y': 'Supplier'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key="top_suppliers_bar")
        
        # Financial trends
        if 'date' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
            st.subheader("Financial Trends")
            grn_df['date'] = pd.to_datetime(grn_df['date'], errors='coerce')
            grn_df = grn_df.dropna(subset=['date'])
            
            if not grn_df.empty:
                grn_df['month'] = grn_df['date'].dt.to_period('M').astype(str)
                monthly_trends = grn_df.groupby('month').agg({
                    'nett_grn_amt': ['sum', 'count', 'mean']
                }).round(2)
                monthly_trends.columns = ['Total_Value', 'Transaction_Count', 'Average_Value']
                monthly_trends = monthly_trends.reset_index()
                
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Monthly Total Value', 'Monthly Transaction Count'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=monthly_trends['month'],
                        y=monthly_trends['Total_Value'],
                        mode='lines+markers',
                        name='Total Value'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=monthly_trends['month'],
                        y=monthly_trends['Transaction_Count'],
                        name='Transaction Count'
                    ),
                    row=1, col=2
                )
                
                fig.update_layout(height=400, showlegend=False)
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True, key="monthly_trends_subplot")
    
    def create_supplier_analysis(self):
        """Create supplier analysis section."""
        st.header("🏪 Supplier Analysis")
        
        grn_df = self.load_data("hr995_grn.csv")
        
        if grn_df.empty or 'supplier_name' not in grn_df.columns:
            st.warning("No supplier data available")
            return
        
        # Supplier performance metrics
        if 'nett_grn_amt' in grn_df.columns:
            grn_df = self.clean_numeric_data(grn_df, 'nett_grn_amt')
            
            supplier_metrics = grn_df.groupby('supplier_name').agg({
                'nett_grn_amt': ['sum', 'count', 'mean']
            }).round(2)
            supplier_metrics.columns = ['Total_Value', 'Transaction_Count', 'Average_Value']
            supplier_metrics = supplier_metrics.reset_index().sort_values('Total_Value', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Supplier Performance Bubble Chart")
                fig = px.scatter(
                    supplier_metrics.head(20),
                    x='Transaction_Count',
                    y='Average_Value',
                    size='Total_Value',
                    hover_name='supplier_name',
                    title='Supplier Performance: Volume vs Value',
                    labels={
                        'Transaction_Count': 'Number of Transactions',
                        'Average_Value': 'Average Transaction Value (R)',
                        'Total_Value': 'Total Value (R)'
                    }
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True, key="supplier_bubble_chart")
            
            with col2:
                st.subheader("Supplier Value Distribution")
                top_suppliers = supplier_metrics.head(10)
                
                fig = px.pie(
                    top_suppliers,
                    values='Total_Value',
                    names='supplier_name',
                    title='Top 10 Suppliers - Value Share'
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True, key="supplier_pie_chart")
            
            # Supplier details table
            st.subheader("Supplier Performance Details")
            st.dataframe(
                supplier_metrics.head(20)[['supplier_name', 'Total_Value', 'Transaction_Count', 'Average_Value']],
                use_container_width=True
            )
    
    def create_inventory_analysis(self):
        """Create inventory analysis section."""
        st.header("📦 Inventory Analysis")
        
        grn_df = self.load_data("hr995_grn.csv")
        issue_df = self.load_data("hr995_issue.csv")
        
        if grn_df.empty and issue_df.empty:
            st.warning("No inventory data available")
            return
        
        col1, col2 = st.columns(2)
        
        # Stock movements
        if not grn_df.empty and not issue_df.empty:
            with col1:
                st.subheader("Stock Movement Summary")
                
                grn_items = len(grn_df.get('item_no', grn_df.get('item_code', pd.Series())))
                issue_items = len(issue_df.get('item_no', issue_df.get('item_code', pd.Series())))
                
                movement_data = pd.DataFrame({
                    'Movement_Type': ['Received (GRN)', 'Issued'],
                    'Count': [grn_items, issue_items]
                })
                
                fig = px.bar(
                    movement_data,
                    x='Movement_Type',
                    y='Count',
                    title='Stock Movement Comparison',
                    color='Movement_Type'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key="stock_movement_bar")
        
        # Category analysis
        if 'description' in grn_df.columns:
            with col2:
                st.subheader("Item Category Analysis")
                
                # Extract categories from descriptions
                grn_df['category'] = grn_df['description'].str.extract(r'^([A-Z]+)', expand=False).fillna('OTHER')
                category_counts = grn_df['category'].value_counts().head(10)
                
                fig = px.bar(
                    x=category_counts.index,
                    y=category_counts.values,
                    title='Top 10 Item Categories',
                    labels={'x': 'Category', 'y': 'Number of Items'}
                )
                fig.update_layout(height=400)
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True, key="category_analysis_bar")
    
    def create_data_relationships(self):
        """Create data relationship analysis."""
        st.header("🔗 Data Relationships")
        
        grn_df = self.load_data("hr995_grn.csv")
        voucher_df = self.load_data("hr995_voucher.csv")
        hr185_df = self.load_data("individual_hr185_transactions.csv")
        hr390_df = self.load_data("individual_hr390_movement_data.csv")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Linkage Summary")
            
            # Calculate linkage statistics
            linkage_stats = []
            
            if not grn_df.empty and not voucher_df.empty:
                # GRN to Voucher linkage
                if 'voucher_normalized' in grn_df.columns and 'voucher_no_normalized' in voucher_df.columns:
                    grn_vouchers = grn_df['voucher_normalized'].dropna().unique()
                    voucher_numbers = voucher_df['voucher_no_normalized'].dropna().unique()
                    matched = len(set(grn_vouchers) & set(voucher_numbers))
                    linkage_stats.append({
                        'Relationship': 'GRN → Voucher',
                        'GRN_Records': len(grn_vouchers),
                        'Target_Records': len(voucher_numbers),
                        'Matched': matched,
                        'Match_Rate': f"{(matched/len(grn_vouchers)*100):.1f}%" if len(grn_vouchers) > 0 else "0%"
                    })
            
            if not grn_df.empty and not hr185_df.empty:
                # GRN to HR185 linkage
                if 'inv_no_normalized' in grn_df.columns and 'reference_normalized' in hr185_df.columns:
                    grn_refs = grn_df['inv_no_normalized'].dropna().unique()
                    hr185_refs = hr185_df['reference_normalized'].dropna().unique()
                    matched = len(set(grn_refs) & set(hr185_refs))
                    linkage_stats.append({
                        'Relationship': 'GRN → HR185',
                        'GRN_Records': len(grn_refs),
                        'Target_Records': len(hr185_refs),
                        'Matched': matched,
                        'Match_Rate': f"{(matched/len(grn_refs)*100):.1f}%" if len(grn_refs) > 0 else "0%"
                    })
            
            if linkage_stats:
                linkage_df = pd.DataFrame(linkage_stats)
                st.dataframe(linkage_df, use_container_width=True)
            else:
                st.info("No relationship data available")
        
        with col2:
            st.subheader("Data Quality Metrics")
            
            quality_metrics = []
            
            for filename, description in [
                ("hr995_grn.csv", "GRN Records"),
                ("hr995_voucher.csv", "Voucher Records"),
                ("individual_hr185_transactions.csv", "HR185 Transactions"),
                ("individual_hr390_movement_data.csv", "HR390 Movements")
            ]:
                df = self.load_data(filename)
                if not df.empty:
                    quality_metrics.append({
                        'Dataset': description,
                        'Records': len(df),
                        'Columns': len(df.columns),
                        'Completeness': f"{((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%"
                    })
            
            if quality_metrics:
                quality_df = pd.DataFrame(quality_metrics)
                st.dataframe(quality_df, use_container_width=True)
    
    def run_dashboard(self):
        """Run the main dashboard."""
        st.title("📊 Stock Management Analytics Dashboard")
        st.markdown("---")
        
        # Sidebar navigation
        st.sidebar.title("📋 Navigation")
        page = st.sidebar.selectbox(
            "Choose Analysis",
            ["Overview", "Financial Analysis", "Supplier Analysis", "Inventory Analysis", "Data Relationships"]
        )
        
        # Main content
        if page == "Overview":
            self.create_overview_metrics()
        elif page == "Financial Analysis":
            self.create_financial_analysis()
        elif page == "Supplier Analysis":
            self.create_supplier_analysis()
        elif page == "Inventory Analysis":
            self.create_inventory_analysis()
        elif page == "Data Relationships":
            self.create_data_relationships()
        
        # Footer
        st.markdown("---")
        st.markdown(
            f"""
            <div style='text-align: center; color: #666; font-size: 0.8em;'>
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Data source: CSV files with corrected business logic
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    """Main function to run the dashboard."""
    dashboard = StockDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
