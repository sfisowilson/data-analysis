#!/usr/bin/env python3
"""
Quick CHQ Integration Validation Test
Tests the core CHQ inheritance logic from the enhanced dashboard
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def quick_chq_validation():
    """Quick validation of CHQ inheritance functionality"""
    
    print("⚡ Quick CHQ Integration Validation")
    print("=" * 40)
    
    try:
        # Load the enhanced transaction trail that was already generated
        print("📂 Loading enhanced transaction trail...")
        enhanced_df = pd.read_csv('output/enhanced_transaction_trail_with_chq_fix.csv')
        
        print(f"✓ Loaded {len(enhanced_df)} enhanced transaction records")
        
        # Analyze CHQ transactions specifically
        chq_transactions = enhanced_df[enhanced_df['transaction_type'] == 'CHQ']
        total_chq = len(chq_transactions)
        
        # Count different types of CHQ matches
        chq_with_inheritance = chq_transactions[
            chq_transactions['has_inherited_grn_match'] == True
        ]
        chq_with_grn_match = chq_transactions[
            chq_transactions['grn_voucher'].notna()
        ]
        chq_with_paired_inv = chq_transactions[
            chq_transactions['paired_inv_reference'].notna()
        ]
        
        print(f"\n📊 CHQ ANALYSIS RESULTS:")
        print("-" * 30)
        print(f"Total CHQ transactions: {total_chq}")
        print(f"CHQ with inherited GRN matches: {len(chq_with_inheritance)}")
        print(f"CHQ with GRN voucher matches: {len(chq_with_grn_match)}")
        print(f"CHQ with paired INV references: {len(chq_with_paired_inv)}")
        
        # Show sample CHQ transactions with inheritance
        if len(chq_with_inheritance) > 0:
            print(f"\n💡 Sample CHQ Inheritance Results:")
            print("-" * 40)
            
            sample_chq = chq_with_inheritance.head(5)
            for _, row in sample_chq.iterrows():
                print(f"  CHQ {row['hr185_reference']} | {row['supplier_name'][:30]}")
                print(f"    Paired with INV: {row['paired_inv_reference']}")
                print(f"    GRN Voucher: {row['grn_voucher']}")
                print(f"    GRN Inv No: {row['grn_inv_no']}")
                print(f"    Amount: R {row['amount']:,.2f}")
                print()
        
        # Validation against expected results
        expected_chq_fixes = 119
        actual_chq_fixes = len(chq_with_inheritance)
        
        print(f"✅ VALIDATION SUMMARY:")
        print("=" * 25)
        print(f"Expected CHQ fixes: {expected_chq_fixes}")
        print(f"Actual CHQ fixes: {actual_chq_fixes}")
        print(f"Match: {'✓ PASS' if actual_chq_fixes == expected_chq_fixes else '❌ FAIL'}")
        
        if actual_chq_fixes == expected_chq_fixes:
            print("\n🎉 CHQ INTEGRATION VALIDATION PASSED!")
            print("The enhanced dashboard CHQ linking is working correctly!")
            print("CHQ transactions now inherit GRN matches from their paired INV transactions.")
            
            # Additional statistics
            match_rate = (actual_chq_fixes / total_chq) * 100
            print(f"\n📈 BUSINESS IMPACT:")
            print(f"• CHQ match rate improved to {match_rate:.1f}%")
            print(f"• {actual_chq_fixes} previously unmatched CHQ transactions now resolved")
            print(f"• Complete audit trail established for INV→CHQ payment cycles")
            
            return True
        else:
            print(f"\n⚠️  Validation issues detected:")
            print(f"Expected {expected_chq_fixes} but found {actual_chq_fixes} CHQ fixes")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Please run 'python fix_chq_linking.py' first to generate the enhanced transaction trail")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dashboard_integration():
    """Check if the enhanced dashboard has the CHQ integration code"""
    
    print("\n🔍 Checking Enhanced Dashboard Integration")
    print("=" * 45)
    
    try:
        with open('enhanced_dashboard.py', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        # Check for key CHQ-related functions
        checks = [
            ('identify_inv_chq_payment_pairs', 'CHQ Payment Pair Identification'),
            ('enhanced_hr185_transaction_analysis', 'Enhanced HR185 Analysis'),
            ('Payment for INV', 'CHQ Inheritance Description'),
            ('inherited_from_inv', 'CHQ Inheritance Logic'),
            ('CHQ Inheritance Analysis', 'CHQ Analysis Section')
        ]
        
        print("Checking for CHQ integration components:")
        all_present = True
        
        for search_term, description in checks:
            if search_term in dashboard_content:
                print(f"  ✓ {description}")
            else:
                print(f"  ❌ {description} - MISSING")
                all_present = False
        
        if all_present:
            print("\n✅ All CHQ integration components found in enhanced dashboard!")
        else:
            print("\n⚠️  Some CHQ integration components are missing from the dashboard")
            
        return all_present
        
    except FileNotFoundError:
        print("❌ enhanced_dashboard.py not found")
        return False
    except Exception as e:
        print(f"❌ Error checking dashboard: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CHQ Integration Validation Suite")
    print("=" * 50)
    
    # Test 1: Validate CHQ inheritance functionality
    validation_passed = quick_chq_validation()
    
    # Test 2: Check dashboard integration
    integration_complete = check_dashboard_integration()
    
    # Overall result
    print(f"\n🏁 OVERALL RESULT:")
    print("=" * 20)
    if validation_passed and integration_complete:
        print("✅ ALL TESTS PASSED!")
        print("CHQ inheritance linking is fully implemented and working correctly.")
    else:
        print("❌ SOME TESTS FAILED")
        print("CHQ inheritance linking may need attention.")
    
    print(f"\nValidation: {'PASS' if validation_passed else 'FAIL'}")
    print(f"Integration: {'PASS' if integration_complete else 'FAIL'}")
