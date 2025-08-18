# QIS v5.0 Changelog

## v5.0.0 - 2025-08-18

### 🎭 New Features
- **AI Personality System** - Switch between HAL 9000, Star Trek LCARS, and TRS-80 Model I
- **Dynamic Graphics** - Personality-specific ANSI art and images that change with themes
- **Unified Settings Dialog** - Single interface for all configuration options
- **Zero Terminal Flashing** - Professional Windows app appearance with multiple launch methods

### 🎨 Visual Enhancements
- **Authentic ANSI Graphics** - TRS-80 boot screen, LCARS interface panels
- **Perfect Alignment** - Fixed whitespace issues in ASCII art
- **Color-Matched Themes** - Graphics use personality-appropriate colors
- **Retro/Modern Toggle** - CRT effects and authentic terminal styling

### ⚙️ Technical Improvements
- **Working Skin System** - Complete personality switching with graphics
- **Enhanced Q CLI Integration** - Multiple access methods (LOCAL/WSL/SSH)
- **Clean Exit Handling** - Proper terminal closure and conversation saving
- **WSL Detection** - Automatic Windows Subsystem for Linux support

### 🚀 Launch Options
- **Python Launcher** - `pythonw launch_qis.py` for zero terminal flashing
- **Minimal Batch** - `QIS.bat` for quick access
- **Debug Mode** - `launch_qis_debug.bat` for troubleshooting

### 🔧 Bug Fixes
- Fixed graphics not switching between personalities
- Resolved terminal window flashing issues
- Corrected ANSI art alignment problems
- Improved settings dialog functionality
- Enhanced error handling and cleanup

### 📦 Package Structure
- Streamlined file organization
- Removed intermediate development files
- Clean GitHub-ready release structure
- Essential files only for distribution

### 🎯 Compatibility
- Windows 10/11 native and WSL
- Python 3.6+ with tkinter
- Optional Pillow for enhanced graphics
- Amazon Q CLI integration (optional)

---

## Previous Versions

### v4.0 and earlier
- Basic HAL 9000 interface
- Windows-specific optimizations
- Q CLI integration foundation
- Initial skin system development
