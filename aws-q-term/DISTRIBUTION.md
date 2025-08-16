# HAL 9000 Interface - Distribution Guide

This document explains how to create and distribute the HAL 9000 Interface package.

## Creating a Distribution Package

### Quick Package Creation

```bash
# Create complete distribution package
make package

# Or run directly
./package.sh
```

This creates a `hal9000-interface-2.0.tar.gz` file containing:
- Complete HAL application
- Automated installer
- HAL 9000 panel image
- Documentation
- All dependencies information

### Manual Package Creation

```bash
# 1. Ensure all files are present
ls -la hal_gui.py install.sh launch_hal.sh README.md requirements.txt

# 2. Create package
./package.sh

# 3. Verify package contents
tar -tzf hal9000-interface-*.tar.gz
```

## Distribution Package Contents

```
hal9000-interface-2.0/
├── hal_gui.py              # Main GUI application
├── install.sh              # Automated installer
├── launch_hal.sh           # Direct launcher
├── requirements.txt        # Python dependencies
├── README.md               # Complete documentation
├── PACKAGE_INFO            # Package information
├── QUICKSTART.md           # Quick start guide
└── assets/
    └── Hal_9000_Panel.svg.png  # HAL image (CC BY-SA 4.0)
```

## Installation Methods for End Users

### Method 1: Automated Installation (Recommended)

```bash
# Extract package
tar -xzf hal9000-interface-2.0.tar.gz
cd hal9000-interface-2.0

# Run installer
./install.sh

# Launch HAL
hal9000
```

### Method 2: Manual Installation

```bash
# Extract package
tar -xzf hal9000-interface-2.0.tar.gz
cd hal9000-interface-2.0

# Install dependencies
pip install -r requirements.txt

# Launch directly
./launch_hal.sh
```

## Installer Features

The automated installer (`install.sh`) provides:

- **System Requirements Check**: Verifies Python 3, tkinter, pip
- **Dependency Installation**: Automatically installs Pillow
- **Image Download**: Downloads HAL image if not included
- **System Integration**: Creates launcher and desktop entry
- **PATH Management**: Guides users on PATH setup
- **Uninstaller**: Creates uninstall script

### Installation Locations

- **Application**: `~/.local/share/hal9000/`
- **Launcher**: `~/.local/bin/hal9000`
- **Desktop Entry**: `~/.local/share/applications/hal9000.desktop`
- **Uninstaller**: `~/.local/share/hal9000/uninstall.sh`

## Distribution Checklist

Before creating a distribution package:

- [ ] Test HAL interface functionality
- [ ] Verify Q CLI integration works
- [ ] Test shell mode commands
- [ ] Confirm image attribution is correct
- [ ] Test installer on clean system
- [ ] Verify all documentation is up to date
- [ ] Test package extraction and installation

## Platform Compatibility

### Tested Platforms
- Ubuntu 20.04+ (Linux)
- Debian 10+ (Linux)
- CentOS 8+ (Linux)
- macOS 10.15+ (with Python 3)

### Requirements
- Python 3.6 or higher
- tkinter (usually included with Python)
- pip for dependency installation
- wget or curl for image download

### Optional
- Amazon Q CLI (for Q mode functionality)
- Desktop environment (for desktop entry)

## Customization for Distribution

### Branding
Edit these files to customize:
- `hal_gui.py`: Window title, about dialog
- `install.sh`: Installation messages
- `README.md`: Documentation

### Default Settings
Modify in `hal_gui.py`:
- Window size: `self.root.geometry("1400x900")`
- Colors: `setup_styles()` method
- Fonts: Font specifications throughout

### Installation Paths
Modify in `install.sh`:
- `INSTALL_DIR`: Application installation directory
- `BIN_DIR`: Launcher script location
- `DESKTOP_DIR`: Desktop entry location

## Troubleshooting Distribution Issues

### Common Package Issues

1. **Missing HAL Image**
   - Ensure internet connection during packaging
   - Manually place image in `assets/` before packaging

2. **Permission Issues**
   - Ensure all scripts are executable: `chmod +x *.sh`
   - Check file permissions in package

3. **Dependency Issues**
   - Test on clean system without Pillow installed
   - Verify pip installation works

### Testing the Package

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Test installation
tar -xzf hal9000-interface-*.tar.gz
cd hal9000-interface-*
./install.sh

# Test functionality
hal9000
```

## License and Attribution

### Package License
This package is provided as-is for educational and practical use with Amazon Q CLI.

### HAL Image Attribution
The HAL 9000 panel image is used under CC BY-SA 4.0 license:
- **Author**: Tom Cowap
- **License**: CC BY-SA 4.0
- **Source**: https://commons.wikimedia.org/w/index.php?curid=103068276

This attribution is included in:
- About dialog in the application
- README.md documentation
- PACKAGE_INFO file

## Support and Updates

### Version Management
Update version in:
- `package.sh`: `VERSION="2.0"`
- About dialog in `hal_gui.py`
- Documentation files

### Creating Updates
1. Update version numbers
2. Update changelog in README.md
3. Test thoroughly
4. Create new package
5. Update distribution checksums

---

*"I'm sorry, Dave. I'm afraid I can't do that."*
*But this HAL can help you distribute AWS interfaces!* 🚀
