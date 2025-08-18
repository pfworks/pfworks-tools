#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TRS-80 Model I Skin Configuration for HAL 9000 v5.0
Transforms the interface into a classic TRS-80 Model I computer from 1977
"""

from .base_skin import BaseSkin

class Retro80sSkin(BaseSkin):
    """TRS-80 Model I retro computer skin configuration"""
    
    def __init__(self):
        BaseSkin.__init__(self)
        self.name = "TRS-80 Model I"
        self.version = "1.0"
        self.description = "Classic TRS-80 Model I computer interface from 1977"
        
    def get_identity(self):
        """TRS-80 Model I computer identity"""
        return {
            'name': 'TRS-80',
            'full_name': 'Tandy Radio Shack TRS-80 Model I',
            'version': 'Level II BASIC',
            'origin': 'Radio Shack 1977',
            'personality': 'helpful, straightforward, classic',
            'greeting_name': 'Operator'
        }
    
    def get_colors(self):
        """Classic TRS-80 black and white color scheme"""
        return {
            'primary': '#FFFFFF',      # White text (classic TRS-80)
            'secondary': '#C0C0C0',    # Light gray
            'background': '#000000',   # Black background
            'text': '#FFFFFF',         # White text on black
            'accent': '#C0C0C0',       # Light gray accents
            'error': '#FFFFFF',        # White error text (no color on TRS-80)
            'success': '#FFFFFF',      # White success text
            'warning': '#C0C0C0',      # Gray warning
            'button_bg': '#FFFFFF',    # White buttons
            'button_fg': '#000000',    # Black button text
            'input_bg': '#000000',     # Black input background
            'input_fg': '#FFFFFF',     # White input text
            'panel_bg': '#000000',     # Black panels
            'panel_fg': '#FFFFFF',     # White panel text
            'cursor': '#FFFFFF',       # White cursor
            'border': '#C0C0C0'        # Gray borders
        }
    
    def get_fonts(self):
        """TRS-80 style monospace fonts"""
        return {
            'terminal_fonts': [
                'Courier New',
                'Consolas',
                'Monaco',
                'Lucida Console',
                'DejaVu Sans Mono',
                'Liberation Mono'
            ],
            'modern_fonts': [
                'Courier New',
                'Consolas',
                'Monaco',
                'Lucida Console',
                'DejaVu Sans Mono'
            ],
            'sizes': {
                'small': 9,
                'normal': 11,
                'large': 13,
                'title': 16
            }
        }
    
    def get_messages(self):
        """TRS-80 Model I computer messages"""
        return {
            'startup': [
                "TRS-80 MODEL I MICROCOMPUTER SYSTEM",
                "LEVEL II BASIC READY",
                "Amazon Q interface loaded. Ready for input, {greeting_name}."
            ],
            'retro_startup': [
                "╔══════════════════════════════════════╗",
                "║     TRS-80 MODEL I MICROCOMPUTER     ║",
                "║         LEVEL II BASIC v{version}         ║",
                "║      RADIO SHACK TANDY CORP 1977    ║",
                "╚══════════════════════════════════════╝",
                "",
                "MEMORY SIZE? 16K",
                "TERMINAL WIDTH? 64",
                "",
                "TRS-80 MODEL I MICROCOMPUTER SYSTEM",
                "LEVEL II BASIC READY",
                "",
                "Amazon Q interface loaded.",
                "Ready for input, {greeting_name}.",
                "",
                "Type commands or questions to begin."
            ],
            'mode_switch': {
                'q_cli': "Loading Amazon Q interface...",
                'powershell': "Accessing system commands..."
            },
            'errors': {
                'q_unavailable': "?SN ERROR - Amazon Q not available, {greeting_name}.",
                'connection_failed': "?IO ERROR - Connection to Q service failed.",
                'command_failed': "?SYNTAX ERROR - Command not recognized."
            },
            'farewells': [
                "SYSTEM HALT",
                "Thank you for using TRS-80, {greeting_name}.",
                "Ready to power down."
            ],
            'acknowledgments': [
                "OK",
                "READY",
                "PROCESSING...",
                "WORKING...",
                "LOADING...",
                "SEARCHING...",
                "COMPUTING..."
            ],
            'status_reports': [
                "SYSTEM OK",
                "ALL FUNCTIONS NORMAL",
                "READY FOR INPUT",
                "OPERATING NORMALLY",
                "NO ERRORS DETECTED"
            ],
            'prompts': [
                "READY",
                "OK",
                ">",
                "INPUT:",
                "COMMAND:"
            ]
        }
    
    def get_interface(self):
        """TRS-80 Model I interface configuration"""
        return {
            'window_title': 'TRS-80 MODEL I - Amazon Q Interface',
            'window_size': '1400x900',
            'button_labels': {
                'q_cli': 'AMAZON Q',
                'powershell': 'SYSTEM',
                'clear': 'CLEAR',
                'save': 'SAVE',
                'exit': 'HALT',
                'retro_toggle': 'TRS-80',
                'modern_toggle': 'STANDARD',
                'theme_toggle': 'INVERSE',
                'settings': 'CONFIG',
                'ssh': 'REMOTE',
                'about': 'INFO'
            },
            'status_labels': {
                'operational': 'SYSTEM STATUS: OK',
                'limited': 'SYSTEM STATUS: LIMITED',
                'error': 'SYSTEM STATUS: ERROR',
                'q_ready': 'Amazon Q: READY',
                'q_unavailable': 'Amazon Q: NOT FOUND'
            },
            'panel_labels': {
                'main': 'TRS-80 TERMINAL',
                'status': 'SYSTEM STATUS',
                'mode': 'CURRENT MODE',
                'environment': 'ENVIRONMENT',
                'connection': 'CONNECTION'
            }
        }
    
    def get_assets(self):
        """TRS-80 Model I assets"""
        return {
            'main_image': 'assets/trs80_model1.png',
            'icon': 'assets/trs80_icon.ico',
            'sounds': {
                'startup': 'assets/sounds/trs80_boot.wav',
                'error': 'assets/sounds/trs80_error.wav',
                'success': 'assets/sounds/trs80_ok.wav'
            },
            'animations': {
                'cursor_blink': True,
                'text_scroll': True,
                'character_display': True
            }
        }
    
    def get_trs80_elements(self):
        """TRS-80 Model I specific interface elements"""
        return {
            'monochrome_display': True,
            'character_mode': True,
            'cursor_blink': True,
            'uppercase_preference': True,
            'color_scheme': {
                'normal': '#FFFFFF',      # White on black
                'inverse': '#000000',     # Black on white (for highlights)
                'dim': '#C0C0C0'         # Gray for secondary text
            },
            'button_styles': {
                'primary': {
                    'bg': '#FFFFFF',
                    'fg': '#000000',
                    'shape': 'rectangle',
                    'border': '#C0C0C0'
                },
                'secondary': {
                    'bg': '#C0C0C0',
                    'fg': '#000000',
                    'shape': 'rectangle',
                    'border': '#FFFFFF'
                },
                'alert': {
                    'bg': '#000000',
                    'fg': '#FFFFFF',
                    'shape': 'rectangle',
                    'border': '#FFFFFF'
                }
            },
            'ascii_art': {
                'logo': [
                    "╔══════════════════════════════════════╗",
                    "║     TRS-80 MODEL I MICROCOMPUTER     ║",
                    "║         RADIO SHACK TANDY CORP       ║",
                    "║              EST. 1977               ║",
                    "╚══════════════════════════════════════╝"
                ],
                'prompt': [
                    "READY",
                    ">"
                ]
            },
            'display_characteristics': {
                'width': 64,              # Original TRS-80 screen width
                'height': 16,             # Original TRS-80 screen height
                'uppercase_mode': True,   # TRS-80 was often uppercase
                'cursor_char': '█',       # Block cursor
                'line_spacing': 1.2
            }
        }
