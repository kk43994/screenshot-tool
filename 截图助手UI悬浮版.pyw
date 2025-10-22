#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 UI 悬浮窗版本 - 为 Claude 快速截图
带有星形悬浮窗，点击展开完整界面
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


class FloatingWidget:
    """悬浮窗组件"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)  # 无边框
        self.window.attributes('-topmost', True)  # 始终置顶
        self.window.attributes('-alpha', 0.95)  # 半透明

        # 窗口尺寸
        self.size = 80
        self.window.geometry(f"{self.size}x{self.size}+{self.get_screen_width()-100}+100")

        # 状态颜色
        self.colors = {
            'ready': '#4CAF50',      # 绿色 - 就绪
            'capturing': '#ff9800',  # 橙色 - 截图中
            'monitoring': '#2196F3', # 蓝色 - 监听中
            'bg': '#2b2b2b'         # 背景色
        }

        # 当前状态
        self.current_state = 'ready'

        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=self.size,
            height=self.size,
            bg=self.colors['bg'],
            highlightthickness=0
        )
        self.canvas.pack()

        # 绘制星形
        self.draw_star()

        # 添加计数文本
        self.count_text = self.canvas.create_text(
            self.size // 2,
            self.size // 2,
            text="0",
            font=("Arial", 16, "bold"),
            fill='white'
        )

        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<Enter>', self.on_hover_enter)
        self.canvas.bind('<Leave>', self.on_hover_leave)

        # 拖动相关
        self.drag_x = 0
        self.drag_y = 0

        # 呼吸动画相关
        self.breath_alpha = 0.95
        self.breath_direction = -1  # -1: 变淡, 1: 变亮
        self.breath_speed = 0.02
        self.is_hovering = False
        self.animation_running = False

        # 启动呼吸动画
        self.start_breath_animation()

    def get_screen_width(self):
        """获取屏幕宽度"""
        return self.window.winfo_screenwidth()

    def draw_star(self):
        """绘制星形"""
        center_x = self.size // 2
        center_y = self.size // 2
        outer_radius = 30
        inner_radius = 15
        points = []

        # 生成星形的点
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.extend([x, y])

        # 绘制星形
        self.star = self.canvas.create_polygon(
            points,
            fill=self.colors[self.current_state],
            outline='white',
            width=2,
            smooth=False
        )

    def update_state(self, state):
        """更新状态和颜色"""
        self.current_state = state
        self.canvas.itemconfig(self.star, fill=self.colors[state])

    def update_count(self, count):
        """更新截图计数"""
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
            # 如果鼠标悬停，停止呼吸动画，保持完全不透明
            if self.is_hovering:
                self.window.attributes('-alpha', 1.0)
            else:
                # 更新透明度
                self.breath_alpha += self.breath_direction * self.breath_speed

                # 透明度范围：0.7 - 0.95
                if self.breath_alpha <= 0.7:
                    self.breath_alpha = 0.7
                    self.breath_direction = 1
                elif self.breath_alpha >= 0.95:
                    self.breath_alpha = 0.95
                    self.breath_direction = -1

                # 应用透明度
                self.window.attributes('-alpha', self.breath_alpha)

            # 继续动画循环 (每50ms更新一次)
            self.window.after(50, self.breath_loop)
        except:
            # 窗口可能已关闭
            self.animation_running = False

    def on_hover_enter(self, event):
        """鼠标进入"""
        self.is_hovering = True
        # 鼠标悬停时完全不透明
        self.window.attributes('-alpha', 1.0)
        # 添加一个轻微的缩放效果
        self.canvas.scale('all', self.size // 2, self.size // 2, 1.1, 1.1)

    def on_hover_leave(self, event):
        """鼠标离开"""
        self.is_hovering = False
        # 恢复缩放
        self.canvas.scale('all', self.size // 2, self.size // 2, 1/1.1, 1/1.1)

    def on_press(self, event):
        """鼠标按下"""
        self.drag_x = event.x
        self.drag_y = event.y

    def on_drag(self, event):
        """拖动窗口"""
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")

    def on_click(self, event):
        """点击事件 - 展开主窗口"""
        # 检查是否是拖动（移动距离很小才算点击）
        if abs(event.x - self.drag_x) < 5 and abs(event.y - self.drag_y) < 5:
            self.parent_app.toggle_main_window()

    def hide(self):
        """隐藏悬浮窗"""
        self.animation_running = False
        self.window.withdraw()

    def show(self):
        """显示悬浮窗"""
        self.window.deiconify()
        self.window.attributes('-topmost', True)
        self.animation_running = True
        self.breath_loop()


class ScreenshotHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图助手 for Claude")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # 设置图标（如果有的话）
        self.root.iconbitmap(default='')

        # 设置路径
        self.base_dir = Path(r"C:\Users\zhouk\Desktop\截图助手")
        self.screenshots_dir = self.base_dir / "screenshots"
        self.current_path = self.base_dir / "current.png"

        # 创建目录
        self.screenshots_dir.mkdir(exist_ok=True)

        # 状态变量
        self.screenshot_count = 0
        self.monitoring = False
        self.last_image = None
        self.should_copy_path = False
        self.main_window_visible = True

        # 设置样式
        self.setup_styles()

        # 创建UI
        self.create_widgets()

        # 创建悬浮窗
        self.floating_widget = FloatingWidget(self)
        self.floating_widget.hide()  # 初始隐藏

        # 注册全局热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_hotkeys(self):
        """注册全局热键"""
        try:
            # Ctrl+Alt+A: 正常截图
            keyboard.add_hotkey('ctrl+alt+a', self.hotkey_normal_screenshot)
            print("✓ 热键已注册: Ctrl+Alt+A - 正常截图")

            # Shift+Win+S: 截图并复制路径
            keyboard.add_hotkey('shift+win+s', self.hotkey_screenshot_copy_path)
            print("✓ 热键已注册: Shift+Win+S - 截图并复制路径")

            # Ctrl+Alt+F: 切换悬浮窗模式
            keyboard.add_hotkey('ctrl+alt+f', self.toggle_main_window)
            print("✓ 热键已注册: Ctrl+Alt+F - 切换悬浮窗")
        except Exception as e:
            print(f"热键注册失败: {e}")
            messagebox.showwarning("提示", "全局热键注册失败，请以管理员身份运行程序")

    def toggle_main_window(self):
        """切换主窗口和悬浮窗"""
        if self.main_window_visible:
            # 隐藏主窗口，显示悬浮窗
            self.root.withdraw()
            self.floating_widget.show()
            self.main_window_visible = False
        else:
            # 显示主窗口，隐藏悬浮窗
            self.floating_widget.hide()
            self.root.deiconify()
            self.root.lift()
            self.main_window_visible = True

    def hotkey_normal_screenshot(self):
        """Ctrl+Alt+A 快捷键处理"""
        self.should_copy_path = False
        self.update_status("正在截图（保留图片）...", 'capturing')

        if not self.main_window_visible:
            time.sleep(0.3)
        else:
            self.root.after(0, lambda: self.root.iconify())

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_for_normal_screenshot()

    def hotkey_screenshot_copy_path(self):
        """Shift+Win+S 快捷键处理"""
        self.should_copy_path = True
        self.update_status("正在截图（将复制路径）...", 'capturing')

        if not self.main_window_visible:
            time.sleep(0.3)
        else:
            self.root.after(0, lambda: self.root.iconify())

        time.sleep(0.3)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        self.start_monitoring_for_hotkey()

    def start_monitoring_for_normal_screenshot(self):
        """监听普通截图"""
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
                        if not self.main_window_visible:
                            pass  # 悬浮窗模式不需要恢复
                        else:
                            self.root.after(500, lambda: self.root.deiconify())
                        return
                except:
                    pass
            self.update_status("✗ 超时：未检测到截图", 'ready')
            if self.main_window_visible:
                self.root.after(0, lambda: self.root.deiconify())

        threading.Thread(target=monitor, daemon=True).start()

    def start_monitoring_for_hotkey(self):
        """监听复制路径截图"""
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
                        if not self.main_window_visible:
                            pass
                        else:
                            self.root.after(500, lambda: self.root.deiconify())
                        return
                except:
                    pass
            self.update_status("✗ 超时：未检测到截图", 'ready')
            if self.main_window_visible:
                self.root.after(0, lambda: self.root.deiconify())
            self.should_copy_path = False

        threading.Thread(target=monitor, daemon=True).start()

    def update_status(self, text, state='ready'):
        """更新状态文本和悬浮窗颜色"""
        self.root.after(0, lambda: self.status_label.config(
            text=text,
            fg=self.colors['accent'] if state == 'ready' else self.colors['warning']
        ))
        self.floating_widget.update_state(state)

    def copy_to_clipboard(self, text):
        """复制到剪贴板"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"复制失败: {e}")
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.root.update()
                return True
            except:
                return False

    def setup_styles(self):
        """设置UI样式"""
        style = ttk.Style()
        style.theme_use('clam')

        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4CAF50',
            'button': '#3f51b5',
            'error': '#f44336',
            'warning': '#ff9800'
        }

        self.root.configure(bg=self.colors['bg'])

    def create_widgets(self):
        """创建UI组件"""
        # 标题
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text="📸 截图助手",
            font=("Microsoft YaHei", 20, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="快速截图并发送给 Claude",
            font=("Microsoft YaHei", 10),
            bg=self.colors['bg'],
            fg='#cccccc'
        )
        subtitle_label.pack()

        # 状态显示
        self.status_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.status_frame.pack(pady=20)

        self.status_label = tk.Label(
            self.status_frame,
            text="准备就绪",
            font=("Microsoft YaHei", 12),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        )
        self.status_label.pack()

        # 计数显示
        self.count_label = tk.Label(
            self.status_frame,
            text=f"已截图: 0 张",
            font=("Microsoft YaHei", 10),
            bg=self.colors['bg'],
            fg='#999999'
        )
        self.count_label.pack(pady=5)

        # 按钮区域
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=20)

        # 截图按钮
        self.capture_btn = tk.Button(
            button_frame,
            text="📷 立即截图",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.colors['button'],
            fg='white',
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=0,
            command=self.capture_screenshot
        )
        self.capture_btn.pack(side=tk.LEFT, padx=10)

        # 自动监听按钮
        self.monitor_btn = tk.Button(
            button_frame,
            text="🔄 自动监听",
            font=("Microsoft YaHei", 12, "bold"),
            bg='#607D8B',
            fg='white',
            width=15,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=0,
            command=self.toggle_monitoring
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=10)

        # 悬浮窗切换按钮
        self.float_btn = tk.Button(
            button_frame,
            text="⭐ 悬浮窗",
            font=("Microsoft YaHei", 11, "bold"),
            bg='#9C27B0',
            fg='white',
            width=10,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=0,
            command=self.toggle_main_window
        )
        self.float_btn.pack(side=tk.LEFT, padx=5)

        # 路径显示框
        path_frame = tk.Frame(self.root, bg=self.colors['bg'])
        path_frame.pack(pady=20, padx=20, fill=tk.X)

        path_label_frame = tk.Frame(path_frame, bg=self.colors['bg'])
        path_label_frame.pack(anchor=tk.W, fill=tk.X)

        path_label = tk.Label(
            path_label_frame,
            text="当前截图路径:",
            font=("Microsoft YaHei", 10),
            bg=self.colors['bg'],
            fg='#cccccc'
        )
        path_label.pack(side=tk.LEFT)

        self.auto_copy_label = tk.Label(
            path_label_frame,
            text="(截图后自动复制)",
            font=("Microsoft YaHei", 9),
            bg=self.colors['bg'],
            fg='#4CAF50'
        )
        self.auto_copy_label.pack(side=tk.LEFT, padx=10)

        # 路径文本框
        self.path_text = tk.Text(
            path_frame,
            height=2,
            font=("Consolas", 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='white',
            wrap=tk.WORD
        )
        self.path_text.pack(fill=tk.X, pady=5)
        self.path_text.insert('1.0', str(self.current_path))

        # 复制按钮
        copy_btn = tk.Button(
            path_frame,
            text="📋 复制路径",
            font=("Microsoft YaHei", 10),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            relief=tk.RAISED,
            bd=0,
            command=self.copy_path
        )
        copy_btn.pack(pady=5)

        # 说明文字
        info_frame = tk.Frame(self.root, bg=self.colors['bg'])
        info_frame.pack(side=tk.BOTTOM, pady=10)

        info_texts = [
            ("Ctrl+Alt+A", "#4CAF50", " - 正常截图"),
            ("Shift+Win+S", "#FFD700", " - 截图并复制路径"),
            ("Ctrl+Alt+F", "#9C27B0", " - 切换悬浮窗")
        ]

        for key, color, desc in info_texts:
            frame = tk.Frame(info_frame, bg=self.colors['bg'])
            frame.pack()
            tk.Label(
                frame,
                text=f"快捷键: {key}",
                font=("Microsoft YaHei", 9, "bold"),
                bg=self.colors['bg'],
                fg=color
            ).pack(side=tk.LEFT)
            tk.Label(
                frame,
                text=desc,
                font=("Microsoft YaHei", 9),
                bg=self.colors['bg'],
                fg='#cccccc'
            ).pack(side=tk.LEFT)

    def capture_screenshot(self):
        """手动截图"""
        self.status_label.config(text="正在截图...", fg=self.colors['warning'])
        self.root.update()

        self.root.iconify()
        time.sleep(0.5)

        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("^+{s}")'])

        self.root.after(2000, self.check_clipboard_once)
        self.root.after(2500, lambda: self.root.deiconify())

    def check_clipboard_once(self):
        """检查一次剪贴板"""
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self.save_screenshot(img)
        except:
            self.status_label.config(text="截图失败", fg=self.colors['error'])

    def toggle_monitoring(self):
        """切换自动监听"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """开始监听剪贴板"""
        self.monitoring = True
        self.monitor_btn.config(text="⏸ 停止监听", bg=self.colors['error'])
        self.update_status("监听中...", 'monitoring')

        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监听"""
        self.monitoring = False
        self.monitor_btn.config(text="🔄 自动监听", bg='#607D8B')
        self.update_status("已停止监听", 'ready')

    def monitor_clipboard(self):
        """监听剪贴板"""
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
            # 保存到固定位置
            img.save(str(self.current_path))

            # 保存备份
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.screenshots_dir / f"screenshot_{timestamp}.png"
            img.save(str(backup_path))

            # 更新计数
            self.screenshot_count += 1
            self.count_label.config(text=f"已截图: {self.screenshot_count} 张")
            self.floating_widget.update_count(self.screenshot_count)

            # 根据标志决定是否复制路径
            if self.should_copy_path:
                if self.copy_to_clipboard(str(self.current_path)):
                    self.update_status("✓ 截图成功！路径已复制", 'ready')
                    self.flash_copy_label()
                    if self.main_window_visible:
                        self.show_notification()
                else:
                    self.update_status("✓ 截图成功！(复制失败)", 'ready')
                self.should_copy_path = False
            else:
                self.update_status("✓ 截图已保存（图片保留在剪贴板）", 'ready')

        except Exception as e:
            self.update_status(f"保存失败: {e}", 'ready')
            self.should_copy_path = False

    def flash_copy_label(self):
        """闪烁提示"""
        original_text = self.auto_copy_label.cget("text")
        original_fg = self.auto_copy_label.cget("fg")

        self.auto_copy_label.config(text="✓ 已复制到剪贴板！", fg='#FFD700')
        self.root.after(1500, lambda: self.auto_copy_label.config(text=original_text, fg=original_fg))

    def copy_path(self):
        """复制路径"""
        path = self.path_text.get('1.0', tk.END).strip()
        if self.copy_to_clipboard(path):
            self.status_label.config(text="✓ 路径已复制！", fg=self.colors['accent'])
            self.flash_copy_label()
        else:
            self.status_label.config(text="✗ 复制失败！", fg=self.colors['error'])

    def show_notification(self):
        """显示通知"""
        notify = tk.Toplevel(self.root)
        notify.title("")
        notify.geometry("300x80+{}+{}".format(
            self.root.winfo_x() + 100,
            self.root.winfo_y() + 150
        ))
        notify.configure(bg=self.colors['accent'])
        notify.overrideredirect(True)

        label = tk.Label(
            notify,
            text="✓ 截图已保存\n路径已复制到剪贴板",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.colors['accent'],
            fg='white'
        )
        label.pack(expand=True)

        notify.after(2000, notify.destroy)

    def on_closing(self):
        """关闭程序"""
        self.monitoring = False
        self.floating_widget.window.destroy()
        self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenshotHelper()
    app.run()
