# 📊 Stock Data Analytics Dashboard

A comprehensive Python-based data analytics platform for stock management analysis, featuring interactive dashboards, automated reporting, and multi-format hosting solutions.

## 🎯 Project Overview

This project provides end-to-end analysis of stock data across multiple formats (Excel, PDF, CSV) with automated processing, visualization, and reporting capabilities. It fulfills 5 key business objectives for stock management analysis.

## 🌟 Key Features

### 📈 **Interactive Dashboard**
- **7 comprehensive tabs**: Financial, Inventory, Supplier, Operational, Anomaly Detection, PDF Reports, Data Tables
- **35+ interactive charts** with tooltips and drill-down capabilities
- **Advanced filtering** by supplier, date ranges, and custom criteria
- **Real-time data processing** with 169K+ records

### 🔧 **Data Processing Pipeline**
- **Multi-format support**: Excel (.xlsx), PDF, CSV, TXT files
- **Recursive processing**: Handles nested folder structures
- **PDF extraction**: Custom parsing for HR185/HR990 reports
- **Data validation**: Comprehensive error checking and logging

### 🎯 **Business Objectives Coverage**
1. **Item Request Frequency (2022-2025)**: Analysis by supplier and timeframe
2. **Stock Requisition vs GRN Matching**: Audit trail verification
3. **Stock Movement Audit Trail**: Complete transaction tracking
4. **End-to-End Process Analysis**: Comprehensive workflow reporting
5. **Stock Balance Analysis**: Multi-year balance reporting

### 🌐 **Hosting Solutions**
- **Interactive Dashboard**: Streamlit-based web application
- **Static HTML Export**: IIS-compatible static reports
- **Docker Support**: Containerized deployment option
- **Cloud Ready**: Heroku, AWS, Azure deployment configurations

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Windows/Linux/macOS
- 4GB+ RAM recommended

### Installation
```bash
# Clone the repository
git clone https://bitbucket.org/sfisowilson/data-analysis.git
cd data-analysis

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# 1. Process all data files
python stock_data_processor.py

# 2. Launch interactive dashboard
streamlit run enhanced_dashboard.py

# 3. Export static HTML for IIS
python export_static_dashboard.py

# 4. Verify requirements compliance
python requirements_check.py
```

## 📁 Project Structure

```
data-analysis/
├── 📊 Core Applications
│   ├── enhanced_dashboard.py          # Main interactive dashboard
│   ├── stock_data_processor.py        # Data processing pipeline
│   └── export_static_dashboard.py     # Static HTML exporter
│
├── 🔧 Utilities & Tools
│   ├── extract_pdf_data_v2.py         # PDF data extraction
│   ├── fix_objective_reports.py       # Report validation
│   ├── requirements_check.py          # Compliance verification
│   └── test_data_tables.py           # Data validation tests
│
├── 📋 Configuration & Deployment
│   ├── requirements.txt               # Python dependencies
│   ├── deploy_to_iis.bat             # IIS deployment script
│   └── launch_dashboard_enhanced.py   # Dashboard launcher
│
├── 📂 Data Folders
│   ├── Data Hand-Over/                # Source data files
│   ├── output/                        # Processed CSV files
│   └── html_reports/                  # Static HTML exports
│
└── 📖 Documentation
    ├── IIS_DEPLOYMENT_GUIDE.md        # IIS hosting guide
    ├── IIS_HOSTING_OPTIONS.md         # Alternative hosting options
    ├── DATA_TABLES_SUMMARY.md         # Data tables feature guide
    └── PROJECT_SUMMARY.md             # Comprehensive project overview
```

## 🔍 Requirements Compliance

✅ **100% Compliance** with all 5 business objectives:

1. **Objective 1**: Item frequency analysis (3,292 records)
2. **Objective 2**: Stock audit trail (28,642 records)  
3. **Objective 3**: Movement audit trail (comprehensive)
4. **Objective 4**: End-to-end process (40,365 records)
5. **Objective 5**: Stock balances by year (complete coverage)

---

**Built with ❤️ for comprehensive stock data analysis**

*Last updated: August 31, 2025*

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the processor:**
   ```bash
   python stock_data_processor.py
   ```

## Input Data Structure
The tool expects data files in the current directory and subdirectories. It will automatically:
- Process all .txt, .xlsx, and .pdf files
- Extract tables from PDFs
- Read all sheets from Excel files
- Handle different separators in text files

## Standard Column Mapping
The tool maps various column names to standard formats:
- **Date**: date, transaction_date, doc_date, created_date
- **Item Code**: item_code, itemcode, item, code, product_code
- **Description**: description, item_description, product_description, desc
- **Supplier**: supplier, vendor, supplier_name, vendor_name
- **Quantity**: quantity, qty, amount, units
- **Official**: official, officer, created_by, user, staff
- **Document Type**: document_type, doc_type, type, transaction_type

## Output Reports

### Data Files
1. **all_stock_data.csv** - Master consolidated file with all data
2. **Individual report CSVs** - Separate files per report type:
   - hr995_grn.csv
   - hr995_voucher.csv
   - hr995_issue.csv
   - hr995_redundant.csv
   - hr990_expenditure.csv
   - hr185_transactions.csv
   - suppliers.csv
   - stock_balances.csv
   - stock_adjustments.csv

### Analysis Reports
1. **objective_1_item_frequency_by_supplier.csv**
   - Frequency of requesting items from specific suppliers (2022–2025)

2. **objective_2_stock_audit_trail.csv**
   - Stock requisition vs GRN audit trail by officials

3. **objective_3_hr995_report.csv**
   - Comprehensive HR995 report combining all HR995 data

4. **objective_4_end_to_end_process.csv**
   - End-to-end process report (GRN → Refund → Vouchers → Stock Balances)

5. **objective_5_stock_balances_by_year.csv**
   - Stock balances per year (2022–2025) with adjustments

## File Type Recognition
The tool automatically categorizes files based on filename patterns:
- **HR995 GRN**: Files containing "hr995grn" or "grn"
- **HR995 Voucher**: Files containing "hr995vouch" or "voucher"
- **HR995 Issue**: Files containing "hr995issue" or "issue"
- **HR995 Redundant**: Files containing "hr995redund" or "redundant"
- **HR990 Expenditure**: Files containing "hr990"
- **HR185 Transactions**: Files containing "hr185"
- **Suppliers**: Files containing "supplier"
- **Stock Balances**: Files containing both "stock" and "balance"
- **Stock Adjustments**: Files containing both "stock" and "adjustment"

## Logging
- All operations are logged to `stock_processor.log`
- Console output shows progress and confirmations
- Error handling with detailed error messages

## Error Handling
- Graceful handling of corrupted or unreadable files
- Automatic encoding detection for text files
- Fallback options for different file formats
- Comprehensive error logging

## Customization
You can modify the following in the code:
- Column mapping in `self.standard_columns`
- File type recognition in `_determine_report_type()`
- Data cleaning rules in `clean_data()`
- Report generation logic in `generate_objective_*_report()` methods

## Dependencies
- pandas: Data manipulation and analysis
- openpyxl: Excel file handling
- pdfplumber: PDF table extraction
- python-dateutil: Date parsing
- numpy: Numerical operations
