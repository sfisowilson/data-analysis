# 🌐 IIS Deployment Guide for Static HTML Dashboard

## ✅ **Solution: Static HTML Dashboard for IIS**

Your Python dashboard has been successfully converted to **static HTML files** that can be hosted directly on your Windows IIS server **without Python installation**.

## 📁 **Generated Files**

The following files are ready for IIS deployment:

```
html_reports/
├── index.html                    # Main dashboard homepage
├── financial_analytics.html     # Financial analysis charts
├── supplier_analytics.html      # Supplier performance analysis  
├── objective_reports.html       # Business objectives summary
├── data_tables.html             # Data overview tables
├── inventory_analytics.html     # Inventory analysis (placeholder)
└── operational_analytics.html   # Operations analysis (placeholder)
```

## 🚀 **IIS Deployment Steps**

### Step 1: Copy Files to IIS Server
```powershell
# Copy the html_reports folder to your IIS server
# Example locations:
C:\inetpub\wwwroot\dashboard\
# OR
C:\inetpub\wwwroot\stock-analytics\
```

### Step 2: Configure IIS Site
1. **Open IIS Manager**
2. **Right-click** on "Default Web Site" (or create new site)
3. **Add Application** or **Add Virtual Directory**:
   - **Alias**: `dashboard` (or your preferred name)
   - **Physical Path**: Point to your `html_reports` folder

### Step 3: Set Permissions
```powershell
# Ensure IIS has read access to the files
# Right-click folder → Properties → Security
# Add "IIS_IUSRS" with Read permissions
```

### Step 4: Test Access
```
http://your-server/dashboard/
# OR
http://your-server/dashboard/index.html
```

## 🎯 **What's Included**

### ✅ **Working Features:**
- 📊 **Interactive Charts**: Plotly-based visualizations
- 🏪 **Supplier Analytics**: Top suppliers, frequency analysis
- 💰 **Financial Trends**: GRN values, spending patterns
- 🎯 **Objective Reports**: All 5 business objectives summary
- 📋 **Data Overview**: File statistics and record counts
- 📱 **Responsive Design**: Works on desktop, tablet, mobile
- 🎨 **Professional Styling**: Clean, modern interface

### ⚠️ **Limitations (Static Version):**
- ❌ **No Real-time Filtering**: Data is pre-generated
- ❌ **No Live Updates**: Requires manual regeneration
- ❌ **Limited Interactivity**: Charts are view-only
- ❌ **No Data Export**: No download functionality

## 🔄 **Updating the Dashboard**

### Option 1: Manual Updates
```powershell
# On your development machine:
cd "d:\Data Hand-Over"
.venv\Scripts\python export_static_dashboard.py

# Copy updated html_reports folder to IIS server
```

### Option 2: Automated Updates (Advanced)
```powershell
# Create batch file for scheduled updates
@echo off
cd "d:\Data Hand-Over"
.venv\Scripts\python stock_data_processor.py
.venv\Scripts\python export_static_dashboard.py
xcopy html_reports\*.* "\\iis-server\share\dashboard\" /Y /S
```

## 📊 **Dashboard Features**

### 🏠 **Homepage (index.html)**
- Dashboard overview with key statistics
- Navigation to all sections
- Last update timestamp
- Responsive card-based layout

### 💰 **Financial Analytics**
- Top 15 suppliers by value (horizontal bar chart)
- Monthly GRN trends (line chart)
- Transaction volume analysis
- Spending pattern visualization

### 🏪 **Supplier Analytics**
- Most frequently requested items (bar chart)
- Request distribution by supplier (pie chart)
- Supplier performance metrics
- Item-supplier frequency analysis

### 🎯 **Objective Reports**
- All 5 business objectives status
- Record counts by objective
- Completion status visualization
- Summary statistics

### 📋 **Data Tables**
- File statistics overview
- Record counts and file sizes
- Available datasets listing
- Data quality metrics

## 🔧 **IIS Configuration Tips**

### MIME Types (if needed)
```xml
<!-- In web.config -->
<system.webServer>
  <staticContent>
    <mimeMap fileExtension=".json" mimeType="application/json" />
  </staticContent>
</system.webServer>
```

### Error Pages
```xml
<system.webServer>
  <httpErrors>
    <remove statusCode="404" subStatusCode="-1" />
    <error statusCode="404" prefixLanguageFilePath="" path="/dashboard/index.html" responseMode="Redirect" />
  </httpErrors>
</system.webServer>
```

### Security Headers
```xml
<system.webServer>
  <httpProtocol>
    <customHeaders>
      <add name="X-Content-Type-Options" value="nosniff" />
      <add name="X-Frame-Options" value="SAMEORIGIN" />
    </customHeaders>
  </httpProtocol>
</system.webServer>
```

## 💡 **Future Enhancement Options**

### Option A: Hybrid Solution
- Keep static HTML for main dashboard
- Add lightweight data update service
- Scheduled regeneration of reports

### Option B: Add Python to IIS
- Install Python on IIS server
- Configure FastCGI for Python
- Deploy full interactive dashboard

### Option C: External Hosting + Proxy
- Host Python app externally (cloud)
- Configure IIS reverse proxy
- Maintain IIS as front-end

## 📞 **Support & Troubleshooting**

### Common Issues:
1. **Charts not loading**: Check Plotly CDN access
2. **403 Forbidden**: Verify IIS permissions
3. **404 Not Found**: Check virtual directory path
4. **Styling issues**: Ensure CSS files accessible

### Testing Checklist:
- ✅ Can access index.html
- ✅ Navigation links work
- ✅ Charts display properly
- ✅ Mobile responsive design
- ✅ All sections accessible

## ✅ **Ready for Production**

Your static HTML dashboard is now ready for production deployment on IIS. Simply copy the `html_reports` folder to your IIS server and configure as described above.

**Benefits:**
- 🚀 Fast loading (static files)
- 🔒 Secure (read-only)
- 💰 Cost-effective (no Python required)
- 📈 Professional presentation
- 🌐 Standard web hosting

The dashboard provides a comprehensive view of your stock analytics with professional charts and reporting, perfect for stakeholder presentations and business decision-making.
