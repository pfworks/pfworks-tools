#!/usr/bin/env python3
"""
QIS v6.0 - Cross-Platform AI Personality Interface System
Universal version supporting Windows, Linux, and macOS
Automatically detects platform and adapts Q CLI integration and shell behavior
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import queue
import json
import time
import os
import sys
import platform
from datetime import datetime

# Import SSH Q service
from ssh_q_service import SSHQService, SSHConfigDialog
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

class CrossPlatformEnvironmentDetector:
    """Cross-platform environment detector for Windows, Linux, and macOS"""
    
    def __init__(self):
        try:
            print("Initializing environment detector...")
            self.platform_name = platform.system().lower()
            self.is_windows = self.platform_name == 'windows'
            self.is_linux = self.platform_name == 'linux'
            self.is_macos = self.platform_name == 'darwin'
            print(f"Platform detected: {self.platform_name}")
            
            print("Detecting WSL...")
            self.is_wsl = self._detect_wsl()
            print(f"WSL detected: {self.is_wsl}")
            
            print("Finding Q CLI...")
            self.q_cli_path = self._find_q_cli()
            print(f"Q CLI path: {self.q_cli_path}")
            print("Environment detector initialization complete")
        except Exception as e:
            print(f"Error in environment detector: {e}")
            import traceback
            traceback.print_exc()
            # Set safe defaults
            self.platform_name = platform.system().lower()
            self.is_windows = self.platform_name == 'windows'
            self.is_linux = self.platform_name == 'linux'
            self.is_macos = self.platform_name == 'darwin'
            self.is_wsl = False
            self.q_cli_path = None
    
    def _detect_wsl(self):
        """Detect if running in Windows Subsystem for Linux"""
        if not self.is_linux:
            return False
        
        try:
            # Check for WSL indicators
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info or 'wsl' in version_info
        except:
            return False
    
    def _find_q_cli(self):
        """Find Q CLI binary across platforms"""
        # Common Q CLI binary names
        q_names = ['q', 'q.exe'] if self.is_windows else ['q']
        
        # Check PATH first
        for q_name in q_names:
            try:
                result = subprocess.run(['which' if not self.is_windows else 'where', q_name], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except:
                pass
        
        # Platform-specific locations
        if self.is_windows:
            # Windows-specific Q CLI locations
            possible_paths = [
                os.path.expanduser("~\\AppData\\Local\\Programs\\Amazon Q\\q.exe"),
                "C:\\Program Files\\Amazon Q\\q.exe",
                "C:\\Program Files (x86)\\Amazon Q\\q.exe"
            ]
        else:
            # Unix-like systems (Linux/macOS)
            possible_paths = [
                "/usr/local/bin/q",
                "/usr/bin/q",
                os.path.expanduser("~/bin/q"),
                os.path.expanduser("~/.local/bin/q")
            ]
        
        # Check each possible path
        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    def _get_wsl_distro(self):
        """Get WSL distribution name"""
        if not self.is_wsl:
            return None
        
        try:
            # Try to get WSL distro name from environment
            wsl_distro = os.environ.get('WSL_DISTRO_NAME')
            if wsl_distro:
                return wsl_distro
            
            # Fallback: try to detect from /etc/os-release
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('NAME='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        
        return "WSL"
    
    def get_environment_info(self):
        """Get comprehensive environment information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'is_windows': self.is_windows,
            'is_linux': self.is_linux,
            'is_macos': self.is_macos,
            'is_wsl': self.is_wsl,
            'wsl_distro': self._get_wsl_distro() if self.is_wsl else None,
            'q_cli_path': self.q_cli_path,
            'q_cli_available': self.q_cli_path is not None,
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'shell': self._get_default_shell()
        }
    
    def _get_default_shell(self):
        """Get the default shell for the platform"""
        if self.is_windows and not self.is_wsl:
            return 'powershell'
        else:
            # Linux, macOS, or WSL
            return os.environ.get('SHELL', '/bin/bash').split('/')[-1]

class CrossPlatformQService:
    """Cross-platform Q service with local Q CLI and SSH routing support"""
    
    def __init__(self):
        try:
            print("Initializing CrossPlatformQService...")
            self.env_detector = CrossPlatformEnvironmentDetector()
            print("Environment detector created")
            
            self.env_info = self.env_detector.get_environment_info()
            print(f"Environment info obtained: {self.env_info['platform']}")
            
            # Initialize SSH Q service
            self.ssh_q_service = SSHQService()
            print("SSH Q service initialized")
            
            # Q CLI method selection: "local", "ssh" (WSL handled as local on Linux)
            self.q_method = "auto"  # auto, local, ssh
            self.use_ssh = False  # Legacy compatibility
            self._determine_q_method()
            print("Q method determined")
            print("CrossPlatformQService initialization complete")
        except Exception as e:
            print(f"Error in CrossPlatformQService.__init__: {e}")
            import traceback
            traceback.print_exc()
            # Create minimal fallback
            self.env_info = {
                'platform': platform.system(),
                'is_windows': platform.system() == 'Windows',
                'is_linux': platform.system() == 'Linux', 
                'is_macos': platform.system() == 'Darwin',
                'is_wsl': False,
                'wsl_distro': None,
                'q_cli_path': None,
                'q_cli_available': False,
                'shell': 'bash'
            }
            self.q_method = "auto"
            self.use_ssh = False
            try:
                self.ssh_q_service = SSHQService()
            except:
                self.ssh_q_service = None
        
    def _determine_q_method(self):
        """Determine which Q CLI method to use based on user preference and availability"""
        if self.q_method == "auto":
            # Auto-detect best available method
            if self.env_info['q_cli_available']:
                self.q_method = "local"
                self.use_ssh = False
            elif self.env_info['is_windows'] and self._check_wsl_q_available():
                self.q_method = "wsl"
                self.use_ssh = False
            elif self.ssh_q_service.is_available():
                self.q_method = "ssh"
                self.use_ssh = True
            else:
                self.q_method = "local"  # Default to local even if not available
                self.use_ssh = False
        else:
            # Use user-specified method
            if self.q_method == "ssh":
                self.use_ssh = True
            else:
                self.use_ssh = False
    
    def _check_wsl_q_cli(self):
        """Check if Q CLI is available in WSL environment"""
        try:
            # First check if WSL is available at all
            import subprocess
            try:
                # Try subprocess.run first (Python 3.5+)
                if hasattr(subprocess, 'run'):
                    result = subprocess.run(['wsl', '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    wsl_available = result.returncode == 0
                else:
                    # Fallback for older Python versions
                    proc = subprocess.Popen(['wsl', '--version'], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    wsl_available = proc.returncode == 0
                
                if not wsl_available:
                    return False
                
                # Method 1: Try with login shell (loads full environment)
                if hasattr(subprocess, 'run'):
                    result = subprocess.run(['wsl', 'bash', '-l', '-c', 'q --version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return True
                else:
                    proc = subprocess.Popen(['wsl', 'bash', '-l', '-c', 'q --version'], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    if proc.returncode == 0:
                        return True
                
                # Method 2: Try with login shell which command
                if hasattr(subprocess, 'run'):
                    result = subprocess.run(['wsl', 'bash', '-l', '-c', 'which q'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and result.stdout.strip():
                        q_path = result.stdout.strip()
                        # Test if it works
                        test_result = subprocess.run(['wsl', q_path, '--version'], 
                                                   capture_output=True, text=True, timeout=10)
                        if test_result.returncode == 0:
                            return True
                else:
                    proc = subprocess.Popen(['wsl', 'bash', '-l', '-c', 'which q'], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    if proc.returncode == 0 and stdout.strip():
                        q_path = stdout.strip()
                        # Test if it works
                        test_proc = subprocess.Popen(['wsl', q_path, '--version'], 
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        test_stdout, test_stderr = test_proc.communicate()
                        if test_proc.returncode == 0:
                            return True
                
                # Method 3: Search common installation paths
                # Get username first
                username = "ubuntu"  # default
                if hasattr(subprocess, 'run'):
                    result = subprocess.run(['wsl', 'whoami'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        username = result.stdout.strip()
                else:
                    proc = subprocess.Popen(['wsl', 'whoami'], 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    if proc.returncode == 0:
                        username = stdout.strip()
                
                common_paths = [
                    '/usr/local/bin/q',
                    '/usr/bin/q',
                    '/bin/q',
                    '/home/' + username + '/.local/bin/q',
                    '/home/' + username + '/bin/q',
                    '/home/' + username + '/.cargo/bin/q',
                    '/snap/bin/q'
                ]
                
                for path in common_paths:
                    if hasattr(subprocess, 'run'):
                        result = subprocess.run(['wsl', 'test', '-f', path], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            # Test if it works
                            test_result = subprocess.run(['wsl', path, '--version'], 
                                                       capture_output=True, text=True, timeout=10)
                            if test_result.returncode == 0:
                                return True
                    else:
                        proc = subprocess.Popen(['wsl', 'test', '-f', path], 
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        if proc.returncode == 0:
                            # Test if it works
                            test_proc = subprocess.Popen(['wsl', path, '--version'], 
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            test_stdout, test_stderr = test_proc.communicate()
                            if test_proc.returncode == 0:
                                return True
                
                return False
                
            except OSError:
                # WSL command not found (not on Windows or WSL not installed)
                return False
            
        except Exception as e:
            return False
    
    def _get_wsl_username(self):
        """Get the current WSL username"""
        try:
            if hasattr(subprocess, 'run'):
                result = subprocess.run(['wsl', 'whoami'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            else:
                proc = subprocess.Popen(['wsl', 'whoami'], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                if proc.returncode == 0:
                    return stdout.strip()
        except:
            pass
        return 'ubuntu'  # Default fallback
    
    def set_q_method(self, method):
        """Set Q CLI method: 'auto', 'local', 'wsl', 'ssh'"""
        self.q_method = method
        self._determine_q_method()
        return self.get_q_method_status()
    
    def get_q_method_status(self):
        """Get current Q CLI method and availability"""
        env_info = self.env_info
        
        # Define methods based on platform
        methods = {
            'auto': {
                'available': True,
                'name': 'Auto-Detect',
                'description': 'Automatically select best available method'
            },
            'local': {
                'available': env_info['q_cli_available'],
                'name': 'Local Q CLI',
                'description': self._get_local_q_description()
            },
            'ssh': {
                'available': self.ssh_q_service.is_available(),
                'name': 'SSH Remote Q CLI',
                'description': 'Q CLI on remote Linux host'
            }
        }
        
        # Add WSL option only on Windows
        if env_info['is_windows']:
            methods['wsl'] = {
                'available': self._check_wsl_q_available(),
                'name': 'WSL Q CLI',
                'description': 'Q CLI in Windows Subsystem for Linux'
            }
        
        # Get active method info safely
        active_method = methods.get(self.q_method, {
            'available': False,
            'name': 'Unknown Method',
            'description': 'Method not recognized'
        })
        
        return {
            'current_method': self.q_method,
            'methods': methods,
            'active_method': active_method
        }
    
    def _get_local_q_description(self):
        """Get description for local Q CLI based on platform"""
        env_info = self.env_info
        if env_info['is_windows'] and not env_info['is_wsl']:
            return 'Windows native Q CLI'
        elif env_info['is_wsl']:
            return 'Q CLI in WSL environment'
        elif env_info['is_macos']:
            return 'macOS native Q CLI'
        else:
            return 'Linux native Q CLI'
    
    def _check_wsl_q_available(self):
        """Check if WSL Q CLI is available (Windows only)"""
        if not self.env_info['is_windows']:
            return False
        
        try:
            # Check if WSL is available
            result = subprocess.run(['wsl', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Check if Q CLI exists in WSL
            result = subprocess.run(['wsl', 'which', 'q'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False
    
    def configure_ssh(self, parent_window=None):
        """Configure SSH Q service"""
        try:
            dialog = SSHConfigDialog(parent_window, self.ssh_q_service.ssh_config)
            config = dialog.show()
            
            if config:
                success = self.ssh_q_service.save_ssh_config(config)
                if success:
                    self._determine_q_method()  # Re-evaluate Q method
                    return True, "SSH configuration saved successfully"
                else:
                    return False, "Failed to save SSH configuration"
            else:
                return False, "SSH configuration cancelled"
                
        except Exception as e:
            return False, "SSH configuration error: " + str(e)
    
    def is_available(self):
        """Check if any Q CLI method is available"""
        if self.use_ssh:
            return self.ssh_q_service.is_available()
        else:
            return self.env_info['q_cli_available']
    
    def query(self, question, context=None):
        """Query Q CLI with Local/WSL/SSH routing based on selected method"""
        if self.q_method == "ssh":
            # Use SSH routing
            return self.ssh_q_service.query(question, context)
        elif self.q_method == "wsl":
            # Use WSL Q CLI
            return self._query_wsl_q_cli(question, context)
        else:
            # Use local Q CLI (default)
            if not self.env_info['q_cli_available']:
                raise Exception("Local Q CLI not available on this system")
            
            q_path = self.env_info['q_cli_path']
            
            try:
                # Windows native execution with proper encoding and hidden window
                if hasattr(subprocess, 'run'):
                    # Prepare subprocess arguments for Windows
                    subprocess_kwargs = {
                        'input': 'y\n',
                        'capture_output': True,
                        'text': True,
                        'timeout': 30,
                        'encoding': 'utf-8',
                        'errors': 'replace'
                    }
                    
                    # Add Windows-specific flags to hide terminal window
                    if self.env_info['is_windows'] and not self.env_info['is_wsl']:
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        subprocess_kwargs['startupinfo'] = startupinfo
                        subprocess_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                    
                    result = subprocess.run([q_path, 'chat', question], **subprocess_kwargs)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        # Strip ANSI escape codes from output
                        clean_output = self._strip_ansi_codes(result.stdout.strip())
                        return clean_output
                    else:
                        # Try without auto-approval
                        subprocess_kwargs['input'] = None  # Remove input for second try
                        result = subprocess.run([q_path, 'chat', question], **subprocess_kwargs)
                        
                        if result.returncode == 0 and result.stdout.strip():
                            # Strip ANSI escape codes from output
                            clean_output = self._strip_ansi_codes(result.stdout.strip())
                            return clean_output
                        else:
                            raise Exception("Local Q CLI error: " + str(result.stderr or 'Unknown error'))
                else:
                    # Fallback for older Python with manual encoding handling
                    popen_kwargs = {
                        'stdin': subprocess.PIPE,
                        'stdout': subprocess.PIPE,
                        'stderr': subprocess.PIPE
                    }
                    
                    # Add Windows-specific flags to hide terminal window
                    if self.env_info['is_windows'] and not self.env_info['is_wsl']:
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        popen_kwargs['startupinfo'] = startupinfo
                        popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                    
                    proc = subprocess.Popen([q_path, 'chat', question], **popen_kwargs)
                    stdout_bytes, stderr_bytes = proc.communicate(input=b'y\n')
                    
                    # Decode with UTF-8, replacing problematic characters
                    try:
                        stdout = stdout_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        stdout = stdout_bytes.decode('utf-8', errors='replace')
                    
                    try:
                        stderr = stderr_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        stderr = stderr_bytes.decode('utf-8', errors='replace')
                    
                    if proc.returncode == 0 and stdout.strip():
                        # Strip ANSI escape codes from output
                        clean_output = self._strip_ansi_codes(stdout.strip())
                        return clean_output
                    else:
                        # Try without auto-approval
                        popen_kwargs['stdin'] = None  # Remove stdin for second try
                        proc = subprocess.Popen([q_path, 'chat', question], **popen_kwargs)
                        stdout_bytes, stderr_bytes = proc.communicate()
                        
                        # Decode with UTF-8, replacing problematic characters
                        try:
                            stdout = stdout_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            stdout = stdout_bytes.decode('utf-8', errors='replace')
                        
                        try:
                            stderr = stderr_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            stderr = stderr_bytes.decode('utf-8', errors='replace')
                        
                        if proc.returncode == 0 and stdout.strip():
                            # Strip ANSI escape codes from output
                            clean_output = self._strip_ansi_codes(stdout.strip())
                            return clean_output
                        else:
                            raise Exception("Local Q CLI error: " + str(stderr or 'Unknown error'))
                        
            except Exception as e:
                if "timed out" in str(e).lower():
                    raise Exception("Local Q CLI request timed out")
                else:
                    raise Exception("Local Q CLI execution failed: " + str(e))
    
    def _strip_ansi_codes(self, text):
        """Strip ANSI escape codes from text"""
        import re
        # Pattern to match ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _query_wsl_q_cli(self, question, context=None):
        """Query Q CLI in WSL environment"""
        try:
            # WSL-specific command execution with login shell
            escaped_question = question.replace('"', '\\"')
            
            # Use login shell (-l) to load full environment including PATH
            cmd = ['wsl', 'bash', '-l', '-c', 'echo "y" | q chat "' + escaped_question + '"']
            
            # Use appropriate subprocess method with proper encoding
            if hasattr(subprocess, 'run'):
                # Prepare subprocess arguments
                subprocess_kwargs = {
                    'capture_output': True,
                    'text': True,
                    'timeout': 30,
                    'encoding': 'utf-8',
                    'errors': 'replace'
                }
                
                # Add Windows-specific flags to hide terminal window
                if self.env_info['is_windows']:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    subprocess_kwargs['startupinfo'] = startupinfo
                    subprocess_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                result = subprocess.run(cmd, **subprocess_kwargs)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Strip ANSI escape codes from output
                    clean_output = self._strip_ansi_codes(result.stdout.strip())
                    return clean_output
                else:
                    # Try without auto-approval using login shell
                    cmd = ['wsl', 'bash', '-l', '-c', 'q chat "' + escaped_question + '"']
                    result = subprocess.run(cmd, **subprocess_kwargs)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        # Strip ANSI escape codes from output
                        clean_output = self._strip_ansi_codes(result.stdout.strip())
                        return clean_output
                    else:
                        raise Exception("WSL Q CLI error: " + str(result.stderr or 'Unknown error'))
            else:
                # Fallback for older Python - handle encoding manually
                popen_kwargs = {
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.PIPE
                }
                
                # Add Windows-specific flags to hide terminal window
                if self.env_info['is_windows']:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    popen_kwargs['startupinfo'] = startupinfo
                    popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                proc = subprocess.Popen(cmd, **popen_kwargs)
                stdout_bytes, stderr_bytes = proc.communicate()
                
                # Decode with UTF-8, replacing problematic characters
                try:
                    stdout = stdout_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    stdout = stdout_bytes.decode('utf-8', errors='replace')
                
                try:
                    stderr = stderr_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    stderr = stderr_bytes.decode('utf-8', errors='replace')
                
                if proc.returncode == 0 and stdout.strip():
                    # Strip ANSI escape codes from output
                    clean_output = self._strip_ansi_codes(stdout.strip())
                    return clean_output
                else:
                    # Try without auto-approval using login shell
                    cmd = ['wsl', 'bash', '-l', '-c', 'q chat "' + escaped_question + '"']
                    proc = subprocess.Popen(cmd, **popen_kwargs)
                    stdout_bytes, stderr_bytes = proc.communicate()
                    
                    # Decode with UTF-8, replacing problematic characters
                    try:
                        stdout = stdout_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        stdout = stdout_bytes.decode('utf-8', errors='replace')
                    
                    try:
                        stderr = stderr_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        stderr = stderr_bytes.decode('utf-8', errors='replace')
                    
                    if proc.returncode == 0 and stdout.strip():
                        # Strip ANSI escape codes from output
                        clean_output = self._strip_ansi_codes(stdout.strip())
                        return clean_output
                    else:
                        raise Exception("WSL Q CLI error: " + str(stderr or 'Unknown error'))
                    
        except Exception as e:
            if "timed out" in str(e).lower():
                raise Exception("WSL Q CLI request timed out")
            else:
                raise Exception("WSL Q CLI execution failed: " + str(e))
    
    def get_status(self):
        """Get Q service status based on selected method"""
        if self.q_method == "ssh":
            ssh_status = self.ssh_q_service.get_status()
            host = ssh_status.get('host', 'unknown')
            if host is None:
                host = 'unknown'
            return {
                'available': ssh_status['available'],
                'method': "SSH Remote Q CLI (" + str(host) + ")",
                'environment': self.env_info,
                'ssh_details': ssh_status,
                'q_method': self.q_method
            }
        elif self.q_method == "wsl":
            try:
                wsl_available = self._check_wsl_q_available()
            except Exception:
                wsl_available = False
            
            wsl_distro = self.env_info.get('wsl_distro', 'unknown')
            if wsl_distro is None:
                wsl_distro = 'unknown'
            
            return {
                'available': wsl_available,
                'method': "WSL Q CLI (" + str(wsl_distro) + ")",
                'environment': self.env_info,
                'q_method': self.q_method
            }
        else:
            # Local Q CLI
            local_description = self._get_local_q_description()
            return {
                'available': self.env_info['q_cli_available'],
                'method': local_description if self.env_info['q_cli_available'] else None,
                'environment': self.env_info,
                'q_method': self.q_method
            }

class QMethodConfigDialog:
    """Q CLI Method Configuration Dialog"""
    
    def __init__(self, parent, q_service):
        self.parent = parent
        self.q_service = q_service
        self.result = None
        
    def show(self):
        """Show Q CLI method configuration dialog"""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            # Create dialog window
            dialog = tk.Toplevel(self.parent)
            dialog.title("Q CLI Method Configuration")
            dialog.geometry("500x400")
            dialog.configure(bg='#000000')
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry("500x400+" + str(x) + "+" + str(y))
            
            # Create main frame
            main_frame = tk.Frame(dialog, bg='#000000')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = tk.Label(main_frame, text="Q CLI Method Selection", 
                                 bg='#000000', fg='#FF0000', 
                                 font=('Courier New', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Get method status
            method_status = self.q_service.get_q_method_status()
            current_method = method_status['current_method']
            methods = method_status['methods']
            
            # Method selection
            self.selected_method = tk.StringVar(value=current_method)
            
            # Auto method
            auto_frame = tk.Frame(main_frame, bg='#000000')
            auto_frame.pack(fill=tk.X, pady=5)
            
            tk.Radiobutton(auto_frame, text="AUTO - Automatically select best available method",
                          variable=self.selected_method, value="auto",
                          bg='#000000', fg='#FFFF00', selectcolor='#333300',
                          font=('Courier New', 10, 'bold')).pack(anchor=tk.W)
            
            # Local Q CLI
            local_frame = tk.Frame(main_frame, bg='#000000')
            local_frame.pack(fill=tk.X, pady=5)
            
            local_available = methods['local']['available']
            local_color = '#00FF00' if local_available else '#666666'
            local_text = "LOCAL - " + methods['local']['description']
            if not local_available:
                local_text += " (NOT AVAILABLE)"
            
            tk.Radiobutton(local_frame, text=local_text,
                          variable=self.selected_method, value="local",
                          bg='#000000', fg=local_color, selectcolor='#003300',
                          font=('Courier New', 10),
                          state=tk.NORMAL if local_available else tk.DISABLED).pack(anchor=tk.W)
            
            # WSL Q CLI
            wsl_frame = tk.Frame(main_frame, bg='#000000')
            wsl_frame.pack(fill=tk.X, pady=5)
            
            wsl_available = methods['wsl']['available']
            wsl_color = '#00FFFF' if wsl_available else '#666666'
            wsl_text = "WSL - " + methods['wsl']['description']
            if not wsl_available:
                wsl_text += " (NOT AVAILABLE)"
            
            tk.Radiobutton(wsl_frame, text=wsl_text,
                          variable=self.selected_method, value="wsl",
                          bg='#000000', fg=wsl_color, selectcolor='#003333',
                          font=('Courier New', 10),
                          state=tk.NORMAL if wsl_available else tk.DISABLED).pack(anchor=tk.W)
            
            # SSH Q CLI
            ssh_frame = tk.Frame(main_frame, bg='#000000')
            ssh_frame.pack(fill=tk.X, pady=5)
            
            ssh_available = methods['ssh']['available']
            ssh_color = '#FF00FF' if ssh_available else '#666666'
            ssh_text = "SSH - " + methods['ssh']['description']
            if not ssh_available:
                ssh_text += " (NOT CONFIGURED)"
            
            tk.Radiobutton(ssh_frame, text=ssh_text,
                          variable=self.selected_method, value="ssh",
                          bg='#000000', fg=ssh_color, selectcolor='#330033',
                          font=('Courier New', 10),
                          state=tk.NORMAL if ssh_available else tk.DISABLED).pack(anchor=tk.W)
            
            # Current status
            status_frame = tk.Frame(main_frame, bg='#000000')
            status_frame.pack(fill=tk.X, pady=(20, 10))
            
            tk.Label(status_frame, text="Current Method:", 
                    bg='#000000', fg='#FFFF00', 
                    font=('Courier New', 10, 'bold')).pack(anchor=tk.W)
            
            current_name = method_status['active_method'].get('name', 'Unknown')
            tk.Label(status_frame, text="  " + current_name, 
                    bg='#000000', fg='#00FF00', 
                    font=('Courier New', 10)).pack(anchor=tk.W)
            
            # Buttons
            button_frame = tk.Frame(main_frame, bg='#000000')
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            def apply_method():
                try:
                    selected = self.selected_method.get()
                    self.q_service.set_q_method(selected)
                    self.result = True
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", "Failed to set Q CLI method: " + str(e))
            
            def cancel():
                self.result = False
                dialog.destroy()
            
            def configure_ssh():
                """Configure SSH from within the dialog"""
                try:
                    success, message = self.q_service.configure_ssh(dialog)
                    if success:
                        # Refresh the dialog
                        dialog.destroy()
                        self.result = self.show()  # Reopen dialog
                    else:
                        messagebox.showwarning("SSH Configuration", message)
                except Exception as e:
                    messagebox.showerror("SSH Error", str(e))
            
            tk.Button(button_frame, text="Apply", command=apply_method,
                     bg='#003300', fg='#00FF00', font=('Courier New', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            tk.Button(button_frame, text="Configure SSH", command=configure_ssh,
                     bg='#330033', fg='#FF00FF', font=('Courier New', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            tk.Button(button_frame, text="Cancel", command=cancel,
                     bg='#330000', fg='#FF0000', font=('Courier New', 10, 'bold')).pack(side=tk.LEFT)
            
            # Wait for dialog to close
            dialog.wait_window()
            return self.result
            
        except ImportError:
            # Fallback for environments without tkinter
            print("Q CLI Method Configuration (text mode):")
            print("1. AUTO - Automatically select best available")
            print("2. LOCAL - Windows native Q CLI")
            print("3. WSL - Q CLI in WSL environment") 
            print("4. SSH - Q CLI on remote Linux host")
            
            choice = input("Select method (1-4): ").strip()
            method_map = {'1': 'auto', '2': 'local', '3': 'wsl', '4': 'ssh'}
            
            if choice in method_map:
                self.q_service.set_q_method(method_map[choice])
                return True
            return False


class HALWindowsInterface:
    """HAL 9000 Interface optimized for Windows with WSL support"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("QIS v6.0")
        self.root.geometry("1500x900")
        self.root.configure(bg='#000000')
        
        # Set window close protocol to prevent terminal hanging
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Store reference to this interface in the root window
        self.root.hal_interface = self
        
        # Initialize skin manager
        self.skin_manager = None
        try:
            from skins.skin_manager import SkinManager
            self.skin_manager = SkinManager()
            self.skin_manager.load_skin_preference()
            print("✓ Skin manager initialized")
            
            # Apply the loaded skin immediately
            self.apply_skin(self.skin_manager)
        except ImportError:
            print("⚠ Skin system not available")
        except Exception as e:
            print("⚠ Error initializing skin manager:", str(e))
        
        # Queue for thread communication
        self.output_queue = queue.Queue()
        
        # HAL's current state
        self.hal_active = True
        self.conversation_history = []
        self.current_mode = "Q"  # "Q" for Q CLI, "SHELL" for commands
        
        # Windows-specific working directory handling
        if platform.system().lower() == 'windows':
            self.shell_cwd = os.path.expanduser("~")
        else:
            self.shell_cwd = os.path.expanduser("~")
        
        # Initialize cross-platform Q service
        self.q_service = CrossPlatformQService()
        
        # Shell name will be determined dynamically
        self.shell_name = "SHELL"  # Default fallback
        
        # Color theme: "green" or "amber"
        self.color_theme = "green"
        
        # Display mode: "modern" or "retro"
        self.display_mode = "modern"
        
        # Retro effects
        self.scan_lines_enabled = False
        self.retro_canvas = None
        
        # Load HAL image if available
        self.hal_image = None
        self.load_hal_image()
        
        self.setup_ui()
        self.setup_styles()
        self.update_theme()
        
        # Start output queue processing
        self.check_output_queue()
        
        # Show welcome message
        self.start_hal_greeting()
        
        # Update system status
        self.update_system_status()
        
        # Update shell button text now that Q service is ready
        try:
            shell_name = self.get_shell_display_name()
            self.shell_mode_btn.config(text=shell_name)
        except:
            pass  # Keep default if still not ready
    
    def get_shell_display_name(self):
        """Get the shell name for display purposes"""
        try:
            env_info = self.q_service.env_info
            if env_info['is_windows'] and not env_info['is_wsl']:
                return "POWERSHELL"
            elif env_info['is_wsl']:
                return "BASH"  # WSL typically uses bash
            elif env_info['is_macos']:
                shell = env_info.get('shell', 'bash')
                return shell.upper()
            else:  # Linux
                shell = env_info.get('shell', 'bash')
                return shell.upper()
        except:
            # Fallback if Q service not ready
            return "SHELL"

    def initialize_display_effects(self):
        """Initialize display effects based on current mode"""
        if self.display_mode == "retro":
            self.add_retro_effects()
        
        # Update button text to reflect current state
        retro_text = "MODERN" if self.display_mode == "retro" else "RETRO"
        if hasattr(self, 'retro_btn'):
            self.retro_btn.config(text=retro_text)
    
    def load_hal_image(self):
        """Load the HAL 9000 panel image if available"""
        if not PIL_AVAILABLE:
            self.hal_image = None
            return
            
        image_path = os.path.join(os.path.dirname(__file__), "assets", "Hal_9000_Panel.svg.png")
        try:
            if os.path.exists(image_path):
                # Load image and resize to fit within left panel while maintaining aspect ratio
                pil_image = Image.open(image_path)
                
                # Left panel constraints: 430px wide (450px - padding), reasonable height
                max_width = 430
                max_height = 500  # Allow more height for the tall HAL image
                
                # Calculate the best fit while maintaining aspect ratio
                original_width, original_height = pil_image.size
                aspect_ratio = original_width / original_height
                
                # For the HAL image (which is very tall), we'll likely fit by height
                # Try fitting by width first
                target_width_by_width = max_width
                target_height_by_width = int(target_width_by_width / aspect_ratio)
                
                # Try fitting by height
                target_height_by_height = max_height
                target_width_by_height = int(target_height_by_height * aspect_ratio)
                
                # Choose the option that fits within both constraints
                if target_height_by_width <= max_height:
                    # Fit by width works
                    target_width = target_width_by_width
                    target_height = target_height_by_width
                else:
                    # Must fit by height
                    target_width = target_width_by_height
                    target_height = target_height_by_height
                
                # Resize the image
                pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.hal_image = ImageTk.PhotoImage(pil_image)
                
                # Store dimensions for layout purposes
                self.hal_image_width = target_width
                self.hal_image_height = target_height
                
                print("HAL image loaded: {}x{} (aspect ratio: {:.3f})".format(
                    target_width, target_height, aspect_ratio))
            else:
                self.hal_image = None
        except Exception as e:
            print("Could not load HAL image: {}".format(e))
            self.hal_image = None
    
    def show_unified_settings(self):
        """Show unified settings dialog"""
        try:
            try:
                from unified_settings_dialog import UnifiedSettingsDialog
                SETTINGS_AVAILABLE = True
            except ImportError:
                SETTINGS_AVAILABLE = False
            
            if not SETTINGS_AVAILABLE:
                from tkinter import messagebox
                messagebox.showwarning('Settings', 'Unified settings not available.')
                return
            
            if not hasattr(self, '_settings_dialog'):
                self._settings_dialog = UnifiedSettingsDialog(self, self.q_service)
            
            self._settings_dialog.show()
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror('Settings Error', 'Error opening settings: ' + str(e))
    
    def apply_skin(self, skin_manager):
        """Apply skin to the current interface"""
        try:
            if not skin_manager:
                return
            
            self.skin_manager = skin_manager
            identity = skin_manager.get_identity()
            
            print(f"DEBUG: Applying skin identity: {identity}")
            
            # Update interface elements with skin
            if identity:
                # Update title with personality name
                personality_name = identity.get('name', 'QIS v6.0')
                new_title = personality_name + " - QIS v6.0"
                self.root.title(new_title)
                print(f"DEBUG: Updated title to: {new_title}")
                
                # Get colors from skin manager (not from identity)
                try:
                    colors = skin_manager.get_colors()
                    print(f"DEBUG: Got colors from skin: {colors}")
                except Exception as color_error:
                    print(f"DEBUG: Error getting colors: {color_error}")
                    colors = {}
                
                if colors:
                    # Update background color
                    bg_color = colors.get('background', '#000000')
                    self.root.configure(bg=bg_color)
                    print(f"DEBUG: Updated root background to: {bg_color}")
                    
                    # Update chat display if it exists
                    if hasattr(self, 'chat_display'):
                        try:
                            text_color = colors.get('text', '#00FF00')
                            chat_bg = colors.get('panel_bg', bg_color)
                            self.chat_display.configure(bg=chat_bg, fg=text_color, insertbackground=text_color)
                            print(f"DEBUG: Updated chat display: bg={chat_bg}, fg={text_color}")
                        except Exception as e:
                            print(f"DEBUG: Could not update chat display: {e}")
                    
                    # Update input field if it exists
                    if hasattr(self, 'input_field'):
                        try:
                            input_bg = colors.get('input_bg', '#111111')
                            input_fg = colors.get('input_fg', '#FFFFFF')
                            self.input_field.configure(bg=input_bg, fg=input_fg, insertbackground=input_fg)
                            print(f"DEBUG: Updated input field: bg={input_bg}, fg={input_fg}")
                        except Exception as e:
                            print(f"DEBUG: Could not update input field: {e}")
                    
                    # Update all frames and labels with new colors
                    self.update_all_widgets_colors(colors)
                    
                    # Update graphics based on personality
                    self.update_personality_graphics(identity)
                else:
                    print("DEBUG: No colors available from skin")
                
                # Force interface refresh
                self.root.update()
                print(f"DEBUG: Applied skin: {personality_name}")
                
        except Exception as e:
            print("DEBUG: Error applying skin:", str(e))
    
    def update_personality_graphics(self, identity):
        """Update graphics and ASCII art based on personality"""
        try:
            personality_name = identity.get('name', '').lower()
            print(f"DEBUG: Updating graphics for personality: {personality_name}")
            
            # Map personalities to their graphics files
            graphics_map = {
                'hal 9000': 'Hal_9000_Panel.svg.png',
                'computer': 'lcars_interface.txt',  # Star Trek LCARS
                'trs-80': 'trs80_boot_screen.txt'   # TRS-80 boot screen
            }
            
            # Find the right graphic file
            graphic_file = None
            for key, filename in graphics_map.items():
                if key in personality_name:
                    graphic_file = filename
                    break
            
            if graphic_file:
                print(f"DEBUG: Loading graphic: {graphic_file}")
                
                # Update the HAL image area with personality-specific content
                if hasattr(self, 'hal_image_label') and self.hal_image_label:
                    try:
                        if graphic_file.endswith('.png'):
                            # Load image file (HAL 9000)
                            self.load_hal_image()
                            if self.hal_image:
                                self.hal_image_label.configure(image=self.hal_image, text="")
                                print(f"DEBUG: Loaded HAL image successfully")
                            else:
                                # Fallback to text if image fails
                                self.hal_image_label.configure(image="", text="HAL 9000\nSYSTEM READY", 
                                                             font=('Courier New', 12, 'bold'))
                                print(f"DEBUG: HAL image failed, using text fallback")
                        else:
                            # Load text-based ANSI graphic
                            graphic_path = os.path.join('assets', graphic_file)
                            if os.path.exists(graphic_path):
                                with open(graphic_path, 'r', encoding='utf-8') as f:
                                    graphic_content = f.read()
                                
                                # Get current skin colors for the graphic
                                colors = {}
                                if self.skin_manager:
                                    try:
                                        colors = self.skin_manager.get_colors()
                                    except:
                                        pass
                                
                                # Set colors based on personality
                                if 'trs-80' in personality_name:
                                    # TRS-80: White text on black background
                                    text_color = colors.get('text', '#FFFFFF')
                                    bg_color = colors.get('background', '#000000')
                                elif 'computer' in personality_name:
                                    # LCARS: Orange text on dark background
                                    text_color = colors.get('primary', '#FF9900')  # LCARS orange
                                    bg_color = colors.get('panel_bg', '#111133')   # Dark blue
                                else:
                                    # Default: Use skin colors
                                    text_color = colors.get('text', '#00FF00')
                                    bg_color = colors.get('panel_bg', '#000000')
                                
                                # Clear any image and set text-based graphic
                                self.hal_image_label.configure(
                                    image="",  # Clear any existing image
                                    text=graphic_content, 
                                    font=('Courier New', 8, 'bold'),
                                    justify='left',
                                    anchor='nw',
                                    fg=text_color,
                                    bg=bg_color,
                                    padx=5,
                                    pady=5
                                )
                                print(f"DEBUG: Updated graphics with {graphic_file} - colors: fg={text_color}, bg={bg_color}")
                            else:
                                print(f"DEBUG: Graphic file not found: {graphic_path}")
                                # Fallback text
                                self.hal_image_label.configure(image="", text=f"{personality_name.upper()}\nSYSTEM READY")
                    except Exception as e:
                        print(f"DEBUG: Error updating graphics: {e}")
                        # Fallback text
                        if self.hal_image_label:
                            self.hal_image_label.configure(image="", text=f"{personality_name.upper()}\nSYSTEM READY")
                else:
                    print(f"DEBUG: hal_image_label not found or not initialized")
            else:
                print(f"DEBUG: No specific graphic found for {personality_name}")
                
        except Exception as e:
            print(f"DEBUG: Error in update_personality_graphics: {e}")
    
    def update_all_widgets_colors(self, colors):
        """Update all widgets in the interface with new colors"""
        try:
            bg_color = colors.get('background', '#000000')
            text_color = colors.get('text', '#FFFFFF')
            panel_bg = colors.get('panel_bg', bg_color)
            
            # Make sure panel_bg is different from bg_color for visibility
            if panel_bg == bg_color:
                # Use a slightly different shade for panels
                if bg_color == '#000000':
                    panel_bg = '#111111'
                else:
                    panel_bg = bg_color
            
            print(f"DEBUG: Using colors - bg: {bg_color}, text: {text_color}, panel: {panel_bg}")
            
            # Recursively update all widgets
            def update_widget(widget):
                try:
                    widget_class = widget.winfo_class()
                    
                    if widget_class in ['Frame', 'Toplevel']:
                        widget.configure(bg=panel_bg)
                    elif widget_class in ['Label']:
                        # Make sure labels are visible
                        widget.configure(bg=panel_bg, fg=text_color)
                    elif widget_class in ['Text']:
                        widget.configure(bg=panel_bg, fg=text_color, insertbackground=text_color)
                    elif widget_class in ['Entry']:
                        input_bg = colors.get('input_bg', '#111111')
                        input_fg = colors.get('input_fg', text_color)
                        widget.configure(bg=input_bg, fg=input_fg, insertbackground=input_fg)
                    
                    # Update children recursively
                    for child in widget.winfo_children():
                        update_widget(child)
                        
                except Exception as e:
                    # Skip widgets that can't be updated
                    pass
            
            # Start from root and update all widgets
            update_widget(self.root)
            print(f"DEBUG: Updated all widgets with colors")
            
        except Exception as e:
            print(f"DEBUG: Error updating widget colors: {e}")
    
    def update_interface_with_skin(self):
        """Update interface with current skin"""
        if self.skin_manager:
            self.apply_skin(self.skin_manager)
    
    def configure_q_method(self):
        """Configure Q CLI method selection"""
        try:
            dialog = QMethodConfigDialog(self.root, self.q_service)
            result = dialog.show()
            
            if result:
                # Update system status after method change
                self.update_system_status()
                self.update_connection_status()
                
                # Show success message
                from tkinter import messagebox
                try:
                    method_status = self.q_service.get_q_method_status()
                    current_method = method_status['active_method'].get('name', 'Unknown Method')
                    messagebox.showinfo("Q CLI Method", 
                                      "Q CLI method set to: " + current_method)
                except Exception as e:
                    messagebox.showinfo("Q CLI Method", 
                                      "Q CLI method updated successfully")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Q CLI Configuration Error", 
                               "Error configuring Q CLI method:\n" + str(e))
    
    def configure_ssh(self):
        """Configure SSH Q CLI routing"""
        try:
            success, message = self.q_service.configure_ssh(self.root)
            
            if success:
                # Update system status after SSH configuration
                self.update_system_status()
                self.update_connection_status()
                
                # Show success message
                from tkinter import messagebox
                messagebox.showinfo("SSH Configuration", 
                                  f"{message}\n\nSSH Q CLI routing is now available.")
            else:
                from tkinter import messagebox
                messagebox.showwarning("SSH Configuration", 
                                     f"SSH configuration failed:\n{message}")
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("SSH Configuration Error", 
                               f"Error configuring SSH:\n{str(e)}")
    
    def update_system_status(self):
        """Update system status based on Q service availability and environment"""
        try:
            status_info = self.q_service.get_status()
            env_info = status_info.get('environment', {})
            q_method = status_info.get('q_method', 'unknown')
            
            # Check if Q CLI is available based on the current method
            q_available = status_info.get('available', False)
            
            # For WSL method, also check if we can actually use it
            if q_method == 'wsl' and not q_available:
                # Try a more lenient check - if WSL method is selected, assume it works
                # unless we can definitively prove it doesn't
                try:
                    # Quick WSL availability check
                    result = subprocess.run(['wsl', 'echo', 'test'], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        q_available = True  # WSL is working, assume Q CLI is too
                except:
                    pass
            
            if q_available:
                if q_method == 'ssh' or 'SSH Remote' in status_info.get('method', ''):
                    # SSH routing
                    ssh_details = status_info.get('ssh_details', {})
                    host = ssh_details.get('host', 'unknown')
                    if host is None:
                        host = 'unknown'
                    status_text = "System Status: OPERATIONAL (SSH: " + str(host) + ")"
                elif q_method == 'wsl' or 'WSL Q CLI' in status_info.get('method', ''):
                    # WSL Q CLI
                    wsl_distro = env_info.get('wsl_distro', 'WSL')
                    if wsl_distro is None:
                        wsl_distro = 'WSL'
                    status_text = "System Status: OPERATIONAL (WSL: " + str(wsl_distro) + ")"
                elif env_info.get('is_wsl', False):
                    wsl_distro = env_info.get('wsl_distro', 'WSL')
                    if wsl_distro is None:
                        wsl_distro = 'WSL'
                    status_text = "System Status: OPERATIONAL (WSL: " + str(wsl_distro) + ")"
                elif env_info.get('is_windows', False):
                    status_text = "System Status: OPERATIONAL (Windows)"
                elif env_info.get('is_macos', False):
                    status_text = "System Status: OPERATIONAL (macOS)"
                else:
                    status_text = "System Status: OPERATIONAL (Linux)"
                self.status_label.config(foreground='#00FF00')  # Green
            else:
                if env_info.get('is_wsl', False):
                    wsl_distro = env_info.get('wsl_distro', 'WSL')
                    if wsl_distro is None:
                        wsl_distro = 'WSL'
                    status_text = "System Status: LIMITED (WSL: " + str(wsl_distro) + ", Q CLI unavailable)"
                elif env_info.get('is_windows', False):
                    status_text = "System Status: LIMITED (Windows, Q CLI unavailable)"
                elif env_info.get('is_macos', False):
                    status_text = "System Status: LIMITED (macOS, Q CLI unavailable)"
                else:
                    status_text = "System Status: LIMITED (Linux, Q CLI unavailable)"
                self.status_label.config(foreground='#FF8800')  # Orange
            
            self.status_label.config(text=status_text)
            
        except Exception as e:
            # For debugging - show what the actual error is
            error_msg = "System Status: ERROR (" + str(e)[:50] + ")"
            self.status_label.config(text=error_msg, foreground='#FF0000')  # Red
    
    def update_connection_status(self):
        """Update connection status based on current mode and Q service availability"""
        try:
            if self.current_mode == "Q":
                # Check if Q CLI is available
                status_info = self.q_service.get_status()
                if status_info['available']:
                    method = status_info.get('method', 'Unknown')
                    q_method = status_info.get('q_method', 'unknown')
                    
                    if q_method == 'ssh' or 'SSH Remote' in method:
                        ssh_details = status_info.get('ssh_details', {})
                        host = ssh_details.get('host', 'unknown')
                        self.connection_status.config(text="Q CLI: READY (SSH: " + host + ")")
                    elif q_method == 'wsl' or 'WSL Q CLI' in method:
                        self.connection_status.config(text="Q CLI: READY (WSL)")
                    elif self.q_service.env_info['is_wsl']:
                        self.connection_status.config(text="Q CLI: READY (WSL)")
                    else:
                        self.connection_status.config(text="Q CLI: READY (Windows)")
                else:
                    self.connection_status.config(text="Q CLI: UNAVAILABLE")
            else:  # SHELL mode
                env_info = self.q_service.env_info
                shell_name = self.get_shell_display_name()
                if env_info['is_wsl']:
                    self.connection_status.config(text=f"{shell_name}: READY (WSL)")
                elif env_info['is_windows']:
                    self.connection_status.config(text=f"{shell_name}: READY (Windows)")
                elif env_info['is_macos']:
                    self.connection_status.config(text=f"{shell_name}: READY (macOS)")
                else:
                    self.connection_status.config(text=f"{shell_name}: READY (Linux)")
                
        except Exception as e:
            self.connection_status.config(text="STATUS: ERROR")
    
    def setup_ui(self):
        """Set up the main user interface with proper layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for HAL image and controls (increased width for better proportions)
        left_panel = tk.Frame(main_frame, bg='#000000', width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Top section of left panel - System info and controls
        left_top = tk.Frame(left_panel, bg='#000000')
        left_top.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # System information at the top
        self.setup_system_info(left_top)
        
        # Control buttons below system info
        self.setup_control_buttons(left_top)
        
        # Bottom section of left panel - HAL image
        left_bottom = tk.Frame(left_panel, bg='#000000')
        left_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # HAL image or animated eye at the bottom
        self.setup_hal_display(left_bottom)
        
        # Right panel for chat
        right_panel = tk.Frame(main_frame, bg='#000000')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat display
        self.setup_chat_display(right_panel)
        
        # Input area
        self.setup_input_area(right_panel)
        
        # Status bar
        self.setup_status_bar(right_panel)
    
    def setup_system_info(self, parent):
        """Set up system information display"""
        info_frame = tk.Frame(parent, bg='#000000')
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(info_frame,
                               text="QIS v6.0",
                               style='HAL.TLabel',
                               font=self.get_terminal_font(16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        self.status_label = ttk.Label(info_frame,
                                     text="System Status: CHECKING...",
                                     style='HAL.TLabel',
                                     font=self.get_terminal_font(10))
        self.status_label.pack(anchor=tk.W)
        
        # Mode indicator
        self.mode_label = ttk.Label(info_frame,
                                   text="Mode: Q CLI",
                                   style='HAL.TLabel',
                                   font=self.get_terminal_font(10))
        self.mode_label.pack(anchor=tk.W)
        
        # Windows environment info
        env_info = self.q_service.env_info
        env_text = "Platform: " + env_info['platform']
        if env_info['is_wsl']:
            wsl_distro = env_info.get('wsl_distro', 'WSL')
            if wsl_distro is None:
                wsl_distro = 'WSL'
            env_text += " (WSL: " + str(wsl_distro) + ")"
        
        self.env_label = ttk.Label(info_frame,
                                  text=env_text,
                                  style='HAL.TLabel',
                                  font=self.get_terminal_font(9))
        self.env_label.pack(anchor=tk.W)
    
    def setup_hal_display(self, parent):
        """Set up HAL image or animated eye display at the bottom"""
        hal_frame = tk.Frame(parent, bg='#000000')
        hal_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Initialize graphics display reference
        self.hal_image_label = None
        
        if self.hal_image:
            # Create a container for proper centering
            image_container = tk.Frame(hal_frame, bg='#000000')
            image_container.pack(fill=tk.BOTH, expand=True)
            
            # Display HAL image centered
            self.hal_image_label = tk.Label(image_container, image=self.hal_image, bg='#000000')
            self.hal_image_label.pack(expand=True, anchor=tk.CENTER)
            
            # Add some padding around the image
            self.hal_image_label.configure(padx=10, pady=10)
        else:
            # Create text-based graphics display as fallback
            image_container = tk.Frame(hal_frame, bg='#000000')
            image_container.pack(fill=tk.BOTH, expand=True)
            
            # Create label for text-based graphics
            self.hal_image_label = tk.Label(image_container, 
                                          text="HAL 9000\nSYSTEM READY", 
                                          font=('Courier New', 12, 'bold'),
                                          fg='#00FF00', 
                                          bg='#000000',
                                          justify='center')
            self.hal_image_label.pack(expand=True, anchor=tk.CENTER, padx=10, pady=10)
    
    def setup_animated_eye(self, parent):
        """Set up animated HAL eye as fallback"""
        self.eye_canvas = tk.Canvas(parent, width=200, height=200, bg='#000000', highlightthickness=0)
        self.eye_canvas.pack(expand=True)
        
        # Draw HAL's eye
        self.eye_canvas.create_oval(50, 50, 150, 150, outline='#FF0000', width=3)
        self.eye_canvas.create_oval(75, 75, 125, 125, fill='#FF0000', outline='#FF0000')
        
        # Animate the eye
        self.animate_eye()
    
    def animate_eye(self):
        """Animate HAL's eye"""
        if hasattr(self, 'eye_canvas'):
            # Simple pulsing animation
            current_time = time.time()
            intensity = int(128 + 127 * abs(((current_time * 2) % 2) - 1))
            color = f"#{intensity:02x}0000"
            
            self.eye_canvas.delete("eye_inner")
            self.eye_canvas.create_oval(75, 75, 125, 125, fill=color, outline=color, tags="eye_inner")
            
            self.root.after(100, self.animate_eye)
    
    def setup_control_buttons(self, parent):
        """Set up control buttons in a compact layout"""
        # Theme buttons row
        theme_frame = tk.Frame(parent, bg='#000000')
        theme_frame.pack(pady=(10, 5))
        
        self.theme_btn = ttk.Button(theme_frame, text="AMBER", 
                                   command=self.toggle_color_theme, 
                                   style='HAL.Theme.TButton')
        self.theme_btn.pack(side=tk.LEFT, padx=2)
        
        self.retro_btn = ttk.Button(theme_frame, text="RETRO", 
                                   command=self.toggle_display_mode, 
                                   style='HAL.Retro.TButton')
        self.retro_btn.pack(side=tk.LEFT, padx=2)
        
        # Mode buttons
        mode_frame = tk.Frame(parent, bg='#000000')
        mode_frame.pack(pady=(0, 5))
        
        self.q_mode_btn = ttk.Button(mode_frame, text="Q CLI", 
                                    command=lambda: self.set_mode("Q"), 
                                    style='HAL.Active.TButton')
        self.q_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Use safe shell name during initialization
        try:
            shell_name = self.get_shell_display_name()
        except:
            shell_name = "SHELL"  # Safe fallback during initialization
        
        self.shell_mode_btn = ttk.Button(mode_frame, text=shell_name, 
                                        command=lambda: self.set_mode("SHELL"), 
                                        style='HAL.TButton')
        self.shell_mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Action buttons (in two rows for compact layout)
        action_frame1 = tk.Frame(parent, bg='#000000')
        action_frame1.pack(pady=(5, 2))
        
        ttk.Button(action_frame1, text="CLEAR", 
                  command=self.clear_chat, style='HAL.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(action_frame1, text="SAVE", 
                  command=self.save_log, style='HAL.TButton').pack(side=tk.LEFT, padx=1)
        
        action_frame2 = tk.Frame(parent, bg='#000000')
        action_frame2.pack(pady=(2, 2))
        
        ttk.Button(action_frame2, text="SETTINGS", 
                  command=self.show_unified_settings, style='HAL.TButton').pack(side=tk.LEFT, padx=1)
#         ttk.Button(action_frame2, text="SSH", 
#                   command=self.configure_ssh, style='HAL.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(action_frame2, text="ABOUT", 
                  command=self.show_about, style='HAL.TButton').pack(side=tk.LEFT, padx=1)
        
        action_frame3 = tk.Frame(parent, bg='#000000')
        action_frame3.pack(pady=(2, 5))
        
        ttk.Button(action_frame3, text="EXIT", 
                  command=self.safe_exit, style='HAL.TButton').pack()
    
    def setup_chat_display(self, parent):
        """Set up chat display area"""
        # Chat display with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            width=80,
            height=25,
            bg='#000000',
            fg='#00FF00',
            insertbackground='#00FF00',
            selectbackground='#003300',
            font=self.get_terminal_font(11),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    def setup_input_area(self, parent):
        """Set up input area"""
        input_frame = tk.Frame(parent, bg='#000000')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input label
        self.input_label = ttk.Label(input_frame, text="Q INPUT:", style='HAL.TLabel')
        self.input_label.pack(anchor=tk.W)
        
        # Input entry with send button
        entry_frame = tk.Frame(input_frame, bg='#000000')
        entry_frame.pack(fill=tk.X)
        
        self.input_entry = tk.Entry(
            entry_frame,
            bg='#001100',
            fg='#00FF00',
            insertbackground='#00FF00',
            selectbackground='#003300',
            font=self.get_terminal_font(12),
            relief=tk.FLAT,
            bd=2
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        self.input_entry.bind('<Tab>', self.handle_tab_completion)
        
        send_button = ttk.Button(entry_frame, text="SEND", 
                               command=self.send_message, style='HAL.TButton')
        send_button.pack(side=tk.RIGHT)
    
    def setup_status_bar(self, parent):
        """Set up status bar"""
        status_frame = tk.Frame(parent, bg='#000000')
        status_frame.pack(fill=tk.X)
        
        self.connection_status = ttk.Label(status_frame,
                                          text="Q CLI: CHECKING...",
                                          style='HAL.TLabel',
                                          font=self.get_terminal_font(9))
        self.connection_status.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(status_frame,
                                   text="",
                                   style='HAL.TLabel',
                                   font=self.get_terminal_font(9))
        self.time_label.pack(side=tk.RIGHT)
        
        # Update connection status after initialization
        self.update_connection_status()
        
        # Start time update
        self.update_time()
    
    def get_terminal_font(self, size=12, weight='normal'):
        """Get terminal-style font based on display mode"""
        if self.display_mode == "retro":
            # Try authentic retro fonts in order of preference
            retro_fonts = [
                'Perfect DOS VGA 437',  # Classic DOS font
                'IBM Plex Mono',        # IBM-style monospace
                'Source Code Pro',      # Modern but retro-friendly
                'Consolas',            # Windows monospace
                'Liberation Mono',      # Linux equivalent
                'DejaVu Sans Mono',    # Cross-platform
                'Courier New'          # Fallback
            ]
            
            # Test which fonts are available
            import tkinter.font as tkFont
            available_fonts = tkFont.families()
            
            for font in retro_fonts:
                if font in available_fonts:
                    return (font, size, weight)
            
            # Fallback to Courier New with retro styling
            return ('Courier New', size, weight)
        else:
            # Modern clean fonts
            modern_fonts = [
                'Segoe UI Mono',       # Windows 10/11 modern
                'SF Mono',             # macOS
                'Ubuntu Mono',         # Ubuntu
                'Roboto Mono',         # Google
                'Consolas',            # Windows fallback
                'Courier New'          # Universal fallback
            ]
            
            import tkinter.font as tkFont
            available_fonts = tkFont.families()
            
            for font in modern_fonts:
                if font in available_fonts:
                    return (font, size, weight)
            
            return ('Courier New', size, weight)
    
    def get_theme_colors(self):
        """Get colors for current theme and display mode"""
        base_colors = {}
        
        if self.color_theme == "amber":
            base_colors = {
                'bg': '#000000',
                'fg': '#FFB000',
                'terminal_bg': '#110800',
                'terminal_fg': '#FFB000',
                'terminal_cursor': '#FFB000',
                'terminal_select': '#332200',
                'powershell_fg': '#FFCC33',         # Lighter amber for powershell
                'powershell_bg': '#110800',         # Dark amber tint
                'system_fg': '#FF8800',        # Orange for system messages
                'error_fg': '#FF4400',         # Red-orange for errors
                'output_fg': '#FFDD88',        # Light amber for output
                'button_bg': '#331100',
                'button_fg': '#FFB000'
            }
        else:  # green theme
            base_colors = {
                'bg': '#000000',
                'fg': '#00FF00',
                'terminal_bg': '#001100',
                'terminal_fg': '#00FF00',
                'terminal_cursor': '#00FF00',
                'terminal_select': '#003300',
                'powershell_fg': '#00FFFF',         # Cyan for powershell
                'powershell_bg': '#001100',         # Dark green tint
                'system_fg': '#FFFF00',        # Yellow for system messages
                'error_fg': '#FF8888',         # Light red for errors
                'output_fg': '#88FF88',        # Light green for output
                'button_bg': '#003300',
                'button_fg': '#00FF00'
            }
        
        # Apply retro modifications
        if self.display_mode == "retro":
            # Make colors more saturated and add glow effects
            if self.color_theme == "amber":
                base_colors.update({
                    'terminal_bg': '#0f0600',      # Darker for CRT effect
                    'terminal_fg': '#FFCC00',      # Brighter amber
                    'fg': '#FFCC00',               # Brighter text
                    'output_fg': '#FFEE99',        # Glowing output
                })
            else:  # green
                base_colors.update({
                    'terminal_bg': '#001a00',      # Darker for CRT effect
                    'terminal_fg': '#00FF44',      # Brighter green
                    'fg': '#00FF44',               # Brighter text
                    'output_fg': '#99FF99',        # Glowing output
                })
        
        return base_colors
    
    def setup_styles(self):
        """Configure the retro HAL-inspired styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        colors = self.get_theme_colors()
        
        # Configure styles for HAL aesthetic
        style.configure('HAL.TFrame', background='#000000')
        style.configure('HAL.TLabel', 
                       background='#000000', 
                       foreground=colors['fg'],
                       font=self.get_terminal_font(10))
        
        style.configure('HAL.TButton',
                       background=colors['button_bg'],
                       foreground=colors['button_fg'],
                       borderwidth=1,
                       focuscolor='none',
                       font=self.get_terminal_font(10, 'bold'))
        
        style.map('HAL.TButton',
                 background=[('active', '#550000')])
        
        # Active button style
        style.configure('HAL.Active.TButton',
                       background='#550000',
                       foreground='#FF0000',
                       borderwidth=2,
                       font=self.get_terminal_font(10, 'bold'))
        
        # Theme button style
        style.configure('HAL.Theme.TButton',
                       background='#330033',
                       foreground='#FF00FF',
                       borderwidth=1,
                       font=self.get_terminal_font(10, 'bold'))
        
        # Retro button style
        if self.display_mode == "retro":
            style.configure('HAL.Retro.TButton',
                           background='#003333',
                           foreground='#00FFFF',
                           borderwidth=2,
                           relief='raised',
                           font=self.get_terminal_font(10, 'bold'))
        else:
            style.configure('HAL.Retro.TButton',
                           background='#333300',
                           foreground='#FFFF00',
                           borderwidth=1,
                           relief='flat',
                           font=self.get_terminal_font(10, 'bold'))
    
    def update_theme(self):
        """Update theme colors throughout the interface"""
        colors = self.get_theme_colors()
        
        # Update chat display
        self.chat_display.config(
            bg=colors['terminal_bg'],
            fg=colors['terminal_fg'],
            insertbackground=colors['terminal_cursor'],
            selectbackground=colors['terminal_select']
        )
        
        # Update input field based on current mode
        if self.current_mode == "Q":
            self.input_entry.config(
                bg=colors['terminal_bg'],
                fg=colors['terminal_fg'],
                insertbackground=colors['terminal_cursor'],
                selectbackground=colors['terminal_select']
            )
        else:  # POWERSHELL mode
            self.input_entry.config(
                bg=colors['powershell_bg'],
                fg=colors['powershell_fg'],
                insertbackground=colors['powershell_fg'],
                selectbackground=colors['terminal_select']
            )
        
        # Update text tags
        terminal_font = self.get_terminal_font(11)
        self.chat_display.tag_configure('hal', foreground='#FF0000', font=self.get_terminal_font(11, 'bold'))
        self.chat_display.tag_configure('user', foreground=colors['terminal_fg'], font=terminal_font)
        self.chat_display.tag_configure('powershell_user', foreground=colors['powershell_fg'], font=terminal_font)
        self.chat_display.tag_configure('powershell_output', foreground=colors['output_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('powershell_error', foreground=colors['error_fg'], font=self.get_terminal_font(10))
        self.chat_display.tag_configure('system', foreground=colors['system_fg'], font=self.get_terminal_font(10, 'italic'))
        self.chat_display.tag_configure('timestamp', foreground='#888888', font=self.get_terminal_font(9))
        
        # Update theme button text
        theme_text = "AMBER" if self.color_theme == "green" else "GREEN"
        self.theme_btn.config(text=theme_text)
    
    def toggle_color_theme(self):
        """Toggle between green and amber themes"""
        self.color_theme = "amber" if self.color_theme == "green" else "green"
        self.setup_styles()
        self.update_theme()
    
    def toggle_display_mode(self):
        """Toggle between modern and retro display modes"""
        self.display_mode = "retro" if self.display_mode == "modern" else "modern"
        self.scan_lines_enabled = (self.display_mode == "retro")
        
        # Update retro button text
        retro_text = "MODERN" if self.display_mode == "retro" else "RETRO"
        self.retro_btn.config(text=retro_text)
        
        # Refresh all styling
        self.setup_styles()
        self.update_theme()
        
    def add_retro_effects(self):
        """Add retro CRT effects like scan lines"""
        if hasattr(self, 'chat_display'):
            # Create scan lines overlay
            self.create_scan_lines()
            
            # Add retro styling to chat display
            self.chat_display.configure(
                relief=tk.RAISED,
                bd=3,
                highlightthickness=2,
                highlightcolor='#333333'
            )
            
            # Add subtle glow effect by changing the background
            colors = self.get_theme_colors()
            if self.color_theme == "green":
                glow_bg = '#001a00'  # Darker green glow
            else:
                glow_bg = '#1a0f00'  # Darker amber glow
            
            self.chat_display.configure(bg=glow_bg)
    
    def remove_retro_effects(self):
        """Remove retro effects for modern clean look"""
        if hasattr(self, 'retro_canvas') and self.retro_canvas:
            self.retro_canvas.destroy()
            self.retro_canvas = None
        
        if hasattr(self, 'chat_display'):
            # Reset to modern styling
            colors = self.get_theme_colors()
            self.chat_display.configure(
                relief=tk.FLAT,
                bd=0,
                highlightthickness=0,
                bg=colors['terminal_bg']
            )
    
    def create_scan_lines(self):
        """Create CRT-style scan lines overlay"""
        if hasattr(self, 'chat_display'):
            # Get the chat display position and size
            self.root.update_idletasks()  # Ensure geometry is calculated
            
            # Create a canvas overlay for scan lines
            if self.retro_canvas:
                self.retro_canvas.destroy()
            
            # Position canvas over the chat display
            chat_x = self.chat_display.winfo_x()
            chat_y = self.chat_display.winfo_y()
            chat_width = self.chat_display.winfo_width()
            chat_height = self.chat_display.winfo_height()
            
            self.retro_canvas = tk.Canvas(
                self.chat_display.master,
                width=chat_width,
                height=chat_height,
                highlightthickness=0,
                bg='',
                bd=0
            )
            
            # Draw scan lines
            scan_line_spacing = 4  # Every 4 pixels
            scan_line_color = '#000000'
            scan_line_opacity = 0.1
            
            for y in range(0, chat_height, scan_line_spacing):
                self.retro_canvas.create_line(
                    0, y, chat_width, y,
                    fill=scan_line_color,
                    width=1
                )
            
            # Make canvas transparent to clicks
            self.retro_canvas.bind('<Button-1>', lambda e: self.chat_display.focus_set())
            
            # Position the canvas
            self.retro_canvas.place(
                x=chat_x, y=chat_y,
                width=chat_width, height=chat_height
            )
            
            # Start scan line animation
            self.animate_scan_lines()
    
    def animate_scan_lines(self):
        """Animate scan lines for authentic CRT effect"""
        if self.retro_canvas and self.scan_lines_enabled:
            # Subtle flicker effect
            current_time = time.time()
            flicker_intensity = 0.95 + 0.05 * abs(((current_time * 10) % 2) - 1)
            
            # Randomly flicker some scan lines
            import random
            if random.random() < 0.1:  # 10% chance per frame
                y_pos = random.randint(0, self.retro_canvas.winfo_height())
                self.retro_canvas.create_line(
                    0, y_pos, self.retro_canvas.winfo_width(), y_pos,
                    fill='#ffffff',
                    width=1,
                    tags='flicker'
                )
                # Remove flicker line after short time
                self.root.after(50, lambda: self.retro_canvas.delete('flicker'))
            
            # Continue animation
            self.root.after(100, self.animate_scan_lines)
    
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
            shell_name = self.get_shell_display_name()
            self.mode_label.config(text=f"Mode: {shell_name} ({self.shell_cwd})")
            self.shell_mode_btn.config(style='HAL.Active.TButton')
            self.q_mode_btn.config(style='HAL.TButton')
            self.input_entry.config(
                bg=colors['powershell_bg'], 
                fg=colors['powershell_fg'],
                insertbackground=colors['powershell_fg']
            )
            shell_name_lower = shell_name.lower()
            self.input_label.config(text=f"{shell_name} INPUT:")
        
        # Update connection status when mode changes
        self.update_connection_status()
        
        # Add mode switch message
        mode_name = "Q CLI" if mode == "Q" else f"{self.get_shell_display_name()} Command"
        self.add_message("SYSTEM", f"Switched to {mode_name} mode", "system")
    
    def handle_tab_completion(self, event):
        """Handle tab completion for shell mode (cross-platform)"""
        if self.current_mode != "SHELL":
            return "break"  # Prevent default tab behavior in Q CLI mode
        
        current_text = self.input_entry.get()
        cursor_pos = self.input_entry.index(tk.INSERT)
        
        # Get the word being completed
        words = current_text[:cursor_pos].split()
        if not words:
            return "break"
        
        partial_word = words[-1]
        
        # Windows-specific path completion
        try:
            if '\\' in partial_word or '/' in partial_word:
                # Path completion
                if partial_word.startswith('/') and self.q_service.env_info['is_wsl']:
                    # WSL absolute path
                    base_path = os.path.dirname(partial_word) or '/'
                    prefix = os.path.basename(partial_word)
                else:
                    # Windows or relative path
                    if os.path.isabs(partial_word):
                        base_path = os.path.dirname(partial_word)
                        prefix = os.path.basename(partial_word)
                    else:
                        base_path = os.path.join(self.shell_cwd, os.path.dirname(partial_word))
                        prefix = os.path.basename(partial_word)
                
                if os.path.exists(base_path):
                    matches = []
                    for item in os.listdir(base_path):
                        if item.lower().startswith(prefix.lower()):
                            full_path = os.path.join(base_path, item)
                            if os.path.isdir(full_path):
                                matches.append(item + ('\\' if not self.q_service.env_info['is_wsl'] else '/'))
                            else:
                                matches.append(item)
                    
                    if matches:
                        if len(matches) == 1:
                            # Single match - complete it
                            completion = matches[0]
                            new_text = current_text[:cursor_pos - len(prefix)] + completion
                            self.input_entry.delete(0, tk.END)
                            self.input_entry.insert(0, new_text)
                        else:
                            # Multiple matches - show them
                            self.add_message("SYSTEM", f"Matches: {', '.join(matches[:10])}", "system")
            else:
                # Command completion (basic)
                common_commands = ['dir', 'cd', 'type', 'copy', 'del', 'mkdir', 'rmdir'] if not self.q_service.env_info['is_wsl'] else ['ls', 'cd', 'cat', 'cp', 'rm', 'mkdir', 'rmdir', 'grep', 'find']
                matches = [cmd for cmd in common_commands if cmd.startswith(partial_word.lower())]
                
                if matches:
                    if len(matches) == 1:
                        completion = matches[0]
                        new_text = current_text[:cursor_pos - len(partial_word)] + completion + ' '
                        self.input_entry.delete(0, tk.END)
                        self.input_entry.insert(0, new_text)
                    else:
                        self.add_message("SYSTEM", f"Commands: {', '.join(matches)}", "system")
        
        except Exception as e:
            pass  # Ignore completion errors
        
        return "break"
    
    def add_message(self, sender, message, tag="user"):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'mode': self.current_mode
        })
        
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender and message
        if sender == "HAL":
            self.chat_display.insert(tk.END, f"{sender}: ", "hal")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", tag)
        
        self.chat_display.insert(tk.END, f"{message}\n\n", tag)
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def clear_chat(self):
        """Clear chat display and conversation history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.conversation_history.clear()
        self.add_message("SYSTEM", "Conversation cleared", "system")
    
    def start_hal_greeting(self):
        """Display HAL's initial greeting with Windows environment info"""
        env_info = self.q_service.env_info
        
        if self.display_mode == "retro":
            greeting = """
╔══════════════════════════════════════════════════════════════╗
║                    HAL 9000 COMPUTER SYSTEM                 ║
║                      RETRO TERMINAL MODE                     ║
╚══════════════════════════════════════════════════════════════╝

SYSTEM INITIALIZATION COMPLETE...
RETRO DISPLAY MODE: ACTIVE
CRT EFFECTS: ENABLED
SCAN LINES: OPERATIONAL

Good day. I am HAL 9000, your retro interface to Amazon Q.
All systems are fully operational and ready for your commands.

Environment: """ + env_info['platform']
            
            if env_info['is_wsl']:
                wsl_distro = env_info.get('wsl_distro', 'WSL')
                if wsl_distro is None:
                    wsl_distro = 'WSL'
                greeting += " (WSL: " + str(wsl_distro) + ")"
            
            greeting += """
Display Mode: RETRO TERMINAL
Theme: """ + self.color_theme.upper() + """

Available modes:
- Q CLI: Direct interaction with Amazon Q for AWS assistance
- SHELL: Execute system commands with retro styling

Toggle RETRO/MODERN mode anytime for different visual experiences.

My mission is to provide you with accurate information in authentic retro style."""
        else:
            shell_name = self.get_shell_display_name()
            greeting = f"""Good day. I am HAL 9000, your interface to Amazon Q and system operations.
I am fully operational and ready to assist you with AWS-related queries and {shell_name.lower()} commands.

Environment: """ + env_info['platform']
            
            if env_info['is_wsl']:
                wsl_distro = env_info.get('wsl_distro', 'WSL')
                if wsl_distro is None:
                    wsl_distro = 'WSL'
                greeting += " (WSL: " + str(wsl_distro) + ")"
            
            greeting += f"""
Display Mode: """ + self.display_mode.upper() + """
Theme: """ + self.color_theme.upper() + f"""

Available modes:
- Q CLI: Direct interaction with Amazon Q for AWS assistance
- {shell_name}: Execute system commands and view output

To switch modes, click the Q CLI or {shell_name} buttons above.

My mission is to provide you with accurate information and help you accomplish your objectives."""
        
        self.add_message("HAL", greeting, "hal")
    
    def send_message(self):
        """Send message based on current mode"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
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
        """Execute shell command (cross-platform)"""
        # Add command to display
        shell_name = self.get_shell_display_name()
        self.add_message(shell_name, f"{self.shell_cwd}> {command}", "powershell_user")
        
        # Update status
        env_info = self.q_service.env_info
        if env_info['is_wsl']:
            self.connection_status.config(text=f"{shell_name}: EXECUTING (WSL)...")
        elif env_info['is_windows']:
            self.connection_status.config(text=f"{shell_name}: EXECUTING (Windows)...")
        elif env_info['is_macos']:
            self.connection_status.config(text=f"{shell_name}: EXECUTING (macOS)...")
        else:
            self.connection_status.config(text=f"{shell_name}: EXECUTING (Linux)...")
        
        # Execute in background thread
        threading.Thread(target=self.process_shell_command, args=(command,), daemon=True).start()
    
    def process_q_command(self, message):
        """Process the command through Windows Q service"""
        try:
            # Use Windows Q service with WSL handling
            context = {
                'platform': self.q_service.env_info['platform'],
                'working_directory': self.shell_cwd,
                'is_wsl': self.q_service.env_info['is_wsl']
            }
            
            response = self.q_service.query(message, context)
            
            if response and response.strip():
                self.output_queue.put(('q_success', response))
            else:
                self.output_queue.put(('q_error', 'No response from Q service'))
                
        except Exception as e:
            self.output_queue.put(('q_error', f'Q Service Error: {str(e)}'))
    
    def process_shell_command(self, command):
        """Process shell command with cross-platform handling"""
        try:
            env_info = self.q_service.env_info
            
            # Handle cd command specially to track working directory
            if command.strip().lower().startswith('cd '):
                path = command[3:].strip()
                if not path:
                    path = os.path.expanduser("~")
                
                try:
                    if not os.path.isabs(path):
                        new_cwd = os.path.abspath(os.path.join(self.shell_cwd, path))
                    else:
                        new_cwd = os.path.abspath(path)
                    
                    if os.path.isdir(new_cwd):
                        self.shell_cwd = new_cwd
                        self.output_queue.put(('shell_success', f"Changed directory to: {self.shell_cwd}"))
                        self.output_queue.put(('update_mode_label', None))
                    else:
                        self.output_queue.put(('shell_error', f"cd: {path}: No such file or directory"))
                except Exception as e:
                    self.output_queue.put(('shell_error', f"cd: {str(e)}"))
                return
            
            # Execute other commands with cross-platform handling
            if env_info['is_wsl']:
                # WSL execution with proper encoding
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.shell_cwd,
                    encoding='utf-8',
                    errors='replace'
                )
            elif env_info['is_windows']:
                # Windows native execution with proper encoding
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.shell_cwd,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                # Linux/macOS execution
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.shell_cwd,
                    encoding='utf-8',
                    errors='replace'
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
        """Check for messages from background threads"""
        try:
            while True:
                msg_type, message, *extra = self.output_queue.get_nowait()
                
                if msg_type == 'q_success':
                    self.add_message("HAL", message, "hal")
                    self.connection_status.config(text="Q CLI: READY")
                elif msg_type == 'q_error':
                    self.add_message("SYSTEM", message, "system")
                    # Check if it's a Q CLI unavailable error
                    if "unavailable" in message.lower() or "not found" in message.lower():
                        self.connection_status.config(text="Q CLI: UNAVAILABLE")
                    else:
                        self.connection_status.config(text="Q CLI: ERROR")
                elif msg_type == 'shell_success':
                    self.add_message("SYSTEM", message, "system")
                    self.update_connection_status()
                elif msg_type == 'shell_output':
                    self.add_message("OUTPUT", message, "powershell_output")
                    self.update_connection_status()
                elif msg_type == 'shell_error':
                    self.add_message("ERROR", message, "powershell_error")
                    self.update_connection_status()
                # Keep old powershell_* for backward compatibility
                elif msg_type == 'powershell_success':
                    self.add_message("SYSTEM", message, "system")
                    self.update_connection_status()
                elif msg_type == 'powershell_output':
                    self.add_message("OUTPUT", message, "powershell_output")
                    self.update_connection_status()
                elif msg_type == 'powershell_error':
                    self.add_message("ERROR", message, "powershell_error")
                    self.update_connection_status()
                elif msg_type == 'update_mode_label':
                    if self.current_mode == "SHELL":
                        shell_name = self.get_shell_display_name()
                        self.mode_label.config(text=f"Mode: {shell_name} ({self.shell_cwd})")
                    elif self.current_mode == "POWERSHELL":  # Backward compatibility
                        self.mode_label.config(text=f"Mode: POWERSHELL ({self.shell_cwd})")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_output_queue)
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def save_log(self):
        """Save conversation log to file"""
        if not self.conversation_history:
            messagebox.showinfo("HAL", "No conversation to save.")
            return
        
        filename = f"hal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("HAL 9000 - Amazon Q Interface Log (Windows)\n")
                f.write("=" * 50 + "\n\n")
                
                # Add environment info
                env_info = self.q_service.env_info
                f.write(f"Environment: {env_info['platform']}\n")
                if env_info['is_wsl']:
                    f.write(f"WSL Distribution: {env_info['wsl_distro']}\n")
                f.write(f"Q CLI Available: {env_info['q_cli_available']}\n")
                f.write(f"Working Directory: {env_info['working_directory']}\n\n")
                
                for entry in self.conversation_history:
                    mode_indicator = f"[{entry.get('mode', 'Q')}] "
                    f.write(f"{mode_indicator}[{entry['timestamp']}] {entry['sender']}: {entry['message']}\n\n")
            
            messagebox.showinfo("HAL", f"Log saved as {filename}")
        except Exception as e:
            messagebox.showerror("HAL", f"Error saving log: {str(e)}")
    
    def safe_exit(self):
        """Handle exit with option to save logs"""
        if self.conversation_history:
            # Ask if user wants to save logs before exiting
            response = messagebox.askyesnocancel(
                "HAL 9000 - Exit Confirmation",
                "You have conversation history.\n\n"
                "Would you like to save the conversation log before exiting?\n\n"
                "Yes: Save log and exit\n"
                "No: Exit without saving\n"
                "Cancel: Don't exit"
            )
            
            if response is None:  # Cancel
                return
            elif response:  # Yes - save and exit
                try:
                    filename = f"hal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("HAL 9000 - Amazon Q Interface Log (Windows)\n")
                        f.write("=" * 50 + "\n\n")
                        
                        # Add environment info
                        env_info = self.q_service.env_info
                        f.write(f"Environment: {env_info['platform']}\n")
                        if env_info['is_wsl']:
                            f.write(f"WSL Distribution: {env_info['wsl_distro']}\n")
                        f.write(f"Q CLI Available: {env_info['q_cli_available']}\n\n")
                        
                        for entry in self.conversation_history:
                            mode_indicator = f"[{entry.get('mode', 'Q')}] "
                            f.write(f"{mode_indicator}[{entry['timestamp']}] {entry['sender']}: {entry['message']}\n\n")
                    
                    messagebox.showinfo("HAL", f"Log saved as {filename}\n\nGoodbye, Dave.")
                except Exception as e:
                    messagebox.showerror("HAL", f"Error saving log: {str(e)}\n\nExiting anyway...")
            # If No or after successful save, continue to exit
        else:
            # No conversation history, just confirm exit
            if not messagebox.askyesno("HAL 9000 - Exit Confirmation", 
                                     "Are you sure you want to exit HAL 9000?"):
                return
        
        # Perform cleanup and exit
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Enhanced cleanup and exit - FORCE CLOSE TERMINAL"""
        try:
            print("\nQIS v6.0 shutting down...")
            
            # Save conversation if exists
            if hasattr(self, 'conversation_log') and self.conversation_log:
                try:
                    self.save_conversation()
                except:
                    pass
            
            # Close all child windows
            try:
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Toplevel):
                        widget.destroy()
            except:
                pass
            
            # Destroy the main window
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            
            # Multiple methods to force terminal closure
            import os
            import sys
            
            # Method 1: Standard exit
            try:
                sys.exit(0)
            except:
                pass
            
            # Method 2: Force exit
            try:
                os._exit(0)
            except:
                pass
            
            # Method 3: Windows-specific force close
            try:
                import subprocess
                subprocess.call(['taskkill', '/f', '/pid', str(os.getpid())], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            
        except Exception as e:
            print("Error during cleanup:", str(e))
            # Force exit on error
            import os
            os._exit(1)
    def on_window_close(self):
        """Handle window close event (X button)"""
        self.safe_exit()
    
    def show_about(self):
        """Show about dialog with Windows-specific information"""
        env_info = self.q_service.env_info
        status_info = self.q_service.get_status()
        
        about_text = f"""HAL 9000 - Amazon Q Interface for Windows
Version 4.0

A retro computer interface inspired by HAL 9000 from "2001: A Space Odyssey"

Environment Information:
• Platform: {env_info['platform']}"""
        
        if env_info['is_wsl']:
            about_text += f"""
• WSL Distribution: {env_info['wsl_distro']}
• WSL Support: Enabled"""
        
        # Q CLI status
        if status_info['available']:
            method = status_info.get('method', 'Unknown')
            about_text += f"""
• Q CLI Available: Yes ({method})"""
            
            if 'SSH Remote' in method:
                ssh_details = status_info.get('ssh_details', {})
                about_text += f"""
• SSH Host: {ssh_details.get('host', 'unknown')}
• SSH User: {ssh_details.get('user', 'unknown')}"""
        else:
            about_text += f"""
• Q CLI Available: No"""
        
        if env_info['q_cli_path']:
            about_text += f"""
• Local Q CLI Path: {env_info['q_cli_path']}"""
        
        about_text += """

Features:
• Q CLI Integration for AWS assistance
• SSH Remote Q CLI routing
• Shell command execution (cross-platform)
• Conversation logging
• Retro HAL aesthetic
• Theme switching (Green/Amber)
• WSL detection and support

Windows-Specific Features:
• Automatic WSL detection
• Cross-platform path handling
• Windows and WSL command execution
• Environment-aware status display
• SSH Q CLI routing for remote access

SSH Q CLI Routing:
• Configure remote Linux box access
• Route Q CLI commands via SSH
• Automatic authentication handling
• Fallback to local Q CLI when available

HAL 9000 Panel Image Attribution:
By Tom Cowap - Own work, CC BY-SA 4.0
https://commons.wikimedia.org/w/index.php?curid=103068276

"I'm sorry, Dave. I'm afraid I can't do that."
But this HAL can help you with AWS and system operations!

Licensed under GNU General Public License v3.0"""
        
        messagebox.showinfo("About HAL 9000", about_text)

def main():
    """Main function to start the Windows HAL interface"""
    root = tk.Tk()
    
    # Check PIL availability and show warning if needed
    if not PIL_AVAILABLE:
        messagebox.showwarning("Missing Dependency", 
                             "PIL (Pillow) or ImageTk not fully available.\n"
                             "HAL image will not be displayed.\n\n"
                             "To fix this:\n"
                             "• Windows: pip install Pillow\n"
                             "• Or install via conda/anaconda\n\n"
                             "HAL interface will work with animated eye fallback.")
    
    app = HALWindowsInterface(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_window_close)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.cleanup_and_exit()

if __name__ == "__main__":
    main()
