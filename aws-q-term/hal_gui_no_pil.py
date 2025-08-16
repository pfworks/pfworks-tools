#!/usr/bin/env python3
"""
HAL-inspired GUI for Amazon Q CLI Agent (PIL-free version)
A retro computer interface with HAL 9000 aesthetic
Includes both Q CLI chat mode and shell command mode
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import queue
import json
import time
import os
from datetime import datetime

class HALInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("HAL 9000 - System Interface")
        self.root.geometry("1400x900")
        self.root.configure(bg='#000000')
        
        # Queue for thread communication
        self.output_queue = queue.Queue()
        
        # HAL's current state
        self.hal_active = True
        self.conversation_history = []
        self.current_mode = "Q"  # "Q" for Q CLI, "SHELL" for bash commands
        self.shell_cwd = os.path.expanduser("~")  # Current working directory for shell
        
        # Color theme: "green" or "amber"
        self.color_theme = "green"
        
        # No PIL - always use animated eye
        self.hal_image = None
        
        self.setup_ui()
        self.setup_styles()
        self.start_hal_greeting()
        
        # Start checking for output updates
        self.root.after(100, self.check_output_queue)
    
    def get_terminal_font(self, size=11, weight='normal'):
        """Get the best available IBM-style terminal font"""
        # Try fonts in order of preference (IBM-style monospace fonts)
        font_preferences = [
            'IBM Plex Mono',      # Modern IBM font
            'IBM 3270',           # Classic IBM terminal font
            'Consolas',           # Windows monospace
            'Monaco',             # macOS monospace
            'Liberation Mono',    # Linux alternative
            'DejaVu Sans Mono',   # Common Linux font
            'Courier New',        # Fallback
            'monospace'           # System default monospace
        ]
        
        for font_name in font_preferences:
            try:
                # Test if font is available by creating a font object
                test_font = (font_name, size, weight)
                # If we get here, the font exists
                return test_font
            except:
                continue
        
        # Ultimate fallback
        return ('monospace', size, weight)
    
    def get_theme_colors(self):
        """Get colors for current theme"""
        if self.color_theme == "amber":
            return {
                'terminal_bg': '#000000',
                'terminal_fg': '#FFB000',      # Amber
                'terminal_cursor': '#FFB000',
                'terminal_select': '#332200',
                'shell_fg': '#FFCC33',         # Lighter amber for shell
                'shell_bg': '#110800',         # Dark amber tint
                'system_fg': '#FF8800',        # Orange for system messages
                'error_fg': '#FF4400',         # Red-orange for errors
                'output_fg': '#FFDD88'         # Light amber for output
            }
        else:  # green theme
            return {
                'terminal_bg': '#000000',
                'terminal_fg': '#00FF00',      # Green
                'terminal_cursor': '#00FF00',
                'terminal_select': '#003300',
                'shell_fg': '#00FFFF',         # Cyan for shell
                'shell_bg': '#001100',         # Dark green tint
                'system_fg': '#FFFF00',        # Yellow for system messages
                'error_fg': '#FF8888',         # Light red for errors
                'output_fg': '#FFFFFF'         # White for output
            }
    
    def toggle_color_theme(self):
        """Toggle between green and amber color themes"""
        self.color_theme = "amber" if self.color_theme == "green" else "green"
        
        # Update all UI elements with new colors
        self.apply_color_theme()
        
        # Add system message about theme change
        theme_name = "AMBER" if self.color_theme == "amber" else "GREEN"
        self.add_message("SYSTEM", f"Terminal theme changed to {theme_name}", "system")
    
    def apply_color_theme(self):
        """Apply the current color theme to all UI elements"""
        colors = self.get_theme_colors()
        
        # Update chat display
        self.chat_display.config(
            bg=colors['terminal_bg'],
            fg=colors['terminal_fg'],
            insertbackground=colors['terminal_cursor'],
            selectbackground=colors['terminal_select']
        )
        
        # Update input entry
        if self.current_mode == "Q":
            self.input_entry.config(
                bg=colors['terminal_bg'],
                fg=colors['terminal_fg'],
                insertbackground=colors['terminal_cursor'],
                selectbackground=colors['terminal_select']
            )
        else:  # SHELL mode
            self.input_entry.config(
                bg=colors['shell_bg'],
                fg=colors['shell_fg'],
                insertbackground=colors['shell_fg'],
                selectbackground=colors['terminal_select']
            )
        
        # Update text tags with new colors
        terminal_font = self.get_terminal_font(11)
        self.chat_display.tag_configure('hal', foreground='#FF0000', font=self.get_terminal_font(11, 'bold'))
        self.chat_display.tag_configure('user', foreground=colors['terminal_fg'], font=terminal_font)
        self.chat_display.tag_configure('shell_user', foreground=colors['shell_fg'], font=terminal_font)
        self.chat_display.tag_configure('shell_output', foreground=colors['output_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('shell_error', foreground=colors['error_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('system', foreground=colors['system_fg'], font=self.get_terminal_font(10, 'italic'))
        self.chat_display.tag_configure('timestamp', foreground='#888888', font=self.get_terminal_font(9))
        
        # Update theme button text
        theme_text = "AMBER" if self.color_theme == "green" else "GREEN"
        self.theme_btn.config(text=theme_text)
        """Load the HAL 9000 panel image if available"""
        if not PIL_AVAILABLE:
            self.hal_image = None
            return
            
        image_path = os.path.join(os.path.dirname(__file__), "assets", "Hal_9000_Panel.svg.png")
        try:
            if os.path.exists(image_path):
                # Load image and resize to full height while maintaining aspect ratio
                pil_image = Image.open(image_path)
                # Calculate size for full height (about 600px for the interface height)
                target_height = 600
                aspect_ratio = pil_image.width / pil_image.height
                target_width = int(target_height * aspect_ratio)
                pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.hal_image = ImageTk.PhotoImage(pil_image)
            else:
                self.hal_image = None
        except Exception as e:
            print(f"Could not load HAL image: {e}")
            self.hal_image = None
    
    def setup_styles(self):
        """Configure the retro HAL-inspired styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Get terminal font for consistent styling
        terminal_font = self.get_terminal_font(12, 'bold')
        button_font = self.get_terminal_font(10, 'bold')
        
        # Configure styles for HAL aesthetic
        style.configure('HAL.TFrame', background='#000000')
        style.configure('HAL.TLabel', 
                       background='#000000', 
                       foreground='#FF0000',
                       font=terminal_font)
        style.configure('HAL.TButton',
                       background='#330000',
                       foreground='#FF0000',
                       font=button_font,
                       borderwidth=2)
        style.map('HAL.TButton',
                 background=[('active', '#550000')])
        
        # Mode-specific button styles
        style.configure('HAL.Active.TButton',
                       background='#550000',
                       foreground='#FFFFFF',
                       font=button_font,
                       borderwidth=2)
        
        # Theme button style
        style.configure('HAL.Theme.TButton',
                       background='#004400',
                       foreground='#00FF00',
                       font=button_font,
                       borderwidth=2)
        style.map('HAL.Theme.TButton',
                 background=[('active', '#006600')])
    
    def setup_ui(self):
        """Create the main interface components"""
        # Main container with horizontal layout
        main_frame = ttk.Frame(self.root, style='HAL.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - HAL image (full height)
        self.create_hal_panel(main_frame)
        
        # Right side - Interface components
        right_frame = ttk.Frame(main_frame, style='HAL.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Header with controls
        self.create_header(right_frame)
        
        # Chat display area
        self.create_chat_area(right_frame)
        
        # Input area
        self.create_input_area(right_frame)
        
        # Status bar
        self.create_status_bar(right_frame)
    
    def create_hal_panel(self, parent):
        """Create the left HAL panel with animated eye"""
        hal_frame = ttk.Frame(parent, style='HAL.TFrame')
        hal_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Always use animated red eye (larger for full height)
        eye_canvas = tk.Canvas(hal_frame, width=120, height=600, 
                              bg='#000000', highlightthickness=0)
        eye_canvas.pack(fill=tk.Y, expand=True)
        self.eye_canvas = eye_canvas
        self.draw_hal_eye()
        self.image_label = None  # No image in PIL-free version
    
    def create_header(self, parent):
        """Create the header with controls (now on right side)"""
        header_frame = ttk.Frame(parent, style='HAL.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title and status (left side of header)
        left_frame = ttk.Frame(header_frame, style='HAL.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(left_frame, 
                               text="HAL 9000 - System Interface",
                               style='HAL.TLabel',
                               font=self.get_terminal_font(16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        self.status_label = ttk.Label(left_frame,
                                     text="System Status: OPERATIONAL",
                                     style='HAL.TLabel',
                                     font=self.get_terminal_font(10))
        self.status_label.pack(anchor=tk.W)
        
        # Mode indicator
        self.mode_label = ttk.Label(left_frame,
                                   text="Mode: Q CLI",
                                   style='HAL.TLabel',
                                   font=self.get_terminal_font(10))
        self.mode_label.pack(anchor=tk.W)
        
        # Control buttons (right side of header)
        button_frame = ttk.Frame(header_frame, style='HAL.TFrame')
        button_frame.pack(side=tk.RIGHT)
        
        # Theme toggle button (top row)
        theme_frame = ttk.Frame(button_frame, style='HAL.TFrame')
        theme_frame.pack(pady=(0, 5))
        
        self.theme_btn = ttk.Button(theme_frame, text="AMBER", 
                                   command=self.toggle_color_theme, 
                                   style='HAL.Theme.TButton')
        self.theme_btn.pack()
        
        # Mode selection buttons (middle row)
        mode_frame = ttk.Frame(button_frame, style='HAL.TFrame')
        mode_frame.pack(pady=(0, 5))
        
        self.q_mode_btn = ttk.Button(mode_frame, text="Q CLI", 
                                    command=lambda: self.set_mode("Q"), 
                                    style='HAL.Active.TButton')
        self.q_mode_btn.pack(side=tk.LEFT, padx=2)
        
        self.shell_mode_btn = ttk.Button(mode_frame, text="SHELL", 
                                        command=lambda: self.set_mode("SHELL"), 
                                        style='HAL.TButton')
        self.shell_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Action buttons (bottom row)
        action_frame = ttk.Frame(button_frame, style='HAL.TFrame')
        action_frame.pack()
        
        ttk.Button(action_frame, text="CLEAR", 
                  command=self.clear_chat, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="SAVE LOG", 
                  command=self.save_log, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="ABOUT", 
                  command=self.show_about, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
    
    def draw_hal_eye(self):
        """Draw and animate HAL's red eye (fallback if no image)"""
        if not hasattr(self, 'eye_canvas'):
            return
            
        self.eye_canvas.delete("all")
        
        # Center the eye in the larger canvas
        center_x, center_y = 60, 300  # Center of 120x600 canvas
        radius = 40
        
        # Outer ring
        self.eye_canvas.create_oval(center_x-radius, center_y-radius, 
                                   center_x+radius, center_y+radius, 
                                   outline='#FF0000', width=4, fill='#330000')
        
        # Inner eye with glow effect
        inner_radius = 25
        self.eye_canvas.create_oval(center_x-inner_radius, center_y-inner_radius, 
                                   center_x+inner_radius, center_y+inner_radius, 
                                   outline='#FF0000', width=3, fill='#FF0000')
        
        # Central dot
        dot_radius = 8
        self.eye_canvas.create_oval(center_x-dot_radius, center_y-dot_radius, 
                                   center_x+dot_radius, center_y+dot_radius, 
                                   outline='#FFFFFF', width=2, fill='#FFFFFF')
        
        # Schedule next animation frame
        self.root.after(2000, self.animate_eye)
    
    def animate_eye(self):
        """Create a subtle pulsing animation for HAL's eye"""
        if not hasattr(self, 'eye_canvas'):
            return
            
        # Dim the eye briefly
        self.eye_canvas.delete("all")
        center_x, center_y = 60, 300
        radius = 40
        inner_radius = 25
        
        self.eye_canvas.create_oval(center_x-radius, center_y-radius, 
                                   center_x+radius, center_y+radius, 
                                   outline='#880000', width=4, fill='#110000')
        self.eye_canvas.create_oval(center_x-inner_radius, center_y-inner_radius, 
                                   center_x+inner_radius, center_y+inner_radius, 
                                   outline='#880000', width=3, fill='#880000')
        
        # Restore after brief dim
        self.root.after(200, self.draw_hal_eye)
    
    def set_mode(self, mode):
        """Switch between Q CLI and Shell modes"""
        self.current_mode = mode
        colors = self.get_theme_colors()
        
        if mode == "Q":
            self.mode_label.config(text="Mode: Q CLI")
            self.q_mode_btn.config(style='HAL.Active.TButton')
            self.shell_mode_btn.config(style='HAL.TButton')
            self.input_entry.config(
                bg=colors['terminal_bg'], 
                fg=colors['terminal_fg'],
                insertbackground=colors['terminal_cursor']
            )
            self.input_label.config(text="Q INPUT:")
        else:  # SHELL
            self.mode_label.config(text=f"Mode: SHELL ({self.shell_cwd})")
            self.shell_mode_btn.config(style='HAL.Active.TButton')
            self.q_mode_btn.config(style='HAL.TButton')
            self.input_entry.config(
                bg=colors['shell_bg'], 
                fg=colors['shell_fg'],
                insertbackground=colors['shell_fg']
            )
            self.input_label.config(text="SHELL INPUT:")
        
        # Add mode switch message
        mode_name = "Q CLI" if mode == "Q" else "Shell Command"
        self.add_message("SYSTEM", f"Switched to {mode_name} mode", "system")
    
    def create_chat_area(self, parent):
        """Create the main chat display area"""
        chat_frame = ttk.Frame(parent, style='HAL.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Get initial colors
        colors = self.get_theme_colors()
        terminal_font = self.get_terminal_font(11)
        
        # Chat display with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg=colors['terminal_bg'],
            fg=colors['terminal_fg'],
            font=terminal_font,
            insertbackground=colors['terminal_cursor'],
            selectbackground=colors['terminal_select'],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('hal', foreground='#FF0000', font=self.get_terminal_font(11, 'bold'))
        self.chat_display.tag_configure('user', foreground=colors['terminal_fg'], font=terminal_font)
        self.chat_display.tag_configure('shell_user', foreground=colors['shell_fg'], font=terminal_font)
        self.chat_display.tag_configure('shell_output', foreground=colors['output_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('shell_error', foreground=colors['error_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('system', foreground=colors['system_fg'], font=self.get_terminal_font(10, 'italic'))
        self.chat_display.tag_configure('timestamp', foreground='#888888', font=self.get_terminal_font(9))
    
    def create_input_area(self, parent):
        """Create the user input area"""
        input_frame = ttk.Frame(parent, style='HAL.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input label
        self.input_label = ttk.Label(input_frame, text="Q INPUT:", style='HAL.TLabel')
        self.input_label.pack(anchor=tk.W)
        
        # Input field and send button
        entry_frame = ttk.Frame(input_frame, style='HAL.TFrame')
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Get initial colors
        colors = self.get_theme_colors()
        terminal_font = self.get_terminal_font(12)
        
        self.input_entry = tk.Entry(
            entry_frame,
            bg=colors['terminal_bg'],
            fg=colors['terminal_fg'],
            font=terminal_font,
            insertbackground=colors['terminal_cursor'],
            selectbackground=colors['terminal_select']
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        self.input_entry.bind('<Tab>', self.handle_tab_completion)
        
        send_button = ttk.Button(entry_frame, text="SEND", 
                               command=self.send_message, style='HAL.TButton')
        send_button.pack(side=tk.RIGHT)
        
        # Focus on input
        self.input_entry.focus()
    
    def handle_tab_completion(self, event):
        """Handle tab completion for shell mode"""
        if self.current_mode != "SHELL":
            return "break"  # Prevent default tab behavior in Q CLI mode
        
        current_text = self.input_entry.get()
        cursor_pos = self.input_entry.index(tk.INSERT)
        
        # Get the word being completed (from last space to cursor)
        text_to_cursor = current_text[:cursor_pos]
        words = text_to_cursor.split()
        
        if not words:
            return "break"
        
        # Get the partial word to complete
        partial_word = words[-1] if text_to_cursor.endswith(words[-1]) else ""
        word_start_pos = cursor_pos - len(partial_word)
        
        # Perform file completion
        try:
            completions = self.get_file_completions(partial_word)
            
            if len(completions) == 1:
                # Single completion - replace the partial word
                completion = completions[0]
                self.input_entry.delete(word_start_pos, cursor_pos)
                self.input_entry.insert(word_start_pos, completion)
            elif len(completions) > 1:
                # Multiple completions - show them and complete common prefix
                common_prefix = self.get_common_prefix(completions)
                if len(common_prefix) > len(partial_word):
                    # There's a common prefix longer than what we have
                    self.input_entry.delete(word_start_pos, cursor_pos)
                    self.input_entry.insert(word_start_pos, common_prefix)
                
                # Show available completions
                self.show_completions(completions)
                
        except Exception as e:
            # Silently handle completion errors
            pass
        
        return "break"  # Prevent default tab behavior
    
    def get_file_completions(self, partial_path):
        """Get file completions for the given partial path"""
        import glob
        import os
        
        if not partial_path:
            # Complete files in current directory
            pattern = "*"
            base_dir = self.shell_cwd
        elif partial_path.startswith('/'):
            # Absolute path
            if partial_path.endswith('/'):
                pattern = partial_path + "*"
                base_dir = ""
            else:
                pattern = partial_path + "*"
                base_dir = ""
        elif '/' in partial_path:
            # Relative path with directory
            dir_part, file_part = os.path.split(partial_path)
            pattern = os.path.join(self.shell_cwd, dir_part, file_part + "*")
            base_dir = ""
        else:
            # Simple filename in current directory
            pattern = os.path.join(self.shell_cwd, partial_path + "*")
            base_dir = ""
        
        try:
            matches = glob.glob(pattern)
            completions = []
            
            for match in matches:
                if base_dir:
                    # Make relative to base directory
                    rel_match = os.path.relpath(match, base_dir)
                else:
                    rel_match = match
                
                # Add trailing slash for directories
                if os.path.isdir(match):
                    rel_match += "/"
                
                completions.append(rel_match)
            
            return sorted(completions)
        except:
            return []
    
    def get_common_prefix(self, strings):
        """Get the common prefix of a list of strings"""
        if not strings:
            return ""
        
        common = strings[0]
        for s in strings[1:]:
            while not s.startswith(common):
                common = common[:-1]
                if not common:
                    break
        
        return common
    
    def show_completions(self, completions):
        """Show available completions in the chat area"""
        if len(completions) <= 20:  # Don't show too many
            completion_text = "  ".join(completions)
            self.add_message("COMPLETIONS", completion_text, "system")
    
    def create_status_bar(self, parent):
        """Create the bottom status bar"""
        status_frame = ttk.Frame(parent, style='HAL.TFrame')
        status_frame.pack(fill=tk.X)
        
        self.connection_status = ttk.Label(status_frame,
                                          text="Q CLI: READY",
                                          style='HAL.TLabel',
                                          font=self.get_terminal_font(9))
        self.connection_status.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(status_frame,
                                   text="",
                                   style='HAL.TLabel',
                                   font=self.get_terminal_font(9))
        self.time_label.pack(side=tk.RIGHT)
        
        self.update_time()
    
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"TIME: {current_time}")
        self.root.after(1000, self.update_time)
    
    def start_hal_greeting(self):
        """Display HAL's initial greeting"""
        greeting = """Good day. I am HAL 9000, your interface to Amazon Q and system operations.
I am fully operational and ready to assist you with AWS-related queries and shell commands.

Available modes:
- Q CLI: Direct interaction with Amazon Q for AWS assistance
- SHELL: Execute bash commands and view output

To switch modes, click the Q CLI or SHELL buttons above.

My mission is to provide you with accurate information and help you accomplish your objectives.

How may I assist you today?"""
        
        self.add_message("HAL", greeting, "hal")
    
    def add_message(self, sender, message, tag):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender and message
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'mode': self.current_mode
        })
    
    def send_message(self, event=None):
        """Send user message to appropriate handler based on mode"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        if self.current_mode == "Q":
            self.send_q_message(message)
        else:  # SHELL
            self.send_shell_command(message)
    
    def send_q_message(self, message):
        """Send message to Q CLI"""
        # Add user message to display
        self.add_message("USER", message, "user")
        
        # Update status
        self.connection_status.config(text="Q CLI: PROCESSING...")
        
        # Send to Q CLI in background thread
        threading.Thread(target=self.process_q_command, args=(message,), daemon=True).start()
    
    def send_shell_command(self, command):
        """Execute shell command"""
        # Add command to display
        self.add_message("SHELL", f"{self.shell_cwd}$ {command}", "shell_user")
        
        # Update status
        self.connection_status.config(text="SHELL: EXECUTING...")
        
        # Execute in background thread
        threading.Thread(target=self.process_shell_command, args=(command,), daemon=True).start()
    
    def process_q_command(self, message):
        """Process the command through Q CLI"""
        try:
            # Run Q CLI command
            result = subprocess.run(
                ['q', 'chat', '--message', message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if response:
                    self.output_queue.put(('q_success', response))
                else:
                    self.output_queue.put(('q_error', 'No response from Q CLI'))
            else:
                error_msg = result.stderr.strip() or "Unknown error occurred"
                self.output_queue.put(('q_error', f"Q CLI Error: {error_msg}"))
                
        except subprocess.TimeoutExpired:
            self.output_queue.put(('q_error', 'Request timed out'))
        except FileNotFoundError:
            self.output_queue.put(('q_error', 'Q CLI not found. Please ensure it is installed and in PATH.'))
        except Exception as e:
            self.output_queue.put(('q_error', f'Error: {str(e)}'))
    
    def process_shell_command(self, command):
        """Process shell command"""
        try:
            # Handle cd command specially to track working directory
            if command.strip().startswith('cd '):
                path = command.strip()[3:].strip()
                if not path:
                    path = os.path.expanduser("~")
                
                try:
                    new_cwd = os.path.abspath(os.path.join(self.shell_cwd, path))
                    if os.path.isdir(new_cwd):
                        self.shell_cwd = new_cwd
                        self.output_queue.put(('shell_success', f"Changed directory to: {self.shell_cwd}"))
                        self.output_queue.put(('update_mode_label', None))
                    else:
                        self.output_queue.put(('shell_error', f"cd: {path}: No such file or directory"))
                except Exception as e:
                    self.output_queue.put(('shell_error', f"cd: {str(e)}"))
                return
            
            # Execute other commands
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.shell_cwd
            )
            
            # Send output
            if result.stdout:
                self.output_queue.put(('shell_output', result.stdout.strip()))
            
            if result.stderr:
                self.output_queue.put(('shell_error', result.stderr.strip()))
            
            if result.returncode != 0 and not result.stderr:
                self.output_queue.put(('shell_error', f"Command exited with code {result.returncode}"))
                
        except subprocess.TimeoutExpired:
            self.output_queue.put(('shell_error', 'Command timed out'))
        except Exception as e:
            self.output_queue.put(('shell_error', f'Error: {str(e)}'))
    
    def check_output_queue(self):
        """Check for responses from background threads"""
        try:
            while True:
                msg_type, message = self.output_queue.get_nowait()
                
                if msg_type == 'q_success':
                    self.add_message("HAL", message, "hal")
                    self.connection_status.config(text="Q CLI: READY")
                elif msg_type == 'q_error':
                    self.add_message("SYSTEM", message, "system")
                    self.connection_status.config(text="Q CLI: ERROR")
                elif msg_type == 'shell_success':
                    self.add_message("SYSTEM", message, "system")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'shell_output':
                    self.add_message("OUTPUT", message, "shell_output")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'shell_error':
                    self.add_message("ERROR", message, "shell_error")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'update_mode_label':
                    if self.current_mode == "SHELL":
                        self.mode_label.config(text=f"Mode: SHELL ({self.shell_cwd})")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_output_queue)
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.conversation_history.clear()
        self.start_hal_greeting()
    
    def save_log(self):
        """Save conversation log to file"""
        if not self.conversation_history:
            messagebox.showinfo("HAL", "No conversation to save.")
            return
        
        filename = f"hal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write("HAL 9000 - Amazon Q Interface Log\n")
                f.write("=" * 40 + "\n\n")
                
                for entry in self.conversation_history:
                    mode_indicator = f"[{entry.get('mode', 'Q')}] "
                    f.write(f"{mode_indicator}[{entry['timestamp']}] {entry['sender']}: {entry['message']}\n\n")
            
            messagebox.showinfo("HAL", f"Log saved as {filename}")
        except Exception as e:
            messagebox.showerror("HAL", f"Error saving log: {str(e)}")
    
    def show_about(self):
        """Show about dialog with attribution and license information"""
        about_text = """HAL 9000 - Amazon Q Interface
Version 2.0

A retro computer interface inspired by HAL 9000 from "2001: A Space Odyssey"

Features:
• Q CLI Integration for AWS assistance
• Shell command execution
• Conversation logging
• Retro HAL aesthetic

HAL 9000 Panel Image Attribution:
By Tom Cowap - Own work, CC BY-SA 4.0
https://commons.wikimedia.org/w/index.php?curid=103068276

License:
This project is licensed under the GNU General Public License v3.0 (GPLv3).
https://www.gnu.org/licenses/gpl-3.0.html

"I'm sorry, Dave. I'm afraid I can't do that."
But this HAL can help you with AWS and system operations! 🚀"""
        
        messagebox.showinfo("About HAL 9000 Interface", about_text)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = HALInterface(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("HAL", "Are you sure you want to disconnect from HAL?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
