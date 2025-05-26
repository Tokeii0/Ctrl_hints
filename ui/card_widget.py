"""
快捷键卡片组件 - 显示单个快捷键的卡片
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSequentialAnimationGroup, QParallelAnimationGroup, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QFont, QBrush, QPen, QRadialGradient
import math
import random

# 使用绝对导入避免相对导入问题
import sys
import os

# 确保项目根目录在sys.path中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.config import get_appearance


class Particle:
    """粒子类 - 用于烟花效果"""
    
    def __init__(self, x, y, vx, vy, color, size=3, life=1.0):
        self.x = x
        self.y = y
        self.vx = vx  # x方向速度
        self.vy = vy  # y方向速度
        self.color = color
        self.size = size
        self.life = life  # 生命值 (0-1)
        self.max_life = life
        self.gravity = 0.3  # 重力
        self.fade_speed = 0.02  # 淡出速度
    
    def update(self):
        """更新粒子状态"""
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 应用重力
        self.vy += self.gravity
        
        # 减少生命值
        self.life -= self.fade_speed
        
        # 减少速度（空气阻力）
        self.vx *= 0.98
        self.vy *= 0.98
        
        return self.life > 0
    
    def draw(self, painter):
        """绘制粒子"""
        if self.life <= 0:
            return
            
        # 根据生命值调整透明度和大小
        alpha = max(0, min(255, int(255 * self.life)))  # 确保alpha在0-255范围内
        current_size = max(0.1, self.size * self.life)  # 确保大小不为0
        
        # 创建渐变效果
        gradient = QRadialGradient(self.x, self.y, current_size)
        color_with_alpha = QColor(self.color)
        color_with_alpha.setAlpha(alpha)
        gradient.setColorAt(0, color_with_alpha)
        
        transparent = QColor(self.color)
        transparent.setAlpha(0)
        gradient.setColorAt(1, transparent)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(self.x - current_size/2), int(self.y - current_size/2), 
                          int(current_size), int(current_size))


class ShortcutCardWidget(QWidget):
    """快捷键卡片组件"""
    
    def __init__(self, key_char: str, action_name: str, parent=None):
        """
        初始化快捷键卡片
        
        Args:
            key_char: 按键字符
            action_name: 动作名称
            parent: 父组件
        """
        super().__init__(parent)
        self.setObjectName("ShortcutCard")  # 用于QSS选择器
        
        # 获取外观配置
        self.appearance = get_appearance()
        card_size = self.appearance.get("card_size", 90)
        
        self.setMinimumSize(card_size, card_size)
        self.setMaximumSize(card_size, card_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # 启用样式背景
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._setup_layout(key_char, action_name)
        self._setup_shadow_effect()
        self._apply_appearance_style()
        self._setup_animations()

    def _setup_layout(self, key_char: str, action_name: str):
        """设置布局和子组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        # 按键标签
        self.key_label = QLabel(key_char)
        self.key_label.setObjectName("keyLabel")
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_key = QFont()
        font_key.setPointSize(self.appearance.get("key_font_size", 24))
        font_key.setBold(True)
        self.key_label.setFont(font_key)

        # 动作标签
        self.action_label = QLabel(action_name)
        self.action_label.setObjectName("actionLabel")
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_action = QFont()
        font_action.setPointSize(self.appearance.get("action_font_size", 10))
        self.action_label.setFont(font_action)
        self.action_label.setWordWrap(True)

        layout.addWidget(self.key_label, stretch=2)
        layout.addWidget(self.action_label, stretch=1)

    def _apply_appearance_style(self):
        """应用外观样式"""
        # 获取颜色配置
        key_color = self.appearance.get("key_color", "#1a1a1e")
        action_color = self.appearance.get("action_color", "#1e1e28")
        bg_start = self.appearance.get("card_bg_color_start", "#ffffff")
        bg_end = self.appearance.get("card_bg_color_end", "#f0f0fa")
        opacity = self.appearance.get("background_opacity", 50)
        
        # 计算实际的透明度值
        alpha = int(255 * opacity / 100)
        
        # 应用样式
        style = f"""
        ShortcutCardWidget#ShortcutCard {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 rgba({self._hex_to_rgb(bg_start)}, {alpha}),
                                       stop: 1 rgba({self._hex_to_rgb(bg_end)}, {alpha}));
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 80);
        }}
        
        QLabel#keyLabel {{
            color: {key_color};
            background-color: transparent;
        }}
        
        QLabel#actionLabel {{
            color: {action_color};
            background-color: transparent;
        }}
        """
        
        self.setStyleSheet(style)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """将十六进制颜色转换为RGB字符串"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"

    def _setup_shadow_effect(self):
        """设置阴影效果"""
        try:
            # 进一步简化阴影效果，减少渲染负担
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(10)  # 大幅减少模糊半径
            shadow.setColor(QColor(0, 0, 0, 30))  # 大幅降低不透明度
            shadow.setOffset(0, 1)  # 最小偏移
            self.setGraphicsEffect(shadow)
        except Exception as e:
            # 如果阴影设置失败，完全禁用阴影
            self.setGraphicsEffect(None)
            print(f"阴影效果已禁用: {e}")
    
    def _setup_animations(self):
        """设置动画效果"""
        # 粒子系统
        self.particles = []
        self.firework_timer = QTimer()
        self.firework_timer.timeout.connect(self._update_particles)
        
        # 烟花颜色列表 - 使用中国风配色
        self.firework_colors = [
            QColor(255, 215, 0),    # 金色
            QColor(255, 69, 0),     # 橙红色
            QColor(255, 20, 147),   # 深粉色
            QColor(138, 43, 226),   # 蓝紫色
            QColor(0, 191, 255),    # 深天蓝
            QColor(50, 205, 50),    # 酸橙绿
            QColor(255, 105, 180),  # 热粉色
            QColor(255, 140, 0),    # 深橙色
        ]
        
        # 动画状态
        self.animation_state = "normal"  # normal, fireworks

    def paintEvent(self, event):
        """自定义绘制以确保圆角背景被正确应用"""
        try:
            # 绘制基础样式
            super().paintEvent(event)
            
            # 绘制粒子效果
            if self.particles:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                
                for particle in self.particles:
                    particle.draw(painter)
                
                painter.end()
                
        except (KeyboardInterrupt, SystemExit):
            # 允许正常的程序退出
            raise
        except Exception as e:
            # 捕获所有其他异常，避免绘制错误导致程序崩溃
            print(f"绘制错误（已忽略）: {e}")
            # 不重新抛出异常，让程序继续运行

    def update_content(self, key_char: str, action_name: str):
        """
        更新卡片内容
        
        Args:
            key_char: 新的按键字符
            action_name: 新的动作名称
        """
        self.key_label.setText(key_char)
        self.action_label.setText(action_name)

    def _create_firework(self, x, y, color):
        """创建烟花爆炸效果"""
        particle_count = random.randint(15, 25)  # 随机粒子数量
        
        for _ in range(particle_count):
            # 随机角度和速度
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            
            # 计算速度分量
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # 随机粒子大小和生命值
            size = random.uniform(2, 5)
            life = random.uniform(0.8, 1.2)
            
            # 创建粒子
            particle = Particle(x, y, vx, vy, color, size, life)
            self.particles.append(particle)
    
    def _update_particles(self):
        """更新粒子状态"""
        try:
            # 更新所有粒子
            self.particles = [p for p in self.particles if p.update()]
            
            # 如果没有粒子了，停止动画
            if not self.particles:
                self.firework_timer.stop()
                self.animation_state = "normal"
                print("✨ 烟花动画结束")
            
            # 重绘组件
            self.update()
            
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print(f"粒子更新错误（已忽略）: {e}")
            # 清理粒子，停止动画
            self.particles.clear()
            self.firework_timer.stop()
            self.animation_state = "normal"
    
    def trigger_animation(self):
        """触发烟花动画效果"""
        try:
            print(f"🎆 触发烟花动画: {self.key_label.text()} 键")
            
            # 停止之前的动画（如果正在运行）
            if self.firework_timer.isActive():
                self.firework_timer.stop()
            
            # 清理之前的粒子
            self.particles.clear()
            
            # 设置动画状态
            self.animation_state = "fireworks"
            
            # 获取卡片中心位置
            center_x = self.width() // 2
            center_y = self.height() // 2
            
            # 创建多个烟花爆炸点
            explosion_points = [
                (center_x, center_y),  # 中心
                (center_x - 20, center_y - 15),  # 左上
                (center_x + 20, center_y - 15),  # 右上
                (center_x, center_y + 20),  # 下方
            ]
            
            # 为每个爆炸点创建烟花，使用不同颜色
            for i, (x, y) in enumerate(explosion_points):
                color = self.firework_colors[i % len(self.firework_colors)]
                # 延迟创建，形成连续爆炸效果
                QTimer.singleShot(i * 150, lambda x=x, y=y, c=color: self._create_firework(x, y, c))
            
            # 启动粒子更新定时器（30fps）
            self.firework_timer.start(33)
            
        except (KeyboardInterrupt, SystemExit):
            # 允许正常的程序退出
            raise
        except Exception as e:
            # 捕获动画触发过程中的异常
            print(f"烟花动画触发错误（已忽略）: {e}")
            # 尝试恢复到正常状态
            try:
                self.particles.clear()
                self.firework_timer.stop()
                self.animation_state = "normal"
            except:
                pass
    
    def matches_key(self, key_char: str) -> bool:
        """
        检查是否匹配指定的按键
        
        Args:
            key_char: 要匹配的按键字符
            
        Returns:
            bool: 匹配返回True，否则返回False
        """
        return self.key_label.text().upper() == key_char.upper()
    
    def update_appearance(self):
        """更新外观设置"""
        # 重新获取外观配置
        self.appearance = get_appearance()
        
        # 更新卡片尺寸
        card_size = self.appearance.get("card_size", 90)
        self.setMinimumSize(card_size, card_size)
        self.setMaximumSize(card_size, card_size)
        
        # 更新字体大小
        font_key = self.key_label.font()
        font_key.setPointSize(self.appearance.get("key_font_size", 24))
        self.key_label.setFont(font_key)
        
        font_action = self.action_label.font()
        font_action.setPointSize(self.appearance.get("action_font_size", 10))
        self.action_label.setFont(font_action)
        
        # 重新应用样式
        self._apply_appearance_style() 