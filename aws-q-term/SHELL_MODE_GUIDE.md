# HAL 9000 Shell Mode Guide

## How to Use Shell Mode

### 1. **Switching to Shell Mode**
- Click the **SHELL** button in the top-right area of the HAL interface
- The input field will change from green to cyan on dark green background
- The mode indicator will show "Mode: SHELL (/current/directory)"

### 2. **Visual Indicators**
- **Q CLI Mode**: Green text input, "Q INPUT:" label
- **Shell Mode**: Cyan text input on dark background, "SHELL INPUT:" label
- **Mode Buttons**: Active mode button is highlighted in white text

### 3. **Shell Commands**
You can run any bash command in shell mode:

```bash
# Basic commands
ls -la                    # List files
pwd                       # Show current directory
whoami                    # Show current user
ps aux                    # Show running processes

# File operations
cat filename.txt          # Display file contents
mkdir new_directory       # Create directory
touch newfile.txt         # Create empty file
cp source dest            # Copy files

# System information
df -h                     # Disk usage
free -h                   # Memory usage
uname -a                  # System information

# Network commands
ping google.com           # Test connectivity
curl -I https://aws.com   # Check website headers
```

### 4. **Directory Navigation**
- Use `cd` commands to change directories
- HAL tracks your current directory
- The mode label shows your current path: "Mode: SHELL (/home/user)"

```bash
cd /home/user/Documents   # Change to Documents
cd ..                     # Go up one directory
cd ~                      # Go to home directory
cd                        # Also goes to home directory
```

### 5. **Output Display**
- **Command**: Shows in cyan text with full path prompt
- **Output**: Normal command output in white text
- **Errors**: Error messages in pink/red text
- **System**: Directory changes and notifications in yellow

### 6. **Example Shell Session**

```
SHELL: /home/user$ ls -la
OUTPUT: total 24
drwxr-xr-x 3 user user 4096 Aug 16 10:30 .
drwxr-xr-x 5 user user 4096 Aug 16 10:25 ..
-rw-r--r-- 1 user user  220 Aug 16 10:25 .bashrc

SHELL: /home/user$ cd Documents
SYSTEM: Changed directory to: /home/user/Documents

SHELL: /home/user/Documents$ pwd
OUTPUT: /home/user/Documents

SHELL: /home/user/Documents$ echo "Hello HAL"
OUTPUT: Hello HAL
```

### 7. **Switching Back to Q CLI Mode**
- Click the **Q CLI** button to return to Amazon Q mode
- Input field changes back to green
- Mode indicator shows "Mode: Q CLI"

### 8. **Tips for Shell Mode**
- **Long-running commands**: Have a 30-second timeout
- **Interactive commands**: Won't work (like `nano`, `vim`)
- **Pipes and redirects**: Work normally (`ls | grep txt`)
- **Environment**: Each command runs in the tracked directory
- **History**: All commands are logged with timestamps

### 9. **Troubleshooting Shell Mode**
- If commands don't work, check you're in SHELL mode (cyan input)
- Some commands require specific permissions
- Interactive programs won't display properly
- Use `Ctrl+C` equivalent: commands timeout after 30 seconds

### 10. **Combining Q CLI and Shell**
You can switch between modes freely:
1. Use **Q CLI mode** to ask "How do I check disk usage?"
2. Switch to **SHELL mode** and run `df -h`
3. Switch back to **Q CLI mode** to ask follow-up questions

This gives you the best of both worlds - AWS expertise from Q CLI and direct system access through shell commands!
