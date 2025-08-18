# QIS v5.0 Launch Options - ZERO FLASH SOLUTIONS

## The Terminal Flashing Problem
Windows shows brief terminal windows when launching Python GUI apps. Here are multiple solutions ranked by effectiveness:

## Launch Options (Best to Worst for Zero Flashing)

### 🏆 **launch_qis.py** (Python Launcher - BEST)
- **True zero flashing** - Uses Python subprocess with hidden window flags
- **Most reliable** - Works on all Windows configurations
- **How to use**: `pythonw launch_qis.py` or double-click in some cases
- **Technical**: Uses `subprocess.CREATE_NO_WINDOW` flag

### 🥇 **QIS.bat** (Ultimate Minimal)
- **Single line**: `@start /min /b pythonw qis_v5.py`
- **Minimal flashing** - Uses Windows `start` command with hidden flags
- **How to use**: Double-click `QIS.bat`
- **Technical**: `/min` minimizes, `/b` runs in background

### 🥈 **launch_qis.ps1** (PowerShell Hidden)
- **PowerShell with hidden window** - Hides console immediately
- **Good for PowerShell users** - Uses native Windows PowerShell
- **How to use**: Right-click → "Run with PowerShell" or use batch wrapper
- **Technical**: Uses `WindowStyle Hidden` and console hiding APIs

### 🥉 **launch_qis.bat** (PowerShell Wrapper)
- **Calls PowerShell script** - `powershell -WindowStyle Hidden`
- **Moderate flashing** - Brief PowerShell window may appear
- **How to use**: Double-click `launch_qis.bat`
- **Technical**: Batch → PowerShell → Python chain

### 🔧 **launch_qis_debug.bat** (Debug Only)
- **Visible terminal** - For troubleshooting only
- **Shows all output** - Debug messages, errors, etc.
- **How to use**: Double-click when you need to see what's happening

## Recommended Usage by Scenario

### For Zero Flashing (Try in Order):

#### Method 1: Python Launcher (Most Reliable)
```cmd
# In command prompt or PowerShell:
pythonw launch_qis.py

# Or create a shortcut with target:
# pythonw "C:\path\to\qis\launch_qis.py"
```

#### Method 2: Ultimate Minimal Batch
```cmd
# Double-click QIS.bat
# Contains: @start /min /b pythonw qis_v5.py
```

#### Method 3: PowerShell Direct
```cmd
# Right-click launch_qis.ps1 → "Run with PowerShell"
# Or in PowerShell: .\launch_qis.ps1
```

### For Debugging:
```cmd
# Double-click launch_qis_debug.bat
# Shows all terminal output
```

## Creating Desktop Shortcuts (Zero Flash)

### Best Method - Python Launcher Shortcut:
1. Right-click on Desktop → New → Shortcut
2. Target: `pythonw "C:\path\to\your\qis\launch_qis.py"`
3. Name: "QIS v5.0"
4. Click Finish
5. **Result**: Zero flashing desktop launch

### Alternative - Batch File Shortcut:
1. Right-click `QIS.bat` → Create Shortcut
2. Move shortcut to Desktop
3. Rename to "QIS v5.0"
4. **Result**: Minimal flashing desktop launch

## Technical Explanation

### Why Flashing Happens:
- **Windows console subsystem** - Python GUI apps briefly create console windows
- **Batch file execution** - `.bat` files always create command windows
- **Process creation** - Windows shows windows during process startup

### How Each Solution Works:

| Method | Technique | Flashing Level |
|--------|-----------|----------------|
| `launch_qis.py` | `subprocess.CREATE_NO_WINDOW` | None |
| `QIS.bat` | `start /min /b` flags | Minimal |
| `launch_qis.ps1` | PowerShell hidden + API calls | Very Low |
| `launch_qis.bat` | PowerShell wrapper | Low |

## Requirements
- **Python 3.6+** installed and in PATH
- **tkinter** (usually included with Python)
- **Pillow** (optional, for HAL image display)
- **PowerShell** (built into Windows 7+)

## Troubleshooting

### Python Launcher Won't Work
```cmd
# Try running directly:
python launch_qis.py

# Check if pythonw is available:
pythonw --version
```

### PowerShell Execution Policy Error
```cmd
# Run once as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use bypass flag:
powershell -ExecutionPolicy Bypass -File launch_qis.ps1
```

### Still Seeing Flashing
1. **Try Python launcher first** - Most reliable
2. **Use desktop shortcut** - Often eliminates flashing
3. **Check Windows version** - Older Windows may always flash briefly
4. **Use debug mode** - If nothing works, use `launch_qis_debug.bat`

## Summary

**For the absolute best experience:**
1. **Use `pythonw launch_qis.py`** - Most reliable zero flash
2. **Create desktop shortcut** - For easy access
3. **Fall back to `QIS.bat`** - If Python launcher doesn't work
4. **Use debug mode** - Only when troubleshooting

**QIS v5.0 now has multiple zero-flash solutions - one of them will work perfectly on your system!**
