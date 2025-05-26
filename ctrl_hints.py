import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QGraphicsDropShadowEffect, QSizePolicy, QSystemTrayIcon, 
                             QMenu, QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, Slot, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QScreen, QGuiApplication, QColor, QPainter, QPainterPath, QFont, QIcon, QAction

# 导入共享配置
from config import DEFAULT_SHORTCUT_ITEMS, SHORTCUT_ITEMS, load_config, save_config

from pynput import keyboard

# 在运行时导入设置模块
def import_settings():
    global SettingsDialog
    from settings import SettingsDialog

class KeyboardSignalEmitter(QObject):
    ctrl_pressed = Signal()
    ctrl_released = Signal()


class ShortcutCardWidget(QWidget):
    def __init__(self, key_char, action_name, parent=None):
        super().__init__(parent)
        self.setObjectName("ShortcutCard") # 用于QSS选择器
        self.setMinimumSize(90, 90) # 匹配QSS中的尺寸
        self.setMaximumSize(90, 90) # 确保是正方形
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # 启用样式背景
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8) # 匹配QSS中的padding
        layout.setSpacing(2)

        self.key_label = QLabel(key_char)
        self.key_label.setObjectName("keyLabel")
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_key = QFont()
        font_key.setPointSize(24) # 匹配QSS中的字体大小
        font_key.setBold(True)
        self.key_label.setFont(font_key)

        self.action_label = QLabel(action_name)
        self.action_label.setObjectName("actionLabel")
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_action = QFont()
        font_action.setPointSize(10) # 匹配QSS中的字体大小
        self.action_label.setFont(font_action)
        self.action_label.setWordWrap(True)

        layout.addWidget(self.key_label, stretch=2)
        layout.addWidget(self.action_label, stretch=1)

        # 卡片自身的阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25) # 增加模糊半径，更柔和
        shadow.setColor(QColor(0, 0, 0, 80)) # 降低阴影不透明度，更柔和
        shadow.setOffset(2, 4) # 调整偏移，更自然
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        # 自定义绘制以确保圆角背景被正确应用
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # 使用self.rect()减去一点边距，如果阴影在外部绘制的话
        path.addRoundedRect(self.rect(), 12, 12) # 匹配QSS中的圆角大小
        painter.setClipPath(path)
        super().paintEvent(event) # 确保子组件被绘制

class HintWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # 无窗口边框
            Qt.WindowType.WindowStaysOnTopHint |      # 窗口总在最前
            Qt.WindowType.Tool |                    # 工具窗口类型 (不在任务栏显示图标)
            Qt.WindowType.NoDropShadowWindowHint     # 禁用系统默认阴影，我们将自定义阴影
        )
        # 设置窗口属性，使其不获取焦点，并且在显示时不激活窗口
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # 启用背景透明，HintWidget本身是透明容器
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;") # 确保HintWidget背景透明
        
        # 初始化不透明度为0，用于动画
        self.setWindowOpacity(0.0)

        # 主容器使用水平布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5) # 容器本身的边距
        self.layout.setSpacing(10) # 卡片之间的间距
        
        # 初始化动画
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(250)  # 增加持续时间
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(180)  # 增加持续时间
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # 初始化位移动画
        self.slide_in_animation = QPropertyAnimation(self, b"pos")
        self.slide_in_animation.setDuration(300) # 增加持续时间，更流畅
        self.slide_in_animation.setEasingCurve(QEasingCurve.Type.OutBack) # 使用弹性效果

        self.slide_out_animation = QPropertyAnimation(self, b"pos")
        self.slide_out_animation.setDuration(200) # 增加持续时间
        self.slide_out_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        
        # 如果SHORTCUT_ITEMS为空，先加载配置
        if not SHORTCUT_ITEMS:
            load_config()
            
        self.setup_ui()

    def setup_ui(self):
        self.load_stylesheet("styles.qss")

        for item_data in SHORTCUT_ITEMS:
            card = ShortcutCardWidget(item_data["key"], item_data["action"])
            self.layout.addWidget(card)
        
        # self.setLayout(self.layout) # QHBoxLayout已在构造时传入self
        self.adjustSize() # 根据内容调整窗口大小

    def load_stylesheet(self, filename):
        try:
            # 处理PyInstaller打包后的路径
            if hasattr(sys, '_MEIPASS'):
                # 在打包的exe中，资源文件在临时目录中
                style_path = os.path.join(sys._MEIPASS, filename)
            else:
                # 在开发环境中，使用相对路径
                style_path = filename
            
            with open(style_path, "r", encoding="utf-8") as f:
                style = f.read()
                self.setStyleSheet(style)
        except FileNotFoundError:
            print(f"错误: 样式文件 '{filename}' 未找到。")
            # 如果找不到样式文件，使用默认样式
            self.apply_default_style()
        except Exception as e:
            print(f"加载样式文件时出错: {e}")
            self.apply_default_style()
    
    def apply_default_style(self):
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

    # HintWidget的paintEvent可能不再需要，因为它现在是透明容器
    # 如果需要为整个容器区域绘制一个统一的圆角背景（在所有卡片之后），则可以保留并修改
    # def paintEvent(self, event):
    #     pass

    def show_above_taskbar(self):
        screen = QGuiApplication.primaryScreen()
        if not screen:
            print("错误: 未找到主屏幕。")
            self.show() # Fallback
            return

        available_geom = screen.availableGeometry() # 可用桌面区域 (通常不包括任务栏)
        full_geom = screen.geometry() # 整个屏幕区域
        
        # 水平居中
        win_x = available_geom.left() + (available_geom.width() - self.width()) / 2
        
        # 默认假设任务栏在底部
        win_y = available_geom.bottom() - self.height() - 10 # 距离任务栏10像素

        # 检查任务栏是否在顶部
        # 如果可用区域的顶部y坐标大于整个屏幕的顶部y坐标 (通常为0)，说明顶部有东西 (可能是任务栏)
        if available_geom.y() > full_geom.y() and available_geom.height() < full_geom.height():
            win_y = available_geom.top() + 10 # 距离顶部任务栏10像素
        
        # 对于左右任务栏的情况，此基本定位逻辑可能不完美，但会确保在可用区域内

        final_pos = QPoint(int(win_x), int(win_y))
        start_pos_slide = QPoint(int(win_x), int(win_y) + 30) # 从下方30px处滑入，增加距离

        self.move(start_pos_slide) # 初始位置在目标位置下方
        self.setWindowOpacity(0.0)  # 确保开始时是透明的
        self.show()

        self.fade_in_animation.start()  # 开始淡入动画

        self.slide_in_animation.setStartValue(start_pos_slide)
        self.slide_in_animation.setEndValue(final_pos)
        self.slide_in_animation.start() # 开始滑入动画



class CtrlHintApp:
    def __init__(self):
        # 确保QApplication实例存在
        self.app = QApplication.instance() 
        if not self.app:
            self.app = QApplication(sys.argv)

        # 加载配置
        load_config()
            
        # 初始化托盘图标
        self.setup_tray_icon()
            
        self.hint_widget = HintWidget()
        self.keyboard_signal_emitter = KeyboardSignalEmitter()

        self.pressed_ctrl_keys = set()

        # 连接信号到槽
        self.keyboard_signal_emitter.ctrl_pressed.connect(self.show_hints)
        self.keyboard_signal_emitter.ctrl_released.connect(self.hide_hints)

        # 创建pynput键盘监听器
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
    def setup_tray_icon(self):
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self.load_icon(), self.app)
        self.tray_icon.setToolTip("Ctrl快捷键提示工具")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 添加设置菜单项
        settings_action = QAction("设置", self.app)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        # 添加退出菜单项
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def load_icon(self):
        # 处理PyInstaller打包后的路径
        if hasattr(sys, '_MEIPASS'):
            # 在打包的exe中，资源文件在临时目录中
            icon_path = os.path.join(sys._MEIPASS, 'res', 'logo.png')
        else:
            # 在开发环境中，使用相对路径
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res', 'logo.png')
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"警告: 图标文件 '{icon_path}' 未找到。")
            return QIcon() # 返回空图标
    
    def show_settings(self):
        global SHORTCUT_ITEMS
        
        # 在使用时才导入SettingsDialog类，避免循环导入
        import_settings()
        
        # 创建设置对话框
        dialog = SettingsDialog(SHORTCUT_ITEMS)
        
        # 如果用户点击保存
        if dialog.exec_():
            # 获取新的快捷键设置
            SHORTCUT_ITEMS = dialog.get_shortcuts()
            
            # 保存到配置文件
            if save_config(SHORTCUT_ITEMS):
                # 更新提示窗口内容而不是重新创建整个窗口
                # 清除现有卡片
                for i in reversed(range(self.hint_widget.layout.count())): 
                    widget = self.hint_widget.layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()
                
                # 添加新卡片
                for item_data in SHORTCUT_ITEMS:
                    card = ShortcutCardWidget(item_data["key"], item_data["action"])
                    self.hint_widget.layout.addWidget(card)
                
                # 调整窗口大小
                self.hint_widget.adjustSize()
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "保存失败", "保存设置时出错，请稍后再试。")
    
    def quit_app(self):
        # 停止监听器
        if hasattr(self, 'listener') and self.listener.running:
            self.listener.stop()
            self.listener.join()
        # 退出应用
        self.app.quit()

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or \
               key == keyboard.Key.ctrl:
                is_first_ctrl = not self.pressed_ctrl_keys
                self.pressed_ctrl_keys.add(key)
                if is_first_ctrl:
                    self.keyboard_signal_emitter.ctrl_pressed.emit()
        except Exception as e:
            print(f"on_press 错误: {e}")

    def on_key_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or \
               key == keyboard.Key.ctrl:
                if key in self.pressed_ctrl_keys:
                    self.pressed_ctrl_keys.remove(key)
                if not self.pressed_ctrl_keys: # 所有Ctrl键都已释放
                    self.keyboard_signal_emitter.ctrl_released.emit()
        except Exception as e:
            print(f"on_release 错误: {e}")

    @Slot()
    def show_hints(self):
        if not self.hint_widget.isVisible():
            self.hint_widget.show_above_taskbar()

    @Slot()
    def hide_hints(self):
        if self.hint_widget.isVisible() and self.hint_widget.fade_out_animation.state() != QPropertyAnimation.State.Running:
            current_pos = self.hint_widget.pos()
            end_pos_slide = QPoint(current_pos.x(), current_pos.y() + 30) # 向下滑出30px，增加距离

            # 断开所有连接，避免重复隐藏或连接累积
            try:
                # 只断开连接到hide方法的信号
                self.hint_widget.fade_out_animation.finished.disconnect(self.hint_widget.hide)
            except (TypeError, RuntimeError):
                # 如果尚未连接或出现其他错误，忽略
                pass

            # 确保动画结束后隐藏窗口
            # 我们让其中一个动画（比如淡出）结束后负责隐藏
            self.hint_widget.fade_out_animation.finished.connect(self.hint_widget.hide)

            self.hint_widget.fade_out_animation.start()

            self.hint_widget.slide_out_animation.setStartValue(current_pos)
            self.hint_widget.slide_out_animation.setEndValue(end_pos_slide)
            self.hint_widget.slide_out_animation.start()

    def run(self):
        print("Ctrl快捷键提示工具已启动。按住Ctrl键查看提示。")
        print("程序将在系统托盘中运行，右键点击托盘图标可以访问设置或退出程序。")
        self.listener.start()  # 在新线程中启动监听器
        
        # 显示托盘消息提示用户
        self.tray_icon.showMessage(
            "Ctrl快捷键提示工具",
            "程序已启动并在后台运行。\n按住Ctrl键可以显示快捷键提示。\n右键点击托盘图标可以访问设置或退出程序。",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        
        exit_code = self.app.exec()
        
        self.listener.stop()   # 停止监听器
        self.listener.join()   # 等待监听器线程结束
        print("程序已退出。")
        sys.exit(exit_code)

if __name__ == "__main__":
    # 高DPI支持，使用新的方式避免警告
    # Qt 6.0+已经默认启用了高DPI缩放
    if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    if hasattr(Qt, 'ApplicationAttribute'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    else:
        # 兼容老版本Qt的写法
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    main_app = CtrlHintApp()
    main_app.run()
