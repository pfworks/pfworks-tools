#!/usr/bin/env python3
"""
QIS v5.0 - Zero Flash Launcher
This Python script launches QIS with absolutely no terminal visibility
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_python_gui():
    """Check if we can create GUI windows"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the test window
        root.destroy()
        return True
    except:
        return False

def launch_qis_hidden():
    """Launch QIS with completely hidden terminal"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        qis_path = os.path.join(script_dir, 'qis_v5.py')
        
        # Check if QIS file exists
        if not os.path.exists(qis_path):
            messagebox.showerror("QIS v5.0 - File Not Found", 
                               f"Could not find qis_v5.py in:\n{script_dir}\n\n"
                               "Please make sure you're running this from the QIS directory.")
            return False
        
        # Launch QIS with completely hidden window
        if sys.platform.startswith('win'):
            # Windows: Use subprocess with hidden window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen([sys.executable, qis_path], 
                           startupinfo=startupinfo,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Non-Windows: Standard hidden launch
            subprocess.Popen([sys.executable, qis_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        return True
        
    except Exception as e:
        messagebox.showerror("QIS v5.0 - Launch Error", 
                           f"Failed to launch QIS:\n\n{str(e)}")
        return False

def main():
    """Main launcher function"""
    # Check if GUI is available
    if not check_python_gui():
        print("Error: GUI support not available. Please install tkinter.")
        sys.exit(1)
    
    # Create hidden root window for message boxes
    root = tk.Tk()
    root.withdraw()  # Hide the launcher window
    
    try:
        # Launch QIS
        if launch_qis_hidden():
            # Success - exit silently
            pass
        else:
            # Error already shown in messagebox
            pass
    except Exception as e:
        messagebox.showerror("QIS v5.0 - Unexpected Error", 
                           f"Unexpected error:\n\n{str(e)}")
    finally:
        # Clean exit
        root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    main()
