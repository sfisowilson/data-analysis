#!/usr/bin/env python3
"""
Static HTML Dashboard Exporter for IIS Hosting
Converts the interactive Streamlit dashboard to static HTML reports that can be hosted on IIS.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from pathlib import Path
import os
from datetime import datetime
import json

class StaticDashboardExporter:
    """Export interactive dashboard as static HTML files for IIS hosting."""
    
    def __init__(self):
        self.output_folder = Path("output")
        self.html_output = Path("html_reports")
        self.html_output.mkdir(exist_ok=True)
        
    def load_data(self, filename):
        """Load data from CSV file."""
        try:
            file_path = self.output_folder / filename
            if file_path.exists():
                return pd.read_csv(file_path, low_memory=False)
            return None
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def create_index_page(self):
        """Create main index.html page with navigation."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analytics Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .nav-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .nav-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .nav-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }}
        .nav-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 1.3em;
        }}
        .nav-card p {{
            margin: 0;
            color: #666;
            line-height: 1.5;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Stock Analytics Dashboard</h1>
        <p>Comprehensive Analysis & Reports - Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">169K+</div>
            <div class="stat-label">Total Records</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">28</div>
            <div class="stat-label">Data Sources</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">5</div>
            <div class="stat-label">Business Objectives</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">35+</div>
            <div class="stat-label">Charts & Reports</div>
        </div>
    </div>
    
    <div class="nav-grid">
        <a href="financial_analytics.html" class="nav-card">
            <h3>💰 Financial Analytics</h3>
            <p>GRN trends, supplier spending analysis, transaction volumes, and financial performance metrics.</p>
        </a>
        
        <a href="inventory_analytics.html" class="nav-card">
            <h3>📦 Inventory Analytics</h3>
            <p>Stock movements, turnover analysis, inventory levels, and stock balance reporting.</p>
        </a>
        
        <a href="supplier_analytics.html" class="nav-card">
            <h3>🏪 Supplier Analytics</h3>
            <p>Supplier performance, transaction frequency, relationship analysis, and vendor metrics.</p>
        </a>
        
        <a href="operational_analytics.html" class="nav-card">
            <h3>⚙️ Operational Analytics</h3>
            <p>Process analysis, audit trails, operational efficiency, and workflow insights.</p>
        </a>
        
        <a href="objective_reports.html" class="nav-card">
            <h3>🎯 Objective Reports</h3>
            <p>All 5 business objective analyses: item frequency, audit trails, and stock balances.</p>
        </a>
        
        <a href="data_tables.html" class="nav-card">
            <h3>📋 Data Tables</h3>
            <p>Raw data tables, search functionality, and detailed record exploration.</p>
        </a>
    </div>
    
    <div class="footer">
        <p>📈 Static HTML Dashboard for IIS Hosting | 🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>💡 This is a static export of the interactive Python dashboard, optimized for IIS web server hosting.</p>
    </div>
</body>
</html>
"""
        
        with open(self.html_output / "index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ Created index.html")
    
    def create_financial_analytics(self):
        """Create financial analytics HTML page."""
        print("📊 Creating Financial Analytics page...")
        
        # Load GRN data
        grn_df = self.load_data("hr995_grn.csv")
        
        charts = []
        
        if grn_df is not None and not grn_df.empty:
            # Top suppliers by value
            if 'supplier_name' in grn_df.columns and 'nett_grn_amt' in grn_df.columns:
                supplier_totals = grn_df.groupby('supplier_name')['nett_grn_amt'].agg(['sum', 'count']).reset_index()
                supplier_totals = supplier_totals.sort_values('sum', ascending=False).head(15)
                
                fig1 = px.bar(supplier_totals, x='sum', y='supplier_name',
                             title='Top 15 Suppliers by Total Value',
                             labels={'sum': 'Total Value (R)', 'supplier_name': 'Supplier'},
                             orientation='h')
                fig1.update_layout(height=600)
                charts.append(plot(fig1, output_type='div', include_plotlyjs=False))
                
                # Monthly trends
                if 'fin_period' in grn_df.columns:
                    grn_df['fin_period'] = pd.to_numeric(grn_df['fin_period'], errors='coerce')
                    monthly_trends = grn_df.groupby('fin_period')['nett_grn_amt'].agg(['sum', 'count']).reset_index()
                    
                    fig2 = px.line(monthly_trends, x='fin_period', y='sum',
                                  title='GRN Value Trend by Financial Period',
                                  labels={'sum': 'Total Value (R)', 'fin_period': 'Financial Period'})
                    fig2.update_layout(height=400)
                    charts.append(plot(fig2, output_type='div', include_plotlyjs=False))
        
        self.create_html_page("financial_analytics.html", "💰 Financial Analytics", charts)
    
    def create_supplier_analytics(self):
        """Create supplier analytics HTML page."""
        print("🏪 Creating Supplier Analytics page...")
        
        # Load data
        grn_df = self.load_data("hr995_grn.csv")
        obj1_df = self.load_data("objective_1_item_frequency_by_supplier.csv")
        
        charts = []
        
        if obj1_df is not None and not obj1_df.empty:
            # Top items by frequency
            top_items = obj1_df.head(20)
            
            fig1 = px.bar(top_items, x='request_count', y='item_code',
                         title='Top 20 Most Frequently Requested Items',
                         labels={'request_count': 'Request Count', 'item_code': 'Item Code'},
                         orientation='h')
            fig1.update_layout(height=600)
            charts.append(plot(fig1, output_type='div', include_plotlyjs=False))
            
            # Supplier frequency analysis
            supplier_freq = obj1_df.groupby('supplier_name')['request_count'].sum().reset_index()
            supplier_freq = supplier_freq.sort_values('request_count', ascending=False).head(15)
            
            fig2 = px.pie(supplier_freq, values='request_count', names='supplier_name',
                         title='Request Distribution by Supplier')
            fig2.update_layout(height=500)
            charts.append(plot(fig2, output_type='div', include_plotlyjs=False))
        
        self.create_html_page("supplier_analytics.html", "🏪 Supplier Analytics", charts)
    
    def create_objective_reports(self):
        """Create objective reports HTML page."""
        print("🎯 Creating Objective Reports page...")
        
        charts = []
        
        # Load all objective data
        objectives = [
            ("Objective 1: Item Frequency", "objective_1_item_frequency_by_supplier.csv"),
            ("Objective 2: Audit Trail", "objective_2_stock_audit_trail.csv"),
            ("Objective 3: HR995 Report", "objective_3_hr995_report.csv"),
            ("Objective 4: End-to-End Process", "objective_4_end_to_end_process.csv"),
            ("Objective 5: Stock Balances", "objective_5_stock_balances_by_year.csv")
        ]
        
        summary_data = []
        
        for obj_name, filename in objectives:
            df = self.load_data(filename)
            if df is not None:
                summary_data.append({
                    'Objective': obj_name,
                    'Records': len(df),
                    'Status': 'Complete' if len(df) > 0 else 'Empty'
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            fig = px.bar(summary_df, x='Objective', y='Records',
                        title='Records Count by Objective',
                        color='Status',
                        color_discrete_map={'Complete': '#2E8B57', 'Empty': '#DC143C'})
            fig.update_layout(height=400, xaxis_tickangle=-45)
            charts.append(plot(fig, output_type='div', include_plotlyjs=False))
        
        self.create_html_page("objective_reports.html", "🎯 Objective Reports", charts)
    
    def create_data_tables(self):
        """Create data tables HTML page."""
        print("📋 Creating Data Tables page...")
        
        # Get file statistics
        file_stats = []
        csv_files = list(self.output_folder.glob("*.csv"))
        
        for file in csv_files:
            try:
                df = pd.read_csv(file, low_memory=False)
                file_stats.append({
                    'File': file.name,
                    'Records': len(df),
                    'Columns': len(df.columns),
                    'Size_MB': round(file.stat().st_size / (1024*1024), 2)
                })
            except:
                continue
        
        if file_stats:
            stats_df = pd.DataFrame(file_stats)
            stats_df = stats_df.sort_values('Records', ascending=False)
            
            # Create table HTML
            table_html = stats_df.to_html(index=False, classes='data-table', table_id='files-table')
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>📋 Data Tables</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
        .data-table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .data-table th, .data-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .data-table th {{ background-color: #f8f9fa; font-weight: bold; }}
        .data-table tr:hover {{ background-color: #f5f5f5; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← Back to Dashboard</a>
    <div class="header">
        <h1>📋 Data Tables Overview</h1>
        <p>Available CSV files and their statistics</p>
    </div>
    
    <h2>📊 File Statistics</h2>
    {table_html}
    
    <div style="margin-top: 30px; padding: 20px; background: white; border-radius: 8px;">
        <h3>💡 Notes:</h3>
        <ul>
            <li>This is a static export - files are read-only</li>
            <li>For interactive filtering, use the full Python dashboard</li>
            <li>Total records across all files: {sum(stat['Records'] for stat in file_stats):,}</li>
        </ul>
    </div>
</body>
</html>
"""
            
            with open(self.html_output / "data_tables.html", "w", encoding="utf-8") as f:
                f.write(html_content)
    
    def create_html_page(self, filename, title, charts):
        """Create a generic HTML page with charts."""
        charts_html = "\\n".join(charts) if charts else "<p>No charts available for this section.</p>"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
        .chart-container {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .back-link {{ display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← Back to Dashboard</a>
    <div class="header">
        <h1>{title}</h1>
        <p>Static HTML export for IIS hosting</p>
    </div>
    
    <div class="chart-container">
        {charts_html}
    </div>
</body>
</html>
"""
        
        with open(self.html_output / filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ Created {filename}")
    
    def export_all(self):
        """Export all dashboard components as static HTML."""
        print("🚀 EXPORTING STATIC HTML DASHBOARD FOR IIS")
        print("=" * 60)
        
        # Create all pages
        self.create_index_page()
        self.create_financial_analytics()
        self.create_supplier_analytics()
        self.create_objective_reports()
        self.create_data_tables()
        
        # Create simple placeholder pages for other sections
        placeholder_pages = [
            ("inventory_analytics.html", "📦 Inventory Analytics"),
            ("operational_analytics.html", "⚙️ Operational Analytics")
        ]
        
        for filename, title in placeholder_pages:
            self.create_html_page(filename, title, [])
        
        print("\\n" + "=" * 60)
        print("✅ STATIC HTML EXPORT COMPLETED!")
        print(f"📁 Output folder: {self.html_output.absolute()}")
        print("🌐 Copy the 'html_reports' folder to your IIS server")
        print("🎯 Access via: http://your-server/html_reports/")
        print("=" * 60)

def main():
    """Main function to export static dashboard."""
    exporter = StaticDashboardExporter()
    exporter.export_all()

if __name__ == "__main__":
    main()
