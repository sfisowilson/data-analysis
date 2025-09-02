# HR185-HR995 Linking Stored Procedures

## Overview
Successfully created stored procedures to link HR185 transactions with HR995 records based on transaction type and reference number matching.

## Created Stored Procedures

### 1. `sp_GetHR995GRN_ByHR185Reference`
**Purpose**: Get HR995 GRN records linked to HR185 transactions
**Parameters**:
- `@TransactionType` (NVARCHAR(10)): 'INV' or 'CHQ' 
- `@ReferenceNo` (NVARCHAR(50)): Reference number to match

**Matching Logic**:
- INV type → matches with `hr995_grn.inv_no`
- CHQ type → matches with `hr995_grn.cheque_no`

**Usage Example**:
```sql
EXEC sp_GetHR995GRN_ByHR185Reference @TransactionType = 'INV', @ReferenceNo = '1015875';
```

### 2. `sp_GetHR995Voucher_ByHR185Reference`
**Purpose**: Get HR995 voucher records linked to HR185 VCH transactions
**Parameters**:
- `@ReferenceNo` (NVARCHAR(50)): Voucher reference number

**Matching Logic**:
- VCH type → matches with `hr995_vouchers.voucher_no`

**Usage Example**:
```sql
EXEC sp_GetHR995Voucher_ByHR185Reference @ReferenceNo = 'SINA000194';
```

### 3. `sp_GetAllHR995Links_ByHR185Transaction`
**Purpose**: Get all HR995 records (GRN + Vouchers) linked to a specific HR185 transaction
**Parameters**:
- `@TransactionId` (INT): HR185 transaction ID

**Returns**: 
- HR185 transaction details
- All linked HR995 GRN records (for INV/CHQ types)
- All linked HR995 voucher records (for VCH types)

**Usage Example**:
```sql
EXEC sp_GetAllHR995Links_ByHR185Transaction @TransactionId = 5;
```

### 4. `sp_GetHR185TransactionSummary_WithLinks`
**Purpose**: Get HR185 transaction summary with link status indicators
**Parameters**:
- `@TransactionType` (NVARCHAR(10), Optional): Filter by transaction type
- `@FinPeriod` (NVARCHAR(20), Optional): Filter by financial period

**Returns**: Transaction list with:
- `grn_link_status`: 'LINKED' / 'NOT_LINKED' / 'N/A'
- `voucher_link_status`: 'LINKED' / 'NOT_LINKED' / 'N/A'
- `linked_records_count`: Number of linked records

**Usage Example**:
```sql
EXEC sp_GetHR185TransactionSummary_WithLinks @TransactionType = 'INV';
```

## Linking Performance Results

Based on testing with your municipal data:

| Transaction Type | Total Transactions | Linked | Link Rate |
|------------------|-------------------|--------|-----------|
| **INV** (Invoices) | 1,578 | 1,548 | **98.10%** |
| **CHQ** (Cheques) | 537 | 0 | **0.00%** |
| **VCH** (Vouchers) | 169 | 145 | **85.80%** |
| **TOTAL** | 2,284 | 1,693 | **74.12%** |

## Key Findings

### Excellent INV Linking (98.10%)
- Invoice transactions have excellent linkage to HR995 GRN records
- This suggests strong data integrity between HR185 and HR995 GRN systems
- Invoice numbers are consistently maintained across systems

### No CHQ Linking (0.00%)
- Cheque transactions from HR185 don't link to HR995 GRN cheque numbers
- This may indicate:
  - Different cheque numbering systems
  - Cheques processed through different workflows
  - Data entry inconsistencies in cheque number formats

### Good VCH Linking (85.80%)
- Voucher transactions have good linkage to HR995 voucher records
- 14.20% unlinked vouchers may be due to:
  - Different voucher numbering sequences
  - Vouchers processed outside the GRN system
  - Timing differences in data capture

## Business Value

### Payment Verification
These procedures enable you to:
1. **Track Invoice Payments**: 98% of invoices can be traced through the system
2. **Audit Transaction Trails**: Link supplier transactions to physical goods receipts
3. **Identify Data Gaps**: Spot unlinked transactions that need investigation
4. **Financial Reconciliation**: Match financial records with inventory movements

### Reporting Capabilities
- Generate comprehensive transaction trail reports
- Identify unprocessed or incomplete transactions
- Create supplier payment status reports
- Track procurement-to-payment cycles

## Usage in Dashboard

These procedures can be integrated into your Streamlit dashboard to provide:
- Real-time linking statistics
- Transaction drill-down capabilities
- Payment status tracking
- Data quality monitoring

## Next Steps

1. **Investigate CHQ Linking**: Analyze why cheque transactions aren't linking
2. **Enhance VCH Matching**: Improve voucher linking accuracy
3. **Create Report Views**: Build dashboard reports using these procedures
4. **Add Audit Trail**: Expand procedures to include HR390 movement links

The stored procedures provide a solid foundation for comprehensive financial transaction analysis and reporting in your SCOA system.
