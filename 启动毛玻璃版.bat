@echo off
chcp 65001 >nul
title 截图助手 - 毛玻璃版启动器
color 0B

cls
echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║                                                  ║
echo   ║     📸 截图助手 v2.5 - iOS风格毛玻璃版           ║
echo   ║                                                  ║
echo   ╚══════════════════════════════════════════════════╝
echo.
echo   正在检查环境...
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo   [✗] 错误：未检测到 Python！
    echo.
    pause
    exit /b 1
)

echo   [✓] Python 环境正常
echo.

REM 检查依赖
python -c "import tkinter; from PIL import Image; import win32clipboard; import keyboard; import pystray" 2>nul
if errorlevel 1 (
    echo   [!] 正在安装依赖库...
    echo.
    pip install pillow pywin32 keyboard pystray BlurWindow
    echo.
)

echo   [✓] 依赖检查完成
echo.
echo   正在启动iOS风格毛玻璃版...
echo.
echo   ══════════════════════════════════════════════════
echo.
echo   ✨ 特色功能：
echo.
echo   • Windows 11 Acrylic 毛玻璃效果
echo   • iOS风格圆形悬浮窗
echo   • 光晕动画效果
echo   • SF Pro Display 字体
echo   • 青色/蓝色/橙色主题
echo.
echo   ══════════════════════════════════════════════════
echo.

REM 启动程序
start "" pythonw "截图助手-毛玻璃版.pyw"

if errorlevel 1 (
    start "" python "截图助手-毛玻璃版.pyw"
)

timeout /t 2 /nobreak >nul
exit
