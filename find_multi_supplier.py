#!/usr/bin/env python3
"""
Comprehensive search for multi_supplier_items key duplications
"""

def find_all_multi_supplier_keys():
    file_path = "enhanced_dashboard.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    print()
    
    # Search for the exact key
    key_matches = []
    for i, line in enumerate(lines):
        if 'multi_supplier_items' in line and 'key=' in line:
            key_matches.append((i + 1, line.strip()))
    
    print(f"Found {len(key_matches)} lines containing 'multi_supplier_items' as a key:")
    for line_num, line in key_matches:
        print(f"  Line {line_num}: {line}")
    print()
    
    # Search for any plotly_chart with this key pattern
    import re
    plotly_matches = []
    for i, line in enumerate(lines):
        if 'st.plotly_chart' in line and 'multi_supplier_items' in line:
            plotly_matches.append((i + 1, line.strip()))
    
    print(f"Found {len(plotly_matches)} plotly_chart calls with 'multi_supplier_items':")
    for line_num, line in plotly_matches:
        print(f"  Line {line_num}: {line}")
    print()
    
    # Show context around each match
    if plotly_matches:
        print("Context around each match:")
        for line_num, _ in plotly_matches:
            print(f"\n--- Context around line {line_num} ---")
            start = max(0, line_num - 6)
            end = min(len(lines), line_num + 3)
            for i in range(start, end):
                prefix = ">>>" if i == line_num - 1 else "   "
                print(f"{prefix} {i+1:4d}: {lines[i].rstrip()}")

if __name__ == "__main__":
    find_all_multi_supplier_keys()
