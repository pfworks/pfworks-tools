#!/bin/bash

# HAL 9000 Interface Packaging Script
# Creates a complete distribution package

set -e

PACKAGE_NAME="hal9000-system-interface"
VERSION="2.0"
PACKAGE_DIR="${PACKAGE_NAME}-${VERSION}"
ARCHIVE_NAME="${PACKAGE_DIR}.tar.gz"

echo "Creating HAL 9000 System Interface distribution package..."

# Clean up any existing package
rm -rf "$PACKAGE_DIR" "$ARCHIVE_NAME" 2>/dev/null || true

# Create package directory
mkdir -p "$PACKAGE_DIR"

echo "Copying files to package directory..."

# Copy main files
cp hal_gui.py "$PACKAGE_DIR/"
cp hal_gui_no_pil.py "$PACKAGE_DIR/"
cp hal_debug.py "$PACKAGE_DIR/"
cp test_pil.py "$PACKAGE_DIR/"
cp install.sh "$PACKAGE_DIR/"
cp launch_hal.sh "$PACKAGE_DIR/"
cp test_hal.sh "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"
cp README.md "$PACKAGE_DIR/"
cp LICENSE "$PACKAGE_DIR/"
cp SHELL_MODE_GUIDE.md "$PACKAGE_DIR/"

# Copy macOS-specific files (if they exist)
if [ -f "hal_gui_macos.py" ]; then
    cp hal_gui_macos.py "$PACKAGE_DIR/"
fi
if [ -f "launch_hal_macos.sh" ]; then
    cp launch_hal_macos.sh "$PACKAGE_DIR/"
fi
if [ -f "README_MACOS.md" ]; then
    cp README_MACOS.md "$PACKAGE_DIR/"
fi

# Copy test and utility files (if they exist)
if [ -f "test_ansi_filter.py" ]; then
    cp test_ansi_filter.py "$PACKAGE_DIR/"
fi
if [ -f "test_wsl.py" ]; then
    cp test_wsl.py "$PACKAGE_DIR/"
fi
if [ -f "WINDOWS_WSL_GUIDE.md" ]; then
    cp WINDOWS_WSL_GUIDE.md "$PACKAGE_DIR/"
fi

# Create assets directory
mkdir -p "$PACKAGE_DIR/assets"

# Check if HAL image already exists locally
if [ -f "assets/Hal_9000_Panel.svg.png" ]; then
    echo "Using existing HAL image..."
    cp "assets/Hal_9000_Panel.svg.png" "$PACKAGE_DIR/assets/"
elif [ -f "Hal_9000_Panel.svg.png" ]; then
    echo "Using HAL image from current directory..."
    cp "Hal_9000_Panel.svg.png" "$PACKAGE_DIR/assets/"
else
    # Download HAL image directly into package
    echo "Downloading HAL 9000 panel image for package..."
    IMAGE_URL="https://upload.wikimedia.org/wikipedia/commons/f/f6/Hal_9000_Panel.svg.png"
    IMAGE_PATH="$PACKAGE_DIR/assets/Hal_9000_Panel.svg.png"
    
    if command -v wget &> /dev/null; then
        if wget -q -O "$IMAGE_PATH" "$IMAGE_URL"; then
            echo "HAL image downloaded successfully."
        else
            echo "Warning: Failed to download HAL image with wget."
        fi
    elif command -v curl &> /dev/null; then
        if curl -s -L -o "$IMAGE_PATH" "$IMAGE_URL"; then
            echo "HAL image downloaded successfully."
        else
            echo "Warning: Failed to download HAL image with curl."
        fi
    else
        echo "Warning: Neither wget nor curl found. Package will not include HAL image."
        echo "Users can download it manually or the installer will handle it."
    fi
fi

# Create package info file
cat > "$PACKAGE_DIR/PACKAGE_INFO" << EOF
HAL 9000 Interface Package
Version: $VERSION
Created: $(date)

Contents:
- hal_gui.py          : Main GUI application (with PIL support)
- hal_gui_no_pil.py   : PIL-free version (animated eye fallback)
- install.sh          : Automated installer script
- launch_hal.sh       : Direct launcher script
- test_hal.sh         : Troubleshooting and test script
- requirements.txt    : Python dependencies
- README.md           : Complete documentation
- LICENSE             : GNU General Public License v3.0
- SHELL_MODE_GUIDE.md : Shell mode usage guide
- assets/             : HAL 9000 panel image and resources

Installation:
1. Extract this package
2. Run: ./install.sh

Manual Installation:
1. Extract this package
2. Install dependencies: pip install -r requirements.txt
3. Run directly: ./launch_hal.sh

Attribution:
HAL 9000 Panel Image by Tom Cowap - Own work, CC BY-SA 4.0
https://commons.wikimedia.org/w/index.php?curid=103068276
EOF

# Create quick start guide
cat > "$PACKAGE_DIR/QUICKSTART.md" << 'EOF'
# HAL 9000 Interface - Quick Start

## Automated Installation (Recommended)

```bash
# Extract the package
tar -xzf hal9000-interface-*.tar.gz
cd hal9000-interface-*

# Run the installer
./install.sh

# Launch HAL
hal9000
```

## Troubleshooting & Testing

If you encounter PIL/ImageTk issues:

```bash
# Extract the package
tar -xzf hal9000-interface-*.tar.gz
cd hal9000-interface-*

# Run the troubleshooting script
./test_hal.sh
```

This script will:
- Check system requirements
- Fix PIL/ImageTk issues automatically
- Launch the best available HAL version

## Manual Installation

```bash
# Extract the package
tar -xzf hal9000-interface-*.tar.gz
cd hal9000-interface-*

# Install Python dependencies
pip install -r requirements.txt

# Launch directly (PIL version)
./launch_hal.sh

# Or launch PIL-free version
python3 hal_gui_no_pil.py
```

## Shell Mode Usage

1. **Launch HAL** using any method above
2. **Click "SHELL" button** in the interface
3. **Type shell commands** in cyan input field
4. **Switch back** with "Q CLI" button

See `SHELL_MODE_GUIDE.md` for detailed shell mode instructions.

## Features

- **Q CLI Mode**: Direct Amazon Q integration for AWS assistance
- **Shell Mode**: Execute bash commands with real-time output
- **HAL Aesthetic**: Authentic HAL 9000 panel image and retro styling
- **Conversation Logging**: Save and export your interactions
- **PIL-Free Fallback**: Works even without image support

## Requirements

- Python 3.6+
- tkinter (usually included)
- Amazon Q CLI (for Q mode)
- PIL/Pillow (optional, for HAL image)

The installer and test script will check all requirements and guide you through any missing dependencies.

---

*"I'm sorry, Dave. I'm afraid I can't do that."*
*But this HAL can help you with AWS and system operations!* 🚀
EOF

# Make scripts executable
chmod +x "$PACKAGE_DIR/install.sh"
chmod +x "$PACKAGE_DIR/launch_hal.sh"
chmod +x "$PACKAGE_DIR/test_hal.sh"
chmod +x "$PACKAGE_DIR/hal_gui.py"
chmod +x "$PACKAGE_DIR/hal_gui_no_pil.py"
chmod +x "$PACKAGE_DIR/hal_debug.py"
chmod +x "$PACKAGE_DIR/test_pil.py"

# Create the archive
echo "Creating archive: $ARCHIVE_NAME"
tar -czf "$ARCHIVE_NAME" "$PACKAGE_DIR"

# Create checksum
if command -v sha256sum &> /dev/null; then
    sha256sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"
    echo "Checksum created: ${ARCHIVE_NAME}.sha256"
elif command -v shasum &> /dev/null; then
    shasum -a 256 "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"
    echo "Checksum created: ${ARCHIVE_NAME}.sha256"
fi

# Display package info
echo ""
echo "Package created successfully!"
echo ""
echo "Package: $ARCHIVE_NAME"
echo "Size: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo "Contents:"
echo "  - Complete HAL 9000 system interface application"
echo "  - Automated installer with dependency checking"
if [ -f "$PACKAGE_DIR/assets/Hal_9000_Panel.svg.png" ]; then
    echo "  - HAL 9000 panel image (CC BY-SA 4.0)"
else
    echo "  - HAL image will be downloaded during installation"
fi
echo "  - Documentation and quick start guide"
echo ""
echo "To distribute:"
echo "  1. Share the $ARCHIVE_NAME file"
echo "  2. Recipients extract and run: ./install.sh"
echo ""
echo "Package contents:"
find "$PACKAGE_DIR" -type f | sort

# Clean up package directory (keep archive)
rm -rf "$PACKAGE_DIR"

echo ""
echo "Distribution package ready: $ARCHIVE_NAME"
