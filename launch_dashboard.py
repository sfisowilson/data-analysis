#!/usr/bin/env python3
"""
Dashboard Launcher Script
Easy launcher for the Stock Data Analytics Dashboard.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if the required data files exist."""
    output_folder = Path("output")
    required_files = [
        "all_stock_data.csv",
        "hr995_grn.csv",
        "hr995_issue.csv",
        "hr995_voucher.csv"
    ]
    
    if not output_folder.exists():
        print("❌ Output folder not found.")
        print("Please run 'python stock_data_processor.py' first to generate the data files.")
        return False
    
    missing_files = []
    for file in required_files:
        if not (output_folder / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Some data files are missing: {', '.join(missing_files)}")
        print("The dashboard will still work, but some charts may not display.")
        print("Run 'python stock_data_processor.py' to generate all data files.")
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print("🚀 Launching Stock Data Analytics Dashboard...")
    print("📊 Dashboard will open in your default web browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {str(e)}")

def main():
    """Main launcher function."""
    print("="*60)
    print("📊 STOCK DATA ANALYTICS DASHBOARD LAUNCHER")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check data files
    if not check_data_files():
        return
    
    print("✅ All requirements met!")
    print("✅ Data files found!")
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
