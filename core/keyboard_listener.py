"""
键盘监听器模块 - 负责监听键盘事件并发出信号
"""

from typing import Callable, Set
from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class KeyboardListener(QObject):
    """键盘监听器类"""
    
    # 定义信号
    key_pressed = Signal(str)    # 按键按下信号，参数为按键类型
    key_released = Signal(str)   # 按键释放信号，参数为按键类型
    
    def __init__(self):
        super().__init__()
        
        # 跟踪按键状态
        self.pressed_ctrl_keys: Set = set()
        self.pressed_alt_keys: Set = set()
        self.pressed_win_keys: Set = set()
        
        # 按键状态
        self.key_states = {
            "ctrl": False,
            "alt": False, 
            "win": False
        }
        
        # 线程安全锁
        self.key_lock = False
        
        # 创建pynput监听器
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )

    def _on_key_press(self, key):
        """处理按键按下事件"""
        try:
            # 防止多线程冲突
            if self.key_lock:
                return
            self.key_lock = True
            
            # 检测Ctrl键按下
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl:
                is_first_ctrl = not self.pressed_ctrl_keys  # 第一次按下Ctrl键
                self.pressed_ctrl_keys.add(key)
                
                if is_first_ctrl:
                    self.key_states["ctrl"] = True
                    # 检查是否已经处于Alt键按下状态
                    if self.key_states["alt"]:
                        # 发出Ctrl+Alt组合键信号
                        self.key_pressed.emit("ctrl_alt")
                    else:
                        # 发出Ctrl信号
                        self.key_pressed.emit("ctrl")
                
            # 检测Alt键按下
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt:
                is_first_alt = not self.pressed_alt_keys  # 第一次按下Alt键
                self.pressed_alt_keys.add(key)
                
                if is_first_alt:
                    self.key_states["alt"] = True
                    # 检查是否已经处于Ctrl键按下状态
                    if self.key_states["ctrl"]:
                        # 发出Ctrl+Alt组合键信号
                        self.key_pressed.emit("ctrl_alt")
                    else:
                        # 发出Alt信号
                        self.key_pressed.emit("alt")
            
            # 检测Win键按下
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
                self.pressed_win_keys.add(key)
                self.key_states["win"] = True
                # 发出Win键信号
                self.key_pressed.emit("win")
        
        except Exception as e:
            print(f"键盘按下事件处理错误: {e}")
        finally:
            self.key_lock = False

    def _on_key_release(self, key):
        """处理按键释放事件"""
        try:
            # 防止多线程冲突
            if self.key_lock:
                return
            self.key_lock = True
            
            # 检测Ctrl键释放
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl:
                self.pressed_ctrl_keys.discard(key)
                if not self.pressed_ctrl_keys:  # 所有Ctrl键都释放了
                    self.key_states["ctrl"] = False
                    # 发出释放信号
                    if self.key_states["alt"]:
                        self.key_released.emit("ctrl_alt")
                    else:
                        self.key_released.emit("ctrl")
                        
            # 检测Alt键释放
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt:
                self.pressed_alt_keys.discard(key)
                if not self.pressed_alt_keys:  # 所有Alt键都释放了
                    self.key_states["alt"] = False
                    # 发出释放信号
                    if self.key_states["ctrl"]:
                        self.key_released.emit("ctrl_alt")
                    else:
                        self.key_released.emit("alt")
                        
            # 检测Win键释放
            elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
                self.pressed_win_keys.discard(key)
                if not self.pressed_win_keys:  # 所有Win键都释放了
                    self.key_states["win"] = False
                    self.key_released.emit("win")
                        
        except Exception as e:
            print(f"键盘释放事件处理错误: {e}")
        finally:
            self.key_lock = False

    def start(self):
        """启动键盘监听"""
        try:
            self.listener.start()
            print("键盘监听器已启动")
        except Exception as e:
            print(f"启动键盘监听器失败: {e}")

    def stop(self):
        """停止键盘监听"""
        try:
            self.listener.stop()
            self.listener.join(timeout=0.5)
            print("键盘监听器已停止")
        except Exception as e:
            print(f"停止键盘监听器失败: {e}")

    def is_running(self) -> bool:
        """
        检查监听器是否正在运行
        
        Returns:
            bool: 正在运行返回True，否则返回False
        """
        return self.listener.running if hasattr(self.listener, 'running') else False

    def get_pressed_keys(self) -> dict:
        """
        获取当前按下的按键状态
        
        Returns:
            dict: 按键状态字典
        """
        return {
            "ctrl": bool(self.pressed_ctrl_keys),
            "alt": bool(self.pressed_alt_keys),
            "win": bool(self.pressed_win_keys)
        }

    def reset_state(self):
        """重置所有按键状态"""
        self.pressed_ctrl_keys.clear()
        self.pressed_alt_keys.clear()
        self.pressed_win_keys.clear()
        self.key_states = {"ctrl": False, "alt": False, "win": False} 