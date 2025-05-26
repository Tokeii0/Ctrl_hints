"""
配置管理模块 - 负责加载和保存应用程序配置
"""

import json
import os
from typing import Dict, List, Any
from .constants import (
    DEFAULT_SHORTCUT_ITEMS, DEFAULT_ALT_SHORTCUT_ITEMS, 
    DEFAULT_CTRL_ALT_SHORTCUT_ITEMS, DEFAULT_WIN_SHORTCUT_ITEMS,
    DEFAULT_APPEARANCE, DEFAULT_EFFECTS, CONFIG_FILE
)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.shortcut_items = []
        self.alt_shortcut_items = []
        self.ctrl_alt_shortcut_items = []
        self.win_shortcut_items = []
        self.appearance = {}
        self.effects = {}
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载快捷键配置
                self.shortcut_items = config.get('shortcuts', DEFAULT_SHORTCUT_ITEMS.copy())
                self.alt_shortcut_items = config.get('alt_shortcuts', DEFAULT_ALT_SHORTCUT_ITEMS.copy())
                self.ctrl_alt_shortcut_items = config.get('ctrl_alt_shortcuts', DEFAULT_CTRL_ALT_SHORTCUT_ITEMS.copy())
                self.win_shortcut_items = config.get('win_shortcuts', DEFAULT_WIN_SHORTCUT_ITEMS.copy())
                
                # 加载外观和效果配置
                self.appearance = config.get('appearance', DEFAULT_APPEARANCE.copy())
                self.effects = config.get('effects', DEFAULT_EFFECTS.copy())
                
                print("配置文件加载成功")
                return True
            else:
                # 配置文件不存在，使用默认配置
                self.reset_to_defaults()
                print("配置文件不存在，使用默认配置")
                return True
                
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            import traceback
            traceback.print_exc()
            # 出错时使用默认配置
            self.reset_to_defaults()
            return False
    
    def save_config(self, shortcuts: List[Dict] = None, 
                    alt_shortcuts: List[Dict] = None,
                    ctrl_alt_shortcuts: List[Dict] = None,
                    win_shortcuts: List[Dict] = None,
                    appearance: Dict = None,
                    effects: Dict = None) -> bool:
        """
        保存配置到文件
        
        Args:
            shortcuts: Ctrl快捷键列表
            alt_shortcuts: Alt快捷键列表  
            ctrl_alt_shortcuts: Ctrl+Alt快捷键列表
            win_shortcuts: Win快捷键列表
            appearance: 外观配置
            effects: 效果配置
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # 更新配置
            if shortcuts is not None:
                self.shortcut_items = shortcuts
            if alt_shortcuts is not None:
                self.alt_shortcut_items = alt_shortcuts
            if ctrl_alt_shortcuts is not None:
                self.ctrl_alt_shortcut_items = ctrl_alt_shortcuts
            if win_shortcuts is not None:
                self.win_shortcut_items = win_shortcuts
            if appearance is not None:
                self.appearance = appearance
            if effects is not None:
                self.effects = effects
                
            # 构建配置字典
            config = {
                'shortcuts': self.shortcut_items,
                'alt_shortcuts': self.alt_shortcut_items,
                'ctrl_alt_shortcuts': self.ctrl_alt_shortcut_items,
                'win_shortcuts': self.win_shortcut_items,
                'appearance': self.appearance,
                'effects': self.effects
            }
            
            # 保存到文件
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            print("配置文件保存成功")
            return True
            
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置所有配置为默认值"""
        self.shortcut_items = DEFAULT_SHORTCUT_ITEMS.copy()
        self.alt_shortcut_items = DEFAULT_ALT_SHORTCUT_ITEMS.copy()
        self.ctrl_alt_shortcut_items = DEFAULT_CTRL_ALT_SHORTCUT_ITEMS.copy()
        self.win_shortcut_items = DEFAULT_WIN_SHORTCUT_ITEMS.copy()
        self.appearance = DEFAULT_APPEARANCE.copy()
        self.effects = DEFAULT_EFFECTS.copy()
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            Dict: 包含所有配置的字典
        """
        return {
            'shortcuts': self.shortcut_items,
            'alt_shortcuts': self.alt_shortcut_items,
            'ctrl_alt_shortcuts': self.ctrl_alt_shortcut_items,
            'win_shortcuts': self.win_shortcut_items,
            'appearance': self.appearance,
            'effects': self.effects
        }

# 创建全局配置管理器实例
_config_manager = ConfigManager()

# 为了向后兼容，创建全局变量
SHORTCUT_ITEMS = []
ALT_SHORTCUT_ITEMS = []
CTRL_ALT_SHORTCUT_ITEMS = []
WIN_SHORTCUT_ITEMS = []
APPEARANCE = {}
EFFECTS = {}

def _update_global_vars():
    """更新全局变量"""
    global SHORTCUT_ITEMS, ALT_SHORTCUT_ITEMS, CTRL_ALT_SHORTCUT_ITEMS
    global WIN_SHORTCUT_ITEMS, APPEARANCE, EFFECTS
    
    SHORTCUT_ITEMS[:] = _config_manager.shortcut_items
    ALT_SHORTCUT_ITEMS[:] = _config_manager.alt_shortcut_items
    CTRL_ALT_SHORTCUT_ITEMS[:] = _config_manager.ctrl_alt_shortcut_items
    WIN_SHORTCUT_ITEMS[:] = _config_manager.win_shortcut_items
    APPEARANCE.clear()
    APPEARANCE.update(_config_manager.appearance)
    EFFECTS.clear()
    EFFECTS.update(_config_manager.effects)

# 为了向后兼容，提供函数接口
def load_config() -> bool:
    """加载配置文件"""
    result = _config_manager.load_config()
    if result:
        _update_global_vars()
    return result

def save_config(shortcuts: List[Dict] = None, 
                alt_shortcuts: List[Dict] = None,
                ctrl_alt_shortcuts: List[Dict] = None,
                win_shortcuts: List[Dict] = None,
                appearance: Dict = None,
                effects: Dict = None) -> bool:
    """保存配置到文件"""
    result = _config_manager.save_config(
        shortcuts, alt_shortcuts, ctrl_alt_shortcuts, 
        win_shortcuts, appearance, effects
    )
    if result:
        _update_global_vars()
    return result

def reset_to_defaults():
    """重置所有配置为默认值"""
    _config_manager.reset_to_defaults()
    _update_global_vars()

def get_config() -> Dict[str, Any]:
    """获取当前配置"""
    return _config_manager.get_config()



# 为了向后兼容，也提供直接访问方式
def get_shortcut_items():
    return _config_manager.shortcut_items

def get_alt_shortcut_items():
    return _config_manager.alt_shortcut_items

def get_ctrl_alt_shortcut_items():
    return _config_manager.ctrl_alt_shortcut_items

def get_win_shortcut_items():
    return _config_manager.win_shortcut_items

def get_appearance():
    return _config_manager.appearance

def get_effects():
    return _config_manager.effects

def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置的有效性
    
    Args:
        config: 要验证的配置字典
        
    Returns:
        bool: 配置有效返回True，无效返回False
    """
    try:
        # 检查必需的键
        required_keys = ['shortcuts', 'alt_shortcuts', 'ctrl_alt_shortcuts', 
                        'win_shortcuts', 'appearance', 'effects']
        
        for key in required_keys:
            if key not in config:
                return False
                
        # 检查快捷键列表格式
        for shortcut_list in [config['shortcuts'], config['alt_shortcuts'], 
                             config['ctrl_alt_shortcuts'], config['win_shortcuts']]:
            if not isinstance(shortcut_list, list):
                return False
            for item in shortcut_list:
                if not isinstance(item, dict) or 'key' not in item or 'action' not in item:
                    return False
                    
        # 检查外观和效果配置
        if not isinstance(config['appearance'], dict) or not isinstance(config['effects'], dict):
            return False
            
        return True
        
    except Exception:
        return False 