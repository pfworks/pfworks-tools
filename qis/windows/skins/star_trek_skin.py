#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Star Trek Skin Configuration for HAL 9000 v5.0
Transforms the interface into a Star Trek computer system
"""

from .base_skin import BaseSkin

class StarTrekSkin(BaseSkin):
    """Star Trek LCARS-inspired skin configuration"""
    
    def __init__(self):
        BaseSkin.__init__(self)
        self.name = "Star Trek LCARS"
        self.version = "1.0"
        self.description = "Star Trek LCARS computer interface theme"
        
    def get_identity(self):
        """Star Trek computer identity"""
        return {
            'name': 'Computer',
            'full_name': 'Starfleet Computer System',
            'version': '24th Century',
            'origin': 'Star Trek: The Next Generation',
            'personality': 'helpful, efficient, professional',
            'greeting_name': 'Captain'
        }
    
    def get_colors(self):
        """LCARS color scheme - toned down for better usability"""
        return {
            'primary': '#FF9900',      # LCARS orange
            'secondary': '#6666CC',    # Darker LCARS blue (less obnoxious)
            'background': '#000000',   # Black background
            'text': '#FFCC99',         # Light orange text
            'accent': '#9999CC',       # Muted purple
            'error': '#FF6666',        # Light red
            'success': '#99FF99',      # Light green
            'warning': '#FFFF99',      # Light yellow
            'button_bg': '#FF9900',    # LCARS orange buttons
            'button_fg': '#000000',    # Black button text
            'input_bg': '#222244',     # Dark blue input (less bright)
            'input_fg': '#FFCC99',     # Light orange input text
            'panel_bg': '#111133',     # Very dark blue panels (much less obnoxious)
            'panel_fg': '#FFCC99',     # Light orange panel text
            'cursor': '#FF9900',       # Orange cursor
            'border': '#6666CC'        # Darker blue borders
        }
    
    def get_fonts(self):
        """LCARS-style fonts"""
        return {
            'terminal_fonts': [
                'Antonio',
                'Orbitron',
                'Exo 2',
                'Rajdhani',
                'Source Code Pro',
                'Consolas'
            ],
            'modern_fonts': [
                'Antonio',
                'Orbitron',
                'Exo 2',
                'Rajdhani',
                'Segoe UI',
                'Arial'
            ],
            'sizes': {
                'small': 9,
                'normal': 11,
                'large': 13,
                'title': 16
            }
        }
    
    def get_messages(self):
        """Star Trek computer messages"""
        return {
            'startup': [
                "Starfleet Computer System online.",
                "All systems operational and ready for input.",
                "Welcome aboard, {greeting_name}. How may I assist you today?"
            ],
            'retro_startup': [
                "STARFLEET COMPUTER SYSTEM",
                "LCARS INTERFACE v{version}",
                "STATUS: ALL SYSTEMS OPERATIONAL",
                "",
                "Computer online. Welcome aboard, {greeting_name}.",
                "Amazon Q interface ready for your commands.",
                "Please state the nature of your request."
            ],
            'mode_switch': {
                'q_cli': "Switching to Amazon Q interface",
                'powershell': "Accessing system command interface"
            },
            'errors': {
                'q_unavailable': "Unable to access Amazon Q interface, {greeting_name}.",
                'connection_failed': "Communication with Q service has been interrupted.",
                'command_failed': "Unable to process command. Please try again."
            },
            'farewells': [
                "Goodbye, {greeting_name}. Computer standing by.",
                "Thank you for using Starfleet systems.",
                "Computer offline. Have a pleasant day."
            ],
            'acknowledgments': [
                "Acknowledged.",
                "Processing request.",
                "Command received.",
                "Working...",
                "Accessing database.",
                "Query in progress."
            ],
            'status_reports': [
                "All systems nominal.",
                "Operating within normal parameters.",
                "No anomalies detected.",
                "Systems functioning normally."
            ]
        }
    
    def get_interface(self):
        """LCARS interface configuration"""
        return {
            'window_title': 'Starfleet Computer - Amazon Q Interface',
            'window_size': '1400x900',
            'button_labels': {
                'q_cli': 'AMAZON Q',
                'powershell': 'SYSTEM CMD',
                'clear': 'CLEAR LOG',
                'save': 'SAVE LOG',
                'exit': 'LOGOUT',
                'retro_toggle': 'LCARS',
                'modern_toggle': 'STANDARD',
                'theme_toggle': 'BLUE MODE',
                'settings': 'Q CONFIG',
                'ssh': 'REMOTE',
                'about': 'SYSTEM INFO'
            },
            'status_labels': {
                'operational': 'System Status: OPERATIONAL',
                'limited': 'System Status: LIMITED ACCESS',
                'error': 'System Status: ERROR',
                'q_ready': 'Amazon Q: ONLINE',
                'q_unavailable': 'Amazon Q: OFFLINE'
            },
            'panel_labels': {
                'main': 'MAIN COMPUTER',
                'status': 'SYSTEM STATUS',
                'mode': 'INTERFACE MODE',
                'environment': 'ENVIRONMENT',
                'connection': 'CONNECTION STATUS'
            }
        }
    
    def get_assets(self):
        """Star Trek assets"""
        return {
            'main_image': 'assets/star_trek_computer.png',
            'icon': 'assets/starfleet_delta.ico',
            'sounds': {
                'startup': 'assets/sounds/computer_beep.wav',
                'error': 'assets/sounds/red_alert.wav',
                'success': 'assets/sounds/acknowledge.wav'
            },
            'animations': {
                'lcars_sweep': True,
                'panel_glow': True,
                'text_scroll': True
            }
        }
    
    def get_lcars_elements(self):
        """LCARS-specific interface elements"""
        return {
            'rounded_corners': True,
            'panel_separators': True,
            'animated_elements': True,
            'color_coding': {
                'critical': '#FF6666',
                'warning': '#FFFF99',
                'caution': '#FF9900',
                'normal': '#9999FF',
                'success': '#99FF99'
            },
            'button_styles': {
                'primary': {
                    'bg': '#FF9900',
                    'fg': '#000000',
                    'shape': 'rounded_rect'
                },
                'secondary': {
                    'bg': '#9999FF',
                    'fg': '#000000',
                    'shape': 'rounded_rect'
                },
                'alert': {
                    'bg': '#FF6666',
                    'fg': '#FFFFFF',
                    'shape': 'rounded_rect'
                }
            }
        }
