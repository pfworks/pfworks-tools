# QIS v6.0 Changelog

## v6.0.0 - 2025-08-18

### 🌍 Cross-Platform Support (NEW!)
- **Universal Compatibility** - Now supports Windows, Linux, and macOS
- **Platform Auto-Detection** - Automatically adapts to the host operating system
- **Native Shell Integration** - PowerShell (Windows), Bash (Linux/macOS/WSL)
- **Cross-Platform Q CLI** - Local Q binary support on all platforms

### 🚀 Enhanced Launch System
- **Universal Launcher** - `launch_qis` script detects platform automatically
- **Platform-Specific Launchers** - Optimized for each operating system
- **Shell Script Support** - `launch_qis.sh` for Linux/macOS systems
- **Zero Terminal Flashing** - Professional app appearance across all platforms

### 🔧 Technical Improvements
- **CrossPlatformEnvironmentDetector** - Unified environment detection
- **CrossPlatformQService** - Simplified Q CLI integration (LOCAL/SSH only)
- **Dynamic Shell Detection** - Automatically uses appropriate shell per platform
- **Simplified Q Methods** - Removed Windows-specific WSL handling for cleaner code

### 🎯 Platform-Specific Features
- **Windows**: Full PowerShell integration with WSL detection
- **Linux**: Native bash integration with Q CLI support
- **macOS**: Native shell integration with Q CLI support
- **WSL**: Automatic detection and Linux-style command handling

### 📦 Updated Package Structure
- **Cross-platform launchers** - Multiple launch options for each platform
- **Universal requirements** - Single requirements.txt for all platforms
- **Platform documentation** - Clear instructions for each operating system

### 🔄 Migration from v5.0
- **Backward Compatible** - All v5.0 features preserved
- **Enhanced Functionality** - Additional platform support
- **Simplified Configuration** - Streamlined Q CLI setup

---

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
