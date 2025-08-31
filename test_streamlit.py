import streamlit as st
import pandas as pd

st.title("Invalid Voucher References Test")

# Load the invalid voucher data
try:
    df = pd.read_csv('output/invalid_voucher_references.csv')
    st.success(f"✅ Loaded {len(df)} invalid voucher records")
    st.metric("Total Value", f"R{df['nett_grn_amt'].sum():,.2f}")
    
    # Show a sample
    st.subheader("Sample Data")
    st.dataframe(df.head())
    
except Exception as e:
    st.error(f"Error loading data: {e}")
