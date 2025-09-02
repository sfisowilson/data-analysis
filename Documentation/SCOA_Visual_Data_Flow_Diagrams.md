# SCOA System - Visual Data Flow Diagrams

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCOA Municipal Inventory System                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  USER REQUEST → AUTHORIZATION → TRANSACTION → PAYMENT → FINANCIAL REPORTING │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Data Relationships (Four-Layer Architecture)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   HR390      │    │   HR995      │    │   HR185      │    │   HR990      │
│  Movement    │◄──►│Authorization │◄──►│  Supplier    │◄──►│ Expenditure  │
│   Records    │    │   Records    │    │  Payments    │    │ Statistics   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                     │                     │                     │
       │                     │                     │                     │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   SUPPLIERS  │    │ Stock        │    │ Invoice      │    │ Anomaly      │
│   Master     │    │ Balances     │    │ Tracking     │    │ Detection    │
│    Data      │    │ & Variance   │    │ & Payments   │    │ Dashboard    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

## Complete Transaction Lifecycle with HR185

```
STEP 1: INVENTORY MOVEMENT (HR390)
┌─────────────────────┐
│   Stock Issue       │
│   Reference: 089322 │ ──┐
│   Type: ISS         │   │
└─────────────────────┘   │
                          ▼
STEP 2: AUTHORIZATION (HR995issue)
┌─────────────────────┐   │
│   Purchase Order    │   │ Direct Reference
│   Requisition: 89322│◄──┘ Matching
│   Approved Amount   │
└─────────────────────┘
          │
          ▼
STEP 3: GOODS RECEIPT (HR995grn)
┌─────────────────────┐
│   GRN Record        │
│   GRN No: 27210     │
│   Inv No: 1015578   │ ──┐
│   Supplier Details  │   │
└─────────────────────┘   │
                          ▼
STEP 4: SUPPLIER PAYMENT (HR185)
┌─────────────────────┐   │
│   Invoice Payment   │   │ Zero-Padded
│   Reference:        │   │ Linking
│   0001015578        │◄──┘ (1015578 → 0001015578)
│   Type: INV         │
│   Payment Amount    │
└─────────────────────┘
```

## Transaction-Specific Linking Logic (Updated with HR185)

```
HR390 Transaction Type          HR995 Authorization          HR185 Payment Link
┌─────────────────────┐        ┌─────────────────────┐       ┌─────────────────────┐
│   ISS (Issue)       │◄──────►│   HR995issue.csv    │       │   No direct link    │
│   Reference: 089322 │        │   Requisition: 89322│       │   (different system)│
└─────────────────────┘        └─────────────────────┘       └─────────────────────┘

┌─────────────────────┐        ┌─────────────────────┐       ┌─────────────────────┐
│   GRN (Received)    │◄──────►│   HR995grn.csv      │◄─────►│   HR185 INV        │
│   Reference: 012345 │        │   Inv No: 1015578   │       │   Ref: 0001015578   │
└─────────────────────┘        └─────────────────────┘       └─────────────────────┘
                                         │                             │
                                         └─────────────────────────────┘
                                           Zero-padding link:
                                           1015578 ↔ 0001015578

┌─────────────────────┐        ┌─────────────────────┐       ┌─────────────────────┐
│   VOUCH (Voucher)   │◄──────►│   HR995vouch.csv    │◄─────►│   HR185 VCH/CHQ    │
│   Reference: 067890 │        │   Voucher No: 67890 │       │   Ref: 067890       │
└─────────────────────┘        └─────────────────────┘       └─────────────────────┘
                                         │                             │
                                         └─────────────────────────────┘
                                           VCH → Voucher No link
                                           CHQ → Cheq/ACB/BDB/ELE No link

ADDITIONAL HR185 TRANSACTION TYPES:
┌─────────────────────┐
│   HR185 CHQ         │ ──► Links to HR995vouch via Cheque/ACB/BDB/ELE No
│   Ref: 27949        │     (cheque payment processing)
└─────────────────────┘
```

## Enhanced Reference Matching Strategies

```
HR390 Reference: '089322' (with leading zeros)
                    │
                    ▼
         ┌─────────────────────────┐
         │   4-Strategy Matching   │
         └─────────────────────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    Strategy 1  Strategy 2  Strategy 3  Strategy 4
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Direct  │ │ Remove  │ │ Zero    │ │Integer  │
    │ String  │ │ Leading │ │ Pad     │ │Compare  │
    │ Match   │ │ Zeros   │ │ HR995   │ │         │
    └─────────┘ └─────────┘ └─────────┘ └─────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
      ❌ FAIL    ✅ MATCH   ✅ MATCH   ✅ MATCH
    '089322'      '89322'    '089322'    89322
       ≠            =          =          =
    '89322'       '89322'    '089322'    89322

Result: 3/4 strategies successful → Authorization FOUND
```

## Complete Issue Transaction Flow

```
Step 1: User Request
┌─────────────────┐
│ User needs item │
│ (e.g., PPE)     │
└─────────────────┘
         │
         ▼
Step 2: Authorization
┌─────────────────┐
│ Create record   │
│ in HR995issue   │
│ Req No: 89322   │
└─────────────────┘
         │
         ▼
Step 3: Issue Transaction
┌─────────────────┐
│ Record in HR390 │
│ Type: ISS       │
│ Ref: '089322'   │
└─────────────────┘
         │
         ▼
Step 4: Inventory Update
┌─────────────────┐
│ Update stock    │
│ balances and    │
│ variance data   │
└─────────────────┘
         │
         ▼
Step 5: Financial Impact
┌─────────────────┐
│ Record in HR990 │
│ expenditure     │
│ statistics      │
└─────────────────┘
         │
         ▼
Step 6: Audit Trail
┌─────────────────┐
│ Complete trail  │
│ available for   │
│ verification    │
└─────────────────┘
```

## Anomaly Detection Flow

```
Data Loading
┌─────────────────┐
│ Load all data   │
│ sources         │
│ (HR390,995,990) │
└─────────────────┘
         │
         ▼
Enhanced Matching
┌─────────────────┐
│ Apply 4-strategy│
│ reference       │
│ matching        │
└─────────────────┘
         │
         ▼
Anomaly Categories
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Authorization   │ Balance         │ Statistical     │ PPE/Electrical  │
│ Mismatches      │ Discrepancies   │ Outliers        │ Issues          │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
    │ ISS w/o │       │ System  │       │ Qty >   │       │ Safety  │
    │ HR995   │       │ vs      │       │ 1.5*IQR │       │ Critical│
    │ match   │       │ Physical│       │         │       │ Items   │
    └─────────┘       └─────────┘       └─────────┘       └─────────┘
```

## Data File Processing Pipeline

```
Source Files (PDF/Excel)
┌─────────────────────────┐
│ HR390 - Movement.pdf    │
│ HR995issue.xlsx         │
│ HR990 - Expenditure.pdf │
│ Suppliers.xlsx          │
└─────────────────────────┘
            │
            ▼
Text Extraction & Conversion
┌─────────────────────────┐
│ PDF → Text → CSV        │
│ Excel → CSV             │
│ Column standardization  │
└─────────────────────────┘
            │
            ▼
Data Validation & Cleaning
┌─────────────────────────┐
│ Type conversion         │
│ Missing value handling  │
│ Format standardization  │
└─────────────────────────┘
            │
            ▼
Structured Data Storage
┌─────────────────────────┐
│ /hr390_structured/      │
│ /converted_csv/         │
│ Ready for analysis      │
└─────────────────────────┘
```

## User Interface Flow

```
Streamlit Application
┌─────────────────────────────────────────────────────────────────┐
│                     Main Navigation                             │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ 📊 Dashboard    │ 📈 Analysis     │ 📄 Reports      │🚨 Anomaly │
│                 │                 │                 │ Detection │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│• Stock Movement ││• Trend Analysis ││• Cross-Ref      ││• Authorization  │
│• Transaction    ││• Performance    │  Summary        │  Mismatches     │
│  Trail Analysis │  Metrics        │• Data           │• Balance        │
│• Enhanced       │• Category       │  Verification   │  Discrepancies  │
│  Matching       │  Breakdown      │• Inventory      │• Real-time      │
│                 │                 │  Data Flow      │  Matching Test  │
└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘
```

## PPE & Electrical Materials Workflow

```
Item Classification
┌─────────────────┐
│ Scan item       │
│ descriptions    │
│ for keywords    │
└─────────────────┘
         │
         ▼
Keyword Matching
┌─────────────────┬─────────────────┐
│ PPE Keywords    │ Electrical      │
│ • safety        │ Keywords        │
│ • protective    │ • electrical    │
│ • helmet        │ • cable         │
│ • glove         │ • switch        │
│ • vest          │ • meter         │
│ • boot          │ • transformer   │
└─────────────────┴─────────────────┘
         │                 │
         ▼                 ▼
Enhanced Monitoring
┌─────────────────────────┐
│ • Higher scrutiny       │
│ • Mandatory auth check  │
│ • Special reporting     │
│ • Cost threshold alert  │
└─────────────────────────┘
```

## Audit Trail Verification

```
Transaction Reference: 089322
┌─────────────────────────────────────────────────────────────────┐
│                     Audit Trail Components                     │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ 1. Transaction  │ 2. Authorization│ 3. Supplier     │4. Financial│
│    (HR390)      │    (HR995)      │    (Master)     │  (HR990)   │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│ Item: 201643    ││ Req No: 89322   ││ Supplier info   ││ Cost impact     │
│ Date: 20230602  ││ Cost: 104186.25 ││ for item        ││ tracking        │
│ Type: ISS       ││ Qty: 1          ││ 3310PRMRCZZHO   ││                 │
│ Ref: '089322'   ││ Vote: 88200.00  ││                 ││                 │
└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘
         │                 │                 │                 │
         └─────────────────┼─────────────────┼─────────────────┘
                           ▼
              ┌─────────────────────────┐
              │ Complete Audit Trail    │
              │ ✅ Transaction Found    │
              │ ✅ Authorization Found  │
              │ ✅ Supplier Verified    │
              │ ✅ Financial Recorded   │
              └─────────────────────────┘
```

## Error Handling & Recovery

```
Data Loading Issues
┌─────────────────┐
│ File not found  │
│ Conversion error│
│ Format mismatch │
└─────────────────┘
         │
         ▼
Graceful Degradation
┌─────────────────┐
│ Partial loading │
│ Error logging   │
│ User notification│
└─────────────────┘
         │
         ▼
Recovery Options
┌─────────────────┐
│ Retry loading   │
│ Alternative path│
│ Manual override │
└─────────────────┘
```

---

*Visual diagrams created using ASCII art for universal compatibility*  
*Can be converted to formal flowcharts using tools like Mermaid, Visio, or Draw.io*
