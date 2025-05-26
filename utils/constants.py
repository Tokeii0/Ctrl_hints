"""
常量定义 - 包含应用程序的默认配置和常量
"""

# 默认快捷键配置
DEFAULT_SHORTCUT_ITEMS = [
    {"key": "C", "action": "复制"},
    {"key": "V", "action": "粘贴"},
    {"key": "X", "action": "剪切"},
    {"key": "Z", "action": "撤销"},
    {"key": "Y", "action": "重做"},
    {"key": "A", "action": "全选"},
    {"key": "S", "action": "保存"},
    {"key": "F", "action": "查找"},
    {"key": "N", "action": "新建"},
    {"key": "O", "action": "打开"}
]

DEFAULT_ALT_SHORTCUT_ITEMS = [
    {"key": "Tab", "action": "切换窗口"},
    {"key": "F4", "action": "关闭窗口"},
    {"key": "Enter", "action": "属性"},
    {"key": "Space", "action": "系统菜单"},
    {"key": "←", "action": "后退"},
    {"key": "→", "action": "前进"}
]

DEFAULT_CTRL_ALT_SHORTCUT_ITEMS = [
    {"key": "Del", "action": "任务管理器"},
    {"key": "T", "action": "新建标签页"},
    {"key": "L", "action": "锁定屏幕"}
]

DEFAULT_WIN_SHORTCUT_ITEMS = [
    {"key": "D", "action": "显示桌面"},
    {"key": "L", "action": "锁定屏幕"},
    {"key": "R", "action": "运行对话框"},
    {"key": "E", "action": "文件资源管理器"},
    {"key": "I", "action": "设置"},
    {"key": "X", "action": "快速链接菜单"},
    {"key": "Tab", "action": "任务视图"},
    {"key": "↑", "action": "最大化窗口"},
    {"key": "↓", "action": "最小化窗口"},
    {"key": "←", "action": "窗口靠左"},
    {"key": "→", "action": "窗口靠右"}
]

# 默认外观配置
DEFAULT_APPEARANCE = {
    "card_size": 90,
    "key_font_size": 24,
    "action_font_size": 10,
    "background_opacity": 50,
    "key_color": "#1a1a1e",
    "action_color": "#1e1e28",
    "card_bg_color_start": "#ffffff",
    "card_bg_color_end": "#f0f0fa"
}

# 样式预设
STYLE_PRESETS = {
    "默认": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 50,
        "key_color": "#1a1a1e",
        "action_color": "#1e1e28",
        "card_bg_color_start": "#ffffff",
        "card_bg_color_end": "#f0f0fa"
    },
    "深色主题": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 80,
        "key_color": "#ffffff",
        "action_color": "#e0e0e0",
        "card_bg_color_start": "#2d2d2d",
        "card_bg_color_end": "#1a1a1a"
    },
    "蓝色主题": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 70,
        "key_color": "#ffffff",
        "action_color": "#e3f2fd",
        "card_bg_color_start": "#1976d2",
        "card_bg_color_end": "#0d47a1"
    },
    "绿色主题": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 70,
        "key_color": "#ffffff",
        "action_color": "#e8f5e8",
        "card_bg_color_start": "#4caf50",
        "card_bg_color_end": "#2e7d32"
    },
    "紫色主题": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 70,
        "key_color": "#ffffff",
        "action_color": "#f3e5f5",
        "card_bg_color_start": "#9c27b0",
        "card_bg_color_end": "#4a148c"
    },
    "橙色主题": {
        "card_size": 90,
        "key_font_size": 24,
        "action_font_size": 10,
        "background_opacity": 70,
        "key_color": "#ffffff",
        "action_color": "#fff3e0",
        "card_bg_color_start": "#ff9800",
        "card_bg_color_end": "#e65100"
    },
    "简约": {
        "card_size": 80,
        "key_font_size": 20,
        "action_font_size": 9,
        "background_opacity": 30,
        "key_color": "#333333",
        "action_color": "#666666",
        "card_bg_color_start": "#f8f9fa",
        "card_bg_color_end": "#e9ecef"
    },
    "大字体": {
        "card_size": 120,
        "key_font_size": 32,
        "action_font_size": 14,
        "background_opacity": 60,
        "key_color": "#1a1a1e",
        "action_color": "#1e1e28",
        "card_bg_color_start": "#ffffff",
        "card_bg_color_end": "#f0f0fa"
    }
}

# 默认效果配置
DEFAULT_EFFECTS = {
    "animation_enabled": True,
    "shadow_enabled": True,
    "blur_enabled": False,
    "fade_duration": 250,
    "slide_duration": 300
}

# 配置文件路径
CONFIG_FILE = "config.json"

# 支持的键盘按键映射
KEYBOARD_KEY_MAPPING = {
    "ctrl_l": "左Ctrl",
    "ctrl_r": "右Ctrl", 
    "ctrl": "Ctrl",
    "alt_l": "左Alt",
    "alt_r": "右Alt",
    "alt": "Alt",
    "cmd": "Win",
    "cmd_r": "右Win"
} 