#!/usr/bin/env python3
"""
HR390 PDF Parser - Converts complex movement per store PDFs to CSV format
Handles nested data and complex table structures
"""

import pdfplumber
import pandas as pd
import re
import os
from datetime import datetime

class HR390Parser:
    def __init__(self):
        self.columns = [
            'item_no', 'tran_date', 'type', 'reference', 'line', 'vote_no', 
            'grn_qty', 'grn_value', 'issue_qty', 'issue_value', 'average_pr', 'var_percent', 'description'
        ]
        
    def parse_header_info(self, text):
        """Extract header information from the page"""
        header_info = {}
        
        # Extract date range
        date_match = re.search(r'Date From\s*:\s*(\d{8})\s*Date To\s*:\s*(\d{8})', text)
        if date_match:
            header_info['date_from'] = date_match.group(1)
            header_info['date_to'] = date_match.group(2)
        
        # Extract store info
        store_match = re.search(r'Store No\s*:\s*([^\s]+(?:\s+[^\s]+)*?)(?=\s+Date)', text)
        if store_match:
            header_info['store'] = store_match.group(1).strip()
            
        return header_info
    
    def parse_data_line(self, line, current_item_description=""):
        """Parse a single data line into structured format"""
        line = line.strip()
        if not line or line.startswith('-') or 'Item No' in line:
            return None, current_item_description
            
        # Split the line into parts, handling the complex structure
        parts = line.split()
        
        if not parts:
            return None, current_item_description
            
        # Check if this is a carried forward or brought forward line
        if 'Carried Forward' in line or 'Brought Forward' in line:
            # Extract item number and description
            if parts[0].isdigit():
                item_no = parts[0]
                # Find quantities and values
                qty_val_pattern = r'(\d+\.?\d*)\s+([0-9,]+\.?\d*)'
                matches = re.findall(qty_val_pattern, line)
                
                # Description is usually at the end
                desc_match = re.search(r'[A-Z][A-Z\s/&-]+$', line)
                description = desc_match.group().strip() if desc_match else current_item_description
                
                record = {
                    'item_no': item_no,
                    'tran_date': parts[1] if len(parts) > 1 and parts[1].isdigit() else '',
                    'type': 'Carried Forward' if 'Carried Forward' in line else 'Brought Forward',
                    'reference': '',
                    'line': '',
                    'vote_no': '',
                    'grn_qty': matches[0][0] if matches else '',
                    'grn_value': matches[0][1].replace(',', '') if matches else '',
                    'issue_qty': '',
                    'issue_value': '',
                    'average_pr': '',
                    'var_percent': '',
                    'description': description
                }
                return record, description
        
        # Check if this is a transaction line (ISS, RND, WRO, etc.)
        elif len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
            item_no = parts[0]
            tran_date = parts[1]
            
            # Find transaction type
            trans_types = ['ISS', 'RND', 'WRO', 'GRN', 'ADJ']
            trans_type = ''
            type_idx = -1
            
            for i, part in enumerate(parts):
                if part in trans_types:
                    trans_type = part
                    type_idx = i
                    break
            
            if trans_type and type_idx > 0:
                # Extract reference and other fields
                reference = parts[type_idx + 1] if type_idx + 1 < len(parts) else ''
                line_num = parts[type_idx + 2] if type_idx + 2 < len(parts) else ''
                vote_no = parts[type_idx + 3] if type_idx + 3 < len(parts) else ''
                
                # Extract quantities and values using regex
                numbers = re.findall(r'(\d+\.?\d*)', line)
                values = re.findall(r'([0-9,]+\.?\d*)', line)
                
                # Try to extract specific quantities and values
                qty_val_matches = re.findall(r'(\d+\.?\d*)\s+([0-9,]+\.?\d*)', line)
                
                record = {
                    'item_no': item_no,
                    'tran_date': tran_date,
                    'type': trans_type,
                    'reference': reference,
                    'line': line_num,
                    'vote_no': vote_no,
                    'grn_qty': '',
                    'grn_value': '',
                    'issue_qty': qty_val_matches[0][0] if qty_val_matches else '',
                    'issue_value': qty_val_matches[0][1].replace(',', '') if qty_val_matches else '',
                    'average_pr': qty_val_matches[1][1].replace(',', '') if len(qty_val_matches) > 1 else '',
                    'var_percent': '',
                    'description': current_item_description
                }
                
                # Extract variance percentage if present
                var_match = re.search(r'([+-]\d+\.?\d*)', line)
                if var_match:
                    record['var_percent'] = var_match.group(1)
                
                return record, current_item_description
        
        # Check if this line contains only a description (new item)
        elif parts[0].isdigit() and not parts[1].isdigit():
            # This might be a line with item number and description only
            desc_match = re.search(r'\d+\s+(.+)', line)
            if desc_match:
                current_item_description = desc_match.group(1).strip()
        
        return None, current_item_description
    
    def parse_pdf_file(self, pdf_path):
        """Parse a single PDF file and return DataFrame"""
        print(f"📄 Processing: {os.path.basename(pdf_path)}")
        
        all_records = []
        current_item_description = ""
        header_info = {}
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # Extract header info from first page
                if page_num == 0:
                    header_info = self.parse_header_info(text)
                
                lines = text.split('\n')
                
                for line in lines:
                    record, current_item_description = self.parse_data_line(line, current_item_description)
                    if record:
                        # Add header info to each record
                        record.update(header_info)
                        all_records.append(record)
        
        df = pd.DataFrame(all_records)
        print(f"✅ Extracted {len(df)} records from {os.path.basename(pdf_path)}")
        return df
    
    def parse_all_hr390_pdfs(self, folder_path="Data Hand-Over/HR390"):
        """Parse all HR390 PDF files in the folder"""
        print("🚀 Starting HR390 PDF parsing...")
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            return None
        
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("❌ No PDF files found in HR390 folder")
            return None
        
        all_dataframes = []
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            try:
                df = self.parse_pdf_file(pdf_path)
                if not df.empty:
                    df['source_file'] = pdf_file
                    all_dataframes.append(df)
            except Exception as e:
                print(f"❌ Error processing {pdf_file}: {str(e)}")
                continue
        
        if all_dataframes:
            # Combine all dataframes
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            # Clean and format the data
            combined_df = self.clean_data(combined_df)
            
            # Save to CSV
            output_file = 'output/hr390_movement_data.csv'
            combined_df.to_csv(output_file, index=False)
            print(f"💾 Saved combined data to: {output_file}")
            
            # Generate summary
            self.generate_summary(combined_df)
            
            return combined_df
        else:
            print("❌ No data could be extracted from PDF files")
            return None
    
    def clean_data(self, df):
        """Clean and format the extracted data"""
        print("🧹 Cleaning extracted data...")
        
        # Convert date columns
        if 'tran_date' in df.columns:
            df['tran_date'] = pd.to_datetime(df['tran_date'], format='%Y%m%d', errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['grn_qty', 'grn_value', 'issue_qty', 'issue_value', 'average_pr']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        # Clean variance percentage
        if 'var_percent' in df.columns:
            df['var_percent'] = df['var_percent'].astype(str).str.replace('+', '').str.replace('%', '')
            df['var_percent'] = pd.to_numeric(df['var_percent'], errors='coerce')
        
        # Sort by item number and transaction date
        df = df.sort_values(['item_no', 'tran_date'], na_position='last')
        
        return df
    
    def generate_summary(self, df):
        """Generate summary statistics"""
        print("\n📊 HR390 Data Summary:")
        print(f"Total records: {len(df):,}")
        print(f"Unique items: {df['item_no'].nunique():,}")
        print(f"Date range: {df['tran_date'].min()} to {df['tran_date'].max()}")
        print(f"Transaction types: {df['type'].value_counts().to_dict()}")
        
        # Value summaries
        total_grn_value = df['grn_value'].sum()
        total_issue_value = df['issue_value'].sum()
        print(f"Total GRN value: R{total_grn_value:,.2f}")
        print(f"Total issue value: R{total_issue_value:,.2f}")

def main():
    """Main function to run the HR390 parser"""
    parser = HR390Parser()
    df = parser.parse_all_hr390_pdfs()
    
    if df is not None:
        print("🎉 HR390 PDF parsing completed successfully!")
        return True
    else:
        print("❌ HR390 PDF parsing failed")
        return False

if __name__ == "__main__":
    main()
