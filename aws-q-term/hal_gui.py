#!/usr/bin/env python3
"""
HAL-inspired GUI for Amazon Q CLI Agent
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
import re
from datetime import datetime

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
        
        # Display modes
        self.display_mode = "retro"  # "retro" for CRT mode, "modern" for clean mode
        
        # SSH environment setup (can be disabled for debugging)
        self.enable_ssh_env_setup = True  # Enabled by default - now checks existing agents first
        
        # Debug window
        self.debug_window = None
        self.debug_text = None
        self.debug_enabled = False
        
        # Detect platform and WSL availability first
        self.platform = self.detect_platform()
        self.use_wsl = self.should_use_wsl()
        
        # Shell session type for Windows
        if self.platform == "windows":
            self.windows_shell_type = "cmd"  # Default to CMD, will be updated by detection
        else:
            # On Linux/macOS, use the shell that invoked the program
            self.windows_shell_type = None  # Not applicable
        
        # Color theme: "green" or "amber"
        self.color_theme = "green"
        
        # Initialize shell environment
        self.init_shell_environment()
        
        # Load HAL image if available
        self.hal_image = None
        self.load_hal_image()
        
        self.setup_ui()
        self.setup_styles()
        
        # Initialize mode and status
        self.set_mode(self.current_mode)
        
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
        """Get platform-appropriate shell command with proper environment"""
        if self.use_wsl:
            # Use interactive login shell to inherit full environment including SSH agent
            return ['wsl', '--', 'bash', '-l', '-c', command]
        elif self.platform == "windows":
            # Windows cmd
            return ['cmd', '/c', command]
        else:  # macOS and Linux
            # Use bash with login shell for full environment
            return ['/bin/bash', '-l', '-c', command]
    
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
    
    def toggle_display_mode(self):
        """Toggle between CRT retro and modern display modes"""
        self.display_mode = "modern" if self.display_mode == "retro" else "retro"
        
        # Update display styling (includes system message)
        self.apply_display_mode()
        
        # Update button text
        display_text = "MODERN" if self.display_mode == "retro" else "CRT"
        self.display_btn.config(text=display_text)
    
    def apply_display_mode(self):
        """Apply the current display mode styling"""
        colors = self.get_theme_colors()
        
        if self.display_mode == "retro":
            # CRT retro mode - enhanced retro styling
            self.chat_display.config(
                relief='sunken',
                bd=3,
                highlightthickness=2,
                highlightcolor=colors['terminal_fg'],
                highlightbackground=colors['terminal_bg'],
                # Add subtle padding for CRT effect
                padx=10,
                pady=8
            )
            
            # Retro input styling
            self.input_entry.config(
                relief='sunken',
                bd=2,
                highlightthickness=2,
                highlightcolor=colors['terminal_fg']
            )
            
            # Retro button styling - more pronounced borders
            style = ttk.Style()
            style.configure('HAL.TButton',
                           relief='raised',
                           borderwidth=2)
            style.configure('HAL.Active.TButton',
                           relief='sunken',
                           borderwidth=2)
            
            # Add retro cursor effect
            self.root.config(cursor='dotbox')
            
            # Update status with retro indicator
            self.add_message("SYSTEM", "CRT RETRO mode activated - Enhanced terminal styling", "system")
            
        else:
            # Modern clean mode - flat, minimal styling
            self.chat_display.config(
                relief='flat',
                bd=1,
                highlightthickness=1,
                highlightcolor='#666666',
                highlightbackground='#333333',
                # Minimal padding for modern look
                padx=5,
                pady=5
            )
            
            # Modern input styling
            self.input_entry.config(
                relief='flat',
                bd=1,
                highlightthickness=1,
                highlightcolor='#666666'
            )
            
            # Modern button styling - flat design
            style = ttk.Style()
            style.configure('HAL.TButton',
                           relief='flat',
                           borderwidth=1)
            style.configure('HAL.Active.TButton',
                           relief='flat',
                           borderwidth=1)
            
            # Standard cursor
            self.root.config(cursor='')
            
            # Update status with modern indicator
            self.add_message("SYSTEM", "MODERN mode activated - Clean minimal styling", "system")
        
        # Force refresh of the display
        self.root.update_idletasks()
    
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
        
        # Update display button text
        display_text = "MODERN" if self.display_mode == "retro" else "CRT"
        self.display_btn.config(text=display_text)
        
        # Apply current display mode
        self.apply_display_mode()
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
        self.theme_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Display mode toggle button
        self.display_btn = ttk.Button(theme_frame, text="CRT", 
                                     command=self.toggle_display_mode, 
                                     style='HAL.Theme.TButton')
        self.display_btn.pack(side=tk.LEFT)
        
        # Mode selection buttons (middle row)
        mode_frame = ttk.Frame(button_frame, style='HAL.TFrame')
        mode_frame.pack(pady=(0, 5))
        
        if self.platform == "windows":
            # Windows: Single mode button that toggles between Q CLI and SHELL
            self.mode_toggle_btn = ttk.Button(mode_frame, text="Q CLI", 
                                            command=self.toggle_mode, 
                                            style='HAL.Active.TButton')
            self.mode_toggle_btn.pack(side=tk.LEFT, padx=2)
        else:
            # Linux/macOS: Separate Q CLI and SHELL buttons
            self.q_mode_btn = ttk.Button(mode_frame, text="Q CLI", 
                                        command=lambda: self.set_mode("Q"), 
                                        style='HAL.Active.TButton')
            self.q_mode_btn.pack(side=tk.LEFT, padx=2)
            
            self.shell_mode_btn = ttk.Button(mode_frame, text="SHELL", 
                                            command=lambda: self.set_mode("SHELL"), 
                                            style='HAL.TButton')
            self.shell_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Directory chooser button
        self.dir_btn = ttk.Button(mode_frame, text="DIR", 
                                 command=self.choose_directory, 
                                 style='HAL.TButton')
        self.dir_btn.pack(side=tk.LEFT, padx=2)
        
        # SSH key management button
        self.ssh_btn = ttk.Button(mode_frame, text="SSH", 
                                 command=self.manage_ssh_keys, 
                                 style='HAL.TButton')
        self.ssh_btn.pack(side=tk.LEFT, padx=2)
        
        # Shell type selector button (Windows only)
        if self.platform == "windows":
            self.shell_selector_btn = ttk.Button(mode_frame, text="CMD", 
                                               command=self.show_shell_selector, 
                                               style='HAL.TButton')
            self.shell_selector_btn.pack(side=tk.LEFT, padx=2)
        
        # Debug button
        self.debug_btn = ttk.Button(mode_frame, text="DEBUG", 
                                   command=self.toggle_debug_window, 
                                   style='HAL.TButton')
        self.debug_btn.pack(side=tk.LEFT, padx=2)
        
        # Action buttons (bottom row)
        action_frame = ttk.Frame(button_frame, style='HAL.TFrame')
        action_frame.pack()
        
        ttk.Button(action_frame, text="CLEAR", 
                  command=self.clear_chat, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="SAVE LOG", 
                  command=self.save_log, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="ABOUT", 
                  command=self.show_about, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="EXIT", 
                  command=self.safe_exit, style='HAL.TButton').pack(side=tk.LEFT, padx=2)
    
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
    
    def toggle_mode(self):
        """Toggle between Q CLI and SHELL modes (Windows only)"""
        if self.platform != "windows":
            return
        
        new_mode = "SHELL" if self.current_mode == "Q" else "Q"
        self.set_mode(new_mode)
    
    def set_mode(self, mode):
        """Switch between Q CLI and Shell modes"""
        self.current_mode = mode
        colors = self.get_theme_colors()
        
        if mode == "Q":
            self.mode_label.config(text="Mode: Q CLI")
            
            # Update buttons based on platform
            if self.platform == "windows":
                # Windows: Update toggle button
                self.mode_toggle_btn.config(text="Q CLI", style='HAL.Active.TButton')
            else:
                # Linux/macOS: Update separate buttons
                self.q_mode_btn.config(style='HAL.Active.TButton')
                self.shell_mode_btn.config(style='HAL.TButton')
            
            self.input_entry.config(
                bg=colors['terminal_bg'], 
                fg=colors['terminal_fg'],
                insertbackground=colors['terminal_cursor']
            )
            self.input_label.config(text="Q INPUT:")
            # Update status to Q CLI
            self.connection_status.config(text="Q CLI: READY")
        else:  # SHELL
            shell_type = "WSL" if self.use_wsl else "SHELL"
            cwd_display = self.format_shell_cwd()
            self.mode_label.config(text=f"Mode: {shell_type} ({cwd_display})")
            
            # Update buttons based on platform
            if self.platform == "windows":
                # Windows: Update toggle button
                self.mode_toggle_btn.config(text="SHELL", style='HAL.Active.TButton')
            else:
                # Linux/macOS: Update separate buttons
                self.shell_mode_btn.config(style='HAL.Active.TButton')
                self.q_mode_btn.config(style='HAL.TButton')
            
            self.input_entry.config(
                bg=colors['shell_bg'], 
                fg=colors['shell_fg'],
                insertbackground=colors['shell_fg']
            )
            self.input_label.config(text=f"{shell_type} INPUT:")
            # Update status to SHELL
            self.connection_status.config(text="SHELL: READY")
        
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
        elif self.platform == "windows":
            # Setup Windows SSH agent and detect shell capabilities
            self.detect_windows_shell_capabilities()
            self.setup_windows_ssh_agent()
            
            # Update shell selector button text if it exists
            self.update_shell_selector_button()
    
    def detect_q_cli_command(self):
        """Detect which Q CLI command is available with proper environment"""
        if not hasattr(self, '_q_cli_command'):
            self._q_cli_command = None
            
            commands_to_test = ['q', 'qchat', 'amazon-q']
            
            for cmd in commands_to_test:
                try:
                    if self.use_wsl:
                        # Test in WSL with login shell to access full PATH
                        result = subprocess.run(
                            ['wsl', '--', 'bash', '-l', '-c', f'which {cmd}'],
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
        """Test WSL environment and report status with full environment"""
        try:
            # Test basic WSL functionality with login shell to get full environment
            test_cmd = '''echo "WSL Environment Test:" && \
echo "HOME: $HOME" && \
echo "PATH: $PATH" && \
echo "SSH_AUTH_SOCK: $SSH_AUTH_SOCK" && \
echo "SSH_AGENT_PID: $SSH_AGENT_PID" && \
echo "Q CLI Status:" && \
(which q >/dev/null 2>&1 && echo "  q: Available at $(which q)" || echo "  q: Not found") && \
(which qchat >/dev/null 2>&1 && echo "  qchat: Available at $(which qchat)" || echo "  qchat: Not found") && \
(which amazon-q >/dev/null 2>&1 && echo "  amazon-q: Available at $(which amazon-q)" || echo "  amazon-q: Not found") && \
echo "SSH Keys:" && \
(ssh-add -l 2>/dev/null | head -3 || echo "  No SSH keys loaded or ssh-agent not running")'''
            
            result = subprocess.run(
                ['wsl', '--', 'bash', '-l', '-c', test_cmd],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='replace'
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
        """Process the command through Q CLI with proper environment inheritance"""
        try:
            # Detect which Q CLI command is available
            q_cmd = self.detect_q_cli_command()
            
            if not q_cmd:
                self.output_queue.put(('q_error', 'No Q CLI found. Please install Amazon Q CLI.\nFor installation instructions, visit: https://docs.aws.amazon.com/amazonq/'))
                return
            
            # Prepare Q CLI command based on platform and detected variant
            if self.use_wsl:
                # WSL execution with login shell to inherit SSH agent and environment
                if q_cmd == 'qchat':
                    cmd_list = ['wsl', '--', 'bash', '-l', '-c', f'cd "{self.shell_cwd}" && echo "{message.replace('"', '\\"')}" | qchat chat']
                else:
                    cmd_list = ['wsl', '--', 'bash', '-l', '-c', f'cd "{self.shell_cwd}" && echo "{message.replace('"', '\\"')}" | {q_cmd} chat']
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
    
    def should_suppress_output(self, stderr_text, stdout_text):
        """Determine if output should be completely suppressed"""
        if not stderr_text and not stdout_text:
            return False
        
        # Combine both stderr and stdout for checking
        combined_text = (stderr_text or "") + "\n" + (stdout_text or "")
        
        # Messages to suppress entirely
        suppress_patterns = [
            # Keychain messages
            r'\* keychain \d+\.\d+\.\d+',
            r'\* Found existing ssh-agent:',
            r'\* Known ssh key:',
            r'\* Adding ssh key:',
            r'\* ssh-agent: Started agent',
            r'http://www\.funtoo\.org',
            # SSH key loading warnings
            r'Warning: No SSH keys loaded',
            r'Could not open a connection to your authentication agent',
            r'Identity added:',
            r'ssh-add: .*: No such file or directory',
            # SSH agent startup messages
            r'SSH_AUTH_SOCK=.*; export SSH_AUTH_SOCK;',
            r'SSH_AGENT_PID=.*; export SSH_AGENT_PID;',
            r'echo Agent pid \d+;',
        ]
        
        # Check if combined text contains only suppressible messages
        lines = combined_text.strip().split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if not non_empty_lines:
            return True  # Empty output can be suppressed
        
        for line in non_empty_lines:
            # Check if this line should be suppressed
            should_suppress = False
            for pattern in suppress_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_suppress = True
                    break
            
            # If we find a line that shouldn't be suppressed, don't suppress the whole output
            if not should_suppress:
                return False
        
        # All non-empty lines are suppressible
        return True
    
    def is_actual_error(self, stderr_text, stdout_text, return_code):
        """Determine if stderr output is actually an error or just informational"""
        if not stderr_text:
            return False
        
        # Keychain outputs informational messages to stderr that aren't errors
        keychain_info_patterns = [
            r'\* keychain \d+\.\d+\.\d+',
            r'\* Found existing ssh-agent:',
            r'\* Known ssh key:',
            r'\* Adding ssh key:',
            r'\* ssh-agent: Started agent',
        ]
        
        # SSH connection informational messages
        ssh_info_patterns = [
            r'Warning: Permanently added .* to the list of known hosts',
            r'The authenticity of host .* can\'t be established',
        ]
        
        # Git informational messages
        git_info_patterns = [
            r'Cloning into',
            r'remote: Counting objects',
            r'Receiving objects:',
        ]
        
        all_info_patterns = keychain_info_patterns + ssh_info_patterns + git_info_patterns
        
        # Check if stderr contains only informational messages
        lines = stderr_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line matches any informational pattern
            is_info = False
            for pattern in all_info_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_info = True
                    break
            
            # If we find a line that's not informational, it's likely an error
            if not is_info:
                return True
        
        # If return code is 0 and all stderr lines are informational, not an error
        if return_code == 0:
            return False
        
        # Non-zero return code with stderr is likely an error
        return True
    
    def process_command_output(self, result):
        """Process command output and determine what to display"""
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        
        # Clean both outputs
        clean_stdout = self.clean_output_text(stdout)
        clean_stderr = self.clean_output_text(stderr)
        
        # Check if stderr should be completely suppressed (keychain messages)
        if clean_stderr and self.should_suppress_output(stderr, stdout):
            # Suppress keychain messages entirely
            clean_stderr = ""
        
        # Determine if remaining stderr is actually an error
        is_error = self.is_actual_error(stderr, stdout, result.returncode) if clean_stderr else False
        
        # Send appropriate output
        if clean_stdout:
            self.output_queue.put(('shell_output', clean_stdout))
        
        if clean_stderr:
            if is_error:
                self.output_queue.put(('shell_error', clean_stderr))
            else:
                # Treat as informational output - use shell_output with Info prefix
                self.output_queue.put(('shell_output', f"[INFO] {clean_stderr}"))
        
        # Only report return code errors if there's no other output
        if result.returncode != 0 and not clean_stdout and not clean_stderr:
            self.output_queue.put(('shell_error', f"Command exited with code {result.returncode}"))
    
    def requires_stdin(self, command):
        """Check if command typically requires stdin input"""
        stdin_commands = [
            'sudo', 'su', 'passwd', 'mysql', 'psql', 'sqlite3',
            'python', 'python3', 'node', 'ruby', 'perl',
            'cat', 'tee', 'sort', 'uniq', 'grep', 'awk', 'sed',
            'gpg', 'openssl', 'ssh-keygen'
        ]
        
        cmd_lower = command.lower().strip()
        
        # SSH commands might need password input if keys aren't working
        if cmd_lower.startswith('ssh'):
            return True  # Always check for SSH password prompts
        
        for stdin_cmd in stdin_commands:
            if cmd_lower.startswith(stdin_cmd):
                # Check for specific flags that don't require stdin
                if stdin_cmd in ['python', 'python3', 'node', 'ruby', 'perl']:
                    if ' -c ' in cmd_lower or '.py' in cmd_lower or '.js' in cmd_lower:
                        return False
                if stdin_cmd == 'cat' and len(cmd_lower.split()) > 1:
                    return False  # cat with filename doesn't need stdin
                return True
        return False
    
    def get_ssh_input(self, command):
        """Get SSH password/passphrase input from user via dialog"""
        ssh_dialog = tk.Toplevel(self.root)
        ssh_dialog.title("SSH Authentication Required")
        ssh_dialog.geometry("500x300")
        ssh_dialog.configure(bg='#000000')
        ssh_dialog.transient(self.root)
        ssh_dialog.grab_set()
        
        # Title
        title_label = tk.Label(ssh_dialog, 
                              text=f"SSH Authentication Required", 
                              font=self.get_terminal_font(14, 'bold'),
                              fg='#FF0000', bg='#000000')
        title_label.pack(pady=10)
        
        # Command info
        cmd_label = tk.Label(ssh_dialog, 
                            text=f"Command: {command}", 
                            font=self.get_terminal_font(11),
                            fg='#00FF00', bg='#000000',
                            wraplength=480)
        cmd_label.pack(pady=5)
        
        # Instructions
        instr_label = tk.Label(ssh_dialog, 
                              text="Enter password or passphrase:", 
                              font=self.get_terminal_font(11),
                              fg='#FFFF00', bg='#000000')
        instr_label.pack(pady=10)
        
        # Password entry (hidden)
        password_var = tk.StringVar()
        password_entry = tk.Entry(ssh_dialog, 
                                 textvariable=password_var,
                                 font=self.get_terminal_font(12),
                                 bg='#001100', fg='#00FF00',
                                 insertbackground='#00FF00',
                                 show='*',  # Hide password
                                 width=40)
        password_entry.pack(pady=10)
        
        # Result variable
        result = {'input': None, 'cancelled': True}
        
        def send_password():
            password = password_var.get()
            if password:
                result['input'] = password + '\n'  # Add newline for SSH
                result['cancelled'] = False
            ssh_dialog.destroy()
        
        def cancel_auth():
            result['cancelled'] = True
            ssh_dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(ssh_dialog, bg='#000000')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Authenticate", command=send_password,
                 font=self.get_terminal_font(11),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=cancel_auth,
                 font=self.get_terminal_font(11),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.LEFT, padx=10)
        
        # Bind Enter to authenticate
        def on_enter(event):
            send_password()
        
        password_entry.bind('<Return>', on_enter)
        password_entry.focus_set()
        
        # Center dialog
        ssh_dialog.update_idletasks()
        x = (ssh_dialog.winfo_screenwidth() // 2) - (ssh_dialog.winfo_width() // 2)
        y = (ssh_dialog.winfo_screenheight() // 2) - (ssh_dialog.winfo_height() // 2)
        ssh_dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        ssh_dialog.wait_window()
        
        return result['input'] if not result['cancelled'] else None
    
    def get_stdin_input(self, command):
        """Get stdin input from user via dialog"""
        stdin_dialog = tk.Toplevel(self.root)
        stdin_dialog.title("Standard Input Required")
        stdin_dialog.geometry("500x400")
        stdin_dialog.configure(bg='#000000')
        stdin_dialog.transient(self.root)
        stdin_dialog.grab_set()
        
        # Title
        title_label = tk.Label(stdin_dialog, 
                              text=f"Command requires input: {command}", 
                              font=self.get_terminal_font(12, 'bold'),
                              fg='#00FF00', bg='#000000',
                              wraplength=480)
        title_label.pack(pady=10)
        
        # Instructions
        instr_label = tk.Label(stdin_dialog, 
                              text="Enter input below (press Ctrl+D or click Send to finish):", 
                              font=self.get_terminal_font(10),
                              fg='#FFFF00', bg='#000000')
        instr_label.pack(pady=5)
        
        # Input text area
        input_frame = tk.Frame(stdin_dialog, bg='#000000')
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        input_text = tk.Text(input_frame, 
                            font=self.get_terminal_font(11),
                            bg='#001100', fg='#00FF00',
                            insertbackground='#00FF00',
                            wrap=tk.WORD)
        input_text.pack(fill=tk.BOTH, expand=True)
        
        # Result variable
        result = {'input': None, 'cancelled': True}
        
        def send_input():
            result['input'] = input_text.get(1.0, tk.END)
            result['cancelled'] = False
            stdin_dialog.destroy()
        
        def cancel_input():
            result['cancelled'] = True
            stdin_dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(stdin_dialog, bg='#000000')
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Send Input", command=send_input,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=cancel_input,
                 font=self.get_terminal_font(10),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.RIGHT, padx=5)
        
        # Bind Ctrl+D to send
        def ctrl_d(event):
            send_input()
        
        input_text.bind('<Control-d>', ctrl_d)
        input_text.focus_set()
        
        # Center dialog
        stdin_dialog.update_idletasks()
        x = (stdin_dialog.winfo_screenwidth() // 2) - (stdin_dialog.winfo_width() // 2)
        y = (stdin_dialog.winfo_screenheight() // 2) - (stdin_dialog.winfo_height() // 2)
        stdin_dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        stdin_dialog.wait_window()
        
        return result['input'] if not result['cancelled'] else None
    
    def is_interactive_command(self, command):
        """Check if command should stream output in real-time"""
        interactive_commands = [
            'ping', 'traceroute', 'telnet', 'nc', 'netcat',
            'tail -f', 'watch', 'top', 'htop', 'iotop',
            'tcpdump', 'wireshark', 'nmap'
        ]
        
        cmd_lower = command.lower().strip()
        
        # SSH is only interactive for certain cases
        if cmd_lower.startswith('ssh'):
            # Parse SSH command to find host and command
            ssh_parts = cmd_lower.split()
            if len(ssh_parts) < 2:
                return True  # Just 'ssh' - interactive
            
            # Skip flags and their arguments to find the host
            i = 1
            while i < len(ssh_parts):
                part = ssh_parts[i]
                if part.startswith('-'):
                    # This is a flag
                    if part in ['-p', '-i', '-l', '-o', '-F', '-J']:
                        # These flags take an argument, skip both flag and argument
                        i += 2
                    else:
                        # Other flags don't take arguments
                        i += 1
                else:
                    # This should be the host
                    # Check if there are more arguments after the host
                    if i + 1 < len(ssh_parts):
                        # There are arguments after the host - this is a command
                        return False
                    else:
                        # No arguments after host - interactive login
                        return True
            
            # If we get here, we didn't find a clear host - assume interactive
            return True
        
        # Check other interactive commands
        for interactive_cmd in interactive_commands:
            if cmd_lower.startswith(interactive_cmd):
                return True
        return False
    
    def setup_windows_ssh_agent(self):
        """Setup SSH agent for Windows PowerShell"""
        if self.platform != "windows" or self.use_wsl:
            return
        
        try:
            # Check if ssh-agent service is running
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Service ssh-agent'],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0 and 'Running' in result.stdout:
                self.add_message("SYSTEM", "Windows SSH Agent service is running", "system")
            else:
                # Try to start ssh-agent service
                self.add_message("SYSTEM", "Starting Windows SSH Agent service...", "system")
                start_result = subprocess.run(
                    ['powershell', '-Command', 'Start-Service ssh-agent'],
                    capture_output=True, text=True, timeout=10,
                    encoding='utf-8', errors='replace'
                )
                
                if start_result.returncode == 0:
                    self.add_message("SYSTEM", "SSH Agent service started successfully", "system")
                else:
                    self.add_message("SYSTEM", "Failed to start SSH Agent service. You may need to run as Administrator.", "system")
            
            # List loaded SSH keys
            keys_result = subprocess.run(
                ['ssh-add', '-l'],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            
            if keys_result.returncode == 0:
                self.add_message("SYSTEM", f"SSH Keys loaded:\n{keys_result.stdout.strip()}", "system")
            else:
                self.add_message("SYSTEM", "No SSH keys loaded. Use 'ssh-add' to add keys.", "system")
                
        except Exception as e:
            self.add_message("SYSTEM", f"Windows SSH Agent setup error: {str(e)}", "system")
    
    def debug_log(self, message):
        """Log debug message to debug window if enabled"""
        if self.debug_enabled and self.debug_text:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.debug_text.see(tk.END)
    
    def toggle_debug_window(self):
        """Toggle debug window visibility"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.create_debug_window()
        else:
            self.debug_window.destroy()
            self.debug_window = None
            self.debug_enabled = False
    
    def create_debug_window(self):
        """Create debug output window"""
        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("HAL Debug Console")
        self.debug_window.geometry("800x600")
        self.debug_window.configure(bg='#000000')
        
        # Title
        title_label = tk.Label(self.debug_window, text="HAL 9000 Debug Console", 
                              font=self.get_terminal_font(14, 'bold'),
                              fg='#FF0000', bg='#000000')
        title_label.pack(pady=5)
        
        # Debug text area with scrollbar
        text_frame = tk.Frame(self.debug_window, bg='#000000')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.debug_text = tk.Text(text_frame, 
                                 font=self.get_terminal_font(9),
                                 bg='#001100', fg='#00FF00',
                                 insertbackground='#00FF00',
                                 wrap=tk.WORD)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.debug_text.yview)
        self.debug_text.config(yscrollcommand=scrollbar.set)
        
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = tk.Frame(self.debug_window, bg='#000000')
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_frame, text="Clear", 
                 command=lambda: self.debug_text.delete(1.0, tk.END),
                 font=self.get_terminal_font(10),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Save Debug Log", 
                 command=self.save_debug_log,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        # SSH environment toggle
        ssh_env_var = tk.BooleanVar(value=self.enable_ssh_env_setup)
        ssh_env_check = tk.Checkbutton(button_frame, text="SSH Env Setup", 
                                      variable=ssh_env_var,
                                      font=self.get_terminal_font(10),
                                      fg='#FFFF00', bg='#000000',
                                      selectcolor='#000000',
                                      activeforeground='#FFFF00',
                                      activebackground='#000000')
        ssh_env_check.pack(side=tk.LEFT, padx=5)
        
        def on_ssh_env_toggle():
            self.enable_ssh_env_setup = ssh_env_var.get()
            status = "enabled" if self.enable_ssh_env_setup else "disabled"
            self.debug_log(f"SSH environment setup {status}")
        
        ssh_env_check.config(command=on_ssh_env_toggle)
        
        # Shell type selector for Windows
        if self.platform == "windows":
            tk.Label(button_frame, text="Shell:", 
                    font=self.get_terminal_font(10),
                    fg='#FFFF00', bg='#000000').pack(side=tk.RIGHT, padx=5)
            
            shell_var = tk.StringVar(value=self.windows_shell_type)
            shell_combo = ttk.Combobox(button_frame, textvariable=shell_var,
                                     values=["cmd", "powershell", "wsl"],
                                     state="readonly", width=10)
            shell_combo.pack(side=tk.RIGHT, padx=5)
            
            def on_shell_change(event):
                old_type = self.windows_shell_type
                self.windows_shell_type = shell_var.get()
                self.update_shell_selector_button()
                self.debug_log(f"Debug console: Shell type changed from {old_type} to {self.windows_shell_type}")
            
            shell_combo.bind('<<ComboboxSelected>>', on_shell_change)
        
        tk.Button(button_frame, text="Close", 
                 command=self.toggle_debug_window,
                 font=self.get_terminal_font(10),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.RIGHT, padx=5)
        
        # Enable debug logging
        self.debug_enabled = True
        
        # Initial debug message
        self.debug_log("Debug console initialized")
        self.debug_log(f"Platform: {self.platform}")
        self.debug_log(f"WSL enabled: {self.use_wsl}")
        if self.platform == "windows":
            self.debug_log(f"Windows shell type: {self.windows_shell_type}")
        
        # Handle window close
        def on_debug_close():
            self.debug_enabled = False
            self.debug_window.destroy()
            self.debug_window = None
        
        self.debug_window.protocol("WM_DELETE_WINDOW", on_debug_close)
    
    def save_debug_log(self):
        """Save debug log to file"""
        if not self.debug_text:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfilename=f"hal_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("HAL 9000 Debug Log\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(self.debug_text.get(1.0, tk.END))
                
                messagebox.showinfo("Debug Log", f"Debug log saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save debug log:\n{str(e)}")
    
    def show_shell_selector(self):
        """Show shell type selector popup menu (Windows only)"""
        if self.platform != "windows":
            return
        
        # Create popup menu
        popup = tk.Menu(self.root, tearoff=0, 
                       bg='#000000', fg='#00FF00',
                       activebackground='#003300', activeforeground='#00FF00',
                       font=self.get_terminal_font(10))
        
        # Shell type options
        shell_options = [
            ("Command Prompt (CMD)", "cmd"),
            ("PowerShell", "powershell"),
            ("Windows Subsystem for Linux (WSL)", "wsl")
        ]
        
        for display_name, shell_type in shell_options:
            # Mark current selection
            if shell_type == self.windows_shell_type:
                display_name = f"● {display_name}"
            else:
                display_name = f"   {display_name}"
            
            popup.add_command(
                label=display_name,
                command=lambda st=shell_type: self.select_shell_type(st)
            )
        
        # Show popup at button location
        try:
            x = self.shell_selector_btn.winfo_rootx()
            y = self.shell_selector_btn.winfo_rooty() + self.shell_selector_btn.winfo_height()
            popup.post(x, y)
        except:
            # Fallback to mouse position
            popup.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def select_shell_type(self, shell_type):
        """Select a specific shell type"""
        if self.platform != "windows":
            return
        
        old_type = self.windows_shell_type
        self.windows_shell_type = shell_type
        
        # Update button text
        self.update_shell_selector_button()
        
        # Add system message
        shell_names = {
            "cmd": "Command Prompt",
            "powershell": "PowerShell", 
            "wsl": "Windows Subsystem for Linux"
        }
        
        old_name = shell_names.get(old_type, old_type.upper())
        new_name = shell_names.get(shell_type, shell_type.upper())
        
        self.add_message("SYSTEM", f"Shell changed from {old_name} to {new_name}", "system")
        self.debug_log(f"Shell type changed from {old_type} to {shell_type}")
    
    def update_shell_selector_button(self):
        """Update shell selector button text to show current shell"""
        if self.platform != "windows" or not hasattr(self, 'shell_selector_btn'):
            return
        
        button_text = {
            "cmd": "CMD",
            "powershell": "PowerShell",
            "wsl": "WSL"
        }
        
        current_text = button_text.get(self.windows_shell_type, "CMD")
        self.shell_selector_btn.config(text=current_text)
    
    def cycle_shell_type(self):
        """Cycle through available shell types on Windows"""
        if self.platform != "windows":
            return
        
        shell_types = ["cmd", "powershell", "wsl"]
        current_index = shell_types.index(self.windows_shell_type)
        next_index = (current_index + 1) % len(shell_types)
        self.windows_shell_type = shell_types[next_index]
        
        # Update button text
        button_text = {
            "cmd": "CMD",
            "powershell": "PS",
            "wsl": "WSL"
        }
        self.shell_type_btn.config(text=button_text[self.windows_shell_type])
        
        # Add system message
        self.add_message("SYSTEM", f"Windows shell type changed to: {self.windows_shell_type.upper()}", "system")
        self.debug_log(f"Shell type cycled to: {self.windows_shell_type}")
    
    def check_ssh_agent_status(self):
        """Check and report SSH agent status for current shell type"""
        try:
            self.debug_log("Checking SSH agent status...")
            
            if self.use_wsl or (self.platform == "windows" and self.windows_shell_type == "wsl"):
                # WSL SSH agent check
                cmd = ['wsl', '--', 'bash', '-l', '-c', 
                       'echo "SSH_AUTH_SOCK: ${SSH_AUTH_SOCK:-not set}"; '
                       'echo "SSH_AGENT_PID: ${SSH_AGENT_PID:-not set}"; '
                       'if [ -n "$SSH_AUTH_SOCK" ] && [ -S "$SSH_AUTH_SOCK" ]; then '
                       'echo "Agent socket exists and is accessible"; '
                       'ssh-add -l 2>/dev/null && echo "Keys loaded successfully" || echo "No keys loaded or agent not responding"; '
                       'else echo "No working SSH agent socket found"; fi']
                       
            elif self.platform == "windows" and self.windows_shell_type == "powershell":
                # PowerShell SSH agent check
                cmd = ['powershell', '-Command', 
                       'Write-Host "SSH Agent Service Status:"; '
                       'Get-Service ssh-agent -ErrorAction SilentlyContinue | Select-Object Status; '
                       'Write-Host "SSH Keys:"; '
                       'ssh-add -l 2>$null; if ($LASTEXITCODE -eq 0) { Write-Host "Keys loaded" } else { Write-Host "No keys loaded" }']
                       
            else:
                # Native SSH agent check
                cmd = ['bash', '-c', 
                       'echo "SSH_AUTH_SOCK: ${SSH_AUTH_SOCK:-not set}"; '
                       'echo "SSH_AGENT_PID: ${SSH_AGENT_PID:-not set}"; '
                       'ssh-add -l 2>/dev/null && echo "Keys loaded successfully" || echo "No keys loaded or agent not responding"']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                                  encoding='utf-8', errors='replace')
            
            status_info = result.stdout.strip() if result.stdout else "No output"
            self.debug_log(f"SSH agent status: {status_info}")
            
            # Also add to main chat for user visibility
            self.add_message("SYSTEM", f"SSH Agent Status:\n{status_info}", "system")
            
        except Exception as e:
            error_msg = f"Error checking SSH agent status: {str(e)}"
            self.debug_log(error_msg)
            self.add_message("SYSTEM", error_msg, "system")
    
    def detect_windows_shell_capabilities(self):
        """Detect available shell capabilities on Windows"""
        if self.platform != "windows":
            return
        
        capabilities = []
        
        # Test PowerShell
        try:
            result = subprocess.run(['powershell', '-Command', 'echo "test"'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                capabilities.append("powershell")
        except:
            pass
        
        # Test WSL
        try:
            result = subprocess.run(['wsl', '--', 'echo', 'test'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                capabilities.append("wsl")
        except:
            pass
        
        # CMD is always available on Windows
        capabilities.append("cmd")
        
        self.debug_log(f"Windows shell capabilities detected: {capabilities}")
        
        # Set optimal default shell type based on capabilities
        if "powershell" in capabilities:
            self.windows_shell_type = "powershell"  # PowerShell is best for SSH
            self.debug_log("Default shell type set to PowerShell (optimal for SSH)")
        elif "wsl" in capabilities:
            self.windows_shell_type = "wsl"  # WSL is second best
            self.debug_log("Default shell type set to WSL")
        else:
            self.windows_shell_type = "cmd"  # CMD as fallback
            self.debug_log("Default shell type set to CMD (fallback)")
        
        # Update button if it exists
        self.update_shell_selector_button()
    
    def prepare_ssh_environment(self, command):
        """Prepare environment specifically for SSH commands"""
        if not self.enable_ssh_env_setup or not command.lower().startswith('ssh'):
            return command
        
        self.debug_log(f"Preparing SSH environment for: {command}")
        
        # Add SSH-specific environment setup
        ssh_env_setup = []
        
        if self.use_wsl or (self.platform == "windows" and self.windows_shell_type == "wsl"):
            # WSL SSH environment - try to inherit existing agent first
            self.debug_log("Using WSL SSH agent - attempting to inherit existing session")
            ssh_env_setup = [
                # First, check if we already have a working SSH agent
                'if ssh-add -l >/dev/null 2>&1; then echo "Using existing SSH agent with loaded keys"; else echo "No working SSH agent found, setting up new one"; if ! ssh-add -l >/dev/null 2>&1; then eval $(ssh-agent -s) >/dev/null 2>&1; fi; ssh-add -l >/dev/null 2>&1 || (ssh-add ~/.ssh/id_rsa >/dev/null 2>&1 || ssh-add ~/.ssh/id_ed25519 >/dev/null 2>&1 || true); fi'
            ]
        elif self.platform == "windows" and self.windows_shell_type == "powershell":
            # Windows PowerShell SSH environment - use Windows SSH agent service
            self.debug_log("Using Windows PowerShell SSH agent")
            ssh_env_setup = [
                # Check if keys are already loaded first
                'if ((ssh-add -l 2>$null | Measure-Object -Line).Lines -gt 0) { Write-Host "Using existing SSH keys" } else { Write-Host "Loading SSH keys"; if ((Get-Service ssh-agent -ErrorAction SilentlyContinue).Status -ne "Running") { Start-Service ssh-agent -ErrorAction SilentlyContinue }; ssh-add ~/.ssh/id_rsa 2>$null; ssh-add ~/.ssh/id_ed25519 2>$null }'
            ]
        elif self.platform == "windows":
            # Windows CMD - limited SSH support
            self.debug_log("Using Windows CMD (limited SSH support)")
            ssh_env_setup = []  # No special setup for CMD
        else:
            # macOS/Linux SSH environment - inherit existing agent
            self.debug_log("Using native Unix SSH agent")
            ssh_env_setup = [
                # Check for existing agent first
                'if ssh-add -l >/dev/null 2>&1; then echo "Using existing SSH agent"; else echo "Setting up SSH agent"; if ! ssh-add -l >/dev/null 2>&1; then eval $(ssh-agent -s) >/dev/null 2>&1; fi; ssh-add -l >/dev/null 2>&1 || (ssh-add ~/.ssh/id_rsa >/dev/null 2>&1 || ssh-add ~/.ssh/id_ed25519 >/dev/null 2>&1 || true); fi'
            ]
        
        if ssh_env_setup:
            if self.platform == "windows" and self.windows_shell_type == "powershell":
                # PowerShell syntax
                env_cmd = '; '.join(ssh_env_setup)
                enhanced_cmd = f'{env_cmd}; {command}'
            else:
                # Bash syntax - ensure proper joining
                env_cmd = ' && '.join(ssh_env_setup)
                enhanced_cmd = f'{env_cmd} && {command}'
            
            self.debug_log(f"Enhanced SSH command: {enhanced_cmd}")
            return enhanced_cmd
        
        self.debug_log("No SSH environment setup needed")
        return command
    
    def stream_command_output(self, cmd_list, command, stdin_input=None):
        """Stream command output in real-time for interactive commands"""
        try:
            # Start the process
            process = subprocess.Popen(
                cmd_list,
                stdin=subprocess.PIPE if stdin_input else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Keep stderr separate for better error handling
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Add initial message
            self.output_queue.put(('shell_output', f"Starting: {command}"))
            if stdin_input:
                self.output_queue.put(('shell_output', "Input provided via dialog"))
            self.output_queue.put(('shell_output', "Press Ctrl+C to stop (close HAL to terminate)"))
            self.output_queue.put(('shell_output', "=" * 50))
            
            # Send stdin if provided
            if stdin_input:
                process.stdin.write(stdin_input)
                process.stdin.close()
            
            # Stream output line by line
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Clean and send each line, suppress keychain messages
                clean_line = self.clean_output_text(line.rstrip())
                if clean_line and not self.should_suppress_output(line, ""):
                    self.output_queue.put(('shell_output', clean_line))
            
            # Wait for process to complete and get stderr
            return_code = process.wait()
            stderr_output = process.stderr.read()
            
            # Send completion message
            self.output_queue.put(('shell_output', "=" * 50))
            
            # Handle stderr
            if stderr_output:
                clean_stderr = self.clean_output_text(stderr_output.strip())
                if clean_stderr and not self.should_suppress_output(stderr_output, ""):
                    if self.is_actual_error(stderr_output, "", return_code):
                        self.output_queue.put(('shell_error', clean_stderr))
                    else:
                        self.output_queue.put(('shell_output', f"[INFO] {clean_stderr}"))
            
            # Report completion status
            if return_code == 0:
                self.output_queue.put(('shell_output', f"Command completed successfully"))
            else:
                self.output_queue.put(('shell_error', f"Command exited with code {return_code}"))
                
        except Exception as e:
            self.output_queue.put(('shell_error', f'Streaming error: {str(e)}'))
    
    def process_shell_command(self, command):
        """Process shell command with proper environment inheritance and stdin handling"""
        try:
            self.debug_log(f"Processing shell command: {command}")
            
            # Handle cd command specially to track working directory
            if command.strip().startswith('cd '):
                self.handle_cd_command(command.strip())
                return
            
            # Check if command requires stdin (including SSH password prompts)
            stdin_input = None
            if self.requires_stdin(command):
                self.debug_log("Command may require stdin input")
                
                # For SSH commands, provide a more specific prompt
                if command.lower().startswith('ssh'):
                    stdin_input = self.get_ssh_input(command)
                else:
                    stdin_input = self.get_stdin_input(command)
                    
                if stdin_input is None:  # User cancelled
                    self.output_queue.put(('shell_error', 'Command cancelled by user'))
                    return
            
            # Prepare command based on platform with full environment
            if self.use_wsl or (self.platform == "windows" and self.windows_shell_type == "wsl"):
                # WSL execution
                self.debug_log("Using WSL execution")
                enhanced_cmd = self.prepare_ssh_environment(command)
                full_cmd = f'cd "{self.shell_cwd}" && {enhanced_cmd}'
                cmd_list = ['wsl', '--', 'bash', '-l', '-c', full_cmd]
                
            elif self.platform == "windows" and self.windows_shell_type == "powershell":
                # PowerShell execution
                self.debug_log("Using PowerShell execution")
                enhanced_cmd = self.prepare_ssh_environment(command)
                full_cmd = f'cd "{self.shell_cwd}"; {enhanced_cmd}'
                cmd_list = ['powershell', '-Command', full_cmd]
                
            elif self.platform == "windows":
                # Windows CMD execution
                self.debug_log("Using Windows CMD execution")
                enhanced_cmd = self.prepare_ssh_environment(command)
                full_cmd = f'cd /d "{self.shell_cwd}" && {enhanced_cmd}'
                cmd_list = ['cmd', '/c', full_cmd]
                
            else:  # macOS and Linux
                # Unix shell execution with login shell for environment
                self.debug_log("Using Unix shell execution")
                enhanced_cmd = self.prepare_ssh_environment(command)
                full_cmd = f'cd "{self.shell_cwd}" && {enhanced_cmd}'
                cmd_list = ['/bin/bash', '-l', '-c', full_cmd]
            
            self.debug_log(f"Command list: {cmd_list}")
            
            # Check if this is an interactive command that should stream
            if self.is_interactive_command(command):
                self.debug_log("Using streaming execution for interactive command")
                # Use streaming for real-time output
                self.stream_command_output(cmd_list, command, stdin_input)
            else:
                self.debug_log("Using regular execution for non-interactive command")
                # Use regular execution for quick commands
                result = subprocess.run(
                    cmd_list,
                    input=stdin_input,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )
                
                self.debug_log(f"Command completed with return code: {result.returncode}")
                
                # Process output with improved error detection
                self.process_command_output(result)
                
        except subprocess.TimeoutExpired:
            self.debug_log("Command timed out")
            self.output_queue.put(('shell_error', 'Command timed out'))
        except Exception as e:
            self.debug_log(f"Error executing command: {str(e)}")
            self.output_queue.put(('shell_error', f'Error executing command: {str(e)}'))
    
    def handle_cd_command(self, command):
        """Handle cd command for directory tracking with proper environment"""
        try:
            path = command[3:].strip()  # Remove 'cd '
            if not path:
                # cd with no arguments goes to home
                if self.use_wsl:
                    # Get WSL home with login shell
                    result = subprocess.run(
                        ['wsl', '--', 'bash', '-l', '-c', 'echo $HOME'],
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
                    # Test path in WSL with login shell for proper environment
                    test_cmd = f'cd "{self.shell_cwd}" && cd "{path}" && pwd'
                    result = subprocess.run(
                        ['wsl', '--', 'bash', '-l', '-c', test_cmd],
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
                elif msg_type == 'shell_info':
                    clean_message = self.clean_output_text(message)
                    self.add_message("INFO", clean_message, "shell_info")
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
        
        # Reset status based on current mode
        if self.current_mode == "Q":
            self.connection_status.config(text="Q CLI: READY")
        else:
            self.connection_status.config(text="SHELL: READY")
        
        self.start_hal_greeting()
    
    def manage_ssh_keys(self):
        """Open SSH key management dialog"""
        ssh_dialog = tk.Toplevel(self.root)
        ssh_dialog.title("SSH Key Management")
        ssh_dialog.geometry("600x400")
        ssh_dialog.configure(bg='#000000')
        
        # Make dialog modal
        ssh_dialog.transient(self.root)
        ssh_dialog.grab_set()
        
        # Title
        title_label = tk.Label(ssh_dialog, text="SSH Key Management", 
                              font=self.get_terminal_font(14, 'bold'),
                              fg='#00FF00', bg='#000000')
        title_label.pack(pady=10)
        
        # Current keys display
        keys_frame = tk.Frame(ssh_dialog, bg='#000000')
        keys_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(keys_frame, text="Currently Loaded SSH Keys:", 
                font=self.get_terminal_font(11, 'bold'),
                fg='#00FF00', bg='#000000').pack(anchor=tk.W)
        
        self.keys_text = tk.Text(keys_frame, height=8, 
                                font=self.get_terminal_font(10),
                                bg='#001100', fg='#00FF00',
                                insertbackground='#00FF00')
        self.keys_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(ssh_dialog, bg='#000000')
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Refresh keys button
        tk.Button(buttons_frame, text="Refresh Keys", 
                 command=self.refresh_ssh_keys,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        # Check agent status button
        tk.Button(buttons_frame, text="Agent Status", 
                 command=self.check_ssh_agent_status,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        # Add key button
        tk.Button(buttons_frame, text="Add Key", 
                 command=self.add_ssh_key,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        # Generate key button
        tk.Button(buttons_frame, text="Generate Key", 
                 command=self.generate_ssh_key,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        # Close button
        tk.Button(buttons_frame, text="Close", 
                 command=ssh_dialog.destroy,
                 font=self.get_terminal_font(10),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.RIGHT, padx=5)
        
        # Load current keys
        self.refresh_ssh_keys()
        
        # Center dialog
        ssh_dialog.update_idletasks()
        x = (ssh_dialog.winfo_screenwidth() // 2) - (ssh_dialog.winfo_width() // 2)
        y = (ssh_dialog.winfo_screenheight() // 2) - (ssh_dialog.winfo_height() // 2)
        ssh_dialog.geometry(f"+{x}+{y}")
    
    def refresh_ssh_keys(self):
        """Refresh the SSH keys display"""
        try:
            if self.use_wsl or (self.platform == "windows" and self.windows_shell_type == "wsl"):
                # WSL SSH agent
                self.debug_log("Refreshing SSH keys from WSL agent")
                cmd = ['wsl', '--', 'bash', '-l', '-c', 'ssh-add -l 2>/dev/null || echo "No SSH keys loaded"']
            elif self.platform == "windows" and self.windows_shell_type == "powershell":
                # Windows PowerShell SSH agent
                self.debug_log("Refreshing SSH keys from Windows PowerShell agent")
                cmd = ['powershell', '-Command', 'ssh-add -l 2>$null; if ($LASTEXITCODE -ne 0) { echo "No SSH keys loaded" }']
            else:
                # Native SSH agent
                self.debug_log("Refreshing SSH keys from native agent")
                cmd = ['ssh-add', '-l']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                                  encoding='utf-8', errors='replace')
            
            self.keys_text.delete(1.0, tk.END)
            if result.returncode == 0:
                self.keys_text.insert(tk.END, result.stdout.strip())
            else:
                self.keys_text.insert(tk.END, "No SSH keys loaded or SSH agent not running")
                
        except Exception as e:
            self.debug_log(f"Error refreshing SSH keys: {str(e)}")
            self.keys_text.delete(1.0, tk.END)
            self.keys_text.insert(tk.END, f"Error checking SSH keys: {str(e)}")
    
    def add_ssh_key(self):
        """Add an SSH key via file dialog"""
        try:
            # Ask user to select SSH key file
            key_file = filedialog.askopenfilename(
                title="Select SSH Private Key",
                initialdir=os.path.expanduser("~/.ssh"),
                filetypes=[("SSH Keys", "id_*"), ("All files", "*.*")]
            )
            
            if key_file:
                self.debug_log(f"Adding SSH key: {key_file}")
                
                if self.use_wsl or (self.platform == "windows" and self.windows_shell_type == "wsl"):
                    # WSL SSH agent - convert Windows path to WSL path if needed
                    if self.platform == "windows":
                        wsl_path = key_file.replace('\\', '/').replace('C:', '/mnt/c')
                    else:
                        wsl_path = key_file
                    cmd = ['wsl', '--', 'bash', '-l', '-c', f'ssh-add "{wsl_path}"']
                elif self.platform == "windows" and self.windows_shell_type == "powershell":
                    # Windows PowerShell SSH agent
                    cmd = ['powershell', '-Command', f'ssh-add "{key_file}"']
                else:
                    # Native SSH agent
                    cmd = ['ssh-add', key_file]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                      encoding='utf-8', errors='replace')
                
                if result.returncode == 0:
                    self.debug_log(f"SSH key added successfully: {key_file}")
                    messagebox.showinfo("SSH Key", f"SSH key added successfully:\n{key_file}")
                    self.refresh_ssh_keys()
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    self.debug_log(f"Failed to add SSH key: {error_msg}")
                    messagebox.showerror("SSH Key Error", f"Failed to add SSH key:\n{error_msg}")
                    
        except Exception as e:
            self.debug_log(f"Error adding SSH key: {str(e)}")
            messagebox.showerror("SSH Key Error", f"Error adding SSH key:\n{str(e)}")
    
    def generate_ssh_key(self):
        """Generate a new SSH key pair"""
        # Open input dialog for key details
        key_dialog = tk.Toplevel(self.root)
        key_dialog.title("Generate SSH Key")
        key_dialog.geometry("400x300")
        key_dialog.configure(bg='#000000')
        key_dialog.transient(self.root)
        key_dialog.grab_set()
        
        # Key name
        tk.Label(key_dialog, text="Key Name:", 
                font=self.get_terminal_font(11),
                fg='#00FF00', bg='#000000').pack(pady=5)
        
        name_var = tk.StringVar(value="id_rsa")
        name_entry = tk.Entry(key_dialog, textvariable=name_var,
                             font=self.get_terminal_font(11),
                             bg='#001100', fg='#00FF00',
                             insertbackground='#00FF00')
        name_entry.pack(pady=5)
        
        # Email
        tk.Label(key_dialog, text="Email (optional):", 
                font=self.get_terminal_font(11),
                fg='#00FF00', bg='#000000').pack(pady=5)
        
        email_var = tk.StringVar()
        email_entry = tk.Entry(key_dialog, textvariable=email_var,
                              font=self.get_terminal_font(11),
                              bg='#001100', fg='#00FF00',
                              insertbackground='#00FF00')
        email_entry.pack(pady=5)
        
        # Key type
        tk.Label(key_dialog, text="Key Type:", 
                font=self.get_terminal_font(11),
                fg='#00FF00', bg='#000000').pack(pady=5)
        
        type_var = tk.StringVar(value="rsa")
        type_combo = ttk.Combobox(key_dialog, textvariable=type_var,
                                 values=["rsa", "ed25519", "ecdsa"],
                                 state="readonly")
        type_combo.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(key_dialog, bg='#000000')
        button_frame.pack(pady=20)
        
        def generate_key():
            try:
                key_name = name_var.get().strip()
                email = email_var.get().strip()
                key_type = type_var.get()
                
                if not key_name:
                    messagebox.showerror("Error", "Key name is required")
                    return
                
                # Build ssh-keygen command
                ssh_dir = os.path.expanduser("~/.ssh")
                key_path = os.path.join(ssh_dir, key_name)
                
                cmd_parts = ['ssh-keygen', '-t', key_type, '-f', key_path]
                if email:
                    cmd_parts.extend(['-C', email])
                cmd_parts.append('-N')  # No passphrase for simplicity
                cmd_parts.append('')
                
                if self.use_wsl:
                    wsl_path = key_path.replace('\\', '/').replace('C:', '/mnt/c')
                    cmd_str = f'ssh-keygen -t {key_type} -f "{wsl_path}" -C "{email}" -N ""'
                    cmd = ['wsl', '--', 'bash', '-l', '-c', cmd_str]
                else:
                    cmd = cmd_parts
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                      encoding='utf-8', errors='replace')
                
                if result.returncode == 0:
                    messagebox.showinfo("SSH Key Generated", 
                                      f"SSH key pair generated successfully:\n{key_path}\n{key_path}.pub")
                    key_dialog.destroy()
                    self.refresh_ssh_keys()
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    messagebox.showerror("Generation Error", f"Failed to generate SSH key:\n{error_msg}")
                    
            except Exception as e:
                messagebox.showerror("Generation Error", f"Error generating SSH key:\n{str(e)}")
        
        tk.Button(button_frame, text="Generate", command=generate_key,
                 font=self.get_terminal_font(10),
                 bg='#003300', fg='#00FF00',
                 activebackground='#005500', activeforeground='#00FF00').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=key_dialog.destroy,
                 font=self.get_terminal_font(10),
                 bg='#330000', fg='#FF0000',
                 activebackground='#550000', activeforeground='#FF0000').pack(side=tk.LEFT, padx=5)
    
    def choose_directory(self):
        """Choose working directory for Q CLI and Shell operations"""
        try:
            # Open directory chooser dialog
            new_dir = filedialog.askdirectory(
                title="Choose Working Directory",
                initialdir=self.shell_cwd
            )
            
            if new_dir:  # User selected a directory
                old_dir = self.shell_cwd
                self.shell_cwd = new_dir
                
                # Update mode label if in shell mode
                if self.current_mode == "SHELL":
                    shell_type = "WSL" if self.use_wsl else "SHELL"
                    cwd_display = self.format_shell_cwd()
                    self.mode_label.config(text=f"Mode: {shell_type} ({cwd_display})")
                
                # Add system message
                self.add_message("SYSTEM", f"Working directory changed:\nFrom: {old_dir}\nTo: {new_dir}", "system")
                
        except Exception as e:
            self.add_message("SYSTEM", f"Error choosing directory: {str(e)}", "system")
    
    def safe_exit(self):
        """Exit HAL with option to save log"""
        if self.conversation_history:
            # Ask if user wants to save log before exiting
            response = messagebox.askyesnocancel(
                "Exit HAL 9000",
                "Do you want to save the conversation log before exiting?\n\n"
                "Yes: Save log and exit\n"
                "No: Exit without saving\n"
                "Cancel: Don't exit"
            )
            
            if response is None:  # Cancel
                return
            elif response:  # Yes - save log
                try:
                    self.save_log()
                    # If save was successful (user didn't cancel), exit
                    self.add_message("SYSTEM", "Log saved. HAL 9000 shutting down...", "system")
                    self.root.after(1000, self.root.quit)  # Delay to show message
                except:
                    # If save was cancelled, don't exit
                    return
            else:  # No - exit without saving
                self.add_message("SYSTEM", "HAL 9000 shutting down...", "system")
                self.root.after(1000, self.root.quit)  # Delay to show message
        else:
            # No conversation history, just exit
            self.add_message("SYSTEM", "HAL 9000 shutting down...", "system")
            self.root.after(1000, self.root.quit)
    
    def save_log(self):
        """Save conversation log to file"""
        if not self.conversation_history:
            messagebox.showinfo("HAL", "No conversation to save.")
            return False
        
        # Ask user where to save
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfilename=f"hal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not filename:  # User cancelled
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("HAL 9000 - System Interface Log\n")
                f.write("=" * 40 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Platform: {self.platform.title()}")
                if self.use_wsl:
                    f.write(" (WSL)")
                f.write("\n" + "=" * 40 + "\n\n")
                
                for entry in self.conversation_history:
                    mode_indicator = f"[{entry.get('mode', 'Q')}] "
                    f.write(f"{mode_indicator}[{entry['timestamp']}] {entry['sender']}: {entry['message']}\n\n")
            
            messagebox.showinfo("HAL", f"Log saved successfully to:\n{filename}")
            return True
            
        except Exception as e:
            messagebox.showerror("HAL", f"Error saving log:\n{str(e)}")
            return False
    
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
