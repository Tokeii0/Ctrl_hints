"""
系统托盘管理器 - 负责管理系统托盘图标和菜单
"""

import sys
import os
from typing import Callable
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal


class TrayManager(QObject):
    """系统托盘管理器"""
    
    # 定义信号
    settings_requested = Signal()  # 请求打开设置
    quit_requested = Signal()      # 请求退出程序
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.tray_icon = None
        self._setup_tray_icon()

    def _setup_tray_icon(self):
        """设置系统托盘图标"""
        # 创建托盘图标
        icon = self._load_icon()
        self.tray_icon = QSystemTrayIcon(icon, self.app)
        self.tray_icon.setToolTip("Ctrl快捷键提示工具")
        
        # 创建托盘菜单
        self._create_tray_menu()
        
        # 显示托盘图标
        self.tray_icon.show()

    def _load_icon(self) -> QIcon:
        """加载托盘图标"""
        # 处理PyInstaller打包后的路径
        if hasattr(sys, '_MEIPASS'):
            # 在打包的exe中，资源文件在临时目录中
            icon_path = os.path.join(sys._MEIPASS, 'resources', 'logo.png')
        else:
            # 在开发环境中，使用相对路径
            icon_path = os.path.join('resources', 'logo.png')
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"警告: 图标文件 '{icon_path}' 未找到。")
            return QIcon()  # 返回空图标

    def _create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()
        
        # 添加设置菜单项
        settings_action = QAction("设置", self.app)
        settings_action.triggered.connect(self._on_settings_clicked)
        tray_menu.addAction(settings_action)
        
        # 添加分隔符
        tray_menu.addSeparator()
        
        # 添加关于菜单项
        about_action = QAction("关于", self.app)
        about_action.triggered.connect(self._on_about_clicked)
        tray_menu.addAction(about_action)
        
        # 添加分隔符
        tray_menu.addSeparator()
        
        # 添加退出菜单项
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self._on_quit_clicked)
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)

    def _on_settings_clicked(self):
        """设置菜单项被点击"""
        self.settings_requested.emit()

    def _on_about_clicked(self):
        """关于菜单项被点击"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            None,
            "关于 Ctrl快捷键提示工具",
            """
            <h3>Ctrl快捷键提示工具</h3>
            <p>版本: 1.0.0</p>
            <p>一个简单实用的快捷键提示工具，帮助您快速查看和学习常用快捷键。</p>
            <p>按住 Ctrl、Alt、Win 键可以显示对应的快捷键提示。</p>
            <p><b>功能特点:</b></p>
            <ul>
            <li>支持 Ctrl、Alt、Win 键和组合键</li>
            <li>美观的卡片式界面</li>
            <li>流畅的动画效果</li>
            <li>可自定义快捷键配置</li>
            </ul>
            """
        )

    def _on_quit_clicked(self):
        """退出菜单项被点击"""
        self.quit_requested.emit()

    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information, timeout: int = 3000):
        """
        显示托盘消息
        
        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标
            timeout: 显示时间（毫秒）
        """
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, timeout)

    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()

    def is_visible(self) -> bool:
        """
        检查托盘图标是否可见
        
        Returns:
            bool: 可见返回True，否则返回False
        """
        return self.tray_icon.isVisible() if self.tray_icon else False

    def is_system_tray_available(self) -> bool:
        """
        检查系统是否支持托盘图标
        
        Returns:
            bool: 支持返回True，否则返回False
        """
        return QSystemTrayIcon.isSystemTrayAvailable()

    def set_tooltip(self, tooltip: str):
        """
        设置托盘图标的工具提示
        
        Args:
            tooltip: 工具提示文本
        """
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)

    def update_icon(self, icon_path: str):
        """
        更新托盘图标
        
        Args:
            icon_path: 新图标的路径
        """
        if self.tray_icon and os.path.exists(icon_path):
            new_icon = QIcon(icon_path)
            self.tray_icon.setIcon(new_icon) 