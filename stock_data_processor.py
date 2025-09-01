#!/usr/bin/env python3
"""
Stock Data Processing Tool
A comprehensive Python tool for processing stock-related data from multiple file formats.

This tool reads data from .txt, .xlsx, and .pdf files, cleans and standardizes the data,
and generates various analytical reports as specified in the requirements.
"""

import os
import logging
import pandas as pd
import pdfplumber
from pathlib import Path
from datetime import datetime
import re
import numpy as np
from typing import List, Dict, Optional, Tuple
import warnings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore')

class StockDataProcessor:
    """Main class for processing stock data from multiple file formats."""
    
    def __init__(self, data_folder: str, output_folder: str = "output"):
        """
        Initialize the Stock Data Processor.
        
        Args:
            data_folder (str): Path to the folder containing data files
            output_folder (str): Path to the output folder for reports
        """
        self.data_folder = Path(data_folder)
        self.output_folder = Path(output_folder)
        self.all_data = []
        self.processed_data = {}
        
        # Setup logging
        self._setup_logging()
        
        # Create output directory
        self.output_folder.mkdir(exist_ok=True)
        
        # Standard column mapping for consistency
        self.standard_columns = {
            'date': ['date', 'transaction_date', 'doc_date', 'created_date'],
            'item_code': ['item_code', 'itemcode', 'item', 'code', 'product_code'],
            'description': ['description', 'item_description', 'product_description', 'desc'],
            'supplier': ['supplier', 'vendor', 'supplier_name', 'vendor_name'],
            'quantity': ['quantity', 'qty', 'amount', 'units'],
            'official': ['official', 'officer', 'created_by', 'user', 'staff'],
            'document_type': ['document_type', 'doc_type', 'type', 'transaction_type']
        }
        
        # Corrected business relationships
        self.business_relationships = {
            'issue_hr390': 'HR995Issue.Requisition No ↔ HR390.reference',
            'grn_hr185': 'HR995GRN.Inv No ↔ HR185.reference',
            'grn_voucher': 'HR995GRN.Voucher ↔ HR995VOUCHER.Voucher No'
        }
        
        self.logger.info(f"Stock Data Processor initialized with corrected business logic")
        self.logger.info(f"Data folder: {self.data_folder}")
        self.logger.info(f"Output folder: {self.output_folder}")
        self.logger.info("Corrected business relationships loaded")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stock_processor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def normalize_reference(self, ref):
        """Normalize reference numbers for proper data linkage."""
        if pd.isna(ref):
            return ref
        
        ref_str = str(ref).strip()
        
        # For numeric references, strip leading zeros and convert to int
        if ref_str.isdigit() or (ref_str.startswith('0') and ref_str.lstrip('0').isdigit()):
            try:
                return int(ref_str.lstrip('0')) if ref_str.lstrip('0') else 0
            except:
                return ref_str
        
        return ref_str.upper()
    
    def apply_business_logic_corrections(self, df, data_type):
        """Apply corrected business logic to data based on type."""
        if df.empty:
            return df
        
        corrected_df = df.copy()
        
        # Apply corrections based on data type
        if data_type == 'hr995_grn':
            # Normalize invoice numbers for GRN → HR185 linkage
            if 'inv_no' in corrected_df.columns:
                corrected_df['inv_no_normalized'] = corrected_df['inv_no'].apply(self.normalize_reference)
            
            # Normalize voucher references for GRN → Voucher linkage
            if 'voucher' in corrected_df.columns:
                corrected_df['voucher_normalized'] = corrected_df['voucher'].apply(
                    lambda x: str(x).strip().upper() if pd.notna(x) else x
                )
        
        elif data_type == 'hr995_issue':
            # Normalize requisition numbers for Issue → HR390 linkage
            if 'requisition_no' in corrected_df.columns:
                corrected_df['requisition_no_normalized'] = corrected_df['requisition_no'].apply(self.normalize_reference)
        
        elif data_type == 'hr995_voucher':
            # Normalize voucher numbers for Voucher linkage
            if 'voucher_no' in corrected_df.columns:
                corrected_df['voucher_no_normalized'] = corrected_df['voucher_no'].apply(
                    lambda x: str(x).strip().upper() if pd.notna(x) else x
                )
        
        elif data_type == 'hr390_movement':
            # Normalize reference for HR390 linkage
            if 'reference' in corrected_df.columns:
                corrected_df['reference_normalized'] = corrected_df['reference'].apply(self.normalize_reference)
        
        elif data_type == 'hr185_transactions':
            # Normalize reference for HR185 linkage
            if 'reference' in corrected_df.columns:
                corrected_df['reference_normalized'] = corrected_df['reference'].apply(self.normalize_reference)
        
        self.logger.info(f"Applied business logic corrections to {data_type}: {len(corrected_df)} records")
        return corrected_df
    
    def load_txt_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from text files (tab or comma separated).
        
        Args:
            file_path (Path): Path to the text file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            self.logger.info(f"Loading text file: {file_path}")
            
            # Try different separators
            separators = ['\t', ',', ';', '|']
            df = None
            
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding='utf-8')
                    if len(df.columns) > 1:  # If we get multiple columns, it's likely correct
                        break
                except:
                    continue
            
            if df is None or len(df.columns) == 1:
                # Try with different encoding
                try:
                    df = pd.read_csv(file_path, sep='\t', encoding='latin-1')
                except:
                    df = pd.read_csv(file_path, encoding='latin-1')
            
            if df is not None and not df.empty:
                df['source_file'] = file_path.name
                df['file_type'] = 'txt'
                self.logger.info(f"Successfully loaded {len(df)} rows from {file_path.name}")
                return df
            else:
                self.logger.warning(f"No data found in {file_path.name}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error loading text file {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def load_excel_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from Excel files.
        
        Args:
            file_path (Path): Path to the Excel file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            self.logger.info(f"Loading Excel file: {file_path}")
            
            # Read all sheets and combine them
            excel_file = pd.ExcelFile(file_path)
            dfs = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    if not df.empty:
                        df['sheet_name'] = sheet_name
                        df['source_file'] = file_path.name
                        df['file_type'] = 'xlsx'
                        dfs.append(df)
                        self.logger.info(f"Loaded sheet '{sheet_name}' with {len(df)} rows")
                except Exception as e:
                    self.logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                self.logger.info(f"Successfully loaded {len(combined_df)} total rows from {file_path.name}")
                return combined_df
            else:
                self.logger.warning(f"No data found in {file_path.name}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error loading Excel file {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def load_pdf_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from PDF files containing tables.
        
        Args:
            file_path (Path): Path to the PDF file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            self.logger.info(f"Loading PDF file: {file_path}")
            
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Extract tables from the page
                        page_tables = page.extract_tables()
                        for table_num, table in enumerate(page_tables):
                            if table and len(table) > 1:  # At least header + one row
                                # Convert table to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df = df.dropna(how='all')  # Remove empty rows
                                if not df.empty:
                                    df['page_number'] = page_num + 1
                                    df['table_number'] = table_num + 1
                                    df['source_file'] = file_path.name
                                    df['file_type'] = 'pdf'
                                    tables.append(df)
                                    self.logger.info(f"Extracted table {table_num + 1} from page {page_num + 1} with {len(df)} rows")
                    except Exception as e:
                        self.logger.warning(f"Could not extract tables from page {page_num + 1}: {str(e)}")
            
            if tables:
                combined_df = pd.concat(tables, ignore_index=True)
                self.logger.info(f"Successfully loaded {len(combined_df)} total rows from {file_path.name}")
                return combined_df
            else:
                self.logger.warning(f"No tables found in {file_path.name}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error loading PDF file {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to standard format.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with normalized column names
        """
        if df.empty:
            return df
        
        # Clean column names
        df.columns = df.columns.astype(str)
        df.columns = [col.lower().strip().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Map to standard column names
        column_mapping = {}
        for standard_col, variations in self.standard_columns.items():
            for col in df.columns:
                if any(var in col for var in variations):
                    column_mapping[col] = standard_col
                    break
        
        df = df.rename(columns=column_mapping)
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the data.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        if df.empty:
            return df
        
        try:
            # Strip whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', np.nan)
            
            # Convert dates to standard format - handle YYYYMMDD and YYYYMM formats
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    # Handle YYYYMMDD format (like GRN Date, Issue Date, Cheq Date)
                    try:
                        # Convert to numeric first to handle YYYYMMDD format
                        numeric_dates = pd.to_numeric(df[col], errors='coerce')
                        df[f'{col}_converted'] = pd.NaT
                        
                        for idx in numeric_dates.dropna().index:
                            try:
                                date_val = int(numeric_dates.loc[idx])
                                date_str = str(date_val)
                                
                                if len(date_str) == 8:  # YYYYMMDD format
                                    year = int(date_str[:4])
                                    month = int(date_str[4:6])
                                    day = int(date_str[6:8])
                                    
                                    if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                                        df.loc[idx, f'{col}_converted'] = pd.Timestamp(year=year, month=month, day=day)
                                
                                elif len(date_str) == 6:  # YYYYMM format (fin_period)
                                    year = int(date_str[:4])
                                    month = int(date_str[4:6])
                                    
                                    if 2000 <= year <= 2030 and 1 <= month <= 12:
                                        df.loc[idx, f'{col}_converted'] = pd.Timestamp(year=year, month=month, day=1)
                                        
                            except Exception:
                                continue
                        
                        # If conversion was successful, replace original column
                        if df[f'{col}_converted'].notna().sum() > 0:
                            df[col] = df[f'{col}_converted']
                            df = df.drop(columns=[f'{col}_converted'])
                        else:
                            # Fallback to standard datetime parsing
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                            df = df.drop(columns=[f'{col}_converted'])
                    
                    except Exception:
                        # Fallback to standard datetime parsing
                        df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert quantities to numeric
            quantity_columns = [col for col in df.columns if any(q in col.lower() for q in ['quantity', 'qty', 'amount'])]
            for col in quantity_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop duplicates
            df = df.drop_duplicates()
            
            # Remove rows that are completely empty except for metadata
            metadata_cols = ['source_file', 'file_type', 'sheet_name', 'page_number', 'table_number']
            data_cols = [col for col in df.columns if col not in metadata_cols]
            if data_cols:
                df = df.dropna(subset=data_cols, how='all')
            
            self.logger.info(f"Data cleaning completed. Rows after cleaning: {len(df)}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            return df
    
    def process_all_files(self):
        """Process all files in the data folder."""
        self.logger.info("Starting to process all files...")
        
        # Store individual file data for separate CSV creation
        self.individual_files = {}
        
        # Recursively find all files
        for file_path in self.data_folder.rglob('*'):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                
                try:
                    if file_extension == '.txt':
                        df = self.load_txt_file(file_path)
                    elif file_extension in ['.xlsx', '.xls']:
                        df = self.load_excel_file(file_path)
                    elif file_extension == '.pdf':
                        df = self.load_pdf_file(file_path)
                    else:
                        self.logger.info(f"Skipping unsupported file type: {file_path}")
                        continue
                    
                    if not df.empty:
                        # Normalize and clean data
                        df = self.normalize_column_names(df)
                        df = self.clean_data(df)
                        
                        if not df.empty:
                            # Determine report type for business logic application
                            report_type = self._determine_report_type(file_path.name)
                            
                            # Apply corrected business logic based on data type
                            df = self.apply_business_logic_corrections(df, report_type)
                            
                            self.all_data.append(df)
                            
                            # Store by report type based on filename
                            if report_type not in self.processed_data:
                                self.processed_data[report_type] = []
                            self.processed_data[report_type].append(df)
                            
                            # Store individual file for separate CSV
                            individual_name = self._get_individual_file_name(file_path.name)
                            self.individual_files[individual_name] = df.copy()
                            
                            self.logger.info(f"Processed {file_path.name} as {report_type} with corrected business logic")
                
                except Exception as e:
                    self.logger.error(f"Failed to process file {file_path}: {str(e)}")
        
        self.logger.info(f"Completed processing. Total files processed: {len(self.all_data)}")
        self.logger.info(f"Individual files for CSV conversion: {len(self.individual_files)}")
    
    def _determine_report_type(self, filename: str) -> str:
        """
        Determine report type based on filename.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Report type
        """
        filename_lower = filename.lower()
        
        if 'hr995grn' in filename_lower or 'grn' in filename_lower:
            return 'hr995_grn'
        elif 'hr995vouch' in filename_lower or 'voucher' in filename_lower:
            return 'hr995_voucher'
        elif 'hr995issue' in filename_lower or 'issue' in filename_lower:
            return 'hr995_issue'
        elif 'hr995redund' in filename_lower or 'redundant' in filename_lower:
            return 'hr995_redundant'
        elif 'hr390' in filename_lower:
            return 'hr390_movement'
        elif 'hr990' in filename_lower:
            return 'hr990_expenditure'
        elif 'hr185' in filename_lower:
            return 'hr185_transactions'
        elif 'supplier' in filename_lower:
            return 'suppliers'
        elif 'stock' in filename_lower and 'balance' in filename_lower:
            return 'stock_balances'
        elif 'stock' in filename_lower and 'adjustment' in filename_lower:
            return 'stock_adjustments'
        elif 'variance' in filename_lower:
            return 'variance_report'
        elif 'hr450' in filename_lower:
            return 'hr450_data'
        else:
            return 'other'
    
    def _get_individual_file_name(self, filename: str) -> str:
        """
        Get a clean filename for individual CSV output.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Clean filename for CSV
        """
        # Remove extension and clean up name
        clean_name = Path(filename).stem
        # Replace spaces and special characters with underscores
        clean_name = re.sub(r'[^\w\-_]', '_', clean_name)
        # Remove multiple underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        return clean_name.lower()
    
    def save_consolidated_data(self):
        """Save all data into consolidated and separate CSV files."""
        self.logger.info("Saving consolidated data...")
        
        if not self.all_data:
            self.logger.warning("No data to save")
            return
        
        # Save master consolidated CSV
        try:
            master_df = pd.concat(self.all_data, ignore_index=True)
            master_file = self.output_folder / "all_stock_data.csv"
            master_df.to_csv(master_file, index=False)
            self.logger.info(f"[SUCCESS] Master consolidated CSV saved: {master_file}")
            print(f"[SUCCESS] Master consolidated CSV saved: {master_file}")
        except Exception as e:
            self.logger.error(f"Error saving master CSV: {str(e)}")
        
        # Save separate CSVs per report type
        for report_type, dfs in self.processed_data.items():
            try:
                if dfs:
                    combined_df = pd.concat(dfs, ignore_index=True)
                    output_file = self.output_folder / f"{report_type}.csv"
                    combined_df.to_csv(output_file, index=False)
                    self.logger.info(f"[SUCCESS] Report CSV saved: {output_file}")
                    print(f"[SUCCESS] Report CSV saved: {output_file}")
            except Exception as e:
                self.logger.error(f"Error saving {report_type} CSV: {str(e)}")
        
        # Save individual CSV files for each source file
        if hasattr(self, 'individual_files'):
            self.logger.info("Saving individual CSV files for each source...")
            for file_name, df in self.individual_files.items():
                try:
                    output_file = self.output_folder / f"individual_{file_name}.csv"
                    df.to_csv(output_file, index=False)
                    self.logger.info(f"[SUCCESS] Individual CSV saved: {output_file}")
                    print(f"[SUCCESS] Individual CSV saved: {output_file}")
                except Exception as e:
                    self.logger.error(f"Error saving individual {file_name} CSV: {str(e)}")
        else:
            self.logger.warning("No individual files data found")
    
    def generate_objective_1_report(self):
        """
        Objective 1: Frequency of requesting certain items from specific suppliers (2022–2025).
        """
        self.logger.info("Generating Objective 1 report: Item request frequency by supplier")
        
        try:
            if not self.all_data:
                self.logger.warning("No data available for analysis")
                return
            
            master_df = pd.concat(self.all_data, ignore_index=True)
            
            # Filter data for 2022-2025
            if 'date' in master_df.columns:
                master_df['date'] = pd.to_datetime(master_df['date'], errors='coerce')
                mask = (master_df['date'].dt.year >= 2022) & (master_df['date'].dt.year <= 2025)
                filtered_df = master_df[mask]
            else:
                filtered_df = master_df
            
            # Group by item and supplier to get frequency
            group_cols = []
            if 'item_code' in filtered_df.columns:
                group_cols.append('item_code')
            if 'description' in filtered_df.columns:
                group_cols.append('description')
            if 'supplier' in filtered_df.columns:
                group_cols.append('supplier')
            
            if group_cols:
                frequency_report = filtered_df.groupby(group_cols).agg({
                    'quantity': ['count', 'sum'],
                    'date': ['min', 'max']
                }).round(2)
                
                frequency_report.columns = ['request_count', 'total_quantity', 'first_request', 'last_request']
                frequency_report = frequency_report.reset_index()
                frequency_report = frequency_report.sort_values('request_count', ascending=False)
                
                output_file = self.output_folder / "objective_1_item_frequency_by_supplier.csv"
                frequency_report.to_csv(output_file, index=False)
                self.logger.info(f"[SUCCESS] Objective 1 report saved: {output_file}")
                print(f"[SUCCESS] Objective 1 report saved: {output_file}")
            else:
                self.logger.warning("Required columns not found for Objective 1 analysis")
                
        except Exception as e:
            self.logger.error(f"Error generating Objective 1 report: {str(e)}")
    
    def generate_objective_2_report(self):
        """
        Objective 2: Match stock requisition vs GRN, and produce an audit trail of stock movement by officials.
        """
        self.logger.info("Generating Objective 2 report: Stock requisition vs GRN audit trail")
        
        try:
            # Get GRN and issue data
            grn_data = self.processed_data.get('hr995_grn', [])
            issue_data = self.processed_data.get('hr995_issue', [])
            
            if not grn_data and not issue_data:
                self.logger.warning("No GRN or issue data available for Objective 2")
                return
            
            audit_reports = []
            
            if grn_data:
                grn_df = pd.concat(grn_data, ignore_index=True)
                grn_df['transaction_type'] = 'GRN'
                audit_reports.append(grn_df)
            
            if issue_data:
                issue_df = pd.concat(issue_data, ignore_index=True)
                issue_df['transaction_type'] = 'Issue'
                audit_reports.append(issue_df)
            
            if audit_reports:
                audit_trail = pd.concat(audit_reports, ignore_index=True)
                
                # Sort by date and item for audit trail
                if 'date' in audit_trail.columns:
                    audit_trail['date'] = pd.to_datetime(audit_trail['date'], errors='coerce')
                    audit_trail = audit_trail.sort_values(['item_code', 'date'] if 'item_code' in audit_trail.columns else ['date'])
                
                output_file = self.output_folder / "objective_2_stock_audit_trail.csv"
                audit_trail.to_csv(output_file, index=False)
                self.logger.info(f"[SUCCESS] Objective 2 report saved: {output_file}")
                print(f"[SUCCESS] Objective 2 report saved: {output_file}")
                
        except Exception as e:
            self.logger.error(f"Error generating Objective 2 report: {str(e)}")
    
    def generate_objective_3_report(self):
        """
        Objective 3: Generate the HR995 report.
        """
        self.logger.info("Generating Objective 3 report: HR995 report")
        
        try:
            hr995_types = ['hr995_grn', 'hr995_voucher', 'hr995_issue', 'hr995_redundant']
            hr995_data = []
            
            for report_type in hr995_types:
                if report_type in self.processed_data:
                    data = self.processed_data[report_type]
                    if data:
                        df = pd.concat(data, ignore_index=True)
                        df['hr995_type'] = report_type
                        hr995_data.append(df)
            
            if hr995_data:
                hr995_report = pd.concat(hr995_data, ignore_index=True)
                
                output_file = self.output_folder / "objective_3_hr995_report.csv"
                hr995_report.to_csv(output_file, index=False)
                self.logger.info(f"[SUCCESS] Objective 3 report saved: {output_file}")
                print(f"[SUCCESS] Objective 3 report saved: {output_file}")
            else:
                self.logger.warning("No HR995 data available for Objective 3")
                
        except Exception as e:
            self.logger.error(f"Error generating Objective 3 report: {str(e)}")
    
    def generate_objective_4_report(self):
        """
        Objective 4: End-to-end process report (GRN → Refund → Vouchers/Payments → Order Summary → Stock Balances).
        """
        self.logger.info("Generating Objective 4 report: End-to-end process report")
        
        try:
            process_data = []
            process_types = ['hr995_grn', 'hr995_redundant', 'hr995_voucher', 'stock_balances']
            
            for process_type in process_types:
                if process_type in self.processed_data:
                    data = self.processed_data[process_type]
                    if data:
                        df = pd.concat(data, ignore_index=True)
                        df['process_stage'] = process_type
                        process_data.append(df)
            
            if process_data:
                end_to_end_report = pd.concat(process_data, ignore_index=True)
                
                # Sort by date if available
                if 'date' in end_to_end_report.columns:
                    end_to_end_report['date'] = pd.to_datetime(end_to_end_report['date'], errors='coerce')
                    end_to_end_report = end_to_end_report.sort_values('date')
                
                output_file = self.output_folder / "objective_4_end_to_end_process.csv"
                end_to_end_report.to_csv(output_file, index=False)
                self.logger.info(f"[SUCCESS] Objective 4 report saved: {output_file}")
                print(f"[SUCCESS] Objective 4 report saved: {output_file}")
            else:
                self.logger.warning("No process data available for Objective 4")
                
        except Exception as e:
            self.logger.error(f"Error generating Objective 4 report: {str(e)}")
    
    def generate_objective_5_report(self):
        """
        Objective 5: Stock balances per year (2022–2025), using Final Stock Lists + Adjustment reports.
        """
        self.logger.info("Generating Objective 5 report: Stock balances per year")
        
        try:
            balance_data = []
            balance_types = ['stock_balances', 'stock_adjustments']
            
            for balance_type in balance_types:
                if balance_type in self.processed_data:
                    data = self.processed_data[balance_type]
                    if data:
                        df = pd.concat(data, ignore_index=True)
                        df['balance_type'] = balance_type
                        balance_data.append(df)
            
            if balance_data:
                stock_balances_report = pd.concat(balance_data, ignore_index=True)
                
                # Extract year from date or filename
                if 'date' in stock_balances_report.columns:
                    stock_balances_report['date'] = pd.to_datetime(stock_balances_report['date'], errors='coerce')
                    stock_balances_report['year'] = stock_balances_report['date'].dt.year
                else:
                    # Try to extract year from filename
                    stock_balances_report['year'] = stock_balances_report['source_file'].str.extract(r'(202[2-5])')
                
                # Filter for 2022-2025
                mask = stock_balances_report['year'].isin([2022, 2023, 2024, 2025])
                yearly_balances = stock_balances_report[mask]
                
                output_file = self.output_folder / "objective_5_stock_balances_by_year.csv"
                yearly_balances.to_csv(output_file, index=False)
                self.logger.info(f"[SUCCESS] Objective 5 report saved: {output_file}")
                print(f"[SUCCESS] Objective 5 report saved: {output_file}")
            else:
                self.logger.warning("No stock balance data available for Objective 5")
                
        except Exception as e:
            self.logger.error(f"Error generating Objective 5 report: {str(e)}")
    
    def generate_all_reports(self):
        """Generate all analytical reports."""
        self.logger.info("Generating all analytical reports...")
        
        self.generate_objective_1_report()
        self.generate_objective_2_report()
        self.generate_objective_3_report()
        self.generate_objective_4_report()
        self.generate_objective_5_report()
        
        self.logger.info("All reports generated successfully!")
        print("All reports generated successfully!")
        
        # Generate relationship validation report
        self.generate_relationship_validation_report()
    
    def generate_relationship_validation_report(self):
        """Generate a report validating the corrected business relationships."""
        self.logger.info("Generating relationship validation report with corrected business logic...")
        
        validation_results = []
        
        try:
            # Load the necessary datasets
            grn_file = self.output_folder / 'hr995_grn.csv'
            issue_file = self.output_folder / 'hr995_issue.csv'
            voucher_file = self.output_folder / 'hr995_voucher.csv'
            hr390_file = self.output_folder / 'individual_hr390_movement_data.csv'
            hr185_file = self.output_folder / 'individual_hr185_transactions.csv'
            
            # Validate Issue → HR390 relationship
            if issue_file.exists() and hr390_file.exists():
                issue_df = pd.read_csv(issue_file)
                hr390_df = pd.read_csv(hr390_file)
                
                if 'requisition_no_normalized' in issue_df.columns and 'reference_normalized' in hr390_df.columns:
                    issue_refs = set(issue_df['requisition_no_normalized'].dropna())
                    hr390_refs = set(hr390_df['reference_normalized'].dropna())
                    
                    linked_issues = issue_refs & hr390_refs
                    coverage_rate = len(linked_issues) / len(issue_refs) * 100 if len(issue_refs) > 0 else 0
                    
                    validation_results.append({
                        'Relationship': 'Issue → HR390',
                        'Source_Records': len(issue_refs),
                        'Target_Records': len(hr390_refs),
                        'Linked_Records': len(linked_issues),
                        'Coverage_Rate': f"{coverage_rate:.1f}%",
                        'Status': 'Valid' if coverage_rate > 0 else 'No Links Found'
                    })
            
            # Validate GRN → HR185 relationship
            if grn_file.exists() and hr185_file.exists():
                grn_df = pd.read_csv(grn_file)
                hr185_df = pd.read_csv(hr185_file)
                
                if 'inv_no_normalized' in grn_df.columns and 'reference_normalized' in hr185_df.columns:
                    grn_refs = set(grn_df['inv_no_normalized'].dropna())
                    hr185_refs = set(hr185_df['reference_normalized'].dropna())
                    
                    linked_grns = grn_refs & hr185_refs
                    coverage_rate = len(linked_grns) / len(grn_refs) * 100 if len(grn_refs) > 0 else 0
                    
                    validation_results.append({
                        'Relationship': 'GRN → HR185',
                        'Source_Records': len(grn_refs),
                        'Target_Records': len(hr185_refs),
                        'Linked_Records': len(linked_grns),
                        'Coverage_Rate': f"{coverage_rate:.1f}%",
                        'Status': 'Valid' if coverage_rate > 0 else 'No Links Found'
                    })
            
            # Validate GRN → Voucher relationship
            if grn_file.exists() and voucher_file.exists():
                grn_df = pd.read_csv(grn_file)
                voucher_df = pd.read_csv(voucher_file)
                
                if 'voucher_normalized' in grn_df.columns and 'voucher_no_normalized' in voucher_df.columns:
                    grn_vouchers = set(grn_df['voucher_normalized'].dropna())
                    actual_vouchers = set(voucher_df['voucher_no_normalized'].dropna())
                    
                    linked_vouchers = grn_vouchers & actual_vouchers
                    coverage_rate = len(linked_vouchers) / len(grn_vouchers) * 100 if len(grn_vouchers) > 0 else 0
                    
                    validation_results.append({
                        'Relationship': 'GRN → Voucher',
                        'Source_Records': len(grn_vouchers),
                        'Target_Records': len(actual_vouchers),
                        'Linked_Records': len(linked_vouchers),
                        'Coverage_Rate': f"{coverage_rate:.1f}%",
                        'Status': 'Valid' if coverage_rate > 0 else 'No Links Found'
                    })
            
            # Save validation report
            if validation_results:
                validation_df = pd.DataFrame(validation_results)
                validation_file = self.output_folder / 'relationship_validation_report.csv'
                validation_df.to_csv(validation_file, index=False)
                
                self.logger.info(f"Relationship validation report saved to {validation_file}")
                print(f"\n✅ Relationship Validation Report Generated:")
                print("=" * 60)
                for result in validation_results:
                    print(f"📊 {result['Relationship']}: {result['Coverage_Rate']} coverage ({result['Status']})")
                print("=" * 60)
            else:
                self.logger.warning("No relationship validation results generated")
                
        except Exception as e:
            self.logger.error(f"Failed to generate relationship validation report: {str(e)}")
            print(f"⚠️ Failed to generate relationship validation report: {str(e)}")
    
    def run(self):
        """Run the complete data processing pipeline with corrected business logic."""
        self.logger.info("Starting Stock Data Processing Pipeline with Corrected Business Logic...")
        print("Starting Stock Data Processing Pipeline with Corrected Business Logic...")
        print("=" * 80)
        print("🔗 Implementing Corrected Business Relationships:")
        print("   • HR995Issue.Requisition No ↔ HR390.reference")
        print("   • HR995GRN.Inv No ↔ HR185.reference") 
        print("   • HR995GRN.Voucher ↔ HR995VOUCHER.Voucher No")
        print("=" * 80)
        
        # Process all files
        self.process_all_files()
        
        # Save consolidated data
        self.save_consolidated_data()
        
        # Generate analytical reports
        self.generate_all_reports()
        
        self.logger.info("Stock Data Processing Pipeline with corrected business logic completed successfully!")
        print("\n" + "="*80)
        print("✅ Stock Data Processing Pipeline with Corrected Business Logic Completed!")
        print(f"📁 Check the '{self.output_folder}' folder for all generated reports.")
        print("🔍 Review 'relationship_validation_report.csv' for business logic validation.")
        print("="*80)


def main():
    """Main function to run the stock data processor."""
    # Configuration
    data_folder = "Data Hand-Over"  # Current folder structure
    output_folder = "output"
    
    # Create and run the processor
    processor = StockDataProcessor(data_folder, output_folder)
    processor.run()


if __name__ == "__main__":
    main()
