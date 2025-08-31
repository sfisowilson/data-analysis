import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Invalid Voucher References Analysis",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ Invalid Voucher References Analysis")
st.markdown("**Critical Financial Control Issue Identified - R35.8M in Invalid Voucher References**")

# Load data
@st.cache_data
def load_invalid_vouchers():
    return pd.read_csv('output/invalid_voucher_references.csv')

try:
    # Try to load corrected analysis first
    corrected_file = 'output/invalid_voucher_references_corrected.csv'
    if os.path.exists(corrected_file):
        invalid_df = pd.read_csv(corrected_file)
        st.success("📊 **Using Corrected Analysis**: PDF → GRN → Voucher linkage applied")
        
        # Additional corrected analysis features
        if 'has_pdf_link' in invalid_df.columns:
            st.markdown("---")
            st.subheader("🔗 PDF Linkage Analysis")
            
            pdf_summary = invalid_df.groupby('has_pdf_link').agg({
                'grn_no': 'count',
                'nett_grn_amt': 'sum'
            }).round(2)
            pdf_summary.columns = ['Count', 'Total_Value_R']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("PDF-Linked Invalid Vouchers", 
                         f"{pdf_summary.loc['Yes', 'Count']:,.0f}" if 'Yes' in pdf_summary.index else "0")
                st.metric("PDF-Linked Value", 
                         f"R{pdf_summary.loc['Yes', 'Total_Value_R']:,.2f}" if 'Yes' in pdf_summary.index else "R0")
            
            with col2:
                st.metric("Non-PDF-Linked Invalid Vouchers", 
                         f"{pdf_summary.loc['No', 'Count']:,.0f}" if 'No' in pdf_summary.index else "0")
                st.metric("Non-PDF-Linked Value", 
                         f"R{pdf_summary.loc['No', 'Total_Value_R']:,.2f}" if 'No' in pdf_summary.index else "R0")
            
            # PDF linkage chart
            fig_pdf = px.pie(
                values=pdf_summary['Total_Value_R'],
                names=pdf_summary.index,
                title="Invalid Voucher Value by PDF Linkage",
                color_discrete_sequence=['#ff9999', '#66b3ff']
            )
            st.plotly_chart(fig_pdf, use_container_width=True)
            
            st.info("""
            **PDF Linkage Insights:**
            - PDF-linked vouchers have proper document traceability
            - Non-PDF-linked vouchers may be from different transaction streams
            - Higher proportion of non-PDF-linked invalid vouchers suggests system gaps
            """)
    else:
        # Fallback to original analysis
        invalid_df = pd.read_csv('output/invalid_voucher_references.csv')
        st.warning("⚠️ **Using Original Analysis**: Run corrected linkage analysis for updated results")
        st.info("To get corrected analysis, run: `python analyze_corrected_voucher_linkage.py`")
    
    # Key metrics at the top
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Invalid GRN Records", f"{len(invalid_df):,}")
    
    with col2:
        total_value = invalid_df['nett_grn_amt'].sum()
        st.metric("💰 Total Value", f"R{total_value:,.2f}")
    
    with col3:
        unique_vouchers = invalid_df['voucher'].nunique()
        st.metric("📄 Unique Invalid Vouchers", f"{unique_vouchers:,}")
    
    with col4:
        avg_value = invalid_df['nett_grn_amt'].mean()
        st.metric("📈 Average Value", f"R{avg_value:,.2f}")
    
    # High value alert
    st.error(f"🚨 **CRITICAL ALERT**: R{total_value:,.2f} in invalid voucher references requires immediate financial review!")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary Analysis", "🔍 Detailed Breakdown", "📈 Visual Analysis", "📋 Raw Data"])
    
    with tab1:
        st.subheader("📊 Summary by Invalid Reason")
        
        reason_summary = invalid_df.groupby('invalid_reason').agg({
            'grn_no': 'count',
            'nett_grn_amt': 'sum'
        }).round(2)
        reason_summary.columns = ['Count', 'Total_Value_R']
        reason_summary['Percentage'] = (reason_summary['Count'] / len(invalid_df) * 100).round(1)
        reason_summary = reason_summary.sort_values('Total_Value_R', ascending=False)
        
        st.dataframe(reason_summary, use_container_width=True)
        
        # Key insights
        st.subheader("🔑 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **INVI Sequence Issues (R30.4M - 84.8%)**
            - 173 records with timing/sequence gaps
            - Represents bulk of invalid references
            - Likely due to GRN-voucher processing delays
            """)
        
        with col2:
            st.warning("""
            **Special/Manual Vouchers (R5.4M - 15.2%)**
            - 46 records with 999I prefix
            - Manual vouchers not in payment system
            - May require special processing workflow
            """)
    
    with tab2:
        st.subheader("🔍 Detailed Analysis")
        
        # Voucher prefix breakdown
        st.markdown("**Voucher Prefix Analysis:**")
        prefix_summary = invalid_df.groupby('voucher_prefix').agg({
            'grn_no': 'count',
            'nett_grn_amt': 'sum'
        }).round(2)
        prefix_summary.columns = ['Count', 'Total_Value_R']
        st.dataframe(prefix_summary)
        
        # Top suppliers affected
        st.markdown("**Top 10 Suppliers by Invalid Voucher Value:**")
        supplier_impact = invalid_df.groupby('supplier_name').agg({
            'grn_no': 'count',
            'nett_grn_amt': 'sum',
            'voucher': 'nunique'
        }).round(2)
        supplier_impact.columns = ['GRN_Count', 'Total_Value_R', 'Unique_Vouchers']
        supplier_impact = supplier_impact.sort_values('Total_Value_R', ascending=False)
        st.dataframe(supplier_impact.head(10))
        
        # Top individual invalid vouchers
        st.markdown("**Top 10 Individual Invalid Vouchers by Value:**")
        top_invalid = invalid_df.nlargest(10, 'nett_grn_amt')[
            ['voucher', 'supplier_name', 'date', 'nett_grn_amt', 'invalid_reason']
        ]
        st.dataframe(top_invalid)
    
    with tab3:
        st.subheader("📈 Visual Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart by reason
            fig_pie = px.pie(
                values=reason_summary['Count'],
                names=reason_summary.index,
                title="Invalid Voucher Distribution by Reason",
                color_discrete_sequence=['#ff6b6b', '#4ecdc4']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart by value
            fig_bar = px.bar(
                x=reason_summary.index,
                y=reason_summary['Total_Value_R'],
                title="Invalid Voucher Value by Reason (R)",
                color=reason_summary['Total_Value_R'],
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Supplier impact chart
        st.markdown("**Top 15 Suppliers by Invalid Voucher Value:**")
        top_suppliers = supplier_impact.head(15).reset_index()
        fig_supplier = px.bar(
            top_suppliers,
            x='Total_Value_R',
            y='supplier_name',
            orientation='h',
            title="Top Suppliers by Invalid Voucher Value",
            color='Total_Value_R',
            color_continuous_scale='Oranges'
        )
        fig_supplier.update_layout(height=600)
        st.plotly_chart(fig_supplier, use_container_width=True)
        
        # Value distribution histogram
        fig_hist = px.histogram(
            invalid_df,
            x='nett_grn_amt',
            nbins=30,
            title="Distribution of Invalid Voucher Values",
            color_discrete_sequence=['#ff9999']
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab4:
        st.subheader("📋 Raw Data with Filters")
        
        # Filter controls
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
            max_rows = st.number_input("Max rows to display:", value=100, min_value=10, max_value=500)
        
        # Apply filters
        filtered_invalid = invalid_df[
            (invalid_df['invalid_reason'].isin(reason_filter)) &
            (invalid_df['nett_grn_amt'] >= min_value)
        ]
        
        st.info(f"📊 Showing {min(len(filtered_invalid), max_rows):,} of {len(filtered_invalid):,} filtered records")
        
        # Display data
        st.dataframe(filtered_invalid.head(max_rows), use_container_width=True)
        
        # Download button
        csv_data = filtered_invalid.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"invalid_voucher_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Recommendations section
    st.markdown("---")
    st.subheader("💡 Immediate Action Required")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔍 Immediate Investigation:**
        - Review all vouchers >R100,000 individually
        - Verify INVI sequence gaps with finance team
        - Check 999I manual voucher processing
        - Confirm supplier payment status
        """)
    
    with col2:
        st.markdown("""
        **🔄 Process Improvements:**
        - Implement automated voucher validation
        - Set up alerts for sequence gaps
        - Standardize manual voucher processing
        - Schedule weekly invalid voucher reviews
        """)
    
    # Explanations
    st.subheader("❓ Understanding Invalid Voucher Reasons")
    
    with st.expander("⏰ INVI sequence gap or timing issue (R30.4M)"):
        st.markdown("""
        **What it means:** These are INVI-prefixed vouchers that fall within expected sequence ranges but don't exist in the payment system.
        
        **Likely causes:**
        - GRNs created before vouchers are processed
        - Sequence gaps in voucher numbering system
        - Timing delays between GRN and voucher creation
        
        **Action needed:** Review with finance team to verify if vouchers are pending or if sequence gaps exist.
        """)
    
    with st.expander("📝 Special/manual voucher not in payment system (R5.4M)"):
        st.markdown("""
        **What it means:** Vouchers with '999I' prefix indicating special, manual, or temporary vouchers.
        
        **Likely causes:**
        - Manual entries outside standard workflow
        - Special processing requirements
        - Temporary vouchers pending final processing
        
        **Action needed:** Verify if these are legitimate manual entries or require special processing.
        """)

except FileNotFoundError:
    st.error("❌ Invalid voucher references file not found. Please run the analysis first.")
except Exception as e:
    st.error(f"❌ Error loading data: {e}")

# Footer
st.markdown("---")
st.markdown("*Analysis generated from comprehensive stock data processing | Critical financial control issue identified*")
