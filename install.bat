@echo off
echo ========================================
echo    Auto-Slideshow Generator V2 Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment.
    echo.
    pause
    exit /b 1
)
echo Done!
echo.

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Done!
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo Done!
echo.

:: Install package in development mode
echo Installing Auto-Slideshow...
pip install -e .
if %errorlevel% neq 0 (
    echo Error: Failed to install Auto-Slideshow.
    echo.
    pause
    exit /b 1
)
echo Done!
echo.

:: Create template directories
echo Creating template directories...
mkdir v2\templates >nul 2>&1
echo Done!
echo.

echo ========================================
echo Installation completed successfully!
echo.
echo To create slideshows:
echo 1. Use run.bat to launch the slideshow creator
echo 2. Or run directly with: venv\Scripts\python -m v2.main
echo ========================================
echo.

pause
