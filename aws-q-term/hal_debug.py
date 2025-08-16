#!/usr/bin/env python3
"""
HAL Debug Version - Simple test to verify buttons and layout
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
from datetime import datetime

class HALDebug:
    def __init__(self, root):
        self.root = root
        self.root.title("HAL 9000 - DEBUG VERSION")
        self.root.geometry("1200x800")
        self.root.configure(bg='#000000')
        
        self.current_mode = "Q"
        self.shell_cwd = os.path.expanduser("~")
        
        self.setup_ui()
        
        # Add debug message
        self.add_debug_message("HAL Debug Version Loaded")
        self.add_debug_message("Looking for Q CLI and SHELL buttons in top-right area")
        self.add_debug_message("Current mode: Q CLI")
    
    def setup_ui(self):
        """Create the main interface components"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with buttons
        self.create_header(main_frame)
        
        # Debug display area
        self.create_debug_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
    
    def create_header(self, parent):
        """Create the HAL header with mode controls"""
        header_frame = tk.Frame(parent, bg='#000000')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - HAL eye
        left_frame = tk.Frame(header_frame, bg='#000000')
        left_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Simple red circle
        eye_canvas = tk.Canvas(left_frame, width=80, height=80, 
                              bg='#000000', highlightthickness=0)
        eye_canvas.pack()
        
        # Draw simple red eye
        eye_canvas.create_oval(10, 10, 70, 70, 
                              outline='#FF0000', width=3, fill='#FF0000')
        eye_canvas.create_oval(35, 35, 45, 45, 
                              outline='#FFFFFF', width=1, fill='#FFFFFF')
        
        # Center - Title
        center_frame = tk.Frame(header_frame, bg='#000000')
        center_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(center_frame, 
                              text="HAL 9000 - System Interface (DEBUG)",
                              bg='#000000', fg='#FF0000',
                              font=('Courier New', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        self.mode_label = tk.Label(center_frame,
                                  text="Mode: Q CLI",
                                  bg='#000000', fg='#FF0000',
                                  font=('Courier New', 10))
        self.mode_label.pack(anchor=tk.W)
        
        # Right side - Control buttons (THIS IS THE IMPORTANT PART)
        button_frame = tk.Frame(header_frame, bg='#000000')
        button_frame.pack(side=tk.RIGHT)
        
        # Mode selection buttons
        mode_frame = tk.Frame(button_frame, bg='#000000')
        mode_frame.pack(pady=(0, 5))
        
        # Q CLI Button
        self.q_mode_btn = tk.Button(mode_frame, text="Q CLI", 
                                   command=lambda: self.set_mode("Q"),
                                   bg='#550000', fg='#FFFFFF',
                                   font=('Courier New', 10, 'bold'),
                                   width=8)
        self.q_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # SHELL Button
        self.shell_mode_btn = tk.Button(mode_frame, text="SHELL", 
                                       command=lambda: self.set_mode("SHELL"),
                                       bg='#330000', fg='#FF0000',
                                       font=('Courier New', 10, 'bold'),
                                       width=8)
        self.shell_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Action buttons
        action_frame = tk.Frame(button_frame, bg='#000000')
        action_frame.pack()
        
        tk.Button(action_frame, text="CLEAR", 
                 command=self.clear_debug,
                 bg='#330000', fg='#FF0000',
                 font=('Courier New', 10, 'bold'),
                 width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="TEST", 
                 command=self.run_test,
                 bg='#330000', fg='#FF0000',
                 font=('Courier New', 10, 'bold'),
                 width=8).pack(side=tk.LEFT, padx=2)
    
    def create_debug_area(self, parent):
        """Create the debug display area"""
        debug_frame = tk.Frame(parent, bg='#000000')
        debug_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Debug display
        self.debug_display = scrolledtext.ScrolledText(
            debug_frame,
            bg='#000000',
            fg='#00FF00',
            font=('Courier New', 11),
            insertbackground='#00FF00',
            selectbackground='#003300',
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.debug_display.pack(fill=tk.BOTH, expand=True)
    
    def create_input_area(self, parent):
        """Create the user input area"""
        input_frame = tk.Frame(parent, bg='#000000')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input label
        self.input_label = tk.Label(input_frame, text="Q INPUT:", 
                                   bg='#000000', fg='#FF0000',
                                   font=('Courier New', 12, 'bold'))
        self.input_label.pack(anchor=tk.W)
        
        # Input field
        entry_frame = tk.Frame(input_frame, bg='#000000')
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.input_entry = tk.Entry(
            entry_frame,
            bg='#000000',
            fg='#00FF00',
            font=('Courier New', 12),
            insertbackground='#00FF00',
            selectbackground='#003300'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.process_input)
        
        tk.Button(entry_frame, text="SEND", 
                 command=self.process_input,
                 bg='#330000', fg='#FF0000',
                 font=('Courier New', 10, 'bold')).pack(side=tk.RIGHT)
        
        self.input_entry.focus()
    
    def set_mode(self, mode):
        """Switch between Q CLI and Shell modes"""
        self.current_mode = mode
        
        if mode == "Q":
            self.mode_label.config(text="Mode: Q CLI")
            self.q_mode_btn.config(bg='#550000', fg='#FFFFFF')
            self.shell_mode_btn.config(bg='#330000', fg='#FF0000')
            self.input_entry.config(bg='#000000', fg='#00FF00')
            self.input_label.config(text="Q INPUT:")
            self.add_debug_message("✓ Switched to Q CLI mode")
        else:  # SHELL
            self.mode_label.config(text=f"Mode: SHELL ({self.shell_cwd})")
            self.shell_mode_btn.config(bg='#550000', fg='#FFFFFF')
            self.q_mode_btn.config(bg='#330000', fg='#FF0000')
            self.input_entry.config(bg='#001100', fg='#00FFFF')
            self.input_label.config(text="SHELL INPUT:")
            self.add_debug_message("✓ Switched to SHELL mode")
            self.add_debug_message("  Input field should now be CYAN on dark green")
            self.add_debug_message("  Try typing: ls -la")
    
    def process_input(self, event=None):
        """Process user input"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.input_entry.delete(0, tk.END)
        
        if self.current_mode == "Q":
            self.add_debug_message(f"Q CLI INPUT: {message}")
            self.add_debug_message("  (Would send to Amazon Q CLI)")
        else:
            self.add_debug_message(f"SHELL COMMAND: {message}")
            self.add_debug_message("  (Would execute as shell command)")
            
            # Actually try to run simple commands for testing
            if message in ['pwd', 'whoami', 'date']:
                try:
                    import subprocess
                    result = subprocess.run(message, shell=True, capture_output=True, text=True, timeout=5)
                    if result.stdout:
                        self.add_debug_message(f"OUTPUT: {result.stdout.strip()}")
                    if result.stderr:
                        self.add_debug_message(f"ERROR: {result.stderr.strip()}")
                except Exception as e:
                    self.add_debug_message(f"ERROR: {str(e)}")
    
    def add_debug_message(self, message):
        """Add a debug message"""
        self.debug_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.debug_display.config(state=tk.DISABLED)
        self.debug_display.see(tk.END)
    
    def clear_debug(self):
        """Clear debug display"""
        self.debug_display.config(state=tk.NORMAL)
        self.debug_display.delete(1.0, tk.END)
        self.debug_display.config(state=tk.DISABLED)
        self.add_debug_message("Debug display cleared")
    
    def run_test(self):
        """Run button visibility test"""
        self.add_debug_message("=== BUTTON VISIBILITY TEST ===")
        self.add_debug_message("Q CLI button exists: " + str(hasattr(self, 'q_mode_btn')))
        self.add_debug_message("SHELL button exists: " + str(hasattr(self, 'shell_mode_btn')))
        self.add_debug_message("Current mode: " + self.current_mode)
        self.add_debug_message("Try clicking SHELL button now!")

def main():
    root = tk.Tk()
    app = HALDebug(root)
    root.mainloop()

if __name__ == "__main__":
    main()
