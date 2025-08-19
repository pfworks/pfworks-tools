@echo off
echo QIS v5.0 Installation
echo ====================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.6 or higher from https://python.org
    pause
    exit /b 1
)

echo Installing QIS v5.0 dependencies...
echo.

REM Install required packages
pip install Pillow
if errorlevel 1 (
    echo Warning: Could not install Pillow. HAL image may not display.
    echo This is optional - QIS will still work without it.
)

echo.
echo Installation complete!
echo.
echo To run QIS v5.0:
echo   launch_qis.bat
echo.
echo Or directly:
echo   python qis_v6.py
echo.
pause
