@echo off
REM QIS v5.0 Launcher - Debug Mode
REM This version shows the terminal window for debugging

echo ========================================
echo QIS v5.0 - Debug Mode
echo ========================================
echo Terminal window will remain visible for debugging
echo Close this window to force-quit QIS
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Show Python version
echo Python version:
python --version
echo.

REM Launch QIS with visible terminal for debugging
echo Starting QIS v5.0...
echo.
python qis_v6.py

REM If we get here, QIS has exited
echo.
echo QIS v5.0 has exited.
pause
