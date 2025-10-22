#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图助手配置文件
在这里可以自定义各种设置
"""

from pathlib import Path
import os

# ==================== 路径配置 ====================

# 基础目录（可修改为你想要的位置）
# 默认：当前用户桌面的"截图助手"文件夹
BASE_DIR = Path(os.path.expanduser("~")) / "Desktop" / "截图助手"

# 截图备份目录
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# 当前截图固定路径
CURRENT_SCREENSHOT_PATH = BASE_DIR / "current.png"

# ==================== 界面配置 ====================

# 窗口尺寸
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400

# 颜色主题（深色主题）
COLORS = {
    'bg': '#2b2b2b',           # 背景色
    'fg': '#ffffff',           # 前景色（文字）
    'accent': '#4CAF50',       # 强调色（绿色）
    'button': '#3f51b5',       # 按钮色（蓝色）
    'error': '#f44336',        # 错误色（红色）
    'warning': '#ff9800'       # 警告色（橙色）
}

# 字体设置
FONT_FAMILY = "Microsoft YaHei"
FONT_SIZE_TITLE = 20
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10

# ==================== 热键配置 ====================

# 可以修改为你喜欢的热键组合
# 注意：修改后需要重启程序
HOTKEYS = {
    # 正常截图（保留图片在剪贴板）
    'normal_screenshot': 'ctrl+alt+a',

    # 截图并复制路径给 Claude
    'screenshot_with_path': 'shift+win+s'
}

# ==================== 功能配置 ====================

# 图片格式
IMAGE_FORMAT = "PNG"  # 可选: PNG, JPEG, BMP

# JPEG 质量（仅当格式为 JPEG 时有效）
JPEG_QUALITY = 95  # 1-100

# 是否保存备份
ENABLE_BACKUP = True

# 备份文件名格式
# 可用变量: {timestamp}, {date}, {time}
BACKUP_FILENAME_FORMAT = "screenshot_{timestamp}.png"

# 时间戳格式
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# 最大备份数量（0 表示不限制）
MAX_BACKUPS = 100

# 剪贴板监听间隔（秒）
CLIPBOARD_CHECK_INTERVAL = 0.5

# 截图等待超时时间（秒）
SCREENSHOT_TIMEOUT = 20

# ==================== 高级配置 ====================

# 是否启用通知
ENABLE_NOTIFICATIONS = True

# 通知显示时间（毫秒）
NOTIFICATION_DURATION = 2000

# 是否最小化到托盘（暂未实现）
MINIMIZE_TO_TRAY = False

# 是否开机自启动（暂未实现）
AUTO_START = False

# 调试模式
DEBUG_MODE = False

# ==================== 配置验证 ====================

def validate_config():
    """验证配置是否正确"""
    errors = []

    # 检查目录权限
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"无法创建目录: {e}")

    # 检查图片格式
    valid_formats = ['PNG', 'JPEG', 'BMP']
    if IMAGE_FORMAT not in valid_formats:
        errors.append(f"不支持的图片格式: {IMAGE_FORMAT}")

    # 检查 JPEG 质量
    if not (1 <= JPEG_QUALITY <= 100):
        errors.append(f"JPEG 质量必须在 1-100 之间: {JPEG_QUALITY}")

    return errors

# ==================== 配置说明 ====================

"""
配置修改指南：

1. 修改截图保存位置：
   BASE_DIR = Path("D:/我的截图")

2. 修改窗口大小：
   WINDOW_WIDTH = 600
   WINDOW_HEIGHT = 500

3. 修改颜色主题（浅色主题示例）：
   COLORS = {
       'bg': '#f5f5f5',
       'fg': '#333333',
       'accent': '#2196F3',
       ...
   }

4. 修改热键：
   HOTKEYS = {
       'normal_screenshot': 'ctrl+shift+a',
       'screenshot_with_path': 'ctrl+shift+s'
   }

5. 更改图片格式为 JPEG（节省空间）：
   IMAGE_FORMAT = "JPEG"
   JPEG_QUALITY = 85

6. 限制备份数量：
   MAX_BACKUPS = 50  # 最多保留 50 张历史截图

注意：修改配置后需要重启程序才能生效！
"""

if __name__ == "__main__":
    # 测试配置
    print("截图助手配置信息：")
    print(f"基础目录: {BASE_DIR}")
    print(f"截图目录: {SCREENSHOTS_DIR}")
    print(f"当前截图: {CURRENT_SCREENSHOT_PATH}")
    print(f"图片格式: {IMAGE_FORMAT}")
    print(f"启用备份: {ENABLE_BACKUP}")
    print(f"最大备份数: {MAX_BACKUPS if MAX_BACKUPS > 0 else '无限制'}")

    # 验证配置
    errors = validate_config()
    if errors:
        print("\n配置错误：")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ 配置验证通过！")
