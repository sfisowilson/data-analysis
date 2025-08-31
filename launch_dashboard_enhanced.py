#!/usr/bin/env python3
"""
Dashboard Launcher Script
Provides options to launch different versions of the stock data dashboard.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import streamlit
        import plotly
        import pandas
        return True
    except ImportError:
        return False

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Requirements installed successfully!")

def launch_basic_dashboard():
    """Launch the basic dashboard."""
    print("🚀 Launching Basic Stock Data Dashboard...")
    print("📊 Features: 4 main charts with basic analytics")
    print("🌐 Opening in your default browser...")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "dashboard.py",
        "--server.headless", "true",
        "--server.port", "8501"
    ])

def launch_enhanced_dashboard():
    """Launch the enhanced dashboard with 25+ charts."""
    print("🚀 Launching Enhanced Stock Analytics Dashboard...")
    print("📊 Features: 25+ interactive charts with drill-down capabilities")
    print("📈 Includes: Financial trends, supplier analytics, inventory management")
    print("🌐 Opening in your default browser...")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py",
        "--server.headless", "true",
        "--server.port", "8502"
    ])

def main():
    """Main launcher function."""
    print("=" * 60)
    print("📊 STOCK DATA ANALYTICS DASHBOARD LAUNCHER")
    print("=" * 60)
    
    # Check if data files exist
    output_folder = Path("output")
    if not output_folder.exists() or not list(output_folder.glob("*.csv")):
        print("⚠️  Warning: No data files found in 'output' folder!")
        print("Please run 'python stock_data_processor.py' first to generate data.")
        print("")
    
    # Check requirements
    if not check_requirements():
        print("📦 Installing required packages...")
        install_requirements()
    
    print("\nChoose your dashboard experience:")
    print("1. 🎯 Basic Dashboard (4 charts, quick overview)")
    print("2. 🚀 Enhanced Dashboard (25+ charts, comprehensive analytics)")
    print("3. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            launch_basic_dashboard()
            break
        elif choice == "2":
            launch_enhanced_dashboard()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
