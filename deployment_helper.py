# Quick deployment scripts for different hosting scenarios

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required = ['streamlit', 'pandas', 'plotly', 'openpyxl', 'pdfplumber']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    return True

def deploy_local_network():
    """Deploy for local network access"""
    print("🌐 Deploying for Local Network Access...")
    print("Dashboard will be accessible to anyone on your network")
    print("URL will be: http://YOUR_IP_ADDRESS:8502")
    
    # Get local IP
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Your IP: {local_ip}")
        print(f"Access URL: http://{local_ip}:8502")
    except:
        print("Could not determine IP address")
    
    print("\nStarting dashboard...")
    cmd = [
        sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py",
        "--server.address", "0.0.0.0",
        "--server.port", "8502",
        "--server.headless", "false"
    ]
    subprocess.run(cmd)

def create_docker_files():
    """Create Docker deployment files"""
    print("🐳 Creating Docker deployment files...")
    
    # Dockerfile
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 8502

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8502/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "enhanced_dashboard.py", "--server.address", "0.0.0.0", "--server.port", "8502"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    # Docker Compose
    compose_content = """version: '3.8'

services:
  stock-dashboard:
    build: .
    ports:
      - "8502:8502"
    volumes:
      - ./output:/app/output:ro
      - ./Data Hand-Over:/app/Data Hand-Over:ro
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8502/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    # Build script
    build_script = """#!/bin/bash
# Docker deployment script

echo "🐳 Building Docker image..."
docker build -t stock-dashboard .

echo "🚀 Starting container..."
docker run -d \\
    --name stock-dashboard \\
    -p 8502:8502 \\
    -v "$(pwd)/output:/app/output:ro" \\
    -v "$(pwd)/Data Hand-Over:/app/Data Hand-Over:ro" \\
    stock-dashboard

echo "✅ Dashboard deployed!"
echo "Access at: http://localhost:8502"
echo "To stop: docker stop stock-dashboard"
echo "To remove: docker rm stock-dashboard"
"""
    
    with open("deploy_docker.sh", "w") as f:
        f.write(build_script)
    
    # Windows batch script
    batch_script = """@echo off
echo 🐳 Building Docker image...
docker build -t stock-dashboard .

echo 🚀 Starting container...
docker run -d ^
    --name stock-dashboard ^
    -p 8502:8502 ^
    -v "%cd%/output:/app/output:ro" ^
    -v "%cd%/Data Hand-Over:/app/Data Hand-Over:ro" ^
    stock-dashboard

echo ✅ Dashboard deployed!
echo Access at: http://localhost:8502
echo To stop: docker stop stock-dashboard
echo To remove: docker rm stock-dashboard
pause
"""
    
    with open("deploy_docker.bat", "w") as f:
        f.write(batch_script)
    
    print("✅ Created Docker files:")
    print("  - Dockerfile")
    print("  - docker-compose.yml")
    print("  - deploy_docker.sh (Linux/Mac)")
    print("  - deploy_docker.bat (Windows)")

def create_cloud_deployment():
    """Create cloud deployment files"""
    print("☁️ Creating cloud deployment files...")
    
    # Streamlit config for cloud
    streamlit_config = """[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    
    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/config.toml", "w") as f:
        f.write(streamlit_config)
    
    # GitHub Actions workflow
    workflow_content = """name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test dashboard
      run: |
        python -c "import streamlit; print('Streamlit OK')"
        python -c "import enhanced_dashboard; print('Dashboard OK')"
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/deploy.yml", "w") as f:
        f.write(workflow_content)
    
    # Heroku Procfile
    with open("Procfile", "w") as f:
        f.write("web: streamlit run enhanced_dashboard.py --server.port=$PORT --server.address=0.0.0.0\n")
    
    # Railway deployment
    railway_config = """{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run enhanced_dashboard.py --server.port=$PORT --server.address=0.0.0.0",
    "healthcheckPath": "/_stcore/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}"""
    
    with open("railway.json", "w") as f:
        f.write(railway_config)
    
    print("✅ Created cloud deployment files:")
    print("  - .streamlit/config.toml")
    print("  - .github/workflows/deploy.yml")
    print("  - Procfile (Heroku)")
    print("  - railway.json (Railway)")

def create_windows_service():
    """Create Windows service files"""
    print("🖥️ Creating Windows service files...")
    
    # Windows service batch file
    service_script = f"""@echo off
title Stock Analytics Dashboard
echo 🚀 Starting Stock Analytics Dashboard...
echo.
echo Dashboard will be available at:
echo   - Local: http://localhost:8502
echo   - Network: http://%COMPUTERNAME%:8502
echo.
echo Press Ctrl+C to stop the dashboard
echo.

cd /d "{os.getcwd()}"
"{os.getcwd()}\\.venv\\Scripts\\python.exe" -m streamlit run enhanced_dashboard.py --server.address 0.0.0.0 --server.port 8502

pause
"""
    
    with open("start_dashboard_service.bat", "w") as f:
        f.write(service_script)
    
    # Auto-start script
    autostart_script = f"""@echo off
echo Creating auto-start shortcut...

set "script_path={os.getcwd()}\\start_dashboard_service.bat"
set "startup_folder=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
set "shortcut_path=%startup_folder%\\Stock Dashboard.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut_path%'); $Shortcut.TargetPath = '%script_path%'; $Shortcut.Save()"

echo ✅ Auto-start shortcut created!
echo Dashboard will start automatically when Windows boots.
echo.
echo To remove auto-start, delete: %shortcut_path%
pause
"""
    
    with open("setup_autostart.bat", "w") as f:
        f.write(autostart_script)
    
    print("✅ Created Windows service files:")
    print("  - start_dashboard_service.bat")
    print("  - setup_autostart.bat")

def main():
    print("🚀 Stock Analytics Dashboard Deployment Helper")
    print("=" * 50)
    
    if not check_requirements():
        return
    
    print("\nSelect deployment option:")
    print("1. 🌐 Local Network (accessible to your network)")
    print("2. 🐳 Docker (containerized deployment)")
    print("3. ☁️ Cloud Deployment Files (Streamlit Cloud, Heroku, etc.)")
    print("4. 🖥️ Windows Service (auto-start on boot)")
    print("5. 📖 Show hosting guide")
    print("6. 🏃 Quick start (current directory)")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        deploy_local_network()
    elif choice == "2":
        create_docker_files()
        print("\nTo deploy with Docker:")
        print("  Windows: deploy_docker.bat")
        print("  Linux/Mac: ./deploy_docker.sh")
    elif choice == "3":
        create_cloud_deployment()
        print("\nNext steps for cloud deployment:")
        print("1. Push code to GitHub")
        print("2. Connect repository to Streamlit Cloud")
        print("3. Deploy enhanced_dashboard.py")
    elif choice == "4":
        create_windows_service()
        print("\nTo set up Windows service:")
        print("1. Run start_dashboard_service.bat")
        print("2. Optional: Run setup_autostart.bat for auto-start")
    elif choice == "5":
        print("\n📖 Hosting guide created: HOSTING_GUIDE.md")
        print("Open this file for comprehensive hosting instructions")
    elif choice == "6":
        print("🏃 Quick starting dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py"])
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
