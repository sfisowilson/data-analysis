@echo off
title Stock Dashboard Hosting Options
color 0A

echo.
echo  ███████╗████████╗ ██████╗  ██████╗██╗  ██╗    ██████╗  █████╗ ███████╗██╗  ██╗
echo  ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║
echo  ███████╗   ██║   ██║   ██║██║     █████╔╝     ██║  ██║███████║███████╗███████║
echo  ╚════██║   ██║   ██║   ██║██║     ██╔═██╗     ██║  ██║██╔══██║╚════██║██╔══██║
echo  ███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗    ██████╔╝██║  ██║███████║██║  ██║
echo  ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
echo.
echo                            🚀 HOSTING DEPLOYMENT CENTER 🚀
echo.
echo ================================================================================
echo.

:menu
echo 🌟 HOSTING OPTIONS:
echo.
echo [1] 🖥️  Local Development (This Computer Only)
echo     - Access: http://localhost:8502
echo     - Perfect for: Testing and development
echo.
echo [2] 🌐 Network Sharing (Company/Home Network)
echo     - Access: http://YOUR-IP:8502 from any device on network
echo     - Perfect for: Team access, internal company use
echo.
echo [3] ☁️  Internet Hosting (Public Access - Streamlit Cloud)
echo     - Access: https://yourapp.streamlit.app
echo     - Perfect for: External clients, public dashboards
echo.
echo [4] 🐳 Docker Deployment (Professional Setup)
echo     - Access: Configurable ports and domains
echo     - Perfect for: Production environments, multiple instances
echo.
echo [5] 📋 Show Full Hosting Guide
echo [6] ❌ Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto network
if "%choice%"=="3" goto cloud
if "%choice%"=="4" goto docker
if "%choice%"=="5" goto guide
if "%choice%"=="6" goto exit
echo Invalid choice. Please try again.
goto menu

:local
echo.
echo 🖥️ STARTING LOCAL DEVELOPMENT SERVER...
echo ================================================================================
echo.
echo ✅ Dashboard will open in your default browser
echo ✅ Access URL: http://localhost:8502
echo ✅ Only accessible from this computer
echo.
echo 💡 Tips:
echo    - Keep this window open while using the dashboard
echo    - Press Ctrl+C to stop the server
echo    - Use this for development and testing
echo.
pause
"%~dp0.venv\Scripts\python.exe" -m streamlit run "%~dp0enhanced_dashboard.py"
goto end

:network
echo.
echo 🌐 STARTING NETWORK SERVER...
echo ================================================================================
echo.
echo ✅ Dashboard will be accessible from any device on your network
echo ✅ Getting your network IP address...

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "ip=%%a"
    goto :found_ip
)
:found_ip
set ip=%ip: =%

echo.
echo 🔗 ACCESS URLS:
echo    📱 From this computer: http://localhost:8502
echo    🌐 From other devices: http://%ip%:8502
echo.
echo 💡 Tips:
echo    - Share the network URL with your team
echo    - Make sure Windows Firewall allows the connection
echo    - Works great for internal company dashboards
echo.
echo 🔥 Starting server...
pause
"%~dp0.venv\Scripts\python.exe" -m streamlit run "%~dp0enhanced_dashboard.py" --server.address 0.0.0.0 --server.port 8502
goto end

:cloud
echo.
echo ☁️ CLOUD HOSTING SETUP
echo ================================================================================
echo.
echo 🎯 STREAMLIT CLOUD (FREE & RECOMMENDED):
echo.
echo 📋 STEPS TO DEPLOY:
echo    1. Create GitHub account (if you don't have one)
echo    2. Upload your dashboard files to GitHub repository
echo    3. Visit: https://share.streamlit.io/
echo    4. Connect your GitHub account
echo    5. Select your repository and enhanced_dashboard.py
echo    6. Click Deploy!
echo.
echo 📁 FILES YOU NEED TO UPLOAD:
echo    ✅ enhanced_dashboard.py
echo    ✅ requirements.txt
echo    ✅ output/ folder (with your CSV files)
echo.
echo 🌟 RESULT:
echo    ✅ Free public URL: https://yourapp.streamlit.app
echo    ✅ Automatic updates when you push to GitHub
echo    ✅ Professional hosting with SSL
echo.
echo 🔧 ALTERNATIVE CLOUD OPTIONS:
echo    - Heroku (with Procfile)
echo    - Railway.app
echo    - Google Cloud Run
echo    - AWS Elastic Beanstalk
echo.
echo Would you like me to prepare the cloud deployment files? (y/n)
set /p prep_cloud="Prepare cloud files: "
if /i "%prep_cloud%"=="y" (
    echo.
    echo 📦 Creating cloud deployment files...
    "%~dp0.venv\Scripts\python.exe" "%~dp0deployment_helper.py"
)
echo.
echo 📖 For detailed cloud setup instructions, see: HOSTING_GUIDE.md
pause
goto menu

:docker
echo.
echo 🐳 DOCKER DEPLOYMENT
echo ================================================================================
echo.
echo 🎯 CONTAINERIZED DEPLOYMENT:
echo.
echo 📋 REQUIREMENTS:
echo    ✅ Docker Desktop installed on your system
echo    ✅ Basic Docker knowledge recommended
echo.
echo 🚀 DOCKER BENEFITS:
echo    ✅ Consistent environment across systems
echo    ✅ Easy scaling and deployment
echo    ✅ Professional production setup
echo    ✅ Portable to any Docker-enabled server
echo.
echo 📦 Creating Docker files...
"%~dp0.venv\Scripts\python.exe" -c "
import sys
sys.path.append(r'%~dp0')
from deployment_helper import create_docker_files
create_docker_files()
"
echo.
echo ✅ Docker files created!
echo.
echo 🔨 TO BUILD AND RUN:
echo    1. Open command prompt in this folder
echo    2. Run: docker build -t stock-dashboard .
echo    3. Run: docker run -p 8502:8502 stock-dashboard
echo    4. Access: http://localhost:8502
echo.
echo 💡 TIP: Use docker-compose for easier management:
echo    docker-compose up -d
echo.
pause
goto menu

:guide
echo.
echo 📖 OPENING FULL HOSTING GUIDE...
echo ================================================================================
start notepad.exe "%~dp0HOSTING_GUIDE.md"
echo.
echo ✅ Full hosting guide opened in Notepad
echo    Contains detailed instructions for all hosting options
echo.
pause
goto menu

:exit
echo.
echo 👋 Thanks for using Stock Analytics Dashboard!
echo    For support, check HOSTING_GUIDE.md
echo.
pause
exit

:end
echo.
echo 🎉 Dashboard session ended.
echo    To restart, run this script again.
echo.
pause
goto menu
