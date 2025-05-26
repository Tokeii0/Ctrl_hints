# 配置文件，存储共享常量和设置

# 定义默认快捷键项目
DEFAULT_SHORTCUT_ITEMS = [
    {"key": "Z", "action": "撤销"},
    {"key": "X", "action": "剪切"},
    {"key": "C", "action": "复制"},
    {"key": "V", "action": "粘贴"},
    {"key": "A", "action": "全选"},
    {"key": "F", "action": "查找"},
    {"key": "G", "action": "替换"}
]

import os
import json

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# 存储实际使用的快捷键项目
SHORTCUT_ITEMS = []

# 加载用户配置
def load_config():
    global SHORTCUT_ITEMS
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'shortcuts' in config and isinstance(config['shortcuts'], list):
                    SHORTCUT_ITEMS = config['shortcuts']
                    return
    except Exception as e:
        print(f"加载配置失败: {e}")
    
    # 使用默认配置
    SHORTCUT_ITEMS = DEFAULT_SHORTCUT_ITEMS.copy()

# 保存用户配置
def save_config(shortcuts):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'shortcuts': shortcuts}, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False

# 初始化加载配置
load_config()
