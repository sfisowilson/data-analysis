# SCOA Database Implementation - Complete Production System

## Overview

This is a comprehensive SQL Server database implementation for the Standard Chart of Accounts (SCOA) inventory and financial tracking system. The system provides complete audit trails, anomaly detection, and transaction tracking across multiple data sources with sophisticated nested data handling capabilities.

## System Architecture

### Four-Layer Data Architecture

1. **HR390** - Store Movement Authorization
   - Movement requests and authorizations
   - Store-to-store transfers
   - Authorization workflow tracking

2. **HR995** - Transaction Processing (Type-Specific)
   - **HR995issue** - Issues and distributions
   - **HR995grn** - Goods Received Notes (invoices)
   - **HR995vouch** - Vouchers and payments

3. **HR185** - Supplier Transaction Tracking
   - Complete supplier payment records
   - Links to HR995 via reference numbers with zero-padding
   - Nested data structure: "Supplier : code name" followed by transaction lines

4. **HR990** - User Activity Tracking
   - User expenditure statistics
   - Department tracking
   - Nested ENQ patterns: "ENQ### - ##### - NAME (DEPARTMENT)"

### Transaction Linking Matrix

| Transaction Type | HR185 Source | HR995 Target | Link Field | Matching Strategy |
|------------------|--------------|--------------|------------|-------------------|
| INV (Invoices)   | HR185        | HR995grn     | Inv No     | Zero-padding removal |
| CHQ (Cheques)    | HR185        | HR995vouch   | Cheq/ACB/BDB/ELE No | Direct reference |
| VCH (Vouchers)   | HR185        | HR995vouch   | Voucher No | Direct reference |
| ISS (Issues)     | HR185        | HR995issue   | Issue No   | Direct reference |
| GRN (Goods Rec.) | HR185        | HR995grn     | GRN No     | Direct reference |

## Database Schema

### Core Tables

#### 1. suppliers
- `supplier_id` (Primary Key)
- `supplier_code` (Unique)
- `supplier_name`
- `contact_info`
- `status`

#### 2. items
- `item_id` (Primary Key)
- `item_code` (Unique)
- `item_name`
- `category` (PPE/Electrical classification)
- `unit_of_measure`

#### 3. stores
- `store_id` (Primary Key)
- `store_code` (Unique)
- `store_name`
- `location`

#### 4. hr390_movements
- `movement_id` (Primary Key)
- `reference_no` with computed `reference_no_clean`
- Links to stores, items, and users
- Authorization status and workflow

#### 5. hr995_issues/grn/vouchers
- Type-specific transaction tables
- Reference number linking with computed clean fields
- Amount and status tracking

#### 6. hr185_transactions
- `transaction_id` (Primary Key)
- `transaction_type` (INV/CHQ/VCH/ISS/GRN)
- `reference_no` with computed `reference_no_clean`
- Links to suppliers
- Nested data from text files

#### 7. hr990_users
- `user_id` (Primary Key)
- User information extracted from ENQ patterns
- Department and reference linking

#### 8. audit_trail_links
- Central relationship tracking
- Four-layer transaction trail mapping
- Anomaly detection flags

### Key Features

#### 1. Reference Number Matching
- **Computed Columns**: Automatic cleaning of reference numbers
- **Zero-Padding Handling**: Converts "0001015578" ↔ "1015578"
- **Four-Strategy Matching**: Direct, cleaned, zero-padded, fuzzy
- **Performance Indexes**: Optimized for fast lookups

#### 2. Nested Data Processing
- **HR185 Parser**: Handles "Supplier : code name" + transaction lines
- **HR990 Parser**: Extracts ENQ patterns with departments
- **Text Mining**: Reference number extraction from context
- **Bulk Import**: Efficient staging table processing

#### 3. Anomaly Detection
- **Statistical Analysis**: Outlier detection algorithms
- **Transaction Gaps**: Missing audit trail identification
- **Amount Discrepancies**: Cross-system validation
- **Orphaned Records**: Unlinked transaction identification

#### 4. Audit Trail Tracking
- **Complete Lineage**: Authorization → Processing → Payment → User
- **Link Validation**: Real-time relationship verification
- **Missing Link Detection**: Automated gap identification
- **Performance Monitoring**: Query execution tracking

## Installation and Setup

### Prerequisites

1. **SQL Server 2017+** with full-text search
2. **PowerShell 5.1+** with SqlServer module
3. **Excel** (for file conversion)
4. **Administrator privileges** (for database creation)

### Quick Start

1. **Run the deployment batch file**:
   ```batch
   Deploy-SCOA.bat
   ```

2. **Or run PowerShell directly**:
   ```powershell
   .\Deploy-SCOA-Database.ps1 -ServerName "localhost" -DatabaseName "SCOA_Inventory"
   ```

### Manual Setup

1. **Create Database**:
   ```sql
   CREATE DATABASE SCOA_Inventory;
   ```

2. **Execute Schema Setup**:
   ```sql
   EXEC sp_executesql @sql = 'SCOA_Database_Setup.sql'
   ```

3. **Execute Import Procedures**:
   ```sql
   EXEC sp_executesql @sql = 'SCOA_Data_Import_Procedures.sql'
   ```

4. **Run System Setup**:
   ```sql
   EXEC sp_SetupSCOASystem;
   ```

5. **Build Audit Trails**:
   ```sql
   EXEC sp_BuildAuditTrailLinks;
   ```

## Data Import Process

### 1. Excel Files
- `2024 List of Suppliers.xlsx` → `suppliers` table
- `HR995issue.xlsx` → `hr995_issues` table
- `HR995grn.xlsx` → `hr995_grn` table
- `HR995vouch.xlsx` → `hr995_vouchers` table

### 2. PDF Text Extraction
- HR185 PDFs → Nested supplier transaction data
- HR390 PDFs → Store movement records
- HR990 PDFs → User expenditure statistics

### 3. Nested Data Processing
```sql
-- HR185 Example Structure
Supplier : 200692 FRIEDENTHAL EN SEUNS TA CHAMPION WHEEL & TYRE
20240115 INV 0001015578     12500.00
20240118 CHQ 089322          8750.00
20240120 VCH 445621          3750.00

-- HR990 Example Structure
ENQ623 - 37211 - S. MOABELO (INSURANCE)
ENQ624 - 37212 - J. SMITH (PROCUREMENT)
```

### 4. Staging Tables
- Temporary staging tables for bulk processing
- Data validation and cleaning
- Error handling and logging

## Stored Procedures

### Core System Procedures

#### sp_SetupSCOASystem
- Master setup procedure
- Creates all tables and relationships
- Initializes system configuration

#### sp_CreateSCOATables
- Table creation with proper schema
- Computed columns and indexes
- Foreign key relationships

#### sp_BuildAuditTrailLinks
- Establishes cross-system relationships
- Four-layer transaction linking
- Missing link identification

### Data Import Procedures

#### sp_ImportHR185Data
- Parses nested supplier transaction structure
- Handles "Supplier : code name" format
- Extracts transaction lines with dates, types, references, amounts

#### sp_ImportHR990Data
- Extracts user information from ENQ patterns
- Identifies departments and reference numbers
- Links users to transaction activities

#### sp_ImportExcelData
- Bulk Excel file import using OPENROWSET
- Dynamic column mapping
- Data type validation

#### sp_ImportAllSCOAData
- Orchestrates complete data import
- Handles dependencies and sequencing
- Error recovery and logging

### Analysis Procedures

#### sp_GenerateAnomalyReport
- Comprehensive anomaly detection
- Statistical outlier identification
- Missing audit trail detection

#### sp_AdvancedAnomalyDetection
- Multi-layer anomaly analysis
- PPE/Electrical material focus
- Cross-system validation

## Views and Reports

### v_CompleteTransactionTrail
- Four-layer transaction visibility
- Authorization → Processing → Payment → User
- Complete audit trail with missing link identification

### v_AnomalyDetection
- Real-time anomaly identification
- Statistical outlier detection
- Missing relationship alerts

### v_PPE_Electrical_Tracking
- Specialized tracking for critical materials
- Enhanced monitoring and alerts
- Compliance reporting

## Anomaly Detection Features

### 1. Statistical Analysis
- **Z-Score Outliers**: Amount-based anomaly detection
- **Interquartile Range**: Distribution-based analysis
- **Trend Analysis**: Time-series anomaly identification
- **Pattern Recognition**: Unusual transaction patterns

### 2. Audit Trail Gaps
- **Missing Authorizations**: Transactions without HR390 approval
- **Orphaned Payments**: HR185 without HR995 backing
- **Incomplete Workflows**: Broken process chains
- **Reference Mismatches**: Link validation failures

### 3. Amount Discrepancies
- **Cross-System Validation**: Amount consistency checks
- **Tolerance Thresholds**: Acceptable variance limits
- **Currency Validation**: Format and calculation checks
- **Duplicate Detection**: Same transaction multiple systems

### 4. PPE/Electrical Focus
- **Critical Material Tracking**: Enhanced monitoring
- **Compliance Alerts**: Regulatory requirement checks
- **Usage Pattern Analysis**: Unusual consumption patterns
- **Cost Center Validation**: Department allocation checks

## Performance Optimization

### 1. Indexing Strategy
- **Clustered Indexes**: Primary keys and main queries
- **Non-Clustered Indexes**: Reference number lookups
- **Computed Column Indexes**: Reference_no_clean fields
- **Composite Indexes**: Multi-column query optimization

### 2. Query Optimization
- **Execution Plans**: Monitored and optimized
- **Statistics Updates**: Automated maintenance
- **Query Hints**: Strategic force operations
- **Partition Strategies**: Large table management

### 3. Caching and Memory
- **Buffer Pool**: Optimized memory allocation
- **Plan Cache**: Stored procedure optimization
- **TempDB**: Efficient temporary storage
- **Connection Pooling**: Resource management

## Security and Compliance

### 1. Access Control
- **Role-Based Security**: Departmental access levels
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: Sensitive field protection
- **Backup Security**: Encrypted backup strategies

### 2. Data Integrity
- **Foreign Key Constraints**: Referential integrity
- **Check Constraints**: Data validation rules
- **Triggers**: Business rule enforcement
- **Transaction Isolation**: Concurrent access protection

### 3. Compliance Features
- **Audit Trail Requirements**: Complete transaction history
- **Retention Policies**: Data lifecycle management
- **Regulatory Reporting**: Standard compliance reports
- **Change Tracking**: Data modification history

## Monitoring and Maintenance

### 1. Health Monitoring
- **Link Validation**: Automated relationship checking
- **Data Quality Metrics**: Completeness and accuracy
- **Performance Counters**: System health indicators
- **Alert Systems**: Proactive issue identification

### 2. Maintenance Procedures
- **Index Maintenance**: Automated reorganization
- **Statistics Updates**: Query optimization
- **Backup Procedures**: Automated and tested
- **Archive Strategies**: Historical data management

## Integration with Streamlit Application

The database integrates seamlessly with the Streamlit anomaly detection application:

1. **Real-time Queries**: Direct database connectivity
2. **Interactive Dashboards**: Dynamic data visualization
3. **Drill-down Capability**: Detailed transaction analysis
4. **Export Functions**: Report generation and sharing

### Starting the Application
```bash
streamlit run pages/4_🚨_Anomaly_Detection.py
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify SQL Server is running
   - Check firewall settings
   - Validate connection string

2. **Permission Errors**
   - Run as administrator
   - Check database permissions
   - Verify OPENROWSET settings

3. **Import Failures**
   - Check file paths and formats
   - Validate Excel structure
   - Review error logs

4. **Performance Issues**
   - Update statistics
   - Rebuild indexes
   - Check query plans

### Support and Documentation

- **System Documentation**: Complete SCOA_*.md files
- **Code Comments**: Inline documentation
- **Error Handling**: Comprehensive logging
- **Best Practices**: Implementation guidelines

## Future Enhancements

1. **Real-time Processing**: Streaming data integration
2. **Machine Learning**: Advanced anomaly detection
3. **API Integration**: External system connectivity
4. **Mobile Interface**: Mobile-responsive dashboard
5. **Advanced Analytics**: Predictive modeling capabilities

---

## Quick Command Reference

### Database Operations
```sql
-- Setup complete system
EXEC sp_SetupSCOASystem;

-- Import all data
EXEC sp_ImportAllSCOAData;

-- Build relationships
EXEC sp_BuildAuditTrailLinks;

-- Generate anomaly report
EXEC sp_GenerateAnomalyReport;

-- Advanced anomaly detection
EXEC sp_AdvancedAnomalyDetection;
```

### PowerShell Deployment
```powershell
# Basic deployment
.\Deploy-SCOA-Database.ps1

# Custom server/database
.\Deploy-SCOA-Database.ps1 -ServerName "MyServer" -DatabaseName "MyDB"

# With credentials
.\Deploy-SCOA-Database.ps1 -UseIntegratedSecurity:$false -Username "user" -Password "pass"
```

### Streamlit Application
```bash
# Start application
streamlit run pages/4_🚨_Anomaly_Detection.py

# Install dependencies
pip install streamlit plotly pandas pyodbc
```

---

**Version**: 1.0  
**Last Updated**: $(Get-Date -Format "yyyy-MM-dd")  
**System**: SCOA Municipal Financial Tracking  
**Architecture**: Four-Layer with Complete Audit Trail  
