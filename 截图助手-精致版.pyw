#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 - 精致版
真正的iOS风格毛玻璃效果，精致美观的现代化设计
"""

import os
import sys
import time
import threading
import math
from datetime import datetime
from pathlib import Path
import ctypes

import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import ImageGrab, Image, ImageTk, ImageDraw, ImageFilter
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "pillow"])
    sys.exit()

import win32clipboard
import win32gui
import win32con

try:
    import keyboard
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard

try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "pystray"])
    import pystray
    from pystray import MenuItem as item

try:
    from BlurWindow.blurWindow import blur
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "BlurWindow"])
    from BlurWindow.blurWindow import blur


# Windows 11 毛玻璃效果
def apply_acrylic_blur(hwnd, dark_mode=False):
    """应用Windows 11 Acrylic毛玻璃效果"""
    try:
        blur(hwnd, Acrylic=True, Dark=dark_mode, Animations=True)
    except:
        pass


class ModernFloatingWidget:
    """现代化悬浮窗 - 精致设计"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.98)

        # 窗口尺寸
        self.size = 100
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"{self.size}x{self.size}+{screen_width-120}+60")

        # iOS风格配色 - 更柔和的色彩
        self.colors = {
            'ready': '#34C759',      # 绿色
            'capturing': '#FF9500',  # 橙色
            'monitoring': '#007AFF', # 蓝色
            'bg': '#FFFFFF',
            'shadow': '#E5E5EA'
        }

        self.current_state = 'ready'

        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg='white',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()

        # 绘制UI
        self.create_modern_ui()

        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<Enter>', self.on_hover_enter)
        self.canvas.bind('<Leave>', self.on_hover_leave)

        self.drag_x = 0
        self.drag_y = 0
        self.is_hovering = False
        self.animation_running = False

        # 启动呼吸动画
        self.breath_alpha = 0
        self.breath_direction = 1
        self.start_breath_animation()

        # 应用毛玻璃效果
        self.window.update()
        try:
            hwnd = int(self.window.wm_frame(), 16)
            apply_acrylic_blur(hwnd, dark_mode=False)
        except:
            pass

    def create_modern_ui(self):
        """创建现代化UI"""
        center = self.size // 2

        # 外圈阴影 - 更柔和的阴影效果
        for i in range(4):
            offset = i * 2
            alpha_val = hex(int(255 * (0.1 - i * 0.02)))[2:].zfill(2)
            shadow_color = f"#{alpha_val}{alpha_val}{alpha_val}"
            self.canvas.create_oval(
                10-offset, 10-offset,
                self.size-10+offset, self.size-10+offset,
                fill='',
                outline=shadow_color,
                width=1
            )

        # 主圆形背景 - 纯白
        self.bg_circle = self.canvas.create_oval(
            10, 10, self.size-10, self.size-10,
            fill='white',
            outline='',
            width=0
        )

        # 状态指示圈 - 彩色圆环
        self.status_ring = self.canvas.create_oval(
            15, 15, self.size-15, self.size-15,
            fill='',
            outline=self.colors[self.current_state],
            width=3
        )

        # 内圈高光
        self.highlight_ring = self.canvas.create_oval(
            18, 13, self.size-32, self.size-37,
            fill='',
            outline='#F5F5F5',
            width=1
        )

        # 相机图标 - 更精致的设计
        icon_scale = 0.25

        # 相机主体 - 圆角矩形效果
        cam_w, cam_h = 24, 18
        self.camera_body = self.canvas.create_oval(
            center - cam_w//2, center - cam_h//3,
            center + cam_w//2, center + cam_h//2,
            fill=self.colors[self.current_state],
            outline='',
            width=0
        )

        # 镜头
        self.lens_outer = self.canvas.create_oval(
            center - 8, center - 4,
            center + 8, center + 10,
            fill='white',
            outline=self.colors[self.current_state],
            width=2
        )

        self.lens_inner = self.canvas.create_oval(
            center - 4, center,
            center + 4, center + 6,
            fill=self.colors[self.current_state],
            outline=''
        )

        # 闪光灯
        self.flash = self.canvas.create_oval(
            center + 10, center - 6,
            center + 14, center - 2,
            fill='white',
            outline=self.colors[self.current_state],
            width=1
        )

        # 计数标签 - 圆形徽章样式
        self.count_bg = self.canvas.create_oval(
            center - 12, self.size - 30,
            center + 12, self.size - 6,
            fill=self.colors[self.current_state],
            outline=''
        )

        self.count_text = self.canvas.create_text(
            center, self.size - 18,
            text="0",
            font=("Segoe UI", 12, "bold"),
            fill='white'
        )

    def start_breath_animation(self):
        """启动呼吸动画"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_breath()

    def animate_breath(self):
        """呼吸动画 - 更流畅自然"""
        if not self.animation_running:
            return

        try:
            if not self.is_hovering:
                # 使用正弦波实现更自然的呼吸效果
                self.breath_alpha += self.breath_direction * 2

                if self.breath_alpha >= 100:
                    self.breath_alpha = 100
                    self.breath_direction = -1
                elif self.breath_alpha <= 0:
                    self.breath_alpha = 0
                    self.breath_direction = 1

                # 计算透明度 (0.95 - 1.0 之间)
                alpha = 0.95 + (self.breath_alpha / 100) * 0.05
                self.window.attributes('-alpha', alpha)

                # 更新圆环宽度 (2-4 之间)
                width = 2 + int((self.breath_alpha / 100) * 2)
                self.canvas.itemconfig(self.status_ring, width=width)

            self.window.after(30, self.animate_breath)
        except:
            self.animation_running = False

    def update_state(self, state):
        """更新状态"""
        self.current_state = state
        color = self.colors[state]

        self.canvas.itemconfig(self.status_ring, outline=color)
        self.canvas.itemconfig(self.camera_body, fill=color)
        self.canvas.itemconfig(self.lens_outer, outline=color)
        self.canvas.itemconfig(self.lens_inner, fill=color)
        self.canvas.itemconfig(self.flash, outline=color)
        self.canvas.itemconfig(self.count_bg, fill=color)

    def update_count(self, count):
        """更新计数"""
        self.canvas.itemconfig(self.count_text, text=str(count))

    def on_hover_enter(self, event):
        """鼠标进入"""
        self.is_hovering = True
        self.window.attributes('-alpha', 1.0)
        self.canvas.itemconfig(self.status_ring, width=4)

        # 放大效果
        self.canvas.scale('all', self.size//2, self.size//2, 1.05, 1.05)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False

        # 还原大小
        self.canvas.scale('all', self.size//2, self.size//2, 1/1.05, 1/1.05)

    def on_press(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.press_time = time.time()

    def on_drag(self, event):
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")

    def on_click(self, event):
        if hasattr(self, 'press_time') and time.time() - self.press_time < 0.3:
            if abs(event.x - self.drag_x) < 5 and abs(event.y - self.drag_y) < 5:
                self.parent_app.show_main_window()

    def on_right_click(self, event):
        """右键菜单"""
        menu = tk.Menu(self.window, tearoff=0, font=("Segoe UI", 10))
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
        self.animate_breath()


class ModernCard(tk.Frame):
    """现代化卡片组件"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self.configure(relief=tk.FLAT, bd=0)


class ModernButton(tk.Canvas):
    """现代化按钮 - 更精致的设计"""
    def __init__(self, parent, text, command, width=180, height=50,
                 bg_color='#007AFF', text_color='white', icon='', style='primary'):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0, bd=0)

        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_hover = False
        self.style = style

        # 计算悬停颜色 (变暗15%)
        self.hover_color = self.darken_color(bg_color, 0.85)

        # 创建按钮背景
        self.create_button_bg(width, height)

        # 图标和文字
        if icon:
            self.icon_text = self.create_text(
                width//2 - 30, height//2,
                text=icon,
                font=("Segoe UI Emoji", 16),
                fill=text_color
            )
            self.text_obj = self.create_text(
                width//2 + 10, height//2,
                text=text,
                font=("Segoe UI", 11, "bold"),
                fill=text_color,
                anchor=tk.W
            )
        else:
            self.text_obj = self.create_text(
                width//2, height//2,
                text=text,
                font=("Segoe UI", 11, "bold"),
                fill=text_color
            )

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', lambda e: self.on_click())

    def create_button_bg(self, width, height):
        """创建按钮背景"""
        radius = 12

        # 阴影效果
        if self.style == 'primary':
            for i in range(3):
                offset = i * 1
                alpha = hex(int(255 * 0.1))[2:].zfill(2)
                shadow = f"#{alpha}{alpha}{alpha}"
                self.create_rounded_rectangle(
                    2, 2+offset, width-2, height-2+offset,
                    radius, fill=shadow, outline=''
                )

        # 主背景
        self.bg_rect = self.create_rounded_rectangle(
            0, 0, width-2, height-4,
            radius, fill=self.bg_color, outline=''
        )

        # 高光效果
        self.highlight = self.create_rounded_rectangle(
            2, 2, width-4, height//2,
            radius-2, fill='white', outline='', stipple='gray25'
        )
        self.itemconfig(self.highlight, state='hidden')

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """创建圆角矩形"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def darken_color(self, hex_color, factor):
        """调暗颜色"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_enter(self, event):
        self.is_hover = True
        self.itemconfig(self.bg_rect, fill=self.hover_color)
        self.itemconfig(self.highlight, state='normal')
        self.config(cursor='hand2')

    def on_leave(self, event):
        self.is_hover = False
        self.itemconfig(self.bg_rect, fill=self.bg_color)
        self.itemconfig(self.highlight, state='hidden')
        self.config(cursor='')

    def on_click(self):
        # 点击动画
        self.scale('all', self.winfo_width()//2, self.winfo_height()//2, 0.95, 0.95)
        self.after(100, lambda: self.scale('all', self.winfo_width()//2, self.winfo_height()//2, 1/0.95, 1/0.95))
        self.after(100, self.command)


class ScreenshotHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图助手 - 精致版")
        self.root.geometry("580x760")
        self.root.resizable(False, False)
        self.root.configure(bg='#F5F5F7')

        # 应用毛玻璃效果
        self.root.update()
        try:
            hwnd = int(self.root.wm_frame(), 16)
            apply_acrylic_blur(hwnd, dark_mode=False)
        except:
            pass

        # 路径设置
        self.base_dir = Path(r"C:\Users\zhouk\Desktop\截图助手")
        self.screenshots_dir = self.base_dir / "screenshots"
        self.current_path = self.base_dir / "current.png"
        self.screenshots_dir.mkdir(exist_ok=True)

        # 状态变量
        self.screenshot_count = 0
        self.monitoring = False
        self.last_image = None
        self.should_copy_path = False

        # iOS风格配色
        self.colors = {
            'bg': '#F5F5F7',
            'card': '#FFFFFF',
            'primary': '#007AFF',
            'success': '#34C759',
            'warning': '#FF9500',
            'danger': '#FF3B30',
            'text': '#000000',
            'text_secondary': '#8E8E93',
            'border': '#E5E5EA'
        }

        # 创建UI
        self.create_refined_ui()

        # 创建悬浮窗
        self.floating_widget = ModernFloatingWidget(self)

        # 创建系统托盘
        self.create_tray_icon()

        # 注册热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.hide_main_window)

        # 默认显示悬浮窗
        self.root.withdraw()
        self.floating_widget.show()

    def create_refined_ui(self):
        """创建精致UI"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # 顶部栏
        self.create_header(main_container)

        # 状态卡片
        self.create_status_card(main_container)

        # 功能按钮区
        self.create_action_buttons(main_container)

        # 路径信息卡片
        self.create_path_card(main_container)

        # 快捷键提示
        self.create_shortcuts_card(main_container)

    def create_header(self, parent):
        """创建顶部栏"""
        header = ModernCard(parent, height=90)
        header.pack(fill=tk.X, pady=(0, 20))

        content = tk.Frame(header, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # 左侧：图标和标题
        left = tk.Frame(content, bg='white')
        left.pack(side=tk.LEFT)

        tk.Label(
            left,
            text="📸",
            font=("Segoe UI Emoji", 36),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 15))

        title_frame = tk.Frame(left, bg='white')
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame,
            text="截图助手",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg='white',
            fg=self.colors['text']
        ).pack(anchor=tk.W)

        tk.Label(
            title_frame,
            text="精致版 v2.5",
            font=("Segoe UI", 10),
            bg='white',
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W)

        # 右侧：关闭按钮
        close_btn = tk.Label(
            content,
            text="✕",
            font=("Segoe UI", 24, "bold"),
            bg='white',
            fg=self.colors['text_secondary'],
            cursor='hand2'
        )
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind('<Button-1>', lambda e: self.hide_main_window())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=self.colors['danger']))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=self.colors['text_secondary']))

    def create_status_card(self, parent):
        """创建状态卡片"""
        card = ModernCard(parent)
        card.pack(fill=tk.X, pady=(0, 20))

        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.BOTH, padx=30, pady=30)

        # 状态指示器
        status_frame = tk.Frame(content, bg='white')
        status_frame.pack()

        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 24),
            bg='white',
            fg=self.colors['success']
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="准备就绪",
            font=("Microsoft YaHei UI", 16, "bold"),
            bg='white',
            fg=self.colors['text']
        )
        self.status_label.pack(side=tk.LEFT)

        # 分隔线
        tk.Frame(content, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=20)

        # 统计信息
        stats_frame = tk.Frame(content, bg='white')
        stats_frame.pack()

        # 今日截图数
        count_col = tk.Frame(stats_frame, bg='white')
        count_col.pack(side=tk.LEFT, padx=40)

        self.count_label = tk.Label(
            count_col,
            text="0",
            font=("Segoe UI", 42, "bold"),
            bg='white',
            fg=self.colors['primary']
        )
        self.count_label.pack()

        tk.Label(
            count_col,
            text="今日截图",
            font=("Microsoft YaHei UI", 11),
            bg='white',
            fg=self.colors['text_secondary']
        ).pack()

        # 分隔线
        tk.Frame(stats_frame, bg=self.colors['border'], width=1).pack(side=tk.LEFT, fill=tk.Y, padx=20)

        # 历史文件数
        history_count = len(list(self.screenshots_dir.glob('*.png')))
        history_col = tk.Frame(stats_frame, bg='white')
        history_col.pack(side=tk.LEFT, padx=40)

        tk.Label(
            history_col,
            text=str(history_count),
            font=("Segoe UI", 42, "bold"),
            bg='white',
            fg=self.colors['success']
        ).pack()

        tk.Label(
            history_col,
            text="历史文件",
            font=("Microsoft YaHei UI", 11),
            bg='white',
            fg=self.colors['text_secondary']
        ).pack()

    def create_action_buttons(self, parent):
        """创建功能按钮"""
        card = ModernCard(parent)
        card.pack(fill=tk.X, pady=(0, 20))

        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.BOTH, padx=25, pady=25)

        tk.Label(
            content,
            text="快速操作",
            font=("Microsoft YaHei UI", 13, "bold"),
            bg='white',
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 15))

        # 第一行：主要功能
        row1 = tk.Frame(content, bg='white')
        row1.pack(fill=tk.X, pady=(0, 12))

        ModernButton(
            row1, "立即截图", self.capture_screenshot,
            width=250, height=56, bg_color='#007AFF',
            icon='📷', style='primary'
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.monitor_btn = ModernButton(
            row1, "自动监听", self.toggle_monitoring,
            width=250, height=56, bg_color='#34C759',
            icon='🔄', style='primary'
        )
        self.monitor_btn.pack(side=tk.LEFT)

        # 第二行：辅助功能
        row2 = tk.Frame(content, bg='white')
        row2.pack(fill=tk.X)

        ModernButton(
            row2, "复制路径", self.copy_path,
            width=164, height=48, bg_color='#8E8E93',
            icon='📋', style='secondary'
        ).pack(side=tk.LEFT, padx=(0, 12))

        ModernButton(
            row2, "打开文件夹", self.open_folder,
            width=164, height=48, bg_color='#8E8E93',
            icon='📂', style='secondary'
        ).pack(side=tk.LEFT, padx=(0, 12))

        ModernButton(
            row2, "清理缓存", self.clear_cache,
            width=164, height=48, bg_color='#FF9500',
            icon='🗑️', style='secondary'
        ).pack(side=tk.LEFT)

    def create_path_card(self, parent):
        """创建路径卡片"""
        card = ModernCard(parent)
        card.pack(fill=tk.X, pady=(0, 20))

        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.BOTH, padx=25, pady=25)

        tk.Label(
            content,
            text="当前截图路径",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg='white',
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 12))

        # 路径显示框
        path_frame = tk.Frame(content, bg='#F5F5F7', relief=tk.FLAT)
        path_frame.pack(fill=tk.X, ipady=8)

        self.path_text = tk.Text(
            path_frame,
            height=2,
            font=("Consolas", 10),
            bg='#F5F5F7',
            fg=self.colors['text'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=10,
            bd=0
        )
        self.path_text.pack(fill=tk.X)
        self.path_text.insert('1.0', str(self.current_path))
        self.path_text.config(state=tk.DISABLED)

        # 提示信息
        self.copy_tip = tk.Label(
            content,
            text="💡 截图后路径将自动复制到剪贴板",
            font=("Microsoft YaHei UI", 10),
            bg='white',
            fg=self.colors['primary']
        )
        self.copy_tip.pack(anchor=tk.W, pady=(12, 0))

    def create_shortcuts_card(self, parent):
        """创建快捷键卡片"""
        card = ModernCard(parent)
        card.pack(fill=tk.X)

        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.BOTH, padx=25, pady=25)

        tk.Label(
            content,
            text="⌨️ 全局快捷键",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg='white',
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 15))

        shortcuts = [
            ("Ctrl+Alt+A", "普通截图"),
            ("Shift+Win+S", "截图并复制路径"),
            ("Ctrl+Alt+F", "切换悬浮窗")
        ]

        for key, desc in shortcuts:
            row = tk.Frame(content, bg='white')
            row.pack(fill=tk.X, pady=5)

            # 快捷键标签
            key_label = tk.Label(
                row,
                text=key,
                font=("Consolas", 10, "bold"),
                bg='#F5F5F7',
                fg=self.colors['text'],
                padx=12,
                pady=6
            )
            key_label.pack(side=tk.LEFT)

            # 描述
            tk.Label(
                row,
                text=desc,
                font=("Microsoft YaHei UI", 10),
                bg='white',
                fg=self.colors['text_secondary']
            ).pack(side=tk.LEFT, padx=15)

    def setup_hotkeys(self):
        """注册热键"""
        try:
            keyboard.add_hotkey('ctrl+alt+a', self.hotkey_normal_screenshot)
            keyboard.add_hotkey('shift+win+s', self.hotkey_screenshot_copy_path)
            keyboard.add_hotkey('ctrl+alt+f', self.toggle_window_mode)
        except:
            pass

    def toggle_window_mode(self):
        if self.root.state() == 'withdrawn':
            self.show_main_window()
        else:
            self.hide_main_window()

    def show_main_window(self):
        self.floating_widget.hide()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_main_window(self):
        self.root.withdraw()
        self.floating_widget.show()

    def hotkey_normal_screenshot(self):
        self.should_copy_path = False
        self.update_status("正在截图...", 'capturing')

        if self.root.state() != 'withdrawn':
            self.root.withdraw()

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_clipboard()

    def hotkey_screenshot_copy_path(self):
        self.should_copy_path = True
        self.update_status("截图并复制路径...", 'capturing')

        if self.root.state() != 'withdrawn':
            self.root.withdraw()

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_clipboard()

    def start_monitoring_clipboard(self):
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
            self.update_status("超时：未检测到截图", 'ready')

        threading.Thread(target=monitor, daemon=True).start()

    def capture_screenshot(self):
        self.update_status("正在截图...", 'capturing')
        self.root.withdraw()
        time.sleep(0.5)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("^+{s}")'])

        self.root.after(2000, self.check_clipboard_once)
        self.root.after(2500, lambda: self.root.deiconify())

    def check_clipboard_once(self):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.save_screenshot(img)
        except:
            self.update_status("截图失败", 'ready')

    def toggle_monitoring(self):
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        self.monitoring = True
        self.update_status("监听中...", 'monitoring')
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        self.update_status("已停止监听", 'ready')

    def monitor_loop(self):
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
                    self.update_status("截图成功！路径已复制", 'ready')
                    self.flash_copy_tip()
                else:
                    self.update_status("截图成功（复制失败）", 'ready')
                self.should_copy_path = False
            else:
                self.update_status("截图已保存", 'ready')

        except Exception as e:
            self.update_status(f"保存失败: {e}", 'ready')

    def update_status(self, text, state='ready'):
        colors_map = {
            'ready': self.colors['success'],
            'capturing': self.colors['warning'],
            'monitoring': self.colors['primary']
        }

        self.status_label.config(text=text)
        self.status_indicator.config(fg=colors_map[state])
        self.floating_widget.update_state(state)

    def copy_to_clipboard(self, text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except:
            return False

    def copy_path(self):
        self.path_text.config(state=tk.NORMAL)
        path = self.path_text.get('1.0', tk.END).strip()
        self.path_text.config(state=tk.DISABLED)

        if self.copy_to_clipboard(path):
            self.update_status("路径已复制", 'ready')
            self.flash_copy_tip()
        else:
            self.update_status("复制失败", 'ready')

    def flash_copy_tip(self):
        self.copy_tip.config(text="✓ 已复制到剪贴板！", fg=self.colors['success'])
        self.root.after(2000, lambda: self.copy_tip.config(
            text="💡 截图后路径将自动复制到剪贴板",
            fg=self.colors['primary']
        ))

    def open_folder(self):
        import subprocess
        subprocess.run(['explorer', str(self.screenshots_dir)])

    def clear_cache(self):
        """清理缓存"""
        count = len(list(self.screenshots_dir.glob('*.png')))
        result = messagebox.askyesno(
            "清理缓存",
            f"确定要清理所有历史截图吗？\n\n当前有 {count} 个文件",
            icon='warning'
        )

        if result:
            try:
                deleted = 0
                for file in self.screenshots_dir.glob('*.png'):
                    file.unlink()
                    deleted += 1

                self.update_status(f"已清理 {deleted} 个文件", 'ready')
                messagebox.showinfo("清理完成", f"成功清理了 {deleted} 个历史截图文件")
            except Exception as e:
                self.update_status(f"清理失败: {e}", 'ready')
                messagebox.showerror("清理失败", f"清理缓存时出错：{e}")

    def create_tray_icon(self):
        def create_icon_image():
            image = Image.new('RGB', (64, 64), color='white')
            draw = ImageDraw.Draw(image)

            # 圆形背景
            draw.ellipse([4, 4, 60, 60], fill='#007AFF', outline='')

            # 相机图标
            draw.rounded_rectangle([20, 24, 44, 40], radius=3, fill='white')
            draw.ellipse([26, 28, 38, 36], fill='#007AFF', outline='white', width=2)
            draw.ellipse([40, 26, 44, 30], fill='white')

            return image

        icon_image = create_icon_image()

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

        self.tray_icon = pystray.Icon("screenshot_helper", icon_image, "截图助手 - 精致版", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_closing(self):
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
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenshotHelper()
    app.run()
