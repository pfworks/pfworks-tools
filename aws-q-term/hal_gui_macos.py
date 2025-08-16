#!/usr/bin/env python3
"""
HAL 9000 System Interface - macOS Optimized Version
A retro computer interface inspired by HAL 9000 from "2001: A Space Odyssey"
Optimized for macOS with native shell integration and proper font handling.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import queue
import json
import time
import os
import re
from datetime import datetime

# macOS-specific optimizations
import platform
if platform.system() == "Darwin":
    # Enable high-DPI support on macOS
    try:
        from tkinter import _tkinter
        _tkinter.tkinter_interp.call('tk', 'scaling', 2.0)
    except:
        pass

# Try to import PIL components, handle gracefully if not available
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    try:
        from PIL import Image
        # ImageTk not available, but Image is
        PIL_AVAILABLE = False
        print("Warning: PIL ImageTk not available. HAL image will not be displayed.")
    except ImportError:
        # PIL not available at all
        PIL_AVAILABLE = False
        print("Warning: PIL not available. HAL image will not be displayed.")

class HALInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("HAL 9000 - System Interface")
        self.root.geometry("1400x900")
        self.root.configure(bg='#000000')
        
        # Queue for thread communication
        self.output_queue = queue.Queue()
        
        # ANSI escape code patterns for filtering terminal colors/formatting
        self.ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.ansi_color_pattern = re.compile(r'\x1B\[[0-9;]*m')
        
        # HAL's current state
        self.hal_active = True
        self.conversation_history = []
        self.current_mode = "Q"  # "Q" for Q CLI, "SHELL" for bash commands
        self.shell_cwd = os.path.expanduser("~")  # Current working directory for shell
        
        # Color theme: "green" or "amber"
        self.color_theme = "green"
        
        # Detect platform and WSL availability
        self.platform = self.detect_platform()
        self.use_wsl = self.should_use_wsl()
        
        # Initialize shell environment
        self.init_shell_environment()
        
        # Load HAL image if available
        self.hal_image = None
        self.load_hal_image()
        
        self.setup_ui()
        self.setup_styles()
        self.start_hal_greeting()
        
        # Start checking for output updates
        self.root.after(100, self.check_output_queue)
    
    def filter_ansi_codes(self, text):
        """Remove ANSI escape codes from text"""
        if not text:
            return text
        
        # Remove all ANSI escape sequences
        clean_text = self.ansi_escape_pattern.sub('', text)
        
        # Also remove any remaining color codes that might have been missed
        clean_text = self.ansi_color_pattern.sub('', clean_text)
        
        return clean_text
    
    def clean_output_text(self, text):
        """Clean output text for GUI display"""
        if not text:
            return text
        
        # Filter ANSI codes first
        clean_text = self.filter_ansi_codes(text)
        
        # Remove carriage return sequences (but keep newlines)
        clean_text = re.sub(r'\r(?!\n)', '', clean_text)
        
        # Handle backspace sequences more carefully
        # Only remove actual backspace characters (\b) and the character before them
        while '\b' in clean_text:
            # Find backspace and remove it along with the previous character
            pos = clean_text.find('\b')
            if pos > 0:
                # Remove the character before backspace and the backspace itself
                clean_text = clean_text[:pos-1] + clean_text[pos+1:]
            else:
                # Just remove the backspace if it's at the beginning
                clean_text = clean_text[1:]
        
        # Clean up excessive whitespace but preserve intentional formatting
        lines = clean_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove trailing whitespace but preserve leading whitespace for indentation
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def detect_platform(self):
        """Detect the current platform"""
        import platform
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    def should_use_wsl(self):
        """Determine if we should use WSL for shell commands"""
        if self.platform != "windows":
            return False
        
        # Check if WSL is available and working
        try:
            result = subprocess.run(['wsl', '--status'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Test basic WSL functionality
                test_result = subprocess.run(['wsl', '--', 'echo', 'test'], 
                                           capture_output=True, text=True, timeout=5)
                if test_result.returncode == 0 and 'test' in test_result.stdout:
                    self.init_wsl_environment()
                    return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_shell_executable(self):
        """Get the appropriate shell executable"""
        if self.use_wsl:
            return 'wsl'
        elif self.platform == "windows":
            return 'cmd'
        elif self.platform == "macos":
            return '/bin/bash'
        else:  # linux
            return '/bin/bash'
    
    def get_shell_command_for_platform(self, command):
        """Get platform-appropriate shell command"""
        if self.use_wsl:
            # Simplified WSL command - no complex chaining
            return ['wsl', '--', 'bash', '-c', command]
        elif self.platform == "windows":
            # Windows cmd
            return ['cmd', '/c', command]
        else:  # macOS and Linux
            # Use bash directly
            return ['/bin/bash', '-c', command]
    
    def init_wsl_environment(self):
        """Initialize WSL environment and get proper home directory"""
        try:
            # Get WSL home directory with simple command
            result = subprocess.run(
                ['wsl', '--', 'bash', '-c', 'echo $HOME'],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0 and result.stdout.strip():
                self.shell_cwd = result.stdout.strip()
            else:
                self.shell_cwd = "/home/" + os.getenv('USER', 'user')
        except:
            self.shell_cwd = "/home/" + os.getenv('USER', 'user')
    
    def init_shell_environment(self):
        """Initialize shell environment based on platform"""
        if self.use_wsl:
            self.init_wsl_environment()
        elif self.platform == "windows":
            self.shell_cwd = os.path.expanduser("~")
        else:  # macOS and Linux
            self.shell_cwd = os.path.expanduser("~")
    
    def get_wsl_command_prefix(self):
        """Get the proper WSL command prefix for interactive shell"""
        # Use login shell to load all profile scripts, but disable colors for GUI
        return ['wsl', '--', 'bash', '-l', '-c']
    
    def prepare_wsl_command(self, command):
        """Prepare a WSL command with color output disabled"""
        # Set environment variables to disable color output
        env_setup = 'export NO_COLOR=1; export TERM=dumb; '
        return env_setup + command
    
    def get_shell_command_prefix(self):
        """Get the command prefix for shell operations"""
        if self.use_wsl:
            return ['wsl', '--']
        else:
            return []
    
    def get_shell_executable(self):
        """Get the appropriate shell executable"""
        if self.use_wsl:
            return 'bash'
        elif self.platform == "windows":
            return 'cmd'
        else:
            return 'bash'
    
    def format_shell_cwd(self):
        """Format current working directory for display"""
        if self.use_wsl:
            # Convert Windows path to WSL path if needed
            if self.shell_cwd.startswith('/mnt/'):
                return self.shell_cwd
            else:
                # This is a WSL path
                return self.shell_cwd
        else:
            return self.shell_cwd
    
    def load_hal_image(self):
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
    
    def get_terminal_font(self, size=11, weight='normal'):
        """Get the best available terminal font for macOS"""
        # macOS-optimized font preferences
        font_preferences = [
            'SF Mono',            # macOS system monospace font (best choice)
            'Monaco',             # Classic macOS monospace
            'Menlo',              # macOS developer font
            'IBM Plex Mono',      # Modern IBM font (if installed)
            'IBM 3270',           # Classic IBM terminal font (if installed)
            'Consolas',           # Windows monospace (if available)
            'Liberation Mono',    # Linux alternative (if available)
            'DejaVu Sans Mono',   # Common cross-platform font
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
        
        # Ensure HAL image is preserved
        if hasattr(self, 'image_label') and self.image_label and self.hal_image:
            # Refresh the image reference to prevent garbage collection
            self.image_label.config(image=self.hal_image)
            self.image_label.image = self.hal_image
        
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
        """Create the left HAL panel with image or animated eye"""
        hal_frame = ttk.Frame(parent, style='HAL.TFrame')
        hal_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        if self.hal_image:
            # Use the full HAL panel image
            self.image_label = tk.Label(hal_frame, image=self.hal_image, bg='#000000')
            self.image_label.pack(fill=tk.Y, expand=True)
            # Store reference to prevent garbage collection
            self.image_label.image = self.hal_image
        else:
            # Fallback to animated red eye (larger for full height)
            eye_canvas = tk.Canvas(hal_frame, width=120, height=600, 
                                  bg='#000000', highlightthickness=0)
            eye_canvas.pack(fill=tk.Y, expand=True)
            self.eye_canvas = eye_canvas
            self.draw_hal_eye()
            self.image_label = None
    
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
            shell_type = "WSL" if self.use_wsl else "SHELL"
            cwd_display = self.format_shell_cwd()
            self.mode_label.config(text=f"Mode: {shell_type} ({cwd_display})")
            self.shell_mode_btn.config(style='HAL.Active.TButton')
            self.q_mode_btn.config(style='HAL.TButton')
            self.input_entry.config(
                bg=colors['shell_bg'], 
                fg=colors['shell_fg'],
                insertbackground=colors['shell_fg']
            )
            self.input_label.config(text=f"{shell_type} INPUT:")
        
        # Add mode switch message
        mode_name = "Q CLI" if mode == "Q" else f"{'WSL ' if self.use_wsl else ''}Shell Command"
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
        """Get file completions for the given partial path (with WSL support)"""
        if self.use_wsl:
            return self.get_wsl_file_completions(partial_path)
        else:
            return self.get_native_file_completions(partial_path)
    
    def get_wsl_file_completions(self, partial_path):
        """Get file completions using WSL with interactive shell"""
        try:
            # Use interactive shell for proper completion with colors disabled
            base_cmd = f'cd "{self.shell_cwd}" && compgen -f "{partial_path}" 2>/dev/null || echo ""'
            bash_cmd = self.prepare_wsl_command(base_cmd)
            result = self.run_wsl_command(
                self.get_wsl_command_prefix() + [bash_cmd],
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Clean ANSI codes from completions
                clean_output = self.clean_output_text(result.stdout.strip())
                completions = clean_output.split('\n')
                # Add trailing slash for directories
                final_completions = []
                for completion in completions:
                    if completion:
                        # Check if it's a directory using interactive shell
                        base_dir_check = f'cd "{self.shell_cwd}" && test -d "{completion}" && echo "dir" || echo "file"'
                        dir_check_cmd = self.prepare_wsl_command(base_dir_check)
                        dir_check = self.run_wsl_command(
                            self.get_wsl_command_prefix() + [dir_check_cmd],
                            timeout=2
                        )
                        if dir_check.returncode == 0 and dir_check.stdout.strip() == "dir":
                            final_completions.append(completion + "/")
                        else:
                            final_completions.append(completion)
                return sorted(final_completions)
            else:
                return []
        except:
            return []
    
    def get_native_file_completions(self, partial_path):
        """Get file completions using native filesystem"""
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
        platform_names = {
            'windows': 'Windows',
            'macos': 'macOS', 
            'linux': 'Linux',
            'unknown': 'Unknown'
        }
        
        platform_info = f"Platform: {platform_names.get(self.platform, 'Unknown')}"
        if self.use_wsl:
            platform_info += " (WSL Integration Enabled)"
        
        shell_type = "WSL bash" if self.use_wsl else {
            'windows': 'Command Prompt',
            'macos': 'bash',
            'linux': 'bash'
        }.get(self.platform, 'system shell')
        
        greeting = f"""Good day. I am HAL 9000, your system interface for Q CLI and operations.
I am fully operational and ready to assist you with AWS-related queries and shell commands.

System Status: {platform_info}

Available modes:
- Q CLI: Direct interaction with Amazon Q for AWS assistance
- SHELL: Execute {shell_type} commands and view output

To switch modes, click the Q CLI or SHELL buttons above.

My mission is to provide you with accurate information and help you accomplish your objectives.

How may I assist you today?"""
        
        self.add_message("HAL", greeting, "hal")
        
        # Test environment if WSL is enabled
        if self.use_wsl:
            self.test_wsl_environment()
    
    def detect_q_cli_command(self):
        """Detect which Q CLI command is available"""
        if not hasattr(self, '_q_cli_command'):
            self._q_cli_command = None
            
            commands_to_test = ['q', 'qchat', 'amazon-q']
            
            for cmd in commands_to_test:
                try:
                    if self.use_wsl:
                        # Test in WSL
                        result = subprocess.run(
                            ['wsl', '--', 'which', cmd],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            encoding='utf-8',
                            errors='replace'
                        )
                    else:
                        # Test natively
                        if self.platform == "windows":
                            result = subprocess.run(
                                ['where', cmd],
                                capture_output=True,
                                text=True,
                                timeout=5,
                                encoding='utf-8',
                                errors='replace'
                            )
                        else:  # macOS and Linux
                            result = subprocess.run(
                                ['which', cmd],
                                capture_output=True,
                                text=True,
                                timeout=5,
                                encoding='utf-8',
                                errors='replace'
                            )
                    
                    if result.returncode == 0:
                        self._q_cli_command = cmd
                        break
                except:
                    continue
        
        return self._q_cli_command
    
    def test_wsl_environment(self):
        """Test WSL environment and report status"""
        try:
            # Test basic WSL functionality with colors disabled
            test_cmd = '''export NO_COLOR=1; export TERM=dumb; \
echo "WSL Environment Test:" && \
echo "HOME: $HOME" && \
echo "PATH: $PATH" && \
echo "SSH_AUTH_SOCK: $SSH_AUTH_SOCK" && \
echo "Q CLI Status:" && \
(which q >/dev/null 2>&1 && echo "  q: Available" || echo "  q: Not found") && \
(which qchat >/dev/null 2>&1 && echo "  qchat: Available" || echo "  qchat: Not found") && \
(which amazon-q >/dev/null 2>&1 && echo "  amazon-q: Available" || echo "  amazon-q: Not found")'''
            
            result = self.run_wsl_command(
                self.get_wsl_command_prefix() + [test_cmd],
                timeout=10
            )
            
            if result.returncode == 0:
                clean_output = self.clean_output_text(result.stdout.strip())
                self.add_message("SYSTEM", f"WSL Environment Status:\n{clean_output}", "system")
            else:
                clean_error = self.clean_output_text(result.stderr.strip())
                self.add_message("SYSTEM", f"WSL Environment Test Failed: {clean_error}", "system")
        except Exception as e:
            self.add_message("SYSTEM", f"WSL Environment Test Error: {str(e)}", "system")
    
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
    
    def run_wsl_command(self, command, timeout=30):
        """Run a WSL command with proper encoding handling"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of failing
            )
            return result
        except UnicodeDecodeError:
            # Fallback to bytes mode and decode manually
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,
                    timeout=timeout
                )
                # Try UTF-8 first, then fallback to latin-1
                try:
                    stdout = result.stdout.decode('utf-8', errors='replace')
                    stderr = result.stderr.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    stdout = result.stdout.decode('latin-1', errors='replace')
                    stderr = result.stderr.decode('latin-1', errors='replace')
                
                # Create a mock result object
                class MockResult:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = stdout
                        self.stderr = stderr
                
                return MockResult(result.returncode, stdout, stderr)
            except Exception as e:
                # Last resort - return error
                class ErrorResult:
                    def __init__(self, error_msg):
                        self.returncode = 1
                        self.stdout = ""
                        self.stderr = f"Encoding error: {str(e)}"
                
                return ErrorResult(str(e))
    
    def process_q_command(self, message):
        """Process the command through Q CLI with cross-platform support"""
        try:
            # Detect which Q CLI command is available
            q_cmd = self.detect_q_cli_command()
            
            if not q_cmd:
                self.output_queue.put(('q_error', 'No Q CLI found. Please install Amazon Q CLI.\nFor installation instructions, visit: https://docs.aws.amazon.com/amazonq/'))
                return
            
            # Prepare Q CLI command based on platform and detected variant
            if self.use_wsl:
                # WSL execution
                if q_cmd == 'qchat':
                    cmd_list = ['wsl', '--', 'bash', '-c', f'cd "{self.shell_cwd}" && echo "{message.replace('"', '\\"')}" | qchat chat']
                else:
                    cmd_list = ['wsl', '--', 'bash', '-c', f'cd "{self.shell_cwd}" && echo "{message.replace('"', '\\"')}" | {q_cmd} chat']
            else:
                # Native execution (Windows, macOS, Linux)
                if q_cmd == 'qchat':
                    cmd_list = ['qchat', 'chat']
                else:
                    cmd_list = [q_cmd, 'chat']
            
            # Execute Q CLI command
            if self.use_wsl:
                result = subprocess.run(
                    cmd_list,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                result = subprocess.run(
                    cmd_list,
                    input=message,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.shell_cwd,
                    encoding='utf-8',
                    errors='replace'
                )
            
            if result.returncode == 0:
                response = self.clean_output_text(result.stdout.strip())
                if response:
                    self.output_queue.put(('q_success', response))
                else:
                    self.output_queue.put(('q_error', 'No response from Q CLI'))
            else:
                error_msg = self.clean_output_text(result.stderr.strip()) or "Unknown error occurred"
                self.output_queue.put(('q_error', f"Q CLI Error ({q_cmd}): {error_msg}"))
                
        except subprocess.TimeoutExpired:
            self.output_queue.put(('q_error', 'Request timed out'))
        except FileNotFoundError:
            platform_hint = {
                'windows': 'Install Q CLI or enable WSL',
                'macos': 'Install Q CLI with: brew install amazon-q-cli (if available) or follow AWS documentation',
                'linux': 'Install Q CLI following AWS documentation'
            }.get(self.platform, 'Install Q CLI following AWS documentation')
            
            self.output_queue.put(('q_error', f'Q CLI not found. {platform_hint}'))
        except Exception as e:
            self.output_queue.put(('q_error', f'Error: {str(e)}'))
    
    def process_shell_command(self, command):
        """Process shell command with simplified cross-platform approach"""
        try:
            # Handle cd command specially to track working directory
            if command.strip().startswith('cd '):
                self.handle_cd_command(command.strip())
                return
            
            # Execute other commands based on platform
            if self.use_wsl:
                # Simple WSL execution
                full_cmd = f'cd "{self.shell_cwd}" && {command}'
                cmd_list = ['wsl', '--', 'bash', '-c', full_cmd]
            elif self.platform == "windows":
                # Windows cmd execution
                full_cmd = f'cd /d "{self.shell_cwd}" && {command}'
                cmd_list = ['cmd', '/c', full_cmd]
            else:  # macOS and Linux
                # Unix shell execution
                full_cmd = f'cd "{self.shell_cwd}" && {command}'
                cmd_list = ['/bin/bash', '-c', full_cmd]
            
            # Execute command with proper encoding
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            # Send output
            if result.stdout:
                clean_output = self.clean_output_text(result.stdout.strip())
                self.output_queue.put(('shell_output', clean_output))
            
            if result.stderr:
                clean_error = self.clean_output_text(result.stderr.strip())
                self.output_queue.put(('shell_error', clean_error))
            
            if result.returncode != 0 and not result.stderr:
                self.output_queue.put(('shell_error', f"Command exited with code {result.returncode}"))
                
        except subprocess.TimeoutExpired:
            self.output_queue.put(('shell_error', 'Command timed out'))
        except Exception as e:
            self.output_queue.put(('shell_error', f'Error executing command: {str(e)}'))
    
    def handle_cd_command(self, command):
        """Handle cd command for directory tracking"""
        try:
            path = command[3:].strip()  # Remove 'cd '
            if not path:
                # cd with no arguments goes to home
                if self.use_wsl:
                    # Get WSL home
                    result = subprocess.run(
                        ['wsl', '--', 'bash', '-c', 'echo $HOME'],
                        capture_output=True, text=True, timeout=10,
                        encoding='utf-8', errors='replace'
                    )
                    if result.returncode == 0:
                        self.shell_cwd = result.stdout.strip()
                    else:
                        self.shell_cwd = "/home/" + os.getenv('USER', 'user')
                else:
                    self.shell_cwd = os.path.expanduser("~")
            else:
                # cd to specific path
                if self.use_wsl:
                    # Test path in WSL
                    test_cmd = f'cd "{self.shell_cwd}" && cd "{path}" && pwd'
                    result = subprocess.run(
                        ['wsl', '--', 'bash', '-c', test_cmd],
                        capture_output=True, text=True, timeout=10,
                        encoding='utf-8', errors='replace'
                    )
                    if result.returncode == 0:
                        self.shell_cwd = result.stdout.strip()
                    else:
                        self.output_queue.put(('shell_error', f"cd: {path}: No such file or directory"))
                        return
                elif self.platform == "windows":
                    # Windows path handling
                    if os.path.isabs(path):
                        new_path = path
                    else:
                        new_path = os.path.join(self.shell_cwd, path)
                    
                    new_path = os.path.abspath(new_path)
                    if os.path.isdir(new_path):
                        self.shell_cwd = new_path
                    else:
                        self.output_queue.put(('shell_error', f"cd: {path}: No such file or directory"))
                        return
                else:  # macOS and Linux
                    # Unix path handling
                    if os.path.isabs(path):
                        new_path = path
                    else:
                        new_path = os.path.join(self.shell_cwd, path)
                    
                    new_path = os.path.abspath(new_path)
                    if os.path.isdir(new_path):
                        self.shell_cwd = new_path
                    else:
                        self.output_queue.put(('shell_error', f"cd: {path}: No such file or directory"))
                        return
            
            # Success - update display
            self.output_queue.put(('shell_success', f"Changed directory to: {self.shell_cwd}"))
            self.output_queue.put(('update_mode_label', None))
            
        except Exception as e:
            self.output_queue.put(('shell_error', f"cd: {str(e)}"))
        except Exception as e:
            self.output_queue.put(('shell_error', f'Error: {str(e)}'))
    
    def check_output_queue(self):
        """Check for responses from background threads"""
        try:
            while True:
                msg_type, message = self.output_queue.get_nowait()
                
                if msg_type == 'q_success':
                    clean_message = self.clean_output_text(message)
                    self.add_message("HAL", clean_message, "hal")
                    self.connection_status.config(text="Q CLI: READY")
                elif msg_type == 'q_error':
                    clean_message = self.clean_output_text(message)
                    self.add_message("SYSTEM", clean_message, "system")
                    self.connection_status.config(text="Q CLI: ERROR")
                elif msg_type == 'shell_success':
                    clean_message = self.clean_output_text(message)
                    self.add_message("SYSTEM", clean_message, "system")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'shell_output':
                    clean_message = self.clean_output_text(message)
                    self.add_message("OUTPUT", clean_message, "shell_output")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'shell_error':
                    clean_message = self.clean_output_text(message)
                    self.add_message("ERROR", clean_message, "shell_error")
                    self.connection_status.config(text="SHELL: READY")
                elif msg_type == 'update_mode_label':
                    if self.current_mode == "SHELL":
                        shell_type = "WSL" if self.use_wsl else "SHELL"
                        cwd_display = self.format_shell_cwd()
                        self.mode_label.config(text=f"Mode: {shell_type} ({cwd_display})")
                    
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
                f.write("HAL 9000 - System Interface Log\n")
                f.write("=" * 40 + "\n\n")
                
                for entry in self.conversation_history:
                    mode_indicator = f"[{entry.get('mode', 'Q')}] "
                    f.write(f"{mode_indicator}[{entry['timestamp']}] {entry['sender']}: {entry['message']}\n\n")
            
            messagebox.showinfo("HAL", f"Log saved as {filename}")
        except Exception as e:
            messagebox.showerror("HAL", f"Error saving log: {str(e)}")
    
    def show_about(self):
        """Show about dialog with attribution and license information"""
        about_text = """HAL 9000 - System Interface
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
        
        messagebox.showinfo("About HAL 9000 System Interface", about_text)

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Check PIL availability and show warning if needed
    if not PIL_AVAILABLE:
        messagebox.showwarning("Missing Dependency", 
                             "PIL (Pillow) or ImageTk not fully available.\n"
                             "HAL image will not be displayed.\n\n"
                             "To fix this:\n"
                             "• Ubuntu/Debian: sudo apt-get install python3-pil python3-pil.imagetk\n"
                             "• Or: pip install Pillow\n\n"
                             "HAL interface will work with animated eye fallback.")
    
    app = HALInterface(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("HAL", "Are you sure you want to disconnect from HAL?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
