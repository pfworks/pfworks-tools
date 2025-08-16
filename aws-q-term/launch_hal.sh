#!/bin/bash

# HAL GUI Launcher Script
# Launches the HAL-inspired GUI for Amazon Q CLI with shell capabilities

echo "Initializing HAL 9000 Interface..."
echo "Checking system requirements..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if Q CLI is available
if ! command -v q &> /dev/null; then
    echo "Warning: Q CLI not found in PATH."
    echo "Please ensure Amazon Q CLI is installed and configured."
    echo "Q CLI mode will be limited without proper installation."
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: tkinter is required but not available."
    echo "Please install python3-tk package:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  CentOS/RHEL: sudo yum install tkinter"
    exit 1
fi

# Check if Pillow is available for HAL image display
python3 -c "from PIL import Image, ImageTk" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: Pillow or ImageTk not fully available. HAL image will not be displayed."
    echo "To fix this:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-pil python3-pil.imagetk"
    echo "  Or: pip install --upgrade Pillow"
    echo "HAL interface will work with animated eye fallback."
    echo ""
fi

# Check if HAL image exists
if [ ! -f "assets/Hal_9000_Panel.svg.png" ]; then
    echo "Note: HAL image not found in assets/Hal_9000_Panel.svg.png"
    echo "Please place the HAL 9000 panel image in the assets directory for full visual experience."
    echo ""
fi

echo "All critical systems operational."
echo "Launching HAL 9000 Interface..."
echo ""
echo "Available modes:"
echo "  - Q CLI: Direct interaction with Amazon Q"
echo "  - SHELL: Execute bash commands and view output"
echo ""

# Launch the HAL GUI
python3 hal_gui.py
