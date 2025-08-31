@echo off
title Deploy Dashboard to IIS
echo.
echo ================================================================
echo              STOCK ANALYTICS DASHBOARD - IIS DEPLOYMENT
echo ================================================================
echo.

REM Check if html_reports folder exists
if not exist "html_reports" (
    echo ERROR: html_reports folder not found!
    echo Please run: python export_static_dashboard.py first
    echo.
    pause
    exit /b 1
)

echo Available options:
echo.
echo 1. Copy to Default IIS Website (C:\inetpub\wwwroot\dashboard)
echo 2. Copy to Custom Location
echo 3. Create ZIP package for manual deployment
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto default_iis
if "%choice%"=="2" goto custom_location
if "%choice%"=="3" goto create_zip
if "%choice%"=="4" goto end

echo Invalid choice. Exiting.
goto end

:default_iis
echo.
echo Copying to Default IIS Location...
set target_dir=C:\inetpub\wwwroot\dashboard

if not exist "%target_dir%" (
    echo Creating directory: %target_dir%
    mkdir "%target_dir%"
)

echo Copying files...
xcopy "html_reports\*.*" "%target_dir%\" /E /Y /I

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo SUCCESS: Dashboard deployed to IIS!
    echo.
    echo Access your dashboard at:
    echo   http://localhost/dashboard/
    echo   http://your-server-ip/dashboard/
    echo.
    echo Next steps:
    echo 1. Open IIS Manager
    echo 2. Verify the 'dashboard' folder is accessible
    echo 3. Test the URL in your browser
    echo ================================================================
) else (
    echo.
    echo ERROR: Failed to copy files. Check permissions.
    echo You may need to run as Administrator.
)
goto end

:custom_location
echo.
set /p custom_path="Enter target directory path: "

if not exist "%custom_path%" (
    echo Creating directory: %custom_path%
    mkdir "%custom_path%"
)

echo Copying files...
xcopy "html_reports\*.*" "%custom_path%\" /E /Y /I

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Dashboard copied to %custom_path%
    echo Configure IIS to point to this location.
) else (
    echo ERROR: Failed to copy files.
)
goto end

:create_zip
echo.
echo Creating deployment package...

REM Use PowerShell to create ZIP if available
powershell -command "Compress-Archive -Path 'html_reports\*' -DestinationPath 'dashboard_for_iis.zip' -Force"

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo SUCCESS: Created dashboard_for_iis.zip
    echo.
    echo Instructions:
    echo 1. Copy dashboard_for_iis.zip to your IIS server
    echo 2. Extract to desired location (e.g., C:\inetpub\wwwroot\dashboard)
    echo 3. Configure IIS virtual directory or application
    echo 4. Test access via web browser
    echo ================================================================
) else (
    echo ERROR: Failed to create ZIP package.
    echo Please manually copy the html_reports folder.
)
goto end

:end
echo.
pause
