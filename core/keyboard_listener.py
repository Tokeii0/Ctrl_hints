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
    specific_key_pressed = Signal(str, str)  # 具体按键按下信号，参数为(修饰键类型, 按键字符)
    
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
            
            # 检测其他按键（在修饰键按下时）
            else:
                # 获取按键字符
                key_char = self._get_key_char(key)
                
                if key_char:
                    # 检查当前按下的修饰键状态
                    if self.key_states["ctrl"] and self.key_states["alt"]:
                        self.specific_key_pressed.emit("ctrl_alt", key_char)
                    elif self.key_states["ctrl"]:
                        self.specific_key_pressed.emit("ctrl", key_char)
                    elif self.key_states["alt"]:
                        self.specific_key_pressed.emit("alt", key_char)
                    elif self.key_states["win"]:
                        self.specific_key_pressed.emit("win", key_char)
        
        except (KeyboardInterrupt, SystemExit):
            # 允许正常的程序退出信号
            raise
        except Exception as e:
            print(f"键盘按下事件处理错误（已忽略）: {e}")
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
                        
        except (KeyboardInterrupt, SystemExit):
            # 允许正常的程序退出信号
            raise
        except Exception as e:
            print(f"键盘释放事件处理错误（已忽略）: {e}")
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

    def _get_key_char(self, key) -> str:
        """
        获取按键字符
        
        Args:
            key: pynput按键对象
            
        Returns:
            str: 按键字符，如果无法识别则返回None
        """
        try:
            # 处理字母和数字键
            if hasattr(key, 'char') and key.char:
                char_code = ord(key.char)
                
                # 处理Ctrl+字母键的控制字符
                if char_code >= 1 and char_code <= 26:
                    # Ctrl+A=1, Ctrl+B=2, ..., Ctrl+Z=26
                    result = chr(char_code + ord('A') - 1)
                    return result
                # 处理正常的可打印字符
                elif key.char.isprintable() and len(key.char) == 1:
                    return key.char.upper()
                else:
                    return None
            
            # 处理特殊键
            special_keys = {
                keyboard.Key.tab: "Tab",
                keyboard.Key.enter: "Enter",
                keyboard.Key.space: "Space",
                keyboard.Key.backspace: "Backspace",
                keyboard.Key.delete: "Del",
                keyboard.Key.esc: "Esc",
                keyboard.Key.f1: "F1",
                keyboard.Key.f2: "F2",
                keyboard.Key.f3: "F3",
                keyboard.Key.f4: "F4",
                keyboard.Key.f5: "F5",
                keyboard.Key.f6: "F6",
                keyboard.Key.f7: "F7",
                keyboard.Key.f8: "F8",
                keyboard.Key.f9: "F9",
                keyboard.Key.f10: "F10",
                keyboard.Key.f11: "F11",
                keyboard.Key.f12: "F12",
                keyboard.Key.left: "←",
                keyboard.Key.right: "→",
                keyboard.Key.up: "↑",
                keyboard.Key.down: "↓",
                keyboard.Key.home: "Home",
                keyboard.Key.end: "End",
                keyboard.Key.page_up: "PgUp",
                keyboard.Key.page_down: "PgDn",
                keyboard.Key.insert: "Ins",
            }
            
            return special_keys.get(key, None)
            
        except (KeyboardInterrupt, SystemExit):
            # 允许正常的程序退出信号
            raise
        except Exception as e:
            print(f"获取按键字符时出错（已忽略）: {e}")
            return None

    def reset_state(self):
        """重置所有按键状态"""
        self.pressed_ctrl_keys.clear()
        self.pressed_alt_keys.clear()
        self.pressed_win_keys.clear()
        self.key_states = {"ctrl": False, "alt": False, "win": False} 