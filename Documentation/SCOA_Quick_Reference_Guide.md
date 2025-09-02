# SCOA System - Quick Reference Guide

## Essential Data Relationships - At a Glance

### 🔗 Primary Linking Rules

| Source | Target | Link Field | Notes |
|--------|--------|------------|-------|
| HR390 ISS | HR995issue | reference ↔ Requisition No | **Leading zero mismatch!** |
| HR390 GRN | HR995grn | reference ↔ GRN No | Format varies |
| HR390 VOUCH | HR995vouch | reference ↔ Voucher No | Multiple formats |
| **HR995grn** | **HR185 INV** | **Inv No ↔ reference** | **Zero-padded link (NEW)** |
| All Systems | Suppliers | item_no ↔ Item codes | String matching |

### 🆕 HR185 Supplier Payment Links (NEW)

```bash
# HR185 Invoice Payment Linking (CONFIRMED)
HR995grn: Inv No = 1015578        # 7 digits, no leading zeros
HR185:    reference = 0001015578   # 10 digits, with leading zeros

# Link Method: Remove leading zeros from HR185
cleaned_ref = str(int("0001015578"))  # → "1015578"
✅ Perfect match with 100% accuracy

# HR185 Transaction Types
INV → Links to HR995grn (supplier payments)
CHQ → Links to HR995vouch via Cheq/ACB/BDB/ELE No (cheque payments)
VCH → Links to HR995vouch (voucher payments)
```

### ⚠️ Critical Data Format Issues

```bash
# The Leading Zero Problem (SOLVED)
HR390: reference = '089322'  # String with leading zeros
HR995: Requisition No = 89322  # Integer/String without leading zeros

# Solution: 4-Strategy Enhanced Matching
✅ Strategy 1: Direct string match
✅ Strategy 2: Remove leading zeros from HR390
✅ Strategy 3: Zero-pad HR995 data  
✅ Strategy 4: Integer comparison
```

### 📁 File Structure Quick Map

```
Data Hand-Over/Data Hand-Over/
├── HR995issue.csv          # Issue authorizations
├── HR995grn.csv           # Goods received authorizations  
├── HR995vouch.csv         # Voucher authorizations
├── HR995redund.csv        # Redundancy records
├── HR185/                 # Supplier payment records (NEW)
│   ├── 1-HR185*202207-202306.pdf
│   ├── 2-HR185*202307-202406.pdf  
│   └── 3-HR185*202407-202506.pdf
├── HR390/                 # Movement reports
│   ├── HR390*202207-202306.pdf
│   ├── HR390*202307-202406.pdf
│   └── HR390*202407-202506.pdf
├── HR990/                 # Expenditure statistics  
│   ├── 1-HR990*202207-202306.pdf
│   ├── 2-HR990*202307-202406.pdf
│   └── 3-HR990*202407-202506.pdf
├── hr390_structured/      # Processed movement data
│   └── *_transactions.csv
├── converted_csv/         # All converted data including HR185
└── Stock Balances/        # Inventory reconciliation
```

## 🏗️ Four-Layer System Architecture (UPDATED)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   HR390     │ ──▶│   HR995     │ ──▶│   HR185     │    │   HR990     │
│ Inventory   │    │Authorization│    │  Supplier   │    │ Statistics  │
│ Movements   │    │ & Approvals │    │  Payments   │    │ & Reports   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                    │                    │                │
Stock Issues        Purchase Orders     Invoice Payments   Financial
Receipts           GRN Records         Cheque Payments    Analytics  
Adjustments        Vouchers            Voucher Payments   User Reports
Transfers          Approvals           Settlements        Expenditure
```

### 🔄 Complete Transaction Lifecycle

```
STEP 1: Stock Movement (HR390)
    Reference: 089322, Type: ISS
           ↓
STEP 2: Authorization (HR995issue)  
    Requisition No: 89322 (linked by reference)
           ↓
STEP 3: Goods Receipt (HR995grn)
    GRN No: 27210, Inv No: 1015578
           ↓  
STEP 4: Supplier Payment (HR185)
    Reference: 0001015578, Type: INV (linked by zero-padded invoice)
           ↓
STEP 5: Financial Reporting (HR990)
    Expenditure statistics and analytics
```

---

## 🚀 Quick Start Commands

### Load Core Data
```python
# Load all data sources
data = load_comprehensive_data()

# Check what's available
print("Available datasets:", list(data.keys()))
```

### Test Reference Matching
```python
# Test specific reference
reference = '089322'
trail = get_transaction_trail(data, reference=reference)
print(f"Authorization found: {'authorization' in trail}")
```

### Run Anomaly Detection
```python
# Detect all anomalies with enhanced matching
anomalies = detect_inventory_anomalies(data)
print(f"Authorization issues: {len(anomalies['authorization_mismatches'])}")
```

---

## 🔍 Troubleshooting Checklist

### Reference Not Matching?
- [ ] Check for leading zeros ('089322' vs '89322')
- [ ] Verify transaction type (ISS → HR995issue)
- [ ] Confirm data files are loaded
- [ ] Test with enhanced matching function

### Performance Issues?
- [ ] Clear Streamlit cache (`@st.cache_data.clear()`)
- [ ] Restart application
- [ ] Check file sizes (large PDFs slow conversion)
- [ ] Use selective loading for testing

### Data Quality Problems?
- [ ] Validate source files exist
- [ ] Check PDF conversion accuracy  
- [ ] Verify column names match expected format
- [ ] Test with known good records

---

## 📊 Key Metrics to Monitor

### System Health
- **Cross-Reference Success Rate**: Target >95%
- **Authorization Coverage**: Target 100% for ISS
- **Data Loading Time**: <30 seconds for full load
- **Memory Usage**: Monitor for large datasets

### Business Metrics  
- **PPE/Electrical Transaction Volume**: Track safety compliance
- **Weekend Transaction Count**: Flag unusual activity
- **High-Value Outliers**: >1.5 * IQR threshold
- **Supplier Coverage**: Verify all items have suppliers

---

## 🛠️ Common Code Patterns

### Safe Data Access
```python
# Always check if data exists
if 'hr995_issue' in data and not data['hr995_issue'].empty:
    # Process data
    pass
else:
    st.warning("HR995 issue data not available")
```

### Flexible Column Detection
```python
# Use helper function for varying column names
item_col = find_item_column(df)  # Handles 'item_no', 'Item', etc.
if item_col:
    items = df[item_col].unique()
```

### Enhanced Reference Matching
```python
# Don't use simple integer matching
# OLD (fails): hr995[hr995['Requisition No'] == int(reference)]
# NEW (works): Use get_transaction_trail() with 4-strategy matching
```

---

## 🎯 Business Rules Summary

### Authorization Requirements
- **ISS transactions**: Must have HR995issue authorization
- **GRN transactions**: Must have HR995grn authorization  
- **High-value items**: Additional scrutiny required
- **PPE/Electrical**: Mandatory authorization verification

### Audit Trail Standards
- **Complete linkage**: HR390 ↔ HR995 ↔ Suppliers ↔ HR990
- **Timing validation**: No unauthorized weekend transactions
- **Balance reconciliation**: System vs physical inventory
- **Exception reporting**: All anomalies must be documented

### Data Quality Standards  
- **Reference format**: Handle leading zero variations
- **Date consistency**: YYYYMMDD standard format
- **Item identification**: Consistent across all systems
- **Currency values**: Proper decimal handling

---

## 📋 Testing Scenarios

### Regression Tests
```python
# Test known good reference
assert get_transaction_trail(data, '089322')['authorization'] is not None

# Test edge cases  
assert handle_reference_formats(['089322', '89322', 89322])

# Test transaction type routing
assert get_hr995_dataset('ISS') == 'hr995_issue'
assert get_hr995_dataset('GRN') == 'hr995_grn'
```

### Performance Tests
```python
# Load time benchmark
import time
start = time.time()
data = load_comprehensive_data()
load_time = time.time() - start
assert load_time < 30  # Should load in under 30 seconds
```

---

## 🚨 Known Issues & Workarounds

### Issue: Leading Zero Loss
**Problem**: Integer conversion strips leading zeros  
**Workaround**: Use string-based matching with enhanced strategies  
**Status**: ✅ RESOLVED

### Issue: Transaction Type Confusion  
**Problem**: Wrong HR995 dataset for transaction type  
**Workaround**: Implement transaction-type-specific routing  
**Status**: ✅ RESOLVED

### Issue: Large File Loading
**Problem**: PDF conversion can be slow  
**Workaround**: Use pre-converted CSV files when available  
**Status**: ⚠️ ONGOING

### Issue: Memory Usage
**Problem**: Loading all data can consume significant memory  
**Workaround**: Selective loading based on analysis needs  
**Status**: ⚠️ ONGOING

---

## 📞 Emergency Contacts

### System Issues
- **Data Loading Failures**: Check file paths and permissions
- **Performance Problems**: Clear cache, restart application
- **Reference Matching**: Use enhanced matching function
- **Memory Issues**: Reduce dataset size or restart

### Business Logic Questions
- **Authorization Rules**: Refer to municipal finance procedures  
- **Audit Requirements**: Check compliance documentation
- **PPE/Electrical Monitoring**: Safety department guidelines
- **Supplier Validation**: Procurement team standards

---

## 🔄 Regular Maintenance Tasks

### Daily
- [ ] Monitor system performance
- [ ] Check anomaly detection results
- [ ] Verify data loading success

### Weekly  
- [ ] Review authorization coverage rates
- [ ] Analyze trend changes
- [ ] Update supplier master data

### Monthly
- [ ] Full data reconciliation
- [ ] Performance optimization review
- [ ] Documentation updates
- [ ] Backup verification

---

*Quick Reference Guide v1.0*  
*Last Updated: September 1, 2025*  
*For detailed information, see full documentation files*
