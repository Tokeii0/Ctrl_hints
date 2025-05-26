import os
import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, 
                             QDialogButtonBox, QColorDialog, QLineEdit, QFormLayout,
                             QComboBox, QTabWidget, QWidget, QSpinBox, QCheckBox,
                             QGroupBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap

# 导入共享配置
from config import DEFAULT_SHORTCUT_ITEMS

class SettingsDialog(QDialog):
    def __init__(self, shortcuts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置快捷键提示")
        self.resize(500, 450)
        self.shortcuts = shortcuts.copy() if shortcuts else DEFAULT_SHORTCUT_ITEMS.copy()
        
        # 设置应用图标
        self.set_app_icon()
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建快捷键和外观两个选项卡
        self.shortcuts_tab = QWidget()
        self.appearance_tab = QWidget()
        
        # 设置选项卡
        self.setup_shortcuts_tab()
        self.setup_appearance_tab()
        
        self.tab_widget.addTab(self.shortcuts_tab, "快捷键")
        self.tab_widget.addTab(self.appearance_tab, "外观")
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        
        # 对话框按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                         QDialogButtonBox.StandardButton.Cancel)
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("保存")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        
        # 应用样式
        self.apply_style()
        
        # 连接信号
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box)
    
    def set_app_icon(self):
        """设置应用图标"""
        try:
            # 处理PyInstaller打包后的路径
            if hasattr(sys, '_MEIPASS'):
                # 在打包的exe中，资源文件在临时目录中
                icon_path = os.path.join(sys._MEIPASS, 'res', 'logo.png')
            else:
                # 在开发环境中，使用相对路径
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res', 'logo.png')
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"设置图标失败: {e}")
    
    def setup_shortcuts_tab(self):
        """设置快捷键选项卡"""
        layout = QVBoxLayout(self.shortcuts_tab)
        
        # 说明标签
        desc_label = QLabel("在此设置按住Ctrl键时显示的快捷键提示:")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 创建表格用于编辑快捷键
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["按键", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        # 加载现有快捷键
        self.load_shortcuts()
        
        # 添加按钮区域
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.delete_btn = QPushButton("删除所选")
        self.reset_btn = QPushButton("恢复默认")
        
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.delete_btn.setIcon(QIcon.fromTheme("list-remove"))
        self.reset_btn.setIcon(QIcon.fromTheme("edit-undo"))
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        
        # 连接信号
        self.add_btn.clicked.connect(self.add_shortcut)
        self.delete_btn.clicked.connect(self.delete_shortcut)
        self.reset_btn.clicked.connect(self.reset_shortcuts)
        
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
    
    def setup_appearance_tab(self):
        """设置外观选项卡"""
        layout = QVBoxLayout(self.appearance_tab)
        
        # 动画设置组
        animation_group = QGroupBox("动画效果")
        animation_layout = QFormLayout(animation_group)
        
        self.animation_speed = QComboBox()
        self.animation_speed.addItems(["快速", "中等", "慢速"])
        self.animation_speed.setCurrentIndex(1)  # 默认中等
        
        self.show_animation = QCheckBox("启用显示动画")
        self.show_animation.setChecked(True)
        
        self.hide_animation = QCheckBox("启用隐藏动画")
        self.hide_animation.setChecked(True)
        
        animation_layout.addRow("动画速度:", self.animation_speed)
        animation_layout.addRow(self.show_animation)
        animation_layout.addRow(self.hide_animation)
        
        # 卡片外观组
        card_group = QGroupBox("卡片外观")
        card_layout = QFormLayout(card_group)
        
        self.card_size = QSpinBox()
        self.card_size.setRange(60, 200)
        self.card_size.setValue(90)
        self.card_size.setSuffix(" px")
        
        self.key_font_size = QSpinBox()
        self.key_font_size.setRange(10, 48)
        self.key_font_size.setValue(24)
        self.key_font_size.setSuffix(" pt")
        
        self.action_font_size = QSpinBox()
        self.action_font_size.setRange(8, 24)
        self.action_font_size.setValue(10)
        self.action_font_size.setSuffix(" pt")
        
        self.background_opacity = QSpinBox()
        self.background_opacity.setRange(10, 100)
        self.background_opacity.setValue(50)
        self.background_opacity.setSuffix(" %")
        
        card_layout.addRow("卡片大小:", self.card_size)
        card_layout.addRow("按键字号:", self.key_font_size)
        card_layout.addRow("操作字号:", self.action_font_size)
        card_layout.addRow("背景透明度:", self.background_opacity)
        
        # 添加到主布局
        layout.addWidget(animation_group)
        layout.addWidget(card_group)
        layout.addStretch()
        
        # 提示标签
        note_label = QLabel("注意: 外观设置将在下次启动程序时生效")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note_label)
    
    def load_shortcuts(self):
        """加载现有快捷键到表格"""
        self.table.setRowCount(len(self.shortcuts))
        for i, shortcut in enumerate(self.shortcuts):
            key_item = QTableWidgetItem(shortcut["key"])
            action_item = QTableWidgetItem(shortcut["action"])
            self.table.setItem(i, 0, key_item)
            self.table.setItem(i, 1, action_item)
    
    def add_shortcut(self):
        """添加新的快捷键"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("新按键"))
        self.table.setItem(row, 1, QTableWidgetItem("新操作"))
        
        # 选中并编辑新添加的项
        self.table.selectRow(row)
        self.table.editItem(self.table.item(row, 0))
    
    def delete_shortcut(self):
        """删除所选快捷键"""
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        
        if not rows:
            QMessageBox.information(self, "提示", "请先选择要删除的项")
            return
            
        # 从后往前删除，避免索引变化
        for row in sorted(rows, reverse=True):
            self.table.removeRow(row)
    
    def reset_shortcuts(self):
        """重置为默认快捷键"""
        reply = QMessageBox.question(
            self, 
            "确认重置", 
            "确定要恢复默认快捷键设置吗？当前自定义设置将丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.shortcuts = DEFAULT_SHORTCUT_ITEMS.copy()
            self.load_shortcuts()
    
    def apply_style(self):
        """应用样式表"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #e0e0e5;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: rgba(255, 255, 255, 0.7);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #444;
                font-weight: bold;
            }
            QPushButton {
                background-color: #f0f0f5;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e8e8f0;
            }
            QPushButton:pressed {
                background-color: #d0d0d8;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                selection-background-color: #e0e8f0;
                alternate-background-color: #f8f8f8;
            }
            QHeaderView::section {
                background-color: #e8e8e8;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QSpinBox, QComboBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px 5px;
                background-color: white;
            }
            QLabel {
                color: #333;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
                padding: 6px 12px;
            }
            QDialogButtonBox QPushButton[text="保存"] {
                background-color: #4a86e8;
                color: white;
                border: none;
            }
            QDialogButtonBox QPushButton[text="保存"]:hover {
                background-color: #3a76d8;
            }
        """)
    
    def accept(self):
        """确认对话框，收集数据并保存"""
        # 收集表格中的数据
        shortcuts = []
        for i in range(self.table.rowCount()):
            key = self.table.item(i, 0).text().strip()
            action = self.table.item(i, 1).text().strip()
            
            # 确保按键和操作都不为空
            if key and action:
                shortcuts.append({"key": key, "action": action})
        
        # 更新数据并关闭对话框
        self.shortcuts = shortcuts
        super().accept()
    
    def get_shortcuts(self):
        """获取快捷键设置"""
        return self.shortcuts

if __name__ == "__main__":
    """测试设置对话框"""
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    dialog = SettingsDialog(DEFAULT_SHORTCUT_ITEMS.copy())
    dialog.exec_()
