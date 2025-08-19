#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skins Package for HAL 9000 v5.0
Provides theming and skin system for the interface
"""

from .skin_manager import SkinManager
from .base_skin import BaseSkin
from .star_trek_skin import StarTrekSkin
from .retro_80s_skin import Retro80sSkin

__all__ = ['SkinManager', 'BaseSkin', 'StarTrekSkin', 'Retro80sSkin']
