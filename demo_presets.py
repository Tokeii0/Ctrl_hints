#!/usr/bin/env python3
"""演示样式预设功能"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from ui.hint_widget import HintWidget
from utils.config import _config_manager
from utils.constants import STYLE_PRESETS

def demo_presets():
    """演示所有样式预设"""
    app = QApplication(sys.argv)
    
    # 演示用的快捷键
    demo_shortcuts = [
        {"key": "C", "action": "复制"},
        {"key": "V", "action": "粘贴"},
        {"key": "X", "action": "剪切"},
        {"key": "Z", "action": "撤销"}
    ]
    
    print("样式预设演示开始...")
    print("每个预设将显示3秒钟")
    print("-" * 40)
    
    for preset_name, preset_config in STYLE_PRESETS.items():
        print(f"正在展示: {preset_name}")
        
        # 应用预设配置
        _config_manager.appearance.update(preset_config)
        
        # 创建并显示窗口
        window = HintWidget(demo_shortcuts)
        window.setWindowTitle(f"样式预设: {preset_name}")
        window.show_above_taskbar()
        
        # 显示3秒
        app.processEvents()
        time.sleep(3)
        
        # 隐藏窗口
        window.hide()
        window.deleteLater()
        
        app.processEvents()
        time.sleep(0.5)  # 短暂间隔
    
    print("-" * 40)
    print("演示结束！")

if __name__ == "__main__":
    demo_presets() 