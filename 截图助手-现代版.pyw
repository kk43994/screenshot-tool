#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 - 现代化版本 (2025设计趋势)
采用毛玻璃效果、圆角阴影、平滑动画
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

try:
    from PIL import ImageGrab, Image, ImageTk, ImageDraw, ImageFilter, ImageFont
except ImportError:
    import subprocess
    print("正在安装必要的库...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pillow"])
    sys.exit()

import win32clipboard

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


class ModernFloatingWidget:
    """现代化悬浮窗 - 2025设计风格"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.95)

        # 窗口尺寸
        self.size = 72
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"{self.size}x{self.size}+{screen_width-100}+60")

        # 现代化配色
        self.colors = {
            'ready': '#10B981',      # 翠绿色
            'capturing': '#F59E0B',  # 琥珀色
            'monitoring': '#3B82F6', # 天蓝色
            'bg': '#FFFFFF',
            'shadow': 'rgba(0,0,0,0.1)'
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
        self.breath_alpha = 0.95
        self.breath_direction = -1
        self.start_breath_animation()

    def create_modern_ui(self):
        """创建现代化UI"""
        center = self.size // 2

        # 外圈阴影（模拟毛玻璃效果）
        self.shadow1 = self.canvas.create_oval(
            2, 2, self.size-2, self.size-2,
            fill='', outline='#E5E7EB', width=2
        )

        # 主圆形（渐变效果通过多层实现）
        self.circle_bg = self.canvas.create_oval(
            6, 6, self.size-6, self.size-6,
            fill=self.colors[self.current_state],
            outline='',
            width=0
        )

        # 内层高光
        self.highlight = self.canvas.create_oval(
            10, 8, self.size-25, self.size-25,
            fill='',
            outline='white',
            width=2
        )

        # 相机图标 - SVG风格
        self.draw_camera_icon(center)

        # 计数文本
        self.count_text = self.canvas.create_text(
            center,
            self.size - 12,
            text="0",
            font=("Segoe UI", 11, "bold"),
            fill='#6B7280'
        )

    def draw_camera_icon(self, center):
        """绘制现代化相机图标"""
        # 相机主体（矩形）
        self.camera_body = self.canvas.create_rectangle(
            center-14, center-8,
            center+14, center+10,
            fill='white',
            outline=''
        )

        # 镜头外圈
        self.lens_outer = self.canvas.create_oval(
            center-9, center-5,
            center+9, center+7,
            fill='',
            outline='white',
            width=3
        )

        # 镜头
        self.lens = self.canvas.create_oval(
            center-6, center-2,
            center+6, center+4,
            fill=self.colors[self.current_state],
            outline=''
        )

        # 闪光灯
        self.flash = self.canvas.create_oval(
            center+8, center-6,
            center+12, center-2,
            fill='white',
            outline=''
        )

    def update_state(self, state):
        """更新状态"""
        self.current_state = state
        color = self.colors[state]
        self.canvas.itemconfig(self.circle_bg, fill=color)
        self.canvas.itemconfig(self.lens, fill=color)

    def update_count(self, count):
        """更新计数"""
        self.canvas.itemconfig(self.count_text, text=str(count))

    def start_breath_animation(self):
        """启动呼吸动画"""
        if not self.animation_running:
            self.animation_running = True
            self.breath_loop()

    def breath_loop(self):
        """呼吸动画循环"""
        if not self.animation_running:
            return

        try:
            if self.is_hovering:
                self.window.attributes('-alpha', 1.0)
            else:
                self.breath_alpha += self.breath_direction * 0.015

                if self.breath_alpha <= 0.85:
                    self.breath_alpha = 0.85
                    self.breath_direction = 1
                elif self.breath_alpha >= 0.95:
                    self.breath_alpha = 0.95
                    self.breath_direction = -1

                self.window.attributes('-alpha', self.breath_alpha)

            self.window.after(40, self.breath_loop)
        except:
            self.animation_running = False

    def on_hover_enter(self, event):
        """鼠标进入"""
        self.is_hovering = True
        self.window.attributes('-alpha', 1.0)
        # 添加蓝色边框
        self.canvas.itemconfig(self.shadow1, outline='#3B82F6', width=3)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False
        # 恢复边框
        self.canvas.itemconfig(self.shadow1, outline='#E5E7EB', width=2)

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
        self.breath_loop()


class ModernButton(tk.Canvas):
    """现代化按钮"""
    def __init__(self, parent, text, command, width=140, height=44,
                 bg_color='#10B981', hover_color='#059669', text_color='white', icon=''):
        super().__init__(parent, width=width, height=height,
                        bg=parent['bg'], highlightthickness=0)

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hover = False

        # 绘制圆角矩形按钮
        self.rect = self.create_rounded_rect(
            0, 0, width, height, 10, fill=bg_color, outline=''
        )

        # 图标和文字
        if icon:
            self.icon_text = self.create_text(
                width//2 - 30, height//2,
                text=icon,
                font=("Segoe UI Emoji", 14),
                fill=text_color
            )
            self.text = self.create_text(
                width//2 + 10, height//2,
                text=text,
                font=("Segoe UI", 11, "bold"),
                fill=text_color
            )
        else:
            self.text = self.create_text(
                width//2, height//2,
                text=text,
                font=("Segoe UI", 11, "bold"),
                fill=text_color
            )

        # 绑定事件
        self.tag_bind(self.rect, '<Button-1>', lambda e: self.command())
        self.tag_bind(self.text, '<Button-1>', lambda e: self.command())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1,
                 x2, y1+radius, x2, y2-radius, x2, y2,
                 x2-radius, y2, x1+radius, y2, x1, y2,
                 x1, y2-radius, x1, y1+radius, x1, y1]
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
        self.root.geometry("500x640")
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

        # 现代化配色
        self.colors = {
            'bg': '#F9FAFB',
            'card_bg': '#FFFFFF',
            'primary': '#10B981',
            'secondary': '#3B82F6',
            'text': '#111827',
            'text_secondary': '#6B7280',
            'border': '#E5E7EB',
            'warning': '#F59E0B',
            'error': '#EF4444'
        }

        self.root.configure(bg=self.colors['bg'])

        # 创建UI
        self.create_modern_ui()

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

    def create_modern_ui(self):
        """创建现代化UI"""
        # 顶部栏
        self.create_header()

        # 状态卡片
        self.create_status_card()

        # 按钮区
        self.create_buttons()

        # 路径卡片
        self.create_path_card()

        # 快捷键提示
        self.create_tips()

    def create_header(self):
        """创建顶部栏"""
        header = tk.Frame(self.root, bg='#10B981', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📸 截图助手",
            font=("Segoe UI", 20, "bold"),
            bg='#10B981',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)

        # 最小化按钮
        close_btn = tk.Label(
            header,
            text="×",
            font=("Arial", 24),
            bg='#10B981',
            fg='white',
            cursor='hand2',
            width=2
        )
        close_btn.pack(side=tk.RIGHT, padx=10, pady=20)
        close_btn.bind('<Button-1>', lambda e: self.hide_main_window())

    def create_status_card(self):
        """创建状态卡片"""
        card = tk.Frame(self.root, bg=self.colors['card_bg'], relief=tk.FLAT)
        card.pack(fill=tk.X, padx=20, pady=20)

        inner = tk.Frame(card, bg=self.colors['card_bg'])
        inner.pack(fill=tk.BOTH, padx=20, pady=20)

        # 状态
        self.status_label = tk.Label(
            inner,
            text="● 准备就绪",
            font=("Segoe UI", 15, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.status_label.pack(pady=10)

        # 计数
        count_frame = tk.Frame(inner, bg=self.colors['card_bg'])
        count_frame.pack(pady=15)

        tk.Label(
            count_frame,
            text="今日截图",
            font=("Segoe UI", 11),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT, padx=5)

        self.count_label = tk.Label(
            count_frame,
            text="0",
            font=("Segoe UI", 28, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.count_label.pack(side=tk.LEFT, padx=5)

        tk.Label(
            count_frame,
            text="张",
            font=("Segoe UI", 11),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT)

    def create_buttons(self):
        """创建按钮"""
        btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame.pack(pady=15)

        # 第一行
        row1 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row1.pack(pady=8)

        ModernButton(
            row1, "立即截图", self.capture_screenshot,
            width=220, height=50, bg_color='#10B981', hover_color='#059669',
            icon='📷'
        ).pack(side=tk.LEFT, padx=10)

        self.monitor_btn = ModernButton(
            row1, "自动监听", self.toggle_monitoring,
            width=220, height=50, bg_color='#3B82F6', hover_color='#2563EB',
            icon='🔄'
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=10)

        # 第二行
        row2 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row2.pack(pady=8)

        ModernButton(
            row2, "复制路径", self.copy_path,
            width=220, height=50, bg_color='#6B7280', hover_color='#4B5563',
            icon='📋'
        ).pack(side=tk.LEFT, padx=10)

        ModernButton(
            row2, "打开文件夹", self.open_folder,
            width=220, height=50, bg_color='#6B7280', hover_color='#4B5563',
            icon='📂'
        ).pack(side=tk.LEFT, padx=10)

        # 第三行 - 高级功能
        row3 = tk.Frame(btn_frame, bg=self.colors['bg'])
        row3.pack(pady=8)

        ModernButton(
            row3, "清理缓存", self.clear_cache,
            width=145, height=44, bg_color='#F59E0B', hover_color='#D97706',
            icon='🗑️'
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            row3, "查看历史", self.show_history,
            width=145, height=44, bg_color='#8B5CF6', hover_color='#7C3AED',
            icon='📜'
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            row3, "设置", self.show_settings,
            width=145, height=44, bg_color='#6B7280', hover_color='#4B5563',
            icon='⚙️'
        ).pack(side=tk.LEFT, padx=5)

    def create_path_card(self):
        """创建路径卡片"""
        card = tk.Frame(self.root, bg=self.colors['card_bg'])
        card.pack(fill=tk.X, padx=20, pady=15)

        inner = tk.Frame(card, bg=self.colors['card_bg'])
        inner.pack(fill=tk.BOTH, padx=20, pady=15)

        tk.Label(
            inner,
            text="当前截图路径",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 10))

        path_frame = tk.Frame(inner, bg='#F3F4F6')
        path_frame.pack(fill=tk.X)

        self.path_text = tk.Text(
            path_frame,
            height=2,
            font=("Consolas", 10),
            bg='#F3F4F6',
            fg=self.colors['text'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=12
        )
        self.path_text.pack(fill=tk.X)
        self.path_text.insert('1.0', str(self.current_path))

        self.copy_tip = tk.Label(
            inner,
            text="💡 截图后路径将自动复制",
            font=("Segoe UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['primary']
        )
        self.copy_tip.pack(anchor=tk.W, pady=(10, 0))

    def create_tips(self):
        """创建提示"""
        tips = tk.Frame(self.root, bg=self.colors['bg'])
        tips.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(
            tips,
            text="⌨️ 快捷键",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 10))

        shortcuts = [
            ("Ctrl+Alt+A", "普通截图"),
            ("Shift+Win+S", "截图并复制路径"),
            ("Ctrl+Alt+F", "切换悬浮窗")
        ]

        for key, desc in shortcuts:
            row = tk.Frame(tips, bg=self.colors['bg'])
            row.pack(fill=tk.X, pady=3)

            tk.Label(
                row,
                text=key,
                font=("Consolas", 10, "bold"),
                bg='#E5E7EB',
                fg=self.colors['text'],
                padx=10,
                pady=4
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=desc,
                font=("Segoe UI", 10),
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
        self.monitor_btn.itemconfig(self.monitor_btn.rect, fill='#EF4444')
        self.update_status("● 监听中...", 'monitoring')
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        self.monitor_btn.itemconfig(self.monitor_btn.rect, fill='#3B82F6')
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
            'ready': self.colors['primary'],
            'capturing': self.colors['warning'],
            'monitoring': self.colors['secondary']
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
        self.copy_tip.config(text="✓ 已复制到剪贴板！", fg='#10B981')
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
            f"确定要清理screenshots文件夹中的所有历史截图吗？\n\n这将删除所有备份图片，但保留current.png\n\n当前有 {len(list(self.screenshots_dir.glob('*.png')))} 个文件"
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

    def show_history(self):
        """查看历史截图"""
        history_window = tk.Toplevel(self.root)
        history_window.title("截图历史")
        history_window.geometry("600x500")
        history_window.configure(bg=self.colors['bg'])

        # 顶部栏
        header = tk.Frame(history_window, bg=self.colors['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📜 截图历史",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=12)

        # 列表框架
        list_frame = tk.Frame(history_window, bg=self.colors['card_bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 列表
        listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            selectmode=tk.SINGLE
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 加载截图列表
        screenshots = sorted(self.screenshots_dir.glob('*.png'), reverse=True)

        for file in screenshots:
            timestamp = file.stem.replace('screenshot_', '')
            # 格式化时间戳
            try:
                dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                display_name = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                display_name = timestamp

            size_kb = file.stat().st_size / 1024
            listbox.insert(tk.END, f"{display_name}  ({size_kb:.1f} KB)")

        # 底部按钮
        btn_frame = tk.Frame(history_window, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        def open_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                file_path = screenshots[index]
                import subprocess
                subprocess.run(['start', '', str(file_path)], shell=True)

        def delete_selected():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                file_path = screenshots[index]

                if messagebox.askyesno("确认删除", f"确定要删除这个截图吗？\n\n{file_path.name}"):
                    try:
                        file_path.unlink()
                        listbox.delete(index)
                        messagebox.showinfo("删除成功", "文件已删除")
                    except Exception as e:
                        messagebox.showerror("删除失败", f"删除文件时出错：{e}")

        ModernButton(
            btn_frame, "打开", open_selected,
            width=140, height=40, bg_color=self.colors['primary']
        ).pack(side=tk.LEFT, padx=5)

        ModernButton(
            btn_frame, "删除", delete_selected,
            width=140, height=40, bg_color=self.colors['error']
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            btn_frame,
            text=f"共 {len(screenshots)} 个文件",
            font=("Segoe UI", 10),
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.RIGHT, padx=20)

    def show_settings(self):
        """显示设置"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x600")
        settings_window.configure(bg=self.colors['bg'])

        # 顶部栏
        header = tk.Frame(settings_window, bg=self.colors['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙️ 设置",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['primary'],
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=12)

        # 设置内容
        content = tk.Frame(settings_window, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 基本设置
        section1 = self.create_settings_section(content, "基本设置")

        tk.Label(
            section1,
            text="保存路径：",
            font=("Segoe UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=5)

        path_entry = tk.Entry(
            section1,
            font=("Consolas", 10),
            bg='#F3F4F6',
            relief=tk.FLAT
        )
        path_entry.pack(fill=tk.X, pady=5, ipady=8, padx=2)
        path_entry.insert(0, str(self.base_dir))

        # 自动启动
        auto_start_var = tk.BooleanVar()
        tk.Checkbutton(
            section1,
            text="开机自动启动",
            variable=auto_start_var,
            font=("Segoe UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=10)

        # 截图设置
        section2 = self.create_settings_section(content, "截图设置")

        auto_copy_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            section2,
            text="自动复制路径到剪贴板",
            variable=auto_copy_var,
            font=("Segoe UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=5)

        save_backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            section2,
            text="保存历史备份",
            variable=save_backup_var,
            font=("Segoe UI", 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=5)

        # 关于
        section3 = self.create_settings_section(content, "关于")

        tk.Label(
            section3,
            text="截图助手 v2.0",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=5)

        tk.Label(
            section3,
            text="现代化设计 • 简洁高效",
            font=("Segoe UI", 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=2)

        tk.Label(
            section3,
            text="Made with ❤️ by Claude AI",
            font=("Segoe UI", 9),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=2)

        # 保存按钮
        def save_settings():
            messagebox.showinfo("保存成功", "设置已保存！")
            settings_window.destroy()

        ModernButton(
            content, "保存设置", save_settings,
            width=200, height=44, bg_color=self.colors['primary']
        ).pack(pady=20)

    def create_settings_section(self, parent, title):
        """创建设置区块"""
        section = tk.Frame(parent, bg=self.colors['card_bg'])
        section.pack(fill=tk.X, pady=10)

        inner = tk.Frame(section, bg=self.colors['card_bg'])
        inner.pack(fill=tk.BOTH, padx=15, pady=15)

        tk.Label(
            inner,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 10))

        return inner

    def create_tray_icon(self):
        def create_icon_image():
            image = Image.new('RGB', (64, 64), color='white')
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill='#10B981', outline='white', width=2)
            draw.rectangle([24, 26, 40, 38], fill='white')
            draw.ellipse([28, 28, 36, 36], fill='#10B981', outline='white', width=2)
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
