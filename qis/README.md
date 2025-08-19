# QIS v6.0 - Cross-Platform AI Personality Interface System

A universal AI interface with multiple computer personalities, featuring HAL 9000, Star Trek LCARS, and TRS-80 Model I themes. Now supports Windows, Linux, and macOS!

## Features

### 🎭 **AI Personalities**
- **HAL 9000** - Classic sci-fi computer with red HAL panel graphics
- **Star Trek LCARS** - Federation computer with orange LCARS interface
- **TRS-80 Model I** - Retro 1977 computer with authentic boot screen

### 🌍 **Cross-Platform Support**
- **Windows** - Full PowerShell integration with WSL detection
- **Linux** - Native bash/shell integration with Q CLI support
- **macOS** - Native shell integration with Q CLI support
- **Universal Launcher** - Automatically detects platform and adapts

### 🖥️ **Platform Integration**
- **Q CLI Integration** - Local Q binary support across all platforms
- **SSH Remote Q CLI** - Access Q CLI on remote Linux servers
- **Native Shell Mode** - PowerShell (Windows), Bash (Linux/macOS/WSL)
- **Zero Terminal Flashing** - Professional app appearance on all platforms

### 🎨 **Visual Features**
- **Dynamic Graphics** - Personality-specific ANSI art and images
- **Theme Switching** - Green/Amber retro color schemes
- **Retro/Modern Toggle** - Authentic terminal styling with CRT effects
- **Perfect Cross-Platform Alignment** - Clean graphics on all systems

### ⚙️ **Technical Features**
- **Unified Settings Dialog** - AI Personality, Q CLI, and SSH configuration
- **Smart Exit** - Clean shutdown with conversation logging
- **Tab Completion** - Platform-aware file and command completion
- **Status Monitoring** - Real-time environment and service status

## Quick Start

### Universal Installation (All Platforms)
```bash
# Install Python dependencies
python3 -m pip install -r requirements.txt

# Universal launcher (detects platform automatically)
python3 launch_qis

# Or use platform-specific launchers below
```

### Platform-Specific Launch Options

#### Windows
```cmd
# Best: Zero terminal flashing
pythonw launch_qis.py

# Alternative: Minimal flashing
QIS.bat

# Debug: Visible terminal
launch_qis_debug.bat
```

#### Linux/macOS
```bash
# Best: Python launcher
python3 launch_qis.py

# Alternative: Shell script
./launch_qis.sh

# Debug: Direct execution
python3 qis_v6.py
```

## Requirements

### All Platforms
- **Python 3.6+** with tkinter
- **Pillow** (optional, for HAL image display)
- **Q CLI binary** (optional, for Q mode functionality)

### Platform-Specific
- **Windows**: PowerShell (built-in)
- **Linux**: bash or preferred shell
- **macOS**: bash/zsh or preferred shell

## Usage

### Personality Switching
1. Click **SETTINGS** button
2. Select **AI Personality** tab
3. Choose personality (HAL 9000, Star Trek LCARS, or TRS-80)
4. Click **APPLY PERSONALITY**
5. Watch interface transform with new colors and graphics

### Q CLI Integration
1. Click **SETTINGS** button
2. Select **Q CLI Settings** tab
3. Choose method: AUTO, LOCAL, or SSH
4. Configure as needed
5. Use Q CLI mode for AWS assistance

### Operating Modes
- **Q CLI Mode** - Direct interaction with Amazon Q
- **Shell Mode** - Native shell command execution (PowerShell/Bash)
- **Modern/Retro Display** - Toggle visual styling

## Cross-Platform Differences

### Windows
- **Shell Mode**: PowerShell commands
- **Q CLI**: Windows Q CLI binary or WSL Q CLI
- **Paths**: Windows-style paths with backslashes

### Linux/macOS
- **Shell Mode**: Bash/shell commands
- **Q CLI**: Local Q binary installation
- **Paths**: Unix-style paths with forward slashes

### WSL (Windows Subsystem for Linux)
- **Detected automatically** - Adapts to Linux-style commands
- **Shell Mode**: Bash commands within WSL
- **Q CLI**: Can use either Windows or Linux Q CLI

## File Structure

```
qis-v6/
├── qis_v6.py                 # Main cross-platform application
├── launch_qis.py             # Cross-platform Python launcher
├── launch_qis                # Universal launcher script
├── launch_qis.sh             # Linux/macOS shell launcher
├── QIS.bat                   # Windows batch launcher
├── launch_qis_debug.bat      # Windows debug launcher
├── ssh_q_service.py          # SSH Q CLI service
├── unified_settings_dialog.py # Settings interface
├── requirements.txt          # Python dependencies
├── skins/                    # Personality system
│   ├── base_skin.py          # HAL 9000 skin
│   ├── star_trek_skin.py     # LCARS skin
│   ├── retro_80s_skin.py     # TRS-80 skin
│   └── skin_manager.py       # Skin switching system
├── assets/                   # Graphics and images
│   ├── Hal_9000_Panel.svg.png
│   ├── lcars_interface.txt
│   └── trs80_boot_screen.txt
└── README.md                 # This file
```

## Troubleshooting

### Python Not Found
- **Windows**: Install from python.org, check "Add to PATH"
- **Linux**: `sudo apt install python3 python3-tk` (Ubuntu/Debian)
- **macOS**: Install from python.org or use Homebrew

### Q CLI Not Working
1. Install Q CLI binary for your platform
2. Ensure it's in your system PATH
3. Configure in Settings → Q CLI Settings
4. Choose LOCAL method for local binary

### Shell Commands Not Working
- **Windows**: Ensure PowerShell is available
- **Linux/macOS**: Ensure bash or preferred shell is available
- **WSL**: QIS automatically detects and adapts

### Graphics Not Switching
1. Use Settings → AI Personality tab
2. Click APPLY PERSONALITY after selection
3. Check debug output if needed

## Platform Installation Notes

### Windows
- Works on Windows 10/11
- Supports both native Windows and WSL environments
- PowerShell integration for command execution

### Linux
- Tested on Ubuntu, Debian, CentOS, Fedora
- Requires X11 or Wayland for GUI
- Native bash integration

### macOS
- Requires macOS 10.12 or later
- Works with both Intel and Apple Silicon
- Native Terminal.app integration

## License

GNU General Public License v3.0

## Attribution

HAL 9000 Panel Image: By Tom Cowap - Own work, CC BY-SA 4.0

---

*"I'm sorry, Dave. I'm afraid I can't do that."*

But this QIS can help you with AI assistance across Windows, Linux, and macOS! 🚀
