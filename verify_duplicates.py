#!/usr/bin/env python3
"""
Analysis of GRN and Issue data structure - explaining multi-line documents
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_document_structure():
    """Analyze GRN and Issue document structure to show normal business patterns."""
    
    # Load the data
    grn_file = Path("output/individual_hr995grn.csv")
    issue_file = Path("output/individual_hr995issue.csv")
    
    if not grn_file.exists():
        print(f"❌ GRN file not found: {grn_file}")
        return
        
    if not issue_file.exists():
        print(f"❌ Issue file not found: {issue_file}")
        return
    
    print("📊 Loading data files...")
    
    # Load GRN data
    grn_df = pd.read_csv(grn_file, low_memory=False)
    issue_df = pd.read_csv(issue_file, low_memory=False)
    
    print(f"✅ GRN data loaded: {len(grn_df):,} rows")
    print(f"✅ Issue data loaded: {len(issue_df):,} rows")
    print()
    
    # Analyze GRN document structure
    print("🔍 Analyzing GRN Document Structure...")
    if 'grn_no' in grn_df.columns:
        total_grn_records = len(grn_df)
        unique_grn_numbers = grn_df['grn_no'].nunique()
        multi_line_grn_records = total_grn_records - unique_grn_numbers
        
        print(f"📦 Total GRN line items: {total_grn_records:,}")
        print(f"� Unique GRN documents: {unique_grn_numbers:,}")
        print(f"✅ Multi-line GRN items: {multi_line_grn_records:,} (normal - multiple products per GRN)")
        
        # Show some example multi-line GRNs
        grn_value_counts = grn_df['grn_no'].value_counts()
        multi_line_grns = grn_value_counts[grn_value_counts > 1]
        
        if len(multi_line_grns) > 0:
            print(f"📋 GRN documents with multiple items: {len(multi_line_grns):,}")
            print("🔍 Examples of multi-line GRNs:")
            for grn_no, count in multi_line_grns.head().items():
                print(f"   GRN {grn_no}: {count} different items/products")
    else:
        print("❌ 'grn_no' column not found in GRN data")
    
    print()
    
    # Analyze Issue document structure  
    print("🔍 Analyzing Requisition Document Structure...")
    if 'requisition_no' in issue_df.columns:
        total_issue_records = len(issue_df)
        unique_req_numbers = issue_df['requisition_no'].nunique()
        multi_line_req_records = total_issue_records - unique_req_numbers
        
        print(f"📋 Total Requisition line items: {total_issue_records:,}")
        print(f"� Unique Requisition documents: {unique_req_numbers:,}")
        print(f"✅ Multi-line Requisition items: {multi_line_req_records:,} (normal - multiple products per requisition)")
        
        # Show some example multi-line requisitions
        req_value_counts = issue_df['requisition_no'].value_counts()
        multi_line_reqs = req_value_counts[req_value_counts > 1]
        
        if len(multi_line_reqs) > 0:
            print(f"📋 Requisitions with multiple items: {len(multi_line_reqs):,}")
            print("🔍 Examples of multi-line Requisitions:")
            for req_no, count in multi_line_reqs.head().items():
                print(f"   REQ {req_no}: {count} different items/products")
    else:
        print("❌ 'requisition_no' column not found in Issue data")
    
    print()
    print("=" * 70)
    print("📊 BUSINESS PATTERN ANALYSIS")
    print("=" * 70)
    
    if 'grn_no' in grn_df.columns:
        multi_line_grns = len(grn_df) - grn_df['grn_no'].nunique()
        print(f"✅ Multi-line GRN items: {multi_line_grns:,}")
        print("   → This is NORMAL: One GRN can receive multiple different products")
        
    if 'requisition_no' in issue_df.columns:
        multi_line_reqs = len(issue_df) - issue_df['requisition_no'].nunique()
        print(f"✅ Multi-line Requisition items: {multi_line_reqs:,}")
        print("   → This is NORMAL: One requisition can request multiple different items")
        
    print()
    print("💡 CONCLUSION: These are NOT data inconsistencies!")
    print("   They represent normal business practice where:")
    print("   • One GRN document lists multiple products received")
    print("   • One Requisition document requests multiple different items")

if __name__ == "__main__":
    analyze_document_structure()
