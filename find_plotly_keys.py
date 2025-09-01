#!/usr/bin/env python3
"""
Find all occurrences of plotly_chart calls and their keys
"""

import re

def find_plotly_keys():
    file_path = "enhanced_dashboard.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all plotly_chart calls with keys
    pattern = r'st\.plotly_chart\([^)]*key=(["\'])([^"\']*)\1[^)]*\)'
    matches = re.finditer(pattern, content)
    
    key_counts = {}
    key_locations = {}
    
    for match in matches:
        key = match.group(2)
        if key not in key_counts:
            key_counts[key] = 0
            key_locations[key] = []
        
        key_counts[key] += 1
        
        # Find line number
        line_num = content[:match.start()].count('\n') + 1
        key_locations[key].append(line_num)
    
    print("All plotly chart keys found:")
    for key, count in sorted(key_counts.items()):
        if count > 1:
            print(f"❌ DUPLICATE: '{key}' appears {count} times at lines: {key_locations[key]}")
        else:
            print(f"✅ '{key}' appears once at line: {key_locations[key][0]}")
    
    # Show duplicates only
    duplicates = {k: v for k, v in key_counts.items() if v > 1}
    if duplicates:
        print(f"\n🚨 Found {len(duplicates)} duplicate keys:")
        for key, count in duplicates.items():
            print(f"  '{key}': {count} occurrences at lines {key_locations[key]}")
    else:
        print("\n✅ No duplicate keys found!")

if __name__ == "__main__":
    find_plotly_keys()
