#!/usr/bin/env python3
"""
CSV Generation Verification Script
Validates that CSV files are generated with corrected business logic
"""

import pandas as pd
import os
from datetime import datetime

def verify_corrected_csv_generation():
    """Verify that CSV files contain corrected business logic columns."""
    
    print("🔍 CSV Generation Verification with Corrected Business Logic")
    print("=" * 70)
    
    verification_results = []
    output_dir = "output"
    
    # Files to verify with expected corrected columns
    files_to_verify = {
        'hr995_grn.csv': ['inv_no_normalized', 'voucher_normalized'],
        'hr995_issue.csv': ['requisition_no_normalized'],
        'hr995_voucher.csv': ['voucher_no_normalized'],
        'individual_hr390_movement_data.csv': ['reference_normalized'],
        'individual_hr185_transactions.csv': ['reference_normalized']
    }
    
    for filename, expected_columns in files_to_verify.items():
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                
                # Check for corrected columns
                has_corrected_columns = all(col in df.columns for col in expected_columns)
                missing_columns = [col for col in expected_columns if col not in df.columns]
                
                verification_results.append({
                    'File': filename,
                    'Exists': True,
                    'Records': len(df),
                    'Has_Corrected_Logic': has_corrected_columns,
                    'Missing_Columns': missing_columns,
                    'Status': '✅ CORRECTED' if has_corrected_columns else '❌ NOT CORRECTED'
                })
                
                # Sample normalized data if available
                if has_corrected_columns:
                    print(f"\n📄 {filename}: ✅ CORRECTED LOGIC APPLIED")
                    print(f"   📊 Records: {len(df):,}")
                    print(f"   🔗 Corrected columns: {', '.join(expected_columns)}")
                    
                    # Show sample of normalized data
                    for col in expected_columns:
                        if col in df.columns:
                            sample_values = df[col].dropna().head(3).tolist()
                            if sample_values:
                                print(f"   📋 {col} samples: {sample_values}")
                else:
                    print(f"\n📄 {filename}: ❌ MISSING CORRECTED LOGIC")
                    print(f"   📊 Records: {len(df):,}")
                    print(f"   ⚠️ Missing columns: {', '.join(missing_columns)}")
                
            except Exception as e:
                verification_results.append({
                    'File': filename,
                    'Exists': True,
                    'Records': 0,
                    'Has_Corrected_Logic': False,
                    'Missing_Columns': expected_columns,
                    'Status': f'❌ ERROR: {str(e)}'
                })
                print(f"\n📄 {filename}: ❌ ERROR reading file: {str(e)}")
        else:
            verification_results.append({
                'File': filename,
                'Exists': False,
                'Records': 0,
                'Has_Corrected_Logic': False,
                'Missing_Columns': expected_columns,
                'Status': '❌ FILE NOT FOUND'
            })
            print(f"\n📄 {filename}: ❌ FILE NOT FOUND")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    corrected_files = sum(1 for result in verification_results if result['Has_Corrected_Logic'])
    total_files = len(verification_results)
    
    print(f"✅ Files with corrected logic: {corrected_files}/{total_files}")
    print(f"❌ Files missing corrected logic: {total_files - corrected_files}/{total_files}")
    
    if corrected_files == total_files:
        print("\n🎉 ALL CSV FILES HAVE CORRECTED BUSINESS LOGIC!")
        print("✅ Ready for advanced analytics with proper data relationships")
    else:
        print(f"\n⚠️ {total_files - corrected_files} files need corrected business logic")
        print("🔄 Run the data processor again to apply corrections")
    
    # Save verification report
    if verification_results:
        verification_df = pd.DataFrame(verification_results)
        verification_file = os.path.join(output_dir, 'csv_verification_report.csv')
        verification_df.to_csv(verification_file, index=False)
        print(f"\n📋 Verification report saved: {verification_file}")
    
    return corrected_files == total_files

def verify_business_relationships():
    """Verify that business relationships are properly implemented."""
    
    print("\n🔗 BUSINESS RELATIONSHIP VERIFICATION")
    print("=" * 70)
    
    try:
        # Load datasets
        grn_df = pd.read_csv('output/hr995_grn.csv')
        issue_df = pd.read_csv('output/hr995_issue.csv')
        voucher_df = pd.read_csv('output/hr995_voucher.csv')
        
        relationship_tests = []
        
        # Test 1: Issue → HR390 linkage potential
        if 'requisition_no_normalized' in issue_df.columns:
            unique_issue_refs = issue_df['requisition_no_normalized'].nunique()
            relationship_tests.append({
                'Relationship': 'Issue → HR390',
                'Source_Column': 'requisition_no_normalized',
                'Unique_References': unique_issue_refs,
                'Status': '✅ Ready for linkage' if unique_issue_refs > 0 else '❌ No references'
            })
        
        # Test 2: GRN → HR185 linkage potential
        if 'inv_no_normalized' in grn_df.columns:
            unique_grn_refs = grn_df['inv_no_normalized'].nunique()
            relationship_tests.append({
                'Relationship': 'GRN → HR185',
                'Source_Column': 'inv_no_normalized',
                'Unique_References': unique_grn_refs,
                'Status': '✅ Ready for linkage' if unique_grn_refs > 0 else '❌ No references'
            })
        
        # Test 3: GRN → Voucher linkage potential
        if 'voucher_normalized' in grn_df.columns and 'voucher_no_normalized' in voucher_df.columns:
            grn_vouchers = set(grn_df['voucher_normalized'].dropna())
            actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
            common_vouchers = grn_vouchers & actual_vouchers
            
            linkage_rate = len(common_vouchers) / len(grn_vouchers) * 100 if len(grn_vouchers) > 0 else 0
            
            relationship_tests.append({
                'Relationship': 'GRN → Voucher',
                'Source_Column': 'voucher_normalized → voucher_no_normalized',
                'Unique_References': f"{len(common_vouchers)}/{len(grn_vouchers)} ({linkage_rate:.1f}%)",
                'Status': '✅ Active linkage' if linkage_rate > 0 else '❌ No linkage'
            })
        
        # Display results
        for test in relationship_tests:
            print(f"🔗 {test['Relationship']}")
            print(f"   📋 Column: {test['Source_Column']}")
            print(f"   📊 References: {test['Unique_References']}")
            print(f"   ✅ {test['Status']}")
            print()
        
        return len([t for t in relationship_tests if '✅' in t['Status']]) == len(relationship_tests)
        
    except Exception as e:
        print(f"❌ Error verifying business relationships: {str(e)}")
        return False

if __name__ == "__main__":
    # Run verification
    csv_corrected = verify_corrected_csv_generation()
    relationships_ready = verify_business_relationships()
    
    print("\n" + "=" * 70)
    print("🏁 FINAL VERIFICATION RESULT")
    print("=" * 70)
    
    if csv_corrected and relationships_ready:
        print("🎉 SUCCESS: All CSV files generated with corrected business logic!")
        print("✅ Business relationships properly implemented")
        print("🚀 Ready for advanced analytics and dashboard use")
    else:
        print("⚠️ INCOMPLETE: Some issues found with corrected business logic")
        print("🔄 Re-run the data processor to fix remaining issues")
    
    print("=" * 70)
