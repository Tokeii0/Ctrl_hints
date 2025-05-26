"""
颜色选择按钮组件
"""

from PySide6.QtWidgets import QPushButton, QColorDialog
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor


class ColorButton(QPushButton):
    """颜色选择按钮"""
    
    colorChanged = Signal(str)  # 颜色改变信号
    
    def __init__(self, initial_color: str = "#FFFFFF", parent=None):
        super().__init__(parent)
        self._color = initial_color
        self.setFixedSize(60, 30)
        self.clicked.connect(self._choose_color)
        self._update_style()
    
    def _update_style(self):
        """更新按钮样式"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #ccc;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
            QPushButton:pressed {{
                border: 2px solid #666;
            }}
        """)
    
    def _choose_color(self):
        """打开颜色选择对话框"""
        color = QColorDialog.getColor(QColor(self._color), self, "选择颜色")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.colorChanged.emit(self._color)
    
    def get_color(self) -> str:
        """获取当前颜色"""
        return self._color
    
    def set_color(self, color: str):
        """设置颜色"""
        self._color = color
        self._update_style() 