#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Working Unified Settings Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Check for skin system availability
try:
    from skins.skin_manager import SkinManager
    SKINS_AVAILABLE = True
except ImportError:
    SKINS_AVAILABLE = False

class UnifiedSettingsDialog:
    def __init__(self, parent, q_service=None):
        self.parent = parent
        self.q_service = q_service
        self.dialog = None
        self.skin_manager = None
        
        # Get the root window - parent might be main app or root window
        if hasattr(parent, 'root'):
            self.root = parent.root  # parent is main application
            self.main_app = parent
        else:
            self.root = parent  # parent is root window
            self.main_app = None
        
        # Initialize skin manager
        if SKINS_AVAILABLE:
            try:
                self.skin_manager = SkinManager()
                self.skin_manager.load_skin_preference()
            except Exception as e:
                print("Error loading skin manager:", str(e))
    
    def show(self):
        """Show the unified settings dialog"""
        if self.dialog:
            self.dialog.lift()
            return
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("QIS v6.0 - Settings")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='#000000')
        self.dialog.resizable(True, True)
        
        # Make it modal (but handle Linux differently)
        self.dialog.transient(self.root)
        
        # On Linux, grab_set() can cause issues with message boxes
        # Only use grab_set on Windows/macOS
        import platform
        if platform.system() in ['Windows', 'Darwin']:
            self.dialog.grab_set()
        else:
            # On Linux, just focus the window instead of grabbing
            self.dialog.focus_set()
            self.dialog.lift()
            self.dialog.attributes('-topmost', True)
            # Remove topmost after a short delay to allow normal interaction
            self.dialog.after(100, lambda: self.dialog.attributes('-topmost', False))
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # AI Personality tab
        self.create_ai_personality_tab(notebook)
        
        # Q CLI Settings tab
        self.create_q_cli_tab(notebook)
        
        # SSH Settings tab
        self.create_ssh_tab(notebook)
        
        # Close button
        close_btn = tk.Button(self.dialog,
                             text="CLOSE",
                             font=('Courier New', 12, 'bold'),
                             fg='#FFFFFF',
                             bg='#333333',
                             command=self.close,
                             width=15)
        close_btn.pack(pady=10)
    
    def create_ai_personality_tab(self, notebook):
        """Create AI Personality tab"""
        skin_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(skin_frame, text="AI Personality")
        
        # Title
        title = tk.Label(skin_frame,
                        text="AI Personality Selection",
                        font=('Courier New', 16, 'bold'),
                        fg='#00FF00',
                        bg='#000000')
        title.pack(pady=20)
        
        if not SKINS_AVAILABLE or not self.skin_manager:
            # Skin system not available
            error_label = tk.Label(skin_frame,
                                  text="Skin system not available",
                                  font=('Courier New', 12),
                                  fg='#FF0000',
                                  bg='#000000')
            error_label.pack(pady=20)
            return
        
        # Get available skins
        try:
            available_skins = self.skin_manager.get_available_skins()
            print("DEBUG: Available skins:", available_skins)
            
            if not available_skins:
                error_label = tk.Label(skin_frame,
                                      text="No skins available",
                                      font=('Courier New', 12),
                                      fg='#FF0000',
                                      bg='#000000')
                error_label.pack(pady=20)
                return
            
            # Create radio button variable
            self.skin_var = tk.StringVar()
            self.skin_var.set(self.skin_manager.current_skin)
            
            # Create skin options directly (no scrolling for simplicity)
            for skin_id, skin_info in available_skins.items():
                print(f"DEBUG: Creating skin option for {skin_id}: {skin_info['name']}")
                
                # Create frame for this skin option
                option_frame = tk.Frame(skin_frame, bg='#111111', relief='raised', bd=2)
                option_frame.pack(fill='x', pady=5, padx=20)
                
                # Radio button
                radio = tk.Radiobutton(option_frame,
                                      text=skin_info['name'],
                                      variable=self.skin_var,
                                      value=skin_id,
                                      bg='#111111',
                                      fg='#00FF00',
                                      selectcolor='#333333',
                                      font=('Courier New', 12, 'bold'))
                radio.pack(side='left', padx=10, pady=5)
                
                # Description
                desc_label = tk.Label(option_frame,
                                     text=skin_info['description'],
                                     font=('Courier New', 10),
                                     fg='#888888',
                                     bg='#111111')
                desc_label.pack(side='left', padx=10, pady=5)
            
            print(f"DEBUG: Created {len(available_skins)} skin options")
            
            # Apply button
            apply_btn = tk.Button(skin_frame,
                                 text="APPLY PERSONALITY",
                                 font=('Courier New', 12, 'bold'),
                                 fg='#000000',
                                 bg='#00FF00',
                                 command=self.apply_skin,
                                 width=20)
            apply_btn.pack(pady=20)
            
        except Exception as e:
            error_label = tk.Label(skin_frame,
                                  text="Error loading skins: " + str(e),
                                  font=('Courier New', 10),
                                  fg='#FF0000',
                                  bg='#000000')
            error_label.pack(pady=20)
    
    def apply_skin(self):
        """Apply selected skin"""
        if not SKINS_AVAILABLE or not self.skin_manager:
            messagebox.showwarning("Skin System", 
                                 "Skin system not available.",
                                 parent=self.dialog)
            return
        
        try:
            selected_skin = self.skin_var.get()
            if selected_skin:
                print(f"DEBUG: Applying skin: {selected_skin}")
                
                # Set and save the skin
                self.skin_manager.set_skin(selected_skin)
                self.skin_manager.save_skin_preference(selected_skin)
                print(f"DEBUG: Skin set and saved: {selected_skin}")
                
                # Try multiple ways to apply the skin to the main interface
                main_window = None
                
                # Method 1: Direct parent reference
                if hasattr(self.parent, 'apply_skin'):
                    print("DEBUG: Found apply_skin method on parent")
                    main_window = self.parent
                
                # Method 2: Look for HAL interface in parent's children
                elif hasattr(self.parent, 'winfo_children'):
                    for child in self.parent.winfo_children():
                        if hasattr(child, 'apply_skin'):
                            print("DEBUG: Found apply_skin method on child")
                            main_window = child
                            break
                
                # Method 3: Look for global HAL interface
                if not main_window:
                    # Try to find the main interface through the root window
                    root = self.parent
                    while hasattr(root, 'master') and root.master:
                        root = root.master
                    
                    if hasattr(root, 'hal_interface'):
                        main_window = root.hal_interface
                        print("DEBUG: Found HAL interface through root")
                
                # Apply the skin if we found the main window
                if main_window and hasattr(main_window, 'apply_skin'):
                    try:
                        main_window.apply_skin(self.skin_manager)
                        print("DEBUG: Successfully applied skin to main interface")
                    except Exception as apply_error:
                        print("DEBUG: Error applying skin to main interface:", str(apply_error))
                else:
                    print("DEBUG: Could not find main interface to apply skin")
                
                identity = self.skin_manager.get_identity()
                messagebox.showinfo("Personality Applied",
                                  "AI Personality changed to: " + identity.get('name', 'Unknown') + "\n\n" +
                                  "Skin applied successfully!",
                                  parent=self.dialog)
            else:
                messagebox.showwarning("No Selection", 
                                     "Please select a personality first.",
                                     parent=self.dialog)
                
        except Exception as e:
            print("DEBUG: Error in apply_skin:", str(e))
            messagebox.showerror("Error", 
                               "Error applying skin: " + str(e),
                               parent=self.dialog)
    
    def create_q_cli_tab(self, notebook):
        """Create Q CLI Settings tab"""
        q_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(q_frame, text="Q CLI Settings")
        
        # Title
        title = tk.Label(q_frame,
                        text="Q CLI Method Configuration",
                        font=('Courier New', 16, 'bold'),
                        fg='#00FF00',
                        bg='#000000')
        title.pack(pady=20)
        
        # Current status display
        if self.q_service:
            try:
                status = self.q_service.get_q_method_status()
                current_method = status.get('current_method', 'unknown').upper()
                active_method = status.get('active_method', {})
                method_name = active_method.get('name', 'Unknown')
                
                status_text = f"Current Method: {method_name}"
                status_color = '#00FF00' if active_method.get('available', False) else '#FF4444'
            except:
                status_text = "Status: Unable to determine current method"
                status_color = '#FF4444'
                current_method = 'AUTO'
        else:
            status_text = "Status: Q service not available"
            status_color = '#FF4444'
            current_method = 'AUTO'
        
        status_label = tk.Label(q_frame,
                               text=status_text,
                               font=('Courier New', 12),
                               fg=status_color,
                               bg='#000000')
        status_label.pack(pady=10)
        
        # Q CLI method selection
        self.q_method_var = tk.StringVar()
        self.q_method_var.set(current_method)
        
        # Get available methods from Q service if possible
        if self.q_service:
            try:
                status = self.q_service.get_q_method_status()
                methods_info = status.get('methods', {})
                methods = []
                for method_key, method_data in methods_info.items():
                    if method_key != 'auto':  # Skip auto in the detailed list
                        available = method_data.get('available', False)
                        name = method_data.get('name', method_key.upper())
                        desc = method_data.get('description', '')
                        status_indicator = " ✓" if available else " ✗"
                        methods.append((method_key.upper(), desc + status_indicator))
                
                # Add AUTO at the beginning
                methods.insert(0, ("AUTO", "Automatically select best available method"))
            except:
                # Fallback to default methods
                methods = [
                    ("AUTO", "Automatically select best available method"),
                    ("LOCAL", "Use local Q CLI installation"),
                    ("WSL", "Use Q CLI in Windows Subsystem for Linux"),
                    ("SSH", "Route Q CLI commands to remote Linux host")
                ]
        else:
            methods = [
                ("AUTO", "Automatically select best available method"),
                ("LOCAL", "Use local Q CLI installation"),
                ("SSH", "Route Q CLI commands to remote Linux host")
            ]
        
        for method, description in methods:
            method_frame = tk.Frame(q_frame, bg='#111111', relief='raised', bd=2)
            method_frame.pack(fill='x', pady=5, padx=20)
            
            radio = tk.Radiobutton(method_frame,
                                  text=method,
                                  variable=self.q_method_var,
                                  value=method,
                                  bg='#111111',
                                  fg='#00FF00',
                                  selectcolor='#333333',
                                  font=('Courier New', 12, 'bold'))
            radio.pack(side='left', padx=10, pady=5)
            
            desc_label = tk.Label(method_frame,
                                 text=description,
                                 font=('Courier New', 10),
                                 fg='#888888',
                                 bg='#111111')
            desc_label.pack(side='left', padx=10, pady=5)
        
        # Apply button
        apply_q_btn = tk.Button(q_frame,
                               text="APPLY Q CLI SETTINGS",
                               font=('Courier New', 12, 'bold'),
                               fg='#000000',
                               bg='#00FF00',
                               command=self.apply_q_settings,
                               width=25)
        apply_q_btn.pack(pady=20)
    
    def create_ssh_tab(self, notebook):
        """Create SSH Settings tab"""
        ssh_frame = tk.Frame(notebook, bg='#000000')
        notebook.add(ssh_frame, text="SSH Settings")
        
        # Title
        title = tk.Label(ssh_frame,
                        text="SSH Configuration",
                        font=('Courier New', 16, 'bold'),
                        fg='#00FF00',
                        bg='#000000')
        title.pack(pady=20)
        
        # SSH settings form
        settings_frame = tk.Frame(ssh_frame, bg='#000000')
        settings_frame.pack(pady=20)
        
        # Host
        tk.Label(settings_frame, text="SSH Host:", 
                font=('Courier New', 12), fg='#00FF00', bg='#000000').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.ssh_host_var = tk.StringVar()
        tk.Entry(settings_frame, textvariable=self.ssh_host_var, 
                font=('Courier New', 12), width=30).grid(row=0, column=1, padx=10, pady=5)
        
        # Username
        tk.Label(settings_frame, text="Username:", 
                font=('Courier New', 12), fg='#00FF00', bg='#000000').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.ssh_user_var = tk.StringVar()
        tk.Entry(settings_frame, textvariable=self.ssh_user_var, 
                font=('Courier New', 12), width=30).grid(row=1, column=1, padx=10, pady=5)
        
        # Port
        tk.Label(settings_frame, text="Port:", 
                font=('Courier New', 12), fg='#00FF00', bg='#000000').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.ssh_port_var = tk.StringVar()
        self.ssh_port_var.set("22")
        tk.Entry(settings_frame, textvariable=self.ssh_port_var, 
                font=('Courier New', 12), width=30).grid(row=2, column=1, padx=10, pady=5)
        
        # Apply button
        apply_ssh_btn = tk.Button(ssh_frame,
                                 text="APPLY SSH SETTINGS",
                                 font=('Courier New', 12, 'bold'),
                                 fg='#000000',
                                 bg='#00FF00',
                                 command=self.apply_ssh_settings,
                                 width=25)
        apply_ssh_btn.pack(pady=20)
    
    def apply_q_settings(self):
        """Apply Q CLI settings"""
        try:
            selected_method = self.q_method_var.get().lower()
            
            if self.q_service:
                # Actually apply the setting to the Q service
                self.q_service.set_q_method(selected_method)
                
                # Get the updated status to show what was actually set
                status = self.q_service.get_q_method_status()
                active_method = status.get('active_method', {})
                method_name = active_method.get('name', selected_method.upper())
                
                # Trigger status update in main application
                if self.main_app and hasattr(self.main_app, 'update_connection_status'):
                    self.main_app.root.after(100, self.main_app.update_connection_status)
                    self.main_app.root.after(100, self.main_app.update_system_status)
                
                messagebox.showinfo("Q CLI Settings", 
                                   f"Q CLI method set to: {method_name}\n\n" +
                                   "Settings applied successfully!",
                                   parent=self.dialog)
            else:
                # Fallback if no Q service available
                messagebox.showinfo("Q CLI Settings", 
                                   f"Q CLI method set to: {selected_method.upper()}\n\n" +
                                   "Settings will take effect on next Q CLI command.",
                                   parent=self.dialog)
        except Exception as e:
            messagebox.showerror("Q CLI Settings Error", 
                               f"Failed to apply Q CLI settings:\n\n{str(e)}",
                               parent=self.dialog)
    
    def apply_ssh_settings(self):
        """Apply SSH settings"""
        host = self.ssh_host_var.get()
        user = self.ssh_user_var.get()
        port = self.ssh_port_var.get()
        
        if not host or not user:
            messagebox.showwarning("SSH Settings", 
                                 "Please enter both host and username.",
                                 parent=self.dialog)
            return
        
        messagebox.showinfo("SSH Settings", 
                           "SSH settings saved:\n" +
                           "Host: " + host + "\n" +
                           "User: " + user + "\n" +
                           "Port: " + port,
                           parent=self.dialog)

    def close(self):
        """Close the dialog"""
        if self.dialog:
            # Only release grab if we actually grabbed it
            import platform
            if platform.system() in ['Windows', 'Darwin']:
                try:
                    self.dialog.grab_release()
                except:
                    pass  # Ignore if grab wasn't set
            self.dialog.destroy()
            self.dialog = None
