import pandas as pd

# Load invalid voucher references
df = pd.read_csv('output/invalid_voucher_references.csv')

print("=== INVALID VOUCHER REFERENCES SUMMARY ===")
print(f"Total Records: {len(df)}")
print(f"Total Value: R{df['nett_grn_amt'].sum():,.2f}")
print(f"Unique Vouchers: {df['voucher'].nunique()}")
print(f"Average Value: R{df['nett_grn_amt'].mean():,.2f}")

print("\n=== BY REASON ===")
reason_summary = df.groupby('invalid_reason').agg({
    'grn_no': 'count',
    'nett_grn_amt': 'sum'
}).round(2)
reason_summary.columns = ['Count', 'Total_Value_R']
print(reason_summary)

print("\n=== BY PREFIX ===")
prefix_summary = df.groupby('voucher_prefix').agg({
    'grn_no': 'count', 
    'nett_grn_amt': 'sum'
}).round(2)
prefix_summary.columns = ['Count', 'Total_Value_R']
print(prefix_summary)

print("\n=== TOP 5 SUPPLIERS BY INVALID VALUE ===")
supplier_summary = df.groupby('supplier_name')['nett_grn_amt'].sum().sort_values(ascending=False).head()
for supplier, value in supplier_summary.items():
    print(f"{supplier}: R{value:,.2f}")

print("\n=== SAMPLE RECORDS ===")
print(df[['voucher', 'supplier_name', 'nett_grn_amt', 'invalid_reason']].head())
