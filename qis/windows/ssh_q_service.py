#!/usr/bin/env python3
"""
SSH Q Service for HAL 9000
Routes Q CLI commands to a remote Linux box via SSH
"""

import subprocess
import json
import os
import time
from datetime import datetime

class SSHQService:
    """Q service that routes commands to remote Linux box via SSH"""
    
    def __init__(self, ssh_config=None):
        """
        Initialize SSH Q service
        
        ssh_config should contain:
        {
            'host': 'remote-server.com',
            'user': 'username',
            'port': 22,
            'key_file': '/path/to/private/key',  # optional
            'password': 'password'  # optional, not recommended
        }
        """
        self.ssh_config = ssh_config or self._load_ssh_config()
        self.connection_tested = False
        self.last_test_time = 0
        
    def _load_ssh_config(self):
        """Load SSH configuration from file or environment"""
        config_file = 'ssh_q_config.json'
        
        # Try to load from config file
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading SSH config: {e}")
        
        # Try to load from environment variables
        env_config = {
            'host': os.environ.get('HAL_SSH_HOST'),
            'user': os.environ.get('HAL_SSH_USER'),
            'port': int(os.environ.get('HAL_SSH_PORT', '22')),
            'key_file': os.environ.get('HAL_SSH_KEY'),
            'password': os.environ.get('HAL_SSH_PASSWORD')
        }
        
        if env_config['host'] and env_config['user']:
            return env_config
        
        # Return default/empty config
        return {
            'host': None,
            'user': None,
            'port': 22,
            'key_file': None,
            'password': None
        }
    
    def save_ssh_config(self, config):
        """Save SSH configuration to file"""
        try:
            with open('ssh_q_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            self.ssh_config = config
            self.connection_tested = False  # Re-test connection
            return True
        except Exception as e:
            print(f"Error saving SSH config: {e}")
            return False
    
    def test_ssh_connection(self):
        """Test SSH connection to remote host"""
        if not self.ssh_config.get('host') or not self.ssh_config.get('user'):
            return False, "SSH host or user not configured"
        
        # Don't test too frequently
        current_time = time.time()
        if self.connection_tested and (current_time - self.last_test_time) < 30:
            return True, "Connection OK (cached)"
        
        try:
            cmd = self._build_ssh_command(['echo', 'SSH_TEST_OK'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            self.last_test_time = current_time
            
            if result.returncode == 0 and 'SSH_TEST_OK' in result.stdout:
                self.connection_tested = True
                return True, "SSH connection successful"
            else:
                self.connection_tested = False
                return False, f"SSH test failed: {result.stderr or 'Unknown error'}"
                
        except subprocess.TimeoutExpired:
            self.connection_tested = False
            return False, "SSH connection timeout"
        except Exception as e:
            self.connection_tested = False
            return False, f"SSH connection error: {str(e)}"
    
    def _build_ssh_command(self, remote_command):
        """Build SSH command with proper authentication"""
        ssh_cmd = ['ssh']
        
        # Add port if specified
        if self.ssh_config.get('port') and self.ssh_config['port'] != 22:
            ssh_cmd.extend(['-p', str(self.ssh_config['port'])])
        
        # Add key file if specified
        if self.ssh_config.get('key_file'):
            ssh_cmd.extend(['-i', self.ssh_config['key_file']])
        
        # Add SSH options for non-interactive use
        ssh_cmd.extend([
            '-o', 'BatchMode=yes',  # No password prompts
            '-o', 'StrictHostKeyChecking=no',  # Accept new host keys
            '-o', 'ConnectTimeout=10'
        ])
        
        # Add user@host
        ssh_cmd.append(f"{self.ssh_config['user']}@{self.ssh_config['host']}")
        
        # Add remote command
        if isinstance(remote_command, list):
            ssh_cmd.extend(remote_command)
        else:
            ssh_cmd.append(remote_command)
        
        return ssh_cmd
    
    def test_remote_q_cli(self):
        """Test if Q CLI is available on remote host"""
        try:
            cmd = self._build_ssh_command(['q', '--version'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return True, f"Remote Q CLI available: {result.stdout.strip()}"
            else:
                return False, f"Remote Q CLI not found: {result.stderr or 'Not installed'}"
                
        except Exception as e:
            return False, f"Error testing remote Q CLI: {str(e)}"
    
    def is_available(self):
        """Check if SSH Q service is available"""
        if not self.ssh_config.get('host') or not self.ssh_config.get('user'):
            return False
        
        # Test connection if not recently tested
        success, _ = self.test_ssh_connection()
        return success
    
    def query(self, question, context=None):
        """Execute Q CLI query on remote host via SSH"""
        if not self.is_available():
            raise Exception("SSH connection not available")
        
        try:
            # Escape the question for shell execution
            escaped_question = question.replace('"', '\\"').replace('$', '\\$')
            
            # Build remote Q CLI command with auto-approval
            remote_cmd = f'echo "y" | q chat "{escaped_question}"'
            
            # Execute via SSH
            ssh_cmd = self._build_ssh_command(['bash', '-c', remote_cmd])
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                # Try without auto-approval
                remote_cmd = f'q chat "{escaped_question}"'
                ssh_cmd = self._build_ssh_command(['bash', '-c', remote_cmd])
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=45)
                
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                else:
                    error_msg = result.stderr.strip() if result.stderr else "No response from remote Q CLI"
                    raise Exception(f"Remote Q CLI error: {error_msg}")
                    
        except subprocess.TimeoutExpired:
            raise Exception("Remote Q CLI request timed out")
        except Exception as e:
            raise Exception(f"SSH Q CLI execution failed: {str(e)}")
    
    def get_status(self):
        """Get SSH Q service status"""
        ssh_ok, ssh_msg = self.test_ssh_connection()
        q_ok, q_msg = self.test_remote_q_cli() if ssh_ok else (False, "SSH not available")
        
        return {
            'available': ssh_ok and q_ok,
            'ssh_status': ssh_msg,
            'q_cli_status': q_msg,
            'method': 'SSH Remote Q CLI',
            'host': self.ssh_config.get('host'),
            'user': self.ssh_config.get('user')
        }

class SSHConfigDialog:
    """Simple SSH configuration dialog"""
    
    def __init__(self, parent, current_config=None):
        self.parent = parent
        self.config = current_config or {}
        self.result = None
        
    def show(self):
        """Show SSH configuration dialog"""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            # Create dialog window
            dialog = tk.Toplevel(self.parent)
            dialog.title("SSH Q CLI Configuration")
            dialog.geometry("400x300")
            dialog.configure(bg='#000000')
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"400x300+{x}+{y}")
            
            # Create form
            main_frame = tk.Frame(dialog, bg='#000000')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = tk.Label(main_frame, text="SSH Q CLI Configuration", 
                                 bg='#000000', fg='#FF0000', 
                                 font=('Courier New', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Form fields
            fields = {}
            
            # Host
            tk.Label(main_frame, text="Remote Host:", bg='#000000', fg='#00FF00').pack(anchor=tk.W)
            fields['host'] = tk.Entry(main_frame, bg='#001100', fg='#00FF00', width=40)
            fields['host'].pack(fill=tk.X, pady=(0, 10))
            fields['host'].insert(0, self.config.get('host', ''))
            
            # User
            tk.Label(main_frame, text="Username:", bg='#000000', fg='#00FF00').pack(anchor=tk.W)
            fields['user'] = tk.Entry(main_frame, bg='#001100', fg='#00FF00', width=40)
            fields['user'].pack(fill=tk.X, pady=(0, 10))
            fields['user'].insert(0, self.config.get('user', ''))
            
            # Port
            tk.Label(main_frame, text="Port (default 22):", bg='#000000', fg='#00FF00').pack(anchor=tk.W)
            fields['port'] = tk.Entry(main_frame, bg='#001100', fg='#00FF00', width=40)
            fields['port'].pack(fill=tk.X, pady=(0, 10))
            fields['port'].insert(0, str(self.config.get('port', 22)))
            
            # Key file
            tk.Label(main_frame, text="Private Key File (optional):", bg='#000000', fg='#00FF00').pack(anchor=tk.W)
            fields['key_file'] = tk.Entry(main_frame, bg='#001100', fg='#00FF00', width=40)
            fields['key_file'].pack(fill=tk.X, pady=(0, 20))
            fields['key_file'].insert(0, self.config.get('key_file', ''))
            
            # Buttons
            button_frame = tk.Frame(main_frame, bg='#000000')
            button_frame.pack(fill=tk.X)
            
            def save_config():
                try:
                    config = {
                        'host': fields['host'].get().strip(),
                        'user': fields['user'].get().strip(),
                        'port': int(fields['port'].get().strip() or 22),
                        'key_file': fields['key_file'].get().strip() or None
                    }
                    
                    if not config['host'] or not config['user']:
                        messagebox.showerror("Error", "Host and Username are required")
                        return
                    
                    self.result = config
                    dialog.destroy()
                    
                except ValueError:
                    messagebox.showerror("Error", "Port must be a number")
                except Exception as e:
                    messagebox.showerror("Error", f"Configuration error: {str(e)}")
            
            def cancel():
                self.result = None
                dialog.destroy()
            
            tk.Button(button_frame, text="Save", command=save_config,
                     bg='#003300', fg='#00FF00', font=('Courier New', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            tk.Button(button_frame, text="Cancel", command=cancel,
                     bg='#330000', fg='#FF0000', font=('Courier New', 10, 'bold')).pack(side=tk.LEFT)
            
            # Wait for dialog to close
            dialog.wait_window()
            return self.result
            
        except ImportError:
            # Fallback for environments without tkinter
            print("SSH Configuration (text mode):")
            config = {}
            config['host'] = input("Remote Host: ").strip()
            config['user'] = input("Username: ").strip()
            port_input = input("Port (default 22): ").strip()
            config['port'] = int(port_input) if port_input else 22
            config['key_file'] = input("Private Key File (optional): ").strip() or None
            
            return config if config['host'] and config['user'] else None
