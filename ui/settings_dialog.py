"""
设置对话框 - 用于配置快捷键和应用程序设置
"""

from typing import Dict, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QHeaderView, QLabel, QSpacerItem, QSizePolicy, QFormLayout,
    QSpinBox, QSlider, QComboBox, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt

# 使用绝对导入避免相对导入问题
import sys
import os

# 确保项目根目录在sys.path中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.config import (
    SHORTCUT_ITEMS, ALT_SHORTCUT_ITEMS, CTRL_ALT_SHORTCUT_ITEMS,
    WIN_SHORTCUT_ITEMS, APPEARANCE, EFFECTS
)
from utils.constants import STYLE_PRESETS
from .color_button import ColorButton


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快捷键设置")
        self.setModal(True)
        self.resize(600, 500)
        
        # 存储当前设置
        self.current_shortcuts = {
            "ctrl": SHORTCUT_ITEMS.copy(),
            "alt": ALT_SHORTCUT_ITEMS.copy(),
            "ctrl_alt": CTRL_ALT_SHORTCUT_ITEMS.copy(),
            "win": WIN_SHORTCUT_ITEMS.copy()
        }
        self.current_appearance = APPEARANCE.copy()
        self.current_effects = EFFECTS.copy()
        
        self._setup_ui()

    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加快捷键设置标签页
        self._create_shortcut_tabs()
        
        # 添加外观设置标签页（占位）
        self._create_appearance_tab()
        
        layout.addWidget(self.tab_widget)
        
        # 添加按钮
        self._create_buttons(layout)

    def _create_shortcut_tabs(self):
        """创建快捷键设置标签页"""
        shortcut_tabs = [
            ("Ctrl快捷键", "ctrl", self.current_shortcuts["ctrl"]),
            ("Alt快捷键", "alt", self.current_shortcuts["alt"]),
            ("Ctrl+Alt快捷键", "ctrl_alt", self.current_shortcuts["ctrl_alt"]),
            ("Win快捷键", "win", self.current_shortcuts["win"])
        ]
        
        self.tables = {}
        
        for tab_name, key, shortcuts in shortcut_tabs:
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # 创建表格
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["按键", "动作"])
            
            # 设置表格属性
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            
            # 填充数据
            self._populate_table(table, shortcuts)
            
            layout.addWidget(table)
            
            # 添加按钮
            button_layout = QHBoxLayout()
            
            add_btn = QPushButton("添加")
            add_btn.clicked.connect(lambda checked, t=table: self._add_row(t))
            
            remove_btn = QPushButton("删除")
            remove_btn.clicked.connect(lambda checked, t=table: self._remove_row(t))
            
            button_layout.addWidget(add_btn)
            button_layout.addWidget(remove_btn)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            self.tab_widget.addTab(tab, tab_name)
            self.tables[key] = table

    def _create_appearance_tab(self):
        """创建外观设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建滚动区域以防内容过多
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 样式预设组
        preset_group = QGroupBox("样式预设")
        preset_layout = QFormLayout(preset_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(STYLE_PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        preset_layout.addRow("选择预设:", self.preset_combo)
        
        # 添加预览按钮
        self.preview_btn = QPushButton("预览")
        self.preview_btn.clicked.connect(self._preview_preset)
        preset_layout.addRow("", self.preview_btn)
        
        scroll_layout.addWidget(preset_group)
        
        # 卡片尺寸设置组
        size_group = QGroupBox("卡片尺寸")
        size_layout = QFormLayout(size_group)
        
        self.card_size_spin = QSpinBox()
        self.card_size_spin.setRange(60, 150)
        self.card_size_spin.setValue(self.current_appearance.get("card_size", 90))
        self.card_size_spin.setSuffix(" px")
        size_layout.addRow("卡片大小:", self.card_size_spin)
        
        scroll_layout.addWidget(size_group)
        
        # 字体设置组
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)
        
        self.key_font_size_spin = QSpinBox()
        self.key_font_size_spin.setRange(12, 48)
        self.key_font_size_spin.setValue(self.current_appearance.get("key_font_size", 24))
        self.key_font_size_spin.setSuffix(" px")
        font_layout.addRow("按键字体大小:", self.key_font_size_spin)
        
        self.action_font_size_spin = QSpinBox()
        self.action_font_size_spin.setRange(8, 24)
        self.action_font_size_spin.setValue(self.current_appearance.get("action_font_size", 10))
        self.action_font_size_spin.setSuffix(" px")
        font_layout.addRow("动作字体大小:", self.action_font_size_spin)
        
        scroll_layout.addWidget(font_group)
        
        # 颜色设置组
        color_group = QGroupBox("颜色设置")
        color_layout = QFormLayout(color_group)
        
        self.key_color_btn = ColorButton(self.current_appearance.get("key_color", "#1a1a1e"))
        color_layout.addRow("按键文字颜色:", self.key_color_btn)
        
        self.action_color_btn = ColorButton(self.current_appearance.get("action_color", "#1e1e28"))
        color_layout.addRow("动作文字颜色:", self.action_color_btn)
        
        self.card_bg_start_btn = ColorButton(self.current_appearance.get("card_bg_color_start", "#ffffff"))
        color_layout.addRow("卡片背景起始色:", self.card_bg_start_btn)
        
        self.card_bg_end_btn = ColorButton(self.current_appearance.get("card_bg_color_end", "#f0f0fa"))
        color_layout.addRow("卡片背景结束色:", self.card_bg_end_btn)
        
        scroll_layout.addWidget(color_group)
        
        # 透明度设置组
        opacity_group = QGroupBox("透明度设置")
        opacity_layout = QFormLayout(opacity_group)
        
        self.background_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.background_opacity_slider.setRange(10, 100)
        self.background_opacity_slider.setValue(self.current_appearance.get("background_opacity", 50))
        
        self.opacity_label = QLabel(f"{self.background_opacity_slider.value()}%")
        self.background_opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_h_layout = QHBoxLayout()
        opacity_h_layout.addWidget(self.background_opacity_slider)
        opacity_h_layout.addWidget(self.opacity_label)
        
        opacity_layout.addRow("背景透明度:", opacity_h_layout)
        
        scroll_layout.addWidget(opacity_group)
        
        # 效果设置组
        effects_group = QGroupBox("动画效果")
        effects_layout = QFormLayout(effects_group)
        
        self.enable_animation_cb = QCheckBox()
        self.enable_animation_cb.setChecked(self.current_effects.get("enable_animation", True))
        effects_layout.addRow("启用动画:", self.enable_animation_cb)
        
        self.enable_blur_cb = QCheckBox()
        self.enable_blur_cb.setChecked(self.current_effects.get("enable_blur", True))
        effects_layout.addRow("启用模糊效果:", self.enable_blur_cb)
        
        self.animation_speed_combo = QComboBox()
        self.animation_speed_combo.addItems(["慢", "中等", "快"])
        speed_mapping = {"slow": 0, "medium": 1, "fast": 2}
        current_speed = self.current_effects.get("animation_speed", "medium")
        self.animation_speed_combo.setCurrentIndex(speed_mapping.get(current_speed, 1))
        effects_layout.addRow("动画速度:", self.animation_speed_combo)
        
        scroll_layout.addWidget(effects_group)
        
        # 添加弹簧
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "外观设置")

    def _create_buttons(self, layout):
        """创建对话框按钮"""
        button_layout = QHBoxLayout()
        
        # 添加弹簧
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # 重置按钮
        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)

    def _populate_table(self, table: QTableWidget, shortcuts: List[Dict]):
        """填充表格数据"""
        table.setRowCount(len(shortcuts))
        
        for row, shortcut in enumerate(shortcuts):
            key_item = QTableWidgetItem(shortcut["key"])
            action_item = QTableWidgetItem(shortcut["action"])
            
            table.setItem(row, 0, key_item)
            table.setItem(row, 1, action_item)

    def _add_row(self, table: QTableWidget):
        """添加新行"""
        row_count = table.rowCount()
        table.insertRow(row_count)
        
        # 设置默认值
        table.setItem(row_count, 0, QTableWidgetItem(""))
        table.setItem(row_count, 1, QTableWidgetItem(""))
        
        # 选中新行
        table.selectRow(row_count)

    def _remove_row(self, table: QTableWidget):
        """删除选中行"""
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)

    def _reset_to_defaults(self):
        """重置为默认设置"""
        # 简化重置逻辑，直接重置而不显示确认对话框
        # 避免QMessageBox可能导致的事件循环问题
        print("正在重置所有设置为默认值...")
        # 重新加载默认设置
        from utils.constants import (
            DEFAULT_SHORTCUT_ITEMS, DEFAULT_ALT_SHORTCUT_ITEMS,
            DEFAULT_CTRL_ALT_SHORTCUT_ITEMS, DEFAULT_WIN_SHORTCUT_ITEMS,
            DEFAULT_APPEARANCE, DEFAULT_EFFECTS
        )
        
        self.current_shortcuts = {
            "ctrl": DEFAULT_SHORTCUT_ITEMS.copy(),
            "alt": DEFAULT_ALT_SHORTCUT_ITEMS.copy(),
            "ctrl_alt": DEFAULT_CTRL_ALT_SHORTCUT_ITEMS.copy(),
            "win": DEFAULT_WIN_SHORTCUT_ITEMS.copy()
        }
        
        self.current_appearance = DEFAULT_APPEARANCE.copy()
        self.current_effects = DEFAULT_EFFECTS.copy()
        
        # 更新表格
        for key, table in self.tables.items():
            self._populate_table(table, self.current_shortcuts[key])
        
        # 更新外观设置控件
        self._update_appearance_controls()
        
        print("设置已重置为默认值")

    def _update_appearance_controls(self):
        """更新外观设置控件的值"""
        try:
            self.card_size_spin.setValue(self.current_appearance.get("card_size", 90))
            self.key_font_size_spin.setValue(self.current_appearance.get("key_font_size", 24))
            self.action_font_size_spin.setValue(self.current_appearance.get("action_font_size", 10))
            self.background_opacity_slider.setValue(self.current_appearance.get("background_opacity", 50))
            
            self.key_color_btn.set_color(self.current_appearance.get("key_color", "#1a1a1e"))
            self.action_color_btn.set_color(self.current_appearance.get("action_color", "#1e1e28"))
            self.card_bg_start_btn.set_color(self.current_appearance.get("card_bg_color_start", "#ffffff"))
            self.card_bg_end_btn.set_color(self.current_appearance.get("card_bg_color_end", "#f0f0fa"))
            
            self.enable_animation_cb.setChecked(self.current_effects.get("enable_animation", True))
            self.enable_blur_cb.setChecked(self.current_effects.get("enable_blur", True))
            
            speed_mapping = {"slow": 0, "medium": 1, "fast": 2}
            current_speed = self.current_effects.get("animation_speed", "medium")
            self.animation_speed_combo.setCurrentIndex(speed_mapping.get(current_speed, 1))
            
        except Exception as e:
            print(f"更新外观控件时出错: {e}")

    def _apply_preset(self, preset_name: str):
        """应用样式预设"""
        if preset_name in STYLE_PRESETS:
            preset = STYLE_PRESETS[preset_name]
            
            # 更新控件值
            self.card_size_spin.setValue(preset["card_size"])
            self.key_font_size_spin.setValue(preset["key_font_size"])
            self.action_font_size_spin.setValue(preset["action_font_size"])
            self.background_opacity_slider.setValue(preset["background_opacity"])
            
            self.key_color_btn.set_color(preset["key_color"])
            self.action_color_btn.set_color(preset["action_color"])
            self.card_bg_start_btn.set_color(preset["card_bg_color_start"])
            self.card_bg_end_btn.set_color(preset["card_bg_color_end"])

    def _preview_preset(self):
        """预览当前设置"""
        try:
            # 创建一个临时的预览窗口
            from ui.hint_widget import HintWidget
            
            # 创建临时配置
            temp_appearance = {
                "card_size": self.card_size_spin.value(),
                "key_font_size": self.key_font_size_spin.value(),
                "action_font_size": self.action_font_size_spin.value(),
                "background_opacity": self.background_opacity_slider.value(),
                "key_color": self.key_color_btn.get_color(),
                "action_color": self.action_color_btn.get_color(),
                "card_bg_color_start": self.card_bg_start_btn.get_color(),
                "card_bg_color_end": self.card_bg_end_btn.get_color()
            }
            
            # 临时更新配置
            from utils.config import _config_manager
            old_appearance = _config_manager.appearance.copy()
            _config_manager.appearance.update(temp_appearance)
            
            # 创建预览窗口
            preview_shortcuts = [
                {"key": "C", "action": "复制"},
                {"key": "V", "action": "粘贴"},
                {"key": "X", "action": "剪切"}
            ]
            
            preview_window = HintWidget(preview_shortcuts)
            preview_window.setWindowTitle("样式预览")
            preview_window.show_above_taskbar()
            
            # 3秒后自动关闭预览，并确保恢复配置
            from PySide6.QtCore import QTimer
            def cleanup_preview():
                try:
                    preview_window.hide()
                    # 恢复原配置
                    _config_manager.appearance.clear()
                    _config_manager.appearance.update(old_appearance)
                except Exception as cleanup_error:
                    print(f"清理预览窗口时出错: {cleanup_error}")
            
            QTimer.singleShot(3000, cleanup_preview)
            
        except Exception as e:
            print(f"预览样式时出错: {e}")
            # 使用print而不是QMessageBox，避免可能的事件循环问题
            print(f"预览失败: {e}")

    def _save_settings(self):
        """保存设置"""
        try:
            # 从表格中获取快捷键数据
            for key, table in self.tables.items():
                shortcuts = []
                for row in range(table.rowCount()):
                    key_item = table.item(row, 0)
                    action_item = table.item(row, 1)
                    
                    if key_item and action_item:
                        key_text = key_item.text().strip()
                        action_text = action_item.text().strip()
                        
                        if key_text and action_text:
                            shortcuts.append({"key": key_text, "action": action_text})
                
                self.current_shortcuts[key] = shortcuts
            
            # 获取外观设置
            self.current_appearance = {
                "card_size": self.card_size_spin.value(),
                "key_font_size": self.key_font_size_spin.value(),
                "action_font_size": self.action_font_size_spin.value(),
                "background_opacity": self.background_opacity_slider.value(),
                "key_color": self.key_color_btn.get_color(),
                "action_color": self.action_color_btn.get_color(),
                "card_bg_color_start": self.card_bg_start_btn.get_color(),
                "card_bg_color_end": self.card_bg_end_btn.get_color()
            }
            
            # 获取效果设置
            speed_mapping = {0: "slow", 1: "medium", 2: "fast"}
            self.current_effects = {
                "enable_animation": self.enable_animation_cb.isChecked(),
                "enable_blur": self.enable_blur_cb.isChecked(),
                "animation_speed": speed_mapping.get(self.animation_speed_combo.currentIndex(), "medium"),
                "show_on_press": True,  # 保持现有设置
                "auto_hide": True       # 保持现有设置
            }
            
            # 验证数据
            if self._validate_settings():
                self.accept()
            
        except Exception as e:
            print(f"保存设置时出错: {e}")
            # 不使用QMessageBox，避免可能的事件循环问题

    def _validate_settings(self) -> bool:
        """验证设置的有效性"""
        # 检查是否有空的快捷键组
        for key, shortcuts in self.current_shortcuts.items():
            if not shortcuts:
                print(f"验证失败: {key.upper()}快捷键组不能为空，请至少添加一个快捷键。")
                # 不使用QMessageBox，避免可能的事件循环问题
                return False
        
        return True

    def get_all_settings(self) -> Dict:
        """获取所有设置"""
        return {
            "shortcuts": self.current_shortcuts["ctrl"],
            "alt_shortcuts": self.current_shortcuts["alt"],
            "ctrl_alt_shortcuts": self.current_shortcuts["ctrl_alt"],
            "win_shortcuts": self.current_shortcuts["win"],
            "appearance": self.current_appearance,
            "effects": self.current_effects
        }

    # 为了兼容性，保留原有的方法名
    def get_shortcuts(self) -> List[Dict]:
        """获取Ctrl快捷键设置"""
        return self.current_shortcuts["ctrl"]

    def get_alt_shortcuts(self) -> List[Dict]:
        """获取Alt快捷键设置"""
        return self.current_shortcuts["alt"]

    def get_ctrl_alt_shortcuts(self) -> List[Dict]:
        """获取Ctrl+Alt快捷键设置"""
        return self.current_shortcuts["ctrl_alt"]

    def get_win_shortcuts(self) -> List[Dict]:
        """获取Win快捷键设置"""
        return self.current_shortcuts["win"]

    def get_appearance(self) -> Dict:
        """获取外观设置"""
        return self.current_appearance

    def get_effects(self) -> Dict:
        """获取效果设置"""
        return self.current_effects 