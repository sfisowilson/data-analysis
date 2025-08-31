#!/usr/bin/env python3
"""
Update master data file to include PDF-extracted data.
"""

import pandas as pd
from pathlib import Path

def update_master_with_pdf_data():
    """Update the master CSV file to include PDF data."""
    output_dir = Path('output')
    
    print("🔄 Updating master file with PDF data...")
    
    # Load existing master data
    master_df = pd.read_csv(output_dir / 'all_stock_data.csv', low_memory=False)
    print(f"📊 Current master records: {len(master_df):,}")
    
    # Load PDF data
    pdf_data = []
    
    # Load HR185 transactions
    try:
        hr185_df = pd.read_csv(output_dir / 'individual_hr185_transactions.csv')
        print(f"📄 HR185 transactions: {len(hr185_df):,} records")
        
        # Normalize column names to match master format
        hr185_normalized = hr185_df.rename(columns={
            'transaction_date': 'date',
            'supplier_name': 'supplier',
            'supplier_code': 'supplier_code',
            'reference': 'reference_no',
            'transaction_type': 'document_type',
            'amount': 'amount'
        })
        
        # Add missing columns to match master structure
        for col in ['quantity', 'item_code', 'description', 'store_no']:
            if col not in hr185_normalized.columns:
                hr185_normalized[col] = None
        
        pdf_data.append(hr185_normalized)
        
    except Exception as e:
        print(f"❌ Error loading HR185: {e}")
    
    # Load HR990 statistics
    try:
        hr990_df = pd.read_csv(output_dir / 'individual_hr990_expenditure.csv')
        print(f"📈 HR990 statistics: {len(hr990_df):,} records")
        
        # Normalize column names to match master format
        hr990_normalized = hr990_df.rename(columns={
            'description': 'description',
            'count': 'quantity',
            'reference': 'reference_no',
            'code': 'item_code'
        })
        
        # Add missing columns to match master structure
        for col in ['date', 'supplier', 'amount', 'store_no']:
            if col not in hr990_normalized.columns:
                hr990_normalized[col] = None
        
        pdf_data.append(hr990_normalized)
        
    except Exception as e:
        print(f"❌ Error loading HR990: {e}")
    
    if pdf_data:
        # Combine PDF data more carefully
        print(f"📋 Combining PDF data...")
        
        # Handle each dataframe separately first
        for i, df in enumerate(pdf_data):
            print(f"  PDF dataset {i+1}: {len(df)} records, {len(df.columns)} columns")
        
        # Ensure same columns for all PDF datasets
        all_pdf_columns = set()
        for df in pdf_data:
            all_pdf_columns.update(df.columns)
        
        # Standardize PDF datasets
        standardized_pdf_data = []
        for df in pdf_data:
            standardized_df = df.copy()
            for col in all_pdf_columns:
                if col not in standardized_df.columns:
                    standardized_df[col] = None
            standardized_df = standardized_df[sorted(all_pdf_columns)]
            standardized_pdf_data.append(standardized_df)
        
        # Now combine PDF data
        combined_pdf_df = pd.concat(standardized_pdf_data, ignore_index=True)
        print(f"📋 Combined PDF data: {len(combined_pdf_df):,} records")
        
        # Ensure all columns match before combining with master
        master_columns = set(master_df.columns)
        pdf_columns = set(combined_pdf_df.columns)
        
        # Add missing columns to PDF data
        for col in master_columns - pdf_columns:
            combined_pdf_df[col] = None
        
        # Add missing columns to master data
        for col in pdf_columns - master_columns:
            master_df[col] = None
        
        # Reorder columns to match
        common_columns = sorted(master_columns.union(pdf_columns))
        master_df = master_df[common_columns]
        combined_pdf_df = combined_pdf_df[common_columns]
        
        # Combine all data
        updated_master = pd.concat([master_df, combined_pdf_df], ignore_index=True)
        
        # Save updated master
        backup_file = output_dir / 'all_stock_data_backup.csv'
        master_df.to_csv(backup_file, index=False)
        print(f"💾 Backup saved: {backup_file}")
        
        updated_master.to_csv(output_dir / 'all_stock_data.csv', index=False)
        print(f"✅ Updated master saved: {len(updated_master):,} total records")
        print(f"📈 Added {len(combined_pdf_df):,} PDF records")
        
        # Show updated source breakdown
        print(f"\n📊 Updated source file breakdown:")
        for source, count in updated_master['source_file'].value_counts().head(15).items():
            print(f"  {source:<45} {count:>8,}")
    
    else:
        print("⚠️ No PDF data found to add")

if __name__ == "__main__":
    update_master_with_pdf_data()
