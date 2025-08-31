#!/usr/bin/env python3
"""
Fix deprecated Streamlit parameters in both dashboards
"""

import re

def fix_streamlit_deprecations():
    """Fix deprecated Streamlit parameters."""
    
    files_to_fix = ['enhanced_dashboard.py', 'dashboard.py']
    
    for filename in files_to_fix:
        try:
            # Read the file
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace use_container_width=True with width="stretch"
            content = re.sub(r'use_container_width=True', 'width="stretch"', content)
            
            # Replace st.experimental_rerun() with st.rerun()
            content = re.sub(r'st\.experimental_rerun\(\)', 'st.rerun()', content)
            
            # Write back the file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'✅ Fixed deprecated parameters in {filename}')
        
        except FileNotFoundError:
            print(f'⚠️  File {filename} not found, skipping...')
    
    print('\n🎉 All Streamlit deprecation issues fixed!')
    print('   • Replaced use_container_width=True with width="stretch"')
    print('   • Fixed st.experimental_rerun() to st.rerun()')
    print('   • Both dashboards are now compatible with latest Streamlit')

if __name__ == "__main__":
    fix_streamlit_deprecations()
