@echo off
chcp 65001 >nul
title Zoom Bot Control Center
color 0B
cls

echo =====================================================================
echo          ZOOM BOT CONTROL CENTER - ONE-CLICK LAUNCHER
echo =====================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH!
    echo Please install Python 3.10 or higher from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Check and Setup Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creating Python Virtual Environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv!
        pause
        exit /b 1
    )
)

:: 3. Activate venv
call venv\Scripts\activate.bat

:: 4. Check & Install Dependencies
echo [2/3] Checking requirements...
pip install -r requirements.txt --quiet --disable-pip-version-check

:: 5. Launch Web Dashboard
echo [3/3] Launching ZoomBot Web Dashboard...
echo.
echo =====================================================================
echo  Web Dashboard will open automatically at:
echo  URL: http://127.0.0.1:5000
echo.
echo  To exit, simply close this window or press CTRL+C.
echo =====================================================================
echo.

python app.py

pause
