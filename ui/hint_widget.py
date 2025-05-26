"""
提示窗口组件 - 显示快捷键提示的主窗口
"""

import sys
import os
from typing import List, Dict
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QGuiApplication

# 使用绝对导入避免相对导入问题
import sys
import os

# 确保项目根目录在sys.path中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.card_widget import ShortcutCardWidget


class HintWidget(QWidget):
    """快捷键提示窗口"""
    
    def __init__(self, shortcut_items: List[Dict] = None):
        """
        初始化提示窗口
        
        Args:
            shortcut_items: 快捷键列表，格式为 [{"key": "C", "action": "复制"}, ...]
        """
        super().__init__()
        self.shortcut_items = shortcut_items or []
        
        self._setup_window_properties()
        self._setup_layout()
        self._setup_animations()
        self._load_stylesheet()
        self._create_cards()

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # 无窗口边框
            Qt.WindowType.WindowStaysOnTopHint |      # 窗口总在最前
            Qt.WindowType.Tool |                      # 工具窗口类型 (不在任务栏显示图标)
            Qt.WindowType.NoDropShadowWindowHint      # 禁用系统默认阴影，我们将自定义阴影
        )
        # 设置窗口属性，使其不获取焦点，并且在显示时不激活窗口
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # 启用背景透明，HintWidget本身是透明容器
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")  # 确保HintWidget背景透明
        
        # 初始化不透明度为0，用于动画
        self.setWindowOpacity(0.0)

    def _setup_layout(self):
        """设置布局"""
        # 主容器使用水平布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)  # 容器本身的边距
        self.layout.setSpacing(10)  # 卡片之间的间距

    def _setup_animations(self):
        """设置动画"""
        # 淡入动画
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(250)  # 增加持续时间
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(180)  # 增加持续时间
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # 滑入动画
        self.slide_in_animation = QPropertyAnimation(self, b"pos")
        self.slide_in_animation.setDuration(300)  # 增加持续时间，更流畅
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.OutBack)  # 使用弹性效果

        # 滑出动画
        self.slide_out_animation = QPropertyAnimation(self, b"pos")
        self.slide_out_animation.setDuration(200)  # 增加持续时间
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InQuad)

    def _load_stylesheet(self):
        """加载样式表"""
        try:
            # 处理PyInstaller打包后的路径
            if hasattr(sys, '_MEIPASS'):
                # 在打包的exe中，资源文件在临时目录中
                style_path = os.path.join(sys._MEIPASS, 'resources', 'styles.qss')
            else:
                # 在开发环境中，使用相对路径
                style_path = os.path.join('resources', 'styles.qss')
            
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    style = f.read()
                    self.setStyleSheet(style)
            else:
                print(f"警告: 样式文件 '{style_path}' 未找到，使用默认样式。")
                self._apply_default_style()
        except Exception as e:
            print(f"加载样式文件时出错: {e}")
            self._apply_default_style()

    def _apply_default_style(self):
        """应用默认样式，当样式文件不可用时使用"""
        default_style = """
        ShortcutCardWidget#ShortcutCard {
            background-color: rgba(255, 255, 255, 120);
            border-radius: 12px;
            min-width: 90px;
            max-width: 90px;
            min-height: 90px;
            max-height: 90px;
            padding: 8px;
            border: 1px solid rgba(255, 255, 255, 80);
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 rgba(255, 255, 255, 140),
                                       stop: 0.5 rgba(250, 250, 255, 100),
                                       stop: 1 rgba(240, 240, 250, 120));
        }
        
        ShortcutCardWidget#ShortcutCard QLabel#keyLabel {
            color: rgba(20, 20, 30, 255);
            font-size: 24px;
            font-weight: bold;
            background-color: transparent;
        }
        
        ShortcutCardWidget#ShortcutCard QLabel#actionLabel {
            color: rgba(30, 30, 40, 240);
            font-size: 10px;
            background-color: transparent;
        }
        """
        self.setStyleSheet(default_style)

    def _create_cards(self):
        """创建快捷键卡片"""
        self._clear_cards()
        
        # 存储卡片引用，用于动画触发
        self.cards = []
        
        for item_data in self.shortcut_items:
            card = ShortcutCardWidget(item_data["key"], item_data["action"])
            self.layout.addWidget(card)
            self.cards.append(card)
        
        self.adjustSize()  # 根据内容调整窗口大小

    def _clear_cards(self):
        """清除所有卡片"""
        # 清空卡片引用
        self.cards = []
        
        for i in reversed(range(self.layout.count())): 
            item = self.layout.itemAt(i)
            if item:
                widget_item = item.widget()
                if widget_item:  # 确保控件存在才删除
                    widget_item.setParent(None)
                    widget_item.deleteLater()

    def update_shortcuts(self, shortcut_items: List[Dict]):
        """
        更新快捷键列表
        
        Args:
            shortcut_items: 新的快捷键列表
        """
        self.shortcut_items = shortcut_items
        self._create_cards()

    def show_above_taskbar(self):
        """在任务栏上方显示窗口"""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            print("错误: 未找到主屏幕。")
            self.show()  # Fallback
            return

        available_geom = screen.availableGeometry()  # 可用桌面区域 (通常不包括任务栏)
        full_geom = screen.geometry()  # 整个屏幕区域
        
        # 水平居中
        win_x = available_geom.left() + (available_geom.width() - self.width()) / 2
        
        # 默认假设任务栏在底部
        win_y = available_geom.bottom() - self.height() - 10  # 距离任务栏10像素

        # 检查任务栏是否在顶部
        # 如果可用区域的顶部y坐标大于整个屏幕的顶部y坐标 (通常为0)，说明顶部有东西 (可能是任务栏)
        if available_geom.y() > full_geom.y() and available_geom.height() < full_geom.height():
            win_y = available_geom.top() + 10  # 距离顶部任务栏10像素
        
        # 对于左右任务栏的情况，此基本定位逻辑可能不完美，但会确保在可用区域内

        final_pos = QPoint(int(win_x), int(win_y))
        start_pos_slide = QPoint(int(win_x), int(win_y) + 30)  # 从下方30px处滑入，增加距离

        self.move(start_pos_slide)  # 初始位置在目标位置下方
        self.setWindowOpacity(0.0)  # 确保开始时是透明的
        self.show()

        self.fade_in_animation.start()  # 开始淡入动画

        self.slide_in_animation.setStartValue(start_pos_slide)
        self.slide_in_animation.setEndValue(final_pos)
        self.slide_in_animation.start()  # 开始滑入动画

    def hide_with_animation(self):
        """带动画地隐藏窗口"""
        if self.isVisible() and self.fade_out_animation.state() != QPropertyAnimation.State.Running:
            current_pos = self.pos()
            end_pos_slide = QPoint(current_pos.x(), current_pos.y() + 30)  # 向下滑出30px

            # 断开所有可能的连接
            # 先检查是否有连接，避免无效断开导致的警告
            connections = self.fade_out_animation.receivers("finished()")
            if connections > 0:
                try:
                    # 既然有连接，就断开这个特定的连接，而不是空白的断开
                    self.fade_out_animation.finished.disconnect(self.hide)
                except Exception:
                    pass  # 忽略断开连接错误

            # 重新连接隐藏信号
            self.fade_out_animation.finished.connect(self.hide)
            
            # 启动渐变和滑动动画
            self.fade_out_animation.start()
            self.slide_out_animation.setStartValue(current_pos)
            self.slide_out_animation.setEndValue(end_pos_slide)
            self.slide_out_animation.start()

    def get_card_count(self) -> int:
        """
        获取卡片数量
        
        Returns:
            int: 卡片数量
        """
        return len(self.shortcut_items)
    
    def trigger_key_animation(self, key_char: str):
        """
        触发指定按键的动画效果
        
        Args:
            key_char: 按键字符
        """
        if hasattr(self, 'cards'):
            for card in self.cards:
                if card.matches_key(key_char):
                    card.trigger_animation()
                    break
    
    def update_appearance(self):
        """更新所有卡片的外观"""
        try:
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'update_appearance'):
                        widget.update_appearance()
            
            # 重新调整窗口大小
            self.adjustSize()
            
        except Exception as e:
            print(f"更新提示窗口外观时出错: {e}") 