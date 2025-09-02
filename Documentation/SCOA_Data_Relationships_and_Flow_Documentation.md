# SCOA Municipal Inventory System - Data Relationships & Flow Documentation

## Overview

This document explains the complete data flow and relationships within the SCOA (Standard Chart of Accounts) Municipal Inventory System based on comprehensive analysis and system improvements implemented.

---

## System Architecture

### Core Data Sources

1. **HR390** - Movement per Store (Transaction Records)
2. **HR995** - Authorization Records (Issue/GRN/Voucher/Redundancy)
3. **HR990** - Expenditure Statistics & User Information
4. **HR185** - Transactions per Supplier (Supplier-Transaction Linkage)
5. **Supplier Lists** - Vendor Information
6. **Stock Reconciliation** - Balance & Variance Data

---

## Data File Structure & Relationships

### 1. HR390 - Movement per Store
**Purpose**: Core transaction tracking system
**Files**: 
- `HR390 - Movement per Store - 202207 - 202306.pdf`
- `HR390 - Movement per Store - 202307 - 202406.pdf`
- `HR390 - Movement per Store - 202407 - 202506.pdf`

**Key Fields**:
- `item_no` - Item identifier (e.g., 201643)
- `date` - Transaction date (YYYYMMDD format)
- `transaction_type` - ISS (Issue), GRN (Goods Received Note), etc.
- `reference` - Reference number (e.g., '089322' with leading zeros)
- `issue_qty` - Quantity issued
- `issue_value` - Value of issue
- `grn_qty` - Goods received quantity
- `grn_value` - Goods received value
- `average_price` - Average unit price
- `variance_pct` - Variance percentage

**Critical Insight**: Reference numbers contain leading zeros (e.g., '089322')

### 2. HR995 - Authorization Records
**Purpose**: Authorization and approval tracking
**File Types**:
- `HR995issue.csv` - Issue authorizations
- `HR995grn.csv` - Goods Received Note authorizations
- `HR995vouch.csv` - Voucher authorizations
- `HR995redund.csv` - Redundancy authorizations

**Key Fields**:
- `Requisition No` - Authorization reference (e.g., 89322 without leading zero)
- `Issue Date` - Authorization date
- `Store No` - Store identifier
- `Item No` - Item identifier
- `Item Short Desc` - Item description
- `Issue Qty` - Authorized quantity
- `Issue Cost` - Authorized cost
- `Vote No` - Budget vote number

**Critical Insight**: Requisition numbers stored WITHOUT leading zeros (89322 vs 089322)

### 4. HR185 - Transactions per Supplier (NEW)
**Purpose**: Supplier payment and transaction tracking
**Files**:
- `1-HR185 - Transactions per Supplier - 202207 - 202306.pdf`
- `2-HR185 - Transactions per Supplier - 202307 - 202406.pdf`  
- `3-HR185 - Transactions per Supplier - 202407 - 202506.pdf`

**Key Fields**:
- `supplier_code` - Supplier identifier (e.g., 200692)
- `supplier_name` - Supplier company name
- `date` - Transaction date (YYYYMMDD format)
- `transaction_type` - INV (Invoice), CHQ (Cheque), VCH (Voucher)
- `reference` - Payment reference number
- `amount` - Transaction amount

**Critical HR185 Linking**:
- **INV transactions**: Reference with leading zeros (e.g., '0001015578') links to HR995grn Inv No (e.g., 1015578)
- **CHQ transactions**: Links to HR995vouch via Cheque/ACB/BDB/ELE No field (cheque payment processing)
- **VCH transactions**: Links to HR995vouch voucher records via direct reference matching

**Data Volumes**:
- Total suppliers: 79
- Total transactions: 2,284
- Transaction breakdown: INV (1,578), CHQ (537), VCH (169)

### 5. HR990 - Expenditure Statistics
**Purpose**: Financial reporting and user tracking
**Files**:
- `1-HR990 - Expenditure Statistics - 202207 - 202306.pdf`
- `2-HR990 - Expenditure Statistics - 202307 - 202406.pdf`
- `3-HR990 - Expenditure Statistics - 202407 - 202506.pdf`

**Contains**: User information, expenditure summaries, statistical analysis

---

## Data Relationships & Linking Logic

### Transaction-Type-Specific Linking

**Critical Discovery**: Different transaction types link to different HR995 datasets:

```
HR390 Transaction Type → HR995 Dataset → Linking Field
─────────────────────────────────────────────────────
ISS (Issue)            → HR995issue   → Requisition No
GRN (Goods Received)   → HR995grn     → GRN No
VOUCH (Voucher)        → HR995vouch   → Voucher No
```

### Reference Number Matching Challenge

**Problem Identified**: Format differences between systems
- **HR390**: References with leading zeros ('089322')
- **HR995**: References without leading zeros (89322)
- **Data Types**: HR995 stores as string/object, not integer

**Solution Implemented**: 4-Strategy Enhanced Matching

```python
# Strategy 1: Direct string match
hr995['Requisition No'].astype(str) == '089322'

# Strategy 2: Remove leading zeros from HR390 reference  
str(int('089322')) == '89322'  # Success!

# Strategy 3: Add leading zeros to HR995 data
hr995['Requisition No'].astype(str).str.zfill(6) == '089322'

# Strategy 4: Integer comparison
int('089322') == 89322  # Success!
```

### HR185 ↔ HR995grn Invoice Number Linking (NEW DISCOVERY)

**Critical HR185 Relationship**: Zero-padded invoice number matching
- **HR995grn Inv No**: 1015578 (7 digits, no leading zeros)
- **HR185 INV reference**: 0001015578 (10 digits, with leading zeros)
- **Link Method**: `str(int(hr185_reference))` removes leading zeros to match HR995grn Inv No
- **Match Rate**: 100% for tested INV transactions

**HR185 Transaction Types**:
```
Transaction Type → Link Destination → Purpose
─────────────────────────────────────────────
INV (Invoice)    → HR995grn Inv No        → Supplier payment for goods received
CHQ (Cheque)     → HR995vouch Cheq/ACB/BDB/ELE No → Cheque payment linked to voucher
VCH (Voucher)    → HR995vouch Voucher No  → Voucher-based payments
```

**Verified Link Examples**:
```
HR185: 0001015578 (INV) → HR995grn: 1015578 ✓
HR185: 0001015580 (INV) → HR995grn: 1015580 ✓  
HR185: 0001015582 (INV) → HR995grn: 1015582 ✓
```

**Amount Validation**: Perfect amount matching between linked HR185 and HR995grn records confirms link accuracy.

---

## Complete Data Flow

### 1. Transaction Initiation
```
User Request → Authorization (HR995) → Transaction (HR390) → Financial Impact (HR990)
```

### 2. Issue Transaction Flow
```
1. User requests item
2. Authorization created in HR995issue with Requisition No (e.g., 89322)
3. Issue transaction recorded in HR390 with reference (e.g., '089322')
4. Inventory levels updated
5. Financial impact recorded in HR990
```

### 3. Goods Received Flow
```
1. Purchase order placed
2. Goods received and recorded in HR390 (GRN transaction)
3. Authorization verified in HR995grn
4. Supplier payment processed
5. Inventory levels increased
```

---

## Data Quality & Validation

### Cross-Reference Success Rates
Based on system analysis:
- **Overall Success Rate**: 95.5%
- **ISS Transaction Matching**: 81.2% (before enhancement)
- **Enhanced Matching**: 99%+ (with leading zero handling)

### Common Data Issues

1. **Leading Zero Mismatch**
   - HR390: '089322'
   - HR995: 89322
   - **Solution**: Multi-strategy matching

2. **Transaction Type Confusion**
   - Different transaction types require different HR995 datasets
   - **Solution**: Transaction-type-specific linking

3. **Date Format Variations**
   - YYYYMMDD in HR390
   - Various formats in other systems
   - **Solution**: Flexible date parsing

---

## System Architecture Implementation

### Data Loading Strategy
```python
def load_comprehensive_data():
    return {
        'hr390_transactions': load_hr390_data(),
        'hr995_issue': load_hr995_issue(),
        'hr995_grn': load_hr995_grn(),
        'hr995_vouch': load_hr995_vouch(),
        'suppliers': load_supplier_data(),
        'stock_balances': load_stock_data()
    }
```

### Enhanced Reference Matching
```python
def get_transaction_trail(data, reference):
    trail = {}
    
    # 1. Find transaction in HR390
    # 2. Apply 4-strategy matching to HR995
    # 3. Cross-reference with suppliers
    # 4. Validate against stock balances
    
    return complete_audit_trail
```

---

## Business Rules & Compliance

### Municipal Financial Regulations
- All transactions must have proper authorization
- Audit trails must be complete and traceable
- PPE (Personal Protective Equipment) requires special tracking
- Electrical materials have enhanced monitoring

### Audit Requirements
1. **Authorization Verification**: Every ISS must link to HR995issue
2. **Supplier Validation**: All purchases must have verified suppliers
3. **Balance Reconciliation**: Physical vs. system inventory alignment
4. **Timing Compliance**: No unauthorized weekend/after-hours transactions

---

## PPE & Electrical Materials Special Handling

### Identification Criteria
```python
PPE_KEYWORDS = ['safety', 'protective', 'helmet', 'glove', 'vest', 'boot']
ELECTRICAL_KEYWORDS = ['electrical', 'cable', 'switch', 'meter', 'transformer']
```

### Enhanced Monitoring
- Higher scrutiny for quantity anomalies
- Mandatory authorization verification
- Special reporting requirements
- Cost threshold monitoring

---

## Performance Optimizations

### Caching Strategy
- Streamlit @st.cache_data for large datasets
- Selective loading based on analysis needs
- Progress indicators for long operations

### Memory Management
- Chunked processing for large files
- Selective column loading
- Efficient data type usage

---

## Anomaly Detection Logic

### Detection Categories

1. **Authorization Mismatches**
   - ISS transactions without HR995issue authorization
   - Enhanced with 4-strategy matching

2. **Balance Discrepancies** 
   - System vs. physical inventory differences
   - Uses movements data for accurate balance calculation

3. **Statistical Outliers**
   - Unusual quantities (beyond 1.5 * IQR)
   - High-value transactions
   - Timing anomalies

4. **PPE/Electrical Focus**
   - Specialized monitoring for critical materials
   - Enhanced validation requirements

---

## Technical Implementation Notes

### File Path Structure
```
Data Hand-Over/
├── 2023 List of Suppliers.xlsx
├── 2024 List of Suppliers.xlsx
├── HR995issue.xlsx / HR995issue.csv
├── HR995grn.xlsx
├── HR995vouch.xlsx
├── HR995redund.xlsx
├── HR185/ (Supplier transactions)
├── HR390/ (Movement reports)
├── HR990/ (Expenditure statistics)
└── Stock Balances/ (Inventory data)
```

### Data Conversion Pipeline
1. PDF → Text extraction → CSV conversion
2. Excel → CSV standardization
3. Column name standardization
4. Data type optimization

---

## Usage Guidelines

### For Analysts
1. Always use enhanced matching for authorization verification
2. Consider transaction-type-specific linking
3. Validate PPE/Electrical materials separately
4. Cross-reference with multiple data sources

### For Auditors
1. Focus on complete transaction trails
2. Verify authorization coverage rates
3. Investigate timing anomalies
4. Validate balance reconciliations

### For System Administrators
1. Monitor data loading performance
2. Ensure file accessibility
3. Validate data conversion accuracy
4. Maintain backup procedures

---

## Future Enhancements

### Planned Improvements
1. Real-time data integration
2. Automated anomaly alerts
3. Enhanced supplier validation
4. Mobile access capabilities

### Scalability Considerations
1. Database integration for large volumes
2. API development for system integration
3. Advanced analytics and machine learning
4. Compliance automation

---

## Troubleshooting Guide

### Common Issues

1. **Reference Not Found**
   - Check for leading zero differences
   - Verify transaction type and corresponding HR995 dataset
   - Confirm date ranges and file availability

2. **Performance Issues**
   - Clear Streamlit cache
   - Restart application
   - Check file sizes and memory usage

3. **Data Quality Problems**
   - Validate source file integrity
   - Check conversion accuracy
   - Verify column mapping

---

## Contact & Support

For technical issues or enhancement requests:
- System Administrator: [Contact Info]
- Data Analyst Team: [Contact Info]
- Municipal Finance Department: [Contact Info]

---

*Document Version: 1.0*  
*Last Updated: September 1, 2025*  
*Based on: Comprehensive system analysis and enhancement implementation*
