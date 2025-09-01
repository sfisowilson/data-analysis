#!/usr/bin/env python3
"""
Script to add unique keys to all plotly_chart calls that are missing keys
"""

import re

def fix_plotly_keys():
    file_path = "enhanced_dashboard.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define unique keys for each line number based on context
    key_mappings = {
        2043: "financial_outliers_scatter",
        2618: "hourly_activity_pattern", 
        2701: "after_hours_transactions",
        2737: "bulk_transaction_pattern",
        2783: "rapid_successive_transactions",
        2832: "same_day_multi_supplier",
        2966: "duplicate_transactions_analysis",
        3118: "authorization_patterns_overview",
        3148: "authorization_compliance_metrics",
        3216: "authorization_trends_timeline",
        3270: "authorization_inconsistencies",
        3403: "scoa_structure_compliance",
        3456: "vote_structure_breakdown", 
        3498: "scoa_validation_summary",
        3556: "ppe_category_distribution",
        3589: "electrical_materials_breakdown",
        3785: "ppe_electrical_trends",
        3840: "supplier_ppe_specialization",
        3994: "materials_seasonal_patterns",
        4304: "enhanced_anomaly_detection",
        4502: "authorization_official_patterns",
        4533: "authorization_value_analysis", 
        4566: "authorization_monthly_trends",
        4631: "authorization_threshold_analysis",
        4656: "multi_official_authorizations",
        4684: "authorization_processing_time",
        4782: "authorization_risk_assessment",
        5152: "pdf_document_patterns",
        5163: "pdf_value_correlation",
        5193: "pdf_type_distribution",
        5252: "pdf_monthly_processing",
        5276: "pdf_processing_timeline"
    }
    
    # Sort by line number to process in order
    for line_num in sorted(key_mappings.keys()):
        key_name = key_mappings[line_num]
        
        # Find the pattern and replace it
        pattern = r'(\s+st\.plotly_chart\(fig[^,]*,\s*use_container_width=True)\)'
        
        # Split content into lines to target specific line
        lines = content.split('\n')
        if line_num - 1 < len(lines):
            line_content = lines[line_num - 1]
            if 'st.plotly_chart' in line_content and 'key=' not in line_content:
                # Replace the line
                new_line = re.sub(pattern, r'\1, key="' + key_name + '")', line_content)
                lines[line_num - 1] = new_line
                print(f"Fixed line {line_num}: Added key '{key_name}'")
        
        content = '\n'.join(lines)
    
    # Write the updated content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ All plotly chart keys have been fixed!")

if __name__ == "__main__":
    fix_plotly_keys()
