#!/bin/bash

echo "HAL 9000 Interface - Troubleshooting & Launch"
echo "=============================================="

# Check Python and tkinter
echo "1. Checking Python and tkinter..."
python3 --version
python3 -c "import tkinter; print('✓ tkinter available')" 2>/dev/null || {
    echo "✗ tkinter not available"
    echo "Install with: sudo apt-get install python3-tk"
    exit 1
}

# Check PIL status
echo ""
echo "2. Checking PIL status..."
python3 -c "
try:
    import PIL
    print('✓ PIL module found')
    try:
        from PIL import Image
        print('✓ PIL.Image available')
    except ImportError as e:
        print('✗ PIL.Image not available:', e)
    
    try:
        from PIL import ImageTk
        print('✓ PIL.ImageTk available')
    except ImportError as e:
        print('✗ PIL.ImageTk not available:', e)
except ImportError:
    print('✗ PIL module not found')
"

echo ""
echo "3. Attempting to fix PIL issues..."

# Try different PIL installation methods
if ! python3 -c "from PIL import Image, ImageTk" 2>/dev/null; then
    echo "Trying to install PIL packages..."
    
    # Method 1: System packages
    if command -v apt-get &> /dev/null; then
        echo "Installing system PIL packages..."
        sudo apt-get update
        sudo apt-get install -y python3-pil python3-pil.imagetk
    fi
    
    # Method 2: pip install
    echo "Installing Pillow via pip..."
    pip3 install --user --upgrade Pillow
    
    # Test again
    echo "Testing PIL after installation..."
    python3 -c "
try:
    from PIL import Image, ImageTk
    print('✓ PIL installation successful!')
except ImportError as e:
    print('✗ PIL still not working:', e)
    print('Will use PIL-free version')
"
fi

echo ""
echo "4. Launching HAL interface..."

# Try PIL version first, fall back to PIL-free version
if python3 -c "from PIL import Image, ImageTk" 2>/dev/null; then
    echo "Using full HAL interface with image support..."
    python3 hal_gui.py
else
    echo "Using PIL-free HAL interface with animated eye..."
    python3 hal_gui_no_pil.py
fi
