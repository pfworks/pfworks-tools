# HAL 9000 System Interface - Windows WSL Guide

This guide explains how to run HAL 9000 System Interface on Windows with WSL (Windows Subsystem for Linux) integration.

## 🚀 Quick Setup

### Prerequisites
1. **Windows 10/11** with WSL enabled
2. **Python 3.6+** installed on Windows
3. **WSL** with Ubuntu or similar Linux distribution
4. **Amazon Q CLI** installed in WSL (optional)

## 📋 Step-by-Step Installation

### 1. Enable WSL (if not already enabled)
```powershell
# Run as Administrator in PowerShell
wsl --install
# Restart your computer when prompted
```

### 2. Install Python on Windows
```powershell
# Download from python.org or use Microsoft Store
# Ensure Python is in PATH
python --version
```

### 3. Install HAL Interface on Windows
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/your-repo/hal9000-system-interface/releases/download/v2.0/hal9000-system-interface-2.0.tar.gz" -OutFile "hal9000-system-interface-2.0.tar.gz"
tar -xzf hal9000-system-interface-2.0.tar.gz
cd hal9000-system-interface-2.0

# Install Python dependencies
pip install -r requirements.txt

# Run HAL
python hal_gui.py
```

### 4. Install Q CLI in WSL (Optional)
```bash
# In WSL terminal
curl -sSL https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/amazon-q-developer-cli-install-linux.sh | bash
source ~/.bashrc
q --version
```

## 🎯 How It Works

### Automatic WSL Detection
HAL automatically detects if you're running on Windows and if WSL is available:

- **Windows + WSL Available**: Uses WSL for shell commands and Q CLI
- **Windows Only**: Uses Windows Command Prompt
- **Linux/macOS**: Uses native shell

### WSL Integration Features

#### Shell Commands
```bash
# These commands run in WSL when available:
ls -la                    # Linux commands work
pwd                       # Shows WSL path
cd /home/username         # Navigate WSL filesystem
apt update                # Package management
docker ps                 # Docker commands
```

#### Q CLI Integration
```bash
# Q CLI commands run in WSL:
q chat --message "How do I create an S3 bucket?"
q --help
```

#### Tab Completion
- **File completion** works with WSL filesystem
- **Directory navigation** uses WSL paths
- **Command completion** uses WSL bash completion

## 🖥️ Interface Indicators

### WSL Status Display
When WSL is active, you'll see:
- **System Status**: "Platform: Windows (WSL Integration Enabled)"
- **Mode Label**: "Mode: WSL (/home/username)" instead of "Mode: SHELL"
- **Input Label**: "WSL INPUT:" instead of "SHELL INPUT:"

### Visual Cues
- **Green Theme**: WSL commands in cyan
- **Amber Theme**: WSL commands in light amber
- **Status Messages**: Show WSL-specific information

## 🔧 Configuration

### Interactive Shell Setup
HAL now uses interactive login shells (`bash -l`) to ensure:
- **Profile Loading**: All `.bashrc`, `.bash_profile`, `.profile` scripts load
- **PATH Setup**: Complete PATH with all installed tools
- **SSH Agent**: Inherits SSH agent from WSL session
- **Environment**: Full environment variable inheritance

### WSL Distribution
HAL uses your default WSL distribution. To change it:
```powershell
# List available distributions
wsl --list

# Set default distribution
wsl --set-default Ubuntu-20.04
```

### SSH Agent Setup
To inherit SSH agent in HAL:
```bash
# In WSL, add to ~/.bashrc:
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval $(ssh-agent -s)
    ssh-add ~/.ssh/id_rsa  # Add your SSH keys
fi

# Or use keychain for persistent agent:
sudo apt install keychain
echo 'eval $(keychain --eval --agents ssh id_rsa)' >> ~/.bashrc
```

### Q CLI Installation
```bash
# In WSL terminal:
curl -sSL https://d2eo22ngex1n9g.cloudfront.net/Documentation/SDK/amazon-q-developer-cli-install-linux.sh | bash
source ~/.bashrc
q --version
```

### Test WSL Integration
```bash
# Run the WSL integration test
python test_wsl.py

# This will test:
# - WSL availability
# - Interactive shell functionality
# - Q CLI installation
# - SSH agent inheritance
# - File operations
# - Tab completion
```

## 🐛 Troubleshooting

### Environment Issues
**Problem**: Commands work in WSL terminal but not in HAL

**Solutions**:
1. Check if HAL uses interactive shell: Look for "WSL Environment Test" in startup
2. Verify profile loading: `wsl -- bash -l -c 'echo $PATH'`
3. Compare environments:
   ```bash
   # In WSL terminal:
   echo $PATH > /tmp/wsl_path.txt
   
   # In HAL shell mode:
   echo $PATH > /tmp/hal_path.txt
   
   # Compare:
   diff /tmp/wsl_path.txt /tmp/hal_path.txt
   ```

### SSH Agent Issues
**Problem**: SSH keys not available in HAL

**Solutions**:
1. Set up persistent SSH agent in `~/.bashrc`:
   ```bash
   # Add to ~/.bashrc
   if [ -z "$SSH_AUTH_SOCK" ]; then
       eval $(ssh-agent -s)
       ssh-add ~/.ssh/id_rsa
   fi
   ```
2. Use keychain for better management:
   ```bash
   sudo apt install keychain
   echo 'eval $(keychain --eval --agents ssh id_rsa)' >> ~/.bashrc
   ```
3. Test SSH agent: `ssh-add -l` in HAL shell mode

### WSL Not Detected
**Problem**: HAL shows "Platform: Windows" without WSL integration

**Solutions**:
1. Ensure WSL is installed: `wsl --status`
2. Check WSL is running: `wsl --list --running`
3. Restart WSL: `wsl --shutdown` then `wsl`

### Q CLI Not Found in WSL
**Problem**: "Q CLI not found in WSL" error

**Solutions**:
1. Install Q CLI in WSL (see step 4 above)
2. Verify installation: `wsl -- q --version`
3. Check PATH in WSL: `wsl -- echo $PATH`

### File Completion Issues
**Problem**: Tab completion doesn't work or shows wrong files

**Solutions**:
1. Ensure you're in SHELL/WSL mode
2. Check current directory: `pwd`
3. Verify WSL filesystem access

### Performance Issues
**Problem**: Commands are slow in WSL mode

**Solutions**:
1. Use WSL 2 instead of WSL 1: `wsl --set-version Ubuntu 2`
2. Store files in WSL filesystem (`/home/`) not Windows (`/mnt/c/`)
3. Update WSL: `wsl --update`

## 🎨 Best Practices

### File Organization
```bash
# Store projects in WSL filesystem for better performance
/home/username/projects/

# Access Windows files when needed
/mnt/c/Users/YourName/Documents/
```

### Command Usage
```bash
# Use Linux commands in WSL mode
ls, grep, awk, sed, find

# Access Windows tools when needed
/mnt/c/Windows/System32/notepad.exe

# Mix Windows and Linux tools
ls | /mnt/c/Windows/System32/findstr.exe "pattern"
```

### Development Workflow
1. **Code**: Use Windows editors (VS Code, etc.)
2. **Execute**: Use WSL for running/testing
3. **Deploy**: Use WSL for AWS CLI, Docker, etc.

## 🚀 Advanced Features

### Cross-Platform Paths
HAL handles path conversion automatically:
```bash
# These all work correctly:
cd /home/username
cd /mnt/c/Users/YourName
ls /mnt/c/Program\ Files/
```

### Environment Variables
Access both Windows and WSL environment variables:
```bash
echo $HOME                    # WSL home
echo $PATH                    # WSL PATH
/mnt/c/Windows/System32/cmd.exe /c echo %USERPROFILE%  # Windows
```

### Network Integration
WSL shares network with Windows:
```bash
# Access Windows services from WSL
curl localhost:8080

# Access WSL services from Windows
# Use localhost from Windows browser
```

## 📊 Performance Comparison

| Operation | Native Windows | WSL Integration | Native Linux |
|-----------|---------------|-----------------|--------------|
| File I/O | Fast | Medium | Fast |
| Command Execution | Medium | Fast | Fast |
| Tab Completion | Basic | Advanced | Advanced |
| Q CLI Performance | Medium | Fast | Fast |
| Cross-platform | Limited | Excellent | N/A |

## 🎯 Use Cases

### Perfect For:
- **AWS Development**: Q CLI + Linux tools
- **DevOps**: Docker, Kubernetes, scripts
- **System Administration**: Linux commands on Windows
- **Cross-platform Development**: Best of both worlds

### Consider Alternatives For:
- **Windows-specific Tasks**: Use native Windows mode
- **Heavy File I/O**: Consider native Linux
- **Simple Tasks**: Native Windows might be sufficient

## 🔗 Related Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Amazon Q CLI Documentation](https://docs.aws.amazon.com/amazonq/)
- [HAL System Interface README](README.md)
- [Shell Mode Guide](SHELL_MODE_GUIDE.md)

---

**Ready to experience the power of HAL with WSL integration!** 🚀

*"I'm sorry, Dave. I'm afraid I can't do that."*
*But this HAL can bridge Windows and Linux seamlessly!* 🤖
