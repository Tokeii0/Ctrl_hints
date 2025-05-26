#!/usr/bin/env python3
"""
Ctrl快捷键提示工具 - 主程序入口
一个简单实用的快捷键提示工具，帮助您快速查看和学习常用快捷键。

使用方法:
    python main.py

功能特点:1
- 支持 Ctrl、Alt、Win 键和组合键
- 美观的卡片式界面
- 流畅的动画效果
- 可自定义快捷键配置
- 系统托盘运行
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import CtrlHintApp


def setup_high_dpi():
    """设置高DPI支持"""
    # Qt 6.0+已经默认启用了高DPI缩放
    if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)


def check_dependencies():
    """检查依赖项"""
    try:
        import pynput
        from PySide6 import QtWidgets, QtCore, QtGui
        return True
    except ImportError as e:
        QMessageBox.critical(
            None,
            "依赖项缺失",
            f"缺少必要的依赖项: {e}\n\n请运行以下命令安装依赖:\npip install -r requirements.txt"
        )
        return False


def main():
    """主函数"""
    # 设置高DPI支持
    setup_high_dpi()
    
    # 创建QApplication实例
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Ctrl快捷键提示工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Assistant")
    app.setOrganizationDomain("github.com")
    
    # 正确处理高DPI
    if hasattr(app, 'setHighDpiScaleFactorRoundingPolicy'):
        app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # 检查依赖项
    if not check_dependencies():
        return 1
    
    try:
        # 创建并运行主应用程序
        main_app = CtrlHintApp()
        return main_app.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 0
    except Exception as e:
        print(f"程序运行时发生未处理的错误: {e}")
        QMessageBox.critical(
            None,
            "程序错误",
            f"程序运行时发生错误:\n{e}\n\n请检查控制台输出获取更多信息。"
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 