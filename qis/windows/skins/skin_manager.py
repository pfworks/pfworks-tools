#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skin Manager for HAL 9000 v5.0
Manages loading and switching between different interface skins
"""

import os
import sys

class SkinManager:
    """Manages interface skins and themes"""
    
    def __init__(self):
        self.skins = {}
        self.current_skin = None
        self.skin_directory = os.path.join(os.path.dirname(__file__))
        self.load_available_skins()
        
    def load_available_skins(self):
        """Load all available skins from the skins directory"""
        try:
            # Load base skin
            from .base_skin import BaseSkin
            self.skins['hal9000'] = BaseSkin()
            
            # Load Star Trek skin
            from .star_trek_skin import StarTrekSkin
            self.skins['star_trek'] = StarTrekSkin()
            
            # Load Retro 80s skin
            from .retro_80s_skin import Retro80sSkin
            self.skins['retro_80s'] = Retro80sSkin()
            
            # Set default skin
            if not self.current_skin:
                self.current_skin = 'hal9000'
                
        except Exception as e:
            print("Error loading skins: " + str(e))
            # Fallback to base skin
            try:
                from .base_skin import BaseSkin
                self.skins['hal9000'] = BaseSkin()
                self.current_skin = 'hal9000'
            except:
                # Ultimate fallback
                self.skins = {}
                self.current_skin = None
    
    def get_available_skins(self):
        """Get list of available skin names and descriptions"""
        skin_info = {}
        for skin_id, skin in self.skins.items():
            skin_info[skin_id] = {
                'name': skin.name,
                'description': skin.description,
                'version': skin.version
            }
        return skin_info
    
    def set_skin(self, skin_id):
        """Set the active skin"""
        if skin_id in self.skins:
            self.current_skin = skin_id
            return True
        return False
    
    def get_current_skin(self):
        """Get the current active skin object"""
        if self.current_skin and self.current_skin in self.skins:
            return self.skins[self.current_skin]
        return self.skins.get('hal9000')  # Fallback to HAL 9000
    
    def get_skin_config(self, skin_id=None):
        """Get complete configuration for specified skin or current skin"""
        if skin_id:
            skin = self.skins.get(skin_id)
        else:
            skin = self.get_current_skin()
        
        if skin:
            return skin.get_config()
        return {}
    
    def get_identity(self):
        """Get current skin's identity configuration"""
        skin = self.get_current_skin()
        return skin.get_identity() if skin else {}
    
    def get_colors(self):
        """Get current skin's color configuration"""
        skin = self.get_current_skin()
        return skin.get_colors() if skin else {}
    
    def get_fonts(self):
        """Get current skin's font configuration"""
        skin = self.get_current_skin()
        return skin.get_fonts() if skin else {}
    
    def get_messages(self):
        """Get current skin's message configuration"""
        skin = self.get_current_skin()
        return skin.get_messages() if skin else {}
    
    def get_interface(self):
        """Get current skin's interface configuration"""
        skin = self.get_current_skin()
        return skin.get_interface() if skin else {}
    
    def get_assets(self):
        """Get current skin's asset configuration"""
        skin = self.get_current_skin()
        return skin.get_assets() if skin else {}
    
    def format_message(self, message_key, **kwargs):
        """Format a message using current skin"""
        skin = self.get_current_skin()
        if skin:
            return skin.format_message(message_key, **kwargs)
        return message_key
    
    def save_skin_preference(self, skin_id):
        """Save skin preference to file"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), '..', 'skin_config.txt')
            with open(config_file, 'w') as f:
                f.write(skin_id)
        except Exception as e:
            print("Could not save skin preference: " + str(e))
    
    def load_skin_preference(self):
        """Load saved skin preference"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), '..', 'skin_config.txt')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    skin_id = f.read().strip()
                    if skin_id in self.skins:
                        self.current_skin = skin_id
                        return True
        except Exception as e:
            print("Could not load skin preference: " + str(e))
        return False
