"""
工具模块 - 包含配置管理和常量定义
"""

from .config import *
from .constants import *

__all__ = ['load_config', 'save_config', 'DEFAULT_SHORTCUT_ITEMS', 'SHORTCUT_ITEMS', 
           'ALT_SHORTCUT_ITEMS', 'CTRL_ALT_SHORTCUT_ITEMS', 'WIN_SHORTCUT_ITEMS',
           'APPEARANCE', 'EFFECTS'] 