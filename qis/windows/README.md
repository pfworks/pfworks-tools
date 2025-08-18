# QIS v5.0 - AI Personality Interface System

A Windows-optimized AI interface with multiple computer personalities, featuring HAL 9000, Star Trek LCARS, and TRS-80 Model I themes.

## Features

### 🎭 **AI Personalities**
- **HAL 9000** - Classic sci-fi computer with red HAL panel graphics
- **Star Trek LCARS** - Federation computer with orange LCARS interface
- **TRS-80 Model I** - Retro 1977 computer with authentic boot screen

### 🖥️ **Windows Integration**
- **WSL Detection** - Automatically detects and adapts to WSL environments
- **Q CLI Integration** - Direct Amazon Q assistance with multiple access methods
- **PowerShell Mode** - Execute Windows commands or WSL Linux commands
- **Zero Terminal Flashing** - Professional Windows app appearance

### 🎨 **Visual Features**
- **Dynamic Graphics** - Personality-specific ANSI art and images
- **Theme Switching** - Green/Amber retro color schemes
- **Retro/Modern Toggle** - Authentic terminal styling with CRT effects
- **Perfect Alignment** - Clean, professional ANSI graphics

### ⚙️ **Technical Features**
- **Unified Settings Dialog** - AI Personality, Q CLI, and SSH configuration
- **Smart Exit** - Clean shutdown with conversation logging
- **Tab Completion** - Windows/WSL-aware file and command completion
- **Status Monitoring** - Real-time environment and service status

## Quick Start

### Installation
```cmd
# Install Python dependencies
install.bat

# Launch QIS (recommended - zero terminal flashing)
pythonw launch_qis.py
```

### Launch Options
- **`pythonw launch_qis.py`** - Best: Zero terminal flashing
- **`QIS.bat`** - Alternative: Minimal flashing
- **`launch_qis_debug.bat`** - Debug: Visible terminal for troubleshooting

## Requirements

- **Python 3.6+** with tkinter
- **Windows 10/11** (native or WSL)
- **Pillow** (optional, for HAL image display)
- **Amazon Q CLI** (optional, for Q mode functionality)

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
3. Choose method: AUTO, LOCAL, WSL, or SSH
4. Configure as needed
5. Use Q CLI mode for AWS assistance

### Operating Modes
- **Q CLI Mode** - Direct interaction with Amazon Q
- **PowerShell Mode** - Windows/WSL command execution
- **Modern/Retro Display** - Toggle visual styling

## File Structure

```
qis-v5/
├── qis_v5.py                 # Main application
├── launch_qis.py             # Zero-flash Python launcher
├── QIS.bat                   # Minimal batch launcher
├── launch_qis_debug.bat      # Debug launcher
├── ssh_q_service.py          # SSH Q CLI service
├── unified_settings_dialog.py # Settings interface
├── install.bat               # Dependency installer
├── requirements.txt          # Python dependencies
├── skins/                    # Personality system
│   ├── base_skin.py
│   ├── hal9000_skin.py
│   ├── star_trek_skin.py
│   ├── retro_80s_skin.py
│   └── skin_manager.py
├── assets/                   # Graphics and images
│   ├── Hal_9000_Panel.svg.png
│   ├── lcars_interface.txt
│   └── trs80_boot_screen.txt
└── README.md                 # This file
```

## Troubleshooting

### Python Not Found
1. Install Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart Windows

### Terminal Still Flashing
1. Use `pythonw launch_qis.py` (most reliable)
2. Try `QIS.bat` as alternative
3. Create desktop shortcut for best experience

### Q CLI Not Working
1. Install Amazon Q CLI
2. Configure in Settings → Q CLI Settings
3. Choose appropriate method (LOCAL/WSL/SSH)

### Graphics Not Switching
1. Use Settings → AI Personality tab
2. Click APPLY PERSONALITY after selection
3. Check debug output with `launch_qis_debug.bat`

## License

GNU General Public License v3.0

## Attribution

HAL 9000 Panel Image: By Tom Cowap - Own work, CC BY-SA 4.0

---

*"I'm sorry, Dave. I'm afraid I can't do that."*

But this QIS can help you with AI assistance and Windows operations! 🚀
