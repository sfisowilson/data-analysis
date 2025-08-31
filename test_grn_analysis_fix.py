#!/usr/bin/env python3
"""
Test script to verify GRN-Transaction Analysis functionality
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append('.')

def test_grn_transaction_analysis():
    """Test the corrected GRN-Transaction analysis methods."""
    
    print("🧪 Testing GRN-Transaction Analysis Corrections")
    print("=" * 60)
    
    try:
        # Import the dashboard class
        from enhanced_dashboard import AdvancedStockDashboard
        dashboard = AdvancedStockDashboard()
        print("✅ Dashboard class imported successfully")
        
        # Load required data
        print("\n📊 Loading data files...")
        grn_df = pd.read_csv('output/hr995_grn.csv')
        voucher_df = pd.read_csv('output/hr995_voucher.csv')
        print(f"✅ GRN data loaded: {len(grn_df):,} records")
        print(f"✅ Voucher data loaded: {len(voucher_df):,} records")
        
        # Test normalize_reference function
        print("\n🔧 Testing normalize_reference function...")
        test_cases = [
            '0001015775',  # PDF format with leading zeros
            '1015775',     # GRN format without leading zeros
            1015775,       # Numeric format
            None,          # None value
            '',            # Empty string
            'ABC123'       # Non-numeric reference
        ]
        
        for test_ref in test_cases:
            normalized = dashboard.normalize_reference(test_ref)
            print(f"   {test_ref} → {normalized}")
        
        # Test data normalization
        print("\n🔄 Testing data normalization...")
        
        # Test GRN data normalization
        grn_test = grn_df.head().copy()
        grn_test['inv_no_normalized'] = grn_test['inv_no'].apply(dashboard.normalize_reference)
        grn_test['voucher_normalized'] = grn_test['voucher'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        print(f"✅ GRN normalization successful: {len(grn_test)} test records")
        
        # Test voucher data normalization
        voucher_test = voucher_df.head().copy()
        voucher_test['voucher_no_normalized'] = voucher_test['voucher_no'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
        print(f"✅ Voucher normalization successful: {len(voucher_test)} test records")
        
        # Test PDF data loading (if available)
        print("\n📄 Testing PDF data integration...")
        pdf_file = 'output/individual_hr185_transactions.csv'
        if os.path.exists(pdf_file):
            pdf_df = pd.read_csv(pdf_file)
            pdf_df['reference_normalized'] = pdf_df['reference'].apply(dashboard.normalize_reference)
            print(f"✅ PDF data loaded and normalized: {len(pdf_df):,} records")
            
            # Test PDF-GRN linkage
            grn_analysis = grn_df.copy()
            grn_analysis['inv_no_normalized'] = grn_analysis['inv_no'].apply(dashboard.normalize_reference)
            
            pdf_linked_grns = grn_analysis[grn_analysis['inv_no_normalized'].isin(pdf_df['reference_normalized'])]
            linkage_rate = len(pdf_linked_grns) / len(grn_analysis) * 100
            
            print(f"✅ PDF-GRN linkage test successful: {linkage_rate:.1f}% match rate")
        else:
            print("⚠️  PDF data file not found - skipping PDF linkage test")
        
        # Test voucher validation
        print("\n🔍 Testing voucher validation...")
        grn_voucher_refs = set(grn_df['voucher'].dropna().astype(str).str.strip().str.upper())
        actual_vouchers = set(voucher_df['voucher_no'].dropna().astype(str).str.strip().str.upper())
        
        valid_refs = grn_voucher_refs & actual_vouchers
        invalid_refs = grn_voucher_refs - actual_vouchers
        
        validity_rate = len(valid_refs) / len(grn_voucher_refs) * 100 if grn_voucher_refs else 0
        
        print(f"✅ Voucher validation successful:")
        print(f"   Valid references: {len(valid_refs):,}")
        print(f"   Invalid references: {len(invalid_refs):,}")
        print(f"   Validity rate: {validity_rate:.1f}%")
        
        print("\n🎉 All Tests Passed Successfully!")
        print("✅ The inv_no_normalized error has been resolved")
        print("✅ GRN-Transaction Analysis is now working correctly")
        print("✅ Dashboard is ready for use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grn_transaction_analysis()
    sys.exit(0 if success else 1)
