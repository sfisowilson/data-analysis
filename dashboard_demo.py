#!/usr/bin/env python3
"""
Dashboard Demo Script
This script demonstrates the visualization capabilities by creating sample charts
and showing what the full dashboard would display.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def create_sample_visualizations():
    """Create sample visualizations to demonstrate dashboard capabilities."""
    
    print("📊 Creating sample visualizations from processed data...")
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Load the processed data
    output_folder = Path("output")
    
    # 1. Financial Overview Chart
    try:
        grn_df = pd.read_csv(output_folder / "hr995_grn.csv")
        
        if not grn_df.empty and 'nett_grn_amt' in grn_df.columns:
            grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
            
            # Top suppliers by value
            supplier_values = grn_df.groupby('supplier_name')['nett_grn_amt'].sum().nlargest(10)
            
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 2, 1)
            supplier_values.plot(kind='barh')
            plt.title('Top 10 Suppliers by Total GRN Value')
            plt.xlabel('Total Value (R)')
            plt.tight_layout()
            
            # Monthly trend
            if 'date' in grn_df.columns:
                grn_df['date'] = pd.to_datetime(grn_df['date'], errors='coerce')
                grn_df['month'] = grn_df['date'].dt.to_period('M')
                monthly_values = grn_df.groupby('month')['nett_grn_amt'].sum()
                
                plt.subplot(2, 2, 2)
                monthly_values.plot(kind='line', marker='o')
                plt.title('Monthly GRN Value Trend')
                plt.ylabel('Total Value (R)')
                plt.xticks(rotation=45)
            
            print("✅ Financial analysis charts created")
    
    except Exception as e:
        print(f"⚠️  Could not create financial charts: {str(e)}")
    
    # 2. Stock Movement Analysis
    try:
        audit_df = pd.read_csv(output_folder / "objective_2_stock_audit_trail.csv")
        
        if not audit_df.empty and 'transaction_type' in audit_df.columns:
            transaction_counts = audit_df['transaction_type'].value_counts()
            
            plt.subplot(2, 2, 3)
            transaction_counts.plot(kind='pie', autopct='%1.1f%%')
            plt.title('Stock Movement by Transaction Type')
            plt.ylabel('')
            
            print("✅ Stock movement charts created")
    
    except Exception as e:
        print(f"⚠️  Could not create stock movement charts: {str(e)}")
    
    # 3. HR995 Report Summary
    try:
        hr995_df = pd.read_csv(output_folder / "objective_3_hr995_report.csv")
        
        if not hr995_df.empty and 'hr995_type' in hr995_df.columns:
            hr995_counts = hr995_df['hr995_type'].value_counts()
            
            plt.subplot(2, 2, 4)
            hr995_counts.plot(kind='bar')
            plt.title('HR995 Report Breakdown')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            print("✅ HR995 analysis charts created")
    
    except Exception as e:
        print(f"⚠️  Could not create HR995 charts: {str(e)}")
    
    # Save the combined chart
    plt.tight_layout()
    plt.savefig('dashboard_sample_charts.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n📊 Sample visualization saved as 'dashboard_sample_charts.png'")

def create_summary_statistics():
    """Create summary statistics table."""
    
    print("\n📈 DASHBOARD ANALYTICS SUMMARY")
    print("=" * 50)
    
    output_folder = Path("output")
    
    # Load key datasets
    datasets = {
        "Master Data": "all_stock_data.csv",
        "GRN Transactions": "hr995_grn.csv", 
        "Stock Issues": "hr995_issue.csv",
        "Vouchers": "hr995_voucher.csv",
        "Suppliers": "suppliers.csv",
        "Stock Adjustments": "stock_adjustments.csv"
    }
    
    summary_stats = []
    
    for name, filename in datasets.items():
        file_path = output_folder / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                
                stats = {
                    'Dataset': name,
                    'Records': len(df),
                    'Columns': len(df.columns),
                    'Memory_MB': round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                    'Completeness': f"{((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%"
                }
                summary_stats.append(stats)
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Create summary DataFrame
    if summary_stats:
        summary_df = pd.DataFrame(summary_stats)
        print(summary_df.to_string(index=False))
        
        # Financial summary
        try:
            grn_df = pd.read_csv(output_folder / "hr995_grn.csv")
            if 'nett_grn_amt' in grn_df.columns:
                grn_df['nett_grn_amt'] = pd.to_numeric(grn_df['nett_grn_amt'], errors='coerce')
                total_value = grn_df['nett_grn_amt'].sum()
                
                print(f"\n💰 FINANCIAL HIGHLIGHTS")
                print(f"Total GRN Value: R{total_value:,.2f}")
                print(f"Average Transaction: R{grn_df['nett_grn_amt'].mean():,.2f}")
                print(f"Largest Transaction: R{grn_df['nett_grn_amt'].max():,.2f}")
                
        except Exception as e:
            print(f"Could not calculate financial summary: {str(e)}")

def demonstrate_dashboard_features():
    """Show what features are available in the dashboard."""
    
    print("\n🎨 DASHBOARD FEATURES AVAILABLE")
    print("=" * 50)
    
    features = [
        "📊 Interactive Overview with Key Metrics",
        "💰 Financial Analysis with Trend Charts", 
        "🏪 Supplier Performance Analytics",
        "📦 Stock Movement Tracking & Heatmaps",
        "📋 Inventory Analysis & Distribution",
        "📈 Time-Series Trend Analysis",
        "🔍 Data Quality Assessment",
        "🔄 Real-time Data Refresh",
        "📱 Responsive Design for Mobile/Desktop",
        "📊 Interactive Charts with Plotly",
        "💾 Export Functionality",
        "🎯 Drill-down Capabilities"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n🌐 ACCESS DASHBOARD")
    print("=" * 50)
    print("1. Run: python launch_dashboard.py")
    print("2. Open browser to: http://localhost:8501")
    print("3. Navigate through different sections using sidebar")
    print("4. Interact with charts by hovering, zooming, filtering")

def main():
    """Main demo function."""
    
    print("🎨 STOCK DATA VISUALIZATION DASHBOARD DEMO")
    print("=" * 60)
    
    # Check if data exists
    output_folder = Path("output")
    if not output_folder.exists():
        print("❌ No processed data found!")
        print("Please run 'python stock_data_processor.py' first.")
        return
    
    # Create sample visualizations
    create_sample_visualizations()
    
    # Show summary statistics
    create_summary_statistics()
    
    # Demonstrate dashboard features
    demonstrate_dashboard_features()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO LAUNCH FULL DASHBOARD!")
    print("Run 'python launch_dashboard.py' to start the interactive web application")
    print("=" * 60)

if __name__ == "__main__":
    main()
