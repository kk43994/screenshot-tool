#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 - 毛玻璃版 (Windows 11 Acrylic效果)
真正的iOS风格毛玻璃效果
"""

import os
import sys
import time
import threading
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
def apply_blur_effect(hwnd, dark_mode=False):
    """应用Windows 11毛玻璃效果"""
    try:
        # 方法1: 使用BlurWindow库
        blur(hwnd, Acrylic=True, Dark=dark_mode, Animations=True)
    except:
        try:
            # 方法2: 使用DWM API
            accent_policy = ctypes.Structure
            accent_policy._fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint),
            ]

            window_composition_attrib_data = ctypes.Structure
            window_composition_attrib_data._fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ctypes.c_int)),
                ("SizeOfData", ctypes.c_size_t),
            ]

            accent = accent_policy()
            accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLURBEHIND
            accent.GradientColor = 0x01FFFFFF if not dark_mode else 0x01000000

            data = window_composition_attrib_data()
            data.Attribute = 19  # WCA_ACCENT_POLICY
            data.SizeOfData = ctypes.sizeof(accent)
            data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))

            ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        except:
            pass


class AcrylicFloatingWidget:
    """毛玻璃悬浮窗"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.95)

        # 设置窗口透明
        self.window.wm_attributes('-transparentcolor', 'black')

        # 窗口尺寸
        self.size = 90
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"{self.size}x{self.size}+{screen_width-110}+50")

        # iOS风格配色
        self.colors = {
            'ready': '#00D9FF',      # 青色
            'capturing': '#FF9F0A',  # 橙色
            'monitoring': '#007AFF', # 蓝色
            'bg': '#F2F2F7',         # 浅灰
            'card': 'rgba(242,242,247,0.8)'
        }

        self.current_state = 'ready'

        # 等待窗口显示
        self.window.update()

        # 获取窗口句柄并应用毛玻璃效果
        try:
            hwnd = self.get_window_handle()
            apply_blur_effect(hwnd, dark_mode=False)
        except:
            pass

        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg='#F2F2F7',
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack()

        # 绘制UI
        self.create_acrylic_ui()

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

        # 启动光晕动画
        self.glow_alpha = 0
        self.glow_direction = 1
        self.start_glow_animation()

    def get_window_handle(self):
        """获取窗口句柄"""
        self.window.update()
        return int(self.window.wm_frame(), 16)

    def create_acrylic_ui(self):
        """创建毛玻璃UI"""
        center = self.size // 2

        # 外圈光晕效果
        self.glow_circle = self.canvas.create_oval(
            8, 8, self.size-8, self.size-8,
            fill='',
            outline=self.colors[self.current_state],
            width=3
        )

        # 主圆形 - 半透明背景
        self.main_circle = self.canvas.create_oval(
            12, 12, self.size-12, self.size-12,
            fill='white',
            outline='',
            width=0
        )

        # 渐变圆圈（模拟玻璃反光）
        self.highlight_circle = self.canvas.create_oval(
            14, 10, self.size-26, self.size-30,
            fill='',
            outline='#FFFFFF',
            width=2
        )

        # 相机图标
        icon_size = 20

        # 相机主体
        self.camera_rect = self.canvas.create_rectangle(
            center - icon_size//2, center - icon_size//3,
            center + icon_size//2, center + icon_size//2,
            fill=self.colors[self.current_state],
            outline='',
            width=0
        )

        # 镜头
        self.lens = self.canvas.create_oval(
            center - icon_size//4, center - icon_size//6,
            center + icon_size//4, center + icon_size//3,
            fill='white',
            outline=self.colors[self.current_state],
            width=2
        )

        # 快门
        self.shutter = self.canvas.create_oval(
            center + icon_size//3, center - icon_size//2,
            center + icon_size//2, center - icon_size//4,
            fill=self.colors[self.current_state],
            outline=''
        )

        # 计数文本
        self.count_text = self.canvas.create_text(
            center,
            self.size - 16,
            text="0",
            font=("SF Pro Display", 13, "bold"),
            fill=self.colors[self.current_state]
        )

    def start_glow_animation(self):
        """启动光晕动画"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_glow()

    def animate_glow(self):
        """光晕动画"""
        if not self.animation_running:
            return

        try:
            if not self.is_hovering:
                self.glow_alpha += self.glow_direction * 3

                if self.glow_alpha >= 100:
                    self.glow_alpha = 100
                    self.glow_direction = -1
                elif self.glow_alpha <= 0:
                    self.glow_alpha = 0
                    self.glow_direction = 1

                # 更新光晕宽度
                width = 2 + (self.glow_alpha / 50)
                self.canvas.itemconfig(self.glow_circle, width=int(width))

            self.window.after(50, self.animate_glow)
        except:
            self.animation_running = False

    def update_state(self, state):
        """更新状态"""
        self.current_state = state
        color = self.colors[state]
        self.canvas.itemconfig(self.glow_circle, outline=color)
        self.canvas.itemconfig(self.camera_rect, fill=color)
        self.canvas.itemconfig(self.lens, outline=color)
        self.canvas.itemconfig(self.shutter, fill=color)
        self.canvas.itemconfig(self.count_text, fill=color)

    def update_count(self, count):
        """更新计数"""
        self.canvas.itemconfig(self.count_text, text=str(count))

    def on_hover_enter(self, event):
        """鼠标进入"""
        self.is_hovering = True
        self.window.attributes('-alpha', 1.0)
        self.canvas.itemconfig(self.glow_circle, width=4)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False
        self.window.attributes('-alpha', 0.95)

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
        self.animate_glow()


class AcrylicButton(tk.Canvas):
    """毛玻璃按钮"""
    def __init__(self, parent, text, command, width=150, height=50,
                 bg_color='#007AFF', hover_color='#0051D5', text_color='white', icon=''):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0, bd=0)

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hover = False

        # 创建圆角矩形
        self.create_rounded_rect(width, height, bg_color)

        # 图标和文字
        if icon:
            self.icon_text = self.create_text(
                width//2 - 25, height//2,
                text=icon,
                font=("SF Pro Display", 16),
                fill=text_color
            )
            self.text_obj = self.create_text(
                width//2 + 15, height//2,
                text=text,
                font=("SF Pro Display", 12, "bold"),
                fill=text_color
            )
        else:
            self.text_obj = self.create_text(
                width//2, height//2,
                text=text,
                font=("SF Pro Display", 12, "bold"),
                fill=text_color
            )

        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', lambda e: self.command())

    def create_rounded_rect(self, width, height, color):
        """创建圆角矩形"""
        radius = 12
        self.rect = self.create_polygon(
            [radius, 0,
             width-radius, 0,
             width, 0,
             width, radius,
             width, height-radius,
             width, height,
             width-radius, height,
             radius, height,
             0, height,
             0, height-radius,
             0, radius,
             0, 0],
            fill=color,
            outline='',
            smooth=True
        )

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
        self.root.geometry("520x680")
        self.root.resizable(False, False)

        # 应用毛玻璃效果到主窗口
        self.root.update()
        try:
            hwnd = int(self.root.wm_frame(), 16)
            apply_blur_effect(hwnd, dark_mode=False)
        except:
            pass

        # 设置透明背景
        self.root.configure(bg='#F2F2F7')

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

        # iOS风格配色
        self.colors = {
            'bg': '#F2F2F7',
            'card': '#FFFFFF',
            'primary': '#007AFF',
            'success': '#00D9FF',
            'warning': '#FF9F0A',
            'text': '#000000',
            'text_secondary': '#8E8E93'
        }

        # 创建UI
        self.create_ios_ui()

        # 创建悬浮窗
        self.floating_widget = AcrylicFloatingWidget(self)

        # 创建系统托盘
        self.create_tray_icon()

        # 注册热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.hide_main_window)

        # 默认显示悬浮窗
        self.root.withdraw()
        self.floating_widget.show()

    def create_ios_ui(self):
        """创建iOS风格UI"""
        # 顶部栏
        header = tk.Frame(self.root, bg='#FFFFFF', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📸",
            font=("SF Pro Display", 32),
            bg='#FFFFFF',
            fg=self.colors['primary']
        ).pack(side=tk.LEFT, padx=20, pady=20)

        tk.Label(
            header,
            text="截图助手",
            font=("SF Pro Display", 24, "bold"),
            bg='#FFFFFF',
            fg=self.colors['text']
        ).pack(side=tk.LEFT, pady=20)

        # 关闭按钮
        close_btn = tk.Label(
            header,
            text="×",
            font=("SF Pro Display", 28),
            bg='#FFFFFF',
            fg=self.colors['text_secondary'],
            cursor='hand2'
        )
        close_btn.pack(side=tk.RIGHT, padx=20)
        close_btn.bind('<Button-1>', lambda e: self.hide_main_window())

        # 状态卡片
        self.create_status_card()

        # 按钮区
        self.create_buttons()

        # 路径卡片
        self.create_path_card()

        # 快捷键提示
        self.create_shortcuts()

    def create_status_card(self):
        """创建状态卡片"""
        card = tk.Frame(self.root, bg=self.colors['card'])
        card.pack(fill=tk.X, padx=20, pady=20)

        inner = tk.Frame(card, bg=self.colors['card'])
        inner.pack(fill=tk.BOTH, padx=25, pady=25)

        self.status_label = tk.Label(
            inner,
            text="● 准备就绪",
            font=("SF Pro Display", 18, "bold"),
            bg=self.colors['card'],
            fg=self.colors['success']
        )
        self.status_label.pack(pady=12)

        # 计数
        count_frame = tk.Frame(inner, bg=self.colors['card'])
        count_frame.pack(pady=15)

        self.count_label = tk.Label(
            count_frame,
            text="0",
            font=("SF Pro Display", 48, "bold"),
            bg=self.colors['card'],
            fg=self.colors['primary']
        )
        self.count_label.pack()

        tk.Label(
            count_frame,
            text="今日截图",
            font=("SF Pro Display", 14),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        ).pack()

    def create_buttons(self):
        """创建按钮"""
        btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame.pack(pady=20)

        # 第一行
        row1 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row1.pack(pady=8)

        AcrylicButton(
            row1, "立即截图", self.capture_screenshot,
            width=240, height=56, bg_color='#007AFF', hover_color='#0051D5',
            icon='📷'
        ).pack(side=tk.LEFT, padx=8)

        self.monitor_btn = AcrylicButton(
            row1, "自动监听", self.toggle_monitoring,
            width=240, height=56, bg_color='#00D9FF', hover_color='#00A8CC',
            icon='🔄'
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=8)

        # 第二行
        row2 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row2.pack(pady=8)

        AcrylicButton(
            row2, "复制路径", self.copy_path,
            width=160, height=48, bg_color='#8E8E93', hover_color='#636366',
            icon='📋'
        ).pack(side=tk.LEFT, padx=8)

        AcrylicButton(
            row2, "打开文件夹", self.open_folder,
            width=160, height=48, bg_color='#8E8E93', hover_color='#636366',
            icon='📂'
        ).pack(side=tk.LEFT, padx=8)

        AcrylicButton(
            row2, "清理缓存", self.clear_cache,
            width=160, height=48, bg_color='#FF9F0A', hover_color='#FF8C00',
            icon='🗑️'
        ).pack(side=tk.LEFT, padx=8)

    def create_path_card(self):
        """创建路径卡片"""
        card = tk.Frame(self.root, bg=self.colors['card'])
        card.pack(fill=tk.X, padx=20, pady=12)

        inner = tk.Frame(card, bg=self.colors['card'])
        inner.pack(fill=tk.BOTH, padx=20, pady=18)

        tk.Label(
            inner,
            text="当前截图路径",
            font=("SF Pro Display", 13, "bold"),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 10))

        path_frame = tk.Frame(inner, bg='#F2F2F7')
        path_frame.pack(fill=tk.X)

        self.path_text = tk.Text(
            path_frame,
            height=2,
            font=("SF Mono", 10),
            bg='#F2F2F7',
            fg=self.colors['text'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=12,
            bd=0
        )
        self.path_text.pack(fill=tk.X)
        self.path_text.insert('1.0', str(self.current_path))

        self.copy_tip = tk.Label(
            inner,
            text="💡 截图后路径将自动复制",
            font=("SF Pro Display", 11),
            bg=self.colors['card'],
            fg=self.colors['primary']
        )
        self.copy_tip.pack(anchor=tk.W, pady=(10, 0))

    def create_shortcuts(self):
        """创建快捷键提示"""
        tips = tk.Frame(self.root, bg=self.colors['bg'])
        tips.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            tips,
            text="⌨️ 快捷键",
            font=("SF Pro Display", 13, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 12))

        shortcuts = [
            ("⌃⌥A", "Ctrl+Alt+A", "普通截图"),
            ("⇧⊞S", "Shift+Win+S", "截图并复制路径"),
            ("⌃⌥F", "Ctrl+Alt+F", "切换悬浮窗")
        ]

        for symbol, key, desc in shortcuts:
            row = tk.Frame(tips, bg=self.colors['bg'])
            row.pack(fill=tk.X, pady=4)

            tk.Label(
                row,
                text=symbol,
                font=("SF Pro Display", 11, "bold"),
                bg='#E5E5EA',
                fg=self.colors['text'],
                padx=12,
                pady=6,
                width=6
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=f"{key}  •  {desc}",
                font=("SF Pro Display", 11),
                bg=self.colors['bg'],
                fg=self.colors['text_secondary']
            ).pack(side=tk.LEFT, padx=12)

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
        self.update_status("● 正在截图...", 'capturing')

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
        self.update_status("● 截图并复制路径...", 'capturing')

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
            self.update_status("✗ 超时：未检测到截图", 'ready')

        threading.Thread(target=monitor, daemon=True).start()

    def capture_screenshot(self):
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
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.save_screenshot(img)
        except:
            self.update_status("✗ 截图失败", 'ready')

    def toggle_monitoring(self):
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        self.monitoring = True
        self.update_status("● 监听中...", 'monitoring')
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        self.update_status("● 已停止监听", 'ready')

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
        colors_map = {
            'ready': self.colors['success'],
            'capturing': self.colors['warning'],
            'monitoring': self.colors['primary']
        }

        self.status_label.config(text=text, fg=colors_map[state])
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
        path = self.path_text.get('1.0', tk.END).strip()
        if self.copy_to_clipboard(path):
            self.update_status("✓ 路径已复制", 'ready')
            self.flash_copy_tip()
        else:
            self.update_status("✗ 复制失败", 'ready')

    def flash_copy_tip(self):
        self.copy_tip.config(text="✓ 已复制到剪贴板！", fg=self.colors['success'])
        self.root.after(2000, lambda: self.copy_tip.config(
            text="💡 截图后路径将自动复制",
            fg=self.colors['primary']
        ))

    def open_folder(self):
        import subprocess
        subprocess.run(['explorer', str(self.screenshots_dir)])

    def clear_cache(self):
        """清理缓存"""
        result = messagebox.askyesno(
            "清理缓存",
            f"确定要清理所有历史截图吗？\n\n当前有 {len(list(self.screenshots_dir.glob('*.png')))} 个文件"
        )

        if result:
            try:
                count = 0
                for file in self.screenshots_dir.glob('*.png'):
                    file.unlink()
                    count += 1

                self.update_status(f"✓ 已清理 {count} 个文件", 'ready')
                messagebox.showinfo("清理完成", f"成功清理了 {count} 个历史截图文件")
            except Exception as e:
                self.update_status(f"✗ 清理失败: {e}", 'ready')
                messagebox.showerror("清理失败", f"清理缓存时出错：{e}")

    def create_tray_icon(self):
        def create_icon_image():
            image = Image.new('RGB', (64, 64), color='white')
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill='#007AFF', outline='white', width=2)
            draw.rectangle([24, 26, 40, 38], fill='white')
            draw.ellipse([28, 28, 36, 36], fill='#007AFF', outline='white', width=2)
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

        self.tray_icon = pystray.Icon("screenshot_helper", icon_image, "截图助手", menu)
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
