import pandas as pd
import os

print("=== ANALYZING LEADING ZEROS ISSUE ===")

# Load PDF data if it exists
if os.path.exists('output/individual_hr185_transactions.csv'):
    hr185_df = pd.read_csv('output/individual_hr185_transactions.csv')
    print(f"📄 HR185 PDF records: {len(hr185_df)}")
    
    pdf_refs = hr185_df['reference'].dropna().astype(str)
    refs_with_zeros = [ref for ref in pdf_refs if ref.startswith('0')]
    
    print(f"📊 PDF references with leading zeros: {len(refs_with_zeros)}")
    print("Sample refs with leading zeros:", refs_with_zeros[:5])
    
    # Strip leading zeros
    refs_stripped = [ref.lstrip('0') for ref in refs_with_zeros if ref.lstrip('0')]
    print("Same refs with leading zeros stripped:", refs_stripped[:5])
else:
    print("⚠️ No HR185 PDF data found")
    refs_stripped = []

# Load voucher data
voucher_df = pd.read_csv('output/hr995_voucher.csv')
grn_df = pd.read_csv('output/hr995_grn.csv')

print(f"\n📊 Payment voucher records: {len(voucher_df)}")
print(f"📊 GRN records: {len(grn_df)}")

# Get all voucher numbers from payment system
all_voucher_numbers = set(voucher_df['voucher_no'].dropna().astype(str))

# Check if stripped PDF references match voucher numbers
if refs_stripped:
    matches = [ref for ref in refs_stripped if ref in all_voucher_numbers]
    print(f"\n🎯 Potential matches after stripping leading zeros: {len(matches)}")
    if matches:
        print("Sample matches:", matches[:5])

# Check GRN vouchers for potential leading zero issues
grn_vouchers = grn_df['voucher'].dropna().astype(str)
grn_numeric = [v for v in grn_vouchers if v.replace('INVI', '').replace('999I', '').isdigit()]

print(f"\n📋 GRN vouchers that might have numeric components: {len(grn_numeric)}")
if grn_numeric:
    print("Sample GRN numeric vouchers:", grn_numeric[:5])

# Check if there are any vouchers in GRN that look like they should have leading zeros
print("\n=== CHECKING FOR POTENTIAL ZERO-PADDING ISSUES ===")

# Extract numeric parts from GRN vouchers and see if they could match PDF refs with leading zeros
invi_vouchers = [v for v in grn_vouchers if v.startswith('INVI')]
invi_numbers = []
for voucher in invi_vouchers:
    try:
        num_part = voucher.replace('INVI', '')
        if num_part.isdigit():
            invi_numbers.append(int(num_part))
    except:
        pass

if invi_numbers:
    print(f"📈 INVI voucher number range: {min(invi_numbers)} to {max(invi_numbers)}")
    
    # Check if any PDF references (stripped of zeros) fall in this range
    if refs_stripped:
        pdf_numbers = []
        for ref in refs_stripped:
            try:
                if ref.isdigit():
                    pdf_numbers.append(int(ref))
            except:
                pass
        
        if pdf_numbers:
            print(f"📈 PDF reference number range: {min(pdf_numbers)} to {max(pdf_numbers)}")
            
            # Check for overlaps
            invi_set = set(invi_numbers)
            pdf_set = set(pdf_numbers)
            overlaps = invi_set & pdf_set
            
            print(f"🔍 Overlapping numbers: {len(overlaps)}")
            if overlaps:
                print(f"Sample overlaps: {sorted(list(overlaps))[:10]}")

print("\n=== RECOMMENDATIONS ===")
print("1. 🔧 Normalize all voucher references by stripping leading zeros")
print("2. 🔄 Re-run invalid voucher analysis with normalized references")
print("3. 📊 Check if INVI numbers should be zero-padded to match PDF format")
print("4. 🎯 Implement reference normalization in voucher matching logic")
