#!/bin/bash
# QIS v6.0 - Cross-Platform Shell Launcher
# For Linux and macOS systems

echo "QIS v6.0 - Cross-Platform AI Personality Interface"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

# Check if QIS file exists
if [ ! -f "qis_v6.py" ]; then
    echo "Error: qis_v6.py not found in current directory"
    echo "Please run this script from the QIS directory"
    exit 1
fi

echo "Starting QIS v6.0..."
echo ""
echo "Features:"
echo "- Cross-platform support (Windows/Linux/macOS)"
echo "- 3 AI personalities (HAL 9000, Star Trek, TRS-80)"
echo "- Local Q CLI integration"
echo "- SSH remote Q CLI support"
echo "- Native shell integration"
echo ""

# Launch QIS
python3 qis_v6.py

echo ""
echo "QIS v6.0 session ended."
