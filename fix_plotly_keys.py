#!/usr/bin/env python3
"""Script to add unique keys to all plotly_chart calls in enhanced_dashboard.py"""

import re

def fix_plotly_charts():
    """Add unique keys to all plotly_chart calls that don't have them."""
    
    # Read the file
    with open('enhanced_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all plotly_chart calls without keys
    pattern = r'st\.plotly_chart\(([^)]*)\)(?!\s*#.*key=)'
    matches = list(re.finditer(pattern, content))
    
    print(f"Found {len(matches)} plotly_chart calls to fix")
    
    # Counter for unique keys
    key_counter = 1
    
    # Process matches in reverse order to maintain line numbers
    for match in reversed(matches):
        full_match = match.group(0)
        params = match.group(1)
        
        # Check if key is already present
        if 'key=' in params:
            print(f"Skipping (already has key): {full_match}")
            continue
            
        # Generate unique key
        unique_key = f"chart_{key_counter:03d}"
        key_counter += 1
        
        # Determine if we need to add comma
        if params.strip():
            if not params.strip().endswith(','):
                new_call = f'st.plotly_chart({params}, key="{unique_key}")'
            else:
                new_call = f'st.plotly_chart({params} key="{unique_key}")'
        else:
            new_call = f'st.plotly_chart(key="{unique_key}")'
        
        # Replace in content
        start, end = match.span()
        content = content[:start] + new_call + content[end:]
        print(f"Fixed: {full_match} -> {new_call}")
    
    # Write back to file
    with open('enhanced_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {key_counter - 1} plotly_chart calls")

if __name__ == "__main__":
    fix_plotly_charts()
