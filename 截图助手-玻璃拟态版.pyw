#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 - 玻璃拟态版 (Glassmorphism)
真正的玻璃拟态设计,半透明毛玻璃效果
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
    from PIL import ImageGrab, Image, ImageTk, ImageDraw, ImageFilter, ImageFont
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "pillow"])
    sys.exit()

import win32clipboard
import win32gui
import win32con
import win32api

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
    from BlurWindow.blurWindow import blur, GlobalBlur
except ImportError:
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", "BlurWindow"])
    from BlurWindow.blurWindow import blur, GlobalBlur


# 玻璃拟态颜色配置
GLASS_COLORS = {
    'primary': {
        'bg': 'rgba(255, 255, 255, 0.15)',
        'border': '#FFFFFF',
        'accent': '#007AFF'
    },
    'success': {
        'bg': 'rgba(52, 199, 89, 0.2)',
        'border': '#34C759',
        'accent': '#34C759'
    },
    'warning': {
        'bg': 'rgba(255, 149, 0, 0.2)',
        'border': '#FF9500',
        'accent': '#FF9500'
    }
}


def apply_glassmorphism(hwnd):
    """应用Windows 11 Acrylic玻璃效果"""
    try:
        # 使用GlobalBlur实现真正的背景模糊
        GlobalBlur(hwnd, Acrylic=True, Dark=False, Animations=True)
    except:
        try:
            blur(hwnd, Acrylic=True, Dark=False)
        except:
            pass


class GlassFloatingWidget:
    """玻璃拟态悬浮窗"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.97)

        # 窗口尺寸
        self.size = 110
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{self.size}x{self.size}+{screen_width-130}+70")

        # 玻璃拟态配色
        self.colors = {
            'ready': '#34C759',
            'capturing': '#FF9500',
            'monitoring': '#007AFF',
            'glass_bg': '#F8F8FF',  # 浅色玻璃背景
            'border': '#FFFFFF',
            'shadow': '#00000020'
        }

        self.current_state = 'ready'

        # 创建画布 - 使用半透明背景
        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg='#F8F8FF',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()

        # 绘制UI
        self.create_glass_ui()

        # 事件绑定
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

        # 启动脉冲动画
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        self.start_pulse_animation()

        # 应用玻璃效果
        self.window.update()
        try:
            hwnd = int(self.window.wm_frame(), 16)
            apply_glassmorphism(hwnd)
        except:
            pass

    def create_glass_ui(self):
        """创建玻璃拟态UI"""
        center = self.size // 2

        # 外层光晕 - 多层柔和阴影
        for i in range(6):
            offset = i * 3
            alpha = int(40 - i * 5)
            color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
            self.canvas.create_oval(
                8-offset, 8-offset,
                self.size-8+offset, self.size-8+offset,
                fill='',
                outline=color,
                width=1
            )

        # 主玻璃圆形 - 半透明白色
        self.glass_bg = self.canvas.create_oval(
            8, 8, self.size-8, self.size-8,
            fill='white',
            outline='',
            width=0
        )

        # 玻璃边框 - 细白线
        self.glass_border = self.canvas.create_oval(
            8, 8, self.size-8, self.size-8,
            fill='',
            outline='white',
            width=2
        )

        # 状态彩色圆环 - 半透明
        self.status_ring = self.canvas.create_oval(
            14, 14, self.size-14, self.size-14,
            fill='',
            outline=self.colors[self.current_state],
            width=3
        )

        # 顶部高光效果
        self.highlight = self.canvas.create_arc(
            18, 12, self.size-18, self.size-30,
            start=30,
            extent=120,
            fill='',
            outline='white',
            width=1,
            style=tk.ARC
        )

        # 相机图标 - 玻璃风格
        icon_size = 24

        # 相机主体 - 圆角
        cam_points = [
            center - icon_size//2 + 4, center - icon_size//4,
            center + icon_size//2 - 4, center - icon_size//4,
            center + icon_size//2, center - icon_size//4 + 2,
            center + icon_size//2, center + icon_size//3 - 2,
            center + icon_size//2 - 4, center + icon_size//3,
            center - icon_size//2 + 4, center + icon_size//3,
            center - icon_size//2, center + icon_size//3 - 2,
            center - icon_size//2, center - icon_size//4 + 2
        ]
        self.camera_body = self.canvas.create_polygon(
            cam_points,
            fill=self.colors[self.current_state],
            outline='',
            smooth=True
        )

        # 镜头外圈
        self.lens_outer = self.canvas.create_oval(
            center - 9, center - 5,
            center + 9, center + 11,
            fill='white',
            outline=self.colors[self.current_state],
            width=2
        )

        # 镜头内圈
        self.lens_inner = self.canvas.create_oval(
            center - 5, center - 1,
            center + 5, center + 7,
            fill=self.colors[self.current_state],
            outline='',
            width=0
        )

        # 镜头反光
        self.lens_reflection = self.canvas.create_oval(
            center - 3, center,
            center + 1, center + 4,
            fill='white',
            outline='',
            stipple='gray50'
        )

        # 闪光灯
        self.flash = self.canvas.create_oval(
            center + 11, center - 7,
            center + 16, center - 2,
            fill='white',
            outline=self.colors[self.current_state],
            width=1
        )

        # 计数徽章 - 玻璃风格
        badge_x = center
        badge_y = self.size - 22

        # 徽章背景
        self.badge_bg = self.canvas.create_oval(
            badge_x - 16, badge_y - 10,
            badge_x + 16, badge_y + 10,
            fill=self.colors[self.current_state],
            outline='white',
            width=1
        )

        # 徽章高光
        self.badge_highlight = self.canvas.create_oval(
            badge_x - 14, badge_y - 8,
            badge_x + 8, badge_y + 2,
            fill='white',
            outline='',
            stipple='gray25'
        )

        # 计数文本
        self.count_text = self.canvas.create_text(
            badge_x, badge_y,
            text="0",
            font=("Segoe UI", 11, "bold"),
            fill='white'
        )

    def start_pulse_animation(self):
        """启动脉冲动画"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_pulse()

    def animate_pulse(self):
        """脉冲动画 - 玻璃呼吸效果"""
        if not self.animation_running:
            return

        try:
            if not self.is_hovering:
                # 脉冲效果
                self.pulse_scale += self.pulse_direction * 0.002

                if self.pulse_scale >= 1.03:
                    self.pulse_scale = 1.03
                    self.pulse_direction = -1
                elif self.pulse_scale <= 1.0:
                    self.pulse_scale = 1.0
                    self.pulse_direction = 1

                # 更新透明度
                alpha = 0.94 + (self.pulse_scale - 1.0) * 10
                self.window.attributes('-alpha', alpha)

                # 更新状态环宽度
                width = int(2 + (self.pulse_scale - 1.0) * 50)
                self.canvas.itemconfig(self.status_ring, width=width)

            self.window.after(40, self.animate_pulse)
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
        self.canvas.itemconfig(self.badge_bg, fill=color)

    def update_count(self, count):
        """更新计数"""
        self.canvas.itemconfig(self.count_text, text=str(count))

    def on_hover_enter(self, event):
        """鼠标进入 - 玻璃高亮"""
        self.is_hovering = True
        self.window.attributes('-alpha', 1.0)
        self.canvas.itemconfig(self.status_ring, width=4)
        self.canvas.itemconfig(self.glass_border, width=3)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False
        self.canvas.itemconfig(self.glass_border, width=2)

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
        """右键菜单 - 玻璃风格"""
        menu = tk.Menu(self.window, tearoff=0,
                      font=("Microsoft YaHei UI", 10),
                      bg='white', fg='black',
                      activebackground='#007AFF',
                      activeforeground='white',
                      relief=tk.FLAT, bd=1)
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
        self.animate_pulse()


class GlassCard(tk.Canvas):
    """玻璃拟态卡片"""
    def __init__(self, parent, width, height, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0, bd=0)

        # 绘制玻璃背景
        self.draw_glass_bg(width, height)

    def draw_glass_bg(self, w, h):
        """绘制玻璃背景"""
        radius = 20

        # 阴影层
        for i in range(4):
            offset = i * 2
            alpha = hex(int(30 - i * 5))[2:].zfill(2)
            shadow = f"#{alpha}{alpha}{alpha}"
            self.create_rounded_rect(
                4+offset, 4+offset, w-4+offset, h-4+offset,
                radius, fill=shadow, outline=''
            )

        # 主玻璃层
        self.bg_rect = self.create_rounded_rect(
            0, 0, w-4, h-4,
            radius, fill='white', outline=''
        )

        # 边框
        self.border = self.create_rounded_rect(
            1, 1, w-5, h-5,
            radius, fill='', outline='white', width=2
        )

        # 高光
        self.highlight = self.create_rounded_rect(
            4, 4, w-8, h//2,
            radius-4, fill='white', outline='', stipple='gray12'
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
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


class GlassButton(tk.Canvas):
    """玻璃拟态按钮"""
    def __init__(self, parent, text, command, width=200, height=54,
                 color='#007AFF', icon=''):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0, bd=0)

        self.command = command
        self.color = color
        self.hover_color = self.lighten_color(color)
        self.is_hover = False

        # 创建按钮
        self.draw_glass_button(width, height, color, icon, text)

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', lambda e: self.on_click())

    def draw_glass_button(self, w, h, color, icon, text):
        """绘制玻璃按钮"""
        radius = 14

        # 阴影
        for i in range(3):
            offset = i * 1
            alpha = hex(int(50 - i * 10))[2:].zfill(2)
            shadow = f"#{alpha}{alpha}{alpha}"
            self.create_rounded_rect(
                2, 2+offset, w-2, h-2+offset,
                radius, fill=shadow, outline=''
            )

        # 按钮背景
        self.bg = self.create_rounded_rect(
            0, 0, w-2, h-4,
            radius, fill=color, outline=''
        )

        # 边框
        self.border = self.create_rounded_rect(
            1, 1, w-3, h-5,
            radius, fill='', outline='white', width=2
        )

        # 高光
        self.highlight = self.create_rounded_rect(
            3, 3, w-5, h//2-2,
            radius-3, fill='white', outline='', stipple='gray12'
        )

        # 图标和文字
        if icon:
            self.icon_label = self.create_text(
                w//2 - 35, h//2,
                text=icon,
                font=("Segoe UI Emoji", 16),
                fill='white'
            )
            self.text_label = self.create_text(
                w//2 + 5, h//2,
                text=text,
                font=("Microsoft YaHei UI", 12, "bold"),
                fill='white',
                anchor=tk.W
            )
        else:
            self.text_label = self.create_text(
                w//2, h//2,
                text=text,
                font=("Microsoft YaHei UI", 12, "bold"),
                fill='white'
            )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
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

    def lighten_color(self, hex_color):
        """调亮颜色"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 增加亮度
        r = min(255, int(r * 1.15))
        g = min(255, int(g * 1.15))
        b = min(255, int(b * 1.15))
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_enter(self, event):
        self.is_hover = True
        self.itemconfig(self.bg, fill=self.hover_color)
        self.itemconfig(self.border, width=3)
        self.config(cursor='hand2')

    def on_leave(self, event):
        self.is_hover = False
        self.itemconfig(self.bg, fill=self.color)
        self.itemconfig(self.border, width=2)
        self.config(cursor='')

    def on_click(self):
        # 点击效果
        self.scale('all', self.winfo_width()//2, self.winfo_height()//2, 0.96, 0.96)
        self.after(80, lambda: self.scale('all', self.winfo_width()//2, self.winfo_height()//2, 1/0.96, 1/0.96))
        self.after(80, self.command)


class ScreenshotHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图助手 - 玻璃拟态版")
        self.root.geometry("620x820")
        self.root.resizable(False, False)

        # 设置半透明背景
        self.root.configure(bg='#F0F0F8')

        # 应用玻璃效果
        self.root.update()
        try:
            hwnd = int(self.root.wm_frame(), 16)
            apply_glassmorphism(hwnd)
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

        # 玻璃拟态配色
        self.colors = {
            'bg': '#F0F0F8',
            'primary': '#007AFF',
            'success': '#34C759',
            'warning': '#FF9500',
            'danger': '#FF3B30',
            'text': '#1C1C1E',
            'text_secondary': '#8E8E93'
        }

        # 创建UI
        self.create_glass_ui()

        # 创建悬浮窗
        self.floating_widget = GlassFloatingWidget(self)

        # 创建系统托盘
        self.create_tray_icon()

        # 注册热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.hide_main_window)

        # 默认显示悬浮窗
        self.root.withdraw()
        self.floating_widget.show()

    def create_glass_ui(self):
        """创建玻璃拟态UI"""
        # 主容器
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # 顶部栏
        self.create_header(main)

        # 状态卡片
        self.create_status_card(main)

        # 功能按钮
        self.create_buttons(main)

        # 路径卡片
        self.create_path_card(main)

        # 快捷键卡片
        self.create_hotkeys_card(main)

    def create_header(self, parent):
        """创建顶部栏"""
        header_canvas = GlassCard(parent, 560, 100)
        header_canvas.pack(pady=(0, 20))

        # 图标
        header_canvas.create_text(
            35, 50,
            text="📸",
            font=("Segoe UI Emoji", 40)
        )

        # 标题
        header_canvas.create_text(
            95, 40,
            text="截图助手",
            font=("Microsoft YaHei UI", 22, "bold"),
            fill=self.colors['text'],
            anchor=tk.W
        )

        # 副标题
        header_canvas.create_text(
            95, 68,
            text="玻璃拟态版 · Glassmorphism",
            font=("Segoe UI", 11),
            fill=self.colors['text_secondary'],
            anchor=tk.W
        )

        # 关闭按钮
        close_x, close_y = 530, 30
        close_btn_bg = header_canvas.create_oval(
            close_x-20, close_y-20,
            close_x+20, close_y+20,
            fill='#FF3B30',
            outline='white',
            width=2
        )
        close_btn_text = header_canvas.create_text(
            close_x, close_y,
            text="✕",
            font=("Segoe UI", 18, "bold"),
            fill='white'
        )

        def on_close_hover(event):
            header_canvas.itemconfig(close_btn_bg, fill='#FF1F14')
            header_canvas.config(cursor='hand2')

        def on_close_leave(event):
            header_canvas.itemconfig(close_btn_bg, fill='#FF3B30')
            header_canvas.config(cursor='')

        def on_close_click(event):
            self.hide_main_window()

        header_canvas.tag_bind(close_btn_bg, '<Enter>', on_close_hover)
        header_canvas.tag_bind(close_btn_text, '<Enter>', on_close_hover)
        header_canvas.tag_bind(close_btn_bg, '<Leave>', on_close_leave)
        header_canvas.tag_bind(close_btn_text, '<Leave>', on_close_leave)
        header_canvas.tag_bind(close_btn_bg, '<Button-1>', on_close_click)
        header_canvas.tag_bind(close_btn_text, '<Button-1>', on_close_click)

    def create_status_card(self, parent):
        """创建状态卡片"""
        card = GlassCard(parent, 560, 180)
        card.pack(pady=(0, 20))

        # 状态指示
        self.status_indicator = card.create_text(
            30, 40,
            text="●",
            font=("Segoe UI", 26),
            fill=self.colors['success']
        )

        self.status_label = card.create_text(
            60, 40,
            text="准备就绪",
            font=("Microsoft YaHei UI", 18, "bold"),
            fill=self.colors['text'],
            anchor=tk.W
        )

        # 分隔线
        card.create_line(40, 75, 520, 75, fill='#E5E5EA', width=1)

        # 统计数据
        # 今日截图
        card.create_text(
            140, 110,
            text="今日截图",
            font=("Microsoft YaHei UI", 12),
            fill=self.colors['text_secondary']
        )

        self.count_label = card.create_text(
            140, 145,
            text="0",
            font=("Segoe UI", 32, "bold"),
            fill=self.colors['primary']
        )

        # 分隔线
        card.create_line(280, 95, 280, 165, fill='#E5E5EA', width=1)

        # 历史文件
        history_count = len(list(self.screenshots_dir.glob('*.png')))
        card.create_text(
            420, 110,
            text="历史文件",
            font=("Microsoft YaHei UI", 12),
            fill=self.colors['text_secondary']
        )

        card.create_text(
            420, 145,
            text=str(history_count),
            font=("Segoe UI", 32, "bold"),
            fill=self.colors['success']
        )

        # 保存引用
        self.status_card = card

    def create_buttons(self, parent):
        """创建按钮"""
        card = GlassCard(parent, 560, 180)
        card.pack(pady=(0, 20))

        # 标题
        card.create_text(
            30, 30,
            text="快速操作",
            font=("Microsoft YaHei UI", 14, "bold"),
            fill=self.colors['text'],
            anchor=tk.W
        )

        # 按钮容器
        btn_frame = tk.Frame(card, bg='white')
        btn_frame.place(x=30, y=55)

        # 第一行
        row1 = tk.Frame(btn_frame, bg='white')
        row1.pack(pady=(0, 12))

        GlassButton(
            row1, "立即截图", self.capture_screenshot,
            width=250, height=54, color='#007AFF', icon='📷'
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.monitor_btn = GlassButton(
            row1, "自动监听", self.toggle_monitoring,
            width=250, height=54, color='#34C759', icon='🔄'
        )
        self.monitor_btn.pack(side=tk.LEFT)

        # 第二行
        row2 = tk.Frame(btn_frame, bg='white')
        row2.pack()

        GlassButton(
            row2, "复制路径", self.copy_path,
            width=166, height=48, color='#8E8E93', icon='📋'
        ).pack(side=tk.LEFT, padx=(0, 10))

        GlassButton(
            row2, "打开文件夹", self.open_folder,
            width=166, height=48, color='#8E8E93', icon='📂'
        ).pack(side=tk.LEFT, padx=(0, 10))

        GlassButton(
            row2, "清理缓存", self.clear_cache,
            width=166, height=48, color='#FF9500', icon='🗑️'
        ).pack(side=tk.LEFT)

    def create_path_card(self, parent):
        """创建路径卡片"""
        card = GlassCard(parent, 560, 130)
        card.pack(pady=(0, 20))

        # 标题
        card.create_text(
            30, 30,
            text="当前截图路径",
            font=("Microsoft YaHei UI", 13, "bold"),
            fill=self.colors['text'],
            anchor=tk.W
        )

        # 路径文本框
        path_bg = card.create_rounded_rect(
            25, 52, 535, 100,
            10, fill='#F5F5F7', outline='#E5E5EA', width=1
        )

        path_text = card.create_text(
            35, 76,
            text=str(self.current_path),
            font=("Consolas", 10),
            fill=self.colors['text'],
            anchor=tk.W,
            width=480
        )

        # 提示
        self.copy_tip_canvas = card
        self.copy_tip = card.create_text(
            30, 112,
            text="💡 截图后路径将自动复制到剪贴板",
            font=("Microsoft YaHei UI", 10),
            fill=self.colors['primary'],
            anchor=tk.W
        )

    def create_hotkeys_card(self, parent):
        """创建快捷键卡片"""
        card = GlassCard(parent, 560, 160)
        card.pack()

        # 标题
        card.create_text(
            30, 30,
            text="⌨️ 全局快捷键",
            font=("Microsoft YaHei UI", 13, "bold"),
            fill=self.colors['text'],
            anchor=tk.W
        )

        shortcuts = [
            ("Ctrl+Alt+A", "普通截图"),
            ("Shift+Win+S", "截图并复制路径"),
            ("Ctrl+Alt+F", "切换悬浮窗")
        ]

        y = 65
        for key, desc in shortcuts:
            # 快捷键标签
            card.create_rounded_rect(
                30, y, 150, y+26,
                8, fill='#F5F5F7', outline='#E5E5EA', width=1
            )
            card.create_text(
                90, y+13,
                text=key,
                font=("Consolas", 10, "bold"),
                fill=self.colors['text']
            )

            # 描述
            card.create_text(
                170, y+13,
                text=desc,
                font=("Microsoft YaHei UI", 11),
                fill=self.colors['text_secondary'],
                anchor=tk.W
            )

            y += 32

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
            self.status_card.itemconfig(self.count_label, text=str(self.screenshot_count))
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

        self.status_card.itemconfig(self.status_label, text=text)
        self.status_card.itemconfig(self.status_indicator, fill=colors_map[state])
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
        path = str(self.current_path)
        if self.copy_to_clipboard(path):
            self.update_status("路径已复制", 'ready')
            self.flash_copy_tip()
        else:
            self.update_status("复制失败", 'ready')

    def flash_copy_tip(self):
        self.copy_tip_canvas.itemconfig(self.copy_tip,
            text="✓ 已复制到剪贴板！",
            fill=self.colors['success']
        )
        self.root.after(2000, lambda: self.copy_tip_canvas.itemconfig(self.copy_tip,
            text="💡 截图后路径将自动复制到剪贴板",
            fill=self.colors['primary']
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

            # 玻璃圆形
            draw.ellipse([4, 4, 60, 60], fill='#007AFF', outline='white', width=2)

            # 相机图标
            draw.rounded_rectangle([20, 24, 44, 38], radius=2, fill='white')
            draw.ellipse([27, 27, 37, 35], fill='#007AFF', outline='white', width=2)
            draw.ellipse([40, 26, 43, 29], fill='white')

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

        self.tray_icon = pystray.Icon("screenshot_helper", icon_image,
                                      "截图助手 - 玻璃拟态版", menu)
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
