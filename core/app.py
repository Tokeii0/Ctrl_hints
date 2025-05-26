"""
主应用程序类 - 整合所有模块，管理应用程序生命周期
"""

import sys
from typing import Dict
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import Qt, Slot

from .keyboard_listener import KeyboardListener
from .tray_manager import TrayManager

# 使用绝对导入避免相对导入问题
import sys
import os

# 确保项目根目录在sys.path中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.hint_widget import HintWidget
from utils.config import (
    load_config, save_config, SHORTCUT_ITEMS, ALT_SHORTCUT_ITEMS,
    CTRL_ALT_SHORTCUT_ITEMS, WIN_SHORTCUT_ITEMS, APPEARANCE, EFFECTS
)


class CtrlHintApp:
    """主应用程序类"""
    
    def __init__(self):
        # 确保QApplication实例存在
        self.app = QApplication.instance() 
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # 设置应用程序退出策略
        self.app.setQuitOnLastWindowClosed(False)

        # 加载配置
        load_config()
        
        # 初始化组件
        self._init_components()
        
        # 连接信号
        self._connect_signals()
        
        # 当前可见窗口状态
        self.current_visible_window = None

    def _init_components(self):
        """初始化所有组件"""
        # 创建键盘监听器
        self.keyboard_listener = KeyboardListener()
        
        # 创建系统托盘管理器
        self.tray_manager = TrayManager(self.app)
        
        # 创建不同组合键的提示窗口
        self.hint_windows = {
            "ctrl": HintWidget(SHORTCUT_ITEMS),
            "alt": HintWidget(ALT_SHORTCUT_ITEMS),
            "ctrl_alt": HintWidget(CTRL_ALT_SHORTCUT_ITEMS),
            "win": HintWidget(WIN_SHORTCUT_ITEMS)
        }

    def _connect_signals(self):
        """连接信号和槽"""
        # 连接键盘监听器信号
        self.keyboard_listener.key_pressed.connect(self._on_key_pressed)
        self.keyboard_listener.key_released.connect(self._on_key_released)
        
        # 连接托盘管理器信号
        self.tray_manager.settings_requested.connect(self._show_settings)
        self.tray_manager.quit_requested.connect(self._quit_app)

    @Slot(str)
    def _on_key_pressed(self, key_type: str):
        """
        处理按键按下事件
        
        Args:
            key_type: 按键类型 ("ctrl", "alt", "ctrl_alt", "win")
        """
        try:
            # 隐藏所有窗口
            self._hide_all_windows()
            
            # 显示对应的提示窗口
            if key_type in self.hint_windows:
                self.current_visible_window = key_type
                self.hint_windows[key_type].show_above_taskbar()
                
        except Exception as e:
            print(f"处理按键按下事件时出错: {e}")

    @Slot(str)
    def _on_key_released(self, key_type: str):
        """
        处理按键释放事件
        
        Args:
            key_type: 按键类型 ("ctrl", "alt", "ctrl_alt", "win")
        """
        try:
            # 如果当前显示的窗口与释放的按键相关，就隐藏
            if self.current_visible_window and self._is_related_key(self.current_visible_window, key_type):
                self._hide_all_windows()
                
        except Exception as e:
            print(f"处理按键释放事件时出错: {e}")

    def _is_related_key(self, window_type: str, key_type: str) -> bool:
        """
        检查窗口类型和按键类型是否相关
        
        Args:
            window_type: 窗口类型
            key_type: 按键类型
            
        Returns:
            bool: 相关返回True，否则返回False
        """
        # 定义相关性映射
        relations = {
            "ctrl": ["ctrl", "ctrl_alt"],
            "alt": ["alt", "ctrl_alt"],
            "ctrl_alt": ["ctrl", "alt", "ctrl_alt"],
            "win": ["win"]
        }
        
        return window_type in relations.get(key_type, [])

    def _hide_all_windows(self):
        """隐藏所有提示窗口"""
        try:
            for window in self.hint_windows.values():
                if window.isVisible():
                    window.hide_with_animation()
            
            self.current_visible_window = None
            
        except Exception as e:
            print(f"隐藏所有窗口时出错: {e}")

    def _show_settings(self):
        """显示设置对话框"""
        try:
            # 动态导入设置对话框，避免循环导入
            from ui.settings_dialog import SettingsDialog
            
            # 创建设置对话框，明确指定父窗口为None
            dialog = SettingsDialog(parent=None)
            
            # 如果用户点击保存
            if dialog.exec():
                # 获取所有新设置
                new_config = dialog.get_all_settings()
                
                # 保存配置
                if save_config(**new_config):
                    # 更新提示窗口
                    self._update_hint_windows()
                    
                    # 使用托盘消息而不是弹窗，避免事件循环问题
                    self.tray_manager.show_message(
                        "设置已保存", 
                        "所有设置已成功保存并应用！",
                        timeout=2000
                    )
                    print("设置已成功保存并应用")
                else:
                    self.tray_manager.show_message(
                        "保存失败", 
                        "保存设置时出错，请稍后再试。",
                        QSystemTrayIcon.MessageIcon.Warning,
                        timeout=3000
                    )
                    print("保存设置时出错")
            
            # 对话框会在exec()结束后自动清理，不需要手动删除
                    
        except Exception as e:
            print(f"显示设置对话框时出错: {e}")
            import traceback
            traceback.print_exc()
            self.tray_manager.show_message(
                "错误", 
                f"打开设置时出错: {e}",
                QSystemTrayIcon.MessageIcon.Critical,
                timeout=3000
            )

    def _update_hint_windows(self):
        """更新所有提示窗口"""
        try:
            # 更新快捷键内容
            self.hint_windows["ctrl"].update_shortcuts(SHORTCUT_ITEMS)
            self.hint_windows["alt"].update_shortcuts(ALT_SHORTCUT_ITEMS)
            self.hint_windows["ctrl_alt"].update_shortcuts(CTRL_ALT_SHORTCUT_ITEMS)
            self.hint_windows["win"].update_shortcuts(WIN_SHORTCUT_ITEMS)
            
            # 更新外观
            self.hint_windows["ctrl"].update_appearance()
            self.hint_windows["alt"].update_appearance()
            self.hint_windows["ctrl_alt"].update_appearance()
            self.hint_windows["win"].update_appearance()
            
        except Exception as e:
            print(f"更新提示窗口时出错: {e}")
            import traceback
            traceback.print_exc()

    def _quit_app(self):
        """退出应用程序"""
        try:
            print("正在退出程序...")
            
            # 停止键盘监听器
            self.keyboard_listener.stop()
            
            # 隐藏所有窗口
            self._hide_all_windows()
            
            # 隐藏托盘图标
            self.tray_manager.hide()
            
            # 退出应用程序
            self.app.quit()
            
        except Exception as e:
            print(f"退出程序时出错: {e}")
        finally:
            sys.exit(0)

    def run(self):
        """运行应用程序"""
        print("Ctrl快捷键提示工具已启动。按住Ctrl键查看提示。")
        print("程序将在系统托盘中运行，右键点击托盘图标可以访问设置或退出程序。")
        
        # 检查系统托盘支持
        if not self.tray_manager.is_system_tray_available():
            QMessageBox.critical(
                None,
                "系统托盘不可用",
                "您的系统不支持系统托盘功能，程序无法正常运行。"
            )
            return 1
        
        # 启动键盘监听器
        self.keyboard_listener.start()
        
        # 显示启动消息
        self.tray_manager.show_message(
            "Ctrl快捷键提示工具",
            "程序已启动并在后台运行。\n按住Ctrl键可以显示快捷键提示。\n右键点击托盘图标可以访问设置或退出程序。",
            timeout=3000
        )
        
        # 运行Qt应用程序主循环
        try:
            exit_code = self.app.exec()
        except Exception as e:
            print(f"程序运行时出错: {e}")
            import traceback
            traceback.print_exc()
            exit_code = 1
        finally:
            # 清理资源
            self._cleanup()
        
        print("程序已退出。")
        return exit_code

    def _cleanup(self):
        """清理资源"""
        try:
            # 停止键盘监听器
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()
                
            # 隐藏托盘图标
            if hasattr(self, 'tray_manager'):
                self.tray_manager.hide()
                
        except Exception as e:
            print(f"清理资源时出错: {e}")

    def get_app_info(self) -> Dict[str, str]:
        """
        获取应用程序信息
        
        Returns:
            Dict: 应用程序信息字典
        """
        return {
            "name": "Ctrl快捷键提示工具",
            "version": "1.0.0",
            "description": "一个简单实用的快捷键提示工具",
            "author": "Assistant",
            "license": "MIT"
        } 