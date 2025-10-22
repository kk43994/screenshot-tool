#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手 UI 版本 - 为 Claude 快速截图
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

# 处理导入
try:
    from PIL import ImageGrab, Image, ImageTk
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


class ScreenshotHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图助手 for Claude")
        self.root.geometry("500x400")
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
        self.should_copy_path = False  # 是否应该复制路径的标志

        # 设置样式
        self.setup_styles()

        # 创建UI
        self.create_widgets()

        # 注册全局热键
        self.setup_hotkeys()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_hotkeys(self):
        """注册全局热键"""
        try:
            # Ctrl+Alt+A: 正常截图（不复制路径，保留图片在剪贴板）
            keyboard.add_hotkey('ctrl+alt+a', self.hotkey_normal_screenshot)
            print("✓ 热键已注册: Ctrl+Alt+A - 正常截图")

            # Shift+Win+S: 截图并复制路径给 Claude
            keyboard.add_hotkey('shift+win+s', self.hotkey_screenshot_copy_path)
            print("✓ 热键已注册: Shift+Win+S - 截图并复制路径")
        except Exception as e:
            print(f"热键注册失败: {e}")
            messagebox.showwarning("提示", "全局热键注册失败，请以管理员身份运行程序")

    def hotkey_normal_screenshot(self):
        """Ctrl+Alt+A 快捷键处理 - 正常截图，不复制路径"""
        # 设置标志：不复制路径
        self.should_copy_path = False

        # 更新状态
        self.root.after(0, lambda: self.status_label.config(
            text="正在截图（保留图片在剪贴板）...",
            fg=self.colors['warning']
        ))

        # 最小化窗口
        self.root.after(0, lambda: self.root.iconify())

        # 等待一下再调用截图
        time.sleep(0.3)

        # 模拟 Win+Shift+S 截图
        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        # 开始监听剪贴板
        self.start_monitoring_for_normal_screenshot()

    def hotkey_screenshot_copy_path(self):
        """Shift+Win+S 快捷键处理 - 截图并复制路径"""
        # 设置标志：需要复制路径
        self.should_copy_path = True

        # 更新状态
        self.root.after(0, lambda: self.status_label.config(
            text="正在截图（将复制路径）...",
            fg=self.colors['warning']
        ))

        # 最小化窗口
        self.root.after(0, lambda: self.root.iconify())

        # 等待一下再调用截图
        time.sleep(0.3)

        # 模拟 Win+Shift+S 截图
        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("+^{s}")'])

        # 开始监听剪贴板
        self.start_monitoring_for_hotkey()

    def start_monitoring_for_normal_screenshot(self):
        """开始监听剪贴板（正常截图，不复制路径）"""
        # 记录当前剪贴板的图片（如果有）
        try:
            current_img = ImageGrab.grabclipboard()
        except:
            current_img = None

        def monitor():
            for i in range(40):  # 最多等待20秒
                time.sleep(0.5)
                try:
                    img = ImageGrab.grabclipboard()
                    # 检测到新的图片（不同于之前的）
                    if isinstance(img, Image.Image) and img != current_img:
                        # 找到图片了，保存但不复制路径（保持图片在剪贴板）
                        self.root.after(0, lambda i=img: self.save_screenshot(i))
                        # 恢复窗口
                        self.root.after(500, lambda: self.root.deiconify())
                        return
                except:
                    pass
            # 超时，重置标志和恢复窗口
            self.root.after(0, lambda: self.status_label.config(
                text="✗ 超时：未检测到截图",
                fg=self.colors['error']
            ))
            self.root.after(0, lambda: self.root.deiconify())

        threading.Thread(target=monitor, daemon=True).start()

    def start_monitoring_for_hotkey(self):
        """开始监听剪贴板（针对热键截图 - 复制路径模式）"""
        # 记录当前剪贴板的图片（如果有）
        try:
            current_img = ImageGrab.grabclipboard()
        except:
            current_img = None

        def monitor():
            for i in range(40):  # 最多等待20秒
                time.sleep(0.5)
                try:
                    img = ImageGrab.grabclipboard()
                    # 检测到新的图片（不同于之前的）
                    if isinstance(img, Image.Image) and img != current_img:
                        # 找到图片了，保存并复制路径
                        self.root.after(0, lambda i=img: self.save_screenshot(i))
                        # 恢复窗口
                        self.root.after(500, lambda: self.root.deiconify())
                        return
                except:
                    pass
            # 超时，重置标志和恢复窗口
            self.root.after(0, lambda: self.status_label.config(
                text="✗ 超时：未检测到截图",
                fg=self.colors['error']
            ))
            self.root.after(0, lambda: self.root.deiconify())
            self.should_copy_path = False

        threading.Thread(target=monitor, daemon=True).start()

    def copy_to_clipboard(self, text):
        """使用 Windows 原生 API 复制到剪贴板"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"复制失败: {e}")
            # 备用方案：使用 tkinter 的剪贴板
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

        # 配置颜色
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

        # 自动复制提示标签
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

        info_text = "快捷键: Ctrl+Alt+A - 正常截图（保留图片在剪贴板）"
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Microsoft YaHei", 9, "bold"),
            bg=self.colors['bg'],
            fg='#4CAF50'
        )
        info_label.pack()

        info_text2 = "快捷键: Shift+Win+S - 截图并复制路径给Claude"
        info_label2 = tk.Label(
            info_frame,
            text=info_text2,
            font=("Microsoft YaHei", 9, "bold"),
            bg=self.colors['bg'],
            fg='#FFD700'
        )
        info_label2.pack(pady=2)

    def capture_screenshot(self):
        """手动截图"""
        self.status_label.config(text="正在截图...", fg=self.colors['warning'])
        self.root.update()

        # 最小化窗口
        self.root.iconify()
        time.sleep(0.5)

        # 模拟按键 Win+Shift+S
        import subprocess
        subprocess.run(['powershell', '-Command',
                       'Add-Type -AssemblyName System.Windows.Forms;'
                       '[System.Windows.Forms.SendKeys]::SendWait("^+{s}")'])

        # 等待用户截图
        self.root.after(2000, self.check_clipboard_once)

        # 恢复窗口
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
        self.status_label.config(text="监听中...", fg=self.colors['accent'])

        # 在新线程中监听
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监听"""
        self.monitoring = False
        self.monitor_btn.config(text="🔄 自动监听", bg='#607D8B')
        self.status_label.config(text="已停止监听", fg='#999999')

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

            # 根据标志决定是否复制路径
            if self.should_copy_path:
                # 需要复制路径给 Claude
                if self.copy_to_clipboard(str(self.current_path)):
                    self.status_label.config(text="✓ 截图成功！路径已复制", fg=self.colors['accent'])
                    self.flash_copy_label()
                    self.show_notification()
                else:
                    self.status_label.config(text="✓ 截图成功！(复制失败)", fg=self.colors['warning'])
                # 重置标志
                self.should_copy_path = False
            else:
                # 普通截图，不复制路径（保留图片在剪贴板）
                self.status_label.config(text="✓ 截图已保存（图片保留在剪贴板）", fg=self.colors['accent'])

        except Exception as e:
            self.status_label.config(text=f"保存失败: {e}", fg=self.colors['error'])
            self.should_copy_path = False

    def flash_copy_label(self):
        """闪烁提示路径已复制"""
        original_text = self.auto_copy_label.cget("text")
        original_fg = self.auto_copy_label.cget("fg")

        # 改变为高亮
        self.auto_copy_label.config(text="✓ 已复制到剪贴板！", fg='#FFD700')

        # 1.5秒后恢复
        self.root.after(1500, lambda: self.auto_copy_label.config(text=original_text, fg=original_fg))

    def copy_path(self):
        """复制路径到剪贴板"""
        path = self.path_text.get('1.0', tk.END).strip()
        if self.copy_to_clipboard(path):
            self.status_label.config(text="✓ 路径已复制！", fg=self.colors['accent'])
            self.flash_copy_label()
        else:
            self.status_label.config(text="✗ 复制失败！", fg=self.colors['error'])

    def show_notification(self):
        """显示通知"""
        # 创建临时通知窗口
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

        # 2秒后自动关闭
        notify.after(2000, notify.destroy)

    def on_closing(self):
        """关闭程序"""
        self.monitoring = False
        self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenshotHelper()
    app.run()