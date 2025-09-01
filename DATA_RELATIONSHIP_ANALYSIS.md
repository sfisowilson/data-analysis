# Data Relationship Analysis Document

## Overview
This document outlines the relationships between all data files in the system, their key columns, and potential linkage points for comprehensive analysis.

---

## Core Data Files Structure

### 1. **HR995GRN.xlsx** - Goods Received Notes (8,346 records)
**Purpose**: Records all incoming inventory receipts from suppliers

**Key Columns:**
- `Supplier No` - Links to Supplier files
- `Supplier Name` - Supplier identification
- `GRN No` - Unique receipt number (PRIMARY KEY)
- `GRN Date` - Receipt date
- `Item No` - Links to Stock Balance and HR390 (FOREIGN KEY)
- `GRN Qty` - Quantity received
- `Nett GRN Amt` - Value of goods received
- `Voucher` - Links to HR995VOUCH.Voucher No (FOREIGN KEY)
- `Store No` - Links to Stock Balance files
- `Order No` - Purchase order reference (Links to HR995VOUCH.Order No)
- `Inv No` - Invoice number (Links to HR185.reference)
- `Supp Own Ref` - Supplier's internal reference (Links to HR185.Supplier's Own Ref)

**Sample Data:**
```
Supplier No: 100060, GRN No: 27210, Item No: 210285, GRN Qty: 50.0, Nett GRN Amt: 140000.0, Voucher: INVI005662
```

---

### 2. **HR995ISSUE.xlsx** - Inventory Issues/Outbound (20,487 records)
**Purpose**: Records all inventory items issued/distributed from stores

**Key Columns:**
- `Requisition No` - Issue request number (PRIMARY KEY, Links to HR390.reference)
- `Issue Date` - Date of issue
- `Item No` - Links to Stock Balance and HR390 (FOREIGN KEY)
- `Issue Qty` - Quantity issued
- `Issue Cost` - Value of items issued
- `Store No` - Links to Stock Balance files
- `Vote No` - Budget/department code (Links to HR390.vote_no)
- `Fleet Unit No` - Vehicle/equipment reference
- `Activity` - Purpose/project code

**Sample Data:**
```
Requisition No: 49245, Item No: 108995, Issue Qty: 2.0, Issue Cost: 5499.0, Vote No: 60052304510PRMRCZZHO
```

---

### 3. **HR995VOUCH.xlsx** - Payment Vouchers (28,697 records)
**Purpose**: Records all payment transactions to suppliers

**Key Columns:**
- `Payee Ref` - Supplier/payee reference (Links to Supplier files)
- `Payee Name` - Name of recipient
- `Voucher No` - Unique voucher number (PRIMARY KEY, Links to HR995GRN.Voucher)
- `Cheq Amt` - Payment amount
- `Cheq Date` - Payment date
- `Order No` - Links to GRN orders (Links to HR995GRN.Order No)

**Sample Data:**
```
Payee Ref: .AJ VAN DEN HEEVER, Voucher No: SINA000194, Cheq Amt: 826.00
```

---

### 4. **HR995REDUND.xlsx** - Redundant/Slow-Moving Stock (3,322 records)
**Purpose**: Items with minimal movement or obsolete inventory

**Key Columns:**
- `Item No` - Links to all other item files (FOREIGN KEY)
- `Store No` - Storage location
- `Qty On Hand` - Current quantity
- `Value On Hand` - Current value
- `Last Move Date` - Last transaction date

---

### 5. **HR390 Movement Data** - Detailed Movement History (20,329 records)
**Purpose**: Comprehensive item movement tracking from PDF extraction

**Key Columns:**
- `item_no` - Links to all HR995 files (FOREIGN KEY)
- `tran_date` - Transaction date
- `type` - Transaction type (ISS, GRN, Carried Forward, etc.)
- `grn_qty`/`grn_value` - Receipt quantities/values
- `issue_qty`/`issue_value` - Issue quantities/values
- `reference` - Transaction reference number (Links to HR995ISSUE.Requisition No)
- `vote_no` - Budget code (Links to HR995ISSUE.Vote No)
- `store` - Store location
- `source_file` - Original PDF source

**Transaction Types:**
- ISS (71.7%) - Issues/Outbound
- Carried Forward (13.4%) - Period transitions
- Brought Forward (7.8%) - Opening balances
- GRN (4.8%) - Goods received
- WRO (1.3%) - Write-offs
- RND (0.8%) - Adjustments
- ADJ (0.2%) - Manual adjustments

**Sample Data:**
```
item_no: 200018, type: ISS, issue_qty: 200018.0, issue_value: 20230815.0, reference: 139843
```

---

### 6. **Stock Balance Files**

#### **Final stock list 2324.xlsx** (3,300 records)
**Purpose**: Current stock positions for 2023-2024

**Key Columns:**
- `Item No   ` - Links to all other files (FOREIGN KEY)
- `Store No  ` - Storage location
- `On Hand Qty      ` - Current quantity
- `Unit Price      ` - Current unit price
- `On Hand Value    ` - Total value
- `Item Cat      ` - Category code
- `Item Cat Desc` - Category description

#### **Final stock listing 2023.xlsx** (3,230 records)
**Purpose**: Historical stock positions for 2023

#### **Stock Adjustment item 2024.xlsx** (3,300 records)
**Purpose**: Stock adjustments and corrections

#### **Variance report.xlsx** (1,570 records)
**Purpose**: Stock count variances

**Key Columns:**
- `Item-No         ` - Links to all other files
- `On Hand Qty` - System quantity
- `Counted Undamaged` - Physical count
- `Sht Qty` - Shortage quantity
- `Surp Qty` - Surplus quantity

---

### 7. **Supplier Reference Files**

#### **2023 List of Suppliers.xlsx** (397 records)
#### **2024 List of Suppliers.xlsx** (79 records)
**Purpose**: Supplier master data

---

### 8. **Unprocessed PDF Files**

#### **HR185 Folder** - Transactions per Supplier (3 PDFs)
- Date ranges: 202207-202306, 202307-202406, 202407-202506
- **Purpose**: Supplier transaction summaries
- **Key Linkages**:
  - `reference` column ↔ HR995GRN.Inv No
  - `Supplier's Own Ref` ↔ HR995GRN.Supp Own Ref

#### **HR990 Folder** - Expenditure Statistics (3 PDFs)
- Date ranges: 202207-202306, 202307-202406, 202407-202506
- **Purpose**: Expenditure analysis and statistics

---

## Key Relationships & Linkages

### Primary Linkage: **Item No**
- **HR995GRN.Item No** ↔ **HR995ISSUE.Item No** ↔ **HR390.item_no** ↔ **Stock Balance.Item No**
- This creates a complete item movement trail from receipt → storage → issue

### Verified Business Linkages:

1. **Issue-to-Movement Chain:**
   ```
   HR995ISSUE.Requisition No ↔ HR390.reference
   HR995ISSUE.Vote No ↔ HR390.vote_no
   ```

2. **GRN-to-Supplier Transaction Chain:**
   ```
   HR995GRN.Inv No ↔ HR185.reference
   HR995GRN.Supp Own Ref ↔ HR185.Supplier's Own Ref
   ```

3. **Financial Payment Chain:**
   ```
   HR995GRN.Voucher ↔ HR995VOUCH.Voucher No
   HR995GRN.Order No ↔ HR995VOUCH.Order No
   ```

4. **Supplier Chain:**
   ```
   Supplier Files.Supplier No ↔ HR995GRN.Supplier No ↔ HR995VOUCH.Payee Ref
   ```

5. **Store/Location Chain:**
   ```
   HR995GRN.Store No ↔ HR995ISSUE.Store No ↔ Stock Balance.Store No ↔ HR390.store
   ```

---

## Questions for Verification - Updated with Complex Structure Findings

### **Multi-Row Transaction Questions:**

1. **HR995GRN Multiple Items**: When GRN 27210 has multiple line items (210285, 210293), should these be:
   - Treated as separate transactions?
   - Grouped as one supplier invoice with multiple lines?
   - How should total invoice value be calculated?

2. **Voucher-to-GRN Relationship**: One voucher (INVI005662) links to multiple GRN line items:
   - Is this one payment covering multiple deliveries?
   - Or one delivery with split payments?

### **Hierarchical Code Structure Questions:**

3. **Vote No Decoding**: Vote codes like "60052304510PRMRCZZHO":
   - What does each segment represent?
   - Is "6005" a department code?
   - What do the letter sequences mean?

4. **Store Code Duplication**: Why "MAIN STORE MAIN STORE" vs "MAIN STORE"?
   - Is this a data quality issue?
   - Or specific business logic (primary/secondary location)?

5. **Supplier Reference Patterns**:
   - "INV202211(01)" vs "2023/000001" vs "078" - different invoice numbering systems?
   - How to handle varying supplier reference formats?

### **Category Hierarchy Questions:**

6. **Item Category Logic**:
   - When `Item Cat` = "GEN" but `Item Cat Desc` = "GENERAL" - is this abbreviation expansion?
   - What's the business rule for 3-level category assignment?

7. **Bin Location Coding**:
   - "NONE" vs "00NONE" vs "SHF A5" - what's the warehouse layout logic?
   - Are shelf codes (SHF) hierarchical within stores?

### **Financial Reconciliation Questions:**

8. **Payment Method Codes**:
   - `Cheq/ACB/BDB/ELE No` - what determines payment method selection?
   - Are there approval workflows for different amounts/methods?

9. **Cash Indicator Values**: What are the 4 unique values in `Cash Ind`?
   - Cash vs Credit?
   - Different approval levels?

### **Supplier Data Questions:**

10. **Supplier Files as Pivot Tables**:
    - Do you have the underlying supplier master data (contact details, addresses)?
    - These appear to be transaction summaries rather than supplier profiles

11. **Supplier Count Variations**:
    - 2023: 397 suppliers, 2024: 79 suppliers
    - Is this a reduction in vendor base or different filtering criteria?

### **Stock Management Questions:**

12. **Variance Report Cycles**:
    - "NTGS23", "NTMS23" - what's the cycle count schedule?
    - How often are physical counts performed?

13. **Reserved Quantity**: All values are 0 in `Res Qty`:
    - Is this field unused?
    - Or just no reservations during count period?

### **Data Evolution Questions:**

14. **Column Changes Over Time**:
    - 2023 stock had separate `Item Sub Cat` column
    - 2324 merged into `Item Sub Cat Desc`
    - Is this a system upgrade impact?

15. **Unnamed Columns**: Stock Adjustment 2024 has `Unnamed: 12` and `Unnamed: 13`:
    - What were these intended for?
    - Are they adjustment amount fields?

### **HR390 Integration Questions:**

16. **Transaction Type Business Rules**:
    - When are "Carried Forward" vs "Brought Forward" generated?
    - Are these system-automated or manual entries?

17. **Value Interpretation**: HR390 shows very large values:
    - Are these cumulative values?
    - Different currency or unit scale?

### **Process Flow Questions:**

18. **End-to-End Process**: Complete workflow confirmation:
    - Purchase Order → GRN → Stock Receipt → Voucher Payment → Stock Issue
    - Are there any steps missing from the data chain?

19. **Approval Hierarchies**:
    - `Vouch Auth User/Name` - what's the approval workflow?
    - Different authority levels for different amounts?

---

## Complex Data Structures Discovered

### **HR995 Files - Advanced Patterns:**

#### **HR995GRN - Multi-line Supplier Transactions:**
- **Pattern**: Same GRN number spans multiple rows for different items
- **Example**: GRN 27210 has 2+ line items with different Item Nos (210285, 210293)
- **Complexity**: Supplier invoices can contain multiple products requiring aggregation
- **Linkage**: `Supp Own Ref` contains supplier's internal invoice numbers (e.g., "INV202211(01)", "2023/000001")

#### **HR995ISSUE - Department/Project Hierarchy:**
- **Vote No Structure**: Multi-level coding (e.g., "60052304510PRMRCZZHO")
  - Appears to be: Budget Year + Department + Sub-department + Project codes
- **Job No vs Activity**: Different levels of work classification
- **Fleet Integration**: `Fleet Unit No` links issues to specific vehicles/equipment
- **EI Code**: Only 2 unique values - likely Equipment Issue classification

#### **HR995VOUCH - Payment Method Complexity:**
- **Payee Ref vs Payee Name**: Many-to-one relationship (multiple refs per supplier)
- **Payment Types**: `Cheq/ACB/BDB/ELE No` suggests multiple payment methods
  - ACB = Automated Clearing Bureau
  - BDB = Bank Debit/Direct Debit  
  - ELE = Electronic transfers
- **Cash Indicator**: 4 unique values suggesting cash vs non-cash transactions

### **Stock Balance Files - Hierarchical Categories:**

#### **Category Structure (3-Level Hierarchy):**
```
Item Cat → Item Cat Desc → Item Sub Cat Desc
```

**Examples of Category Relationships:**
- **OIL** → **OIL** → **OIL** (Simple 1:1:1)
- **GENERAL** → **GENERAL** → **GENERAL** (Default/catch-all)
- **STATION** → **STATIONARY** → **STATIONARY** (Abbreviation expansion)
- **GEN** → **GENERAL** → **GENERAL** (Short code expansion)

#### **Store/Bin Location Hierarchy:**
```
Store No → Bin No → Item No
```
- **Store Types**: GARAGE STO, MAIN STORE, STAT.STORE, PARKS DIES, PARKS FUEL
- **Bin Variations**: NONE, 00NONE, SHF A5, SHF A7, SHF A8 (shelf locations)

#### **Evolution Across Years:**
- **2023**: Had separate `Item Sub Cat` column (12 columns total)
- **2324**: Merged into `Item Sub Cat Desc` (11 columns)
- **Adjustment 2024**: Added 2 unnamed columns (14 total) - possibly for adjustments

### **Variance Report - Stock Count Structure:**
- **Stock-Cnt-Ref-2**: Cycle count references (NTGS23, NTMS23) = Store abbreviation + year
- **Damage Tracking**: Separate columns for undamaged vs damaged quantities
- **Shortage/Surplus**: Dedicated variance tracking with values
- **Reserved Qty**: All values are 0 - possibly unused field

### **Supplier Files - Pivot Table Structure:**
Both supplier files are **pivot table exports** rather than master data:

#### **2023 Suppliers (397 records):**
- **Structure**: Count ranking of suppliers by transaction volume
- **Header Row**: "List of Supplier who provided Electrical and PPE materials..."
- **Data**: Rank, Supplier Name, Transaction Count
- **Top Supplier**: FRIEDENTHAL EN SEUNS (253 transactions)

#### **2024 Suppliers (79 records):**
- **Same Structure**: But focused on "Electrical and PPE materials related services"
- **Reduced Count**: Only 79 vs 397 (more targeted supplier list)
- **Top Supplier**: Same FRIEDENTHAL EN SEUNS but only 32 transactions

### **HR390 Movement Data - Transaction Complexity:**
Based on earlier analysis, this contains **nested business logic**:
- **Carried Forward/Brought Forward**: Period transitions creating opening/closing balances
- **Multiple Transaction Types**: Each with different value interpretations
- **Store Duplication**: "MAIN STORE MAIN STORE" suggests concatenated location codes

## Data Quality Observations

### **Complex Issues Identified:**
1. **Multi-row Transactions**: GRN/Voucher numbers span multiple rows requiring grouping
2. **Hierarchical Categories**: 3-level category structure with inconsistent coding
3. **Date Formats**: All dates stored as integers (YYYYMMDD format confirmed)
4. **Supplier Data**: Pivot tables instead of master data - missing contact details
5. **Column Evolution**: Structure changes across years affecting historical analysis
6. **Code Concatenation**: Vote numbers and store names contain embedded hierarchies
7. **Unnamed Columns**: Extra columns in some files with unclear purposes

### **Advanced Strengths:**
1. **Transaction Granularity**: Individual line items maintained across all systems
2. **Audit Trail**: Complete voucher → GRN → stock → issue chain
3. **Variance Management**: Detailed stock count and adjustment tracking
4. **Multi-store Operations**: Complete store and bin location tracking
5. **Project Accounting**: Vote numbers enable project-level cost tracking
6. **Supplier Performance**: Transaction frequency data available through pivot exports

---

## Recommended Analysis Workflows

### 1. **Complete Item Lifecycle Tracking**
```
GRN Receipt → Stock Balance → Issue/Movement → Variance Analysis
```

### 2. **Supplier Performance Analysis**
```
Supplier Master → GRN Analysis → Payment Analysis → Transaction Frequency
```

### 3. **Financial Reconciliation**
```
GRN Values → Voucher Payments → Stock Valuations → Variance Impact
```

### 4. **Inventory Management**
```
Stock Balances → Movement History → Redundant Analysis → Optimization
```

---

*Document Created: Based on analysis of all data files in workspace*
*Status: Pending verification of unclear column definitions*
