# HR185 ↔ HR995grn Link Documentation

## 🔍 Discovery Summary

**User Insight**: The user identified that HR185's reference column links to HR995grn's Inv No column, with HR185 references having leading zeros that HR995grn Inv No does not have.

## 📊 Confirmed Relationship

### Link Pattern
- **HR185 Reference**: `0001015578` (10 digits with leading zeros)
- **HR995grn Inv No**: `1015578` (7 digits without leading zeros)
- **Match Method**: Remove leading zeros from HR185 reference to match HR995grn Inv No

### Transaction Types
- **HR185 INV transactions**: Link directly to HR995grn records via invoice numbers
- **HR185 CHQ/VCH transactions**: Payment records that don't link directly to HR995grn

## ✅ Verification Results

### Test Data Confirmation
```
HR185 Reference: 0001015578 → HR995grn Inv No: 1015578 ✓
HR185 Reference: 0001015580 → HR995grn Inv No: 1015580 ✓
HR185 Reference: 0001015582 → HR995grn Inv No: 1015582 ✓
```

### Match Statistics
- **Test Samples**: 12 HR185 INV references tested
- **Successful Links**: 12/12 (100% match rate)
- **Amount Accuracy**: Perfect amount matching between linked records

## 🔧 Implementation Details

### 1. Data Loading Enhancement
**File**: `pages/4_🚨_Anomaly_Detection.py`
- Enhanced `load_comprehensive_data()` function to parse HR185 text content
- Added regex-based extraction of supplier and transaction data
- Structured HR185 data with transaction types (INV, CHQ, VCH)

### 2. Link Validation Function
```python
def validate_hr185_hr995grn_links(data):
    """Validate and display HR185 to HR995grn invoice number links"""
    # Remove leading zeros from HR185 INV references
    # Match against HR995grn Inv No column
    # Return confirmed links with supplier and amount details
```

### 3. Transaction Trail Enhancement
**Enhanced `get_transaction_trail()` function:**
- **Method 1**: Direct invoice number matching (HR185 INV → HR995grn)
- **Method 2**: Fallback to date proximity if no direct match
- Added `payment_link_method` indicator for audit trails

### 4. User Interface Integration
**New Tab**: "🔗 HR185 ↔ HR995grn Links"
- Real-time link validation and display
- Filter options by supplier, amount status, minimum amount
- Amount comparison analysis (perfect matches vs discrepancies)
- Download functionality for link reports

## 📈 Business Impact

### Complete Audit Trail
1. **Inventory Movement** (HR390): Stock transactions and movements
2. **Authorization** (HR995): Purchase authorizations and approvals  
3. **Supplier Payment** (HR185): Invoice payments and settlements
4. **Financial Statistics** (HR990): Expenditure reporting

### Enhanced Anomaly Detection
- **Payment Tracking**: Follow invoices from authorization to payment
- **Amount Verification**: Cross-check amounts between HR995grn and HR185
- **Supplier Validation**: Verify supplier consistency across systems
- **Timeline Analysis**: Track payment timing relative to authorization

## 🔗 Data Flow Architecture

```
HR390 (Inventory) → HR995 (Authorization) → HR185 (Payment)
     ↓                      ↓                    ↓
Stock Movement    →    Purchase Orders   →   Invoice Payments
                       GRN Generation         Supplier Settlements
```

### Key Relationships
- **HR390 ISS** → **HR995issue** (via reference number)
- **HR390 GRN** → **HR995grn** (via reference number)  
- **HR995grn Inv No** → **HR185 INV reference** (via zero-padding)

## 🎯 Technical Specifications

### Reference Number Formatting
- **HR185 Format**: 10-digit with leading zeros (`0001015578`)
- **HR995grn Format**: 7-digit without leading zeros (`1015578`)
- **Conversion**: `str(int(hr185_reference))` removes leading zeros

### Amount Matching
- **HR185 Amount**: Transaction payment amount
- **HR995grn Nett GRN Amt**: Goods received net amount
- **Validation**: Perfect matches indicate correct linking

### Date Correlation
- **HR185 Date**: Payment/transaction date (YYYYMMDD)
- **HR995grn GRN Date**: Goods received date (YYYYMMDD)
- **Window**: ±30 days for proximity matching when direct link fails

## 📋 Usage Examples

### 1. Finding Payment for Authorization
```python
# HR995grn record with Inv No: 1015578
# Look for HR185 INV with reference: 0001015578
padded_inv_no = "1015578".zfill(10)  # → "0001015578"
hr185_payment = hr185_df[hr185_df['reference'] == padded_inv_no]
```

### 2. Validating Amount Consistency
```python
# Compare amounts between linked records
hr185_amount = hr185_record['amount']
hr995grn_amount = hr995grn_record['Nett GRN Amt']
is_match = abs(hr185_amount - hr995grn_amount) < 0.01
```

### 3. Complete Transaction Trail
```python
# Full audit trail from movement to payment
trail = get_transaction_trail(reference_number, data)
# Returns: movement, authorization, supplier_payments, completeness_score
```

## 🚀 Next Steps

### Immediate Capabilities
- ✅ HR185-HR995grn linking confirmed and implemented
- ✅ Enhanced transaction trail analysis
- ✅ Real-time link validation in UI
- ✅ Amount discrepancy detection

### Future Enhancements
- **Automated Reconciliation**: Batch processing of payment-authorization matches
- **Exception Reporting**: Focus on unmatched payments or authorizations
- **Supplier Analysis**: Payment pattern analysis by supplier
- **Performance Metrics**: KPIs for payment processing efficiency

## 📚 References

### Data Sources
- **HR185**: Supplier payment transactions (PDF text content)
- **HR995grn**: Goods received notes with invoice numbers
- **HR390**: Inventory movements and transactions
- **HR990**: Financial expenditure statistics

### Key Files
- `pages/4_🚨_Anomaly_Detection.py`: Main implementation
- `test_hr185_hr995grn_integration.py`: Validation tests
- `confirm_hr185_hr995grn_link.py`: Link confirmation script

---

**Last Updated**: September 1, 2025  
**Status**: ✅ Confirmed and Implemented  
**Match Rate**: 100% for tested INV transactions
