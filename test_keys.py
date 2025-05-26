import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from pynput import keyboard

class KeyTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("按键测试")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        self.status_label = QLabel("请按下或释放键盘上的按键...")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 创建键盘监听器
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
    def on_press(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
        
        self.status_label.setText(f"按下: {key_name}")
        print(f"按下键: {key_name}")
        
    def on_release(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
        
        self.status_label.setText(f"释放: {key_name}")
        print(f"释放键: {key_name}")
        
    def closeEvent(self, event):
        self.listener.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyTestWindow()
    window.show()
    sys.exit(app.exec())
