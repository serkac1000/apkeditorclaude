@echo off
echo ===============================================
echo    Android App Builder Server Startup
echo ===============================================
echo Starting server on 127.0.0.1:5000...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required packages
echo Installing required packages...
pip install flask flask-cors requests pillow

REM Check if server.py exists
if not exist "server.py" (
    echo ERROR: server.py not found!
    echo Please save the Python Flask Server artifact as 'server.py' in this directory.
    echo.
    pause
    exit /b 1
)

REM Check if HTML file exists
if exist "android_app_builder.html" (
    echo HTML file found - server ready!
) else (
    echo WARNING: android_app_builder.html not found!
    echo Please save the HTML artifact as 'android_app_builder.html' in this directory.
    echo The server will still start but will show a placeholder page.
    echo.
)

echo.
echo ===============================================
echo Server starting... Opening browser...
echo ===============================================

REM Start the server
echo Starting Python Flask server...
start "" http://127.0.0.1:5000
python server.py

REM If server stops, pause to see any error messages
pause