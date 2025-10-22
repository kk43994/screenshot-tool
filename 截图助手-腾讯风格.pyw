#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 - 腾讯风格版本
现代化的界面设计，仿照腾讯系产品风格
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
import math

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

# 处理导入
try:
    from PIL import ImageGrab, Image, ImageTk, ImageDraw
except ImportError:
    import subprocess
    print("正在安装必要的库...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pillow"])
    print("安装完成，请重新运行程序")
    sys.exit()

# Windows 剪贴板支持
import win32clipboard

# 全局热键支持
try:
    import keyboard
except ImportError:
    import subprocess
    print("正在安装 keyboard 库...")
    subprocess.call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard

# 系统托盘支持
try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    import subprocess
    print("正在安装 pystray 库...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pystray"])
    import pystray
    from pystray import MenuItem as item


class FloatingWidget:
    """腾讯风格悬浮窗"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.92)

        # 窗口尺寸
        self.size = 70
        self.window.geometry(f"{self.size}x{self.size}+{self.get_screen_width()-90}+80")

        # 腾讯风格颜色
        self.colors = {
            'ready': '#07C160',      # 微信绿
            'capturing': '#FF9500',  # 提示橙
            'monitoring': '#1485EE', # 腾讯蓝
            'bg': '#FFFFFF',         # 白色背景
            'shadow': '#E0E0E0'      # 阴影
        }

        self.current_state = 'ready'

        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack()

        # 绘制圆形渐变背景
        self.draw_circle()

        # 添加图标（相机）
        self.draw_camera_icon()

        # 添加计数
        self.count_text = self.canvas.create_text(
            self.size // 2,
            self.size - 15,
            text="0",
            font=("Microsoft YaHei UI", 10, "bold"),
            fill='#666666'
        )

        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<Enter>', self.on_hover_enter)
        self.canvas.bind('<Leave>', self.on_hover_leave)

        self.drag_x = 0
        self.drag_y = 0

        # 动画相关
        self.is_hovering = False
        self.animation_running = False
        self.scale_factor = 1.0
        self.target_scale = 1.0

        # 添加阴影效果
        self.add_shadow()

        # 启动动画
        self.start_animation()

    def get_screen_width(self):
        return self.window.winfo_screenwidth()

    def add_shadow(self):
        """添加阴影效果"""
        # 外层阴影圆
        self.shadow_circle = self.canvas.create_oval(
            2, 2, self.size-2, self.size-2,
            fill='',
            outline=self.colors['shadow'],
            width=1
        )

    def draw_circle(self):
        """绘制圆形背景"""
        # 主圆形
        self.circle = self.canvas.create_oval(
            5, 5, self.size-5, self.size-5,
            fill=self.colors[self.current_state],
            outline='',
            width=0
        )

    def draw_camera_icon(self):
        """绘制相机图标"""
        center_x = self.size // 2
        center_y = self.size // 2 - 5

        # 相机主体（矩形）
        self.camera_body = self.canvas.create_rectangle(
            center_x - 12, center_y - 6,
            center_x + 12, center_y + 8,
            fill='white',
            outline='',
            width=0
        )

        # 镜头（圆形）
        self.camera_lens = self.canvas.create_oval(
            center_x - 7, center_y - 4,
            center_x + 7, center_y + 6,
            fill=self.colors[self.current_state],
            outline='white',
            width=2
        )

        # 快门按钮
        self.camera_button = self.canvas.create_rectangle(
            center_x + 8, center_y - 8,
            center_x + 12, center_y - 5,
            fill='white',
            outline='',
            width=0
        )

    def update_state(self, state):
        """更新状态和颜色"""
        self.current_state = state
        color = self.colors[state]
        self.canvas.itemconfig(self.circle, fill=color)
        self.canvas.itemconfig(self.camera_lens, fill=color)

    def update_count(self, count):
        """更新计数"""
        self.canvas.itemconfig(self.count_text, text=str(count))

    def start_animation(self):
        """启动缩放动画"""
        if not self.animation_running:
            self.animation_running = True
            self.animate()

    def animate(self):
        """平滑缩放动画"""
        if not self.animation_running:
            return

        try:
            # 平滑过渡到目标缩放
            if abs(self.scale_factor - self.target_scale) > 0.01:
                self.scale_factor += (self.target_scale - self.scale_factor) * 0.2

                # 应用缩放（通过改变窗口大小和透明度）
                if self.is_hovering:
                    self.window.attributes('-alpha', 1.0)
                else:
                    self.window.attributes('-alpha', 0.92)

            self.window.after(30, self.animate)
        except:
            self.animation_running = False

    def on_hover_enter(self, event):
        """鼠标进入"""
        self.is_hovering = True
        self.target_scale = 1.05
        self.window.attributes('-alpha', 1.0)
        # 添加高亮边框
        self.canvas.itemconfig(self.shadow_circle, outline='#1485EE', width=2)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False
        self.target_scale = 1.0
        self.window.attributes('-alpha', 0.92)
        # 恢复阴影
        self.canvas.itemconfig(self.shadow_circle, outline=self.colors['shadow'], width=1)

    def on_press(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.press_time = time.time()

    def on_drag(self, event):
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")

    def on_click(self, event):
        # 判断是点击还是拖动
        if hasattr(self, 'press_time') and time.time() - self.press_time < 0.3:
            if abs(event.x - self.drag_x) < 5 and abs(event.y - self.drag_y) < 5:
                self.parent_app.show_main_window()

    def on_right_click(self, event):
        """右键菜单"""
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="📷 立即截图", command=self.parent_app.capture_screenshot)
        menu.add_command(label="📋 复制路径", command=self.parent_app.copy_path)
        menu.add_separator()
        menu.add_command(label="🔄 打开主界面", command=self.parent_app.show_main_window)
        menu.add_separator()
        menu.add_command(label="❌ 退出程序", command=self.parent_app.on_closing)
        menu.post(event.x_root, event.y_root)

    def hide(self):
        self.animation_running = False
        self.window.withdraw()

    def show(self):
        self.window.deiconify()
        self.window.attributes('-topmost', True)
        self.animation_running = True
        self.animate()


class ModernButton(tk.Canvas):
    """现代化按钮组件"""
    def __init__(self, parent, text, command, width=120, height=40,
                 bg_color='#07C160', hover_color='#06AD56', text_color='white'):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0)

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hover = False

        # 绘制圆角矩形
        self.rect = self.create_rounded_rect(0, 0, width, height, 8, fill=bg_color)
        self.text = self.create_text(width//2, height//2, text=text,
                                     font=("Microsoft YaHei UI", 11, "bold"),
                                     fill=text_color)

        # 绑定事件
        self.tag_bind(self.rect, '<Button-1>', lambda e: self.command())
        self.tag_bind(self.text, '<Button-1>', lambda e: self.command())
        self.tag_bind(self.rect, '<Enter>', self.on_enter)
        self.tag_bind(self.text, '<Enter>', self.on_enter)
        self.tag_bind(self.rect, '<Leave>', self.on_leave)
        self.tag_bind(self.text, '<Leave>', self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, event):
        self.is_hover = True
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor='hand2')

    def on_leave(self, event):
        self.is_hover = False
        self.itemconfig(self.rect, fill=self.bg_color)
        self.config(cursor='')


class ScreenshotHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图助手")
        self.root.geometry("480x580")
        self.root.resizable(False, False)

        # 设置路径
        self.base_dir = Path(r"C:\Users\zhouk\Desktop\截图助手")
        self.screenshots_dir = self.base_dir / "screenshots"
        self.current_path = self.base_dir / "current.png"
        self.screenshots_dir.mkdir(exist_ok=True)

        # 状态变量
        self.screenshot_count = 0
        self.monitoring = False
        self.last_image = None
        self.should_copy_path = False

        # 腾讯风格颜色
        self.colors = {
            'bg': '#F7F7F7',
            'card_bg': '#FFFFFF',
            'primary': '#07C160',
            'secondary': '#1485EE',
            'text_primary': '#191919',
            'text_secondary': '#8C8C8C',
            'border': '#E5E5E5',
            'warning': '#FF9500',
            'error': '#FA5151'
        }

        self.root.configure(bg=self.colors['bg'])

        # 创建UI
        self.create_modern_ui()

        # 创建悬浮窗
        self.floating_widget = FloatingWidget(self)

        # 注册热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 创建系统托盘图标
        self.create_tray_icon()

        # 默认隐藏主窗口，显示悬浮窗
        self.root.withdraw()
        self.floating_widget.show()

    def create_modern_ui(self):
        """创建现代化UI"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 顶部栏
        self.create_header(main_frame)

        # 状态卡片
        self.create_status_card(main_frame)

        # 操作按钮区
        self.create_action_buttons(main_frame)

        # 路径卡片
        self.create_path_card(main_frame)

        # 快捷键说明
        self.create_hotkey_tips(main_frame)

    def create_header(self, parent):
        """创建顶部栏"""
        header = tk.Frame(parent, bg='#07C160', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # 标题
        title_label = tk.Label(
            header,
            text="📸 截图助手",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg='#07C160',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # 最小化按钮
        minimize_btn = tk.Label(
            header,
            text="—",
            font=("Arial", 16, "bold"),
            bg='#07C160',
            fg='white',
            cursor='hand2',
            width=3
        )
        minimize_btn.pack(side=tk.RIGHT, padx=5, pady=15)
        minimize_btn.bind('<Button-1>', lambda e: self.hide_main_window())

        # 悬浮窗按钮
        float_btn = tk.Label(
            header,
            text="⭐",
            font=("Arial", 16),
            bg='#07C160',
            fg='white',
            cursor='hand2',
            width=3
        )
        float_btn.pack(side=tk.RIGHT, padx=5, pady=15)
        float_btn.bind('<Button-1>', lambda e: self.hide_main_window())

    def create_status_card(self, parent):
        """创建状态卡片"""
        card = tk.Frame(parent, bg=self.colors['card_bg'])
        card.pack(fill=tk.X, padx=20, pady=15)

        # 添加圆角效果（模拟）
        card_inner = tk.Frame(card, bg=self.colors['card_bg'])
        card_inner.pack(fill=tk.BOTH, padx=2, pady=2)

        # 状态文本
        self.status_label = tk.Label(
            card_inner,
            text="● 准备就绪",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.status_label.pack(pady=15)

        # 计数显示
        count_frame = tk.Frame(card_inner, bg=self.colors['card_bg'])
        count_frame.pack(pady=10)

        tk.Label(
            count_frame,
            text="今日截图",
            font=("Microsoft YaHei UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT, padx=5)

        self.count_label = tk.Label(
            count_frame,
            text="0",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.count_label.pack(side=tk.LEFT, padx=5)

        tk.Label(
            count_frame,
            text="张",
            font=("Microsoft YaHei UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT)

    def create_action_buttons(self, parent):
        """创建操作按钮"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg'])
        btn_frame.pack(pady=20)

        # 第一行按钮
        row1 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row1.pack(pady=5)

        btn1 = ModernButton(
            row1, "📷 立即截图", self.capture_screenshot,
            width=200, height=48, bg_color='#07C160', hover_color='#06AD56'
        )
        btn1.pack(side=tk.LEFT, padx=10)

        # 自动监听按钮（状态按钮）
        self.monitor_btn_widget = ModernButton(
            row1, "🔄 自动监听", self.toggle_monitoring,
            width=200, height=48, bg_color='#1485EE', hover_color='#0D6FCC'
        )
        self.monitor_btn_widget.pack(side=tk.LEFT, padx=10)

        # 第二行按钮
        row2 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row2.pack(pady=5)

        btn3 = ModernButton(
            row2, "📋 复制路径", self.copy_path,
            width=200, height=48, bg_color='#8C8C8C', hover_color='#737373'
        )
        btn3.pack(side=tk.LEFT, padx=10)

        btn4 = ModernButton(
            row2, "📂 打开文件夹", self.open_folder,
            width=200, height=48, bg_color='#8C8C8C', hover_color='#737373'
        )
        btn4.pack(side=tk.LEFT, padx=10)

    def create_path_card(self, parent):
        """创建路径卡片"""
        card = tk.Frame(parent, bg=self.colors['card_bg'])
        card.pack(fill=tk.X, padx=20, pady=10)

        card_inner = tk.Frame(card, bg=self.colors['card_bg'])
        card_inner.pack(fill=tk.BOTH, padx=15, pady=15)

        # 标题
        tk.Label(
            card_inner,
            text="当前截图路径",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, pady=(0, 10))

        # 路径框
        path_frame = tk.Frame(card_inner, bg='#F5F5F5')
        path_frame.pack(fill=tk.X)

        self.path_text = tk.Text(
            path_frame,
            height=2,
            font=("Consolas", 9),
            bg='#F5F5F5',
            fg=self.colors['text_primary'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.path_text.pack(fill=tk.X)
        self.path_text.insert('1.0', str(self.current_path))

        # 提示文本
        self.copy_tip = tk.Label(
            card_inner,
            text="💡 截图后路径将自动复制到剪贴板",
            font=("Microsoft YaHei UI", 9),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.copy_tip.pack(anchor=tk.W, pady=(8, 0))

    def create_hotkey_tips(self, parent):
        """创建快捷键提示"""
        tips_frame = tk.Frame(parent, bg=self.colors['bg'])
        tips_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            tips_frame,
            text="⌨️ 快捷键",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_primary']
        ).pack(anchor=tk.W, pady=(0, 10))

        shortcuts = [
            ("Ctrl+Alt+A", "普通截图"),
            ("Shift+Win+S", "截图并复制路径"),
            ("Ctrl+Alt+F", "切换悬浮窗")
        ]

        for key, desc in shortcuts:
            row = tk.Frame(tips_frame, bg=self.colors['bg'])
            row.pack(fill=tk.X, pady=2)

            tk.Label(
                row,
                text=key,
                font=("Consolas", 9, "bold"),
                bg='#E5E5E5',
                fg=self.colors['text_primary'],
                padx=8,
                pady=2
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=desc,
                font=("Microsoft YaHei UI", 9),
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']
            ).pack(side=tk.LEFT, padx=10)

    def setup_hotkeys(self):
        """注册热键"""
        try:
            keyboard.add_hotkey('ctrl+alt+a', self.hotkey_normal_screenshot)
            keyboard.add_hotkey('shift+win+s', self.hotkey_screenshot_copy_path)
            keyboard.add_hotkey('ctrl+alt+f', self.toggle_window_mode)
            print("✓ 热键注册成功")
        except Exception as e:
            print(f"热键注册失败: {e}")

    def toggle_window_mode(self):
        """切换窗口模式"""
        if self.root.state() == 'withdrawn':
            self.show_main_window()
        else:
            self.hide_main_window()

    def show_main_window(self):
        """显示主窗口"""
        self.floating_widget.hide()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_main_window(self):
        """隐藏主窗口"""
        self.root.withdraw()
        self.floating_widget.show()

    def hotkey_normal_screenshot(self):
        """普通截图"""
        self.should_copy_path = False
        self.update_status("● 正在截图...", 'capturing')

        # 隐藏所有窗口
        if self.root.state() != 'withdrawn':
            self.root.withdraw()

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_clipboard()

    def hotkey_screenshot_copy_path(self):
        """截图并复制路径"""
        self.should_copy_path = True
        self.update_status("● 截图并复制路径...", 'capturing')

        # 隐藏所有窗口
        if self.root.state() != 'withdrawn':
            self.root.withdraw()

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_clipboard()

    def start_monitoring_clipboard(self):
        """监听剪贴板"""
        try:
            current_img = ImageGrab.grabclipboard()
        except:
            current_img = None

        def monitor():
            for i in range(40):
                time.sleep(0.5)
                try:
                    img = ImageGrab.grabclipboard()
                    if isinstance(img, Image.Image) and img != current_img:
                        self.root.after(0, lambda i=img: self.save_screenshot(i))
                        return
                except:
                    pass
            self.update_status("✗ 超时：未检测到截图", 'ready')

        threading.Thread(target=monitor, daemon=True).start()

    def capture_screenshot(self):
        """手动截图"""
        self.update_status("● 正在截图...", 'capturing')
        self.root.withdraw()
        time.sleep(0.5)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("^+{s}")'])

        self.root.after(2000, self.check_clipboard_once)
        self.root.after(2500, lambda: self.root.deiconify())

    def check_clipboard_once(self):
        """检查剪贴板"""
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.save_screenshot(img)
        except:
            self.update_status("✗ 截图失败", 'ready')

    def toggle_monitoring(self):
        """切换监听"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """开始监听"""
        self.monitoring = True
        # 更新按钮
        self.monitor_btn_widget.itemconfig(
            self.monitor_btn_widget.rect,
            fill='#FA5151'
        )
        self.monitor_btn_widget.itemconfig(
            self.monitor_btn_widget.text,
            text="⏸ 停止监听"
        )
        self.update_status("● 监听中...", 'monitoring')

        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        """停止监听"""
        self.monitoring = False
        self.monitor_btn_widget.itemconfig(
            self.monitor_btn_widget.rect,
            fill='#1485EE'
        )
        self.monitor_btn_widget.itemconfig(
            self.monitor_btn_widget.text,
            text="🔄 自动监听"
        )
        self.update_status("● 已停止监听", 'ready')

    def monitor_loop(self):
        """监听循环"""
        while self.monitoring:
            try:
                img = ImageGrab.grabclipboard()
                if isinstance(img, Image.Image) and img != self.last_image:
                    self.last_image = img
                    self.root.after(0, lambda: self.save_screenshot(img))
            except:
                pass
            time.sleep(1)

    def save_screenshot(self, img):
        """保存截图"""
        try:
            img.save(str(self.current_path))

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.screenshots_dir / f"screenshot_{timestamp}.png"
            img.save(str(backup_path))

            self.screenshot_count += 1
            self.count_label.config(text=str(self.screenshot_count))
            self.floating_widget.update_count(self.screenshot_count)

            if self.should_copy_path:
                if self.copy_to_clipboard(str(self.current_path)):
                    self.update_status("✓ 截图成功！路径已复制", 'ready')
                    self.flash_copy_tip()
                else:
                    self.update_status("✓ 截图成功（复制失败）", 'ready')
                self.should_copy_path = False
            else:
                self.update_status("✓ 截图已保存", 'ready')

        except Exception as e:
            self.update_status(f"✗ 保存失败: {e}", 'ready')

    def update_status(self, text, state='ready'):
        """更新状态"""
        colors_map = {
            'ready': self.colors['primary'],
            'capturing': self.colors['warning'],
            'monitoring': self.colors['secondary']
        }

        self.status_label.config(text=text, fg=colors_map[state])
        self.floating_widget.update_state(state)

    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except:
            return False

    def copy_path(self):
        """复制路径"""
        path = self.path_text.get('1.0', tk.END).strip()
        if self.copy_to_clipboard(path):
            self.update_status("✓ 路径已复制", 'ready')
            self.flash_copy_tip()
        else:
            self.update_status("✗ 复制失败", 'ready')

    def flash_copy_tip(self):
        """闪烁提示"""
        self.copy_tip.config(text="✓ 已复制到剪贴板！", fg='#07C160')
        self.root.after(2000, lambda: self.copy_tip.config(
            text="💡 截图后路径将自动复制到剪贴板",
            fg=self.colors['primary']
        ))

    def open_folder(self):
        """打开文件夹"""
        import subprocess
        subprocess.run(['explorer', str(self.screenshots_dir)])

    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建一个简单的图标图像
        def create_icon_image():
            from PIL import Image, ImageDraw
            # 创建64x64的图像
            image = Image.new('RGB', (64, 64), color='white')
            draw = ImageDraw.Draw(image)
            # 绘制绿色圆形
            draw.ellipse([8, 8, 56, 56], fill='#07C160', outline='white')
            # 绘制相机形状（简化）
            draw.rectangle([24, 26, 40, 38], fill='white')
            draw.ellipse([28, 28, 36, 36], fill='#07C160', outline='white')
            return image

        # 创建托盘图标
        icon_image = create_icon_image()

        # 创建菜单
        def quit_app(icon, item):
            icon.stop()
            self.on_closing()

        def show_window(icon, item):
            self.root.after(0, self.show_main_window)

        def show_float(icon, item):
            self.root.after(0, self.hide_main_window)

        menu = (
            item('显示主界面', show_window),
            item('显示悬浮窗', show_float),
            item('退出', quit_app)
        )

        self.tray_icon = pystray.Icon("screenshot_helper", icon_image, "截图助手", menu)

        # 在后台线程运行托盘图标
        def run_tray():
            self.tray_icon.run()

        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()

    def on_closing(self):
        """关闭程序"""
        self.monitoring = False
        try:
            self.tray_icon.stop()
        except:
            pass
        try:
            self.floating_widget.window.destroy()
        except:
            pass
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenshotHelper()
    app.run()
