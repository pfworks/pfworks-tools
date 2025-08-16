#!/bin/bash
# HAL 9000 System Interface - macOS Launcher
# Optimized launcher for macOS systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}HAL 9000 System Interface - macOS Edition${NC}"
echo -e "${BLUE}===========================================${NC}"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}Warning: This is the macOS-optimized version but you're not running macOS.${NC}"
    echo -e "${YELLOW}Consider using the standard version: ./launch_hal.sh${NC}"
    echo ""
fi

# Check Python installation
echo -e "${BLUE}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    if [[ $PYTHON_VERSION == 3.* ]]; then
        echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}✗ Python 3 required, found Python $PYTHON_VERSION${NC}"
        echo -e "${YELLOW}Please install Python 3: brew install python3${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python not found${NC}"
    echo -e "${YELLOW}Please install Python 3: brew install python3${NC}"
    exit 1
fi

# Check tkinter availability
echo -e "${BLUE}Checking tkinter availability...${NC}"
if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo -e "${GREEN}✓ tkinter is available${NC}"
else
    echo -e "${RED}✗ tkinter not available${NC}"
    echo -e "${YELLOW}tkinter should be included with Python on macOS${NC}"
    echo -e "${YELLOW}If missing, try: brew install python-tk${NC}"
    exit 1
fi

# Check for PIL (optional)
echo -e "${BLUE}Checking PIL/Pillow (optional for HAL image)...${NC}"
if $PYTHON_CMD -c "import PIL" 2>/dev/null; then
    echo -e "${GREEN}✓ PIL/Pillow is available - HAL image will be displayed${NC}"
    HAL_SCRIPT="hal_gui_macos.py"
else
    echo -e "${YELLOW}! PIL/Pillow not found - HAL image will not be displayed${NC}"
    echo -e "${YELLOW}  To install: pip3 install Pillow${NC}"
    HAL_SCRIPT="hal_gui_macos.py"
fi

# Check for HAL script
if [[ ! -f "$HAL_SCRIPT" ]]; then
    echo -e "${RED}✗ HAL script not found: $HAL_SCRIPT${NC}"
    exit 1
fi

# macOS-specific optimizations
echo -e "${BLUE}Applying macOS optimizations...${NC}"

# Set high-DPI scaling if on Retina display
if system_profiler SPDisplaysDataType | grep -q "Retina"; then
    echo -e "${GREEN}✓ Retina display detected - enabling high-DPI support${NC}"
    export TK_SILENCE_DEPRECATION=1  # Suppress tkinter deprecation warnings on macOS
fi

# Set proper font rendering
export PYTHONIOENCODING=utf-8

# Launch HAL
echo -e "${BLUE}Launching HAL 9000 System Interface (macOS Edition)...${NC}"
echo -e "${GREEN}Ready to assist with AWS operations and system commands.${NC}"
echo ""

# Run with proper error handling
if ! $PYTHON_CMD "$HAL_SCRIPT"; then
    echo ""
    echo -e "${RED}HAL encountered an error. Troubleshooting tips:${NC}"
    echo -e "${YELLOW}1. Ensure all dependencies are installed: pip3 install -r requirements.txt${NC}"
    echo -e "${YELLOW}2. Check Python version compatibility (3.6+)${NC}"
    echo -e "${YELLOW}3. Verify tkinter installation: python3 -c 'import tkinter'${NC}"
    echo -e "${YELLOW}4. For Q CLI integration, ensure Amazon Q CLI is installed${NC}"
    exit 1
fi
