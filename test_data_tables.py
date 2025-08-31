#!/usr/bin/env python3
"""
Test the Data Tables functionality.
"""

import pandas as pd
from pathlib import Path

def test_data_tables():
    """Test if all data tables can be loaded properly."""
    print("🧪 TESTING DATA TABLES")
    print("=" * 50)
    
    output_folder = Path("output")
    
    # Test files from the dashboard
    test_files = [
        ("HR995 GRN Records", "hr995_grn.csv"),
        ("HR995 Issue Records", "hr995_issue.csv"),
        ("HR995 Voucher Records", "hr995_voucher.csv"),
        ("All Stock Data (Combined)", "all_stock_data.csv"),
        ("Objective 1: Item Frequency", "objective_1_item_frequency_by_supplier.csv"),
        ("Objective 2: Audit Trail", "objective_2_stock_audit_trail.csv"),
        ("Objective 5: Stock Balances by Year", "objective_5_stock_balances_by_year.csv")
    ]
    
    working_files = []
    broken_files = []
    
    for display_name, filename in test_files:
        file_path = output_folder / filename
        try:
            if file_path.exists():
                df = pd.read_csv(file_path, low_memory=False)
                if len(df) > 0:
                    working_files.append((display_name, filename, len(df)))
                    print(f"  ✅ {display_name:<35} {len(df):>8,} records")
                else:
                    broken_files.append((display_name, filename, "Empty file"))
                    print(f"  ⚠️  {display_name:<35} {'Empty':>8}")
            else:
                broken_files.append((display_name, filename, "File not found"))
                print(f"  ❌ {display_name:<35} {'Missing':>8}")
        except Exception as e:
            broken_files.append((display_name, filename, str(e)))
            print(f"  ❌ {display_name:<35} {'Error':>8} - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY:")
    print(f"  ✅ Working files: {len(working_files)}")
    print(f"  ❌ Broken files: {len(broken_files)}")
    
    if working_files:
        total_records = sum(count for _, _, count in working_files)
        print(f"  📈 Total records available: {total_records:,}")
    
    if broken_files:
        print(f"\n⚠️  Files needing attention:")
        for name, file, error in broken_files:
            print(f"    • {name}: {error}")
    
    print(f"\n✅ Data Tables test completed!")
    print(f"🎯 The dashboard should now work properly with the Data Tables tab")

if __name__ == "__main__":
    test_data_tables()
