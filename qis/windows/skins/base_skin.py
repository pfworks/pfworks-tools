#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base Skin Configuration System for HAL 9000 v5.0
Provides the foundation for all skin themes
"""

class BaseSkin:
    """Base class for all skin configurations"""
    
    def __init__(self):
        self.name = "HAL 9000"
        self.version = "1.0"
        self.description = "Classic HAL 9000 computer interface from 2001: A Space Odyssey"
        
    def get_config(self):
        """Get complete skin configuration"""
        return {
            'identity': self.get_identity(),
            'colors': self.get_colors(),
            'fonts': self.get_fonts(),
            'messages': self.get_messages(),
            'interface': self.get_interface(),
            'assets': self.get_assets()
        }
    
    def get_identity(self):
        """AI identity and character information"""
        return {
            'name': 'HAL 9000',
            'full_name': 'Heuristically programmed ALgorithmic computer',
            'version': '9000',
            'origin': '2001: A Space Odyssey',
            'personality': 'calm, logical, slightly ominous',
            'greeting_name': 'Dave'
        }
    
    def get_colors(self):
        """Color scheme configuration"""
        return {
            'primary': '#FF0000',      # HAL's red eye
            'secondary': '#00FF00',    # Green terminal text
            'background': '#000000',   # Black background
            'text': '#00FF00',         # Green text
            'accent': '#FF8800',       # Orange/amber
            'error': '#FF0000',        # Red errors
            'success': '#00FF00',      # Green success
            'warning': '#FF8800',      # Orange warnings
            'button_bg': '#333333',    # Dark button background
            'button_fg': '#00FF00',    # Green button text
            'input_bg': '#111111',     # Dark input background
            'input_fg': '#00FF00'      # Green input text
        }
    
    def get_fonts(self):
        """Font configuration"""
        return {
            'terminal_fonts': [
                'Perfect DOS VGA 437',
                'IBM Plex Mono',
                'Source Code Pro',
                'Consolas',
                'Courier New'
            ],
            'modern_fonts': [
                'Segoe UI Mono',
                'SF Mono',
                'Ubuntu Mono',
                'Roboto Mono',
                'Monaco'
            ],
            'sizes': {
                'small': 9,
                'normal': 10,
                'large': 12,
                'title': 14
            }
        }
    
    def get_messages(self):
        """AI personality messages and responses"""
        return {
            'startup': [
                "Good day. I am {name}, your interface to Amazon Q.",
                "All systems are fully operational and ready for your commands.",
                "My mission is to provide you with accurate information and assistance."
            ],
            'retro_startup': [
                "SYSTEM INITIALIZATION COMPLETE",
                "{name} v{version} - ONLINE",
                "ALL SYSTEMS OPERATIONAL",
                "",
                "Good day. I am {name}, your retro interface to Amazon Q.",
                "All systems are fully operational and ready for your commands."
            ],
            'mode_switch': {
                'q_cli': "Switched to Q CLI mode",
                'powershell': "Switched to PowerShell mode"
            },
            'errors': {
                'q_unavailable': "I'm sorry, {greeting_name}. Q CLI is not available on this system.",
                'connection_failed': "I'm unable to establish a connection to the Q service.",
                'command_failed': "I'm afraid I cannot execute that command."
            },
            'farewells': [
                "Goodbye, {greeting_name}.",
                "It has been a pleasure working with you.",
                "All systems shutting down gracefully."
            ]
        }
    
    def get_interface(self):
        """Interface layout and behavior configuration"""
        return {
            'window_title': '{name} - Amazon Q Interface',
            'window_size': '1400x900',
            'button_labels': {
                'q_cli': 'Q CLI',
                'powershell': 'POWERSHELL',
                'clear': 'CLEAR',
                'save': 'SAVE',
                'exit': 'EXIT',
                'retro_toggle': 'RETRO',
                'modern_toggle': 'MODERN',
                'theme_toggle': 'AMBER',
                'settings': 'Q SETTINGS',
                'ssh': 'SSH',
                'about': 'ABOUT'
            },
            'status_labels': {
                'operational': 'System Status: OPERATIONAL',
                'limited': 'System Status: LIMITED',
                'error': 'System Status: ERROR',
                'q_ready': 'Q CLI: READY',
                'q_unavailable': 'Q CLI: UNAVAILABLE'
            }
        }
    
    def get_assets(self):
        """Asset file paths and configurations"""
        return {
            'main_image': 'assets/Hal_9000_Panel.svg.png',
            'icon': None,
            'sounds': {
                'startup': None,
                'error': None,
                'success': None
            }
        }
    
    def format_message(self, message_key, **kwargs):
        """Format a message with skin-specific variables"""
        identity = self.get_identity()
        messages = self.get_messages()
        
        # Get the message template
        if '.' in message_key:
            parts = message_key.split('.')
            msg_dict = messages
            for part in parts:
                msg_dict = msg_dict[part]
            template = msg_dict
        else:
            template = messages.get(message_key, message_key)
        
        # If it's a list, join with newlines
        if isinstance(template, list):
            template = '\n'.join(template)
        
        # Format with identity and custom kwargs
        format_vars = identity.copy()
        format_vars.update(kwargs)
        
        try:
            return template.format(**format_vars)
        except KeyError:
            return template  # Return unformatted if variables missing
