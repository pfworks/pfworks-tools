#!/bin/bash

# HAL 9000 Interface Installer
# Complete installation package for HAL-inspired Amazon Q CLI GUI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="$HOME/.local/share/hal9000"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    HAL 9000 INSTALLER                       ║"
echo "║              Amazon Q Interface Installation                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found."
        echo "Please install Python 3 and run this installer again."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Found Python $PYTHON_VERSION"
    
    # Check tkinter
    if ! python3 -c "import tkinter" 2>/dev/null; then
        print_error "tkinter is required but not available."
        echo "Please install python3-tk package:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  CentOS/RHEL: sudo yum install tkinter"
        echo "  macOS: tkinter should be included with Python"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        print_error "pip is required but not found."
        echo "Please install pip3 and run this installer again."
        exit 1
    fi
    
    # Check Q CLI (optional)
    if command -v q &> /dev/null; then
        Q_VERSION=$(q --version 2>/dev/null || echo "unknown")
        print_status "Found Amazon Q CLI: $Q_VERSION"
    else
        print_warning "Amazon Q CLI not found. Q CLI mode will be limited."
        print_warning "Install Q CLI for full functionality."
    fi
    
    print_status "System requirements check completed."
}

install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Check if Pillow and ImageTk are available
    if python3 -c "from PIL import Image, ImageTk" 2>/dev/null; then
        print_status "Pillow with ImageTk already installed"
    elif python3 -c "import PIL" 2>/dev/null; then
        print_warning "Pillow found but ImageTk not available"
        print_warning "Installing additional packages for full image support..."
        
        # Try to install ImageTk support
        if command -v apt-get &> /dev/null; then
            print_status "Installing python3-pil.imagetk..."
            sudo apt-get update && sudo apt-get install -y python3-pil.imagetk 2>/dev/null || {
                print_warning "Could not install python3-pil.imagetk with apt-get"
                print_warning "HAL will use animated eye fallback"
            }
        else
            print_status "Installing/upgrading Pillow..."
            if command -v pip3 &> /dev/null; then
                pip3 install --user --upgrade Pillow>=8.0.0
            else
                python3 -m pip install --user --upgrade Pillow>=8.0.0
            fi
        fi
    else
        print_status "Installing Pillow..."
        if command -v pip3 &> /dev/null; then
            pip3 install --user Pillow>=8.0.0
        else
            python3 -m pip install --user Pillow>=8.0.0
        fi
    fi
    
    print_status "Dependencies installation completed."
}

create_directories() {
    print_status "Creating installation directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/assets"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    
    print_status "Directories created."
}

download_hal_image() {
    print_status "Downloading HAL 9000 panel image..."
    
    IMAGE_URL="https://upload.wikimedia.org/wikipedia/commons/f/f6/Hal_9000_Panel.svg.png"
    IMAGE_PATH="$INSTALL_DIR/assets/Hal_9000_Panel.svg.png"
    
    if [ -f "$IMAGE_PATH" ]; then
        print_status "HAL image already exists, skipping download."
        return
    fi
    
    if command -v wget &> /dev/null; then
        wget -q -O "$IMAGE_PATH" "$IMAGE_URL"
    elif command -v curl &> /dev/null; then
        curl -s -L -o "$IMAGE_PATH" "$IMAGE_URL"
    else
        print_warning "Neither wget nor curl found. Skipping image download."
        print_warning "HAL interface will use fallback animated eye."
        return
    fi
    
    if [ -f "$IMAGE_PATH" ]; then
        print_status "HAL image downloaded successfully."
    else
        print_warning "Failed to download HAL image. Using fallback display."
    fi
}

install_files() {
    print_status "Installing HAL interface files..."
    
    # Copy main application
    cp hal_gui.py "$INSTALL_DIR/"
    
    # Copy documentation
    cp README.md "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"
    
    # Make files executable
    chmod +x "$INSTALL_DIR/hal_gui.py"
    
    print_status "Application files installed."
}

create_launcher() {
    print_status "Creating launcher script..."
    
    cat > "$BIN_DIR/hal9000" << 'EOF'
#!/bin/bash

# HAL 9000 Interface Launcher
INSTALL_DIR="$HOME/.local/share/hal9000"

if [ ! -f "$INSTALL_DIR/hal_gui.py" ]; then
    echo "Error: HAL 9000 interface not found."
    echo "Please run the installer again."
    exit 1
fi

cd "$INSTALL_DIR"
python3 hal_gui.py "$@"
EOF
    
    chmod +x "$BIN_DIR/hal9000"
    
    print_status "Launcher script created at $BIN_DIR/hal9000"
}

create_desktop_entry() {
    print_status "Creating desktop entry..."
    
    cat > "$DESKTOP_DIR/hal9000.desktop" << EOF
[Desktop Entry]
Name=HAL 9000 Interface
Comment=Amazon Q CLI GUI with HAL 9000 aesthetic
Exec=$BIN_DIR/hal9000
Icon=$INSTALL_DIR/assets/Hal_9000_Panel.svg.png
Terminal=false
Type=Application
Categories=Development;Utility;
Keywords=AWS;Amazon;Q;CLI;HAL;Terminal;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_DIR/hal9000.desktop"
    
    print_status "Desktop entry created."
}

update_path() {
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH."
        echo ""
        echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Then run: source ~/.bashrc (or restart your terminal)"
        echo ""
    fi
}

create_uninstaller() {
    print_status "Creating uninstaller..."
    
    cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash

# HAL 9000 Interface Uninstaller

echo "Uninstalling HAL 9000 Interface..."

# Remove files
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/hal9000"
rm -f "$DESKTOP_DIR/hal9000.desktop"

echo "HAL 9000 Interface has been uninstalled."
echo "Note: Python dependencies (like Pillow) were not removed."
EOF
    
    chmod +x "$INSTALL_DIR/uninstall.sh"
    
    print_status "Uninstaller created at $INSTALL_DIR/uninstall.sh"
}

main() {
    echo "Starting HAL 9000 Interface installation..."
    echo ""
    
    check_requirements
    echo ""
    
    install_dependencies
    echo ""
    
    create_directories
    download_hal_image
    install_files
    create_launcher
    create_desktop_entry
    create_uninstaller
    echo ""
    
    update_path
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 INSTALLATION COMPLETE!                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "HAL 9000 Interface has been installed successfully!"
    echo ""
    echo "To launch HAL:"
    echo "  • Command line: hal9000"
    echo "  • Desktop: Look for 'HAL 9000 Interface' in your applications"
    echo ""
    echo "Installation location: $INSTALL_DIR"
    echo "Launcher: $BIN_DIR/hal9000"
    echo ""
    echo "To uninstall: $INSTALL_DIR/uninstall.sh"
    echo ""
    echo -e "${BLUE}\"Good day. I am HAL 9000. I am ready to assist you.\"${NC}"
}

# Run main installation
main
