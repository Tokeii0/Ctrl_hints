"""
快捷键卡片组件 - 显示单个快捷键的卡片
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont

# 使用绝对导入避免相对导入问题
import sys
import os

# 确保项目根目录在sys.path中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.config import get_appearance


class ShortcutCardWidget(QWidget):
    """快捷键卡片组件"""
    
    def __init__(self, key_char: str, action_name: str, parent=None):
        """
        初始化快捷键卡片
        
        Args:
            key_char: 按键字符
            action_name: 动作名称
            parent: 父组件
        """
        super().__init__(parent)
        self.setObjectName("ShortcutCard")  # 用于QSS选择器
        
        # 获取外观配置
        self.appearance = get_appearance()
        card_size = self.appearance.get("card_size", 90)
        
        self.setMinimumSize(card_size, card_size)
        self.setMaximumSize(card_size, card_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # 启用样式背景
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._setup_layout(key_char, action_name)
        self._setup_shadow_effect()
        self._apply_appearance_style()

    def _setup_layout(self, key_char: str, action_name: str):
        """设置布局和子组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        # 按键标签
        self.key_label = QLabel(key_char)
        self.key_label.setObjectName("keyLabel")
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_key = QFont()
        font_key.setPointSize(self.appearance.get("key_font_size", 24))
        font_key.setBold(True)
        self.key_label.setFont(font_key)

        # 动作标签
        self.action_label = QLabel(action_name)
        self.action_label.setObjectName("actionLabel")
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_action = QFont()
        font_action.setPointSize(self.appearance.get("action_font_size", 10))
        self.action_label.setFont(font_action)
        self.action_label.setWordWrap(True)

        layout.addWidget(self.key_label, stretch=2)
        layout.addWidget(self.action_label, stretch=1)

    def _apply_appearance_style(self):
        """应用外观样式"""
        # 获取颜色配置
        key_color = self.appearance.get("key_color", "#1a1a1e")
        action_color = self.appearance.get("action_color", "#1e1e28")
        bg_start = self.appearance.get("card_bg_color_start", "#ffffff")
        bg_end = self.appearance.get("card_bg_color_end", "#f0f0fa")
        opacity = self.appearance.get("background_opacity", 50)
        
        # 计算实际的透明度值
        alpha = int(255 * opacity / 100)
        
        # 应用样式
        style = f"""
        ShortcutCardWidget#ShortcutCard {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 rgba({self._hex_to_rgb(bg_start)}, {alpha}),
                                       stop: 1 rgba({self._hex_to_rgb(bg_end)}, {alpha}));
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 80);
        }}
        
        QLabel#keyLabel {{
            color: {key_color};
            background-color: transparent;
        }}
        
        QLabel#actionLabel {{
            color: {action_color};
            background-color: transparent;
        }}
        """
        
        self.setStyleSheet(style)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """将十六进制颜色转换为RGB字符串"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"

    def _setup_shadow_effect(self):
        """设置阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)  # 增加模糊半径，更柔和
        shadow.setColor(QColor(0, 0, 0, 80))  # 降低阴影不透明度，更柔和
        shadow.setOffset(2, 4)  # 调整偏移，更自然
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        """自定义绘制以确保圆角背景被正确应用"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # 使用self.rect()减去一点边距，如果阴影在外部绘制的话
        path.addRoundedRect(self.rect(), 12, 12)  # 匹配QSS中的圆角大小
        painter.setClipPath(path)
        super().paintEvent(event)  # 确保子组件被绘制

    def update_content(self, key_char: str, action_name: str):
        """
        更新卡片内容
        
        Args:
            key_char: 新的按键字符
            action_name: 新的动作名称
        """
        self.key_label.setText(key_char)
        self.action_label.setText(action_name)

    def set_highlighted(self, highlighted: bool):
        """
        设置卡片高亮状态
        
        Args:
            highlighted: 是否高亮
        """
        if highlighted:
            self.setProperty("highlighted", True)
        else:
            self.setProperty("highlighted", False)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def update_appearance(self):
        """更新外观设置"""
        # 重新获取外观配置
        self.appearance = get_appearance()
        
        # 更新卡片尺寸
        card_size = self.appearance.get("card_size", 90)
        self.setMinimumSize(card_size, card_size)
        self.setMaximumSize(card_size, card_size)
        
        # 更新字体大小
        font_key = self.key_label.font()
        font_key.setPointSize(self.appearance.get("key_font_size", 24))
        self.key_label.setFont(font_key)
        
        font_action = self.action_label.font()
        font_action.setPointSize(self.appearance.get("action_font_size", 10))
        self.action_label.setFont(font_action)
        
        # 重新应用样式
        self._apply_appearance_style() 